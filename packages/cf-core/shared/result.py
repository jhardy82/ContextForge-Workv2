"""
Result Monad Pattern

Functional error handling using Result type to encapsulate success/failure.
Eliminates exceptions for expected errors, making error handling explicit.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")

# Sentinel for distinguishing None value from no value
_UNSET = object()


class Result(Generic[T]):
    """
    Result monad for functional error handling.

    Either contains a success value or an error message, never both.
    Inspired by Rust's Result<T, E> and Haskell's Either.

    Usage:
        # Success case
        result = Result.success(value)
        if result.is_success:
            print(result.value)

        # Failure case
        result = Result.failure("Something went wrong")
        if result.is_failure:
            print(result.error)

        # Chaining with map
        result = Result.success(10).map(lambda x: x * 2)  # Result.success(20)
    """

    __slots__ = ("_value", "_error", "_is_success")

    def __init__(
        self,
        value: T | None = None,
        error: str | None = None,
        *,
        _sentinel: object = _UNSET,
    ):
        """
        Private constructor. Use Result.success() or Result.failure() instead.

        Args:
            value: Success value (mutually exclusive with error)
            error: Error message (mutually exclusive with value)
            _sentinel: Internal flag to allow None as valid success value
        """
        # Support None as a valid success value using sentinel pattern
        has_value = _sentinel is not _UNSET or value is not None
        has_error = error is not None

        if has_value and has_error:
            raise ValueError("Result cannot have both value and error")
        if not has_value and not has_error:
            raise ValueError("Result must have either value or error")

        self._value = value
        self._error = error
        self._is_success = has_value

    @classmethod
    def success(cls, value: T) -> Result[T]:
        """
        Create a successful Result containing a value.

        Args:
            value: The success value to wrap (can be None)

        Returns:
            Result[T]: Success result containing the value
        """
        # Use sentinel to allow None as valid value
        return cls(value=value, _sentinel=value)

    @classmethod
    def failure(cls, error: str) -> Result[T]:
        """
        Create a failed Result containing an error message.

        Args:
            error: Error message describing what went wrong

        Returns:
            Result[T]: Failure result containing the error
        """
        return cls(error=error)

    @property
    def is_success(self) -> bool:
        """Check if this Result represents success."""
        return self._is_success

    @property
    def is_failure(self) -> bool:
        """Check if this Result represents failure."""
        return not self._is_success

    @property
    def value(self) -> T:
        """
        Get the success value.

        Returns:
            T: The wrapped success value

        Raises:
            ValueError: If this Result is a failure
        """
        if self.is_failure:
            raise ValueError(f"Cannot get value from failed Result: {self._error}")
        return self._value  # type: ignore[return-value]

    @property
    def error(self) -> str:
        """
        Get the error message.

        Returns:
            str: The error message

        Raises:
            ValueError: If this Result is a success
        """
        if self.is_success:
            raise ValueError("Cannot get error from successful Result")
        return self._error  # type: ignore[return-value]

    def map(self, fn: Callable[[T], U]) -> Result[U]:
        """
        Transform the success value using the given function.

        If this Result is a success, applies fn to the value and wraps the result.
        If this Result is a failure, returns the failure unchanged.

        Args:
            fn: Function to apply to the success value

        Returns:
            Result[U]: New Result with transformed value, or original failure

        Example:
            Result.success(10).map(lambda x: x * 2)  # Result.success(20)
            Result.failure("error").map(lambda x: x * 2)  # Result.failure("error")
        """
        if self.is_failure:
            return Result.failure(self._error)  # type: ignore[arg-type]
        try:
            return Result.success(fn(self._value))  # type: ignore[arg-type]
        except Exception as e:
            return Result.failure(f"Map function raised exception: {e}")

    def flat_map(self, fn: Callable[[T], Result[U]]) -> Result[U]:
        """
        Chain Result-returning operations (monadic bind).

        If this Result is a success, applies fn to the value (fn returns Result).
        If this Result is a failure, returns the failure unchanged.

        Args:
            fn: Function that takes T and returns Result[U]

        Returns:
            Result[U]: Result from fn, or original failure

        Example:
            def divide(x: int) -> Result[float]:
                if x == 0:
                    return Result.failure("Division by zero")
                return Result.success(10 / x)

            Result.success(5).flat_map(divide)  # Result.success(2.0)
            Result.success(0).flat_map(divide)  # Result.failure("Division by zero")
        """
        if self.is_failure:
            return Result.failure(self._error)  # type: ignore[arg-type]
        try:
            return fn(self._value)  # type: ignore[arg-type]
        except Exception as e:
            return Result.failure(f"FlatMap function raised exception: {e}")

    def unwrap_or(self, default: T) -> T:
        """
        Get the success value or return a default if failure.

        Args:
            default: Value to return if this is a failure

        Returns:
            T: The success value or the default
        """
        if self.is_success:
            return self._value  # type: ignore[return-value]
        return default

    def unwrap_or_else(self, fn: Callable[[str], T]) -> T:
        """
        Get the success value or compute a default from the error.

        Args:
            fn: Function that takes the error message and returns a default value

        Returns:
            T: The success value or the computed default
        """
        if self.is_success:
            return self._value  # type: ignore[return-value]
        return fn(self._error)  # type: ignore[arg-type]

    def __repr__(self) -> str:
        """String representation for debugging."""
        if self.is_success:
            return f"Result.success({self._value!r})"
        else:
            return f"Result.failure({self._error!r})"

    def __bool__(self) -> bool:
        """Boolean conversion: True for success, False for failure."""
        return self._is_success

    def __eq__(self, other: object) -> bool:
        """Check equality with another Result."""
        if not isinstance(other, Result):
            return NotImplemented
        if self.is_success != other.is_success:
            return False
        if self.is_success:
            return self._value == other._value
        return self._error == other._error

    def __hash__(self) -> int:
        """Make Result hashable."""
        if self.is_success:
            return hash(("success", self._value))
        return hash(("failure", self._error))
