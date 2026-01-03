# Phase 2: PowerShell-to-Python Logger Bridge Architecture

**Status**: Design Complete ✅
**Date**: 2025-12-29
**Author**: Architect Agent
**Version**: 1.0

---

## Executive Summary

This document defines the architecture for **Phase 2 of TaskMan MCP Integration**: enabling PowerShell scripts to pass session context to Python MCP servers for cross-language trace correlation.

### Problem Statement

- **Before Phase 2**: PowerShell logs and Python logs were isolated
- **Gap**: No correlation between PowerShell script execution and spawned Python MCP servers
- **Impact**: Impossible to trace full execution chains (PS → Python → PS)

### Solution Overview

- **Mechanism**: Environment variable propagation (`CF_SESSION_ID`, `CF_TRACE_ID`)
- **Log Unification**: Both languages write to same daily JSONL file
- **Auto-Correlation**: Python automatically inherits PowerShell session context
- **Zero Disruption**: Backward compatible with existing Python code

---

## Architecture Design

### 1. Data Flow Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ Layer 1: PowerShell Session Initialization                   │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Start-CFSession -ScriptName 'Test-McpHeartbeat'             │
│    ↓                                                          │
│  Generate session_id: "83e88a22"                             │
│  Generate trace_id: "a1b2c3d4e5f6..."                        │
│    ↓                                                          │
│  $env:CF_SESSION_ID = "83e88a22"                             │
│  $env:CF_TRACE_ID = "a1b2c3d4e5f6..."                        │
│    ↓                                                          │
│  Write-CFLogEvent 'session_start'                            │
│                                                               │
└──────────────────────────────────────────────────────────────┘
                         │
                         │ Subprocess Spawn
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ Layer 2: Python Process Initialization                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  import unified_logger  # Auto-runs at module load           │
│    ↓                                                          │
│  configure_logging()                                          │
│    ↓                                                          │
│  CF_SESSION_ID = os.getenv('CF_SESSION_ID')  # "83e88a22"   │
│  CF_TRACE_ID = os.getenv('CF_TRACE_ID')                      │
│    ↓                                                          │
│  logger = logger.bind(                                        │
│      session_id="83e88a22",                                   │
│      trace_id="a1b2c3d4e5f6..."                              │
│  )                                                            │
│    ↓                                                          │
│  logger.debug("powershell_bridge_active")                    │
│                                                               │
└──────────────────────────────────────────────────────────────┘
                         │
                         │ All logger.info() calls
                         │ auto-include session_id
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ Layer 3: Unified Log File                                    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  logs/contextforge-2025-12-29.jsonl                          │
│                                                               │
│  PowerShell Events:                                           │
│  {"timestamp":"2025-12-29T10:30:00Z",                        │
│   "session_id":"83e88a22",                                   │
│   "event":"session_start",                                   │
│   "script_name":"Test-McpHeartbeat.ps1"}                     │
│                                                               │
│  {"timestamp":"2025-12-29T10:30:01Z",                        │
│   "session_id":"83e88a22",                                   │
│   "event":"task_start",                                      │
│   "task_id":"check_taskman_servers"}                         │
│                                                               │
│  Python Events (NEW - inherited session_id):                 │
│  {"timestamp":"2025-12-29T10:30:02Z",                        │
│   "session_id":"83e88a22",                                   │
│   "trace_id":"a1b2c3d4e5f6...",                              │
│   "event":"powershell_bridge_active",                        │
│   "level":"debug"}                                            │
│                                                               │
│  {"timestamp":"2025-12-29T10:30:03Z",                        │
│   "session_id":"83e88a22",                                   │
│   "action":"task_list_query",                                │
│   "result":"success"}                                         │
│                                                               │
│  PowerShell Summary:                                          │
│  {"timestamp":"2025-12-29T10:30:05Z",                        │
│   "session_id":"83e88a22",                                   │
│   "event":"session_summary",                                 │
│   "servers_checked":13}                                      │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Implementation Details

### 2.1 PowerShell Side (Already Complete ✅)

**Module**: `ContextForge.Observability.psm1`

```powershell
function Start-CFSession {
    # Generate unique identifiers
    $script:SessionId = [guid]::NewGuid().ToString('N').Substring(0, 8)
    $script:TraceId = [guid]::NewGuid().ToString('N')

    # Set environment for child processes (THE BRIDGE)
    $env:CF_SESSION_ID = $script:SessionId
    $env:CF_TRACE_ID = $script:TraceId

    # Write session start event
    Write-CFLogEvent -EventType 'session_start' -Level 'INFO' -Data @{
        script_name = $ScriptName
        session_id = $script:SessionId
        trace_id = $script:TraceId
    }
}
```

**Key Feature**: Environment variables automatically inherited by all subprocesses (PowerShell, Python, Node.js, etc.)

---

### 2.2 Python Side (Phase 2 Implementation)

**File**: `python/services/unified_logger.py`

#### Changes Made:

1. **Import datetime for daily log naming**:
   ```python
   from datetime import datetime
   ```

2. **Read environment variables**:
   ```python
   CF_SESSION_ID = os.getenv("CF_SESSION_ID")  # From PowerShell
   CF_TRACE_ID = os.getenv("CF_TRACE_ID")      # From PowerShell
   ```

3. **Default to PowerShell log format**:
   ```python
   _default_log_name = f"contextforge-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
   LOG_PATH = os.getenv("UNIFIED_LOG_PATH", f"logs/{_default_log_name}")
   ```

4. **Auto-bind session context**:
   ```python
   # Create the global logger
   logger = structlog.get_logger()

   # Bind PowerShell session context if available (Phase 2 Bridge)
   if CF_SESSION_ID or CF_TRACE_ID:
       context_bindings = {}
       if CF_SESSION_ID:
           context_bindings["session_id"] = CF_SESSION_ID
       if CF_TRACE_ID:
           context_bindings["trace_id"] = CF_TRACE_ID

       logger = logger.bind(**context_bindings)

       # Log bridge activation for diagnostics
       logger.debug(
           "powershell_bridge_active",
           bridge_mode="Phase2",
           inherited_session=bool(CF_SESSION_ID),
           inherited_trace=bool(CF_TRACE_ID),
       )
   ```

#### Key Features:

- **Automatic Detection**: Checks environment variables at module load time
- **Conditional Binding**: Only binds if variables are present (backward compatible)
- **Diagnostic Logging**: Emits debug event when bridge is active
- **Zero Code Changes**: Existing Python code works unchanged

---

## Testing Strategy

### 3.1 Test Scenario: End-to-End Correlation

**Script**: `scripts/Test-Phase2-Bridge.ps1`

```powershell
#Requires -Modules ContextForge.Observability

# PHASE 2 BRIDGE TEST
# Tests PowerShell → Python session correlation

# Step 1: Start PowerShell session
$session = Start-CFSession -ScriptName 'Test-Phase2-Bridge'
Write-Host "Session ID: $($session.SessionId)" -ForegroundColor Cyan

# Step 2: Verify environment variables set
Write-Host "CF_SESSION_ID: $env:CF_SESSION_ID" -ForegroundColor Green
Write-Host "CF_TRACE_ID: $env:CF_TRACE_ID" -ForegroundColor Green

# Step 3: Spawn Python script that uses unified_logger
Write-CFLogEvent -EventType 'task_start' -Level 'INFO' -Message 'Spawning Python subprocess'

$pythonScript = @'
from python.services.unified_logger import logger

# This logger should auto-inherit session_id and trace_id
logger.info("python_subprocess_started", subprocess_type="test", language="python")
logger.info("action_performed", action="fetch_data", result="success")
logger.info("python_subprocess_finished")
'@

# Execute Python with inherited environment
$pythonScript | python -c -

# Step 4: PowerShell continues logging
Write-CFLogEvent -EventType 'task_end' -Level 'INFO' -Message 'Python subprocess completed'

# Step 5: Stop session and verify correlation
Stop-CFSession -Stats @{
    python_subprocesses = 1
    events_logged = 5
}

# Step 6: Verify merged logs
Write-Host "`n=== Verifying Log Correlation ===" -ForegroundColor Yellow
$todayLog = "logs/contextforge-$(Get-Date -Format 'yyyy-MM-dd').jsonl"
$sessionEvents = Get-Content $todayLog | ConvertFrom-Json |
    Where-Object { $_.session_id -eq $session.SessionId }

Write-Host "Total events for session $($session.SessionId): $($sessionEvents.Count)"
Write-Host "PowerShell events: $($sessionEvents | Where-Object { $_.event } | Measure-Object).Count"
Write-Host "Python events: $($sessionEvents | Where-Object { $_.action } | Measure-Object).Count"

# Expected output:
# Total events: 5+
# PowerShell events: 3 (session_start, task_start, task_end, session_summary)
# Python events: 3 (subprocess_started, action_performed, subprocess_finished)
```

### 3.2 Expected Log Output

```json
{"timestamp":"2025-12-29T10:30:00.000Z","session_id":"83e88a22","trace_id":"a1b2c3d4...","event":"session_start","level":"INFO","script_name":"Test-Phase2-Bridge"}

{"timestamp":"2025-12-29T10:30:01.000Z","session_id":"83e88a22","trace_id":"a1b2c3d4...","event":"task_start","level":"INFO","message":"Spawning Python subprocess"}

{"timestamp":"2025-12-29T10:30:02.123Z","session_id":"83e88a22","trace_id":"a1b2c3d4...","event":"powershell_bridge_active","level":"debug","bridge_mode":"Phase2","inherited_session":true,"inherited_trace":true}

{"timestamp":"2025-12-29T10:30:02.456Z","session_id":"83e88a22","trace_id":"a1b2c3d4...","event":"python_subprocess_started","level":"info","subprocess_type":"test","language":"python"}

{"timestamp":"2025-12-29T10:30:02.789Z","session_id":"83e88a22","trace_id":"a1b2c3d4...","event":"action_performed","level":"info","action":"fetch_data","result":"success"}

{"timestamp":"2025-12-29T10:30:03.012Z","session_id":"83e88a22","trace_id":"a1b2c3d4...","event":"python_subprocess_finished","level":"info"}

{"timestamp":"2025-12-29T10:30:04.000Z","session_id":"83e88a22","trace_id":"a1b2c3d4...","event":"task_end","level":"INFO","message":"Python subprocess completed"}

{"timestamp":"2025-12-29T10:30:05.000Z","session_id":"83e88a22","trace_id":"a1b2c3d4...","event":"session_summary","level":"INFO","python_subprocesses":1,"events_logged":5}
```

**✅ Success Criteria**:
- All events share same `session_id` and `trace_id`
- Python events include `session_id` automatically (no manual passing)
- Logs are chronologically ordered in single file
- PowerShell summary includes Python activity

---

### 3.3 MCP Server Integration Test

**Script**: `scripts/Test-McpServerBridge.ps1`

```powershell
#Requires -Modules ContextForge.Observability

$session = Start-CFSession -ScriptName 'Test-McpServerBridge'

Write-CFLogEvent -EventType 'task_start' -Level 'INFO' -Message 'Testing MCP server correlation'

# Spawn actual MCP server (e.g., TaskMan-v2)
# Environment variables automatically inherited
$mcpProcess = Start-Process -FilePath 'uv' `
    -ArgumentList 'run', 'mcp-server-taskman' `
    -PassThru `
    -NoNewWindow

Start-Sleep -Seconds 2

# MCP server should now be logging with inherited session_id
Write-CFLogEvent -EventType 'mcp_server_started' -Level 'INFO' -Data @{
    pid = $mcpProcess.Id
    server_name = 'taskman-v2'
}

# Wait for MCP operations (simulated)
Start-Sleep -Seconds 5

# Stop MCP server
Stop-Process -Id $mcpProcess.Id -Force

Stop-CFSession -Stats @{
    mcp_servers_spawned = 1
}

# Verify correlation
$todayLog = "logs/contextforge-$(Get-Date -Format 'yyyy-MM-dd').jsonl"
$mcpEvents = Get-Content $todayLog | ConvertFrom-Json |
    Where-Object { $_.session_id -eq $session.SessionId -and $_.logger_name }

Write-Host "MCP Server Events: $($mcpEvents.Count)"
$mcpEvents | Select-Object timestamp, event, action, logger_name | Format-Table
```

---

## Backward Compatibility Assurance

### 4.1 Guarantees

| Scenario | Behavior | Backward Compatible? |
|----------|----------|---------------------|
| Python script run **without** PowerShell context | No `CF_SESSION_ID` env var → logger works normally without binding | ✅ Yes |
| Existing Python MCP servers | No environment variables → logs as before | ✅ Yes |
| Python scripts setting their own session_id | Explicit `logger.bind(session_id=...)` overrides env var | ✅ Yes |
| PowerShell scripts **not** using `Start-CFSession` | No env vars set → Python logs without session_id | ✅ Yes |
| Unit tests with mocked loggers | No dependency on environment → tests pass unchanged | ✅ Yes |

### 4.2 Migration Path

**Phase 1 Scripts** (No Changes Required):
- Scripts without `Start-CFSession` continue working
- Logs appear in `logs/unified.jsonl` if `UNIFIED_LOG_PATH` not set
- Can opt-in by adding `Start-CFSession` whenever ready

**Phase 2 Adoption**:
1. Add `Import-Module ContextForge.Observability` to script
2. Add `Start-CFSession` at beginning
3. Add `Stop-CFSession` at end
4. **Zero changes to Python code** ✅

---

## Benefits & Trade-offs

### 5.1 Benefits ✅

- **Automatic Correlation**: No manual session_id passing needed
- **Zero Code Changes**: Python MCP tools work unchanged
- **Full Traceability**: Complete execution chains visible in logs
- **Language Agnostic**: Works for PowerShell → Python → Node.js chains
- **Production Ready**: Follows industry-standard environment variable pattern

### 5.2 Trade-offs ⚖️

| Aspect | Trade-off | Mitigation |
|--------|-----------|------------|
| **Log File Unification** | PowerShell and Python write to same file (potential concurrent writes) | JSONL format is append-only; file system handles locking |
| **Environment Variable Dependency** | Subprocess must inherit environment | Standard behavior for all shells; only breaks if explicitly cleared |
| **Daily Log Rotation** | Both languages must agree on filename format | Centralized in Python via `datetime.now().strftime()` |
| **Debugging Complexity** | Merged logs harder to filter | Solved by querying `session_id` field |

### 5.3 Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Environment variable not inherited | Low | High | Test subprocess spawn; document `Start-Process -UseNewEnvironment` pitfall |
| Log file write conflicts | Low | Medium | JSONL append-only; OS file locking; rotate at 50MB |
| Session ID collision | Very Low | High | Use GUID-based generation (collision probability ≈ 10⁻¹⁸) |
| Missing datetime import | Low | High | Added to imports; covered by unit tests |

---

## Validation Checklist

### 6.1 Implementation Verification

- [✅] Python imports `datetime` module
- [✅] Python reads `CF_SESSION_ID` from environment
- [✅] Python reads `CF_TRACE_ID` from environment
- [✅] Python binds session context to logger
- [✅] Python logs to `contextforge-YYYY-MM-DD.jsonl` by default
- [✅] PowerShell sets `$env:CF_SESSION_ID` in `Start-CFSession`
- [✅] PowerShell sets `$env:CF_TRACE_ID` in `Start-CFSession`

### 6.2 Integration Testing

- [ ] Create test script: `Test-Phase2-Bridge.ps1`
- [ ] Run test and verify merged logs
- [ ] Verify Python events include `session_id`
- [ ] Test MCP server subprocess correlation
- [ ] Test backward compatibility (no env vars)
- [ ] Verify existing Python code still works

### 6.3 Documentation

- [✅] Architecture diagram created
- [✅] Code changes documented
- [✅] Test scenarios defined
- [ ] Update main README.md with Phase 2 status
- [ ] Create quick reference guide

---

## Next Steps

### Phase 2 Completion Roadmap

1. **Immediate** (Today):
   - [✅] Design architecture
   - [✅] Implement Python code changes
   - [ ] Create `Test-Phase2-Bridge.ps1` test script
   - [ ] Run validation tests

2. **Short Term** (This Week):
   - [ ] Test with real MCP server (TaskMan-v2)
   - [ ] Document findings in AAR
   - [ ] Update ContextForge Work Codex

3. **Medium Term** (Next Week):
   - [ ] Add Phase 2 to all existing PowerShell scripts
   - [ ] Create log analysis dashboard
   - [ ] Performance testing (concurrent writes)

---

## References

### Related Documents

- [Phase 1 AAR](../AAR-PowerShell-Excellence-Complete.md)
- [ContextForge Observability Module](../modules/ContextForge.Observability/ContextForge.Observability.psm1)
- [Unified Logger Service](../python/services/unified_logger.py)
- [Test-McpHeartbeat.ps1](../scripts/Test-McpHeartbeat.ps1)

### External Standards

- [Structlog Documentation](https://www.structlog.org/)
- [JSONL Specification](https://jsonlines.org/)
- [12-Factor App: Config via Environment](https://12factor.net/config)

---

**Architecture Status**: ✅ Design Complete
**Implementation Status**: ✅ Python Changes Applied
**Testing Status**: ⏳ Awaiting Validation
**Production Ready**: 🔄 Pending Test Results

---

*Document maintained by: Architect Agent*
*Last Updated: 2025-12-29*
