"""
Base schemas and mixins for TaskMan-v2 Pydantic models.
Provides reusable components for timestamps, observability, and ownership.
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at fields."""

    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def parse_datetime(cls, v: datetime | str | None) -> datetime | None:
        """Parse datetime from string or datetime object."""
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            # Handle ISO format strings
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v


class ObservabilityMixin(BaseModel):
    """Mixin for observability/health tracking fields."""

    observability: dict[str, Any] = Field(
        default_factory=dict,
        description="Observability data: last_health, last_heartbeat_utc, evidence_log"
    )


class OwnershipMixin(BaseModel):
    """Mixin for owner and assignees fields."""

    owner: str = Field(..., min_length=1, max_length=100, description="Primary owner")
    assignees: list[str] = Field(default_factory=list, description="List of assignees")


class ProjectSprintAssociationMixin(BaseModel):
    """Mixin for project and sprint associations."""

    primary_project: str = Field(..., description="Primary project ID (P-xxx format)")
    primary_sprint: str = Field(..., description="Primary sprint ID (S-xxx format)")
    related_projects: list[str] = Field(default_factory=list, description="Related project IDs")
    related_sprints: list[str] = Field(default_factory=list, description="Related sprint IDs")


class DependencyMixin(BaseModel):
    """Mixin for task dependency fields."""

    parents: list[str] = Field(default_factory=list, description="Parent task IDs")
    depends_on: list[str] = Field(default_factory=list, description="Upstream dependencies")
    blocks: list[str] = Field(default_factory=list, description="Tasks this blocks")
    blockers: list[str] = Field(default_factory=list, description="Active blocking issues")


class QualityMixin(BaseModel):
    """Mixin for quality and validation fields."""

    acceptance_criteria: list[dict[str, Any]] = Field(
        default_factory=list, description="Acceptance criteria checklist"
    )
    definition_of_done: list[str] = Field(
        default_factory=list, description="Definition of done checklist"
    )
    quality_gates: dict[str, Any] = Field(
        default_factory=dict, description="Quality gate configurations"
    )
    verification: dict[str, Any] = Field(
        default_factory=dict, description="MPV verification data"
    )


class MetadataMixin(BaseModel):
    """Mixin for labels and links."""

    labels: list[str] = Field(default_factory=list, description="Tags/labels")
    related_links: list[dict[str, str]] = Field(
        default_factory=list, description="External links (title, url)"
    )


class ContextForgeMixin(BaseModel):
    """Mixin for ContextForge integration fields."""

    shape: str | None = Field(None, description="Geometry shape: triangle, square, etc.")
    stage: str | None = Field(None, description="Development stage")
    work_type: str | None = Field(None, description="Work classification")
    work_stream: str | None = Field(None, max_length=100, description="Work stream name")


class BusinessMetricsMixin(BaseModel):
    """Mixin for business value tracking."""

    business_value_score: int | None = Field(None, ge=0, le=100, description="Business value 0-100")
    cost_of_delay_score: int | None = Field(None, ge=0, le=100, description="Cost of delay 0-100")
    automation_candidate: bool = Field(False, description="Flag for automation potential")
    cycle_time_days: float | None = Field(None, ge=0, description="Cycle time in days")


class RiskMixin(BaseModel):
    """Mixin for risk tracking."""

    risks: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Risk items with probability, impact, mitigation"
    )


# Base configuration for all schemas
class TaskManBaseModel(BaseModel):
    """Base model with common configuration for all TaskMan schemas."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


# Aliases for State Store compatibility
BaseSchema = TaskManBaseModel
TimestampSchema = TimestampMixin
