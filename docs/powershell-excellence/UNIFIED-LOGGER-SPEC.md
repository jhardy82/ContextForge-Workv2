# Unified Logger Specification

**Version**: 1.0.0
**Last Updated**: 2025-12-29
**Status**: Reference Implementation

---

## Executive Summary

Cross-language logging specification for ContextForge systems. Ensures consistent observability across Python, PowerShell, and TypeScript components with JSONL output format.

## Reference Implementation

**Python**: `python/services/unified_logger.py`
**Framework**: structlog with JSONL serialization

## Core Event Schema

### Required Fields (All Events)

```json
{
  "timestamp": "2025-12-29T14:30:00.000Z",
  "level": "info",
  "event": "event_type",
  "cf_trace_id": "uuid-v4",
  "cf_session_id": "uuid-v4",
  "cf_project_id": "PROJECT-001"
}
```

### Trace Context Environment Variables

| Variable | Purpose | Format |
|----------|---------|--------|
| `CF_TRACE_ID` | Distributed trace correlation | UUID v4 |
| `CF_SESSION_ID` | Session boundary tracking | UUID v4 |
| `CF_PROJECT_ID` | Project association | `PROJECT-###` |

## 8 Baseline Events

### 1. session_start

```json
{
  "event": "session_start",
  "session_id": "abc123",
  "project_id": "PROJECT-001",
  "agent_type": "copilot|claude|cursor",
  "environment": "vscode|terminal|ci"
}
```

### 2. task_start

```json
{
  "event": "task_start",
  "task_id": "TASK-042",
  "task_title": "Implement authentication",
  "parent_session": "abc123"
}
```

### 3. decision

```json
{
  "event": "decision",
  "decision_type": "branch|reuse|architecture",
  "choice": "selected_option",
  "alternatives": ["option_a", "option_b"],
  "rationale": "Brief explanation"
}
```

### 4. artifact_touch_batch

```json
{
  "event": "artifact_touch_batch",
  "operation": "read",
  "artifacts": [
    {"path": "src/main.py", "lines": [1, 50]},
    {"path": "tests/test_main.py", "lines": [1, 100]}
  ],
  "count": 2
}
```

### 5. artifact_emit

```json
{
  "event": "artifact_emit",
  "path": "src/new_feature.py",
  "operation": "create|modify|delete",
  "size_bytes": 2048,
  "hash": "sha256:a1b2c3..."
}
```

### 6. warning

```json
{
  "event": "warning",
  "code": "W001",
  "message": "Deprecated API usage detected",
  "context": {"file": "src/legacy.py", "line": 42}
}
```

### 7. error

```json
{
  "event": "error",
  "code": "E001",
  "message": "Connection timeout",
  "exception_type": "TimeoutError",
  "stack_trace": "...",
  "recoverable": true
}
```

### 8. session_summary

```json
{
  "event": "session_summary",
  "session_id": "abc123",
  "duration_seconds": 1847,
  "tasks_completed": 3,
  "tasks_failed": 0,
  "artifacts_created": 5,
  "artifacts_modified": 12,
  "warnings": 2,
  "errors": 0,
  "evidence_bundle": "sha256:d4e5f6..."
}
```

## Evidence Bundles

### Hash Format

All artifact hashes use SHA-256 with the `sha256:` prefix:

```
sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

### Evidence Bundle Structure

```json
{
  "bundle_id": "uuid-v4",
  "created_at": "2025-12-29T14:30:00.000Z",
  "session_id": "abc123",
  "artifacts": [
    {
      "path": "src/feature.py",
      "hash": "sha256:a1b2c3...",
      "size": 2048,
      "operation": "create"
    }
  ],
  "bundle_hash": "sha256:combined..."
}
```

## PowerShell Implementation

```powershell
function Write-CFLog {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [ValidateSet('session_start', 'task_start', 'decision',
                     'artifact_touch_batch', 'artifact_emit',
                     'warning', 'error', 'session_summary')]
        [string]$Event,

        [Parameter(Mandatory)]
        [ValidateSet('debug', 'info', 'warning', 'error')]
        [string]$Level,

        [hashtable]$Context = @{}
    )

    $logEntry = @{
        timestamp     = (Get-Date -Format 'o')
        level         = $Level
        event         = $Event
        cf_trace_id   = $env:CF_TRACE_ID ?? (New-Guid).ToString()
        cf_session_id = $env:CF_SESSION_ID ?? (New-Guid).ToString()
        cf_project_id = $env:CF_PROJECT_ID ?? 'UNKNOWN'
    }

    # Merge context
    foreach ($key in $Context.Keys) {
        $logEntry[$key] = $Context[$key]
    }

    # JSONL output (one line)
    $json = $logEntry | ConvertTo-Json -Compress -Depth 10

    # Write to stderr for structured logging
    [Console]::Error.WriteLine($json)

    # Also append to log file if configured
    if ($env:CF_LOG_PATH) {
        $json | Out-File -FilePath $env:CF_LOG_PATH -Append -Encoding utf8
    }
}

# Convenience functions
function Write-CFSessionStart {
    param([string]$ProjectId, [string]$AgentType = 'unknown')

    $env:CF_SESSION_ID = (New-Guid).ToString()
    $env:CF_TRACE_ID = (New-Guid).ToString()

    Write-CFLog -Event 'session_start' -Level 'info' -Context @{
        session_id  = $env:CF_SESSION_ID
        project_id  = $ProjectId
        agent_type  = $AgentType
        environment = if ($env:VSCODE_AGENT_MODE) { 'vscode' }
                      elseif ($env:CI) { 'ci' }
                      else { 'terminal' }
    }
}

function Write-CFArtifactEmit {
    param(
        [string]$Path,
        [ValidateSet('create', 'modify', 'delete')]
        [string]$Operation
    )

    $hash = $null
    $size = 0

    if (Test-Path $Path) {
        $content = Get-Content $Path -Raw -ErrorAction SilentlyContinue
        if ($content) {
            $bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
            $sha = [System.Security.Cryptography.SHA256]::Create()
            $hashBytes = $sha.ComputeHash($bytes)
            $hash = "sha256:" + [BitConverter]::ToString($hashBytes).Replace('-', '').ToLower()
            $size = $bytes.Length
        }
    }

    Write-CFLog -Event 'artifact_emit' -Level 'info' -Context @{
        path       = $Path
        operation  = $Operation
        size_bytes = $size
        hash       = $hash
    }
}
```

## Log File Locations

| Environment | Path |
|-------------|------|
| VS Code | `${workspaceFolder}/logs/cf-session-{date}.jsonl` |
| CI | `${CI_PROJECT_DIR}/logs/cf-pipeline-{id}.jsonl` |
| Terminal | `~/.contextforge/logs/cf-{date}.jsonl` |

## Validation Queries

```powershell
# Count events by type
Get-Content logs/*.jsonl |
    ConvertFrom-Json |
    Group-Object event |
    Select-Object Name, Count

# Find all errors in session
Get-Content logs/*.jsonl |
    ConvertFrom-Json |
    Where-Object { $_.event -eq 'error' }

# Calculate session duration
$logs = Get-Content logs/session.jsonl | ConvertFrom-Json
$start = $logs | Where-Object { $_.event -eq 'session_start' } | Select-Object -First 1
$end = $logs | Where-Object { $_.event -eq 'session_summary' } | Select-Object -First 1
($end.timestamp - $start.timestamp).TotalSeconds
```

---

*"Logs are the source of truth—structure them for machines, read them for wisdom."*
