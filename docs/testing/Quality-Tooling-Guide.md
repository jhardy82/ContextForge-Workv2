# Quality Tooling Guide - P008 Implementation

**Agent:** SCCM-InfraEval-Agent
**Date:** 2025-01-07
**Version:** 1.0.0

---

## 🎯 Overview

This guide documents the P008 Quality Tooling Optimization implementation that eliminates Pester version conflicts and enforces zero PSScriptAnalyzer warnings as hard quality gates for enterprise PowerShell development.

## 🔧 Architecture

The P008 framework provides:

- **Deterministic Pester 5.7.x loading** - Never loads 3.x versions
- **Zero-warnings PSScriptAnalyzer policy** - Hard quality gate for enterprise compliance
- **Console-first approach** - No dependency on VS Code Pester extension
- **Comprehensive artifacts** - CI/CD ready outputs with clear exit codes
- **Idempotent bootstrap** - Consistent results across environments

## 📋 Prerequisites

### Required Environment

- **Windows PowerShell 5.1** (no PowerShell Core required)
- **PSScriptAnalyzer ≥ 1.24.0**
- **Pester ≥ 5.7.0** (will be enforced during bootstrap)

### Installation Commands

```powershell
# Install required modules (if not present)
Install-Module PSScriptAnalyzer -Force -Scope CurrentUser
Install-Module Pester -Force -Scope CurrentUser -MinimumVersion 5.7.0
```

## ⚠️ The Pester Version Conflict Problem

### Why VSCode Pester Extension Fails

Microsoft Learn Documentation: [PowerShell Module Versioning](https://learn.microsoft.com/en-us/powershell/scripting/developer/module/understanding-a-windows-powershell-module)

**Root Cause**: Windows systems often have both:

- **Pester 3.4.0** in `C:\Program Files\WindowsPowerShell\Modules` (inbox)
- **Pester 5.7.x** in `$env:USERPROFILE\Documents\WindowsPowerShell\Modules` (user-installed)

**VS Code Issue**: The Pester extension may load the wrong version or fail to initialize when multiple versions are present.

### Module Load Precedence

PowerShell searches `$env:PSModulePath` in order:

1. User modules (`Documents\WindowsPowerShell\Modules`)
2. Program Files modules (`Program Files\WindowsPowerShell\Modules`)
3. System modules (`$PSHOME\Modules`)

However, without explicit version specification, the behavior can be unpredictable.

## 🚀 Quick Start

### 1. One-Click Quality Validation

```powershell
# Run complete quality bootstrap
.\build\Bootstrap-Quality.ps1

# With verbose output
.\build\Bootstrap-Quality.ps1 -Verbose

# With optional Pester 3.4.0 disabling (Admin required)
.\build\Bootstrap-Quality.ps1 -DisablePester3 -Verbose
```

### 2. Individual Quality Operations

```powershell
# PSScriptAnalyzer only
.\build\Invoke-PSSA.ps1

# Pester tests only (with explicit version)
Import-Module Pester -MinimumVersion 5.7.0 -Force
Invoke-Pester .\tests -Output Detailed

# Environment validation
Invoke-Pester .\tests\Quality.Environment.Tests.ps1 -Output Detailed
```

### 3. VS Code Integration

Use **Terminal → Run Task** and select:

- **Quality: Full Bootstrap** - Complete validation
- **Quality: Static Analysis** - PSScriptAnalyzer only
- **Quality: Tests (Pester 5.7.x)** - Tests with explicit version
- **Quality: Environment Check** - Validate setup

## 🔍 Understanding Exit Codes

| Code | Meaning | Action Required |
|------|---------|-----------------|
| 0 | ✅ Success | No action needed |
| 2 | ⚠️ PSScriptAnalyzer warnings | Review and fix findings |
| 3 | ❌ Pester tests failed | Fix failing tests |
| 4 | ❌ Wrong Pester version | Check Pester installation |
| 5 | ❌ Unsupported PowerShell | Use Windows PowerShell 5.1 |
| 6 | ❌ PSScriptAnalyzer unavailable | Install PSScriptAnalyzer |
| 7 | ❌ General bootstrap error | Check logs and environment |

## 🛠️ Resolving Pester Conflicts

### Console-First Approach (Recommended)

**Always use explicit module imports:**

```powershell
# Force load correct Pester version
Import-Module Pester -MinimumVersion 5.7.0 -Force

# Verify loaded version
$pesterModule = Get-Module Pester
Write-Host "Loaded Pester v$($pesterModule.Version) from $($pesterModule.ModuleBase)"

# Run tests
Invoke-Pester .\tests -Output Detailed
```

### Optional: Disable Inbox Pester 3.4.0

**⚠️ Administrative Action Required**

If you have Administrator privileges and want to permanently resolve conflicts:

```powershell
# Check current Pester versions
Get-Module -ListAvailable Pester | Format-Table Version, ModuleBase

# Run bootstrap with disable option (prompts for confirmation)
.\build\Bootstrap-Quality.ps1 -DisablePester3 -Verbose
```

**What this does:**

1. Takes ownership of `C:\Program Files\WindowsPowerShell\Modules\Pester`
2. Renames folder to `_3.4.0.disabled`
3. Requires user confirmation before making changes

**Rollback instructions:**

```powershell
# To re-enable inbox Pester 3.4.0 (if needed)
$disabledPath = "C:\Program Files\WindowsPowerShell\Modules\_3.4.0.disabled"
$originalPath = "C:\Program Files\WindowsPowerShell\Modules\Pester"

if (Test-Path $disabledPath) {
    Rename-Item -Path $disabledPath -NewName "Pester"
    Write-Host "Inbox Pester 3.4.0 restored"
}
```

### VS Code Pester Extension Issues

**Why the extension fails:**

- Multiple Pester versions confuse initialization
- Extension may load wrong version internally
- Test discovery fails with version conflicts

**Our solution:**

- Bypass VS Code extension entirely
- Use direct PowerShell execution via tasks
- Explicit version control in all operations

## 📊 Enterprise PSScriptAnalyzer Standards

### Zero Warnings Policy

**Enterprise Requirement**: All PowerShell code must pass PSScriptAnalyzer with zero warnings.

**Configuration**: `build/PSSA.Settings.psd1`

**Key Rules Enforced:**

- **Security**: No plain-text passwords, proper credential handling
- **Style**: Consistent formatting, approved verbs, help documentation
- **Quality**: No unused variables, proper error handling
- **Compatibility**: PowerShell 5.1 syntax validation

### Rule Categories

#### Critical Security Rules

- `PSAvoidUsingPlainTextForPassword`
- `PSUsePSCredentialType`
- `PSAvoidUsingConvertToSecureStringWithPlainText`
- `PSAvoidUsingComputerNameHardcoded`

#### Code Quality Rules

- `PSUseApprovedVerbs`
- `PSUseSingularNouns`
- `PSProvideCommentHelp`
- `PSAvoidGlobalVars`
- `PSUseDeclaredVarsMoreThanAssignments`

#### Style Consistency Rules

- `PSUseConsistentWhitespace`
- `PSUseConsistentIndentation`
- `PSPlaceOpenBrace`
- `PSAlignAssignmentStatement`
- `PSUseCorrectCasing`

## 🏗️ CI/CD Integration

### GitHub Actions Example

```yaml
# samples/ci/github-actions-windows-ps5.yml
name: Quality Validation
on: [push, pull_request]

jobs:
  quality:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v3

    - name: Install PSScriptAnalyzer
      shell: powershell
      run: Install-Module PSScriptAnalyzer -Force -Scope CurrentUser

    - name: Install Pester 5.7.x
      shell: powershell
      run: Install-Module Pester -Force -Scope CurrentUser -MinimumVersion 5.7.0

    - name: Run Quality Bootstrap
      shell: powershell
      run: .\build\Bootstrap-Quality.ps1

    - name: Upload Artifacts
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: quality-reports
        path: build/artifacts/
```

### Azure DevOps Pipeline

```yaml
# Azure DevOps YAML Pipeline
trigger:
- main

pool:
  vmImage: 'windows-latest'

steps:
- powershell: |
    Install-Module PSScriptAnalyzer -Force -Scope CurrentUser
    Install-Module Pester -Force -Scope CurrentUser -MinimumVersion 5.7.0
  displayName: 'Install Quality Modules'

- powershell: .\build\Bootstrap-Quality.ps1
  displayName: 'Run Quality Validation'

- task: PublishTestResults@2
  inputs:
    testResultsFormat: 'NUnit'
    testResultsFiles: 'build/artifacts/Pester-Results-NUnit.xml'
  displayName: 'Publish Test Results'

- task: PublishBuildArtifacts@1
  inputs:
    pathToPublish: 'build/artifacts'
    artifactName: 'quality-reports'
  displayName: 'Publish Quality Artifacts'
```

## 📁 Generated Artifacts

The quality framework generates comprehensive artifacts in `build/artifacts/`:

### Core Reports

- **`Quality-Summary.json`** - Complete validation summary with metrics
- **`Quality-Audit.jsonl`** - Structured audit log for compliance
- **`PSSA-Report.json`** - Detailed PSScriptAnalyzer findings
- **`PSSA-Findings.txt`** - Human-readable findings report
- **`Pester-Results-NUnit.xml`** - Test results in NUnit format
- **`Pester-Console.txt`** - Test execution console output

### Artifact Structure Example

```json
{
  "timestamp": "2025-01-07T18:30:00.000Z",
  "status": "SUCCESS",
  "exitCode": 0,
  "results": {
    "PSScriptAnalyzer": {
      "Status": "Completed",
      "Warnings": 0,
      "Errors": 0,
      "Files": 25
    },
    "Pester": {
      "Status": "Completed",
      "TestsPassed": 42,
      "TestsFailed": 0,
      "Duration": "00:00:15.234"
    }
  }
}
```

## 🎛️ PowerShell Profile Integration

### Optional Profile Enhancement

Add to `$PROFILE.CurrentUserAllHosts` for automatic Pester 5.7.x loading:

```powershell
# P008 Quality Tooling - Auto-load Pester 5.7.x
if (Get-Module -ListAvailable Pester) {
    Import-Module Pester -MinimumVersion 5.7.0 -Force -Global
    Write-Host "Loaded Pester v$((Get-Module Pester).Version)" -ForegroundColor Green
}
```

## 🔧 Troubleshooting

### Common Issues

#### Issue: "Multiple Pester versions found"

**Solution**: Use explicit version imports

```powershell
Import-Module Pester -MinimumVersion 5.7.0 -Force
```

#### Issue: "PSScriptAnalyzer not found"

**Solution**: Install the module

```powershell
Install-Module PSScriptAnalyzer -Force -Scope CurrentUser
```

#### Issue: "Access denied when disabling Pester 3.4.0"

**Solution**: Run PowerShell as Administrator

```powershell
# Right-click PowerShell → Run as Administrator
.\build\Bootstrap-Quality.ps1 -DisablePester3
```

#### Issue: "VS Code Pester extension not working"

**Solution**: Use console-first approach

- Don't rely on VS Code Pester extension
- Use VS Code tasks instead: **Terminal → Run Task → Quality: Tests (Pester 5.7.x)**

### Diagnostic Commands

```powershell
# Check PowerShell version
$PSVersionTable

# List all Pester versions
Get-Module -ListAvailable Pester | Format-Table Version, ModuleBase

# Check currently loaded Pester
Get-Module Pester | Format-List Version, ModuleBase

# Test PSScriptAnalyzer
Get-Command Invoke-ScriptAnalyzer

# Verify module paths
$env:PSModulePath -split ';'
```

## 📚 Microsoft Learn References

### PowerShell Module Management

- [About PowerShell Modules](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_modules)
- [Module Installation Path](https://learn.microsoft.com/en-us/powershell/scripting/developer/module/modifying-the-psmodulepath-installation-path)
- [Import-Module Documentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/import-module)

### PSScriptAnalyzer

- [PSScriptAnalyzer Overview](https://learn.microsoft.com/en-us/powershell/utility-modules/psscriptanalyzer/overview)
- [Using PSScriptAnalyzer](https://learn.microsoft.com/en-us/powershell/utility-modules/psscriptanalyzer/using-scriptanalyzer)
- [PSScriptAnalyzer Rules](https://learn.microsoft.com/en-us/powershell/utility-modules/psscriptanalyzer/rules-recommendations)

### Pester Testing

- [Pester GitHub Repository](https://github.com/pester/Pester)
- [Pester v5 Documentation](https://pester.dev/docs/quick-start)

### PowerShell Best Practices

- [PowerShell Practice and Style Guide](https://learn.microsoft.com/en-us/powershell/scripting/developer/cmdlet/cmdlet-development-guidelines)
- [PowerShell Security Best Practices](https://learn.microsoft.com/en-us/powershell/scripting/learn/security/powershell-security-best-practices)

---

## 🎯 Quick Reference Card

### Essential Commands

```powershell
# Complete quality validation
.\build\Bootstrap-Quality.ps1

# Individual components
.\build\Invoke-PSSA.ps1                           # Static analysis
Import-Module Pester -Min 5.7.0 -Force; Invoke-Pester  # Tests

# VS Code tasks
Ctrl+Shift+P → "Tasks: Run Task" → "Quality: Full Bootstrap"

# Check results
Get-Content .\build\artifacts\Quality-Summary.json | ConvertFrom-Json
```

### File Locations

- **Bootstrap**: `build/Bootstrap-Quality.ps1`
- **Settings**: `build/PSSA.Settings.psd1`
- **Tests**: `tests/Quality.Environment.Tests.ps1`
- **Results**: `build/artifacts/`
- **Tasks**: `.vscode/tasks.json`

### Exit Codes Quick Ref

- **0** = Success | **2** = PSSA warnings | **3** = Test failures | **4** = Wrong Pester | **5** = Wrong PS version

---

**Remember**: Console-first approach eliminates VS Code extension dependencies and provides reliable, deterministic results across all corporate environments.
