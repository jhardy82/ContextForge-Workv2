# Tracker Dashboard

HostPolicy: PythonHelper

## Overview

A lightweight FastAPI-based dashboard rendering Projects, Sprints, and Tasks from the tracker SQLite database (`db/trackers.sqlite`). Provides quick visibility plus server-side filtering.

## Running

```bash
python dashboard_server.py
```

(Default port 8077; override PORT env var if needed.)

Or directly with uvicorn:

```bash
python -m uvicorn python.dashboard.app:app --reload --port 8077
```

## Filters

| Route     | Query Params                           | Description                                                         |
| --------- | -------------------------------------- | ------------------------------------------------------------------- |
| /projects | status, search                         | Exact status filter; case-insensitive substring match on id or name |
| /sprints  | status, search                         | Same semantics as projects                                          |
| /tasks    | status, project, sprint, shape, search | Exact filters; search matches id or title                           |

All filters are optional and combinable. Empty submission resets to the unfiltered view; each page includes a Reset link.

## Pagination (Implemented)

`/tasks` supports server-side pagination via `page` (1-based) and `limit` (default 50, min 5,
max 200). Responses clamp `page` to last available page if out of range. JSON API variant
(`/api/tasks`) returns metadata: `page`, `pages`, `limit`, `total`, `count`.

Example:

```text
/api/tasks?status=done&limit=25&page=3
```

## Aggregated Metrics (Implemented)

Root (`/`) renders status count summaries for Projects, Sprints, and Tasks. `/tasks` view includes filtered status distribution for the current filter set. JSON variant of tasks also includes `status_counts` for external consumers.

## JSON API Endpoints (Implemented)

| Endpoint      | Description                                       |
| ------------- | ------------------------------------------------- |
| /api/projects | Projects (same filters: status, search)           |
| /api/sprints  | Sprints (status, search)                          |
| /api/tasks    | Tasks with filters + pagination + `status_counts` |

Each API returns: `data` (list), `count` (page row count), filter echo, and for tasks additional pagination and totals. Intended for lightweight integration or future SPA.

## Accessibility Enhancements

Templates include ARIA labels for navigation, form landmarks, table captions, `scope="col"` headers, and badges with sufficient contrast classes. Pagination controls expose `aria-label` per button.

## Query Timing

Requests accumulate per-query timings (middleware attaches a wrapper). Aggregated total (ms)
emitted in response header `X-Query-Time-MS` when queries executed. Useful for quick
performance inspection without full profiling. (Header available for both HTML and JSON
routes.)

## Test Coverage

Pytest coverage now includes: filters, pagination metadata, JSON API structure, query timing header, and metrics presence (`tests/python/test_dashboard_*.py`).

## Indices

On startup the app ensures indices for common columns: tasks(status, project_id, sprint_id, geometry_shape, updated_at), projects(status), sprints(status).

## Logging

Each page view emits a `dashboard_view` unified log event; startup emits `dashboard_startup` with success state.

## Testing

Pytest tests in `tests/python/test_dashboard_filters.py` exercise filtering logic with an isolated temporary database.

## Future Enhancements

- Optional per-query breakdown exposure (`?debug=timing`) in JSON
- Shape/priority distribution charts
- Caching layer for heavy aggregate queries
- Auth + role-based visibility
- CSV export / streaming endpoint
