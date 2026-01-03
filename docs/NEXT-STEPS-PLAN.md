# ContextForge Next Steps Plan

> Comprehensive roadmap for Phase Tracking integration and system alignment
> Generated: 2025-12-28

## Executive Summary

The cf_core models now include PhaseTracking (research, planning, implementation, testing phases) added to Task, Sprint, and Project entities. This plan outlines the work needed to integrate these models into the full stack: backend API, MCP server, database, and frontend.

---

## Current State

### Completed Work
- [x] PhaseTracking Pydantic model with 4 phases (cf_core/models/phase_tracking.py)
- [x] Phase fields added to Task, Sprint, Project models
- [x] TaskStatus updated to 8 states (added `active`)
- [x] Status enum documentation (Unified v1.3.0)
- [x] Core Skills documentation in CLAUDE.md
- [x] 118 e2e tests passing
- [x] **Entity-appropriate phases implemented** (2025-12-28):
  - Task: 4 phases (research, planning, implementation, testing)
  - Sprint: 2 phases (planning, implementation) - sprints organize work execution
  - Project: 2 phases (research, planning) - strategic containers
- [x] **Pydantic schemas updated** with phases and pending/blocked_reason fields
- [x] **SQLAlchemy models updated** with phases JSONB and status reason columns
- [x] **Alembic migration created** (934f38a4fc73) for phases and status fields
- [x] **Unified v1.2.0 status enums aligned** - Sprint/Project now use 8-state lifecycle

### Architecture Layers

| Layer | Location | Status |
|-------|----------|--------|
| Domain Models | cf_core/models/ | ✅ Complete |
| SQLAlchemy Models | TaskMan-v2/backend-api/src/taskman_api/db/models/ | ✅ Complete (phases + status fields) |
| Pydantic Schemas | TaskMan-v2/backend-api/src/taskman_api/schemas/ | ✅ Complete (phases + status fields) |
| Database Migration | TaskMan-v2/backend-api/alembic/versions/ | ✅ Created (934f38a4fc73) |
| Repositories | TaskMan-v2/backend-api/src/taskman_api/db/repositories/ | ⚠️ Missing phase methods |
| Services | TaskMan-v2/backend-api/src/taskman_api/services/ | ⚠️ Missing PhaseService |
| API Endpoints | TaskMan-v2/backend-api/src/taskman_api/api/v1/ | ⚠️ Missing phase endpoints |
| MCP Tools | TaskMan-v2/mcp-server-ts/src/ | ⚠️ Missing phase tools |
| Frontend | TaskMan-v2/frontend/src/ | ⚠️ No phase UI |

---

## Model Alignment Analysis (2025-12-28)

### cf_core vs Backend Comparison

#### TaskStatus Enum
| cf_core (8 states) | Backend (7 states) | Gap |
|-------------------|-------------------|-----|
| new | new | ✅ |
| ready | ready | ✅ |
| **active** | ❌ missing | ⚠️ **ADD** |
| in_progress | in_progress | ✅ |
| blocked | blocked | ✅ |
| review | review | ✅ |
| done | done | ✅ |
| dropped | dropped | ✅ |

#### Sprint/Project Status
| cf_core (8 states) | Backend | Gap |
|-------------------|---------|-----|
| new, pending, assigned, active, in_progress, blocked, completed, cancelled | discovery, active, paused, closed | ⚠️ **Major redesign needed** |

#### Missing Fields in Backend Models
| Field | cf_core Location | Backend Status |
|-------|------------------|----------------|
| `phases: PhaseTracking` | Task, Sprint, Project | ❌ Missing |
| `pending_reason: str` | Task, Sprint, Project | ❌ Missing |
| `blocked_reason: str` | Task (already has blockers) | Partial |

### Priority Actions
1. **Add `active` to TaskStatus enum** - TaskMan-v2/backend-api/src/taskman_api/core/enums.py:9-20
2. **Add `phases` JSONB column** - All 3 entity tables
3. **Align Sprint/Project status enums** - Significant schema change

---

## Epic 1: Foundation Alignment ✅ COMPLETE

**Priority:** Critical | **Effort:** 2-3 days | **Dependencies:** None
**Completed:** 2025-12-28

### Objective
Align cf_core Pydantic models with backend SQLAlchemy models and prepare database schema.

### Tasks

#### 1.1 Audit Model Alignment ✅
- [x] Compare cf_core/models/task.py with backend-api/src/models/task.py
- [x] Compare cf_core/models/sprint.py with backend-api/src/models/sprint.py
- [x] Compare cf_core/models/project.py with backend-api/src/models/project.py
- [x] Document discrepancies - Entity-appropriate phases designed

#### 1.2 Update Database Enums ✅
- [x] TaskStatus already has 7 states (new, ready, in_progress, blocked, review, done, dropped)
- [x] SprintStatus updated to 8 states (Unified v1.2.0)
- [x] ProjectStatus updated to 8 states (Unified v1.2.0)
- [x] PhaseStatus enum added (not_started, in_progress, completed, skipped, blocked)

#### 1.3 Add Phase Tracking Schema ✅
- [x] Design phase tracking storage strategy - **Embedded JSONB chosen**
- [x] Create Alembic migration (934f38a4fc73) adding `phases` JSONB to all entities
- [x] Add `pending_reason` and `blocked_reason` VARCHAR(500) to Sprint and Project
- [x] Add default values for existing records with entity-appropriate phases

### Deliverables ✅
- ~~Model alignment report~~ Entity-appropriate phases documented
- 1 consolidated Alembic migration (934f38a4fc73)
- Updated SQLAlchemy models with phases, pending_reason, blocked_reason
- Updated Pydantic schemas with phases field
- Unit tests updated for Unified v1.2.0 enums

### Files Modified
```
backend-api/src/taskman_api/db/models/task.py ✅
backend-api/src/taskman_api/db/models/sprint.py ✅
backend-api/src/taskman_api/db/models/project.py ✅
backend-api/src/taskman_api/schemas/task.py ✅
backend-api/src/taskman_api/schemas/sprint.py ✅
backend-api/src/taskman_api/schemas/project.py ✅
backend-api/alembic/versions/20251228_1548_934f38a4fc73_add_phases_and_status_fields.py ✅
```

---

## Epic 2: Phase Tracking Backend ✅ COMPLETE

**Priority:** High | **Effort:** 3-4 days | **Dependencies:** Epic 1 ✅
**Started:** 2025-12-28 | **Completed:** 2025-12-28

### Objective
Implement repository and service layers for phase tracking operations.

### Tasks

#### 2.1 Repository Layer ✅ COMPLETE
- [x] Add phase query methods to TaskRepository
  - `find_by_phase_status(phase: str, status: PhaseStatus)` - JSONB query
  - `find_with_blocked_phase()` - Find tasks with any blocked phase
  - `find_by_current_phase(phase: str)` - Find tasks in in_progress phase
  - `find_with_completed_phases(min_completed)` - Find tasks with N+ completed phases
- [x] Add phase query methods to SprintRepository
  - `find_by_phase_status()`, `find_with_blocked_phase()`, `find_by_current_phase()`
- [x] Add phase query methods to ProjectRepository
  - `find_by_phase_status()`, `find_with_blocked_phase()`, `find_by_current_phase()`
- [x] Entity-appropriate phase constants defined:
  - TASK_PHASES = ["research", "planning", "implementation", "testing"]
  - SPRINT_PHASES = ["planning", "implementation"]
  - PROJECT_PHASES = ["research", "planning"]

#### 2.2 Service Layer ✅ COMPLETE
- [x] Create PhaseService class
  - `get_phases(entity_id, entity_type)` - Get all phases
  - `get_phase_status(entity_id, entity_type, phase_name)` - Get specific phase status
  - `update_phase(entity_id, entity_type, phase_name, updates)` - Update phase data
  - `set_phase_status(entity_id, entity_type, phase_name, status)` - Set phase status with validation
  - `advance_phase(entity_id, entity_type)` - Advance to next phase
  - `block_phase(entity_id, entity_type, phase_name, reason)` - Block a phase
  - `unblock_phase(entity_id, entity_type, phase_name)` - Unblock a phase
  - `skip_phase(entity_id, entity_type, phase_name, reason)` - Skip a phase
  - `get_phase_summary(entity_id, entity_type)` - Get phase summary with metrics
  - `find_entities_in_phase(entity_type, phase_name, status)` - Find entities in phase
  - `find_blocked_entities(entity_type)` - Find all blocked entities
- [x] Implement phase transition state machine
  - NOT_STARTED → IN_PROGRESS, SKIPPED
  - IN_PROGRESS → COMPLETED, BLOCKED, SKIPPED
  - BLOCKED → IN_PROGRESS, SKIPPED
  - COMPLETED, SKIPPED → (terminal states)
- [x] 33 unit tests for PhaseService (all passing)

#### 2.3 Integration with Existing Services ✅ COMPLETE
- [x] Update TaskService with phase methods:
  - `get_by_phase_status()`, `get_with_blocked_phases()`, `get_by_current_phase()`
- [x] Update SprintService with phase methods:
  - `get_by_phase_status()`, `get_with_blocked_phases()`, `get_by_current_phase()`
- [x] Update ProjectService with phase methods:
  - `get_by_phase_status()`, `get_with_blocked_phases()`, `get_by_current_phase()`

### Deliverables ✅ ALL COMPLETE
- [x] PhaseService with full lifecycle methods (177 lines, 82% coverage)
- [x] Enhanced repositories with phase queries (744 lines added across 6 files)
- [x] Phase transition validation logic
- [x] Service layer phase query methods

### Files Created/Modified
```
backend-api/src/taskman_api/services/phase_service.py ✅ (NEW - 177 lines)
backend-api/src/taskman_api/services/__init__.py ✅ (updated exports)
backend-api/tests/unit/services/test_phase_service.py ✅ (NEW - 33 tests)
backend-api/src/taskman_api/db/repositories/task_repository.py ✅ (+184 lines)
backend-api/src/taskman_api/db/repositories/sprint_repository.py ✅ (+121 lines)
backend-api/src/taskman_api/db/repositories/project_repository.py ✅ (+121 lines)
backend-api/src/taskman_api/services/task_service.py ✅ (+107 lines)
backend-api/src/taskman_api/services/sprint_service.py ✅ (+107 lines)
backend-api/src/taskman_api/services/project_service.py ✅ (+110 lines)
```

---

## Epic 3: API Layer ✅ COMPLETE

**Priority:** High | **Effort:** 2-3 days | **Dependencies:** Epic 2 ✅
**Started:** 2025-12-28 | **Completed:** 2025-12-28

### Objective
Expose phase tracking functionality via FastAPI endpoints.

### Tasks

#### 3.1 Phase Management Endpoints ✅ COMPLETE
- [x] `GET /api/v1/phases/{entity_type}/{id}` - Get entity phase status
- [x] `GET /api/v1/phases/{entity_type}/{id}/summary` - Get phase summary with metrics
- [x] `PATCH /api/v1/phases/{entity_type}/{id}/{phase}` - Update specific phase
- [x] `POST /api/v1/phases/{entity_type}/{id}/advance` - Advance to next phase
- [x] `POST /api/v1/phases/{entity_type}/{id}/{phase}/block` - Block a phase
- [x] `POST /api/v1/phases/{entity_type}/{id}/{phase}/unblock` - Unblock a phase
- [x] `POST /api/v1/phases/{entity_type}/{id}/{phase}/skip` - Skip a phase
- [x] `POST /api/v1/phases/{entity_type}/{id}/{phase}/complete` - Complete a phase
- [x] `POST /api/v1/phases/{entity_type}/{id}/{phase}/start` - Start a phase

#### 3.2 Phase Analytics Endpoints ✅ COMPLETE
- [x] `GET /api/v1/phases/{entity_type}/search` - Find entities in specific phase
- [x] `GET /api/v1/phases/blocked` - All blocked entities across all types
- [x] `GET /api/v1/phases/{entity_type}/analytics` - Phase analytics with metrics

#### 3.3 Update Existing Endpoints ✅ N/A
- [x] `phases` already included in Task response schema (from Epic 1)
- [x] `phases` already included in Sprint response schema (from Epic 1)
- [x] `phases` already included in Project response schema (from Epic 1)

#### 3.4 Schema Updates ✅ COMPLETE
- [x] Created `PhaseUpdateRequest` - Status and custom field updates
- [x] Created `PhaseStatusRequest` - Status-only changes
- [x] Created `BlockPhaseRequest` - Block phase with reason
- [x] Created `SkipPhaseRequest` - Skip phase with reason
- [x] Created `PhaseResponse` - Single phase response
- [x] Created `PhasesResponse` - All phases for an entity
- [x] Created `PhaseSummaryResponse` - Phase summary with metrics
- [x] Created `EntityInPhaseResponse` - Entity search result
- [x] Created `BlockedEntityResponse` - Blocked entity summary
- [x] Created `PhaseAnalyticsResponse` - Analytics metrics

### Deliverables ✅ ALL COMPLETE
- [x] 12 new API endpoints in phases router
- [x] 10 new Pydantic schemas for phase operations
- [x] PhaseService dependency injection in deps.py
- [x] Phases router registered in main.py
- [x] 25 unit tests for API endpoints (all passing)

### Files Created/Modified
```
backend-api/src/taskman_api/api/v1/phases.py ✅ (NEW - 144 lines)
backend-api/src/taskman_api/schemas/phase.py ✅ (NEW - 194 lines)
backend-api/src/taskman_api/schemas/__init__.py ✅ (updated exports)
backend-api/src/taskman_api/api/deps.py ✅ (added get_phase_service)
backend-api/src/taskman_api/main.py ✅ (registered phases router)
backend-api/tests/unit/api/__init__.py ✅ (NEW)
backend-api/tests/unit/api/test_phases_api.py ✅ (NEW - 25 tests)
```

---

## Epic 4: MCP Server

**Priority:** Medium | **Effort:** 3-4 days | **Dependencies:** Epic 3

### Objective
Add phase tracking tools to the TypeScript MCP server.

### Tasks

#### 4.1 TypeScript Types
- [ ] Create PhaseTracking interfaces matching cf_core models
- [ ] Create PhaseStatus, ResearchPhase, PlanningPhase, etc. types
- [ ] Add phase fields to Task, Sprint, Project types

#### 4.2 Phase Management Tools
- [ ] `get_entity_phases` - Get phase status for any entity
- [ ] `update_phase` - Update a specific phase
- [ ] `advance_phase` - Move to next phase
- [ ] `block_phase` - Mark phase as blocked
- [ ] `unblock_phase` - Clear phase block

#### 4.3 Phase Query Tools
- [ ] `find_by_phase` - Find entities in specific phase
- [ ] `find_blocked_phases` - Find all blocked entities
- [ ] `get_phase_metrics` - Get completion statistics

#### 4.4 Tool Documentation
- [ ] Add tool descriptions and examples
- [ ] Update MCP tool manifest

### Deliverables
- 7-8 new MCP tools
- TypeScript type definitions
- Tool documentation

### Files to Create/Modify
```
mcp-server-ts/src/types/phase.ts (NEW)
mcp-server-ts/src/tools/phase-tools.ts (NEW)
mcp-server-ts/src/types/task.ts
mcp-server-ts/src/types/sprint.ts
mcp-server-ts/src/types/project.ts
mcp-server-ts/src/index.ts
```

---

## Epic 5: Testing

**Priority:** High | **Effort:** 2-3 days | **Dependencies:** Epics 2-4

### Objective
Comprehensive test coverage for phase tracking functionality.

### Tasks

#### 5.1 Unit Tests
- [ ] PhaseService unit tests
  - Phase transition validation
  - Advance logic
  - Block/unblock logic
- [ ] Repository phase query tests
- [ ] Schema validation tests

#### 5.2 Integration Tests
- [ ] Phase API endpoint tests
- [ ] Database migration tests
- [ ] Phase persistence tests

#### 5.3 E2E Tests
- [ ] Full phase lifecycle workflow
- [ ] Multi-entity phase coordination
- [ ] Error handling scenarios

#### 5.4 Property-Based Tests
- [ ] Phase state machine invariants
- [ ] Transition rule compliance

### Deliverables
- 30-50 new tests
- >80% coverage for phase code
- Test fixtures and factories

### Files to Create
```
backend-api/tests/unit/services/test_phase_service.py (NEW)
backend-api/tests/unit/repositories/test_phase_queries.py (NEW)
backend-api/tests/integration/api/test_phases_api.py (NEW)
backend-api/tests/e2e/test_phase_lifecycle.py (NEW)
mcp-server-ts/tests/tools/phase-tools.test.ts (NEW)
```

---

## Epic 6: Documentation & Observability

**Priority:** Medium | **Effort:** 1-2 days | **Dependencies:** Epics 3-4

### Objective
Document phase tracking and add observability.

### Tasks

#### 6.1 API Documentation
- [ ] Update docs/10-API-Reference.md with phase endpoints
- [ ] Add phase workflow diagrams (Mermaid)
- [ ] Document phase transition rules

#### 6.2 MCP Documentation
- [ ] Document phase MCP tools
- [ ] Add usage examples
- [ ] Update tool manifest documentation

#### 6.3 Observability
- [ ] Add phase transition metrics (Prometheus)
- [ ] Add phase duration tracking
- [ ] Add phase completion rate metrics
- [ ] Update Grafana dashboard (if exists)

#### 6.4 Architecture Documentation
- [ ] Add phase tracking to architecture diagrams
- [ ] Document data flow for phase operations

### Deliverables
- Updated API documentation
- Phase workflow diagrams
- Prometheus metrics
- Architecture diagrams

### Files to Create/Modify
```
docs/10-API-Reference.md
docs/PHASE-TRACKING.md (NEW)
docs/diagrams/phase-workflow.md (NEW)
backend-api/src/metrics/phase_metrics.py (NEW)
```

---

## Implementation Checklist

### Pre-Implementation
- [x] Review and approve this plan
- [x] Set up feature branch: `infallible-kalam` (worktree)
- [x] Verify test environment is working

### Epic 1: Foundation (Critical) ✅ COMPLETE
- [x] 1.1 Model alignment audit complete - Entity-appropriate phases designed
- [x] 1.2 Database enum migrations created - Unified v1.2.0 aligned
- [x] 1.3 Phase tracking schema migrations created - 934f38a4fc73
- [x] All migrations tested locally - Unit tests pass (94 pass, 7 pre-existing errors)

### Epic 2: Backend (High) ✅ COMPLETE
- [x] 2.1 Repository phase methods implemented - JSONB queries for all 3 entities
- [x] 2.2 PhaseService created with lifecycle methods - 33 tests passing
- [x] 2.3 Existing services updated - phase query methods added to all services
- [x] Unit tests passing - 97 pass, 7 pre-existing ActionListService errors

### Epic 3: API (High)
- [ ] 3.1 Phase management endpoints created
- [ ] 3.2 Analytics endpoints created
- [ ] 3.3 Existing endpoints updated
- [ ] 3.4 Schemas updated
- [ ] Integration tests passing

### Epic 4: MCP (Medium)
- [ ] 4.1 TypeScript types created
- [ ] 4.2 Phase management tools created
- [ ] 4.3 Phase query tools created
- [ ] 4.4 Tool documentation complete

### Epic 5: Testing (High)
- [ ] 5.1 Unit tests complete
- [ ] 5.2 Integration tests complete
- [ ] 5.3 E2E tests complete
- [ ] Coverage target met (>80%)

### Epic 6: Documentation (Medium)
- [ ] 6.1 API documentation updated
- [ ] 6.2 MCP documentation updated
- [ ] 6.3 Observability metrics added
- [ ] 6.4 Architecture diagrams updated

### Post-Implementation
- [ ] All tests passing (target: 150+ tests)
- [ ] Code review complete
- [ ] Documentation reviewed
- [ ] Merge to main branch
- [ ] Tag release

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Schema migration breaks existing data | Test migrations on copy of prod data first |
| Phase transitions too restrictive | Allow "skipped" status for flexibility |
| Performance degradation with JSONB | Add GIN indexes on phase fields |
| MCP/Backend type drift | Generate types from shared schema |
| Test coverage gaps | Mandate tests before merging |

---

## Decision Log

| Decision | Rationale | Date |
|----------|-----------|------|
| Embedded JSONB over separate tables | Simpler queries, matches cf_core design | 2025-12-28 |
| 4-phase model (R/P/I/T) | Covers standard dev lifecycle | 2025-12-28 |
| PhaseStatus includes "skipped" | Flexibility for different workflows | 2025-12-28 |
| 8-state TaskStatus (added 'active') | Distinguishes assignment from work start | 2025-12-28 |

---

## Estimated Timeline

| Epic | Effort | Parallel? |
|------|--------|-----------|
| Epic 1: Foundation | 2-3 days | No (blocks others) |
| Epic 2: Backend | 3-4 days | No (blocks API/MCP) |
| Epic 3: API | 2-3 days | Yes (with Epic 4) |
| Epic 4: MCP | 3-4 days | Yes (with Epic 3) |
| Epic 5: Testing | 2-3 days | Partial |
| Epic 6: Docs | 1-2 days | Yes |

**Total Estimated Effort:** 10-15 working days

---

## Quick Start

To begin implementation:

```bash
# Create feature branch
git checkout -b feature/phase-tracking-integration

# Start with Epic 1.1 - Model Alignment Audit
# Compare models:
diff cf_core/models/task.py backend-api/src/models/task.py
```

---

---

## Immediate Action Items ✅ COMPLETED

All foundation items have been executed:

### ✅ 1. Backend Enums Updated
- TaskStatus: 7 states (new, ready, in_progress, blocked, review, done, dropped)
- SprintStatus: 8 states (Unified v1.2.0)
- ProjectStatus: 8 states (Unified v1.2.0)
- PhaseStatus: 5 states (not_started, in_progress, completed, skipped, blocked)

### ✅ 2. Entity-Appropriate Phases Implemented
- Task: 4 phases (research, planning, implementation, testing)
- Sprint: 2 phases (planning, implementation)
- Project: 2 phases (research, planning)

### ✅ 3. SQLAlchemy Models Updated
- `phases` JSONB column added to Task, Sprint, Project models
- `pending_reason` and `blocked_reason` added to Sprint, Project models

### ✅ 4. Alembic Migration Created
- Migration ID: `934f38a4fc73`
- File: `20251228_1548_934f38a4fc73_add_phases_and_status_fields.py`

### ✅ 5. Tests Updated
- Schema unit tests pass (94 tests)
- Fixtures updated with entity-appropriate phases

---

## Next Steps (Epic 3: API Layer)

| Item | Status | Next Step |
|------|--------|-----------|
| Repository phase methods | ✅ Complete | JSONB queries implemented |
| PhaseService implementation | ✅ Complete | 33 tests passing |
| Service layer integration | ✅ Complete | Phase methods added to all services |
| API endpoints | 🔜 Ready to start | Create phase management endpoints |
| MCP tools | ⏳ Blocked by Epic 3 | Complete API first |
| Frontend UI | ⏳ Blocked by Epic 3 | Complete API first |

---

*"Trust Nothing, Verify Everything. Execute Immediately, Clean Thoroughly."*
