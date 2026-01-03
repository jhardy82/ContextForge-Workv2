from datetime import datetime
from typing import Any, List, Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import JSON, TypeDecorator

# =============================================================================
# Base & Custom Types
# =============================================================================


class Base(DeclarativeBase):
    pass


class JSONVariant(TypeDecorator):
    """
    Type decorator to handle JSON consistently across PostgreSQL (JSONB)
    and SQLite (JSON).
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(JSON())


# =============================================================================
# Models
# =============================================================================


class Task(Base):
    """
    Task model representing a unit of work.
    Maps to 'tasks' table.
    """

    __tablename__ = "tasks"

    # Core Identity
    id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        default=lambda: f"T-{uuid4().hex[:8].upper()}",
        doc="Task ID (T-xxx)",
    )
    title: Mapped[str] = mapped_column(String(500), index=True)
    summary: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)

    # Status & Workflow
    status: Mapped[str] = mapped_column(String(50), default="new", index=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    severity: Mapped[str | None] = mapped_column(String(20))

    # Work Classification
    work_type: Mapped[str | None] = mapped_column(String(50))
    work_stream: Mapped[str | None] = mapped_column(String(100))
    stage: Mapped[str | None] = mapped_column(String(50))
    shape: Mapped[str | None] = mapped_column(String(50))

    # Ownership & Relationships
    owner: Mapped[str | None] = mapped_column(String(100), index=True)
    assignee: Mapped[str | None] = mapped_column(String(100), index=True)
    assignees: Mapped[list[str] | None] = mapped_column(JSONVariant, default=list)

    project_id: Mapped[str | None] = mapped_column(String(50), index=True)
    sprint_id: Mapped[str | None] = mapped_column(String(50), index=True)

    primary_project: Mapped[str | None] = mapped_column(String(50))
    primary_sprint: Mapped[str | None] = mapped_column(String(50))

    # Relationships (JSON references)
    parents: Mapped[list[str] | None] = mapped_column(JSONVariant, default=list)
    depends_on: Mapped[list[str] | None] = mapped_column(JSONVariant, default=list)
    blocks: Mapped[list[str] | None] = mapped_column(JSONVariant, default=list)
    related_projects: Mapped[list[dict] | None] = mapped_column(JSONVariant, default=list)
    related_sprints: Mapped[list[dict] | None] = mapped_column(JSONVariant, default=list)
    related_links: Mapped[list[dict] | None] = mapped_column(JSONVariant, default=list)

    # Estimates & Time
    estimate_points: Mapped[float | None] = mapped_column(Float)
    story_points: Mapped[int | None] = mapped_column(Integer)
    estimated_hours: Mapped[float | None] = mapped_column(Float)
    actual_hours: Mapped[float | None] = mapped_column(Float)
    actual_time_hours: Mapped[float | None] = mapped_column(Float)

    # Dates
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_heartbeat_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Quality & Compliance
    acceptance_criteria: Mapped[list[str] | None] = mapped_column(JSONVariant, default=list)
    definition_of_done: Mapped[list[str] | None] = mapped_column(JSONVariant, default=list)
    quality_gates: Mapped[dict | None] = mapped_column(JSONVariant, default=dict)
    verification: Mapped[dict | None] = mapped_column(JSONVariant, default=dict)
    risks: Mapped[list[dict] | None] = mapped_column(JSONVariant, default=list)

    # Blockers & Actions
    blockers: Mapped[list[dict] | None] = mapped_column(JSONVariant, default=list)
    blocked_reason: Mapped[str | None] = mapped_column(Text)
    actions_taken: Mapped[list[dict] | None] = mapped_column(JSONVariant, default=list)
    action_items: Mapped[list[dict] | None] = mapped_column(JSONVariant, default=list)

    # Metadata & Tags
    tags: Mapped[list[str] | None] = mapped_column(JSONVariant, default=list)
    labels: Mapped[list[str] | None] = mapped_column(JSONVariant, default=list)
    observability: Mapped[dict | None] = mapped_column(JSONVariant, default=dict)

    # Metrics
    business_value_score: Mapped[int | None] = mapped_column(Integer)
    cost_of_delay_score: Mapped[int | None] = mapped_column(Integer)
    automation_candidate: Mapped[bool | None] = mapped_column(Boolean, default=False)
    cycle_time_days: Mapped[float | None] = mapped_column(Float)

    # Indexes
    __table_args__ = (Index("ix_tasks_title_desc", "title", "description"),)

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"


class Project(Base):
    """
    Project model.
    Maps to 'projects' table.
    """

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: f"P-{uuid4().hex[:8].upper()}"
    )
    name: Mapped[str] = mapped_column(String(200), index=True)
    mission: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="active", index=True)

    owner: Mapped[str | None] = mapped_column(String(100), index=True)

    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    target_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # JSON Fields
    tags: Mapped[list[str] | None] = mapped_column(JSONVariant, default=list)
    labels: Mapped[list[str] | None] = mapped_column(JSONVariant, default=list)
    observability: Mapped[dict | None] = mapped_column(JSONVariant, default=dict)
    risks: Mapped[list[dict] | None] = mapped_column(JSONVariant, default=list)
    metrics: Mapped[dict | None] = mapped_column(JSONVariant, default=dict)
    governance: Mapped[dict | None] = mapped_column(JSONVariant, default=dict)

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, status={self.status})>"


class Sprint(Base):
    """
    Sprint model.
    Maps to 'sprints' table.
    """

    __tablename__ = "sprints"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    title: Mapped[str | None] = mapped_column(String(256), nullable=True)
    goal: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    owner: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cadence: Mapped[str | None] = mapped_column(String(32), nullable=True)

    project_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    # Timing
    start_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    end_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    updated_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_utc: Mapped[str | None] = mapped_column(String(32), nullable=True)
    updated_utc: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Health & Metrics
    velocity_target: Mapped[str | None] = mapped_column(String(32), nullable=True)
    velocity_actual: Mapped[float | None] = mapped_column(Float, nullable=True)
    committed_points: Mapped[str | None] = mapped_column(String(32), nullable=True)
    delivered_points: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # JSON Fields
    ceremonies: Mapped[dict | None] = mapped_column(JSONVariant, default=lambda: {})
    metrics: Mapped[dict | None] = mapped_column(JSONVariant, default=lambda: {})
    observability: Mapped[dict | None] = mapped_column(JSONVariant, default=lambda: {})
    risks: Mapped[list[dict] | None] = mapped_column(JSONVariant, default=lambda: [])
    dependencies: Mapped[list[str] | None] = mapped_column(JSONVariant, default=lambda: [])
    sprints: Mapped[list[str] | None] = mapped_column(JSONVariant, default=lambda: [])
    related_projects: Mapped[list[str] | None] = mapped_column(JSONVariant, default=lambda: [])

    def __repr__(self) -> str:
        return f"<Sprint(id={self.id}, name={self.name}, status={self.status})>"


class Context(Base):
    """
    Context model (Knowledge Graph Node).
    Maps to 'contexts' table.
    """

    __tablename__ = "contexts"

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: f"C-{uuid4().hex[:8].upper()}"
    )
    kind: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)

    # Dimensions
    dim_motivational: Mapped[str | None] = mapped_column(Text)
    dim_relational: Mapped[str | None] = mapped_column(Text)
    dim_temporal: Mapped[str | None] = mapped_column(Text)
    dim_spatial: Mapped[str | None] = mapped_column(Text)
    dim_resource: Mapped[str | None] = mapped_column(Text)
    dim_operational: Mapped[str | None] = mapped_column(Text)
    dim_risk: Mapped[str | None] = mapped_column(Text)
    dim_policy: Mapped[str | None] = mapped_column(Text)
    dim_knowledge: Mapped[str | None] = mapped_column(Text)
    dim_signal: Mapped[str | None] = mapped_column(Text)
    dim_outcome: Mapped[str | None] = mapped_column(Text)
    dim_emergent: Mapped[str | None] = mapped_column(Text)
    dim_cultural: Mapped[str | None] = mapped_column(Text)

    # Relationships
    parent_id: Mapped[str | None] = mapped_column(String(50), ForeignKey("contexts.id"), index=True)
    children: Mapped[list["Context"]] = relationship("Context")

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    attributes: Mapped[dict | None] = mapped_column(JSONVariant, default=dict)

    def __repr__(self) -> str:
        return f"<Context(id={self.id}, title={self.title}, kind={self.kind})>"
