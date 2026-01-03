# Vibe Check MCP - STDIO Transport Validation Plan

**Created:** 2025-11-10
**Authority:** HTTP transport discovery analysis
**Status:** ACTIVE - Ready for execution
**Transport:** stdio (CLI-managed configuration)

---

## Executive Summary

This plan focuses **exclusively on stdio transport validation** after discovering that Vibe Check MCP's HTTP
transport is designed for **client-integration only** (not standalone JSON-RPC testing). All validation
objectives can be achieved via stdio, which is:
- ✅ Simpler and more reliable
- ✅ Already configured via CLI for both VS Code and Claude Code
- ✅ The primary transport method for most MCP servers
- ✅ Fully functional for all Vibe Check features

---

## Phase 1: Foundation & Tool Discovery

### 1.1 Environment Validation
**Objective:** Confirm stdio transport is operational in both editors

**Tasks:**
1. **VS Code validation:**
   - Restart VS Code to load CLI-managed configuration
   - Open MCP tools panel (if available in VS Code MCP extension)
   - Verify "vibe-check-mcp" appears in available servers
   - Capture screenshot/evidence of server presence

2. **Claude Code validation:**
   - Restart Claude Code (if needed)
   - Check MCP connection status
   - Verify vibe-check-mcp is listed and connected
   - Document connection confirmation

3. **Environment check:**
   ```bash
   npx @pv-bhat/vibe-check-mcp doctor
   ```
   - Confirm Node.js v24.5.0
   - Verify .env file detection
   - Document stdio transport confirmation

**Success Criteria:**
- ✅ Both editors show vibe-check-mcp server active
- ✅ Doctor command passes all checks
- ✅ No connection errors in editor logs

**Evidence Required:**
- Doctor command output (JSON/text)
- Editor configuration confirmations
- Server availability screenshots/logs

---

### 1.2 STDIO Tools Enumeration
**Objective:** Establish complete tool inventory with IDs and schemas

**Tasks:**
1. **List all tools via stdio:**
   - Connect via VS Code MCP interface
   - Enumerate all available tools
   - Capture tool names, descriptions, and IDs

2. **Expected tools inventory:**
   - `vibe_check` - Pattern interrupt and assumption challenge
   - `vibe_learn` - Learning capture and pattern recognition
   - `update_constitution` - Session rule establishment
   - `check_constitution` - Rule inspection
   - `reset_constitution` - Rule replacement/clearing

3. **Schema documentation:**
   - For each tool, document:
     - Required parameters
     - Optional parameters
     - Parameter types and constraints
     - Expected output format

**Success Criteria:**
- ✅ All 5 expected tools discovered
- ✅ Complete schema documentation for each tool
- ✅ Tool IDs captured for reference

**Evidence Required:**
- Complete tools/list response (JSON)
- Schema documentation table
- Tool capability summary

---

## Phase 2: Constitution Framework Validation

### 2.1 Constitution Echo Test (Single Rule)
**Objective:** Validate basic update → check → reset cycle with single rule

**Test Sequence:**
```javascript
// Step 1: Update with single rule
{
  "sessionId": "test-session-001",
  "rule": "Unit tests before any production code changes"
}

// Step 2: Check constitution
{
  "sessionId": "test-session-001"
}
// Expected: { "rules": ["Unit tests before any production code changes"] }

// Step 3: Reset constitution
{
  "sessionId": "test-session-001",
  "rules": []
}

// Step 4: Verify cleared
{
  "sessionId": "test-session-001"
}
// Expected: { "rules": [] }
```

**Success Criteria:**
- ✅ Update returns success confirmation
- ✅ Check returns exact rule verbatim
- ✅ Reset clears rules successfully
- ✅ Post-reset check returns empty array

**Evidence Required:**
- Complete request/response JSON for all 4 steps
- Structured event log with timestamps
- Assertion results (pass/fail for each step)

---

### 2.2 Constitution Merge Test (Multiple Rules)
**Objective:** Verify update_constitution merges rules rather than replacing

**Test Sequence:**
```javascript
// Step 1: Add first rule
{
  "sessionId": "test-session-002",
  "rule": "No external network calls without approval"
}

// Step 2: Add second rule
{
  "sessionId": "test-session-002",
  "rule": "Use small, reversible change sets"
}

// Step 3: Check constitution
{
  "sessionId": "test-session-002"
}
// Expected: { "rules": [
//   "No external network calls without approval",
//   "Use small, reversible change sets"
// ]}

// Step 4: Add third rule
{
  "sessionId": "test-session-002",
  "rule": "Document all architectural decisions"
}

// Step 5: Final check
{
  "sessionId": "test-session-002"
}
// Expected: All 3 rules present
```

**Success Criteria:**
- ✅ Each update_constitution adds to existing rules
- ✅ Check returns all rules in order
- ✅ No rules are lost or overwritten
- ✅ Duplicate prevention works (if applicable)

**Evidence Required:**
- Full request/response chain
- Rule accumulation verification
- Merge behavior documentation

---

### 2.3 Constitution Persistence Test
**Objective:** Verify constitution persists across multiple check operations

**Test Sequence:**
```javascript
// Setup: Establish constitution with 2 rules
update_constitution(sessionId: "test-session-003", rule: "Rule A")
update_constitution(sessionId: "test-session-003", rule: "Rule B")

// Test: Multiple checks should return same rules
check_1 = check_constitution(sessionId: "test-session-003")
// ... perform other operations ...
check_2 = check_constitution(sessionId: "test-session-003")
// ... perform other operations ...
check_3 = check_constitution(sessionId: "test-session-003")

// Assert: All checks return identical rule sets
assert check_1 == check_2 == check_3
```

**Success Criteria:**
- ✅ Rules persist across multiple check calls
- ✅ No degradation or data loss
- ✅ Consistent ordering maintained

**Evidence Required:**
- Multiple check responses with timestamps
- Consistency verification results

---

### 2.4 Constitution Reset Verification
**Objective:** Confirm reset_constitution clears all rules completely

**Test Sequence:**
```javascript
// Setup: Establish constitution with multiple rules
update_constitution(sessionId: "test-session-004", rule: "Rule 1")
update_constitution(sessionId: "test-session-004", rule: "Rule 2")
update_constitution(sessionId: "test-session-004", rule: "Rule 3")

// Verify populated
pre_reset = check_constitution(sessionId: "test-session-004")
// Expected: 3 rules present

// Reset with explicit empty array
reset_constitution(sessionId: "test-session-004", rules: [])

// Verify cleared
post_reset = check_constitution(sessionId: "test-session-004")
// Expected: { "rules": [] }

// Verify persistence of cleared state
final_check = check_constitution(sessionId: "test-session-004")
// Expected: Still empty
```

**Success Criteria:**
- ✅ Pre-reset check shows all rules
- ✅ Reset clears all rules immediately
- ✅ Post-reset check returns empty array
- ✅ Cleared state persists

**Evidence Required:**
- Before/after comparison
- Empty state confirmation
- Persistence verification

---

## Phase 3: Vibe Check Core Functionality

### 3.1 Baseline Vibe Check
**Objective:** Establish minimal viable vibe_check invocation baseline

**Test Configuration:**
```javascript
{
  "goal": "Implement user authentication system",
  "plan": "1. Add JWT library\n2. Create auth middleware\n3. Protect routes\n4. Add login endpoint"
}
```

**Analysis Focus:**
- Response structure and format
- Types of challenges/questions raised
- Risk assessment methodology
- Follow-up question quality

**Success Criteria:**
- ✅ Call completes without errors
- ✅ Response includes challenges or guidance
- ✅ Output is actionable and relevant
- ✅ Latency < 5 seconds

**Evidence Required:**
- Complete request/response JSON
- Response quality assessment
- Latency measurement

---

### 3.2 Enriched Vibe Check with Full Context
**Objective:** Validate comprehensive context parameter usage

**Test Configuration:**
```javascript
{
  "goal": "Implement user authentication system",
  "plan": "Phase: planning — 1. Add JWT library\n2. Create auth middleware\n3. Protect routes\n4. Add login endpoint | Constitution: Unit tests first, No external calls without approval",
  "userPrompt": "Add authentication to the API using JWT tokens",
  "sessionId": "test-session-005",
  "taskContext": "phase=planning; workId=W-AUTH-001; project=API-SECURITY",
  "uncertainties": [
    "Which JWT library to use (jsonwebtoken vs jose)",
    "Session storage strategy (Redis vs database)",
    "Token refresh mechanism design"
  ],
  "progress": "Research completed; ready for implementation planning"
}
```

**Comparison vs Baseline:**
- Response depth increase
- Context-awareness in challenges
- Phase-specific guidance
- Constitution integration in feedback

**Success Criteria:**
- ✅ Response demonstrates context awareness
- ✅ Challenges reference constitution rules
- ✅ Uncertainties addressed in feedback
- ✅ Phase-appropriate guidance provided

**Evidence Required:**
- Full request/response JSON
- Baseline comparison analysis
- Context-awareness assessment

---

### 3.3 Vibe Check with Constitution Integration
**Objective:** Verify vibe_check considers active session constitution

**Test Sequence:**
```javascript
// Step 1: Establish constitution
update_constitution(sessionId: "test-session-006", rule: "No ORMs - use raw SQL")
update_constitution(sessionId: "test-session-006", rule: "Maximum 3 files per PR")

// Step 2: Run vibe_check with constitution-violating plan
vibe_check({
  goal: "Add user profiles feature",
  plan: "Phase: planning — 1. Install Prisma ORM\n2. Generate 8 model files\n3. Create migrations\n4. Add controllers",
  sessionId: "test-session-006"
})

// Expected: Response should challenge ORM usage and large file count
```

**Success Criteria:**
- ✅ Response challenges constitution violations
- ✅ Feedback references specific constitution rules
- ✅ Alternative approaches suggested
- ✅ Constitution compliance emphasized

**Evidence Required:**
- Constitution setup confirmation
- Vibe check request/response
- Violation detection analysis

---

### 3.4 Vibe Check Strategic Cadence Test
**Objective:** Demonstrate optimal 10-15% CPI dosage pattern

**Test Scenario:** 8-phase workflow with strategic checkpoints

**Checkpoint Schedule:**
```javascript
// MANDATORY checkpoints (4 total = 50% of phases)
Phase 0: Session initialization
  → vibe_check(goal, plan: "Phase: initialization — ...")

Phase 3: Pre-implementation validation
  → vibe_check(goal, plan: "Phase: design complete — ...")

Phase 6: Execution preflight
  → vibe_check(goal, plan: "Phase: ready to execute — ...")

Phase 8: Reflection and AAR
  → vibe_check(goal, plan: "Phase: reflection — ...")

// CONDITIONAL checkpoint (0-1 based on complexity)
Phase 4: IF high uncertainty detected
  → vibe_check(goal, plan: "Phase: validation concerns — ...")
```

**Metrics Collection:**
- Total vibe_check calls: 4-5
- Percentage of workflow steps: 10-15%
- Average latency per call
- Total CPI overhead
- Feedback incorporation rate

**Success Criteria:**
- ✅ 4-5 checkpoints executed (not every phase)
- ✅ Strategic placement at key decision points
- ✅ Total overhead < 10% of workflow time
- ✅ Demonstrates CPI methodology compliance

**Evidence Required:**
- Complete checkpoint sequence log
- Timing analysis
- Dosage calculation (calls/total steps)
- CPI compliance validation

---

## Phase 4: Vibe Learn Pattern Recognition

### 4.1 Mistake Category Coverage
**Objective:** Validate vibe_learn across all standard categories

**Test Cases:**
```javascript
// Category 1: Complex Solution Bias
vibe_learn({
  mistake: "Implemented custom ORM instead of using standard library",
  category: "Complex Solution Bias",
  solution: "Switched to built-in database/sql package",
  type: "mistake",
  sessionId: "test-session-007"
})

// Category 2: Feature Creep
vibe_learn({
  mistake: "Added real-time notifications when not requested",
  category: "Feature Creep",
  solution: "Removed unnecessary feature, focused on core requirements",
  type: "mistake",
  sessionId: "test-session-007"
})

// Category 3: Premature Implementation
vibe_learn({
  mistake: "Started coding before design review completed",
  category: "Premature Implementation",
  solution: "Paused implementation, completed design validation first",
  type: "mistake",
  sessionId: "test-session-007"
})

// Category 4: Misalignment
vibe_learn({
  mistake: "Built GraphQL API when REST was specified",
  category: "Misalignment",
  solution: "Rebuilt as REST API per requirements",
  type: "mistake",
  sessionId: "test-session-007"
})

// Category 5: Overtooling
vibe_learn({
  mistake: "Introduced Kafka when simple queue would suffice",
  category: "Overtooling",
  solution: "Replaced with channel-based queue",
  type: "mistake",
  sessionId: "test-session-007"
})

// Category 6: Preference (positive)
vibe_learn({
  mistake: "Team prefers table-driven tests over individual test functions",
  category: "Preference",
  type: "preference",
  sessionId: "test-session-007"
})

// Category 7: Success (learning)
vibe_learn({
  mistake: "Breaking changes into atomic commits improved review speed",
  category: "Success",
  solution: "Adopted small commit strategy for all PRs",
  type: "success",
  sessionId: "test-session-007"
})
```

**Success Criteria:**
- ✅ All 7 categories accepted without errors
- ✅ Persistence confirmation for each entry
- ✅ Optional fields (solution, type) handled correctly
- ✅ Learning entries retrievable (if query supported)

**Evidence Required:**
- Request/response JSON for all categories
- Acceptance confirmations
- Category coverage matrix

---

### 4.2 Vibe Learn Minimal Payload Test
**Objective:** Verify minimal required fields work without optional parameters

**Test Case:**
```javascript
{
  "mistake": "Implemented feature without tests",
  "category": "Premature Implementation"
}
// Note: No solution, no type, no sessionId
```

**Success Criteria:**
- ✅ Minimal payload accepted
- ✅ Defaults applied appropriately
- ✅ No errors on missing optional fields

**Evidence Required:**
- Minimal payload request/response
- Default behavior documentation

---

## Phase 5: Multi-Provider Validation

### 5.1 Provider Key Smoke Test
**Objective:** Verify multiple LLM providers work correctly

**Test Configurations:**

**Gemini (if key available):**
```bash
export GEMINI_API_KEY=<key>
# Run vibe_check
```

**OpenAI (if key available):**
```bash
export OPENAI_API_KEY=<key>
# Run vibe_check
```

**OpenRouter (if key available):**
```bash
export OPENROUTER_API_KEY=<key>
# Run vibe_check with modelOverride
vibe_check({
  goal: "Test",
  plan: "Test",
  modelOverride: { provider: "openrouter", model: "anthropic/claude-3.5-sonnet" }
})
```

**Success Criteria:**
- ✅ Each provider successfully processes vibe_check
- ✅ No authentication errors
- ✅ Provider selection follows documented priority
- ✅ modelOverride parameter works when specified

**Evidence Required:**
- Provider selection confirmation
- Successful response from each provider
- Model selection verification

---

## Phase 6: Error Handling & Edge Cases

### 6.1 Schema Validation Test
**Objective:** Verify proper error handling for invalid inputs

**Test Cases:**

**Missing required field:**
```javascript
// vibe_check without 'plan'
{
  "goal": "Test goal"
  // plan field missing - should error
}
```

**Invalid enum value:**
```javascript
// vibe_learn with invalid category
{
  "mistake": "Test",
  "category": "InvalidCategory"  // Not in allowed enum
}
```

**Type mismatch:**
```javascript
// sessionId as number instead of string
{
  "sessionId": 12345  // Should be string
}
```

**Success Criteria:**
- ✅ Clear error messages for each violation
- ✅ Schema validation occurs before processing
- ✅ Error responses include helpful guidance

**Evidence Required:**
- Error response JSON for each case
- Error message clarity assessment

---

### 6.2 Edge Case Handling
**Objective:** Test boundary conditions and unusual inputs

**Test Cases:**

**Empty string inputs:**
```javascript
update_constitution({ sessionId: "test", rule: "" })
vibe_check({ goal: "", plan: "" })
```

**Very long inputs:**
```javascript
vibe_check({
  goal: "Test",
  plan: "<5000+ character plan>"
})
```

**Special characters in sessionId:**
```javascript
check_constitution({ sessionId: "test-session-🎯-001" })
```

**Null vs undefined in optional fields:**
```javascript
vibe_check({ goal: "Test", plan: "Test", uncertainties: null })
vibe_check({ goal: "Test", plan: "Test", uncertainties: undefined })
```

**Success Criteria:**
- ✅ Graceful handling of edge cases
- ✅ No crashes or hangs
- ✅ Appropriate validation messages

**Evidence Required:**
- Edge case test results
- Error handling assessment

---

## Phase 7: Schema Snapshot & Documentation

### 7.1 Complete Schema Capture
**Objective:** Document exact schema for all tools

**Deliverables:**

**For each tool, capture:**
1. Complete JSON schema definition
2. Parameter descriptions and constraints
3. Example valid payloads
4. Example invalid payloads
5. Expected response formats
6. Error response formats

**Schema documentation structure:**
```markdown
## Tool: vibe_check

### Required Parameters:
- `goal` (string): Objective description
- `plan` (string): Implementation narrative

### Optional Parameters:
- `userPrompt` (string): Original user request
- `sessionId` (string): Session identifier
- `taskContext` (string): Context metadata
- `uncertainties` (array<string>): Known uncertainties
- `progress` (string): Current progress state
- `modelOverride` (object): Provider override
  - `provider` (enum): gemini|openai|openrouter
  - `model` (string): Model identifier

### Response Format:
{
  "challenges": [...],
  "risks": [...],
  "questions": [...]
}

### Example Valid:
{...}

### Example Invalid:
{...}
```

**Success Criteria:**
- ✅ Complete schema for all 5 tools
- ✅ Examples validated against server
- ✅ Documentation matches actual behavior

**Evidence Required:**
- Complete schema documentation file
- Validation test results for all examples

---

### 7.2 README Comparison Audit
**Objective:** Detect any schema drift between implementation and documentation

**Process:**
1. Extract schema claims from package README
2. Compare against captured actual schemas
3. Document any discrepancies
4. Create issue list for upstream fixes

**Success Criteria:**
- ✅ Complete comparison performed
- ✅ Discrepancies documented
- ✅ Validation confidence established

**Evidence Required:**
- Comparison report
- Discrepancy list (if any)
- Validation summary

---

## Phase 8: Integration & Workflow Testing

### 8.1 Complete Workflow Simulation
**Objective:** Execute realistic multi-tool workflow

**Scenario:** Implement new feature with full CPI oversight

**Workflow Steps:**
```javascript
// Phase 0: Initialize session with constitution
update_constitution({
  sessionId: "workflow-test-001",
  rule: "Unit tests before implementation"
})
update_constitution({
  sessionId: "workflow-test-001",
  rule: "Maximum 3 files per change"
})

// Phase 0: Initial vibe_check
vibe_check({
  goal: "Add user avatar upload feature",
  plan: "Phase: initialization — Research image processing libraries, design upload flow, plan storage strategy",
  userPrompt: "Add ability for users to upload profile pictures",
  sessionId: "workflow-test-001"
})

// Phase 3: Pre-implementation vibe_check
vibe_check({
  goal: "Add user avatar upload feature",
  plan: "Phase: design complete — Use stdlib HTTP multipart, save to /uploads, add avatar_url field to users table | Constitution: Unit tests first, Max 3 files",
  sessionId: "workflow-test-001",
  uncertainties: ["Image size limits", "File type validation approach"]
})

// Phase 6: Execution preflight
vibe_check({
  goal: "Add user avatar upload feature",
  plan: "Phase: ready to execute — Implementation plan validated, tests written, ready to code",
  sessionId: "workflow-test-001",
  progress: "Test suite ready, storage configured"
})

// Phase 7: Capture learning
vibe_learn({
  mistake: "Initially designed for S3 storage, simplified to local filesystem per YAGNI",
  category: "Complex Solution Bias",
  solution: "Used local filesystem with documented S3 migration path",
  sessionId: "workflow-test-001"
})

// Phase 8: Final reflection
vibe_check({
  goal: "Add user avatar upload feature",
  plan: "Phase: reflection — Feature complete, tests passing, constitution followed",
  sessionId: "workflow-test-001",
  progress: "3 files changed, all tests green, avatar upload working"
})

// Cleanup
reset_constitution({ sessionId: "workflow-test-001", rules: [] })
```

**Success Criteria:**
- ✅ All tools work together seamlessly
- ✅ Constitution influences vibe_check feedback
- ✅ Learning captured appropriately
- ✅ Complete workflow evidence trail

**Evidence Required:**
- Complete workflow execution log
- Tool interaction analysis
- Integration success assessment

---

## Execution Strategy

### Implementation Approach

**Harness Development:**
Create `scripts/Test-VibeCheck-STDIO.ps1` with:
- Structured JSONL event logging
- Comprehensive error handling
- Evidence capture for all interactions
- Assertion framework for validation
- Session correlation tracking

**Execution Order:**
1. Phase 1 (Foundation) - Establish baseline
2. Phase 2 (Constitution) - Core functionality
3. Phase 3 (Vibe Check) - Primary feature validation
4. Phase 4 (Vibe Learn) - Pattern recognition
5. Phase 5 (Multi-Provider) - Flexibility validation
6. Phase 6 (Error Handling) - Robustness
7. Phase 7 (Schema) - Documentation
8. Phase 8 (Integration) - End-to-end validation

**Parallel Opportunities:**
- Phase 5 (Provider tests) can run independently
- Phase 6 (Error handling) can run alongside Phase 3-4
- Phase 7 (Schema capture) can accumulate throughout

### Evidence Management

**Log Structure:**
```
logs/
  vibe-check-stdio-validation-<timestamp>/
    00-environment-validation.jsonl
    01-tools-enumeration.jsonl
    02-constitution-echo.jsonl
    03-constitution-merge.jsonl
    04-constitution-persistence.jsonl
    05-constitution-reset.jsonl
    06-vibe-check-baseline.jsonl
    07-vibe-check-enriched.jsonl
    08-vibe-check-constitution.jsonl
    09-vibe-check-cadence.jsonl
    10-vibe-learn-categories.jsonl
    11-vibe-learn-minimal.jsonl
    12-provider-tests.jsonl
    13-error-handling.jsonl
    14-edge-cases.jsonl
    15-schema-capture.jsonl
    16-workflow-integration.jsonl
    summary.yaml
```

**Event Format:**
```json
{
  "ts": "2025-11-10T15:30:45.123Z",
  "type": "test_start|tool_call|tool_response|assertion|test_complete",
  "phase": "2.1",
  "test": "constitution-echo",
  "data": {...}
}
```

### Success Metrics

**Phase Completion Criteria:**
- All test cases executed
- All assertions passed
- Complete evidence captured
- No blocking issues found

**Overall Validation Success:**
- ✅ 100% of planned tests executed
- ✅ ≥95% of assertions passed
- ✅ Complete schema documentation
- ✅ Integration workflow successful
- ✅ Evidence bundle complete

### Risk Mitigation

**Known Risks:**

1. **Constitution empty return issue** (from prior testing)
   - Mitigation: Detailed request/response capture for diagnosis
   - Fallback: Document issue, continue other validation

2. **Provider key availability**
   - Mitigation: Phase 5 marked as conditional
   - Fallback: Document untested providers

3. **MCP connection stability**
   - Mitigation: Retry logic in harness
   - Fallback: Manual retry of failed tests

4. **Schema drift from README**
   - Mitigation: Phase 7 comparison audit
   - Fallback: Document discrepancies for upstream

### Timeline Estimate

**Phase Durations:**
- Phase 1: 30 minutes (environment setup)
- Phase 2: 60 minutes (constitution testing)
- Phase 3: 90 minutes (vibe_check validation)
- Phase 4: 45 minutes (vibe_learn coverage)
- Phase 5: 30 minutes (provider tests)
- Phase 6: 45 minutes (error handling)
- Phase 7: 60 minutes (schema documentation)
- Phase 8: 45 minutes (integration workflow)

**Total Estimated Time:** 6-7 hours

**Suggested Schedule:**
- Session 1 (2 hours): Phases 1-2
- Session 2 (2 hours): Phases 3-4
- Session 3 (2 hours): Phases 5-7
- Session 4 (1 hour): Phase 8 + summary

---

## Deliverables

### Primary Artifacts

1. **Validation Report:**
   - Executive summary
   - Phase-by-phase results
   - Assertion pass/fail matrix
   - Issues discovered
   - Recommendations

2. **Schema Documentation:**
   - Complete tool schemas
   - Parameter reference
   - Example payloads
   - Response formats

3. **Evidence Bundle:**
   - Complete JSONL event logs
   - Request/response captures
   - Timing metrics
   - Error samples

4. **Integration Guide:**
   - Best practices from testing
   - Constitution usage patterns
   - CPI cadence examples
   - Common pitfalls

### Todo List Updates

**Mark as complete:**
- ~~HTTP constitution echo~~ → Documented as not applicable
- STDIO tools list → Execute in Phase 1.2
- Update merge test → Execute in Phase 2.2
- Check echo diagnosis → Execute in Phase 2.1
- Reset clearing test → Execute in Phase 2.4
- Vibe_check enriched → Execute in Phase 3.2
- Vibe_learn coverage → Execute in Phase 4.1
- Provider key smoke → Execute in Phase 5.1
- Schema snapshot → Execute in Phase 7.1
- Cadence simulation → Execute in Phase 3.4
- Failure mode injection → Execute in Phase 6.1

**Add new items:**
- [ ] Constitution persistence test (Phase 2.3)
- [ ] Constitution integration with vibe_check (Phase 3.3)
- [ ] Vibe learn minimal payload (Phase 4.2)
- [ ] Edge case handling (Phase 6.2)
- [ ] README comparison audit (Phase 7.2)
- [ ] Complete workflow simulation (Phase 8.1)
- [ ] Create validation report
- [ ] Create schema documentation
- [ ] Archive evidence bundle

---

## HTTP Transport Disposition

**Finding:** Vibe Check MCP HTTP transport is designed for **client-integration** (e.g., Windsurf, VS Code with MCP extension), not standalone JSON-RPC testing.

**Documentation:** "streamable HTTP transport" requires MCP-aware client that implements full protocol handshake.

**Decision:** HTTP standalone testing marked as **NOT APPLICABLE**. HTTP validation would require:
- MCP-aware client installation (Windsurf)
- Client configuration for HTTP transport
- Testing through client interface

**Recommendation:** If HTTP transport validation becomes necessary in the future, implement through Windsurf or VS Code MCP extension integration testing, not standalone HTTP harness.

**Evidence:**
- HTTP server returns 404 for /rpc, /health, /jsonrpc, /api
- /mcp endpoint returns 406 (Not Acceptable)
- Server designed for client-initiated MCP connections
- README confirms "HTTP-capable clients receive http://127.0.0.1:PORT endpoint"---

## Next Steps

1. **Review and approve this plan**
2. **Create stdio harness:** `scripts/Test-VibeCheck-STDIO.ps1`
3. **Execute Phase 1:** Environment validation and tool discovery
4. **Iterate through phases** with evidence capture
5. **Generate validation report** and schema documentation
6. **Update todo list** with completion status
7. **Archive evidence bundle** for future reference

---

**Plan Status:** READY FOR EXECUTION
**Approval Required:** Yes
**Estimated Effort:** 6-7 hours across 4 sessions
**Dependencies:** CLI-managed stdio configuration (✅ complete)
