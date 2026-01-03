"""
Full ActionList schemas matching the 20-field database schema.
Includes items, evidence refs, and ContextForge integration.
"""
from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from taskman_api.core.enums import ActionListStatus
from taskman_api.schemas.base import TaskManBaseModel, TimestampMixin


# =============================================================================
# ActionList Create Schema
# =============================================================================
class ActionListCreate(TaskManBaseModel):
    """Request schema for creating a new action list.

    All action lists must have a unique ID (AL-xxx format) and a title.
    Additional metadata and ContextForge integration fields are optional.
    """

    # Core fields
    id: str = Field(
        ...,
        pattern=r"^AL-[A-Za-z0-9_-]+$",
        description="Unique action list identifier (must start with 'AL-')",
        examples=["AL-sprint-tasks", "AL-backend-api-work"],
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Action list title (human-readable name)",
        examples=["Sprint 2025-Q1 Backend Tasks", "Technical Debt Backlog"],
    )
    description: str | None = Field(
        None,
        max_length=2000,
        description="Detailed description of the action list purpose and scope",
        examples=["Core API implementation tasks for Q1 sprint cycle"],
    )
    status: ActionListStatus = Field(
        ActionListStatus.ACTIVE,
        description="Current status of the action list (active, completed, archived)",
    )

    # Ownership
    owner: str | None = Field(
        None,
        max_length=100,
        description="Owner or team responsible for this action list",
        examples=["backend-team", "john.doe", "devops"],
    )

    # Tags
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorization and filtering",
        examples=[["api", "backend", "priority"]],
    )

    # Project/Sprint associations (optional)
    project_id: str | None = Field(
        None,
        description="Associated project identifier for grouping lists",
        examples=["PROJ-001", "backend-redesign"],
    )
    sprint_id: str | None = Field(
        None,
        description="Associated sprint identifier for time-boxing",
        examples=["SPRINT-2025-Q1", "sprint-24"],
    )

    # Items (JSON array with text, completed, order)
    items: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Checklist items with text, completion status, and order",
        examples=[
            [
                {"text": "Implement authentication", "completed": False, "order": 0},
                {"text": "Add tests", "completed": False, "order": 1},
            ]
        ],
    )

    # ContextForge integration
    geometry_shape: str | None = Field(
        None,
        description="ContextForge geometry shape for spatial organization",
        examples=["rectangle", "circle", "polygon"],
    )
    priority: str | None = Field(
        None,
        description="Priority level for task ordering and visualization",
        examples=["high", "medium", "low", "critical"],
    )
    due_date: datetime | None = Field(
        None,
        description="Due date for the action list (ISO-8601 timestamp)",
        examples=["2025-12-31T23:59:59Z"],
    )

    # Evidence and metadata
    evidence_refs: list[str] = Field(
        default_factory=list,
        description="References to evidence artifacts (logs, test results, etc.)",
        examples=[["EVD-001", "EVD-002"]],
    )
    extra_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional custom metadata for extensibility",
        examples=[{"velocity": 8, "confidence": 0.85, "team_size": 3}],
    )
    notes: str | None = Field(
        None,
        description="Free-form notes for additional context",
        examples=["Critical path items for Q1 release"],
    )


# =============================================================================
# ActionList Update Schema
# =============================================================================
class ActionListUpdate(TaskManBaseModel):
    """Request schema for updating an action list.

    All fields are optional - only provided fields will be modified.
    The updated_at timestamp is automatically set on any update.
    """

    title: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="New action list title",
        examples=["Updated Sprint Tasks"],
    )
    description: str | None = Field(
        None, description="New description", examples=["Updated task list with documentation work"]
    )
    status: ActionListStatus | None = Field(
        None, description="New status (active, completed, archived)"
    )
    owner: str | None = Field(None, description="New owner or team", examples=["frontend-team"])
    tags: list[str] | None = Field(
        None,
        description="New tags array (replaces existing tags)",
        examples=[["api", "backend", "docs"]],
    )
    project_id: str | None = Field(None, description="New project association")
    sprint_id: str | None = Field(None, description="New sprint association")
    items: list[dict[str, Any]] | None = Field(
        None,
        description="Updated checklist items (replaces all items)",
        examples=[
            [
                {"text": "Task 1", "completed": True, "order": 0},
                {"text": "Task 2", "completed": False, "order": 1},
            ]
        ],
    )
    geometry_shape: str | None = Field(None, description="New ContextForge geometry shape")
    priority: str | None = Field(
        None, description="New priority level", examples=["critical", "high"]
    )
    due_date: datetime | None = Field(None, description="New due date (ISO-8601)")
    evidence_refs: list[str] | None = Field(None, description="Updated evidence references")
    extra_metadata: dict[str, Any] | None = Field(None, description="Updated custom metadata")
    notes: str | None = Field(None, description="Updated notes")
    completed_at: datetime | None = Field(
        None,
        description="Completion timestamp (set when marking as completed)",
        examples=["2025-12-28T18:00:00Z"],
    )


# =============================================================================
# ActionList Response Schema
# =============================================================================
class ActionListResponse(TaskManBaseModel, TimestampMixin):
    """Full action list response schema with all 20 database fields.

    Returned by GET, POST, PUT/PATCH operations. Includes complete action list
    details with metadata, associations, and timestamps.
    """

    id: str = Field(
        ...,
        description="Unique action list identifier (AL-xxx format)",
        examples=["AL-sprint-tasks"],
    )
    title: str = Field(
        ...,
        validation_alias="name",
        description="Action list title (human-readable name)",
        examples=["Sprint 2025-Q1 Backend Tasks"],
    )
    description: str | None = Field(None, description="Detailed description of the action list")
    status: ActionListStatus = Field(
        ..., description="Current status (active, completed, archived)"
    )
    owner: str | None = Field(None, description="Owner or team responsible for this list")
    tags: list[str] = Field(
        default_factory=list, description="Tags for categorization and filtering"
    )
    project_id: str | None = Field(None, description="Associated project identifier")
    sprint_id: str | None = Field(None, description="Associated sprint identifier")
    items: list[dict[str, Any] | str] = Field(
        default_factory=list,
        validation_alias="task_ids",
        description="Checklist items with text, completion status, and order",
    )
    geometry_shape: str | None = Field(
        None, description="ContextForge geometry shape for spatial organization"
    )
    priority: str | None = Field(None, description="Priority level for ordering and visualization")
    due_date: datetime | None = Field(
        None, description="Due date for the action list (ISO-8601 timestamp)"
    )
    evidence_refs: list[str] = Field(
        default_factory=list, description="References to evidence artifacts"
    )
    extra_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional custom metadata"
    )
    notes: str | None = Field(None, description="Free-form notes")
    parent_deleted_at: datetime | None = Field(
        None, description="Timestamp when parent was deleted (null if not deleted)"
    )
    parent_deletion_note: dict[str, Any] = Field(
        default_factory=dict, description="Metadata about parent deletion"
    )
    completed_at: datetime | None = Field(
        None, description="Timestamp when action list was marked completed"
    )

    @field_validator("status", mode="before")
    @classmethod
    def parse_status(cls, v: str | ActionListStatus) -> ActionListStatus:
        if isinstance(v, ActionListStatus):
            return v
        return ActionListStatus(v)


# =============================================================================
# ActionList Collection Response
# =============================================================================
class ActionListCollection(TaskManBaseModel):
    """Paginated collection of action lists.

    Returned by list endpoint with filtering and pagination support.
    Use 'has_more' to determine if additional pages exist.
    """

    action_lists: list[ActionListResponse] = Field(
        ..., description="Array of action list objects for the current page"
    )
    total: int = Field(
        ..., ge=0, description="Total number of action lists matching the filter criteria"
    )
    page: int = Field(..., ge=1, description="Current page number (1-indexed)")
    per_page: int = Field(..., ge=1, le=100, description="Number of items per page (maximum 100)")
    has_more: bool = Field(..., description="Whether additional pages exist after the current page")


# =============================================================================
# ActionList Item Schemas
# =============================================================================
class ActionListItem(TaskManBaseModel):
    """Individual item in an action list."""

    id: str = Field(..., description="Item ID")
    text: str = Field(..., min_length=1, description="Item text")
    completed: bool = Field(False, description="Completion status")
    order: int = Field(0, ge=0, description="Display order")
    created_at: datetime | None = None
    completed_at: datetime | None = None


class ActionListAddItemRequest(TaskManBaseModel):
    """Request to add item to action list."""

    text: str = Field(..., min_length=1, description="Item text")
    order: int | None = Field(None, ge=0, description="Optional position")


class ReorderItemsRequest(TaskManBaseModel):
    """Request to reorder items in action list."""

    item_ids: list[str] = Field(..., description="Item IDs in desired order")

ActionListCreateRequest = ActionListCreate
ActionListUpdateRequest = ActionListUpdate
