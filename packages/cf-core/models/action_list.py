"""ActionList domain model for cf_core.

Provides a rich Pydantic v2 model for ActionList entities.
Aligned with TaskMan-v2 database schema (20 fields).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# Status types
ActionListStatus = Literal["active", "completed", "archived"]


class ActionList(BaseModel):
    """
    ActionList domain model.

    Represents a curated collection of tasks with metadata and lifecycle tracking.
    Aligned with TaskMan-v2 production schema (20 fields).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "title": "ActionList",
            "description": "Curated collection of tasks",
        },
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    # Identity
    id: str = Field(..., description="Unique identifier (AL-XXXX format)")
    name: str = Field(..., description="Action list name")
    description: str = Field(default="", description="Action list description")

    # Status
    status: ActionListStatus = Field(default="active", description="Current status")

    # Ownership & categorization
    owner: str = Field(default="system", description="Owner identifier")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")

    # Association fields
    project_id: str | None = Field(default=None, description="Associated project ID")
    sprint_id: str | None = Field(default=None, description="Associated sprint ID")

    # Task references (array of task IDs)
    task_ids: list[str] = Field(default_factory=list, description="List of task IDs")

    # Checklist items (rich action items structure)
    items: list[dict[str, Any]] = Field(
        default_factory=list, description="Checklist items with metadata"
    )

    # ContextForge metadata
    geometry_shape: str | None = Field(default=None, description="Geometric context shape")
    priority: str | None = Field(default=None, description="Priority level")
    due_date: datetime | None = Field(default=None, description="Due date")
    evidence_refs: list[str] = Field(default_factory=list, description="Evidence references")
    extra_metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    notes: str | None = Field(default=None, description="Free-form notes")

    # Soft delete tracking
    parent_deleted_at: datetime | None = Field(
        default=None, description="Parent deletion timestamp"
    )
    parent_deletion_note: dict[str, Any] = Field(
        default_factory=dict, description="Parent deletion metadata"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Last update timestamp"
    )
    completed_at: datetime | None = Field(default=None, description="Completion timestamp")

    # Legacy field mapping (for backward compatibility)
    # Note: 'created_by' in old schema maps to 'owner' in new schema
    @property
    def created_by(self) -> str:
        """Backward compatibility property for created_by field."""
        return self.owner
