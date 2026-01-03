# cf_core/domain - Domain Entities (DDD)

Domain-Driven Design (DDD) entities implementing core business logic.

## Overview

This module contains rich domain entities that encapsulate business rules and behavior. These entities are the core of the domain model and are used by services and repositories.

## Entity Pattern

Each entity follows this structure:

```python
class TaskEntity:
    """Rich domain entity with business logic."""

    def __init__(self, task: Task):
        self._task = task  # Underlying Pydantic model

    @property
    def id(self) -> str:
        return self._task.id

    # Business methods
    def complete(self) -> None:
        """Mark task as complete with business rules."""
        self._task.status = "done"
        self._task.completed_at = datetime.now(UTC)
```

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Module exports |
| `task_entity.py` | TaskEntity with task lifecycle logic |
| `sprint_entity.py` | SprintEntity with sprint management |
| `project_entity.py` | ProjectEntity with project hierarchy |
| `entities/` | Additional entity definitions |

## Entity Lifecycle

### Task States
```
todo → in_progress → done
  ↓        ↓
  blocked → cancelled
```

### Sprint States
```
planning → active → completed
```

### Project States
```
planning → active → completed/cancelled
```

## Usage

```python
from cf_core.domain.task_entity import TaskEntity
from cf_core.models.task import Task

# Create entity from model
task = Task(id="T-001", title="Example", status="todo")
entity = TaskEntity(task)

# Use business methods
entity.start()  # → in_progress
entity.complete()  # → done
```

## Testing

```bash
pytest tests/cf_core/unit/domain/ -v
```

## Related

- [Models README](../models/README.md) - Pydantic data models
- [Repositories README](../repositories/README.md) - Persistence layer
