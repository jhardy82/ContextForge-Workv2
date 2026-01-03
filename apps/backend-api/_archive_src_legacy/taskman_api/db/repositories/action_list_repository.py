"""ActionList repository with action list-specific queries.

Provides specialized queries for lightweight task container management.
"""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.errors import DatabaseError
from taskman_api.core.result import Err, Ok, Result
from taskman_api.db.models.action_list import ActionList

from .base import BaseRepository


class ActionListRepository(BaseRepository[ActionList]):
    """Repository for ActionList entity with specialized queries.

    Example:
        ```python
        async with get_db() as session:
            repo = ActionListRepository(session)
            lists = await repo.find_by_owner("john.doe")
        ```
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize action list repository.

        Args:
            session: Async database session
        """
        super().__init__(ActionList, session)

    async def find_by_owner(
        self,
        owner: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[ActionList], DatabaseError]:
        """Find action lists by owner.

        Args:
            owner: Owner username to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of action lists or error
        """
        try:
            stmt = (
                select(ActionList)
                .where(ActionList.owner == owner)
                .order_by(ActionList.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            action_lists = result.scalars().all()
            return Ok(action_lists)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find action lists by owner {owner}",
                    operation="find_by_owner",
                    details=str(e),
                )
            )

    async def find_by_status(
        self,
        status: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[ActionList], DatabaseError]:
        """Find action lists by status.

        Args:
            status: Status to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of action lists or error
        """
        try:
            stmt = (
                select(ActionList)
                .where(ActionList.status == status)
                .order_by(ActionList.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            action_lists = result.scalars().all()
            return Ok(action_lists)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find action lists by status {status}",
                    operation="find_by_status",
                    details=str(e),
                )
            )

    async def find_by_project(
        self,
        project_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[ActionList], DatabaseError]:
        """Find action lists by project.

        Args:
            project_id: Project ID to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of action lists or error
        """
        try:
            stmt = (
                select(ActionList)
                .where(ActionList.project_id == project_id)
                .order_by(ActionList.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            action_lists = result.scalars().all()
            return Ok(action_lists)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find action lists by project {project_id}",
                    operation="find_by_project",
                    details=str(e),
                )
            )

    async def find_by_sprint(
        self,
        sprint_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[ActionList], DatabaseError]:
        """Find action lists by sprint.

        Args:
            sprint_id: Sprint ID to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of action lists or error
        """
        try:
            stmt = (
                select(ActionList)
                .where(ActionList.sprint_id == sprint_id)
                .order_by(ActionList.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            action_lists = result.scalars().all()
            return Ok(action_lists)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find action lists by sprint {sprint_id}",
                    operation="find_by_sprint",
                    details=str(e),
                )
            )

    async def find_orphaned(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[ActionList], DatabaseError]:
        """Find orphaned action lists (no project or sprint association).

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of orphaned action lists or error
        """
        try:
            stmt = (
                select(ActionList)
                .where(ActionList.project_id.is_(None), ActionList.sprint_id.is_(None))
                .order_by(ActionList.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            action_lists = result.scalars().all()
            return Ok(action_lists)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message="Failed to find orphaned action lists",
                    operation="find_orphaned",
                    details=str(e),
                )
            )

    async def find_soft_deleted(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[ActionList], DatabaseError]:
        """Find soft-deleted action lists (parent was deleted).

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of soft-deleted action lists or error
        """
        try:
            stmt = (
                select(ActionList)
                .where(ActionList.parent_deleted_at.isnot(None))
                .order_by(ActionList.parent_deleted_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            action_lists = result.scalars().all()
            return Ok(action_lists)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message="Failed to find soft-deleted action lists",
                    operation="find_soft_deleted",
                    details=str(e),
                )
            )

    async def find_by_tag(
        self,
        tag: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[ActionList], DatabaseError]:
        """Find action lists with specific tag.

        Args:
            tag: Tag to filter by (searches tags JSON array)
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of action lists or error
        """
        try:
            # Note: This uses PostgreSQL JSON containment operator @>
            stmt = (
                select(ActionList)
                .where(ActionList.tags.contains([tag]))
                .order_by(ActionList.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            action_lists = result.scalars().all()
            return Ok(action_lists)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find action lists by tag {tag}",
                    operation="find_by_tag",
                    details=str(e),
                )
            )
