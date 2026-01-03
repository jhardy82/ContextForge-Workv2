# pytest-rich ContextForge Configuration Template

## pyproject.toml - Recommended Configuration
```toml
[tool.pytest.ini_options]
# Enable Rich terminal reporter by default
addopts = [
    "--rich",
    "--rich-capture=svg",
    "--tb=rich",
    "-v",
    "--strict-markers",
    "--strict-config"
]

# Test discovery paths
testpaths = [
    "tests",
    "tests/constitutional",
    "tests/evidence",
    "tests/quality_gates"
]

# ContextForge-specific test markers
markers = [
    "constitutional: Constitutional framework compliance tests",
    "evidence: Evidence-tier tests requiring capture artifacts",
    "quality_gate: Quality gate validation tests",
    "sacred_geometry: Sacred geometry pattern tests",
    "triangle: Triangle (Stability) pattern tests",
    "circle: Circle (Unity) pattern tests",
    "spiral: Spiral (Evolution) pattern tests",
    "fractal: Fractal (Modularity) pattern tests",
    "pentagon: Pentagon (Harmony) pattern tests"
]

# Test filtering configuration
filterwarnings = [
    "ignore::pytest.PytestUnraisableExceptionWarning",
    "ignore::DeprecationWarning"
]

# Minimum test version requirements
minversion = "7.0"
```

## Custom ContextForge Theme Implementation
```python
# contextforge_theme.py
from rich.theme import Theme
from rich.console import Console

# ContextForge Constitutional Framework Theme
CONTEXTFORGE_THEME = Theme({
    # Primary ContextForge colors
    "primary": "#6A5ACD",           # SlateBlue - Primary brand
    "secondary": "#9370DB",         # MediumPurple - Secondary accent
    "accent": "#8A2BE2",            # BlueViolet - Accent highlights

    # Status colors
    "success": "#32CD32",           # LimeGreen - Success states
    "warning": "#FFD700",           # Gold - Warning states
    "error": "#DC143C",             # Crimson - Error states
    "info": "#4169E1",              # RoyalBlue - Information

    # Constitutional Framework colors
    "constitutional": "#6A5ACD",    # Primary constitutional
    "evidence": "#DDA0DD",          # Plum - Evidence trails
    "quality_gate": "#9932CC",      # DarkOrchid - Quality gates
    "sacred_geometry": "#8A2BE2",   # BlueViolet - Sacred geometry

    # Sacred Geometry pattern colors
    "triangle": "#4B0082",          # Indigo - Stability
    "circle": "#6A5ACD",            # SlateBlue - Unity
    "spiral": "#9370DB",            # MediumPurple - Evolution
    "fractal": "#8A2BE2",           # BlueViolet - Modularity
    "pentagon": "#9932CC",          # DarkOrchid - Harmony

    # Test result colors
    "passed": "#32CD32",            # LimeGreen - Passed tests
    "failed": "#DC143C",            # Crimson - Failed tests
    "skipped": "#FFD700",           # Gold - Skipped tests
    "xfail": "#FF8C00",             # DarkOrange - Expected failures
    "xpass": "#FF6347",             # Tomato - Unexpected passes

    # Progress and status indicators
    "progress": "#9370DB",          # MediumPurple - Progress bars
    "spinner": "#8A2BE2",           # BlueViolet - Loading spinners
    "percentage": "#6A5ACD",        # SlateBlue - Percentage display
})

def create_contextforge_console(**kwargs):
    """Create a Rich console with ContextForge theme."""
    return Console(theme=CONTEXTFORGE_THEME, **kwargs)

# Usage in pytest configuration
import os
os.environ['RICH_THEME'] = 'contextforge_theme.CONTEXTFORGE_THEME'
```

## Environment Variables for CI/CD
```bash
# .env.pytest - Environment configuration
# Rich terminal configuration
export FORCE_COLOR=1
export RICH_THEME="contextforge"
export COLUMNS=120
export LINES=30

# pytest-rich specific settings
export PYTEST_RICH_CAPTURE_PATH="./artifacts/pytest/"
export PYTEST_RICH_DEFAULT_FORMAT="svg"

# ContextForge evidence collection
export CF_EVIDENCE_ENABLED=1
export CF_CONSTITUTIONAL_TESTING=1
export CF_QUALITY_GATES_STRICT=1

# CI/CD optimizations
export PYTEST_ADDOPTS="--rich --rich-capture=svg --tb=rich -v"
export PYTEST_WORKERS=auto
export PYTEST_TIMEOUT=300
```

## Makefile Integration
```make
# pytest-rich ContextForge testing targets

.PHONY: test-rich test-constitutional test-evidence test-quality-gates

# Basic Rich testing
test-rich:
	python -m pytest --rich tests/ -v

# Constitutional framework testing with evidence capture
test-constitutional:
	python -m pytest --rich --rich-capture=svg tests/constitutional/ \
		-m constitutional --tb=rich -v

# Evidence-tier testing with HTML capture for interactivity
test-evidence:
	python -m pytest --rich --rich-capture=html tests/evidence/ \
		-m evidence --tb=rich -v --html=reports/evidence_report.html

# Quality gate validation with comprehensive output
test-quality-gates:
	python -m pytest --rich --rich-capture=svg tests/quality_gates/ \
		-m quality_gate --tb=rich -v --cov=src --cov-report=html

# Sacred geometry pattern testing
test-sacred-geometry:
	python -m pytest --rich --rich-capture=svg \
		-m "triangle or circle or spiral or fractal or pentagon" \
		--tb=rich -v

# Full ContextForge test suite with all enhancements
test-contextforge-full:
	python -m pytest --rich --rich-capture=html tests/ \
		--tb=rich -v --cov=src --cov-report=html \
		--html=reports/full_test_report.html \
		--metadata="framework:ContextForge" \
		--metadata="theme:purple" \
		--metadata="capture:enabled"

# Performance testing with minimal Rich overhead
test-performance:
	python -m pytest --rich --no-header --no-summary \
		--tb=short tests/performance/ -v

# CI/CD optimized testing
test-ci:
	python -m pytest --rich --rich-capture=svg \
		--tb=short -v --cov=src --cov-report=xml \
		--junitxml=reports/junit.xml
```

## VS Code Tasks Integration
```json
{
    "label": "pytest-rich: Constitutional Tests",
    "type": "process",
    "command": "${workspaceFolder}/.venv/Scripts/python.exe",
    "args": [
        "-m", "pytest",
        "--rich",
        "--rich-capture=svg",
        "tests/constitutional/",
        "-m", "constitutional",
        "--tb=rich",
        "-v"
    ],
    "group": "test",
    "options": {
        "cwd": "${workspaceFolder}",
        "env": {
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
            "FORCE_COLOR": "1",
            "RICH_THEME": "contextforge"
        }
    },
    "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared",
        "showReuseMessage": true,
        "clear": false
    },
    "problemMatcher": "$pytest"
}
```

## Custom pytest Plugin Integration
```python
# conftest.py - ContextForge pytest-rich integration
import pytest
import os
from pathlib import Path
from rich.theme import Theme
from rich.console import Console

# ContextForge theme configuration
CONTEXTFORGE_THEME = Theme({
    "constitutional": "#6A5ACD",
    "evidence": "#DDA0DD",
    "quality_gate": "#9932CC",
    "sacred_geometry": "#8A2BE2",
    "passed": "#32CD32",
    "failed": "#DC143C",
    "warning": "#FFD700"
})

def pytest_configure(config):
    """Configure pytest with ContextForge enhancements."""
    # Ensure artifacts directory exists
    artifacts_dir = Path("artifacts/pytest")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Set Rich theme if not already configured
    if not os.environ.get('RICH_THEME'):
        os.environ['RICH_THEME'] = 'contextforge'

    # Configure Rich console for ContextForge
    config._rich_console = Console(theme=CONTEXTFORGE_THEME)

@pytest.fixture
def rich_console():
    """Provide Rich console with ContextForge theme to tests."""
    return Console(theme=CONTEXTFORGE_THEME)

@pytest.fixture
def evidence_capture():
    """Enable evidence capture for evidence-tier tests."""
    artifacts_dir = Path("artifacts/evidence")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    return artifacts_dir

# Custom markers for ContextForge integration
pytest.mark.constitutional = pytest.mark.constitutional
pytest.mark.evidence = pytest.mark.evidence
pytest.mark.quality_gate = pytest.mark.quality_gate
pytest.mark.sacred_geometry = pytest.mark.sacred_geometry

# Sacred geometry pattern markers
pytest.mark.triangle = pytest.mark.triangle
pytest.mark.circle = pytest.mark.circle
pytest.mark.spiral = pytest.mark.spiral
pytest.mark.fractal = pytest.mark.fractal
pytest.mark.pentagon = pytest.mark.pentagon
```

## GitHub Actions Integration
```yaml
# .github/workflows/pytest-rich-contextforge.yml
name: ContextForge pytest-rich Testing

on: [push, pull_request]

jobs:
  test-contextforge:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest-rich rich pytest pytest-cov pytest-html
        pip install -r requirements.txt

    - name: Create artifacts directory
      run: mkdir -p artifacts/pytest artifacts/evidence

    - name: Run constitutional tests with Rich
      env:
        FORCE_COLOR: 1
        RICH_THEME: contextforge
      run: |
        python -m pytest --rich --rich-capture=svg \
          tests/constitutional/ -m constitutional \
          --tb=rich -v --cov=src

    - name: Run evidence-tier tests with HTML capture
      env:
        FORCE_COLOR: 1
        RICH_THEME: contextforge
      run: |
        python -m pytest --rich --rich-capture=html \
          tests/evidence/ -m evidence \
          --tb=rich -v --html=artifacts/evidence_report.html

    - name: Run quality gate validation
      env:
        FORCE_COLOR: 1
        RICH_THEME: contextforge
      run: |
        python -m pytest --rich --rich-capture=svg \
          tests/quality_gates/ -m quality_gate \
          --tb=rich -v --cov=src --cov-report=xml

    - name: Upload pytest-rich artifacts
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: pytest-rich-outputs-${{ matrix.python-version }}
        path: |
          artifacts/
          *.svg
          *.html
          coverage.xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
```

## Docker Integration
```dockerfile
# Dockerfile.pytest-rich - ContextForge testing container
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Rich terminal support
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
COPY requirements-dev.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements-dev.txt \
    && pip install pytest-rich

# Copy source code and tests
COPY . .

# Set environment variables for Rich terminal support
ENV FORCE_COLOR=1
ENV RICH_THEME=contextforge
ENV COLUMNS=120
ENV LINES=30

# Create artifacts directory
RUN mkdir -p artifacts/pytest artifacts/evidence

# Default command runs ContextForge test suite with Rich
CMD ["python", "-m", "pytest", "--rich", "--rich-capture=svg", \
     "--tb=rich", "-v", "--cov=src", "--cov-report=xml"]
```

## Usage Examples

### Basic Rich Testing
```bash
# Enable Rich output for all tests
pytest --rich tests/

# Constitutional framework testing with evidence capture
pytest --rich --rich-capture=svg tests/constitutional/ -m constitutional

# Quality gate validation with HTML report
pytest --rich --rich-capture=html tests/quality_gates/ -m quality_gate
```

### Advanced Sacred Geometry Testing
```bash
# Triangle pattern stability tests
pytest --rich tests/ -m triangle --rich-capture=svg

# Circle pattern unity tests
pytest --rich tests/ -m circle --rich-capture=html

# Spiral pattern evolution tests
pytest --rich tests/ -m spiral --rich-capture=svg

# All sacred geometry patterns
pytest --rich tests/ -m "triangle or circle or spiral" --rich-capture=html
```

### Evidence Collection and Documentation
```bash
# Evidence-tier tests with comprehensive capture
pytest --rich --rich-capture=html tests/evidence/ -m evidence \
  --html=reports/evidence_report.html --tb=rich -v

# Constitutional compliance with SVG documentation
pytest --rich --rich-capture=svg tests/constitutional/ \
  --tb=rich -v --metadata="compliance:required"

# Full documentation generation
pytest --rich --rich-capture=html tests/ --tb=rich -v \
  --html=reports/full_report.html \
  --cov=src --cov-report=html
```

This configuration template provides comprehensive pytest-rich integration with ContextForge's
constitutional framework, evidence-based testing, and sacred geometry patterns while maintaining
observability-first principles and visual documentation capabilities.
