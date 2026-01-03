# Pytest Monokai Enhanced Theme Guide

## Overview

This implementation provides a visually enhanced pytest experience using the **Monokai Enhanced** color theme with **detailed layout** formatting, combining all the functional settings from `pytest-rich.ini` with beautiful visual styling.

## Visual Features

The Monokai Enhanced theme provides:

- 🎨 **Purple/lavender borders** around information panels
- ✅ **Green checkmarks (✔)** for passing tests
- ❌ **Red X marks (✗)** for failing tests
- 💥 **Explosion emoji** for errors and exceptions
- 🔵 **Purple headers** with white text for sections
- 📊 **Detailed layout** with comprehensive session information
- 🎯 **Rich formatting** with styled progress bars and summaries

## Usage

### Basic Usage

```bash
# Run with Monokai Enhanced theme
python run_pytest_monokai_themed.py

# Run specific test file
python run_pytest_monokai_themed.py tests/python/test_dbcli_plugin.py

# Run with additional pytest arguments
python run_pytest_monokai_themed.py tests/ -v -x --tb=short
```

### Features Included

All features from `pytest-rich.ini` are preserved:

- ✅ **Rich console output** with styled formatting
- ✅ **Timeout settings** (60s default)
- ✅ **Test markers** for unit/integration/slow/skip categories
- ✅ **Coverage reporting** with XML and HTML output
- ✅ **Warnings filtering** for clean output
- ✅ **Plugin conflict resolution** (rerunfailures, randomly disabled)
- ✅ **Gamification elements** from CF-Gamification-Nudge02
- ✅ **Sacred Geometry staging** indicators
- ✅ **Detailed session information** in bordered panels

### Configuration Files

- `pytest-monokai-enhanced-working.ini` - Complete pytest configuration with all working settings
- `run_pytest_monokai_themed.py` - Themed runner script that applies visual styling

## Comparison

### With Monokai Enhanced Theme

- Purple/lavender styled borders and headers
- Enhanced visual contrast and readability
- Professional color scheme matching Monokai Enhanced editor theme
- Coordinated with development environment styling

### Standard pytest-rich

- Default terminal colors
- Basic Rich formatting without custom theme
- Standard green/red/yellow color scheme

## Technical Implementation

The theme works by:

1. **Theme Definition**: Uses Rich `Theme` object with Monokai Enhanced color palette
2. **Console Wrapper**: Creates themed `Console` instance for styled output
3. **Subprocess Execution**: Runs pytest with complete configuration while applying theme to wrapper output
4. **Configuration Preservation**: Uses `pytest-monokai-enhanced-working.ini` with all functional settings

## Color Palette

The Monokai Enhanced theme uses:
- **Primary**: Purple/magenta (#AE81FF)
- **Success**: Green (#A6E22E)
- **Error**: Red (#F92672)
- **Warning**: Orange (#FD971F)
- **Info**: Cyan (#66D9EF)
- **Borders**: Light purple/lavender
- **Text**: White/light gray on colored backgrounds## Integration

This implementation maintains full compatibility with:
- All existing pytest plugins
- Coverage reporting (pytest-cov)
- Test markers and filtering
- Timeout handling (pytest-timeout)
- Rich console integration (pytest-rich)
- CF-Gamification system
- Sacred Geometry test staging

## Example Output

```text
🎨 Running pytest with Monokai Enhanced Theme
Theme: Monokai Enhanced | Layout: Detailed
────────────────────────────────────────────────────────────

[GAME] Starting CF-Gamification-Nudge02 Test Suite
============================================================
RunId: CF-NUDGE02-TESTS-20250829-145439
Stage: Triangle Testing (Sacred Geometry Stage 2)
============================================================

┌─────────────────────────────────────────────────────────────────────┐
│ platform win32 pytest 8.4.2 python 3.12.9                        │
│ root C:\Users\james.e.hardy\Documents\PowerShell Projects        │
│ plugins [comprehensive plugin list with versions]                   │
│ configfile: pytest-monokai-enhanced-working.ini                    │
└─────────────────────────────────────────────────────────────────────┘

[100%] tests\python\test_dbcli_plugin.py ✔

┌─────── Summary ────────┐
│        1  Total tests  │
│        1  Passed (✔)   │
│    0.47s  Init phase   │
│    0.18s  Collection   │
│    0.54s  Execution    │
│    1.19s  Overall      │
└────────────────────────┘

✅ pytest execution completed successfully!
```

This provides a professional, visually consistent testing experience that matches modern development environments while preserving all functional testing capabilities.
