"""Application error types and exception hierarchy.

Implements RFC 9457 Problem Details for HTTP APIs with structured error information.
All errors include problem_type for RFC 9457 compliance.
"""

from typing import Any


class AppError(Exception):
    """Base class for all application errors.

    Attributes:
        message: Human-readable error message
        status_code: HTTP status code
        problem_type: RFC 9457 problem type identifier
        title: Short, human-readable summary
        detail: Human-readable explanation
        extra: Additional error-specific information
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        problem_type: str = "internal-error",
        title: str | None = None,
        detail: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.problem_type = problem_type
        self.title = title or self.__class__.__name__
        self.detail = detail or message
        self.extra = extra or {}

    def to_problem_details(self, instance: str) -> dict[str, Any]:
        """Convert to RFC 9457 Problem Details format.

        Args:
            instance: URI reference to specific occurrence (request URL)

        Returns:
            RFC 9457 compliant problem details dictionary
        """
        problem = {
            "type": f"https://api.taskman-v2.local/problems/{self.problem_type}",
            "title": self.title,
            "status": self.status_code,
            "detail": self.detail,
            "instance": instance,
        }
        # Add any extra fields from subclasses
        problem.update(self.extra)
        return problem


class NotFoundError(AppError):
    """Entity not found in database.

    HTTP 404 - The requested resource does not exist.
    """

    def __init__(
        self,
        message: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
    ) -> None:
        extra = {}
        if entity_type:
            extra["entity_type"] = entity_type
        if entity_id:
            extra["entity_id"] = entity_id

        super().__init__(
            message=message,
            status_code=404,
            problem_type="not-found",
            title="Resource Not Found",
            detail=message,
            extra=extra,
        )


class ValidationError(AppError):
    """Input validation failure.

    HTTP 422 - The request was well-formed but contains invalid data.
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any | None = None,
        validation_errors: list[dict[str, Any]] | None = None,
    ) -> None:
        extra: dict[str, Any] = {}
        if field:
            extra["field"] = field
        if value is not None:
            extra["value"] = value
        if validation_errors:
            extra["validation_errors"] = validation_errors

        super().__init__(
            message=message,
            status_code=422,
            problem_type="validation-error",
            title="Validation Error",
            detail=message,
            extra=extra,
        )


class ConflictError(AppError):
    """Resource conflict (e.g., duplicate ID, concurrent modification).

    HTTP 409 - The request conflicts with the current state of the resource.
    """

    def __init__(
        self,
        message: str,
        conflict_type: str | None = None,
        existing_id: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        constraint: str | None = None,
        original_error: str | None = None,
    ) -> None:
        extra: dict[str, Any] = {}
        if conflict_type:
            extra["conflict_type"] = conflict_type
        if existing_id:
            extra["existing_id"] = existing_id
        if entity_type:
            extra["entity_type"] = entity_type
        if entity_id:
            extra["entity_id"] = entity_id
        if constraint:
            extra["constraint"] = constraint
        if original_error:
            extra["original_error"] = original_error

        super().__init__(
            message=message,
            status_code=409,
            problem_type="conflict",
            title="Resource Conflict",
            detail=message,
            extra=extra,
        )


class DatabaseError(AppError):
    """Database operation failure.

    HTTP 500 - An error occurred while accessing the database.
    """

    def __init__(
        self,
        message: str,
        operation: str | None = None,
        original_error: str | None = None,
        details: str | None = None,
    ) -> None:
        extra: dict[str, Any] = {}
        if operation:
            extra["operation"] = operation
        if original_error:
            extra["original_error"] = original_error
        if details:
            extra["details"] = details

        super().__init__(
            message=message,
            status_code=500,
            problem_type="database-error",
            title="Database Error",
            detail=message,
            extra=extra,
        )


class AuthorizationError(AppError):
    """User lacks permission to perform operation.

    HTTP 403 - The user is authenticated but lacks permission.
    """

    def __init__(
        self,
        message: str,
        required_permission: str | None = None,
        resource: str | None = None,
    ) -> None:
        extra = {}
        if required_permission:
            extra["required_permission"] = required_permission
        if resource:
            extra["resource"] = resource

        super().__init__(
            message=message,
            status_code=403,
            problem_type="forbidden",
            title="Forbidden",
            detail=message,
            extra=extra,
        )


class AuthenticationError(AppError):
    """User authentication failure.

    HTTP 401 - The request requires authentication or credentials are invalid.
    """

    def __init__(
        self,
        message: str,
        auth_scheme: str | None = None,
    ) -> None:
        extra = {}
        if auth_scheme:
            extra["auth_scheme"] = auth_scheme

        super().__init__(
            message=message,
            status_code=401,
            problem_type="unauthorized",
            title="Unauthorized",
            detail=message,
            extra=extra,
        )


class ConcurrencyError(AppError):
    """Optimistic locking failure (concurrent modification detected).

    HTTP 409 - The resource was modified by another request.
    Use x-concurrency-token header for optimistic locking.
    """

    def __init__(
        self,
        message: str,
        expected_version: str | None = None,
        actual_version: str | None = None,
    ) -> None:
        extra = {}
        if expected_version:
            extra["expected_version"] = expected_version
        if actual_version:
            extra["actual_version"] = actual_version

        super().__init__(
            message=message,
            status_code=409,
            problem_type="concurrency-conflict",
            title="Concurrent Modification Detected",
            detail=message,
            extra=extra,
        )
