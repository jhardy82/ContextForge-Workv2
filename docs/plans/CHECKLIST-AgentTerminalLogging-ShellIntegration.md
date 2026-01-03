# AgentTerminalLogging Shell Integration - Implementation Checklist

> **Implementation Order**: Option A — Shell integration first (enables immediate test validation)

---

## 📊 Project Dashboard

| Metric | Value | Target | Status |
|--------|-------|--------|:------:|
| **Overall Progress** | 0/32 | 32 tasks | 🔴 0% |
| **P0 Critical Tasks** | 0/14 | 14 tasks | 🔴 0% |
| **P1 High Tasks** | 0/12 | 12 tasks | 🔴 0% |
| **P2 Nice-to-have** | 0/6 | 6 tasks | 🔴 0% |
| **Estimated LOC** | 0/~310 | ~310 lines | 🔴 0% |
| **Test Coverage** | 0/10 | 10 new tests | 🔴 0% |

### Timeline

```text
Started:  2025-11-28  ████████████████████░░░░░░░░░░  Target: 2025-11-29
          Phase 1 ──▶ Phase 2 ──▶ Phase 3 ──▶ Phase 4 ──▶ Phase 5 ──▶ Phase 6
          [CURRENT]
```

### Blocking Issues

| ID | Issue | Blocker | Impact | Resolution |
|:--:|-------|---------|--------|------------|
| — | *None currently* | — | — | — |

---

## 🎯 Phase 1: Shell Integration Detection Functions

**Goal**: Implement 3 new detection functions in `AgentTerminalLogging.psm1`
**Estimated LOC**: ~125 | **Priority**: P0 Critical | **Status**: ⬜ Not Started

### Prerequisites

- [ ] Verify `modules/Agent/AgentTerminalLogging.psm1` exists and is writable
- [ ] Review [Shell Integration Recommendations](../research/AgentTerminalLogging-Shell-Integration-Recommendations.md)

### Tasks

| ID | Task | Est. LOC | Priority | Depends | Status | Notes |
|:--:|------|:--------:|:--------:|:-------:|:------:|-------|
| 1.1 | **Create `Test-VSCodeShellIntegration` function** | ~35 | P0 | — | ⬜ | Detect VS Code shell integration via env vars |
| 1.1.1 | ↳ Check `$env:TERM_PROGRAM -eq 'vscode'` | — | P0 | — | ⬜ | Primary detection |
| 1.1.2 | ↳ Check `$env:VSCODE_SHELL_INTEGRATION` | — | P0 | — | ⬜ | Secondary detection |
| 1.1.3 | ↳ Return `[PSCustomObject]` with detection details | — | P0 | 1.1.1-1.1.2 | ⬜ | Include version info if available |
| 1.2 | **Create `Remove-EscapeSequences` function** | ~45 | P0 | — | ⬜ | Strip ANSI/OSC escape sequences |
| 1.2.1 | ↳ Handle OSC 633 sequences (VS Code shell integration) | — | P0 | — | ⬜ | `\x1b]633;.*?\x07` pattern |
| 1.2.2 | ↳ Handle standard ANSI CSI sequences | — | P0 | — | ⬜ | `\x1b\[[\d;]*[A-Za-z]` pattern |
| 1.2.3 | ↳ Handle SGR (color) sequences | — | P1 | — | ⬜ | `\x1b\[\d*(;\d+)*m` pattern |
| 1.2.4 | ↳ Preserve newlines and whitespace | — | P0 | — | ⬜ | Important for log formatting |
| 1.3 | **Create `Test-ShellIntegrationHealth` function** | ~45 | P0 | 1.1 | ⬜ | Comprehensive health check |
| 1.3.1 | ↳ Check for escape sequence pollution in output | — | P0 | 1.2 | ⬜ | Detect malformed sequences |
| 1.3.2 | ↳ Validate terminal capabilities | — | P1 | 1.1 | ⬜ | `$Host.UI.SupportsVirtualTerminal` |
| 1.3.3 | ↳ Return health status object with recommendations | — | P0 | 1.3.1-1.3.2 | ⬜ | Actionable diagnostics |
| 1.4 | **Add function exports to module manifest** | ~5 | P0 | 1.1-1.3 | ⬜ | Update `.psd1` if exists |
| 1.5 | **Validate module loads without errors** | — | P0 | 1.4 | ⬜ | `Import-Module -Force` test |

### Acceptance Criteria
- [ ] All 3 functions implemented and exported
- [ ] No errors on `Import-Module AgentTerminalLogging -Force`
- [ ] Functions return expected types (documented)
- [ ] Help comments included for all functions

---

## 🔧 Phase 2: Enhance Existing Logging Functions

**Goal**: Update 3 existing functions with shell integration awareness
**Estimated LOC**: ~60 | **Priority**: P1 High | **Status**: ⬜ Not Started

### Prerequisites
- [ ] Phase 1 complete (functions available)
- [ ] Backup of existing function implementations

### Tasks

| ID | Task | Est. LOC | Priority | Depends | Status | Notes |
|:--:|------|:--------:|:--------:|:-------:|:------:|-------|
| 2.1 | **Add `-PreserveEscapeSequences` switch to `Write-AgentLog`** | ~15 | P1 | 1.2 | ⬜ | Default: auto-clean |
| 2.1.1 | ↳ Add `[switch]$PreserveEscapeSequences` parameter | — | P1 | — | ⬜ | Parameter definition |
| 2.1.2 | ↳ Add conditional call to `Remove-EscapeSequences` | — | P1 | 1.2 | ⬜ | When switch is `$false` |
| 2.2 | **Implement auto-cleaning logic in `Write-AgentLog`** | ~20 | P1 | 2.1 | ⬜ | Clean by default |
| 2.2.1 | ↳ Detect if running in VS Code terminal | — | P1 | 1.1 | ⬜ | Use `Test-VSCodeShellIntegration` |
| 2.2.2 | ↳ Apply cleaning only when VS Code detected | — | P1 | 2.2.1 | ⬜ | Avoid unnecessary processing |
| 2.3 | **Add shell integration status to `Start-AgentSessionLogging`** | ~10 | P1 | 1.1 | ⬜ | Log in `session_start` event |
| 2.3.1 | ↳ Call `Test-VSCodeShellIntegration` at session start | — | P1 | 1.1 | ⬜ | Capture environment state |
| 2.3.2 | ↳ Include detection result in session metadata | — | P1 | 2.3.1 | ⬜ | For debugging |
| 2.4 | **Add optional health check to `Enable-ErrorCounter`** | ~15 | P2 | 1.3 | ⬜ | Optional integration |
| 2.4.1 | ↳ Add `-RunHealthCheck` switch parameter | — | P2 | — | ⬜ | Opt-in behavior |
| 2.4.2 | ↳ Log health check results if enabled | — | P2 | 1.3 | ⬜ | Diagnostic output |
| 2.5 | **Verify backward compatibility** | — | P0 | 2.1-2.4 | ⬜ | No breaking changes |
| 2.5.1 | ↳ Test existing scripts still work | — | P0 | — | ⬜ | Regression testing |
| 2.5.2 | ↳ Verify default behavior unchanged | — | P0 | — | ⬜ | Unless explicitly opted-in |

### Acceptance Criteria
- [ ] All existing function signatures remain compatible
- [ ] New parameters are optional with sensible defaults
- [ ] Escape sequences cleaned from logs in VS Code by default
- [ ] Health check available but opt-in

---

## 🧪 Phase 3: Pester Test Coverage

**Goal**: Add 10+ new test cases for shell integration features
**Estimated Tests**: 10 | **Priority**: P0-P2 Mixed | **Status**: ⬜ Not Started

### Prerequisites
- [ ] Phases 1-2 complete
- [ ] Pester 5.x installed and configured

### Tasks

| ID | Task | Tests | Priority | Depends | Status | Notes |
|:--:|------|:-----:|:--------:|:-------:|:------:|-------|
| 3.1 | **Test `Test-VSCodeShellIntegration` detection** | 2 | P0 | 1.1 | ⬜ | Mock env vars |
| 3.1.1 | ↳ Test returns `$true` when VS Code env detected | 1 | P0 | — | ⬜ | Happy path |
| 3.1.2 | ↳ Test returns `$false` in non-VS Code environment | 1 | P0 | — | ⬜ | Negative case |
| 3.2 | **Test `Remove-EscapeSequences` with various inputs** | 3 | P0 | 1.2 | ⬜ | Edge cases |
| 3.2.1 | ↳ Test removes OSC 633 sequences | 1 | P0 | — | ⬜ | VS Code specific |
| 3.2.2 | ↳ Test removes ANSI color codes | 1 | P0 | — | ⬜ | Common case |
| 3.2.3 | ↳ Test preserves clean text unchanged | 1 | P0 | — | ⬜ | Passthrough case |
| 3.3 | **Test `Test-ShellIntegrationHealth` scenarios** | 2 | P0 | 1.3 | ⬜ | Health states |
| 3.3.1 | ↳ Test returns healthy status when no issues | 1 | P0 | — | ⬜ | Normal operation |
| 3.3.2 | ↳ Test returns warnings when issues detected | 1 | P0 | — | ⬜ | Degraded state |
| 3.4 | **Test `-PreserveEscapeSequences` switch behavior** | 2 | P1 | 2.1 | ⬜ | Switch functionality |
| 3.4.1 | ↳ Test sequences preserved when switch is `$true` | 1 | P1 | — | ⬜ | Opt-in |
| 3.4.2 | ↳ Test sequences removed when switch is `$false` | 1 | P1 | — | ⬜ | Default behavior |
| 3.5 | **Integration test with mock VS Code environment** | 1 | P2 | 3.1-3.4 | ⬜ | Full integration |
| 3.5.1 | ↳ Set up mock environment with skip condition | 1 | P2 | — | ⬜ | `$env:TERM_PROGRAM` mock |
| 3.6 | **Run full test suite and verify pass rate** | — | P0 | 3.5 | ⬜ | ≥95% pass rate |

### Test Data Samples

```powershell
# OSC 633 escape sequence (VS Code shell integration)
$osc633Sample = "`e]633;C`a`e]633;D;0`a"

# ANSI color escape sequence
$ansiColorSample = "`e[32mGreen Text`e[0m"

# Mixed content
$mixedSample = "`e]633;A`aHello `e[31mWorld`e[0m`e]633;B`a"
```

### Acceptance Criteria
- [ ] All 10 tests written and passing
- [ ] Code coverage for new functions ≥80%
- [ ] Tests run in CI/CD pipeline
- [ ] Integration test skips gracefully outside VS Code

---

## 📚 Phase 4: Documentation

**Goal**: Create module documentation and update indexes
**Files**: 2 | **Priority**: P1-P2 | **Status**: ⬜ Not Started

### Prerequisites
- [ ] Phases 1-3 complete (features implemented and tested)

### Tasks

| ID | Task | Priority | Depends | Status | Notes |
|:--:|------|:--------:|:-------:|:------:|-------|
| 4.1 | **Create `modules/Agent/README.md`** | P1 | 2.5 | ⬜ | Module documentation |
| 4.1.1 | ↳ Module overview and purpose | P1 | — | ⬜ | What and why |
| 4.1.2 | ↳ Installation and import instructions | P1 | — | ⬜ | How to use |
| 4.1.3 | ↳ Function reference with examples | P1 | — | ⬜ | All exported functions |
| 4.1.4 | ↳ VS Code shell integration section | P1 | — | ⬜ | Special considerations |
| 4.2 | **Add VS Code troubleshooting section** | P2 | 4.1 | ⬜ | Common issues |
| 4.2.1 | ↳ Escape sequence pollution symptoms | P2 | — | ⬜ | How to identify |
| 4.2.2 | ↳ Resolution steps and workarounds | P2 | — | ⬜ | How to fix |
| 4.2.3 | ↳ Health check usage guide | P2 | — | ⬜ | Diagnostic workflow |
| 4.3 | **Update `modules/README.md` index** | P1 | 4.1 | ⬜ | Add Agent module entry |

### Acceptance Criteria
- [ ] README follows project documentation standards
- [ ] All new functions documented with examples
- [ ] Troubleshooting covers common VS Code issues
- [ ] Index updated with new module reference

---

## 🐍 Phase 5: TaskMan-v2 Python MCP Scaffold

**Goal**: Create initial Python MCP server structure with 37 tool stubs
**Files**: ~13 | **Priority**: P0-P1 | **Status**: ⬜ Not Started

### Prerequisites
- [ ] Review [RESEARCH-REPORT.md](../../TaskMan-v2/mcp-server-py/docs/RESEARCH-REPORT.md)
- [ ] Review [PYPROJECT-TEMPLATE.md](../../TaskMan-v2/mcp-server-py/PYPROJECT-TEMPLATE.md)
- [ ] Python 3.11+ installed

### Tasks

| ID | Task | Files | Priority | Depends | Status | Notes |
|:--:|------|:-----:|:--------:|:-------:|:------:|-------|
| 5.1 | **Create `pyproject.toml` from template** | 1 | P0 | — | ⬜ | Project configuration |
| 5.1.1 | ↳ Configure dependencies (fastmcp, pydantic, etc.) | — | P0 | — | ⬜ | Core deps |
| 5.1.2 | ↳ Configure dev dependencies (pytest, ruff, etc.) | — | P1 | — | ⬜ | Dev tooling |
| 5.2 | **Scaffold FastMCP server configuration** | 2 | P0 | 5.1 | ⬜ | Server setup |
| 5.2.1 | ↳ Create `src/taskman_mcp/__init__.py` | 1 | P0 | — | ⬜ | Package init |
| 5.2.2 | ↳ Create `src/taskman_mcp/server.py` | 1 | P0 | — | ⬜ | FastMCP server |
| 5.3 | **Create 37 tool stubs per RESEARCH-REPORT.md** | ~10 | P1 | 5.2 | ⬜ | Tool definitions |
| 5.3.1 | ↳ Task management tools (create, read, update, delete) | 2 | P1 | — | ⬜ | CRUD operations |
| 5.3.2 | ↳ Sprint management tools | 2 | P1 | — | ⬜ | Sprint lifecycle |
| 5.3.3 | ↳ Project management tools | 2 | P1 | — | ⬜ | Project operations |
| 5.3.4 | ↳ Context management tools | 2 | P1 | — | ⬜ | COF/UCL tools |
| 5.3.5 | ↳ Evidence bundle tools | 2 | P1 | — | ⬜ | Evidence operations |
| 5.4 | **Validate server starts without errors** | — | P0 | 5.3 | ⬜ | Smoke test |
| 5.4.1 | ↳ Run `python -m taskman_mcp` | — | P0 | — | ⬜ | Basic startup |
| 5.4.2 | ↳ Verify tool list in MCP inspector | — | P1 | — | ⬜ | Tool registration |

### Tool Categories (37 Total)

| Category | Count | Files | Status |
|----------|:-----:|:-----:|:------:|
| Task Management | 8 | `tools/tasks.py` | ⬜ |
| Sprint Management | 6 | `tools/sprints.py` | ⬜ |
| Project Management | 5 | `tools/projects.py` | ⬜ |
| Context Management | 6 | `tools/contexts.py` | ⬜ |
| Evidence Bundles | 4 | `tools/evidence.py` | ⬜ |
| Velocity Tracking | 4 | `tools/velocity.py` | ⬜ |
| Health & Status | 4 | `tools/health.py` | ⬜ |
| **Total** | **37** | **7 files** | ⬜ |

### Acceptance Criteria
- [ ] `pyproject.toml` valid and installable
- [ ] Server starts without import errors
- [ ] All 37 tools registered (stubs OK)
- [ ] Basic type hints on all tool functions

---

## 🧹 Phase 6: Commit & Cleanup

**Goal**: Stage, commit, and clean up orphaned files
**Priority**: P0-P2 | **Status**: ⬜ Not Started

### Prerequisites
- [ ] Phases 1-5 complete
- [ ] All tests passing

### Tasks

| ID | Task | Priority | Depends | Status | Notes |
|:--:|------|:--------:|:-------:|:------:|-------|
| 6.1 | **Move orphaned `EvidenceBundle.*.jsonl` files** | P2 | — | ⬜ | 17+ files |
| 6.1.1 | ↳ Create `.QSE/v2/Evidence/orphaned/` directory | P2 | — | ⬜ | If not exists |
| 6.1.2 | ↳ Move files preserving timestamps | P2 | — | ⬜ | `Move-Item -Force` |
| 6.1.3 | ↳ Verify files moved successfully | P2 | — | ⬜ | Count validation |
| 6.2 | **Stage all changes** | P0 | 1-5 | ⬜ | `git add` |
| 6.2.1 | ↳ Review staged changes | P0 | — | ⬜ | `git diff --staged` |
| 6.2.2 | ↳ Verify no unintended files | P0 | — | ⬜ | Check `.gitignore` |
| 6.3 | **Commit with conventional format** | P0 | 6.2 | ⬜ | Conventional commit |
| 6.3.1 | ↳ Write descriptive commit message | P0 | — | ⬜ | See template below |
| 6.3.2 | ↳ Reference related issues/PRs | P1 | — | ⬜ | If applicable |

### Commit Message Template

```
feat(logging): add VS Code shell integration detection

- Add Test-VSCodeShellIntegration function for environment detection
- Add Remove-EscapeSequences function for log cleaning
- Add Test-ShellIntegrationHealth for diagnostics
- Update Write-AgentLog with -PreserveEscapeSequences switch
- Add 10 Pester tests for new functionality
- Create module documentation

BREAKING CHANGE: None (backward compatible)
```

### Acceptance Criteria
- [ ] All files staged correctly
- [ ] Commit message follows conventional format
- [ ] No orphaned evidence bundles in root directory
- [ ] Clean working tree after commit

---

## 📋 Tracking Reference

### Status Legend

| Symbol | Meaning | When to Use |
|:------:|---------|-------------|
| ⬜ | Not started | Task not yet begun |
| 🔄 | In progress | Currently working on |
| ✅ | Complete | Done and verified |
| ❌ | Blocked | Cannot proceed (see Blocking Issues) |
| ⏭️ | Skipped | Intentionally skipped (document reason) |
| ⚠️ | At risk | May not complete on time |

### Priority Definitions

| Level | Name | Description | SLA |
|:-----:|------|-------------|-----|
| P0 | Critical | Blocks other work, must complete | Same day |
| P1 | High | Important, should complete | Within sprint |
| P2 | Nice-to-have | Can defer if needed | Best effort |

### Progress Calculation

```
Overall: (Completed Tasks / Total Tasks) × 100%
Phase:   (Completed in Phase / Total in Phase) × 100%

Weight by Priority:
  P0 = 3x weight
  P1 = 2x weight  
  P2 = 1x weight

Weighted Progress = Σ(completed × weight) / Σ(total × weight) × 100%
```

---

## 🔗 Related Documents

| Document | Purpose | Location |
|----------|---------|----------|
| Implementation Plan | High-level plan | `docs/plans/plan-agentTerminalLoggingShellIntegration.prompt.md` |
| Shell Integration Research | Technical recommendations | `docs/research/AgentTerminalLogging-Shell-Integration-Recommendations.md` |
| MCP Research Report | Python MCP architecture | `TaskMan-v2/mcp-server-py/docs/RESEARCH-REPORT.md` |
| Pyproject Template | Python project config | `TaskMan-v2/mcp-server-py/PYPROJECT-TEMPLATE.md` |

---

## 📝 Session Notes

### 2025-11-28: Checklist Created

- Created comprehensive checklist from plan
- Decided on Option A (Shell integration first)
- Identified 32 total tasks across 6 phases
- Estimated ~310 LOC for implementation

---

*Last Updated: 2025-11-28 | Version: 1.0.0*
