# Pytest Plugin Conflict Analysis

**Date**: 2025-11-29  
**Purpose**: Identify specific plugin conflicts and determine compatibility for structured test output

---

## 🎯 Your Requirements

1. **Structured summaries** → ✅ `pytest-json-report` provides machine-readable JSON
2. **Dashboards** → ✅ `pytest-html` generates HTML reports  
3. **Informative progress bars** → ✅ `pytest-progress` shows `██████████`
4. **Unique JSON files** → ✅ Configurable via `--json-report-file=<name>.json`
5. **Digital intelligence readability** → ✅ JSON output is fully structured

---

## 🔴 CONFLICT ANALYSIS: Why Some Plugins Cannot Work Together

### Root Cause: `sys.stdout` Capture Conflicts

All pytest plugins that modify terminal output must interact with pytest's capture system. The issue is **HOW** they interact:

```
pytest's Capture System
        ↓
┌───────────────────────────────────────────────────────────┐
│  sys.stdout  ←──────── All plugins write here            │
│  sys.stderr  ←──────── Error output                      │
└───────────────────────────────────────────────────────────┘
        ↑                    ↑                    ↑
   pytest-rich          pytest-richer       pytest-sugar
   (takes full          (takes full         (takes full
    control)             control)            control)
```

### Specific Conflicts Identified

| Plugin | Conflict Type | Why It Fails |
|--------|---------------|--------------|
| **pytest-rich** | Stdout takeover | Uses Rich's `Console` which replaces `sys.stdout` entirely. When pytest's capture system tries to restore stdout after test, the file handle is closed → `ValueError: I/O operation on closed file` |
| **pytest-richer** | Stdout takeover | Same mechanism as pytest-rich |
| **pytest-sugar** | Reporter replacement | Completely replaces pytest's default reporter with custom progress bars. Conflicts with any plugin that expects standard terminal output |
| **pytest-instafail** | Output buffering | Modifies when test output is flushed, breaking assumptions of other plugins about when stdout is available |
| **pytest-randomly** | Test ordering | Reorders tests which can break state-dependent tests (not a stdout conflict but causes failures) |

### The Critical Technical Issue

```python
# What pytest-rich/richer do:
console = Console(file=sys.stdout)  # Takes over stdout
# ... runs tests ...
# pytest's teardown tries to use original stdout
print("results")  # ❌ ERROR: stdout file handle is closed!
```

---

## ✅ COMPATIBLE PLUGIN COMBINATIONS

### Best Configuration for Your Requirements

| Plugin | Purpose | Compatible? | Notes |
|--------|---------|-------------|-------|
| `pytest-progress` | Visual progress bar `██████████` | ✅ YES | Non-invasive, works with standard reporter |
| `pytest-json-report` | Machine-readable JSON | ✅ YES | Critical for AI/digital intelligence |
| `pytest-html` | Human-readable HTML reports | ✅ YES | Dashboard-style output |
| `pytest-metadata` | Environment metadata | ✅ YES | Required by json-report and html |
| `pytest-cov` | Code coverage | ✅ YES | Generates coverage.json |
| `pytest-xdist` | Parallel execution | ✅ YES | Use `-n auto` for speed |
| `pytest-benchmark` | Performance benchmarks | ✅ YES | Generates benchmark.json |

### Plugins That MUST Be Disabled

| Plugin | Why Disable |
|--------|-------------|
| `pytest-sugar` | Conflicts with progress bars, replaces reporter |
| `pytest-rich` | Takes over stdout, causes `ValueError` on close |
| `pytest-richer` | Same as pytest-rich |
| `pytest-instafail` | Breaks output buffering assumptions |
| `pytest-anyio` | Not needed unless using async tests, adds overhead |
| `pytest-randomly` | Can cause state-dependent test failures |

---

## 🔧 RECOMMENDED CONFIGURATION

### pyproject.toml

```toml
[tool.pytest.ini_options]
# === DISABLE CONFLICTING PLUGINS ===
addopts = """
    -p no:sugar
    -p no:rich
    -p no:richer
    -p no:instafail
    -p no:anyio
    -p no:randomly
    --json-report
    --json-report-file=artifacts/test/results.json
    --html=artifacts/test/report.html
    --self-contained-html
    --show-progress
    --tb=short
"""

# Progress bar configuration (works without conflicts)
progress_position = 0
progress_style = "auto"
progress_unicode = true
```

### Unique File Naming Pattern

For generating uniquely named JSON files:

```bash
# PowerShell example with timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
pytest tests/ --json-report-file="artifacts/test/results_$timestamp.json"

# Or use pytest-json-report's summary naming
pytest tests/ --json-report-summary --json-report-file="artifacts/test/summary.json"
```

---

## 📊 OUTPUT FORMATS ACHIEVED

### 1. Terminal Progress (Human-Friendly)
```
tests/test_example.py ████████████████████████████████████ 100%
================================ 34 passed in 4.10s ================================
```

### 2. JSON Report (Machine-Readable)
```json
{
  "created": 1764446175.39864,
  "duration": 4.09181547164917,
  "summary": {
    "passed": 33,
    "failed": 1,
    "total": 34,
    "collected": 34
  },
  "tests": [
    {
      "nodeid": "tests/test_example.py::test_function",
      "outcome": "passed",
      "duration": 0.001,
      "setup": {...},
      "call": {...},
      "teardown": {...}
    }
  ],
  "collectors": [...],
  "environment": {...}
}
```

### 3. HTML Dashboard Report
- Visual test results with pass/fail highlighting
- Filter and search capabilities
- Environment details
- Collapsible test details

---

## ⚠️ CANNOT ALL WORK TOGETHER

### Definitive Answer: No, These Specific Plugins Cannot Coexist

The following plugins are **fundamentally incompatible** due to their architecture:

```
pytest-rich  ─┬─→ Takes exclusive control of sys.stdout
pytest-richer ┘   Cannot share with standard pytest capture

pytest-sugar ───→ Replaces pytest's terminal reporter entirely
                  Cannot coexist with pytest-progress or others

pytest-instafail → Modifies output timing assumptions
                   Breaks synchronization with other plugins
```

### Why They Conflict at a Code Level

1. **pytest-rich** creates a `rich.Console(file=sys.stdout)` which:
   - Wraps stdout in a Rich Console object
   - Uses ANSI escape codes for formatting
   - Closes the file handle on shutdown → pytest teardown fails

2. **pytest-sugar** uses `terminal.write()` hooks that:
   - Override `pytest_collection_modifyitems`
   - Replace `pytest_runtest_logreport`
   - Prevent other plugins from writing to terminal

---

## 🐛 KNOWN WINDOWS ISSUE: tmp_path PermissionError

### Symptom
After tests complete, you may see:
```
Exception ignored in atexit callback: <function cleanup_numbered_dir at 0x...>
PermissionError: [WinError 5] Access is denied: '...\pytest-current'
```

### Root Cause
- pytest creates a `pytest-current` symlink in the temp directory
- On Windows, cleaning up symlinks during atexit can fail due to permission issues
- This is a known pytest issue on Windows (not a plugin conflict)

### Impact
- **Non-blocking**: Tests run and complete successfully
- **Noisy**: Error message appears after test output
- **Harmless**: No data loss or test corruption

### Status
- Added `tmp_path_retention_policy = "none"` to pyproject.toml (mitigates but doesn't fully resolve)
- This is tracked in pytest GitHub issues - waiting for upstream fix

---

## ✅ FINAL RECOMMENDATION

### Use This Exact Command for All Your Requirements:

```bash
pytest tests/ \
    -p no:sugar \
    -p no:rich \
    -p no:richer \
    -p no:instafail \
    -p no:anyio \
    -p no:randomly \
    --json-report \
    --json-report-file="artifacts/test/results_$(Get-Date -Format 'yyyyMMdd_HHmmss').json" \
    --html="artifacts/test/report_$(Get-Date -Format 'yyyyMMdd_HHmmss').html" \
    --self-contained-html \
    --show-progress \
    --cov=src \
    --cov-report=json:artifacts/coverage/coverage.json \
    -v \
    --tb=short
```

### This Achieves:
| Requirement | Fulfilled By |
|-------------|--------------|
| Structured summaries | `--json-report` → JSON file with full test data |
| Dashboards | `--html` → Interactive HTML report |
| Progress bars | `--show-progress` → Terminal progress bar |
| Unique filenames | Timestamp in filename |
| AI-readable | JSON output is machine-parseable |
| Code coverage | `--cov-report=json` → Coverage data |

---

## 📝 Summary Table

| Plugin | Status | Reason |
|--------|--------|--------|
| pytest-json-report | ✅ KEEP | Machine-readable output |
| pytest-html | ✅ KEEP | Dashboard reports |
| pytest-progress | ✅ KEEP | Visual progress bars |
| pytest-cov | ✅ KEEP | Coverage JSON |
| pytest-metadata | ✅ KEEP | Required by others |
| pytest-xdist | ✅ KEEP | Parallel execution |
| pytest-sugar | ❌ DISABLE | Conflicts with reporter |
| pytest-rich | ❌ DISABLE | Stdout takeover |
| pytest-richer | ❌ DISABLE | Stdout takeover |
| pytest-instafail | ❌ DISABLE | Output timing issues |
| pytest-randomly | ❌ DISABLE | Test ordering issues |
| pytest-anyio | ❌ DISABLE | Unnecessary overhead |

---

*Document generated as part of pytest plugin compatibility analysis*
