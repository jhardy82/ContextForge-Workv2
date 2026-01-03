"""Project Pydantic schemas.

Request/response schemas for Project API endpoints.
"""

import re
from datetime import date

from pydantic import Field, field_validator

from taskman_api.core.enums import ProjectStatus

from .base import BaseSchema, TimestampSchema


class ProjectCreateRequest(BaseSchema):
    """Schema for creating a new project."""

    id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Project ID matching pattern P-[A-Za-z0-9_-]+",
        examples=["P-TASKMAN-V2", "P-ULOG"],
    )

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Project name",
    )

    mission: str = Field(
        ...,
        min_length=1,
        description="Project mission statement",
    )

    status: ProjectStatus = Field(
        default=ProjectStatus.DISCOVERY,
        description="Project status",
    )

    start_date: date = Field(
        ...,
        description="Project start date",
    )

    target_end_date: date | None = Field(
        default=None,
        description="Target completion date",
    )

    owner: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Project owner/lead",
    )

    sponsors: list[str] = Field(
        default_factory=list,
        description="List of project sponsors",
    )

    stakeholders: list[str] = Field(
        default_factory=list,
        description="List of stakeholders",
    )

    repositories: list[str] = Field(
        default_factory=list,
        description="Git repository URLs",
    )

    comms_channels: list[str] = Field(
        default_factory=list,
        description="Communication channel URLs",
    )

    okrs: list[dict] = Field(
        default_factory=list,
        description="OKRs [{obj, key_results[]}]",
    )

    kpis: list[dict] = Field(
        default_factory=list,
        description="KPIs [{name, target, current}]",
    )

    roadmap: list[dict] = Field(
        default_factory=list,
        description="Roadmap milestones",
    )

    risks: list[dict] = Field(
        default_factory=list,
        description="Project-level risks (extended form)",
    )

    assumptions: list[str] = Field(
        default_factory=list,
        description="Project assumptions",
    )

    constraints: list[str] = Field(
        default_factory=list,
        description="Project constraints",
    )

    dependencies_external: list[str] = Field(
        default_factory=list,
        description="External dependencies",
    )

    sprints: list[str] = Field(
        default_factory=list,
        description="Sprint IDs associated with this project",
    )

    related_projects: list[dict] = Field(
        default_factory=list,
        description="Related projects [{id, relationship_type, rationale}]",
    )

    shared_components: list[dict] = Field(
        default_factory=list,
        description="Shared components [{name, description, providing_project}]",
    )

    security_posture: str | None = Field(
        default=None,
        description="Security posture description",
    )

    compliance_requirements: list[str] = Field(
        default_factory=list,
        description="Compliance requirements (SOC2, GDPR, etc.)",
    )

    governance: dict = Field(
        default_factory=dict,
        description="Governance {cadence, decision_log[]}",
    )

    success_metrics: list[str] = Field(
        default_factory=list,
        description="Success metrics",
    )

    mpv_policy: dict = Field(
        default_factory=dict,
        description="MPV policy {required_sources, freshness_hours}",
    )

    tnve_mandate: bool | None = Field(
        default=False,
        description="TNVE mandate enabled",
    )

    evidence_root: str | None = Field(
        default=None,
        max_length=500,
        description="Root directory for evidence artifacts",
    )

    observability: dict = Field(
        default_factory=dict,
        description="Observability data",
    )

    @field_validator("id")
    @classmethod
    def validate_project_id_pattern(cls, v: str) -> str:
        """Validate project ID matches pattern P-[A-Za-z0-9_-]+"""
        if not re.match(r"^P-[A-Za-z0-9_-]+$", v):
            raise ValueError("Project ID must match pattern P-[A-Za-z0-9_-]+")
        return v


class ProjectUpdateRequest(BaseSchema):
    """Schema for updating an existing project.

    All fields are optional for partial updates.
    """

    name: str | None = Field(default=None, min_length=1, max_length=200)
    mission: str | None = Field(default=None, min_length=1)
    status: ProjectStatus | None = None
    start_date: date | None = None
    target_end_date: date | None = None
    owner: str | None = Field(default=None, min_length=1, max_length=100)

    sponsors: list[str] | None = None
    stakeholders: list[str] | None = None
    repositories: list[str] | None = None
    comms_channels: list[str] | None = None

    okrs: list[dict] | None = None
    kpis: list[dict] | None = None
    roadmap: list[dict] | None = None
    risks: list[dict] | None = None

    assumptions: list[str] | None = None
    constraints: list[str] | None = None
    dependencies_external: list[str] | None = None
    sprints: list[str] | None = None

    related_projects: list[dict] | None = None
    shared_components: list[dict] | None = None

    security_posture: str | None = None
    compliance_requirements: list[str] | None = None
    governance: dict | None = None
    success_metrics: list[str] | None = None

    mpv_policy: dict | None = None
    tnve_mandate: bool | None = None
    evidence_root: str | None = Field(default=None, max_length=500)
    observability: dict | None = None


class ProjectResponse(TimestampSchema):
    """Schema for project API responses."""

    id: str
    name: str
    mission: str
    status: ProjectStatus
    start_date: date
    target_end_date: date | None
    owner: str

    sponsors: list[str]
    stakeholders: list[str]
    repositories: list[str]
    comms_channels: list[str]

    okrs: list[dict]
    kpis: list[dict]
    roadmap: list[dict]
    risks: list[dict]

    assumptions: list[str]
    constraints: list[str]
    dependencies_external: list[str]
    sprints: list[str]

    related_projects: list[dict]
    shared_components: list[dict]

    security_posture: str | None
    compliance_requirements: list[str]
    governance: dict
    success_metrics: list[str]

    mpv_policy: dict
    tnve_mandate: bool | None
    evidence_root: str | None
    observability: dict
