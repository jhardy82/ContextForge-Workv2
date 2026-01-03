# Phase 1 Testing Platform Refactor – Completion & Foundation Solidification Plan

> Authoritative plan file for Phase 1 ("TPR Phase1 Completion + Foundation Solidification"). Establishes objectives, scope, execution steps, artifacts, acceptance criteria, event taxonomy, risks, rollback triggers, and implementation sequencing.
> Generated: 2025-11-23
> Version: 1.1.1 (Editorial – Live Progress Checklist added; integrity hash refreshed) – Applied 2025-11-23

---
## 1. Purpose
Create a reliable, reproducible, lower-latency test execution foundation that: (a) captures a precise baseline of current quality metrics, (b) introduces controlled fail‑fast mechanisms, (c) pilots property-based testing for future invariant coverage, (d) emits a formal foundation checkpoint artifact proving readiness, and (e) validates environment consistency pre-test to reduce flaky / polluted runs.

## 2. Scope (Phase 1 Only)
Included:
- Python pytest ecosystem (unit, integration, system, constitutional markers already present)
- Coverage (line + branch) extraction and storage
- Test duration profiling (p50/p90/p95/p99 + Top N slow tests)
- Flake detection (signature clustering + rate) – initial passive collection
- Environment validator (level 1: Python version, lock hash, OS, required env vars, seed, tool availability)
- Fail‑fast modes (off / soft / hard) wiring and gating semantics
- Property-based testing pilot (3 target invariants)
- Foundation checkpoint emission artifact
- Event taxonomy for structured logging of test platform operations

Excluded (deferred to Phase 2+):
- Marker system consolidation (large unused marker set cleanup)
- Spatial diversity matrix expansion (additional OS beyond current primary)
- Performance optimization of test harness beyond initial latency improvements
- Hypothesis global profile tuning & advanced shrinking strategies

## 3. High-Level Objectives (SMART)
1. Baseline Metrics Captured: Produce `baseline.metrics.json` with ≥95% metric field population and SHA-256 hash recorded.
2. Deterministic Fail-Fast: Provide configuration allowing reduction of mean failure detection time by ≥40% on seeded failure scenario.
3. Property Pilot Reliability: Add 3 invariant tests with <1s execution each and zero non-deterministic flake over 30 consecutive runs.
4. Environment Consistency: Validator rejects mismatched Python minor, missing env var, or lock hash mismatch in <1s with structured log event.
5. Foundation Checkpoint: Emit `foundation.checkpoint.(md|json)` proving readiness (all acceptance criteria satisfied, event log shows no deficits).

## 4. Detailed Execution Steps
### Step 1: Baseline Metrics Capture
Actions:
- Implement metrics extraction script `scripts/tests/collect_metrics.py`.
- Run full test suite once (no fail-fast), capture:
  - Coverage XML (line, branch)
  - Durations (collect per-test timing, compute percentiles + Top N slow tests)
  - Flake raw data: parse last N runs’ JUnit XML (if available) / start empty structure
  - Environment signature
- Write consolidated `baseline.metrics.json`.
- Compute SHA-256 hash → store in `baseline.metrics.hash` and embed in metrics file.
Artifacts:
- `coverage.xml`
- `durations.json`
- `flake.report.json` (initial structure)
- `env.signature.json`
- `baseline.metrics.json` / `baseline.metrics.hash`
Acceptance Criteria (AC-1): All metric fields present (null only where data genuinely absent); hash stored; event log contains `metrics_capture_complete`.

### Step 2: Fail-Fast Wiring (off / soft / hard)
Modes:
- off: Default; no early termination.
- soft: Fail immediately on first failure but still emit partial metrics & summary.
- hard: Up to `--maxfail=1` AND skip remaining collection steps; emit emergency summary + rollback evaluation.
Implementation:
- Config surfaces: env var `TPR_FAILFAST_MODE` + CLI flag `--failfast-mode` (CLI overrides env).
- Soft mode: wrap pytest call, intercept first failure via hook, set flag to run minimal metrics script.
- Hard mode: rely on pytest `-x` + disable durations deep profiling (fast exit).
Artifacts:
- `failfast.summary.json` (for soft/hard) including: mode, first failure test id, elapsed until detection.
Acceptance Criteria (AC-2): In seeded failure scenario, soft reduces detection time ≥40%; hard reduces ≥60%; summary contains mandatory fields; event log has `failfast_mode_applied` and `early_exit_detected` when triggered.

### Step 3: Property-Based Testing Pilot
Targets (choose deterministic domain areas):
1. **Round-trip Serialization** (idempotence): encode→decode returns original object.
2. **Monotonic Sequence Invariant** (ordering): generated sequence elements always non-decreasing.
3. **Boundary Handling** (robust parse): parser never throws on generated in-range edge values.
Design:
- Hypothesis tests with fixed seed `TPR_SEED` for determinism in CI baseline; nightly fuzz job removes seed for exploration.
- Guardrail: each property test <1s avg runtime.
Artifacts:
- `property.results.json` capturing: test name, examples run, falsifying_examples (if any), runtime stats, seed used.
Acceptance Criteria (AC-3): All 3 property tests pass 30 consecutive deterministic runs; runtime <1s each; no flake events logged; property results file includes performance metrics & zero falsifying examples.

### Step 4: Foundation Checkpoint Emission
Conditions:
- AC-1..AC-3 met
- Environment validator passes
- No high severity risks unresolved
Action:
- Generate `foundation.checkpoint.md` (human-readable) + `foundation.checkpoint.json` (machine) summarizing metrics, fail-fast test delta, property pilot status, event coverage stats, risk matrix.
Acceptance Criteria (AC-4): Checkpoint files exist, contain all sections, log includes `foundation_checkpoint_emitted`; coverage ladder baseline recorded.

### Step 5: CI Pre-Test Environment Validation (Level 1)
Validator checks prior to any test run:
- Python version == expected minor
- lock hash matches recorded baseline (`requirements.lock.hash` or `poetry.lock` hash)
- required env vars present (list defined below)
- reproducibility seed present & numeric
- OS classification (record for spatial diversity future expansion)
Failure emits structured event and halts tests (except override `TPR_ENV_VALIDATE=skip`).
Artifacts:
- `env.signature.json` (produced once; reused)
- On failure: `env.validation.failure.json`
Acceptance Criteria (AC-5): Mismatch aborts before tests start; success logs `environment_validated`; failure logs include reason codes; avg runtime <1s.

## 5. Additional Considerations (Supporting Controls)
1. Parallelization Guardrails: Defer aggressive parallel until flake classification stable; maintain deterministic ordering in metric collection.
2. `lock_sources` Enrichment: Include primary lock file hash + Python version + platform tag → persisted in env signature.
3. Coverage Ladder: `coverage-ladder.yaml` defines baseline (current), target (+Δ for next phase), enforcement gate (fail if regression > configured tolerance or improvement target missed after horizon date).
4. Marker Cleanup (Deferred): Inventory 283 markers; Phase 1 only records usage stats to `markers.usage.json`.

## 6. Artifacts Summary
| Artifact | Purpose | Generation Step | Hash? | Mandatory |
|----------|---------|-----------------|-------|-----------|
| coverage.xml | Raw coverage data | 1 | no | yes |
| durations.json | Performance profiling | 1 | optional | yes |
| flake.report.json | Flake signature seed | 1 | yes (embedded) | yes |
| env.signature.json | Environment determinism | 1 / 5 | yes | yes |
| baseline.metrics.json | Consolidated baseline | 1 | yes | yes |
| failfast.summary.json | Early exit context | 2 | yes | conditional |
| property.results.json | Property test outcomes | 3 | yes | yes |
| foundation.checkpoint.md/json | Readiness proof | 4 | yes | yes |
| coverage-ladder.yaml | Baseline + target | 1 (after metrics) | optional | yes |
| env.validation.failure.json | Diagnose validation issue | 5 | yes | conditional |
| events.log.jsonl | Structured event stream | all | rolling | yes |
| markers.usage.json | Usage statistics | 1 (post scan) | optional | yes |

## 7. Event Taxonomy (Minimum Set)
Each event: JSONL line with `timestamp, event, context` + fields.
Required Events:
- `metrics_capture_start/complete`
- `environment_validation_start/ok/fail`
- `failfast_mode_applied`
- `early_exit_detected` (hard/soft)
- `property_test_start/complete`
- `flake_scan_complete`
- `coverage_ladder_recorded`
- `foundation_checkpoint_emitted`
- `logging_deficit` (if any expected events missing)
- `risk_trigger` (rollback evaluation initiated)

## 8. Acceptance Criteria Consolidated
| ID | Criterion | Verification Method |
|----|-----------|--------------------|
| AC-1 | Baseline metrics produced & hashed; event logged | Inspect artifacts + events.log.jsonl |
| AC-2 | Soft ≥40% & Hard ≥60% failure detection improvement | Controlled failure scenario timing comparison |
| AC-3 | 3 property tests deterministic pass 30 runs <1s each | CI loop + `property.results.json` runtime stats |
| AC-4 | Foundation checkpoint emitted after all prior criteria met | Presence of both checkpoint files + event |
| AC-5 | Environment validator halts on mismatch <1s | Inject mismatch; verify failure artifact & event |
| AC-6 | Coverage ladder baseline & target recorded | `coverage-ladder.yaml` + event present |
| AC-7 | Event coverage: 100% required events seen | Query events log for taxonomy completion |

## 9. Risk & Mitigation Matrix
| Risk | Impact | Likelihood | Mitigation | Trigger Event |
|------|--------|-----------|-----------|---------------|
| Missing plan file again | High | Low | Version control + hash audit | N/A (Plan now created) |
| Flaky property tests | Medium | Low | Deterministic seed + nightly fuzz isolated | `property_test_complete` mismatch rates |
| Fail-fast hides systemic failures | Medium | Medium | Hard mode blocks metrics; soft mode preserves partial metrics | `early_exit_detected` + absence of metrics artifact warning |
| Coverage regression | Medium | Medium | Ladder enforcement gate | `coverage_ladder_recorded` then gate failure event |
| Environment drift | High | Medium | Validator with abort + hash checks | `environment_validation_fail` |
| Overhead from metrics collection | Low | Medium | Optimize extraction sequence; allow skip flag | `metrics_capture_complete` duration > threshold |
| Parallelization induced race | High | Low (deferred) | Guardrails; enable after flake classification stable | Future Phase event |

## 10. Rollback Triggers & Actions
Triggers (any):
- Coverage drop > configured tolerance.
- Flake rate spike > threshold after fail-fast introduction.
- Property test false failure rate >0.5% across last 30 deterministic runs.
Rollback Actions:
1. Disable fail-fast (set mode=off).
2. Re-run baseline metrics with seed locked.
3. Open incident log entry `risk_trigger` including snapshot of artifacts.
4. Re-evaluate ladder targets; adjust Phase 2 scheduling.

## 11. Implementation Sequencing (Ordered)
1. Create artifact directories & events log scaffold.
2. Implement environment validator (step can run standalone) – generate `env.signature.json`.
3. Run baseline metrics capture script (Step 1) – produce artifacts + ladder file.
4. Wire fail-fast modes and produce detection benchmark scenario.
5. Implement property-based tests & results aggregator.
6. Emit foundation checkpoint after AC-1..AC-3 satisfied.
7. Integrate CI gates (validator → tests → metrics post → ladder enforcement).
8. Add rollback monitoring hooks & thresholds.
9. (Deferred) Marker usage scan & parallelization evaluation.

## 12. Configuration Keys
| Key | Description | Default |
|-----|-------------|---------|
| TPR_FAILFAST_MODE | off|soft|hard | off |
| TPR_SEED | Deterministic seed for property tests | 12345 |
| TPR_ENV_VALIDATE | enable|skip | enable |
| TPR_MAX_FAIL_FAST_IMPROVEMENT_TARGET | Soft fail target (%) | 40 |
| TPR_HARD_FAIL_FAST_IMPROVEMENT_TARGET | Hard fail target (%) | 60 |
| TPR_COVERAGE_BASELINE | Numeric baseline (line %) | (captured) |
| TPR_COVERAGE_TARGET | Phase 1 target (line %) | (baseline + Δ) |
| TPR_COVERAGE_TOLERANCE_DROP | Allowed regression (%) | 1 |
| TPR_PROPERTY_RUNTIME_THRESHOLD_MS | Max avg runtime property test | 1000 |
| TPR_FLAKE_RATE_THRESHOLD | Flake spike rollback trigger | 2% |

## 13. Environment Validator Required Fields
- Python minor version (e.g., 3.11.x)
- Lock file hash (e.g., `poetry.lock` SHA256 or requirements freeze hash)
- OS name + architecture
- Required env vars: `TPR_SEED`, `TPR_FAILFAST_MODE`, (others: `DATABASE_URL` if integration tests rely)
- Installed tool versions: pytest, hypothesis, coverage
- Timestamp, monotonic start time

## 14. Reproducibility & Determinism
- Seed captured in `env.signature.json` and referenced in property results.
- All generated artifacts hashed; checkpoint embeds hash listing.
- Events log includes correlation IDs for each run.

## 15. Logging Standards Integration
All events follow unified logger pattern: `logger.info(event, **fields)` with automatic redaction of secrets (see logging instructions). Coverage: aim ≥90% of execution paths emitting at least one defined event.

## 16. Future Phase Hooks (References Only)
Phase 2+: marker cleanup automation; parallelization benchmarking & enabling; advanced property strategies (stateful models); spatial diversity expansion (Windows, Linux, macOS matrix); mutation testing integration.

## 17. Definition of Done (Phase 1)
Phase 1 is complete when:
- All AC-1..AC-7 satisfied
- All mandatory artifacts exist with hashes
- Foundation checkpoint emitted & committed
- Rollback triggers configured & documented
- CI pipeline enforces validator + ladder gate
- Event log shows complete taxonomy coverage without deficits

---
## 18. Immediate Next Actions (Implementation Kickoff)
1. Implement environment validator script.
2. Implement metrics collection script & produce baseline artifacts.
3. Create coverage ladder file with baseline + target.
4. Integrate fail-fast configuration hooks.
5. Add property-based tests & aggregator.
6. Emit foundation checkpoint after criteria satisfied.

### 18.1 Live Progress Checklist (Status)

Legend: [x] = done, [ ] = pending

- [x] Implement environment validator script
- [x] Implement metrics collection script & produce baseline artifacts
- [x] Create coverage ladder file with baseline + target
- [x] Integrate fail-fast configuration hooks
- [x] Add property-based tests & aggregator
- [x] Emit foundation checkpoint after criteria satisfied

Last updated: 2025-11-24T09:30:00Z

---
## 19. File Integrity
This document is now the authoritative Phase 1 plan. Commit immediately; future changes require version bump + changelog entry.

SHA256: 4A0D47E1235751AD6037D4E961BC069590A6A3187E533785B6E464960939869A (Version 1.1.1 integrity lock, computed 2025-11-24)

---
## 20. COF 13-Dimensional Snapshot (Phase 1 Test Platform Refactor)
| Dimension | Summary (Phase 1 Context) | Evidence Artifact(s) |
|-----------|---------------------------|----------------------|
| Motivational | Reduce latency of failure detection; establish deterministic baseline & reliability foundation prior to Phase 2 optimization. | foundation.checkpoint.*, baseline.metrics.json |
| Relational | Depends on existing pytest suite, logging standards, coverage extraction; provides upstream data to future parallelization, marker cleanup, mutation testing. | coverage.xml, events.log.jsonl |
| Situational | Current harness has incomplete governance overlays (no COF/UCL sections, no fail-fast gating, limited property invariants); moderate flake risk due to environment drift. | env.signature.json, flake.report.json |
| Resource | Team time: small focused iteration (< 2 days). Tools: pytest, hypothesis, coverage, Python 3.11, unified logger. Seed & lock file ensure constrained variability. | env.signature.json |
| Narrative | Story: “Establish indisputable, evidence-backed test platform foundation enabling faster confident iteration.” Communicates readiness via checkpoint artifact. | foundation.checkpoint.md |
| Recursive | Spiral: deterministic baseline → measure improvements → elevate thresholds (coverage ladder). Feedback loops: flake classification & property pass rates inform Phase 2. | coverage-ladder.yaml, property.results.json |
| Computational | Algorithms: percentile computation, hash generation (SHA-256), property-based example generation under fixed seed, failure detection timing deltas. | durations.json, baseline.metrics.json |
| Emergent | Potential discovery: hidden slow tests, latent environment variability, opportunity to tighten seed & coverage gates. | durations.json, env.validation.failure.json (if any) |
| Temporal | Executed early to unblock later performance and parallelization initiatives; baseline timestamp embedded in metrics checkpoint. | foundation.checkpoint.json |
| Spatial | Single OS/arch captured (Phase 1); spatial matrix expansion deferred; env signature records current platform. | env.signature.json |
| Holistic | Integrates environment validation, metrics, fail-fast, property pilot, coverage ladder into one deterministic envelope. | All mandatory artifacts + events taxonomy |
| Validation | AC-1..AC-7 map directly to artifact presence & event stream completeness; ladder gate ensures ongoing compliance. | events.log.jsonl, coverage-ladder.yaml |
| Integration | Outputs consumed by CI gates & future Phase 2 tasks (parallelization, marker cleanup, mutation testing). | baseline.metrics.json, coverage-ladder.yaml |

Completeness: 13/13 dimensions addressed (no placeholders). UCL check: anchored (parent initiative: Test Platform Refactor), no cycles (linear sequencing), evidence complete (artifacts & events taxonomy defined).

## 21. Sacred Geometry Alignment
| Pattern | Applied Meaning (Phase 1) | Supporting Mechanism | Proof Artifact/Event |
|---------|---------------------------|----------------------|-----------------------|
| Triangle (Stability) | Three core pillars: Environment Validation → Deterministic Metrics → Checkpoint Emission. | Sequenced steps 2/1/4; fail-fast modes protect stability. | foundation.checkpoint.emitted event |
| Circle (Completeness) | All mandatory artifacts + events taxonomy produced before declaring DoD. | AC-1..AC-7 gating. | foundation.checkpoint.*, events.log.jsonl completeness query |
| Spiral (Iteration) | Coverage ladder and property run reliability feed future targets. | coverage-ladder.yaml baseline + target. | coverage_ladder_recorded event |
| Golden Ratio (Balance) | Focus on high-leverage reliability controls (20%) yielding majority stability gains; defers non-essential optimizations. | Explicit Phase 1 scope boundaries. | scope section + risk matrix |
| Fractal (Modularity) | Reusable scripts (validator, metrics collector, property aggregator) scale in later phases unchanged. | Script separation under `scripts/tests/`. | artifact listing + future phase hooks |

## 22. UCL Compliance Checklist (This Plan & Execution Artifacts)
| Law | Requirement | Plan Implementation | Verification Method |
|-----|-------------|---------------------|--------------------|
| No Orphans | Context anchored to parent project / refactor initiative. | Section 1 Purpose + header referencing Phase 1. | Repository hierarchy & commit message referencing refactor epic. |
| No Cycles | Sequencing flows forward; rollback only resets state, not forming loops. | Section 11 linear sequencing + rollback triggers separate. | Review of sequencing & absence of recursive artifact generation loop. |
| Complete Evidence | Every criterion maps to artifact + event; integrity hash recorded. | Artifacts summary (Sec 6) + events taxonomy (Sec 7) + integrity (Sec 19). | Query events.log.jsonl for all required events; verify artifact hashes. |
| Deterministic Closure | Definition of Done enumerates closure conditions with hash lock. | Section 17 & Integrity Section. | Cross-check DoD + final SHA256. |
| Traceability | Version bump & changelog protocol (Sec 24) ensure lineage. | Section 24 added. | Presence of version & changelog entry. |

## 23. Quality Gates Matrix (Phase 1)
| Gate | Type | Enforcement Level | Input Artifacts | Trigger Event | Failure Response |
|------|------|-------------------|-----------------|---------------|------------------|
| Environment Validation | Pre-test | Hard (abort) | env.signature.json, lock hash | environment_validation_fail | Halt tests; emit failure artifact |
| Coverage Baseline Regression | Post-test | Hard (threshold) | coverage.xml, coverage-ladder.yaml | coverage_ladder_recorded + gate eval | Fail job; rollback evaluation |
| Fail-Fast Improvement | Benchmark | Advisory (metrics) | failfast.summary.json | failfast_mode_applied | If delta < targets: log optimization backlog item |
| Property Stability | Reliability | Advisory (trend) | property.results.json | property_test_complete | If flake >0: seed audit + isolation run |
| Event Taxonomy Completeness | Observability | Hard (audit) | events.log.jsonl | metrics_capture_complete (final audit) | Emit logging_deficit & block checkpoint |
| Artifact Hash Integrity | Integrity | Hard | *.hash, foundation.checkpoint.json | foundation_checkpoint_emitted | Abort release; recompute & investigate |

## 24. Versioning & Changelog Protocol
Versioning Rules:
- Increment minor version for governance structure augmentation (this change: 1.0 → 1.1).
- Increment patch for editorial or formatting fixes not altering semantics.
- Increment major if acceptance criteria set (AC-1..AC-7) materially change.

Changelog File: `CHANGELOG.testing-platform-refactor.md`
Entry Template:
```
## [1.1] – 2025-11-24
### Added
- COF 13-dimensional snapshot section.
- Sacred Geometry alignment mapping.
- UCL compliance checklist.
- Quality Gates matrix clarifying enforcement.
- Versioning & changelog protocol.
- Enhancement Appendix Definition of Done.

### Integrity
- Updated plan SHA256: <POPULATED_AFTER_HASH>
```
Commit Message Convention:
`chore(tpr-phase1): governance enhancements v1.1 (COF/UCL/geometry quality gates)`

## 25. Enhancement Appendix Definition of Done (Governance Augmentation)
Enhancement phase (v1.1) is complete when:
1. Sections 20–25 present with no placeholder markers.
2. Version line updated (header) & changelog entry prepared.
3. SHA256 computed AFTER augmentation & replaced in Section 19.
4. Events taxonomy unchanged (non-destructive) – diff confirms only additive changes.
5. All artifact references cross-checked (no broken names, all appear in Artifacts Summary or newly justified governance-only artifacts).
6. COF snapshot covers all 13 dimensions substantively (no blank cells).
7. Quality Gates matrix aligns exactly with AC mappings (consistency check between Sec 8 & Sec 23).
8. Git commit includes hash, version bump, and references governance additions.
9. No logging_deficit event emitted during augmentation scripts (if any executed).
10. UCL checklist passes (traceability, evidence completeness) verified via pre-commit hook (planned Phase 2 extension – manual verification for now).

Status: All governance sections inserted; pending hash computation & changelog external file creation.

---
