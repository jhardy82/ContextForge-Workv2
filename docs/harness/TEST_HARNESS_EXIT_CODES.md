# Test Harness Exit Codes

Source: `python/run_tests.py`

| Code | Meaning | Trigger Examples | Action |
|------|---------|------------------|--------|
| 0 | Success | All selected tests collected and passed | Proceed normally |
| 2 | Tests directory missing | `tests/` not found | Create tests directory or adjust path |
| 3 | Environment error | Virtual env / dependency bootstrap failure | Inspect env manifest, reinstall deps |
| 4 | Dependency mismatch (parity) | `validate_uv_parity.py` mismatch | Run parity sync / update lock |
| 6 | JUnit artifact missing | Post-run artifact check failed | Re-run with `--no-clean`, inspect logs |
| 7 | Collection preflight failed (zero match) | Selector expansion yields no nodeids | Correct selector or run without filter |
| 9 | Serialization lock active | Another test run holding lock | Wait or remove stale lock if safe |

## Notes
- Selector expansion converts bare test function names into fully-qualified nodeids prior to collection. A 7 exit code now surfaces clearly in `show_latest_test_summary.py` output with `early_exit_reason`.
- Always inspect `summary.json` for `early_exit_reason` when non-zero exit codes occur.
- Exit codes >100 are reserved for future governance gates.

## Maintenance
Update this file when new exit codes are introduced or semantics change.
