
## Appendix C — Risk Register (REM‑003)

This appendix summarizes the risk register maintained at `.QSE/v2/Indexes/Risks.index.yaml`.

Model
- Severity weights: Critical=4, High=3, Moderate=2, Low=1
- Likelihood weights: High=3, Medium=2, Low=1
- Formula: riskScore = severityWeight × likelihoodWeight

Aggregated Stats (as of 2025‑11‑10)
- Total risks: 13
- Score distribution: 6→5, 4→7, 2→1
- Highest score: 6; Lowest score: 2
- High‑score risks (6): R‑001, R‑005, R‑007, R‑008, R‑012

High‑Priority Risk → Ticket Links
- R‑001 (No external CF_CORE spec; surrogate authority risk) → REM‑015
- R‑005 (cf_cli breaking changes lack deprecation gates) → REM‑018
- R‑007 (Virtualenv activation inconsistency) → REM‑019
- R‑008 (TaskMan‑v2 API divergence from cf_cli contract) → REM‑017
- R‑012 (CF_CORE CLI surrogate spec not published) → REM‑015

Additional Links
- R‑002 → REM‑001, REM‑002
- R‑003 → REM‑002
- R‑004 → REM‑017
- R‑006 → REM‑019
- R‑009 → REM‑020
- R‑010 → REM‑021
- R‑011 → REM‑001
- R‑013 → REM‑022

Governance Notes
- All high‑score (6) risks are linked to at least one ticket.
- Cross‑link state: complete (see Risks.index.yaml aggregatedStats.pendingCrossLink=false).
# CF_CORE CLI & Migration Audit — 10‑Section Report
Generated: 2025-11-10

## 1) Objectives & Scope
- Inventory CF_CORE CLIs, wrappers, and related subsystems
- Quantify .QSE/v2 artifact folders; differentiate v1 vs v2
- Catalog migration records (IntegrationGuide/DeprecationLog)
- Assign confidence ratings and record negative findings
- Deliver a structured report suitable for governance

## 2) Methodology
- Workspace-first enumeration with dedup and family grouping
- Surrogate structural authority: Python Typer CLI patterns (external CF_CORE spec absent)
- Evidence captured by exact file paths and directory lists
- Excluded test harness CLIs from CF_CORE counts

## 3) CLI Inventory (Summary)
- Primary: cf_cli.py (Python Typer)
- Specialized: dbcli.py, tasks_cli.py, sprints_cli.py, projects_cli.py
- Wrappers: PowerShell scripts invoking cf_cli.py (8 unique call sites)
- Subsystem CLI: TaskMan‑v2 (bin: taskman)
- Bridges: mcp-cfcli-bridge.js (Node shebang)
- Negatives: simple_cli.py, working_cli.py not present

See detailed inventory: `CF_CORE_Audit_Inventory.md`

## 4) .QSE Artifacts (v1 vs v2)
- v2 top-level: artifacts/, Evidence/, Indexes/, Research/, Sessions/, shadow/, Sync/, TaskMan-v2/ (+ QSE-INDEX.yaml)
- v1 top-level: artifacts/, evidence/, sessions/, scripts/ (+ QSE-INDEX.yaml)

## 5) Migration Records
- Integration Guides (3):
  - .QSE\\v2\\artifacts\\P-CF-SPECTRE-001\\IntegrationGuide.TaskMan-CF_CORE-UTMW.20251107-0125.yaml
  - .QSE\\v2\\artifacts\\P-CF-SPECTRE-001\\IntegrationGuide.TaskMan-CF_CORE-UTMW.20251107-1530.yaml
  - .QSE\\v2\\artifacts\\P-CF-SPECTRE-001\\IntegrationGuide.P-CF-SPECTRE-001.20251107-PHASE1-2.yaml
- Deprecation Log (1):
  - .QSE\\v2\\artifacts\\P-CF-SPECTRE-001\\DeprecationLog.IntegrationGuide.P-CF-SPECTRE-001.20251110.yaml

## 6) Migration Classification Matrix (Condensed)
| Component | Role | Phase | Evidence | Confidence |
|---|---|---|---|---|
| cf_cli.py | Primary | Active (Bridge coexists with TaskMan‑v2) | PS wrappers, usage in scripts | High |
| dbcli/tasks_cli/sprints_cli/projects_cli | Specialized | Active | File presence; Typer pattern | High |
| PowerShell wrappers | Wrapper | Active | Direct invocations of cf_cli.py | High |
| TaskMan‑v2 CLI (taskman) | Subsystem CLI | Active | package.json bin + bin scripts | High |
| mcp-cfcli-bridge.js | Bridge | Active | Shebang + integration name | Medium‑High |
| Legacy CF_CORE CLI | Legacy | Unknown | Requires reading DeprecationLog content | Medium |

## 7) Confidence Ledger
- High: Python CLIs, wrappers, TaskMan‑v2 CLI, v1/v2 .QSE structure, migration filenames
- Medium‑High: Bridge role inference via filename/location
- Medium: Explicit deprecation status of CF_CORE pending deeper artifact read

## 8) Negative Findings
- No external authoritative CF_CORE spec located
- Expected auxiliary CLIs (simple_cli.py, working_cli.py) absent

## 9) Risks & Mitigations
- Risk: Overcounting IntegrationGuide timestamps — Mitigation: count as logical uniques, report instances separately if needed
- Risk: Ambiguity in `.QSE/v2` adjunct folders — Mitigation: treat as adjunct subtrees, not core artifact types
- Risk: Legacy status uncertainty — Mitigation: optional follow-up: parse deprecation log content

## 10) Recommendations & Next Actions
- Accept current classification and counts for governance usage
- Optional: parse DeprecationLog to confirm/deny explicit CF_CORE CLI deprecation pathways
- Maintain PS wrappers as supported user entrypoints on Windows; document standard usage patterns
- Keep TaskMan‑v2 CLI cataloged as subsystem (do not conflate with CF_CORE primary)

### Progress Update (2025-11-10)
REM-003 (Risk Register) completed:
- 13 risk entries validated
- Cross-links to tickets established
- High-score risks mapped (R-001, R-005, R-007, R-008, R-012)

CSV/YAML tickets synchronized:
- Added RiskIds column
- Appended REM-017–REM-022 (contract, deprecation, wrapper, bridge, performance, docs)

REM-004 (Materialization) — Completed:
- Script: `scripts/Import-RemediationTickets.ps1` (uses repo `.venv` Python; direct call operator; JSONL logging)
- Run: Full apply with `-NoSprint` succeeded
- Result: Processed=22 Upserted=22 Updated=22 Failed=0
- Notes: Warnings only for status normalization ("Not Started" → `new`)

Owner workload distribution (tickets per owner):
- Governance/PM: 4
- Engineering (CLI): 3
- Docs + Engineering: 3
- Architecture + Governance: 1
- DevEx: 1
- DevOps + Docs: 1
- Engineering (Analytics) + Docs: 1
- Engineering (DB) + Docs: 1
- Engineering (Planning): 1
- Governance/PM + Docs: 1
- Governance/PM + Engineering: 1
- Platform + DevOps: 1
- Platform + Engineering: 1
- SRE + Platform: 1

Next actions:
1) Normalize CSV statuses to canonical values (replace "Not Started" with `new`) to remove warnings
2) Compute `.QSE/v1` vs `.QSE/v2` evolution metrics and narrative (tracking maturity)
3) Build dependency matrix and identify parallelizable items
4) Define completion criteria and sign‑off sequence; draft stakeholder communication plan

---
Prepared as part of CF_CORE-AUDIT-SESSION. See `CF_CORE_Audit_Inventory.md` for full evidence.

## Appendix A: Lifecycle Taxonomy (REM-002)

The following lifecycle stages are used to tag CF_CORE components and adjacent subsystems. These definitions are concise, machine-comprehensible, and cite the audit and remediation plan context.

- Active: Primary or specialized components in current, supported use. Evidence: inventory paths and current wrappers/usage. Governance: Report §§1–5; Plan §2.
- Migrating: Components with an approved transition path and partial adoption. Evidence: IntegrationGuide with target, migration plan. Governance: Report §§6–7; Plan §2.
- Deprecated: Components superseded by canonical artifacts or retired patterns. Evidence: Deprecations.index.yaml entries or explicit deprecation decisions. Governance: Report §8; Plan §1.
- Candidate: Proposed or emerging components pending adoption decision. Evidence: Options/Research artifacts; not yet binding. Governance: Report §10; Plan backlog items.
- Adjunct: Supporting tools (bridges, subsystem CLIs, VS Code integrations) that are not CF_CORE but are intentionally coupled. Evidence: file paths and role classification. Governance: Report §3; Plan scope notes.

Confidence scale: High | Medium‑High | Medium | Low (rationale captured per row). Citations prefer exact file paths and index entries over narrative references.

## Appendix B: Lifecycle Matrix (Components → Stage, Confidence, Citations)

| Component | Path | Role | Lifecycle | Confidence | Citations | Notes |
|---|---|---|---|---|---|---|
| cf_cli.py | cf_cli.py | Primary CLI | Active | High | CF_CORE_Audit_Inventory.md §1; PS wrappers | Windows entrypoint via wrappers; session lifecycle guarded in source |
| dbcli.py | dbcli.py | Specialized CLI | Active | High | CF_CORE_Audit_Inventory.md §1 | Typer pattern present |
| tasks_cli.py | tasks_cli.py | Specialized CLI | Active | High | CF_CORE_Audit_Inventory.md §1 | Typer pattern present |
| sprints_cli.py | sprints_cli.py | Specialized CLI | Active | High | CF_CORE_Audit_Inventory.md §1 | Typer pattern present |
| projects_cli.py | projects_cli.py | Specialized CLI | Active | High | CF_CORE_Audit_Inventory.md §1 | Typer pattern present |
| Deploy-CFEnhancedCLI.ps1 | scripts/Deploy-CFEnhancedCLI.ps1 | Wrapper | Active | High | CF_CORE_Audit_Inventory.md §2 | Invokes cf_cli.py |
| Invoke-CFEnhancedWorkflow.ps1 | scripts/Invoke-CFEnhancedWorkflow.ps1 | Wrapper | Active | High | CF_CORE_Audit_Inventory.md §2 | Invokes cf_cli.py |
| cf_cli_clean.ps1 | scripts/cf_cli_clean.ps1 | Wrapper | Active | High | CF_CORE_Audit_Inventory.md §2 | Invokes cf_cli.py |
| cf-cli.ps1 | scripts/cf-cli.ps1 | Wrapper | Active | High | CF_CORE_Audit_Inventory.md §2 | Invokes cf_cli.py |
| bulk-create-missing-tasks.ps1 | scripts/bulk-create-missing-tasks.ps1 | Wrapper | Active | High | CF_CORE_Audit_Inventory.md §2 | Invokes cf_cli.py |
| Test-TaskManagerDTMTracking.ps1 | scripts/Test-TaskManagerDTMTracking.ps1 | Wrapper | Active | High | CF_CORE_Audit_Inventory.md §2 | Invokes cf_cli.py |
| Deploy-DTM-Native.ps1 | scripts/Deploy-DTM-Native.ps1 | Wrapper | Active | High | CF_CORE_Audit_Inventory.md §2 | Invokes cf_cli.py |
| update_pending_tasks.ps1 | scripts/update_pending_tasks.ps1 | Wrapper | Active | High | CF_CORE_Audit_Inventory.md §2 | Invokes cf_cli.py |
| TaskMan‑v2 CLI | TaskMan-v2/cli/bin/run.js | Subsystem CLI (Adjunct) | Active | High | CF_CORE_Audit_Inventory.md §3 (package.json bin) | Managed as adjunct subsystem; not CF_CORE primary |
| CF_CLI bridge | vs-code-task-manager/mcp-cfcli-bridge.js | Bridge (Adjunct) | Active | Medium‑High | CF_CORE_Audit_Inventory.md §3 | Integration bridge; inferred by location/name |
| IntegrationGuide (canonical) | .QSE/v2/artifacts/P-CF-SPECTRE-001/IntegrationGuide.TaskMan-CF_CORE-UTMW.20251107-1530.yaml | Guide | Active | High | Inventory §5 | Canonical guide used by migrations |
| IntegrationGuide (verbose variant) | .QSE/v2/artifacts/P-CF-SPECTRE-001/IntegrationGuide.P-CF-SPECTRE-001.20251107-PHASE1-2.yaml | Guide | Deprecated | High | .QSE/v2/Indexes/Deprecations.index.yaml; DeprecationLog…20251110.yaml | Replacement path cited in index |

Citations to Deprecations index (Appendix source): `.QSE/v2/Indexes/Deprecations.index.yaml`.

Acceptance (REM‑002): Lifecycle definitions published (Appendix A) and lifecycle matrix produced (Appendix B) with confidence and citations. This enables REM‑003 (risk register) to proceed.
