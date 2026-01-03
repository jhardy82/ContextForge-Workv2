# CF-Work Memory Graph (MCP v1)

Purpose: Provide an MCP-compliant memory graph of ContextForge Work principles mapped to concrete workspace mechanisms (modules, scripts, artifacts) for discoverability and governance alignment.

Key file: `memory_graph.json` (schema: https://modelcontextprotocol.io/memory/graph/v1)
Helper: `scripts/memory_mcp.ps1`

Usage

- List nodes (JSON): `./scripts/memory_mcp.ps1 -View nodes -Json`
- Search: `./scripts/memory_mcp.ps1 -View nodes -Search cf-work -Json`
- Get by Id: `./scripts/memory_mcp.ps1 -Id cfw:LogsFirst -Json`
- Export: `./scripts/memory_mcp.ps1 -View edges -Json -Export build/artifacts/memory_edges.json`

Notable links wired

- LogsFirst → artifacts: `build/artifacts/logs/`, `build/artifacts/logging/`, `Quality-Audit.jsonl`, `logging_console.txt`
- QualityGates → artifacts: `Pester-Results-NUnit.xml`, `Quality-Summary.json`, `pytest_raw.txt`, `junit-pytests.xml`
- PythonEnvPolicy → artifacts: `env/env_info.txt`, `env/env.validation.json`
- DBAuthority → artifacts: `trackers/DB_AUTHORITY.SENTINEL`, `build/artifacts/dbcli_status_migration.json`
- TrackerFramework → artifacts: `build/artifacts/inventory.latest.json`

Notes

- Python harness latest-run markers were not present; `pytest_raw.txt` and `junit-pytests.xml` exist and serve as evidence for runs.
- DB Authority is confirmed via `build/artifacts/dbcli_status_migration.json` (ok=true) and the sentinel file.
- Keep `generated_at` current when editing the graph.

## Last-Run vs Last-Success Pointers

- `build/artifacts/tests/python/latest-run.txt` and `UNIFIED_POINTER.txt` record the most recent run (may include timeouts or failures).
- `build/artifacts/tests/python/LAST_SUCCESS.txt` records the most recent successful pytest run (rc=0).
- The memory graph node `evidence:pytest:last_success` links to the last-success artifacts to stabilize governance evidence.
- When new successful runs occur, update `LAST_SUCCESS.txt` and refresh the evidence node metadata.

## MCP servers wiring

Your `.vscode/mcp.json` is mirrored in the memory graph as tool nodes to support MCP‑first operations:

- `tool:MCP:Docs` → microsoft.docs.mcp (HTTP) — enriches `cfw:Evidence` with Learn references
- `tool:MCP:DuckDB` → DuckDB (stdio via `uvx mcp-server-duckdb`) — supports `cfw:TrackerFramework`
- `tool:MCP:Memory` → server-memory (npx stdio) — supports `cfw:LogsFirst` and graph updates
- `tool:MCP:SeqThinking` → server-sequential-thinking (npx stdio) — plans_with `cfw:TaskBurstHierarchy`
- `tool:MCP:DeepWiki` → DeepWiki (HTTP SSE) — enriches `cfw:Fractal`
- `tool:MCP:Interactive` → http://localhost:8090/mcp — integrates with `cfw:Circle`

Use `scripts/memory_mcp.ps1` to query these tool nodes and their edges:

- `./scripts/memory_mcp.ps1 -View nodes -Search MCP -Json`
- `./scripts/memory_mcp.ps1 -Id tool:MCP:Memory -Json`

Try it

- Run a tiny smoke to create latest-run markers and a run directory:
  - PowerShell task: "Py: Smoke (fixed)" from VS Code tasks
  - Or terminal:
    - `& .\.venv\Scripts\python.exe .\python\run_tests.py -t tests\python\test_heartbeat_summary.py --heartbeat-interval 1.0`
- Then inspect artifacts:
  - `Get-Content .\build\artifacts\tests\python\latest-run.txt`
  - `Get-Content .\build\artifacts\tests\python\latest-runs.json | Select-Object -First 100`
  - `Get-ChildItem .\build\artifacts\tests\python\$(Get-Content .\build\artifacts\tests\python\latest-run.txt)`

## Query the memory graph

Use `scripts/Query-MemoryGraph.ps1` to filter nodes and flatten linked artifacts/scripts/modules.

Examples (PowerShell 7):

- By labels (links only, JSON): `./scripts/Query-MemoryGraph.ps1 -Labels QualityGates -TraverseDepth 0 -LinksOnly -Output json`
- By tags: `./scripts/Query-MemoryGraph.ps1 -Tags cf-work -Output json`
- By id: `./scripts/Query-MemoryGraph.ps1 -Id cfw:QualityGates -Output json`
- Include neighbors (depth 1): `./scripts/Query-MemoryGraph.ps1 -Labels LogsFirst -TraverseDepth 1 -Output json`

Notes

- Graph path defaults to `./memory_graph.json` (override with `-GraphPath`).
- A JSONL query log is written to `./logs/cli/Query-MemoryGraph.log.jsonl`.
