# Copilot Instructions – Workspace Quick Pointers (Repo-Bound Addendum)

Date: 2025-09-11
Status: Active (addendum; does not replace the global instructions)

This addendum ties the global Copilot instructions to concrete signals and paths in this repository so verification, logging, and execution behaviors are deterministic and reproducible.

## 1) Start-of-Prompt Verification (Python tests)

- Latest run pointer (authoritative):
  - `build/artifacts/tests/python/UNIFIED_POINTER.txt`
  - Example (current): `PYT-1757626350-2a2842`
- Run folder layout:
  - `<run>/summary.json` (totals, failures, args)
  - `<run>/junit.xml`, `<run>/debug.log`, `<run>/run_id.txt`
- Recent success list:
  - `build/artifacts/tests/python/success-runs.json` (retention window)
- Evidence to surface at session start:
  - run_id, total, failed_count, return_code, prior-success delta (if applicable)

Current snapshot (reference):

- run_id: PYT-1757626350-2a2842
- totals: total=1, failed_count=0, return_code=0
- previous success: PYT-1757625462-a28568 (total=3, failed=0)

## 2) Logging Gate (Baseline Events)

- Gate artifact: `build/artifacts/tests/logging_gate_report.json`
- Failure signature (observed): Missing baseline events: `session_end`, `session_summary`
- Required MVE events (baseline): session_start, task_start, decision, artifact_touch_batch, artifact_emit, warning/error, task_end, session_summary
- Action: Ensure UnifiedLogger (or equivalent) emits both `session_end` and `session_summary` for non‑trivial runs. If a wrapper or runner suppresses finalization, add a finally/atexit hook to flush these events on success and failure.

Acceptance check (fast): run the logging gate pytest and assert zero failures.

## 3) Direct Invocation & Environment

- Interpreter: `.venv` is the canonical environment; invoke Python directly (no nested pwsh wrappers)
- Examples (PowerShell 7+):
  - Python module: `.\\.venv\\Scripts\\python.exe -m pytest -vv --color=yes tests`
  - dbcli status: `.\\.venv\\Scripts\\python.exe dbcli.py status migration --json`
- UV managed: `uv.toml` (managed=true); `uv.lock` present. Keep the venv activated/used consistently.

## 4) Pytest Configuration Nuances

Two sources exist and may merge at runtime:

- `pyproject.toml` → `[tool.pytest.ini_options]` addopts: `-q -n auto --dist=loadfile --timeout=120 --durations=10`
- `pytest.ini` (root) addopts: `-q --color=yes --maxfail=25 --disable-warnings -k "not test_heartbeat_summary"`

Notes:

- Explicit CLI args (e.g., `-vv`) will override defaults for that invocation.
- To debug single tests, consider disabling xdist via `CF_DISABLE_XDIST=1` (sanitizer in `tests/conftest.py`).

## 5) Coverage Gate

- Config: `pyproject.toml` → `[tool.coverage.report] fail_under = 85`
- Source include: `src/`, `cli/python/cf_tracker`

## 6) Tracker Authority (DBCLI)

- Mandate: Interact via dbcli with direct Python invocation.
- Authority status: `.venv\\Scripts\\python.exe dbcli.py status migration --json`
  - Expect: `{ ok: true, sentinel_present: true, db_authority_file: "trackers\\DB_AUTHORITY.SENTINEL" }`
- Direct CSV mutation is prohibited once sentinel is present.

## 7) Host Policy Tags (for new/modified scripts)

Include at the top of reusable scripts:

```
# HostPolicy: ModernPS7
```

If a legacy constraint exists (WinPS 5.1), document it:

```
# HostPolicy: LegacyPS51
# HostFallbackReason: SCCM module requires 5.1
```

## 8) VS Code Extension (local integration)

- Manifest: `interface/vscode-extension/package.json`
  - engines.vscode: ">=1.91.0"
  - Commands: `contextforge.acceptBurst`, `contextforge.previewGaps`, `contextforge.showVarietyMetrics`, `contextforge.openFile`, `contextforge.explainBurst`
- Build scripts: `npm run compile` (TypeScript → `dist/extension.js`)

## 9) Quick Gate Runners (optional)

- VS Code tasks (when present) prefer direct `.venv` interpreter usage.
- Fast checks:
  - Quick pytest: `.\\.venv\\Scripts\\python.exe -m pytest -vv --color=yes tests`
  - Verbose pytest: `.\\.venv\\Scripts\\python.exe -m pytest -vv --maxfail=25`
  - Logging gate only: `.\\.venv\\Scripts\\python.exe -m pytest -vv --color=yes tests\\python\\test_logging_gate.py`

## 10) Remediation TODO (tracked outside this file)

- Emit `session_end` and `session_summary` in logging flows; re-run the logging gate test until green.
- Consolidate pytest addopts if conflicting behavior is observed (optional; document any change).

---

This addendum is intended to keep the global instructions stable while surfacing repository‑specific pointers and commands that satisfy the verification and governance mandates.
