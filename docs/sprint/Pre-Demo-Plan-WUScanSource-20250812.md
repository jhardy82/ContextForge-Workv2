# Pre-Demo Action Plan: Get-WUScanSource (2025-08-12)

Goal: Close Learn-backed gaps, keep tests green, and prep a tight demo.

## Scope
- File: `SCCM/Get-WUScanSource.ps1`
- Tests: `tests/SCCM.Get-WUScanSource.*.Tests.ps1`
- Docs: `docs/reference/Windows-Update-ScanSource-Research-20250812.md`

## Status Summary (as of 2025-08-12)
- Analyzer clean (scoped) for target script and harness; repo-wide cleanup ongoing
- Harness implemented with JSONL audit, progress, and artifact verification
- Evidence export produces JSON/CSV/Markdown, reg exports, gpresult, events, and hash manifest
- Learn-backed conflict taxonomy and URL mapping integrated; local run shows WUfB (MDM CSP) with no conflicts
- Evidence validator implemented and wired into harness post-export

## Tasks (with status)
1. Add new flags and evidence — Done
    - PublicOnlineBlocked:
       `HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\DoNotConnectToWindowsUpdateInternetLocations = 1`
    - WUUXBlocked: `DisableWindowsUpdateAccess` (ADMX_ICM) or `SetDisableUXWUAccess` (CSP)
    - ScanSourceRegistryCaveat:
       `SetPolicyDrivenUpdateSource*` via registry without `UseUpdateClassPolicySource`
    - MUDeferralBypass: `AllowMUUpdateService=1` with WSUS configured
    - Proxy/TLS signals:
       `SetProxyBehaviorForUpdateDetection`, `DoNotEnforceEnterpriseTLSCertPinningForUpdateDetection`;
       compare with WinHTTP proxy

2. OS-aware defaults — Partial
   - Implemented in `Resolve-ScanSource` heuristics; add explicit tests to validate:
     - Win10: WSUS + deferrals (no scan-source, DualScan not set) → WU; with DisableDualScan=1 → WSUS
     - Win11: WSUS + no scan-source → WSUS

3. Evidence enrichment — Done
   - TRV/ProductVersion pair validation; BranchReadiness/ManagePreviewBuilds surfaced;
     Pause/Defer/DisableWUfBSafeguards/ExcludeWUDrivers captured

4. Tests — In progress
   - Extend Matrix + MockScenarios for each new condition and OS-default behaviors
   - Keep runs focused to WU suites
   - Add coverage for Learn URL mapping and conflict codes

5. PSSA style pass (no behavior change) — Done (scoped)
   - Replaced Write-Host; filled catch blocks; normalized spacing/long lines
   - Repo-wide reductions continue via batch formatting

6. Demo pack — Planned
   - 5 mock scenarios: WSUS, WU, DualScanRisk, PublicOnlineBlocked, Invalid WSUS URL, MU under WSUS
   - Evidence bundles (JSON/CSV/JSONL) + summary strings

## New Tasks (added 2025-08-12)
- [x] Implement PS 5.1 harness with context object, temp captures, progress, JSONL, and artifact checks
- [x] Add VS Code task: “Quality: Run WUScanSource Harness” (runs `build/Run-WUScanSourceHarness.ps1`)
- [x] Evidence bundle validator script (required files present, non-empty, hashes verified)
- [x] Scoped PSSA gate for `SCCM/Get-WUScanSource.ps1` and `build/Run-WUScanSourceHarness.ps1`
- [ ] Expand Pester tests for:
  - Dual-scan detection
  - WSUS URL hardening
  - Driver exclusion
  - MDM CSP vs GPO precedence
  - Learn URL mapping
- [ ] Minimal README for usage (how to run, interpret `scan.json`/`Summary.md`, evidence locations)
- [ ] Optional focused quality chain task: Env Check → Fix Pester Conflicts → Static (scoped) → Tests (focused) → View Results

## Acceptance Criteria
- New flags appear with correct provenance; focused tests PASS (including Learn URL mapping and OS-default behaviors)
- PSSA: 0 errors for target and harness; repo-wide warnings trending down
- Evidence bundle validator passes for a harness run; mismatch yields actionable errors
- VS Code task for harness available in Task Runner, and produces artifacts under
   `Outputs/WUScanSource/LocalRun-<ts>` and `logs/WUScanSource/`

## References
- Learn: WUfB vs WSUS, Update CSP, WSUS GPOs, Autopatch conflicts (see research doc)
