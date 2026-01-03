# TaskMan Health Enhancement Specification

**Version**: 1.0.0
**Last Updated**: 2025-12-29
**Status**: Ready for Implementation

---

## Executive Summary

The `Test-TaskManHealth.ps1` script is well-designed with zero external dependencies. This document specifies adding dual-mode output (human-readable + JSON) for CI/automation integration.

## Current State Analysis

### Script Metrics

| Metric | Value |
|--------|-------|
| Total Lines | 406 |
| Functions | 6 |
| Health Checks | 11 |
| External Dependencies | **0** (profile-free) |

### Exit Code Semantics

| Code | Status | Meaning |
|------|--------|---------|
| 0 | Healthy | All checks passed |
| 1 | Degraded | Some checks failed, system operational |
| 2 | Critical | Core services unavailable |

### Current Function Structure

```powershell
# Existing functions (preserve all)
Test-DatabaseConnection
Test-BackendApiHealth
Test-McpServerHealth
Test-FrontendHealth
Test-NetworkConnectivity
Get-HealthSummary
```

## Enhancement: Dual-Mode Output

### Parameter Addition

```powershell
[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet('Text', 'JSON', 'Both')]
    [string]$OutputFormat = 'Text',

    [Parameter()]
    [switch]$Quiet,

    [Parameter()]
    [string]$OutputPath
)
```

### JSON Output Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "TaskMan Health Report",
  "type": "object",
  "properties": {
    "timestamp": { "type": "string", "format": "date-time" },
    "version": { "type": "string" },
    "overall_status": { "enum": ["healthy", "degraded", "critical"] },
    "exit_code": { "type": "integer", "minimum": 0, "maximum": 2 },
    "duration_ms": { "type": "number" },
    "checks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "category": { "type": "string" },
          "status": { "enum": ["pass", "warn", "fail", "skip"] },
          "message": { "type": "string" },
          "duration_ms": { "type": "number" },
          "details": { "type": "object" }
        }
      }
    },
    "summary": {
      "type": "object",
      "properties": {
        "total": { "type": "integer" },
        "passed": { "type": "integer" },
        "warnings": { "type": "integer" },
        "failed": { "type": "integer" },
        "skipped": { "type": "integer" }
      }
    }
  }
}
```

### Implementation

```powershell
#region Health Check Result Type
class HealthCheckResult {
    [string]$Name
    [string]$Category
    [ValidateSet('pass', 'warn', 'fail', 'skip')]
    [string]$Status
    [string]$Message
    [double]$DurationMs
    [hashtable]$Details = @{}

    HealthCheckResult([string]$name, [string]$category) {
        $this.Name = $name
        $this.Category = $category
    }
}
#endregion

#region Check Wrapper
function Invoke-HealthCheck {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Name,

        [Parameter(Mandatory)]
        [string]$Category,

        [Parameter(Mandatory)]
        [scriptblock]$Check
    )

    $result = [HealthCheckResult]::new($Name, $Category)
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

    try {
        $checkResult = & $Check
        $stopwatch.Stop()
        $result.DurationMs = $stopwatch.Elapsed.TotalMilliseconds

        if ($checkResult.Success) {
            $result.Status = 'pass'
            $result.Message = $checkResult.Message ?? 'Check passed'
        } else {
            $result.Status = if ($checkResult.Critical) { 'fail' } else { 'warn' }
            $result.Message = $checkResult.Message ?? 'Check failed'
        }

        if ($checkResult.Details) {
            $result.Details = $checkResult.Details
        }
    }
    catch {
        $stopwatch.Stop()
        $result.DurationMs = $stopwatch.Elapsed.TotalMilliseconds
        $result.Status = 'fail'
        $result.Message = "Exception: $($_.Exception.Message)"
        $result.Details = @{
            exception_type = $_.Exception.GetType().Name
            stack_trace    = $_.ScriptStackTrace
        }
    }

    return $result
}
#endregion

#region Output Formatters
function Format-HealthReportText {
    param([array]$Results, [hashtable]$Summary, [string]$OverallStatus)

    $statusEmoji = @{
        'pass' = '✓'
        'warn' = '⚠'
        'fail' = '✗'
        'skip' = '○'
    }

    $output = @()
    $output += "=" * 60
    $output += "TaskMan Health Report - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    $output += "=" * 60
    $output += ""

    # Group by category
    $grouped = $Results | Group-Object Category
    foreach ($group in $grouped) {
        $output += "[$($group.Name)]"
        foreach ($check in $group.Group) {
            $emoji = $statusEmoji[$check.Status]
            $output += "  $emoji $($check.Name): $($check.Message) ($([math]::Round($check.DurationMs, 1))ms)"
        }
        $output += ""
    }

    # Summary
    $output += "-" * 60
    $output += "Summary: $($Summary.passed)/$($Summary.total) passed, $($Summary.warnings) warnings, $($Summary.failed) failed"
    $output += "Overall Status: $($OverallStatus.ToUpper())"
    $output += "=" * 60

    return $output -join "`n"
}

function Format-HealthReportJson {
    param(
        [array]$Results,
        [hashtable]$Summary,
        [string]$OverallStatus,
        [int]$ExitCode,
        [double]$DurationMs
    )

    $report = @{
        timestamp      = (Get-Date -Format 'o')
        version        = '1.0.0'
        overall_status = $OverallStatus
        exit_code      = $ExitCode
        duration_ms    = [math]::Round($DurationMs, 2)
        checks         = $Results | ForEach-Object {
            @{
                name        = $_.Name
                category    = $_.Category
                status      = $_.Status
                message     = $_.Message
                duration_ms = [math]::Round($_.DurationMs, 2)
                details     = $_.Details
            }
        }
        summary        = $Summary
    }

    return $report | ConvertTo-Json -Depth 10
}
#endregion

#region Main Execution
function Invoke-TaskManHealthCheck {
    [CmdletBinding()]
    param(
        [ValidateSet('Text', 'JSON', 'Both')]
        [string]$OutputFormat = 'Text',

        [switch]$Quiet,

        [string]$OutputPath
    )

    $totalStopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $results = @()

    # Run all health checks
    $results += Invoke-HealthCheck -Name 'PostgreSQL Connection' -Category 'Database' -Check {
        Test-DatabaseConnection
    }

    $results += Invoke-HealthCheck -Name 'Backend API' -Category 'Services' -Check {
        Test-BackendApiHealth
    }

    $results += Invoke-HealthCheck -Name 'MCP Server' -Category 'Services' -Check {
        Test-McpServerHealth
    }

    $results += Invoke-HealthCheck -Name 'Frontend' -Category 'Services' -Check {
        Test-FrontendHealth
    }

    $results += Invoke-HealthCheck -Name 'Network' -Category 'Infrastructure' -Check {
        Test-NetworkConnectivity
    }

    # Calculate summary
    $totalStopwatch.Stop()
    $summary = @{
        total    = $results.Count
        passed   = ($results | Where-Object Status -eq 'pass').Count
        warnings = ($results | Where-Object Status -eq 'warn').Count
        failed   = ($results | Where-Object Status -eq 'fail').Count
        skipped  = ($results | Where-Object Status -eq 'skip').Count
    }

    # Determine overall status and exit code
    $overallStatus = 'healthy'
    $exitCode = 0

    if ($summary.failed -gt 0) {
        $criticalChecks = $results | Where-Object { $_.Status -eq 'fail' -and $_.Category -in @('Database', 'Services') }
        if ($criticalChecks) {
            $overallStatus = 'critical'
            $exitCode = 2
        } else {
            $overallStatus = 'degraded'
            $exitCode = 1
        }
    } elseif ($summary.warnings -gt 0) {
        $overallStatus = 'degraded'
        $exitCode = 1
    }

    # Output based on format
    $textOutput = Format-HealthReportText -Results $results -Summary $summary -OverallStatus $overallStatus
    $jsonOutput = Format-HealthReportJson -Results $results -Summary $summary -OverallStatus $overallStatus `
                                          -ExitCode $exitCode -DurationMs $totalStopwatch.Elapsed.TotalMilliseconds

    switch ($OutputFormat) {
        'Text' {
            if (-not $Quiet) { Write-Host $textOutput }
        }
        'JSON' {
            if (-not $Quiet) { Write-Output $jsonOutput }
        }
        'Both' {
            if (-not $Quiet) {
                Write-Host $textOutput
                Write-Host "`n--- JSON Output ---`n"
                Write-Output $jsonOutput
            }
        }
    }

    # Write to file if requested
    if ($OutputPath) {
        if ($OutputFormat -eq 'JSON' -or $OutputFormat -eq 'Both') {
            $jsonOutput | Out-File -FilePath $OutputPath -Encoding utf8
        } else {
            $textOutput | Out-File -FilePath $OutputPath -Encoding utf8
        }
    }

    exit $exitCode
}
#endregion
```

## Usage Examples

```powershell
# Default: Human-readable text output
./Test-TaskManHealth.ps1

# JSON for CI pipelines
./Test-TaskManHealth.ps1 -OutputFormat JSON

# Both formats (debugging)
./Test-TaskManHealth.ps1 -OutputFormat Both

# Quiet mode with file output for monitoring
./Test-TaskManHealth.ps1 -OutputFormat JSON -Quiet -OutputPath "./health-report.json"

# In GitHub Actions
- name: Health Check
  run: |
    $result = ./Test-TaskManHealth.ps1 -OutputFormat JSON
    echo "health_report=$result" >> $env:GITHUB_OUTPUT
  shell: pwsh
```

## CI Integration

### GitHub Actions Example

```yaml
- name: TaskMan Health Check
  id: health
  run: |
    ./Test-TaskManHealth.ps1 -OutputFormat JSON -OutputPath health.json
  shell: pwsh
  continue-on-error: true

- name: Upload Health Report
  uses: actions/upload-artifact@v4
  with:
    name: health-report
    path: health.json

- name: Fail on Critical
  if: steps.health.outcome == 'failure'
  run: |
    $report = Get-Content health.json | ConvertFrom-Json
    if ($report.exit_code -eq 2) {
      throw "Critical health check failure"
    }
  shell: pwsh
```

## Implementation Checklist

- [ ] Add `$OutputFormat` parameter
- [ ] Create `HealthCheckResult` class
- [ ] Implement `Invoke-HealthCheck` wrapper
- [ ] Add `Format-HealthReportText` function
- [ ] Add `Format-HealthReportJson` function
- [ ] Update main execution flow
- [ ] Add `-OutputPath` for file output
- [ ] Add `-Quiet` for silent operation
- [ ] Test in CI pipeline
- [ ] Update documentation

## Backward Compatibility

All existing behavior is preserved:
- Default output remains human-readable text
- Exit codes unchanged (0, 1, 2)
- No new external dependencies
- Profile-free execution maintained

---

*"Health checks should speak both human and machine."*
