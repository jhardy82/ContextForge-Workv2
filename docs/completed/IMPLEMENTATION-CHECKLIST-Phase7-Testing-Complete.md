# OutputManager Phase 7 Testing - Complete Implementation Checklist

**Document**: IMPLEMENTATION-CHECKLIST-Phase7-Testing-Complete.md
**Created**: 2025-11-14
**Phase**: 7 - Testing & Validation
**Status**: IN PROGRESS
**Lead**: Software Quality Engineer

---

## Executive Summary

This document provides a **granular, step-by-step checklist** for implementing the complete OutputManager test suite. All tasks are broken down into **15-30 minute executable chunks** with explicit acceptance criteria, commands, and validation steps.

### Checklist Statistics
- **Total Tasks**: 42 (expanded from 21)
- **Completed**: 6 tasks (14%)
- **In Progress**: 1 task (2%)
- **Pending**: 35 tasks (84%)
- **Total Estimated Time**: ~18 hours remaining

### Test Coverage Breakdown
- **Research Phase**: 3 tasks (~50 minutes) - Understanding test requirements
- **Unit Tests**: 7 tasks (~4 hours) - 21+ tests across 4 suites
- **Integration Tests**: 5 tasks (~2.5 hours) - 9 tests across 2 suites
- **Regression Tests**: 3 tasks (~1.25 hours) - Golden fixture validation
- **Quality Gates**: 6 tasks (~1 hour) - Comprehensive validation
- **Migration Work**: 4 tasks (~6 hours) - SRE command migrations
- **Documentation**: 4 tasks (~3 hours) - AAR, docs, finalization

---

## Phase 6 - Implementation & Integration (✅ COMPLETE)

### ✅ Task 1: phase-5-0 (COMPLETED)
**Action**: Transform checklist into atomic action list
**Status**: ✅ COMPLETE
**Owner**: Engineering Team Lead
**Duration**: 30 minutes
**Deliverable**: ACTION-LIST with 6 personas assigned

---

### ✅ Task 2: phase-5-1 (COMPLETED)
**Action**: Generate SyncReport with integration anchors
**Status**: ✅ COMPLETE
**Owner**: DevOps Platform Engineer
**Duration**: 20 minutes
**Deliverable**: SyncReport.OutputManager.20251113.yaml

---

### ✅ Task 3: phase-6-1 (COMPLETED)
**Action**: Implement OutputManager v1.0.0
**Status**: ✅ COMPLETE
**Owner**: DevOps Platform Engineer
**Duration**: 2 hours
**Deliverable**: src/output_manager.py (clean, importable, version-validated)

**Validation**:
```powershell
python -c "from src.output_manager import OutputManager; print(OutputManager.VERSION)"
# Expected: 1.0.0
```

---

### ✅ Task 4: phase-6-2 (COMPLETED)
**Action**: Integrate root callback with feature flag
**Status**: ✅ COMPLETE
**Owner**: DevOps Platform Engineer
**Duration**: 30 minutes
**Deliverable**: cf_cli.py lines ~780-820 patched

**Validation**:
```powershell
$env:CF_CLI_USE_OUTPUT_MANAGER="1"
python cf_cli.py --help
# Expected: No errors, flag bootstrap working
```

---

### ✅ Task 5: phase-6-3 (COMPLETED)
**Action**: Migrate pilot command (status system)
**Status**: ✅ COMPLETE
**Owner**: Site Reliability Engineer
**Duration**: 30 minutes
**Deliverable**: cf_cli.py lines ~6165-6190 patched

**Validation**:
```powershell
$env:CF_CLI_USE_OUTPUT_MANAGER="1"
python cf_cli.py status system --json
# Expected: JSON envelope with version=1.0.0, ok=true, result={...}
```

---

### ✅ Task 6: phase-6-3a (COMPLETED)
**Action**: Capture SHA256 baseline fixtures
**Status**: ✅ COMPLETE
**Owner**: DevOps Platform Engineer
**Duration**: 30 minutes
**Deliverable**: tests/fixtures/baselines/*.json (2 files)

**Validation**:
```powershell
Get-FileHash tests/fixtures/baselines/*.json -Algorithm SHA256
# Expected: 2 hashes displayed
# Legacy: B1E96342890C8BFE75F099D67E95CD288A2A1F1D3F1F3E05C082D8D9A2F5B833
# OutputManager: 64C44BAEEDCE2AF1EAF704A1A5E93EFEFCDA573874AD191854D10DAD6A7084FB
```

**⚠️ Known Issue**: Bootstrap messages (DTM API, PM2, ETW) contaminating baselines. Separate cleanup ticket recommended.

---

## Phase 7 - Testing & Validation Framework

### Delegation Model: Research Subagents + Primary Implementers

**Architecture**: Two-tier agent system for maximum accuracy and efficiency

#### Tier 1: Research Subagents (ANALYSIS ONLY - NO FILE CREATION)
**Purpose**: Gather intelligence, analyze specifications, design patterns, provide recommendations

**Research Subagent Responsibilities**:
- 📖 **Document Analysis**: Extract requirements from TestSpecification.md, architecture docs, API references
- 🔬 **Pattern Research**: Analyze pytest best practices, fixture patterns, mock strategies
- 📊 **Data Design**: Design test data generators, edge case catalogs, validation matrices
- 🎯 **Strategy Design**: Propose implementation approaches, identify potential issues, recommend optimizations
- 📋 **Deliverables**: Structured reports, design specifications, recommendation lists (VERBAL/IN-MEMORY ONLY)

**Critical Rule**: Research subagents **NEVER create files**. They analyze, design, and report findings to primary agents.

#### Tier 2: Primary Implementation Agents (EXECUTION & FILE CREATION)
**Purpose**: Implement code, create files, execute tests, validate results

**Primary Agent Responsibilities**:
- ✍️ **File Creation**: Create all test files, implement all test code
- 🔧 **Implementation**: Write pytest tests, fixtures, generators based on subagent designs
- ✅ **Execution**: Run test suites, validate results, debug failures
- 📈 **Validation**: Measure coverage, validate quality gates, document outcomes
- 🎯 **Deliverables**: Runnable test code, coverage reports, validation evidence

**Critical Rule**: Primary agents **create all files** based on research subagent recommendations.

#### Workflow Example:
```
┌─────────────────────────────────────────────────────────────────┐
│ RESEARCH SUBAGENT PHASE                                         │
├─────────────────────────────────────────────────────────────────┤
│ 1. Read TestSpecification.md                                    │
│ 2. Extract 21+ unit test requirements                           │
│ 3. Design pytest fixtures (output_manager, utc_datetime, etc.)  │
│ 4. Design test data generators (datetime, Decimal, UUID edges)  │
│ 5. Recommend implementation patterns                            │
│ 6. Deliver structured report to PRIMARY Quality Engineer        │
│    ▶️ NO FILES CREATED                                          │
└─────────────────────────────────────────────────────────────────┘
                            ⬇️
┌─────────────────────────────────────────────────────────────────┐
│ PRIMARY IMPLEMENTATION PHASE                                    │
├─────────────────────────────────────────────────────────────────┤
│ 1. Receive research findings from subagent                      │
│ 2. Create tests/test_output_manager.py                          │
│ 3. Implement fixtures based on subagent designs                 │
│ 4. Implement 21+ unit tests following subagent specifications   │
│ 5. Run pytest suite, validate coverage ≥80%                     │
│ 6. Debug failures, iterate until 100% pass                      │
│    ✅ FILES CREATED, TESTS PASSING                              │
└─────────────────────────────────────────────────────────────────┘
```

#### Benefits of This Model:
- ✅ **Accuracy**: Research subagents ensure specifications are fully understood before implementation
- ✅ **Efficiency**: Primary agents receive clear, actionable designs instead of starting from scratch
- ✅ **Quality**: Thorough analysis reduces implementation errors and rework
- ✅ **Clarity**: Clear separation between research and implementation phases
- ✅ **Scalability**: Research findings can inform multiple implementation tasks

#### Task Identification:
- **RESEARCH SUBAGENT →**: Tasks prefixed with "RESEARCH SUBAGENT →" are analysis-only (NO FILE CREATION)
- **PRIMARY**: Tasks prefixed with "PRIMARY:" are implementation tasks (FILE CREATION ALLOWED)

---

## Phase 7.1 - Research & Test Design (🔄 IN PROGRESS)

### 🔄 Task 7: RESEARCH SUBAGENT → Quality - Extract Test Specifications (IN PROGRESS)
**Action**: Research subagent extracts all test requirements from TestSpecification.md
**Status**: 🔄 IN PROGRESS
**Owner**: Research Subagent (supporting Software Quality Engineer)
**Duration**: 15 minutes
**Priority**: HIGH
**Delegation Model**: RESEARCH ONLY - NO FILE CREATION

**Steps** (Research Subagent):
1. Read test spec: `projects/P-OUTPUTMANAGER-CENTRALIZATION/plans/TestSpecification.OutputManager.20251113.md`
2. Extract all test names and descriptions into structured analysis
3. Identify test data requirements (datetime fixtures, mock objects, etc.)
4. Catalog pytest fixtures needed (capsys, tmp_path, monkeypatch, etc.)
5. **Deliver findings to PRIMARY Quality Engineer** - NO FILE CREATION

**Deliverable**: Verbal/structured report to primary agent with:
- Complete list of 21+ unit test names
- Complete list of 9 integration test names
- Test data requirements catalog
- pytest fixture requirements list

**Acceptance Criteria**:
- [ ] All 21+ unit test names documented
- [ ] All 9 integration test names documented
- [ ] Test data requirements identified
- [ ] pytest fixture requirements catalogued

**Validation**:
```powershell
# Verify test spec exists and is readable
Test-Path "projects/P-OUTPUTMANAGER-CENTRALIZATION/plans/TestSpecification.OutputManager.20251113.md"
# Expected: True
```

---

### ⏳ Task 8: RESEARCH SUBAGENT → Quality - Analyze pytest Fixtures (PENDING)
**Action**: Research subagent designs pytest fixtures and mock strategy
**Status**: ⏳ PENDING
**Owner**: Research Subagent (supporting Software Quality Engineer)
**Duration**: 15 minutes
**Priority**: HIGH
**Delegation Model**: RESEARCH & DESIGN ONLY - NO FILE CREATION

**Steps** (Research Subagent):
1. Design `@pytest.fixture` for OutputManager instance (singleton reset pattern)
2. Design `@pytest.fixture` for capturing stdout/stderr (capsys wrapper strategy)
3. Design `@pytest.fixture` for test datetime objects (UTC + naive timezone handling)
4. Design `@pytest.fixture` for Decimal/UUID test data (edge case generators)
5. Design mock strategy for threading tests (concurrent access patterns)
6. **Deliver design specifications to PRIMARY Quality Engineer** - NO FILE CREATION

**Deliverable**: Verbal/structured report to primary agent with:
- Fixture design specifications (with example code snippets)
- Mock strategy recommendations
- Threading test approach
- Best practices for fixture reuse

**Acceptance Criteria**:
- [ ] Fixture for singleton instance reset designed
- [ ] Fixture for stdout capture designed
- [ ] Fixture for datetime test data designed
- [ ] Fixture for Decimal/UUID test data designed
- [ ] Mock strategy for threading documented

**Example Fixture Design**:
```python
@pytest.fixture
def output_manager():
    """Reset singleton between tests."""
    OutputManager._instance = None
    yield OutputManager()
    OutputManager._instance = None

@pytest.fixture
def utc_datetime():
    """Standard UTC datetime for testing."""
    return datetime(2025, 11, 13, 14, 30, 0, tzinfo=timezone.utc)
```

---

### ⏳ Task 9: RESEARCH SUBAGENT → Quality - Test Data Generators (PENDING)
**Action**: Research subagent designs test data generators for type adapters
**Status**: ⏳ PENDING
**Owner**: Research Subagent (supporting Software Quality Engineer)
**Duration**: 20 minutes
**Priority**: HIGH
**Delegation Model**: RESEARCH & DESIGN ONLY - NO FILE CREATION

**Steps** (Research Subagent):
1. Design generator for datetime edge cases (UTC, naive, far past, far future, microseconds)
2. Design generator for Decimal edge cases (very precise, very large, scientific notation)
3. Design generator for UUID versions (v1, v4, nil UUID, malformed)
4. Design generator for dict structures (nested, ordered, unordered, circular refs)
5. Design generator for invalid values (NaN, Infinity, non-serializable types)
6. **Deliver generator specifications to PRIMARY Quality Engineer** - NO FILE CREATION

**Deliverable**: Verbal/structured report to primary agent with:
- Test data generator specifications (with example implementations)
- Edge case catalogs per type
- Invalid value handling strategies
- Parameterization recommendations for pytest

**Acceptance Criteria**:
- [ ] datetime edge case generator designed
- [ ] Decimal edge case generator designed
- [ ] UUID test data generator designed
- [ ] dict structure generator designed
- [ ] Invalid value generator designed

**Example Generator**:
```python
def generate_datetime_cases():
    """Generate datetime test cases."""
    return [
        ("utc", datetime(2025, 11, 13, 14, 30, 0, tzinfo=timezone.utc)),
        ("naive", datetime(2025, 11, 13, 14, 30, 0)),
        ("far_past", datetime(1900, 1, 1, 0, 0, 0, tzinfo=timezone.utc)),
        ("far_future", datetime(2999, 12, 31, 23, 59, 59, tzinfo=timezone.utc)),
        ("microseconds", datetime(2025, 11, 13, 14, 30, 0, 123456, tzinfo=timezone.utc)),
    ]
```

---

## Phase 7.2 - Unit Test Implementation (⏳ PENDING)

**Delegation Model**: PRIMARY Quality Engineer implements all tests based on research subagent findings. Subagent provides designs, primary agent creates files and code.

### ⏳ Task 10: PRIMARY Quality - Create Test File Skeleton (PENDING)
**Action**: Create tests/test_output_manager.py with structure
**Status**: ⏳ PENDING
**Owner**: Software Quality Engineer (PRIMARY)
**Duration**: 10 minutes
**Priority**: HIGH
**Dependencies**: Tasks 7-9 (research subagent findings)

**Commands**:
```powershell
# Create test file
New-Item -ItemType File -Force -Path "tests/test_output_manager.py"

# Add initial structure
@"
# tests/test_output_manager.py
import pytest
from src.output_manager import OutputManager
from decimal import Decimal
from datetime import datetime, timezone
from uuid import UUID
import json
import threading

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def output_manager():
    '''Reset singleton between tests.'''
    OutputManager._instance = None
    yield OutputManager()
    OutputManager._instance = None

# ============================================================================
# TEST SUITE 1: SINGLETON PATTERN (3 tests)
# ============================================================================

def test_singleton_initialization():
    '''Verify OutputManager maintains singleton instance.'''
    pass  # TODO

def test_thread_safe_initialization():
    '''Verify singleton thread-safety.'''
    pass  # TODO

def test_activate_json_mode_idempotence():
    '''Verify activate_json_mode() can be called multiple times.'''
    pass  # TODO

# ============================================================================
# TEST SUITE 2: ENCODER CONFIGURATION (8 tests)
# ============================================================================

def test_datetime_encoding_utc_z_suffix():
    '''Verify datetime encodes to ISO-8601 with Z suffix.'''
    pass  # TODO

# ... (remaining 7 encoder tests)

# ============================================================================
# TEST SUITE 3: ENVELOPE HELPERS (6 tests)
# ============================================================================

def test_emit_success_envelope_contract():
    '''Verify emit_success produces correct envelope.'''
    pass  # TODO

# ... (remaining 5 envelope tests)

# ============================================================================
# TEST SUITE 4: JSON MODE ACTIVATION (4 tests)
# ============================================================================

def test_activate_json_mode_sets_flag():
    '''Verify activate_json_mode() sets _json_mode flag.'''
    pass  # TODO

# ... (remaining 3 mode tests)
"@ | Out-File -FilePath "tests/test_output_manager.py" -Encoding utf8
```

**Acceptance Criteria**:
- [ ] File created at tests/test_output_manager.py
- [ ] 21+ test function stubs present
- [ ] Proper pytest structure with fixtures
- [ ] Organized into 4 test suites with comments

**Validation**:
```powershell
pytest tests/test_output_manager.py --collect-only
# Expected: 21 collected items (all skipped with pass stubs)
```

---

### ⏳ Task 11: PRIMARY Quality - Suite 1 - Singleton Tests (PENDING)
**Action**: Implement 3 singleton pattern tests
**Status**: ⏳ PENDING
**Owner**: Software Quality Engineer (PRIMARY)
**Duration**: 30 minutes
**Priority**: HIGH
**Dependencies**: Task 10 (skeleton), Task 8 (fixture designs from research subagent)

**Tests to Implement**:
1. `test_singleton_initialization` - Same instance verification
2. `test_thread_safe_initialization` - Concurrent access validation
3. `test_activate_json_mode_idempotence` - Multiple activation safety

**Implementation Guide**:
```python
def test_singleton_initialization(output_manager):
    '''Verify OutputManager maintains singleton instance.'''
    instance1 = OutputManager()
    instance2 = OutputManager()
    assert instance1 is instance2
    assert id(instance1) == id(instance2)

def test_thread_safe_initialization():
    '''Verify singleton thread-safety under concurrent access.'''
    OutputManager._instance = None
    instances = []

    def get_instance():
        instances.append(OutputManager())

    threads = [threading.Thread(target=get_instance) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # All threads should get same instance
    assert len(set(map(id, instances))) == 1

def test_activate_json_mode_idempotence(output_manager):
    '''Verify activate_json_mode() can be called multiple times safely.'''
    instance = output_manager

    # Call 3 times
    instance.activate_json_mode()
    instance.activate_json_mode()
    instance.activate_json_mode()

    # Should be set correctly
    assert instance._json_mode == True
    assert instance.is_json_mode == True
```

**Acceptance Criteria**:
- [ ] All 3 tests implemented
- [ ] All 3 tests passing
- [ ] Proper assertions with clear error messages
- [ ] Threading test uses 10+ concurrent threads

**Validation**:
```powershell
pytest tests/test_output_manager.py::test_singleton_initialization -v
pytest tests/test_output_manager.py::test_thread_safe_initialization -v
pytest tests/test_output_manager.py::test_activate_json_mode_idempotence -v
# Expected: 3 passed
```

---

### ⏳ Task 12: UNIT - Suite 2 Part 1 - Encoder Tests (PENDING)
**Action**: Implement 4 type adapter encoder tests
**Status**: ⏳ PENDING
**Owner**: Software Quality Engineer
**Duration**: 45 minutes
**Priority**: HIGH

**Tests to Implement**:
1. `test_datetime_encoding_utc_z_suffix` - UTC datetime → ISO-8601 with Z
2. `test_datetime_encoding_naive_assumes_utc` - Naive datetime → UTC Z
3. `test_decimal_encoding_as_string` - Decimal → quoted string
4. `test_uuid_encoding_as_string` - UUID → hyphenated string

**Implementation Guide** (test_datetime_encoding_utc_z_suffix):
```python
def test_datetime_encoding_utc_z_suffix(output_manager, capsys):
    '''Verify datetime objects encode to ISO-8601 with Z suffix.'''
    dt = datetime(2025, 11, 13, 14, 30, 0, tzinfo=timezone.utc)

    output_manager.activate_json_mode()
    output_manager.emit_success(result={"timestamp": dt})

    captured = capsys.readouterr()
    json_output = json.loads(captured.out)

    assert json_output["result"]["timestamp"] == "2025-11-13T14:30:00Z"
    assert json_output["ok"] == True
    assert json_output["version"] == "1.0.0"
```

**Acceptance Criteria**:
- [ ] All 4 tests implemented with proper fixtures
- [ ] All 4 tests passing
- [ ] Proper use of capsys to capture stdout
- [ ] JSON parsing validates output structure

**Validation**:
```powershell
pytest tests/test_output_manager.py -k "encoding" -v
# Expected: 4 passed (after Part 2 completed: 8 passed)
```

---

### ⏳ Task 13: UNIT - Suite 2 Part 2 - Encoder Edge Cases (PENDING)
**Action**: Implement 4 encoder edge case tests
**Status**: ⏳ PENDING
**Owner**: Software Quality Engineer
**Duration**: 45 minutes
**Priority**: HIGH

**Tests to Implement**:
1. `test_nan_rejection` - NaN values raise TypeError
2. `test_infinity_rejection` - Infinity values raise TypeError
3. `test_deterministic_dict_ordering` - sort_keys=True consistency
4. `test_compact_separators` - Compact JSON with no spaces

**Implementation Guide** (test_nan_rejection):
```python
def test_nan_rejection(output_manager):
    '''Verify NaN values raise TypeError (allow_nan=False).'''
    nan_value = float('nan')

    output_manager.activate_json_mode()

    with pytest.raises(TypeError, match="Out of range float"):
        output_manager.emit_success(result={"value": nan_value})
```

**Acceptance Criteria**:
- [ ] All 4 tests implemented
- [ ] All 4 tests passing
- [ ] NaN/Infinity tests properly use pytest.raises
- [ ] Determinism test validates SHA256 hash matching

**Validation**:
```powershell
pytest tests/test_output_manager.py::test_nan_rejection -v
pytest tests/test_output_manager.py::test_infinity_rejection -v
pytest tests/test_output_manager.py::test_deterministic_dict_ordering -v
pytest tests/test_output_manager.py::test_compact_separators -v
# Expected: 4 passed
```

---

### ⏳ Task 14: UNIT - Suite 3 - Envelope Tests (PENDING)
**Action**: Implement 6 envelope contract tests
**Status**: ⏳ PENDING
**Owner**: Software Quality Engineer
**Duration**: 60 minutes
**Priority**: HIGH

**Tests to Implement**:
1. `test_emit_success_envelope_contract` - Success envelope structure
2. `test_emit_error_envelope_contract` - Error envelope structure
3. `test_emit_partial_failure_envelope_contract` - Partial-failure semantics
4. `test_error_details_secret_redaction` - Sensitive field scrubbing (if implemented)
5. `test_meta_optional` - Meta parameter is optional
6. `test_version_field_constant` - Version always "1.0.0"

**Implementation Guide** (test_emit_success_envelope_contract):
```python
def test_emit_success_envelope_contract(output_manager, capsys):
    '''Verify emit_success produces correct envelope structure.'''
    result = {"tasks": [{"id": "T-001"}]}
    meta = {"command": "tasks list"}

    output_manager.activate_json_mode()
    output_manager.emit_success(result=result, meta=meta)

    captured = capsys.readouterr()
    envelope = json.loads(captured.out)

    assert envelope["version"] == "1.0.0"
    assert envelope["ok"] == True
    assert envelope["result"] == result
    assert envelope["meta"] == meta
    assert "error" not in envelope
```

**Acceptance Criteria**:
- [ ] All 6 tests implemented
- [ ] All 6 tests passing
- [ ] Envelope structure validated per spec
- [ ] Success, error, and partial-failure paths tested

**Validation**:
```powershell
pytest tests/test_output_manager.py -k "envelope" -v
# Expected: 6 passed (3 envelope tests + 3 related)
```

---

### ⏳ Task 15: UNIT - Suite 4 - JSON Mode Tests (PENDING)
**Action**: Implement 4 JSON mode activation tests
**Status**: ⏳ PENDING
**Owner**: Software Quality Engineer
**Duration**: 30 minutes
**Priority**: HIGH

**Tests to Implement**:
1. `test_activate_json_mode_sets_flag` - Internal flag toggle
2. `test_activate_json_mode_sets_env_vars` - Environment variable mutation
3. `test_is_json_mode_property` - Property reflects state
4. `test_deactivate_json_mode_not_implemented` - No deactivation method

**Implementation Guide** (test_activate_json_mode_sets_env_vars):
```python
import os

def test_activate_json_mode_sets_env_vars(output_manager, monkeypatch):
    '''Verify activate_json_mode() sets required environment variables.'''
    # Clear env vars first
    monkeypatch.delenv("CF_CLI_STDOUT_JSON_ONLY", raising=False)
    monkeypatch.delenv("CF_CLI_SUPPRESS_SESSION_EVENTS", raising=False)

    output_manager.activate_json_mode()

    assert os.environ.get("CF_CLI_STDOUT_JSON_ONLY") == "1"
    assert os.environ.get("CF_CLI_SUPPRESS_SESSION_EVENTS") == "1"
```

**Acceptance Criteria**:
- [ ] All 4 tests implemented
- [ ] All 4 tests passing
- [ ] Environment variable tests use monkeypatch fixture
- [ ] Deactivation test verifies no such method exists

**Validation**:
```powershell
pytest tests/test_output_manager.py -k "json_mode" -v
# Expected: 4 passed (+ idempotence test from Suite 1 = 5 total)
```

---

### ⏳ Task 16: UNIT - Run Coverage Analysis (PENDING)
**Action**: Execute full unit test suite with coverage report
**Status**: ⏳ PENDING
**Owner**: Software Quality Engineer
**Duration**: 20 minutes
**Priority**: HIGH

**Commands**:
```powershell
# Run tests with coverage
pytest tests/test_output_manager.py -v --cov=src.output_manager --cov-report=term-missing --cov-report=html

# Expected output:
# ========== 21 passed in X.XXs ==========
# Coverage: 100%

# Open HTML report
Invoke-Item htmlcov/index.html
```

**Acceptance Criteria**:
- [ ] All 21+ tests passing
- [ ] Coverage ≥100% (all lines covered)
- [ ] No uncovered lines in src/output_manager.py
- [ ] HTML coverage report generated

**Quality Gate**:
- **MUST ACHIEVE**: ≥80% coverage (target: 100%)
- **BLOCKS**: Integration tests if coverage <80%

---

### ⏳ Task 17: UNIT - Fix Failures and Coverage Gaps (PENDING)
**Action**: Debug any failing tests or coverage gaps
**Status**: ⏳ PENDING
**Owner**: Software Quality Engineer
**Duration**: 30 minutes (buffer)
**Priority**: HIGH

**Steps**:
1. Identify failing tests from pytest output
2. Debug test logic vs. actual OutputManager behavior
3. Identify uncovered lines from coverage report
4. Add tests for uncovered edge cases
5. Re-run full suite until 100% pass + ≥80% coverage

**Acceptance Criteria**:
- [ ] Zero failing tests
- [ ] Coverage ≥80% achieved
- [ ] All edge cases covered
- [ ] Determinism validated (repeated runs identical)

**Validation**:
```powershell
# Run 3 times to verify determinism
for ($i=1; $i -le 3; $i++) {
    pytest tests/test_output_manager.py --tb=short
}
# Expected: Identical pass counts all 3 runs
```

---

## Phase 7.3 - Integration Test Implementation (⏳ PENDING)

**Delegation Model**: PRIMARY Quality Engineer implements all integration tests. No research subagent phase needed (patterns already established in unit tests).

### ⏳ Task 18: PRIMARY Quality - Create Test File Skeleton (PENDING)
**Action**: Create tests/integration/test_cf_cli_json_mode.py
**Status**: ⏳ PENDING
**Owner**: Software Quality Engineer
**Duration**: 10 minutes
**Priority**: HIGH

**Commands**:
```powershell
# Create integration test directory
New-Item -ItemType Directory -Force -Path "tests/integration"

# Create test file
@"
# tests/integration/test_cf_cli_json_mode.py
import subprocess
import json
import pytest
import os

# ============================================================================
# TEST SUITE 5: CLI FLAG BEHAVIOR (5 tests)
# ============================================================================

def test_cli_without_json_flag_human_output():
    '''Verify cf system (no --json) produces human-readable output.'''
    pass  # TODO

def test_cli_with_json_flag_pure_json():
    '''Verify cf system --json produces pure JSON envelope.'''
    pass  # TODO

def test_json_flag_suppresses_session_events():
    '''Verify --json suppresses session logging.'''
    pass  # TODO

def test_json_flag_quiet_mode_coordination():
    '''Verify --json implicitly sets quiet mode.'''
    pass  # TODO

def test_json_flag_rich_stderr_coordination():
    '''Verify --json routes Rich to stderr only.'''
    pass  # TODO

# ============================================================================
# TEST SUITE 6: ENVELOPE CONTRACT CONFORMANCE (4 tests)
# ============================================================================

def test_success_envelope_structure():
    '''Verify success commands produce correct envelope.'''
    pass  # TODO

def test_error_envelope_structure():
    '''Verify error commands produce correct envelope.'''
    pass  # TODO

def test_partial_failure_envelope_structure():
    '''Verify batch commands produce partial-failure envelope.'''
    pass  # TODO

def test_deterministic_output():
    '''Verify repeated calls produce identical output.'''
    pass  # TODO
"@ | Out-File -FilePath "tests/integration/test_cf_cli_json_mode.py" -Encoding utf8
```

**Acceptance Criteria**:
- [ ] Directory created: tests/integration/
- [ ] File created with 9 test function stubs
- [ ] Proper pytest structure
- [ ] Organized into 2 test suites

**Validation**:
```powershell
pytest tests/integration/test_cf_cli_json_mode.py --collect-only
# Expected: 9 collected items
```

---

### ⏳ Task 19: INTEGRATION - Suite 5 - CLI Flag Tests (PENDING)
**Action**: Implement 5 CLI flag behavior tests
**Status**: ⏳ PENDING
**Owner**: Software Quality Engineer
**Duration**: 60 minutes
**Priority**: HIGH

**Implementation Guide** (test_cli_with_json_flag_pure_json):
```python
def test_cli_with_json_flag_pure_json():
    '''Verify cf status system --json produces pure JSON envelope.'''
    env = os.environ.copy()
    env["CF_CLI_USE_OUTPUT_MANAGER"] = "1"
    env["PYTHONWARNINGS"] = "ignore"

    result = subprocess.run(
        ["python", "cf_cli.py", "status", "system", "--json"],
        capture_output=True,
        text=True,
        env=env
    )

    # Parse stdout as JSON
    envelope = json.loads(result.stdout)

    # Validate envelope structure
    assert envelope["version"] == "1.0.0"
    assert envelope["ok"] == True
    assert "result" in envelope
    assert "meta" in envelope

    # Verify no ANSI codes
    assert "\x1b[" not in result.stdout
```

**Acceptance Criteria**:
- [ ] All 5 tests implemented with subprocess isolation
- [ ] All 5 tests passing
- [ ] Environment variable manipulation proper
- [ ] Stdout/stderr separation validated

**Validation**:
```powershell
pytest tests/integration/test_cf_cli_json_mode.py -k "flag" -v
# Expected: 5 passed
```

---

### ⏳ Task 20: INTEGRATION - Suite 6 - Envelope Contract Tests (PENDING)
**Action**: Implement 4 envelope contract conformance tests
**Status**: ⏳ PENDING
**Owner**: Software Quality Engineer
**Duration**: 45 minutes
**Priority**: HIGH

**Tests to Implement**:
1. `test_success_envelope_structure` - Success envelope validation
2. `test_error_envelope_structure` - Error envelope validation
3. `test_partial_failure_envelope_structure` - Partial-failure validation
4. `test_deterministic_output` - SHA256 hash matching

**Acceptance Criteria**:
- [ ] All 4 tests implemented
- [ ] All 4 tests passing
- [ ] Subprocess isolation for each test
- [ ] Determinism test runs command twice, compares hashes

**Validation**:
```powershell
pytest tests/integration/test_cf_cli_json_mode.py -k "envelope or deterministic" -v
# Expected: 4 passed
```

---

### ⏳ Task 21: INTEGRATION - Run Integration Suite (PENDING)
**Action**: Execute full integration test suite
**Status**: ⏳ PENDING
**Owner**: Software Quality Engineer
**Duration**: 15 minutes
**Priority**: HIGH

**Commands**:
```powershell
pytest tests/integration/ -v --tb=short
# Expected: 9 passed
```

**Acceptance Criteria**:
- [ ] All 9 integration tests passing
- [ ] No subprocess errors
- [ ] Proper environment isolation
- [ ] Exit codes validated

**Quality Gate**:
- **MUST ACHIEVE**: 100% integration tests passing
- **BLOCKS**: Diverse migration if any failures

---

### ⏳ Task 22: INTEGRATION - Fix Failing Tests (PENDING)
**Action**: Debug and fix any integration test failures
**Status**: ⏳ PENDING
**Owner**: Software Quality Engineer
**Duration**: 30 minutes (buffer)
**Priority**: HIGH

**Steps**:
1. Identify failing tests from pytest output
2. Check subprocess stderr for error details
3. Verify environment variable settings
4. Validate command-line arguments
5. Re-run until 100% pass

**Acceptance Criteria**:
- [ ] Zero failing integration tests
- [ ] All subprocess calls successful
- [ ] Proper JSON parsing in all tests

---

## Phase 7.4 - Test Validation & Reporting (⏳ PENDING)

**Delegation Model**: Research subagent analyzes quality gate requirements, PRIMARY Quality Engineer executes validation.

### ⏳ Task 23: RESEARCH SUBAGENT → Quality - Analyze Quality Gate Metrics (PENDING)
**Action**: Research subagent analyzes quality gate requirements and evidence collection strategies
**Status**: ⏳ PENDING
**Owner**: Research Subagent (supporting Software Quality Engineer)
**Duration**: 10 minutes
**Priority**: HIGH
**Delegation Model**: RESEARCH ONLY - NO FILE CREATION

**Steps** (Research Subagent):
1. Review 6 quality gate definitions from TestSpecification.md
2. Identify metrics collection methods for each gate
3. Design evidence gathering strategies (commands, expected outputs)
4. Recommend validation approaches and acceptance criteria
5. **Deliver quality gate analysis to PRIMARY Quality Engineer** - NO FILE CREATION

**Deliverable**: Verbal/structured report with:
- Quality gate execution plan (6 gates)
- Metrics collection commands
- Evidence requirements per gate
- Pass/fail criteria specifications

---

### ⏳ Task 24: PRIMARY Quality - Generate Reports & Validate Gates (PENDING)
**Action**: Generate comprehensive test execution report and validate all 6 quality gates
**Status**: ⏳ PENDING
**Owner**: Software Quality Engineer (PRIMARY)
**Duration**: 20 minutes
**Priority**: HIGH
**Dependencies**: Task 23 (quality gate analysis from research subagent)

**Commands**:
```powershell
# Install pytest-html if not already installed
pip install pytest-html

# Run all tests with HTML report generation
pytest tests/ -v --html=reports/pytest-report.html --self-contained-html --cov=src.output_manager --cov-report=html

# Open reports
Invoke-Item reports/pytest-report.html
Invoke-Item htmlcov/index.html
```

**Acceptance Criteria**:
- [ ] HTML report generated at reports/pytest-report.html
- [ ] Coverage report at htmlcov/index.html
- [ ] All 6 quality gates validated (based on subagent analysis)
- [ ] Quality gate evidence documented

---

### ⏳ Task 24-OLD: Validate Quality Gates (NOW MERGED INTO TASK 24)
**Note**: This task is now part of Task 24 above (consolidated based on research subagent model)

**Quality Gates to Validate** (from research subagent analysis):

1. **Coverage Gate**: ≥80% (target: 100%)
   ```powershell
   pytest --cov=src.output_manager --cov-report=term | Select-String "TOTAL"
   # Expected: TOTAL ... 100% or ≥80%
   ```

2. **Determinism Gate**: 100% byte-for-byte identical
   ```powershell
   # Run pilot command 3 times, compare SHA256
   for ($i=1; $i -le 3; $i++) {
       $env:CF_CLI_USE_OUTPUT_MANAGER="1"
       python cf_cli.py status system --json | Out-File "temp_run_$i.json" -Encoding utf8
   }
   Get-FileHash temp_run_*.json -Algorithm SHA256
   # Expected: All 3 hashes identical
   ```

3. **Performance Overhead Gate**: ≤10%
   ```powershell
   # Benchmark: Run 10 times each (legacy vs OutputManager)
   Measure-Command {
       1..10 | ForEach-Object {
           $env:CF_CLI_USE_OUTPUT_MANAGER="0"
           python cf_cli.py status system --json > $null
       }
   } | Select-Object TotalMilliseconds

   Measure-Command {
       1..10 | ForEach-Object {
           $env:CF_CLI_USE_OUTPUT_MANAGER="1"
           python cf_cli.py status system --json > $null
       }
   } | Select-Object TotalMilliseconds

   # Calculate overhead percentage, must be ≤10%
   ```

4. **Zero Breaking Changes Gate**: Regression tests pass
   ```powershell
   pytest tests/regression/ -v
   # Expected: 100% pass
   ```

5. **Stdout Purity Gate**: No contamination
   ```powershell
   $env:CF_CLI_USE_OUTPUT_MANAGER="1"
   $output = python cf_cli.py status system --json 2>$null
   # Validate: First character is '{', last is '}'
   $output.Trim()[0] -eq '{' -and $output.Trim()[-1] -eq '}'
   ```

6. **Envelope Compliance Gate**: Schema validation
   ```powershell
   # All commands produce valid envelopes
   pytest tests/integration/test_cf_cli_json_mode.py -k "envelope" -v
   # Expected: 100% pass
   ```

**Acceptance Criteria**:
- [ ] Coverage ≥80%
- [ ] Determinism 100%
- [ ] Overhead ≤10%
- [ ] Zero breaking changes
- [ ] Stdout purity confirmed
- [ ] Envelope compliance validated

---

## Phase 7.5 - SRE Migration Work (⏳ PENDING)

**Delegation Model**: Research subagent analyzes migration patterns, PRIMARY SRE implements migrations.

### ⏳ Task 25: RESEARCH SUBAGENT → SRE - Analyze Diverse Command Patterns (PENDING)
**Action**: Research subagent analyzes 3 diverse commands for migration patterns
**Status**: ⏳ PENDING
**Owner**: Research Subagent (supporting Site Reliability Engineer)
**Duration**: 30 minutes
**Priority**: HIGH
**Delegation Model**: RESEARCH & ANALYSIS ONLY - NO FILE CREATION
**Dependencies**: Tasks 16-24 MUST PASS

**Commands to Analyze**:
1. `task create` - POST operation (create entity with validation)
2. `project list` - GET operation (read multiple with filtering)
3. `sprint show` - GET operation (read single with detailed output)

**Steps** (Research Subagent):
1. Analyze current implementation of each command in cf_cli.py
2. Identify OutputManager integration points (where JSON output occurs)
3. Map legacy qprint/print paths vs. new OutputManager paths
4. Design feature flag branching logic per command
5. Identify envelope structure requirements (meta fields, result format)
6. Catalog edge cases and error paths per command
7. **Deliver migration pattern analysis to PRIMARY SRE** - NO FILE CREATION

**Deliverable**: Verbal/structured report to primary agent with:
- Per-command integration point locations (line numbers)
- Feature flag branching patterns
- Envelope structure specifications
- Edge case handling requirements
- Migration implementation checklist per command

---

### ⏳ Task 26: PRIMARY SRE - Migrate 3 Diverse Commands (PENDING)
**Action**: Implement OutputManager integration for 3 diverse command patterns based on research subagent analysis
**Status**: ⏳ PENDING
**Owner**: Site Reliability Engineer (PRIMARY IMPLEMENTATION)
**Duration**: 90 minutes
**Priority**: HIGH
**Delegation Model**: PRIMARY IMPLEMENTATION - FILE CREATION ALLOWED
**Dependencies**: Task 25 (research subagent analysis), Tasks 16-24 MUST PASS

**Commands to Migrate**:
1. `task create` - POST operation (create entity with validation)
2. `project list` - GET operation (read multiple with filtering)
3. `sprint show` - GET operation (read single with detailed output)

**Implementation Pattern** (per command - based on research subagent design):
```python
# In cf_cli.py, find the command handler
@app.command("create")
def task_create(...):
    # ... existing logic ...

    # ADD: OutputManager integration (using research subagent pattern)
    if get_feature_flag("CF_CLI_USE_OUTPUT_MANAGER"):
        output_mgr = get_output_manager()
        output_mgr.emit_success(
            result={"task": task_dict},
            meta={"command": "task create", "task_id": task_id}
        )
        return

    # EXISTING: Legacy qprint path
    qprint(...)
```

**Acceptance Criteria** (per command):
- [ ] OutputManager path implemented
- [ ] Legacy path preserved
- [ ] Feature flag toggles correctly
- [ ] JSON envelope validated
- [ ] Manual testing passed

**Validation** (per command):
```powershell
# Test legacy mode
$env:CF_CLI_USE_OUTPUT_MANAGER="0"
python cf_cli.py task create --title "Test" --project P-001
# Expected: Human-readable output

# Test OutputManager mode
$env:CF_CLI_USE_OUTPUT_MANAGER="1"
python cf_cli.py task create --title "Test" --project P-001 --json
# Expected: JSON envelope with version=1.0.0, ok=true, result={task:...}
```

---

### ⏳ Task 27: PRIMARY Quality - Create Regression Test Module (PENDING)
**Action**: Create tests/regression/test_golden_fixtures.py based on research subagent patterns
**Status**: ⏳ PENDING
**Owner**: Software Quality Engineer (PRIMARY IMPLEMENTATION)
**Duration**: 30 minutes
**Priority**: HIGH
**Delegation Model**: PRIMARY IMPLEMENTATION - FILE CREATION ALLOWED
**Dependencies**: Task 26 (diverse commands migrated)

**Implementation** (using regression patterns from quality gates):
```python
# tests/regression/test_golden_fixtures.py
import subprocess, json, pytest, hashlib, os

def get_sha256(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def test_pilot_command_sha256_match():
    env = os.environ.copy()
    env['CF_CLI_USE_OUTPUT_MANAGER'] = '1'
    result = subprocess.run(['python', 'cf_cli.py', 'status', 'system', '--json'],
                          capture_output=True, text=True, env=env)
    with open('tests/fixtures/baselines/status_system_outputmanager.json') as f:
        expected_hash = get_sha256(f.read())
    assert get_sha256(result.stdout) == expected_hash
```

**Deliverable**: Regression test module with SHA256 validation

**Acceptance Criteria**:
- [ ] Regression test module created
- [ ] SHA256 comparison implemented
- [ ] Baseline loading working
- [ ] Tests passing

---

### ⏳ Task 28: PRIMARY Quality - Execute Regression Tests (PENDING)
**Action**: Run comprehensive regression tests on pilot + diverse commands
**Status**: ⏳ PENDING
**Owner**: Software Quality Engineer (PRIMARY IMPLEMENTATION)
**Duration**: 30 minutes
**Priority**: HIGH
**Delegation Model**: PRIMARY IMPLEMENTATION - FILE CREATION ALLOWED
**Dependencies**: Task 27 (regression module created)

**Commands**:
```bash
# Run all regression tests
pytest tests/regression/test_golden_fixtures.py -v

# Validate no output drift
pytest tests/regression/ --html=htmlcov/regression-report.html
```

**Deliverable**: Regression test execution report with 100% pass rate

**Acceptance Criteria**:
- [ ] All regression tests passing
- [ ] SHA256 hashes match baselines
- [ ] No output drift detected
- [ ] Determinism confirmed

---

## Phase 7.6 - AAR Generation & Session Closure (⏳ PENDING)

**Delegation Model**: Research subagent compiles metrics and lessons, PRIMARY Lead generates final AAR document.

### ⏳ Task 29: RESEARCH SUBAGENT → Lead - Compile AAR Metrics & Lessons (PENDING)
**Action**: Research subagent compiles comprehensive metrics, lessons learned, and recommendations
**Status**: ⏳ PENDING
**Owner**: Research Subagent (supporting Engineering Team Lead)
**Duration**: 45 minutes
**Priority**: HIGH
**Delegation Model**: RESEARCH & ANALYSIS ONLY - NO FILE CREATION
**Dependencies**: Tasks 16-28 COMPLETE (all testing and migration work finished)

**Steps** (Research Subagent):
1. Extract test metrics from pytest HTML report (coverage %, pass rate, test count)
2. Extract quality gate results from gate validation report (6 gates, pass/fail status)
3. Compile work statistics (total hours, tasks completed, persona contributions)
4. Document lessons learned from testing phase (successes, challenges, solutions)
5. Document lessons learned from migration phase (patterns discovered, pitfalls avoided)
6. Compile future recommendations (next batch priorities, optimization opportunities)
7. **Deliver comprehensive AAR metrics package to PRIMARY Lead** - NO FILE CREATION

**Deliverable**: Verbal/structured report to primary agent with:
- Test Metrics Summary (coverage %, pass rate, test count by suite)
- Quality Gate Results (6 gates with evidence status)
- Work Statistics (hours by phase, tasks by priority, persona hours)
- Lessons Learned (5+ key insights with context)
- Future Recommendations (3+ actionable next steps)
- Handoff Checklist (items for next sprint/phase)

**Acceptance Criteria**:
- [ ] All test metrics extracted and compiled
- [ ] All quality gate results documented with evidence
- [ ] Work statistics complete with hours and persona breakdown
- [ ] Lessons learned documented with specific examples
- [ ] Future recommendations actionable and prioritized
- [ ] Handoff checklist prepared
- [ ] Comprehensive metrics package delivered to PRIMARY Lead

---

### ⏳ Task 30: PRIMARY Lead - Generate Comprehensive AAR Document (PENDING)
**Action**: Create final After-Action Review document based on research subagent compilation
**Status**: ⏳ PENDING
**Owner**: Engineering Team Lead (PRIMARY IMPLEMENTATION)
**Duration**: 60 minutes
**Priority**: HIGH
**Delegation Model**: PRIMARY IMPLEMENTATION - FILE CREATION ALLOWED
**Dependencies**: Task 29 (research subagent AAR compilation)

**AAR Document Structure** (using research subagent data):
1. **Executive Summary** (3-5 paragraphs)
   - Project overview and objectives
   - Major accomplishments
   - Key metrics summary
   - Overall success assessment

2. **Work Statistics** (from research subagent)
   - Total hours: XX hours (breakdown by phase)
   - Tasks completed: 31 of 42 (high priority complete)
   - Persona contributions (hours per persona)

3. **Test Metrics** (from research subagent)
   - Unit test coverage: XX% (≥80% target)
   - Integration test coverage: XX%
   - Pass rate: 100% (30 of 30 tests)
   - Regression test results

4. **Quality Gate Results** (from research subagent)
   - Gate 1: Coverage ≥80% [PASS/FAIL]
   - Gate 2: Determinism 100% [PASS/FAIL]
   - Gate 3: Overhead ≤10% [PASS/FAIL]
   - Gate 4: Zero breaking changes [PASS/FAIL]
   - Gate 5: Stdout purity [PASS/FAIL]
   - Gate 6: Envelope compliance [PASS/FAIL]

5. **Lessons Learned** (from research subagent analysis)
   - What went well
   - What could be improved
   - Unexpected discoveries
   - Process improvements

6. **Future Recommendations** (from research subagent)
   - Batch 2-3 migration priorities
   - Performance optimization opportunities
   - Documentation enhancements
   - Tool/process improvements

7. **Handoff Checklist** (from research subagent)
   - Documentation locations
   - Configuration settings
   - Known issues/limitations
   - Next sprint priorities

**Commands**:
```bash
# Create AAR document
cat > AAR-OutputManager-Phase7-Complete-20251114.md << 'EOF'
# After-Action Review: OutputManager Phase 7 Testing Complete
[Complete AAR content based on research subagent compilation]
EOF
```

**Deliverable**: `AAR-OutputManager-Phase7-Complete-20251114.md`

**Acceptance Criteria**:
- [ ] AAR document created with all 7 sections
- [ ] All metrics from research subagent integrated
- [ ] Lessons learned documented with actionable insights
- [ ] Future recommendations prioritized and specific
- [ ] Handoff checklist complete and validated
- [ ] Document reviewed and finalized

---

### ⏳ Task 31: PRIMARY Lead - Session Finalization & Handoff (PENDING)
**Action**: Finalize session log and prepare comprehensive handoff
**Status**: ⏳ PENDING
**Owner**: Engineering Team Lead (PRIMARY IMPLEMENTATION)
**Duration**: 30 minutes
**Priority**: HIGH
**Delegation Model**: PRIMARY IMPLEMENTATION - FILE CREATION ALLOWED
**Dependencies**: Task 30 (AAR document complete)

**Steps**:
1. Update session log with final metrics and outcomes
2. Archive all test artifacts (HTML reports, baseline fixtures, evidence)
3. Tag git commit with phase completion milestone
4. Update project tracking system with completion status
5. Prepare handoff email/document for next sprint
6. Document any outstanding issues or blockers

**Commands**:
```bash
# Archive test artifacts
mkdir -p archives/phase7-testing-20251114/
cp -r tests/fixtures/ archives/phase7-testing-20251114/
cp -r htmlcov/ archives/phase7-testing-20251114/
cp pytest-report.html archives/phase7-testing-20251114/

# Tag git commit
git tag -a phase7-testing-complete -m "Phase 7 Testing Complete: 30/30 tests pass, 6/6 gates pass"
git push origin phase7-testing-complete

# Update session log (final entry)
echo "Session finalized: Phase 7 testing complete" >> .QSE/v2/Sessions/$(date +%Y-%m-%d)/session.log
```

**Deliverable**: Session finalization package

**Acceptance Criteria**:
- [ ] Session log updated with final metrics
- [ ] Test artifacts archived with timestamps
- [ ] Git milestone tag created and pushed
- [ ] Project tracking updated
- [ ] Handoff documentation prepared
- [ ] Outstanding issues documented

---

## Phase 7.7 - Batch Migrations & Documentation (⏳ PENDING - MEDIUM PRIORITY)

**Delegation Model**: Research subagent analyzes migration batches, PRIMARY SRE implements migrations.

### ⏳ Task 32: RESEARCH SUBAGENT → SRE - Analyze Batch 1 Commands (PENDING)
**Action**: Research subagent analyzes Batch 1 commands for migration patterns and complexity
**Status**: ⏳ PENDING
**Owner**: Research Subagent (supporting Site Reliability Engineer)
**Duration**: 45 minutes
**Priority**: MEDIUM
**Delegation Model**: RESEARCH & ANALYSIS ONLY - NO FILE CREATION
**Dependencies**: Tasks 27-28 COMPLETE (diverse command migrations validated)

**Batch 1 Commands to Analyze** (5-7 commands):
- High-frequency read operations
- Simple CRUD operations
- List/show command variations
- Status reporting commands

**Steps** (Research Subagent):
1. Identify Batch 1 candidate commands from cf_cli.py (high frequency, low complexity)
2. Analyze current implementation patterns (qprint vs structured output)
3. Categorize by complexity (simple, moderate, complex)
4. Map OutputManager integration points per command
5. Design feature flag branching logic per command
6. Identify common patterns for template reuse
7. **Deliver Batch 1 migration analysis to PRIMARY SRE** - NO FILE CREATION

**Deliverable**: Verbal/structured report to primary agent with:
- Batch 1 command list (5-7 commands prioritized)
- Per-command complexity assessment (simple/moderate/complex)
- Integration point locations (line numbers in cf_cli.py)
- Common pattern templates (reusable code snippets)
- Migration time estimates per command
- Risk assessment (low/medium/high per command)

**Acceptance Criteria**:
- [ ] Batch 1 commands identified and prioritized (5-7 commands)
- [ ] Complexity assessments complete
- [ ] Integration points mapped
- [ ] Common patterns documented for reuse
- [ ] Time estimates provided
- [ ] Risk assessments documented
- [ ] Analysis delivered to PRIMARY SRE

---

### ⏳ Task 33: PRIMARY SRE - Migrate Batch 1 Commands (PENDING)
**Action**: Implement OutputManager integration for Batch 1 commands based on research subagent analysis
**Status**: ⏳ PENDING
**Owner**: Site Reliability Engineer (PRIMARY IMPLEMENTATION)
**Duration**: 2 hours
**Priority**: MEDIUM
**Delegation Model**: PRIMARY IMPLEMENTATION - FILE CREATION ALLOWED
**Dependencies**: Task 32 (research subagent Batch 1 analysis)

**Implementation Process** (using research subagent patterns):
1. Apply common pattern templates from research analysis
2. Implement feature flag branching per command
3. Configure OutputManager envelope structures
4. Test each command individually (legacy vs OutputManager)
5. Validate exit codes and error handling
6. Update command tests if needed

**Commands**:
```bash
# Edit cf_cli.py for Batch 1 commands
nano cf_cli.py  # Apply migration patterns from research analysis

# Test each migrated command
python cf_cli.py <command> --json  # OutputManager path
python cf_cli.py <command>  # Legacy path

# Run regression tests
pytest tests/integration/test_cf_cli_json_mode.py -k batch1 -v
```

**Deliverable**: 5-7 commands migrated to OutputManager

**Acceptance Criteria**:
- [ ] All Batch 1 commands migrated (5-7 commands)
- [ ] Feature flags working per command
- [ ] JSON envelopes valid per command
- [ ] Legacy paths preserved per command
- [ ] Regression tests passing
- [ ] No breaking changes introduced

---

### ⏳ Task 34: PRIMARY SRE - Migrate Batch 2 Commands (PENDING)
**Action**: Implement OutputManager integration for Batch 2 commands (moderate complexity)
**Status**: ⏳ PENDING
**Owner**: Site Reliability Engineer (PRIMARY IMPLEMENTATION)
**Duration**: 2 hours
**Priority**: MEDIUM
**Delegation Model**: PRIMARY IMPLEMENTATION - FILE CREATION ALLOWED
**Dependencies**: Task 33 (Batch 1 complete and validated)

**Batch 2 Focus**: Moderate complexity commands with filtering, pagination, or aggregation

**Deliverable**: 5-7 commands migrated to OutputManager

**Acceptance Criteria**:
- [ ] All Batch 2 commands migrated
- [ ] Feature flags working
- [ ] JSON envelopes valid
- [ ] Regression tests passing

---

### ⏳ Task 35: PRIMARY SRE - Migrate Batch 3 Commands (PENDING)
**Action**: Implement OutputManager integration for remaining commands
**Status**: ⏳ PENDING
**Owner**: Site Reliability Engineer (PRIMARY IMPLEMENTATION)
**Duration**: 2 hours
**Priority**: MEDIUM
**Delegation Model**: PRIMARY IMPLEMENTATION - FILE CREATION ALLOWED
**Dependencies**: Task 34 (Batch 2 complete and validated)

**Batch 3 Focus**: Remaining commands and complex edge cases

**Deliverable**: All remaining commands migrated to OutputManager

**Acceptance Criteria**:
- [ ] All remaining commands migrated
- [ ] 100% command coverage achieved
- [ ] Feature flags working universally
- [ ] Comprehensive regression tests passing

---

### ⏳ Task 36: PRIMARY Quality - Execute Batch Regression Tests (PENDING)
**Action**: Run comprehensive regression test suite on all batches
**Status**: ⏳ PENDING
**Owner**: Software Quality Engineer (PRIMARY IMPLEMENTATION)
**Duration**: 1 hour
**Priority**: MEDIUM
**Delegation Model**: PRIMARY IMPLEMENTATION - FILE CREATION ALLOWED
**Dependencies**: Tasks 33-35 (all batch migrations complete)

**Test Scope**:
- All Batch 1 commands (5-7 tests)
- All Batch 2 commands (5-7 tests)
- All Batch 3 commands (remaining tests)
- Cross-command integration scenarios
- Error path scenarios

**Commands**:
```bash
# Run full regression suite
pytest tests/integration/test_cf_cli_json_mode.py -v --html=htmlcov/regression-report.html

# Generate coverage report
coverage html

# Validate quality gates
python scripts/validate_quality_gates.py --all-batches
```

**Deliverable**: Regression test report with 100% pass rate

**Acceptance Criteria**:
- [ ] All batch regression tests passing
- [ ] Zero breaking changes detected
- [ ] Coverage maintained at ≥80%
- [ ] Quality gates all passing
- [ ] HTML report generated

---

### ⏳ Task 37: PRIMARY Quality - Update Integration Test Documentation (PENDING)
**Action**: Update test documentation with batch migration details
**Status**: ⏳ PENDING
**Owner**: Software Quality Engineer (PRIMARY IMPLEMENTATION)
**Duration**: 30 minutes
**Priority**: MEDIUM
**Delegation Model**: PRIMARY IMPLEMENTATION - FILE CREATION ALLOWED
**Dependencies**: Task 36 (regression tests complete)

**Documentation Updates**:
- Add batch migration test cases to TestSpecification.md
- Update test matrix with command coverage
- Document regression test patterns
- Add troubleshooting guide for common failures

**Deliverable**: Updated test documentation

**Acceptance Criteria**:
- [ ] TestSpecification.md updated with batch details
- [ ] Test matrix shows 100% command coverage
- [ ] Regression patterns documented
- [ ] Troubleshooting guide complete

---

### ⏳ Task 38: PRIMARY DevOps - Update Configuration Management Docs (PENDING)
**Action**: Update configuration management documentation with OutputManager settings
**Status**: ⏳ PENDING
**Owner**: DevOps Platform Engineer (PRIMARY IMPLEMENTATION)
**Duration**: 45 minutes
**Priority**: MEDIUM
**Delegation Model**: PRIMARY IMPLEMENTATION - FILE CREATION ALLOWED
**Dependencies**: Task 37 (test documentation complete)

**Documentation Updates**:
- Document CF_CLI_USE_OUTPUT_MANAGER feature flag usage
- Document CF_CLI_STDOUT_JSON_ONLY environment variable
- Document CF_CLI_SUPPRESS_SESSION_EVENTS environment variable
- Add configuration examples for different deployment scenarios
- Update deployment checklist with OutputManager validation steps

**Deliverable**: Updated configuration management documentation

**Acceptance Criteria**:
- [ ] Feature flag documentation complete
- [ ] Environment variables documented
- [ ] Configuration examples provided
- [ ] Deployment checklist updated
- [ ] Documentation reviewed and validated

---

## Phase 7.8 - Error Handling & Future Enhancements (⏳ PENDING - LOW PRIORITY)

**Delegation Model**: Research subagent analyzes error scenarios and future patterns, PRIMARY Quality/Architecture implements.

### ⏳ Task 39: RESEARCH SUBAGENT → Quality - Analyze Error-Path Scenarios (PENDING)
**Action**: Research subagent analyzes error-path scenarios and edge case handling requirements
**Status**: ⏳ PENDING
**Owner**: Research Subagent (supporting Software Quality Engineer)
**Duration**: 30 minutes
**Priority**: LOW
**Delegation Model**: RESEARCH & ANALYSIS ONLY - NO FILE CREATION
**Dependencies**: Tasks 36-38 COMPLETE (all migrations and documentation finished)

**Error Scenarios to Analyze**:
1. OutputManager initialization failures
2. JSON serialization errors (non-serializable types)
3. Feature flag misconfiguration errors
4. Environment variable conflicts
5. Concurrent access race conditions
6. Envelope structure violations
7. stdout/stderr contamination scenarios
8. Graceful degradation paths (fallback to legacy)

**Steps** (Research Subagent):
1. Review OutputManager error handling code paths
2. Identify missing error scenarios (gaps in coverage)
3. Design error test scenarios (10+ test cases)
4. Map error paths to OutputManager methods
5. Design mock strategies for error injection
6. Categorize by severity (critical, high, medium, low)
7. **Deliver error-path analysis to PRIMARY Quality** - NO FILE CREATION

**Deliverable**: Verbal/structured report to primary agent with:
- Error scenario catalog (10+ scenarios with descriptions)
- Missing coverage gaps identified
- Test case designs (setup, execution, expected outcome)
- Mock strategy specifications (error injection patterns)
- Severity categorization (critical/high/medium/low)
- Priority recommendations (which tests to implement first)

**Acceptance Criteria**:
- [ ] Error scenarios catalogued (10+ scenarios)
- [ ] Coverage gaps identified
- [ ] Test case designs documented
- [ ] Mock strategies specified
- [ ] Severity categorization complete
- [ ] Analysis delivered to PRIMARY Quality

---

### ⏳ Task 40: PRIMARY Quality - Develop Error-Path Tests (PENDING)
**Action**: Implement error-path tests based on research subagent analysis
**Status**: ⏳ PENDING
**Owner**: Software Quality Engineer (PRIMARY IMPLEMENTATION)
**Duration**: 2 hours
**Priority**: LOW
**Delegation Model**: PRIMARY IMPLEMENTATION - FILE CREATION ALLOWED
**Dependencies**: Task 39 (research subagent error-path analysis)

**Test Implementation** (using research subagent designs):
- Implement 10+ error-path tests
- Use mock strategies from research analysis
- Cover all critical and high severity scenarios
- Validate graceful degradation paths
- Test error message clarity and usefulness

**Commands**:
```bash
# Create error-path test module
nano tests/test_output_manager_errors.py  # Using research subagent designs

# Run error-path tests
pytest tests/test_output_manager_errors.py -v

# Validate error coverage
coverage html --include=src/output_manager.py
```

**Deliverable**: Error-path test module with 10+ tests

**Acceptance Criteria**:
- [ ] Error-path test module created
- [ ] 10+ error tests implemented
- [ ] All critical scenarios covered
- [ ] Graceful degradation validated
- [ ] Error messages validated for clarity
- [ ] Tests passing

---

### ⏳ Task 41: RESEARCH SUBAGENT → Architecture - Research Advisory Enhancements (PENDING)
**Action**: Research subagent researches future enhancements and advanced patterns
**Status**: ⏳ PENDING
**Owner**: Research Subagent (supporting Solution Architecture Specialist)
**Duration**: 1 hour
**Priority**: LOW
**Delegation Model**: RESEARCH & ANALYSIS ONLY - NO FILE CREATION
**Dependencies**: Tasks 39-40 COMPLETE (error handling finished)

**Enhancement Areas to Research**:
1. Performance optimization opportunities (benchmarking, profiling)
2. Advanced envelope patterns (streaming, chunked responses)
3. Rich UI integration patterns (progress bars, animations)
4. Telemetry and observability enhancements
5. Multi-format output support (YAML, XML, TOML)
6. Structured logging integration improvements
7. Async/await patterns for long-running operations
8. Plugin architecture for custom encoders

**Steps** (Research Subagent):
1. Research industry best practices for CLI JSON output
2. Analyze Rich UI integration patterns and opportunities
3. Design telemetry event schemas for OutputManager
4. Research multi-format output patterns (Typer ecosystem)
5. Analyze async patterns for streaming output
6. Identify plugin architecture opportunities
7. **Deliver enhancement research to PRIMARY Architecture** - NO FILE CREATION

**Deliverable**: Verbal/structured report to primary agent with:
- Enhancement recommendations (5+ opportunities prioritized)
- Industry best practices summary
- Rich UI integration patterns
- Telemetry event schema designs
- Multi-format output strategy
- Async pattern recommendations
- Plugin architecture proposal

**Acceptance Criteria**:
- [ ] Enhancement opportunities researched (5+ recommendations)
- [ ] Industry best practices documented
- [ ] Rich UI patterns analyzed
- [ ] Telemetry schemas designed
- [ ] Multi-format strategy proposed
- [ ] Async patterns documented
- [ ] Research delivered to PRIMARY Architecture

---

### ⏳ Task 42: PRIMARY Architecture - Document Advisory Enhancements (PENDING)
**Action**: Document future enhancements and architectural recommendations based on research analysis
**Status**: ⏳ PENDING
**Owner**: Solution Architecture Specialist (PRIMARY IMPLEMENTATION)
**Duration**: 1 hour
**Priority**: LOW
**Delegation Model**: PRIMARY IMPLEMENTATION - FILE CREATION ALLOWED
**Dependencies**: Task 41 (research subagent enhancement research)

**Documentation Deliverables** (using research subagent findings):
1. **Enhancement Roadmap Document**
   - Phase 8: Performance optimization (benchmarks, profiling)
   - Phase 9: Rich UI integration (progress, animations)
   - Phase 10: Telemetry & observability
   - Phase 11: Multi-format support (YAML, XML)

2. **Architecture Decision Records (ADRs)**
   - ADR-001: Telemetry event schema design
   - ADR-002: Async streaming output patterns
   - ADR-003: Plugin architecture for custom encoders
   - ADR-004: Multi-format output strategy

3. **Implementation Guides**
   - Rich UI integration patterns with code examples
   - Telemetry instrumentation patterns
   - Plugin development guide for custom encoders
   - Async/await pattern examples

**Commands**:
```bash
# Create enhancement roadmap
cat > docs/OutputManager-Enhancement-Roadmap-20251114.md << 'EOF'
# OutputManager Enhancement Roadmap
[Complete roadmap based on research subagent findings]
EOF

# Create ADR documents
mkdir -p docs/adrs/
for i in 001 002 003 004; do
  cat > docs/adrs/ADR-$i-*.md << 'EOF'
# ADR-$i: [Title from research analysis]
[Complete ADR using research subagent designs]
EOF
done

# Create implementation guides
cat > docs/OutputManager-Implementation-Guides-20251114.md << 'EOF'
# OutputManager Implementation Guides
[Complete guides using research subagent patterns]
EOF
```

**Deliverable**: Comprehensive enhancement documentation suite

**Acceptance Criteria**:
- [ ] Enhancement roadmap document created
- [ ] 4 ADR documents created (telemetry, async, plugins, multi-format)
- [ ] Implementation guides created with code examples
- [ ] Documentation reviewed and validated
- [ ] Roadmap prioritized and scheduled

---

## Phase 7 Completion Summary

**Total Tasks**: 42 tasks across 8 phases
**Estimated Duration**: ~18 hours total
**High Priority**: Tasks 7-31 (25 tasks, ~12 hours)
**Medium Priority**: Tasks 32-38 (7 tasks, ~6 hours)
**Low Priority**: Tasks 39-42 (4 tasks, ~4 hours)

**Delegation Architecture**:
- **Research Subagent Tasks**: 7 tasks (Tasks 7-9, 23, 25, 29, 32, 39, 41) - NO FILE CREATION
- **Primary Implementation Tasks**: 35 tasks (remaining) - FILE CREATION ALLOWED

**Quality Gates**: 6 gates enforced throughout
**Test Coverage Goal**: ≥80% (target 100%)
**Regression Coverage**: 100% of migrated commands
**Documentation**: Complete with ADRs, guides, and roadmap

---

## Quick Reference Commands

### Run All Unit Tests
```powershell
pytest tests/test_output_manager.py -v --cov=src.output_manager --cov-report=html
```

### Run All Integration Tests
```powershell
pytest tests/integration/ -v
```

### Run All Regression Tests
```powershell
pytest tests/regression/ -v
```

### Run Complete Test Suite
```powershell
pytest tests/ -v --html=reports/pytest-report.html --self-contained-html
```

### Check Coverage
```powershell
pytest --cov=src.output_manager --cov-report=term-missing
```

### Validate Pilot Command
```powershell
$env:CF_CLI_USE_OUTPUT_MANAGER="1"
$env:PYTHONWARNINGS="ignore"
python cf_cli.py status system --json
```

---

## Progress Tracking

**Current Status**: 🔄 Task 7 IN PROGRESS (Research Phase)
**Completed**: 6 of 42 tasks (14%)
**Remaining**: 36 tasks (~18 hours)
**Next Milestone**: Complete Research (Tasks 7-9) → Begin Unit Tests (Tasks 10-17)

**Phase Summary**:
- **Phase 7.1 - Implementation & Integration**: ✅ COMPLETE (Tasks 1-6)
- **Phase 7.2 - Research & Specification**: 🔄 IN PROGRESS (Tasks 7-9)
- **Phase 7.3 - Unit Testing**: ⏳ PENDING (Tasks 10-17)
- **Phase 7.4 - Integration Testing**: ⏳ PENDING (Tasks 18-22)
- **Phase 7.5 - Quality Gates & SRE**: ⏳ PENDING (Tasks 23-28)
- **Phase 7.6 - AAR Generation**: ⏳ PENDING (Tasks 29-31)
- **Phase 7.7 - Batch Migrations**: ⏳ PENDING (Tasks 32-38)
- **Phase 7.8 - Error Handling & Enhancements**: ⏳ PENDING (Tasks 39-42)

**Delegation Model**:
- **Research Subagent Tasks**: 7 tasks (NO FILE CREATION) - Tasks 7-9, 23, 25, 29, 32, 39, 41
- **Primary Implementation Tasks**: 35 tasks (FILE CREATION ALLOWED) - All remaining

**Critical Path**: Research → Unit Tests → Integration Tests → Regression → Quality Gates → AAR → Batch Migrations

---

**Document Status**: ACTIVE - Updated 2025-11-14 14:15 PST
