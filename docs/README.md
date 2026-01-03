---
created: 2025-08-14
updated: 2025-11-29
author: GitHub Copilot
version: 2.0.0
purpose: Documentation index with modernization quick-start and quality workflows
---

# Documentation Index

## 📁 Documentation Structure (Updated 2025-11-29)

The documentation library spans **69 subdirectories** with **550+ markdown files**. Major directories:

### Core Documentation (High-Volume)

| Directory | Purpose | Files |
| --- | --- | ---: |
| `research/` | Research documents, findings, investigations | 71 |
| `completed/` | Completed work and deliverables | 45 |
| `reference/` | API reference and technical specifications | 42 |
| `reports/` | Analysis, status, and completion reports | 41 |
| `plans/` | Implementation plans, roadmaps, project plans | 40 |
| `testing/` | Test strategies, specifications, validation | 34 |
| `guides/` | User and developer guides, how-to docs | 26 |
| `mcp/` | Model Context Protocol integration | 23 |
| `architecture/` | Architecture decisions, system design | 18 |
| `roadmap/` | Feature roadmaps and phase planning | 18 |
| `aar/` | After Action Reviews (lessons learned) | 17 |

### Active Work Directories

| Directory | Purpose | Files |
| --- | --- | ---: |
| `context/` | Evidence, cache, monitoring artifacts | 15 |
| `validation/` | Validation reports and compliance | 13 |
| `implementation/` | Implementation guides and status | 12 |
| `plugins/` | Plugin documentation and integrations | 12 |
| `Codex/` | ContextForge Work Codex principles | 11 |
| `sessions/` | Session logs and meeting records | 11 |
| `dtm/` | Dynamic Task Manager documentation | 10 |
| `database/` | Database design and migrations | 10 |
| `ai-assistants/` | AI assistant configurations | 10 |
| `governance/` | Governance policies and standards | 9 |

### Quick Navigation

- **Need a guide?** → `docs/guides/`
- **Looking for a plan?** → `docs/plans/`
- **Researching a topic?** → `docs/research/`
- **Architecture decisions?** → `docs/architecture/` or `docs/adr/`
- **Testing documentation?** → `docs/testing/`
- **MCP integration?** → `docs/mcp/`
- **Work principles?** → `docs/Codex/`

---

Runtime Policy Summary (Updated Modernization):

Primary Development / Orchestration Engine = PowerShell 7 (pwsh) where available (preferred).
Fallback / Legacy Compatibility = Windows PowerShell 5.1 only when required by legacy modules (tag with HostPolicy: LegacyPS51 + HostFallbackReason).
DualHost scripts MUST avoid PS7-only syntax unless guarded; ModernPS7 scripts MAY use PS7 features (parallel, null-coalescing, pipeline chains).

## 📊 DuckDB Velocity Tracker (Data-Driven Planning)

**Proven Baseline (as of 2025-08-27):**
- **Velocity Rate**: 0.44 hours per story point (validated across 21 story points / 11.0 actual hours)
- **Data Source**: DuckDB analytics engine (`db/velocity.duckdb`)
- **Confidence Level**: High (90%+) for tasks within established complexity patterns

**Quick Usage:**

```powershell
# Generate data-driven roadmap with proven velocity metrics
.\cli\Invoke-VelocityTracker.ps1 -Action Report

# Record work session for velocity tracking
.\cli\Invoke-VelocityTracker.ps1 -Action Record -TaskId "T-20250827-001" -Hours 2.1 -StoryPoints 5

# Predict completion time with complexity factor
.\cli\Invoke-VelocityTracker.ps1 -Action Predict -StoryPoints 8 -Complexity 1.2
```

**Implementation Files:**
- PowerShell CLI: `cli/Invoke-VelocityTracker.ps1`
- Python Core Engine: `python/velocity/velocity_tracker.py`
- Roadmap Generator: `python/velocity/generate_roadmap.py`

Governance artifacts:
- variety_metrics.json
- variety_alerts.json
- governance_gap_report.json
- chain_summary.json
- chain_summary_integrity.json
- circle_closure_aar.json

Tagline: "Pwsh-First Modernization | 5.1 Fallback Only When Justified".

## Structure
- reference/ – API reference documentation
- guides/ – User and developer guides
- examples/ – Usage examples
- api/ – Generated API documentation
- context/ – Evidence, cache, and monitoring descriptors/artifacts

## Professional Supplements
- [ContextForge Work Codex — Professional Principles with Philosophy](Codex/ContextForge Work Codex — Professional Principles with Philosophy.md)

Master vs Work Codex:
- Master Codex: Foundational, exhaustive philosophy (use when explicitly requested).
- Work Codex: Focused professional principles with concise philosophy (default reference for excerpts).

## Documentation Index (Auto-Generated Summary)
This section is augmented by `python/tools/build_indexes.py` (idempotent). Key artifacts:
- Files Index: `orchestrator/index/files.index.json`
- Docs Index: `orchestrator/index/docs.index.json`
- Tags Index: `orchestrator/index/tags.index.json`
- Links Report: `orchestrator/index/links.report.json`
Regenerate with: `python python/tools/build_indexes.py --auto-stub`

Key references:
- Dev environment modernization: `Dev-Environment-Modernization.md`
- Developer environment quickstart: `DEV-ENV-QUICKSTART.md`
- Workspace External Dependencies Modernization Plan (Updated 2025-08-13): `reference/Workspace-External-Dependencies-Modernization-Plan.md`

## Quick start (modernized)
1. Start the background watcher (PowerShell 7): task "Background: Watch-BackgroundTasks (pwsh)".
1. Kick off quality runs in the background:
- Pester: task "Start: Pester Detached (pwsh)"
- PSSA (All): task "Start: PSSA Detached (pwsh, All)"
1. View results and evidence:
- Latest summaries: task "Quality: View Latest (Top 1)"
- JSONL logs and artifacts under `logs/` and `docs/context/cache/`

Notes:
- Default Host Selection: Central helper (scripts/helpers/HostSelection.ps1) chooses pwsh when present.
- Fallback Justification: Any hard-coded powershell.exe usage must include HostPolicy: LegacyPS51 + HostFallbackReason.
- Artifact Parity: Unless explicitly ModernPS7-only, outputs must remain content-identical (ignoring run_id/timestamp + engine metadata) across engines.
- Parallel / Advanced Features: ModernPS7 scripts may adopt ForEach-Object -Parallel, pipeline chain (&&/||), null-coalescing (??) with Legacy skip guards.
- Governance Artifacts:
  - variety_metrics.json – diversity statistics
  - variety_alerts.json – threshold evaluation (LOW_SHAPE_DIVERSITY, CLASS_MONOCULTURE_RUN)
  - governance_gap_report.json – evidence presence gaps
  - chain_summary.json – unified planning + metrics + evidence_presence
  - chain_summary_integrity.json – SHA256 hash over stable planning fields
  - circle_closure_aar.json / .md – integrated After Action Review
- Logging-first: Every generator moving toward JSONL logs (chain summary + AAR already). New generators (alerts/integrity) will add JSONL trace in upcoming iteration.
- Current baseline: Migration in progress; verification harness now uses dynamic host selection (pwsh-first). Legacy 5.1-only launchers archived/refactored.

## Generating reference docs (PlatyPS)
Use PlatyPS to generate reference documentation:
Import-Module PlatyPS
New-MarkdownHelp -Module YourModule -OutputFolder ./docs/reference/

## Related guides
- Background monitoring helpers module: `../build/Background-Tasks.psm1`
- Watcher CLI: `../cli/Watch-BackgroundTasks.ps1`
- Starters (pwsh orchestration): `../cli/Start-Pester-Detached.ps1`, `../cli/Start-PSSA-Detached.ps1`

## ✅ Trust-but-Verify Checklist
- [x] All functions have docstrings (applies to scriptable modules)
- [x] Progress indicators implemented (watcher + tasks show progress)
- [x] Error handling included (wrappers and watcher use try/catch patterns)
- [x] Tests written and passing (Pester flows integrated; see tests/README.md)
- [x] CLI usage documented (see Quick start and related guides above)
- [x] RunId sanitization centralized via build/RunId-Utils.ps1
- [x] Diversity optimization tie-break (-OptimizeVariety) implemented
- [x] Variety alerts + integrity hash artifacts generated
- [ ] Dual-engine parity harness (planned)
- [ ] JSON schema validation for new alert/integrity artifacts (planned)
