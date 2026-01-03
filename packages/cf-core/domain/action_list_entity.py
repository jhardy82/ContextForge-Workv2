"""
ActionList Domain Entity

Domain entity that wraps the ActionList model with business logic and validation rules.
Follows domain-driven design principles to encapsulate action list-specific behavior.
"""

from datetime import UTC, datetime

from cf_core.models.action_list import ActionList, ActionListStatus


class ActionListEntity:
    """
    Domain entity for ActionList with business logic and state management.

    Wraps the ActionList Pydantic model to provide domain-specific behavior,
    validation rules, and state transition logic.
    """

    def __init__(self, action_list: ActionList):
        """
        Initialize ActionListEntity from an ActionList model.

        Args:
            action_list: ActionList Pydantic model instance
        """
        self._action_list = action_list

    @classmethod
    def create(
        cls,
        list_id: str,
        name: str,
        status: ActionListStatus = "active",
        description: str | None = None,
        task_ids: list[str] | None = None,
        created_by: str = "system",
        tags: list[str] | None = None,
    ) -> "ActionListEntity":
        """
        Factory method to create a new ActionListEntity.

        Args:
            list_id: Unique identifier for the action list
            name: Action list name
            status: Initial status
            description: Optional description
            task_ids: List of task IDs
            created_by: Creator identifier
            tags: Optional tags

        Returns:
            New ActionListEntity instance
        """
        now = datetime.now(UTC)
        action_list = ActionList(
            id=list_id,
            name=name,
            description=description or "",
            status=status,
            task_ids=task_ids or [],
            owner=created_by,
            created_at=now,
            updated_at=now,
            tags=tags or [],
        )
        return cls(action_list)

    # Property accessors (read-only)
    @property
    def id(self) -> str:
        """Get action list ID."""
        return self._action_list.id

    @property
    def name(self) -> str:
        """Get action list name."""
        return self._action_list.name

    @property
    def description(self) -> str:
        """Get action list description."""
        return self._action_list.description

    @property
    def status(self) -> ActionListStatus:
        """Get action list status."""
        return self._action_list.status

    @property
    def task_ids(self) -> list[str]:
        """Get task IDs (copy to prevent mutation)."""
        return list(self._action_list.task_ids)

    @property
    def created_by(self) -> str:
        """Get creator identifier."""
        return self._action_list.created_by

    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._action_list.created_at

    @property
    def updated_at(self) -> datetime:
        """Get last update timestamp."""
        return self._action_list.updated_at

    @property
    def tags(self) -> list[str]:
        """Get tags (copy to prevent mutation)."""
        return list(self._action_list.tags)

    # Model accessor
    @property
    def model(self) -> ActionList:
        """Get underlying Pydantic model."""
        return self._action_list

    # State transition methods (immutable - return new instances)
    def add_task(self, task_id: str) -> "ActionListEntity":
        """
        Add a task to the action list.

        Args:
            task_id: Task identifier to add

        Returns:
            New ActionListEntity with updated task list
        """
        if task_id in self._action_list.task_ids:
            # Already exists, return self
            return self

        new_task_ids = list(self._action_list.task_ids) + [task_id]
        updated = self._action_list.model_copy(
            update={
                "task_ids": new_task_ids,
                "updated_at": datetime.now(UTC),
            }
        )
        return ActionListEntity(updated)

    def remove_task(self, task_id: str) -> "ActionListEntity":
        """
        Remove a task from the action list.

        Args:
            task_id: Task identifier to remove

        Returns:
            New ActionListEntity with updated task list
        """
        if task_id not in self._action_list.task_ids:
            # Not in list, return self
            return self

        new_task_ids = [tid for tid in self._action_list.task_ids if tid != task_id]
        updated = self._action_list.model_copy(
            update={
                "task_ids": new_task_ids,
                "updated_at": datetime.now(UTC),
            }
        )
        return ActionListEntity(updated)

    def clear_tasks(self) -> "ActionListEntity":
        """
        Remove all tasks from the action list.

        Returns:
            New ActionListEntity with empty task list
        """
        updated = self._action_list.model_copy(
            update={
                "task_ids": [],
                "updated_at": datetime.now(UTC),
            }
        )
        return ActionListEntity(updated)

    def archive(self) -> "ActionListEntity":
        """
        Archive the action list.

        Returns:
            New ActionListEntity with archived status
        """
        updated = self._action_list.model_copy(
            update={
                "status": "archived",
                "updated_at": datetime.now(UTC),
            }
        )
        return ActionListEntity(updated)

    def complete(self) -> "ActionListEntity":
        """
        Mark the action list as completed.

        Returns:
            New ActionListEntity with completed status
        """
        updated = self._action_list.model_copy(
            update={
                "status": "completed",
                "updated_at": datetime.now(UTC),
            }
        )
        return ActionListEntity(updated)

    def activate(self) -> "ActionListEntity":
        """
        Reactivate the action list.

        Returns:
            New ActionListEntity with active status
        """
        updated = self._action_list.model_copy(
            update={
                "status": "active",
                "updated_at": datetime.now(UTC),
            }
        )
        return ActionListEntity(updated)

    def update_name(self, name: str) -> "ActionListEntity":
        """
        Update the action list name.

        Args:
            name: New name

        Returns:
            New ActionListEntity with updated name
        """
        updated = self._action_list.model_copy(
            update={
                "name": name,
                "updated_at": datetime.now(UTC),
            }
        )
        return ActionListEntity(updated)

    def update_description(self, description: str) -> "ActionListEntity":
        """
        Update the action list description.

        Args:
            description: New description

        Returns:
            New ActionListEntity with updated description
        """
        updated = self._action_list.model_copy(
            update={
                "description": description,
                "updated_at": datetime.now(UTC),
            }
        )
        return ActionListEntity(updated)

    def can_transition_to(self, new_status: ActionListStatus) -> bool:
        """
        Check if status transition is allowed.

        Args:
            new_status: Proposed new status

        Returns:
            True if transition is allowed
        """
        current = self._action_list.status

        # Define valid transitions
        valid_transitions = {
            "active": ["completed", "archived"],
            "completed": ["active", "archived"],
            "archived": ["active"],
        }

        allowed = valid_transitions.get(current, [])
        return new_status in allowed

    # Dunder methods
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"ActionListEntity(id={self.id!r}, name={self.name!r}, status={self.status!r}, task_count={len(self.task_ids)})"

    def __eq__(self, other: object) -> bool:
        """Equality based on ID."""
        if not isinstance(other, ActionListEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)
