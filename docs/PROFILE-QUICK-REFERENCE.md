# ContextForge Profile Quick Reference

**Version**: 2.0-Agent-First (Master-Level)
**Quality**: 9.5/10
**Documentation**: Complete comment-based help on all functions

---

## 🚀 Quick Start

### View Session Information
```powershell
Get-CFSessionInfo
# Returns: SessionID, StartTime, Duration, User, Host, PSVersion, CurrentLocation
```

### Get Help on Any Function
```powershell
Get-Help <function-name> -Full      # Complete documentation
Get-Help <function-name> -Examples  # Just examples
Get-Help <function-name> -Parameter <param>  # Parameter details
```

---

## 📚 Available Functions

| Function | Purpose | Help |
|----------|---------|------|
| `Write-CFSessionEvent` | Write structured event to session log | `Get-Help Write-CFSessionEvent` |
| `Get-CFSessionInfo` | Get session metadata | `Get-Help Get-CFSessionInfo` |
| `Set-CFEnvironment` | Set environment variable with logging | `Get-Help Set-CFEnvironment` |
| `Get-CFEnvironment` | Get environment variables | `Get-Help Get-CFEnvironment` |
| `Start-CFCommand` | Execute command with timing | `Get-Help Start-CFCommand` |
| `Get-CFCommandPath` | Locate command (like 'which') | `Get-Help Get-CFCommandPath` |
| `New-CFDirectory` | Create directory idempotently | `Get-Help New-CFDirectory` |
| `Invoke-UVCommand` | Execute uv with logging | `Get-Help Invoke-UVCommand` (alias: `uvr`) |

---

## 🔥 Common Tasks

### Environment Variables

```powershell
# Set with logging
Set-CFEnvironment -Name "API_KEY" -Value "secret123" -Log

# Preview changes (WhatIf)
Set-CFEnvironment -Name "API_KEY" -Value "secret123" -WhatIf

# Get all Python-related variables
Get-CFEnvironment -Filter "PYTHON*"

# Get all as JSON
Get-CFEnvironment -AsJson
```

### Command Location

```powershell
# Find Python executable
Get-CFCommandPath -Command "python"

# Check if command exists
if (Get-CFCommandPath -Command "node") {
    Write-Host "Node.js is installed"
}
```

### Directory Management

```powershell
# Create directory (idempotent - safe to run multiple times)
New-CFDirectory -Path "C:\Projects\MyApp"

# Preview directory creation
New-CFDirectory -Path "C:\Projects\MyApp" -WhatIf

# Create with logging
New-CFDirectory -Path "C:\Projects\MyApp" -Log
```

### Command Execution

```powershell
# Run command with timing
Start-CFCommand -ScriptBlock { python -m pytest } -Label "pytest"

# With custom timeout
Start-CFCommand -ScriptBlock { npm test } -Label "npm-test" -TimeoutSeconds 300
```

### UV Package Manager

```powershell
# Sync dependencies
Invoke-UVCommand -Arguments @("sync") -Log

# Install package
uvr "add" "fastapi"  # Using alias

# Run Python with uv
uvr "run" "python" "script.py"
```

---

## 🎯 ShouldProcess Support

Functions that modify state support `-WhatIf` and `-Confirm`:

```powershell
# Preview what would happen
Set-CFEnvironment -Name "VAR" -Value "value" -WhatIf
New-CFDirectory -Path "C:\Test" -WhatIf

# Require confirmation
Set-CFEnvironment -Name "PROD_API_KEY" -Value "secret" -Confirm
```

---

## 📊 Session Logging

### Enable Structured Logging

```powershell
# Set log path (persist across sessions in $PROFILE)
$env:CF_SESSION_LOG = 'C:\logs\contextforge\session.jsonl'

# Now all Log-enabled functions will write to this file
Set-CFEnvironment -Name "TEST" -Value "123" -Log
New-CFDirectory -Path "C:\Test" -Log
Start-CFCommand -ScriptBlock { python --version } -Label "version-check"
```

### Log Event Manually

```powershell
Write-CFSessionEvent -EventType "custom_event" -Data @{
    action = "deployment"
    status = "success"
    version = "1.0.0"
}
```

### Log Format (JSONL)

Each log entry is a single-line JSON object:
```json
{"timestamp":"2025-12-29T14:20:38Z","session_id":"22bfcf3d","event_type":"environment_set","data":{"variable":"API_KEY","value_length":9,"value_hash":"a3b2c1..."}}
{"timestamp":"2025-12-29T14:20:45Z","session_id":"22bfcf3d","event_type":"command_start","data":{"label":"pytest","script":"python -m pytest"}}
{"timestamp":"2025-12-29T14:20:48Z","session_id":"22bfcf3d","event_type":"command_end","data":{"label":"pytest","duration_ms":3245,"exit_code":0}}
```

---

## 🛡️ Error Handling

All functions include robust error handling:

```powershell
# Gracefully handles non-existent commands
$cmd = Get-CFCommandPath -Command "non-existent"
if ($null -eq $cmd) {
    Write-Host "Command not found"
}

# Parameter validation prevents errors early
Set-CFEnvironment -Name "" -Value "test"
# Error: Cannot validate argument on parameter 'Name'

# Try/catch wraps all external operations
try {
    Set-CFEnvironment -Name "TEST" -Value "value" -ErrorAction Stop
} catch {
    Write-Host "Failed: $_"
}
```

---

## 🎨 Customization

### Disable Profile for Automation

```powershell
# Before running scripts
$env:CF_SKIP_PROFILE = '1'

# Or skip just bash compatibility layer
$env:CF_SKIP_BASH_LAYER = '1'
```

### Customize Prompt

The profile includes a custom prompt showing:
- 🐍 Virtual environment (if active)
- 📋 Session ID (first 8 chars)
- 📂 Current directory
- 🌿 Git branch (if in repo)

To disable:
```powershell
$env:CF_DISABLE_PROMPT = '1'
```

---

## 📖 Getting Help

### List All CF Functions
```powershell
Get-Command *-CF*
```

### View Function Details
```powershell
Get-Help <function-name> -Full
```

### See All Parameters
```powershell
Get-Help <function-name> -Parameter *
```

### Just Show Examples
```powershell
Get-Help <function-name> -Examples
```

---

## 🔧 Troubleshooting

### Profile Not Loading

Check PowerShell profile path:
```powershell
$PROFILE
# Should point to: C:\Users\<username>\Documents\PowerShell\profile.ps1
```

Verify file exists:
```powershell
Test-Path $PROFILE
```

### Functions Not Available

Check if profile guard is active:
```powershell
$env:CF_SKIP_PROFILE
$env:CF_SKIP_BASH_LAYER
```

If either is `'1'`, functions won't load (by design for automation).

### Session Logging Not Working

Verify log path is set:
```powershell
$env:CF_SESSION_LOG
```

Check directory exists:
```powershell
Test-Path (Split-Path $env:CF_SESSION_LOG -Parent)
```

### Rollback to Previous Profile

```powershell
Copy-Item 'C:\Users\James\Documents\PowerShell\profile-backups\PS7-20251229-142017.ps1' `
          'C:\Users\James\Documents\PowerShell\profile.ps1' -Force

# Restart PowerShell
```

---

## 📚 Documentation

- **Full Enhancement Summary**: `docs/PROFILE-ENHANCEMENT-SUMMARY.md`
- **Deployment Report**: `docs/DEPLOYMENT-VERIFICATION-REPORT.md`
- **Migration Guide**: `docs/guides/ai-agent-profile-migration.md`
- **Test Suite**: `tests/Test-AgentProfile.ps1`

---

## 🎯 Pro Tips

1. **Use WhatIf First**: Always test with `-WhatIf` before modifying state
2. **Enable Logging**: Set `$env:CF_SESSION_LOG` for AI agent observability
3. **Check Help**: Every function has complete documentation via `Get-Help`
4. **Parameter Validation**: Functions validate input - trust the errors!
5. **Session IDs**: Use session IDs to correlate events in logs
6. **UV Alias**: Use `uvr` shorthand for `Invoke-UVCommand`

---

**Quick Reference Card v1.0**
**Profile Version**: 2.0-Agent-First
**Last Updated**: December 29, 2025
