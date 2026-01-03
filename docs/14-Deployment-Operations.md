# 14 – Deployment & Operations

**Status**: Complete
**Version**: 2.0
**Last Updated**: 2025-11-11
**Related**: [01-Overview](01-Overview.md) | [02-Architecture](02-Architecture.md) | [12-Security-Authentication](12-Security-Authentication.md) | [13-Testing-Validation](13-Testing-Validation.md)

---

## Overview

ContextForge implements **local-first, offline-tolerant operations** with production-grade CI/CD pipelines, monitoring, and deployment strategies. Deployments are orchestrated through GitHub Actions with comprehensive quality gates.

### Deployment Principles (Codex)

From [ContextForge Work Codex](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md):

1. **Deployment is Orchestration** - Rollouts balance order with adaptability, ensuring resilience
2. **Resilience & Recovery** - MTTR is as critical as uptime; test it regularly
3. **Logs First** - All deployment events produce structured logs
4. **Triple-Check Protocol** - (1) Build → (2) Logs-first diagnostics → (3) Reproducibility validation

---

## Deployment Environments

### Environment Strategy

| Environment | Purpose | Branch | Deployment | Database |
|-------------|---------|--------|------------|----------|
| **Local** | Development | feature/* | Manual | SQLite |
| **CI** | Automated testing | PR | GitHub Actions | PostgreSQL (service) |
| **Staging** | Pre-production testing | develop | Auto (on merge) | PostgreSQL (cloud) |
| **Production** | Live system | main | Manual approval | PostgreSQL (HA) |

### Local Development

**Docker Compose** (recommended):
```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: taskman
      POSTGRES_PASSWORD: taskman
      POSTGRES_DB: taskman_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./TaskMan-v2/backend-api
    environment:
      DATABASE_URL: postgresql://taskman:taskman@postgres:5432/taskman_dev
      JWT_SECRET: dev-secret-change-in-prod
      LOG_LEVEL: DEBUG
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    volumes:
      - ./TaskMan-v2/backend-api:/app
    command: uvicorn backend_api.main:app --host 0.0.0.0 --reload

  frontend:
    build: ./TaskMan-v2
    environment:
      VITE_API_BASE_URL: http://localhost:8000
    ports:
      - "5173:5173"
    volumes:
      - ./TaskMan-v2:/app
      - /app/node_modules
    command: npm run dev

volumes:
  postgres_data:
```

**WSL Development** (Windows):
```powershell
# Start PostgreSQL in WSL
wsl -d Ubuntu -e sudo service postgresql start

# Set environment variables
$env:DATABASE_URL = "postgresql://taskman:taskman@localhost:5432/taskman_dev"
$env:JWT_SECRET = "dev-secret"

# Start backend
cd TaskMan-v2/backend-api
uvicorn backend_api.main:app --reload

# Start frontend (separate terminal)
cd TaskMan-v2
npm run dev
```

---

## CI/CD Pipelines

### GitHub Actions Workflows

ContextForge currently has **18 active CI/CD workflows**:

| Workflow | Purpose | Trigger | Status |
|----------|---------|---------|--------|
| **quality.yml** | Primary quality gates | PR, push to main | ✅ Active |
| **pytest-pr.yml** | Python test suite | PR | ✅ Active |
| **spectre-pester.yml** | PowerShell module tests | PR | ✅ Active |
| **constitutional-cognitive-testing.yml** | UCL/COF compliance | PR | ✅ Active |
| **guardrail-no-quiet.yml** | Logging coverage enforcement | PR | ✅ Active |
| **loguru-gap-gate.yml** | Logging quality gate | PR | ✅ Active |
| **pytest-discovery-guard.yml** | Test discovery validation | PR | ✅ Active |
| **pytest-slow.yml** | Slow test isolation | Scheduled | ✅ Active |
| **perf-guard.yml** | Performance regression | PR | ✅ Active |
| **ulog-benchmark.yml** | Logging performance | PR | ✅ Active |
| **hostpolicy-scan.yml** | Security scanning | PR | ✅ Active |
| **harness-smoke.yml** | Test harness smoke | PR | ✅ Active |
| **spectre-demo-smoke.yml** | Spectre UI smoke | PR | ✅ Active |
| **docs-validation.yml** | Documentation validation | PR | ✅ Active |
| **contextforge-orchestration.yml** | Full system integration | Push to main | ✅ Active |
| **quality-wu.yml** | Quality warm-up | PR | ✅ Active |
| **harness-dashboard-smoke.yml** | Dashboard smoke | PR | ✅ Active |
| **ulog-benchmark-schedule.yml** | Scheduled benchmarks | Daily | ✅ Active |

### Primary Quality Gate Pipeline

**File**: [.github/workflows/quality.yml](.github/workflows/quality.yml)

```yaml
name: Quality Gates

on:
  pull_request:
  push:
    branches: [main]

jobs:
  validate:
    runs-on: windows-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Create venv
        run: python -m venv .venv

      - name: Install Python deps
        run: |
          .\.venv\Scripts\python -m pip install --upgrade pip
          if (Test-Path pyproject.toml) {
            .\.venv\Scripts\python -m pip install .[dev]
          } else {
            .\.venv\Scripts\python -m pip install pytest pytest-cov typer ruff
          }

      - name: Guard - Enforce pytest-richer policy
        shell: pwsh
        run: |
          .\.venv\Scripts\python python\ci\verify_richer_policy.py

      - name: Run Validate-Stacks
        shell: pwsh
        run: pwsh -NoProfile -ExecutionPolicy Bypass -File build/Validate-Stacks.ps1

      - name: PowerShell Coverage
        shell: pwsh
        run: pwsh -NoProfile -ExecutionPolicy Bypass -File build/Generate-PowerShellCoverage.ps1

      - name: Autofix Sweep (PSSA + Ruff) (Non-Blocking)
        shell: pwsh
        run: |
          $ErrorActionPreference='Continue'
          Write-Host 'Starting autofix sweep'
          if (Test-Path build/Invoke-PSSA-Mode.ps1) {
            pwsh -NoProfile -ExecutionPolicy Bypass -File build/Invoke-PSSA-Mode.ps1 -Mode All -AutoFix -Path . -EnableCache 2>&1 | Write-Host
          }
          if (Test-Path build/Invoke-Ruff.ps1) {
            pwsh -NoProfile -ExecutionPolicy Bypass -File build/Invoke-Ruff.ps1 -AutoFix -Path . 2>&1 | Write-Host
          }

      - name: Python Linting Validation (Blocking)
        shell: pwsh
        run: |
          .\.venv\Scripts\python -m ruff check . --output-format=github
          if ($LASTEXITCODE -ne 0) {
            Write-Error "Python linting validation failed"
            exit 1
          }

      - name: Upload coverage artifacts
        uses: actions/upload-artifact@v4
        with:
          name: coverage-artifacts
          path: |
            build/artifacts/coverage/python/coverage.xml
            build/artifacts/coverage/powershell/coverage.xml
            build/artifacts/validation/stack_validation.json
```

### TaskMan-v2 CI/CD (Planned - P0-006)

**Current Status**: Planned for production readiness

**Phase 1: CI Pipeline** (2 days)

```yaml
# .github/workflows/taskman-ci.yml
name: TaskMan-v2 CI

on:
  pull_request:
    paths:
      - 'TaskMan-v2/**'
  push:
    branches: [main, develop]

jobs:
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install frontend dependencies
        working-directory: TaskMan-v2
        run: npm ci

      - name: Run linting
        run: npm run lint

      - name: Run unit tests
        run: npm run test

      - name: Run E2E tests
        run: npm run test:e2e

      - name: Run accessibility tests
        run: npm run test:a11y

      - name: Build frontend
        run: npm run build

  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install backend dependencies
        working-directory: TaskMan-v2/backend-api
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run linting
        run: ruff check .

      - name: Run type checking
        run: mypy .

      - name: Run tests
        run: pytest --cov=backend_api --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

**Phase 2: CD Pipeline** (1-2 days)

```yaml
# .github/workflows/taskman-cd.yml
name: TaskMan-v2 CD

on:
  push:
    branches: [main]
    paths:
      - 'TaskMan-v2/**'

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v3

      - name: Deploy backend to staging
        run: |
          # Deploy to AWS/Azure/GCP staging environment
          # Update DATABASE_URL, JWT_SECRET from staging secrets

      - name: Deploy frontend to staging
        run: |
          # Deploy to Vercel/Netlify staging

      - name: Run smoke tests
        run: npm run test:smoke -- --env=staging

  deploy-production:
    runs-on: ubuntu-latest
    needs: deploy-staging
    environment: production
    steps:
      - uses: actions/checkout@v3

      - name: Deploy backend to production
        run: |
          # Deploy to production with blue-green strategy

      - name: Deploy frontend to production
        run: |
          # Deploy to production CDN

      - name: Run smoke tests
        run: npm run test:smoke -- --env=production

      - name: Notify deployment
        run: |
          # Send Slack/Teams notification
```

---

## Container Deployment

### Docker Images

**Backend Dockerfile**:
```dockerfile
# TaskMan-v2/backend-api/Dockerfile
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 taskman && chown -R taskman:taskman /app
USER taskman

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD python -c "import requests; requests.get('http://localhost:8000/healthz')"

# Run application
EXPOSE 8000
CMD ["uvicorn", "backend_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile**:
```dockerfile
# TaskMan-v2/Dockerfile
FROM node:18-alpine as build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Build application
COPY . .
RUN npm run build

# Production image
FROM nginx:alpine

# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget -q --spider http://localhost:80/ || exit 1

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Kubernetes Deployment

**Backend Deployment**:
```yaml
# k8s/backend-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: taskman-backend
  namespace: contextforge
spec:
  replicas: 3
  selector:
    matchLabels:
      app: taskman-backend
  template:
    metadata:
      labels:
        app: taskman-backend
    spec:
      containers:
      - name: backend
        image: contextforge/taskman-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: taskman-secrets
              key: database-url
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: taskman-secrets
              key: jwt-secret
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /healthz
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: taskman-backend
  namespace: contextforge
spec:
  selector:
    app: taskman-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## Database Operations

### Migration Management

**Alembic Migrations** (TaskMan-v2):
```bash
# Create new migration
alembic revision --autogenerate -m "Add user roles table"

# Review generated migration
cat alembic/versions/xxxxx_add_user_roles_table.py

# Apply migration (staging)
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history --verbose
```

**Migration CI/CD**:
```yaml
# .github/workflows/db-migration.yml
name: Database Migration

on:
  push:
    branches: [main]
    paths:
      - 'TaskMan-v2/backend-api/alembic/**'

jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run migrations on staging
        env:
          DATABASE_URL: ${{ secrets.STAGING_DATABASE_URL }}
        run: |
          alembic upgrade head

      - name: Verify migration
        run: |
          alembic current
          alembic history
```

### Database Backups

**Automated Backups** (PostgreSQL):
```bash
#!/bin/bash
# scripts/backup-postgres.sh

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/backups/postgres"
DB_NAME="taskman_prod"

# Create backup
pg_dump -U taskman -h localhost -d $DB_NAME \
  | gzip > "$BACKUP_DIR/taskman_$TIMESTAMP.sql.gz"

# Upload to S3
aws s3 cp "$BACKUP_DIR/taskman_$TIMESTAMP.sql.gz" \
  s3://contextforge-backups/postgres/

# Retain last 30 days
find $BACKUP_DIR -name "taskman_*.sql.gz" -mtime +30 -delete

# Emit event
python -c "from python.services.unified_logger import logger; \
logger.info('database_backup_completed', timestamp='$TIMESTAMP')"
```

**Restore Procedure**:
```bash
#!/bin/bash
# scripts/restore-postgres.sh

BACKUP_FILE=$1

# Download from S3
aws s3 cp "s3://contextforge-backups/postgres/$BACKUP_FILE" /tmp/

# Restore
gunzip < "/tmp/$BACKUP_FILE" | psql -U taskman -h localhost -d taskman_prod

# Verify
psql -U taskman -h localhost -d taskman_prod -c "SELECT COUNT(*) FROM tasks;"

# Emit event
python -c "from python.services.unified_logger import logger; \
logger.info('database_restore_completed', backup_file='$BACKUP_FILE')"
```

---

## Monitoring & Observability

### Health Checks

**Backend Health Endpoint**:
```python
# backend-api/routers/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..dependencies.database import get_db
from ..services.unified_logger import logger

router = APIRouter()

@router.get("/healthz")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint.

    Emits: health_check event
    """
    try:
        # Check database connection
        db.execute("SELECT 1")

        logger.info("health_check", status="healthy")
        return {"status": "ok", "database": "connected"}

    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        return {"status": "degraded", "database": "disconnected"}

@router.get("/readyz")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check for Kubernetes.

    Emits: readiness_check event
    """
    # Check all dependencies (DB, Redis, etc.)
    checks = {
        "database": check_database(db),
        "redis": check_redis(),
        "storage": check_storage()
    }

    all_ready = all(checks.values())
    status_code = 200 if all_ready else 503

    logger.info("readiness_check", checks=checks, ready=all_ready)
    return {"status": "ready" if all_ready else "not_ready", "checks": checks}
```

### Logging Infrastructure

**Log Aggregation** (Planned):
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - loki_data:/loki

  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log
      - ./promtail-config.yml:/etc/promtail/config.yml
    command: -config.file=/etc/promtail/config.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  loki_data:
  grafana_data:
```

**Structured Logging Configuration**:
```python
# backend-api/services/unified_logger.py
import structlog
from pythonjsonlogger import jsonlogger

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
```

### Metrics (Planned)

**Prometheus Integration**:
```python
# backend-api/middleware/metrics.py
from prometheus_client import Counter, Histogram, Gauge
from fastapi import Request
import time

# Define metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"]
)

ACTIVE_TASKS = Gauge(
    "active_tasks_total",
    "Number of active tasks"
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Collect request metrics."""
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response
```

---

## Deployment Strategies

### Blue-Green Deployment

**Strategy**:
1. Deploy new version (green) alongside current (blue)
2. Run smoke tests on green
3. Switch traffic to green
4. Monitor for 15 minutes
5. If successful, decommission blue
6. If failed, instant rollback to blue

**Implementation** (Kubernetes):
```yaml
# k8s/blue-green-deployment.yml
apiVersion: v1
kind: Service
metadata:
  name: taskman-backend
spec:
  selector:
    app: taskman-backend
    version: blue  # Switch to 'green' during deployment
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
```

### Canary Deployment

**Strategy**:
1. Deploy new version to 10% of traffic
2. Monitor metrics (error rate, latency)
3. If healthy, increase to 50%
4. If healthy, increase to 100%
5. If unhealthy, instant rollback

**Implementation** (Istio):
```yaml
# k8s/canary-virtual-service.yml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: taskman-backend
spec:
  hosts:
  - taskman-backend
  http:
  - match:
    - headers:
        user-agent:
          regex: ".*Chrome.*"
    route:
    - destination:
        host: taskman-backend
        subset: v2
      weight: 10
    - destination:
        host: taskman-backend
        subset: v1
      weight: 90
```

### Rolling Deployment

**Strategy** (default Kubernetes):
```yaml
# k8s/rolling-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: taskman-backend
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1  # Max 1 pod down
      maxSurge: 1        # Max 1 extra pod
```

---

## Disaster Recovery

### Recovery Time Objective (RTO)

| Component | RTO | RPO | Strategy |
|-----------|-----|-----|----------|
| **Database** | 1 hour | 5 minutes | Automated backups every 5 min |
| **Backend API** | 15 minutes | 0 (stateless) | Blue-green deployment |
| **Frontend** | 5 minutes | 0 (static) | CDN with multiple regions |
| **File Storage** | 30 minutes | 1 hour | S3 with versioning |

### Disaster Recovery Playbook

**Scenario 1: Database Corruption**
1. Identify corruption timestamp from logs
2. Stop all write operations
3. Restore from most recent backup before corruption
4. Replay transaction logs to RPO
5. Verify data integrity
6. Resume operations
7. Post-mortem: Identify corruption source

**Scenario 2: Complete Region Failure**
1. Activate disaster recovery runbook
2. Promote secondary region to primary
3. Update DNS to point to DR region
4. Verify all services healthy
5. Restore database from replicas
6. Monitor for 24 hours
7. Post-mortem: Review failure cascade

**Scenario 3: Security Breach**
1. Isolate affected systems immediately
2. Rotate all secrets (JWT, DB passwords)
3. Review audit logs for breach scope
4. Deploy security patches
5. Notify affected users
6. File incident report
7. Implement additional controls

---

## Operational Runbooks

### Common Operations

**Restart Backend Service**:
```bash
# Docker
docker-compose restart backend

# Kubernetes
kubectl rollout restart deployment/taskman-backend -n contextforge

# Verify
kubectl get pods -n contextforge -l app=taskman-backend
```

**Scale Backend Service**:
```bash
# Kubernetes
kubectl scale deployment/taskman-backend --replicas=5 -n contextforge

# Verify
kubectl get deployment taskman-backend -n contextforge
```

**View Logs**:
```bash
# Docker
docker-compose logs -f backend

# Kubernetes
kubectl logs -f deployment/taskman-backend -n contextforge

# Loki (if configured)
logcli query '{app="taskman-backend"}' --since=1h
```

**Check Database Connection**:
```bash
# From backend pod
kubectl exec -it deployment/taskman-backend -n contextforge -- \
  python -c "from backend_api.dependencies.database import get_db; \
  db = next(get_db()); db.execute('SELECT 1')"
```

---

## Performance Optimization

### Caching Strategy

**Redis Cache** (planned):
```python
# backend-api/services/cache.py
import redis
from functools import wraps
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(ttl: int = 300):
    """Decorator to cache function results in Redis."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{args}:{kwargs}"

            # Check cache
            cached = redis_client.get(cache_key)
            if cached:
                logger.debug("cache_hit", key=cache_key)
                return json.loads(cached)

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            redis_client.setex(cache_key, ttl, json.dumps(result))
            logger.debug("cache_miss", key=cache_key)

            return result
        return wrapper
    return decorator

# Usage
@cache_result(ttl=600)
async def get_sprint_status(sprint_id: str):
    """Get sprint status (cached for 10 minutes)."""
    # Expensive query
    pass
```

### Database Optimization

**Connection Pooling**:
```python
# backend-api/dependencies/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # Max connections
    max_overflow=10,       # Extra connections during spikes
    pool_pre_ping=True,    # Verify connections before use
    pool_recycle=3600      # Recycle connections after 1 hour
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

**Query Optimization**:
```python
# Use eager loading to prevent N+1 queries
from sqlalchemy.orm import joinedload

def get_tasks_with_assignees(db: Session):
    """Fetch tasks with assignees in single query."""
    return db.query(Task).options(
        joinedload(Task.assignee),
        joinedload(Task.sprint)
    ).all()
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing (unit, integration, E2E)
- [ ] Code review approved
- [ ] Security scan completed
- [ ] Performance benchmarks meet targets
- [ ] Database migrations tested
- [ ] Rollback plan documented
- [ ] Deployment window scheduled
- [ ] Stakeholders notified
- [ ] Monitoring dashboards ready
- [ ] Incident response team on standby

### During Deployment

- [ ] Deploy to staging first
- [ ] Run smoke tests
- [ ] Monitor error rates
- [ ] Monitor latency (p50, p95, p99)
- [ ] Check database connection pool
- [ ] Verify authentication working
- [ ] Test critical user flows
- [ ] Monitor resource utilization (CPU, memory)

### Post-Deployment

- [ ] Verify all services healthy
- [ ] Monitor for 1 hour minimum
- [ ] Check logs for errors
- [ ] Verify metrics dashboards
- [ ] Test rollback procedure
- [ ] Document deployment notes
- [ ] Update runbooks if needed
- [ ] Send deployment summary

---

## Cross References

### Foundation Documents

- [01-Overview.md](01-Overview.md) - System overview with operational principles
- [02-Architecture.md](02-Architecture.md) - Deployment topology
- [12-Security-Authentication.md](12-Security-Authentication.md) - Security in production
- [13-Testing-Validation.md](13-Testing-Validation.md) - Test automation

### Authoritative Source

- [docs/Codex/ContextForge Work Codex.md](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md) - **PRIMARY SOURCE**

### Implementation Details

- [.github/workflows/quality.yml](../.github/workflows/quality.yml) - Primary CI/CD pipeline
- [docker-compose.yml](../docker-compose.yml) - Local development environment

---

**Document Status**: Complete ✅
**Authoritative**: Yes (integrated with Codex)
**Next Review**: 2026-02-11 (quarterly)
**Maintained By**: ContextForge DevOps Team

---

*"Deployment is orchestration: rollouts must balance order with adaptability, ensuring resilience."*
