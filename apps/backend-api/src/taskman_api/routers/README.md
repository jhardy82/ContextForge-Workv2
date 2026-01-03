# TaskMan-v2 Routers Package

FastAPI route handlers using centralized schemas from `schemas/` package.

## Router Files

| File | Endpoints | Description |
|------|-----------|-------------|
| `tasks.py` | `/api/v1/tasks` | Task CRUD operations |
| `projects.py` | `/api/v1/projects` | Project management |
| `sprints.py` | `/api/v1/sprints` | Sprint lifecycle |
| `action_lists.py` | `/api/v1/action-lists` | Action list operations |

## Refactoring (December 2025)

All routers were refactored to use centralized schemas:

```python
# Before (inline Pydantic definitions)
class TaskCreate(BaseModel):
    title: str
    status: str = "todo"

# After (centralized import)
from schemas import TaskCreate, TaskResponse, TaskList
```

**Lines Reduced**: ~325 lines of duplicate Pydantic classes removed

## Schema Imports

Each router imports from `schemas/`:

```python
from schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskList,
)
```

## Adding New Endpoints

1. Define schema in `schemas/task.py` (or appropriate module)
2. Export from `schemas/__init__.py`
3. Import in router file
4. Use as `response_model` in route decorator
