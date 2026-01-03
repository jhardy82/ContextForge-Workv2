# Test Domain Inventory (Initial Decomposition)

Generated: 2025-08-26T05:35:00Z

Domains Identified:

| Domain | Purpose | Primary Tests (current filenames) | Gaps / Notes |
|--------|---------|------------------------------------|--------------|
| CRUD Core | Basic task lifecycle (create/read/update/delete/restore) | test_api_tasks.py, test_crud_roundtrip.py, test_soft_delete_restore.py | Need MPV anchors on create/update/delete assertions |
| Extended Endpoints | Labels, acceptance, quality gates, actions, stats, export | test_api_extended.py | Currently failing some cases (investigate) |
| Parity & Search | REST vs CLI parity, advanced filters, drift detection | test_api_search_parity.py, test_tasks_parity.py, test_list_filters.py | Add explicit @pytest.mark.mpv on zero-drift assertion |
| Audit Trail | Field-level audit entries | test_api_audit.py, test_audit_delete.py | Add MPV anchor for \_\_create\_\_/deleted_at coverage |
| Logging Baseline | Unified logger structure & event presence | test_unified_logger*.py, test_logging_paths.py | Add enforcement plugin (T-LOGGING-MPV-AUTO) |
| Migration & Schema | DB schema creation, migrations idempotency | test_tasks_migration.py, test_migrator_and_projection.py | Mark critical migration invariants with anchors |
| Coverage & Quality Gates | Coverage scan + reporting | test_coverage_scan.py | Integrate with quality gate patch endpoint to update trackers |
| CLI Integration | CLI CRUD & analysis parity | test_cli_analyze_integration.py | Ensure MPV marker on CLI vs REST equivalence assertions |
| DuckDB Builders | Incremental / CID builder behavior | test_duckdb_builder_*.py | Not in current task scope (future decomposition) |
| Validation & Failure Handling | Negative cases / validation failures | test_validation_failure.py | Anchor at expected failure patterns |

Planned MPV Anchors (Prefix `# MPV:` in tests):
- CRUD_CREATE_OK
- CRUD_UPDATE_STATUS
- CRUD_SOFT_DELETE
- EXT_LABEL_PATCH
- EXT_ACCEPTANCE_REPLACE
- EXT_QUALITY_GATES_PATCH
- EXT_ACTION_RECORD
- EXT_STATS_COUNTS
- EXT_EXPORT_YAML
- PARITY_ZERO_DRIFT
- AUDIT_CREATE_ENTRY
- AUDIT_DELETE_FIELD
- MIGRATION_IDEMPOTENT
- COVERAGE_THRESHOLD
- CLI_PARITY_LIST

Next Actions:
1. Inject anchors into listed tests.
2. Introduce @pytest.mark.mpv to mark anchor-bearing tests.
3. Implement logging/MPV enforcement plugin.
4. Update tracker tasks with actions_taken referencing domain mapping.
