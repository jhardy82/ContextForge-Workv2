# HostPolicy Tagging Guide

This guide explains how to classify PowerShell scripts using the required `# HostPolicy:` header.

## Policies

| Policy       | Use Case                                        | Notes                                                        |
| ------------ | ----------------------------------------------- | ------------------------------------------------------------ |
| ModernPS7    | New & modernized scripts (prefer PowerShell 7+) | May use PS7-only constructs (parallel, `??`, `\&\&`, `\|\|`) |
| LegacyPS51   | Module constraint (e.g., ConfigurationManager)  | Add `# HostFallbackReason:` with justification               |
| DualHost     | Must run under both 5.1 and 7+                  | Avoid PS7-only syntax; validate in both hosts                |
| PythonHelper | Python-oriented helper wrapper                  | Prefer direct python invocation when possible                |

## Placement

Add within the first 20 lines (ideally top 5). Example:

```powershell
#!/usr/bin/env pwsh
# HostPolicy: ModernPS7
```

Legacy fallback example:

```powershell
# HostPolicy: LegacyPS51
# HostFallbackReason: SCCM ConfigurationManager module not PS7-compatible
```

## Selection Heuristics

- Contains SCCM / ConfigMgr cmdlets → LegacyPS51
- Performs cross-host orchestration with no PS7 features → DualHost
- Otherwise → ModernPS7

## Remediation Workflow

1. Generate audit: `pwsh scripts/Generate-HostPolicyAudit.ps1`
2. Apply tags to priority directories:
   - build/
   - scripts/
   - src/core/Public/
   - cli/
3. Use automation: `pwsh scripts/Apply-HostPolicyTags.ps1 -Max 100`
4. Re-run audit; iterate until coverage ≥ 80% (stretch goal) – minimum enforced: 50%.

## Automation Script

`scripts/Apply-HostPolicyTags.ps1` performs prioritized tagging and can infer LegacyPS51 for SCCM-related scripts.

Dry-run:

```powershell
pwsh scripts/Apply-HostPolicyTags.ps1 -WhatIf -Max 25 -VerboseList
```

Apply first 120 untagged (default ModernPS7):

```powershell
pwsh scripts/Apply-HostPolicyTags.ps1 -Max 120
pwsh scripts/Generate-HostPolicyAudit.ps1
```

## Governance Test

`tests/governance/HostPolicyCoverage.Tests.ps1` enforces ≥50% coverage.

## Next Steps

- After reaching 50%, focus on SCCM / module-constrained scripts classification.
- Track coverage trend in future governance metrics.
