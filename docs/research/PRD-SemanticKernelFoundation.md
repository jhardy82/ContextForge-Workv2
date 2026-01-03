# Product Requirements Document (PRD)
**Component:** `CFSemanticKernelFoundation` (Semantic Kernel Foundation Layer)
**Repository:** PowerShell Projects (Python orchestration layer)
**Document Version:** 1.0.0
**Date:** 2025-09-23
**Author:** Generated collaboratively (assistant + existing repo context)
**Status:** Draft → (Approve -> Implement -> Validate)

---
## 1. Executive Summary
The `CFSemanticKernelFoundation` component provides a unified, observable abstraction around Azure/OpenAI powered Semantic Kernel (SK) capabilities (chat completion, embeddings, conversation summary, optional memory) with:
- Deterministic, low‑overhead "fast path" when advanced plugins are disabled (< **50 ms** init target).
- Rich per‑plugin initialization diagnostics (attempted/active/error + elapsed timings).
- Structured plugin error taxonomy (enumerated codes + severity preserving legacy simple `error` string for backward compatibility).
- Performance metrics including latency distribution percentiles (p50/p90/p99).
- Configurable health check surface (optionally includes plugin initialization snapshot).
- Strict vs non‑strict initialization behavior for hard fail governance contexts.

The module underpins higher level orchestration, quality gates, and governance instrumentation, enabling subsequent scenario + automated testing via TestSprite and PyTest harnesses.

---
## 2. Problem Statement
Prior to enhancements, plugin initialization & performance characteristics were opaque:
- No granular insight into which advanced plugins attempted, succeeded, or failed.
- Failures collapsed into unstructured string messages with limited machine actionability.
- No latency percentile insight—only raw response times, obstructing SLO tracking.
- Health endpoint could become heavy if it always returned verbose plugin state.
- Error handling used broad `except` blocks reducing diagnosability and testability.

**Impact:** Slower mean time to detect (MTTD) plugin regressions, difficulty constructing targeted tests, inability to assert operational SLO adherence programmatically.

---
## 3. Goals & Success Metrics
| Goal | Metric / KPI | Target | Measurement Source |
|------|--------------|--------|--------------------|
| Fast path overhead minimal | Init time without advanced plugins | < 50 ms (p90) | Synthetic timer in unit test |
| Observability completeness | Required logging events emitted per run | 100% baseline (LOG-001..009) | Log coverage test |
| Plugin diagnostics fidelity | Accurate attempted/active/error for each enabled plugin | 100% correctness across matrix | Scenario tests (TestSprite) |
| Percentile accuracy | p50/p90/p99 within ±1 sample rank of nearest-rank definition | 100% deterministic arrays | Unit tests |
| Strict mode fail-fast | Raises `PluginInitializationError` on any plugin failure when strict | 100% of failure cases | Unit tests |
| Backward compatibility | Legacy `error` field remains truthy & unchanged semantics | No regressions | Regression tests |

---
## 4. Scope
### In Scope
- Initialization orchestration of memory & summary plugins.
- Structured plugin metrics & error taxonomy.
- Performance metric aggregation (avg, min, max, p50/p90/p99).
- Health check selective inclusion of plugin metrics.
- Strict vs soft plugin initialization semantics.
- Percentile calculation (nearest-rank).
- Test harness coverage (unit + integration + scenario).

### Out of Scope (Phase 1)
- Dynamic plugin discovery/loading beyond memory & summary.
- External persistence of metrics (DB / telemetry export).
- Adaptive retry policies for initialization.
- Full structured tracing / distributed spans.

---
## 5. Stakeholders
| Role | Interest |
|------|----------|
| Platform Engineer | Reliability, diagnostics clarity |
| QA / Test Automation | Deterministic metrics & taxonomy for assertions |
| Observability / SRE | Percentiles & health gating |
| Security / Governance | Strict mode enforcement for compliance contexts |
| Product / Ops | Stable integration behavior |

---
## 6. User Stories
1. **As a QA engineer** I can force plugin initialization to fail hard (strict mode) so misconfiguration is surfaced early in CI.
2. **As a reliability engineer** I can view per-plugin elapsed time & failure reasons to triage slowdowns.
3. **As a governance system** I can parse structured error codes to classify and escalate only severe deviations.
4. **As a developer** I can exclude plugin metrics from a lightweight health probe to keep performance fast.
5. **As a tester** I can feed deterministic latency arrays and assert percentile computation correctness.

---
## 7. Functional Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | Provide `plugin_init_metrics` with per-plugin: attempted, active (bool), error (string code or ""), error_obj (structured), elapsed_ms (float). | High |
| FR-002 | Aggregate totals: attempted_count, active_count, failure_count, total_elapsed_ms. | High |
| FR-003 | Expose strict mode: raise on first plugin failure when `strict_plugin_init=True`. | High |
| FR-004 | Provide structured error object: code, severity, message, optional exception_type, exception_message, detail. | High |
| FR-005 | Maintain backward compatibility: `error` retains code string or empty. | High |
| FR-006 | Compute response time metrics: count, min, max, avg, p50, p90, p99. | High |
| FR-007 | Health check API includes plugin metrics only when `include_plugin_metrics=True`. | High |
| FR-008 | Support enumerated error codes (see taxonomy). | High |
| FR-009 | Distinguish dependency `ImportError` vs generic exceptions with different codes. | Medium |
| FR-010 | Ensure percentile logic gracefully returns None for insufficient data. | Medium |
| FR-011 | Provide correlation_id surface for logs/events (already available). | Medium |
| FR-012 | Expose method(s) stable for unit test invocation without side effects. | High |
| FR-013 | Initialization logic does not exceed 50 ms (median) when both advanced plugins disabled. | High |
| FR-014 | Fast path avoids loading unused plugin modules. | High |
| FR-015 | Logging at initialization emits success/failure per plugin (leveraging existing logger). | Medium |

---
## 8. Non-Functional Requirements
| Category | Requirement |
|----------|------------|
| Performance | Fast path <50 ms p90 (no advanced plugins). |
| Reliability | No unhandled exceptions escape non-strict initialization path. |
| Maintainability | Error codes enumerated; additive extensibility only. |
| Testability | Deterministic functions for metric and percentile computation. |
| Observability | Structured logs (JSON) with correlation_id & plugin outcomes. |
| Security | No secrets written in error_obj detail fields (sanitized). |
| Backward Compatibility | Legacy fields preserved; no schema shrinkage. |

---
## 9. Configuration Surface
| Field | Type | Default | Behavior |
|-------|------|---------|----------|
| enable_memory_plugin | bool | False | Controls TextMemoryPlugin init. |
| enable_summary_plugin | bool | False | Controls ConversationSummaryPlugin init. |
| strict_plugin_init | bool | False | Hard fail on any plugin error when True. |
| log_performance_metrics | bool | True | Emits performance summary logs. |
| include_plugin_metrics (health param) | bool | False | Gated inclusion of plugin metrics. |

---
## 10. Initialization Flow (Simplified)
1. Instantiate foundation with config → set correlation_id.
2. If advanced plugins enabled → call `_initialize_advanced_plugins()`.
3. For each plugin: mark attempted, time start, try init, set active or error, record elapsed.
4. Aggregate totals.
5. Strict mode: raise `PluginInitializationError` on failure branch.
6. Ready for `create_ai_response` invocations (records response times).

---
## 11. Error Taxonomy (Current)
| Code | Severity (Default) | Meaning | Trigger Conditions | Retry Guidance |
|------|--------------------|---------|--------------------|----------------|
| missing_configuration | warning | Required config absent (endpoint/key/deployment). | Missing env / config fields. | Populate config & retry. |
| initialization_exception | error | Generic runtime failure during plugin setup. | Any non-import exception. | Investigate stack & fix. |
| dependency_unavailable | error | Required module not importable. | `ImportError` raised. | Install dependency. |
| timeout | error | (Reserved) Operation exceeded allowed time. | Future extension. | Increase timeout / optimize. |
| unexpected_exception | error | (Reserved) Catch-all internal unexpected state. | Future extension for sentinel paths. | File issue / escalate. |

**Backward Compatibility:** Legacy `error` field holds the `code` string; consumers previously checking `if metrics[plugin]['error']:` continue to work.

---
## 12. Data Structures
### 12.1 Plugin Metrics Schema
```jsonc
{
  "memory": {
    "attempted": true,
    "active": false,
    "error": "missing_configuration",
    "error_obj": {
      "code": "missing_configuration",
      "severity": "warning",
      "message": "Embedding configuration incomplete (endpoint/key/deployment)",
      "detail": { "have_endpoint": false, "have_key": true, "deployment": null }
    },
    "elapsed_ms": 0.0
  },
  "summary": { /* same shape */ },
  "totals": {
    "attempted_count": 1,
    "active_count": 0,
    "failure_count": 1,
    "total_elapsed_ms": 12.67
  }
}
```

### 12.2 Performance Metrics Schema
```jsonc
{
  "count": 5,
  "min_ms": 123.4,
  "max_ms": 412.9,
  "avg_ms": 240.12,
  "p50_ms": 230.1,
  "p90_ms": 400.9,
  "p99_ms": 412.9,
  "plugin_snapshot": { /* plugin_init_metrics copy */ }
}
```

---
## 13. Public Methods (Testable)
| Method | Purpose | Side Effects | Deterministic |
|--------|---------|--------------|--------------|
| `initialize_foundation()` | Orchestrates start-up; may call advanced plugin init. | Mutates metrics. | Deterministic with fixed config & environment. |
| `_initialize_advanced_plugins()` | Internal advanced plugin setup. | Metrics + possible raised error (strict). | Deterministic barring external dependencies. |
| `create_ai_response(prompt:str, ...)` | Generates chat completion; records latency. | Network call + metrics. | Non-deterministic; latency captured. |
| `get_performance_metrics()` | Computes aggregate stats and percentiles. | None (read-only). | Deterministic given underlying list. |
| `health_check(include_plugin_metrics=False)` | Returns readiness (and optional plugin metrics). | None. | Deterministic if metrics stable. |

---
## 14. Percentile Algorithm
Nearest-rank definition: For sorted list `L` length `n`, percentile `p` (e.g. 0.9) index = `ceil(p * n) - 1` (bounded to `[0, n-1]`). Edge Cases: n==0 → None for all; n==1 → that value for all defined percentiles.

---
## 15. Strict Mode Semantics
| Condition | strict_plugin_init=False | strict_plugin_init=True |
|-----------|--------------------------|-------------------------|
| Plugin failure | Record error; continue. | Raise `PluginInitializationError` immediately. |
| Partial success | Allowed; health may still show degraded. | Aborted initialization; caller decides handling. |

---
## 16. Logging & Observability
Baseline events required (LOG-001..009). Each plugin initialization attempt logs either success (`INFO`) or failure (`ERROR` or `WARNING` if missing config). Structured fields: `plugin`, `elapsed_ms`, `error_code` (when present), `correlation_id`.

---
## 17. Performance Requirements
| Metric | Target | Test Strategy |
|--------|--------|---------------|
| Fast path init time | <50 ms p90 | Synthetic test bypassing plugin flags; time monotonic spans. |
| Overhead with 2 plugins | <250 ms p90 (non-network) | Mock embedding & summary to isolate framework overhead. |
| Percentile computation cost | O(n log n) via sort; acceptable for n < 10k. | Micro-benchmark optional. |

---
## 18. Backward Compatibility
- Retain existing field names: `plugin_init_metrics[plugin]['error']` remains.
- Additive: new `error_obj`, enums internal only.
- No existing method signatures removed.

---
## 19. Migration Strategy
1. Land central error helper + enums (DONE).
2. Add tests (unit + scenario) referencing enumerations.
3. Document schemas (this PRD + README excerpt).
4. Introduce future additional plugins behind flags (non-breaking).

---
## 20. Test Strategy (For PyTest + TestSprite)
### 20.1 Unit Tests
| Area | Test Cases |
|------|------------|
| Percentiles | Empty list → None values; 1 element list → same value; Known vector `[10,20,30,40,50]` → p50=30 p90=50 p99=50. |
| Error Helper | Build error with/without exception/detail; severity default; enum string persistence. |
| Strict Mode | Force ImportError via monkeypatch; assert raises `PluginInitializationError` when strict. |
| Missing Config | Omit embedding endpoint/key/deployment; ensure `missing_configuration` + severity warning. |
| Dependency Unavailable | Simulate ImportError for summary plugin. |
| Initialization Exception | Raise generic Exception; code `initialization_exception`. |

### 20.2 Integration Tests
| Scenario | Validation |
|----------|-----------|
| Both plugins enabled, all configs valid | active_count=2 failure_count=0. |
| Memory disabled, summary enabled | attempted_count=1; memory absent. |
| Health check w/o plugin metrics | No `plugin_init_metrics` key in response. |
| Health check with plugin metrics | Contains plugin metrics + totals inlined. |

### 20.3 Negative / Resilience
| Scenario | Expected |
|----------|----------|
| Strict mode + missing config | Immediate raise. |
| Non-strict + exception | Metrics record error, init continues. |

### 20.4 TestSprite Mapping
TestSprite test plan will:
- Load code summary; identify class & methods.
- Generate targeted tests for: percentile helper path, strict vs soft flows, plugin metrics schema invariants, health check gating.
- Use mocks/stubs to avoid actual network calls.

### 20.5 Coverage Targets
| Layer | Target |
|-------|--------|
| Logic branches in `_initialize_advanced_plugins` | >=95% |
| Error taxonomy code paths | 100% active codes |
| Percentile edge cases | 100% enumerated |

---
## 21. Requirement → Test Traceability Matrix
| Requirement | Test IDs (Planned) |
|-------------|--------------------|
| FR-001 | UT_plugin_metrics_shape, IT_full_enable |
| FR-002 | UT_totals_math, IT_partial_enable |
| FR-003 | UT_strict_mode_raise, NG_strict_missing_conf |
| FR-004 | UT_error_helper_fields |
| FR-005 | UT_legacy_error_truthiness |
| FR-006 | UT_percentiles_vector, UT_percentiles_single, UT_percentiles_empty |
| FR-007 | IT_health_without_metrics, IT_health_with_metrics |
| FR-008 | UT_error_codes_constants |
| FR-009 | UT_importerror_dependency_code |
| FR-010 | UT_percentiles_empty |
| FR-013 | PERF_fast_path_timings |
| FR-014 | UT_fast_path_no_plugin_calls |

---
## 22. Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Over-logging slows fast path | Performance regression | Keep plugin logs conditional on enable flags; measure. |
| Enum code changes break tests | CI instability | Add docs: additive-only; freeze names. |
| Percentile miscalc under rare rounding | Incorrect p90 alerting | Comprehensive deterministic tests. |
| Strict mode misused in prod | Startup outages | Document intended CI/validation use. |

---
## 23. Rollout Plan
| Phase | Deliverable | Exit Criteria |
|-------|-------------|---------------|
| 1 | Core instrumentation & enums | Code merged; fast path perf validated. |
| 2 | Unit & integration tests | Coverage & passing CI. |
| 3 | TestSprite scenario harness | Automated scenario validation green. |
| 4 | Documentation & README excerpt | PRD + usage docs published. |
| 5 | Optional perf profiling | Baseline metrics captured. |

---
## 24. Acceptance Criteria Checklist
- [ ] All FR-001..FR-015 implemented or justified.
- [ ] Unit tests passing (≥ coverage targets).
- [ ] Scenario tests validate strict vs soft behavior.
- [ ] Health check gating proven.
- [ ] Fast path timing under threshold (synthetic test).
- [ ] Documentation (PRD + user guide section) committed.
- [ ] No breaking API changes (backward compatibility validated).

---
## 25. Open Questions
| ID | Question | Owner | Resolution Needed By |
|----|----------|-------|----------------------|
| Q1 | Should timeout code be activated with a config-based soft timeout? | TBD | Before adding new plugin types |
| Q2 | Export metrics to a central aggregator? | Observability Team | After phase 3 |
| Q3 | Add structured success object mirroring error_obj for symmetry? | Platform | Optional post-MVP |

---
## 26. Appendix: Sample Health Check Payload (With Metrics)
```jsonc
{
  "status": "ok",
  "correlation_id": "<guid>",
  "performance": { "avg_ms": 234.1, "p90_ms": 400.2 },
  "plugin_init_metrics": { /* see schema */ }
}
```

---
## 27. Appendix: TestSprite Guidance
When invoking TestSprite:
1. Generate code summary to identify functions.
2. Focus backend test plan on `_initialize_advanced_plugins`, percentile calculation, strict mode raising path.
3. Use fixture/mocking layer to intercept network calls by patching SK client objects.
4. Validate structured error object shape with JSON schema assertion.
5. Inject synthetic latency samples before calling `get_performance_metrics()`.

---
**End of Document**
