"""TaskMan API - FastAPI application entry point.

Production-ready REST API for task management system with:
- Structured JSON logging
- Health check endpoints (liveness, readiness, startup)
- Request logging middleware
- OpenTelemetry metrics
- CORS configuration
- Error handling middleware
"""

from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from taskman_api.api.middleware.error_handler import error_handler_middleware
from taskman_api.api.middleware.request_logger import RequestLoggingMiddleware
from taskman_api.api.v1 import action_lists, health, projects, sprints, tasks
from taskman_api.config import get_settings
from taskman_api.db.session import close_db, init_db
from taskman_api.infrastructure.logging import configure_logging, get_logger
from taskman_api.infrastructure.metrics import configure_metrics

# Configure structured logging before creating app
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Handles startup and shutdown events:
    - Startup: Initialize database connection, configure metrics
    - Shutdown: Close database connections

    Args:
        app: FastAPI application instance

    Yields:
        Control to application during its lifetime
    """
    # Startup
    startup_time = datetime.now(UTC)
    logger.info("application_startup", timestamp=startup_time.isoformat())

    try:
        # Initialize database
        await init_db()
        logger.info("database_initialized")

        # Configure metrics
        settings = get_settings()
        configure_metrics(app, settings)

    except Exception as exc:
        logger.error(
            "startup_failed",
            error_type=type(exc).__name__,
            error_message=str(exc),
            exc_info=True,
        )
        raise

    yield

    # Shutdown
    logger.info("application_shutdown")
    await close_db()
    logger.info("database_closed")


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        Configured FastAPI application instance with:
        - Structured logging
        - Health check endpoints
        - Request logging
        - Metrics collection
        - Error handling
        - CORS support
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="Production REST API for task management system",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add request logging middleware (before error handler to log all requests)
    app.add_middleware(RequestLoggingMiddleware)

    # Add error handling middleware (last middleware to catch all errors)
    app.middleware("http")(error_handler_middleware)

    # Include routers
    app.include_router(health.router, tags=["Health"])
    app.include_router(tasks.router, prefix="/api/v1", tags=["Tasks"])
    app.include_router(projects.router, prefix="/api/v1", tags=["Projects"])
    app.include_router(sprints.router, prefix="/api/v1", tags=["Sprints"])
    app.include_router(action_lists.router, prefix="/api/v1", tags=["ActionLists"])

    logger.info(
        "application_created",
        app_name=settings.app_name,
        environment=settings.environment,
        debug=settings.debug,
    )

    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "taskman_api.main:app",
        host="0.0.0.0",  # nosec B104 - Intentional for Docker containers
        port=8000,
        reload=True,
        log_level="info",
    )
