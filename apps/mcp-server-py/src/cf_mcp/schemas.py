from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskManBaseModel(BaseModel):
    """Base model for all TaskMan schemas."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# =============================================================================
# Task Schemas
# =============================================================================


class TaskBase(TaskManBaseModel):
    """Common fields for Task."""

    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    summary: str | None = Field(None, description="Brief summary")
    description: str | None = Field(None, description="Detailed description")

    status: str = Field("new", description="Task status (new, todo, in_progress, etc.)")
    priority: str = Field("medium", description="Priority (low, medium, high, critical, p0-p3)")
    severity: str | None = Field(None, description="Severity level")

    project_id: str | None = Field(None, description="Project ID (P-xxx)")
    sprint_id: str | None = Field(None, description="Sprint ID (S-xxx)")

    owner: str | None = Field(None, description="Owner username")
    assignee: str | None = Field(None, description="Assignee username")
    assignees: list[str] | None = Field(default_factory=list, description="List of assignees")

    tags: list[str] | None = Field(default_factory=list, description="Tags")
    labels: list[str] | None = Field(default_factory=list, description="Labels")

    story_points: int | None = Field(None, description="Story points (Fibonacci)")
    estimated_hours: float | None = Field(None, description="Estimated hours")

    due_date: datetime | None = Field(None, description="Due date")


class TaskCreate(TaskBase):
    """Schema for creating a new task."""

    id: str | None = Field(None, pattern=r"^T-[A-Za-z0-9_-]+$", description="Optional custom ID")

    # Additional creation fields
    depends_on: list[str] | None = Field(default_factory=list)
    observability: dict | None = Field(default_factory=dict)
    risks: list[dict] | None = Field(default_factory=list)
    acceptance_criteria: list[str] | None = Field(default_factory=list)


class TaskUpdate(TaskManBaseModel):
    """Schema for updating a task."""

    title: str | None = None
    summary: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    project_id: str | None = None
    sprint_id: str | None = None
    assignee: str | None = None
    assignees: list[str] | None = None
    tags: list[str] | None = None
    labels: list[str] | None = None
    story_points: int | None = None
    estimated_hours: float | None = None
    actual_hours: float | None = None
    due_date: datetime | None = None

    # Completion update
    completed_at: datetime | None = None
    blocked_reason: str | None = None


class TaskResponse(TaskBase):
    """Full task response schema."""

    id: str
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None

    # Include all other fields from model if needed for full view
    actual_hours: float | None = None
    primary_project: str | None = None
    primary_sprint: str | None = None

    observability: dict | None = None
    risks: list[dict] | None = None
    quality_gates: dict | None = None
    action_items: list[dict] | None = None
    blockers: list[dict] | None = None


class TaskList(TaskManBaseModel):
    """Response schema for list operations."""

    items: list[TaskResponse]
    total: int
    limit: int
    offset: int


# =============================================================================
# Project Schemas
# =============================================================================


class ProjectBase(TaskManBaseModel):
    """Common fields for Project."""

    name: str = Field(..., min_length=1, max_length=200, description="Project name")
    mission: str | None = Field(None, description="Mission statement")
    status: str = Field("active", description="Project status")

    owner: str | None = Field(None, description="Project owner")
    start_date: datetime | None = Field(None)
    target_date: datetime | None = Field(None)

    tags: list[str] | None = Field(default_factory=list)
    labels: list[str] | None = Field(default_factory=list)


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""

    id: str | None = Field(None, pattern=r"^P-[A-Za-z0-9_-]+$", description="Optional custom ID")

    observability: dict | None = Field(default_factory=dict)
    risks: list[dict] | None = Field(default_factory=list)
    quarter: str | None = Field(None, description="Target quarter (e.g. 2026-Q1)")


class ProjectUpdate(TaskManBaseModel):
    """Schema for updating a project."""

    name: str | None = None
    mission: str | None = None
    status: str | None = None
    owner: str | None = None
    start_date: datetime | None = None
    target_date: datetime | None = None
    completed_at: datetime | None = None
    tags: list[str] | None = None


class ProjectResponse(ProjectBase):
    """Full project response schema."""

    id: str
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None

    progress: float | None = Field(None, description="Progress percentage (0-100)")
    health: str | None = Field(None, description="Project health (green, yellow, red)")

    observability: dict | None = None
    risks: list[dict] | None = None


class ProjectList(TaskManBaseModel):
    """Response schema for listing projects."""

    items: list[ProjectResponse]
    total: int
    limit: int
    offset: int


# =============================================================================
# Sprint Schemas
# =============================================================================

from datetime import date
from enum import Enum


class SprintStatus(str, Enum):
    NEW = "new"
    PLANNING = "planning"
    ACTIVE = "active"
    REVIEW = "review"
    RETRO = "retro"
    CLOSED = "closed"


class SprintCadence(str, Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


class SprintBase(TaskManBaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    goal: str | None = None
    cadence: SprintCadence | None = None
    start_date: date | str | None = None
    end_date: date | str | None = None
    status: SprintStatus | str = SprintStatus.NEW
    owner: str | None = None

    project_id: str | None = None
    primary_project: str | None = None

    velocity_target_points: float | None = None
    committed_points: float | None = None
    actual_points: float | None = None

    ceremonies: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)
    observability: dict[str, Any] = Field(default_factory=dict)
    risks: list[dict[str, Any]] = Field(default_factory=list)
    dependencies: list[str] | list[dict[str, Any]] = Field(
        default_factory=list
    )  # Relaxed type for JSONVariant compat


class SprintCreate(SprintBase):
    id: str | None = Field(None, pattern=r"^S-[A-Za-z0-9_-]+$", description="Optional custom ID")


class SprintUpdate(TaskManBaseModel):
    name: str | None = None
    goal: str | None = None
    status: SprintStatus | str | None = None
    start_date: date | str | None = None
    end_date: date | str | None = None
    velocity_actual: float | None = None
    metrics: dict[str, Any] | None = None


class SprintResponse(SprintBase):
    id: str
    created_at: datetime | str | None = None
    updated_at: datetime | str | None = None


class SprintList(TaskManBaseModel):
    sprints: list[SprintResponse]
    total: int
    page: int
    per_page: int
    has_more: bool


# =============================================================================
# Context Schemas
# =============================================================================


class ContextBase(TaskManBaseModel):
    """Base Context model."""

    kind: str = Field(..., description="Type of context context (e.g. project, domain, person)")
    title: str = Field(..., min_length=1, max_length=255)
    summary: str | None = None
    confidence: float = 1.0

    # Dimensions
    dim_motivational: str | None = None
    dim_relational: str | None = None
    dim_temporal: str | None = None
    dim_spatial: str | None = None
    dim_resource: str | None = None
    dim_operational: str | None = None
    dim_risk: str | None = None
    dim_policy: str | None = None
    dim_knowledge: str | None = None
    dim_signal: str | None = None
    dim_outcome: str | None = None
    dim_emergent: str | None = None
    dim_cultural: str | None = None

    parent_id: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class ContextCreate(ContextBase):
    id: str | None = Field(None, pattern=r"^C-[A-Za-z0-9_-]+$")


class ContextUpdate(TaskManBaseModel):
    title: str | None = None
    summary: str | None = None
    confidence: float | None = None

    dim_motivational: str | None = None
    dim_relational: str | None = None
    dim_temporal: str | None = None
    dim_spatial: str | None = None
    dim_resource: str | None = None
    dim_operational: str | None = None
    dim_risk: str | None = None
    dim_policy: str | None = None
    dim_knowledge: str | None = None
    dim_signal: str | None = None
    dim_outcome: str | None = None
    dim_emergent: str | None = None
    dim_cultural: str | None = None

    parent_id: str | None = None
    attributes: dict[str, Any] | None = None


class ContextResponse(ContextBase):
    id: str
    created_at: datetime
    updated_at: datetime


class ContextList(TaskManBaseModel):
    contexts: list[ContextResponse]
    total: int
    page: int
    per_page: int
    has_more: bool
