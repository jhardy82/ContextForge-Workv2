"""
Task Model - Full 40+ field schema aligned with tracker-task.schema.json.

SQLAlchemy ORM model for tasks table.
"""

from datetime import datetime
from typing import Any

from taskman_api.db.base import Base
from sqlalchemy import JSON, Boolean, DateTime, Float, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column


class Task(Base):
    """
    Task entity with full ContextForge integration.

    Follows tracker-task.schema.json v1.1.1 specification.
    Pattern: T-[A-Za-z0-9_-]+ (e.g., T-ULOG-001, T-FEAT-042)
    """

    __tablename__ = "tasks"

    # Primary key - String ID pattern T-xxx
    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        doc="Task ID matching pattern T-[A-Za-z0-9_-]+",
    )

    # Core fields (required)
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        doc="Short descriptive title",
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
        doc="Brief summary of the task (1-2 sentences)",
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
        doc="Detailed task description with context and requirements",
    )

    # Status and lifecycle
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="new",
        index=True,
        doc="Current task status (new, ready, in_progress, blocked, review, done, dropped)",
    )

    # Ownership and assignment
    owner: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="",
        doc="Task owner (primary responsible person)",
    )

    assignees: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="List of assigned team members",
    )

    # Priority and severity
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="p2",
        doc="Task priority (p0=critical, p1=high, p2=medium, p3=low)",
    )

    severity: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        doc="Severity for bugs/incidents (sev1-sev4)",
    )

    # Project and sprint associations (required)
    primary_project: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="",
        index=True,
        doc="Primary project this task belongs to",
    )

    primary_sprint: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="",
        index=True,
        doc="Primary sprint this task is assigned to",
    )

    # Legacy fields for backward compatibility
    project_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    sprint_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    assignee: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Multi-project/sprint associations (JSON arrays)
    related_projects: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Additional related project IDs",
    )

    related_sprints: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Additional related sprint IDs",
    )

    # Estimates and tracking
    estimate_points: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        doc="Story points or effort estimate",
    )

    actual_time_hours: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        doc="Actual time spent in hours",
    )

    # Legacy time fields
    estimated_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actual_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    story_points: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Temporal
    due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Due date/time (if applicable)",
    )

    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Dependencies and relationships
    parents: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Parent task IDs (for sub-tasks)",
    )

    depends_on: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Task IDs this task depends on",
    )

    blocks: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Task IDs that this task blocks",
    )

    blockers: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Active blockers [{id, description, owner, since, eta}]",
    )

    # Acceptance criteria and validation
    acceptance_criteria: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="List of acceptance criteria",
    )

    definition_of_done: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Definition of done checklist",
    )

    # Quality gates
    quality_gates: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        doc="Quality gate results {lint, tests, security_scan, performance_check}",
    )

    # Verification (MPV)
    verification: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        doc="Verification plan and evidence {mpv_plan, mpv_evidence}",
    )

    # Actions and audit
    actions_taken: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Action history [{when, actor, action, artifacts}]",
    )

    # Metadata
    labels: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Searchable labels/tags",
    )

    related_links: Mapped[list[dict[str, str]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Related URLs (PRs, docs, tickets)",
    )

    tags: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ContextForge integration
    shape: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        doc="Sacred Geometry shape",
    )

    stage: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="Lifecycle stage descriptor",
    )

    work_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="Categorical work type",
    )

    work_stream: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        doc="Higher-level thematic work stream grouping",
    )

    # Business metrics
    business_value_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Relative business value (0-100)",
    )

    cost_of_delay_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Relative cost of delay (0-100)",
    )

    automation_candidate: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="True if task is a candidate for automation",
    )

    cycle_time_days: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        doc="Computed cycle time in days",
    )

    # Risks
    risks: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Task-level risks [{description, impact, likelihood, mitigation}]",
    )

    # Observability (required) - health monitoring
    observability: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        doc="Observability data {last_health, last_heartbeat_utc, evidence_log}",
    )

    # Heartbeat tracking
    last_heartbeat_utc: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Indexes
    __table_args__ = (
        Index("idx_tasks_status", "status"),
        Index("idx_tasks_priority", "priority"),
        Index("idx_tasks_owner", "owner"),
        Index("idx_tasks_primary_project", "primary_project"),
        Index("idx_tasks_primary_sprint", "primary_sprint"),
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title='{self.title[:30]}...', status='{self.status}')>"
