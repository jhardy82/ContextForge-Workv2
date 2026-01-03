"""ActionList service for cf_core.

Provides business logic for action list operations using cf_core models.
Orchestrates repository layer with validation, filtering, and task association.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from cf_core.models.action_list import ActionList
from cf_core.shared.result import Result

if TYPE_CHECKING:
    from cf_core.repositories.action_list_repository import ActionListRepository


class ActionListService:
    """Service for ActionList business logic operations.

    Provides orchestration layer between API and repository:
    - CRUD operations with validation
    - Task association management
    - Status transitions
    - Filtering and pagination

    Attributes:
        repository: ActionList repository instance
    """

    def __init__(self, repository: ActionListRepository) -> None:
        """Initialize action list service.

        Args:
            repository: ActionListRepository instance for persistence
        """
        self.repository = repository

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
        items: list[dict] | None = None,
    ) -> Result[ActionList]:
        """Create a new action list.

        Args:
            name: Action list name (required)
            description: Optional description
            owner: Owner identifier
            project_id: Associated project ID
            sprint_id: Associated sprint ID
            tags: List of tags for categorization
            priority: Priority level
            due_date: Due date for completion
            items: Initial checklist items

        Returns:
            Result[ActionList]: Success with created entity or Failure with error
        """
        action_list = ActionList(
            id=self._generate_action_list_id(),
            name=name,
            description=description,
            owner=owner,
            project_id=project_id,
            sprint_id=sprint_id,
            tags=tags or [],
            priority=priority,
            due_date=due_date,
            items=items or [],
            status="active",
        )

        return await self.repository.create(action_list)

    async def get_action_list(self, list_id: str) -> Result[ActionList | None]:
        """Get an action list by ID.

        Args:
            list_id: Action list identifier

        Returns:
            Result[ActionList | None]: Success with entity if found, or Failure
        """
        return await self.repository.get_by_id(list_id)

    async def update_action_list(
        self,
        list_id: str,
        **updates,
    ) -> Result[ActionList]:
        """Update an action list.

        Args:
            list_id: Action list identifier
            **updates: Fields to update (name, description, status, etc.)

        Returns:
            Result[ActionList]: Success with updated entity or Failure
        """
        # Get existing action list
        get_result = await self.repository.get_by_id(list_id)
        if get_result.is_failure:
            return get_result  # type: ignore

        action_list = get_result.value
        if action_list is None:
            return Result.failure(f"ActionList not found: {list_id}")

        # Apply updates
        updated_data = action_list.model_dump()
        updated_data.update(updates)
        updated_data["updated_at"] = datetime.now(UTC)

        updated_list = ActionList(**updated_data)
        return await self.repository.update(updated_list)

    async def delete_action_list(self, list_id: str) -> Result[bool]:
        """Delete an action list.

        Args:
            list_id: Action list identifier

        Returns:
            Result[bool]: Success(True) if deleted, Failure otherwise
        """
        return await self.repository.delete(list_id)

    async def list_action_lists(
        self,
        status: str | None = None,
        owner: str | None = None,
        project_id: str | None = None,
        sprint_id: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Result[tuple[list[ActionList], int]]:
        """List action lists with optional filtering and pagination.

        Args:
            status: Filter by status
            owner: Filter by owner
            project_id: Filter by project
            sprint_id: Filter by sprint
            limit: Maximum results to return
            offset: Number of results to skip

        Returns:
            Result[tuple[list[ActionList], int]]: Success with (lists, total_count) or Failure
        """
        # Get all action lists from repository
        if project_id:
            all_lists_result = await self.repository.find_by_project_id(project_id)
        else:
            all_lists_result = await self.repository.list_all(limit=10000)

        if all_lists_result.is_failure:
            return all_lists_result  # type: ignore

        all_lists = all_lists_result.value

        # Apply filters
        filtered_lists = all_lists
        if status:
            filtered_lists = [al for al in filtered_lists if al.status == status]
        if owner:
            filtered_lists = [al for al in filtered_lists if al.owner == owner]
        if sprint_id:
            filtered_lists = [al for al in filtered_lists if al.sprint_id == sprint_id]

        # Get total count before pagination
        total_count = len(filtered_lists)

        # Apply pagination
        paginated_lists = filtered_lists[offset : offset + limit]

        return Result.success((paginated_lists, total_count))

    async def add_task_to_action_list(
        self,
        list_id: str,
        task_id: str,
    ) -> Result[ActionList]:
        """Add a task to an action list.

        Args:
            list_id: Action list identifier
            task_id: Task identifier to add

        Returns:
            Result[ActionList]: Success with updated entity or Failure
        """
        # Get existing action list
        get_result = await self.repository.get_by_id(list_id)
        if get_result.is_failure:
            return get_result  # type: ignore

        action_list = get_result.value
        if action_list is None:
            return Result.failure(f"ActionList not found: {list_id}")

        # Add task if not already present
        if task_id not in action_list.task_ids:
            updated_task_ids = action_list.task_ids + [task_id]
            return await self.update_action_list(
                list_id,
                task_ids=updated_task_ids,
            )

        # Task already present, return unchanged
        return Result.success(action_list)

    async def remove_task_from_action_list(
        self,
        list_id: str,
        task_id: str,
    ) -> Result[ActionList]:
        """Remove a task from an action list.

        Args:
            list_id: Action list identifier
            task_id: Task identifier to remove

        Returns:
            Result[ActionList]: Success with updated entity or Failure
        """
        # Get existing action list
        get_result = await self.repository.get_by_id(list_id)
        if get_result.is_failure:
            return get_result  # type: ignore

        action_list = get_result.value
        if action_list is None:
            return Result.failure(f"ActionList not found: {list_id}")

        # Remove task if present
        if task_id in action_list.task_ids:
            updated_task_ids = [tid for tid in action_list.task_ids if tid != task_id]
            return await self.update_action_list(
                list_id,
                task_ids=updated_task_ids,
            )

        # Task not present, return unchanged
        return Result.success(action_list)

    async def get_tasks_for_action_list(
        self,
        list_id: str,
    ) -> Result[list[str]]:
        """Get all task IDs associated with an action list.

        Args:
            list_id: Action list identifier

        Returns:
            Result[list[str]]: Success with task IDs or Failure
        """
        get_result = await self.repository.get_by_id(list_id)
        if get_result.is_failure:
            return get_result  # type: ignore

        action_list = get_result.value
        if action_list is None:
            return Result.failure(f"ActionList not found: {list_id}")

        return Result.success(action_list.task_ids)

    async def get_action_lists_for_task(
        self,
        task_id: str,
    ) -> Result[list[ActionList]]:
        """Get all action lists containing a specific task.

        Args:
            task_id: Task identifier

        Returns:
            Result[list[ActionList]]: Success with matching lists or Failure
        """
        return await self.repository.find_by_task_id(task_id)

    def _generate_action_list_id(self) -> str:
        """Generate a unique action list ID."""
        import uuid
        return f"AL-{uuid.uuid4().hex[:8].upper()}"


__all__ = ["ActionListService"]
