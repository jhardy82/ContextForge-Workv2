"""
Full Sprint schemas matching the 26-field database schema.
Includes velocity tracking, ceremonies, and full agile integration.
"""
from datetime import date
from typing import Any

from pydantic import Field, field_validator

from taskman_api.core.enums import SprintCadence, SprintStatus
from taskman_api.schemas.base import TaskManBaseModel, TimestampMixin


# =============================================================================
# Sprint Create Schema
# =============================================================================
class SprintCreate(TaskManBaseModel):
    """Schema for creating a new sprint with full complexity."""

    # Core required fields
    id: str = Field(..., pattern=r"^S-[A-Za-z0-9_-]+$", description="Sprint ID (S-xxx format)")
    name: str = Field(..., min_length=1, max_length=200, description="Sprint name")
    goal: str | None = Field(None, min_length=1, description="Sprint goal")
    cadence: SprintCadence = Field(SprintCadence.BIWEEKLY, description="Sprint cadence")
    start_date: date | None = Field(None, description="Sprint start date")
    end_date: date | None = Field(None, description="Sprint end date")
    status: SprintStatus = Field(SprintStatus.NEW, description="Sprint status")
    owner: str | None = Field(None, min_length=1, max_length=100, description="Sprint owner")

    # Project association (required)
    primary_project: str = Field(..., description="Primary project ID")

    # Task assignments
    tasks: list[str] = Field(default_factory=list, description="Task IDs in sprint")
    imported_tasks: list[str] = Field(default_factory=list, description="Imported task IDs")
    related_projects: list[str] = Field(default_factory=list, description="Related project IDs")

    # Capacity and velocity
    velocity_target_points: float | None = Field(None, ge=0, description="Target velocity")
    committed_points: float | None = Field(None, ge=0, description="Committed points")
    actual_points: float | None = Field(None, ge=0, description="Actual points completed")
    carried_over_points: float | None = Field(None, ge=0, description="Carried over points")

    # Definition of Done
    definition_of_done: list[str] = Field(default_factory=list, description="DoD checklist")

    # Dependencies
    dependencies: list[dict[str, Any]] = Field(default_factory=list, description="Sprint dependencies")

    # Scope and risks
    scope_changes: list[dict[str, Any]] = Field(default_factory=list, description="Scope change log")
    risks: list[dict[str, Any]] = Field(default_factory=list, description="Sprint risks")

    # Ceremonies and metrics
    ceremonies: dict[str, Any] = Field(default_factory=dict, description="Ceremony schedule")
    metrics: dict[str, Any] = Field(default_factory=dict, description="Sprint metrics")

    # Timezone
    timezone: str | None = Field(None, max_length=50, description="Sprint timezone")

    # Observability
    observability: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Sprint Update Schema
# =============================================================================
class SprintUpdate(TaskManBaseModel):
    """Schema for updating a sprint. All fields optional."""

    name: str | None = Field(None, min_length=1, max_length=200)
    goal: str | None = None
    cadence: SprintCadence | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: SprintStatus | None = None
    owner: str | None = Field(None, min_length=1, max_length=100)
    primary_project: str | None = None
    tasks: list[str] | None = None
    imported_tasks: list[str] | None = None
    related_projects: list[str] | None = None
    velocity_target_points: float | None = Field(None, ge=0)
    committed_points: float | None = Field(None, ge=0)
    actual_points: float | None = Field(None, ge=0)
    carried_over_points: float | None = Field(None, ge=0)
    definition_of_done: list[str] | None = None
    dependencies: list[dict[str, Any]] | None = None
    scope_changes: list[dict[str, Any]] | None = None
    risks: list[dict[str, Any]] | None = None
    ceremonies: dict[str, Any] | None = None
    metrics: dict[str, Any] | None = None
    timezone: str | None = None
    observability: dict[str, Any] | None = None


# =============================================================================
# Sprint Response Schema
# =============================================================================
class SprintResponse(TaskManBaseModel, TimestampMixin):
    """Full sprint response with all 26 fields."""

    # Core identity
    id: str = Field(..., description="Sprint ID")
    name: str = Field(..., description="Sprint name")
    goal: str | None = Field(None, description="Sprint goal")
    cadence: SprintCadence | None = Field(None, description="Cadence")
    start_date: date | None = Field(None, description="Start date")
    end_date: date | None = Field(None, description="End date")
    status: SprintStatus = Field(..., description="Status")
    owner: str | None = Field(None, description="Owner")

    # Project association
    primary_project: str = Field(..., description="Primary project ID")

    # Task assignments
    tasks: list[str] = Field(default_factory=list)
    imported_tasks: list[str] = Field(default_factory=list)
    related_projects: list[str] = Field(default_factory=list)

    # Velocity tracking
    velocity_target_points: float | None = Field(None)
    committed_points: float | None = Field(None)
    actual_points: float | None = Field(None)
    carried_over_points: float | None = Field(None)

    # DoD
    definition_of_done: list[str] = Field(default_factory=list)

    # Dependencies and risks
    dependencies: list[dict[str, Any]] = Field(default_factory=list)
    scope_changes: list[dict[str, Any]] = Field(default_factory=list)
    risks: list[dict[str, Any]] = Field(default_factory=list)

    # Ceremonies and metrics
    ceremonies: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)

    # Timezone
    timezone: str | None = Field(None)

    # Observability
    observability: dict[str, Any] = Field(default_factory=dict)

    @field_validator("status", mode="before")
    @classmethod
    def parse_status(cls, v: str | SprintStatus) -> SprintStatus:
        if isinstance(v, SprintStatus):
            return v
        return SprintStatus(v)

    @field_validator("cadence", mode="before")
    @classmethod
    def parse_cadence(cls, v: str | SprintCadence) -> SprintCadence:
        if isinstance(v, SprintCadence):
            return v
        return SprintCadence(v)

    @field_validator(
        "tasks", "imported_tasks", "related_projects", "definition_of_done", mode="before"
    )
    @classmethod
    def parse_json_list_str(cls, v: Any) -> list[str]:
        """Parse JSON string or return list as-is."""
        import json

        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else []
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    @field_validator("dependencies", "scope_changes", "risks", mode="before")
    @classmethod
    def parse_json_list_dict(cls, v: Any) -> list[dict[str, Any]]:
        """Parse JSON string or return list as-is."""
        import json

        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else []
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    @field_validator("ceremonies", "metrics", "observability", mode="before")
    @classmethod
    def parse_json_dict(cls, v: Any) -> dict[str, Any]:
        """Parse JSON string or return dict as-is."""
        import json

        if v is None:
            return {}
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, dict) else {}
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}


# =============================================================================
# Sprint List Response
# =============================================================================
class SprintList(TaskManBaseModel):
    """Paginated list of sprints."""

    sprints: list[SprintResponse]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    per_page: int = Field(..., ge=1, le=100)
    has_more: bool


# =============================================================================
# Sprint Progress Report
# =============================================================================
class SprintProgress(TaskManBaseModel):
    """Sprint progress summary for dashboards."""

    sprint_id: str
    name: str
    status: SprintStatus
    task_count: int = Field(..., ge=0)
    completed_count: int = Field(..., ge=0)
    completion_percentage: float = Field(..., ge=0, le=100)
    total_points: float = Field(0, ge=0)
    completed_points: float = Field(0, ge=0)
    days_remaining: int | None = None

SprintCreateRequest = SprintCreate
SprintUpdateRequest = SprintUpdate
