# CF_CORE Audit — Structured Inventory (Unique Counts + Citations)

Generated: 2025-11-10

## 1) Python CLIs (Primary + Specialized)

- Primary (1)
  - `c:\Users\james.e.hardy\Documents\PowerShell Projects\cf_cli.py`
- Specialized (4)
  - `c:\Users\james.e.hardy\Documents\PowerShell Projects\dbcli.py`
  - `c:\Users\james.e.hardy\Documents\PowerShell Projects\tasks_cli.py`
  - `c:\Users\james.e.hardy\Documents\PowerShell Projects\sprints_cli.py`
  - `c:\Users\james.e.hardy\Documents\PowerShell Projects\projects_cli.py`

## 2) PowerShell Wrappers / Operators (invoke cf_cli.py)

- 8 unique invocation points (representative citations):
  - `scripts\Deploy-CFEnhancedCLI.ps1`
  - `scripts\Invoke-CFEnhancedWorkflow.ps1`
  - `scripts\cf_cli_clean.ps1`
  - `scripts\cf-cli.ps1`
  - `scripts\bulk-create-missing-tasks.ps1`
  - `Test-TaskManagerDTMTracking.ps1`
  - `Deploy-DTM-Native.ps1`
  - `update_pending_tasks.ps1`

## 3) Subsystem / Bridge CLIs (Node/TypeScript)

- TaskMan‑v2 CLI
  - `TaskMan-v2\cli\package.json` ("bin": "taskman")
  - `TaskMan-v2\cli\bin\run.js`
  - `TaskMan-v2\cli\bin\dev.js`
- CF_CLI Bridge
  - `vs-code-task-manager\mcp-cfcli-bridge.js` (shebang)
- Test Harness CLIs (excluded from CF_CORE counts)
  - `TaskMan-v2\src\test\run-tests.ts`
  - `TaskMan-v2\src\test\run-comprehensive-tests.ts`
  - `TaskMan-v2\validate-tests.js`
  - `vs-code-task-manager\test-*.js`

## 4) .QSE Inventory

- v2 top-level directories (8)
  - `artifacts/`, `Evidence/`, `Indexes/`, `Research/`, `Sessions/`, `shadow/`, `Sync/`, `TaskMan-v2/`
  - Index file: `QSE-INDEX.yaml`
- v1 top-level directories (4)
  - `artifacts/`, `evidence/`, `sessions/`, `scripts/`
  - Index file: `QSE-INDEX.yaml`

## 5) Migration Artifacts (exact paths)

- Integration Guides (3 unique logical files)
  - `.QSE\v2\artifacts\P-CF-SPECTRE-001\IntegrationGuide.TaskMan-CF_CORE-UTMW.20251107-0125.yaml`
  - `.QSE\v2\artifacts\P-CF-SPECTRE-001\IntegrationGuide.TaskMan-CF_CORE-UTMW.20251107-1530.yaml`
  - `.QSE\v2\artifacts\P-CF-SPECTRE-001\IntegrationGuide.P-CF-SPECTRE-001.20251107-PHASE1-2.yaml`
- Deprecation Log (1 unique)
  - `.QSE\v2\artifacts\P-CF-SPECTRE-001\DeprecationLog.IntegrationGuide.P-CF-SPECTRE-001.20251110.yaml`

## 6) Negative Findings

- External authoritative CF_CORE specification: not found
- Expected auxiliary CLIs (name candidates) absent: `simple_cli.py`, `working_cli.py`

## 7) Classification Rollup

- Primary: `cf_cli.py` — Active (Bridge coexists with TaskMan‑v2)
- Specialized: `dbcli.py`, `tasks_cli.py`, `sprints_cli.py`, `projects_cli.py` — Active
- Wrappers: PowerShell scripts invoking `cf_cli.py` — Active
- Subsystem CLI: TaskMan‑v2 CLI ("taskman") — Active
- Bridge: `mcp-cfcli-bridge.js` — Active (integration)
- Legacy: None confirmed (CF_CORE Python CLI appears active; deprecation status not indicated by artifacts)

## 8) Confidence Ledger

- High: Python CLIs presence/role; PS wrapper function; TaskMan‑v2 CLI; QSE directory sets; migration artifact filenames
- Medium‑High: Bridge role of `mcp-cfcli-bridge.js` inferred by naming and location
- Medium: CF_CORE deprecation status — pending reading deprecation log content for explicit statements

## 9) Notes on Counting Policy

- IntegrationGuide counted as unique logical files (timestamps distinguished but grouped by filename family)
- Test harness CLIs excluded from CF_CORE CLI counts
- `.QSE\v2\shadow` and `.QSE\v2\TaskMan-v2` treated as adjunct subtrees under v2

## 10) Next Steps

- QA vibe_check on counts and classification
- Produce final 10‑section report
