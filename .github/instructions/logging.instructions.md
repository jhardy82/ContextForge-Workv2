---
applyTo: "log*, logging*, evidence*, audit*, trace*"
description: "Unified logging standards, evidence protocols, and audit requirements"
---

# Logging Quick Reference

## Baseline Events (Required)

| Event | When | Required Fields |
|-------|------|-----------------|
| `session_start` | Begin work | `session_id`, `project_id` |
| `task_start` | Each unit begins | `task_id`, `task_name` |
| `decision` | Branch/choice point | `decision_type`, `selected`, `rationale` |
| `artifact_touch_batch` | Read files | `artifacts[]`, `count` |
| `artifact_emit` | Create/modify | `path`, `hash`, `size_bytes` |
| `warning` / `error` | Issues | `type`, `message` |
| `task_end` | Unit complete | `status`, `duration_seconds` |
| `session_summary` | End session | `tasks_completed`, `evidence_hash` |

**Coverage Target**: ≥90% of execution paths

## Python Implementation

```python
from python.ulog import ulog

ulog("session_start", session_id="QSE-001", project_id="P-001")
ulog("task_start", task_id="T-001", task_name="Implement auth")
ulog("decision", decision_type="branch", selected="oauth2", rationale="standard")
ulog("artifact_emit", path="auth.py", hash="sha256:abc...", size_bytes=4096)
ulog("task_end", status="success", duration_seconds=3600)
ulog("session_summary", tasks_completed=3, evidence_hash="sha256:xyz...")
```

## Evidence Bundle Structure

```
.QSE/v2/Evidence/{project_id}/{session_id}/
├── execution_plan.yaml
├── validation_results.json
└── evidence_bundle.jsonl  # SHA-256 hashed
```

## Full Reference
See `.github/instructions/archive/logging-full.md`

## Verification Logging (CRITICAL)

All verification commands MUST create evidence artifacts to prevent "Terminal Racing" and false claims.

1. **Format**: `logs/{topic}-{YYYY-MM-DD-HHMM}.txt`
2. **Procedure**:
   - Run command with output redirected to file (e.g., `> logs/test-results.txt 2>&1`).
   - USE `read_file` tool to inspect the log file (do not rely on terminal stdout).
   - Verify the COMPLETE content of the file.
3. **Citation**: Every verification claim MUST reference the log file path.
4. **Zero-Claim Checkpoint**: If claiming "zero errors" or "no matches", perform a secondary verification with a different method and document both.

Example:
```powershell
uv run pytest --cov=taskman_api > logs/pytest-coverage-20251229-1000.txt 2>&1
```
Then: `read_file("logs/pytest-coverage-20251229-1000.txt")`
Then: Make claim citing the log file.
