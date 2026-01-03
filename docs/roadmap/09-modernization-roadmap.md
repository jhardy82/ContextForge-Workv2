# 09 – Modernization Roadmap (ContextForge & TaskMan‑v2)

This roadmap describes how to keep the ContextForge workspace – including TaskMan‑v2, CF_CORE/CF_CLI, MCP servers, QSE, and logging infrastructure – modern, streamlined, and aligned with current architectural principles.

It is intended to be read alongside:
- `00-executive-summary.md` (high-level goals)
- `01-current-state-analysis.md` (baseline)
- `02-technical-architecture.md` (architecture blueprint)
- `05-testing-strategy.md` (quality gates)
- `08-success-metrics.md` (KPI definitions)

---

## 1. Objectives & Principles

**Primary objectives**

- Ensure all core systems (TaskMan‑v2, CF_CLI, MCP, QSE, logging, analytics) are:
  - **Observable** (structured logging + metrics),
  - **Testable** (pytest/Pester/CI gates),
  - **Composable** (MCP + CF_CLI orchestration),
  - **Upgradable** (runtime/tooling updates with minimal friction).

**Guiding principles**

- CF_CLI remains the **authoritative orchestration entry point** for CF_CORE workflows.
- TaskMan‑v2 is the **authoritative source of truth** for tasks/projects/sprints.
- Logs are **JSONL‑first**, with a consistent schema and correlation IDs.
- Runtimes are kept within current LTS (or LTS+1) windows.
- Tests and gates enforce behavior; documentation explains it.

---

## 2. Current State – Gap Summary

- **Logging**
  - UnifiedLogger/structured logging patterns exist but are not yet uniformly adopted.
  - TaskMan‑v2 backend had print‑based startup/shutdown logs; now partially migrated to structured logging with correlation IDs.
  - Canonical root‑level JSONL logs for TaskMan‑v2 (`logs/backend-api.log`, `logs/system-operations.log`, etc.) are only beginning to appear.

- **TaskMan‑v2 & CF_CLI integration**
  - TaskMan‑v2 backend API is present but still evolving (PostgreSQL/SQLite, schema alignment, validation).
  - CF_CLI is authoritative for CF_CORE, but some flows still rely on legacy trackers or scripts.

- **MCP servers & AI assistants**
  - MCP health checklist exists; TaskMan MCP and TypeScript MCP server have project‑level checklists.
  - Standardization of structured logging and health reporting across MCP servers is in progress.

- **Testing & CI**
  - Pytest/Pester suites and specialized gates (logging gate, QSE validation) exist.
  - Coverage and logging gates are enforced in some areas but not uniformly across all subsystems.

- **Documentation & governance**
  - Roadmap docs, Codex, AGENTS, and checklists are present and connected.
  - A structured logging inventory tracker has been created, but a complete inventory scan is still pending.

---

## 3. Modernization Pillars & Workstreams

### 3.1 Structured Logging & Observability

**Goals**

- All core components emit structured JSONL logs with consistent fields and correlation IDs.
- Canonical log locations exist per subsystem (TaskMan‑v2, CF_CLI, MCP servers, PowerShell tools).
- Log artifacts support automated clustering and evidence bundle creation (Phase 1 bug mining).

**Key actions**

- Finalize logging schema:
  - Fields: `timestamp`, `level`, `component`/`logger`, `action`, `message`, `correlation_id`/`run_id`, `ok`/`command_ok`, optional `error_message`/`stack_trace`.
- TaskMan‑v2:
  - Use `TaskMan-v2/backend-api/utils/logger.py` (structured formatter + correlation middleware).
  - Route backend logs to `logs/backend-api.log` (JSONL).
  - Add structured logging in routers for key operations and error paths.
- CF_CORE / CF_CLI:
  - Ensure CF_CLI flows emit UnifiedLogger‑compatible JSONL events (align with logging gate tests).
- MCP servers:
  - Adopt a JSON logger (Node/TS) with the same schema.
  - Emit health/traffic logs suitable for `docs/mcp/MCP-Servers-Health-Checklist.md`.
- PowerShell:
  - Introduce or standardize a structured logging helper to emit JSONL (UnifiedLogger adapter).

**Artifacts**

- `projects/cf_logging/Project-Checklist.md`
- `projects/unified_logger/Project-Checklist.md`
- `.github/TODOs/Structured-Logging-Inventory-Tracker.md`
- `python/analysis/logging_inventory_scan.py`

---

### 3.2 TaskMan‑v2 & CF_CLI Modernization

**Goals**

- Treat TaskMan‑v2 as the authoritative task/project/sprint system, with PostgreSQL as primary DB authority.
- Ensure CF_CLI routes task operations through TaskMan‑v2 wherever feasible.
- Align TaskMan‑v2 schemas/constraints with CF_CLI expectations and roadmap docs.

**Key actions**

- Schema & constraints (CL‑A):
  - Align `tasks` table enums and fields with CF_CLI and API (status, work_type, hours, assignee).
  - Ensure constraint violations and schema mismatches are surfaced via structured logs.
- Backend runtime & validation (CL‑B):
  - Harden simple‑API / backend routes with strict JSON schema validation and robust error handling.
  - Replace any in‑memory `tasks` usage with DB‑backed queries.
- Connectivity & authority (CL‑D):
  - Stabilize PostgreSQL connectivity, timeouts, and degraded modes.
  - Emit structured logs for connection failures and recovery attempts.
- CF_CLI alignment:
  - Ensure CF_CLI commands for tasks/projects/sprints target TaskMan‑v2 and surface structured events for logs/analytics.

**Artifacts**

- `TaskMan-v2/Project-Checklist.md`
- `docs/bugs/TaskMan-Phase2-Triage-Plan.md`
- `.QSE/v2/TaskMan-v2/Project-Checklist.md`

---

### 3.3 MCP Servers & AI Assistant Integration

**Goals**

- MCP servers are small, focused, and consistently observable.
- AI assistants (Copilot, Claude, Codex) use MCP + CF_CLI in a governed way.

**Key actions**

- MCP health:
  - Implement standard `/api/health` and/or STDIO ping endpoints.
  - Emit structured MCP health logs (JSONL) and integrate with the MCP health checklist.
- TaskMan MCP:
  - Ensure the TypeScript MCP server and P‑TASKMAN‑MCP project share a common view of tools, logging, and health.
- AI assistants:
  - Use `docs/ai-assistants/INDEX.md` as the single landing page.
  - Keep agent behavior aligned with AGENTS + Codex (CF_CLI authority, logs‑first, TaskMan‑first).

**Artifacts**

- `docs/mcp/INDEX.md`, `docs/mcp/MCP-Servers-Health-Checklist.md`
- `projects/P-TASKMAN-MCP/Project-Checklist.md`
- `TaskMan-v2/mcp-server-ts/docs/Project-Checklist.md`
- `docs/ai-assistants/INDEX.md`

---

### 3.4 Data & Database Modernization

**Goals**

- PostgreSQL is the primary authority for TaskMan‑v2 and CF_CORE; SQLite remains a well‑understood fallback where necessary.
- Migrations, schema validation, and data integrity checks are automated and logged.

**Key actions**

- Consolidate DB authority docs and trackers:
  - Keep `DATABASE-INTEGRATION-SUMMARY.md` and authority maps current.
- Harden migrations:
  - Ensure Alembic migrations are tested and logged; failures emit structured events.
- Integrate DB MCP server usage for introspection and validation.

**Artifacts**

- `docs/authority/INDEX.md`
- `TaskMan-v2/backend-api` (Alembic, `database.py`)
- DB MCP server docs and tests

---

### 3.5 Testing, Gates & CI

**Goals**

- A small, focused set of tests and gates verify modernization progress.
- Logging, coverage, and MCP/QSE validation are enforced consistently.

**Key actions**

- Pytest:
  - Keep pytest as the primary Python test runner.
  - Add tests for new logging helpers (log scan, inventory scan, backend logger).
- Logging gates:
  - Maintain and extend `test_logging_gate.py` to cover core UnifiedLogger/structured logging requirements.
- CI pipelines:
  - Ensure CI runs:
    - Lint/typecheck (ruff, mypy),
    - Tests (with logging/QSE/MCP gates),
    - Coverage and basic performance checks.

**Artifacts**

- `docs/testing/` (and `docs/validation/INDEX.md`)
- `tests/python/test_logging_gate.py`
- CI pipeline configuration (GitHub Actions, scripts under `build/` / `.github/scripts/`)

---

### 3.6 Developer Experience & Environments

**Goals**

- Developers have a predictable way to set up, run, and observe the system.
- Local environments resemble CI/production where it matters.

**Key actions**

- Environments:
  - Standardize on Python virtualenv + uv, Node LTS, PS7 for local dev.
  - Keep `.env` files and config docs up to date for TaskMan‑v2 and CF_CLI.
- Tooling:
  - Maintain minimal VS Code tasks that wrap CF_CLI / TaskMan flows.
  - Provide a small set of “golden” commands for starting/stopping key services and viewing logs.

**Artifacts**

- `docs/guides/INDEX.md`
- `docs/environment/` (if present)
- TaskMan‑v2 and CF_CLI README files

---

### 3.7 Documentation, Governance & Evidence

**Goals**

- Roadmaps, checklists, and trackers stay in sync with actual behavior.
- Evidence (logs, bundles, AARs) is easy to find and verify.

**Key actions**

- Keep project checklists current:
  - Ensure each major project (TaskMan‑v2, cf_logging, unified_logger, MCP servers) has an up‑to‑date `Project-Checklist.md`.
- Maintain modernization trackers:
  - Use `.github/TODOs/Structured-Logging-Inventory-Tracker.md` and related trackers to record progress.
- Evidence:
  - Use Phase‑1/Phase‑2 bug catalogs and evidence indexes for TaskMan‑v2 as a model for future campaigns.

**Artifacts**

- `.github/TODOs/Structured-Logging-Inventory-Tracker.md`
- `.github/TODOs/Next-Steps-Indexes-Bugs-QSE-Checklist.md`
- `docs/bugs/INDEX.md`, `reports/bugs/*`

---

## 4. Phased Modernization Plan

### Phase 1 – Stabilize (Short Term)

- Establish canonical logging schema and root‑level JSONL locations.
- Refactor high‑impact components (TaskMan‑v2 backend, CF_CLI) to structured logging.
- Run initial logging inventory scans for key subtrees (TaskMan‑v2, python/, mcp-servers/).
- Deliver first Phase‑1 bug catalog and evidence index for TaskMan‑v2.

### Phase 2 – Harden (Medium Term)

- Extend structured logging to MCP servers and critical PowerShell scripts.
- Close gaps identified by logging inventory (unstructured/mixed hotspots).
- Strengthen TaskMan‑v2 schema, API validation, and CF_CLI integration.
- Enforce logging/test/coverage gates across CI.

### Phase 3 – Optimize (Longer Term)

- Integrate logs with dashboards/analytics (DuckDB, QSE dashboards).
- Tune performance and SLOs using metrics and log‑driven analysis.
- Periodically reevaluate runtimes, dependencies, and tooling to stay on modern LTS lines.

---

## 5. Success Metrics (Linkage to 08-Success-Metrics)

Use `08-success-metrics.md` for concrete KPI definitions. Modernization should improve:

- **Reliability:** fewer runtime errors and DB connectivity issues, as observed in JSONL logs and bug catalogs.
- **Observability:** all critical flows produce structured logs with correlation IDs; logging gate tests pass consistently.
- **Velocity:** easier reproduction/triage from logs, shorter mean time to detect (MTTD) and resolve (MTTR) for bugs.
- **Consistency:** CF_CLI, TaskMan‑v2, MCP, and PowerShell scripts share the same logging and configuration patterns.

This roadmap should be updated as major architectural decisions are made or as new pillars (e.g., additional MCP servers or QSE capabilities) are introduced.

