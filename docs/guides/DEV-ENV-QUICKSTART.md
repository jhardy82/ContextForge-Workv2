# Developer Environment Quickstart (Python + PowerShell)

Purpose: Fast, repeatable setup aligned with workspace `.vscode/settings.json` and ContextForge methodology (Python-first for analytics/governance, PS7 preferred; WinPS 5.1 reserved for legacy SCCM modules).

## 1. Prerequisites
- Python 3.11.x installed (on PATH)
- PowerShell 7 (`pwsh`) installed (`C:/Program Files/PowerShell/7/pwsh.exe`)
- Git, VS Code + Python, Pylance, Ruff, PowerShell extensions
- (Optional) `pip install --upgrade pip setuptools wheel`

## 2. Create / Recreate Virtual Environment

```pwsh
# From repo root
Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue  # optional reset
python -m venv .venv
# Activate (PowerShell)
& .\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e .[dev]  # fallback: pip install -r requirements.txt
```

## 3. VS Code Interpreter Selection
Command Palette: "Python: Select Interpreter" → choose `.venv` entry.
Settings reference: `python.defaultInterpreterPath = .venv/Scripts/python.exe` (workspace scoped).

## 4. Testing & Quality

```pwsh
# Run all pytest suites (fast path)
python -m pytest -q
# With coverage
python -m pytest --cov --cov-report=term-missing
# Pester (PowerShell tests)
pwsh build/Run-PesterTests.ps1 -Suite Gate -NonInteractive
```

Coverage thresholds: Python ≥80% (config in pyproject), PowerShell ≥70% (governance standard).

## 5. Linting & Type Checking

```pwsh
# Ruff (lint + format suggestions)
ruff check .
# Auto-fix safe issues
ruff check --fix .
# Type checking (strict mode enforced in workspace)
mypy .
```

`python.analysis.typeCheckingMode = strict` ensures IDE surfacing; mypy is the authoritative batch gate.

## 6. Performance & Indexing
Workspace excludes heavy / transient folders: `.venv`, `__pycache__`, `.mypy_cache`, `.pytest_cache`, `logs`. Diagnostic mode: `openFilesOnly` to reduce initial indexing cost.

## 7. Environment Variables
Use `.env` at repo root (gitignored) for transient configuration. Referenced by `python.envFile` in workspace settings. Do NOT store secrets in logs or commit them.

## 8. Tracker / DB Authority
`trackers/DB_AUTHORITY.SENTINEL` present → mutate tasks via Python dbcli only (avoid direct CSV edits). (Future: document dbcli usage once script path stabilized.)

## 9. Regeneration / Troubleshooting

| Symptom | Action |
|--------|--------|
| Missing imports / stale stubs | Delete `.mypy_cache` & `.pytest_cache`; reopen VS Code |
| Pylance unresolved module | Confirm `python.analysis.extraPaths` covers path; else add or adjust package install |
| Ruff not formatting | Ensure Ruff extension enabled; run `ruff check --fix` |
| mypy spurious errors after upgrade | Clear caches + recreate `.venv` |

## 10. CI Parity Expectations
Local steps must mirror CI: direct `python` invocation (no pwsh wrapper) and structured logging events (session_start → session_summary). Failing to emit baseline logging is a defect.

## 11. PowerShell Notes
Prefer PS7 for new scripts; tag host policies in headers (`# HostPolicy: ModernPS7`). Use WinPS 5.1 only when a module lacks PS7 support (`# HostPolicy: LegacyPS51` + `# HostFallbackReason:`). Keep destructive operations behind `-WhatIf` / `-Confirm`.

## 12. Future Enhancements (Not Yet Implemented)
- Automated `dbcli.py` quickstart section
- Pre-commit hook configuration (ruff + mypy + pytest subset)
- Scripted environment verification (`python scripts/verify_env.py`)

---
Last updated: 2025-08-28  (sync with `.vscode/settings.json` Python block).
