# GitIgnore Observability Analysis Report

**Date**: 2025-11-25
**Status**: Complete
**Analyst**: ContextForge Cognitive Agent
**Priority**: HIGH - Affects project governance and evidence tracking

---

## Executive Summary

A comprehensive analysis of the `.gitignore` configuration reveals **significant observability gaps** that are limiting version control of critical files. The current configuration excludes:

- **~342,000+ files** from version control
- **Evidence bundles** (`.jsonl` files) critical for ContextForge governance
- **QSE session artifacts** required for audit trails
- **Database files** containing task and velocity data
- **Configuration and workflow artifacts** needed for reproducibility

While many exclusions are appropriate (Python cache, node_modules, IDE files), several patterns are **over-broad** and inadvertently exclude files that should be tracked per ContextForge Universal Methodology.

---

## Critical Issues Identified

### Issue 1: JSONL Evidence Files Blocked Despite Overrides

**Pattern**: `*.jsonl` (line 110)

**Problem**: The blanket exclusion of `*.jsonl` files blocks evidence bundles even though there are "Provenance Protection Overrides" attempting to unignore them.

**Evidence**:
```
!EvidenceBundle*.jsonl    # Override attempt (line 117)
!artifact-manifest.jsonl  # Override attempt (line 118)
```

**Root Cause**: Git negation patterns (`!pattern`) only work if the file's parent directory isn't ignored. Many evidence files live in directories that are themselves ignored (e.g., `logs/`, `.QSE/`).

**Impact**:
- Evidence bundles not tracked
- Audit trail incomplete
- Constitutional Framework compliance compromised

---

### Issue 2: QSE Session Artifacts Completely Excluded

**Patterns** (lines 143-158):
```gitignore
QSE-LOG-*.yaml
QSM-*.yaml
*Matrix.*.yaml
*Plan.*.yaml
*Report.*.yaml
*Scope.*.yaml
*Check.*.yaml
SME.*.yaml
ConstitutionalComplianceReport.*.yaml
ExecutionPlan.CF-*.yaml
TaskScope.*.yaml
OptionsMatrix.*.yaml
ResearchPlan.*.yaml
SourceTrustReport.*.yaml
ScopeCheck.*.yaml
```

**Problem**: These patterns exclude ALL QSE workflow artifacts including:
- Session logs for audit trails
- Constitutional compliance reports
- Execution plans and scopes
- Research plans and matrices

**Impact**:
- No version history of QSE sessions
- Cannot reproduce workflows
- UCL compliance evidence lost

---

### Issue 3: Database Files Ignored

**Patterns** (lines 194-204):
```gitignore
db/*.backup.*
db/test_*.duckdb
db/local.sqlite
db/cf_cli_registry.sqlite
db/backups/
db/contextforge.duckdb
velocity_tracker.db
```

**Problem**: Critical operational databases are excluded:
- `contextforge.duckdb` - Velocity tracking data
- `cf_cli_registry.sqlite` - CLI configuration registry
- `velocity_tracker.db` - Performance metrics

**Impact**:
- Velocity baseline data not preserved
- Configuration drift across environments
- Performance trend analysis impossible

---

### Issue 4: Logs Directory Over-Restricted

**Pattern** (line 109):
```gitignore
logs/*
!logs/README.md
```

**Problem**: Only `README.md` is kept from logs directory. All structured JSONL logs excluded.

**Impact**:
- UnifiedLogger output not tracked
- Session evidence incomplete
- Debugging history lost

---

### Issue 5: Development Scripts Pattern Too Broad

**Patterns** (lines 215-228):
```gitignore
working_*.py
simple_*.py
debug_*.py
test_*.py      # TOO BROAD - excludes actual test files
check_*.py
validate_*.py
```

**Problem**: `test_*.py` pattern excludes legitimate test files that should be tracked.

**Impact**:
- Test files may be excluded
- Coverage gaps introduced

---

### Issue 6: Missing .QSE Directory Protection

**Finding**: The `.QSE/` directory and its nested `.gitignore` further restrict observability.

**Nested .QSE/.gitignore**:
```gitignore
# Typical QSE exclusions
Sessions/
Evidence/
temp/
```

**Impact**:
- QSE session history not tracked
- Evidence bundles double-blocked
- Workflow reproducibility impossible

---

## Inventory of Key Excluded Files

### Category: Evidence & Governance (CRITICAL)

| Pattern | Example Files | Should Track? |
|---------|---------------|---------------|
| `*.jsonl` | `EvidenceBundle-20251125.jsonl` | ✅ YES |
| `QSE-LOG-*.yaml` | `QSE-LOG-session-20251125.yaml` | ✅ YES |
| `ConstitutionalComplianceReport.*.yaml` | `ConstitutionalComplianceReport.W-001.yaml` | ✅ YES |
| `*Matrix.*.yaml` | `DecisionMatrix.W-001.yaml` | ✅ YES |

### Category: Configuration & State (IMPORTANT)

| Pattern | Example Files | Should Track? |
|---------|---------------|---------------|
| `db/contextforge.duckdb` | Velocity tracking database | ⚠️ CONSIDER |
| `velocity_tracker.db` | Performance baseline | ⚠️ CONSIDER |
| `.vscode/settings.json` | Workspace configuration | ⚠️ CONSIDER |

### Category: Development Artifacts (APPROPRIATE)

| Pattern | Example Files | Should Track? |
|---------|---------------|---------------|
| `__pycache__/` | Python bytecode | ❌ NO |
| `node_modules/` | NPM dependencies | ❌ NO |
| `.pytest_cache/` | Test cache | ❌ NO |
| `*.pyc` | Compiled Python | ❌ NO |

---

## Recommendations

### R1: Fix Evidence Bundle Tracking (CRITICAL)

**Current** (line 110):
```gitignore
*.jsonl
*.ndjson
```

**Recommended**:
```gitignore
# JSONL logs (exclude ephemeral, keep evidence)
logs/*.jsonl
!logs/evidence-*.jsonl
!**/EvidenceBundle*.jsonl
!**/artifact-manifest.jsonl
```

**Alternative**: Move evidence to dedicated tracked directory:
```gitignore
# Track evidence directory explicitly
!evidence/
evidence/**/*.jsonl
```

---

### R2: Selective QSE Artifact Tracking (HIGH)

**Current** (lines 143-158): All excluded

**Recommended**:
```gitignore
# QSE Temporary Session Files (exclude)
.QSE/v*/Sessions/temp/
.QSE/v*/temp/

# QSE Evidence & Archives (TRACK)
!.QSE/v*/Evidence/
!.QSE/v*/Archives/
!.QSE/v*/Schemas/

# QSE Reports - Keep finalized, exclude in-progress
*Matrix.*.yaml
*Plan.*.yaml
!*.FINAL.yaml
!*-COMPLETE.yaml
```

---

### R3: Protect Key Database Files (MEDIUM)

**Recommended**:
```gitignore
# Database backups (exclude)
db/*.backup.*
db/backups/

# Development databases (exclude)
db/test_*.duckdb
db/local.sqlite

# Production databases (TRACK with LFS for large files)
!db/contextforge.duckdb
!db/velocity.duckdb
```

**Note**: Consider Git LFS for database files >50MB.

---

### R4: Fix Test File Pattern (HIGH)

**Current** (line 221):
```gitignore
test_*.py
```

**Problem**: Excludes legitimate test files like `test_unified_logger.py`.

**Recommended**:
```gitignore
# Temporary test scripts (root only)
/test_*.py
/temp_test_*.py

# But DO track actual test modules
!tests/test_*.py
!**/tests/test_*.py
```

---

### R5: Structured Logs Directory (MEDIUM)

**Current** (line 109):
```gitignore
logs/*
!logs/README.md
```

**Recommended**:
```gitignore
# Ephemeral logs (exclude)
logs/*.log
logs/debug/
logs/temp/

# Structured evidence logs (TRACK)
!logs/evidence/
!logs/sessions/
!logs/audit/
```

---

### R6: Create Evidence-First Directory Structure

**Proposed Structure**:
```
evidence/                    # TRACKED - All evidence bundles
├── sessions/               # QSE session exports
├── bundles/                # Constitutional evidence
└── audit/                  # Compliance reports

.QSE/v2/
├── Schemas/                # TRACKED - Schema definitions
├── Archives/               # TRACKED - Archived sessions
├── Evidence/               # TRACKED - Evidence bundles
└── Sessions/               # EXCLUDED - Active session temp files
    └── temp/               # EXCLUDED
```

---

## Implementation Plan

### Phase 1: Critical Fixes (Immediate)

1. Fix `*.jsonl` pattern to allow evidence bundles
2. Remove over-broad `test_*.py` pattern
3. Add explicit `!evidence/` negation

### Phase 2: QSE Artifact Management (This Week)

1. Create `evidence/` tracked directory
2. Update QSE workflows to output to tracked location
3. Archive existing evidence to new structure

### Phase 3: Database Strategy (Next Sprint)

1. Evaluate Git LFS for database files
2. Create database export/restore workflow
3. Track schema definitions, not data files

---

## Verification Commands

After implementing changes, verify with:

```bash
# Check what would be tracked
git status --ignored

# Find critical files still ignored
git ls-files --ignored --exclude-standard | grep -E "(Evidence|evidence|\.jsonl|QSE-LOG)"

# Verify evidence directory tracked
git check-ignore -v evidence/

# Test specific file
git check-ignore -v EvidenceBundle-test.jsonl
```

---

## Related Documents

- [03-Context-Ontology-Framework.md](../03-Context-Ontology-Framework.md) - COF evidence requirements
- [09-Development-Guidelines.md](../09-Development-Guidelines.md) - Logging standards
- [13-Testing-Validation.md](../13-Testing-Validation.md) - QSE framework

---

## Conclusion

The current `.gitignore` configuration prioritizes repository hygiene over observability, inadvertently excluding critical evidence and governance artifacts. The recommendations above balance cleanliness with the ContextForge Universal Methodology's requirements for evidence-based governance.

**Priority Actions**:
1. ✅ Fix evidence bundle tracking immediately
2. ✅ Remove over-broad test pattern
3. ⚠️ Restructure QSE evidence storage
4. ⚠️ Consider Git LFS for databases

---

**Document Status**: Complete ✅
**Next Review**: After implementation
**Maintained By**: ContextForge Architecture Team
