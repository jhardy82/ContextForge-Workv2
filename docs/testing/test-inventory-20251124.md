# Test Infrastructure Inventory (2025-11-24)

## Overview
Comprehensive cross-language inventory generated to support Phase 2 Reliability Expansion & Optimization. This document enumerates discovered test artifacts across Python (pytest) and PowerShell (Pester), plus configuration anchors (pytest.ini, pyproject.toml) and marker/tag usage.

## Summary Counts
- PowerShell Pester test files (`*.Tests.ps1`): 173
- Python test-related files under `tests/` and other creators (scripts generating tests): 381 (initial glob) + generator scripts (`create_all_qse_tests.py`, `create_remaining_qse_tests.py`, `create_test_files.py`)
- Pytest configuration files (`pytest.ini`): 5
- Python project configuration files (`pyproject.toml`): 4
- Distinct pytest markers encountered in initial scan sample (subset): asyncio, integration, unit, circle, triangle, spiral, fractal, pentagon, performance, dtm, critical, rich_terminal, gamification, migration, constitutional, contextforge, production, load, failover, mpv, mcp.

## Configuration Files
| File | Purpose |
|------|---------|
| `pytest.ini` (root) | Global pytest defaults & markers |
| `python/pytest.ini` | Python submodule / isolated test settings |
| `test_suite_20250930-2210/pytest.ini` | Historical snapshot suite config |
| `python/api/tests/pytest.ini` | API-specific test configuration |
| `projects/unified_logger/pytest.ini` | Logger project isolated config |
| Root `pyproject.toml` | Top-level tooling (ruff, mypy, packaging) |
| `analytics/pyproject.toml` | Analytics module dependencies/tooling |
| `cli/python/cf_tracker/pyproject.toml` | CLI tracker tooling & deps |
| `projects/unified_logger/Notebooks/pyproject.toml` | Notebook env packaging |

## PowerShell Pester Tests (Representative Selection)
```
tests/AuthorityMap.Tests.ps1
tests/AuthorityFreshness.Tests.ps1
tests/ChainSummary.Integrity.Tests.ps1
tests/Governance.Smoke.Tests.ps1
tests/Governance.EvidenceManifest.Tests.ps1
tests/MCP.Integration.Tests.ps1
tests/MCP.Configuration.Tests.ps1
tests/memory_mcp.Tests.ps1
tests/governance/AcceleratorMetrics.Tests.ps1
tests/governance/AcceleratorBursts.Tests.ps1
... (total 173)
```
Focus areas: Governance, MCP integration, SCCM, HostPolicy enforcement, evidence manifest validation.

## Python Test Generators
Scripts generating or scaffolding large test matrices:
- `create_all_qse_tests.py`
- `create_remaining_qse_tests.py`
- `create_test_files.py`
These contain extensive `@pytest.mark.asyncio` usage and likely produce synthetic or parameterized test cases for QSE coverage amplification.

## Pytest Marker Taxonomy (Observed Subset)
| Marker | Domain / Intent |
|--------|-----------------|
| asyncio | Async event loop tests |
| unit | Unit-level isolation |
| integration | Cross-component behavior |
| triangle | Sacred Geometry stability dimension |
| circle | Completeness validation pattern |
| spiral | Iterative progression validation |
| fractal | Modular consistency across scales |
| pentagon | (Extended geometry / harmony) |
| performance | Performance / benchmarking |
| dtm | Digital Transformation Module workflows |
| critical | High-risk / gating tests |
| rich_terminal | Terminal rendering / ANSI diagnostics |
| gamification | Gamification subsystem workflows |
| migration | Migration path or compatibility checks |
| constitutional | UCL / COF compliance enforcement |
| contextforge | Brand/system-wide integration |
| production | Production readiness / hardening |
| load | Load / stress patterns |
| failover | Failover / resilience validation |
| mpv | (Likely "minimum product viability" parity) |
| mcp | Model Context Protocol integration |

Additional parametrize usages indicate high test matrix density for reliability & edge coverage (e.g., timeouts, concurrent commands, error scenarios).

## Notable Integration Suites
- `tests/integration/test_dtm_integration.py` – Critical + dtm markers, repeated multi-phase coverage.
- `tests/integration/test_gamification_workflow.py` – Large scenario coverage; multiple integration + gamification + performance + constitutional segments.
- `tests/integration/test_contextforge_comprehensive_integration.py` – Broad platform synthesis (contextforge + pentagon + asyncio sections).
- `tests/integration/test_layer1_infrastructure.py` – Docker conditional skips (SKIP_DOCKER_TESTS guard).
- `tests/integration/test_layer5_production_readiness.py` – Production, load, failover gating (late-phase readiness).
- `tests/integration/test_mcp_integration.py` – MCP server capability and health verification across multiple servers.

## Performance & Concurrency Focus
Performance-oriented tests in `tests/tasksync/performance/` exercising concurrent sessions, monitoring throughput, memory usage—heavy `@pytest.mark.asyncio` distribution suggests async event loop stress harness.

## Reliability Expansion Opportunities (Initial Observations)
1. Marker Consolidation: Large marker surface suggests opportunity to rationalize taxonomy (reduce cognitive overhead & accelerate selection logic).
2. Async Saturation: High prevalence of `@pytest.mark.asyncio` – ensure loop fixture standardization, evaluate flakiness risk & timeouts.
3. Parametrization Density: Many parameterized blocks (timeouts, error scenarios, concurrency) – potential for combining related cases into scenario tables to reduce redundant setup overhead.
4. Cross-Layer Alignment: Layered tests (layer1..layer5) – verify consistent environment provisioning (Docker skip conditions vs production readiness gating).
5. Sacred Geometry Coverage Mapping: Geometry markers (triangle, circle, spiral, fractal, pentagon) – create coverage matrix to ensure each geometry dimension is paired with reliability + performance assertions.
6. MCP Integration Gating: Ensure MCP server health preflight fixture reused across all MCP tests to avoid duplicated connection logic.
7. Production Readiness: Load/failover tests – confirm evidence bundles include resource utilization snapshots (memory, CPU) for traceable optimization cycles.
8. Test Data Governance: Large JSON fixtures – evaluate central fixture factory vs raw file proliferation for maintainability.
9. Skipped Tests Audit: Skip markers referencing future implementation (e.g., cf_cli functional) – create tracking list to convert into actionable backlog.
10. Redundancy Detection: Potential overlap between `test_layer3_performance_framework.py` and `performance_gate_stability_integration.py` – consider unification under a single performance orchestration suite.

## Next Action Recommendations
| Priority | Action | Outcome |
|----------|--------|---------|
| P0 | Build consolidated marker registry & deprecate unused tags | Reduced complexity & faster suite targeting |
| P0 | Add unified MCP health fixture | Lower flake rate, faster fail-fast |
| P1 | Generate Sacred Geometry coverage matrix artifact | Visibility into geometry-driven reliability scope |
| P1 | Create async event loop stability test harness (timeout regression watch) | Reduced intermittent failures |
| P2 | Parameter set normalization (grouping similar timeouts/concurrency cases) | Shorter runtime, clearer analytics |
| P2 | Evidence bundle enrichments for performance/failover tests | Stronger optimization feedback loops |
| P3 | Skip audit backlog file (auto-generated) | Roadmap clarity for enabling skipped scenarios |

## Proposed Artifacts to Add
- `tests/_registry/marker_registry.yaml` – canonical marker definitions & ownership
- `tests/_coverage/sacred_geometry_matrix.md` – mapping of geometry marker → test file → reliability dimension
- `tests/conftest.py` enhancement – shared MCP server health check fixture + async loop safeguards
- `tests/_backlog/skipped_tests_catalog.json` – machine-generated from decorators

## Validation Hooks (Future)
Implement pre-run hook:
- Scan for orphaned geometry markers without corresponding reliability assertions.
- Auto-fail if MCP integration tests run without server health evidence event emitted.

---
Generated automatically. Extend or refine with deeper static analysis & runtime metrics collection in subsequent phases.
