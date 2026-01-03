# Development Environment Modernization

Goal: Use modern tooling (PowerShell 7, Python where appropriate) to orchestrate and accelerate development while keeping production outputs and scripts compatible with Windows PowerShell 5.1 (enterprise operational baseline).

## Principles
- Operational Baseline: All production / infrastructure / SCCM automation must execute under Windows PowerShell 5.1.
- Development Acceleration: PowerShell 7 enables parallelism (future), faster JSON, richer diagnostics.
- Parity First: Optimize only after establishing artifact parity & integrity hash stability across engines.
- Logging First: All new tooling emits structured JSONL; PS7 does not change log schema.
- Single Source Sanitization: RunId sanitation centralized (build/RunId-Utils.ps1).

## New Tools
- Background watcher: `cli/Watch-BackgroundTasks.ps1`
- Background helpers module: `build/Background-Tasks.psm1`
- Starters (pwsh orchestration): `cli/Start-Pester-Detached.ps1`, `cli/Start-PSSA-Detached.ps1`

## Typical Workflow (Dual-Engine Aware)
1. Start watcher under PowerShell 7 (task: Background: Watch-BackgroundTasks (pwsh)).
2. Kick off a background run with tasks:
   - Pester: Start: Pester Detached (pwsh)
   - PSSA: Start: PSSA Detached (pwsh, All)
3. Watcher will move descriptors from `docs/context/monitor/pending/` to `completed/` or `failed/` and log to `logs/background-monitor.jsonl`.
4. (Planned) Run key generators under both engines to confirm parity before merging major governance changes.

## New Governance Artifacts (2025-08-15)
- variety_alerts.json: Diversity threshold evaluation (codes: LOW_SHAPE_DIVERSITY, CLASS_MONOCULTURE_RUN)
- chain_summary_integrity.json: SHA256 hash over stable planning fields enabling drift detection

## Engine Guard Pattern

```powershell
$IsPwsh7 = $PSVersionTable.PSVersion.Major -ge 7
if ($IsPwsh7) {
   # Optional optimized branch
} else {
   # Baseline authoritative logic
}
```

## Parity Validation Strategy (Planned)
- Normalize JSON (remove timestamp/run_id) then diff.
- Verify integrity hash identical across engines for unchanged inputs.
- Fail CI if drift detected.

## Notes
- Existing wrappers remain unchanged; optimization is additive.
- Expected artifacts validated before task success.
- Extend pattern to WU harness, signing, or future compliance scans.
- Upcoming: JSON schema enforcement for variety_alerts & chain_summary_integrity.
