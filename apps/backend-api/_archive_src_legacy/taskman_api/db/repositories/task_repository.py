"""Task repository with task-specific queries.

Provides specialized queries for task filtering and analysis.
"""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.enums import PhaseStatus, Priority, TaskStatus
from taskman_api.core.errors import DatabaseError
from taskman_api.core.result import Err, Ok, Result
from taskman_api.db.models.task import Task

from .base import BaseRepository

# Valid task phases
TASK_PHASES = ["research", "planning", "implementation", "testing"]


class TaskRepository(BaseRepository[Task]):
    """Repository for Task entity with specialized queries.

    Example:
        ```python
        async with get_db() as session:
            repo = TaskRepository(session)
            tasks = await repo.find_by_status(TaskStatus.IN_PROGRESS)
        ```
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize task repository.

        Args:
            session: Async database session
        """
        super().__init__(Task, session)

    async def find_by_status(
        self,
        status: TaskStatus,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Task], DatabaseError]:
        """Find tasks by status.

        Args:
            status: Task status to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of tasks or error
        """
        try:
            stmt = (
                select(Task)
                .where(Task.status == status)
                .order_by(Task.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            tasks = result.scalars().all()
            return Ok(tasks)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find tasks by status {status}",
                    operation="find_by_status",
                    details=str(e),
                )
            )

    async def find_by_priority(
        self,
        priority: Priority,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Task], DatabaseError]:
        """Find tasks by priority.

        Args:
            priority: Priority level to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of tasks or error
        """
        try:
            stmt = (
                select(Task)
                .where(Task.priority == priority)
                .order_by(Task.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            tasks = result.scalars().all()
            return Ok(tasks)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find tasks by priority {priority}",
                    operation="find_by_priority",
                    details=str(e),
                )
            )

    async def find_by_owner(
        self,
        owner: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Task], DatabaseError]:
        """Find tasks by owner.

        Args:
            owner: Owner username to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of tasks or error
        """
        try:
            stmt = (
                select(Task)
                .where(Task.owner == owner)
                .order_by(Task.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            tasks = result.scalars().all()
            return Ok(tasks)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find tasks by owner {owner}",
                    operation="find_by_owner",
                    details=str(e),
                )
            )

    async def find_by_project(
        self,
        project_id: str,
        status: TaskStatus | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Task], DatabaseError]:
        """Find tasks by project with optional status filter.

        Args:
            project_id: Project ID to filter by
            status: Optional status filter
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of tasks or error
        """
        try:
            stmt = select(Task).where(Task.primary_project == project_id)

            if status is not None:
                stmt = stmt.where(Task.status == status)

            stmt = stmt.order_by(Task.created_at.desc()).limit(limit).offset(offset)

            result = await self.session.execute(stmt)
            tasks = result.scalars().all()
            return Ok(tasks)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find tasks by project {project_id}",
                    operation="find_by_project",
                    details=str(e),
                )
            )

    async def find_by_sprint(
        self,
        sprint_id: str,
        status: TaskStatus | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Task], DatabaseError]:
        """Find tasks by sprint with optional status filter.

        Args:
            sprint_id: Sprint ID to filter by
            status: Optional status filter
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of tasks or error
        """
        try:
            stmt = select(Task).where(Task.primary_sprint == sprint_id)

            if status is not None:
                stmt = stmt.where(Task.status == status)

            stmt = stmt.order_by(Task.created_at.desc()).limit(limit).offset(offset)

            result = await self.session.execute(stmt)
            tasks = result.scalars().all()
            return Ok(tasks)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find tasks by sprint {sprint_id}",
                    operation="find_by_sprint",
                    details=str(e),
                )
            )

    async def find_by_status_and_priority(
        self,
        status: TaskStatus,
        priority: Priority,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Task], DatabaseError]:
        """Find tasks by status and priority (uses composite index).

        Args:
            status: Task status to filter by
            priority: Priority level to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of tasks or error
        """
        try:
            stmt = (
                select(Task)
                .where(Task.status == status, Task.priority == priority)
                .order_by(Task.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            tasks = result.scalars().all()
            return Ok(tasks)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find tasks by status {status} and priority {priority}",
                    operation="find_by_status_and_priority",
                    details=str(e),
                )
            )

    async def find_blocked_tasks(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Task], DatabaseError]:
        """Find all blocked tasks.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of blocked tasks or error
        """
        return await self.find_by_status(TaskStatus.BLOCKED, limit, offset)

    async def find_high_priority_tasks(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Task], DatabaseError]:
        """Find all P0 and P1 (critical and high priority) tasks.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of high priority tasks or error
        """
        try:
            stmt = (
                select(Task)
                .where(Task.priority.in_([Priority.P0, Priority.P1]))
                .order_by(Task.priority, Task.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            tasks = result.scalars().all()
            return Ok(tasks)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message="Failed to find high priority tasks",
                    operation="find_high_priority_tasks",
                    details=str(e),
                )
            )

    # =========================================================================
    # Phase Query Methods
    # =========================================================================

    async def find_by_phase_status(
        self,
        phase_name: str,
        phase_status: PhaseStatus,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Task], DatabaseError]:
        """Find tasks by phase status using JSONB query.

        Args:
            phase_name: Phase name (research, planning, implementation, testing)
            phase_status: Status to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of tasks or error

        Example:
            # Find tasks in planning phase that are blocked
            tasks = await repo.find_by_phase_status("planning", PhaseStatus.BLOCKED)
        """
        if phase_name not in TASK_PHASES:
            return Err(
                DatabaseError(
                    message=f"Invalid phase name '{phase_name}'. Valid phases: {TASK_PHASES}",
                    operation="find_by_phase_status",
                )
            )

        try:
            # JSONB query: phases->'phase_name'->>'status' = 'status_value'
            stmt = (
                select(Task)
                .where(Task.phases[phase_name]["status"].astext == phase_status.value)
                .order_by(Task.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            tasks = result.scalars().all()
            return Ok(tasks)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find tasks by phase {phase_name} status {phase_status}",
                    operation="find_by_phase_status",
                    details=str(e),
                )
            )

    async def find_with_blocked_phase(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Task], DatabaseError]:
        """Find tasks that have any phase blocked.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of tasks with blocked phases or error

        Example:
            # Find all tasks with blocked phases
            blocked_tasks = await repo.find_with_blocked_phase()
        """
        try:
            # Check all phases for blocked status using OR
            from sqlalchemy import or_

            blocked_conditions = [
                Task.phases[phase]["status"].astext == PhaseStatus.BLOCKED.value
                for phase in TASK_PHASES
            ]

            stmt = (
                select(Task)
                .where(or_(*blocked_conditions))
                .order_by(Task.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            tasks = result.scalars().all()
            return Ok(tasks)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message="Failed to find tasks with blocked phases",
                    operation="find_with_blocked_phase",
                    details=str(e),
                )
            )

    async def find_by_current_phase(
        self,
        phase_name: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Task], DatabaseError]:
        """Find tasks where the specified phase is in_progress (current phase).

        Args:
            phase_name: Phase name to check as current
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of tasks in the specified phase or error

        Example:
            # Find tasks currently in implementation phase
            tasks = await repo.find_by_current_phase("implementation")
        """
        return await self.find_by_phase_status(
            phase_name, PhaseStatus.IN_PROGRESS, limit, offset
        )

    async def find_with_completed_phases(
        self,
        min_completed: int = 1,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Task], DatabaseError]:
        """Find tasks with at least N completed phases.

        Args:
            min_completed: Minimum number of completed phases
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of tasks or error

        Note:
            This is a simpler filter - for complex phase analytics,
            use PhaseService.get_phase_summary() instead.
        """
        try:
            # Fetch all tasks and filter in Python
            # (JSONB array counting is complex in SQL)
            stmt = (
                select(Task)
                .order_by(Task.created_at.desc())
                .limit(limit * 2)  # Fetch extra to account for filtering
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            all_tasks = result.scalars().all()

            # Filter tasks with enough completed phases
            filtered_tasks = []
            for task in all_tasks:
                completed_count = sum(
                    1 for phase in TASK_PHASES
                    if task.phases.get(phase, {}).get("status") in ("completed", "skipped")
                )
                if completed_count >= min_completed:
                    filtered_tasks.append(task)
                    if len(filtered_tasks) >= limit:
                        break

            return Ok(filtered_tasks)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find tasks with {min_completed}+ completed phases",
                    operation="find_with_completed_phases",
                    details=str(e),
                )
            )
