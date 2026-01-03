# TaskMan-v2 GitHub Repository Scaffolding Plan

**Created**: 2025-12-04
**Status**: Planning
**Issue**: The TaskMan-v2 submodule has a placeholder remote URL and needs a proper GitHub repository

## Current State

| Aspect | Current Value | Issue |
|--------|---------------|-------|
| Submodule path | `TaskMan-v2/` | ✅ Exists |
| Remote URL in .gitmodules | `https://github.com/jhardy82/TaskMan-v2-clean.git` | ❌ Repo doesn't exist |
| Actual origin remote | `https://github.com/jhardy82/SCCMScripts` | ❌ Points to parent repo |
| Branch | `fix/flaky-test-improvements-20251203` | ⚠️ Should have its own branch |

## Goal

Create a new clean GitHub repository for TaskMan-v2 and properly configure it as a submodule in the main ContextForge workspace.

---

## Phase 1: Prepare Local Repository (5 min)

### 1.1 Navigate to TaskMan-v2 directory
```bash
cd "c:\Users\james.e.hardy\Documents\PowerShell Projects\TaskMan-v2"
```

### 1.2 Remove the incorrect origin remote
```bash
git remote remove origin
```

### 1.3 Create a clean initial branch
```bash
git checkout -b main
# Or reset to just the TaskMan-v2 specific commits if history is mixed
```

---

## Phase 2: Create GitHub Repository (2 min)

### 2.1 Create repository via GitHub CLI
```bash
gh repo create jhardy82/TaskMan-v2 \
  --description "TaskMan v2 - Modern task management with TypeScript MCP integration" \
  --public \
  --source=. \
  --remote=origin \
  --push
```

**Alternative (Web UI)**:
1. Go to https://github.com/new
2. Name: `TaskMan-v2`
3. Description: "TaskMan v2 - Modern task management with TypeScript MCP integration"
4. Public repository
5. NO README, .gitignore, or license (we already have them)
6. Create repository

### 2.2 Add new remote and push
```bash
git remote add origin https://github.com/jhardy82/TaskMan-v2.git
git push -u origin main
```

---

## Phase 3: Update Parent Repository (5 min)

### 3.1 Update .gitmodules in parent repo
Change:
```ini
[submodule "TaskMan-v2"]
    path = TaskMan-v2
    url = https://github.com/jhardy82/TaskMan-v2-clean.git
```

To:
```ini
[submodule "TaskMan-v2"]
    path = TaskMan-v2
    url = https://github.com/jhardy82/TaskMan-v2.git
    branch = main
```

### 3.2 Sync submodule configuration
```bash
cd "c:\Users\james.e.hardy\Documents\PowerShell Projects"
git submodule sync
git submodule update --remote TaskMan-v2
```

### 3.3 Commit the configuration change
```bash
git add .gitmodules TaskMan-v2
git commit -m "chore: Update TaskMan-v2 submodule to use new repository

- Created dedicated TaskMan-v2 GitHub repository
- Updated .gitmodules with correct URL
- Synced submodule configuration"
```

---

## Phase 4: Verify Setup (2 min)

### 4.1 Test fresh clone
```bash
# In a temp directory
git clone --recurse-submodules https://github.com/jhardy82/SCCMScripts.git test-clone
cd test-clone/TaskMan-v2
git remote -v
# Should show: origin  https://github.com/jhardy82/TaskMan-v2.git
```

### 4.2 Test pre-push hook
```bash
cd "c:\Users\james.e.hardy\Documents\PowerShell Projects"
# Make a test change in TaskMan-v2
echo "# Test" >> TaskMan-v2/README.md
git add TaskMan-v2
git commit -m "test: Verify submodule hook"
git push
# Hook should detect and push TaskMan-v2 changes first
```

---

## Files Included in TaskMan-v2

Based on directory listing, TaskMan-v2 contains:
- **MCP Server**: `mcp-server-ts/` - TypeScript MCP implementation
- **Frontend**: React + TypeScript (`src/`, `vscode-extension/`)
- **Tests**: Playwright, Vitest (`tests/`, `testsprite_tests/`)
- **Docs**: Implementation plans and guides (`docs/`, multiple `.md` files)
- **Config**: Docker, Vite, Tailwind, etc.

---

## Decision Points

### Q1: Should we filter git history?
**Options**:
1. Keep full history (includes parent repo commits) - Simple but noisy
2. Filter to only TaskMan-v2 relevant commits - Clean but complex
3. Squash to single initial commit - Cleanest but loses history

**Recommendation**: Option 1 (keep full history) initially, can clean up later

### Q2: Should we use SSH or HTTPS for submodule URL?
**Options**:
1. HTTPS (current) - Works without SSH key setup
2. SSH - Requires SSH key but more secure for push

**Recommendation**: HTTPS for now, can switch later

---

## Rollback Plan

If something goes wrong:
```bash
# Restore original .gitmodules
git checkout HEAD~1 -- .gitmodules
git submodule sync

# Remove the new remote from TaskMan-v2
cd TaskMan-v2
git remote remove origin
git remote add origin https://github.com/jhardy82/SCCMScripts
```

---

## Success Criteria

- [ ] TaskMan-v2 has its own GitHub repository at `jhardy82/TaskMan-v2`
- [ ] `git submodule update --remote TaskMan-v2` works
- [ ] Pre-push hook successfully pushes TaskMan-v2 changes
- [ ] Fresh clone with `--recurse-submodules` works correctly
- [ ] All TaskMan-v2 tests pass after migration

---

## Estimated Time

| Phase | Time |
|-------|------|
| Phase 1: Prepare Local | 5 min |
| Phase 2: Create GitHub Repo | 2 min |
| Phase 3: Update Parent | 5 min |
| Phase 4: Verify | 2 min |
| **Total** | **~15 min** |
