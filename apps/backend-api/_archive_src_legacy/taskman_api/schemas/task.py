"""Task Pydantic schemas.

Request/response schemas for Task API endpoints.
"""

import re
from datetime import datetime

from pydantic import Field, field_validator

from taskman_api.core.enums import GeometryShape, Priority, Severity, TaskStatus

from .base import BaseSchema, TimestampSchema


class TaskCreateRequest(BaseSchema):
    """Schema for creating a new task.

    Validates all required fields and patterns.
    """

    id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Task ID matching pattern T-[A-Za-z0-9_-]+",
        examples=["T-ULOG-001", "T-FEAT-042"],
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Short descriptive title",
    )

    summary: str = Field(
        ...,
        min_length=1,
        description="Brief summary (1-2 sentences)",
    )

    description: str = Field(
        ...,
        min_length=1,
        description="Detailed task description",
    )

    status: TaskStatus = Field(
        default=TaskStatus.NEW,
        description="Current task status",
    )

    owner: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Task owner (primary responsible person)",
    )

    assignees: list[str] = Field(
        default_factory=list,
        description="List of assigned team members",
    )

    priority: Priority = Field(
        ...,
        description="Task priority (p0=critical, p1=high, p2=medium, p3=low)",
    )

    severity: Severity | None = Field(
        default=None,
        description="Severity for bugs/incidents (sev1-sev4)",
    )

    primary_project: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Primary project this task belongs to",
    )

    primary_sprint: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Primary sprint this task is assigned to",
    )

    related_projects: list[dict] = Field(
        default_factory=list,
        description="Additional related projects [{id, relationship_type}]",
    )

    related_sprints: list[dict] = Field(
        default_factory=list,
        description="Additional related sprints [{id, relationship_type}]",
    )

    estimate_points: float | None = Field(
        default=None,
        ge=0,
        description="Story points or effort estimate",
    )

    actual_time_hours: float | None = Field(
        default=None,
        ge=0,
        description="Actual time spent in hours",
    )

    due_at: datetime | None = Field(
        default=None,
        description="Due date/time",
    )

    parents: list[str] = Field(
        default_factory=list,
        description="Parent task IDs (for sub-tasks)",
    )

    depends_on: list[str] = Field(
        default_factory=list,
        description="Task IDs this task depends on",
    )

    blocks: list[str] = Field(
        default_factory=list,
        description="Task IDs that this task blocks",
    )

    blockers: list[dict] = Field(
        default_factory=list,
        description="Active blockers [{id, description, owner, since, eta}]",
    )

    acceptance_criteria: list[str] = Field(
        default_factory=list,
        description="List of acceptance criteria",
    )

    definition_of_done: list[str] = Field(
        default_factory=list,
        description="Definition of done checklist",
    )

    quality_gates: dict = Field(
        default_factory=dict,
        description="Quality gate results {lint, tests, security_scan, performance_check}",
    )

    verification: dict = Field(
        default_factory=dict,
        description="Verification plan and evidence {mpv_plan, mpv_evidence}",
    )

    actions_taken: list[dict] = Field(
        default_factory=list,
        description="Action history [{when, actor, action, artifacts}]",
    )

    labels: list[str] = Field(
        default_factory=list,
        description="Searchable labels/tags",
    )

    related_links: list[str] = Field(
        default_factory=list,
        description="Related URLs (PRs, docs, tickets)",
    )

    shape: GeometryShape | None = Field(
        default=None,
        description="Sacred Geometry shape",
    )

    stage: str | None = Field(
        default=None,
        max_length=50,
        description="Lifecycle stage descriptor",
    )

    work_type: str | None = Field(
        default=None,
        max_length=50,
        description="Categorical work type",
    )

    work_stream: str | None = Field(
        default=None,
        max_length=100,
        description="Higher-level thematic work stream grouping",
    )

    business_value_score: int | None = Field(
        default=None,
        ge=0,
        le=10,
        description="Relative business value (0-10)",
    )

    cost_of_delay_score: int | None = Field(
        default=None,
        ge=0,
        le=10,
        description="Relative cost of delay (0-10)",
    )

    automation_candidate: bool | None = Field(
        default=False,
        description="True if task is a candidate for automation",
    )

    cycle_time_days: float | None = Field(
        default=None,
        ge=0,
        description="Computed cycle time in days (readOnly)",
    )

    risks: list[dict] = Field(
        default_factory=list,
        description="Task-level risks [{description, impact, likelihood, mitigation}]",
    )

    observability: dict = Field(
        default_factory=dict,
        description="Observability data {last_health, last_heartbeat_utc, evidence_log}",
    )

    @field_validator("id")
    @classmethod
    def validate_task_id_pattern(cls, v: str) -> str:
        """Validate task ID matches pattern T-[A-Za-z0-9_-]+"""
        if not re.match(r"^T-[A-Za-z0-9_-]+$", v):
            raise ValueError("Task ID must match pattern T-[A-Za-z0-9_-]+")
        return v


class TaskUpdateRequest(BaseSchema):
    """Schema for updating an existing task.

    All fields are optional for partial updates.
    """

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
    )

    summary: str | None = Field(
        default=None,
        min_length=1,
    )

    description: str | None = Field(
        default=None,
        min_length=1,
    )

    status: TaskStatus | None = None
    owner: str | None = Field(default=None, min_length=1, max_length=100)
    assignees: list[str] | None = None
    priority: Priority | None = None
    severity: Severity | None = None

    primary_project: str | None = Field(default=None, min_length=1, max_length=50)
    primary_sprint: str | None = Field(default=None, min_length=1, max_length=50)

    related_projects: list[dict] | None = None
    related_sprints: list[dict] | None = None

    estimate_points: float | None = Field(default=None, ge=0)
    actual_time_hours: float | None = Field(default=None, ge=0)
    due_at: datetime | None = None

    parents: list[str] | None = None
    depends_on: list[str] | None = None
    blocks: list[str] | None = None
    blockers: list[dict] | None = None

    acceptance_criteria: list[str] | None = None
    definition_of_done: list[str] | None = None
    quality_gates: dict | None = None
    verification: dict | None = None
    actions_taken: list[dict] | None = None

    labels: list[str] | None = None
    related_links: list[str] | None = None

    shape: GeometryShape | None = None
    stage: str | None = Field(default=None, max_length=50)
    work_type: str | None = Field(default=None, max_length=50)
    work_stream: str | None = Field(default=None, max_length=100)

    business_value_score: int | None = Field(default=None, ge=0, le=10)
    cost_of_delay_score: int | None = Field(default=None, ge=0, le=10)
    automation_candidate: bool | None = None
    cycle_time_days: float | None = Field(default=None, ge=0)

    risks: list[dict] | None = None
    observability: dict | None = None


class TaskResponse(TimestampSchema):
    """Schema for task API responses.

    Includes all fields plus timestamps.
    """

    id: str
    title: str
    summary: str
    description: str
    status: TaskStatus
    owner: str
    assignees: list[str]
    priority: Priority
    severity: Severity | None

    primary_project: str
    primary_sprint: str
    related_projects: list[dict]
    related_sprints: list[dict]

    estimate_points: float | None
    actual_time_hours: float | None
    due_at: datetime | None

    parents: list[str]
    depends_on: list[str]
    blocks: list[str]
    blockers: list[dict]

    acceptance_criteria: list[str]
    definition_of_done: list[str]
    quality_gates: dict
    verification: dict
    actions_taken: list[dict]

    labels: list[str]
    related_links: list[str]

    shape: GeometryShape | None
    stage: str | None
    work_type: str | None
    work_stream: str | None

    business_value_score: int | None
    cost_of_delay_score: int | None
    automation_candidate: bool | None
    cycle_time_days: float | None

    risks: list[dict]
    observability: dict
