# cf_core/models - Pydantic Data Models

Pydantic v2 models for data validation and serialization.

## Overview

This module contains Pydantic BaseModel classes that define the data structures used throughout cf_core. These models provide:

- Strong type validation
- JSON serialization/deserialization
- Schema generation for OpenAPI
- Field constraints and defaults

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Module exports |
| `priority.py` | **Unified priority enum with comparison operators** |
| `identifiers.py` | ID normalization and validation |
| `status.py` | Task/sprint/project status enums |
| `task.py` | Task model with status, priority, tags |
| `sprint.py` | Sprint model with dates, goals |
| `project.py` | Project model with ownership |
| `velocity.py` | Velocity metrics model |
| `context.py` | Context tracking model |
| `action_item.py` | Sub-task/action item model |

## Model Conventions

### ID Patterns
- Tasks: `T-{identifier}` (e.g., `T-001`, `T-auth-fix`)
- Sprints: `S-{identifier}` (e.g., `S-001`, `S-2025-01`)
- Projects: `P-{identifier}` (e.g., `P-CFWORK`)

### Status Values
```python
TaskStatus = Literal["todo", "in_progress", "blocked", "done", "cancelled"]
SprintStatus = Literal["planning", "active", "completed"]
ProjectStatus = Literal["planning", "active", "completed", "cancelled"]
```

### Priority Levels
```python
from cf_core.models.priority import Priority

# Unified Priority enum with full comparison support
Priority.CRITICAL  # P0 - Highest priority (sort_order=0, score=5)
Priority.URGENT    # P1 - Urgent (sort_order=1, score=4)
Priority.HIGH      # P2 - High (sort_order=2, score=3)
Priority.MEDIUM    # P3 - Medium (sort_order=3, score=2)
Priority.LOW       # P4 - Low (sort_order=4, score=1)
Priority.NONE      # P5 - No priority (sort_order=5, score=0)

# Comparison operators (priority-level semantics)
Priority.CRITICAL > Priority.HIGH    # True (higher importance)
Priority.HIGH < Priority.CRITICAL    # True (lower importance)
Priority.MEDIUM <= Priority.MEDIUM   # True (equal)
Priority.HIGH >= Priority.LOW        # True (higher or equal)

# Bidirectional conversion
Priority.from_int(2)       # → Priority.HIGH (MCP compatibility)
Priority.from_string("P2") # → Priority.HIGH (cf_core compatibility)
Priority.HIGH.to_int()     # → 2
Priority.HIGH.to_string()  # → "high"

# Properties for UI and comparison
Priority.CRITICAL.color    # → "red"
Priority.CRITICAL.score    # → 5 (highest numeric value)
Priority.CRITICAL.sort_order # → 0 (min-heap ordering)
```

## Usage

```python
from cf_core.models.task import Task

# Create with validation
task = Task(
    id="T-001",
    title="Fix authentication bug",
    status="in_progress",
    priority="high",
    tags=["bug", "auth"]
)

# Serialize to JSON
json_data = task.model_dump_json()

# Parse from JSON
task = Task.model_validate_json(json_data)
```

## Configuration

All models use strict configuration:

```python
model_config = ConfigDict(
    extra="forbid",           # No extra fields allowed
    validate_assignment=True, # Validate on attribute set
    str_strip_whitespace=True # Strip whitespace from strings
)
```

## Testing

```bash
pytest tests/cf_core/unit/models/ -v
```

## Related

- [Domain README](../domain/README.md) - Rich domain entities
- [Repositories README](../repositories/README.md) - Persistence layer
