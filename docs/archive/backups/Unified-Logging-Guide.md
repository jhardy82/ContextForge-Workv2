<!-- markdownlint-disable-file -->

## Unified Logging Guide

### Quickstart

- Set `UNIFIED_LOG_PATH` and optional rotation envs.
- Minimal example: use `ulog()` to emit a structured event.

### API Basics

- `ulog(action, target=None, result=None, ok=None, severity=None, details=None, evidence_path=None)`
- `logged_action` context manager for duration and automatic end emission.

### Redaction

- `UNIFIED_LOG_REDACT` (literal tokens)
- `UNIFIED_LOG_REDACT_REGEX` (pattern list)

### Lifecycle Baseline

- Autostart behavior and `UNIFIED_LOG_NO_AUTOSTART`.
- Required lifecycle events: session_start, session_end, python_session_end, session_summary.

### Rotation & Retention

- Size/age/backups: `UNIFIED_LOG_ROTATE_MAX_MB`, `UNIFIED_LOG_ROTATE_MAX_AGE_SEC`, `UNIFIED_LOG_ROTATE_BACKUPS`.
- Rotated filename pattern and `log_rotation` event fields.
- Note: `UNIFIED_LOG_MAX_MB` is an alias; prefer `UNIFIED_LOG_ROTATE_MAX_MB`.

### Governance note on benchmarks

There is a single, intentional exception to the "use ulog() everywhere" rule:
the micro-benchmark at `python/tools/bench_ulog_vs_structlog.py` imports
`structlog` to compare overhead against `ulog()`. This file is explicitly
allowlisted in the governance gap report and should not be used as a pattern
for application code. All production and tooling code should prefer `ulog()`.

### OTEL (Optional)

- `UNIFIED_LOG_OTEL` for best-effort span linking, trace/span id injection.

### Console Mirroring (Optional)

- Guard patterns to avoid duplicated console; default off for JSONL-focused scripts.

### Rich Console Mirroring (Opt-in)

Rich-powered console mirroring is available as an optional, opt-in developer UX on top of the durable JSONL logs. It is disabled by default to preserve pure stdout for JSON-mode CLIs and tests.

- Enable via environment:
  - `UNIFIED_LOG_RICH=1`
  - `UNIFIED_LOG_RICH_MIRROR=1`
  - `UNIFIED_LOG_RICH_STDERR=1` to render to stderr (recommended when stdout must stay machine-readable)
  - `UNIFIED_LOG_RICH_JSON=1` to pretty-print the `details` payload after the compact header line
  - Optional: `UNIFIED_LOG_RICH_WIDTH=<columns>` to constrain console width

- Enable via CLI flags (when supported, e.g., `dbcli` root options):
  - `--rich-log` to enable the mirror
  - `--rich-json/--no-rich-json` to toggle pretty-printing of `details`
  - `--rich-stderr` to send mirror output to stderr (default on)

Behavior

- By default (no flags/envs), no console mirror is added; only JSONL files are written.
- When enabled, a concise header line is printed per event (e.g., `[INFO] action target=result`). If `UNIFIED_LOG_RICH_JSON=1` (or `--rich-json`), the event `details` object is pretty-printed below via Rich’s JSON renderer.
- Rich is an optional dependency. If it is not installed, the system degrades gracefully by omitting the mirror.

Cautions

- Keep stdout pure when emitting JSON for machine consumption. Prefer mirroring to stderr (`UNIFIED_LOG_RICH_STDERR=1` or `--rich-stderr`) in JSON contexts.
- Do not enable mirroring in CI workflows that parse stdout unless explicitly required.

#### Quick Reference

Env Vars

- `UNIFIED_LOG_RICH=1` — enable Rich support
- `UNIFIED_LOG_RICH_MIRROR=1` — enable console mirroring
- `UNIFIED_LOG_RICH_STDERR=1|0` — route to stderr (1, default) or stdout (0)
- `UNIFIED_LOG_RICH_JSON=1|0` — pretty-print `details` JSON (1 default)
- `UNIFIED_LOG_RICH_WIDTH=<cols>` — optional console width

CLI Flags (when supported, e.g., `dbcli`)

- `--rich-log` — enable mirroring
- `--rich-json` / `--no-rich-json` — toggle pretty-printing of `details`
- `--rich-stderr` — route to stderr (default on)

### Troubleshooting

- Windows path quoting, rename permissions, finals idempotency, multiprocessing tips.

### Migration (structlog ➜ ulog)

### Rotated filename format and Windows safety

Rotated files now include millisecond precision in the timestamp to prevent per-second filename collisions on Windows during rapid rotations. Example:

- Original: build/logs/app.log.jsonl
- Rotated: build/logs/app.log.jsonl.20250131_142315.327

If an extremely rare collision still occurs within the same millisecond, the system automatically retries with a numeric suffix and finally a unique suffix, guaranteeing a collision-free rename. This change eliminates transient `[WinError 183]` errors observed under very small rotation thresholds.

- Replace new structlog usage with `ulog()`; keep legacy modules under allowlist.

### Appendix: Handoff Checklist

- Env names align with `src/unified_logger.py`.
- Lifecycle tests validated (including finals idempotency).
- Governance scan green; rotation smoke plan ready.
- PR narrative added with env flags and risks.
