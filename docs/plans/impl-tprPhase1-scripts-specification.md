## Phase 1 Foundation Script Suite Specification

Status: APPROVED
Seal: PENDING_HASH
Approval Rationale: Branch feat/tpr-phase1-foundation-scripts established; governance integrity verified; no content drift from prior validated draft. Transitioning to APPROVED to enable deterministic hash sealing. No functional script implementation permitted until Seal replaced with computed SHA256.

### 1. Purpose
This specification defines the initial governance-controlled script suite for Phase 1 (foundation) prior to broader implementation. Scripts provide environment validation, metrics collection, fail-fast orchestration, property test aggregation, and foundation checkpoint emission. All scripts must adhere to integrity-first workflow: no side-effectful operations outside designated artifact directory and append-only logging.

### 2. Scripts Overview
1. validate_env.py – Verifies Python version (>=3.11), virtual environment activation, required tools (git, pytest, ruff, mypy), writable directories, and absence of conflicting sentinel files. Emits env.signature.json and structured log events.
2. collect_metrics.py – Gathers CPU cores, memory (total/available), Python implementation/version, installed package versions for critical tooling, and timing benchmarks for a noop import set. Outputs baseline.metrics.json.
3. failfast_wrapper.py – Orchestrates validate_env and collect_metrics; halts (non-zero exit) if any mandatory precondition fails, else emits failfast.summary.json summarizing pass/fail sections and timing.
4. aggregate_property_tests.py – Runs property-based tests (hypothesis) within designated tests/property/ path; aggregates outcomes, flakiness indicators, and example counterexamples into property.results.json.
5. generate_foundation_checkpoint.py – Consolidates artifacts {env.signature.json, baseline.metrics.json, failfast.summary.json, property.results.json} plus a manifest into foundation.checkpoint.yaml for downstream phases.

### 3. Acceptance Criteria Mapping
AC-1 Deterministic canonical hashing (spec seal) enforced prior to any implementation commits changing code content.
AC-2 Structured JSONL logging with event taxonomy: session_start, task_start, decision, artifact_emit, warning, error, task_end, session_summary.
AC-3 All scripts exit non-zero on internal validation failure and never partially write primary artifact (atomic temp -> move strategy).
AC-4 Redaction of sensitive env variables (match keys: password|token|secret|api_key) in logs.
AC-5 Hash sealing prevents silent edits; post-seal modifications require CHANGELOG entry and version bump reference.
AC-6 Metrics script reproducibility: repeated runs produce identical schema; numeric variances logged with delta fields.
AC-7 Property aggregation surfaces hypothesis health: counts of examples, falsifying examples, and average execution time per property.

### 4. Logging & Integrity
Unified logger (unified_logger.py) will provide append-only JSONL with size rotation (~10MB) and UTC timestamps. Each artifact write logged via artifact_emit including SHA256 of file contents. Temporary files named with .tmp suffix; moved atomically after successful validation.

### 5. Hash Sealing Procedure
1. Confirm APPROVED status and stable content on feature branch.
2. Compute canonical SHA256 over UTF-8 normalized file (LF line endings, trim trailing whitespace, exclude Seal line placeholder token PENDING_HASH).
3. Replace Seal value with computed hash (format: sha256:<hex>). Commit with message: "spec: seal Phase 1 foundation scripts (sha256:...)".
4. Create CHANGELOG.md entry documenting seal.

### 6. Error Handling Model
Scripts define exit codes: 0 success, 10 validation failure, 20 dependency missing, 30 unexpected exception. Fail-fast wrapper interprets child exit codes and produces consolidated summary.

### 7. Artifact Directory & Paths
Artifacts written to .qse/v2/projects/P-TPR/phase1/ ensuring isolation:
 - .qse/v2/projects/P-TPR/phase1/env.signature.json
 - .qse/v2/projects/P-TPR/phase1/baseline.metrics.json
 - .qse/v2/projects/P-TPR/phase1/failfast.summary.json
 - .qse/v2/projects/P-TPR/phase1/property.results.json
 - .qse/v2/projects/P-TPR/phase1/foundation.checkpoint.yaml
 - logs/phase1.events.jsonl (shared logger target)

### 8. Future Extensions (Non-scope)
Not in Phase 1: performance benchmarking harness, dependency graph analyzer, security audit integration. Will reference sealed spec for subsequent phase scoping.

### 9. COF 13D Snapshot (Abbreviated)
Motivational: Provide reliable base validation to reduce downstream defect propagation.
Relational: Dependencies on Python runtime, git, pytest, ruff, mypy.
Situational: Operating in isolated feature branch for governance sealing.
Resource: Minimal time footprint (<2 minutes total execution).
Narrative: Developer runs failfast_wrapper.py before any deeper implementation to ensure prerequisites.
Recursive: Outputs feed checkpoint which future phases reference; iteration enables refinement without breaking seal history.
Computational: Simple I/O, hashing, subprocess calls, JSON writes; complexity intentionally low.
Emergent: Early detection of environment drift trends via metrics deltas.
Temporal: Executed at start of development sessions; seal placed once then only amended via governed process.
Spatial: All artifacts confined to .qse/phase1/; no writes outside controlled tree.
Holistic: Forms foundation ensuring integrity-first across subsequent modules.
Validation: Acceptance criteria mapped; tests will assert artifact schema & exit codes.
Integration: Checkpoint consumed by later orchestration scripts.

### 10. Change Control
Post-seal alterations require: (1) new feature branch, (2) CHANGELOG entry specifying reason, (3) re-computation of hash, (4) review.

### 11. Security & Redaction
Environment collection excludes full PATH, redacts variables with sensitive key patterns, logs only allowed metadata.

### 12. Open Issues
Define hypothesis test directory structure; finalize rotation strategy thresholds; confirm Windows-specific resource acquisition nuances.
# TPR Phase 1 Implementation Scripts - Technical Specification

**Document Version**: 1.0.0
**Created**: 2025-11-23
**Status**: DRAFT
**Authority**: plan-tprPhase1CompletionFoundationSolidification.prompt.md
**Purpose**: Detailed technical specifications for Phase 1 implementation scripts

---

## Overview

This document specifies the four core scripts required to complete TPR Phase 1:

1. **Environment Validator** (`validate_env.py`)
2. **Metrics Collector** (`collect_metrics.py`)
3. **Fail-Fast Wiring** (`failfast_wrapper.py`)
4. **Property Tests Aggregator** (`aggregate_property_tests.py`)

Each script specification includes:
- Input/Output contracts
- Dependencies and integration points
- Event taxonomy emissions
- Error handling and rollback
- Validation criteria mapping to Acceptance Criteria
- Sacred Geometry alignment

---

## Script 1: Environment Validator (`validate_env.py`)

### Purpose
Pre-test validation ensuring environment consistency before test execution. Halts on mismatch <1s with structured logging.

### Inputs
- **Environment Variables** (required):
  - `PYTHON_VERSION` (expected: 3.11+)
  - `TPR_LOCK_HASH` (expected SHA256 from requirements.lock)
  - `TPR_ENV_VALIDATE` (optional override: "skip")

- **Files** (required):
  - `requirements.lock` (dependency lock file)
  - `.env` or environment state

### Outputs
- **Success Path**:
  - `env.signature.json` (validation signature with timestamp, Python version, lock hash, status)
  - JSONL event: `env_validation_complete` (status: "pass", duration_ms: <1000)
  - Exit code: 0

- **Failure Path**:
  - JSONL event: `env_validation_failed` (reason: "python_version_mismatch" | "lock_hash_mismatch" | "missing_env_var")
  - Error message to stderr
  - Exit code: 1 (halts test execution)

### Dependencies
- **Python**: 3.11+
- **Modules**: `sys`, `hashlib`, `json`, `os`, `pathlib`
- **Internal**: `python.services.unified_logger` (for JSONL emission)

### Logic Flow
```python
1. Load environment variables
2. Check Python version (sys.version_info >= (3, 11))
3. Compute SHA256 of requirements.lock
4. Compare computed hash with TPR_LOCK_HASH
5. IF override TPR_ENV_VALIDATE=skip → log warning, exit 0
6. IF any validation fails → emit env_validation_failed, exit 1
7. IF all pass → emit env_validation_complete, write env.signature.json, exit 0
```

### Event Taxonomy
```jsonl
{"timestamp": "2025-11-23T...", "event": "env_validation_start", "context": "pre_test", "python_version": "3.11.5", "lock_hash_expected": "abc..."}
{"timestamp": "2025-11-23T...", "event": "env_validation_complete", "context": "pre_test", "status": "pass", "duration_ms": 847}
```

### Acceptance Criteria Mapping
- **AC-5**: Environment validator halts on mismatch <1s
- **Quality Gate 1**: Environment Validation (Pre-test, Hard abort)

### Sacred Geometry Alignment
- **Triangle (Stability)**: Three-point validation (Python version, lock hash, env vars)
- **Circle (Completeness)**: Full environment state captured in signature
- **Spiral (Iteration)**: Validation runs before every test suite

### Integration Points
- **pytest conftest.py**: Call `validate_env.py` in `pytest_configure` hook
- **CI/CD**: Run as first step in pipeline before test execution
- **CF_CLI**: Integrate with `cf_cli test` command via pre-test hook

---

## Script 2: Metrics Collector (`collect_metrics.py`)

### Purpose
Aggregate baseline metrics from pytest coverage, complexity, and custom metrics into consolidated `baseline.metrics.json`.

### Inputs
- **Files** (required):
  - `coverage.xml` (pytest-cov output)
  - `complexity.json` (radon/mccabe output)
  - `test_results.json` (pytest JSON report)

- **Environment Variables** (optional):
  - `TPR_METRICS_MODE` (default: "full", options: "full" | "minimal")

### Outputs
- **Always**:
  - `baseline.metrics.json` (consolidated metrics with SHA256 hash)
  - JSONL event: `metrics_capture_complete` (fields_captured: 15, hash: "sha256:...")

- **Structure of baseline.metrics.json**:
```json
{
  "timestamp": "2025-11-23T...",
  "schema_version": "1.0",
  "hash": "sha256:...",
  "coverage": {
    "line_pct": 85.3,
    "branch_pct": 72.1,
    "functions_covered": 234,
    "functions_total": 312
  },
  "complexity": {
    "avg_cyclomatic": 3.8,
    "max_cyclomatic": 12,
    "files_above_threshold": 5
  },
  "test_stats": {
    "total_tests": 1247,
    "passed": 1235,
    "failed": 0,
    "skipped": 12,
    "duration_seconds": 45.2
  },
  "metadata": {
    "python_version": "3.11.5",
    "pytest_version": "7.4.3",
    "collection_mode": "full"
  }
}
```

### Dependencies
- **Python**: 3.11+
- **Modules**: `xml.etree.ElementTree` (coverage.xml parsing), `json`, `hashlib`, `pathlib`
- **Internal**: `python.services.unified_logger`

### Logic Flow
```python
1. Parse coverage.xml → extract line/branch coverage percentages
2. Parse complexity.json → compute avg/max cyclomatic complexity
3. Parse test_results.json → extract pass/fail/skip counts, duration
4. Consolidate into baseline.metrics.json structure
5. Compute SHA256 hash of JSON content (canonical sorted keys)
6. Write baseline.metrics.json with hash field
7. Emit metrics_capture_complete event
```

### Event Taxonomy
```jsonl
{"timestamp": "2025-11-23T...", "event": "metrics_capture_start", "context": "post_test", "mode": "full"}
{"timestamp": "2025-11-23T...", "event": "metrics_capture_complete", "context": "post_test", "fields_captured": 15, "hash": "sha256:abc..."}
```

### Acceptance Criteria Mapping
- **AC-1**: All metric fields present (null only where data genuinely absent); hash stored; event log contains `metrics_capture_complete`
- **Quality Gate 2**: Coverage Baseline Regression (Post-test, Hard threshold)

### Sacred Geometry Alignment
- **Circle (Completeness)**: All metrics consolidated into single authoritative artifact
- **Golden Ratio (Balance)**: Metrics capture optimizes for essential data (15 fields vs exhaustive 100+)
- **Fractal (Modularity)**: Reusable across projects via schema versioning

### Integration Points
- **pytest**: Run as `pytest --cov --json-report` → then call `collect_metrics.py`
- **CI/CD**: Post-test artifact generation step
- **CF_CLI**: `cf_cli test --with-metrics` flag triggers collection

---

## Script 3: Fail-Fast Wiring (`failfast_wrapper.py`)

### Purpose
Pytest wrapper enabling soft/hard fail-fast modes with early exit detection and benchmark comparison.

### Inputs
- **Command-line Args**:
  - `--mode` (required: "soft" | "hard" | "baseline")
  - `--benchmark-file` (optional: path to previous run's failfast.summary.json)
  - Remaining args passed to pytest

- **Environment Variables** (optional):
  - `TPR_FAILFAST_THRESHOLD` (default: 3 failures before exit)

### Outputs
- **Always**:
  - `failfast.summary.json` (mode, detection_time_ms, failures_before_exit, improvement_pct)
  - JSONL events: `failfast_mode_applied`, `early_exit_detected` (when triggered)

- **Structure of failfast.summary.json**:
```json
{
  "timestamp": "2025-11-23T...",
  "mode": "hard",
  "baseline_comparison": {
    "baseline_detection_ms": 4500,
    "current_detection_ms": 1200,
    "improvement_pct": 73.3
  },
  "execution": {
    "total_tests_run": 23,
    "failures_before_exit": 3,
    "early_exit_triggered": true,
    "time_saved_ms": 3300
  }
}
```

### Dependencies
- **Python**: 3.11+
- **Modules**: `pytest` (programmatic API), `json`, `time`, `subprocess`
- **Internal**: `python.services.unified_logger`

### Logic Flow
```python
1. Parse command-line args (--mode, --benchmark-file)
2. IF mode == "baseline":
   - Run pytest with NO fail-fast flags
   - Seed 1 intentional failure at test #50
   - Measure total time to complete
   - Write failfast.summary.json with baseline timing
3. IF mode == "soft" or "hard":
   - Load baseline from --benchmark-file
   - Run pytest with --maxfail=3 (soft) or --exitfirst (hard)
   - Measure time to first failure detection
   - Calculate improvement_pct vs baseline
   - Write failfast.summary.json with comparison
4. Emit failfast_mode_applied event
5. IF early exit triggered → emit early_exit_detected event
```

### Event Taxonomy
```jsonl
{"timestamp": "2025-11-23T...", "event": "failfast_mode_applied", "context": "test_execution", "mode": "hard", "threshold": 3}
{"timestamp": "2025-11-23T...", "event": "early_exit_detected", "context": "test_execution", "failures_count": 3, "time_saved_ms": 3300}
```

### Acceptance Criteria Mapping
- **AC-2**: In seeded failure scenario, soft reduces detection time ≥40%; hard reduces ≥60%; summary contains mandatory fields; event log has `failfast_mode_applied` and `early_exit_detected`
- **Quality Gate 3**: Fail-Fast Improvement (Benchmark, Advisory metrics)

### Sacred Geometry Alignment
- **Spiral (Iteration)**: Benchmark establishes baseline, subsequent runs measure improvement
- **Triangle (Stability)**: Three modes (baseline, soft, hard) provide stable comparison framework
- **Golden Ratio (Balance)**: Threshold (3 failures) balances early detection with false positive risk

### Integration Points
- **pytest**: Invoked via `failfast_wrapper.py --mode hard -- -v tests/`
- **CI/CD**: Optional fast-fail stage for rapid feedback
- **CF_CLI**: `cf_cli test --fail-fast hard` flag

---

## Script 4: Property Tests Aggregator (`aggregate_property_tests.py`)

### Purpose
Run Hypothesis property tests 30 consecutive times, aggregate results, validate determinism, and report performance.

### Inputs
- **Command-line Args**:
  - `--test-pattern` (default: "test_property_*.py")
  - `--runs` (default: 30)
  - `--timeout-per-test` (default: 1.0 seconds)

- **Files** (discovered):
  - All files matching `test_pattern` containing `@given` decorated tests

### Outputs
- **Always**:
  - `property.results.json` (per-test results with 30-run summary)
  - JSONL events: `property_test_start`, `property_test_complete` (per test)

- **Structure of property.results.json**:
```json
{
  "timestamp": "2025-11-23T...",
  "total_property_tests": 3,
  "runs_per_test": 30,
  "results": [
    {
      "test_name": "test_property_idempotent_metrics",
      "runs_passed": 30,
      "runs_failed": 0,
      "avg_runtime_ms": 234,
      "max_runtime_ms": 450,
      "deterministic": true,
      "falsifying_examples": [],
      "performance": {
        "within_timeout": true,
        "timeout_ms": 1000
      }
    }
  ],
  "summary": {
    "all_tests_passed": true,
    "deterministic_rate": 100.0,
    "avg_performance_ms": 298,
    "flake_events_logged": 0
  }
}
```

### Dependencies
- **Python**: 3.11+
- **Modules**: `pytest`, `hypothesis`, `json`, `time`, `pathlib`
- **Internal**: `python.services.unified_logger`

### Logic Flow
```python
1. Discover property tests matching --test-pattern
2. FOR each property test:
   a. FOR i in range(30):
      - Run test with Hypothesis
      - Measure runtime
      - Capture pass/fail, falsifying examples
      - IF runtime > timeout_ms → log performance warning
   b. Aggregate 30-run results (pass rate, avg runtime, determinism)
   c. Emit property_test_complete event
3. Compute summary statistics (all tests, deterministic rate, flakes)
4. Write property.results.json
5. IF any test non-deterministic OR avg runtime >1s → exit 1
6. ELSE → exit 0
```

### Event Taxonomy
```jsonl
{"timestamp": "2025-11-23T...", "event": "property_test_start", "context": "property_validation", "test_name": "test_property_idempotent_metrics", "runs_planned": 30}
{"timestamp": "2025-11-23T...", "event": "property_test_complete", "context": "property_validation", "test_name": "test_property_idempotent_metrics", "runs_passed": 30, "deterministic": true, "avg_runtime_ms": 234}
```

### Acceptance Criteria Mapping
- **AC-3**: All 3 property tests pass 30 consecutive deterministic runs; runtime <1s each; no flake events logged; property results file includes performance metrics & zero falsifying examples
- **Quality Gate 4**: Property Stability (Reliability, Advisory trend)

### Sacred Geometry Alignment
- **Spiral (Iteration)**: 30 consecutive runs validate stability across iterations
- **Circle (Completeness)**: All property tests must pass full 30-run cycle
- **Triangle (Stability)**: Three property tests form stable foundation for test suite reliability

### Integration Points
- **pytest**: Run after main test suite as property validation stage
- **CI/CD**: Separate property test job with extended timeout
- **CF_CLI**: `cf_cli test --property-validation` flag

---

## Cross-Script Integration

### Execution Sequence (Complete Phase 1 Flow)
```
1. validate_env.py
   ↓ (exit 0) → env.signature.json
2. pytest --cov --json-report
   ↓ → coverage.xml, test_results.json
3. collect_metrics.py
   ↓ → baseline.metrics.json
4. failfast_wrapper.py --mode baseline
   ↓ → failfast.summary.json (baseline)
5. failfast_wrapper.py --mode hard --benchmark-file failfast.summary.json
   ↓ → failfast.summary.json (with improvement)
6. aggregate_property_tests.py
   ↓ → property.results.json
7. [Future] generate_foundation_checkpoint.py
   ↓ → foundation.checkpoint.md + foundation.checkpoint.json
```

### Shared Dependencies
All scripts depend on:
- `python.services.unified_logger` → JSONL event emission
- `pathlib` → Cross-platform path handling
- `json` (stdlib) → Artifact serialization
- `hashlib` (stdlib) → SHA256 integrity

### Error Handling Strategy
All scripts follow unified error pattern:
```python
try:
    # Script logic
except Exception as e:
    logger.error("script_error", script=__file__, error=str(e), traceback=traceback.format_exc())
    sys.exit(1)
```

### Event Log Consolidation
All scripts write to shared `events.log.jsonl` via unified_logger:
- Rolling log file (rotate at 10MB)
- Structured JSONL format
- Mandatory fields: `timestamp`, `event`, `context`

---

## COF 13-Dimensional Analysis (Scripts Package)

| Dimension | Application | Validation |
|-----------|-------------|------------|
| **Motivational** | Scripts automate Phase 1 acceptance criteria validation | AC-1 through AC-7 directly implemented |
| **Relational** | Scripts depend on pytest, hypothesis, unified_logger | Dependency graph documented in each spec |
| **Situational** | Scripts operate in pre-test, test, post-test phases | Sequencing diagram shows execution flow |
| **Resource** | Scripts require Python 3.11+, <5s execution each | Performance constraints specified per script |
| **Narrative** | Scripts tell story of test platform foundation solidification | Checkpoint artifact synthesizes narrative |
| **Recursive** | Scripts emit events enabling future analysis and iteration | Event taxonomy supports recursive improvement |
| **Computational** | Scripts optimize for <1s validation, <5s metrics collection | Performance benchmarks in acceptance criteria |
| **Emergent** | Scripts may reveal new failure patterns or flake sources | Property tests designed to surface edge cases |
| **Temporal** | Scripts enforce Phase 1 completion within 2-3 days | Sequencing optimized for rapid validation |
| **Spatial** | Scripts operate locally (dev), CI/CD (automated), production (validation) | Environment validator ensures consistency across spaces |
| **Holistic** | Scripts integrate into cf_cli, pytest, and CI/CD ecosystem | Integration points documented per script |
| **Validation** | Scripts produce artifacts with SHA256 hashes and structured logs | All outputs include cryptographic integrity |
| **Integration** | Scripts compose into unified Phase 1 validation pipeline | Execution sequence diagram shows integration |

---

## Sacred Geometry Alignment (Scripts Package)

| Pattern | Manifestation | Evidence |
|---------|---------------|----------|
| **Triangle (Stability)** | Three-point validation in env validator (Python, lock, vars) | AC-5 enforcement |
| **Circle (Completeness)** | All metrics consolidated in single baseline artifact | AC-1 "all metric fields present" |
| **Spiral (Iteration)** | Fail-fast benchmark enables iterative improvement | AC-2 "≥40%/≥60% improvement" |
| **Golden Ratio (Balance)** | 15 essential metrics vs exhaustive 100+ fields | Metrics collector optimization |
| **Fractal (Modularity)** | Reusable scripts across projects via schema versioning | Schema_version: "1.0" in all artifacts |

---

## Quality Gates Matrix (Scripts Package)

| Quality Gate | Scripts Involved | Enforcement |
|--------------|------------------|-------------|
| **1. Environment Validation** | validate_env.py | Hard abort (exit 1 on fail) |
| **2. Coverage Baseline** | collect_metrics.py | Hard threshold (coverage ≥70%) |
| **3. Fail-Fast Improvement** | failfast_wrapper.py | Advisory metrics (≥40%/≥60% targets) |
| **4. Property Stability** | aggregate_property_tests.py | Advisory trend (30 consecutive passes) |
| **5. Event Taxonomy Completeness** | All scripts | Hard audit (all required events emitted) |
| **6. Artifact Hash Integrity** | collect_metrics.py | Hard (SHA256 present in all artifacts) |

---

## UCL Compliance Checklist (Scripts Package)

- [ ] **No Orphaned Contexts**: All scripts reference parent plan document
- [ ] **No Cyclical Dependencies**: Scripts have DAG execution order (validate_env → tests → collect_metrics → failfast → property)
- [ ] **Evidence Completeness**: All scripts emit JSONL events and produce hashed artifacts
- [ ] **Traceability**: Events include `context` field linking to plan sections
- [ ] **Reproducibility**: All scripts use deterministic hashing and structured logging

---

## Implementation Roadmap

### Phase 1.1: Environment Validator (Day 1, 2-3 hours)
- [ ] Implement validate_env.py core logic
- [ ] Write unit tests (3 tests: pass, version mismatch, lock mismatch)
- [ ] Integrate with pytest conftest.py
- [ ] Validate AC-5 and Quality Gate 1

### Phase 1.2: Metrics Collector (Day 1-2, 3-4 hours)
- [ ] Implement XML/JSON parsers for coverage, complexity, test results
- [ ] Implement baseline.metrics.json generation with SHA256
- [ ] Write unit tests (5 tests: full parse, missing files, hash integrity, null fields, schema validation)
- [ ] Validate AC-1 and Quality Gate 2

### Phase 1.3: Fail-Fast Wiring (Day 2, 4-5 hours)
- [ ] Implement pytest programmatic invocation with --maxfail/--exitfirst
- [ ] Implement benchmark comparison logic
- [ ] Write integration tests (3 tests: baseline mode, soft mode, hard mode)
- [ ] Seed intentional failure for testing
- [ ] Validate AC-2 and Quality Gate 3

### Phase 1.4: Property Tests Aggregator (Day 2-3, 3-4 hours)
- [ ] Implement Hypothesis test discovery and 30-run loop
- [ ] Implement determinism and performance validation
- [ ] Write property tests (3 tests: idempotent metrics, commutative operations, invariant preservation)
- [ ] Validate AC-3 and Quality Gate 4

### Phase 1.5: Integration & Checkpoint (Day 3, 2-3 hours)
- [ ] Wire all scripts into unified execution sequence
- [ ] Generate foundation.checkpoint.md and .json
- [ ] Validate AC-4 and Quality Gates 5-6
- [ ] Run full Phase 1 validation pipeline
- [ ] Document results in AAR

---

## Versioning & Changelog Governance

All script changes must:
1. Update version in docstring (semantic versioning: MAJOR.MINOR.PATCH)
2. Add entry to `CHANGELOG-tprPhase1-scripts.md` with:
   - Date, version, change type (Added/Changed/Fixed/Removed)
   - Impact on acceptance criteria
   - Event taxonomy additions
3. Recompute SHA256 hash of this specification document

---

## Document Integrity

**Document SHA256**: <TO-BE-COMPUTED-AFTER-APPROVAL>
**Last Modified**: 2025-11-23T01:15:00Z
**Next Review**: After Phase 1.1 completion (validate_env.py implemented)

---

**AUTHORIZATION**: This specification is DRAFT pending review. Implementation SHALL NOT commence until:
1. COF 13D analysis verified complete
2. Sacred Geometry alignment confirmed
3. UCL compliance checklist validated
4. Quality Gates matrix cross-referenced with plan document
5. Document hash computed and recorded

**SIGN-OFF**: [PENDING]
