# VS Code Task Profile Interference - Quick Reference

**TL;DR**: Use "Python: Pytest (direct)" task (default) for fast, reliable testing. Use "Python: Pytest (with-logging)" if you need observability (requires profile guard).

---

## Problem

VS Code tasks fail with `-Command` error due to PowerShell profile loading despite `-NoProfile` flag.

**Root Cause**: VS Code's integrated terminal loads `profile.ps1` (legacy profile) containing "Sacred Geometry Bash Compatibility Layer" that interferes with argument parsing.

---

## Quick Fix

### Option 1: Use Direct Execution (Recommended)

**When**: Standard testing, CI/CD, quick iteration

**Command Palette**: `Ctrl+Shift+P` → `Tasks: Run Task` → `Python: Pytest (direct)`

**Why**: Bypasses PowerShell entirely, runs Python directly. Fast, reliable, no configuration needed.

---

### Option 2: Use Wrapper with Profile Guard

**When**: Debugging, need JSONL logs, argument redaction required

**Prerequisites**: Add profile guard clause (one-time setup)

**Steps**:

1. **Open profile**:
   ```powershell
   code $PROFILE
   ```

2. **Add guard as FIRST block**:
   ```powershell
   #region CF Terminal Frame Skip Guard (MUST BE FIRST)
   if ($env:CF_SKIP_BASH_LAYER -eq '1') {
       [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
       [Console]::InputEncoding = [System.Text.Encoding]::UTF8
       $env:PYTHONIOENCODING = 'utf-8'
       $env:PYTHONUTF8 = '1'
       return
   }
   #endregion
   ```

3. **Run wrapper task**:
   `Ctrl+Shift+P` → `Tasks: Run Task` → `Python: Pytest (with-logging)`

4. **Verify JSONL logs**:
   ```powershell
   Get-Content '.ai-workspace/cf-terminal-observability/logs/task-frame.jsonl' -Tail 5
   ```

---

## Comparison

| Feature | Direct Execution | Wrapper (with guard) |
|---------|-----------------|---------------------|
| **Startup Time** | ~120ms | ~320ms |
| **Profile Loading** | None | Minimal (guard only) |
| **Observability** | ❌ No JSONL logs | ✅ Full JSONL logging |
| **Argument Redaction** | ❌ No | ✅ Yes (secrets scrubbed) |
| **Configuration** | ✅ None required | ⚠️ Profile guard needed |
| **CI/CD Compatibility** | ✅ Perfect | ⚠️ Requires env setup |
| **Default Task** | ✅ Yes | ❌ No (manual selection) |

---

## Troubleshooting

### "Sacred Geometry Bash Compatibility Layer Loaded!" appears

**Cause**: Profile guard not installed or not at top of profile

**Fix**: Ensure guard clause is **first block** in `$PROFILE` (before any other code)

---

### `-Command` error still occurs

**Cause**: Multiple profiles loading, guard clause bypassed

**Fix**: Check all profile locations:
```powershell
$PROFILE                                  # Current user, current host
$PROFILE.Replace('Microsoft.PowerShell_', '')  # Current user, all hosts (legacy)
```

Add guard to **both** files.

---

### JSONL logs not created

**Cause**: Environment variable not set or path doesn't exist

**Fix**: Check task configuration includes:
```json
"env": {
  "CF_TERMINAL_FRAME_LOG": "${workspaceFolder}/.ai-workspace/cf-terminal-observability/logs/task-frame.jsonl",
  "CF_SKIP_BASH_LAYER": "1"
}
```

Create directory if missing:
```powershell
mkdir -Force '.ai-workspace/cf-terminal-observability/logs'
```

---

### Direct execution task runs from wrong directory

**Cause**: Task `cwd` option not set correctly

**Fix**: Verify in `.vscode/tasks.json`:
```json
"options": {
  "cwd": "${workspaceFolder}/TaskMan-v2/backend-api"
}
```

---

## Full Documentation

See [docs/troubleshooting/vscode-task-profile-interference.md](../troubleshooting/vscode-task-profile-interference.md) for:
- Complete root cause analysis
- Evidence and timeline
- Alternative solutions evaluated
- Prevention strategies
- Profile design best practices

---

**Last Updated**: 2025-12-29
**Version**: 1.0.0
**Status**: Production Ready
