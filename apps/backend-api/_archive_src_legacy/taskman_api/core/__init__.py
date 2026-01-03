"""Core infrastructure for TaskMan API.

This module contains fundamental components used throughout the application:
- Enumerations (TaskStatus, Priority, Severity, etc.)
- Error types and exception hierarchy
- Result monad for functional error handling
"""

from .enums import (
    GeometryShape,
    HealthStatus,
    Priority,
    ProjectStatus,
    Severity,
    SprintCadence,
    SprintStatus,
    TaskStatus,
    WorkType,
)
from .errors import (
    AppError,
    ConflictError,
    DatabaseError,
    NotFoundError,
    ValidationError,
)
from .result import Result

__all__ = [
    # Enums
    "TaskStatus",
    "Priority",
    "Severity",
    "ProjectStatus",
    "SprintStatus",
    "SprintCadence",
    "WorkType",
    "GeometryShape",
    "HealthStatus",
    # Errors
    "AppError",
    "NotFoundError",
    "ValidationError",
    "ConflictError",
    "DatabaseError",
    # Result monad
    "Result",
]
