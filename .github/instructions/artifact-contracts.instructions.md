---
applyTo: "**"
excludeAgent: "code-review"
---

# Artifact Contracts

## Purpose

Defines YAML contracts for all Triad Orchestrator artifacts. Recorder role MUST follow these schemas exactly.

---

## LayerPlan Contract

**When**: L0 Foundation Layer  
**Role**: Recorder  
**Schema**:

```yaml
layer_id: string                    # "L0", "L1", "L2", etc.
layer_goal: string                  # What this layer accomplishes
personas: [string]                  # List of persona IDs for this layer
dependencies: [string]              # Previous layers this depends on
acceptance_criteria: [string]       # How to verify layer complete
estimated_complexity: string        # "low" | "medium" | "high"
```

**Example**:
```yaml
layer_id: "L0"
layer_goal: "Establish foundation with basic user authentication"
personas: ["security-expert", "backend-architect"]
dependencies: []
acceptance_criteria:
  - "User can register with email and password"
  - "Password hashing implemented"
  - "Unit tests pass"
estimated_complexity: "medium"
```

---

## PersonaPlan Contract

**When**: L0 Foundation Layer (one per persona)  
**Role**: Recorder  
**Schema**:

```yaml
persona_id: string                  # Must match persona-registry.instructions.md
layer_id: string                    # Which layer this persona applies to
context: string                     # Specific context for this persona's work
constraints: [string]               # Limitations or boundaries
focus_areas: [string]               # What this persona concentrates on
```

**Example**:
```yaml
persona_id: "security-expert"
layer_id: "L0"
context: "Authentication and authorization for web application"
constraints:
  - "Must use industry-standard password hashing (bcrypt/argon2)"
  - "No custom crypto implementations"
focus_areas:
  - "Password storage security"
  - "Session management"
  - "Input validation"
```

---

## Implementation Artifact Contract

**When**: L1+ Implementation Layers  
**Role**: Recorder  
**Schema**:

```yaml
layer_id: string                    # "L1", "L2", etc.
implementation_summary: string      # Brief description of what was implemented
files_modified: [string]            # List of file paths changed
tests_added: [string]               # List of test files created/modified
technical_decisions: [string]       # Key technical choices made
known_issues: [string]              # Any issues or limitations
```

**Example**:
```yaml
layer_id: "L1"
implementation_summary: "Implemented user registration endpoint with password hashing"
files_modified:
  - "src/routes/auth.ts"
  - "src/models/user.ts"
  - "src/middleware/validation.ts"
tests_added:
  - "tests/routes/auth.test.ts"
  - "tests/models/user.test.ts"
technical_decisions:
  - "Used bcrypt with cost factor 12"
  - "Email validation via regex + DNS check"
  - "Rate limiting: 5 attempts per 15 minutes"
known_issues:
  - "Email confirmation not yet implemented"
```

---

## PersonaRegistryProposal Contract

**When**: Missing capability detected  
**Role**: Recorder  
**Schema**:

```yaml
proposed_persona_id: string         # Proposed ID (kebab-case)
justification: string               # Why this persona is needed
expertise_areas: [string]           # Domain expertise this persona provides
typical_constraints: [string]       # Common limitations or boundaries
example_use_cases: [string]         # Scenarios where this persona applies
similar_existing_personas: [string] # Related personas in registry (if any)
```

**Example**:
```yaml
proposed_persona_id: "blockchain-integration-expert"
justification: "Need expertise in blockchain smart contract integration for payment processing"
expertise_areas:
  - "Ethereum/Solidity smart contracts"
  - "Web3 integration patterns"
  - "Cryptocurrency payment processing"
typical_constraints:
  - "Gas optimization required"
  - "Must handle network latency and failures"
  - "Testnet validation before mainnet deployment"
example_use_cases:
  - "Integrate cryptocurrency payments"
  - "Implement NFT minting functionality"
  - "Build DAO governance features"
similar_existing_personas: []
```

---

## Output Ordering Rules

### Executor Output (Bullets Only)
```
**Executor**: Implementation Steps
- [ ] Step 1: Description
- [ ] Step 2: Description
- [ ] Step 3: Description
```

### Critic Output (Bullets Only)
```
**Critic**: Challenges & Validations
- ⚠️ Challenge 1: Description
- ✅ Validation 1: Description
- ⚠️ Challenge 2: Description
```

### Recorder Output (YAML Only)
````
**Recorder**: Layer Artifacts

```yaml
# LayerPlan, PersonaPlan, or Implementation artifacts
# NO bullet points, ONLY YAML
```
````

---

## Artifact Generation Rules

1. **Recorder outputs YAML only**: No bullets, no prose, ONLY YAML blocks
2. **One artifact per YAML block**: Do not mix LayerPlan with PersonaPlan
3. **Schema compliance**: Follow contracts exactly, all required fields present
4. **Examples as templates**: Use contract examples as starting point
5. **No silent modifications**: PersonaRegistry edits require PersonaRegistryProposal

---

## Validation Checklist

Before outputting Recorder artifacts:
- ✅ YAML syntax valid
- ✅ All required fields present
- ✅ Field values match expected types (string, [string], etc.)
- ✅ persona_id values exist in persona-registry.instructions.md
- ✅ layer_id values follow "L0", "L1", "L2" format
- ✅ No bullet points in YAML blocks
- ✅ No prose mixed with YAML

---

## Cross-References

- **Persona IDs**: See `persona-registry.instructions.md` for valid values
- **Persona selection rules**: See `persona-selection.instructions.md`
- **Workflow phases**: See `triad-relay-core.instructions.md`
- **Growth triggers**: See `persona-growth.instructions.md`
