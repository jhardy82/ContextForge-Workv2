<!-- markdownlint-disable-file -->
## Monitoring Configuration & Baseline Plan

This document supports parallel development by the primary monitoring implementation agent by supplying:

1. Current environment/config flag inventory
2. Proposed reserved names (do **not** implement until agreed)
3. Baseline performance measurement procedure (pre full instrumentation)
4. Backward compatibility expectations

### 1. Existing Flags Observed in Code

| Flag | Purpose | Source Location | Notes |
|------|---------|-----------------|-------|
| `UNIFIED_LOG_BACKEND` | Select logging backend (direct/structured) | `cf_cli._root_callback` | Defaults to `direct` if unset |
| `UNIFIED_LOG_RICH` | Enable rich mirror | `cf_cli._root_callback` | String "0/1" |
| `UNIFIED_LOG_RICH_MIRROR` | Mirror activation gate | `cf_cli._root_callback` | |
| `UNIFIED_LOG_RICH_STDERR` | Mirror stream selection | `cf_cli._root_callback` | |
| `UNIFIED_LOG_RICH_JSON` | Pretty JSON mode | `cf_cli._root_callback` | |
| `CF_CLI_LAZY_MODE` | Lazy settings bootstrap | Top‑level | Skips heavy config import |
| `CF_CLI_SUPPRESS_SESSION_EVENTS` | Suppress lifecycle events | `_emit_struct_or_fallback` | Important for JSON purity |
| `CF_CLI_QUIET_MODE` | Alternate quiet gate | `_emit_struct_or_fallback` | Harmonizes with `--quiet` |
| `CF_CLI_TRACING_DISABLED` | Hard disable tracing | `_root_callback` & manager | Prevents OTEL init |
| `CF_CLI_FORCE_FALLBACK` | Force JSONL logging path | Logger init | Avoid structlog |

### 2. Proposed Reserved Monitoring Flags (Not Yet Implemented)

| Proposed | Intended Use | Rationale |
|----------|--------------|-----------|
| `CF_MONITORING_CONFIG_PATH` | Override default `monitoring.yaml` path | Deterministic config injection |
| `CF_MONITORING_FEATURES` | Comma list: `metrics,tracing,logging` | Single switch for bulk enable |
| `CF_MONITORING_FORCE_DISABLE` | Hard kill all monitoring init | Support emergency rollback |
| `CF_MONITORING_METRICS_PORT` | Explicit port override | Keeps `--metrics-port` CLI but enables headless run |
| `CF_MONITORING_NAMESPACE` | Metrics namespace prefix | Consistency across exporters |

Do **not** implement until naming ratified to avoid conflict with parallel agent decisions.

### 3. Baseline Performance Measurement Procedure

Goal: Establish import + empty invocation cost prior to full instrumentation; target < **5ms added overhead** later (absolute import time may be higher; we track delta).

Steps:
1. Ensure environment disables monitoring:
   - `set CF_CLI_TRACING_DISABLED=1`
   - Avoid `--metrics-port` flag
2. Measure import time (Python one‑liner or provided test harness).
3. Measure Typer root invocation with no command.
4. Record results to `artifacts/monitoring_baseline.json` (created by test if not present).
5. After instrumentation, repeat with metrics/tracing enabled to compute delta.

### 4. Backward Compatibility Expectations

| Scenario | Expected Behavior |
|----------|-------------------|
| Prometheus client missing | CLI still imports; specifying `--metrics-port` logs or silently ignores metrics without non‑zero exit |
| OpenTelemetry missing | CLI still imports; `--enable-tracing` ignored / soft failure |
| Both libs missing simultaneously | Still zero exit code for help or simple commands |
| Quiet mode with monitoring enabled | No additional stdout noise beyond explicit command output |
| JSON-producing commands (`--json`) | No spurious lifecycle events preceding output when suppressed flag set |

### 5. Test Artifacts Added

Backward compatibility tests under `tests/python/test_cli_backward_compat.py` verify import/run with simulated missing libs and write import timing baseline artifact.

### 6. Next Additions (Left for Primary Agent)

- Formal metrics naming spec (prefix, label cardinality policy)
- Trace attribute schema (e.g., `cf.cli.command`, `cf.session.id`)
- Logging bridge enrichment rules
- Multiprocess strategy decision (e.g., Prometheus multiprocess mode or single aggregator process)

---
Document intentionally minimal and non-authoritative—serves as a coordination aid. Update sections only after cross-agent agreement.
