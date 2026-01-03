# PowerShell Profile Configuration

**Version**: 3.0 (Agent-Optimized)  
**Status**: Active  
**Last Updated**: 2025-11-28  
**Profile Path**: `C:\Users\james.e.hardy\Documents\PowerShell\Microsoft.PowerShell_profile.ps1`  
**Related**: [09-Development-Guidelines](09-Development-Guidelines.md) | [Terminal Output Standard](../.github/instructions/terminal-output.instructions.md)

---

## Table of Contents

1. [Overview](#overview)
2. [Deployment](#deployment)
3. [Architecture](#architecture)
4. [VS Code Shell Integration](#vs-code-shell-integration)
5. [Agent Terminal Optimizations](#agent-terminal-optimizations)
6. [Python Venv Compatibility](#python-venv-compatibility)
7. [Module Configuration](#module-configuration)
8. [Environment Detection](#environment-detection)
9. [Troubleshooting](#troubleshooting)
10. [Configuration Reference](#configuration-reference)

---

## Overview

The ContextForge PowerShell Profile is a dual-mode configuration optimized for both **AI agent terminal perception** and **human interactive use**. It automatically detects the execution environment and applies appropriate settings.

### Design Goals

| Goal | Implementation |
|------|----------------|
| **VS Code Shell Integration** | OSC 633 escape sequences for command detection |
| **Agent-Friendly Output** | Suppress ANSI noise, progress bars, colors |
| **Venv Compatibility** | Prompt wrapping works with Python virtual environments |
| **Human UX Preservation** | Full PSReadLine features when not in VS Code/CI |
| **UTF-8 Consistency** | Proper encoding for cross-platform compatibility |

### Version History

| Version | Date | Changes |
|---------|------|---------|
| v3.0 | 2025-11-28 | Added OSC 633 shell integration, removed `TERM=dumb` blocker |
| v2.0 | 2025-11-15 | Agent terminal perception optimizations |
| v1.0 | 2025-10-01 | Initial ContextForge profile |

---

## Deployment

### Quick Start

Use the deployment script to install the ContextForge profile on any system:

```powershell
# Navigate to repo root
cd "C:\Users\james.e.hardy\Documents\PowerShell Projects"

# Run deployment script
.\scripts\Deploy-PowerShellProfile.ps1
```

### Deployment Script

**Location**: [`scripts/Deploy-PowerShellProfile.ps1`](../scripts/Deploy-PowerShellProfile.ps1)

The deployment script provides:

| Feature | Description |
|---------|-------------|
| **Automatic Backup** | Creates timestamped backup of existing profile |
| **Template Deployment** | Installs profile with correct module paths |
| **Health Validation** | Post-deployment verification |
| **Interactive/Forced** | Supports `-Force` for automation |

### Usage Examples

```powershell
# Interactive deployment with confirmation
.\scripts\Deploy-PowerShellProfile.ps1

# Force deployment (skip prompts)
.\scripts\Deploy-PowerShellProfile.ps1 -Force

# Validate current profile without changes
.\scripts\Deploy-PowerShellProfile.ps1 -Validate

# Create backup only
.\scripts\Deploy-PowerShellProfile.ps1 -BackupOnly

# Custom module path
.\scripts\Deploy-PowerShellProfile.ps1 -ModulePath "D:\CustomModules"
```

### CI/CD Deployment

For automated deployment in CI/CD pipelines:

```powershell
# Silent deployment for automation
.\scripts\Deploy-PowerShellProfile.ps1 -Force -WhatIf:$false
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PowerShell Profile v3.0                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Core Encoding (Always Active)               │    │
│  │  • UTF-8 Output/Input Encoding                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│              ┌───────────────┴───────────────┐                  │
│              ▼                               ▼                  │
│  ┌─────────────────────┐       ┌─────────────────────────┐     │
│  │   VS Code / CI Mode │       │   Human Interactive     │     │
│  │                     │       │                         │     │
│  │ • OSC 633 Sequences │       │ • Standard Prompt       │     │
│  │ • Progress Suppress │       │ • PSReadLine Enhanced   │     │
│  │ • Color Suppression │       │ • Predictive Text       │     │
│  │ • Plain Text Output │       │ • History Search        │     │
│  │ • No Pagers         │       │ • Tab Completion        │     │
│  └─────────────────────┘       └─────────────────────────┘     │
│                              │                                   │
│              ┌───────────────┴───────────────┐                  │
│              ▼                               ▼                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │           Module Path + Startup Confirmation             │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## VS Code Shell Integration

### Purpose

VS Code shell integration enables:
- **Command Detection**: Highlighting executed commands in terminal
- **Exit Code Tracking**: Visual indicators for command success/failure
- **Working Directory Awareness**: VS Code knows the current path
- **Semantic Prompt Regions**: Distinct prompt vs. output areas

### OSC 633 Escape Sequences

The profile emits Operating System Command (OSC) sequences that VS Code interprets:

| Sequence | Purpose | When Emitted |
|----------|---------|--------------|
| `OSC 633;A` | Prompt Start | Before prompt text |
| `OSC 633;B` | Prompt End | After prompt text (command input starts) |
| `OSC 633;C` | Command Finished | Before command output appears |
| `OSC 633;D;{code}` | Exit Code | After command completes |
| `OSC 633;P;Cwd={path}` | Working Directory | With each prompt |

### Implementation

```powershell
function global:__VSCode-Prompt {
    # Get exit code from last command
    $lastExitCode = $global:LASTEXITCODE
    $success = $?

    # OSC 633 D: Report previous command exit code
    if ($null -ne $lastExitCode) {
        $exitCodeSeq = "`e]633;D;$lastExitCode`a"
    } else {
        $exitCodeSeq = "`e]633;D;$(if ($success) { 0 } else { 1 })`a"
    }

    # OSC 633 P: Set current working directory property
    $cwdSeq = "`e]633;P;Cwd=$((Get-Location).Path)`a"

    # OSC 633 A: Prompt Start
    $promptStartSeq = "`e]633;A`a"

    # Build the actual prompt text
    $promptText = "PS $($executionContext.SessionState.Path.CurrentLocation)$('>' * ($nestedPromptLevel + 1)) "

    # OSC 633 B: Prompt End (command input area starts)
    $promptEndSeq = "`e]633;B`a"

    # Emit: [ExitCode][Cwd][PromptStart][PromptText][PromptEnd]
    return "$exitCodeSeq$cwdSeq$promptStartSeq$promptText$promptEndSeq"
}
```

### PSReadLine Hook

The profile hooks PSReadLine's Enter key to emit `OSC 633;C` before command execution:

```powershell
Set-PSReadLineKeyHandler -Key Enter -ScriptBlock {
    [Console]::Write("`e]633;C`a")  # Mark: command input ended
    [Microsoft.PowerShell.PSConsoleReadLine]::AcceptLine()
}
```

### Verification

Check shell integration status:

```powershell
# Environment variable
$env:VSCODE_SHELL_INTEGRATION  # Should be '1'

# Prompt contains OSC sequences
$promptOutput = prompt
$promptOutput -match '\x1b\]633'  # Should be True

# Use health check module
Import-Module Agent
Test-ShellIntegrationHealth  # Should return 'Healthy'
```

---

## Agent Terminal Optimizations

### Philosophy

AI agents parsing terminal output are impaired by ANSI escape sequences, progress bars, and color codes. The profile eliminates these when running in VS Code or CI environments.

### Optimizations Applied

#### Priority 1: Progress Bar Suppression

```powershell
$ProgressPreference = 'SilentlyContinue'
```

**Problem Solved**: `Invoke-WebRequest`, `Copy-Item`, and other cmdlets emit ANSI-heavy progress bars that corrupt agent perception.

#### Priority 2: Plain Text Output

```powershell
$PSStyle.OutputRendering = 'PlainText'
```

**Problem Solved**: PowerShell 7+ outputs ANSI formatting by default; this forces plain text.

#### Priority 3: Universal Color Suppression

```powershell
$env:NO_COLOR = '1'
$env:FORCE_COLOR = '0'
```

**Problem Solved**: Many tools respect `NO_COLOR` (https://no-color.org/) to disable ANSI colors.

#### Why Not `TERM=dumb`?

Previous versions set `$env:TERM = 'dumb'` but this **blocked VS Code shell integration injection**. The profile now handles integration explicitly via OSC 633 sequences instead.

#### CI/Non-Interactive Mode

```powershell
$env:CI = 'true'
$ConfirmPreference = 'None'
$InformationPreference = 'SilentlyContinue'
```

**Problem Solved**: Prevents confirmation prompts and informational messages that could block automation.

#### Pager Control

```powershell
$env:PAGER = 'cat'
$env:GIT_PAGER = 'cat'
```

**Problem Solved**: Prevents `git log`, `man`, etc. from opening interactive pagers.

#### Python Optimizations

```powershell
$env:PYTHONUNBUFFERED = '1'
$env:TQDM_DISABLE = '1'
$env:COLUMNS = '120'
```

**Problem Solved**: 
- Unbuffered output for real-time logging
- Disable tqdm progress bars
- Set consistent column width for formatting

#### PSReadLine Noise Reduction

```powershell
Set-PSReadLineOption -PredictionSource None
Set-PSReadLineOption -BellStyle None
```

**Problem Solved**: Predictive suggestions and bell sounds create noise in agent context.

---

## Python Venv Compatibility

### The Challenge

Python virtual environment activation scripts wrap the PowerShell `prompt` function to prepend `(.venv)`. This wrapping must work correctly with our custom prompt.

### Solution Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Prompt Call Chain                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  PowerShell                                                  │
│      │                                                       │
│      ▼                                                       │
│  ┌─────────────────────────────────────────────┐            │
│  │         Venv Wrapper (if active)            │            │
│  │   Returns: "(.venv) " + inner_prompt()      │            │
│  └─────────────────────────────────────────────┘            │
│      │                                                       │
│      ▼                                                       │
│  ┌─────────────────────────────────────────────┐            │
│  │        __VSCode-Prompt Function             │            │
│  │   Returns: [OSC633][PromptText][OSC633]     │            │
│  └─────────────────────────────────────────────┘            │
│      │                                                       │
│      ▼                                                       │
│  Final Output: (.venv) [OSC sequences]PS C:\path>           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Implementation

The profile stores a reference for venv compatibility:

```powershell
# Set the prompt function - this is what venv will wrap
function global:prompt { __VSCode-Prompt }

# Store reference so venv wrapping works correctly
$global:__ContextForge_OriginalPrompt = ${function:prompt}
```

### Verification

```powershell
# After activating venv
.\.venv\Scripts\Activate.ps1

# Prompt should show (.venv) prefix
# (.venv) PS C:\Users\james.e.hardy\Documents\PowerShell Projects>

# OSC sequences should still be present
$promptOutput = prompt
$promptOutput -match '\x1b\]633'  # Should be True
```

---

## Module Configuration

### ContextForge Module Path

```powershell
$cfModulesPath = "C:\Users\james.e.hardy\Documents\PowerShell Projects\modules"
if ($env:PSModulePath -notlike "*$cfModulesPath*") {
    $env:PSModulePath = "$cfModulesPath;$env:PSModulePath"
}
```

### Available Modules

| Module | Purpose |
|--------|---------|
| `ContextForge.Spectre` | Rich terminal UI with Spectre.Console |
| `Agent` | Agent terminal logging and diagnostics |
| `Agent.AgentTerminalLogging` | Shell integration health checks |

### Loading Modules

```powershell
# Import specific module
Import-Module ContextForge.Spectre

# Import agent diagnostics
Import-Module Agent
```

---

## Environment Detection

The profile uses environment detection to apply appropriate settings:

```powershell
# VS Code Detection
if ($env:TERM_PROGRAM -eq 'vscode') {
    # Apply VS Code-specific settings
}

# CI Detection
if ($env:CI) {
    # Apply CI-specific settings
}

# Combined Check
if ($env:TERM_PROGRAM -eq 'vscode' -or $env:CI) {
    # Apply agent/automation settings
}
```

### Environment Variables Set by Profile

| Variable | Value | Purpose |
|----------|-------|---------|
| `VSCODE_SHELL_INTEGRATION` | `1` | Marks shell integration active |
| `NO_COLOR` | `1` | Suppresses colors globally |
| `FORCE_COLOR` | `0` | Disables forced colors |
| `CI` | `true` | CI mode for tools |
| `PAGER` | `cat` | Disables interactive pagers |
| `GIT_PAGER` | `cat` | Disables git pagers |
| `PYTHONUNBUFFERED` | `1` | Unbuffered Python output |
| `TQDM_DISABLE` | `1` | Disables tqdm progress bars |
| `COLUMNS` | `120` | Terminal width hint |

---

## Troubleshooting

### Shell Integration Not Active

**Symptoms**: 
- No command decorations in VS Code terminal
- `$env:VSCODE_SHELL_INTEGRATION` is empty or not `1`

**Solutions**:

1. **Reload the profile**:
   ```powershell
   . $PROFILE
   ```

2. **Open a new terminal**: Existing terminals may not have loaded the updated profile

3. **Check environment**:
   ```powershell
   $env:TERM_PROGRAM  # Should be 'vscode'
   ```

4. **Verify prompt function**:
   ```powershell
   Get-Command __VSCode-Prompt  # Should exist
   ```

### Venv Prefix Missing

**Symptoms**: Prompt shows `PS C:\path>` instead of `(.venv) PS C:\path>`

**Solutions**:

1. **Re-activate venv**:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. **Verify venv is active**:
   ```powershell
   $env:VIRTUAL_ENV  # Should show venv path
   ```

### Colors Still Appearing

**Symptoms**: Output contains ANSI color codes despite agent mode

**Solutions**:

1. **Check environment detection**:
   ```powershell
   $env:TERM_PROGRAM -eq 'vscode'  # Should be True
   ```

2. **Verify settings applied**:
   ```powershell
   $env:NO_COLOR  # Should be '1'
   $PSStyle.OutputRendering  # Should be 'PlainText'
   ```

3. **For specific tools**, add their color suppression flags:
   ```powershell
   git --no-color status
   ruff check --no-color
   ```

### Profile Not Loading

**Symptoms**: `[OK] ContextForge Profile v3.0` message not appearing

**Solutions**:

1. **Check profile path**:
   ```powershell
   Test-Path $PROFILE  # Should be True
   ```

2. **Check execution policy**:
   ```powershell
   Get-ExecutionPolicy  # Should allow script execution
   ```

3. **Manual load**:
   ```powershell
   . $PROFILE
   ```

---

## Configuration Reference

### Complete Profile Source

```powershell
# ContextForge PowerShell Profile - Agent-Optimized v3.0
# VS Code Shell Integration + AI Agent Terminal Perception + Venv Compatibility
# Last Updated: 2025-11-28

#region Core Encoding (Required)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
#endregion

#region VS Code Shell Integration
function global:__VSCode-Prompt {
    $lastExitCode = $global:LASTEXITCODE
    $success = $?

    if ($null -ne $lastExitCode) {
        $exitCodeSeq = "`e]633;D;$lastExitCode`a"
    } else {
        $exitCodeSeq = "`e]633;D;$(if ($success) { 0 } else { 1 })`a"
    }

    $cwdSeq = "`e]633;P;Cwd=$((Get-Location).Path)`a"
    $promptStartSeq = "`e]633;A`a"
    $promptText = "PS $($executionContext.SessionState.Path.CurrentLocation)$('>' * ($nestedPromptLevel + 1)) "
    $promptEndSeq = "`e]633;B`a"

    return "$exitCodeSeq$cwdSeq$promptStartSeq$promptText$promptEndSeq"
}

$global:__ContextForge_OriginalPrompt = $null

function global:__VSCode-PreCommand {
    [Console]::Write("`e]633;C`a")
}

if ($env:TERM_PROGRAM -eq 'vscode') {
    function global:prompt { __VSCode-Prompt }
    $global:__ContextForge_OriginalPrompt = ${function:prompt}

    if (Get-Module PSReadLine) {
        Set-PSReadLineKeyHandler -Key Enter -ScriptBlock {
            [Console]::Write("`e]633;C`a")
            [Microsoft.PowerShell.PSConsoleReadLine]::AcceptLine()
        }
    }

    $env:VSCODE_SHELL_INTEGRATION = '1'
}
#endregion

#region AI Agent Terminal Perception Optimizations
if ($env:TERM_PROGRAM -eq 'vscode' -or $env:CI) {
    $ProgressPreference = 'SilentlyContinue'
    $PSStyle.OutputRendering = 'PlainText'
    $env:NO_COLOR = '1'
    $env:FORCE_COLOR = '0'
    $env:CI = 'true'
    $ConfirmPreference = 'None'
    $InformationPreference = 'SilentlyContinue'
    $env:PAGER = 'cat'
    $env:GIT_PAGER = 'cat'
    $env:PYTHONUNBUFFERED = '1'
    $env:TQDM_DISABLE = '1'
    $env:COLUMNS = '120'

    if (Get-Module PSReadLine) {
        Set-PSReadLineOption -PredictionSource None -ErrorAction SilentlyContinue
        Set-PSReadLineOption -BellStyle None -ErrorAction SilentlyContinue
    }
}
#endregion

#region Module Path Configuration
$cfModulesPath = "C:\Users\james.e.hardy\Documents\PowerShell Projects\modules"
if ($env:PSModulePath -notlike "*$cfModulesPath*") {
    $env:PSModulePath = "$cfModulesPath;$env:PSModulePath"
}
#endregion

#region Human-Interactive Features
if (-not ($env:TERM_PROGRAM -eq 'vscode' -or $env:CI)) {
    function global:prompt {
        "PS $($executionContext.SessionState.Path.CurrentLocation)$('>' * ($nestedPromptLevel + 1)) "
    }

    if (Get-Module PSReadLine -ListAvailable) {
        try {
            Set-PSReadLineOption -PredictionSource HistoryAndPlugin -PredictionViewStyle ListView
            Set-PSReadLineOption -HistorySearchCursorMovesToEnd $true
            Set-PSReadLineKeyHandler -Key UpArrow -Function HistorySearchBackward
            Set-PSReadLineKeyHandler -Key DownArrow -Function HistorySearchForward
            Set-PSReadLineKeyHandler -Key Tab -Function MenuComplete
        } catch { }
    }
}
#endregion

#region Startup Confirmation
if ($env:TERM_PROGRAM -eq 'vscode' -or $env:CI) {
    $mode = if ($env:VSCODE_SHELL_INTEGRATION) { "Agent+ShellIntegration" } else { "Agent" }
    Write-Host "[OK] ContextForge Profile v3.0 ($mode)"
} else {
    Write-Host "[OK] ContextForge Profile v3.0" -ForegroundColor Green
}
#endregion
```

### File Locations

| File | Purpose |
|------|---------|
| `$PROFILE` | Main profile (`Microsoft.PowerShell_profile.ps1`) |
| `$PROFILE.backup-*` | Backup copies before updates |
| `modules/Agent/` | Agent terminal logging module |
| `modules/ContextForge.Spectre/` | Rich terminal UI module |

---

## See Also

- [09-Development-Guidelines](09-Development-Guidelines.md) - Development standards
- [Terminal Output Standard](../.github/instructions/terminal-output.instructions.md) - Rich console formatting
- [VS Code Shell Integration](https://code.visualstudio.com/docs/terminal/shell-integration) - Official documentation
- [NO_COLOR Standard](https://no-color.org/) - Color suppression convention

---

**Document Status**: Complete ✅  
**Maintained By**: ContextForge Engineering Team  
**Next Review**: 2026-02-28 (quarterly)
