# Pytest UI & Logging Guide

This project standardizes test output and evidence collection:

- Rich panels: Start/end panels summarize run state and results
- Structured summary table: Compact Rich table with Passed/Failed/Skipped/Total
- JSONL lifecycle/events: Repo-local logs under `logs/tests/duckdb`
- Optional pytest-rich: Enables progress bars/tables when installed

## Where artifacts go

- Events JSONL: `logs/tests/duckdb/<RUN_ID>.events.jsonl`
- Summary JSON: `logs/tests/duckdb/<RUN_ID>.summary.json`
- Pointer: `logs/tests/duckdb/LATEST.events.pointer.json`

## Enabling/Disabling banners

- Disable banners: pass `--no-rich` or set `CF_RICH_BANNER=0`
- Default is ON if Rich is installed

## pytest-rich integration (optional)

If `pytest-rich` is installed, the test session will render richer progress bars and result tables automatically.

## Running a focused subset

Use your venv’s Python to run specific tests:

```pwsh
& "$PWD\.venv\Scripts\python.exe" -m pytest -q tests\python\test_rich_ui_rendering.py
```

## Troubleshooting

- If panels/tables don’t appear, check that Rich is installed and banners aren’t disabled.
- Always check `LATEST.events.pointer.json` to locate the current run’s JSONL.
