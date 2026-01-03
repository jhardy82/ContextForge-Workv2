# Vibe Check STDIO Validation - Quick Reference Card

## 🎯 Plan At-A-Glance

| Aspect | Details |
|--------|---------|
| **Transport** | stdio (CLI-managed, both editors) |
| **Total Phases** | 8 phases across 4 sessions |
| **Duration** | 6-7 hours total |
| **Test Cases** | 24 comprehensive tests |
| **Tools Validated** | All 5 (vibe_check, vibe_learn, 3 constitution) |
| **Success Target** | ≥95% assertion pass rate |
| **Evidence Files** | 17 JSONL logs + summary report |

## 📋 8-Phase Checklist

### Session 1: Foundation (2 hours)
- [ ] **Phase 1.1** Environment validation (30m)
  - VS Code + Claude Code connection verification
  - Doctor command execution and validation
  - Server availability confirmation
- [ ] **Phase 1.2** Tool discovery (30m)
  - Enumerate all 5 tools with schemas
  - Document parameters and responses
- [ ] **Phase 2.1** Constitution echo test (15m)
  - update → check → reset → verify cleared
- [ ] **Phase 2.2** Constitution merge test (15m)
  - Multiple updates accumulate rules
- [ ] **Phase 2.3** Constitution persistence (15m)
  - Multiple checks return same rules
- [ ] **Phase 2.4** Constitution reset (15m)
  - Reset clears all rules completely

### Session 2: Core Features (2 hours)
- [ ] **Phase 3.1** Vibe check baseline (20m)
  - Minimal invocation (goal + plan)
- [ ] **Phase 3.2** Vibe check enriched (30m)
  - Full context parameters test
- [ ] **Phase 3.3** Constitution integration (20m)
  - Verify rule-aware feedback
- [ ] **Phase 3.4** Strategic cadence (20m)
  - Demonstrate 10-15% CPI dosage
- [ ] **Phase 4.1** Vibe learn categories (30m)
  - Test all 7 categories
- [ ] **Phase 4.2** Vibe learn minimal (15m)
  - Required fields only

### Session 3: Quality & Docs (2 hours)
- [ ] **Phase 5.1** Multi-provider tests (30m)
  - Gemini/OpenAI/OpenRouter validation
- [ ] **Phase 6.1** Schema validation (25m)
  - Invalid inputs and error handling
- [ ] **Phase 6.2** Edge cases (20m)
  - Boundary conditions testing
- [ ] **Phase 7.1** Schema capture (40m)
  - Complete documentation for all tools
- [ ] **Phase 7.2** README audit (20m)
  - Detect schema drift

### Session 4: Integration (1 hour)
- [ ] **Phase 8.1** Complete workflow (45m)
  - Multi-tool integration simulation
- [ ] **Report Generation** (15m)
  - Validation summary and deliverables

## 🔧 5 Tools to Validate

| Tool | Purpose | Required Params | Optional Params |
|------|---------|-----------------|-----------------|
| **vibe_check** | Pattern interrupt | goal, plan | userPrompt, sessionId, taskContext, uncertainties, progress, modelOverride |
| **vibe_learn** | Learning capture | mistake, category | solution, type, sessionId |
| **update_constitution** | Add rule | sessionId, rule | - |
| **check_constitution** | Inspect rules | sessionId | - |
| **reset_constitution** | Clear rules | sessionId, rules | - |

## 📊 Success Criteria Quick Check

### Phase Completion
- ✅ All test cases executed
- ✅ Assertions passed (≥95% target)
- ✅ Evidence captured (JSONL logs)
- ✅ No blocking issues

### Tool Validation
- ✅ All 5 tools discovered
- ✅ Schemas fully documented
- ✅ Parameters validated
- ✅ Errors handled gracefully

### Integration Success
- ✅ Multi-tool workflow works
- ✅ Constitution influences vibe_check
- ✅ Learning captured appropriately
- ✅ CPI cadence demonstrated

## 🎬 Quick Start Commands

```bash
# Verify environment
npx @pv-bhat/vibe-check-mcp doctor

# Run validation (when harness is ready)
pwsh -File scripts/Test-VibeCheck-STDIO.ps1 -Phase All -Verbose

# Run specific phase
pwsh -File scripts/Test-VibeCheck-STDIO.ps1 -Phase 1 -Verbose
pwsh -File scripts/Test-VibeCheck-STDIO.ps1 -Phase 2 -Verbose
# ... etc

# Generate report
pwsh -File scripts/Generate-ValidationReport.ps1 -LogDir logs/vibe-check-stdio-validation-*
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `docs/Vibe-Check-Validation-Plan-STDIO.md` | Complete detailed plan |
| `docs/Vibe-Check-Validation-Plan-STDIO-Summary.md` | Executive summary |
| `docs/Vibe-Check-Validation-Plan-STDIO-Roadmap.md` | Visual roadmap |
| `scripts/Test-VibeCheck-STDIO.ps1` | Main test harness (to create) |
| `logs/vibe-check-stdio-validation-*/` | Evidence bundle |
| `.vscode/mcp.json` | VS Code config (CLI-managed) |
| `.claude/mcp.json` | Claude Code config (CLI-managed) |

## ⚠️ Common Pitfalls to Avoid

1. **❌ DON'T** Skip Phase 1 environment validation
   - **✅ DO** Verify both editors connect before proceeding

2. **❌ DON'T** Test HTTP transport standalone
   - **✅ DO** Use stdio transport for all validation

3. **❌ DON'T** Run all tests at once initially
   - **✅ DO** Execute phase-by-phase with evidence review

4. **❌ DON'T** Ignore constitution empty return issue
   - **✅ DO** Capture detailed diagnostics for analysis

5. **❌ DON'T** Skip provider tests without documenting
   - **✅ DO** Mark as conditional and explain why skipped

## 🏆 CPI Methodology Quick Reference

### Optimal Dosage: 10-15% of workflow steps
- **MANDATORY checkpoints:** 4 per 8-phase workflow
  - Phase 0: Initialization
  - Phase 3: Pre-implementation
  - Phase 6: Execution preflight
  - Phase 8: Reflection
- **CONDITIONAL checkpoints:** 0-1 based on complexity
  - High uncertainty
  - Material plan changes
  - Risk escalation

### Research-Backed Results
- Success rate: 27% → 54% (2x improvement)
- Harmful actions: 83% → 42% (halved)
- Optimal pattern: Strategic placement, not continuous monitoring

## 🔍 Troubleshooting Quick Guide

| Issue | Quick Fix |
|-------|-----------|
| MCP not connecting | Restart editor, verify config with doctor |
| Constitution returns empty | Capture raw request/response for analysis |
| Tools not discovered | Check stdio transport in editor logs |
| Provider auth error | Verify API key in .env or shell environment |
| Timeout on vibe_check | Check network, verify provider key validity |

## 📈 Evidence Quality Checklist

Each JSONL log file must contain:
- [ ] Timestamp for every event (ISO 8601)
- [ ] Event type classification (test_start, tool_call, etc.)
- [ ] Phase and test identification
- [ ] Complete request payloads
- [ ] Complete response captures
- [ ] Assertion results (pass/fail)
- [ ] Error details when applicable
- [ ] Correlation IDs for tracing

## 🎓 Learning Capture Categories

1. **Complex Solution Bias** - Over-engineering
2. **Feature Creep** - Scope expansion
3. **Premature Implementation** - Acting before validation
4. **Misalignment** - Not following requirements
5. **Overtooling** - Using complex tools unnecessarily
6. **Preference** - Team/personal preferences
7. **Success** - Positive patterns to repeat

## 📞 Support Resources

- **Package:** @pv-bhat/vibe-check-mcp v2.7.1
- **Research:** CPI methodology paper (linked in README)
- **GitHub:** https://github.com/PV-Bhat/vibe-check-mcp-server
- **Documentation:** Package README and docs/
- **Local Config:** .vscode/mcp.json, .claude/mcp.json

---

**Status:** READY FOR EXECUTION
**Last Updated:** 2025-11-10
**Version:** 1.0
**Print This:** Keep handy during validation sessions!

## 🚧 Known Defect & Temporary Workaround (2025-11-10)

Issue: `update_constitution` returns success while `check_constitution` always returns empty (CLI 2.7.1 & 2.7.6, stdio). Blocks Phase 2 constitution tests.

Upstream Draft: `logs/IssueDraft-Constitution-Persistence.md` (prepared; pending submission).

Workaround (local only): Enable shim to unblock downstream test scenarios.

```powershell
$env:VIBE_CONSTITUTION_SHIM = '1'
pwsh -File scripts/Test-ConstitutionShim.ps1 -VerboseLogs
```

Shim Module: `scripts/ConstitutionShim.psm1` — Provides Set / Get / Reset functions mirroring expected persistence semantics.

Label all shim-derived results clearly; do not treat as authoritative. After upstream fix, run reconciliation and retire shim.
