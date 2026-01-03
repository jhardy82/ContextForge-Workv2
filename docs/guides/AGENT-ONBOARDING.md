# AI Agent Onboarding & MCP Setup Guide

**Version**: 1.0 (2025-12-29)
**Scope**: Antigravity, Claude Desktop, and other MCP Clients
**Prerequisites**: Windows OS, PowerShell 7+, Git

## 🚀 Quick Start (Zero to Hero)

If you are a new AI agent or developer joining this workspace, follow these steps to bootstrap your environment with full tool capabilities.

### 1. Environment Configuration

The workspace uses a central `.env` file to manage secrets for all MCP servers.

1.  **Copy Template**:
    ```powershell
    Copy-Item .env.example .env
    ```
2.  **Populate Secrets**:
    Open `.env` and fill in the following critical values:
    *   `GITHUB_TOKEN`: Your personal access token (repo, workflow, user scopes).
    *   `MCP_DATABASE_SECRET_KEY`: Random string for database security (if applicable).
    *   `BRAVE_API_KEY`: (Optional) For Brave Search integration.

> **⚠️ Security Warning**: Never commit `.env` to version control. It is gitignored by default.

### 2. Synchronize MCP Settings

We use a unified script to configure MCP servers across all installed clients (Antigravity/VS Code and Claude Desktop).

```powershell
./scripts/Sync-McpSettings.ps1
```

**What this does**:
*   Reads server definitions from `config/MCP-SERVERS.md`.
*   Injects absolute paths and variables from `.env`.
*   Updates:
    *   `%APPDATA%\Claude\claude_desktop_config.json`
    *   `.vscode/settings.json` (Workspace level)

### 3. Verify Connectivity (Heartbeat)

Before attempting complex tasks, run the heartbeat check to ensure all servers are responsive.

```powershell
./scripts/Test-McpHeartbeat.ps1
```

**Expected Output**:
*   ✅ `taskman-v2` - OK
*   ✅ `github` - OK
*   ✅ `command-access` - OK
*   (and so on for all 12 servers)

### 4. Validation (Smoketest)

If you need to verify deep functionality (e.g. database writing, GitHub API calls), follow the [Playbook-MCP-Validation.md](../.gemini/antigravity/brain/bf9ab81a-6b87-48c9-8707-d9de13935435/Playbook-MCP-Validation.md).

---

## �️ Database Access

All agents have **direct database access** for maximum performance and simplicity.

### Quick Access

**30-Second Start**: [../DATABASE-QUICK-REFERENCE.md](../DATABASE-QUICK-REFERENCE.md)

**Databases**:
- **taskman_v2** - localhost:5434 (Primary TaskMan database)
- **contextforge** - localhost:5433 (ContextForge project)
- **context_forge** - localhost:5432 (Sacred Geometry)

**Credentials**: `contextforge/contextforge` (dev)

### Access Methods

1. **Python psycopg2** (168ms P95) - Recommended for automation
   ```python
   from scripts.db_auth import get_db_credentials
   conn = get_db_credentials(format='connection')
   ```

2. **Docker exec** (223ms P95) - Recommended for debugging
   ```bash
   docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "SELECT COUNT(*) FROM tasks;"
   ```

3. **PowerShell** - Cross-platform wrapper
   ```powershell
   . scripts/Get-DatabaseCredentials.ps1
   # Returns connection objects for all 3 databases
   ```

### Documentation

- **Examples**: [../DATABASE-EXAMPLE-QUERIES.md](../DATABASE-EXAMPLE-QUERIES.md) (30+ tested queries)
- **Troubleshooting**: [../DATABASE-TROUBLESHOOTING-FLOWCHART.md](../DATABASE-TROUBLESHOOTING-FLOWCHART.md)
- **Comprehensive Guide**: [../AGENT-DATABASE-ACCESS.md](../AGENT-DATABASE-ACCESS.md) (500+ lines)
- **Auto-activation**: Instructions load automatically on `database*`, `db*`, `postgres*`, `sql*` keywords

**Performance**: Direct access is 30% faster than MCP with zero configuration complexity.

---

## �🛠️ MCP Tool Reference

**Authoritative Source**: [config/MCP-SERVERS.md](../../config/MCP-SERVERS.md)

| Server | Key Tools |
|--------|-----------|
| **TaskMan-v2** | `task_create`, `task_list`, `task_update` (Project management) |
| **GitHub** | `github_create_issue`, `github_get_file_contents` |
| **Filesystem** | `read_file`, `write_file`, `list_directory` (Restricted scope) |
| **Database** | `query` (Read/Write access to project DBs) |
| **Memory** | `create_entity`, `create_relation` (Knowledge graph) |

---

## ⚠️ Troubleshooting

**"Tool not found" in Client**:
1.  Run `./scripts/Sync-McpSettings.ps1` again.
2.  Restart the Client (Antigravity or Claude Desktop).
3.  Check `logs/mcp-sync.log` for errors.

**"Environment variable not found"**:
*   Ensure the variable is defined in your root `.env` file.
*   Claude Desktop does NOT inherit system environment variables easily; `Sync-McpSettings.ps1` handles injection explicitly.

**"Access Denied" on Files**:
*   The `Filesystem` MCP server is restricted to the workspace root. Do not attempt to access files outside this directory.
