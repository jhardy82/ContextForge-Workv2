# Terminal Observability Best Practices for AI Agents

**Version**: 1.0
**Created**: 2025-11-21
**Purpose**: Comprehensive guide for optimizing PowerShell terminals for maximum observability with GitHub Copilot and AI agents in VS Code

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [VS Code Shell Integration (OSC 633)](#vs-code-shell-integration-osc-633)
3. [PowerShell Profile Optimization](#powershell-profile-optimization)
4. [PSReadLine Configuration](#psreadline-configuration)
5. [ANSI & Escape Sequence Management](#ansi--escape-sequence-management)
6. [Complete Implementation Guide](#complete-implementation-guide)
7. [Troubleshooting](#troubleshooting)
8. [References](#references)

---

## Executive Summary

### Key Principles

1. **Shell Integration is Critical**: VS Code's OSC 633 sequences enable reliable command tracking and output capture for agents
2. **Minimize Startup Overhead**: Guard profiles for non-interactive/agent contexts, lazy-load expensive modules
3. **Machine-Readable Output**: Use PlainText rendering and suppress PSReadLine visual features for agents
4. **Conditional Configuration**: Detect context (interactive vs automation vs agent) and configure accordingly

### Quick Wins

- ✅ Enable and verify VS Code shell integration ("Rich" status)
- ✅ Add profile guards to skip heavy initialization for agents/CI
- ✅ Set PSReadLine to `PredictionSource None` for automation contexts
- ✅ Use `$PSStyle.OutputRendering = 'PlainText'` for machine-parsable output
- ✅ Keep prompts simple in VS Code (disable RPROMPT, async widgets)

### Performance Targets

- **CI/Automation**: ~0ms (via `-NoProfile -NonInteractive`)
- **Interactive Sessions**: <300-500ms profile load time
- **Agent Sessions**: <100ms with minimal PSReadLine, plain text output

---

## VS Code Shell Integration (OSC 633)

### What Are OSC 633 Sequences?

OSC (Operating System Command) 633 sequences are escape sequences that VS Code uses for "shell integration":

- **OSC 633;A** — Prompt start
- **OSC 633;B** — Prompt end
- **OSC 633;C** — Pre-execution
- **OSC 633;D[;exitCode]** — Execution finished
- **OSC 633;E;commandLine[;nonce]** — Explicit command line
- **OSC 633;P;Property=Value** — Set properties (e.g., `Cwd`)

**Official Documentation**: [VS Code Terminal Shell Integration](https://code.visualstudio.com/docs/terminal/shell-integration)

### Why Shell Integration Matters for Agents

- **Command Segmentation**: Agents can reliably detect where commands start/end
- **Output Capture**: Tools like `#terminalLastCommand` and `#getTerminalOutput` depend on it
- **CWD Tracking**: Accurate working directory detection improves file link resolution
- **Completion Detection**: Agents know when commands finish to avoid hanging

**Critical**: When shell integration breaks, agents may:
- Fail to see terminal output
- Hang waiting for completion
- Misinterpret command boundaries

### Validating Shell Integration Status

In VS Code terminal:
1. Hover over terminal tab
2. Tooltip shows: **"Shell integration: Rich/Basic/None"**
3. **Rich** is ideal; **None** means broken integration

### Common Issues & Solutions

#### Issue: Seeing Raw `]633;A` Sequences

**Cause**: Missing BEL terminator or emitting sequences outside VS Code

**Solution**:
```powershell
# Always guard on TERM_PROGRAM
if ($env:TERM_PROGRAM -eq 'vscode') {
    $esc = [char]27; $bel = [char]7
    [Console]::Out.Write("$esc]633;A$bel")
}
```

#### Issue: Agents Hang or Miss Output

**Cause**: Complex prompts (right prompts, async widgets) break command detection

**Solution**:
```powershell
# In VS Code terminal, keep prompts minimal
if ($env:TERM_PROGRAM -eq 'vscode') {
    # Disable right prompts
    $env:POSH_TRANSIENT_PROMPT = '1'
    # Use simple prompt
    function global:prompt { "PS $($PWD.Path)> " }
}
```

#### Issue: Plugins Disable Integration

**Cause**: Some shell plugins unset `$VSCODE_SHELL_INTEGRATION`

**Solution**: Use manual installation from [VS Code docs](https://code.visualstudio.com/docs/terminal/shell-integration#_manual-installation)

### Best Practices for OSC 633

1. **Let VS Code Handle It**: Prefer VS Code's built-in shell integration script
2. **Guard Emissions**: Only emit OSC 633 when `TERM_PROGRAM=vscode`
3. **Always Terminate**: End sequences with BEL (`\a` or `[char]7`)
4. **Keep Prompts Simple**: Disable RPROMPT and async features in VS Code
5. **Escape Payloads**: For OSC 633;E, escape semicolons and control chars

### Example: Minimal OSC 633 in PowerShell

```powershell
if ($env:TERM_PROGRAM -eq 'vscode') {
    function Send-Osc633([string]$suffix) {
        $esc = [char]27; $bel = [char]7
        [Console]::Out.Write("$esc]633;$suffix$bel")
    }

    function global:prompt {
        Send-Osc633 "A"  # Prompt start
        Send-Osc633 "P;Cwd=$((Get-Location).Path)"  # Update CWD
        Send-Osc633 "B"  # Prompt end
        "PS $((Get-Location).Path)> "
    }
}
```

---

## PowerShell Profile Optimization

### Context Detection Framework

Robust detection of interactive vs automation vs agent sessions:

```powershell
function Test-IsNonInteractiveFlag {
    try {
        [Environment]::CommandLine -match '(?i)(^|\s)-NonInteractive(\s|$)'
    } catch { $false }
}

function Test-IsCI {
    @(
        $env:CI -eq 'true',
        $env:GITHUB_ACTIONS -eq 'true',
        $env:TF_BUILD -eq 'True',
        ![string]::IsNullOrEmpty($env:AGENT_ID),
        ![string]::IsNullOrEmpty($env:SYSTEM_COLLECTIONURI)
    ) -contains $true
}

function Test-IsVSCodeTerminal {
    @(
        $env:TERM_PROGRAM -eq 'vscode',
        $Host.Name -like '*Visual Studio*',
        ![string]::IsNullOrEmpty($env:VSCODE_GIT_IPC_HANDLE)
    ) -contains $true
}

function Test-HasConsoleUI {
    try {
        if ($null -eq $Host.UI -or $null -eq $Host.UI.RawUI) { return $false }
        $null = $Host.UI.RawUI.WindowTitle
        $true
    } catch { $false }
}

function Test-IsInteractiveSession {
    if (Test-IsNonInteractiveFlag) { return $false }
    if (Test-IsCI) { return $false }
    if (-not (Test-HasConsoleUI)) { return $false }

    $userInteractive = $false
    try { $userInteractive = [Environment]::UserInteractive } catch {}
    ($userInteractive -or $Host.Name -eq 'ConsoleHost')
}
```

### Profile Guard Pattern

**Place at the top of your profile** (Microsoft.PowerShell_profile.ps1):

```powershell
# === Profile Guard (Top of file) ===
$__profileSw = [System.Diagnostics.Stopwatch]::StartNew()

# Hard skips for automation and non-interactive
if (Test-IsCI)                     { return }
if (Test-IsNonInteractiveFlag)     { return }
if (-not (Test-IsInteractiveSession)) { return }

# Optional: Keep VS Code ultra-minimal (uncomment to skip all profile logic)
# if (Test-IsVSCodeTerminal)        { return }

# === From here: only interactive sessions execute ===
```

### Lazy Loading Pattern

**Defer expensive modules until actually needed**:

```powershell
# Single-flight guard
$script:__init = @{}
function Invoke-Once {
    param([string]$Key, [ScriptBlock]$Init)
    if ($script:__init.ContainsKey($Key)) { return }
    $script:__init[$Key] = $true
    & $Init
}

# Lazy oh-my-posh: initialize on first prompt render
$script:__ompConfigured = $false
function global:prompt {
    if (-not $script:__ompConfigured) {
        $script:__ompConfigured = $true

        if (Test-IsInteractiveSession -and (Get-Command oh-my-posh -ErrorAction SilentlyContinue)) {
            Invoke-Once 'oh-my-posh:init' {
                oh-my-posh init pwsh | Invoke-Expression
            }
        }
    }

    # Lazy posh-git: only load when in a Git repo
    if (-not (Get-Module posh-git) -and (Get-Command git -ErrorAction SilentlyContinue)) {
        try {
            if (Test-Path (Join-Path -Path (Get-Location) -ChildPath '.git')) {
                Invoke-Once 'posh-git:import' {
                    Import-Module posh-git -ErrorAction SilentlyContinue
                }
            }
        } catch {}
    }

    "PS $($executionContext.SessionState.Path.CurrentLocation)> "
}
```

### Performance Measurement

**External timing**:
```powershell
# Measure no-profile baseline
Measure-Command { pwsh -NoLogo -NoProfile -Command 1 | Out-Null }

# Measure with profile
Measure-Command { pwsh -NoLogo -Command 1 | Out-Null }
```

**Internal timing** (in profile):
```powershell
$__profileSw = [System.Diagnostics.Stopwatch]::StartNew()
# ... profile logic ...
$__profileSw.Stop()
Write-Verbose ("[profile] loaded in $($__profileSw.ElapsedMilliseconds) ms")
```

**Trace command discovery**:
```powershell
Trace-Command -Name CommandDiscovery, ParameterBinding `
    -Expression { Get-Command git } -PSHost
```

---

## PSReadLine Configuration

### Agent-Friendly Settings

**Disable visual features that interfere with output capture**:

```powershell
if (Test-IsInteractiveSession) {
    if (Get-Module PSReadLine) {
        Set-PSReadLineOption `
            -PredictionSource None `
            -ShowToolTips:$false `
            -BellStyle None `
            -HistorySaveStyle SaveNothing
    }
}
```

### PredictionSource Options

| Setting | Behavior | Use Case |
|---------|----------|----------|
| **None** | No predictions | Automation, agents, CI |
| **History** | History-based suggestions | Minimal interactive |
| **HistoryAndPlugin** | History + plugins (e.g., Az.Tools.Predictor) | Rich interactive |
| **Plugin** | Plugin predictions only | Specialized scenarios |

**For agents**: Always use **None**

### Complete Minimal Configuration

```powershell
# For agent/automation contexts
if ($env:AGENT_CONTEXT -eq '1' -or $env:CI -eq 'true') {
    if (Get-Command Set-PSReadLineOption -ErrorAction Ignore) {
        Set-PSReadLineOption `
            -PredictionSource None `
            -ShowToolTips:$false `
            -BellStyle None `
            -HistorySaveStyle SaveNothing `
            -ErrorAction SilentlyContinue
    }

    # Optional: completely remove PSReadLine for headless contexts
    # if (Get-Module PSReadLine) { Remove-Module PSReadLine -Force }
}
```

---

## ANSI & Escape Sequence Management

### $PSStyle.OutputRendering Modes

PowerShell 7.2+ provides direct control via `$PSStyle.OutputRendering`:

| Mode | Terminal Display | Redirected/Piped | Use Case |
|------|------------------|------------------|----------|
| **Host** (default) | ANSI if supported | ANSI removed | Interactive terminals |
| **PlainText** | No ANSI | No ANSI | Machine parsing, CI logs |
| **Ansi** | ANSI | ANSI preserved | Preserve styling in artifacts |

### Environment Variables

- **NO_COLOR=1**: Forces `$PSStyle.OutputRendering = 'PlainText'`
- **TERM=dumb**: Disables VT support, sets PlainText rendering

### Agent Configuration

**For machine-readable output**:

```powershell
# Force plain text for the session
$PSStyle.OutputRendering = 'PlainText'
$env:NO_COLOR = '1'
$env:TERM = 'dumb'
```

**VS Code settings** (persist for integrated terminal):

```json
{
  "terminal.integrated.env.windows": {
    "NO_COLOR": "1",
    "TERM": "dumb",
    "AGENT_CONTEXT": "1"
  }
}
```

### Scoped ANSI Control

**Temporarily suppress ANSI for specific commands**:

```powershell
$prev = $PSStyle.OutputRendering
try {
    $PSStyle.OutputRendering = 'PlainText'
    Get-ChildItem | Format-Table | Out-File .\output.txt
}
finally {
    $PSStyle.OutputRendering = $prev
}
```

**Preserve ANSI in redirected output** (when downstream tools need it):

```powershell
$prev = $PSStyle.OutputRendering
try {
    $PSStyle.OutputRendering = 'Ansi'
    Get-Service | Format-Table | Out-File .\services.ansi.txt
}
finally {
    $PSStyle.OutputRendering = $prev
}
```

---

## Complete Implementation Guide

### Step 1: Create Optimized Profile

Save as `Microsoft.PowerShell_profile.ps1`:

```powershell
# ===========================================
# Optimized PowerShell Profile
# Agent-safe, Interactive-friendly
# ===========================================

$__profileSw = [System.Diagnostics.Stopwatch]::StartNew()

# ---- Context Detection Helpers ----

function Test-IsNonInteractiveFlag {
    try { [Environment]::CommandLine -match '(?i)(^|\s)-NonInteractive(\s|$)' } catch { $false }
}

function Test-IsCI {
    @(
        $env:CI -eq 'true',
        $env:GITHUB_ACTIONS -eq 'true',
        $env:TF_BUILD -eq 'True',
        ![string]::IsNullOrEmpty($env:AGENT_ID),
        ![string]::IsNullOrEmpty($env:SYSTEM_COLLECTIONURI)
    ) -contains $true
}

function Test-IsVSCodeTerminal {
    @(
        $env:TERM_PROGRAM -eq 'vscode',
        $Host.Name -like '*Visual Studio*',
        ![string]::IsNullOrEmpty($env:VSCODE_GIT_IPC_HANDLE)
    ) -contains $true
}

function Test-HasConsoleUI {
    try {
        if ($null -eq $Host.UI -or $null -eq $Host.UI.RawUI) { return $false }
        $null = $Host.UI.RawUI.WindowTitle
        $true
    } catch { $false }
}

function Test-IsInteractiveSession {
    if (Test-IsNonInteractiveFlag) { return $false }
    if (Test-IsCI) { return $false }
    if (-not (Test-HasConsoleUI)) { return $false }
    $userInteractive = $false
    try { $userInteractive = [Environment]::UserInteractive } catch {}
    ($userInteractive -or $Host.Name -eq 'ConsoleHost')
}

# ---- Profile Guards ----

if (Test-IsCI)                     { return }
if (Test-IsNonInteractiveFlag)     { return }
if (-not (Test-IsInteractiveSession)) { return }

# ---- Agent Context Configuration ----

if ($env:AGENT_CONTEXT -eq '1') {
    # Force plain text output
    $PSStyle.OutputRendering = 'PlainText'

    # Minimal PSReadLine
    if (Get-Command Set-PSReadLineOption -ErrorAction Ignore) {
        Set-PSReadLineOption `
            -PredictionSource None `
            -ShowToolTips:$false `
            -BellStyle None `
            -HistorySaveStyle SaveNothing `
            -ErrorAction SilentlyContinue
    }
}

# ---- Interactive Configuration ----

# PSReadLine (light config)
if (Get-Module PSReadLine) {
    Set-PSReadLineOption `
        -PredictionSource History `
        -ErrorAction SilentlyContinue
}

# ---- Lazy Loading ----

$script:__init = @{}
function Invoke-Once {
    param([string]$Key, [ScriptBlock]$Init)
    if ($script:__init.ContainsKey($Key)) { return }
    $script:__init[$Key] = $true
    & $Init
}

# Lazy oh-my-posh
$script:__ompConfigured = $false
function global:prompt {
    if (-not $script:__ompConfigured) {
        $script:__ompConfigured = $true
        if (Get-Command oh-my-posh -ErrorAction SilentlyContinue) {
            Invoke-Once 'oh-my-posh' {
                oh-my-posh init pwsh | Invoke-Expression
            }
        }
    }

    # Lazy posh-git (only in Git repos)
    if (-not (Get-Module posh-git) -and (Get-Command git -ErrorAction SilentlyContinue)) {
        try {
            if (Test-Path (Join-Path -Path (Get-Location) -ChildPath '.git')) {
                Invoke-Once 'posh-git' {
                    Import-Module posh-git -ErrorAction SilentlyContinue
                }
            }
        } catch {}
    }

    "PS $($executionContext.SessionState.Path.CurrentLocation)> "
}

# ---- Profile Load Time ----

try {
    $__profileSw.Stop()
    # Uncomment to always see timing:
    # Write-Host ("[profile] loaded in $($__profileSw.ElapsedMilliseconds) ms") -ForegroundColor DarkGray
} catch {}
```

### Step 2: Configure VS Code Settings

Add to `.vscode/settings.json`:

```json
{
  "terminal.integrated.profiles.windows": {
    "PowerShell (Agent-Optimized)": {
      "path": "pwsh.exe",
      "args": ["-NoLogo", "-NoExit"],
      "env": {
        "AGENT_CONTEXT": "1",
        "NO_COLOR": "1",
        "TERM": "dumb"
      },
      "icon": "robot"
    },
    "PowerShell (Interactive)": {
      "path": "pwsh.exe",
      "args": ["-NoLogo", "-NoExit"],
      "icon": "terminal-powershell"
    }
  },
  "terminal.integrated.defaultProfile.windows": "PowerShell (Agent-Optimized)",
  "terminal.integrated.env.windows": {
    "TERM_PROGRAM": "vscode"
  }
}
```

### Step 3: Validate Shell Integration

1. Open VS Code integrated terminal
2. Hover terminal tab → Verify **"Shell integration: Rich"**
3. If not Rich, manually install: [VS Code Shell Integration Docs](https://code.visualstudio.com/docs/terminal/shell-integration#_manual-installation)

### Step 4: Test Performance

```powershell
# Measure profile load time
Measure-Command { pwsh -NoLogo -NoProfile -Command 1 | Out-Null }
Measure-Command { pwsh -NoLogo -Command 1 | Out-Null }

# Target: <300-500ms with profile, <50ms without
```

---

## Troubleshooting

### Agents Can't See Terminal Output

**Symptoms**: Agents hang, miss output, or report command didn't complete

**Diagnosis**:
1. Check shell integration status (should be "Rich")
2. Verify no complex prompt themes (right prompts, async widgets)
3. Confirm OSC 633 sequences aren't doubled or malformed

**Solutions**:
- Simplify prompt in VS Code terminals
- Disable RPROMPT/right-side prompts
- Update oh-my-posh/Starship to latest version
- Use minimal prompt function (see examples above)

### Profile Takes Too Long to Load

**Symptoms**: >1 second startup time

**Diagnosis**:
```powershell
# Measure no-profile vs with-profile
Measure-Command { pwsh -NoLogo -NoProfile -Command 1 | Out-Null }
Measure-Command { pwsh -NoLogo -Command 1 | Out-Null }

# Trace command discovery
Trace-Command -Name CommandDiscovery -Expression { Get-Command git } -PSHost
```

**Solutions**:
- Add profile guards (skip non-interactive)
- Implement lazy loading for oh-my-posh, posh-git
- Defer module imports until first use
- Remove unnecessary module auto-loading from PSModulePath

### PSReadLine Predictions Polluting Logs

**Symptoms**: Logs contain inline prediction text or list-view artifacts

**Solutions**:
```powershell
# Disable predictions in agent contexts
Set-PSReadLineOption -PredictionSource None
```

### ANSI Escape Codes in Output Files

**Symptoms**: Redirected output contains escape sequences like `[0m`, `[31m`

**Solutions**:
```powershell
# Force plain text before redirecting
$PSStyle.OutputRendering = 'PlainText'
Get-ChildItem | Out-File output.txt

# Or set environment variables
$env:NO_COLOR = '1'
$env:TERM = 'dumb'
```

---

## References

### Official Documentation

- **VS Code Terminal Shell Integration**: https://code.visualstudio.com/docs/terminal/shell-integration
- **VS Code Copilot Features**: https://code.visualstudio.com/docs/copilot/reference/copilot-vscode-features
- **PowerShell Profiles**: https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_profiles
- **PowerShell about_pwsh**: https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_pwsh
- **PSReadLine Documentation**: https://learn.microsoft.com/powershell/module/psreadline/about/about_psreadline
- **about_ANSI_Terminals**: https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_ansi_terminals

### Community Resources

- **GitHub: VS Code Shell Integration Issues**: https://github.com/microsoft/vscode/issues?q=label%3Aterminal-shell-integration
- **GitHub: Copilot Agent Output Detection**: https://github.com/microsoft/vscode-copilot-release/issues/7261
- **oh-my-posh Documentation**: https://ohmyposh.dev/docs/installation/windows
- **posh-git Repository**: https://github.com/dahlbyk/posh-git

### Tools

- **Trace-Command**: https://learn.microsoft.com/powershell/module/microsoft.powershell.utility/trace-command
- **Get-TraceSource**: https://learn.microsoft.com/powershell/module/microsoft.powershell.utility/get-tracesource
- **Measure-Command**: https://learn.microsoft.com/powershell/module/microsoft.powershell.utility/measure-command

---

## Quick Reference

### One-Line Fixes

**Make session machine-readable immediately**:
```powershell
$PSStyle.OutputRendering = 'PlainText'; Set-PSReadLineOption -PredictionSource None; $env:NO_COLOR='1'; $env:TERM='dumb'
```

**Test if shell integration is working**:
```powershell
# Should show "Rich" in VS Code terminal tab hover tooltip
$env:TERM_PROGRAM -eq 'vscode'
```

**Measure profile performance**:
```powershell
Measure-Command { pwsh -NoLogo -Command 1 | Out-Null } | Select-Object TotalMilliseconds
```

### Environment Variables for Agents

```powershell
$env:AGENT_CONTEXT = '1'  # Custom flag for profile logic
$env:NO_COLOR = '1'       # Suppress ANSI globally
$env:TERM = 'dumb'        # Disable VT, force plain text
$env:TERM_PROGRAM = 'vscode'  # Signal VS Code context
```

---

**Document Status**: v1.0 Complete
**Last Updated**: 2025-11-21
**Maintained By**: ContextForge Engineering Team
