# ADR-017: ActionList Repository Layer Enhancement

## Status
**Proposed** | 2025-12-28

## Context

ContextForge Work employs a layered architecture with clear separation of concerns:

- **cf_core**: Domain models, business logic, and repository interfaces (technology-agnostic)
- **TaskMan-v2**: Concrete implementations using SQLAlchemy ORM with PostgreSQL/SQLite dual-database support

Phase 3 execution requires implementing the concrete `ActionListRepository` to bridge cf_core's `IActionListRepository` interface with TaskMan-v2's database layer. This ADR documents the architectural decisions for this critical integration point.

### Current State

**cf_core Interface** ([action_list_repository.py](../../cf_core/repositories/action_list_repository.py)):
```python
class IActionListRepository(ABC):
    @abstractmethod
    def save(self, entity: ActionListEntity) -> Result[ActionListEntity]: ...

    @abstractmethod
    def get_by_id(self, list_id: str) -> Result[ActionListEntity]: ...

    @abstractmethod
    def find_all(self) -> Result[list[ActionListEntity]]: ...

    @abstractmethod
    def delete(self, list_id: str) -> Result[bool]: ...

    @abstractmethod
    def find_by_status(self, status: str) -> Result[list[ActionListEntity]]: ...

    @abstractmethod
    def find_by_task_id(self, task_id: str) -> Result[list[ActionListEntity]]: ...
```

**TaskMan-v2 Current Implementation** ([repositories/action_list_repository.py](../../TaskMan-v2/backend-api/src/taskman_api/repositories/action_list_repository.py)):
- Extends `BaseRepository[ActionList]` for standard CRUD
- Uses `AsyncSession` for database operations
- Implements TaskMan-specific query methods (`get_active`, `search`, `add_task`)
- **Gap**: No Result monad pattern, no alignment with cf_core interface

**Existing Patterns to Follow**:
- `TaskRepository`: 234 lines with 10+ query methods, full test coverage
- `SprintRepository`: Similar pattern with project/status filtering
- `BaseRepository`: Generic CRUD foundation with async/await

### The Integration Challenge

1. **Result Monad Pattern**: cf_core uses `Result[T]` for explicit error handling; TaskMan-v2 uses exceptions
2. **Sync vs Async**: cf_core interface is synchronous; TaskMan-v2 uses async SQLAlchemy
3. **Entity vs Model**: cf_core uses `ActionListEntity`; TaskMan-v2 uses SQLAlchemy `ActionList` model
4. **Session Management**: Need dependency injection pattern for database session lifecycle

## Decision Drivers

### Functional Requirements
- ✅ Implement all 6 cf_core interface methods with Result monad pattern
- ✅ Support specialized queries (status-based, task-based filtering)
- ✅ Maintain compatibility with existing TaskMan-v2 API endpoints
- ✅ Preserve dual-database support (PostgreSQL ARRAY, SQLite JSON via `StringList`)

### Quality Attributes
- **Maintainability**: Follow established BaseRepository/TaskRepository patterns
- **Testability**: 10 unit tests with 100% method coverage, isolated session fixtures
- **Performance**: Minimize N+1 queries, use eager loading for relationships
- **Reliability**: Comprehensive error handling with Result monad wrapping

### Constraints
- Must use async SQLAlchemy (TaskMan-v2 is fully async)
- Cannot break existing API endpoints (`search`, `create_action_list`, etc.)
- Session injection via FastAPI dependency injection
- Must align with ADR-016 schema compatibility matrix

### Assumptions
- cf_core consumers will handle Result unwrapping
- Database migrations (Alembic) already include ActionList table
- Session lifecycle managed by FastAPI request scope

## Options Considered

### Option 1: Direct SQLAlchemy in Services (Anti-Pattern) ❌

**Approach**: Bypass repository layer; services directly query database.

```python
# Anti-pattern example
class ActionListService:
    async def get_list(self, session: AsyncSession, list_id: str):
        result = await session.execute(select(ActionList).where(ActionList.id == list_id))
        return result.scalar_one_or_none()
```

**Pros**:
- Zero abstraction overhead
- Simplest possible implementation

**Cons**:
- Violates separation of concerns (domain logic coupled to ORM)
- Impossible to mock for testing without full database
- No Result monad error handling
- Breaks cf_core architecture contract
- Duplicates query logic across services

**Verdict**: Rejected — fundamentally incompatible with ContextForge architecture

---

### Option 2: Generic Repository Base Class

**Approach**: Extend BaseRepository with generic Result monad adapters.

```python
class ResultRepository(BaseRepository[T], Generic[T]):
    async def get_by_id_result(self, entity_id: str) -> Result[T]:
        try:
            entity = await self.get_by_id(entity_id)
            if entity is None:
                return Result.failure(f"Entity {entity_id} not found")
            return Result.success(entity)
        except Exception as e:
            return Result.failure(str(e))

class ActionListRepository(ResultRepository[ActionList]):
    pass  # Inherit all methods
```

**Pros**:
- Reusable across Task/Sprint/Project repositories
- Minimal code duplication
- Automatic Result wrapping for all operations

**Cons**:
- Generic error messages lose context ("Entity not found" vs "ActionList AL-001 not found")
- Doesn't handle specialized queries (find_by_task_id)
- Mixing sync/async paradigms confusing
- Over-abstraction for this phase (premature generalization)

**Verdict**: Rejected for Phase 3 — Consider for future Phase 4 refactoring if pattern emerges across 3+ repositories

---

### Option 3: Specialized ActionListRepository (Recommended) ✅

**Approach**: Concrete implementation implementing cf_core interface with explicit Result monad adapters.

```python
class ActionListRepository(BaseRepository[ActionList]):
    """
    Concrete repository implementing IActionListRepository interface.
    Bridges cf_core domain models with TaskMan-v2 SQLAlchemy persistence.
    """

    model_class = ActionList

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    # --- cf_core Interface Methods (Result Monad Pattern) ---

    async def save_result(self, entity: ActionListEntity) -> Result[ActionListEntity]:
        """Save with Result monad error handling."""
        try:
            # Transform: ActionListEntity → SQLAlchemy ActionList
            db_model = self._entity_to_model(entity)

            if await self.exists(entity.id):
                # Update existing
                existing = await self.get_by_id(entity.id)
                self._update_fields(existing, entity)
                await self.session.commit()
                await self.session.refresh(existing)
                return Result.success(self._model_to_entity(existing))
            else:
                # Create new
                saved = await self.create(db_model)
                return Result.success(self._model_to_entity(saved))

        except IntegrityError as e:
            await self.session.rollback()
            return Result.failure(f"Database constraint violation: {e.orig}")
        except SQLAlchemyError as e:
            await self.session.rollback()
            return Result.failure(f"Database error: {str(e)}")

    async def get_by_id_result(self, list_id: str) -> Result[ActionListEntity]:
        """Get by ID with Result monad."""
        try:
            model = await self.get_by_id(list_id)
            if model is None:
                return Result.failure(f"ActionList '{list_id}' not found")
            return Result.success(self._model_to_entity(model))
        except SQLAlchemyError as e:
            return Result.failure(f"Database error retrieving {list_id}: {str(e)}")

    async def find_by_status_result(self, status: str) -> Result[list[ActionListEntity]]:
        """Find by status with Result monad."""
        try:
            # Leverage BaseRepository query method
            result = await self.session.execute(
                select(ActionList).where(ActionList.status == status)
            )
            models = list(result.scalars().all())
            entities = [self._model_to_entity(m) for m in models]
            return Result.success(entities)
        except SQLAlchemyError as e:
            return Result.failure(f"Database error filtering by status '{status}': {str(e)}")

    async def find_by_task_id_result(self, task_id: str) -> Result[list[ActionListEntity]]:
        """Find action lists containing task_id (PostgreSQL ARRAY / SQLite JSON)."""
        try:
            # PostgreSQL: task_ids @> ARRAY['task_id']
            # SQLite: JSON search via StringList TypeDecorator
            result = await self.session.execute(
                select(ActionList).where(ActionList.task_ids.contains([task_id]))
            )
            models = list(result.scalars().all())
            entities = [self._model_to_entity(m) for m in models]
            return Result.success(entities)
        except SQLAlchemyError as e:
            return Result.failure(f"Database error searching for task '{task_id}': {str(e)}")

    # --- TaskMan-v2 API Compatibility Methods (Existing) ---

    async def get_active(self, limit: int = 100) -> list[ActionList]:
        """Existing method for API endpoints."""
        result = await self.session.execute(
            select(ActionList).where(ActionList.status == "active").limit(limit)
        )
        return list(result.scalars().all())

    # --- Helper Methods ---

    def _entity_to_model(self, entity: ActionListEntity) -> ActionList:
        """Transform domain entity to SQLAlchemy model."""
        return ActionList(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            status=entity.status,
            task_ids=entity.task_ids,
            tags=entity.tags,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def _model_to_entity(self, model: ActionList) -> ActionListEntity:
        """Transform SQLAlchemy model to domain entity."""
        return ActionListEntity(
            id=model.id,
            name=model.name,
            description=model.description or "",
            status=model.status,
            task_ids=model.task_ids or [],
            tags=model.tags or [],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
```

**Pros**:
- ✅ Explicit cf_core interface implementation with Result monad
- ✅ Follows established TaskRepository pattern (234 lines reference)
- ✅ Specialized error messages with context
- ✅ Preserves existing TaskMan-v2 API methods (`get_active`, `search`)
- ✅ Clear transformation layer (Entity ↔ Model)
- ✅ Testable with session mocks/fixtures

**Cons**:
- More verbose than generic base class (acceptable trade-off for clarity)
- Some code duplication across repositories (mitigated by copy-paste from TaskRepository)

**Verdict**: **Accepted** — Best balance of maintainability, testability, and alignment with existing patterns

## Decision

We will implement **Option 3: Specialized ActionListRepository** with the following technical architecture:

### 1. Session Lifecycle Management

**Pattern**: Dependency Injection via FastAPI

```python
# FastAPI dependency
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

# Service layer injection
@router.post("/action-lists")
async def create_action_list(
    data: ActionListCreate,
    session: AsyncSession = Depends(get_db_session)
):
    repo = ActionListRepository(session)
    result = await repo.save_result(entity)
    # Handle Result monad...
```

**Rationale**:
- Session scope = HTTP request lifecycle (auto-commit/rollback)
- Testable via fixture injection
- No manual session.close() required (context manager handles cleanup)

### 2. Error Mapping Strategy

**SQLAlchemy Exception → Result.failure() Mapping**:

| Exception | Result.failure() Message Pattern | HTTP Status (if API) |
|-----------|----------------------------------|---------------------|
| `IntegrityError` | "Database constraint violation: [original error]" | 409 Conflict |
| `NoResultFound` | "ActionList '{id}' not found" | 404 Not Found |
| `MultipleResultsFound` | "Multiple ActionLists found for '{id}' (data corruption)" | 500 Internal Error |
| `SQLAlchemyError` | "Database error: [operation context]" | 500 Internal Error |
| Unexpected exception | "Unexpected error: [type]" (logged with stack trace) | 500 Internal Error |

**Implementation**:
```python
async def get_by_id_result(self, list_id: str) -> Result[ActionListEntity]:
    try:
        model = await self.get_by_id(list_id)
        if model is None:
            return Result.failure(f"ActionList '{list_id}' not found")
        return Result.success(self._model_to_entity(model))
    except IntegrityError as e:
        logger.error(f"Integrity error fetching {list_id}", exc_info=True)
        return Result.failure(f"Database constraint violation: {e.orig}")
    except SQLAlchemyError as e:
        logger.error(f"Database error fetching {list_id}", exc_info=True)
        return Result.failure(f"Database error: {str(e)}")
    except Exception as e:
        logger.critical(f"Unexpected error fetching {list_id}", exc_info=True)
        return Result.failure(f"Unexpected error: {type(e).__name__}")
```

### 3. Query Optimization

**Indexing Strategy** (aligned with database schema):

```sql
-- Existing indexes from Alembic migrations
CREATE INDEX idx_action_lists_status ON action_lists(status);
CREATE INDEX idx_action_lists_created_at ON action_lists(created_at DESC);

-- Recommend adding for find_by_task_id performance
CREATE INDEX idx_action_lists_task_ids_gin ON action_lists USING GIN(task_ids);  -- PostgreSQL
```

**Eager Loading** (if relationships added in future):
```python
# Example for future Sprint/Project relationships
async def get_with_tasks(self, list_id: str) -> Result[ActionListEntity]:
    result = await self.session.execute(
        select(ActionList)
        .options(selectinload(ActionList.tasks))  # Eager load
        .where(ActionList.id == list_id)
    )
    # ...
```

**N+1 Query Prevention**:
```python
# BAD: N+1 queries
for action_list in action_lists:
    tasks = await session.execute(select(Task).where(Task.id.in_(action_list.task_ids)))

# GOOD: Single query with JOIN or IN clause
task_ids = {tid for al in action_lists for tid in al.task_ids}
tasks = await session.execute(select(Task).where(Task.id.in_(task_ids)))
task_map = {t.id: t for t in tasks.scalars().all()}
```

### 4. Test Isolation Strategy

**10 Unit Tests Targeting All Methods**:

```python
# tests/unit/repositories/test_action_list_repository.py

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

class TestActionListRepository:
    """Test suite for ActionListRepository (10 tests = 100% method coverage)."""

    @pytest.fixture
    async def repo(self, async_session: AsyncSession):
        """Provide repository with test session."""
        return ActionListRepository(async_session)

    @pytest.fixture
    async def sample_entity(self):
        """Provide sample ActionListEntity."""
        return ActionListEntity(
            id="AL-001",
            name="Test List",
            description="Test description",
            status="active",
            task_ids=["T-001", "T-002"],
            tags=["test"],
        )

    # --- Test Methods ---

    async def test_save_new_entity(self, repo, sample_entity):
        """Test creating new action list."""
        result = await repo.save_result(sample_entity)
        assert result.is_success()
        assert result.value.id == "AL-001"

    async def test_save_existing_entity_updates(self, repo, sample_entity):
        """Test updating existing action list."""
        await repo.save_result(sample_entity)
        sample_entity.name = "Updated Name"
        result = await repo.save_result(sample_entity)
        assert result.is_success()
        assert result.value.name == "Updated Name"

    async def test_get_by_id_success(self, repo, sample_entity):
        """Test retrieving existing action list."""
        await repo.save_result(sample_entity)
        result = await repo.get_by_id_result("AL-001")
        assert result.is_success()
        assert result.value.name == "Test List"

    async def test_get_by_id_not_found(self, repo):
        """Test retrieving non-existent action list."""
        result = await repo.get_by_id_result("NONEXISTENT")
        assert result.is_failure()
        assert "not found" in result.error.lower()

    async def test_find_all(self, repo, sample_entity):
        """Test retrieving all action lists."""
        await repo.save_result(sample_entity)
        result = await repo.find_all_result()
        assert result.is_success()
        assert len(result.value) >= 1

    async def test_delete_success(self, repo, sample_entity):
        """Test deleting existing action list."""
        await repo.save_result(sample_entity)
        result = await repo.delete_result("AL-001")
        assert result.is_success()
        assert result.value is True  # Deletion confirmed

    async def test_delete_not_found(self, repo):
        """Test deleting non-existent action list."""
        result = await repo.delete_result("NONEXISTENT")
        assert result.is_failure()  # Or success with False, depending on design

    async def test_find_by_status(self, repo, sample_entity):
        """Test filtering by status."""
        await repo.save_result(sample_entity)
        result = await repo.find_by_status_result("active")
        assert result.is_success()
        assert all(e.status == "active" for e in result.value)

    async def test_find_by_task_id(self, repo, sample_entity):
        """Test finding lists containing specific task."""
        await repo.save_result(sample_entity)
        result = await repo.find_by_task_id_result("T-001")
        assert result.is_success()
        assert len(result.value) == 1
        assert "T-001" in result.value[0].task_ids

    async def test_database_error_handling(self, repo, monkeypatch):
        """Test Result.failure() on database errors."""
        async def mock_execute_error(*args, **kwargs):
            raise SQLAlchemyError("Mock database error")

        monkeypatch.setattr(repo.session, "execute", mock_execute_error)
        result = await repo.get_by_id_result("AL-001")
        assert result.is_failure()
        assert "database error" in result.error.lower()
```

**Fixture Strategy**:
```python
# conftest.py
@pytest.fixture
async def async_session():
    """Provide isolated async session with automatic rollback."""
    async with async_session_factory() as session:
        async with session.begin():
            yield session
            await session.rollback()  # Rollback after each test
```

## Consequences

### Positive

✅ **Clear Separation of Concerns**: Domain logic (cf_core) completely decoupled from ORM (TaskMan-v2)

✅ **Explicit Error Handling**: Result monad forces consumers to handle failures (no silent exceptions)

✅ **Testability**: 100% method coverage achievable with isolated session fixtures

✅ **Performance Optimization**: Indexing strategy documented; eager loading ready for relationships

✅ **Maintainability**: Follows established TaskRepository pattern (easy onboarding for new developers)

✅ **API Compatibility**: Existing TaskMan-v2 endpoints (`get_active`, `search`) preserved

### Negative

⚠️ **Async Complexity**: cf_core interface is sync but implementation is async (consumers must use `asyncio.run()` or event loop)

⚠️ **Code Duplication**: Result monad wrapping repeated across methods (mitigated by clear patterns)

⚠️ **Transformation Overhead**: Entity ↔ Model conversion adds CPU cost (negligible for <1000 lists, optimize if needed)

### Neutral

➖ **Testing Investment**: 10 unit tests required (~2-3 hours implementation)

➖ **Documentation Burden**: Transformation logic must be documented (this ADR serves as reference)

## Related Decisions

- **[ADR-016: Schema Audit for ActionList Integration](./ADR-016-Schema-Audit-ActionList-Integration.md)** — Defines field mapping between cf_core Entity and TaskMan-v2 Model
- **[ADR-001: QSE-UTMW Architecture](./ADR-001-QSE-UTMW-Architecture.md)** — Establishes Result monad pattern as core standard
- **Future ADR-018**: Task Repository Enhancement (will follow this pattern)
- **Future ADR-019**: Sprint Repository Enhancement (will follow this pattern)

## Implementation Checklist

- [ ] Create `ActionListRepository` in `TaskMan-v2/backend-api/src/taskman_api/repositories/action_list_repository.py`
- [ ] Implement 6 cf_core interface methods with Result monad wrapping
- [ ] Add specialized query methods (`find_by_status`, `find_by_task_id`)
- [ ] Implement entity/model transformation helpers (`_entity_to_model`, `_model_to_entity`)
- [ ] Create 10 unit tests in `tests/unit/repositories/test_action_list_repository.py`
- [ ] Add GIN index for `task_ids` in Alembic migration (PostgreSQL performance)
- [ ] Update repository `__init__.py` exports
- [ ] Validate with integration test hitting real database
- [ ] Document session lifecycle in service layer integration guide

## Notes

### Performance Benchmarks (Target)
- `get_by_id`: <5ms (indexed primary key)
- `find_by_status`: <20ms for 1000 records (indexed status column)
- `find_by_task_id`: <50ms for 1000 records (GIN index on PostgreSQL, full scan on SQLite)

### Future Optimization Opportunities
1. **Generic Result Adapter**: If pattern repeats across Task/Sprint/Project, extract to `ResultRepository` mixin
2. **Caching Layer**: Redis cache for frequently accessed lists (status="active")
3. **Batch Operations**: Add `save_many()` for bulk imports
4. **Soft Deletes**: Add `is_deleted` flag instead of hard deletes (audit trail)

### References
- [Repository Pattern - Martin Fowler](https://martinfowler.com/eaaCatalog/repository.html)
- [SQLAlchemy Async ORM](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Result Monad Pattern - ContextForge Standards](../../cf_core/shared/result.py)
