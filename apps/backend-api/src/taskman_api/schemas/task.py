"""
Full Task schemas matching the 40+ field database schema.
All fields from the Alembic migration are represented.
"""
from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from taskman_api.core.enums import Priority as TaskPriority
from taskman_api.core.enums import Severity as TaskSeverity
from taskman_api.core.enums import TaskStatus
from taskman_api.schemas.base import TaskManBaseModel, TimestampMixin


# =============================================================================
# Task Create Schema
# =============================================================================
class TaskCreate(TaskManBaseModel):
    """
    Schema for creating a new task.
    Includes all required fields from database schema.
    """

    # Core required fields
    id: str = Field(..., pattern=r"^T-[A-Za-z0-9_-]+$", description="Task ID (T-xxx format)")
    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    summary: str = Field(..., min_length=1, description="Brief task summary")
    description: str | None = Field(None, min_length=1, description="Detailed description")

    # Status and lifecycle
    status: TaskStatus = Field(TaskStatus.NEW, description="Task status")

    # Ownership
    owner: str = Field(..., min_length=1, max_length=100, description="Primary owner")
    assignees: list[str] = Field(default_factory=list, description="Assignees")

    # Priority and severity
    priority: TaskPriority = Field(TaskPriority.P2, description="Priority level")
    severity: TaskSeverity | None = Field(None, description="Severity (for bugs)")

    # Project and sprint associations (required)
    primary_project: str = Field(..., description="Primary project ID")
    primary_sprint: str | None = Field(
        default=None, description="Primary sprint ID (optional for backlog)"
    )
    related_projects: list[str] = Field(default_factory=list)
    related_sprints: list[str] = Field(default_factory=list)

    # Estimates
    estimate_points: float | None = Field(None, ge=0, le=21, description="Story points")
    actual_time_hours: float | None = Field(None, ge=0, description="Actual hours spent")
    due_at: datetime | None = Field(None, description="Due date")

    # Dependencies
    parents: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    blocks: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)

    # Quality
    acceptance_criteria: list[dict[str, Any]] = Field(default_factory=list)
    definition_of_done: list[str] = Field(default_factory=list)
    quality_gates: dict[str, Any] = Field(default_factory=dict)
    verification: dict[str, Any] = Field(default_factory=dict)

    # Actions and audit
    actions_taken: list[dict[str, Any]] = Field(default_factory=list)

    # Metadata
    labels: list[str] = Field(default_factory=list)
    related_links: list[dict[str, str]] = Field(default_factory=list)

    # ContextForge integration
    shape: str | None = Field(None, description="Geometry shape")
    stage: str | None = Field(None, description="Development stage")
    work_type: str | None = Field(None, description="Work type classification")
    work_stream: str | None = Field(None, max_length=100)

    # Business metrics
    business_value_score: int | None = Field(None, ge=0, le=100)
    cost_of_delay_score: int | None = Field(None, ge=0, le=100)
    automation_candidate: bool = Field(False)
    cycle_time_days: float | None = Field(None, ge=0)

    # Risks
    risks: list[dict[str, Any]] = Field(default_factory=list)

    # Observability (required JSON)
    observability: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Task Update Schema (all fields optional)
# =============================================================================
class TaskUpdate(TaskManBaseModel):
    """Schema for updating an existing task. All fields optional."""

    title: str | None = Field(None, min_length=1, max_length=500)
    summary: str | None = Field(None, min_length=1)
    description: str | None = None
    status: TaskStatus | None = None
    owner: str | None = Field(None, min_length=1, max_length=100)
    assignees: list[str] | None = None
    priority: TaskPriority | None = None
    severity: TaskSeverity | None = None
    primary_project: str | None = None
    primary_sprint: str | None = None
    related_projects: list[str] | None = None
    related_sprints: list[str] | None = None
    estimate_points: float | None = Field(None, ge=0, le=21)
    actual_time_hours: float | None = Field(None, ge=0)
    due_at: datetime | None = None
    parents: list[str] | None = None
    depends_on: list[str] | None = None
    blocks: list[str] | None = None
    blockers: list[str] | None = None
    acceptance_criteria: list[dict[str, Any]] | None = None
    definition_of_done: list[str] | None = None
    quality_gates: dict[str, Any] | None = None
    verification: dict[str, Any] | None = None
    actions_taken: list[dict[str, Any]] | None = None
    labels: list[str] | None = None
    related_links: list[dict[str, str]] | None = None
    shape: str | None = None
    stage: str | None = None
    work_type: str | None = None
    work_stream: str | None = None
    business_value_score: int | None = Field(None, ge=0, le=100)
    cost_of_delay_score: int | None = Field(None, ge=0, le=100)
    automation_candidate: bool | None = None
    cycle_time_days: float | None = Field(None, ge=0)
    risks: list[dict[str, Any]] | None = None
    observability: dict[str, Any] | None = None


# =============================================================================
# Task Response Schema (full representation)
# =============================================================================
class TaskResponse(
    TaskManBaseModel,
    TimestampMixin,
):
    """
    Full task response with all 40+ fields.
    Matches database schema exactly.
    """

    # Core identity
    id: str = Field(..., description="Task ID (T-xxx format)")
    title: str = Field(..., description="Task title")
    summary: str = Field(..., description="Brief summary")
    description: str = Field(..., description="Detailed description")

    # Status and lifecycle
    status: TaskStatus = Field(..., description="Current status")

    # Ownership
    owner: str = Field(..., description="Primary owner")
    assignees: list[str] = Field(default_factory=list, description="Assignees")

    # Priority and severity
    priority: TaskPriority = Field(..., description="Priority level")
    severity: TaskSeverity | None = Field(None, description="Severity")

    # Project and sprint associations
    primary_project: str = Field(..., description="Primary project ID")
    primary_sprint: str | None = Field(None, description="Primary sprint ID")
    related_projects: list[str] = Field(default_factory=list)
    related_sprints: list[str] = Field(default_factory=list)

    # Estimates and tracking
    estimate_points: float | None = Field(None, description="Story points")
    actual_time_hours: float | None = Field(None, description="Actual hours")
    due_at: datetime | None = Field(None, description="Due date")

    # Dependencies
    parents: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    blocks: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)

    # Quality and validation
    acceptance_criteria: list[dict[str, Any]] = Field(default_factory=list)
    definition_of_done: list[str] = Field(default_factory=list)
    quality_gates: dict[str, Any] = Field(default_factory=dict)
    verification: dict[str, Any] = Field(default_factory=dict)

    # Actions and audit
    actions_taken: list[dict[str, Any]] = Field(default_factory=list)

    # Metadata
    labels: list[str] = Field(default_factory=list)
    related_links: list[dict[str, str]] = Field(default_factory=list)

    # ContextForge integration
    shape: str | None = Field(None)
    stage: str | None = Field(None)
    work_type: str | None = Field(None)
    work_stream: str | None = Field(None)

    # Business metrics
    business_value_score: int | None = Field(None)
    cost_of_delay_score: int | None = Field(None)
    automation_candidate: bool = Field(False)
    cycle_time_days: float | None = Field(None)

    # Risks
    risks: list[dict[str, Any]] = Field(default_factory=list)

    # Observability
    observability: dict[str, Any] = Field(default_factory=dict)

    @field_validator("status", mode="before")
    @classmethod
    def parse_status(cls, v: str | TaskStatus) -> TaskStatus:
        """Parse status from string or enum."""
        if isinstance(v, TaskStatus):
            return v
        if isinstance(v, str):
            try:
                return TaskStatus(v.lower())
            except ValueError:
                # Fallback or let it raise
                pass
        return TaskStatus(v)

    @field_validator("priority", mode="before")
    @classmethod
    def parse_priority(cls, v: str | TaskPriority) -> TaskPriority:
        """Parse priority from string or enum."""
        if isinstance(v, TaskPriority):
            return v
        if isinstance(v, str):
            v_lower = v.lower()
            # Map legacy values
            if v_lower == "medium":
                return TaskPriority.P2
            if v_lower == "high":
                return TaskPriority.P1
            if v_lower == "low":
                return TaskPriority.P3
            if v_lower == "critical":
                return TaskPriority.P0
            try:
                return TaskPriority(v_lower)
            except ValueError:
                pass
        return TaskPriority(v)

    @field_validator(
        "parents", "depends_on", "blocks", "blockers", "definition_of_done", "labels", mode="before"
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
        "acceptance_criteria", "actions_taken", "related_links", "risks", mode="before"
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

    @field_validator("quality_gates", "verification", "observability", mode="before")
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

    @field_validator("automation_candidate", mode="before")
    @classmethod
    def parse_bool(cls, v: Any) -> bool:
        """Parse boolean from various types including None."""
        if v is None:
            return False
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return bool(v)


# =============================================================================
# Task List Response (paginated)
# =============================================================================
class TaskList(TaskManBaseModel):
    """Paginated list of tasks."""

    tasks: list[TaskResponse]
    total: int = Field(..., ge=0, description="Total number of tasks")
    page: int = Field(..., ge=1, description="Current page")
    per_page: int = Field(..., ge=1, le=100, description="Items per page")
    has_more: bool = Field(..., description="More pages available")

TaskCreateRequest = TaskCreate
TaskUpdateRequest = TaskUpdate
