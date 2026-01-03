# SCCMScripts Workspace Index

Quick reference for developers and AI agents navigating the ContextForge workspace.

---

## Entry Points

| Component | Path | How to Run |
|-----------|------|------------|
| **CF CLI** | `cf_core/cli/main.py` | `python -m cf_core.cli.main` or `cf` alias |
| **TaskMan-v2 API** | `TaskMan-v2/backend-api/main.py` | `uvicorn main:app --port 8002` |
| **TaskMan MCP (TS)** | `TaskMan-v2/mcp-server-ts/` | `npm start` (STDIO server) |
| **TaskMan MCP (Py)** | `TaskMan-v2/mcp-server-py/` | Template only |

---

## Key Directories

### Core Application

| Directory | Purpose |
|-----------|---------|
| `cf_core/` | Main Python package - CLI, services, domain logic |
| `cf_core/cli/` | Command-line interface modules |
| `cf_core/services/` | Business logic and service layer |
| `cf_core/repositories/` | Data access layer |
| `cf_core/mcp/` | MCP integration components |

### TaskMan-v2 (Task Management)

| Directory | Purpose |
|-----------|---------|
| `TaskMan-v2/backend-api/` | FastAPI backend (port 8002) |
| `TaskMan-v2/mcp-server-ts/` | TypeScript MCP server (primary) |
| `TaskMan-v2/src/` | React frontend |
| `TaskMan-v2/shared/` | Shared types/schemas |

### Scripts & Automation

| Directory | Purpose |
|-----------|---------|
| `scripts/` | PowerShell/Python automation scripts |
| `scripts/Invoke-TaskManStack.ps1` | Stack orchestration (start/stop/health) |
| `scripts/Invoke-CFTerminalFrame.ps1` | Terminal observability wrapper |

---

## Databases

### PostgreSQL (Production)

| Database | Connection | Purpose | Access Guide |
|----------|------------|---------|-------------|
| **taskman_v2** | localhost:5434 (PostgreSQL 16) | Primary TaskMan database | [Quick Ref](DATABASE-QUICK-REFERENCE.md) |
| **contextforge** | localhost:5433 (PostGIS 15) | ContextForge project database | [Quick Ref](DATABASE-QUICK-REFERENCE.md) |
| **context_forge** | localhost:5432 (PostgreSQL 15) | Sacred Geometry database | [Quick Ref](DATABASE-QUICK-REFERENCE.md) |

**Credentials**: `contextforge/contextforge` (dev default, override via environment variables)

### Legacy Databases

| Database | Path | Purpose |
|----------|------|------|
| **Velocity Metrics** | `db/velocity.duckdb` | DuckDB analytics/velocity tracking |
| **TaskMan** | `db/taskman.db` | SQLite task storage (legacy) |
| **Orchestration** | `db/orch.sqlite` | Orchestration state |
| **Trackers** | `db/trackers.sqlite` | Tracker metadata |

### Database Access Tools

| Script | Purpose | Features |
|--------|---------|----------|
| `scripts/db_auth.py` | Python credential helper | Environment variable support, 168ms P95 latency |
| `scripts/Get-DatabaseCredentials.ps1` | PowerShell credential helper | Cross-platform, env var support |
| `scripts/Benchmark-DatabaseAccess.ps1` | Performance benchmarking | Statistical analysis, multiple query types |

**Complete Guide**: [docs/AGENT-DATABASE-ACCESS.md](AGENT-DATABASE-ACCESS.md) (500+ lines)
**Quick Start**: [docs/DATABASE-QUICK-REFERENCE.md](DATABASE-QUICK-REFERENCE.md) (30-second access)
**Examples**: [docs/DATABASE-EXAMPLE-QUERIES.md](DATABASE-EXAMPLE-QUERIES.md) (30+ tested queries)

---

## Configuration Files

### Python

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project metadata, dependencies, tool config |
| `.python-version` | Python version constraint |
| `uv.toml` | uv package manager settings |
| `uv.lock` | Locked dependencies |
| `.ruff.toml` | Ruff linter configuration |
| `mypy.ini` | Type checking configuration |

### Environment

| File | Purpose |
|------|---------|
| `.env` | Active environment variables |
| `.env.example` | Template for new setups |
| `.env.contextforge` | ContextForge-specific settings |
| `.env.mcp.template` | MCP server configuration template |

### VS Code

| File | Purpose |
|------|---------|
| `.vscode/tasks.json` | Build/run/test tasks |
| `.vscode/launch.json` | Debug configurations |
| `.vscode/settings.json` | Workspace settings |

---

## MCP Servers

| Server | Location | Transport |
|--------|----------|-----------|
| TaskMan-v2 TS | `TaskMan-v2/mcp-server-ts/` | STDIO |
| GitHub | `.mcp/github-server.json` | Config |
| PostgreSQL | `.mcp/postgres-server.json` | Config |
| Alt Servers | `mcp-alt-servers/servers/` | Various |

**MCP Config**: `.mcp.json` (workspace root)

---

## Documentation

| Path | Content |
|------|---------|
| `docs/` | All project documentation |
| `docs/adr/` | Architecture Decision Records |
| `docs/api/` | API documentation |
| `docs/guides/` | User guides |
| `docs/guides/AGENT-ONBOARDING.md` | **NEW** Agent Setup & MCP Guide |
| `.github/copilot-instructions.md` | AI agent instructions |
| `.github/instructions/` | Domain-specific guidance |

---

## Testing

| Command | Purpose |
|---------|---------|
| `pytest` | Run Python tests |
| `pytest --cov` | Run with coverage |
| `ruff check .` | Lint Python code |
| `mypy .` | Type checking |

**Test Directories**: `tests/`, `cf_core/*/tests/`, `TaskMan-v2/tests/`

---

## VS Code Tasks (Quick Actions)

| Task | Description |
|------|-------------|
| `Stack: Start` | Start full development stack |
| `Stack: Fast Start` | Start stack (skip slow checks) |
| `Stack: Stop` | Stop all services |
| `Health: One-Off` | Run health check |
| `Python: Pytest` | Run Python tests |
| `Python: Ruff` | Run linter |

Run via: `Ctrl+Shift+P` → "Tasks: Run Task"

---

## Quick Commands

```powershell
# Activate Python environment
.\.venv\Scripts\Activate.ps1

# Run CF CLI
python -m cf_core.cli.main --help

# Start TaskMan-v2 stack
.\scripts\Invoke-TaskManStack.ps1 -Action Start

# Run tests
pytest -rA

# Check linting
ruff check .
```

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `cf_cli.py` | CLI entry shim |
| `conftest.py` | Pytest fixtures (root) |
| `CLAUDE.md` | Claude-specific instructions |
| `AGENTS.md` | Multi-agent coordination |
| `README.md` | Project overview |
| `CHANGELOG.md` | Version history |

---

*Last updated: 2025-12-25*
