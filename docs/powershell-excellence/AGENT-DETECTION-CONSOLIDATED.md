# Agent Detection Consolidation

**Version**: 1.0.0
**Last Updated**: 2025-12-29
**Status**: Ready for Implementation

---

## Executive Summary

Agent and environment detection is currently duplicated across 5+ files. This document specifies a consolidated `Get-CFAgentContext` function to centralize detection logic with comprehensive coverage.

## Current State: Detection Fragmentation

### Duplication Inventory

| File | Detection Logic | Lines |
|------|-----------------|-------|
| `Microsoft.PowerShell_profile.ps1` | CI, VSCode | ~20 |
| `agent-profile-enhanced.ps1` | Agent mode | ~15 |
| `Test-TaskManHealth.ps1` | Environment checks | ~10 |
| `cf_cli.py` | Python CI detection | ~25 |
| Various scripts | Scattered checks | ~30 |

**Total duplicated**: ~100 lines across 5+ files

## Environment Variable Reference

### CI Platform Detection (6 platforms)

| Platform | Variable | Example Value |
|----------|----------|---------------|
| GitHub Actions | `GITHUB_ACTIONS` | `true` |
| Azure DevOps | `TF_BUILD` | `True` |
| Jenkins | `JENKINS_URL` | `https://jenkins.example.com` |
| GitLab CI | `GITLAB_CI` | `true` |
| TeamCity | `TEAMCITY_VERSION` | `2023.05` |
| Generic CI | `CI` | `true` |

### VS Code Detection (4 variables)

| Variable | Purpose | Example |
|----------|---------|---------|
| `TERM_PROGRAM` | Terminal identification | `vscode` |
| `VSCODE_SHELL_INTEGRATION` | Shell integration active | `1` |
| `VSCODE_GIT_IPC_HANDLE` | Git integration handle | `\\.\pipe\...` |
| `VSCODE_AGENT_MODE` | Copilot agent mode | `1` |

### ContextForge Control (8 variables)

| Variable | Purpose | Values |
|----------|---------|--------|
| `CF_SKIP_PROFILE` | Skip profile loading | `0`, `1` |
| `CF_SKIP_BASH_LAYER` | Skip bash compatibility | `0`, `1` |
| `CF_TRACE_ID` | Distributed trace ID | UUID |
| `CF_SESSION_ID` | Session identifier | UUID |
| `CF_PROJECT_ID` | Active project | `PROJECT-###` |
| `CF_LOG_LEVEL` | Logging verbosity | `debug`, `info`, `warn`, `error` |
| `CF_AGENT_TYPE` | Agent identification | `copilot`, `claude`, `cursor` |
| `CF_MEMORY_PATH` | Episodic memory location | Path |

### Gaps Identified

- ❌ No cloud shell detection (Azure, AWS, GCP)
- ❌ No container detection (Docker, Kubernetes)
- ❌ No centralized function (scattered logic)
- ❌ Inconsistent caching (repeated checks)

## Solution: Get-CFAgentContext

### Function Specification

```powershell
function Get-CFAgentContext {
    <#
    .SYNOPSIS
        Consolidated agent and environment detection for ContextForge.

    .DESCRIPTION
        Detects CI platforms, VS Code integration, cloud shells, containers,
        and ContextForge-specific configuration. Caches results for performance.

    .PARAMETER Force
        Bypass cache and re-detect environment.

    .OUTPUTS
        [PSCustomObject] with detection results

    .EXAMPLE
        $ctx = Get-CFAgentContext
        if ($ctx.IsCI) { Write-Host "Running in CI: $($ctx.CIPlatform)" }
    #>
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [switch]$Force
    )

    # Return cached result if available
    if ($script:CFAgentContextCache -and -not $Force) {
        return $script:CFAgentContextCache
    }

    $context = [PSCustomObject]@{
        # Timestamps
        DetectedAt    = Get-Date -Format 'o'

        # CI Detection
        IsCI          = $false
        CIPlatform    = $null

        # VS Code Detection
        IsVSCode      = $false
        VSCodeAgent   = $false

        # Cloud Shell Detection
        IsCloudShell  = $false
        CloudPlatform = $null

        # Container Detection
        IsContainer   = $false
        ContainerType = $null

        # ContextForge State
        CFTraceId     = $env:CF_TRACE_ID
        CFSessionId   = $env:CF_SESSION_ID
        CFProjectId   = $env:CF_PROJECT_ID
        CFAgentType   = $env:CF_AGENT_TYPE
        CFSkipProfile = $env:CF_SKIP_PROFILE -eq '1'

        # Environment
        IsInteractive = [Environment]::UserInteractive
        Shell         = $PSVersionTable.PSEdition
        OS            = $PSVersionTable.OS
    }

    #region CI Platform Detection
    $ciPlatforms = @{
        'GitHub Actions' = { $env:GITHUB_ACTIONS -eq 'true' }
        'Azure DevOps'   = { $env:TF_BUILD -eq 'True' }
        'Jenkins'        = { $null -ne $env:JENKINS_URL }
        'GitLab CI'      = { $env:GITLAB_CI -eq 'true' }
        'TeamCity'       = { $null -ne $env:TEAMCITY_VERSION }
        'Generic CI'     = { $env:CI -eq 'true' -or $env:CI -eq '1' }
    }

    foreach ($platform in $ciPlatforms.Keys) {
        if (& $ciPlatforms[$platform]) {
            $context.IsCI = $true
            $context.CIPlatform = $platform
            break
        }
    }
    #endregion

    #region VS Code Detection
    $vsCodeIndicators = @(
        { $env:TERM_PROGRAM -eq 'vscode' }
        { $null -ne $env:VSCODE_SHELL_INTEGRATION }
        { $null -ne $env:VSCODE_GIT_IPC_HANDLE }
        { $null -ne $env:VSCODE_PID }
    )

    foreach ($check in $vsCodeIndicators) {
        if (& $check) {
            $context.IsVSCode = $true
            break
        }
    }

    $context.VSCodeAgent = $env:VSCODE_AGENT_MODE -eq '1'
    #endregion

    #region Cloud Shell Detection (NEW)
    $cloudShells = @{
        'Azure Cloud Shell' = { $null -ne $env:AZUREPS_HOST_ENVIRONMENT }
        'AWS CloudShell'    = { $null -ne $env:AWS_EXECUTION_ENV -and
                                $env:AWS_EXECUTION_ENV -match 'CloudShell' }
        'Google Cloud Shell'= { $null -ne $env:CLOUD_SHELL -or
                                $null -ne $env:DEVSHELL_PROJECT_ID }
    }

    foreach ($cloud in $cloudShells.Keys) {
        if (& $cloudShells[$cloud]) {
            $context.IsCloudShell = $true
            $context.CloudPlatform = $cloud
            break
        }
    }
    #endregion

    #region Container Detection (NEW)
    $containerChecks = @{
        'Docker'     = {
            (Test-Path '/.dockerenv') -or
            ($env:container -eq 'docker')
        }
        'Kubernetes' = {
            $null -ne $env:KUBERNETES_SERVICE_HOST
        }
        'Podman'     = {
            $env:container -eq 'podman'
        }
    }

    foreach ($type in $containerChecks.Keys) {
        if (& $containerChecks[$type]) {
            $context.IsContainer = $true
            $context.ContainerType = $type
            break
        }
    }
    #endregion

    # Cache the result
    $script:CFAgentContextCache = $context

    return $context
}
```

### Usage Examples

```powershell
# Basic usage
$ctx = Get-CFAgentContext

# Conditional profile loading
if ($ctx.IsCI) {
    Write-Verbose "CI mode: $($ctx.CIPlatform) - minimal profile"
    return
}

# Agent-aware logging
if ($ctx.VSCodeAgent) {
    Write-CFLog -Event 'session_start' -Context @{
        agent_mode = 'vscode_copilot'
    }
}

# Cloud shell handling
if ($ctx.IsCloudShell) {
    Write-Host "Running in $($ctx.CloudPlatform)" -ForegroundColor Cyan
    # Adjust paths for cloud environment
}

# Force re-detection after environment change
$refreshed = Get-CFAgentContext -Force
```

### Integration Points

```powershell
# In Microsoft.PowerShell_profile.ps1 (top)
$ctx = Get-CFAgentContext
if ($ctx.CFSkipProfile -or $ctx.IsCI) { return }

# In logging functions
function Write-CFSessionStart {
    $ctx = Get-CFAgentContext
    Write-CFLog -Event 'session_start' -Context @{
        ci_platform    = $ctx.CIPlatform
        is_vscode      = $ctx.IsVSCode
        agent_type     = $ctx.CFAgentType ?? 'interactive'
        cloud_platform = $ctx.CloudPlatform
    }
}
```

## Implementation Checklist

- [ ] Create `Get-CFAgentContext` in shared module
- [ ] Add cloud shell detection (Azure, AWS, GCP)
- [ ] Add container detection (Docker, K8s, Podman)
- [ ] Replace scattered detection with function calls
- [ ] Add caching for performance
- [ ] Write Pester tests for all platforms
- [ ] Document in profile header comments

## Testing

```powershell
Describe 'Get-CFAgentContext' {
    It 'Detects GitHub Actions' {
        $env:GITHUB_ACTIONS = 'true'
        $ctx = Get-CFAgentContext -Force
        $ctx.IsCI | Should -BeTrue
        $ctx.CIPlatform | Should -Be 'GitHub Actions'
        Remove-Item env:GITHUB_ACTIONS
    }

    It 'Detects VS Code' {
        $env:TERM_PROGRAM = 'vscode'
        $ctx = Get-CFAgentContext -Force
        $ctx.IsVSCode | Should -BeTrue
        Remove-Item env:TERM_PROGRAM
    }

    It 'Caches results' {
        $first = Get-CFAgentContext
        $second = Get-CFAgentContext
        $first.DetectedAt | Should -Be $second.DetectedAt
    }
}
```

---

*"One function to detect them all, one source of truth to bind them."*
