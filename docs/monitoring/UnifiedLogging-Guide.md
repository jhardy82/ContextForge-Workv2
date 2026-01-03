---
post_title: Unified Logging Guide (ulog + Loguru default)
author1: AI Agent
post_slug: unified-logging-guide
microsoft_alias: none
featured_image: none
categories: [engineering]
tags: [logging, python, loguru, structlog, governance]
ai_note: true
summary: How to use the unified ulog() API with Loguru default, governance rules, path policy, CI gap gate, and a micro-benchmark.
post_date: 2025-09-12
---

## Unified Logging Guide (ulog + Loguru default)

This guide explains how to use the unified logging helper `ulog()` with Loguru as the default backend,
keep structlog for legacy code, follow path and governance policies, and run our CI gap gate.
It also includes a small benchmark to compare `ulog()` with legacy structlog.

### Quick start

```python
from src.unified_logging.core import ulog

ulog("startup", component="demo", result="success", details={"msg": "hello"})
```

Common fields: `action`, `target`, `result`, `severity`, `ok`, `details`, `correlation_id`, `run_id`, `timestamp`, `pid`,
`script`, and optional `trace_id`/`span_id` when OpenTelemetry is active.

### Environment controls (UNIFIED*LOG*\*)

- UNIFIED_LOG_BACKEND: loguru | structlog | direct (default: loguru)
- UNIFIED_LOG_DUAL_WRITE: 1 to emit via both legacy structlog and unified file (default: 0)
- UNIFIED_LOG_PATH: JSONL file path (default: repo-local `logs/unified.log.jsonl`)
- UNIFIED_LOG_ROTATE_MAX_MB: rotate by size in MB (default: 50) — alias: UNIFIED_LOG_MAX_MB
- UNIFIED_LOG_ROTATE_BACKUPS: keep last N rotated files (default: 5) — alias: UNIFIED_LOG_RETENTION
- UNIFIED_LOG_ROTATE_MAX_AGE_SEC: prune logs older than N seconds (default: off) — alias: UNIFIED_LOG_MAX_AGE_HOURS
- UNIFIED_LOG_REDACT: comma-separated tokens to mask as `***`
- UNIFIED_LOG_HASH_CHAIN: 1 to include hash-chain fields (default: 0)
- UNIFIED_LOG_EVIDENCE_AUTO: 1 to mark evidence on error/fail (default: 0)
- UNIFIED_LOG_OTEL: 1 to enable OTEL bridge (no-op if SDK absent)

### Governance note on benchmarks

There is a single, intentional exception to the "use ulog() everywhere" rule:
the micro-benchmark at `python/tools/bench_ulog_vs_structlog.py` imports
`structlog` to compare overhead against `ulog()`. This file is explicitly
allowlisted in the governance gap report and should not be used as a pattern
for application code. All production and tooling code should prefer `ulog()`.

Notes:

- The file writer is handled by the unified logger directly; Loguru is used as the console mirror by default and is disabled
  during shutdown to avoid noisy stderr writes on Windows.
- For benchmarking or tests, you can set `UNIFIED_LOG_PATH` to `NUL` (Windows) to avoid disk I/O.

### Path policy

- Python: default to repo-local `logs/...` paths; do not use `C:\\Temp`.
- Exception: external-use PowerShell scripts may default to `C:\\Temp` but must allow configuration.

### Governance and migration

- New Python code should use `ulog()`; structlog is retained for legacy only.
- The AST-based governance scanner catalogs logging usage and the gap report flags any structlog usage outside legacy/shim areas.
- To generate the report locally:

```pwsh
& .\.venv\Scripts\python.exe python\tools\generate_loguru_gap_report.py
```

Artifacts: `build/artifacts/logging/loguru_gap_report.json`

### CI gap gate

A GitHub Actions workflow (`.github/workflows/loguru-gap-gate.yml`) runs the report on PRs and on `main`. It uploads the
artifact and fails the job if `offender_count > 0`.

### Targeted tests (examples)

- Redaction masks tokens in both JSONL and console mirror
- Hash-chain links across events and resets per action
- Rotation/retention pruning and shutdown mirror safety
- OTEL bridge no-op by default and attribute mapping when enabled

Run a specific test file:

```pwsh
& .\.venv\Scripts\python.exe -m pytest -vv --color=yes tests\python\test_otel_bridge.py
```

### Micro-benchmark (ulog vs structlog)

We include a simple script to compare the minimal `ulog()` path to a no-op structlog configuration. It avoids disk I/O by
writing to `NUL` and emits a JSON summary.

```pwsh
& .\.venv\Scripts\python.exe python\tools\bench_ulog_vs_structlog.py --iterations 20000
```

Outputs:

- Console summary
- JSON results at `build/artifacts/benchmarks/ulog_vs_structlog.json`

Note on quiet output:

- The benchmark explicitly sets `UNIFIED_LOG_BACKEND=direct` to avoid Loguru console mirroring in tight loops.
  This keeps runs quiet and prevents excessive console output and token/log noise.
  You can override this by exporting `UNIFIED_LOG_BACKEND` before running,
  but it’s not recommended when measuring minimal overhead.

#### Run the benchmark in CI (manual)

You can run the same benchmark in GitHub Actions via a manual workflow:

- Navigate to Actions → "Manual - Unified Logging Benchmark" → Run workflow
- Optionally set `iterations` (default 20000)
- After completion, download the artifact named `ulog-benchmark-<iterations>`
- Open `ulog_vs_structlog.json` inside the artifact to see timings

This is useful for ad-hoc comparisons across environments without running locally.

#### Scheduled CI benchmark (weekly)

A scheduled workflow runs weekly to collect trends automatically:

- File: `.github/workflows/Unified Logging Benchmark (Scheduled)` → `.github/workflows/ulog-benchmark-schedule.yml`
- Schedule: Mondays at 05:17 UTC
- Behavior: sets `UNIFIED_RUN_ID` from the GitHub run ID, installs minimal deps (`structlog`, `loguru`), runs the benchmark with 20,000 iterations, and uploads the artifact.
- Artifact name: `ulog-benchmark-<run_id>` containing `ulog_vs_structlog.json`.

You can also trigger it manually from Actions if you need an on-demand scheduled-style run.

#### Benchmark JSON schema and metadata

Every benchmark run emits a JSON file with timing and environment details:

```json
{
  "iterations": <int>,
  "ulog_seconds": <float>,
  "structlog_seconds": <float>,
  "ulog_faster": <float|null>,   // structlog_seconds - ulog_seconds
  "meta": {
    "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
    "python_version": "3.x.y",
    "platform": "<platform string>",
    "os": "posix|nt",
    "machine": "<arch>",
    "processor": "<cpu>",
    "ci": true|false,
    "runner_os": "Windows|Linux|macOS|<null>",
    "runner_arch": "X64|ARM64|<null>"
  }
}
```

Use these metadata fields to compare results across machines and CI runners. The file is saved at `build/artifacts/benchmarks/ulog_vs_structlog.json` and uploaded as a workflow artifact in CI.

### Troubleshooting

- If you see shutdown noise on Windows, ensure you’re using the unified logger version that disables the console mirror during
  `atexit`.
- If the gap gate fails in CI, open the artifact and replace flagged `structlog.get_logger` usages with `ulog()`.

### Rotated filename format and Windows safety

Rotated files now include millisecond precision in the timestamp to prevent per-second
filename collisions on Windows during rapid rotations. Example:

- Original: build/logs/app.log.jsonl
- Rotated: build/logs/app.log.jsonl.20250131_142315.327

If an extremely rare collision still occurs within the same millisecond, the system
automatically retries with a numeric suffix and finally a unique suffix, guaranteeing a
collision-free rename. This change eliminates transient `[WinError 183]` errors observed
under very small rotation thresholds.
