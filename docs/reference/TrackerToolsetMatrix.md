# Tracker Toolset Coverage Matrix

| Phase | Objective | Existing Script/CLI | Notes | Gaps |
|-------|-----------|---------------------|-------|------|
| Initialize DB | Apply migrations | `cli/Invoke-TaskDbCli.ps1 migrate`, `scripts/Invoke-TaskMigrations.ps1` | Emits migration_file + snapshot | Add project/sprint migration extensions (future) |
| Seed | Seed master tasks | `cli ... seed`, `scripts/Seed-Tasks.ps1` | seed_input + seed_delta artifact events | None immediate |
| Backlog Import | CSV backlog ingest | `cli ... backlog`, `scripts/Migrate-TasksBacklog.ps1` | backlog_input + backlog_delta | None immediate |
| Create Task | Add task row | `cli ... add`, `New-TaskDbTask` | task_row artifact | Wrapper for bulk add optional |
| Update Task | Update fields | `cli ... update`, `Update-TaskDbTask` | mutation_result + task_row artifact | Add explicit changed fields diff artifact (optional) |
| Status Transition | Change status | `cli ... status`, `Set-TaskDbStatus` | task_row artifact | Duration enrichment post-processing (future) |
| Delete Task | Remove task | `cli ... delete`, `Remove-TaskDbTask` | logical task_deletion event | Soft-delete pattern (future) |
| List/Query | List/filter tasks | `cli ... list`, `Get-Tasks.ps1` | read_only decision | Add advanced filters later |
| History | Status history | `cli ... history`, `Get-TaskDbStatusHistory` | read_only | Add duration auto calc artifact (optional) |
| Summary Metrics | Quick aggregate | `cli ... summary` | console object | Emit artifact_emit? (optional) |
| Report | Detailed report | `cli ... report` | report json + md artifacts | Add risk trend metrics |
| Export | Export tasks | `cli ... export` | artifact_emit export file | Add JSONL variants optional |
| Diagnose | Diagnostic snapshot | `cli ... diagnose`, `Diagnose-TaskDb.ps1` | artifact_touch_batch pre | Add structured output artifact |
| Governance | Drift / completeness | `Detect-TrackerSchemaDrift.ps1`, `Verify-TaskDbCompleteness.ps1` | outside CLI currently | Integrate CLI subcommands (future) |
| Metrics | Compute metrics | `Compute-TrackerMetrics.ps1` | offline script | Add CLI hook (future) |
| Migration Snapshot | schema_versions snapshot | `cli ... migrate` extended logging | snapshot artifact covered by new test | None |

## Next Enhancements
- Add project/sprint CRUD DAL + CLI commands.
- Introduce governance/metrics CLI subcommands.
- Optional: emit summary/report JSONL transforms for analytics ingestion.
