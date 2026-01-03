# Conversation Triggers & Prompt Shortcuts

Purpose: Lightweight, predictable keywords you can paste as a single word (or short phrase) to advance the workflow without re‑explaining context.

Applies To: Agent chat prompts, commit / PR review guidance, governance YAML footers.

> Implementation Note: These are semantic intents, not commands. The agent interprets them relative to current repository state.

## Core Progress Triggers

| Trigger | Intent | Typical Next Action |
|---------|--------|--------------------|
| `Proceed` | Advance to next queued task (no re-plan) | Executes top backlog item |
| `Continue` | Resume prior multi-step action | Picks up pending sub-step |
| `Execute` | Run previously proposed plan now | Runs tasks/scripts/tests |
| `Advance` | Move to next phase/milestone summary & readiness check | Emits phase gate validation |
| `Next` | Show 1–3 immediately actionable options | Returns mini menu only |
| `Refocus` | Rebuild concise task list from latest repo state | Fresh delta assessment |
| `Summarize` | Output compressed status + blockers | High-signal summary |
| `ChangelogDraft` | Generate unreleased CHANGELOG section | Draft markdown |

## Quality & Governance

| Trigger | Intent | Action |
|---------|--------|--------|
| `QualityChain` | Run PSSA errors-only + Pester (generic chain) | Invokes quality chain task |
| `PesterIncremental` | Run only changed tests | Executes incremental test task |
| `PSSAIncremental` | Run analyzer on changed files | Executes incremental PSSA task |
| `GovernanceScan` | Full governance suite (anchor map, inventory, expiries, compliance) | Runs governance full suite |
| `HostScan` | Modernization & host usage context refresh | Runs modernization + inventory scripts |
| `ParityCheck` | Dual-engine parity hash compare (planned harness) | Launch parity harness (when implemented) |

## Context & Evidence

| Trigger | Intent | Action |
|---------|--------|--------|
| `ContextRefresh` | Rebuild host execution context JSON | Calls Generate-HostExecutionContext script |
| `MetricsSnapshot` | Emit migration metrics (host usage, policy distribution) | Runs metrics emitter (planned) |
| `EvidencePack` | Bundle recent changes + governance logs | Creates evidence zip (planned) |
| `AAR` | Produce After Action Review for last major action | Generates AAR artifact |

## Differential / Planning

| Trigger | Intent | Action |
|---------|--------|--------|
| `DeltaPlan` | Show only new diffs since last summary & propose next edits | Diff-based micro plan |
| `RiskScan` | Enumerate current high-risk or deprecated patterns | Pattern scan & report |
| `Backlog` | Output prioritized backlog (3–10 items) | Rebuilds backlog list |

## Usage Patterns
Minimal: Send a single trigger keyword (e.g., `Proceed`).
Compound: Chain with a qualifier: `Proceed QualityChain` (priority left→right). The agent handles first recognized token, then secondary if safe.
Explicit: `Execute: QualityChain` (colon form) for clarity in logs.

## Footer Snippet (Optional Inclusion)
Paste or template this at the end of any chat for quick reuse:

```
Triggers: Proceed | Continue | Next | QualityChain | PesterIncremental | PSSAIncremental | HostScan | ContextRefresh | ParityCheck | Backlog
```

## Integration Ideas
1. VS Code User Snippet: Map each trigger to an expandable explanation.
2. PR Template Footer: Add “Reviewer Shortcuts” line with top 5 triggers.
3. Communication YAML: New field `next_triggers: [Proceed, QualityChain, Backlog]` for handoff clarity.
4. Pre-commit Hook (opt.): Warn if staged changes touch host spawning logic; suggest `HostScan` trigger.

## Roadmap (Planned Helpers)

| Helper | Status | Notes |
|--------|--------|-------|
| Parity harness (`ParityCheck`) | Planned | Dual host run + hash compare |
| Migration metrics emitter | Planned | Counts legacy spawns & policy distribution |
| Evidence pack creator | Planned | Bundles logs + diffs + governance results |
| Trigger autosuggest | Consider | Ranks triggers by recent context gaps |

## Maintenance
Add / remove triggers by editing `config/conversation_triggers.json`; documentation should mirror keys.

---
Version: 1.0.0
Last Updated: 2025-08-16
