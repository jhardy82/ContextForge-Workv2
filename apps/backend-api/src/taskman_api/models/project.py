"""
Project Model - Aligned with Production Schema.

SQLAlchemy ORM model for projects table.
Schema verified via information_schema on 2025-01-16.
Note: Production has 40+ columns; this model covers essential ones.
"""

from sqlalchemy import TIMESTAMP, Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from taskman_api.db.base import Base
from taskman_api.db.custom_types import JSONVariant


class Project(Base):
    """
    Project entity representing a collection of tasks and sprints.

    Production schema (verified):
    - String ID (varchar 64)
    - Timestamps as varchar(32) in production
    - Many additional fields for governance, OKRs, etc.
    """

    __tablename__ = "projects"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Core fields
    name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    title: Mapped[str | None] = mapped_column(String(256), nullable=True)
    mission: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)

    # Ownership
    owner: Mapped[str | None] = mapped_column(String(128), nullable=True)
    sponsors: Mapped[list[dict] | None] = mapped_column(JSONVariant, nullable=True)
    stakeholders: Mapped[list[dict] | None] = mapped_column(JSONVariant, nullable=True)

    # Timing (stored as varchar in production)
    start_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    target_end_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    actual_end_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    updated_at: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_utc: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    updated_utc: Mapped[str | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    # Health tracking
    last_health: Mapped[str | None] = mapped_column(String(32), nullable=True)
    last_heartbeat_utc: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Repositories and comms (JSON as text)
    repositories: Mapped[list[str] | None] = mapped_column(JSONVariant, nullable=True)
    comms_channels: Mapped[list[str] | None] = mapped_column(JSONVariant, nullable=True)

    # Strategy and metrics (JSON as text)
    okrs: Mapped[list[dict] | None] = mapped_column(JSONVariant, nullable=True)
    kpis: Mapped[list[dict] | None] = mapped_column(JSONVariant, nullable=True)
    roadmap: Mapped[list[dict] | None] = mapped_column(JSONVariant, nullable=True)
    success_metrics: Mapped[list[dict] | None] = mapped_column(JSONVariant, nullable=True)

    # Risks and dependencies (JSON as text)
    risks: Mapped[list[dict] | None] = mapped_column(JSONVariant, nullable=True)
    assumptions: Mapped[list[str] | None] = mapped_column(JSONVariant, nullable=True)
    constraints: Mapped[list[str] | None] = mapped_column(JSONVariant, nullable=True)
    dependencies_external: Mapped[list[str] | None] = mapped_column(JSONVariant, nullable=True)
    # Associations
    sprints: Mapped[list[str] | None] = mapped_column(JSONVariant, nullable=True)
    related_projects: Mapped[list[str] | None] = mapped_column(JSONVariant, nullable=True)
    shared_components: Mapped[list[str] | None] = mapped_column(JSONVariant, nullable=True)
    team_members: Mapped[list[str] | None] = mapped_column(JSONVariant, nullable=True)
    labels: Mapped[list[str] | None] = mapped_column(JSONVariant, nullable=True)

    # Governance and compliance (JSON as text)
    governance: Mapped[dict | None] = mapped_column(JSONVariant, nullable=True)
    security_posture: Mapped[dict | None] = mapped_column(JSONVariant, nullable=True)
    compliance_requirements: Mapped[dict | None] = mapped_column(JSONVariant, nullable=True)
    mpv_policy: Mapped[dict | None] = mapped_column(JSONVariant, nullable=True)
    tnve_mandate: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Evidence
    evidence_root: Mapped[str | None] = mapped_column(String(256), nullable=True)
    evidence_log: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Soft delete
    deleted_at: Mapped[str | None] = mapped_column(String(32), nullable=True)

    def __repr__(self) -> str:
        return f"<Project(id='{self.id}', name='{self.name}', status='{self.status}')>"

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "mission": self.mission,
            "description": self.description,
            "status": self.status,
            "owner": self.owner,
            "start_date": self.start_date,
            "target_end_date": self.target_end_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
