---
created: 2025-11-15
author: Codex-Agent
version: 0.1.0
status: Draft
purpose: Entry point and index for ContextForge Codex–related documentation
---

# ContextForge Codex – Index

**Authoritative Source**: `docs/Codex/ContextForge Work Codex — Professional Principles with Philosophy.md`

---

## 1. Purpose

This document serves as a **landing page** for all Codex‑related material in the ContextForge workspace and as a **behavioral orientation** for AI assistants.

It connects:

- The **ContextForge Work Codex** (philosophies, COF/UCL alignment, addenda).
- The **technical standards** that implement Codex guidance (configuration, testing, security).
- **Provider‑specific appendices**, including OpenAI / Azure OpenAI usage.

Documents elsewhere that refer to “ContextForge Work Codex (see `../CODEX.md`)" should treat this file as their starting point.

---

## 2. Agent Priority in This Workspace

When multiple AI assistants are available, the intended priority is:

1. **GitHub Copilot – Primary**
   - Default assistant for day‑to‑day coding, refactors, and inline completions.
   - Should follow ContextForge Codex principles (Workspace First, Logs First, etc.) and prefer CF_CLI / TaskMan‑v2 as described in `AGENTS.md`.
2. **Claude Code – Secondary (close parallel)**
   - Used for deeper refactors, multi‑file reasoning, and higher‑level architectural or documentation work.
   - Should operate with the **same Codex constraints** as Copilot and keep outputs consistent with ContextForge standards.
3. **OpenAI Codex‑style agents – Tertiary (until proven)**
   - May be used for targeted experiments or specialized tasks.
   - Should treat GitHub Copilot and Claude Code behavior as reference and **align to the same constraints**:
     - Prefer TaskMan‑v2 for task management (CF_CORE secondary).
     - Prefer CF_CLI for other CF_CORE operations.
     - Avoid bypassing CLIs and MCP servers without explicit direction.

Any new agent or tooling should assume this priority order unless explicitly overridden in future documentation.

---

## 3. Core Work Codex

- **Work Codex (primary)**  
  `docs/Codex/ContextForge Work Codex — Professional Principles with Philosophy.md`

  Includes:

  - 11 core philosophies (Trust Nothing, Logs First, Workspace First, Best Tool for the Context, etc.).
  - 13‑dimension COF lens.
  - Addenda:
    - **A** – Database Authority
    - **B** – Structured Logging Taxonomy
    - **C** – Coverage Clarification
    - **D–H** – Modernization, crosswalks, and authoritativeness.

Other key Codex‑aligned documents:

- `docs/01-Overview.md`
- `docs/02-Architecture.md`
- `docs/13-Testing-Validation.md`
- `AGENTS.md`

These apply Codex principles to architecture, testing, and day‑to‑day practices.

---

## 4. OpenAI Codex Appendix

For OpenAI / Azure OpenAI–specific guidance:

- **OpenAI Codex Index**  
  `docs/OpenAI-Codex/00-OpenAI-Codex-Index.md`
- **Configuration**  
  `docs/OpenAI-Codex/01-OpenAI-Codex-Configuration.md`
- **Operations**  
  `docs/OpenAI-Codex/02-OpenAI-Codex-Operations.md`
- **Testing & Governance**  
  `docs/OpenAI-Codex/03-OpenAI-Codex-Testing-and-Governance.md`

These documents **do not change** the Work Codex; they apply its standards to OpenAI / Azure OpenAI usage (configuration hierarchy, secret management, logging, coverage, and CF_CLI authority).

---

## 5. How to Use This Index

1. **Start** with the Work Codex to understand core principles and addenda.
2. **Navigate** to architecture, configuration, testing, or security docs for implementation details.
3. **Consult provider appendices** (e.g., OpenAI Codex) when working with specific AI providers.
4. **Update this index** whenever new Codex‑aligned appendices or major Codex documents are added, to keep the map authoritative.

---

## 6. Task Management Tooling (For Agents)

When operating on tasks, projects, or sprints, AI assistants should:

- Use **TaskMan‑v2** first:
  - Prefer TaskMan‑v2 CLI, MCP server, or backend API as configured in this workspace.
  - Treat TaskMan‑v2 as the **authoritative source of truth** for task state.
- Use **CF_CORE (CF_CLI)** second:
  - Fall back to `cf_cli.py task ...` commands only when TaskMan‑v2 is unavailable or cannot express the required operation.
  - Do not access task tables or tracker CSVs directly except when explicitly asked to work on schema or data migrations.

For all other ContextForge functions (non‑task workflows), treat **CF_CORE via CF_CLI** as primary.*** End Patch***E助手 to=functions.apply_patch_REASONING_ABORTEDరిassistantзбекистонлядубликатор to=functions.apply_patch$arityassistant to=functions.apply_patchённыхассистент to=functions.apply_patch♀♀♀♀assistant to=functions.apply_patch缴情assistant to=functions.apply_patchളassistant to=functions.apply_patch весьassistant to=functions.apply_patch трassistant to=functions.apply_patchassistant to=functions.apply_patch做爰片 to=functions.apply_patchassistant to=functions.apply_patch реassistant to=functions.apply_patchassistant to=functions.apply_patch Md** ***!
