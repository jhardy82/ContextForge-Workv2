"""ContextForge Exit Codes Module.

Semantic exit codes following BSD/POSIX conventions with extensions
for ContextForge-specific error categories.

Code Ranges:
- 0:      Success
- 1-9:    User/input errors
- 10-19:  Authentication/authorization errors
- 20-29:  Resource errors (not found, already exists)
- 30-39:  Validation errors
- 40-49:  Reserved for future use
- 50-59:  Configuration errors
- 60-69:  Connection/network errors
- 70-79:  Internal/system errors
- 80-89:  Special status codes (partial success, interrupted)
- 90-99:  Reserved for plugins/extensions

Usage:
    from cf_core.errors import ExitCode, exit_with_code

    if not task:
        exit_with_code(ExitCode.NOT_FOUND, "Task not found")

    # Or use with sys.exit directly
    sys.exit(ExitCode.SUCCESS)
"""

from __future__ import annotations

import sys
from enum import IntEnum
from typing import NoReturn


class ExitCode(IntEnum):
    """Semantic exit codes for ContextForge CLI.

    Following BSD sysexits.h conventions with extensions for
    task management and agent-specific error categories.
    """

    # ==========================================================================
    # Success (0)
    # ==========================================================================
    SUCCESS = 0

    # ==========================================================================
    # User/Input Errors (1-9)
    # ==========================================================================
    GENERAL_ERROR = 1          # Catchall for general errors
    USAGE_ERROR = 2            # Command line usage error (wrong args)
    INVALID_ARGUMENT = 3       # Invalid argument value
    MISSING_ARGUMENT = 4       # Required argument not provided
    INVALID_INPUT = 5          # Invalid input data format
    OPERATION_CANCELLED = 6    # User cancelled operation
    PERMISSION_DENIED = 7      # User lacks permission for operation
    RATE_LIMITED = 8           # Too many requests
    TIMEOUT_USER = 9           # User-initiated timeout

    # ==========================================================================
    # Authentication/Authorization Errors (10-19)
    # ==========================================================================
    AUTH_REQUIRED = 10         # Authentication required
    AUTH_FAILED = 11           # Authentication failed
    AUTH_EXPIRED = 12          # Authentication token expired
    INSUFFICIENT_PRIVILEGES = 13  # Insufficient privileges for operation
    AUTH_REVOKED = 14          # Authentication revoked

    # ==========================================================================
    # Resource Errors (20-29)
    # ==========================================================================
    NOT_FOUND = 20             # Resource not found
    ALREADY_EXISTS = 21        # Resource already exists
    CONFLICT = 22              # Resource conflict (concurrent modification)
    GONE = 23                  # Resource permanently deleted
    LOCKED = 24                # Resource is locked
    DEPENDENCY_MISSING = 25    # Required dependency not found
    QUOTA_EXCEEDED = 26        # Resource quota exceeded
    RESOURCE_BUSY = 27         # Resource is busy/in use

    # ==========================================================================
    # Validation Errors (30-39)
    # ==========================================================================
    VALIDATION_ERROR = 30      # General validation failure
    SCHEMA_ERROR = 31          # Schema validation error
    CONSTRAINT_VIOLATION = 32  # Constraint violation (business rule)
    STATE_INVALID = 33         # Invalid state transition
    DATA_INTEGRITY = 34        # Data integrity violation
    FORMAT_ERROR = 35          # Data format error

    # ==========================================================================
    # Configuration Errors (50-59)
    # ==========================================================================
    CONFIG_ERROR = 50          # General configuration error
    CONFIG_NOT_FOUND = 51      # Configuration file not found
    CONFIG_INVALID = 52        # Invalid configuration format
    CONFIG_MISSING_KEY = 53    # Required configuration key missing
    ENV_VAR_MISSING = 54       # Required environment variable missing
    ENV_VAR_INVALID = 55       # Invalid environment variable value

    # ==========================================================================
    # Connection/Network Errors (60-69)
    # ==========================================================================
    CONNECTION_ERROR = 60      # General connection error
    DATABASE_ERROR = 61        # Database connection/operation error
    API_ERROR = 62             # External API error
    NETWORK_ERROR = 63         # Network communication error
    TIMEOUT = 64               # Operation timeout
    DNS_ERROR = 65             # DNS resolution failure
    SSL_ERROR = 66             # SSL/TLS error
    PROTOCOL_ERROR = 67        # Protocol error

    # ==========================================================================
    # Internal/System Errors (70-79)
    # ==========================================================================
    INTERNAL_ERROR = 70        # Internal error (bug)
    NOT_IMPLEMENTED = 71       # Feature not implemented
    SYSTEM_ERROR = 72          # OS/system error
    IO_ERROR = 73              # File I/O error
    MEMORY_ERROR = 74          # Out of memory
    DEPENDENCY_ERROR = 75      # Third-party dependency error
    SERIALIZATION_ERROR = 76   # Serialization/deserialization error

    # ==========================================================================
    # Special Status Codes (80-89)
    # ==========================================================================
    INTERRUPTED = 80           # Operation interrupted (Ctrl+C)
    PARTIAL_SUCCESS = 81       # Some operations succeeded, some failed
    DRY_RUN = 82               # Dry run completed (no changes made)
    SKIPPED = 83               # Operation skipped (already complete)
    DEPRECATED = 84            # Deprecated feature used
    NEEDS_UPDATE = 85          # CLI/component needs update

    # ==========================================================================
    # Plugin/Extension Reserved (90-99)
    # ==========================================================================
    PLUGIN_ERROR = 90          # Plugin error
    EXTENSION_ERROR = 91       # Extension error

    @property
    def category(self) -> str:
        """Get the error category for this exit code."""
        if self.value == 0:
            return "success"
        elif 1 <= self.value <= 9:
            return "user_error"
        elif 10 <= self.value <= 19:
            return "auth_error"
        elif 20 <= self.value <= 29:
            return "resource_error"
        elif 30 <= self.value <= 39:
            return "validation_error"
        elif 50 <= self.value <= 59:
            return "config_error"
        elif 60 <= self.value <= 69:
            return "connection_error"
        elif 70 <= self.value <= 79:
            return "internal_error"
        elif 80 <= self.value <= 89:
            return "special"
        elif 90 <= self.value <= 99:
            return "plugin_error"
        else:
            return "unknown"

    @property
    def is_success(self) -> bool:
        """Check if this exit code indicates success."""
        return self.value == 0

    @property
    def is_error(self) -> bool:
        """Check if this exit code indicates an error."""
        return self.value != 0

    @property
    def is_recoverable(self) -> bool:
        """Check if this error type is potentially recoverable.

        User errors, auth errors, and some resource errors may be
        recoverable with user intervention. Internal errors are not.
        """
        return self.category in ("user_error", "auth_error", "config_error")

    def __str__(self) -> str:
        """Return human-readable representation."""
        return f"{self.name} ({self.value})"


# =============================================================================
# Exit Helpers
# =============================================================================

def exit_with_code(code: ExitCode, message: str | None = None) -> NoReturn:
    """Exit with the specified exit code and optional message.

    Args:
        code: Exit code to use
        message: Optional error message to print to stderr

    Raises:
        SystemExit: Always raises with the specified exit code
    """
    if message:
        print(f"Error [{code.name}]: {message}", file=sys.stderr)
    sys.exit(code.value)


def get_exit_code_for_exception(exc: Exception) -> ExitCode:
    """Map an exception to an appropriate exit code.

    Args:
        exc: Exception to map

    Returns:
        Appropriate ExitCode for the exception type
    """
    # Map common exception types to exit codes
    exception_map = {
        KeyboardInterrupt: ExitCode.INTERRUPTED,
        FileNotFoundError: ExitCode.NOT_FOUND,
        PermissionError: ExitCode.PERMISSION_DENIED,
        TimeoutError: ExitCode.TIMEOUT,
        ConnectionError: ExitCode.CONNECTION_ERROR,
        ValueError: ExitCode.VALIDATION_ERROR,
        TypeError: ExitCode.INVALID_ARGUMENT,
        NotImplementedError: ExitCode.NOT_IMPLEMENTED,
        MemoryError: ExitCode.MEMORY_ERROR,
        OSError: ExitCode.SYSTEM_ERROR,
        IOError: ExitCode.IO_ERROR,
    }

    for exc_type, exit_code in exception_map.items():
        if isinstance(exc, exc_type):
            return exit_code

    # Check for custom exception attributes
    if hasattr(exc, "exit_code"):
        return exc.exit_code

    # Default to general error
    return ExitCode.GENERAL_ERROR


__all__ = [
    "ExitCode",
    "exit_with_code",
    "get_exit_code_for_exception",
]
