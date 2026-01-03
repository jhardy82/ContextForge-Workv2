# 01 – ContextForge Work Overview

**Status**: Complete
**Version**: 2.0
**Authoritative Source**: [docs/Codex/](Codex/)
**Last Updated**: 2025-11-11
**Related**: [02-Architecture](02-Architecture.md) | [03-Context-Ontology-Framework](03-Context-Ontology-Framework.md) | [09-Development-Guidelines](09-Development-Guidelines.md)

---

## Table of Contents

1. [What is ContextForge Work?](#what-is-contextforge-work)
2. [Vision & Mission](#vision--mission)
3. [Core Philosophies](#core-philosophies)
4. [System Summary](#system-summary)
5. [Key Components](#key-components)
6. [Operating Constraints](#operating-constraints)
7. [Quality & Compliance Principles](#quality--compliance-principles)
8. [Non-Goals / Out of Scope](#non-goals--out-of-scope)
9. [Document Map](#document-map)
10. [Quick Start](#quick-start)
11. [See Also](#see-also)

---

## What is ContextForge Work?

**ContextForge Work** is a governed, observable, idempotent workspace for enterprise scripting, analytics, and augmentation. It is both a **toolset and a discipline** that teaches us that **context defines action**, and that every system reflects the order—or disorder—of its makers.

### Definition

ContextForge isn't just technology—it's a framework for ensuring that all work is:

- **Structured** - Following the 13-dimensional Context Ontology Framework (COF)
- **Traceable** - With evidence bundles, logs, and metrics at every step
- **Aligned** - With organizational goals and the Universal Context Law (UCL)
- **Coherent** - Across teams, time, and complexity

> **Philosophy**: "Context is soil: nothing grows without it."
>
> Technology is built on mathematics, but guided by human values. ContextForge captures both.

### Purpose & Scope

This document orients:

- **Engineers** (primary) - Core objectives, interaction surfaces, development practices
- **Compliance / Audit** (secondary) - Evidence requirements, quality gates, governance
- **Leadership** (tertiary) - Strategic value, alignment with enterprise goals

---

## Vision & Mission

### Vision

**A world where all professional work is multi-dimensional, evidence-backed, and traceable** - where context defines action and systems reflect intentional order.

### Mission

Provide an enterprise-grade platform that:

1. **Captures Context** - 13-dimensional analysis (COF) for all work
2. **Enforces Coherence** - Universal Context Law (UCL) prevents orphans, cycles, deadlocks
3. **Enables Evolution** - Sacred Geometry patterns ensure harmony, stability, growth
4. **Delivers Value** - Observable, governed, idempotent workflows

### Strategic Alignment

ContextForge Work aligns with:

- **Quality First**: Evidence-based validation (QSE framework)
- **Continuous Improvement**: Velocity tracking (0.23 hrs/point proven baseline)
- **Organizational Knowledge**: Documentation as resilience (not afterthought)
- **Technical Excellence**: Domain-Driven Design (DDD), Repository Pattern, Result Monad

---

## Core Philosophies

ContextForge is guided by **11 core philosophies** from the [Work Codex](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md):

### 1. Trust Nothing, Verify Everything

**Principle**: Evidence is the closing loop of trust. Logs and tests ground belief.

**Implementation**:
- Structured JSONL logs for all state mutations
- Quality gates enforce evidence requirements
- Constitutional validation ensures compliance

---

### Database Access

**Quick Access**: ContextForge provides direct database access for AI agents and developers:

- **Quick Start**: [DATABASE-QUICK-REFERENCE.md](DATABASE-QUICK-REFERENCE.md) (30-second access)
- **Comprehensive Guide**: [AGENT-DATABASE-ACCESS.md](AGENT-DATABASE-ACCESS.md) (500+ lines)
- **SQL Examples**: [DATABASE-EXAMPLE-QUERIES.md](DATABASE-EXAMPLE-QUERIES.md) (30+ tested queries)
- **Troubleshooting**: [DATABASE-TROUBLESHOOTING-FLOWCHART.md](DATABASE-TROUBLESHOOTING-FLOWCHART.md) (decision trees)
- **Performance**: Python psycopg2 (168ms P95), Docker exec (223ms P95)
- **Security**: [PRODUCTION-DATABASE-DEPLOYMENT.md](PRODUCTION-DATABASE-DEPLOYMENT.md) (deployment guide)

**Helper Scripts**:
- `scripts/db_auth.py` - Python credential helper (environment variable support)
- `scripts/Get-DatabaseCredentials.ps1` - PowerShell credential helper

See [AGENTS.md](../AGENTS.md#database-access) for complete reference.

---

### 2. Workspace First

**Principle**: Begin with what exists; build outward only when necessary.

**Implementation**:
- Reuse before regenerate mandate
- Database authority (SQLite over CSV)
- Idempotent operations (re-runs converge)

---

### 3. Logs First

**Principle**: Truth lives in records, not assumptions.

**Implementation**:
- Unified Logger (structlog + JSONL)
- Event taxonomy (Codex Addendum B)
- ≥90% logging coverage target

**Event Flow**:
```
session_start → task_start → decision → artifact_emit → task_end → session_summary
```

---

### 4. Leave Things Better

**Principle**: Every action should enrich the system for those who follow.

**Implementation**:
- Documentation as resilience
- After-Action Reviews (AARs) mandatory
- Knowledge sharing over hoarding

---

### 5. Fix the Root, Not the Symptom

**Principle**: Problems repeat until addressed at the source.

**Implementation**:
- Root cause analysis in AARs
- Database normalization passes
- Migration scripts with rationale

---

### 6. Best Tool for the Context

**Principle**: Every task has its proper tool; discernment is the engineer's art.

**Implementation**:
- PowerShell for automation
- Python for orchestration
- DuckDB for analytics
- React for UX

---

### 7. Balance Order and Flow

**Principle**: Rigid order calcifies; unchecked flow dissolves. The right path blends both.

**Implementation**:
- Governance (COF/UCL) + Iteration (Spiral)
- Quality gates + Continuous improvement
- Planning + Adaptability

---

### 8. Iteration is Sacred

**Principle**: Progress spirals, not straight lines.

**Implementation**:
- Sprint retrospectives every 2 weeks
- Velocity tracking (DuckDB)
- Lessons learned captured in AARs

---

### 9. Context Before Action

**Principle**: To act without context is to cut against the grain.

**Implementation**:
- COF 13-dimensional analysis before work
- UCL compliance checks
- Evidence bundles required

---

### 10. Resonance is Proof

**Principle**: Solutions that harmonize across business, user, and technical needs endure.

**Implementation**:
- Sacred Geometry validation (Circle, Triangle, Spiral, Golden Ratio, Fractal)
- Cross-functional alignment
- Holistic integration checks

---

### 11. Diversity, Equity, and Inclusion

**Principle**: Teams and systems thrive when perspectives are varied, access is fair, and participation is open.

**Implementation**:
- Inclusive documentation practices
- Accessible interfaces (CLI + API + UI)
- Knowledge sharing culture

---

## System Summary

ContextForge Work is built on **6 core components** working in harmony:

### Interaction Flow (High-Level)

```
┌────────────────────────────────────────────────────────────────┐
│  CLI Commands (dbcli, cf_cli, tasks_cli)                     │
│  ↓                                                              │
│  State Mutation (SQLite authority)                            │
│  ↓                                                              │
│  JSONL Events Emitted (Unified Logger)                        │
│  ↓                                                              │
│  Trackers/DB Updated (evidence bundles)                       │
│  ↓                                                              │
│  Context Round-Tripped (context.yaml + JSON shadow)           │
│  ↓                                                              │
│  Docs Reflect State (living documentation)                    │
│  ↓                                                              │
│  Analytics Derive Signals (DuckDB velocity tracker)           │
└────────────────────────────────────────────────────────────────┘
```

### Base Concepts

From the Work Codex, ContextForge is built on **4 base concepts**:

1. **Foundation (Stability)** - A system is only as strong as its most stable component. Build with persistence in mind.
2. **Flow (Adaptability)** - Processes must evolve like water, iterative and renewing.
3. **Connection (Communication)** - Interfaces matter as much as implementations. Without clear connection, no structure holds.
4. **Potential (Unbuilt Future)** - Backlogs and unused capacity aren't waste; they're soil where the next growth will take root.

---

## Key Components

### 1. dbcli - Authoritative Operations

**Purpose**: Authoritative task / project / sprint / context operations

**Key Commands**:
```powershell
# Task operations
python dbcli.py task create "Implement JWT auth" --priority high
python dbcli.py task start TASK-001
python dbcli.py task complete TASK-001

# Sprint operations
python dbcli.py sprint status SPRINT-001 --json
python dbcli.py sprint create "Q1 2025 Sprint"

# Project operations
python dbcli.py project update PROJ-001 --status active
```

**Event Emissions**: All commands emit structured JSONL logs with evidence hashes

---

### 2. Trackers (CSV → SQLite Authority)

**Purpose**: Lifecycle & heartbeat metadata with **Database Authority** enforcement

**Key Principle** (Codex Addendum A):
- SQLite (`db/trackers.sqlite`) is the **single persistence authority** for trackers
- Runtime mutation of legacy CSVs is **blocked**
- Any legacy path triggers `direct_csv_access_blocked` and aborts

**Tables**:
- `tasks` - Task tracking with 64-field schema
- `sprints` - Sprint metadata and velocity
- `projects` - Project hierarchy and governance
- `contexts` - COF 13D context objects

**Authority Sentinel**: Logs `authority_check` events ensuring SQLite-first operations

---

### 3. Velocity Tracker (DuckDB)

**Purpose**: Performance / forecasting analytics with **proven baseline**

**Key Metrics**:
- **Proven Velocity Baseline**: 0.23 hrs/point (historical data analysis)
- **Sprint Velocity**: Story points completed per sprint
- **Forecast Accuracy**: Predicted vs actual completion times

**Analytics**:
```python
import duckdb

conn = duckdb.connect('db/metrics.duckdb')
result = conn.execute("""
    SELECT sprint_id, velocity, story_points
    FROM sprint_velocity
    ORDER BY sprint_id DESC
    LIMIT 5
""").fetchall()
```

**See**: [DuckDB-Velocity-Tracker.md](database/DuckDB-Velocity-Tracker.md)

---

### 4. Context Layer (COF Implementation)

**Purpose**: COF object graph & artifact states

**Files**:
- `context.yaml` - Human-readable context definitions
- `context.json` - Machine-readable JSON shadow
- `evidence_bundles/` - JSONL logs with SHA-256 hashes

**COF 13 Dimensions** (see [03-Context-Ontology-Framework.md](03-Context-Ontology-Framework.md)):
1. Motivational, 2. Relational, 3. Dimensional, 4. Situational, 5. Resource, 6. Narrative, 7. Recursive, 8. Sacred Geometry, 9. Computational, 10. Emergent, 11. Temporal, 12. Spatial, 13. Holistic

**UCL Enforcement**:
- No orphaned contexts (all anchored to parents)
- No cycles or deadlocks (flow toward resolution)
- Evidence bundles mandatory (logs, metrics, tests)

---

### 5. Logging Substrate (Unified Logger)

**Purpose**: JSONL event stream, evidence gating with **structured taxonomy**

**Event Taxonomy** (Codex Addendum B):

| Event | Purpose | Key Fields |
|-------|---------|------------|
| `task_create` | Persist a new task | task_id, persisted_via |
| `task_start` | Transition to in_progress | task_id, elapsed_prev_state |
| `task_update` | Field-level mutation | task_id, changes[], persisted_via |
| `task_complete` | Mark done | task_id, done_date, persisted_via |
| `sprint_status` | Sprint metrics | sprint_id, tasks_total, completion_pct |
| `artifact_emit` | Artifact created | path, hash, size, kind |
| `decision` | Branch / guard outcome | action, result, context_ids |

**Logging Quality Targets**:
- ≥90% of mutating command code paths emit domain event + decision outcome
- UTC timestamps, no PII
- JSON or enriched logger format

**See**: [UnifiedLogging-Guide.md](monitoring/UnifiedLogging-Guide.md)

---

### 6. Documentation Set (15+ docs)

**Purpose**: Structured knowledge & operational contracts

**Organization** (ContextForge Library):
- **1-FOUNDATION/**: Overview, Architecture, COF/UCL
- **2-APPLICATION/**: TaskMan-v2, Idea Capture, Workflow Designer
- **3-DATA/**: Database design, Velocity Tracker
- **4-ENGINEERING/**: Development Guidelines, API Reference, Configuration
- **5-QUALITY/**: Testing & Validation, QSE Framework
- **6-OPERATIONS/**: Security, Deployment, CI/CD

**Living Documentation**: Docs reflect current system state, not aspirational goals

---

## Operating Constraints

### Platform Requirements

- **Windows + PowerShell 5.1** - Compatibility retained for SCCM edges
- **PowerShell 7** - Default for new automation
- **Python ≥3.11** - Required for type hints, performance
- **Virtual Environment** - Auto-activation enforced (`.venv` mandatory)

### Network Constraints

- **Offline-Tolerant** - Core flows run without external network except dependency acquisition
- **Air-Gapped Ready** - All dependencies vendorable
- **Edge-Compatible** - SCCM environments supported

### Performance Constraints

- **DuckDB Analytics** - Sub-second query performance on 10K+ tasks
- **SQLite Authority** - ACID transactions with <100ms latency
- **JSONL Logging** - Async writes, no blocking mutations

---

## Quality & Compliance Principles

### Evidence Requirements

**Triple-Check Protocol** (UCL Enforcement):

1. **Initial Build** - Construct with COF 13D analysis
2. **Logs-First Diagnostics** - Verify evidence capture
3. **Reproducibility/DoD Compliance** - Confirm Definition of Done met

### Idempotency Guarantees

**Principle**: Re-runs converge (no duplicate rows / artifacts)

**Implementation**:
- Unique constraints on task_id, sprint_id, project_id
- Idempotent SQL operations (INSERT OR REPLACE)
- SHA-256 hashes prevent duplicate artifacts

### Reuse Before Regenerate

**Workspace-First Mandate**:
- Check for existing artifacts before creating new
- Use authority check to verify SQLite state
- Log `artifact_touch_batch` for reads

### Deterministic Environment

**Locked Dependencies**:
- `requirements.txt` with pinned versions
- `package-lock.json` for Node dependencies
- `.venv` manifest with Python version

---

## Non-Goals / Out of Scope

ContextForge Work **does not**:

1. **Provide production multi-tenant SaaS hosting** - Single-tenant, enterprise-focused
2. **Replace full CMDB or enterprise ITSM tooling** - Integrates with, doesn't replace
3. **Persist secrets** - Stores references only (use secrets management)
4. **Perform destructive infra changes without explicit confirmation** - Safety-first mandate

---

## Document Map

### Foundation (Start Here)

| Doc | Focus | Status |
|-----|-------|--------|
| [01-Overview](01-Overview.md) | **THIS DOC** - Orientation & principles | ✅ Complete |
| [02-Architecture](02-Architecture.md) | Structural & runtime model | ✅ Draft |
| [03-Context-Ontology-Framework](03-Context-Ontology-Framework.md) | COF 13D + UCL | ✅ Complete |

### Application Layer

| Doc | Focus | Status |
|-----|-------|--------|
| [04-Desktop-Application-Architecture](04-Desktop-Application-Architecture.md) | TaskMan-v2 (React + FastAPI) | 🚧 Planned |
| [06-Idea-Capture-System](06-Idea-Capture-System.md) | Rapid task capture workflows | 🚧 Planned |
| [07-Workflow-Designer](07-Workflow-Designer.md) | Multi-phase workflows | 🚧 Planned |

### Data Layer

| Doc | Focus | Status |
|-----|-------|--------|
| [05-Database-Design-Implementation](05-Database-Design-Implementation.md) | Storage, schema, migrations | ✅ Draft |

### Engineering

| Doc | Focus | Status |
|-----|-------|--------|
| [08-Optimization-Standards](08-Optimization-Standards.md) | Performance benchmarks | 🚧 Planned |
| [09-Development-Guidelines](09-Development-Guidelines.md) | Coding standards | ✅ Draft |
| [10-API-Reference](10-API-Reference.md) | CLI + REST API docs | ✅ Draft |
| [11-Configuration-Management](11-Configuration-Management.md) | Config schema & validation | ✅ Draft |

### Quality & Operations

| Doc | Focus | Status |
|-----|-------|--------|
| [12-Security-Authentication](12-Security-Authentication.md) | JWT, RBAC, secrets | 🚧 Planned |
| [13-Testing-Validation](13-Testing-Validation.md) | QSE quality gates | 🚧 Planned |
| [14-Deployment-Operations](14-Deployment-Operations.md) | CI/CD, monitoring | 🚧 Planned |

### Roadmap

| Doc | Focus | Status |
|-----|-------|--------|
| [15-Future-Roadmap](15-Future-Roadmap.md) | Feature roadmap | 🚧 Planned |

**Full Index**: See [README.md](../README.md) and [00-ContextForge-Library-Index.md](00-ContextForge-Library-Index.md)

---

## Quick Start

### 1. Check System Status

```powershell
# View database authority status
python dbcli.py status migration --json

# Check sprint velocity
python python/velocity_tracker.py analyze --sprint SPRINT-001
```

### 2. Create a Task

```powershell
# Create task with COF context
python dbcli.py task create "Implement JWT authentication" \
    --priority high \
    --sprint SPRINT-001 \
    --estimated-hours 16
```

### 3. View Evidence Logs

```powershell
# Tail recent logs
Get-Content logs/cf-work.jsonl -Tail 20

# Filter by event type
Get-Content logs/cf-work.jsonl | Where-Object { $_ -match "task_create" }
```

### 4. Run Quality Gates

```powershell
# Run QSE quality gates
pytest -m quality_gate

# Check coverage
pytest --cov=cf_core --cov-report=html
```

---

## See Also

### Foundation Documents

- [02-Architecture.md](02-Architecture.md) - Technical architecture, component diagram
- [03-Context-Ontology-Framework.md](03-Context-Ontology-Framework.md) - COF 13D + UCL definitions
- [09-Development-Guidelines.md](09-Development-Guidelines.md) - Development practices

### Authoritative Reference

- [docs/Codex/COF and UCL Definitions.md](Codex/COF%20and%20UCL%20Definitions.md) - **PRIMARY SOURCE** for COF/UCL
- [docs/Codex/ContextForge Work Codex.md](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md) - **PRIMARY SOURCE** for philosophies

### Implementation Guides

- [cf_core/README.md](../cf_core/README.md) - Domain-Driven Design implementation
- [UnifiedLogging-Guide.md](monitoring/UnifiedLogging-Guide.md) - Logging standards
- [DuckDB-Velocity-Tracker.md](database/DuckDB-Velocity-Tracker.md) - Velocity analytics

### Project Documentation

- [projects/P-CFWORK-DOCUMENTATION/](../projects/P-CFWORK-DOCUMENTATION/) - Documentation project artifacts
- [README.md](../README.md) - Project root with component overview

---

**Document Status**: Complete ✅
**Authoritative**: Yes (sourced from docs/Codex/)
**Next Review**: 2026-02-11 (quarterly)
**Maintained By**: ContextForge Architecture Team

---

*"ContextForge isn't just a toolset; it's a discipline. It teaches us that context defines action, and that every system reflects the order—or disorder—of its makers."*

*"Context is soil: nothing grows without it."*
