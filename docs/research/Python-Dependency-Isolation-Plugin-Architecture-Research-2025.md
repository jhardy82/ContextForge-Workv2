# Python Dependency Isolation Strategies for CLI Applications with Plugin Architectures

**Research Date**: 2025-11-24
**Project**: ContextForge Work (SCCMScripts)
**Context**: Multi-technology stack (Python + PowerShell + Node.js MCP servers)
**Primary Environment**: Windows with PowerShell automation

---

## Executive Summary

This research analyzes modern Python dependency isolation strategies for CLI applications with plugin architectures, focusing on practical solutions for the ContextForge Work project. The analysis covers seven distinct approaches, with **uv + dependency groups** emerging as the recommended solution due to its exceptional performance, modern PEP compliance, and seamless integration with existing tools.

### Key Findings

1. **uv (astral-sh)** provides 10-100x faster package installation than pip while maintaining full pip compatibility
2. **PDM** offers the most comprehensive PEP standards support (PEP 582, 621, 631, 660)
3. **Hatch** excels at multi-environment management with built-in test matrices
4. **Poetry** remains the most mature solution with the largest ecosystem
5. Current project uses a **hybrid approach** (requirements.txt + pyproject.toml) that needs modernization

### Recommended Approach

**Primary**: uv with PEP 735 dependency groups
**Secondary**: PDM for comprehensive PEP compliance
**Migration Path**: Gradual adoption with backward compatibility

---

## 1. Current Problem Analysis

### Project Structure Analysis

**Location**: `c:\Users\James\Documents\Github\GHrepos\SCCMScripts`

#### Current Dependency Management

```toml
# pyproject.toml (partial)
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
dependencies = [
    "click>=8.1.7,<8.2.0",
    "typer>=0.12.3,<0.13.0",
    "rich>=13.7,<14.0",
    # ... 20+ core dependencies
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
    "black>=23.0.0",
]
```

#### Multiple Requirements Files Detected

```
requirements.txt              # Core ML/testing dependencies
requirements-dev.txt          # Development tools (faker, factory-boy)
requirements-test.txt         # Testing (pytest-xdist, faker)
requirements-extra.txt        # Additional features
requirements-docker.txt       # Container-specific
requirements-cf-testing.txt   # ContextForge testing
```

**Issues Identified**:
- ❌ Fragmented dependency management across 6+ files
- ❌ No lock file for reproducible installations
- ❌ Version conflicts between faker (19.3.0 in dev) and (30.8.2 in test)
- ❌ pytest-xdist not in main requirements causing import errors
- ❌ No clear separation between plugin dependencies and core dependencies
- ❌ setuptools build backend (legacy approach)

### Plugin Architecture Analysis

**Current Entry Points**:
```toml
[project.entry-points."contextforge.cli.plugin"]
tasks = "contextforge.cli.plugins.tasks:app"
sprints = "contextforge.cli.plugins.sprints:app"
projects = "contextforge.cli.plugins.projects:app"
action_lists = "contextforge.cli.plugins.action_lists:app"
db = "contextforge.cli.plugins.db:app"
```

**Strengths**:
- ✅ Standard entry points mechanism
- ✅ Clear plugin namespace
- ✅ Typer-based architecture

**Gaps**:
- ❌ No optional dependency groups for plugins
- ❌ No version compatibility matrix
- ❌ No plugin isolation strategy

---

## 2. Modern Isolation Strategies

### 2.1 uv (astral-sh) - Recommended Primary Solution

**Website**: https://docs.astral.sh/uv/
**Installation**: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`

#### Key Features

- **Performance**: 10-100x faster than pip (Rust-based)
- **Compatibility**: Drop-in replacement for pip, pip-tools, pipx, poetry
- **Modern Standards**: PEP 621, 735 (dependency groups)
- **Lock Files**: Fast, deterministic `uv.lock` format
- **Python Management**: Built-in Python version management
- **Project Management**: Full lifecycle support (init, add, run, sync)

#### Workflow Example

```powershell
# Install uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Initialize project (converts existing pyproject.toml)
uv init

# Add dependencies
uv add click typer rich structlog

# Add development dependencies
uv add --dev pytest pytest-cov ruff mypy black

# Add optional plugin dependencies
uv add --optional database psycopg2-binary asyncpg
uv add --optional mcp jsonschema PyYAML

# Install with specific groups
uv sync                      # Install all dependencies
uv sync --no-dev            # Production only
uv sync --extra database    # With database plugin
uv sync --extra mcp         # With MCP plugin

# Run commands in isolated environment
uv run pytest
uv run python cf_cli.py

# Compile requirements.txt for CI/CD (backward compatibility)
uv pip compile pyproject.toml -o requirements.txt --universal
```

#### Migration Strategy for ContextForge

```toml
# pyproject.toml with uv + dependency groups
[project]
name = "sccmscripts"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "click>=8.1.7",
    "typer>=0.12.3",
    "rich>=13.7",
    "structlog>=24.0",
    # Core dependencies only
]

# Optional plugin dependencies
[project.optional-dependencies]
database = [
    "psycopg2-binary>=2.9.11",
    "asyncpg>=0.30.0",
]
mcp = [
    "jsonschema>=4.22",
    "PyYAML>=6.0",
]
analytics = [
    "pandas>=2.2",
    "polars>=1.5",
    "pyarrow>=16.0",
]

# PEP 735 dependency groups (development only)
[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]
test = [
    "pytest-xdist>=3.6.1",
    "faker>=30.8.2",
    "factory-boy>=3.3.1",
]
e2e = [
    "playwright>=1.40.0",
    "hypothesis>=6.115.2",
]

[tool.uv]
dev-dependencies = [
    "pre-commit>=3.5.0",
    "tqdm>=4.66",
]

[tool.uv.sources]
# Use local development versions of MCP servers
taskman-mcp = { path = "TaskMan-v2/mcp/taskman-typescript", editable = true }
```

**Advantages**:
- ⚡ **10-100x faster** than pip
- 🔒 Fast, deterministic lock files
- 🐍 Built-in Python version management
- 📦 Single tool replaces pip, pip-tools, pipx, poetry
- 🔄 Seamless pip compatibility
- 🪟 Excellent Windows support

**Disadvantages**:
- 📅 Relatively new (2024)
- 🧩 Still maturing plugin ecosystem
- 📚 Less community resources than Poetry

---

### 2.2 PDM (Python Development Master) - Recommended Secondary

**Website**: https://pdm-project.org/
**Installation**: `pip install pdm`

#### Key Features

- **PEP 582 Support**: No virtualenv needed (`__pypackages__`)
- **PEP 621 Native**: Full pyproject.toml compliance
- **PEP 631**: Dependency groups specification
- **Lock Files**: `pdm.lock` with full dependency graph
- **Plugin System**: Extensible via entry points

#### Workflow Example

```powershell
# Install PDM
pip install pdm

# Initialize project
pdm init

# Add dependencies
pdm add click typer rich

# Add to specific groups
pdm add -G test pytest pytest-cov
pdm add -G e2e pytest-xdist faker
pdm add -G database psycopg2-binary

# Install specific groups
pdm install                    # All groups
pdm install --prod            # Production only
pdm install -G test           # Just test group
pdm install -G test -G e2e    # Multiple groups

# Run commands
pdm run pytest
pdm run python cf_cli.py
```

#### Configuration Example

```toml
[project]
dependencies = [
    "click>=8.1.7",
    "typer>=0.12.3",
]

[project.optional-dependencies]
database = [
    "psycopg2-binary>=2.9.11",
]

[dependency-groups]
test = [
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
]
e2e = [
    "pytest-xdist>=3.6.1",
    "faker>=30.8.2",
]
dev = [
    {"include-group": "test"},
    {"include-group": "e2e"},
    "ruff>=0.1.0",
]
```

**Advantages**:
- ✅ Most comprehensive PEP standards support
- ✅ PEP 582 eliminates virtualenv complexity
- ✅ Excellent monorepo support
- ✅ Built-in plugin system
- ✅ Cross-platform (Windows, Linux, macOS)

**Disadvantages**:
- ⚠️ PEP 582 not widely adopted
- ⚠️ Smaller ecosystem than Poetry
- ⚠️ Learning curve for PEP 582 concepts

---

### 2.3 Poetry - Most Mature Solution

**Website**: https://python-poetry.org/
**Installation**: `powershell -c "(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -"`

#### Key Features

- **Mature Ecosystem**: Largest plugin ecosystem
- **Dependency Groups**: Comprehensive group management
- **Lock Files**: `poetry.lock` with deterministic resolution
- **Publishing**: Built-in package publishing
- **Virtual Environments**: Automatic venv management

#### Workflow Example

```powershell
# Install Poetry
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# Initialize
poetry init

# Add dependencies
poetry add click typer rich

# Add to groups
poetry add --group test pytest pytest-cov
poetry add --group e2e pytest-xdist faker
poetry add --group database psycopg2-binary

# Install groups
poetry install                      # All groups
poetry install --without dev       # Exclude dev
poetry install --with docs         # Include docs
poetry install --only main         # Only main deps
```

#### Configuration Example

```toml
[tool.poetry.dependencies]
python = "^3.11"
click = "^8.1.7"
typer = "^0.12.3"

[tool.poetry.group.test.dependencies]
pytest = "^8.0.0"
pytest-cov = "^5.0.0"

[tool.poetry.group.e2e.dependencies]
pytest-xdist = "^3.6.1"
faker = "^30.8.2"

[tool.poetry.group.database]
optional = true

[tool.poetry.group.database.dependencies]
psycopg2-binary = "^2.9.11"
```

**Advantages**:
- ✅ Most mature and battle-tested
- ✅ Largest ecosystem (plugins, integrations)
- ✅ Excellent documentation
- ✅ Built-in publishing workflow
- ✅ Strong VS Code integration

**Disadvantages**:
- ⚠️ Slower than uv/PDM
- ⚠️ Dependency resolution can be slow
- ⚠️ Custom lock file format
- ⚠️ Heavier than alternatives

---

### 2.4 Hatch - Best for Multi-Environment Testing

**Website**: https://hatch.pypa.io/
**Installation**: `pipx install hatch`

#### Key Features

- **Environment Matrices**: Built-in test matrix support
- **Workspace Management**: Monorepo-friendly
- **Multiple Environments**: Parallel environment management
- **Scripts**: Environment-specific scripts
- **uv Integration**: Can use uv as installer

#### Workflow Example

```powershell
# Install Hatch
pipx install hatch

# Create environment
hatch env create

# Run commands in environment
hatch run python -V
hatch run pytest

# Run in specific environment
hatch run test:pytest
hatch run lint:ruff check

# Test across Python versions
hatch test
```

#### Configuration Example

```toml
[tool.hatch.envs.default]
dependencies = [
    "click>=8.1.7",
    "typer>=0.12.3",
]

[tool.hatch.envs.test]
dependencies = [
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
]

[[tool.hatch.envs.test.matrix]]
python = ["3.11", "3.12"]
feature = ["basic", "full"]

[tool.hatch.envs.test.scripts]
test = "pytest {args}"
cov = "pytest --cov {args}"

[tool.hatch.envs.lint]
detached = true
dependencies = [
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]

[tool.hatch.envs.lint.scripts]
check = ["ruff check .", "mypy ."]
fmt = ["ruff check --fix .", "ruff format ."]

# Use uv for faster installs
[tool.hatch.envs.default]
installer = "uv"
```

**Advantages**:
- ✅ Excellent test matrix support
- ✅ Multiple isolated environments per project
- ✅ Built-in scripts system
- ✅ Can use uv as installer
- ✅ PyPA official project

**Disadvantages**:
- ⚠️ More complex configuration
- ⚠️ Primarily focused on environment management
- ⚠️ Less emphasis on dependency resolution

---

### 2.5 pipx + pip-tools

**Installation**: `pip install pipx pip-tools`

#### Key Features

- **Isolated Tools**: pipx installs CLI tools in isolation
- **Pinned Dependencies**: pip-compile generates locked requirements
- **Simple**: Uses standard pip underneath
- **Backward Compatible**: Works with existing workflows

#### Workflow Example

```powershell
# Install tools
pip install pip-tools
pipx install black
pipx install ruff
pipx install pytest

# Create requirements files
pip-compile requirements.in -o requirements.txt
pip-compile requirements-dev.in -o requirements-dev.txt
pip-compile requirements-test.in -o requirements-test.txt

# Install
pip-sync requirements.txt requirements-dev.txt

# Run isolated tools
pipx run black .
pipx run ruff check .
```

#### Configuration

```ini
# requirements.in
click>=8.1.7
typer>=0.12.3
rich>=13.7

# requirements-dev.in
-c requirements.txt
ruff>=0.1.0
mypy>=1.5.0
black>=23.0.0

# requirements-test.in
-c requirements.txt
-c requirements-dev.txt
pytest>=8.0.0
pytest-cov>=5.0.0
pytest-xdist>=3.6.1
faker>=30.8.2
```

**Advantages**:
- ✅ Simple and familiar
- ✅ Works with existing pip
- ✅ Lightweight
- ✅ Good for tool isolation

**Disadvantages**:
- ⚠️ Manual requirements file management
- ⚠️ No dependency groups
- ⚠️ Slower than modern tools
- ⚠️ Limited plugin support

---

### 2.6 Docker/Podman

#### Configuration Example

```dockerfile
# Dockerfile for ContextForge
FROM python:3.11-slim as base

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (production)
RUN uv sync --no-dev

# Copy application
COPY . .

# Development stage
FROM base as dev
RUN uv sync --all-groups

# Testing stage
FROM dev as test
RUN uv run pytest

# Production stage
FROM base as prod
CMD ["uv", "run", "python", "cf_cli.py"]
```

**Advantages**:
- ✅ Complete isolation
- ✅ Reproducible across systems
- ✅ Production-ready
- ✅ Multi-stage builds

**Disadvantages**:
- ⚠️ Overhead for development
- ⚠️ Windows Docker performance
- ⚠️ Additional complexity

---

### 2.7 Nix/Devbox

**Not Recommended for ContextForge** due to:
- Limited Windows support
- Steep learning curve
- Overkill for Python-focused project
- Better suited for polyglot projects

---

## 3. Plugin Architecture Patterns

### 3.1 Entry Points (Current Approach)

**Used by**: pytest, Flask, Django, Typer

```toml
[project.entry-points."contextforge.cli.plugin"]
tasks = "contextforge.cli.plugins.tasks:app"
database = "contextforge.cli.plugins.database:app"
```

**Discovery Code**:
```python
from importlib.metadata import entry_points

def discover_plugins():
    discovered = entry_points(group='contextforge.cli.plugin')
    return {ep.name: ep.load() for ep in discovered}
```

**Advantages**:
- ✅ Standard Python mechanism
- ✅ Automatic discovery
- ✅ No runtime dependencies

**Disadvantages**:
- ⚠️ Requires package installation
- ⚠️ No runtime enable/disable

---

### 3.2 Namespace Packages

**Used by**: Azure SDK, Google Cloud SDK

```python
# contextforge/plugins/__init__.py
__path__ = __import__('pkgutil').extend_path(__path__, __name__)

# Multiple locations can contribute:
# - core/contextforge/plugins/tasks.py
# - plugins/database/contextforge/plugins/database.py
```

**Configuration**:
```toml
[tool.setuptools.packages.find]
where = ["src"]
include = ["contextforge.plugins.*"]

[project.optional-dependencies]
all-plugins = [
    "contextforge-plugin-database",
    "contextforge-plugin-analytics",
]
```

---

### 3.3 Stevedore (OpenStack Pattern)

```python
from stevedore import driver, extension

# Load single plugin
mgr = driver.DriverManager(
    namespace='contextforge.plugins',
    name='database',
    invoke_on_load=True,
)

# Load all plugins
mgr = extension.ExtensionManager(
    namespace='contextforge.plugins',
    invoke_on_load=True,
)
```

---

### 3.4 Pluggy (Pytest Pattern)

```python
import pluggy

hookspec = pluggy.HookspecMarker("contextforge")
hookimpl = pluggy.HookimplMarker("contextforge")

class PluginSpec:
    @hookspec
    def cf_register_command(self):
        """Register a CLI command"""

class DatabasePlugin:
    @hookimpl
    def cf_register_command(self):
        return database_command

# Discovery
pm = pluggy.PluginManager("contextforge")
pm.add_hookspecs(PluginSpec)
pm.load_setuptools_entrypoints("contextforge")
```

---

## 4. Requirements Management Best Practices

### 4.1 Dependency Groups Strategy

**Recommended Structure**:

```toml
[project]
dependencies = [
    # Core runtime dependencies only
    "click>=8.1.7",
    "typer>=0.12.3",
    "rich>=13.7",
    "structlog>=24.0",
]

[project.optional-dependencies]
# Plugin-specific dependencies (user-installable)
database = [
    "psycopg2-binary>=2.9.11",
    "asyncpg>=0.30.0",
]
mcp = [
    "jsonschema>=4.22",
    "PyYAML>=6.0",
]
analytics = [
    "pandas>=2.2",
    "polars>=1.5",
]
# Convenience group
all-plugins = [
    "sccmscripts[database]",
    "sccmscripts[mcp]",
    "sccmscripts[analytics]",
]

[dependency-groups]
# Development-only groups (PEP 735)
dev = [
    "ruff>=0.1.0",
    "mypy>=1.5.0",
    "black>=23.0.0",
]
test = [
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
    "pytest-xdist>=3.6.1",
]
e2e = [
    "faker>=30.8.2",
    "factory-boy>=3.3.1",
    "hypothesis>=6.115.2",
]
```

### 4.2 Version Pinning Strategies

**For Applications** (ContextForge):
```toml
# Exact versions in lock file, ranges in pyproject.toml
dependencies = [
    "click>=8.1.7,<8.2.0",      # Pin major.minor
    "typer>=0.12.3,<0.13.0",    # Pin major.minor
    "rich~=13.7",                # Compatible release
]
```

**For Libraries**:
```toml
# Wider ranges
dependencies = [
    "click>=8.0",
    "typer>=0.9",
]
```

### 4.3 Lock File Strategy

**Recommended**: Generate multiple lock files for different scenarios

```powershell
# Using uv
uv pip compile pyproject.toml -o requirements.txt --universal
uv pip compile pyproject.toml -o requirements-dev.txt --extra dev --universal
uv pip compile pyproject.toml -o requirements-test.txt --extra test --universal

# Using pip-tools
pip-compile pyproject.toml -o requirements.txt
pip-compile --extra dev pyproject.toml -o requirements-dev.txt
```

---

## 5. Practical Recommendations for ContextForge

### 5.1 Recommended Approach: uv + Dependency Groups

**Rationale**:
1. ⚡ **Performance**: 10-100x faster than current pip-based workflow
2. 🔒 **Reliability**: Deterministic lock files prevent "works on my machine"
3. 🪟 **Windows-First**: Excellent PowerShell integration
4. 🔄 **Backward Compatible**: Can generate requirements.txt for CI/CD
5. 🐍 **Python Management**: Built-in Python version management
6. 📦 **Single Tool**: Replaces pip, pip-tools, virtualenv

### 5.2 Migration Plan (3 Phases)

#### Phase 1: Foundation (Week 1)

```powershell
# 1. Install uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. Convert existing pyproject.toml
# (uv auto-detects and uses existing configuration)
uv init

# 3. Create lock file
uv lock

# 4. Test in development
uv sync
uv run pytest

# 5. Update CI/CD
uv pip compile pyproject.toml -o requirements.txt --universal
```

#### Phase 2: Restructure (Week 2-3)

```toml
# Consolidate requirements files into pyproject.toml

[project]
dependencies = [
    # Move from requirements.txt
]

[dependency-groups]
dev = [
    # Move from requirements-dev.txt
]
test = [
    # Move from requirements-test.txt + requirements-testing-enhanced.txt
]
e2e = [
    # E2E-specific dependencies
]
cf-testing = [
    # Move from requirements-cf-testing.txt
]
```

#### Phase 3: Plugin Isolation (Week 4)

```toml
[project.optional-dependencies]
# Convert plugins to optional dependencies
taskman = [
    "psycopg2-binary>=2.9.11",
]
mcp-integration = [
    "jsonschema>=4.22",
    "PyYAML>=6.0",
]
```

### 5.3 CI/CD Integration

**GitHub Actions Example**:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        run: irm https://astral.sh/uv/install.ps1 | iex

      - name: Set up Python
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync --all-groups

      - name: Run tests
        run: uv run pytest --cov

      - name: Run type checking
        run: uv run mypy python

      - name: Run linting
        run: uv run ruff check python
```

### 5.4 PowerShell Integration

**Helper Script** (`scripts/dev.ps1`):

```powershell
# Development helpers for ContextForge

function Invoke-CFTest {
    param([string]$Args = "")
    uv run pytest $Args
}

function Invoke-CFLint {
    uv run ruff check python
    uv run mypy python
}

function Invoke-CFFormat {
    uv run ruff check --fix python
    uv run ruff format python
}

function Invoke-CFRun {
    param([string]$Command)
    uv run python cf_cli.py $Command
}

# Aliases
Set-Alias cftest Invoke-CFTest
Set-Alias cflint Invoke-CFLint
Set-Alias cffmt Invoke-CFFormat
Set-Alias cfrun Invoke-CFRun

Export-ModuleMember -Function * -Alias *
```

### 5.5 Plugin Version Compatibility Matrix

```toml
[project.optional-dependencies]
# Plugin dependencies with compatibility constraints
taskman = [
    "psycopg2-binary>=2.9.11,<3.0",  # PostgreSQL driver
]
mcp = [
    "jsonschema>=4.22,<5.0",          # Schema validation
    "PyYAML>=6.0,<7.0",                # YAML support
]

[tool.uv.sources]
# Development versions (local paths)
taskman-mcp = { path = "TaskMan-v2/mcp/taskman-typescript", editable = true }

# Version-specific overrides
[tool.uv.override-dependencies]
# Force specific versions when conflicts occur
numpy = ">=1.26,<2.0"  # For Python 3.12 compatibility
```

---

## 6. Real-World Examples

### 6.1 Pytest Plugin Ecosystem

**Structure**:
```python
# pytest_plugin_example.py
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow")

# setup.py / pyproject.toml
[project.entry-points.pytest11]
myplugin = "pytest_plugin_example"
```

**Installation**:
```toml
[dependency-groups]
test = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-xdist>=3.6",  # Parallel execution
    "pytest-asyncio",      # Async testing
    "pytest-mock",         # Mocking helpers
]
```

### 6.2 Black Plugin System

```toml
[tool.black]
line-length = 120
target-version = ['py311']

[dependency-groups]
dev = [
    "black>=23.0",
    "black[d]",  # Extra for "blackd" server
]
```

### 6.3 Ruff Plugin Configuration

```toml
[tool.ruff]
line-length = 120
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort
    "UP",  # pyupgrade
]

[dependency-groups]
dev = [
    "ruff>=0.1.0",
]
```

### 6.4 VS Code Extension: Python

**Detection Logic**: Automatically detects:
- `uv.lock` → Uses uv
- `pdm.lock` → Uses PDM
- `poetry.lock` → Uses Poetry
- `requirements.txt` → Uses pip

---

## 7. Comparison Matrix

| Feature | uv | PDM | Poetry | Hatch | pipx+pip-tools |
|---------|-----|-----|--------|-------|----------------|
| **Performance** | ⚡⚡⚡⚡⚡ | ⚡⚡⚡ | ⚡⚡ | ⚡⚡⚡ | ⚡⚡ |
| **Lock Files** | ✅ Fast | ✅ Yes | ✅ Yes | ❌ No | ✅ Manual |
| **PEP 621** | ✅ | ✅ | ❌ Custom | ✅ | ✅ |
| **PEP 735** | ✅ | ✅ | ❌ | ✅ | ❌ |
| **Dependency Groups** | ✅ | ✅ | ✅ | ✅ | ⚠️ Manual |
| **Windows Support** | ✅✅ | ✅ | ✅ | ✅ | ✅ |
| **Python Management** | ✅ Built-in | ❌ | ❌ | ❌ | ❌ |
| **Plugin Ecosystem** | ⚠️ New | ✅ | ✅✅ | ✅ | ⚠️ Limited |
| **Maturity** | ⚠️ 2024 | ✅ | ✅✅ | ✅ | ✅ |
| **Learning Curve** | 🔵 Low | 🟡 Medium | 🟡 Medium | 🟡 Medium | 🔵 Low |
| **Mono-repo Support** | ✅ | ✅✅ | ⚠️ Limited | ✅✅ | ❌ |
| **Multi-Python Testing** | ✅ | ⚠️ Manual | ⚠️ Manual | ✅✅ | ❌ |
| **CI/CD Friendly** | ✅✅ | ✅ | ✅ | ✅ | ✅✅ |

---

## 8. Final Recommendations

### For ContextForge Work: uv + Dependency Groups

**Primary Toolchain**:
1. **uv** for dependency management and isolation
2. **PEP 735 dependency groups** for development categories
3. **Entry points** for plugin discovery
4. **Optional dependencies** for user-installable plugins
5. **uv.lock** for deterministic installations

**Workflow**:
```powershell
# Development
uv sync --all-groups
uv run pytest
uv run python cf_cli.py

# CI/CD
uv pip compile pyproject.toml -o requirements.txt
uv pip sync requirements.txt
uv run pytest

# User installation
uv pip install "sccmscripts[database,mcp]"
```

**Benefits for ContextForge**:
- ✅ 10-100x faster than current pip workflow
- ✅ Solves current version conflicts (faker, pytest-xdist)
- ✅ Excellent Windows/PowerShell integration
- ✅ Backward compatible (can generate requirements.txt)
- ✅ Built-in Python version management for testing
- ✅ Simplifies MCP server integration
- ✅ No breaking changes to existing code

**Migration Effort**: Low (1-2 weeks)

### Alternative: PDM for Maximum PEP Compliance

Consider PDM if:
- PEP 582 (`__pypackages__`) is desirable
- Maximum PEP standards compliance is required
- Monorepo management is a priority

### Avoid:
- ❌ Poetry (slower, custom formats, heavier)
- ❌ Nix/Devbox (Windows support issues, complexity)
- ❌ Docker-only (development overhead on Windows)

---

## 9. Implementation Checklist

### Pre-Migration
- [ ] Audit all dependencies across requirements files
- [ ] Resolve version conflicts (faker: 19.3.0 vs 30.8.2)
- [ ] Document current plugin architecture
- [ ] Create test coverage baseline

### Phase 1: Setup (Week 1)
- [ ] Install uv: `irm https://astral.sh/uv/install.ps1 | iex`
- [ ] Initialize uv: `uv init`
- [ ] Generate lock file: `uv lock`
- [ ] Test in development: `uv sync && uv run pytest`
- [ ] Update `.gitignore` (add `uv.lock`)

### Phase 2: Consolidation (Week 2-3)
- [ ] Merge requirements files into `pyproject.toml`
- [ ] Define dependency groups (dev, test, e2e)
- [ ] Define optional dependencies (plugins)
- [ ] Update documentation
- [ ] Update PowerShell automation scripts

### Phase 3: CI/CD (Week 3-4)
- [ ] Update GitHub Actions workflows
- [ ] Generate backward-compatible requirements.txt
- [ ] Test across Python 3.11 and 3.12
- [ ] Update deployment scripts
- [ ] Update developer onboarding docs

### Phase 4: Validation (Week 4)
- [ ] Run full test suite
- [ ] Verify plugin loading
- [ ] Check MCP server integration
- [ ] Performance benchmarks
- [ ] Team review and feedback

---

## 10. References

### Official Documentation
- **uv**: https://docs.astral.sh/uv/
- **PDM**: https://pdm-project.org/
- **Poetry**: https://python-poetry.org/
- **Hatch**: https://hatch.pypa.io/
- **pip-tools**: https://pip-tools.readthedocs.io/

### PEP Standards
- **PEP 621**: Storing project metadata in pyproject.toml
- **PEP 735**: Dependency Groups in pyproject.toml
- **PEP 631**: Dependency specification for Python
- **PEP 582**: Python local packages directory
- **PEP 660**: Editable installs for pyproject.toml

### Plugin Architecture
- **Entry Points**: https://packaging.python.org/specifications/entry-points/
- **Stevedore**: https://docs.openstack.org/stevedore/
- **Pluggy**: https://pluggy.readthedocs.io/

### Community Resources
- Astral Discord: https://discord.gg/astral-sh
- Python Packaging Authority: https://www.pypa.io/
- Python Packaging User Guide: https://packaging.python.org/

---

## Appendix A: Complete Migration Example

```toml
# pyproject.toml - After Migration
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "sccmscripts"
version = "0.1.0"
description = "ContextForge-Work Library for SCCM automation and task management"
authors = [{ name = "James Hardy", email = "james@sccmscripts.dev" }]
requires-python = ">=3.11"
readme = "README.md"
license = "MIT"
keywords = ["automation", "sccm", "contextforge", "task-management"]

# Core runtime dependencies
dependencies = [
    "click>=8.1.7,<8.2.0",
    "typer>=0.12.3,<0.13.0",
    "rich>=13.7,<14.0",
    "python-dateutil>=2.9.0",
    "pydantic>=2.11,<3.0",
    "orjson>=3.10,<4.0",
    "PyYAML>=6.0",
    "structlog>=24.0,<26.0",
]

# Optional plugin dependencies
[project.optional-dependencies]
database = [
    "psycopg2-binary>=2.9.11",
    "asyncpg>=0.30.0",
]
mcp = [
    "jsonschema>=4.22,<5.0",
    "PyYAML>=6.0",
]
analytics = [
    "pandas>=2.2,<2.3",
    "pyarrow>=16.0,<17.0",
    "polars>=1.5,<2.0",
]
all-plugins = [
    "sccmscripts[database]",
    "sccmscripts[mcp]",
    "sccmscripts[analytics]",
]

# PEP 735 dependency groups (development only)
[dependency-groups]
dev = [
    "ruff>=0.1.0",
    "mypy>=1.5.0",
    "black>=23.0.0",
    "pre-commit>=3.5.0",
]
test = [
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
    "pytest-xdist>=3.6.1",
    "pytest-rich>=0.2.0",
]
e2e = [
    "faker>=30.8.2",
    "factory-boy>=3.3.1",
    "hypothesis>=6.115.2",
    "pytest-html>=4.1.1",
]

[project.scripts]
cf = "contextforge.cli.main:main"

[project.entry-points."contextforge.cli.plugin"]
tasks = "contextforge.cli.plugins.tasks:app"
sprints = "contextforge.cli.plugins.sprints:app"
projects = "contextforge.cli.plugins.projects:app"
action_lists = "contextforge.cli.plugins.action_lists:app"
db = "contextforge.cli.plugins.db:app"

[tool.uv]
dev-dependencies = [
    "tqdm>=4.66,<5.0",
]

[tool.uv.sources]
# Local development versions
taskman-mcp = { path = "TaskMan-v2/mcp/taskman-typescript", editable = true }

[tool.ruff]
line-length = 120
target-version = "py311"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
pythonpath = [".", "python", "src"]
testpaths = ["tests", "python"]
addopts = ["--strict-markers", "--color=yes", "-v"]
```

---

## Appendix B: PowerShell Automation Scripts

```powershell
# scripts/cf-dev-tools.ps1
# ContextForge Development Tools

function Install-CFDevelopmentTools {
    Write-Host "Installing ContextForge development tools..." -ForegroundColor Green

    # Install uv
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

    # Refresh PATH
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("PATH", "User")

    # Verify installation
    uv --version

    Write-Host "uv installed successfully!" -ForegroundColor Green
}

function Initialize-CFEnvironment {
    param(
        [switch]$AllGroups
    )

    Write-Host "Initializing ContextForge environment..." -ForegroundColor Green

    if ($AllGroups) {
        uv sync --all-groups
    } else {
        uv sync
    }

    Write-Host "Environment initialized!" -ForegroundColor Green
}

function Invoke-CFTest {
    param(
        [string]$Path = "tests",
        [switch]$Coverage,
        [switch]$Parallel
    )

    $args = @($Path)
    if ($Coverage) { $args += "--cov" }
    if ($Parallel) { $args += "-n", "auto" }

    uv run pytest @args
}

function Invoke-CFLint {
    Write-Host "Running linters..." -ForegroundColor Green

    uv run ruff check python
    uv run mypy python --show-error-codes
}

function Invoke-CFFormat {
    Write-Host "Formatting code..." -ForegroundColor Green

    uv run ruff check --fix python
    uv run ruff format python
}

function Update-CFDependencies {
    Write-Host "Updating dependencies..." -ForegroundColor Green

    uv lock --upgrade
    uv sync --all-groups

    Write-Host "Dependencies updated!" -ForegroundColor Green
}

function Export-CFRequirements {
    param(
        [string]$OutputFile = "requirements.txt",
        [switch]$Dev
    )

    Write-Host "Exporting requirements to $OutputFile..." -ForegroundColor Green

    if ($Dev) {
        uv pip compile pyproject.toml --extra dev -o $OutputFile --universal
    } else {
        uv pip compile pyproject.toml -o $OutputFile --universal
    }

    Write-Host "Requirements exported!" -ForegroundColor Green
}

# Aliases
Set-Alias cftest Invoke-CFTest
Set-Alias cflint Invoke-CFLint
Set-Alias cffmt Invoke-CFFormat
Set-Alias cfupdate Update-CFDependencies
Set-Alias cfexport Export-CFRequirements

Export-ModuleMember -Function * -Alias *
```

---

**End of Research Document**

This research provides a comprehensive analysis of modern Python dependency isolation strategies tailored for the ContextForge Work project. The recommendation is to adopt **uv + PEP 735 dependency groups** as the primary solution, with a clear migration path and implementation checklist.
