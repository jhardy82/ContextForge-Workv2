"""
Sprint Domain Entity

Domain entity that wraps the Sprint model with business logic and validation rules.
Follows domain-driven design principles to encapsulate sprint-specific behavior.
"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from cf_core.models.sprint import Sprint

if TYPE_CHECKING:
    from cf_core.models.observability import Observability


class SprintEntity:
    """
    Domain entity for Sprint with business logic and state management.

    Wraps the Sprint Pydantic model to provide domain-specific behavior,
    validation rules, and state transition logic.
    """

    def __init__(self, sprint: Sprint):
        """
        Initialize SprintEntity from a Sprint model.

        Args:
            sprint: Sprint Pydantic model instance
        """
        self._sprint = sprint

    @classmethod
    def create(
        cls,
        sprint_id: str,
        name: str,
        start_date: datetime,
        end_date: datetime | None = None,
        status: str = "new",
        description: str = "",
        goal: str | None = None,
        project_id: str | None = None,
        completed_at: datetime | None = None,
        # Phase 2 Fields
        owner: str | None = None,
        cadence: str | None = None,
        observability: "Observability | None" = None,
        task_ids: list[str] | None = None,
    ) -> "SprintEntity":
        """
        Factory method to create a new SprintEntity.

        Args:
            sprint_id: Unique identifier for the sprint
            name: Sprint name
            start_date: Sprint start date (required)
            end_date: Sprint end date (optional)
            status: Initial status (default: "new")
            description: Sprint description/goal
            goal: Sprint goal (alias for description, MCP compatibility)
            project_id: Associated project ID
            completed_at: Completion timestamp (required when status="completed")
            owner: Sprint owner (Phase 2)
            cadence: Sprint cadence - weekly, biweekly, monthly (Phase 2)
            observability: Observability tracking data (Phase 2)
            task_ids: List of task IDs associated with sprint (Phase 2)

        Returns:
            SprintEntity: New sprint entity instance
        """
        # Use goal if provided, otherwise use description
        final_description = goal if goal is not None else description

        sprint = Sprint(
            id=sprint_id,
            name=name,
            status=status,
            start_date=start_date,
            end_date=end_date,
            description=final_description,
            project_id=project_id,
            completed_at=completed_at,
            owner=owner,
            cadence=cadence,
            goal=goal,
            task_ids=task_ids or [],
        )
        # Set observability after creation if provided
        if observability is not None:
            sprint.observability = observability
        return cls(sprint)

    @property
    def model(self) -> Sprint:
        """Get the underlying Sprint model."""
        return self._sprint

    @property
    def id(self) -> str:
        """Get sprint ID."""
        return self._sprint.id

    @property
    def name(self) -> str:
        """Get sprint name."""
        return self._sprint.name

    @name.setter
    def name(self, value: str) -> None:
        """Set sprint name."""
        self._sprint.name = value

    @property
    def title(self) -> str:
        """Get sprint title (alias for name, backward compatibility)."""
        return self.name

    @title.setter
    def title(self, value: str) -> None:
        """Set sprint title (alias for name, backward compatibility)."""
        self.name = value

    @property
    def status(self) -> str:
        """Get sprint status."""
        return self._sprint.status

    @property
    def start_date(self) -> datetime:
        """Get sprint start date."""
        return self._sprint.start_date

    @property
    def end_date(self) -> datetime:
        """Get sprint end date."""
        return self._sprint.end_date

    @property
    def description(self) -> str:
        """Get sprint description."""
        return self._sprint.description

    @property
    def goal(self) -> str:
        """Get sprint goal (alias for description, MCP compatibility)."""
        return self._sprint.description

    @goal.setter
    def goal(self, value: str) -> None:
        """Set sprint goal (alias for description, MCP compatibility)."""
        self._sprint.description = value

    @description.setter
    def description(self, value: str) -> None:
        """Set sprint description."""
        self._sprint.description = value

    # NOTE: goal property already defined above (lines 124-132) as alias for description
    # Removed duplicate definition that was here

    @property
    def project_id(self) -> str | None:
        """Get associated project ID."""
        return self._sprint.project_id

    @property
    def created_at(self) -> datetime:
        """Get sprint creation timestamp."""
        return self._sprint.created_at

    @property
    def updated_at(self) -> datetime:
        """Get sprint last update timestamp."""
        return self._sprint.updated_at

    @property
    def owner(self) -> str | None:
        """Get sprint owner."""
        return self._sprint.owner

    @owner.setter
    def owner(self, value: str | None) -> None:
        """Set sprint owner."""
        self._sprint.owner = value

    @property
    def tags(self) -> list[str]:
        """Get sprint tags."""
        return self._sprint.tags

    def can_transition_to(self, new_status: str) -> bool:
        """
        Check if sprint can transition to the specified status.

        Uses the unified status lifecycle aligned with Sprint model:
        - new → pending, assigned, active, cancelled
        - pending → active, cancelled
        - assigned → active, pending, cancelled
        - active → in_progress, blocked, completed, cancelled
        - in_progress → active, blocked, completed, cancelled
        - blocked → active, in_progress, cancelled
        - completed → (terminal state)
        - cancelled → (terminal state)

        Args:
            new_status: Target status to transition to

        Returns:
            bool: True if transition is valid, False otherwise
        """
        # Delegate to the model's can_transition_to method for consistency
        return self._sprint.can_transition_to(new_status)

    def update_status(self, new_status: str) -> None:
        """
        Update sprint status with validation.

        Args:
            new_status: New status to set

        Raises:
            ValueError: If transition is not valid
        """
        if not self.can_transition_to(new_status):
            raise ValueError(
                f"Invalid status transition from '{self._sprint.status}' to '{new_status}'"
            )

        self._sprint.status = new_status

    def update_dates(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> None:
        """
        Update sprint dates with validation.

        Args:
            start_date: New start date (None to keep current)
            end_date: New end date (None to keep current)

        Raises:
            ValueError: If end_date is before start_date
        """
        new_start = start_date if start_date is not None else self._sprint.start_date
        new_end = end_date if end_date is not None else self._sprint.end_date

        if new_start and new_end and new_end < new_start:
            raise ValueError("End date cannot be before start date")

        if start_date is not None:
            self._sprint.start_date = start_date
        if end_date is not None:
            self._sprint.end_date = end_date

    def is_active(self) -> bool:
        """Check if sprint is currently active."""
        return self._sprint.status == "active"

    def is_completed(self) -> bool:
        """Check if sprint is completed."""
        return self._sprint.status == "completed"

    def is_cancelled(self) -> bool:
        """Check if sprint is cancelled."""
        return self._sprint.status == "cancelled"

    def update(self, **kwargs) -> "SprintEntity":
        """
        Update multiple sprint fields at once.

        Accepts any valid Sprint model fields as keyword arguments.
        Automatically updates the updated_at timestamp.

        Args:
            **kwargs: Fields to update (name, title, goal, status, start_date, end_date, etc.)

        Returns:
            SprintEntity: Updated entity with new field values

        Example:
            updated = sprint.update(title="New Title", goal="New Goal", status="active")
        """
        if not kwargs:
            return self

        # Handle title as alias for name
        if "title" in kwargs and "name" not in kwargs:
            kwargs["name"] = kwargs.pop("title")
        elif "title" in kwargs:
            kwargs.pop("title")  # Remove duplicate if both provided

        # Always update the timestamp
        kwargs["updated_at"] = datetime.now(UTC)

        updated = self._sprint.model_copy(update=kwargs)
        return SprintEntity(updated)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"SprintEntity(id='{self.id}', title='{self.title}', status='{self.status}')"
