"""
ActionList Service logic.
"""

from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.errors import AppError, NotFoundError, ValidationError
from taskman_api.core.result import Err, Ok, Result
from taskman_api.models.action_list import ActionList
from taskman_api.repositories.action_list_repository import ActionListRepository
from taskman_api.schemas import (
    ActionListAddItemRequest,
    ActionListCreate,
    ActionListResponse,
    ActionListUpdate,
    ReorderItemsRequest,
)

from .base import BaseService

# Global counter for ID generation (mimicking legacy router behavior)
_action_list_counter = 0


def _generate_action_list_id() -> str:
    """Generate a new action list ID in AL-xxxx format."""
    global _action_list_counter
    _action_list_counter += 1
    return f"AL-{_action_list_counter:04d}"


class ActionListService(
    BaseService[ActionList, ActionListCreate, ActionListUpdate, ActionListResponse]
):
    """ActionList business logic."""

    def __init__(self, session: AsyncSession) -> None:
        repository = ActionListRepository(session)
        super().__init__(repository, ActionList, ActionListResponse)
        self.action_list_repo = repository

    async def search(
        self,
        status: str | None = None,
        is_active: bool | None = None,
        priority: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[tuple[list[ActionListResponse], int], AppError]:
        """Search action lists."""
        try:
            items, total = await self.action_list_repo.search(
                status=status,
                is_active=is_active,
                priority=priority,
                limit=limit,
                offset=offset,
            )

            responses = [
                self.response_class.model_validate(item, from_attributes=True) for item in items
            ]
            return Ok((responses, total))
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def list_action_lists(
        self,
        status: str | None = None,
        owner: str | None = None,
        project_id: str | None = None,
        sprint_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[tuple[list[ActionListResponse], int], AppError]:
        """List and filter action lists (Router compatibility method)."""
        try:
            # Note: repository search handles the heavy lifting
            items, total = await self.action_list_repo.search(
                status=status,
                owner=owner,
                project_id=project_id,
                sprint_id=sprint_id,
                limit=limit,
                offset=offset,
            )

            responses = [
                self.response_class.model_validate(item, from_attributes=True) for item in items
            ]
            return Ok((responses, total))
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def update(
        self, id: str, update_data: ActionListUpdate
    ) -> Result[ActionListResponse, AppError]:
        """Update action list with field mapping."""
        try:
            # Map title -> name
            data = update_data.model_dump(exclude_unset=True)
            if "title" in data:
                data["name"] = data.pop("title")

            # Create new update model with mapped fields if needed,
            # but since BaseService uses model_dump, we can't easily inject dict if types mismatch.
            # So better to just do manual update here similar to BaseService but with mapped dict.

            entity = await self.repository.get_by_id(id)
            if not entity:
                return Err(NotFoundError(f"ActionList {id} not found"))

            for key, value in data.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)

            updated = await self.repository.update(entity)
            return Ok(self.response_class.model_validate(updated, from_attributes=True))
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def create(self, create_data: ActionListCreate) -> Result[ActionListResponse, AppError]:
        """Create a new action list with AL-xxxx ID."""
        try:
            # Generate ID
            new_id = _generate_action_list_id()

            # Prepare data
            data = create_data.model_dump(mode="json")

            # Extract only supported fields
            name = data.get("title") or data.get("name")
            task_ids = data.get("items", [])
            description = data.get("description")
            status = data.get("status", "active")

            # Create entity directly
            entity = self.model_class(
                id=new_id, name=name, description=description, status=status, task_ids=task_ids
            )

            # Save
            created = await self.repository.create(entity)
            return Ok(self.response_class.model_validate(created, from_attributes=True))
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def create_action_list(
        self,
        name: str,
        description: str = "",
        owner: str = "system",
        project_id: str | None = None,
        sprint_id: str | None = None,
        tags: list[str] | None = None,
        priority: str | None = None,
        due_date: datetime | None = None,
        items: list[str | dict] | None = None,
    ) -> Result[ActionListResponse, AppError]:
        """Create a new action list (Router compatibility method)."""
        try:
            new_id = _generate_action_list_id()
            entity = ActionList(
                id=new_id,
                name=name,
                description=description,
                owner=owner,
                project_id=project_id,
                sprint_id=sprint_id,
                tags=tags or [],
                priority=priority,
                due_date=due_date,
                task_ids=items or [],
                status="active",
            )
            created = await self.repository.create(entity)
            return Ok(self.response_class.model_validate(created, from_attributes=True))
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def get_action_list(self, id: str) -> Result[ActionListResponse, AppError]:
        """Get action list by ID (Router compatibility method)."""
        return await self.get(id)

    async def delete_action_list(self, id: str) -> Result[bool, AppError]:
        """Delete action list by ID (Router compatibility method)."""
        return await self.delete(id)

    async def update_action_list(
        self, id: str, **updates: Any
    ) -> Result[ActionListResponse, AppError]:
        """Update action list (Router compatibility method)."""
        # Map fields if necessary and call internal service logic
        try:
            entity = await self.repository.get_by_id(id)
            if not entity:
                return Err(NotFoundError(f"ActionList {id} not found"))

            # Map 'title' to 'name' if present in updates
            if "title" in updates:
                updates["name"] = updates.pop("title")

            for key, value in updates.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)

            updated = await self.repository.update(entity)
            return Ok(self.response_class.model_validate(updated, from_attributes=True))
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def add_item(
        self, list_id: str, item_request: ActionListAddItemRequest
    ) -> Result[ActionListResponse, AppError]:
        """Add a manual text item to the list."""
        try:
            # BaseService.get returns a Response model, not the entity.
            # So we rely on repo.get_by_id to get the entity for updates
            entity = await self.repository.get_by_id(list_id)
            if not entity:
                return Err(NotFoundError(f"Action list {list_id} not found"))

            # Create item structure matching schema
            from uuid import uuid4

            item = {
                "id": f"Item-{uuid4().hex[:8]}",
                "text": item_request.text,
                "completed": False,
                "order": item_request.order or 0,
            }
            updated = await self.action_list_repo.add_task(entity, item)
            return Ok(self.response_class.model_validate(updated, from_attributes=True))
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def add_task_by_id(
        self, list_id: str, task_id: str
    ) -> Result[ActionListResponse, AppError]:
        """Add an actual task ID to the list."""
        try:
            entity = await self.repository.get_by_id(list_id)
            if not entity:
                return Err(NotFoundError(f"Action list {list_id} not found"))

            updated = await self.action_list_repo.add_task(entity, task_id)
            return Ok(self.response_class.model_validate(updated, from_attributes=True))
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def remove_item(self, list_id: str, item_id: str) -> Result[ActionListResponse, AppError]:
        """Remove an item (task ID or text) from the list."""
        try:
            entity = await self.repository.get_by_id(list_id)
            if not entity:
                return Err(NotFoundError(f"Action list {list_id} not found"))

            # Find item to remove (match ID or text)
            item_to_remove = None
            for item in entity.task_ids:
                if isinstance(item, dict):
                    if item.get("id") == item_id or item.get("text") == item_id:
                        item_to_remove = item
                        break
                elif item == item_id:
                    item_to_remove = item
                    break

            if item_to_remove is None:
                return Err(NotFoundError(f"Item {item_id} not found in list {list_id}"))

            updated = await self.action_list_repo.remove_task(entity, item_to_remove)
            return Ok(self.response_class.model_validate(updated, from_attributes=True))
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def reorder_items(
        self, list_id: str, reorder_request: ReorderItemsRequest
    ) -> Result[ActionListResponse, AppError]:
        """Reorder items in the list."""
        try:
            entity = await self.repository.get_by_id(list_id)
            if not entity:
                return Err(NotFoundError(f"Action list {list_id} not found"))

            current_ids = set(entity.task_ids)
            requested_ids = set(reorder_request.item_ids)

            if current_ids != requested_ids:
                missing = current_ids - requested_ids
                extra = requested_ids - current_ids
                detail_parts = []
                if missing:
                    detail_parts.append(f"missing: {list(missing)}")
                if extra:
                    detail_parts.append(f"unknown: {list(extra)}")
                return Err(ValidationError(f"Item mismatch - {', '.join(detail_parts)}"))

            entity.task_ids = reorder_request.item_ids
            updated = await self.repository.update(entity)
            return Ok(self.response_class.model_validate(updated, from_attributes=True))
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def get_tasks_for_action_list(self, list_id: str) -> Result[list[str], AppError]:
        """Get all task IDs for a list."""
        try:
            entity = await self.repository.get_by_id(list_id)
            if not entity:
                return Err(NotFoundError(f"Action list {list_id} not found"))
            return Ok(entity.task_ids)
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def add_task_to_action_list(
        self, list_id: str, task_id: str
    ) -> Result[ActionListResponse, AppError]:
        """Alias for add_task_by_id for router compatibility."""
        return await self.add_task_by_id(list_id, task_id)

    async def remove_task_from_action_list(
        self, list_id: str, task_id: str
    ) -> Result[ActionListResponse, AppError]:
        """Remove a task from the list (Router compatibility method)."""
        return await self.remove_item(list_id, task_id)
