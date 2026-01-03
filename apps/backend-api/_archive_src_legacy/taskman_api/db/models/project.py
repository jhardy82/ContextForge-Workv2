"""Project ORM model.

Implements the tracker-project.schema.json specification with 40+ fields.
Project management entity with OKRs, roadmap, and governance.
"""

from datetime import date
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from taskman_api.core.enums import ProjectStatus
from taskman_api.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from .sprint import Sprint
    from .task import Task


class Project(Base, TimestampMixin):
    """Project model for multi-association surface.

    Follows tracker-project.schema.json v1.1.1 specification.
    Pattern: P-[A-Za-z0-9_-]+ (e.g., P-TASKMAN-V2, P-ULOG)
    """

    __tablename__ = "projects"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        doc="Project ID matching pattern P-[A-Za-z0-9_-]+",
    )

    # Core fields (required)
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        doc="Project name",
    )

    mission: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Project mission statement",
    )

    status: Mapped[ProjectStatus] = mapped_column(
        String(20),
        nullable=False,
        default=ProjectStatus.NEW,
        doc="Project status (new, pending, assigned, active, in_progress, blocked, completed, cancelled)",
    )

    start_date: Mapped[date] = mapped_column(
        nullable=False,
        doc="Project start date",
    )

    target_end_date: Mapped[date | None] = mapped_column(
        nullable=True,
        doc="Target completion date (if applicable)",
    )

    # Ownership and stakeholders
    owner: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Project owner/lead",
    )

    sponsors: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="List of project sponsors",
    )

    stakeholders: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="List of stakeholders",
    )

    # Resources and communication
    repositories: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Git repository URLs",
    )

    comms_channels: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Communication channel URLs (Slack, Teams, etc.)",
    )

    # Objectives and Key Results (OKRs)
    okrs: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="OKRs [{obj, key_results[]}]",
    )

    # Key Performance Indicators
    kpis: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="KPIs [{name, target, current}]",
    )

    # Roadmap and milestones
    roadmap: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Roadmap milestones [{milestone_id, name, target_date, status, notes}]",
    )

    # Risk management
    risks: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Project-level risks (extended form) [{id, description, likelihood, impact, owner, mitigation}]",
    )

    # Planning and constraints
    assumptions: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Project assumptions",
    )

    constraints: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Project constraints",
    )

    dependencies_external: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="External dependencies (non-task dependencies)",
    )

    # Sprint associations
    sprints: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Sprint IDs associated with this project",
    )

    # Related projects
    related_projects: Mapped[list[dict[str, str]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Related projects [{id, relationship_type, rationale}]",
    )

    # Shared components
    shared_components: Mapped[list[dict[str, str]]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Shared components [{name, description, providing_project}]",
    )

    # Security and compliance
    security_posture: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Security posture description",
    )

    compliance_requirements: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Compliance requirements (SOC2, GDPR, etc.)",
    )

    # Governance
    governance: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        doc="Governance {cadence, decision_log[{when, decision, rationale, approvers}]}",
    )

    # Success metrics
    success_metrics: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        doc="Success metrics",
    )

    # MPV (Multi-source Provenance Validation) policy
    mpv_policy: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        doc="MPV policy {required_sources, freshness_hours}",
    )

    # TNVE (Trust Nothing, Verify Everything) mandate
    tnve_mandate: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        default=False,
        doc="TNVE mandate enabled for this project",
    )

    # Evidence root directory
    evidence_root: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        doc="Root directory for evidence artifacts",
    )

    # Observability (required)
    observability: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        doc="Observability data {last_health, last_heartbeat_utc, evidence_log}",
    )

    # Phase tracking for Projects (research, planning only)
    # Projects are strategic containers - implementation/testing happen at task level
    phases: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: {
            "research": {"status": "not_started", "has_market_research": False, "has_technical_research": False, "research_adequate": False},
            "planning": {"status": "not_started", "has_prd": False, "has_architecture": False, "has_roadmap": False},
        },
        doc="Project lifecycle phases {research, planning}",
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
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        foreign_keys="Task.primary_project",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    project_sprints: Mapped[list["Sprint"]] = relationship(
        "Sprint",
        foreign_keys="Sprint.primary_project",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_projects_status", "status"),
        Index("idx_projects_owner", "owner"),
        Index("idx_projects_start_date", "start_date"),
        Index("idx_projects_created_at", "created_at"),
        Index("idx_projects_updated_at", "updated_at"),
    )
