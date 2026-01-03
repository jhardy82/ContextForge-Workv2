---
applyTo: "**"
description: "Context Ontology Framework (COF) 13D and Universal Context Law (UCL) enforcement"
---

# COF & UCL Enforcement

**Authority**: [03-Context-Ontology-Framework.md](../../docs/03-Context-Ontology-Framework.md)

---

## Context Ontology Framework (COF) - 13 Dimensions

**Every significant context must be analyzed across 13 ontological dimensions.**

### Core Dimensions (1-5)

#### 1. Motivational Context
**Focus**: Purpose and driving forces
**Questions**: Why does this exist? What problem does it solve? What value does it create?
**Application**: Business alignment, goal setting, stakeholder buy-in

#### 2. Relational Context
**Focus**: Dependencies and cross-links
**Questions**: What does this depend on? What depends on this? How does it connect to the system?
**Application**: Dependency mapping, integration planning, impact analysis

#### 3. Situational Context
**Focus**: Environmental conditions and constraints
**Questions**: What are the current conditions? What constraints exist? What opportunities are present?
**Application**: Risk assessment, constraint identification, opportunity analysis

#### 4. Resource Context
**Focus**: Available time, skill, and tools
**Questions**: What resources are available? What skills are needed? What tools can we use?
**Application**: Resource allocation, capacity planning, tool selection

#### 5. Narrative Context
**Focus**: Business case and communication framing
**Questions**: How do we tell this story? Who needs to know? What's the business case?
**Application**: Stakeholder communication, documentation, business case development

### Advanced Dimensions (6-10)

#### 6. Recursive Context
**Focus**: Feedback cycles and iteration patterns
**Questions**: What feedback loops exist? How do we iterate? What lessons feed forward?
**Application**: Continuous improvement, iteration planning, learning cycles

#### 7. Computational Context
**Focus**: Algorithms and processing efficiency
**Questions**: What algorithms apply? What's the computational complexity? How do we optimize?
**Application**: Performance optimization, algorithm selection, efficiency analysis

#### 8. Emergent Context
**Focus**: Unexpected interactions and novel outcomes
**Questions**: What might emerge? What interactions could occur? What's unpredictable?
**Application**: Risk identification, innovation opportunities, system behavior prediction

#### 9. Temporal Context
**Focus**: Timing, sequencing, and deadlines
**Questions**: When must this happen? What's the sequence? What are the time constraints?
**Application**: Timeline planning, scheduling, dependency sequencing

#### 10. Spatial Context
**Focus**: Distribution across teams and environments
**Questions**: Where does this exist? How is it distributed? What geographic factors apply?
**Application**: Distributed systems, team coordination, geographic constraints

### Integration Dimensions (11-13)

#### 11. Holistic Context
**Focus**: System-wide integration and synthesis
**Questions**: How does this fit the whole? What's the broader impact? How do parts relate?
**Application**: Systems thinking, big-picture analysis, integration planning

#### 12. Validation Context
**Focus**: Evidence that requirements are met
**Questions**: How do we validate? What evidence is needed? How do we measure success?
**Application**: Testing strategy, acceptance criteria, quality gates

#### 13. Integration Context
**Focus**: How it fits back into the whole
**Questions**: How does this reintegrate? What handoffs are needed? How do we maintain coherence?
**Application**: Integration planning, handoff protocols, system coherence

---

## Universal Context Law (UCL)

### The Law

**"No orphaned, cyclical, or incomplete context may persist in the system."**

### Three Requirements

#### 1. No Orphans
**Requirement**: Every context must be anchored to at least one parent project or initiative.

**Validation**:
```sql
SELECT * FROM contexts
WHERE parent_id IS NULL
AND context_type != 'root_project';
```

**Fix**: Link orphaned contexts to appropriate parent or archive if obsolete.

#### 2. No Cycles
**Requirement**: Context relationships must flow toward resolution or transformation, never creating circular dependencies.

**Validation**:
```python
def detect_cycles(context_graph):
    visited = set()
    rec_stack = set()

    for node in context_graph.nodes():
        if detect_cycle_util(node, visited, rec_stack):
            return True  # Cycle detected
    return False
```

**Fix**: Break circular dependencies by introducing intermediate contexts or redefining relationships.

#### 3. Complete Evidence
**Requirement**: Every context must carry evidence bundles and logs—no unverifiable work.

**Validation**:
```python
def validate_evidence_completeness(context_id):
    evidence = get_evidence_bundle(context_id)
    required_fields = ['correlation_id', 'hash', 'timestamp', 'artifacts', 'logs']
    return all(field in evidence for field in required_fields)
```

**Fix**: Generate missing evidence bundles, create logs for untracked work, hash all artifacts.

---

## Application Guidelines

### When to Perform COF 13D Analysis

**Required for**:
- Major architectural decisions
- System design and redesign
- New project/initiative planning
- Significant process changes
- Risk-heavy implementations
- Cross-functional initiatives
- Technology selection decisions

**Not required for**:
- Routine bug fixes
- Minor documentation updates
- Simple configuration changes
- Trivial refactoring

### COF Analysis Template

```yaml
cof_analysis:
  context_id: "CTX-001"
  analyzed_at: "2025-11-14T15:30:00Z"
  analyst: "agent-id or user-id"

  dimensions:
    motivational:
      purpose: "Enable secure user authentication"
      value: "Protect user data, meet compliance requirements"
      stakeholders: ["Security team", "Product management", "End users"]

    relational:
      depends_on: ["AUTH-PROVIDER-001", "USER-DB-002"]
      depended_by: ["API-GATEWAY-003", "MOBILE-APP-004"]
      integration_points: ["OAuth2 provider", "User directory"]

    situational:
      current_state: "No authentication, public API"
      constraints: ["90-day compliance deadline", "Limited security expertise"]
      opportunities: ["Leverage Auth0 SaaS", "Implement MFA"]

    resource:
      time_available: "6 weeks"
      skills_needed: ["OAuth2/OIDC", "Token management", "Security testing"]
      tools: ["Auth0", "JWT libraries", "Security scanners"]

    narrative:
      business_case: "Compliance requirement + competitive differentiation"
      communication_plan: "Phased rollout with user communication"
      stakeholder_messaging: "Security-first, minimal user friction"

    recursive:
      feedback_loops: ["User login success rate", "Support tickets", "Security audit findings"]
      iteration_plan: "Beta → Limited rollout → Full deployment"
      learning_capture: "Document authentication patterns for future services"

    computational:
      algorithms: ["JWT signing/verification", "PBKDF2 key derivation", "Rate limiting"]
      performance_targets: ["<100ms token validation", "<1s login flow"]
      optimization_strategy: ["Token caching", "Connection pooling"]

    emergent:
      unexpected_interactions: ["Token refresh during load spikes", "MFA adoption rate impact"]
      innovation_opportunities: ["Passwordless authentication", "Biometric integration"]
      unpredictable_factors: ["User behavior patterns", "Attack vectors"]

    temporal:
      timeline: "Sprint 1: Design, Sprint 2-3: Implementation, Sprint 4: Testing"
      dependencies_sequence: ["Auth provider setup → Integration → Testing → Rollout"]
      deadlines: ["Compliance: 2025-12-31", "Beta launch: 2025-11-30"]

    spatial:
      distribution: ["3 development teams", "5 geographic regions", "Cloud + on-prem"]
      team_coordination: ["Daily standups", "Shared Slack channel", "Integration points"]
      geographic_factors: ["GDPR (EU)", "Data residency requirements"]

    holistic:
      system_impact: ["Enables secure API access", "Foundation for authorization", "Audit trail"]
      broader_context: ["Part of security modernization initiative"]
      relationship_to_whole: ["Critical infrastructure component"]

    validation:
      acceptance_criteria: ["99.9% login success rate", "Zero critical vulnerabilities", "Compliance audit pass"]
      testing_strategy: ["Unit tests ≥80%", "Integration tests", "Penetration testing"]
      evidence_requirements: ["Test results", "Security scan reports", "Audit documentation"]

    integration:
      reintegration_plan: ["API gateway integration", "Mobile app integration", "Admin dashboard"]
      handoff_protocols: ["Security team review", "Operations runbook", "Support documentation"]
      coherence_maintenance: ["Regular security reviews", "Dependency updates", "Documentation sync"]

  completeness_score: 13/13
  ucl_compliance:
    no_orphans: true
    no_cycles: true
    evidence_complete: true
```

---

## UCL Compliance Validation

### Automated Checks

```python
def validate_ucl_compliance(context_id):
    """Validate UCL compliance for a context."""
    context = get_context(context_id)

    # Check 1: No orphans
    if not context.parent_id and context.type != 'root_project':
        return {
            'compliant': False,
            'violation': 'orphan',
            'message': f'Context {context_id} has no parent'
        }

    # Check 2: No cycles
    if detect_cycle_in_ancestry(context_id):
        return {
            'compliant': False,
            'violation': 'cycle',
            'message': f'Context {context_id} creates circular dependency'
        }

    # Check 3: Evidence complete
    evidence = get_evidence_bundle(context_id)
    if not validate_evidence_completeness(evidence):
        return {
            'compliant': False,
            'violation': 'incomplete_evidence',
            'message': f'Context {context_id} missing evidence fields'
        }

    return {
        'compliant': True,
        'message': f'Context {context_id} is UCL compliant'
    }
```

### Manual Review Checklist

**Orphan Check**:
- [ ] Context has valid parent_id reference
- [ ] Parent context exists and is active
- [ ] Context appears in project hierarchy

**Cycle Check**:
- [ ] No context depends on its own descendants
- [ ] Dependency chain terminates at root project
- [ ] No mutual dependencies exist

**Evidence Check**:
- [ ] Evidence bundle exists for context
- [ ] All artifacts have SHA-256 hashes
- [ ] Logs cover all state mutations
- [ ] Correlation IDs link evidence to context

---

## Integration with Quality Gates

### COF Completeness Gate

**Trigger**: Major architectural decision or system design
**Requirement**: All 13 COF dimensions must be addressed
**Validation**: `pytest -m constitution_cof_completeness`

```python
@pytest.mark.constitution_cof_completeness
def test_cof_analysis_complete():
    """Ensure all 13 COF dimensions analyzed for major contexts."""
    major_contexts = get_contexts(type='architectural_decision')

    for context in major_contexts:
        cof_analysis = get_cof_analysis(context.id)
        assert cof_analysis is not None, f"Missing COF analysis for {context.id}"

        required_dimensions = [
            'motivational', 'relational', 'situational', 'resource', 'narrative',
            'recursive', 'computational', 'emergent', 'temporal', 'spatial',
            'holistic', 'validation', 'integration'
        ]

        for dimension in required_dimensions:
            assert dimension in cof_analysis.dimensions, \
                f"Missing dimension '{dimension}' for {context.id}"
```

### UCL Compliance Gate

**Trigger**: All context state changes
**Requirement**: No orphans, cycles, or incomplete evidence
**Validation**: `pytest -m constitution_ucl_compliance`

```python
@pytest.mark.constitution_ucl_compliance
def test_ucl_compliance():
    """Ensure all contexts comply with Universal Context Law."""
    all_contexts = get_all_contexts()

    for context in all_contexts:
        compliance = validate_ucl_compliance(context.id)
        assert compliance['compliant'], \
            f"UCL violation in {context.id}: {compliance['message']}"
```

---

## Sacred Geometry Integration

**COF and UCL align with Sacred Geometry patterns**:

- **Circle**: Completion and closure—contexts flow toward resolution (no cycles)
- **Triangle**: Stability—three-point validation (no orphans, no cycles, evidence complete)
- **Spiral**: Iterative improvement—recursive dimension captures lessons feeding forward
- **Golden Ratio**: Balanced analysis—no dimension dominates, all 13 weighted appropriately
- **Fractal**: Self-similar patterns—COF applies consistently across scales (epic → feature → task)

---

## Anti-Patterns to Avoid

❌ Performing 13D analysis for trivial changes
❌ Superficial dimension analysis (checkbox mentality)
❌ Skipping UCL validation after context mutations
❌ Creating contexts without parent anchoring
❌ Allowing circular dependencies to persist
❌ Missing evidence bundles for significant work

---

## Definition of Done (COF & UCL)

### For COF Analysis
✅ All 13 dimensions addressed for major contexts
✅ Each dimension has substantive content (not placeholders)
✅ Analysis stored in evidence bundle
✅ Completeness score = 13/13

### For UCL Compliance
✅ No orphaned contexts detected
✅ No circular dependencies in context graph
✅ Evidence bundles complete for all contexts
✅ Automated UCL tests passing

---

**See Also**:
- [03-Context-Ontology-Framework.md](../../docs/03-Context-Ontology-Framework.md) — Complete COF reference
- `.github/instructions/quality-gates.instructions.md` — Testing and validation standards
- `.github/instructions/logging.instructions.md` — Evidence bundle requirements
