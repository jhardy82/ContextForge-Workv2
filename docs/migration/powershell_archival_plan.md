# PowerShell Core Script Archival Plan (Draft)

Status: Draft (2025-08-25)

## Scope
Identify non-essential PowerShell scripts slated for deprecation in favor of Python equivalents while retaining SCCM / host-specific shims.

## Candidate Scripts (Initial Enumeration)
- scripts/Migrate-TasksToArrayRoot.ps1 (Python replacement present)
- scripts/Invoke-GovernanceFullSuite.ps1 (future Python governance orchestrator planned)
- build/Run-PesterTests.ps1 (retain short-term for legacy tests; mark read-only post Python test runner)
- build/Invoke-PSSA-Mode.ps1 (Python lint surrogate TBD; keep until parity design)

## Sequencing
1. Dual-run parity (in-progress) -> green runs ≥2
2. Tag files with `# DEPRECATED` header referencing Python replacement
3. Archive move to `/archive` or subfolder with README pointer
4. Remove after one sprint of zero-diff governance results

## Rollback Strategy
Retain original file hash in artifact_emit event; restore from git history if Python gate fails.

## Open Items
- Define Python governance orchestrator CLI spec
- Implement Python PSSA-equivalent lint coverage or integrate existing analyzer via wrapper
- Add metrics emission for parity harness executions
