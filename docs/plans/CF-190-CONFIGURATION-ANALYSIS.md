# CF-190: cf_cli.py Configuration Analysis Report

**Version**: 1.0  
**Created**: 2025-12-03  
**Status**: Complete  
**Author**: Agent Analysis  
**Linear Issue**: CF-190

---

## Executive Summary

This document provides a comprehensive analysis of all configuration-related code in `cf_cli.py` (8,312 lines) that needs to be migrated to pydantic-settings. The analysis identifies **31 configuration fields** across 5 major patterns spanning **~180 lines** of code to remove/refactor.

---

## 1. Configuration Fields Inventory

### 1.1 Root Callback CLI Options (Lines 650-695)

These are the primary configuration fields defined as `typer.Option` parameters in `_root_callback()`:

| # | Field Name | Type | Default | Env Variable | Description |
|---|-----------|------|---------|--------------|-------------|
| 1 | `csv_root` | `str` | `"trackers/csv"` | `CF_CLI_CSV_ROOT` | Legacy CSV root directory override |
| 2 | `log_path` | `str` | `"logs/cf_cli.log"` | `CF_CLI_LOG_PATH` | Supplemental log file path |
| 3 | `log_level` | `str` | `"INFO"` | `CF_CLI_LOG_LEVEL` | Log level (DEBUG, INFO, WARN, ERROR) |
| 4 | `quiet` | `bool` | `False` | `CF_CLI_QUIET_MODE` | Suppress logging output for automation |
| 5 | `rich_log` | `bool` | `False` | `UNIFIED_LOG_RICH` | Enable Rich console mirror |
| 6 | `rich_json` | `bool` | `True` | `UNIFIED_LOG_RICH_JSON` | Pretty-print details as JSON when Rich enabled |
| 7 | `rich_stderr` | `bool` | `True` | `UNIFIED_LOG_RICH_STDERR` | Route Rich mirror to stderr (vs stdout) |
| 8 | `metrics_port` | `int \| None` | `None` | - | Prometheus metrics port (optional) |
| 9 | `enable_tracing` | `bool` | `False` | - | OpenTelemetry tracing flag |

### 1.2 Environment Variables Set at Startup (Lines 71-92)

These environment variables are set via `os.environ.setdefault()` before any imports:

| # | Field Name | Type | Default | Env Variable | Description |
|---|-----------|------|---------|--------------|-------------|
| 10 | `unified_log_backend` | `str` | `"direct"` | `UNIFIED_LOG_BACKEND` | Logging backend (direct, loguru, structlog) |
| 11 | `unified_log_rich` | `bool` | `False` | `UNIFIED_LOG_RICH` | Enable Rich formatting |
| 12 | `unified_log_rich_mirror` | `bool` | `False` | `UNIFIED_LOG_RICH_MIRROR` | Rich console mirroring |
| 13 | `unified_log_dual_write` | `bool` | `False` | `UNIFIED_LOG_DUAL_WRITE` | Dual write (console + file) |
| 14 | `unified_log_rich_stderr` | `bool` | `False` | `UNIFIED_LOG_RICH_STDERR` | Route Rich to stderr |
| 15 | `unified_log_rich_json` | `bool` | `False` | `UNIFIED_LOG_RICH_JSON` | JSON pretty-print for Rich |
| 16 | `unified_log_suppress_json` | `str` | `"true"` | `UNIFIED_LOG_SUPPRESS_JSON` | Suppress JSON console output |
| 17 | `dbcli_rich_enable` | `bool` | `True` | `DBCLI_RICH_ENABLE` | Enable Rich for dbcli |

### 1.3 Feature Flags (Lines 434, 486, 805-810)

| # | Field Name | Type | Default | Env Variable | Description |
|---|-----------|------|---------|--------------|-------------|
| 18 | `lazy_mode` | `bool` | `False` | `CF_CLI_LAZY_MODE` | Defer pydantic settings loading |
| 19 | `force_fallback` | `bool` | `False` | `CF_CLI_FORCE_FALLBACK` | Force JSONL fallback path |
| 20 | `disable_perf_opt` | `bool` | `False` | `CF_CLI_DISABLE_PERF_OPT` | Disable performance optimization |
| 21 | `use_output_manager` | `bool` | `False` | `CF_CLI_USE_OUTPUT_MANAGER` | Enable OutputManager feature |
| 22 | `stdout_json_only` | `bool` | `False` | `CF_CLI_STDOUT_JSON_ONLY` | Force JSON-only stdout |
| 23 | `suppress_session_events` | `bool` | `False` | `CF_CLI_SUPPRESS_SESSION_EVENTS` | Suppress session start/end events |

### 1.4 Output Configuration (Lines 888-904)

| # | Field Name | Type | Default | Env Variable | Description |
|---|-----------|------|---------|--------------|-------------|
| 24 | `json_output` | `bool` | `False` | `CF_JSON_OUTPUT` | Enable JSON output format |

### 1.5 Settings Object Attributes (accessed via get_settings())

These are accessed via `settings.logging.*` and `settings.paths.*` in `_root_callback()`:

| # | Field Path | Type | Default | Description |
|---|-----------|------|---------|-------------|
| 25 | `settings.paths.csv_root` | `Path` | `trackers/csv` | CSV root path |
| 26 | `settings.logging.path` | `Path` | `logs/cf_cli.log` | Log file path |
| 27 | `settings.logging.level` | `str` | `"INFO"` | Log level |
| 28 | `settings.logging.rich_enabled` | `bool` | `False` | Rich console enabled |
| 29 | `settings.logging.rich_mirror` | `bool` | `False` | Rich mirror enabled |
| 30 | `settings.logging.backend` | `str` | `"direct"` | Logging backend |
| 31 | `settings.logging.rich_json` | `bool` | `False` | Rich JSON output |
| 32 | `settings.logging.rich_stderr` | `bool` | `False` | Rich to stderr |

---

## 2. Code Patterns to Remove/Refactor

### 2.1 Global State Variables (Lines 432-436)

**Lines**: 432-436 (5 lines)  
**Action**: DELETE

```python
_SETTINGS_LOADED = False
_settings: Any | None = None
_LAZY_MODE = os.environ.get("CF_CLI_LAZY_MODE") == "1"
```

**Replacement**: `@lru_cache` singleton pattern in `get_settings()`

---

### 2.2 _ensure_settings_loaded() Function (Lines 437-459)

**Lines**: 437-459 (23 lines)  
**Action**: DELETE

```python
def _ensure_settings_loaded() -> None:  # pragma: no cover
    """Idempotent settings bootstrap (lazy mode support)."""
    global _SETTINGS_LOADED, _settings
    if _SETTINGS_LOADED:
        return
    # Attempt optimized config path (never fatal)
    if not os.environ.get("CF_CLI_DISABLE_PERF_OPT"):
        try:
            perf_mod = lazy_module("tools.performance_optimization")
            get_optimized_config = getattr(perf_mod, "get_optimized_config", None)
            if callable(get_optimized_config):
                _settings = get_optimized_config()
            else:
                _settings = None
        except Exception:
            _settings = None
    _SETTINGS_LOADED = True
```

**Replacement**: `get_settings()` function with `@lru_cache(maxsize=1)`

---

### 2.3 _init_config_package() Function (Lines 462-475)

**Lines**: 462-475 (14 lines)  
**Action**: DELETE

```python
def _init_config_package() -> None:  # pragma: no cover
    """Placeholder synthetic config package initializer."""
    return None


if not _LAZY_MODE:  # preserve original eager injection by default
    _init_config_package()
```

**Replacement**: No replacement needed - direct import from `src.config`

---

### 2.4 _GetSettingsProto Protocol Class (Lines 513-530)

**Lines**: 513-530 (18 lines)  
**Action**: DELETE

```python
class _GetSettingsProto(Protocol):
    def __call__(self) -> Any: ...

get_settings: _GetSettingsProto | None = None  # default None; injected

if TYPE_CHECKING:
    from cf_cli.config import get_settings  # type: ignore
```

**Replacement**: Direct import `from src.config import get_settings`

---

### 2.5 _root_callback() Function (Lines 649-826)

**Lines**: 649-826 (178 lines)  
**Action**: REFACTOR to ~40 lines

**Current Complexity**:
- 9 typer.Option parameters
- Settings object retrieval with fallback
- Manual attribute setting (15+ attributes)
- Environment variable exports (15+ os.environ[] calls)
- OutputManager bootstrap
- Monitoring infrastructure bootstrap

**Target Implementation**:
```python
def _root_callback(ctx: typer.Context, ...):
    """Apply global configuration via CFSettings."""
    if ctx.resilient_parsing:
        return
    
    settings = get_settings()
    
    # Override from CLI args
    if csv_root != "trackers/csv":
        settings.paths.csv_root = Path(csv_root)
    if log_path != "logs/cf_cli.log":
        settings.logging.path = Path(log_path)
    # ... minimal overrides
    
    # Export to environment for legacy compatibility
    settings.apply_to_environment()
    
    # Store in context for downstream commands
    ctx.obj = settings
```

---

## 3. Dependencies and Import Structure

### 3.1 Current Import Chain

```
cf_cli.py
├── Global state (_SETTINGS_LOADED, _settings, _LAZY_MODE)
├── _ensure_settings_loaded()
│   └── tools.performance_optimization.get_optimized_config()
├── _init_config_package()
│   └── (synthetic package injection - removed)
├── _GetSettingsProto Protocol
│   └── cf_cli.config.get_settings (TYPE_CHECKING only)
└── _root_callback()
    └── lazy_module("cf_cli.config").get_settings()
```

### 3.2 Target Import Chain

```
cf_cli.py
└── from src.config import get_settings, CFSettings
    └── src/config/cf_settings.py
        └── CFSettings(BaseAppSettings)
            ├── LoggingConfig (nested)
            ├── PathConfig (nested)
            ├── OutputConfig (nested)
            └── @lru_cache singleton
```

---

## 4. Environment Variable Mapping

### 4.1 CF_CLI_* Variables (Primary)

| Env Variable | CFSettings Field | Type | Default |
|--------------|------------------|------|---------|
| `CF_CLI_CSV_ROOT` | `paths.csv_root` | `Path` | `"trackers/csv"` |
| `CF_CLI_LOG_PATH` | `logging.path` | `Path` | `"logs/cf_cli.log"` |
| `CF_CLI_LOG_LEVEL` | `logging.level` | `LogLevel` | `"INFO"` |
| `CF_CLI_QUIET_MODE` | `output.quiet` | `bool` | `False` |
| `CF_CLI_LAZY_MODE` | `lazy_mode` | `bool` | `False` |
| `CF_CLI_FORCE_FALLBACK` | `force_fallback` | `bool` | `False` |
| `CF_CLI_DISABLE_PERF_OPT` | `disable_perf_opt` | `bool` | `False` |
| `CF_CLI_USE_OUTPUT_MANAGER` | `use_output_manager` | `bool` | `False` |
| `CF_CLI_STDOUT_JSON_ONLY` | `stdout_json_only` | `bool` | `False` |
| `CF_CLI_SUPPRESS_SESSION_EVENTS` | `suppress_session_events` | `bool` | `False` |

### 4.2 UNIFIED_LOG_* Variables (Logging)

| Env Variable | CFSettings Field | Type | Default |
|--------------|------------------|------|---------|
| `UNIFIED_LOG_BACKEND` | `logging.backend` | `str` | `"direct"` |
| `UNIFIED_LOG_RICH` | `logging.rich_enabled` | `bool` | `False` |
| `UNIFIED_LOG_RICH_MIRROR` | `logging.rich_mirror` | `bool` | `False` |
| `UNIFIED_LOG_DUAL_WRITE` | `logging.dual_write` | `bool` | `False` |
| `UNIFIED_LOG_RICH_STDERR` | `logging.rich_stderr` | `bool` | `False` |
| `UNIFIED_LOG_RICH_JSON` | `logging.rich_json` | `bool` | `False` |
| `UNIFIED_LOG_SUPPRESS_JSON` | `logging.suppress_json` | `bool` | `True` |

### 4.3 Other Variables

| Env Variable | CFSettings Field | Type | Default |
|--------------|------------------|------|---------|
| `CF_JSON_OUTPUT` | `output.json_output` | `bool` | `False` |
| `DBCLI_RICH_ENABLE` | `rich.dbcli_enabled` | `bool` | `True` |

---

## 5. Edge Cases and Special Handling

### 5.1 CF_CLI_LAZY_MODE Preservation

**Current Behavior** (Line 434):
```python
_LAZY_MODE = os.environ.get("CF_CLI_LAZY_MODE") == "1"
```

**Must Preserve**:
- Settings loading deferred until first `get_settings()` call
- Performance benefit for tab completion
- Tests relying on `CF_CLI_LAZY_MODE=1`

**Implementation**:
```python
@lru_cache(maxsize=1)
def get_settings() -> CFSettings:
    """Lazy-loaded cached settings."""
    if os.environ.get("CF_CLI_LAZY_MODE") == "1":
        # Minimal validation, defer expensive operations
        return CFSettings(_env_parse_none_str=True)
    return CFSettings()
```

---

### 5.2 apply_to_environment() Pattern

**Current Location**: `settings.apply_to_environment()` call at line 774

**Purpose**: Export settings to `os.environ` for legacy code compatibility

**Must Preserve**: Legacy code reads `os.environ["CF_CLI_*"]` directly

**Implementation** (in CFSettings):
```python
def apply_to_environment(self) -> None:
    """Export settings to environment variables for legacy compatibility."""
    os.environ["CF_CLI_CSV_ROOT"] = str(self.paths.csv_root)
    os.environ["CF_CLI_LOG_PATH"] = str(self.logging.path)
    os.environ["CF_CLI_LOG_LEVEL"] = self.logging.level
    os.environ["CF_CLI_QUIET_MODE"] = "1" if self.output.quiet else "0"
    # ... (15+ exports)
```

---

### 5.3 Quiet Mode Side Effects

**Current Behavior** (Lines 760-772):
```python
if quiet:
    os.environ["CF_CLI_QUIET_MODE"] = "1"
    if getattr(settings, "logging", None):
        settings.logging.backend = "direct"
        settings.logging.rich_enabled = False
        settings.logging.rich_mirror = False
```

**Must Preserve**: Quiet mode disables Rich and forces direct logging backend

---

### 5.4 Rich Log Enabling

**Current Behavior** (Lines 739-749):
```python
if rich_log and getattr(settings, "logging", None):
    settings.logging.rich_enabled = True
    settings.logging.rich_mirror = True
    if getattr(settings.logging, "backend", "direct") == "direct":
        settings.logging.backend = "loguru"
```

**Must Preserve**: `--rich` flag enables Rich console and switches backend

---

### 5.5 Log Level Validation

**Current Behavior** (Lines 731-736):
```python
_allowed = {"DEBUG", "INFO", "WARN", "ERROR"}
_lvl = str(log_level).upper()
if _lvl not in _allowed:
    _lvl = "INFO"
```

**Implementation**: Use pydantic `field_validator` with `LogLevel` enum

---

## 6. CFSettings Class Structure (Proposed)

```python
# src/config/cf_settings.py

from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config.models import LoggingConfig, PathConfig, OutputConfig


class CFSettings(BaseSettings):
    """CF_CLI configuration with environment variable support."""

    # =========================================================================
    # Core Settings
    # =========================================================================
    
    lazy_mode: bool = Field(
        default=False,
        description="Defer settings loading (CF_CLI_LAZY_MODE)",
    )
    force_fallback: bool = Field(
        default=False,
        description="Force JSONL fallback path",
    )
    disable_perf_opt: bool = Field(
        default=False,
        description="Disable performance optimization",
    )
    
    # =========================================================================
    # Feature Flags
    # =========================================================================
    
    use_output_manager: bool = Field(
        default=False,
        description="Enable OutputManager feature",
    )
    stdout_json_only: bool = Field(
        default=False,
        description="Force JSON-only stdout",
    )
    suppress_session_events: bool = Field(
        default=False,
        description="Suppress session start/end events",
    )
    json_output: bool = Field(
        default=False,
        description="Enable JSON output format (CF_JSON_OUTPUT)",
    )
    
    # =========================================================================
    # Observability
    # =========================================================================
    
    metrics_port: int | None = Field(
        default=None,
        ge=1024,
        le=65535,
        description="Prometheus metrics port (optional)",
    )
    enable_tracing: bool = Field(
        default=False,
        description="Enable OpenTelemetry tracing",
    )
    
    # =========================================================================
    # Nested Configuration Models
    # =========================================================================
    
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig,
        description="Logging configuration",
    )
    paths: PathConfig = Field(
        default_factory=PathConfig,
        description="File system paths",
    )
    output: OutputConfig = Field(
        default_factory=OutputConfig,
        description="CLI output formatting",
    )
    
    # =========================================================================
    # Pydantic Settings Configuration
    # =========================================================================
    
    model_config = SettingsConfigDict(
        env_prefix="CF_CLI_",
        env_nested_delimiter="__",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        validate_default=True,
        extra="ignore",
    )
    
    # =========================================================================
    # Methods
    # =========================================================================
    
    def apply_to_environment(self) -> None:
        """Export settings to environment for legacy compatibility."""
        import os
        
        os.environ["CF_CLI_CSV_ROOT"] = str(self.paths.csv_root)
        os.environ["CF_CLI_LOG_PATH"] = str(self.logging.log_file_path)
        os.environ["CF_CLI_LOG_LEVEL"] = str(self.logging.level.value)
        os.environ["CF_CLI_QUIET_MODE"] = "1" if self.output.quiet else "0"
        os.environ["CF_CLI_LAZY_MODE"] = "1" if self.lazy_mode else "0"
        os.environ["UNIFIED_LOG_BACKEND"] = self.logging.backend
        os.environ["UNIFIED_LOG_RICH"] = "1" if self.logging.rich_enabled else "0"
        os.environ["UNIFIED_LOG_RICH_MIRROR"] = "1" if self.logging.rich_mirror else "0"
        os.environ["UNIFIED_LOG_RICH_STDERR"] = "1" if self.logging.rich_stderr else "0"
        os.environ["UNIFIED_LOG_RICH_JSON"] = "1" if self.logging.rich_json else "0"
        os.environ["CF_JSON_OUTPUT"] = "true" if self.json_output else "false"


@lru_cache(maxsize=1)
def get_settings() -> CFSettings:
    """Get cached CF_CLI settings (singleton pattern)."""
    return CFSettings()


def reload_settings() -> CFSettings:
    """Force reload settings (clears cache)."""
    get_settings.cache_clear()
    return get_settings()
```

---

## 7. Lines to Remove Summary

| Pattern | Line Range | Lines | Action |
|---------|-----------|-------|--------|
| Global state variables | 432-436 | 5 | DELETE |
| `_ensure_settings_loaded()` | 437-459 | 23 | DELETE |
| `_init_config_package()` | 462-475 | 14 | DELETE |
| `_GetSettingsProto` | 513-530 | 18 | DELETE |
| `_root_callback()` | 649-826 | 178 | REFACTOR to ~40 lines |
| **Total to Remove** | | **~180 lines** | |

---

## 8. Validation Checklist

### 8.1 Pre-Migration

- [ ] Document all 31 configuration fields
- [ ] Map all environment variables
- [ ] Identify edge cases (lazy mode, quiet mode, rich log)
- [ ] Review existing test coverage

### 8.2 Post-Migration

- [ ] All 31 fields accessible via `get_settings()`
- [ ] All environment variables load correctly
- [ ] `CF_CLI_LAZY_MODE` performance preserved
- [ ] `apply_to_environment()` exports all legacy keys
- [ ] Quiet mode disables Rich and sets direct backend
- [ ] `--rich` flag enables Rich and switches to loguru
- [ ] Log level validation via enum
- [ ] 85 existing tests pass
- [ ] 15+ new CFSettings tests added
- [ ] ≥90% coverage for `src/config/cf_settings.py`

---

## 9. Next Steps

1. **Create `src/config/cf_settings.py`** - Implement CFSettings class with all 31 fields
2. **Update `src/config/__init__.py`** - Export CFSettings, get_settings, reload_settings
3. **Refactor `cf_cli.py`** - Replace 180 lines with new imports and simplified `_root_callback()`
4. **Write tests** - `tests/unit/config/test_cf_settings.py`
5. **Validate** - Run full test suite, check performance

---

**Analysis Complete**: 2025-12-03  
**Ready for Implementation**: Yes
