# YAML Indentation Policy

Two-space indentation with ZERO tab characters is mandated for all YAML governance artifacts.

## Scope
- trackers/*.yaml (ledger, coverage, multiplicity, missing catalog, tasks, digest, metrics)
- docs/*.yaml (future)

## Tooling
- `scripts/Normalize-YamlIndentation.ps1` (logging, remediation, check mode, CI friendly)
- `scripts/Replace-YamlTabs.ps1` (lightweight, optional leading-only mode)

## CI/Test Gate
- Pester test `tests/quality/IndentationCompliance.Tests.ps1` fails build if any tab ("\t") is present.

## Developer Workflow
1. Check: `pwsh ./scripts/Normalize-YamlIndentation.ps1 -CheckOnly`
2. Fix: `pwsh ./scripts/Normalize-YamlIndentation.ps1`
3. Re-run tests; commit after zero-tab confirmation.

## Pre-commit Hook (optional)
Add `.githooks/pre-commit` and enable via:

```pwsh
git config core.hooksPath .githooks/
```

## Rationale
- Prevents hidden diffs & merge conflicts.
- Guarantees consistent parsing across tooling.
- Simplifies future semantic indentation validation.

## Future Enhancements
- Semantic indentation validator (anchor alignment).
- Integration with evidence logging for hygiene metrics.
