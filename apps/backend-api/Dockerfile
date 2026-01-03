# TaskMan-v2 Backend API - Production Dockerfile
# Multi-stage build with uv package manager for optimized image size

# ============================================================================
# Stage 1: Builder - Install dependencies with uv
# ============================================================================
FROM python:3.11-slim AS builder

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files and source (for package installation)
COPY pyproject.toml requirements.txt README.md ./
COPY src/ ./src/

# Install Python dependencies and the taskman_api package using uv
RUN uv pip install --system --no-cache -r requirements.txt && \
    uv pip install --system --no-cache -e .

# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM python:3.11-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r taskman && \
    useradd -r -g taskman -u 1000 taskman

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn
COPY --from=builder /usr/local/bin/alembic /usr/local/bin/alembic

# Copy application code
COPY --chown=taskman:taskman . .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH="/app/src" \
    PATH="/app/.local/bin:$PATH" \
    # Default values (override with docker run -e or .env)
    API_HOST=0.0.0.0 \
    API_PORT=3001 \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO

# Expose API port
EXPOSE 3001

# Health check (validates both service and database connectivity)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3001/health || exit 1

# Switch to non-root user
USER taskman

# Run database migrations on startup, then start server with Gunicorn
# Gunicorn provides graceful worker management and zero-downtime reloads
# Uses the packaged taskman_api.main:app which includes Prometheus metrics
CMD ["sh", "-c", "alembic upgrade head && gunicorn taskman_api.main:app --bind ${API_HOST}:${API_PORT} --workers 4 --worker-class uvicorn.workers.UvicornWorker --log-level ${LOG_LEVEL} --access-logfile - --error-logfile -"]
