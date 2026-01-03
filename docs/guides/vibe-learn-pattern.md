# Vibe Learn Pattern Guide

## What is vibe_learn?

`vibe_learn` is an MCP tool from `vibe-check-mcp` that records patterns, lessons, and discoveries during agent sessions. It builds a knowledge base that helps prevent repeated mistakes and reinforces successful approaches.

**Purpose**: Transform ephemeral session insights into persistent organizational memory.

## Category Types

| Category | Use Case |
|----------|----------|
| `Success` | Completed task, working solution, milestone achieved |
| `Mistake` | Error made, wrong approach taken |
| `Preference` | User or system preference discovered |
| `Complex Solution Bias` | Over-engineered when simple would suffice |
| `Feature Creep` | Scope expanded beyond requirements |
| `Premature Implementation` | Coded before understanding requirements |
| `Misalignment` | Assumption didn't match reality |
| `Overtooling` | Used more tools than necessary |

## When to Call vibe_learn

| Trigger | Category | Example |
|---------|----------|---------|
| After fixing a bug | `Mistake` | Schema mismatch discovered |
| After completing a task | `Success` | E2E tests passing |
| After user correction | `Preference` | User prefers explicit imports |
| After reverting code | `Premature Implementation` | Started coding before reading spec |
| After simplifying | `Complex Solution Bias` | Replaced framework with script |

## Parameters

```typescript
{
  sessionId: string,     // Optional - links to vibe_check session
  category: CategoryType,
  mistake: string,       // One-sentence description of the learning
  solution?: string,     // How it was corrected (if applicable)
  type?: "mistake" | "preference" | "success"
}
```

## Practical Examples

### Recording a Schema Mismatch Lesson

```json
{
  "sessionId": "session-123",
  "category": "Misalignment",
  "mistake": "Assumed 'status' column existed but database uses 'state'",
  "solution": "Query information_schema before generating SQL",
  "type": "mistake"
}
```

### Recording a Successful Session Completion

```json
{
  "sessionId": "session-123",
  "category": "Success",
  "mistake": "Completed E2E test suite with 100% pass rate",
  "type": "success"
}
```

### Recording a Premature Implementation Discovery

```json
{
  "sessionId": "session-123",
  "category": "Premature Implementation",
  "mistake": "Started writing migration before checking existing schema",
  "solution": "Always run pgsql_db_context before DDL operations",
  "type": "mistake"
}
```

## Best Practices

1. **Record immediately** — Capture lessons while context is fresh
2. **Be specific** — Include table names, file paths, or tool names
3. **Include solution** — Future sessions benefit from the fix, not just the problem
4. **Use correct type** — `success` for wins, `mistake` for errors, `preference` for choices

## Integration with ContextForge

In ContextForge sessions, `vibe_learn` is called:
- At phase transitions (after vibe_check)
- When errors are encountered and resolved
- When tasks complete successfully
- When user corrections reveal preferences

Patterns accumulate across sessions, informing future vibe_check responses.

---

*"Every mistake recorded is a mistake prevented."*
