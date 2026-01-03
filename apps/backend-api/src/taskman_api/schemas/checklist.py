"""Checklist Pydantic schemas.

Request/response schemas for checklist API endpoints.
Supports reusable checklist templates and item lifecycle tracking.
"""

from datetime import datetime
from typing import Literal

from pydantic import Field, computed_field

from .base import BaseSchema, TimestampSchema


# Status type aliases
ChecklistStatus = Literal["active", "completed", "archived"]
ChecklistItemStatus = Literal["pending", "in_progress", "completed", "skipped", "blocked"]
ChecklistItemPriority = Literal["low", "medium", "high", "critical"]


# ============================================================================
# Checklist Item Schemas
# ============================================================================


class ChecklistItemInput(BaseSchema):
    """Schema for checklist item input (create/update)."""

    id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Checklist item ID, prefer CLI-* prefix",
    )

    order: int = Field(
        ...,
        ge=1,
        description="Item order in checklist",
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Item title",
    )

    description: str | None = Field(
        default=None,
        description="Detailed item description",
    )

    # Lifecycle
    status: ChecklistItemStatus = Field(
        default="pending",
        description="Item status",
    )

    priority: ChecklistItemPriority = Field(
        default="medium",
        description="Item priority",
    )

    # Timing
    due_at: datetime | None = Field(
        default=None,
        description="Due date",
    )

    # Assignment
    assignee: str | None = Field(
        default=None,
        max_length=100,
        description="Assigned user",
    )

    # Evidence
    artifacts: list[str] = Field(
        default_factory=list,
        description="Files/URIs associated with item",
    )


class ChecklistItemResponse(BaseSchema):
    """Schema for checklist item API responses."""

    id: str
    order: int
    title: str
    description: str | None = None

    # Lifecycle (may not be present in JSON)
    status: ChecklistItemStatus = "pending"
    priority: ChecklistItemPriority = "medium"

    # Timing (may not be present in JSON)
    created_at: datetime | None = None
    completed_at: datetime | None = None
    due_at: datetime | None = None

    # Assignment
    assignee: str | None = None

    # Evidence (may not be present in JSON)
    notes: str | None = None
    artifacts: list[str] = Field(default_factory=list)


class ChecklistItemUpdateRequest(BaseSchema):
    """Schema for updating a checklist item."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: ChecklistItemStatus | None = None
    priority: ChecklistItemPriority | None = None
    due_at: datetime | None = None
    assignee: str | None = None
    notes: str | None = None
    artifacts: list[str] | None = None


class ChecklistItemAddRequest(BaseSchema):
    """Schema for adding a new item to an existing checklist."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Item title",
    )

    description: str | None = Field(
        default=None,
        description="Item description",
    )

    priority: ChecklistItemPriority = Field(
        default="medium",
        description="Item priority",
    )

    due_at: datetime | None = Field(
        default=None,
        description="Due date",
    )

    assignee: str | None = Field(
        default=None,
        max_length=100,
        description="Assigned user",
    )

    # Insert position (optional, defaults to end)
    after_item_id: str | None = Field(
        default=None,
        description="Insert after this item ID (optional)",
    )


# ============================================================================
# Checklist Schemas
# ============================================================================


class ChecklistCreateRequest(BaseSchema):
    """Schema for creating a new checklist."""

    id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Checklist ID, prefer CL-* prefix",
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Checklist title",
    )

    description: str | None = Field(
        default=None,
        description="Checklist description",
    )

    # Items
    items: list[ChecklistItemInput] = Field(
        default_factory=list,
        description="Checklist items",
    )

    # Context
    conversation_id: str | None = Field(
        default=None,
        max_length=100,
        description="Associated conversation",
    )

    plan_id: str | None = Field(
        default=None,
        max_length=100,
        description="Associated plan",
    )

    task_id: str | None = Field(
        default=None,
        max_length=50,
        description="Associated task",
    )

    # Templates
    is_template: bool = Field(
        default=False,
        description="True if this is a reusable template",
    )

    template_id: str | None = Field(
        default=None,
        max_length=100,
        description="Source template if cloned",
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


class ChecklistUpdateRequest(BaseSchema):
    """Schema for updating an existing checklist.

    All fields are optional for partial updates.
    """

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: ChecklistStatus | None = None

    # Context
    conversation_id: str | None = Field(default=None, max_length=100)
    plan_id: str | None = Field(default=None, max_length=100)
    task_id: str | None = Field(default=None, max_length=50)

    # Templates
    is_template: bool | None = None

    # Metadata
    tags: list[str] | None = None
    metadata: dict | None = None


class ChecklistResponse(TimestampSchema):
    """Schema for checklist API responses."""

    model_config = {"from_attributes": True, "populate_by_name": True}

    id: str
    title: str
    description: str | None
    status: ChecklistStatus

    # Items
    items: list[ChecklistItemResponse]

    # Context
    conversation_id: str | None
    plan_id: str | None
    task_id: str | None

    # Templates
    is_template: bool
    template_id: str | None

    # Lifecycle
    completed_at: datetime | None

    # Metadata
    tags: list[str]
    # Note: SQLAlchemy reserves 'metadata', so ORM uses 'extra_metadata'
    metadata: dict = Field(validation_alias="extra_metadata")

    @computed_field
    @property
    def progress_pct(self) -> float:
        """Calculate completion percentage."""
        if not self.items:
            return 0.0
        completed = sum(1 for i in self.items if i.status == "completed")
        return (completed / len(self.items)) * 100

    @computed_field
    @property
    def pending_count(self) -> int:
        """Count pending items."""
        return sum(1 for i in self.items if i.status == "pending")

    @computed_field
    @property
    def blocked_count(self) -> int:
        """Count blocked items."""
        return sum(1 for i in self.items if i.status == "blocked")


# ============================================================================
# Checklist List/Action Schemas
# ============================================================================


class ChecklistListResponse(BaseSchema):
    """Schema for listing checklists."""

    checklists: list[ChecklistResponse]
    total: int


class ChecklistFromTemplateRequest(BaseSchema):
    """Schema for creating checklist from template."""

    new_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="ID for the new checklist",
    )

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Override template title (optional)",
    )

    # Context for new checklist
    conversation_id: str | None = Field(
        default=None,
        max_length=100,
        description="Associated conversation",
    )

    plan_id: str | None = Field(
        default=None,
        max_length=100,
        description="Associated plan",
    )

    task_id: str | None = Field(
        default=None,
        max_length=50,
        description="Associated task",
    )


class ItemCompleteRequest(BaseSchema):
    """Schema for completing a checklist item."""

    notes: str | None = Field(
        default=None,
        description="Completion notes",
    )

    artifacts: list[str] = Field(
        default_factory=list,
        description="Artifacts produced",
    )
