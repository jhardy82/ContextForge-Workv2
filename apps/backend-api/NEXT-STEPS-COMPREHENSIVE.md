# TaskMan-v2 Backend API - Comprehensive Next Steps

**Generated**: 2025-12-25
**Current Phase**: 0.4 - Service Layer
**Overall Progress**: 37.5% (3 of 8 phases complete)

---

## 🎯 Executive Summary

**What We've Built**:
- ✅ **Foundation Layer**: 14 files, 9 enums, 8 error classes, 4 ORM models (175+ fields)
- ✅ **Database Layer**: 10 files, BaseRepository + 4 specialized repositories, 32 query methods
- ✅ **Schema Layer**: 8 files, 12 Pydantic schemas, 50+ validation rules

**What's Next**:
- 🔄 **Service Layer**: Business logic with Result monad (Phase 0.4)
- ⏳ **API Endpoints**: 22 REST endpoints with FastAPI (Phase 0.5)
- ⏳ **Infrastructure**: Logging, health checks, migrations (Phases 0.6-0.7)
- ⏳ **Testing & Docs**: Integration tests, documentation (Phases 0.8-0.9)

**Time Investment**:
- Completed: ~7 hours
- Remaining: ~33-48 hours (at current velocity: ~13-18 hours)
- Total: ~40-55 hours

---

## 📊 Current State Analysis

### Completed Components

| Component | Files | Lines | Key Features |
|-----------|-------|-------|--------------|
| **Enums** | 1 | 161 | 9 enumeration types for status, priority, severity, shapes |
| **Errors** | 1 | 251 | RFC 9457 Problem Details, 8 error classes |
| **Result Monad** | 1 | 41 | Type-safe error handling with monadic-error |
| **ORM Models** | 4 | 946 | Task (70+ fields), Project (40+), Sprint (30+), ActionList (18+) |
| **Database Session** | 2 | 208 | Async engine, session factory, dependency injection |
| **Repositories** | 5 | 1,247 | BaseRepository[T] + 4 specialized with 32 query methods |
| **Schemas** | 5 | 915 | 12 Pydantic schemas with 50+ validation rules |
| **Tests** | 6 | 2,203 | 70+ test cases for repos and schemas |

**Total Production Code**: ~3,947 lines
**Total Test Code**: ~2,203 lines
**Test-to-Code Ratio**: 56% (excellent)

### Architecture Strengths

1. **Type Safety**: 100% type hints throughout
2. **Error Handling**: RFC 9457 compliant with Result monad
3. **Async Patterns**: SQLAlchemy 2.0 with proper session management
4. **Validation**: Comprehensive field validation with Pydantic
5. **Testing**: Strong test coverage foundation

### Gaps to Address

1. **Business Logic**: No service layer yet
2. **API Endpoints**: No REST endpoints implemented
3. **Infrastructure**: Missing logging, health checks
4. **Integration Tests**: No E2E tests
5. **Documentation**: No API docs yet

---

## 🚀 Phase 0.4: Service Layer - Detailed Plan

### Overview

**Duration**: 8-10 hours (estimated 3-4 hours at current velocity)
**Dependencies**: ✅ All previous phases complete
**Deliverables**: 5 service files + tests (~2,000 lines)

### Task Breakdown

#### Task 1: Create BaseService[T] (2-3 hours)

**File**: `src/taskman_api/services/base.py`

**Implementation**:
```python
from typing import Generic, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.result import Result, Ok, Err
from taskman_api.core.errors import NotFoundError, ValidationError, AppError
from taskman_api.db.repositories.base import BaseRepository

TModel = TypeVar("TModel")  # SQLAlchemy model
TCreate = TypeVar("TCreate")  # Pydantic create schema
TUpdate = TypeVar("TUpdate")  # Pydantic update schema
TResponse = TypeVar("TResponse")  # Pydantic response schema


class BaseService(Generic[TModel, TCreate, TUpdate, TResponse]):
    """Generic service layer with business logic.

    Coordinates between repositories and schemas.
    Provides CRUD operations with Result monad pattern.
    """

    def __init__(
        self,
        repository: BaseRepository[TModel],
        model_class: type[TModel],
        response_class: type[TResponse],
    ):
        self.repository = repository
        self.model_class = model_class
        self.response_class = response_class

    async def create(
        self,
        request: TCreate,
    ) -> Result[TResponse, AppError]:
        """Create entity with validation.

        Args:
            request: Validated create request schema

        Returns:
            Result with created entity response or error
        """
        # Convert Pydantic schema to ORM model
        model_data = request.model_dump(exclude_unset=True)
        entity = self.model_class(**model_data)

        # Repository operation
        result = await self.repository.create(entity)

        # Convert ORM model to response schema
        match result:
            case Ok(created_entity):
                response = self.response_class.model_validate(created_entity)
                return Ok(response)
            case Err(error):
                return Err(error)

    async def get(
        self,
        entity_id: str,
    ) -> Result[TResponse, NotFoundError | AppError]:
        """Get entity by ID.

        Args:
            entity_id: Entity identifier

        Returns:
            Result with entity response or error
        """
        result = await self.repository.find_by_id(entity_id)

        match result:
            case Ok(entity):
                response = self.response_class.model_validate(entity)
                return Ok(response)
            case Err(error):
                return Err(error)

    async def update(
        self,
        entity_id: str,
        request: TUpdate,
    ) -> Result[TResponse, NotFoundError | AppError]:
        """Update entity with partial fields.

        Args:
            entity_id: Entity identifier
            request: Validated update request schema

        Returns:
            Result with updated entity response or error
        """
        # Get existing entity
        find_result = await self.repository.find_by_id(entity_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entity):
                # Apply partial updates (only set fields that were provided)
                update_data = request.model_dump(exclude_unset=True)
                for field, value in update_data.items():
                    setattr(entity, field, value)

                # Save updated entity
                update_result = await self.repository.update(entity)

                match update_result:
                    case Ok(updated_entity):
                        response = self.response_class.model_validate(updated_entity)
                        return Ok(response)
                    case Err(error):
                        return Err(error)

    async def delete(
        self,
        entity_id: str,
    ) -> Result[bool, NotFoundError | AppError]:
        """Delete entity by ID.

        Args:
            entity_id: Entity identifier

        Returns:
            Result with True if deleted, or error
        """
        return await self.repository.delete(entity_id)

    async def list(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[TResponse], AppError]:
        """List entities with pagination.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of entity responses or error
        """
        result = await self.repository.find_all(limit=limit, offset=offset)

        match result:
            case Ok(entities):
                responses = [
                    self.response_class.model_validate(entity)
                    for entity in entities
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)
```

**Tests**: `tests/unit/services/test_base_service.py` (10 test cases)

**Deliverables**:
- Generic CRUD operations
- Request → ORM conversion
- ORM → Response conversion
- Partial update handling
- Result monad pattern
- 10 unit tests with mocked repository

---

#### Task 2: Create TaskService (3-4 hours)

**File**: `src/taskman_api/services/task_service.py`

**Specialized Methods**:
```python
class TaskService(BaseService[Task, TaskCreateRequest, TaskUpdateRequest, TaskResponse]):
    """Task business logic and operations."""

    def __init__(self, session: AsyncSession):
        from taskman_api.db.repositories.task_repository import TaskRepository
        from taskman_api.db.models.task import Task
        from taskman_api.schemas.task import TaskResponse

        repository = TaskRepository(session)
        super().__init__(repository, Task, TaskResponse)
        self.task_repo = repository  # Type-specific access

    async def change_status(
        self,
        task_id: str,
        new_status: TaskStatus,
    ) -> Result[TaskResponse, NotFoundError | ValidationError | AppError]:
        """Change task status with transition validation.

        Args:
            task_id: Task identifier
            new_status: New status to set

        Returns:
            Result with updated task or error
        """
        # Get current task
        get_result = await self.get(task_id)

        match get_result:
            case Err(error):
                return Err(error)
            case Ok(task_response):
                # Validate status transition
                current_status = task_response.status
                if not self._is_valid_transition(current_status, new_status):
                    return Err(
                        ValidationError(
                            message=f"Invalid status transition: {current_status} -> {new_status}",
                            field="status",
                            value=new_status,
                        )
                    )

                # Update status
                from taskman_api.schemas.task import TaskUpdateRequest
                update_request = TaskUpdateRequest(status=new_status)
                return await self.update(task_id, update_request)

    def _is_valid_transition(
        self,
        current: TaskStatus,
        new: TaskStatus,
    ) -> bool:
        """Validate status transition rules.

        Transition Matrix:
        - NEW → READY, DROPPED
        - READY → IN_PROGRESS, DROPPED
        - IN_PROGRESS → BLOCKED, REVIEW, DONE, DROPPED
        - BLOCKED → IN_PROGRESS, DROPPED
        - REVIEW → IN_PROGRESS, DONE, DROPPED
        - DONE → (no transitions)
        - DROPPED → (no transitions)
        """
        valid_transitions = {
            TaskStatus.NEW: [TaskStatus.READY, TaskStatus.DROPPED],
            TaskStatus.READY: [TaskStatus.IN_PROGRESS, TaskStatus.DROPPED],
            TaskStatus.IN_PROGRESS: [
                TaskStatus.BLOCKED,
                TaskStatus.REVIEW,
                TaskStatus.DONE,
                TaskStatus.DROPPED,
            ],
            TaskStatus.BLOCKED: [TaskStatus.IN_PROGRESS, TaskStatus.DROPPED],
            TaskStatus.REVIEW: [
                TaskStatus.IN_PROGRESS,
                TaskStatus.DONE,
                TaskStatus.DROPPED,
            ],
            TaskStatus.DONE: [],
            TaskStatus.DROPPED: [],
        }

        return new in valid_transitions.get(current, [])

    async def assign_to_sprint(
        self,
        task_id: str,
        sprint_id: str,
    ) -> Result[TaskResponse, NotFoundError | AppError]:
        """Assign task to sprint.

        Args:
            task_id: Task identifier
            sprint_id: Sprint identifier

        Returns:
            Result with updated task or error
        """
        from taskman_api.schemas.task import TaskUpdateRequest

        update_request = TaskUpdateRequest(primary_sprint=sprint_id)
        return await self.update(task_id, update_request)

    async def bulk_update(
        self,
        updates: list[dict],
    ) -> Result[list[TaskResponse], AppError]:
        """Bulk update multiple tasks.

        Args:
            updates: List of {id, fields} to update

        Returns:
            Result with list of updated tasks or error
        """
        results = []
        for update_data in updates:
            task_id = update_data.pop("id")
            from taskman_api.schemas.task import TaskUpdateRequest

            update_request = TaskUpdateRequest(**update_data)
            result = await self.update(task_id, update_request)

            match result:
                case Ok(task):
                    results.append(task)
                case Err(error):
                    return Err(error)  # Fail fast on first error

        return Ok(results)

    async def search(
        self,
        status: TaskStatus | None = None,
        priority: Priority | None = None,
        owner: str | None = None,
        project_id: str | None = None,
        sprint_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[TaskResponse], AppError]:
        """Search tasks with filters.

        Args:
            status: Optional status filter
            priority: Optional priority filter
            owner: Optional owner filter
            project_id: Optional project filter
            sprint_id: Optional sprint filter
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result with filtered tasks or error
        """
        # Apply filters (use repository specialized methods)
        if status and priority:
            result = await self.task_repo.find_by_status_and_priority(
                status, priority, limit, offset
            )
        elif status:
            result = await self.task_repo.find_by_status(status, limit, offset)
        elif priority:
            result = await self.task_repo.find_by_priority(priority, limit, offset)
        elif owner:
            result = await self.task_repo.find_by_owner(owner, limit, offset)
        elif project_id:
            result = await self.task_repo.find_by_project(
                project_id, status, limit, offset
            )
        elif sprint_id:
            result = await self.task_repo.find_by_sprint(
                sprint_id, status, limit, offset
            )
        else:
            result = await self.repository.find_all(limit=limit, offset=offset)

        # Convert to responses
        match result:
            case Ok(tasks):
                responses = [
                    self.response_class.model_validate(task) for task in tasks
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)
```

**Tests**: `tests/unit/services/test_task_service.py` (15 test cases)

**Deliverables**:
- Status transition validation
- Sprint assignment
- Bulk operations
- Complex search filters
- 15 unit tests

---

#### Task 3: Create ProjectService (2 hours)

**File**: `src/taskman_api/services/project_service.py`

**Specialized Methods**:
```python
async def get_metrics(
    self,
    project_id: str,
) -> Result[dict, NotFoundError | AppError]:
    """Calculate project metrics.

    Returns:
        {
            "total_tasks": int,
            "tasks_by_status": {"new": 5, "in_progress": 3, ...},
            "average_velocity": float,
            "health_status": "green" | "yellow" | "red",
        }
    """

async def add_sprint(
    self,
    project_id: str,
    sprint_id: str,
) -> Result[ProjectResponse, NotFoundError | AppError]:
    """Add sprint to project sprints array."""
```

**Tests**: `tests/unit/services/test_project_service.py` (8 test cases)

---

#### Task 4: Create SprintService (2 hours)

**File**: `src/taskman_api/services/sprint_service.py`

**Specialized Methods**:
```python
async def calculate_velocity(
    self,
    sprint_id: str,
) -> Result[float, NotFoundError | AppError]:
    """Calculate actual velocity from completed tasks."""

async def get_burndown(
    self,
    sprint_id: str,
) -> Result[dict, NotFoundError | AppError]:
    """Calculate burndown chart data."""
```

**Tests**: `tests/unit/services/test_sprint_service.py` (8 test cases)

---

#### Task 5: Create ActionListService (1 hour)

**File**: `src/taskman_api/services/action_list_service.py`

**Specialized Methods**:
```python
async def reorder_items(
    self,
    list_id: str,
    item_order: list[int],
) -> Result[ActionListResponse, NotFoundError | AppError]:
    """Reorder items in action list."""

async def mark_complete(
    self,
    list_id: str,
) -> Result[ActionListResponse, NotFoundError | AppError]:
    """Mark action list as completed."""
```

**Tests**: `tests/unit/services/test_action_list_service.py` (5 test cases)

---

#### Task 6: Create Service Tests (2-3 hours)

**Files**:
- `tests/unit/services/conftest.py` - Mock repository fixtures
- `tests/unit/services/test_base_service.py` - 10 tests
- `tests/unit/services/test_task_service.py` - 15 tests
- `tests/unit/services/test_project_service.py` - 8 tests
- `tests/unit/services/test_sprint_service.py` - 8 tests
- `tests/unit/services/test_action_list_service.py` - 5 tests

**Total**: 46 test cases

**Mock Repository Pattern**:
```python
@pytest.fixture
def mock_task_repo(mocker):
    """Mock TaskRepository for service tests."""
    mock = mocker.Mock(spec=TaskRepository)

    # Mock find_by_id
    mock.find_by_id = mocker.AsyncMock(
        return_value=Ok(create_mock_task())
    )

    # Mock create
    mock.create = mocker.AsyncMock(
        return_value=Ok(create_mock_task())
    )

    return mock


async def test_create_task_success(mock_task_repo):
    """Test successful task creation."""
    service = TaskService(session=mock_session)
    service.task_repo = mock_task_repo

    request = TaskCreateRequest(...)
    result = await service.create(request)

    assert isinstance(result, Ok)
    task = result.ok()
    assert task.id == "T-TEST-001"
    mock_task_repo.create.assert_called_once()
```

---

### Phase 0.4 Success Criteria

- ✅ BaseService[T] with 5 CRUD methods
- ✅ 4 specialized services with domain logic
- ✅ Status transition validation (TaskService)
- ✅ Metrics calculation (ProjectService)
- ✅ Bulk operations (TaskService)
- ✅ 46 unit tests with mock repositories
- ✅ 100% type hints
- ✅ Result monad pattern throughout

---

## 📅 Timeline Recommendation

### This Week (Phase 0.4)

**Day 1**: BaseService + TaskService (4-5 hours)
- Morning: BaseService implementation + tests
- Afternoon: TaskService implementation + tests

**Day 2**: Remaining Services (3-4 hours)
- Morning: ProjectService + SprintService
- Afternoon: ActionListService + final tests

### Next Week (Phases 0.5-0.6)

**Days 3-4**: API Endpoints (8-10 hours)
- Task endpoints (10 endpoints)
- Project/Sprint/ActionList endpoints (12 endpoints)
- Dependency injection
- Error middleware

**Day 5**: Infrastructure (4-5 hours)
- Structured logging
- Health checks
- Database migrations

### Following Week (Phases 0.7-0.9)

**Days 6-7**: Testing (6-8 hours)
- Integration tests (E2E)
- Coverage analysis
- Performance testing

**Day 8**: Documentation & Polish (2-3 hours)
- API documentation
- README updates
- Final cleanup

**Total Timeline**: ~3 weeks at 2-3 hours per day

---

## 🎯 Decision Points

### Option 1: Complete Phase 0.4 Now (Recommended)

**Pros**:
- Maintains momentum
- Completes business logic layer
- Enables rapid API implementation
- Foundation for testing

**Cons**:
- Requires 3-4 hours of focused work

**Recommendation**: ✅ **Proceed with Phase 0.4**

### Option 2: Skip to API Endpoints

**Pros**:
- Get visible progress faster (working endpoints)
- Immediate testing capability

**Cons**:
- Business logic in endpoint handlers (anti-pattern)
- Harder to test
- Duplicate code across endpoints
- Poor separation of concerns

**Recommendation**: ❌ **Not recommended**

### Option 3: Pause for Review

**Pros**:
- Consolidate understanding
- Plan ahead
- Review code quality

**Cons**:
- Loses momentum
- Delays completion

**Recommendation**: 🤔 **Only if uncertain about approach**

---

## 📋 Checklist Before Starting

- [x] Phases 0.1-0.3 complete
- [x] ORM models ready
- [x] Repositories ready
- [x] Schemas ready
- [x] Test infrastructure ready
- [ ] **Decision made to proceed**
- [ ] Create service directory structure
- [ ] Begin BaseService implementation

---

## 🚀 Quick Start Command

```bash
# Create service directory
mkdir -p TaskMan-v2/backend-api/src/taskman_api/services

# Create __init__.py
touch TaskMan-v2/backend-api/src/taskman_api/services/__init__.py

# Create test directory
mkdir -p TaskMan-v2/backend-api/tests/unit/services

# Ready to begin BaseService implementation
```

---

**"Service Layer: The Bridge Between Data and APIs"**
