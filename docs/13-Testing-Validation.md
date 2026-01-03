# 13 – Testing & Validation

**Status**: Complete
**Version**: 2.0
**Authoritative Sources**: [QSE-FRAMEWORK-ANALYSIS.md](../projects/P-CFWORK-DOCUMENTATION/QSE-FRAMEWORK-ANALYSIS.md) | [docs/Codex/ContextForge Work Codex.md](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md)
**Last Updated**: 2025-11-11
**Related**: [01-Overview](01-Overview.md) | [03-Context-Ontology-Framework](03-Context-Ontology-Framework.md) | [09-Development-Guidelines](09-Development-Guidelines.md)

---

## Table of Contents

1. [Introduction](#introduction)
2. [QSE Framework Overview](#qse-framework-overview)
3. [UTMW Workflow](#utmw-workflow-5-phases)
4. [Coverage Standards](#coverage-standards)
5. [Test Infrastructure](#test-infrastructure)
6. [Pytest Marker System](#pytest-marker-system)
7. [Quality Gates](#quality-gates-github-actions)
8. [Constitutional Validation](#constitutional-validation)
9. [Evidence Bundles](#evidence-bundles)
10. [Testing Anti-Patterns](#testing-anti-patterns)
11. [Quick Start](#quick-start)
12. [See Also](#see-also)

---

## Introduction

The **Quality Software Engineering (QSE) Framework** is ContextForge's evidence-based quality methodology, implementing comprehensive quality gates, test infrastructure, and Constitutional validation.

### Philosophy

From the [Work Codex](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md):

> **"Trust Nothing, Verify Everything"** - Evidence is the closing loop of trust. Logs and tests ground belief.
>
> **"Testing is validation across dimensions"** - Unit, integration, system, acceptance tests prove quality.

### Key Features

- **UTMW Workflow**: 5-phase quality process (Understand → Trust → Measure → Validate → Work)
- **COF 13-Dimensional Testing**: Quality assessment across all context dimensions
- **Constitutional Validation**: UCL/COF compliance automated checks
- **Evidence-Based**: SHA-256 cryptographic hashing, JSONL evidence bundles
- **CI/CD Integration**: 18 GitHub Actions workflows (7 blocking, 11 advisory)

### Current Status (2025-11-11)

- **Documentation Quality**: 9.3/10 (Excellent)
- **Test Infrastructure**: 428 test files, 2,226 tests
- **Test Collection**: 95.8% success (93 errors cataloged)
- **Branch Coverage**: 0.4% (target: 70% - critical gap)
- **Pytest Markers**: 283 defined (44 actively used)
- **Quality Gates**: 18 GitHub Actions (all operational)

---

## QSE Framework Overview

QSE (Quality Software Engineering) is ContextForge's comprehensive quality methodology.

### Core Principles

1. **Evidence First** - All quality claims backed by automated tests and metrics
2. **Focused Coverage** - 35% strategic coverage of critical paths (not 100%)
3. **Constitutional Compliance** - Automated UCL/COF validation
4. **Continuous Validation** - Quality gates enforce standards at every commit
5. **Dimensional Quality** - Testing across COF 13 dimensions

### Architecture

```
QSE Framework Architecture

┌─────────────────────────────────────────────────────────────┐
│                    UTMW Workflow Engine                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Test Pyramid │  │ Quality Gates│  │ Constitutional│
│              │  │              │  │  Validation  │
│ - Unit       │  │ - Blocking   │  │              │
│ - Integration│  │ - Advisory   │  │ - UCL        │
│ - System     │  │ - Evidence   │  │ - COF 13D    │
│ - Acceptance │  │              │  │ - Sacred Geo │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                          ▼
                  ┌──────────────┐
                  │ Evidence     │
                  │ Bundles      │
                  │ (JSONL+SHA)  │
                  └──────────────┘
```

---

## UTMW Workflow (5 Phases)

**UTMW** = Understand → Trust → Measure → Validate → Work

### Phase 0: UNDERSTAND

**Goal**: Gather context and define quality success criteria

**Activities**:
- COF 13-dimensional analysis of feature/component
- Identify quality characteristics (ISO 25010)
- Define Definition of Done (DoD)
- Create quality acceptance criteria

**Outputs**:
- Quality plan document
- DoD checklist
- Risk assessment

**Example**:
```yaml
# Quality Plan: JWT Authentication (P0-005)
feature: jwt_authentication
quality_dimensions:
  motivational: "Secure user authentication"
  relational: "Depends on Auth0 integration"
  validation: "100% auth paths covered"
success_criteria:
  - JWT validation test suite passing
  - Security scan (Bandit) clean
  - API contract tests passing
  - Constitutional validation passing
```

---

### Phase 1: TRUST

**Goal**: Establish baseline trust and validate assumptions

**Activities**:
- Create test fixtures and mocks
- Establish test data baseline
- Validate external dependencies
- Document trust assumptions

**Outputs**:
- Test fixtures (`tests/fixtures/`)
- Mock services
- Assumption documentation

**Example**:
```python
# tests/fixtures/auth_fixtures.py
import pytest
from jose import jwt

@pytest.fixture
def valid_jwt_token():
    """Trusted JWT token for testing"""
    payload = {"sub": "user123", "exp": 9999999999}
    return jwt.encode(payload, "test_secret", algorithm="HS256")

@pytest.fixture
def mock_auth0_client():
    """Trusted mock Auth0 client"""
    class MockAuth0:
        def validate_token(self, token):
            return {"valid": True, "sub": "user123"}
    return MockAuth0()
```

---

### Phase 2: MEASURE

**Goal**: Collect quantitative quality metrics

**Activities**:
- Instrument code with telemetry
- Run test suites with coverage
- Collect performance metrics
- Track quality indicators

**Outputs**:
- Coverage reports (HTML, JSON)
- Performance benchmarks
- Quality metrics dashboard

**Metrics Collected**:
- **Line Coverage**: % of code lines executed
- **Branch Coverage**: % of decision branches taken
- **Mutation Coverage**: % of mutants killed
- **Performance**: Request latency, throughput
- **Complexity**: Cyclomatic complexity, maintainability index

**Example**:
```bash
# Run pytest with coverage
pytest --cov=cf_core \
       --cov-report=html \
       --cov-report=json \
       --cov-branch

# Generate coverage report
coverage report --show-missing
```

---

### Phase 3: VALIDATE

**Goal**: Run quality gates and verify compliance

**Activities**:
- Execute test suites (unit, integration, E2E)
- Run quality gates (type check, lint, security)
- Verify Constitutional compliance (UCL/COF)
- Generate evidence bundles

**Outputs**:
- Test results (JUnit XML)
- Quality gate status
- Constitutional validation report
- Evidence bundle (JSONL + SHA-256)

**Quality Gates**:
1. **Unit Tests**: ≥70% passing
2. **Type Check**: mypy strict mode clean
3. **Lint**: ruff PEP 8 compliance
4. **Security**: Bandit scan clean
5. **Constitutional**: UCL/COF validation passing

**Example**:
```bash
# Run full validation suite
pytest -m quality_gate --junitxml=results.xml

# Type check
mypy cf_core/ --strict

# Lint
ruff check .

# Security scan
bandit -r cf_core/

# Constitutional validation
pytest -m constitution
```

---

### Phase 4: WORK

**Goal**: Implement features with quality-first mindset

**Activities**:
- Test-Driven Development (TDD) where applicable
- Continuous validation during implementation
- Evidence collection at each step
- Iterative improvement

**Practices**:
- Write tests before implementation (TDD)
- Run quality gates locally before commit
- Update evidence bundles with each change
- Retrospective after completion

**Example Workflow**:
```bash
# 1. Write failing test
pytest tests/test_jwt_auth.py::test_valid_token_authentication
# FAIL - not implemented

# 2. Implement feature
# (write code in cf_core/auth/jwt_validator.py)

# 3. Run test again
pytest tests/test_jwt_auth.py::test_valid_token_authentication
# PASS

# 4. Run quality gates
pytest -m quality_gate && mypy cf_core/ && ruff check .
# ALL PASS

# 5. Commit with evidence
git add . && git commit -m "feat(auth): implement JWT validation"
```

---

## Coverage Standards

### Codex Coverage Targets (Addendum C)

From the [Work Codex](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md):

| Layer | Baseline Minimum | Aspirational | Notes |
|-------|------------------|-------------|-------|
| **Unit** | 70% | 80%+ | Python core logic trending upward post-refactor |
| **Integration** | 40% | 55% | Focus: DB mutation round-trips |
| **System** | 25% | 35% | End-to-end CLI workflows |
| **Acceptance** | 15% | 25% | Narrative user journeys |
| **Logging (path coverage)** | 90% | 95% | Count distinct code paths logging |

**Current Status** (2025-11-11):
- **Unit**: ~60% (below baseline, improving)
- **Integration**: ~35% (below baseline)
- **System**: ~20% (below baseline)
- **Acceptance**: ~10% (below baseline)
- **Branch Coverage**: 0.4% (critical gap vs 70% target)

### Focused Core Coverage Philosophy

**NOT aiming for 100% coverage** - inefficient use of resources

**Focus Areas** (35% strategic coverage):
1. **Domain Logic** (cf_core entities, services) - 85% target
2. **API Endpoints** (TaskMan-v2 FastAPI) - 80% target
3. **Data Integrity** (repositories, migrations) - 75% target
4. **Security** (auth, validation) - 90% target

**Acceptable Exclusions**:
- UI styling and CSS
- Boilerplate and scaffolding
- Deprecated code paths
- Third-party library wrappers (thin)
- Generated code (protobuf, OpenAPI)

### Test Pyramid Structure

```
Test Pyramid (2,226 Total Tests)

            ┌─────────┐
            │   E2E   │ 5% (113 tests)
            │  Tests  │ Slowest, most expensive
            └─────────┘
          ┌─────────────┐
          │  Integration │ 20% (445 tests)
          │    Tests     │ Multi-component
          └─────────────┘
       ┌──────────────────┐
       │   System Tests   │ 25% (557 tests)
       │  (CLI workflows) │ Full stack
       └──────────────────┘
    ┌────────────────────────┐
    │      Unit Tests        │ 50% (1,113 tests)
    │   (Isolated logic)     │ Fast, focused
    └────────────────────────┘
```

**Rationale**: More unit tests (fast, cheap) than E2E tests (slow, expensive)

---

## Test Infrastructure

### Test Directory Organization

```
tests/
├── unit/                    # 1,113 tests - Isolated logic
│   ├── domain/             # Domain entities (DDD)
│   ├── repositories/       # Data access patterns
│   ├── services/           # Business logic
│   └── utils/              # Utility functions
│
├── integration/             # 445 tests - Multi-component
│   ├── api/                # FastAPI endpoint tests
│   ├── database/           # Repository integration
│   └── mcp/                # MCP server integration
│
├── system/                  # 557 tests - Full stack
│   ├── cli/                # dbcli, cf_cli, tasks_cli
│   └── workflows/          # End-to-end workflows
│
├── e2e/                     # 113 tests - User journeys
│   ├── task_creation/      # Task creation flow
│   ├── sprint_planning/    # Sprint planning flow
│   └── velocity_tracking/  # Velocity tracking flow
│
├── performance/             # 20 tests - Benchmarks
│   ├── api_latency/        # API response time
│   └── query_performance/  # Database query speed
│
├── security/                # 10 tests - Security validation
│   ├── auth/               # Authentication tests
│   └── injection/          # SQL injection tests
│
├── constitutional/          # 5 tests - UCL/COF compliance
│   ├── ucl_validation/     # UCL law enforcement
│   └── cof_validation/     # COF 13D completeness
│
└── fixtures/               # 43 files - Shared test data
    ├── auth_fixtures.py
    ├── task_fixtures.py
    └── sprint_fixtures.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific layer
pytest tests/unit/
pytest tests/integration/
pytest tests/system/
pytest tests/e2e/

# Run with coverage
pytest --cov=cf_core --cov-report=html

# Run specific marker
pytest -m unit
pytest -m integration
pytest -m slow
pytest -m quality_gate

# Run specific test
pytest tests/unit/domain/test_sprint_entity.py::test_create_sprint

# Run in parallel (faster)
pytest -n auto
```

---

## Pytest Marker System

### Marker Categories (283 Defined, 44 Active)

#### ISTQB Compliance (50 markers)

Standard test level markers:

```python
@pytest.mark.unit              # Isolated logic tests
@pytest.mark.integration       # Multi-component tests
@pytest.mark.system            # Full stack tests
@pytest.mark.acceptance        # User acceptance tests
```

#### ISO 25010 Quality Characteristics (45 markers)

```python
@pytest.mark.functional_suitability    # Feature completeness
@pytest.mark.performance_efficiency    # Speed and resource usage
@pytest.mark.compatibility             # Interoperability
@pytest.mark.usability                 # User experience
@pytest.mark.reliability               # Availability and fault tolerance
@pytest.mark.security                  # Authentication, authorization
@pytest.mark.maintainability           # Modifiability
@pytest.mark.portability               # Adaptability
```

#### Constitutional Validation (38 markers)

```python
@pytest.mark.constitution_ucl1         # UCL Law 1: No orphans
@pytest.mark.constitution_ucl2         # UCL Law 2: No cycles
@pytest.mark.constitution_ucl3         # UCL Law 3: Evidence required
@pytest.mark.constitution_cof_motivational    # COF Dimension 1
@pytest.mark.constitution_cof_relational      # COF Dimension 2
# ... (36 more)
```

#### Component-Specific (44 markers)

```python
@pytest.mark.taskman              # TaskMan-v2 tests
@pytest.mark.velocity_tracker     # Velocity tracker tests
@pytest.mark.qse                  # QSE framework tests
@pytest.mark.cf_core              # cf_core domain tests
@pytest.mark.spectre              # ContextForge.Spectre tests
```

#### Custom Markers (106 markers)

```python
@pytest.mark.slow                 # Tests taking >5s
@pytest.mark.requires_db          # Database required
@pytest.mark.requires_network     # Network access needed
@pytest.mark.requires_auth        # Authentication required
@pytest.mark.quality_gate         # Quality gate enforcement
```

### Marker Consolidation (P1-006)

**Issue**: 84% of markers unused (239 of 283)

**Planned Action** (P1-006, deferred):
- Audit all 283 markers
- Remove 239 unused markers
- Document marker usage strategy
- Update pyproject.toml

---

## Quality Gates (GitHub Actions)

### Blocking Workflows (7)

These workflows **MUST PASS** before PR merge:

#### 1. constitution-validation.yml

**Purpose**: UCL/COF compliance validation

**Checks**:
- ✅ All contexts anchored (no orphans)
- ✅ No cycles or deadlocks
- ✅ Evidence bundles present

**Command**: `pytest -m constitution`

---

#### 2. pytest-core.yml

**Purpose**: Core test suite must pass

**Checks**:
- ✅ Unit tests passing
- ✅ Integration tests passing
- ✅ System tests passing

**Command**: `pytest -m "not slow"`

---

#### 3. type-check.yml

**Purpose**: Static type checking with mypy

**Checks**:
- ✅ No type errors
- ✅ Strict mode compliance
- ✅ Type coverage >90%

**Command**: `mypy cf_core/ --strict`

---

#### 4. lint-check.yml

**Purpose**: Code quality and PEP 8 compliance

**Checks**:
- ✅ ruff linting clean
- ✅ PEP 8 compliance
- ✅ Import sorting (isort)

**Command**: `ruff check . && isort --check .`

---

#### 5. security-scan.yml

**Purpose**: Security vulnerability detection

**Checks**:
- ✅ Bandit security scan clean
- ✅ No SQL injection vulnerabilities
- ✅ No hardcoded secrets

**Command**: `bandit -r cf_core/`

---

#### 6. migration-check.yml

**Purpose**: Database migration validation

**Checks**:
- ✅ Alembic migrations valid
- ✅ Migration reversibility
- ✅ Schema consistency

**Command**: `alembic check && alembic upgrade head && alembic downgrade -1`

---

#### 7. contract-test.yml

**Purpose**: API contract testing (Pact)

**Checks**:
- ✅ API contracts valid
- ✅ Provider verification
- ✅ Consumer compatibility

**Command**: `pytest -m contract_test`

---

### Advisory Workflows (11)

These workflows **report but don't block** (informational):

1. **coverage-report.yml** - Code coverage metrics
2. **performance-benchmark.yml** - Regression detection
3. **dependency-check.yml** - Outdated dependencies
4. **documentation-lint.yml** - Markdown validation
5. **accessibility-test.yml** - WCAG 2.1 AA compliance
6. **bundle-size.yml** - Frontend bundle size tracking
7. **e2e-tests.yml** - Full workflow validation
8. **mutation-testing.yml** - Test quality assessment
9. **license-check.yml** - License compliance
10. **changelog-check.yml** - CHANGELOG.md updated
11. **broken-links.yml** - Documentation link validation

---

## Constitutional Validation

### UCL Enforcement Tests

**Universal Context Law (UCL)**: "No orphaned, cyclical, or incomplete context may persist"

```python
# tests/constitutional/test_ucl_validation.py

@pytest.mark.constitution_ucl1
def test_no_orphaned_contexts(db_session):
    """UCL Law 1: All contexts must be anchored"""
    orphans = db_session.query(Context).filter(
        Context.parent_id == None
    ).all()

    assert len(orphans) == 0, f"Found {len(orphans)} orphaned contexts"

@pytest.mark.constitution_ucl2
def test_no_cyclical_contexts(db_session):
    """UCL Law 2: No cycles in context graph"""
    contexts = db_session.query(Context).all()

    for context in contexts:
        visited = set()
        current = context

        while current:
            if current.id in visited:
                pytest.fail(f"Cycle detected: {current.id}")

            visited.add(current.id)
            current = current.parent

@pytest.mark.constitution_ucl3
def test_evidence_bundles_present(db_session):
    """UCL Law 3: All contexts must have evidence"""
    incomplete = db_session.query(Context).filter(
        Context.evidence_bundle_hash == None
    ).all()

    assert len(incomplete) == 0, f"{len(incomplete)} contexts missing evidence"
```

### COF 13D Validation Tests

```python
# tests/constitutional/test_cof_validation.py

@pytest.mark.constitution_cof_completeness
def test_cof_13_dimensions_complete(task_context):
    """All 13 COF dimensions must be addressed"""
    required_dimensions = [
        'motivational', 'relational', 'dimensional', 'situational',
        'resource', 'narrative', 'recursive', 'sacred_geometry',
        'computational', 'emergent', 'temporal', 'spatial', 'holistic'
    ]

    missing = [d for d in required_dimensions if d not in task_context]

    assert len(missing) == 0, f"Missing dimensions: {missing}"
```

---

## Evidence Bundles

### Structure

Evidence bundles are **JSONL files** with **SHA-256 cryptographic hashing** using **canonical serialization** (RFC 8785).

> **📋 Serialization Standard**: All evidence bundles MUST use the [Output Manager](output-manager/serialization-spec.md) for deterministic JSON serialization to ensure hash stability across systems.

```json
{
  "timestamp": "2025-11-11T18:30:00Z",
  "event": "test_execution",
  "test_suite": "unit",
  "results": {
    "passed": 1050,
    "failed": 5,
    "skipped": 58,
    "total": 1113
  },
  "coverage": {
    "line": 60.2,
    "branch": 0.4
  },
  "evidence_hash": "sha256:abc123def456...",
  "quality_gate": "PASS"
}
```

### Canonical Serialization (RFC 8785)

Evidence hashes MUST be generated from **canonical JSON** to ensure:
- **Reproducibility**: Same data → same hash across all systems
- **Verification**: Evidence can be independently verified
- **Integrity**: Tamper detection via hash comparison

**Implementation** (using Output Manager):
```python
from python.output_manager import OutputManager

def generate_evidence_hash(test_results: dict) -> str:
    """Generate SHA-256 hash of test results using canonical serialization."""
    return OutputManager.hash_evidence(test_results)
```

**Legacy Pattern** (Deprecated - migrate to Output Manager):
```python
# ⚠️ DEPRECATED - Does not guarantee cross-platform consistency
import hashlib
import json

def generate_evidence_hash_legacy(test_results: dict) -> str:
    canonical = json.dumps(test_results, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()
```

---

## Testing Anti-Patterns

From the [Work Codex](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md):

### Anti-Pattern: Skipping Tests to Save Time

**Problem**: "We'll add tests later" leads to technical debt

**Solution**: TDD - write tests first, implementation second

---

### Anti-Pattern: Testing Implementation, Not Behavior

**Problem**: Tests break when refactoring, even if behavior unchanged

**Solution**: Test public interfaces and behaviors, not internal implementation

---

### Anti-Pattern: Over-Mocking

**Problem**: Tests pass but production fails due to mock inaccuracy

**Solution**: Use integration tests with real dependencies where practical

---

### Anti-Pattern: Flaky Tests

**Problem**: Tests fail randomly, eroding trust in test suite

**Solution**: Eliminate non-determinism (time, randomness, network)

---

## Quick Start

### 1. Run All Tests

```bash
pytest
```

### 2. Run Quality Gates Locally

```bash
pytest -m quality_gate && mypy cf_core/ && ruff check . && bandit -r cf_core/
```

### 3. Check Coverage

```bash
pytest --cov=cf_core --cov-report=html
open htmlcov/index.html  # View coverage report
```

### 4. Run Constitutional Validation

```bash
pytest -m constitution
```

### 5. Run Specific Test Layer

```bash
pytest tests/unit/          # Fast, focused
pytest tests/integration/   # Multi-component
pytest tests/system/        # Full stack
pytest tests/e2e/           # User journeys
```

---

## See Also

### Foundation Documents

- [01-Overview.md](01-Overview.md) - System overview with quality principles
- [03-Context-Ontology-Framework.md](03-Context-Ontology-Framework.md) - COF 13D + UCL definitions
- [09-Development-Guidelines.md](09-Development-Guidelines.md) - Development practices

### Authoritative Reference

- [docs/Codex/ContextForge Work Codex.md](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md) - **PRIMARY SOURCE** for coverage standards (Addendum C)
- [projects/P-CFWORK-DOCUMENTATION/QSE-FRAMEWORK-ANALYSIS.md](../projects/P-CFWORK-DOCUMENTATION/QSE-FRAMEWORK-ANALYSIS.md) - Complete QSE analysis (618 lines)

### Implementation Details

- [projects/P-CFWORK-DOCUMENTATION/TEST-COLLECTION-ERROR-CATALOG.md](../projects/P-CFWORK-DOCUMENTATION/TEST-COLLECTION-ERROR-CATALOG.md) - Test collection errors (473 lines)
- [.github/workflows/](../.github/workflows/) - CI/CD workflows (18 files)

---

**Document Status**: Complete ✅
**Authoritative**: Yes (sourced from QSE-FRAMEWORK-ANALYSIS.md + Codex)
**Next Review**: 2026-02-11 (quarterly)
**Maintained By**: ContextForge Quality Team

---

*"Trust Nothing, Verify Everything. Evidence is the closing loop of trust."*

*"Testing is validation across dimensions: unit, integration, system, acceptance."*
