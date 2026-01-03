"""Sprint Pydantic schemas.

Request/response schemas for Sprint API endpoints.
"""

import re
from datetime import date

from pydantic import Field, field_validator

from taskman_api.core.enums import SprintCadence, SprintStatus

from .base import BaseSchema, TimestampSchema


class SprintCreateRequest(BaseSchema):
    """Schema for creating a new sprint."""

    id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Sprint ID matching pattern S-[A-Za-z0-9_-]+",
        examples=["S-2025-01", "S-ULOG-SPRINT-1"],
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Sprint name",
    )

    goal: str = Field(
        ...,
        min_length=1,
        description="Sprint goal/objective",
    )

    cadence: SprintCadence = Field(
        ...,
        description="Sprint cadence",
    )

    start_date: date = Field(
        ...,
        description="Sprint start date",
    )

    end_date: date = Field(
        ...,
        description="Sprint end date",
    )

    status: SprintStatus = Field(
        default=SprintStatus.PLANNED,
        description="Sprint status",
    )

    owner: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Sprint owner/Scrum Master",
    )

    primary_project: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Primary project this sprint belongs to",
    )

    tasks: list[str] = Field(
        default_factory=list,
        description="Task IDs assigned to this sprint",
    )

    imported_tasks: list[dict] = Field(
        default_factory=list,
        description="Imported tasks [{id, counts_toward_velocity, reason}]",
    )

    related_projects: list[dict] = Field(
        default_factory=list,
        description="Related projects [{id, relationship_type}]",
    )

    velocity_target_points: float | None = Field(
        default=None,
        ge=0,
        description="Target velocity in story points",
    )

    committed_points: float | None = Field(
        default=None,
        ge=0,
        description="Committed story points at sprint start",
    )

    actual_points: float | None = Field(
        default=None,
        ge=0,
        description="Actual completed story points",
    )

    carried_over_points: float | None = Field(
        default=None,
        ge=0,
        description="Story points carried over from previous sprint",
    )

    definition_of_done: list[str] = Field(
        default_factory=list,
        description="Sprint-level Definition of Done checklist",
    )

    dependencies: dict = Field(
        default_factory=dict,
        description="Dependencies {inbound[], outbound[]}",
    )

    scope_changes: list[dict] = Field(
        default_factory=list,
        description="Scope changes during sprint",
    )

    risks: list[dict] = Field(
        default_factory=list,
        description="Sprint-level risks (simple form)",
    )

    ceremonies: dict = Field(
        default_factory=dict,
        description="Ceremony notes {planning_notes, standup_cadence, review_demo_link, retro_notes}",
    )

    metrics: dict = Field(
        default_factory=dict,
        description="Sprint metrics {throughput, predictability_pct, burndown_asset}",
    )

    timezone: str | None = Field(
        default=None,
        max_length=50,
        description="Timezone for sprint dates",
    )

    observability: dict = Field(
        default_factory=dict,
        description="Observability data",
    )

    @field_validator("id")
    @classmethod
    def validate_sprint_id_pattern(cls, v: str) -> str:
        """Validate sprint ID matches pattern S-[A-Za-z0-9_-]+"""
        if not re.match(r"^S-[A-Za-z0-9_-]+$", v):
            raise ValueError("Sprint ID must match pattern S-[A-Za-z0-9_-]+")
        return v


class SprintUpdateRequest(BaseSchema):
    """Schema for updating an existing sprint.

    All fields are optional for partial updates.
    """

    name: str | None = Field(default=None, min_length=1, max_length=200)
    goal: str | None = Field(default=None, min_length=1)
    cadence: SprintCadence | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: SprintStatus | None = None
    owner: str | None = Field(default=None, min_length=1, max_length=100)
    primary_project: str | None = Field(default=None, min_length=1, max_length=50)

    tasks: list[str] | None = None
    imported_tasks: list[dict] | None = None
    related_projects: list[dict] | None = None

    velocity_target_points: float | None = Field(default=None, ge=0)
    committed_points: float | None = Field(default=None, ge=0)
    actual_points: float | None = Field(default=None, ge=0)
    carried_over_points: float | None = Field(default=None, ge=0)

    definition_of_done: list[str] | None = None
    dependencies: dict | None = None
    scope_changes: list[dict] | None = None
    risks: list[dict] | None = None
    ceremonies: dict | None = None
    metrics: dict | None = None

    timezone: str | None = Field(default=None, max_length=50)
    observability: dict | None = None


class SprintResponse(TimestampSchema):
    """Schema for sprint API responses."""

    id: str
    name: str
    goal: str
    cadence: SprintCadence
    start_date: date
    end_date: date
    status: SprintStatus
    owner: str
    primary_project: str

    tasks: list[str]
    imported_tasks: list[dict]
    related_projects: list[dict]

    velocity_target_points: float | None
    committed_points: float | None
    actual_points: float | None
    carried_over_points: float | None

    definition_of_done: list[str]
    dependencies: dict
    scope_changes: list[dict]
    risks: list[dict]
    ceremonies: dict
    metrics: dict

    timezone: str | None
    observability: dict
