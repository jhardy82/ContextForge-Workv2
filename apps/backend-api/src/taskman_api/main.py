"""
TaskMan-v2 Backend API - FastAPI Application
Production-ready REST API server with health checks and database connectivity.
"""

from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError

from taskman_api.api import health as health_router
from taskman_api.api import metrics as metrics_router
from taskman_api.core.errors import AppError, ConflictError, NotFoundError
from taskman_api.db.session import check_db_health, init_db
from taskman_api.middleware import LoggingMiddleware
from taskman_api.rate_limiter import limiter
from taskman_api.routers import (
    action_lists_router,
    agent_router,
    checklists_router,
    conversations_router,
    diagnostic_router,
    phases_router,
    plans_router,
    projects_router,
    qse_router,
    sprints_router,
    tasks_router,
)
from taskman_api.routers import context as context_router

# OpenTelemetry circuit breaker and metrics


# ============================================================================
# Configuration
# ============================================================================
class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Allow extra env vars without failing
        env_prefix="APP_",
    )

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 3001
    environment: str = "development"

    # Database Configuration
    database_url: str = "postgresql://contextforge:contextforge@localhost:5434/taskman_v2"

    # Logging Configuration
    log_level: str = "INFO"

    def validate_startup(self) -> list[str]:
        """
        Validate critical configuration at startup.
        Returns list of validation warnings (empty if all OK).
        """
        warnings = []

        # Validate database URL format
        if not self.database_url.startswith(("postgresql://", "postgres://")):
            warnings.append(
                f"DATABASE_URL should start with postgresql:// (got: {self.database_url[:20]}...)"
            )

        # Validate log level
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level.upper() not in valid_levels:
            warnings.append(f"LOG_LEVEL should be one of {valid_levels} (got: {self.log_level})")

        # Validate port range
        if not (1 <= self.api_port <= 65535):
            warnings.append(f"API_PORT should be 1-65535 (got: {self.api_port})")

        # Environment-specific validations
        if self.environment == "production" and (
            "localhost" in self.database_url or "127.0.0.1" in self.database_url
        ):
            warnings.append("Production environment should not use localhost database")

        return warnings


settings = Settings()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
)
logger = structlog.get_logger()

# Session metrics for summary event
_session_metrics = {
    "requests_processed": 0,
    "errors_logged": 0,
    "start_time": None,
}


# ============================================================================
# Application Lifecycle
# ============================================================================
@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan manager - handles startup and shutdown."""
    import time

    _session_metrics["start_time"] = time.time()
    logger.info("session_start", environment=settings.environment, version="0.1.0")

    # Configure LoggingMiddleware to update session metrics
    LoggingMiddleware.set_metrics(_session_metrics)

    # Startup validation
    validation_warnings = settings.validate_startup()
    if validation_warnings:
        for warning in validation_warnings:
            logger.warning("config_validation_warning", message=warning)

    # Initialize database tables
    try:
        # Initialize primary API models
        await init_db()

        # Initialize QSE models (using their own Base)
        from cf_core.dao.base import Base as QSEBase

        await init_db(base_class=QSEBase)
        db_health = await check_db_health()
        logger.info(
            "database_connected",
            connected=db_health.get("connected", False),
            latency_ms=db_health.get("latency_ms"),
        )
    except Exception as e:
        logger.error("database_init_failed", error=str(e))
        # Continue startup - API can run without DB for health checks

    logger.info(
        "api_startup",
        environment=settings.environment,
        port=settings.api_port,
        database_configured=bool(settings.database_url),
        validation_warnings=len(validation_warnings),
    )

    yield

    # Shutdown with session_summary
    import hashlib

    uptime_seconds = (
        time.time() - _session_metrics["start_time"]
        if _session_metrics["start_time"]
        else 0
    )
    evidence_data = f"{_session_metrics['requests_processed']}:{_session_metrics['errors_logged']}:{uptime_seconds}"
    evidence_hash = hashlib.sha256(evidence_data.encode()).hexdigest()[:16]

    logger.info(
        "session_summary",
        requests_processed=_session_metrics["requests_processed"],
        errors_logged=_session_metrics["errors_logged"],
        uptime_seconds=round(uptime_seconds, 2),
        evidence_hash=evidence_hash,
    )
    logger.info("session_end", uptime_seconds=round(uptime_seconds, 2))
    logger.info("api_shutdown")


# ============================================================================
# FastAPI Application
# ============================================================================
app = FastAPI(
    title="TaskMan-v2 Backend API",
    description="Production REST API for TaskMan-v2 task management system",
    version="0.1.0",
    lifespan=lifespan,
)

# Register rate limiter with app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "*",
    ],  # Expanded for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Request/Response Logging Middleware (IV-002 Enhancement)
# ============================================================================
# LoggingMiddleware provides:
# - Correlation ID (X-Request-ID) generation and propagation
# - Request timing with X-Response-Time header
# - Structured JSON logging of requests and responses
# - Sensitive query parameter redaction
# - Configurable health endpoint exclusion (TASKMAN_LOG_HEALTH_ENDPOINTS)
# - Log level control via TASKMAN_LOG_LEVEL environment variable
app.add_middleware(LoggingMiddleware)


# ============================================================================
# Response Models
# ============================================================================
class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    environment: str
    version: str
    database: dict[str, Any]


class ErrorResponse(BaseModel):
    """Standard error response model."""

    detail: str
    status_code: int


# ============================================================================
# Health Check Endpoints
# ============================================================================
@app.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> HealthResponse:
    """
    Health check endpoint for Docker HEALTHCHECK and monitoring.

    Returns:
        HealthResponse with system status and database connectivity
    """
    # Perform actual database connectivity check
    db_health = await check_db_health()

    # Determine overall status based on active mode connectivity
    mode = db_health.get("mode", "unknown")
    primary_ok = db_health.get("primary", {}).get("connected", False)
    fallback_ok = db_health.get("fallback", {}).get("connected", False)

    overall_status = "healthy"
    if mode == "primary" and not primary_ok:
        overall_status = "degraded"  # Should allow fallback?
    if mode == "fallback":
        overall_status = "degraded"  # Running on fallback is a degraded state for production
    if not primary_ok and not fallback_ok:
        overall_status = "unhealthy"

    return HealthResponse(
        status=overall_status,
        environment=settings.environment,
        version="0.1.0",
        database={
            "mode": mode,
            "connected": primary_ok or fallback_ok,
            "primary": db_health.get("primary"),
            "fallback": db_health.get("fallback"),
            "url": settings.database_url.split("@")[1]
            if "@" in settings.database_url
            else "masked",
        },
    )


@app.get("/", status_code=status.HTTP_200_OK)
async def root() -> dict[str, str]:
    """
    Root endpoint - API information.

    Returns:
        Basic API metadata
    """
    return {
        "name": "TaskMan-v2 Backend API",
        "version": "0.1.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
    }


# ============================================================================
# MCP Compatibility Endpoints
#
# The TaskMan MCP tooling (and some legacy clients) probe /api and /api/health
# for readiness, and may call resource routes under /api/*.
#
# TaskMan-v2's canonical REST surface is /api/v1/*.
# To keep the updated backend as the single source of truth while preserving
# compatibility, we provide a minimal additive shim here.
# ============================================================================


@app.get("/api", status_code=status.HTTP_200_OK)
async def api_root() -> dict[str, str]:
    return {
        "status": "ok",
        "message": "TaskMan-v2 API compatibility root",
        "canonical_base": "/api/v1",
        "health": "/api/health",
        "docs": "/docs",
    }


@app.get("/api/health", status_code=status.HTTP_200_OK)
async def api_health() -> dict[str, str]:
    return {
        "status": "ok",
        "canonical": "/health",
        "canonical_base": "/api/v1",
    }


# ============================================================================
# Error Handlers
# ============================================================================
@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request, exc: NotFoundError) -> JSONResponse:
    """Handle NotFoundError as HTTP 404."""
    logger.warning(
        "not_found_error",
        error=str(exc),
        path=request.url.path,
        entity_type=exc.extra.get("entity_type"),
        entity_id=exc.extra.get("entity_id"),
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=exc.to_problem_details(str(request.url)),
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc: IntegrityError) -> JSONResponse:
    """Handle SQLAlchemy IntegrityError as HTTP 409 Conflict."""
    logger.warning(
        "conflict_error",
        error=str(exc.orig) if exc.orig else str(exc),
        path=request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "type": "https://api.taskman-v2.local/problems/conflict",
            "title": "Resource Conflict",
            "status": 409,
            "detail": "A resource with this identifier already exists",
            "instance": str(request.url),
        },
    )


@app.exception_handler(ConflictError)
async def conflict_error_handler(request, exc: ConflictError) -> JSONResponse:
    """Handle ConflictError as HTTP 409 Conflict."""
    logger.warning(
        "conflict_error",
        error=str(exc),
        path=request.url.path,
        entity_type=exc.extra.get("entity_type"),
    )
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=exc.to_problem_details(str(request.url)),
    )


@app.exception_handler(AppError)
async def app_error_handler(request, exc: AppError) -> JSONResponse:
    """Handle application errors with their configured status codes."""
    logger.warning(
        "app_error",
        error=str(exc),
        path=request.url.path,
        status_code=exc.status_code,
        problem_type=exc.problem_type,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_problem_details(str(request.url)),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled errors."""
    logger.error("unhandled_exception", error=str(exc), path=request.url.path)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "status_code": 500},
    )


# ============================================================================
# API Routers
# ============================================================================
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(projects_router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(sprints_router, prefix="/api/v1/sprints", tags=["sprints"])
app.include_router(action_lists_router, prefix="/api/v1/action-lists", tags=["action-lists"])
app.include_router(agent_router, prefix="/api/v1/agent", tags=["agent"])
app.include_router(qse_router, prefix="/api/v1", tags=["qse"])
app.include_router(context_router.router, prefix="/api/v1/context", tags=["context"])


# State Store routers (restored in PR #179)

# These routers include their resource prefix in endpoints (e.g., /checklists/search)
app.include_router(checklists_router, prefix="/api/v1", tags=["checklists"])
app.include_router(conversations_router, prefix="/api/v1", tags=["conversations"])
app.include_router(phases_router, prefix="/api/v1", tags=["phases"])
app.include_router(plans_router, prefix="/api/v1", tags=["plans"])
app.include_router(diagnostic_router, prefix="/api/v1/diagnostic", tags=["diagnostic"])

# Legacy/compat aliases for MCP tooling that targets /api/*
app.include_router(tasks_router, prefix="/api/tasks", tags=["tasks", "compat"])
app.include_router(projects_router, prefix="/api/projects", tags=["projects", "compat"])
app.include_router(sprints_router, prefix="/api/sprints", tags=["sprints", "compat"])
app.include_router(action_lists_router, prefix="/api/action-lists", tags=["action-lists", "compat"])

# OpenTelemetry health and metrics endpoints
app.include_router(health_router.router, tags=["health"])
app.include_router(metrics_router.router, tags=["metrics"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
    )
