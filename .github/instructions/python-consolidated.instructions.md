---
applyTo: "**/*.py"
description: "Python coding standards, research methodology, and LangChain patterns (consolidated)"
---

# Python Development Guide

**Authority**: PEP 8 | PEP 257 | Modern Python 3.12+ Best Practices
**Package Manager**: uv (NOT pip)

> Consolidated quick-reference for Python coding, research, and LangChain development.

---

## Package Management (uv - REQUIRED)

**ALWAYS use uv** for Python package management. Never use pip directly.

| Task | Command |
|------|---------|
| **Install all deps** | `uv sync` |
| **Add package** | `uv add package-name` |
| **Add dev package** | `uv add --dev package-name` |
| **Remove package** | `uv remove package-name` |
| **Run script** | `uv run python script.py` |
| **Run tests** | `uv run pytest` |
| **Update deps** | `uv sync --upgrade` |
| **Create venv** | `uv venv --python 3.12` |
| **Lock deps** | `uv lock` |

### ⚠️ NEVER USE

```bash
# ❌ DEPRECATED - Do not use these
pip install package-name
pip install -r requirements.txt
python -m venv .venv

# ✅ CORRECT - Use these instead
uv add package-name
uv sync
uv venv --python 3.12
```

---

## Code Style (PEP 8)

| Rule | Standard |
|------|----------|
| **Indentation** | 4 spaces |
| **Line length** | 79 characters max |
| **Imports** | Grouped: stdlib, third-party, local |
| **Naming** | `snake_case` functions/vars, `PascalCase` classes |
| **Type hints** | Required for public APIs |
| **Docstrings** | PEP 257 format |

### Quick Example

```python
def calculate_area(radius: float) -> float:
    """Calculate the area of a circle.

    Args:
        radius: The radius of the circle.

    Returns:
        The area calculated as π * radius².
    """
    import math
    return math.pi * radius ** 2
```

---

## Best Practices

- **Type hints**: Use `typing` module (`List[str]`, `Dict[str, int]`, `Optional[T]`)
- **Docstrings**: Every public function/class with PEP 257 format
- **Error handling**: Explicit exception handling with context
- **Testing**: pytest-style with fixtures and parametrization
- **Readability**: Prefer clear code over clever one-liners

---

## Research Hierarchy (When Needed)

| Tier | Source | Use For |
|------|--------|---------|
| **1** | Context7 MCP | Internal patterns, prior research |
| **2** | Official docs (python.org, vendor) | Authoritative reference |
| **3** | Validated web sources | When tiers 1-2 insufficient |

### When to Research

**Skip research for**: Local reasoning, formatting, small mechanical edits

**Research required for**: New libraries, API design, security/architecture changes

### Research Intensity

| Task Type | Intensity | Output |
|-----------|-----------|--------|
| Syntax question | Low | Short answer + 1-3 sources |
| Library comparison | Medium | Pros/cons table + recommendation |
| New core dependency | High | Mini-report with risks/recommendations |

---

## Confidence Scoring

For research-backed answers:

```
Confidence: 0.XX
```

| Score | Meaning | Action |
|-------|---------|--------|
| ≥0.90 | High | Single clear recommendation |
| 0.60-0.89 | Moderate | Note uncertainties, suggest validation |
| <0.60 | Low | Label tentative, provide next steps |

Mark unverified claims with `<UNVERIFIED>`.

---

## Testing Standards

- **Unit tests**: Core logic with pytest
- **Integration tests**: I/O, networking, database
- **Coverage**: Match project requirements
- **Fixtures**: Reuse setup via conftest.py

---

## Anti-Patterns

- Heavy dependencies for trivial tasks
- Outdated patterns conflicting with current best practices
- Clever one-liners over readable code
- Missing type hints on public APIs
- Logging secrets or unredacted outputs

---

**Consolidated from**: `python.instructions.md`, `Python-research.instructions.md`

**Full Reference**: See archived files for complete research methodology and intensity mapping.
