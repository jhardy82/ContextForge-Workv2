# UnifiedLogger Migration Guide (Python)

Effective date: 2025-09-12

## Policy

- New Python code MUST use `ulog()` from `src/unified_logging/core.py`.
- Default backend = `loguru` (configured via `UNIFIED_LOG_BACKEND`, default `loguru`).
- `structlog` is supported only for legacy/shim paths; migrate on next touch.

## Quickstart

```python
from src.unified_logging.core import ulog

ulog("session_start", target="my/cli", details={"dry_run": True})
ulog("artifact_emit", target="build/artifacts/report.json", details={"size": 1024})
ulog("session_summary", details={"events": 42})
```

## Migrate existing structlog usage

1. Replace imports:
   - Before: `import structlog` or `from python.logging.unified import get_logger`
   - After: `from src.unified_logging.core import ulog`

2. Map common calls:
   - Before: `logger = structlog.get_logger(__name__)`; `logger.info("action", key=value)`
   - After: `ulog("action", target="<entity>", details={"key": value})`

3. Environment (optional):
   - `UNIFIED_LOG_LEVEL` (DEBUG|INFO|WARN|ERROR)
   - `UNIFIED_LOG_PATH` (base directory; hierarchical run dirs by default)
   - `UNIFIED_LOG_REDACT` (comma-separated tokens)
   - `UNIFIED_LOG_BACKEND=loguru|structlog|direct` (default `loguru`)

4. Console mirroring
   - `ulog()` mirrors to console via loguru; file writing remains centralized and backend-agnostic.
   - Shutdown guards prevent stderr-closed errors.

## Governance

- The scanner (`python/tools/catalog_logging_impls.py`) flags `STRUCTLOG_IN_NEW_CODE` when structlog is
  used outside whitelisted legacy paths. Suggested fix: import `ulog` and emit events via the unified helper.

## Notes

- Rotation/retention and redaction are handled centrally; behavior is consistent across backends.
- Legacy shim (`python/_logging_legacy/unified.py`) remains temporarily for compatibility and emits a
  DeprecationWarning when imported.
