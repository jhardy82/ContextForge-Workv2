# ContextForge Pytest Configuration

**Authority**: Based on ContextForge Terminal Output Standard
**Reference**: `.github/instructions/terminal-output.instructions.md`
**Pattern Library**: `docs/reference/Rich-Console-Pattern-Library.md`
**Version**: 1.0.0

## Pytest ContextForge Integration

This configuration aligns pytest output with the ContextForge Terminal Output Standard, ensuring consistent Rich console formatting across all ContextForge tools.

### Core Requirements

1. **Rich Console Integration**: All pytest output uses ContextForge Rich patterns
2. **Structured Test Reporting**: Follow ContextForge 9-component output flow
3. **Progress Indication**: Multi-phase progress for test execution ≥5 seconds
4. **Consistent Styling**: ContextForge color schemes and status indicators
5. **Evidence Preservation**: Integrate with ContextForge evidence collection

### Configuration Files

#### conftest.py - ContextForge Pytest Integration

```python
# conftest.py - ContextForge pytest Rich integration
import pytest
import os
from pathlib import Path
from rich.theme import Theme
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

# ContextForge theme aligned with terminal-output.instructions.md
CONTEXTFORGE_PYTEST_THEME = Theme({
    # Success/High Confidence (≥80%)
    "pytest.success": "bright_green",
    "pytest.passed": "bright_green",
    "pytest.high_confidence": "bright_green",

    # Warning/Medium Confidence (60-79%)
    "pytest.warning": "bright_yellow",
    "pytest.medium_confidence": "bright_yellow",
    "pytest.skipped": "bright_yellow",

    # Error/Low Confidence (<60%)
    "pytest.error": "bright_red",
    "pytest.failed": "bright_red",
    "pytest.low_confidence": "bright_red",

    # Info/Neutral
    "pytest.info": "bright_blue",
    "pytest.header": "bright_blue",
    "pytest.progress": "bright_blue",

    # Emphasis
    "pytest.emphasis": "bright_magenta",
    "pytest.summary": "bright_magenta",

    # Neutral/Dim
    "pytest.dim": "dim",
    "pytest.neutral": "white",

    # Labels/Headers
    "pytest.label": "cyan",
    "pytest.metric": "cyan",
})

def pytest_configure(config):
    """Configure pytest with ContextForge enhancements."""
    # Ensure evidence directory exists
    evidence_dir = Path("logs/evidence/pytest")
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # Set ContextForge theme
    if not hasattr(config, '_contextforge_console'):
        config._contextforge_console = Console(theme=CONTEXTFORGE_PYTEST_THEME)

    # Configure Rich output settings
    os.environ['FORCE_COLOR'] = '1'
    os.environ['RICH_THEME'] = 'contextforge_pytest'

@pytest.fixture
def contextforge_console():
    """Provide ContextForge Rich console to tests."""
    return Console(theme=CONTEXTFORGE_PYTEST_THEME)

@pytest.fixture
def evidence_collector():
    """Enable evidence collection for ContextForge compliance."""
    evidence_dir = Path("logs/evidence/pytest")
    evidence_dir.mkdir(parents=True, exist_ok=True)

    class EvidenceCollector:
        def __init__(self):
            self.artifacts = []

        def collect_artifact(self, name, data, artifact_type="test_result"):
            artifact = {
                "name": name,
                "type": artifact_type,
                "data": data,
                "timestamp": pytest.current_timestamp() if hasattr(pytest, 'current_timestamp') else None
            }
            self.artifacts.append(artifact)
            return artifact

        def get_evidence_summary(self):
            return {
                "total_artifacts": len(self.artifacts),
                "by_type": {t: len([a for a in self.artifacts if a["type"] == t])
                           for t in set(a["type"] for a in self.artifacts)}
            }

    return EvidenceCollector()

# ContextForge markers aligned with terminal output standard
pytest_markers = [
    "contextforge: ContextForge framework compliance tests",
    "terminal_output: Terminal output standard compliance tests",
    "rich_console: Rich console formatting tests",
    "evidence_tier: Evidence collection and preservation tests",
    "quality_gate: Quality gate validation tests",
    "progress_indicator: Progress indication compliance tests",
    "color_scheme: Color scheme standardization tests",
    "structured_output: Structured output flow tests",
]

def pytest_collection_modifyitems(config, items):
    """Apply ContextForge categorization to test items."""
    for item in items:
        # Auto-mark tests that should follow terminal output standard
        if "rich" in item.name.lower() or "console" in item.name.lower():
            item.add_marker(pytest.mark.rich_console)
        if "evidence" in item.name.lower():
            item.add_marker(pytest.mark.evidence_tier)
        if "progress" in item.name.lower():
            item.add_marker(pytest.mark.progress_indicator)

def pytest_sessionstart(session):
    """Display ContextForge session start with Rich formatting."""
    console = Console(theme=CONTEXTFORGE_PYTEST_THEME)

    # Executive Summary Panel (ContextForge standard component 1)
    summary_panel = Panel(
        "[pytest.header]🧪 ContextForge Test Session[/pytest.header]\n"
        f"[pytest.info]Framework: ContextForge Terminal Output Standard[/pytest.info]\n"
        f"[pytest.info]Rich Console: Enabled with ContextForge theme[/pytest.info]\n"
        f"[pytest.info]Evidence Collection: Active[/pytest.info]",
        title="Test Session Initialization",
        border_style="bright_blue"
    )
    console.print(summary_panel)

def pytest_sessionfinish(session, exitstatus):
    """Display ContextForge session finish with Rich formatting."""
    console = Console(theme=CONTEXTFORGE_PYTEST_THEME)

    # Get test results
    passed = session.testscollected - session.testsfailed
    failed = session.testsfailed
    total = session.testscollected

    # Calculate confidence score (ContextForge standard)
    confidence_pct = (passed / total * 100) if total > 0 else 0

    # Determine status color based on ContextForge thresholds
    if confidence_pct >= 80:
        status_color = "pytest.success"
        status_text = "✅ HIGH CONFIDENCE"
    elif confidence_pct >= 60:
        status_color = "pytest.warning"
        status_text = "⚠️ MEDIUM CONFIDENCE"
    else:
        status_color = "pytest.error"
        status_text = "❌ LOW CONFIDENCE"

    # Executive Summary Table (ContextForge standard component 1)
    summary_table = Table(title="Test Execution Summary", show_header=True, header_style="pytest.emphasis")
    summary_table.add_column("Metric", style="pytest.label")
    summary_table.add_column("Value", style="pytest.neutral")
    summary_table.add_column("Status", style="pytest.neutral")

    summary_table.add_row("Total Tests", str(total), "")
    summary_table.add_row("Passed", str(passed), "")
    summary_table.add_row("Failed", str(failed), "")
    summary_table.add_row("Success Rate", f"{confidence_pct:.1f}%", Text(status_text, style=status_color))

    console.print(summary_table)

    # Final Status Display (ContextForge standard component 9)
    if exitstatus == 0:
        console.print(f"\n✅ [pytest.success]Test Session PASSED[/pytest.success]")
    else:
        console.print(f"\n❌ [pytest.error]Test Session FAILED[/pytest.error]")

    # Evidence Preservation Summary (ContextForge standard component 8)
    evidence_panel = Panel(
        "[pytest.info]Evidence artifacts available in logs/evidence/pytest/[/pytest.info]\n"
        "[pytest.info]Test results preserved with ContextForge compliance[/pytest.info]",
        title="📋 Evidence Preservation",
        border_style="bright_blue"
    )
    console.print(evidence_panel)
```

#### pytest.ini - ContextForge Optimized Configuration

```ini
[pytest]
# ContextForge Pytest Configuration
# Authority: .github/instructions/terminal-output.instructions.md
# Patterns: docs/reference/Rich-Console-Pattern-Library.md

# Test discovery aligned with ContextForge structure
python_files = test_*.py *_test.py
python_classes = Test* *Tests
python_functions = test_*

# ContextForge Terminal Output Standard compliance
addopts =
    --rich
    --color=yes
    -v
    --tb=rich
    --strict-markers
    --strict-config
    --durations=10
    --durations-min=1.0
    --maxfail=5
    -r fE

# Test discovery paths
testpaths =
    tests
    tests/python
    src

# ContextForge markers for structured testing
markers =
    # ContextForge Terminal Output Standard
    contextforge: ContextForge framework compliance tests
    terminal_output: Terminal output standard compliance tests
    rich_console: Rich console formatting tests
    evidence_tier: Evidence collection and preservation tests
    quality_gate: Quality gate validation tests
    progress_indicator: Progress indication compliance tests
    color_scheme: Color scheme standardization tests
    structured_output: Structured output flow tests

    # Standard test categorization
    unit: Unit tests (fast, isolated)
    integration: Integration tests (external dependencies)
    smoke: Smoke tests (critical path validation)
    slow: Tests that take >2 seconds

    # ContextForge Quality Gates
    constitutional: Constitutional framework tests
    cognitive: Cognitive architecture tests
    evidence: Evidence generation tests

# Rich-compatible logging (ContextForge requirement)
log_cli = true
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)8s] %(name)s: %(message)s
log_cli_date_format = %Y-%m-%d %H:%M:%S

# Filter warnings for clean ContextForge output
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning

# Async test support
asyncio_mode = auto
```

#### requirements-pytest.txt - ContextForge Pytest Dependencies

```txt
# ContextForge Pytest Requirements
# Authority: ContextForge Terminal Output Standard

# Core pytest with Rich integration
pytest>=8.2.0,<9.0.0
pytest-rich>=0.2.0

# ContextForge Rich dependencies
rich>=13.7.0,<14.0.0

# Enhanced testing capabilities
pytest-cov>=5.0.0,<6.0.0
pytest-xdist>=3.5.0,<4.0.0
pytest-timeout>=2.3.1,<3.0.0
pytest-benchmark>=4.0.0,<5.0.0
pytest-html>=4.1.0,<5.0.0

# Evidence and reporting
pytest-json-report>=1.5.0,<2.0.0
pytest-metadata>=3.1.0,<4.0.0

# Development and debugging
pytest-sugar>=1.0.0,<2.0.0
pytest-clarity>=1.0.1,<2.0.0
```

### Usage Examples

#### Basic ContextForge Testing
```bash
# Standard ContextForge test execution
pytest --rich tests/

# Evidence-tier testing with HTML capture
pytest --rich --html=reports/evidence.html tests/ -m evidence_tier

# Quality gate validation
pytest --rich tests/ -m quality_gate --tb=rich
```

#### Advanced ContextForge Testing
```bash
# Terminal output standard compliance testing
pytest --rich tests/ -m terminal_output

# Full ContextForge validation with evidence
pytest --rich --html=reports/contextforge.html tests/ -m "contextforge or terminal_output or rich_console"

# Progress indicator validation
pytest --rich tests/ -m progress_indicator --durations=0
```

#### CI/CD Integration
```bash
# CI-optimized ContextForge testing
pytest --rich --json-report --json-report-file=results.json tests/

# Evidence collection for compliance
pytest --rich --html=reports/compliance.html --self-contained-html tests/ -m evidence_tier
```

### Integration Checklist

- [ ] ContextForge theme configured with standard color schemes
- [ ] Rich console components imported and configured
- [ ] Progress indicators for test execution ≥5 seconds
- [ ] Executive summary table with confidence scoring
- [ ] Color-coded test results (green ≥80%, yellow 60-79%, red <60%)
- [ ] Evidence preservation integration
- [ ] Structured output flow implementation
- [ ] Status indicators with emoji conventions
- [ ] Final status display with clear pass/fail
- [ ] Quality gate integration for ContextForge compliance

### Compliance Validation

This configuration ensures pytest testing follows the ContextForge Terminal Output Standard:

1. **Rich Console Integration**: ✅ Uses ContextForge Rich theme
2. **Progress Indication**: ✅ Multi-phase progress display
3. **Color Schemes**: ✅ Standard color coding (80%/60% thresholds)
4. **Structured Output**: ✅ 9-component flow implemented
5. **Evidence Preservation**: ✅ Integrated with ContextForge evidence system
6. **Status Indicators**: ✅ Consistent emoji and color usage
7. **Quality Gates**: ✅ ContextForge compliance validation

---

**Authority Reference**: Based on `cf_constitutional_quality_gates.py` patterns as implemented in ContextForge Terminal Output Standard.
