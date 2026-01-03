# Workflow Designer

**Version**: 1.0.0
**Created**: 2025-11-11
**Status**: Active (Planned Implementation)

---

## Purpose

The ContextForge Workflow Designer is a visual workflow builder that uses Sacred Geometry patterns as a design language to create, visualize, and execute structured workflows. It integrates with TaskMan-v2, the Idea Capture System, and ContextForge.Spectre to provide an intuitive interface for designing workflows that inherently align with COF principles and Sacred Geometry patterns.

**Key Objectives**:
- Provide visual drag-and-drop workflow design
- Enforce Sacred Geometry patterns (Triangle, Circle, Spiral, Golden Ratio, Fractal)
- Support UTMW methodology (Understand → Trust → Measure → Validate → Work)
- Generate executable task sequences in TaskMan-v2
- Real-time validation and progress visualization
- PowerShell and web-based interfaces

---

## Table of Contents

1. [Philosophy & Design Principles](#philosophy--design-principles)
2. [Sacred Geometry Workflow Patterns](#sacred-geometry-workflow-patterns)
3. [UTMW Methodology Integration](#utmw-methodology-integration)
4. [Architecture Overview](#architecture-overview)
5. [Visual Designer Interface](#visual-designer-interface)
6. [Workflow Templates](#workflow-templates)
7. [ContextForge.Spectre Integration](#contextforgespectre-integration)
8. [Workflow Execution](#workflow-execution)
9. [Best Practices](#best-practices)

---

## Philosophy & Design Principles

### Core Principles

**1. Geometry as Language**

Sacred Geometry patterns are not mere visualizations—they are the **fundamental language** of workflow design. Each pattern enforces specific structural and behavioral properties.

```text
┌────────────────────────────────────────────────────┐
│  Traditional Workflow                              │
│  Step 1 → Step 2 → Step 3 → Step 4 → Step 5      │
│  (Linear, no inherent structure)                  │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│  Sacred Geometry Workflow (Triangle)               │
│         Plan (△ vertex 1)                          │
│        /    \                                      │
│    Execute—Validate (△ vertices 2-3)               │
│  (Stable three-point foundation)                  │
└────────────────────────────────────────────────────┘
```

**Why**: Geometry provides **structural guarantees** (e.g., Triangle prevents workflows without validation, Circle enforces completeness checks).

---

**2. Visual Clarity**

Workflows should be immediately understandable at a glance.

```text
△ Triangle = 3-stage workflow (stable)
○ Circle = Closed-loop workflow (complete)
🌀 Spiral = Iterative workflow (progressive)
φ Golden Ratio = Balanced effort distribution
❄️ Fractal = Nested sub-workflows
```

---

**3. Constraint-Based Design**

The designer **enforces** Sacred Geometry constraints, preventing invalid workflows.

**Examples**:
- **Triangle**: Must have exactly 3 phases
- **Circle**: Must return to start or terminate at defined completion node
- **Golden Ratio**: Plan/Execute distribution must approximate 38%/62% effort
- **Fractal**: Sub-workflows must use same pattern as parent

---

**4. UTMW First**

Every workflow must map to the UTMW methodology: **Understand → Trust → Measure → Validate → Work**.

---

## Sacred Geometry Workflow Patterns

### 1. Triangle (Stability)

**Use Case**: Simple, stable 3-phase workflows

**Structure**:
```text
       ┌─────────────┐
       │   Phase 1   │  Plan / Understand
       │   (Plan)    │
       └──────┬──────┘
              │
       ┌──────▼──────┐
       │   Phase 2   │  Execute / Implement
       │  (Execute)  │
       └──────┬──────┘
              │
       ┌──────▼──────┐
       │   Phase 3   │  Validate / Verify
       │  (Validate) │
       └─────────────┘
```

**Constraints**:
- Exactly **3 phases** (no more, no less)
- Must proceed in order: Plan → Execute → Validate
- Cannot skip validation phase

**Example Workflows**:
- Feature implementation: Design → Develop → Test
- Bug fix: Diagnose → Fix → Verify
- Documentation: Research → Write → Review

**Code Definition**:
```json
{
  "workflow_id": "WF-TRIANGLE-001",
  "name": "Feature Implementation",
  "pattern": "Triangle",
  "phases": [
    {
      "id": "phase_1",
      "name": "Design",
      "description": "Create technical design and acceptance criteria",
      "duration_estimate": "2 hours",
      "utmw": ["Understand", "Trust"],
      "tasks": ["TASK-001", "TASK-002"]
    },
    {
      "id": "phase_2",
      "name": "Develop",
      "description": "Implement feature according to design",
      "duration_estimate": "5 hours",
      "dependencies": ["phase_1"],
      "utmw": ["Measure", "Work"],
      "tasks": ["TASK-003", "TASK-004", "TASK-005"]
    },
    {
      "id": "phase_3",
      "name": "Test",
      "description": "Validate feature meets acceptance criteria",
      "duration_estimate": "1.5 hours",
      "dependencies": ["phase_2"],
      "utmw": ["Validate"],
      "tasks": ["TASK-006"]
    }
  ]
}
```

---

### 2. Circle (Completeness)

**Use Case**: Closed-loop workflows with feedback validation

**Structure**:
```text
   ┌──────────────────────────────────┐
   │                                  │
Start ──→ Process ──→ Validate ──────┤
                         │            │
                         ↓            │
                      [Pass?]         │
                      /    \          │
                  Yes       No        │
                   │         │        │
                   ↓         └────────┘ (Loop back)
                Complete
```

**Constraints**:
- Must have **explicit validation gate**
- Must define **loop-back condition** OR **termination condition**
- Cannot exit without validation passing

**Example Workflows**:
- Sprint cycle: Plan → Execute → Review → Retrospective → (repeat or complete)
- CI/CD pipeline: Build → Test → Deploy → Monitor → (rollback or complete)
- Idea refinement: Capture → Enrich → Review → (promote or refine more)

---

### 3. Spiral (Iteration)

**Use Case**: Iterative workflows with progressive refinement

**Structure**:
```text
Cycle 1: Plan₁ → Execute₁ → Review₁ ──┐
                                        │
Cycle 2:    Plan₂ → Execute₂ → Review₂ ─┤
                                         │
Cycle 3:       Plan₃ → Execute₃ → Review₃ ─→ Complete

(Each cycle builds on previous learnings)
```

**Constraints**:
- Minimum **2 cycles** (otherwise use Triangle)
- Each cycle must include **retrospective/learning capture**
- Subsequent cycles incorporate **learnings from previous**

**Example Workflows**:
- Agile sprints: Sprint 1 → Sprint 2 → Sprint 3 → Release
- Optimization cycles: Baseline → Optimize 1 → Optimize 2 → Target achieved
- Documentation iterations: Draft → Review → Refine → Publish

---

### 4. Golden Ratio (Balance)

**Use Case**: Workflows requiring balanced effort distribution

**Structure**:
```text
┌──────────────────────┬────────────────────────────────────┐
│   Planning (38%)     │     Execution (62%)                │
│   Understand         │  Trust → Measure → Validate → Work │
├──────────────────────┴────────────────────────────────────┤
│  Total Effort: 10 hours                                   │
│  Planning: 3.8 hours  |  Execution: 6.2 hours             │
└───────────────────────────────────────────────────────────┘
```

**Constraints**:
- Planning phase must be **~38%** of total effort (φ ≈ 1.618)
- Execution phase must be **~62%** of total effort
- Tolerance: ±10% (28-48% planning, 52-72% execution)

---

### 5. Fractal (Modularity)

**Use Case**: Nested workflows with self-similar patterns

**Structure**:
```text
Parent Workflow (Triangle):
  ├─ Phase 1: Design
  │   └─ Sub-Workflow (Triangle):
  │       ├─ Research
  │       ├─ Draft
  │       └─ Review
  ├─ Phase 2: Implement
  │   └─ Sub-Workflow (Spiral):
  │       ├─ Cycle 1: Core feature
  │       ├─ Cycle 2: Edge cases
  │       └─ Cycle 3: Optimization
  └─ Phase 3: Validate
      └─ Sub-Workflow (Triangle):
          ├─ Unit tests
          ├─ Integration tests
          └─ Performance tests
```

**Constraints**:
- Sub-workflows must use **same or compatible Sacred Geometry pattern**
- Depth limit: **3 levels** (prevents over-nesting)
- Each sub-workflow must be **independently executable**

---

## UTMW Methodology Integration

### UTMW: Understand → Trust → Measure → Validate → Work

Every workflow phase must map to one or more UTMW stages to ensure evidence-based execution.

#### Phase 1: Understand (Context Building)

**Purpose**: Gather context, establish baseline, identify unknowns

**Activities**:
- Read documentation
- Profile current system
- Analyze requirements
- Research solutions

**Outputs**:
- Context summary
- Baseline metrics
- Knowledge gaps identified

---

#### Phase 2: Trust (Identify Critical Path)

**Purpose**: Identify the vital few (20%) that deliver 80% impact (Golden Ratio)

**Activities**:
- Analyze profiling data
- Identify hot paths
- Prioritize optimizations

**Outputs**:
- Critical path identified
- Hot path list (top 20%)
- Prioritized backlog

---

#### Phase 3: Measure (Estimate & Plan)

**Purpose**: Estimate effort using DuckDB velocity data

**Activities**:
- Story point estimation
- Time prediction (0.23 hrs/point baseline)
- Resource allocation

**Outputs**:
- Effort estimates
- Timeline projection
- Resource plan

---

#### Phase 4: Validate (Apply & Benchmark)

**Purpose**: Implement changes and validate improvements

**Activities**:
- Apply optimizations
- Run benchmarks
- Compare before/after

**Outputs**:
- Benchmark results
- Improvement metrics
- Evidence bundle

---

#### Phase 5: Work (Record & Iterate)

**Purpose**: Capture actual completion data for velocity tracking

**Activities**:
- Record actual hours
- Update velocity baseline
- Capture learnings (AAR)

**Outputs**:
- Velocity update
- AAR document
- Learnings captured

---

### Mapping UTMW to Sacred Geometry

| Sacred Geometry | Primary UTMW Phases | Rationale |
|-----------------|---------------------|-----------|
| **Triangle** | Trust → Measure → Validate | Stable 3-phase foundation |
| **Circle** | All 5 (looped) | Complete cycle with feedback |
| **Spiral** | All 5 (per cycle) | UTMW repeated each iteration |
| **Golden Ratio** | Understand (38%) + Rest (62%) | Balanced planning vs execution |
| **Fractal** | UTMW at each nesting level | Consistent across scales |

---

## Architecture Overview

### System Components

```text
┌───────────────────────────────────────────────────────────────┐
│                    User Interfaces                             │
│  Web UI (React) │ CLI (cf-core) │ PowerShell (Spectre)        │
└─────────────────┬─────────────────────────────────────────────┘
                  ↓
┌───────────────────────────────────────────────────────────────┐
│                 Workflow Designer Core                         │
│  - Pattern validation engine                                   │
│  - UTMW mapping engine                                         │
│  - Geometry constraint checker                                 │
│  - Task sequence generator                                     │
└─────────────────┬─────────────────────────────────────────────┘
                  ↓
┌───────────────────────────────────────────────────────────────┐
│             Workflow Storage (PostgreSQL)                      │
│  - workflows table (definitions)                               │
│  - workflow_executions table (runtime state)                   │
│  - workflow_templates table (Sacred Geometry patterns)         │
└─────────────────┬─────────────────────────────────────────────┘
                  ↓
┌───────────────────────────────────────────────────────────────┐
│              Integration Layer                                 │
│  TaskMan-v2 │ Idea Capture │ Velocity Tracker │ Evidence Gen  │
└───────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Web Designer** | React 19 + React Flow | Visual drag-and-drop interface |
| **CLI Designer** | CF_Core (Python + Rich) | Terminal-based workflow creation |
| **PowerShell Viz** | ContextForge.Spectre | Sacred Geometry rendering |
| **Backend** | FastAPI 0.100+ | Workflow API, validation engine |
| **Database** | PostgreSQL 15+ | Workflow definitions and state |
| **Execution Engine** | TaskMan-v2 Integration | Execute workflows as task sequences |

---

## Visual Designer Interface

### Web UI (React + React Flow)

**Layout**:
```text
┌────────────────────────────────────────────────────────────────────┐
│  [File] [Edit] [View] [Workflow]                      [Save] [Run] │
├─────────┬──────────────────────────────────────────────┬───────────┤
│ Palette │           Canvas                             │ Inspector │
│         │                                              │           │
│ △       │     ┌──────────┐                            │ Selected: │
│Triangle │     │  Phase 1 │                            │  Phase 1  │
│         │     │  (Plan)  │                            │           │
│ ○       │     └────┬─────┘                            │ Name:     │
│Circle   │          │                                  │ [Plan   ] │
│         │     ┌────▼─────┐                            │           │
│ 🌀      │     │  Phase 2 │                            │ Duration: │
│Spiral   │     │ (Execute)│                            │ [2 hours] │
│         │     └────┬─────┘                            │           │
│ φ       │          │                                  │ Tasks:    │
│Golden   │     ┌────▼─────┐                            │ [+ Add]   │
│         │     │  Phase 3 │                            │           │
│ ❄️      │     │(Validate)│                            │ UTMW:     │
│Fractal  │     └──────────┘                            │ ☑Understand│
│         │                                              │ ☐Trust    │
│         │     Pattern: Triangle ✓                     │ ☐Measure  │
└─────────┴──────────────────────────────────────────────┴───────────┘
```

**Features**:
- Drag-and-drop nodes from palette to canvas
- Real-time validation (pattern constraints enforced)
- Auto-layout based on Sacred Geometry pattern
- Task assignment (link to TaskMan-v2 tasks)
- UTMW mapping checkboxes for each phase
- Export to JSON, TaskMan-v2 tasks, or Evidence bundle

---

### CLI Designer (cf-core workflow)

**Interactive Workflow Creation**:
```bash
cf-core workflow create --interactive

# Prompts:
# 1. Workflow name: Feature Implementation
# 2. Select Sacred Geometry pattern:
#    [1] Triangle (3-phase stable)
#    [2] Circle (closed-loop)
#    [3] Spiral (iterative)
#    [4] Golden Ratio (balanced)
#    [5] Fractal (nested)
#    Choice: 1

# 3. Define Phase 1 (Plan):
#    Name: Design
#    Duration: 2 hours
#    Tasks: TASK-001, TASK-002
#    UTMW: Understand, Trust

# ✓ Workflow created: WF-TRIANGLE-001
# Preview: cf-core workflow show WF-TRIANGLE-001
# Execute: cf-core workflow run WF-TRIANGLE-001
```

---

## Workflow Templates

### Template Library

Pre-built workflows for common scenarios:

#### 1. Feature Implementation (Triangle)
```yaml
name: Feature Implementation
pattern: Triangle
phases:
  - name: Design
    duration: "2 hours"
    utmw: [Understand, Trust]
    tasks: [design_task]
  - name: Develop
    duration: "5 hours"
    utmw: [Measure, Work]
    tasks: [implement_task]
  - name: Test
    duration: "1.5 hours"
    utmw: [Validate]
    tasks: [test_task]
```

#### 2. Sprint Cycle (Circle)
```yaml
name: 2-Week Sprint
pattern: Circle
phases:
  - name: Sprint Planning
    duration: "2 hours"
    utmw: [Understand, Trust, Measure]
  - name: Development
    duration: "80 hours"
    utmw: [Work]
  - name: Sprint Review
    duration: "1 hour"
    utmw: [Validate]
  - name: Retrospective
    duration: "1 hour"
    utmw: [Work]
validation_gate:
  criteria: ["All stories completed", "No critical bugs"]
  on_pass: complete
  on_fail: loop_to_development
```

#### 3. Performance Optimization (Spiral)
```yaml
name: API Optimization
pattern: Spiral
cycles:
  - name: Baseline
    phases: [Understand, Trust, Measure, Validate]
    duration: "2 hours"
  - name: First Pass
    phases: [Understand, Trust, Measure, Validate, Work]
    duration: "3 hours"
  - name: Final Pass
    phases: [Understand, Trust, Measure, Validate, Work]
    duration: "2 hours"
completion_criteria: "p95 latency < 200ms"
```

---

## ContextForge.Spectre Integration

### PowerShell Sacred Geometry Rendering

**Module**: `ContextForge.Spectre`

#### Visualize Workflow as Sacred Geometry

```powershell
Import-Module ContextForge.Spectre

# Define workflow
$workflow = @{
    Pattern = 'Triangle'
    Phases = @(
        @{ Name = 'Design'; Duration = '2h'; Status = 'completed' }
        @{ Name = 'Develop'; Duration = '5h'; Status = 'in_progress' }
        @{ Name = 'Test'; Duration = '1.5h'; Status = 'pending' }
    )
    CurrentPhase = 'Develop'
}

# Render Sacred Geometry visualization
Show-CFWorkflowVisualization -Workflow $workflow -Geometry Triangle

# Output:
#          △ Design (✓ completed)
#         △ △
#        △   △ Develop (◐ in progress) ← Current
#       △     △
#      △       △ Test (○ pending)
```

---

#### Progress Tracking with Sacred Geometry

```powershell
# Initialize workflow progress
Start-CFProgress -Activity "Feature Implementation" -Pattern Triangle -TotalPhases 3

# Update as phases complete
Update-CFProgress -Phase "Design" -Status Completed
Write-Host "△ Design: Completed" -ForegroundColor Green

Update-CFProgress -Phase "Develop" -Status InProgress
Write-Host "△ Develop: In Progress" -ForegroundColor Yellow

# Complete workflow
Complete-CFProgress
Write-Host "△△△ Feature Implementation: Complete" -ForegroundColor Cyan
```

---

#### Sacred Geometry Symbols

```powershell
# Display available Sacred Geometry symbols
Write-ContextForgeSacredGeometry -AsPanel

# Output:
# ┌─────────────────────────────────────────────────┐
# │ Sacred Geometry Framework                       │
# ├─────────────────────────────────────────────────┤
# │ △ Triangle:     Stability, three-point validation│
# │ ○ Circle:       Completion, unified workflows   │
# │ 🌀 Spiral:       Iteration, upward progression   │
# │ φ Golden Ratio: Optimization, balanced distribution│
# │ ⬠ Pentagon:     Harmony, five-point balance     │
# │ ❄️ Fractal:      Modularity, self-similar patterns│
# └─────────────────────────────────────────────────┘
```

---

#### Workflow Execution with Spectre

```powershell
# Execute workflow with live updates
Invoke-CFWorkflow -WorkflowId "WF-TRIANGLE-001" -Verbose

# Output (live updating):
# ┌─────────────────────────────────────────────────┐
# │ Workflow: Feature Implementation                │
# │ Pattern: Triangle (△)                           │
# ├─────────────────────────────────────────────────┤
# │ Phase 1: Design                                 │
# │   ✓ TASK-001: Create technical design          │
# │   ✓ TASK-002: Write acceptance criteria        │
# │   Duration: 2.1h (estimated 2h)                 │
# ├─────────────────────────────────────────────────┤
# │ Phase 2: Develop                      [▰▰▰▰▰▱▱▱]│
# │   ✓ TASK-003: Implement core feature           │
# │   ◐ TASK-004: Handle edge cases (50% complete) │
# │   ○ TASK-005: Add error handling                │
# │   Duration: 2.5h / 5h                           │
# ├─────────────────────────────────────────────────┤
# │ Phase 3: Test                         [○○○○○○○○]│
# │   ○ TASK-006: Run integration tests             │
# │   Duration: 0h / 1.5h                           │
# └─────────────────────────────────────────────────┘
```

---

## Workflow Execution

### Execution Engine

**Backend**: FastAPI + TaskMan-v2 Integration

#### Execute Workflow

**Endpoint**: `POST /api/v1/workflows/{workflow_id}/execute`

**Request**:
```json
{
  "workflow_id": "WF-TRIANGLE-001",
  "execution_mode": "sequential",
  "auto_advance": true
}
```

**Response**:
```json
{
  "execution_id": "WE-20251111-001",
  "workflow_id": "WF-TRIANGLE-001",
  "status": "in_progress",
  "current_phase": "phase_2",
  "started_at": "2025-11-11T10:00:00Z",
  "phases_completed": 1,
  "phases_total": 3,
  "estimated_completion": "2025-11-11T18:30:00Z"
}
```

---

## Best Practices

### 1. Choose the Right Pattern

**Decision Tree**:
```text
Start
 ├─ Simple, one-time execution? → Triangle
 ├─ Needs feedback loop? → Circle
 ├─ Multiple iterations? → Spiral
 ├─ Need balanced planning/execution? → Golden Ratio
 └─ Large project with sub-workflows? → Fractal
```

---

### 2. Map All Phases to UTMW

**Good**:
```json
{
  "phases": [
    {"name": "Research", "utmw": ["Understand"]},
    {"name": "Design", "utmw": ["Trust", "Measure"]},
    {"name": "Implement", "utmw": ["Work"]},
    {"name": "Test", "utmw": ["Validate"]}
  ]
}
```

---

### 3. Use Templates for Common Workflows

```bash
# Use template
cf-core workflow create --template feature_implementation
```

**Template Library**:
- `feature_implementation` (Triangle)
- `sprint_cycle` (Circle)
- `optimization_cycles` (Spiral)
- `documentation_project` (Golden Ratio)
- `platform_migration` (Fractal)

---

### 4. Validate Early and Often

```bash
# Validate workflow definition before execution
cf-core workflow validate WF-TRIANGLE-001

# Output:
# ✓ Pattern: Triangle (valid)
# ✓ Phase count: 3 (required for Triangle)
# ✓ UTMW mapping: Complete
# ✓ Task assignments: All tasks exist in TaskMan-v2
```

---

### 5. Capture Workflow Metrics

```json
{
  "workflow_metrics": {
    "execution_id": "WE-20251111-001",
    "total_duration_estimated": "8.5 hours",
    "total_duration_actual": "9.2 hours",
    "variance": "+8.2%",
    "lessons_learned": [
      "Develop phase took longer due to unexpected edge cases"
    ]
  }
}
```

---

### 6. Visualize Progress

**PowerShell**:
```powershell
Show-CFWorkflowProgress -ExecutionId "WE-20251111-001" -Pattern Triangle
```

**Web UI**: Real-time progress bars, phase completion checkmarks

---

### 7. Export Workflows for Reuse

```bash
cf-core workflow export WF-TRIANGLE-001 --format json > feature_workflow.json
cf-core workflow import feature_workflow.json
```

---

## Related Documents

- **[03-Context-Ontology-Framework.md](03-Context-Ontology-Framework.md)** - Sacred Geometry patterns and COF
- **[06-Idea-Capture-System.md](06-Idea-Capture-System.md)** - Idea → Task → Workflow integration
- **[08-Optimization-Standards.md](08-Optimization-Standards.md)** - UTMW optimization workflow
- **[09-Development-Guidelines.md](09-Development-Guidelines.md)** - ContextForge.Spectre standards
- **[10-API-Reference.md](10-API-Reference.md)** - Workflow API endpoints
- **[15-Future-Roadmap.md](15-Future-Roadmap.md)** - P3-002 Workflow Designer initiative

---

**For professional philosophy guidance, see [ContextForge Work Codex](Codex/CODEX.md)**
