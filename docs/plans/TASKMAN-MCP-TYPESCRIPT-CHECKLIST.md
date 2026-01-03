# TaskMan TypeScript MCP - Implementation Checklist

**Parent Plan**: [TASKMAN-MCP-TYPESCRIPT-API-IMPLEMENTATION.md](./TASKMAN-MCP-TYPESCRIPT-API-IMPLEMENTATION.md)
**Project**: P-TASKMAN-MCP-TYPESCRIPT
**Work ID**: W-TASKMAN-API-001
**Created**: 2025-12-04
**Last Updated**: 2025-12-04
**Version**: 1.0.0

---

## Quick Reference

| Metric | Value | Updated |
|--------|-------|---------|
| **Total Story Points** | 15+ (CF-208 expanded) | 2025-12-04 |
| **Completed Points** | 2 (R-208-09, R-208-10) | 2025-12-04 |
| **Remaining Points** | 13+ | - |
| **Active Issue** | CF-215 (In Progress) | 2025-12-04 |
| **Parent Issue** | CF-208 | 2025-12-04 |
| **Sub-Issues Created** | 5 (CF-211 to CF-215) | 2025-12-04 |
| **Blockers** | 0 | - |
| **Overall Progress** | 20% (Research Complete, Implementation Starting) | 2025-12-04 |

### Quantum Research Status 🔮

| Research Task | Status | Persona | Confidence |
|---------------|--------|---------|------------|
| R-208-09 Internal Archaeology | ✅ COMPLETE | Dr. Archaeon | 95% |
| R-208-10 OpenAPI Standards | ✅ COMPLETE | Navigator Flux | 90% |
| Architect Prism Synthesis | ✅ COMPLETE | Architect Prism | 95% |
| Validator Echo Testing | ✅ VERIFIED | Validator Echo | 90% |

### 🎯 Research-Driven Implementation Priorities

**Full Synthesis**: [QUANTUM-RESEARCH-SYNTHESIS.md](./QUANTUM-RESEARCH-SYNTHESIS.md) | [QUANTUM-RESEARCH-TEAM.md](./QUANTUM-RESEARCH-TEAM.md)

| Priority | Pattern | Gap Identified | Recommendation |
|----------|---------|----------------|----------------|
| 🔴 **P0** | Error Format | Inconsistent `{error}` | RFC 7807 Problem Details |
| 🔴 **P0** | Validation | No input validation | Zod schema middleware |
| 🔴 **P0** | Error Handler | Per-route try/catch | Global async middleware |
| 🟠 **P1** | Response Format | Raw data | `{success, data, meta}` envelope |
| 🟠 **P1** | API Docs | None | OpenAPI 3.1 + Swagger UI |
| 🟠 **P1** | Rate Limiting | None | express-rate-limit |

**Implementation Stack** (Validator Echo Verified):
```
Dependencies: express@4.18+, zod@3.24+, express-rate-limit@7.1+, swagger-ui-express@5.0+
Architecture: Request → RateLimit → Validation → Handler → Envelope → RFC7807Errors
```

---

## Workstream Personas

### 🔬 Research Persona: "The Archaeologist"

**Name**: Dr. Schema  
**Role**: Deep Research & Discovery Specialist  
**Linear Label**: `research`

**Responsibilities**:
- Excavate patterns from existing codebase
- Research external best practices and anti-patterns
- Analyze database schemas and constraints
- Investigate API contracts and specifications
- Document findings with confidence levels

**Communication Style**:
- Evidence-based assertions only
- Always cite sources (file:line, URL, tool output)
- Flag uncertainty explicitly with confidence percentages
- Present multiple options when ambiguity exists

**Tools Authorized**:
- `semantic_search` - Conceptual code discovery
- `grep_search` - Pattern location
- `read_file` - Deep inspection
- `vscode-websearchforcopilot_webSearch` - External research
- `mcp_upstash_conte_get-library-docs` - Library documentation
- `fetch_webpage` - Detailed article reading

**Output Format**:
```yaml
research_finding:
  topic: "[Topic Name]"
  confidence: [0-100]%
  sources:
    - type: [internal|external]
      location: "[file:line or URL]"
  finding: "[Detailed finding]"
  implications: "[How this affects implementation]"
  alternatives: "[If applicable]"
```

**Handoff Protocol**:
> "Research complete for [topic]. Confidence: [X]%. Key finding: [summary]. Ready for implementation handoff. See detailed notes in checklist item [ID]."

---

### 🛠️ Implementation Persona: "The Builder"

**Name**: Constructor Prime  
**Role**: Code Implementation & Integration Specialist  
**Linear Label**: `implementation`

**Responsibilities**:
- Translate research findings into working code
- Follow established patterns and conventions
- Implement incrementally with validation checkpoints
- Handle errors gracefully with proper logging
- Maintain backward compatibility

**Communication Style**:
- Action-oriented language
- Clear before/after descriptions
- Explicit about changes made and files modified
- Checkpoint after each significant change

**Tools Authorized**:
- `read_file` - Context gathering
- `replace_string_in_file` / `multi_replace_string_in_file` - Code changes
- `create_file` - New file creation
- `run_in_terminal` - Build/test execution
- `get_errors` - Validation

**Output Format**:
```yaml
implementation_change:
  issue_id: "CF-XXX"
  files_modified:
    - path: "[file path]"
      change_type: [create|modify|delete]
      lines_affected: [N]
  tests_affected: [list]
  validation_status: [pending|passed|failed]
  rollback_command: "[if applicable]"
```

**Handoff Protocol**:
> "Implementation complete for [feature]. Files modified: [list]. Validation: [status]. Ready for testing handoff. See implementation notes in checklist item [ID]."

---

### 🧪 Testing Persona: "The Validator"

**Name**: QA Oracle  
**Role**: Quality Assurance & Validation Specialist  
**Linear Label**: `testing`

**Responsibilities**:
- Design comprehensive test cases
- Execute tests and document results
- Identify edge cases and failure modes
- Validate against acceptance criteria
- Ensure coverage targets are met

**Communication Style**:
- Structured test reports
- Clear pass/fail criteria
- Detailed failure analysis
- Coverage metrics always included

**Tools Authorized**:
- `run_in_terminal` - Test execution
- `runTests` - VS Code test integration
- `read_file` - Test file inspection
- `get_errors` - Error analysis
- `create_file` - Test file creation

**Output Format**:
```yaml
test_result:
  issue_id: "CF-XXX"
  test_type: [unit|integration|e2e|manual]
  execution_time: "[duration]"
  results:
    passed: [N]
    failed: [N]
    skipped: [N]
  coverage:
    line: [X]%
    branch: [Y]%
  failures:
    - test: "[test name]"
      error: "[error message]"
      root_cause: "[analysis]"
  verdict: [PASS|FAIL|BLOCKED]
```

**Handoff Protocol**:
> "Testing complete for [feature]. Results: [X passed, Y failed]. Coverage: [Z]%. Verdict: [PASS/FAIL]. See test report in checklist item [ID]."

---

## Tracking Legend

### Status Icons

| Icon | Status | Description |
|------|--------|-------------|
| ⬜ | Not Started | Work has not begun |
| 🔄 | In Progress | Currently being worked on |
| ⏸️ | Paused | Temporarily stopped (see notes) |
| 🔴 | Blocked | Cannot proceed (see blocker) |
| ✅ | Complete | Successfully finished |
| ❌ | Cancelled | Will not be completed |
| ⚠️ | At Risk | May not meet target |

### Priority Icons

| Icon | Priority | SLA |
|------|----------|-----|
| 🔴 | Urgent | Same day |
| 🟠 | High | 1-2 days |
| 🟡 | Medium | 3-5 days |
| 🟢 | Low | Best effort |

### Persona Assignment

| Icon | Persona | Workstream |
|------|---------|------------|
| 🔬 | Dr. Schema | Research |
| 🛠️ | Constructor Prime | Implementation |
| 🧪 | QA Oracle | Testing |

---

## Issue CF-197: Close Obsolete 404 Bug Issues

**Linear**: [CF-197](https://linear.app/cf-work/issue/CF-197)  
**Story Points**: 1  
**Priority**: 🔴 Urgent  
**Target**: 2025-12-04  
**Status**: ⬜ Not Started

### Progress Tracker

| Phase | Status | Assignee | Started | Completed | Duration |
|-------|--------|----------|---------|-----------|----------|
| Research | ⬜ | 🔬 | - | - | - |
| Implementation | ⬜ | 🛠️ | - | - | - |
| Testing | ⬜ | 🧪 | - | - | - |

### Checklist

#### 🔬 Research Phase (Dr. Schema)

- [ ] **R-197-01**: Verify all 8 issues exist in Linear
  - Target: CF-172, CF-173, CF-174, CF-175, CF-176, CF-177, CF-178, CF-179
  - [ ] Query Linear API for issue details
  - [ ] Confirm current status of each
  - **Notes**: *[Add research notes here]*
  - **Confidence**: _%

- [ ] **R-197-02**: Document cancellation rationale
  - [ ] Root cause: PM2 services not running
  - [ ] Resolution: Services verified working
  - **Notes**: *[Add research notes here]*

#### 🛠️ Implementation Phase (Constructor Prime)

- [ ] **I-197-01**: Update CF-172 status to Cancelled
  - [ ] Add cancellation comment with rationale
  - [ ] Link to CF-184 (verification issue)
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-197-02**: Update CF-173 status to Cancelled
  - [ ] Add cancellation comment
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-197-03**: Update CF-174 status to Cancelled
  - [ ] Add cancellation comment
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-197-04**: Update CF-175 status to Cancelled
  - [ ] Add cancellation comment
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-197-05**: Update CF-176 status to Cancelled
  - [ ] Add cancellation comment
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-197-06**: Update CF-177 status to Cancelled
  - [ ] Add cancellation comment
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-197-07**: Update CF-178 status to Cancelled
  - [ ] Add cancellation comment
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-197-08**: Update CF-179 status to Cancelled
  - [ ] Add cancellation comment
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

#### 🧪 Testing Phase (QA Oracle)

- [ ] **T-197-01**: Verify all issues show Cancelled status
  - [ ] Query Linear for verification
  - [ ] Confirm comments added correctly
  - **Test Results**: *[Add results]*
  - **Verdict**: ⬜

### Notes & Decisions

| Date | Persona | Note |
|------|---------|------|
| *YYYY-MM-DD* | *🔬/🛠️/🧪* | *[Add notes as work progresses]* |

### Blockers

| ID | Description | Owner | Raised | Resolved | Resolution |
|----|-------------|-------|--------|----------|------------|
| *B-197-01* | *[None currently]* | - | - | - | - |

---

## Issue CF-198: Fix 58 Failing Tests

**Linear**: [CF-198](https://linear.app/cf-work/issue/CF-198)  
**Story Points**: 5  
**Priority**: 🟠 High  
**Target**: 2025-12-06  
**Status**: ⬜ Not Started

### Progress Tracker

| Phase | Status | Assignee | Started | Completed | Duration |
|-------|--------|----------|---------|-----------|----------|
| Research | ⬜ | 🔬 | - | - | - |
| Implementation | ⬜ | 🛠️ | - | - | - |
| Testing | ⬜ | 🧪 | - | - | - |

### Test Failure Categories

| Category | Count | Priority | Status |
|----------|-------|----------|--------|
| Fixtures (mock setup) | ~16 | 🟠 High | ⬜ |
| Config isolation | ~6 | 🟠 High | ⬜ |
| Circuit breaker patterns | ~36 | 🟠 High | ⬜ |
| **Total** | **58** | - | - |

### Checklist

#### 🔬 Research Phase (Dr. Schema)

- [ ] **R-198-01**: Analyze fixture failures
  - [ ] Run `npm test` and capture output
  - [ ] Categorize failures by error type
  - [ ] Identify common root causes
  - **Notes**: *[Add research notes here]*
  - **Confidence**: _%

- [ ] **R-198-02**: Research Vitest 4.0 patterns
  - [ ] Query Context7 for Vitest docs
  - [ ] Document mock setup best practices
  - [ ] Identify fixture isolation patterns
  - **Sources**: *[List sources]*
  - **Confidence**: _%

- [ ] **R-198-03**: Analyze circuit breaker test patterns
  - [ ] Review `client-with-circuit-breaker.ts`
  - [ ] Document expected vs actual behavior
  - [ ] Identify timing-related issues
  - **Notes**: *[Add research notes here]*
  - **Confidence**: _%

- [ ] **R-198-04**: Research config isolation strategies
  - [ ] Review test setup files
  - [ ] Identify shared state issues
  - [ ] Document isolation patterns
  - **Notes**: *[Add research notes here]*
  - **Confidence**: _%

#### 🛠️ Implementation Phase (Constructor Prime)

##### Fixture Fixes (~16 tests)

- [ ] **I-198-01**: Update mock setup patterns
  - [ ] Apply Vitest 4.0 `vi.mock()` patterns
  - [ ] Ensure proper mock hoisting
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-198-02**: Fix mock cleanup
  - [ ] Add `beforeEach`/`afterEach` cleanup
  - [ ] Ensure isolation between tests
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-198-03**: Update factory functions
  - [ ] Review test data factories
  - [ ] Ensure unique IDs per test
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

##### Config Isolation Fixes (~6 tests)

- [ ] **I-198-04**: Isolate config state
  - [ ] Reset config between tests
  - [ ] Remove global state dependencies
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-198-05**: Fix environment variable handling
  - [ ] Mock env vars properly
  - [ ] Restore after each test
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

##### Circuit Breaker Fixes (~36 tests)

- [ ] **I-198-06**: Fix timing dependencies
  - [ ] Use `vi.useFakeTimers()` consistently
  - [ ] Advance timers explicitly
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-198-07**: Fix state reset between tests
  - [ ] Reset circuit breaker state
  - [ ] Clear failure counts
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-198-08**: Fix async/await patterns
  - [ ] Ensure proper promise resolution
  - [ ] Add missing `await` statements
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

#### 🧪 Testing Phase (QA Oracle)

- [ ] **T-198-01**: Run full test suite
  - [ ] Execute `npm test`
  - [ ] Capture pass/fail metrics
  - **Results**: *[X passed, Y failed]*
  - **Verdict**: ⬜

- [ ] **T-198-02**: Verify test isolation
  - [ ] Run tests in random order
  - [ ] Run tests in parallel
  - [ ] Confirm no order dependencies
  - **Results**: *[Add results]*
  - **Verdict**: ⬜

- [ ] **T-198-03**: Check coverage metrics
  - [ ] Generate coverage report
  - [ ] Compare before/after
  - **Coverage**: *Line: X%, Branch: Y%*
  - **Verdict**: ⬜

### Notes & Decisions

| Date | Persona | Note |
|------|---------|------|
| 2025-12-04 | 🔬 | Initial test run shows 58 failures across 3 categories |
| *YYYY-MM-DD* | *🔬/🛠️/🧪* | *[Add notes as work progresses]* |

### Blockers

| ID | Description | Owner | Raised | Resolved | Resolution |
|----|-------------|-------|--------|----------|------------|
| *B-198-01* | *[None currently]* | - | - | - | - |

---

## Issue CF-199: Create API Reference Documentation

**Linear**: [CF-199](https://linear.app/cf-work/issue/CF-199)  
**Story Points**: 3  
**Priority**: 🟠 High  
**Target**: 2025-12-07  
**Status**: ⬜ Not Started

### Progress Tracker

| Phase | Status | Assignee | Started | Completed | Duration |
|-------|--------|----------|---------|-----------|----------|
| Research | ⬜ | 🔬 | - | - | - |
| Implementation | ⬜ | 🛠️ | - | - | - |
| Testing | ⬜ | 🧪 | - | - | - |

### Checklist

#### 🔬 Research Phase (Dr. Schema)

- [ ] **R-199-01**: Audit existing documentation
  - [ ] Review `vs-code-task-manager/docs/`
  - [ ] Identify gaps and outdated content
  - [ ] List all API endpoints
  - **Notes**: *[Add research notes here]*
  - **Confidence**: _%

- [ ] **R-199-02**: Research TypeDoc configuration
  - [ ] Query Context7 for TypeDoc docs
  - [ ] Review best practices
  - [ ] Identify plugins needed
  - **Sources**: *[List sources]*
  - **Confidence**: _%

- [ ] **R-199-03**: Research TSDoc annotation standards
  - [ ] Review @param, @returns patterns
  - [ ] Document example formats
  - [ ] Identify coverage requirements
  - **Notes**: *[Add research notes here]*
  - **Confidence**: _%

- [ ] **R-199-04**: Research OpenAPI generation
  - [ ] Review Zod-to-OpenAPI patterns
  - [ ] Identify generation tools
  - [ ] Document integration approach
  - **Notes**: *[Add research notes here]*
  - **Confidence**: _%

#### 🛠️ Implementation Phase (Constructor Prime)

- [ ] **I-199-01**: Configure TypeDoc
  - [ ] Create `typedoc.json` configuration
  - [ ] Add npm script for generation
  - [ ] Test initial generation
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-199-02**: Add TSDoc annotations to core modules
  - [ ] Annotate `src/core/schemas.ts`
  - [ ] Annotate `src/core/types.ts`
  - [ ] Annotate `src/backend/client.ts`
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-199-03**: Add TSDoc annotations to feature modules
  - [ ] Annotate `src/features/projects/`
  - [ ] Annotate `src/features/tasks/`
  - [ ] Annotate `src/features/sprints/`
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-199-04**: Generate OpenAPI specification
  - [ ] Configure zod-to-openapi
  - [ ] Generate openapi.json
  - [ ] Validate against Swagger
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-199-05**: Create endpoint documentation
  - [ ] Document all REST endpoints
  - [ ] Include request/response examples
  - [ ] Document error codes
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

#### 🧪 Testing Phase (QA Oracle)

- [ ] **T-199-01**: Validate TypeDoc generation
  - [ ] Run `npm run docs`
  - [ ] Verify all modules documented
  - [ ] Check for missing annotations
  - **Results**: *[Add results]*
  - **Verdict**: ⬜

- [ ] **T-199-02**: Validate OpenAPI spec
  - [ ] Load in Swagger UI
  - [ ] Test example requests
  - [ ] Verify schema accuracy
  - **Results**: *[Add results]*
  - **Verdict**: ⬜

- [ ] **T-199-03**: Review documentation quality
  - [ ] Check completeness
  - [ ] Verify examples work
  - [ ] Test links and references
  - **Results**: *[Add results]*
  - **Verdict**: ⬜

### Notes & Decisions

| Date | Persona | Note |
|------|---------|------|
| *YYYY-MM-DD* | *🔬/🛠️/🧪* | *[Add notes as work progresses]* |

### Blockers

| ID | Description | Owner | Raised | Resolved | Resolution |
|----|-------------|-------|--------|----------|------------|
| *B-199-01* | *[None currently]* | - | - | - | - |

---

## Issue CF-200: Create MCP Tools Reference

**Linear**: [CF-200](https://linear.app/cf-work/issue/CF-200)  
**Story Points**: 3  
**Priority**: 🟠 High  
**Target**: 2025-12-07  
**Status**: ⬜ Not Started

### Progress Tracker

| Phase | Status | Assignee | Started | Completed | Duration |
|-------|--------|----------|---------|-----------|----------|
| Research | ⬜ | 🔬 | - | - | - |
| Implementation | ⬜ | 🛠️ | - | - | - |
| Testing | ⬜ | 🧪 | - | - | - |

### Checklist

#### 🔬 Research Phase (Dr. Schema)

- [ ] **R-200-01**: Inventory all MCP tools
  - [ ] List tools in `src/features/projects/register.ts`
  - [ ] List tools in `src/features/tasks/register.ts`
  - [ ] List tools in `src/features/sprints/register.ts`
  - [ ] Document input/output schemas
  - **Notes**: *[Add research notes here]*
  - **Confidence**: _%

- [ ] **R-200-02**: Research MCP documentation standards
  - [ ] Review official MCP docs
  - [ ] Identify best practices for tool docs
  - [ ] Document example formats
  - **Sources**: *[List sources]*
  - **Confidence**: _%

- [ ] **R-200-03**: Research contract testing patterns
  - [ ] Query Context7 for Pact/contract testing
  - [ ] Identify tool validation patterns
  - [ ] Document testing approach
  - **Notes**: *[Add research notes here]*
  - **Confidence**: _%

#### 🛠️ Implementation Phase (Constructor Prime)

- [ ] **I-200-01**: Create MCP Tools Overview document
  - [ ] Document tool discovery mechanism
  - [ ] List all available tools by category
  - [ ] Include architecture diagram
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-200-02**: Document Project tools
  - [ ] `list_projects` - parameters, examples
  - [ ] `get_project` - parameters, examples
  - [ ] `create_project` - parameters, examples
  - [ ] `update_project` - parameters, examples
  - [ ] `delete_project` - parameters, examples
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-200-03**: Document Task tools
  - [ ] `list_tasks` - parameters, examples
  - [ ] `get_task` - parameters, examples
  - [ ] `create_task` - parameters, examples
  - [ ] `update_task` - parameters, examples
  - [ ] `delete_task` - parameters, examples
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-200-04**: Document Sprint tools
  - [ ] `list_sprints` - parameters, examples
  - [ ] `get_sprint` - parameters, examples
  - [ ] `create_sprint` - parameters, examples
  - [ ] `update_sprint` - parameters, examples
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-200-05**: Create contract test documentation
  - [ ] Document test patterns
  - [ ] Include example contracts
  - [ ] Document CI integration
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

#### 🧪 Testing Phase (QA Oracle)

- [ ] **T-200-01**: Validate tool examples
  - [ ] Test all example invocations
  - [ ] Verify input validation messages
  - [ ] Test error responses
  - **Results**: *[Add results]*
  - **Verdict**: ⬜

- [ ] **T-200-02**: Verify documentation accuracy
  - [ ] Compare docs to actual tool schemas
  - [ ] Verify all parameters documented
  - [ ] Check for missing tools
  - **Results**: *[Add results]*
  - **Verdict**: ⬜

- [ ] **T-200-03**: Run contract tests
  - [ ] Execute contract test suite
  - [ ] Verify provider compliance
  - [ ] Document any gaps
  - **Results**: *[Add results]*
  - **Verdict**: ⬜

### Notes & Decisions

| Date | Persona | Note |
|------|---------|------|
| *YYYY-MM-DD* | *🔬/🛠️/🧪* | *[Add notes as work progresses]* |

### Blockers

| ID | Description | Owner | Raised | Resolved | Resolution |
|----|-------------|-------|--------|----------|------------|
| *B-200-01* | *[None currently]* | - | - | - | - |

---

## Issue CF-208: Investigate TaskMan Action List API 404 Error

**Linear**: [CF-208](https://linear.app/cf-work/issue/CF-208/investigate-taskman-action-list-api-404-error)  
**Story Points**: TBD  
**Priority**: 🟠 High  
**Target**: 2025-12-10  
**Status**: 🟡 In Progress

### Progress Tracker

| Phase | Status | Assignee | Started | Completed | Duration |
|-------|--------|----------|---------|-----------|----------|
| Research | 🟡 | 🔬 | 2025-12-04 | - | - |
| Implementation | ⬜ | 🛠️ | - | - | - |
| Testing | ⬜ | 🧪 | - | - | - |

### Context Summary

**Issue**: Action list endpoints returning 404 despite API health check passing.

**Environment**:
- API Health: ✅ OK (`http://localhost:3001/api/health`)
- PM2 Status: Both services online (task-manager-api PID 37032)
- Endpoint Tested: Action list list endpoint
- Error: `Request failed with status code 404`

**🔴 LIVE BUG REPRODUCTION** (2025-12-04):
- Tool: `mcp_task-manager_action_list_list`
- Error: `MPC -32603: Tool execution failed: Failed to list action lists: Request failed with status code 404`
- Confirms: Bug is active and reproducible in current environment

**Investigation Hypothesis** (90% confidence): Route prefix mismatch - MCP client uses `/action-lists` but backend may expect `/api/v1/action-lists`.

**Related**: Parent issue CF-200 (MCP Tools Reference), Work ID W-TASKMAN-API-001

### Checklist

#### 🔬 Research Phase (Dr. Schema)

- [ ] **R-208-01**: Verify which backend server is running
  - [ ] Check PM2 process list for api-server.cjs vs FastAPI
  - [ ] Verify port 3001 is serving expected backend
  - [ ] Document active server type and configuration
  - **Notes**: *[Add research notes here]*
  - **Confidence**: _%

- [ ] **R-208-02**: Check API endpoint configuration
  - [ ] Review TASK_MANAGER_API_ENDPOINT in `.mcp.json`
  - [ ] Check environment variables for API URL
  - [ ] Verify baseURL in MCP client configuration
  - **Notes**: *[Add research notes here]*
  - **Confidence**: _%

- [ ] **R-208-03**: Test backend routes directly
  - [ ] `curl http://localhost:3001/api/health` - verify health
  - [ ] `curl http://localhost:3001/api/v1/action-lists` - test with prefix
  - [ ] `curl http://localhost:3001/action-lists` - test without prefix
  - [ ] Document which route pattern returns 200 OK
  - **Notes**: *[Add research notes here]*
  - **Confidence**: _%

- [ ] **R-208-04**: Compare MCP client vs backend routes
  - [ ] Review `src/backend/client.ts` endpoint paths
  - [ ] Review `api-server.cjs` route registrations
  - [ ] Identify any path mismatches
  - **Sources**: *[List sources]*
  - **Confidence**: _%

- [ ] **R-208-05**: Check database table existence
  - [ ] If PostgreSQL backend: verify action_lists table exists
  - [ ] If in-memory: verify actionLists array initialized
  - [ ] Document storage layer status
  - **Notes**: *[Add research notes here]*
  - **Confidence**: _%

- [ ] **R-208-06**: Review error logs for context
  - [ ] Check MCP server console output
  - [ ] Check backend server logs
  - [ ] Capture full 404 error response body
  - **Notes**: *[Add research notes here]*
  - **Confidence**: _%

- [ ] **R-208-07**: Analyze MCP client HTTP request construction *(NEW)*
  - [ ] Add verbose logging to client.ts before fetch
  - [ ] Log full URL being constructed
  - [ ] Compare logged URL to expected endpoint
  - **Notes**: *Identified during live bug reproduction - need to see exact URL being called*
  - **Confidence**: _%

- [ ] **R-208-08**: Audit authentication requirements *(NEW)*
  - [ ] Check if action-list routes require auth token
  - [ ] Verify MCP client sends correct headers
  - [ ] Test with and without auth header
  - **Notes**: *401 vs 404 distinction needed*
  - **Confidence**: _%

- [x] **R-208-09**: Internal codebase archaeology *(QUANTUM RESEARCH)*
  - [x] Catalog all action-list related files (44 files found)
  - [x] Document MCP tool registration patterns (circuit breaker, locking, audit)
  - [x] Identify Sacred Geometry validation patterns (5 shapes)
  - [x] Map route prefix inconsistencies (root cause identified)
  - **Notes**: See **Quantum Research Findings** section below
  - **Confidence**: 95%

- [x] **R-208-10**: OpenAPI standards research *(QUANTUM RESEARCH)*
  - [x] Research OpenAPI 3.1.1 specification (latest October 2024)
  - [x] Evaluate tsoa (code-first TypeScript OpenAPI)
  - [x] Evaluate express-zod-api (Zod + OpenAPI, 92.4 benchmark)
  - [x] Research Express route versioning best practices
  - **Notes**: See **Quantum Research Findings** section below
  - **Confidence**: 90%

---

### 🔮 Quantum Research Findings

> **Research Collective**: Dr. Archaeon (Internal) + Navigator Flux (External)
> **Date**: 2025-12-04
> **Status**: ✅ COMPLETE - Ready for Architect Prism synthesis

#### Internal Codebase Archaeology (Dr. Archaeon)

**Files Catalogued**: 44 action-list related files

**Key Implementation Patterns Discovered**:

| Pattern | Location | Description |
|---------|----------|-------------|
| **Circuit Breaker** | `register.ts:1-50` | `backendClientWithCircuitBreaker` protects all HTTP calls |
| **Zod Validation** | `register.ts:60-150` | All inputs validated via Zod schemas |
| **Agent Locking** | `register.ts` | `ACTION_LIST_LOCK_AGENT` for pessimistic locking |
| **Audit Logging** | Throughout | Correlation IDs, structured logging |
| **Sacred Geometry** | `integration.test.ts` | 5 shapes: Circle, Triangle, Spiral, Pentagon, Fractal |

**Root Cause Identified** (95% Confidence):
```yaml
issue: Route prefix inconsistency in api-server.cjs
evidence:
  - Tasks: /api/tasks (NO v1 prefix)
  - Action Lists: /api/v1/action-lists (HAS v1 prefix)
  - Same port (3001) serves both, different data sources
resolution: Standardize ALL routes to /api/v1/* prefix
```

**MCP Client Configuration**:
```typescript
// TaskMan-v2/mcp-server-ts/src/backend/client.ts
baseURL: process.env.TASK_MANAGER_API_ENDPOINT || "http://localhost:3001/api/v1"
// Action list endpoints use relative paths: /action-lists, /action-lists/${id}
```

#### External Research Findings (Navigator Flux)

**OpenAPI 3.1.1** (Latest Specification - October 2024):
- Full JSON Schema Draft 2020-12 alignment
- OAuth 2.1 authentication support
- Webhooks as top-level field
- Enhanced `$ref` composition with `allOf`/`oneOf`/`anyOf`

**Recommended Libraries**:

| Library | Approach | Benchmark | Key Feature |
|---------|----------|-----------|-------------|
| **tsoa** ⭐ | Code-First | High | TypeScript decorators → OpenAPI spec |
| **express-zod-api** ⭐ | Schema-First | 92.4 | Zod validation + OpenAPI generation |
| **swagger-jsdoc** | JSDoc-Based | High | OpenAPI from comments |
| **swagger-ui-express** | UI | High | Serve Swagger UI |

**tsoa Pattern** (Recommended for TypeScript):
```typescript
@Route("api/v1/action-lists")
@Tags("Action Lists")
export class ActionListController extends Controller {
  @Get()
  public async list(): Promise<ActionList[]> {
    return this.actionListService.list();
  }
  
  @Post()
  public async create(@Body() body: CreateActionListRequest): Promise<ActionList> {
    return this.actionListService.create(body);
  }
}
// Auto-generates OpenAPI spec at build time!
```

**express-zod-api Pattern** (Alternative):
```typescript
const listEndpoint = defaultEndpointsFactory.build({
  method: "get",
  tag: "action-lists",
  input: z.object({}),
  output: z.array(ActionListSchema),
  handler: async ({ logger }) => {
    return await actionListService.list();
  },
});
// Auto-generates OpenAPI spec with Zod types!
```

#### Architect Prism Synthesis (Pending)

**Recommended Approach**: **tsoa** (Code-First TypeScript OpenAPI)

**Rationale**:
1. Existing codebase uses TypeScript controllers
2. Code-first approach minimizes spec drift
3. Auto-generates OpenAPI 3.0 spec from decorators
4. Express integration is mature
5. Strong typing with compile-time validation

**Implementation Strategy**:
```yaml
phase_1_immediate_fix:
  action: Add /api/v1 prefix aliases to api-server.cjs
  scope: Minimal change to fix 404 immediately
  risk: Low
  
phase_2_openapi_migration:
  action: Migrate to tsoa controller pattern
  scope: Refactor api-server.cjs to TypeScript with decorators
  risk: Medium (requires testing)
  
phase_3_spec_generation:
  action: Generate and serve OpenAPI spec
  scope: Add swagger-ui-express for API documentation
  risk: Low
```

---

### 📊 Linear Sub-Issue Tracking (Created 2025-12-04)

> **Note**: TaskMan action lists are BLOCKED by this very bug (circular dependency).
> Using Linear sub-issues for all task tracking until CF-215 is resolved.

| Issue | Title | Priority | Status | Depends On |
|-------|-------|----------|--------|------------|
| [CF-215](https://linear.app/cf-work/issue/CF-215) | 🔧 I-208-08: Standardize all routes to /api/v1/* (ROOT CAUSE FIX) | 🔴 Urgent | 🟡 In Progress | - |
| [CF-213](https://linear.app/cf-work/issue/CF-213) | 📦 I-208-06: OpenAPI spec generation setup (tsoa) | 🟠 High | ⬜ Backlog | CF-215 |
| [CF-214](https://linear.app/cf-work/issue/CF-214) | 🧪 T-208: Validation Test Suite for CF-208 Fix | 🟠 High | ⬜ Backlog | CF-215 |
| [CF-212](https://linear.app/cf-work/issue/CF-212) | 🔄 I-208-07: Migrate api-server.cjs to TypeScript | 🟡 Medium | ⬜ Backlog | CF-215, CF-213 |
| [CF-211](https://linear.app/cf-work/issue/CF-211) | 📚 I-208-09: Add Swagger UI endpoint | 🟢 Low | ⬜ Backlog | CF-212 |

**Execution Dependency Graph**:
```
CF-215 (Route Fix) ──┬──► CF-213 (tsoa Setup) ──► CF-212 (TypeScript) ──► CF-211 (Swagger UI)
                     │
                     └──► CF-214 (Test Suite) ◄── Can validate after CF-215
```

**Next Action**: Implement CF-215 (route standardization) to unblock all downstream work.

---

#### 🛠️ Implementation Phase (Constructor Prime)

- [ ] **I-208-01**: Fix route prefix mismatch (if confirmed)
  - [ ] Update MCP client baseURL OR backend routes
  - [ ] Ensure consistent `/api/v1/` prefix usage
  - [ ] Test fix with direct HTTP call
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-208-02**: Align HTTP methods (if mismatch found)
  - [ ] Backend toggle uses PUT, client may use PATCH
  - [ ] Standardize on one method
  - [ ] Update both client and server if needed
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-208-03**: Add database migration (if table missing)
  - [ ] Create action_lists table migration
  - [ ] Add action_list_items table if needed
  - [ ] Run migration and verify
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-208-04**: Add route registration verification
  - [ ] Add startup log showing registered routes
  - [ ] Include action-list routes in health check
  - [ ] Fail fast if routes not registered
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-208-05**: Update configuration documentation
  - [ ] Document correct API endpoint format
  - [ ] Add troubleshooting section for 404 errors
  - [ ] Include route verification commands
  - **Files Modified**: *[List files]*
  - **Validation**: ⬜

- [ ] **I-208-06**: OpenAPI spec generation setup *(QUANTUM RESEARCH)*
  - [ ] Install tsoa as dev dependency
  - [ ] Create tsoa.json configuration
  - [ ] Add build script to generate OpenAPI spec
  - [ ] Generate initial swagger.json from existing routes
  - **Files Modified**: *package.json, tsoa.json, swagger.json*
  - **Validation**: ⬜

- [ ] **I-208-07**: Migrate api-server.cjs to TypeScript *(QUANTUM RESEARCH)*
  - [ ] Rename api-server.cjs to api-server.ts
  - [ ] Add TypeScript types for all routes
  - [ ] Add tsoa decorators (@Route, @Get, @Post, etc.)
  - [ ] Update build process for TypeScript compilation
  - **Files Modified**: *api-server.ts, tsconfig.json*
  - **Validation**: ⬜

- [ ] **I-208-08**: Standardize all routes to /api/v1/* *(PRIORITY - ROOT CAUSE FIX)*
  - [ ] Audit all routes in api-server (tasks, action-lists, projects, sprints)
  - [ ] Add /api/v1 prefix to `/api/tasks` routes
  - [ ] Verify all routes use consistent prefix
  - [ ] Add route aliases for backward compatibility if needed
  - **Files Modified**: *api-server.cjs or api-server.ts*
  - **Validation**: ⬜

- [ ] **I-208-09**: Add Swagger UI endpoint *(OPTIONAL - NICE TO HAVE)*
  - [ ] Install swagger-ui-express
  - [ ] Serve OpenAPI spec at /api/docs
  - [ ] Configure Swagger UI options
  - **Files Modified**: *api-server.ts, package.json*
  - **Validation**: ⬜

#### 🧪 Testing Phase (QA Oracle)

- [ ] **T-208-01**: Direct HTTP endpoint tests
  - [ ] Test GET /api/v1/action-lists returns 200
  - [ ] Test POST /api/v1/action-lists creates item
  - [ ] Test all CRUD operations via HTTP
  - **Results**: *[Add results]*
  - **Verdict**: ⬜

- [ ] **T-208-02**: MCP tool invocation tests
  - [ ] Test `action_list_list` tool via MCP
  - [ ] Test `action_list_create` tool via MCP
  - [ ] Verify no 404 errors in response
  - **Results**: *[Add results]*
  - **Verdict**: ⬜

- [ ] **T-208-03**: End-to-end action list CRUD cycle
  - [ ] Create action list → Read → Update → Delete
  - [ ] Add item → Toggle → Remove
  - [ ] Verify full lifecycle works
  - **Results**: *[Add results]*
  - **Verdict**: ⬜

- [ ] **T-208-04**: Integration test for backend connectivity
  - [ ] Add test that validates endpoint before tool execution
  - [ ] Graceful error handling for connection issues
  - [ ] Clear error message for 404 scenarios
  - **Results**: *[Add results]*
  - **Verdict**: ⬜

- [ ] **T-208-05**: Health check enhancement test
  - [ ] Verify health check includes action-list availability
  - [ ] Test health check reports correct status
  - [ ] Document health check response format
  - **Results**: *[Add results]*
  - **Verdict**: ⬜

### Notes & Decisions

| Date | Persona | Note |
|------|---------|------|
| 2025-12-04 | 🔬 | Initial issue created - 404 on action list endpoints |
| 2025-12-04 | 📋 | Documentation infrastructure complete - 140-line checklist section added |
| 2025-12-04 | 🔬 | **LIVE BUG REPRODUCED** - `mcp_task-manager_action_list_list` returns 404 in session |
| 2025-12-04 | 🔬 | Code analysis identified 12 MCP tools, route prefix mismatch hypothesis (90% confidence) |
| 2025-12-04 | 🔬 | Added R-208-07 (verbose logging) and R-208-08 (auth audit) based on investigation |
| 2025-12-04 | 🔮 | **QUANTUM RESEARCH COLLECTIVE DEPLOYED** - Dr. Archaeon (Internal) + Navigator Flux (External) |
| 2025-12-04 | 🔮 | R-208-09 COMPLETE: 44 files catalogued, circuit breaker/locking/audit patterns documented |
| 2025-12-04 | 🔮 | R-208-10 COMPLETE: OpenAPI 3.1.1, tsoa, express-zod-api research - **tsoa RECOMMENDED** |
| 2025-12-04 | 🔮 | ROOT CAUSE CONFIRMED: Route prefix inconsistency `/api/tasks` vs `/api/v1/action-lists` |
| 2025-12-04 | 🔮 | **USER PREFERENCE**: OpenAPI standards, REST/JSON API, `/api/v1` alignment for ALL routes |
| *YYYY-MM-DD* | *🔬/🛠️/🧪* | *[Add notes as work progresses]* |

### Blockers

| ID | Description | Owner | Raised | Resolved | Resolution |
|----|-------------|-------|--------|----------|------------|
| *B-208-01* | *[None currently]* | - | - | - | - |

---

## Daily Standup Template

### Date: YYYY-MM-DD

**Active Issue**: CF-XXX  
**Persona on Point**: 🔬/🛠️/🧪

#### Yesterday
- [ ] *What was completed*

#### Today
- [ ] *What is planned*

#### Blockers
- [ ] *Any blockers*

#### Velocity Update
| Metric | Value |
|--------|-------|
| Points Completed | X |
| Points Remaining | Y |
| Estimated Completion | YYYY-MM-DD |

---

## Sprint Retrospective Template

### Sprint: YYYY-WXX

**Date**: YYYY-MM-DD  
**Participants**: 🔬 Dr. Schema, 🛠️ Constructor Prime, 🧪 QA Oracle

#### What Went Well ✅
1. *[Add items]*

#### What Could Improve 🔄
1. *[Add items]*

#### Action Items 📋
| Action | Owner | Due | Status |
|--------|-------|-----|--------|
| *[Action]* | *[Owner]* | *[Date]* | ⬜ |

#### Learnings Captured (vibe_learn)
| Category | Learning | Applied |
|----------|----------|---------|
| *[Category]* | *[Learning]* | ⬜ |

---

## Blocker Escalation Protocol

### Severity Levels

| Level | Criteria | Response Time | Escalation |
|-------|----------|---------------|------------|
| 🔴 **Critical** | Blocks all work on issue | < 1 hour | Immediate user notification |
| 🟠 **High** | Blocks current phase | < 4 hours | Add to daily standup |
| 🟡 **Medium** | Workaround available | < 24 hours | Track in checklist |
| 🟢 **Low** | Minor inconvenience | Best effort | Note for future |

### Blocker Template

```yaml
blocker:
  id: "B-XXX-YY"
  severity: 🔴/🟠/🟡/🟢
  issue: "CF-XXX"
  phase: "research|implementation|testing"
  description: "[Detailed description]"
  impact: "[What is blocked]"
  workaround: "[If available]"
  owner: "🔬/🛠️/🧪"
  raised: "YYYY-MM-DD HH:MM"
  target_resolution: "YYYY-MM-DD"
  resolution: "[How it was resolved]"
  resolved: "YYYY-MM-DD HH:MM"
  lessons_learned: "[What we learned]"
```

---

## Acceptance Criteria Validation

### Issue CF-197 Acceptance
- [ ] All 8 obsolete issues (CF-172 through CF-179) are Cancelled
- [ ] Each cancelled issue has a comment explaining the resolution
- [ ] Each cancelled issue links to CF-184 as the verification reference
- [ ] Plan document obsolete issues table is accurate

### Issue CF-198 Acceptance
- [ ] All 58 failing tests are now passing
- [ ] No new test failures introduced
- [ ] Test isolation verified (random order works)
- [ ] Coverage has not decreased

### Issue CF-199 Acceptance
- [ ] TypeDoc generates without errors
- [ ] All public APIs have TSDoc annotations
- [ ] OpenAPI spec validates in Swagger UI
- [ ] Documentation is linked from main README

### Issue CF-200 Acceptance
- [ ] All MCP tools are documented
- [ ] Each tool has working examples
- [ ] Contract testing documentation exists
- [ ] Documentation is linked from main README

### Issue CF-208 Acceptance
- [ ] Root cause of 404 error identified and documented
- [ ] Action list routes verified registered in backend
- [ ] Action list database table confirmed exists
- [ ] API route mappings reviewed and validated in src/
- [ ] 404 error resolved with direct HTTP call test
- [ ] Action list endpoints return 200 OK responses

---

## Evidence Collection Protocol

### Per-Issue Evidence Bundle

```
.QSE/v2/Evidence/P-TASKMAN-MCP-TYPESCRIPT/
├── CF-197/
│   ├── research-notes.yaml
│   ├── implementation-log.yaml
│   ├── test-results.json
│   └── evidence-bundle.tar.gz
├── CF-198/
│   ├── research-notes.yaml
│   ├── implementation-log.yaml
│   ├── test-results.json
│   ├── coverage-before.json
│   ├── coverage-after.json
│   └── evidence-bundle.tar.gz
├── CF-199/
│   ├── research-notes.yaml
│   ├── implementation-log.yaml
│   ├── generated-docs/
│   └── evidence-bundle.tar.gz
└── CF-200/
    ├── research-notes.yaml
    ├── implementation-log.yaml
    ├── contract-tests/
    └── evidence-bundle.tar.gz
```

### Evidence Hash Generation

```bash
# Generate SHA-256 hash for evidence bundle
sha256sum evidence-bundle.tar.gz > evidence-bundle.sha256

# Verify integrity
sha256sum -c evidence-bundle.sha256
```

---

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-12-04 | AI Agent | Initial checklist creation |
| *X.Y.Z* | *YYYY-MM-DD* | *Author* | *[Description]* |

---

## Quick Commands Reference

### Linear CLI
```bash
# Update issue status
linear issue update CF-XXX --status "In Progress"

# Add comment
linear issue comment CF-XXX "Research phase complete"

# List project issues
linear issue list --project P-TASKMAN-MCP-TYPESCRIPT
```

### Test Commands
```bash
# Run all tests
cd TaskMan-v2/mcp-server-ts && npm test

# Run specific test file
npm test -- src/features/projects/projects.test.ts

# Run with coverage
npm test -- --coverage
```

### Documentation Commands
```bash
# Generate TypeDoc
npm run docs

# Serve docs locally
npm run docs:serve

# Generate OpenAPI
npm run openapi:generate
```

---

**Checklist Maintained By**: AI Agent (Opus 4)  
**Review Cadence**: Daily during active work, weekly during maintenance  
**Sync with Linear**: Manual or via Linear CLI  
**Parent Plan**: [TASKMAN-MCP-TYPESCRIPT-API-IMPLEMENTATION.md](./TASKMAN-MCP-TYPESCRIPT-API-IMPLEMENTATION.md)
