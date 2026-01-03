# TaskMan-v2 v1.0.2 Quick Start Guide

## Installation Verification

✅ **Extension Installed**: `contextforge.taskman-v2-extension@1.0.2`

## What's New in v1.0.2

### Fixed
- ✅ **TypeScript Compilation** (UB-002 RESOLVED)
  - Was: 62 compilation errors
  - Now: 0 errors - fully buildable from source

- ✅ **API Port Configuration** (CRITICAL)
  - Was: Extension defaulted to port 3000
  - Now: Correctly defaults to port 3001 with `/api/v1` path
  - Files updated: 3 (databaseService.ts, settingsManager.ts, sharedConfigBridge.ts)
  - Total changes: 10 occurrences

### Added
- ✅ **Action Lists Integration**
  - Full TreeView provider for action lists
  - 9 status types supported (planned, new, pending, active, in_progress, blocked, completed, archived, cancelled)
  - Item toggle functionality
  - Status grouping with icons and colors
  - Models match PostgreSQL schema exactly (20 columns)

- ✅ **E2E Testing Framework**
  - 3 test suites (activation, CRUD, settings)
  - Run with: `npm run test:e2e`

- ✅ **MCP Integration** (4 servers configured)
  - Sequential Thinking (complex problem-solving)
  - Firebase (Firestore integration)
  - GitHub Copilot (AI assistance)
  - Vibe Check (validation)

### Tested
- ✅ **Backend API Validation** (100% pass rate)
  - Health endpoint: Working
  - Action lists endpoint: Working
  - 5 backend smoke tests: All passed
  - Test duration: 9.08s

## Quick Commands

### Extension Development
```bash
# Navigate to extension directory
cd TaskMan-v2/vscode-extension

# Install dependencies (IMPORTANT: use --include=dev)
npm install --include=dev

# Compile TypeScript
npm run compile

# Run E2E tests
npm run test:e2e

# Package extension
npm run package
```

### Extension Usage in VS Code
1. Open Activity Bar (left sidebar)
2. Look for TaskMan-v2 icon
3. Click to view tasks
4. Use commands: `Ctrl+Shift+P` → type "TaskMan"

## Backend Requirements

**Backend must be running on port 3001** (not 3000)

```bash
# Check backend health
curl http://localhost:3001/health

# Expected response:
# {"status":"healthy","version":"1.0.0","database":"connected"}
```

## Configuration Defaults (Fixed in v1.0.2)

- ✅ DTM Server Port: **3001** (was 3000 in v1.0.0)
- ✅ API URL: `http://localhost:3001/api/v1` (updated path)
- ✅ Database Mode: API (default)
- ✅ Auto-sync: Enabled

**Note**: All default API URLs updated to use port 3001 and `/api/v1` path to match TaskMan-v2 backend API.

## Testing

### Run E2E Tests
```bash
cd TaskMan-v2/vscode-extension
npm run test:e2e
```

### Automated Testing Results (2025-11-14)
✅ **All automated tests passed (100% success rate)**

| Test | Status | Evidence |
|------|--------|----------|
| TypeScript compilation | ✅ PASS | 0 errors |
| API health endpoint | ✅ PASS | Status: healthy, DB: connected |
| Action lists endpoint | ✅ PASS | 5 lists returned with items |
| Backend smoke tests | ✅ PASS | 5/5 passed in 9.08s |
| Extension packaging | ✅ PASS | 305.38 KB, 103 files |

**Test Report**: [TEST-REPORT-ACTION-LISTS-20251114.md](TEST-REPORT-ACTION-LISTS-20251114.md)

### Manual Testing Checklist (Pending)
- [ ] Extension appears in Activity Bar
- [ ] TreeView loads tasks
- [ ] **Action Lists TreeView displays** (NEW)
- [ ] **Action lists grouped by status** (NEW)
- [ ] **Can toggle action list items** (NEW)
- [ ] Can create new task
- [ ] Can toggle task completion
- [ ] Settings command works
- [ ] Backend sync works (port 3001)

## MCP Usage

### Access MCPs in Claude Code

**Sequential Thinking**:
```
Use sequential thinking to plan [complex task]
```

**Firebase** (requires `firebase login` first):
```
Query Firebase for [data]
```

**GitHub Copilot**:
```
Use GitHub Copilot to review [code]
```

## Troubleshooting

### Extension Not Loading
1. Check VS Code version (must be 1.95.0+)
2. Restart VS Code
3. Check Output panel: "TaskMan-v2"

### Backend Not Connecting
1. Verify backend on port 3001: `curl http://localhost:3001/health`
2. Check extension settings: `taskman.dtm.serverPort` should be 3001
3. Test connection: Command Palette → "TaskMan: Test Connection"

### Compilation Errors
```bash
# If npm install fails, use:
npm install --include=dev

# Then compile:
npm run compile
```

### MCPs Not Working
1. Check `.claude/mcp.json` exists
2. Restart Claude Code
3. See: [MCP-AGENT-USAGE-GUIDE.md](../../MCP-AGENT-USAGE-GUIDE.md)

## Documentation

- **Full Deployment Guide**: [DEPLOYMENT-READY-v1.0.2.md](DEPLOYMENT-READY-v1.0.2.md)
- **Action Lists Test Report**: [TEST-REPORT-ACTION-LISTS-20251114.md](TEST-REPORT-ACTION-LISTS-20251114.md) 🆕
- **MCP Usage Guide**: [MCP-AGENT-USAGE-GUIDE.md](../../MCP-AGENT-USAGE-GUIDE.md)
- **Test Summary (E2E)**: [TEST-SUMMARY-20251113.md](TEST-SUMMARY-20251113.md)
- **Issues Catalog**: [UNEXPECTED-BEHAVIORS.md](UNEXPECTED-BEHAVIORS.md)
- **v1.0.2 MCP Session**: [.QSE/v2/Sessions/2025-11-13/SESSION-SUMMARY-TASKMAN-V102-MCP-20251113.md](../../.QSE/v2/Sessions/2025-11-13/SESSION-SUMMARY-TASKMAN-V102-MCP-20251113.md)
- **Action Lists Testing Session**: [.QSE/v2/Sessions/2025-11-14/SESSION-SUMMARY-ACTION-LISTS-TESTING-20251114.md](../../.QSE/v2/Sessions/2025-11-14/SESSION-SUMMARY-ACTION-LISTS-TESTING-20251114.md) 🆕

## Next Steps

1. **Immediate**: Manual VSCode UI testing
   - Install extension v1.0.2
   - Verify action lists TreeView
   - Test item toggle functionality
   - Complete manual checklist above

2. **This Week**: Production validation
   - User acceptance testing
   - Performance monitoring
   - Error handling verification

3. **v1.0.3 Sprint**: Improvements
   - Add .vscodeignore (reduce VSIX size)
   - Expand E2E test coverage
   - Improve error messaging

4. **v1.1 Sprint**: Features
   - In-extension item creation
   - Bulk operations
   - Search and filter UI

## Support

- Issues Catalog: `UNEXPECTED-BEHAVIORS.md`
- Agent Documentation: `AGENTS.md`
- Extension Logs: VS Code Output → "TaskMan-v2"

---

**Status**: 🟢 **READY FOR MANUAL TESTING**

*Version: 1.0.2*
*Last Updated: 2025-11-14*
*Automated Tests: 100% PASS (9/9)*
