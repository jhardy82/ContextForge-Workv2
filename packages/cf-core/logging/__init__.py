"""cf_core.logging - Unified logging infrastructure for ContextForge.

This package provides a centralized logging solution that consolidates 5+
fragmented implementations across the codebase. Key features:

- RFC 8785 canonical JSON serialization for evidence bundles
- SHA-256 cryptographic hashing for integrity verification
- ContextVar-based correlation ID propagation (thread/async safe)
- ThreadPoolExecutor and subprocess context propagation
- Backward compatibility with existing ulog() API
- Feature flag support for gradual migration

Example:
    Basic usage:
        from cf_core.logging import get_logger, ulog, configure_logging

        # Configure logging
        configure_logging(level="INFO", format="json")

        # Get logger
        logger = get_logger("my_app")
        logger.info("Application started")

        # Legacy ulog API
        ulog("task_start", "TASK-001", "success", task_id="TASK-001")

Feature Flag:
    Set CFCORE_LOGGING_V3=1 to enable this logging package.
    Without the flag, falls back to existing implementations.

Requirements:
    - Python 3.11+ (for asyncio context inheritance)
    - structlog (for structured logging)
    - contextvars (for thread/async-safe correlation)

Authority:
    - PRD: docs/prd/PRD-CFCORE-LOGGING.md
    - ADR-002: docs/adr/ADR-002-correlation-id-strategy.md
    - ADR-003: docs/adr/ADR-003-evidence-bundle-compliance.md
    - Migration: docs/plans/MIGRATION-CFCORE-LOGGING.md
"""

import os

# Feature flag check
# Feature flag check - Default to True for cf_core standalone
_CFCORE_LOGGING_ENABLED = os.getenv("CFCORE_LOGGING_V3", "1").lower() in ("1", "true", "yes")

if _CFCORE_LOGGING_ENABLED:
    # New cf_core.logging implementation
    from .core import configure_logging, get_logger, ulog
    from .correlation import (
        correlation_context,
        get_correlation_id,
        set_correlation_id,
        spawn_correlated_subprocess,
        submit_with_context,
    )
    from .decorators import logged_action
    from .evidence import canonicalize, capture_evidence, hash_evidence
    from .runtime import Runtime, RuntimeBuilder

    __all__ = [
        # Core logging API
        "configure_logging",
        "get_logger",
        "ulog",
        # Correlation management
        "correlation_context",
        "get_correlation_id",
        "set_correlation_id",
        "spawn_correlated_subprocess",
        "submit_with_context",
        # Decorators
        "logged_action",
        # Evidence bundles
        "canonicalize",
        "capture_evidence",
        "hash_evidence",
        # Runtime configuration
        "Runtime",
        "RuntimeBuilder",
    ]

else:
    # Fallback to existing implementations
    import warnings
    warnings.warn(
        "cf_core.logging not enabled. Set CFCORE_LOGGING_V3=1 to use new implementation. "
        "Falling back to python.services.unified_logger",
        DeprecationWarning,
        stacklevel=2
    )

    # Import from existing locations for backward compatibility
    try:
        from cf_core.logger_provider import RuntimeBuilder
        from python.services.unified_logger import get_logger, ulog
        # Stub implementations for new APIs
        def configure_logging(**kwargs):
            """Stub - configure_logging not available in legacy mode."""
            pass
        def get_correlation_id() -> str:
            """Stub - returns empty string in legacy mode."""
            return ""

        __all__ = [
            "get_logger",
            "ulog",
            "RuntimeBuilder",
            "configure_logging",
            "get_correlation_id"
        ]

    except ImportError:
        # If legacy imports fail, provide minimal stubs
        import logging
        def get_logger(name: str = "cf_core"):
            return logging.getLogger(name)
        def ulog(*args, **kwargs):
            """Stub ulog implementation."""
            pass
        def configure_logging(**kwargs):
            """Stub configure_logging implementation."""
            pass
        def get_correlation_id() -> str:
            """Stub get_correlation_id implementation."""
            return ""

        __all__ = ["get_logger", "ulog", "configure_logging", "get_correlation_id"]
