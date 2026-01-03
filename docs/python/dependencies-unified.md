## Unified Dependency Set (All Plugins Required)

Date: 2025-08-29

This document enumerates the consolidated, now-required dependency set merged from:
- Root orchestration helper (`pyproject.toml`)
- Analytics layer (`analytics/pyproject.toml`)
- Tracker CLI (`cli/python/cf_tracker/pyproject.toml`)
- Former optional / dev / perf extras (pytest stack, auditing, perf, telemetry)

All items below are placed under the root `[project].dependencies` (optional groups emptied) to ensure a single environment can execute any subsystem without ad‑hoc installs.

| Category | Package | Version Range | Source(s) | Notes |
|----------|---------|---------------|-----------|-------|
| Core CLI | click | >=8.1.7,<8.2.0 | root | Bound minor to avoid Click 8→9 surprises |
| Core CLI | typer | >=0.12.3,<0.13.0 | all | Unified upper bound for stability |
| Core CLI | rich | >=13.7,<14.0 | all | Align on latest 13.x used |
| Data Model | pydantic | >=2.7,<2.8 | analytics, tracker, root | Narrowed (root had looser) |
| Serialization | orjson | >=3.10,<4.0 | analytics, root | Raised lower bound & added upper |
| Config | PyYAML | >=6.0 | root | |
| Hashing | xxhash | >=3.4.1,<4.0.0 | root, tracker | Added upper bound |
| Date Utils | python-dateutil | >=2.9.0.post0 | root | |
| Typing | typing_extensions | >=4.12,<5.0 | dev extras | Needed for forward annotations |
| DataFrame | pandas | >=2.2,<2.3 | analytics | |
| Columnar | pyarrow | >=16.0,<17.0 | analytics | |
| Alt DF | polars | >=0.21,<0.22 | analytics(perf) | Promoted from perf optional |
| Progress | tqdm | >=4.66,<5.0 | analytics | |
| Schema | jsonschema | >=4.22,<5.0 | analytics | |
| Env | python-dotenv | >=1.0,<2.0 | analytics | |
| Telemetry | structlog | >=25.0.0,<26.0.0 | all | |
| Telemetry | opentelemetry-api | >=1.36.0,<1.37.0 | all | Version-locked family |
| Telemetry | opentelemetry-sdk | >=1.36.0,<1.37.0 | all | |
| Telemetry | opentelemetry-exporter-otlp | >=1.36.0,<1.37.0 | all | |
| Bridge | structlog-opentelemetry | >=0.5.0,<0.6.0 | all | |
| Observability | prometheus-client | >=0.21.0,<0.22.0 | root | |
| Observability | sentry-sdk | >=2.35.0,<3.0.0 | root | |
| Platform | duckdb | >=1.0.0,<2.0.0 | root, tracker | Added upper bound for major safety |
| Web | fastapi | >=0.111.0,<0.112.0 | root | |
| Web | uvicorn | >=0.30.0,<0.31.0 | root | |
| Packaging | packaging | >=24.0 | root | |
| Testing | pytest | >=8.2,<9.0 | dev | |
| Testing | pytest-cov | >=5.0,<6.0 | dev | |
| Testing | pytest-xdist | >=3.5.0,<4.0.0 | dev | Parallel execution |
| Testing | pytest-timeout | >=2.3.1,<3.0.0 | dev | Deterministic timeouts |
| Testing | pytest-randomly | >=3.15.0,<4.0.0 | dev | Order randomization |
| Testing | pytest-benchmark | >=4.0.0,<5.0.0 | dev | Micro-bench harness |
| Property Testing | hypothesis | >=6.100.0,<7.0.0 | dev | |
| Lint | ruff | >=0.5.0,<0.6.0 | dev | |
| Type Checking | mypy | >=1.10.0,<1.11.0 | dev | |
| Security | pip-audit | >=2.7.0,<3.0.0 | dev | |
| Hooks | pre-commit | >=3.7.0,<4.0.0 | dev | |

Rationale:
- Eliminates environment drift across subprojects.
- Enables single uv sync to provision full toolchain.
- Upper bounds added where absent to reduce surprise major upgrades.

Follow-up:
1. Generate a lock file (future) for reproducibility once versions validated in CI.
2. Introduce an automated drift checker to flag dependency version divergence proposals.
3. Periodically (monthly) review upper bounds for safe expansion.

Install (after uv present):

```bash
uv pip install -r requirements.unified.in
```

Or regenerate from `pyproject.toml` directly (uv resolves ranges) once lock strategy adopted.
