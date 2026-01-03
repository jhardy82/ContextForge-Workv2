# Tracker Validation Execution Guide

## Overview
Describes how to run tracker framework validation in environments with or without Pester 5.x.

## Modes

| Mode | Command | Requirements | Output |
|------|---------|-------------|--------|
| Auto (default) | `pwsh ./scripts/Invoke-TrackerValidationShim.ps1` | Optional Pester >=5 | Pester summary or light JSON report |
| Pester | `pwsh ./scripts/Invoke-TrackerValidationShim.ps1 -Mode Pester` | Pester >=5 | Pester summary |
| Light | `pwsh ./scripts/Invoke-TrackerValidationShim.ps1 -Mode Light` | None | JSON file under `logs/tracker-validation/` |

## Lightweight Runner Output
JSON schema:

```json
{
  "status": "pass|fail",
  "total_checks": 11,
  "passed": 11,
  "failed": 0,
  "timestamp_utc": "2025-08-18T12:20:00.0000000Z",
  "checks": [ { "id": "task.primary", "passed": true, "description": "Task schema includes primary_sprint" } ]
}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | One or more checks failed |
| >1 | Script/thrown error |

## Common Issues

| Symptom | Cause | Resolution |
|---------|-------|-----------|
| Pester tests skipped | Only Pester 3.x present | Use `-Mode Light` or install Pester 5+ |
| No JSON output | Light mode not executed | Force `-Mode Light` |
| Fail: shared_components missing | Instructions not updated | Re-run schema insertion step |

## Recommended CI Step

```powershell
pwsh ./scripts/Invoke-TrackerValidationShim.ps1 -Mode Auto
```

Treat non-zero exit as build failure.

## Change Log
- 2025-08-18: Initial guide.
