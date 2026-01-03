# CF CORE Plugin Development Guide

**Version**: 2.0
**Last Updated**: 2025-11-16
**Status**: Active

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Plugin Discovery](#plugin-discovery)
4. [PLUGIN_META Schema](#plugin_meta-schema)
5. [Plugin Registration](#plugin-registration)
6. [Environment Variables](#environment-variables)
7. [Version Constraints](#version-constraints)
8. [Dependency Management](#dependency-management)
9. [Enable/Disable Control](#enabledisable-control)
10. [Testing Your Plugin](#testing-your-plugin)
11. [Troubleshooting](#troubleshooting)
12. [Best Practices](#best-practices)
13. [Examples](#examples)

---

## Overview

The CF CORE plugin system allows you to extend the CLI with custom commands using a simple file-based discovery pattern. Plugins are Python modules that follow a specific contract and are automatically discovered and registered at CLI startup.

### Key Features

- **File-Based Discovery**: No package installation required
- **Typer Integration**: Use Typer sub-apps for command groups
- **Version Constraints**: Declare minimum/maximum CLI versions
- **Dependency Management**: Declare plugin dependencies
- **Enable/Disable Control**: Control which plugins load
- **Optional Caching**: Fast startup with file-based cache
- **Fail-Soft**: Bad plugins don't crash the CLI

---

## Quick Start

### 1. Create a Plugin File

Create a file named `plugin_<name>.py` in `src/cli_plugins/`:

```python
# src/cli_plugins/plugin_hello.py
import typer

# Metadata (required)
PLUGIN_META = {
    "name": "hello",
    "version": "1.0.0",
    "summary": "Hello world plugin",
}

# Create Typer sub-app
app = typer.Typer(help="Hello commands")

@app.command()
def world():
    """Say hello to the world."""
    typer.echo("Hello, World!")

# Registration function (required)
def register(main_app, context: dict):
    """Register plugin with main CLI."""
    main_app.add_typer(app, name="hello")
    return ["hello.world"]
```

### 2. Test Your Plugin

```bash
# Verify discovery
cf plugins list

# Test your command
cf hello world
```

That's it! Your plugin is now part of the CLI.

---

## Plugin Discovery

### Discovery Process

1. **Scan Filesystem**: Find all `plugin_*.py` files in:
   - `src/cli_plugins/` (built-in location)
   - Paths in `CF_CLI_PLUGIN_PATHS` (semicolon-separated)

2. **Parse Metadata**: Extract `PLUGIN_META` from each file

3. **Apply Filters**:
   - Check version constraints (`min_cli_version`, `max_cli_version`)
   - Check enable/disable settings (`CF_PLUGINS_ENABLED`, `CF_PLUGINS_DISABLED`)
   - Validate dependencies

4. **Sort by Dependencies**: Use topological sort to ensure correct load order

5. **Load and Register**: Import modules and call `register()` functions

### Naming Convention

- **Required**: File must start with `plugin_`
- **Plugin Name**: Derived from filename (e.g., `plugin_tasks.py` → `tasks`)
- **Module Import**: `src.cli_plugins.plugin_<name>`

### Custom Plugin Paths

Add external plugin directories:

```bash
# Windows
set CF_CLI_PLUGIN_PATHS=C:\my\plugins;D:\other\plugins

# Linux/Mac
export CF_CLI_PLUGIN_PATHS=/my/plugins:/other/plugins
```

---

## PLUGIN_META Schema

The `PLUGIN_META` dictionary contains plugin metadata. Only `name` is required; all other fields are optional.

### Required Fields

```python
PLUGIN_META = {
    "name": "my_plugin",  # REQUIRED: unique identifier
}
```

### Basic Metadata (v1.0)

```python
PLUGIN_META = {
    "name": "tasks",
    "version": "1.0.0",              # Semantic version
    "summary": "Task management",    # One-line description
    "features": ["crud", "query"],   # List of capabilities
}
```

### Advanced Metadata (v2.0)

```python
PLUGIN_META = {
    "name": "tasks",
    "version": "1.0.0",
    "summary": "Task management commands",
    "features": ["task_crud", "task_query"],

    # Dependencies (v2.0)
    "depends": ["db", "logging"],    # Must load after these

    # Version constraints (v2.0)
    "min_cli_version": "2.0.0",      # Minimum CLI version
    "max_cli_version": "2.9.999",    # Maximum CLI version

    # Enable/disable (v2.0)
    "enabled_by_default": True,      # Auto-enable flag

    # Optional metadata
    "author": "Your Name",
    "license": "MIT",
    "homepage": "https://github.com/...",
    "tags": ["productivity", "tasks"],
}
```

### Schema Reference

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | Yes | - | Unique plugin identifier |
| `version` | string | No | "0.0.0" | Semantic version (MAJOR.MINOR.PATCH) |
| `summary` | string | No | null | One-line description |
| `description` | string | No | null | Detailed description (alias for summary) |
| `features` | array | No | [] | List of capability identifiers |
| `depends` | array | No | [] | Plugin dependencies (v2.0) |
| `min_cli_version` | string | No | null | Minimum CLI version (v2.0) |
| `max_cli_version` | string | No | null | Maximum CLI version (v2.0) |
| `enabled_by_default` | boolean | No | true | Auto-enable flag (v2.0) |
| `author` | string | No | null | Author name or team |
| `license` | string | No | null | License identifier (SPDX) |
| `homepage` | string | No | null | Documentation/repository URL |
| `tags` | array | No | [] | Searchable tags |

See [plugin-meta-schema-v2.yaml](plugin-meta-schema-v2.yaml) for complete specification.

---

## Plugin Registration

### Registration Function

Every plugin must implement a `register()` function:

```python
def register(main_app, context: dict) -> list[str]:
    """Register plugin with main CLI.

    Args:
        main_app: Main Typer application instance
        context: Shared context dictionary with services

    Returns:
        List of registered command names (for tracking)
    """
    # Register your sub-app
    main_app.add_typer(my_app, name="my_plugin")

    # Return command names
    return ["my_plugin.command1", "my_plugin.command2"]
```

### Context Dictionary

The `context` parameter provides access to shared services:

```python
def register(main_app, context: dict):
    # Access services
    logger = context.get("services", {}).get("logger")
    db = context.get("services", {}).get("db")
    config = context.get("services", {}).get("config")

    # Access config values
    db_host = context.get("config", {}).get("db_host")

    # Access utilities
    utc = context.get("utc")  # UTC timestamp function

    # Register plugin
    main_app.add_typer(app, name="my_plugin")
    return ["my_plugin.command"]
```

### Typer Sub-App Pattern

```python
import typer

# Create sub-app
app = typer.Typer(
    name="tasks",
    help="Task management commands",
    no_args_is_help=True,
)

# Add commands to sub-app
@app.command()
def list(status: str = "active"):
    """List tasks by status."""
    # Implementation

@app.command()
def create(title: str):
    """Create a new task."""
    # Implementation

# Register sub-app
def register(main_app, context):
    main_app.add_typer(app, name="tasks")
    return ["tasks.list", "tasks.create"]
```

---

## Environment Variables

### CF_CLI_PLUGIN_PATHS

Add custom plugin directories (semicolon-separated on Windows, colon-separated on Linux/Mac):

```bash
# Windows
set CF_CLI_PLUGIN_PATHS=C:\plugins;D:\more_plugins

# Linux/Mac
export CF_CLI_PLUGIN_PATHS=/home/user/plugins:/opt/plugins
```

### CF_PLUGINS_DISABLED

Disable specific plugins (comma-separated):

```bash
# Disable experimental and alpha plugins
set CF_PLUGINS_DISABLED=experimental,alpha_feature

# Plugin will be discovered but not loaded
```

### CF_PLUGINS_ENABLED

Enable **only** specified plugins (allowlist mode, comma-separated):

```bash
# Only load tasks and db plugins
set CF_PLUGINS_ENABLED=tasks,db

# All other plugins will be disabled
# Overrides CF_PLUGINS_DISABLED
```

### CF_PLUGIN_CACHE

Enable plugin discovery caching for faster startup:

```bash
# Enable cache
set CF_PLUGIN_CACHE=1

# Cache stored in: %TEMP%\cf_cli\plugin_cache.pkl
# Invalidated when plugin files change (mtime check)
```

### Priority Order

1. **CF_PLUGINS_ENABLED** (highest) - Allowlist mode
2. **CF_PLUGINS_DISABLED** - Denylist mode
3. **enabled_by_default** - Plugin's default setting

---

## Version Constraints

### Declaring Constraints

Specify minimum and/or maximum CLI versions:

```python
PLUGIN_META = {
    "name": "modern_plugin",
    "min_cli_version": "2.0.0",  # Requires CLI >= 2.0.0
    "max_cli_version": "2.9.999",  # Not compatible with CLI >= 3.0.0
}
```

### Version Comparison

- Uses semantic versioning (MAJOR.MINOR.PATCH)
- Pre-release metadata stripped (e.g., `2.0.0-beta` → `2.0.0`)
- Comparison: `(2, 0, 0) < (2, 5, 0) < (3, 0, 0)`

### Incompatible Plugins

If a plugin's version constraints aren't met:
- Plugin is skipped during discovery
- Warning logged with reason
- Other plugins continue loading

```
[WARN] Plugin 'modern_plugin' requires CLI >= 2.0.0 (current: 1.5.0)
```

---

## Dependency Management

### Declaring Dependencies

Specify plugins that must load before yours:

```python
PLUGIN_META = {
    "name": "tasks",
    "depends": ["db", "logging"],  # Requires db and logging plugins
}
```

### Dependency Resolution

1. **Topological Sort**: Plugins sorted to respect dependencies
2. **Circular Detection**: Circular dependencies cause error
3. **Missing Dependencies**: Plugin skipped if dependency not found

### Example Dependency Chain

```python
# plugin_db.py
PLUGIN_META = {"name": "db", "depends": []}

# plugin_tasks.py
PLUGIN_META = {"name": "tasks", "depends": ["db"]}

# plugin_velocity.py
PLUGIN_META = {"name": "velocity", "depends": ["db", "tasks"]}

# Load order: db → tasks → velocity
```

### Circular Dependencies

**Detected and reported**:

```
[ERROR] Circular dependency detected: tasks → velocity → tasks
```

Both plugins will be skipped.

---

## Enable/Disable Control

### Default Behavior

```python
# Enabled by default
PLUGIN_META = {
    "name": "stable",
    "enabled_by_default": True,  # Default
}

# Disabled by default (experimental)
PLUGIN_META = {
    "name": "experimental",
    "enabled_by_default": False,  # Requires opt-in
}
```

### Enabling Disabled Plugins

```bash
# Enable specific plugin
set CF_PLUGINS_ENABLED=experimental

# Or use allowlist to enable multiple
set CF_PLUGINS_ENABLED=stable,experimental,alpha
```

### Disabling Enabled Plugins

```bash
# Disable specific plugin
set CF_PLUGINS_DISABLED=unwanted

# Or disable multiple
set CF_PLUGINS_DISABLED=unwanted,experimental,alpha
```

---

## Testing Your Plugin

### Manual Testing

```bash
# 1. Verify discovery
cf plugins list | findstr your_plugin

# 2. Check version constraints
cf plugins list

# 3. Test commands
cf your_plugin command --help
cf your_plugin command arg1 arg2

# 4. Test with env vars
set CF_PLUGINS_DISABLED=other_plugin
cf your_plugin command
```

### Unit Tests

Create `tests/test_plugin_your_plugin.py`:

```python
import pytest
from src.cli_plugins.plugin_your_plugin import PLUGIN_META, register

def test_plugin_meta():
    """Test PLUGIN_META structure."""
    assert PLUGIN_META["name"] == "your_plugin"
    assert "version" in PLUGIN_META

def test_register_function():
    """Test registration returns command list."""
    from unittest.mock import Mock

    app = Mock()
    context = {"services": {}}

    commands = register(app, context)

    assert isinstance(commands, list)
    assert len(commands) > 0
    app.add_typer.assert_called_once()
```

### Integration Tests

Test plugin with actual CLI:

```python
# tests/test_integration_your_plugin.py
def test_plugin_loads():
    """Test plugin loads without errors."""
    from src.cli_plugins import load_and_register

    app = typer.Typer()
    context = {"services": {}}

    plugins = load_and_register(app, context)

    # Find your plugin
    your_plugin = next((p for p in plugins if p.name == "your_plugin"), None)
    assert your_plugin is not None
    assert your_plugin.registered is True
    assert your_plugin.error is None
```

---

## Troubleshooting

### Plugin Not Discovered

**Symptom**: Plugin doesn't appear in `cf plugins list`

**Checks**:
1. ✅ Filename starts with `plugin_`
2. ✅ File location is `src/cli_plugins/` or in `CF_CLI_PLUGIN_PATHS`
3. ✅ File has `.py` extension
4. ✅ Not in `.gitignore` or excluded directory

### Plugin Discovered But Not Loaded

**Symptom**: Plugin appears in list but not registered

**Checks**:
1. ✅ `PLUGIN_META` is a dictionary (not string, list, etc.)
2. ✅ `register()` function exists and is callable
3. ✅ Version constraints met (`min_cli_version`, `max_cli_version`)
4. ✅ Dependencies satisfied
5. ✅ Not disabled via `CF_PLUGINS_DISABLED`
6. ✅ Included in `CF_PLUGINS_ENABLED` (if set)

### Import Errors

**Symptom**: Plugin import fails

**Checks**:
1. ✅ All imports at top of file are available
2. ✅ No syntax errors (`python -m py_compile plugin_your.py`)
3. ✅ Dependencies installed (`pip install -r requirements.txt`)
4. ✅ No circular imports

### Version Mismatch

**Symptom**: Plugin skipped with version warning

**Solution**:
```python
# Check CLI version
cf --version

# Adjust plugin constraints
PLUGIN_META = {
    "min_cli_version": "1.5.0",  # Lower requirement
}
```

### Circular Dependency

**Symptom**: Plugins not loading due to circular dependency

**Solution**:
- Review dependency declarations
- Remove or break circular chain
- Use shared library for common code instead

---

## Best Practices

### 1. Naming

- ✅ Use lowercase, underscores for plugin names (`my_plugin`)
- ✅ Match filename to plugin name (`plugin_my_plugin.py`)
- ✅ Use descriptive names (`tasks` not `t`)
- ❌ Avoid special characters, spaces

### 2. Versioning

- ✅ Use semantic versioning (`1.0.0`, `2.1.3`)
- ✅ Increment versions on changes:
  - **MAJOR**: Breaking changes
  - **MINOR**: New features (backward compatible)
  - **PATCH**: Bug fixes
- ✅ Document version constraints if needed

### 3. Dependencies

- ✅ Declare all plugin dependencies in `depends`
- ✅ Keep dependency chains shallow (prefer 1-2 levels)
- ❌ Avoid circular dependencies
- ✅ Use shared libraries for common code

### 4. Error Handling

- ✅ Handle errors gracefully in commands
- ✅ Provide helpful error messages
- ✅ Use `try/except` for external operations
- ✅ Don't crash on missing config/services

### 5. Documentation

- ✅ Write clear command help text
- ✅ Document required context services
- ✅ Add docstrings to functions
- ✅ Include usage examples

### 6. Testing

- ✅ Write unit tests for your plugin
- ✅ Test with different env var combinations
- ✅ Test with missing dependencies
- ✅ Test error conditions

---

## Examples

### Example 1: Simple Plugin

```python
# src/cli_plugins/plugin_greet.py
import typer

PLUGIN_META = {
    "name": "greet",
    "version": "1.0.0",
    "summary": "Greeting commands",
}

app = typer.Typer(help="Greeting commands")

@app.command()
def hello(name: str = "World"):
    """Greet someone."""
    typer.echo(f"Hello, {name}!")

def register(main_app, context):
    main_app.add_typer(app, name="greet")
    return ["greet.hello"]
```

Usage:
```bash
cf greet hello --name Alice
# Output: Hello, Alice!
```

### Example 2: Plugin with Dependencies

```python
# src/cli_plugins/plugin_reports.py
import typer

PLUGIN_META = {
    "name": "reports",
    "version": "1.0.0",
    "summary": "Generate reports from tasks",
    "depends": ["db", "tasks"],  # Requires db and tasks plugins
    "min_cli_version": "2.0.0",
}

app = typer.Typer(help="Report generation")

@app.command()
def weekly():
    """Generate weekly report."""
    # Access db and tasks via context
    typer.echo("Generating weekly report...")

def register(main_app, context):
    # Access dependencies from context
    db = context.get("services", {}).get("db")
    if not db:
        typer.echo("Warning: Database service not available", err=True)

    main_app.add_typer(app, name="reports")
    return ["reports.weekly"]
```

### Example 3: Experimental Plugin

```python
# src/cli_plugins/plugin_ai_suggest.py
import typer

PLUGIN_META = {
    "name": "ai_suggest",
    "version": "0.1.0-alpha",
    "summary": "AI-powered task suggestions (experimental)",
    "enabled_by_default": False,  # Disabled by default
    "min_cli_version": "2.5.0",
    "tags": ["ai", "experimental"],
}

app = typer.Typer(help="AI suggestions (experimental)")

@app.command()
def suggest():
    """Get AI task suggestions."""
    typer.echo("🤖 Analyzing your tasks...")

def register(main_app, context):
    main_app.add_typer(app, name="ai")
    return ["ai.suggest"]
```

Enable it:
```bash
set CF_PLUGINS_ENABLED=ai_suggest
cf ai suggest
```

### Example 4: Plugin with Configuration

```python
# src/cli_plugins/plugin_export.py
import typer

PLUGIN_META = {
    "name": "export",
    "version": "1.0.0",
    "summary": "Export data to various formats",
    "depends": ["db"],
}

app = typer.Typer(help="Data export commands")

@app.command()
def csv(output: str = "export.csv"):
    """Export to CSV."""
    typer.echo(f"Exporting to {output}...")

@app.command()
def json(output: str = "export.json"):
    """Export to JSON."""
    typer.echo(f"Exporting to {output}...")

def register(main_app, context):
    # Get config from context
    config = context.get("config", {})
    export_path = config.get("export_path", "./exports")

    main_app.add_typer(app, name="export")
    return ["export.csv", "export.json"]
```

---

## Hot Reload

The CF CORE plugin system supports **hot reload** functionality (Sprint 2 - T-011), allowing you to modify plugin code and see changes without restarting the CLI application.

### When to Use Hot Reload

Hot reload is ideal for:
- ✅ **Plugin Development**: Rapid iteration during development
- ✅ **Configuration Changes**: Update plugin behavior without downtime
- ✅ **Bug Fixes**: Test fixes immediately in running application
- ✅ **Debugging**: Make changes and retry without full restart

### How It Works

The hot reload system automatically:
1. **Watches Plugin Directories**: Monitors `src/cli_plugins/` and custom paths for `.py` file changes
2. **Detects Changes**: Triggers reload when Python files are saved (debounced 100ms)
3. **Preserves State**: Saves plugin enabled/disabled status and custom state
4. **Reloads Module**: Uses `importlib.reload()` to reload Python module
5. **Re-registers Plugin**: Calls `register()` function with fresh code
6. **Restores State**: Restores saved state to maintain continuity

### Reload Lifecycle Hooks

Plugins can implement optional hooks for hot reload support:

```python
from src.cli_plugins.base import BasePlugin

class MyPlugin(BasePlugin):
    async def get_reload_state(self) -> dict:
        """Save custom state before reload."""
        return {
            "cached_data": self.cache,
            "user_settings": self.settings,
        }

    async def set_reload_state(self, state: dict) -> None:
        """Restore custom state after reload."""
        self.cache = state.get("cached_data", {})
        self.settings = state.get("user_settings", {})

    async def on_reload_async(self) -> None:
        """Called after successful reload."""
        self.logger.info("Plugin reloaded successfully")
```

### Performance

- **Target Reload Time**: < 1 second for most plugins
- **Typical Reload Times**:
  - Simple plugin: 50-200ms
  - Complex plugin with dependencies: 200-500ms
  - Heavy plugin with async I/O: 500-1000ms

### Limitations

- **Manual Trigger**: Requires file save to trigger reload
- **Single Plugin**: Reloads one plugin per file change
- **No Cascade**: Doesn't automatically reload dependent plugins
- **Limited Rollback**: State rolls back on error, but module doesn't

### See Also

For comprehensive hot reload information, see:
- **[Plugin Hot Reload Guide](plugin-hot-reload-guide.md)** - Complete hot reload documentation
- **[Async Plugin Development Guide](plugin-async-guide.md)** - Async lifecycle hooks

---

## See Also

- [PLUGIN_META Schema v2.0](plugin-meta-schema-v2.yaml) - Complete schema specification
- [Typer Documentation](https://typer.tiangolo.com/) - Typer framework
- [Plugin Discovery Implementation](../src/cli_plugins/__init__.py) - Source code
- [Plugin Tests](../tests/test_plugin_discovery.py) - Test examples
- [Plugin Hot Reload Guide](plugin-hot-reload-guide.md) - Hot reload system documentation
- [Async Plugin Development Guide](plugin-async-guide.md) - Async plugin patterns

---

**Version History**:
- **2.0** (2025-11-16): Added v2.0 features (dependencies, version constraints, enable/disable)
- **1.0** (2024): Initial version with basic discovery

**Maintained By**: ContextForge Team
**License**: MIT
