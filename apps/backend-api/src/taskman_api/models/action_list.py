"""
ActionList Model
SQLAlchemy ORM model for action lists.
Matches the actual database schema.
Uses StringList TypeDecorator for PostgreSQL/SQLite dual-database support.
"""

import logging
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON, TypeDecorator

from taskman_api.db.base import Base

logger = logging.getLogger(__name__)


class StringList(TypeDecorator):
    """Custom type for list of strings.

    Uses PostgreSQL ARRAY in production, JSON for SQLite testing.
    This enables dual-database support without schema changes.
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Choose implementation based on dialect."""
        logger.debug(f"[DEBUG] StringList.load_dialect_impl called for dialect: {dialect.name}")
        if dialect.name == "postgresql":
            return dialect.type_descriptor(ARRAY(String(36)))
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value, _dialect):
        """Convert list to storage format."""
        if value is None:
            return []
        return list(value)

    def process_result_value(self, value, _dialect):
        """Convert from storage format to list."""
        if value is None:
            return []
        return list(value)


class ActionList(Base):
    """
    Action list entity representing a curated collection of tasks.

    TaskMan ID format: AL-XXXX (e.g., AL-0001)
    Matches actual database schema (20 fields).
    """

    __tablename__ = "action_lists"

    # Primary key
    id: Mapped[str] = mapped_column(String(50), primary_key=True)

    # Core fields (note: production uses 'title' but keeping 'name' for API compatibility)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    # Ownership & categorization
    owner: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, default=list)

    # Association fields (foreign keys to other entities)
    project_id: Mapped[str | None] = mapped_column(
        String(50), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )
    sprint_id: Mapped[str | None] = mapped_column(
        String(50), ForeignKey("sprints.id", ondelete="SET NULL"), nullable=True
    )

    # Task references (stored as array of task IDs)
    # Uses StringList for PostgreSQL/SQLite dual-database support
    task_ids: Mapped[list[str]] = mapped_column(StringList(), nullable=False, default=list)

    # Checklist items (rich structure for action items)
    items: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True, default=list)

    # ContextForge metadata fields
    geometry_shape: Mapped[str | None] = mapped_column(String(20), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(20), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    evidence_refs: Mapped[list[str] | None] = mapped_column(JSON, nullable=True, default=list)
    extra_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Soft delete tracking (parent context deletion)
    parent_deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    parent_deletion_note: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Performance indexes
    __table_args__ = (
        # GIN index for task_ids containment queries (PostgreSQL-specific)
        Index("ix_action_lists_task_ids", "task_ids", postgresql_using="gin"),
        # B-tree indexes for filtering and sorting
        Index("ix_action_lists_status", "status"),
        Index("ix_action_lists_priority", "priority"),
        Index("ix_action_lists_created_at", "created_at"),
        Index("ix_action_lists_completed_at", "completed_at"),
        Index("ix_action_lists_due_date", "due_date"),
        # Composite index for common query patterns
        Index("ix_action_lists_status_priority", "status", "priority"),
    )

    @property
    def task_count(self) -> int:
        """Return number of tasks in list."""
        return len(self.task_ids) if self.task_ids else 0

    @property
    def is_active(self) -> bool:
        """Check if list is active (for API compatibility)."""
        return self.status == "active"

    def __repr__(self) -> str:
        return f"<ActionList(id={self.id!r}, name={self.name!r}, status={self.status!r})>"
