"""Sprint service with velocity and burndown calculations.

Handles sprint operations, metrics, and sprint lifecycle management.
"""

from datetime import date
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.enums import PhaseStatus, SprintStatus, TaskStatus
from taskman_api.core.errors import AppError, NotFoundError
from taskman_api.core.result import Err, Ok, Result
from taskman_api.db.session import manager
from taskman_api.models.sprint import Sprint
from taskman_api.repositories.postgres_sprint_repository import PostgresSprintRepository
from taskman_api.repositories.project_repository import ProjectRepository
from taskman_api.repositories.sprint_repository import SprintRepository
from taskman_api.repositories.task_repository import TaskRepository
from taskman_api.schemas.sprint import (
    SprintCreateRequest,
    SprintProgress,
    SprintResponse,
    SprintUpdateRequest,
)

from .base import BaseService


class SprintService(
    BaseService[Sprint, SprintCreateRequest, SprintUpdateRequest, SprintResponse]
):
    """Sprint business logic and operations.

    Provides sprint management functionality including:
    - CRUD operations (inherited from BaseService)
    - Velocity calculation
    - Burndown chart data
    - Sprint lifecycle management
    - Progress tracking

    Example:
        service = SprintService(session)
        velocity = await service.calculate_velocity("S-2025-01")
        match velocity:
            case Ok(points):
                print(f"Sprint velocity: {points} points")
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize SprintService with session.

        Args:
            session: Async database session
        """
        if not manager._using_fallback:
            repository = PostgresSprintRepository(session)
        else:
            repository = SprintRepository(session)

        super().__init__(repository, Sprint, SprintResponse)
        self.sprint_repo = repository
        self.task_repo = TaskRepository(session)
        self.project_repo = ProjectRepository(session)
        self.session = session

    async def search(
        self,
        status: SprintStatus | None = None,
        project_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[tuple[list[SprintResponse], int], AppError]:
        """Search sprints with filters.

        Args:
            status: Optional status filter
            project_id: Optional project filter
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing (sprints, total_count) or error
        """
        try:
            repo_status = status.value if status else None

            sprints, total = await self.sprint_repo.search(
                status=repo_status,
                project_id=project_id,
                limit=limit,
                offset=offset,
            )

            responses = [
                self.response_class.model_validate(self._deserialize_json_fields(sprint))
                for sprint in sprints
            ]

            return Ok((responses, total))
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def get_progress(
        self,
        sprint_id: str,
    ) -> Result[SprintProgress, NotFoundError | AppError]:
        """Get sprint progress report.

        Calculates completed tasks, points, and days remaining.

        Args:
            sprint_id: Sprint identifier

        Returns:
            Result containing progress report or error
        """
        # Verify sprint exists
        sprint_result = await self.get(sprint_id)
        match sprint_result:
            case Err(error):
                return Err(error)
            case Ok(sprint):
                pass

        try:
            # Reuse burndown calculation for internal logic if efficient,
            # but here we just need summary stats.

            # Get all tasks
            tasks = await self.task_repo.get_by_sprint(sprint_id, limit=1000)

            total_tasks = len(tasks)
            completed_tasks = [t for t in tasks if t.status == TaskStatus.DONE]
            completed_count = len(completed_tasks)

            total_points = sum(t.estimate_points or 0 for t in tasks)
            completed_points = sum(t.estimate_points or 0 for t in completed_tasks)

            percentage = (completed_points / total_points * 100) if total_points > 0 else 0.0

            # Calculate days remaining
            days_remaining = None
            if sprint.end_date:
                # Calculate based on Today vs End Date
                today = date.today()
                days_remaining = max(0, (sprint.end_date - today).days)

            return Ok(
                SprintProgress(
                    sprint_id=sprint.id,
                    name=sprint.name,
                    status=sprint.status,
                    task_count=total_tasks,
                    completed_count=completed_count,
                    completion_percentage=round(percentage, 1),
                    total_points=total_points,
                    completed_points=completed_points,
                    days_remaining=days_remaining,
                )
            )
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def create(self, create_data: SprintCreateRequest) -> Result[SprintResponse, AppError]:
        """Create a new sprint with validation.

        Args:
            create_data: Sprint creation data

        Returns:
            Created sprint or error
        """
        # Validate project exists
        project = await self.project_repo.get_by_id(create_data.primary_project)
        if not project:
            return Err(NotFoundError(f"Project {create_data.primary_project} not found"))

        return await super().create(create_data)

    def _serialize_json_fields(self, data: dict[str, Any]) -> dict[str, Any]:
        """Override to handle primary_project -> project_id mapping."""
        if "primary_project" in data:
            data["project_id"] = data.pop("primary_project")
        return super()._serialize_json_fields(data)

    def _deserialize_json_fields(self, entity: Sprint) -> dict[str, Any]:
        """Override to handle project_id -> primary_project mapping."""
        data = super()._deserialize_json_fields(entity)
        if "project_id" in data and "primary_project" not in data:
            data["primary_project"] = data["project_id"]
        return data

    async def calculate_velocity(
        self,
        sprint_id: str,
    ) -> Result[float, NotFoundError | AppError]:
        """Calculate actual velocity from completed tasks.

        Sums estimate_points for all tasks with status=DONE in the sprint.

        Args:
            sprint_id: Sprint identifier

        Returns:
            Result containing velocity (points) or error

        Example:
            result = await service.calculate_velocity("S-2025-01")
            match result:
                case Ok(velocity):
                    print(f"Completed {velocity} story points")
        """
        # Verify sprint exists
        sprint_result = await self.get(sprint_id)
        match sprint_result:
            case Err(error):
                return Err(error)
            case Ok(_):
                pass

        # Get all completed tasks in sprint
        tasks_result = await self.task_repo.find_by_sprint(
            sprint_id, status=TaskStatus.DONE, limit=1000, offset=0
        )

        match tasks_result:
            case Err(error):
                return Err(error)
            case Ok(tasks):
                # Sum estimate_points for completed tasks
                total_points = sum(
                    task.estimate_points for task in tasks if task.estimate_points
                )
                return Ok(total_points)

    async def get_burndown(
        self,
        sprint_id: str,
    ) -> Result[dict, NotFoundError | AppError]:
        """Calculate burndown chart data.

        Returns:
            {
                "total_points": float,
                "remaining_points": float,
                "completed_points": float,
                "days_total": int,
                "days_remaining": int,
                "ideal_burndown_rate": float,
                "actual_burndown_rate": float,
            }

        Args:
            sprint_id: Sprint identifier

        Returns:
            Result containing burndown data or error

        Example:
            result = await service.get_burndown("S-2025-01")
            match result:
                case Ok(data):
                    print(f"Remaining: {data['remaining_points']} points")
                    print(f"Days left: {data['days_remaining']}")
        """
        # Get sprint
        sprint_result = await self.get(sprint_id)
        match sprint_result:
            case Err(error):
                return Err(error)
            case Ok(sprint):
                pass

        # Get all tasks in sprint
        all_tasks_result = await self.task_repo.find_by_sprint(
            sprint_id, status=None, limit=1000, offset=0
        )

        match all_tasks_result:
            case Err(error):
                return Err(error)
            case Ok(all_tasks):
                # Calculate points
                total_points = sum(
                    task.estimate_points for task in all_tasks if task.estimate_points
                )

                # Get completed tasks
                completed_tasks_result = await self.task_repo.find_by_sprint(
                    sprint_id, status=TaskStatus.DONE, limit=1000, offset=0
                )

                match completed_tasks_result:
                    case Err(error):
                        return Err(error)
                    case Ok(completed_tasks):
                        completed_points = sum(
                            task.estimate_points
                            for task in completed_tasks
                            if task.estimate_points
                        )
                        remaining_points = total_points - completed_points

                        # Calculate days
                        today = date.today()
                        days_total = (sprint.end_date - sprint.start_date).days
                        days_elapsed = max(0, (today - sprint.start_date).days)
                        days_remaining = max(0, (sprint.end_date - today).days)

                        # Calculate burndown rates
                        ideal_burndown_rate = (
                            total_points / days_total if days_total > 0 else 0.0
                        )
                        actual_burndown_rate = (
                            completed_points / days_elapsed if days_elapsed > 0 else 0.0
                        )

                        burndown_data = {
                            "total_points": total_points,
                            "remaining_points": remaining_points,
                            "completed_points": completed_points,
                            "days_total": days_total,
                            "days_elapsed": days_elapsed,
                            "days_remaining": days_remaining,
                            "ideal_burndown_rate": round(ideal_burndown_rate, 2),
                            "actual_burndown_rate": round(actual_burndown_rate, 2),
                            "on_track": actual_burndown_rate >= ideal_burndown_rate,
                        }

                        return Ok(burndown_data)

    async def change_status(
        self,
        sprint_id: str,
        new_status: SprintStatus,
    ) -> Result[SprintResponse, NotFoundError | AppError]:
        """Change sprint status.

        Args:
            sprint_id: Sprint identifier
            new_status: New sprint status

        Returns:
            Result containing updated sprint or error

        Example:
            result = await service.change_status("S-2025-01", SprintStatus.ACTIVE)
        """
        update_request = SprintUpdateRequest(status=new_status)
        return await self.update(sprint_id, update_request)

    async def get_current_sprints(
        self,
        current_date: date | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[SprintResponse], AppError]:
        """Get currently active sprints.

        Args:
            current_date: Date to check (default: today)
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing list of current sprints or error

        Example:
            result = await service.get_current_sprints()
            match result:
                case Ok(sprints):
                    print(f"Found {len(sprints)} active sprints")
        """
        result = await self.sprint_repo.find_current_sprints(
            current_date, limit, offset
        )

        match result:
            case Ok(sprints):
                responses = [
                    self.response_class.model_validate(sprint) for sprint in sprints
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def get_by_project(
        self,
        project_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[SprintResponse], AppError]:
        """Get sprints for project.

        Args:
            project_id: Project identifier
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing list of sprints or error

        Example:
            result = await service.get_by_project("P-TASKMAN")
        """
        result = await self.sprint_repo.find_by_project(
            project_id, status=None, limit=limit, offset=offset
        )

        match result:
            case Ok(sprints):
                responses = [
                    self.response_class.model_validate(sprint) for sprint in sprints
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def get_by_status(
        self,
        status: SprintStatus,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[SprintResponse], AppError]:
        """Get sprints by status.

        Args:
            status: Sprint status filter
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing list of sprints or error

        Example:
            result = await service.get_by_status(SprintStatus.ACTIVE)
        """
        result = await self.sprint_repo.find_by_status(status, limit, offset)

        match result:
            case Ok(sprints):
                responses = [
                    self.response_class.model_validate(sprint) for sprint in sprints
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def update_metrics(
        self,
        sprint_id: str,
    ) -> Result[SprintResponse, NotFoundError | AppError]:
        """Update sprint metrics fields.

        Recalculates and updates:
        - actual_points (from completed tasks)
        - Velocity metrics

        Args:
            sprint_id: Sprint identifier

        Returns:
            Result containing updated sprint or error

        Example:
            result = await service.update_metrics("S-2025-01")
        """
        # Calculate current velocity
        velocity_result = await self.calculate_velocity(sprint_id)

        match velocity_result:
            case Err(error):
                return Err(error)
            case Ok(actual_points):
                # Update sprint with calculated metrics
                update_request = SprintUpdateRequest(actual_points=actual_points)
                return await self.update(sprint_id, update_request)

    # =========================================================================
    # Phase Query Methods
    # =========================================================================

    async def get_by_phase_status(
        self,
        phase_name: str,
        phase_status: PhaseStatus,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[SprintResponse], AppError]:
        """Get sprints by phase status.

        Args:
            phase_name: Phase name (planning, implementation)
            phase_status: Phase status to filter by
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing sprints in specified phase status or error

        Example:
            result = await service.get_by_phase_status("planning", PhaseStatus.IN_PROGRESS)
            match result:
                case Ok(sprints):
                    print(f"Found {len(sprints)} sprints in planning phase")
        """
        result = await self.sprint_repo.find_by_phase_status(
            phase_name, phase_status, limit, offset
        )

        match result:
            case Ok(sprints):
                responses = [
                    self.response_class.model_validate(sprint) for sprint in sprints
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def get_with_blocked_phases(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[SprintResponse], AppError]:
        """Get sprints that have any phase blocked.

        Args:
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing sprints with blocked phases or error

        Example:
            result = await service.get_with_blocked_phases()
            match result:
                case Ok(sprints):
                    print(f"Found {len(sprints)} sprints with blocked phases")
        """
        result = await self.sprint_repo.find_with_blocked_phase(limit, offset)

        match result:
            case Ok(sprints):
                responses = [
                    self.response_class.model_validate(sprint) for sprint in sprints
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def get_by_current_phase(
        self,
        phase_name: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[SprintResponse], AppError]:
        """Get sprints currently in a specific phase (phase is in_progress).

        Args:
            phase_name: Phase name to check as current
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing sprints in the specified phase or error

        Example:
            result = await service.get_by_current_phase("implementation")
            match result:
                case Ok(sprints):
                    print(f"Found {len(sprints)} sprints in implementation phase")
        """
        result = await self.sprint_repo.find_by_current_phase(phase_name, limit, offset)

        match result:
            case Ok(sprints):
                responses = [
                    self.response_class.model_validate(sprint) for sprint in sprints
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)
