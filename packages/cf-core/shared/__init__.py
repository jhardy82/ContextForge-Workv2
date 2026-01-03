"""CF Core Shared Module.

Common utilities and patterns used across the cf_core package. This module
provides reusable components for error handling, result types, and utilities.

Exports:
    Result: Monadic result type for explicit error handling (Success/Failure)
    NotFoundException: Exception for resource not found errors
    ensure_str: Safe string conversion utility
    Stopwatch: Simple performance timing utility

Example Usage::

    from cf_core.shared import Result, NotFoundException

    def get_user(user_id: str) -> Result[User]:
        if not user_id:
            return Result.failure("User ID required")
        user = db.find(user_id)
        if not user:
            return Result.failure(f"User {user_id} not found")
        return Result.success(user)

    result = get_user("U-001")
    if result.is_success:
        print(f"Found: {result.value.name}")
    else:
        print(f"Error: {result.error}")
"""

from cf_core.shared.exceptions import NotFoundException
from cf_core.shared.result import Result
from cf_core.utils import Stopwatch, ensure_str

__all__ = ["Result", "NotFoundException", "ensure_str", "Stopwatch"]
