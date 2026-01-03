"""Sprint domain model for cf_core.

Provides a rich Pydantic v2 model for Sprint entities with:
- Status lifecycle (new, pending, active, in_progress, blocked, completed, cancelled)
- Status-based validations (pending_reason, blocked_reason, completed_at)
- Date range validation (end_date > start_date)
- Capacity and velocity tracking
- Task association
- Team member management
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator, model_validator

from cf_core.models.action_item import ActionItem
from cf_core.models.observability import Observability
from cf_core.models.phase_tracking import PhaseTracking
from cf_core.models.risk_entry import RiskEntrySimple
from cf_core.models.verification import Verification

# Sprint status aligned with Task/Project status enums for consistency
# Includes 'assigned' for alignment with Project model
SprintStatus = Literal[
    "new",
    "pending",
    "assigned",
    "active",
    "in_progress",
    "blocked",
    "completed",
    "cancelled",
]


class Sprint(BaseModel):
    """Domain model for Sprint entities.

    Attributes:
        id: Unique sprint identifier (S- prefix)
        name: Sprint name
        status: Current sprint status
        start_date: Sprint start date
        end_date: Sprint end date
        description: Optional sprint description
        project_id: Associated project ID
        completed_at: Completion timestamp
        capacity_hours: Planned capacity in hours
        velocity_points: Velocity in story points
        actual_hours: Actual hours spent
        actual_points: Actual story points completed
        task_ids: List of associated task IDs
        action_items: List of action items for this sprint
        tags: List of tags
        team_members: List of team member identifiers
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    id: str = Field(..., pattern=r"^S-[a-zA-Z0-9_-]+$")
    name: str = Field(..., min_length=1, max_length=200)
    status: SprintStatus = Field(default="new")
    start_date: datetime
    end_date: datetime
    description: str = Field(default="")
    project_id: str | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    capacity_hours: float | None = Field(default=None, ge=0)
    velocity_points: float | None = Field(default=None, ge=0)
    actual_hours: float = Field(default=0.0, ge=0)
    actual_points: int = Field(default=0, ge=0)

    # Task association (tasks is schema name, task_ids is internal)
    task_ids: list[str] = Field(
        default_factory=list, validation_alias=AliasChoices("tasks", "task_ids")
    )

    action_items: list[ActionItem] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    team_members: list[str] = Field(default_factory=list)

    # Phase 2 New Fields
    owner: str | None = Field(default=None)
    cadence: str | None = Field(default=None)  # weekly, biweekly, monthly
    goal: str | None = Field(default=None)  # Alias for description or specific goal

    # Status Reasons (aligned with Project model)
    pending_reason: str | None = Field(default=None)
    blocked_reason: str | None = Field(default=None)

    # Complex JSON Fields
    observability: Observability = Field(
        default_factory=lambda: Observability(
            last_health="green", last_heartbeat_utc=datetime.now(UTC)
        )
    )
    risks: list[RiskEntrySimple] = Field(default_factory=list)
    verification: Verification | None = Field(default=None)

    # Metrics
    committed_points: float | None = Field(default=None)
    completed_points: float | None = Field(default=None)
    velocity_trend: float | None = Field(default=None)

    # Phase Tracking (Research -> Planning -> Implementation -> Testing)
    phases: PhaseTracking = Field(
        default_factory=PhaseTracking,
        description="Lifecycle phase tracking (research, planning, implementation, testing)"
    )

    # =========================================================================
    # FIELD VALIDATORS
    # =========================================================================

    @field_validator("id", mode="before")
    @classmethod
    def validate_id_prefix(cls, v: str) -> str:
        """Validate that ID starts with S- prefix and has content after it."""
        if not v:
            raise ValueError("Sprint ID is required")
        if not v.startswith("S-"):
            raise ValueError("Sprint ID must start with 'S-' prefix")
        if len(v) <= 2:
            raise ValueError("Sprint ID must have at least one character after 'S-'")
        return v

    @field_validator("start_date", "end_date", "completed_at", mode="before")
    @classmethod
    def ensure_utc(cls, v: datetime | None) -> datetime | None:
        """Convert datetimes to UTC.

        - Naive datetimes are assumed to be UTC and get tzinfo added
        - Timezone-aware datetimes are converted to UTC
        """
        if v is None:
            return v
        if isinstance(v, datetime):
            if v.tzinfo is None:
                # Naive datetime - assume UTC
                return v.replace(tzinfo=UTC)
            elif v.tzinfo != UTC:
                # Convert from other timezone to UTC
                return v.astimezone(UTC)
        return v

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, v: list[str] | None) -> list[str]:
        """Strip whitespace, remove empty strings, and deduplicate tags."""
        if not v:
            return []
        # Strip whitespace, filter empty, deduplicate while preserving order
        seen: set[str] = set()
        result: list[str] = []
        for tag in v:
            stripped = tag.strip() if isinstance(tag, str) else tag
            if stripped and stripped not in seen:
                seen.add(stripped)
                result.append(stripped)
        return result

    @field_validator("task_ids", mode="before")
    @classmethod
    def validate_and_normalize_task_ids(cls, v: list[str] | None) -> list[str]:
        """Validate task ID prefixes and deduplicate."""
        if not v:
            return []
        # Validate prefixes and deduplicate while preserving order
        seen: set[str] = set()
        result: list[str] = []
        for task_id in v:
            if not task_id.startswith("T-"):
                raise ValueError(f"Task ID must start with 'T-' prefix: {task_id}")
            if task_id not in seen:
                seen.add(task_id)
                result.append(task_id)
        return result

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def tasks(self) -> list[str]:
        """Alias for task_ids to match schema."""
        return self.task_ids

    @property
    def primary_project(self) -> str | None:
        """Alias for project_id."""
        return self.project_id

    @model_validator(mode="after")
    def validate_date_range(self) -> Sprint:
        """Validate that end_date is after start_date."""
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self

    @model_validator(mode="after")
    def validate_completed_at(self) -> Sprint:
        """Validate completed_at aligns with status."""
        if self.status == "completed" and self.completed_at is None:
            raise ValueError("completed_at required when status is 'completed'")
        if self.status != "completed" and self.completed_at is not None:
            raise ValueError("completed_at only allowed when status is 'completed'")
        return self

    def is_completed(self) -> bool:
        """Check if sprint is completed."""
        return self.status == "completed"

    def is_active(self) -> bool:
        """Check if sprint is currently active."""
        return self.status == "active"

    def is_cancelled(self) -> bool:
        """Check if sprint was cancelled."""
        return self.status == "cancelled"

    def days_remaining(self) -> int:
        """Calculate days remaining in sprint."""
        if self.is_completed() or self.is_cancelled():
            return 0
        now = datetime.utcnow()
        if now >= self.end_date:
            return 0
        return (self.end_date - now).days

    def duration_days(self) -> float:
        """Calculate total sprint duration in days."""
        delta = self.end_date - self.start_date
        return delta.total_seconds() / 86400  # seconds per day

    def duration_hours(self) -> float:
        """Calculate total sprint duration in hours."""
        delta = self.end_date - self.start_date
        return delta.total_seconds() / 3600  # seconds per hour

    def capacity_utilization(self) -> float | None:
        """Calculate capacity utilization percentage.

        Returns:
            Percentage of capacity used (actual_hours / capacity_hours * 100),
            or None if capacity_hours is not set.
        """
        if self.capacity_hours is None or self.capacity_hours == 0:
            return None
        return (self.actual_hours / self.capacity_hours) * 100

    def velocity_completion(self) -> float | None:
        """Calculate velocity completion percentage.

        Returns:
            Percentage of velocity achieved (actual_points / velocity_points * 100),
            or None if velocity_points is not set.
        """
        if self.velocity_points is None or self.velocity_points == 0:
            return None
        return (self.actual_points / self.velocity_points) * 100

    def add_task(self, task_id: str) -> None:
        """Add a task ID to the sprint.

        Args:
            task_id: Task ID to add (must start with 'T-')

        Raises:
            ValueError: If task_id doesn't start with 'T-'
        """
        if not task_id.startswith("T-"):
            raise ValueError(f"Task ID must start with 'T-' prefix: {task_id}")
        if task_id not in self.task_ids:
            self.task_ids.append(task_id)

    def remove_task(self, task_id: str) -> bool:
        """Remove a task ID from the sprint."""
        if task_id in self.task_ids:
            self.task_ids.remove(task_id)
            return True
        return False

    def add_action_item(self, action_item: ActionItem) -> None:
        """Add an action item to the sprint."""
        if action_item not in self.action_items:
            self.action_items.append(action_item)

    def get_pending_actions(self) -> list[ActionItem]:
        """Get all pending action items."""
        return [a for a in self.action_items if a.is_pending()]

    def get_completed_actions(self) -> list[ActionItem]:
        """Get all completed action items."""
        return [a for a in self.action_items if a.is_completed()]

    def mark_completed(self) -> None:
        """Mark sprint as completed with timestamp.

        Sets status to 'closed', completed_at to now, and updates updated_at.
        Uses object.__setattr__ to bypass Pydantic validation during atomic update.
        """
        now = datetime.now(UTC)
        object.__setattr__(self, "status", "completed")
        object.__setattr__(self, 'completed_at', now)
        object.__setattr__(self, 'updated_at', now)

    def start(self) -> None:
        """Start the sprint by setting status to 'active'."""
        object.__setattr__(self, 'status', 'active')
        object.__setattr__(self, 'updated_at', datetime.now(UTC))

    def cancel(self) -> None:
        """Cancel the sprint by setting status to 'cancelled'."""
        object.__setattr__(self, "status", "cancelled")
        object.__setattr__(self, 'updated_at', datetime.now(UTC))

    def hold(self, reason: str) -> None:
        """Put the sprint on hold (pending status).

        Args:
            reason: Why the sprint is being put on hold
        """
        object.__setattr__(self, 'pending_reason', reason)
        object.__setattr__(self, 'status', 'pending')
        object.__setattr__(self, 'updated_at', datetime.now(UTC))

    def block(self, reason: str) -> None:
        """Block the sprint.

        Args:
            reason: What is blocking the sprint
        """
        object.__setattr__(self, 'blocked_reason', reason)
        object.__setattr__(self, 'status', 'blocked')
        object.__setattr__(self, 'updated_at', datetime.now(UTC))

    def is_on_hold(self) -> bool:
        """Check if sprint is on hold (pending or blocked)."""
        return self.status in ("pending", "blocked")

    def can_transition_to(self, target_status: SprintStatus) -> bool:
        """Check if transition to target status is valid.

        Valid transitions follow this state machine:
        - new → pending, assigned, active, cancelled
        - pending → active, cancelled (requires pending_reason first)
        - assigned → active, pending, cancelled
        - active → in_progress, blocked, completed, cancelled
        - in_progress → active, blocked, completed, cancelled
        - blocked → active, in_progress, cancelled (requires blocked_reason first)
        - completed → (terminal state, no transitions)
        - cancelled → (terminal state, no transitions)

        Args:
            target_status: The status to transition to

        Returns:
            True if transition is valid, False otherwise
        """
        valid_transitions: dict[SprintStatus, tuple[SprintStatus, ...]] = {
            "new": ("pending", "assigned", "active", "cancelled"),
            "pending": ("active", "cancelled"),
            "assigned": ("active", "pending", "cancelled"),
            "active": ("in_progress", "blocked", "completed", "cancelled"),
            "in_progress": ("active", "blocked", "completed", "cancelled"),
            "blocked": ("active", "in_progress", "cancelled"),
            "completed": (),  # Terminal state
            "cancelled": (),  # Terminal state
        }
        return target_status in valid_transitions.get(self.status, ())


__all__ = ["Sprint", "SprintStatus"]
