# Profile Guard Implementation Validation Checklist

**Purpose**: Verify profile guard clause is correctly installed for VS Code task observability

**Estimated Time**: 5 minutes

---

## Prerequisites

- [ ] PowerShell 7+ installed
- [ ] VS Code with workspace open
- [ ] Python venv activated (TaskMan-v2/backend-api)

---

## Step 1: Locate Profile

```powershell
# Display profile path
$PROFILE
```

**Expected Output**: `C:\Users\<username>\Documents\PowerShell\Microsoft.PowerShell_profile.ps1`

**Legacy Profile Path** (this is the one we're modifying):
```powershell
# Show legacy profile (all hosts)
$PROFILE.Replace('Microsoft.PowerShell_', '')
```

**Expected Output**: `C:\Users\<username>\Documents\PowerShell\profile.ps1`

- [ ] Profile path confirmed

---

## Step 2: Backup Current Profile

```powershell
# Create timestamped backup
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$legacyProfile = $PROFILE.Replace('Microsoft.PowerShell_', '')
$backupPath = "$legacyProfile.backup-$timestamp"
Copy-Item $legacyProfile $backupPath -Force
Write-Host "Backup created: $backupPath"
```

- [ ] Backup created successfully

---

## Step 3: Open Profile for Editing

```powershell
# Open legacy profile in VS Code
$legacyProfile = $PROFILE.Replace('Microsoft.PowerShell_', '')
code $legacyProfile
```

- [ ] Profile opened in VS Code

---

## Step 4: Verify Current Profile Structure

**Before adding guard, confirm these exist**:

- [ ] Conda initialization block (if using conda)
- [ ] "Sacred Geometry PowerShell Bash Compatibility Layer" comment
- [ ] UTF-8 configuration lines
- [ ] Bash alias definitions (`Set-Alias` commands)
- [ ] Startup banner: `Write-Host "🎉 Sacred Geometry Bash Compatibility Layer Loaded!"`

---

## Step 5: Add Guard Clause

**Insert this block as THE VERY FIRST CODE** (before conda, before any other code):

```powershell
#region CF Terminal Frame Skip Guard (MUST BE FIRST)
# Purpose: Prevent profile interference when running CF observability tools
# Documentation: docs/troubleshooting/vscode-task-profile-interference.md
# Environment Variable: CF_SKIP_BASH_LAYER=1
if ($env:CF_SKIP_BASH_LAYER -eq '1') {
    # Only load essential UTF-8 encoding, skip all aliases and banners
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::InputEncoding = [System.Text.Encoding]::UTF8
    $env:PYTHONIOENCODING = 'utf-8'
    $env:PYTHONUTF8 = '1'
    return  # Exit profile immediately (nothing below this executes)
}
#endregion

# ... rest of profile (conda, Sacred Geometry, etc.) ...
```

- [ ] Guard clause added as FIRST block
- [ ] Spacing preserved (blank line after #endregion)
- [ ] No code before the guard clause

---

## Step 6: Save and Validate Syntax

```powershell
# Reload profile to check for syntax errors
. $legacyProfile

# Should see Sacred Geometry banner (guard not active yet)
```

**Expected Output**:
```
🎉 Sacred Geometry Bash Compatibility Layer Loaded!
   - Use bash commands naturally in PowerShell
   - Type 'Get-BashHelp' for command reference
```

- [ ] Profile reloaded without errors
- [ ] Sacred Geometry banner still appears (guard not triggered)

---

## Step 7: Test Guard Activation

```powershell
# Set environment variable to activate guard
$env:CF_SKIP_BASH_LAYER = '1'

# Reload profile
. $legacyProfile

# Check if guard worked
if ($env:PYTHONIOENCODING -eq 'utf-8' -and $global:PHI -eq $null) {
    Write-Host "✅ Guard clause working correctly!" -ForegroundColor Green
} else {
    Write-Host "❌ Guard clause NOT working - Sacred Geometry still loaded" -ForegroundColor Red
}
```

**Expected Output**: `✅ Guard clause working correctly!`

**Verification Criteria**:
- [ ] No Sacred Geometry banner displayed
- [ ] `$global:PHI` variable is `$null` (Sacred Geometry constants not loaded)
- [ ] `$env:PYTHONIOENCODING` is `'utf-8'` (UTF-8 encoding still set)
- [ ] No errors or warnings

---

## Step 8: Test VS Code Task Integration

```powershell
# Clear environment variable for next test
Remove-Item Env:\CF_SKIP_BASH_LAYER -ErrorAction SilentlyContinue

# Close and reopen VS Code terminal to reset
```

**In VS Code**:

1. Open Command Palette: `Ctrl+Shift+P`
2. Type: `Tasks: Run Task`
3. Select: `Python: Pytest (with-logging)`

**Expected Behavior**:
- [ ] Task starts without Sacred Geometry banner
- [ ] No `-Command` error
- [ ] Tests execute successfully (442 passing)
- [ ] JSONL log file created: `.ai-workspace/cf-terminal-observability/logs/task-frame.jsonl`

---

## Step 9: Verify JSONL Logging

```powershell
# Check if log file exists
$logFile = '.ai-workspace/cf-terminal-observability/logs/task-frame.jsonl'
if (Test-Path $logFile) {
    Write-Host "✅ JSONL log file exists" -ForegroundColor Green

    # Display last 2 log entries (start and end)
    Get-Content $logFile -Tail 2 | ForEach-Object {
        $_ | ConvertFrom-Json | Format-List event, timestamp_utc, label, exit_code, duration_ms
    }
} else {
    Write-Host "❌ JSONL log file NOT created" -ForegroundColor Red
}
```

**Expected Output**:
```
✅ JSONL log file exists

event         : command_start
timestamp_utc : 2025-12-29T19:00:15.1234567Z
label         : Python: Pytest (with-logging)

event         : command_end
timestamp_utc : 2025-12-29T19:00:23.5678901Z
label         : Python: Pytest (with-logging)
exit_code     : 0
duration_ms   : 8445
```

- [ ] JSONL log file exists
- [ ] `command_start` event logged
- [ ] `command_end` event logged with `exit_code: 0`
- [ ] `duration_ms` recorded

---

## Step 10: Compare Task Performance

**Run both task variants and compare**:

### Direct Execution Task
```
Ctrl+Shift+P → Tasks: Run Task → "Python: Pytest (direct)"
```

- [ ] No profile loading (immediate test start)
- [ ] Duration: ~8.5 seconds (baseline)

### Wrapper Task
```
Ctrl+Shift+P → Tasks: Run Task → "Python: Pytest (with-logging)"
```

- [ ] Profile guard activates (no Sacred Geometry banner)
- [ ] Duration: ~8.7 seconds (+200ms overhead acceptable)
- [ ] JSONL logs created

---

## Step 11: Validate Profile Restoration

**Test that normal interactive shells still work**:

1. Open NEW PowerShell terminal (not VS Code integrated terminal)
2. Observe startup

**Expected Behavior**:
- [ ] Sacred Geometry banner APPEARS (guard not active)
- [ ] Bash aliases available (`ls`, `cat`, etc.)
- [ ] `$global:PHI` variable exists

**Verification**:
```powershell
# Check Sacred Geometry constants
$global:PHI
# Expected: 1.6180339887498948

# Check bash aliases
Get-Alias ls
# Expected: ls -> Get-ChildItem
```

---

## Troubleshooting

### ❌ Guard clause not working (Sacred Geometry still loads)

**Cause**: Guard clause not at top of file OR syntax error

**Fix**:
1. Open profile: `code ($PROFILE.Replace('Microsoft.PowerShell_', ''))`
2. Ensure guard clause is FIRST block (line 1-11)
3. Check for typos in `if` statement
4. Verify `return` statement present

---

### ❌ JSONL log file not created

**Cause**: Environment variable not set OR directory doesn't exist

**Fix**:
```powershell
# Create log directory if missing
New-Item -ItemType Directory -Path '.ai-workspace/cf-terminal-observability/logs' -Force

# Verify task configuration includes:
# "env": { "CF_TERMINAL_FRAME_LOG": "..." }
```

---

### ❌ Tests fail with "module not found" error

**Cause**: Working directory incorrect

**Fix**:
- Verify task `cwd` option: `"cwd": "${workspaceFolder}/TaskMan-v2/backend-api"`
- Ensure Python venv activated

---

### ❌ UTF-8 encoding issues (garbled characters)

**Cause**: Guard clause missing UTF-8 configuration

**Fix**:
- Ensure guard clause includes:
  ```powershell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  [Console]::InputEncoding = [System.Text.Encoding]::UTF8
  ```

---

## Success Criteria

**All checkboxes must be checked** for validation to pass:

- [ ] Profile guard clause installed as FIRST block
- [ ] Backup created before modification
- [ ] Syntax validation passed (profile reloads without errors)
- [ ] Guard activation test passed (Sacred Geometry not loaded when `CF_SKIP_BASH_LAYER=1`)
- [ ] VS Code task "Python: Pytest (with-logging)" runs successfully
- [ ] JSONL log file created with `command_start` and `command_end` events
- [ ] Performance overhead acceptable (~200ms)
- [ ] Normal interactive shells still work (Sacred Geometry loads)

**If ALL criteria met**: ✅ **VALIDATION COMPLETE**

**If ANY criteria failed**: ❌ **Review troubleshooting section and retry**

---

## Rollback Procedure

**If guard clause causes issues**:

```powershell
# Restore from backup
$timestamp = '<your-backup-timestamp>'
$legacyProfile = $PROFILE.Replace('Microsoft.PowerShell_', '')
$backupPath = "$legacyProfile.backup-$timestamp"

Copy-Item $backupPath $legacyProfile -Force
Write-Host "Profile restored from backup"

# Reload profile
. $legacyProfile
```

---

**Checklist Version**: 1.0.0
**Last Updated**: 2025-12-29
**Estimated Completion Time**: 5 minutes
**Difficulty**: Easy
**Risk Level**: Low (backup created before modification)
