# VS Code Tasks Refactor: Audit, Changes, and Usage

## What changed

- Global pwsh shell and root options configured in `.vscode/tasks.json` with `dependsOrder: sequence`.
- Deterministic background readiness using `problemMatcher.background` for:
  - FastAPI: waits for `[pid-runner] Server starting` then `Application startup complete`.
  - API monitor: streams `api_monitor_tick` and ends on `api_monitor_failed`.
  - Heartbeat server: prints `[heartbeat] server_start`; also logs `readiness_status`.
  - Background watcher: begins on `Starting background task watcher` and ends on `session_summary`.
- Kept existing canonical tasks; improved JSONC formatting and sequencing.
- Added helper scripts:
  - `scripts/Backup-TasksJson.ps1` to snapshot tasks.json with SHA256 and git HEAD into `.vscode/backups/` and log JSONL evidence.
  - `scripts/Accept-TasksRefactor.ps1` to emit acceptance events (`refactor_tasks_json_applied`, `background_ready_confirmed`, `tm_api_verify_pass`).

## Why

- Make background tasks reliable in VS Code by gating on concrete, emitted lines.
- Standardize shell invocation and options to reduce per-task boilerplate.
- Provide auditable evidence for changes and a quick acceptance flow.

## How to use

- Backup current tasks.json:
  - Run the task "Governance: Instructions Compliance" first to ensure repo health (optional).
  - Run PowerShell: `pwsh -NoProfile -File scripts/Backup-TasksJson.ps1`.
- Start background services deterministically:
  - Run task "API: Start FastAPI Server (Background)"; it will show ready after uvicorn prints startup complete.
  - Run task "Monitoring: Start Heartbeat Server (Background)"; it will show ready after `[heartbeat] server_start`.
- Verify acceptance:
  - `pwsh -NoProfile -File scripts/Accept-TasksRefactor.ps1` writes logs under `logs/ops/`.

## Audit and verification

A lightweight audit script validates `.vscode/tasks.json` against key rules:

- DUP-001: duplicate task labels
- SHELL-002: pwsh only; avoid python via wrappers; no global shell override
- BG-003: background tasks must have problemMatcher.background begins/ends
- PY-004: direct Python via `.venv\\Scripts\\python.exe`
- PATH-005: options.cwd present (task or root)
- EXIT-006: shell tasks include `-NoProfile -ExecutionPolicy Bypass`
- DEP-007: python process tasks depend on `Env: Ensure .venv`
- FMT-008: JSONC parseable

Artifacts:

- JSON: `build/artifacts/audit/tasks_json_audit.json`
- JSONL: `logs/ops/tasks_json_audit.jsonl`

Run:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\Audit-TasksJson.ps1
```

## Notes

- tasks.json remains JSONC; comments document the readiness patterns.
- If uvicorn output format changes, update the `endsPattern` to match the new readiness line.
- Heartbeat server emits both JSONL events and a plain line for editors to match.
