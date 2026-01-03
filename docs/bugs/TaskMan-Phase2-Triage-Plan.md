# TaskMan‑v2 Phase 2 Triage & Hypothesis Plan

Phase: Triangle → **Think** (Triage & Hypothesize)  
Scope: TaskMan‑v2 backend, DB, frontend, cf_cli, MCP logging  
Authority: CF_CLI is the orchestration entry point

---

## Quick Links (Evidence & Artifacts)

- Phase 1 Bug Catalog: `reports/bugs/phase-1-bug-catalog.json`
- Phase 1 Evidence Index: `reports/bugs/phase-1-evidence-index.json`
- Phase 1 Analysis Report: `reports/bugs/PHASE-1-LOG-ANALYSIS.md`
- Phase 2 Triage Matrix: `reports/bugs/phase-2-triage-matrix.json`
- Phase 2 Hypotheses: `reports/bugs/phase-2-hypotheses.json`
- Phase 2 Repro Specs: `reports/bugs/phase-2-repro-specs.yaml`
- Phase 2 Triage→Task Map: `reports/bugs/phase-2-triage-task-map.json`

---

## Tracking Dashboard (Clusters)

Use this section as a living status board. Update status checkboxes and owners as work progresses.

| Cluster ID         | Title                                          | Priority | Owner(s)         | CF_CLI Task Created | Status      |
|--------------------|-----------------------------------------------|----------|------------------|----------------------|------------|
| CL-A-DB-SCHEMA     | Tasks table schema & constraint failures      | P0       | `@backend-db`    | ☐                    | ☐ Not started |
| CL-B-API-RUNTIME   | simple-api runtime & JSON validation          | P0       | `@backend-api`   | ☐                    | ☐ Not started |
| CL-C-UI-DEVPIPE    | Vite/dev pipeline dependency failures         | P1       | `@frontend`      | ☐                    | ☐ Not started |
| CL-D-DB-CONNECTIVITY | PostgreSQL host resolution & degraded mode  | P0       | `@infra`         | ☐                    | ☐ Not started |
| CL-E-INSTRUMENTATION | cf_cli & MCP logging instrumentation        | P2       | `@platform-obs`  | ☐                    | ☐ Not started |

Legend:
- CF_CLI Task Created: check when the cluster’s coordinating TaskMan task exists.
- Status: choose one per cluster (Not started / In progress / Done).

---

## Cluster Workspaces

Each cluster has its own mini‑workspace for tracking tasks, hypotheses, and collaboration notes.

### CL-A-DB-SCHEMA – Tasks Table Schema & Constraint Failures (P0)

- Overall Status:
  - [ ] Not started
  - [ ] In progress
  - [ ] Done
- Owners: `@backend-db`, `@cf_cli`
- Related Bugs: `BUG-011`, `BUG-012`, `BUG-013`, `BUG-014`, `BUG-015`, `BUG-016`, `BUG-017`
- Evidence bundles: `EVID-BUG-011`–`EVID-BUG-017`

**CF_CLI Coordination Task**

- Proposed command (update project/sprint as needed):
  - `python cf_cli.py task create --title "[CL-A] Align tasks schema with TaskMan API" --project P-TASKMAN-BUGS --sprint S-2025-09-01`
- Task ID: `T-CL-A-XXXX` (fill after creation)

**Work Checklist**

- [ ] Inspect `tasks` table schema via DB MCP (columns, types).
- [ ] Dump `tasks_status_check` and `tasks_work_type_check` definitions directly from PostgreSQL.
- [ ] Compare PostgreSQL `tasks` schema (via DB MCP) with the legacy SQLite schema in `src/TaskDatabase/Initialize-TaskDatabase.ps1`; document any differences that affect TaskMan-v2 and CF_CLI behavior.
- [ ] Define canonical enums for `status` and `work_type` (CF_CLI + API + DB).
- [ ] Decide on canonical presence/absence of: `assignee`, `due_date`, `estimated_hours`, `actual_hours`.
- [ ] Implement migrations to align DB schema with canonical model.
- [ ] Add cf_cli‑side validation for `status` and `work_type`.
- [ ] Add API request validation for task create/update payloads.
- [ ] Re‑run CL‑A repro spec; confirm no new constraint/column‑missing errors in logs.

**Key Research Questions**

- What is the intended lifecycle/state machine for `tasks.status`?
- Which `work_type` values are required by business rules and which are legacy?
- Are `assignee` / `estimated_hours` / `actual_hours` stored in DB, derived, or tracked elsewhere (e.g., analytics only)?
- How should canonical `tasks` semantics in PostgreSQL relate to legacy SQLite task schemas (QSE/COF alignment)?

**Collaboration Notes**

- Decisions:
  - …
- Open discussions:
  - …
- Follow‑ups:
  - …

---

### CL-B-API-RUNTIME – simple-api Runtime & JSON Validation (P0)

- Overall Status:
  - [ ] Not started
  - [ ] In progress
  - [ ] Done
- Owners: `@backend-api`
- Related Bugs: `BUG-001`, `BUG-004`, `BUG-005`, `BUG-006`, `BUG-007`, `BUG-008`
- Evidence bundles: `EVID-BUG-001`, `EVID-BUG-004`–`EVID-BUG-008`

**CF_CLI Coordination Task**

- Proposed command:
  - `python cf_cli.py task create --title "[CL-B] Harden simple-api runtime & JSON validation" --project P-TASKMAN-BUGS --sprint S-2025-09-01`
- Task ID: `T-CL-B-XXXX`

**Work Checklist**

- [ ] Verify `chalk` is installed in the runtime/container image (dependency is already declared in `vs-code-task-manager/package.json`).
- [ ] Ensure Node dependencies (including any devDependencies needed for the running mode) are installed in the same environment used by PM2 / `node simple-api.js`.
- [ ] Make `db` initialization deterministic before route registration and confirm all deployments use the current PostgreSQL-backed wrapper (`simple-api.js` / `simple-api-fixed.js`).
- [ ] Replace any use of an in-memory `tasks` array (for example in `/api/stats`) with DB-backed queries, or remove legacy endpoints that depend on undefined globals.
- [ ] Introduce a JSON/schema validation layer for incoming requests.
- [ ] Enforce `Content-Type: application/json` for JSON endpoints.
- [ ] Add null/undefined guards and defaults for `taskName` and related fields.
- [ ] Centralize error handling with structured JSONL logging (no raw stack traces only).
- [ ] Re‑run CL‑B repro spec; confirm disappearance of reference/JSON/TypeError patterns in logs.

**Research Questions**

- Which routes are currently responsible for `db` and `tasks` access?
- Which backend entrypoint is authoritative for TaskMan-v2 (`simple-api.js` vs `simple-api-fixed.js`), and can legacy variants be retired?
- Where is the best insertion point for schema validation (before or inside simple-api handlers)?

**Collaboration Notes**

- Decisions:
  - …
- Open discussions:
  - …
- Follow‑ups:
  - …

---

### CL-C-UI-DEVPIPE – Vite/Dev Pipeline Dependency Failures (P1)

- Overall Status:
  - [ ] Not started
  - [ ] In progress
  - [ ] Done
- Owners: `@frontend`
- Related Bugs: `BUG-002`, `BUG-003`
- Evidence bundles: `EVID-BUG-002`, `EVID-BUG-003`

**CF_CLI Coordination Task**

- Proposed command:
  - `python cf_cli.py task create --title "[CL-C] Fix TaskMan frontend Vite/dev pipeline" --project P-TASKMAN-BUGS --sprint S-2025-09-01`
- Task ID: `T-CL-C-XXXX`

**Work Checklist**

- [ ] Confirm `@vitejs/plugin-react-swc` presence in `package.json` (already present as a devDependency in `vs-code-task-manager/package.json`).
- [ ] Ensure the plugin is installed in dev and container environments (e.g., `npm ls @vitejs/plugin-react-swc` succeeds inside the same environment that runs Vite/PM2).
- [ ] Validate `vite.config.ts` path and module resolution in the container.
- [ ] Align dev server start command with CI/VS Code tasks.
- [ ] Re‑run CL‑C repro spec; confirm Vite starts without config/plugin errors.

**Research Questions**

- Are there environment‑specific differences (local vs container) causing plugin resolution issues?
- Are we installing devDependencies in dev images (TaskMan MCP/VS Code Task Manager), or only production dependencies?
- Should dev dependencies be bundled differently for the MCP Task Manager stack?

**Collaboration Notes**

- Decisions:
  - …
- Open discussions:
  - …
- Follow‑ups:
  - …

---

### CL-D-DB-CONNECTIVITY – PostgreSQL Host Resolution & Degraded Mode (P0)

- Overall Status:
  - [ ] Not started
  - [ ] In progress
  - [ ] Done
- Owners: `@infra`, `@backend-db`
- Related Bugs: `BUG-009`, `BUG-010`
- Evidence bundles: `EVID-BUG-009`, `EVID-BUG-010`

**CF_CLI Coordination Task**

- Proposed command:
  - `python cf_cli.py task create --title "[CL-D] Stabilize PostgreSQL connectivity for TaskMan API" --project P-TASKMAN-BUGS --sprint S-2025-09-01`
- Task ID: `T-CL-D-XXXX`

**Work Checklist**

- [ ] Inspect Docker/compose configs for `postgres-mcp` and `contextforge-postgres` service names.
- [ ] Verify `POSTGRES_HOST`/`POSTGRES_PORT` (and related env vars) used by both CF_CLI and the TaskMan API match actual Docker/compose service names.
- [ ] Align env vars / connection URLs used by the TaskMan API with actual service names.
- [ ] Configure health checks and retries/backoff in the API’s DB client.
- [ ] Use DB MCP and CF_CLI (`status migration`, `context sync`) to validate DB authority and connectivity.
- [ ] Re‑run CL‑D repro spec; confirm EAI_AGAIN errors are eliminated.

**Research Questions**

- Is degraded “continue without DB” behavior still desired, or should API fail fast and signal health failure instead?
- Are there multiple environments (dev, CI, prod) with different hostnames requiring an indirection layer?

**Collaboration Notes**

- Decisions:
  - …
- Open discussions:
  - …
- Follow‑ups:
  - …

---

### CL-E-INSTRUMENTATION – cf_cli & MCP Logging (P2)

- Overall Status:
  - [ ] Not started
  - [ ] In progress
  - [ ] Done
- Owners: `@platform-obs`, `@cf_cli`
- Related Bugs: `BUG-018`, `BUG-019`, `BUG-020`
- Evidence bundles: `EVID-BUG-018`, `EVID-BUG-019`, `EVID-BUG-020`

**CF_CLI Coordination Task**

- Proposed command:
  - `python cf_cli.py task create --title "[CL-E] Improve cf_cli and MCP logging instrumentation" --project P-TASKMAN-BUGS --sprint S-2025-10-01`
- Task ID: `T-CL-E-XXXX`

**Work Checklist**

- [ ] Clarify semantics of `ok` vs `details.status` in cf_cli logs.
- [ ] Introduce a dedicated `command_ok` or `session_ok` field for business outcome.
- [ ] Add richer `details` payloads (command, args, exit codes, correlation_id).
- [ ] Wrap Node MCP API/frontend error logging in JSONL (timestamp, event_type, component, error_message, stack_trace).
- [ ] Keep human‑friendly banners, but ensure every error has a structured JSONL twin.
- [ ] Re‑run CL‑E repro spec; confirm new structured events and clearer cf_cli semantics.

**Research Questions**

- How are logs currently consumed by analytics/COF/QSE layers (Polars, DuckDB)?
- What minimal fields are required for full evidence bundle reconstruction (timestamp, event_type, error_message, stack_trace, affected_component, correlation_id)?

**Collaboration Notes**

- Decisions:
  - …
- Open discussions:
  - …
- Follow‑ups:
  - …

---

## Cross‑Cluster Research & Coordination

Use this section for questions and insights that span multiple clusters.

- [ ] Confirm desired canonical task lifecycle (status + work_type) and record in docs.
- [ ] Define shared validation rules to be reused across cf_cli, API, and MCP surfaces.
- [ ] Align logging schemas (JSONL fields) between cf_cli, backend API, frontend, and QSE.
- [ ] Ensure TaskMan MCP and CF_CLI surfaces stay in sync (feature parity for key operations).

Open Questions:

- How should TaskMan distinguish transient infra failures (e.g., DB DNS) from logical/business errors in tasks?
- What SLIs/SLOs will we track for:
  - DB connectivity
  - Task mutation success rate
  - cf_cli session success rate

---

## Collaboration & Meeting Notes

Use this section to capture synchronous discussions and decisions.

### Standups / Check‑ins

- Date: `YYYY-MM-DD`
  - Participants: …
  - Clusters touched: …
  - Key updates:
    - …
  - Blockers:
    - …

### Design Reviews

- Topic: …
  - Related clusters: …
  - Decision summary:
    - …
  - Action items:
    - [ ] …
    - [ ] …

---

## Validation & Closure

Before declaring Phase 2 complete:

- [ ] All P0 clusters (CL-A, CL-B, CL-D) have CF_CLI tasks **Done**.
- [ ] All P1/P2 clusters (CL-C, CL-E) are at least **In progress** with owners.
- [ ] Re‑run Phase 1 style log mining over a fresh window (e.g., 7–30 days).
- [ ] Regenerate:
  - `reports/bugs/phase-1-bug-catalog.json`
  - `reports/bugs/PHASE-1-LOG-ANALYSIS.md`
- [ ] Confirm:
  - Critical/high DB and connectivity errors have disappeared or dropped below agreed thresholds.
  - New instrumentation provides sufficient evidence for COF/UCL and QSE workflows.
