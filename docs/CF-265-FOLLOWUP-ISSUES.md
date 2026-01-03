# CF-265 Follow-up Issues - Architecture Improvements

**Created**: 2025-12-15
**Status**: Backlog
**Parent**: CF-265 (TaskMan-v2 Python MCP Server Validation)

---

## CF-275: Relationship CRUD Methods (Created in Linear)

See Linear issue CF-275 for full details.

**Gaps Identified**:
1. `list_tasks_in_sprint(sprint_id)` - Query tasks by sprint_id
2. `list_tasks_in_project(project_id)` - Query tasks by project_id
3. `list_sprints_in_project(project_id)` - Query sprints by project_id
4. `assign_task_to_sprint(task_id, sprint_id)` - Bidirectional sync
5. `unassign_task_from_sprint(task_id)` - Set task.sprint_id = None
6. Full project CRUD (`create_project`, `update_project`, `delete_project`)
7. `get_orphaned_tasks()` - UCL compliance

---

## CF-274: Priority System Unification (Needs Linear Issue)

### Current State
- `cf_core/models/task.py`: Uses `TaskPriority = Literal["low", "medium", "high", "critical"]` (string)
- `cf_core/domain/entities/task_entity.py`: Uses `priority: int = 3` (integer)
- `cf_core/models/priority.py`: Has unified `Priority` enum with bidirectional int↔string mapping

### Problem
- Inconsistent priority handling across codebase
- MCP validation showed priority must be string literal
- Linear uses integer (1=urgent, 2=high, 3=medium, 4=low)

### Proposed Solution

1. **Storage**: Use integer (1-4) internally
   - 1 = urgent/critical
   - 2 = high
   - 3 = medium (default)
   - 4 = low

2. **Display**: Convert to string for user-facing output
   - `priority_display` property returns human-readable string
   - `priority_label` property returns P1/P2/P3/P4 notation

3. **Input**: Accept both formats
   - `normalize_priority()` from `cf_core/models/priority.py` handles conversion
   - Service layer accepts `int | str` and normalizes

### Implementation Tasks

- [ ] Update `Task` model to use `Priority` enum from `priority.py`
- [ ] Add `priority_display` computed property
- [ ] Update `TaskManService` to accept int or string
- [ ] Update MCP tools to use normalized priority
- [ ] Add tests for priority conversion

### Files to Modify

- `cf_core/models/task.py`
- `cf_core/domain/task_entity.py`
- `cf_core/services/taskman_service.py`
- `cf_core/mcp/taskman_server.py`

---

## CF-276: Async Service Layer Support (Needs Linear Issue)

### Current State
- All `TaskManService` methods are synchronous (`def`, not `async def`)
- MCP servers typically benefit from async operations
- Database operations could be async for better concurrency

### Proposed Solution

1. **Dual Support**: Add async versions alongside sync
   - `create_task()` → `create_task_async()`
   - Maintains backwards compatibility

2. **Alternative**: Full async migration
   - Convert all methods to `async def`
   - Use `asyncio.to_thread()` for sync database operations

### Implementation Pattern

```python
# Option 1: Dual support
def create_task(self, ...) -> Result[TaskEntity]:
    """Sync version"""
    return self._create_task_impl(...)

async def create_task_async(self, ...) -> Result[TaskEntity]:
    """Async version"""
    return await asyncio.to_thread(self._create_task_impl, ...)

# Option 2: Full async with sync wrapper
async def create_task(self, ...) -> Result[TaskEntity]:
    """Async primary"""
    ...

def create_task_sync(self, ...) -> Result[TaskEntity]:
    """Sync wrapper for non-async contexts"""
    return asyncio.run(self.create_task(...))
```

### Decision Needed
- Which pattern to use?
- What's the expected async usage (MCP? API? CLI?)

---

## CF-277: Entity Structure Consolidation (Needs Linear Issue)

### Current State

Two different patterns exist:

**Pattern A** (`cf_core/domain/task_entity.py`, `sprint_entity.py`, `project_entity.py`):
- Wrapper class around Pydantic model
- `__init__(self, model: Model)`
- Properties expose model fields
- Business logic methods

**Pattern B** (`cf_core/domain/entities/task_entity.py`):
- Dataclass-based entity
- Direct fields (not wrapped)
- Value objects (TaskId)
- Different field names

### Problem
- Duplicate `TaskEntity` in two locations
- Inconsistent patterns
- Confusing for developers

### Proposed Solution

1. **Choose Pattern A** (wrapper around Pydantic model)
   - Already used by Sprint and Project
   - Cleaner separation of model vs. entity
   - Better for validation

2. **Create BaseEntity**
   ```python
   class BaseEntity:
       @property
       def id(self) -> str: ...
       @property
       def created_at(self) -> datetime: ...
       @property
       def updated_at(self) -> datetime: ...

       def can_transition_to(self, new_status: str) -> bool: ...
       def update_status(self, new_status: str) -> None: ...
   ```

3. **Remove duplicate**
   - Delete `cf_core/domain/entities/task_entity.py`
   - Update imports throughout codebase

### Files to Modify
- Create `cf_core/domain/base_entity.py`
- Update `cf_core/domain/task_entity.py`
- Update `cf_core/domain/sprint_entity.py`
- Update `cf_core/domain/project_entity.py`
- Delete `cf_core/domain/entities/task_entity.py`

---

## Priority Order

| Issue | Priority | Effort | Impact |
|-------|----------|--------|--------|
| CF-275 | P0 | High | Enables relationship queries |
| CF-274 | P1 | Medium | Consistency |
| CF-277 | P2 | Medium | Code quality |
| CF-276 | P3 | High | Future-proofing |

---

## Validation Results (2025-12-15)

```
Relationship CRUD Results
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━┓
┃ Category         ┃ Passed ┃ Failed ┃ Gaps ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━┩
│ Task ↔ Sprint    │ 4      │ 0      │ 2    │
│ Task ↔ Project   │ 0      │ 0      │ 2    │
│ Sprint ↔ Project │ 0      │ 0      │ 2    │
│ Cascading        │ 0      │ 0      │ 1    │
├──────────────────┼────────┼────────┼──────┤
│ TOTAL            │ 4      │ 0      │ 7    │
└──────────────────┴────────┴────────┴──────┘
```

---

## Next Steps

1. Implement `list_tasks_in_sprint()` - most commonly needed
2. Implement project CRUD in TaskManService
3. Create MCP tools for new methods
4. Run validation again to confirm gaps closed
