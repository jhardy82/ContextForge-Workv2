---
applyTo: "QSE*, QSM*, workflow*, task plan*, implement task*"
description: "ContextForge Task Workflow - PAOAL cycle and COF integration"
---

# Task Workflow Quick Reference

## PAOAL Execution Cycle

```
Plan → Act → Observe → Adapt → Log → [repeat]
```

| Phase | Actions | Key Tools |
|-------|---------|-----------|
| **Plan** | Analyze, select tools | `sequential_thinking`, `vibe_check` |
| **Act** | Execute minimum action | MCP tools, CF_CLI |
| **Observe** | Run tests, validate | pytest, quality gates |
| **Adapt** | Adjust based on results | `vibe_learn` |
| **Log** | Record evidence | ulog, .QSE/ artifacts |

## When to Use Full COF

| Complexity | Files | COF Required? |
|------------|-------|---------------|
| Simple | 1-2 | ❌ Skip |
| Medium | 3-5 | ⚠️ Key dimensions only |
| Complex | 6+ | ✅ Full 13D analysis |

## Sacred Geometry Gates

| Pattern | Check | Threshold |
|---------|-------|-----------|
| Circle | Completeness | All dimensions addressed |
| Triangle | Stability | Tests pass, docs exist |
| Spiral | Iteration | Retrospective captured |
| Golden Ratio | Balance | Effort ∝ value |
| Fractal | Modularity | Reusable patterns |

**Pass Requirement**: ≥3 of 5 patterns must validate

## Full Reference
See `.github/instructions/archive/qsm-workflow-full.md`
