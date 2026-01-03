"""Checklist repository with checklist-specific queries.

Provides specialized queries for checklist management and templates.
"""

from collections.abc import Sequence
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.errors import DatabaseError
from taskman_api.core.result import Err, Ok, Result
from taskman_api.models.checklist import Checklist

from .base import BaseRepository

# Valid checklist statuses
CHECKLIST_STATUSES = ["active", "completed", "archived"]


class ChecklistRepository(BaseRepository[Checklist]):
    """Repository for Checklist entity with specialized queries.

    Example:
        ```python
        async with get_db() as session:
            repo = ChecklistRepository(session)
            templates = await repo.find_templates()
        ```
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize checklist repository.

        Args:
            session: Async database session
        """
        super().__init__(Checklist, session)

    async def find_by_status(
        self,
        status: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Checklist], DatabaseError]:
        """Find checklists by status.

        Args:
            status: Checklist status (active, completed, archived)
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of checklists or error
        """
        try:
            stmt = (
                select(Checklist)
                .where(Checklist.status == status)
                .order_by(Checklist.updated_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            checklists = result.scalars().all()
            return Ok(checklists)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find checklists by status {status}",
                    operation="find_by_status",
                    details=str(e),
                )
            )

    async def find_active(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Checklist], DatabaseError]:
        """Find all active checklists.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of active checklists or error
        """
        return await self.find_by_status("active", limit, offset)

    async def find_templates(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Checklist], DatabaseError]:
        """Find all checklist templates.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of templates or error
        """
        try:
            stmt = (
                select(Checklist)
                .where(Checklist.is_template == True)  # noqa: E712
                .order_by(Checklist.title.asc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            checklists = result.scalars().all()
            return Ok(checklists)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message="Failed to find checklist templates",
                    operation="find_templates",
                    details=str(e),
                )
            )

    async def find_by_template(
        self,
        template_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Checklist], DatabaseError]:
        """Find checklists cloned from a specific template.

        Args:
            template_id: Source template ID
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of checklists cloned from template or error
        """
        try:
            stmt = (
                select(Checklist)
                .where(Checklist.template_id == template_id)
                .order_by(Checklist.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            checklists = result.scalars().all()
            return Ok(checklists)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find checklists from template {template_id}",
                    operation="find_by_template",
                    details=str(e),
                )
            )

    async def find_by_task(
        self,
        task_id: str,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Checklist], DatabaseError]:
        """Find checklists by associated task.

        Args:
            task_id: Task ID to filter by
            status: Optional status filter
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of checklists or error
        """
        try:
            stmt = select(Checklist).where(Checklist.task_id == task_id)

            if status is not None:
                stmt = stmt.where(Checklist.status == status)

            stmt = stmt.order_by(Checklist.created_at.desc()).limit(limit).offset(offset)

            result = await self.session.execute(stmt)
            checklists = result.scalars().all()
            return Ok(checklists)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find checklists for task {task_id}",
                    operation="find_by_task",
                    details=str(e),
                )
            )

    async def find_by_plan(
        self,
        plan_id: str,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Checklist], DatabaseError]:
        """Find checklists by associated plan.

        Args:
            plan_id: Plan ID to filter by
            status: Optional status filter
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of checklists or error
        """
        try:
            stmt = select(Checklist).where(Checklist.plan_id == plan_id)

            if status is not None:
                stmt = stmt.where(Checklist.status == status)

            stmt = stmt.order_by(Checklist.created_at.desc()).limit(limit).offset(offset)

            result = await self.session.execute(stmt)
            checklists = result.scalars().all()
            return Ok(checklists)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find checklists for plan {plan_id}",
                    operation="find_by_plan",
                    details=str(e),
                )
            )

    async def find_by_conversation(
        self,
        conversation_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Checklist], DatabaseError]:
        """Find checklists by associated conversation.

        Args:
            conversation_id: Conversation ID to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of checklists or error
        """
        try:
            stmt = (
                select(Checklist)
                .where(Checklist.conversation_id == conversation_id)
                .order_by(Checklist.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            checklists = result.scalars().all()
            return Ok(checklists)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find checklists for conversation {conversation_id}",
                    operation="find_by_conversation",
                    details=str(e),
                )
            )

    async def find_incomplete(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Checklist], DatabaseError]:
        """Find active checklists with unchecked items.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of incomplete checklists or error
        """
        try:
            # Get active non-template checklists
            stmt = (
                select(Checklist)
                .where(
                    Checklist.status == "active",
                    Checklist.is_template == False,  # noqa: E712
                )
                .order_by(Checklist.updated_at.desc())
                .limit(limit * 2)  # Fetch extra to account for filtering
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            checklists = result.scalars().all()

            # Filter to those with pending items
            incomplete = [
                c
                for c in checklists
                if any(
                    item.get("status") in ("pending", "blocked")
                    for item in (c.items or [])
                )
            ][:limit]
            return Ok(incomplete)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message="Failed to find incomplete checklists",
                    operation="find_incomplete",
                    details=str(e),
                )
            )

    async def find_recently_completed(
        self,
        days: int = 7,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Checklist], DatabaseError]:
        """Find checklists completed in the last N days.

        Args:
            days: Number of days to look back
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of recently completed checklists or error
        """
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)

            stmt = (
                select(Checklist)
                .where(
                    Checklist.completed_at >= cutoff,
                    Checklist.completed_at.isnot(None),
                )
                .order_by(Checklist.completed_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            checklists = result.scalars().all()
            return Ok(checklists)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find checklists completed in last {days} days",
                    operation="find_recently_completed",
                    details=str(e),
                )
            )

    async def find_with_blocked_items(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[Checklist], DatabaseError]:
        """Find checklists that have blocked items.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of checklists with blocked items or error
        """
        try:
            # Get active checklists
            stmt = (
                select(Checklist)
                .where(Checklist.status == "active")
                .order_by(Checklist.updated_at.desc())
                .limit(limit * 2)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            checklists = result.scalars().all()

            # Filter to those with blocked items
            with_blocked = [
                c
                for c in checklists
                if any(item.get("status") == "blocked" for item in (c.items or []))
            ][:limit]
            return Ok(with_blocked)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message="Failed to find checklists with blocked items",
                    operation="find_with_blocked_items",
                    details=str(e),
                )
            )

    async def count_by_status(self) -> Result[dict[str, int], DatabaseError]:
        """Get count of checklists grouped by status.

        Returns:
            Result with dict of status -> count or error
        """
        try:
            stmt = select(
                Checklist.status,
                func.count(Checklist.id).label("count"),
            ).group_by(Checklist.status)

            result = await self.session.execute(stmt)
            rows = result.all()
            counts = {row.status: row.count for row in rows}
            return Ok(counts)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message="Failed to count checklists by status",
                    operation="count_by_status",
                    details=str(e),
                )
            )

    async def count_templates(self) -> Result[int, DatabaseError]:
        """Get count of checklist templates.

        Returns:
            Result with template count or error
        """
        try:
            stmt = select(func.count(Checklist.id)).where(
                Checklist.is_template == True  # noqa: E712
            )
            result = await self.session.execute(stmt)
            count = result.scalar() or 0
            return Ok(count)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message="Failed to count checklist templates",
                    operation="count_templates",
                    details=str(e),
                )
            )

    async def get_template_usage_stats(self) -> Result[list[dict], DatabaseError]:
        """Get usage statistics for checklist templates.

        Returns:
            Result with list of template usage stats or error
        """
        try:
            # Get all templates
            templates_result = await self.find_templates(limit=1000)
            if isinstance(templates_result, Err):
                return templates_result

            templates = templates_result.value
            stats = []

            for template in templates:
                # Count checklists using this template
                count_stmt = select(func.count(Checklist.id)).where(
                    Checklist.template_id == template.id
                )
                count_result = await self.session.execute(count_stmt)
                usage_count = count_result.scalar() or 0

                stats.append(
                    {
                        "template_id": template.id,
                        "title": template.title,
                        "item_count": len(template.items or []),
                        "usage_count": usage_count,
                    }
                )

            # Sort by usage count descending
            stats.sort(key=lambda x: x["usage_count"], reverse=True)
            return Ok(stats)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message="Failed to get template usage stats",
                    operation="get_template_usage_stats",
                    details=str(e),
                )
            )
