"""Plan repository with plan-specific queries.

Provides specialized queries for plan management and tracking.
"""

from collections.abc import Sequence
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.errors import DatabaseError
from taskman_api.core.result import Err, Ok, Result
from taskman_api.models.plan import Plan

from .base import BaseRepository

# Valid plan statuses
PLAN_STATUSES = ["draft", "approved", "in_progress", "completed", "abandoned"]


class PlanRepository(BaseRepository[Plan]):
    """Repository for Plan entity with specialized queries.

    Example:
        ```python
        async with get_db() as session:
            repo = PlanRepository(session)
            plans = await repo.find_by_status("in_progress")
        ```
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize plan repository.

        Args:
            session: Async database session
        """
        super().__init__(Plan, session)

    async def find_by_status(
        self,
        status: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Plan], DatabaseError]:
        """Find plans by status.

        Args:
            status: Plan status (draft, approved, in_progress, completed, abandoned)
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of plans or error
        """
        try:
            stmt = (
                select(Plan)
                .where(Plan.status == status)
                .order_by(Plan.updated_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            plans = result.scalars().all()
            return Ok(plans)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find plans by status {status}",
                    operation="find_by_status",
                    details=str(e),
                )
            )

    async def find_drafts(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Plan], DatabaseError]:
        """Find all draft plans awaiting approval.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of draft plans or error
        """
        return await self.find_by_status("draft", limit, offset)

    async def find_in_progress(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Plan], DatabaseError]:
        """Find all plans currently in progress.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of in-progress plans or error
        """
        return await self.find_by_status("in_progress", limit, offset)

    async def find_by_conversation(
        self,
        conversation_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Plan], DatabaseError]:
        """Find plans by originating conversation.

        Args:
            conversation_id: Conversation ID to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of plans or error
        """
        try:
            stmt = (
                select(Plan)
                .where(Plan.conversation_id == conversation_id)
                .order_by(Plan.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            plans = result.scalars().all()
            return Ok(plans)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find plans for conversation {conversation_id}",
                    operation="find_by_conversation",
                    details=str(e),
                )
            )

    async def find_by_project(
        self,
        project_id: str,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Plan], DatabaseError]:
        """Find plans by project with optional status filter.

        Args:
            project_id: Project ID to filter by
            status: Optional status filter
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of plans or error
        """
        try:
            stmt = select(Plan).where(Plan.project_id == project_id)

            if status is not None:
                stmt = stmt.where(Plan.status == status)

            stmt = stmt.order_by(Plan.updated_at.desc()).limit(limit).offset(offset)

            result = await self.session.execute(stmt)
            plans = result.scalars().all()
            return Ok(plans)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find plans for project {project_id}",
                    operation="find_by_project",
                    details=str(e),
                )
            )

    async def find_by_sprint(
        self,
        sprint_id: str,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Plan], DatabaseError]:
        """Find plans by sprint with optional status filter.

        Args:
            sprint_id: Sprint ID to filter by
            status: Optional status filter
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of plans or error
        """
        try:
            stmt = select(Plan).where(Plan.sprint_id == sprint_id)

            if status is not None:
                stmt = stmt.where(Plan.status == status)

            stmt = stmt.order_by(Plan.updated_at.desc()).limit(limit).offset(offset)

            result = await self.session.execute(stmt)
            plans = result.scalars().all()
            return Ok(plans)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find plans for sprint {sprint_id}",
                    operation="find_by_sprint",
                    details=str(e),
                )
            )

    async def find_recently_approved(
        self,
        days: int = 7,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Plan], DatabaseError]:
        """Find plans approved in the last N days.

        Args:
            days: Number of days to look back
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of recently approved plans or error
        """
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)

            stmt = (
                select(Plan)
                .where(Plan.approved_at >= cutoff, Plan.approved_at.isnot(None))
                .order_by(Plan.approved_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            plans = result.scalars().all()
            return Ok(plans)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find plans approved in last {days} days",
                    operation="find_recently_approved",
                    details=str(e),
                )
            )

    async def find_with_pending_steps(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Plan], DatabaseError]:
        """Find plans that have pending steps (not fully completed).

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of plans with pending steps or error
        """
        try:
            # Find plans that are approved or in_progress (have actionable steps)
            stmt = (
                select(Plan)
                .where(Plan.status.in_(["approved", "in_progress"]))
                .order_by(Plan.updated_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            plans = result.scalars().all()

            # Filter to only those with pending steps
            plans_with_pending = [
                p
                for p in plans
                if any(
                    s.get("status") in ("pending", "in_progress") for s in (p.steps or [])
                )
            ]
            return Ok(plans_with_pending)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message="Failed to find plans with pending steps",
                    operation="find_with_pending_steps",
                    details=str(e),
                )
            )

    async def find_stalled(
        self,
        days_inactive: int = 3,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Plan], DatabaseError]:
        """Find in-progress plans that haven't been updated recently.

        Args:
            days_inactive: Days without update to consider stalled
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of stalled plans or error
        """
        try:
            cutoff = datetime.utcnow() - timedelta(days=days_inactive)

            stmt = (
                select(Plan)
                .where(Plan.status == "in_progress", Plan.updated_at < cutoff)
                .order_by(Plan.updated_at.asc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            plans = result.scalars().all()
            return Ok(plans)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find stalled plans (>{days_inactive} days)",
                    operation="find_stalled",
                    details=str(e),
                )
            )

    async def count_by_status(self) -> Result[dict[str, int], DatabaseError]:
        """Get count of plans grouped by status.

        Returns:
            Result with dict of status -> count or error
        """
        try:
            stmt = select(
                Plan.status,
                func.count(Plan.id).label("count"),
            ).group_by(Plan.status)

            result = await self.session.execute(stmt)
            rows = result.all()
            counts = {row.status: row.count for row in rows}
            return Ok(counts)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message="Failed to count plans by status",
                    operation="count_by_status",
                    details=str(e),
                )
            )

    async def get_completion_stats(
        self,
        days: int = 30,
    ) -> Result[dict, DatabaseError]:
        """Get plan completion statistics for the last N days.

        Args:
            days: Number of days to analyze

        Returns:
            Result with completion stats or error
        """
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)

            # Count completed plans
            completed_stmt = select(func.count(Plan.id)).where(
                Plan.completed_at >= cutoff,
                Plan.completed_at.isnot(None),
            )
            completed_result = await self.session.execute(completed_stmt)
            completed_count = completed_result.scalar() or 0

            # Count abandoned plans
            abandoned_stmt = select(func.count(Plan.id)).where(
                Plan.status == "abandoned",
                Plan.updated_at >= cutoff,
            )
            abandoned_result = await self.session.execute(abandoned_stmt)
            abandoned_count = abandoned_result.scalar() or 0

            # Count created plans
            created_stmt = select(func.count(Plan.id)).where(Plan.created_at >= cutoff)
            created_result = await self.session.execute(created_stmt)
            created_count = created_result.scalar() or 0

            stats = {
                "period_days": days,
                "created": created_count,
                "completed": completed_count,
                "abandoned": abandoned_count,
                "completion_rate": (
                    (completed_count / created_count * 100) if created_count > 0 else 0
                ),
            }
            return Ok(stats)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to get completion stats for {days} days",
                    operation="get_completion_stats",
                    details=str(e),
                )
            )
