# TaskMan‑v2 API & Runtime Validation Matrix (SR‑2)

This matrix captures the SR‑2 focused deep‑dive on TaskMan‑v2 API and runtime behavior (CL‑A…E related), using a **plan‑first** approach with evidence drawn from code, logs, and tests.

## Components & Results

| ID           | Component / Scenario                                     | Test Type    | Expected Behavior                                               | Actual (SR‑2 Static Review)                                                                 | Evidence (Paths)                                                                                                                                         | Status   |
|--------------|----------------------------------------------------------|--------------|------------------------------------------------------------------|---------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| TMV-API-1    | Task listing (`GET /api/v1/tasks`)                       | Integration  | Paginated, filtered task list; structured logs with filters     | Query and filters implemented; list endpoint now emits structured logs via `utils.logger`   | `TaskMan-v2/backend-api/routers/tasks.py`, `TaskMan-v2/backend-api/utils/logger.py`, `logs/backend-api.log` (dev_smoke), `python/analysis/taskman_phase1_log_scan.py` | PARTIAL  |
| TMV-API-2    | Project listing (`GET /api/v1/projects`)                 | Integration  | Filterable by status; structured logs with filters              | Filtering by status implemented; list endpoint now emits structured list log event          | `TaskMan-v2/backend-api/routers/projects.py`, `TaskMan-v2/backend-api/utils/logger.py`, `logs/backend-api.log` (after runtime traffic)                   | PARTIAL  |
| TMV-API-3    | Sprint listing (`GET /api/v1/sprints`)                   | Integration  | Filterable by status/project; structured logs with filters      | Filters implemented; list endpoint now logs `taskman_v2.sprints.list` with filter context   | `TaskMan-v2/backend-api/routers/sprints.py`, `TaskMan-v2/backend-api/utils/logger.py`, `logs/backend-api.log`                                           | PARTIAL  |
| TMV-API-4    | Action list listing (`GET /api/v1/action-lists`)         | Integration  | Filterable by status/project/sprint/owner; structured logs      | Filters implemented; list endpoint now logs `taskman_v2.action_lists.list` with filter data | `TaskMan-v2/backend-api/routers/action_lists.py`, `TaskMan-v2/backend-api/utils/logger.py`, `logs/backend-api.log`                                      | PARTIAL  |
| TMV-API-5    | Backend startup & DB init (`startup_event`, `init_db`)   | System       | Startup logs with version/db info; DB init logs; no crashes     | Structured startup logs added; DB init logs `taskman_v2.database.init_db.complete`         | `TaskMan-v2/backend-api/main.py`, `TaskMan-v2/backend-api/database.py`, `logs/backend-api.log`                                                           | PARTIAL  |
| TMV-API-6    | Error pattern clustering (Phase‑1 helper)                | System/Tools | Repeated error patterns clustered; singletons ignored           | Phase‑1 helper implemented and unit‑tested; dev_smoke error cluster confirmed              | `python/analysis/taskman_phase1_log_scan.py`, `tests/python/test_taskman_phase1_log_scan.py`, `logs/backend-api.log`, `reports/bugs/phase-1-log-summary.json`       | PASS     |
| TMV-API-7    | Phase‑1 bug catalog & evidence index                     | Governance   | Initial bug catalog and evidence bundles populated from logs    | Dev_smoke diagnostic bug and evidence bundle in place (low severity)                       | `reports/bugs/phase-1-bug-catalog.json`, `reports/bugs/phase-1-evidence-index.json`, `.QSE/v2/TaskMan-v2/Project-Checklist.md`                          | PASS     |

Status key: **PASS** – behavior confirmed with evidence; **PARTIAL** – code/logs wired but needs runtime + tests; **GAP** – missing or unimplemented.

## Notes & Next Steps (SR‑2)

- The list endpoints (tasks, projects, sprints, action-lists) now emit structured logs, but the matrix remains **PARTIAL** until:  
  - TaskMan‑v2 backend is exercised under real workloads and `logs/backend-api.log` captures non‑smoke traffic.  
  - Pytest integration tests (using `TestClient`) confirm both API responses and log events.
- The Phase‑1 clustering tool and initial bug/evidence entries are in place and marked **PASS** for a diagnostic dev_smoke cluster; they must be extended to real runtime errors.

