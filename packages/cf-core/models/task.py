"""Task domain model for cf_core - Schema-aligned version.

Provides a rich Pydantic v2 model for Task entities aligned with tracker-task.schema.json:
- Status lifecycle (new, ready, in_progress, blocked, review, done, dropped)
- Priority levels (p0, p1, p2, p3)
- Full observability tracking
- Multi-project/sprint associations
- Quality gates and verification
- Backward compatibility via property aliases
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from cf_core.models.action_item import ActionItem
from cf_core.models.action_taken import ActionTaken
from cf_core.models.blocker_entry import BlockerEntry
from cf_core.models.observability import Observability
from cf_core.models.quality_gates import QualityGates
from cf_core.models.relationship_ref import RelationshipRef
from cf_core.models.risk_entry import RiskEntrySimple
from cf_core.models.verification import Verification

# Schema-aligned enums (keeping old for backward compatibility during migration)
# Schema-aligned enums
TaskStatus = Literal[
    "new", "ready", "in_progress", "blocked", "review", "done", "dropped", "cancelled"
]
TaskSeverity = Literal["sev1", "sev2", "sev3", "sev4"]
TaskShape = Literal["Triangle", "Circle", "Spiral", "Fractal", "Pentagon", "Dodecahedron"]

# Priority is now stored as int (0=critical/p0, 1=urgent/p1, 2=high/p2, 3=medium/p3, 4=low/p4)
# Lower number = higher priority for sequential sorting
PRIORITY_STRING_TO_INT: dict[str, int] = {
    "p0": 0, "critical": 0,
    "p1": 1, "urgent": 1,
    "p2": 2, "high": 2,
    "p3": 3, "medium": 3,
    "p4": 4, "low": 4,
}
PRIORITY_INT_TO_LABEL: dict[int, str] = {
    0: "P0 (Critical)",
    1: "P1 (Urgent)",
    2: "P2 (High)",
    3: "P3 (Medium)",
    4: "P4 (Low)",
}


class Task(BaseModel):
    """Domain model for Task entities aligned with tracker-task.schema.json v1.1.1.

    This model provides full compatibility with the authoritative JSON schema while
    maintaining backward compatibility via property aliases.

    Required Fields (from schema):
        id: Unique task identifier (T-xxx pattern)
        title: Task title
        summary: Brief summary (different from description)
        description: Detailed task description
        status: Current task status
        owner: Primary task owner
        priority: Task priority level
        created_at: Creation timestamp
        updated_at: Last update timestamp
        primary_project: Primary project ID (P-xxx)
        primary_sprint: Primary sprint ID (S-xxx)
        observability: Health tracking and heartbeat
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    # =========================================================================
    # REQUIRED FIELDS (from schema)
    # =========================================================================

    id: str = Field(..., min_length=3, pattern=r"^T-[A-Za-z0-9_-]+$")
    title: str = Field(..., min_length=1, max_length=200)
    summary: str = Field(..., min_length=1, description="Brief summary of the task")
    description: str = Field(..., description="Detailed task description")
    status: TaskStatus = Field(default="new")
    owner: str = Field(..., description="Primary task owner")
    priority: int = Field(default=3, ge=0, le=9, description="Priority (0=highest/P0, 9=lowest)")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    primary_project: str = Field(..., pattern=r"^P-[A-Za-z0-9_-]+$")
    primary_sprint: str = Field(..., pattern=r"^S-[A-Za-z0-9_-]+$")
    observability: Observability = Field(default_factory=Observability.create_healthy)

    # =========================================================================
    # VALIDATORS
    # =========================================================================

    @field_validator("priority", mode="before")
    @classmethod
    def coerce_priority(cls, v: int | str) -> int:
        """Accept int or string priority (p0, p1, critical, etc) and convert to int."""
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            v_lower = v.lower().strip()
            if v_lower in PRIORITY_STRING_TO_INT:
                return PRIORITY_STRING_TO_INT[v_lower]
            # Try parsing as int string
            if v_lower.isdigit():
                return int(v_lower)
            raise ValueError(f"Invalid priority '{v}'. Use int (0-9) or p0/p1/p2/p3/p4")
        raise ValueError(f"Priority must be int or str, got {type(v).__name__}")

    @property
    def priority_label(self) -> str:
        """Human-readable priority label."""
        return PRIORITY_INT_TO_LABEL.get(self.priority, f"P{self.priority}")

    # =========================================================================
    # CORE OPTIONAL FIELDS
    # =========================================================================

    # Associations (schema names)
    assignees: list[str] = Field(default_factory=list, description="Multiple assignees")
    parents: list[str] = Field(default_factory=list, description="Parent task IDs")
    depends_on: list[str] = Field(default_factory=list, description="Dependency task IDs")
    blocks: list[str] = Field(default_factory=list, description="Tasks this blocks")
    related_projects: list[RelationshipRef] = Field(default_factory=list)
    related_sprints: list[RelationshipRef] = Field(default_factory=list)
    related_links: list[str] = Field(default_factory=list, description="External URIs")

    # Effort tracking (schema names)
    estimate_points: float | None = Field(default=None, ge=0, description="Story point estimate")
    actual_time_hours: float | None = Field(default=None, ge=0, description="Actual hours spent")
    due_at: datetime | None = Field(default=None, description="Task due date/time")

    # Classification
    labels: list[str] = Field(default_factory=list, description="Task labels/tags")
    severity: TaskSeverity | None = Field(default=None, description="Issue severity")
    work_type: str | None = Field(default=None, description="Type of work (feature, refactor, etc)")
    work_stream: str | None = Field(default=None, description="Thematic work stream")
    stage: str | None = Field(default=None, description="Lifecycle stage")
    shape: TaskShape | None = Field(default=None, description="Geometry shape classification")

    # Planning & Execution
    acceptance_criteria: list[str] = Field(default_factory=list)
    definition_of_done: list[str] = Field(default_factory=list)
    blockers: list[BlockerEntry] = Field(
        default_factory=list, description="Structured blocker tracking"
    )
    actions_taken: list[ActionTaken] = Field(default_factory=list, description="Audit trail")

    # Quality & Verification
    quality_gates: QualityGates | None = Field(
        default=None, description="Test/lint/security status"
    )
    verification: Verification | None = Field(default=None, description="MPV evidence tracking")
    risks: list[RiskEntrySimple] = Field(default_factory=list, description="Task-level risks")

    # Metrics & Scoring
    business_value_score: int | None = Field(
        default=None, ge=0, le=10, description="Business value (0-10)"
    )
    cost_of_delay_score: int | None = Field(
        default=None, ge=0, le=10, description="Cost of delay (0-10)"
    )
    automation_candidate: bool = Field(default=False, description="Candidate for automation")
    cycle_time_days: float | None = Field(
        default=None, ge=0, description="Computed cycle time (read-only)"
    )

    # Timestamps
    completed_at: datetime | None = Field(default=None)

    # =========================================================================
    # LEGACY FIELDS (for backward compatibility - will deprecate)
    # =========================================================================

    # Keep old field names
    project_id: str | None = Field(default=None, description="DEPRECATED: Use primary_project")
    sprint_id: str | None = Field(default=None, description="DEPRECATED: Use primary_sprint")
    assignee: str | None = Field(default=None, description="DEPRECATED: Use owner")
    parent_id: str | None = Field(default=None, description="DEPRECATED: Use parents array")
    blocked_reason: str | None = Field(default=None, description="DEPRECATED: Use blockers array")
    tags: list[str] = Field(default_factory=list, description="DEPRECATED: Use labels")
    action_items: list[ActionItem] = Field(default_factory=list, description="Legacy action items")
    estimated_hours: float | None = Field(
        default=None, ge=0, description="DEPRECATED: Use estimate_points"
    )
    actual_hours: float | None = Field(
        default=None, ge=0, description="DEPRECATED: Use actual_time_hours"
    )
    story_points: int | None = Field(
        default=None, ge=1, le=21, description="DEPRECATED: Use estimate_points"
    )
    due_date: datetime | None = Field(default=None, description="DEPRECATED: Use due_at")

    # COF 13 Dimensions (keeping for existing functionality)
    cof_motivational: str | None = Field(default=None)
    cof_relational: str | None = Field(default=None)
    cof_situational: str | None = Field(default=None)
    cof_resource: str | None = Field(default=None)
    cof_narrative: str | None = Field(default=None)
    cof_recursive: str | None = Field(default=None)
    cof_sacred_geometry: str | None = Field(default=None)
    cof_computational: str | None = Field(default=None)
    cof_emergent: str | None = Field(default=None)
    cof_temporal: str | None = Field(default=None)
    cof_spatial: str | None = Field(default=None)
    cof_holistic: str | None = Field(default=None)
    cof_dimensional: str | None = Field(default=None)
    cof_validation: str | None = Field(default=None)
    cof_integration: str | None = Field(default=None)

    # =========================================================================
    # VALIDATORS
    # =========================================================================

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, v: str | None) -> str:
        """Convert None to empty string for description."""
        if v is None:
            return ""
        return v

    @field_validator("id", mode="before")
    @classmethod
    def validate_task_id(cls, v: str) -> str:
        """Validate task ID format (T- prefix required)."""
        if not v:
            raise ValueError("Task ID required")
        if not v.startswith("T-"):
            raise ValueError("Task ID must start with 'T-' prefix")
        if len(v) <= 2:
            raise ValueError("Task ID must have at least one character after 'T-'")
        return v

    @model_validator(mode="after")
    def validate_completed_at(self) -> Task:
        """Ensure completed_at is set when status is 'done'."""
        if self.status == "done" and self.completed_at is None:
            self.completed_at = datetime.now(UTC)
        return self

    @model_validator(mode="after")
    def sync_legacy_fields(self) -> Task:
        """Sync legacy and new field names for backward compatibility."""
        # Sync project/sprint IDs
        if self.project_id and not self.primary_project:
            # Use project_id as fallback (but log warning in production)
            pass
        if self.sprint_id and not self.primary_sprint:
            # Use sprint_id as fallback
            pass

        # Sync assignee/owner
        if self.assignee and not self.owner:
            self.owner = self.assignee

        # Sync tags/labels
        if self.tags and not self.labels:
            self.labels = self.tags.copy()

        return self

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def is_blocked(self) -> bool:
        """Check if task is currently blocked."""
        return self.status == "blocked" or len(self.blockers) > 0

    def is_complete(self) -> bool:
        """Check if task is completed."""
        return self.status == "done"

    def is_in_progress(self) -> bool:
        """Check if task is actively being worked on."""
        return self.status in ("doing", "in_progress")

    def update_heartbeat(self) -> None:
        """Update the observability heartbeat."""
        self.observability.update_heartbeat()
        self.updated_at = datetime.now(UTC)

    def add_blocker(self, blocker: BlockerEntry) -> None:
        """Add a blocker and update status."""
        self.blockers.append(blocker)
        if self.status != "blocked":
            self.status = "blocked"
        self.observability.set_health("yellow", f"Blocked: {blocker.description}")

    def clear_blockers(self) -> None:
        """Clear all blockers and optionally update status."""
        self.blockers.clear()
        if self.status == "blocked":
            self.status = "in_progress"
        self.observability.set_health("green", "Blockers cleared")
