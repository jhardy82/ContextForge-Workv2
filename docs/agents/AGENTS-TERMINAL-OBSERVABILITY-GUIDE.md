# Agent Terminal Observability Guide

**Version**: 1.0.0
**Created**: 2025-11-21
**Authority**: Research from VS Code, PowerShell, and PSReadLine documentation
**Status**: Complete

---

## Purpose

This document provides **comprehensive guidance** for AI agents to achieve **maximum terminal observability** in PowerShell environments, particularly within VS Code. It synthesizes best practices from multiple research streams into actionable implementation patterns.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [VS Code Shell Integration (OSC 633)](#vs-code-shell-integration-osc-633)
3. [PowerShell Profile Optimization](#powershell-profile-optimization)
4. [PSReadLine Configuration](#psreadline-configuration)
5. [Environment Variables](#environment-variables)
6. [Detection Patterns](#detection-patterns)
7. [Implementation Checklist](#implementation-checklist)
8. [Troubleshooting](#troubleshooting)
9. [References](#references)

---

## Executive Summary

**Goal**: Enable AI agents to reliably observe, capture, and parse terminal output with minimal interference from interactive features.

**Key Principles**:
1. **OSC 633 Integration**: Leverage VS Code's shell integration for command tracking
2. **Profile Optimization**: Detect automation contexts and skip expensive interactive features
3. **PSReadLine Configuration**: Disable predictions, tooltips, and visual noise for agents
4. **Environment Variables**: Use standard flags (NO_COLOR, TERM=dumb) for machine-parsable output
5. **Graceful Degradation**: Work in both interactive and automation modes

**Target Outcomes**:
- ✅ Command boundaries clearly marked (OSC 633 sequences)
- ✅ Output is clean, parsable text (no ANSI unless needed)
- ✅ Profile loads fast in automation (<100ms) and reasonably in interactive (<500ms)
- ✅ Agents can reliably extract exit codes, timing, and output

---

## VS Code Shell Integration (OSC 633)

### What is OSC 633?

**Operating System Command (OSC) 633** is a suite of escape sequences that VS Code injects into shells to enable:
- **Command tracking**: Know when commands start/end
- **Output capture**: Isolate command output from prompts
- **Exit code detection**: Reliable $LASTEXITCODE/$? capture
- **CWD tracking**: Monitor directory changes
- **Terminal features**: Right-click context, rerun commands, decorations

### How It Works

VS Code modifies the PowerShell prompt function to emit OSC sequences:

```powershell
# Injected by VS Code (simplified)
function prompt {
    $loc = Get-Location
    # OSC 633 ; P ; Cwd=<path> ST (mark prompt start with CWD)
    # OSC 633 ; A ST (mark prompt end, command input start)
    "PS $loc> "
    # OSC 633 ; B ST (mark command input end)
    # OSC 633 ; C ST (mark command execution start)
}

# After command completes:
# OSC 633 ; D ; <exit_code> ST (mark command execution end with exit code)
```

**Sequences**:
- `OSC 633 ; A ST` - Prompt start
- `OSC 633 ; B ST` - Prompt end / command input start
- `OSC 633 ; C ST` - Command execution start
- `OSC 633 ; D ; <exit_code> ST` - Command execution end with exit code
- `OSC 633 ; P ; Cwd=<path> ST` - Current working directory
- `OSC 633 ; E ; <command_line> ; <nonce> ST` - Explicit command line (optional)

### Critical Issues for Agents

**Problem**: Right prompts, async widgets, and fancy themes can break OSC 633 detection.

**Affected configurations**:
- oh-my-posh with right-side segments
- Starship with right prompts
- Custom async functions in prompt
- ANSI color codes that interfere with sequence detection

**Solution**: Use minimal prompts in VS Code automation contexts:

```powershell
# Agent-friendly prompt
if ($env:TERM_PROGRAM -eq 'vscode') {
    function prompt {
        "PS $($executionContext.SessionState.Path.CurrentLocation)$('>' * ($nestedPromptLevel + 1)) "
    }
}
```

### Validation

**Check if shell integration is working**:

```powershell
# In VS Code terminal, run:
$PSStyle.OutputRendering
# Should show: Host (integration active)

# Check for OSC 633 in prompt function:
(Get-Command prompt).ScriptBlock -match '633'
# Should return: True
```

**Agent detection pattern**:

```powershell
function Test-VSCodeShellIntegration {
    # Check if VS Code injected shell integration
    $promptCode = (Get-Command prompt -ErrorAction SilentlyContinue)?.ScriptBlock
    if ($promptCode -and $promptCode -match '\x1b\]633') {
        return $true
    }

    # Fallback: Check $PSStyle.OutputRendering
    if ($PSStyle.OutputRendering -eq 'Host') {
        return $true
    }

    return $false
}
```

---

## PowerShell Profile Optimization

### Problem Statement

**Interactive profiles** load modules, configure prompts, and initialize tooling that:
- Takes 500ms-3000ms to load
- Produces visual output (logos, tips, version checks)
- Makes network calls (update checks, telemetry)
- Is unnecessary for automation/agent contexts

### Detection Pattern (Layered Approach)

Use **multiple checks** to detect automation contexts:

```powershell
# Profile: Detect automation/CI context
function Test-AutomationContext {
    # Layer 1: CI environment variables
    $ciFlags = @('CI', 'GITHUB_ACTIONS', 'TF_BUILD', 'JENKINS_HOME', 'GITLAB_CI')
    if ($ciFlags | Where-Object { $env:$_ }) { return $true }

    # Layer 2: PowerShell host state
    if ([Environment]::GetCommandLineArgs() -contains '-NonInteractive') { return $true }
    if ($Host.Name -eq 'ServerRemoteHost') { return $true }

    # Layer 3: Console UI availability
    if (-not [Console]::IsInputRedirected -and -not [Console]::IsOutputRedirected) {
        # Interactive console likely
    } else {
        return $true  # Redirected I/O = automation
    }

    # Layer 4: VS Code terminal + agent context
    if ($env:TERM_PROGRAM -eq 'vscode' -and $env:VSCODE_AGENT_MODE -eq '1') {
        return $true
    }

    return $false
}
```

### Lazy Loading Pattern

**Defer expensive operations** until first use:

```powershell
# Profile: Lazy load oh-my-posh
if (-not (Test-AutomationContext)) {
    # Register lazy loader
    $ExecutionContext.InvokeCommand.CommandNotFoundAction = {
        param($CommandName, $CommandLookupEventArgs)

        if ($CommandName -eq 'oh-my-posh' -and (Get-Command oh-my-posh -ErrorAction SilentlyContinue)) {
            oh-my-posh init pwsh --config ~/.config/ohmyposh/theme.json | Invoke-Expression
            $CommandLookupEventArgs.StopSearch = $false  # Retry resolution
        }
    }

    # Or: Lazy load on first Git repo entry
    $global:__git_repo_entered = $false
    function prompt {
        if (-not $global:__git_repo_entered -and (Test-Path .git)) {
            $global:__git_repo_entered = $true
            Import-Module posh-git
        }
        # Minimal prompt until oh-my-posh loads
        "PS $($executionContext.SessionState.Path.CurrentLocation)> "
    }
}
```

### Performance Targets

| Context | Load Time Target | Strategy |
|---------|------------------|----------|
| **CI/Automation** | ~0ms | Use `-NoProfile` flag |
| **Agent in VS Code** | <100ms | Skip all interactive features |
| **Interactive** | <500ms | Lazy load, async init where possible |

### Implementation Example

```powershell
# Microsoft.PowerShell_profile.ps1
# Optimized for agent observability

# === AUTOMATION DETECTION ===
$isAutomation = Test-AutomationContext  # (function defined above)

if ($isAutomation) {
    # === AGENT-FRIENDLY MODE ===

    # Minimal prompt (preserves OSC 633 if in VS Code)
    if ($env:TERM_PROGRAM -eq 'vscode') {
        # VS Code will inject OSC 633 sequences
        function prompt { "PS $($executionContext.SessionState.Path.CurrentLocation)> " }
    } else {
        # Plain prompt for other automation
        function prompt { "PS> " }
    }

    # Skip all interactive features
    return
}

# === INTERACTIVE MODE ===
# Load oh-my-posh, posh-git, etc. (lazily if possible)
```

---

## PSReadLine Configuration

### Agent-Friendly Settings

**Goal**: Disable interactive features that interfere with output parsing.

```powershell
# Profile or agent initialization script
if (Get-Module PSReadLine) {
    # Disable predictions (tooltips, suggestions)
    Set-PSReadLineOption -PredictionSource None

    # Disable visual/audio feedback
    Set-PSReadLineOption -BellStyle None
    Set-PSReadLineOption -ShowToolTips:$false

    # Use plain text colors (or minimal highlighting)
    Set-PSReadLineOption -Colors @{
        Command = 'White'
        Parameter = 'White'
        Operator = 'White'
        Variable = 'White'
        String = 'White'
        Number = 'White'
        Comment = 'DarkGray'
    }

    # Disable history search in inline mode
    Set-PSReadLineKeyHandler -Key UpArrow -Function HistorySearchBackward
    Set-PSReadLineKeyHandler -Key DownArrow -Function HistorySearchForward
}
```

### Disabling PSReadLine Entirely

**For maximum observability**, agents can disable PSReadLine completely:

```powershell
# Option 1: Environment variable (before PowerShell starts)
$env:PSREADLINE_ENABLED = '0'

# Option 2: Remove module (in profile or script)
if (Get-Module PSReadLine) {
    Remove-Module PSReadLine -Force
}

# Option 3: Import with -ArgumentList (in profile)
Import-Module PSReadLine -ArgumentList @{ EditMode = 'Windows'; PredictionSource = 'None' }
```

---

## Environment Variables

### Standard Flags for Machine-Parsable Output

Set these environment variables **before starting PowerShell** to ensure clean output:

```powershell
# Disable ANSI color codes across all tools
$env:NO_COLOR = '1'

# Set terminal type to "dumb" (disables fancy output)
$env:TERM = 'dumb'

# Disable PSReadLine predictions
$env:PSREADLINE_ENABLED = '0'

# Agent mode flag (custom)
$env:VSCODE_AGENT_MODE = '1'

# Force UTF-8 encoding
$env:LANG = 'en_US.UTF-8'
$env:LC_ALL = 'en_US.UTF-8'
```

### PowerShell $PSStyle Configuration

**PowerShell 7.2+** provides `$PSStyle.OutputRendering` for direct ANSI control:

```powershell
# Disable all ANSI output
$PSStyle.OutputRendering = 'PlainText'

# Or: Force ANSI (if agent can parse ANSI)
$PSStyle.OutputRendering = 'Ansi'

# Or: Let VS Code decide (default)
$PSStyle.OutputRendering = 'Host'  # Uses OSC 633 integration
```

**Agent recommendation**: Use `PlainText` unless you can reliably parse ANSI:

```powershell
if ($env:VSCODE_AGENT_MODE -eq '1') {
    $PSStyle.OutputRendering = 'PlainText'
}
```

---

## Detection Patterns

### Comprehensive Environment Detection

```powershell
function Get-TerminalEnvironment {
    [PSCustomObject]@{
        # Shell integration
        HasVSCodeIntegration = Test-VSCodeShellIntegration
        OSC633Active = (Get-Command prompt)?.ScriptBlock -match '633'

        # Host information
        HostName = $Host.Name
        IsInteractive = [Environment]::UserInteractive
        IsInputRedirected = [Console]::IsInputRedirected
        IsOutputRedirected = [Console]::IsOutputRedirected

        # Environment variables
        TermProgram = $env:TERM_PROGRAM
        Term = $env:TERM
        NoColor = $env:NO_COLOR
        AgentMode = $env:VSCODE_AGENT_MODE

        # PSReadLine state
        PSReadLineEnabled = $null -ne (Get-Module PSReadLine)
        PredictionSource = (Get-PSReadLineOption)?.PredictionSource

        # PowerShell style
        OutputRendering = $PSStyle.OutputRendering

        # Performance
        ProfileLoadTime = $null  # Measure separately
    }
}
```

---

## Implementation Checklist

### For Agent Developers

- [ ] **Before starting PowerShell**: Set environment variables (`NO_COLOR=1`, `TERM=dumb`, `PSREADLINE_ENABLED=0`)
- [ ] **Launch with flags**: Use `pwsh -NoProfile -NonInteractive` for maximum speed
- [ ] **Detect context**: Check if VS Code OSC 633 is active (`Test-VSCodeShellIntegration`)
- [ ] **Configure PSStyle**: Set `$PSStyle.OutputRendering = 'PlainText'` for clean output
- [ ] **Parse output**: Look for OSC 633 sequences to identify command boundaries
- [ ] **Extract exit codes**: Parse `OSC 633 ; D ; <code>` or check `$LASTEXITCODE`
- [ ] **Handle timeouts**: Set reasonable timeouts for profile loads and command execution

### For Profile Authors

- [ ] **Detect automation**: Use `Test-AutomationContext` pattern
- [ ] **Skip expensive features**: No oh-my-posh, posh-git, network calls in automation
- [ ] **Preserve OSC 633**: Don't override prompt function in VS Code if integration is active
- [ ] **Lazy load**: Defer module imports until first use
- [ ] **Performance test**: Measure profile load time (`Measure-Command { . $PROFILE }`)

---

## Troubleshooting

### Issue: OSC 633 sequences not detected

**Symptoms**: Agent cannot parse command boundaries, exit codes missing.

**Diagnosis**:
```powershell
# Check if VS Code injected OSC 633
(Get-Command prompt).ScriptBlock -match '633'
```

**Solutions**:
1. Verify you're in a VS Code integrated terminal (`$env:TERM_PROGRAM -eq 'vscode'`)
2. Check profile isn't overriding prompt function
3. Disable oh-my-posh/Starship right prompts
4. Update VS Code to latest version

### Issue: Profile loads slowly in automation

**Symptoms**: Agent waits 2-3 seconds for PowerShell to initialize.

**Diagnosis**:
```powershell
Measure-Command { pwsh -NoProfile -NonInteractive -Command 'exit' }
# Should be <100ms

Measure-Command { pwsh -Command 'exit' }
# Compare with profile
```

**Solutions**:
1. Use `pwsh -NoProfile` for agent operations
2. Add automation detection to profile (skip expensive features)
3. Lazy load modules instead of eager import
4. Profile your profile: `Measure-Command { . $PROFILE }`

### Issue: ANSI codes in output

**Symptoms**: Agent sees `\x1b[31m` escape codes in text.

**Solutions**:
```powershell
# Set environment variable before PowerShell starts
$env:NO_COLOR = '1'

# Or in PowerShell:
$PSStyle.OutputRendering = 'PlainText'
```

### Issue: PSReadLine interferes with automation

**Symptoms**: Predictions, tooltips, or history search appears in output.

**Solutions**:
```powershell
# Disable before PowerShell starts
$env:PSREADLINE_ENABLED = '0'

# Or in session:
Set-PSReadLineOption -PredictionSource None
Remove-Module PSReadLine -Force
```

---

## References

### Official Documentation

1. **VS Code Shell Integration**:
   - [Terminal Shell Integration](https://code.visualstudio.com/docs/terminal/shell-integration)
   - [OSC 633 Sequences](https://code.visualstudio.com/docs/terminal/shell-integration#_vs-code-custom-sequences-osc-633)

2. **PowerShell Profile Optimization**:
   - [about_Profiles](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_profiles)
   - [PowerShell Performance Tips](https://learn.microsoft.com/en-us/powershell/scripting/dev-cross-plat/performance/script-authoring-considerations)

3. **PSReadLine Configuration**:
   - [PSReadLine Documentation](https://learn.microsoft.com/en-us/powershell/module/psreadline/)
   - [Set-PSReadLineOption](https://learn.microsoft.com/en-us/powershell/module/psreadline/set-psreadlineoption)

4. **ANSI and $PSStyle**:
   - [about_ANSI_Terminals](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_ansi_terminals)
   - [$PSStyle](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_psStyle)

### Related Documents

- [AGENTS.md](../AGENTS.md) - Agent development guide
- [scripts/Invoke-TerminalDiagnostics.ps1](../scripts/Invoke-TerminalDiagnostics.ps1) - Diagnostics tool
- [.github/instructions/taming-copilot.instructions.md](../.github/instructions/taming-copilot.instructions.md) - Agent control patterns

---

**Document Status**: Complete ✅
**Maintained By**: ContextForge Agent Systems Team
**Next Review**: 2026-02-21 (quarterly)

---

*"Observability is the foundation of reliability. Agents that can see clearly can act decisively."*
