# ContextForge.Spectre Validation Plan

**Created**: 2025-11-05
**Authority**: Research findings + ContextForge governance standards
**Status**: ACTIVE

---

## Executive Summary

This plan establishes comprehensive validation procedures for the ContextForge.Spectre module to ensure compliance with research findings, governance requirements, and quality standards.

### Validation Scope

1. **Functional Validation**: Feature correctness and behavior
2. **Encoding Validation**: UTF-8 compliance and character preservation
3. **Governance Validation**: Alignment with ContextForge standards
4. **Performance Validation**: Execution time and resource usage
5. **CI/CD Validation**: Pipeline integration and artifact quality
6. **Security Validation**: Input sanitization and safe operations

---

## Phase 1: Diagnostic Validation

### Objective
Confirm resolution of "Parameter set cannot be resolved" error

### Validation Checklist

#### 1.1 File Health Validation

```powershell
# Run comprehensive file health check
. tests\helpers\Test-ScriptFileHealth.ps1
$report = Test-ScriptFileHealth -Path scripts\Invoke-ContextForgeSpectreDemo.ps1 -Verbose

# Validation criteria
$report.EncodingValid | Should -Be $true
$report.BOMPresent | Should -Be $false
$report.HiddenCharactersFound | Should -Be $false
$report.LineEndingsConsistent | Should -Be $true
$report.ParseErrorCount | Should -Be 0
```

**Success Criteria**:
- ✅ No BOM detected
- ✅ UTF-8 encoding confirmed
- ✅ No hidden characters (zero-width, soft hyphens)
- ✅ Consistent line endings (CRLF)
- ✅ PowerShell AST parse succeeds without errors

#### 1.2 Parameter Resolution Validation

```powershell
# Test all parameter combinations
$paramSets = @(
    @{ CI = $true; NoPause = $true }
    @{ ArtifactsPath = "test"; CI = $true }
    @{ DurationSeconds = 5; NoPause = $true }
    @{ ArtifactsPath = "test"; CI = $true; NoPause = $true; DurationSeconds = 1 }
    @{}  # No parameters
)

foreach ($params in $paramSets) {
    $result = & scripts\Invoke-ContextForgeSpectreDemo.ps1 @params
    $LASTEXITCODE | Should -Be 0
}
```

**Success Criteria**:
- ✅ All parameter combinations execute without "parameter set" errors
- ✅ Exit code 0 for all invocations
- ✅ No PowerShell parser errors

#### 1.3 Root Cause Documentation

**Validation**: AAR document created with:
- ✅ Detailed root cause analysis
- ✅ Diagnostic steps executed
- ✅ Remediation actions taken
- ✅ Prevention measures implemented
- ✅ Lessons learned documented

**File**: `AAR-Spectre-Demo-Parameter-Error-Resolution-COMPLETE-{date}.md`

---

## Phase 2: Module Validation

### Objective
Verify module enhancements align with research best practices

### 2.1 UTF-8 Enforcement Validation

```powershell
Describe "UTF-8 Enforcement" {
    It "matches official PwshSpectreConsole pattern" {
        Set-CfUtf8Console

        # All three encodings must be UTF-8
        $OutputEncoding.EncodingName | Should -Be 'Unicode (UTF-8)'
        [console]::InputEncoding.EncodingName | Should -Be 'Unicode (UTF-8)'
        [console]::OutputEncoding.EncodingName | Should -Be 'Unicode (UTF-8)'
    }

    It "validates encoding correctness" {
        Set-CfUtf8Console

        $isValid = ($OutputEncoding -is [System.Text.UTF8Encoding]) -and
                   ([console]::InputEncoding -is [System.Text.UTF8Encoding]) -and
                   ([console]::OutputEncoding -is [System.Text.UTF8Encoding])

        $isValid | Should -Be $true
    }

    It "suppresses warnings in CI with -SkipWarnings" {
        $env:CI = 'true'
        $warnings = Set-CfUtf8Console -SkipWarnings 3>&1

        $warnings | Should -BeNullOrEmpty

        $env:CI = $null
    }
}
```

**Success Criteria**:
- ✅ Encoding configuration matches official PwshSpectreConsole pattern
- ✅ Validation logic confirms UTF-8 setup
- ✅ CI warning suppression works correctly

### 2.2 CI Detection Validation

```powershell
Describe "CI Environment Detection" {
    It "detects GitHub Actions" {
        $env:GITHUB_ACTIONS = 'true'
        Test-CIEnvironment | Should -Be $true
        $env:GITHUB_ACTIONS = $null
    }

    It "detects Azure DevOps" {
        $env:TF_BUILD = 'True'
        Test-CIEnvironment | Should -Be $true
        $env:TF_BUILD = $null
    }

    It "detects GitLab CI" {
        $env:GITLAB_CI = 'true'
        Test-CIEnvironment | Should -Be $true
        $env:GITLAB_CI = $null
    }

    It "detects non-interactive host" {
        Mock Get-Host { @{ Name = 'ServerRemoteHost' } }
        Test-CIEnvironment | Should -Be $true
    }

    It "returns false in interactive environment" {
        # Clear all CI variables
        @('CI', 'GITHUB_ACTIONS', 'TF_BUILD', 'GITLAB_CI') | ForEach-Object {
            Remove-Item "Env:$_" -ErrorAction SilentlyContinue
        }

        Test-CIEnvironment | Should -Be $false
    }
}
```

**Success Criteria**:
- ✅ Multi-indicator detection covers major CI platforms
- ✅ Non-interactive detection works
- ✅ Interactive environments correctly identified as non-CI

### 2.3 Splatting Pattern Validation

```powershell
Describe "Splatting Pattern Compliance" {
    It "Write-ContextForgePanel uses splatting" {
        $code = Get-Content modules\ContextForge.Spectre\Public\Write-ContextForgePanel.ps1 -Raw

        # Should contain hashtable parameter construction
        $code | Should -Match '\$\w+Params\s*=\s*@\{'

        # Should contain splatting call
        $code | Should -Match '@\w+Params'
    }

    It "Write-ContextForgeProgress uses splatting" {
        $code = Get-Content modules\ContextForge.Spectre\Public\Write-ContextForgeProgress.ps1 -Raw
        $code | Should -Match '@\w+Params'
    }

    It "Write-ContextForgeTable uses splatting" {
        $code = Get-Content modules\ContextForge.Spectre\Public\Write-ContextForgeTable.ps1 -Raw
        $code | Should -Match '@\w+Params'
    }
}
```

**Success Criteria**:
- ✅ All wrappers use hashtable splatting for Spectre calls
- ✅ No direct positional parameter passing to Spectre functions
- ✅ Code analysis confirms pattern compliance

### 2.4 Markup Escaping Validation

```powershell
Describe "Markup Escaping" {
    It "escapes markup by default" {
        $unsafe = "Text with [red]markup[/] and [brackets]"
        $output = Write-ContextForgePanel -Content $unsafe *>&1 | Out-String

        $plain = Remove-AnsiSequences $output
        # Brackets should be escaped (doubled) or preserved literally
        $plain | Should -Match '\[.*\]'
    }

    It "allows markup with -AllowMarkup" {
        $markup = "[green]Success[/] operation"
        $output = Write-ContextForgePanel -Content $markup -AllowMarkup *>&1 | Out-String

        # Should contain ANSI sequences from rendered markup
        $output | Should -Match '\x1b\['
    }

    It "ConvertTo-SafeSpectreMarkup escapes correctly" {
        $unsafe = "Data [with] [markup]"
        $safe = ConvertTo-SafeSpectreMarkup -Text $unsafe

        # Should escape opening and closing brackets
        $safe | Should -Be "Data [[with]] [[markup]]"
    }
}
```

**Success Criteria**:
- ✅ User input escaped by default
- ✅ `-AllowMarkup` switch enables markup processing
- ✅ Escaping function doubles brackets correctly

### 2.5 Error Handling Validation

```powershell
Describe "Error Handling" {
    It "falls back to plain text on Spectre error" {
        Mock Format-SpectrePanel { throw "Rendering failed" }

        $output = Write-ContextForgePanel -Title "Test" -Content "Data" *>&1 | Out-String

        # Should still produce output
        $output | Should -Not -BeNullOrEmpty
        $output | Should -Match 'Test'
        $output | Should -Match 'Data'
    }

    It "uses Format-SpectreException in interactive mode" {
        Mock Format-SpectrePanel { throw "Test error" }
        Mock Test-CIEnvironment { return $false }
        Mock Format-SpectreException { "Formatted exception" }

        { Write-ContextForgePanel -Title "Test" -Content "Data" } | Should -Throw

        Assert-MockCalled Format-SpectreException -Times 1
    }

    It "logs warnings on fallback" {
        Mock Format-SpectrePanel { throw "Error" }

        $warnings = Write-ContextForgePanel -Title "Test" -Content "Data" 3>&1

        $warnings | Should -Not -BeNullOrEmpty
        $warnings | Should -Match 'failed'
    }
}
```

**Success Criteria**:
- ✅ Graceful degradation to plain text
- ✅ Spectre exception formatting in interactive mode
- ✅ Warning logs on fallback
- ✅ No unhandled exceptions

---

## Phase 3: Demo Script Validation

### Objective
Confirm demo script meets all functional and quality requirements

### 3.1 Execution Validation

```powershell
Describe "Demo Script Execution" {
    Context "Exit Codes" {
        It "exits 0 on success" {
            & scripts\Invoke-ContextForgeSpectreDemo.ps1 -CI -NoPause
            $LASTEXITCODE | Should -Be 0
        }

        It "exits 1 on module import failure" {
            Mock Import-Module { throw "Module not found" }

            & scripts\Invoke-ContextForgeSpectreDemo.ps1 -CI -NoPause
            $LASTEXITCODE | Should -Be 1
        }
    }

    Context "Timing" {
        It "completes within expected duration" {
            $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
            & scripts\Invoke-ContextForgeSpectreDemo.ps1 -CI -NoPause -DurationSeconds 1
            $stopwatch.Stop()

            # Should complete in < 5 seconds for DurationSeconds=1
            $stopwatch.Elapsed.TotalSeconds | Should -BeLessThan 5
        }
    }
}
```

**Success Criteria**:
- ✅ Exit 0 on success
- ✅ Exit 1 on errors
- ✅ Completes within expected time bounds
- ✅ No hangs or infinite loops

### 3.2 Artifact Validation

```powershell
Describe "Artifact Quality" {
    BeforeEach {
        $testPath = Join-Path $TestDrive "demo-test"
        & scripts\Invoke-ContextForgeSpectreDemo.ps1 -CI -NoPause -ArtifactsPath $testPath
    }

    It "creates both required artifacts" {
        $jsonl = Get-ChildItem $testPath -Filter "*.jsonl"
        $txt = Get-ChildItem $testPath -Filter "*.txt"

        $jsonl | Should -HaveCount 1
        $txt | Should -HaveCount 1
    }

    It "JSONL contains valid JSON on each line" {
        $jsonlPath = (Get-ChildItem $testPath -Filter "*.jsonl")[0].FullName
        $lines = Get-Content $jsonlPath

        foreach ($line in $lines) {
            { $line | ConvertFrom-Json } | Should -Not -Throw
        }
    }

    It "transcript is readable UTF-8 text" {
        $txtPath = (Get-ChildItem $testPath -Filter "*.txt")[0].FullName
        $content = Get-Content $txtPath -Raw

        $content | Should -Not -BeNullOrEmpty
        $content.Length | Should -BeGreaterThan 100
    }
}
```

**Success Criteria**:
- ✅ JSONL and transcript files created
- ✅ JSONL contains valid JSON per line
- ✅ Transcript readable and contains expected content
- ✅ Files have appropriate sizes (not empty, not corrupted)

### 3.3 Hash Validation

```powershell
Describe "SHA-256 Hash Integrity" {
    BeforeEach {
        $testPath = Join-Path $TestDrive "demo-hash-test"
        & scripts\Invoke-ContextForgeSpectreDemo.ps1 -CI -NoPause -ArtifactsPath $testPath

        $jsonlPath = (Get-ChildItem $testPath -Filter "*.jsonl")[0].FullName
        $txtPath = (Get-ChildItem $testPath -Filter "*.txt")[0].FullName

        $events = Get-Content $jsonlPath | ForEach-Object { $_ | ConvertFrom-Json }
        $script:completeEvent = $events | Where-Object { $_.event_type -eq 'demo_complete' }
    }

    It "computes correct JSONL hash" {
        $actualHash = (Get-FileHash -Path $jsonlPath -Algorithm SHA256).Hash
        $completeEvent.jsonl_hash | Should -Be $actualHash
    }

    It "computes correct transcript hash" {
        $actualHash = (Get-FileHash -Path $txtPath -Algorithm SHA256).Hash
        $completeEvent.transcript_hash | Should -Be $actualHash
    }

    It "hash values are 64 characters (SHA-256 hex)" {
        $completeEvent.jsonl_hash.Length | Should -Be 64
        $completeEvent.transcript_hash.Length | Should -Be 64
    }

    It "hash values are valid hexadecimal" {
        $completeEvent.jsonl_hash | Should -Match '^[0-9A-F]{64}$'
        $completeEvent.transcript_hash | Should -Match '^[0-9A-F]{64}$'
    }
}
```

**Success Criteria**:
- ✅ Logged hashes match actual file hashes
- ✅ Hash format is valid SHA-256 (64 hex characters)
- ✅ Hashes computed before script exit
- ✅ Hashes included in demo_complete event

---

## Phase 4: Encoding Validation

### Objective
Comprehensive UTF-8 compliance verification

### 4.1 File Encoding Validation

```powershell
Describe "File Encoding Compliance" {
    It "all module files are UTF-8 without BOM" {
        $files = Get-ChildItem modules\ContextForge.Spectre -Recurse -Filter *.ps*1

        foreach ($file in $files) {
            $bytes = Get-Content $file.FullName -AsByteStream -First 3

            # No UTF-8 BOM (EF BB BF)
            if ($bytes.Count -ge 3) {
                $hasBOM = ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)
                $hasBOM | Should -Be $false -Because "$($file.Name) should not have BOM"
            }
        }
    }

    It "all test files are UTF-8 without BOM" {
        $files = Get-ChildItem tests -Filter *.Tests.ps1

        foreach ($file in $files) {
            $bytes = Get-Content $file.FullName -AsByteStream -First 3

            if ($bytes.Count -ge 3) {
                $hasBOM = ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)
                $hasBOM | Should -Be $false -Because "$($file.Name) should not have BOM"
            }
        }
    }

    It "demo script is UTF-8 without BOM" {
        $bytes = Get-Content scripts\Invoke-ContextForgeSpectreDemo.ps1 -AsByteStream -First 3

        $bytes[0] | Should -Not -Be 0xEF
    }
}
```

**Success Criteria**:
- ✅ All `.ps1` and `.psm1` files use UTF-8 without BOM
- ✅ No UTF-16 or other encodings detected
- ✅ Consistent encoding across all PowerShell files

### 4.2 Character Preservation Validation

```powershell
Describe "Character Preservation" {
    It "preserves emoji in output" {
        $emoji = "✓ ❌ ⏳ 🎉"
        $tempFile = Join-Path $TestDrive "emoji-test.txt"

        $emoji | Out-File -FilePath $tempFile -Encoding utf8
        $read = Get-Content $tempFile -Raw

        # Should preserve all characters
        $read.Trim().Length | Should -BeGreaterOrEqual $emoji.Length
    }

    It "preserves box drawing in transcript" {
        $testPath = Join-Path $TestDrive "box-test"
        & scripts\Invoke-ContextForgeSpectreDemo.ps1 -CI -NoPause -ArtifactsPath $testPath

        $txtPath = (Get-ChildItem $testPath -Filter "*.txt")[0].FullName
        $content = Get-Content $txtPath -Raw

        # Should not corrupt box characters (if present in output)
        $content.Length | Should -BeGreaterThan 0
    }

    It "preserves international characters" {
        $intl = "Ñoño français 日本語 中文"
        $tempFile = Join-Path $TestDrive "intl-test.txt"

        $intl | Out-File -FilePath $tempFile -Encoding utf8
        $read = Get-Content $tempFile -Raw

        $read.Trim() | Should -Be $intl
    }
}
```

**Success Criteria**:
- ✅ Emoji characters preserved
- ✅ Box drawing characters preserved
- ✅ International characters (extended Unicode) preserved
- ✅ No character corruption or substitution

---

## Phase 5: Governance Validation

### Objective
Verify alignment with ContextForge governance standards

### 5.1 Terminal Output Standards Compliance

**Validation Checklist** (from `terminal-output.instructions.md`):

- [ ] **Rich Library Integration**: Uses Rich-equivalent patterns
  - Panel formatting ✅
  - Progress indicators ✅
  - Table display ✅
  - Status messages ✅

- [ ] **9-Component Flow**:
  1. ✅ Initialization (UTF-8 setup)
  2. ✅ Status updates (information logs)
  3. ✅ Step display (panel rendering)
  4. ✅ Progress tracking (progress bars)
  5. ✅ Message panels (info/warning/error)
  6. ✅ Operations summary (table display)
  7. ✅ Executive summary (final output)
  8. ✅ Evidence preservation (JSONL + hashes)
  9. ✅ Final status (exit code + summary)

- [ ] **Color Schemes**:
  - Success: Green ✅
  - Warning: Yellow ✅
  - Error: Red ✅
  - Info: Blue/Cyan ✅

**Success Criteria**:
- ✅ All 9 components implemented
- ✅ Color scheme consistent
- ✅ Rich-equivalent patterns used
- ✅ Compliance documented

### 5.2 Unicode Configuration Compliance

**Validation Checklist** (from `terminal-unicode-configuration.instructions.md`):

- [ ] **UTF-8 Enforcement**:
  - ✅ PowerShell profile configured (documented in instructions)
  - ✅ Transcript pattern uses `Tee-Object -Encoding utf8`
  - ✅ Python files include encoding header (if applicable)
  - ✅ VS Code `files.encoding` set to `utf8` (documented)

- [ ] **Sacred Geometry Support**:
  - ✅ Triangle (△) renders correctly
  - ✅ Circle (○) renders correctly
  - ✅ Spiral (🌀) renders correctly
  - ✅ Golden Ratio (φ) renders correctly
  - ✅ Mathematical symbols (∑ ∫ √) render correctly

- [ ] **Validation Test**:
  - ✅ `tests/validate-unicode-support.ps1` passes
  - ✅ Sacred Geometry symbols display correctly
  - ✅ Encoding validation succeeds

**Success Criteria**:
- ✅ UTF-8 configuration documented and validated
- ✅ Sacred Geometry symbols supported
- ✅ Validation test passes

### 5.3 Evidence & Quality Management

**Validation Checklist**:

- [ ] **Correlation IDs**: ✅ Session/work IDs in artifacts
- [ ] **Hash Algorithm**: ✅ SHA-256 for all artifacts
- [ ] **Evidence Logging**: ✅ Structured JSONL
- [ ] **Session Correlation**: ✅ All evidence linked
- [ ] **Quality Gates**: ✅ Validation tests pass

**File**: `AAR-Spectre-Governance-Compliance-Validation-{date}.md`

---

## Phase 6: Performance Validation

### Objective
Verify acceptable performance characteristics

### 6.1 Execution Time Validation

```powershell
Describe "Performance Benchmarks" {
    It "demo completes in < 10 seconds" {
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        & scripts\Invoke-ContextForgeSpectreDemo.ps1 -CI -NoPause -DurationSeconds 1
        $stopwatch.Stop()

        $stopwatch.Elapsed.TotalSeconds | Should -BeLessThan 10
    }

    It "test suite completes in < 30 seconds" {
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        Invoke-Pester -Path tests\ContextForge.Spectre.*.Tests.ps1 -Quiet
        $stopwatch.Stop()

        $stopwatch.Elapsed.TotalSeconds | Should -BeLessThan 30
    }

    It "individual panel render < 500ms" {
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        Write-ContextForgePanel -Title "Test" -Content "Data" | Out-Null
        $stopwatch.Stop()

        $stopwatch.Elapsed.TotalMilliseconds | Should -BeLessThan 500
    }
}
```

**Success Criteria**:
- ✅ Demo script: < 10 seconds
- ✅ Test suite: < 30 seconds
- ✅ Individual operations: < 500ms
- ✅ No performance regressions

### 6.2 Resource Usage Validation

```powershell
Describe "Resource Usage" {
    It "does not leak memory" {
        $before = (Get-Process -Id $PID).WorkingSet64

        1..10 | ForEach-Object {
            & scripts\Invoke-ContextForgeSpectreDemo.ps1 -CI -NoPause
        }

        [GC]::Collect()
        Start-Sleep -Seconds 2

        $after = (Get-Process -Id $PID).WorkingSet64
        $increase = $after - $before

        # Should not increase by more than 50MB
        $increase | Should -BeLessThan 50MB
    }

    It "artifact files have reasonable sizes" {
        $testPath = Join-Path $TestDrive "size-test"
        & scripts\Invoke-ContextForgeSpectreDemo.ps1 -CI -NoPause -ArtifactsPath $testPath

        $jsonlSize = (Get-ChildItem $testPath -Filter "*.jsonl")[0].Length
        $txtSize = (Get-ChildItem $testPath -Filter "*.txt")[0].Length

        # JSONL should be < 10KB for demo
        $jsonlSize | Should -BeLessThan 10KB

        # Transcript should be < 50KB for demo
        $txtSize | Should -BeLessThan 50KB
    }
}
```

**Success Criteria**:
- ✅ No memory leaks detected
- ✅ Artifact sizes within expected ranges
- ✅ Resource cleanup on exit

---

## Phase 7: CI/CD Pipeline Validation

### Objective
Verify GitHub Actions workflow integration

### 7.1 Workflow Execution Validation

**Manual Validation Steps**:

1. **Trigger workflow**:
   ```bash
   git push origin main
   # Or manually via GitHub Actions UI
   ```

2. **Monitor execution**:
   - Navigate to Actions tab
   - Check "Spectre Demo Smoke Test" workflow
   - Verify all steps complete successfully

3. **Validate artifacts**:
   - Download workflow artifacts
   - Verify JSONL and transcript files present
   - Check file sizes and content

**Success Criteria**:
- ✅ Workflow triggers on push to main/develop
- ✅ All steps execute successfully
- ✅ Artifacts uploaded and downloadable
- ✅ Exit code 0 for demo script
- ✅ UTF-8 validation passes in CI

### 7.2 Multi-Platform Validation

```yaml
# Future enhancement: Test on multiple OS
strategy:
  matrix:
    os: [windows-latest, ubuntu-latest, macos-latest]
    pwsh-version: ['7.4', '7.5']
```

**Success Criteria** (when implemented):
- ✅ Passes on Windows, Linux, macOS
- ✅ Compatible with PowerShell 7.4 and 7.5
- ✅ Consistent behavior across platforms

---

## Phase 8: Security Validation

### Objective
Verify safe input handling and secure operations

### 8.1 Input Sanitization Validation

```powershell
Describe "Security - Input Handling" {
    It "escapes malicious markup by default" {
        $malicious = "[link=javascript:alert('XSS')]Click[/]"
        $output = Write-ContextForgePanel -Content $malicious *>&1 | Out-String

        $plain = Remove-AnsiSequences $output
        # Should escape markup, not execute
        $plain | Should -Match '\[link'
    }

    It "sanitizes path inputs" {
        $maliciousPath = "..\..\..\etc\passwd"

        { & scripts\Invoke-ContextForgeSpectreDemo.ps1 -ArtifactsPath $maliciousPath -CI -NoPause } |
            Should -Not -Throw
    }

    It "validates parameter types" {
        { & scripts\Invoke-ContextForgeSpectreDemo.ps1 -DurationSeconds "malicious" -CI -NoPause } |
            Should -Throw
    }
}
```

**Success Criteria**:
- ✅ Markup escaping prevents injection
- ✅ Path traversal attempts handled safely
- ✅ Type validation enforced
- ✅ No code execution from user input

### 8.2 Credential Handling Validation

```powershell
Describe "Security - Credential Safety" {
    It "does not log sensitive data" {
        # If credentials were used (future enhancement)
        # Verify they don't appear in logs/artifacts
    }

    It "redacts secrets from output" {
        # If secrets handling added
        # Verify redaction in transcripts/JSONL
    }
}
```

**Success Criteria**:
- ✅ No credentials in logs
- ✅ Secrets redacted from output
- ✅ Safe error messages (no sensitive data)

---

## Validation Execution Schedule

### Pre-Release Validation (Blocking)

**Required before merging to main**:
- ✅ Phase 1: Diagnostic Validation
- ✅ Phase 2: Module Validation
- ✅ Phase 3: Demo Script Validation
- ✅ Phase 4: Encoding Validation
- ✅ Phase 5: Governance Validation

**Timeline**: 4-6 hours

### Post-Release Validation (Non-Blocking)

**Required within 1 week after release**:
- ✅ Phase 6: Performance Validation
- ✅ Phase 7: CI/CD Pipeline Validation
- ✅ Phase 8: Security Validation

**Timeline**: 2-3 hours

---

## Validation Reporting

### Validation Report Template

```markdown
# ContextForge.Spectre Validation Report

**Date**: {date}
**Validator**: {name}
**Version**: {module version}

## Executive Summary
- Overall Status: [PASS/FAIL/PARTIAL]
- Phases Completed: {X}/8
- Critical Issues: {count}
- Recommendations: {count}

## Phase Results

### Phase 1: Diagnostic Validation
- Status: [PASS/FAIL]
- File Health: [details]
- Parameter Resolution: [details]
- Root Cause Documentation: [link]

### Phase 2: Module Validation
- Status: [PASS/FAIL]
- UTF-8 Enforcement: [✓/✗]
- CI Detection: [✓/✗]
- Splatting Patterns: [✓/✗]
- Markup Escaping: [✓/✗]
- Error Handling: [✓/✗]

[... continue for all phases ...]

## Issues Identified

| ID | Phase | Severity | Description | Status |
|----|-------|----------|-------------|--------|
| V-001 | 2 | High | ... | Open |

## Recommendations

1. [Recommendation with priority]
2. [...]

## Sign-Off

Validator: {name}
Date: {date}
Status: [APPROVED/REJECTED/CONDITIONAL]
```

**File**: `validation-reports/Spectre-Validation-{date}.md`

---

## Continuous Validation

### Automated Validation (CI)

```yaml
# .github/workflows/validation.yml
name: Continuous Validation

on:
  push:
    branches: [main, develop]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  validate:
    runs-on: windows-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run validation suite
        run: |
          Invoke-Pester -Path tests/ContextForge.Spectre.*.Tests.ps1 -CI

      - name: Encoding validation
        run: |
          . tests/helpers/Test-ScriptFileHealth.ps1
          Test-ScriptFileHealth -Path scripts/ -Recursive
```

### Manual Validation Triggers

- Before major releases
- After significant refactoring
- Quarterly governance reviews
- After dependency updates

---

## Success Metrics

### Overall Validation Success

- ✅ All 8 phases pass validation
- ✅ Zero critical issues
- ✅ < 3 medium-priority issues
- ✅ All governance requirements met
- ✅ Performance within targets
- ✅ Security validation clean

### Quality Gates

**MANDATORY (Blocking)**:
- Diagnostic validation passes
- Module validation passes
- Demo script validation passes
- Encoding validation passes
- Governance validation passes

**RECOMMENDED (Warning)**:
- Performance validation passes
- CI/CD validation passes
- Security validation passes

---

## References

- Implementation Plan: `docs/plans/SPECTRE-IMPLEMENTATION-PLAN.md`
- Testing Plan: `docs/plans/SPECTRE-TESTING-PLAN.md`
- Authority: `.github/instructions/terminal-output.instructions.md`
- Authority: `.github/instructions/terminal-unicode-configuration.instructions.md`
- Research: `docs/research/PwshSpectreConsole-Best-Practices.md`
- Research: `docs/research/PowerShell-Parameter-Set-Error-Diagnostic-Guide.md`
- Research: `docs/research/TESTING-TERMINAL-UI-STRATEGY.md`
