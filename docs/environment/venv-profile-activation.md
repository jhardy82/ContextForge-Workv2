# Python Virtual Environment Auto-Activation (Profile Best Practice)

This repository now relies **only on the stock** `./.venv/Scripts/Activate.ps1` script provided by Python together with the reusable
initializer `scripts/Init-VenvAndLogger.ps1` that seeds logging env vars and (optionally) emits a banner. The prior custom shim
`scripts/AutoActivate-Venv.ps1` has been removed to eliminate duplication and drift.

## Why remove the custom script?

- Avoids re‑implementing activation logic (path munging, prompt, variables) that Python already maintains.
- Prevents filename / convention divergence (`venv_auto.jsonl` vs `venv_activate.jsonl`).
- Reduces maintenance surface and potential parsing issues encountered in the shim.
- Aligns with instruction mandate: reuse authoritative artifacts; keep startup fast.

## Recommended VS Code Terminal Profile (Preferred)

The workspace `settings.json` defines a PowerShell profile that invokes:

```powershell
& "$([IO.Path]::Combine($PWD.Path,'scripts','Init-VenvAndLogger.ps1'))" -EmitBanner
```

It performs:
1. Unified logger env var seeding (if unset)
2. Upward search + activation of nearest `.venv`
3. Optional colored banner

## Alternate PowerShell Profile Snippet (Fallback)

Add the following to your PowerShell 7 profile (e.g. `$PROFILE.CurrentUserAllHosts` or just `$PROFILE`) one time:

```powershell
# Auto-activate repository .venv when in (or below) repo root
function Invoke-RepoVenvActivation {
    param(
        [string]$Marker = 'pyproject.toml'
    )
    if ($env:CF_VENV_ACTIVE) { return }
    $start = Get-Location
    $dir = $start
    while ($dir -and -not (Test-Path (Join-Path $dir $Marker))) {
        $parent = Split-Path -Parent $dir
        if ($parent -and $parent -ne $dir) { $dir = $parent } else { $dir = $null }
    }
    if (-not $dir) { return }
    $activate = Join-Path $dir '.venv/Scripts/Activate.ps1'
    if (-not (Test-Path $activate)) { return }
    try { . $activate } catch { Write-Verbose "[venv-profile] activation failed: $($_.Exception.Message)" }
    if ($env:VIRTUAL_ENV -like '*\.venv*') { $env:CF_VENV_ACTIVE = '1' }
}
Invoke-RepoVenvActivation
```

### Behavior
1. Walks upward from the current directory until it finds a `pyproject.toml` (repository root heuristic).
2. If `.venv/` and its `Scripts/Activate.ps1` exist, it dot‑sources the stock activation script.
3. Sets `CF_VENV_ACTIVE` sentinel once; subsequent shells skip additional work.

### Why not log here?
Activation is a high‑frequency, low‑risk operation. Structured logging remains available via `scripts/Ensure-VenvEnforced.ps1` which
performs full verification, dependency checks, and emits rich events (`py_env_activate_start`, `py_env_activate_end`, etc.). Use that
script for governance runs or CI environment preparation; keep profile activation lightweight.

### Verification
After opening a new terminal inside the repo:

```powershell
echo $env:VIRTUAL_ENV
echo $env:CF_VENV_ACTIVE
python --version
```

Expect `VIRTUAL_ENV` to point into the repo `.venv` and `CF_VENV_ACTIVE=1`.

## CI / On-Demand Enforcement

For CI or when you explicitly need validation + dependency assurance, call:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Ensure-VenvEnforced.ps1
```

That script will (re)create the environment (if missing), install baseline dev dependencies, emit structured JSONL events to `logs/venv/venv_activate.jsonl`, and produce an environment manifest under `build/artifacts/env/`.

## Removal Notes

Removed:
- `scripts/AutoActivate-Venv.ps1` (superseded by `Init-VenvAndLogger.ps1`)
- `tests/unit/Venv.AutoActivate.Tests.ps1` (placeholder test retired after consolidation)

Any existing references in local profiles to `AutoActivate-Venv.ps1` can be replaced with the snippet above. No other repository code was dependent on the deleted file.

## Future Enhancements (Optional)

- Add a lightweight warning if activation fails but `.venv` exists (guarded by a once‑per‑session flag).
- Provide a `scripts/Write-VenvProfileSnippet.ps1` helper that emits / installs the snippet automatically (only if missing).

---

Last updated: 2025-09-19 (post‑consolidation to Init-VenvAndLogger.ps1)
Maintainer: Automation (Profile Activation Simplification)
