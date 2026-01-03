"""ActionList ORM model.

Matches the ACTUAL database schema with 7 columns.
Lightweight task containers with JSON task_ids array.
Uses JSON type for SQLite/PostgreSQL compatibility in tests.
"""

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON, TypeDecorator


class StringList(TypeDecorator):
    """Custom type for list of strings.

    Uses PostgreSQL ARRAY in production, JSON for SQLite testing.
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Choose implementation based on dialect."""
        if dialect.name == "postgresql":
            return dialect.type_descriptor(ARRAY(String(36)))
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value, dialect):
        """Convert list to storage format."""
        if value is None:
            return []
        return list(value)

    def process_result_value(self, value, dialect):
        """Convert from storage format to list."""
        if value is None:
            return []
        return list(value)


from taskman_api.db.base import Base, TimestampMixin


class ActionList(Base, TimestampMixin):
    """ActionList model for lightweight task containers.

    Matches ACTUAL database schema (7 columns):
    - id, name, description, status, task_ids, created_at, updated_at
    """

    __tablename__ = "action_lists"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        doc="Action list ID (UUID format)",
    )

    # Core fields (matching actual DB)
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Action list name",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Detailed description",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
        doc="Action list status",
    )

    # Task references (stored as array of task IDs)
    # Uses StringList for PostgreSQL/SQLite compatibility
    task_ids: Mapped[list[str]] = mapped_column(
        StringList(),
        nullable=False,
        default=list,
        doc="Task IDs in this list",
    )

    @property
    def task_count(self) -> int:
        """Return number of tasks in list."""
        return len(self.task_ids) if self.task_ids else 0

    @property
    def is_active(self) -> bool:
        """Check if action list is active."""
        return self.status == "active"
