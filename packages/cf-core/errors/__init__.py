"""ContextForge Error Handling Module.

Provides unified error handling with:
- Semantic exit codes (BSD/POSIX conventions)
- Structured error/success response envelopes
- Error handling decorators for CLI commands

Usage:
    from cf_core.errors import ExitCode, ErrorResponse, handle_errors

    @handle_errors
    def my_command():
        ...
        raise NotFoundError("Task not found")  # Returns exit code 4
"""

from cf_core.errors.codes import ExitCode, exit_with_code
from cf_core.errors.handlers import (
    CLIError,
    ConfigurationError,
    ConflictError,
    ConnectionError,
    DatabaseError,
    InternalError,
    NotFoundError,
    ValidationError,
    handle_errors,
)
from cf_core.errors.response import (
    ErrorDetail,
    ErrorResponse,
    ResponseEnvelope,
    SuccessResponse,
    create_error,
    create_success,
)

__all__ = [
    # Exit codes
    "ExitCode",
    "exit_with_code",
    # Response types
    "ErrorDetail",
    "ErrorResponse",
    "SuccessResponse",
    "ResponseEnvelope",
    "create_success",
    "create_error",
    # Handlers and exceptions
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
