# Migration Plan: cf_core.logging Consolidation

**Status:** Draft
**Version:** 1.0.0
**Created:** 2025-12-30
**Project ID:** P-CFCORE-LOGGING-CONSOLIDATION

---

## Overview

This document defines the 4-phase migration strategy for consolidating 5+ fragmented logging implementations into the unified `cf_core.logging` module while maintaining 100% backward compatibility.

**Goal:** Zero disruption to existing code during migration, with clear deprecation path.

---

## Phase Summary

| Phase | Name | Duration | Risk | Key Deliverable |
|-------|------|----------|------|-----------------|
| 1 | Parallel Implementation | 1-2 weeks | Low | `cf_core/logging/` module with opt-in flag |
| 2 | Shim Layer | 1 week | Low | Re-exports from legacy paths |
| 3 | Deprecation Warnings | 2 weeks | Medium | CI enforcement of warnings |
| 4 | Consolidation | 1-2 weeks | High | Remove deprecated modules |

**Total Timeline:** 5-7 weeks

---

## Phase 1: Parallel Implementation

**Duration:** 1-2 weeks
**Risk Level:** Low
**Feature Flag:** `CFCORE_LOGGING_V3=1`

### Objectives

- Build complete `cf_core/logging/` package alongside existing implementations
- Opt-in testing via environment variable
- Zero impact to existing code paths

### Deliverables

```
cf_core/logging/
├── __init__.py           # Public API exports
├── core.py               # get_logger(), ulog(), configure_logging()
├── correlation.py        # ContextVar, get_correlation_id(), correlation_context()
├── evidence.py           # RFC 8785 canonicalize(), hash_evidence(), capture_evidence()
├── runtime.py            # RuntimeBuilder, Runtime (moved from logger_provider.py)
└── _compat.py            # Internal compatibility utilities
```

### Implementation Tasks

| Task | Estimate | Dependencies |
|------|----------|--------------|
| Create `cf_core/logging/__init__.py` with API surface | 2h | None |
| Implement `core.py` with structlog backend | 4h | ADR-002 |
| Implement `correlation.py` with ContextVar | 3h | ADR-002 |
| Implement `evidence.py` with RFC 8785 | 4h | ADR-003 |
| Move RuntimeBuilder to `runtime.py` | 2h | correlation.py |
| Add unit tests (≥80% coverage) | 4h | All modules |
| Add integration tests | 3h | Unit tests |
| Documentation in module docstrings | 2h | All modules |

**Total Estimate:** ~24 hours (based on 0.23 hrs/point velocity)

### Feature Flag Behavior

```python
# cf_core/logging/__init__.py

import os

_V3_ENABLED = os.environ.get("CFCORE_LOGGING_V3", "0") == "1"

if _V3_ENABLED:
    from cf_core.logging.core import get_logger, ulog
    from cf_core.logging.correlation import correlation_context
    from cf_core.logging.evidence import capture_evidence
else:
    # Fall back to existing implementations
    from python.services.unified_logger import logger as get_logger
    from python.services.unified_logger import ulog
    # ... etc
```

### Exit Criteria

- [ ] All modules pass unit tests
- [ ] Feature flag enables new implementation
- [ ] Feature flag disabled keeps existing behavior
- [ ] No changes to any existing files (except adding new package)

### Rollback Procedure

Delete `cf_core/logging/` directory. No other changes needed.

---

## Phase 2: Shim Layer

**Duration:** 1 week
**Risk Level:** Low
**Prerequisite:** Phase 1 complete and tested

### Objectives

- Add re-exports from legacy import paths
- Preserve 100% API compatibility
- Enable gradual migration without code changes

### Shim Implementations

#### Shim 1: python/services/unified_logger.py

```python
"""
Backward compatibility shim.

DEPRECATED: Use cf_core.logging instead.
This module re-exports from cf_core.logging for compatibility.
"""
import warnings
import os

# Only warn in non-test environments
if os.environ.get("PYTEST_CURRENT_TEST") is None:
    warnings.warn(
        "python.services.unified_logger is deprecated. "
        "Use 'from cf_core.logging import get_logger, ulog' instead.",
        DeprecationWarning,
        stacklevel=2
    )

# Re-export everything from new location
from cf_core.logging import (
    get_logger,
    ulog,
    configure_logging,
    correlation_context,
    get_correlation_id,
)

# Preserve 'logger' alias for common pattern
logger = get_logger("python.services.unified_logger")

__all__ = [
    "get_logger",
    "ulog",
    "configure_logging",
    "correlation_context",
    "get_correlation_id",
    "logger",
]
```

#### Shim 2: src/unified_logging/__init__.py

```python
"""
Backward compatibility shim.

DEPRECATED: Use cf_core.logging instead.
"""
import warnings
import os

if os.environ.get("PYTEST_CURRENT_TEST") is None:
    warnings.warn(
        "src.unified_logging is deprecated. "
        "Use 'from cf_core.logging import ulog' instead.",
        DeprecationWarning,
        stacklevel=2
    )

from cf_core.logging import (
    ulog,
    capture_evidence,
    hash_evidence,
)

# Preserve logged_action decorator if it exists
try:
    from cf_core.logging.decorators import logged_action
except ImportError:
    # Create minimal implementation
    def logged_action(func):
        return func

__all__ = ["ulog", "capture_evidence", "hash_evidence", "logged_action"]
```

#### Shim 3: src/unified_logging/core.py

```python
"""
Backward compatibility shim for core utilities.

DEPRECATED: Use cf_core.logging instead.
"""
import warnings

warnings.warn(
    "src.unified_logging.core is deprecated. "
    "Use 'from cf_core.logging import get_correlation_id' instead.",
    DeprecationWarning,
    stacklevel=2
)

from cf_core.logging.correlation import (
    get_correlation_id,
    set_correlation_id,
)

__all__ = ["get_correlation_id", "set_correlation_id"]
```

#### Shim 4: src/unified_logging/processors.py

```python
"""
Backward compatibility shim for log processors.

DEPRECATED: Use cf_core.logging instead.
"""
import warnings

warnings.warn(
    "src.unified_logging.processors is deprecated. "
    "Use 'from cf_core.logging.core import configure_logging' instead.",
    DeprecationWarning,
    stacklevel=2
)

from cf_core.logging.core import configure_logging

__all__ = ["configure_logging"]
```

#### Shim 5: cf_core/logger_provider.py

```python
"""
Backward compatibility shim for RuntimeBuilder.

DEPRECATED: Use cf_core.logging.runtime instead.
"""
import warnings

warnings.warn(
    "cf_core.logger_provider is deprecated. "
    "Use 'from cf_core.logging.runtime import RuntimeBuilder, Runtime' instead.",
    DeprecationWarning,
    stacklevel=2
)

from cf_core.logging.runtime import RuntimeBuilder, Runtime

__all__ = ["RuntimeBuilder", "Runtime"]
```

### Implementation Tasks

| Task | Estimate | Dependencies |
|------|----------|--------------|
| Update `python/services/unified_logger.py` | 1h | Phase 1 |
| Update `src/unified_logging/__init__.py` | 1h | Phase 1 |
| Update `src/unified_logging/core.py` | 1h | Phase 1 |
| Update `src/unified_logging/processors.py` | 1h | Phase 1 |
| Update `cf_core/logger_provider.py` | 1h | Phase 1 |
| Add deprecation warning tests | 2h | Shims |
| Verify all 393 `ulog()` call sites work | 8h | All shims |
| Verify MCP servers work unchanged | 2h | RuntimeBuilder shim |

**Total Estimate:** ~15 hours (updated for 393 actual call sites)

### Exit Criteria

- [ ] All existing imports continue working
- [ ] DeprecationWarning emitted for legacy imports
- [ ] All 393 `ulog()` call sites pass tests (verified via grep: `grep -r "ulog(" --include="*.py" | grep -v test | grep -v archived | wc -l`)
- [ ] MCP servers function unchanged
- [ ] No functional regressions

### Rollback Procedure

Revert shim file changes via git. Original implementations remain functional.

---

## Phase 3: Deprecation Warnings

**Duration:** 2 weeks
**Risk Level:** Medium
**Prerequisite:** Phase 2 complete

### Objectives

- Enable deprecation warnings in CI
- Track migration progress
- Provide clear migration guidance

### CI Configuration

```yaml
# .github/workflows/deprecation-check.yml
name: Deprecation Warning Check

on: [push, pull_request]

jobs:
  check-deprecations:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -e .

      - name: Run deprecation check
        run: |
          python -W error::DeprecationWarning -c "
          import warnings
          warnings.filterwarnings('error', category=DeprecationWarning)

          # Test known legacy imports
          try:
              from python.services.unified_logger import ulog
              print('FAIL: python.services.unified_logger still in use')
              exit(1)
          except DeprecationWarning:
              print('OK: Deprecation warning raised')
          "
```

### Migration Progress Tracking

```bash
# Track migration progress with grep
echo "=== Migration Progress ==="
echo "Legacy imports remaining:"
grep -r "from python.services.unified_logger" --include="*.py" | wc -l
grep -r "from src.unified_logging" --include="*.py" | wc -l
grep -r "from cf_core.logger_provider" --include="*.py" | wc -l

echo "New imports adopted:"
grep -r "from cf_core.logging" --include="*.py" | wc -l
```

### Migration Guide for Developers

```markdown
## Migrating to cf_core.logging

### Before (deprecated)
```python
from python.services.unified_logger import logger, ulog
from src.unified_logging import logged_action
from cf_core.logger_provider import RuntimeBuilder
```

### After (recommended)
```python
from cf_core.logging import get_logger, ulog
from cf_core.logging.decorators import logged_action
from cf_core.logging.runtime import RuntimeBuilder
```

### Quick migration script
```bash
# Find and replace in your codebase
find . -name "*.py" -exec sed -i \
  's/from python.services.unified_logger import/from cf_core.logging import/g' {} \;
```
```

### Implementation Tasks

| Task | Estimate | Dependencies |
|------|----------|--------------|
| Create deprecation check workflow | 2h | Phase 2 |
| Create migration progress script | 1h | None |
| Write migration guide | 2h | None |
| Migrate 50% of call sites (~197 imports) | 12h | Migration guide |
| Update contributor docs | 1h | Migration guide |

**Total Estimate:** ~18 hours (updated for 393 actual call sites)

### Exit Criteria

- [ ] CI warns on deprecated imports
- [ ] ≥50% of call sites migrated to new imports
- [ ] Migration guide published
- [ ] No new code uses deprecated imports
- [ ] **CRITICAL:** Create and push `pre-consolidation` branch for Phase 4 rollback: `git checkout -b pre-consolidation && git push -u origin pre-consolidation`

### Rollback Procedure

Disable deprecation workflow. Shims continue working.

---

## Phase 4: Consolidation

**Duration:** 1-2 weeks
**Risk Level:** High
**Prerequisite:** Phase 3 complete, ≥80% migrated

### Objectives

- Remove deprecated modules
- Update all remaining imports
- Archive historical code

### Pre-Consolidation Checklist

- [ ] ≥80% of imports migrated (run progress script)
- [ ] All CI tests passing
- [ ] No P0/P1 issues blocked by logging
- [ ] Team notified of breaking change date
- [ ] Rollback procedure tested

### Files to Remove

| File | Status | Replacement |
|------|--------|-------------|
| `src/unified_logger.py` | DELETE | `cf_core/logging/` |
| `python/ulog/__init__.py` | DELETE | `cf_core/logging/` |
| `python/ulog/unified.py` | DELETE | `cf_core/logging/` |
| `python/unified_logger.py` | DELETE | `cf_core/logging/` |

### Files to Archive (Move to archive/)

| File | Reason |
|------|--------|
| `src/unified_logging/core.py` | Historical reference |
| `src/unified_logging/evidence.py` | Historical reference |
| `cf_core/logger_provider.py` | Historical reference |

### Final Import Updates

```bash
# Automated migration for remaining legacy imports
find . -name "*.py" -type f ! -path "./archive/*" -exec sed -i \
  -e 's/from python\.services\.unified_logger import/from cf_core.logging import/g' \
  -e 's/from src\.unified_logging import/from cf_core.logging import/g' \
  -e 's/from cf_core\.logger_provider import/from cf_core.logging.runtime import/g' \
  {} \;
```

### Implementation Tasks

| Task | Estimate | Dependencies |
|------|----------|--------------|
| Run pre-consolidation checklist | 1h | Phase 3 |
| Migrate remaining call sites | 4h | Checklist pass |
| Remove deprecated files | 1h | All migrated |
| Archive historical files | 1h | Files removed |
| Update all tests | 2h | Files removed |
| Final CI validation | 1h | Tests updated |
| Update documentation | 2h | All complete |

**Total Estimate:** ~12 hours

### Exit Criteria

- [ ] Zero deprecated imports in codebase
- [ ] All deprecated files removed or archived
- [ ] CI passes with deprecation errors enabled
- [ ] Documentation updated to reference only `cf_core.logging`
- [ ] Migration AAR written

### Rollback Procedure

**Note:** Phase 4 rollback requires git revert of file deletions.

```bash
# Revert Phase 4 changes
git revert --no-commit HEAD~5..HEAD
git checkout origin/pre-consolidation -- src/unified_logging/
git checkout origin/pre-consolidation -- python/services/unified_logger.py
git checkout origin/pre-consolidation -- cf_core/logger_provider.py
git commit -m "chore: rollback Phase 4 consolidation"
```

---

## Risk Matrix

| Risk | Phase | Impact | Probability | Mitigation |
|------|-------|--------|-------------|------------|
| Breaking existing imports | 2 | High | Low | Comprehensive shims |
| Performance regression | 1 | Medium | Low | Benchmark in CI |
| Evidence hash mismatch | 1 | Medium | Medium | RFC 8785 test suite |
| Incomplete migration tracking | 3 | Medium | Medium | Automated grep scripts |
| Rollback complexity | 4 | High | Low | Pre-consolidation branch |
| Team confusion | 3 | Low | Medium | Clear migration guide |

---

## Success Metrics

### Quantitative

| Metric | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|--------|---------|---------|---------|---------|
| Import paths working | N/A | 6/6 | 6/6 | 1 canonical |
| Test coverage | ≥80% | ≥80% | ≥80% | ≥80% |
| Performance (ulog overhead) | <5ms | <5ms | <5ms | <5ms |
| Migration % | 0% | 0% | ≥50% | 100% |

### Qualitative

- [ ] No developer confusion about which logger to use
- [ ] Clear deprecation warnings guide migration
- [ ] Evidence bundles pass audit verification
- [ ] PowerShell ↔ Python correlation works seamlessly

---

## Communication Plan

| Milestone | Audience | Channel | Message |
|-----------|----------|---------|---------|
| Phase 1 Start | Dev team | Slack | "New cf_core.logging available for opt-in testing" |
| Phase 2 Complete | Dev team | Email | "Migration guide published, start updating imports" |
| Phase 3 Start | All contributors | README | "Deprecation warnings active, legacy imports sunset in 2 weeks" |
| Phase 4 Start | All contributors | Slack + Email | "Final migration: update imports by [date]" |
| Phase 4 Complete | All | CHANGELOG | "cf_core.logging consolidation complete" |

---

## References

- PRD: `docs/prd/PRD-CFCORE-LOGGING.md`
- ADR-002: Correlation ID Strategy
- ADR-003: Evidence Bundle Compliance
- Design Prompt: `docs/prompts/cf-core-centralized-logging-design.prompt.md`
- Codex: `docs/Codex/ContextForge Work Codex.md`

---

**Document Status:** Draft
**Next Review:** Before Phase 1 kickoff
**Maintained By:** ContextForge QSE Team
