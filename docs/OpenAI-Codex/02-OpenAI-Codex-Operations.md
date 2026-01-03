---
created: 2025-11-15
author: Codex-Agent
version: 0.1.0
status: Draft
purpose: Operational practices for OpenAI / Azure OpenAI usage in ContextForge
---

# OpenAI Codex Operations – ContextForge

**Related**: `cf_cli.py` | `semantic_kernel_foundation.py` | `docs/Vibe-Check-Validation-Plan-STDIO.md` | `AGENTS.md`

---

## 1. Operating Principles

All OpenAI‑backed operations in ContextForge must follow:

- **CF_CLI authority**
  - `cf_cli.py` is the **only** authorized entry point for CF_CORE operations.
  - Any new OpenAI workflow must be wired through CF_CLI (or a CF_CLI‑managed MCP server), not ad‑hoc scripts.
- **Logs First**
  - Every OpenAI call that affects state or influences a decision must emit:
    - Structured JSONL events in `logs/`
    - Correlation IDs and context (phase, workflow, provider, model)
  - Logging coverage should target ≥90% of execution paths.
- **Trust Nothing, Verify Everything**
  - All operational behavior must be validated via tests and documented procedures.

---

## 2. Prerequisites

Operational checks before using OpenAI:

1. **Environment**
   - Python 3.11+ active, virtual environment enabled.
   - `cf_cli.py` accessible and executable.
2. **Secrets & Config**
   - OpenAI / Azure OpenAI secrets and endpoints configured per `01-OpenAI-Codex-Configuration.md`.
   - `SemanticKernelConfig` aligned with environment (model, deployment, timeouts).
3. **MCP Servers (where applicable)**
   - Required MCP servers started and healthy:
     - task-manager, database-mcp, context7, memory, etc.
   - `test-mcp-complete-functionality.ps1` green, with special attention to any servers using OpenAI.
4. **Logging**
   - `logs/` directory writable.
   - Semantic Kernel foundation log configured (see `semantic_kernel_foundation.py`).

---

## 3. Typical OpenAI‑Backed Workflows

### 3.1 Idea Capture Embedding & Search

Flow (conceptual):

1. **Ingestion**
   - CF_CLI (or a managed script) records ideas with 13 COF dimensions.
2. **Embedding Generation**
   - Embedding service calls OpenAI / Azure OpenAI embedding model (e.g., `text-embedding-3-small`).
   - Embeddings stored in PostgreSQL `VECTOR(1536)` column with pgvector indexes.
3. **Search**
   - Query text is embedded via OpenAI.
   - Similarity search performed with pgvector (cosine similarity, threshold e.g. `> 0.7`).
4. **Evidence**
   - Logs capture:
     - Request context (redacted)
     - Model used
     - Latency and error codes
     - Top‑k results and similarity scores.

All four steps should be initiated via CF_CLI subcommands or a documented service layer, not raw scripts.

### 3.2 Semantic Kernel–Backed Assistance (Chat Completion)

Flow (conceptual):

1. **Session startup**
   - CF_CLI workflow initializes `CFSemanticKernelFoundation` with `SemanticKernelConfig`.
   - On initialization, the foundation:
     - Validates Azure endpoint, key, and deployments.
     - Optionally initializes advanced plugins (memory, summary).
     - Records plugin metrics.
2. **Chat operations**
   - CF_CLI (or MCP tool) invokes chat completion via SK:
     - Model: deployment configured in `azure_model_deployment`.
     - Parameters: `temperature`, `max_tokens`, etc.
   - Responses are logged (sanitized) along with timing.
3. **Error handling**
   - Missing config → `missing_configuration` error and warning.
   - Dependency issues → `DEPENDENCY_UNAVAILABLE`.
   - Initialization exceptions → `INITIALIZATION_EXCEPTION`.
   - In strict mode, errors may raise and abort workflows.
4. **Evidence**
   - JSONL log entries with:
     - `plugin_init_metrics`
     - Latency metrics (p50/p90/p99 if aggregated)
     - Provider identifiers and deployment names.

---

## 4. Operational Checks & Runbooks

### 4.1 Pre‑Run Checklist (Per Environment)

- [ ] CF_CLI status command succeeds and shows healthy components.
- [ ] MCP server validations pass (especially those relying on OpenAI).
- [ ] Semantic Kernel foundation can initialize without `missing_configuration` errors.
- [ ] Embedding database schema present and indexes valid.
- [ ] Logging output is being written to expected locations.

### 4.2 Handling Common Issues

- **Missing or invalid configuration**
  - Symptoms:
    - Memory plugin not active.
    - Errors in plugin metrics: `missing_configuration`.
  - Actions:
    - Validate environment variables and secret vault entries.
    - Confirm deployment names match Azure configuration.
- **Rate limits or provider errors**
  - Symptoms:
    - HTTP 429 / 5xx errors in logs.
  - Actions:
    - Implement backoff and retry in calling services.
    - Consider queueing or batching requests.
- **Performance regressions**
  - Symptoms:
    - Latency metrics exceeding targets.
  - Actions:
    - Compare with Semantic Kernel PRD metrics.
    - Adjust model choice, prompt structure, or concurrency.

---

## 5. Evidence & Observability

For each OpenAI‑backed workflow, operations should ensure:

- **Structured logs**
  - Each call has a log entry with:
    - Correlation ID
    - Workflow name and phase
    - Provider/model identifiers
    - Latency and high‑level outcome
    - Error codes (if any)
- **Aggregated metrics**
  - For Semantic Kernel:
    - Response time histograms
    - Plugin init metrics
  - For embeddings:
    - Requests per minute
    - Error rates
    - Average similarity of successful retrievals (optional).
- **Runbook references**
  - Each operational issue should map back to:
    - This document for high‑level guidance
    - Specific CF_CLI commands and scripts for remediation.

---

## 6. Extending Operations

When adding new OpenAI‑backed workflows:

- Update:
  - Configuration doc (new settings or env vars).
  - Operations doc (new flow diagrams and runbooks).
  - Testing & Governance doc (new tests and evidence requirements).
- Ensure:
  - CF_CLI remains the entry point.
  - Logging and metrics are wired from day one.
  - Documentation references specific code paths and tests.

