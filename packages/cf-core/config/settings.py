"""ContextForge Unified Settings Module.

Provides pydantic-settings based configuration with layered sources:
1. CLI flags (--machine, --output, etc.) - highest priority
2. Environment variables (CF_*)
3. Project TOML (.contextforge.toml)
4. User TOML (~/.contextforge/config.toml)
5. Defaults - lowest priority

Merges configuration patterns from:
- cf_cli.py (UNIFIED_LOG_*, DBCLI_RICH_ENABLE)
- cf_core/mcp/taskman_server.py (TASKMAN_DB_PATH)
- Party Mode design specification (pydantic-settings + TOML)

Usage:
    from cf_core.config import get_settings

    settings = get_settings()
    if settings.machine_mode:
        # Output JSON for agent consumption
        ...
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# =============================================================================
# Output Format Types
# =============================================================================

OutputFormat = Literal["json", "jsonl", "table", "yaml", "csv"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LogFormat = Literal["text", "json", "jsonl"]
McpTransport = Literal["stdio", "sse", "websocket"]


# =============================================================================
# Settings Classes
# =============================================================================

class OutputSettings(BaseSettings):
    """Output configuration for CLI and agent consumption."""

    model_config = SettingsConfigDict(
        env_prefix="CONTEXTFORGE_OUTPUT_",
        extra="ignore",
    )

    format: OutputFormat = Field(
        default="table",
        description="Output format: json, jsonl, table, yaml, csv",
    )
    color: bool = Field(
        default=True,
        description="Enable colored output (disabled in machine mode)",
    )
    verbose: bool = Field(
        default=False,
        description="Enable verbose output",
    )
    quiet: bool = Field(
        default=False,
        description="Suppress non-essential output",
    )
    session_log_path: Path | None = Field(
        default=None,
        description="Path for CLI session JSONL logging (legacy: UNIFIED_CLI_LOG_PATH)",
    )


class LoggingSettings(BaseSettings):
    """Logging configuration merging UNIFIED_LOG_* and structlog patterns."""

    model_config = SettingsConfigDict(
        env_prefix="CONTEXTFORGE_LOGGING_",
        extra="ignore",
    )

    level: LogLevel = Field(
        default="INFO",
        description="Log level threshold",
    )
    format: LogFormat = Field(
        default="jsonl",
        description="Log format: text (human), json, jsonl (machine)",
    )
    file: Path | None = Field(
        default=None,
        description="Log file path (None for stdout only)",
    )
    console: str = Field(
        default="stderr",
        description="Console output routing: stderr, stdout, none",
    )
    max_mb: float = Field(
        default=50.0,
        description="Maximum log file size in MB before rotation",
    )
    backups: int = Field(
        default=5,
        description="Number of rotated log files to retain",
    )
    suppress_json_console: bool = Field(
        default=True,
        description="Suppress JSON output to console (legacy: UNIFIED_LOG_SUPPRESS_JSON)",
    )
    rich_mirror: bool = Field(
        default=False,
        description="Mirror Rich output to logs (legacy: UNIFIED_LOG_RICH_MIRROR)",
    )
    run_id: str | None = Field(
        default=None,
        description="Execution run identifier (legacy: UNIFIED_RUN_ID)",
    )
    enable_hash_chain: bool = Field(
        default=False,
        description="Enable cryptographic hash chaining for event lineage (legacy: UNIFIED_LOG_HASH_CHAIN)",
    )


class DatabaseSettings(BaseSettings):
    """Database configuration for SQLite and PostgreSQL backends."""

    model_config = SettingsConfigDict(
        env_prefix="CONTEXTFORGE_DB_",
        extra="ignore",
    )

    url: SecretStr = Field(
        default="sqlite:///db/taskman.db",
        description="Database connection URL",
    )
    pool_size: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Connection pool size",
    )
    echo: bool = Field(
        default=False,
        description="Echo SQL statements for debugging",
    )

    @field_validator("url", mode="before")
    @classmethod
    def normalize_sqlite_path(cls, v: str | SecretStr) -> str | SecretStr:
        """Normalize SQLite paths to absolute paths."""
        # Unwrap if already SecretStr (e.g. from copy)
        val = v.get_secret_value() if isinstance(v, SecretStr) else v

        if val.startswith("sqlite:///") and not val.startswith("sqlite:////"):
            # Relative path - make absolute from project root
            rel_path = val.replace("sqlite:///", "")
            abs_path = Path.cwd() / rel_path
            return f"sqlite:///{abs_path}"
        return v


class McpSettings(BaseSettings):
    """MCP (Model Context Protocol) server configuration."""

    model_config = SettingsConfigDict(
        env_prefix="CONTEXTFORGE_MCP_",
        extra="ignore",
    )

    enabled: bool = Field(
        default=True,
        description="Enable MCP server functionality",
    )
    transport: McpTransport = Field(
        default="stdio",
        description="MCP transport protocol",
    )
    timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="MCP operation timeout in seconds",
    )
    db_path: str = Field(
        default="db/taskman.db",
        description="Database path for MCP operations (legacy: TASKMAN_DB_PATH)",
    )


class ProjectSettings(BaseSettings):
    """Project context and workspace configuration."""

    model_config = SettingsConfigDict(
        env_prefix="CONTEXTFORGE_PROJECT_",
        extra="ignore",
    )

    root: Path | None = Field(
        default=None,
        description="Project root directory (auto-detected if None)",
    )
    name: str | None = Field(
        default=None,
        description="Project name (from config or directory name)",
    )

    @model_validator(mode="after")
    def detect_project_root(self) -> ProjectSettings:
        """Auto-detect project root if not specified."""
        if self.root is None:
            # Look for common project markers
            markers = [".git", "pyproject.toml", ".contextforge.toml", "cf_core"]
            cwd = Path.cwd()
            for parent in [cwd, *cwd.parents]:
                if any((parent / marker).exists() for marker in markers):
                    self.root = parent
                    break
            else:
                self.root = cwd

        if self.name is None and self.root:
            self.name = self.root.name

        return self


# =============================================================================
# Main Settings Class
# =============================================================================

class ContextForgeSettings(BaseSettings):
    """Unified ContextForge configuration.

    Merges all configuration sources with layered priority:
    1. CLI flags (applied via apply_cli_overrides)
    2. Environment variables (CONTEXTFORGE_*)
    3. Project TOML (.contextforge.toml)
    4. User TOML (~/.contextforge/config.toml)
    5. Defaults

    Legacy Compatibility:
    - UNIFIED_LOG_* variables mapped to logging.*
    - DBCLI_RICH_ENABLE mapped to output.color
    - TASKMAN_DB_PATH mapped to mcp.db_path
    """

    model_config = SettingsConfigDict(
        env_prefix="CONTEXTFORGE_",
        env_nested_delimiter="__",
        env_file=".env",
        extra="ignore",
        validate_default=True,
    )

    # Machine mode - universal agent flag
    machine_mode: bool = Field(
        default=False,
        description="Enable machine mode for agent consumption (JSON output, no color)",
    )

    # Nested configuration sections
    output: OutputSettings = Field(default_factory=OutputSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    mcp: McpSettings = Field(default_factory=McpSettings)
    project: ProjectSettings = Field(default_factory=ProjectSettings)

    # Version info
    version: str = Field(default="0.1.0", description="cf_core version")

    @model_validator(mode="before")
    @classmethod
    def load_legacy_env_vars(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Map legacy environment variables to new schema."""
        legacy_mappings = {
            # UNIFIED_LOG_* -> logging.*
            "UNIFIED_LOG_SUPPRESS_JSON": ("logging", "suppress_json_console"),
            "UNIFIED_LOG_RICH_MIRROR": ("logging", "rich_mirror"),
            "UNIFIED_LOG_PATH": ("logging", "file"),
            "UNIFIED_LOG_LEVEL": ("logging", "level"),
            "UNIFIED_LOG_CONSOLE": ("logging", "console"),
            "UNIFIED_LOG_ROTATE_MAX_MB": ("logging", "max_mb"),
            "UNIFIED_LOG_ROTATE_BACKUPS": ("logging", "backups"),
            "UNIFIED_RUN_ID": ("logging", "run_id"),
            "UNIFIED_LOG_HASH_CHAIN": ("logging", "enable_hash_chain"),
            "UNIFIED_CLI_LOG_PATH": ("output", "session_log_path"),
            # DBCLI_* -> output.*
            "DBCLI_RICH_ENABLE": ("output", "color"),
            # TASKMAN_* -> mcp.*
            "TASKMAN_DB_PATH": ("mcp", "db_path"),
        }

        for legacy_var, (section, key) in legacy_mappings.items():
            if legacy_var in os.environ:
                # Check for precedence: New CONTEXTFORGE_ variable overrides legacy
                # We need to construct the expected new variable name
                # Sections map to specific prefixes based on their Settings classes
                prefixes = {
                    "logging": "CONTEXTFORGE_LOGGING_",
                    "output": "CONTEXTFORGE_OUTPUT_",
                    "mcp": "CONTEXTFORGE_MCP_",
                }

                # Default behavior if section not found in map (should not happen with current mappings)
                prefix = prefixes.get(section, f"CONTEXTFORGE_{section.upper()}__")
                new_var = f"{prefix}{key.upper()}"

                if new_var in os.environ:
                    # New variable exists, ignore legacy
                    continue

                value = os.environ[legacy_var]
                # Convert string booleans
                if value.lower() in ("true", "1", "yes"):
                    value = True
                elif value.lower() in ("false", "0", "no"):
                    value = False

                if section not in data:
                    data[section] = {}
                if isinstance(data[section], dict):
                    data[section][key] = value

        # Fallback: if UNIFIED_LOG_PATH is set but UNIFIED_CLI_LOG_PATH is not,
        # use UNIFIED_LOG_PATH for session logs too.
        if "UNIFIED_LOG_PATH" in os.environ and "UNIFIED_CLI_LOG_PATH" not in os.environ:
            if "output" not in data:
                data["output"] = {}
            if isinstance(data["output"], dict):
                data["output"]["session_log_path"] = os.environ["UNIFIED_LOG_PATH"]

        return data

    def apply_machine_mode(self) -> ContextForgeSettings:
        """Apply machine mode overrides for agent consumption.

        When machine_mode is True:
        - Output format → JSON
        - Color → disabled
        - Logging format → JSONL
        - Verbose → disabled

        Returns:
            Self for method chaining
        """
        if self.machine_mode:
            self.output.format = "json"
            self.output.color = False
            self.output.verbose = False
            self.logging.format = "jsonl"
        return self

    def apply_cli_overrides(
        self,
        machine: bool | None = None,
        output_format: OutputFormat | None = None,
        no_color: bool | None = None,
        verbose: bool | None = None,
        quiet: bool | None = None,
        log_level: LogLevel | None = None,
    ) -> ContextForgeSettings:
        """Apply CLI flag overrides (highest priority).

        Args:
            machine: Enable machine mode
            output_format: Override output format
            no_color: Disable colored output
            verbose: Enable verbose output
            quiet: Enable quiet mode
            log_level: Override log level

        Returns:
            Self for method chaining
        """
        if machine is not None:
            self.machine_mode = machine
        if output_format is not None:
            self.output.format = output_format
        if no_color is not None:
            self.output.color = not no_color
        if verbose is not None:
            self.output.verbose = verbose
        if quiet is not None:
            self.output.quiet = quiet
        if log_level is not None:
            self.logging.level = log_level

        # Apply machine mode after all overrides
        return self.apply_machine_mode()

    def to_env_dict(self) -> dict[str, str]:
        """Export settings as environment variables for subprocess inheritance."""
        env = {}

        # Core settings
        env["CONTEXTFORGE_MACHINE_MODE"] = str(self.machine_mode).lower()

        # Output settings
        env["CONTEXTFORGE_OUTPUT_FORMAT"] = self.output.format
        env["CONTEXTFORGE_OUTPUT_COLOR"] = str(self.output.color).lower()
        env["CONTEXTFORGE_OUTPUT_VERBOSE"] = str(self.output.verbose).lower()

        # Logging settings
        env["CONTEXTFORGE_LOGGING_LEVEL"] = self.logging.level
        env["CONTEXTFORGE_LOGGING_FORMAT"] = self.logging.format
        env["CONTEXTFORGE_LOGGING_CONSOLE"] = str(self.logging.console)

        # Legacy compatibility
        env["UNIFIED_LOG_SUPPRESS_JSON"] = str(self.logging.suppress_json_console).lower()
        env["DBCLI_RICH_ENABLE"] = "1" if self.output.color else "0"

        # Database/MCP
        env["CONTEXTFORGE_DB_URL"] = self.database.url.get_secret_value()
        env["TASKMAN_DB_PATH"] = self.mcp.db_path

        # File paths
        if self.logging.file:
            env["UNIFIED_LOG_PATH"] = str(self.logging.file)
        if self.output.session_log_path:
            env["UNIFIED_CLI_LOG_PATH"] = str(self.output.session_log_path)

        return env


# =============================================================================
# Settings Factory
# =============================================================================

@lru_cache
def get_settings() -> ContextForgeSettings:
    """Get cached settings instance.

    Settings are loaded once and cached for the process lifetime.
    Use get_settings.cache_clear() to reload.

    Returns:
        ContextForgeSettings instance
    """
    return ContextForgeSettings()


def get_fresh_settings() -> ContextForgeSettings:
    """Get fresh settings instance (bypasses cache).

    Use this when you need to reload settings or apply CLI overrides.

    Returns:
        New ContextForgeSettings instance
    """
    return ContextForgeSettings()


# =============================================================================
# TOML Loader (for future use with toml_file support)
# =============================================================================

def load_toml_config(path: Path) -> dict[str, Any]:
    """Load configuration from TOML file.

    Args:
        path: Path to TOML file

    Returns:
        Configuration dictionary
    """
    if not path.exists():
        return {}

    try:
        # Python 3.11+ has tomllib in stdlib
        import tomllib
        with open(path, "rb") as f:
            return tomllib.load(f)
    except ImportError:
        # Fallback to tomli for Python < 3.11
        try:
            import tomli
            with open(path, "rb") as f:
                return tomli.load(f)
        except ImportError:
            # No TOML library available
            return {}


__all__ = [
    "ContextForgeSettings",
    "OutputSettings",
    "LoggingSettings",
    "DatabaseSettings",
    "McpSettings",
    "ProjectSettings",
    "OutputFormat",
    "LogLevel",
    "LogFormat",
    "McpTransport",
    "get_settings",
    "get_fresh_settings",
    "load_toml_config",
]
