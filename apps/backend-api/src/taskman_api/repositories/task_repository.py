"""
Task Repository.

Data access layer for Task entities.
"""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.errors import AppError, NotFoundError
from taskman_api.core.result import Err, Ok, Result
from taskman_api.models.task import Task
from taskman_api.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """Repository for Task entity operations."""

    model_class = Task

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def exists(self, entity_id: str | UUID) -> bool:
        """Check if task exists by ID."""
        result = await self.session.execute(
            select(func.count()).select_from(Task).where(Task.id == entity_id)
        )
        return (result.scalar() or 0) > 0

    async def get_by_status(self, status: str, limit: int = 100) -> list[Task]:
        """Get tasks by status."""
        result = await self.session.execute(select(Task).where(Task.status == status).limit(limit))
        return list(result.scalars().all())

    async def get_by_project(self, project_id: str, limit: int = 100) -> list[Task]:
        """Get tasks by primary project ID."""
        result = await self.session.execute(
            select(Task).where(Task.primary_project == project_id).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_sprint(self, sprint_id: str, limit: int = 100) -> list[Task]:
        """Get tasks by primary sprint ID."""
        result = await self.session.execute(
            select(Task).where(Task.primary_sprint == sprint_id).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_assignee(self, assignee: str, limit: int = 100) -> list[Task]:
        """Get tasks assigned to a specific user."""
        result = await self.session.execute(
            select(Task).where(Task.assignee == assignee).limit(limit)
        )
        return list(result.scalars().all())

    async def search(
        self,
        status: str | None = None,
        priority: str | None = None,
        project_id: str | None = None,
        sprint_id: str | None = None,
        assignee: str | None = None,
        owner: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Task], int]:
        """
        Search tasks with multiple filters.

        Returns: (tasks, total_count)
        """
        query = select(Task)

        # Apply filters
        if status:
            query = query.where(Task.status == status)
        if priority:
            query = query.where(Task.priority == priority)
        if project_id:
            query = query.where(Task.primary_project == project_id)
        if sprint_id:
            query = query.where(Task.primary_sprint == sprint_id)
        if assignee:
            query = query.where(Task.assignee == assignee)
        if owner:
            query = query.where(Task.owner == owner)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)

        return list(result.scalars().all()), total

    async def create_task(
        self,
        id: str,
        title: str,
        summary: str,
        description: str,
        owner: str,
        primary_project: str,
        primary_sprint: str,
        status: str = "new",
        priority: str = "p2",
        severity: str | None = None,
        assignees: list[str] | None = None,
        related_projects: list[str] | None = None,
        related_sprints: list[str] | None = None,
        estimate_points: float | None = None,
        actual_time_hours: float | None = None,
        due_at: str | None = None,
        parents: list[str] | None = None,
        depends_on: list[str] | None = None,
        blocks: list[str] | None = None,
        blockers: list | None = None,
        acceptance_criteria: list | None = None,
        definition_of_done: list[str] | None = None,
        quality_gates: dict | None = None,
        verification: dict | None = None,
        actions_taken: list | None = None,
        labels: list[str] | None = None,
        related_links: list | None = None,
        shape: str | None = None,
        stage: str | None = None,
        work_type: str | None = None,
        work_stream: str | None = None,
        business_value_score: int | None = None,
        cost_of_delay_score: int | None = None,
        automation_candidate: bool = False,
        cycle_time_days: float | None = None,
        risks: list | None = None,
        observability: dict | None = None,
        **kwargs,  # Accept any extra fields
    ) -> Task:
        """Create a new task with all fields from the full schema."""
        task = Task(
            id=id,
            title=title,
            summary=summary or "",
            description=description or "",
            owner=owner or "",
            primary_project=primary_project or "",
            primary_sprint=primary_sprint or "",
            status=status,
            priority=priority,
            severity=severity,
            assignees=assignees or [],
            related_projects=related_projects or [],
            related_sprints=related_sprints or [],
            estimate_points=estimate_points,
            actual_time_hours=actual_time_hours,
            parents=parents or [],
            depends_on=depends_on or [],
            blocks=blocks or [],
            blockers=blockers or [],
            acceptance_criteria=acceptance_criteria or [],
            definition_of_done=definition_of_done or [],
            quality_gates=quality_gates or {},
            verification=verification or {},
            actions_taken=actions_taken or [],
            labels=labels or [],
            related_links=related_links or [],
            shape=shape,
            stage=stage,
            work_type=work_type,
            work_stream=work_stream,
            business_value_score=business_value_score,
            cost_of_delay_score=cost_of_delay_score,
            automation_candidate=automation_candidate,
            cycle_time_days=cycle_time_days,
            risks=risks or [],
            observability=observability or {},
        )
        return await self.create(task)

    async def update_task(
        self,
        task: Task,
        title: str | None = None,
        summary: str | None = None,
        description: str | None = None,
        status: str | None = None,
        owner: str | None = None,
        assignees: list[str] | None = None,
        priority: str | None = None,
        severity: str | None = None,
        primary_project: str | None = None,
        primary_sprint: str | None = None,
        estimate_points: float | None = None,
        actual_time_hours: float | None = None,
        labels: list[str] | None = None,
        **kwargs,  # Accept any extra fields dynamically
    ) -> Task:
        """Update task fields (only non-None values)."""
        if title is not None:
            task.title = title
        if summary is not None:
            task.summary = summary
        if description is not None:
            task.description = description
        if status is not None:
            task.status = status
        if owner is not None:
            task.owner = owner
        if assignees is not None:
            task.assignees = assignees
        if priority is not None:
            task.priority = priority
        if severity is not None:
            task.severity = severity
        if primary_project is not None:
            task.primary_project = primary_project
        if primary_sprint is not None:
            task.primary_sprint = primary_sprint
        if estimate_points is not None:
            task.estimate_points = estimate_points
        if actual_time_hours is not None:
            task.actual_time_hours = actual_time_hours
        if labels is not None:
            task.labels = labels

        # Handle legacy or dynamic fields via kwargs if safe
        for key, value in kwargs.items():
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)

        return await self.update(task)

    async def find_high_priority_tasks(self, limit: int = 100, offset: int = 0) -> list[Task]:
        """Get high priority tasks (P0, P1)."""
        result = await self.session.execute(
            select(Task).where(Task.priority.in_(["p0", "p1"])).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    # find_prefix methods returning Result for Service Layer
    async def find_by_id(self, entity_id: str | UUID) -> Result[Task, NotFoundError]:
        """Find task by ID with Result wrapper."""
        task = await self.get_by_id(entity_id)
        if task is None:
            return Err(
                NotFoundError(
                    message=f"Task not found: {entity_id}",
                    entity_id=str(entity_id),
                    entity_type="Task",
                )
            )
        return Ok(task)

    async def find_by_project(
        self, project_id: str, status: str | None = None, limit: int = 100, offset: int = 0
    ) -> Result[list[Task], AppError]:
        """Find tasks by project with Result wrapper."""
        try:
            tasks, _ = await self.search(
                project_id=project_id, status=status, limit=limit, offset=offset
            )
            return Ok(tasks)
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def find_by_sprint(
        self, sprint_id: str, status: str | None = None, limit: int = 100, offset: int = 0
    ) -> Result[list[Task], AppError]:
        """Find tasks by sprint with Result wrapper."""
        try:
            tasks, _ = await self.search(
                sprint_id=sprint_id, status=status, limit=limit, offset=offset
            )
            return Ok(tasks)
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def find_by_status(
        self, status: str, limit: int = 100, offset: int = 0
    ) -> Result[list[Task], AppError]:
        """Find tasks by status with Result wrapper."""
        try:
            tasks, _ = await self.search(status=status, limit=limit, offset=offset)
            return Ok(tasks)
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def find_by_priority(
        self, priority: str, limit: int = 100, offset: int = 0
    ) -> Result[list[Task], AppError]:
        """Find tasks by priority with Result wrapper."""
        try:
            tasks, _ = await self.search(priority=priority, limit=limit, offset=offset)
            return Ok(tasks)
        except Exception as e:
            return Err(AppError(message=str(e)))
