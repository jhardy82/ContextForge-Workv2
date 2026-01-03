"""Phase tracking Pydantic schemas.

Request/response schemas for Phase API endpoints.
"""

from typing import Any, Literal

from pydantic import Field

from taskman_api.core.enums import PhaseStatus

from .base import BaseSchema

# Entity type literal
EntityType = Literal["task", "sprint", "project"]


class PhaseUpdateRequest(BaseSchema):
    """Schema for updating a specific phase.

    Allows updating any phase field including status.
    """

    status: PhaseStatus | None = Field(
        default=None,
        description="Phase status",
    )

    # Common phase fields
    blocked_reason: str | None = Field(
        default=None,
        max_length=500,
        description="Reason for blocked status",
    )

    skip_reason: str | None = Field(
        default=None,
        max_length=500,
        description="Reason for skipping phase",
    )

    # Additional fields can be passed as dict
    additional_fields: dict[str, Any] | None = Field(
        default=None,
        description="Additional phase-specific fields",
    )


class PhaseStatusRequest(BaseSchema):
    """Schema for changing phase status only."""

    status: PhaseStatus = Field(
        ...,
        description="New phase status",
    )


class BlockPhaseRequest(BaseSchema):
    """Schema for blocking a phase."""

    blocked_reason: str | None = Field(
        default=None,
        max_length=500,
        description="Reason for blocking the phase",
    )


class SkipPhaseRequest(BaseSchema):
    """Schema for skipping a phase."""

    skip_reason: str | None = Field(
        default=None,
        max_length=500,
        description="Reason for skipping the phase",
    )


class PhaseResponse(BaseSchema):
    """Schema for single phase response."""

    phase_name: str = Field(
        ...,
        description="Name of the phase",
    )

    status: PhaseStatus = Field(
        ...,
        description="Current phase status",
    )

    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Full phase data including all fields",
    )


class PhasesResponse(BaseSchema):
    """Schema for all phases of an entity."""

    entity_id: str = Field(
        ...,
        description="Entity identifier",
    )

    entity_type: EntityType = Field(
        ...,
        description="Type of entity (task, sprint, project)",
    )

    phases: dict[str, Any] = Field(
        ...,
        description="All phases with their data",
    )


class PhaseSummaryResponse(BaseSchema):
    """Schema for phase summary with progress metrics."""

    entity_id: str = Field(
        ...,
        description="Entity identifier",
    )

    entity_type: EntityType = Field(
        ...,
        description="Type of entity",
    )

    current_phase: str | None = Field(
        default=None,
        description="Name of currently active phase",
    )

    phases_completed: int = Field(
        ...,
        ge=0,
        description="Number of completed phases",
    )

    phases_total: int = Field(
        ...,
        ge=0,
        description="Total number of phases for this entity type",
    )

    completion_pct: float = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage of phases completed",
    )

    phases: dict[str, Any] = Field(
        ...,
        description="Full phase details",
    )


class EntityInPhaseResponse(BaseSchema):
    """Schema for entity found in a specific phase."""

    id: str = Field(
        ...,
        description="Entity identifier",
    )

    phase: str = Field(
        ...,
        description="Phase name",
    )

    status: str = Field(
        ...,
        description="Phase status value",
    )

    phase_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Full phase data",
    )


class BlockedEntityResponse(BaseSchema):
    """Schema for blocked entity summary."""

    entity_type: EntityType = Field(
        ...,
        description="Type of entity",
    )

    entity_id: str = Field(
        ...,
        description="Entity identifier",
    )

    phase: str = Field(
        ...,
        description="Blocked phase name",
    )

    blocked_reason: str | None = Field(
        default=None,
        description="Reason for being blocked",
    )


class PhaseAnalyticsResponse(BaseSchema):
    """Schema for phase analytics across entities."""

    entity_type: EntityType = Field(
        ...,
        description="Type of entities analyzed",
    )

    total_entities: int = Field(
        ...,
        ge=0,
        description="Total number of entities",
    )

    by_phase: dict[str, dict[str, int]] = Field(
        ...,
        description="Count of entities by phase and status",
    )

    blocked_count: int = Field(
        ...,
        ge=0,
        description="Number of entities with blocked phases",
    )

    average_completion_pct: float = Field(
        ...,
        ge=0,
        le=100,
        description="Average phase completion percentage",
    )
