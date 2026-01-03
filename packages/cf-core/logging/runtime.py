"""Runtime configuration and builder for cf_core.logging.

Provides RuntimeBuilder for fluent configuration of logging runtimes and
Runtime for managing configured logging environments with provider and context.

Extracted from cf_core.logger_provider per Phase 1 consolidation plan.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any
from uuid import uuid4

# Check if structlog is available
try:
    import structlog
    _STRUCTLOG_AVAILABLE = True
except ImportError:
    _STRUCTLOG_AVAILABLE = False


# ==============================================================================
# Correlation ID Generation
# ==============================================================================


def generate_correlation_id() -> str:
    """Generate a correlation ID for session tracking.

    Returns a 32-character lowercase hex string (UUID4 without hyphens).
    Contains no PII or secrets - only random hex characters.
    """
    return uuid4().hex


# ==============================================================================
# JSON Formatter for Structured Logging
# ==============================================================================


class _JsonFormatter(logging.Formatter):
    """Custom JSON formatter that extracts correlation_id from extra fields."""

    def format(self, record: logging.LogRecord) -> str:
        # Build the log data structure
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include correlation_id and other extra fields
        for key, value in record.__dict__.items():
            if key not in (
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "lineno", "funcName", "created", "msecs",
                "relativeCreated", "thread", "threadName", "processName",
                "process", "message", "exc_info", "exc_text", "stack_info",
                "getMessage", "correlation_id", "plugin_id", "plugin_scope_id",
            ):
                if not key.startswith("_"):
                    log_data[key] = value

        return json.dumps(log_data)


# ==============================================================================
# Abstract Base Logger Provider
# ==============================================================================


class LoggerProvider(ABC):
    """Abstract base class for logger providers with correlation support."""

    def __init__(
        self,
        name: str = "cf_core",
        default_context: dict[str, Any] | None = None,
    ):
        self.name = name
        self.default_context = default_context or {}

    @abstractmethod
    def get_logger(
        self,
        plugin_id: str,
        correlation_id: str | None = None,
        **extra_context: Any,
    ) -> Any:
        """Get a logger bound to the given plugin with correlation context.

        Args:
            plugin_id: Identifier for the plugin requesting the logger
            correlation_id: Session correlation ID (from Runtime)
            **extra_context: Additional context to bind to the logger

        Returns:
            A logger instance with correlation_id and plugin_id bound
        """


# ==============================================================================
# Stdlib Logger Provider
# ==============================================================================


class StdlibLoggerProvider(LoggerProvider):
    """Logger provider using Python's standard logging library.

    Returns logging.LoggerAdapter instances with correlation context in 'extra'.
    Suitable when structlog is not available or not desired.
    """

    def get_logger(
        self,
        plugin_id: str,
        correlation_id: str | None = None,
        **extra_context: Any,
    ) -> logging.LoggerAdapter:
        """Get a stdlib LoggerAdapter with correlation context.

        Args:
            plugin_id: Identifier for the plugin
            correlation_id: Session correlation ID
            **extra_context: Additional context fields

        Returns:
            logging.LoggerAdapter with extra dict containing correlation_id
        """
        base_logger = logging.getLogger(f"{self.name}.{plugin_id}")

        # Build extra context - session correlation_id is immutable
        extra = dict(self.default_context)
        extra["plugin_id"] = plugin_id

        # Use provided correlation_id, or fall back to default_context, or generate
        if correlation_id is not None:
            extra["correlation_id"] = correlation_id
        elif "correlation_id" not in extra:
            extra["correlation_id"] = generate_correlation_id()

        # Add extra context (but never override correlation_id from session)
        for key, value in extra_context.items():
            if key != "correlation_id":  # Protect session correlation
                extra[key] = value

        return logging.LoggerAdapter(base_logger, extra)


# ==============================================================================
# Structlog Logger Provider
# ==============================================================================


class StructlogLoggerProvider(LoggerProvider):
    """Logger provider using structlog for structured logging.

    Returns bound loggers with correlation context automatically included.
    Falls back to StdlibLoggerProvider if structlog is not available.
    """

    _fallback: StdlibLoggerProvider | None

    def __init__(
        self,
        name: str = "cf_core",
        default_context: dict[str, Any] | None = None,
    ):
        super().__init__(name, default_context)
        if not _STRUCTLOG_AVAILABLE:
            self._fallback = StdlibLoggerProvider(name, default_context)
        else:
            self._fallback = None
            self._configure_structlog()

    def _configure_structlog(self) -> None:
        """Configure structlog with correlation-aware processors."""
        if not _STRUCTLOG_AVAILABLE:
            return

        # Configure structlog if not already configured
        if not structlog.is_configured():
            structlog.configure(
                processors=[
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.add_logger_name,
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.JSONRenderer(),
                ],
                context_class=dict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )

    def get_logger(
        self,
        plugin_id: str,
        correlation_id: str | None = None,
        **extra_context: Any,
    ) -> Any:
        """Get a structlog BoundLogger with correlation context.

        Args:
            plugin_id: Identifier for the plugin
            correlation_id: Session correlation ID
            **extra_context: Additional context fields

        Returns:
            structlog.BoundLogger with correlation_id bound
        """
        if self._fallback is not None:
            return self._fallback.get_logger(
                plugin_id, correlation_id, **extra_context
            )

        # Build context - session correlation_id is immutable
        context = dict(self.default_context)
        context["plugin_id"] = plugin_id

        # Use provided correlation_id, or fall back to default_context, or generate
        if correlation_id is not None:
            context["correlation_id"] = correlation_id
        elif "correlation_id" not in context:
            context["correlation_id"] = generate_correlation_id()

        # Add extra context (but never override correlation_id from session)
        for key, value in extra_context.items():
            if key != "correlation_id":  # Protect session correlation
                context[key] = value

        # Get structlog logger bound with context
        logger = structlog.get_logger(f"{self.name}.{plugin_id}")
        return logger.bind(**context)


# ==============================================================================
# Runtime Configuration
# ==============================================================================


class LoggingRuntimeConfig:
    """Configuration for the logging runtime.

    Immutable configuration object that holds all settings for a logging runtime.
    Created by RuntimeBuilder and consumed by Runtime.

    Attributes:
        provider_name: Name of the logging provider
        log_level: Logging level (e.g., "DEBUG", "INFO")
        log_format: Format type ("json" or "text")
        default_context: Base context applied to all log entries
        correlation_id: Session correlation ID
        enable_console: Whether to enable console output
        enable_file: Whether to enable file output
        file_path: Path to log file (if file output enabled)
    """

    __slots__ = (
        "provider_name",
        "log_level",
        "log_format",
        "default_context",
        "correlation_id",
        "enable_console",
        "enable_file",
        "file_path",
    )

    def __init__(
        self,
        provider_name: str = "default",
        log_level: str = "INFO",
        log_format: str = "json",
        default_context: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        enable_console: bool = True,
        enable_file: bool = False,
        file_path: str | None = None,
    ) -> None:
        """Initialize logging runtime configuration.

        Args:
            provider_name: Name of the logging provider
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_format: Output format (json or text)
            default_context: Base context for all log entries
            correlation_id: Session correlation ID
            enable_console: Enable console output
            enable_file: Enable file output
            file_path: Path to log file
        """
        self.provider_name = provider_name
        self.log_level = log_level
        self.log_format = log_format
        self.default_context = default_context or {}
        self.correlation_id = correlation_id or generate_correlation_id()
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.file_path = file_path


# ==============================================================================
# Runtime Class
# ==============================================================================


class Runtime:
    """Logging runtime instance.

    Encapsulates a configured logging environment with provider and context.
    Created exclusively by RuntimeBuilder.build().

    Example:
        runtime = RuntimeBuilder().with_level("DEBUG").build()
        logger = runtime.logger("my_plugin")
        logger.info("message")
    """

    def __init__(self, config: LoggingRuntimeConfig) -> None:
        """Initialize the runtime with configuration.

        Args:
            config: Validated runtime configuration
        """
        self._config = config
        self._provider = StructlogLoggerProvider(
            name=config.provider_name,
            default_context={
                **config.default_context,
                "correlation_id": config.correlation_id,
            },
        )
        self._loggers: dict[str, Any] = {}

    @property
    def correlation_id(self) -> str:
        """Get the session correlation ID."""
        return self._config.correlation_id

    @property
    def config(self) -> LoggingRuntimeConfig:
        """Get the runtime configuration."""
        return self._config

    @property
    def provider(self) -> StructlogLoggerProvider:
        """Get the underlying logging provider."""
        return self._provider

    def logger(self, plugin_id: str, **extra_context: Any) -> Any:
        """Get a logger for the specified plugin.

        Args:
            plugin_id: Identifier for the plugin/module
            **extra_context: Additional context fields

        Returns:
            Bound logger instance
        """
        cache_key = f"{plugin_id}:{hash(frozenset(extra_context.items()))}"

        if cache_key not in self._loggers:
            self._loggers[cache_key] = self._provider.get_logger(
                plugin_id=plugin_id,
                correlation_id=self._config.correlation_id,
                **extra_context,
            )

        return self._loggers[cache_key]


# ==============================================================================
# Runtime Builder
# ==============================================================================


class RuntimeBuilder:
    """Builder for creating Runtime instances.

    Fluent builder pattern for constructing logging runtimes with validated
    configuration. Supports method chaining for readable configuration.

    Example:
        runtime = (
            RuntimeBuilder()
            .with_name("my_app")
            .with_level("DEBUG")
            .with_json_format()
            .with_context(environment="production")
            .build()
        )
    """

    # Valid log levels
    VALID_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})
    VALID_FORMATS = frozenset({"json", "text"})

    def __init__(self) -> None:
        """Initialize builder with default values."""
        self._provider_name: str = "default"
        self._log_level: str = "INFO"
        self._log_format: str = "json"
        self._default_context: dict[str, Any] = {}
        self._correlation_id: str | None = None
        self._enable_console: bool = True
        self._enable_file: bool = False
        self._file_path: str | None = None

    def with_name(self, name: str) -> RuntimeBuilder:
        """Set the provider name.

        Args:
            name: Provider/runtime name

        Returns:
            Self for method chaining
        """
        if not name or not name.strip():
            raise ValueError("Provider name cannot be empty")
        self._provider_name = name.strip()
        return self

    def with_level(self, level: str) -> RuntimeBuilder:
        """Set the logging level.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

        Returns:
            Self for method chaining

        Raises:
            ValueError: If level is invalid
        """
        level_upper = level.upper()
        if level_upper not in self.VALID_LEVELS:
            raise ValueError(
                f"Invalid log level: {level}. "
                f"Valid levels: {', '.join(sorted(self.VALID_LEVELS))}"
            )
        self._log_level = level_upper
        return self

    def with_format(self, fmt: str) -> RuntimeBuilder:
        """Set the log output format.

        Args:
            fmt: Format type (json or text)

        Returns:
            Self for method chaining

        Raises:
            ValueError: If format is invalid
        """
        fmt_lower = fmt.lower()
        if fmt_lower not in self.VALID_FORMATS:
            raise ValueError(
                f"Invalid format: {fmt}. "
                f"Valid formats: {', '.join(sorted(self.VALID_FORMATS))}"
            )
        self._log_format = fmt_lower
        return self

    def with_json_format(self) -> RuntimeBuilder:
        """Configure JSON output format.

        Returns:
            Self for method chaining
        """
        self._log_format = "json"
        return self

    def with_text_format(self) -> RuntimeBuilder:
        """Configure text output format.

        Returns:
            Self for method chaining
        """
        self._log_format = "text"
        return self

    def with_context(self, **context: Any) -> RuntimeBuilder:
        """Add default context fields.

        Args:
            **context: Context key-value pairs

        Returns:
            Self for method chaining
        """
        self._default_context.update(context)
        return self

    def with_correlation_id(self, correlation_id: str) -> RuntimeBuilder:
        """Set the session correlation ID.

        Args:
            correlation_id: Correlation ID for tracing

        Returns:
            Self for method chaining
        """
        if not correlation_id or not correlation_id.strip():
            raise ValueError("Correlation ID cannot be empty")
        self._correlation_id = correlation_id.strip()
        return self

    def with_console(self, enabled: bool = True) -> RuntimeBuilder:
        """Configure console output.

        Args:
            enabled: Whether to enable console output

        Returns:
            Self for method chaining
        """
        self._enable_console = enabled
        return self

    def with_file(self, path: str) -> RuntimeBuilder:
        """Configure file output.

        Args:
            path: Path to log file

        Returns:
            Self for method chaining
        """
        if not path or not path.strip():
            raise ValueError("File path cannot be empty")
        self._enable_file = True
        self._file_path = path.strip()
        return self

    def build(self) -> Runtime:
        """Build and return the configured Runtime.

        Returns:
            Configured Runtime instance

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate file configuration
        if self._enable_file and not self._file_path:
            raise ValueError("File path required when file output is enabled")

        # Create configuration
        config = LoggingRuntimeConfig(
            provider_name=self._provider_name,
            log_level=self._log_level,
            log_format=self._log_format,
            default_context=self._default_context.copy(),
            correlation_id=self._correlation_id,
            enable_console=self._enable_console,
            enable_file=self._enable_file,
            file_path=self._file_path,
        )

        return Runtime(config)


# ==============================================================================
# Module-level convenience functions
# ==============================================================================


def create_runtime(
    name: str = "default",
    level: str = "INFO",
    **context: Any,
) -> Runtime:
    """Create a runtime with common configuration.

    Convenience function for creating a runtime without using the builder
    pattern directly.

    Args:
        name: Provider name
        level: Log level
        **context: Default context fields

    Returns:
        Configured Runtime instance

    Example:
        runtime = create_runtime("my_app", "DEBUG", environment="dev")
    """
    builder = RuntimeBuilder().with_name(name).with_level(level)

    if context:
        builder.with_context(**context)

    return builder.build()
