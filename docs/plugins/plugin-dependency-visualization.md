# Plugin Dependency Visualization

Comprehensive guide to visualizing and debugging plugin dependency graphs using Rich Tree (T-CFCORE-PLUGIN_INFRASTRUCTURE-009).

## Table of Contents

1. [Overview](#overview)
2. [Visualization Function](#visualization-function)
3. [Status Indicators](#status-indicators)
4. [Usage Examples](#usage-examples)
5. [Interpreting Output](#interpreting-output)
6. [Troubleshooting Dependencies](#troubleshooting-dependencies)
7. [Enhanced Error Messages](#enhanced-error-messages)
8. [API Reference](#api-reference)

## Overview

The plugin dependency visualization system provides a beautiful, hierarchical view of plugin dependencies using Rich Tree formatting. This tool is essential for:

- **Debugging dependency issues**: Quickly identify circular dependencies and missing plugins
- **Understanding load order**: Visualize which plugins depend on which
- **Monitoring plugin health**: See registration status at a glance
- **Documentation**: Generate visual dependency maps for your plugin ecosystem

**Key Features:**
- Hierarchical tree view with color-coded status indicators
- Circular dependency detection with visual markers
- Orphaned plugin identification
- Error message display inline
- Summary statistics

## Visualization Function

### Basic Usage

```python
from src.cli_plugins import discover_plugins, build_dependency_graph, visualize_dependency_graph

# Discover all plugins
plugins = discover_plugins()

# Build dependency graph
graph, plugin_map = build_dependency_graph(plugins)

# Visualize the graph
visualize_dependency_graph(graph, plugin_map)
```

### Advanced Options

```python
# Customize visualization
visualize_dependency_graph(
    graph,
    plugin_map,
    max_depth=5,           # Limit tree depth to 5 levels
    show_orphans=False,    # Hide orphaned plugins
    console=my_console     # Use custom Rich Console
)
```

## Status Indicators

The visualization uses visual indicators to show plugin status:

| Icon | Status | Description |
|------|--------|-------------|
| ✅ | **Registered** | Plugin successfully registered and operational |
| ❌ | **Failed** | Plugin registration failed (error present) |
| ⏸️ | **Pending** | Plugin discovered but not yet registered |
| 🔄 | **Circular** | Circular reference detected in dependency chain |
| ❓ | **Not Found** | Plugin referenced but not in plugin map |

### Color Coding

- **Green**: Healthy, registered plugins
- **Red**: Failed plugins with errors
- **Yellow**: Pending or warning status
- **Magenta**: Circular references
- **Dim**: Secondary information (dependency counts, errors)

## Usage Examples

### Example 1: Simple Plugin Ecosystem

```python
# Given plugins: alpha (no deps), beta (depends on alpha)
visualize_dependency_graph(graph, plugin_map)
```

**Output:**
```
📦 Plugin Dependency Graph
├── ✅ alpha
│   └── ✅ beta (1 dep)
```

### Example 2: Complex Dependencies

```python
# Multiple dependency levels
visualize_dependency_graph(graph, plugin_map)
```

**Output:**
```
📦 Plugin Dependency Graph
├── ✅ database
│   ├── ✅ tasks (1 dep)
│   │   └── ✅ sprints (1 dep)
│   └── ✅ projects (1 dep)
└── ✅ auth
    └── ✅ api (1 dep)

Summary: 6 plugins total
  ✅ 6 registered
  ❌ 0 failed
  ⏸️  0 pending
```

### Example 3: Circular Dependency

```python
# Circular: alpha → beta → gamma → alpha
visualize_dependency_graph(graph, plugin_map)
```

**Output:**
```
📦 Plugin Dependency Graph
├── ✅ alpha (1 dep)
│   └── ✅ beta (1 dep)
│       └── ✅ gamma (1 dep)
│           └── 🔄 alpha (circular reference)

⚠️  Circular dependency detected in the graph
```

### Example 4: Failed Plugin with Error

```python
# Plugin with registration error
visualize_dependency_graph(graph, plugin_map)
```

**Output:**
```
📦 Plugin Dependency Graph
├── ✅ database
│   └── ❌ tasks (1 dep) - import_failed: No module named 'typer'

Summary: 2 plugins total
  ✅ 1 registered
  ❌ 1 failed
  ⏸️  0 pending
```

### Example 5: Orphaned Plugins

```python
# Plugin with missing dependency
visualize_dependency_graph(graph, plugin_map, show_orphans=True)
```

**Output:**
```
📦 Plugin Dependency Graph
├── ✅ database
└── ⏸️  Unresolved Dependencies
    └── ⏸️  orphan_plugin (1 dep)

Summary: 2 plugins total
  ✅ 1 registered
  ❌ 0 failed
  ⏸️  1 pending
```

### Example 6: Large Ecosystem with Depth Limit

```python
# Prevent infinite recursion in large graphs
visualize_dependency_graph(graph, plugin_map, max_depth=3)
```

**Output:**
```
📦 Plugin Dependency Graph
├── ✅ level1
│   └── ✅ level2 (1 dep)
│       └── ✅ level3 (1 dep)
│           └── ... (max depth reached)
```

## Interpreting Output

### Reading the Tree Structure

- **Root level**: Plugins with no dependencies (foundation plugins)
- **Child nodes**: Plugins that depend on their parent
- **Indentation**: Shows dependency hierarchy depth
- **Dependency count**: Number in parentheses shows how many dependencies a plugin has

### Understanding Dependency Flow

```
📦 Plugin Dependency Graph
├── ✅ database           ← Root (no dependencies)
│   ├── ✅ tasks (1 dep)  ← Depends on database
│   │   └── ✅ workflow (1 dep)  ← Depends on tasks
│   └── ✅ projects (1 dep)  ← Also depends on database
```

**Key Points:**
- `database` loads first (no dependencies)
- `tasks` and `projects` can load after `database`
- `workflow` must wait for `tasks`

### Identifying Issues

**Circular Dependencies:**
- Look for 🔄 markers in the tree
- Follow the path to see the cycle
- One plugin in the cycle must remove a dependency

**Missing Dependencies:**
- Check the "Unresolved Dependencies" section
- Plugins listed here have dependencies that don't exist
- Install missing plugins or remove invalid depends entries

**Failed Registrations:**
- Look for ❌ markers with error messages
- Error shown inline (truncated to 50 chars)
- Check full error details in plugin logs

## Troubleshooting Dependencies

### Problem 1: Circular Dependency Detected

**Symptom:**
```
🔄 alpha (circular reference)
```

**Solution:**
1. Follow the dependency chain shown in the tree
2. Identify which dependency creates the cycle
3. Remove or modify one dependency to break the cycle
4. Consider if all dependencies are actually required

**Example Fix:**
```python
# Before: alpha → beta → gamma → alpha (circular)
PLUGIN_META = {
    "name": "alpha",
    "depends": ["gamma"],  # Remove this dependency
}

# After: alpha → beta → gamma (no cycle)
PLUGIN_META = {
    "name": "alpha",
    "depends": [],  # Dependency removed
}
```

### Problem 2: Orphaned Plugin

**Symptom:**
```
⚠️  Unresolved Dependencies
└── ⏸️  orphan_plugin (1 dep)
```

**Solution:**
1. Check which dependency is missing
2. Install the missing plugin
3. Or remove the invalid dependency from PLUGIN_META

**Debugging:**
```python
# Check plugin's dependencies
plugin = plugin_map["orphan_plugin"]
print(plugin.depends)  # Shows what it's looking for

# Verify dependency exists
if "missing_dep" not in plugin_map:
    print("Missing dependency: install or remove from depends list")
```

### Problem 3: Plugin Fails to Register

**Symptom:**
```
❌ tasks (1 dep) - import_failed: No module named 'typer'
```

**Solution:**
1. Read the error message (shown inline)
2. Install missing Python packages
3. Fix import errors in plugin code
4. Check PLUGIN_META is correctly defined

**Common Errors:**
- `import_failed`: Python import error (missing package or syntax error)
- `contract_violation`: Plugin missing required functions (register, PLUGIN_META)
- `missing_dependency`: Required plugin not available
- `circular_dependency`: Dependency cycle detected

### Problem 4: All Plugins Have Dependencies

**Symptom:**
```
⚠️  No root plugins found (all plugins have dependencies)
```

**Solution:**
This indicates a systemic issue:
1. Every plugin lists dependencies
2. Likely a circular dependency chain
3. At least one plugin should have `depends: []`

**Fix:**
```python
# Identify your foundation plugins (no external dependencies)
# These should have depends: []

PLUGIN_META = {
    "name": "database",  # Foundation plugin
    "depends": [],       # No dependencies
}
```

## Enhanced Error Messages

### CircularDependencyError

Enhanced with actionable fix instructions:

```python
from src.cli_plugins.errors import CircularDependencyError

# Error includes:
# - Visual cycle representation: "alpha → beta → gamma → alpha"
# - Step-by-step fix instructions
# - Example fix based on the detected cycle
```

**Example Error:**
```
Circular dependency detected: alpha → beta → gamma → alpha

This circular dependency cannot be resolved. To fix:
1. Review the 'depends' field in PLUGIN_META for each plugin in the cycle
2. Remove or modify dependencies to break the cycle
3. Consider if all dependencies are actually required

Example fix: If alpha doesn't actually need gamma, remove that dependency.
```

### MissingDependencyError with fail_soft

Enhanced to distinguish required vs optional dependencies:

```python
from src.cli_plugins.errors import MissingDependencyError

# Hard fail (required dependency)
error = MissingDependencyError(
    plugin_name="beta",
    missing_dependencies=["alpha"],
    fail_soft=False  # Default: plugin cannot load
)

# Soft fail (optional dependency)
error = MissingDependencyError(
    plugin_name="beta",
    missing_dependencies=["metrics"],
    fail_soft=True  # Plugin loads with reduced functionality
)
```

**Hard Fail Message:**
```
Plugin 'beta' requires missing dependencies: alpha

The plugin cannot be loaded. To fix:
1. Install missing plugins: alpha
2. Check if plugins are in the correct directory (src/cli_plugins/)
3. Verify PLUGIN_META is correctly defined in each plugin
4. Ensure plugins are enabled (check CF_PLUGINS_ENABLED/CF_PLUGINS_DISABLED)
5. Remove 'beta' from depends list if dependency is not actually needed
```

**Soft Fail Message:**
```
Plugin 'beta' has missing optional dependencies: metrics

The plugin will load with reduced functionality.
To enable full functionality:
1. Install missing plugins: metrics
2. Check if plugins are in the correct directory (src/cli_plugins/)
3. Verify PLUGIN_META is correctly defined in each plugin
4. Ensure plugins are enabled (check CF_PLUGINS_ENABLED/CF_PLUGINS_DISABLED)
```

## API Reference

### visualize_dependency_graph()

```python
def visualize_dependency_graph(
    graph: dict[str, set[str]],
    plugin_map: dict[str, PluginRecord],
    max_depth: int = 10,
    show_orphans: bool = True,
    console: Optional[Console] = None,
) -> None:
    """Visualize plugin dependency graph as a Rich Tree."""
```

**Parameters:**

- `graph` (dict[str, set[str]]): Dependency graph mapping plugin name to set of dependencies
  - Returned by `build_dependency_graph()`
  - Format: `{"plugin_name": {"dep1", "dep2"}}`

- `plugin_map` (dict[str, PluginRecord]): Mapping of plugin name to PluginRecord
  - Also returned by `build_dependency_graph()`
  - Contains plugin metadata and status

- `max_depth` (int, optional): Maximum tree depth to prevent infinite recursion
  - Default: 10
  - Use lower values for large ecosystems
  - Prevents stack overflow with circular dependencies

- `show_orphans` (bool, optional): Whether to show plugins with unresolved dependencies
  - Default: True
  - Set to False to hide orphaned plugins section

- `console` (Console, optional): Rich Console instance
  - Default: Creates new Console()
  - Pass custom console for testing or custom output

**Returns:** None (prints to console)

**Raises:** None (errors are displayed in the visualization)

### build_dependency_graph()

```python
def build_dependency_graph(
    plugins: list[PluginRecord]
) -> tuple[dict[str, set[str]], dict[str, PluginRecord]]:
    """Build dependency graph from plugin records."""
```

**Parameters:**
- `plugins` (list[PluginRecord]): List of discovered plugin records

**Returns:**
- `tuple[dict, dict]`: (graph, plugin_map)
  - `graph`: Dependency graph
  - `plugin_map`: Plugin name to record mapping

## Integration with Development Workflow

### During Development

```python
# Check dependencies after adding new plugin
from src.cli_plugins import discover_plugins, build_dependency_graph, visualize_dependency_graph

plugins = discover_plugins()
graph, plugin_map = build_dependency_graph(plugins)
visualize_dependency_graph(graph, plugin_map)

# Verify:
# - New plugin appears in tree
# - Dependencies correctly shown
# - No circular references introduced
```

### In CI/CD Pipeline

```python
# Validate dependency graph in tests
def test_no_circular_dependencies():
    plugins = discover_plugins()
    graph, plugin_map = build_dependency_graph(plugins)

    # This will raise if circular dependency exists
    from src.cli_plugins.registration import topological_sort_plugins
    sorted_names, _ = topological_sort_plugins(plugins)

    # Visualize for debugging
    visualize_dependency_graph(graph, plugin_map)
```

### For Documentation

```bash
# Generate dependency visualization for docs
python -c "
from src.cli_plugins import discover_plugins, build_dependency_graph, visualize_dependency_graph
plugins = discover_plugins()
graph, plugin_map = build_dependency_graph(plugins)
visualize_dependency_graph(graph, plugin_map)
" > docs/plugin-dependencies.txt
```

## Best Practices

### 1. Regular Visualization

Run visualization regularly during development:

```bash
# Create helper script: scripts/visualize_plugins.py
from src.cli_plugins import discover_plugins, build_dependency_graph, visualize_dependency_graph

plugins = discover_plugins()
graph, plugin_map = build_dependency_graph(plugins)
visualize_dependency_graph(graph, plugin_map)
```

```bash
# Run it
python scripts/visualize_plugins.py
```

### 2. Keep Dependency Depth Low

- Aim for max depth of 3-4 levels
- Deep dependency chains are fragile
- Consider refactoring if depth > 5

### 3. Document Dependencies

```python
# In PLUGIN_META
PLUGIN_META = {
    "name": "tasks",
    "depends": ["database", "auth"],
    "description": "Task management (requires database for storage, auth for permissions)",
}
```

### 4. Use Fail-Soft for Optional Dependencies

```python
# Example: Plugin works without metrics, but provides more features with it
try:
    from .plugin_metrics import record_metric
    HAS_METRICS = True
except ImportError:
    HAS_METRICS = False

# In register()
if not HAS_METRICS:
    # Raise soft fail warning
    raise MissingDependencyError(
        plugin_name="tasks",
        missing_dependencies=["metrics"],
        fail_soft=True,
    )
```

## See Also

- [Plugin Error Handling](plugin-error-handling.md)
- [Plugin Development Guide](plugin-development.md)
- [Plugin Discovery Guide](plugin-discovery.md)
- [Plugin Enable/Disable Mechanism](plugin-enable-disable.md)
