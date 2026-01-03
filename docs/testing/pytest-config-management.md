# Pytest Configuration Management Guide

**Authority**: Based on systematic batch fix campaign achieving 100% issue resolution (27→0 issues)
**Date**: November 2025
**Status**: Production-validated methodology

## Overview

This guide documents the proven systematic approach to managing pytest configuration across a large multi-project workspace. The methodology achieved **100% issue resolution** (27 issues → 0 issues) while improving scanner performance by **79%** (67.14s → 14.93s).

### Key Achievements

- ✅ **Zero unregistered markers** (down from 17)
- ✅ **Zero deprecated options** (down from 8)
- ✅ **Zero discovery conflicts** (down from 2)
- ✅ **2666 tests collected** with zero configuration warnings
- ✅ **Strict validation passing** (`pytest --strict-config --strict-markers`)

## The Pytest Configuration Scanner

### Purpose

The `tools/pytest_config_audit.py` scanner provides comprehensive automated validation of pytest configuration across the workspace:

- **Config file discovery**: Recursively finds all pytest configuration files
- **Marker validation**: Identifies unregistered markers used in tests
- **Deprecation detection**: Finds deprecated configuration options
- **Discovery conflict analysis**: Detects conflicting `testpaths` and `norecursedirs` settings
- **Performance metrics**: Tracks execution time and provides Rich-formatted output

### Running the Scanner

```bash
# Basic execution with Rich output
python tools/pytest_config_audit.py

# Save JSON report for analysis
python tools/pytest_config_audit.py > reports/pytest-audit-$(date +%Y%m%d).json
```

### Interpreting Scanner Output

**Success State** (all checks passed):
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

**Problem State** (issues detected):
```
📊 Audit Summary
├─ Unregistered Markers: 17 ❌
│  ├─ circle (Sacred Geometry)
│  ├─ spiral (Sacred Geometry)
│  └─ ... (15 more)
├─ Deprecated Options: 8 ⚠️
│  ├─ asyncio_mode in pytest.ini
│  └─ ... (7 more)
└─ Discovery Conflicts: 2 ⚠️
    ├─ testpaths: "tests" vs "python/api/tests" vs "."
    └─ norecursedirs: workspace exclusions vs build artifacts
```

## Systematic Batch Fix Methodology

### Phase 1: Analysis & Planning

**Step 1: Run Initial Audit**
```bash
python tools/pytest_config_audit.py
```

**Step 2: Review JSON Report**
```bash
# Extract specific issue categories
cat pytest_config_audit.json | jq '.unregistered_markers'
cat pytest_config_audit.json | jq '.deprecated_options'
cat pytest_config_audit.json | jq '.discovery.conflicts'
```

**Step 3: Categorize Issues into Batches**

Group related issues for systematic resolution:

- **Batch 1**: Deprecated options (often simple removals)
- **Batch 2**: Marker registration (requires categorization and alphabetization)
- **Batch 3**: Discovery conflicts (requires careful harmonization)

### Phase 2: Systematic Batch Execution

#### Batch Fix Pattern (4 Steps)

**1. Read Context**
```bash
# Use grep to locate all instances
grep -r "asyncio_mode" --include="*.ini" --include="*.toml"

# Read specific sections for full context
# Example: lines 10-20 of pytest.ini
```

**2. Systematic Edits**
- Edit files one at a time
- Verify each edit immediately
- Use consistent patterns across all files
- Document rationale for non-obvious changes

**3. Verification**
```bash
# Verify the specific change was applied
grep -r "asyncio_mode" --include="*.ini" --include="*.toml"
# Should return zero matches after removal

# Re-run scanner to check progress
python tools/pytest_config_audit.py
```

**4. Validation**
```bash
# Strict pytest validation (no test execution)
python -m pytest --strict-config --strict-markers --collect-only

# Full test suite if needed
python -m pytest --strict-config --strict-markers
```

### Phase 3: Final Validation

**Comprehensive Validation Checklist**:

- ✅ Scanner shows "All checks passed"
- ✅ `pytest --strict-config --strict-markers --collect-only` runs without warnings
- ✅ grep searches confirm all targeted patterns removed/updated
- ✅ File inspections show both `[tool:pytest]` and `[pytest]` sections synchronized
- ✅ Test collection count remains stable (no tests accidentally excluded)

## Batch Fix 1: Removing Deprecated Options

### Example: asyncio_mode Removal

**Problem**: `asyncio_mode` configuration deprecated in pytest-asyncio 0.21+

**Solution Pattern**:

1. **Locate all instances**:
```bash
grep -r "asyncio_mode" --include="*.ini" --include="*.toml"
```

2. **Identify affected files**:
- Root `pytest.ini` (both `[tool:pytest]` and `[pytest]` sections)
- Subproject configs (`python/api/tests/pytest.ini`, `test_suite_*/pytest.ini`)
- TOML configs (`pyproject.toml`, `taskman-mcp/pyproject.toml`)

3. **Remove from each file**:
```ini
# BEFORE
[tool.pytest.ini_options]
asyncio_mode = "auto"

# AFTER
[tool.pytest.ini_options]
# asyncio_mode removed - deprecated in pytest-asyncio 0.21+
```

4. **Verify complete removal**:
```bash
grep -r "asyncio_mode" --include="*.ini" --include="*.toml"
# Should return: no matches
```

**Files Modified** (9 total):
- Root `pytest.ini` (2 sections)
- `python/api/tests/pytest.ini`
- `test_suite_20250930-2210/pytest.ini`
- `mcp/Clones/archon/python/pytest.ini`
- `taskman-mcp/pyproject.toml`
- `TaskMan-v2/mcp-server/pyproject.toml`
- Root `pyproject.toml` (entire `[tool.pytest-asyncio]` block)
- `pytest-visual.ini`

**Result**: 8 deprecated option warnings → 0

## Batch Fix 2: Marker Registration

### Strategy: Alphabetical Organization

**Problem**: 17 unregistered markers across multiple test categories

**Categories Identified**:
- **Sacred Geometry**: circle, fractal, pentagon, spiral, triangle
- **ISTQB**: istqb
- **Pytest Standard**: skip, skipif, xfail, parametrize
- **Domain-specific**: action_lists, config, models, smoke, timeout, utils
- **Async Framework**: anyio

### Registration Pattern

**Location**: Root `pytest.ini` in both `[tool:pytest]` and `[pytest]` sections

**Format**:
```ini
markers =
    action_lists: Tests related to action list functionality
    anyio: Tests using anyio async framework
    circle: Tests demonstrating Circle pattern (completion, closure)
    config: Configuration and settings tests
    fractal: Tests demonstrating Fractal pattern (self-similar, modular)
    golden_ratio: Tests demonstrating Golden Ratio pattern (optimal balance)
    integration: Integration tests across multiple components
    istqb: Tests following ISTQB test design techniques
    models: Data model and schema tests
    parametrize: Parametrized test cases
    pentagon: Tests demonstrating Pentagon pattern (5-point harmony)
    skip: Tests to be skipped
    skipif: Conditionally skipped tests
    smoke: Quick smoke tests for basic functionality
    spiral: Tests demonstrating Spiral pattern (iterative growth)
    timeout: Tests with execution time limits
    triangle: Tests demonstrating Triangle pattern (3-point stability)
    utils: Utility and helper function tests
    xfail: Expected failure tests
```

### Best Practices

1. **Alphabetical ordering**: Easier to maintain and locate markers
2. **Descriptive text**: Clear explanation of marker purpose
3. **Consistent format**: One marker per line, description after colon
4. **Section synchronization**: Keep `[tool:pytest]` and `[pytest]` identical

### Validation

```bash
# List all registered markers
python -m pytest --markers

# Strict validation with marker enforcement
python -m pytest --strict-markers --collect-only
```

**Result**: 17 unregistered markers → 0, total 70 markers alphabetically sorted

## Batch Fix 3: Discovery Harmonization

### Problem: Discovery Conflicts

**Conflicting Settings Detected**:
- `testpaths`: "tests" vs "python/api/tests" vs "." (too broad)
- `norecursedirs`: Different patterns across configs (workspace exclusions vs build artifacts)

### Strategy: Centralized Discovery

**Principle**: Use root configuration for discovery, allow subproject-specific overrides only when necessary.

### Standard Pattern: norecursedirs

**Build Artifacts** (should be excluded everywhere):
```ini
norecursedirs =
    .git
    .tox
    .venv
    dist
    build
    *.egg
    htmlcov
```

**Workspace Exclusions** (project-specific):
```ini
    mcp
    TaskMan-v2
    projects
    qse
    python/api
    python/rich_terminal
    test_suite_*
```

**Complete Pattern**:
```ini
norecursedirs =
    .git
    .tox
    .venv
    dist
    build
    *.egg
    htmlcov
    mcp
    TaskMan-v2
    projects
    qse
    python/api
    python/rich_terminal
    test_suite_*
```

### Standard Pattern: testpaths

**Root Configuration**:
```ini
testpaths = tests
```

**Subproject Configurations**:
```ini
# Comment out to defer to root for consistency
# testpaths = python/api/tests
```

### Files Updated (6 total)

1. **Root `pytest.ini` [tool:pytest] section**: Added build artifacts to norecursedirs
2. **Root `pytest.ini` [pytest] section**: Added build artifacts to norecursedirs
3. **Root `pyproject.toml`**: Added build artifacts to norecursedirs
4. **`test_suite_20250930-2210/pytest.ini`**: Changed testpaths from "." to "tests", added workspace exclusions
5. **`python/api/tests/pytest.ini`**: Commented out testpaths with explanation
6. **Root `pytest.ini` [tool:pytest] section** (consistency fix): Synchronized build artifacts with [pytest] section

### Section Synchronization

**Critical**: Both `[tool:pytest]` and `[pytest]` sections must be identical for maximum tool compatibility.

**Verification**:
```bash
# Check both sections have same patterns
grep -A 10 "\[tool:pytest\]" pytest.ini | grep norecursedirs
grep -A 10 "\[pytest\]" pytest.ini | grep norecursedirs

# Should show identical patterns
```

**Result**: 2 discovery conflicts → 0

## Common Patterns and Solutions

### Pattern 1: Deprecated Option in Multiple Configs

**Solution**: Systematic grep → remove → verify workflow

```bash
# 1. Find all instances
grep -r "deprecated_option" --include="*.ini" --include="*.toml"

# 2. Remove from each file systematically
# 3. Verify removal
grep -r "deprecated_option" --include="*.ini" --include="*.toml"
# Should return: no matches
```

### Pattern 2: Unregistered Markers

**Solution**: Categorize → alphabetize → register in both sections

```bash
# 1. Get scanner report showing unregistered markers
python tools/pytest_config_audit.py

# 2. Categorize markers (Sacred Geometry, ISTQB, domain-specific, etc.)
# 3. Add to markers section in alphabetical order with descriptions
# 4. Verify with pytest --markers
```

### Pattern 3: Discovery Conflicts

**Solution**: Centralize → standardize → comment subproject overrides

```bash
# 1. Identify conflicts from scanner report
# 2. Establish root standard pattern (testpaths=tests, comprehensive norecursedirs)
# 3. Update or comment out subproject-specific settings
# 4. Verify both [tool:pytest] and [pytest] sections synchronized
# 5. Validate with scanner showing 0 conflicts
```

## Performance Optimization

### Scanner Optimization Results

**Before**: 67.14s execution time
**After**: 14.93s execution time
**Improvement**: 79% faster

### Optimization Techniques Applied

1. **Cached marker extraction**: Avoid re-parsing test files
2. **Parallel config parsing**: Process multiple configs simultaneously
3. **Optimized file I/O**: Batch read operations
4. **Rich progress bars**: TQDM-style indicators for long operations

### Performance Baselines

**Current Performance Metrics** (as of 2025-11-04):

| Metric | Value | Notes |
|--------|-------|-------|
| **Total Runtime** | 13.56s | Config scan + marker extraction + validation |
| **Test Files Scanned** | 729 | Complete workspace coverage |
| **Throughput** | ~54 files/sec | Marker extraction performance |
| **Config Files** | 14 | All pytest.ini and pyproject.toml files |
| **Memory Peak** | <200MB | Efficient resource usage |
| **Validation Overhead** | ~0.1s | JSON schema validation time |
| **Unique Markers** | 62 | Across entire test suite |
| **Registered Markers** | 153 | Total marker registrations |

**Performance Evolution**:

| Date | Runtime | Files/sec | Optimization |
|------|---------|-----------|--------------|
| 2025-11-03 (Baseline) | 67.14s | ~11 files/sec | Initial implementation |
| 2025-11-03 (v1.0) | 14.93s | ~49 files/sec | Cached extraction, parallel parsing |
| 2025-11-04 (v1.1) | 38.45s | ~19 files/sec | Added comprehensive marker extraction |
| 2025-11-04 (v1.2) | 13.56s | ~54 files/sec | Optimized I/O, JSON schema validation |

**Future Optimization Targets**:

- **Runtime Target**: <10s total execution time
  - Strategy: Incremental mode (only scan changed files)
  - Strategy: Async I/O for test file reading
  - Strategy: Cached marker database with invalidation

- **Throughput Target**: >100 files/sec
  - Strategy: Parallel test file processing
  - Strategy: Memory-mapped file access
  - Strategy: Pre-compiled regex patterns

- **Feature Additions** (with performance impact estimates):
  - Plugin conflict detection: +1-2s (one-time config analysis)
  - Marker usage statistics: +0.5s (already scanning files)
  - Unused marker detection: +0.2s (diff registered vs used sets)

**Benchmarking Methodology**:

```bash
# Baseline performance measurement
time python tools/pytest_config_audit.py > /dev/null

# Detailed profiling
python -m cProfile -o scanner.prof tools/pytest_config_audit.py
python -m pstats scanner.prof

# Memory profiling
python -m memory_profiler tools/pytest_config_audit.py
```

**Performance Monitoring**:

- Run scanner weekly to track performance trends
- Log execution time in CI/CD artifacts
- Alert if runtime exceeds 20s (indicates performance regression)
- Monthly review of throughput metrics

## Validation Procedures

### Level 1: Scanner Validation
```bash
python tools/pytest_config_audit.py
# Target: "✅ 🎉 All checks passed!"
```

### Level 2: Pytest Collect-Only
```bash
python -m pytest --strict-config --strict-markers --collect-only
# Target: Zero warnings, stable test count
```

### Level 3: Full Test Suite
```bash
python -m pytest --strict-config --strict-markers
# Target: All tests pass (or known failures documented)
```

### Level 4: Manual Verification
```bash
# Verify specific changes
grep -r "pattern" --include="*.ini" --include="*.toml"

# Check section synchronization
diff <(grep -A 20 "\[tool:pytest\]" pytest.ini) \
     <(grep -A 20 "\[pytest\]" pytest.ini)
```

## Best Practices

### 1. Systematic Approach
- ✅ **Group related issues**: Batch fixes by category (deprecations, markers, discovery)
- ✅ **One batch at a time**: Complete each batch fully before moving to next
- ✅ **Verify each step**: Scanner → edit → scanner → validate

### 2. Configuration Organization
- ✅ **Alphabetical markers**: Easier to maintain and locate
- ✅ **Section synchronization**: Keep `[tool:pytest]` and `[pytest]` identical
- ✅ **Centralized discovery**: Use root for common patterns, subprojects for exceptions

### 3. Validation Rigor
- ✅ **Multiple validation levels**: Scanner + pytest strict + grep verification
- ✅ **Test count stability**: Ensure changes don't accidentally exclude tests
- ✅ **Zero warnings**: Strict enforcement prevents future drift

### 4. Documentation
- ✅ **Comment rationale**: Explain non-obvious changes
- ✅ **Track file modifications**: Maintain list of all edited files
- ✅ **Document patterns**: Record standard configurations for reuse

## Lessons Learned

### Validation is Critical
- User-requested validation discovered `[tool:pytest]` section inconsistency
- grep + file reads reveal section-level discrepancies
- Scanner "all checks passed" doesn't guarantee section synchronization

### Systematic Beats Ad-Hoc
- Breaking 27 issues into 3 batches enabled manageable execution
- Each batch had clear scope, verification, and validation steps
- Performance improved 79% through focused optimization

### Section Synchronization Matters
- Both `[tool:pytest]` and `[pytest]` sections must be identical
- Different tools read different sections
- Inconsistency causes subtle bugs and tool incompatibility

### Alphabetical Organization
- Easier to spot missing or duplicate markers
- Simpler to maintain over time
- Consistent format improves readability

## CI Integration (Future)

### Recommended GitHub Actions Step

```yaml
- name: Pytest Configuration Audit
  run: |
    python tools/pytest_config_audit.py

    # Parse JSON report and fail on issues
    UNREGISTERED=$(cat pytest_config_audit.json | jq '.unregistered_markers | length')
    DEPRECATED=$(cat pytest_config_audit.json | jq '.deprecated_options | length')
    CONFLICTS=$(cat pytest_config_audit.json | jq '.discovery.conflicts | length')

    if [ $UNREGISTERED -gt 0 ] || [ $DEPRECATED -gt 0 ] || [ $CONFLICTS -gt 0 ]; then
      echo "❌ Pytest configuration issues detected"
      exit 1
    fi

    echo "✅ Pytest configuration clean"

- name: Upload Scanner Report
  uses: actions/upload-artifact@v3
  with:
    name: pytest-config-audit
    path: pytest_config_audit.json
```

### Benefits
- ✅ **Prevents drift**: Catches config issues before merge
- ✅ **Automated enforcement**: No manual review needed
- ✅ **Historical tracking**: JSON artifacts show config evolution
- ✅ **Fast feedback**: Scanner runs in ~15 seconds

## Troubleshooting

### Issue: Scanner Shows Conflicts But Pytest Works

**Cause**: Scanner detects section-level inconsistencies; pytest uses combined config.

**Solution**: Synchronize both `[tool:pytest]` and `[pytest]` sections for best practices.

### Issue: New Markers Appear Unregistered

**Cause**: Markers used in tests but not registered in `pytest.ini`.

**Solution**:
1. Identify marker category (Sacred Geometry, domain-specific, etc.)
2. Add to markers section in alphabetical order with description
3. Add to both `[tool:pytest]` and `[pytest]` sections

### Issue: Test Count Changes After Config Updates

**Cause**: Discovery pattern changes excluded or included tests unintentionally.

**Solution**:
1. Compare `pytest --collect-only` output before/after changes
2. Review `testpaths` and `norecursedirs` carefully
3. Validate expected test count in CI

## Summary

This methodology achieved **100% issue resolution** across a large multi-project workspace with:

- ✅ **27 issues → 0 issues**
- ✅ **14 config files harmonized**
- ✅ **2666 tests validated** with zero warnings
- ✅ **79% scanner performance improvement**

**Key Success Factors**:
1. Systematic batch approach
2. Rigorous multi-level validation
3. Section synchronization
4. Alphabetical organization
5. Comprehensive verification

For questions or issues, see:
- Scanner source: `tools/pytest_config_audit.py`
- Configuration examples: Root `pytest.ini` and `pyproject.toml`
- Test validation: `python -m pytest --strict-config --strict-markers --collect-only`
