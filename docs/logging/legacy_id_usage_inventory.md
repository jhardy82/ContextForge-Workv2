# Legacy ID Usage Inventory

Generated: 2025-09-19
Scope: Occurrences of legacy globals `_RUN_ID` / `_CORR_ID` and related environment propagation outside the new lazy accessor core.

## Summary
- Core implementation now uses ContextVar-backed `get_run_id()` / `get_correlation_id()` in `src/unified_logging/core.py`.
- Remaining legacy symbol touch points are limited to the backward compatibility facade `src/unified_logger.py` and `src/unified_logging/__init__.py` interception.
- Test suite intentionally references legacy names to validate deprecation bridge.
- Additional scripts still synthesize run IDs directly (`RUN-`, `PYT-`, `STAT-`) – candidates for optional future unification but not blocking modernization goal.

## Direct Legacy Globals
File | Lines | Notes
---- | ----- | -----
`src/unified_logger.py` | 113-114, 346, 422-428, 442-456 | Facade caches first resolved values to preserve legacy module expectations.
`src/unified_logging/core.py` | 93-94 (comment), 572-580, 590-598 | Internal tracking; legacy names retained only for backward compat references.
`src/unified_logging/__init__.py` | 44, 68-69, 78-80 | `__getattr__` deprecation handling.

## Test References (Expected)
File | Purpose
---- | -------
`tests/python/test_unified_logging_ids.py` | Validates legacy vs new accessor parity.
`tests/python/test_unified_logger_run_id.py` | Environment override coverage.
`tests/python/test_unified_logging_ids_governance.py` | Governance uniqueness gate.

## Indirect / Environment Propagation
File | Pattern | Action
---- | ------- | ------
`python/logging/artifacts.py` | Sets `UNIFIED_RUN_ID` from CF_TEST_RUN_ID or timestamp | Acceptable; could migrate to accessor later.
`python/run_tests.py` | Exports `CF_TEST_RUN_ID` for pytest child processes | Required for deterministic test grouping.
`python/pytest_plugins/unified_reporting.py` | Generates `PYT-` prefixed ID and sets `UNIFIED_RUN_ID` | Candidate for accessor migration after stability window.
`python/logging/setup_structlog.py` | Local run id caching `_CURRENT_RUN_ID` | Legacy; outside immediate modernization scope.

## Migration Assessment
Category | Count | Migration Required Now
-------- | ----- | ----------------------
Critical legacy globals outside core/facade | 0 | No
Intentional facade/test references | 1 facade, multiple tests | No (by design)
Script direct run id generation | ~6 scripts | Optional follow-up

## Recommendations
1. Proceed with deprecation warnings implementation (next tasks) – inventory complete.
2. Defer unifying run id synthesis in peripheral scripts until after PowerShell parity & hash chain test updates.
3. Add section in forthcoming `docs/logging-id-migration.md` referencing this inventory with link.

---
This file serves as the evidence artifact for `inventory-static-id-usage` task.
