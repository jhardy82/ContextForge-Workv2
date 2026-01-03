# cf_core Centralized Logging Design Prompt

**Version:** 1.0.0
**Created:** 2025-12-30
**Authority:** ContextForge Work Codex, COF 13D Framework
**Project ID:** P-CFCORE-LOGGING-CONSOLIDATION

---

## Mission Statement

Design and document a **centralized logging solution** for the `cf_core` namespace that consolidates 5+ fragmented logging implementations while maintaining 100% backward compatibility, implementing correlation ID propagation per CF-133, and ensuring evidence bundle compliance with UCL Law 3.

---

## Background: Current State Analysis

### Logging Implementation Inventory

| Location | Purpose | Status | Lines |
|----------|---------|--------|-------|
| `python/services/unified_logger.py` | Primary unified logger (structlog) | **ACTIVE** | 165 |
| `cf_core/logger_provider.py` | RuntimeBuilder + correlation tracking | **ACTIVE** | 610 |
| `src/unified_logging/core.py` | Comprehensive engine with async queue, hash chain | **ACTIVE** | 732 |
| `src/unified_logging/evidence.py` | Evidence bundle capture | **ACTIVE** | ~200 |
| `src/unified_logging/__init__.py` | Package facade | **ACTIVE** | 89 |
| `src/unified_logger.py` | Deprecated shim → python.services | **DEPRECATED** | 10 |
| `python/ulog/__init__.py` | Deprecated shim → python.services | **DEPRECATED** | 10 |
| `python/unified_logger.py` | Deprecated shim → python.services | **DEPRECATED** | 10 |
| `cf_tracker/unified_logger.py` | Tracker-specific adapter | **ACTIVE** | 205 |
| `TaskManMcpIntegration/modules/ContextForge.Observability/*.psm1` | PowerShell bridge | **ACTIVE** | 549 |

### Problem Statement

1. **Fragmentation**: 5+ active implementations with overlapping functionality
2. **Inconsistent APIs**: `ulog()` vs `logger.info()` vs `get_logger()` patterns
3. **Correlation Gap**: Correlation ID propagation incomplete across CLI → Runtime → Plugins
4. **Evidence Compliance**: RFC 8785 canonical serialization not enforced consistently
5. **No Single Authority**: No canonical import path for new code

---

## ContextForge Codex Requirements

### Core Principles (from `.github/copilot-instructions.md`)

1. **"Logs First"** — Truth lives in records, not assumptions
2. **"Trust Nothing, Verify Everything"** — Evidence closes trust loops
3. **Context Before Action** — Understanding precedes implementation
4. **Iteration is Sacred** — Progress spirals, not straight lines

### LOG-001 Baseline Event Taxonomy

All implementations MUST emit these events with required fields:

| Event | When | Required Fields |
|-------|------|-----------------|
| `session_start` | Session initialization | `session_id`, `project_id` |
| `task_start` | Each substantive unit begins | `task_id`, `task_name` |
| `decision` | Any branching/reuse/risk classification | `decision_type`, `selected`, `rationale` |
| `artifact_touch_batch` | Read operations ≥1 item | `artifacts[]`, `count` |
| `artifact_emit` | Each created/modified artifact | `path`, `hash`, `size_bytes` |
| `warning` / `error` | Structured, one-line JSON each | `message`, `remediation[]` |
| `task_end` | With outcome and duration | `task_id`, `duration_ms` |
| `session_summary` | Aggregated counts, failures, evidence | `tasks_completed`, `evidence_hash` |

**Coverage Target:** ≥90% of execution paths produce structured logs

### CF-133 Correlation Rules

```
CLI Entry Point
    │
    ├── RuntimeBuilder.with_correlation_id(id)
    │       │
    │       ▼
    │   Runtime.logger(plugin_id)
    │       │
    │       ▼
    │   Plugin Logger (correlation_id IMMUTABLE)
    │
    └── Environment Bridge
            CF_SESSION_ID → PowerShell ↔ Python
            CF_TRACE_ID → Cross-language correlation
```

### UCL Law 3: Evidence Requirements

- All contexts MUST have evidence bundles
- Evidence bundles use SHA-256 hashing
- JSONL format with RFC 8785 canonical serialization
- Directory structure: `.QSE/v2/Evidence/{project_id}/{session_id}/`

---

## Deliverables Required

### 1. PRD: cf_core.logging Module

**Document:** `docs/prd/PRD-CFCORE-LOGGING.md`

**Sections:**
1. **Executive Summary** - Single paragraph on consolidation goals
2. **User Stories** - Developer, CLI user, MCP server author personas
3. **Functional Requirements**
   - FR-001: Unified `get_logger()` function with correlation binding
   - FR-002: `ulog()` function with LOG-001 compliance
   - FR-003: Evidence bundle generation with SHA-256 hashing
   - FR-004: Backward-compatible shims for existing imports
   - FR-005: PowerShell ↔ Python correlation bridge
   - FR-006: Async queue-based file writing
   - FR-007: Environment variable configuration (preserved)
4. **Non-Functional Requirements**
   - NFR-001: <5ms overhead per log call
   - NFR-002: Thread-safe and async-safe (ContextVar)
   - NFR-003: 100% backward compatibility during migration
   - NFR-004: Zero data loss during rotation
5. **API Contract**
   ```python
   # Public API
   from cf_core.logging import get_logger, ulog, correlation_context

   logger = get_logger(__name__)
   logger.info("event_name", key="value")

   ulog("task_start", "process_file", result="started", task_id="T-001")

   with correlation_context(correlation_id="abc123"):
       # All logs in this context inherit correlation_id
       logger.info("scoped_event")
   ```
6. **Migration Matrix**
   | Old Import | New Import | Timeline |
   |------------|------------|----------|
   | `from python.services.unified_logger import logger` | `from cf_core.logging import get_logger` | Phase 2 |
   | `from src.unified_logging import ulog` | `from cf_core.logging import ulog` | Phase 2 |
   | `from cf_core.logger_provider import RuntimeBuilder` | `from cf_core.logging.runtime import RuntimeBuilder` | Phase 3 |
7. **Success Criteria**
   - All 47 `ulog()` call sites work unchanged
   - Correlation ID appears in 100% of MCP server logs
   - Evidence bundles pass SHA-256 verification
   - LOG-001 gap detection triggers on missing events

---

### 2. ADR-002: Correlation ID Strategy

**Document:** `docs/adr/ADR-002-correlation-id-strategy.md`

**Sections:**
1. **Status:** Proposed
2. **Context:** Multiple correlation patterns exist; need unified approach
3. **Decision:**
   - Use ContextVar for thread/async-safe propagation
   - Environment variables (`CF_SESSION_ID`, `CF_TRACE_ID`, `UNIFIED_LOG_CORRELATION`) as fallback
   - Precedence: ContextVar override > Environment > Auto-generated UUID
4. **Consequences:**
   - Existing `RuntimeBuilder` pattern preserved for MCP
   - PowerShell bridge continues working via env vars
   - New code uses ContextVar context managers
5. **Implementation:**
   ```python
   from contextvars import ContextVar
   from contextlib import contextmanager

   _CORRELATION_VAR: ContextVar[str | None] = ContextVar("cf_correlation", default=None)

   def get_correlation_id() -> str:
       """Resolution order: ContextVar > Env > UUID"""
       if (ctx := _CORRELATION_VAR.get()) is not None:
           return ctx
       if (env := os.getenv("UNIFIED_LOG_CORRELATION")):
           return env
       if (session := os.getenv("CF_SESSION_ID")):
           return session
       return str(uuid.uuid4())

   @contextmanager
   def correlation_context(correlation_id: str):
       token = _CORRELATION_VAR.set(correlation_id)
       try:
           yield
       finally:
           _CORRELATION_VAR.reset(token)
   ```

---

### 3. ADR-003: Evidence Bundle Compliance

**Document:** `docs/adr/ADR-003-evidence-bundle-compliance.md`

**Sections:**
1. **Status:** Proposed
2. **Context:** UCL Law 3 requires evidence for all contexts
3. **Decision:**
   - RFC 8785 canonical JSON serialization for hash stability
   - SHA-256 hash chain (optional via `UNIFIED_LOG_HASH_CHAIN=1`)
   - Mandatory `evidence_hash` field on bundle close
   - Auto-capture triggers: WARN/ERROR events or explicit request
4. **RFC 8785 Requirements:**
   | Requirement | Implementation |
   |-------------|----------------|
   | Key ordering | UTF-16 code unit lexicographic sort |
   | Whitespace | None (compact) |
   | Unicode | UTF-8 throughout |
   | Integer range | ±(2^53 - 1) per I-JSON |
5. **Directory Structure:**
   ```
   .QSE/v2/Evidence/{project_id}/{session_id}/
   ├── execution_plan.yaml
   ├── validation_results.json
   └── evidence_bundle.jsonl  # SHA-256 hashed
   ```
6. **Implementation:**
   ```python
   import hashlib
   import json

   def canonicalize(data: dict) -> str:
       """RFC 8785 canonical JSON."""
       return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

   def hash_evidence(data: dict) -> str:
       """SHA-256 of canonical form."""
       canonical = canonicalize(data)
       return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
   ```

---

### 4. Migration Plan

**Document:** `docs/plans/MIGRATION-CFCORE-LOGGING.md`

**Phases:**

| Phase | Duration | Deliverables | Risk |
|-------|----------|--------------|------|
| **Phase 1: Parallel Implementation** | 1-2 weeks | `cf_core/logging/` module with feature flag | Low |
| **Phase 2: Shim Layer** | 1 week | Backward-compatible re-exports from old paths | Low |
| **Phase 3: Deprecation Warnings** | 2 weeks | `DeprecationWarning` on old imports | Medium |
| **Phase 4: Consolidation** | 1-2 weeks | Remove deprecated modules, update all imports | High |

**Phase 1 Details:**
- Create `cf_core/logging/__init__.py` with public API
- Implement `cf_core/logging/core.py` (ContextVar, structlog backend)
- Implement `cf_core/logging/evidence.py` (RFC 8785, hash chain)
- Feature flag: `CFCORE_LOGGING_V3=1` to opt-in

**Phase 2 Details:**
- Add shims to `python/services/unified_logger.py`:
  ```python
  import warnings
  from cf_core.logging import get_logger, ulog  # Re-export
  warnings.warn("python.services.unified_logger is deprecated. Use cf_core.logging.", DeprecationWarning)
  ```
- Preserve 100% API compatibility

**Phase 3 Details:**
- Enable deprecation warnings in CI
- Track migration progress (target: 80% of imports migrated)

**Phase 4 Details:**
- Delete deprecated shims
- Update all remaining imports
- Close migration project

---

## Constraints & Principles

### Must Preserve (Backward Compatibility)

1. **Import Patterns:**
   ```python
   from python.services.unified_logger import logger, get_logger, ulog  # 47 locations
   from cf_core.logger_provider import RuntimeBuilder, Runtime  # MCP servers
   from src.unified_logging import ulog, logged_action  # CLI plugins
   ```

2. **Environment Variables:**
   ```bash
   UNIFIED_LOG_LEVEL=DEBUG|INFO|WARN|ERROR
   UNIFIED_LOG_PATH=logs/unified.log.jsonl
   UNIFIED_LOG_CONSOLE=true|false
   UNIFIED_LOG_CORRELATION=<override>
   UNIFIED_LOG_HASH_CHAIN=1
   UNIFIED_LOG_EVIDENCE_AUTO=1
   CF_SESSION_ID=<powershell-session>
   CF_TRACE_ID=<cross-language-trace>
   ```

3. **JSONL Format:**
   ```json
   {"timestamp": "2025-12-30T21:00:00Z", "level": "info", "event": "task_start", "correlation_id": "abc123", "task_id": "T-001"}
   ```

4. **PowerShell Bridge:**
   - `Start-CFSession` sets `$env:CF_SESSION_ID`
   - `Write-CFLogEvent` produces compatible JSONL
   - Both languages produce identical JSON structure

### Must Implement (New Requirements)

1. **Correlation ID per CF-133:**
   - ContextVar propagation in async contexts
   - RuntimeBuilder pattern for MCP servers
   - Immutable session binding (correlation_id protected)

2. **Evidence Bundles per UCL Law 3:**
   - RFC 8785 canonical serialization
   - SHA-256 hash on bundle close
   - QSE directory structure

3. **LOG-001 Compliance:**
   - Baseline event taxonomy enforcement
   - Gap detection (`logging_gap_detected`)
   - Coverage validation (≥90%)

---

## Validation Criteria

### PRD Acceptance

- [ ] All user stories have acceptance criteria
- [ ] API contract includes type signatures
- [ ] Migration matrix covers all known imports
- [ ] Success criteria are measurable

### ADR Acceptance

- [ ] Status, Context, Decision, Consequences complete
- [ ] Implementation code samples compile
- [ ] Alternatives considered (at least 2)
- [ ] Risks documented with mitigations

### Migration Plan Acceptance

- [ ] Each phase has clear deliverables
- [ ] Rollback procedure defined per phase
- [ ] Timeline realistic (velocity: 0.23 hrs/point)
- [ ] Risk matrix complete

---

## Research Questions (Follow-Up)

1. **Output Manager Status**: Is `python/output_manager.py` active or archived? Does it implement RFC 8785?
2. **OTEL Integration**: Current implementation is stub; production requirements?
3. **PowerShell Parity**: Verify `Write-CFLogEvent` produces identical JSON structure to Python
4. **Performance Baseline**: Current `ulog()` overhead per call?

---

## Execution Instructions

### Step 1: Draft PRD

Use the PRD template from `docs/templates/` or create following the sections above. Focus on:
- Developer experience (DX) for the API
- Zero-friction migration for existing code
- Evidence bundle automation

### Step 2: Draft ADRs

Use ADR template (`docs/adr/template.md`). Include:
- At least 2 alternatives considered
- Clear rationale for chosen approach
- Implementation code samples

### Step 3: Draft Migration Plan

Create phased rollout with:
- Feature flag for opt-in during Phase 1
- Backward-compatible shims in Phase 2
- CI enforcement of deprecation warnings in Phase 3
- Completion criteria for Phase 4

### Step 4: Validation

Before declaring complete:
- [ ] PRD reviewed by 1+ stakeholder
- [ ] ADRs linked to PRD requirements
- [ ] Migration plan validated against codebase grep
- [ ] Test plan drafted for each phase

---

## References

- **Codex:** `docs/Codex/ContextForge Work Codex.md`
- **COF 13D:** `docs/03-Context-Ontology-Framework.md`
- **Development Guidelines:** `docs/09-Development-Guidelines.md`
- **Existing Prompt:** `docs/prompts/universal-logger-implementation-prompt.md`
- **logger_provider.py:** `cf_core/logger_provider.py`
- **unified_logging package:** `src/unified_logging/`

---

## Appendix: Correlation ID Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CLI / Entry Point                                                           │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ with correlation_context(correlation_id="user-provided-or-auto"):      │ │
│ │     # All logs in this block inherit correlation_id                    │ │
│ │     main_logic()                                                       │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ ContextVar Propagation (Thread/Async Safe)                                  │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ _CORRELATION_VAR.get() returns "user-provided-or-auto"                 │ │
│ │                                                                        │ │
│ │ # Resolution: ContextVar > CF_SESSION_ID > UNIFIED_LOG_CORRELATION > UUID│ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Log Event Emission                                                          │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ {                                                                       │ │
│ │   "timestamp": "2025-12-30T21:00:00Z",                                 │ │
│ │   "level": "info",                                                     │ │
│ │   "event": "task_complete",                                            │ │
│ │   "correlation_id": "user-provided-or-auto",  ← Injected by processor │ │
│ │   "task_id": "T-001"                                                   │ │
│ │ }                                                                       │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ Evidence Bundle (on session close or trigger)                               │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ .QSE/v2/Evidence/{project_id}/{correlation_id}/evidence_bundle.jsonl   │ │
│ │                                                                        │ │
│ │ evidence_hash = sha256(canonical_json(all_events))                    │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**End of Prompt**
