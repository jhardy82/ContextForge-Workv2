"""
CF Core Repositories Package

Repository pattern implementations for data persistence with SQLite backend.
Provides abstract interfaces and concrete implementations following DDD principles.
"""

from cf_core.repositories.project_repository import (
    IProjectRepository,
    SqliteProjectRepository,
)
from cf_core.repositories.sprint_repository import (
    ISprintRepository,
    SqliteSprintRepository,
)
from cf_core.repositories.task_repository import (
    ITaskRepository,
    SqliteTaskRepository,
)

__all__ = [
    "ISprintRepository",
    "SqliteSprintRepository",
    "ITaskRepository",
    "SqliteTaskRepository",
    "IProjectRepository",
    "SqliteProjectRepository",
]
