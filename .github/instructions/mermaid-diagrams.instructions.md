---
applyTo: "diagram*, mermaid*, visual*, flow*, chart*, erd*, entity*, sequence*, state*"
description: "Mermaid diagram templates and usage guide for ContextForge agents"
version: "1.0"
---

# ContextForge Mermaid Diagram Guide

**Purpose**: Visual communication for workflows, decisions, data models, and processes

**Tool**: vscode.mermaid-chat-features/renderMermaidDiagram (available in orchestrator)

---

## When to Create Diagrams

### ALWAYS Create Diagrams For:
- [ ] COMPLEX workflow routing (6+ steps or multiple decision points)
- [ ] Data model design (3+ entities with relationships)
- [ ] Multi-agent handoff sequences
- [ ] PAOAL phase transitions (state diagrams)
- [ ] Complexity classification logic (decision trees)
- [ ] VECTOR analysis workflow
- [ ] Sacred Geometry validation flow

### OPTIONAL Diagrams For:
- [ ] SIMPLE workflows (can describe in text)
- [ ] Binary decisions (yes/no)
- [ ] Single-agent operations

---

## Diagram Types & Templates

### 1. Flowchart - Process Workflows

**When to Use**: PAOAL execution, agent workflows, implementation processes

**Template**:
```mermaid
flowchart TD
    Start([Start: User Request]) --> Classify{Classify<br/>Complexity}
    
    Classify -->|SIMPLE| Simple[Lightweight PAOAL]
    Classify -->|MEDIUM| Medium[Full PAOAL]
    Classify -->|COMPLEX| Complex[PAOAL + COF]
    
    Simple --> Executor[Executor Implements]
    Medium --> Executor
    Complex --> Architect[Architect Designs] --> Executor
    
    Executor --> Tests{Tests<br/>Pass?}
    
    Tests -->|Yes| Critic[Critic Validates]
    Tests -->|No| Fix[Fix Issues] --> Tests
    
    Critic --> VECTOR{VECTOR<br/>5/6 Pass?}
    
    VECTOR -->|Yes| SG[Sacred Geometry Check]
    VECTOR -->|No| Changes[Request Changes] --> Executor
    
    SG --> SGPass{3/5<br/>Gates Pass?}
    
    SGPass -->|Yes| Recorder[Recorder Documents]
    SGPass -->|No| Changes
    
    Recorder --> AAR[Conduct AAR]
    AAR --> Learnings[Extract Learnings]
    Learnings --> End([Complete])
    
    style Start fill:#e1f5e1
    style End fill:#e1f5e1
    style Tests fill:#fff3cd
    style VECTOR fill:#fff3cd
    style SGPass fill:#fff3cd
    style Critic fill:#d1ecf1
    style Recorder fill:#d1ecf1
```

**Usage**:
```markdown
**@orchestrator creates workflow diagram**:

Here's the complete workflow for this MEDIUM complexity task:

[Insert Mermaid flowchart above]

This shows: User → Classify → Executor → Critic (VECTOR + SG) → Recorder → Complete
```

---

### 2. Decision Matrix - Complexity Classification

**When to Use**: Routing decisions, complexity analysis, multi-factor decisions

**Template**:
```mermaid
flowchart TD
    Start([Task Analysis]) --> Files{Estimate<br/>Files}
    
    Files -->|≤2| CheckFamiliar{Technology<br/>Familiar?}
    Files -->|3-5| CheckArch{Architectural<br/>Change?}
    Files -->|>5| Complex[COMPLEX]
    
    CheckFamiliar -->|Yes| CheckRisk{Risk<br/>Level?}
    CheckFamiliar -->|No| Medium[MEDIUM]
    
    CheckRisk -->|Low| Simple[SIMPLE]
    CheckRisk -->|Med/High| Medium
    
    CheckArch -->|Yes| Complex
    CheckArch -->|No| CheckIntegration{Cross-System<br/>Integration?}
    
    CheckIntegration -->|Yes| Complex
    CheckIntegration -->|No| Medium
    
    Simple --> RouteSimple[Route: Executor → Critic → Recorder]
    Medium --> RouteMedium[Route: Executor → Critic → Recorder<br/>Full PAOAL Required]
    Complex --> RouteComplex[Route: Docs → Arch → Executor → Critic → Recorder<br/>PAOAL + COF + ADR Required]
    
    RouteSimple --> End([Workflow Planned])
    RouteMedium --> End
    RouteComplex --> End
    
    style Simple fill:#d4edda
    style Medium fill:#fff3cd
    style Complex fill:#f8d7da
    style End fill:#e1f5e1
```

**Usage**:
```markdown
**@orchestrator uses decision matrix for classification**:

Analyzing task complexity using decision matrix:

[Insert decision matrix diagram]

Result: 
- Files: 4 (3-5 range)
- Architectural: No
- Integration: No
→ Classification: MEDIUM
→ Route: Executor → Critic → Recorder with full PAOAL
```

---

### 3. Entity Relationship Diagram - Data Models

**When to Use**: Database design, data model documentation, relationship mapping

**Template**:
```mermaid
erDiagram
    USER ||--o{ TASK : creates
    USER ||--o{ LEARNING : captures
    USER {
        string user_id PK
        string name
        string email
        datetime created_at
    }
    
    TASK ||--o{ IMPLEMENTATION : has
    TASK ||--|| COMPLEXITY : classified_as
    TASK {
        string task_id PK
        string title
        string description
        string complexity
        string status
        datetime created_at
    }
    
    IMPLEMENTATION ||--|| PAOAL_EVIDENCE : generates
    IMPLEMENTATION ||--|| VECTOR_ANALYSIS : validated_by
    IMPLEMENTATION ||--|| SACRED_GEOMETRY : validated_by
    IMPLEMENTATION {
        string impl_id PK
        string task_id FK
        int estimated_loc
        int actual_loc
        float ratio
        datetime completed_at
    }
    
    PAOAL_EVIDENCE {
        string evidence_id PK
        string impl_id FK
        json plan
        json act
        json observe
        json adapt
        json log
    }
    
    VECTOR_ANALYSIS {
        string vector_id PK
        string impl_id FK
        boolean validation_pass
        boolean execution_pass
        boolean coherence_pass
        boolean throughput_pass
        boolean observability_pass
        boolean resilience_pass
        int dimensions_passed
    }
    
    SACRED_GEOMETRY {
        string sg_id PK
        string impl_id FK
        boolean circle_pass
        boolean triangle_pass
        boolean spiral_pass
        boolean golden_ratio_pass
        boolean fractal_pass
        int gates_passed
    }
    
    LEARNING ||--o{ PATTERN : extracted_to
    LEARNING {
        string learning_id PK
        string task_id FK
        string category
        text lesson
        int times_referenced
        int times_prevented_issue
        float effectiveness_score
        datetime created_at
    }
    
    PATTERN {
        string pattern_id PK
        string name
        text description
        text when_to_use
        string reusability
    }
```

**Usage**:
```markdown
**@recorder documents data model**:

Here's the complete data model for ContextForge implementation tracking:

[Insert ERD diagram]

Key relationships:
- USER creates many TASKS
- TASK has one IMPLEMENTATION
- IMPLEMENTATION generates PAOAL_EVIDENCE, VECTOR_ANALYSIS, SACRED_GEOMETRY
- IMPLEMENTATION may generate LEARNINGS
- LEARNINGS may be extracted to PATTERNS
```

---

### 4. Sequence Diagram - Agent Handoffs

**When to Use**: Multi-agent interactions, handoff protocols, communication flows

**Template**:
```mermaid
sequenceDiagram
    participant User
    participant Orchestrator
    participant Executor
    participant Critic
    participant Recorder
    participant VibLearn as vibe_learn MCP
    participant Memory as agent-memory MCP
    
    User->>Orchestrator: Implement password reset
    
    activate Orchestrator
    Orchestrator->>Orchestrator: Classify complexity → MEDIUM
    Orchestrator->>Orchestrator: Use sequential_thinking for plan
    Orchestrator->>Executor: Implement with PAOAL framework
    deactivate Orchestrator
    
    activate Executor
    Executor->>Executor: PAOAL Plan (sequential_thinking)
    Executor->>Executor: PAOAL Act (propose edits)
    Executor->>User: Approve edits?
    User->>Executor: Approved ✅
    Executor->>Executor: PAOAL Observe (run tests)
    Executor->>User: Approve test command?
    User->>Executor: Approved ✅
    Executor->>Executor: Tests: 14/14 passing ✅
    Executor->>Executor: PAOAL Adapt (optimize)
    Executor->>Executor: PAOAL Log (evidence bundle)
    Executor->>Critic: Review implementation + evidence
    deactivate Executor
    
    activate Critic
    Critic->>Critic: Coordinate 6 VECTOR subagents
    Critic->>Critic: VECTOR analysis: 6/6 passed ✅
    Critic->>Critic: Sacred Geometry: 5/5 passed ✅
    Critic->>Critic: Verdict: APPROVED
    Critic->>Recorder: Document + AAR + learnings
    deactivate Critic
    
    activate Recorder
    Recorder->>Recorder: Update CHANGELOG
    Recorder->>Recorder: Create YAML artifact
    Recorder->>Recorder: Conduct AAR
    Recorder->>Recorder: Extract learnings
    
    Recorder->>VibLearn: vibe_learn(lesson, pattern)
    VibLearn-->>Recorder: Stored ✅
    
    Recorder->>Memory: store(learning_id, content)
    Memory-->>Recorder: Stored ✅
    
    Recorder->>Recorder: Create learning file
    Recorder->>Orchestrator: Documentation complete
    deactivate Recorder
    
    activate Orchestrator
    Orchestrator->>User: ✅ Implementation complete<br/>VECTOR: 6/6, SG: 5/5<br/>Learnings: 2 captured, 1 pattern
    deactivate Orchestrator
```

**Usage**:
```markdown
**@orchestrator visualizes agent handoff sequence**:

Here's the complete agent interaction flow for this implementation:

[Insert sequence diagram]

This shows:
1. Orchestrator classifies and plans
2. Executor implements with PAOAL (user approvals at gates)
3. Critic validates with VECTOR + Sacred Geometry
4. Recorder documents with AAR + triple storage
5. Orchestrator confirms completion
```

---

### 5. State Diagram - PAOAL Phases

**When to Use**: State transitions, phase workflows, status tracking

**Template**:
```mermaid
stateDiagram-v2
    [*] --> Planning
    
    Planning --> Acting: Plan approved
    Planning --> Planning: Refine approach
    
    state Planning {
        [*] --> AnalyzeRequirements
        AnalyzeRequirements --> UseSequentialThinking
        UseSequentialThinking --> DocumentApproach
        DocumentApproach --> EstimateLOC
        EstimateLOC --> IdentifyRisks
        IdentifyRisks --> [*]
    }
    
    Acting --> Observing: Implementation complete
    Acting --> Acting: Continue implementation
    
    state Acting {
        [*] --> ProposeEdits
        ProposeEdits --> UserApproval
        UserApproval --> ApplyEdits: Approved
        UserApproval --> ProposeEdits: Rejected
        ApplyEdits --> CommitChanges
        CommitChanges --> AddTests
        AddTests --> [*]
    }
    
    Observing --> Adapting: Issues found
    Observing --> Logging: All checks pass
    Observing --> Acting: Critical failure
    
    state Observing {
        [*] --> RunTests
        RunTests --> CheckCoverage
        CheckCoverage --> RunLinting
        RunLinting --> ValidateCriteria
        ValidateCriteria --> [*]
    }
    
    Adapting --> Observing: Fixes applied
    Adapting --> Adapting: Continue fixing
    
    state Adapting {
        [*] --> RootCauseAnalysis
        RootCauseAnalysis --> ImplementFixes
        ImplementFixes --> Optimize
        Optimize --> Refactor
        Refactor --> [*]
    }
    
    Logging --> [*]: Evidence complete
    
    state Logging {
        [*] --> GenerateEvidence
        GenerateEvidence --> CaptureDeviations
        CaptureDeviations --> ExtractLessons
        ExtractLessons --> StoreLearnings
        StoreLearnings --> [*]
    }
```

**Usage**:
```markdown
**@executor shows PAOAL state transitions**:

Here's the PAOAL execution flow with state transitions:

[Insert state diagram]

Current state: Acting → Observing
Next: Run tests, check coverage, validate criteria
```

---

### 6. Flowchart - VECTOR Analysis Workflow

**When to Use**: VECTOR validation process, dimensional analysis flow

**Template**:
```mermaid
flowchart TD
    Start([Implementation<br/>Received]) --> CoordSubagents[Coordinate 6<br/>VECTOR Subagents]
    
    CoordSubagents --> V[Validation Subagent]
    CoordSubagents --> E[Execution Subagent]
    CoordSubagents --> C[Coherence Subagent]
    CoordSubagents --> T[Throughput Subagent]
    CoordSubagents --> O[Observability Subagent]
    CoordSubagents --> R[Resilience Subagent]
    
    V --> VCheck{Input/Output<br/>Validated?}
    VCheck -->|Yes| VPass[V: ✅ PASS]
    VCheck -->|No| VFail[V: ❌ FAIL]
    
    E --> ECheck{Error Handling<br/>Complete?}
    ECheck -->|Yes| EPass[E: ✅ PASS]
    ECheck -->|No| EFail[E: ❌ FAIL]
    
    C --> CCheck{Architecture<br/>Consistent?}
    CCheck -->|Yes| CPass[C: ✅ PASS]
    CCheck -->|No| CFail[C: ❌ FAIL]
    
    T --> TCheck{Performance<br/>Acceptable?}
    TCheck -->|Yes| TPass[T: ✅ PASS]
    TCheck -->|No| TFail[T: ❌ FAIL]
    
    O --> OCheck{Logging<br/>Complete?}
    OCheck -->|Yes| OPass[O: ✅ PASS]
    OCheck -->|No| OFail[O: ❌ FAIL]
    
    R --> RCheck{Fault Tolerance<br/>Implemented?}
    RCheck -->|Yes| RPass[R: ✅ PASS]
    RCheck -->|No| RFail[R: ❌ FAIL]
    
    VPass --> Synthesize
    VFail --> Synthesize
    EPass --> Synthesize
    EFail --> Synthesize
    CPass --> Synthesize
    CFail --> Synthesize
    TPass --> Synthesize
    TFail --> Synthesize
    OPass --> Synthesize
    OFail --> Synthesize
    RPass --> Synthesize
    RFail --> Synthesize
    
    Synthesize[Use sequential_thinking<br/>to Synthesize Findings] --> Count{Count<br/>Dimensions<br/>Passed}
    
    Count -->|5-6/6| Approve[VECTOR: APPROVE]
    Count -->|4/6| RequestChanges[VECTOR: REQUEST CHANGES]
    Count -->|<4/6| Block[VECTOR: BLOCK]
    
    Approve --> SG[Sacred Geometry<br/>Validation]
    RequestChanges --> SG
    Block --> SG
    
    SG --> Report[Generate<br/>VECTOR Report]
    Report --> End([Hand to Recorder])
    
    style VPass fill:#d4edda
    style EPass fill:#d4edda
    style CPass fill:#d4edda
    style TPass fill:#d4edda
    style OPass fill:#d4edda
    style RPass fill:#d4edda
    style VFail fill:#f8d7da
    style EFail fill:#f8d7da
    style CFail fill:#f8d7da
    style TFail fill:#f8d7da
    style OFail fill:#f8d7da
    style RFail fill:#f8d7da
    style Approve fill:#d4edda
    style Block fill:#f8d7da
```

**Usage**:
```markdown
**@critic shows VECTOR analysis workflow**:

Here's the systematic VECTOR validation process:

[Insert VECTOR flowchart]

Current status:
- V: ✅ PASS (all inputs validated)
- E: ✅ PASS (error handling complete)
- C: ✅ PASS (architecture consistent)
- T: ✅ PASS (performance acceptable)
- O: ⚠️ WARN (missing state logging)
- R: ✅ PASS (fault tolerance implemented)

Result: 5/6 passed → APPROVE (with logging recommendation)
```

---

### 7. Flowchart - Sacred Geometry Validation

**When to Use**: 5-gate validation process

**Template**:
```mermaid
flowchart TD
    Start([VECTOR Analysis<br/>Complete]) --> Circle{Circle Gate<br/>Completeness<br/>4/4?}
    
    Circle -->|Yes| CirclePass[Circle: ✅]
    Circle -->|No| CircleFail[Circle: ❌]
    
    CirclePass --> Triangle
    CircleFail --> Triangle
    
    Triangle{Triangle Gate<br/>Stability<br/>3/3?}
    
    Triangle -->|Yes| TrianglePass[Triangle: ✅]
    Triangle -->|No| TriangleFail[Triangle: ❌]
    
    TrianglePass --> Spiral
    TriangleFail --> Spiral
    
    Spiral{Spiral Gate<br/>Learning<br/>2/3?}
    
    Spiral -->|Yes| SpiralPass[Spiral: ✅]
    Spiral -->|No| SpiralWarn[Spiral: ⚠️]
    
    SpiralPass --> GoldenRatio
    SpiralWarn --> GoldenRatio
    
    GoldenRatio{Golden Ratio Gate<br/>Balance<br/>3/3?}
    
    GoldenRatio -->|Yes| GoldenPass[Golden Ratio: ✅]
    GoldenRatio -->|No| GoldenFail[Golden Ratio: ❌]
    
    GoldenPass --> Fractal
    GoldenFail --> Fractal
    
    Fractal{Fractal Gate<br/>Consistency<br/>3/3?}
    
    Fractal -->|Yes| FractalPass[Fractal: ✅]
    Fractal -->|No| FractalFail[Fractal: ❌]
    
    FractalPass --> Count
    FractalFail --> Count
    
    Count[Count Gates Passed] --> Minimum{≥3 Gates<br/>Passed?}
    
    Minimum -->|Yes| Pass[Sacred Geometry:<br/>PASS]
    Minimum -->|No| Fail[Sacred Geometry:<br/>FAIL]
    
    Pass --> Report[Generate SG Report]
    Fail --> Report
    
    Report --> CombineVerdict{Combine<br/>VECTOR + SG}
    
    CombineVerdict --> FinalVerdict[Final Verdict:<br/>APPROVE/CHANGES/BLOCK]
    
    FinalVerdict --> End([Hand to Recorder])
    
    style CirclePass fill:#d4edda
    style TrianglePass fill:#d4edda
    style SpiralPass fill:#d4edda
    style GoldenPass fill:#d4edda
    style FractalPass fill:#d4edda
    style Pass fill:#d4edda
    style CircleFail fill:#f8d7da
    style TriangleFail fill:#f8d7da
    style GoldenFail fill:#f8d7da
    style FractalFail fill:#f8d7da
    style Fail fill:#f8d7da
    style SpiralWarn fill:#fff3cd
```

**Usage**:
```markdown
**@critic shows Sacred Geometry validation flow**:

Here's the 5-gate Sacred Geometry validation:

[Insert SG flowchart]

Results:
- Circle: ✅ (4/4 complete)
- Triangle: ✅ (3/3 stable)
- Spiral: ✅ (2/3 learning captured)
- Golden Ratio: ✅ (3/3 balanced)
- Fractal: ✅ (3/3 consistent)

Gates passed: 5/5 ✅ (exceeds minimum 3/5)
Sacred Geometry: PASS
```

---

### 8. Gantt Chart - Project Timeline

**When to Use**: Sprint planning, milestone tracking, phase scheduling

**Template**:
```mermaid
gantt
    title ContextForge MVP v3.0 Implementation
    dateFormat YYYY-MM-DD
    
    section Gate 1 - Foundation
    Enhance copilot-instructions.md     :done, g1-1, 2025-12-30, 1d
    Create instruction modules           :done, g1-2, 2025-12-31, 1d
    Update agent files with UCL          :active, g1-3, 2026-01-01, 2d
    Test Gate 1.1 validation            :g1-4, after g1-3, 1d
    
    section Gate 2 - Validation
    Enhance Critic with VECTOR          :crit, g2-1, 2026-01-04, 2d
    Enhance Executor with PAOAL         :g2-2, 2026-01-04, 2d
    Implement 5-gate framework          :g2-3, after g2-1, 1d
    Test validation workflows           :g2-4, after g2-2 g2-3, 2d
    
    section Gate 3 - Production
    Handoff templates (top 6)           :g3-1, 2026-01-10, 2d
    Comprehensive testing               :g3-2, after g3-1, 3d
    Documentation complete              :g3-3, after g3-2, 1d
    Production readiness                :milestone, g3-4, after g3-3, 0d
```

**Usage**:
```markdown
**@orchestrator shows project timeline**:

Here's the complete implementation timeline for MVP v3.0:

[Insert Gantt chart]

Current status: Gate 1.3 (update agent files) - Day 2 of 2
Next: Gate 1.4 (validation testing) starts tomorrow
```

---

## Integration with Agents

### Orchestrator
**Uses Mermaid for**:
- Complexity classification decision trees
- Workflow routing diagrams
- Project timelines (Gantt)
- Agent handoff sequences

### Executor
**Uses Mermaid for**:
- PAOAL state transitions
- Implementation workflow
- Data model ERDs (when designing)

### Critic
**Uses Mermaid for**:
- VECTOR analysis workflow
- Sacred Geometry validation flow
- Issue dependency graphs

### Recorder
**Uses Mermaid for**:
- AAR process flow
- Learning lifecycle
- Pattern extraction workflow
- Data model documentation (ERDs)

---

## Best Practices

### 1. Keep Diagrams Simple
- ❌ 20+ nodes (too complex)
- ✅ 5-15 nodes (optimal)
- If >15 nodes: Break into multiple diagrams

### 2. Use Consistent Styling
```mermaid
flowchart TD
    Success[Step] 
    Warning[Step]
    Error[Step]
    
    style Success fill:#d4edda
    style Warning fill:#fff3cd
    style Error fill:#f8d7da
```

**Color Palette**:
- Green (#d4edda): Success, pass, complete
- Yellow (#fff3cd): Warning, partial, in-progress
- Red (#f8d7da): Error, fail, blocked
- Blue (#d1ecf1): Info, process, neutral
- Gray (#e9ecef): Background, inactive

### 3. Include Legend (if needed)
```mermaid
flowchart LR
    subgraph Legend
        Success[✅ Pass]
        Warning[⚠️ Warn]
        Error[❌ Fail]
    end
    
    style Success fill:#d4edda
    style Warning fill:#fff3cd
    style Error fill:#f8d7da
```

### 4. Progressive Disclosure
- High-level diagram first (workflow overview)
- Detailed diagrams on request (specific phase breakdown)

### 5. Embed in Documentation
- Always include text explanation before/after diagram
- Reference diagram in markdown artifacts
- Store diagram source in code blocks for reproducibility

---

## Quick Reference

### Diagram Selection Guide

| Need to Show | Diagram Type | Example |
|--------------|-------------|---------|
| Process flow | Flowchart | PAOAL execution, VECTOR analysis |
| Decision logic | Flowchart (diamond nodes) | Complexity classification |
| Agent interactions | Sequence diagram | Executor → Critic → Recorder |
| State transitions | State diagram | PAOAL phases, task status |
| Data relationships | ERD | Learning → Pattern, Task → Implementation |
| Timeline | Gantt chart | Sprint planning, milestone tracking |
| Hierarchy | Flowchart (tree structure) | Agent specialization, subagent coordination |

---

## Version

**Document**: ContextForge Mermaid Diagram Guide  
**Version**: 1.0  
**Last Updated**: 2025-12-31  
**Use**: Visual communication for all ContextForge agents
