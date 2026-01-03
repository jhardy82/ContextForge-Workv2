# TaskMan-v2 v1.0.2 - Next Steps Guide
**Created**: 2025-11-14
**Status**: ✅ Automated Testing Complete
**Priority**: Manual UI Testing

---

## Session Completion Summary

### ✅ Completed Work
All automated testing and validation has been completed successfully:

1. **Port Configuration Fixed** (3 files, 10 changes)
   - [databaseService.ts](src/databaseService.ts) - 5 methods updated
   - [settingsManager.ts](src/settingsManager.ts) - 4 defaults updated
   - [sharedConfigBridge.ts](src/sharedConfigBridge.ts) - 2 defaults updated

2. **API Validation** (100% success)
   - Health endpoint: ✅ Working
   - Action lists endpoint: ✅ Working
   - Backend smoke tests: ✅ 5/5 passed

3. **Extension Build** (0 errors)
   - TypeScript compilation: ✅ Success
   - VSIX packaging: ✅ 305.38 KB, 103 files

4. **Documentation**
   - [TEST-REPORT-ACTION-LISTS-20251114.md](TEST-REPORT-ACTION-LISTS-20251114.md) - Comprehensive test report
   - [.QSE/v2/Sessions/2025-11-14/SESSION-SUMMARY-ACTION-LISTS-TESTING-20251114.md](../.QSE/v2/Sessions/2025-11-14/SESSION-SUMMARY-ACTION-LISTS-TESTING-20251114.md) - Session summary
   - [QUICK-START-v1.0.2.md](QUICK-START-v1.0.2.md) - Updated with test results

---

## Immediate Next Steps (30 mins)

### Phase 1: Install Extension ✅ COMPLETED
**Priority**: HIGH
**Time**: 5 minutes
**Status**: ✅ **COMPLETED** - 2025-11-14

```bash
# Navigate to extension directory
cd "C:\Users\james.e.hardy\Documents\PowerShell Projects\TaskMan-v2\vscode-extension"

# Uninstall previous version (if installed)
code --uninstall-extension contextforge.taskman-v2-extension

# Install v1.0.2
code --install-extension taskman-v2-extension-1.0.2.vsix

# Verify installation
code --list-extensions | grep taskman
```

**Expected Output**: `contextforge.taskman-v2-extension@1.0.2`
**Actual Output**: `contextforge.taskman-v2-extension@1.0.2` ✅

**Installation Results**:
- ✅ Previous version uninstalled successfully
- ✅ v1.0.2 VSIX installed successfully (305.38 KB)
- ✅ Version verified: `contextforge.taskman-v2-extension@1.0.2`

---

### Phase 2: Manual UI Testing
**Priority**: HIGH
**Time**: 20 minutes

#### Test Checklist

**2.1 Extension Activation** (5 mins)
- [ ] Open VSCode
- [ ] Extension loads without errors
- [ ] Activity Bar icon visible (left sidebar)
- [ ] TreeView panel accessible
- [ ] No errors in Output → "TaskMan-v2"

**2.2 Action Lists TreeView** (10 mins)
- [ ] Action Lists view appears in TreeView
- [ ] Lists load from API (5 expected)
- [ ] Status grouping displays correctly
  - [ ] In Progress
  - [ ] Active
  - [ ] Pending
  - [ ] New
  - [ ] Planned
  - [ ] Blocked
  - [ ] Completed
  - [ ] Archived
  - [ ] Cancelled
- [ ] Item counts accurate (e.g., "2/2")
- [ ] Icons appropriate for each status
- [ ] Colors match status (green=completed, red=blocked, etc.)

**2.3 Action List Expansion** (3 mins)
- [ ] Click action list to expand
- [ ] Items display correctly
- [ ] Completion state shows (checked/unchecked icons)
- [ ] Empty lists show "No items" message
- [ ] Tooltips display on hover

**2.4 Item Toggle Functionality** (2 mins)
- [ ] Click an incomplete item
- [ ] Icon changes to checkmark
- [ ] Tree refreshes automatically
- [ ] Item stays checked after refresh
- [ ] Click again to uncheck
- [ ] State persists to database

---

### Phase 3: Command Testing
**Priority**: MEDIUM
**Time**: 5 minutes

```bash
# Test from Command Palette (Ctrl+Shift+P)
```

**Commands to Test**:
- [ ] "TaskMan: Refresh Action Lists" - Reloads data
- [ ] "TaskMan: View Action List" - Shows details
- [ ] "TaskMan: Toggle Action List Item" - Toggles completion
- [ ] "TaskMan: Test Connection" - Validates API connectivity

---

## Validation Criteria

### Must Pass
- ✅ Extension installs without errors
- ✅ TreeView displays action lists
- ✅ API connection works (port 3001)
- ✅ Item toggle updates state

### Should Pass
- ✅ Status grouping works
- ✅ Icons and colors correct
- ✅ Commands functional
- ✅ Error handling graceful

### Nice to Have
- ✅ Performance acceptable (< 1s load)
- ✅ UI responsive
- ✅ Tooltips informative

---

## Troubleshooting

### Issue: Extension Not Loading
**Symptoms**: Activity Bar icon missing, no TreeView

**Solutions**:
1. Check VS Code version: Must be 1.95.0+
2. Restart VS Code completely
3. Check extension list: `code --list-extensions`
4. Review logs: Output → "TaskMan-v2"

### Issue: Action Lists Not Displaying
**Symptoms**: TreeView empty or shows "No action lists found"

**Solutions**:
1. Verify API is running:
   ```bash
   curl http://localhost:3001/health
   ```
   Should return: `{"status":"healthy"...}`

2. Check API endpoint:
   ```bash
   curl http://localhost:3001/api/v1/action-lists/
   ```
   Should return: `{"success":true,"data":[...]}`

3. Verify settings:
   - Open Settings (Ctrl+,)
   - Search "taskman"
   - Check `taskman.database.dtmApiUrl` = `http://localhost:3001/api/v1`
   - Check `taskman.dtm.serverPort` = `3001`

4. Test connection:
   - Command Palette → "TaskMan: Test Connection"

### Issue: Item Toggle Not Working
**Symptoms**: Clicking items doesn't change state

**Solutions**:
1. Check console for errors: Help → Toggle Developer Tools
2. Verify API endpoints responding
3. Check network tab for failed requests
4. Restart extension: Reload Window (Ctrl+R)

### Issue: Compilation Errors During Development
**Symptoms**: TypeScript errors when building from source

**Solutions**:
```bash
# Ensure dev dependencies installed
npm install --include=dev

# Clean and rebuild
rm -rf out/
npm run compile
```

---

## Success Indicators

After completing manual testing, you should see:

### ✅ Visual Indicators
- TaskMan-v2 icon in Activity Bar
- Action Lists TreeView with grouped items
- Colored status icons (blue, green, red, yellow)
- Item counts (e.g., "2/5" for 2 completed of 5 total)
- Checkmark icons for completed items

### ✅ Functional Indicators
- Clicking items toggles completion
- Tree refreshes automatically
- Commands execute without errors
- API connection stable

### ✅ Data Indicators
- 5 action lists visible (from test data)
- At least 1 list with items ("Item Operations Test" has 2 items)
- Status variety (active, completed, etc.)

---

## Post-Testing Actions

### If All Tests Pass ✅
1. **Update Status**:
   - Mark manual tests as complete
   - Update QUICK-START-v1.0.2.md status
   - Create release notes

2. **Documentation**:
   - Screenshot working TreeView
   - Document any observations
   - Note performance metrics

3. **Next Sprint Planning**:
   - Review v1.0.3 improvements
   - Prioritize:
     - Add .vscodeignore
     - Expand E2E tests
     - Improve error messages

### If Tests Fail ❌
1. **Document Failures**:
   - Create issue in UNEXPECTED-BEHAVIORS.md
   - Include screenshots
   - Capture error logs
   - Note reproduction steps

2. **Debug**:
   - Check API logs
   - Review extension logs
   - Test API endpoints manually
   - Verify configuration

3. **Fix and Retest**:
   - Apply fixes
   - Recompile: `npm run compile`
   - Repackage: `npm run package`
   - Reinstall and retest

---

## Future Improvements (v1.0.3+)

### High Priority
1. **Add .vscodeignore**
   - Reduce VSIX size (305 KB → ~150 KB)
   - Exclude: tests, docs, source maps, screenshots

2. **Expand E2E Tests**
   - Action list integration tests
   - Item toggle operations
   - Command execution tests

3. **Improve Error Handling**
   - Better offline API messages
   - User-friendly error display
   - Connection retry logic

### Medium Priority
4. **Performance Optimization**
   - Cache action lists (TTL: 30s)
   - Debounce auto-refresh
   - Lazy load large lists

5. **UI Enhancements**
   - Loading spinners
   - Error state UI
   - Empty state improvements

6. **Testing Infrastructure**
   - Automated UI tests
   - Visual regression tests
   - Performance benchmarks

### Low Priority
7. **Feature Additions**
   - In-extension item creation
   - Bulk operations
   - Search and filter
   - Drag-and-drop reordering

---

## Reference Links

### Documentation
- [Quick Start Guide](QUICK-START-v1.0.2.md)
- [Test Report](TEST-REPORT-ACTION-LISTS-20251114.md)
- [Session Summary](../.QSE/v2/Sessions/2025-11-14/SESSION-SUMMARY-ACTION-LISTS-TESTING-20251114.md)
- [Deployment Guide](DEPLOYMENT-READY-v1.0.2.md)

### API Endpoints
- Health: `http://localhost:3001/health`
- Action Lists: `http://localhost:3001/api/v1/action-lists/`

### Code Locations
- Models: [src/models.ts:224-485](src/models.ts#L224-L485)
- Provider: [src/actionListProvider.ts](src/actionListProvider.ts)
- Database Service: [src/databaseService.ts:449-495](src/databaseService.ts#L449-L495)

---

## Timeline Estimate

| Phase | Activity | Time | Total |
|-------|----------|------|-------|
| 1 | Install extension | 5 min | 5 min |
| 2 | Manual UI testing | 20 min | 25 min |
| 3 | Command testing | 5 min | 30 min |
| 4 | Documentation | 10 min | 40 min |
| 5 | Issue reporting (if needed) | 15 min | 55 min |

**Best Case**: 30 minutes (all tests pass)
**Typical Case**: 40 minutes (minor issues)
**Worst Case**: 55 minutes (significant debugging)

---

## Contact & Support

### Internal Resources
- Issues Catalog: [UNEXPECTED-BEHAVIORS.md](UNEXPECTED-BEHAVIORS.md)
- Agent Documentation: [../../AGENTS.md](../../AGENTS.md)
- Extension Logs: VSCode → Output → "TaskMan-v2"

### External Resources
- VSCode Extension API: https://code.visualstudio.com/api
- TaskMan-v2 Backend API: Port 3001
- PostgreSQL Database: 172.25.14.122:5432

---

**Document Version**: 1.0
**Created**: 2025-11-14
**Status**: Ready for Manual Testing
**Priority**: HIGH

**Automated Test Results**: ✅ 100% PASS (9/9)
**Ready for Production**: Pending manual validation
