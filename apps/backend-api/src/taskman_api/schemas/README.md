# TaskMan-v2 Schemas Package

Centralized Pydantic v2 schemas for the TaskMan-v2 Backend API.

## Purpose

Provides a single source of truth for API request/response schemas, replacing inline definitions in routers. All schemas are aligned with the full database complexity (40+ fields for tasks).

## Files

| File | Contents |
|------|----------|
| `enums.py` | TaskStatus, TaskPriority, ProjectStatus, SprintStatus |
| `base.py` | Reusable mixins (TimestampMixin, ObservabilityMixin, etc.) |
| `task.py` | TaskCreate, TaskUpdate, TaskResponse, TaskList |
| `project.py` | ProjectCreate, ProjectUpdate, ProjectResponse |
| `sprint.py` | SprintCreate, SprintUpdate, SprintResponse, SprintProgress |
| `action_list.py` | ActionListCreate, ActionListResponse, etc. |
| `__init__.py` | All public exports |

## Usage

```python
from schemas import TaskCreate, TaskResponse, TaskStatus, TaskPriority

# Create a new task
task = TaskCreate(
    title="My Task",
    status=TaskStatus.NEW,
    priority=TaskPriority.P1,
    owner="user@example.com"
)

# Validate response
response = TaskResponse.model_validate(db_task, from_attributes=True)
```

## Enums

```python
class TaskStatus(str, Enum):
    NEW = "new"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    REVIEW = "review"
    DONE = "done"
    DROPPED = "dropped"

class TaskPriority(str, Enum):
    P0 = "p0"  # Critical
    P1 = "p1"  # High
    P2 = "p2"  # Medium
    P3 = "p3"  # Low
```

## Base Mixins

Reusable field groups:

- **TimestampMixin**: `created_at`, `updated_at`
- **ObservabilityMixin**: `dashboards`, `alerts`, `logs`, `slos`
- **OwnershipMixin**: `owner`, `assignees`, `sponsors`, `stakeholders`
- **QualityMixin**: `acceptance_criteria`, `definition_of_done`, `quality_gates`
