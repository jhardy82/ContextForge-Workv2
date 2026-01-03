# Context Ontology Framework (COF)

**Status**: Complete
**Version**: 2.0
**Authoritative Source**: [docs/Codex/COF and UCL Definitions.md](Codex/COF%20and%20UCL%20Definitions.md)
**Last Updated**: 2025-11-11
**Related**: [01-Overview](01-Overview.md) | [02-Architecture](02-Architecture.md) | [09-Development-Guidelines](09-Development-Guidelines.md)

---

## Table of Contents

1. [Introduction](#introduction)
2. [What is COF?](#what-is-cof)
3. [The 13 Dimensions of Context](#the-13-dimensions-of-context)
4. [Sacred Geometry Integration](#sacred-geometry-integration)
5. [Evidence Orientation](#evidence-orientation)
6. [Pattern-Driven Relationships](#pattern-driven-relationships)
7. [Universal Context Law (UCL)](#universal-context-law-ucl)
8. [COF + UCL Together](#cof--ucl-together)
9. [Implementation in ContextForge](#implementation-in-contextforge)
10. [Practical Examples](#practical-examples)
11. [Quality Gates & Validation](#quality-gates--validation)
12. [See Also](#see-also)

---

## Introduction

The **Context Ontology Framework (COF)** is the structural backbone of ContextForge Work. It defines how ideas, contexts, workflows, and projects are captured, related, validated, and evolved.

COF ensures that every piece of work exists not as a flat record, but as a **multi-dimensional entity** analyzed across 13 axes of context. This approach guarantees completeness, traceability, and alignment with organizational goals.

> **Philosophy**: "No context exists in isolation. Every action, decision, and artifact must be anchored in its multi-dimensional reality."

---

## What is COF?

COF is a **13-dimensional ontology** that structures knowledge as a **lattice**, not silos. It serves as the ontology engine behind:

- **Idea Capture System** - Rapid capture with context preservation
- **Workflow Designer** - Multi-phase workflows with geometry alignment
- **TaskMan-v2** - 64-field task schema with COF integration
- **API & CLI** - Context-aware interfaces for all operations

### Key Features

1. **13 Ontology Dimensions** - Every context analyzed across 13 axes for multi-dimensional completeness
2. **Sacred Geometry Integration** - Validation against Circle, Triangle, Spiral, Golden Ratio, and Fractal patterns
3. **Evidence Orientation** - Logs, metrics, and validation are mandatory; contexts without evidence are orphans
4. **Pattern-Driven Relationships** - Links between contexts are geometric, reflecting resonance rather than arbitrary references

### Purpose

- **Organize knowledge** as a structured lattice, not silos
- **Ensure every context** is multi-dimensional, evidence-backed, and traceable
- **Serve as the ontology engine** behind Idea Capture, Workflow Designer, and the API
- **Enable coherent evolution** of work across teams, time, and complexity

---

## The 13 Dimensions of Context

Every context in ContextForge is analyzed across **13 dimensions** to ensure nothing exists as a flat record. Each dimension contributes to the multi-dimensional completeness of the system.

### 1. Motivational Context

**Purpose, goals, and driving forces behind the work.**

- **Business Driver**: Revenue, compliance, technical debt, innovation
- **Stakeholder Goals**: Executive vision, team objectives, customer needs
- **Value Proposition**: Expected outcomes and benefits

**Example**: "Reduce authentication latency by 50% to improve user experience and reduce support tickets."

---

### 2. Relational Context

**Dependencies, influences, and cross-links to other contexts.**

- **Upstream Dependencies**: What must complete before this work starts
- **Downstream Impacts**: What will be affected by this work
- **Cross-Component Links**: Integration points with other systems

**Example**: "JWT authentication (P0-005) blocks TaskMan-v2 production deployment and depends on Auth0 integration."

---

### 3. Dimensional Context

**Mapping across perspectives (scope, depth, and integration).**

- **Scope**: Breadth of impact (single component vs. system-wide)
- **Depth**: Technical complexity (surface vs. architectural change)
- **Integration**: How many systems/teams are involved

**Example**: "Database migration affects 3 components (cf_core, TaskMan-v2, Velocity Tracker) with deep schema changes."

---

### 4. Situational Context

**Environmental conditions, timing, and business circumstances.**

- **Market Conditions**: Competitive pressure, regulatory changes
- **Organizational State**: Capacity, priorities, constraints
- **Technical Environment**: Current architecture, tech debt, platform

**Example**: "Production deployment urgent due to Q4 customer commitments; infrastructure ready but docs missing."

---

### 5. Resource Context

**People, tools, budget, and other assets required.**

- **Team Capacity**: Available FTE, skill levels, availability
- **Tooling**: Required tools, licenses, infrastructure
- **Budget**: Financial constraints, cost-benefit analysis

**Example**: "Requires Team Alpha (2.5 FTE) + Team Beta (1.8 FTE) with FastAPI, PostgreSQL, React 19 expertise."

---

### 6. Narrative Context

**Business case, description, and communication framing.**

- **User Story**: How users experience this work
- **Business Case**: ROI, risk mitigation, strategic alignment
- **Communication Strategy**: How to explain to stakeholders

**Example**: "As a developer, I need comprehensive JWT docs so I can integrate authentication without trial-and-error."

---

### 7. Recursive Context

**Feedback cycles, iteration, and continuous improvement.**

- **Iteration Strategy**: How this work evolves over time
- **Feedback Loops**: Monitoring, metrics, retrospectives
- **Learning Capture**: What knowledge is gained and documented

**Example**: "Sprint velocity tracked in DuckDB; retrospectives every 2 weeks adjust estimation baseline."

---

### 8. Sacred Geometry Context

**Alignment with Circle, Triangle, Spiral, Golden Ratio, Fractal.**

- **Circle (Completeness)**: Is this work complete in all dimensions?
- **Triangle (Stability)**: Does it have a stable foundation?
- **Spiral (Iteration)**: Does it support continuous improvement?
- **Golden Ratio (Balance)**: Is effort balanced with value?
- **Fractal (Modularity)**: Does it scale and compose cleanly?

**Example**: "Test infrastructure (Triangle) enables confidence, with fractal test organization supporting growth."

---

### 9. Computational Context

**Logical models, algorithms, or calculations applied.**

- **Data Structures**: Entities, schemas, relationships
- **Algorithms**: Processing logic, optimization strategies
- **Performance**: Complexity, resource usage, scalability

**Example**: "DuckDB analytics engine with 0.23 hrs/point velocity baseline using linear regression."

---

### 10. Emergent Context

**Novel outcomes, lessons, or unexpected evolution.**

- **Unexpected Insights**: Discoveries during implementation
- **Risk Materialization**: Issues that emerged during work
- **Innovation Opportunities**: New possibilities identified

**Example**: "JWT implementation discovery saved 56-64 hours; shifted P0-005 from implementation to documentation."

---

### 11. Temporal Context

**Deadlines, milestones, and time-related factors.**

- **Hard Deadlines**: External commitments, compliance dates
- **Milestones**: Key checkpoints and deliverables
- **Sequencing**: Order of operations, critical path

**Example**: "Sprint 1 (P0 Critical) must complete before production deployment in 2-4 weeks."

---

### 12. Spatial Context

**Distribution across teams, locations, or environments.**

- **Team Topology**: Which teams own which components
- **Geographic Distribution**: Time zones, remote vs. co-located
- **Environment**: Dev, staging, production deployment topology

**Example**: "TaskMan-v2 frontend (Team Alpha) and backend (Team Alpha) deployed to Vercel + Cloud Run."

---

### 13. Holistic Context

**The unified view; synthesis of all other dimensions into coherence.**

- **Integration**: How all dimensions fit together
- **Coherence**: Are there conflicts or misalignments?
- **Completeness**: Are all dimensions adequately addressed?

**Example**: "P-CFWORK-DOCUMENTATION project synthesizes 35 files across 13 dimensions to create comprehensive roadmap."

---

## Sacred Geometry Integration

Every context must validate against the **five sacred patterns** to ensure harmony, stability, growth, balance, and recursion.

### The Five Sacred Patterns

#### 1. Circle (Completeness)

**Principle**: Work is complete when all dimensions are addressed and evidence is captured.

**Validation**:
- ✅ All 13 dimensions analyzed
- ✅ Evidence bundles present
- ✅ No orphaned contexts

**Example**: Sprint completion requires all tasks Done, evidence logged, retrospective complete.

---

#### 2. Triangle (Stability)

**Principle**: Three-point foundation provides stability: Plan → Execute → Validate.

**Validation**:
- ✅ Planning documentation exists
- ✅ Execution tracked with logs
- ✅ Validation tests passing

**Example**: QSE framework ensures Plan (requirements) → Execute (tests) → Validate (gates).

---

#### 3. Spiral (Iteration)

**Principle**: Progress is iterative, with each cycle building on the previous.

**Validation**:
- ✅ Retrospectives conducted
- ✅ Lessons captured in AARs
- ✅ Velocity trends tracked

**Example**: Velocity tracker shows iteration improvement from 0.18 → 0.23 hrs/point baseline.

---

#### 4. Golden Ratio (Balance)

**Principle**: Effort balanced with value; no over-engineering or under-engineering.

**Validation**:
- ✅ Cost-benefit analysis documented
- ✅ Right-sized solution (not perfect)
- ✅ Technical debt managed

**Example**: Sprint 2 deferred complex tasks (pytest markers) appropriately; focused on high-value READMEs.

---

#### 5. Fractal (Modularity)

**Principle**: Patterns repeat at different scales; components compose cleanly.

**Validation**:
- ✅ Modular architecture (DDD, Repository pattern)
- ✅ Reusable components
- ✅ Consistent patterns across scales

**Example**: cf_core domain entities use same Result monad pattern at all layers (services, repositories, API).

---

## Evidence Orientation

**Principle**: "Logs, metrics, and validation are mandatory. Contexts without evidence are treated as orphans and must be resolved or eliminated."

### Evidence Requirements

Every context must have:

1. **Structured Logs** - JSONL evidence bundles with UTC timestamps
2. **Metrics** - Quantitative measures of progress and quality
3. **Validation** - Tests, quality gates, compliance checks
4. **Documentation** - Architecture Decision Records (ADRs), READMEs, guides

### Evidence Hierarchy

```
Evidence Pyramid

    ┌─────────────────────────────┐
    │      Synthesis (AAR)        │ ← After-Action Reviews
    ├─────────────────────────────┤
    │    Validation (Tests)       │ ← Automated tests, quality gates
    ├─────────────────────────────┤
    │    Metrics (Analytics)      │ ← DuckDB velocity, coverage reports
    ├─────────────────────────────┤
    │   Logs (Structured JSONL)   │ ← Unified Logger, event taxonomy
    └─────────────────────────────┘
```

### Orphan Detection

Contexts become **orphans** when:

- No parent project or initiative (violates UCL)
- No evidence logs or metrics
- No validation tests
- No documentation

**Resolution**: Orphan contexts must be either:
1. **Anchored** - Link to parent context
2. **Archived** - Move to historical records
3. **Deleted** - Remove if no value

---

## Pattern-Driven Relationships

**Principle**: "Links between contexts are geometric, reflecting resonance rather than arbitrary references."

### Relationship Types

#### 1. Dependency (Sequential)

**Pattern**: Linear chain (A → B → C)

**Example**: P0-005 (JWT docs) → P0-006 (CI/CD) → Production Deployment

---

#### 2. Hierarchy (Nested)

**Pattern**: Tree structure (Project → Sprint → Task)

**Example**:
```
P-CFWORK-DOCUMENTATION
├── Sprint 1 (P0 Critical)
│   ├── P0-005 (JWT docs)
│   └── P0-006 (CI/CD)
└── Sprint 2 (P1 Quick Wins)
    ├── P1-005 (cf_core README)
    └── P1-007 (MCP config)
```

---

#### 3. Network (Many-to-Many)

**Pattern**: Graph with multiple connections

**Example**: cf_core domain layer used by TaskMan-v2, QSE framework, Velocity Tracker

---

#### 4. Resonance (Geometric Alignment)

**Pattern**: Contexts sharing Sacred Geometry patterns

**Example**: All DDD components (cf_core, TaskMan-v2) share Triangle (stability) + Fractal (modularity) patterns

---

## Universal Context Law (UCL)

UCL is the **governing principle** that ensures all contexts remain coherent, traceable, and complete.

### Core Law

> **"No orphaned, cyclical, or incomplete context may persist in the system."**

Every context must:

1. **Be anchored** to at least one parent project or initiative (no orphans)
2. **Flow toward resolution** (no deadlocks or cycles)
3. **Carry evidence** bundles, logs, and AARs (no unverifiable work)

### Enforcement Mechanisms

#### 1. Triple-Check Protocol

**Steps**:
1. **Initial Build** - Construct with COF 13D analysis
2. **Logs-First Diagnostics** - Verify evidence capture
3. **Reproducibility/DoD Compliance** - Confirm Definition of Done met

**Example**: Sprint completion checklist validates all three checks before declaring Done.

---

#### 2. Strategic Session Audits (3/6/9 Cadence)

**Schedule**:
- **3 weeks**: Tactical review (sprint progress, blockers)
- **6 weeks**: Strategic review (milestone alignment, roadmap)
- **9 weeks**: Governance review (COF, UCL, SCF compliance)

**Validation**: Confirm alignment with COF, UCL, SCF, and process standards.

---

#### 3. Compliance Gates

**Principle**: Nothing is "Done" until linkage, evidence, geometry, and closure are validated.

**Gates**:
- ✅ **Linkage**: Context anchored to parent
- ✅ **Evidence**: Logs and metrics captured
- ✅ **Geometry**: Sacred patterns validated
- ✅ **Closure**: DoD met, AAR documented

**Example**: TaskMan-v2 production deployment blocked by P0-005 (JWT docs) gate failure.

---

### Purpose of UCL

1. **Prevent Contextual Entropy** - Work falling into chaos or ambiguity
2. **Guarantee Global Coherence** - System remains traceable across all dimensions
3. **Provide Universal Guardrails** - For both human and AI agents in professional environments

---

## COF + UCL Together

### Relationship

- **COF** = The framework of how contexts are structured and analyzed (13D lattice)
- **UCL** = The law enforcing coherence, flow, and evidence completeness
- **Together** = COF gives the multidimensional map; UCL enforces the rules of navigation

### Governance Flow

```
COF + UCL Governance Loop

    ┌──────────────────────────────┐
    │   1. Capture Context (COF)   │ → 13D analysis
    └──────────────┬───────────────┘
                   │
    ┌──────────────▼───────────────┐
    │ 2. Validate Evidence (UCL)   │ → Logs, metrics, tests
    └──────────────┬───────────────┘
                   │
    ┌──────────────▼───────────────┐
    │ 3. Enforce Compliance (UCL)  │ → Gates, audits, checks
    └──────────────┬───────────────┘
                   │
    ┌──────────────▼───────────────┐
    │  4. Iterate & Improve (COF)  │ → Spiral pattern
    └──────────────┬───────────────┘
                   │
                   └─────────────────► Loop continues
```

### Implementation

Both COF and UCL are **implemented and enforced** through the ContextForge platform:

- **TaskMan-v2**: 64-field schema captures 13D context
- **QSE Framework**: Quality gates enforce UCL compliance
- **Velocity Tracker**: DuckDB analytics track iteration improvement
- **Unified Logger**: JSONL evidence bundles ensure traceability
- **Constitutional Validation**: Automated UCL compliance checks

---

## Implementation in ContextForge

### 64-Field Task Schema (TaskMan-v2)

The TaskMan-v2 task schema implements COF 13D analysis:

| COF Dimension | TaskMan-v2 Fields |
|---------------|-------------------|
| **Motivational** | `title`, `description`, `business_value`, `priority` |
| **Relational** | `dependencies`, `related_tasks`, `epic_id`, `sprint_id` |
| **Dimensional** | `scope`, `complexity`, `integration_points` |
| **Situational** | `context`, `environment`, `constraints` |
| **Resource** | `assignee`, `team`, `estimated_hours`, `tools_required` |
| **Narrative** | `user_story`, `acceptance_criteria`, `stakeholders` |
| **Recursive** | `iteration`, `feedback_notes`, `retrospective_links` |
| **Sacred Geometry** | `stability_score`, `completeness_pct`, `iteration_count` |
| **Computational** | `algorithm_notes`, `data_structures`, `performance_targets` |
| **Emergent** | `lessons_learned`, `risks_identified`, `innovations` |
| **Temporal** | `due_date`, `start_date`, `completed_date`, `milestones` |
| **Spatial** | `deployment_env`, `team_location`, `service_topology` |
| **Holistic** | `status`, `health`, `coherence_score`, `evidence_bundle_hash` |

### Quality Gates (QSE Framework)

QSE quality gates enforce UCL compliance:

1. **Linkage Gate**: Every task linked to sprint → project → initiative
2. **Evidence Gate**: Logs present, metrics captured, tests passing
3. **Geometry Gate**: Sacred patterns validated (Circle, Triangle, Spiral, Golden Ratio, Fractal)
4. **Closure Gate**: DoD met, AAR documented, retrospective complete

### Evidence Bundles (Unified Logger)

Structured JSONL logs implement evidence orientation:

```json
{
  "timestamp": "2025-11-11T18:30:00Z",
  "event": "task_complete",
  "task_id": "TASK-1234",
  "cof_dimensions": {
    "motivational": "Reduce auth latency 50%",
    "relational": ["P0-005", "Sprint-1"],
    "temporal": {"completed": "2025-11-11T18:30:00Z"},
    "holistic": {"status": "done", "evidence_hash": "sha256:abc123..."}
  },
  "persisted_via": "db",
  "ucl_compliance": {
    "anchored": true,
    "evidence_complete": true,
    "geometry_valid": true
  }
}
```

---

## Practical Examples

### Example 1: Sprint Planning with COF

**Context**: Planning Sprint 1 (P0 Critical) for TaskMan-v2 production deployment.

**COF 13D Analysis**:

1. **Motivational**: Business priority - Q4 customer commitments require production deployment
2. **Relational**: P0-005 (JWT docs) → P0-006 (CI/CD) → Production
3. **Dimensional**: System-wide scope (auth + infrastructure), deep architectural changes
4. **Situational**: Production urgent, infrastructure ready, docs missing
5. **Resource**: Team Alpha (2.5 FTE) + Team Beta (1.8 FTE), 2-4 weeks
6. **Narrative**: "As a DevOps engineer, I need CI/CD pipeline so deployments are reliable and repeatable"
7. **Recursive**: Sprint velocity 0.23 hrs/point, retrospective after Sprint 1
8. **Sacred Geometry**: Triangle (stable foundation), Circle (complete deployment), Spiral (iterate post-production)
9. **Computational**: GitHub Actions workflows, Docker containers, PostgreSQL 15
10. **Emergent**: JWT already implemented - changed P0-005 from implementation to documentation (saved 56-64 hours)
11. **Temporal**: 2-4 week deadline, P0-005 first (1-2 days), then P0-006 (3-5 days)
12. **Spatial**: Vercel (frontend), Cloud Run (backend), PostgreSQL (managed)
13. **Holistic**: Sprint 1 coherent, all dimensions aligned, evidence bundles ready

**UCL Validation**:
- ✅ Anchored to P-CFWORK-DOCUMENTATION project
- ✅ Evidence: Sprint plan documented, team assigned, backlog created
- ✅ Flow: Clear path to production deployment

---

### Example 2: Task Completion with UCL

**Context**: Completing P1-005 (cf_core README creation).

**UCL Enforcement**:

**1. Anchored Check**:
- ✅ Parent: Sprint 2 (P1 Quick Wins)
- ✅ Grandparent: P-CFWORK-DOCUMENTATION project
- ✅ No orphan status

**2. Flow Check**:
- ✅ Status: in_progress → done
- ✅ No cycles: Linear progression
- ✅ Resolution: README created, 300 lines, comprehensive

**3. Evidence Check**:
- ✅ Logs: `task_complete` event with timestamp
- ✅ Metrics: 300 lines, 9/10 quality score
- ✅ Validation: README reviewed, cross-references working
- ✅ Documentation: Content extracted from cf_core codebase

**Compliance Gate Result**: ✅ PASS - Task marked Done

---

### Example 3: Orphan Detection & Resolution

**Context**: Test files in `backup/` directory fail pytest collection.

**Orphan Detection**:
- ❌ No parent sprint or initiative
- ❌ No active development
- ❌ No recent git commits
- ❌ Causing 7 pytest collection errors

**UCL Violation**: Orphaned context (no anchor, causing issues)

**Resolution Options**:
1. **Anchor**: Move to active test directory, link to test infrastructure work
2. **Archive**: Move to historical records, exclude from pytest
3. **Delete**: Remove if no value

**Decision**: Option 2 (Archive) - Exclude `backup/` from pytest collection

**Result**: Orphan resolved, pytest errors eliminated

---

## Quality Gates & Validation

### COF Completeness Gate

**Check**: All 13 dimensions addressed?

**Validation**:
```python
def validate_cof_completeness(context: dict) -> bool:
    required_dimensions = [
        'motivational', 'relational', 'dimensional', 'situational',
        'resource', 'narrative', 'recursive', 'sacred_geometry',
        'computational', 'emergent', 'temporal', 'spatial', 'holistic'
    ]

    missing = [d for d in required_dimensions if d not in context]

    if missing:
        logger.warning(f"COF incomplete: missing {missing}")
        return False

    return True
```

---

### UCL Compliance Gate

**Check**: Anchored, flowing, evidenced?

**Validation**:
```python
def validate_ucl_compliance(context: dict) -> bool:
    checks = {
        'anchored': context.get('parent_id') is not None,
        'flowing': context.get('status') not in ['blocked', 'orphaned'],
        'evidenced': context.get('evidence_bundle_hash') is not None
    }

    if not all(checks.values()):
        logger.error(f"UCL violation: {checks}")
        return False

    return True
```

---

### Sacred Geometry Validation

**Check**: Patterns validated?

**Validation**:
```python
def validate_sacred_geometry(context: dict) -> bool:
    patterns = {
        'circle': context.get('completeness_pct', 0) >= 95,
        'triangle': context.get('stability_score', 0) >= 8,
        'spiral': context.get('iteration_count', 0) > 0,
        'golden_ratio': context.get('roi_score', 0) >= 7,
        'fractal': context.get('modularity_score', 0) >= 8
    }

    passing = sum(patterns.values())

    if passing < 3:  # At least 3 of 5 patterns must pass
        logger.warning(f"Sacred geometry insufficient: {patterns}")
        return False

    return True
```

---

## See Also

### Foundation Documents

- [01-Overview](01-Overview.md) - System overview with COF/UCL introduction
- [02-Architecture](02-Architecture.md) - Technical architecture implementing COF
- [09-Development-Guidelines](09-Development-Guidelines.md) - Development practices aligned with COF/UCL

### Authoritative Reference

- [docs/Codex/COF and UCL Definitions.md](Codex/COF%20and%20UCL%20Definitions.md) - **PRIMARY SOURCE** for COF/UCL definitions
- [docs/Codex/ContextForge Work Codex.md](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md) - Professional principles and governance

### Implementation Guides

- [04-Desktop-Application-Architecture](04-Desktop-Application-Architecture.md) - TaskMan-v2 64-field schema implementing COF
- [13-Testing-Validation](13-Testing-Validation.md) - QSE quality gates enforcing UCL
- [10-API-Reference](10-API-Reference.md) - Context-aware API design

### Related Frameworks

- **QSE (Quality Software Engineering)**: Evidence-based quality gates
- **UTMW (Understand-Transform-Model-Work)**: Workflow methodology
- **Sacred Geometry Patterns**: Circle, Triangle, Spiral, Golden Ratio, Fractal
- **DDD (Domain-Driven Design)**: cf_core domain modeling

---

**Document Status**: Complete ✅
**Authoritative**: Yes (sourced from docs/Codex/)
**Next Review**: 2026-02-11 (quarterly)
**Maintained By**: ContextForge Architecture Team

---

*"Context defines action. Every system reflects the order—or disorder—of its makers. COF and UCL together ensure that order prevails."*
