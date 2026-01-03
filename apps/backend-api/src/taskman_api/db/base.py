"""
SQLAlchemy Base Model Configuration.

Declarative base for all ORM models.
Note: Timestamp columns are NOT defined here because production
schemas vary (some use DateTime, some use varchar).
Each model must define its own timestamp fields.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamps.

    Used by State Store models (Checklist, Conversation, Plan, Phase).
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        doc="Creation timestamp",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        doc="Last update timestamp",
    )


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    Provides:
    - Common table naming convention
    - to_dict() helper for serialization

    Note: Timestamp columns must be defined per-model to match
    the actual production schema.
    """

    # Type annotation map for custom types
    type_annotation_map: dict[type, Any] = {}

    def to_dict(self) -> dict[str, Any]:
        """Convert model instance to dictionary."""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
