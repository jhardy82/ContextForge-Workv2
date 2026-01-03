# Tasks CLI Repair & Enhancement — Comprehensive Checklist

Project: ContextForge QSE — Tasks CLI Repair & Enhancement
Project ID(s): P-CF-CLI-ALIGNMENT, P-TERMINAL-STANDARDS, P-OBSERVABILITY, P-CLI-TESTING, P-DB-MIGRATION, P-DOCUMENTATION, P-CI-CD
Date: 2025-11-11

Authoritative Analysis: .QSE/v2/Artifacts/TASKS-CLI-COMPREHENSIVE-ANALYSIS-20251111.md
Related Tracker: MCP Todos — "ContextForge Work - Tasks CLI Repair & Enhancement (2025-11-11)"

---

## Phase 0 — Emergency Repair (Blocking)

- [ ] tasks-cli-emergency-repair — Repair structural corruption in `tasks_cli.py`
  - [ ] Add complete import block (~50 lines)
  - [ ] Implement helper functions: `_utc`, `_format_timestamp`, `_apply_notes_mutation`, `_fallback_event`, `_safe_log`, `_resolve_pg_dsn`, `_get_write_connection`, `_execute_authoritative_upsert`, `_emit_evidence_event`
  - [ ] Remove corrupted module-level code (lines 12–154; 156–169)
  - [ ] Validate with `py_compile`, import test, `--help`
  - Acceptance: File imports cleanly; basic command help works; no stray module-level bodies remain

- [ ] wire-task-upsert — Wire `task_upsert` to `_execute_authoritative_upsert` (in progress)
  - [ ] Preserve `--dry-run` and `--json`
  - [ ] Compute SHA-256 row hash; emit JSONL evidence
  - [ ] Fail fast if Postgres unavailable
  - Acceptance: Dry-run shows diff; live writes succeed; evidence event logged

---

## Phase 1 — PostgreSQL Foundation & Rich UI (High)

Database Foundation
- [ ] postgres-connection-pooling — Implement `ThreadedConnectionPool` (1–10)
  - Acceptance: Pool used across writes; health checks (SELECT 1); retries with backoff
- [ ] dsn-resolution-support — Support DSN: `DBCLI_PG_DSN` > `DATABASE_URL` > env vars
  - Acceptance: All three forms validated in dev; errors clear when missing
- [ ] refactor-task-update — Use `_get_write_connection` + `_execute_authoritative_upsert`
  - Acceptance: Update path is Postgres-only; idempotent; evidence logged
- [ ] replace-sqlite-writes — Eliminate sqlite3 write paths; document read-only uses
  - Acceptance: No writes to `db/trackers.sqlite`; read-only aggregations documented

Rich UI Compliance
- [ ] rich-ui-progress-system — Add multi‑phase progress (🔧 PREP, ⚡ EXEC, 📋 PROC)
  - Acceptance: Progress used for operations ≥5s; columns per standard
- [ ] rich-ui-public-api — Add `get_operations_log()` accessor
  - Acceptance: Tests can assert on operations log without private members
- [ ] rich-ui-command-integration — Use progress in list/show/bulk ops
  - Acceptance: Long operations display progress consistently
- [ ] rich-ui-fix-double-print — Remove duplicate status printing (optional tidy)
  - Acceptance: Status spinner is singular; no double output

---

## Phase 2 — Configuration, Testing, Observability (Medium)

Configuration & UX
- [ ] typer-config-integration — YAML/JSON config support (`--config`, profiles)
  - Acceptance: db/config loaded via file; env overrides; profiles work
- [ ] questionary-integration — Interactive create/update flows
  - Acceptance: Wizard validates and confirms before write

Testing & Quality
- [ ] typer-testing-suite — CLI tests via `CliRunner` (≥80% coverage target)
  - Acceptance: Commands tested: dry-run, json output, error cases, `--help`
- [ ] hypothesis-testing — Property-based tests (idempotency, parameters)
  - Acceptance: Idempotency verified; failure cases covered
- [ ] add-upsert-tests — Unit tests for `_execute_authoritative_upsert`
  - Acceptance: Insert, conflict-update, invalid row, rollback paths covered
- [ ] run-lint-and-tests — Ruff, mypy, pytest; coverage reports
  - Acceptance: Lint clean or waivers; tests pass; coverage threshold met

Observability
- [ ] structlog-optimization — Structured logging with correlation_id
  - Acceptance: Dev renderer (console), prod (JSON); fields present
- [ ] opentelemetry-tracing — Spans for DB/CLI/DTM ops with attributes
  - Acceptance: Trace tree visible (console/OTLP); overhead acceptable
- [ ] sentry-error-tracking — Sentry SDK DSN, 10% traces, env/release tags
  - Acceptance: Errors captured with context; slow queries flagged

Documentation
- [ ] mkdocs-typer-documentation — Auto‑generated CLI docs + CI publish
  - Acceptance: docs/cli-reference.md generated; GH Pages updates on commit
- [ ] add-adr-postgres-authoritative — ADR for Postgres‑first decision
  - Acceptance: Includes SENTINEL behavior, evidence format, rollback plan

Data Migration
- [ ] schema-divergence-resolution — Map SQLite↔Postgres (summary→notes, etc.)
  - Acceptance: Mapping + validation tests finalized
- [ ] migration-script — One‑time SQLite→Postgres migration script with evidence
  - Acceptance: Dry‑run/apply modes; per-row evidence; summary report

CI/CD
- [ ] psycopg-in-ci — Ensure CI installs psycopg2; provides DB or mock
  - Acceptance: CI runs DB tests or skips with clear logs

---

## Phase 3 — Architecture Evolution (Low / Deferred)

- [ ] pydantic-v2-12-upgrade — Upgrade to v2.12.x and validate
  - Acceptance: Models validate; no breaking changes
- [ ] (Deferred) SQLAlchemy ORM + Alembic migrations (v2.0 track)
  - Acceptance: Planned; out of scope for current milestone

---

## Evidence & Validation

- All authoritative writes must emit JSONL evidence with SHA‑256 hash
- All long‑running operations use Rich progress per Terminal Output Standard v2.0.0
- Quality gates: pytest ≥80% coverage (Python), Pester ≥70% (PowerShell), analyzers clean
- DB authority: No SQLite writes; Postgres‑first with DSN resolution

---

## Cross‑References (Todo IDs)

- tasks-cli-emergency-repair
- wire-task-upsert
- postgres-connection-pooling
- dsn-resolution-support
- refactor-task-update
- replace-sqlite-writes
- centralize-evidence-logger
- rich-ui-progress-system
- rich-ui-public-api
- rich-ui-command-integration
- typer-config-integration
- questionary-integration
- typer-testing-suite
- structlog-optimization
- hypothesis-testing
- opentelemetry-tracing
- sentry-error-tracking
- pydantic-v2-12-upgrade
- mkdocs-typer-documentation
- add-upsert-tests
- psycopg-in-ci
- migration-script
- add-adr-postgres-authoritative
- schema-divergence-resolution
- run-lint-and-tests

---

Notes:
- This checklist mirrors the current MCP todo list and the master analysis document. Update both when scope changes.
- Use DSN priority: DBCLI_PG_DSN > DATABASE_URL > discrete env vars.
- Ensure `DB_AUTHORITY.SENTINEL` behavior documented in ADR.
