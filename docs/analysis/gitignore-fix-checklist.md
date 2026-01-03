# GitIgnore Fix Implementation Checklist

**Created**: 2025-11-25
**Source Analysis**: [gitignore-observability-analysis.md](./gitignore-observability-analysis.md)
**Branch**: `feat/taskman-v2-python-mcp-research-20251125`

---

## Quick Summary

| Issue # | Description | Severity | Lines | Status |
|---------|-------------|----------|-------|--------|
| 1 | `*.jsonl` blocks evidence bundles | CRITICAL | 110 | ⬜ |
| 2 | QSE session artifacts excluded | CRITICAL | 143-158 | ⬜ |
| 3 | Database files ignored | HIGH | 194-204 | ⬜ |
| 4 | `logs/*` too broad | HIGH | 109 | ⬜ |
| 5 | `test_*.py` blocks real tests | MEDIUM | 221 | ⬜ |
| 6 | `.QSE/` nested gitignore | HIGH | N/A | ⬜ |

---

## Phase 0: Pre-Implementation Preparation

### Backup & Baseline

- [ ] **Backup current `.gitignore`**
  ```powershell
  Copy-Item .gitignore .gitignore.backup-$(Get-Date -Format 'yyyyMMdd-HHmm')
  ```

- [ ] **Document currently ignored evidence files**
  ```powershell
  git ls-files --ignored --exclude-standard | Select-String -Pattern "(Evidence|evidence|\.jsonl|QSE-LOG)" | Out-File docs/analysis/ignored-evidence-baseline.txt
  ```

- [ ] **Create test files for verification** (optional but recommended)
  ```powershell
  # Create test evidence files to verify tracking after fixes
  New-Item -ItemType File -Path "evidence/test-evidence-bundle.jsonl" -Force
  New-Item -ItemType File -Path ".QSE/v2/Evidence/test-bundle.jsonl" -Force
  New-Item -ItemType File -Path "logs/evidence-test.jsonl" -Force
  ```

### Verify Current State

- [ ] **Confirm test files are ignored (pre-fix baseline)**
  ```powershell
  git check-ignore -v evidence/test-evidence-bundle.jsonl
  # Expected: Should show ignore rule
  ```

---

## Phase 1: Critical Fixes (Issues 1-2)

### Issue 1: `*.jsonl` Pattern (Line 110) - CRITICAL

**Current Pattern** (line 110):
```gitignore
*.jsonl
*.ndjson
```

**Problem**: Blocks ALL JSONL files including evidence bundles, even with negation overrides.

**Action Items**:

- [ ] **Locate line 110** in `.gitignore`
  ```powershell
  Select-String -Path .gitignore -Pattern "\*\.jsonl" -Context 2,2
  ```

- [ ] **Replace the pattern** - Change line 110-111 from:
  ```gitignore
  *.jsonl
  *.ndjson
  ```

  To:
  ```gitignore
  # JSONL logs (exclude ephemeral, keep evidence)
  logs/*.jsonl
  !logs/evidence-*.jsonl
  !**/EvidenceBundle*.jsonl
  !**/artifact-manifest.jsonl
  !evidence/**/*.jsonl
  !.QSE/**/Evidence/**/*.jsonl
  ```

- [ ] **Verify fix**
  ```powershell
  git check-ignore -v EvidenceBundle-test.jsonl
  # Expected: No output (file NOT ignored)

  git check-ignore -v evidence/test-evidence-bundle.jsonl
  # Expected: No output (file NOT ignored)
  ```

---

### Issue 2: QSE Session Artifacts (Lines 143-158) - CRITICAL

**Current Patterns** (lines 143-158):
```gitignore
QSE-LOG-*.yaml
TaskScope.*.yaml
ResearchPlan.*.yaml
*Matrix.*.yaml
*Plan.*.yaml
*Report.*.yaml
ConstitutionalComplianceReport.*.yaml
```

**Problem**: Excludes ALL QSE workflow artifacts including finalized evidence.

**Action Items**:

- [ ] **Add selective tracking exceptions** after line 158:
  ```gitignore
  # QSE Evidence & Finalized Artifacts (TRACK)
  !*-COMPLETE.yaml
  !*.FINAL.yaml
  !.QSE/v*/Evidence/**
  !.QSE/v*/Archives/**
  !.QSE/v*/Schemas/**
  !AAR-*.yaml
  ```

- [ ] **Verify fix**
  ```powershell
  # Finalized files should now be tracked
  git check-ignore -v "AAR-Test-COMPLETE.yaml"
  # Expected: No output (file NOT ignored)

  git check-ignore -v ".QSE/v2/Evidence/session-001.yaml"
  # Expected: No output (file NOT ignored)
  ```

---

## Phase 2: High Priority Fixes (Issues 3-4, 6)

### Issue 3: Database Files (Lines 194-204) - HIGH

**Current Patterns** (lines 194-204):
```gitignore
*.duckdb
*.duckdb.wal
velocity_tracker.db
contextforge.db
*.sqlite
*.sqlite3
*.db
```

**Problem**: Excludes velocity tracking and registry databases needed for reproducibility.

**Action Items**:

- [ ] **Add exceptions for key databases** after line 204:
  ```gitignore
  # Track key databases (consider Git LFS for large files)
  !db/contextforge.duckdb
  !db/velocity.duckdb
  !db/registry.sqlite
  ```

- [ ] **Verify fix**
  ```powershell
  git check-ignore -v db/contextforge.duckdb
  # Expected: No output (file NOT ignored) - or shows specific exception
  ```

- [ ] **Consider Git LFS** for large database files (>50MB)
  ```powershell
  # Optional: Enable Git LFS for database files
  git lfs track "*.duckdb"
  ```

---

### Issue 4: Logs Directory (Line 109) - HIGH

**Current Pattern** (line 109):
```gitignore
logs/*
!logs/README.md
```

**Problem**: Blocks ALL files in logs/ except README, including structured evidence logs.

**Action Items**:

- [ ] **Expand log exceptions** after line 109:
  ```gitignore
  logs/*
  !logs/README.md
  # Structured evidence logs (TRACK)
  !logs/evidence/
  !logs/evidence/**
  !logs/sessions/
  !logs/sessions/**
  !logs/audit/
  !logs/audit/**
  !logs/unified_log.jsonl
  !logs/session.jsonl
  ```

- [ ] **Verify fix**
  ```powershell
  git check-ignore -v logs/evidence/test.jsonl
  # Expected: No output (file NOT ignored)
  ```

---

### Issue 6: `.QSE/` Nested GitIgnore - HIGH

**Current** (`.QSE/.gitignore` or `.QSE/v2/.gitignore`):
```gitignore
Sessions/
Evidence/
temp/
```

**Problem**: Double-blocks QSE evidence even if root gitignore allows it.

**Action Items**:

- [ ] **Locate nested .gitignore files**
  ```powershell
  Get-ChildItem -Path ".QSE" -Filter ".gitignore" -Recurse -Force
  ```

- [ ] **Modify `.QSE/` gitignore** to allow Evidence:
  ```gitignore
  # Temporary session files only
  Sessions/temp/
  temp/

  # DO NOT ignore Evidence
  # Evidence/  <- REMOVE THIS LINE
  ```

- [ ] **Verify fix**
  ```powershell
  git check-ignore -v .QSE/v2/Evidence/test.jsonl
  # Expected: No output (file NOT ignored)
  ```

---

## Phase 3: Medium Priority Fix (Issue 5)

### Issue 5: Test File Pattern (Line 221) - MEDIUM

**Current Pattern** (line 221):
```gitignore
test_*.py
```

**Problem**: Excludes legitimate test files like `tests/test_unified_logger.py`.

**Action Items**:

- [ ] **Replace broad pattern** - Change line 221 from:
  ```gitignore
  test_*.py
  ```

  To:
  ```gitignore
  # Temporary test scripts in root only
  /test_*.py
  /temp_test_*.py

  # Track actual test modules in tests/ directories
  !tests/test_*.py
  !**/tests/test_*.py
  !tests/**/test_*.py
  ```

- [ ] **Verify fix**
  ```powershell
  git check-ignore -v tests/test_unified_logger.py
  # Expected: No output (file NOT ignored)

  git check-ignore -v test_scratch.py
  # Expected: Shows ignore rule (root temp file still ignored)
  ```

---

## Phase 4: Post-Implementation Verification

### Full Verification Suite

- [ ] **Run comprehensive ignore check**
  ```powershell
  # Should return empty or minimal results for evidence files
  git ls-files --ignored --exclude-standard | Select-String -Pattern "(Evidence|evidence|\.jsonl|QSE-LOG|AAR-)"
  ```

- [ ] **Test specific critical paths**
  ```powershell
  # All should return NO OUTPUT (not ignored)
  git check-ignore -v evidence/test.jsonl
  git check-ignore -v .QSE/v2/Evidence/bundle.jsonl
  git check-ignore -v logs/evidence/session.jsonl
  git check-ignore -v AAR-Test-COMPLETE.yaml
  git check-ignore -v tests/test_example.py
  ```

- [ ] **Verify trackable files appear**
  ```powershell
  git status
  # Should show new untracked files in evidence directories
  ```

### Commit Changes

- [ ] **Stage gitignore changes**
  ```powershell
  git add .gitignore
  git add .QSE/.gitignore  # If modified
  ```

- [ ] **Stage newly trackable evidence files**
  ```powershell
  git add evidence/
  git add .QSE/v2/Evidence/
  git add logs/evidence/
  ```

- [ ] **Create commit**
  ```powershell
  git commit -m "fix(gitignore): Enable evidence bundle tracking and QSE artifact observability

  CRITICAL FIXES:
  - Replace broad *.jsonl pattern with selective evidence exceptions
  - Add QSE Evidence/ and Archives/ to tracked directories
  - Enable structured logs tracking in logs/evidence/

  HIGH PRIORITY FIXES:
  - Add database file exceptions for velocity tracking
  - Fix nested .QSE/ gitignore to allow Evidence/
  - Scope test_*.py pattern to root directory only

  Resolves observability gaps identified in gitignore-observability-analysis.md

  Issue: 6 critical patterns blocking 522+ evidence files
  Solution: Selective negations preserving evidence while excluding ephemeral files"
  ```

- [ ] **Push to remote**
  ```powershell
  git push origin feat/taskman-v2-python-mcp-research-20251125
  ```

---

## Phase 5: Optional Enhancements (Future Sprint)

### Evidence Directory Restructure

- [ ] **Create dedicated evidence directory**
  ```powershell
  New-Item -ItemType Directory -Path evidence/sessions -Force
  New-Item -ItemType Directory -Path evidence/bundles -Force
  New-Item -ItemType Directory -Path evidence/audit -Force
  ```

- [ ] **Add tracking rule**
  ```gitignore
  # Evidence directory (always tracked)
  !evidence/
  !evidence/**
  ```

### Git LFS for Large Files

- [ ] **Install Git LFS** (if not already)
  ```powershell
  git lfs install
  ```

- [ ] **Track large database files**
  ```powershell
  git lfs track "*.duckdb"
  git lfs track "db/*.sqlite"
  ```

- [ ] **Commit .gitattributes**
  ```powershell
  git add .gitattributes
  git commit -m "chore: Enable Git LFS for database files"
  ```

---

## Rollback Instructions

If fixes cause unexpected issues:

```powershell
# Restore backup
Copy-Item .gitignore.backup-YYYYMMDD-HHMM .gitignore

# Or revert commit
git revert HEAD

# Or reset to previous state
git checkout HEAD~1 -- .gitignore
```

---

## Verification Checklist Summary

After all changes, confirm:

- [ ] Evidence bundles (`.jsonl`) can be tracked
- [ ] QSE finalized artifacts (`*-COMPLETE.yaml`) can be tracked
- [ ] AAR files (`AAR-*.yaml`) can be tracked
- [ ] Test files in `tests/` directory can be tracked
- [ ] Logs in `logs/evidence/` can be tracked
- [ ] `.QSE/v2/Evidence/` contents can be tracked
- [ ] Ephemeral files (temp, cache) are still ignored
- [ ] `node_modules/` and `.venv/` are still ignored

---

## Related Documents

- [gitignore-observability-analysis.md](./gitignore-observability-analysis.md) - Full analysis
- [03-Context-Ontology-Framework.md](../03-Context-Ontology-Framework.md) - COF evidence requirements
- [09-Development-Guidelines.md](../09-Development-Guidelines.md) - Logging standards

---

**Document Status**: Complete ✅
**Implementation Priority**: CRITICAL - Blocking evidence observability
**Estimated Time**: 30-45 minutes
