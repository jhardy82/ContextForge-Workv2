"""
Full Project schemas matching the 26-field database schema.
Includes OKRs, KPIs, governance, and full ContextForge integration.
"""
from datetime import date, datetime
from typing import Any

from pydantic import ConfigDict, Field, field_validator

from taskman_api.core.enums import ProjectStatus
from taskman_api.schemas.base import TaskManBaseModel, TimestampMixin


# =============================================================================
# Project Create Schema
# =============================================================================
class ProjectCreate(TaskManBaseModel):
    """Schema for creating a new project with full complexity."""

    # Core required fields
    id: str = Field(..., pattern=r"^P-[A-Za-z0-9_-]+$", description="Project ID (P-xxx format)")
    name: str = Field(..., min_length=1, max_length=200, description="Project name")
    mission: str | None = Field(None, min_length=1, description="Project mission statement")
    status: ProjectStatus = Field(ProjectStatus.NEW, description="Project status")
    start_date: date | None = Field(None, description="Project start date")
    target_end_date: date | None = Field(None, description="Target end date")

    # Ownership
    owner: str | None = Field(None, min_length=1, max_length=100, description="Project owner")
    sponsors: list[str] = Field(default_factory=list, description="Executive sponsors")
    stakeholders: list[dict[str, Any]] = Field(default_factory=list, description="Stakeholder registry")

    # Resources
    repositories: list[str] = Field(default_factory=list, description="Git repository URLs")
    comms_channels: list[dict[str, str]] = Field(default_factory=list, description="Communication channels")

    # OKRs and KPIs
    okrs: list[dict[str, Any]] = Field(default_factory=list, description="Objectives and Key Results")
    kpis: list[dict[str, Any]] = Field(default_factory=list, description="Key Performance Indicators")

    # Planning
    roadmap: list[dict[str, Any]] = Field(default_factory=list, description="Milestone roadmap")
    risks: list[dict[str, Any]] = Field(default_factory=list, description="Risk registry")
    assumptions: list[str] = Field(default_factory=list, description="Project assumptions")
    constraints: list[str] = Field(default_factory=list, description="Project constraints")
    dependencies_external: list[dict[str, Any]] = Field(default_factory=list, description="External dependencies")

    # Associations
    sprints: list[str] = Field(default_factory=list, description="Associated sprint IDs")
    related_projects: list[str] = Field(default_factory=list, description="Related project IDs")
    shared_components: list[str] = Field(default_factory=list, description="Shared component refs")

    # Security and compliance
    security_posture: str | None = Field(None, description="Security posture description")
    compliance_requirements: list[str] = Field(default_factory=list, description="Compliance requirements")

    # Governance
    governance: dict[str, Any] = Field(default_factory=dict, description="Governance configuration")
    success_metrics: list[dict[str, Any]] = Field(default_factory=list, description="Success metrics")

    # MPV and TNVE
    mpv_policy: dict[str, Any] = Field(default_factory=dict, description="MPV policy configuration")
    tnve_mandate: bool = Field(False, description="TNVE mandate flag")
    evidence_root: str | None = Field(None, max_length=500, description="Evidence root path")

    # Observability
    observability: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Project Update Schema
# =============================================================================
class ProjectUpdate(TaskManBaseModel):
    """Schema for updating a project. All fields optional."""

    name: str | None = Field(None, min_length=1, max_length=200)
    mission: str | None = None
    status: ProjectStatus | None = None
    start_date: date | None = None
    target_end_date: date | None = None
    owner: str | None = Field(None, min_length=1, max_length=100)
    sponsors: list[str] | None = None
    stakeholders: list[dict[str, Any]] | None = None
    repositories: list[str] | None = None
    comms_channels: list[dict[str, str]] | None = None
    okrs: list[dict[str, Any]] | None = None
    kpis: list[dict[str, Any]] | None = None
    roadmap: list[dict[str, Any]] | None = None
    risks: list[dict[str, Any]] | None = None
    assumptions: list[str] | None = None
    constraints: list[str] | None = None
    dependencies_external: list[dict[str, Any]] | None = None
    sprints: list[str] | None = None
    related_projects: list[str] | None = None
    shared_components: list[str] | None = None
    security_posture: str | None = None
    compliance_requirements: list[str] | None = None
    governance: dict[str, Any] | None = None
    success_metrics: list[dict[str, Any]] | None = None
    mpv_policy: dict[str, Any] | None = None
    tnve_mandate: bool | None = False
    evidence_root: str | None = None

    # Timestamps (Optionally provided by client, otherwise DB/Model should handle - but DB has no default?)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    created_utc: datetime | None = None
    updated_utc: datetime | None = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")
    observability: dict[str, Any] | None = None


# =============================================================================
# Project Response Schema
# =============================================================================
class ProjectResponse(TaskManBaseModel, TimestampMixin):
    """Full project response with all 26 fields."""

    # Core identity
    id: str = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    mission: str | None = Field(None, description="Mission statement")
    status: ProjectStatus = Field(..., description="Project status")
    start_date: date | None = Field(None, description="Start date")
    target_end_date: date | None = Field(None, description="Target end date")

    # Ownership
    owner: str | None = Field(None, description="Project owner (optional)")
    sponsors: list[str] = Field(default_factory=list)
    stakeholders: list[dict[str, Any]] = Field(default_factory=list)

    # Resources
    repositories: list[str] = Field(default_factory=list)
    comms_channels: list[dict[str, str]] = Field(default_factory=list)

    # OKRs and KPIs
    okrs: list[dict[str, Any]] = Field(default_factory=list)
    kpis: list[dict[str, Any]] = Field(default_factory=list)

    # Planning
    roadmap: list[dict[str, Any]] = Field(default_factory=list)
    risks: list[dict[str, Any]] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    dependencies_external: list[dict[str, Any]] = Field(default_factory=list)

    # Associations
    sprints: list[str] = Field(default_factory=list)
    related_projects: list[str] = Field(default_factory=list)
    shared_components: list[str] = Field(default_factory=list)

    # Security and compliance
    security_posture: str | None = Field(None)
    compliance_requirements: list[str] = Field(default_factory=list)

    # Governance
    governance: dict[str, Any] = Field(default_factory=dict)
    success_metrics: list[dict[str, Any]] = Field(default_factory=list)

    # MPV and TNVE
    mpv_policy: dict[str, Any] = Field(default_factory=dict)
    tnve_mandate: bool = Field(False)
    evidence_root: str | None = Field(None)

    # Observability
    observability: dict[str, Any] = Field(default_factory=dict)

    @field_validator("status", mode="before")
    @classmethod
    def parse_status(cls, v: str | ProjectStatus) -> ProjectStatus:
        if isinstance(v, ProjectStatus):
            return v
        return ProjectStatus(v)

    @field_validator(
        "sponsors",
        "repositories",
        "assumptions",
        "constraints",
        "sprints",
        "related_projects",
        "shared_components",
        "compliance_requirements",
        mode="before",
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

    @field_validator(
        "stakeholders",
        "comms_channels",
        "okrs",
        "kpis",
        "roadmap",
        "risks",
        "dependencies_external",
        "success_metrics",
        mode="before",
    )
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

    @field_validator("governance", "mpv_policy", "observability", mode="before")
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

    @field_validator("tnve_mandate", mode="before")
    @classmethod
    def parse_bool(cls, v: Any) -> bool:
        """Parse boolean from various types."""
        if v is None:
            return False
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return bool(v)


# =============================================================================
# Project List Response
# =============================================================================
class ProjectList(TaskManBaseModel):
    """Paginated list of projects."""

    projects: list[ProjectResponse]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    per_page: int = Field(..., ge=1, le=100)
    has_more: bool

ProjectCreateRequest = ProjectCreate
ProjectUpdateRequest = ProjectUpdate
