"""ContextForge Response Envelope Module.

Provides structured response schemas for consistent CLI output,
especially for agent/machine consumption.

Response Envelope Pattern:
    {
        "success": true/false,
        "data": {...} | null,
        "error": {...} | null,
        "meta": {...},
        "timestamp": "ISO8601"
    }

Usage:
    from cf_core.errors import create_success, create_error

    # Success response
    response = create_success({"task_id": "T-001", "title": "My Task"})

    # Error response
    response = create_error(
        code="NOT_FOUND",
        message="Task not found",
        exit_code=ExitCode.NOT_FOUND,
    )
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Generic, Literal, TypeVar
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from cf_core.errors.codes import ExitCode

T = TypeVar("T")


# =============================================================================
# Error Detail Schema
# =============================================================================

class ErrorDetail(BaseModel):
    """Detailed error information for structured error responses.

    Attributes:
        code: Machine-readable error code (e.g., "NOT_FOUND", "VALIDATION_ERROR")
        message: Human-readable error message
        field: Optional field name that caused the error (for validation errors)
        context: Additional context about the error
        suggestion: Optional suggestion for fixing the error
        documentation_url: Optional URL to relevant documentation
    """

    code: str = Field(
        description="Machine-readable error code",
    )
    message: str = Field(
        description="Human-readable error message",
    )
    field: str | None = Field(
        default=None,
        description="Field that caused the error (for validation errors)",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional error context",
    )
    suggestion: str | None = Field(
        default=None,
        description="Suggested action to fix the error",
    )
    documentation_url: str | None = Field(
        default=None,
        description="URL to relevant documentation",
    )


# =============================================================================
# Response Metadata
# =============================================================================

class ResponseMeta(BaseModel):
    """Metadata included with every response.

    Attributes:
        request_id: Unique identifier for this request/operation
        duration_ms: Operation duration in milliseconds
        version: API/CLI version
        machine_mode: Whether response is formatted for machine consumption
        pagination: Optional pagination information
    """

    request_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique request/operation identifier",
    )
    duration_ms: float | None = Field(
        default=None,
        description="Operation duration in milliseconds",
    )
    version: str = Field(
        default="0.1.0",
        description="API/CLI version",
    )
    machine_mode: bool = Field(
        default=False,
        description="Whether machine mode is active",
    )
    pagination: dict[str, Any] | None = Field(
        default=None,
        description="Pagination information (cursor, total, etc.)",
    )


# =============================================================================
# Response Envelopes
# =============================================================================

class SuccessResponse(BaseModel, Generic[T]):
    """Successful operation response envelope.

    Attributes:
        success: Always True for success responses
        data: The response payload
        meta: Response metadata
        timestamp: ISO8601 timestamp
    """

    model_config = ConfigDict(
        ser_json_timedelta="iso8601",
    )

    success: Literal[True] = Field(
        default=True,
        description="Always true for success responses",
    )
    data: T = Field(
        description="Response payload",
    )
    meta: ResponseMeta = Field(
        default_factory=ResponseMeta,
        description="Response metadata",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Response timestamp (ISO8601)",
    )


class ErrorResponse(BaseModel):
    """Error response envelope.

    Attributes:
        success: Always False for error responses
        error: Detailed error information
        exit_code: Numeric exit code for CLI
        meta: Response metadata
        timestamp: ISO8601 timestamp
    """

    model_config = ConfigDict(
        ser_json_timedelta="iso8601",
    )

    success: Literal[False] = Field(
        default=False,
        description="Always false for error responses",
    )
    error: ErrorDetail = Field(
        description="Detailed error information",
    )
    exit_code: int = Field(
        description="CLI exit code",
    )
    meta: ResponseMeta = Field(
        default_factory=ResponseMeta,
        description="Response metadata",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Response timestamp (ISO8601)",
    )


# Type alias for union of response types
ResponseEnvelope = SuccessResponse[T] | ErrorResponse


# =============================================================================
# Factory Functions
# =============================================================================

def create_success(
    data: T,
    request_id: str | None = None,
    duration_ms: float | None = None,
    machine_mode: bool = False,
    pagination: dict[str, Any] | None = None,
) -> SuccessResponse[T]:
    """Create a success response envelope.

    Args:
        data: Response payload
        request_id: Optional request identifier (generated if not provided)
        duration_ms: Optional operation duration
        machine_mode: Whether machine mode is active
        pagination: Optional pagination information

    Returns:
        SuccessResponse envelope containing the data
    """
    meta = ResponseMeta(
        request_id=request_id or str(uuid4()),
        duration_ms=duration_ms,
        machine_mode=machine_mode,
        pagination=pagination,
    )
    return SuccessResponse(data=data, meta=meta)


def create_error(
    code: str,
    message: str,
    exit_code: ExitCode = ExitCode.GENERAL_ERROR,
    field: str | None = None,
    context: dict[str, Any] | None = None,
    suggestion: str | None = None,
    documentation_url: str | None = None,
    request_id: str | None = None,
    duration_ms: float | None = None,
    machine_mode: bool = False,
) -> ErrorResponse:
    """Create an error response envelope.

    Args:
        code: Machine-readable error code
        message: Human-readable error message
        exit_code: CLI exit code
        field: Optional field that caused the error
        context: Optional additional context
        suggestion: Optional fix suggestion
        documentation_url: Optional documentation URL
        request_id: Optional request identifier
        duration_ms: Optional operation duration
        machine_mode: Whether machine mode is active

    Returns:
        ErrorResponse envelope containing the error details
    """
    error = ErrorDetail(
        code=code,
        message=message,
        field=field,
        context=context or {},
        suggestion=suggestion,
        documentation_url=documentation_url,
    )
    meta = ResponseMeta(
        request_id=request_id or str(uuid4()),
        duration_ms=duration_ms,
        machine_mode=machine_mode,
    )
    return ErrorResponse(error=error, exit_code=exit_code.value, meta=meta)


def create_error_from_exception(
    exc: Exception,
    exit_code: ExitCode | None = None,
    request_id: str | None = None,
    duration_ms: float | None = None,
    machine_mode: bool = False,
) -> ErrorResponse:
    """Create an error response from an exception.

    Args:
        exc: Exception to convert
        exit_code: Optional override for exit code (inferred from exception if not provided)
        request_id: Optional request identifier
        duration_ms: Optional operation duration
        machine_mode: Whether machine mode is active

    Returns:
        ErrorResponse envelope for the exception
    """
    from cf_core.errors.codes import get_exit_code_for_exception

    # Determine exit code
    if exit_code is None:
        if hasattr(exc, "exit_code"):
            exit_code = exc.exit_code
        else:
            exit_code = get_exit_code_for_exception(exc)

    # Extract error details
    code = type(exc).__name__
    message = str(exc)

    # Extract additional context if available
    context = {}
    if hasattr(exc, "context"):
        context = exc.context
    if hasattr(exc, "field"):
        field = exc.field
    else:
        field = None

    suggestion = getattr(exc, "suggestion", None)

    return create_error(
        code=code,
        message=message,
        exit_code=exit_code,
        field=field,
        context=context,
        suggestion=suggestion,
        request_id=request_id,
        duration_ms=duration_ms,
        machine_mode=machine_mode,
    )


__all__ = [
    "ErrorDetail",
    "ResponseMeta",
    "SuccessResponse",
    "ErrorResponse",
    "ResponseEnvelope",
    "create_success",
    "create_error",
    "create_error_from_exception",
]
