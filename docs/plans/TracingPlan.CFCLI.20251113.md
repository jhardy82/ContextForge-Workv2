---
# Tracing Plan — CF_CLI Evidence and Correlation

WorkId: W-SPRINT-RENAME-001
Date: 2025-11-13

## Goals
- Emit structured JSONL for each CLI operation (start, success/fail, duration)
- Include correlation IDs (QSE-YYYYMMDD-HHMM-UUID) and sha256 hashes of artifacts
- Keep logs under `logs/` and evaluations under `logs/evaluations/`

## Fields
- timestamp (RFC3339)
- event (start|success|error)
- command (string)
- args (array)
- cwd (string)
- correlation_id (string)
- evidence_files (array of {path, sha256})
- duration_ms (number)
- result_excerpt (string)

## Practices
1. Log before and after each step in EvaluationPlan.*
2. Hash any produced JSON artifacts (exports, temp_sprint_upsert_dryrun.json)
3. Use Windows-safe paths and avoid paging in commands
4. Keep per-run logs small and rotate by date

## Example JSONL Entry
```json
{"timestamp":"2025-11-13T19:28:00Z","event":"start","command":"python cf_cli.py sprint upsert","args":["--id","S-CF-Work-MCP-STDIO-Test-Baseline","--title","MCP STDIO Test Baseline","--status","planned","--dry-run","--json"],"cwd":"c:/Users/james.e.hardy/Documents/PowerShell Projects","correlation_id":"QSE-20251113-1928-3a3f","evidence_files":[]}
```

## Next Steps
- Optionally add a small PowerShell wrapper to write JSONL entries per step
- Consider integrating with existing unified logging if present
