# MCP Server Testing for VS Code Extensions
**Date**: 2025-11-07
**Platform**: VS Code with GitHub Copilot Agent + Claude Code Extensions
**Authority**: Manual testing phase for Task 4 verification

---

## Executive Summary

**Your Environment:**
- ✅ VS Code with MCP configuration at `.vscode/mcp.json`
- ✅ 13 MCP servers configured (STDIO: 11, HTTP: 1, SSE: 1)
- ✅ GitHub Copilot Agent extension installed
- ✅ Claude Code extension installed
- ✅ Environment variables validated (4/4 present)

**Key Insight:** The sync script we tested pushes configuration FROM `.vscode/mcp.json` TO other platforms (Claude Desktop/Cursor/Windsurf). Since you're using VS Code, your source configuration is already in place!

---

## VS Code MCP Architecture

### **How MCP Works in VS Code Extensions**

**GitHub Copilot Agent Extension:**
- Uses VS Code's Model Context Protocol (MCP) integration
- Reads MCP servers from `.vscode/mcp.json` in workspace
- Exposes MCP tools via `#mcp-server-name/*` syntax in agent mode
- Example: `#context7/*` for Context7 library documentation

**Claude Code Extension:**
- May have separate MCP integration (needs verification)
- Check extension settings for MCP configuration path
- Possibly uses different invocation pattern

---

## Testing Methodology for VS Code

### **Phase 1: Verify MCP Server Availability**

**Option A: Check GitHub Copilot Agent MCP Status**

1. Open Command Palette: `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type: `GitHub Copilot: Show MCP Servers`
3. Expected: List of 13 configured servers from `.vscode/mcp.json`

**Option B: Check VS Code Extension Host Logs**

1. Open Command Palette: `Ctrl+Shift+P`
2. Type: `Developer: Show Logs...`
3. Select: `Extension Host`
4. Look for MCP-related startup messages or errors

**Option C: Test MCP Tool Invocation Directly**

Open a new GitHub Copilot Agent chat and try these commands:

---

### **Phase 2: STDIO Server Testing**

#### **Test 1: Context7 (Library Documentation)** ⭐ RECOMMENDED

**GitHub Copilot Agent Command:**
```
@workspace Use the #context7/* tool to look up the pytest library
```

**Alternative Syntax:**
```
What is the pytest library? (Use Context7 MCP server)
```

**Expected Result:**
- Context7 MCP server invoked
- CONTEXT7_API_KEY environment variable resolved
- Library documentation returned (pytest description, usage, version)

**Troubleshooting:**
- ❌ "Tool not found" → MCP servers not loaded, check `.vscode/mcp.json` location
- ❌ "Authentication failed" → CONTEXT7_API_KEY not resolving (check environment variable)
- ❌ "Server error" → Check Extension Host logs for startup errors

---

#### **Test 2: DuckDB (SQL Database)**

**GitHub Copilot Agent Command:**
```
@workspace Use the #DuckDB/* tool to execute: SELECT 'MCP Server Working!' as status;
```

**Expected Result:**
- DuckDB MCP server invoked
- SQL query executed against `.tmp/metrics.duckdb`
- Result table showing "MCP Server Working!" in status column

**Why This Test:**
- No API key required (simpler validation)
- Tests STDIO transport mechanism
- Validates command execution and argument passing

---

#### **Test 3: Memory (Knowledge Graph)**

**GitHub Copilot Agent Command:**
```
@workspace Use the #Memory/* tool to store: "MCP testing conducted on 2025-11-07"
```

**Follow-up Command:**
```
@workspace Use the #Memory/* tool to retrieve information about MCP testing
```

**Expected Result:**
- First command: Confirmation that information stored in knowledge graph
- Second command: Retrieval of stored information from previous command

**Why This Test:**
- Tests stateful MCP server (memory persistence)
- Validates multi-turn MCP interactions

---

#### **Test 4: SeqThinking (Sequential Reasoning)**

**GitHub Copilot Agent Command:**
```
@workspace Use the #SeqThinking/* tool to analyze: What are the benefits of using MCP servers?
```

**Expected Result:**
- Sequential thinking process displayed
- Step-by-step reasoning breakdown
- Structured thought progression

**Why This Test:**
- Tests advanced MCP tool with complex interactions
- Validates agent's ability to use reasoning tools

---

### **Phase 3: HTTP Server Testing**

#### **Test 5: microsoft.docs.mcp (Microsoft Learn)**

**GitHub Copilot Agent Command:**
```
@workspace Use the #microsoft.docs.mcp/* tool to search for "Azure App Service documentation"
```

**Expected Result:**
- HTTP connection to https://learn.microsoft.com/api/mcp
- Documentation snippets from Microsoft Learn
- Relevant Azure App Service information

**Troubleshooting:**
- ❌ "Connection timeout" → Check internet connectivity
- ❌ "HTTP 404" → Microsoft Learn MCP endpoint may have changed
- ℹ️ **Note:** HTTP MCP servers may not be fully supported in all VS Code extensions yet

---

### **Phase 4: SSE Server Testing (CONDITIONAL)**

#### **Test 6: Archon (Server-Sent Events)**

**Prerequisite Check:**
```powershell
Test-NetConnection -ComputerName localhost -Port 8051
```

**If Archon is Running:**

**GitHub Copilot Agent Command:**
```
@workspace Use the #archon/* tool to interact with the Archon server
```

**Expected Result:**
- SSE connection established to http://localhost:8051/mcp
- Archon server responses received

**If Archon is NOT Running:**
- ℹ️ **SKIP this test** - SSE server not running is expected, not an error
- Archon is optional and may not be started by default

---

## Environment Variable Resolution Testing

### **Validation Method**

**Test with Context7 (API Key Required):**
```
@workspace Use the #context7/* tool to look up any library
```

**Success Indicators:**
- ✅ No "Authentication failed" errors
- ✅ Library documentation returned
- ✅ CONTEXT7_API_KEY resolved from environment

**VS Code Environment Variable Resolution:**
- VS Code reads environment variables from:
  1. System environment variables
  2. User environment variables
  3. VS Code integrated terminal environment
  4. `.env` files (if configured)

**Validation Command (PowerShell):**
```powershell
[System.Environment]::GetEnvironmentVariable('CONTEXT7_API_KEY', 'User')
# Should return: ctx7sk-9*** (masked)
```

---

## Quick Testing Checklist

### **Minimum Required Tests (Choose ONE):**

- [ ] **Option A:** Context7 library lookup (`#context7/*`) - Tests STDIO + API key
- [ ] **Option B:** DuckDB SQL query (`#DuckDB/*`) - Tests STDIO without API key
- [ ] **Option C:** Memory store/retrieve (`#Memory/*`) - Tests stateful STDIO

### **Optional Extended Tests:**

- [ ] SeqThinking reasoning (`#SeqThinking/*`)
- [ ] Microsoft Learn HTTP (`#microsoft.docs.mcp/*`)
- [ ] Archon SSE (if service running)
- [ ] GitHub MCP (`#github-mcp/*`)
- [ ] Task Manager (`#task-manager/*`)
- [ ] Playwright (`#playwright/*`)

---

## Reporting Results Template

### **Test Results for VS Code Extensions**

**Date:** 2025-11-07
**Environment:** VS Code + GitHub Copilot Agent + Claude Code

#### **MCP Server Status Check:**
- [ ] ✅ MCP servers visible in GitHub Copilot Agent
- [ ] ❌ MCP servers not showing (error details: _______)

#### **STDIO Test (Context7/DuckDB/Memory):**
- [ ] ✅ SUCCESS - Server responded correctly
- [ ] ❌ FAILED - Error: _______

#### **HTTP Test (microsoft.docs.mcp):**
- [ ] ✅ SUCCESS - Documentation retrieved
- [ ] ⏭️ SKIPPED - Not supported in extension
- [ ] ❌ FAILED - Error: _______

#### **SSE Test (Archon):**
- [ ] ✅ SUCCESS - Connection established
- [ ] ⏭️ SKIPPED - Service not running
- [ ] ❌ FAILED - Error: _______

#### **Environment Variable Resolution:**
- [ ] ✅ WORKING - Context7 authentication succeeded
- [ ] ❌ FAILED - Authentication error: _______

#### **Overall Assessment:**
- [ ] ✅ MCP integration working - At least 1 server tested successfully
- [ ] ⚠️ PARTIAL - Some servers working, some failing
- [ ] ❌ NOT WORKING - No servers responding

---

## Troubleshooting Guide

### **Issue: MCP Servers Not Showing**

**Potential Causes:**
1. `.vscode/mcp.json` not in workspace root
2. GitHub Copilot Agent extension not updated to MCP-compatible version
3. VS Code needs restart after MCP configuration changes

**Resolution Steps:**
```powershell
# 1. Verify configuration file location
Test-Path ".vscode/mcp.json"  # Should return: True

# 2. Check VS Code version (MCP requires recent version)
# Open: Help → About

# 3. Check GitHub Copilot Agent extension version
# Extensions → GitHub Copilot Agent → Version

# 4. Restart VS Code completely
# File → Exit → Reopen
```

---

### **Issue: Authentication Failures (Context7)**

**Symptoms:**
- "Authentication failed" error when testing Context7
- "Invalid API key" messages

**Resolution Steps:**
```powershell
# 1. Verify environment variable exists
[System.Environment]::GetEnvironmentVariable('CONTEXT7_API_KEY', 'User')

# 2. Check if VS Code can access it
# Open integrated terminal in VS Code:
$env:CONTEXT7_API_KEY
# Should show: ctx7sk-9*** (value present)

# 3. If not accessible in VS Code, restart VS Code after setting variable
```

---

### **Issue: STDIO Server Command Failures**

**Symptoms:**
- "Server failed to start" errors
- "Command not found" messages

**Resolution Steps:**
```powershell
# 1. Verify Node.js is accessible
node --version  # Should show version (e.g., v20.x.x)

# 2. Verify npx is accessible
npx --version   # Should show version

# 3. Check if required packages installed
Test-Path "interface/vscode-extension/node_modules/@modelcontextprotocol/server-memory"
# Should return: True

# 4. Install missing packages if needed
npm install
```

---

## Extension-Specific Testing Notes

### **GitHub Copilot Agent Extension**

**MCP Tool Invocation Syntax:**
- Format: `#mcp-server-name/*`
- Example: `#context7/*`, `#DuckDB/*`, `#Memory/*`
- Context: Must be used in agent mode chat (not inline suggestions)

**Expected Behavior:**
- MCP servers load when workspace opened
- Tools available in agent chat immediately
- Extension Host logs show MCP initialization

**Known Limitations:**
- Not all MCP server types may be supported (HTTP/SSE experimental)
- Some tools may require explicit invocation syntax
- Tool discovery may vary by extension version

---

### **Claude Code Extension**

**MCP Integration Status:**
- Verify if extension supports MCP tools
- Check extension settings for MCP configuration path
- May use different invocation pattern than GitHub Copilot Agent

**Testing Approach:**
- Open Claude Code chat interface
- Attempt same test queries as GitHub Copilot Agent
- Compare behavior and availability

**Documentation Reference:**
- Check extension marketplace page for MCP support status
- Review extension changelog for MCP integration updates

---

## Success Criteria for VS Code Testing

### **Minimum Acceptable Result:**
- ✅ At least ONE STDIO server working (Context7/DuckDB/Memory)
- ✅ MCP servers visible in extension (status check passed)
- ✅ Environment variables resolving correctly (if applicable)

### **Ideal Result:**
- ✅ Multiple STDIO servers working (3+ tested successfully)
- ✅ HTTP server working (microsoft.docs.mcp)
- ✅ Environment variable resolution validated (Context7 auth works)
- ✅ Both GitHub Copilot Agent and Claude Code extensions support MCP

### **Acceptable Partial Results:**
- ⚠️ STDIO servers working, HTTP/SSE not supported (common in early MCP adoption)
- ⚠️ One extension supports MCP, other doesn't (extension-specific feature)
- ⚠️ Manual invocation required (no automatic tool discovery yet)

---

## Next Steps After Testing

### **Report Back to Agent:**

**If Successful:**
```
"VS Code MCP testing complete. GitHub Copilot Agent successfully invoked Context7
and DuckDB servers. Environment variables resolving correctly."
```

**If Issues Found:**
```
"VS Code MCP testing - Issue: MCP servers not showing in GitHub Copilot Agent.
Extension Host logs show: [error message]. Configuration file verified at
.vscode/mcp.json with 13 servers."
```

### **Agent Will Then:**
1. Mark Task 4 as 100% complete (or document blocking issues)
2. Update verification document with VS Code-specific findings
3. Proceed to Task 5 (Quick Start Guide) with VS Code focus
4. Incorporate VS Code testing results into documentation

---

## Additional Resources

### **VS Code MCP Documentation:**
- GitHub Copilot Agent extension documentation
- Claude Code extension documentation
- Model Context Protocol specification: https://modelcontextprotocol.io/

### **Configuration References:**
- Source configuration: `.vscode/mcp.json` (13 servers)
- Environment variables: User-level Windows environment
- Extension logs: `Developer: Show Logs... → Extension Host`

### **Support Channels:**
- GitHub Copilot Agent issues: GitHub repository
- Claude Code support: Extension marketplace
- MCP specification: Official MCP community

---

## Revision History

- **2025-11-07 10:45** - Initial version for VS Code extension testing
- Platform clarification: User uses VS Code, not standalone platforms
- Focus shifted from Claude Desktop/Cursor/Windsurf to VS Code extensions
- Testing methodology adapted for extension-based MCP integration
