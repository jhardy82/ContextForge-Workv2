# Plugin Enable/Disable Mechanism

Comprehensive guide to controlling which plugins are loaded at runtime using environment variables (T-CFCORE-PLUGIN_INFRASTRUCTURE-008).

## Table of Contents

1. [Overview](#overview)
2. [Environment Variables](#environment-variables)
3. [Precedence Rules](#precedence-rules)
4. [Usage Examples](#usage-examples)
5. [Case-Insensitive Matching](#case-insensitive-matching)
6. [Integration with Discovery](#integration-with-discovery)
7. [Logging](#logging)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Overview

The plugin infrastructure provides runtime control over which plugins are loaded via environment variables. This allows you to:

- **Disable specific plugins** without modifying code (denylist mode)
- **Enable only specific plugins** for minimal environments (allowlist mode)
- **Override plugin defaults** without changing PLUGIN_META
- **Test plugin isolation** by disabling dependencies

**Key Features:**
- Environment variable-based filtering
- Case-insensitive plugin name matching
- Precedence rules for conflict resolution
- Comprehensive logging of enable/disable decisions
- Integration with plugin discovery and registration

## Environment Variables

### CF_PLUGINS_DISABLED (Denylist Mode)

Disable specific plugins by name:

```bash
# Disable single plugin
export CF_PLUGINS_DISABLED="tasks"

# Disable multiple plugins (comma-separated)
export CF_PLUGINS_DISABLED="tasks,sprints,projects"

# Whitespace is ignored
export CF_PLUGINS_DISABLED=" tasks , sprints , projects "
```

**Behavior:**
- Plugins in the list are **disabled**
- Plugins not in the list follow their `enabled_by_default` setting
- Empty value means no plugins are disabled

### CF_PLUGINS_ENABLED (Allowlist Mode)

Enable only specific plugins:

```bash
# Enable single plugin
export CF_PLUGINS_ENABLED="tasks"

# Enable multiple plugins (comma-separated)
export CF_PLUGINS_ENABLED="tasks,sprints,projects"

# Whitespace is ignored
export CF_PLUGINS_ENABLED=" tasks , sprints , projects "
```

**Behavior:**
- **Only plugins in the list are enabled**
- Plugins not in the list are disabled
- Empty value means fall back to `enabled_by_default`

## Precedence Rules

When both environment variables and `enabled_by_default` are present, the following precedence applies (highest to lowest):

1. **CF_PLUGINS_ENABLED (allowlist)** - If set, ONLY listed plugins are enabled
2. **CF_PLUGINS_DISABLED (denylist)** - If set, listed plugins are disabled
3. **enabled_by_default** - Plugin's PLUGIN_META flag

### Precedence Examples

```python
# Example 1: Allowlist takes precedence
# CF_PLUGINS_ENABLED="tasks"
# CF_PLUGINS_DISABLED="tasks,sprints"
# Result:
#   - tasks: ENABLED (in allowlist, despite denylist)
#   - sprints: DISABLED (not in allowlist)
#   - projects: DISABLED (not in allowlist)

# Example 2: Denylist overrides enabled_by_default
# CF_PLUGINS_DISABLED="tasks"
# tasks PLUGIN_META: enabled_by_default=True
# Result: tasks DISABLED (denylist takes precedence)

# Example 3: enabled_by_default used when no env vars
# (no env vars set)
# tasks PLUGIN_META: enabled_by_default=True
# sprints PLUGIN_META: enabled_by_default=False
# Result:
#   - tasks: ENABLED
#   - sprints: DISABLED
```

## Usage Examples

### Example 1: Development Environment

Disable resource-intensive plugins during development:

```bash
# Disable database and metrics plugins
export CF_PLUGINS_DISABLED="database,metrics,telemetry"

# Run CLI
cf tasks list
```

### Example 2: Minimal Production Environment

Enable only essential plugins for a lightweight deployment:

```bash
# Enable only core plugins
export CF_PLUGINS_ENABLED="tasks,sprints,projects"

# Run CLI
cf server start
```

### Example 3: Testing Plugin Isolation

Test a plugin without its dependencies:

```bash
# Disable all plugins except the one being tested
export CF_PLUGINS_ENABLED="my_plugin"

# Run tests
pytest tests/test_my_plugin.py
```

### Example 4: Temporary Override

Temporarily disable a plugin for debugging:

```bash
# One-time disable for single command
CF_PLUGINS_DISABLED="problematic_plugin" cf tasks list

# Or use shell session
export CF_PLUGINS_DISABLED="problematic_plugin"
cf tasks list
cf sprints show
unset CF_PLUGINS_DISABLED
```

### Example 5: Docker/Container Environments

Set environment variables in Docker:

```dockerfile
# Dockerfile
FROM python:3.9

# Disable unnecessary plugins in container
ENV CF_PLUGINS_DISABLED="local_file_watcher,desktop_notifications"

COPY . /app
WORKDIR /app
CMD ["python", "cf_cli.py", "server", "start"]
```

Or in docker-compose.yaml:

```yaml
services:
  cf_cli:
    image: cf_cli:latest
    environment:
      CF_PLUGINS_ENABLED: "tasks,sprints,projects,database"
```

## Case-Insensitive Matching

Plugin names are matched **case-insensitively** for user convenience:

```bash
# All of these disable the "tasks" plugin:
export CF_PLUGINS_DISABLED="tasks"
export CF_PLUGINS_DISABLED="Tasks"
export CF_PLUGINS_DISABLED="TASKS"
export CF_PLUGINS_DISABLED="tAsKs"

# Mixed case in comma-separated list also works:
export CF_PLUGINS_DISABLED="Tasks,SPRINTS,PrOjEcTs"
```

**Implementation Detail:**
- Plugin names are converted to lowercase before comparison
- Original plugin name preserved in PLUGIN_META and logs
- Case-insensitive matching applies to both env vars and PLUGIN_META

**Example:**
```python
# In PLUGIN_META
PLUGIN_META = {"name": "TaskManager", ...}

# User can disable with any case:
# CF_PLUGINS_DISABLED="taskmanager"
# CF_PLUGINS_DISABLED="TaskManager"
# CF_PLUGINS_DISABLED="TASKMANAGER"
# All will successfully disable the plugin
```

## Integration with Discovery

The enable/disable mechanism is integrated into the plugin discovery and registration pipeline:

```
1. discover_plugins()
   ↓
   Finds all plugin_*.py files

2. For each plugin:
   ↓
   Load PLUGIN_META

3. _should_enable_plugin(name, enabled_by_default)
   ↓
   Check CF_PLUGINS_ENABLED (allowlist)
   Check CF_PLUGINS_DISABLED (denylist)
   Check enabled_by_default flag

4. If disabled:
   ↓
   Skip plugin registration
   Log reason for skipping

5. If enabled:
   ↓
   Continue with registration
```

**Code Reference:**

From [src/cli_plugins/__init__.py:472-482](../src/cli_plugins/__init__.py#L472-L482):

```python
# v2.0 filtering: Check enable/disable
should_enable, enable_reason = _should_enable_plugin(
    rec.name, rec.enabled_by_default
)
if not should_enable:
    rec.error = f"disabled: {enable_reason}"
    ulog(
        "plugin_skip_disabled",
        plugin=rec.name,
        reason=enable_reason,
    )
    continue  # Skip this plugin
```

## Logging

All enable/disable decisions are logged using unified logging (`ulog()`):

### Log Events

**plugin_enabled** - Plugin enabled for registration:
```json
{
  "action": "plugin_enabled",
  "plugin": "tasks",
  "reason": "allowlist",
  "env_var": "CF_PLUGINS_ENABLED"
}
```

**plugin_disabled** - Plugin disabled, skipping registration:
```json
{
  "action": "plugin_disabled",
  "plugin": "sprints",
  "reason": "not_in_allowlist",
  "env_var": "CF_PLUGINS_ENABLED"
}
```

**plugin_skip_disabled** - Plugin skipped during discovery:
```json
{
  "action": "plugin_skip_disabled",
  "plugin": "projects",
  "reason": "disabled via CF_PLUGINS_DISABLED"
}
```

### Logging Reasons

| Reason | Description |
|--------|-------------|
| `allowlist` | Plugin in CF_PLUGINS_ENABLED |
| `not_in_allowlist` | Plugin not in CF_PLUGINS_ENABLED |
| `denylist` | Plugin in CF_PLUGINS_DISABLED |
| `enabled_by_default_true` | Plugin has enabled_by_default=True |
| `enabled_by_default_false` | Plugin has enabled_by_default=False |

### Viewing Logs

```bash
# View all plugin enable/disable decisions
cf logs filter --action plugin_enabled,plugin_disabled

# View only disabled plugins
cf logs filter --action plugin_disabled

# View logs for specific plugin
cf logs filter --plugin tasks
```

## Best Practices

### 1. Use Allowlist for Production

In production environments, explicitly enable only required plugins:

```bash
# Good - explicit allowlist
export CF_PLUGINS_ENABLED="tasks,sprints,projects,database,auth"

# Avoid - relying on enabled_by_default
# (harder to track which plugins are actually running)
```

### 2. Use Denylist for Development

In development, disable problematic plugins temporarily:

```bash
# Good - disable specific problem plugin during debugging
export CF_PLUGINS_DISABLED="flaky_plugin"

# Avoid - disabling many plugins with allowlist
# (easier to miss dependencies)
```

### 3. Document Plugin Dependencies

When disabling plugins, be aware of dependencies:

```python
# In PLUGIN_META
PLUGIN_META = {
    "name": "tasks",
    "depends": ["database", "auth"],  # Tasks depends on database and auth
}

# Disabling database will cause tasks to fail
# CF_PLUGINS_DISABLED="database"  # Bad - breaks tasks plugin
```

### 4. Test with Minimal Plugin Sets

Regularly test with minimal plugin configurations:

```bash
# Test with only core plugins
CF_PLUGINS_ENABLED="tasks,sprints" pytest tests/

# Test with plugins disabled
CF_PLUGINS_DISABLED="optional_plugin" pytest tests/
```

### 5. Use Descriptive Plugin Names

Choose plugin names that are easy to remember and type:

```python
# Good
PLUGIN_META = {"name": "database_postgres"}

# Avoid
PLUGIN_META = {"name": "db_pg_v2_final_FIXED"}
```

## Troubleshooting

### Problem 1: Plugin Not Loading

**Symptoms:**
- Plugin not appearing in `cf plugins list`
- Commands missing despite plugin file present

**Solution:**
1. Check if plugin is in denylist:
   ```bash
   echo $CF_PLUGINS_DISABLED
   ```

2. Check if allowlist is active:
   ```bash
   echo $CF_PLUGINS_ENABLED
   # If set, plugin must be in this list
   ```

3. Check plugin logs:
   ```bash
   cf logs filter --plugin my_plugin
   ```

4. Verify plugin name matches (case-insensitive):
   ```bash
   # These are equivalent:
   CF_PLUGINS_DISABLED="TaskManager"
   CF_PLUGINS_DISABLED="taskmanager"
   ```

### Problem 2: Allowlist Not Working

**Symptoms:**
- CF_PLUGINS_ENABLED set but plugins still loading
- More plugins enabled than expected

**Solution:**
1. Check environment variable is actually set:
   ```bash
   echo $CF_PLUGINS_ENABLED
   ```

2. Verify no typos in plugin names:
   ```bash
   # Wrong - typo in name
   CF_PLUGINS_ENABLED="task,sprints"  # "task" != "tasks"

   # Correct
   CF_PLUGINS_ENABLED="tasks,sprints"
   ```

3. Check for extra whitespace:
   ```bash
   # All valid - whitespace ignored
   CF_PLUGINS_ENABLED="tasks,sprints"
   CF_PLUGINS_ENABLED=" tasks , sprints "
   CF_PLUGINS_ENABLED="tasks, sprints"
   ```

### Problem 3: Precedence Confusion

**Symptoms:**
- Plugin in both allowlist and denylist behaving unexpectedly

**Solution:**
Remember precedence: **allowlist > denylist > enabled_by_default**

```bash
# Both set
export CF_PLUGINS_ENABLED="tasks,sprints"
export CF_PLUGINS_DISABLED="tasks,projects"

# Result:
# - tasks: ENABLED (in allowlist, denylist ignored)
# - sprints: ENABLED (in allowlist)
# - projects: DISABLED (not in allowlist)
```

**Best Practice:** Don't use both env vars at the same time. Choose one:
- Use CF_PLUGINS_ENABLED for production (explicit allowlist)
- Use CF_PLUGINS_DISABLED for development (temporary disables)

### Problem 4: Case Sensitivity Issues

**Symptoms:**
- Plugin not disabled despite being in denylist

**Solution:**
Plugin name matching is case-insensitive, but check for typos:

```bash
# All of these disable "TaskManager" plugin:
CF_PLUGINS_DISABLED="taskmanager"  # OK
CF_PLUGINS_DISABLED="TaskManager"  # OK
CF_PLUGINS_DISABLED="TASKMANAGER"  # OK

# This does NOT work (typo):
CF_PLUGINS_DISABLED="TaskManagar"  # Typo - won't match
```

### Problem 5: Empty Environment Variable

**Symptoms:**
- Unexpected behavior when env var set to empty string

**Solution:**
Empty env vars are ignored (fall back to enabled_by_default):

```bash
# Empty allowlist - uses enabled_by_default
export CF_PLUGINS_ENABLED=""

# Empty denylist - no plugins disabled
export CF_PLUGINS_DISABLED=""

# To actually disable all plugins:
export CF_PLUGINS_ENABLED="none"  # Only enable plugin named "none"
```

## API Reference

### Functions

#### `_should_enable_plugin(plugin_name, enabled_by_default)`

Determine if plugin should be enabled based on environment variables.

**Parameters:**
- `plugin_name` (str): Name of the plugin
- `enabled_by_default` (bool): Plugin's enabled_by_default flag

**Returns:**
- `tuple[bool, str | None]`: (should_enable, reason)

**Example:**
```python
from src.cli_plugins import _should_enable_plugin

should_enable, reason = _should_enable_plugin("tasks", enabled_by_default=True)
if should_enable:
    print(f"Plugin enabled: {reason}")
else:
    print(f"Plugin disabled: {reason}")
```

### Environment Variables

| Variable | Type | Description |
|----------|------|-------------|
| `CF_PLUGINS_DISABLED` | str | Comma-separated list of plugins to disable |
| `CF_PLUGINS_ENABLED` | str | Comma-separated list of plugins to enable (disables all others) |

**Access in Python:**
```python
import os
from src.cli_plugins import ENV_PLUGINS_DISABLED, ENV_PLUGINS_ENABLED

# Read current settings
disabled = os.environ.get(ENV_PLUGINS_DISABLED, "")
enabled = os.environ.get(ENV_PLUGINS_ENABLED, "")

print(f"Disabled plugins: {disabled}")
print(f"Enabled plugins: {enabled}")
```

## See Also

- [Plugin Discovery Guide](plugin-discovery.md)
- [Plugin Configuration](configuration-management.md)
- [Plugin Error Handling](plugin-error-handling.md)
- [Plugin Development Guide](plugin-development.md)
