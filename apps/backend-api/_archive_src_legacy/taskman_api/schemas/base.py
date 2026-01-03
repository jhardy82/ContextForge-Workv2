"""Base Pydantic schemas.

Provides common configuration and mixins for all schemas.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration.

    Provides:
    - Strict type validation
    - JSON serialization support
    - ORM mode for SQLAlchemy models
    """

    model_config = ConfigDict(
        strict=False,  # Allow type coercion from JSON (e.g., "p1" string -> Priority.P1 enum)
        from_attributes=True,  # Enable ORM mode (SQLAlchemy)
        validate_assignment=True,  # Validate on attribute assignment
        use_enum_values=False,  # Keep Enum objects (don't convert to values)
        populate_by_name=True,  # Allow population by field name or alias
    )


class TimestampSchema(BaseSchema):
    """Schema mixin for created_at/updated_at timestamps.

    Use for response schemas that include timestamp fields.
    """

    created_at: datetime
    updated_at: datetime
