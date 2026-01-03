# Pytest-Rich: Comprehensive Installation, Configuration & Integration Guide

## Overview
Pytest-Rich is a comprehensive Rich library integration plugin for pytest that replaces the standard terminal reporter with enhanced visual output, progress tracking, syntax highlighting, and terminal capture capabilities.

## Installation & Setup

### Current Environment Status
✅ **pytest-rich 0.2.0** - Successfully installed
❌ **pytest-richer** - Removed due to --rich option conflict
✅ **Rich 14.1.0+** - Available for full integration

### Installation Command
```bash
# Install latest version (0.2.0)
python -m pip install pytest-rich

# Dependency verification
python -m pip show pytest-rich
```

### Compatibility Requirements
- **Python**: 3.9+ (dropped support for 3.7/3.8 in v0.2.0)
- **pytest**: 7.0+
- **Rich**: 14.1.0+
- **Dependencies**: attrs, pygments

## Core Features Demonstration

### 1. Enhanced Terminal Output
The plugin replaces pytest's standard terminal reporter with Rich-formatted output including:
- **Rich Panel Headers**: Comprehensive session information with system metadata
- **Progress Tracking**: Spinner-based progress indicators with percentage completion
- **Styled Summary Tables**: Color-coded test results with pass/fail statistics
- **Enhanced Exception Display**: Syntax-highlighted tracebacks with Rich Panel formatting

### 2. Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--rich` | Enable Rich terminal reporter | `pytest --rich tests/` |
| `--rich-capture` | Save terminal output to file | `pytest --rich-capture=svg tests/` |
| `--no-header` | Disable Rich header panel | `pytest --rich --no-header tests/` |
| `--no-summary` | Disable Rich summary panel | `pytest --rich --no-summary tests/` |

### 3. Terminal Capture Functionality
**Supported Formats**: SVG, HTML, TXT
```bash
# SVG export (recommended for documentation)
pytest --rich --rich-capture=svg tests/

# HTML export with interactive features
pytest --rich --rich-capture=html tests/

# Plain text export
pytest --rich --rich-capture=txt tests/
```

**Generated Files**: Automatic timestamp-based naming
- Format: `pytest_rich-YYYYMMDD_HHMMSS.{format}`
- Example: `pytest_rich-20250925_063002.svg`

## Theme & Styling Configuration

### 1. SyntaxTheme Integration
```python
# Default: "ansi_dark" theme for code syntax highlighting
# Available themes: "default", "emacs", "friendly", "colorful", "autumn", "murphy", "manni", "monokai", "perldoc", "pastie", "borland", "trac", "native", "fruity", "bw", "vim", "vs", "tango", "rrt", "xcode", "igor", "paraiso-light", "paraiso-dark", "lovelace", "algol", "algol_nu", "arduino", "rainbow_dash", "abap", "solarized-dark", "solarized-light", "github-dark", "ansi_dark"
```

### 2. Environment Variable Configuration
```bash
# Force color output
export FORCE_COLOR=1

# Disable color output
export NO_COLOR=1

# Terminal compatibility mode
export TTY_COMPATIBLE=1

# Interactive mode control
export TTY_INTERACTIVE=1

# Rich console width override
export COLUMNS=120
```

### 3. Custom Theme Development
```python
# Example custom theme for ContextForge integration
from rich.theme import Theme
from rich.console import Console

contextforge_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "progress": "magenta",
    "constitutional": "bold blue",
    "evidence": "bright_yellow",
    "quality_gate": "bright_green"
})

# Apply via environment or programmatic configuration
console = Console(theme=contextforge_theme)
```

## ContextForge Integration Recommendations

### 1. Constitutional Framework Testing Enhancement
**Alignment**: pytest-rich's Rich Panel system perfect for constitutional analysis visualization
```bash
# Enhanced constitutional gate testing
pytest --rich tests/constitutional/ --rich-capture=svg

# Quality gate validation with Rich formatting
pytest --rich -k "quality_gate" --rich-capture=html
```

### 2. Purple Theme Compatibility
**ContextForge Purple Theme Integration**:
```python
# Custom ContextForge purple theme
contextforge_purple_theme = Theme({
    "primary": "#6A5ACD",        # SlateBlue (ContextForge primary)
    "secondary": "#9370DB",      # MediumPurple
    "accent": "#8A2BE2",         # BlueViolet
    "success": "#32CD32",        # LimeGreen
    "warning": "#FFD700",        # Gold
    "error": "#DC143C",          # Crimson
    "info": "#4169E1",           # RoyalBlue
    "constitutional": "#6A5ACD", # Primary constitutional color
    "evidence": "#DDA0DD",       # Plum for evidence trails
    "quality": "#9932CC"         # DarkOrchid for quality gates
})
```

### 3. Evidence Trail Integration
**Rich Capture for Evidence**: SVG exports provide perfect evidence trail artifacts
```bash
# Evidence-tier testing with capture
pytest --rich --rich-capture=svg tests/evidence/ -m evidence

# Constitutional compliance with visual documentation
pytest --rich --rich-capture=html tests/constitutional/ --tb=rich
```

## Configuration Files Integration

### 1. pyproject.toml Configuration
```toml
[tool.pytest.ini_options]
addopts = [
    "--rich",
    "--rich-capture=svg",
    "--tb=rich",
    "-v"
]
testpaths = ["tests"]
markers = [
    "constitutional: Constitutional framework tests",
    "evidence: Evidence-tier tests requiring capture",
    "quality_gate: Quality gate validation tests"
]
```

### 2. pytest.ini Configuration
```ini
[pytest]
addopts = --rich --rich-capture=svg --tb=rich -v
testpaths = tests
markers =
    constitutional: Constitutional framework tests
    evidence: Evidence-tier tests requiring capture
    quality_gate: Quality gate validation tests
```

### 3. Environment-Specific Configurations
```bash
# Development environment - full Rich features
export PYTEST_ADDOPTS="--rich --rich-capture=svg --tb=rich -v"

# CI/CD environment - minimal Rich features for performance
export PYTEST_ADDOPTS="--rich --no-header --tb=short -v"

# Documentation generation - HTML capture with full metadata
export PYTEST_ADDOPTS="--rich --rich-capture=html --tb=rich -v --metadata"
```

## Advanced Usage Patterns

### 1. Sacred Geometry Testing Integration
```bash
# Triangle (Stability) testing phase
pytest --rich tests/triangle/ --rich-capture=svg -m stability

# Circle (Unity) testing phase
pytest --rich tests/circle/ --rich-capture=html -m unity

# Spiral (Evolution) testing phase
pytest --rich tests/spiral/ --rich-capture=svg -m evolution
```

### 2. Quality Gate Orchestration
```bash
# Constitutional gates with Rich visualization
pytest --rich tests/constitutional/ --rich-capture=svg --tb=rich

# Operational gates with progress tracking
pytest --rich tests/operational/ --rich-capture=html --tb=short

# Cognitive gates with detailed output
pytest --rich tests/cognitive/ --rich-capture=svg --tb=rich -v
```

### 3. Multi-Format Documentation Generation
```bash
# Generate comprehensive test documentation
pytest --rich --rich-capture=html tests/ --html=reports/test_report.html

# Create SVG artifacts for embedding in documentation
pytest --rich --rich-capture=svg tests/evidence/ -m evidence

# Plain text output for CI/CD logs
pytest --rich --rich-capture=txt tests/ > test_output.log
```

## Troubleshooting & Conflict Resolution

### 1. Plugin Conflicts
**Issue**: `ValueError: option names {'--rich'} already added`
**Solution**:
```bash
# Identify conflicting plugins
python -m pip list | grep pytest

# Disable conflicting plugins
pytest -p no:pytest_richer --rich tests/

# Or uninstall conflicting plugins
python -m pip uninstall pytest-richer -y
```

### 2. Terminal Compatibility Issues
**Issue**: Rich formatting not displaying correctly
**Solutions**:
```bash
# Force color output
export FORCE_COLOR=1
pytest --rich tests/

# Enable TTY compatibility mode
export TTY_COMPATIBLE=1
pytest --rich tests/

# Disable Rich if terminal incompatible
pytest --tb=short tests/
```

### 3. Capture File Issues
**Issue**: Capture files not generated or corrupted
**Solutions**:
```bash
# Verify write permissions in target directory
pytest --rich --rich-capture=svg tests/ --capture-path=./reports/

# Check for internal errors preventing capture
pytest --rich --rich-capture=svg tests/ -v --tb=rich

# Use alternative capture format
pytest --rich --rich-capture=html tests/
```

## Performance Considerations

### 1. Capture Performance Impact
- **SVG**: Minimal performance impact, excellent for documentation
- **HTML**: Moderate impact, interactive features
- **TXT**: Lowest impact, plain text output

### 2. CI/CD Optimization
```bash
# Optimized CI/CD configuration
pytest --rich --no-header --no-summary --tb=short tests/

# Evidence-only capture for critical tests
pytest --rich --rich-capture=svg tests/ -m evidence
```

### 3. Large Test Suite Recommendations
```bash
# Progress tracking for long-running suites
pytest --rich tests/ --tb=short -q

# Selective capture for important test categories
pytest --rich --rich-capture=svg tests/constitutional/ tests/evidence/
```

## Integration with Existing ContextForge Infrastructure

### 1. Unified Logging Compatibility
- ✅ **Compatible**: pytest-rich works alongside existing JSONL structured logging
- ✅ **Enhanced**: Rich terminal output supplements structured evidence trails
- ✅ **Complementary**: Terminal capture provides visual evidence artifacts

### 2. Constitutional Framework Integration
- ✅ **Visual Enhancement**: Rich Panels ideal for constitutional analysis display
- ✅ **Evidence Generation**: SVG/HTML captures serve as evidence artifacts
- ✅ **Quality Gates**: Rich formatting enhances quality gate validation visibility

### 3. Sacred Geometry Pattern Support
- ✅ **Triangle Tests**: Rich progress indicators for stability validation
- ✅ **Circle Tests**: Rich summary tables for unity/integration testing
- ✅ **Spiral Tests**: Rich capture for iterative improvement documentation

## Next Steps & Recommendations

### 1. Immediate Implementation
1. **Configure pyproject.toml** with `--rich` default option
2. **Set up capture directories** for evidence artifacts
3. **Create ContextForge purple theme** for brand consistency
4. **Update CI/CD pipelines** with Rich-optimized settings

### 2. Advanced Integration
1. **Custom Rich themes** matching ContextForge visual identity
2. **Evidence tier automation** with SVG capture for high-risk tests
3. **Constitutional gate visualization** with Rich Panel formatting
4. **Sacred geometry test organization** with Rich progress tracking

### 3. Documentation Enhancement
1. **SVG exports** for test result embedding in documentation
2. **HTML captures** for interactive test reports
3. **Theme examples** demonstrating ContextForge integration
4. **Performance benchmarks** for different capture modes

## Conclusion

pytest-rich provides a mature, comprehensive enhancement to pytest's terminal output with excellent compatibility for ContextForge's constitutional framework, evidence-based testing, and sacred geometry patterns. The plugin's Rich integration, theme customization, and capture capabilities align perfectly with ContextForge's observability-first principles and visual documentation requirements.

**Recommended Configuration**:
- Enable `--rich` by default in pyproject.toml
- Use SVG capture for evidence-tier tests
- Implement ContextForge purple theme
- Integrate with existing structured logging infrastructure
- Leverage capture functionality for constitutional compliance documentation
