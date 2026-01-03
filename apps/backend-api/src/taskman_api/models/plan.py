"""Plan ORM model.

Provides multi-step plan persistence with lifecycle tracking.
"""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from taskman_api.db.base import Base, TimestampMixin


class Plan(Base, TimestampMixin):
    """SQLAlchemy model for plans.

    Multi-step plans with lifecycle tracking.
    """

    __tablename__ = "plans"

    # Identity
    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
        doc="Plan ID (prefer PLAN-* prefix)",
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Plan title",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Plan description",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="draft",
        doc="Plan status: draft, approved, in_progress, completed, abandoned",
    )

    # Structure (steps stored as JSON array)
    steps: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Plan steps as JSON array",
    )

    # Context
    conversation_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        doc="Originating conversation ID",
    )

    project_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="Associated project ID",
    )

    sprint_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="Associated sprint ID",
    )

    # Metadata
    tags: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Tags for categorization",
    )

    extra_metadata: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        doc="Additional metadata",
    )

    # Lifecycle timestamps
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when plan was approved",
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when plan was completed",
    )

    __table_args__ = (
        Index("idx_plans_status", "status"),
        Index("idx_plans_conv", "conversation_id"),
        Index("idx_plans_project", "project_id"),
    )

    @property
    def is_draft(self) -> bool:
        """Check if plan is in draft status."""
        return self.status == "draft"

    @property
    def is_approved(self) -> bool:
        """Check if plan has been approved."""
        return self.status in ("approved", "in_progress", "completed")

    @property
    def is_completed(self) -> bool:
        """Check if plan is completed."""
        return self.status == "completed"

    @property
    def step_count(self) -> int:
        """Return number of steps in plan."""
        return len(self.steps) if self.steps else 0

    @property
    def completed_step_count(self) -> int:
        """Return number of completed steps."""
        if not self.steps:
            return 0
        return sum(1 for s in self.steps if s.get("status") == "completed")

    @property
    def progress_pct(self) -> float:
        """Calculate completion percentage."""
        if not self.steps:
            return 0.0
        return (self.completed_step_count / len(self.steps)) * 100

    @property
    def current_step(self) -> dict | None:
        """Get current step (first pending/in_progress)."""
        if not self.steps:
            return None
        for step in sorted(self.steps, key=lambda s: s.get("order", 0)):
            if step.get("status") in ("pending", "in_progress"):
                return step
        return None
