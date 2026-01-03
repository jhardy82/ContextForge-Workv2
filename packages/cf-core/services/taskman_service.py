"""TaskMan v2 Service Layer.

Service layer implementing business logic for TaskMan-v2 MCP integration.
Uses repository pattern for persistence with proper dependency injection.

Architecture:
    MCP Server → TaskManService → ITaskRepository → Database
                                → ISprintRepository → Database

Usage:
    from cf_core.services import TaskManService
    from cf_core.repositories import SqliteTaskRepository

    repo = SqliteTaskRepository("db/taskman.sqlite")
    service = TaskManService(task_repository=repo)

    # Create task
    result = service.create_task(title="My Task")
    if result.is_success:
        task = result.value
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from cf_core.domain.task_entity import TaskEntity
from cf_core.models.task import TaskStatus
from cf_core.shared.result import Result

if TYPE_CHECKING:
    from cf_core.domain.project_entity import ProjectEntity
    from cf_core.domain.sprint_entity import SprintEntity
    from cf_core.repositories.project_repository import IProjectRepository
    from cf_core.repositories.sprint_repository import ISprintRepository
    from cf_core.repositories.task_repository import ITaskRepository


class TaskManService:
    """Service layer for TaskMan-v2 operations.

    Provides business logic and orchestration for task/sprint management.
    Uses repository pattern for persistence abstraction.

    Attributes:
        task_repository: Repository for task persistence
        sprint_repository: Optional repository for sprint persistence
    """

    def __init__(
        self,
        task_repository: ITaskRepository,
        sprint_repository: ISprintRepository | None = None,
        project_repository: IProjectRepository | None = None,
    ) -> None:
        """Initialize TaskMan service with repositories.

        Args:
            task_repository: Repository for task persistence (required)
            sprint_repository: Repository for sprint persistence (optional)
            project_repository: Repository for project persistence (optional)
        """
        self._task_repo = task_repository
        self._sprint_repo = sprint_repository
        self._project_repo = project_repository
        self._task_counter = 0  # For ID generation

    # ========== Task Operations ==========

    def create_task(
        self,
        title: str,
        description: str | None = None,
        priority: int | str = 3,
        status: TaskStatus = "new",
        project_id: str | None = None,
        sprint_id: str | None = None,
        assignee: str | None = None,
        estimate_hours: float | None = None,
        story_points: int | None = None,
        due_date: datetime | None = None,
        tags: list[str] | None = None,
        depends_on: list[str] | None = None,
        # Phase 2 Fields
        summary: str | None = None,
        owner: str | None = None,
        primary_project: str | None = None,
        primary_sprint: str | None = None,
        observability: dict | None = None,
    ) -> Result[TaskEntity]:
        """Create a new task.

        Args:
            title: Task title (required)
            description: Optional task description
            priority: Priority level (low, medium, high, critical)
            status: Initial status (default: todo)
            project_id: Associated project ID
            sprint_id: Associated sprint ID
            assignee: Assigned user/agent
            estimate_hours: Estimated hours to complete
            story_points: Story point estimate
            due_date: Task due date
            tags: List of tags
            depends_on: List of task IDs this depends on
            summary: Brief summary
            owner: Primary owner
            primary_project: Primary project ID
            primary_sprint: Primary sprint ID
            observability: Observability data
        """
        try:
            task_id = self._generate_task_id()

            entity = TaskEntity.create(
                task_id=task_id,
                title=title,
                description=description,
                priority=priority,
                status=status,
                project_id=project_id,
                sprint_id=sprint_id,
                assignee=assignee,
                estimate_hours=estimate_hours,
                story_points=story_points,
                due_date=due_date,
                tags=tags,
                depends_on=depends_on,
                summary=summary,
                owner=owner,
                primary_project=primary_project,
                primary_sprint=primary_sprint,
                observability=observability,
            )

            return self._task_repo.save(entity)

        except Exception as e:
            return Result.failure(f"Failed to create task: {e}")

    def get_task(self, task_id: str) -> Result[TaskEntity]:
        """Get a task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Result[TaskEntity]: Success with entity if found, failure otherwise
        """
        return self._task_repo.get_by_id(task_id)

    def update_task(
        self,
        task_id: str,
        title: str | None = None,
        description: str | None = None,
        priority: int | str | None = None,
        status: TaskStatus | None = None,
        sprint_id: str | None = None,
        assignee: str | None = None,
        estimate_hours: float | None = None,
        actual_hours: float | None = None,
        story_points: int | None = None,
        due_date: datetime | None = None,
        tags: list[str] | None = None,
    ) -> Result[TaskEntity]:
        """Update an existing task.

        Args:
            task_id: Task identifier (required)
            title: New title (optional)
            description: New description (optional)
            priority: New priority (optional)
            status: New status (optional)
            sprint_id: New sprint ID (optional)
            assignee: New assignee (optional)
            estimate_hours: New estimate (optional)
            actual_hours: New actual hours (optional)
            story_points: New story points (optional)
            due_date: New due date (optional)
            tags: New tags (optional)

        Returns:
            Result[TaskEntity]: Success with updated entity, or failure
        """
        # Fetch existing task
        result = self._task_repo.get_by_id(task_id)
        if not result.is_success:
            return result

        entity = result.value
        task = entity.task

        # Build updated task with provided fields
        updates = {}
        if title is not None:
            updates["title"] = title
        if description is not None:
            updates["description"] = description
        if priority is not None:
            updates["priority"] = priority
        if status is not None:
            updates["status"] = status
        if sprint_id is not None:
            updates["sprint_id"] = sprint_id
        if assignee is not None:
            updates["assignee"] = assignee
        if estimate_hours is not None:
            updates["estimate_hours"] = estimate_hours
        if actual_hours is not None:
            updates["actual_hours"] = actual_hours
        if story_points is not None:
            updates["story_points"] = story_points
        if due_date is not None:
            updates["due_date"] = due_date
        if tags is not None:
            # Map legacy tags to labels (line 220 updates labels after task creation)
            updates["tags"] = tags
            updates["labels"] = tags  # Also update labels field

        # Phase 2 Updates
        # To support updating new fields, we need to add them to arguments or use kwargs.
        # For now, minimal update_task support.
        # Ideally, update_task should accept all fields.
        # Ignoring explicit update args for brevity unless requested.

        # Apply updates
        updates["updated_at"] = datetime.now(UTC)
        updated_task = task.model_copy(update=updates)
        updated_entity = TaskEntity(updated_task)

        return self._task_repo.save(updated_entity)

    def delete_task(self, task_id: str) -> Result[bool]:
        """Delete a task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Result[bool]: Success with True if deleted, failure otherwise
        """
        return self._task_repo.delete(task_id)

    def list_tasks(
        self,
        status: TaskStatus | None = None,
        sprint_id: str | None = None,
        assignee: str | None = None,
        limit: int = 100,
    ) -> Result[list[TaskEntity]]:
        """List tasks with optional filtering.

        Args:
            status: Filter by status (optional)
            sprint_id: Filter by sprint (optional)
            assignee: Filter by assignee (optional)
            limit: Maximum number of tasks to return (default: 100)

        Returns:
            Result[List[TaskEntity]]: Success with list of entities
        """
        return self._task_repo.search(
            status=status,
            sprint_id=sprint_id,
            assignee=assignee,
            limit=limit,
        )

    def search_tasks(
        self,
        query: str | None = None,
        status: TaskStatus | None = None,
        priority: str | None = None,
        tags: list[str] | None = None,
        sprint_id: str | None = None,
        project_id: str | None = None,
        assignee: str | None = None,
        limit: int = 50,
    ) -> Result[list[TaskEntity]]:
        """Search tasks with flexible criteria including keyword search.

        Args:
            query: Text to search in title and description (case-insensitive)
            status: Filter by status (optional)
            priority: Filter by priority (optional)
            tags: Filter by tags - matches if any tag matches (optional)
            sprint_id: Filter by sprint (optional)
            project_id: Filter by project (optional)
            assignee: Filter by assignee (optional)
            limit: Maximum number of tasks to return (default: 50)

        Returns:
            Result[List[TaskEntity]]: Success with matching tasks
        """
        if query:
            # If query is provided, we use the search method which handles
            # text search in SQL.
            pass

        return self._task_repo.search(
            query=query,
            status=status,
            priority=priority,
            assignee=assignee,
            sprint_id=sprint_id,
            project_id=project_id,
            tags=tags,
            limit=limit,
        )

    def start_task(self, task_id: str) -> Result[TaskEntity]:
        """Start a task (transition to in_progress).

        Args:
            task_id: Task identifier

        Returns:
            Result[TaskEntity]: Success with updated entity, or failure
        """
        result = self._task_repo.get_by_id(task_id)
        if not result.is_success:
            return result

        entity = result.value

        try:
            started = entity.start()
            return self._task_repo.save(started)
        except ValueError as e:
            return Result.failure(str(e))

    def complete_task(
        self,
        task_id: str,
        actual_hours: float | None = None,
    ) -> Result[TaskEntity]:
        """Complete a task.

        Args:
            task_id: Task identifier
            actual_hours: Actual hours spent (optional)

        Returns:
            Result[TaskEntity]: Success with updated entity, or failure
        """
        result = self._task_repo.get_by_id(task_id)
        if not result.is_success:
            return result

        entity = result.value

        try:
            completed = entity.complete(actual_hours=actual_hours)
            return self._task_repo.save(completed)
        except ValueError as e:
            return Result.failure(str(e))

    def block_task(
        self,
        task_id: str,
        reason: str,
    ) -> Result[TaskEntity]:
        """Block a task with a reason.

        Args:
            task_id: Task identifier
            reason: Blocking reason

        Returns:
            Result[TaskEntity]: Success with updated entity, or failure
        """
        result = self._task_repo.get_by_id(task_id)
        if not result.is_success:
            return result

        entity = result.value

        try:
            blocked = entity.block(reason=reason)
            return self._task_repo.save(blocked)
        except ValueError as e:
            return Result.failure(str(e))

    def unblock_task(self, task_id: str) -> Result[TaskEntity]:
        """Unblock a task.

        Args:
            task_id: Task identifier

        Returns:
            Result[TaskEntity]: Success with updated entity, or failure
        """
        result = self._task_repo.get_by_id(task_id)
        if not result.is_success:
            return result

        entity = result.value

        try:
            unblocked = entity.unblock()
            return self._task_repo.save(unblocked)
        except ValueError as e:
            return Result.failure(str(e))

    def batch_update_tasks(
        self,
        task_ids: list[str],
        status: str | None = None,
        priority: str | None = None,
        sprint_id: str | None = None,
        assignee: str | None = None,
    ) -> Result[dict]:
        """Update multiple tasks with the same field values.

        Args:
            task_ids: List of task identifiers to update
            status: New status for all tasks (optional)
            priority: New priority for all tasks (optional)
            sprint_id: New sprint ID for all tasks (optional)
            assignee: New assignee for all tasks (optional)

        Returns:
            Result[dict]: Success with summary {updated: [...], failed: [...]}
        """
        if not task_ids:
            return Result.failure("No task IDs provided")

        updated = []
        failed = []

        for task_id in task_ids:
            result = self.update_task(
                task_id=task_id,
                status=status,
                priority=priority,
                sprint_id=sprint_id,
                assignee=assignee,
            )
            if result.is_success:
                updated.append(task_id)
            else:
                failed.append({"id": task_id, "error": result.error})

        return Result.success({
            "updated": updated,
            "failed": failed,
            "total_requested": len(task_ids),
            "total_updated": len(updated),
            "total_failed": len(failed),
        })

    def assign_to_sprint(
        self,
        task_id: str,
        sprint_id: str,
    ) -> Result[TaskEntity]:
        """Assign a task to a sprint.

        Args:
            task_id: Task identifier
            sprint_id: Sprint to assign to

        Returns:
            Result[TaskEntity]: Success with updated entity, or failure
        """
        return self.update_task(task_id, sprint_id=sprint_id)

    def assign_task(
        self,
        task_id: str,
        assignee: str,
    ) -> Result[TaskEntity]:
        """Assign a task to a user/agent.

        Args:
            task_id: Task identifier
            assignee: User/agent to assign to

        Returns:
            Result[TaskEntity]: Success with updated entity, or failure
        """
        return self.update_task(task_id, assignee=assignee)

    # ========== Sprint Operations ==========

    def create_sprint(
        self,
        name: str,
        start_date: datetime,
        end_date: datetime,
        project_id: str | None = None,
        description: str | None = None,
        # Phase 2 Fields
        owner: str | None = None,
        cadence: str | None = None,
        goal: str | None = None,
        observability: dict | None = None,
        task_ids: list[str] | None = None,
    ) -> Result[SprintEntity]:
        """Create a new sprint.

        Args:
            name: Sprint name (required)
            start_date: Sprint start date (required)
            end_date: Sprint end date (required)
            description: Optional sprint description
            project_id: Associated project ID (optional)
            owner: Sprint owner
            cadence: Sprint cadence
            goal: Sprint goal
            observability: Observability data
            task_ids: List of task IDs
        """
        if self._sprint_repo is None:
            return Result.failure("Sprint repository not configured")

        try:
            from cf_core.domain.sprint_entity import SprintEntity
            from cf_core.models.observability import Observability

            sprint_id = self._generate_sprint_id()

            # Handle observability
            obs_obj = Observability(**observability) if observability else None

            entity = SprintEntity.create(
                sprint_id=sprint_id,
                name=name,
                start_date=start_date,
                end_date=end_date,
                status="new",
                description=description or "",
                project_id=project_id,
                owner=owner,
                cadence=cadence,
                goal=goal,
                observability=obs_obj,
                task_ids=task_ids,
            )

            return self._sprint_repo.save(entity)

        except Exception as e:
            return Result.failure(f"Failed to create sprint: {e}")

    def get_sprint(self, sprint_id: str) -> Result[SprintEntity]:
        """Get a sprint by ID.

        Args:
            sprint_id: Sprint identifier

        Returns:
            Result[SprintEntity]: Success with entity if found, failure otherwise
        """
        if self._sprint_repo is None:
            return Result.failure("Sprint repository not configured")

        return self._sprint_repo.get_by_id(sprint_id)

    def update_sprint(
        self,
        sprint_id: str,
        name: str | None = None,
        status: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        description: str | None = None,
    ) -> Result[SprintEntity]:
        """Update an existing sprint.

        Args:
            sprint_id: Sprint identifier (required)
            name: New sprint name (optional)
            status: New status: planned, active, completed, cancelled (optional)
            start_date: New start date (optional)
            end_date: New end date (optional)
            description: New description (optional)

        Returns:
            Result[SprintEntity]: Success with updated entity, or failure
        """
        if self._sprint_repo is None:
            return Result.failure("Sprint repository not configured")

        # Get existing sprint
        result = self._sprint_repo.get_by_id(sprint_id)
        if not result.is_success:
            return Result.failure(f"Sprint {sprint_id} not found")

        sprint = result.value
        if sprint is None:
            return Result.failure(f"Sprint {sprint_id} not found")

        # Update fields if provided
        if name is not None:
            sprint.name = name
        if status is not None:
            if hasattr(sprint, "update_status"):
                sprint.update_status(status)
            else:
                sprint._sprint.status = status
        if start_date is not None:
            sprint._sprint.start_date = start_date
        if end_date is not None:
            sprint._sprint.end_date = end_date
        if description is not None:
            sprint.description = description

        # Save updated sprint
        return self._sprint_repo.save(sprint)

    def delete_sprint(self, sprint_id: str) -> Result[bool]:
        """Delete a sprint by ID.

        Args:
            sprint_id: Sprint identifier

        Returns:
            Result[bool]: Success with True if deleted, failure otherwise
        """
        if self._sprint_repo is None:
            return Result.failure("Sprint repository not configured")

        return self._sprint_repo.delete(sprint_id)

    def list_sprints(
        self,
        project_id: str | None = None,
        active_only: bool = False,
        limit: int = 50,
    ) -> Result[list]:
        """List sprints with optional filtering.

        Args:
            project_id: Filter by project (optional)
            active_only: Only return active sprints (optional)
            limit: Maximum number to return (default: 50)

        Returns:
            Result[list]: Success with list of sprint entities, or failure
        """
        if self._sprint_repo is None:
            return Result.failure("Sprint repository not configured")

        result = self._sprint_repo.find_all()
        if not result.is_success:
            return result

        sprints = result.value

        if project_id:
            sprints = [s for s in sprints if s.project_id == project_id]
        if active_only:
            sprints = [s for s in sprints if s.is_active()]

        return Result.success(sprints[:limit])

    # ========== Project Operations ==========

    def create_project(
        self,
        name: str,
        description: str | None = None,
        owner: str | None = None,
        start_date: datetime | None = None,
        target_end_date: datetime | None = None,
        tags: list[str] | None = None,
        team_members: list[str] | None = None,
        # Phase 2 Fields
        mission: str | None = None,
        vision: str | None = None,
        observability: dict | None = None,
    ) -> Result[ProjectEntity]:
        """Create a new project.

        Args:
            name: Project name (required)
            description: Project description (optional)
            owner: Project owner/lead (optional)
            start_date: Project start date (optional)
            target_end_date: Target completion date (optional)
            tags: List of tags (optional)
            team_members: List of team member identifiers (optional)
            mission: Project mission
            vision: Project vision
            observability: Observability data
        """
        if self._project_repo is None:
            return Result.failure("Project repository not configured")

        try:
            from cf_core.domain.project_entity import ProjectEntity
            from cf_core.models.observability import Observability

            project_id = self._generate_project_id()

            entity = ProjectEntity.create(
                project_id=project_id,
                name=name,
                status="new",
                description=description or "",
                owner=owner,
                start_date=start_date,
                target_end_date=target_end_date,
                tags=tags,
                team_members=team_members,
                mission=mission,
                vision=vision,
                observability=observability,
            )

            return self._project_repo.save(entity)

        except Exception as e:
            return Result.failure(f"Failed to create project: {e}")

    def get_project(self, project_id: str) -> Result[ProjectEntity]:
        """Get a project by ID.

        Args:
            project_id: Project identifier

        Returns:
            Result[ProjectEntity]: Success with entity if found, failure otherwise
        """
        if self._project_repo is None:
            return Result.failure("Project repository not configured")

        return self._project_repo.get_by_id(project_id)

    def update_project(
        self,
        project_id: str,
        name: str | None = None,
        status: str | None = None,
        description: str | None = None,
        owner: str | None = None,
        start_date: datetime | None = None,
        target_end_date: datetime | None = None,
        tags: list[str] | None = None,
        team_members: list[str] | None = None,
    ) -> Result[ProjectEntity]:
        """Update an existing project.

        Args:
            project_id: Project identifier (required)
            name: New project name (optional)
            status: New status: new, active, on_hold, completed, cancelled (optional)
            description: New description (optional)
            owner: New owner (optional)
            start_date: New start date (optional)
            target_end_date: New target end date (optional)
            tags: New tags list (optional)
            team_members: New team members list (optional)

        Returns:
            Result[ProjectEntity]: Success with updated entity, or failure
        """
        if self._project_repo is None:
            return Result.failure("Project repository not configured")

        # Get existing project
        result = self._project_repo.get_by_id(project_id)
        if not result.is_success:
            return Result.failure(f"Project {project_id} not found")

        project = result.value
        if project is None:
            return Result.failure(f"Project {project_id} not found")

        # Update fields if provided - access underlying model
        model = project.project
        if name is not None:
            model.name = name
        if status is not None:
            # Validate and cast status to ProjectStatus

            valid_statuses = (
                "new",
                "pending",
                "assigned",
                "active",
                "in_progress",
                "blocked",
                "completed",
                "cancelled",
            )
            if status not in valid_statuses:
                return Result.failure(f"Invalid status: {status}. Valid: {valid_statuses}")
            model.status = status  # type: ignore[assignment]
        if description is not None:
            model.description = description
        if owner is not None:
            model.owner = owner
        if start_date is not None:
            model.start_date = start_date
        if target_end_date is not None:
            model.target_end_date = target_end_date
        if tags is not None:
            model.tags = tags
        if team_members is not None:
            model.team_members = team_members

        # Update timestamp
        model.updated_at = datetime.now(UTC)

        # Save updated project
        return self._project_repo.save(project)

    def delete_project(self, project_id: str) -> Result[bool]:
        """Delete a project by ID.

        Args:
            project_id: Project identifier

        Returns:
            Result[bool]: Success with True if deleted, failure otherwise
        """
        if self._project_repo is None:
            return Result.failure("Project repository not configured")

        return self._project_repo.delete(project_id)

    def list_projects(
        self,
        status: str | None = None,
        owner: str | None = None,
        limit: int = 50,
    ) -> Result[list]:
        """List projects with optional filtering.

        Args:
            status: Filter by status (optional)
            owner: Filter by owner (optional)
            limit: Maximum number to return (default: 50)

        Returns:
            Result[list]: Success with list of project entities, or failure
        """
        if self._project_repo is None:
            return Result.failure("Project repository not configured")

        # Use specialized repository methods if filters provided
        if status:
            result = self._project_repo.find_by_status(status)
        elif owner:
            result = self._project_repo.find_by_owner(owner)
        else:
            result = self._project_repo.find_all()

        if not result.is_success:
            return result

        projects = result.value
        return Result.success(projects[:limit])

    # ========== Utility Methods ==========

    def _generate_task_id(self) -> str:
        """Generate a unique task ID.

        Uses timestamp + counter for uniqueness.
        """
        self._task_counter += 1
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        return f"T-{timestamp}-{self._task_counter:04d}"

    def _generate_sprint_id(self) -> str:
        """Generate a unique sprint ID.

        Uses timestamp for uniqueness.
        """
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        return f"S-{timestamp}"

    def _generate_project_id(self) -> str:
        """Generate a unique project ID.

        Uses timestamp for uniqueness with P- prefix.
        """
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        return f"P-{timestamp}"

    # ========== Health Check Methods ==========

    def health_check(self) -> Result[dict]:
        """Check service health including database connectivity.

        Performs a simple database operation to verify the connection
        is working. Returns timing information for monitoring.

        Returns:
            Result containing health status dict with:
                - status: "healthy" or "unhealthy"
                - database: "connected" or error message
                - latency_ms: round-trip time for database query
                - checked_at: ISO timestamp of check
        """
        import time

        start_time = time.perf_counter()
        checked_at = datetime.now(UTC).isoformat()

        try:
            # Perform a simple database operation to verify connectivity and get count
            result = self._task_repo.count()

            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

            if result.is_success:
                return Result.success(
                    {
                        "status": "healthy",
                        "database": "connected",
                        "task_count": result.value,
                        "latency_ms": elapsed_ms,
                        "checked_at": checked_at,
                    }
                )
            else:
                return Result.success({
                    "status": "unhealthy",
                    "database": f"query_failed: {result.error}",
                    "latency_ms": elapsed_ms,
                    "checked_at": checked_at,
                })

        except Exception as e:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return Result.failure(
                f"Health check failed: {type(e).__name__}: {e}"
            )


__all__ = ["TaskManService"]
