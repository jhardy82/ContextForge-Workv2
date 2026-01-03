# Governance Chain Safeguards

This repository includes lightweight governance health checks to ensure a
summary artifact is always produced even under failure or timeout conditions.

## Artifacts

`build/artifacts/governance/chain_summary.json` – Emitted by
`Emit-ChainSmokeSummary.ps1` (status `smoke_pass` by default) or via
`Invoke-GovernanceChain.ps1` (which may emit `timeout`).

## Scripts

- `build/Emit-ChainSmokeSummary.ps1` – Idempotent summary emitter with optional
  `-Status` parameter.
- `build/Invoke-GovernanceChain.ps1` – Wraps governance work with a timeout; on
  exceed emits a timeout summary.

## Tests

- `tests/Governance.Smoke.Tests.ps1` – Verifies emitter and CLI list basic path.
- `tests/Governance.Timeout.Tests.ps1` – Forces timeout to validate safeguard.

## Usage

```powershell
pwsh ./build/Emit-ChainSmokeSummary.ps1              # Smoke pass
pwsh ./build/Invoke-GovernanceChain.ps1 -TimeoutSeconds 5 -SimulatedWorkSeconds 10  # Timeout example
```

## Compliance

Aligns with Logging First principle by emitting an `artifact_emit` JSON line and
timeout/complete events for observability.
