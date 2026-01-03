"""Plan Pydantic schemas.

Request/response schemas for multi-step plan API endpoints.
Supports plan-driven development workflows.
"""

from datetime import datetime
from typing import Literal

from pydantic import Field, computed_field

from .base import BaseSchema, TimestampSchema


# Status type aliases
PlanStatus = Literal["draft", "approved", "in_progress", "completed", "abandoned"]
StepStatus = Literal["pending", "in_progress", "completed", "skipped", "blocked"]


# ============================================================================
# Plan Step Schemas
# ============================================================================


class PlanStepInput(BaseSchema):
    """Schema for plan step input (create/update)."""

    id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Step ID, prefer STEP-* prefix",
    )

    order: int = Field(
        ...,
        ge=1,
        description="Step order in plan",
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Step title",
    )

    description: str | None = Field(
        default=None,
        description="Detailed step description",
    )

    status: StepStatus = Field(
        default="pending",
        description="Step status",
    )

    # Dependencies
    depends_on: list[str] = Field(
        default_factory=list,
        description="Step IDs this step depends on",
    )

    # Evidence
    artifacts: list[str] = Field(
        default_factory=list,
        description="Files/URIs produced by this step",
    )


class PlanStepResponse(BaseSchema):
    """Schema for plan step API responses."""

    id: str
    order: int
    title: str
    description: str | None = None
    status: StepStatus = "pending"

    # Execution (optional - may not be present in JSON)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    notes: str | None = None

    # Dependencies
    depends_on: list[str] = Field(default_factory=list)

    # Evidence
    artifacts: list[str] = Field(default_factory=list)


class PlanStepUpdateRequest(BaseSchema):
    """Schema for updating a plan step."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: StepStatus | None = None
    notes: str | None = None
    depends_on: list[str] | None = None
    artifacts: list[str] | None = None


# ============================================================================
# Plan Schemas
# ============================================================================


class PlanCreateRequest(BaseSchema):
    """Schema for creating a new plan."""

    id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Plan ID, prefer PLAN-* prefix",
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Plan title",
    )

    description: str | None = Field(
        default=None,
        description="Plan description",
    )

    # Structure
    steps: list[PlanStepInput] = Field(
        default_factory=list,
        description="Plan steps",
    )

    # Context
    conversation_id: str | None = Field(
        default=None,
        max_length=100,
        description="Originating conversation",
    )

    project_id: str | None = Field(
        default=None,
        max_length=50,
        description="Associated project",
    )

    sprint_id: str | None = Field(
        default=None,
        max_length=50,
        description="Associated sprint",
    )

    # Metadata
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorization",
    )

    metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata",
    )


class PlanUpdateRequest(BaseSchema):
    """Schema for updating an existing plan.

    All fields are optional for partial updates.
    """

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: PlanStatus | None = None

    # Context
    conversation_id: str | None = Field(default=None, max_length=100)
    project_id: str | None = Field(default=None, max_length=50)
    sprint_id: str | None = Field(default=None, max_length=50)

    # Metadata
    tags: list[str] | None = None
    metadata: dict | None = None


class PlanResponse(TimestampSchema):
    """Schema for plan API responses."""

    model_config = {"from_attributes": True, "populate_by_name": True}

    id: str
    title: str
    description: str | None
    status: PlanStatus

    # Structure
    steps: list[PlanStepResponse]

    # Context
    conversation_id: str | None
    project_id: str | None
    sprint_id: str | None

    # Lifecycle
    approved_at: datetime | None
    completed_at: datetime | None

    # Metadata
    tags: list[str]
    # Note: SQLAlchemy reserves 'metadata', so ORM uses 'extra_metadata'
    metadata: dict = Field(validation_alias="extra_metadata")

    @computed_field
    @property
    def progress_pct(self) -> float:
        """Calculate completion percentage."""
        if not self.steps:
            return 0.0
        completed = sum(1 for s in self.steps if s.status == "completed")
        return (completed / len(self.steps)) * 100

    @computed_field
    @property
    def current_step_id(self) -> str | None:
        """Get ID of current step (first pending/in_progress)."""
        for step in sorted(self.steps, key=lambda s: s.order):
            if step.status in ("pending", "in_progress"):
                return step.id
        return None


# ============================================================================
# Plan List/Action Schemas
# ============================================================================


class PlanListResponse(BaseSchema):
    """Schema for listing plans."""

    plans: list[PlanResponse]
    total: int


class PlanApproveRequest(BaseSchema):
    """Schema for approving a plan."""

    notes: str | None = Field(
        default=None,
        description="Approval notes",
    )


class StepStartRequest(BaseSchema):
    """Schema for starting a step."""

    notes: str | None = Field(
        default=None,
        description="Notes on starting step",
    )


class StepCompleteRequest(BaseSchema):
    """Schema for completing a step."""

    notes: str | None = Field(
        default=None,
        description="Completion notes",
    )

    artifacts: list[str] = Field(
        default_factory=list,
        description="Artifacts produced during step",
    )


class StepSkipRequest(BaseSchema):
    """Schema for skipping a step."""

    reason: str = Field(
        ...,
        min_length=1,
        description="Reason for skipping",
    )
