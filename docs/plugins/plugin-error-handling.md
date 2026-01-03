# Plugin Error Handling Guide

Comprehensive guide to error handling in the plugin infrastructure (T-CFCORE-PLUGIN_INFRASTRUCTURE-005).

## Table of Contents

1. [Overview](#overview)
2. [Exception Hierarchy](#exception-hierarchy)
3. [Error Reporting](#error-reporting)
4. [Recovery Mechanisms](#recovery-mechanisms)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

## Overview

The plugin infrastructure provides robust error handling to ensure system stability even when plugins fail. Key features:

- **Comprehensive exception hierarchy** with rich context capture
- **Rich CLI error formatting** with suggested actions
- **Automatic recovery** via retry and reload mechanisms
- **Health monitoring** to track plugin reliability
- **Graceful degradation** - system continues despite plugin failures

## Exception Hierarchy

All plugin errors inherit from `PluginError` base class:

```
PluginError (base)
├── PluginDiscoveryError (import/metadata failures)
├── PluginRegistrationError
│   ├── CircularDependencyError
│   └── MissingDependencyError
├── PluginConfigurationError
│   ├── ConfigValidationError
│   └── ConfigLoadError
├── PluginLifecycleError (setup/teardown failures)
├── PluginExecutionError (command execution failures)
│   ├── PluginTimeoutError (operation timeouts)
│   └── PluginResourceError (resource allocation/cleanup)
└── PluginDependencyError (dependency resolution failures)
```

### Base PluginError

All plugin errors capture rich context:

```python
from src.cli_plugins import PluginError

try:
    # Plugin operation
    plugin.execute()
except Exception as e:
    raise PluginError(
        "Operation failed",
        plugin_name="my_plugin",
        context={"operation": "execute", "user": "admin"},
        original_error=e,
    )
```

**Attributes:**
- `message`: Human-readable error message
- `plugin_name`: Name of plugin that caused error
- `context`: Dictionary with additional error context
- `original_error`: Underlying exception if wrapping another error
- `_traceback`: Captured traceback for debugging

### Discovery Errors

Raised when plugin discovery fails:

```python
from src.cli_plugins import PluginDiscoveryError

raise PluginDiscoveryError(
    "Failed to import plugin",
    plugin_name="broken_plugin",
    file_path="/path/to/plugin.py",
    original_error=import_error,
)
```

**Common causes:**
- Missing plugin file
- Python syntax errors
- Missing PLUGIN_META
- Invalid module structure

### Registration Errors

Raised when plugin registration fails:

```python
from src.cli_plugins import (
    CircularDependencyError,
    MissingDependencyError,
)

# Circular dependency
raise CircularDependencyError(["A", "B", "C", "A"])

# Missing dependency
raise MissingDependencyError(
    "plugin_b",
    ["plugin_a", "plugin_c"],
)
```

### Configuration Errors

Raised when configuration validation or loading fails:

```python
from src.cli_plugins import (
    ConfigValidationError,
    ConfigLoadError,
)

# Validation error
raise ConfigValidationError(
    "Invalid timeout value",
    plugin_name="my_plugin",
    validation_errors=[{"field": "timeout", "error": "must be positive"}],
)

# Load error
raise ConfigLoadError(
    "Config file not found",
    file_path="/path/to/config.yaml",
)
```

### Execution Errors

Raised when plugin commands fail during runtime:

```python
from src.cli_plugins import (
    PluginExecutionError,
    PluginTimeoutError,
    PluginResourceError,
)

# Generic execution error
raise PluginExecutionError(
    "Command failed",
    plugin_name="my_plugin",
    command="process_data",
    original_error=runtime_error,
)

# Timeout
raise PluginTimeoutError(
    plugin_name="my_plugin",
    timeout=30,
    command="slow_operation",
)

# Resource error
raise PluginResourceError(
    "Database connection failed",
    plugin_name="my_plugin",
    resource_type="database",
)
```

## Error Reporting

### Rich CLI Formatting

The error reporting system uses Rich library for beautiful CLI output:

```python
from src.cli_plugins import print_plugin_error, PluginError

try:
    plugin.execute()
except PluginError as e:
    print_plugin_error(
        e,
        show_traceback=True,  # Include full traceback
        show_context=True,    # Include error context
        show_suggestions=True, # Include suggested actions
    )
```

**Output includes:**
- Color-coded error type (yellow for warnings, red for critical)
- Plugin name and error message
- Error context table
- Suggested remediation actions
- Optional traceback for debugging

### Error Aggregation

For batch operations, use `ErrorReporter` to collect and report multiple errors:

```python
from src.cli_plugins import ErrorReporter, PluginError

reporter = ErrorReporter()

for plugin in plugins:
    try:
        plugin.setup()
    except PluginError as e:
        reporter.add_error(e)

# Print summary grouped by plugin
if reporter.has_errors():
    reporter.print_summary(group_by="plugin")
```

**Grouping options:**
- `group_by="plugin"`: Group by plugin name
- `group_by="type"`: Group by error type
- `group_by="none"`: List all errors sequentially

### Custom Error Messages

The system provides context-aware suggested actions:

```python
from src.cli_plugins.error_reporting import get_suggested_actions

error = PluginTimeoutError("slow_plugin", timeout=30)
actions = get_suggested_actions(error)

# Actions might include:
# - "Increase timeout setting (current: 30s)"
# - "Check if command 'operation' is hanging"
# - "Review plugin logs for slow operations"
```

## Recovery Mechanisms

### Retry with Exponential Backoff

Automatically retry failed operations:

```python
from src.cli_plugins import retry_with_backoff

result = retry_with_backoff(
    func=lambda: plugin.connect_to_service(),
    max_retries=3,
    initial_delay=1.0,      # Start with 1 second
    max_delay=60.0,         # Cap at 60 seconds
    backoff_factor=2.0,     # Double delay each retry
    exceptions=(ConnectionError,),  # Only retry these errors
)
```

**Retry behavior:**
1. First attempt: Immediate execution
2. First retry: Wait 1 second
3. Second retry: Wait 2 seconds
4. Third retry: Wait 4 seconds
5. If all fail: Re-raise last exception

### Plugin Reload

Reload a failed plugin:

```python
from src.cli_plugins import reload_plugin

# Reload plugin after error
success = reload_plugin(
    plugin_name="my_plugin",
    app=typer_app,
    context=shared_context,
)

if success:
    print("Plugin reloaded successfully")
else:
    print("Plugin reload failed")
```

**Reload process:**
1. Call plugin's `teardown()` if it exists
2. Reload module from disk using `importlib.reload()`
3. Call plugin's `setup()` if it exists
4. Re-register plugin commands

### Health Monitoring

Track plugin health over time:

```python
from src.cli_plugins import PluginHealthChecker

checker = PluginHealthChecker(
    error_threshold=3,              # Unhealthy after 3 errors
    error_window=timedelta(minutes=5),  # Within 5 minutes
)

# Record errors
checker.record_error("my_plugin", "Connection timeout")

# Record success
checker.record_success("my_plugin")

# Check health
result = checker.check_plugin("my_plugin")
if not result.is_healthy:
    print(f"Plugin unhealthy: {result.last_error}")
    print(f"Error count: {result.error_count}")
    print(f"Checks failed: {result.checks_failed}")
```

**Health checks:**
- Error count below threshold
- Recent successful operation
- Plugin module loaded

### Automatic Recovery

The system can automatically recover from certain errors:

```python
from src.cli_plugins import attempt_auto_recovery

try:
    plugin.execute()
except PluginError as e:
    recovered = attempt_auto_recovery(
        plugin_name="my_plugin",
        error=e,
        app=typer_app,
        context=shared_context,
        health_checker=checker,  # Optional
    )

    if not recovered:
        # Manual intervention needed
        print_plugin_error(e)
```

**Recovery strategies:**
- **Execution errors**: Retry with backoff (2 attempts)
- **Lifecycle errors**: Reload plugin
- **Other errors**: Log and return False

## Best Practices

### 1. Use Specific Exception Types

```python
# Good - specific error type
raise PluginTimeoutError("my_plugin", timeout=30, command="fetch_data")

# Avoid - generic error
raise PluginError("Timeout after 30 seconds")
```

### 2. Provide Rich Context

```python
# Good - rich context
raise PluginExecutionError(
    "Data processing failed",
    plugin_name="processor",
    command="process_batch",
    original_error=processing_error,
)

# Avoid - minimal context
raise PluginExecutionError("Processing failed", plugin_name="processor")
```

### 3. Handle Errors Gracefully

```python
from src.cli_plugins import PluginError, print_plugin_error

try:
    result = plugin.process_data(data)
except PluginError as e:
    # Log error with full context
    print_plugin_error(e, show_traceback=True)

    # Continue with fallback behavior
    result = fallback_processor(data)
except Exception as e:
    # Wrap unexpected errors
    raise PluginExecutionError(
        "Unexpected error",
        plugin_name="processor",
        original_error=e,
    )
```

### 4. Use Health Checking

```python
# Monitor plugin health
checker = PluginHealthChecker()

for item in batch:
    try:
        plugin.process(item)
        checker.record_success("processor")
    except PluginError as e:
        checker.record_error("processor", str(e))

        # Check if plugin is failing too often
        health = checker.check_plugin("processor")
        if not health.is_healthy:
            # Disable plugin or alert operators
            disable_plugin("processor")
            break
```

### 5. Leverage Auto-Recovery

```python
from src.cli_plugins import BasePlugin, PluginExecutionError

class MyPlugin(BasePlugin):
    def on_error(self, exc: Exception) -> None:
        """Override error callback for custom handling."""
        if isinstance(exc, PluginExecutionError):
            # Attempt auto-recovery
            from src.cli_plugins import attempt_auto_recovery
            attempt_auto_recovery(
                self.plugin_name,
                exc,
                self.app,
                self.context,
            )
        else:
            # Re-raise non-plugin errors
            raise
```

## Troubleshooting

### Common Error Scenarios

#### Scenario 1: Plugin Won't Load

**Symptoms:**
- `PluginDiscoveryError: Failed to import plugin`
- Plugin not appearing in `cf plugins list`

**Solutions:**
1. Check plugin file exists: `ls src/cli_plugins/plugin_*.py`
2. Verify Python syntax: `python -m py_compile plugin_name.py`
3. Check PLUGIN_META is defined
4. Review import errors in logs

#### Scenario 2: Circular Dependency

**Symptoms:**
- `CircularDependencyError: A → B → C → A`
- Plugins register in unexpected order

**Solutions:**
1. Review PLUGIN_META depends lists
2. Break circular dependencies by removing unnecessary deps
3. Consider restructuring plugin relationships

#### Scenario 3: Plugin Crashes Frequently

**Symptoms:**
- Multiple `PluginExecutionError` in logs
- Health checker reports plugin unhealthy

**Solutions:**
1. Check plugin logs for root cause
2. Use retry with backoff for transient errors
3. Reload plugin: `cf plugins reload <name>`
4. Review plugin resource usage
5. Check external dependencies (database, API)

#### Scenario 4: Configuration Invalid

**Symptoms:**
- `ConfigValidationError: Invalid configuration`
- Plugin fails during setup()

**Solutions:**
1. Validate config: `cf plugins config validate <name>`
2. Check YAML syntax
3. Review required settings in plugin docs
4. Check environment variables

### Debugging Tips

#### 1. Enable Verbose Error Output

```python
# Show full traceback
print_plugin_error(error, show_traceback=True)
```

#### 2. Check Error Context

```python
# Get full error context
context = error.get_full_context()
print(context)
```

#### 3. Monitor Health Over Time

```python
# Check all unhealthy plugins
unhealthy = checker.get_unhealthy_plugins()
for plugin_name in unhealthy:
    result = checker.check_plugin(plugin_name)
    print(f"{plugin_name}: {result.checks_failed}")
```

#### 4. Review Recent Errors

```python
# Get recent errors for a plugin
errors = checker.get_recent_errors(
    "my_plugin",
    window=timedelta(hours=1),
)
for timestamp, error_msg in errors:
    print(f"{timestamp}: {error_msg}")
```

## API Reference

### Core Exceptions

- `PluginError(message, plugin_name, context, original_error)`
- `PluginDiscoveryError(message, plugin_name, file_path, original_error)`
- `CircularDependencyError(cycle, message)`
- `MissingDependencyError(plugin_name, missing_dependencies, message)`
- `ConfigValidationError(message, plugin_name, validation_errors)`
- `ConfigLoadError(message, file_path, original_error)`
- `PluginLifecycleError(message, plugin_name, phase, original_error)`
- `PluginExecutionError(message, plugin_name, command, original_error)`
- `PluginTimeoutError(plugin_name, timeout, command)`
- `PluginResourceError(message, plugin_name, resource_type, original_error)`

### Error Reporting

- `print_plugin_error(error, show_traceback, show_context, show_suggestions)`
- `ErrorReporter()` - Error aggregation
  - `add_error(error)`
  - `has_errors() -> bool`
  - `error_count() -> int`
  - `print_summary(show_traceback, group_by)`
  - `clear()`

### Recovery

- `retry_with_backoff(func, max_retries, initial_delay, max_delay, backoff_factor, exceptions)`
- `reload_plugin(plugin_name, app, context, module_name)`
- `PluginHealthChecker(error_threshold, error_window)`
  - `record_error(plugin_name, error)`
  - `record_success(plugin_name)`
  - `check_plugin(plugin_name) -> HealthCheckResult`
  - `get_unhealthy_plugins() -> List[str]`
  - `clear_history(plugin_name)`
- `attempt_auto_recovery(plugin_name, error, app, context, health_checker)`

## See Also

- [Plugin Development Guide](plugin-development.md)
- [Configuration Management](configuration-management.md)
- [BasePlugin Reference](baseplugin-reference.md)
