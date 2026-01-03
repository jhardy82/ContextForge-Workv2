---
created: 2025-11-15
author: Codex-Agent
version: 0.1.0
status: Draft
purpose: Index for OpenAI Codex–specific documentation within ContextForge
---

# OpenAI Codex – Documentation Index

**Related**: `docs/Codex/ContextForge Work Codex — Professional Principles with Philosophy.md` | `docs/11-Configuration-Management.md` | `docs/13-Testing-Validation.md`

---

## 1. Purpose

This subdirectory (`docs/OpenAI-Codex/`) provides **provider‑specific guidance** for using OpenAI / Azure OpenAI capabilities inside the ContextForge workspace, while remaining fully aligned with:

- The **ContextForge Work Codex** (core philosophies + addenda)
- The **Configuration Management** standards (hierarchy, secrets, domains)
- The **Testing & Validation** framework (coverage, evidence, governance)
- The **CF_CLI authority model** defined in `AGENTS.md` (CF_CLI as the only operational entry point)

These documents do **not** replace the Work Codex; they are a **provider appendix** that applies Codex principles to OpenAI‑backed workflows (chat completion, embeddings, and Semantic Kernel usage).

---

## 2. Scope

In scope for this folder:

- Configuration of OpenAI / Azure OpenAI settings (API keys, endpoints, deployments, and model choices) as used by:
  - `semantic_kernel_foundation.py` (`SemanticKernelConfig`)
  - Idea Capture / pgvector search (`docs/06-Idea-Capture-System.md`)
  - Future OpenAI‑backed workflows (e.g., semantic search, task similarity)
- Operational workflows that **use CF_CLI + MCP** to drive OpenAI calls and collect evidence (JSONL logs, metrics, AAR artifacts).
- Testing and governance policies specific to OpenAI usage (coverage expectations, performance SLOs, failure handling).

Out of scope:

- The core philosophical principles themselves (defined in the Work Codex).
- Non‑OpenAI providers (Gemini, OpenRouter, local models) – these will have their own provider appendices if needed.

---

## 3. Document Map (OpenAI Codex)

- **01 – Configuration**
  - `docs/OpenAI-Codex/01-OpenAI-Codex-Configuration.md`
  - How OpenAI / Azure OpenAI configuration integrates with:
    - `SemanticKernelConfig` (endpoint, deployments, temperature, max_tokens)
    - Idea Capture embeddings (`text-embedding-3-small`, pgvector)
    - Configuration hierarchy and secret management standards.

- **02 – Operations**
  - `docs/OpenAI-Codex/02-OpenAI-Codex-Operations.md`
  - Day‑to‑day operational guidance for:
    - Running CF_CLI + MCP workflows that call OpenAI
    - Emitting JSONL evidence for Codex‑backed flows
    - Troubleshooting and environment validation.

- **03 – Testing & Governance**
  - `docs/OpenAI-Codex/03-OpenAI-Codex-Testing-and-Governance.md`
  - Test plans and governance criteria for:
    - Coverage and logging targets (Codex Addendum C)
    - Performance and reliability SLOs
    - Provider‑specific failure modes and escalation paths.

---

## 4. Relationship to ContextForge Work Codex

The **Work Codex** remains the **authoritative source** for:

- Core philosophies:
  - **Trust Nothing, Verify Everything**
  - **Workspace First**
  - **Logs First**
  - **Best Tool for the Context**
- Addendum A–H (database authority, logging taxonomy, coverage targets, authoritativeness checklist).

All OpenAI Codex documents in this folder must:

1. **Reference** the Work Codex where they derive standards (coverage, logging, authority).
2. **Demonstrate evidence** that OpenAI usage satisfies those standards (tests, logs, metrics).
3. **Respect CF_CLI authority** – any operational examples must route through `cf_cli.py` or approved MCP servers, never ad‑hoc scripts alone.

---

## 5. How to Use This Folder

1. Start with the **Work Codex** to understand the philosophical and governance baseline.
2. Read this index to locate the OpenAI‑specific appendix you need:
   - Configuration, Operations, or Testing & Governance.
3. When adding or updating OpenAI usage:
   - Update the relevant file(s) here.
   - Ensure you cite evidence (logs, tests, metrics) and keep CF_CLI as the operational entry point.

