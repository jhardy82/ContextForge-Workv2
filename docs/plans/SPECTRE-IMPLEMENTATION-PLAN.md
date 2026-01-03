# ContextForge.Spectre Implementation Plan

**Created**: 2025-11-05
**Authority**: Research findings from PwshSpectreConsole analysis
**Status**: ACTIVE

---

## Executive Summary

This plan consolidates research findings from three autonomous research agents to create a comprehensive implementation strategy for the ContextForge.Spectre module and demo script.

### Research Foundation
- **PwshSpectreConsole Best Practices**: Official patterns, CI configuration, UTF-8 requirements
- **Parameter Set Error Diagnostics**: Root cause analysis, file-level issues, remediation strategies
- **Terminal UI Testing**: Dual-mode testing, ANSI handling, CI/CD integration

---

## Phase 1: Diagnostic Resolution (Priority: CRITICAL)

### Objective
Resolve the "Parameter set cannot be resolved" error in `scripts/Invoke-ContextForgeSpectreDemo.ps1`

### Root Cause Analysis

Based on research findings, the error occurring **before script execution** indicates file-level issues. Top suspects:

1. **BOM (Byte Order Mark)** - 25% likelihood
   - Status: RULED OUT ✅ (Format-Hex shows no BOM: starts with `23` = `#`)

2. **Hidden Characters** - 10% likelihood
   - Zero-width spaces (U+200B, U+200C, U+200D)
   - Zero-width joiners/non-joiners
   - Soft hyphens (U+00AD)
   - **ACTION REQUIRED**: Full character scan needed

3. **Line Ending Issues** - 2% likelihood
   - Mixed CRLF/LF causing parser confusion
   - **ACTION REQUIRED**: Analyze with `Get-Content -Raw | % { $_ -replace '\r\n', '...' }`

4. **Encoding Corruption** - 60% likelihood (HIGHEST)
   - UTF-8 → Windows-1252 → UTF-8 round-trip corruption
   - En-dash (U+2013) mistaken for hyphen-minus (U+002D)
   - Smart quotes, curly apostrophes from web copy/paste
   - **ACTION REQUIRED**: Deep character-by-character comparison with working script

### Diagnostic Checklist

```powershell
# Step 1: Run comprehensive file health check
. tests\helpers\Test-ScriptFileHealth.ps1
Test-ScriptFileHealth -Path scripts\Invoke-ContextForgeSpectreDemo.ps1 -Verbose

# Step 2: Compare character-by-character with working test-params.ps1
$demo = Get-Content scripts\Invoke-ContextForgeSpectreDemo.ps1 -Raw
$test = Get-Content scripts\test-params.ps1 -Raw

# Extract param blocks
$demoParam = ($demo -match '(?s)\[CmdletBinding\(\)\]param\(.*?\n\)')[0]
$testParam = ($test -match '(?s)\[CmdletBinding\(\)\]param\(.*?\n\)')[0]

# Byte-level comparison
$demoBytes = [System.Text.Encoding]::UTF8.GetBytes($demoParam)
$testBytes = [System.Text.Encoding]::UTF8.GetBytes($testParam)

# Find first difference
for ($i = 0; $i -lt [Math]::Min($demoBytes.Length, $testBytes.Length); $i++) {
    if ($demoBytes[$i] -ne $testBytes[$i]) {
        Write-Host "First diff at byte $i"
        Write-Host "Demo: 0x$($demoBytes[$i].ToString('X2')) ($([char]$demoBytes[$i]))"
        Write-Host "Test: 0x$($testBytes[$i].ToString('X2')) ($([char]$testBytes[$i]))"
        break
    }
}

# Step 3: Create fresh copy with explicit UTF-8 encoding
$content = Get-Content scripts\Invoke-ContextForgeSpectreDemo.ps1 -Raw
$content | Out-File -FilePath scripts\Invoke-ContextForgeSpectreDemo-CLEAN.ps1 -Encoding utf8NoBOM

# Step 4: Test clean copy
pwsh -NoProfile -File scripts\Invoke-ContextForgeSpectreDemo-CLEAN.ps1 -NoSpectre
```

### Remediation Strategy

**If hidden characters found**:
```powershell
# Use provided cleaning function
. tests\helpers\TerminalUI.TestHelpers.psm1
$cleaned = Remove-HiddenCharacters -FilePath scripts\Invoke-ContextForgeSpectreDemo.ps1
$cleaned | Out-File -FilePath scripts\Invoke-ContextForgeSpectreDemo.ps1 -Encoding utf8NoBOM -Force
```

**If encoding corruption found**:
```powershell
# Manual repair of common patterns
$content = Get-Content scripts\Invoke-ContextForgeSpectreDemo.ps1 -Raw
$content = $content -replace [char]0x2013, '-'  # En-dash → hyphen
$content = $content -replace [char]0x2014, '-'  # Em-dash → hyphen
$content = $content -replace [char]0x2018, "'"  # Left single quote
$content = $content -replace [char]0x2019, "'"  # Right single quote
$content = $content -replace [char]0x201C, '"'  # Left double quote
$content = $content -replace [char]0x201D, '"'  # Right double quote
$content | Out-File -FilePath scripts\Invoke-ContextForgeSpectreDemo.ps1 -Encoding utf8NoBOM -Force
```

**Success Criteria**:
- ✅ Demo script runs without parameter errors
- ✅ Root cause documented in AAR
- ✅ Prevention measures added to `.editorconfig` and pre-commit hooks

---

## Phase 2: Module Enhancement (Priority: HIGH)

### Objective
Align ContextForge.Spectre with PwshSpectreConsole best practices and research findings

### Implementation Tasks

#### 2.1 UTF-8 Enforcement Upgrade

**Current State**: `Set-CfUtf8Console` sets encoding but lacks validation
**Target State**: Comprehensive UTF-8 setup matching official guidance

```powershell
function Set-CfUtf8Console {
    [CmdletBinding()]
    param(
        [switch]$ForceAnsi,
        [switch]$Quiet,
        [switch]$SkipWarnings  # NEW: Suppress warnings in CI
    )

    # Official PwshSpectreConsole pattern (FIRST LINE in $PROFILE)
    $OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding =
        New-Object System.Text.UTF8Encoding

    # Add validation
    $isUtf8 = ($OutputEncoding.EncodingName -eq 'Unicode (UTF-8)') -and
              ([console]::InputEncoding.EncodingName -eq 'Unicode (UTF-8)') -and
              ([console]::OutputEncoding.EncodingName -eq 'Unicode (UTF-8)')

    if (-not $isUtf8 -and -not $SkipWarnings) {
        Write-Warning "UTF-8 encoding not fully applied. Check `$PROFILE configuration."
    }

    # Existing ANSI logic...
    if ($ForceAnsi -or $env:WT_SESSION -or $env:TERM_PROGRAM) {
        # Enable ANSI sequences
    }

    if (-not $Quiet) {
        $msg = if ($isUtf8) { "UTF-8 encoding active ✓" } else { "UTF-8 partial" }
        Write-Information $msg -InformationAction Continue
    }
}
```

**Files**: `modules/ContextForge.Spectre/Public/Set-CfUtf8Console.ps1`

#### 2.2 CI Environment Detection

**NEW**: Add comprehensive CI detection following research findings

```powershell
function Test-CIEnvironment {
    [CmdletBinding()]
    [OutputType([bool])]
    param()

    # Multi-indicator CI detection (research-backed)
    $indicators = @(
        $env:CI -eq 'true'
        $env:GITHUB_ACTIONS -eq 'true'
        $env:TF_BUILD -eq 'True'  # Azure DevOps
        $env:GITLAB_CI -eq 'true'
        $env:JENKINS_URL
        $env:APPVEYOR -eq 'True'
        (-not [Environment]::UserInteractive)
        ($Host.Name -eq 'ServerRemoteHost')  # Non-interactive PowerShell
    )

    return ($indicators -contains $true)
}
```

**Integration**: Use in all wrapper functions for fallback behavior

```powershell
function Write-ContextForgePanel {
    param(...)

    if (Test-CIEnvironment) {
        # Fallback to plain text
        Write-Host "=== $Title ===" -ForegroundColor Cyan
        $Message | Out-String | Write-Host
    } else {
        # Spectre rendering
        Format-SpectrePanel @spectreParams | Out-SpectreHost
    }
}
```

**Files**:
- NEW: `modules/ContextForge.Spectre/Private/Test-CIEnvironment.ps1`
- UPDATE: All `Public/*.ps1` wrappers

#### 2.3 Splatting Pattern Adoption

**Current**: Mixed direct parameter and splatting
**Target**: Consistent splatting for all Spectre calls (research best practice)

```powershell
# BEFORE
Format-SpectrePanel $data $header $border $color

# AFTER (research-backed pattern)
$panelParams = @{
    Data   = $data
    Header = $header
    Border = $border
    Color  = $color
}
Format-SpectrePanel @panelParams
```

**Files**: All `Public/*.ps1` wrappers

#### 2.4 Markup Escaping

**NEW**: Add safe text handling for user input

```powershell
function ConvertTo-SafeSpectreMarkup {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [string]$Text,

        [switch]$AllowMarkup  # Explicit opt-in for markup
    )

    process {
        if ($AllowMarkup) {
            return $Text
        }

        # Escape markup characters (research finding: critical for user input)
        $escaped = $Text -replace '\[', '[['
        $escaped = $escaped -replace '\]', ']]'
        return $escaped
    }
}
```

**Integration**: Add `-AllowMarkup` switch to all wrappers, default to escaped

**Files**:
- NEW: `modules/ContextForge.Spectre/Private/ConvertTo-SafeSpectreMarkup.ps1`
- UPDATE: All `Public/*.ps1` wrappers

#### 2.5 Error Handling Enhancement

**Pattern**: Research-backed try/catch with Spectre exception formatting

```powershell
function Write-ContextForgePanel {
    [CmdletBinding()]
    param(...)

    try {
        $safeMessage = if ($AllowMarkup) { $Message }
                       else { $Message | ConvertTo-SafeSpectreMarkup }

        $panelParams = @{
            Data = $safeMessage
            # ... other params
        }

        Format-SpectrePanel @panelParams | Out-SpectreHost
    }
    catch {
        if (Test-CIEnvironment) {
            # Plain text fallback
            Write-Warning "Panel rendering failed: $_"
            Write-Host "=== $Title ===" -ForegroundColor Cyan
            $Message | Write-Host
        } else {
            # Spectre exception formatting
            $_ | Format-SpectreException -ExceptionFormat ShortenEverything | Out-SpectreHost
            throw
        }
    }
}
```

**Files**: All `Public/*.ps1` wrappers

---

## Phase 3: Demo Script Reconstruction (Priority: HIGH)

### Objective
Rebuild demo script following research-backed patterns

### Implementation Strategy

**Approach**: Start with minimal working script (test-params.ps1) and add functionality incrementally

```powershell
#Requires -Version 7.0

<#
.SYNOPSIS
  ContextForge Spectre demo with UTF-8 artifacts and CI safety.

.NOTES
  HostPolicy: ModernPS7
  Research Authority: PwshSpectreConsole best practices analysis 2025-11-05
#>

[CmdletBinding()]
param(
    [string]$ArtifactsPath = (Join-Path (Get-Location) "artifacts/spectre-demo"),
    [switch]$CI,
    [switch]$NoPause,
    [int]$DurationSeconds = 3
)

$ErrorActionPreference = 'Stop'

# Phase 1: UTF-8 initialization (FIRST - research critical finding)
$OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding =
    New-Object System.Text.UTF8Encoding

# Phase 2: Module import with error handling
try {
    Import-Module "$PSScriptRoot\..\modules\ContextForge.Spectre" -Force -ErrorAction Stop
} catch {
    Write-Error "Failed to import ContextForge.Spectre: $_"
    exit 1
}

# Phase 3: Directory setup
if (-not (Test-Path $ArtifactsPath)) {
    New-Item -ItemType Directory -Path $ArtifactsPath -Force | Out-Null
}

$jsonlPath = Join-Path $ArtifactsPath "demo-$(Get-Date -Format 'yyyyMMdd-HHmmss').jsonl"
$transcriptPath = Join-Path $ArtifactsPath "demo-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"

# Phase 4: JSONL helper
function Write-JsonlRecord {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$EventType,
        [hashtable]$Data = @{}
    )

    $record = @{
        timestamp  = (Get-Date -Format 'o')
        event_type = $EventType
    } + $Data

    $record | ConvertTo-Json -Compress |
        Add-Content -Path $Path -Encoding utf8
}

# Phase 5: Startup event (before ANY Spectre calls)
Write-JsonlRecord -Path $jsonlPath -EventType "demo_start" -Data @{
    ci_mode = $CI.IsPresent
    artifacts_path = $ArtifactsPath
}

# Phase 6: UTF-8 console setup (research-backed: call early)
Set-CfUtf8Console -Quiet:$CI

# Phase 7: Demo execution (wrapped in transcript capture)
& {
    Write-Output "=== ContextForge Spectre Demo Start: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==="

    # Demo step 1: Panel
    try {
        Write-ContextForgePanel -Title "Welcome" -Content "ContextForge.Spectre Demo" -Type Info
        Write-JsonlRecord -Path $jsonlPath -EventType "panel_rendered" -Data @{ step = 1 }
    } catch {
        Write-JsonlRecord -Path $jsonlPath -EventType "panel_error" -Data @{ error = $_.ToString() }
        throw
    }

    # Demo step 2: Progress (research pattern: use splatting)
    try {
        $progressParams = @{
            Title = "Processing Demo Steps"
            Total = 100
        }
        Write-ContextForgeProgress @progressParams
        Write-JsonlRecord -Path $jsonlPath -EventType "progress_rendered" -Data @{ step = 2 }
    } catch {
        Write-JsonlRecord -Path $jsonlPath -EventType "progress_error" -Data @{ error = $_.ToString() }
        throw
    }

    # Demo step 3: Table
    try {
        $tableData = @(
            [PSCustomObject]@{ Step = 1; Status = "✓"; Duration = "50ms" }
            [PSCustomObject]@{ Step = 2; Status = "✓"; Duration = "75ms" }
            [PSCustomObject]@{ Step = 3; Status = "⏳"; Duration = "pending" }
        )
        Write-ContextForgeTable -Data $tableData -Title "Demo Results"
        Write-JsonlRecord -Path $jsonlPath -EventType "table_rendered" -Data @{ step = 3; rows = 3 }
    } catch {
        Write-JsonlRecord -Path $jsonlPath -EventType "table_error" -Data @{ error = $_.ToString() }
        throw
    }

    Write-Output "=== Demo End: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==="
} 2>&1 | Tee-Object -FilePath $transcriptPath -Encoding utf8

# Phase 8: Compute hashes (governance requirement)
$jsonlHash = (Get-FileHash -Path $jsonlPath -Algorithm SHA256).Hash
$transcriptHash = (Get-FileHash -Path $transcriptPath -Algorithm SHA256).Hash

Write-JsonlRecord -Path $jsonlPath -EventType "demo_complete" -Data @{
    jsonl_hash = $jsonlHash
    transcript_hash = $transcriptHash
}

# Phase 9: Summary output
Write-Host "`n=== Demo Summary ===" -ForegroundColor Green
Write-Host "Artifacts: $ArtifactsPath" -ForegroundColor Cyan
Write-Host "  JSONL:      $(Split-Path $jsonlPath -Leaf) (SHA256: $($jsonlHash.Substring(0,16))...)"
Write-Host "  Transcript: $(Split-Path $transcriptPath -Leaf) (SHA256: $($transcriptHash.Substring(0,16))...)"

if (-not $NoPause -and -not $CI) {
    Write-Host "`nPress Enter to exit..." -ForegroundColor Yellow
    Read-Host
}

exit 0
```

**Success Criteria**:
- ✅ Script runs green with `-CI -NoPause`
- ✅ Artifacts created with UTF-8 encoding
- ✅ SHA-256 hashes computed and logged
- ✅ Interactive mode shows Spectre UI
- ✅ CI mode uses plain text fallback

**Files**: `scripts/Invoke-ContextForgeSpectreDemo.ps1`

---

## Phase 4: Testing Framework (Priority: MEDIUM)

### Objective
Implement dual-mode testing strategy from research findings

### Test Structure

```
tests/
├── ContextForge.Spectre.Helpers.Tests.ps1        # Existing (keep)
├── ContextForge.Spectre.DemoScript.Tests.ps1     # NEW
├── ContextForge.Spectre.Integration.Tests.ps1    # NEW
└── helpers/
    ├── TerminalUI.TestHelpers.psm1               # From research
    └── Test-ScriptFileHealth.ps1                 # From research
```

### Demo Script Tests

```powershell
Describe "Invoke-ContextForgeSpectreDemo" {
    BeforeAll {
        $demoScript = "$PSScriptRoot\..\scripts\Invoke-ContextForgeSpectreDemo.ps1"
        $testArtifactsPath = Join-Path $TestDrive "demo-artifacts"
    }

    Context "CI Mode Execution" {
        It "runs successfully in CI mode" {
            $result = & $demoScript -CI -NoPause -ArtifactsPath $testArtifactsPath
            $LASTEXITCODE | Should -Be 0
        }

        It "creates JSONL artifact" {
            $jsonlFiles = Get-ChildItem -Path $testArtifactsPath -Filter "*.jsonl"
            $jsonlFiles | Should -HaveCount 1
        }

        It "creates transcript artifact" {
            $txtFiles = Get-ChildItem -Path $testArtifactsPath -Filter "*.txt"
            $txtFiles | Should -HaveCount 1
        }

        It "logs demo_start event" {
            $jsonl = Get-Content (Get-ChildItem $testArtifactsPath -Filter "*.jsonl")[0].FullName
            $events = $jsonl | ForEach-Object { $_ | ConvertFrom-Json }
            $events.event_type | Should -Contain "demo_start"
        }

        It "logs demo_complete with hashes" {
            $jsonl = Get-Content (Get-ChildItem $testArtifactsPath -Filter "*.jsonl")[0].FullName
            $events = $jsonl | ForEach-Object { $_ | ConvertFrom-Json }
            $complete = $events | Where-Object { $_.event_type -eq 'demo_complete' }
            $complete.jsonl_hash | Should -Not -BeNullOrEmpty
            $complete.transcript_hash | Should -Not -BeNullOrEmpty
        }
    }

    Context "File Encoding Validation" {
        It "creates UTF-8 JSONL files" {
            $jsonlPath = (Get-ChildItem $testArtifactsPath -Filter "*.jsonl")[0].FullName
            $bytes = Get-Content $jsonlPath -AsByteStream -First 3
            # UTF-8 without BOM: no EF BB BF prefix
            $bytes[0] | Should -Not -Be 0xEF
        }

        It "creates UTF-8 transcript files" {
            $txtPath = (Get-ChildItem $testArtifactsPath -Filter "*.txt")[0].FullName
            $bytes = Get-Content $txtPath -AsByteStream -First 3
            $bytes[0] | Should -Not -Be 0xEF
        }
    }
}
```

**Files**: `tests/ContextForge.Spectre.DemoScript.Tests.ps1`

---

## Phase 5: CI/CD Integration (Priority: MEDIUM)

### Objective
Create smoke test workflow following research patterns

### GitHub Actions Workflow

```yaml
name: Spectre Demo Smoke Test

on:
  push:
    branches: [main, master, develop]
    paths:
      - 'modules/ContextForge.Spectre/**'
      - 'scripts/Invoke-ContextForgeSpectreDemo.ps1'
  pull_request:
    paths:
      - 'modules/ContextForge.Spectre/**'
      - 'scripts/Invoke-ContextForgeSpectreDemo.ps1'
  workflow_dispatch:

env:
  CI: true

jobs:
  smoke-test:
    name: Spectre Demo Validation
    runs-on: windows-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install PwshSpectreConsole
        shell: pwsh
        run: |
          Install-Module -Name PwshSpectreConsole -Scope CurrentUser -Force -SkipPublisherCheck
          Import-Module PwshSpectreConsole -Force

      - name: Run Spectre demo (CI mode)
        shell: pwsh
        run: |
          $result = & ./scripts/Invoke-ContextForgeSpectreDemo.ps1 -CI -NoPause -ArtifactsPath ./artifacts/ci-demo
          if ($LASTEXITCODE -ne 0) {
            Write-Error "Demo script failed with exit code $LASTEXITCODE"
            exit 1
          }

      - name: Validate artifacts created
        shell: pwsh
        run: |
          $jsonl = Get-ChildItem ./artifacts/ci-demo -Filter "*.jsonl" -ErrorAction Stop
          $txt = Get-ChildItem ./artifacts/ci-demo -Filter "*.txt" -ErrorAction Stop

          if (-not $jsonl -or -not $txt) {
            Write-Error "Missing expected artifacts"
            exit 1
          }

          Write-Host "✓ Artifacts validated: $($jsonl.Name), $($txt.Name)"

      - name: Verify UTF-8 encoding
        shell: pwsh
        run: |
          $jsonlPath = (Get-ChildItem ./artifacts/ci-demo -Filter "*.jsonl")[0].FullName
          $bytes = Get-Content $jsonlPath -AsByteStream -First 3

          if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
            Write-Error "JSONL has UTF-8 BOM (should be UTF-8 without BOM)"
            exit 1
          }

          Write-Host "✓ UTF-8 encoding validated (no BOM)"

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: spectre-demo-artifacts
          path: ./artifacts/ci-demo/
          retention-days: 7
```

**Files**: `.github/workflows/spectre-demo-smoke.yml`

---

## Phase 6: Documentation (Priority: LOW)

### Objective
Document usage, patterns, and governance alignment

### Documentation Tasks

1. **Module README** (`modules/ContextForge.Spectre/README.md`)
   - Add "Spectre Demo" section
   - Document parameters and usage
   - Explain JSONL event structure
   - Provide examples (local, CI, artifact inspection)

2. **Governance Documentation**
   - Map to `terminal-output.instructions.md` requirements
   - Document 9-component flow implementation
   - Create compliance checklist

3. **Research Archive**
   - Store research findings in `docs/research/`
   - Link from module docs for future reference

---

## Success Metrics

### Phase 1 (Diagnostic)
- [ ] Root cause identified and documented
- [ ] Demo script runs without parameter errors
- [ ] Prevention measures in place

### Phase 2 (Module Enhancement)
- [ ] UTF-8 enforcement upgraded to official pattern
- [ ] CI detection implemented
- [ ] Splatting pattern adopted
- [ ] Markup escaping added
- [ ] Error handling enhanced

### Phase 3 (Demo Rebuild)
- [ ] Demo script runs green (exit 0)
- [ ] Artifacts created with correct encoding
- [ ] SHA-256 hashes computed
- [ ] Interactive mode shows Spectre UI
- [ ] CI mode uses plain fallback

### Phase 4 (Testing)
- [ ] Demo script tests passing (5+ tests)
- [ ] Encoding validation tests passing
- [ ] Integration tests passing

### Phase 5 (CI/CD)
- [ ] GitHub Actions workflow created
- [ ] Smoke test passes on push
- [ ] Artifacts uploaded successfully

### Phase 6 (Documentation)
- [ ] README updated
- [ ] Governance alignment documented
- [ ] Research archived

---

## Timeline Estimate

- **Phase 1**: 1-2 hours (diagnostic + fix)
- **Phase 2**: 3-4 hours (module enhancements)
- **Phase 3**: 2-3 hours (demo rebuild)
- **Phase 4**: 2-3 hours (testing framework)
- **Phase 5**: 1 hour (CI/CD setup)
- **Phase 6**: 1-2 hours (documentation)

**Total**: 10-15 hours over 2-3 development sessions

---

## Dependencies

- PwshSpectreConsole v2.3.0+ installed
- PowerShell 7.0+ runtime
- Pester 5.7+ for testing
- Git for encoding control (.gitattributes)

---

## Risk Mitigation

### Risk: Hidden characters persist after cleaning
**Mitigation**: Manual byte-level inspection and surgical replacement

### Risk: Demo script complexity causes maintenance burden
**Mitigation**: Keep demo minimal; complex scenarios in separate examples

### Risk: CI environment variations break tests
**Mitigation**: Multi-indicator CI detection; plain text fallback

### Risk: UTF-8 encoding reverts in future edits
**Mitigation**: Pre-commit hooks, .editorconfig, CI validation

---

## References

- Research: `docs/research/PwshSpectreConsole-Best-Practices.md`
- Research: `docs/research/PowerShell-Parameter-Set-Error-Diagnostic-Guide.md`
- Research: `docs/research/TESTING-TERMINAL-UI-STRATEGY.md`
- Authority: `.github/instructions/terminal-output.instructions.md`
- Authority: `.github/instructions/terminal-unicode-configuration.instructions.md`
