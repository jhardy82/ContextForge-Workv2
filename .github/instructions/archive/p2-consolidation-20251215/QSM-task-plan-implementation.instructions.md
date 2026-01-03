---
applyTo: "QSE*, QSM*, task plan*, implement task*, implementation plan*"
description: "QSM Task Plan Implementation with COF 13-dimensional analysis, Sacred Geometry validation, UCL compliance, integrated with Agent Core MCP protocols and CF_CLI authority. PowerShell-first scripting."
---

# QSM Task Plan Implementation (ContextForge + Agent-Core Complete)

## Authority & Integration

**Primary References:**

- `agent-core.instructions.md` — MCP orchestration, session integrity
- ContextForge Work Codex — 11 core philosophies
- Context Ontology Framework (COF) — 13-dimensional analysis (MANDATORY)
- Sacred Geometry Patterns — Circle, Triangle, Spiral, Golden Ratio, Fractal (MANDATORY)
- Universal Context Law (UCL) — No orphaned, cyclical, or incomplete contexts (MANDATORY)
- CF_CLI — Authoritative orchestration for CF_CORE operations

**Integration Philosophy:**
Task implementation must honor **both** ContextForge's ontological depth (COF 13D, Sacred Geometry, UCL) **and** agent-core's MCP protocols. Every task becomes a multi-dimensional entity with traceable evidence, sacred pattern alignment, and strategic tool usage.

**Task Management Hierarchy:**

1. **CF_CLI** → Authoritative entry point for domain workflows
2. **MCP Tools (STDIO-first)** → Assistant-driven tasks with COF awareness
3. **TaskMan MCP** → 64-field schema with COF integration and evidence correlation

---

## Session Integrity (MANDATORY)

### Constitution Check (Every Implementation Session)

**Execute at the beginning of any implementation session:**

Use vibe-check-mcp/constitution_check tool

**Purpose:**

- Validates session ID matches current project ID
- Synchronizes context if misaligned
- Logs corrections to evidence store (.QSE/evidence/)
- **UCL Compliance**: Prevents orphaned session contexts

**Enforcement:** No implementation may proceed without constitution_check completion.

---

## Implementation Process (ContextForge + Agent-Core Unified)

### Phase 0: Preconditions & COF Baseline (MANDATORY)

**A. Verify ContextForge Artifacts Present:**

```yaml
required_artifacts:
  - projects/{projectName}/.QSE/qse-config.yaml
  - projects/{projectName}/.QSE/quality-gates/*.yaml (Sacred Geometry gates)
  - projects/{projectName}/.QSE/cof-analyses/baseline.yaml (13D baseline)
  - projects/{projectName}/.QSE/docs/quality-plan.md
```

**B. Load COF 13-Dimensional Baseline:**

```yaml
# If exists, load previous COF analysis for continuity
cof_baseline_path: projects/{projectName}/.QSE/cof-analyses/baseline-{projectId}.yaml

# If not exists, will be created during Phase 1
```

**C. MCP Transport Readiness (STDIO-first):**

```powershell
# Verify TaskMan MCP health (HTTP fallback)
$healthUri = "http://localhost:3001/api/health"
$response = Invoke-RestMethod -Method GET -Uri $healthUri -ErrorAction Stop
if ($response.status -ne 'ok') {
    throw "TaskMan MCP not ready. Status: $($response.status)"
}
Write-Host "✓ TaskMan MCP ready" -ForegroundColor Green
```

**D. CF_CLI Validation:**

```powershell
# Verify CF_CLI accessibility
$cfCliStatus = python cf_cli.py status --format json | ConvertFrom-Json
if (-not $cfCliStatus) {
    throw "CF_CLI not accessible"
}
Write-Host "✓ CF_CLI accessible: version $($cfCliStatus.version)" -ForegroundColor Green
```

**E. Sacred Geometry Lock Acquisition:**

```powershell
# Create lock file for work isolation
$lockPath = "projects/$projectName/.QSE/temp/locks/$workId.lock"
$lockMetadata = @{
    sacred_pattern = "spiral"  # Iteration-based work
    cof_dimension_focus = @("computational", "recursive", "emergent")
    timestamp = Get-Date -Format "o"
    session_id = $env:QSE_SESSION_ID
}

New-Item -Path $lockPath -ItemType File -Force | Out-Null
$lockMetadata | ConvertTo-Json | Set-Content $lockPath
Write-Host "✓ Lock acquired: $lockPath" -ForegroundColor Green
```

---

### Phase 1: COF 13D Analysis with Agent Memory (MANDATORY)

**A. Load Historical Context:**

Use digitarald.agent-memory/memory tool
Query: "Previous implementations for {projectName}, COF dimensional patterns, sacred geometry effectiveness, lessons learned"

**B. Perform Complete COF 13-Dimensional Analysis:**

> **MANDATORY: Address ALL 13 dimensions with ≥200 words per dimension**

```yaml
cof_dimensional_analysis:

  1_motivational_context:
    business_driver: "Specific business need this implementation addresses"
    success_criteria: "Measurable outcomes expected"
    stakeholder_value: "Who benefits and specific value delivered"
    priority_justification: "Why this work is prioritized now (with evidence)"

  2_relational_context:
    dependencies: "Upstream dependencies (task IDs, systems, data)"
    influences: "Downstream impacts (what will be affected)"
    connections: "Integration points with existing systems"
    ucl_parent_linkage: "Parent sprint/project (MANDATORY for orphan prevention)"

  3_dimensional_context:
    scope: "Breadth (single function vs. system-wide)"
    depth: "Complexity (surface change vs. architectural)"
    integration: "Cross-system coordination required"

  4_situational_context:
    environment: "Current technical/organizational state"
    constraints: "Limitations (time, resources, technical debt)"
    opportunities: "Favorable conditions enabling this work"
    market_timing: "External factors (compliance, competition)"

  5_resource_context:
    human_resources: "Team members, FTE allocation, skill requirements"
    technical_resources: "Tools, libraries, infrastructure needed"
    temporal_resources: "Time estimate with breakdown"
    budget_allocation: "Costs (if applicable)"

  6_narrative_context:
    user_journey: "End-user interaction and experience"
    stakeholder_story: "Business stakeholder perspective"
    technical_narrative: "Implementation approach and maintenance"
    business_case: "ROI, value proposition, strategic alignment"

  7_recursive_context:
    feedback_loops: "How results inform next iterations"
    improvement_cycles: "Continuous enhancement mechanisms"
    learning_capture: "Knowledge retention strategy (agent memory + .QSE/)"
    retrospective_plan: "AAR documentation plan"

  8_sacred_geometry_context:
    circle_completeness: "Plan for full cycle coverage"
    triangle_stability: "Three-point validation strategy"
    spiral_progression: "Learning integration approach"
    golden_ratio_balance: "Resource optimization rationale"
    fractal_consistency: "Pattern coherence across scales"

  9_computational_context:
    algorithms: "Processing logic and decision rules"
    data_models: "Entities, schemas, relationships"
    performance: "Efficiency targets, scalability considerations"
    technical_architecture: "Design patterns (DDD, Repository, etc.)"

  10_emergent_context:
    unexpected_outcomes: "Potential novel discoveries"
    serendipitous_benefits: "Unplanned positive impacts possible"
    adaptive_responses: "System evolution anticipated"
    innovation_potential: "Breakthrough possibilities"

  11_temporal_context:
    scheduling: "Timeline, milestones, dependencies"
    sequencing: "Order of operations, critical path"
    cadence: "Sprint cycle alignment"
    deadline_criticality: "Hard vs. soft deadlines"

  12_spatial_context:
    distribution: "Geographic/organizational spread"
    topology: "Network and communication structure"
    boundaries: "Interface and integration points"
    deployment_architecture: "Environment topology (dev/staging/prod)"

  13_holistic_context:
    synthesis: "Unified view across all 12 dimensions"
    coherence: "Internal consistency validation"
    completeness: "Coverage assessment"
    resonance: "Business/user/technical harmony"
```

**C. Document COF Analysis:**

```powershell
# Store COF analysis in .QSE/ for traceability
$cofAnalysisPath = "projects/$projectName/.QSE/cof-analyses/implementation-$taskId-$(Get-Date -Format 'yyyyMMdd').yaml"
$cofAnalysis | ConvertTo-Yaml | Set-Content $cofAnalysisPath
Write-Host "✓ COF analysis saved: $cofAnalysisPath" -ForegroundColor Green
```

**D. Apply Sequential Thinking with COF Integration:**

Use SeqThinking/sequential_thinking tool
Plan → Act → Observe → Adapt → Log cycle incorporating:

- COF dimensional insights
- Sacred geometry alignment requirements
- UCL compliance checkpoints
- Agent memory learnings

---

### Phase 2: Systematic Implementation (Task-by-Task with COF Evidence)

**For each implementation task:**

#### 1. Bind to TaskMan with COF Profile (via MCP or CF_CLI)

##### Option A: MCP Tool (interactive tasks)

Use TaskMan MCP tool: task_update
Set task status: in_progress
Record COF profile: 13D analysis reference
Log sacred geometry pattern: primary pattern for this task
Record start timestamp

##### Option B: CF_CLI (system operations)

```powershell
# Update task status with COF context
$taskParams = @{
    TaskId = "T-001"
    Status = "in_progress"
    CofAnalysisId = "implementation-T-001-$(Get-Date -Format 'yyyyMMdd')"
    SacredPattern = "spiral"
}

python cf_cli.py task update $taskParams.TaskId `
    --status $taskParams.Status `
    --cof-analysis-id $taskParams.CofAnalysisId `
    --sacred-pattern $taskParams.SacredPattern

Write-Host "✓ Task $($taskParams.TaskId) bound with COF profile" -ForegroundColor Green
```

#### 2. Execute with Evidence Generation (ContextForge Principles)

**A. Follow ContextForge Work Codex Principles:**

1. **Trust Nothing, Verify Everything**: Validate all assumptions with evidence
2. **Workspace First**: Inventory existing artifacts, enhance rather than replace
3. **Logs First**: Generate structured evidence from the start
4. **Leave Things Better**: Enrich system for future work
5. **Fix the Root, Not the Symptom**: Address underlying causes
6. **Best Tool for the Context**: Strategic MCP tool selection
7. **Balance Order and Flow**: Structured yet adaptive execution
8. **Iteration is Sacred**: Capture learning for next spiral
9. **Context Before Action**: COF analysis guides implementation
10. **Resonance is Proof**: Validate business/user/technical harmony
11. **Diversity, Equity, and Inclusion**: Multiple perspectives considered

**B. Follow Design Patterns from ContextForge:**

```powershell
# Pattern discovery from framework
$frameworkPatterns = Get-ChildItem -Path "contextforge/infrastructure","contextforge/core" -Recurse -Filter "*.pattern.yaml"
$applicablePatterns = $frameworkPatterns | Where-Object { $_.Name -match $taskContext.Domain }

Write-Host "Applying ContextForge patterns:" -ForegroundColor Cyan
$applicablePatterns | ForEach-Object {
    Write-Host "  - $($_.Name)" -ForegroundColor Gray
}
```

**C. Generate COF-Enhanced Evidence:**

```yaml
evidence_bundle:
  type: implementation
  task_id: T-001
  work_id: W-0001
  timestamp: 2025-11-21T11:00:00Z
  session_id: QSE-20251121-1100-UUID

  cof_dimensional_impacts:
    motivational: "Achieved 50% latency reduction (success criterion met)"
    relational: "Unblocked P0-006 (downstream dependency)"
    computational: "Implemented caching with O(1) lookup"
    recursive: "Documented pattern for future optimizations"
    holistic: "Resonance achieved: business KPI met, users satisfied, technical debt reduced"

  sacred_geometry_adherence:
    circle: "Complete implementation with tests and docs"
    triangle: "Three-point validation: unit tests + integration tests + manual QA"
    spiral: "Learning captured in AAR for next iteration"
    golden_ratio: "2.3 days actual vs. 2.5 estimated (balanced)"
    fractal: "Pattern consistent from epic → feature → task level"

  changes:
    - path: "projects/my-project/src/cache.py"
      change: added
      summary: "Redis caching layer with TTL management"
      lines_changed: 145
      pattern: "Repository pattern with dependency injection"

  tools_used:
    - mcp: "SeqThinking/sequential_thinking"
      purpose: "Plan implementation approach with COF guidance"
    - cf_cli: "python cf_cli.py context sync"
      purpose: "Synchronize COF analysis with task state"

  validation:
    tests_run: ["unit/test_cache.py::TestCacheLayer", "integration/test_auth_flow.py"]
    tests_passed: true
    coverage: 87%
    quality_gates: ["pre-commit", "pre-merge"]
    sacred_geometry_gates: ["circle", "triangle", "spiral"]

  ucl_compliance:
    parent_linkage: "Sprint-2, P-MY-PROJECT"
    evidence_complete: true
    no_orphans: true
    no_cycles: true

  lessons_learned:
    - insight: "Redis TTL strategy prevented memory bloat"
      cof_dimension: "emergent"
      stored_in_memory: true
      memory_id: "mem-cache-ttl-20251121"
```

**D. Record to TaskMan with COF Tags:**

```powershell
# Update TaskMan with complete evidence
$evidenceUpdate = @{
    TaskId = "T-001"
    Status = "completed"
    CofProfile = "implementation-T-001-$(Get-Date -Format 'yyyyMMdd')"
    SacredPatterns = @("spiral", "triangle")
    Changes = $changes
    Evidence = $evidenceBundle
    Links = @{
        commits = @("sha256:abc123...")
        prs = @("PR-456")
        artifacts = @(".QSE/evidence/implementation-T-001.yaml")
    }
}

# Via MCP or CF_CLI
Use TaskMan MCP tool: task_update with $evidenceUpdate
# OR
python cf_cli.py task update $evidenceUpdate.TaskId --evidence-json ($evidenceUpdate | ConvertTo-Json -Depth 10)

Write-Host "✓ TaskMan updated with COF evidence" -ForegroundColor Green
```

#### 3. Sacred Geometry Quality Validation (EVERY change)

**A. Run Quality Checks:**

```powershell
# Via QSE tooling with Sacred Geometry validation
./scripts/qse/Run-QualityChecks.ps1 `
    -ProjectPath "projects/$projectName" `
    -ValidateSacredGeometry `
    -Verbose

# Generates:
# - projects/$projectName/.QSE/test-results/
# - projects/$projectName/.QSE/metrics/
# - projects/$projectName/.QSE/sacred-geometry/validation-*.yaml

Write-Host "✓ Quality checks completed with Sacred Geometry validation" -ForegroundColor Green
```

**B. Validate Against Sacred Geometry Gates:**

```yaml
sacred_geometry_validation:

  circle_gate:
    requirement: "Complete implementation with closure"
    checks:
      - code_complete: PASS
      - tests_complete: PASS
      - docs_complete: PASS
      - evidence_complete: PASS
    result: PASS

  triangle_gate:
    requirement: "Three-point stability"
    checks:
      - plan_exists: PASS
      - execution_tracked: PASS
      - validation_passed: PASS
    result: PASS

  spiral_gate:
    requirement: "Learning captured for iteration"
    checks:
      - retrospective_notes: PASS
      - lessons_in_aar: PASS
      - agent_memory_stored: PASS
    result: PASS

  golden_ratio_gate:
    requirement: "Balanced resource utilization"
    checks:
      - estimate_accuracy: PASS (2.3 actual / 2.5 estimated = 92%)
      - technical_debt_managed: PASS
      - value_delivered: PASS
    result: PASS

  fractal_gate:
    requirement: "Pattern consistency across scales"
    checks:
      - epic_pattern_match: PASS
      - feature_pattern_match: PASS
      - task_pattern_match: PASS
    result: PASS

overall_sacred_geometry_compliance: 5/5 gates passed
```

**C. Validate Against Quality Gates:**

```powershell
# Validate with CF_CLI
$gateValidation = python cf_cli.py gate validate `
    --project "projects/$projectName" `
    --gate pre-merge `
    --format json | ConvertFrom-Json

if ($gateValidation.passed) {
    Write-Host "✓ Quality gates: PASS" -ForegroundColor Green
    Write-Host "  Coverage: $($gateValidation.coverage)% (target: 80%)" -ForegroundColor Gray
    Write-Host "  Complexity: $($gateValidation.complexity) avg (limit: 10)" -ForegroundColor Gray
} else {
    Write-Host "✗ Quality gates: FAIL" -ForegroundColor Red
    $gateValidation.failures | ForEach-Object {
        Write-Host "  - $_" -ForegroundColor Red
    }
    throw "Quality gate validation failed"
}
```

#### 4. Evidence Correlation with COF Tagging

**A. Update .QSE artifacts with COF metadata:**

```powershell
# Verify .QSE/ structure
$qseArtifacts = @(
    "projects/$projectName/.QSE/cof-analyses/implementation-T-001-$(Get-Date -Format 'yyyyMMdd').yaml"
    "projects/$projectName/.QSE/sacred-geometry/validation-T-001-$(Get-Date -Format 'yyyyMMdd').yaml"
    "projects/$projectName/.QSE/test-results/latest-results.xml"
    "projects/$projectName/.QSE/metrics/latest-complexity.json"
    "projects/$projectName/.QSE/evidence/implementation-T-001-$(Get-Date -Format 'yyyyMMdd').yaml"
)

$qseArtifacts | ForEach-Object {
    if (Test-Path $_) {
        Write-Host "✓ $_" -ForegroundColor Green
    } else {
        Write-Host "✗ Missing: $_" -ForegroundColor Red
    }
}
```

**B. Commit changes with COF context:**

```powershell
# Stage changes
git add projects/$projectName/src/ projects/$projectName/.QSE/

# Create comprehensive commit message
$commitMessage = @"
feat(T-001): implement Redis caching layer

Implementation:
- Added caching with O(1) lookup performance
- Repository pattern with dependency injection
- TTL management prevents memory bloat

COF Dimensional Impacts:
- Motivational: Achieved 50% latency reduction target
- Computational: O(1) performance vs. previous O(n)
- Recursive: Pattern documented for future optimizations
- Holistic: Resonance achieved across business/user/technical

Sacred Geometry Compliance:
- Circle: Complete with tests and docs
- Triangle: Three-point validation passed
- Spiral: Learning captured for iteration
- Golden Ratio: 92% estimate accuracy
- Fractal: Pattern consistent across scales

QSE Metrics:
- Coverage: 87% (target: 80%)
- Complexity: 8.2 avg (limit: 10)
- All quality gates: PASS
- All sacred geometry gates: PASS

Evidence: projects/$projectName/.QSE/evidence/implementation-T-001-$(Get-Date -Format 'yyyyMMdd').yaml
COF Analysis: projects/$projectName/.QSE/cof-analyses/implementation-T-001-$(Get-Date -Format 'yyyyMMdd').yaml
"@

git commit -m $commitMessage
git push

Write-Host "✓ Changes committed with COF context" -ForegroundColor Green
```

---

### Phase 3: Continuous Validation & UCL Compliance

**A. After Each Task Completion:**

```powershell
# 1. Run tests
npm test  # or pytest, depending on project

# 2. Collect metrics
./scripts/qse/Run-QualityChecks.ps1 -ProjectPath "projects/$projectName"

# 3. Validate Sacred Geometry gates
$sgValidation = Get-Content "projects/$projectName/.QSE/sacred-geometry/validation-latest.yaml" | ConvertFrom-Yaml
$passedGates = ($sgValidation.gates | Where-Object { $_.result -eq "PASS" }).Count
Write-Host "Sacred Geometry: $passedGates/5 gates passed" -ForegroundColor $(if ($passedGates -ge 3) { "Green" } else { "Yellow" })

# 4. Update COF analysis if dimensions changed
if ($dimensionChanges) {
    ./scripts/qse/Update-COFAnalysis.ps1 -ProjectPath "projects/$projectName" -TaskId "T-001"
}

# 5. Update TaskMan
python cf_cli.py task update T-001 --status completed --evidence-path ".QSE/evidence/implementation-T-001.yaml"

# 6. Use vibe_learn on any failures
if ($failures) {
    Use vibe-check-mcp/vibe_learn tool
    # Store in agent memory with COF context
}

# 7. Verify UCL compliance
$uclCheck = ./scripts/qse/Verify-UCLCompliance.ps1 -ProjectPath "projects/$projectName" -TaskId "T-001"
if (-not $uclCheck.Passed) {
    throw "UCL compliance violation: $($uclCheck.Violations -join ', ')"
}
Write-Host "✓ UCL compliance verified" -ForegroundColor Green
```

**B. If Task Diverges from Plan (Sacred Pattern Adjustment):**

```powershell
# Use branched thinking for alternatives
Use SeqThinking/branched_thinking tool

# Explore alternatives considering:
# - Which sacred geometry patterns still apply
# - COF dimensional trade-offs
# - UCL compliance preservation

# Record deviation in TaskMan
$deviation = @{
    Reason = "Interface changed due to upstream API update"
    CofImpact = "Relational dimension updated, no holistic impact"
    SacredPatternAdjustment = "Triangle still valid, added Circle verification"
    ApprovedBy = "tech-lead@domain"
    Evidence = "link to updated COF analysis"
}

python cf_cli.py task update T-001 --deviation-json ($deviation | ConvertTo-Json)

Write-Host "✓ Deviation recorded with COF context" -ForegroundColor Yellow
```

**C. If Blocked (UCL Violation Detection):**

```powershell
# 1. Identify UCL violation type
$uclViolation = ./scripts/qse/Detect-UCLViolation.ps1 -ProjectPath "projects/$projectName" -TaskId "T-001"

switch ($uclViolation.Type) {
    "orphaned" {
        Write-Host "✗ UCL Violation: Orphaned context (no parent linkage)" -ForegroundColor Red
        $resolution = "Add parent linkage to sprint/project"
    }
    "cyclical" {
        Write-Host "✗ UCL Violation: Cyclical dependency detected" -ForegroundColor Red
        $resolution = "Break circular dependency chain"
    }
    "incomplete" {
        Write-Host "✗ UCL Violation: Incomplete evidence" -ForegroundColor Red
        $resolution = "Complete evidence bundle generation"
    }
}

# 2. Set task status: blocked
python cf_cli.py task update T-001 `
    --status blocked `
    --blocking-reason "UCL Violation: $($uclViolation.Type)" `
    --blocking-dependencies $uclViolation.Details `
    --ucl-violation-type $uclViolation.Type `
    --cof-dimension-impact ($uclViolation.CofDimensions -join ',')

# 3. Use vibe_check for guidance
Use vibe-check-mcp/vibe_check tool
# Request: UCL compliance restoration strategies with sacred geometry alignment

# 4. Route appropriately
$routeTo = switch ($uclViolation.Type) {
    "orphaned" { "QSE-Planner" }
    "cyclical" { "Architecture-Review" }
    "incomplete" { "QSE-Researcher" }
}
Write-Host "→ Routing to: $routeTo for resolution" -ForegroundColor Cyan

# 5. Resume when unblocked
# (Manual intervention required, then update status)
```

---

### Phase 4: Completion & Sacred Closeout

**Implementation complete when:**

```powershell
# Verify completion criteria
$completionCheck = @{
    TasksCompleted = (Get-TaskManTasks -Status completed).Count -eq $totalTasks
    COFComplete = Test-COFCompleteness -ProjectPath "projects/$projectName"
    SacredGeometryPassed = (Get-SacredGeometryValidation -ProjectPath "projects/$projectName").PassedGates -ge 3
    UCLCompliant = Test-UCLCompliance -ProjectPath "projects/$projectName"
    QualityGatesPassed = Test-QualityGates -ProjectPath "projects/$projectName" -Gate "all"
    EvidenceBundlesComplete = Test-EvidenceBundles -ProjectPath "projects/$projectName"
    QSEArtifactsCommitted = Test-GitStatus -Path "projects/$projectName/.QSE" -ExpectedStatus "clean"
    AgentMemoryUpdated = Test-AgentMemoryEntries -ProjectName $projectName -MinEntries 1
}

$allChecks = $completionCheck.Values | Where-Object { $_ -eq $false }
if ($allChecks.Count -eq 0) {
    Write-Host "✓ All completion criteria met" -ForegroundColor Green
} else {
    Write-Host "✗ Incomplete criteria:" -ForegroundColor Red
    $completionCheck.GetEnumerator() | Where-Object { -not $_.Value } | ForEach-Object {
        Write-Host "  - $($_.Key)" -ForegroundColor Red
    }
    throw "Implementation not complete"
}
```

**Final Actions:**

```powershell
# 1. Generate AAR with complete COF synthesis
./scripts/qse/Create-AAR.ps1 `
    -ProjectPath "projects/$projectName" `
    -WorkId $workId `
    -IncludeCOFSynthesis `
    -IncludeSacredGeometryValidation

$aarPath = "projects/$projectName/.QSE/evidence/aar/AAR-$workId-$(Get-Date -Format 'yyyyMMdd').yaml"
Write-Host "✓ AAR generated: $aarPath" -ForegroundColor Green

# 2. Store project insights in agent memory with COF + Sacred Geometry tags
Use digitarald.agent-memory/memory tool
# Action: create
# Tags: [cof_dimension:holistic, sacred_pattern:all, project:$projectName]
# Content: [complete synthesis from AAR]

# 3. Commit final .QSE/ state with holistic COF validation
git add "projects/$projectName/.QSE/"
git commit -m "docs: AAR for $workId - COF synthesis and Sacred Geometry validation

- All 13 COF dimensions synthesized
- 5/5 Sacred Geometry patterns validated
- UCL compliance verified
- Quality gates passed
- Resonance achieved: business/user/technical harmony
"
git push

Write-Host "✓ Final .QSE/ state committed" -ForegroundColor Green

# 4. Close TaskMan tasks via CF_CLI or MCP with COF completion record
python cf_cli.py task close T-001 `
    --cof-completion-record "projects/$projectName/.QSE/cof-analyses/final-synthesis.yaml" `
    --sacred-geometry-validation "projects/$projectName/.QSE/sacred-geometry/final-validation.yaml"

Write-Host "✓ Tasks closed with COF completion record" -ForegroundColor Green

# 5. Celebrate resonance achievement
Write-Host ""
Write-Host "🎉 Implementation Complete - Resonance Achieved! 🎉" -ForegroundColor Cyan
Write-Host "   Business/User/Technical harmony validated" -ForegroundColor Green
Write-Host "   Sacred Geometry patterns aligned" -ForegroundColor Green
Write-Host "   COF 13-dimensional synthesis complete" -ForegroundColor Green
```

---

## MCP Tool Integration Points (ContextForge-Enhanced)

### Strategic Tool Usage with COF Context

| Phase | MCP Tool | Purpose | ContextForge Integration |
|-------|----------|---------|-------------------------|
| **Every Prompt** | `vibe-check-mcp/constitution_check` | Session integrity | UCL orphan prevention |
| **Phase Transitions** | `vibe-check-mcp/vibe_check` | Pattern interrupt, guidance | Sacred geometry alignment validation |
| **Complex Planning** | `SeqThinking/sequential_thinking` | PAOAL with COF | 13-dimensional synthesis |
| **Alternatives** | `SeqThinking/branched_thinking` | Explore approaches | Sacred pattern comparison |
| **Failures** | `vibe-check-mcp/vibe_learn` | Capture lessons | Spiral learning + agent memory |
| **Knowledge Storage** | `digitarald.agent-memory/memory` | Persist insights | COF-tagged historical context |
| **Historical Context** | `digitarald.agent-memory/memory` | Query patterns | COF similarity matching |
| **Task Management** | TaskMan MCP | Track progress | 64-field schema with COF profile |

---

## Evidence Generation Standards (ContextForge Complete)

### Required Evidence per Task

```yaml
task_evidence:
  metadata:
    task_id: T-001
    work_id: W-0001
    project_id: P-MY-PROJECT
    timestamp: RFC3339
    session_id: QSE-YYYYMMDD-HHMM-UUID
    cof_analysis_id: "implementation-T-001-20251121"
    sacred_patterns: ["circle", "triangle", "spiral"]

  cof_dimensional_analysis:
    # Complete 13-dimensional analysis reference
    baseline: "projects/my-project/.QSE/cof-analyses/implementation-T-001-20251121.yaml"
    dimensions_addressed: 13/13
    depth_quality: "adequate" # ≥200 words per dimension

  sacred_geometry_validation:
    circle_completeness: true
    triangle_stability: true
    spiral_progression: true
    golden_ratio_balance: true
    fractal_consistency: true
    gates_passed: 5/5

  ucl_compliance:
    parent_linkage: "Sprint-2, P-MY-PROJECT"
    no_orphans: true
    no_cycles: true
    evidence_complete: true

  implementation:
    changes:
      - path: "relative/path/to/file"
        change: added|modified|removed
        summary: "Description with COF context"
        lines: 45
        pattern: "Design pattern used (DDD, Repository, etc.)"
    tools_used:
      - tool: "mcp:SeqThinking/sequential_thinking"
        purpose: "COF-guided implementation planning"
      - tool: "cf_cli:task update"
        purpose: "Update task with COF profile"

  validation:
    tests:
      - test_file: "tests/unit/test_module.py"
        status: passed
        coverage: 87%
    quality_gates:
      - gate: "pre-commit"
        checks: ["linting", "unit_tests"]
        status: passed
      - gate: "circle"
        checks: ["completeness"]
        status: passed

  artifacts:
    qse_generated:
      - "projects/my-project/.QSE/test-results/latest-results.xml"
      - "projects/my-project/.QSE/metrics/latest-complexity.json"
      - "projects/my-project/.QSE/cof-analyses/implementation-T-001.yaml"
      - "projects/my-project/.QSE/sacred-geometry/validation-T-001.yaml"
    evidence_bundle: "projects/my-project/.QSE/evidence/implementation-T-001.yaml"

  lessons_learned:
    - insight: "Redis TTL strategy prevented memory issues"
      cof_dimension: "emergent"
      sacred_pattern: "spiral"
      stored_in_memory: true
      memory_id: "mem-12345"
```

---

## QSE Integration (Organic Documentation with COF)

### .QSE/ Directory as Living ContextForge History

All .QSE/ artifacts are **committed to source control** as organic, evolving documentation:

projects/my-project/.QSE/
├── qse-config.yaml              # ✅ Configuration with COF + Sacred Geometry
├── quality-gates/               # ✅ Sacred Geometry gate definitions
│   ├── circle-completeness.yaml
│   ├── triangle-stability.yaml
│   ├── spiral-iteration.yaml
│   ├── golden-ratio-balance.yaml
│   └── fractal-consistency.yaml
├── cof-analyses/                # ✅ NEW: 13-dimensional analyses
│   ├── baseline-{projectId}.yaml
│   ├── implementation-*.yaml
│   └── final-synthesis.yaml
├── sacred-geometry/             # ✅ NEW: Pattern validation records
│   ├── validation-*.yaml
│   └── alignment-reports/
├── test-results/                # ✅ Latest results (committed)
├── metrics/                     # ✅ Quality metrics (committed, COF-tagged)
├── evidence/                    # ✅ Evidence bundles (committed)
│   ├── aar/                     # After Action Reports with COF synthesis
│   └── implementation-*.yaml    # Task evidence with COF + Sacred Geometry
├── reports/                     # ✅ Dashboards (committed)
└── docs/                        # ✅ Documentation

**Evolution Pattern:**

- Each implementation updates COF analysis
- Sacred geometry validation recorded
- UCL compliance verified
- Git history shows quality evolution with COF context
- Evidence bundles link code changes to dimensional impacts

---

## Problem Resolution Protocol (ContextForge-Aware)

### When Blocked (UCL Violation)

```powershell
# 1. Identify UCL Violation Type
$uclViolation = ./scripts/qse/Detect-UCLViolation.ps1 `
    -ProjectPath "projects/$projectName" `
    -TaskId "T-001"

Write-Host "UCL Violation Detected:" -ForegroundColor Red
Write-Host "  Type: $($uclViolation.Type)" -ForegroundColor Yellow
Write-Host "  Details: $($uclViolation.Details)" -ForegroundColor Gray

# 2. Log in TaskMan with COF Context
python cf_cli.py task update T-001 `
    --status blocked `
    --blocking-reason $uclViolation.Reason `
    --blocking-dependencies ($uclViolation.Dependencies -join ',') `
    --ucl-violation-type $uclViolation.Type `
    --cof-dimension-impact ($uclViolation.CofDimensions -join ',')

# 3. Use vibe_check for guidance
Use vibe-check-mcp/vibe_check tool
# Request: UCL compliance restoration strategies with sacred geometry alignment

# 4. Route appropriately
$routingDecision = switch ($uclViolation.Type) {
    "orphaned" {
        @{
            Specialist = "QSE-Planner"
            Action = "Add parent linkage to restore UCL compliance"
            COFFocus = "relational"
        }
    }
    "cyclical" {
        @{
            Specialist = "Architecture-Review"
            Action = "Break circular dependency chain"
            COFFocus = "relational,holistic"
        }
    }
    "incomplete" {
        @{
            Specialist = "QSE-Researcher"
            Action = "Complete evidence bundle generation"
            COFFocus = "all"
        }
    }
}

Write-Host "→ Routing to: $($routingDecision.Specialist)" -ForegroundColor Cyan
Write-Host "  Action: $($routingDecision.Action)" -ForegroundColor Gray
Write-Host "  COF Focus: $($routingDecision.COFFocus)" -ForegroundColor Gray

# 5. Resume when unblocked
# (After manual resolution)
python cf_cli.py task update T-001 --status in_progress
./scripts/qse/Update-COFAnalysis.ps1 -ProjectPath "projects/$projectName" -TaskId "T-001"
Write-Host "✓ Task unblocked, COF analysis updated" -ForegroundColor Green
```

### When Failures Occur (Spiral Learning)

#### MANDATORY: Execute vibe_learn + agent memory storage immediately

```powershell
# 1. Capture failure context
$failureContext = @{
    Issue = "Detailed description of what failed"
    COFDimensionalContext = "Which COF dimensions were involved"
    Phase = "Which implementation phase"
    Environment = "Dev/staging/prod context"
    SacredPatternsAttempted = @("spiral", "triangle")
    AttemptedResolution = "What was tried to fix it"
    LessonLearned = "Specific, actionable takeaway"
    PatternRecognition = "How to recognize this in future"
}

# 2. Use vibe_learn tool
Use vibe-check-mcp/vibe_learn tool
# Capture: $failureContext with complete COF context

# 3. Store in agent memory with COF + Sacred Geometry tags
Use digitarald.agent-memory/memory tool
# Action: create
# Type: insight
# Tags: [
#   cof_dimension: $failureContext.COFDimensionalContext,
#   sacred_pattern: $failureContext.SacredPatternsAttempted,
#   project: $projectName,
#   failure_type: $failureContext.Issue
# ]
# Content: [complete lesson with COF context and resolution path]

Write-Host "✓ Failure captured in agent memory with COF context" -ForegroundColor Yellow
Write-Host "  Memory ID: mem-$(Get-Date -Format 'yyyyMMddHHmm')" -ForegroundColor Gray
```

---

## Success Criteria (ContextForge Complete)

### Implementation Complete

```powershell
# Comprehensive completion validation
$successCriteria = @{
    SessionIntegrity = Test-ConstitutionCheck -AllPrompts
    COFComplete = Test-COFCompleteness -AllDimensions -MinWords 200
    SacredGeometry = Test-SacredGeometryValidation -MinPatterns 3
    UCLCompliance = Test-UCLCompliance -NoViolations
    MCPIntegration = Test-MCPToolUsage -StrategicOnly -WithCOFContext
    TaskManUpdated = Test-TaskManEvidence -Complete
    QSEArtifacts = Test-QSEArtifacts -WithCOFTags -Committed
    QualityGates = Test-QualityGates -Standard -SacredGeometry -AllPassed
    EvidenceBundles = Test-EvidenceBundles -Traceable -COFTagged
    AgentMemory = Test-AgentMemoryStorage -COFTags -PatternTags
    GitHistory = Test-GitHistory -CleanCommits -EvidenceLinks -COFContext
    ResonanceAchieved = Test-Resonance -Business -User -Technical -Validated
    NoBlockers = Test-TaskStatus -NoBlockers -ExplicitDeferrals
}

$passedCriteria = ($successCriteria.Values | Where-Object { $_ }).Count
$totalCriteria = $successCriteria.Count

Write-Host ""
Write-Host "Success Criteria Validation:" -ForegroundColor Cyan
Write-Host "  Passed: $passedCriteria / $totalCriteria" -ForegroundColor $(if ($passedCriteria -eq $totalCriteria) { "Green" } else { "Yellow" })
Write-Host ""

$successCriteria.GetEnumerator() | ForEach-Object {
    $status = if ($_.Value) { "✓" } else { "✗" }
    $color = if ($_.Value) { "Green" } else { "Red" }
    Write-Host "  $status $($_.Key)" -ForegroundColor $color
}

if ($passedCriteria -eq $totalCriteria) {
    Write-Host ""
    Write-Host "🎉 Implementation Complete - All Criteria Met! 🎉" -ForegroundColor Cyan
} else {
    throw "Implementation incomplete: $($totalCriteria - $passedCriteria) criteria not met"
}
```

### Quality Thresholds (ContextForge Standards)

```yaml
quality_requirements:
  # Standard quality metrics
  test_coverage: ">= 80%"
  complexity: "<= 10 cyclomatic"
  documentation: "All public APIs documented"

  # ContextForge-specific metrics
  cof_completeness: "13/13 dimensions addressed"
  cof_depth: "≥200 words per dimension"
  sacred_geometry_compliance: "≥3/5 patterns validated"
  ucl_compliance: "100% (no violations)"

  # Evidence and traceability
  evidence: "100% tasks have evidence bundles with COF tags"
  validation: "All quality gates + sacred geometry gates passed"
  mcp_usage: "Strategic inflection points documented with COF context"
  memory_storage: "Lessons learned persisted with COF + pattern tags"
```

---

## Guardrails (ContextForge Enforced)

```powershell
# Validation guardrails (run before any operation)
function Test-ContextForgeGuardrails {
    param([string]$Operation)

    $violations = @()

    # Constitution check enforcement
    if (-not (Test-ConstitutionCheck -Latest)) {
        $violations += "Constitution check not performed on latest prompt"
    }

    # COF analysis enforcement
    if ($Operation -eq "Implementation" -and -not (Test-COFAnalysis -Complete)) {
        $violations += "COF 13-dimensional analysis incomplete or missing dimensions"
    }

    # Sacred Geometry enforcement
    if ($Operation -in @("Implementation", "Validation") -and -not (Test-SacredGeometry -MinPatterns 3)) {
        $violations += "Sacred Geometry patterns not validated (minimum 3/5 required)"
    }

    # UCL enforcement
    $uclCheck = Test-UCLCompliance
    if (-not $uclCheck.Passed) {
        $violations += "UCL violation: $($uclCheck.Violations -join ', ')"
    }

    # CF_CLI bypass check
    if ($Operation -match "Domain" -and -not $env:VIA_CF_CLI) {
        $violations += "Domain workflow bypassed CF_CLI (use python cf_cli.py)"
    }

    # Evidence generation check
    if ($Operation -eq "Implementation" -and -not (Test-EvidenceGeneration)) {
        $violations += "Evidence generation not configured or incomplete"
    }

    if ($violations.Count -gt 0) {
        Write-Host "✗ Guardrail Violations Detected:" -ForegroundColor Red
        $violations | ForEach-Object {
            Write-Host "  - $_" -ForegroundColor Red
        }
        throw "ContextForge guardrails not satisfied"
    }

    Write-Host "✓ All ContextForge guardrails satisfied" -ForegroundColor Green
}
```

❌ **Never skip constitution_check** on any prompt
❌ **Never bypass COF 13-dimensional analysis** (all dimensions mandatory)
❌ **Never ignore Sacred Geometry patterns** (minimum 3/5 required)
❌ **Never violate UCL** (orphaned/cyclical/incomplete contexts)
❌ **Never bypass CF_CLI** for domain workflows
❌ **Never implement without evidence generation** (with COF tags)
❌ **Never fail without vibe_learn capture** (with COF context)
❌ **Never complete without .QSE/ updates** (COF + Sacred Geometry artifacts)
❌ **Never commit without quality validation** (standard + sacred gates)
❌ **Never block without explicit reasoning** (with COF dimensional analysis)

✅ **Always use STDIO-first** for MCP transport
✅ **Always perform complete COF analysis** (13 dimensions, ≥200 words each)
✅ **Always validate Sacred Geometry** (all 5 patterns, minimum 3 passing)
✅ **Always enforce UCL compliance** (no exceptions)
✅ **Always generate evidence bundles** per task with COF context
✅ **Always commit .QSE/ artifacts** with code changes
✅ **Always store lessons** in agent memory with COF + pattern tags
✅ **Always validate** against quality + sacred geometry gates
✅ **Always log MCP tool usage** for audit trail
✅ **Always achieve resonance** (business/user/technical harmony)

---

**Version**: 2.0 (ContextForge + Agent-Core Complete - PowerShell First)
**Last Updated**: 2025-11-21
**Authority**: agent-core.instructions.md + ContextForge Work Codex + COF + Sacred Geometry + UCL
