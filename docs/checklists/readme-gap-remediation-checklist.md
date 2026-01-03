# README Gap Remediation Checklist

Track the work required to backfill missing README files and repair incorrect ones. Each entry includes discrete research vs. implementation plan checkboxes so evidence gathering stays separate from documentation work.

## Missing READMEs

### projects/QSE-SME-Development/README.md
- [x] **Research Plan**: Interview CF_CLI owners on scope; inspect `projects/QSE-SME-Development` history and any linked `AAR.*` files for context.
- [x] **Implementation Plan**: Draft README covering project goals, CF/UCL alignment, and authoritative entry points (`cf_cli.py task ...`), then link to `projects/INDEX.md`.

### projects/cf_logging/README.md
- [x] **Research Plan**: Review `unified_logger` project docs, `logs/` automation scripts, and governance evidence to define overlaps/conflicts.
- [x] **Implementation Plan**: Document architecture, dependencies, and how this project differs from `projects/unified_logger`; include conflict note in README.

### projects/cf_tracker/README.md
- [x] **Research Plan**: Analyze `tracker` scripts, `trackers/` data, and `dbcli` commands for authoritative tracker processes.
- [x] **Implementation Plan**: Produce README outlining tracker ingestion, authority flow, and CF_CLI touchpoints; reference `scripts/tracker`.

### projects/dtm/README.md
- [x] **Research Plan**: Inspect `dynamic-task-manager/`, TaskMan-v2 docs, and DTM tests to confirm whether this folder mirrors or extends those efforts.
- [x] **Implementation Plan**: Clarify ownership vs. `projects/taskman-mcp` and `TaskMan-v2` in README, outlining current status and future work.

### projects/taskman-mcp/README.md
- [x] **Research Plan**: Compare with `projects/P-TASKMAN-MCP` and `TaskMan-v2/mcp-server*` to resolve scope collisions.
- [x] **Implementation Plan**: Author README stating how this folder differs from the prefixed variant; add cross-links and conflict callouts.

## Incorrect / Placeholder READMEs

### tests/README.md
- [x] **Research Plan**: Leverage `tests/INDEX.md`, suite owners, and constitutional testing requirements to define expected sections.
- [x] **Implementation Plan**: Replace placeholder content with suite taxonomy, execution commands, and coverage expectations; keep parity with the index.

### out/phase-1-*/README.md (all Phase 1 run folders)
- [x] **Research Plan**: Inspect JSONL logs and artifacts within each `out/phase-1-*` folder to identify the run intent and command provenance.
- [x] **Implementation Plan**: Update each README with a concise summary (command, timestamp, pass/fail, evidence links); create a template to prevent future placeholders.

### README duplicates for TaskMan MCP scopes
- [x] **Research Plan**: Determine whether `projects/P-TASKMAN-MCP/README.md` and the missing `projects/taskman-mcp/README.md` should represent the same initiative.
- [x] **Implementation Plan**: After clarifying scope, adjust READMEs (or consolidate folders) so duplicates no longer diverge; reflect the decision in `projects/INDEX.md`.

## Next Steps Plan

### Phase 1 – Missing READMEs

| Target README | Research Steps | Implementation Steps | Owner(s) | ETA | Status |
| --- | --- | --- | --- | --- | --- |
| `projects/QSE-SME-Development/README.md` | 1. Pull git history + review `AAR.W-QSE-*` artifacts.<br>2. Interview CF_CLI owners for current charter. | 1. Author README (mission, CF/UCL coverage, tooling).<br>2. Link from `projects/INDEX.md` + related trackers. | DocsOps + Architecture | Day 1 | ✅ Complete |
| `projects/cf_logging/README.md` | 1. Compare with `projects/unified_logger` scope.<br>2. Audit `logs/`, `scripts/logs/`, governance docs for overlap. | 1. Produce delta-focused README.<br>2. Document conflict resolution w/ unified logger. | Logging WG | Day 2 | ✅ Complete |
| `projects/cf_tracker/README.md` | 1. Review tracker scripts + `trackers/` datasets.<br>2. Map dbcli tracker commands. | 1. Capture ingestion + authority model in README.<br>2. Reference canonical tracker automation. | Tracker WG | Day 3 | ✅ Complete |
| `projects/dtm/README.md` | 1. Inspect `dynamic-task-manager/` + TaskMan-v2 migration docs.<br>2. Confirm whether folder is legacy holdover. | 1. Document historical context + current status.<br>2. Add migration pointers (DTM → TaskMan-v2). | TaskMan Program | Day 4 | ✅ Complete |
| `projects/taskman-mcp/README.md` | 1. Compare repo contents with `P-TASKMAN-MCP`.<br>2. Interview MCP maintainers for intended split. | 1. Clarify scope and cross-link READMEs.<br>2. Flag consolidation decision in `projects/INDEX.md`. | TaskMan Program | Day 4 | ✅ Complete |

### Phase 2 – Incorrect / Placeholder READMEs

| Target README | Research Steps | Implementation Steps | Owner(s) | ETA | Status |
| --- | --- | --- | --- | --- | --- |
| `tests/README.md` | 1. Synthesize suite taxonomy from `tests/INDEX.md` + maintainers.<br>2. Collect execution commands + coverage gates. | 1. Replace placeholder with taxonomy + commands.<br>2. Keep README synced with `tests/INDEX.md`. | Test Guild | Day 2 | ✅ Complete |
| `out/phase-1-*/README.md` | 1. Enumerate each `out/phase-1-*` folder.<br>2. Review JSONL logs + evidence for intent/outcome. | 1. Populate template summary (cmd, result, evidence).<br>2. Backfill across all Phase 1 folders. | Evidence Ops | Day 5 | ✅ Complete |
| TaskMan MCP duplicate READMEs | 1. Audit both folders and stakeholders to decide on single source of truth.<br>2. Document decision in governance notes. | 1. Update/merge READMEs per decision.<br>2. Update indexes + checklist once resolved. | TaskMan Program + Governance | Day 5 | ✅ Complete |

### Execution Cadence

1. **Daily Standup (15 min)**: Review progress vs. ETA, unblock interviews.
2. **Evidence Capture**: Attach research notes to `docs/checklists/readme-gap-remediation-checklist.md` as items complete.
3. **Validation**: Each README PR must cite research evidence and link back to this checklist before closure.

## Post-Remediation Next Steps

1. **Continuous Monitoring** ✅ `scripts/validate_readme_index.py` plus the Docs Validation workflow now warn (non-blocking) when `README_INDEX.md` drifts.
2. **Delta Audits** ✅ `.github/pull_request_template.md` now includes checkboxes requiring README + `README_INDEX.md` updates for new directories.
3. **Phase Output Template** ✅ `docs/templates/run-readme-template.md` created; `out/INDEX.md` references it.
4. **TaskMan Consolidation Watch** ⏳ Continue monitoring until MCP harness fully migrates under `TaskMan-v2/mcp-server`.
5. **Quarterly Review** ⏳ Schedule recurring audits to ensure catalogs stay fresh.

### TaskMan MCP Consolidation Log

| Date | Status | Notes |
| --- | --- | --- |
| 2025-11-16 | In progress | `projects/taskman-mcp` hosts Python harness; production MCP runs from `TaskMan-v2/mcp-server`. Review consolidation once milestones migrate. |

### Quarterly Audit Schedule

- Next audit checkpoint: **2026-02-16** (aligns with 90-day cadence from latest remediation).

## Extended Catalog (2025-11-16)

- `TaskMan-v2/INDEX.md` – Maps UI, backend API, MCP servers, shared config, and extension assets.
- `archive/README.md`, `authority/README.md`, `modules/README.md`, `interface/README.md` – Root documentation for high-churn directories.
- `docs/roadmap/INDEX.md`, `docs/guides/INDEX.md` – Local indexes for dense documentation clusters.
- `docs/templates/run-readme-template.md` – Template referenced by all `out/phase-*` READMEs (also linked from `out/INDEX.md`).
