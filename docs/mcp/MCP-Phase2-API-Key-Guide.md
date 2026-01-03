# MCP Phase 2 API Key Acquisition Guide

## Installation Status: 4 of 5 servers installed ✅

Successfully installed and configured in VS Code:
- ✅ TestSprite MCP Server (`@testsprite/testsprite-mcp`)
- ✅ AgentOps MCP Server (`agentops-mcp`)
- ✅ AgentQL MCP Server (`agentql-mcp`)
- ✅ Magic MCP Server (`@21st-dev/magic`)
- ⚠️ APIMatic Validator (no dedicated MCP package found)

## Required API Keys

### 1. TestSprite API Key (`TESTSPRITE_API_KEY`)

**Purpose**: Node.js testing automation and test generation
**Platform**: https://testsprite.io

**Steps to obtain**:
1. Visit https://testsprite.io and create an account
2. Navigate to dashboard: https://testsprite.io/dashboard
3. Go to API keys section
4. Generate new API key for MCP integration
5. Copy key for environment variable setup

**Environment Variable**:
```bash
TESTSPRITE_API_KEY=your_testsprite_api_key_here
```

### 2. AgentOps API Key (`AGENTOPS_API_KEY`)

**Purpose**: AI agent monitoring, tracing, and performance metrics
**Platform**: https://agentops.ai

**Steps to obtain**:
1. Sign up at https://agentops.ai
2. Complete account verification
3. Navigate to settings: https://agentops.ai/settings/api
4. Generate API key for workspace
5. Copy key value

**Environment Variable**:
```bash
AGENTOPS_API_KEY=your_agentops_api_key_here
```

### 3. AgentQL API Key (`AGENTQL_API_KEY`)

**Purpose**: Natural language web scraping and data extraction
**Platform**: https://agentql.com

**Steps to obtain**:
1. Register account at https://agentql.com
2. Login and access dashboard
3. Navigate to API keys: https://agentql.com/dashboard/api-keys
4. Create new API key for MCP server usage
5. Note usage limits and pricing tier

**Environment Variable**:
```bash
AGENTQL_API_KEY=your_agentql_api_key_here
```

### 4. Magic API Key (`TWENTY_FIRST_API_KEY`)

**Purpose**: AI-powered UI component generation and refinement
**Platform**: https://21st.dev/magic

**Steps to obtain**:
1. Create account at https://21st.dev
2. Access Magic console: https://21st.dev/magic/console
3. Navigate to API settings or developer section
4. Generate API token for server integrations
5. Copy key for configuration

**Environment Variable**:
```bash
TWENTY_FIRST_API_KEY=your_21st_dev_api_key_here
```

### 5. APIMatic (Alternative Solutions)

**Issue**: No dedicated MCP server found for APIMatic
**Available Packages**: `@apimatic/cli`, various SDK packages

**Options**:
1. Use APIMatic CLI directly for API validation
2. Create custom MCP server wrapper
3. Integrate with existing API validation tools
4. Skip if not critical to workflow

## Environment Variable Setup

### Windows PowerShell (Permanent)
```powershell
# Set system-wide environment variables
[Environment]::SetEnvironmentVariable("TESTSPRITE_API_KEY", "your_key_here", "User")
[Environment]::SetEnvironmentVariable("AGENTOPS_API_KEY", "your_key_here", "User")
[Environment]::SetEnvironmentVariable("AGENTQL_API_KEY", "your_key_here", "User")
[Environment]::SetEnvironmentVariable("TWENTY_FIRST_API_KEY", "your_key_here", "User")

# Restart VS Code after setting environment variables
```

### VS Code Integration Verification

After setting environment variables:

1. Restart VS Code completely
2. Open PowerShell terminal in VS Code
3. Verify environment variables:
   ```powershell
   $env:TESTSPRITE_API_KEY
   $env:AGENTOPS_API_KEY
   $env:AGENTQL_API_KEY
   $env:TWENTY_FIRST_API_KEY
   ```

## Testing Installation

Run the Phase 2 server tests:
```bash
cd "C:\Users\james.e.hardy\Documents\PowerShell Projects"
python test_mcp_servers.py --phase 2
```

Expected results after API key setup:
- ✅ All Node.js version requirements (should pass)
- ✅ All API key validations (should pass after setup)
- ✅ Installation validations (should pass)

## VS Code MCP Configuration

Current `.vscode/mcp.json` configuration includes:
- TestSprite server with `TESTSPRITE_API_KEY` reference
- AgentOps server with `AGENTOPS_API_KEY` reference
- AgentQL server with `AGENTQL_API_KEY` reference
- Magic MCP server with `TWENTY_FIRST_API_KEY` reference

## Security Best Practices

1. **Never commit API keys to repositories**
2. Use environment variables for all keys
3. Consider using `.env` files for development (add to `.gitignore`)
4. Rotate keys periodically
5. Monitor API usage and limits
6. Use least privilege principle for key permissions

## Next Steps

1. **Obtain all required API keys** from respective platforms
2. **Set environment variables** using PowerShell commands above
3. **Restart VS Code** to reload environment
4. **Run validation tests** to confirm all servers functional
5. **Begin using MCP servers** in GitHub Copilot workflows

## Available MCP Server Capabilities

Once configured, you'll have access to:

### TestSprite
- Automated test generation
- Node.js testing workflows
- Test coverage analysis

### AgentOps
- AI agent performance monitoring
- Conversation tracing
- Usage analytics

### AgentQL
- Natural language web scraping
- DOM element extraction
- Web automation

### Magic MCP
- UI component generation
- Logo and design assets
- TypeScript component creation

## Troubleshooting

### API Key Issues
- Verify environment variables are set correctly
- Restart VS Code after setting variables
- Check API key validity on respective platforms

### Server Connection Issues
- Confirm Node.js version ≥16 (current: v24.5.0 ✅)
- Verify npm packages installed globally
- Check VS Code MCP configuration syntax

### Testing Issues
- Run individual server tests: `python test_mcp_servers.py --phase 2 --server testsprite`
- Check detailed error messages in test output
- Validate API key permissions on platforms

---

**Status**: 4/5 servers successfully installed and configured. API key collection required for full functionality.
