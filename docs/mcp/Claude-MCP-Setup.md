## Claude Code Vibe Check MCP Setup

This guide enables the Vibe Check MCP server for Claude Code alongside existing VS Code integration.

### 1. Prerequisites
- Node.js 20+ with `npx` available in PATH.
- Workspace already contains `.vscode/mcp.json` with the `vibe-check-mcp` server.

### 2. Claude MCP Configuration
Created file: `.mcp.json` (at project root)
```json
{
  "mcpServers": {
    "vibe-check-mcp": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@pv-bhat/vibe-check-mcp", "start", "--stdio"],
      "env": {},
      "managedBy": "vibe-check-mcp-cli"
    }
  }
}
```

**Important:** Claude Code requires the configuration file to be named `.mcp.json` and located at the project root directory. The top-level key must be `"mcpServers"` (not `"servers"`). All servers must include a `"type"` field (`"stdio"` or `"http"`).

### 3. Activation Steps (Claude Code UI)
1. Restart Claude Code to detect the new `.mcp.json` file at the project root.
2. Run the `/mcp` command to view and approve the configured servers.
3. Approve any servers that require permissions.
4. Run a basic tool call:
   - `update_constitution` with a test rule.
   - `check_constitution` to confirm rule echoes.

### 4. Validation Checklist
- [ ] Server process launches (observe log "[MCP] stdio transport connected" in Claude console if exposed).
- [ ] Tools enumerate: `update_constitution`, `check_constitution`, `reset_constitution`, `vibe_check`, `vibe_learn`.
- [ ] Adding a rule returns success.
- [ ] Checking constitution returns non-empty rule array including the added rule.
- [ ] Reset clears the rules array.
- [ ] A `vibe_check` call with `goal` and `plan` returns structured advice/questions.

### 5. Troubleshooting
| Symptom | Action |
|---------|--------|
| Empty `check_constitution` response | Ensure a prior `update_constitution` succeeded; retry after restart. |
| npx command not found | Install Node.js or ensure PATH reflects installation. |
| Tools missing | Confirm package `@pv-bhat/vibe-check-mcp` installed (npx auto-install) and args use `start --stdio`. |
| Repeated timeouts | Check for lingering orphan processes; terminate stale Node tasks. |

### 6. Cadence Policy Reminder
Follow strategic checkpoints (Phase planning, pre-implementation, execution preflight, reflection) with 10–15% vibe_check dosage. Avoid over-invocation (>20%).

### 7. Session Governance
Embed constitution rules inside the `plan` narrative of each `vibe_check` call. Log adaptations and learnings with `vibe_learn` after non-trivial resolutions.

---
Last Updated: 2025-11-10
Authority: Internal workspace MCP integration guidelines.
