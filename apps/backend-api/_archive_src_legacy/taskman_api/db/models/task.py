"""Task ORM model.

Implements the tracker-task.schema.json specification with 70+ fields.
Primary entity for task management with full ContextForge integration.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from taskman_api.core.enums import (
    GeometryShape,
    Priority,
    Severity,
    TaskStatus,
)
from taskman_api.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from .project import Project
    from .sprint import Sprint


class Task(Base, TimestampMixin):
    """Task model with full ContextForge integration.

    Follows tracker-task.schema.json v1.1.1 specification.
    Pattern: T-[A-Za-z0-9_-]+ (e.g., T-ULOG-001, T-FEAT-042)
    """

    __tablename__ = "tasks"

    # Primary key and identifiers
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
        doc="Brief summary of the task (1-2 sentences)",
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Detailed task description with context and requirements",
    )

    # Status and lifecycle
    status: Mapped[TaskStatus] = mapped_column(
        String(20),
        nullable=False,
        default=TaskStatus.NEW,
        doc="Current task status (new, ready, in_progress, blocked, review, done, dropped)",
    )

    # Ownership and assignment
    owner: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Task owner (primary responsible person)",
    )

    assignees: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="List of assigned team members",
    )

    # Priority and severity
    priority: Mapped[Priority] = mapped_column(
        String(20),
        nullable=False,
        doc="Task priority (p0=critical, p1=high, p2=medium, p3=low)",
    )

    severity: Mapped[Severity | None] = mapped_column(
        String(20),
        nullable=True,
        doc="Severity for bugs/incidents (sev1-sev4)",
    )

    # Project and sprint associations (required)
    primary_project: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        doc="Primary project this task belongs to",
    )

    primary_sprint: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("sprints.id", ondelete="CASCADE"),
        nullable=False,
        doc="Primary sprint this task is assigned to",
    )

    # Multi-project/sprint associations (JSON arrays)
    related_projects: Mapped[list[dict[str, str]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Additional related projects [{id, relationship_type}]",
    )

    related_sprints: Mapped[list[dict[str, str]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Additional related sprints [{id, relationship_type}]",
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

    # Temporal
    due_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
        doc="Due date/time (if applicable)",
    )

    # Dependencies and relationships
    parents: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Parent task IDs (for sub-tasks)",
    )

    depends_on: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Task IDs this task depends on",
    )

    blocks: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Task IDs that this task blocks",
    )

    blockers: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Active blockers [{id, description, owner, since, eta}]",
    )

    # Acceptance criteria and validation
    acceptance_criteria: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="List of acceptance criteria",
    )

    definition_of_done: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Definition of done checklist",
    )

    # Quality gates
    quality_gates: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        doc="Quality gate results {lint, tests, security_scan, performance_check}",
    )

    # Verification (MPV - Multi-source Provenance Validation)
    verification: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        doc="Verification plan and evidence {mpv_plan, mpv_evidence}",
    )

    # Actions and audit
    actions_taken: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Action history [{when, actor, action, artifacts}]",
    )

    # Metadata
    labels: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Searchable labels/tags",
    )

    related_links: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Related URLs (PRs, docs, tickets)",
    )

    # ContextForge integration
    shape: Mapped[GeometryShape | None] = mapped_column(
        String(20),
        nullable=True,
        doc="Sacred Geometry shape (Triangle, Circle, Spiral, Pentagon, Dodecahedron, Fractal)",
    )

    stage: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="Lifecycle stage descriptor",
    )

    work_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="Categorical work type (feature, refactor, governance, migration, etc.)",
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
        doc="Relative business value (0-10)",
    )

    cost_of_delay_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Relative cost of delay (0-10)",
    )

    automation_candidate: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        default=False,
        doc="True if task is a candidate for automation",
    )

    cycle_time_days: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        doc="Computed cycle time in days (readOnly)",
    )

    # Risks
    risks: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Task-level risks (simple form) [{description, impact, likelihood, mitigation}]",
    )

    # Observability (required) - health monitoring
    observability: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        doc="Observability data {last_health, last_heartbeat_utc, evidence_log}",
    )

    # Phase tracking (research, planning, implementation, testing)
    # Aligned with cf_core/models/phase_tracking.py PhaseTracking model
    phases: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: {
            "research": {"status": "not_started", "has_research": False, "research_adequate": False},
            "planning": {"status": "not_started", "has_acceptance_criteria": False, "has_definition_of_done": False},
            "implementation": {"status": "not_started", "progress_pct": 0, "has_code_changes": False},
            "testing": {"status": "not_started", "has_unit_tests": False, "tests_passing": False},
        },
        doc="Lifecycle phase tracking {research, planning, implementation, testing}",
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        foreign_keys=[primary_project],
        back_populates="tasks",
    )

    sprint: Mapped["Sprint"] = relationship(
        "Sprint",
        foreign_keys=[primary_sprint],
        back_populates="sprint_tasks",
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_tasks_status", "status"),
        Index("idx_tasks_priority", "priority"),
        Index("idx_tasks_owner", "owner"),
        Index("idx_tasks_primary_project", "primary_project"),
        Index("idx_tasks_primary_sprint", "primary_sprint"),
        Index("idx_tasks_status_priority", "status", "priority"),
        Index("idx_tasks_project_status", "primary_project", "status"),
        Index("idx_tasks_sprint_status", "primary_sprint", "status"),
        Index("idx_tasks_created_at", "created_at"),
        Index("idx_tasks_updated_at", "updated_at"),
    )
