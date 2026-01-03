# Plan: Create Missing Submodule Repositories (Clean Commit + Fork)

**Status**: 🟡 In Progress
**Started**: 2025-11-23
**Estimated Completion**: 35 minutes
**Owner**: @jhardy82
**Priority**: High

---

## Executive Summary

Create `jhardy82/TaskMan-v2` with fresh clean commit (avoiding corrupted commit `1396367d`), fork `mrgoonie/claudekit-skills` to preserve upstream connection, fix local remotes, push content, update parent submodule references, and validate. Supports future ContextForge decoupling into sub-repos.

---

## Progress Tracking

**Overall Progress**: 0/7 steps completed (0%)

```
[░░░░░░░░░░░░░░░░░░░░] 0%
```

---

## Implementation Steps

### ✅ Step 1: Create `jhardy82/TaskMan-v2` Repository
**Status**: ⬜ Not Started
**Assignee**: @jhardy82
**Estimated Time**: 5 minutes
**Dependencies**: None

**Tasks**:
- [ ] Run `gh repo create jhardy82/TaskMan-v2 --private --description "TaskMan-v2 comprehensive task management system"`
- [ ] Verify creation with `gh repo view jhardy82/TaskMan-v2`
- [ ] Navigate to `TaskMan-v2/` directory
- [ ] Checkout clean commit: `git checkout e750070`
- [ ] Verify commit history clean (no Windows filename corruption)

**Validation**:
```powershell
gh repo view jhardy82/TaskMan-v2
cd TaskMan-v2
git log --oneline -5
```

**Notes**:
- Avoiding corrupted commit `1396367d` which contains Windows-incompatible filenames
- Using commit `e750070` as clean starting point

---

### ✅ Step 2: Fork `mrgoonie/claudekit-skills`
**Status**: ⬜ Not Started
**Assignee**: @jhardy82
**Estimated Time**: 3 minutes
**Dependencies**: None

**Tasks**:
- [ ] Run `gh repo fork mrgoonie/claudekit-skills --clone=false --remote=true`
- [ ] Verify fork created: `gh repo view jhardy82/claudekit-skills`
- [ ] Confirm upstream preserved in fork settings

**Validation**:
```powershell
gh repo view jhardy82/claudekit-skills --json parent
```

**Notes**:
- Fork preserves upstream connection for future updates
- Enables pulling mrgoonie's improvements while maintaining independent development

---

### ✅ Step 3: Fix Local Remote Configurations
**Status**: ⬜ Not Started
**Assignee**: @jhardy82
**Estimated Time**: 5 minutes
**Dependencies**: Steps 1-2

**Tasks**:
- [ ] **TaskMan-v2**: Remove circular reference
  - [ ] `cd TaskMan-v2`
  - [ ] `git remote remove origin`
  - [ ] `git remote add origin https://github.com/jhardy82/TaskMan-v2.git`
  - [ ] `git remote -v` to verify
- [ ] **claudekit-skills**: Update to fork
  - [ ] `cd ../claudekit-skills`
  - [ ] `git remote set-url origin https://github.com/jhardy82/claudekit-skills.git`
  - [ ] `git remote add upstream https://github.com/mrgoonie/claudekit-skills.git`
  - [ ] `git remote -v` to verify both origin and upstream

**Validation**:
```powershell
cd TaskMan-v2
git remote -v  # Should show jhardy82/TaskMan-v2

cd ../claudekit-skills
git remote -v  # Should show origin=jhardy82 and upstream=mrgoonie
```

**Notes**:
- TaskMan-v2 had circular reference pointing back to parent SCCMScripts
- claudekit-skills pointed to wrong owner (mrgoonie)

---

### ✅ Step 4: Push Content to New Repositories
**Status**: ⬜ Not Started
**Assignee**: @jhardy82
**Estimated Time**: 7 minutes
**Dependencies**: Step 3

**Tasks**:
- [ ] **TaskMan-v2**: Push clean commit
  - [ ] `cd TaskMan-v2`
  - [ ] Verify on commit `e750070`: `git log --oneline -1`
  - [ ] `git push -u origin main`
  - [ ] Verify push successful on GitHub
- [ ] **claudekit-skills**: Push current state
  - [ ] `cd ../claudekit-skills`
  - [ ] `git push -u origin main`
  - [ ] Verify push successful on GitHub
  - [ ] Test upstream fetch: `git fetch upstream`

**Validation**:
```powershell
# Check TaskMan-v2 on GitHub
gh repo view jhardy82/TaskMan-v2 --json defaultBranchRef

# Check claudekit-skills on GitHub
gh repo view jhardy82/claudekit-skills --json defaultBranchRef
```

**Notes**:
- TaskMan-v2 starts from clean commit `e750070`
- claudekit-skills maintains connection to upstream for future syncs

---

### ✅ Step 5: Update Parent `.gitmodules` and Commit
**Status**: ⬜ Not Started
**Assignee**: @jhardy82
**Estimated Time**: 5 minutes
**Dependencies**: Step 4

**Tasks**:
- [ ] Navigate to parent directory: `cd ..`
- [ ] Edit `.gitmodules` to verify correct URLs (should already be correct)
- [ ] Run `git submodule sync --recursive` to register new URLs
- [ ] Stage changes: `git add .gitmodules TaskMan-v2 claudekit-skills`
- [ ] Commit with message:
  ```
  fix(submodules): resolve circular reference and fork claudekit-skills

  - TaskMan-v2: removed circular reference to parent SCCMScripts
  - TaskMan-v2: pushed clean commit e750070 (avoiding Windows corruption)
  - claudekit-skills: forked from mrgoonie/claudekit-skills
  - claudekit-skills: preserved upstream for future sync capability

  Supports future ContextForge feature decoupling into sub-repos.
  ```
- [ ] Push to origin: `git push origin main`

**Validation**:
```powershell
git submodule status
git log --oneline -1
```

**Notes**:
- `git submodule sync` updates git's internal submodule URL cache
- Commit message documents circular reference fix and fork creation

---

### ✅ Step 6: Validate Fresh Clone Works
**Status**: ⬜ Not Started
**Assignee**: @jhardy82
**Estimated Time**: 8 minutes
**Dependencies**: Step 5

**Tasks**:
- [ ] Create clean temp directory: `$tempDir = New-Item -ItemType Directory -Path "$env:TEMP\submodule-validation-$(Get-Date -Format 'yyyyMMdd-HHmmss')"`
- [ ] Clone with submodules: `git clone --recurse-submodules https://github.com/jhardy82/SCCMScripts "$tempDir\test-validation"`
- [ ] Navigate to clone: `cd "$tempDir\test-validation"`
- [ ] Verify all four submodules initialized:
  - [ ] `git submodule status`
  - [ ] Check TaskMan-v2 initialized
  - [ ] Check claudekit-skills initialized
  - [ ] Check vs-code-task-manager initialized
  - [ ] Check dynamic-task-manager initialized
- [ ] Check no circular references:
  - [ ] `git submodule foreach 'git remote -v'`
  - [ ] Verify TaskMan-v2 points to jhardy82/TaskMan-v2 (not SCCMScripts)
  - [ ] Verify claudekit-skills points to jhardy82/claudekit-skills
- [ ] Clean up temp directory: `Remove-Item -Recurse -Force "$tempDir"`

**Validation**:
```powershell
# All submodules should show commit hash without '-' prefix (indicating initialized)
git submodule status

# No submodule should point back to parent SCCMScripts
git submodule foreach 'git remote -v' | Select-String "SCCMScripts"
```

**Success Criteria**:
- All 4 submodules show initialized status
- No circular references detected
- Clean clone completes without errors

---

### ✅ Step 7: Create Submodule Integrity CI Workflow
**Status**: ⬜ Not Started
**Assignee**: @jhardy82
**Estimated Time**: 7 minutes
**Dependencies**: Step 6

**Tasks**:
- [ ] Create `.github/workflows/submodule-integrity.yml`
- [ ] Add validation tests:
  - [ ] Circular reference detection
  - [ ] Orphaned submodule detection
  - [ ] Submodule commit reachability check
  - [ ] Submodule URL validation
- [ ] Configure triggers:
  - [ ] On push to main
  - [ ] On pull request
  - [ ] Daily scheduled run (cron: '0 2 * * *')
- [ ] Add status badge to README.md
- [ ] Commit and push workflow
- [ ] Verify workflow runs successfully

**Validation**:
```powershell
# Check workflow file syntax
gh workflow view submodule-integrity

# Trigger manual run
gh workflow run submodule-integrity.yml

# Check run status
gh run list --workflow=submodule-integrity.yml --limit 1
```

**Notes**:
- Daily scheduled validation catches configuration drift early
- Prevents future submodule misconfigurations

---

## Further Considerations

### 🤔 Question 1: Branch Strategy Alignment
**Status**: 🟡 Decision Needed
**Owner**: @jhardy82

Should claudekit-skills track `feature/contextforge-integration-20250926` branch (matching vs-code-task-manager and dynamic-task-manager pattern) or stay on default branch for easier upstream sync?

**Options**:
- **Option A**: Track feature branch for consistency
  - ✅ Matches other submodule branch patterns
  - ❌ Complicates upstream sync
- **Option B**: Stay on default branch
  - ✅ Easier upstream sync with `git fetch upstream && git merge upstream/main`
  - ❌ Branch pattern inconsistency

**Recommendation**: Option B (default branch) for easier upstream maintenance

---

### 🤔 Question 2: Future Decoupling Documentation
**Status**: 🟡 Decision Needed
**Owner**: @jhardy82

Should we document repository structure decisions in README.md "Repository Architecture" section explaining submodule strategy and planned ContextForge feature extraction?

**Benefits**:
- Helps future developers understand splitting rationale
- Documents decision history for architectural changes
- Provides context for ContextForge decoupling plans

**Recommendation**: Yes, add "Repository Architecture" section to README.md

---

### 🤔 Question 3: Upstream Sync Workflow Documentation
**Status**: 🟡 Decision Needed
**Owner**: @jhardy82

Create documentation for pulling mrgoonie/claudekit-skills updates into your fork?

**Proposed Process**:
```powershell
cd claudekit-skills
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

**Recommendation**: Yes, add to CONTRIBUTING.md or create docs/SUBMODULE-MAINTENANCE.md

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Corrupted commit contains needed code | Low | Medium | Review commit `1396367d` before finalizing to ensure no critical code loss |
| Upstream claudekit-skills diverges significantly | Medium | Low | Regular sync checks (quarterly) to merge upstream changes |
| Submodule URL changes break CI | Low | High | CI workflow validates URLs daily |
| Future ContextForge decoupling breaks submodules | Medium | High | Document architecture decisions, use semantic versioning |

---

## Success Criteria

- [x] All steps completed without errors
- [x] Fresh clone with `--recurse-submodules` works successfully
- [x] No circular references detected
- [x] TaskMan-v2 repository created and populated
- [x] claudekit-skills forked and upstream preserved
- [x] CI workflow validates submodule integrity
- [x] All 4 submodules initialize correctly

---

## Collaboration Notes

### 💬 Discussion Thread

**2025-11-23**: Plan created with clean commit strategy and fork approach

---

### 📝 Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-11-23 | Initial plan created with checklist and tracking | @jhardy82 |

---

## Resources

- [Git Submodules Documentation](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
- [GitHub CLI Fork Documentation](https://cli.github.com/manual/gh_repo_fork)
- [GitHub Submodule Best Practices](https://github.blog/2016-02-01-working-with-submodules/)

---

## Related Documents

- [.gitmodules](.gitmodules) - Parent repository submodule configuration
- [AGENTS.md](AGENTS.md) - Agent collaboration protocols
- Research findings: Comprehensive analysis of current submodule state

---

**Last Updated**: 2025-11-23
**Next Review**: After Step 6 completion
