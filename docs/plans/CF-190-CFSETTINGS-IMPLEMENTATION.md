# CF-190: CFSettings Implementation Plan

**Version**: 1.0  
**Created**: 2025-12-03  
**Status**: Ready for Implementation  
**Prerequisites**: CF-189 BaseAppSettings (Complete)  
**Linear Issue**: CF-190

---

## 1. Implementation Overview

This document provides the complete Python code skeleton for `src/config/cf_settings.py` implementing the CFSettings class that extends BaseAppSettings to replace 342 lines of manual configuration in `cf_cli.py`.

---

## 2. Extended LoggingConfig Model

The base `LoggingConfig` from `models.py` needs extension with CF_CLI-specific fields:

```python
# src/config/cf_settings.py - Extended LoggingConfig

class CFLoggingConfig(LoggingConfig):
    """Extended logging configuration with CF_CLI-specific fields."""
    
    # Inherited from LoggingConfig:
    # - level: LogLevel = LogLevel.INFO
    # - format: Literal["json", "text", "rich"] = "rich"
    # - correlation_enabled: bool = True
    # - file_logging_enabled: bool = False
    # - log_file_path: Path = Path("logs/contextforge.log")
    
    # CF_CLI-specific extensions:
    backend: Literal["direct", "loguru", "structlog"] = Field(
        default="direct",
        description="Logging backend (UNIFIED_LOG_BACKEND)",
    )
    rich_enabled: bool = Field(
        default=False,
        description="Enable Rich console formatting (UNIFIED_LOG_RICH)",
    )
    rich_mirror: bool = Field(
        default=False,
        description="Enable Rich console mirroring (UNIFIED_LOG_RICH_MIRROR)",
    )
    dual_write: bool = Field(
        default=False,
        description="Enable dual write (console + file) (UNIFIED_LOG_DUAL_WRITE)",
    )
    rich_stderr: bool = Field(
        default=False,
        description="Route Rich output to stderr (UNIFIED_LOG_RICH_STDERR)",
    )
    rich_json: bool = Field(
        default=False,
        description="Pretty-print JSON in Rich output (UNIFIED_LOG_RICH_JSON)",
    )
    suppress_json: bool = Field(
        default=True,
        description="Suppress JSON console output (UNIFIED_LOG_SUPPRESS_JSON)",
    )
    
    # Path overrides for CLI
    path: Path = Field(
        default=Path("logs/cf_cli.log"),
        description="CLI log file path (CF_CLI_LOG_PATH)",
    )
```

---

## 3. Extended PathConfig Model

```python
# src/config/cf_settings.py - Extended PathConfig

class CFPathConfig(PathConfig):
    """Extended path configuration with CF_CLI-specific fields."""
    
    # Inherited from PathConfig:
    # - artifacts_dir: Path = Path("artifacts")
    # - qse_dir: Path = Path(".QSE/v2")
    # - logs_dir: Path = Path("logs")
    # - trackers_dir: Path = Path("trackers")
    # - temp_dir: Path = Path(".tmp")
    
    # CF_CLI-specific extensions:
    csv_root: Path = Field(
        default=Path("trackers/csv"),
        description="Legacy CSV tracker root directory (CF_CLI_CSV_ROOT)",
    )
    
    @field_validator("csv_root", mode="after")
    @classmethod
    def ensure_csv_root_absolute(cls, v: Path) -> Path:
        """Convert csv_root to absolute path if relative."""
        if not v.is_absolute():
            project_root = Path(__file__).parent.parent.parent
            return (project_root / v).resolve()
        return v
```

---

## 4. New Nested Models

### 4.1 RichConfig

```python
class RichConfig(BaseModel):
    """Rich library console configuration."""
    
    console_width: int | None = Field(
        default=None,
        ge=40,
        le=500,
        description="Console width override (None=auto-detect)",
    )
    force_terminal: bool = Field(
        default=False,
        description="Force terminal mode even when not detected",
    )
    highlight: bool = Field(
        default=True,
        description="Enable syntax highlighting in output",
    )
    markup: bool = Field(
        default=True,
        description="Enable Rich markup parsing",
    )
    dbcli_enabled: bool = Field(
        default=True,
        description="Enable Rich for dbcli commands (DBCLI_RICH_ENABLE)",
    )
```

### 4.2 QSEConfig

```python
class QSEConfig(BaseModel):
    """QSE framework configuration."""
    
    phases: list[str] = Field(
        default_factory=lambda: [
            "analysis",
            "design",
            "implementation",
            "testing",
            "deployment",
        ],
        description="QSE workflow phases",
    )
    artifacts_dir: Path = Field(
        default=Path(".QSE/v2/artifacts"),
        description="QSE artifacts directory",
    )
    evidence_required: bool = Field(
        default=True,
        description="Require evidence for phase transitions",
    )
    auto_archive: bool = Field(
        default=True,
        description="Auto-archive completed sessions",
    )
```

### 4.3 CLIConfig

```python
class CLIConfig(BaseModel):
    """CLI behavior configuration."""
    
    default_output_format: OutputFormat = Field(
        default=OutputFormat.TABLE,
        description="Default output format for commands",
    )
    pager: str = Field(
        default="less",
        description="Pager command for long output",
    )
    editor: str = Field(
        default="code",
        description="Default editor for --edit commands",
    )
    confirm_destructive: bool = Field(
        default=True,
        description="Require confirmation for destructive operations",
    )
    history_enabled: bool = Field(
        default=True,
        description="Enable command history tracking",
    )
    max_history_size: int = Field(
        default=1000,
        ge=100,
        le=10000,
        description="Maximum command history entries",
    )
```

### 4.4 ObservabilityConfig

```python
class ObservabilityConfig(BaseModel):
    """Observability and monitoring configuration."""
    
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
    trace_sample_rate: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Trace sampling rate (0.0-1.0)",
    )
    health_check_port: int | None = Field(
        default=None,
        ge=1024,
        le=65535,
        description="Health check HTTP port (optional)",
    )
```

---

## 5. Complete CFSettings Class Skeleton

```python
"""
CF_CLI configuration using pydantic-settings.

This module provides CFSettings, the central configuration class for cf_cli.py.
It extends BaseAppSettings from CF-189 and adds all CF_CLI-specific fields.
"""

from __future__ import annotations

import os
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import SettingsConfigDict

from src.config.base import BaseAppSettings
from src.config.models import (
    DatabaseConfig,
    LoggingConfig,
    LogLevel,
    OutputConfig,
    OutputFormat,
    PathConfig,
)

if TYPE_CHECKING:
    from typing import Self


# =============================================================================
# Extended Nested Models for CF_CLI
# =============================================================================


class CFLoggingConfig(LoggingConfig):
    """Extended logging configuration with CF_CLI-specific fields.
    
    Inherits from LoggingConfig:
    - level: LogLevel (INFO)
    - format: json|text|rich (rich)
    - correlation_enabled: bool (True)
    - file_logging_enabled: bool (False)
    - log_file_path: Path (logs/contextforge.log)
    """
    
    backend: Literal["direct", "loguru", "structlog"] = Field(
        default="direct",
        description="Logging backend implementation",
    )
    rich_enabled: bool = Field(
        default=False,
        description="Enable Rich console formatting",
    )
    rich_mirror: bool = Field(
        default=False,
        description="Mirror Rich output to secondary destination",
    )
    dual_write: bool = Field(
        default=False,
        description="Write logs to both console and file",
    )
    rich_stderr: bool = Field(
        default=False,
        description="Route Rich output to stderr instead of stdout",
    )
    rich_json: bool = Field(
        default=False,
        description="Enable JSON pretty-printing in Rich output",
    )
    suppress_json: bool = Field(
        default=True,
        description="Suppress raw JSON in console output",
    )
    path: Path = Field(
        default=Path("logs/cf_cli.log"),
        description="CLI-specific log file path",
    )


class CFPathConfig(PathConfig):
    """Extended path configuration with CF_CLI-specific fields.
    
    Inherits from PathConfig:
    - artifacts_dir, qse_dir, logs_dir, trackers_dir, temp_dir
    """
    
    csv_root: Path = Field(
        default=Path("trackers/csv"),
        description="Legacy CSV tracker root directory",
    )
    
    @field_validator("csv_root", mode="after")
    @classmethod
    def ensure_csv_root_absolute(cls, v: Path) -> Path:
        """Convert csv_root to absolute path."""
        if not v.is_absolute():
            project_root = Path(__file__).parent.parent.parent
            return (project_root / v).resolve()
        return v


class RichConfig(BaseModel):
    """Rich library console configuration."""
    
    console_width: int | None = Field(
        default=None,
        ge=40,
        le=500,
        description="Console width override (None=auto-detect)",
    )
    force_terminal: bool = Field(
        default=False,
        description="Force terminal mode even when not detected",
    )
    highlight: bool = Field(
        default=True,
        description="Enable syntax highlighting",
    )
    markup: bool = Field(
        default=True,
        description="Enable Rich markup parsing",
    )
    dbcli_enabled: bool = Field(
        default=True,
        description="Enable Rich for dbcli commands",
    )


class QSEConfig(BaseModel):
    """QSE framework configuration."""
    
    phases: list[str] = Field(
        default_factory=lambda: [
            "analysis", "design", "implementation", "testing", "deployment"
        ],
        description="QSE workflow phases",
    )
    artifacts_dir: Path = Field(
        default=Path(".QSE/v2/artifacts"),
        description="QSE artifacts directory",
    )
    evidence_required: bool = Field(
        default=True,
        description="Require evidence for phase transitions",
    )
    auto_archive: bool = Field(
        default=True,
        description="Auto-archive completed sessions",
    )


class CLIConfig(BaseModel):
    """CLI behavior configuration."""
    
    default_output_format: OutputFormat = Field(
        default=OutputFormat.TABLE,
        description="Default output format for commands",
    )
    pager: str = Field(
        default="less",
        description="Pager command for long output",
    )
    editor: str = Field(
        default="code",
        description="Default editor for --edit commands",
    )
    confirm_destructive: bool = Field(
        default=True,
        description="Require confirmation for destructive operations",
    )
    history_enabled: bool = Field(
        default=True,
        description="Enable command history tracking",
    )
    max_history_size: int = Field(
        default=1000,
        ge=100,
        le=10000,
        description="Maximum command history entries",
    )


class ObservabilityConfig(BaseModel):
    """Observability and monitoring configuration."""
    
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
    trace_sample_rate: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Trace sampling rate (0.0-1.0)",
    )
    health_check_port: int | None = Field(
        default=None,
        ge=1024,
        le=65535,
        description="Health check HTTP port (optional)",
    )


# =============================================================================
# Main CFSettings Class
# =============================================================================


class CFSettings(BaseAppSettings):
    """
    Central configuration for cf_cli.py using pydantic-settings.
    
    Extends BaseAppSettings with all CF_CLI-specific fields, replacing
    342 lines of manual configuration code.
    
    Configuration precedence (highest to lowest):
    1. CLI arguments (passed to _root_callback)
    2. Environment variables (CF_CLI_* prefix)
    3. .env file in project root
    4. Default values defined here
    
    Environment Variable Examples:
        CF_CLI_DEBUG=true
        CF_CLI_LAZY_MODE=1
        CF_CLI_LOGGING__LEVEL=DEBUG
        CF_CLI_LOGGING__BACKEND=loguru
        CF_CLI_PATHS__CSV_ROOT=/custom/path
    
    Usage:
        from src.config import get_cf_settings
        
        settings = get_cf_settings()
        print(settings.debug)  # False
        print(settings.logging.level)  # INFO
        print(settings.paths.csv_root)  # trackers/csv
    """
    
    # =========================================================================
    # Core Settings (inherited: debug, lazy_mode, environment)
    # =========================================================================
    
    verbose: bool = Field(
        default=False,
        description="Enable verbose output mode",
    )
    
    # =========================================================================
    # Feature Flags
    # =========================================================================
    
    force_fallback: bool = Field(
        default=False,
        description="Force JSONL fallback path for data operations",
    )
    disable_perf_opt: bool = Field(
        default=False,
        description="Disable performance optimizations (for debugging)",
    )
    use_output_manager: bool = Field(
        default=False,
        description="Enable OutputManager feature (experimental)",
    )
    stdout_json_only: bool = Field(
        default=False,
        description="Force JSON-only output to stdout",
    )
    suppress_session_events: bool = Field(
        default=False,
        description="Suppress session start/end event logging",
    )
    json_output: bool = Field(
        default=False,
        alias="CF_JSON_OUTPUT",
        description="Enable JSON output format globally",
    )
    
    # =========================================================================
    # Extended Nested Configuration Models
    # =========================================================================
    
    logging: CFLoggingConfig = Field(
        default_factory=CFLoggingConfig,
        description="Extended logging configuration",
    )
    paths: CFPathConfig = Field(
        default_factory=CFPathConfig,
        description="Extended path configuration",
    )
    output: OutputConfig = Field(
        default_factory=OutputConfig,
        description="CLI output formatting",
    )
    database: DatabaseConfig = Field(
        default_factory=DatabaseConfig,
        description="Database connection settings",
    )
    rich: RichConfig = Field(
        default_factory=RichConfig,
        description="Rich console configuration",
    )
    qse: QSEConfig = Field(
        default_factory=QSEConfig,
        description="QSE framework configuration",
    )
    cli: CLIConfig = Field(
        default_factory=CLIConfig,
        description="CLI behavior configuration",
    )
    observability: ObservabilityConfig = Field(
        default_factory=ObservabilityConfig,
        description="Observability and monitoring",
    )
    
    # =========================================================================
    # Pydantic Settings Configuration
    # =========================================================================
    
    model_config = SettingsConfigDict(
        # Environment variable settings
        env_prefix="CF_CLI_",
        env_nested_delimiter="__",
        case_sensitive=False,
        # .env file settings
        env_file=".env",
        env_file_encoding="utf-8",
        # Validation settings
        validate_default=True,
        extra="ignore",  # Allow extra fields for forward compatibility
        # Serialization
        use_enum_values=True,
    )
    
    # =========================================================================
    # Field Validators
    # =========================================================================
    
    @field_validator("logging", mode="before")
    @classmethod
    def parse_logging_config(cls, v: Any) -> Any:
        """Handle logging config from various sources."""
        if isinstance(v, dict):
            # Normalize log level string to LogLevel enum
            if "level" in v and isinstance(v["level"], str):
                level_str = v["level"].upper()
                allowed = {"DEBUG", "INFO", "WARNING", "WARN", "ERROR", "CRITICAL"}
                if level_str not in allowed:
                    v["level"] = "INFO"  # Default for invalid values
                elif level_str == "WARN":
                    v["level"] = "WARNING"  # Normalize WARN -> WARNING
        return v
    
    @model_validator(mode="after")
    def apply_quiet_mode_side_effects(self) -> Self:
        """Apply quiet mode side effects to logging configuration.
        
        When quiet mode is enabled:
        - Disable Rich formatting
        - Disable Rich mirroring
        - Force direct backend
        """
        if self.output.quiet:
            self.logging.backend = "direct"
            self.logging.rich_enabled = False
            self.logging.rich_mirror = False
        return self
    
    # =========================================================================
    # Methods
    # =========================================================================
    
    def apply_to_environment(self) -> None:
        """
        Export settings to environment variables for legacy compatibility.
        
        This method exports all relevant settings to os.environ so that
        legacy code that reads environment variables directly will work.
        
        Exported variables:
        - CF_CLI_CSV_ROOT
        - CF_CLI_LOG_PATH
        - CF_CLI_LOG_LEVEL
        - CF_CLI_QUIET_MODE
        - CF_CLI_LAZY_MODE
        - UNIFIED_LOG_BACKEND
        - UNIFIED_LOG_RICH
        - UNIFIED_LOG_RICH_MIRROR
        - UNIFIED_LOG_DUAL_WRITE
        - UNIFIED_LOG_RICH_STDERR
        - UNIFIED_LOG_RICH_JSON
        - UNIFIED_LOG_SUPPRESS_JSON
        - CF_JSON_OUTPUT
        - DBCLI_RICH_ENABLE
        """
        # Path settings
        os.environ["CF_CLI_CSV_ROOT"] = str(self.paths.csv_root)
        os.environ["CF_CLI_LOG_PATH"] = str(self.logging.path)
        
        # Logging settings
        os.environ["CF_CLI_LOG_LEVEL"] = (
            self.logging.level.value
            if isinstance(self.logging.level, LogLevel)
            else str(self.logging.level)
        )
        
        # Boolean flags (use "1"/"0" for shell compatibility)
        os.environ["CF_CLI_QUIET_MODE"] = "1" if self.output.quiet else "0"
        os.environ["CF_CLI_LAZY_MODE"] = "1" if self.lazy_mode else "0"
        
        # Unified logging backend settings
        os.environ["UNIFIED_LOG_BACKEND"] = self.logging.backend
        os.environ["UNIFIED_LOG_RICH"] = "1" if self.logging.rich_enabled else "0"
        os.environ["UNIFIED_LOG_RICH_MIRROR"] = "1" if self.logging.rich_mirror else "0"
        os.environ["UNIFIED_LOG_DUAL_WRITE"] = "1" if self.logging.dual_write else "0"
        os.environ["UNIFIED_LOG_RICH_STDERR"] = "1" if self.logging.rich_stderr else "0"
        os.environ["UNIFIED_LOG_RICH_JSON"] = "1" if self.logging.rich_json else "0"
        os.environ["UNIFIED_LOG_SUPPRESS_JSON"] = (
            "true" if self.logging.suppress_json else "false"
        )
        
        # Output format
        os.environ["CF_JSON_OUTPUT"] = "true" if self.json_output else "false"
        
        # Rich configuration
        os.environ["DBCLI_RICH_ENABLE"] = "1" if self.rich.dbcli_enabled else "0"
    
    def enable_rich_mode(self) -> None:
        """Enable Rich console output with recommended settings.
        
        Called when --rich flag is passed to CLI. Switches backend to loguru
        if currently using direct backend for better Rich integration.
        """
        self.logging.rich_enabled = True
        self.logging.rich_mirror = True
        if self.logging.backend == "direct":
            self.logging.backend = "loguru"
    
    def enable_quiet_mode(self) -> None:
        """Enable quiet mode for automation/scripting.
        
        Disables Rich formatting and forces direct backend.
        """
        self.output.quiet = True
        self.logging.backend = "direct"
        self.logging.rich_enabled = False
        self.logging.rich_mirror = False
    
    def to_cli_context(self) -> dict[str, Any]:
        """Convert settings to dict for storing in typer.Context.obj.
        
        Returns:
            Dictionary suitable for use as ctx.obj in typer commands.
        """
        return {
            "settings": self,
            "debug": self.debug,
            "verbose": self.verbose,
            "quiet": self.output.quiet,
            "json_output": self.json_output,
            "log_level": self.logging.level,
        }


# =============================================================================
# Singleton Access Functions
# =============================================================================


@lru_cache(maxsize=1)
def get_cf_settings() -> CFSettings:
    """
    Get cached CF_CLI settings (singleton pattern).
    
    Settings are loaded once from environment variables and .env file,
    then cached for the lifetime of the process. This prevents redundant
    parsing and provides consistent settings across all modules.
    
    The caching is compatible with CF_CLI_LAZY_MODE - settings are only
    loaded when first accessed, not at import time.
    
    Returns:
        CFSettings: Validated CF_CLI configuration
    
    Example:
        from src.config import get_cf_settings
        
        settings = get_cf_settings()
        print(f"Debug: {settings.debug}")
        print(f"Log Level: {settings.logging.level}")
        print(f"CSV Root: {settings.paths.csv_root}")
    """
    return CFSettings()


def reload_cf_settings() -> CFSettings:
    """
    Force reload settings (clears cache).
    
    Use when environment variables change during runtime.
    Primarily useful for testing scenarios.
    
    Returns:
        CFSettings: Freshly loaded settings
    
    Example:
        import os
        os.environ["CF_CLI_DEBUG"] = "true"
        
        # Clear cache and reload
        settings = reload_cf_settings()
        assert settings.debug is True
    """
    get_cf_settings.cache_clear()
    return get_cf_settings()


# =============================================================================
# Module-level Aliases for Backward Compatibility
# =============================================================================

# Alias for simpler import: from src.config.cf_settings import get_settings
get_settings = get_cf_settings
reload_settings = reload_cf_settings
```

---

## 6. Complete Fields Reference

### 6.1 Core Settings (7 fields)

| Field | Type | Default | Env Variable | Description |
|-------|------|---------|--------------|-------------|
| `debug` | `bool` | `False` | `CF_CLI_DEBUG` | Enable debug mode |
| `verbose` | `bool` | `False` | `CF_CLI_VERBOSE` | Enable verbose output |
| `lazy_mode` | `bool` | `False` | `CF_CLI_LAZY_MODE` | Defer settings loading |
| `environment` | `Literal` | `"development"` | `CF_CLI_ENVIRONMENT` | Deployment environment |
| `force_fallback` | `bool` | `False` | `CF_CLI_FORCE_FALLBACK` | Force JSONL fallback |
| `disable_perf_opt` | `bool` | `False` | `CF_CLI_DISABLE_PERF_OPT` | Disable optimizations |
| `json_output` | `bool` | `False` | `CF_JSON_OUTPUT` | Enable JSON output |

### 6.2 Feature Flags (3 fields)

| Field | Type | Default | Env Variable | Description |
|-------|------|---------|--------------|-------------|
| `use_output_manager` | `bool` | `False` | `CF_CLI_USE_OUTPUT_MANAGER` | OutputManager feature |
| `stdout_json_only` | `bool` | `False` | `CF_CLI_STDOUT_JSON_ONLY` | JSON-only stdout |
| `suppress_session_events` | `bool` | `False` | `CF_CLI_SUPPRESS_SESSION_EVENTS` | Suppress events |

### 6.3 CFLoggingConfig (13 fields)

| Field | Type | Default | Env Variable | Description |
|-------|------|---------|--------------|-------------|
| `level` | `LogLevel` | `INFO` | `CF_CLI_LOGGING__LEVEL` | Log level |
| `format` | `Literal` | `"rich"` | `CF_CLI_LOGGING__FORMAT` | Log format |
| `backend` | `Literal` | `"direct"` | `UNIFIED_LOG_BACKEND` | Logging backend |
| `rich_enabled` | `bool` | `False` | `UNIFIED_LOG_RICH` | Rich formatting |
| `rich_mirror` | `bool` | `False` | `UNIFIED_LOG_RICH_MIRROR` | Rich mirroring |
| `dual_write` | `bool` | `False` | `UNIFIED_LOG_DUAL_WRITE` | Dual write mode |
| `rich_stderr` | `bool` | `False` | `UNIFIED_LOG_RICH_STDERR` | Rich to stderr |
| `rich_json` | `bool` | `False` | `UNIFIED_LOG_RICH_JSON` | JSON in Rich |
| `suppress_json` | `bool` | `True` | `UNIFIED_LOG_SUPPRESS_JSON` | Suppress JSON |
| `path` | `Path` | `logs/cf_cli.log` | `CF_CLI_LOG_PATH` | Log file path |
| `correlation_enabled` | `bool` | `True` | - | Correlation IDs |
| `file_logging_enabled` | `bool` | `False` | - | File logging |
| `log_file_path` | `Path` | `logs/contextforge.log` | - | Main log file |

### 6.4 CFPathConfig (6 fields)

| Field | Type | Default | Env Variable | Description |
|-------|------|---------|--------------|-------------|
| `csv_root` | `Path` | `trackers/csv` | `CF_CLI_CSV_ROOT` | CSV root dir |
| `artifacts_dir` | `Path` | `artifacts` | `CF_CLI_PATHS__ARTIFACTS_DIR` | Artifacts dir |
| `qse_dir` | `Path` | `.QSE/v2` | `CF_CLI_PATHS__QSE_DIR` | QSE dir |
| `logs_dir` | `Path` | `logs` | `CF_CLI_PATHS__LOGS_DIR` | Logs dir |
| `trackers_dir` | `Path` | `trackers` | `CF_CLI_PATHS__TRACKERS_DIR` | Trackers dir |
| `temp_dir` | `Path` | `.tmp` | `CF_CLI_PATHS__TEMP_DIR` | Temp dir |

### 6.5 RichConfig (5 fields)

| Field | Type | Default | Env Variable | Description |
|-------|------|---------|--------------|-------------|
| `console_width` | `int\|None` | `None` | `CF_CLI_RICH__CONSOLE_WIDTH` | Console width |
| `force_terminal` | `bool` | `False` | `CF_CLI_RICH__FORCE_TERMINAL` | Force terminal |
| `highlight` | `bool` | `True` | `CF_CLI_RICH__HIGHLIGHT` | Highlighting |
| `markup` | `bool` | `True` | `CF_CLI_RICH__MARKUP` | Markup parsing |
| `dbcli_enabled` | `bool` | `True` | `DBCLI_RICH_ENABLE` | Rich for dbcli |

### 6.6 QSEConfig (4 fields)

| Field | Type | Default | Env Variable | Description |
|-------|------|---------|--------------|-------------|
| `phases` | `list[str]` | `[5 phases]` | `CF_CLI_QSE__PHASES` | QSE phases |
| `artifacts_dir` | `Path` | `.QSE/v2/artifacts` | `CF_CLI_QSE__ARTIFACTS_DIR` | QSE artifacts |
| `evidence_required` | `bool` | `True` | `CF_CLI_QSE__EVIDENCE_REQUIRED` | Evidence req |
| `auto_archive` | `bool` | `True` | `CF_CLI_QSE__AUTO_ARCHIVE` | Auto archive |

### 6.7 CLIConfig (6 fields)

| Field | Type | Default | Env Variable | Description |
|-------|------|---------|--------------|-------------|
| `default_output_format` | `OutputFormat` | `TABLE` | `CF_CLI_CLI__DEFAULT_OUTPUT_FORMAT` | Output format |
| `pager` | `str` | `"less"` | `CF_CLI_CLI__PAGER` | Pager command |
| `editor` | `str` | `"code"` | `CF_CLI_CLI__EDITOR` | Editor command |
| `confirm_destructive` | `bool` | `True` | `CF_CLI_CLI__CONFIRM_DESTRUCTIVE` | Confirm ops |
| `history_enabled` | `bool` | `True` | `CF_CLI_CLI__HISTORY_ENABLED` | History |
| `max_history_size` | `int` | `1000` | `CF_CLI_CLI__MAX_HISTORY_SIZE` | History size |

### 6.8 ObservabilityConfig (4 fields)

| Field | Type | Default | Env Variable | Description |
|-------|------|---------|--------------|-------------|
| `metrics_port` | `int\|None` | `None` | `CF_CLI_OBSERVABILITY__METRICS_PORT` | Metrics port |
| `enable_tracing` | `bool` | `False` | `CF_CLI_OBSERVABILITY__ENABLE_TRACING` | Tracing |
| `trace_sample_rate` | `float` | `0.1` | `CF_CLI_OBSERVABILITY__TRACE_SAMPLE_RATE` | Sample rate |
| `health_check_port` | `int\|None` | `None` | `CF_CLI_OBSERVABILITY__HEALTH_CHECK_PORT` | Health port |

**Total Fields**: 48 (vs 31 in original analysis - extended for completeness)

---

## 7. Implementation Notes for Complex Validators

### 7.1 Log Level Validator

```python
@field_validator("logging", mode="before")
@classmethod
def parse_logging_config(cls, v: Any) -> Any:
    """Normalize log level strings to valid LogLevel enum values.
    
    Handles:
    - Case normalization: "debug" -> "DEBUG"
    - Legacy alias: "WARN" -> "WARNING"
    - Invalid values: default to "INFO"
    
    Example:
        CF_CLI_LOGGING__LEVEL=warn  # Becomes LogLevel.WARNING
        CF_CLI_LOGGING__LEVEL=INVALID  # Becomes LogLevel.INFO
    """
    if isinstance(v, dict):
        if "level" in v and isinstance(v["level"], str):
            level_str = v["level"].upper()
            allowed = {"DEBUG", "INFO", "WARNING", "WARN", "ERROR", "CRITICAL"}
            if level_str not in allowed:
                v["level"] = "INFO"
            elif level_str == "WARN":
                v["level"] = "WARNING"
    return v
```

### 7.2 Path Validator (Already in PathConfig)

The base `PathConfig.ensure_absolute_path` validator handles conversion of relative paths to absolute paths based on project root. The `CFPathConfig.ensure_csv_root_absolute` extends this for the `csv_root` field.

### 7.3 Quiet Mode Model Validator

```python
@model_validator(mode="after")
def apply_quiet_mode_side_effects(self) -> Self:
    """Apply quiet mode side effects after all fields are populated.
    
    When quiet=True:
    - backend -> "direct" (fastest, no formatting overhead)
    - rich_enabled -> False (no Rich output)
    - rich_mirror -> False (no mirroring)
    
    This ensures quiet mode truly suppresses all decorative output.
    """
    if self.output.quiet:
        self.logging.backend = "direct"
        self.logging.rich_enabled = False
        self.logging.rich_mirror = False
    return self
```

### 7.4 Database URL Validator (Inherited from DatabaseConfig)

The base `DatabaseConfig.validate_postgres_url` validator ensures database URLs use the `postgresql://` or `postgresql+asyncpg://` scheme.

### 7.5 Metrics Port Validator

```python
metrics_port: int | None = Field(
    default=None,
    ge=1024,  # Must be >= 1024 (non-privileged port)
    le=65535,  # Must be <= 65535 (max port number)
    description="Prometheus metrics port (optional)",
)
```

Port validation is handled declaratively via `ge`/`le` constraints.

---

## 8. Required Updates to `src/config/__init__.py`

```python
"""
ContextForge configuration management.

Exports:
- BaseAppSettings: Base settings class
- CFSettings: CF_CLI configuration
- get_base_settings, reload_settings: Base settings singleton
- get_cf_settings, reload_cf_settings: CF_CLI settings singleton
- All nested config models
"""

from src.config.base import (
    BaseAppSettings,
    get_base_settings,
    reload_settings,
)
from src.config.cf_settings import (
    CFLoggingConfig,
    CFPathConfig,
    CFSettings,
    CLIConfig,
    ObservabilityConfig,
    QSEConfig,
    RichConfig,
    get_cf_settings,
    reload_cf_settings,
)
from src.config.models import (
    DatabaseConfig,
    LoggingConfig,
    LogLevel,
    OutputConfig,
    OutputFormat,
    PathConfig,
)

__all__ = [
    # Base settings
    "BaseAppSettings",
    "get_base_settings",
    "reload_settings",
    # CF_CLI settings
    "CFSettings",
    "get_cf_settings",
    "reload_cf_settings",
    # Extended models
    "CFLoggingConfig",
    "CFPathConfig",
    "CLIConfig",
    "ObservabilityConfig",
    "QSEConfig",
    "RichConfig",
    # Base models
    "DatabaseConfig",
    "LoggingConfig",
    "LogLevel",
    "OutputConfig",
    "OutputFormat",
    "PathConfig",
]
```

---

## 9. Test Skeleton

```python
"""
Tests for CFSettings configuration.

Covers:
- Default value validation
- Environment variable loading
- Field validators
- Singleton behavior
- apply_to_environment() exports
"""

import os
from pathlib import Path

import pytest

from src.config import (
    CFSettings,
    get_cf_settings,
    reload_cf_settings,
)
from src.config.models import LogLevel


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    """Clear CF_CLI_* environment variables before each test."""
    for key in list(os.environ.keys()):
        if key.startswith(("CF_CLI_", "UNIFIED_LOG_", "CF_JSON_", "DBCLI_")):
            monkeypatch.delenv(key, raising=False)
    # Clear singleton cache
    get_cf_settings.cache_clear()
    yield


class TestCFSettingsDefaults:
    """Test default values match expected cf_cli.py defaults."""
    
    def test_debug_default_false(self):
        settings = CFSettings()
        assert settings.debug is False
    
    def test_lazy_mode_default_false(self):
        settings = CFSettings()
        assert settings.lazy_mode is False
    
    def test_logging_level_default_info(self):
        settings = CFSettings()
        assert settings.logging.level == LogLevel.INFO
    
    def test_logging_backend_default_direct(self):
        settings = CFSettings()
        assert settings.logging.backend == "direct"
    
    def test_paths_csv_root_default(self):
        settings = CFSettings()
        assert settings.paths.csv_root.name == "csv"
    
    def test_output_quiet_default_false(self):
        settings = CFSettings()
        assert settings.output.quiet is False


class TestCFSettingsEnvVars:
    """Test environment variable loading."""
    
    def test_debug_from_env(self, monkeypatch):
        monkeypatch.setenv("CF_CLI_DEBUG", "true")
        settings = CFSettings()
        assert settings.debug is True
    
    def test_lazy_mode_from_env(self, monkeypatch):
        monkeypatch.setenv("CF_CLI_LAZY_MODE", "1")
        settings = CFSettings()
        assert settings.lazy_mode is True
    
    def test_nested_logging_level_from_env(self, monkeypatch):
        monkeypatch.setenv("CF_CLI_LOGGING__LEVEL", "DEBUG")
        settings = CFSettings()
        assert settings.logging.level == LogLevel.DEBUG
    
    def test_unified_log_backend_from_env(self, monkeypatch):
        monkeypatch.setenv("UNIFIED_LOG_BACKEND", "loguru")
        # Note: This requires special handling in SettingsConfigDict
        settings = CFSettings()
        # May need alias mapping for non-prefixed vars


class TestCFSettingsValidators:
    """Test field validators."""
    
    def test_log_level_validator_normalizes_warn(self, monkeypatch):
        monkeypatch.setenv("CF_CLI_LOGGING__LEVEL", "WARN")
        settings = CFSettings()
        assert settings.logging.level == LogLevel.WARNING
    
    def test_log_level_validator_invalid_defaults_to_info(self, monkeypatch):
        monkeypatch.setenv("CF_CLI_LOGGING__LEVEL", "INVALID")
        settings = CFSettings()
        assert settings.logging.level == LogLevel.INFO
    
    def test_metrics_port_valid_range(self):
        settings = CFSettings(observability={"metrics_port": 8080})
        assert settings.observability.metrics_port == 8080
    
    def test_metrics_port_below_1024_raises(self):
        with pytest.raises(ValueError):
            CFSettings(observability={"metrics_port": 80})


class TestCFSettingsSingleton:
    """Test singleton behavior."""
    
    def test_get_cf_settings_returns_same_instance(self):
        s1 = get_cf_settings()
        s2 = get_cf_settings()
        assert s1 is s2
    
    def test_reload_cf_settings_returns_new_instance(self):
        s1 = get_cf_settings()
        s2 = reload_cf_settings()
        assert s1 is not s2
    
    def test_env_change_requires_reload(self, monkeypatch):
        s1 = get_cf_settings()
        assert s1.debug is False
        
        monkeypatch.setenv("CF_CLI_DEBUG", "true")
        s2 = get_cf_settings()
        assert s2.debug is False  # Still cached
        
        s3 = reload_cf_settings()
        assert s3.debug is True  # Now updated


class TestCFSettingsApplyEnv:
    """Test apply_to_environment() exports."""
    
    def test_apply_exports_csv_root(self):
        settings = CFSettings()
        settings.apply_to_environment()
        assert "CF_CLI_CSV_ROOT" in os.environ
        assert "csv" in os.environ["CF_CLI_CSV_ROOT"]
    
    def test_apply_exports_log_level(self):
        settings = CFSettings()
        settings.apply_to_environment()
        assert os.environ["CF_CLI_LOG_LEVEL"] == "INFO"
    
    def test_apply_exports_quiet_mode_0(self):
        settings = CFSettings()
        settings.apply_to_environment()
        assert os.environ["CF_CLI_QUIET_MODE"] == "0"
    
    def test_apply_exports_unified_log_backend(self):
        settings = CFSettings()
        settings.apply_to_environment()
        assert os.environ["UNIFIED_LOG_BACKEND"] == "direct"


class TestQuietModeIntegration:
    """Test quiet mode side effects."""
    
    def test_quiet_mode_disables_rich(self):
        settings = CFSettings(output={"quiet": True})
        assert settings.logging.rich_enabled is False
        assert settings.logging.rich_mirror is False
        assert settings.logging.backend == "direct"
    
    def test_enable_quiet_mode_method(self):
        settings = CFSettings()
        settings.logging.rich_enabled = True
        settings.enable_quiet_mode()
        assert settings.logging.rich_enabled is False


class TestRichModeIntegration:
    """Test rich mode enabling."""
    
    def test_enable_rich_mode_method(self):
        settings = CFSettings()
        settings.enable_rich_mode()
        assert settings.logging.rich_enabled is True
        assert settings.logging.rich_mirror is True
        assert settings.logging.backend == "loguru"
```

---

## 10. Implementation Status

### Completed Issues

| Issue | Title | Status | Commit | Coverage |
|-------|-------|--------|--------|----------|
| CF-188 | Add pydantic dependencies | ✅ Done | - | - |
| CF-189 | BaseAppSettings foundation | ✅ Done | - | 99.05% |
| CF-203 | Write CFSettings tests | ✅ Done | `f5860a16` | 94.12% (54 tests) |
| CF-204 | Integrate into cf_cli.py | ✅ Done | `588247da` | - |

### Remaining Issues

| Issue | Title | Status | Notes |
|-------|-------|--------|-------|
| CF-202 | Remove legacy config code | 📋 Pending | ~180 lines to remove |
| CF-201 | Final validation & testing | 📋 Pending | Regression testing |

### Key Discoveries

1. **Pydantic Alias Kwarg Pattern**: Fields with `alias="CF_CLI_*"` require using the alias name as the kwarg:
   ```python
   # ❌ WRONG
   settings = CFSettings(lazy_mode=True)  # lazy_mode stays False!
   
   # ✅ CORRECT
   settings = CFSettings(CF_CLI_LAZY_MODE=True)  # Works!
   ```

2. **CF-204 Simplification**: `_root_callback()` reduced from ~130 lines to ~55 lines

---

**Plan Complete**: 2025-12-03  
**Implementation Status**: ✅ Core implementation complete (CF-203, CF-204)
**Remaining**: CF-202 (legacy removal), CF-201 (final validation)
