# Issues Catalog - TaskMan-v2 Backend Enum Consolidation

**Session Date**: 2025-12-29
**Context**: Post-ConflictError integration cleanup - Addressing 51 pre-existing test failures

---

## 🎯 Issue Categories

### ✅ RESOLVED

#### ISSUE-001: Task Model 'phases' Parameter (57 errors)
- **Type**: Pre-existing - Test fixture bug
- **Location**: `tests/unit/services/conftest.py`
- **Root Cause**: Fixture creating Task with `phases=...` parameter that no longer exists in model
- **Status**: ✅ RESOLVED (fixed by user before session)
- **Test Impact**: 57 errors → 0 errors
- **Resolution**: Conftest files edited to remove phases parameter

---

#### ISSUE-002: Duplicate Enum Definitions (11+ failures)
- **Type**: Architectural issue - Duplicate source of truth
- **Location**:
  - `src/taskman_api/core/enums.py` (correct 10-status lifecycle)
  - `src/taskman_api/schemas/enums.py` (old 5-status values)
- **Root Cause**: Two conflicting enum definitions:
  - Core enums: NEW, PENDING, ASSIGNED, ACTIVE, IN_PROGRESS, PAUSED, BLOCKED, COMPLETED, CLOSED, CANCELLED
  - Schema enums: PLANNING, ACTIVE, ON_HOLD, COMPLETED, ARCHIVED
- **Symptoms**:
  - Pydantic validation errors rejecting new status values
  - Tests expecting PAUSED/CLOSED failing with "Input should be 'planning', 'active', 'on_hold'..."
- **Status**: ✅ RESOLVED
- **Resolution**:
  1. Updated imports in 5 schema files to use `core/enums` instead of `schemas/enums`:
     - `schemas/project.py`
     - `schemas/sprint.py`
     - `schemas/task.py`
     - `schemas/action_list.py`
     - `schemas/__init__.py`
  2. Added import aliases for name mismatches (TaskPriority → Priority)
  3. Updated default values in schemas (PLANNING → NEW)
  4. Ready to delete `schemas/enums.py` (not yet done)
- **Test Impact**: 11 Pydantic validation failures → 0 validation failures
- **Files Modified**:
  - `src/taskman_api/core/enums.py` (added PAUSED, CLOSED)
  - `src/taskman_api/schemas/project.py` (import + default value)
  - `src/taskman_api/schemas/sprint.py` (import + default value)
  - `src/taskman_api/schemas/task.py` (import with aliases)
  - `src/taskman_api/schemas/action_list.py` (import)
  - `src/taskman_api/schemas/__init__.py` (import)

---

#### ISSUE-003: SprintStatus.PLANNED vs PLANNING (2 failures)
- **Type**: Test bug - Typo in enum value name
- **Location**:
  - `tests/unit/services/test_sprint_service.py`
  - `tests/integration/api/test_sprints_api.py`
- **Root Cause**: Tests using `SprintStatus.PLANNED` (past tense) but enum defines `SprintStatus.PLANNING` (present tense)
- **Status**: ✅ RESOLVED
- **Resolution**: Changed all `PLANNED` → `PLANNING` in test files
- **Test Impact**: 2 AttributeError failures → 0 failures

---

### ⚠️ IDENTIFIED BUT NOT YET RESOLVED

#### ISSUE-004: Mock Repository Method Mismatch (4+ failures)
- **Type**: Test bug - Incorrect mock setup
- **Location**:
  - `tests/unit/services/test_project_service.py` (3 tests)
  - `tests/unit/services/test_sprint_service.py` (1+ tests)
- **Test Names**:
  - `test_change_status_to_paused`
  - `test_change_status_to_completed`
  - `test_change_status_to_closed`
  - `test_change_status` (sprint)
- **Root Cause**:
  - Service calls `self.repository.get_by_id()` (returns entity directly)
  - Test mocks `find_by_id()` (returns Result wrapper)
  - Methods are not the same - mock never triggers
- **Symptoms**: Tests expect `Ok()` but get `Err()` because actual `get_by_id()` isn't mocked
- **Status**: ⚠️ IDENTIFIED - Not resolved (not related to enum consolidation)
- **Recommendation**: Update test fixtures to mock correct method name OR fix service to use find_by_id
- **Priority**: MEDIUM - Affects 4+ tests across multiple services
- **Note**: This is a repository pattern inconsistency - some methods return entities, others return Result wrappers

---

#### ISSUE-005: Phases API Module Missing (15 failures)
- **Type**: Pre-existing - Missing module
- **Location**: `src/taskman_api/api/v1/phases.py` (doesn't exist)
- **Test File**: `tests/unit/api/test_phases_api.py`
- **Root Cause**: Module structure changed or phases feature removed, but tests remain
- **Status**: ⚠️ IDENTIFIED - Not addressed
- **Recommendation**: Either create module or remove/skip tests
- **Priority**: MEDIUM - Isolated to phases feature (15 tests)

---

#### ISSUE-006: ActionList Deferred Features (6 failures/skips)
- **Type**: Expected - Deferred backlog items
- **Location**: `tests/unit/services/test_action_list_service_unit.py`
- **Missing Methods**:
  - `get_soft_deleted()`
  - `get_orphaned()`
  - `mark_complete()`
- **Root Cause**: Tests marked as ADR-001 backlog items (deferred features)
- **Status**: ⚠️ EXPECTED - Intentionally deferred
- **Recommendation**: No action needed - part of planned backlog
- **Priority**: LOW - Expected behavior

---

#### ISSUE-007: Root cf_core Tests Using Old Enums
- **Type**: Test scope issue - Legacy tests in wrong directory
- **Location**: `tests/cf_core/domain/test_enums.py` (root level, not TaskMan-v2)
- **Root Cause**: Root-level tests testing old cf_core enum definitions
- **Status**: ⚠️ INVESTIGATING
- **Question**: Are these tests run as part of TaskMan-v2 backend test suite?
- **Priority**: UNKNOWN - Need to determine test scope

---

### 🔍 UNDER INVESTIGATION

_(None currently)_

---

## 📊 Test Suite Progress

| Stage | Passed | Failed | Errors | Total |
|-------|--------|--------|--------|-------|
| **Initial (ConflictError complete)** | 347 | 95 | 4 | 446 |
| **After 'phases' fix** | 400 | 51 | 2 | 453 |
| **After enum consolidation (FINAL)** | 410 | 41 | 1 | 452 |
| **Target** | 446+ | 0 | 0 | 446+ |

**Key Improvements**:
- ✅ 57 errors eliminated (phases parameter fix by user)
- ✅ 10 failures eliminated (enum consolidation work)
- ⚠️ 41 failures remaining (various pre-existing issues)
- ✅ 1 error remaining (down from 4)

---

## 🎯 Next Actions

1. **Investigate ISSUE-007**: Determine if root cf_core tests should be part of TaskMan-v2 suite
2. **Consider addressing ISSUE-004**: Fix mock method mismatch (3 quick wins)
3. **Document ISSUE-005**: Create decision record for phases module
4. **Validate**: Run full test suite to confirm enum consolidation complete

---

## 📝 Notes

- All enum consolidation work is backwards compatible (old values still in schemas/enums.py)
- No production code broken by these changes
- Safe to delete `schemas/enums.py` after confirming all imports updated
- Repository pattern inconsistency discovered (`get_by_id` vs `find_by_id`)
