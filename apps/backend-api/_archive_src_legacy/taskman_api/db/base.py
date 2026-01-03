"""SQLAlchemy declarative base and shared model functionality."""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models.

    Provides common functionality:
    - Type annotations for SQLAlchemy 2.0
    - Common timestamp fields (created_at, updated_at)
    - String representation for debugging
    """

    # Disable type checking for class vars (SQLAlchemy internals)
    type_annotation_map = {
        datetime: DateTime(timezone=True),
    }

    def __repr__(self) -> str:
        """String representation for debugging."""
        attrs = []
        for column in self.__table__.columns:
            value = getattr(self, column.name, None)
            # Truncate long strings for readability
            if isinstance(value, str) and len(value) > 50:
                value = value[:47] + "..."
            attrs.append(f"{column.name}={value!r}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps.

    All models should include this mixin for audit trail.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when record was created (UTC)",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Timestamp when record was last updated (UTC)",
    )


# Import all models here to ensure they're registered with Base.metadata
# This is required for Alembic to detect all models
def import_models() -> None:
    """Import all models to register them with Base.metadata.

    Call this before running Alembic migrations or creating tables.
    """
    # Import models here to avoid circular dependencies
    from .models import action_list, project, sprint, task  # noqa: F401
