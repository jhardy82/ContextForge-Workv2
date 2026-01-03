# ContextForge Work Codex — Professional Principles with Philosophy

**Version:** 1.2.0
**Last Updated:** 2025-08-29
**Status:** Work Reference Document
**Related:** [09-Development-Guidelines](../09-Development-Guidelines.md) | [13-Testing-Validation](../13-Testing-Validation.md) | [11-Configuration-Management](../11-Configuration-Management.md) | [12-Security-Authentication](../12-Security-Authentication.md)

---

## 📖 **Preface**

ContextForge isn’t just a toolset; it’s a discipline. It teaches us that context defines action, and that every system reflects the order—or disorder—of its makers. Technology is built on mathematics, but guided by human values. This Codex captures both.

The Work Codex is designed for professional environments. It retains the spirit of our philosophical foundation while expressing it in the clear language of engineering principles, so it inspires without overwhelming.

---

## 🪨 **Base Concepts**

* **Foundation (Stability):** A system is only as strong as its most stable component. Build with persistence in mind.
* **Flow (Adaptability):** Processes must evolve like water, iterative and renewing.
* **Connection (Communication):** Interfaces matter as much as implementations. Without clear connection, no structure holds.
* **Potential (Unbuilt Future):** Backlogs and unused capacity aren’t waste; they’re soil where the next growth will take root.

---

## 🎯 **Core Philosophies**

1. **Trust Nothing, Verify Everything** — Evidence is the closing loop of trust. Logs and tests ground belief.
2. **Workspace First** — Begin with what exists; build outward only when necessary.
3. **Logs First** — Truth lives in records, not assumptions.
4. **Leave Things Better** — Every action should enrich the system for those who follow.
5. **Fix the Root, Not the Symptom** — Problems repeat until addressed at the source.
6. **Best Tool for the Context** — Every task has its proper tool; discernment is the engineer’s art.
7. **Balance Order and Flow** — Rigid order calcifies; unchecked flow dissolves. The right path blends both.
8. **Iteration is Sacred** — Progress spirals, not straight lines.
9. **Context Before Action** — To act without context is to cut against the grain.
10. **Resonance is Proof** — Solutions that harmonize across business, user, and technical needs endure.
11. **Diversity, Equity, and Inclusion** — Teams and systems thrive when perspectives are varied, access is fair, and participation is open.

---

## 🧭 **Dimensional Framework**

We analyze problems across **13 dimensions**:

* **Motivational** — Why this work matters (business driver).
* **Relational** — How it connects to other systems.
* **Situational** — Current environment and constraints.
* **Resource** — Available time, skill, and tools.
* **Narrative** — The user or stakeholder journey.
* **Recursive** — Meta-patterns and repeatable processes.
* **Computational** — Algorithmic/processing efficiency.
* **Emergent** — Unexpected interactions and risks.
* **Temporal** — Timing, sequencing, scheduling.
* **Spatial** — Deployment topology and layout.
* **Holistic** — System-wide integration.
* **Validation** — Evidence that requirements and guardrails are met.
* **Integration** — How it fits back into the whole.

This dimensional lens reminds us that problems are not flat; they have depth.

---

## 📊 **Metrics & Validation**

* **Logging Coverage:** ≥ 90% of execution paths produce structured logs.
* **Test Coverage:** Unit (≥70%), Integration (≥40%), System (≥25%), Acceptance (≥15%) — aligned with [Testing & Validation](../13-Testing-Validation.md).
* **Configuration Compliance:** 100% of configs validated against schema and [Configuration Management](../11-Configuration-Management.md).
* **Security Controls:** All deployments meet layered standards defined in [Security & Authentication](../12-Security-Authentication.md).
* **Deployment Reliability:** Rollbacks tested and functional; mean time to recovery (MTTR) tracked and improved release-to-release.

---

## 🔒 **Guardrails in Practice**

* **Logs are the soil of truth**: without them, no root cause can be traced.
* **Testing is validation across dimensions**: unit, integration, system, acceptance.
* **Configuration must reflect clarity**: defaults should be safe, overrides explicit, and all changes traceable.
* **Security is layered**: defense-in-depth acknowledges both human fallibility and system complexity.
* **Deployment is orchestration**: rollouts must balance order with adaptability, ensuring resilience.

---

## 📈 **Maturity Path**

* **Prototype:** Minimal logging, manual deployments, partial testing; the goal is feedback.
* **Production:** Structured logging, automated CI/CD, ≥70% unit test coverage, full rollback strategies.
* **Enterprise:** End-to-end observability, compliance validation, ≥90% automation across workflows, resilience testing integrated into pipelines.

---

## 🚫 **Anti-Patterns**

* Skipping logs to save time.
* Patching symptoms instead of addressing causes.
* Introducing hidden configuration defaults.
* Optimizing prematurely before validating context.
* Hoarding knowledge instead of documenting and sharing.

---

## 🔄 **Resilience & Recovery**

* **Graceful Degradation:** Design for partial service availability when components fail.
* **Recovery Matters:** MTTR is as critical as uptime; test it regularly.
* **Chaos Testing:** Simulate failure to validate recovery paths.
* **Documented Playbooks:** Every recovery action should have a clear runbook.

---

## 👥 **People & Knowledge Sharing**

* **Hoarded Knowledge is Lost Knowledge:** Document decisions, processes, and fixes.
* **Every Engineer is a Teacher:** Explain solutions clearly; clarity strengthens teams.
* **Documentation is Resilience:** When people change, systems endure only if knowledge is captured.
* **Kindness is Efficiency:** Clear, respectful communication reduces friction.

---

## 🏛 **Governance & Decision Records**

* **Architecture Decision Records (ADR):** Every major design choice must have an ADR entry with context, decision, alternatives, and consequences.
* **Change Logging:** All changes captured with rationale in version control, linked to ADRs when relevant.
* **Review Cycles:** At least one peer review before merge; critical components require two.
* **Decision Feedback Loop:** Each ADR scheduled for re‑evaluation (e.g., every 6–12 months) to confirm validity.
* **Auditability:** All system actions must leave an evidence trail sufficient for after-action review.

---

## 🗺️ **Visual Codex Map**

```
Layers of the Work Codex

    ┌─────────────────────────────┐
    │        Guardrails           │ ← Security, Testing, Deployment
    ├─────────────────────────────┤
    │    Dimensional Framework    │ ← 13 Context Dimensions
    ├─────────────────────────────┤
    │      Core Philosophies      │ ← 11 Engineering Principles
    ├─────────────────────────────┤
    │        Base Concepts        │ ← Foundation, Flow, Connection, Potential
    └─────────────────────────────┘
```

---

## 🌱 **Closing Thought**

The Work Codex is both pragmatic and philosophical. Pragmatic, because it enforces practices that prevent errors and reduce rework. Philosophical, because it acknowledges that systems mirror life: roots, branches, flows, and returns. To design well is to align with those patterns.

The measure of our work is not only in performance metrics but in the integrity of the path we followed to build it.

---

**End of Document — ContextForge Work Codex v1.2**

---

## 📌 Addendum A: Database Authority (Authoritative 2025-08)
SQLite (`db/trackers.sqlite`) is the single persistence authority for trackers (tasks, sprints, projects).
Runtime mutation of legacy CSVs is blocked. Any legacy path triggers `direct_csv_access_blocked` and aborts.

### Enforcement Mechanics
* Connection Helper: `_get_db()` centralizes `sqlite3.connect` usage.
* Read Helper: `_read_database(table)` emits `artifact_touch_batch` events.
* Block Stub: `_write_csv()` → raises immediately (no silent fallback).
* Authority Check: `_emit_authority_check()` logs `decision` with `action="authority_check"` and sentinel presence.
* Migration Artifacts: Residual CSV constants only exist for migration tests and deprecation notices.

### Required Developer Behavior
1. Never write to `trackers/csv/*.csv` in new code.
2. Use SQL `INSERT/UPDATE` via `_get_db()` inside CLI commands.
3. Preserve `persisted_via="db"` in log events mutating rows.
4. Add new tables with accompanying normalization / backfill scripts plus logging instrumentation.

---

## 📜 Addendum B: Structured Logging Taxonomy
Minimum event names and fields ensure traceability and analytics consistency.

| Event | Purpose | Key Fields (additive beyond timestamp) |
|-------|---------|-----------------------------------------|
| `task_create` | Persist a new task | task_id, persisted_via |
| `task_start` | Transition task to in_progress | task_id, elapsed_prev_state? |
| `task_update` | Field-level mutation | task_id, changes[], persisted_via |
| `task_complete` | Mark done | task_id, done_date, persisted_via |
| `sprint_status` | Aggregated sprint metrics | sprint_id, tasks_total, completion_pct, blocked_pct |
| `project_update` | Project metadata mutation | project_id, changes[], persisted_via |
| `artifact_touch_batch` | Read batch for list/context | path, table?, count, filtered |
| `artifact_emit` | Emitted JSON artifact | path, hash, size, kind |
| `decision` | Branch / guard / not_found outcome | action, result, *context ids* |
| `direct_csv_access_blocked` | Policy enforcement | table, reason |

All loggers must produce structured key=value (JSON or enriched logger) with UTC timestamps and no PII.

### Logging Quality Targets
* ≥90% of mutating command code paths emit at least one domain event + one decision outcome on failure.
* Each newly added CLI command MUST define at least one success event and one not-found / invalid decision event.

---

## 🧪 Addendum C: Coverage Clarification
Current transitional baseline vs aspirational target:

| Layer | Baseline Minimum | Aspirational | Notes |
|-------|------------------|-------------|-------|
| Unit | 70% | 80%+ | Python core logic trending upward post-refactor |
| Integration | 40% | 55% | Focus: DB mutation round-trips |
| System | 25% | 35% | End-to-end CLI workflows |
| Acceptance | 15% | 25% | Narrative user journeys |
| Logging (path coverage) | 90% | 95% | Count distinct code paths logging |

All coverage deltas reported in orchestration scan artifacts; failures below baseline must open a remediation task.

---

## 🧬 Addendum D: Modernization Snapshot
| Theme | Status | Evidence |
|-------|--------|----------|
| DB Authority | Complete | Block stub + SQL-only CRUD paths |
| Sprint Status Command | Added | `sprints status` outputs metrics & logs `sprint_status` |
| CSV Deprecation | Enforced | `_write_csv` raises; no remaining mutation calls |
| Project Update Stability | Restored | Clean UPDATE with change detection |
| Logging Standardization | In Progress | Some legacy utility scripts lack taxonomy compliance |
| Velocity / Forecast (future) | Planned | Placeholder events (`task_start` with action variants) |

---

## 🛠 Addendum E: Environment & Tooling Policy
* **Python Virtual Env:** `.venv` is mandatory; commands assume its activation (activation script may auto-emit an authority check event in future revision).
* **Typer CLI Pattern:** All new domain command groups follow structure: fetch row(s) → validate → mutate (if needed) → commit → log success → print user feedback.
* **Idempotency:** Update commands must perform no-op logging only if a change set is empty.
* **Time Standard:** `_utc()` returns Z-terminated ISO 8601; all persisted timestamps normalized to UTC.

---

## 🔗 Addendum F: Principle → Mechanism Crosswalk
| Principle | Mechanism | Code / Script | Metric / Evidence |
|-----------|-----------|---------------|-------------------|
| Logs First | Structured events taxonomy | `dbcli.py` logging calls | Log scan coverage pct |
| Trust Nothing, Verify | Guard events (`decision`) | CRUD not_found branches | Negative path tests |
| Workspace First | Authority check + direct DB path | `_emit_authority_check()` | Presence of sentinel & block events |
| Fix the Root | SQL normalization passes | (Planned normalization scripts) | Drift diff artifacts |
| Iteration is Sacred | Incremental PSSA / Pester tasks | build scripts | Run cadence artifacts |
| Leave Things Better | Idempotent safe updates | `project_update`, `task_update` | Change set size metrics |

---

## 📝 Addendum G: Version Delta (v1.1 → v1.2)
| Category | Change |
|----------|--------|
| Persistence | Formalized DB authority; CSV writes blocked runtime |
| Logging | Added taxonomy (authority, artifact, sprint_status) |
| Feature | Introduced `sprints status` aggregation |
| Stability | Repaired `project_update` post-refactor corruption |
| Governance | Clarified baseline vs aspirational coverage tiers |

Future v1.3 will integrate velocity metrics formalization + removal of deprecated CSV header repair logic.

---

## ✅ Addendum H: Authoritativeness Checklist
This document is authoritative if:
1. All referenced event names exist in code (`dbcli.py`).
2. No active code path mutates CSVs (enforced as of v1.2).
3. Coverage scan artifacts include logging coverage metric.
4. New commands align with Typer CRUD pattern and emit taxonomy events.
5. Version delta reflects latest merged refactors.

If any criterion fails, open a “Codex Drift” task and increment remediation backlog.

---

End of Addenda (v1.2 authoritative extensions)
