"""Sprint ORM model.

Implements the tracker-sprint.schema.json specification with 30+ fields.
Agile sprint tracking with velocity, burndown, and ceremonies.
"""

from datetime import date
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from taskman_api.core.enums import SprintCadence, SprintStatus
from taskman_api.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from .project import Project
    from .task import Task


class Sprint(Base, TimestampMixin):
    """Sprint model for Agile sprint tracking.

    Follows tracker-sprint.schema.json v1.1.1 specification.
    Pattern: S-[A-Za-z0-9_-]+ (e.g., S-2025-01, S-ULOG-SPRINT-1)
    """

    __tablename__ = "sprints"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        doc="Sprint ID matching pattern S-[A-Za-z0-9_-]+",
    )

    # Core fields (required)
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Sprint name",
    )

    goal: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Sprint goal/objective",
    )

    cadence: Mapped[SprintCadence] = mapped_column(
        String(20),
        nullable=False,
        doc="Sprint cadence (weekly, biweekly, monthly, custom)",
    )

    start_date: Mapped[date] = mapped_column(
        nullable=False,
        doc="Sprint start date",
    )

    end_date: Mapped[date] = mapped_column(
        nullable=False,
        doc="Sprint end date",
    )

    status: Mapped[SprintStatus] = mapped_column(
        String(20),
        nullable=False,
        default=SprintStatus.NEW,
        doc="Sprint status (new, pending, assigned, active, in_progress, blocked, completed, cancelled)",
    )

    owner: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Sprint owner/Scrum Master",
    )

    # Project association (required)
    primary_project: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        doc="Primary project this sprint belongs to",
    )

    # Task assignments (required)
    tasks: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Task IDs assigned to this sprint",
    )

    # Imported tasks (from other sprints/projects)
    imported_tasks: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Imported tasks [{id, counts_toward_velocity, reason}]",
    )

    # Related projects
    related_projects: Mapped[list[dict[str, str]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Related projects [{id, relationship_type}]",
    )

    # Capacity and velocity
    velocity_target_points: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        doc="Target velocity in story points",
    )

    committed_points: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        doc="Committed story points at sprint start",
    )

    actual_points: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        doc="Actual completed story points",
    )

    carried_over_points: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        doc="Story points carried over from previous sprint",
    )

    # Definition of Done
    definition_of_done: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Sprint-level Definition of Done checklist",
    )

    # Dependencies
    dependencies: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        doc="Dependencies {inbound[], outbound[]}",
    )

    # Scope changes
    scope_changes: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Scope changes during sprint [{when, change, id, reason}]",
    )

    # Risks
    risks: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Sprint-level risks (simple form) [{description, impact, likelihood, mitigation}]",
    )

    # Ceremonies
    ceremonies: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        doc="Ceremony notes {planning_notes, standup_cadence, review_demo_link, retro_notes}",
    )

    # Metrics
    metrics: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        doc="Sprint metrics {throughput, predictability_pct, burndown_asset}",
    )

    # Timezone
    timezone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="Timezone for sprint dates (e.g., America/New_York)",
    )

    # Observability (required)
    observability: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        doc="Observability data {last_health, last_heartbeat_utc, evidence_log}",
    )

    # Phase tracking for Sprints (planning, implementation only)
    # Sprints organize work execution - research/testing happen at task level
    phases: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: {
            "planning": {"status": "not_started", "has_sprint_goal": False, "has_capacity_plan": False, "tasks_estimated": False},
            "implementation": {"status": "not_started", "progress_pct": 0, "tasks_completed": 0, "tasks_total": 0},
        },
        doc="Sprint lifecycle phases {planning, implementation}",
    )

    # Status reasons (for pending/blocked states)
    pending_reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        doc="Reason for pending status",
    )

    blocked_reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        doc="Reason for blocked status",
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        foreign_keys=[primary_project],
        back_populates="project_sprints",
    )

    sprint_tasks: Mapped[list["Task"]] = relationship(
        "Task",
        foreign_keys="Task.primary_sprint",
        back_populates="sprint",
        cascade="all, delete-orphan",
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_sprints_status", "status"),
        Index("idx_sprints_primary_project", "primary_project"),
        Index("idx_sprints_owner", "owner"),
        Index("idx_sprints_start_date", "start_date"),
        Index("idx_sprints_end_date", "end_date"),
        Index("idx_sprints_project_status", "primary_project", "status"),
        Index("idx_sprints_created_at", "created_at"),
        Index("idx_sprints_updated_at", "updated_at"),
    )
