# cf_core/mcp - MCP Server Implementation

Model Context Protocol (MCP) server for TaskMan integration with AI agents.

## Overview

This module provides an MCP server that exposes TaskMan operations as tools callable by AI agents. It implements the [MCP specification](https://modelcontextprotocol.io/) for tool-based interactions.

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Module exports |
| `taskman_server.py` | Main MCP server implementation with tool handlers |
| `schemas.py` | Pydantic schemas for MCP tool inputs/outputs |

## Transport Options

The MCP server supports multiple transport mechanisms:

- **STDIO** (preferred): Direct stdio communication in VS Code
- **HTTP**: REST-like interface for remote clients

## Tool Categories

### Task Operations
- `create_task` - Create a new task
- `get_task` - Retrieve task by ID
- `update_task` - Update task fields
- `delete_task` - Delete a task
- `list_tasks` - List tasks with filters
- `complete_task` - Mark task as done

### Sprint Operations
- `create_sprint` - Create a new sprint
- `get_sprint` - Retrieve sprint by ID
- `update_sprint` - Update sprint fields
- `list_sprints` - List sprints with filters

### Project Operations
- `create_project` - Create a new project
- `get_project` - Retrieve project by ID

## Usage

```python
from cf_core.mcp.taskman_server import create_mcp_server

# Create server instance
server = create_mcp_server()

# Run with STDIO transport
server.run_stdio()
```

## Testing

```bash
# Run MCP-specific tests
pytest tests/cf_core/mcp/ -v

# Run E2E workflow tests
pytest tests/cf_core/mcp/e2e/ -v
```

## Related Documentation

- [Main cf_core README](../README.md)
- [MCP Specification](https://modelcontextprotocol.io/)
