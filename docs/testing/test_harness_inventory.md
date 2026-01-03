# Test Harness Inventory

Generated inventory of current test harness entry points (Python & PowerShell).

| Harness                         | Type       | Path                                    | Purpose                                                | Status         | Notes                               |
| ------------------------------- | ---------- | --------------------------------------- | ------------------------------------------------------ | -------------- | ----------------------------------- |
| run_tests.py                    | Python     | python/run_tests.py                     | Canonical unified pytest harness (batching, structlog) | active         | Use --batch-size for batching       |
| orch/run_tests.py               | Python     | python/orch/run_tests.py                | Back-compat shim delegating to canonical               | consider-prune | Remove after consumers updated      |
| Run-PythonTests.ps1             | PowerShell | scripts/Run-PythonTests.ps1             | Legacy invocation wrapper                              | deprecate      | Prefer direct `python run_tests.py` |
| Run-QualityGates.ps1            | PowerShell | Run-QualityGates.ps1                    | Aggregated quality gates orchestrator                  | active         | May call Python + Pester            |
| Run-AllChecks.ps1               | PowerShell | Run-AllChecks.ps1                       | Broad legacy check runner                              | deprecate      | Split into targeted tasks           |
| Run-NormalizationTests.ps1      | PowerShell | Run-NormalizationTests.ps1              | Data normalization tests (PowerShell)                  | review         | Could fold into pytest if ported    |
| Run-MockCacheTest.ps1           | PowerShell | Run-MockCacheTest.ps1                   | Mock cache validation                                  | review         | Evaluate merging into unit tests    |
| Run-AdditionalAnalyzerTests.ps1 | PowerShell | scripts/Run-AdditionalAnalyzerTests.ps1 | Extra analyzer checks                                  | review         | Consolidate into quality gates      |

## Missing / Recommended Harnesses

| Recommended               | Rationale                             | Proposed Path                       | Notes                              |
| ------------------------- | ------------------------------------- | ----------------------------------- | ---------------------------------- |
| Smoke test harness        | Fast critical-path validation (<30s)  | python/harness/smoke_tests.py       | Collect subset markers             |
| Performance micro harness | Timing hot paths to watch regressions | python/harness/perf_micro.py        | Use pytest-benchmark if allowed    |
| Integration harness       | External service / DB boundary tests  | python/harness/integration_tests.py | Mark with @pytest.mark.integration |
| Logging coverage harness  | Validate logging baseline events      | python/harness/logging_coverage.py  | Parses JSONL and asserts baseline  |

## Pruning Recommendations

- Remove `python/orch/run_tests.py` after downstream references updated.
- Delete `scripts/Run-PythonTests.ps1` once CI calls canonical runner directly.
- Migrate logic from `Run-AllChecks.ps1` into discrete tasks or Python scripts and retire file.
- Evaluate porting PowerShell-only normalization and mock tests into Python for consistency.

## Machine-Readable Manifest

See `build/artifacts/tests/harness_inventory.json` for structured data (generated).
