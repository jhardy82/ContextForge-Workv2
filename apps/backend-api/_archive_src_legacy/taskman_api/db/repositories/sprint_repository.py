"""Sprint repository with sprint-specific queries.

Provides specialized queries for sprint management and Agile workflows.
"""

from collections.abc import Sequence
from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.enums import PhaseStatus, SprintCadence, SprintStatus
from taskman_api.core.errors import DatabaseError
from taskman_api.core.result import Err, Ok, Result
from taskman_api.db.models.sprint import Sprint

from .base import BaseRepository

# Valid sprint phases (sprints organize work execution)
SPRINT_PHASES = ["planning", "implementation"]


class SprintRepository(BaseRepository[Sprint]):
    """Repository for Sprint entity with specialized queries.

    Example:
        ```python
        async with get_db() as session:
            repo = SprintRepository(session)
            sprints = await repo.find_active_sprints()
        ```
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize sprint repository.

        Args:
            session: Async database session
        """
        super().__init__(Sprint, session)

    async def find_by_status(
        self,
        status: SprintStatus,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Sprint], DatabaseError]:
        """Find sprints by status.

        Args:
            status: Sprint status to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of sprints or error
        """
        try:
            stmt = (
                select(Sprint)
                .where(Sprint.status == status)
                .order_by(Sprint.start_date.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            sprints = result.scalars().all()
            return Ok(sprints)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find sprints by status {status}",
                    operation="find_by_status",
                    details=str(e),
                )
            )

    async def find_by_project(
        self,
        project_id: str,
        status: SprintStatus | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Sprint], DatabaseError]:
        """Find sprints by project with optional status filter.

        Args:
            project_id: Project ID to filter by
            status: Optional status filter
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of sprints or error
        """
        try:
            stmt = select(Sprint).where(Sprint.primary_project == project_id)

            if status is not None:
                stmt = stmt.where(Sprint.status == status)

            stmt = stmt.order_by(Sprint.start_date.desc()).limit(limit).offset(offset)

            result = await self.session.execute(stmt)
            sprints = result.scalars().all()
            return Ok(sprints)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find sprints by project {project_id}",
                    operation="find_by_project",
                    details=str(e),
                )
            )

    async def find_active_sprints(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Sprint], DatabaseError]:
        """Find all active sprints.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of active sprints or error
        """
        return await self.find_by_status(SprintStatus.ACTIVE, limit, offset)

    async def find_by_date_range(
        self,
        start_after: date | None = None,
        start_before: date | None = None,
        end_after: date | None = None,
        end_before: date | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Sprint], DatabaseError]:
        """Find sprints by date range.

        Args:
            start_after: Filter for sprints starting after this date
            start_before: Filter for sprints starting before this date
            end_after: Filter for sprints ending after this date
            end_before: Filter for sprints ending before this date
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of sprints or error
        """
        try:
            stmt = select(Sprint)

            if start_after is not None:
                stmt = stmt.where(Sprint.start_date >= start_after)

            if start_before is not None:
                stmt = stmt.where(Sprint.start_date <= start_before)

            if end_after is not None:
                stmt = stmt.where(Sprint.end_date >= end_after)

            if end_before is not None:
                stmt = stmt.where(Sprint.end_date <= end_before)

            stmt = stmt.order_by(Sprint.start_date.desc()).limit(limit).offset(offset)

            result = await self.session.execute(stmt)
            sprints = result.scalars().all()
            return Ok(sprints)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message="Failed to find sprints by date range",
                    operation="find_by_date_range",
                    details=str(e),
                )
            )

    async def find_by_owner(
        self,
        owner: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Sprint], DatabaseError]:
        """Find sprints by owner (Scrum Master).

        Args:
            owner: Owner username to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of sprints or error
        """
        try:
            stmt = (
                select(Sprint)
                .where(Sprint.owner == owner)
                .order_by(Sprint.start_date.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            sprints = result.scalars().all()
            return Ok(sprints)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find sprints by owner {owner}",
                    operation="find_by_owner",
                    details=str(e),
                )
            )

    async def find_by_cadence(
        self,
        cadence: SprintCadence,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Sprint], DatabaseError]:
        """Find sprints by cadence type.

        Args:
            cadence: Sprint cadence to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of sprints or error
        """
        try:
            stmt = (
                select(Sprint)
                .where(Sprint.cadence == cadence)
                .order_by(Sprint.start_date.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            sprints = result.scalars().all()
            return Ok(sprints)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find sprints by cadence {cadence}",
                    operation="find_by_cadence",
                    details=str(e),
                )
            )

    async def find_current_sprints(
        self,
        current_date: date | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Sprint], DatabaseError]:
        """Find sprints active on a given date (defaults to today).

        Args:
            current_date: Date to check (defaults to today)
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of current sprints or error
        """
        try:
            if current_date is None:
                from datetime import date as date_module

                current_date = date_module.today()

            stmt = (
                select(Sprint)
                .where(
                    Sprint.start_date <= current_date,
                    Sprint.end_date >= current_date,
                    Sprint.status == SprintStatus.ACTIVE,
                )
                .order_by(Sprint.start_date.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            sprints = result.scalars().all()
            return Ok(sprints)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message="Failed to find current sprints",
                    operation="find_current_sprints",
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
    ) -> Result[Sequence[Sprint], DatabaseError]:
        """Find sprints by phase status using JSONB query.

        Args:
            phase_name: Phase name (planning, implementation)
            phase_status: Status to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of sprints or error

        Example:
            # Find sprints in planning phase that are in_progress
            sprints = await repo.find_by_phase_status("planning", PhaseStatus.IN_PROGRESS)
        """
        if phase_name not in SPRINT_PHASES:
            return Err(
                DatabaseError(
                    message=f"Invalid phase name '{phase_name}'. Valid phases: {SPRINT_PHASES}",
                    operation="find_by_phase_status",
                )
            )

        try:
            # JSONB query: phases->'phase_name'->>'status' = 'status_value'
            stmt = (
                select(Sprint)
                .where(Sprint.phases[phase_name]["status"].astext == phase_status.value)
                .order_by(Sprint.start_date.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            sprints = result.scalars().all()
            return Ok(sprints)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find sprints by phase {phase_name} status {phase_status}",
                    operation="find_by_phase_status",
                    details=str(e),
                )
            )

    async def find_with_blocked_phase(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Sprint], DatabaseError]:
        """Find sprints that have any phase blocked.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of sprints with blocked phases or error
        """
        try:
            from sqlalchemy import or_

            blocked_conditions = [
                Sprint.phases[phase]["status"].astext == PhaseStatus.BLOCKED.value
                for phase in SPRINT_PHASES
            ]

            stmt = (
                select(Sprint)
                .where(or_(*blocked_conditions))
                .order_by(Sprint.start_date.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            sprints = result.scalars().all()
            return Ok(sprints)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message="Failed to find sprints with blocked phases",
                    operation="find_with_blocked_phase",
                    details=str(e),
                )
            )

    async def find_by_current_phase(
        self,
        phase_name: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Sprint], DatabaseError]:
        """Find sprints where the specified phase is in_progress.

        Args:
            phase_name: Phase name to check as current
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of sprints in the specified phase or error
        """
        return await self.find_by_phase_status(
            phase_name, PhaseStatus.IN_PROGRESS, limit, offset
        )
