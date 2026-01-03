# Python MCP Server Research Report

**Research Date**: 2025-11-25
**Agent**: Python MCP Server Research Agent
**Status**: ✅ COMPLETE

---

## Executive Summary

This research provides a comprehensive analysis of existing MCP implementations in the workspace and recommends an architecture for the Python MCP server that will achieve feature parity with the TypeScript implementation.

**Key Findings:**
1. TypeScript MCP server (`mcp-server-ts`) is production-ready with 37 tools across 3 domains
2. Python scaffold (`mcp-server-py`) exists with detailed README roadmap
3. Prior research in `PHASE3-MCP-PYTHON-RESEARCH-FINDINGS.md` recommends FastMCP + Typer pattern
4. Existing Python infrastructure (unified_logger, mcp_stdio_harness) is reusable
5. MCP configurations exist in `.vscode/mcp.json` and `.mcp.json`

---

## 1. Inventory of Existing MCP Implementations

### 1.1 TypeScript MCP Server (`TaskMan-v2/mcp-server-ts/`)

**Status**: Production-Ready
**Transport**: STDIO (primary), HTTP (optional)
**Version**: 0.1.0

**Key Infrastructure:**
- OpenTelemetry distributed tracing (Phase 2)
- Prometheus metrics
- Pino structured logging
- Circuit breaker-protected backend client
- Resource locking service
- Session management with cleanup
- Health check endpoints

**Directory Structure:**
```
mcp-server-ts/
├── src/
│   ├── index.ts                    # Main entry point
│   ├── instrumentation.ts          # OpenTelemetry setup
│   ├── config/                     # Configuration management
│   ├── core/                       # Types and schemas (Zod)
│   ├── backend/                    # Backend API client
│   ├── infrastructure/             # Logger, cache, metrics, audit
│   ├── transports/                 # STDIO/HTTP transports
│   ├── features/
│   │   ├── tasks/                  # Task tools (11 tools)
│   │   ├── projects/               # Project tools (13 tools)
│   │   └── action-lists/           # Action list tools (13 tools)
│   └── services/                   # Business logic
├── tests/                          # Vitest tests
└── package.json                    # Dependencies
```

### 1.2 Python MCP Server Scaffold (`TaskMan-v2/mcp-server-py/`)

**Status**: Planned (README + pyproject.toml template only)
**Files Present:**
- `README.md` - Comprehensive roadmap (458 lines)
- `pyproject.toml.template` - Dependency template

### 1.3 MCP Configuration Files

| File | Purpose | Client |
|------|---------|--------|
| `.vscode/mcp.json` | VS Code Copilot MCP servers | VS Code |
| `.mcp.json` | Root workspace config | Claude Code |
| `.mcp/postgres-server.json` | PostgreSQL MCP config | Claude Code |
| `.mcp/github-server.json` | GitHub MCP config | Claude Code |

### 1.4 Other MCP-Related Components

| Component | Location | Purpose |
|-----------|----------|---------|
| MCP STDIO Harness | `python/src/mcp_stdio_harness/` | Testing harness for MCP servers |
| MCP Bridge (JS) | `vs-code-task-manager/mcp-*-bridge.js` | CF_CLI bridge components |
| MCP Mocks | `test-infrastructure/mcp-mocks/` | Testing mock server |
| MCP Documentation | `docs/mcp/INDEX.md` | Central MCP documentation |

---

## 2. TypeScript MCP Server Tool List (For Parity)

### 2.1 Task Tools (11 tools)

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `task_create` | Create a new task record | `task` (TaskSchema) |
| `task_read` | Retrieve a task by ID | `taskId` |
| `task_update` | Update an existing task | `taskId`, `changes` |
| `task_set_status` | Update task status | `taskId`, `status`, `notes?`, `completion_notes?` |
| `task_assign` | Assign/reassign task | `taskId`, `assignee?`, `assignees?` |
| `task_delete` | Delete a task | `taskId` |
| `task_list` | List tasks with filters | `status?`, `work_type?`, `priority?`, `owner?`, `assignee?`, `project_id?`, `sprint_id?`, `search?`, `tags?`, `limit?`, `cursor?` |
| `task_bulk_update` | Bulk update tasks | `taskIds`, `changes` |
| `task_bulk_assign_sprint` | Bulk assign to sprint | `taskIds`, `sprintId` |
| `task_search` | Search tasks | `query`, `fields?`, `project_id?`, `sprint_id?`, `skip?`, `limit?` |

### 2.2 Project Tools (13 tools)

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `project_create` | Create new project | `project` (ProjectSchema) |
| `project_read` | Get project by ID | `projectId` |
| `project_update` | Update project | `projectId`, `changes` |
| `project_delete` | Delete project | `projectId` |
| `project_list` | List projects | `status?`, `search?`, `limit?`, `cursor?` |
| `project_add_sprint` | Add sprint to project | `projectId`, `sprintId` |
| `project_remove_sprint` | Remove sprint | `projectId`, `sprintId` |
| `project_add_meta_task` | Add meta task | `projectId`, `metaTask` |
| `project_add_comment` | Add comment | `projectId`, `comment` |
| `project_add_blocker` | Add blocker | `projectId`, `blocker` |
| `project_get_comments` | List comments | `projectId`, `params?` |
| `project_get_metrics` | Get project metrics | `projectId` |

### 2.3 Action List Tools (13 tools)

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `action_list_create` | Create action list | `ActionListSchema` |
| `action_list_read` | Get action list | `action_list_id` |
| `action_list_list` | List action lists | `status?`, `priority?`, `owner?`, `project_id?`, `sprint_id?`, `tags?`, `limit?`, `cursor?` |
| `action_list_update` | Update action list | `action_list_id`, `changes` |
| `action_list_delete` | Delete action list | `action_list_id` |
| `action_list_add_item` | Add item | `action_list_id`, `text`, `order?` |
| `action_list_toggle_item` | Toggle item completion | `action_list_id`, `item_id` |
| `action_list_remove_item` | Remove item | `action_list_id`, `item_id` |
| `action_list_reorder_items` | Reorder items | `action_list_id`, `item_ids` |
| `action_list_bulk_delete` | Bulk delete | `action_list_ids` |
| `action_list_bulk_update` | Bulk update | `action_list_ids`, `updates` |
| `action_list_search` | Search action lists | `q`, `fields?`, `project_id?`, `status?`, `priority?`, `skip?`, `limit?` |

**Total Tools**: 37 (11 task + 13 project + 13 action-list)

---

## 3. Python MCP Implementation Patterns Found

### 3.1 MCP SDK Usage (from `claudekit-skills/.claude/skills/mcp-builder/`)

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client

class MCPConnectionStdio(MCPConnection):
    """MCP connection using standard input/output."""

    def __init__(self, command: str, args: list[str] = None, env: dict[str, str] = None):
        self.command = command
        self.args = args or []
        self.env = env

    def _create_context(self):
        return stdio_client(
            StdioServerParameters(command=self.command, args=self.args, env=self.env)
        )
```

### 3.2 STDIO Harness Pattern (from `python/src/mcp_stdio_harness/`)

Key features:
- JSON-RPC over STDIO
- Multi-framing support (CRLF, LF, Content-Type, bare JSON)
- Layered timeouts (overall / per-call / idle)
- SHA-256 evidence digests
- Structured JSONL logging

### 3.3 Prior Research Recommendation (from `PHASE3-MCP-PYTHON-RESEARCH-FINDINGS.md`)

**Recommended Pattern**: FastMCP with Typer CLI

```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

mcp = FastMCP("TaskMan-v2")

@mcp.tool()
def list_tasks(status: str | None = None) -> dict:
    """List all tasks with optional status filter"""
    return {"implemented": False, "milestone": "core_parity_phase"}
```

---

## 4. Existing Python Services for Reuse

### 4.1 Unified Logger (`python/unified_logger.py`)

**Features:**
- Session-based logging with unique IDs
- Correlation ID tracking
- JSONL output format
- PowerShell plugin coordination
- Enhanced terminal console integration
- Achievement/milestone tracking
- COF 13D + UCL compliance validation

**Reuse Pattern:**
```python
from python.unified_logger import UnifiedLogger

logger = UnifiedLogger(
    session_id="mcp_session_001",
    enable_achievement_tracking=True,
    constitutional_compliance=True
)
```

### 4.2 CF_CLI Patterns (`python/cf_cli/`)

- Custom help system with Rich formatting
- Clean module organization
- Integration-ready structure

### 4.3 MCP STDIO Harness (`python/src/mcp_stdio_harness/`)

**Files:**
- `harness.py` - Core STDIO harness implementation
- `cli.py` - CLI interface
- `__init__.py` - Module exports

**Key Patterns:**
- Async subprocess management
- JSON-RPC message framing
- Evidence artifact generation (Markdown + JSONL)
- Per-message SHA-256 digests

---

## 5. Recommended Python MCP Server Architecture

### 5.1 Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **MCP Framework** | FastMCP (`mcp.server.fastmcp`) | Decorator-based, automatic schema generation |
| **CLI** | Typer | Clean command interface, consistent with patterns |
| **Validation** | Pydantic 2.x | Type safety, automatic JSON schema |
| **Logging** | structlog + UnifiedLogger | Integration with workspace logging |
| **Transport** | STDIO (primary), HTTP (future) | MCP protocol standard |
| **Database** | SQLAlchemy 2.0 async | Shared PostgreSQL with TS server |

### 5.2 Directory Structure

```
TaskMan-v2/mcp-server-py/
├── pyproject.toml                # Dependencies, scripts, tool config
├── README.md                     # Documentation (existing)
├── src/
│   └── taskman_mcp/
│       ├── __init__.py           # __version__, exports
│       ├── __main__.py           # Entry point
│       ├── server.py             # FastMCP + Typer CLI (~150 LOC)
│       ├── config.py             # Pydantic Settings
│       ├── logging.py            # structlog + UnifiedLogger bridge (~80 LOC)
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── tasks.py          # Task Pydantic models
│       │   ├── projects.py       # Project Pydantic models
│       │   └── action_lists.py   # ActionList Pydantic models
│       ├── tools/
│       │   ├── __init__.py       # register_all_tools()
│       │   ├── tasks.py          # 11 task tools (~200 LOC)
│       │   ├── projects.py       # 13 project tools (~250 LOC)
│       │   └── action_lists.py   # 13 action-list tools (~250 LOC)
│       ├── backend/
│       │   ├── __init__.py
│       │   └── client.py         # Backend API client (async httpx)
│       └── infrastructure/
│           ├── audit.py          # Audit logging
│           └── locking.py        # Resource locking
├── tests/
│   └── mcp/
│       ├── conftest.py           # Shared fixtures
│       ├── test_tool_registry.py # Tool enumeration tests
│       ├── test_schemas.py       # Pydantic model tests
│       └── test_stdio.py         # STDIO transport tests
└── scripts/
    └── smoke_test.py             # Quick validation script
```

### 5.3 Implementation Phases

#### Phase 3A: Scaffold (Current Priority)
1. `pyproject.toml` with dependencies
2. `server.py` with FastMCP + Typer CLI
3. Stub tools returning `NotImplemented` responses
4. Basic test suite (tool registry, schema validation)

**Target**: ~600 LOC, 37 stub tools

#### Phase 3B: Logging Integration
1. structlog configuration
2. UnifiedLogger bridge
3. Session-level logging
4. Tool invocation logging

**Target**: ~100 additional LOC

#### Phase 4: Core Parity
1. Backend API client
2. Database integration (SQLAlchemy)
3. Full tool implementations
4. Integration tests

**Target**: ~1500 additional LOC

### 5.4 Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Parity Target** | 37 tools (100% TypeScript parity) | Feature completeness |
| **Transport Priority** | STDIO first, HTTP later | Simpler, matches VS Code pattern |
| **Stub Pattern** | `NotImplementedResponse` model | Clear milestone tracking |
| **Async/Sync** | Async throughout | Backend API, database compatibility |
| **Logging** | Structured JSONL | Matches workspace standards |

---

## 6. Dependencies (pyproject.toml)

```toml
[project]
name = "taskman-mcp-server"
version = "0.1.0"
description = "TaskMan-v2 MCP Server - Python Implementation"
requires-python = ">=3.11"
dependencies = [
    "mcp[cli]>=0.9.0",           # MCP SDK with CLI
    "typer[all]>=0.12.0",        # CLI framework
    "pydantic>=2.8.0",           # Validation
    "pydantic-settings>=2.0.0",  # Config management
    "structlog>=24.1.0",         # Structured logging
    "httpx>=0.27.0",             # Async HTTP client
    "sqlalchemy[asyncio]>=2.0.0",# Database ORM
    "asyncpg>=0.29.0",           # PostgreSQL async driver
    "python-dotenv>=1.0.0",      # Environment config
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.5.0",
    "mypy>=1.10.0",
]

[project.scripts]
taskman-mcp = "taskman_mcp.server:app"
```

---

## 7. Quality Gates

| Gate | Requirement | Tool |
|------|-------------|------|
| Linting | Clean | `ruff check` |
| Type Check | Strict mode | `mypy --strict` |
| Test Coverage | ≥70% | `pytest --cov` |
| Tool Parity | 37 tools registered | Smoke test |
| STDIO Transport | Functional | Integration test |

---

## 8. References

### Source Files Analyzed
- `TaskMan-v2/mcp-server-ts/src/features/tasks/register.ts`
- `TaskMan-v2/mcp-server-ts/src/features/projects/register.ts`
- `TaskMan-v2/mcp-server-ts/src/features/action-lists/register.ts`
- `TaskMan-v2/PHASE3-MCP-PYTHON-RESEARCH-FINDINGS.md`
- `python/unified_logger.py`
- `python/src/mcp_stdio_harness/harness.py`
- `claudekit-skills/.claude/skills/mcp-builder/scripts/connections.py`

### External References
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk/blob/main/README.md)
- [VS Code MCP Integration](https://code.visualstudio.com/api/extension-guides/ai/mcp)

---

## 9. Next Steps

1. **Create branch**: `feature/phase3-mcp-python-scaffold`
2. **Implement Phase 3A** (scaffold with stub tools)
3. **Validate tool parity** (37 tools registered)
4. **Add CI workflow** (lint, type-check, test)
5. **Generate AAR** documenting completion

---

**Research Status**: ✅ COMPLETE
**Recommended Action**: Proceed with Phase 3A scaffold implementation
**Estimated Effort**: 2-3 days for Phase 3A scaffold
