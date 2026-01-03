# Immediate Corrective Actions – Orchestration & Logging

Generated: 2025-08-18T00:00:00Z (placeholder)
Owner: Automation Modernization
Status: Draft

## Objectives
Stabilize orchestration event ingestion, raise logging coverage to baseline (no FAIL_CORE_MISSING), and eliminate repetitive error floods.

## Scope
- Scripts: `Populate-OrchestrationDb.ps1`, Pester/CLI harness scripts, provider helpers.
- Datastores: (a) Orchestration DB (new schema/bootstrap) (b) Task DB (reference only, unchanged).
Strategy Decision Incorporated: Maintain dual databases; add read-model projection of tasks inside Orchestration DB (CQRS) instead of full merge.

## Action Table

| ID | Category | Action | Detail / Acceptance | Owner | ETA | Status |
|----|----------|--------|---------------------|-------|-----|--------|
| A1 | Schema | Create orchestration DB migrations | Add 0001 core DDL (events, tasks, artifacts, metrics). Idempotent. Verify tables exist before inserts. | Dev | +1d | Open |
| A2 | Ingestion | Gate inserts on schema presence | Fail-fast w/ single error, emit `decision` rationale, no error flood. | Dev | +1d | Open |
| A3 | Logging | Emit `task_end` in Populate script | Always output success/failure, duration_ms. | Dev | +1d | Open |
| A4 | Logging | Implement artifact_emit for Pester outputs | After each run, emit one event per artifact with hash+size. | Dev | +1d | Open |
| A5 | Coverage | Guarantee `command_end` | Wrap CLI entrypoints in try/finally. | Dev | +1d | Open |
| A6 | Noise | Error deduplication | Collate identical SQL errors; single event with count. | Dev | +2d | Open |
| A7 | Reporting | Host policy violations detail | Populate file/policy/rule fields (no nulls). | Dev | +2d | Open |
| A8 | Validation | Post-fix coverage scan target | Overall status != FAIL, zero FAIL_CORE_MISSING; sessions_with_gaps <= 2. | QA | +2d | Open |
| A9 | Metrics | Insert provider_type metric | Map Microsoft=1 System=2 CacheHit boolean -> provider_cache_hit metric. | Dev | +1d | Open |
| A10 | Tests | Add migration/bootstrap unit test | Pester: asserts tables exist; negative test triggers single controlled error. | QA | +2d | Open |
| C1 | Projection | Add tasks projection table | Migration 0002_TaskProjection.sql: task_id PK, title, status, last_status_ts, priority, tags_json, last_event_ts, updated_utc. | Dev | +2d | Open |
| C2 | Projection | Implement projection updater | On event ingest (task_start/task_end/decision) upsert projection row; update last_event_ts. | Dev | +2d | Open |
| C3 | Projection | Reconciliation script | Nightly script compares authoritative Tasks DB vs projection; emits drift metrics & decision events. | Dev | +3d | Open |
| C4 | Metrics | Projection drift metrics | Emit metrics: projection_drift_count, projection_sync_latency_ms (avg), last_reconcile_ts. | Dev | +3d | Open |

## Sequencing (Critical Path)
1. A1 → A2 (schema before gating logic)
2. A3 + A5 (baseline completeness) → A4 (artifact emits) → A6 (noise reduction) → A9 (metrics) → A7 (report enrichment) → A8 (coverage validation) → A10 (tests hardened).
3. After A1–A3 stable: implement C1 → C2 → C4 → C3 (reconciliation depends on metrics emission).

## Implementation Notes
- Migration file naming: `/db/orch_migrations/0001_Core.sql` (distinct path from task DB). Include IF NOT EXISTS DDL.
- Hash each artifact in A4 using SHA256; record hex digest.
- Dedup (A6): maintain hashtable (message -> count); flush aggregated errors at script end or on different message encounter.
- Provider metric (A9): `provider_type` numeric + existing `provider_cache_hit` bool; emit during task_start or immediately after provider selection.
- Coverage criteria (A8): run existing logging coverage script; compare JSON; if status FAIL_CORE_MISSING present → block release.
Projection (C1–C4): Keep projection strictly denormalized snapshot; no business logic originates there. Rebuild allowed (drop & rehydrate) if drift > threshold.
Reconciliation (C3): classify differences: missing_in_projection, missing_in_tasks, status_mismatch; emit decision events with counts & top 5 sample IDs.

## Risk & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Misapplied DDL on existing DB | Data loss | Use IF NOT EXISTS; no DROP statements. |
| Over-aggregation hides distinct errors | Missed real issue | Cap aggregation window to identical message + stage only. |
| Artifact hashing performance | Slow large files | Skip hash for >50MB (log decision). |
| Projection drift ignored | Stale analytics decisions | Nightly reconcile + alert if drift_count > 0 for 2 consecutive runs. |
| Projection misused for writes | Data inconsistency | Document projection as read-only; add guard comment header + optional trigger to block direct updates. |

## Verification Checklist
- [ ] Orchestration DB tables exist (events, tasks, artifacts, metrics).
- [ ] Populate script emits: task_start, decision (schema_ok), 0+ event_insert, task_end.
- [ ] No repeated identical SQL error spam.
- [ ] CLI logs include artifact_emit for Pester artifacts.
- [ ] Coverage scan: zero FAIL_CORE_MISSING.
- [ ] Host policy report: no null file/policy/rule.
- [ ] provider_type metric present in metrics table.
- [ ] New Pester tests pass (migration + error dedup).
- [ ] Projection table exists with expected columns.
- [ ] Projection updated after a simulated task_start/task_end event ingest.
- [ ] Reconciliation script emits drift metrics & decision events (drift_count=0 post initial sync).
- [ ] Projection metrics (projection_drift_count, projection_sync_latency_ms) recorded.

## Exit Criteria
All verification checklist items true in a single run; logging coverage target met; projection drift_count=0 after reconciliation; plan status moved to Complete.

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-08-18 | Initial draft | Automation |
| 2025-08-18 | Added tasks projection (C1–C4) & rationale | Automation |

## Rationale: Dual DB + Projection vs Merge
Maintaining an authoritative Tasks DB separate from the high‑volume Orchestration DB preserves isolation (backlog integrity) while enabling rapid evolution of observability schema.

A tasks projection inside the Orchestration DB supplies low-latency joins for analytics without introducing write contention or transactional coupling.

Full merge is deferred until/unless measured cross-db join cost & operational overhead exceed isolation benefits. The projection can be rebuilt; authoritative tasks data remains minimal, auditable, and stable.
