"""ContextForge Error Handlers Module.

Provides CLI error handling decorators and exception classes for consistent
error propagation and exit code management.

Usage:
    from cf_core.errors import handle_errors, NotFoundError

    @handle_errors
    def my_command():
        if not task:
            raise NotFoundError("Task", "TASK-001")
        ...
"""

from __future__ import annotations

import functools
import sys
import traceback
from collections.abc import Callable
from typing import Any, TypeVar

from cf_core.errors.codes import ExitCode, get_exit_code_for_exception
from cf_core.errors.response import create_error_from_exception

# Type variable for decorated function return type
F = TypeVar("F", bound=Callable[..., Any])


# =============================================================================
# CLI Exception Classes
# =============================================================================


class CLIError(Exception):
    """Base exception for CLI operations.

    All CLI-specific exceptions inherit from this class and carry
    structured information for error responses.

    Attributes:
        message: Human-readable error message
        exit_code: Exit code for CLI termination
        code: Machine-readable error code
        field: Optional field that caused the error
        context: Additional error context
        suggestion: Optional suggestion for fixing the error
    """

    exit_code: ExitCode = ExitCode.GENERAL_ERROR
    code: str = "CLI_ERROR"

    def __init__(
        self,
        message: str,
        *,
        exit_code: ExitCode | None = None,
        code: str | None = None,
        field: str | None = None,
        context: dict[str, Any] | None = None,
        suggestion: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if exit_code is not None:
            self.exit_code = exit_code
        if code is not None:
            self.code = code
        self.field = field
        self.context = context or {}
        self.suggestion = suggestion


class ValidationError(CLIError):
    """Raised when input validation fails.

    Used for schema validation errors, constraint violations,
    and invalid data formats.
    """

    exit_code = ExitCode.VALIDATION_ERROR
    code = "VALIDATION_ERROR"

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        context: dict[str, Any] | None = None,
        suggestion: str | None = None,
    ) -> None:
        super().__init__(
            message,
            field=field,
            context=context,
            suggestion=suggestion,
        )


class NotFoundError(CLIError):
    """Raised when a requested resource cannot be found.

    Provides consistent formatting for resource lookup failures.
    """

    exit_code = ExitCode.NOT_FOUND
    code = "NOT_FOUND"

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        *,
        context: dict[str, Any] | None = None,
        suggestion: str | None = None,
    ) -> None:
        message = f"{resource_type} not found: {resource_id}"
        ctx = context or {}
        ctx["resource_type"] = resource_type
        ctx["resource_id"] = resource_id
        super().__init__(
            message,
            context=ctx,
            suggestion=suggestion or f"Check that the {resource_type.lower()} ID is correct",
        )


class ConflictError(CLIError):
    """Raised when a resource conflict occurs.

    Used for duplicate resources, concurrent modifications,
    and state conflicts.
    """

    exit_code = ExitCode.CONFLICT
    code = "CONFLICT"

    def __init__(
        self,
        message: str,
        *,
        resource_type: str | None = None,
        resource_id: str | None = None,
        context: dict[str, Any] | None = None,
        suggestion: str | None = None,
    ) -> None:
        ctx = context or {}
        if resource_type:
            ctx["resource_type"] = resource_type
        if resource_id:
            ctx["resource_id"] = resource_id
        super().__init__(
            message,
            context=ctx,
            suggestion=suggestion,
        )


class ConfigurationError(CLIError):
    """Raised when configuration is invalid or missing.

    Used for config file errors, missing environment variables,
    and invalid settings.
    """

    exit_code = ExitCode.CONFIG_ERROR
    code = "CONFIGURATION_ERROR"

    def __init__(
        self,
        message: str,
        *,
        config_key: str | None = None,
        context: dict[str, Any] | None = None,
        suggestion: str | None = None,
    ) -> None:
        ctx = context or {}
        if config_key:
            ctx["config_key"] = config_key
        super().__init__(
            message,
            field=config_key,
            context=ctx,
            suggestion=suggestion,
        )


class DatabaseError(CLIError):
    """Raised when a database operation fails.

    Used for connection errors, query failures, and
    data integrity issues.
    """

    exit_code = ExitCode.DATABASE_ERROR
    code = "DATABASE_ERROR"

    def __init__(
        self,
        message: str,
        *,
        operation: str | None = None,
        context: dict[str, Any] | None = None,
        suggestion: str | None = None,
    ) -> None:
        ctx = context or {}
        if operation:
            ctx["operation"] = operation
        super().__init__(
            message,
            context=ctx,
            suggestion=suggestion or "Check database connection and configuration",
        )


class ConnectionError(CLIError):
    """Raised when a network/connection operation fails.

    Used for API errors, network timeouts, and
    connection refused scenarios.
    """

    exit_code = ExitCode.CONNECTION_ERROR
    code = "CONNECTION_ERROR"

    def __init__(
        self,
        message: str,
        *,
        host: str | None = None,
        port: int | None = None,
        context: dict[str, Any] | None = None,
        suggestion: str | None = None,
    ) -> None:
        ctx = context or {}
        if host:
            ctx["host"] = host
        if port:
            ctx["port"] = port
        super().__init__(
            message,
            context=ctx,
            suggestion=suggestion or "Check network connectivity and service availability",
        )


class InternalError(CLIError):
    """Raised when an internal error occurs.

    Used for bugs, unexpected states, and system failures.
    These should be logged and reported.
    """

    exit_code = ExitCode.INTERNAL_ERROR
    code = "INTERNAL_ERROR"

    def __init__(
        self,
        message: str,
        *,
        context: dict[str, Any] | None = None,
        suggestion: str | None = None,
    ) -> None:
        super().__init__(
            message,
            context=context,
            suggestion=suggestion or "This is an internal error. Please report this issue.",
        )


# =============================================================================
# Error Handler Decorator
# =============================================================================


def handle_errors(
    func: F | None = None,
    *,
    machine_mode: bool = False,
    show_traceback: bool = False,
) -> F | Callable[[F], F]:
    """Decorator for consistent CLI error handling.

    Catches exceptions and converts them to appropriate exit codes
    and error responses. In machine mode, outputs structured JSON.

    Args:
        func: Function to decorate
        machine_mode: If True, output JSON error responses
        show_traceback: If True, include traceback in error output

    Returns:
        Decorated function with error handling

    Usage:
        @handle_errors
        def my_command():
            ...

        @handle_errors(machine_mode=True)
        def agent_command():
            ...

    Example:
        @handle_errors
        def get_task(task_id: str):
            task = db.tasks.find(task_id)
            if not task:
                raise NotFoundError("Task", task_id)
            return task
    """

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return fn(*args, **kwargs)
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                if machine_mode:
                    _output_error_json(
                        code="INTERRUPTED",
                        message="Operation cancelled by user",
                        exit_code=ExitCode.INTERRUPTED,
                    )
                else:
                    print("\nOperation cancelled.", file=sys.stderr)
                sys.exit(ExitCode.INTERRUPTED)
            except CLIError as e:
                # Handle our custom CLI errors
                if machine_mode:
                    _output_error_json(
                        code=e.code,
                        message=e.message,
                        exit_code=e.exit_code,
                        field=e.field,
                        context=e.context,
                        suggestion=e.suggestion,
                    )
                else:
                    _output_error_text(e, show_traceback=show_traceback)
                sys.exit(e.exit_code)
            except Exception as e:
                # Handle unexpected exceptions
                exit_code = get_exit_code_for_exception(e)
                if machine_mode:
                    response = create_error_from_exception(
                        e,
                        exit_code=exit_code,
                        machine_mode=True,
                    )
                    print(response.model_dump_json())
                else:
                    _output_unexpected_error(e, show_traceback=show_traceback)
                sys.exit(exit_code)

        return wrapper  # type: ignore[return-value]

    if func is not None:
        return decorator(func)
    return decorator


def _output_error_json(
    code: str,
    message: str,
    exit_code: ExitCode,
    field: str | None = None,
    context: dict[str, Any] | None = None,
    suggestion: str | None = None,
) -> None:
    """Output error as JSON for machine consumption."""
    from cf_core.errors.response import create_error

    response = create_error(
        code=code,
        message=message,
        exit_code=exit_code,
        field=field,
        context=context,
        suggestion=suggestion,
        machine_mode=True,
    )
    print(response.model_dump_json())


def _output_error_text(error: CLIError, *, show_traceback: bool = False) -> None:
    """Output error as human-readable text."""
    print(f"Error [{error.code}]: {error.message}", file=sys.stderr)

    if error.suggestion:
        print(f"Suggestion: {error.suggestion}", file=sys.stderr)

    if error.context and show_traceback:
        print(f"Context: {error.context}", file=sys.stderr)

    if show_traceback:
        traceback.print_exc()


def _output_unexpected_error(
    error: Exception,
    *,
    show_traceback: bool = False,
) -> None:
    """Output unexpected error with optional traceback."""
    error_type = type(error).__name__
    print(f"Unexpected error [{error_type}]: {error}", file=sys.stderr)
    print(
        "This may be a bug. Please report this issue with the error details.",
        file=sys.stderr,
    )

    if show_traceback:
        traceback.print_exc()


__all__ = [
    "handle_errors",
    "CLIError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "ConfigurationError",
    "DatabaseError",
    "ConnectionError",
    "InternalError",
]
