"""ActionList service with item management.

Handles action list operations and item management.
"""

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.errors import AppError, NotFoundError, ValidationError
from taskman_api.core.result import Err, Ok, Result
from taskman_api.db.models.action_list import ActionList
from taskman_api.db.repositories.action_list_repository import ActionListRepository
from taskman_api.schemas.action_list import (
    ActionListCreateRequest,
    ActionListResponse,
    ActionListUpdateRequest,
)

from .base import BaseService


class ActionListService(
    BaseService[
        ActionList, ActionListCreateRequest, ActionListUpdateRequest, ActionListResponse
    ]
):
    """ActionList business logic and operations.

    Provides action list management functionality including:
    - CRUD operations (inherited from BaseService)
    - Item reordering
    - Completion tracking
    - Soft delete support

    Example:
        service = ActionListService(session)
        result = await service.mark_complete("AL-001")
        match result:
            case Ok(action_list):
                print(f"Completed at: {action_list.completed_at}")
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize ActionListService with session.

        Args:
            session: Async database session
        """
        repository = ActionListRepository(session)
        super().__init__(repository, ActionList, ActionListResponse)
        self.action_list_repo = repository

    async def reorder_items(
        self,
        list_id: str,
        item_order: list[int],
    ) -> Result[ActionListResponse, NotFoundError | ValidationError | AppError]:
        """Reorder items in action list.

        Args:
            list_id: Action list identifier
            item_order: New order of item indices (0-based)

        Returns:
            Result containing updated action list or error

        Example:
            # Reorder items: [0, 1, 2] → [2, 0, 1]
            result = await service.reorder_items("AL-001", [2, 0, 1])
            match result:
                case Ok(action_list):
                    print(f"Items reordered: {len(action_list.items)}")
        """
        # Get current action list
        get_result = await self.get(list_id)

        match get_result:
            case Err(error):
                return Err(error)
            case Ok(action_list):
                # Validate item_order length matches current items
                current_items = action_list.items
                if len(item_order) != len(current_items):
                    return Err(
                        ValidationError(
                            message=f"Item order length ({len(item_order)}) must match current items ({len(current_items)})",
                            field="item_order",
                            value=str(item_order),
                        )
                    )

                # Validate all indices are valid
                valid_indices = set(range(len(current_items)))
                provided_indices = set(item_order)
                if provided_indices != valid_indices:
                    return Err(
                        ValidationError(
                            message=f"Invalid item indices: {provided_indices - valid_indices}",
                            field="item_order",
                            value=str(item_order),
                        )
                    )

                # Reorder items
                reordered_items = [current_items[i] for i in item_order]

                # Update action list
                update_request = ActionListUpdateRequest(items=reordered_items)
                return await self.update(list_id, update_request)

    async def mark_complete(
        self,
        list_id: str,
    ) -> Result[ActionListResponse, NotFoundError | AppError]:
        """Mark action list as completed.

        Sets completed_at timestamp and updates status.

        Args:
            list_id: Action list identifier

        Returns:
            Result containing updated action list or error

        Example:
            result = await service.mark_complete("AL-001")
        """
        update_request = ActionListUpdateRequest(
            status="completed", completed_at=datetime.utcnow()
        )
        return await self.update(list_id, update_request)

    async def add_item(
        self,
        list_id: str,
        item: dict,
    ) -> Result[ActionListResponse, NotFoundError | AppError]:
        """Add item to action list.

        Args:
            list_id: Action list identifier
            item: Item dict to add (e.g., {"task": "Do something", "done": False})

        Returns:
            Result containing updated action list or error

        Example:
            new_item = {"task": "Review PR", "done": False}
            result = await service.add_item("AL-001", new_item)
        """
        # Get current action list
        get_result = await self.get(list_id)

        match get_result:
            case Err(error):
                return Err(error)
            case Ok(action_list):
                # Add item to items array
                updated_items = action_list.items + [item]

                # Update action list
                update_request = ActionListUpdateRequest(items=updated_items)
                return await self.update(list_id, update_request)

    async def remove_item(
        self,
        list_id: str,
        item_index: int,
    ) -> Result[ActionListResponse, NotFoundError | ValidationError | AppError]:
        """Remove item from action list by index.

        Args:
            list_id: Action list identifier
            item_index: Index of item to remove (0-based)

        Returns:
            Result containing updated action list or error

        Example:
            result = await service.remove_item("AL-001", 2)  # Remove 3rd item
        """
        # Get current action list
        get_result = await self.get(list_id)

        match get_result:
            case Err(error):
                return Err(error)
            case Ok(action_list):
                # Validate item index
                if item_index < 0 or item_index >= len(action_list.items):
                    return Err(
                        ValidationError(
                            message=f"Invalid item index: {item_index} (valid range: 0-{len(action_list.items)-1})",
                            field="item_index",
                            value=str(item_index),
                        )
                    )

                # Remove item
                updated_items = [
                    item
                    for i, item in enumerate(action_list.items)
                    if i != item_index
                ]

                # Update action list
                update_request = ActionListUpdateRequest(items=updated_items)
                return await self.update(list_id, update_request)

    async def get_by_project(
        self,
        project_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[ActionListResponse], AppError]:
        """Get action lists for project.

        Args:
            project_id: Project identifier
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing list of action lists or error

        Example:
            result = await service.get_by_project("P-TASKMAN")
        """
        result = await self.action_list_repo.find_by_project(
            project_id, limit, offset
        )

        match result:
            case Ok(action_lists):
                responses = [
                    self.response_class.model_validate(al) for al in action_lists
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def get_by_sprint(
        self,
        sprint_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[ActionListResponse], AppError]:
        """Get action lists for sprint.

        Args:
            sprint_id: Sprint identifier
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing list of action lists or error

        Example:
            result = await service.get_by_sprint("S-2025-01")
        """
        result = await self.action_list_repo.find_by_sprint(sprint_id, limit, offset)

        match result:
            case Ok(action_lists):
                responses = [
                    self.response_class.model_validate(al) for al in action_lists
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def get_orphaned(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[ActionListResponse], AppError]:
        """Get action lists not associated with any project or sprint.

        Args:
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing list of orphaned action lists or error

        Example:
            result = await service.get_orphaned()
            match result:
                case Ok(orphaned):
                    print(f"Found {len(orphaned)} orphaned action lists")
        """
        result = await self.action_list_repo.find_orphaned(limit, offset)

        match result:
            case Ok(action_lists):
                responses = [
                    self.response_class.model_validate(al) for al in action_lists
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def get_soft_deleted(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[ActionListResponse], AppError]:
        """Get soft-deleted action lists.

        Args:
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing list of soft-deleted action lists or error

        Example:
            result = await service.get_soft_deleted()
        """
        result = await self.action_list_repo.find_soft_deleted(limit, offset)

        match result:
            case Ok(action_lists):
                responses = [
                    self.response_class.model_validate(al) for al in action_lists
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)
