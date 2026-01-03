# Quantum Sync Engine (QSE) & Universal Task Management Workflow (UTMW)

## Complete Technical Reference

**Version**: 3.0 (Quantum Persona Team Synthesis)
**Date**: 2025-12-06
**Status**: Authoritative Reference Document
**Authors**: Quantum Persona Research Team

---

## Executive Summary

The **Quantum Sync Engine (QSE)** and **Universal Task Management Workflow (UTMW)** form the foundational quality assurance and task orchestration framework within ContextForge Work. Together, they implement a comprehensive evidence-based quality methodology that ensures all work is traceable, validated, and aligned with organizational goals through 13-dimensional context analysis and Sacred Geometry validation patterns.

### Core Value Proposition

| Framework | Purpose | Key Benefit |
|-----------|---------|-------------|
| **QSE** | Quality Software Engineering methodology | Evidence-based quality gates with Constitutional validation |
| **UTMW** | Universal Task Management Workflow | 5-phase structured approach ensuring complete context capture |

---

## Part I: Quantum Sync Engine (QSE)

### 1.1 QSE Foundation

The Quantum Sync Engine is ContextForge's comprehensive quality methodology implementing:

- **Evidence-First Engineering**: All quality claims backed by automated tests and metrics
- **Focused Coverage**: 35% strategic coverage of critical paths (not 100%)
- **Constitutional Compliance**: Automated UCL/COF validation
- **Continuous Validation**: Quality gates enforce standards at every commit
- **Dimensional Quality**: Testing across COF 13 dimensions

### 1.2 QSE Core Principles

From the ContextForge Work Codex:

> **"Trust Nothing, Verify Everything"** - Evidence is the closing loop of trust. Logs and tests ground belief.
>
> **"Testing is validation across dimensions"** - Unit, integration, system, acceptance tests prove quality.

### 1.3 QSE Architecture

```
QSE Framework Architecture

┌─────────────────────────────────────────────────────────────┐
│                    UTMW Workflow Engine                      │
│        (Understand → Trust → Measure → Validate → Work)      │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Test Pyramid │  │ Quality Gates│  │ Constitutional│
│              │  │              │  │  Validation  │
│ - Unit (50%) │  │ - Blocking   │  │              │
│ - Integration│  │   (7 gates)  │  │ - UCL Laws   │
│   (20%)      │  │ - Advisory   │  │ - COF 13D    │
│ - System     │  │   (11 gates) │  │ - Sacred Geo │
│   (25%)      │  │ - Evidence   │  │   Patterns   │
│ - E2E (5%)   │  │   Bundles    │  │              │
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

### 1.4 Test Pyramid Structure

QSE implements a balanced test pyramid optimized for efficiency:

```
Test Pyramid (2,226+ Total Tests)

            ┌─────────┐
            │   E2E   │ 5% (~113 tests)
            │  Tests  │ Slowest, most expensive
            └─────────┘
          ┌─────────────┐
          │  Integration │ 20% (~445 tests)
          │    Tests     │ Multi-component
          └─────────────┘
       ┌──────────────────┐
       │   System Tests   │ 25% (~557 tests)
       │  (CLI workflows) │ Full stack
       └──────────────────┘
    ┌────────────────────────┐
    │      Unit Tests        │ 50% (~1,113 tests)
    │   (Isolated logic)     │ Fast, focused
    └────────────────────────┘
```

**Coverage Targets (Codex Addendum C)**:

| Layer | Baseline Minimum | Aspirational | Notes |
|-------|------------------|-------------|-------|
| **Unit** | 70% | 80%+ | Python core logic |
| **Integration** | 40% | 55% | DB mutation round-trips |
| **System** | 25% | 35% | End-to-end CLI workflows |
| **Acceptance** | 15% | 25% | Narrative user journeys |
| **Logging** | 90% | 95% | Count distinct code paths |

### 1.5 Quality Gates

#### Blocking Workflows (7 Gates)

These workflows **MUST PASS** before PR merge:

| Gate | Purpose | Command |
|------|---------|---------|
| **constitution-validation** | UCL/COF compliance | `pytest -m constitution` |
| **pytest-core** | Core test suite | `pytest -m "not slow"` |
| **type-check** | mypy strict mode | `mypy cf_core/ --strict` |
| **lint-check** | PEP 8 compliance | `ruff check . && isort --check .` |
| **security-scan** | Vulnerability detection | `bandit -r cf_core/` |
| **migration-check** | Database migration validity | `alembic check` |
| **contract-test** | API contract validation | `pytest -m contract_test` |

#### Advisory Workflows (11 Gates)

These provide informational reports:

1. coverage-report
2. performance-benchmark
3. dependency-check
4. documentation-lint
5. accessibility-test
6. bundle-size
7. e2e-tests
8. mutation-testing
9. license-check
10. changelog-check
11. broken-links

### 1.6 Pytest Marker System

QSE defines **283 markers** across categories:

#### ISTQB Compliance (50 markers)
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
@pytest.mark.reliability               # Availability and fault tolerance
@pytest.mark.security                  # Authentication, authorization
@pytest.mark.maintainability           # Modifiability
```

#### Constitutional Validation (38 markers)
```python
@pytest.mark.constitution_ucl1         # No orphans
@pytest.mark.constitution_ucl2         # No cycles
@pytest.mark.constitution_ucl3         # Evidence required
@pytest.mark.constitution_cof_*        # COF Dimensions
```

### 1.7 Evidence Bundles

QSE generates cryptographically-verified evidence bundles:

```json
{
  "timestamp": "2025-12-06T18:30:00Z",
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

**Evidence Bundle Structure**:
```
.QSE/v2/Evidence/{projectId}/{sessionId}/
├── evidence-bundle-{timestamp}.jsonl
├── artifacts/
│   ├── ExecutionPlan-001.yaml
│   └── TestResults-001.json
└── logs/
    └── session-log-{timestamp}.yaml
```

---

## Part II: Universal Task Management Workflow (UTMW)

### 2.1 UTMW Foundation

**UTMW** = **U**nderstand → **T**rust → **M**easure → **V**alidate → **W**ork

The Universal Task Management Workflow provides a 5-phase structured approach that ensures:
- Complete context capture across 13 COF dimensions
- Sacred Geometry pattern alignment
- UCL compliance at every stage
- Evidence generation for all work

### 2.2 UTMW Phase Overview

```
UTMW Workflow Flow

┌─────────────────────────────────────────────────────────────┐
│  Phase 0: Session Foundation (MANDATORY)                    │
│  - Constitution check (every prompt)                        │
│  - COF context loading                                      │
│  - Project summary header                                   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: UNDERSTAND (Dimensional Scoping)                  │
│  - COF 13D analysis (≥200 words per dimension)             │
│  - Strategic vibe_check                                     │
│  - Scope documentation                                      │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: TRUST (Evidence Research)                         │
│  - Agent memory query                                       │
│  - Pattern identification                                   │
│  - Research documentation                                   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: MEASURE (Sacred Planning)                         │
│  - Branched thinking for alternatives                       │
│  - Plan generation with COF + Sacred Geometry              │
│  - MCP tool selection                                       │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: VALIDATE (Resonance Validation)                   │
│  - COF completeness validation                              │
│  - Sacred Geometry pattern validation                       │
│  - UCL compliance audit                                     │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 5: WORK (Resonant Execution)                         │
│  - Implementation with evidence generation                  │
│  - PAOAL cycles (Plan→Act→Observe→Adapt→Log)               │
│  - Quality gate enforcement                                 │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 6: REFLECT (Sacred Reflection)                       │
│  - After Action Report (AAR)                               │
│  - Agent memory storage                                     │
│  - Lessons learned capture                                  │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Detailed Phase Descriptions

#### Phase 0: Session Foundation (MANDATORY)

**Execute FIRST, before any action:**

```
Constitution Check Protocol:
1. Use vibe-check-mcp/constitution_check tool
2. Validate session ID matches project ID
3. Synchronize context if misaligned
4. Log corrections to .QSE/evidence/
```

**Project Summary Header (Required)**:
```
**Active Project**: [P-PROJECT-001] - [Project Name]
**Phase**: [Current Phase] | **Session**: [YYYY-MM-DDTHH:MM:SSZ]
**MCP Transport**: [STDIO] | **CF_CLI**: [Available]
**COF Dimensions**: [Baseline loaded] | **Sacred Geometry**: [Validation ready]
```

#### Phase 1: UNDERSTAND (Dimensional Scoping)

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

#### Phase 2: TRUST (Evidence Research)

**Goal**: Establish baseline trust and validate assumptions

**Activities**:
- Create test fixtures and mocks
- Establish test data baseline
- Validate external dependencies
- Query agent memory for historical context

**Outputs**:
- Test fixtures (`tests/fixtures/`)
- Mock services
- Assumption documentation

#### Phase 3: MEASURE (Sacred Planning)

**Goal**: Collect quantitative quality metrics and plan implementation

**Activities**:
- Instrument code with telemetry
- Run test suites with coverage
- Use branched thinking for alternatives
- Apply Golden Ratio prioritization

**Outputs**:
- Coverage reports
- Performance benchmarks
- Execution plan with COF tags

#### Phase 4: VALIDATE (Resonance Validation)

**Goal**: Run quality gates and verify compliance

**Activities**:
- Execute all test suites
- Run quality gates (type check, lint, security)
- Verify Constitutional compliance (UCL/COF)
- Validate Sacred Geometry patterns

**Validation Checks**:
```yaml
cof_validation:
  dimensions_addressed: 13/13
  depth_quality: "≥200 words per dimension"

sacred_geometry_validation:
  circle: "Completeness check passed"
  triangle: "Three-point stability verified"
  spiral: "Learning capture confirmed"
  golden_ratio: "Resource balance justified"
  fractal: "Pattern consistency validated"
  gates_passed: "5/5 REQUIRED"

ucl_compliance:
  no_orphans: true
  no_cycles: true
  evidence_complete: true
```

#### Phase 5: WORK (Resonant Execution)

**Goal**: Implement features with evidence generation

**PAOAL Cycle**:
```
Plan → Act → Observe → Adapt → Log

1. PLAN: Define action with COF dimension awareness
2. ACT: Execute with Workspace First + Logs First principles
3. OBSERVE: Collect evidence to .QSE/ with COF tags
4. ADAPT: Adjust based on sacred geometry alignment
5. LOG: Update .QSE/ and TaskMan with COF learning
```

**Evidence Generation Per Task**:
```yaml
implementation_evidence:
  changes:
    - path: "relative/path/to/file"
      change: added|modified|removed
      summary: "Description with COF context"
  tools_used:
    - tool: "mcp:SeqThinking/sequential_thinking"
      purpose: "COF-guided planning"
  validation:
    tests: "passed"
    quality_gates: "all passed"
    sacred_geometry_gates: "5/5"
```

#### Phase 6: REFLECT (Sacred Reflection)

**Goal**: Capture lessons and store insights

**After Action Report (AAR) Structure**:
```yaml
aar:
  what_accomplished: "With COF dimension breakdown"
  what_went_well: "With sacred geometry alignment evidence"
  what_to_improve: "COF gaps, pattern misalignments"
  lessons_learned: "Specific, actionable, COF-tagged"
  recommendations: "UCL-compliant future work"
```

---

## Part III: Context Ontology Framework (COF) Integration

### 3.1 The 13 Dimensions of Context

Every context in ContextForge MUST be analyzed across **13 dimensions**:

| # | Dimension | Focus | Application |
|---|-----------|-------|-------------|
| 1 | **Motivational** | Purpose, goals, driving forces | Business alignment |
| 2 | **Relational** | Dependencies, cross-links | Integration planning |
| 3 | **Dimensional** | Scope, depth, integration | Impact analysis |
| 4 | **Situational** | Environment, constraints | Risk assessment |
| 5 | **Resource** | People, tools, budget | Capacity planning |
| 6 | **Narrative** | User journey, business case | Stakeholder communication |
| 7 | **Recursive** | Feedback loops, iteration | Continuous improvement |
| 8 | **Sacred Geometry** | Pattern alignment | Validation structure |
| 9 | **Computational** | Algorithms, data models | Technical architecture |
| 10 | **Emergent** | Unexpected outcomes | Innovation capture |
| 11 | **Temporal** | Deadlines, sequencing | Project management |
| 12 | **Spatial** | Team distribution, topology | Coordination planning |
| 13 | **Holistic** | System-wide synthesis | Coherence validation |

### 3.2 COF 13D Analysis Template

```yaml
cof_dimensional_analysis:

  1_motivational_context:
    business_driver: "Why this work matters to organization"
    success_criteria: "How we measure achievement"
    stakeholder_value: "Who benefits and how"
    priority_justification: "Business priority with evidence"

  2_relational_context:
    dependencies: "What this work depends on"
    influences: "What this work affects"
    connections: "Integration points"
    ucl_parent_linkage: "Parent project (orphan prevention)"

  3_dimensional_context:
    scope: "Breadth of impact"
    depth: "Technical complexity"
    integration: "Cross-team coordination"

  4_situational_context:
    environment: "Current state"
    constraints: "Limitations"
    opportunities: "Favorable conditions"
    market_timing: "External factors"

  5_resource_context:
    human_resources: "People, skills, FTE"
    technical_resources: "Tools, infrastructure"
    temporal_resources: "Time allocation"
    budget_allocation: "Financial constraints"

  6_narrative_context:
    user_journey: "End-user experience"
    stakeholder_story: "Business perspective"
    technical_narrative: "Implementation story"
    business_case: "ROI and value"

  7_recursive_context:
    feedback_loops: "How results inform iterations"
    improvement_cycles: "Enhancement mechanisms"
    learning_capture: "Knowledge retention"
    retrospective_plan: "AAR strategy"

  8_sacred_geometry_context:
    circle_completeness: "Full cycle coverage"
    triangle_stability: "Three-point validation"
    spiral_progression: "Learning integration"
    golden_ratio_balance: "Resource optimization"
    fractal_consistency: "Pattern coherence"

  9_computational_context:
    algorithms: "Processing logic"
    data_models: "Information structure"
    performance: "Efficiency targets"
    technical_architecture: "Design patterns"

  10_emergent_context:
    unexpected_outcomes: "Novel discoveries"
    serendipitous_benefits: "Unplanned impacts"
    adaptive_responses: "System evolution"
    innovation_potential: "Breakthrough possibilities"

  11_temporal_context:
    scheduling: "Timeline management"
    sequencing: "Dependency order"
    cadence: "Sprint cycle alignment"
    deadline_criticality: "Hard vs soft deadlines"

  12_spatial_context:
    distribution: "Geographic spread"
    topology: "Communication structure"
    boundaries: "Integration points"
    deployment_architecture: "Environment topology"

  13_holistic_context:
    synthesis: "Unified view across dimensions"
    coherence: "Internal consistency"
    completeness: "Coverage assessment"
    resonance: "Business/user/technical harmony"
```

---

## Part IV: Sacred Geometry Patterns

### 4.1 The Five Sacred Patterns

Every context MUST validate against these patterns:

#### 1. Circle (Completeness)

**Principle**: Work is complete when all dimensions are addressed and evidence is captured.

**Validation Criteria**:
- ✅ All 13 COF dimensions analyzed
- ✅ Evidence bundles present
- ✅ No orphaned contexts
- ✅ Workflow has defined start and clear closure
- ✅ .QSE/ artifacts committed

**Quality Gate**:
```yaml
circle_gate:
  requirement: "Complete cycle with closure and continuity"
  validation_method: "COF completeness check + UCL audit"
  evidence_required: "Full workflow documentation"
  failure_action: "Block progression, capture gaps via vibe_learn"
```

#### 2. Triangle (Stability)

**Principle**: Three-point foundation provides stability: Plan → Execute → Validate.

**Validation Criteria**:
- ✅ Planning documentation exists
- ✅ Execution tracked with logs
- ✅ Validation tests passing
- ✅ Business/user/technical perspectives addressed
- ✅ Stakeholder approval obtained

**Quality Gate**:
```yaml
triangle_gate:
  requirement: "Three-point stability and validation"
  validation_method: "QSE quality checks + stakeholder sign-off"
  evidence_required: "Test results + docs + approvals"
  failure_action: "Identify missing point, use branched_thinking"
```

#### 3. Spiral (Iteration)

**Principle**: Progress is iterative, with each cycle building on the previous.

**Validation Criteria**:
- ✅ Retrospectives conducted (AARs)
- ✅ Lessons captured in agent memory
- ✅ Velocity trends tracked and improving
- ✅ Each iteration builds on previous insights
- ✅ Learning integration documented

**Quality Gate**:
```yaml
spiral_gate:
  requirement: "Upward progression with learning integration"
  validation_method: "AAR analysis + agent memory + velocity trends"
  evidence_required: ".QSE/evidence/aar/*.yaml + memory_id references"
  failure_action: "Generate AAR, use vibe_learn to capture lessons"
```

#### 4. Golden Ratio (Balance)

**Principle**: Effort balanced with value; no over-engineering or under-engineering.

**The φ (Phi) Ratio**: 1.618 guides optimization prioritization:
- 20% of code paths → 80% of runtime (Pareto)
- Focus profiling on hot paths
- Apply φ ratio to effort allocation

**Validation Criteria**:
- ✅ Cost-benefit analysis documented
- ✅ Right-sized solution (not perfect)
- ✅ Technical debt managed
- ✅ Resource allocation follows natural proportions

**Quality Gate**:
```yaml
golden_ratio_gate:
  requirement: "Optimal balance and resource distribution"
  validation_method: "Resource optimization + ROI calculation"
  evidence_required: "Cost-benefit analysis + debt assessment"
  failure_action: "Adjust scope, use vibe_check for guidance"
```

#### 5. Fractal (Modularity)

**Principle**: Patterns repeat at different scales; components compose cleanly.

**Validation Criteria**:
- ✅ Modular architecture (DDD, Repository pattern)
- ✅ Reusable components
- ✅ Consistent patterns across scales (epic/feature/task)
- ✅ Composition principles followed

**Quality Gate**:
```yaml
fractal_gate:
  requirement: "Pattern consistency across all scales"
  validation_method: "Architecture review + pattern analysis"
  evidence_required: "Pattern documentation + scale consistency"
  failure_action: "Refactor for consistency, document deviations"
```

---

## Part V: Universal Context Law (UCL)

### 5.1 The Core Law

> **"No orphaned, cyclical, or incomplete context may persist in the system."**

### 5.2 Three UCL Requirements

#### UCL-1: No Orphans

**Every context must be anchored** to at least one parent project or initiative.

```sql
-- Orphan detection query
SELECT * FROM contexts
WHERE parent_id IS NULL
AND context_type != 'root_project';
```

**Resolution**: Link orphaned contexts to appropriate parent or archive if obsolete.

#### UCL-2: No Cycles

**Context relationships must flow toward resolution**, never creating circular dependencies.

```python
def detect_cycles(context_graph):
    visited = set()
    rec_stack = set()

    for node in context_graph.nodes():
        if detect_cycle_util(node, visited, rec_stack):
            return True  # Cycle detected
    return False
```

**Resolution**: Break circular dependencies by introducing intermediate contexts.

#### UCL-3: Complete Evidence

**Every context must carry evidence bundles** and logs—no unverifiable work.

```python
def validate_evidence_completeness(context_id):
    evidence = get_evidence_bundle(context_id)
    required_fields = ['correlation_id', 'hash', 'timestamp', 'artifacts', 'logs']
    return all(field in evidence for field in required_fields)
```

**Resolution**: Generate missing evidence bundles, create logs for untracked work.

### 5.3 Triple-Check Protocol

**Steps for UCL Enforcement**:
1. **Initial Build** - Construct with COF 13D analysis
2. **Logs-First Diagnostics** - Verify evidence capture
3. **Reproducibility/DoD Compliance** - Confirm Definition of Done met

---

## Part VI: MCP Tool Integration

### 6.1 Tool Selection by Phase

| Phase | MCP Tool | Purpose | Integration |
|-------|----------|---------|-------------|
| **Every Prompt** | `vibe-check-mcp/constitution_check` | Session integrity | UCL orphan prevention |
| **Phase Transitions** | `vibe-check-mcp/vibe_check` | Pattern interrupt | Sacred geometry alignment |
| **Complex Planning** | `SeqThinking/sequential_thinking` | PAOAL cycles | 13D synthesis |
| **Alternatives** | `SeqThinking/branched_thinking` | Explore approaches | Pattern comparison |
| **Failures** | `vibe-check-mcp/vibe_learn` | Capture lessons | Spiral learning |
| **Knowledge** | `digitarald.agent-memory/memory` | Persist insights | Recursive context |
| **Tasks** | TaskMan MCP | Track progress | 64-field schema |

### 6.2 MCP Transport Policy

**STDIO-first**: Prefer MCP over STDIO for assistant-driven operations inside VS Code.

**HTTP fallback**: Use only when STDIO is unavailable or remote service explicitly requires it.

**Health Check**:
```powershell
$resp = Invoke-RestMethod -Method GET -Uri "http://localhost:3001/api/health"
if ($null -eq $resp -or $resp.status -ne 'ok') {
    throw 'MCP server not ready'
}
```

---

## Part VII: .QSE Directory Structure

### 7.1 Complete .QSE Layout

```
projects/{projectName}/.QSE/
├── qse-config.yaml              # Configuration with COF + Sacred Geometry
├── quality-gates/               # Sacred Geometry gate definitions
│   ├── circle-completeness.yaml
│   ├── triangle-stability.yaml
│   ├── spiral-iteration.yaml
│   ├── golden-ratio-balance.yaml
│   └── fractal-consistency.yaml
├── cof-analyses/                # COF 13-dimensional analyses
│   ├── baseline-{workId}.yaml
│   ├── iteration-*.yaml
│   └── final-synthesis.yaml
├── sacred-geometry/             # Pattern validation records
│   ├── pattern-alignment-*.yaml
│   └── validation-reports/
├── test-results/                # Latest results (committed)
├── metrics/                     # Historical snapshots with COF tags
├── evidence/                    # Evidence bundles with COF + Sacred Geometry
│   ├── aar/                     # After Action Reports
│   │   └── AAR-*.yaml
│   └── implementation-*.yaml
├── reports/                     # Dashboards with metrics
└── docs/                        # Documentation
```

---

## Part VIII: Success Criteria

### 8.1 Workflow Complete Checklist

A workflow is COMPLETE when ALL conditions are met:

✅ **Session Integrity**: Constitution check on every prompt
✅ **COF Complete**: All 13 dimensions adequately addressed (≥200 words each)
✅ **Sacred Geometry**: All 5 patterns validated (minimum 3 of 5 passing)
✅ **UCL Compliant**: No orphaned, cyclical, or incomplete contexts
✅ **MCP Integration**: Strategic tools used at inflection points
✅ **Evidence Generation**: Complete .QSE/ artifacts committed with COF tags
✅ **Quality Gates**: All gates passed (including sacred geometry gates)
✅ **TaskMan Updated**: Complete task history with COF evidence
✅ **Agent Memory**: Lessons stored with COF and pattern tags
✅ **AAR Generated**: Reflection documented with COF synthesis
✅ **Resonance Achieved**: Business/user/technical harmony validated

### 8.2 Anti-Patterns to Avoid

❌ Skipping constitution_check
❌ Incomplete COF analysis (missing dimensions)
❌ Ignoring sacred geometry patterns
❌ Violating UCL (orphaned/cyclical contexts)
❌ Bypassing CF_CLI for domain workflows
❌ Failing without vibe_learn execution
❌ Missing .QSE/ artifact commits
❌ Superficial dimensional analysis (<200 words)
❌ Pattern inconsistency across scales

---

## Part IX: Quick Reference

### 9.1 UTMW Phase Summary

| Phase | Name | Duration | Key Output |
|-------|------|----------|------------|
| 0 | Session Foundation | 15-30 min | Context loaded, header displayed |
| 1 | UNDERSTAND | 30-90 min | COF 13D analysis, scope document |
| 2 | TRUST | 1-4 hours | Research documentation, patterns |
| 3 | MEASURE | 1-3 hours | Execution plan, benchmarks |
| 4 | VALIDATE | 30-90 min | All gates passed |
| 5 | WORK | Variable | Implementation complete |
| 6 | REFLECT | 30-90 min | AAR, lessons stored |

### 9.2 Sacred Geometry Quick Validation

```yaml
sacred_geometry_quick_check:
  circle: "Are all 13 COF dimensions complete?"
  triangle: "Is there Plan → Execute → Validate flow?"
  spiral: "Are lessons captured for next iteration?"
  golden_ratio: "Is effort balanced with value?"
  fractal: "Are patterns consistent across scales?"

minimum_passing: "3 of 5 patterns must pass"
recommended_passing: "5 of 5 patterns for critical work"
```

### 9.3 UCL Quick Validation

```yaml
ucl_quick_check:
  ucl1_no_orphans: "Every context has parent linkage"
  ucl2_no_cycles: "No circular dependencies"
  ucl3_evidence: "All work has evidence bundles"

compliance_required: "100% (no exceptions)"
```

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **AAR** | After Action Report - structured reflection document |
| **COF** | Context Ontology Framework - 13-dimensional analysis system |
| **PAOAL** | Plan → Act → Observe → Adapt → Log cycle |
| **QSE** | Quality Software Engineering - evidence-based quality methodology |
| **Sacred Geometry** | Five validation patterns (Circle, Triangle, Spiral, Golden Ratio, Fractal) |
| **UCL** | Universal Context Law - no orphaned, cyclical, or incomplete contexts |
| **UTMW** | Universal Task Management Workflow - 5-phase structured approach |

---

## Appendix B: Authority Sources

| Source | Path | Purpose |
|--------|------|---------|
| Work Codex | `docs/Codex/ContextForge Work Codex.md` | Core philosophies |
| COF Reference | `docs/03-Context-Ontology-Framework.md` | 13D definitions |
| Development Guidelines | `docs/09-Development-Guidelines.md` | Engineering standards |
| Testing Validation | `docs/13-Testing-Validation.md` | QSE framework |
| Optimization Standards | `docs/08-Optimization-Standards.md` | Performance patterns |
| QSM Workflow Instructions | `.github/instructions/QSM-Workflow.instructions.md` | Workflow protocol |
| QSM Implementation | `.github/instructions/QSM-task-plan-implementation.instructions.md` | Implementation guide |

---

**Document Status**: Complete ✅
**Synthesized By**: Quantum Persona Research Team
**Authority**: ContextForge Work Codex + COF + Sacred Geometry + UCL
**Version**: 3.0 (2025-12-06)

---

*"Context defines action. Every system reflects the order—or disorder—of its makers. COF and UCL together ensure that order prevails."*

*"Trust Nothing, Verify Everything. Evidence is the closing loop of trust."*
