# pytest-rich Custom Integration - Activation Instructions

## Overview
This custom pytest-rich integration provides the comprehensive rich reporting features you requested:
- ✅ Detailed layout with summary panel, split views for logs and stats
- ✅ Monokai theme for syntax highlighting and output
- ✅ Stack traces with rich formatting
- ✅ Configuration files in TOML format
- ✅ Runnable code samples
- ✅ Live progress reporting and HTML/text export

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages (already in requirements.txt):
- `pytest>=8.0.0`
- `rich>=13.0.0`
- `pytest-rich>=0.2.0` (basic plugin, we extend it)

### 2. File Structure
```
your-project/
├── conftest_rich_custom.py      # Custom Rich integration (main implementation)
├── pyproject_rich_custom.toml   # Configuration file
├── test_rich_sample.py          # Sample tests demonstrating features
├── requirements.txt             # Dependencies
└── tests/                       # Your actual test files
```

## Activation Methods

### Method 1: Replace conftest.py (Recommended)
1. Backup your existing `conftest.py`:
   ```bash
   mv conftest.py conftest_backup.py
   ```

2. Use the custom rich integration:
   ```bash
   mv conftest_rich_custom.py conftest.py
   ```

3. Update pyproject.toml with rich configuration:
   ```bash
   # Merge pyproject_rich_custom.toml content into your pyproject.toml
   ```

### Method 2: Import in Existing conftest.py
Add this to your existing `conftest.py`:
```python
# Import custom rich integration
from conftest_rich_custom import *
```

### Method 3: Use as Plugin
Run pytest with the custom file as a plugin:
```bash
pytest -p conftest_rich_custom test_rich_sample.py
```

## Running Tests

### Basic Rich Reporting
```bash
pytest test_rich_sample.py -v
```

### With Specific Test Selection
```bash
# Run only passing tests
pytest test_rich_sample.py -k "not intentional_failure" -v

# Run integration tests
pytest test_rich_sample.py -m integration -v

# Run with maximum verbosity
pytest test_rich_sample.py -vvv
```

### Advanced Options
```bash
# Generate coverage report with rich output
pytest test_rich_sample.py --cov=your_module -v

# Run with custom configuration
pytest -c pyproject_rich_custom.toml test_rich_sample.py -v

# Parallel execution (if pytest-xdist installed)
pytest test_rich_sample.py -n auto -v
```

## Configuration Options

### pyproject.toml Configuration
The `pyproject_rich_custom.toml` includes:

```toml
[tool.pytest-rich-custom]
theme = "monokai"                    # Monokai theme for syntax highlighting
detailed_layout = true              # Enable detailed layout with panels
summary_panel = true                # Show summary panel
split_views = true                  # Enable split views for logs/stats
stack_traces = true                 # Show detailed stack traces
save_reports = true                 # Save HTML and text reports
```

### Runtime Configuration
You can also configure via environment variables:
```bash
export PYTEST_RICH_THEME=monokai
export PYTEST_RICH_DETAILED=true
pytest test_rich_sample.py -v
```

## Features Demonstrated

### 1. Summary Panel
- Real-time test statistics
- Success rate calculation
- Elapsed time tracking
- Color-coded status indicators

### 2. Detailed Layout
- Split view with test results and logs
- Live progress updates
- Rich formatting with icons and colors

### 3. Monokai Theme
- Syntax highlighting for code and stack traces
- Consistent color scheme across all output
- HTML/SVG export with theme preservation

### 4. Stack Traces
- Comprehensive error formatting
- Line numbers and syntax highlighting
- Context-aware error details

### 5. Export Features
- HTML reports with Monokai theme
- Plain text reports for CI/CD
- Optional SVG exports

## Expected Output

When you run the sample tests, you'll see:
1. **Startup Banner**: Rich formatted session start
2. **Live Progress**: Real-time test execution with colored status
3. **Summary Panel**: Comprehensive statistics with success rates
4. **Test Results Table**: Detailed test outcomes with timing
5. **Failure Analysis**: Rich formatted stack traces for failed tests
6. **Session Summary**: Final statistics and export file locations

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
   ```bash
   pip install --upgrade rich pytest
   ```

2. **Theme Not Applied**: Verify terminal supports color
   ```bash
   pytest test_rich_sample.py --color=yes -v
   ```

3. **Layout Issues**: Check terminal width
   ```bash
   # Force wider terminal
   COLUMNS=120 pytest test_rich_sample.py -v
   ```

### VS Code Integration
Add to `.vscode/settings.json`:
```json
{
    "python.testing.pytestArgs": [
        "test_rich_sample.py",
        "-v",
        "--color=yes"
    ],
    "python.testing.pytestEnabled": true
}
```

## Sample Commands

Try these commands to see the rich reporting in action:

```bash
# Basic rich reporting
pytest test_rich_sample.py -v

# Show only failures with rich stack traces
pytest test_rich_sample.py -v --tb=short

# Run with live progress (this is default with our integration)
pytest test_rich_sample.py -v -s

# Generate reports and run tests
pytest test_rich_sample.py -v && echo "Check pytest_rich_report.html"
```

## Integration with CI/CD

For CI environments, the custom integration automatically:
- Detects terminal capabilities
- Generates text reports for log parsing
- Provides structured output for analysis
- Maintains compatibility with existing pytest workflows

Example GitHub Actions configuration:
```yaml
- name: Run tests with rich reporting
  run: |
    python -m pytest test_rich_sample.py -v
    # HTML reports are automatically generated
```

## Next Steps

1. **Replace Sample Tests**: Replace `test_rich_sample.py` with your actual tests
2. **Customize Configuration**: Modify `pyproject_rich_custom.toml` for your needs
3. **Extend Functionality**: Add custom reporters or modify the RichTestReporter class
4. **Integration**: Integrate with your CI/CD pipeline using the generated reports

The custom integration provides all the comprehensive rich reporting features you requested while maintaining full pytest compatibility.
