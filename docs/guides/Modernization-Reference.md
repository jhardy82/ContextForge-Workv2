# Modernization Reference (Living)

> Purpose: Single-page operational snapshot of platform modernization & analytics enablement. Updated only when material state changes (not a diary).

## 1. Objectives (Active)
- Host modernization: PowerShell 7 default; retain PS 5.1 only where required (SCCM / unsupported modules).
- Script estate classification → authoritative HostPolicy tags (LegacyPS51 / DualHost / ModernPS7 / PythonHelper).
- Parallelization readiness (ForEach-Object -Parallel, runspace-safe patterns) after classification & container baseline.
- Reproducible analytics lane (ML notebook, deterministic seeds, dependency pinning, optional torch/papermill) without polluting infra scripts.
- Logging Minimum Viable Events (MVE) everywhere: session_start, task_start, decision, artifact_touch_batch, artifact_emit, warning/error, task_end, session_summary.
- Containerized dev environment for consistent tooling (PowerShell + Python stack) & CI parity.

## 2. Architecture & Taxonomy Snapshot
- HostPolicy Tags: LegacyPS51 (constrained), DualHost, ModernPS7 (preferred), PythonHelper (analytics / orchestration, non‑mutating SCCM).
- Burst vs Task: burst = ordered set of ≥1 tasks; tasks emit `task_start`/`task_end`. Future optional `burst_start`/`burst_end`.
- Logging Elevation Triggers: duration >5s, multi-artifact mutation, cross-boundary orchestration, public API change → evidence tier.
- Evidence Activation (EVD-190+): only on high-risk refactor / public API change / explicit evidence:true.

## 3. Key Tools & Artifacts

| Domain | Tool/File | Status | Notes |
|--------|-----------|--------|-------|
| Classification | `scripts/Inventory-HostPolicyClassification.ps1` | Authored | Needs execution & integration outputs committed. |
| Test Harness | `build/Run-PesterTests.ps1` | Modernized (PS7 relaunch) | Add compliance artifact & dedupe burst_end. |
| Analytics | `notebooks/ML_Workflow.ipynb` | Hardened | Dependency presence check; profiling clone; feature importance fallback. |
| Dependencies | `requirements.txt`, `requirements-extra.txt` | Present | Consider future pin (hash lock). |
| Governance | `anchor_map.json` | Present | Sync after large instruction updates. |
| Instructions | `.github/copilot-instructions.md` | v1.3.0 | Anchor for rule IDs. |

## 4. Current State & Gaps (Delta Focus)
Completed:
- HostPolicy taxonomy defined.
- PS7 default in tasks/settings.
- Inventory script authored.
- ML workflow notebook scaffold + hardening.
- Dependency externalization.
- Dev container strategy researched (not implemented).

Gaps (Actionable):
1. Run classification → emit JSON/CSV; summarize counts & tag deficits.
2. Add `.devcontainer/` (devcontainer.json + optional Dockerfile + postCreate) → bake Python + pwsh + caching.
3. Harness fix: ensure single burst_end & emit compliance JSON artifact.
4. Notebook CI lane (papermill execution + optional nbval) with metric/assert threshold.
5. Parallelization helper module & safety patterns (after classification & container).
6. Environment provenance hashing (requirements + devcontainer.json) → artifact_emit.
7. Logging coverage enforcement script invocation in governance suite (if not already wired) and gap remediation.

## 5. Immediate 7-Day Priorities
(Ordered for dependency chaining)
1. Execute classification & commit artifacts. (Enables scoping of migration tasks.)
2. Implement dev container + verify PSSA/Pester + notebook run inside container. (Repro baseline.)
3. Harness compliance artifact + duplicate event fix. (Governance completeness.)
4. Add notebook CI lane (papermill run + simple metric assertion). (Analytics validation.)
5. Emit environment provenance hash after container build. (Integrity.)

## 6. Logging MVE Reminder
Emit (always when non-trivial): session_start, task_start, decision, artifact_touch_batch, artifact_emit, warning/error, task_end, session_summary. Missing any in multi-artifact or >5s ops → log `logging_gap_detected`.

## 7. Pending Enhancements (Backlog Seeds)
- Parallelization wave: Introduce `Invoke-ParallelSafe` wrapper; evaluate runspace-safe file writes.
- Evidence bundling automation on API change detection (hash manifest under `evidence/<session_id>`).
- Automatic HostPolicy insertion patcher for untagged scripts.
- Lock file generation (pip-compile or uv lock) for deterministic Python builds.
- Container prebuild optimization (GitHub Codespaces / Dev Container CLI cache warming).
- Burst boundary optional events once governance tool updated.

## 8. Reference Anchors
- Instructions Version: v1.3.0 (`.github/copilot-instructions.md`)
- Anchor Map Hash: (update after regeneration) current file: `anchor_map.json`
- This Document Path: `docs/Modernization-Reference.md`

## 9. Update Protocol
1. Apply material change (state/procedure/tool). 2. Update relevant section succinctly. 3. Commit with `docs: refresh modernization reference`. 4. Avoid duplicating granular details already present in instruction file.

---
Maintainer Notes: Keep under ~250 lines; prune resolved gaps; escalate items to backlog once tasks scheduled.
