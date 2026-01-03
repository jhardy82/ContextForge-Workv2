# CF-77 Resolution Plan: CF_CLI Research and Validation

**Status**: Active  
**Created**: 2025-12-03  
**Linear Issue**: [CF-77](https://linear.app/contextforge/issue/CF-77)  
**Parent Plan**: [CF-RESEARCH-AND-VALIDATION-PLAN.md](./CF-RESEARCH-AND-VALIDATION-PLAN.md)  
**Branch**: `fix/flaky-test-improvements-20251203`

---

## Executive Summary

CF-77 encompasses comprehensive research and validation for CF_CLI, organized into 8 sub-issues across 4 research tracks. This plan defines the execution sequence, dependencies, parallel workstreams, and success criteria for resolving all issues.

**Total Sub-Issues**: 8  
**Estimated Total Effort**: 13-19 hours  
**Parallel Tracks**: 2 (Research Track + Output Architecture Track)

---

## Issue Inventory

| Issue ID | Title | Priority | Estimate | Track | Status |
|----------|-------|----------|----------|-------|--------|
| CF-127 | Track 1: CF_CLI Surface & Workflows - Command Discovery | High | 2h | Research | Todo |
| CF-128 | Track 2: Architecture & Data Flows - CF_CORE Mapping | High | 3h | Research | Todo |
| CF-129 | Track 3: MCP Integration & Transport - Catalog & Policy | Medium | 2h | Research | Todo |
| CF-130 | Track 4: QSE/QSM Integration - Phase Mapping | Medium | 2h | Research | In Progress |
| CF-131 | Layer 1: Functional Validation Test Suite | High | 3h | Validation | Todo |
| CF-132 | Layer 1.5: PowerShell `cf` Wrapper Validation | Medium | 2h | Validation | Todo |
| CF-133 | Output Architecture: CFOutputFormatter Implementation | High | 3h | Output | In Progress |
| CF-134 | Output Architecture: PowerShell Integration & Hybrid Testing | Medium | 2h | Output | Todo |

---

## Dependency Graph

```
                    ┌─────────────────────────────────────────────┐
                    │           CF-77 (Parent Epic)               │
                    └─────────────────────────────────────────────┘
                                         │
            ┌────────────────────────────┼────────────────────────────┐
            │                            │                            │
            ▼                            ▼                            ▼
    ┌───────────────┐          ┌───────────────┐          ┌───────────────┐
    │ Research Track│          │Output Arch    │          │Validation     │
    │ (CF-127→130)  │          │(CF-133→134)   │          │(CF-131→132)   │
    └───────────────┘          └───────────────┘          └───────────────┘
            │                            │                            │
            ▼                            ▼                            ▼
    ┌───────────────┐          ┌───────────────┐          ┌───────────────┐
    │   CF-127      │          │   CF-133      │          │   CF-131      │
    │ CLI Discovery │◄─────────│ Output Format │──────────►│ Functional   │
    └───────────────┘          └───────────────┘          │ Tests        │
            │                          │                   └───────────────┘
            ▼                          │                          │
    ┌───────────────┐                  │                          ▼
    │   CF-128      │                  │                   ┌───────────────┐
    │ Architecture  │                  │                   │   CF-132      │
    └───────────────┘                  │                   │ PS Wrapper    │
            │                          │                   └───────────────┘
            ├───────────────────────────┘                          ▲
            ▼                                                      │
    ┌───────────────┐          ┌───────────────┐                   │
    │   CF-129      │          │   CF-134      │───────────────────┘
    │ MCP Catalog   │          │ PS Integration│
    └───────────────┘          └───────────────┘
            │
            ▼
    ┌───────────────┐
    │   CF-130      │
    │ QSE/QSM      │
    └───────────────┘
```

### Critical Dependencies

| Dependency | From | To | Nature |
|------------|------|-----|--------|
| CLI Discovery → Output | CF-127 | CF-133 | Output formatter must support all discovered commands |
| Output → Functional Tests | CF-133 | CF-131 | Tests validate output formatting behavior |
| Architecture → MCP | CF-128 | CF-129 | MCP catalog needs architecture context |
| PS Integration → PS Wrapper | CF-134 | CF-132 | PS wrapper tests depend on integration layer |

---

## Execution Strategy

### Phase 1: Foundation (Days 1-2)

**Parallel Workstreams:**

#### Workstream A: Research Foundation
1. **CF-127** (Track 1: CLI Discovery) - 2h
   - Enumerate all `cf_cli.py` commands via `--help`
   - Map commands to TaskMan-v2 operations
   - Document command categories
   - Output: Command matrix table

2. **CF-128** (Track 2: Architecture) - 3h  
   - Map CF_CLI → CF_CORE → DB layers
   - Document TaskMan-v2 entities
   - Identify authority rules
   - Output: Architecture diagrams

#### Workstream B: Output Architecture
3. **CF-133** (CFOutputFormatter) - 3h
   - Implement dual-mode output (Rich + JSON)
   - Create formatter classes
   - Integrate with existing CLI
   - Output: Working formatter module

**Phase 1 Gate**: CLI discovery complete + Architecture documented + Formatter functional

---

### Phase 2: Integration & Catalog (Days 3-4)

**Sequential with Overlap:**

4. **CF-129** (Track 3: MCP Catalog) - 2h
   - Catalog CF-related MCP tools
   - Document transport policy
   - Map CF_CLI and MCP overlap
   - Output: MCP tool catalog

5. **CF-130** (Track 4: QSE/QSM) - 2h
   - Map QSE phases to CF_CLI commands
   - Document quality expectations
   - Align with UTMW workflow
   - Output: QSE × CF_CLI matrix

6. **CF-134** (PS Integration) - 2h
   - Test CFOutputFormatter from PowerShell
   - Validate JSON parsing pipeline
   - Ensure hybrid architecture works
   - Output: Integration tests

**Phase 2 Gate**: All 4 research tracks complete + PS integration verified

---

### Phase 3: Validation (Days 5-6)

**Validation Test Implementation:**

7. **CF-131** (Functional Validation) - 3h
   - Create `tests/system/test_cf_cli_functional.py`
   - Happy path tests for all commands
   - Input validation tests
   - Error surface tests
   - Output: Comprehensive test suite

8. **CF-132** (PS Wrapper Validation) - 2h
   - Create Pester tests for `cf` wrapper
   - Test delegation, environment, output
   - Verify error handling
   - Output: Pester test suite

**Phase 3 Gate**: All validation layers implemented + Tests passing

---

## Detailed Issue Plans

### CF-127: Track 1 - CLI Discovery

**Objective**: Build complete inventory of CF_CLI commands and their behaviors

**Acceptance Criteria**:
- [ ] All `cf_cli.py` commands enumerated with descriptions
- [ ] Command categories defined (core, context, diagnostic)
- [ ] TaskMan-v2 operation mapping complete
- [ ] Gap analysis document produced
- [ ] PowerShell `cf` wrapper coverage documented

**Execution Steps**:
```bash
# 1. Enumerate top-level commands
python cf_cli.py --help > artifacts/cf_cli_help.txt

# 2. Enumerate each subcommand
python cf_cli.py task --help
python cf_cli.py project --help
python cf_cli.py sprint --help
python cf_cli.py status --help
python cf_cli.py context --help

# 3. Document command signatures and options
# 4. Create command matrix in docs/
```

**Deliverables**:
- `docs/reference/CF_CLI_COMMAND_MATRIX.md`
- `docs/reference/CF_CLI_GAP_ANALYSIS.md`

---

### CF-128: Track 2 - Architecture Mapping

**Objective**: Document CF_CLI → CF_CORE → DB architecture layers

**Acceptance Criteria**:
- [ ] CF_CLI ↔ CF_CORE ↔ DB context diagram created
- [ ] TaskMan-v2 entity relationships documented
- [ ] Data flow diagrams for task/project/sprint lifecycle
- [ ] Authority rules (PostgreSQL vs SQLite) documented

**Key Files to Analyze**:
- `cf_cli.py` - Entry point
- `src/cf_core/` - Core domain logic
- `src/cf_output_formatter.py` - Output formatting
- `python/cf_cli_database_config.py` - DB configuration
- TaskMan-v2 ORM models

**Deliverables**:
- `docs/architecture/CF_CLI_ARCHITECTURE.md`
- Mermaid diagrams for data flows
- Entity relationship documentation

---

### CF-129: Track 3 - MCP Catalog

**Objective**: Catalog MCP tools and document integration with CF

**Acceptance Criteria**:
- [ ] CF-related MCP tools cataloged
- [ ] Transport policy documented (STDIO-first)
- [ ] CF_CLI and MCP overlap points identified
- [ ] Health check patterns verified

**MCP Servers to Catalog**:
- `task-manager` - Task management (REQUIRES STARTUP)
- `database-mcp` - Database operations
- `git-mcp` - Git repository operations

**Deliverables**:
- `docs/reference/MCP_TOOL_CATALOG.md`
- `docs/reference/MCP_TRANSPORT_MATRIX.md`

---

### CF-130: Track 4 - QSE/QSM Integration

**Objective**: Map QSE/QSM phases to CF_CLI commands

**Acceptance Criteria**:
- [ ] QSE phases × CF_CLI commands matrix created
- [ ] Quality and evidence expectations documented
- [ ] UTMW workflow alignment verified
- [ ] E2E workflow validation list produced

**Key Documents**:
- `docs/plans/QSM-Implementation-Setup.md`
- `docs/plans/QSE-PM2-Migration-Implementation-Guide.md`
- UTMW workflow documentation

**Deliverables**:
- `docs/reference/QSE_CF_INTEGRATION_MATRIX.md`
- E2E workflow validation checklist

---

### CF-133: CFOutputFormatter Implementation

**Objective**: Implement dual-mode output architecture for CF_CLI

**Current State**: Partial implementation exists in `src/cf_output_formatter.py`

**Acceptance Criteria**:
- [ ] `CFOutputFormatter` class fully implemented
- [ ] Rich output mode functional (tables, panels, trees)
- [ ] JSON output mode functional (structured, machine-readable)
- [ ] Hybrid mode supports simultaneous output
- [ ] Error formatting standardized
- [ ] Integration with `cf_cli.py` complete

**Design Specifications**:
```python
class CFOutputFormatter:
    """Dual-mode output formatter for CF_CLI."""
    
    def __init__(self, output_format: OutputFormat = OutputFormat.RICH):
        ...
    
    def output_list(self, items: list, columns: list, title: str) -> None:
        """Output a list of items in table format."""
        ...
    
    def output_detail(self, item: dict, title: str) -> None:
        """Output detailed view of a single item."""
        ...
    
    def output_summary(self, operation: str, status: str, **details) -> None:
        """Output operation summary."""
        ...
    
    def output_error(self, error: str, remediation: list = None) -> None:
        """Output error with optional remediation steps."""
        ...
```

**Deliverables**:
- Completed `src/cf_output_formatter.py`
- Unit tests in `tests/unit/test_cf_output_formatter.py`
- Integration with `cf_cli.py` commands

---

### CF-134: PowerShell Integration Testing

**Objective**: Validate CFOutputFormatter works correctly from PowerShell

**Acceptance Criteria**:
- [ ] JSON output correctly parsed to PSObjects
- [ ] Error output captured and formatted
- [ ] Performance measurement integration works
- [ ] Hybrid architecture (PS → Python → PS) validated

**Test Scenarios**:
```powershell
# Test 1: JSON output parsing
$result = cf task list --json | ConvertFrom-Json
$result | Should -BeOfType [PSCustomObject]

# Test 2: Error handling
{ cf task show "INVALID-ID" } | Should -Throw

# Test 3: Performance measurement
$timing = Measure-Command { cf status }
$timing.TotalMilliseconds | Should -BeLessThan 500
```

**Deliverables**:
- Integration tests in `tests/pester/CFOutputFormatter.Integration.Tests.ps1`
- Performance baseline documentation

---

### CF-131: Functional Validation Test Suite

**Objective**: Create comprehensive functional tests for CF_CLI

**Acceptance Criteria**:
- [ ] Happy path tests for all commands
- [ ] Input validation tests
- [ ] Error surface tests
- [ ] pytest markers configured (`cf_cli`, `cf_cli_validation`, `cf_cli_errors`)

**Test Structure**:
```
tests/
├── system/
│   └── test_cf_cli_functional.py
├── integration/
│   └── test_cf_integration.py
└── e2e/
    └── test_cf_workflows.py
```

**Test Categories**:
| Category | Description | Count Target |
|----------|-------------|--------------|
| Happy path | Expected inputs → expected outputs | 15-20 tests |
| Validation | Missing/invalid args handled | 10-15 tests |
| Error surfaces | DB unreachable, MCP unavailable | 5-10 tests |

**Deliverables**:
- `tests/system/test_cf_cli_functional.py`
- Test documentation in `docs/testing/CF_CLI_TEST_COVERAGE.md`

---

### CF-132: PowerShell Wrapper Validation

**Objective**: Validate PowerShell `cf` wrapper functions correctly

**Acceptance Criteria**:
- [ ] `cf` alias exported and functional
- [ ] `Invoke-CFCommand` delegates correctly
- [ ] JSON parsing for `--json` outputs works
- [ ] Error handling captures Python errors
- [ ] Venv detection works correctly

**Pester Test Structure**:
```powershell
Describe "CF Wrapper" {
    Context "Delegation" {
        It "cf task list calls python cf_cli.py task list" { }
    }
    Context "Environment" {
        It "Detects .venv correctly" { }
    }
    Context "Output" {
        It "Parses JSON output to PSObjects" { }
    }
    Context "Errors" {
        It "Surfaces Python errors correctly" { }
    }
}
```

**Deliverables**:
- `tests/pester/ContextForge.PythonIntegration.Tests.ps1`
- Wrapper command matrix documentation

---

## Risk Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Output formatter breaks existing CLI | High | Medium | Comprehensive tests before integration |
| MCP server unavailable during testing | Medium | Low | Mock MCP responses, document skip conditions |
| PS wrapper path resolution fails | Medium | Medium | Multiple fallback paths, clear error messages |
| Test infrastructure gaps | Medium | Medium | Use existing task infrastructure for testing |
| Time estimate overflow | Medium | Medium | Phase gates allow scope adjustment |

---

## Success Criteria

### Phase 1 Complete When:
- [ ] CF-127 deliverables produced
- [ ] CF-128 deliverables produced
- [ ] CF-133 formatter passing unit tests

### Phase 2 Complete When:
- [ ] CF-129 deliverables produced
- [ ] CF-130 deliverables produced
- [ ] CF-134 integration tests passing

### Phase 3 Complete When:
- [ ] CF-131 functional tests passing (≥90% pass rate)
- [ ] CF-132 Pester tests passing
- [ ] All 8 sub-issues closed in Linear

### CF-77 Resolution Complete When:
- [ ] All 8 sub-issues marked Done
- [ ] Documentation reviewed and merged
- [ ] Test suites integrated into CI
- [ ] CF_CLI validated against all research findings

---

## Execution Commands Reference

### Quick Start

```bash
# Activate environment
& ".venv/Scripts/Activate.ps1"

# Run CF-133 output formatter tests
pytest tests/unit/test_cf_output_formatter.py -v

# Run functional tests (CF-131)
pytest tests/system/test_cf_cli_functional.py -v

# Run Pester tests (CF-132)
Invoke-Pester tests/pester/ContextForge.PythonIntegration.Tests.ps1 -Tag CFWrapper
```

### CI Integration

```yaml
# Quality gate for CF changes
- pytest tests/ -m "cf_cli" -v
- Invoke-Pester -Tag CFWrapper
- ruff check src/cf_output_formatter.py
- mypy src/cf_output_formatter.py --strict
```

---

## Appendix: Linear Issue Links

| Issue | Link |
|-------|------|
| CF-77 | [Parent Epic](https://linear.app/contextforge/issue/CF-77) |
| CF-127 | [Track 1: CLI Discovery](https://linear.app/contextforge/issue/CF-127) |
| CF-128 | [Track 2: Architecture](https://linear.app/contextforge/issue/CF-128) |
| CF-129 | [Track 3: MCP Catalog](https://linear.app/contextforge/issue/CF-129) |
| CF-130 | [Track 4: QSE/QSM](https://linear.app/contextforge/issue/CF-130) |
| CF-131 | [Layer 1: Functional Tests](https://linear.app/contextforge/issue/CF-131) |
| CF-132 | [Layer 1.5: PS Wrapper](https://linear.app/contextforge/issue/CF-132) |
| CF-133 | [Output Architecture](https://linear.app/contextforge/issue/CF-133) |
| CF-134 | [PS Integration](https://linear.app/contextforge/issue/CF-134) |

---

**Document Version**: 1.0.0  
**Last Updated**: 2025-12-03  
**Author**: Cognitive Architect Agent (Opus 4)
