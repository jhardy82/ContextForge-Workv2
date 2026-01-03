---
applyTo: "memory-bank/*, **/memory-bank/*, update memory bank*, memory bank*, projectbrief*, activeContext*, progress.md"
description: "Memory Bank system for persistent AI context across sessions"
---

# Memory Bank Quick Reference

## Core Files

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `projectbrief.md` | Project scope & goals | On major changes |
| `activeContext.md` | Current focus & decisions | Every session |
| `progress.md` | Completed work & next steps | After each task |
| `systemPatterns.md` | Architecture & patterns | When patterns evolve |
| `techContext.md` | Tech stack & constraints | On stack changes |

## Update Protocol

1. **Read** all memory files at session start
2. **Update** `activeContext.md` with current focus
3. **Log** completed work to `progress.md`
4. **Preserve** existing content (append, don't replace)

## File Structure

```
memory-bank/
├── projectbrief.md      # Foundation (rarely changes)
├── activeContext.md     # Current session (update often)
├── progress.md          # Work log (append after tasks)
├── systemPatterns.md    # Architecture decisions
└── techContext.md       # Technologies used
```

## Full Reference
See `.github/instructions/archive/memory-bank-full.md`
