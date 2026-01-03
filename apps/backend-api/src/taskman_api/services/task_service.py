"""Task service with business logic and validation.

Handles task operations, status transitions, and task management.
"""


from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.enums import Priority, TaskStatus
from taskman_api.core.errors import (
    AppError,
    NotFoundError,
    ValidationError,
)
from taskman_api.core.result import Err, Ok, Result
from taskman_api.db.session import manager
from taskman_api.models.task import Task
from taskman_api.repositories.postgres_task_repository import PostgresTaskRepository
from taskman_api.repositories.project_repository import ProjectRepository
from taskman_api.repositories.sprint_repository import SprintRepository
from taskman_api.repositories.task_repository import TaskRepository
from taskman_api.schemas.task import TaskCreateRequest, TaskResponse, TaskUpdateRequest

from .base import BaseService


class TaskService(BaseService[Task, TaskCreateRequest, TaskUpdateRequest, TaskResponse]):
    """Task business logic and operations.

    Provides task management functionality including:
    - CRUD operations (inherited from BaseService)
    - Status transition validation
    - Sprint assignment
    - Bulk operations
    - Advanced search with filters

    Example:
        service = TaskService(session)
        result = await service.create(TaskCreateRequest(...))
        match result:
            case Ok(task):
                print(f"Created task: {task.id}")
            case Err(error):
                print(f"Failed: {error.message}")
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize TaskService with session.

        Args:
            session: Async database session
        """
        if not manager._using_fallback:
            repository = PostgresTaskRepository(session)
        else:
            repository = TaskRepository(session)
        super().__init__(repository, Task, TaskResponse)
        self.task_repo = repository  # Type-specific repository access
        self.project_repo = ProjectRepository(session)
        self.sprint_repo = SprintRepository(session)

    async def create(
        self, create_data: TaskCreateRequest
    ) -> Result[TaskResponse, ValidationError | AppError]:
        """Create new task with validation.

        Args:
            create_data: Task creation data

        Returns:
            Result containing created task or error
        """
        # Validate project exists
        project = await self.project_repo.get_by_id(create_data.primary_project)
        if not project:
            return Err(
                NotFoundError(
                    message=f"Project not found: {create_data.primary_project}",
                    entity_type="Project",
                    entity_id=create_data.primary_project,
                )
            )

        # Validate sprint exists
        sprint = await self.sprint_repo.get_by_id(create_data.primary_sprint)
        if not sprint:
            return Err(
                NotFoundError(
                    message=f"Sprint not found: {create_data.primary_sprint}",
                    entity_type="Sprint",
                    entity_id=create_data.primary_sprint,
                )
            )

        return await super().create(create_data)

    async def update(
        self,
        id: str,
        update_data: TaskUpdateRequest,
    ) -> Result[TaskResponse, NotFoundError | ValidationError | AppError]:
        """Update task with validation.

        Args:
            id: Task identifier
            update_data: Task update data

        Returns:
            Result containing updated task or error
        """
        # Validate project exists if being updated
        if update_data.primary_project:
            project = await self.project_repo.get_by_id(update_data.primary_project)
            if not project:
                return Err(
                    NotFoundError(
                        message=f"Project not found: {update_data.primary_project}",
                        entity_type="Project",
                        entity_id=update_data.primary_project,
                    )
                )

        # Validate sprint exists if being updated
        if update_data.primary_sprint:
            sprint = await self.sprint_repo.get_by_id(update_data.primary_sprint)
            if not sprint:
                return Err(
                    NotFoundError(
                        message=f"Sprint not found: {update_data.primary_sprint}",
                        entity_type="Sprint",
                        entity_id=update_data.primary_sprint,
                    )
                )

        return await super().update(id, update_data)

    async def change_status(
        self,
        task_id: str,
        new_status: TaskStatus,
    ) -> Result[TaskResponse, NotFoundError | ValidationError | AppError]:
        """Change task status with transition validation.

        Validates status transitions according to allowed state machine:
        - NEW → READY, DROPPED
        - READY → IN_PROGRESS, DROPPED
        - IN_PROGRESS → BLOCKED, REVIEW, DONE, DROPPED
        - BLOCKED → IN_PROGRESS, DROPPED
        - REVIEW → IN_PROGRESS, DONE, DROPPED
        - DONE → (terminal state)
        - DROPPED → (terminal state)

        Args:
            task_id: Task identifier
            new_status: New status to set

        Returns:
            Result containing updated task or validation error

        Example:
            result = await service.change_status("T-001", TaskStatus.IN_PROGRESS)
            match result:
                case Ok(task):
                    print(f"Status changed to {task.status}")
                case Err(ValidationError() as error):
                    print(f"Invalid transition: {error.message}")
        """
        # Get current task
        get_result = await self.get(task_id)

        match get_result:
            case Err(error):
                return Err(error)
            case Ok(task_response):
                # Validate status transition
                current_status = task_response.status
                if not self._is_valid_transition(current_status, new_status):
                    return Err(
                        ValidationError(
                            message=f"Invalid status transition: {current_status.value} -> {new_status.value}",
                            field="status",
                            value=new_status.value,
                        )
                    )

                # Update status
                update_request = TaskUpdateRequest(status=new_status)
                return await self.update(task_id, update_request)

    def _is_valid_transition(
        self,
        current: TaskStatus,
        new: TaskStatus,
    ) -> bool:
        """Validate status transition rules.

        Transition Matrix:
        - NEW → READY, DROPPED
        - READY → IN_PROGRESS, DROPPED
        - IN_PROGRESS → BLOCKED, REVIEW, DONE, DROPPED
        - BLOCKED → IN_PROGRESS, DROPPED
        - REVIEW → IN_PROGRESS, DONE, DROPPED
        - DONE → (no transitions)
        - DROPPED → (no transitions)

        Args:
            current: Current task status
            new: Requested new status

        Returns:
            True if transition is valid, False otherwise
        """
        valid_transitions: dict[TaskStatus, list[TaskStatus]] = {
            TaskStatus.NEW: [TaskStatus.READY, TaskStatus.DROPPED],
            TaskStatus.READY: [TaskStatus.IN_PROGRESS, TaskStatus.DROPPED],
            TaskStatus.IN_PROGRESS: [
                TaskStatus.BLOCKED,
                TaskStatus.REVIEW,
                TaskStatus.DONE,
                TaskStatus.DROPPED,
            ],
            TaskStatus.BLOCKED: [TaskStatus.IN_PROGRESS, TaskStatus.DROPPED],
            TaskStatus.REVIEW: [
                TaskStatus.IN_PROGRESS,
                TaskStatus.DONE,
                TaskStatus.DROPPED,
            ],
            TaskStatus.DONE: [],  # Terminal state
            TaskStatus.DROPPED: [],  # Terminal state
        }

        return new in valid_transitions.get(current, [])

    async def assign_to_sprint(
        self,
        task_id: str,
        sprint_id: str,
    ) -> Result[TaskResponse, NotFoundError | AppError]:
        """Assign task to sprint.

        Sets the primary_sprint field for the task.

        Args:
            task_id: Task identifier
            sprint_id: Sprint identifier

        Returns:
            Result containing updated task or error

        Example:
            result = await service.assign_to_sprint("T-001", "S-2025-01")
            match result:
                case Ok(task):
                    print(f"Task assigned to sprint: {task.primary_sprint}")
                case Err(error):
                    print(f"Assignment failed: {error.message}")
        """
        update_request = TaskUpdateRequest(primary_sprint=sprint_id)
        return await self.update(task_id, update_request)

    async def assign_to_project(
        self,
        task_id: str,
        project_id: str,
    ) -> Result[TaskResponse, NotFoundError | AppError]:
        """Assign task to project.

        Sets the primary_project field for the task.

        Args:
            task_id: Task identifier
            project_id: Project identifier

        Returns:
            Result containing updated task or error

        Example:
            result = await service.assign_to_project("T-001", "P-TASKMAN")
            match result:
                case Ok(task):
                    print(f"Task assigned to project: {task.primary_project}")
        """
        update_request = TaskUpdateRequest(primary_project=project_id)
        return await self.update(task_id, update_request)

    async def bulk_update(
        self,
        updates: list[dict],
    ) -> Result[list[TaskResponse], AppError]:
        """Bulk update multiple tasks.

        Applies updates to multiple tasks in sequence.
        Fails fast on first error (returns immediately).

        Args:
            updates: List of dicts with {id: str, ...fields}

        Returns:
            Result containing list of updated tasks or error

        Example:
            updates = [
                {"id": "T-001", "status": "in_progress"},
                {"id": "T-002", "priority": "high"},
            ]
            result = await service.bulk_update(updates)
            match result:
                case Ok(tasks):
                    print(f"Updated {len(tasks)} tasks")
                case Err(error):
                    print(f"Bulk update failed: {error.message}")
        """
        results: list[TaskResponse] = []

        for update_data in updates:
            # Extract ID from update dict
            task_id = update_data.pop("id")

            # Create update request from remaining fields
            update_request = TaskUpdateRequest(**update_data)

            # Update task
            result = await self.update(task_id, update_request)

            match result:
                case Ok(task):
                    results.append(task)
                case Err(error):
                    # Fail fast on first error
                    return Err(error)

        return Ok(results)

    async def search(
        self,
        status: TaskStatus | None = None,
        priority: Priority | None = None,
        owner: str | None = None,
        project_id: str | None = None,
        sprint_id: str | None = None,
        assignee: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[tuple[list[TaskResponse], int], AppError]:
        """Search tasks with filters.

        Delegates to repository for efficient DB-side filtering and counting.

        Args:
            status: Optional status filter
            priority: Optional priority filter
            owner: Optional owner username filter
            project_id: Optional project ID filter
            sprint_id: Optional sprint ID filter
            assignee: Optional assignee filter
            limit: Maximum results (default: 100, max: 1000)
            offset: Results to skip (default: 0)

        Returns:
            Result containing (tasks, total_count) or error
        """
        try:
            # Convert Query params handling (repo expects str for enums often, but SQLAlchemy handles enums too)
            # The repo signature expects str|None for most.
            # TaskStatus and Priority are Enums in generic code but DB might be strict.
            # TaskRepo signature has str | None for status/priority.

            # The repository 'search' method handles flexible arguments.
            # We must ensure we pass arguments that match the repo's expected types.
            # TaskRepo.search definition:
            # status: str | None
            # priority: str | None
            # project_id, sprint_id, assignee...

            repo_status = status.value if status else None
            repo_priority = priority.value if priority else None

            tasks, total = await self.task_repo.search(
                status=repo_status,
                priority=repo_priority,
                project_id=project_id,
                sprint_id=sprint_id,
                assignee=assignee,
                owner=owner,  # Added assignee to service method arg too
                limit=limit,
                offset=offset,
            )

            responses = [
                self.response_class.model_validate(self._deserialize_json_fields(task))
                for task in tasks
            ]

            return Ok((responses, total))

        except Exception as e:
            return Err(AppError(message=str(e)))

    async def get_high_priority_tasks(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[TaskResponse], AppError]:
        """Get high-priority tasks (P0, P1).

        Args:
            limit: Maximum results (default: 100)
            offset: Results to skip (default: 0)

        Returns:
            Result containing high-priority tasks or error

        Example:
            result = await service.get_high_priority_tasks(limit=20)
            match result:
                case Ok(tasks):
                    print(f"Found {len(tasks)} critical tasks")
        """
        try:
            tasks = await self.task_repo.find_high_priority_tasks(limit, offset)
            responses = [
                self.response_class.model_validate(self._deserialize_json_fields(task))
                for task in tasks
            ]
            return Ok(responses)
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def get_blocked_tasks(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[TaskResponse], AppError]:
        """Get all blocked tasks.

        Args:
            limit: Maximum results (default: 100)
            offset: Results to skip (default: 0)

        Returns:
            Result containing blocked tasks or error

        Example:
            result = await service.get_blocked_tasks()
            match result:
                case Ok(tasks):
                    for task in tasks:
                        print(f"Blocked: {task.title}")
        """
        result = await self.task_repo.find_by_status(
            TaskStatus.BLOCKED, limit, offset
        )

        match result:
            case Ok(tasks):
                responses = [
                    self.response_class.model_validate(task) for task in tasks
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)
