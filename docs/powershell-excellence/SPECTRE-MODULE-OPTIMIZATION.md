# Spectre Module Optimization Strategy

**Version**: 1.0.0
**Last Updated**: 2025-12-29
**Status**: Ready for Implementation

---

## Executive Summary

The `ContextForge.Spectre` module provides rich console output but incurs 80-200ms load penalty. This document outlines a proxy module pattern to achieve zero-cost import with on-demand loading.

## Current State Analysis

### Module Structure

```
modules/ContextForge.Spectre/
├── ContextForge.Spectre.psd1    # Module manifest
├── ContextForge.Spectre.psm1    # Root module
└── Public/                       # 22 exported functions
    ├── Write-SpectreHost.ps1
    ├── Write-SpectreTable.ps1
    ├── Show-SpectreProgress.ps1
    └── ... (19 more)
```

### Performance Bottlenecks

| Issue | Latency | Cause |
|-------|---------|-------|
| `#Requires -Modules PwshSpectreConsole` | 80-200ms | Forces eager module load |
| Type instantiation at load | 20-50ms | 15+ `[Spectre.Console.Color]` accesses |
| Function dot-sourcing | 10-20ms | 22 files parsed at import |

**Total overhead**: 110-270ms per import

## Root Cause: #Requires Statement

```powershell
# In ContextForge.Spectre.psm1 (line 1)
#Requires -Modules PwshSpectreConsole  # <-- This blocks!
```

PowerShell evaluates `#Requires` **before** any code runs, forcing:
1. Full `PwshSpectreConsole` module load
2. All Spectre.Console .NET assemblies loaded
3. Type accelerators registered

## Optimization Strategy: Proxy Module Pattern

### Architecture

```
┌─────────────────────────────────────┐
│  ContextForge.Spectre (Proxy)       │ ← Fast import (5ms)
│  - Stub functions                   │
│  - Deferred loading                 │
└──────────────┬──────────────────────┘
               │ First call triggers
               ▼
┌─────────────────────────────────────┐
│  ContextForge.Spectre.Core          │ ← Real implementation
│  - Full Spectre integration         │
│  - Rich console output              │
└─────────────────────────────────────┘
```

### Implementation

#### Step 1: Create Proxy Module

**File: `ContextForge.Spectre.psm1` (replacement)**

```powershell
# ContextForge.Spectre - Proxy Module
# Zero-cost import with on-demand loading

$script:CoreLoaded = $false
$script:ColorPalette = $null

function Initialize-SpectreCore {
    [CmdletBinding()]
    param()

    if ($script:CoreLoaded) { return }

    # Now load the real module
    Import-Module PwshSpectreConsole -ErrorAction Stop

    # Load implementation functions
    $privatePath = Join-Path $PSScriptRoot 'Private'
    $publicPath = Join-Path $PSScriptRoot 'Public'

    Get-ChildItem "$privatePath/*.ps1" -ErrorAction SilentlyContinue |
        ForEach-Object { . $_.FullName }
    Get-ChildItem "$publicPath/*.ps1" -ErrorAction SilentlyContinue |
        ForEach-Object { . $_.FullName }

    $script:CoreLoaded = $true
}

# Proxy function template
function Write-SpectreHost {
    [CmdletBinding()]
    param(
        [Parameter(Position = 0, ValueFromPipeline)]
        [string]$Message,
        [string]$Color = 'White'
    )

    process {
        Initialize-SpectreCore
        Write-SpectreHostCore @PSBoundParameters
    }
}

function Write-SpectreTable {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [object[]]$Data,
        [string]$Title
    )

    process {
        Initialize-SpectreCore
        Write-SpectreTableCore @PSBoundParameters
    }
}

# Export only proxy functions
Export-ModuleMember -Function @(
    'Write-SpectreHost'
    'Write-SpectreTable'
    'Show-SpectreProgress'
    # ... other proxies
)
```

#### Step 2: Defer Color Palette

**Before:**
```powershell
# Evaluated at module load
$script:Colors = @{
    Success = [Spectre.Console.Color]::Green
    Warning = [Spectre.Console.Color]::Yellow
    Error   = [Spectre.Console.Color]::Red
}
```

**After:**
```powershell
# Lazy color palette
function Get-CFSpectreColor {
    param([string]$Name)

    if ($null -eq $script:ColorPalette) {
        Initialize-SpectreCore
        $script:ColorPalette = @{
            Success = [Spectre.Console.Color]::Green
            Warning = [Spectre.Console.Color]::Yellow
            Error   = [Spectre.Console.Color]::Red
            Info    = [Spectre.Console.Color]::Blue
            Muted   = [Spectre.Console.Color]::Grey
        }
    }

    return $script:ColorPalette[$Name]
}
```

#### Step 3: Fallback for Non-Spectre Environments

```powershell
function Write-SpectreHostCore {
    [CmdletBinding()]
    param(
        [string]$Message,
        [string]$Color = 'White'
    )

    # Check if Spectre is available
    if (-not (Get-Module PwshSpectreConsole)) {
        # Graceful fallback to standard Write-Host
        $consoleColor = switch ($Color) {
            'Green'  { 'Green' }
            'Yellow' { 'Yellow' }
            'Red'    { 'Red' }
            'Blue'   { 'Cyan' }
            default  { 'White' }
        }
        Write-Host $Message -ForegroundColor $consoleColor
        return
    }

    # Use Spectre
    Write-SpectreHost $Message -Color $Color
}
```

## Module Manifest Update

**File: `ContextForge.Spectre.psd1`**

```powershell
@{
    RootModule        = 'ContextForge.Spectre.psm1'
    ModuleVersion     = '2.0.0'
    GUID              = 'unique-guid-here'
    Author            = 'ContextForge'
    Description       = 'Rich console output with lazy-loaded Spectre.Console'

    # REMOVED: RequiredModules - no longer blocking!
    # RequiredModules = @('PwshSpectreConsole')

    FunctionsToExport = @(
        'Write-SpectreHost'
        'Write-SpectreTable'
        'Show-SpectreProgress'
        'Get-CFSpectreColor'
    )

    PrivateData = @{
        PSData = @{
            Tags = @('Console', 'Rich', 'Spectre', 'LazyLoad')
        }
    }
}
```

## Implementation Checklist

- [ ] Backup existing module files
- [ ] Create proxy `ContextForge.Spectre.psm1`
- [ ] Move implementations to `*Core` functions
- [ ] Update module manifest (remove RequiredModules)
- [ ] Add fallback for non-Spectre environments
- [ ] Test lazy loading with `Measure-Command`
- [ ] Validate all 22 functions work correctly

## Validation

```powershell
# Measure import time (should be <10ms)
Measure-Command { Import-Module ContextForge.Spectre } |
    Select-Object TotalMilliseconds

# Verify lazy load triggers on first use
Remove-Module ContextForge.Spectre, PwshSpectreConsole -ErrorAction SilentlyContinue
Import-Module ContextForge.Spectre
Get-Module PwshSpectreConsole  # Should be empty
Write-SpectreHost "Test"
Get-Module PwshSpectreConsole  # Should now be loaded
```

## Expected Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Import time | 200ms | 5ms | 97% faster |
| First function call | 0ms | 200ms | Deferred |
| No-Spectre fallback | Error | Works | Graceful |

---

*"The fastest code is code that doesn't run until needed."*
