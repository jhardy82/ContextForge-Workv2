---
created: 2025-11-15
author: Codex-Agent
version: 0.1.0
status: Draft
purpose: Testing and governance framework for OpenAI / Azure OpenAI usage in ContextForge
---

# OpenAI Codex Testing & Governance – ContextForge

**Related**: `docs/13-Testing-Validation.md` | `docs/Codex/ContextForge Work Codex — Professional Principles with Philosophy.md` | `docs/PRD-SemanticKernelFoundation.md` | `semantic_kernel_foundation.py`

---

## 1. Philosophy

From the Work Codex:

- **Trust Nothing, Verify Everything** – Evidence (tests + logs) closes the loop of trust.
- **Logs First** – Truth lives in records, not assumptions.
- **Best Tool for the Context** – Use CF_CLI and existing test harnesses wherever possible.

This document applies those principles to **OpenAI / Azure OpenAI** usage.

---

## 2. Coverage Targets (Provider‑Specific)

ContextForge’s general coverage targets (Codex Addendum C + `docs/13-Testing-Validation.md`) apply to OpenAI workflows as follows:

- **Python (OpenAI‑relevant code paths)**
  - Unit tests: ≥80% line coverage, with special focus on:
    - Configuration handling (`SemanticKernelConfig`).
    - Error handling paths (missing config, dependency failures, provider errors).
  - Integration tests:
    - Cover end‑to‑end flows when using mock or sandbox providers.
  - System / acceptance tests:
    - Validate OpenAI‑backed workflows via CF_CLI or MCP interfaces.
- **Logging coverage**
  - ≥90% of OpenAI‑related execution paths must emit structured logs.
- **Evidence**
  - Coverage reports and log scans must be produced and stored under `artifacts/` or equivalent.

---

## 3. Test Matrix

### 3.1 Configuration & Initialization

Tests should validate:

- **Happy path**
  - All required secrets and endpoints present.
  - SemanticKernel foundation initializes without errors.
  - Plugins (memory, summary) initialize when enabled.
- **Missing configuration**
  - No endpoint or key → `missing_configuration` error and warning.
  - Missing deployment name → plugin not active, error recorded.
- **Strict vs non‑strict**
  - When `strict_plugin_init=True`, plugin init failures raise `PluginInitializationError`.
  - When `False`, failures are logged and metrics include error codes.

### 3.2 Chat Completion Behavior

Tests (unit / integration) should cover:

- Deterministic responses:
  - `temperature=0.0` with mock or recorded responses.
  - Validation of prompt construction and response shape.
- Error handling:
  - Timeouts or provider errors mapped to internal error taxonomy.
  - Retrying or fail‑fast behavior (as configured).

### 3.3 Embedding Generation & Search

Tests should validate:

- Embedding service:
  - Correct handling of input text (including edge cases).
  - Correct handling of provider errors and rate limits.
- Database integration:
  - Schema matches embedding dimension.
  - pgvector similarity search queries behave as expected on sample data.

---

## 4. Governance & Evidence Requirements

For each OpenAI‑backed capability, governance requires:

- **Documented configuration**
  - Referenced in `01-OpenAI-Codex-Configuration.md`.
  - Linked to environment variables, secret managers, and CF_CLI flags where applicable.
- **Logged behavior**
  - JSONL logs containing:
    - Provider, model/deployment identifiers.
    - Latency and outcome (success/error code).
    - Correlation IDs for tracing across components.
- **Tests**
  - Mapped to requirements from `docs/PRD-SemanticKernelFoundation.md` (for SK) and any related PRDs.
  - Executable via standard test commands (pytest, CF_CLI test harnesses).
- **Review & sign‑off**
  - Changes to OpenAI configurations or usage patterns should:
    - Update this document and associated config/ops docs.
    - Be reviewed with an eye to coverage, logging, and security impacts.

---

## 5. Failure Modes & Escalation

Common failure modes:

- **Configuration errors**
  - Missing or incorrect endpoint, key, or deployment.
- **Secret management issues**
  - Inaccessible secret vaults, expired keys.
- **Provider‑side issues**
  - Rate limits, outages, changes in model behavior.

For each, tests should:

- Reproduce the failure scenario (with mocks where appropriate).
- Assert that:
  - The failure is **detected** and **logged**.
  - The system either:
    - Fails fast with clear error messages (strict contexts), or
    - Degrades gracefully with clear warnings (non‑strict contexts).

Escalation:

- Persistent failures or regressions in OpenAI behavior should:
  - Be captured in AARs and QSE artifacts.
  - Trigger review of configuration, quotas, and fallback strategies.

---

## 6. Extending Testing & Governance

When new OpenAI‑backed features are added:

- Update this document with:
  - New test cases (what is being validated).
  - New metrics or logs required for evidence.
- Ensure:
  - Tests can run in environments without live OpenAI access (using mocks or alternate providers).
  - Production validation can be performed safely with minimal, controlled real calls.

This keeps OpenAI usage in ContextForge aligned with the broader constitutional and Codex‑based governance model.

