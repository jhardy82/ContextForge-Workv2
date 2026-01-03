"""OpenTelemetry Tracing Support for ContextForge CLI."""

from __future__ import annotations

import functools
import os
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any

try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor,
        ConsoleSpanExporter,
        SimpleSpanProcessor,
    )
except ImportError:
    # Graceful degradation if deps missing (shouldn't happen per pyproject.toml)
    trace = None # type: ignore

from cf_core.config.settings import get_settings

_TRACER_NAME = "contextforge.cli"

def init_tracing() -> None:
    """Initialize OpenTelemetry tracing if enabled."""
    if not trace:
        return

    settings = get_settings()
    # Check for trace enablement via env var or settings
    # For now, let's use a dedicated env var for explicit tracing
    enable_trace = os.environ.get("CONTEXTFORGE_TRACE_ENABLE", "").lower() == "true" or settings.output.verbose

    if not enable_trace:
        return

    resource = Resource.create({
        "service.name": "contextforge-cli",
        "service.version": settings.version,
    })

    provider = TracerProvider(resource=resource)

    # Check for OTLP endpoint, default to Console if not set but tracing enabled
    otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")

    if otlp_endpoint:
        exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
        processor = BatchSpanProcessor(exporter)
    else:
        # Default to Console for local debugging/modern feel
        exporter = ConsoleSpanExporter()
        processor = SimpleSpanProcessor(exporter)

    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)


def get_tracer() -> Any:
    """Get the global tracer."""
    if trace:
        return trace.get_tracer(_TRACER_NAME)
    return None

def instrument(name: str | None = None) -> Callable:
    """Decorator to instrument functions with OTel spans."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            tracer = get_tracer()
            if not tracer:
                return func(*args, **kwargs)

            span_name = name or func.__name__
            with tracer.start_as_current_span(span_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


@contextmanager
def span(name: str) -> Generator[None, None, None]:
    """Context manager for manual spans."""
    tracer = get_tracer()
    if tracer:
        with tracer.start_as_current_span(name):
            yield
    else:
        yield
