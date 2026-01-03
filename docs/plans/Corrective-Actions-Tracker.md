# Corrective Actions Tracker (Orchestration & Logging)

Generated: 2025-08-18T00:00:00Z (placeholder)
Source Plan: `plans/Immediate-Corrective-Actions-Orchestration-Logging.md`

Status Legend:
- Open: Not started
- Partial: Some implementation present; not validated end-to-end
- InProgress: Active work (validation / finishing touches)
- Complete: Implemented & validated (meets acceptance)

| ID  | Category   | Status    | Progress Notes (delta) |
|-----|------------|-----------|------------------------|
| A1  | Schema     | Complete  | Migrations 0001 & 0002 applied via `python.orch.migrator` (events: migration_applied, migrations_complete). |
| A2  | Ingestion  | Partial   | Gating logic added to `Populate-OrchestrationDb.ps1`; blocked pending A1 live apply & run validation. |
| A3  | Logging    | Partial   | `task_end` duration logic added; awaiting runtime verification. |
| A4  | Logging    | InProgress| artifact_emit added to loader & projection (verify hashes stable). |
| A5  | Coverage   | Open      | No guaranteed command_end wrapper implemented. |
| A6  | Noise      | Partial   | Error aggregation function added; not stress-tested. |
| A7  | Reporting  | Open      | Host policy enrichment not added to projections/ingestion. |
| A8  | Validation | Open      | Post-fix coverage scan not executed (dependencies incomplete). |
| A9  | Metrics    | InProgress| Metrics emission added in loader (events_inserted/skipped/parse_errors); initial errors resolved; verify row presence next. |
| A10 | Tests      | Partial   | Python migration test exists; task DB + negative/hash mismatch tests missing. |
| C1  | Projection | InProgress| Projection table applied (0002); projection_update processed 60 events (log entries). Row count currently 5 (needs reconciliation). |
| C2  | Projection | InProgress| Loader + updater executed on live DB (events: loader_start/loader_end, projection_update). Need verification of why only 5 rows vs 60 processed events. |
| C3  | Projection | InProgress| Reconciliation script `python.orch.reconcile_projection` added; emits projection_reconciliation + metrics (optional). Pending validation & integration into quality chain. |
| C4  | Metrics    | InProgress| projection_distinct_tasks, projection_rows, projection_drift_tasks metrics added; drift_alert emits on non-zero. |

## Immediate Next Validation Targets
1. Run Python migrator against real orchestration DB (promote A1 to InProgress → Complete).
2. Execute ingestion to confirm A2/A3/A6/A9 behavior; update statuses accordingly.
3. Add task DB migration test + hash mismatch simulation (advance A10).
4. Introduce projection table migration (0002_TaskProjection.sql) to move C1 forward.

## Exit Criteria Snapshot
Pending: No items have met full acceptance validation yet; earliest candidates after steps above are A1, A2, A3, A6, A9.

## Update Procedure
- Modify this file when an item transitions status.
- Add concise evidence reference (log snippet, test name) when marking Complete.

---
(Tracker auto-created by assistant on user request confirmation.)
