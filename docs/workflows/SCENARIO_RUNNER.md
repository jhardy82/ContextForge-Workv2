# E2E Scenario Runner

This runner provides a safe, non-destructive way to produce workspace inventory snapshots and gamification events for E2E scenario validation.

Files produced:

- `build/artifacts/inventory.e2e.<ts>.json` — timestamped inventory snapshot
- `build/artifacts/e2e_context_snapshot.json` — stable snapshot used by downstream steps
- `build/artifacts/gamify.jsonl` — appended gamification events

Usage:

Run a dry-run (safe, default):

pwsh -NoProfile -ExecutionPolicy Bypass -Command "python .\workflows\scenario_runner.py --dry-run"

Request commit mode (not implemented in this lightweight scaffold):

pwsh -NoProfile -ExecutionPolicy Bypass -Command "python .\workflows\scenario_runner.py --commit"

Notes:

- By design this scaffold does not modify DB or CSV files. It is intended as a starting point for the E2E harness.
- The gamification helper (`tools/gamify.py`) writes JSONL events which can be aggregated for dashboards or scoring.
