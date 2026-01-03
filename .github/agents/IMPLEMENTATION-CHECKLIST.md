# VS Code Custom Agent System Implementation Checklist

**Project**: ContextForge Custom Agent Architecture  
**Branch**: `feat/taskman-v2-python-mcp-research-20251125`  
**Created**: 2025-11-28  
**Last Updated**: 2025-11-28 @ 00:55 EST  
**Owner**: @jhardy82  
**Status**: 🟡 In Progress (Phase 1.2 Active)

---

## Research Reports & References

| Document | Path | Description |
|----------|------|-------------|
| TPR Phase 2 Research Summary | `artifacts/PHASE2-TPR-DEVOPS-RESEARCH-EXECUTIVE-SUMMARY.md` | DevOps and CI/CD research findings |
| Cross-OS Performance Analysis | `artifacts/PHASE2-TPR-CROSS-OS-PERFORMANCE-RESEARCH-SYNTHESIS.md` | Performance testing across platforms |
| Coverage Ladder Research | `artifacts/PHASE2-TPR-COVERAGE-LADDER-RESEARCH-SYNTHESIS.md` | Test coverage strategies |
| Marker Systems Audit | `artifacts/MARKER-SYSTEMS-AUDIT-RESEARCH-REPORT.md` | Pytest marker system analysis |
| Pytest Reliability Study | `research-pytest-reliability-parallelization-2024.md` | Pytest reliability patterns |

---

## Tracking Legend

| Symbol | Meaning |
|--------|---------|
| ⬜ | Not Started |
| 🔄 | In Progress |
| ✅ | Completed |
| ❌ | Blocked |
| ⏸️ | Paused |
| 🔍 | Under Review |
| ⚠️ | Needs Attention |

**Priority Levels**: P0 (Critical) | P1 (High) | P2 (Medium) | P3 (Low)

---

## Phase 1: VS Code Parsing Issue Resolution

**Objective**: Eliminate VS Code extension errors in agent files  
**Estimated Duration**: 1-2 hours  
**Dependencies**: None  
**Risk Level**: 🟡 Medium

### 1.1 Diagnostic Analysis

| # | Task | Priority | Status | Assignee | Started | Completed | Duration | Notes |
|---|------|----------|--------|----------|---------|-----------|----------|-------|
| 1.1.1 | Create minimal `.agent.md` reproduction file | P0 | ✅ | @copilot | 2025-11-28 | 2025-11-28 | 5m | Template.agent.md created |
| 1.1.2 | Compare byte-level structure with working file (`coder.agent.md`) | P0 | ✅ | @copilot | 2025-11-28 | 2025-11-28 | 10m | Block scalar vs quoted identified |
| 1.1.3 | Test VS Code extension cache clearing | P1 | ✅ | @copilot | 2025-11-28 | 2025-11-28 | 3m | Reload verified fixes |
| 1.1.4 | Document exact error messages and line numbers | P0 | ✅ | @copilot | 2025-11-28 | 2025-11-28 | 5m | YAML parsing error on `prompt: \|` |
| 1.1.5 | Identify pattern: which files error vs which don't | P1 | ✅ | @copilot | 2025-11-28 | 2025-11-28 | 10m | All `prompt: \|` files error |

**Phase 1.1 Acceptance Criteria**:
- [x] Root cause identified: Block scalar `prompt: |` causes parsing errors
- [x] Reproduction steps documented: Any `prompt: |` with multiline content fails
- [x] Pattern analysis complete: All 27 files audited

---

### 1.2 Workaround Implementation

| # | Task | Priority | Status | Assignee | Started | Completed | Duration | Notes |
|---|------|----------|--------|----------|---------|-----------|----------|-------|
| 1.2.1 | Test alternative YAML syntax: quoted strings vs block scalar | P0 | ✅ | @copilot | 2025-11-28 | 2025-11-28 | 5m | Quoted strings work perfectly |
| 1.2.2 | Test with reduced handoff count per file | P1 | ✅ | @copilot | 2025-11-28 | 2025-11-28 | 5m | N/A - issue is syntax not count |
| 1.2.3 | Test different indentation patterns | P1 | ✅ | @copilot | 2025-11-28 | 2025-11-28 | 3m | 2-space consistent works |
| 1.2.4 | Apply successful workaround to all 27 agent files | P0 | 🔄 | @copilot | 2025-11-28 | | | **16/27 complete (60%)** |
| 1.2.5 | Verify each file parses cleanly in VS Code | P0 | 🔄 | @copilot | 2025-11-28 | | | Verified as each file fixed |

**Conversion Status Matrix**:
| Status | Files |
|--------|-------|
| ✅ FIXED (16) | `coder`, `orchestrator`, `database`, `devops`, `researcher`, `Template`, `CF-Enhanced-Thinking-Beast-Mode`, `cof-13d-analyst`, `evidence-bundle`, `implementer`, `qa-reviewer`, `scientific-method`, `strategic-planner`, `task-workflow-validation-swarm`, `troop-leading`, `ultimate-cognitive-architecture`, `Ultimate-Transparent-Thinking-Beast-Mode-Enhanced` |
| ⚠️ NEEDS FIX (10) | `architect`, `documenter`, `frontend`, `performance`, `planner`, `powershell`, `refactor`, `reviewer`, `security`, `tester` |

**Phase 1.2 Acceptance Criteria**:
- [ ] All 27 agent files show 0 parsing errors (16/27 complete)
- [x] Workaround documented: Use `prompt: "..."` instead of `prompt: |`
- [x] No functionality lost from workaround

---

### 1.3 Bug Documentation (If Unresolvable)

| # | Task | Priority | Status | Assignee | Started | Completed | Duration | Notes |
|---|------|----------|--------|----------|---------|-----------|----------|-------|
| 1.3.1 | Create GitHub issue template for Copilot extension | P2 | ⏸️ | | | | | Not needed - workaround found |
| 1.3.2 | Document workaround in `AGENTS.md` | P1 | ⬜ | | | | | Under Troubleshooting section |
| 1.3.3 | Add inline comment to affected agent files | P2 | ✅ | @copilot | 2025-11-28 | 2025-11-28 | 2m | Using quoted string format |
| 1.3.4 | File issue with GitHub Copilot extension team | P3 | ⏸️ | | | | | Workaround sufficient |

**Phase 1.3 Acceptance Criteria**:
- [x] Bug documented with reproduction steps (block scalar causes parsing errors)
- [x] Workaround clearly explained (use quoted strings)
- [ ] Issue filed (if applicable) - Paused, workaround is sufficient

---

### Phase 1 Summary

| Metric | Target | Actual |
|--------|--------|--------|
| Total Tasks | 14 | 14 |
| Completed | 14 | 11 |
| In Progress | 0 | 2 |
| Paused | 0 | 1 |
| Duration | 1-2 hrs | ~1.5 hrs |
| Blockers | 0 | 0 |

**Phase 1 Sign-off**: 🔄 In Progress (79% complete, 10 agent files remaining)

---

## Phase 1.5: Remaining Agent File Conversions (NEW)

**Objective**: Complete conversion of remaining 10 agent files  
**Estimated Duration**: 30-45 minutes  
**Dependencies**: Phase 1.2 method validated  
**Risk Level**: 🟢 Low (method proven)

### Remaining Files Conversion

| # | File | Priority | Status | Notes |
|---|------|----------|--------|-------|
| 1.5.1 | `architect.agent.md` | P0 | ⬜ | Convert `prompt: \|` to quoted |
| 1.5.2 | `documenter.agent.md` | P0 | ⬜ | Convert `prompt: \|` to quoted |
| 1.5.3 | `frontend.agent.md` | P0 | ⬜ | Convert `prompt: \|` to quoted |
| 1.5.4 | `performance.agent.md` | P0 | ⬜ | Convert `prompt: \|` to quoted |
| 1.5.5 | `planner.agent.md` | P0 | ⬜ | Convert `prompt: \|` to quoted |
| 1.5.6 | `powershell.agent.md` | P0 | ⬜ | Convert `prompt: \|` to quoted |
| 1.5.7 | `refactor.agent.md` | P0 | ⬜ | Convert `prompt: \|` to quoted |
| 1.5.8 | `reviewer.agent.md` | P0 | ⬜ | Convert `prompt: \|` to quoted |
| 1.5.9 | `security.agent.md` | P0 | ⬜ | Convert `prompt: \|` to quoted |
| 1.5.10 | `tester.agent.md` | P0 | ⬜ | Convert `prompt: \|` to quoted |

**Phase 1.5 Acceptance Criteria**:
- [ ] All 10 remaining files converted to quoted string format
- [ ] VS Code shows 0 parsing errors for all 27 files
- [ ] Commit with clear message

---

## Phase 2: Agent Handoff Validation

**Objective**: Verify handoff chains work correctly in practice  
**Estimated Duration**: 2-3 hours  
**Dependencies**: Phase 1 Complete  
**Risk Level**: 🟡 Medium

### 2.1 Test Scenario Definition

| # | Task | Priority | Status | Assignee | Started | Completed | Duration | Notes |
|---|------|----------|--------|----------|---------|-----------|----------|-------|
| 2.1.1 | Define Feature Flow test case | P0 | ⬜ | | | | | orchestrator→planner→coder→reviewer→tester |
| 2.1.2 | Define Bug Fix Flow test case | P0 | ⬜ | | | | | debug→coder→tester→reviewer |
| 2.1.3 | Define Database Flow test case | P0 | ⬜ | | | | | planner→database→coder→reviewer |
| 2.1.4 | Create sample task inputs for each flow | P1 | ⬜ | | | | | Realistic scenarios |
| 2.1.5 | Document expected outputs per agent in chain | P1 | ⬜ | | | | | Success criteria |

**Phase 2.1 Acceptance Criteria**:
- [ ] 3 test flows fully defined
- [ ] Input/output expectations documented
- [ ] Test data prepared

---

### 2.2 Test Execution

| # | Task | Priority | Status | Assignee | Started | Completed | Duration | Notes |
|---|------|----------|--------|----------|---------|-----------|----------|-------|
| 2.2.1 | Execute Feature Flow: Start with orchestrator | P0 | ⬜ | | | | | Record full conversation |
| 2.2.2 | Execute Feature Flow: Handoff to planner | P0 | ⬜ | | | | | Verify context received |
| 2.2.3 | Execute Feature Flow: Handoff to coder | P0 | ⬜ | | | | | Verify plan received |
| 2.2.4 | Execute Feature Flow: Handoff to reviewer | P0 | ⬜ | | | | | Verify code received |
| 2.2.5 | Execute Feature Flow: Handoff to tester | P0 | ⬜ | | | | | Verify review passed |
| 2.2.6 | Execute Bug Fix Flow: Complete chain | P0 | ⬜ | | | | | debug→coder→tester→reviewer |
| 2.2.7 | Execute Database Flow: Complete chain | P0 | ⬜ | | | | | planner→database→coder→reviewer |
| 2.2.8 | Document any context loss between handoffs | P0 | ⬜ | | | | | Critical finding |
| 2.2.9 | Document any handoff failures | P0 | ⬜ | | | | | Agent not found, etc. |
| 2.2.10 | Capture timing metrics for each handoff | P2 | ⬜ | | | | | Performance baseline |

**Phase 2.2 Acceptance Criteria**:
- [ ] All 3 test flows executed
- [ ] Context preservation verified at each step
- [ ] No critical failures blocking handoffs

---

### 2.3 Issue Resolution

| # | Task | Priority | Status | Assignee | Started | Completed | Duration | Notes |
|---|------|----------|--------|----------|---------|-----------|----------|-------|
| 2.3.1 | Fix handoff prompts lacking clarity | P1 | ⬜ | | | | | Based on test findings |
| 2.3.2 | Add missing context fields to handoff prompts | P1 | ⬜ | | | | | Ensure complete info transfer |
| 2.3.3 | Adjust `send: false` vs `send: true` settings | P1 | ⬜ | | | | | User control vs auto-send |
| 2.3.4 | Re-test fixed handoffs | P0 | ⬜ | | | | | Verify fixes work |
| 2.3.5 | Update agent files with fixes | P0 | ⬜ | | | | | Commit changes |

**Phase 2.3 Acceptance Criteria**:
- [ ] All identified issues resolved
- [ ] Re-tests pass
- [ ] Changes committed

---

### Phase 2 Summary

| Metric | Target | Actual |
|--------|--------|--------|
| Total Tasks | 20 | |
| Completed | 20 | |
| Duration | 2-3 hrs | |
| Blockers | 0 | |

**Phase 2 Sign-off**: ⬜ Not Complete

---

## Phase 3: Mode System Validation

**Objective**: Verify mode switching works correctly  
**Estimated Duration**: 1 hour  
**Dependencies**: None (can parallel with Phase 2)  
**Risk Level**: 🟢 Low

### 3.1 Mode Testing

| # | Task | Priority | Status | Assignee | Started | Completed | Duration | Notes |
|---|------|----------|--------|----------|---------|-----------|----------|-------|
| 3.1.1 | Test `plan` mode activation | P1 | ⬜ | | | | | Verify planner behavior |
| 3.1.2 | Test `code` mode activation | P1 | ⬜ | | | | | Verify coder behavior |
| 3.1.3 | Test `review` mode activation | P1 | ⬜ | | | | | Verify reviewer behavior |
| 3.1.4 | Test `test` mode activation | P1 | ⬜ | | | | | Verify tester behavior |
| 3.1.5 | Test `research` mode activation | P1 | ⬜ | | | | | Verify researcher behavior |
| 3.1.6 | Verify tool access per mode | P1 | ⬜ | | | | | Correct tools available |
| 3.1.7 | Verify mode-specific instructions apply | P1 | ⬜ | | | | | Behavior changes |
| 3.1.8 | Test mode switching mid-conversation | P2 | ⬜ | | | | | Context preserved |

**Phase 3.1 Acceptance Criteria**:
- [ ] All 5 modes activate correctly
- [ ] Tool access matches mode definition
- [ ] Instructions apply as expected

---

### 3.2 Mode Documentation

| # | Task | Priority | Status | Assignee | Started | Completed | Duration | Notes |
|---|------|----------|--------|----------|---------|-----------|----------|-------|
| 3.2.1 | Add mode descriptions to agent README | P2 | ⬜ | | | | | Brief explanation each |
| 3.2.2 | Create quick reference card for mode switching | P2 | ⬜ | | | | | One-liner commands |
| 3.2.3 | Document mode-specific tool access | P2 | ⬜ | | | | | Table format |

**Phase 3.2 Acceptance Criteria**:
- [ ] Mode documentation complete
- [ ] Quick reference usable

---

### Phase 3 Summary

| Metric | Target | Actual |
|--------|--------|--------|
| Total Tasks | 11 | |
| Completed | 11 | |
| Duration | 1 hr | |
| Blockers | 0 | |

**Phase 3 Sign-off**: ⬜ Not Complete

---

## Phase 4: Documentation

**Objective**: Create comprehensive agent system documentation  
**Estimated Duration**: 1-2 hours  
**Dependencies**: Phases 2-3 Complete  
**Risk Level**: 🟢 Low

### 4.1 Agent README Creation

| # | Task | Priority | Status | Assignee | Started | Completed | Duration | Notes |
|---|------|----------|--------|----------|---------|-----------|----------|-------|
| 4.1.1 | Create `.github/agents/README.md` | P1 | ⬜ | | | | | Main documentation |
| 4.1.2 | Document all 13 agents with descriptions | P1 | ⬜ | | | | | Table format |
| 4.1.3 | List handoff chains (who → whom) | P1 | ⬜ | | | | | Mermaid diagram |
| 4.1.4 | Document tool access per agent | P2 | ⬜ | | | | | Reference table |
| 4.1.5 | Include usage examples | P2 | ⬜ | | | | | Common scenarios |
| 4.1.6 | Add troubleshooting section | P2 | ⬜ | | | | | Known issues |

**Phase 4.1 Acceptance Criteria**:
- [ ] README comprehensive and accurate
- [ ] All 13 agents documented
- [ ] Handoff chains visualized

---

### 4.2 AGENTS.md Update

| # | Task | Priority | Status | Assignee | Started | Completed | Duration | Notes |
|---|------|----------|--------|----------|---------|-----------|----------|-------|
| 4.2.1 | Add Custom Agent System section | P1 | ⬜ | | | | | New major section |
| 4.2.2 | Document mode system | P1 | ⬜ | | | | | How to use modes |
| 4.2.3 | Add troubleshooting section | P2 | ⬜ | | | | | VS Code issues |
| 4.2.4 | Link to detailed agent README | P2 | ⬜ | | | | | Cross-reference |

**Phase 4.2 Acceptance Criteria**:
- [ ] AGENTS.md updated
- [ ] Integration with existing docs

---

### 4.3 Quick Reference Guide

| # | Task | Priority | Status | Assignee | Started | Completed | Duration | Notes |
|---|------|----------|--------|----------|---------|-----------|----------|-------|
| 4.3.1 | Create one-page agent selection guide | P2 | ⬜ | | | | | Decision tree |
| 4.3.2 | Create handoff chain diagram (Mermaid) | P2 | ⬜ | | | | | Visual flowchart |
| 4.3.3 | Document common workflow patterns | P2 | ⬜ | | | | | 3-5 patterns |
| 4.3.4 | Create cheat sheet for agent commands | P3 | ⬜ | | | | | Copy-paste ready |

**Phase 4.3 Acceptance Criteria**:
- [ ] Quick reference created
- [ ] Diagram renders correctly
- [ ] Patterns documented

---

### Phase 4 Summary

| Metric | Target | Actual |
|--------|--------|--------|
| Total Tasks | 14 | |
| Completed | 14 | |
| Duration | 1-2 hrs | |
| Blockers | 0 | |

**Phase 4 Sign-off**: ⬜ Not Complete

---

## Phase 5: Final Validation & Merge

**Objective**: Complete final checks and merge to main  
**Estimated Duration**: 30 minutes  
**Dependencies**: All previous phases  
**Risk Level**: 🟢 Low

### 5.1 Final Checks

| # | Task | Priority | Status | Assignee | Started | Completed | Duration | Notes |
|---|------|----------|--------|----------|---------|-----------|----------|-------|
| 5.1.1 | Verify 0 parsing errors in VS Code | P0 | ⬜ | | | | | Full reload test |
| 5.1.2 | Run complete handoff test one more time | P0 | ⬜ | | | | | Smoke test |
| 5.1.3 | Review all documentation for accuracy | P1 | ⬜ | | | | | Spell check, links |
| 5.1.4 | Verify git status clean | P1 | ⬜ | | | | | All changes committed |
| 5.1.5 | Create PR description | P1 | ⬜ | | | | | Summary of changes |

**Phase 5.1 Acceptance Criteria**:
- [ ] All checks pass
- [ ] Ready for PR

---

### 5.2 Merge Process

| # | Task | Priority | Status | Assignee | Started | Completed | Duration | Notes |
|---|------|----------|--------|----------|---------|-----------|----------|-------|
| 5.2.1 | Create Pull Request | P0 | ⬜ | | | | | feat/taskman-v2... → main |
| 5.2.2 | Request review (if applicable) | P1 | ⬜ | | | | | Code review |
| 5.2.3 | Address review feedback | P1 | ⬜ | | | | | If any |
| 5.2.4 | Merge to main | P0 | ⬜ | | | | | Squash or merge |
| 5.2.5 | Verify deployment successful | P1 | ⬜ | | | | | If CI/CD applies |
| 5.2.6 | Delete feature branch | P3 | ⬜ | | | | | Cleanup |

**Phase 5.2 Acceptance Criteria**:
- [ ] PR merged successfully
- [ ] Main branch stable

---

### Phase 5 Summary

| Metric | Target | Actual |
|--------|--------|--------|
| Total Tasks | 11 | |
| Completed | 11 | |
| Duration | 30 min | |
| Blockers | 0 | |

**Phase 5 Sign-off**: ⬜ Not Complete

---

## Overall Progress Dashboard

### Task Summary

| Phase | Total Tasks | Completed | In Progress | Blocked | % Complete |
|-------|-------------|-----------|-------------|---------|------------|
| Phase 1: Parsing Resolution | 14 | 11 | 2 | 0 | 79% |
| Phase 1.5: Remaining Conversions | 10 | 0 | 0 | 0 | 0% |
| Phase 2: Handoff Validation | 20 | 0 | 0 | 0 | 0% |
| Phase 3: Mode Validation | 11 | 0 | 0 | 0 | 0% |
| Phase 4: Documentation | 14 | 0 | 0 | 0 | 0% |
| Phase 5: Final & Merge | 11 | 0 | 0 | 0 | 0% |
| **TOTAL** | **80** | **11** | **2** | **0** | **14%** |

### Timeline

| Phase | Estimated | Actual | Variance |
|-------|-----------|--------|----------|
| Phase 1 | 1-2 hrs | ~1.5 hrs | On track |
| Phase 1.5 | 0.5 hr | - | Not started |
| Phase 2 | 2-3 hrs | - | Not started |
| Phase 3 | 1 hr | - | Not started |
| Phase 4 | 1-2 hrs | - | Not started |
| Phase 5 | 0.5 hr | - | Not started |
| **TOTAL** | **6-9 hrs** | **~1.5 hrs** | |

### Risk Register

| Risk ID | Description | Probability | Impact | Status | Mitigation |
|---------|-------------|-------------|--------|--------|------------|
| R1 | VS Code extension bug unresolvable | Medium | High | ✅ Resolved | Quoted string format works |
| R2 | Handoff context loss | Low | High | ⬜ Open | Increase prompt context |
| R3 | Agent tool access denied | Low | Medium | ⬜ Open | Verify tool names |
| R4 | Mode switching not working | Low | Medium | ⬜ Open | Validate mode syntax |

### Blockers Log

| Blocker ID | Description | Phase | Raised | Resolved | Resolution |
|------------|-------------|-------|--------|----------|------------|
| B1 | YAML block scalar parsing | 1.1 | 2025-11-28 | 2025-11-28 | Use quoted strings instead of `prompt: \|` |

---

## Change Log

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-11-28 | 1.0 | @jhardy82 | Initial checklist created |
| 2025-11-28 | 1.1 | @copilot | Phase 1.1 complete, 1.2 60% done, added Phase 1.5 for remaining files, added research links |

---

## Appendix A: Agent Inventory

| Agent | File | Specialty | Handoffs To |
|-------|------|-----------|-------------|
| orchestrator | `orchestrator.agent.md` | Task routing | planner, coder, researcher |
| planner | `planner.agent.md` | Execution planning | coder, researcher |
| coder | `coder.agent.md` | Implementation | reviewer, tester, database |
| reviewer | `reviewer.agent.md` | Code review | coder, orchestrator |
| tester | `tester.agent.md` | Test creation | coder, reviewer |
| researcher | `researcher.agent.md` | Information gathering | planner, coder |
| database | `database.agent.md` | Schema design | coder, reviewer |
| api | `api.agent.md` | API design | coder, docs |
| devops | `devops.agent.md` | Infrastructure | coder, security |
| security | `security.agent.md` | Security review | coder, reviewer |
| ux | `ux.agent.md` | UX design | coder, docs |
| docs | `docs.agent.md` | Documentation | reviewer |
| debug | `debug.agent.md` | Issue diagnosis | coder, tester |

---

## Appendix B: Mode Inventory

| Mode | File | Behavior | Primary Tools |
|------|------|----------|---------------|
| plan | `plan.chatmode.md` | Strategic planning | SeqThinking, todos |
| code | `code.chatmode.md` | Implementation | edit, search, runTests |
| review | `review.chatmode.md` | Code review | search, problems |
| test | `test.chatmode.md` | Test creation | runTests, edit |
| research | `research.chatmode.md` | Information gathering | fetch, websearch |

---

*Last Updated: 2025-11-28*
