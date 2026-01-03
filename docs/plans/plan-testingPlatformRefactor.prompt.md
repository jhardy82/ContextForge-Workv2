Testing Platform Refactor Recovery Plan (P-TPR)

Summary
Restore momentum for Testing Platform Refactor by executing five phased tracks: Stabilize → Align → Harden → Optimize → Govern & Iterate. Environment strategy: Option B (lockfile + hash manifest) for deterministic reproducibility without heavy hermetic sandbox overhead. All work governed by COF 13D analysis, Sacred Geometry gates (circle, triangle, spiral, goldenRatio, fractal), and UCL compliance (no orphan, no cycle, evidence complete).

Phase 1: Stabilize (Foundation Artifacts & Evidence Scaffold)
Objectives:
- Instantiate missing foundational artifacts
- Establish evidence lineage root for P-TPR
- Capture current baseline (env, coverage, logging) before changes
Artifacts to Create:
1. TPR-FOUNDATION-PHASE-PLAN.md – narrative + scope + success criteria + initial risk summary
2. foundation-checklist.P-TPR.v0.1.yaml – actionable checklist (sections: artifacts, env, coverage, logging, governance hooks)
3. .QSE/v2/Evidence/P-TPR/ directory tree:
   - evidence-bundles/ (future JSONL bundles)
   - coverage-baseline/ (store initial coverage.json + html snapshot)
   - logging-baseline/ (sample structured JSONL run)
   - env-manifest/ (lockfile + hashes)
4. env-hash-manifest.P-TPR.json – package to {version, sha256} mapping
5. initial-session-log.P-TPR.yaml – session_start, task_start, artifact_emit events
Immediate Actions (ordered):
- Copy existing lockfile (requirements or poetry/pip-tools) → generate hash manifest
- Run pytest (fast subset) to capture current coverage + store baseline
- Emit unified logger sample run to logging-baseline
- Populate foundation checklist (mark created items, flag pending)
Exit Criteria:
- All listed artifacts exist and are hashed
- Baseline coverage + logging captured
- Checklist ≥80% foundation items marked COMPLETE

Phase 2: Align (COF 13D + Sacred Geometry + UCL)
Objectives:
- Dimensionalize recovery context against COF 13D
- Define Sacred Geometry gate thresholds specific to P-TPR
- Verify UCL (anchored, flowing, evidenced) on new artifacts
Artifacts:
1. cof-13d-matrix.P-TPR.yaml – 13 sections (motivational … holistic) each ≥150–200 words
2. sacred-gates.P-TPR.yaml – definitions: circle.completenessPct≥95, triangle.validationSteps=[plan,execute,validate], spiral.learningArtifacts=[AAR, lessons], goldenRatio.balanceHeuristic (value/effort scoring), fractal.patternConsistency rules
3. ucl-audit.P-TPR.yaml – results of orphan/cycle/evidence checks (PASS/FAIL + remediation)
4. taskman-linkage-manifest.P-TPR.yaml – mapping of recovery tasks → TaskMan IDs
Actions:
- Draft COF matrix referencing foundation artifacts
- Parameterize gate thresholds using current baselines (e.g. coverage uplift target)
- Run UCL audit script (reuse existing compliance utilities) and store report
- Link tasks in TaskMan (ensure parent project reference P-TPR)
Exit Criteria:
- COF matrix complete (13/13 dimensions, depth adequate)
- All Sacred gates defined and versioned
- UCL audit PASS (or remediations logged and scheduled)
- Task linkage manifest merged

Phase 3: Harden (Reproducibility, Coverage, Logging)
Objectives:
- Enforce deterministic env checks pre-test
- Raise coverage & logging path coverage to agreed thresholds
- Automate drift detection + evidence generation
Targets (initial, adjustable after metrics review):
- Line coverage: raise from baseline to ≥70% (then iterate toward 80%)
- Logging path coverage: ≥90% mandatory baseline
- Env drift: zero unpinned packages; hash validation on CI
Artifacts/Automation:
1. validate-env.P-TPR.py – compares installed packages & hashes vs manifest, emits artifact_emit & warning events
2. coverage-threshold.P-TPR.yaml – staged thresholds (baseline, target, stretch)
3. logging-path-map.P-TPR.json – enumerated code paths with log events (for deficit detection)
4. evidence-bundle on each CI run (.QSE/v2/Evidence/P-TPR/evidence-bundles/eb-<timestamp>.jsonl)
Actions:
- Implement env validation script + integrate into pre-test hook
- Add coverage threshold config → CI gating workflow
- Generate logging path map (static analysis + runtime sampling)
- Integrate evidence bundle generation in test workflow (session_start → task_end → session_summary)
Exit Criteria:
- CI fails on env drift or coverage below threshold
- Logging deficit detector reports <5% missing paths
- Evidence bundles present for ≥90% test runs

Phase 4: Optimize (Parallelization, Selective Execution, Performance)
Objectives:
- Reduce test wall-clock (partition + mark slow)
- Introduce mutation testing sampling for critical modules
- Optimize logging & evidence write overhead
Artifacts:
1. test-refactor-plan.P-TPR.md – classification: unit/fast, integration, system, slow, mutation candidates
2. parallelization-config.P-TPR.yaml – worker counts, affinity (group by DB usage)
3. mutation-sample-set.P-TPR.txt – list of high-value modules (e.g., core validators, env checks)
4. perf-benchmark.P-TPR.json – timings pre/post optimization (pytest total, slowest 10 tests, evidence generation latency)
Actions:
- Tag slow tests & introduce -m "not slow" subset baseline run
- Configure xdist / concurrency (avoid DB contention)
- Pilot mutation testing (e.g., mutmut or cosmic-ray) on sample set
- Profile evidence generation; cache static segments to lower overhead
Exit Criteria:
- Average test runtime reduced ≥30% vs baseline
- Slow test subset isolated & optional
- Mutation kill rate baseline established (track improvement)
- Evidence latency ≤ accepted threshold (define numeric target after measurement)

Phase 5: Govern & Iterate (Continuous Quality & Feedback Loops)
Objectives:
- Institutionalize audits & retrospectives (Spiral pattern)
- Maintain gate evolution & adapt thresholds (Golden Ratio balance)
- Sustain fractal consistency across new modules
Artifacts & Cadence:
1. governance-schedule.P-TPR.yaml – weekly quick audit, bi-weekly deep dive, monthly strategic review
2. velocity-baseline.P-TPR.yaml – story points vs hours (updated per sprint)
3. risk-register.P-TPR.yaml – risks, severity, mitigation, status (review each governance cycle)
4. lessons-log.P-TPR.jsonl – appended from vibe_learn / retrospectives
5. gate-history.P-TPR.csv – timeline of gate threshold changes
Actions:
- Automate generation of governance reports (scripts calling audits + formatting)
- Update velocity baseline after each sprint or major test batch
- Capture lessons immediately on failures (write to lessons-log)
- Periodically reassess golden ratio balance (cost vs impact of added tests)
Exit Criteria:
- Governance cycles executed for ≥2 consecutive intervals
- Velocity variance within planned tolerance band
- Risk register actively maintained (no stale high-severity > 2 cycles)
- Lessons integrated → measurable improvements (e.g., reduced flaky tests)

Environment Strategy (Option B Details)
- Keep existing lockfile (requirements.txt / poetry.lock / pip-tools compiled) as primary version pinning
- Generate secondary hash manifest (env-hash-manifest.P-TPR.json) with sha256 per dist file
- CI: validate-env.P-TPR.py performs: (1) compare versions, (2) hash check, (3) emit warning/error logs, (4) block if mismatch severity ≥ defined threshold
- Allows moderate agility (upgrade workflow: update lockfile → regen hashes → commit) without hermetic container overhead

Parallelization Strategy (Phase 4)
- Partition tests by marker: unit/integration/system/slow
- Use xdist: auto workers up to CPU-1; isolate DB-heavy tests sequentially
- Potential future: sharded coverage combination for accuracy

Risk Mitigation Overview
Top risks & counters:
1. Missing artifacts → Early Stabilize creation + checklist gating
2. Env drift → Hash manifest + validate-env script pre-test
3. Coverage stagnation → Incremental thresholds + per-module focused uplift
4. Logging gaps → Path map + deficit detector, enforce ≥90% coverage
5. Test runtime bloat → Partition & parallelization, slow marker adoption
6. Evidence overhead → Cache static sections, streaming JSONL writes
7. Governance decay → Scheduled audits encoded in governance-schedule
8. Flaky tests → Quarantine label + targeted stabilization tasks

Metrics & Success Signals
- Coverage trend (weekly): upward toward target
- Runtime trend: decreasing median suite time
- Drift incidents: zero blocked merges due to env mismatch
- Logging deficit %: trending to ≤5%
- Governance adherence: executed audits vs scheduled
- Mutation kill rate: baseline established then improved

Immediate Next Actions (Execution Order)
1. Create foundation artifacts (plan, checklist, evidence root, hash manifest stub)
2. Capture baseline coverage & logging + store in evidence directory
3. Draft COF 13D matrix & sacred gate definitions
4. Run initial UCL audit & link tasks in TaskMan
5. Implement validate-env script & integrate into CI pre-test
6. Define coverage thresholds & logging path map; enable gating
7. Begin optimization prep: classify tests, add markers
8. Schedule governance cycles & initialize risk register / lessons log

Tracking & Tooling Notes
- All new artifacts emit artifact_emit log entries (include hash + size)
- Each phase start/end logged (task_start / task_end) with evidence bundle hash
- Evidence bundles aggregated in .QSE/v2/Evidence/P-TPR/evidence-bundles
- Use existing unified logger; ensure redaction rules respected

Sacred Geometry Mapping (Quick Reference)
- Circle: Completeness = foundation + COF + gates + baseline evidence
- Triangle: Plan → Execute → Validate in each phase (checklist + tests + audits)
- Spiral: Lessons-log + velocity updates fueling iterative uplifts
- GoldenRatio: Balance sheet (value vs cost) reviewed in governance meetings
- Fractal: Consistent patterns (env validation, evidence emission, gating) replicated across new modules/tests

End of Plan
