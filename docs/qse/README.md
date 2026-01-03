# QSE (Quality Software Engineering) Directory

## Overview

The `.QSE` directory contains quality assurance artifacts, session decisions, and testing infrastructure for the SCCMScripts project. This structure supports systematic testing, evidence collection, and decision tracking.

## Structure

```
.QSE/
├── v2/
│   ├── Artifacts/           # Test artifacts and work item documentation
│   │   └── W-REDIS-001/     # Redis containerization testing artifacts
│   │       ├── ExecutionPlan.*.yaml
│   │       ├── TestSpec.*.yaml
│   │       ├── ResearchPlan.*.yaml
│   │       └── Test.Checklist.*.yaml
│   └── Sessions/            # Session decision logs and After Action Reviews
│       └── SESSION-DECISION-*.yaml
```

## Artifact Types

### Execution Plans
- **Purpose:** Define test execution phases, tasks, and timelines
- **Naming:** `ExecutionPlan.<work-item>.<timestamp>.yaml`
- **Content:** Phase definitions, task breakdowns, duration estimates, checkpoints

### Test Specifications
- **Purpose:** Detail test cases with inputs, outputs, and acceptance criteria
- **Naming:** `TestSpec.<work-item>.<timestamp>.yaml`
- **Content:** Test categories, success criteria, evidence requirements

### Research Plans
- **Purpose:** Document research, prerequisites, and preparation evidence
- **Naming:** `ResearchPlan.<work-item>.<timestamp>.yaml`
- **Content:** Infrastructure requirements, documentation sources, tool requirements

### Test Checklists
- **Purpose:** Track individual test task status and acceptance criteria
- **Naming:** `Test.Checklist.<work-item>.<timestamp>.yaml`
- **Content:** All test tasks with status, acceptance criteria, evidence links

### Session Decisions
- **Purpose:** Document session-level decisions, risk assessments, and outcomes
- **Naming:** `SESSION-DECISION-<date>.yaml`
- **Content:** Decision rationale, risk factors, prerequisites assessment, next steps

## Work Item Naming

Work items follow the pattern: `W-<COMPONENT>-<NUMBER>`

Examples:
- `W-REDIS-001` - Redis containerization comprehensive testing
- `W-SCCM-001` - SCCM integration testing
- `W-AUTH-001` - Authentication system validation

## Hard Stop Rules

Per QSE methodology, certain prerequisites MUST be met before proceeding:

### Artifact Verification Rule
Before executing comprehensive testing:
1. Verify all required artifacts exist (ExecutionPlan, TestSpec, ResearchPlan, TestChecklist)
2. Validate YAML schema correctness
3. Confirm acceptance criteria are measurable
4. Check evidence correlation references

**If ANY artifact is missing or incomplete:**
- ❌ STOP IMMEDIATELY - Do NOT proceed
- 🔄 DEFER TO NEXT SESSION - Requires replanning
- 📝 DOCUMENT BLOCKER - Create session decision log

### Session Duration Rule
For tasks exceeding 2 hours:
- Implement checkpoint gates at logical intervals
- Document energy/cognitive state at checkpoints
- Maintain option to pause and save state

## Template Files

Files with `.TEMPLATE.yaml` suffix are templates showing required structure but are not complete artifacts. They indicate prerequisites that are not yet met.

## Integration with AGENTS.md

The QSE structure complements the AGENTS.md development workflow:

1. **Planning Phase:** QSE artifacts define the "what" and "why"
2. **Development Phase:** AGENTS.md defines the "how"
3. **Validation Phase:** QSE tracks evidence and outcomes
4. **Review Phase:** Session decisions inform future planning

## Compliance

This structure aligns with:
- **Copilot Instructions:** Multi-angle solution drafts, decision documentation
- **AGENTS.md:** Scoped commits, descriptive changes, test evidence
- **ContextForge:** Workflow intent, approvals, telemetry capture

## Best Practices

1. **Always create session decision logs** for high-risk or deferred work
2. **Use templates to show intent** even when prerequisites aren't met
3. **Document rationale** for continuing or deferring complex work
4. **Correlate evidence** to implementation checkpoints
5. **Maintain traceability** from requirements through testing to deployment

## Example: Redis Phase 7 Decision

See `.QSE/v2/Sessions/SESSION-DECISION-2025-01-04.yaml` for an example of:
- Risk assessment documentation
- Prerequisites validation
- Hard stop rule application
- Deferral decision with clear rationale

This demonstrates proper use of QSE methodology to avoid high-risk paths and maintain quality standards.
