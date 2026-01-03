# Complete Recommendations Checklist

**Created**: 2025-12-29
**Source Documents**: T11 AAR, T12 Production Readiness Report, Pydantic Settings Resolution Plan
**Status**: IN PROGRESS

---

## Quick Stats

| Category | Total | Done | Remaining |
|----------|-------|------|-----------|
| Critical (Blocking) | 2 | 1 | 1 |
| Priority 1 (Before Production) | 6 | 2 | 4 |
| Priority 2 (Sprint Backlog) | 7 | 0 | 7 |
| Priority 3 (Tech Debt) | 5 | 0 | 5 |
| **Total** | **20** | **3** | **17** |

---

## 🔴 Critical (Blocking Deployment)

### From T11 AAR

- [x] **C1**: Fix router-service contract mismatch in `action_lists.py`
  - **Status**: ✅ RESOLVED (2025-12-29 04:50 UTC)
  - **Evidence**: Service wrapper methods added (lines 153-328)
  - **Verification**: 9/9 integration tests pass

### From Pydantic Settings Plan

- [ ] **C2**: Resolve Pydantic Settings environment variable conflicts
  - **Issue**: 8/25 config tests failing with `extra_forbidden`
  - **Root Cause**: `.env` uses `DATABASE_URL`, Settings expects `APP_DATABASE__HOST`
  - **Solution**: Implement Option A (migrate `.env` to `APP_` prefix)
  - **Effort**: 45 min

---

## 🟠 Priority 1: Before Production Traffic

### From T12 Report - Code Quality

- [x] **P1-1**: Fix ruff import sorting error (I001)
  - **File**: `action_list_repository.py`
  - **Command**: `ruff check --fix`
  - **Status**: ✅ Fixed (commit ee498b9c)

- [x] **P1-2**: Fix mypy implicit Optional warnings
  - **Files**: `action_list_service.py` lines 158, 161
  - **Fix**: Added `Optional` type hints
  - **Status**: ✅ Fixed (commit ee498b9c)

- [ ] **P1-3**: Add missing router tests to reach 70% coverage
  - **Current**: 30.37% router, 39.80% service
  - **Target**: 70% minimum
  - **Gap**: ~50 additional test cases
  - **Effort**: 2-3 hours

### From Pydantic Settings Plan - Migration

- [ ] **P1-4**: Backup and update `.env` file to `APP_` prefix format
  - **Current**: `DATABASE_URL`, `API_HOST`, `API_PORT`
  - **Target**: `APP_DATABASE__HOST`, `APP_DATABASE__PORT`, etc.
  - **Effort**: 10 min

- [ ] **P1-5**: Create/update `.env.example` with new format
  - **Purpose**: Documentation for developers
  - **Effort**: 5 min

- [ ] **P1-6**: Verify all 25 config tests pass
  - **Command**: `pytest tests/unit/test_config.py -v`
  - **Expected**: 25/25 PASS
  - **Effort**: 5 min

---

## 🟡 Priority 2: Sprint Backlog

### From T12 Report - Code Hygiene

- [ ] **P2-1**: Remove unused arguments (ARG002) in repository
  - **File**: `action_list_repository.py`
  - **Issues**: `priority` (line 45, 84), `context` (line 83)
  - **Options**: Remove or implement functionality
  - **Effort**: 30 min

- [ ] **P2-2**: Fix `repository.search()` kwargs type signature
  - **Issue**: Unexpected kwargs in search() call
  - **Location**: `action_list_service.py:82`
  - **Effort**: 30 min

- [ ] **P2-3**: Add `log_level` field to Settings class (optional)
  - **Current**: LOG_LEVEL in .env but not in Settings
  - **Add**: `log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]`
  - **Effort**: 10 min

### From T11 AAR - Test Infrastructure

- [ ] **P2-4**: Verify all integration tests continue passing
  - **Command**: `pytest tests/integration -v`
  - **Expected**: 12/12 PASS
  - **Effort**: 5 min

- [ ] **P2-5**: Run E2E tests after all fixes
  - **Command**: `pytest tests/e2e -v`
  - **Expected**: 15/15 PASS
  - **Effort**: 5 min

- [ ] **P2-6**: Run performance tests for baseline metrics
  - **Command**: `pytest tests/performance -v`
  - **Expected**: 7/7 PASS
  - **Effort**: 5 min

- [ ] **P2-7**: Run regression tests
  - **Command**: `pytest tests/regression -v`
  - **Expected**: 8/8 PASS
  - **Effort**: 5 min

---

## 🟢 Priority 3: Tech Debt / Future Improvements

### From T12 Report - Quality Targets

- [ ] **P3-1**: Achieve 90% test coverage for ActionList components
  - **Current**: 47.09% overall, 39.80% service
  - **Target**: 90%
  - **Gap**: ~50% improvement needed
  - **Effort**: 8 hours

- [ ] **P3-2**: Implement performance benchmarks (pytest-benchmark)
  - **Purpose**: SLA validation per ADR-023 targets
  - **Targets**: P50<45ms, P95<85ms, P99<120ms
  - **Effort**: 4 hours

- [ ] **P3-3**: Add authorization matrix tests
  - **Purpose**: Validate RBAC enforcement
  - **Requires**: Authenticated API test infrastructure
  - **Effort**: 4 hours

- [ ] **P3-4**: Implement load testing with Locust
  - **Purpose**: Scalability validation
  - **Target**: 100+ concurrent users
  - **Effort**: 8 hours

### From Pydantic Settings Plan - Documentation

- [ ] **P3-5**: Update README.md with new configuration format
  - **Content**: Environment variable reference
  - **Effort**: 15 min

---

## Execution Order (Recommended)

### Phase 1: Config Resolution (45 min)
```
C2 → P1-4 → P1-5 → P1-6
```
Fixes 8 failing config tests.

### Phase 2: Code Quality (1 hour)
```
P2-1 → P2-2 → P2-3
```
Cleans up remaining linting/typing issues.

### Phase 3: Test Verification (30 min)
```
P2-4 → P2-5 → P2-6 → P2-7
```
Validates all test suites pass after fixes.

### Phase 4: Coverage Push (2-3 hours)
```
P1-3
```
Adds router tests to reach 70% minimum.

### Phase 5: Tech Debt (Future Sprints)
```
P3-1 → P3-2 → P3-3 → P3-4 → P3-5
```
Long-term quality improvements.

---

## Commands Reference

### Run All Config Tests
```powershell
cd TaskMan-v2/backend-api
pytest tests/unit/test_config.py -v
```

### Run All Integration Tests
```powershell
pytest tests/integration -v
```

### Run Full Test Suite with Coverage
```powershell
pytest --cov=taskman_api --cov-report=term-missing -v
```

### Fix Ruff Issues
```powershell
ruff check . --fix
```

### Run Mypy Type Check
```powershell
mypy src/taskman_api/
```

### Run Security Scan
```powershell
bandit -r src/taskman_api/
```

---

## Progress Log

| Date | Item | Action | Result |
|------|------|--------|--------|
| 2025-12-29 04:50 | C1 | Router-service fix | ✅ RESOLVED |
| 2025-12-29 05:00 | P1-1 | Ruff --fix | ✅ Fixed |
| 2025-12-29 05:05 | P1-2 | Optional hints | ✅ Fixed |
| | | | |

---

## Approvals

| Phase | Approver | Date | Status |
|-------|----------|------|--------|
| Pydantic Migration | | | ⏳ Pending |
| Production Deploy | | | ⏳ Pending |

---

**Prepared by**: Cognitive Architect
**Last Updated**: 2025-12-29
