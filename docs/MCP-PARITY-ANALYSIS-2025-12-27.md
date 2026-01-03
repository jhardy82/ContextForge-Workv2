# MCP Parity Analysis Report (ST-006)

**Generated**: 2025-12-27
**Source**: Research-Specialist Subagent Analysis
**Status**: COMPLETE ✅

## Executive Summary

- **TypeScript MCP Server**: **38 tools** (corrected from prior estimate of 24)
- **Python MCP Server**: **13 tools** implemented (corrected from prior estimate of 0)
- **Feature Gap**: **25 tools** missing from Python implementation
- **Overall Parity**: **34%**
- **Primary Gap Areas**: Action Lists (0%), Project extensions (0%), Activation (0%)

---

## Feature Gap Matrix

| Tool Category | TypeScript | Python | Gap | Parity % |
|---------------|------------|--------|-----|----------|
| **Task CRUD** | 7 | 6 | 1 | 86% |
| **Task Bulk Ops** | 2 | 0 | 2 | 0% |
| **Task Search** | 1 | 0 | 1 | 0% |
| **Sprint CRUD** | 4 | 4 | 0 | 100% |
| **Project CRUD** | 5 | 3 | 2 | 60% |
| **Project Extensions** | 7 | 0 | 7 | 0% |
| **Action Lists** | 12 | 0 | 12 | 0% |
| **Activation** | 4 | 0 | 4 | 0% |
| **TOTAL** | **38** | **13** | **25** | **34%** |

---

## Top 10 Python MCP Implementation Roadmap

### Phase 1: Core Operations (Priority 1) — Est. 12h total

| # | Tool | Rationale | Effort | Dependencies |
|---|------|-----------|--------|--------------|
| 1 | `activate_taskman_server` | Health check critical for agent startup | 2h | None |
| 2 | `project_create` | Complete CRUD, fix existing stub | 1h | ProjectRepository |
| 3 | `project_list` | Enable project discovery | 2h | ProjectRepository |
| 4 | `task_update_status` | Workflow state transitions | 1h | Update wrapper |
| 5 | `task_assign` | Assign/reassign tasks | 1h | Update wrapper |
| 6 | `task_search` | Agent search workflows | 3h | Text search impl |

### Phase 2: Extended Operations (Priority 2) — Est. 16h total

| # | Tool | Rationale | Effort | Dependencies |
|---|------|-----------|--------|--------------|
| 7 | `task_bulk_update` | Batch operations | 3h | Locking service |
| 8 | `task_assign_to_sprint` | Sprint planning | 2h | Locking service |
| 9 | `project_get_metrics` | Analytics for agents | 4h | Aggregation queries |
| 10 | `action_list_*` (CRUD) | Action list foundation | 4h | ActionListRepository |

---

## Implementation Notes

### Missing Python Infrastructure

| Component | TypeScript | Python Status |
|-----------|------------|---------------|
| `ActionListRepository` | ✅ Backend API | ❌ Not implemented |
| `ProjectRepository` | ✅ Backend API | ❌ Not implemented |
| `LockingService` | ✅ infrastructure/locking.ts | ❌ Not implemented |
| `CircuitBreaker` | ✅ client-with-circuit-breaker.ts | ❌ Not implemented |
| `SessionManager` | ✅ infrastructure/session-manager.ts | ❌ Not implemented |

### Patterns to Mirror from TypeScript

1. **Circuit Breaker Pattern** - Implement using `tenacity` or custom state machine
2. **Resource Locking** - Thread-safe dict with agent tracking
3. **Audit Logging** - Already uses `structlog` ✅
4. **Validation Schemas** - Pydantic schemas already in place ✅

---

## Estimated Total Effort

| Phase | Tools | Effort | Cumulative |
|-------|-------|--------|------------|
| Phase 1 (Core) | 6 tools | 10h | 10h |
| Phase 2 (Extended) | 4 tools | 13h | 23h |
| Phase 3 (Action Lists) | 12 tools | 24h | 47h |
| Phase 4 (Project Extensions) | 7 tools | 16h | 63h |
| Phase 5 (Activation) | 4 tools | 4h | **67h total** |

---

## Quick Wins (≤2h each)

1. `task_update_status` — Wrapper around `task_update`
2. `task_assign` — Wrapper around `task_update`
3. `activate_taskman_server` — Health check endpoint
4. `project_delete` — Fix stub to query repository

---

## Data Sources

- `cf_core/mcp/taskman_server.py` (1525 lines)
- `mcp-servers/taskman-mcp/src/` (4 registration files)

---

*This analysis informs the `python-mcp-skeleton` task (8-10h estimated).*
