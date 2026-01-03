# Logging & Observability Index

| Document | Purpose |
| --- | --- |
| `legacy_id_usage_inventory.md` | Legacy logging ID usage inventory (historical reference). |
| `../../projects/cf_logging/Project-Checklist.md` | Project checklist for cf_logging (logging configuration and pipelines). |
| `../../projects/unified_logger/Project-Checklist.md` | Project checklist for UnifiedLogger (JSONL schema and adapters). |
| `../../TaskMan-v2/backend-api/utils/logger.py` | Structured logging helper for TaskMan-v2 backend (JSON formatter + correlation IDs). |
| `../../docs/validation/INDEX.md` | Validation index including logging gate tests and QSE validation guidance. |

## Canonical Structured Logging Schema (High-Level)

All new and modernized logging should aim to emit JSONL events with fields such as:

- `timestamp`: ISO8601 UTC timestamp for the event.  
- `level`: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).  
- `logger` / `component`: Logical name of the logger or subsystem.  
- `action`: Short, machine-friendly event name (for example, `taskman_v2.backend.startup`).  
- `message`: Human-readable message string.  
- `correlation_id` / `run_id`: Identifier for correlating related events.  
- `ok` / `command_ok`: Boolean or semantics flag indicating success/failure (where applicable).  
- `error_message` / `stack_trace`: Included for error events when available.  
- Additional context fields: structured key/value pairs relevant to the event.

For Python components, prefer the existing helpers:

- UnifiedLogger (for CF_CORE / CF_CLI flows where available).  
- `TaskMan-v2/backend-api/utils/logger.py` for backend API routes and startup/shutdown.  

For Node/TypeScript and PowerShell components, choose loggers or wrappers that emit the same field set and JSONL structure.

