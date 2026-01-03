# Test Suite Audit & Remediation

## Overview
A structured hygiene audit was introduced to baseline and iteratively improve the PowerShell Pester test suite.
The guiding principle: **assume every test is incomplete until proven otherwise**.
Automation now supplies objective evidence, enabling phased, low-risk refactors.

## Tools Introduced

| Artifact | Purpose | Notes |
|----------|---------|-------|
| `scripts/Audit-TestSuite.ps1` | Static scanner over `tests/` | Emits JSON + Markdown summaries (`logs/test-audit/`) with categorized issues |
| `scripts/Apply-TestMetadataFixes.ps1` | Phase 1 automated remediation | Adds HostPolicy tag, Shape/Stage metadata block, explicit `Import-Module Pester` |
| `scripts/Generate-TestIsolationPatchSuggestions.ps1` | Phase 2 preparation | Produces non‑destructive isolation suggestion scripts per impacted test |
| `logs/test-audit/*summary*.json` | Baseline + delta metrics | Schema `taskdb.tests.audit.v1` |
| `logs/test-audit/isolation_suggestions/` | Refactor scaffolds | One file per isolation candidate + manifest |

## Issue Categories (Audit)

| Category | Description | Phase |
|----------|-------------|-------|
| `missing_hostpolicy_tag` | Absent `# HostPolicy:` header | 1 (resolved) |
| `missing_shape_stage_metadata` | Missing Shape/Stage .NOTES block | 1 (mostly resolved) |
| `missing_pester_import` | No explicit `Import-Module Pester` guard | 1 (resolved) |
| `missing_negative_variant` | Lacks failure/edge counterpart | 3 |
| `direct_fs_write_outside_testdrive` | Writes / path logic against repo disk instead of `$TestDrive` | 2 |
| `env_var_mutation` | Direct `$env:` modification without backup/restore | 2 |
| `uses_sleep` | `Start-Sleep` usages (flakiness risk) | 2 |
| `no_assertions` | 0 Should assertions in Describe/Context (rare) | Backlog |
| `excessive_sleep_duration` | Sleep > threshold (future refinement) | Backlog |

## Phase 1 Results (Metadata & Imports)
Baseline (2025-08-19 23:42:33Z) vs Post-Remediation (2025-08-20 00:12:10Z):

| Metric | Baseline | After | Delta |
|--------|----------|-------|-------|
| Files scanned | 114 | 114 | — |
| Files with issues | 108 | 81 | -27 (−25.0%) |
| missing_hostpolicy_tag | 87 | 0 | -87 (100%) |
| missing_pester_import | 86 | 0 | -86 (100%) |
| missing_shape_stage_metadata | 95 | 7 | -88 (−92.6%) |

Residual `missing_shape_stage_metadata` files lack a Pester `Describe` block or require manual classification.

## Phase 2 Plan (Isolation & Timing)
Focus: deterministic, isolated, and faster tests.

1. File System Isolation
   - Replace repo-root discovery + direct `Join-Path` writes with `$TestDrive` scaffolds.
   - Provide synthetic structure when tests depend on relative paths (e.g. `build/`, `logs/`).
2. Environment Variable Hygiene
   - Introduce helper pair: `Set-TestEnvVar` (records original) + `Restore-TestEnvVars` (AfterAll hook).
3. Sleep Replacement
   - Convert fixed `Start-Sleep` to polling helper `Wait-Until { <condition> }` with timeout.
4. Negative Variant Generation
   - For each positive test group lacking a failure path, scaffold `Context 'Negative'` with explicit expectation (error code, thrown message, or sentinel log event).

### Isolation Suggestion Artifacts
`Generate-TestIsolationPatchSuggestions.ps1` produced 60 per-file suggestion scripts containing:
- Observed direct FS lines (annotated)
- Replacement `$TestDrive` snippet
- Env var mutation replacement helpers
- Polling helper template when `uses_sleep` present

These are stored under `logs/test-audit/isolation_suggestions/` with a manifest `isolation_manifest.json` (enumerating issues + counts per test).

## Refactor Strategy

| Step | Action | Safety Mechanism |
|------|--------|------------------|
| 1 | Apply FS isolation to highest churn tests first | Commit in small batches, re-run audit |
| 2 | Add env helpers globally (shared snippet) | Idempotent function guards |
| 3 | Replace sleeps (≤1 per PR) | Fail fast on timeout to highlight fragile logic |
| 4 | Add negative variants | Leverage existing positive fixtures; assert distinct failure signals |
| 5 | Introduce CI Gate | Fail build if regression in resolved categories |

## Potential CI Gate (Draft)
- Run audit; fail if any regression in Phase 1 categories or net increase in `uses_sleep`.
- Warn (not fail) on unchanged Phase 2 categories until thresholds reached.

## Helpers (Proposed Snippets)

```powershell
# Env var hygiene
if (-not (Get-Variable -Name __EnvBackup -Scope Script -ErrorAction SilentlyContinue)) { $script:__EnvBackup = @{} }
function Set-TestEnvVar { param([string]$Name,[string]$Value) if (-not $script:__EnvBackup.ContainsKey($Name)) { $script:__EnvBackup[$Name] = (Get-Item env:$Name -ErrorAction SilentlyContinue)?.Value }; $env:$Name = $Value }
function Restore-TestEnvVars { foreach ($k in $script:__EnvBackup.Keys) { if ($script:__EnvBackup[$k]) { $env:$k = $script:__EnvBackup[$k] } else { Remove-Item env:$k -ErrorAction SilentlyContinue } } }
AfterAll { Restore-TestEnvVars }

# Polling helper
function Wait-Until { param([scriptblock]$Condition,[int]$TimeoutSeconds=5,[int]$IntervalMs=100)
  $sw=[Diagnostics.Stopwatch]::StartNew()
  while($sw.Elapsed.TotalSeconds -lt $TimeoutSeconds){ if (& $Condition){ return $true }; Start-Sleep -Milliseconds $IntervalMs }
  throw "Condition not met within $TimeoutSeconds seconds"
}
```

## Metrics & Evidence Evolution
Future enhancements:
- Track mean test duration pre/post sleep refactors.
- Emit coverage metric: percentage of tests declaring Shape/Stage.
- Negative variant adoption rate (variants / eligible positive contexts).

## Open Questions
- Standardize synthetic repo layout fixture? (Could reduce per-test boilerplate.)
- Introduce lint rule enforcing `Wait-Until` over `Start-Sleep`?
- Threshold for env var mutation warnings vs failures.

## Next Steps (If Approved)
1. Implement env helper snippet centrally; re-run audit to ensure no raw `$env:` writes remain in modified files.
2. Batch convert 5 logging-related tests to `$TestDrive`; measure delta.
3. Replace sleeps in those tests; confirm no flakiness.
4. Scaffold negative variant for one representative logging command (baseline pattern).
5. Draft CI gate script wrapping audit + regression rules.

---
*This document will be updated after completing Phase 2 isolation refactors or if audit schema evolves.*
