# Local Heartbeat Monitoring

Lightweight local HTTP server + pusher to surface and collect test heartbeat + summary data.

## Components

- `python/monitoring/heartbeat_server.py` – stdlib http.server with endpoints:
  - `GET /health` current watcher status
  - `GET /runs` brief map of known runs
  - `GET /runs/{run_id}` detailed cached heartbeat + summary
  - `POST /heartbeat` accept heartbeat JSON `{ run_id, ... }`
  - `POST /event` generic event logging
- `python/monitoring/push_heartbeat.py` – posts latest run heartbeat (or a synthesized stub) once or on an interval.

## VS Code Tasks

- `Monitoring: Start Heartbeat Server (Background)` – starts server on `127.0.0.1:8765`.
- `Monitoring: Push Heartbeats (Background)` – periodically sends heartbeats every 5s.

## Manual Usage

```powershell
# Start server (foreground)
python python/monitoring/heartbeat_server.py --port 8765

# Push once
python python/monitoring/push_heartbeat.py --server http://127.0.0.1:8765 --once

# Query health
Invoke-RestMethod -Uri http://127.0.0.1:8765/health

# List runs
Invoke-RestMethod -Uri http://127.0.0.1:8765/runs

# View specific run
Invoke-RestMethod -Uri http://127.0.0.1:8765/runs/PYT-<id>

# Post custom heartbeat
$hb = @{ run_id = 'PYT-DEMO'; progress_updates = 3; tests_per_sec = 0.9 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8765/heartbeat -Body $hb -ContentType 'application/json'
```

## Logs

JSONL events: `logs/monitor/heartbeat_server.jsonl` (watcher_start, server_start, heartbeat_ingest, watcher_error,...)

## Integration Ideas

- Enhance pytest harness to POST incremental progress on each collected test.
- Create a VS Code custom view polling `/runs` for live status.
- Add retention or persistence if long-term history required (currently in-memory).

## Design Notes

- Zero external dependencies (fits Direct Invocation policy).
- Uses timezone-aware UTC timestamps (`datetime.UTC`).
- Watcher polls `latest-run.txt` every 2s; if available, ingests `heartbeat.json` + `summary.json`.
