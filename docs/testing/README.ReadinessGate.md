<!-- HostPolicy: PythonHelper -->
# Nudge Readiness & Migration Authority Gate

> **UNIFIED TRACKER NOTICE**: The readiness & authority model described here assumes the unified SQLite tracker (via `dbcli.py`) is canonical. Legacy direct CSV workflows are deprecated and only retained as archival artifacts.

This document describes the consolidated readiness gating, refresher evidence pack, and CSV→SQLite migration authority model implemented under the "Nudge 11.5 Readiness & Validation Gate" initiative.

## Artifact Overview

Generated into `build/artifacts/` (unless otherwise noted):

| Artifact | Purpose | Generation Trigger |
|----------|---------|--------------------|
| `inventory.validation.json` | Current inventory snapshot (nudges/tasks) | Base readiness run |
| `nudge_status.json` | Per‑nudge detection results & alias matches | Base readiness run |
| `nudge_task_audit.json` | Task coverage / gaps | Base readiness run |
| `env.validation.json` | Environment sanity (python, paths) | Base readiness run |
| `quality_validation.json` | Lightweight quality summary (pytest/ruff subset) | Base readiness run (non-blocking on failures) |
| `nudge_readiness.json` | Aggregated readiness pass/fail + gating summary | Base readiness run |
| `refresh_status.json` | Refresher Pack summary & condensed statements | Refresher pack run |
| `refresh_nudge_*.json` | Per‑nudge evidence (1,4,6,7,11) | Refresher pack run |
| `transcription_capture.txt` | Tail of migration/log transcript (N4 evidence) | Refresher pack run |
| `plugin_research.lock` | Plugin research lock sentinel (N6) | Refresher pack run |
| `cli_unification_map.json` | CLI subcommand mapping evidence (N7) | Refresher pack run |
| `gamify_drift.json` | Gamification drift heuristic state (N11) | Refresher pack run |
| `db_authority.validation.json` | Migration authority validation (meta table, pending/unarchived) | Readiness integration or standalone authority check |
| `nudge_readiness_enriched.json` | Unified enriched readiness (readiness + authority + condensed refresher) | Enrichment phase (auto after readiness + refresher) |
| `readiness.min.json` | Minimal fallback (tests / light runs) | `generate_enriched_only()` path |
| `trackers/DB_AUTHORITY.SENTINEL` | High‑confidence authority sentinel (clean migration state) | Emitted when no pending/unarchived CSVs |
| `nudge_readiness_enriched.json` (hash chain fields) | `prev_hash`, `content_hash`, `chain_length`, `schema_version` for tamper-evident lineage | Automatically added on each enrichment write |

## Enriched Readiness Schema (Excerpt)

```jsonc
{
  "readiness": { "ok": true, "nudges_passed": 11, ... },
  "authority": { "meta_table_present": true, "pending_migration": [], ... },
  "refresher": {
    "condensed": {
      "1": "Inventory diff clean (Δ0) — steady baseline",
      "4": "Transcription tail captured (lines=42) — recent activity present",
      "6": "Plugin research lock present — research phase acknowledged",
      "7": "CLI unification stable (mapped=12) — no divergence",
      "11": "Gamify streak stable — no drift detected"
    }
  },
  "generated_at": "2025-08-27T12:34:56.789Z"
}
```

Condensed statements are hard‑capped at 369 chars to remain HUD‑friendly.

Hash Chain:

Each successive enriched readiness artifact includes the SHA‑256 of its serialized predecessor
(`prev_hash`) and its own `content_hash`, yielding a simple append‑only verification chain (reset
if file deleted). `chain_length` monotonically increments.

## CLI Status Command

Use the dbcli Typer application to query migration authority and (optionally) refresher condensed output:

```pwsh
python dbcli.py status migration            # Rich table (default)
python dbcli.py status migration --json     # Force machine JSON output
python dbcli.py status migration --no-show-condensed  # Omit refresher condensed block
```

Key fields:

- `ok`: Overall authority health (meta table present & no pending/unarchived CSVs)
- `sentinel_present`: Whether `trackers/DB_AUTHORITY.SENTINEL` exists
- `pending_migration`: CSVs migrated logically but not archived / recorded
- `unarchived_csv`: CSVs still present without archival marker after successful migration
- `refresher_condensed`: Map of nudge → condensed statement (if available)

## Test Utilities

`generate_enriched_only()` (in `python/validation/nudge_readiness_gate.py`) enables tests to synthesize enriched artifacts without executing full quality (lint/tests) for speed and isolation.

## Gamification Drift Heuristic

`gamify_drift.json` encodes a boolean flag derived from searching recent gamification transcript lines for streak continuity markers. Tests validate both drift and non‑drift branches to ensure heuristic robustness.

## Sentinel Rationale

`DB_AUTHORITY.SENTINEL` is the human + pipeline readable assertion that CSV→SQLite migration has
completed, the meta table is authoritative, and no legacy writable sources remain. Its absence
indicates either in‑flight migration or regression requiring remediation.

## Unified Task Management (dbcli)

All task / sprint / project interactions MUST occur through the unified database CLI (`dbcli.py`) once the authority sentinel is present. Direct CSV edits are deprecated (read-only for forensics). Core patterns:

```pwsh
# List tasks (rich)
python dbcli.py task list

# Create a task
python dbcli.py task create --title "Add JSON flag" --project P-READINESS-MIG --sprint S-2025-08-27-RD --priority medium

# Update status to done
python dbcli.py task update T-DBCLI-JSON --status done

# Show migration authority (machine JSON)
python dbcli.py status migration --json
```

Policy: If `trackers/DB_AUTHORITY.SENTINEL` exists, agents/scripts should refuse to write CSVs and instead invoke the appropriate dbcli subcommand (emit a decision event `direct_csv_write_blocked` on attempted legacy path).

## CI / Pipeline Consumption

For deterministic parsing, prefer:

```pwsh
$status = python dbcli.py status migration --json | ConvertFrom-Json
if (-not $status.ok) { throw "Migration authority not clean" }
```

## Next Enhancements

- Expand integration test to verify enriched artifact after end‑to‑end quality chain.
- Add schema versioning header to enriched readiness artifact.
- Emit `artifact_emit` events with sha256 for each readiness artifact (hash chaining) for evidence tier promotion.

---
Maintained under the ContextForge Universal Methodology (Logging First, Workspace Reuse, DB‑First authority). Suggestions & refinements welcome.
