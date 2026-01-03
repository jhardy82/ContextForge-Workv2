"""Project service with metrics and management logic.

Handles project operations, metrics calculation, and project management.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.enums import ProjectStatus
from taskman_api.core.errors import AppError, NotFoundError
from taskman_api.core.result import Err, Ok, Result
from taskman_api.db.models.project import Project
from taskman_api.db.repositories.project_repository import ProjectRepository
from taskman_api.db.repositories.task_repository import TaskRepository
from taskman_api.schemas.project import (
    ProjectCreateRequest,
    ProjectResponse,
    ProjectUpdateRequest,
)

from .base import BaseService


class ProjectService(
    BaseService[Project, ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse]
):
    """Project business logic and operations.

    Provides project management functionality including:
    - CRUD operations (inherited from BaseService)
    - Metrics calculation
    - Sprint management
    - Project health assessment

    Example:
        service = ProjectService(session)
        metrics = await service.get_metrics("P-TASKMAN")
        match metrics:
            case Ok(data):
                print(f"Project health: {data['health_status']}")
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize ProjectService with session.

        Args:
            session: Async database session
        """
        repository = ProjectRepository(session)
        super().__init__(repository, Project, ProjectResponse)
        self.project_repo = repository
        self.task_repo = TaskRepository(session)
        self.session = session

    async def get_metrics(
        self,
        project_id: str,
    ) -> Result[dict, NotFoundError | AppError]:
        """Calculate project metrics.

        Computes various project health and progress metrics:
        - Total task count
        - Tasks by status breakdown
        - Average velocity across sprints
        - Overall health status (green/yellow/red)

        Args:
            project_id: Project identifier

        Returns:
            Result containing metrics dict or error

        Example:
            result = await service.get_metrics("P-TASKMAN")
            match result:
                case Ok(metrics):
                    print(f"Total tasks: {metrics['total_tasks']}")
                    print(f"Health: {metrics['health_status']}")
                case Err(error):
                    print(f"Failed: {error.message}")
        """
        # Verify project exists
        project_result = await self.get(project_id)
        match project_result:
            case Err(error):
                return Err(error)
            case Ok(_):
                pass

        # Get all tasks for project
        tasks_result = await self.task_repo.find_by_project(
            project_id, status=None, limit=1000, offset=0
        )

        match tasks_result:
            case Err(error):
                return Err(error)
            case Ok(tasks):
                # Calculate metrics
                total_tasks = len(tasks)

                # Count tasks by status
                tasks_by_status: dict[str, int] = {}
                for task in tasks:
                    status_value = task.status.value
                    tasks_by_status[status_value] = (
                        tasks_by_status.get(status_value, 0) + 1
                    )

                # Calculate health status
                if total_tasks == 0:
                    health_status = "green"  # No tasks yet
                else:
                    blocked_count = tasks_by_status.get("blocked", 0)
                    done_count = tasks_by_status.get("done", 0)

                    blocked_pct = (blocked_count / total_tasks) * 100
                    completion_pct = (done_count / total_tasks) * 100

                    if blocked_pct > 20:
                        health_status = "red"  # Too many blocked tasks
                    elif blocked_pct > 10 or completion_pct < 30:
                        health_status = "yellow"  # Warning
                    else:
                        health_status = "green"  # Healthy

                metrics = {
                    "total_tasks": total_tasks,
                    "tasks_by_status": tasks_by_status,
                    "health_status": health_status,
                    "completion_percentage": (
                        (tasks_by_status.get("done", 0) / total_tasks * 100)
                        if total_tasks > 0
                        else 0.0
                    ),
                    "blocked_percentage": (
                        (tasks_by_status.get("blocked", 0) / total_tasks * 100)
                        if total_tasks > 0
                        else 0.0
                    ),
                }

                return Ok(metrics)

    async def add_sprint(
        self,
        project_id: str,
        sprint_id: str,
    ) -> Result[ProjectResponse, NotFoundError | AppError]:
        """Add sprint to project's sprints array.

        Args:
            project_id: Project identifier
            sprint_id: Sprint identifier to add

        Returns:
            Result containing updated project or error

        Example:
            result = await service.add_sprint("P-TASKMAN", "S-2025-01")
            match result:
                case Ok(project):
                    print(f"Sprint added: {len(project.sprints)} total")
        """
        # Get current project
        get_result = await self.get(project_id)

        match get_result:
            case Err(error):
                return Err(error)
            case Ok(project_response):
                # Add sprint to sprints array if not already present
                current_sprints = project_response.sprints
                if sprint_id not in current_sprints:
                    updated_sprints = current_sprints + [sprint_id]
                    update_request = ProjectUpdateRequest(sprints=updated_sprints)
                    return await self.update(project_id, update_request)
                else:
                    # Sprint already in project, return current state
                    return Ok(project_response)

    async def remove_sprint(
        self,
        project_id: str,
        sprint_id: str,
    ) -> Result[ProjectResponse, NotFoundError | AppError]:
        """Remove sprint from project's sprints array.

        Args:
            project_id: Project identifier
            sprint_id: Sprint identifier to remove

        Returns:
            Result containing updated project or error

        Example:
            result = await service.remove_sprint("P-TASKMAN", "S-2025-01")
        """
        # Get current project
        get_result = await self.get(project_id)

        match get_result:
            case Err(error):
                return Err(error)
            case Ok(project_response):
                # Remove sprint from sprints array
                current_sprints = project_response.sprints
                if sprint_id in current_sprints:
                    updated_sprints = [s for s in current_sprints if s != sprint_id]
                    update_request = ProjectUpdateRequest(sprints=updated_sprints)
                    return await self.update(project_id, update_request)
                else:
                    # Sprint not in project, return current state
                    return Ok(project_response)

    async def change_status(
        self,
        project_id: str,
        new_status: ProjectStatus,
    ) -> Result[ProjectResponse, NotFoundError | AppError]:
        """Change project status.

        Args:
            project_id: Project identifier
            new_status: New project status

        Returns:
            Result containing updated project or error

        Example:
            result = await service.change_status("P-TASKMAN", ProjectStatus.ACTIVE)
        """
        update_request = ProjectUpdateRequest(status=new_status)
        return await self.update(project_id, update_request)

    async def get_by_status(
        self,
        status: ProjectStatus,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[ProjectResponse], AppError]:
        """Get projects by status.

        Args:
            status: Project status filter
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing list of projects or error

        Example:
            result = await service.get_by_status(ProjectStatus.ACTIVE)
            match result:
                case Ok(projects):
                    print(f"Found {len(projects)} active projects")
        """
        result = await self.project_repo.find_by_status(status, limit, offset)

        match result:
            case Ok(projects):
                responses = [
                    self.response_class.model_validate(project)
                    for project in projects
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def get_by_owner(
        self,
        owner: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[ProjectResponse], AppError]:
        """Get projects by owner.

        Args:
            owner: Owner username
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing list of projects or error

        Example:
            result = await service.get_by_owner("john.doe")
        """
        result = await self.project_repo.find_by_owner(owner, limit, offset)

        match result:
            case Ok(projects):
                responses = [
                    self.response_class.model_validate(project)
                    for project in projects
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)
