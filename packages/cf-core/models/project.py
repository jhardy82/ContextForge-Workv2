"""Project domain model for cf_core.

Provides a rich Pydantic v2 model for Project entities with:
- Status lifecycle (new, pending, assigned, active, in_progress, blocked, completed, cancelled)
- Date range validation (completed_at >= start_date, target_end_date > start_date)
- Status-based field validation (pending_reason, blocked_reason, owner, completed_at)
- Sprint and task association
- Team member management
- Action item tracking
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from cf_core.models.action_item import ActionItem
from cf_core.models.observability import Observability
from cf_core.models.phase_tracking import PhaseTracking
from cf_core.models.risk_entry import RiskEntrySimple

# Project status aligned with Task/Sprint status enums for consistency
# Uses full descriptive lifecycle: new -> pending -> assigned -> active -> in_progress -> blocked -> completed/cancelled
ProjectStatus = Literal[
    "new",
    "pending",
    "assigned",
    "active",
    "in_progress",
    "blocked",
    "completed",
    "cancelled",
]


class Project(BaseModel):
    """Domain model for Project entities.

    Attributes:
        id: Unique project identifier (P- prefix)
        name: Project name (1-200 characters)
        status: Current project status
        description: Optional project description
        owner: Project owner/lead (required for assigned/active/in_progress)
        start_date: Project start date
        target_end_date: Target completion date
        completed_at: Completion timestamp (required when status is 'completed')
        pending_reason: Reason if status is pending (required when status is 'pending')
        blocked_reason: Reason if status is blocked (required when status is 'blocked')
        context_ids: List of associated context IDs
        sprint_ids: List of associated sprint IDs
        task_ids: List of associated task IDs
        team_members: List of team member identifiers
        tags: List of tags
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    id: str = Field(..., pattern=r"^P-[a-zA-Z0-9_-]+$")
    name: str = Field(..., min_length=1, max_length=200)
    status: ProjectStatus = Field(default="new")
    description: str = Field(default="")

    # Core Fields
    owner: str | None = Field(default=None)
    mission: str | None = Field(default=None)
    vision: str | None = Field(default=None)
    roadmap_url: str | None = Field(default=None)

    start_date: datetime | None = Field(default=None)
    target_end_date: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)

    # Status Reasons
    pending_reason: str | None = Field(default=None)
    blocked_reason: str | None = Field(default=None)

    # Collections
    context_ids: list[str] = Field(default_factory=list)
    sprint_ids: list[str] = Field(default_factory=list)
    task_ids: list[str] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)

    # Stakeholders & Resources
    team_members: list[str] = Field(default_factory=list)
    sponsors: list[str] = Field(default_factory=list)
    stakeholders: list[str] = Field(default_factory=list)

    # Complex Fields
    observability: Observability = Field(
        default_factory=Observability.create_healthy
    )
    risks: list[RiskEntrySimple] = Field(default_factory=list)
    milestones: list[dict] = Field(
        default_factory=list
    )  # Placeholder for Milestone model or simple dict
    resources: list[dict] = Field(default_factory=list)
    dependencies: list[dict] = Field(default_factory=list)
    quality_gates: dict | None = Field(default=None)

    # Metrics
    tags: list[str] = Field(default_factory=list)
    budget: float | None = Field(default=None)
    spend: float | None = Field(default=None)
    progress: float | None = Field(default=None)  # 0-100
    health_score: int | None = Field(default=None)  # 0-100

    # Phase Tracking (Research -> Planning -> Implementation -> Testing)
    phases: PhaseTracking = Field(
        default_factory=PhaseTracking,
        description="Lifecycle phase tracking (research, planning, implementation, testing)"
    )

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("id", mode="before")
    @classmethod
    def validate_id_prefix(cls, v: str) -> str:
        """Validate that ID starts with P- prefix."""
        if not v or not v.startswith("P-") or len(v) <= 2:
            raise ValueError("Project ID must start with 'P-'")
        return v

    @field_validator("context_ids", mode="before")
    @classmethod
    def validate_context_ids(cls, v: list[str]) -> list[str]:
        """Validate that all context IDs start with CTX- prefix."""
        if v:
            for ctx_id in v:
                if not ctx_id.startswith("CTX-"):
                    raise ValueError("All context_ids must start with 'CTX-'")
        return v

    @field_validator("sprint_ids", mode="before")
    @classmethod
    def validate_sprint_ids(cls, v: list[str]) -> list[str]:
        """Validate that all sprint IDs start with S- prefix."""
        if v:
            for sprint_id in v:
                if not sprint_id.startswith("S-"):
                    raise ValueError("All sprint_ids must start with 'S-'")
        return v

    @field_validator("task_ids", mode="before")
    @classmethod
    def validate_task_ids(cls, v: list[str]) -> list[str]:
        """Validate that all task IDs start with T- prefix."""
        if v:
            for task_id in v:
                if not task_id.startswith("T-"):
                    raise ValueError("All task_ids must start with 'T-'")
        return v

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, v: list[str]) -> list[str]:
        """Strip whitespace, remove empty strings, and deduplicate tags."""
        if not v:
            return []
        # Strip whitespace, filter empty, deduplicate while preserving order
        seen = set()
        result = []
        for tag in v:
            stripped = tag.strip() if isinstance(tag, str) else tag
            if stripped and stripped not in seen:
                seen.add(stripped)
                result.append(stripped)
        return result

    @field_validator("team_members", mode="before")
    @classmethod
    def normalize_team_members(cls, v: list[str]) -> list[str]:
        """Strip whitespace and deduplicate team members."""
        if not v:
            return []
        # Deduplicate while preserving order
        seen = set()
        result = []
        for member in v:
            stripped = member.strip() if isinstance(member, str) else member
            if stripped and stripped not in seen:
                seen.add(stripped)
                result.append(stripped)
        return result

    @field_validator("start_date", "target_end_date", "completed_at", mode="before")
    @classmethod
    def ensure_utc(cls, v: datetime | None) -> datetime | None:
        """Convert naive datetimes to UTC."""
        if v is None:
            return v
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=UTC)
        return v

    @model_validator(mode="after")
    def validate_date_range(self) -> Project:
        """Validate that target_end_date is strictly after start_date."""
        if self.start_date and self.target_end_date:
            if self.target_end_date <= self.start_date:
                raise ValueError("target_end_date must be after start_date")
        return self

    @model_validator(mode="after")
    def validate_completed_at_range(self) -> Project:
        """Validate that completed_at is after or equal to start_date."""
        if self.start_date and self.completed_at:
            if self.completed_at < self.start_date:
                raise ValueError("completed_at must be after or equal to start_date")
        return self

    @model_validator(mode="after")
    def validate_completed_at_coupling(self) -> Project:
        """Validate bidirectional coupling between completed_at and status.

        - status='completed' requires completed_at
        - completed_at requires status='completed'
        """
        if self.status == "completed":
            if self.completed_at is None:
                raise ValueError("completed_at required when status is 'completed'")
        elif self.completed_at is not None:
            raise ValueError("completed_at can only be set when status is 'completed'")
        return self

    @model_validator(mode="after")
    def validate_pending_reason(self) -> Project:
        """Validate pending_reason required when status is 'pending'."""
        if self.status == "pending":
            if not self.pending_reason:
                raise ValueError("pending_reason required when status is 'pending'")
        return self

    @model_validator(mode="after")
    def validate_blocked_reason(self) -> Project:
        """Validate blocked_reason required when status is 'blocked'."""
        if self.status == "blocked":
            if not self.blocked_reason:
                raise ValueError("blocked_reason required when status is 'blocked'")
        return self

    @model_validator(mode="after")
    def validate_owner(self) -> Project:
        """Validate owner required when status in ('assigned', 'active', 'in_progress')."""
        if self.status in ("assigned", "active", "in_progress"):
            if not self.owner:
                raise ValueError(
                    f"owner required when status is '{self.status}'"
                )
        return self

    def is_active(self) -> bool:
        """Check if project is active or in progress."""
        return self.status in ("active", "in_progress")

    def is_completed(self) -> bool:
        """Check if project is completed."""
        return self.status == "completed"

    def is_on_hold(self) -> bool:
        """Check if project is on hold (pending or blocked)."""
        return self.status in ("pending", "blocked")

    def add_context(self, context_id: str) -> None:
        """Add a context ID to the project."""
        if context_id not in self.context_ids:
            self.context_ids.append(context_id)

    def remove_context(self, context_id: str) -> None:
        """Remove a context ID from the project."""
        if context_id in self.context_ids:
            self.context_ids.remove(context_id)

    def add_sprint(self, sprint_id: str) -> None:
        """Add a sprint ID to the project."""
        if sprint_id not in self.sprint_ids:
            self.sprint_ids.append(sprint_id)

    def add_task(self, task_id: str) -> None:
        """Add a task ID to the project."""
        if task_id not in self.task_ids:
            self.task_ids.append(task_id)

    def add_action_item(self, action_item: ActionItem) -> None:
        """Add an action item to the project."""
        if action_item not in self.action_items:
            self.action_items.append(action_item)

    def get_pending_actions(self) -> list[ActionItem]:
        """Get all pending action items."""
        return [a for a in self.action_items if a.is_pending()]

    def get_completed_actions(self) -> list[ActionItem]:
        """Get all completed action items."""
        return [a for a in self.action_items if a.is_completed()]

    def action_progress(self) -> tuple[int, int]:
        """Get action item progress as (completed, total)."""
        completed = len([a for a in self.action_items if a.is_completed()])
        return (completed, len(self.action_items))

    def mark_completed(self) -> None:
        """Mark the project as completed with current timestamp.

        Uses object.__setattr__ to bypass validation during the atomic update
        since status='completed' requires completed_at and vice versa.
        """
        now = datetime.now(UTC)
        # Bypass validation to set both fields atomically
        object.__setattr__(self, "completed_at", now)
        object.__setattr__(self, "status", "completed")
        object.__setattr__(self, "updated_at", now)

    def start(self) -> None:
        """Start the project by setting status to 'active'.

        Sets start_date to now if not already set.
        Requires owner to be set.
        """
        if not self.owner:
            raise ValueError("owner required to start project")
        if self.start_date is None:
            self.start_date = datetime.now(UTC)
        self.status = "active"
        self.updated_at = datetime.now(UTC)

    def hold(self, reason: str) -> None:
        """Put the project on hold (pending status)."""
        self.pending_reason = reason
        self.status = "pending"
        self.updated_at = datetime.now(UTC)

    def block(self, reason: str) -> None:
        """Block the project."""
        self.blocked_reason = reason
        self.status = "blocked"
        self.updated_at = datetime.now(UTC)

    def cancel(self) -> None:
        """Cancel the project."""
        self.status = "cancelled"
        self.updated_at = datetime.now(UTC)

    def can_transition_to(self, new_status: ProjectStatus) -> bool:
        """Check if transition to new_status is valid.

        Valid state transitions:
        - new -> pending, assigned, active, cancelled
        - pending -> new, assigned, active, cancelled
        - assigned -> pending, active, in_progress, cancelled
        - active -> pending, in_progress, blocked, completed, cancelled
        - in_progress -> active, blocked, completed, cancelled
        - blocked -> active, in_progress, cancelled
        - completed -> [] (terminal state)
        - cancelled -> [] (terminal state)

        Args:
            new_status: Target status to transition to

        Returns:
            bool: True if transition is valid, False otherwise
        """
        valid_transitions = {
            "new": ["pending", "assigned", "active", "cancelled"],
            "pending": ["new", "assigned", "active", "cancelled"],
            "assigned": ["pending", "active", "in_progress", "cancelled"],
            "active": ["pending", "in_progress", "blocked", "completed", "cancelled"],
            "in_progress": ["active", "blocked", "completed", "cancelled"],
            "blocked": ["active", "in_progress", "cancelled"],
            "completed": [],  # Terminal state
            "cancelled": [],  # Terminal state
        }
        return new_status in valid_transitions.get(self.status, [])


__all__ = ["Project", "ProjectStatus"]
