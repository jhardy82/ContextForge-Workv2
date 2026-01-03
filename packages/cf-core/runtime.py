"""Runtime and RuntimeBuilder for ContextForge session management.

This module implements the core Runtime abstraction that provides:
- Session-level correlation ID tracking
- Plugin logger provisioning with correlation context
- Centralized access to console, config, and task manager

Target Architecture (CF-133):
    RuntimeBuilder → Runtime with correlation_id
    Runtime.logger_for_plugin() → Logger with bound correlation

Reference: tests/python/test_correlation_propagation.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from cf_core.logger_provider import LoggerProvider, StdlibLoggerProvider, generate_correlation_id

if TYPE_CHECKING:
    from rich.console import Console


# ════════════════════════════════════════════════════════════════════════════
# Runtime - Session Container
# ════════════════════════════════════════════════════════════════════════════


@dataclass
class Runtime:
    """Runtime container for session-level state and services.

    The Runtime holds:
    - correlation_id: Session-wide correlation for log tracing
    - logger_provider: Abstraction for creating loggers
    - console: Rich console for output (optional)
    - task_manager: Task management interface (optional)
    - config: Configuration dictionary (optional)
    - workspace_root: Working directory path

    Plugin loggers created via logger_for_plugin() automatically
    inherit the session correlation_id.
    """

    correlation_id: str
    logger_provider: LoggerProvider
    console: Console | None = None
    task_manager: Any = None
    config: dict[str, Any] = field(default_factory=dict)
    workspace_root: Path = field(default_factory=Path.cwd)

    def logger_for_plugin(
        self,
        plugin_id: str,
        *,
        context: dict[str, Any] | None = None,
    ) -> Any:
        """Get a logger for a plugin with session correlation bound.

        The session correlation_id is automatically bound to the logger.
        Additional context can be provided but CANNOT override correlation_id.

        Args:
            plugin_id: Unique identifier for the plugin
            context: Additional context to bind (plugin_scope_id, etc.)

        Returns:
            A logger instance with correlation_id and plugin_id bound

        Example:
            logger = runtime.logger_for_plugin(
                "my-plugin",
                context={"plugin_scope_id": "exec-123"}
            )
            logger.info("Processing started")
            # Output includes: correlation_id=<session>, plugin_scope_id=exec-123
        """
        # Merge context, ensuring correlation_id cannot be overridden
        extra_context = context.copy() if context else {}

        # Correlation ID from session is authoritative - prevent override
        extra_context.pop("correlation_id", None)

        return self.logger_provider.get_logger(
            plugin_id=plugin_id,
            correlation_id=self.correlation_id,
            **extra_context,
        )


# ════════════════════════════════════════════════════════════════════════════
# RuntimeBuilder - Fluent Construction
# ════════════════════════════════════════════════════════════════════════════


class RuntimeBuilder:
    """Fluent builder for Runtime instances.

    Provides a clean, testable way to construct Runtime with all
    required and optional dependencies.

    Example:
        runtime = (
            RuntimeBuilder()
            .with_correlation_id(generate_correlation_id())
            .with_logger_provider(StdlibLoggerProvider())
            .with_console(Console())
            .build()
        )
    """

    def __init__(self) -> None:
        """Initialize builder with defaults."""
        self._correlation_id: str | None = None
        self._logger_provider: LoggerProvider | None = None
        self._console: Console | None = None
        self._task_manager: Any = None
        self._config: dict[str, Any] = {}
        self._workspace_root: Path = Path.cwd()

    def with_correlation_id(self, correlation_id: str) -> RuntimeBuilder:
        """Set the session correlation ID.

        Args:
            correlation_id: 32-char hex UUID for session tracing

        Returns:
            Self for fluent chaining
        """
        self._correlation_id = correlation_id
        return self

    def with_logger_provider(self, provider: LoggerProvider) -> RuntimeBuilder:
        """Set the logger provider.

        Args:
            provider: LoggerProvider implementation (Stdlib or Structlog)

        Returns:
            Self for fluent chaining
        """
        self._logger_provider = provider
        return self

    def with_console(self, console: Console | None) -> RuntimeBuilder:
        """Set the Rich console for output.

        Args:
            console: Rich Console instance or None

        Returns:
            Self for fluent chaining
        """
        self._console = console
        return self

    def with_task_manager(self, task_manager: Any) -> RuntimeBuilder:
        """Set the task manager interface.

        Args:
            task_manager: Task manager implementation

        Returns:
            Self for fluent chaining
        """
        self._task_manager = task_manager
        return self

    def with_config(self, config: dict[str, Any] | None) -> RuntimeBuilder:
        """Set the configuration dictionary.

        Args:
            config: Configuration dict or None

        Returns:
            Self for fluent chaining
        """
        self._config = config or {}
        return self

    def with_workspace_root(self, path: Path) -> RuntimeBuilder:
        """Set the workspace root path.

        Args:
            path: Path to workspace root

        Returns:
            Self for fluent chaining
        """
        self._workspace_root = path
        return self

    def build(self) -> Runtime:
        """Build the Runtime instance.

        Returns:
            Configured Runtime instance

        Raises:
            ValueError: If required fields are missing
        """
        # Apply defaults for missing required fields
        correlation_id = self._correlation_id or generate_correlation_id()
        logger_provider = self._logger_provider or StdlibLoggerProvider()

        return Runtime(
            correlation_id=correlation_id,
            logger_provider=logger_provider,
            console=self._console,
            task_manager=self._task_manager,
            config=self._config,
            workspace_root=self._workspace_root,
        )


# ════════════════════════════════════════════════════════════════════════════
# Module Exports
# ════════════════════════════════════════════════════════════════════════════

__all__ = [
    "Runtime",
    "RuntimeBuilder",
]
