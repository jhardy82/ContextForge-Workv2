# TaskMan MCP Troubleshooting Guide

**Version**: 1.0.0
**Last Updated**: December 30, 2025
**Scope**: Common issues, diagnostics, and resolutions for TaskMan MCP Integration

---

## Quick Diagnosis Decision Tree

```
Issue?
├─ Server won't start → Issue #1
├─ Session correlation failing → Issue #2
├─ Evidence bundles missing → Issue #3
├─ Logs not appearing → Issue #4
├─ Health checks failing → Issue #5
├─ Performance slow → Issue #6
├─ Automation mode not working → Issue #7
├─ SHA-256 hash mismatch → Issue #8
├─ Port conflicts → Issue #9
└─ Permission errors → Issue #10
```

---

## Issue 1: Server Won't Start

### Symptoms
- `Failed to start MCP server` error message
- Server process terminates immediately
- Health check reports server as FAILED
- No server logs in session file

### Diagnosis

```powershell
# Step 1: Check server configuration
.\scripts\Start-McpServers.ps1 -ServerNames "MyServer" -WhatIf -Verbose

# Step 2: Verify binary exists
$config = Get-Content config/MCP-SERVERS.md | Select-String "MyServer"
# Check if Command path is valid

# Step 3: Review error evidence bundle
$latestError = Get-ChildItem evidence/mcp-error-*.json |
    Sort-Object LastWriteTime -Desc |
    Select-Object -First 1
Get-Content $latestError | ConvertFrom-Json | Format-List

# Step 4: Check Node.js installation
node --version
npm --version

# Step 5: Check Python/uv installation
python --version
uv --version
```

### Resolution

**If Node.js missing**:
```powershell
# Install Node.js 18+ from nodejs.org
winget install OpenJS.NodeJS.LTS
```

**If Python/uv missing**:
```powershell
# Install Python 3.11+
winget install Python.Python.3.11

# Install uv package manager
pip install uv
```

**If configuration invalid**:
```powershell
# Validate MCP-SERVERS.md syntax
Get-Content config/MCP-SERVERS.md | Select-String "^\s*\|" | Measure-Object
# Should have consistent column count per row

# Fix: Edit config/MCP-SERVERS.md with proper table formatting
```

**If environment variables missing**:
```powershell
# Check required variables
$env:GITHUB_TOKEN
$env:MCP_DATABASE_SECRET_KEY

# Set if missing
$env:GITHUB_TOKEN = "ghp_..."
```

### Prevention

- ✅ Run `Test-McpHeartbeat.ps1` before deploying configuration changes
- ✅ Use `-WhatIf` to preview server startup commands
- ✅ Keep Node.js and Python updated to LTS versions
- ✅ Document required environment variables in `.env.example`

---

## Issue 2: Session Correlation Not Working

### Symptoms
- Python logs missing `session_id` field
- PowerShell and Python events not correlating
- Different `session_id` values in same workflow
- `CF_SESSION_ID` shows as empty/null in Python

### Diagnosis

```powershell
# Step 1: Check PowerShell session creation
Import-Module .\modules\ContextForge.Observability
$session = Start-CFSession -ScriptName "DiagTest"
Write-Output "Session ID: $($session.SessionId)"

# Step 2: Verify environment variables exported
$env:CF_SESSION_ID
$env:CF_TRACE_ID

# Step 3: Test Python bridge
python -c "import os; print('CF_SESSION_ID:', os.environ.get('CF_SESSION_ID'))"

# Step 4: Check unified_logger.py configuration
python -c "
from python.services.unified_logger import logger, CF_SESSION_ID, CF_TRACE_ID
print(f'Session: {CF_SESSION_ID}')
print(f'Trace: {CF_TRACE_ID}')
"

# Step 5: Review logs for bridge_activated events
$logFile = "logs/contextforge-$(Get-Date -Format yyyy-MM-dd).jsonl"
Get-Content $logFile |
    ConvertFrom-Json |
    Where-Object { $_.event -eq "bridge_activated" } |
    Format-List
```

### Resolution

**If CF_SESSION_ID not set**:
```powershell
# Ensure Start-CFSession called before Python
Import-Module .\modules\ContextForge.Observability -Force
$session = Start-CFSession -ScriptName "MyScript"

# Verify export
if (-not $env:CF_SESSION_ID) {
    throw "Session ID not exported - check module version"
}
```

**If Python not detecting environment variables**:
```powershell
# Test direct environment access
python -c "import os; print(list(os.environ.keys()))" | Select-String "CF_"

# If missing, ensure PowerShell exports to child processes
$env:PSModulePath += ";$(Get-Location)\modules"
Import-Module ContextForge.Observability -Force
```

**If unified_logger.py not loading**:
```python
# Verify module import
python -c "from python.services.unified_logger import logger; logger.info('test')"

# Check log file created
Get-ChildItem logs/contextforge-*.jsonl
```

**If session IDs mismatched**:
```powershell
# Check for multiple Start-CFSession calls
Get-Content $logFile |
    ConvertFrom-Json |
    Where-Object { $_.event -eq "session_start" } |
    Select-Object timestamp, session_id

# Fix: Ensure only one session per script execution
```

### Prevention

- ✅ Always call `Start-CFSession` before Python subprocesses
- ✅ Verify `CF_SESSION_ID` exported with `$env:CF_SESSION_ID` check
- ✅ Use `unified_logger.py` for all Python logging (no `print` statements)
- ✅ Test correlation with Phase 2 validation script

---

## Issue 3: Evidence Bundles Missing

### Symptoms
- No files in `evidence/` directory
- Evidence bundles empty (0 bytes)
- Evidence bundles corrupted (invalid JSON)
- SHA-256 hashes showing as null

### Diagnosis

```powershell
# Step 1: Check evidence directory exists
Test-Path evidence/
Get-ChildItem evidence/ -Recurse

# Step 2: Verify permissions
$acl = Get-Acl evidence/
$acl.Access | Format-Table IdentityReference, FileSystemRights

# Step 3: Review evidence creation events in logs
$logFile = "logs/contextforge-$(Get-Date -Format yyyy-MM-dd).jsonl"
Get-Content $logFile |
    Select-String "evidence_created" |
    ConvertFrom-Json

# Step 4: Check for errors during bundle generation
Get-Content $logFile |
    ConvertFrom-Json |
    Where-Object { $_.event -like "*evidence*" -and $_.level -eq "ERROR" } |
    Format-List

# Step 5: Verify New-CFEvidenceBundle function available
Get-Command New-CFEvidenceBundle -ErrorAction SilentlyContinue
```

### Resolution

**If directory missing**:
```powershell
# Create evidence directory
New-Item -ItemType Directory -Path evidence -Force

# Verify creation
Test-Path evidence/ -PathType Container
```

**If permission denied**:
```powershell
# Fix permissions
$acl = Get-Acl evidence/
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $env:USERNAME, "FullControl", "Allow"
)
$acl.SetAccessRule($rule)
Set-Acl evidence/ $acl
```

**If function not available**:
```powershell
# Ensure Observability module loaded
Import-Module .\modules\ContextForge.Observability -Force

# Verify function
Get-Command New-CFEvidenceBundle | Format-List
```

**If bundles corrupted**:
```powershell
# Check disk space
Get-PSDrive C | Select-Object Used, Free

# Review error evidence bundles
Get-ChildItem evidence/mcp-error-*.json |
    ForEach-Object {
        try {
            Get-Content $_ | ConvertFrom-Json | Out-Null
            Write-Output "$($_.Name): Valid JSON"
        } catch {
            Write-Output "$($_.Name): CORRUPTED - $($_.Exception.Message)"
        }
    }
```

### Prevention

- ✅ Pre-create `evidence/` directory in repository
- ✅ Add `evidence/*.json` to `.gitignore`
- ✅ Monitor disk space with alerts at 90% usage
- ✅ Validate bundle JSON structure in tests

---

## Issue 4: Logs Not Appearing

### Symptoms
- No JSONL files in `logs/` directory
- Log file empty despite script execution
- Expected events missing from logs
- Timestamps not advancing

### Diagnosis

```powershell
# Step 1: Check logs directory exists
Test-Path logs/
Get-ChildItem logs/ -Filter "*.jsonl"

# Step 2: Verify log file path
$logFile = "logs/contextforge-$(Get-Date -Format yyyy-MM-dd).jsonl"
Write-Output "Expected log file: $logFile"
Test-Path $logFile

# Step 3: Check UNIFIED_LOG_PATH environment variable
$env:UNIFIED_LOG_PATH
# Should match actual log file location

# Step 4: Verify logger configured
python -c "
from python.services import unified_logger
print(f'Log path: {unified_logger.LOG_PATH}')
print(f'Log level: {unified_logger.LOG_LEVEL}')
"

# Step 5: Test write permissions
Out-File -FilePath "logs/test-write.txt" -InputObject "test"
Remove-Item "logs/test-write.txt"
```

### Resolution

**If directory missing**:
```powershell
New-Item -ItemType Directory -Path logs -Force
```

**If log level too high**:
```powershell
# Lower log level to capture more events
$env:UNIFIED_LOG_LEVEL = "DEBUG"

# Restart script
.\scripts\Start-McpServers.ps1
```

**If log path misconfigured**:
```powershell
# Override log path
$env:UNIFIED_LOG_PATH = "logs/contextforge-$(Get-Date -Format yyyy-MM-dd).jsonl"

# Verify
python -c "import os; print(os.getenv('UNIFIED_LOG_PATH'))"
```

**If console-only logging**:
```powershell
# Enable file logging
$env:UNIFIED_LOG_CONSOLE = "true"  # Console AND file

# Check unified_logger.py configuration
python -c "
from python.services.unified_logger import LOG_CONSOLE
print(f'Console logging: {LOG_CONSOLE}')
"
```

### Prevention

- ✅ Pre-create `logs/` directory in repository
- ✅ Add `logs/*.jsonl` to `.gitignore`
- ✅ Set `UNIFIED_LOG_LEVEL=DEBUG` for development
- ✅ Implement log rotation (daily or size-based)

---

## Issue 5: Health Checks Failing

### Symptoms
- `Test-McpHeartbeat.ps1` reports FAILED servers
- Timeout errors during health checks
- Intermittent failures (pass/fail inconsistently)
- All servers failing

### Diagnosis

```powershell
# Step 1: Run health check with verbose output
.\scripts\Test-McpHeartbeat.ps1 -Verbose

# Step 2: Check specific server configuration
Get-Content config/MCP-SERVERS.md | Select-String "FailingServer"

# Step 3: Test server binary directly
node --version  # For Node.js servers
uv --version    # For Python uvx servers

# Step 4: Check network connectivity (for remote servers)
Test-NetConnection -ComputerName mcp.linear.app -Port 443

# Step 5: Review server-specific logs
# (if server has logging to file)
```

### Resolution

**If timeouts occurring**:
```powershell
# Increase timeout in health check script
# Edit Test-McpHeartbeat.ps1
# Find: $timeout = 5
# Change to: $timeout = 30
```

**If server configuration invalid**:
```markdown
<!-- config/MCP-SERVERS.md -->
<!-- Ensure proper escaping of special characters -->
| Server | Command | Args | EnvVars | Description |
| **TaskMan-API** | `node.exe` | `path/to/index.js` | `NODE_ENV=production` | TypeScript API |
```

**If binary not in PATH**:
```powershell
# Find actual path
where.exe node
where.exe uv

# Update MCP-SERVERS.md with absolute path
# e.g., C:\Program Files\nodejs\node.exe
```

**If environment variables missing**:
```powershell
# Check required variables
Get-Content config/MCP-SERVERS.md |
    Select-String "Environment Variables" -Context 5

# Set missing variables
$env:GITHUB_TOKEN = "ghp_..."
$env:NODE_ENV = "production"
```

### Prevention

- ✅ Run health checks before production deployment
- ✅ Use absolute paths for server binaries
- ✅ Document required environment variables
- ✅ Implement retry logic for transient failures

---

## Issue 6: Performance Slow

### Symptoms
- Server startup takes >60 seconds
- Evidence bundle generation >500ms
- Health checks timeout
- High CPU/memory usage

### Diagnosis

```powershell
# Step 1: Measure server startup time
Measure-Command { .\scripts\Start-McpServers.ps1 -Force }

# Step 2: Profile individual servers
foreach ($server in @("TaskMan-API", "DuckDB-Velocity")) {
    Measure-Command {
        .\scripts\Start-McpServers.ps1 -ServerNames $server
    }
}

# Step 3: Check system resources
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
Get-Process | Sort-Object WS -Descending | Select-Object -First 10

# Step 4: Profile evidence bundle generation
Measure-Command {
    New-CFEvidenceBundle -EventType "test" -Artifacts @{ file = "test.txt" }
}
```

### Resolution

**If too many servers starting**:
```powershell
# Start only essential servers
.\scripts\Start-McpServers.ps1 -ServerNames @(
    "TaskMan-API",
    "Sequential-Thinking"
)
```

**If evidence bundles slow**:
```powershell
# Skip non-critical hashing
# (for development only - NOT production)
$env:CF_SKIP_HASHING = "true"
```

**If health checks slow**:
```powershell
# Skip health checks
.\scripts\Start-McpServers.ps1 -SkipHealthCheck
```

**If resource-constrained system**:
```powershell
# Reduce log verbosity
$env:UNIFIED_LOG_LEVEL = "ERROR"

# Disable console logging
$env:UNIFIED_LOG_CONSOLE = "false"

# Limit concurrent server starts
# Edit Start-McpServers.ps1 - add throttling
```

### Prevention

- ✅ Benchmark on target hardware before deployment
- ✅ Use selective server startup during development
- ✅ Profile with `Measure-Command` for optimization
- ✅ Monitor system resources with alerts

---

## Issue 7: Automation Mode Not Working

### Symptoms
- Prompts appearing despite `CF_AGENT_CONTEXT` set
- `-Force` flag not skipping confirmation
- Automation mode not detected in logs
- Script waiting for user input in CI/CD

### Diagnosis

```powershell
# Step 1: Verify agent context variable
$env:CF_AGENT_CONTEXT
# Should output: vscode-copilot, github-actions, etc.

# Step 2: Check automation mode detection in logs
$logFile = "logs/contextforge-$(Get-Date -Format yyyy-MM-dd).jsonl"
Get-Content $logFile |
    ConvertFrom-Json |
    Where-Object { $_.event -eq "automation_mode_detected" } |
    Format-List

# Step 3: Test agent detection logic
.\scripts\Start-McpServers.ps1 -WhatIf -Verbose
# Should show [Automation Mode] or [Interactive Mode]

# Step 4: Verify -Force parameter
Get-Help .\scripts\Start-McpServers.ps1 -Parameter Force
```

### Resolution

**If CF_AGENT_CONTEXT not recognized**:
```powershell
# Set before script execution
$env:CF_AGENT_CONTEXT = "automation"

# Verify export
Write-Output "Agent context: $env:CF_AGENT_CONTEXT"

# Run script
.\scripts\Start-McpServers.ps1
```

**If -Force flag ignored**:
```powershell
# Ensure parameter passed correctly
.\scripts\Start-McpServers.ps1 -Force

# Not: .\scripts\Start-McpServers.ps1 Force (missing dash)
```

**If prompts still appearing**:
```powershell
# Bypass all prompts in CI/CD
$env:CF_AGENT_CONTEXT = "ci-cd"
.\scripts\Start-McpServers.ps1 -Force -Confirm:$false
```

### Prevention

- ✅ Set `CF_AGENT_CONTEXT` in CI/CD pipeline environment variables
- ✅ Use `-Force` in automation scripts
- ✅ Test automation mode locally before deploying
- ✅ Log automation mode detection for debugging

---

## Issue 8: SHA-256 Hash Mismatch

### Symptoms
- Evidence bundle hash doesn't match file hash
- `Get-FileHash` returns different value
- Bundle validation failing
- Integrity check errors

### Diagnosis

```powershell
# Step 1: Extract bundle hash
$bundle = Get-Content evidence/mcp-startup-abc.json | ConvertFrom-Json
$bundleHash = $bundle.artifacts[0].hash -replace "^sha256:",""
Write-Output "Bundle hash: $bundleHash"

# Step 2: Compute actual file hash
$actualHash = (Get-FileHash -Path $bundle.artifacts[0].path -Algorithm SHA256).Hash
Write-Output "Actual hash: $actualHash"

# Step 3: Compare
if ($bundleHash -eq $actualHash) {
    Write-Output "✅ Hashes match"
} else {
    Write-Output "❌ Hash mismatch!"
    Write-Output "Difference: $(Compare-Object $bundleHash $actualHash)"
}

# Step 4: Check if file modified after bundle creation
$bundleTime = [datetime]$bundle.timestamp
$fileTime = (Get-Item $bundle.artifacts[0].path).LastWriteTime
Write-Output "Bundle created: $bundleTime"
Write-Output "File modified: $fileTime"
```

### Resolution

**If file modified after bundle creation**:
```text
Evidence bundles are immutable snapshots. Hash mismatch indicates file was
changed after bundle generation. This is expected behavior.

To regenerate bundle:
.\scripts\Start-McpServers.ps1 -Force
```

**If bundle corrupted**:
```powershell
# Delete corrupted bundle
Remove-Item evidence/mcp-startup-abc.json

# Regenerate
.\scripts\Start-McpServers.ps1 -Force
```

**If sanitization affecting hash**:
```text
Sanitization modifies content before hashing. The hash represents the
SANITIZED content, not the original file.

This is expected behavior for security compliance.
```

### Prevention

- ✅ Treat evidence bundles as read-only
- ✅ Regenerate bundles if files change
- ✅ Document that hashes represent sanitized content
- ✅ Store bundles in tamper-proof storage for compliance

---

## Issue 9: Port Conflicts

### Symptoms
- `EADDRINUSE` errors in server logs
- Server starts then immediately stops
- Multiple instances of same server running
- Network connection refused errors

### Diagnosis

```powershell
# Step 1: Check listening ports
netstat -ano | findstr "LISTENING"

# Step 2: Identify process using port
$port = 3000  # Example port
Get-NetTCPConnection -LocalPort $port |
    Select-Object LocalAddress, LocalPort, OwningProcess

# Step 3: Get process details
$pid = 12345  # From step 2
Get-Process -Id $pid | Format-List

# Step 4: Check for duplicate server instances
Get-Job | Where-Object { $_.Name -like "MCP-*" } | Format-Table
```

### Resolution

**If duplicate servers running**:
```powershell
# Stop all MCP server jobs
Get-Job | Where-Object { $_.Name -like "MCP-*" } | Stop-Job
Get-Job | Where-Object { $_.Name -like "MCP-*" } | Remove-Job

# Verify stopped
Get-Job
```

**If port occupied by other process**:
```powershell
# Kill process (if safe to do so)
Stop-Process -Id 12345 -Force

# Or change server port in configuration
# Edit config/MCP-SERVERS.md or server .env file
```

**If multiple script executions**:
```powershell
# Ensure only one instance running
$scriptName = "Start-McpServers"
$running = Get-Process powershell | Where-Object {
    $_.MainWindowTitle -like "*$scriptName*"
}

if ($running.Count -gt 1) {
    Write-Error "Multiple instances detected - stop extras"
}
```

### Prevention

- ✅ Stop servers before restarting
- ✅ Use unique ports for each server
- ✅ Implement port availability checks before startup
- ✅ Document port allocations

---

## Issue 10: Permission Errors

### Symptoms
- `Access denied` when creating evidence bundles
- `UnauthorizedAccessException` in logs
- Cannot write to `logs/` or `evidence/` directories
- Module import failures

### Diagnosis

```powershell
# Step 1: Check current user permissions
whoami
whoami /groups

# Step 2: Verify directory permissions
Get-Acl logs/ | Format-List
Get-Acl evidence/ | Format-List

# Step 3: Test write access
try {
    Out-File -FilePath "logs/test.txt" -InputObject "test"
    Remove-Item "logs/test.txt"
    Write-Output "✅ Write access confirmed"
} catch {
    Write-Error "❌ Permission denied: $_"
}

# Step 4: Check module execution policy
Get-ExecutionPolicy -List
```

### Resolution

**If directory permissions restrictive**:
```powershell
# Fix logs directory permissions
$acl = Get-Acl logs/
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $env:USERNAME, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
)
$acl.SetAccessRule($rule)
Set-Acl logs/ $acl

# Repeat for evidence directory
$acl = Get-Acl evidence/
$acl.SetAccessRule($rule)
Set-Acl evidence/ $acl
```

**If execution policy blocking**:
```powershell
# Set execution policy (requires admin)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**If running as non-admin**:
```powershell
# Run PowerShell as administrator
Start-Process pwsh -Verb RunAsAdministrator

# Then execute scripts
```

### Prevention

- ✅ Pre-configure directory permissions in setup scripts
- ✅ Document required execution policy
- ✅ Use least-privilege access where possible
- ✅ Test deployment as non-admin user

---

## Advanced Diagnostics

### Full System Health Check

```powershell
# Comprehensive diagnostic script
$diagnostics = @{
    NodeVersion = (node --version 2>&1)
    PythonVersion = (python --version 2>&1)
    UvVersion = (uv --version 2>&1)
    PowerShellVersion = $PSVersionTable.PSVersion
    LogsExist = (Test-Path logs/)
    EvidenceExist = (Test-Path evidence/)
    ConfigExists = (Test-Path config/MCP-SERVERS.md)
    SessionIdSet = [bool]$env:CF_SESSION_ID
    AgentContext = $env:CF_AGENT_CONTEXT
}

$diagnostics | ConvertTo-Json -Depth 10 | Out-File diagnostics-$(Get-Date -Format yyyyMMdd-HHmmss).json
Write-Output "Diagnostics saved"
```

### Log Analysis

```powershell
# Analyze errors in logs
$logFile = "logs/contextforge-$(Get-Date -Format yyyy-MM-dd).jsonl"
$errors = Get-Content $logFile |
    ConvertFrom-Json |
    Where-Object { $_.level -eq "ERROR" } |
    Group-Object event |
    Select-Object Count, Name

$errors | Format-Table -AutoSize
```

### Evidence Bundle Audit

```powershell
# Audit all evidence bundles
$bundles = Get-ChildItem evidence/*.json | ForEach-Object {
    $content = Get-Content $_ | ConvertFrom-Json
    [PSCustomObject]@{
        File = $_.Name
        Timestamp = $content.timestamp
        EventType = $content.event_type
        ArtifactCount = $content.artifacts.Count
        SessionId = $content.session_id
    }
}

$bundles | Format-Table -AutoSize
```

---

## Emergency Recovery

### Complete Reset

```powershell
# CAUTION: This deletes all logs and evidence bundles

# Step 1: Stop all MCP servers
Get-Job | Where-Object { $_.Name -like "MCP-*" } | Stop-Job
Get-Job | Where-Object { $_.Name -like "MCP-*" } | Remove-Job

# Step 2: Backup existing data (optional)
$backupDir = "backup-$(Get-Date -Format yyyyMMdd-HHmmss)"
New-Item -ItemType Directory -Path $backupDir
Copy-Item logs/* $backupDir/logs/ -Recurse -ErrorAction SilentlyContinue
Copy-Item evidence/* $backupDir/evidence/ -Recurse -ErrorAction SilentlyContinue

# Step 3: Clear logs and evidence
Remove-Item logs/*.jsonl -Force
Remove-Item evidence/*.json -Force

# Step 4: Restart clean
.\scripts\Start-McpServers.ps1 -Force
```

---

## Getting Help

### Before Reporting Issues

1. ✅ Run `Test-McpHeartbeat.ps1 -Verbose`
2. ✅ Collect error evidence bundle
3. ✅ Extract relevant session logs
4. ✅ Check this troubleshooting guide
5. ✅ Review [Integration Guide](TaskMan-MCP-Integration-Guide.md)

### Issue Report Template

```markdown
## Issue Description
[Brief description of the problem]

## Environment
- PowerShell version: 7.x.x
- Node.js version: v18.x.x
- Python version: 3.11.x
- OS: Windows 11 / Windows Server 2022

## Steps to Reproduce
1. Execute: .\scripts\Start-McpServers.ps1
2. Observe: [Error message]
3. Expected: [Expected behavior]

## Diagnostics
- Session ID: abc-123-def-456
- Error evidence bundle: [Attach sanitized JSON]
- Log excerpt: [Paste relevant logs]
- Health check output: [Paste Test-McpHeartbeat.ps1 output]

## Attempted Solutions
- [x] Checked Node.js version
- [x] Verified environment variables
- [ ] Other...
```

---

## Related Documentation

- **[Integration Guide](TaskMan-MCP-Integration-Guide.md)** - Complete technical overview
- **[User Guide](TaskMan-MCP-User-Guide.md)** - Practical usage instructions
- **[Rollout Checklist](../ROLLOUT-CHECKLIST.md)** - Production deployment
- **[MCP Server Configuration](../config/MCP-SERVERS.md)** - Server definitions

---

**Document Version**: 1.0.0
**Coverage**: 10+ common issues with diagnostics and resolutions
**Maintenance**: Review and update quarterly or after major changes
