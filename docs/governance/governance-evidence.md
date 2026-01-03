# Governance Evidence & Logging Coverage (Pass 1)

## Overview
Pass 1 establishes baseline instrumentation and evidence aggregation without enforcing new quality gates by default.

## Evidence Manifest
Location: `build/artifacts/governance/evidence-manifest.json`
Schema: `governance.evidence.manifest.v1`
Fields:
- schema
- generated_utc (ISO8601)
- artifact_count
- artifacts[]: path, role, sha256 (SHA256 hex), bytes

Current Roles (expected ≥7):
- anchor_map
- rules_inventory
- governance_events
- host_policy_report
- modernization_report
- progress_summary
- logging_coverage (latest)

## Logging Coverage Assessment
Script: `scripts/Assess-LoggingCoverage.ps1`
Output: `logs/logging_coverage/logging_coverage_*.json`
Key fields: status (PASS / PASS_WITH_GAPS / FAIL), events_emitted, required_minimum.

Statuses:
- PASS: Core minimum emitted for every assessed session, no gaps.
- PASS_WITH_GAPS: Core present, extended recommended events missing.
- FAIL: One or more sessions missing a core required event.

## Optional Gate (Disabled by Default)
`Invoke-GovernanceFullSuite.ps1` now supports `-FailOnLoggingCoverage`. When supplied and coverage status == FAIL, exit code 3 is returned.

## Next Pass (Planned)
Pass 2 will add: freshness check (coverage report timestamp alignment), regression guard for artifact count growth, optional promotion of PASS_WITH_GAPS to warning.
Pass 3 will enable gate in CI once stability confirmed.

## Troubleshooting
- Manifest empty (artifact_count=0): Ensure suite completed and roles files exist; verify script scope fix (Add-Art uses $script:artifacts).
- Missing logging_coverage role: Run full suite; confirm Assess-LoggingCoverage script produced latest JSON.

## Change Log Reference
Added in CHANGELOG under Unreleased: Evidence manifest & advisory logging coverage (Pass 1 foundation).
