"""ActionList Pydantic schemas.

Request/response schemas for ActionList API endpoints.
"""

from datetime import datetime

from pydantic import Field

from .base import BaseSchema, TimestampSchema


class ActionListCreateRequest(BaseSchema):
    """Schema for creating a new action list."""

    id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Action list ID",
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Action list title",
    )

    description: str | None = Field(
        default=None,
        description="Detailed description",
    )

    status: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Action list status",
    )

    owner: str | None = Field(
        default=None,
        max_length=100,
        description="Action list owner",
    )

    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorization",
    )

    project_id: str | None = Field(
        default=None,
        max_length=50,
        description="Associated project ID",
    )

    sprint_id: str | None = Field(
        default=None,
        max_length=50,
        description="Associated sprint ID",
    )

    items: list[dict] = Field(
        default_factory=list,
        description="Action items in JSON format",
    )

    geometry_shape: str | None = Field(
        default=None,
        max_length=20,
        description="Sacred Geometry shape",
    )

    priority: str | None = Field(
        default=None,
        max_length=20,
        description="Priority level",
    )

    due_date: datetime | None = Field(
        default=None,
        description="Due date",
    )

    evidence_refs: list[str] = Field(
        default_factory=list,
        description="Evidence reference URIs",
    )

    extra_metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata",
    )

    notes: str | None = Field(
        default=None,
        description="Additional notes",
    )

    parent_deleted_at: datetime | None = Field(
        default=None,
        description="Timestamp when parent was deleted (soft delete)",
    )

    parent_deletion_note: dict = Field(
        default_factory=dict,
        description="Note explaining parent deletion",
    )

    completed_at: datetime | None = Field(
        default=None,
        description="Timestamp when action list was completed",
    )


class ActionListUpdateRequest(BaseSchema):
    """Schema for updating an existing action list.

    All fields are optional for partial updates.
    """

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: str | None = Field(default=None, min_length=1, max_length=20)
    owner: str | None = Field(default=None, max_length=100)
    tags: list[str] | None = None

    project_id: str | None = Field(default=None, max_length=50)
    sprint_id: str | None = Field(default=None, max_length=50)
    items: list[dict] | None = None

    geometry_shape: str | None = Field(default=None, max_length=20)
    priority: str | None = Field(default=None, max_length=20)
    due_date: datetime | None = None

    evidence_refs: list[str] | None = None
    extra_metadata: dict | None = None
    notes: str | None = None

    parent_deleted_at: datetime | None = None
    parent_deletion_note: dict | None = None
    completed_at: datetime | None = None


class ActionListResponse(TimestampSchema):
    """Schema for action list API responses."""

    id: str
    title: str
    description: str | None
    status: str
    owner: str | None
    tags: list[str]

    project_id: str | None
    sprint_id: str | None
    items: list[dict]

    geometry_shape: str | None
    priority: str | None
    due_date: datetime | None

    evidence_refs: list[str]
    extra_metadata: dict
    notes: str | None

    parent_deleted_at: datetime | None
    parent_deletion_note: dict
    completed_at: datetime | None
