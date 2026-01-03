## Plan: CF-130 TaskMan-v2 Test Suite Implementation

**TL;DR**: Build comprehensive unit tests for TaskMan-v2 services (`TaskServiceV2`, `EnhancedTaskService`, `TaskManService`) and integration tests for the MCP server tool handlers. Research existing patterns, fixtures, and installed dependencies first to maximize reuse and avoid duplication.

### Phase 0: Internal Research (Subagent Tasks)

#### Research Task 1: Existing Test Infrastructure
- Search for existing `conftest.py` files and catalog reusable fixtures (`temp_db`, `task_factory`, `mock_*`)
- Identify pytest plugins already installed (`pytest-asyncio`, `pytest-cov`, `pytest-mock`, `pytest-benchmark`)
- Find existing test helpers and assertion utilities in `tests/` directory
- Catalog pytest markers defined in [`pyproject.toml`](pyproject.toml) that should be used

#### Research Task 2: Existing TaskMan/Service Tests
- Search for any existing tests in `tests/taskman*`, `tests/**/taskman*`, `tests/**/mcp*`
- Find tests for similar services (`test_task_repository.py`, `test_*_service.py`) to copy patterns
- Identify if `InMemoryTaskRepository` or similar mocks already exist
- Check for existing Result monad test helpers (`assert_success`, `assert_failure`)

#### Research Task 3: Installed Python Dependencies
- Extract test dependencies from [`pyproject.toml`](pyproject.toml) `[project.optional-dependencies]` or `[tool.poetry.group.dev.dependencies]`
- Verify `pytest-asyncio` is installed for async MCP handler testing
- Check for `faker`, `factory-boy`, or similar for test data generation
- Identify mocking libraries available (`unittest.mock`, `pytest-mock`, `responses`)

#### Research Task 4: MCP & VS Code Tool Opportunities
- Identify MCP tools that could assist with test generation or validation
- Check for VS Code tasks in `.vscode/tasks.json` for running tests
- Look for existing test coverage reporting setup
- Find any test-related scripts in `build/` or `scripts/`

### Phase 1: Test Infrastructure Setup
1. Create [`tests/taskman_v2/__init__.py`](tests/taskman_v2/__init__.py) and directory structure with subdirectories for `unit/services/`, `unit/models/`, `mcp/`
2. Create [`tests/taskman_v2/conftest.py`](tests/taskman_v2/conftest.py):
   - Import/extend existing fixtures from parent conftest files
   - Add TaskMan-specific factories (`task_entity_factory`, `task_dto_factory`, `sprint_factory`, `project_factory`)
   - Add Result monad helpers (`assert_success()`, `assert_failure(error_contains=)`)
   - Configure in-memory repository fixtures for fast unit tests
   - Configure SQLite temp database fixtures for integration tests

### Phase 2: Unit Tests - Core Services
3. Create [`tests/taskman_v2/unit/services/test_task_service_v2.py`](tests/taskman_v2/unit/services/test_task_service_v2.py):
   - Test CRUD operations: `create_task`, `get_task`, `get_task_or_none`, `update_task`, `delete_task`
   - Test status transitions: `change_status`, `start_task`, `complete_task`, `block_task`, `cancel_task`
   - Test listing/filtering: `list_tasks`, `get_active_tasks`, `get_blocked_tasks`, `get_completed_tasks`
   - Test error handling: `TaskNotFoundError` propagation, invalid status transitions
   - Use `@pytest.mark.unit` and `@pytest.mark.services` markers

4. Create [`tests/taskman_v2/unit/services/test_enhanced_task_service.py`](tests/taskman_v2/unit/services/test_enhanced_task_service.py):
   - Test time logging: `log_time` with hours validation
   - Test bulk operations: `bulk_update_status`, `bulk_assign_sprint`
   - Test assignments: `assign_to_user`, `assign_to_sprint`, `unassign`
   - Test queries: `get_sprint_tasks`, `get_project_tasks`, `get_overdue_tasks`
   - Test statistics: `get_task_statistics`

5. Create [`tests/taskman_v2/unit/services/test_project_service.py`](tests/taskman_v2/unit/services/test_project_service.py):
   - Test CRUD: `create_project`, `get_project`, `get_project_by_uuid`, `get_project_by_name`, `update_project`, `delete_project`

6. Create [`tests/taskman_v2/unit/services/test_sprint_service.py`](tests/taskman_v2/unit/services/test_sprint_service.py):
   - Test CRUD: `create_sprint`, `get_sprint`, `get_sprint_by_uuid`, `update_sprint`

### Phase 3: Schema & Model Validation Tests
7. Create [`tests/taskman_v2/unit/models/test_schemas.py`](tests/taskman_v2/unit/models/test_schemas.py):
   - Test Pydantic schema validation for `CreateTaskInput`, `UpdateTaskInput`, `ListTasksInput`
   - Test required field enforcement
   - Test regex patterns (`^T-` for task_id, `^S-` for sprint_id, `^P-` for project_id)
   - Test field constraints (priority 1-5, limit 1-100)

### Phase 4: MCP Server Tests
8. Create [`tests/taskman_v2/mcp/test_tool_handlers.py`](tests/taskman_v2/mcp/test_tool_handlers.py):
   - Test each MCP tool: `create_task`, `get_task`, `list_tasks`, `update_task`, `complete_task`, `delete_task`
   - Test input validation at MCP layer
   - Test error response formatting
   - Use `@pytest.mark.asyncio` for async handlers
   - Mock `AppContext` with in-memory service

9. Create [`tests/taskman_v2/mcp/test_mcp_lifespan.py`](tests/taskman_v2/mcp/test_mcp_lifespan.py):
   - Test MCP server startup/shutdown lifecycle
   - Verify `@asynccontextmanager` lifespan proper initialization
   - Test graceful shutdown behavior

### Phase 5: Integration with cf_core
10. Create [`tests/cf_core/unit/services/test_taskman_service.py`](tests/cf_core/unit/services/test_taskman_service.py):
    - Test `TaskManService` wrapper that bridges cf_core to TaskMan-v2
    - Test Result monad propagation through service chain
    - Test repository exception wrapping

### Phase 6: Error Propagation & Edge Cases
11. Add error propagation tests across all test files:
    - Verify repository exceptions wrap properly in `Result.failure()`
    - Test error messages surface correctly through service → MCP tool chain
    - Test concurrent access scenarios (if applicable)
    - Test boundary conditions (empty lists, max limits, null fields)

### Phase 7: Validation & Coverage
12. Run full test suite with coverage reporting:
    - Execute `pytest tests/taskman_v2/ --cov=python/src/taskman_v2 --cov-report=html`
    - Verify ≥70% unit coverage target met
    - Identify and fill coverage gaps
    - Run VS Code test tasks to validate integration
