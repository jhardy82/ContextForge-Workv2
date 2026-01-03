"""Logging decorators for ContextForge.

Provides the @logged_action decorator for automatic function call logging
with correlation ID tracking and evidence bundle generation.

Key Features:
- Automatic entry/exit logging
- Exception handling and logging
- Correlation ID propagation
- Evidence bundle generation
- Configurable log levels per function

Authority: docs/prd/PRD-CFCORE-LOGGING.md (FR-007)
"""

import functools
import time
from collections.abc import Callable
from typing import Any, TypeVar

from .core import log_baseline_event, ulog

F = TypeVar('F', bound=Callable[..., Any])


def logged_action(
    func_or_action_name: Callable[[F], F] | str = None,
    *,
    action_name: str = "",
    log_entry: bool = True,
    log_exit: bool = True,
    log_errors: bool = True,
    level: str = "INFO",
    capture_args: bool = False,
    capture_result: bool = False
) -> Callable[[F], F] | F:
    """Decorator to automatically log function calls with correlation tracking.

    Provides comprehensive logging of function entry, exit, duration, and errors.
    Automatically generates baseline events and evidence bundles per QSE framework.

    Can be used with or without parentheses:
        @logged_action
        def my_func(): ...

        @logged_action("custom_name", capture_args=True)
        def my_func(): ...

    Args:
        func_or_action_name: Function (when used without parens) or action name
        action_name: Custom action name (defaults to function name)
        log_entry: Log function entry (default: True)
        log_exit: Log successful function exit (default: True)
        log_errors: Log exceptions (default: True)
        level: Log level for normal operations (default: "INFO")
        capture_args: Include function arguments in logs (default: False)
        capture_result: Include return value in logs (default: False)

    Returns:
        Decorated function with logging

    Example:
        @logged_action("process_task", capture_args=True)
        def process_task(task_id: str, priority: int = 1) -> dict:
            # Function implementation
            return {"status": "completed", "task_id": task_id}

        # Generates logs:
        # INFO: Action started: process_task (correlation_id: abc123, args: {...})
        # INFO: Action completed: process_task (duration_ms: 150, result: {...})
    """

    # Handle both @logged_action and @logged_action(...) usage
    if callable(func_or_action_name):
        # Used as @logged_action (without parentheses)
        func = func_or_action_name
        effective_action_name = action_name or f"{func.__module__}.{func.__qualname__}"
        return _create_logged_wrapper(
            func, effective_action_name, log_entry, log_exit, log_errors,
            level, capture_args, capture_result
        )
    else:
        # Used as @logged_action(...) (with parentheses)
        def decorator(func: F) -> F:
            effective_action_name = func_or_action_name or action_name or f"{func.__module__}.{func.__qualname__}"
            return _create_logged_wrapper(
                func, effective_action_name, log_entry, log_exit, log_errors,
                level, capture_args, capture_result
            )
        return decorator


def _create_logged_wrapper(
    func: F,
    action: str,
    log_entry: bool,
    log_exit: bool,
    log_errors: bool,
    level: str,
    capture_args: bool,
    capture_result: bool
) -> F:
    """Create the actual wrapper function with logging behavior."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Record start time
        start_time = time.time()

        # Prepare logging context
        log_context = {
            "function": func.__qualname__,
            "function_module": func.__module__,  # Changed from "module" to avoid conflict
        }

        # Add arguments if requested
        if capture_args:
            # Be careful not to log sensitive data
            log_context["function_args"] = _sanitize_args(args, kwargs)  # Changed from "args" to avoid conflict

        # Log function entry
        if log_entry:
            log_baseline_event("task_start",
                             task_id=action,
                             action_type="function_call",
                             **log_context)
            ulog("action_start", action, "started", level, **log_context)

        try:
            # Execute the function
            result = func(*args, **kwargs)

            # Calculate duration
            duration_ms = round((time.time() - start_time) * 1000, 2)

            # Prepare exit context
            exit_context = {
                **log_context,
                "duration_ms": duration_ms,
                "result_type": type(result).__name__ if result is not None else "None"
            }

            # Add result if requested
            if capture_result:
                exit_context["function_result"] = _sanitize_result(result)  # Changed from "result" to avoid conflicts

            # Log successful exit
            if log_exit:
                log_baseline_event("task_end",
                                 task_id=action,
                                 status="completed",
                                 **exit_context)
                ulog("action_complete", action, "success", level, **exit_context)

            return result

        except Exception as e:
            # Calculate duration for failed operation
            duration_ms = round((time.time() - start_time) * 1000, 2)

            # Prepare error context
            error_context = {
                **log_context,
                "duration_ms": duration_ms,
                "error_type": type(e).__name__,
                "error_message": str(e),
            }

            # Log error
            if log_errors:
                log_baseline_event("error",
                                 task_id=action,
                                 **error_context)
                ulog("action_error", action, "error", "ERROR", **error_context)

            # Re-raise the exception
            raise

    return wrapper


def _sanitize_args(args: tuple, kwargs: dict) -> dict:
    """Sanitize function arguments for logging.

    Removes or masks potentially sensitive data from function arguments
    before including in log entries.

    Args:
        args: Positional arguments tuple
        kwargs: Keyword arguments dict

    Returns:
        dict: Sanitized arguments safe for logging
    """
    # Sensitive parameter names to mask
    sensitive_params = {
        'password', 'passwd', 'secret', 'token', 'key', 'auth',
        'credential', 'private', 'confidential', 'api_key'
    }

    sanitized = {}

    # Handle positional args
    if args:
        sanitized['positional_count'] = len(args)
        # Don't log positional arg values to avoid accidental exposure

    # Handle keyword args
    if kwargs:
        sanitized['keyword_args'] = {}
        for key, value in kwargs.items():
            key_lower = key.lower()
            if any(sensitive_word in key_lower for sensitive_word in sensitive_params):
                sanitized['keyword_args'][key] = "***MASKED***"
            elif isinstance(value, str | int | float | bool | type(None)):
                # Only include simple types
                sanitized['keyword_args'][key] = value
            else:
                # For complex types, just log the type
                sanitized['keyword_args'][key] = f"<{type(value).__name__}>"

    return sanitized


def _sanitize_result(result: Any) -> Any:
    """Sanitize function result for logging.

    Args:
        result: Function return value

    Returns:
        Sanitized result safe for logging
    """
    # For simple types, return as-is
    if isinstance(result, str | int | float | bool | type(None)):
        return result
    elif isinstance(result, list | tuple):
        return f"<{type(result).__name__} len={len(result)}>"
    elif isinstance(result, dict):
        return f"<dict keys={list(result.keys())[:5]}{'...' if len(result) > 5 else ''}>"
    else:
        return f"<{type(result).__name__}>"


# Convenience decorators for common use cases

def logged_api_call(endpoint: str = "", **kwargs) -> Callable[[F], F]:
    """Decorator specifically for API endpoint functions.

    Args:
        endpoint: API endpoint name (defaults to function name)
        **kwargs: Additional arguments for logged_action
    """
    return logged_action(
        action_name=endpoint or "api_call",
        capture_args=True,
        level="INFO",
        **kwargs
    )


def logged_task(task_name: str = "", **kwargs) -> Callable[[F], F]:
    """Decorator specifically for task processing functions.

    Args:
        task_name: Task name (defaults to function name)
        **kwargs: Additional arguments for logged_action
    """
    return logged_action(
        action_name=task_name or "task",
        capture_args=True,
        capture_result=True,
        level="INFO",
        **kwargs
    )


def logged_operation(operation_name: str = "", **kwargs) -> Callable[[F], F]:
    """Decorator for general operations with minimal logging.

    Args:
        operation_name: Operation name (defaults to function name)
        **kwargs: Additional arguments for logged_action
    """
    return logged_action(
        action_name=operation_name or "operation",
        capture_args=False,
        capture_result=False,
        level="DEBUG",
        **kwargs
    )
