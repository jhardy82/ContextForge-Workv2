# MCP Best Practices for Agent/Copilot Instructions

**Version**: 1.0.0
**Created**: 2025-11-16
**Authority**: ContextForge Work | MCP Ecosystem Research
**Status**: Production Guidance

---

## Executive Summary

This document provides comprehensive best practices for documenting Model Context Protocol (MCP) tools in agent instruction files, enabling AI assistants to effectively discover, invoke, and fall back gracefully when MCP tools are unavailable.

**Key Objectives**:
1. Enable AI assistants to discover and understand MCP tool capabilities
2. Provide clear invocation patterns with proper parameter usage
3. Define graceful degradation when MCP tools are unavailable
4. Establish health check and readiness verification procedures
5. Document error handling patterns for MCP tool failures

---

## 0. Transport Policy: STDIO-first, HTTP as Fallback

MCP transport selection directly impacts reliability, latency, and developer ergonomics. Adopt a clear, enforced transport policy:

**Policy**:
- STDIO-first for MCP tool invocation in local/dev and editor-integrated workflows (e.g., VS Code)
- HTTP(S) fallback only when STDIO is not available or when cross-host/network access is explicitly required
- Always record the chosen transport in session evidence and note fallback rationale

**Why STDIO-first**:
- Lower latency and overhead (no HTTP stack, fewer moving parts)
- Robust editor integration (stable IO streams, fewer port conflicts)
- Easier local composition and multiplexing in multi-tool sessions

**When HTTP is Appropriate**:
- Remote MCP servers accessed over the network
- Containerized or platform services where port exposure is required
- Zero-trust boundaries where HTTP gateways/proxies enforce policy

### 0.1 Transport Decision Matrix

| Context | Recommended Transport | Notes |
|--------|------------------------|-------|
| VS Code local development | STDIO | Preferred for reliability and speed |
| Local automation scripts | STDIO | Use a stdio harness for health and ping |
| Remote service (same VPC) | HTTP(S) | Ensure liveness/readiness endpoints |
| Cross-org/network boundary | HTTP(S) | Include auth, TLS, rate limits |

### 0.2 Transport Readiness & Health

Perform a quick readiness check before invoking tools, aligned to transport:

```ts
// Pseudocode: transport-aware health check
async function ensureMCPReady(transport: 'stdio'|'http', client: MCPClient) {
  if (transport === 'stdio') {
    // 1) Spawn stdio process and perform initialize/ping handshake
    await client.initialize();
    const ok = await client.ping?.();
    if (!ok) throw new Error('STDIO MCP ping failed');
  } else {
    // 2) Call health endpoints for HTTP transports
    const health = await fetch(client.baseUrl + '/api/health').then(r => r.json());
    if (health.status !== 'ok') throw new Error('HTTP MCP unhealthy');
  }
}
```

For local testing and CI, prefer a stdio harness to validate the handshake and basic request/response loop. See `python/src/mcp_stdio_harness/` for patterns and tests you can adapt.

### 0.3 Example Invocation Patterns

```yaml
# STDIO (preferred): VS Code / local tool runner
transport: stdio
command: "node"
args:
  - "./dist/server.js"   # your MCP server entry
environment:
  MCP_LOG_LEVEL: info

# HTTP fallback: remote/containerized MCP
transport: http
baseUrl: "https://mcp.example.com"
healthEndpoints:
  live: "/health/live"
  ready: "/health/ready"
timeouts:
  requestMs: 15000
```

**Agent Guidance**:
1) Attempt STDIO first; if spawn/handshake fails, log the failure and fall back to HTTP (if configured)
2) On fallback, preserve parameters and semantics; record decision and rationale in the session evidence bundle
3) Use the same error handling patterns (timeouts, retries, circuit breakers) regardless of transport


## 1. MCP Tool Discovery and Documentation Structure

### 1.1 Tool Reference Format

**Recommended Structure**:

```markdown
## Tool Reference

```yaml
tool_name: "mcp-server-name.tool_name"     # Full qualified tool name
purpose: "Brief description of what the tool does"
when_to_use: "Specific triggers or scenarios"
required_parameters:
  - parameter_name: "Description and type"
optional_parameters:
  - parameter_name: "Description and default value"
returns: "Expected return type and structure"
```

**Example** (from vibe-check-mcp):

```yaml
vibe_check: "vibe-check-mcp.vibe_check"
purpose: "Challenge assumptions, prevent tunnel vision via metacognitive analysis"
when_to_use: "Phase transitions, complex reasoning, high-impact changes"
required_parameters:
  - goal: "Original user request (string)"
  - plan: "Detailed implementation plan with phase context (string)"
optional_parameters:
  - userPrompt: "Original user prompt for context (string)"
  - taskContext: "Additional task/project context (string)"
  - sessionId: "Session identifier for tracking (string)"
  - uncertainties: "Array of uncertainty descriptions (string[])"
  - modelOverride: "Custom model configuration (object)"
returns: "Metacognitive analysis with questions, risks, recommendations"
```

### 1.2 Tool Categorization

**Organize tools by domain and priority**:

```markdown
## MCP Tools by Category

### Critical Infrastructure (Always Available)
- `vibe-check-mcp/constitution_check` - Session integrity validation
- `taskman-typescript/task_create` - Task management operations
- `digitarald.agent-memory/memory` - Knowledge persistence

### Strategic Operations (Phase-Specific)
- `vibe-check-mcp/vibe_check` - Metacognitive checkpoints
- `SeqThinking/sequential_thinking` - Complex reasoning chains
- `SeqThinking/branched_thinking` - Multi-path analysis

### Development Support (Context-Aware)
- `context7/resolve_library_id` - Library documentation lookup
- `context7/get_library_docs` - Retrieve library documentation
- `microsoft-docs/microsoft_docs_search` - Microsoft documentation search
```

---

## 2. MCP-First, CLI Fallback Pattern

### 2.1 Decision Tree Template

```markdown
## Task Execution Decision Tree

1. **Check MCP Tool Availability**
   - Use MCP tool if available (preferred)
   - Document tool invocation with parameters
   - Capture output for evidence bundle

2. **Fallback to CLI (If MCP Unavailable)**
   - Use `cf_cli.py` or equivalent CLI command
   - Log fallback decision with rationale
   - Maintain same parameter structure

3. **Document Choice**
   - Record which method was used
   - Note any differences in capabilities
   - Flag for future MCP migration if using CLI
```

### 2.2 Implementation Example

**Good Pattern** (from copilot-instructions.md):

```markdown
### Create Task (TaskMan-v2)

**MCP First (Preferred in VS Code)**:
```yaml
tool: taskman-typescript.task_create
parameters:
  title: "Implement JWT authentication"
  priority: "high"
  work_type: "feature"
  status: "pending"
```

**CLI Fallback (When MCP Unavailable)**:
```bash
python cf_cli.py task create \
  --title "Implement JWT authentication" \
  --priority high \
  --work-type feature \
  --status pending
```

**Decision Logic**:
- Use MCP if available in VS Code tool palette
- Fall back to CLI if MCP server not running
- Log which method was used for audit trail
```

### 2.3 Anti-Pattern (Poor Documentation)

❌ **Avoid This**:

```markdown
## Create Task

Use the TaskMan MCP tool to create tasks.

# Example
taskman.create_task("title", "description")
```

**Problems**:
- No clear tool reference (missing server prefix)
- No CLI fallback pattern
- Missing parameter structure
- No guidance on when to use
- No error handling

---

## 3. Tool Invocation Patterns

### 3.1 Required vs Optional Parameters

**Clear Parameter Documentation**:

```markdown
### Tool: vibe-check-mcp.vibe_check

**Required Parameters** (MUST provide):
- `goal` (string): Original user request or objective
- `plan` (string): Detailed implementation plan with phase context

**Optional Parameters** (provide when relevant):
- `userPrompt` (string): Original user prompt for additional context
- `taskContext` (string): Project ID, phase, or environmental context
- `sessionId` (string): Session identifier for tracking
- `uncertainties` (string[]): List of specific uncertainties or risks
- `modelOverride` (object): Custom model configuration if needed

**Do NOT include unsupported parameters** - Extra keys trigger schema validation failures.

**Example Invocation**:
```typescript
// Minimal invocation
vibe_check({
  goal: "Implement authentication system",
  plan: "Phase: Implementation | Steps: 1) Design schema 2) Implement API 3) Add tests"
})

// Enhanced invocation
vibe_check({
  goal: "Implement authentication system",
  plan: "Phase: Implementation | Constitution: No external calls | Steps: ...",
  sessionId: "contextforge-work-20251116",
  taskContext: "project_id=P-CFWORK-001; phase=implementation",
  uncertainties: ["Token expiration strategy unclear", "Password reset flow needs validation"]
})
```
```

### 3.2 Schema Validation Guidance

```markdown
## Schema Compliance

**Critical Requirements**:
1. **Only use documented parameters** - Do not add custom fields
2. **Match types exactly** - String for strings, arrays for arrays
3. **Provide required fields** - Missing required params cause failures
4. **Check for schema updates** - Refer to `VibeCheck-Schema-Reference.*.md` when uncertain

**Validation Failure Example**:
```json
{
  "error": "Invalid parameters",
  "details": "Unexpected property 'phase' - use plan or taskContext instead"
}
```

**Resolution**: Embed phase context in the `plan` field or use `taskContext` parameter.
```

---

## 4. Error Handling and Graceful Degradation

### 4.1 MCP Tool Unavailability Pattern

```markdown
## Handling MCP Tool Unavailability

### Detection Pattern
```python
try:
    # Attempt MCP tool invocation
    result = mcp_tool.invoke(parameters)
    log_tool_usage("mcp", tool_name, result)
except ToolUnavailableError:
    # Log degradation
    logger.warning(f"MCP tool {tool_name} unavailable, falling back to CLI")

    # Execute CLI fallback
    result = cli_fallback(parameters)
    log_tool_usage("cli", tool_name, result)
except ToolError as e:
    # Log error details
    logger.error(f"MCP tool {tool_name} failed: {e}")

    # Attempt recovery or fallback
    result = handle_tool_failure(tool_name, parameters, e)
```

### Agent Instruction
```markdown
**When MCP Tool Unavailable**:
1. Log the unavailability event
2. Execute CLI fallback with same parameters
3. Document the fallback choice in session log
4. Flag for follow-up: "Consider MCP server health check"
```
```

### 4.2 Timeout and Circuit Breaker Patterns

```markdown
## Timeout Configuration

**Recommended Timeouts by Tool Category**:

| Tool Category | Timeout | Rationale |
|--------------|---------|-----------|
| Health checks | 5s | Fast feedback for readiness |
| Task operations | 15s | CRUD operations with validation |
| Database queries | 60s | Complex queries with joins |
| Library resolution | 10s | Context7 resolution (avg 100ms) |
| Document retrieval | 20s | Context7 retrieval (avg 200ms) |
| Memory operations | 25s | Knowledge graph searches |

**Circuit Breaker Pattern** (TypeScript Example):
```typescript
import CircuitBreaker from 'opossum';

const breaker = new CircuitBreaker(
  async (config) => this.client.request(config),
  {
    timeout: 30000,               // Request timeout
    errorThresholdPercentage: 50, // Open at 50% failure rate
    resetTimeout: 30000,          // Try again after 30s
    volumeThreshold: 10,          // Min requests before calculation
  }
);

// Log circuit state changes
breaker.on('open', () => {
  auditLog({
    operation: 'circuit_breaker',
    result: 'opened',
    details: { message: 'MCP service degraded' }
  });
});
```

**Agent Guidance**:
- Respect timeout values when invoking tools
- Document timeout extensions in ADR
- Log circuit breaker state changes
- Implement exponential backoff for retries
```

---

## 5. Health Monitoring and Readiness Checks

### 5.1 Startup Validation Template

```markdown
## MCP Server Health Check Protocol

### Pre-Invocation Health Check

**Before invoking MCP tools**:
1. Verify MCP server is running
2. Check health endpoint status
3. Validate required services are ready
4. Confirm configuration is valid

**Health Check Example**:
```typescript
async function validateMCPServerHealth() {
  try {
    // 1. Verify server connectivity
    const health = await mcpClient.health();
    if (health.status !== 'ok') {
      throw new Error(`MCP server unhealthy: ${health.message}`);
    }

    // 2. Validate backend connectivity (if applicable)
    const backendHealth = await backendClient.health();
    if (backendHealth.status !== 'ok') {
      throw new Error(`Backend unhealthy: ${backendHealth.message}`);
    }

    // 3. Test database connectivity (if direct access)
    // await db.ping();

    logger.info('MCP server health check passed');
    return true;
  } catch (error) {
    logger.error('MCP server health check failed:', error);
    return false;
  }
}
```

**Agent Instruction**:
- Run health check during session initialization
- Re-check health after prolonged idle periods
- Log health status in session evidence bundle
```

### 5.2 Health Endpoint Standards

**Kubernetes-Compatible Health Probes**:

```markdown
## Health Probe Types

### Liveness Probe (`/health/live`)
**Purpose**: Is the process alive and responsive?
**Should Always Pass**: Unless process is completely hung
**Kubernetes Action**: Restart pod if fails

### Readiness Probe (`/health/ready`)
**Purpose**: Can the service accept traffic?
**May Fail**: When dependencies are down or initializing
**Kubernetes Action**: Stop routing traffic until passes

### Startup Probe (`/health/startup`)
**Purpose**: Has initialization completed?
**Used During**: Initial container startup
**Kubernetes Action**: Allow time for startup before liveness checks

**Response Format**:
```json
{
  "status": "ok" | "degraded" | "down",
  "timestamp": "2025-11-16T10:30:00.000Z",
  "uptime": 3600.5,
  "checks": {
    "startup": {
      "status": "pass",
      "output": "Complete"
    },
    "memory": {
      "status": "pass",
      "output": "128.50MB / 256.00MB (50.2%)",
      "observedValue": 50.2,
      "observedUnit": "percent"
    },
    "backend": {
      "status": "pass",
      "output": "Responsive in 45ms"
    }
  }
}
```
```

---

## 6. Resource Patterns (URIs, Completion, Templates)

### 6.1 Resource URI Patterns

```markdown
## MCP Resource URIs

**URI Structure**:
```
mcp://{server-name}/{resource-type}/{resource-id}
```

**Examples**:
- `mcp://taskman/project/P-CFWORK-001` - Project resource
- `mcp://taskman/task/TASK-001` - Task resource
- `mcp://context7/library/pytest` - Library documentation
- `mcp://memory/entity/person-james-hardy` - Knowledge entity

**Resource Operations**:
```typescript
// Read resource
const project = await mcpClient.readResource('mcp://taskman/project/P-CFWORK-001');

// List resources
const tasks = await mcpClient.listResources('mcp://taskman/task/*');

// Subscribe to resource changes
mcpClient.subscribeResource('mcp://taskman/task/TASK-001', (change) => {
  console.log('Task updated:', change);
});
```
```

### 6.2 Completion and Templates

```markdown
## MCP Completion Support

**Completion Types**:
1. **Parameter Completion**: Suggest valid parameter values
2. **Resource Completion**: Suggest available resources
3. **Template Completion**: Provide common usage patterns

**Example** (Task Creation Completion):
```json
{
  "type": "completion",
  "context": "task_create",
  "suggestions": [
    {
      "label": "feature-task",
      "description": "Create feature development task",
      "template": {
        "title": "Implement ${1:feature-name}",
        "work_type": "feature",
        "priority": "medium",
        "status": "pending",
        "description": "${2:Feature description}"
      }
    },
    {
      "label": "bugfix-task",
      "description": "Create bug fix task",
      "template": {
        "title": "Fix ${1:bug-description}",
        "work_type": "bugfix",
        "priority": "high",
        "status": "pending",
        "description": "${2:Bug details and reproduction steps}"
      }
    }
  ]
}
```
```

---

## 7. Comparison: Good vs Poor MCP Documentation

### 7.1 Example: Task Management

#### ❌ Poor Documentation

```markdown
## Task Management

Use TaskMan MCP to manage tasks.

Tools:
- create_task
- update_task
- delete_task

Example:
```
taskman.create_task(title="New Task")
```
```

**Problems**:
- No server prefix in tool names
- Missing parameter specifications
- No CLI fallback guidance
- No error handling patterns
- No when-to-use triggers
- No health check requirements

#### ✅ Good Documentation

```markdown
## Task Management (TaskMan-v2 MCP)

### Tool Reference

```yaml
tools:
  task_create: "taskman-typescript.task_create"
  task_update: "taskman-typescript.task_update"
  task_close: "taskman-typescript.task_close"
  task_list: "taskman-typescript.task_list"
```

### When to Use
- Task lifecycle management (create, update, complete)
- Project and sprint task organization
- Progress tracking and status transitions
- Task dependency and relationship management

### MCP-First Pattern

**Create Task** (Preferred):
```yaml
tool: taskman-typescript.task_create
required_parameters:
  title: "Task title (string)"
  priority: "low | medium | high | critical"
optional_parameters:
  description: "Detailed task description"
  work_type: "feature | bugfix | research | documentation"
  status: "pending (default) | in_progress | completed"
  project_id: "Associated project ID"
  assignee: "Task assignee username"
```

**CLI Fallback** (When MCP Unavailable):
```bash
python cf_cli.py task create \
  --title "Task title" \
  --priority medium \
  --description "Task description" \
  --work-type feature \
  --status pending
```

### Health Check Requirements
```typescript
// Verify TaskMan MCP availability before bulk operations
const health = await mcpClient.health('taskman-typescript');
if (health.status !== 'ok') {
  logger.warning('TaskMan MCP unavailable, using CLI fallback');
  // Use CLI commands instead
}
```

### Error Handling
```typescript
try {
  const task = await taskman.task_create({
    title: "Implement authentication",
    priority: "high"
  });
  logger.info('Task created via MCP:', task.id);
} catch (ToolUnavailableError) {
  logger.warning('MCP unavailable, falling back to CLI');
  const result = exec(`python cf_cli.py task create --title "Implement authentication" --priority high`);
  logger.info('Task created via CLI:', result);
} catch (ToolError as e) {
  logger.error('Task creation failed:', e);
  throw new Error(`Unable to create task: ${e.message}`);
}
```

### Evidence Logging
- Log tool invocation method (MCP or CLI)
- Capture task ID and creation timestamp
- Document parameter values used
- Store result in evidence bundle with SHA-256 hash
```

---

## 8. Agent Instruction Template

### 8.1 Complete MCP Tool Section Template

```markdown
---
applyTo: "{scope}"
description: "{MCP server name} integration guidance"
---

# {MCP Server Name} Integration

## Overview
{Brief description of MCP server purpose and capabilities}

## Tool Reference

```yaml
server_name: "{mcp-server-prefix}"
tools:
  {tool_name}: "{mcp-server-prefix}.{tool_name}"
    purpose: "{What the tool does}"
    required_parameters:
      - {param}: "{Description and type}"
    optional_parameters:
      - {param}: "{Description and default}"
    returns: "{Return type and structure}"
```

## When to Use
- {Trigger condition 1}
- {Trigger condition 2}
- {Trigger condition 3}

## Invocation Patterns

### {Tool Name 1}

**MCP First (Preferred)**:
```yaml
tool: {mcp-server-prefix}.{tool_name}
parameters:
  {required_param}: "{value}"
  {optional_param}: "{value}"
```

**CLI Fallback** (When MCP Unavailable):
```bash
{cli_command} {tool_name} \
  --{param1} {value1} \
  --{param2} {value2}
```

**Decision Logic**:
- Use MCP if server is running and healthy
- Fall back to CLI if MCP unavailable
- Log which method was used
- Document any capability differences

## Health Check Requirements

**Pre-Invocation Check**:
```typescript
const health = await mcpClient.health('{mcp-server-prefix}');
if (health.status !== 'ok') {
  // Use CLI fallback or fail gracefully
}
```

**Health Endpoint**: `{health_endpoint_url}`
**Expected Response Time**: `{expected_ms}ms`
**Circuit Breaker Threshold**: `{threshold}% failure rate`

## Error Handling

```typescript
try {
  const result = await mcpTool.invoke(parameters);
  logToolUsage('mcp', toolName, result);
} catch (ToolUnavailableError) {
  logger.warning('MCP tool unavailable, using CLI fallback');
  result = cliCommand(parameters);
  logToolUsage('cli', toolName, result);
} catch (TimeoutError) {
  logger.error('MCP tool timeout, retrying with extended timeout');
  result = await retryWithBackoff(mcpTool, parameters);
} catch (ToolError as e) {
  logger.error('MCP tool failed:', e);
  throw new Error(`Tool invocation failed: ${e.message}`);
}
```

## Configuration

**Environment Variables**:
```bash
{ENV_VAR_1}={default_value}  # {Description}
{ENV_VAR_2}={default_value}  # {Description}
```

**Timeout Settings**:
- Connection timeout: `{value}s`
- Operation timeout: `{value}s`
- Health check timeout: `{value}s`

## Evidence Logging

**Mandatory Events**:
- `tool_invocation` - Log tool name, parameters, method (MCP/CLI)
- `tool_result` - Log result summary, execution time
- `tool_fallback` - Log fallback decision and rationale
- `tool_error` - Log error details and recovery actions

## Anti-Patterns

❌ **Avoid**:
- Invoking tools without health check for critical operations
- Missing CLI fallback implementation
- Hard-coding timeouts without configuration
- Ignoring tool unavailability errors
- Failing to log tool usage method

✅ **Prefer**:
- Health check before bulk operations
- Graceful degradation to CLI when needed
- Configurable timeout values
- Comprehensive error handling
- Detailed logging for audit trail

---

**For detailed {MCP server name} documentation, refer to**: `{reference_docs_path}`
```

---

## 9. Implementation Checklist

### 9.1 For Each MCP Tool Documentation

- [ ] **Tool Reference Section**
  - [ ] Full qualified tool name (server-prefix.tool-name)
  - [ ] Purpose and description
  - [ ] When-to-use triggers clearly defined
  - [ ] Required parameters with types
  - [ ] Optional parameters with defaults
  - [ ] Return type and structure

- [ ] **Invocation Patterns**
  - [ ] MCP invocation example with all parameters
  - [ ] CLI fallback command with equivalent parameters
  - [ ] Decision logic for choosing MCP vs CLI
  - [ ] Parameter mapping between MCP and CLI

- [ ] **Health and Readiness**
  - [ ] Health check endpoint documented
  - [ ] Pre-invocation health check pattern
  - [ ] Expected response times
  - [ ] Graceful degradation strategy

- [ ] **Error Handling**
  - [ ] Tool unavailability handling
  - [ ] Timeout error recovery
  - [ ] Circuit breaker pattern
  - [ ] Retry with exponential backoff

- [ ] **Evidence and Logging**
  - [ ] Tool invocation logging
  - [ ] Method documentation (MCP vs CLI)
  - [ ] Result capture for evidence bundle
  - [ ] Failure logging with recovery actions

- [ ] **Configuration**
  - [ ] Environment variables documented
  - [ ] Timeout settings specified
  - [ ] Configuration file locations
  - [ ] Override patterns explained

---

## 10. References and Resources

### 10.1 Codebase Examples

**Excellent MCP Documentation**:
- `.github/instructions/vibe-check-mcp-integration.instructions.md` - Comprehensive workflow integration
- `.github/instructions/context7-mcp.instructions.md` - Auto-invoke patterns with research validation
- `.github/instructions/agent-core.instructions.md` - Tool preference hierarchy and orchestration

**MCP Server Implementations**:
- `TaskMan-v2/mcp-server-ts/` - TypeScript MCP with health checks, circuit breakers
- `TaskMan-v2/mcp-server-ts/src/infrastructure/health.ts` - Health check service implementation
- `TaskMan-v2/mcp-server-ts/src/backend/client-with-circuit-breaker.ts` - Circuit breaker pattern

**Documentation Standards**:
- `docs/technical-standards/MCP-Ecosystem-Documentation-Enhancement.md` - Operational guidance
- `docs/taskman-mcp-v2-improvement-recommendations.md` - Stability and enhancement patterns

### 10.2 External Resources

**MCP Specification**:
- Model Context Protocol specification (external)
- MCP SDK documentation (`@modelcontextprotocol/sdk`)
- VS Code MCP extension integration patterns

**Best Practices**:
- Kubernetes health probe patterns (liveness, readiness, startup)
- Circuit breaker patterns (opossum library)
- Exponential backoff algorithms
- Structured logging with context (pino library)

---

## 11. Summary: Key Takeaways

### For AI Assistants

1. **Always check MCP tool availability** before invoking
2. **Use MCP first, CLI fallback** pattern consistently
3. **Document which method was used** in evidence logs
4. **Handle errors gracefully** with circuit breakers and retries
5. **Verify health** before bulk operations or critical workflows
6. **Log all decisions** including fallback rationale

### For Instruction Authors

1. **Full qualified tool names** (server-prefix.tool-name)
2. **Clear parameter specifications** with types and defaults
3. **MCP and CLI examples** side-by-side
4. **Health check patterns** included
5. **Error handling templates** provided
6. **Evidence logging requirements** explicit

### For System Architects

1. **Health endpoints** for all MCP servers
2. **Circuit breakers** to prevent cascade failures
3. **Timeout configurations** based on performance baselines
4. **Graceful degradation** strategies designed in
5. **Observability** with structured logging and metrics
6. **Documentation** kept in sync with implementations

---

**This guidance enables AI assistants to effectively leverage MCP tools while maintaining robust fallback strategies and comprehensive observability.**
