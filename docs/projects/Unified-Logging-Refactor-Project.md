# Unified Logging Refactor Project (Structlog-Centric Redesign)

## 1. Executive Summary
Current logging is a hybrid: a custom `ulog` implementation augmented incrementally to optionally use structlog plus a separate tracker adapter and ad‑hoc dual‑write. This has produced branching logic, duplicated rotation/redaction code, and test friction. We will build a first‑class structlog-centric Unified Logging layer with a clean processor pipeline, then migrate all callers via a measured shim approach ensuring backward compatibility.

Goals:
- Single authoritative emission API with stable schema.
- Processor-driven enrichment (timestamp, correlation, host_policy, redaction, evidence flags, routing) – no branching inside emit.
- Deterministic dual routing (file + console) configurable once.
- Backward-compatible shim for existing `ulog()` & tracker adapter until all migrations are completed.
- Catalog and migrate all legacy logging usage patterns.

Success Criteria (Definition of Done):
1. New module `unified_logging/` provides `log()` & lightweight context helpers; 100% unit test coverage for processors; integration tests pass.
2. All internal Python components call new API directly (tracker adapter, duckdb builder, tests, orchestration scripts).
3. Legacy `ulog()` still available but emits a deprecation warning exactly once per process and internally calls the new API.
4. Redaction, rotation, correlation, evidence auto-tag features preserved or improved.
5. Documentation (README subsection + migration guide) and CHANGELOG entry added.
6. Removal plan for shim recorded with target date.

## 2. Scope
In-Scope:
- New logging core (processors, API, configuration, routing, rotation, redaction, correlation, evidence flagging).
- Migration of Python emit points (unified_logger, tracker adapter, duckdb builder, tests).
- Backward-compatible shims.
- Logging usage catalog & remediation plan (PowerShell not immediately refactored; will reuse JSON schema later).
- Test suite enhancements (unit + integration + regression for legacy path).

Out-of-Scope (Phase 1):
- Async/network streaming sink.
- Structured SQLite / metrics aggregation (future phases).
- PowerShell module rewrite (tracked separately).

## 3. Architecture Overview
### 3.1 Components
- `unified_logging/config.py`: Environment + programmatic config resolution (log level, paths, dual routing, redact tokens, max size MB, evidence auto conditions).
- `unified_logging/context.py`: Correlation/contextvars management (get_cid, push/pop contextual fields, optional task/sprint IDs later).
- `unified_logging/processors.py`: Individual processors (timestamp, host_policy injector, context merge, result→ok normalizer, redaction structural, routing, JSON renderer).
- `unified_logging/rotation.py`: File rotation (size + optional daily) encapsulated without side effects in core API.
- `unified_logging/api.py`: Public `log(action, *, target=None, result="success", severity="INFO", **details)` and `log_phase()`, `operation()` context manager (emits start/end/error with timing).
- `unified_logging/shim.py`: Legacy adapter exposing `ulog()` mapping args → new `log()`; emits one-time deprecation warning.

### 3.2 Processor Pipeline (Default Order)
1. Ensure event dict (base fields injected).
2. Add timestamp (ISO8601 ms UTC).
3. Merge contextvars (correlation_id, host_policy, script).
4. Normalize result → ok boolean.
5. Add evidence flags (if severity >= WARN or result != success AND evidence_auto enabled).
6. Structural redaction (token replacement in nested structures).
7. Routing (fan out to: file sink writer, console JSON).
8. Final JSON render (structlog JSONRenderer).

### 3.3 Configuration Priority
1. Explicit function param override (future extension).
2. Environment variables (UNIFIED_LOG_LEVEL, UNIFIED_LOG_PATH, UNIFIED_LOG_DUAL_WRITE, UNIFIED_LOG_REDACT, UNIFIED_LOG_MAX_MB, UNIFIED_LOG_EVIDENCE_AUTO).
3. Defaults baked into config module.

### 3.4 Rotation Strategy
- Size-based rotate at N MB (configurable) with retention count (e.g., 5).
- Single writer function acquires threading lock; no rotation logic elsewhere.

## 4. Migration Strategy
### 4.1 Catalog Legacy Usage

| Category | Pattern | Discovery Method | Action |
|----------|---------|------------------|--------|
| Core Python logger | `from src.unified_logger import ulog` | grep `ulog(` | Replace with `from unified_logging import log` |
| Tracker adapter | `logging_setup.Logger.log` | grep `logging_setup.Logger` | Replace internals to call new `log()`; remove fallback JSON write |
| DuckDB builder | `_ULOGGER.log(...)` | grep `_ULOGGER.log` | Instantiate no custom logger; call `log()` directly |
| Tests | `ulog(` / tracker fallback tests | grep/test files | Update fixtures to new API; keep one compatibility test |
| Direct file writes | manual JSON lines with schema fields | grep `"ok":` `"evidence_path"` | Replace with `log()` or file sink wrapper |

Automation Script: `scripts/catalog_logging_usage.py` will:
- Scan `.py` files for patterns above.
- Produce JSON report: file, line, pattern, migration_status (pending/updated/skipped rationale).
- Emit summary counts.

### 4.2 Incremental Steps
1. Create new package `unified_logging/` with processors & API (no shim yet).
2. Implement unit tests (processors + api) and integration test (log → file + console) under `tests/python/unified_logging/`.
3. Introduce shim: Repoint existing `src/unified_logger.py` to import from new API; mark deprecation.
4. Migrate tracker adapter to call new `log()` directly; remove fallback writer logic (just leverage routing processor).
5. Migrate duckdb builder: remove local `_ULOGGER` object; direct calls to `log()`.
6. Run catalog script; patch remaining occurrences automatically where safe (regex with verification) or manually for edge cases.
7. Remove dual-write hack from legacy file once all callers switched (now handled by routing processor).
8. Update docs & CHANGELOG; add migration guide table.
9. Add deprecation warning test ensuring single emission per process.
10. Schedule removal date for legacy shim (e.g., +30 days).

### 4.3 Rollback Plan
- If new API causes failures: set env `UNIFIED_LOG_SHIM_ONLY=1` (shim bypass config; revert to legacy file emission logic kept temporarily in a backup module `legacy_unified_logger.py`).
- Keep backup module for one sprint; remove after stability proven (no critical issues after 7 days of CI runs).

## 5. Risk & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Hidden edge-case reliance on legacy file rotation | Event loss / disk growth | Dedicated rotation unit tests + stress test (generate > threshold). |
| Performance regression due to processor overhead | Higher latency per emit | Micro-benchmark before & after; optional disabling of console sink in prod. |
| Schema drift during migration | Inconsistent analytics | Freeze schema dataclass + contract test comparing old/new event keys. |
| Incomplete usage migration | Mixed logging paths | Catalog script gating merge (fails CI if pending count >0 after migration phase). |
| Redaction misses nested tokens | PII leakage | Structural redaction test with nested structures and arrays. |

## 6. Testing Plan
Test Layers:
- Unit: Each processor (input→output invariants); redaction, rotation, evidence flag.
- Contract: Compare event dict keys with legacy baseline JSON sample.
- Integration: End-to-end log() call writes file + console JSON; verify dual sink.
- Concurrency: Parallel threads (e.g., 10) emit events; ensure no JSON corruption & rotation correctness.
- Performance: Benchmark N=10k emits; assert <= X% increase vs legacy (target <15%).
- Backward Compatibility: Call `ulog()` and assert deprecation warning + correct event output.

## 7. Implementation Timeline (Indicative)

| Day | Milestone |
|-----|-----------|
| 1 | Create package skeleton + config + timestamp/normalize processors |
| 2 | Add redaction & context processors + routing + rotation |
| 3 | API + operation context manager + unit tests (processors) |
| 4 | Integration & concurrency tests + performance benchmark harness |
| 5 | Shim in `src/unified_logger.py` + tracker adapter migration |
| 6 | DuckDB builder migration + catalog script + automated replacements |
| 7 | Documentation (README, migration guide) + CHANGELOG + deprecation warning test |
| 8 | CI stabilization, fix gaps, finalize removal schedule |

## 8. Configuration Matrix

| Variable | Purpose | Default | Notes |
|----------|---------|---------|-------|
| UNIFIED_LOG_LEVEL | Minimum severity | DEBUG | Evaluated per event |
| UNIFIED_LOG_PATH | Primary file path | logs/unified.log.jsonl | Created lazily |
| UNIFIED_LOG_DUAL_WRITE | File+console toggle | 1 | 0 = suppress file when console ok |
| UNIFIED_LOG_MAX_MB | Rotate threshold | 50 | Size-based rotation |
| UNIFIED_LOG_REDACT | Comma tokens | (empty) | Structural + string pass |
| UNIFIED_LOG_EVIDENCE_AUTO | Auto flag failing events | 0 | Adds evidence_auto field |
| UNIFIED_HOST_POLICY | Host policy tag | Unknown | Injected processor |

## 9. Migration Guide (Excerpt)
Legacy → New mapping:

```
ulog(action, target=..., result=..., severity=..., duration_ms=..., evidence_path=..., **details)
 -> log(action, target=..., result=..., severity=..., **details)
(duration_ms,evidence_path move into details automatically by helper if supplied)
```

Tracker adapter: Replace custom Logger.log with direct `log()` + optional wrapper for correlation.

## 10. Backward Compatibility & Deprecation
- `src/unified_logger.py` retains `ulog()`; imports new API; warns once (DeprecationWarning subclass UnifiedLoggerDeprecation).
- Removal target date recorded in docs (30 days post merge) with criteria (no shim callers in catalog for 3 consecutive CI runs).

## 11. Operational Metrics
- events_per_run distribution (existing metrics scripts can parse new schema unchanged).
- logging_gap_detected count expected to drop (simpler pipeline).
- Benchmark: median emit latency, rotation time, redaction overhead (reported in build artifacts JSON).

## 12. Open Questions / Decisions

| Topic | Decision Needed By | Notes |
|-------|--------------------|-------|
| Async sink (future) | After stabilization | Possibly structlog async wrapper |
| Structured SQLite index | Post-migration | Build on unified schema |
| PowerShell integration | Separate project | Mirror schema via Write-ULog cmdlet |

## 13. Acceptance Checklist
- [ ] New package merged with tests ≥90% coverage.
- [ ] Legacy paths still functional; deprecation warning emitted once.
- [ ] All catalogged callsites migrated (report shows 0 pending).
- [ ] Docs + CHANGELOG updated.
- [ ] Performance benchmark within target.
- [ ] Rotation & redaction tests green.
- [ ] Rollback switch documented & tested.

## 14. Follow-Up (Phase 2 Ideas)
- Async queue + batch writer.
- OpenTelemetry exporter processor.
- Metrics counter (events by severity) emitted every N events.
- Integrity hash chain per file (tamper detection).

---
Project file version: 1.0.0
