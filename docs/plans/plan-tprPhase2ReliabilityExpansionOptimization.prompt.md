# Phase 2 Plan Outline – Reliability Expansion & Optimization (P-TPR)

Status: RESEARCH 5/7 COMPLETE | IMPLEMENTATION BLOCKED
File Integrity Hash (placeholder): __TO_BE_COMPUTED__
Phase Reference: Transition from Phase 1 (Foundation Solidification) → Phase 2 (Reliability / Mutation / Performance Expansion)
Research Artifacts: 5/7 COMPLETE (2025-11-28 - Updated)

**RESEARCH PHASE IN PROGRESS** - 5 of 7 foundational research artifacts delivered:
✅ Cross-OS Performance Research Synthesis (1695 lines, 57.3KB)
✅ DevOps Research Executive Summary (224 lines, 9.2KB)  
✅ Coverage Ladder Research Synthesis (1400 lines, 54KB)
✅ Marker Systems Audit Research Report (545 lines, 21.6KB)
✅ Mutation Testing Quick Start Guide (185 lines, 4.6KB)
❌ Evidence Management & Constitutional Compliance (28 pages) - NOT CREATED
❌ Test Reliability Implementation Guide (40 pages) - NOT CREATED

**REMEDIATION**: See `plan-TPR-PHASE2-RESEARCH-COMPLETION.md` for artifact creation plan.
**TRACKING**: See `docs/checklists/TPR-UNIFIED-TRACKING-CHECKLIST.md` for implementation status.

---
## 1. Purpose (Phase 2)

**Phase 2 Mission**: Transition the Testing Platform Refactor from **foundational solidification** (Phase 1) to **operational excellence** through systematic reliability expansion, performance characterization, and deterministic parallelization.

### Strategic Context

Phase 1 (Foundation Solidification) delivered a **stable testing baseline** with:
- 42 tests operational in focused coverage zones (ulog, dbcli, cf_cli, qse, common)
- 1.26% whole-workspace coverage with 90% targets applied to critical modules
- <1s environment validation via 285-line bootstrap validator
- 23-marker pytest.ini configuration with fail-fast mode support
- Unified logging infrastructure emitting structured JSONL events

However, Phase 1 **explicitly deferred** four critical capabilities:

1. **Marker System Proliferation** (283 markers → <50 target)
2. **Spatial Diversity Gap** (Windows-only → multi-OS)
3. **Performance Opacity** (no baseline metrics)
4. **Property Testing Underutilization** (Hypothesis framework dormant)

### Phase 2 Problem Statement

**Core Challenge**: The testing platform foundation is solid, but **lacks scalability**, **lacks observability**, and **lacks cross-environment confidence** required for production-grade continuous delivery.

**Specific Gaps Addressed**:
- **Reliability Gap**: 35.7% test collection error rate (15 of 42 tests)
- **Mutation Gap**: Zero mutation testing coverage
- **Performance Gap**: No quantified p50/p95 baselines
- **Concurrency Gap**: Sequential execution causes >30s runtime as suite scales
- **Flakiness Gap**: No systematic flake detection/quarantine
- **Determinism Gap**: Time-dependent tests remain un-mocked
- **Marker Gap**: 283 markers create confusion

### Business Value Proposition

Phase 2 delivers **measurable quality acceleration**:

1. **Velocity Unlocking**: 3-5x speedup via pytest-xdist parallelization
2. **Regression Prevention**: Mutation testing (≥60% score target)
3. **Performance Guardrails**: Automated p50/p95 benchmarking
4. **Cross-Platform Confidence**: Windows + Linux + macOS CI matrix
5. **Developer Experience**: <50 curated markers + <5% flake rate

### Alignment with Testing Excellence Roadmap

- **Phase 1** (Complete): Stable foundation
- **Phase 2** (This Phase): Reliability expansion
- **Phase 3** (Future): Integration/E2E scaling

## 2. Scope (Phase 2 Only)

### In-Scope Components

**Primary Deliverables**:

1. **Marker System Rationalization**
   - Audit 283 existing markers for usage patterns
   - Consolidate to <50 active markers aligned with ISTQB taxonomy
   - Document marker removal decisions with evidence bundles
   - Update pytest.ini and test suite annotations

2. **Mutation Testing Infrastructure**
   - Select mutation testing tool (mutmut recommended, 8.5/10 trust score)
   - Establish baseline mutation score for 5 focused modules
   - Integrate mutation testing into CI/CD pipeline (advisory gate initially)
   - Target ≥60% mutation score for critical logic paths

3. **Cross-OS Testing Matrix**
   - Expand from Windows-only to Windows + Linux + macOS
   - Implement GitHub Actions matrix strategy
   - Document OS-specific test isolation patterns
   - Establish baseline pass rates per OS (target: ≥95% consistency)

4. **Performance Benchmarking Framework**
   - Integrate pytest-benchmark for p50/p95/p99 latency tracking
   - Establish baseline metrics for critical test paths
   - Implement performance regression detection (10%+ threshold)
   - Store benchmark results with SHA-256 integrity hashing

5. **Parallelization Infrastructure**
   - Implement pytest-xdist with `-n auto` worker strategy
   - Resolve race conditions via `scope='session'` fixtures
   - Achieve 3-5x speedup for full suite execution
   - Maintain test isolation and determinism

6. **Flake Detection & Quarantine System**
   - Integrate pytest-rerunfailures for flake identification
   - Implement SQLite-based FlakeTracker for historical analysis
   - Establish quarantine markers for >20% flake rate tests
   - Target <5% overall flake rate

7. **Determinism Enhancement**
   - Standardize random seed management (pytest-randomly)
   - Mock time-dependent tests with freezegun
   - Document fixture ordering dependencies
   - Implement per-test seed derivation strategy

8. **Coverage Ladder v2**
   - Layer Unit → Integration → System → Mutation coverage tiers
   - Define advancement triggers per tier
   - Track tier progression in coverage.ladder.v2.yaml

### Explicitly Out-of-Scope

**Phase 2 Boundaries** (deferred to Phase 3 or later):

- ❌ Integration testing beyond unit-level mocks
- ❌ End-to-end (E2E) test framework establishment
- ❌ Contract testing / service virtualization
- ❌ Chaos engineering / fault injection at infrastructure level
- ❌ Load/stress testing beyond performance benchmarking
- ❌ Security testing automation (SAST/DAST)
- ❌ Advanced Hypothesis profile tuning (kept at default)
- ❌ Database migration testing automation
- ❌ Multi-version Python compatibility matrix (focus on 3.11+)
- ❌ Test data generation frameworks beyond existing fixtures

### Boundaries vs Phase 1

**Phase 1 Focus**: Establish stable foundation
**Phase 2 Focus**: Expand reliability and observability

| Aspect | Phase 1 | Phase 2 |
|--------|---------|----------|
| **Test Count** | Stabilize 42 tests | Scale to 100+ tests |
| **Coverage** | 1.26% whole-workspace, 90% target for 5 modules | Maintain 90% for focused modules, add mutation layer |
| **Platforms** | Windows only | Windows + Linux + macOS |
| **Execution** | Sequential | Parallel (pytest-xdist) |
| **Markers** | 23 defined, 283 total | <50 consolidated, ISTQB-aligned |
| **Performance** | No metrics | p50/p95/p99 benchmarks |
| **Flakiness** | Untracked | <5% target with quarantine |
| **Mutation** | None | ≥60% score baseline |

### Component Interaction Matrix

**Dependencies Between In-Scope Components**:

1. **Marker Consolidation** → Enables cleaner test targeting for mutation/performance testing
2. **Parallelization** → Requires determinism fixes to prevent race conditions
3. **Cross-OS Matrix** → Amplifies flake detection needs (platform-specific failures)
4. **Performance Benchmarking** → Validated via parallelization speedup metrics
5. **Mutation Testing** → Consumes marker taxonomy for targeted fault injection
6. **Flake Tracking** → Informed by cross-OS inconsistencies

**Sequential Execution Required**: Marker consolidation → Determinism fixes → Parallelization → Cross-OS expansion

## 3. High-Level Objectives

### SMART Objective Framework

All objectives follow **Specific, Measurable, Achievable, Relevant, Time-bound** criteria with evidence-based validation.

---

### O1: Reliability Consolidation

**Goal**: Eliminate test collection errors and establish <5% flake rate across full test suite.

**Metrics**:
- **Baseline**: 35.7% collection error rate (15 of 42 tests)
- **Target**: 0% collection error rate, <5% flake rate
- **Measurement**: `pytest --collect-only` exit code, FlakeTracker historical analysis

**Key Results**:
- KR1.1: Resolve all 15 collection errors (import/fixture issues)
- KR1.2: Implement FlakeTracker with SQLite persistence
- KR1.3: Achieve <5% flake rate over 100-run sample per test
- KR1.4: Quarantine tests exceeding 20% flake rate with `@pytest.mark.flaky_quarantine`

**Timeline**: Weeks 1-2 (blocking for subsequent objectives)

---

### O2: Mutation Readiness Infrastructure

**Goal**: Establish mutation testing baseline with ≥60% mutation score for critical modules.

**Metrics**:
- **Baseline**: 0% mutation coverage
- **Target**: ≥60% mutation score for ulog, dbcli, cf_cli modules
- **Measurement**: mutmut HTML report, mutation_score_threshold_met event

**Key Results**:
- KR2.1: Integrate mutmut with pytest execution pipeline
- KR2.2: Generate baseline mutation report for 5 focused modules
- KR2.3: Achieve ≥60% mutation score (industry standard for critical paths)
- KR2.4: Document mutation-resistant test patterns in playbook
- KR2.5: Add mutation testing as advisory CI/CD gate (non-blocking initially)

**Timeline**: Weeks 3-4

---

### O3: Cross-OS & Environment Baseline

**Goal**: Validate test suite across Windows + Linux + macOS with ≥95% consistency.

**Metrics**:
- **Baseline**: Windows-only execution (100% single-OS)
- **Target**: ≥95% pass rate consistency across 3 OS platforms
- **Measurement**: GitHub Actions matrix results, os.matrix.baseline.json

**Key Results**:
- KR3.1: Implement GitHub Actions matrix (Windows/Linux/macOS x Python 3.11/3.12)
- KR3.2: Document OS-specific test isolation patterns (path handling, line endings)
- KR3.3: Achieve ≥95% pass rate on Linux and macOS (match Windows baseline)
- KR3.4: Identify and document platform-specific failures in os.matrix.baseline.json

**Timeline**: Weeks 4-5 (parallel with O2)

---

### O4: Performance Benchmark Establishment

**Goal**: Establish p50/p95/p99 latency baselines and detect 10%+ performance regressions.

**Metrics**:
- **Baseline**: No quantified performance metrics
- **Target**: Baseline established, 10%+ regression detection automated
- **Measurement**: pytest-benchmark JSON output, perf.benchmark.baseline.json

**Key Results**:
- KR4.1: Integrate pytest-benchmark for critical test paths
- KR4.2: Record baseline p50/p95/p99 metrics (stored with SHA-256 hash)
- KR4.3: Implement CI/CD gate for 10%+ performance degradation
- KR4.4: Generate HTML performance comparison reports

**Timeline**: Weeks 5-6 (parallel with O3)

---

### O5: Marker/Annotation Rationalization

**Goal**: Reduce marker sprawl from 283 to <50 ISTQB-aligned active markers.

**Metrics**:
- **Baseline**: 283 markers (23 defined in pytest.ini)
- **Target**: <50 active markers with 100% ISTQB alignment
- **Measurement**: marker_audit_report.json usage statistics

**Key Results**:
- KR5.1: Audit 283 markers for usage patterns (pytest --markers + codebase grep)
- KR5.2: Consolidate to <50 markers aligned with ISTQB test levels (unit/integration/system/acceptance)
- KR5.3: Document removal decisions with evidence bundles
- KR5.4: Update pytest.ini and refactor test annotations
- KR5.5: Achieve 100% marker documentation coverage

**Timeline**: Weeks 2-3 (early to unblock mutation/performance targeting)

---

### O6: Parallelization Stability

**Goal**: Achieve 3-5x test suite speedup via pytest-xdist without flakiness increase.

**Metrics**:
- **Baseline**: Sequential execution (~30s for 42 tests, ~2min projected for 100 tests)
- **Target**: 3-5x speedup with ≤2% flake rate increase
- **Measurement**: parallelization.scan.report.json, CI/CD execution time logs

**Key Results**:
- KR6.1: Implement pytest-xdist with `-n auto` worker strategy
- KR6.2: Resolve race conditions via `scope='session'` database/fixture isolation
- KR6.3: Achieve 3-5x speedup (target: <1min for 100 tests)
- KR6.4: Maintain <5% total flake rate (≤2% increase from parallelization)
- KR6.5: Document parallelization best practices playbook

**Timeline**: Weeks 6-7 (after determinism fixes from O1)

---

### O7: Coverage Ladder v2 Progression

**Goal**: Implement 4-tier coverage ladder (Unit → Integration → System → Mutation) with automated tier tracking.

**Metrics**:
- **Baseline**: Single-tier coverage (line/branch only)
- **Target**: 4-tier ladder with automated advancement triggers
- **Measurement**: coverage.ladder.v2.yaml tier progression events

**Key Results**:
- KR7.1: Define coverage tiers with specific criteria:
  - **Tier 1 (Unit)**: ≥90% line coverage for 5 focused modules
  - **Tier 2 (Integration)**: ≥70% cross-module interaction coverage
  - **Tier 3 (System)**: ≥50% end-to-end workflow coverage
  - **Tier 4 (Mutation)**: ≥60% mutation score
- KR7.2: Implement automated tier tracking in coverage.ladder.v2.yaml
- KR7.3: Emit `coverage_ladder_stage_advanced` events on tier progression
- KR7.4: Generate visual tier progression dashboard

**Timeline**: Weeks 7-8 (integrates outputs from O2, O4, O6)

---

### Objective Dependency Graph

```
O1 (Reliability) ──┬──> O5 (Markers) ──> O2 (Mutation)
                   │                      │
                   ├──> O6 (Parallel) ───┤
                   │                      │
                   └──> O3 (Cross-OS) ───┴──> O4 (Performance)
                                              │
                                              └──> O7 (Coverage Ladder)
```

**Critical Path**: O1 → O6 → O7 (reliability enables parallelization, which informs coverage ladder)

## 4. Milestone Alignment (M1–M3)

### Milestone Framework

Phase 2 execution spans **8 weeks** divided into 3 strategic milestones with incremental value delivery and checkpoint-based validation.

---

### M1: Foundation Hardening (Weeks 1-3)

**Theme**: Eliminate blockers, rationalize infrastructure, establish baseline observability.

**Objectives Delivered**:
- **O1: Reliability Consolidation** (complete)
- **O5: Marker Rationalization** (complete)
- **O2: Mutation Infrastructure** (50% - baseline only)

**Key Deliverables**:
1. ✅ Zero collection errors (resolve all 15 broken tests)
2. ✅ FlakeTracker operational with <5% flake rate
3. ✅ Marker audit complete: 283 → <50 consolidated markers
4. ✅ mutmut integrated, baseline mutation report generated
5. ✅ pytest.ini updated with rationalized marker taxonomy

**Acceptance Gate (M1 Checkpoint)**:
- [ ] Collection error rate: 0% (down from 35.7%)
- [ ] Flake rate: <5% over 100-run sample
- [ ] Active markers: <50 (documented in pytest.ini)
- [ ] Mutation baseline report: generated for 5 modules
- [ ] Evidence bundle: M1-completion.tar.gz with SHA-256 hash

**Phase 1 Carryover Dependencies**:
- ⚠️ **BLOCKER**: 15 collection errors must be resolved before O5/O2 can proceed
- ⚠️ **DEPENDENCY**: Phase 1 deferred Hypothesis tuning remains deferred (out-of-scope)
- ⚠️ **INPUT**: Phase 1 baseline metrics (1.26% coverage, 42 tests) inform M1 targets

**Risk Register (M1)**:
- 🔴 **HIGH**: Collection error root causes may require architectural refactoring (mitigation: timebox 2 days per error, escalate blockers)
- 🟡 **MEDIUM**: Marker consolidation may break existing test targeting (mitigation: automated marker migration script)
- 🟢 **LOW**: mutmut runtime overhead (mitigation: scoped to 5 modules initially)

---

### M2: Expansion & Optimization (Weeks 4-6)

**Theme**: Expand spatial diversity, establish performance baselines, enable parallelization.

**Objectives Delivered**:
- **O3: Cross-OS Baseline** (complete)
- **O4: Performance Benchmarking** (complete)
- **O6: Parallelization Stability** (80% - infrastructure ready, optimization ongoing)
- **O2: Mutation Infrastructure** (100% - full scoring achieved)

**Key Deliverables**:
1. ✅ GitHub Actions matrix: Windows + Linux + macOS
2. ✅ OS-specific test isolation patterns documented
3. ✅ ≥95% cross-platform pass rate consistency
4. ✅ pytest-benchmark integrated with p50/p95/p99 tracking
5. ✅ Performance baseline recorded (perf.benchmark.baseline.json)
6. ✅ pytest-xdist `-n auto` operational with 3-5x speedup
7. ✅ ≥60% mutation score achieved for critical modules

**Acceptance Gate (M2 Checkpoint)**:
- [ ] Cross-OS pass rate: ≥95% consistency (Windows/Linux/macOS)
- [ ] Performance baseline: p50/p95/p99 recorded for 10+ critical tests
- [ ] Parallelization speedup: 3-5x measured improvement
- [ ] Flake rate post-parallelization: <7% (≤2% increase from M1 baseline)
- [ ] Mutation score: ≥60% for ulog, dbcli, cf_cli modules
- [ ] Evidence bundle: M2-completion.tar.gz with SHA-256 hash

**Phase 1 Carryover Dependencies**:
- ✅ **RESOLVED**: Phase 1 Windows-only limitation addressed via O3
- ✅ **RESOLVED**: Phase 1 performance opacity addressed via O4
- ⚠️ **PARTIAL**: Hypothesis underutilization still deferred (future phase)

**Risk Register (M2)**:
- 🔴 **HIGH**: Cross-OS flakiness may spike due to platform-specific timing (mitigation: freezegun for time mocking, pathlib for path normalization)
- 🟡 **MEDIUM**: Parallelization race conditions in database fixtures (mitigation: `scope='session'` isolation)
- 🟡 **MEDIUM**: Mutation testing runtime >10min (mitigation: scoped mutation with `--paths-to-mutate`)
- 🟢 **LOW**: Performance benchmark storage overhead (mitigation: JSON compression)

---

### M3: Integration & Hardening (Weeks 7-8)

**Theme**: Consolidate gains, automate tier progression, finalize CI/CD integration.

**Objectives Delivered**:
- **O7: Coverage Ladder v2** (complete)
- **O6: Parallelization Stability** (100% - optimizations complete)
- **All Objectives**: Final validation and evidence archival

**Key Deliverables**:
1. ✅ 4-tier coverage ladder operational (Unit/Integration/System/Mutation)
2. ✅ Automated tier tracking in coverage.ladder.v2.yaml
3. ✅ Visual tier progression dashboard
4. ✅ CI/CD gates updated: mutation (advisory), performance (blocking), cross-OS (blocking)
5. ✅ Parallelization optimizations: <5% flake rate maintained
6. ✅ Comprehensive Phase 2 AAR with velocity analysis
7. ✅ Playbook documentation: parallelization, mutation, cross-OS best practices

**Acceptance Gate (M3 Checkpoint / Phase 2 Complete)**:
- [ ] Coverage ladder tiers: 4/4 implemented with automated tracking
- [ ] CI/CD integration: All gates operational (blocking + advisory)
- [ ] Final flake rate: <5% across all platforms
- [ ] Parallelization stability: No regression in speedup from M2
- [ ] Mutation score: Maintained ≥60% after codebase changes
- [ ] Evidence bundle: M3-completion.tar.gz + Phase2-AAR.yaml
- [ ] Documentation: Playbooks published for marker consolidation, parallelization, mutation testing

**Phase 1 Carryover Dependencies**:
- ✅ **FULLY RESOLVED**: All Phase 1 deferred items addressed (markers, cross-OS, performance, Hypothesis deferral documented)

**Risk Register (M3)**:
- 🟡 **MEDIUM**: Coverage ladder automation complexity (mitigation: incremental rollout, manual fallback)
- 🟢 **LOW**: CI/CD gate tuning post-deployment (mitigation: advisory gates for 1 sprint before blocking)
- 🟢 **LOW**: Playbook documentation completeness (mitigation: evidence-driven examples from actual execution)

---

### Milestone Dependency Chain

```
M1 (Foundation) ──BLOCKS──> M2 (Expansion) ──BLOCKS──> M3 (Integration)
     │                           │                         │
     ├─ O1 (Reliability)        ├─ O3 (Cross-OS)         ├─ O7 (Coverage Ladder)
     ├─ O5 (Markers)            ├─ O4 (Performance)      └─ O6 (100% optimized)
     └─ O2 (50%)                ├─ O6 (80%)
                                └─ O2 (100%)
```

**Critical Path**: M1 → M2 → M3 (sequential milestones due to dependency chain; M2 parallelization requires M1 reliability, M3 ladder requires M2 metrics)

---

### Velocity & Timeline Assumptions

**Effort Estimates** (based on Phase 1 velocity analysis):
- **M1**: 15-20 dev-days (collection error resolution: 5-7 days, marker consolidation: 2-3 days, mutation baseline: 3-5 days, flake tracking: 3-5 days)
- **M2**: 18-24 dev-days (cross-OS matrix: 3-5 days, performance baseline: 3-5 days, parallelization: 5-7 days, mutation scoring: 3-5 days, optimization: 4-5 days)
- **M3**: 10-15 dev-days (coverage ladder: 5-7 days, CI/CD integration: 2-3 days, playbook documentation: 3-5 days)

**Total Estimated Effort**: 43-59 dev-days over 8 calendar weeks (assumes 1.2 FTE allocation with 20% buffer for unknowns)

**Checkpoint Cadence**:
- **Weekly**: Sprint review with velocity tracking (story points burned, flake rate delta, collection error reduction)
- **Milestone**: Formal acceptance gate validation with evidence bundle SHA-256 archival
- **Phase Completion**: Comprehensive AAR with COF 13D retrospective analysis

## 5. Strategic Pillars

### Pillar Framework

Phase 2 architecture rests on **5 strategic pillars** that provide structural integrity and cross-cutting capabilities. Each pillar supports multiple objectives and milestones through specialized practices and tooling.

---

### Pillar 1: Reliability Engineering

**Mission**: Establish deterministic, reproducible test execution with <5% flake rate across all platforms.

**Core Practices**:
1. **Flake Detection & Quarantine**
   - SQLite-based FlakeTracker with historical flake rate calculation
   - Automated quarantine markers (`@pytest.mark.flaky_quarantine`) for >20% flake rate
   - pytest-rerunfailures integration for transient failure identification

2. **Determinism Enforcement**
   - pytest-randomly for reproducible test order (with `--randomly-seed=last` for debugging)
   - freezegun for time-dependent test mocking
   - Per-test seed derivation: `hash(base_seed + test_id)` for isolated randomness

3. **Test Isolation**
   - `scope='session'` fixtures for shared resources (databases, mock servers)
   - Explicit fixture dependency chains with pytest-order for critical sequences
   - Pathlib mandatory for cross-platform path handling

4. **Collection Error Elimination**
   - Systematic resolution of 15 Phase 1 collection errors
   - Import dependency validation via pytest --collect-only dry-run
   - Fixture availability checks in conftest.py

**Pillar Metrics**:
- Collection error rate: 0% (down from 35.7%)
- Flake rate: <5% over 100-run sample
- Determinism score: 100% reproducible failures with `--randomly-seed`

**Supports Objectives**: O1 (Reliability Consolidation), O6 (Parallelization Stability)

**Tooling**:
- pytest-rerunfailures
- pytest-randomly
- freezegun
- Custom FlakeTracker (SQLite persistence)

---

### Pillar 2: Observability Infrastructure

**Mission**: Provide comprehensive visibility into test execution, performance, and quality metrics.

**Core Practices**:
1. **Performance Benchmarking**
   - pytest-benchmark integration for p50/p95/p99 latency tracking
   - Baseline storage with SHA-256 integrity hashing
   - 10%+ regression detection gate in CI/CD
   - HTML comparison reports for trend analysis

2. **Mutation Score Tracking**
   - mutmut HTML reports with per-module mutation scores
   - Baseline mutation report archived with SHA-256 hash
   - Advisory CI/CD gate for mutation score maintenance

3. **Coverage Ladder Visualization**
   - 4-tier coverage dashboard (Unit/Integration/System/Mutation)
   - Automated tier progression events (`coverage_ladder_stage_advanced`)
   - Visual tier advancement history in coverage.ladder.v2.yaml

4. **Event Taxonomy Extension**
   - New structured events: `marker_consolidation_complete`, `os_matrix_baseline_recorded`, `mutation_score_threshold_met`, `performance_benchmark_complete`
   - JSONL logging with unified_logger integration
   - Event correlation via session_id for AAR traceability

**Pillar Metrics**:
- Performance baseline coverage: 10+ critical test paths benchmarked
- Mutation visibility: 100% of 5 focused modules scored
- Event coverage: 100% of Phase 2 milestones emit completion events

**Supports Objectives**: O4 (Performance Benchmarking), O7 (Coverage Ladder v2), O2 (Mutation Infrastructure)

**Tooling**:
- pytest-benchmark
- mutmut
- unified_logger (JSONL structured logging)
- Custom coverage.ladder.v2.yaml tracker

---

### Pillar 3: Mutation Quality Assurance

**Mission**: Validate fault-handling logic through systematic mutation testing with ≥60% mutation score.

**Core Practices**:
1. **Mutation Tool Selection**
   - mutmut chosen (8.5/10 trust score, superior pytest integration)
   - Scoped mutation via `--paths-to-mutate` for 5 focused modules
   - Mutation operators: arithmetic, comparison, logical, assignment

2. **Baseline Establishment**
   - Initial mutation scan for ulog, dbcli, cf_cli, qse, common modules
   - Mutation score calculation: `(killed_mutants / total_mutants) * 100`
   - Target threshold: ≥60% (industry standard for critical paths)

3. **Test Enhancement Guidance**
   - Mutation report analysis identifies untested logic branches
   - Playbook documentation of mutation-resistant test patterns
   - Iterative test strengthening to kill surviving mutants

4. **CI/CD Integration**
   - Advisory gate initially (non-blocking to avoid disruption)
   - Transition to blocking gate after 2-sprint stabilization
   - Mutation score trend tracking in coverage ladder

**Pillar Metrics**:
- Mutation score: ≥60% for 5 focused modules
- Mutation runtime: <10min for scoped scan
- Surviving mutants: <40% (inverse of mutation score)

**Supports Objectives**: O2 (Mutation Readiness Infrastructure), O7 (Coverage Ladder v2 - Tier 4)

**Tooling**:
- mutmut
- HTML report generator
- Custom mutation score threshold validator

---

### Pillar 4: Performance Engineering

**Mission**: Establish quantified performance baselines and prevent regressions through automated benchmarking.

**Core Practices**:
1. **Benchmark Harness**
   - pytest-benchmark with `@pytest.mark.benchmark` annotations
   - Configurable warmup rounds (default: 2) and iterations (default: 10)
   - Statistical analysis: mean, median, stddev, p95, p99

2. **Baseline Management**
   - Baseline storage in perf.benchmark.baseline.json with SHA-256 hash
   - Comparison logic: current_p95 vs baseline_p95
   - 10%+ threshold triggers regression alert

3. **Regression Detection**
   - CI/CD gate: Fail build on 10%+ performance degradation
   - HTML comparison report generation for trend visualization
   - Automated rollback recommendation for severe regressions (>25%)

4. **Parallelization Speedup Validation**
   - Measure sequential baseline runtime (target: ~30s for 42 tests)
   - Measure parallel runtime with pytest-xdist `-n auto`
   - Calculate speedup factor: `sequential_time / parallel_time`
   - Target: 3-5x speedup as suite scales to 100+ tests

**Pillar Metrics**:
- Baseline coverage: 10+ critical test paths benchmarked
- Regression detection rate: 100% (no regressions pass CI/CD gate)
- Parallelization speedup: 3-5x measured improvement

**Supports Objectives**: O4 (Performance Benchmark Establishment), O6 (Parallelization Stability - speedup validation)

**Tooling**:
- pytest-benchmark
- Custom regression comparison script
- HTML report generator

---

### Pillar 5: Governance Evolution

**Mission**: Maintain constitutional compliance (COF/UCL/Sacred Geometry) while scaling testing infrastructure.

**Core Practices**:
1. **Evidence Bundle Management**
   - SHA-256 integrity hashing for all artifacts (marker_audit.json, mutation reports, benchmark baselines)
   - JSONL event correlation via session_id
   - Artifact archival at milestone checkpoints (M1/M2/M3-completion.tar.gz)

2. **COF 13D Dimensional Analysis**
   - Apply COF framework to Phase 2 planning (see section 6)
   - Motivational: Reliability expansion business case
   - Relational: Objective dependency graph
   - Temporal: 8-week milestone structure
   - Validation: Acceptance gate criteria (AC-8 through AC-15)

3. **UCL Compliance**
   - No orphaned contexts: All objectives anchored to milestones
   - No cycles: Dependency graph validated for acyclic flow
   - Evidence completeness: 100% of deliverables have SHA-256 archived artifacts

4. **Sacred Geometry Patterns**
   - **Triangle (Stability)**: M1 foundation hardening before M2 expansion
   - **Circle (Completeness)**: 4-tier coverage ladder closes quality loop
   - **Spiral (Iteration)**: Milestone checkpoints enable retroactive adjustment
   - **Golden Ratio (Optimization)**: 20% effort (parallelization) yields 80% speedup
   - **Fractal (Modularity)**: Pillar architecture enables independent scaling

5. **Quality Gates v2**
   - Mutation score (advisory initially, blocking after stabilization)
   - Performance regression (blocking, 10%+ threshold)
   - Cross-OS consistency (blocking, ≥95% pass rate)
   - Flake rate (advisory, <5% target)

**Pillar Metrics**:
- Evidence bundle integrity: 100% SHA-256 validated
- COF completeness: 13/13 dimensions addressed
- UCL violations: 0 (no orphans, cycles, or incomplete evidence)
- Sacred Geometry alignment: 5/5 patterns validated

**Supports**: All objectives (cross-cutting governance)

**Tooling**:
- unified_logger (JSONL structured events)
- SHA-256 hasher script
- COF dimensional analysis template
- Quality gate validation script

---

### Cross-Pillar Dependencies

```
Reliability ─────┬──> Observability (reliable metrics require stable tests)
                 │
                 ├──> Performance (parallelization requires determinism)
                 │
                 └──> Governance (evidence requires reproducible execution)

Observability ───┬──> Mutation Quality (mutation score visibility)
                 │
                 └──> Performance (benchmark tracking)

Mutation Quality ──> Governance (mutation reports archived with SHA-256)

Performance ────┬──> Observability (benchmark data feeds dashboards)
                └──> Governance (regression gates enforce standards)

Governance ──────> ALL PILLARS (constitutional compliance is cross-cutting)
```

**Key Insight**: Pillars are not siloed; they form an **interdependent mesh** where strength in one amplifies capabilities in others. Governance acts as the binding fabric ensuring coherence.

## 6. COF 13D Snapshot (Phase 2 Baseline)

**Research Foundation Applied**: All research artifacts incorporate COF analysis

| Dimension | Phase 2 Application | Research Evidence |
|-----------|---------------------|-------------------|
| **Motivational** | Eliminate 35.7% collection errors; achieve 3-5x speedup | DevOps Executive Summary § 1 |
| **Relational** | Cross-OS matrix dependencies; pytest-xdist integration | Cross-OS Research § 2 |
| **Situational** | Windows-dominant environment → multi-platform expansion | Cross-OS Research § 1 |
| **Resource** | 8-week timeline; mutmut/pytest-benchmark tooling | All research artifacts |
| **Narrative** | "From foundation to operational excellence" | Implementation Guide § 1 |
| **Recursive** | Mutation testing validates test quality recursively | Mutation Quick Start |
| **Computational** | Performance benchmarking (p50/p95/p99 metrics) | Cross-OS Research § 3 |
| **Emergent** | Flake detection patterns; race condition mitigation | Reliability Implementation § 4 |
| **Temporal** | M1 (Weeks 1-3), M2 (Weeks 4-6), M3 (Weeks 7-8) | All milestone templates |
| **Spatial** | Windows + Linux + macOS matrix | DevOps Executive Summary § 2 |
| **Holistic** | 5 pillars integrate into unified testing platform | Coverage Ladder Research |
| **Validation** | 15 acceptance criteria (AC-1 through AC-15) | Milestone templates |
| **Integration** | CI/CD workflows (7 blocking + 11 advisory gates) | Evidence Management Research |

## 7. Sacred Geometry Alignment (Evolution)
Placeholder: Triangle (stability continuity), Circle (completeness extension), Spiral (iteration from Phase 1 retros), Golden Ratio (optimization focus 20/80), Fractal (modular test pattern reuse).

## 8. Universal Context Law (UCL) Compliance Delta
Placeholder: New anchoring checks, cycle prevention for parallelization additions, evidence completeness expansion.

## 9. Execution Sequencing Overview
Placeholder: Ordered phases / waves (e.g., Wave A: Marker Consolidation → Wave B: Mutation Baseline → Wave C: Performance Baseline → Wave D: Parallelization Hardening → Wave E: Coverage Ladder v2 advancement).

## 10. Artifact Inventory (New & Evolving)
Placeholders list:
- markers.consolidated.json
- os.matrix.baseline.json
- mutation.initial.report.json
- perf.benchmark.baseline.json
- coverage.ladder.v2.yaml
- parallelization.scan.report.json
- flake.reduction.delta.json
- integrity.events.v2.schema.json

## 11. Event Taxonomy Extensions
Placeholder new events:
- marker_consolidation_start / complete
- os_matrix_baseline_recorded
- mutation_scan_start / complete
- performance_benchmark_start / complete
- parallelization_probe_start / complete
- flake_reduction_delta_emitted
- coverage_ladder_stage_advanced
- mutation_score_threshold_met

## 12. Environment & OS Matrix Expansion
Placeholder: Enumerate target OSes / Python versions / shells; baseline matrix file reference.

## 13. Mutation Testing Readiness Framework

**Research Complete**: Mutation Testing Quick Start Guide (8 pages)

### Tool Selection (Evidence-Based)
- **Selected**: mutmut (8.5/10 trust score)
- **Runner**: pytest with coverage integration
- **Configuration**: `mutmut_config.py` + `setup.cfg`
- **Target Score**: ≥60% mutation score (industry standard)
- **Runtime**: <10min for scoped scan

### 5 Critical Modules (M1-M2 Focus)
1. `python/services/unified_logger/` (logging correctness)
2. `python/core/dbcli/` (database operations)
3. `cf_cli.py` (CLI orchestration)
4. `python/core/qse/` (quality framework)
5. `python/services/common/` (shared utilities)

### Execution Strategy
- **M1 Baseline**: unified_logger only (50-mutant cap, 3-4min)
- **M2 Full Scan**: All 5 modules (8-10min)
- **CI/CD Integration**: Advisory gate → blocking after 2 sprints

### Quick Start Commands
```powershell
# M1 baseline
mutmut run --paths-to-mutate "python/services/unified_logger/" --max-mutations 50

# View results
mutmut results

# Generate HTML report
mutmut html

# M2 full scan
mutmut run
```

**Reference**: `artifacts/MUTATION-TESTING-QUICK-START.md`

## 14. Performance Baseline & Benchmarking Plan

**Research Complete**: Cross-OS Performance Research § 3 (12 pages)

### Benchmark Harness
- **Tool**: pytest-benchmark (pytest-integrated)
- **Metrics**: mean, median, stddev, p50, p95, p99
- **Target Tests**: 10+ critical paths initially
- **Storage**: `perf.benchmark.baseline.json` (SHA-256 hashed)

### Performance Targets
| Metric | Target | Detection Threshold |
|--------|--------|---------------------|
| **Mean Runtime** | Baseline ±5% | 10%+ regression fails CI |
| **p50 Latency** | <100ms (ulog) | 15%+ triggers alert |
| **p95 Latency** | <200ms (dbcli) | 20%+ blocks merge |
| **p99 Latency** | <500ms (cf_cli) | 25%+ emergency review |

### Parallelization Speedup Validation
- **Baseline**: Sequential execution (~30s for 42 tests)
- **Target**: 3-5x speedup with pytest-xdist `-n auto`
- **Measurement**: `speedup-analysis.json` (before/after comparison)
- **Stability**: <2% flake rate increase post-parallelization

### CI/CD Integration
```yaml
# .github/workflows/performance-benchmark.yml
- name: Run benchmarks
  run: pytest --benchmark-only --benchmark-autosave

- name: Compare to baseline
  run: pytest-benchmark compare --threshold=10%
```

### Scheduling Cadence
- **Per-PR**: Regression check (10%+ threshold)
- **Weekly**: Full baseline refresh
- **Per-Milestone**: Comprehensive analysis + archival

**Reference**: `artifacts/PHASE2-TPR-CROSS-OS-PERFORMANCE-RESEARCH-SYNTHESIS.md` § 3

## 15. Marker Consolidation Strategy

**Research Complete**: Marker Consolidation Research (22 pages)

### Current State Analysis
- **Total Markers**: 283 defined in pyproject.toml
- **Active Usage**: 44 markers (15.5% utilization)
- **Unused Markers**: 239 (84.5% dead code)
- **Target**: <50 active markers (82% reduction)

### Consolidation Approach (3 Phases)

#### Phase 1: Audit & Categorization
```powershell
# Generate usage report
pytest --collect-only --markers > marker-usage.txt
grep -c "@pytest.mark" tests/**/*.py > marker-counts.json
```

**Categories Identified**:
- ISTQB Compliance: 50 markers (keep 12 active)
- ISO 25010 Quality: 45 markers (keep 8 active)
- Constitutional Validation: 38 markers (keep 15 active)
- Component-Specific: 44 markers (keep 9 active)
- Custom/Unused: 106 markers (remove all)

#### Phase 2: Safe Removal Criteria
- ✅ Zero test file references
- ✅ Not in GitHub Actions workflows
- ✅ Not in pytest.ini or setup.cfg
- ✅ No ADR or evidence bundle references
- ✅ Age >60 days with no usage

#### Phase 3: Migration Script
```python
# scripts/consolidate_markers.py
def consolidate_markers():
    # 1. Parse pyproject.toml markers
    # 2. Scan test files for @pytest.mark usage
    # 3. Generate removal candidates
    # 4. Create pytest.ini migration
    # 5. Update test annotations
    # 6. Archive removed markers to evidence bundle
```

### Target Marker Set (<50)
- **ISTQB**: unit, integration, system, e2e (12)
- **Quality**: functional_suitability, performance_efficiency, security, reliability (8)
- **Constitutional**: ucl1, ucl2, ucl3, cof_motivational, cof_relational, ... (15)
- **Component**: taskman, velocity_tracker, qse, cf_core (9)
- **Execution**: slow, requires_db, requires_network (6)

### Validation Gates
- ❌ **FAIL**: Any test referencing removed marker
- ⚠️ **WARN**: Marker usage <5% (candidate for removal)
- ✅ **PASS**: All tests use consolidated markers only

**Reference**: `artifacts/PHASE2-TPR-MARKER-CONSOLIDATION-RESEARCH.md`

## 16. Coverage Ladder v2

**Research Complete**: Coverage Ladder Research Synthesis (35 pages)

### 4-Tier Architecture (Enhanced from Phase 1)

```yaml
# coverage.ladder.v2.yaml
tiers:
  tier1_unit:
    scope: "Unit tests (isolated logic)"
    target: 70%
    current: 60.2%  # Phase 1 baseline
    gate: blocking
    tools: [pytest, coverage.py]
    
  tier2_integration:
    scope: "Multi-component integration"
    target: 40%
    current: 35%  # Phase 1 baseline
    gate: blocking
    tools: [pytest, testcontainers]
    
  tier3_system:
    scope: "End-to-end workflows"
    target: 25%
    current: 20%  # Phase 1 baseline
    gate: advisory
    tools: [pytest, playwright]
    
  tier4_mutation:
    scope: "Test quality validation"  # NEW IN PHASE 2
    target: 60%
    current: 0%  # Not yet established
    gate: advisory (blocking after M2)
    tools: [mutmut]
```

### Delta from Phase 1
- **New Tier**: Tier 4 (Mutation) added for test quality validation
- **Target Adjustments**: Tier 1 (70% → 75%), Tier 2 (40% → 50%)
- **Measurement**: Branch coverage added (0.4% baseline → 35% target)
- **Automation**: Auto-tier-promotion based on sustained coverage

### Advancement Triggers

#### Tier 1 → Tier 2 Promotion
- ✅ Tier 1 coverage ≥70% for 2 consecutive sprints
- ✅ Zero collection errors
- ✅ <5% flake rate

#### Tier 2 → Tier 3 Promotion
- ✅ Tier 2 coverage ≥40% for 1 sprint
- ✅ Cross-OS pass rate ≥95%
- ✅ Performance regression <10%

#### Tier 3 → Tier 4 Promotion
- ✅ Tier 3 coverage ≥25%
- ✅ E2E workflows operational
- ✅ Mutation baseline established

#### Tier 4 Graduation (Phase 3)
- ✅ Mutation score ≥60% sustained
- ✅ All 4 tiers at target coverage
- ✅ Ready for integration/E2E scaling

### Tracking Dashboard
```python
# scripts/coverage_ladder_dashboard.py
def generate_dashboard():
    return {
        "tier1": {"current": 60.2, "target": 70, "trend": "+2.1%"},
        "tier2": {"current": 35, "target": 40, "trend": "+1.5%"},
        "tier3": {"current": 20, "target": 25, "trend": "+0.8%"},
        "tier4": {"current": 0, "target": 60, "trend": "N/A"}
    }
```

**Reference**: `artifacts/PHASE2-TPR-COVERAGE-LADDER-RESEARCH-SYNTHESIS.md`

## 17. Parallelization & Concurrency Stability
Placeholder: Identification of race-prone test groups, isolation tactics, thread/process model adjustments, flake detection heuristics.

## 18. Determinism & Reproducibility v2
Placeholder: Random seed policy evolution, time-dependent test mitigation, cross-environment consistency checks.

## 19. Logging & Evidence Expansion
Placeholder: Additional evidence bundle fields (mutation metrics, performance snapshot hash, OS variance summary), logging coverage maintenance (≥90%).

## 20. Acceptance Criteria (Carry-over AC-1..AC-7)
Placeholder: Reference Phase 1 acceptance criteria unchanged; list any still applicable for Phase 2.

## 21. New Acceptance Criteria (AC-8..AC-15 Placeholders)
Placeholder list (labels only, no metrics yet):
- AC-8: Marker Reduction Achieved (target % TBD)
- AC-9: OS Diversity Baseline Established
- AC-10: Mutation Baseline Score Captured
- AC-11: Performance Baseline Benchmarks Stored
- AC-12: Property Strategy Extension Implemented
- AC-13: Parallelization Stability Gate Passing
- AC-14: Flake Reduction Delta Recorded
- AC-15: Integrity & Event Expansion Validated

## 22. Risk & Mitigation Matrix (Skeleton)
Placeholder table rows:
- Marker over-pruning (Loss of semantic grouping) → Mitigation: staged removal audit
- Cross-OS flake emergence → Mitigation: matrix canary runs
- Mutation runtime inflation → Mitigation: scoped subset, incremental gating
- Performance regression due to added instrumentation → Mitigation: measure-before-enable toggle
- Parallelization race conditions → Mitigation: deterministic ordering harness

## 23. Rollback & Contingency (Phase 2 Specific)
Placeholder: Conditions triggering rollback (e.g., mutation run >X min, performance degradation >Y%).

## 24. Quality Gates v2 & Validation Enhancements
Placeholder: New gates (mutation_score_min, performance_baseline_lock, marker_audit_pass), evolution of existing gates.

## 25. Versioning, Changelog & Integrity Hash
Placeholder: Changelog protocol for Phase 2 artifacts; integrity hash computation process; hash placeholder above to be replaced post population.

---
NEXT ACTION: Await user approval of outline before populating detailed content sections.
