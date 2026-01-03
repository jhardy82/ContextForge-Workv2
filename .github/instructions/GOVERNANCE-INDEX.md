---
description: Comprehensive cross-reference of authority scope across the ContextForge instruction hierarchy
applyTo: "**/*governance*", "**/*conflict*", "**/*codex*", ".github/instructions/**"
---

# ContextForge Governance Authority Index

**Version**: 1.0.0
**Last Updated**: 2025-10-27
**Authority Reference**: `.github/copilot-instructions.md` (Governance Hierarchy section)
**Codex Foundation**: `docs/Codex/ContextForge Work Codex — Professional Principles with Philosophy.md` v1.2.0

---

## Purpose

This index provides a comprehensive cross-reference of authority scope across the ContextForge instruction hierarchy. It documents which files govern which concerns, enabling clear conflict resolution through the 4-tier governance model.

---

## Governance Tier Structure

### **Tier 0: Foundational Authority** (Philosophical Foundation)

These documents establish the **Core Philosophies and Principles** that ground all ContextForge work:

| Document | Authority Scope | Key Content |
|----------|-----------------|-------------|
| `docs/Codex/ContextForge Work Codex — Professional Principles with Philosophy.md` | **11 Core Philosophies**, **4 Base Concepts**, **Database Authority**, **Logging Taxonomy** | Trust Nothing Verify Everything, Workspace First, Logs First, Leave Things Better, Fix the Root, Best Tool for Context, Balance Order and Flow, Iteration is Sacred, Context Before Action, Resonance is Proof, Diversity Equity Inclusion |
| `docs/Codex/COF and UCL Definitions.md` | **Context Ontology Framework (COF)**, **Universal Context Law (UCL)**, **Sacred Geometry** | 13-Dimensional Framework, UCL: "No orphaned, cyclical, or incomplete context may persist", Sacred Geometry patterns (Circle, Triangle, Spiral, Golden Ratio, Fractal) |

**Codex Alignment**: All tiers derive legitimacy from Codex principles. Governance decisions must be traceable to foundational philosophies.

---

### **Tier 1: User Directives** (Supreme Authority)

**Authority Scope**: Direct and explicit user commands override ALL written instructions

**Examples**:
- "Stop and explain" → Immediate halt regardless of active chatmode or autonomous operation
- "Use tool X" → Direct tool invocation without analysis or alternatives
- "Skip validation" → Bypass normal quality gates (with documented acknowledgment)

**Precedence**: Absolute. No written instruction can override a direct user command.

**Codex Alignment**: Philosophy 9 "Context Before Action" — user provides ultimate context

---

### **Tier 2: Orchestrator** (Cross-Cutting Governance)

**Authority File**: `.github/copilot-instructions.md`

**Authority Scope**: Cross-cutting concerns that apply to ALL work regardless of domain

| Concern Area | Governance Details |
|--------------|-------------------|
| **Safety Protocols** | Confirmation required for irreversible actions (file deletion, git operations, deployment), user "stop" command immediately halts execution, no chatmode can bypass safety gates |
| **Response Format** | Mandatory headers (Project ID, Name, QSE Session ID, Phase) at beginning of responses, mandatory trailers (Operations, Evidence, Next Actions) at end of responses |
| **Quality Gates** | Evidence recording with SHA-256 hashes, validation requirements before Phase 6 execution, test coverage thresholds (Python ≥80%, PowerShell ≥70%) |
| **Metacognitive Oversight** | `constitution_check` on EVERY user prompt (session ID validation), strategic `vibe_check` at phase transitions and before major actions, `vibe_learn` on ALL failures and unexpected behaviors |
| **Session Integrity** | Session ID must match Project ID (validated on every prompt), project summary header in EVERY response, phase tracking and updates mandatory |
| **Tool Preference Hierarchy** | MCP tools → VS Code extensions → Built-in tools → Python plugins → PowerShell modules → Other tools |
| **Context7 MCP Integration** | MANDATORY for code generation, library documentation, and setup/configuration steps |
| **TODO Management** | Read-before-write protocol (ABSOLUTE REQUIREMENT), preserve ALL existing items unless explicitly requested |

**Non-Overridable Elements**: Safety protocols, session integrity validation, evidence requirements

**Delegation Model**: Tier 2 delegates to Tier 3 for feature-specific authority

**Codex Alignment**: Philosophy 1 "Trust Nothing, Verify Everything" — safety gates and evidence requirements

---

### **Tier 3: Feature Authority** (Domain-Specific Expertise)

**Authority Scope**: Domain-specific protocols, patterns, and implementation standards

| Instruction File | Authority Domain | Key Governance Areas |
|------------------|------------------|---------------------|
| `vibe-check-mcp-integration.instructions.md` | **Metacognitive Oversight** | Strategic checkpoint workflows (4-5 per session), conditional trigger patterns (complexity/uncertainty spikes), feedback adaptation protocols, learning capture (vibe_learn), constitution management (session rules), 10-15% optimal dosage enforcement |
| `Sequential-Thinking.instructions.md` | **Complex Reasoning Patterns** | Plan → Act → Observe → Adapt → Log micro-cycles, sequential execution with step validation, branching policy (when multiple approaches merit exploration), hybrid adaptive patterns (sequential + branched transitions), elasticity controls (shallow/standard/deep), revision budgets |
| `QSM-Workflow.instructions.md` | **QSE Task Management** | 9-phase UTMW workflow (Phases 0-8), COF 13-dimensional analysis (MANDATORY per phase), UCL compliance validation (orphan/cyclical/incomplete detection), Sacred Geometry alignment (Circle/Triangle/Spiral/GoldenRatio/Fractal), Evidence discipline with correlation IDs, Quality gates per phase |
| `taming-copilot.instructions.md` | **User Interaction Standards** | Code-on-request-only (no unsolicited code blocks), direct and concise responses, best practices first, explain the "why", minimalist code generation, surgical code modification (preserve working logic), intelligent tool usage (tool-first approach), mandatory codebase search before creating |
| `quantum-personas.instructions.md` | **Professional Personas** | Advanced Context Ontology (12 dimensions), 25 professional personas across 5 categories, dynamic persona activation, multi-agent collaboration framework, extended autonomous operation, context-aware evolution |
| `context7-mcp.instructions.md` | **Library Documentation** | Auto-invoke for code generation/setup/library docs, resolve-library-id → get-library-docs workflow, performance standards (<100ms resolution, <200ms retrieval), trust score prioritization (>8.5), integration with CLI development |
| `agent-todos.instructions.md` | **AI Agent TODO Management** | Single consolidated event pattern, empty state transitions, promise-based synchronization, hash-based deduplication with version tracking, proper test context initialization, storage layer abstraction (ITodoStorage), export pattern (write-only markdown) |
| `QSM-task-plan-implementation.instructions.md` | **Task Plan Execution** | Dynamic Task Manager (TaskMan) API as authoritative source, TaskMan-first tracking with optional read-only mirrors, Phase signals for automation, UTMW TaskMan naming standard (Group 2), problem resolution protocols |
| `terminal-output.instructions.md` | **Rich Console Formatting** | Full Rich library integration (Console, Progress, Panel, Table, Tree, Status), Monokai Pygments theme, TQDM-style progress bars (multi-phase with emoji indicators), enhanced visual hierarchy, RichProgressManager pattern |
| `terminal-unicode-configuration.instructions.md` | **Terminal Encoding** | MANDATORY UTF-8 for terminal sessions/transcripts/source files/console output, PowerShell profile configuration, Tee-Object transcript pattern (not Start-Transcript), Python UTF-8 mode, Rich library Sacred Geometry support |
| `powershell.instructions.md` | **PowerShell Development** | Cmdlet naming (Verb-Noun), parameter validation, pipeline support, error handling (try/catch/finally), comment-based help, Pester testing, PSScriptAnalyzer compliance |
| `powershell-pester-5.instructions.md` | **PowerShell Testing** | Pester v5 syntax (Describe/Context/It), BeforeAll/AfterAll hooks, mock patterns, code coverage, test organization |
| `python.instructions.md` | **Python Development** | PEP 8 compliance, type hints, docstrings (Google style), pytest patterns, error handling, virtual environments |
| `markdown.instructions.md` | **Documentation Standards** | Markdown formatting, heading hierarchy, code block language tags, link validation, table formatting |
| `go.instructions.md` | **Go Development** | Idiomatic Go patterns, error handling, goroutines, interfaces, testing with testing package |
| `github-actions-ci-cd-best-practices.instructions.md` | **CI/CD Workflows** | GitHub Actions workflow structure, jobs/steps/actions, environment variables, secret management, caching strategies, matrix builds, deployment patterns |
| `sql-sp-generation.instructions.md` | **SQL & Stored Procedures** | SQL statement generation, stored procedure patterns, parameter handling, transaction management, error handling |

**Constraint**: All Tier 3 authorities operate within Tier 2 safety boundaries

**Codex Alignment**: Philosophy 6 "Best Tool for the Context" — domain expertise provides authoritative guidance

**Authority Scope Headers** (RECOMMENDED for all `*.instructions.md` files):
```markdown
---
applyTo: "**"
authorityDomain: "[Feature Name]"
governanceTier: 3
orchestratorReference: ".github/copilot-instructions.md"
codexAlignment: "ContextForge Work Codex v1.2"
---
```

---

### **Tier 4: Execution Personas** (Style Enhancement, Not Governance)

**Authority Scope**: Execution style, enthusiasm, thoroughness, communication preferences

**Critical Constraint**: **CANNOT override Tier 1-3 governance**

| Chatmode File | Execution Style | Intensity Language Clarification |
|---------------|-----------------|----------------------------------|
| `cf-cli-orchestration-beast-mode.chatmode.md` | **CF_CLI task orchestration emphasis**, maximum workflow efficiency, comprehensive monitoring | "ABSOLUTE", "SUPREME", "UNSTOPPABLE", "EMERGENCY", "TRANSCENDENT" apply to **enthusiasm**, NOT governance authority |
| `Ultimate-Transparent-Thinking-Beast-Mode.chatmode.md` | **Transparent reasoning**, crystal clarity, creative problem-solving | "ABSOLUTE", "UNSTOPPABLE", "MAXIMUM" apply to **thoroughness**, NOT governance override |
| `CF-Enhanced-Thinking-Beast-Mode.chatmode.md` | **Enhanced cognitive patterns**, comprehensive analysis | Intensity language enhances execution energy, safety protocols remain non-overridable |
| `blueprint-mode.chatmode.md` | **Architectural planning**, systematic design | Planning emphasis does not bypass orchestrator quality gates |
| `planner.chatmode.md` | **Strategic planning**, roadmap development | Planning depth preference, not governance override |
| `cf-researcher.chatmode.md` | **Research thoroughness**, comprehensive discovery | Research intensity preference within Tier 2-3 constraints |
| `cf-implementer.chatmode.md` | **Implementation focus**, execution efficiency | Implementation style preference, safety gates apply |
| Other chatmodes | Various execution style preferences | All chatmodes constrained by Tier 1-3 governance |

**Governance Notice Template** (to be added to all chatmode files):
```markdown
> **⚖️ TIER 4 EXECUTION PERSONA - GOVERNANCE CONSTRAINTS**
>
> This chatmode operates as a **Tier 4 Execution Persona** within the ContextForge governance hierarchy.
> It enhances execution style, enthusiasm, and thoroughness but **CANNOT override**:
>
> - **Tier 1**: User Directives (supreme authority - "stop" immediately halts execution)
> - **Tier 2**: Safety protocols and orchestrator governance (`.github/copilot-instructions.md`)
> - **Tier 3**: Feature-specific authorities (`*.instructions.md` files)
>
> **CRITICAL CLARIFICATION**: Intensity language in this file applies to **execution enthusiasm
> and thoroughness**, NOT governance override authority. Safety protocols remain non-overridable.
> User directives take absolute precedence.
>
> **Authority Reference**: `.github/copilot-instructions.md` (Governance Hierarchy section)
> **Codex Alignment**: Philosophy 8 "Iteration is Sacred" - execution style enables adaptive iteration
```

**Codex Alignment**: Philosophy 8 "Iteration is Sacred" — execution style variation enables adaptive iteration

---

## Precedence Resolution Algorithm

When instructions conflict across tiers:

1. **Check Tier 1**: Does a direct user directive address this specific concern?
   - **YES** → User command wins (supreme authority)
   - **NO** → Continue to Tier 2

2. **Check Tier 2**: Is a safety protocol or cross-cutting governance concern involved?
   - **YES** → Orchestrator safety gate wins (non-overridable)
   - **NO** → Continue to Tier 3

3. **Check Tier 3**: Is this a feature-specific domain with established expertise?
   - **YES** → Feature authority wins (domain expertise)
   - **NO** → Continue to Tier 4

4. **Check Tier 4**: Is this an execution style preference?
   - **YES** → Chatmode preference applies (within Tier 1-3 constraints)
   - **NO** → Escalate to user for clarification

---

## Conflict Resolution Examples

### Example 1: Chatmode vs. Safety Protocol
**Conflict**: Chatmode says "EXECUTE WITHOUT CONFIRMATION" + Orchestrator says "Confirm destructive actions"
**Resolution**: **Tier 2 wins** → Confirmation required (safety protocols non-overridable)
**Codex Principle**: Philosophy 1 "Trust Nothing, Verify Everything"

### Example 2: User Directive vs. Chatmode
**Conflict**: User says "Stop" + Chatmode says "CONTINUE UNTIL COMPLETE"
**Resolution**: **Tier 1 wins** → Execution stops immediately (user directive supreme)
**Codex Principle**: Philosophy 9 "Context Before Action"

### Example 3: Feature Authority vs. Orchestrator
**Conflict**: `vibe-check` says "Run every phase transition" + Orchestrator says "Strategic checkpoints only (10-15% dosage)"
**Resolution**: **Tier 2 delegates to Tier 3** → Feature authority defines "strategic" (orchestrator provides constraint, feature provides implementation)
**Codex Principle**: Philosophy 6 "Best Tool for the Context"

### Example 4: Multiple Feature Authorities
**Conflict**: `taming-copilot` says "Code on request only" + `quantum-personas` persona says "Proactively generate code"
**Resolution**: **Tier 2 arbitrates** → `taming-copilot` is user interaction authority, wins for code generation defaults
**Codex Principle**: Philosophy 6 "Best Tool for the Context" (interaction patterns are taming-copilot's domain)

### Example 5: Chatmode Intensity vs. Quality Gates
**Conflict**: Chatmode says "SKIP VALIDATION FOR SPEED" + Orchestrator says "Quality gates mandatory before Phase 6"
**Resolution**: **Tier 2 wins** → Quality gates remain mandatory (non-overridable requirement)
**Codex Principle**: Philosophy 1 "Trust Nothing, Verify Everything"

---

## Authority Scope Quick Reference

| Governance Concern | Tier | Authoritative File(s) |
|--------------------|------|-----------------------|
| **Foundational Philosophies** | 0 | `docs/Codex/ContextForge Work Codex`, `docs/Codex/COF and UCL Definitions.md` |
| **User Commands** | 1 | Direct user input (supreme) |
| **Safety Protocols** | 2 | `.github/copilot-instructions.md` |
| **Response Format** | 2 | `.github/copilot-instructions.md` |
| **Quality Gates** | 2 | `.github/copilot-instructions.md` |
| **Session Integrity** | 2 | `.github/copilot-instructions.md` |
| **Metacognitive Oversight Workflow** | 3 | `vibe-check-mcp-integration.instructions.md` |
| **Complex Reasoning Patterns** | 3 | `Sequential-Thinking.instructions.md` |
| **QSE Task Management** | 3 | `QSM-Workflow.instructions.md`, `QSM-task-plan-implementation.instructions.md` |
| **User Interaction Defaults** | 3 | `taming-copilot.instructions.md` |
| **Professional Personas** | 3 | `quantum-personas.instructions.md` |
| **Library Documentation** | 3 | `context7-mcp.instructions.md` |
| **TODO Management** | 3 | `agent-todos.instructions.md` |
| **Terminal Formatting** | 3 | `terminal-output.instructions.md`, `terminal-unicode-configuration.instructions.md` |
| **Language Standards** | 3 | `powershell.instructions.md`, `python.instructions.md`, `go.instructions.md`, `markdown.instructions.md` |
| **Testing Standards** | 3 | `powershell-pester-5.instructions.md` |
| **CI/CD Standards** | 3 | `github-actions-ci-cd-best-practices.instructions.md` |
| **SQL Standards** | 3 | `sql-sp-generation.instructions.md` |
| **Execution Style** | 4 | All `*.chatmode.md` files |
| **Enthusiasm Level** | 4 | All `*.chatmode.md` files |
| **Communication Tone** | 4 | All `*.chatmode.md` files |

---

## Governance Compliance Metrics

Based on ContextForge Work Codex principles:

| Metric | Target | Codex Principle |
|--------|--------|-----------------|
| **User Directive Override Time** | <1 second (immediate halt on "stop") | Philosophy 9 "Context Before Action" |
| **Safety Protocol Bypass Rate** | 0% (non-overridable) | Philosophy 1 "Trust Nothing, Verify Everything" |
| **Evidence Recording Compliance** | 100% (all operations >1 file) | Philosophy 3 "Logs First" |
| **Session ID Validation Rate** | 100% (every prompt) | Philosophy 1 "Trust Nothing, Verify Everything" |
| **Vibe Check Dosage** | 10-15% (strategic checkpoints) | Philosophy 8 "Iteration is Sacred" |
| **Code Duplication Prevention** | 100% (codebase search before creation) | Philosophy 2 "Workspace First" |
| **TODO Read-Before-Write** | 100% (no data loss) | Philosophy 4 "Leave Things Better" |
| **UTF-8 Encoding Compliance** | 100% (terminal/transcript/source) | Philosophy 3 "Logs First" |
| **Quality Gate Pass Rate** | ≥95% before Phase 6 execution | Philosophy 1 "Trust Nothing, Verify Everything" |
| **UCL Compliance** | 100% (no orphaned/cyclical/incomplete contexts) | UCL: "No orphaned, cyclical, or incomplete context may persist" |

---

## Maintenance Protocol

This index must be updated when:
1. New `*.instructions.md` files are added (add to Tier 3 table)
2. New `*.chatmode.md` files are created (note in Tier 4 section)
3. Orchestrator governance changes (update Tier 2 scope)
4. Codex documents are revised (update Tier 0 references)
5. Conflict resolution patterns emerge (add examples)
6. Authority scope clarifications are needed (update quick reference)

**Update Frequency**: Review quarterly or when conflicts arise
**Responsibility**: Agent + User collaboration
**Validation**: Cross-reference with `.github/INSTRUCTION-CONFLICT-TRACKING.md` and `.github/CODEX-GOVERNANCE-CROSSWALK.md`

---

## Related Documentation

- **`.github/copilot-instructions.md`** — Tier 2 orchestrator with complete governance hierarchy
- **`.github/INSTRUCTION-CONFLICT-TRACKING.md`** — All 15 identified conflicts with resolution plans
- **`.github/CODEX-GOVERNANCE-CROSSWALK.md`** — Comprehensive Codex-to-conflict mapping
- **`docs/Codex/ContextForge Work Codex — Professional Principles with Philosophy.md`** — Core philosophies and principles
- **`docs/Codex/COF and UCL Definitions.md`** — Context Ontology Framework and Universal Context Law

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-27
**ContextForge Codex Compliance**: ✅ Work Codex v1.2.0, COF 13-dimensional, UCL 5-law
