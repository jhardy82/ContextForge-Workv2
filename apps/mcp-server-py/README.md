# TaskMan-v2 Python MCP Server

## Status: ✅ Active (Feature Complete)

This is the Python implementation of the TaskMan-v2 MCP (Model Context Protocol) server. It provides a comprehensive suite of tools for managing tasks, projects, sprints, and context within the ContextForge ecosystem.

## Architecture

*   **Stack**: Async-First Python 3.12+
*   **Framework**: FastAPI (via `mcp` library)
*   **Data Access**: SQLAlchemy 2.0 (AsyncIO) + AsyncPG
*   **Database**: PostgreSQL (Development in WSL)
*   **Package Management**: `uv`

## Features

### 1. Task Management
*   `create_task`: Create tasks with detailed metadata (title, status, priority, etc.).
*   `list_tasks`: Filter tasks by status, priority, project, sprint, or context.
*   `get_task`: Retrieve full task details including 40+ dimensions.
*   `update_task`: Modify task attributes.
*   `delete_task`: Remove tasks.

### 2. Project Management
*   `create_project`: Define new projects with lifecycle states.
*   `list_projects`: View all projects or filter by status.
*   `get_project`: Retrieve project details.
*   `update_project`: Modify project settings.

### 3. Sprint Management
*   `create_sprint`: Define sprints with start/end dates and goals.
*   `list_sprints`: View sprints by project or status.
*   `get_sprint`: Retrieve sprint metrics and status.
*   `update_sprint`: Update sprint progress.

### 4. Context Management
*   `create_context`: Create context nodes (domains, entities) with 11-dimensional attributes.
*   `list_contexts`: Search context hierarchies.
*   `get_context`: Retrieve context definitions.

## Setup & installation

### Prerequisites
*   Windows 10/11 with WSL 2 (Ubuntu recommended)
*   Python 3.12+ (installed in WSL)
*   `uv` package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
*   PostgreSQL running (docker or local in WSL)

### Installation (WSL)

```bash
# 1. Clone the repository (if not already done)
git clone <repo-url>
cd TaskMan-v2/mcp-server-py

# 2. Configure Environment
cp .env.example .env
# Edit .env to match your PostgreSQL credentials (e.g., localhost if running locally)

# 3. Install Dependencies
uv sync
```

### Running the Server

```bash
# Activate changes and run
export PYTHONPATH=src
uv run python -m cf_mcp.server
```

## Usage with Claude Desktop (Windows)

Since the server runs in WSL but Claude Desktop runs on Windows, you must configure a bridge.

1.  Open `%APPDATA%\Claude\claude_desktop_config.json`.
2.  Add the following server configuration:

```json
{
  "mcpServers": {
    "TaskMan-Python": {
      "command": "wsl.exe",
      "args": [
        "-d",
        "Ubuntu-24.04",
        "bash",
        "-c",
        "cd /mnt/c/Users/James/Documents/Github/GHrepos/SCCMScripts/TaskMan-v2/mcp-server-py && export UV_LINK_MODE=copy && export PYTHONPATH=src && uv run python -m cf_mcp.server"
      ]
    }
  }
}
```

> **Note**: Replace `/mnt/c/Users/...` with the actual path to your project if different. Ensure `Ubuntu-24.04` matches your default WSL distribution (`wsl --list`).

## Testing

Run the integration test suite to verify functionality:

```bash
uv run python -m pytest tests/ -v
```
