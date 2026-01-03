# Vibe Check MCP - STDIO Validation Plan Summary

**Created:** 2025-11-10
**Plan Document:** [Vibe-Check-Validation-Plan-STDIO.md](./Vibe-Check-Validation-Plan-STDIO.md)
**Status:** READY FOR EXECUTION

---

## Quick Overview

### Why STDIO Transport?

After extensive HTTP transport investigation, we discovered that Vibe Check MCP's HTTP mode is designed for
**client-integration** (e.g., Windsurf, VS Code MCP extension), not standalone JSON-RPC testing.

**Key Findings:**
- ✅ HTTP server starts successfully but expects MCP-aware client connections
- ✅ Standard JSON-RPC endpoints return 404 (not designed for standalone testing)
- ✅ /mcp endpoint returns 406 (requires proper MCP client protocol)
- ✅ stdio transport provides complete functionality and is simpler to validate

**Decision:** Focus validation efforts on **stdio transport** where all features are accessible and testable.

---

## 8-Phase Validation Plan

### Phase 1: Foundation & Tool Discovery (30 min)
- Validate stdio configuration in VS Code and Claude Code
- Run `npx @pv-bhat/vibe-check-mcp doctor` validation
- Enumerate all available tools (vibe_check, vibe_learn, update/check/reset_constitution)
- Document complete tool schemas

### Phase 2: Constitution Framework (60 min)
- **Echo test:** Single rule update → check → reset cycle
- **Merge test:** Multiple updates accumulate rules correctly
- **Persistence test:** Rules survive multiple check operations
- **Reset test:** Clear all rules and verify empty state

### Phase 3: Vibe Check Core (90 min)
- **Baseline:** Minimal vibe_check (goal + plan only)
- **Enriched:** Full context (userPrompt, sessionId, taskContext, uncertainties, progress)
- **Constitution integration:** Verify vibe_check considers active session rules
- **Strategic cadence:** Demonstrate optimal 10-15% CPI dosage pattern (4-5 checkpoints in 8-phase workflow)

### Phase 4: Vibe Learn Coverage (45 min)
- Test all 7 categories: Complex Solution Bias, Feature Creep, Premature Implementation, Misalignment,
  Overtooling, Preference, Success
- Validate with/without optional fields (solution, type, sessionId)
- Confirm persistence and acceptance

### Phase 5: Multi-Provider (30 min)
- Validate GEMINI_API_KEY if available
- Validate OPENAI_API_KEY if available
- Test modelOverride parameter with OpenRouter
- Confirm provider selection works correctly

### Phase 6: Error Handling (45 min)
- Schema validation: Missing required fields, invalid enums, type mismatches
- Edge cases: Empty strings, very long inputs, special characters, null vs undefined
- Document error responses and handling quality

### Phase 7: Schema Documentation (60 min)
- Capture complete JSON schemas for all 5 tools
- Document all parameters (required/optional, types, constraints)
- Create example valid/invalid payloads
- Compare against README for any schema drift

### Phase 8: Integration Workflow (45 min)
- Execute realistic multi-tool workflow simulating feature implementation
- Demonstrate constitution → vibe_check → vibe_learn → reset cycle
- Validate seamless tool integration
- Capture complete evidence trail

---

## Key Benefits of This Plan

### ✅ Comprehensive Coverage
- All 5 tools validated (vibe_check, vibe_learn, 3 constitution tools)
- All major use cases tested (baseline, enriched, multi-provider, edge cases)
- Complete schema documentation produced
- Integration workflow validated

### ✅ Research-Backed Methodology
- Demonstrates CPI (Chain-Pattern Interrupt) optimal dosage (10-15%)
- Validates strategic checkpoint placement (4-5 per 8-phase workflow)
- Tests assumption challenge and oversight mechanisms
- Covers pattern recognition via vibe_learn

### ✅ Practical Evidence
- Structured JSONL event logging throughout
- Complete request/response capture for all tools
- Timing metrics and performance analysis
- Reproducible test scenarios

### ✅ Quality Assurance
- Assertion framework for pass/fail validation
- Error handling verification
- Schema compliance testing
- Integration success measurement

---

## Timeline & Effort

**Total Estimated Time:** 6-7 hours

**Suggested 4-Session Schedule:**

| Session | Duration | Phases | Focus |
|---------|----------|--------|-------|
| 1 | 2 hours | 1-2 | Foundation & Constitution |
| 2 | 2 hours | 3-4 | Core Features & Learning |
| 3 | 2 hours | 5-7 | Providers & Documentation |
| 4 | 1 hour | 8 | Integration & Summary |

**Parallel Opportunities:**
- Provider tests (Phase 5) can run independently
- Error handling (Phase 6) can overlap with Phases 3-4
- Schema capture (Phase 7) accumulates throughout

---

## Deliverables

### Primary Artifacts

1. **Validation Report** (comprehensive results summary)
   - Executive summary
   - Phase-by-phase results with pass/fail matrix
   - Issues discovered and recommendations
   - Schema drift analysis

2. **Schema Documentation** (complete reference)
   - All 5 tool schemas with parameters
   - Example valid/invalid payloads
   - Response format documentation
   - Error handling reference

3. **Evidence Bundle** (complete audit trail)
   - Structured JSONL event logs per phase
   - Request/response captures
   - Timing and performance metrics
   - Error samples and edge cases

4. **Integration Guide** (best practices)
   - Constitution usage patterns
   - CPI cadence examples from testing
   - Common pitfalls and solutions
   - Multi-tool workflow patterns

---

## Success Criteria

### Phase Completion
- ✅ All planned test cases executed
- ✅ All assertions passed (≥95% target)
- ✅ Complete evidence captured
- ✅ No blocking issues

### Overall Validation Success
- ✅ 100% of planned tests executed
- ✅ ≥95% of assertions passed
- ✅ Complete schema documentation produced
- ✅ Integration workflow successful
- ✅ Evidence bundle complete and archived

---

## HTTP Transport Disposition

### Finding
Vibe Check MCP's HTTP transport is designed for **MCP-aware client integration** (e.g., Windsurf, VS Code
MCP extension), not standalone JSON-RPC testing.

### Technical Evidence
- HTTP server starts successfully but returns 404 for /rpc, /health, /jsonrpc, /api
- /mcp endpoint returns 406 (Not Acceptable) indicating protocol mismatch
- Server expects client-initiated MCP connection with proper protocol handshake
- README confirms: "HTTP-capable clients receive http://127.0.0.1:PORT endpoint"

### Decision
HTTP standalone testing marked as **NOT APPLICABLE**. If HTTP transport validation becomes necessary:
- Use Windsurf or VS Code MCP extension
- Configure client for HTTP transport
- Test through client interface (not standalone harness)

### Preserved Artifacts
- `scripts/Test-VibeCheck-HTTP.ps1` - Marked as reference implementation
- `scripts/Test-VibeCheck-HTTP-Simple.ps1` - Diagnostic tool for HTTP behavior
- HTTP investigation logs - Complete discovery process documented

---

## Risk Mitigation

### Known Risks & Mitigations

1. **Constitution empty return issue** (observed in prior testing)
   - Mitigation: Detailed request/response capture for diagnosis
   - Fallback: Document issue, continue other validation

2. **Provider key availability**
   - Mitigation: Phase 5 marked as conditional based on key availability
   - Fallback: Document which providers tested, which skipped

3. **MCP connection stability**
   - Mitigation: Retry logic built into harness
   - Fallback: Manual retry of failed tests with fresh connection

4. **Schema drift from README**
   - Mitigation: Phase 7 includes explicit README comparison
   - Fallback: Document discrepancies for upstream reporting

---

## Next Actions

### Immediate (Today)
1. ✅ Review and approve validation plan
2. ⏳ Create stdio test harness: `scripts/Test-VibeCheck-STDIO.ps1`
3. ⏳ Execute Phase 1: Environment validation

### Short Term (This Week)
4. Execute Phases 2-4: Core functionality validation
5. Execute Phases 5-7: Provider, error handling, schema documentation

### Completion (Next Week)
6. Execute Phase 8: Integration workflow
7. Generate validation report and deliverables
8. Update todo list with final status
9. Archive complete evidence bundle

---

## References

- **Full Plan:** [Vibe-Check-Validation-Plan-STDIO.md](./Vibe-Check-Validation-Plan-STDIO.md)
- **Package:** @pv-bhat/vibe-check-mcp v2.7.1
- **Research:** CPI (Chain-Pattern Interrupt) methodology (27→54% success improvement)
- **Todo List:** [Project Todo List](../README.md#todolist)
- **MCP Protocol:** Version 2024-11-05

---

**Status:** READY FOR EXECUTION
**Approval Required:** Yes
**Est. Completion:** 4 sessions over 1-2 weeks
**Prerequisites:** ✅ CLI-managed stdio configuration complete
