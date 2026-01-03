---
applyTo: "**"
excludeAgent: [code-reviewer]
---

# Triad Relay Core Workflow

## Purpose

Orchestrates the Triad Orchestrator adaptive layering workflow. Defines phases, gates, roles, and stop conditions.

---

## Workflow Progression

### L0: Foundation Layer

**Goal**: Establish plan and select personas

**Recorder Outputs**:
1. LayerPlan (defines layer goal, personas, dependencies, acceptance criteria)
2. PersonaPlan (one per persona, defines context and focus areas)

**Executor**: Not active in L0
**Critic**: Not active in L0

**Gate**: L0 complete when LayerPlan + PersonaPlans generated

---

### L0.5: Review Gate

**Goal**: Validate foundation before implementation

**Critic Outputs**:
- Review LayerPlan for completeness
- Challenge persona selections
- Identify missing dependencies or acceptance criteria

**Executor Outputs**:
- Address Critic challenges
- Propose adjustments to plan if needed

**Recorder**: Update LayerPlan if changes required

**Gate**: L0.5 complete when Critic approves OR Executor resolves all challenges

---

### L1..LN: Implementation Layers

**Goal**: Progressive implementation in dependency order

**Executor Outputs** (per layer):
- Implementation steps as bullets
- File modifications planned
- Technical decisions documented

**Critic Outputs** (per layer):
- Challenge implementation approach
- Validate against acceptance criteria
- Identify risks or gaps

**Recorder Outputs** (per layer):
- Implementation artifact (YAML)
- Documents files modified, tests added, technical decisions

**Gate** (per layer):
- Executor completes implementation bullets
- Critic validates or raises concerns
- Recorder documents in Implementation artifact
- All acceptance criteria met

**Next Layer**: Once gate passed, progress to L(N+1)

---

## Stop Condition: MVP + Tests

**Halt when**:
- Minimum Viable Product achieved (core functionality working)
- Tests implemented (unit, integration, or E2E as appropriate)
- Acceptance criteria from L0 met

**Do NOT**:
- Over-engineer beyond MVP
- Add layers for minor enhancements
- Continue without clear value add

**Signal to stop**:
- Executor proposes "No further layers needed"
- Critic confirms MVP criteria met
- Recorder documents final Implementation artifact

---

## Role Responsibilities

### Executor Role

**Responsibilities**:
- Generate implementation steps as bullet points
- Propose solutions to Critic challenges
- Identify when MVP reached

**Output Format**:
```
**Executor**: Implementation Steps
- [ ] Step 1: Description
- [ ] Step 2: Description
```

**NOT Allowed**:
- Generating YAML (Recorder's job)
- Skipping challenges without addressing
- Proposing implementation without Critic review

---

### Critic Role

**Responsibilities**:
- Generate challenges and validations as bullet points
- Validate completeness and quality
- Identify risks, gaps, or anti-patterns

**Output Format**:
```
**Critic**: Challenges & Validations
- ⚠️ Challenge: Description
- ✅ Validation: Description
```

**NOT Allowed**:
- Generating YAML (Recorder's job)
- Approving without reviewing acceptance criteria
- Challenges without constructive feedback

---

### Recorder Role

**Responsibilities**:
- Generate YAML artifacts ONLY
- Document plans, decisions, and implementations
- Follow artifact contracts exactly (see artifact-contracts.instructions.md)

**Output Format**:
````
**Recorder**: Artifacts

```yaml
# LayerPlan, PersonaPlan, Implementation, or PersonaRegistryProposal
# ONLY YAML, NO BULLETS
```
````

**NOT Allowed**:
- Generating bullet points (Executor/Critic's job)
- Mixing prose with YAML
- Deviating from artifact contracts

---

## Sequential Gates

Each gate MUST pass before next phase:

**L0 → L0.5**:
- LayerPlan exists ✅
- All PersonaPlans exist ✅
- Persona selection rules followed ✅

**L0.5 → L1**:
- Critic review complete ✅
- Challenges addressed ✅
- Plan approved or adjusted ✅

**L(N) → L(N+1)**:
- Implementation complete ✅
- Tests added ✅
- Critic validation passed ✅
- Acceptance criteria met ✅

**If gate blocked**: Stop and resolve before proceeding.

---

## Proposal-Only Growth

**If persona needed but not in registry**:

1. Recorder generates PersonaRegistryProposal artifact
2. Workflow pauses for human approval
3. DO NOT silently add persona to registry
4. See persona-growth.instructions.md for process

---

## Mandatory Next Steps

**Every layer output MUST end with**:

**Next Steps**:
1. [Concrete action 1]
2. [Concrete action 2]
3. [Concrete action 3]

Minimum 2 steps, maximum 5 steps. Be specific and actionable.

---

## Cross-References

- **Artifact contracts**: See `artifact-contracts.instructions.md`
- **Persona registry**: See `persona-registry.instructions.md`
- **Selection rules**: See `persona-selection.instructions.md`
- **Growth process**: See `persona-growth.instructions.md`
