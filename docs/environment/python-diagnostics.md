# Python Diagnostics Documentation

## pytest_diag.py - Direct Python Pytest Diagnostics

**Location**: `python/diagnostics/pytest_diag.py`

**Purpose**: Replace PowerShell-based pytest diagnostics with direct Python invocation, compliant with Direct Invocation Policy (no wrapper shells for standard Python test tooling).

### Features

- Ensures dev extras installed (pytest + plugins)
- Optional disable of auto plugin loading
- Optional suppression of parallelization (xdist)
- Runs focused test with verbose output
- Emits structured JSON summary (machine-parsable)
- Rich console integration for enhanced UX
- Unified logging integration for structured event capture

### Usage Examples

#### Basic focused test run

```bash
python python/diagnostics/pytest_diag.py
```

#### Custom test with options

```bash
python python/diagnostics/pytest_diag.py \
    --test tests/test_specific.py::test_function \
    --no-parallel \
    --no-plugins \
    --verbose
```

#### JSON output for CI/automation

```bash
python python/diagnostics/pytest_diag.py \
    --test tests/test_unified_logging.py::test_unified_logging \
    --json
```

#### Disable parallelization (useful for debugging)

```bash
python python/diagnostics/pytest_diag.py \
    --test tests/test_flaky.py::test_intermittent \
    --no-parallel \
    --verbose
```

### Configuration Override

The script automatically handles pytest configuration conflicts by:
- Using `--override-ini addopts=-q --maxfail=1` to bypass pyproject.toml parallelization
- Setting `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` when `--no-plugins` specified
- Clearing `PYTEST_ADDOPTS` environment variable when `--no-parallel` specified

### Integrated Toolchain

- **Rich Console**: Colored output with markup support (graceful fallback if not available)
- **Unified Logging**: Structured JSONL events logged to `logs/pytest_diag.jsonl`
- **Typer**: Not used here, but available for future CLI enhancements

### Exit Codes

- `0`: Success
- `1`: Generic failure (pytest execution failed)
- `2`: Dependency install failure

### Policy Compliance

- ✅ **Direct Invocation Policy**: Pure Python script, no PowerShell wrapper
- ✅ **HostPolicy: PythonHelper**: Appropriate for Python test tooling
- ✅ **Python-First Transition**: Replaces deprecated PowerShell diagnostics

### Migration Notes

- **Replaced**: `build/Run-PytestDiag.ps1` (removed per policy compliance)
- **Enhanced**: Added Rich console and unified logging integration
- **Improved**: Better configuration override handling for pytest conflicts

### Troubleshooting

1. **Missing dev dependencies**: Script auto-installs via `pip install -e .[dev]`
2. **Plugin conflicts**: Use `--no-plugins` to disable auto-loading
3. **Parallelization issues**: Use `--no-parallel` to force single-threaded execution
4. **Configuration conflicts**: Script automatically overrides problematic pyproject.toml settings

### Future Enhancements

- Integration with hypothesis for property testing
- mypy type checking in diagnostic mode
- Integration with pytest-benchmark for performance testing
- Custom plugin detection and recommendation
