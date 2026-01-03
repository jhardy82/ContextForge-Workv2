<!-- markdownlint-disable-file -->

# Pytest-Rich Usage (Direct Invocation)

To run pytest with Rich UI directly (outside the harness), use deterministic settings:

1. Disable plugin autoload
2. Explicitly load pytest_rich.plugin
3. Clear inherited addopts
4. Enable Rich UI with color and verbosity

Example (PowerShell):

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
& .\.venv\Scripts\python.exe -m pytest -p pytest_rich.plugin -o addopts= --rich -vv --color=yes tests\python
```

Notes:

- Prefer the harness (`python/run_rich_harness.py`) when you also need live event monitoring and dashboard artifacts.
- Keep `--color=yes` in CI for readable logs.
