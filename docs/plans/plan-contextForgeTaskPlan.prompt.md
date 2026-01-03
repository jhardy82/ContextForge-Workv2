# Testing Platform Refactor Recovery Plan

## Goal
Restore momentum and structural integrity for the Testing Platform Refactor (P-TPR) by stabilizing foundational artifacts, aligning environment determinism, hardening reproducibility, optimizing test/logging/evidence automation, and instituting durable governance & iteration cycles.

## Phase 1 – Stabilize (Foundation)
Artifacts to create:
- TPR-FOUNDATION-PHASE-PLAN.md (authoritative phase charter)
- foundation-checklist.P-TPR.v0.1.yaml (track artifact presence & status)
- env-hash-manifest.P-TPR.json (supplemental per-package + tool hash list)
- coverage-baseline-report (HTML/JSON) + coverage-thresholds.yaml
- logging-path-map.json (enumerate critical execution paths with expected log events)
- evidence-root: .QSE/v2/Evidence/P-TPR/ (scaffold directories: coverage-baseline, logging-baseline, env-manifest, bundles/)
Exit Criteria:
- Checklist shows ≥90% foundation artifacts present
- Hash manifest populated for all direct prod/test dependencies
- Baseline coverage & logging reports stored & hashed
- UCL compliance scan passes (no orphan contexts; evidence bundles exist for artifact creation session)

## Phase 2 – Align (Environment & Governance)
Focus:
- Environment Strategy Option B (keep existing lockfile; add hash manifest + validation script validate-env.P-TPR.ps1)
- COF 13D matrix (cof-13d-matrix.P-TPR.yaml) fully populated
- Sacred Geometry gates definitions (sacred-gates.P-TPR.yaml) with metrics:
  - circle.completenessPct
  - triangle.validationSteps
  - spiral.learningCycles
  - goldenRatio.valueEffortIndex
  - fractal.patternConsistencyScore
- UCL audit report (ucl-audit.P-TPR.yaml) linking each artifact to parent context P-TPR
Exit Criteria:
- validate-env script produces clean run (all hashes match)
- COF matrix completeness score 13/13
- Sacred gates file committed; initial gate metrics recorded
- UCL audit shows zero orphans, zero cycles, evidence completeness true

## Phase 3 – Harden (Automation & Reproducibility)
Focus:
- Automated generation: coverage + logging + env validation on CI (workflow additions)
- Parallelization config (pytest-xdist / PowerShell Pester split) parallelization-config.P-TPR.yaml
- Mutation test sample set mutation-sample-set.P-TPR.yaml (target the highest business-value modules first)
- Performance benchmark baseline perf-benchmark.P-TPR.json (p50, p95 latency & critical test suite runtime)
- Logging deficit detector script (detect-logging-deficit.py) referencing logging-path-map
Exit Criteria:
- CI shows deterministic run (no env drift) across 3 consecutive builds
- Mutation baseline captured and ≥60% mutants killed for critical module set
- Parallel test execution stable: flakiness rate <1%
- Logging deficit report zero high-priority gaps

## Phase 4 – Optimize (Coverage, Performance, Evidence Efficiency)
Focus:
- Coverage uplift: baseline → ≥70% (strategic) then iterative toward 80%
- Reduce test runtime by ≥30% via selective parallelization & fixture reuse
- Evidence bundle size optimization: prune redundant payloads while retaining integrity (target ≤40% size reduction without losing required fields)
- Velocity baseline (velocity-baseline.P-TPR.json) capture + story point calibration functions
Exit Criteria:
- Coverage thresholds enforced in pipeline (hard fail <70%)
- Runtime reduction goals met & benchmark diff logged
- Evidence bundles hashed & size reduction validated
- Velocity predictor accuracy within ±15% for 3 successive tasks

## Phase 5 – Govern & Iterate (Sustainability)
Artifacts:
- governance-schedule.P-TPR.yaml (cadence: weekly foundation check; bi-weekly coverage/logging review; monthly mutation/perf audit)
- risk-register.P-TPR.yaml (categories: env drift, coverage stagnation, logging deficit, runtime bloat, evidence overhead, governance decay, flaky tests)
- lessons-log.P-TPR.jsonl (spiral learning entries each iteration)
- gate-history.P-TPR.jsonl (append sacred gate metrics per cycle)
Practices:
- After Action Review (AAR) generated each iteration & stored under evidence bundle path
- Sequence: Plan → Act → Observe → Adapt → Log (sequential thinking cycles) logged & hashed
Exit Criteria:
- Governance schedule executed for first full cycle
- Risk register populated & first mitigation statuses applied
- ≥3 lessons entries and ≥2 gate-history snapshots
- COF/UCL revalidation passes post-optimization changes

## Environment Strategy (Option B Justification)
Trade-offs:
- Fast adoption: reuse existing lockfile
- Strong reproducibility: supplemental hash manifest & validation script
- Moderate overhead: avoid full hermetic container upfront, enabling faster iteration
Future upgrade path: promote to Option C (container pinning) after stabilization if drift risk increases.

## Metrics (Key Signals)
- coverage.linePct
- logging.pathCoveragePct
- evidence.bundleSizeBytes & bundleRedundancyRatio
- mutation.killedPct
- perf.testSuiteRuntimeSeconds (baseline vs optimized)
- env.driftIncidents (per week → target 0)
- velocity.hoursPerPoint & forecastAccuracyPct
- sacredGeometry: circlePct, triangleStepsPass, spiralCycles, goldenRatioIndex, fractalConsistency

## Risks & Mitigations (Snapshot)
1. Artifact Gaps → Mitigation: foundation-checklist gating Phase 1 exit
2. Environment Drift → Mitigation: validate-env script + hash manifest CI step
3. Coverage Stagnation → Mitigation: weekly diff + targeted high-value module selection map
4. Logging Deficit → Mitigation: logging-path-map baseline + deficit detector
5. Runtime Bloat → Mitigation: parallelization config + fixture consolidation
6. Evidence Overhead → Mitigation: pruning policy & size metrics
7. Governance Decay → Mitigation: calendar-driven governance-schedule file
8. Flaky Tests → Mitigation: quarantined list + flake triage workflow

## Immediate Next Actions (Sequenced)
1. Create foundation-checklist YAML (status: pending)
2. Scaffold evidence root directories (.QSE/v2/Evidence/P-TPR/…)
3. Generate env-hash-manifest JSON from current lockfile + tooling versions
4. Capture baseline coverage & logging outputs; store & hash
5. Produce validate-env.P-TPR.ps1 script referencing hash manifest & emitting structured log events

## Sacred Geometry Mapping (Phase Correlation)
- Circle: Phase 1 completeness threshold ≥90% artifacts present
- Triangle: Phase 2 validation steps (env, COF, sacred gate definitions) must all pass
- Spiral: Lessons & gate-history accumulation across Phases 3–5
- Golden Ratio: Optimization effort vs runtime & evidence size improvement tracked Phase 4
- Fractal: Pattern consistency (environment validation + evidence structure) across all phases

## Success Criteria Summary
Project considered stable when: foundation artifacts ≥95% presence, env drift incidents = 0 (30-day window), coverage ≥70% sustained, logging path coverage ≥90%, gated CI enforcement operational, first governance cycle archived with lessons & risk mitigations, and COF/UCL audits green.

## Validation & Evidence
Every artifact creation emits artifact_emit log with hash + size. Baselines & audits produce evidence bundles in .QSE/v2/Evidence/P-TPR/. UCL compliance script ensures no orphan artifacts and all evidence bundles complete.

## Evolution Path
After stabilization and initial optimization: evaluate containerization (Option C) or partial hermetic builds for critical test shards; introduce advanced mutation orchestration and performance regression early warning gates.

(End of plan)
