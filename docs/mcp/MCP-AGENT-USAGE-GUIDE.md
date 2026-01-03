# MCP Agent Usage Guide for Claude Code
**Last Updated**: 2025-11-13
**Workspace**: PowerShell Projects
**MCPs Configured**: 4 (Vibe Check, Sequential Thinking, Firebase, GitHub Copilot)

---

## Table of Contents

1. [Overview](#overview)
2. [Configured MCPs](#configured-mcps)
3. [Usage Examples](#usage-examples)
4. [Best Practices](#best-practices)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Workflows](#advanced-workflows)

---

## Overview

This workspace has **4 Model Context Protocol (MCP) servers** configured to enhance Claude Code capabilities. MCPs extend Claude Code with specialized tools, resources, and integrations.

### What are MCPs?

MCPs (Model Context Protocol servers) are external tools that Claude Code can invoke to:
- Access external APIs and services
- Perform specialized computations
- Integrate with development tools (Git, GitHub, Firebase, etc.)
- Provide domain-specific capabilities

### Configuration Location

MCPs are configured in `.claude/mcp.json` at the workspace level.

**To reload MCPs**: Restart Claude Code

---

## Configured MCPs

### 1. Vibe Check MCP
**Package**: `@pv-bhat/vibe-check-mcp`
**Status**: ✅ Active (managed by vibe-check-mcp-cli)

**Purpose**: Constitutional testing and validation framework

**Capabilities**:
- Vibe check validation
- Constitutional framework testing
- Quality gate enforcement
- System health verification

**When to Use**:
- Validating system architecture decisions
- Running quality gates
- Checking constitutional compliance
- System health checks

**Example Invocation**:
```
Run a vibe check on the current TaskMan-v2 extension implementation
```

Claude Code will automatically invoke the Vibe Check MCP to perform validation.

---

### 2. Sequential Thinking MCP
**Package**: `@modelcontextprotocol/server-sequential-thinking`
**Status**: ✅ Active

**Purpose**: Advanced problem-solving with structured reasoning

**Capabilities**:
- Break down complex problems into steps
- Plan and design with room for revision
- Analysis with course correction
- Handle problems where full scope isn't initially clear

**When to Use**:
- Complex architectural decisions
- Multi-step refactoring plans
- Debugging intricate issues
- Planning feature implementations

**Example Invocation**:
```
Use sequential thinking to plan the implementation of JWT authentication for TaskMan-v2
```

**Features**:
- Thought logging enabled (DISABLE_THOUGHT_LOGGING=false)
- Shows intermediate reasoning steps
- Allows for plan revision during execution
- Suitable for exploratory problem-solving

**Environment Variables**:
- `DISABLE_THOUGHT_LOGGING`: Set to "false" (logging enabled)

---

### 3. Firebase MCP
**Package**: `firebase-tools@latest`
**Status**: ✅ Active (requires authentication)

**Purpose**: Firebase and Firestore integration

**Capabilities**:
- Firebase project management
- Firestore database operations
- Cloud Functions interaction
- Firebase CLI integration

**Prerequisites**:
```bash
# Authenticate with Firebase (one-time setup)
npx firebase login

# Check authentication status
npx firebase login --status
```

**When to Use**:
- Managing Firebase projects
- Firestore database queries
- Deploying Cloud Functions
- Firebase configuration management

**Example Invocation**:
```
List all Firestore collections in my Firebase project
```

**Note**: First use will prompt for Firebase authentication if not already logged in.

---

### 4. GitHub Copilot MCP
**Package**: `@leonardommello/copilot-mcp-server`
**Status**: ✅ Active (authorized for jhardy82)

**Purpose**: GitHub Copilot integration for Claude Code

**Capabilities**:
- AI-powered code assistance
- GitHub Copilot CLI integration
- Full MCP capabilities (Tools, Resources, Prompts)
- Seamless authentication

**Prerequisites**:
```bash
# Install GitHub Copilot CLI (if not installed)
npm install -g @github/copilot

# Authenticate with GitHub
gh auth login

# Verify authentication
gh auth status
```

**Current Authentication**:
- ✅ Logged in to github.com as **jhardy82**
- ✅ Token scopes include: copilot, repo, workflow
- ✅ GitHub Copilot subscription active

**When to Use**:
- Code completion and suggestions
- Code explanation and documentation
- Refactoring assistance
- Best practices recommendations

**Example Invocation**:
```
Use GitHub Copilot to suggest improvements for the TodoItem class
```

**Environment Variables**:
- `GITHUB_USER`: Set to "jhardy82"

---

## Usage Examples

### Example 1: Complex Problem Solving (Sequential Thinking)

**Scenario**: Planning a multi-phase refactoring

**User Prompt**:
```
Use sequential thinking to create a plan for migrating TaskMan-v2 from direct PostgreSQL access to a DTM API-only model
```

**What Happens**:
1. Claude Code invokes Sequential Thinking MCP
2. Problem is broken down into phases
3. Each phase is analyzed with dependencies
4. Plan includes revision points
5. Final plan is presented with rationale

**Expected Output**:
- Phase-by-phase implementation plan
- Dependencies and blockers identified
- Risk assessment included
- Course-correction opportunities highlighted

---

### Example 2: Firebase Database Query

**Scenario**: Querying Firestore for project data

**User Prompt**:
```
Query the Firestore database for all tasks in project P-CF-SPECTRE-001
```

**What Happens**:
1. Firebase MCP authenticates (if needed)
2. Connects to configured Firebase project
3. Executes Firestore query
4. Returns results to Claude Code
5. Claude Code formats and presents data

**Expected Output**:
- Task data from Firestore
- Formatted as structured data
- Ready for analysis or export

---

### Example 3: GitHub Copilot Code Review

**Scenario**: Getting code improvement suggestions

**User Prompt**:
```
Use GitHub Copilot to review the E2E test infrastructure and suggest improvements
```

**What Happens**:
1. GitHub Copilot MCP analyzes code structure
2. Provides AI-powered suggestions
3. Identifies potential issues
4. Recommends best practices
5. Returns suggestions to Claude Code

**Expected Output**:
- Code quality recommendations
- Best practice suggestions
- Potential bug identifications
- Refactoring opportunities

---

### Example 4: Vibe Check Validation

**Scenario**: Validating architectural decision

**User Prompt**:
```
Run a vibe check on the decision to use Sequential Thinking MCP for complex problem solving
```

**What Happens**:
1. Vibe Check MCP analyzes the decision
2. Checks constitutional compliance
3. Validates against quality gates
4. Returns validation report

**Expected Output**:
- Constitutional framework validation
- Quality gate status
- Recommendation (approve/reject/revise)
- Rationale for assessment

---

## Best Practices

### 1. Explicit MCP Invocation

**✅ Good**:
```
Use sequential thinking to plan the JWT implementation
Use GitHub Copilot to review this code
Query Firebase for project data
```

**❌ Avoid**:
```
Plan the JWT implementation  (ambiguous - may not invoke MCP)
Review this code             (may use built-in capability instead)
```

**Tip**: Explicitly mention the MCP name to ensure correct tool is used.

---

### 2. Provide Context

**✅ Good**:
```
Use sequential thinking to plan JWT authentication for TaskMan-v2 extension, considering:
- Current port configuration (3001)
- Existing DTM API integration
- Need for token storage
- VS Code extension constraints
```

**❌ Avoid**:
```
Plan JWT auth  (insufficient context)
```

**Tip**: More context = better MCP results.

---

### 3. Combine MCPs

**Example: Multi-MCP Workflow**:
```
1. Use sequential thinking to plan Firebase integration for TaskMan-v2
2. Use Firebase MCP to create the Firestore schema
3. Use GitHub Copilot to review the integration code
4. Run a vibe check to validate the architecture
```

**Tip**: MCPs can be chained for comprehensive workflows.

---

### 4. Verify MCP Availability

**Check if MCPs are loaded**:
```
What MCPs are currently available?
```

Claude Code will list all configured and active MCPs.

**If MCP not available**:
1. Check `.claude/mcp.json` configuration
2. Restart Claude Code
3. Verify npm package installation
4. Check authentication (Firebase, GitHub)

---

## Troubleshooting

### Problem: MCP Not Responding

**Symptoms**:
- MCP command fails
- No response from MCP
- Error: "MCP server not found"

**Solutions**:
1. **Restart Claude Code**: MCPs are loaded on startup
2. **Verify configuration**: Check `.claude/mcp.json` syntax
3. **Check package availability**:
   ```bash
   npx -y @modelcontextprotocol/server-sequential-thinking --help
   npx -y firebase-tools --version
   npx -y @leonardommello/copilot-mcp-server --help
   ```
4. **Review logs**: Check Claude Code output for MCP errors

---

### Problem: Firebase Authentication Failed

**Symptoms**:
- "Firebase login required"
- "Authentication error"

**Solutions**:
1. **Login to Firebase**:
   ```bash
   npx firebase login
   ```
2. **Check login status**:
   ```bash
   npx firebase login --status
   ```
3. **Select correct project**:
   ```bash
   npx firebase use <project-id>
   ```

---

### Problem: GitHub Copilot MCP Not Working

**Symptoms**:
- Copilot suggestions not appearing
- "GitHub authentication required"

**Solutions**:
1. **Check GitHub CLI auth**:
   ```bash
   gh auth status
   ```
2. **Re-authenticate**:
   ```bash
   gh auth login
   ```
3. **Verify Copilot subscription**:
   - GitHub account must have active Copilot subscription
   - Check: https://github.com/settings/copilot

---

### Problem: Sequential Thinking MCP Silent

**Symptoms**:
- MCP invoked but no thought logging
- No intermediate steps shown

**Solutions**:
1. **Check environment variable**: `DISABLE_THOUGHT_LOGGING` should be "false"
2. **Verify in mcp.json**:
   ```json
   "env": {
     "DISABLE_THOUGHT_LOGGING": "false"
   }
   ```
3. **Restart Claude Code** after configuration change

---

## Advanced Workflows

### Workflow 1: Feature Development with Full MCP Stack

**Scenario**: Implementing a new TaskMan-v2 feature

**Steps**:
1. **Planning** (Sequential Thinking):
   ```
   Use sequential thinking to plan the implementation of task priority levels in TaskMan-v2
   ```

2. **Architecture Validation** (Vibe Check):
   ```
   Run a vibe check on the priority levels implementation plan
   ```

3. **Code Generation** (GitHub Copilot):
   ```
   Use GitHub Copilot to generate the TypeScript interface for task priorities
   ```

4. **Data Schema** (Firebase):
   ```
   Create a Firestore collection schema for task priorities
   ```

5. **Final Validation** (Vibe Check):
   ```
   Run final vibe check on the complete implementation
   ```

---

### Workflow 2: Debugging Complex Issues

**Steps**:
1. **Problem Analysis** (Sequential Thinking):
   ```
   Use sequential thinking to debug why TaskMan-v2 extension fails to sync with DTM API
   ```

2. **Code Review** (GitHub Copilot):
   ```
   Use GitHub Copilot to review the sync logic for potential issues
   ```

3. **Validation** (Vibe Check):
   ```
   Run vibe check to ensure the fix aligns with architectural principles
   ```

---

### Workflow 3: Documentation and Knowledge Transfer

**Steps**:
1. **Architecture Documentation** (Sequential Thinking):
   ```
   Use sequential thinking to create comprehensive documentation for TaskMan-v2 architecture
   ```

2. **Code Examples** (GitHub Copilot):
   ```
   Use GitHub Copilot to generate example code snippets for each feature
   ```

3. **Firebase Integration Docs** (Firebase MCP):
   ```
   Document the Firebase integration including schemas and queries
   ```

---

## MCP Configuration Reference

### Current Configuration (.claude/mcp.json)

```json
{
  "servers": {},
  "mcpServers": {
    "vibe-check-mcp": {
      "command": "npx",
      "args": ["-y", "@pv-bhat/vibe-check-mcp", "start", "--stdio"],
      "env": {},
      "managedBy": "vibe-check-mcp-cli"
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "env": {
        "DISABLE_THOUGHT_LOGGING": "false"
      }
    },
    "firebase": {
      "command": "npx",
      "args": ["-y", "firebase-tools@latest", "mcp"],
      "env": {}
    },
    "github-copilot": {
      "command": "npx",
      "args": ["-y", "@leonardommello/copilot-mcp-server"],
      "env": {
        "GITHUB_USER": "jhardy82"
      }
    }
  }
}
```

---

## Quick Reference Card

| MCP | Use For | Example Prompt |
|-----|---------|----------------|
| **Sequential Thinking** | Complex planning, multi-step problems | "Use sequential thinking to plan..." |
| **Firebase** | Database queries, Firebase management | "Query Firebase for...", "Deploy to Firebase..." |
| **GitHub Copilot** | Code review, suggestions, best practices | "Use GitHub Copilot to review...", "Suggest improvements..." |
| **Vibe Check** | Architecture validation, quality gates | "Run vibe check on...", "Validate architecture..." |

---

## Getting Help

### Resources
- **Sequential Thinking MCP**: https://www.npmjs.com/package/@modelcontextprotocol/server-sequential-thinking
- **Firebase Tools**: https://firebase.google.com/docs/cli
- **GitHub Copilot MCP**: https://www.npmjs.com/package/@leonardommello/copilot-mcp-server
- **MCP Documentation**: https://docs.anthropic.com/en/docs/claude-code/mcp
- **AGENTS.md**: Complete MCP documentation in this workspace

### Support
- Check AGENTS.md for detailed configuration
- Review .claude/mcp.json for current setup
- Restart Claude Code after configuration changes
- Verify authentication for Firebase and GitHub

---

**Status**: 🟢 All 4 MCPs configured and ready for use

*Last Verified: 2025-11-13*
