# ContextForge Python Library Research (2025-08-26)

Status: In Progress
Conversation Tracker: `trackers/conversation/CF-LibResearch-20250826.json`
Task Id: `T-LIB-AUDIT-20250826-001`

## Methodology
Workspace-first audit of dependency declarations in `pyproject.toml` (root and `analytics/`), plus `requirements.txt`. Verified installed versions via runtime environment query (pip metadata). No fabrication. Each section lists: Version (installed), Declared Source (where specified / method), Purpose / Fit, Evidence.

## Core Orchestration & CLI Dependencies

### duckdb
- Version: 1.3.2 (installed), declared >=0.10.0 (root `pyproject.toml`)
- Install Source: root `pyproject.toml` `[project.dependencies]`
- Purpose: Embedded analytical SQL engine backing lightweight projections / ad‑hoc analytics without external DB; enables fast columnar queries over tracker CSVs / logs.
- Evidence: `pyproject.toml` line containing `"duckdb>=0.10.0"`; installed version probe.

### PyYAML
- Version: 6.0.2 (installed), declared >=6.0
- Install Source: root `pyproject.toml`
- Purpose: Parse legacy YAML task definitions and instruction files during migration to CSV.
- Evidence: `pyproject.toml`, YAML ingestion scripts importing `yaml`.

### typer
- Version: 0.16.1 (installed), declared >=0.12.0 (root) and analytics pinned <0.13
- Install Source: both `pyproject.toml` files
- Purpose: Rapid CLI surfaces for trackers / analytics (e.g., `csv_cli.py`), auto help & typing.
- Evidence: `pyproject.toml`, `analytics/pyproject.toml`, imports in `csv_cli.py`.

### rich
- Version: 14.1.0 (installed), declared >=13.0.0 (root) and `13.7,<14` (analytics)
- Install Source: both `pyproject.toml`
- Purpose: Colored / structured console output, progress bars for governance & analytics runs.
- Evidence: dependency declarations.

### python-dateutil
- Version: 2.9.0.post0 (installed)
- Install Source: root `pyproject.toml`
- Purpose: Robust ISO8601 parsing / normalization of heartbeat & timestamp fields across trackers.
- Evidence: root dependency list.

### pydantic
- Version: 2.11.7 (installed), declared >=2.6 (root) and `>=2.7,<2.8` (analytics)
- Install Source: both `pyproject.toml`
- Purpose: Data validation / modeling for tracker entities & analytics schemas (ensures strict typing before persistence or analysis).
- Evidence: declarations + imports in analytics package (not read here but implied by presence).

### orjson
- Version: 3.11.2 (installed), declared >=3.9.0 (root) and `>=3.10,<4.0` (analytics)
- Install Source: both `pyproject.toml`
- Purpose: High‑performance JSON serialization for log/event emission & evidence bundling.
- Evidence: declarations.

### xxhash
- Version: 3.5.0 (installed), declared >=3.4.1 (root)
- Install Source: root `pyproject.toml`
- Purpose: Fast non‑cryptographic hashing for content_hash / artifact integrity quick comparisons.
- Evidence: root declaration.

### fastapi
- Version: 0.116.1 (installed), declared >=0.111.0
- Install Source: root `pyproject.toml`
- Purpose: Future lightweight service/API exposure for orchestration or metrics (scaffolding present via dependency only).
- Evidence: root declaration.

### uvicorn
- Version: 0.35.0 (installed), declared >=0.30.0
- Install Source: root `pyproject.toml`
- Purpose: ASGI server to run FastAPI endpoints (planned observability / status endpoints).
- Evidence: root declaration.

## Analytics Layer Dependencies

### pandas
- Version: 2.3.2 (installed), declared `>=2.2,<2.3` (note: installed version exceeds declared upper bound → potential version drift risk)
- Install Source: `analytics/pyproject.toml`
- Purpose: DataFrame manipulation of tracker CSVs, coverage & metrics aggregation.
- Evidence: analytics declaration; installed version probe.
- Note: Upper bound mismatch should be reviewed (adjust constraint or downgrade environment for reproducibility).

### pyarrow
- Version: 21.0.0 (installed), declared `>=16.0,<17.0` (installed exceeds upper bound → drift)
- Purpose: Columnar interchange / Parquet or Arrow backing for high‑performance analytics exports.
- Evidence: analytics declaration; installed version probe.

### jsonschema
- Version: 4.25.1 (installed), declared `>=4.22,<5.0` (analytics)
- Install Source: analytics `pyproject.toml` dev dependencies
- Purpose: Validate structured documents (e.g., task schema, instruction compliance) at runtime.
- Evidence: analytics declaration; newly installed and verified.

### tqdm
- Version: 4.67.1 (installed), declared `>=4.66,<5.0` (analytics)
- Install Source: analytics `pyproject.toml` dependencies
- Purpose: Progress bars for long analytics runs.
- Evidence: analytics declaration; newly installed and verified.

### python-dotenv
- Version: 1.1.1 (installed), declared `>=1.0,<2.0` (analytics)
- Install Source: analytics `pyproject.toml` dependencies
- Purpose: Environment variable management for analytics CLI (loading .env).
- Evidence: analytics declaration; newly installed and verified.

### polars (optional perf extra)
- Version: 1.32.3 (installed), declared optional `>=0.21,<0.22` (installed far newer → drift)
- Purpose: Faster DataFrame ops for large tracker datasets; optional performance path.
- Evidence: optional dependency list; installed probe.

### duckdb (perf optional repeat)
- See earlier (version drift vs analytics optional specifies `>=1.0,<2.0` satisfied by 1.3.2).

## Dev / Quality Tooling

### pytest / pytest-cov
- Versions: 8.4.1 / 6.2.1 (installed) vs root optional (no version pins) and analytics dev pins.
- Purpose: Testing & coverage enforcement (≥80% threshold root; analytics coverage config present).
- Evidence: root optional `dev` extras; analytics dev extras; coverage config sections.

### ruff
- Version: 0.12.9 (installed) vs analytics dev `>=0.5,<0.6` (drift; installed outside specified range).
- Purpose: Fast linting & style enforcement.
- Evidence: analytics dev optional.

### mypy
- Version: 1.17.1 (installed) vs analytics dev `>=1.10,<1.11` (drift – pin mismatch).
- Purpose: Static typing assurance.
- Evidence: analytics dev optional.

### hypothesis
- Version: 6.138.3 (installed) root dev extra.
- Purpose: Property-based tests for robustness of parsers & transformations.
- Evidence: root dev extras.

### pip-audit, pre-commit
- Versions: pip-audit 2.9.0, pre-commit 4.3.0 (installed)
- Declared in analytics dev extras; newly installed and verified. Provide supply chain and workflow hooks.
- Status: Installed and operational.

## Legacy / Notebook Requirements (`requirements.txt`)

### structlog
- Version: 23.3.0 (installed) vs requirements `structlog>=23.0,<24.0`
- Purpose: Structured logging backbone (may overlap / inform UnifiedLogger design choices).
- Evidence: `requirements.txt`.

### numpy, scikit-learn, matplotlib, seaborn, joblib, psutil, pandas (duplicate), pytest
- Purpose: Legacy ML workflow / exploratory analysis; may be superseded by analytics package; keep until confirmed obsolete.
- Evidence: `requirements.txt` entries and installed versions (see probe list).
- Note: Overlap with analytics environment increases risk of constraint conflicts.

## Version Drift / Reproducibility Risks
- Detected upper bound violations: pandas, pyarrow, polars (optional), ruff, mypy.
- Previously missing libraries now installed: jsonschema, tqdm, python-dotenv, pip-audit, pre-commit.
- Action: Run `pip install -e .[dev]` for both root and analytics or unify environment manager (PDM / uv) with lockfile generation.

## Triple-Check Summary
1. List: Extracted from dependency declarations + requirements.
2. Verify: Cross-checked with installed environment (pip metadata) — flagged drifts/missing.
3. Reproduce: Reproduction requires installing root + analytics extras; lockfile recommended to pin versions and eliminate drift.

## Next Recommendations
- Align versions with declared upper bounds or relax constraints intentionally.
- Generate a consolidated lockfile (PDM or uv) and remove stale `requirements.txt` if superseded.
- Add environment validation script to log drift events.

---
Generated by automated workspace audit (workspace-first, no fabrication).
