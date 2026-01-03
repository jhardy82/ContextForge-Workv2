# DuckDB Velocity & Analytics Validation Matrix (SR‑4)

This matrix captures the SR‑4 synthesis for **DuckDB‑based analytics** in ContextForge, focused on:
- The DuckDB velocity tracker (`python/velocity/velocity_tracker.py`),
- The PowerShell CLI wrapper (`cli/Invoke-VelocityTracker.ps1`),
- Tracker‑driven DuckDB prototypes (`scripts/Acquire-DuckDbCli.ps1`, `scripts/Build-DuckDbTrackerIndex.ps1`),
- DuckDB MCP servers configured in `.vscode/mcp.json`.

The emphasis is on **static evidence from this repository** (code and docs). Runtime validation and performance testing are called out as explicit next steps.

## Components & Results

| ID          | Component / Scenario                                                    | Test Type    | Expected Behavior                                                                 | Actual (SR‑4 Static Review)                                                                                                                                                                                                                                            | Evidence (Paths)                                                                                                                                                                                                                                                     | Status   |
|-------------|-------------------------------------------------------------------------|--------------|----------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| DKV-1       | DuckDB velocity schema initialization                                  | Unit / Schema | DuckDB DB at `db/velocity.duckdb` initialized with work_sessions, tasks, metrics | `VelocityTracker.__init__` creates `db/velocity.duckdb` (if missing) and `_initialize_schema` defines `work_sessions`, `tasks`, `velocity_metrics`, `complexity_factors` with appropriate columns and defaults.                                                        | `python/velocity/velocity_tracker.py`, `docs/DuckDB-Velocity-Tracker.md`                                                                                                                                                                                             | PARTIAL  |
| DKV-2       | Velocity calculation from recent work_sessions/tasks                    | Unit         | Aggregates recent sessions into velocity metrics (hours/point, points/day, etc.) | `calculate_velocity(days_back=30)` implements CTE‑based aggregation over `work_sessions` and `tasks`, returning a dict with `completed_tasks`, `total_points`, `avg_hours_per_point`, `points_per_day`, etc., with a sensible default branch when no data is present. | `python/velocity/velocity_tracker.py` (calculate_velocity), `docs/DuckDB-Velocity-Tracker.md`                                                                                                                                | PARTIAL  |
| DKV-3       | CLI wrapper for record / update / velocity / predict / report           | Integration  | PowerShell CLI delegates to Python engine and returns JSON / formatted output    | `Invoke-VelocityTracker.ps1` validates the venv and script path, then invokes `velocity_tracker.py` with `--action` (record/update/velocity/predict/report) and formats JSON output for human‑readable summaries; import modes are scaffolded but not fully implemented. | `cli/Invoke-VelocityTracker.ps1`, `python/velocity/velocity_tracker.py`, `docs/DuckDB-Velocity-Tracker.md`                                                                                                                   | PARTIAL  |
| DKV-4       | Velocity‑based prediction behavior (historical vs fallback defaults)    | Integration  | Uses historical DuckDB data when available, otherwise falls back to safe defaults | `predict_completion` defers to `calculate_velocity`; when `avg_hours_per_point` > 0 it computes estimated hours/days and confidence based on completed task count, otherwise falls back to a conservative default (8 hrs/point, low confidence), as described in docs. | `python/velocity/velocity_tracker.py` (predict_completion), `docs/DuckDB-Velocity-Tracker.md`                                                                                                                                | PARTIAL  |
| DKV-5       | DuckDB CLI acquisition for analytics parity                            | System / Tooling | Acquire `duckdb.exe` deterministically for parity tests                          | `Acquire-DuckDbCli.ps1` downloads and extracts a pinned DuckDB CLI into `tools/duckdb/`, emits structured JSONL events via `Write-ULogSafe`, and exits gracefully (skipped or fail) depending on `-FailIfMissing`; not exercised here.                                  | `scripts/Acquire-DuckDbCli.ps1`, `docs/DuckDB-Velocity-Tracker.md`                                                                                                                                                                                                  | PARTIAL  |
| DKV-6       | Tracker‑driven DuckDB prototype DB (`data/trackers.duckdb`)             | System / Prototype | Build analytical DuckDB DB over tracker JSON/CSV artifacts                       | `Build-DuckDbTrackerIndex.ps1` first prefers a Python implementation (`cf_tracker.duckdb_builder`), then falls back to `duckdb.exe`, creating `trackers`, `inventory_history`, `kind_stats`, `sqlite_meta` tables and views, emitting JSONL events when `-EmitEvents`. | `scripts/Build-DuckDbTrackerIndex.ps1`, `inventory/trackers/*` (expected inputs), `logs/duckdb_tracker_events.jsonl` (when `-EmitEvents` used)                                                                               | PARTIAL  |
| DKV-7       | DuckDB MCP servers for velocity and dashboard DBs                       | MCP / Integration | DuckDB MCP servers expose DuckDB DBs over STDIO for assistants                   | `.vscode/mcp.json` defines `DuckDB-velocity` and `DuckDB-dashboard` servers using `mcp-server-duckdb` with `db/velocity.duckdb` and `db/dashboard_history.duckdb` paths; not exercised here, but aligned with DuckDB velocity tracker and dashboard history concepts.     | `.vscode/mcp.json`, `docs/DuckDB-Velocity-Tracker.md`, `docs/01-Overview.md` (velocity sections)                                                                                                                             | PARTIAL  |

Status key: **PASS** – behavior confirmed with runtime evidence; **PARTIAL** – implementation present but needs runtime/tests; **GAP** – missing or unimplemented.

At the SR‑4 synthesis stage, all rows above are **PARTIAL** because this environment has not executed the DuckDB engine, CLI, or MCP servers end‑to‑end. The matrix is designed to be upgraded to PASS as runtime validation and tests are added.

## Notes & Next Steps (SR‑4)

- Add **pytest‑based velocity tracker tests** (for example, `@pytest.mark.velocity_tracker`) that:
  - Create a temporary DuckDB file, seed a few `tasks` and `work_sessions` rows, and assert the `calculate_velocity` and `predict_completion` outputs.
  - Exercise `generate_report` with realistic data and assert the shape of `recent_tasks`.
- Add a small **CLI smoke test** (Python or PowerShell) that:
  - Invokes `Invoke-VelocityTracker.ps1` with `-Action Velocity` and `-Action Predict`, capturing JSON output for evidence.
  - Verifies that the CLI passes `--db` correctly and surfaces Python errors meaningfully if the venv is misconfigured.
- For **tracker‑driven DuckDB prototypes**:
  - Ensure `inventory/trackers/*.json` and related artifacts are present, then run `scripts/Build-DuckDbTrackerIndex.ps1 -EmitEvents` and capture `logs/duckdb_tracker_events.jsonl` as evidence.
  - Add minimal tests or scripts that query `data/trackers.duckdb` (for example, `SELECT COUNT(*) FROM trackers.trackers;`) to confirm that ingestion works.
- For **MCP integration**:
  - Use the DuckDB MCP servers defined in `.vscode/mcp.json` from a local VS Code instance to:
    - Run simple `SELECT 1` queries against `db/velocity.duckdb`.
    - Explore velocity metrics via MCP tools (read‑only).
  - Record at least one JSONL evidence bundle tying MCP behavior to DuckDB contents.

These steps will allow the matrix rows above to be upgraded from **PARTIAL** to **PASS**, and will generate additional evidence bundles for QSE and CF_CLI‑aligned validation workflows.

## Runtime Validation Plan (Fast Smoke)

To promote items from PARTIAL → PASS quickly, execute a focused smoke set and capture evidence.

1) Python embedded engine (smoke)

```powershell
& ".\.venv\Scripts\Activate.ps1"

# Basic SELECT and arithmetic
python - << 'PY'
import duckdb
con = duckdb.connect()
print(con.execute("SELECT 1 AS ok").fetchall())
print(con.execute("SELECT 2+2 AS four").fetchone())
PY

# Window function & join sample
python - << 'PY'
import duckdb
con = duckdb.connect()
con.execute("CREATE TABLE t(a INTEGER, g INTEGER)")
con.execute("INSERT INTO t VALUES (1,1),(2,1),(3,2),(4,2)")
q = """
SELECT a, g,
       ROW_NUMBER() OVER (PARTITION BY g ORDER BY a) AS rn
FROM t
ORDER BY g, a
"""
print(con.execute(q).fetchdf())
PY

# Parquet/CSV ingestion check
python - << 'PY'
import duckdb, pandas as pd
from pathlib import Path
p = Path('tmp_duckdb')
p.mkdir(exist_ok=True)
df = pd.DataFrame({'x':[1,2,3],'y':[10,20,30]})
parquet = p/'sample.parquet'
csv = p/'sample.csv'
df.to_parquet(parquet)
df.to_csv(csv, index=False)
con = duckdb.connect()
print(con.execute(f"SELECT COUNT(*) FROM read_parquet('{parquet.as_posix()}')").fetchone())
print(con.execute(f"SELECT SUM(y) FROM read_csv('{csv.as_posix()}')").fetchone())
PY
```

2) Evidence capture

- Record command outputs and compute SHA‑256 with `Get-FileHash`.
- Log DuckDB version: `python -c "import duckdb; print(duckdb.__version__)"`.
- Store artifacts and hashes in the session evidence bundle (JSONL) per logging standards.

3) Reference

- See `.QSE/v2/Research/SR-4-DuckDB-Capabilities-Comparative-Matrix.md` for the detailed comparison and DKV mapping table.
