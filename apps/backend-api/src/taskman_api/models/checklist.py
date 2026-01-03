"""Checklist ORM model.

Provides reusable checklist persistence with item lifecycle tracking.
"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from taskman_api.db.base import Base, TimestampMixin


class Checklist(Base, TimestampMixin):
    """SQLAlchemy model for checklists.

    Reusable checklists with item lifecycle tracking.
    """

    __tablename__ = "checklists"

    # Identity
    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
        doc="Checklist ID (prefer CL-* prefix)",
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Checklist title",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Checklist description",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        doc="Checklist status: active, completed, archived",
    )

    # Items (stored as JSON array)
    items: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Checklist items as JSON array",
    )

    # Context
    conversation_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        doc="Associated conversation ID",
    )

    plan_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        doc="Associated plan ID",
    )

    task_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="Associated task ID",
    )

    # Templates
    is_template: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="True if this is a reusable template",
    )

    template_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        doc="Source template ID if cloned",
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

    # Lifecycle
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when checklist was completed",
    )

    __table_args__ = (
        Index("idx_checklists_status", "status"),
        Index("idx_checklists_template", "is_template"),
        Index("idx_checklists_task", "task_id"),
        Index("idx_checklists_plan", "plan_id"),
    )

    @property
    def is_active(self) -> bool:
        """Check if checklist is active."""
        return self.status == "active"

    @property
    def is_completed(self) -> bool:
        """Check if checklist is completed."""
        return self.status == "completed"

    @property
    def item_count(self) -> int:
        """Return number of items in checklist."""
        return len(self.items) if self.items else 0

    @property
    def completed_item_count(self) -> int:
        """Return number of completed items."""
        if not self.items:
            return 0
        return sum(1 for i in self.items if i.get("status") == "completed")

    @property
    def pending_item_count(self) -> int:
        """Return number of pending items."""
        if not self.items:
            return 0
        return sum(1 for i in self.items if i.get("status") == "pending")

    @property
    def blocked_item_count(self) -> int:
        """Return number of blocked items."""
        if not self.items:
            return 0
        return sum(1 for i in self.items if i.get("status") == "blocked")

    @property
    def progress_pct(self) -> float:
        """Calculate completion percentage."""
        if not self.items:
            return 0.0
        return (self.completed_item_count / len(self.items)) * 100
