## Unified Logger (v0.2.1)

Lightweight, zero-config (env driven) structured JSONL event emitter with optional structlog + OpenTelemetry dual path.

### Quick Start

```python
from src import unified_logger as ul

ul.ulog("startup", severity="INFO", component="demo")

with ul.logged_action("process_items", target="batch"):
    # your code
    pass

print("Correlation:", ul.get_correlation_id())
```

### Key Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| UNIFIED_LOG_PATH | JSONL log file path | logs/unified.log.jsonl |
| UNIFIED_LOG_LEVEL | Minimum severity (DEBUG/INFO/WARN/ERROR) | DEBUG |
| UNIFIED_LOG_ROTATE_MAX_MB | Size-based rotation threshold (MB) | 50 |
| UNIFIED_LOG_ROTATE_MAX_AGE_SEC | Age rotation threshold (seconds) | off |
| UNIFIED_LOG_ROTATE_BACKUPS | Retained rotated copies | 5 |
| UNIFIED_LOG_REDACT | Comma tokens to redact (*** replacement) | (none) |
| UNIFIED_LOG_DUAL_WRITE | 1=structlog+file, 0=file only | 1 |
| UNIFIED_LOG_EVIDENCE_AUTO | Auto evidence flag on warn/error/fail | 0 |
| UNIFIED_LOG_NO_AUTOSTART | Suppress session_start autolog events | 0 |
| UNIFIED_HOST_POLICY | Populates host_policy field | Unknown |
| UNIFIED_RUN_ID | Override auto-generated run identifier | random |

### Rotation Metrics

```python
metrics = ul.get_logger_metrics()
# {'rotations': 1, 'bytes_rotated': 12345, 'last_reason': 'size'}
```

### Event Fields (JSONL line)
`timestamp, correlation_id, run_id, script, action, target, result, duration_ms, severity, ok, evidence_path, details, pid, host_policy` (+ optional `trace_id`, `span_id`).

### Trace / Span IDs
If OpenTelemetry SDK + context active, `trace_id` / `span_id` are injected (structlog path and file parity).

### Context Manager
`logged_action` auto-emits success/fail with `duration_ms`.

### Redaction
Tokens in `UNIFIED_LOG_REDACT` are replaced globally with `***` in string values (deep traversal).

### Version 0.2.1 Highlights
* Lifecycle autostart events (`python_session_start`, `session_start`).
* Correlation accessor `get_correlation_id()`.
* Stable per-process `run_id` (override with `UNIFIED_RUN_ID`, accessor `get_run_id()`).
* `logged_action` duration + fail logging.
* Rotation metrics introspection stable.
* Trace/span parity for file output.

### Testing Guidance
See `tests/python/test_unified_logger.py` for examples (context manager, rotation, lifecycle).

### Future Considerations
Planned: configurable JSON schema version field, optional structured stdout mirror, OTEL span creation helper.
