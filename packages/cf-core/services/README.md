# cf_core/services - Service Layer

Business logic and orchestration services.

## Overview

This module contains service classes that implement business logic, orchestrating repositories and domain entities. Services are the primary interface for CLI and MCP handlers.

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Module exports |
| `taskman_service.py` | Main TaskMan service with CRUD + search |
| `task_service.py` | Task-specific operations |
| `velocity_service.py` | Velocity tracking and metrics |

## Service Pattern

Services follow this structure:

```python
class TaskManService:
    """Orchestrates task management operations."""

    def __init__(self, repository: ITaskRepository):
        self._repo = repository

    def create_task(self, **kwargs) -> Result[dict]:
        """Create a new task with validation."""
        # Validate input
        # Create entity
        # Persist via repository
        # Return result
```

## Key Service: TaskManService

Primary service for task management:

### Task Operations
- `create_task()` - Create with validation
- `get_task()` - Retrieve by ID
- `update_task()` - Partial updates
- `delete_task()` - Remove task
- `list_tasks()` - List with filters
- `search_tasks()` - Full-text search
- `batch_update_tasks()` - Bulk updates

### Sprint Operations
- `create_sprint()` - Create sprint
- `get_sprint()` - Retrieve by ID
- `update_sprint()` - Update fields
- `list_sprints()` - List with filters

### Health
- `health_check()` - Database connectivity

## Usage

```python
from cf_core.services.taskman_service import TaskManService
from cf_core.repositories.task_repository import SqliteTaskRepository

# Create service with repository
repo = SqliteTaskRepository(db_path="tasks.sqlite")
service = TaskManService(repository=repo)

# Create task
result = service.create_task(
    title="Implement feature",
    priority="high",
    status="todo"
)

if result.is_success:
    task = result.value
```

## Testing

```bash
# Unit tests (36 tests)
pytest tests/cf_core/unit/services/test_taskman_service.py -v
```

## Related

- [Repositories README](../repositories/README.md) - Data access layer
- [CLI README](../cli/README.md) - Command-line interface
