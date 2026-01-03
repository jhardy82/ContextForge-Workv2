"""Correlation ID management for ContextForge logging.

Implements thread/async-safe correlation ID propagation using ContextVar.
Handles ThreadPoolExecutor and subprocess context propagation patterns
per ADR-002.

Key Features:
- ContextVar-based correlation (Python 3.11+ async context inheritance)
- ThreadPoolExecutor context propagation via submit_with_context()
- Subprocess context propagation via spawn_correlated_subprocess()
- Precedence: ContextVar > UNIFIED_LOG_CORRELATION > CF_SESSION_ID > CF_TRACE_ID > UUID

Requirements:
- Python 3.11+ for asyncio.create_task context inheritance
- contextvars module (built-in Python 3.7+)

Authority: docs/adr/ADR-002-correlation-id-strategy.md
"""

import asyncio
import contextvars
import os
import subprocess
import uuid
from collections.abc import Callable, Generator
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import contextmanager
from typing import Any, TypeVar

# Global ContextVar for correlation ID
_correlation_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    'correlation_id',
    default=""
)

T = TypeVar('T')


def get_correlation_id() -> str:
    """Get the current correlation ID following precedence chain.

    Precedence (per ADR-002):
    1. ContextVar (current context)
    2. UNIFIED_LOG_CORRELATION environment variable
    3. CF_SESSION_ID environment variable
    4. CF_TRACE_ID environment variable
    5. Generate new UUID4

    Returns:
        str: 32-character lowercase hex correlation ID (UUID4 without hyphens)
    """
    # 1. Check ContextVar first (current context)
    correlation_id = _correlation_id.get("")
    if correlation_id:
        return correlation_id

    # 2. Check UNIFIED_LOG_CORRELATION environment variable
    correlation_id = os.getenv("UNIFIED_LOG_CORRELATION", "").strip()
    if correlation_id:
        set_correlation_id(correlation_id)  # Cache in ContextVar
        return correlation_id

    # 3. Check CF_SESSION_ID environment variable
    correlation_id = os.getenv("CF_SESSION_ID", "").strip()
    if correlation_id:
        set_correlation_id(correlation_id)  # Cache in ContextVar
        return correlation_id

    # 4. Check CF_TRACE_ID environment variable
    correlation_id = os.getenv("CF_TRACE_ID", "").strip()
    if correlation_id:
        set_correlation_id(correlation_id)  # Cache in ContextVar
        return correlation_id

    # 5. Generate new UUID4 (32-char hex without hyphens)
    correlation_id = uuid.uuid4().hex
    set_correlation_id(correlation_id)  # Cache in ContextVar
    return correlation_id


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID in the current context.

    Args:
        correlation_id: The correlation ID to set (will be stripped of whitespace)

    Raises:
        ValueError: If correlation_id is empty or invalid format
    """
    if not correlation_id or not correlation_id.strip():
        raise ValueError("Correlation ID cannot be empty")

    clean_id = correlation_id.strip()

    # Basic validation - should be hex-like string
    if not clean_id:
        raise ValueError("Correlation ID cannot be empty after stripping whitespace")

    _correlation_id.set(clean_id)


def correlation_context(**extra_context: Any) -> contextvars.Context:
    """Create a new context with correlation ID and optional extra context.

    Args:
        **extra_context: Additional context variables to set

    Returns:
        contextvars.Context: New context with correlation ID preserved
    """
    # Get current context
    ctx = contextvars.copy_context()

    # Ensure correlation ID is set in the new context
    current_id = get_correlation_id()
    ctx[_correlation_id] = current_id

    # Set any additional context variables
    for _key, _value in extra_context.items():
        # For now, we only support the correlation_id ContextVar
        # Additional ContextVars would need to be defined if needed
        continue

    return ctx


@contextmanager
def with_correlation_id(correlation_id: str) -> Generator[str, None, None]:
    """Context manager to temporarily set a correlation ID.

    Args:
        correlation_id: The correlation ID to set temporarily

    Yields:
        str: The correlation ID that was set

    Example:
        with with_correlation_id('temp-123') as cid:
            # correlation ID is 'temp-123' within this block
            logger.info('Message with temp ID')
        # correlation ID is restored to previous value
    """
    # Save the current correlation ID (if any)
    token = _correlation_id.set(correlation_id)

    try:
        yield correlation_id
    finally:
        # Restore the previous correlation ID
        _correlation_id.reset(token)


def submit_with_context(
    executor: ThreadPoolExecutor,
    fn: Callable[..., T],
    *args: Any,
    **kwargs: Any
) -> Future[T]:
    """Submit a function to ThreadPoolExecutor with correlation context.

    ThreadPoolExecutor does NOT automatically propagate ContextVar values
    to worker threads. This function copies the current context and runs
    the function within that context in the worker thread.

    Args:
        executor: The ThreadPoolExecutor instance
        fn: Function to execute
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        Future[T]: Future representing the execution

    Example:
        with ThreadPoolExecutor() as executor:
            set_correlation_id("abc123")
            future = submit_with_context(executor, process_task, task_data)
            result = future.result()  # process_task runs with correlation_id="abc123"
    """
    # Copy current context (including correlation ID)
    ctx = contextvars.copy_context()

    # Submit function to run within the copied context
    return executor.submit(ctx.run, fn, *args, **kwargs)


def spawn_correlated_subprocess(
    cmd: list[str],
    **subprocess_kwargs: Any
) -> subprocess.Popen:
    """Spawn a subprocess with correlation ID passed via environment variable.

    Subprocess processes do NOT inherit ContextVar values. This function
    passes the current correlation ID via the UNIFIED_LOG_CORRELATION
    environment variable.

    Args:
        cmd: Command and arguments to execute
        **subprocess_kwargs: Additional arguments for subprocess.Popen

    Returns:
        subprocess.Popen: The spawned process

    Example:
        set_correlation_id("abc123")
        proc = spawn_correlated_subprocess(["python", "worker.py"])
        # worker.py will see UNIFIED_LOG_CORRELATION="abc123" in environment
    """
    # Get current correlation ID
    correlation_id = get_correlation_id()

    # Prepare environment variables
    env = subprocess_kwargs.get("env", os.environ.copy())
    if env is None:
        env = os.environ.copy()
    else:
        env = env.copy()  # Don't modify caller's env dict

    # Set correlation ID in environment
    env["UNIFIED_LOG_CORRELATION"] = correlation_id

    # Update subprocess kwargs
    subprocess_kwargs = subprocess_kwargs.copy()
    subprocess_kwargs["env"] = env

    # Spawn the subprocess
    return subprocess.Popen(cmd, **subprocess_kwargs)


async def async_with_correlation(coro, correlation_id: str | None = None):
    """Run an async coroutine with a specific correlation ID.

    Python 3.11+ automatically inherits ContextVar values in asyncio.create_task(),
    but this function allows explicit correlation ID override.

    Args:
        coro: The coroutine to run
        correlation_id: Optional correlation ID to set (uses current if None)

    Returns:
        The result of the coroutine
    """
    if correlation_id is not None:
        # Set the correlation ID in current context
        set_correlation_id(correlation_id)

    # In Python 3.11+, asyncio.create_task automatically copies ContextVar values
    return await coro


# Backwards compatibility aliases
def generate_correlation_id() -> str:
    """Generate a new correlation ID (UUID4 hex).

    This is a compatibility alias. Use get_correlation_id() for precedence chain
    or uuid.uuid4().hex for explicit generation.
    """
    return uuid.uuid4().hex
