## Python Virtual Environment Auto-Activation (Consolidated Guidance)

Authoritative activation script: `.venv/Scripts/Activate.ps1` (stock venv output).

As of 2025-09-19 the repository removed the legacy helper `AutoActivate-Venv.ps1` and standardised on:

* `scripts/Init-VenvAndLogger.ps1` – lightweight initializer (env var seeding, upward search, optional banner)
* `scripts/Ensure-VenvEnforced.ps1` – heavier enforcement (creation, deps, manifest, logging events)

All activation paths MUST delegate to the stock Activate script (never re‑implement its logic).

### When to Use Which
| Scenario | Use | Rationale |
|----------|-----|-----------|
| Interactive VS Code terminal | `Init-VenvAndLogger.ps1` via profile | Fast, minimal, banner optional |
| CI bootstrap / governance run | `Ensure-VenvEnforced.ps1` | Creates / repairs venv, emits evidence |
| Manual local repair | `Ensure-VenvEnforced.ps1 -ForceRecreate` | Fresh baseline & manifest |

### Auto-Activation Conditions
Activation only triggers if a `.venv` folder (with `Scripts/Activate.ps1`) is found by upward search. This avoids accidental cross-repo interference.

### Example VS Code Profile Snippet
Already encoded in workspace `settings.json` (calls initializer with `-EmitBanner`). If adding to a user profile:

```powershell
& "$PWD/scripts/Init-VenvAndLogger.ps1" -EmitBanner
```

### CI Pattern
```powershell
pwsh -NoLogo -NoProfile -File scripts/Ensure-VenvEnforced.ps1
```

### Expected Logging (Enforced Path)
`py_env_activate_start`, `py_env_dependency_install` (when needed), `py_env_activate_end`, `py_env_manifest_emit`.

### Troubleshooting (Quick)
| Symptom | Check | Fix |
|---------|-------|-----|
| No activation banner | Profile not using initializer | Update terminal profile or add snippet |
| Wrong interpreter | `$env:VIRTUAL_ENV` blank | Run enforcement script, confirm `.venv` exists |
| Missing deps | Imports fail in activated shell | Run enforcement script to install baseline |

### Deprecations
Removed: `scripts/AutoActivate-Venv.ps1` (replaced), any docs pointing to it should be updated to reference this file and `docs/venv-profile-activation.md`.

---
Last updated: 2025-09-19 (post-consolidation)
