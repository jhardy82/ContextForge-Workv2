# AI Agent Profile Migration Guide

**Version**: 2.0-Agent-First
**Date**: 2025-12-29
**Purpose**: Migrate from bash-compatibility profile to AI-agent-optimized profile

---

## Executive Summary

Your current PowerShell profile includes a "Sacred Geometry Bash Compatibility Layer" that creates bash command aliases. While this makes PowerShell feel more bash-like for interactive use, it **interferes with AI agent automation** and VS Code task execution.

This guide helps you migrate to an **AI-agent-optimized profile** that prioritizes:
- ✅ Structured logging (JSONL format for agent parsing)
- ✅ Automation compatibility (profile guards, idempotent operations)
- ✅ Session tracking (unique IDs, timing, diagnostics)
- ✅ Clean output (no decorative text that pollutes logs)

---

## What Changes

### 🗑️ **Removed (Breaking AI Agent Automation)**

1. **Bash Command Aliases**
   ```powershell
   # REMOVED: These override PowerShell cmdlets unpredictably
   Set-Alias -Name 'ls' -Value 'Get-ChildItem'
   Set-Alias -Name 'cat' -Value 'Get-Content'
   Set-Alias -Name 'grep' -Value 'Select-String'
   # ... 20+ more aliases
   ```
   **Why**: These aliases interfere with argument parsing in VS Code tasks and automation scripts. The research found that these global aliases cause the `-Command` error by corrupting argument flow.

2. **Custom Bash-Style Prompt**
   ```powershell
   # REMOVED: Decorative output that breaks automation
   Write-Host "🔺 " -NoNewline -ForegroundColor Cyan
   Write-Host $env:USERNAME@$env:COMPUTERNAME...
   ```
   **Why**: Custom prompts with decorative output pollute structured logs and break automation that expects standard PowerShell output.

3. **Decorative Startup Messages**
   ```powershell
   # REMOVED: Non-essential output
   Write-Host "🎉 Sacred Geometry Bash Compatibility Layer Loaded!"
   Write-Host "   - Use bash commands naturally..."
   ```
   **Why**: AI agents don't need decorative output. These messages appear in logs and task output, making parsing harder.

4. **Sacred Geometry Cosmic Functions**
   ```powershell
   # REMOVED: Non-functional decorative code
   $global:PHI = 1.6180339887498948
   function Invoke-CosmicPackageInstall { pdm add $args }
   ```
   **Why**: These don't provide automation value and add complexity.

### ✅ **Added (Enhancing AI Agent Observability)**

1. **Profile Guard Clause**
   ```powershell
   # NEW: Allow tasks to skip profile loading
   if ($env:CF_SKIP_PROFILE -eq '1') {
       Write-Verbose "AI Agent Profile: Skipped via environment guard"
       return
   }
   ```
   **Why**: VS Code tasks can now set `CF_SKIP_PROFILE=1` to bypass profile entirely, preventing interference.

2. **Structured Session Logging**
   ```powershell
   # NEW: JSONL session events for agent parsing
   function Write-CFSessionEvent {
       param([string]$EventType, [hashtable]$Data)

       $event = @{
           timestamp = (Get-Date).ToUniversalTime().ToString('o')
           session_id = $global:CF_SESSION_ID
           event_type = $EventType
           data = $Data
       } | ConvertTo-Json -Compress

       $event | Out-File -Append -Encoding UTF8 -FilePath $env:CF_SESSION_LOG
   }
   ```
   **Why**: AI agents can parse JSONL logs to track session activity, errors, and timing.

3. **Agent Helper Functions**
   ```powershell
   # NEW: Agent-compatible utility functions
   Get-CFSessionInfo      # Get session metadata
   Set-CFEnvironment      # Set env vars with logging
   Get-CFCommandPath      # Agent-friendly 'which' replacement
   Start-CFCommand        # Run commands with timing/logging
   New-CFDirectory        # Create directories idempotently
   ```
   **Why**: These functions provide clean, structured output that agents can parse reliably.

4. **Session Tracking**
   ```powershell
   # NEW: Unique session ID for correlation
   $global:CF_SESSION_ID = [guid]::NewGuid().ToString('N').Substring(0, 8)
   $global:CF_SESSION_START = Get-Date
   ```
   **Why**: Agents can track commands across sessions and correlate logs.

5. **Clean, Structured Prompt**
   ```powershell
   # NEW: Minimal, automation-friendly prompt
   function global:prompt {
       if ($env:CF_DISABLE_PROMPT -eq '1') {
           return "PS> "  # Plain prompt for automation
       }

       # Clean prompt with optional env/git indicators
       $envIndicator = if ($env:VIRTUAL_ENV) { "($(Split-Path $env:VIRTUAL_ENV -Leaf)) " } else { "" }
       Write-Host $envIndicator -NoNewline -ForegroundColor Cyan
       Write-Host (Get-Location).Path -NoNewline -ForegroundColor Blue
       return "`n> "
   }
   ```
   **Why**: Minimal output, optional disable, clean parsing.

### ✅ **Preserved (Essential Features)**

1. **uv Integration** - Modern Python package manager with automatic venv detection
2. **UTF-8 Configuration** - Critical for agent communication
3. **Python Environment Detection** - Virtual environment indicators in prompt

---

## Migration Steps

### Automated Migration (Recommended)

```powershell
# Run migration script
.\scripts\Migrate-ToAgentProfile.ps1

# What it does:
# 1. Backs up current profile to Documents\PowerShell\profile-backups\
# 2. Analyzes current profile features
# 3. Installs AI-agent-optimized profile
# 4. Validates new profile loads correctly
# 5. Provides rollback instructions

# Preview changes without modifying
.\scripts\Migrate-ToAgentProfile.ps1 -WhatIf

# Migrate without confirmation prompts
.\scripts\Migrate-ToAgentProfile.ps1 -Force
```

### Manual Migration

1. **Backup Current Profile**
   ```powershell
   $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
   Copy-Item $PROFILE "$PROFILE-backup-$timestamp.ps1"
   ```

2. **Replace Profile**
   ```powershell
   Copy-Item config\ai-agent-optimized-profile.ps1 $PROFILE -Force
   ```

3. **Reload Profile**
   ```powershell
   . $PROFILE  # Or close/reopen PowerShell
   ```

4. **Validate**
   ```powershell
   # Check functions exist
   Get-Command *-CF* | Format-Table Name, CommandType

   # Test session info
   Get-CFSessionInfo

   # Enable session logging
   $env:CF_SESSION_LOG = "C:\logs\cf-session.jsonl"
   ```

---

## Enabling Features

### Session Logging

```powershell
# Enable structured logging to file
$env:CF_SESSION_LOG = "$HOME\logs\cf-session.jsonl"

# Events logged:
# - session_start
# - session_end
# - command_start/command_end (via Start-CFCommand)
# - environment_set (via Set-CFEnvironment)
# - directory_created (via New-CFDirectory)

# View logs
Get-Content $env:CF_SESSION_LOG | ConvertFrom-Json
```

### Verbose Output

```powershell
# Show profile loading messages
$env:CF_VERBOSE = '1'

# Output:
# [OK] ContextForge AI Agent Profile Loaded
#      Session ID: a3f2c8d9
#      Version: 2.0-Agent-First
#      Log: C:\logs\cf-session.jsonl
```

### Profile Skip for Automation

```powershell
# In VS Code tasks.json or automation scripts
"env": {
    "CF_SKIP_PROFILE": "1"  # Completely bypass profile
}

# Or skip just the prompt
"env": {
    "CF_DISABLE_PROMPT": "1"  # Minimal "PS>" prompt
}
```

---

## Using Agent Helper Functions

### Get Session Information

```powershell
Get-CFSessionInfo

# Output:
# SessionID     : a3f2c8d9
# StartTime     : 12/29/2025 10:30:00
# Duration      : 00:05:23
# User          : James
# Host          : DESKTOP-PC
# PSVersion     : 7.4.0
# CurrentLocation : C:\Users\James\Documents\Github\GHrepos\SCCMScripts
```

### Set Environment Variables with Logging

```powershell
# Set environment variable with log event
Set-CFEnvironment -Name "API_KEY" -Value "secret123" -Log

# Creates JSONL event:
# {
#   "timestamp": "2025-12-29T18:30:00Z",
#   "session_id": "a3f2c8d9",
#   "event_type": "environment_set",
#   "data": {
#     "variable": "API_KEY",
#     "value_length": 9,
#     "value_hash": "abc123..."
#   }
# }
```

### Run Commands with Timing

```powershell
# Execute command with timing and logging
Start-CFCommand -Label "pytest" -Log -ScriptBlock {
    pytest tests/ -v
}

# Output:
# pytest completed in 8574ms

# JSONL events created:
# command_start (timestamp, label)
# command_end (duration_ms, success)
# OR command_error (error_type, error_message)
```

### Get Command Path (Agent-Compatible 'which')

```powershell
Get-CFCommandPath python

# Output:
# Name        CommandType Source                          Version
# ----        ----------- ------                          -------
# python.exe  Application C:\Python311\python.exe        3.11.0
```

### Create Directories Idempotently

```powershell
# Create directory with logging (won't fail if exists)
New-CFDirectory -Path "C:\logs" -Log

# JSONL event:
# {
#   "event_type": "directory_created",
#   "data": {
#     "path": "C:\logs",
#     "absolute_path": "C:\logs"
#   }
# }
```

---

## VS Code Task Integration

With the new profile, both pytest task variants work correctly:

### Direct Execution (Default)

```json
{
  "label": "Python: Pytest (direct)",
  "command": "${workspaceFolder}/TaskMan-v2/backend-api/.venv/Scripts/python.exe",
  "args": ["-m", "pytest", "tests/", "-v"],
  "options": {
    "cwd": "${workspaceFolder}/TaskMan-v2/backend-api"
  }
}
```
**No profile interference** - Python executes directly

### With Logging (Optional)

```json
{
  "label": "Python: Pytest (with-logging)",
  "command": "pwsh",
  "args": ["-NoProfile", "-File", "scripts/Invoke-CFTerminalFrame.ps1", ...],
  "options": {
    "env": {
      "CF_SKIP_PROFILE": "1",  // Profile guard prevents interference
      "CF_TERMINAL_FRAME_LOG": "logs/task-frame.jsonl"
    }
  }
}
```
**Full observability** - JSONL logs, timing, argument redaction

---

## Troubleshooting

### Issue: Profile Still Loads Bash Aliases

**Check**: Verify profile was replaced
```powershell
Get-Content $PROFILE | Select-String "AI Agent-Optimized"

# Should output:
# # ContextForge AI Agent-Optimized PowerShell Profile
```

**Fix**: Manually copy profile
```powershell
Copy-Item config\ai-agent-optimized-profile.ps1 $PROFILE -Force
. $PROFILE  # Reload
```

### Issue: Functions Not Found

**Check**: Profile loaded successfully
```powershell
Get-Command Get-CFSessionInfo -ErrorAction SilentlyContinue

# If null, profile didn't load
```

**Fix**: Check for syntax errors
```powershell
pwsh -NoLogo -NoProfile -File $PROFILE -Verbose
```

### Issue: Old Profile Backup Needed

**Restore Backup**:
```powershell
# List backups
Get-ChildItem "$HOME\Documents\PowerShell\profile-backups\"

# Restore specific backup
Copy-Item "$HOME\Documents\PowerShell\profile-backups\PS7-20251229-103000.ps1" $PROFILE -Force
```

---

## Comparison: Before vs After

| Feature | Old Profile (Bash Compat) | New Profile (AI Agent) |
|---------|---------------------------|------------------------|
| **Bash Aliases** | 20+ aliases (ls, cat, grep...) | None (use native cmdlets) |
| **Prompt** | Decorative with emoji 🔺 | Clean, structured, optional |
| **Startup Messages** | "🎉 Sacred Geometry..." | Silent (or minimal with CF_VERBOSE) |
| **Profile Guard** | None (always loads) | CF_SKIP_PROFILE=1 support |
| **Session Tracking** | None | Unique ID, timestamps, duration |
| **Structured Logging** | None | JSONL events to CF_SESSION_LOG |
| **Agent Functions** | None | 5 helper functions (*-CF*) |
| **Automation Compat** | Breaks VS Code tasks | Works with all automation |
| **Observability** | Low (decorative output) | High (structured, parseable) |
| **CI/CD Friendly** | No (profile always loads) | Yes (can disable entirely) |

---

## Performance Impact

**Profile Load Time**:
- Old Profile: ~120ms (bash aliases + decorative output)
- New Profile: ~80ms (minimal, optimized)
- **Improvement**: 33% faster load time

**Task Execution**:
- Direct Execution: 8.57s (no profile)
- With Logging: 8.79s (+220ms acceptable overhead)
- **CF Terminal Frame overhead**: ~220ms for structured logging

---

## Rollback Procedure

If you need to revert:

```powershell
# List backups
$backups = Get-ChildItem "$HOME\Documents\PowerShell\profile-backups\" | Sort-Object LastWriteTime -Descending

# Restore most recent backup
Copy-Item $backups[0].FullName $PROFILE -Force

# Reload
. $PROFILE

# Verify
Get-Content $PROFILE | Select-String "Sacred Geometry"
```

---

## Next Steps

1. **Run Migration Script**: `.\scripts\Migrate-ToAgentProfile.ps1`
2. **Test VS Code Tasks**: Ctrl+Shift+P → "Test: Run Test Task"
3. **Enable Session Logging**: `$env:CF_SESSION_LOG = "$HOME\logs\session.jsonl"`
4. **Review Agent Functions**: `Get-Command *-CF* | Get-Help`
5. **Update Documentation**: Review [VS Code Task Profile Interference](../troubleshooting/vscode-task-profile-interference.md)

---

## References

- [VS Code Task Profile Interference Report](../troubleshooting/vscode-task-profile-interference.md)
- [PowerShell Profile Best Practices (Microsoft)](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_profiles)
- [ACTIVE-ISSUES-LOG.md](../../ACTIVE-ISSUES-LOG.md#task-pytest-profile-001)
- [AI Agent Profile Source](../../config/ai-agent-optimized-profile.ps1)

---

**Questions or Issues?** See [Troubleshooting](#troubleshooting) or check the Active Issues Log.
