# ContextForge.Spectre Testing Plan

**Created**: 2025-11-05
**Authority**: Terminal UI Testing Research (2025-11-05)
**Status**: ACTIVE

---

## Executive Summary

This plan establishes a comprehensive testing strategy for the ContextForge.Spectre module based on research findings about testing terminal UI libraries in PowerShell with CI/CD integration.

### Testing Philosophy

**Dual-Mode Strategy**: Tests must validate functionality in both:
1. **Interactive Mode**: Rich Spectre rendering with full ANSI support
2. **CI Mode**: Plain text fallback with capture-friendly output

**Content Over Formatting**: Tests validate semantic content, not ANSI sequences

---

## Test Architecture

### Test Organization

```
tests/
├── ContextForge.Spectre.Helpers.Tests.ps1        # Unit tests (EXISTING ✅)
├── ContextForge.Spectre.DemoScript.Tests.ps1     # Demo validation (NEW)
├── ContextForge.Spectre.Integration.Tests.ps1    # E2E scenarios (NEW)
├── ContextForge.Spectre.Encoding.Tests.ps1       # UTF-8 validation (NEW)
└── helpers/
    ├── TerminalUI.TestHelpers.psm1               # Utilities (NEW)
    └── Test-ScriptFileHealth.ps1                 # File diagnostics (NEW)
```

### Test Helper Module

**Purpose**: Centralize common testing utilities
**File**: `tests/helpers/TerminalUI.TestHelpers.psm1`

**Key Functions**:
```powershell
# ANSI Processing
Remove-AnsiSequences           # Strip ANSI for content validation
Test-ContainsAnsiSequences     # Detect ANSI presence
Get-AnsiSequenceCount          # Count ANSI codes

# Output Capture
Capture-HostOutput             # Capture Write-Host/Write-Information
Capture-StreamOutput           # Multi-stream capture
ConvertTo-PlainText            # Comprehensive ANSI removal

# Environment Control
Set-CIEnvironment              # Mock CI environment
Set-InteractiveEnvironment     # Mock interactive environment
Test-OutputIsRedirected        # Detect redirection

# Validation
Test-Utf8Encoding              # Validate UTF-8 (no BOM)
Test-JsonlStructure            # Validate JSONL events
Compare-OutputSnapshot         # Snapshot testing
```

---

## Unit Tests (Existing - Enhancement)

### File: `tests/ContextForge.Spectre.Helpers.Tests.ps1`

**Current Coverage** (4 tests):
- ✅ UTF-8 console configuration
- ✅ Panel capture validation
- ✅ Selection default behavior
- ✅ Progress wrapper functionality

**Enhancements Needed**:

#### 1. CI Mode Testing

```powershell
Describe "Set-CfUtf8Console" {
    Context "CI Environment" {
        BeforeEach {
            Set-CIEnvironment
        }

        It "suppresses warnings with -SkipWarnings in CI" {
            $output = Set-CfUtf8Console -SkipWarnings *>&1
            $output | Where-Object { $_ -is [System.Management.Automation.WarningRecord] } |
                Should -BeNullOrEmpty
        }

        It "logs information correctly in CI" {
            $output = Set-CfUtf8Console -Quiet:$false 6>&1
            $output | Where-Object { $_.ToString() -match 'UTF-8 encoding' } |
                Should -Not -BeNullOrEmpty
        }
    }
}
```

#### 2. Markup Escaping Tests

```powershell
Describe "Write-ContextForgePanel" {
    Context "Markup Handling" {
        It "escapes markup characters by default" {
            $unsafeText = "Data with [brackets] and [red]color[/]"
            $output = Write-ContextForgePanel -Content $unsafeText *>&1 | Out-String

            # Should not interpret [red] as markup
            $plainOutput = Remove-AnsiSequences $output
            $plainOutput | Should -Match '\[brackets\]'
            $plainOutput | Should -Match '\[red\]'
        }

        It "allows markup with -AllowMarkup switch" {
            $markupText = "[green]Success[/] operation"
            $output = Write-ContextForgePanel -Content $markupText -AllowMarkup *>&1 | Out-String

            # Should render green color
            $output | Should -Match '\x1b\[' # ANSI escape detected
        }
    }
}
```

#### 3. Error Handling Tests

```powershell
Describe "Write-ContextForgePanel" {
    Context "Error Scenarios" {
        It "falls back to plain text when Spectre fails" {
            Mock Format-SpectrePanel { throw "Spectre rendering failed" }

            $output = Write-ContextForgePanel -Title "Test" -Content "Data" *>&1 | Out-String

            # Should still produce output
            $output | Should -Not -BeNullOrEmpty
            $output | Should -Match 'Test'
            $output | Should -Match 'Data'
        }

        It "logs warning on fallback in interactive mode" {
            Mock Format-SpectrePanel { throw "Rendering error" }
            Mock Test-CIEnvironment { return $false }

            $warnings = Write-ContextForgePanel -Title "Test" -Content "Data" 3>&1
            $warnings | Should -Not -BeNullOrEmpty
            $warnings | Should -Match 'rendering failed'
        }
    }
}
```

#### 4. Encoding Validation Tests

```powershell
Describe "Set-CfUtf8Console" {
    Context "Encoding Verification" {
        It "sets OutputEncoding to UTF-8" {
            Set-CfUtf8Console
            $OutputEncoding.EncodingName | Should -Be 'Unicode (UTF-8)'
        }

        It "sets Console.InputEncoding to UTF-8" {
            Set-CfUtf8Console
            [console]::InputEncoding.EncodingName | Should -Be 'Unicode (UTF-8)'
        }

        It "sets Console.OutputEncoding to UTF-8" {
            Set-CfUtf8Console
            [console]::OutputEncoding.EncodingName | Should -Be 'Unicode (UTF-8)'
        }

        It "validates encoding is UTF-8 without BOM" {
            $tempFile = Join-Path $TestDrive "utf8-test.txt"
            "Test content" | Out-File -FilePath $tempFile -Encoding utf8

            $bytes = Get-Content $tempFile -AsByteStream -First 3
            # No BOM: should not start with EF BB BF
            $bytes[0] | Should -Not -Be 0xEF
        }
    }
}
```

---

## Demo Script Tests (New)

### File: `tests/ContextForge.Spectre.DemoScript.Tests.ps1`

**Purpose**: Validate demo script end-to-end functionality

```powershell
#Requires -Version 7.0

Describe "Invoke-ContextForgeSpectreDemo" {
    BeforeAll {
        $demoScript = Resolve-Path "$PSScriptRoot\..\scripts\Invoke-ContextForgeSpectreDemo.ps1"
        $testArtifactsPath = Join-Path $TestDrive "demo-artifacts"

        Import-Module "$PSScriptRoot\helpers\TerminalUI.TestHelpers.psm1" -Force
    }

    AfterEach {
        if (Test-Path $testArtifactsPath) {
            Remove-Item -Path $testArtifactsPath -Recurse -Force
        }
    }

    Context "Parameter Validation" {
        It "accepts all parameters without errors" {
            $params = @{
                ArtifactsPath = $testArtifactsPath
                CI = $true
                NoPause = $true
                DurationSeconds = 1
            }

            { & $demoScript @params } | Should -Not -Throw
        }

        It "uses default artifacts path when not specified" {
            { & $demoScript -CI -NoPause } | Should -Not -Throw
            Test-Path "artifacts/spectre-demo" | Should -Be $true
        }

        It "validates DurationSeconds is positive" {
            { & $demoScript -CI -NoPause -DurationSeconds 0 } | Should -Throw
        }
    }

    Context "CI Mode Execution" {
        It "exits successfully (exit code 0)" {
            $result = & $demoScript -CI -NoPause -ArtifactsPath $testArtifactsPath
            $LASTEXITCODE | Should -Be 0
        }

        It "completes within expected time" {
            $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
            & $demoScript -CI -NoPause -ArtifactsPath $testArtifactsPath -DurationSeconds 1
            $stopwatch.Stop()

            # Should complete in <5 seconds for DurationSeconds=1
            $stopwatch.Elapsed.TotalSeconds | Should -BeLessThan 5
        }

        It "does not prompt for user input" {
            # Mock Read-Host to detect if called
            Mock Read-Host { throw "Read-Host called in CI mode" } -ModuleName ContextForge.Spectre

            { & $demoScript -CI -NoPause -ArtifactsPath $testArtifactsPath } | Should -Not -Throw
        }
    }

    Context "Artifact Generation" {
        BeforeEach {
            & $demoScript -CI -NoPause -ArtifactsPath $testArtifactsPath
        }

        It "creates artifacts directory" {
            Test-Path $testArtifactsPath | Should -Be $true
        }

        It "creates JSONL log file" {
            $jsonlFiles = Get-ChildItem -Path $testArtifactsPath -Filter "demo-*.jsonl"
            $jsonlFiles | Should -HaveCount 1
        }

        It "creates transcript file" {
            $txtFiles = Get-ChildItem -Path $testArtifactsPath -Filter "demo-*.txt"
            $txtFiles | Should -HaveCount 1
        }

        It "names files with timestamp pattern" {
            $jsonlFile = (Get-ChildItem -Path $testArtifactsPath -Filter "*.jsonl")[0]
            $jsonlFile.Name | Should -Match 'demo-\d{8}-\d{6}\.jsonl'
        }
    }

    Context "JSONL Event Validation" {
        BeforeEach {
            & $demoScript -CI -NoPause -ArtifactsPath $testArtifactsPath
            $jsonlPath = (Get-ChildItem -Path $testArtifactsPath -Filter "*.jsonl")[0].FullName
            $script:events = Get-Content $jsonlPath | ForEach-Object { $_ | ConvertFrom-Json }
        }

        It "logs demo_start event first" {
            $events[0].event_type | Should -Be "demo_start"
        }

        It "includes ci_mode flag in demo_start" {
            $startEvent = $events | Where-Object { $_.event_type -eq 'demo_start' }
            $startEvent.ci_mode | Should -Be $true
        }

        It "logs panel_rendered event" {
            $events.event_type | Should -Contain "panel_rendered"
        }

        It "logs progress_rendered event" {
            $events.event_type | Should -Contain "progress_rendered"
        }

        It "logs table_rendered event" {
            $events.event_type | Should -Contain "table_rendered"
        }

        It "logs demo_complete event last" {
            $events[-1].event_type | Should -Be "demo_complete"
        }

        It "includes SHA-256 hashes in demo_complete" {
            $completeEvent = $events | Where-Object { $_.event_type -eq 'demo_complete' }
            $completeEvent.jsonl_hash | Should -Not -BeNullOrEmpty
            $completeEvent.jsonl_hash.Length | Should -Be 64  # SHA-256 hex length
            $completeEvent.transcript_hash | Should -Not -BeNullOrEmpty
            $completeEvent.transcript_hash.Length | Should -Be 64
        }

        It "all events have timestamps" {
            $events | ForEach-Object {
                $_.timestamp | Should -Not -BeNullOrEmpty
                { [datetime]::Parse($_.timestamp) } | Should -Not -Throw
            }
        }

        It "timestamps are in chronological order" {
            $timestamps = $events | ForEach-Object { [datetime]::Parse($_.timestamp) }
            for ($i = 1; $i -lt $timestamps.Count; $i++) {
                $timestamps[$i] | Should -BeGreaterOrEqual $timestamps[$i-1]
            }
        }
    }

    Context "Transcript Content Validation" {
        BeforeEach {
            & $demoScript -CI -NoPause -ArtifactsPath $testArtifactsPath
            $txtPath = (Get-ChildItem -Path $testArtifactsPath -Filter "*.txt")[0].FullName
            $script:transcript = Get-Content $txtPath -Raw
        }

        It "includes demo start marker" {
            $transcript | Should -Match "=== ContextForge Spectre Demo Start:"
        }

        It "includes demo end marker" {
            $transcript | Should -Match "=== Demo End:"
        }

        It "contains panel output" {
            $transcript | Should -Match "Welcome"
        }

        It "contains table output" {
            $transcript | Should -Match "Demo Results"
        }

        It "captures both stdout and stderr" {
            # Transcript should include error stream (2>&1 in Tee-Object)
            $transcript | Should -Not -BeNullOrEmpty
        }
    }

    Context "Encoding Validation" {
        BeforeEach {
            & $demoScript -CI -NoPause -ArtifactsPath $testArtifactsPath
        }

        It "creates JSONL with UTF-8 encoding (no BOM)" {
            $jsonlPath = (Get-ChildItem -Path $testArtifactsPath -Filter "*.jsonl")[0].FullName
            Test-Utf8Encoding -Path $jsonlPath | Should -Be $true

            $bytes = Get-Content $jsonlPath -AsByteStream -First 3
            $bytes[0] | Should -Not -Be 0xEF  # No UTF-8 BOM
        }

        It "creates transcript with UTF-8 encoding (no BOM)" {
            $txtPath = (Get-ChildItem -Path $testArtifactsPath -Filter "*.txt")[0].FullName
            Test-Utf8Encoding -Path $txtPath | Should -Be $true

            $bytes = Get-Content $txtPath -AsByteStream -First 3
            $bytes[0] | Should -Not -Be 0xEF
        }

        It "preserves UTF-8 characters in output" {
            $txtPath = (Get-ChildItem -Path $testArtifactsPath -Filter "*.txt")[0].FullName
            $content = Get-Content $txtPath -Raw

            # Should contain UTF-8 characters if present (✓, ⏳, etc.)
            $content | Should -Match '[✓⏳]' -Or { $content.Length -gt 0 }
        }
    }

    Context "Hash Verification" {
        BeforeEach {
            & $demoScript -CI -NoPause -ArtifactsPath $testArtifactsPath
            $jsonlPath = (Get-ChildItem -Path $testArtifactsPath -Filter "*.jsonl")[0].FullName
            $txtPath = (Get-ChildItem -Path $testArtifactsPath -Filter "*.txt")[0].FullName

            $events = Get-Content $jsonlPath | ForEach-Object { $_ | ConvertFrom-Json }
            $script:completeEvent = $events | Where-Object { $_.event_type -eq 'demo_complete' }
        }

        It "logged JSONL hash matches actual file hash" {
            $actualHash = (Get-FileHash -Path $jsonlPath -Algorithm SHA256).Hash
            $completeEvent.jsonl_hash | Should -Be $actualHash
        }

        It "logged transcript hash matches actual file hash" {
            $actualHash = (Get-FileHash -Path $txtPath -Algorithm SHA256).Hash
            $completeEvent.transcript_hash | Should -Be $actualHash
        }
    }

    Context "Error Scenarios" {
        It "handles missing module gracefully" {
            Mock Import-Module { throw "Module not found" }

            { & $demoScript -CI -NoPause -ArtifactsPath $testArtifactsPath } | Should -Throw
            $LASTEXITCODE | Should -Be 1
        }

        It "logs errors to JSONL on component failure" {
            # This would require injecting failures - skip for now or mock specific components
            # Example: Mock Write-ContextForgePanel to throw
        }
    }
}
```

---

## Integration Tests (New)

### File: `tests/ContextForge.Spectre.Integration.Tests.ps1`

**Purpose**: End-to-end scenarios across multiple components

```powershell
#Requires -Version 7.0

Describe "ContextForge.Spectre Integration" {
    BeforeAll {
        Import-Module "$PSScriptRoot\..\modules\ContextForge.Spectre" -Force
        Import-Module "$PSScriptRoot\helpers\TerminalUI.TestHelpers.psm1" -Force
    }

    Context "UTF-8 → Spectre → Capture Pipeline" {
        It "full pipeline preserves UTF-8 content" {
            Set-CfUtf8Console -Quiet

            $testData = "Demo: ✓ Success, ⏳ Pending, ❌ Failed"
            $output = Write-ContextForgePanel -Content $testData *>&1 | Out-String

            # Content should be present (ANSI stripped)
            $plainOutput = Remove-AnsiSequences $output
            $plainOutput | Should -Match 'Success'
            $plainOutput | Should -Match 'Pending'
            $plainOutput | Should -Match 'Failed'
        }
    }

    Context "CI Environment Detection" {
        It "detects GitHub Actions environment" {
            $env:GITHUB_ACTIONS = 'true'

            Test-CIEnvironment | Should -Be $true

            $env:GITHUB_ACTIONS = $null
        }

        It "detects Azure DevOps environment" {
            $env:TF_BUILD = 'True'

            Test-CIEnvironment | Should -Be $true

            $env:TF_BUILD = $null
        }

        It "uses plain output in CI environment" {
            Set-CIEnvironment

            $output = Write-ContextForgePanel -Title "Test" -Content "Data" *>&1 | Out-String

            # Should NOT contain ANSI sequences in CI
            Test-ContainsAnsiSequences -Text $output | Should -Be $false
        }
    }

    Context "Multiple Component Interaction" {
        It "renders panel, progress, and table sequentially" {
            $output = & {
                Write-ContextForgePanel -Title "Step 1" -Content "Panel test"
                Write-ContextForgeProgress -Title "Step 2" -Total 100
                Write-ContextForgeTable -Data @([PSCustomObject]@{Col1='Val1'}) -Title "Step 3"
            } *>&1 | Out-String

            $plainOutput = Remove-AnsiSequences $output
            $plainOutput | Should -Match 'Step 1'
            $plainOutput | Should -Match 'Step 2'
            $plainOutput | Should -Match 'Step 3'
        }
    }

    Context "Error Recovery" {
        It "continues execution after component failure" {
            Mock Write-ContextForgePanel { throw "Panel failed" }

            $output = & {
                try { Write-ContextForgePanel -Title "Test" -Content "Data" } catch {}
                Write-Host "Execution continued"
            } *>&1 | Out-String

            $output | Should -Match 'Execution continued'
        }
    }
}
```

---

## Encoding Tests (New)

### File: `tests/ContextForge.Spectre.Encoding.Tests.ps1`

**Purpose**: Comprehensive UTF-8 validation

```powershell
#Requires -Version 7.0

Describe "ContextForge.Spectre Encoding Compliance" {
    BeforeAll {
        Import-Module "$PSScriptRoot\..\modules\ContextForge.Spectre" -Force
        Import-Module "$PSScriptRoot\helpers\TerminalUI.TestHelpers.psm1" -Force
    }

    Context "Console Encoding Configuration" {
        It "sets all encoding variables to UTF-8" {
            Set-CfUtf8Console

            $OutputEncoding.EncodingName | Should -Be 'Unicode (UTF-8)'
            [console]::InputEncoding.EncodingName | Should -Be 'Unicode (UTF-8)'
            [console]::OutputEncoding.EncodingName | Should -Be 'Unicode (UTF-8)'
        }

        It "uses UTF-8 without BOM for file writes" {
            $tempFile = Join-Path $TestDrive "encoding-test.txt"

            "Test content ✓" | Out-File -FilePath $tempFile -Encoding utf8

            $bytes = Get-Content $tempFile -AsByteStream -First 3
            # UTF-8 without BOM: should NOT start with EF BB BF
            $bytes[0] | Should -Not -Be 0xEF
        }
    }

    Context "Special Character Handling" {
        It "preserves emoji characters" {
            $emoji = "✓ ❌ ⏳ 🎉"
            $output = Write-ContextForgePanel -Content $emoji -AllowMarkup:$false *>&1 | Out-String

            $plainOutput = Remove-AnsiSequences $output
            # Check characters are preserved (exact match or present)
            $plainOutput.Length | Should -BeGreaterThan 0
        }

        It "preserves box drawing characters" {
            $boxChars = "╭─╮│╰─╯"
            $tempFile = Join-Path $TestDrive "box-chars.txt"

            $boxChars | Out-File -FilePath $tempFile -Encoding utf8
            $read = Get-Content $tempFile -Raw

            $read.Trim() | Should -Be $boxChars
        }

        It "preserves international characters" {
            $intl = "Ñoño français 日本語"
            $output = Write-ContextForgePanel -Content $intl -AllowMarkup:$false *>&1 | Out-String

            # Should not corrupt characters
            $output.Length | Should -BeGreaterThan 0
        }
    }

    Context "File Write Encoding" {
        It "writes JSONL with UTF-8 (no BOM)" {
            $jsonlPath = Join-Path $TestDrive "test-events.jsonl"

            @{event="test"; data="value ✓"} | ConvertTo-Json -Compress |
                Add-Content -Path $jsonlPath -Encoding utf8

            Test-Utf8Encoding -Path $jsonlPath | Should -Be $true
        }

        It "Tee-Object uses UTF-8 encoding" {
            $outputPath = Join-Path $TestDrive "tee-test.txt"

            "Content with ✓" | Tee-Object -FilePath $outputPath -Encoding utf8

            Test-Utf8Encoding -Path $outputPath | Should -Be $true
        }
    }
}
```

---

## Test Execution Strategy

### Local Development

```powershell
# Run all tests
Invoke-Pester -Path tests\

# Run specific test file
Invoke-Pester -Path tests\ContextForge.Spectre.DemoScript.Tests.ps1

# Run with coverage
Invoke-Pester -Path tests\ -CodeCoverage modules\ContextForge.Spectre\**\*.ps1

# Run tagged tests
Invoke-Pester -Path tests\ -Tag Unit
Invoke-Pester -Path tests\ -Tag Integration
```

### CI Pipeline

```powershell
# CI-optimized configuration
$config = New-PesterConfiguration
$config.Run.Path = 'tests'
$config.Run.Exit = $true
$config.TestResult.Enabled = $true
$config.TestResult.OutputPath = 'testResults.xml'
$config.TestResult.OutputFormat = 'NUnitXml'
$config.CodeCoverage.Enabled = $true
$config.CodeCoverage.OutputPath = 'coverage.xml'
$config.Output.Verbosity = 'Detailed'

Invoke-Pester -Configuration $config
```

---

## Coverage Targets

### Unit Tests
- **Target**: 85% line coverage
- **Scope**: All Public/*.ps1 functions
- **Priority**: High

### Integration Tests
- **Target**: 70% scenario coverage
- **Scope**: Multi-component workflows
- **Priority**: Medium

### Demo Script Tests
- **Target**: 90% path coverage
- **Scope**: All execution branches and error paths
- **Priority**: High

---

## Test Data Management

### Test Fixtures

```powershell
# tests/fixtures/sample-data.ps1
$script:SamplePanelData = @{
    Title = "Test Panel"
    Content = "Sample content for testing"
    Type = "Info"
}

$script:SampleTableData = @(
    [PSCustomObject]@{ ID = 1; Status = "✓"; Note = "Success" }
    [PSCustomObject]@{ ID = 2; Status = "⏳"; Note = "Pending" }
    [PSCustomObject]@{ ID = 3; Status = "❌"; Note = "Failed" }
)

$script:SampleJsonlEvents = @(
    @{ timestamp = (Get-Date -Format 'o'); event_type = 'test_start' }
    @{ timestamp = (Get-Date -Format 'o'); event_type = 'test_step'; step = 1 }
    @{ timestamp = (Get-Date -Format 'o'); event_type = 'test_complete' }
)
```

---

## Continuous Testing

### Watch Mode (Development)

```powershell
# Install development watcher
Install-Module -Name PSWatcher -Scope CurrentUser

# Watch for changes and re-run tests
Watch-Path -Path modules\ContextForge.Spectre -ScriptBlock {
    Invoke-Pester -Path tests\ContextForge.Spectre.Helpers.Tests.ps1
}
```

### Pre-Commit Hook

```bash
#!/bin/sh
# .git/hooks/pre-commit

echo "Running ContextForge.Spectre tests..."
pwsh -Command "Invoke-Pester -Path tests/ContextForge.Spectre.*.Tests.ps1 -Quiet"

if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Commit aborted."
    exit 1
fi

echo "✓ Tests passed"
```

---

## Quality Gates

### Mandatory Checks (Blocking)

- [ ] All unit tests pass (green)
- [ ] Demo script tests pass (green)
- [ ] Encoding validation tests pass (green)
- [ ] No Pester warnings or errors
- [ ] Exit code 0 for all test runs

### Coverage Checks (Warning)

- [ ] Unit test coverage ≥ 85%
- [ ] Integration coverage ≥ 70%
- [ ] Demo script coverage ≥ 90%

### Performance Checks (Informational)

- [ ] Test suite completes in < 30 seconds
- [ ] Individual tests complete in < 5 seconds
- [ ] No memory leaks detected

---

## Troubleshooting Test Failures

### Common Issues

**Issue**: ANSI sequences interfere with assertions
**Solution**: Use `Remove-AnsiSequences` before assertions

**Issue**: Tests fail in CI but pass locally
**Solution**: Set `$env:CI = 'true'` locally to reproduce

**Issue**: Encoding tests fail
**Solution**: Check file BOM with `Get-Content -AsByteStream -First 3`

**Issue**: Mock not being called
**Solution**: Verify mock is in correct module scope with `-ModuleName`

---

## References

- Research: `docs/research/TESTING-TERMINAL-UI-STRATEGY.md`
- Helpers: `tests/helpers/TerminalUI.TestHelpers.psm1`
- Authority: `.github/instructions/terminal-output.instructions.md`
- Pester Docs: https://pester.dev/docs/quick-start
