"""
Sprint Model - Aligned with Production Schema.

SQLAlchemy ORM model for sprints table.
Schema verified via information_schema on 2025-01-16.
Note: Production has 35+ columns; this model covers essential ones.
"""

from sqlalchemy import JSON, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from taskman_api.db.base import Base


class Sprint(Base):
    """
    Sprint entity representing a time-boxed iteration.

    Production schema (verified):
    - String ID (varchar 64)
    - Timestamps as varchar(32) in production (not DateTime)
    - Many additional fields for ceremonies, velocity, etc.
    """

    __tablename__ = "sprints"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Core fields
    name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    title: Mapped[str | None] = mapped_column(String(256), nullable=True)
    goal: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    owner: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cadence: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Parent project (varchar, no FK constraint)
    project_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    @property
    def primary_project(self) -> str | None:
        """Alias for project_id to match Pydantic schema."""
        return self.project_id

    @primary_project.setter
    def primary_project(self, value: str | None):
        self.project_id = value

    # Timing (stored as varchar in production)
    start_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    end_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    updated_at: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_utc: Mapped[str | None] = mapped_column(String(32), nullable=True)
    updated_utc: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Health tracking
    last_health: Mapped[str | None] = mapped_column(String(32), nullable=True)
    last_heartbeat_utc: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Scope and type
    scope: Mapped[str | None] = mapped_column(Text, nullable=True)
    scope_type: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Velocity metrics
    committed_points: Mapped[str | None] = mapped_column(String(32), nullable=True)
    delivered_points: Mapped[str | None] = mapped_column(String(32), nullable=True)
    velocity_target: Mapped[str | None] = mapped_column(String(32), nullable=True)
    velocity_actual: Mapped[float | None] = mapped_column(Float, nullable=True)
    predictability_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    throughput: Mapped[float | None] = mapped_column(Float, nullable=True)
    burndown_asset: Mapped[str | None] = mapped_column(String(256), nullable=True)

    # Ceremonies and notes (JSON as text)
    # Ceremonies and notes
    ceremonies: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    planning_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    standup_cadence: Mapped[str | None] = mapped_column(String(32), nullable=True)
    review_demo_link: Mapped[str | None] = mapped_column(String(256), nullable=True)
    retro_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Dependencies and relationships
    risks: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    dependencies: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    sprints: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)  # Related sprints
    related_projects: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    shared_components: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    # Observability
    observability: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    evidence_log: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Soft delete
    deleted_at: Mapped[str | None] = mapped_column(String(32), nullable=True)

    def __repr__(self) -> str:
        return f"<Sprint(id='{self.id}', name='{self.name}', status='{self.status}')>"

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "goal": self.goal,
            "status": self.status,
            "owner": self.owner,
            "cadence": self.cadence,
            "project_id": self.project_id,
            "primary_project": self.project_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "velocity_actual": self.velocity_actual,
            "committed_points": self.committed_points,
            "delivered_points": self.delivered_points,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
