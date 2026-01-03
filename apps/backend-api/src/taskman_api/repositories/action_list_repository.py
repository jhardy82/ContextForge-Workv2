"""
ActionList Repository.

Data access layer for ActionList entities.
Updated to match actual database schema.
"""

from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.models.action_list import ActionList
from taskman_api.repositories.base import BaseRepository


class ActionListRepository(BaseRepository[ActionList]):
    """Repository for ActionList entity operations."""

    model_class = ActionList

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def exists(self, entity_id: str) -> bool:
        """Check if action list exists by ID."""
        result = await self.session.execute(
            select(func.count())
            .select_from(ActionList)
            .where(ActionList.id == entity_id)
        )
        return (result.scalar() or 0) > 0

    async def get_active(self, limit: int = 100) -> list[ActionList]:
        """Get all active action lists."""
        result = await self.session.execute(
            select(ActionList).where(ActionList.status == "active").limit(limit)
        )
        return list(result.scalars().all())

    async def search(
        self,
        status: str | None = None,
        is_active: bool | None = None,
        priority: str | None = None,
        owner: str | None = None,
        project_id: str | None = None,
        sprint_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[ActionList], int]:
        """
        Search action lists with filters.

        Args:
            status: Filter by status (e.g., 'active', 'archived', 'completed')
            is_active: API compatibility - maps True to status='active'
            priority: Filter by priority level (e.g., 'high', 'medium', 'low')
            owner: Filter by owner
            project_id: Filter by project association
            sprint_id: Filter by sprint association
            limit: Max results to return
            offset: Number of results to skip

        Returns: (action_lists, total_count)
        """
        query = select(ActionList)

        # Filter by status (database field)
        if status is not None:
            query = query.where(ActionList.status == status)
        elif is_active is not None:
            # API compatibility: map is_active to status
            if is_active:
                query = query.where(ActionList.status == "active")
            else:
                query = query.where(ActionList.status != "active")

        # Filter by priority (now exists in DB as VARCHAR(20))
        if priority is not None:
            query = query.where(ActionList.priority == priority)

        # Filter by owner
        if owner is not None:
            query = query.where(ActionList.owner == owner)

        # Filter by project_id
        if project_id is not None:
            query = query.where(ActionList.project_id == project_id)

        # Filter by sprint_id
        if sprint_id is not None:
            query = query.where(ActionList.sprint_id == sprint_id)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)

        return list(result.scalars().all()), total

    async def create_action_list(
        self,
        name: str,
        description: str | None = None,
        priority: str | None = None,
        owner: str | None = None,
        project_id: str | None = None,
        sprint_id: str | None = None,
        task_ids: list[str] | None = None,
    ) -> ActionList:
        """Create a new action list with all optional fields."""
        action_list = ActionList(
            id=str(uuid4()),
            name=name,
            description=description,
            status="active",
            priority=priority,
            owner=owner,
            project_id=project_id,
            sprint_id=sprint_id,
            task_ids=task_ids or [],
        )
        return await self.create(action_list)

    async def add_task(self, action_list: ActionList, task_id: str) -> ActionList:
        """Add a task to the action list."""
        if task_id not in action_list.task_ids:
            action_list.task_ids = [*action_list.task_ids, task_id]
        return await self.update(action_list)

    async def remove_task(self, action_list: ActionList, task_id: str) -> ActionList:
        """Remove a task from the action list."""
        if task_id in action_list.task_ids:
            action_list.task_ids = [t for t in action_list.task_ids if t != task_id]
        return await self.update(action_list)

    async def archive(self, action_list: ActionList) -> ActionList:
        """Archive an action list."""
        action_list.status = "archived"
        return await self.update(action_list)
