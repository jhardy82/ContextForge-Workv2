"""Result monad for functional error handling.

Simple Result type implementation for type-safe error handling without exceptions.

Example usage:
    from taskman_api.core import Result, Ok, Err, NotFoundError

    async def get_task(task_id: str) -> Result[Task, AppError]:
        task = await repository.find_by_id(task_id)
        if task is None:
            return Err(NotFoundError(f"Task {task_id} not found"))
        return Ok(task)

    # In route handler
    result = await get_task("task-123")
    if result.is_err():
        error = result.unwrap_err()
        raise HTTPException(status_code=error.status_code, detail=error.message)
    task = result.unwrap()
"""

from typing import Generic, TypeVar, Union

T = TypeVar("T")
E = TypeVar("E")


class Ok(Generic[T]):
    """Success result containing a value."""

    __match_args__ = ("value",)

    def __init__(self, value: T) -> None:
        self.value = value

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def unwrap(self) -> T:
        return self.value

    def ok(self) -> T:
        """Get the success value (alias for unwrap)."""
        return self.value

    def unwrap_err(self) -> None:
        raise ValueError("Called unwrap_err() on an Ok value")

    def err(self) -> None:
        """Raises error when called on Ok (alias for unwrap_err)."""
        raise ValueError("Called err() on an Ok value")


class Err(Generic[E]):
    """Error result containing an error."""

    __match_args__ = ("error",)

    def __init__(self, error: E) -> None:
        self.error = error

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def unwrap(self) -> None:
        raise ValueError(f"Called unwrap() on an Err value: {self.error}")

    def ok(self) -> None:
        """Raises error when called on Err."""
        raise ValueError(f"Called ok() on an Err value: {self.error}")

    def unwrap_err(self) -> E:
        return self.error

    def err(self) -> E:
        """Get the error value (alias for unwrap_err)."""
        return self.error


# Result type is a union of Ok and Err
Result = Union[Ok[T], Err[E]]


__all__ = ["Result", "Ok", "Err"]
