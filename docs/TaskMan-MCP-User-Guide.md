# TaskMan MCP Integration - User Guide

**Version**: 1.0.0
**Audience**: Developers, DevOps Engineers, AI Agents
**Last Updated**: December 30, 2025

---

## Quick Start (5 Minutes)

### Prerequisites Check

```powershell
# Verify Node.js installed
node --version
# Required: v18.0.0 or higher

# Verify PowerShell version
$PSVersionTable.PSVersion
# Required: 7.0 or higher

# Verify Python and uv
python --version  # Required: 3.11+
uv --version      # Required: Latest
```

---

### 1. Start All MCP Servers

**Interactive Mode** (prompts for confirmation):
```powershell
.\scripts\Start-McpServers.ps1
```

**Automation Mode** (skip prompts - for CI/CD or AI agents):
```powershell
# Set agent context
$env:CF_AGENT_CONTEXT = "vscode-copilot"

# Or use -Force flag
.\scripts\Start-McpServers.ps1 -Force
```

**Test Mode** (preview without execution):
```powershell
.\scripts\Start-McpServers.ps1 -WhatIf
```

**Expected Output**:
```
Starting MCP Server Orchestration...
[Automation Mode] Agent context detected: vscode-copilot
Session ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890

Starting MCP servers:
✅ TaskMan-API started (PID: 12345)
✅ TaskMan-Sqlite started (PID: 12346)
✅ DuckDB-Velocity started (PID: 12347)
✅ Sequential-Thinking started (PID: 12348)
... (13 servers total)

MCP Server Startup Complete
Success: 13 | Failed: 0 | Duration: 28.3s
Evidence bundles: 15 created in evidence/
```

---

### 2. Verify Server Health

```powershell
.\scripts\Test-McpHeartbeat.ps1
```

**Expected Output**:
```
Starting MCP Heartbeat Check...
Checking [Linear]... ✅ Passed
Checking [TaskMan-Sqlite]... ✅ Passed
Checking [TaskMan-API]... ✅ Passed
Checking [DuckDB-Velocity]... ✅ Passed
...

MCP Heartbeat Check Complete
Checked: 13 | Passed: 13 | Failed: 0 | Skipped: 0
```

**If servers fail**, see [Troubleshooting Guide](TaskMan-MCP-Troubleshooting.md#issue-1-server-wont-start).

---

### 3. View Session Logs

**View today's log file**:
```powershell
# Get current date log
$logFile = "logs/contextforge-$(Get-Date -Format yyyy-MM-dd).jsonl"
Get-Content $logFile -Tail 20
```

**View specific session**:
```powershell
# Filter by session ID
Get-Content $logFile |
    ConvertFrom-Json |
    Where-Object { $_.session_id -eq "a1b2c3d4-..." } |
    Format-Table timestamp, event, task_id, outcome
```

**Example Log Entry**:
```json
{
  "timestamp": "2025-12-30T10:15:32.123456",
  "level": "INFO",
  "event": "mcp_server_start",
  "server_name": "TaskMan-API",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "outcome": "Success"
}
```

---

### 4. Check Evidence Bundles

```powershell
# List all evidence bundles
Get-ChildItem evidence/*.json |
    Select-Object Name, Length, LastWriteTime |
    Format-Table -AutoSize
```

**View bundle contents**:
```powershell
# View latest bundle
$latest = Get-ChildItem evidence/*.json |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

Get-Content $latest | ConvertFrom-Json | Format-List
```

**Example Bundle**:
```json
{
  "bundle_id": "mcp-startup-a1b2c3d4",
  "timestamp": "2025-12-30T10:15:32Z",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "event_type": "mcp_server_start",
  "artifacts": [
    {
      "type": "configuration",
      "path": "config/MCP-SERVERS.md",
      "hash": "sha256:abc123def456...",
      "size_bytes": 4567
    }
  ]
}
```

---

## Common Workflows

### Workflow 1: Start Specific Servers

**Use Case**: Only need TaskMan and DuckDB servers, skip others for faster startup.

```powershell
.\scripts\Start-McpServers.ps1 -ServerNames @(
    "TaskMan-API",
    "TaskMan-Sqlite",
    "DuckDB-Velocity",
    "DuckDB-Dashboard"
)
```

**Benefits**:
- Faster startup (4 servers vs 13)
- Lower resource usage
- Focused testing

---

### Workflow 2: Verify Cross-Language Session Correlation

**Use Case**: Ensure PowerShell and Python logs are correlated by session ID.

```powershell
# Step 1: Start session in PowerShell
Import-Module .\modules\ContextForge.Observability
$session = Start-CFSession -ScriptName "CorrelationTest"
Write-Output "Session ID: $($session.SessionId)"

# Step 2: Call Python with inherited session
python -c "
import os
from python.services.unified_logger import logger
logger.info('python_event', message='Testing correlation')
print(f'Python session_id: {os.getenv(\"CF_SESSION_ID\")}')
"

# Step 3: Verify logs contain same session_id
$logFile = "logs/contextforge-$(Get-Date -Format yyyy-MM-dd).jsonl"
Get-Content $logFile |
    ConvertFrom-Json |
    Where-Object { $_.session_id -eq $session.SessionId } |
    Select-Object timestamp, event, logger
```

**Expected Output**:
```
timestamp                event              logger
---------                -----              ------
2025-12-30T10:15:32.100  session_start      PowerShell
2025-12-30T10:15:32.150  python_event       unified_logger
```

---

### Workflow 3: Automated CI/CD Startup

**Use Case**: GitHub Actions workflow needs MCP servers running for integration tests.

```yaml
# .github/workflows/integration-tests.yml
steps:
  - name: Start MCP Servers
    shell: pwsh
    run: |
      $env:CF_AGENT_CONTEXT = "github-actions"
      .\scripts\Start-McpServers.ps1 -Force

  - name: Verify Server Health
    shell: pwsh
    run: |
      .\scripts\Test-McpHeartbeat.ps1
      if ($LASTEXITCODE -ne 0) {
        throw "MCP health check failed"
      }

  - name: Run Integration Tests
    run: |
      pytest tests/integration/ -v

  - name: Collect Evidence Bundles
    if: always()
    uses: actions/upload-artifact@v3
    with:
      name: mcp-evidence-bundles
      path: evidence/*.json
```

---

### Workflow 4: Debugging Failed Server Startup

**Use Case**: A server fails to start, need to diagnose the issue.

```powershell
# Step 1: Start servers in verbose mode
.\scripts\Start-McpServers.ps1 -Verbose

# Step 2: Review error evidence bundle
$errorBundle = Get-ChildItem evidence/mcp-error-*.json |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

Get-Content $errorBundle | ConvertFrom-Json | Format-List

# Step 3: Check specific server configuration
Get-Content config/MCP-SERVERS.md |
    Select-String -Pattern "TaskMan-API" -Context 2

# Step 4: Test server manually
node TaskMan-v2/mcp-server-ts/dist/index.js
```

**Common Issues**:
- Missing Node.js: Install from nodejs.org
- Invalid configuration: Check MCP-SERVERS.md syntax
- Port conflict: Another process using port (check with `netstat -ano`)
- Missing environment variables: Check `.env` file

See [Troubleshooting Guide](TaskMan-MCP-Troubleshooting.md) for more details.

---

### Workflow 5: Validate Evidence Bundle Integrity

**Use Case**: Audit compliance requires cryptographic verification of evidence bundles.

```powershell
# Step 1: Get bundle
$bundle = Get-Content evidence/mcp-startup-abc-123.json | ConvertFrom-Json

# Step 2: Extract artifact hash
$artifactHash = $bundle.artifacts[0].hash -replace "^sha256:",""

# Step 3: Compute actual hash
$actualHash = (Get-FileHash -Path $bundle.artifacts[0].path -Algorithm SHA256).Hash

# Step 4: Compare
if ($actualHash -eq $artifactHash) {
    Write-Output "✅ Evidence bundle integrity verified"
} else {
    Write-Error "❌ Evidence bundle integrity check FAILED"
}
```

---

## Advanced Usage

### Custom Server Configuration

**Add a new MCP server** to [config/MCP-SERVERS.md](../config/MCP-SERVERS.md):

```markdown
| **Custom-Server** | `node.exe` | `path/to/server.js` | `API_KEY=${env:CUSTOM_API_KEY}` | Custom integration |
```

**Start the new server**:
```powershell
.\scripts\Start-McpServers.ps1 -ServerNames "Custom-Server"
```

---

### Session Correlation Across Languages

**PowerShell → Python → Node.js correlation**:

```powershell
# PowerShell
Import-Module .\modules\ContextForge.Observability
$session = Start-CFSession -ScriptName "MultiLanguageTest"

# Python subprocess
python -c "
from python.services.unified_logger import logger
logger.info('python_task', task='Data processing')
"

# Node.js subprocess (if configured with logger)
node -e "
const sessionId = process.env.CF_SESSION_ID;
console.log(JSON.stringify({
  timestamp: new Date().toISOString(),
  session_id: sessionId,
  event: 'nodejs_task'
}));
"

# Verify correlation
$logFile = "logs/contextforge-$(Get-Date -Format yyyy-MM-dd).jsonl"
Get-Content $logFile |
    ConvertFrom-Json |
    Where-Object { $_.session_id -eq $session.SessionId } |
    Select-Object event, logger
```

---

### Evidence Bundle Analysis

**Query evidence bundles for audit reports**:

```powershell
# Get all bundles from today
$bundles = Get-ChildItem evidence/*.json |
    Where-Object { $_.LastWriteTime -gt (Get-Date).Date } |
    ForEach-Object { Get-Content $_ | ConvertFrom-Json }

# Group by event type
$bundles |
    Group-Object event_type |
    Select-Object Count, Name |
    Format-Table -AutoSize

# Find bundles with sanitized data
$bundles |
    Where-Object {
        $_.artifacts | Where-Object { $_.sanitized -eq $true }
    } |
    Select-Object bundle_id, timestamp, event_type
```

---

### Environment Variable Reference

Set these variables **before** running MCP scripts for customization:

```powershell
# Agent context (automation mode)
$env:CF_AGENT_CONTEXT = "vscode-copilot"

# Python log level (DEBUG, INFO, WARN, ERROR)
$env:UNIFIED_LOG_LEVEL = "DEBUG"

# Custom log path
$env:UNIFIED_LOG_PATH = "logs/custom-mcp.jsonl"

# Disable console logging (file only)
$env:UNIFIED_LOG_CONSOLE = "false"

# Then run scripts
.\scripts\Start-McpServers.ps1
```

---

## Integration with VS Code

### GitHub Copilot MCP Integration

**Automatic Context**: GitHub Copilot automatically sets `CF_AGENT_CONTEXT`:

```powershell
# No manual setup needed - Copilot sets this automatically
$env:CF_AGENT_CONTEXT
# Output: vscode-copilot
```

**Using MCP Tools in Chat**:
```
User: Create a task in TaskMan
Copilot: (uses TaskMan-API MCP tool)
         Task T-001 created successfully

User: Query velocity metrics
Copilot: (uses DuckDB-Velocity MCP tool)
         Sprint velocity: 45 points/week
```

---

### VS Code Tasks Integration

**Create custom task** in [.vscode/tasks.json](../.vscode/tasks.json):

```json
{
  "label": "Start MCP Servers (Force)",
  "type": "shell",
  "command": "pwsh",
  "args": [
    "-NoProfile",
    "-Command",
    "& { ./scripts/Start-McpServers.ps1 -Force }"
  ],
  "group": "none",
  "presentation": {
    "reveal": "always",
    "panel": "new"
  }
}
```

**Run from Command Palette**: `Ctrl+Shift+P` → "Tasks: Run Task" → "Start MCP Servers (Force)"

---

## Best Practices

### ✅ Do

- **Always verify server health** after startup with `Test-McpHeartbeat.ps1`
- **Review evidence bundles** for audit compliance
- **Use automation mode** in CI/CD with `CF_AGENT_CONTEXT`
- **Check session logs** when debugging cross-language issues
- **Validate SHA-256 hashes** for critical evidence bundles

### ⚠️ Caution

- **Don't modify evidence bundles** - invalidates cryptographic signatures
- **Don't commit logs/** to git - contains session-specific data
- **Don't hardcode API keys** - use environment variables
- **Don't skip health checks** - silent failures are hard to debug

### 🚫 Avoid

- **Running multiple server instances** - causes port conflicts
- **Deleting logs without backup** - needed for audit trails
- **Ignoring evidence bundle errors** - indicates serious issues
- **Manual server starts** - bypasses observability and evidence generation

---

## Performance Tips

### Faster Startup

```powershell
# Start only essential servers
.\scripts\Start-McpServers.ps1 -ServerNames @(
    "TaskMan-API",
    "Sequential-Thinking"
)

# Skip health checks (not recommended for production)
.\scripts\Start-McpServers.ps1 -SkipHealthCheck
```

### Reduced Resource Usage

```powershell
# Disable verbose logging
$env:UNIFIED_LOG_LEVEL = "ERROR"

# Disable console output (file only)
$env:UNIFIED_LOG_CONSOLE = "false"

.\scripts\Start-McpServers.ps1 -Force
```

---

## Frequently Asked Questions

**Q: How long does server startup take?**
A: ~30 seconds for all 13 servers in parallel. Selective startup is faster.

**Q: Can I run servers in the background?**
A: Yes, `Start-McpServers.ps1` uses PowerShell background jobs. Servers persist until stopped.

**Q: How do I stop all MCP servers?**
A: Use PowerShell job management:
```powershell
Get-Job | Where-Object { $_.Name -like "MCP-*" } | Stop-Job
```

**Q: Where are logs stored?**
A: `logs/contextforge-YYYY-MM-DD.jsonl` (daily rotation)

**Q: How do I know if automation mode is active?**
A: Check the startup output for `[Automation Mode]` or query `$env:CF_AGENT_CONTEXT`

**Q: Can I customize server configurations?**
A: Yes, edit [config/MCP-SERVERS.md](../config/MCP-SERVERS.md) and restart servers.

**Q: What if a server fails to start?**
A: Check the error evidence bundle in `evidence/mcp-error-*.json` for diagnostics.

**Q: Are evidence bundles required?**
A: Yes for audit compliance. They provide tamper-proof operation records.

**Q: How do I verify evidence integrity?**
A: Compare SHA-256 hashes in bundles with actual file hashes using `Get-FileHash`.

---

## Related Documentation

- **[Integration Guide](TaskMan-MCP-Integration-Guide.md)** - Complete technical overview
- **[Troubleshooting Guide](TaskMan-MCP-Troubleshooting.md)** - Common issues and solutions
- **[Rollout Checklist](../ROLLOUT-CHECKLIST.md)** - Production deployment steps
- **[MCP Server Configuration](../config/MCP-SERVERS.md)** - Server definitions

---

## Support

**Issues**: Create GitHub issue with:
- Error evidence bundle (sanitized)
- Session log excerpt (`session_id` filtered)
- Output from `Test-McpHeartbeat.ps1 -Verbose`

**Questions**: Check [Troubleshooting Guide](TaskMan-MCP-Troubleshooting.md) first.

---

**Document Version**: 1.0.0
**Target Audience**: Developers, DevOps, AI Agents
**Skill Level**: Beginner to Advanced
**Est. Time to Proficiency**: 30 minutes
