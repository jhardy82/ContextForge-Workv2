# dbcli Command Map (Discovery Draft)

Status: Draft (Updated 2025-08-29 – post DB-first upsert & dry-run implementation)
Scope: Enumerates current dbcli subcommands, purpose, idempotency pattern, key options, and logging expectations.
Reflects explicit upsert commands, sprint normalization, DB-first persistence, dry-run support, and CSV write guard under authority sentinel.
Direct CSV editing is deprecated; after authority activation core tracker CSV writes are blocked (guard) instead of silently exporting.

## Global Patterns
- Invocation: `.venv/Scripts/python.exe dbcli.py <domain> <subcommand> [options]`
- Global Flags (root): `--quiet` (suppress non-essential output), `--test-mode` (enables quiet + CF_TEST_MODE=1 for deterministic automation)
- Logging: session_start, decision (empty/results), artifact_emit (CSV/JSON outputs), task_* transitions, session_summary.
- Idempotency: Create commands generate new IDs; updates mutate existing record fields. Upsert pattern = list/filter + conditional create/update.

## Context
| Subcommand | Purpose | Notes |
|-----------|---------|-------|
| get | Show current context objects | JSON/text variants (future) |
| export | Write context snapshot to file | Emits artifact_emit |
| import | Load context snapshot | Validates schema before replace |
| set | Set a single context key | Idempotent key overwrite |
| sync | Reconcile context vs DB | Decision events on drift |
| upsert-object | Insert or update arbitrary context object | Explicit upsert support (diff logged) |
| validate | Validate context consistency | Emits decision event (result=success/fail) |

## Status
| Subcommand | Purpose | Key Flags | Notes |
| migration | Show migration authority & sentinel state | --json | Gate tasks after sentinel |
| repair | Attempt authority repair | high risk operations log decision |
| validate | Validate tracker integrity | emits integrity results |
| duckdb | Inspect DuckDB status | future consolidation |
| hours-scan | Scan legacy hours fields | Promotes normalization |

## Tasks
| Subcommand | Purpose | Key Flags | Idempotency | Logging |
| create | Create new task (auto ID) | --title, --priority, --project-id | Always new ID (T-YYYYMMDD[-N]) | task_create + artifact_emit |
| list | List tasks (filter/sort) | --status, --project, --json, --order-by, --desc, --limit | Read-only | artifact_touch_batch, decision empty |
| start | Transition to in_progress | task_id (arg) | Guarded noop if already in_progress | task_start (decision noop) |
| complete | Transition to done | --notes | Guarded noop if already done | task_complete (decision noop) |
| update | Mutate fields (title,status,minutes,etc.) | many flags | Update existing only | task_update |
| show | Show single task details | task_id | Read-only | decision not_found on miss |
| search | Text search task fields | --query | Read-only | decision empty |
| enhance | Auto enrich task metadata | --task-id | Mutates record | task_enhance (future) |

## Projects
| Subcommand | Purpose | Notes |
| tasks | List tasks for project | Convenience filter |
| create | Create project (ID pattern P-`slug`[suffix]) | Collision adds numeric suffix |
| list | List projects | JSON via --json |
| show | Show single project | decision not_found on miss |
| update | Update project metadata | Partial field mutation |
| normalize | Normalize project records | Repairs malformed legacy array ingestion rows |
| upsert | Idempotent create/update | Accepts --id plus --title/--name (aliases) |

## Sprints
| Subcommand | Purpose | Notes |
| create | Create sprint (S-YYYY-MM-DD) | Date-based ID uniqueness |
| list | List sprints | JSON via --json |
| show | Show sprint details | Includes linked tasks (future) |
| update | Update sprint metadata | Partial mutation |
| tasks | List sprint tasks | DB authority (CSV read fallback pre-sentinel) |
| normalize | Normalize sprint records | Repairs missing id/name from legacy rows |
| upsert | Idempotent create/update | Accepts --id, --title/--name, optional --project-id |

## Agents (Gamification)
| Subcommand | Purpose |
| register | Register new agent |
| whoami | Show active agent identity |
| list | List agents |
| complement | Add compliment / positive feedback |
| leaderboard | Show leaderboard |
| activity | Show agent activity feed |
| deregister | Remove agent (soft) |
| heartbeat | Update agent heartbeat |
| recover | Recover soft-deleted agent |
| prune | Hard prune inactive agents |

## Velocity
| Subcommand | Purpose |
| record | Record completed work (hours/points) |
| report | Summarize recent velocity metrics |
| predict | Predict time for points w/ complexity |
| metrics | Emit velocity metrics artifact |

## Workflow
| Subcommand | Purpose |
| template | Show workflow template |
| apply | Apply workflow to tasks/projects |
| transition | Perform batch status transition |
| batch | Batch operation helper |
| link | Link related entities |

## Performance
| Subcommand | Purpose |
| cache | Show or prime caches |
| optimize | Run optimization tasks |
| validate | Validate performance assumptions |
| compliance | Performance compliance scan |
| benchmark | Run benchmarks |

## Drift
| Subcommand | Purpose |
| monitor | Start or run drift monitor |
| check | One-time drift scan |

## Analytics
| Subcommand | Purpose |
| velocity | Advanced velocity analytics |
| burndown | Burndown chart data |
| geometry | Sacred geometry distribution |
| metrics | Aggregate metrics export |

## Logging Expectations
- Every mutating subcommand: session_start, task_start (implicit domain), artifact_emit (CSV changed), decision (when branching or noop), session_summary.
- Read-only list/show: session_start, artifact_touch_batch (when >1), decision empty (when none), session_summary.

## Upsert Commands & Guidance
Explicit upsert commands now exist (DB-first when authority sentinel present):
| Domain | Command | Key Aliases | Behavior |
|--------|---------|-------------|----------|
| Project | `project upsert` | --title / --name | Create or update by id or name; generates P- slug if absent |
| Sprint | `sprint upsert` | --title / --name | Create or update; derives S-YYYY-MM-DD id if dates supplied or uses provided id |
| Task | `task upsert` | --title | Create or update by id or title; generates T-shortuuid if absent |

Pattern:
1. Detect existing entity (by --id first, then name/title alias when supported).
2. Compute minimal field diff (changed keys only).
3. If `--dry-run` specified: emit JSON preview and skip persistence.
4. Persist changes:
	 - When `trackers/DB_AUTHORITY.SENTINEL` present: write to SQLite only (`persisted_via="db"`). Core CSV export is suppressed by guard.
	 - Otherwise (pre-authority): write legacy CSV (`persisted_via="csv"`).
5. Emit upsert decision event + JSON (fields: created, changes, entity snapshot, dry_run, persisted_via).

Non-JSON output uses quiet-aware `qprint` (suppressed when `--quiet` / `--test-mode`). Deprecated fallback workflow (manual list → conditional create/update) is superseded.

Dry-Run Output Schema (example):
```json
{
	"created": true,
	"changes": {"title": "Example Project"},
	"entity": {"id": "P-EXAMPLE", "title": "Example Project", "status": "new"},
	"dry_run": true,
	"persisted_via": "db" | "csv"
}
```
`created` false + non-empty `changes` => update; both false/empty => noop.

## Pending Enhancements
- Extend noop decision logging parity across all guarded transitions (start/complete done; add review->done nuance later).
- Integrate quiet/test-mode usage examples into README/operator guide.
- Add JSON output for `tasks` listing under project/sprint subcommands (consistent cross-domain behavior).
- Introduce explicit `export snapshot` command to produce read-only CSV artifacts post-DB mutation (guard currently blocks implicit export).
- Add focused tests for `persisted_via` correctness (CSV vs DB) and `direct_csv_write_blocked` event log surface (partial coverage added; expand to all domains).
- Refactor diff computation into shared helper to reduce duplication across project/sprint/task upsert implementations.

## Database Authority Note
Once `trackers/DB_AUTHORITY.SENTINEL` is present:
- Core tracker CSV files (projects.csv, sprints.csv, tasks.csv) become **read-only export artifacts**; implicit writes are blocked.
- Upsert & mutation commands persist exclusively to SQLite (DB-first) and set `persisted_via="db"`.
- Legacy CSV fallback path remains active only when the sentinel is absent (`persisted_via="csv"`).

Write Guard:
- Attempted core CSV writes emit `direct_csv_write_blocked` decision events and are skipped.
- Non-core / analytics CSV outputs remain permitted.
- Future snapshot export will be an explicit command (pending) rather than automatic side-effect.

Operational Implication: CI / tooling relying on updated CSV must transition to DB queries or await the explicit snapshot command.

(End of draft)
