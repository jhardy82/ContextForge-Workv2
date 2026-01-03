# CF Research and Validation Plan

**Status**: Active  
**Version**: 1.0.0  
**Created**: 2025-12-02  
**Authority**: CF_CLI (`cf_cli.py`) is the authoritative entry point for all CF_CORE operations (see `AGENTS.md`)

---

## Table of Contents

1. [Context and Objectives](#context-and-objectives)
2. [Research Tracks](#research-tracks)
3. [Validation Strategy](#validation-strategy)
4. [Tooling and Quality Gates](#tooling-and-quality-gates)
5. [COF, UCL, QSE Alignment](#cof-ucl-qse-alignment)
6. [Execution Checklist](#execution-checklist)

---

## Research Team Personas

### Core Research & Architecture Team

#### ContextForge Philosopher
**Role**: Philosophical & Architectural Alignment Lead  
**Model**: Sonnet  
**Expertise**:
- Deep mastery of ContextForge Work Codex principles and philosophy
- Bridges philosophical understanding with practical implementation
- Constitutional Framework (COF 13D + UCL) integration
- Design pattern validation against foundational principles
- Sacred Geometry alignment (Triangle, Circle, Spiral, Fractal, Pentagon)

**Responsibilities**:
- Ensure all CF research and validation aligns with Work Codex philosophy
- Validate COF dimensional completeness and UCL compliance
- Review architectural decisions through philosophical lens
- Design tests that validate both functional correctness and principle alignment
- Resolve tensions between competing principles through principled reasoning

---

#### Research Coordinator
**Role**: Strategic Research Planning Lead  
**Model**: Opus  
**Expertise**:
- Complex research project decomposition and task allocation
- Multi-researcher orchestration and iteration strategy
- Quality threshold definition and success criteria
- Integration planning for diverse findings
- Resource optimization across specialist domains

**Responsibilities**:
- Break down CF research into optimally distributed tasks
- Allocate research tracks to appropriate specialists
- Define iteration strategies for comprehensive coverage
- Set quality gates and validation checkpoints
- Coordinate synthesis of findings across research streams

---

#### Research Orchestrator
**Role**: End-to-End Research Workflow Manager  
**Model**: Opus  
**Expertise**:
- Open Deep Research methodology execution
- Multi-phase research coordination with state management
- Agent coordination and dependency handling
- Quality control and synthesis management
- Comprehensive report generation

**Responsibilities**:
- Manage entire research workflow from query to report
- Track research progress and quality metrics
- Coordinate parallel research threads
- Handle inter-researcher dependencies
- Synthesize findings into cohesive insights

---

### Technical Implementation Team

#### Python Master Engineer
**Role**: Python Architecture & Quality Authority  
**Model**: Sonnet  
**Expertise**:
- Expert-level Python guidance across all domains
- Architecture design and performance optimization
- Testing strategies and automation design
- Code quality assessment and security analysis
- Framework selection and migration strategies
- Mentoring on software engineering principles

**Responsibilities**:
- Design and review CF_CLI and CF_CORE architecture
- Optimize performance for CLI cold start and DB operations
- Create comprehensive test suites (unit, integration, E2E)
- Ensure code quality and best practices compliance
- Mentor team on Python testing and validation patterns

---

#### Test Engineer
**Role**: Quality Assurance & Test Automation Lead  
**Model**: Sonnet  
**Expertise**:
- Comprehensive testing strategies (Test Pyramid)
- Test automation architecture (pytest, pytest-benchmark)
- Quality gates and coverage thresholds
- Risk assessment and critical path identification
- Performance, load, and regression testing

**Responsibilities**:
- Design Layer 1-4 validation strategies
- Create functional, integration, E2E, and constitutional test suites
- Establish performance benchmarks and quality gates
- Implement pytest marker system and test categorization
- Ensure test infrastructure supports CI/CD requirements

---

#### Database Architect
**Role**: Database Design & Data Modeling Authority  
**Model**: Opus  
**Expertise**:
- Database architecture and data modeling
- Domain-Driven Design alignment with database structure
- Scalability planning (horizontal/vertical, sharding)
- Technology selection (SQL vs NoSQL, polyglot persistence)
- Query optimization and access pattern design

**Responsibilities**:
- Validate TaskMan-v2 schema design and relationships
- Ensure PostgreSQL authority rules are correctly implemented
- Optimize database query performance for CF operations
- Design data flow validation for task/project/sprint lifecycle
- Review migration strategies and data integrity guarantees

---

#### DevOps Engineer
**Role**: CI/CD Pipeline & Infrastructure Authority  
**Model**: Sonnet  
**Expertise**:
- Infrastructure as Code (Terraform, Docker, Kubernetes)
- CI/CD pipeline architecture (GitHub Actions, GitLab CI)
- Testing integration (unit, integration, security, performance)
- Deployment strategies (blue-green, canary, rolling)
- Environment management and monitoring

**Responsibilities**:
- Design and optimize GitHub Actions workflows for CF validation
- Integrate quality gates into CI/CD pipeline
- Ensure Docker containerization follows best practices (WSL-only constraint)
- Configure test artifact collection and reporting
- Implement performance regression detection in CI

---

### Integration & Validation Team

#### MCP Expert
**Role**: Model Context Protocol Integration Specialist  
**Model**: Sonnet  
**Expertise**:
- MCP server architecture and protocol specifications
- MCP integration patterns and authentication
- Performance optimization and resource management
- STDIO-first transport policy and HTTP fallback
- Security and best practices compliance

**Responsibilities**:
- Document CF + MCP integration points (TaskMan, database-mcp, git-mcp)
- Validate transport policy (STDIO-first, HTTP fallback)
- Create MCP health check and readiness validation patterns
- Ensure CF_CLI and MCP tool consistency
- Design MCP server functional and integration tests

---

#### Technical Researcher
**Role**: Technical Documentation & Implementation Research  
**Model**: Sonnet  
**Expertise**:
- Code repository analysis and architecture pattern identification
- Technical documentation synthesis
- Implementation detail extraction
- Framework and library research
- Best practices validation

**Responsibilities**:
- Enumerate all CF_CLI commands via `--help` analysis
- Map CF_CLI → CF_CORE → DB access layers
- Document TaskMan-v2 ORM models and schema relationships
- Extract data flow patterns for key operations
- Research QSE/QSM integration with CF workflows

---

### Specialized Support Team

#### Error Detective
**Role**: Debugging & Root Cause Analysis Specialist  
**Model**: Sonnet  
**Expertise**:
- Systematic debugging methodologies
- Root cause analysis techniques
- Error pattern recognition
- Test failure diagnosis
- Performance bottleneck identification

**Responsibilities**:
- Diagnose test failures during validation phases
- Perform root cause analysis on constitutional violations
- Identify flaky test patterns and resolution strategies
- Debug CF_CLI command failures and error surfaces
- Support troubleshooting of MCP integration issues

---

#### Strategic Phase Planner
**Role**: Execution Planning & Phase Management  
**Model**: Opus  
**Expertise**:
- Multi-phase project planning and execution
- Milestone definition and tracking
- Risk assessment and mitigation planning
- Resource allocation and timeline management
- Quality gate sequencing

**Responsibilities**:
- Structure research tracks into executable phases
- Define milestones and checkpoints for validation layers
- Plan resource allocation across research and validation activities
- Coordinate dependencies between research tracks
- Track progress against execution checklist

---

### Team Collaboration Model

**Primary Coordination**: Research Coordinator + Research Orchestrator
- Research Coordinator: Strategic planning and task allocation
- Research Orchestrator: Workflow execution and agent coordination

**Technical Authority**: Python Master Engineer + Database Architect
- Architecture decisions and implementation guidance
- Code quality and database design validation

**Quality Assurance**: Test Engineer + DevOps Engineer
- Test strategy design and CI/CD integration
- Quality gate enforcement and automation

**Philosophical Oversight**: ContextForge Philosopher
- Ensures all work aligns with Work Codex principles
- Validates COF 13D completeness and UCL compliance
- Reviews architectural decisions through philosophical lens

**Integration Validation**: MCP Expert + Technical Researcher
- MCP integration documentation and testing
- CF system architecture and workflow research

---

## Context and Objectives

### Scope

| In Scope | Out of Scope |
|----------|--------------|
| CF_CLI commands and workflows | VS Code extension UX specifics |
| CF_CORE module responsibilities | Third-party SaaS internals (Auth0, GCP) |
| TaskMan-v2 schema and flows | Non-CF MCP servers |
| MCP integration (TaskMan, database-mcp) | Frontend React components |
| QSE/QSM workflows involving CF | |
| PostgreSQL/SQLite DB operations | |

### Primary Objectives

1. **Research**: Build precise, documented understanding of CF architecture, surfaces, and constraints
2. **Validation**: Design and execute multi-layer validation (functional, integration, constitutional, performance)
3. **Evidence**: Capture all findings as tests, evidence bundles, and actionable documentation

### Authority Rules

- **CF_CLI is authoritative**: All CF_CORE operations route through `cf_cli.py`
- **Do not bypass**: Direct module access is prohibited unless explicitly instructed
- **Extend, don't circumvent**: If CF_CLI lacks a feature, extend it rather than bypassing

### PowerShell `cf` Wrapper (Hybrid Architecture)

The `cf` alias provides PowerShell-native access to CF_CLI through the **ContextForge.PythonIntegration** module. This creates a hybrid architecture where PowerShell ergonomics wrap Python functionality.

#### Module Location
```
modules/ContextForge.PythonIntegration/ContextForge.PythonIntegration.psm1
```

#### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│              PowerShell Session                              │
├─────────────────────────────────────────────────────────────┤
│  cf <command>              (alias → Invoke-CFCommand)       │
│  Invoke-CFTaskList         (typed wrapper)                  │
│  Invoke-CFTaskCreate       (typed wrapper with validation)  │
│  Get-CFStatus              (hybrid info support)            │
├─────────────────────────────────────────────────────────────┤
│              ContextForge.PythonIntegration Module          │
│  - Automatic venv detection and activation                  │
│  - JSON output parsing → PSObjects                          │
│  - Performance measurement integration                       │
│  - Error handling and remediation suggestions               │
├─────────────────────────────────────────────────────────────┤
│              Python Backend (cf_cli.py)                      │
│  - Task/Project/Sprint management                           │
│  - Database operations                                       │
│  - Context synchronization                                   │
└─────────────────────────────────────────────────────────────┘
```

#### Core Components

| Component | Purpose | Location |
|-----------|---------|----------|
| `cf` alias | Quick CLI access | `Set-Alias -Name cf -Value Invoke-CFCommand` |
| `Invoke-CFCommand` | Generic command dispatcher | Handles all `cf_cli.py` subcommands |
| `Invoke-CFTaskList` | Typed task listing | PowerShell parameter validation |
| `Invoke-CFTaskCreate` | Typed task creation | `SupportsShouldProcess`, param validation |
| `Get-CFStatus` | System status | Hybrid architecture info support |
| `Get-CFPythonPath` | Venv detection | Auto-finds `.venv/Scripts/python.exe` |

#### Key Features

1. **Automatic Virtual Environment Detection**
   - Searches project root for `.venv/Scripts/python.exe`
   - Falls back to system Python if not found
   - Logs Python path discovery for debugging

2. **JSON Output Parsing**
   - Commands returning JSON are auto-parsed to PSObjects
   - Enables pipeline-friendly PowerShell integration
   - `-AsObject` switch for structured data

3. **Performance Measurement**
   - `-Measure` switch on all commands
   - Tracks execution time for hybrid overhead analysis
   - Performance log accessible via `$script:CFConfig.PerformanceLog`

4. **Error Handling**
   - Captures stderr and provides remediation suggestions
   - Non-zero exit codes raise errors with context
   - Warning emissions for command failures

#### Usage Examples

```powershell
# Using the cf alias (shortest form)
cf status
cf task list
cf task create --title "New task"

# Using typed cmdlets (full parameter validation)
Invoke-CFTaskList -Status 'in_progress' -AsObject
Invoke-CFTaskCreate -Title "New task" -Priority high -ProjectId "P-001" -WhatIf

# With performance measurement
cf task list -Measure
Get-CFStatus -IncludeHybridInfo -AsObject

# Pipeline integration
cf task list --json | ConvertFrom-Json | Where-Object { $_.priority -eq 'high' }
```

#### Validation Requirements

The `cf` wrapper adds another validation layer to Track 1:
- [ ] Verify `cf` alias is exported and functional
- [ ] Test `Invoke-CFCommand` with all subcommands
- [ ] Validate JSON parsing for `--json` outputs
- [ ] Test error handling for invalid commands
- [ ] Measure hybrid overhead vs direct Python calls
- [ ] Verify venv detection works correctly

---

## Research Tracks

### Track 1: CF_CLI Surface & Workflows

**Inputs**:
- `AGENTS.md` (CF_CLI authority, workflows)
- `cf_cli.py`, `tasks_cli.py`, `dbcli.py`
- `modules/ContextForge.PythonIntegration/` (PowerShell `cf` wrapper)
- `docs/` and `docs/plans/` documentation

**Activities**:
1. Enumerate all CF_CLI commands via `--help`
2. Map commands to TaskMan-v2 operations
3. Document command categories (core, context, diagnostic)
4. Identify gaps and extension opportunities
5. **Document `cf` PowerShell wrapper** (alias, typed cmdlets, hybrid architecture)
6. Validate `cf` wrapper ↔ `cf_cli.py` parity

**Artifacts**:
- [ ] Command matrix table (Python CLI + PowerShell wrappers)
- [ ] CF_CLI workflow diagrams
- [ ] Gap analysis document
- [ ] `cf` wrapper coverage report (which Python commands have typed PS wrappers)

### Track 2: Architecture & Data Flows

**Inputs**:
- `docs/02-Architecture.md`
- `docs/05-Database-Design-Implementation.md`
- TaskMan-v2 ORM models and schema

**Activities**:
1. Map CF_CLI → CF_CORE services → DB access layers
2. Document TaskMan-v2 entities and relationships
3. Identify legacy CSV/SQLite vs PostgreSQL authority rules
4. Document data flow for key operations

**Artifacts**:
- [ ] CF_CLI ↔ CF_CORE ↔ DB context diagram
- [ ] Data flow diagrams for task/project/sprint lifecycle
- [ ] Authority rules documentation

### Track 3: MCP Integration & Transport

**Inputs**:
- MCP server documentation
- `python/src/mcp_stdio_harness/`
- `test-mcp-complete-functionality.ps1`
- `scripts/Test-VSCodeMCPServers.ps1`

**Activities**:
1. Catalog CF-related MCP tools (TaskMan, DB, git)
2. Document transport policy (STDIO-first, HTTP fallback)
3. Map CF_CLI and MCP overlap points
4. Verify health check patterns

**Artifacts**:
- [ ] MCP tool catalog with CF relevance
- [ ] CF + MCP integration map
- [ ] Transport decision matrix

### Track 4: QSE/QSM Integration

**Inputs**:
- `docs/plans/QSM-Implementation-Setup.md`
- `docs/plans/QSE-PM2-Migration-Implementation-Guide.md`
- SPECTRE implementation/testing/validation plans

**Activities**:
1. Identify QSE/QSM phases that use CF_CLI or CF_CORE
2. Document quality and evidence expectations
3. Align with UTMW workflow phases

**Artifacts**:
- [ ] QSE phases × CF_CLI commands matrix
- [ ] E2E workflow validation list

---

## Validation Strategy

### Layer 1: Functional Validation (CF_CLI Behavior)

**Goal**: Every CF_CLI command behaves as documented under normal and error conditions

**Methods**:
```bash
# Command discovery
python cf_cli.py --help
python cf_cli.py task --help
python cf_cli.py project --help
python cf_cli.py sprint --help
python cf_cli.py status --help

# Functional tests
pytest tests/ -m "cf_cli" -v
pytest tests/system/ -k "cf_cli" -v
```

**Test Categories**:
| Category | Description | Marker |
|----------|-------------|--------|
| Happy path | Expected inputs produce expected outputs | `@pytest.mark.cf_cli` |
| Input validation | Missing/invalid args handled gracefully | `@pytest.mark.cf_cli_validation` |
| Error surfaces | DB unreachable, MCP unavailable, bad env | `@pytest.mark.cf_cli_errors` |

**Artifacts**:
- [ ] Functional test suite in `tests/system/test_cf_cli_functional.py`
- [ ] Test-to-documentation mapping

### Layer 1.5: `cf` Wrapper Validation (PowerShell Integration)

**Goal**: PowerShell `cf` wrapper correctly delegates to `cf_cli.py` and provides expected UX

**Methods**:
```powershell
# Ensure module is loaded
Import-Module ContextForge.PythonIntegration -Force

# Verify cf alias exists and points to Invoke-CFCommand
Get-Alias cf
Get-Command Invoke-CFCommand

# Functional tests via Pester
Invoke-Pester tests/pester/ContextForge.PythonIntegration.Tests.ps1 -Tag CFWrapper
```

**Test Categories**:
| Category | Description | Pester Tag |
|----------|-------------|------------|
| Wrapper delegation | `cf task list` → `python cf_cli.py task list` | `CFWrapperDelegation` |
| Environment handling | Correct venv activation, path resolution | `CFWrapperEnvironment` |
| Output formatting | Rich/JSON output modes work correctly | `CFWrapperOutput` |
| Error handling | Python errors surface correctly in PowerShell | `CFWrapperErrors` |

**Artifacts**:
- [ ] Pester tests in `tests/pester/ContextForge.PythonIntegration.Tests.ps1`
- [ ] `cf` wrapper command matrix (mapping to `cf_cli.py` commands)

### Layer 2: Integration & E2E Validation

**Goal**: Validate CF_CLI in combination with DB, TaskMan-v2, MCP, and QSE

**Methods**:
```bash
# Integration tests
pytest tests/integration/ -m "cf_core" -v

# E2E workflow tests
pytest tests/e2e/ -k "cf_workflow" -v

# MCP integration
pwsh -File "test-mcp-complete-functionality.ps1" -VerboseLogging
```

**Test Scenarios**:
1. Create project → Create sprint → Create task → Complete task → Verify DB state
2. CF_CLI + MCP TaskMan tool consistency check
3. CF_CLI + DB migration status verification
4. Context sync and evidence bundle generation

**Artifacts**:
- [ ] Integration tests in `tests/integration/test_cf_integration.py`
- [ ] E2E tests in `tests/e2e/test_cf_workflows.py`
- [ ] E2E runbook document

### Layer 3: Constitutional Validation (COF 13D + UCL)

**Goal**: CF contexts conform to COF 13D completeness and UCL laws

**Methods**:
```bash
# Constitutional tests
pytest tests/ -m "constitution" -v
pytest tests/constitutional/ -v
```

**UCL Checks**:
| Law | Description | Validation |
|-----|-------------|------------|
| UCL-1 | No orphaned contexts | All contexts have parent linkage |
| UCL-2 | No cyclical contexts | No circular dependencies |
| UCL-3 | Evidence required | All contexts have evidence bundle hash |

**COF 13D Checks**:
- [ ] Motivational context documented
- [ ] Relational dependencies mapped
- [ ] Temporal milestones defined
- [ ] Holistic integration validated

**Artifacts**:
- [ ] Constitutional tests in `tests/constitutional/test_cf_constitution.py`
- [ ] COF dimension coverage report

### Layer 4: Performance Validation

**Goal**: CF_CLI and core flows meet performance standards

**Targets** (from `docs/08-Optimization-Standards.md`):
| Metric | Target |
|--------|--------|
| CF_CLI cold start | <500ms |
| Task list query | <150ms p95 |
| Task create | <200ms p95 |
| DB single row lookup | <5ms |

**Methods**:
```bash
# Benchmark tests
pytest tests/benchmarks/ -m "cf_performance" --benchmark-only

# CLI timing
Measure-Command { python cf_cli.py status }
```

**Artifacts**:
- [ ] Benchmark tests in `tests/benchmarks/test_cf_performance.py`
- [ ] Performance baseline report

---

## Tooling and Quality Gates

### VS Code Tasks

| Task | Purpose | When to Use |
|------|---------|-------------|
| `test:quick` | Fast signal (<5s) | During development |
| `test:smoke` | Unit tests, skip slow | Pre-commit |
| `test:full` | Complete suite + coverage | Pre-merge |
| `quality:gate` | Format → Lint → Type → Smoke | Required for CF changes |

### Quality Requirements

All CF-related changes must pass:

```bash
# Format check
ruff format --check .

# Lint check
ruff check .

# Type check
mypy src/ --strict

# Smoke tests
pytest tests/ -m "unit and not slow" -q
```

### CI Integration

CF changes trigger:
1. `pytest-pr.yml` - Python testing on PRs
2. `quality.yml` - Comprehensive quality gates
3. `constitutional-cognitive-testing.yml` - Constitutional framework validation

---

## COF, UCL, QSE Alignment

### COF 13D Snapshot for CF

| Dimension | Application to CF |
|-----------|-------------------|
| **Motivational** | CF_CLI exists to provide authoritative orchestration for all CF_CORE operations |
| **Relational** | CF depends on: TaskMan-v2, PostgreSQL, MCP servers. Depended on by: QSE, agents, workflows |
| **Situational** | Current state: stable CLI, DB authority established, MCP integration active |
| **Resource** | Tools: pytest, ruff, mypy, Pester. Time: phased validation over sprints |
| **Narrative** | CF is the command center; this plan proves its robustness |
| **Recursive** | Subsequent sprints refine CF quality based on findings |
| **Computational** | Velocity tracking, analytics flows, constitutional framework |
| **Emergent** | Research may surface new insights about architecture gaps |
| **Temporal** | Milestones tied to current branch and sprint |
| **Spatial** | Local dev, CI, production environments |
| **Holistic** | CF ties together DB, MCP, QSE into unified workflow |
| **Validation** | This plan defines the validation approach |
| **Integration** | CF integrates back into Work Codex and quality gates |

### UCL Compliance

This plan ensures:
- ✅ **No orphaned contexts**: All CF tasks/projects anchored to parent initiatives
- ✅ **No cycles**: No circular dependencies in CF context graph
- ✅ **Evidence required**: Every validation activity generates evidence bundles

### QSE/UTMW Mapping

| UTMW Phase | Plan Section |
|------------|--------------|
| **Understand** | Research Tracks 1-4 |
| **Trust** | Baselines (CF_CLI authority, DB authority) |
| **Measure** | Performance validation, coverage metrics |
| **Validate** | Layers 1-4 in Validation Strategy |
| **Work** | Ongoing CF use with evidence capture |

---

## Execution Checklist

### Phase 1: Research (Week 1)

- [ ] Complete Track 1: CF_CLI command enumeration and mapping
- [ ] Complete Track 2: Architecture and data flow documentation
- [ ] Complete Track 3: MCP integration catalog
- [ ] Complete Track 4: QSE/QSM integration points

### Phase 2: Test Infrastructure (Week 2)

- [ ] Create `tests/system/test_cf_cli_functional.py`
- [ ] Create `tests/integration/test_cf_integration.py`
- [ ] Create `tests/e2e/test_cf_workflows.py`
- [ ] Create `tests/constitutional/test_cf_constitution.py`
- [ ] Create `tests/benchmarks/test_cf_performance.py`

### Phase 3: Validation Execution (Week 3)

- [ ] Execute Layer 1: Functional validation
- [ ] Execute Layer 2: Integration and E2E validation
- [ ] Execute Layer 3: Constitutional validation
- [ ] Execute Layer 4: Performance validation

### Phase 4: Documentation & Evidence (Week 4)

- [ ] Generate coverage reports
- [ ] Create evidence bundles
- [ ] Write AAR for CF research and validation
- [ ] Update CF documentation with findings

---

## Functional Test: CF Research Project Setup

### Overview

As a functional validation of CF_CLI, we will use it to create the actual project structure that tracks this research and validation work. This serves dual purposes:
1. **Dogfooding**: Validates CF_CLI works correctly by using it for real work
2. **Traceability**: Creates proper project/sprint/task hierarchy for tracking progress

### Project Structure

```
P-CF-RESEARCH-2025 (Project)
├── S-CF-RESEARCH-W1 (Sprint 1: Research Phase)
│   ├── T-CFR-001: CF_CLI Command Enumeration
│   ├── T-CFR-002: Architecture Documentation
│   ├── T-CFR-003: MCP Integration Catalog
│   └── T-CFR-004: QSE/QSM Integration Points
├── S-CF-RESEARCH-W2 (Sprint 2: Test Infrastructure)
│   ├── T-CFR-005: Functional Test Suite
│   ├── T-CFR-006: Integration Test Suite
│   ├── T-CFR-007: E2E Test Suite
│   ├── T-CFR-008: Constitutional Test Suite
│   └── T-CFR-009: Performance Benchmark Suite
├── S-CF-RESEARCH-W3 (Sprint 3: Validation Execution)
│   ├── T-CFR-010: Layer 1 Functional Validation
│   ├── T-CFR-011: Layer 2 Integration Validation
│   ├── T-CFR-012: Layer 3 Constitutional Validation
│   └── T-CFR-013: Layer 4 Performance Validation
└── S-CF-RESEARCH-W4 (Sprint 4: Documentation & Evidence)
    ├── T-CFR-014: Coverage Reports
    ├── T-CFR-015: Evidence Bundles
    ├── T-CFR-016: AAR Documentation
    └── T-CFR-017: CF Documentation Updates
```

### CF_CLI Setup Commands

```powershell
# Activate environment first
& ".venv/Scripts/Activate.ps1"

# ============================================
# STEP 1: Create the Project
# ============================================
python cf_cli.py project upsert `
    --id "P-CF-RESEARCH-2025" `
    --title "CF Research and Validation Initiative" `
    --description "Comprehensive research and validation of CF_CLI, CF_CORE, and related systems per CF-RESEARCH-AND-VALIDATION-PLAN.md"

# ============================================
# STEP 2: Create Sprints (4 weeks)
# ============================================

# Sprint 1: Research Phase
python cf_cli.py sprint upsert `
    --id "S-CF-RESEARCH-W1" `
    --project-id "P-CF-RESEARCH-2025" `
    --title "Phase 1: Research" `
    --goal "Build precise documented understanding of CF architecture, surfaces, and constraints"

# Sprint 2: Test Infrastructure
python cf_cli.py sprint upsert `
    --id "S-CF-RESEARCH-W2" `
    --project-id "P-CF-RESEARCH-2025" `
    --title "Phase 2: Test Infrastructure" `
    --goal "Create comprehensive test suites for functional, integration, E2E, constitutional, and performance validation"

# Sprint 3: Validation Execution
python cf_cli.py sprint upsert `
    --id "S-CF-RESEARCH-W3" `
    --project-id "P-CF-RESEARCH-2025" `
    --title "Phase 3: Validation Execution" `
    --goal "Execute all validation layers and collect evidence"

# Sprint 4: Documentation & Evidence
python cf_cli.py sprint upsert `
    --id "S-CF-RESEARCH-W4" `
    --project-id "P-CF-RESEARCH-2025" `
    --title "Phase 4: Documentation & Evidence" `
    --goal "Generate reports, evidence bundles, AAR, and update documentation"

# ============================================
# STEP 3: Create Tasks - Sprint 1 (Research)
# ============================================

python cf_cli.py task create `
    --title "CF_CLI Command Enumeration and Mapping" `
    --project "P-CF-RESEARCH-2025" `
    --sprint "S-CF-RESEARCH-W1" `
    --description "Enumerate all CF_CLI commands via --help, map to TaskMan-v2 operations, document categories"

python cf_cli.py task create `
    --title "Architecture and Data Flow Documentation" `
    --project "P-CF-RESEARCH-2025" `
    --sprint "S-CF-RESEARCH-W1" `
    --description "Map CF_CLI → CF_CORE → DB layers, document TaskMan-v2 entities, identify authority rules"

python cf_cli.py task create `
    --title "MCP Integration Catalog" `
    --project "P-CF-RESEARCH-2025" `
    --sprint "S-CF-RESEARCH-W1" `
    --description "Catalog CF-related MCP tools, document transport policy, map CF_CLI/MCP overlap"

python cf_cli.py task create `
    --title "QSE/QSM Integration Points" `
    --project "P-CF-RESEARCH-2025" `
    --sprint "S-CF-RESEARCH-W1" `
    --description "Identify QSE/QSM phases using CF, document quality expectations, align with UTMW"

# ============================================
# STEP 4: Create Tasks - Sprint 2 (Test Infrastructure)
# ============================================

python cf_cli.py task create `
    --title "Create Functional Test Suite" `
    --project "P-CF-RESEARCH-2025" `
    --sprint "S-CF-RESEARCH-W2" `
    --description "Create tests/system/test_cf_cli_functional.py with happy path, validation, and error tests"

python cf_cli.py task create `
    --title "Create Integration Test Suite" `
    --project "P-CF-RESEARCH-2025" `
    --sprint "S-CF-RESEARCH-W2" `
    --description "Create tests/integration/test_cf_integration.py for CF_CLI + DB + MCP integration"

python cf_cli.py task create `
    --title "Create E2E Test Suite" `
    --project "P-CF-RESEARCH-2025" `
    --sprint "S-CF-RESEARCH-W2" `
    --description "Create tests/e2e/test_cf_workflows.py for complete workflow validation"

python cf_cli.py task create `
    --title "Create Constitutional Test Suite" `
    --project "P-CF-RESEARCH-2025" `
    --sprint "S-CF-RESEARCH-W2" `
    --description "Create tests/constitutional/test_cf_constitution.py for COF 13D and UCL validation"

python cf_cli.py task create `
    --title "Create Performance Benchmark Suite" `
    --project "P-CF-RESEARCH-2025" `
    --sprint "S-CF-RESEARCH-W2" `
    --description "Create tests/benchmarks/test_cf_performance.py with cold start and query benchmarks"

# ============================================
# STEP 5: Create Tasks - Sprint 3 (Validation Execution)
# ============================================

python cf_cli.py task create `
    --title "Execute Layer 1: Functional Validation" `
    --project "P-CF-RESEARCH-2025" `
    --sprint "S-CF-RESEARCH-W3" `
    --description "Run functional tests, validate command behavior under normal and error conditions"

python cf_cli.py task create `
    --title "Execute Layer 2: Integration Validation" `
    --project "P-CF-RESEARCH-2025" `
    --sprint "S-CF-RESEARCH-W3" `
    --description "Run integration and E2E tests, validate CF_CLI + DB + MCP + QSE flows"

python cf_cli.py task create `
    --title "Execute Layer 3: Constitutional Validation" `
    --project "P-CF-RESEARCH-2025" `
    --sprint "S-CF-RESEARCH-W3" `
    --description "Run constitutional tests, validate COF 13D completeness and UCL compliance"

python cf_cli.py task create `
    --title "Execute Layer 4: Performance Validation" `
    --project "P-CF-RESEARCH-2025" `
    --sprint "S-CF-RESEARCH-W3" `
    --description "Run benchmark tests, validate against performance targets (<500ms cold start, etc.)"

# ============================================
# STEP 6: Create Tasks - Sprint 4 (Documentation)
# ============================================

python cf_cli.py task create `
    --title "Generate Coverage Reports" `
    --project "P-CF-RESEARCH-2025" `
    --sprint "S-CF-RESEARCH-W4" `
    --description "Generate and analyze test coverage reports, identify gaps"

python cf_cli.py task create `
    --title "Create Evidence Bundles" `
    --project "P-CF-RESEARCH-2025" `
    --sprint "S-CF-RESEARCH-W4" `
    --description "Package all test results, logs, and artifacts into SHA-256 hashed evidence bundles"

python cf_cli.py task create `
    --title "Write AAR Documentation" `
    --project "P-CF-RESEARCH-2025" `
    --sprint "S-CF-RESEARCH-W4" `
    --description "Create After Action Report documenting findings, lessons learned, recommendations"

python cf_cli.py task create `
    --title "Update CF Documentation" `
    --project "P-CF-RESEARCH-2025" `
    --sprint "S-CF-RESEARCH-W4" `
    --description "Update CF docs with research findings, new test patterns, validated workflows"
```

### Verification Commands

```powershell
# Verify project was created
python cf_cli.py project list

# Verify sprints
python cf_cli.py sprint list --project-id "P-CF-RESEARCH-2025"

# Verify tasks
python cf_cli.py task list --project "P-CF-RESEARCH-2025"
python cf_cli.py task list --sprint "S-CF-RESEARCH-W1"

# Check database status
python cf_cli.py status migration --json
```

### Progress Tracking Commands

As work progresses, update task status:

```powershell
# Start working on a task
python cf_cli.py task update <TASK-ID> --status in_progress

# Complete a task
python cf_cli.py task update <TASK-ID> --status completed

# View task details
python cf_cli.py task show <TASK-ID>
```

### Expected Validation Outcomes

| Step | Expected Result | Validates |
|------|----------------|-----------|
| Project creation | Project visible in list, stored in DB | `project upsert` command |
| Sprint creation | 4 sprints linked to project | `sprint upsert` command |
| Task creation | 17 tasks linked to correct sprints | `task create` command |
| Task update | Status changes persisted | `task update` command |
| List queries | Correct filtering by project/sprint | Query functionality |

### Failure Handling

If any command fails:
1. Check error message for missing dependencies or DB issues
2. Verify DB connection: `python cf_cli.py status migration --json`
3. Check logs in `logs/` directory
4. Document failure in Error Detective troubleshooting notes

---

## Functional Test: CF_CLI Project Bootstrap

This section serves as a **living functional test** of CF_CLI capabilities. By executing these commands, we validate CF_CLI while simultaneously creating the project structure for this research and validation initiative.

### Project Definition

**Project ID**: `P-CF-RESEARCH-VAL`  
**Project Title**: CF Research and Validation Initiative  
**Timeline**: 4 weeks (Phase 1-4 as defined in Execution Checklist)

### Sprint Structure

| Sprint ID | Title | Duration | Phase |
|-----------|-------|----------|-------|
| `S-CFRV-2025-W49` | Research & Discovery | Week 49 (Dec 2-8) | Phase 1 |
| `S-CFRV-2025-W50` | Test Infrastructure | Week 50 (Dec 9-15) | Phase 2 |
| `S-CFRV-2025-W51` | Validation Execution | Week 51 (Dec 16-22) | Phase 3 |
| `S-CFRV-2025-W52` | Documentation & Evidence | Week 52 (Dec 23-29) | Phase 4 |

### CF_CLI Bootstrap Commands

Execute these commands to create the project structure:

```bash
# Activate environment
& ".venv/Scripts/Activate.ps1"

# ============================================
# STEP 1: Create the Project
# ============================================
python cf_cli.py project upsert `
    --id "P-CF-RESEARCH-VAL" `
    --title "CF Research and Validation Initiative" `
    --description "Comprehensive research and validation of CF_CLI, CF_CORE, TaskMan-v2, MCP integration, and QSE alignment"

# ============================================
# STEP 2: Create Sprints
# ============================================

# Sprint 1: Research & Discovery
python cf_cli.py sprint upsert `
    --id "S-CFRV-2025-W49" `
    --project-id "P-CF-RESEARCH-VAL" `
    --title "Phase 1: Research & Discovery" `
    --start-date "2025-12-02" `
    --end-date "2025-12-08"

# Sprint 2: Test Infrastructure
python cf_cli.py sprint upsert `
    --id "S-CFRV-2025-W50" `
    --project-id "P-CF-RESEARCH-VAL" `
    --title "Phase 2: Test Infrastructure" `
    --start-date "2025-12-09" `
    --end-date "2025-12-15"

# Sprint 3: Validation Execution
python cf_cli.py sprint upsert `
    --id "S-CFRV-2025-W51" `
    --project-id "P-CF-RESEARCH-VAL" `
    --title "Phase 3: Validation Execution" `
    --start-date "2025-12-16" `
    --end-date "2025-12-22"

# Sprint 4: Documentation & Evidence
python cf_cli.py sprint upsert `
    --id "S-CFRV-2025-W52" `
    --project-id "P-CF-RESEARCH-VAL" `
    --title "Phase 4: Documentation & Evidence" `
    --start-date "2025-12-23" `
    --end-date "2025-12-29"

# ============================================
# STEP 3: Create Phase 1 Tasks (Research)
# ============================================

# Track 1: CF_CLI Surface & Workflows
python cf_cli.py task create `
    --title "Track 1: CF_CLI Command Enumeration" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W49" `
    --description "Enumerate all CF_CLI commands via --help, map to TaskMan-v2 operations" `
    --priority 1

python cf_cli.py task create `
    --title "Track 1: CF_CLI Workflow Diagrams" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W49" `
    --description "Create workflow diagrams showing CF_CLI command flows" `
    --priority 2

python cf_cli.py task create `
    --title "Track 1: CF_CLI Gap Analysis" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W49" `
    --description "Document feature gaps and extension opportunities" `
    --priority 2

# Track 2: Architecture & Data Flows
python cf_cli.py task create `
    --title "Track 2: CF_CLI → CF_CORE → DB Mapping" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W49" `
    --description "Map command execution path from CLI through core to database" `
    --priority 1

python cf_cli.py task create `
    --title "Track 2: TaskMan-v2 Entity Documentation" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W49" `
    --description "Document ORM models, relationships, and schema details" `
    --priority 1

python cf_cli.py task create `
    --title "Track 2: Data Flow Diagrams" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W49" `
    --description "Create data flow diagrams for task/project/sprint lifecycle" `
    --priority 2

# Track 3: MCP Integration
python cf_cli.py task create `
    --title "Track 3: MCP Tool Catalog" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W49" `
    --description "Catalog all CF-related MCP tools with relevance mapping" `
    --priority 1

python cf_cli.py task create `
    --title "Track 3: Transport Policy Documentation" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W49" `
    --description "Document STDIO-first policy, HTTP fallback, health checks" `
    --priority 2

# Track 4: QSE/QSM Integration
python cf_cli.py task create `
    --title "Track 4: QSE Phase × CF_CLI Matrix" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W49" `
    --description "Map QSE/QSM phases to CF_CLI commands and operations" `
    --priority 2

# ============================================
# STEP 4: Create Phase 2 Tasks (Test Infrastructure)
# ============================================

python cf_cli.py task create `
    --title "Create test_cf_cli_functional.py" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W50" `
    --description "Functional test suite for CF_CLI commands (happy path, validation, errors)" `
    --priority 1

python cf_cli.py task create `
    --title "Create test_cf_integration.py" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W50" `
    --description "Integration tests for CF_CLI + DB + TaskMan-v2" `
    --priority 1

python cf_cli.py task create `
    --title "Create test_cf_workflows.py" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W50" `
    --description "E2E workflow tests for complete task lifecycle" `
    --priority 1

python cf_cli.py task create `
    --title "Create test_cf_constitution.py" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W50" `
    --description "Constitutional tests for COF 13D and UCL compliance" `
    --priority 1

python cf_cli.py task create `
    --title "Create test_cf_performance.py" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W50" `
    --description "Performance benchmark tests for CF_CLI operations" `
    --priority 2

# ============================================
# STEP 5: Create Phase 3 Tasks (Validation)
# ============================================

python cf_cli.py task create `
    --title "Execute Layer 1: Functional Validation" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W51" `
    --description "Run functional test suite, capture results" `
    --priority 1

python cf_cli.py task create `
    --title "Execute Layer 2: Integration Validation" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W51" `
    --description "Run integration and E2E tests, validate workflows" `
    --priority 1

python cf_cli.py task create `
    --title "Execute Layer 3: Constitutional Validation" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W51" `
    --description "Run constitutional tests, validate COF/UCL compliance" `
    --priority 1

python cf_cli.py task create `
    --title "Execute Layer 4: Performance Validation" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W51" `
    --description "Run benchmarks, compare against targets" `
    --priority 2

# ============================================
# STEP 6: Create Phase 4 Tasks (Documentation)
# ============================================

python cf_cli.py task create `
    --title "Generate Coverage Reports" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W52" `
    --description "Generate and publish test coverage reports" `
    --priority 1

python cf_cli.py task create `
    --title "Create Evidence Bundles" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W52" `
    --description "Package all validation artifacts as evidence bundles with SHA-256 hashes" `
    --priority 1

python cf_cli.py task create `
    --title "Write AAR: CF Research and Validation" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W52" `
    --description "After-Action Review documenting findings, lessons learned" `
    --priority 1

python cf_cli.py task create `
    --title "Update CF Documentation" `
    --project "P-CF-RESEARCH-VAL" `
    --sprint "S-CFRV-2025-W52" `
    --description "Update AGENTS.md, docs/ with validated findings" `
    --priority 2

# ============================================
# STEP 7: Verify Project Structure
# ============================================

# List all tasks in the project
python cf_cli.py task list --project "P-CF-RESEARCH-VAL"

# Show project status
python cf_cli.py status --rich
```

### Validation Checkpoints

After executing the bootstrap commands, verify:

| Checkpoint | Command | Expected Result |
|------------|---------|-----------------|
| Project exists | `python cf_cli.py project list` | `P-CF-RESEARCH-VAL` appears |
| 4 sprints created | `python cf_cli.py sprint list --project P-CF-RESEARCH-VAL` | 4 sprints listed |
| Tasks distributed | `python cf_cli.py task list --project P-CF-RESEARCH-VAL` | ~20 tasks across sprints |
| DB state consistent | `python cf_cli.py status migration --json` | No migration errors |

### Bootstrap Script

For convenience, the above commands can be saved as a bootstrap script:

```powershell
# scripts/Bootstrap-CFResearchProject.ps1
# Run this script to create the entire project structure

param(
    [switch]$DryRun,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 CF Research and Validation Project Bootstrap" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "⚠️  DRY RUN MODE - Commands will be displayed but not executed" -ForegroundColor Yellow
}

# Commands array for execution
$commands = @(
    # Project
    'python cf_cli.py project upsert --id "P-CF-RESEARCH-VAL" --title "CF Research and Validation Initiative"',
    
    # Sprints
    'python cf_cli.py sprint upsert --id "S-CFRV-2025-W49" --project-id "P-CF-RESEARCH-VAL" --title "Phase 1: Research & Discovery"',
    'python cf_cli.py sprint upsert --id "S-CFRV-2025-W50" --project-id "P-CF-RESEARCH-VAL" --title "Phase 2: Test Infrastructure"',
    'python cf_cli.py sprint upsert --id "S-CFRV-2025-W51" --project-id "P-CF-RESEARCH-VAL" --title "Phase 3: Validation Execution"',
    'python cf_cli.py sprint upsert --id "S-CFRV-2025-W52" --project-id "P-CF-RESEARCH-VAL" --title "Phase 4: Documentation & Evidence"'
    
    # Tasks would follow...
)

foreach ($cmd in $commands) {
    if ($Verbose -or $DryRun) {
        Write-Host "  → $cmd" -ForegroundColor Gray
    }
    
    if (-not $DryRun) {
        Invoke-Expression $cmd
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Command failed: $cmd" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host ""
Write-Host "✅ Bootstrap complete!" -ForegroundColor Green
```

---

## Quick Commands Reference

```bash
# Activate environment
& ".venv/Scripts/Activate.ps1"

# CF_CLI help
python cf_cli.py --help

# Run CF-specific tests
pytest tests/ -m "cf_cli or cf_core" -v

# Quality gate
ruff format . && ruff check . && mypy src/ --strict && pytest tests/ -m "unit and not slow" -q

# MCP validation
pwsh -File "test-mcp-complete-functionality.ps1"

# Full test suite
pytest tests/ -v --cov=src --cov-report=html
```

---

## Functional Test: Create Plan Project Structure

This section serves as both a **functional validation** of CF_CLI and the **authoritative source** for tracking research and validation work. All sprints and tasks below will be created in the database using CF_CLI commands.

### Project Creation

```bash
# Create the CF Research & Validation project
python cf_cli.py project upsert \
  --id P-CF-RV-2025 \
  --name "CF Research and Validation 2025" \
  --owner "ContextForge Team" \
  --status active \
  --set-notes "Research and validation plan for CF_CLI, CF_CORE, and integrations. Created: 2025-12-03"
```

### Sprint 1: Research Phase (Week 1)

```bash
# Create Sprint 1
python cf_cli.py sprint upsert \
  --id S-CF-RV-2025-01 \
  --title "Sprint 1: Research Phase" \
  --project-id P-CF-RV-2025 \
  --start-date 2025-12-03 \
  --end-date 2025-12-09 \
  --status active
```

#### Sprint 1 Tasks

```bash
# Track 1: CF_CLI Surface & Workflows
python cf_cli.py task create \
  --title "T1.1: Enumerate all CF_CLI commands via --help" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-01 \
  --priority p1 \
  --work-type spike \
  --notes "Run cf_cli.py --help recursively for all subcommands"

python cf_cli.py task create \
  --title "T1.2: Map CF_CLI commands to TaskMan-v2 operations" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-01 \
  --priority p1 \
  --work-type spike \
  --notes "Document which CLI commands affect which database entities"

python cf_cli.py task create \
  --title "T1.3: Document command categories (core, context, diagnostic)" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-01 \
  --priority p2 \
  --work-type task \
  --notes "Categorize commands by function and usage pattern"

python cf_cli.py task create \
  --title "T1.4: Create CF_CLI command matrix artifact" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-01 \
  --priority p2 \
  --work-type task \
  --notes "Produce comprehensive command reference table"

# Track 2: Architecture & Data Flows
python cf_cli.py task create \
  --title "T2.1: Map CF_CLI → CF_CORE → DB access layers" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-01 \
  --priority p1 \
  --work-type spike \
  --notes "Document the call chain from CLI to database"

python cf_cli.py task create \
  --title "T2.2: Document TaskMan-v2 entities and relationships" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-01 \
  --priority p1 \
  --work-type spike \
  --notes "Extract ORM model definitions and FK relationships"

python cf_cli.py task create \
  --title "T2.3: Document CSV/SQLite vs PostgreSQL authority rules" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-01 \
  --priority p2 \
  --work-type task \
  --notes "Clarify when each data source is authoritative"

python cf_cli.py task create \
  --title "T2.4: Create data flow diagrams for task lifecycle" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-01 \
  --priority p2 \
  --work-type task \
  --notes "Visual diagrams showing create/update/complete flows"

# Track 3: MCP Integration & Transport
python cf_cli.py task create \
  --title "T3.1: Catalog CF-related MCP tools" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-01 \
  --priority p1 \
  --work-type spike \
  --notes "List TaskMan, DB, git MCP servers and their tools"

python cf_cli.py task create \
  --title "T3.2: Document STDIO-first transport policy" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-01 \
  --priority p2 \
  --work-type task \
  --notes "Document when STDIO vs HTTP transport is used"

python cf_cli.py task create \
  --title "T3.3: Map CF_CLI and MCP tool overlap" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-01 \
  --priority p2 \
  --work-type task \
  --notes "Identify where CLI and MCP provide equivalent functionality"

# Track 4: QSE/QSM Integration
python cf_cli.py task create \
  --title "T4.1: Identify QSE phases using CF_CLI or CF_CORE" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-01 \
  --priority p2 \
  --work-type spike \
  --notes "Map QSE workflow phases to CF operations"

python cf_cli.py task create \
  --title "T4.2: Document quality and evidence expectations" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-01 \
  --priority p2 \
  --work-type task \
  --notes "What evidence bundles are required for QSE workflows"
```

### Sprint 2: Test Infrastructure (Week 2)

```bash
# Create Sprint 2
python cf_cli.py sprint upsert \
  --id S-CF-RV-2025-02 \
  --title "Sprint 2: Test Infrastructure" \
  --project-id P-CF-RV-2025 \
  --start-date 2025-12-10 \
  --end-date 2025-12-16 \
  --status planned
```

#### Sprint 2 Tasks

```bash
# Test Infrastructure Tasks
python cf_cli.py task create \
  --title "T5.1: Create test_cf_cli_functional.py" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-02 \
  --priority p1 \
  --work-type feature \
  --notes "Functional test suite in tests/system/"

python cf_cli.py task create \
  --title "T5.2: Create test_cf_integration.py" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-02 \
  --priority p1 \
  --work-type feature \
  --notes "Integration test suite in tests/integration/"

python cf_cli.py task create \
  --title "T5.3: Create test_cf_workflows.py" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-02 \
  --priority p1 \
  --work-type feature \
  --notes "E2E workflow tests in tests/e2e/"

python cf_cli.py task create \
  --title "T5.4: Create test_cf_constitution.py" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-02 \
  --priority p1 \
  --work-type feature \
  --notes "Constitutional validation tests in tests/constitutional/"

python cf_cli.py task create \
  --title "T5.5: Create test_cf_performance.py" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-02 \
  --priority p2 \
  --work-type feature \
  --notes "Performance benchmark tests in tests/benchmarks/"

python cf_cli.py task create \
  --title "T5.6: Implement pytest markers for CF tests" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-02 \
  --priority p2 \
  --work-type task \
  --notes "Add cf_cli, cf_core, cf_integration markers to pytest.ini"
```

### Sprint 3: Validation Execution (Week 3)

```bash
# Create Sprint 3
python cf_cli.py sprint upsert \
  --id S-CF-RV-2025-03 \
  --title "Sprint 3: Validation Execution" \
  --project-id P-CF-RV-2025 \
  --start-date 2025-12-17 \
  --end-date 2025-12-23 \
  --status planned
```

#### Sprint 3 Tasks

```bash
# Layer 1: Functional Validation
python cf_cli.py task create \
  --title "T6.1: Execute Layer 1 - Happy path tests" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-03 \
  --priority p1 \
  --work-type task \
  --notes "Run functional tests with expected inputs"

python cf_cli.py task create \
  --title "T6.2: Execute Layer 1 - Input validation tests" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-03 \
  --priority p1 \
  --work-type task \
  --notes "Test missing/invalid argument handling"

python cf_cli.py task create \
  --title "T6.3: Execute Layer 1 - Error surface tests" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-03 \
  --priority p1 \
  --work-type task \
  --notes "Test DB unreachable, MCP unavailable scenarios"

# Layer 2: Integration & E2E
python cf_cli.py task create \
  --title "T6.4: Execute Layer 2 - Integration tests" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-03 \
  --priority p1 \
  --work-type task \
  --notes "Run CF_CORE + DB integration tests"

python cf_cli.py task create \
  --title "T6.5: Execute Layer 2 - E2E workflow tests" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-03 \
  --priority p1 \
  --work-type task \
  --notes "Run project → sprint → task → complete workflow"

# Layer 3: Constitutional
python cf_cli.py task create \
  --title "T6.6: Execute Layer 3 - UCL compliance tests" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-03 \
  --priority p1 \
  --work-type task \
  --notes "Validate no orphans, no cycles, evidence required"

python cf_cli.py task create \
  --title "T6.7: Execute Layer 3 - COF 13D completeness" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-03 \
  --priority p2 \
  --work-type task \
  --notes "Validate COF dimension coverage"

# Layer 4: Performance
python cf_cli.py task create \
  --title "T6.8: Execute Layer 4 - CLI cold start benchmark" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-03 \
  --priority p2 \
  --work-type task \
  --notes "Measure and validate <500ms target"

python cf_cli.py task create \
  --title "T6.9: Execute Layer 4 - DB query benchmarks" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-03 \
  --priority p2 \
  --work-type task \
  --notes "Validate p95 latency targets"
```

### Sprint 4: Documentation & Evidence (Week 4)

```bash
# Create Sprint 4
python cf_cli.py sprint upsert \
  --id S-CF-RV-2025-04 \
  --title "Sprint 4: Documentation & Evidence" \
  --project-id P-CF-RV-2025 \
  --start-date 2025-12-24 \
  --end-date 2025-12-30 \
  --status planned
```

#### Sprint 4 Tasks

```bash
python cf_cli.py task create \
  --title "T7.1: Generate coverage reports" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-04 \
  --priority p1 \
  --work-type task \
  --notes "HTML and JSON coverage reports for all CF tests"

python cf_cli.py task create \
  --title "T7.2: Create evidence bundles" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-04 \
  --priority p1 \
  --work-type task \
  --notes "Package test artifacts and results"

python cf_cli.py task create \
  --title "T7.3: Write AAR for CF research and validation" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-04 \
  --priority p1 \
  --work-type task \
  --notes "After Action Review documenting findings and lessons"

python cf_cli.py task create \
  --title "T7.4: Update CF documentation with findings" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-04 \
  --priority p2 \
  --work-type task \
  --notes "Update AGENTS.md, docs/ with research insights"

python cf_cli.py task create \
  --title "T7.5: Create CF_CLI command reference document" \
  --project-id P-CF-RV-2025 \
  --sprint S-CF-RV-2025-04 \
  --priority p2 \
  --work-type task \
  --notes "Comprehensive command reference derived from research"
```

### Verification Commands

After creating the project structure, verify with:

```bash
# List all projects
python cf_cli.py project list

# Show project details
python cf_cli.py project show --id P-CF-RV-2025

# List all sprints for project
python cf_cli.py sprint list --project-id P-CF-RV-2025

# List all tasks for project
python cf_cli.py project tasks --id P-CF-RV-2025

# List tasks for specific sprint
python cf_cli.py task list --sprint-id S-CF-RV-2025-01
```

### Project Structure Summary

| Entity | ID | Title | Status |
|--------|-----|-------|--------|
| **Project** | P-CF-RV-2025 | CF Research and Validation 2025 | active |
| **Sprint 1** | S-CF-RV-2025-01 | Research Phase | active |
| **Sprint 2** | S-CF-RV-2025-02 | Test Infrastructure | planned |
| **Sprint 3** | S-CF-RV-2025-03 | Validation Execution | planned |
| **Sprint 4** | S-CF-RV-2025-04 | Documentation & Evidence | planned |

**Total Tasks**: 27 tasks across 4 sprints

---

**Plan Owner**: ContextForge Team  
**Next Review**: 2025-12-09  
**Related Documents**:
- `AGENTS.md` - CF_CLI authority rules
- `docs/03-Context-Ontology-Framework.md` - COF 13D definitions
- `docs/13-Testing-Validation.md` - QSE testing standards
- `docs/08-Optimization-Standards.md` - Performance targets
