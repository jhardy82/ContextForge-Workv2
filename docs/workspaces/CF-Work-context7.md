# CF-Work Workspace (context7)

This workspace is tailored for CF-Work development with an emphasis on:

- Direct Python invocation using the repo-managed virtual environment at `.venv/`
- MCP servers configured via `.vscode/mcp.json`
- Quality grounding through test artifacts under `build/artifacts/tests/python/`

## What is Context7?

Context7 is an Upstash project and Model Context Protocol (MCP) server that provides up‑to‑date, version‑specific documentation and code examples for libraries so AI code editors and LLMs can pull accurate snippets at prompt time.

Authoritative references:

- Site: https://context7.com/
- GitHub: https://github.com/upstash/context7
- Intro blog: https://upstash.com/blog/context7-llmtxt-cursor
- VS Code extension: https://marketplace.visualstudio.com/items?itemName=Upstash.context7-mcp

Key idea: instead of relying on a model’s stale training data, Context7 fetches current docs/code directly from the source and injects them into your prompt via MCP integrations (Cursor, Claude Code, Roo Code, Windsurf, etc.).

### Optional integration (VS Code / MCP)

- If your MCP client supports remote servers, you can configure Context7’s MCP endpoint (commonly `https://mcp.context7.com/mcp`) in your MCP configuration (for this repo, see `.vscode/mcp.json`).
- Alternatively, install the "Context7 MCP Server" extension from the Marketplace and follow its instructions.

Note: Context7 is external to this repository; our workspace remains compatible whether or not you enable it.

## Quick Starts

- Python tests (quick): use the VS Code task "PyTest: Quick" or run the runner under `python/tools`.
- Tracker authority: `dbcli.py status migration --json` (always run via `.venv` Python).

## Pointers

- Workspace file: `config/CF-Work.code-workspace`
- MCP configuration: `.vscode/mcp.json`
- Latest pytest pointer: `build/artifacts/tests/python/UNIFIED_POINTER.txt`
- Last successful runs: `build/artifacts/tests/python/success-runs.json`

## Host Policy

New scripts should declare a HostPolicy header when applicable and target PowerShell 7 or Python helpers per repository standards.

## Logging baseline checklist (UnifiedLogger)

Use this checklist to verify the required baseline events are present and the gate test remains green across runs:

- Required early-phase events (observed during test execution):
  - session_start
  - artifact_touch_batch
  - task_start / task_end
  - decision
- Required finals (emitted at process exit via atexit):
  - session_end
  - session_summary
- Path policy:
  - Default is repo-local under `logs/`; external PowerShell-only utilities may write to `C:\Temp` per exception policy.
- Redaction:
  - Configure token redaction with `UNIFIED_LOG_REDACT`
  - Configure regex redaction with `UNIFIED_LOG_REDACT_REGEX` (comma/semicolon separated patterns)
- Environment flags of interest:
  - `UNIFIED_LOG_PATH`, `UNIFIED_LOG_LEVEL`, `UNIFIED_LOG_DUAL_WRITE`, `UNIFIED_LOG_EVIDENCE_AUTO`, `UNIFIED_LOG_ROTATE_MAX_MB`, `UNIFIED_LOG_ROTATE_MAX_AGE_SEC`, `UNIFIED_LOG_ROTATE_BACKUPS`, `UNIFIED_LOG_OTEL`

### Quick verify

- VS Code task: "PyTest: Logging Gate only" — validates early baseline and absence of `logging_gap_detected`.
- Lifecycle: "PyTest: Verbose" or the targeted dbcli lifecycle tests ensure `session_end` and `session_summary` exist post-session.

Troubleshooting:

- If running only the gate test, finals may not yet exist at assertion time; the gate safely synthesizes finals when appropriate to avoid order-induced false negatives.
- On Windows, ensure paths are quoted correctly when invoking CLI wrappers; prefer `.venv\\Scripts\\python.exe -m pytest` via tasks.
