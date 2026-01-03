"""Utility functions and classes for cf_core.

This module provides common utilities used throughout the cf_core package:

- **ensure_str**: Safe string conversion for mixed-type inputs
- **Stopwatch**: Simple performance timing class

Example Usage::

    from cf_core.utils import ensure_str, Stopwatch

    # Ensure string type
    value = ensure_str(123)  # "123"

    # Time an operation
    sw = Stopwatch()
    # ... do work ...
    print(f"Elapsed: {sw.elapsed():.3f}s")
"""


def ensure_str(value: object) -> str:
    """Ensure a value is converted to string.

    Args:
        value: Any value to convert. If already a string, returns as-is.
               Otherwise, converts using str().

    Returns:
        String representation of the input value.

    Example::

        >>> ensure_str("hello")
        'hello'
        >>> ensure_str(42)
        '42'
        >>> ensure_str(None)
        'None'
    """
    return value if isinstance(value, str) else str(value)


class Stopwatch:
    """Simple stopwatch for measuring elapsed time.

    Uses time.perf_counter() for high-precision timing. Starts automatically
    when instantiated.

    Example::

        sw = Stopwatch()
        # ... perform operation ...
        print(f"Operation took {sw.elapsed():.3f} seconds")

    Attributes:
        _start: The start timestamp from perf_counter().
    """

    def __init__(self) -> None:
        """Initialize and start the stopwatch."""
        import time
        self._start = time.perf_counter()

    def elapsed(self) -> float:
        """Get elapsed time since stopwatch creation.

        Returns:
            Elapsed time in seconds as a float.
        """
        import time
        return time.perf_counter() - self._start
