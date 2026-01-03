# Agent Handoffs - UCL-Compliant Structure

**Version**: 3.0.0 (MVP v3.0)
**Purpose**: Explicit deliverable tracking preventing orphaned work
**Status**: APPROVED

---

## Standard Handoff Structure (MANDATORY)

```markdown
## HANDOFF CONTEXT
From Agent: {source_agent}
To Agent: {target_agent}
Task: {task_id} - {task_title}
Parent Linkage: {parent_id} (UCL compliance)

## DELIVERABLES RECEIVED (from {source_agent})
| Artifact | Format | Validation | Notes |
|----------|--------|------------|-------|
| {name} | {format} | ✅/⚠️/❌ | {notes} |

## DELIVERABLES TO PRODUCE (for {target_agent})
| Artifact | Format | Success Criteria |
|----------|--------|------------------|
| {name} | {format} | {criteria} |

## CONTEXT FOR THIS AGENT
{Task-specific details}
```

---

## UCL Three Rules

1. **No Orphans** - All work has parent linkage
2. **No Cycles** - No circular dependencies  
3. **Complete Evidence** - All claims backed by proof

---

## Validation Symbols

- ✅ **Complete**: Meets all success criteria
- ⚠️ **Partial**: Present but incomplete
- ❌ **Missing**: Not provided (blocker)

---

## Common Handoff Templates

### Meta → Documentation Specialist
- Input: User request, complexity classification
- Output: Requirements doc, user flow, edge cases

### Documentation → Architect
- Input: Requirements, flows, edge cases
- Output: ADR, data model, API spec

### Architect → Executor
- Input: ADR, schemas, integration plan
- Output: Implementation, tests, PAOAL evidence

### Executor → Critic
- Input: Code, tests, evidence bundle
- Output: Sacred Geometry validation, approval/rework

### Critic → Executor (Rework)
- Input: Validation report, rework requirements
- Output: Fixed implementation, updated evidence

### Meta → Debugger
- Input: Bug report, logs, reproduction steps
- Output: Root cause, fix, regression test

---

For detailed templates see `contextforge-foundation.instructions.md` section on UCL.

---

**Document**: Agent Handoffs - UCL Templates  
**Version**: 3.0.0 (MVP v3.0)  
**Last Updated**: 2025-12-31
