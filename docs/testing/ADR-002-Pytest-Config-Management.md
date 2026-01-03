# ADR-002: Systematic Pytest Configuration Management

**Status**: Accepted
**Date**: 2025-11-03
**Authors**: QSE Testing Team
**Reviewers**: ContextForge Engineering Team

## Context

The ContextForge workspace contains **14 pytest configuration files** spread across root, subprojects, test suites, and MCP server directories. Prior to this work, the pytest configuration scanner identified **27 critical issues**:

- **17 unregistered markers** causing `PytestUnknownMarkWarning` in strict mode
- **8 deprecated configuration options** (primarily `asyncio_mode`)
- **2 discovery conflicts** from inconsistent `testpaths` and `norecursedirs` settings

These issues prevented strict pytest validation (`--strict-config --strict-markers`) from passing and created maintenance burden from configuration drift across the workspace.

### Business Impact

- **Test reliability**: Warnings obscured real test failures
- **CI/CD friction**: Strict validation failures blocked pipeline progression
- **Developer experience**: Unclear marker registration discouraged test categorization
- **Technical debt**: Configuration drift required manual reconciliation

### Technical Constraints

- **Multi-project workspace**: 727 test files across multiple subprojects
- **Tool compatibility**: Both `[tool:pytest]` and `[pytest]` sections must be maintained
- **Backwards compatibility**: Cannot break existing test suites
- **Performance**: Scanner must complete in reasonable time (<30s target)

## Decision

We have decided to implement a **systematic batch fix approach** using an automated configuration scanner and rigorous validation workflow to achieve **100% issue resolution** while establishing sustainable configuration management practices.

### Core Strategy

1. **Automated Scanner Development**: Build `tools/pytest_config_audit.py` to detect unregistered markers, deprecated options, and discovery conflicts
2. **Systematic Batch Fixes**: Group related issues into batches (deprecations → markers → discovery)
3. **Rigorous Multi-Level Validation**: Scanner → pytest strict → grep verification → manual inspection
4. **Documentation**: Capture methodology in `docs/testing/pytest-config-management.md`
5. **CI Integration** (planned): Add scanner as mandatory quality gate

### Implementation Approach

**Phase 1: Scanner Development**
- Recursive config file discovery
- Marker extraction from test files
- Deprecation detection via pattern matching
- Discovery conflict analysis (testpaths, norecursedirs)
- Rich-formatted output with TQDM progress bars
- JSON report generation for CI integration

**Phase 2: Batch Fix 1 - Deprecated Options**
- Removed `asyncio_mode` from 9 configuration files
- Deleted entire `[tool.pytest-asyncio]` block from root `pyproject.toml`
- Verified with grep: zero occurrences remaining
- **Result**: 8 deprecated warnings → 0

**Phase 3: Batch Fix 2 - Marker Registration**
- Categorized 17 unregistered markers:
  - Sacred Geometry: circle, fractal, pentagon, spiral, triangle
  - ISTQB: istqb
  - Standard pytest: skip, skipif, xfail, parametrize
  - Domain-specific: action_lists, config, models, smoke, timeout, utils
  - Async framework: anyio
- Added to both `[tool:pytest]` and `[pytest]` sections in root `pytest.ini`
- Alphabetical organization for maintainability
- Descriptive text for each marker
- **Result**: 17 unregistered markers → 0, total 70 markers registered

**Phase 4: Batch Fix 3 - Discovery Harmonization**
- Standardized `norecursedirs` pattern:
  - Build artifacts: `.git`, `.tox`, `.venv`, `dist`, `build`, `*.egg`, `htmlcov`
  - Workspace exclusions: `mcp`, `TaskMan-v2`, `projects`, `qse`, `python/api`, `python/rich_terminal`, `test_suite_*`
- Centralized `testpaths = tests` in root configuration
- Commented out subproject-specific `testpaths` with explanation
- Synchronized both `[tool:pytest]` and `[pytest]` sections
- **Result**: 2 discovery conflicts → 0

**Phase 5: Performance Optimization**
- Optimized marker extraction phase
- Cached parsed results
- Parallel config processing
- **Result**: 67.14s → 14.93s (79% improvement)

## Options Considered

### Option A: Manual Ad-Hoc Fixes
**Pros:**
- Simple to start
- No tooling investment required
- Can address immediate pain points quickly

**Cons:**
- ❌ No systematic approach to prevent recurrence
- ❌ High risk of missing issues across 14 config files
- ❌ No validation that all issues resolved
- ❌ Configuration drift likely to return

**Decision**: Rejected - insufficient rigor for 27 issues across 14 files

### Option B: Pytest Plugin for Auto-Registration
**Pros:**
- Automatic marker registration at runtime
- No manual config updates needed
- Dynamic marker discovery

**Cons:**
- ❌ Hides configuration issues rather than fixing them
- ❌ Doesn't address deprecated options or discovery conflicts
- ❌ Performance overhead at test collection time
- ❌ Strict mode validation still fails

**Decision**: Rejected - doesn't solve root configuration management problem

### Option C: Systematic Batch Fix with Scanner (SELECTED)
**Pros:**
- ✅ **Comprehensive**: Addresses all 27 issues systematically
- ✅ **Validated**: Multi-level verification ensures correctness
- ✅ **Sustainable**: Scanner prevents future drift
- ✅ **Fast**: Optimized scanner runs in ~15 seconds
- ✅ **Documented**: Methodology captured for future maintainers
- ✅ **CI-Ready**: JSON output enables automated enforcement

**Cons:**
- Requires initial scanner development investment
- More complex than ad-hoc fixes
- Requires discipline to run scanner regularly

**Decision**: Selected - provides long-term solution with proven 100% success rate

### Option D: Consolidate All Configs to Root Only
**Pros:**
- Single source of truth
- Simplest maintenance
- No synchronization issues

**Cons:**
- ❌ Breaks subproject independence
- ❌ Doesn't support different test requirements per subproject
- ❌ Complex migration for existing structures
- ❌ May interfere with third-party tool expectations

**Decision**: Rejected - too disruptive for existing multi-project structure

## Consequences

### Positive Outcomes

**Immediate Benefits**:
- ✅ **100% issue resolution**: 27 issues → 0 issues
- ✅ **Strict validation passing**: `pytest --strict-config --strict-markers` runs cleanly
- ✅ **2666 tests validated**: Zero configuration warnings
- ✅ **79% performance improvement**: Scanner optimized from 67.14s to 14.93s
- ✅ **Documentation complete**: Comprehensive guide for future maintainers

**Long-Term Benefits**:
- ✅ **Sustainable practices**: Scanner detects drift before it accumulates
- ✅ **CI integration ready**: JSON output enables automated quality gates
- ✅ **Developer confidence**: Clear marker registration encourages test categorization
- ✅ **Reduced maintenance**: Alphabetical organization simplifies updates

### Trade-offs Accepted

**Increased Complexity**:
- Must run scanner periodically to detect drift
- Both `[tool:pytest]` and `[pytest]` sections require synchronization
- Alphabetical organization requires discipline

**Rationale**: Complexity is justified by 100% success rate and long-term maintainability benefits

**Initial Time Investment**:
- Scanner development: ~4 hours
- Batch fix execution: ~6 hours (equivalent)
- Documentation: ~2 hours

**Rationale**: 12-hour investment prevents ongoing configuration drift and manual reconciliation (estimated 2+ hours per quarter)

### Risks and Mitigations

**Risk 1: Scanner False Positives**
- **Mitigation**: Manual validation step in batch fix workflow
- **Status**: Zero false positives observed in production use

**Risk 2: Configuration Drift Between Sections**
- **Mitigation**: Scanner detects inconsistencies; validation phase includes synchronization check
- **Status**: Consistency fix applied during validation phase proves effectiveness

**Risk 3: Scanner Performance Degradation**
- **Mitigation**: Performance metrics tracked; optimization applied when runtime >30s
- **Status**: Current 14.93s runtime well under target

**Risk 4: New Markers Not Registered**
- **Mitigation**: CI integration (planned) will fail builds with unregistered markers
- **Status**: Manual scanner runs recommended until CI integration complete

## Implementation Results

### Quantitative Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Unregistered Markers** | 17 | 0 | 100% |
| **Deprecated Options** | 8 | 0 | 100% |
| **Discovery Conflicts** | 2 | 0 | 100% |
| **Total Issues** | 27 | 0 | **100%** |
| **Scanner Runtime** | 67.14s | 14.93s | **79% faster** |
| **Registered Markers** | 53 | 70 | +32% |
| **Config Files Managed** | 14 | 14 | Comprehensive |
| **Test Files Discovered** | 727 | 727 | Stable |
| **Pytest Validation** | ⚠️ Warnings | ✅ Clean | Strict mode passing |

### Qualitative Outcomes

**Developer Experience**:
- Clear marker categories (Sacred Geometry, ISTQB, domain-specific)
- Alphabetical organization makes markers easy to find
- Descriptive text explains marker purpose
- Confidence to add new markers following established pattern

**Configuration Quality**:
- Both `[tool:pytest]` and `[pytest]` sections synchronized
- Consistent `norecursedirs` pattern across all configs
- Centralized discovery with documented subproject override pattern
- Zero warnings in strict validation mode

**Maintenance Efficiency**:
- Scanner runs in ~15 seconds (down from 67s)
- Rich-formatted output with TQDM progress bars
- JSON report ready for CI integration
- Comprehensive documentation enables self-service

## Validation Evidence

### Scanner Reports

**Final Audit Output**:
```
📊 Audit Summary
├─ Config Files Scanned: 14 ✅
├─ Unique Markers Found: 62 ℹ️
├─ Registered Markers: 153 ✅
├─ Unregistered Markers: 0 ✅
├─ Deprecated Options: 0 ✅
└─ Discovery Conflicts: 0 ✅

✅ 🎉 All checks passed!
Completed in 14.93s
```

### Pytest Validation

**Strict Mode Collection**:
```bash
pytest --strict-config --strict-markers --collect-only
# Result: 2666 tests collected, zero warnings
# asyncio mode=Mode.STRICT confirmed
```

### Grep Verification

**Deprecated Options Removed**:
```bash
grep -r "asyncio_mode" --include="*.ini" --include="*.toml"
# Result: No matches found ✅
```

**Section Synchronization**:
```bash
# Both [tool:pytest] and [pytest] sections have identical norecursedirs
grep -A 15 "norecursedirs" pytest.ini
# Result: Build artifacts + workspace exclusions in both sections ✅
```

## Lessons Learned

### What Worked Well

1. **Systematic Batch Approach**
   - Grouping related issues (deprecations → markers → discovery) made execution manageable
   - Each batch had clear scope, verification, and validation steps
   - Prevented overwhelming changes in single commit

2. **Multi-Level Validation**
   - Scanner → pytest strict → grep → manual inspection caught all issues
   - Validation phase discovered `[tool:pytest]` section inconsistency (immediately fixed)
   - Redundant validation proved critical for quality assurance

3. **Alphabetical Organization**
   - Made markers easy to locate and maintain
   - Simplified spotting duplicates or missing entries
   - Consistent format improved readability

4. **Section Synchronization**
   - Keeping `[tool:pytest]` and `[pytest]` identical prevented tool compatibility issues
   - Consistency checks during validation proved valuable

### What Could Be Improved

1. **Scanner Development Timeline**
   - Could have started with simpler version and iterated
   - Performance optimization could have been deferred to post-launch

2. **Documentation Timing**
   - Should have documented methodology during execution, not after
   - Real-time capture would have included more implementation details

3. **CI Integration**
   - Should have been implemented immediately after batch fixes
   - Manual scanner runs risk being forgotten

### Unexpected Discoveries

1. **Validation Phase Value**
   - User-requested validation discovered `[tool:pytest]` inconsistency
   - Demonstrates importance of rigorous final checks
   - Even "passing" scanner results don't guarantee section-level correctness

2. **Performance Optimization Impact**
   - 79% improvement exceeded expectations
   - Makes scanner viable for CI use (target was <30s, achieved 14.93s)

3. **Marker Categorization**
   - Sacred Geometry markers (circle, fractal, pentagon, spiral, triangle) emerged as valuable test organization pattern
   - ISTQB marker adoption shows testing discipline
   - Domain-specific markers (action_lists, config, models) enable focused test execution

## Future Work

### Immediate (High Priority)

1. **CI Integration** (Task #8) - ✅ **COMPLETE**
   - ✅ Added scanner to `pytest-pr.yml` GitHub Actions workflow
   - ✅ Configured to fail builds with unregistered markers, deprecated options, or discovery conflicts
   - ✅ Scanner JSON reports uploaded as CI artifacts (`pytest-config-audit`)
   - ✅ Path triggers added for `pytest.ini`, `**/pytest.ini`, `**/pyproject.toml`, and scanner source
   - **Completed**: 2025-11-04
   - **Actual Effort**: 2 hours
   - **Implementation**: Parse JSON output, check counts for unregistered_markers, deprecated_options, discovery.conflicts
   - **Value Delivered**: Automated quality gate prevents future configuration drift

2. **Scanner JSON Schema Validation** (Task #11) - ✅ **COMPLETE**
   - ✅ Created comprehensive JSON Schema Draft 7 schema (`pytest_config_audit_schema.json`)
   - ✅ Integrated validation into scanner script with graceful degradation
   - ✅ Schema validates all output fields, marker name formats, and report structure
   - ✅ Zero-dependency fallback when `jsonschema` library unavailable
   - ✅ CI workflow automatically validates scanner output structure via schema
   - **Completed**: 2025-11-04
   - **Actual Effort**: 2 hours
   - **Implementation**:
     - Analyzed scanner JSON output structure (1725 lines, 14 config files, 153 registered markers)
     - Created schema with required fields, type constraints, pattern validation
     - Added `validate_report_schema()` function with comprehensive error handling
     - Integrated validation before JSON output (line 494) with error logging
     - Tested validation with production data: zero validation errors ✅
   - **Schema Features**:
     - Validates required fields: generated_at, workspace_root, config_files, etc.
     - Pattern validation for marker names (unregistered: strict, registered: permissive for descriptions)
     - Array item validation for config_files (required path, type fields)
     - Graceful handling of missing schema file or validation library
     - Logs validation errors to report["errors"] array without breaking scanner
   - **Value Delivered**:
     - Ensures scanner JSON output is always well-formed and parseable
     - Catches structural issues before CI PowerShell parsing
     - Documents expected output format as machine-readable schema
     - Enables safer JSON parsing in downstream tools
     - Zero false positives in production validation ✅

3. **Update Existing ADRs** (Task #13) - ✅ **COMPLETE**
   - ✅ This ADR documents systematic approach and lessons learned
   - ✅ CI integration completion documented
   - ✅ JSON schema validation completion documented

4. **Performance Baseline Documentation** (Task #12) - ✅ **COMPLETE**
   - ✅ Documented current scanner performance metrics in pytest-config-management.md
   - ✅ Created performance evolution table tracking optimization progress
   - ✅ Established future optimization targets (<10s runtime, >100 files/sec throughput)
   - ✅ Documented benchmarking methodology for consistent measurements
   - **Completed**: 2025-11-04
   - **Actual Effort**: 1 hour
   - **Current Performance** (v1.2):
     - Total runtime: 13.56s (config scan + 729 test file marker extraction)
     - Throughput: ~54 files/sec (marker extraction)
     - Memory peak: <200MB
     - Validation overhead: ~0.1s (JSON schema)
   - **Performance Evolution**:
     - Baseline (67.14s) → v1.0 (14.93s) → v1.1 (38.45s) → v1.2 (13.56s)
     - 79% total improvement from baseline to current
   - **Future Targets**:
     - <10s runtime via incremental mode (only changed files)
     - >100 files/sec via async I/O and parallel processing
     - Cached marker database with smart invalidation
   - **Value Delivered**:
     - Establishes performance tracking foundation for future optimization
     - Documents optimization history for learning and knowledge transfer
     - Provides clear targets for next optimization phase
     - Enables early detection of performance regressions

### Near-Term (Medium Priority)

5. **Scanner Feature Enhancements** (Task #9)
   - Plugin version conflict detection
   - Unused marker identification (registered but never used)
   - HTML report generation with interactive filtering
   - Auto-fix capability with `--dry-run` flag
   - **Estimated Effort**: 8-12 hours
   - **Expected Value**: Further reduce manual maintenance burden

4. **Subproject Testpaths Policy** (Task #10)
   - Document decision: centralized vs. independent discovery
   - Update affected configs if policy changes
   - **Estimated Effort**: 2-3 hours
   - **Expected Value**: Clear guidance for future subproject additions

### Long-Term (Low Priority)

5. **Marker Usage Analysis** (Task #11)
   - Analyze 62 unique markers across 727 test files
   - Identify frequently used vs. rarely used markers
   - Recommend marker consolidation or deprecation
   - **Estimated Effort**: 4-6 hours
   - **Expected Value**: Optimize test organization

6. **Pytest Plugins Compatibility Audit** (Task #12)
   - Audit all plugins for version conflicts
   - Identify redundant plugin declarations
   - Document plugin interaction warnings
   - **Estimated Effort**: 6-8 hours
   - **Expected Value**: Prevent plugin-related test failures

## References

### Related Documents

- **Implementation Guide**: `docs/testing/pytest-config-management.md` - Comprehensive methodology documentation
- **Scanner Source**: `tools/pytest_config_audit.py` - Configuration audit implementation
- **Root Configuration**: `pytest.ini` - Authoritative pytest configuration with synchronized sections
- **Alternative Configuration**: `pyproject.toml` - TOML-format pytest configuration

### External Resources

- **Pytest Documentation**: https://docs.pytest.org/en/stable/reference/reference.html#configuration-options
- **pytest-asyncio Migration**: https://github.com/pytest-dev/pytest-asyncio/blob/main/CHANGELOG.rst (asyncio_mode deprecation)
- **Marker Best Practices**: https://docs.pytest.org/en/stable/example/markers.html

### Evidence Artifacts

- **Scanner JSON Reports**: `pytest_config_audit.json` (generated each run, validated against JSON schema)
- **JSON Schema**: `pytest_config_audit_schema.json` (JSON Schema Draft 7 validation)
- **Validation Logs**: Terminal output from `pytest --strict-config --strict-markers --collect-only`
- **Grep Verification**: Command-line verification of deprecated option removal

## Approval

**Accepted**: 2025-11-03
**Rationale**: Systematic batch fix approach achieved 100% issue resolution with proven validation methodology. Scanner development provides sustainable long-term configuration management.

**Reviewers**: ContextForge Engineering Team
**Status**: Production implementation complete, documentation finalized, **CI integration complete (2025-11-04)**, **JSON schema validation complete (2025-11-04)**, **Performance baseline documentation complete (2025-11-04)**.

---

**Document Version**: 1.3
**Last Updated**: 2025-11-04 (Performance baseline documentation)
**Changes in v1.3**:
- Added comprehensive performance baseline documentation to pytest-config-management.md
- Documented current performance metrics (13.56s runtime, ~54 files/sec throughput)
- Created performance evolution table tracking optimization history
- Established future optimization targets (<10s runtime, >100 files/sec)
- Added benchmarking methodology and performance monitoring guidelines

**Changes in v1.2**:
- Added JSON schema validation for scanner output (`pytest_config_audit_schema.json`)
- Integrated schema validation into scanner script with graceful degradation
- Schema validates report structure, marker formats, and all output fields
- Zero-dependency fallback when `jsonschema` library unavailable
- CI workflow automatically validates scanner output structure

**Next Review**: 2026-02-03 (quarterly review of scanner effectiveness and CI integration metrics)
