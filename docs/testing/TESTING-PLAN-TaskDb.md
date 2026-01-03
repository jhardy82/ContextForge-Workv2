# Task Database Testing & Mock Strategy

HostPolicy: DualHost  (Some suites optionally elevate to ModernPS7 when PS7 features are present)
Shape: Triangle → Spiral progression (Foundation + Regression)

## Objectives
1. Validate schema (migrations) and core CRUD correctness.
2. Guarantee idempotency of seeding & backlog ingestion.
3. Verify status history trigger integrity & helper functions.
4. Enforce structured logging baseline (session_start, command_start, command_end, session_summary + decision, artifact_* where applicable) with gap repair coverage.
5. Validate provenance tagging (sidecar manifests + optional inline tag) produced by `Verify-TaskDbCompleteness.ps1`.
6. Exercise negative/fault paths (duplicate refs, invalid status, constraint violations, logging gap auto‑repair).
7. Provide lightweight performance smoke comparison (sequential vs. pseudo-parallel insertion) under PS7.
8. Lay groundwork for future provider mocking (PSSQLite vs. raw ADO.NET) without changing production code.

## Coverage Matrix

| Area | Test File | Key Assertions |
|------|-----------|----------------|
| Migrations Schema | 01 / existing | Tables, views, indexes present |
| Idempotency | 02_Idempotency | Re-running seed/backlog does not duplicate tasks |
| Seeding Integrity | 03_SeedingIntegrity | Row counts, representative fields populated |
| Views & Logs | 04_ViewsAndLogs | Views return expected projections; core log artifacts exist |
| Status History | 05_StatusHistory | History rows emitted; chronological order |
| Status Helper | 06_StatusHelper | No history row when status unchanged |
| Logging Baseline & Gap Repair | 07_Logging.Events | Required core events present; retro repair path synthesizes command_end |
| Provenance Tagging | 08_Tagging.Provenance | Sidecar `.processed.json` created; inline tag optional marker inserted |
| Fault / Negative | 09_Fault.Negative | Duplicate external_ref rejected; invalid status rejected; FK cascade tested |
| Performance Smoke | 10_Performance.BulkInsert | Sequential vs. parallel (if PS7) timing captured, not a strict gate |

## Logging Event Expectations (Baseline)
Required: session_start, command_start, command_end (or synthesized), session_summary.
Supplemental (when applicable): decision (each branch), artifact_touch_batch (migrate/seed/report/export/backlog), artifact_emit (report/export outputs), logging_gap_detected (only in repair scenario), mutation_result (update), error (on exception paths).

## Provenance Tagging
`Verify-TaskDbCompleteness.ps1 -TagSources -TagLabel TEST-TAG` should produce sidecar manifests: `<source>.processed.json` containing: tracking_id, entries array, tag_label. Inline markdown tag insertion is optional; test only asserts sidecar presence & JSON parse validity to avoid brittle diffs.

## Fault Injection Strategy
Fault scenarios executed without modifying production scripts:
1. Duplicate Add: Invoke `Add-Task.ps1` twice with same `-Name` / `-ExternalRef` expecting second failure or skip (depending on logic) – assert DB row count unchanged.
2. Invalid Status: Attempt `Set-TaskStatus.ps1 -Status NotARealStatus` (expect terminating error). Ensure no history row created for that task.
3. Foreign Key Cascade: Add task + dependency (if dependency script available); delete parent; assert dependency rows removed OR skip if dependency scripts not yet implemented.
4. Logging Gap Repair: Manually remove the `command_end` line from a produced log file, then re-run CLI with `-EnforceLogging` referencing same SessionId? (Simpler: run CLI normally and verify no repair, THEN simulate by copying log minus last line into temp path and force coverage tool later — deferred if complexity high). Current test focuses on natural path and ensures no missing events.

## Performance Smoke (Non-Gating)
Under PS7, insert N=200 tasks sequentially (CLI add) then (optionally) via background jobs (Start-Job) or simple parallel ForEach-Object -Parallel when available. Record elapsed ms for both; assert completion & reasonableness (parallel not > sequential * 2). Skip parallel portion under Windows PowerShell 5.1.

## Ephemeral Database Pattern
All new tests rely on helper `New-TaskDbTempDb` (added to `TaskDb-TestCommon.ps1`) creating a throwaway DB path under `tests/.tmp/taskdb/<guid>/tasks.db`, running migrations (and optionally seeding/backlog) to isolate side effects.

## Future Enhancements (Deferred)
* Add `tasks.source_origin` column & migration with provenance tests.
* Provider mock abstraction that simulates transient write failures to exercise retry (not yet implemented in production code).
* Parallel ingestion using ForEach-Object -Parallel for larger backlog sets.
* Incremental export differential tests (baseline vs. changed snapshot hashing).

## Exit Criteria for This Phase
* All new test files execute without fatal errors.
* Logging baseline test confirms presence of required events.
* Provenance test confirms sidecar tagging artifacts.
* Negative tests demonstrate expected rejection behavior.
* Performance test emits timing data and does not fail (skip gracefully under PS5.1 for parallel section).

---
Generated: 2025-08-16T00:00:00Z
