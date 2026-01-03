# PAOAL Execution Cycle - Complete Templates

**Version**: 3.0.0 (MVP v3.0)
**Purpose**: Systematic execution framework with evidence generation
**Status**: APPROVED
**Authority**: MVP v3.0 Package + ContextForge PAOAL Model

---

## Document Purpose

This file provides **complete PAOAL execution guidance** for systematic implementation with evidence generation.

**For quick reference**: See `copilot-instructions.md`
**For philosophy**: See `contextforge-foundation.instructions.md`

---

## When to Use PAOAL

**ALWAYS Use** (Medium/Complex):
- Implementations affecting 3+ files
- Architectural changes
- Cross-system integrations
- When evidence trail required

**OPTIONAL** (Simple):
- Single file changes
- Typo/config fixes

---

## Complete PAOAL Template

```yaml
paoal_execution:
  task_id: [TASK-XXX]
  complexity: [SIMPLE/MEDIUM/COMPLEX]
  
  plan:
    approach: "[implementation strategy]"
    estimate:
      loc: [number]
      time: "[X hours]"
    tools: [list]
    patterns: [list]
    order: [steps]
  
  act:
    files_created: [list with LOC]
    commits: [list with hashes]
    tests_added: [count]
    loc_total: [number]
  
  observe:
    tests: "[X/Y passing]"
    coverage: [percentage]
    quality: "[linting status]"
    criteria: [acceptance criteria check]
  
  adapt:
    issues_resolved: [count]
    optimizations: [list]
    deviations: [list with rationale]
  
  log:
    evidence_path: [file]
    lessons: [list]
    patterns: [list]
    memory_stored: [true/false]
```

See `contextforge-foundation.instructions.md` for detailed phase descriptions and examples.

---

**Document**: PAOAL Execution Templates  
**Version**: 3.0.0 (MVP v3.0)  
**Last Updated**: 2025-12-31
