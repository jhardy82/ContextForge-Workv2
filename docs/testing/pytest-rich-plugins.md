## Rich-formatted pytest output (pytest-rich baseline)

We standardize on pytest-rich for Rich-formatted pytest output. pytest-richer is considered deprecated/legacy and is not installed by default.

- Installed by default: pytest-rich
- Deprecated/blocked: pytest-richer

### Installation

No action required for pytest-rich; it is part of the project dependencies.

Deprecated: pytest-richer is not supported and is blocked in this repository to avoid option conflicts and UX divergence.

### Usage

- Default runs use pytest-rich. Root `pytest.ini` includes `-p no:pytest_richer -p no:richer` to avoid conflicts.
- To be explicit, pass `-p pytest_rich.plugin` when invoking pytest directly, or use the harness.

PowerShell examples:

```powershell
# Preferred: deterministic harness (disables autoload and enables pytest_rich.plugin)
& .\.venv\Scripts\python.exe .\python\run_rich_harness.py --paths .\tests\python --pattern 'test_*.py'

# Direct pytest with pytest-rich explicitly enabled
& .\.venv\Scripts\python.exe -m pytest -p pytest_rich.plugin -vv --color=yes
```

Notes:

- Loading both pytest-rich and pytest-richer simultaneously can cause option registration conflicts (e.g., shared `--rich` flag). Our configuration blocks pytest-richer by default to prevent this.
- If your local environment autoloads plugins, set `$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'` and pass explicit `-p` flags.

### Deprecated plugin (blocked): pytest-richer

pytest-richer is not part of this environment and must not be used. The repository explicitly blocks it via `pytest.ini` to avoid conflicts. Do not install or enable it.

### Harness usage

We provide a deterministic runner that disables plugin autoload and explicitly enables pytest-rich while clearing inherited `addopts`. It also discovers a `*.events.jsonl` file and shows Rich progress.

PowerShell example:

```powershell
& .\.venv\Scripts\python.exe .\python\run_rich_harness.py --paths .\tests\python --pattern 'test_plugin_validation*.py'
```

### Files relevant to this integration

- `pytest.ini`: includes `-p no:pytest_richer -p no:richer` in `addopts` to avoid conflicts.
- `pyproject.toml`: includes `pytest-rich` only (pytest-richer is not listed).
- `python/run_rich_harness.py`: forces rich-only deterministic runs for progress UX.
- `tests/python/test_plugin_validation.py`: minimal sample test to validate plugin output.

### CI/CD

Defaults require no changes. To be explicit in CI, prefer pytest-rich and/or use the harness.

```powershell
# Explicit rich
& .\.venv\Scripts\python.exe -m pytest -p pytest_rich.plugin -vv --color=yes
```

pytest-richer is not supported and is blocked in CI and local runs.

### Banner semantics

When tests start, stderr includes a diagnostic line like:

```text
[rich] active=true rich=true richer=false driver=plugin
```

- `active` refers to the progress UI being enabled
- `rich` indicates the pytest-rich plugin is loaded
- `richer` indicates the legacy pytest-richer plugin (should remain false)
- `driver` shows whether progress comes from the unified plugin (`plugin`) or local fallback (`local`)

### Banner panels toggle (CF_RICH_BANNER)

We provide optional Rich-styled panels at both session start and finish. These are controlled by the environment variable `CF_RICH_BANNER` and always respect the `--no-rich` flag:

- When `CF_RICH_BANNER` is enabled (default), and `--no-rich` is not set, the test run prints Rich-styled panels at the start and end of the session for readability.
- When `CF_RICH_BANNER` is disabled or `--no-rich` is set, the panels are suppressed and the suite falls back to concise plain-text lines.

Panels are emitted from:

- `tests/python/conftest.py` (general test suite)
- `tests/conftest.py` (gamification suite)

This preserves deterministic pytest-rich activation while offering a clean, readable summary in terminals that support Rich.
