# MCP Configuration Best Practices & Standards

**Version**: 1.0
**Last Updated**: 2025-12-04
**Status**: ✅ ACTIVE STANDARD

---

## Executive Summary

This document establishes best practices for configuring Model Context Protocol (MCP) servers in VS Code, based on lessons learned from resolving the "tool disabled by user" issue.

**Key Principles**:
1. **Two-Layer Configuration Required**: Server registration (mcp.json) + Model permissions (settings.json)
2. **serverSampling is NOT Optional**: All servers need explicit model allowlists
3. **STDIO-First Transport**: Prefer local stdio over HTTP for VS Code integration
4. **Health Checks Mandatory**: Verify server connectivity before assuming tools work
5. **Documentation is Critical**: Every MCP server needs configuration guide

---

## Configuration Architecture

### Layer 1: Server Registration (`.vscode/mcp.json`)

**Purpose**: Define MCP servers, transport type, and environment

**Required Fields**:
```jsonc
{
  "mcpServers": {
    "server-name": {
      "type": "stdio" | "http",  // REQUIRED: Transport type
      "command": "node",           // For stdio: executable
      "args": ["path/to/server"],  // For stdio: arguments
      "env": {                     // OPTIONAL: Environment variables
        "API_ENDPOINT": "http://..."
      }
    }
  }
}
```

**Best Practices**:
- Use descriptive server names (lowercase-with-hyphens)
- Prefer `stdio` transport for local servers
- Use absolute paths or paths relative to workspace root
- Document required environment variables
- Include health check endpoints for HTTP servers

**Example (STDIO)**:
```jsonc
{
  "mcpServers": {
    "task-manager": {
      "type": "stdio",
      "command": "node",
      "args": ["mcp-servers/task-manager/dist/index.js"],
      "env": {
        "TASK_MANAGER_API_ENDPOINT": "http://localhost:3001/api",
        "LOG_LEVEL": "info"
      }
    }
  }
}
```

**Example (HTTP)**:
```jsonc
{
  "mcpServers": {
    "linear-remote": {
      "type": "http",
      "url": "https://mcp.linear.app/mcp",
      "headers": {
        "Authorization": "Bearer ${env:LINEAR_API_KEY}"
      }
    }
  }
}
```

### Layer 2: Model Permissions (`.vscode/settings.json`)

**Purpose**: Control which AI models can access each server's tools

**Required Configuration**:
```jsonc
{
  "chat.mcp.serverSampling": {
    "[workspace-folder]/.vscode/mcp.json: [server-name]": {
      "allowedModels": [
        "copilot/claude-sonnet-4.5",
        "copilot/claude-opus-4.5",
        "copilot/gpt-5"
      ],
      "allowedDuringChat": true  // OPTIONAL: Default true
    }
  }
}
```

**Critical**: The key format MUST exactly match:
```
"[workspace-folder]/.vscode/mcp.json: [server-name]"
```

**Example**:
```jsonc
{
  "chat.mcp.serverSampling": {
    "PowerShell Projects/.vscode/mcp.json: task-manager": {
      "allowedModels": [
        "copilot/claude-sonnet-4.5",
        "copilot/claude-opus-4.5",
        "copilot/gpt-5"
      ]
    }
  }
}
```

**Model Identifiers**:
- `copilot/claude-sonnet-4.5` - Balanced performance
- `copilot/claude-opus-4.5` - Maximum reasoning depth
- `copilot/gpt-5` - GPT-5 (if available)
- `copilot/gpt-4o` - GPT-4 Optimized

---

## Server Categories & Configuration Templates

### Category 1: Task & Project Management

**Characteristics**:
- High tool count (30-50 tools)
- Complex input schemas
- Requires all models for flexibility
- Benefits from GPT-5 for planning

**Template**:
```jsonc
{
  "mcpServers": {
    "task-manager": {
      "type": "stdio",
      "command": "node",
      "args": ["mcp-servers/task-manager/dist/index.js"],
      "env": {
        "TASK_MANAGER_API_ENDPOINT": "http://localhost:3001/api"
      }
    }
  }
}

// settings.json
{
  "chat.mcp.serverSampling": {
    "PowerShell Projects/.vscode/mcp.json: task-manager": {
      "allowedModels": [
        "copilot/claude-sonnet-4.5",
        "copilot/claude-opus-4.5",
        "copilot/gpt-5"
      ]
    }
  }
}
```

**Examples**: task-manager, Linear, Jira

### Category 2: Metacognitive & Reasoning

**Characteristics**:
- Few tools (3-10)
- Requires deep reasoning
- Best with Opus or GPT-5
- Pattern interrupt and validation tools

**Template**:
```jsonc
{
  "mcpServers": {
    "vibe-check-mcp": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@jhardy82/vibe-check-mcp"]
    }
  }
}

// settings.json
{
  "chat.mcp.serverSampling": {
    "PowerShell Projects/.vscode/mcp.json: vibe-check-mcp": {
      "allowedModels": [
        "copilot/claude-opus-4.5",  // Prioritize Opus for reasoning
        "copilot/claude-sonnet-4.5"
      ]
    }
  }
}
```

**Examples**: vibe-check-mcp, SeqThinking, branched-thinking

### Category 3: Analytics & Data

**Characteristics**:
- Data processing tools
- Query building and execution
- Benefits from all models
- May require database credentials

**Template**:
```jsonc
{
  "mcpServers": {
    "duckdb-velocity": {
      "type": "stdio",
      "command": "node",
      "args": ["mcp-servers/duckdb/dist/index.js"],
      "env": {
        "DUCKDB_PATH": "db/velocity.duckdb",
        "READ_ONLY": "false"
      }
    }
  }
}

// settings.json
{
  "chat.mcp.serverSampling": {
    "PowerShell Projects/.vscode/mcp.json: duckdb-velocity": {
      "allowedModels": [
        "copilot/claude-sonnet-4.5",
        "copilot/claude-opus-4.5",
        "copilot/gpt-5"
      ]
    }
  }
}
```

**Examples**: DuckDB-velocity, database-mcp, postgres-mcp

### Category 4: Memory & Context

**Characteristics**:
- Persistent storage tools
- Cross-session state
- Simple schemas
- Works well with Sonnet

**Template**:
```jsonc
{
  "mcpServers": {
    "memory": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}

// settings.json
{
  "chat.mcp.serverSampling": {
    "PowerShell Projects/.vscode/mcp.json: memory": {
      "allowedModels": [
        "copilot/claude-sonnet-4.5",
        "copilot/claude-opus-4.5"
      ]
    }
  }
}
```

**Examples**: Memory, context-store, session-manager

### Category 5: External Integrations

**Characteristics**:
- Remote HTTP servers
- OAuth/API key authentication
- Third-party services
- May work without serverSampling (verify)

**Template**:
```jsonc
{
  "mcpServers": {
    "linear": {
      "type": "http",
      "url": "https://mcp.linear.app/mcp",
      "headers": {
        "Authorization": "Bearer ${env:LINEAR_API_KEY}"
      }
    }
  }
}

// settings.json
{
  "chat.mcp.serverSampling": {
    "PowerShell Projects/.vscode/mcp.json: linear": {
      "allowedModels": [
        "copilot/claude-sonnet-4.5",
        "copilot/claude-opus-4.5"
      ]
    }
  }
}
```

**Examples**: Linear, GitHub, Slack, Notion

---

## Configuration Validation

### Automated Validation Script

**PowerShell Validation** (`scripts/Validate-MCPConfiguration.ps1`):
```powershell
<#
.SYNOPSIS
Validate MCP configuration completeness and correctness

.DESCRIPTION
Checks that:
1. All servers in mcp.json have serverSampling entries
2. JSON syntax is valid
3. Environment variables are defined
4. Server executables exist
#>

param(
    [string]$WorkspaceRoot = $PWD
)

# Load configurations
$mcpConfigPath = Join-Path $WorkspaceRoot ".vscode/mcp.json"
$settingsPath = Join-Path $WorkspaceRoot ".vscode/settings.json"

Write-Host "Validating MCP Configuration..." -ForegroundColor Cyan

# Test JSON validity
try {
    $mcpConfig = Get-Content $mcpConfigPath -Raw | ConvertFrom-Json
    Write-Host "✅ mcp.json is valid JSON" -ForegroundColor Green
} catch {
    Write-Host "❌ mcp.json has syntax errors: $_" -ForegroundColor Red
    exit 1
}

try {
    $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
    Write-Host "✅ settings.json is valid JSON" -ForegroundColor Green
} catch {
    Write-Host "❌ settings.json has syntax errors: $_" -ForegroundColor Red
    exit 1
}

# Check serverSampling coverage
$mcpServers = $mcpConfig.mcpServers.PSObject.Properties.Name
$samplingKeys = $settings.'chat.mcp.serverSampling'.PSObject.Properties.Name

Write-Host "`nServer Coverage Check:" -ForegroundColor Cyan

$missingServers = @()
foreach ($server in $mcpServers) {
    $expectedKey = "PowerShell Projects/.vscode/mcp.json: $server"
    
    if ($samplingKeys -contains $expectedKey) {
        Write-Host "✅ $server - serverSampling configured" -ForegroundColor Green
    } else {
        Write-Host "⚠️  $server - MISSING serverSampling entry" -ForegroundColor Yellow
        $missingServers += $server
    }
}

if ($missingServers.Count -gt 0) {
    Write-Host "`n⚠️  WARNING: $($missingServers.Count) servers missing serverSampling configuration" -ForegroundColor Yellow
    Write-Host "These servers may show as 'disabled by user' in Copilot Chat" -ForegroundColor Yellow
    Write-Host "`nMissing servers:" -ForegroundColor Yellow
    $missingServers | ForEach-Object { Write-Host "  - $_" }
    
    Write-Host "`nAdd to settings.json:" -ForegroundColor Cyan
    foreach ($server in $missingServers) {
        Write-Host @"
"PowerShell Projects/.vscode/mcp.json: $server": {
  "allowedModels": [
    "copilot/claude-sonnet-4.5",
    "copilot/claude-opus-4.5"
  ]
},
"@ -ForegroundColor Gray
    }
    exit 1
}

Write-Host "`n✅ All MCP servers have serverSampling configuration" -ForegroundColor Green
exit 0
```

### Manual Validation Checklist

**Pre-Deployment**:
- [ ] mcp.json JSON syntax valid
- [ ] settings.json JSON syntax valid
- [ ] All servers have serverSampling entries
- [ ] Server executable paths correct
- [ ] Environment variables documented
- [ ] Health check endpoints tested (for HTTP servers)

**Post-Deployment**:
- [ ] VS Code window reloaded
- [ ] All servers appear in Copilot Chat tools list
- [ ] No "disabled by user" errors
- [ ] Sample tool invocation succeeds
- [ ] Error messages are clear and actionable

---

## Troubleshooting Guide

### Problem: "Tool is currently disabled by the user"

**Root Cause**: Missing serverSampling entry

**Solution**:
1. Open `.vscode/settings.json`
2. Find `chat.mcp.serverSampling` section
3. Add entry for your server:
```jsonc
"PowerShell Projects/.vscode/mcp.json: [your-server]": {
  "allowedModels": [
    "copilot/claude-sonnet-4.5",
    "copilot/claude-opus-4.5"
  ]
}
```
4. Reload VS Code window (`Ctrl+Shift+P` → Developer: Reload Window)

### Problem: Server Not Appearing in Tools List

**Possible Causes**:
1. Server not registered in mcp.json
2. Server executable not found
3. Server crashed during startup
4. Transport type mismatch

**Debugging**:
```powershell
# Check server logs in VS Code Output panel
# View → Output → Select "MCP: [server-name]"

# Test stdio server manually
node mcp-servers/task-manager/dist/index.js

# Test HTTP server health
curl http://localhost:3001/api/health
```

### Problem: Tools Work in One Model But Not Another

**Root Cause**: Model not in allowedModels list

**Solution**:
Add missing model to serverSampling:
```jsonc
"PowerShell Projects/.vscode/mcp.json: task-manager": {
  "allowedModels": [
    "copilot/claude-sonnet-4.5",
    "copilot/claude-opus-4.5",
    "copilot/gpt-5"  // ← Add missing model
  ]
}
```

### Problem: Environment Variables Not Loading

**Causes**:
1. `.env` file not in workspace root
2. Variable name typo in mcp.json
3. VS Code not reloaded after .env changes

**Solution**:
```powershell
# Verify .env file exists
Test-Path .env

# Check variable names match
Get-Content .env | Select-String "API_ENDPOINT"

# Reload VS Code
# Ctrl+Shift+P → Developer: Reload Window
```

---

## Security Best Practices

### 1. Never Commit API Keys

**Bad** (committed to git):
```jsonc
{
  "env": {
    "API_KEY": "sk-1234567890abcdef"  // ❌ NEVER DO THIS
  }
}
```

**Good** (uses environment variable):
```jsonc
{
  "env": {
    "API_KEY": "${env:MY_API_KEY}"  // ✅ Safe - references .env
  }
}
```

### 2. Use `.env` for Secrets

**File**: `.env` (add to .gitignore)
```bash
LINEAR_API_KEY=lin_api_1234567890abcdef
GITHUB_TOKEN=ghp_abcdefghijklmnop
TASK_MANAGER_API_ENDPOINT=http://localhost:3001/api
```

**File**: `.gitignore`
```
.env
.env.local
.env.mcp-keys
*.secret
```

### 3. Limit Model Access for Sensitive Tools

**High Security** (financial tools - Opus only):
```jsonc
"PowerShell Projects/.vscode/mcp.json: finance-tools": {
  "allowedModels": [
    "copilot/claude-opus-4.5"  // Only most capable model
  ]
}
```

**Medium Security** (task management - Sonnet + Opus):
```jsonc
"PowerShell Projects/.vscode/mcp.json: task-manager": {
  "allowedModels": [
    "copilot/claude-sonnet-4.5",
    "copilot/claude-opus-4.5"
  ]
}
```

**Low Security** (read-only analytics - all models):
```jsonc
"PowerShell Projects/.vscode/mcp.json: analytics": {
  "allowedModels": [
    "copilot/claude-sonnet-4.5",
    "copilot/claude-opus-4.5",
    "copilot/gpt-5"
  ]
}
```

---

## Performance Optimization

### 1. Minimize Server Count

**Problem**: Too many servers slow VS Code startup

**Solution**: Consolidate related functionality
- ✅ Single task-manager server (tasks + projects + sprints)
- ❌ Separate servers for tasks, projects, sprints

### 2. Use HTTP for Remote Services

**Problem**: STDIO adds process management overhead for remote services

**Solution**: Use HTTP transport for external APIs
```jsonc
{
  "linear": {
    "type": "http",  // ✅ Efficient for remote
    "url": "https://mcp.linear.app/mcp"
  }
}
```

### 3. Lazy Load Large Datasets

**Problem**: Server loading entire database on startup

**Solution**: Implement pagination and filtering
```typescript
// ❌ Bad: Load all tasks
async listTasks(): Promise<Task[]> {
  return db.tasks.findMany();
}

// ✅ Good: Paginate and filter
async listTasks(filters: {
  limit?: number;
  offset?: number;
  status?: string;
}): Promise<Task[]> {
  return db.tasks.findMany({
    take: filters.limit || 100,
    skip: filters.offset || 0,
    where: filters.status ? { status: filters.status } : {}
  });
}
```

---

## Documentation Standards

### Server README Template

Every MCP server should have a `README.md`:

```markdown
# [Server Name] MCP Server

## Overview
Brief description of what this server does.

## Tools Provided
- `tool_name_1` - Description
- `tool_name_2` - Description
- ...

## Configuration

### mcp.json
\`\`\`jsonc
{
  "server-name": {
    "type": "stdio",
    "command": "node",
    "args": ["path/to/dist/index.js"],
    "env": {
      "REQUIRED_VAR": "description",
      "OPTIONAL_VAR": "description"
    }
  }
}
\`\`\`

### settings.json
\`\`\`jsonc
{
  "chat.mcp.serverSampling": {
    "PowerShell Projects/.vscode/mcp.json: server-name": {
      "allowedModels": [
        "copilot/claude-sonnet-4.5",
        "copilot/claude-opus-4.5"
      ]
    }
  }
}
\`\`\`

### Environment Variables
- `REQUIRED_VAR` - (Required) Description and purpose
- `OPTIONAL_VAR` - (Optional) Description, default: value

## Testing

### Health Check
\`\`\`bash
curl http://localhost:PORT/health
\`\`\`

### Sample Tool Invocation
\`\`\`
@workspace Use tool_name_1 to do something
\`\`\`

## Troubleshooting

### Issue: Server Not Responding
Solution: Check that API is running on port PORT

### Issue: Tools Disabled
Solution: Verify serverSampling configuration in settings.json
```

---

## Migration Checklist

When adding a new MCP server:

### Phase 1: Server Implementation
- [ ] Implement MCP server code
- [ ] Define tool schemas (ListToolsRequestSchema)
- [ ] Implement tool handlers (CallToolRequestSchema)
- [ ] Add health check endpoint (if HTTP)
- [ ] Write comprehensive README

### Phase 2: Configuration
- [ ] Add server entry to `.vscode/mcp.json`
- [ ] Add serverSampling entry to `.vscode/settings.json`
- [ ] Document required environment variables
- [ ] Add variables to `.env.example`
- [ ] Test JSON syntax validity

### Phase 3: Testing
- [ ] Build server (`npm run build` or equivalent)
- [ ] Reload VS Code window
- [ ] Verify server appears in tools list
- [ ] Test health check (if applicable)
- [ ] Test sample tool invocation
- [ ] Verify no "disabled" errors

### Phase 4: Documentation
- [ ] Update team wiki with configuration
- [ ] Add server to MCP servers inventory
- [ ] Document tool usage examples
- [ ] Create troubleshooting guide
- [ ] Add to onboarding checklist

---

## References

**MCP Specification**:
- https://github.com/modelcontextprotocol/specification
- https://github.com/modelcontextprotocol/typescript-sdk

**VS Code MCP Integration**:
- https://code.visualstudio.com/docs/copilot/mcp
- https://github.com/microsoft/vscode-mcp

**Related Issues**:
- GitHub #259: MCP tool registry caching
- GitHub #254684: Dynamic tool registration

**Internal Documentation**:
- `MCP-TOOL-AVAILABILITY-ROOT-CAUSE-ANALYSIS.md`
- `ACTION-LIST-CLIENT-IMPLEMENTATION-PLAN.md`
- `mcp-servers/task-manager/TOOL-REGISTRATION-ANALYSIS.md`

---

**Version History**:
- 1.0 (2025-12-04): Initial version based on task-manager investigation

**Maintained By**: ContextForge Engineering Team
**Review Cycle**: Quarterly
