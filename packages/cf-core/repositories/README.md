# cf_core/repositories - Repository Pattern Implementation

Data access layer implementing the Repository pattern for persistence.

## Overview

This module provides repository interfaces and implementations for persisting domain entities. The Repository pattern abstracts data access, allowing the domain layer to remain independent of storage details.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Services     │ --> │   Repositories  │ --> │    Database     │
│  (TaskManSvc)   │     │   (ITaskRepo)   │     │    (SQLite)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               ↑
                        ┌──────┴──────┐
                   SqliteTaskRepo  PostgresTaskRepo
```

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Module exports |
| `task_repository.py` | ITaskRepository + SqliteTaskRepository |
| `sprint_repository.py` | ISprintRepository + SqliteSprintRepository |
| `project_repository.py` | IProjectRepository + SqliteProjectRepository |

## Interface Pattern

Each repository defines an abstract interface:

```python
class ITaskRepository(ABC):
    """Abstract repository interface for Task entities."""

    @abstractmethod
    def save(self, entity: TaskEntity) -> Result[TaskEntity]:
        """Persist a task entity."""
        pass

    @abstractmethod
    def get_by_id(self, task_id: str) -> Result[TaskEntity]:
        """Retrieve task by ID."""
        pass

    @abstractmethod
    def delete(self, task_id: str) -> Result[bool]:
        """Delete task by ID."""
        pass
```

## Result Monad

All repository methods return `Result[T]` for explicit error handling:

```python
from cf_core.shared.result import Result

result = repo.get_by_id("T-001")
if result.is_success:
    task = result.value
else:
    error_msg = result.error
```

## Usage

```python
from cf_core.repositories.task_repository import SqliteTaskRepository
from cf_core.domain.task_entity import TaskEntity

# Create repository
repo = SqliteTaskRepository(db_path="tasks.sqlite")

# Save entity
result = repo.save(task_entity)

# Query
tasks = repo.find_by_status("in_progress")
```

## Testing

```bash
# Unit tests with mocks
pytest tests/cf_core/unit/repositories/ -v

# Integration tests with real DB
pytest tests/cf_core/integration/ -v
```

## Related

- [Domain README](../domain/README.md) - Domain entities
- [Services README](../services/README.md) - Business logic layer
