<!-- markdownlint-disable-file -->

# PyTest Harness: Usage, Timeout Semantics, and Artifacts

This document describes the unified pytest harness (`python/run_tests.py`), how to use it, how timeouts are signaled, and which artifacts are produced for CI consumption.

## Overview

The harness standardizes pytest execution and artifact emission across the repo:

- Invokes pytest with sensible defaults (`-vv --maxfail=25` by default)
- Emits artifacts under `build/artifacts/tests/python/<run_id>/`
  - `junit.xml` (when executing tests)
  - `summary.json` (always, guarded)
  - `summary.txt` (human-readable snippet)
  - `heartbeat.json` (if heartbeat is enabled)
- Maintains pointers and rolling history
  - `build/artifacts/tests/python/latest-run-started.txt`
  - `build/artifacts/tests/python/latest-runs.json`

## CLI

Run the harness with either positional test targets or explicit flags:

- Positional targets (files/dirs/nodeids):
  - `python/run_tests.py tests/python/test_foo.py`
- Explicit targets (aliases):
  - `-t`, `--target <path-or-nodeid>`
  - `--test <path-or-nodeid>` (alias for adapter compatibility)
- Collection-only:
  - `--list-only` (no execution; emits minimal `summary.json`)
- Filtering:
  - `-k <expr>` (standard pytest -k expression)
- Batching:
  - `--batch-size <N>` (execute targets in chunks; summary aggregates and records `worst_rc`)
  - `--max-batches <M>` (optional limit)
- Heartbeat (opt-in):
  - `--enable-heartbeat` / `--disable-heartbeat`
  - `--heartbeat-interval <seconds>` (used only when enabled)
- Output quieting:
  - `--ci-quiet` (suppress console echo; artifacts still written)
- Coverage:
  - `--no-cov` (disable coverage integration if otherwise enabled)

Environment toggles:

- `CF_CI_QUIET=1` (quiet output)
- `CF_ENABLE_HEARTBEAT=1` / `CF_DISABLE_HEARTBEAT=1`
- `PYTHONIOENCODING=utf-8` (forced by harness for child process)

## Timeout Semantics (rc=124)

Pytest itself has no native timeout exit code (its exit codes are 0..5). The harness maps a subprocess timeout to a distinct non-zero `return_code` to make CI signaling explicit and stable:

- The child pytest process is executed via `subprocess.run(..., timeout=...)`.
- When a timeout is hit, Python raises `subprocess.TimeoutExpired`.
- The harness catches this and returns `rc=124` by convention.
- This value is then propagated to artifacts.

Controlling the timeout:

- Set `CF_PYTEST_TIMEOUT_SEC` (string float) to control the harness-level timeout for the child pytest process.
  - Example: `CF_PYTEST_TIMEOUT_SEC=1.0` forces a very short timeout for test runs.

Artifacts on timeout:

- `summary.json` is guaranteed to exist (via normal write or final guard) and must include a non-zero `return_code` (typically `124`).
- `latest-runs.json` will have an entry for the run with a `return_code`.
- `junit.xml` may be absent or incomplete when the run times out.

## Artifacts and Schema

Key artifact locations:

- `build/artifacts/tests/python/<run_id>/summary.json`
- `build/artifacts/tests/python/<run_id>/junit.xml` (when available)
- `build/artifacts/tests/python/latest-runs.json`
- `build/artifacts/tests/python/latest-run-started.txt` (pointer)

`summary.json` (single-run shape):

- `run_id` (string)
- `return_code` (int) — non-zero indicates failure; `124` means timeout
- `total`, `failed_count`, `failures` — counts/list (may be `0`/`None` on timeout)
- `explicit_tests` (list[str]) — the explicit targets provided
- `pytest_args` (list[str]) — args used to invoke pytest
- `progress_updates` (int)
- `heartbeat_enabled` (bool), `heartbeat_reason` (str; optional), and `heartbeat_path` (string; optional)
- `batched` (bool), and in batched runs, `batches` with per-batch metadata and `return_code`
- `rich_progress` — object with `enabled`, `forced`, `reason_disabled`
- `tests_per_sec`, `tests_per_sec_ema`, `tests_per_sec_peak`, `tests_per_sec_avg` — placeholders (null)

`latest-runs.json`:

- Rolling history of runs under a top-level `runs` array
- Each entry includes `run_id` and `return_code` at minimum
- Updated at start and on completion (guarded)

## Examples

Force a timeout to validate artifacts:

```powershell
# Windows PowerShell / pwsh
$env:CF_PYTEST_TIMEOUT_SEC = "1.0"
.\.venv\Scripts\python.exe python\run_tests.py -t tests\python\test_harness_timeout_summary.py
```

Force collection-only:

```powershell
.\.venv\Scripts\python.exe python\run_tests.py --list-only -t tests\python
```

Batched run:

```powershell
.\.venv\Scripts\python.exe python\run_tests.py --batch-size 10 -t tests\python
```

## VS Code Python Test Adapter Compatibility

Some adapters/tools invoke the harness with `--test` when passing targets. The harness accepts both `--target` and `--test` to ensure discovery and execution paths are compatible.

If you encounter an adapter error like “Invalid test discovery output,” ensure you are on the current harness version with `--test` support, or call the harness directly as shown above.

## References

- Python subprocess: https://docs.python.org/3/library/subprocess.html
- Pytest exit codes: https://docs.pytest.org/en/stable/reference/reference.html#exit-codes
