# Async Plugin Development Guide

## Table of Contents
1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Async Registration](#async-registration)
4. [Async Lifecycle Hooks](#async-lifecycle-hooks)
5. [Parallel vs Sequential Loading](#parallel-vs-sequential-loading)
6. [Performance Optimization](#performance-optimization)
7. [Migration Guide](#migration-guide)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The CF-CORE plugin system supports both synchronous and asynchronous plugin registration, enabling:

- **Parallel Loading**: Independent plugins load concurrently for faster startup
- **Async Operations**: Plugins can perform async I/O during initialization
- **Backward Compatibility**: Existing sync plugins work unchanged
- **Dependency Ordering**: Topological sorting ensures correct load order

### Key Features

- ✅ **Auto-detection**: System detects sync vs async `register()` functions
- ✅ **Batched Loading**: Independent plugins grouped into parallel batches
- ✅ **Performance**: 4x+ faster loading for large plugin sets
- ✅ **Type Safety**: Full type hints with `typing` module
- ✅ **Error Handling**: Graceful degradation on async failures

---

## Quick Start

### Simple Async Plugin

```python
"""my_async_plugin/__init__.py"""
import asyncio
from typing import Any
import typer
from src.cli_plugins.base import BasePlugin


# 1. Define async register function
async def register(app: typer.Typer, shared: dict[str, Any]) -> BasePlugin:
    """Async plugin registration."""

    # 2. Perform async initialization
    await asyncio.sleep(0.1)  # Simulate async I/O

    # 3. Create plugin instance
    plugin = MyAsyncPlugin(app, shared)

    # 4. Async setup
    await plugin.setup_async()

    return plugin


class MyAsyncPlugin(BasePlugin):
    """Example async plugin."""

    async def setup_async(self) -> None:
        """Async initialization logic."""
        # Connect to database, load config, etc.
        await self._connect_to_database()

    async def teardown_async(self) -> None:
        """Async cleanup logic."""
        await self._close_database()

    async def _connect_to_database(self) -> None:
        """Connect to async database."""
        # Your async database connection code
        pass

    async def _close_database(self) -> None:
        """Close database connection."""
        # Your async cleanup code
        pass


# PLUGIN_META for discovery
PLUGIN_META = {
    "name": "my_async_plugin",
    "version": "2.0.0",
    "enabled": True,
    "dependencies": [],
}
```

---

## Async Registration

### Registration Function Signature

The plugin system supports two signatures:

#### Synchronous (Legacy)
```python
def register(app: typer.Typer, shared: dict[str, Any]) -> BasePlugin:
    """Sync registration."""
    plugin = MyPlugin(app, shared)
    plugin.setup()  # Synchronous setup
    return plugin
```

#### Asynchronous (Recommended)
```python
async def register(app: typer.Typer, shared: dict[str, Any]) -> BasePlugin:
    """Async registration."""
    plugin = MyPlugin(app, shared)
    await plugin.setup_async()  # Async setup
    return plugin
```

### Auto-Detection

The system uses `inspect.iscoroutinefunction()` to detect async functions:

```python
from src.cli_plugins.registration import register_plugin_async

# Automatically handles both sync and async
plugin_instance = await register_plugin_async(
    plugin_record=record,
    app=app,
    shared_context=shared,
)
```

### Mixed Sync/Async Plugins

You can mix sync and async plugins in the same application:

```python
# plugins/sync_plugin.py
def register(app, shared):  # Sync
    return SyncPlugin(app, shared)

# plugins/async_plugin.py
async def register(app, shared):  # Async
    await asyncio.sleep(0.1)
    return AsyncPlugin(app, shared)
```

Both will work correctly with the registration system.

---

## Async Lifecycle Hooks

The `BasePlugin` class provides 5 async lifecycle hooks:

### 1. `setup_async()`

Called after plugin instantiation for async initialization.

```python
class DatabasePlugin(BasePlugin):
    async def setup_async(self) -> None:
        """Connect to database."""
        self.db_pool = await asyncpg.create_pool(
            host='localhost',
            database='mydb',
        )
        self.logger.info("Database pool created")
```

### 2. `teardown_async()`

Called during shutdown for async cleanup.

```python
class DatabasePlugin(BasePlugin):
    async def teardown_async(self) -> None:
        """Close database connections."""
        if self.db_pool:
            await self.db_pool.close()
            self.logger.info("Database pool closed")
```

### 3. `on_enable_async()`

Called when plugin is enabled at runtime.

```python
class CachePlugin(BasePlugin):
    async def on_enable_async(self) -> None:
        """Start cache refresh task."""
        self.refresh_task = asyncio.create_task(
            self._refresh_cache_loop()
        )
```

### 4. `on_disable_async()`

Called when plugin is disabled at runtime.

```python
class CachePlugin(BasePlugin):
    async def on_disable_async(self) -> None:
        """Stop cache refresh task."""
        if self.refresh_task:
            self.refresh_task.cancel()
            try:
                await self.refresh_task
            except asyncio.CancelledError:
                pass
```

### 5. `on_reload_async()`

Called during hot reload (Sprint 2 - T-011).

```python
class ConfigPlugin(BasePlugin):
    async def on_reload_async(self) -> None:
        """Reload configuration files."""
        self.config = await self._load_config_async()
        self.logger.info("Configuration reloaded")
```

### Default Implementations

All async hooks have default (no-op) implementations:

```python
async def setup_async(self) -> None:
    """Default: no async setup."""
    pass
```

Override only the hooks you need.

---

## Parallel vs Sequential Loading

The plugin system supports two loading modes:

### Parallel Loading (Default, Recommended)

Independent plugins load concurrently:

```python
from src.cli_plugins.registration import load_and_register_ordered_async

plugins = await load_and_register_ordered_async(
    plugin_records=[alpha, beta, gamma],
    app=app,
    shared_context=shared,
    parallel=True,  # Default
)
```

**Performance**: 4x+ faster for large plugin sets

**Example**:
- Alpha, Beta (no dependencies) → Load in parallel
- Gamma (depends on Alpha, Beta) → Load after both complete

### Sequential Loading

Plugins load one at a time (useful for debugging):

```python
plugins = await load_and_register_ordered_async(
    plugin_records=[alpha, beta, gamma],
    app=app,
    shared_context=shared,
    parallel=False,
)
```

**When to Use**:
- Debugging registration issues
- Resource-constrained environments
- Plugins with side effects

### Batched Parallel Loading

The system automatically groups plugins into dependency-ordered batches:

```python
from src.cli_plugins.registration import topological_sort_batches

# Given dependencies: gamma → [alpha, beta]
batches = topological_sort_batches(plugins)
# Returns: [[alpha, beta], [gamma]]
```

**Batch 1** (parallel): alpha, beta
**Batch 2** (after Batch 1): gamma

---

## Performance Optimization

### Benchmarks (Sprint 2 - T-010)

Test: 5 independent plugins, 50ms async work each

| Mode | Time | Speedup |
|------|------|---------|
| Sequential | 250ms | 1.0x (baseline) |
| Parallel | 60ms | **4.2x faster** |

### Optimization Strategies

#### 1. Minimize Dependencies

```python
# Bad: Unnecessary dependency
PLUGIN_META = {
    "dependencies": ["logging", "config", "database"],  # Too many!
}

# Good: Only essential dependencies
PLUGIN_META = {
    "dependencies": ["config"],  # Just what you need
}
```

More dependencies = less parallelism.

#### 2. Use Async I/O

```python
# Bad: Blocking I/O
def register(app, shared):
    time.sleep(0.5)  # Blocks entire event loop!
    return Plugin(app, shared)

# Good: Async I/O
async def register(app, shared):
    await asyncio.sleep(0.5)  # Allows other tasks to run
    return Plugin(app, shared)
```

#### 3. Defer Heavy Work

```python
async def register(app, shared):
    """Fast registration."""
    plugin = MyPlugin(app, shared)

    # Don't load heavy data during registration
    # plugin.data = await load_massive_dataset()  # ❌ Slow!

    # Instead, load on-demand
    plugin.data = None  # ✅ Fast registration
    return plugin

class MyPlugin(BasePlugin):
    async def _get_data(self):
        """Lazy load data."""
        if self.data is None:
            self.data = await load_massive_dataset()
        return self.data
```

#### 4. Profile Slow Plugins

```python
import time

async def register(app, shared):
    start = time.perf_counter()
    plugin = MyPlugin(app, shared)
    await plugin.setup_async()
    duration = time.perf_counter() - start

    if duration > 0.1:  # Warn if > 100ms
        logger.warning(f"Slow registration: {duration:.3f}s")

    return plugin
```

---

## Migration Guide

### Sync to Async Migration

#### Step 1: Change Function Signature

```python
# Before
def register(app: typer.Typer, shared: dict[str, Any]) -> BasePlugin:

# After
async def register(app: typer.Typer, shared: dict[str, Any]) -> BasePlugin:
```

#### Step 2: Convert Blocking to Async

```python
# Before
def register(app, shared):
    response = requests.get("https://api.example.com/config")  # Blocking!
    config = response.json()
    return MyPlugin(app, shared, config)

# After
async def register(app, shared):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.example.com/config") as response:
            config = await response.json()
    return MyPlugin(app, shared, config)
```

#### Step 3: Use Async Hooks

```python
# Before
class MyPlugin(BasePlugin):
    def __init__(self, app, shared):
        super().__init__(app, shared)
        self.db = connect_to_database()  # Sync in __init__

# After
class MyPlugin(BasePlugin):
    async def setup_async(self):
        """Async initialization."""
        self.db = await connect_to_database_async()
```

#### Step 4: Test Both Modes

```python
# Test parallel loading
plugins = await load_and_register_ordered_async(
    records, app, shared, parallel=True
)

# Test sequential loading (validates async correctness)
plugins = await load_and_register_ordered_async(
    records, app, shared, parallel=False
)
```

---

## Best Practices

### ✅ DO

1. **Use `async def register()`** for new plugins
2. **Minimize dependencies** for better parallelism
3. **Use async I/O** (aiohttp, asyncpg, aiofiles)
4. **Test both sync and async modes** during development
5. **Profile slow plugins** and optimize
6. **Document async requirements** in plugin README

### ❌ DON'T

1. **Don't block the event loop** with `time.sleep()` or blocking I/O
2. **Don't create circular dependencies** (prevents loading)
3. **Don't assume load order** (use dependencies instead)
4. **Don't perform heavy work in `register()`** (defer to first use)
5. **Don't forget cleanup** in `teardown_async()`

### Code Example: Best Practices

```python
"""best_practice_plugin/__init__.py - Example of async best practices."""
import asyncio
import logging
from typing import Any
import aiofiles
import typer
from src.cli_plugins.base import BasePlugin

logger = logging.getLogger(__name__)


async def register(app: typer.Typer, shared: dict[str, Any]) -> BasePlugin:
    """
    Async plugin registration following best practices.

    ✅ Uses async def
    ✅ Fast registration (< 100ms)
    ✅ Proper error handling
    """
    try:
        plugin = BestPracticePlugin(app, shared)
        await plugin.setup_async()
        return plugin
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise


class BestPracticePlugin(BasePlugin):
    """Example plugin following async best practices."""

    def __init__(self, app: typer.Typer, shared: dict[str, Any]):
        super().__init__(app, shared)
        self.config = None
        self.db_pool = None

    async def setup_async(self) -> None:
        """
        Async initialization.

        ✅ Uses async I/O
        ✅ Proper resource management
        """
        # Load config asynchronously
        async with aiofiles.open("config.yaml", mode="r") as f:
            content = await f.read()
            self.config = parse_yaml(content)

        # Initialize database pool
        self.db_pool = await create_pool(self.config["database"])

        logger.info("Plugin setup complete")

    async def teardown_async(self) -> None:
        """
        Async cleanup.

        ✅ Closes resources
        ✅ Handles errors gracefully
        """
        if self.db_pool:
            try:
                await self.db_pool.close()
                logger.info("Database pool closed")
            except Exception as e:
                logger.error(f"Error closing pool: {e}")

    async def on_reload_async(self) -> None:
        """
        Async reload.

        ✅ Reloads configuration
        ✅ Preserves state where needed
        """
        old_config = self.config
        try:
            async with aiofiles.open("config.yaml", mode="r") as f:
                content = await f.read()
                self.config = parse_yaml(content)
            logger.info("Configuration reloaded")
        except Exception as e:
            # Rollback on error
            self.config = old_config
            logger.error(f"Reload failed: {e}")
            raise


PLUGIN_META = {
    "name": "best_practice_plugin",
    "version": "2.0.0",
    "enabled": True,
    "dependencies": [],  # ✅ Minimal dependencies
}


def parse_yaml(content: str) -> dict:
    """Parse YAML content."""
    import yaml
    return yaml.safe_load(content)


async def create_pool(config: dict) -> Any:
    """Create async database pool."""
    # Your async pool creation code
    await asyncio.sleep(0.01)  # Simulate async work
    return {"pool": "mock"}
```

---

## Troubleshooting

### Common Issues

#### 1. "RuntimeError: This event loop is already running"

**Cause**: Calling `asyncio.run()` inside an async context.

```python
# ❌ Bad
async def register(app, shared):
    asyncio.run(some_async_function())  # Error!

# ✅ Good
async def register(app, shared):
    await some_async_function()
```

#### 2. Plugin Hangs During Registration

**Cause**: Blocking I/O in async function.

```python
# ❌ Bad - blocks event loop
async def register(app, shared):
    time.sleep(5)  # Blocks everything!

# ✅ Good
async def register(app, shared):
    await asyncio.sleep(5)
```

#### 3. Circular Dependency Error

**Cause**: Plugin A depends on B, B depends on A.

```python
# ❌ Bad
# plugin_a: dependencies = ["plugin_b"]
# plugin_b: dependencies = ["plugin_a"]

# ✅ Good - extract common logic to plugin_c
# plugin_a: dependencies = ["plugin_c"]
# plugin_b: dependencies = ["plugin_c"]
# plugin_c: dependencies = []
```

#### 4. Test Failures in CI

**Cause**: Timing-sensitive tests on slow CI runners.

```python
# ❌ Bad - brittle timing
async def test_performance():
    start = time.time()
    await load_plugins()
    assert time.time() - start < 0.1  # Fails on slow CI!

# ✅ Good - use relative comparisons
async def test_performance():
    sequential_time = await measure_sequential()
    parallel_time = await measure_parallel()
    assert parallel_time < sequential_time * 0.6  # 40%+ faster
```

### Debugging Tips

#### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now you'll see detailed registration logs
await load_and_register_ordered_async(...)
```

#### Test Sequentially First

```python
# Isolate issues by disabling parallelism
plugins = await load_and_register_ordered_async(
    records, app, shared,
    parallel=False,  # Easier to debug
)
```

#### Add Timing Instrumentation

```python
import time

async def register(app, shared):
    start = time.perf_counter()

    # Your registration code
    plugin = MyPlugin(app, shared)
    await plugin.setup_async()

    duration = time.perf_counter() - start
    print(f"Registration took {duration:.3f}s")

    return plugin
```

---

## See Also

- [Plugin Development Guide](plugin-development-guide.md) - General plugin concepts
- [Plugin Registration Contract](plugin-registration-contract.yaml) - Registration spec
- [Plugin Error Handling](plugin-error-handling.md) - Error patterns
- [Plugin Enable/Disable](plugin-enable-disable.md) - Runtime control

---

**Sprint 2 - T-010**: Async Plugin Support (5 SP)
**Last Updated**: 2025-11-17
**Status**: ✅ Implementation Complete
