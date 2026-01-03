# Unexpected Behaviors Catalog
*Created: 2025-11-13*

## Purpose
Document unexpected behaviors discovered during TaskMan-v2 VSCode Extension resumption.

---

## UB-001: Backend Port Mismatch
**Date**: 2025-11-13
**Severity**: Medium
**Status**: Discovered

### Issue
Extension configuration defaults to port 3000, but actual backend runs on port 3001.

### Evidence
- Extension `package.json`: `"taskman.dtm.serverPort": { "default": 3000 }`
- User correction: "Look at port 3001, that is the correct port for task management activities"

### Impact
- Extension cannot connect to backend with default settings
- Users must manually configure port setting
- Connection errors on first install

### Root Cause
- Likely changed during development but config not updated
- Or multiple services running on different ports

### Resolution Options
1. **Quick Fix**: Update default port in package.json to 3001
2. **Auto-Discovery**: Add port detection logic
3. **Better Defaults**: Check both ports and use whichever responds

### Recommended Action
Update `package.json` default from 3000 to 3001 (1 line change)

---

## UB-002: TypeScript Compilation Errors
**Date**: 2025-11-13
**Severity**: Medium
**Status**: RESOLVED (2025-11-13)

### Issue
Extension has TypeScript compilation errors preventing rebuild. 62+ type errors in existing code.

### Evidence
```
npm run compile fails with:
- Cannot find module 'vscode' (multiple files)
- Missing properties on TodoItem/TodoGroup (contextValue, tooltip, iconPath, etc.)
- Type 'unknown' not assignable to Project[]/Sprint[]/Task[]
- Implicit 'any' types in various places
```

### Impact
- Cannot rebuild extension from source
- Must use pre-compiled version
- Future development requires fixing types

### Root Cause
- Code was written but types weren't properly defined/exported
- VS Code types may not be properly resolved
- Model interfaces incomplete (missing UI-specific properties)

### Resolution Options
1. **Quick**: Use existing compiled version (out/ directory exists)
2. **Medium**: Fix type definitions incrementally
3. **Long**: Comprehensive type safety refactor

### Recommended Action
~~Use existing compiled version for v1.0.1 release. Fix types in v1.1 development cycle.~~

### Resolution (2025-11-13)
**Root Cause**: devDependencies were not being installed. npm was only installing production dependencies (4 packages) instead of all 406 packages.

**Fix Applied**:
1. Deleted package-lock.json and node_modules
2. Ran `npm install --include=dev` to force devDependencies installation
3. Verified @types/vscode@1.95.0 was installed correctly
4. Compilation now succeeds with 0 errors
5. Re-enabled prepublish script in package.json
6. Version bumped to 1.0.2

**Result**: TypeScript compilation fully working. Extension can now be rebuilt from source.

---

## UB-003: VS Code Engine/Types Version Mismatch
**Date**: 2025-11-13
**Severity**: High (blocks packaging)
**Status**: Discovered

### Issue
Package.json specifies VS Code engine ^1.80.0 (July 2023) but uses @types/vscode ^1.106.0 (much newer).

### Evidence
```
ERROR @types/vscode ^1.106.0 greater than engines.vscode ^1.80.0
```

### Impact
- Cannot package extension
- Extension may not work with older VS Code versions
- Packaging tool enforces version consistency

### Root Cause
- Types were updated but engine version wasn't
- VS Code 1.80 is from July 2023 (very old)
- Current VS Code is 1.95+ (November 2024)

### Resolution Options
1. **Upgrade engine**: Update to ^1.95.0 or ^1.90.0 (recommended)
2. **Downgrade types**: Use @types/vscode ^1.80.0 (loses modern APIs)

### Recommended Action
Upgrade engines.vscode to ^1.90.0 (stable, widely adopted, matches types better)

---

## UB-004: Extension Requires Newer VS Code Than Installed
**Date**: 2025-11-13
**Severity**: High (blocks installation)
**Status**: Discovered

### Issue
Extension now requires VS Code ^1.106.0 but user has VS Code 1.105.1 installed.

### Evidence
```
Error: Unable to install extension 'contextforge.taskman-v2-extension' as it is not compatible with VS Code '1.105.1'.
```

### Impact
- Cannot install extension on current VS Code
- Users must upgrade VS Code or we must downgrade requirement
- VS Code 1.106 is very recent (may not be widely adopted yet)

### Root Cause
- We matched engine version to @types/vscode ^1.106.0
- But VS Code 1.106.0 is bleeding edge (Nov 2024)
- User is on 1.105.1 (one version behind)

### Resolution Options
1. **Downgrade engine**: Use ^1.95.0 (stable, widely adopted)
2. **User upgrades**: Ask user to update VS Code (not ideal)
3. **Downgrade types**: Match types to realistic VS Code version

### Recommended Action
Downgrade engines.vscode to ^1.95.0 and package again. This is stable and widely deployed.

---

## UB-005: [Template for next issue]
**Date**:
**Severity**:
**Status**:

### Issue
[Description]

### Evidence
[What was observed]

### Impact
[Effect on users/functionality]

### Root Cause
[Why it happened]

### Resolution Options
[Possible fixes]

### Recommended Action
[Chosen approach]

---
