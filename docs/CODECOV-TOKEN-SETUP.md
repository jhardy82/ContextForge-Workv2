# Codecov Token Setup - Manual Steps Required

**Created**: 2025-12-31
**Implementation**: IMPL-2025-Q4-CODECOV-INTEGRATION
**Status**: ⚠️ **USER ACTION REQUIRED**

---

## Purpose

Enable Codecov integration in GitHub Actions workflows for automated coverage reporting. This document provides step-by-step instructions for adding the CODECOV_TOKEN secret to the repository.

---

## Prerequisites

- ✅ Codecov account with repository access
- ✅ GitHub repository admin access (jhardy82/SCCMScripts)
- ✅ codecov.yml configured (completed)
- ✅ Workflows updated with codecov-action@v4 (completed)

---

## Step 1: Get Codecov Upload Token

### Option A: From Codecov Dashboard

1. **Navigate to Codecov**:
   - URL: https://app.codecov.io/
   - Login with GitHub account

2. **Select Repository**:
   - Organization: `jhardy82`
   - Repository: `SCCMScripts`

3. **Get Upload Token**:
   - Go to: Settings → General
   - Copy the "Repository Upload Token" (starts with `CODECOV_TOKEN_`)

### Option B: Via Codecov CLI (Alternative)

```bash
# Install Codecov CLI
pip install codecov-cli

# Get token
codecov upload-token --repo=jhardy82/SCCMScripts
```

---

## Step 2: Add Token to GitHub Secrets

### Via GitHub Web UI (Recommended)

1. **Navigate to Repository Settings**:
   - URL: https://github.com/jhardy82/SCCMScripts/settings/secrets/actions

2. **Create New Secret**:
   - Click: "New repository secret"
   - Name: `CODECOV_TOKEN`
   - Value: [Paste token from Step 1]
   - Click: "Add secret"

3. **Verify Secret Created**:
   - Check that `CODECOV_TOKEN` appears in secrets list
   - Secret value should be hidden (dots)

### Via GitHub CLI (Alternative)

```bash
# Set token as secret
gh secret set CODECOV_TOKEN --body="YOUR_TOKEN_HERE" --repo=jhardy82/SCCMScripts

# Verify secret created
gh secret list --repo=jhardy82/SCCMScripts
```

---

## Step 3: Verify Integration

### Test Workflow Execution

1. **Trigger Quality Workflow**:
   ```bash
   # Option 1: Push changes to trigger
   git push

   # Option 2: Manual workflow dispatch
   gh workflow run quality.yml
   ```

2. **Check Workflow Run**:
   - Navigate to: https://github.com/jhardy82/SCCMScripts/actions
   - Select latest quality.yml run
   - Verify steps:
     - ✅ "Upload Python Coverage to Codecov" succeeds
     - ✅ "Upload PowerShell Coverage to Codecov" succeeds

3. **Check Codecov Dashboard**:
   - Navigate to: https://app.codecov.io/gh/jhardy82/SCCMScripts
   - Verify coverage reports uploaded
   - Check coverage percentages displayed

---

## Step 4: Validate Flag Configuration

### Verify Flags in Codecov Dashboard

1. **Navigate to Flags**:
   - URL: https://app.codecov.io/gh/jhardy82/SCCMScripts/flags

2. **Verify Expected Flags**:
   - ✅ `python` (existing)
   - ✅ `powershell` (existing)
   - ✅ `python-quality` (new from quality.yml)
   - ✅ `powershell-quality` (new from quality.yml)
   - ✅ `pr-fast-tests` (new from pytest-pr.yml)

3. **Check Flag Coverage**:
   - Each flag should show coverage percentage
   - Click flag to see detailed coverage report

---

## Troubleshooting

### Issue: Codecov Upload Fails with 401 Unauthorized

**Symptoms**:
```
Error: There was an error running the uploader: Error uploading to https://codecov.io: Error: There was an error fetching the storage URL during POST: 401 - Unauthorized
```

**Resolution**:
1. Verify CODECOV_TOKEN secret exists in repository
2. Check token hasn't expired in Codecov dashboard
3. Regenerate token if necessary and update GitHub secret

---

### Issue: Workflow Can't Access CODECOV_TOKEN

**Symptoms**:
```
Error: Codecov token not found. Please provide via with.token, or use other upload methods
```

**Resolution**:
1. Check secret name is exactly `CODECOV_TOKEN` (case-sensitive)
2. Verify workflow has `secrets: inherit` or accesses `${{ secrets.CODECOV_TOKEN }}`
3. Confirm repository settings allow workflows to access secrets

---

### Issue: Coverage Files Not Found

**Symptoms**:
```
Error: Unable to locate coverage files
```

**Resolution**:
1. Check coverage file paths match workflow configuration:
   - quality.yml: `build/artifacts/coverage/python/coverage.xml`, `build/artifacts/coverage/powershell/coverage.xml`
   - pytest-pr.yml: `coverage-pr.xml`
2. Verify pytest generates coverage files in expected locations
3. Add debug step to list files: `ls -R build/artifacts/coverage/`

---

## Workflow Configuration Summary

### quality.yml (2 Codecov uploads)

```yaml
- name: Upload Python Coverage to Codecov
  if: always()
  uses: codecov/codecov-action@v4
  with:
    files: build/artifacts/coverage/python/coverage.xml
    flags: python-quality
    name: Quality Gates - Python
    fail_ci_if_error: false

- name: Upload PowerShell Coverage to Codecov
  if: always()
  uses: codecov/codecov-action@v4
  with:
    files: build/artifacts/coverage/powershell/coverage.xml
    flags: powershell-quality
    name: Quality Gates - PowerShell
    fail_ci_if_error: false
```

### pytest-pr.yml (1 Codecov upload)

```yaml
- name: Upload PR Coverage to Codecov
  if: always()
  uses: codecov/codecov-action@v4
  with:
    files: coverage-pr.xml
    flags: pr-fast-tests
    name: PR Fast Tests
    fail_ci_if_error: false
```

---

## Flag Strategy

| Flag | Workflow | Path Coverage | Carryforward |
|------|----------|---------------|--------------|
| `python` | (existing) | python/, tests/python/ | Yes |
| `powershell` | (existing) | *.ps1, build/ | Yes |
| `python-quality` | quality.yml | python/, cf_core/ | Yes |
| `powershell-quality` | quality.yml | *.ps1, build/ | Yes |
| `pr-fast-tests` | pytest-pr.yml | python/, cf_core/, tests/ | No |

**Carryforward Strategy**:
- `Yes`: Preserve coverage when flag not uploaded (stable baseline)
- `No`: Always require fresh coverage (PR validation)

---

## Success Criteria

- ✅ CODECOV_TOKEN secret created in GitHub repository
- ✅ quality.yml uploads Python + PowerShell coverage successfully
- ✅ pytest-pr.yml uploads PR test coverage successfully
- ✅ Codecov dashboard shows 5 flags (2 existing + 3 new)
- ✅ Coverage percentages displayed for each flag
- ✅ No workflow failures due to Codecov integration

---

## Next Steps

1. **After Token Setup**:
   - Monitor first workflow run with Codecov integration
   - Verify coverage reports appear in Codecov dashboard
   - Check for any upload failures in workflow logs

2. **Optional Enhancements**:
   - Add Codecov badge to README.md
   - Configure Codecov GitHub App for PR comments
   - Set up coverage status checks in branch protection rules

---

## References

- **Codecov Documentation**: https://docs.codecov.com/docs
- **GitHub Secrets Guide**: https://docs.github.com/en/actions/security-guides/encrypted-secrets
- **codecov-action@v4**: https://github.com/codecov/codecov-action
- **codecov.yml Config**: https://docs.codecov.com/docs/codecov-yaml

---

**Status**: ⚠️ **AWAITING USER ACTION** - Add CODECOV_TOKEN to repository secrets
**Implementation**: IMPL-2025-Q4-CODECOV-INTEGRATION
**Evidence**: Changes committed in recovery/main-worktree-20241230 branch
