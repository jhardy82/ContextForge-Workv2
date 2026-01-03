---
created: 2025-11-15
author: Codex-Agent
version: 0.1.0
status: Draft
purpose: Configuration standards for OpenAI / Azure OpenAI usage in ContextForge
---

# OpenAI Codex Configuration – ContextForge

**Related**: `semantic_kernel_foundation.py` | `docs/06-Idea-Capture-System.md` | `docs/11-Configuration-Management.md` | `docs/Codex/ContextForge Work Codex — Professional Principles with Philosophy.md`

---

## 1. Goals

OpenAI / Azure OpenAI configuration in ContextForge must:

- Honor the **Configuration Philosophy** and **Hierarchy** in `docs/11-Configuration-Management.md`.
- Respect **secret‑refs only** (no plaintext API keys or endpoints in source control).
- Integrate cleanly with CF_CLI and MCP orchestration (no direct, unmanaged calls in production workflows).
- Provide enough structure that tests and logs can prove correct configuration for both:
  - **Chat completion** (via `CFSemanticKernelFoundation`)
  - **Embeddings** (Idea Capture, pgvector search).

---

## 2. Configuration Hierarchy (Applied to OpenAI)

ContextForge uses a layered hierarchy:

1. **CLI arguments** (highest priority)
2. **Environment variables**
3. **.env files** (dev convenience)
4. **Defaults in code**

For OpenAI / Azure OpenAI, this maps to:

- **Environment variables (recommended)**
  - `OPENAI_API_KEY` (for public OpenAI, if/when used)
  - `OPENAI_BASE_URL` or `OPENAI_API_BASE` (if non‑default)
  - `AZURE_AI_ENDPOINT` (Azure AI Foundry endpoint URL)
  - `AZURE_AI_KEY` (Azure API key)
  - Optional deployment/environment hints (e.g., `AZURE_CHAT_DEPLOYMENT`, `AZURE_EMBEDDING_DEPLOYMENT`).
- **SemanticKernelConfig fields** (code defaults / overrides)
  - `azure_endpoint: str | None`
  - `azure_api_key: str | None`
  - `azure_model_deployment: str` (default `"gpt-4"`)
  - `azure_embedding_deployment: str` (default `"text-embedding-ada-002"`)
  - `max_tokens: int` (default `1000`)
  - `temperature: float` (default `0.7`)

The implementation in `semantic_kernel_foundation.py` applies the hierarchy for the Semantic Kernel memory plugin as:

- Use `SemanticKernelConfig.azure_endpoint` or `AZURE_AI_ENDPOINT`
- Use `SemanticKernelConfig.azure_api_key` or `AZURE_AI_KEY`
- Require a configured `azure_embedding_deployment`

If any of these are missing, the memory plugin records a **`missing_configuration`** error and may raise in strict mode.

---

## 3. Secret Management Requirements

Per `docs/11-Configuration-Management.md` and `docs/12-Security-Authentication.md`:

- **Secret refs only**:
  - API keys must be stored in:
    - PowerShell SecretManagement vaults (`Microsoft.PowerShell.SecretManagement`), or
    - Azure Key Vault / AWS Secrets Manager (for production), or
    - Environment variables injected by CI/CD.
  - They must **not** appear in:
    - Git‑tracked `.env` files
    - Markdown examples (except as placeholders)
    - Logs or error messages.
- Suggested pattern:
  - Local dev:
    - Store `OPENAI_API_KEY` or `AZURE_AI_KEY` in a SecretManagement vault.
    - Export to environment for dev shell sessions using a short helper script.
  - CI / Production:
    - Configure Key Vault / Secrets Manager → CI runner → environment variables.

All examples in this document use placeholder values like `YOUR_AZURE_AI_KEY` and must be replaced via secret managers, not directly in code.

---

## 4. Chat Completion Configuration (Semantic Kernel)

The `CFSemanticKernelFoundation` component (`semantic_kernel_foundation.py`) provides the main orchestration layer for chat completion via Azure AI / OpenAI models, with configuration encapsulated in `SemanticKernelConfig`.

Key fields:

- `azure_endpoint`: Azure AI endpoint URL (or `AZURE_AI_ENDPOINT`)
- `azure_api_key`: Azure AI key (or `AZURE_AI_KEY`)
- `azure_model_deployment`: model deployment name (e.g., `"gpt-4"` or `"gpt-4o"`), as configured in Azure AI
- `max_tokens`: upper bound on completion tokens per request
- `temperature`: sampling temperature
- `use_default_credential`: whether to use `DefaultAzureCredential` instead of API key
- `enable_quality_gates`, `enable_cof_validation`: enforcement toggles for constitutional checks

**Configuration guidance:**

- For **deterministic tests**, prefer:
  - `temperature = 0.0`
  - Fixed prompts and seed data
  - Captured JSONL logs for replay.
- For **production flows**:
  - Use model deployments with appropriate latency and cost characteristics.
  - Align `max_tokens` with prompt sizes and SLO requirements.
  - Ensure environment values are consistent across environments (dev/stage/prod).

Because `SemanticKernelConfig` is a Python dataclass, it is safe to extend in the future to include OpenAI‑specific parameters (e.g., `top_p`, `frequency_penalty`) as needed, as long as:

- CF_CLI remains the authoritative orchestration entry point.
- Changes are reflected in configuration docs and tests.

---

## 5. Embedding Configuration (Idea Capture + pgvector)

The Idea Capture system (`docs/06-Idea-Capture-System.md`) assumes:

- Embeddings generated using **OpenAI `text-embedding-3-small`** (1536 dimensions).
- Storage in PostgreSQL using **pgvector**:
  - Column: `embedding VECTOR(1536)`
  - Index: `USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)`

Key configuration concerns:

- **Model selection**
  - Primary: `"text-embedding-3-small"` (as referenced in the docs).
  - Any change must update:
    - Database schema (vector dimension)
    - Index definitions
    - Application code using the embeddings.
- **Thresholds**
  - Example query uses a similarity threshold of `> 0.7` for candidate retrieval.
  - Thresholds should be configurable (env or config) to allow tuning.
- **Batching and rate limits**
  - When embedding many ideas, batching and backoff strategies should be configurable to respect OpenAI / Azure rate limits.

All embedding calls must be made through managed modules (e.g., Semantic Kernel or a dedicated embedding helper) and integrated with ContextForge logging (JSONL + database metrics).

---

## 6. CF_CLI and MCP Integration

While this document focuses on configuration values, all **operational use** of OpenAI capabilities must:

- Be invoked via **CF_CLI** commands or approved MCP servers (per `AGENTS.md`).
- Emit structured logs under `logs/` with:
  - Correlation IDs
  - Request context (redacted of secrets)
  - Provider details (model, endpoint, latency, token counts where available).

Examples:

- CF_CLI commands that trigger:
  - Idea Capture enrichment with embeddings.
  - Semantic Kernel–driven summarization or assistance.
- MCP servers (e.g., context7, vibe-check, task-manager) that internally use OpenAI / Azure OpenAI.

Provider configuration should be surfaced via:

- CF_CLI diagnostics (e.g., `cf_cli.py status --rich` extended with AI provider status).
- MCP doctor/health commands (as in `docs/Vibe-Check-Validation-Plan-STDIO.md`).

---

## 7. Configuration Checklist

Before enabling OpenAI / Azure OpenAI in a new environment:

1. **Secrets**
   - [ ] `OPENAI_API_KEY` or `AZURE_AI_KEY` stored in a secret manager.
   - [ ] No API keys in `.env`, source code, or logs.
2. **Endpoints & Deployments**
   - [ ] `AZURE_AI_ENDPOINT` configured (or `SemanticKernelConfig.azure_endpoint`).
   - [ ] Chat deployment name set (`azure_model_deployment`).
   - [ ] Embedding deployment name set (`azure_embedding_deployment`).
3. **Database**
   - [ ] `embedding VECTOR(1536)` (or correct dimension) in idea tables.
   - [ ] pgvector indexes created and healthy.
4. **CF_CLI / MCP**
   - [ ] CF_CLI status surfaces provider health.
   - [ ] Relevant MCP servers configured and passing stdio tests.
5. **Evidence**
   - [ ] JSONL logs show successful calls with latency and result summaries.
   - [ ] Tests cover configuration error paths (missing/invalid config) and success paths.

