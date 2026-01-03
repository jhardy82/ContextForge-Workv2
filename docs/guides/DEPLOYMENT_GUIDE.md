# ContextForge CLI - Production Deployment Guide

## Overview

This comprehensive guide covers deploying the ContextForge CLI in production environments with emphasis on security, performance, monitoring, and maintainability.

## Table of Contents

- [Environment Management](#environment-management)
- [Security Considerations](#security-considerations)
- [Container Deployment](#container-deployment)
- [CI/CD Integration](#cicd-integration)
- [Performance Tuning](#performance-tuning)
- [Monitoring and Logging](#monitoring-and-logging)
- [Troubleshooting](#troubleshooting)
- [Backup and Recovery](#backup-and-recovery)
- [Health Checks](#health-check-implementation)
- [Migration Guide](#migration-guide)

---

## Environment Management

### Environment File Patterns

The ContextForge CLI follows a hierarchical environment file loading pattern:

```bash
# Loading order (highest precedence first):
.env.local          # Local overrides (never commit)
.env.production     # Production-specific settings
.env.staging        # Staging-specific settings
.env.development    # Development-specific settings
.env                # Default/shared settings
```

### Environment Variable Precedence

The complete precedence order from highest to lowest:

1. **System Environment Variables** - `os.environ`
2. **Command Line Arguments** - CLI flags and options
3. **Local Environment File** - `.env.local`
4. **Environment-Specific File** - `.env.{environment}`
5. **Default Environment File** - `.env`
6. **Application Defaults** - Built-in configuration

### Production Environment Template

Create `.env.production` with production-specific settings:

```bash
# Production Environment Configuration
CF_ENVIRONMENT=production

# Performance Optimizations
CF_CLI_ENABLE_PERF_OPT=true
CF_CACHE_TTL=300
CF_MAX_WORKERS=4

# Security Settings
CF_LOG_LEVEL=INFO
CF_DISABLE_DEBUG=true
CF_SECURE_MODE=true

# Database Configuration
CF_DB_CONNECTION_TIMEOUT=30
CF_DB_POOL_SIZE=10
CF_DB_MAX_OVERFLOW=20

# Monitoring
CF_METRICS_ENABLED=true
CF_HEALTH_CHECK_INTERVAL=60
CF_TELEMETRY_ENDPOINT=https://monitoring.company.com/telemetry

# Error Handling
CF_ERROR_REPORTING=true
CF_SENTRY_DSN=${SENTRY_DSN}
CF_SLACK_WEBHOOK=${SLACK_WEBHOOK}
```

### Environment-Specific Configuration

#### Development (.env.development)
```bash
CF_ENVIRONMENT=development
CF_LOG_LEVEL=DEBUG
CF_ENABLE_DEV_TOOLS=true
CF_AUTO_RELOAD=true
CF_MOCK_EXTERNAL_APIS=true
```

#### Staging (.env.staging)
```bash
CF_ENVIRONMENT=staging
CF_LOG_LEVEL=INFO
CF_ENABLE_PERFORMANCE_PROFILING=true
CF_LOAD_TEST_MODE=true
CF_ENABLE_SMOKE_TESTS=true
```

---

## Security Considerations

### Sensitive Data Management

**Never commit sensitive data to version control:**

```bash
# Add to .gitignore
.env.local
.env.production
.env.staging
secrets/
*.key
*.pem
*.p12
```

### Secret Management Best Practices

#### 1. Use Environment Variables for Secrets

```bash
# Good: Environment variable
CF_API_KEY=${API_KEY}
CF_DATABASE_PASSWORD=${DB_PASSWORD}

# Bad: Hardcoded secret
CF_API_KEY=sk-1234567890abcdef
```

#### 2. Secret Management Services

**AWS Secrets Manager Integration:**
```python
# tools/secret_manager.py
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name, region_name="us-east-1"):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        response = client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    except ClientError as e:
        raise e
```

**Azure Key Vault Integration:**
```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

def get_azure_secret(vault_url, secret_name):
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    secret = client.get_secret(secret_name)
    return secret.value
```

**HashiCorp Vault Integration:**
```python
import hvac

def get_vault_secret(vault_url, token, secret_path):
    client = hvac.Client(url=vault_url, token=token)
    response = client.secrets.kv.v2.read_secret_version(path=secret_path)
    return response['data']['data']
```

### Environment Variable Security

#### Encryption at Rest
```python
# tools/env_encryption.py
from cryptography.fernet import Fernet
import base64

class EncryptedEnvManager:
    def __init__(self, key: str):
        self.cipher = Fernet(key.encode())

    def encrypt_value(self, value: str) -> str:
        encrypted = self.cipher.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()

    def decrypt_value(self, encrypted_value: str) -> str:
        encrypted_bytes = base64.b64decode(encrypted_value.encode())
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return decrypted.decode()
```

#### Environment Variable Validation
```python
# tools/env_validator.py
import re
from typing import Dict, List

class EnvironmentValidator:
    SENSITIVE_PATTERNS = [
        r'.*password.*',
        r'.*secret.*',
        r'.*key.*',
        r'.*token.*',
        r'.*credential.*',
    ]

    def validate_environment(self, env_vars: Dict[str, str]) -> List[str]:
        issues = []

        for key, value in env_vars.items():
            # Check for potentially sensitive data
            if self._is_sensitive_key(key):
                if len(value) < 8:
                    issues.append(f"Potentially weak secret: {key}")
                if value in ['password', 'secret', 'changeme']:
                    issues.append(f"Default/weak value for: {key}")

            # Check for common issues
            if ' ' in value and not value.startswith('"'):
                issues.append(f"Unquoted value with spaces: {key}")

        return issues

    def _is_sensitive_key(self, key: str) -> bool:
        return any(re.match(pattern, key.lower())
                  for pattern in self.SENSITIVE_PATTERNS)
```

---

## Container Deployment

### Docker Configuration

#### Multi-Stage Dockerfile
```dockerfile
# Dockerfile
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r cfuser && useradd --no-log-init -r -g cfuser cfuser

WORKDIR /app

# Development stage
FROM base as development

COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

COPY . .
RUN chown -R cfuser:cfuser /app
USER cfuser

CMD ["python", "cf_cli.py", "--help"]

# Production stage
FROM base as production

# Install production dependencies only
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY --chown=cfuser:cfuser . .

# Remove development files
RUN rm -rf tests/ docs/dev/ .git/

# Switch to non-root user
USER cfuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import cf_cli; print('OK')" || exit 1

# Default command
CMD ["python", "cf_cli.py", "status", "health"]
```

#### Docker Compose for Production
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  cf-cli:
    build:
      context: .
      dockerfile: Dockerfile
      target: production

    environment:
      - CF_ENVIRONMENT=production
      - CF_LOG_LEVEL=INFO
      - CF_ENABLE_PERF_OPT=true

    env_file:
      - .env.production

    volumes:
      - ./logs:/app/logs
      - ./data:/app/data:ro

    restart: unless-stopped

    healthcheck:
      test: ["CMD", "python", "cf_cli.py", "status", "health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

    security_opt:
      - no-new-privileges:true

    read_only: true

    tmpfs:
      - /tmp:noexec,nosuid,size=100m

  # Redis for caching (optional)
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  redis_data:
```

#### Kubernetes Deployment
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cf-cli
  labels:
    app: cf-cli
    version: v1.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cf-cli
  template:
    metadata:
      labels:
        app: cf-cli
        version: v1.0
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000

      containers:
      - name: cf-cli
        image: contextforge/cf-cli:v1.0
        imagePullPolicy: IfNotPresent

        ports:
        - containerPort: 8000
          name: http

        env:
        - name: CF_ENVIRONMENT
          value: "production"
        - name: CF_LOG_LEVEL
          value: "INFO"
        - name: CF_ENABLE_PERF_OPT
          value: "true"

        envFrom:
        - secretRef:
            name: cf-cli-secrets
        - configMapRef:
            name: cf-cli-config

        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"

        livenessProbe:
          exec:
            command: ["python", "cf_cli.py", "status", "health"]
          initialDelaySeconds: 30
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3

        readinessProbe:
          exec:
            command: ["python", "cf_cli.py", "status", "ready"]
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3

        volumeMounts:
        - name: config
          mountPath: /app/config
          readOnly: true
        - name: logs
          mountPath: /app/logs
        - name: tmp
          mountPath: /tmp

      volumes:
      - name: config
        configMap:
          name: cf-cli-config
      - name: logs
        emptyDir: {}
      - name: tmp
        emptyDir: {}

---
apiVersion: v1
kind: Service
metadata:
  name: cf-cli-service
spec:
  selector:
    app: cf-cli
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
  type: ClusterIP

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: cf-cli-config
data:
  .env.production: |
    CF_ENVIRONMENT=production
    CF_LOG_LEVEL=INFO
    CF_ENABLE_PERF_OPT=true
    CF_CACHE_TTL=300
    CF_MAX_WORKERS=4

---
apiVersion: v1
kind: Secret
metadata:
  name: cf-cli-secrets
type: Opaque
stringData:
  CF_API_KEY: "your-api-key-here"
  CF_DATABASE_PASSWORD: "your-db-password-here"
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy-production.yml
name: Production Deployment

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}/cf-cli

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'

    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

  build-and-test:
    runs-on: ubuntu-latest
    needs: security-scan

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt

    - name: Run tests
      run: |
        python -m pytest tests/ -v --cov=./ --cov-report=xml

    - name: Performance benchmarks
      run: |
        python tools/performance_benchmark.py --runs 5 --export-results

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build-docker:
    runs-on: ubuntu-latest
    needs: build-and-test
    outputs:
      image-digest: ${{ steps.build.outputs.digest }}

    steps:
    - uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=tag
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          type=sha

    - name: Build and push
      id: build
      uses: docker/build-push-action@v5
      with:
        context: .
        target: production
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        platforms: linux/amd64,linux/arm64
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy-production:
    runs-on: ubuntu-latest
    needs: build-docker
    environment: production

    steps:
    - uses: actions/checkout@v4

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1

    - name: Deploy to EKS
      run: |
        aws eks update-kubeconfig --name production-cluster
        kubectl set image deployment/cf-cli cf-cli=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}@${{ needs.build-docker.outputs.image-digest }}
        kubectl rollout status deployment/cf-cli --timeout=300s

    - name: Run smoke tests
      run: |
        kubectl exec deployment/cf-cli -- python cf_cli.py status health
        kubectl exec deployment/cf-cli -- python cf_cli.py config validate

    - name: Notify deployment
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        text: "Production deployment completed successfully!"
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### Azure DevOps Pipeline

```yaml
# azure-pipelines.yml
trigger:
  tags:
    include:
    - v*

pool:
  vmImage: 'ubuntu-latest'

variables:
  REGISTRY: 'cfregistry.azurecr.io'
  IMAGE_NAME: 'cf-cli'
  TAG: $(Build.SourceBranchName)

stages:
- stage: Build
  displayName: 'Build and Test'
  jobs:
  - job: Test
    displayName: 'Run Tests'
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '3.12'
        displayName: 'Use Python 3.12'

    - script: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
      displayName: 'Install dependencies'

    - script: |
        python -m pytest tests/ -v --junitxml=test-results.xml --cov=./ --cov-report=xml
      displayName: 'Run tests'

    - task: PublishTestResults@2
      inputs:
        testResultsFiles: 'test-results.xml'
        testRunTitle: 'Python Tests'

    - task: PublishCodeCoverageResults@1
      inputs:
        codeCoverageTool: 'Cobertura'
        summaryFileLocation: 'coverage.xml'

  - job: Docker
    displayName: 'Build Docker Image'
    dependsOn: Test
    steps:
    - task: Docker@2
      displayName: 'Build and push image'
      inputs:
        containerRegistry: 'Azure Container Registry'
        repository: $(IMAGE_NAME)
        command: 'buildAndPush'
        Dockerfile: 'Dockerfile'
        tags: |
          $(TAG)
          latest

- stage: Deploy
  displayName: 'Deploy to Production'
  dependsOn: Build
  condition: and(succeeded(), startsWith(variables['Build.SourceBranch'], 'refs/tags/v'))
  jobs:
  - deployment: Production
    displayName: 'Deploy to AKS'
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: KubernetesManifest@0
            displayName: 'Deploy to AKS'
            inputs:
              action: 'deploy'
              kubernetesServiceConnection: 'AKS-Production'
              manifests: |
                k8s/deployment.yaml
                k8s/service.yaml
              containers: '$(REGISTRY)/$(IMAGE_NAME):$(TAG)'
```

---

## Performance Tuning

### Optimization Configuration

Based on the performance benchmark findings, apply these production optimizations:

```bash
# .env.production - Performance Settings
CF_CLI_ENABLE_PERF_OPT=true
CF_CACHE_TTL=300
CF_CONFIG_CACHE_SIZE=100
CF_ENV_VAR_CACHE_SIZE=256

# Connection pooling
CF_DB_POOL_SIZE=20
CF_DB_MAX_OVERFLOW=10
CF_CONNECTION_TIMEOUT=30
CF_READ_TIMEOUT=60

# Worker configuration
CF_MAX_WORKERS=4
CF_WORKER_TIMEOUT=300
CF_QUEUE_SIZE=1000

# Memory optimization
CF_GC_THRESHOLD=700,10,10
CF_MAX_MEMORY_MB=512

# I/O optimization
CF_ASYNC_IO=true
CF_BUFFER_SIZE=8192
CF_BATCH_SIZE=100
```

### Resource Limits

#### Docker Resource Limits
```yaml
# docker-compose.prod.yml
services:
  cf-cli:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '1.0'
        reservations:
          memory: 256M
          cpus: '0.5'
```

#### Kubernetes Resource Management
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
    ephemeral-storage: "1Gi"
  limits:
    memory: "512Mi"
    cpu: "1000m"
    ephemeral-storage: "2Gi"
```

### Performance Monitoring

```python
# tools/performance_monitor.py
import psutil
import time
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class PerformanceMetrics:
    timestamp: float
    cpu_percent: float
    memory_mb: float
    disk_io: Dict[str, int]
    network_io: Dict[str, int]

class ProductionPerformanceMonitor:
    def __init__(self, interval: int = 60):
        self.interval = interval
        self.metrics_history: List[PerformanceMetrics] = []

    def collect_metrics(self) -> PerformanceMetrics:
        return PerformanceMetrics(
            timestamp=time.time(),
            cpu_percent=psutil.cpu_percent(interval=1),
            memory_mb=psutil.virtual_memory().used / 1024 / 1024,
            disk_io=psutil.disk_io_counters()._asdict(),
            network_io=psutil.net_io_counters()._asdict()
        )

    def check_thresholds(self, metrics: PerformanceMetrics) -> List[str]:
        alerts = []

        if metrics.cpu_percent > 80:
            alerts.append(f"High CPU usage: {metrics.cpu_percent:.1f}%")

        if metrics.memory_mb > 400:  # 400MB threshold
            alerts.append(f"High memory usage: {metrics.memory_mb:.1f}MB")

        return alerts
```

---

## Monitoring and Logging

### Structured Logging Configuration

```python
# tools/production_logging.py
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, 'correlation_id'):
            log_entry['correlation_id'] = record.correlation_id

        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id

        return json.dumps(log_entry)

def setup_production_logging():
    """Configure production-ready logging"""

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)

    # File handler for errors
    error_handler = logging.FileHandler('/app/logs/error.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(error_handler)

    # Performance logger
    perf_logger = logging.getLogger('performance')
    perf_handler = logging.FileHandler('/app/logs/performance.log')
    perf_handler.setFormatter(JSONFormatter())
    perf_logger.addHandler(perf_handler)
    perf_logger.setLevel(logging.INFO)
```

### Metrics Collection

```python
# tools/metrics_collector.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
from functools import wraps

# Define metrics
REQUEST_COUNT = Counter('cf_cli_requests_total', 'Total requests', ['method', 'status'])
REQUEST_DURATION = Histogram('cf_cli_request_duration_seconds', 'Request duration')
ACTIVE_CONNECTIONS = Gauge('cf_cli_active_connections', 'Active connections')
CACHE_HIT_RATIO = Gauge('cf_cli_cache_hit_ratio', 'Cache hit ratio')

def track_performance(func):
    """Decorator to track function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            REQUEST_COUNT.labels(method=func.__name__, status='success').inc()
            return result
        except Exception as e:
            REQUEST_COUNT.labels(method=func.__name__, status='error').inc()
            raise
        finally:
            REQUEST_DURATION.observe(time.time() - start_time)
    return wrapper

def start_metrics_server(port: int = 8000):
    """Start Prometheus metrics server"""
    start_http_server(port)
```

### Health Check Implementation

```python
# tools/health_check.py
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
import subprocess
import psutil

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class HealthCheckResult:
    name: str
    status: HealthStatus
    message: str
    details: Optional[Dict] = None

class ProductionHealthChecker:
    def __init__(self):
        self.checks = [
            self._check_system_resources,
            self._check_configuration,
            self._check_dependencies,
            self._check_cache_system,
        ]

    def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        results = {}

        for check in self.checks:
            try:
                result = check()
                results[result.name] = result
            except Exception as e:
                results[check.__name__] = HealthCheckResult(
                    name=check.__name__,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check failed: {str(e)}"
                )

        return results

    def _check_system_resources(self) -> HealthCheckResult:
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage('/')

        if memory.percent > 90 or cpu_percent > 90 or disk.percent > 90:
            return HealthCheckResult(
                name="system_resources",
                status=HealthStatus.UNHEALTHY,
                message="High resource usage",
                details={
                    "memory_percent": memory.percent,
                    "cpu_percent": cpu_percent,
                    "disk_percent": disk.percent
                }
            )
        elif memory.percent > 80 or cpu_percent > 80 or disk.percent > 80:
            return HealthCheckResult(
                name="system_resources",
                status=HealthStatus.DEGRADED,
                message="Moderate resource usage",
                details={
                    "memory_percent": memory.percent,
                    "cpu_percent": cpu_percent,
                    "disk_percent": disk.percent
                }
            )

        return HealthCheckResult(
            name="system_resources",
            status=HealthStatus.HEALTHY,
            message="Resource usage normal"
        )

    def _check_configuration(self) -> HealthCheckResult:
        try:
            from tools.performance_optimization import get_optimized_config
            config = get_optimized_config()

            return HealthCheckResult(
                name="configuration",
                status=HealthStatus.HEALTHY,
                message="Configuration loaded successfully"
            )
        except Exception as e:
            return HealthCheckResult(
                name="configuration",
                status=HealthStatus.UNHEALTHY,
                message=f"Configuration error: {str(e)}"
            )

    def _check_dependencies(self) -> HealthCheckResult:
        critical_imports = [
            'pydantic',
            'typer',
            'rich',
        ]

        failed_imports = []
        for module in critical_imports:
            try:
                __import__(module)
            except ImportError:
                failed_imports.append(module)

        if failed_imports:
            return HealthCheckResult(
                name="dependencies",
                status=HealthStatus.UNHEALTHY,
                message=f"Missing dependencies: {', '.join(failed_imports)}"
            )

        return HealthCheckResult(
            name="dependencies",
            status=HealthStatus.HEALTHY,
            message="All dependencies available"
        )

    def _check_cache_system(self) -> HealthCheckResult:
        try:
            from tools.performance_optimization import get_cache_stats
            stats = get_cache_stats()

            # Check cache hit ratio
            env_stats = stats.get('env_var_cache_info', {})
            hits = env_stats.get('hits', 0)
            misses = env_stats.get('misses', 0)

            if hits + misses > 0:
                hit_ratio = hits / (hits + misses)
                if hit_ratio < 0.5:
                    return HealthCheckResult(
                        name="cache_system",
                        status=HealthStatus.DEGRADED,
                        message=f"Low cache hit ratio: {hit_ratio:.2f}",
                        details=stats
                    )

            return HealthCheckResult(
                name="cache_system",
                status=HealthStatus.HEALTHY,
                message="Cache system functioning normally",
                details=stats
            )
        except Exception as e:
            return HealthCheckResult(
                name="cache_system",
                status=HealthStatus.UNHEALTHY,
                message=f"Cache system error: {str(e)}"
            )
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Performance Issues

**Symptom:** Slow CLI startup times (>2 seconds)
```bash
# Diagnosis
python tools/performance_benchmark.py --detailed --memory-profile

# Solutions
export CF_CLI_ENABLE_PERF_OPT=true  # Enable optimizations
export CF_CACHE_TTL=600             # Increase cache TTL
python cf_cli.py config clear-cache # Clear corrupted cache
```

**Symptom:** High memory usage
```bash
# Diagnosis
python -c "
from tools.performance_optimization import get_cache_stats
import json
print(json.dumps(get_cache_stats(), indent=2))
"

# Solutions
export CF_CONFIG_CACHE_SIZE=50      # Reduce cache size
export CF_GC_THRESHOLD=500,5,5      # More aggressive garbage collection
python cf_cli.py config clear-cache # Clear cache
```

#### 2. Configuration Issues

**Symptom:** Environment variables not loading
```bash
# Diagnosis
python cf_cli.py config validate --verbose
python cf_cli.py config show --all

# Solutions
# Check file permissions
ls -la .env*

# Verify environment precedence
CF_DEBUG=true python cf_cli.py config show

# Test specific environment
CF_ENVIRONMENT=production python cf_cli.py config validate
```

**Symptom:** Cache corruption
```bash
# Diagnosis
python cf_cli.py config perf-stats

# Solutions
python cf_cli.py config clear-cache
rm -rf ~/.cache/cf-cli/  # Clear user cache
export CF_CLI_DISABLE_PERF_OPT=1  # Temporary disable
```

#### 3. Container Issues

**Symptom:** Container startup failures
```bash
# Diagnosis
docker logs cf-cli-container --tail 100
docker exec -it cf-cli-container python cf_cli.py status health

# Solutions
# Check resource limits
docker stats cf-cli-container

# Verify environment variables
docker exec cf-cli-container env | grep CF_

# Test without optimizations
docker run -e CF_CLI_DISABLE_PERF_OPT=1 cf-cli:latest
```

**Symptom:** Permission issues in container
```bash
# Diagnosis
docker exec cf-cli-container id
docker exec cf-cli-container ls -la /app

# Solutions
# Rebuild with correct permissions
docker build --build-arg USER_ID=1000 --build-arg GROUP_ID=1000 .

# Fix runtime permissions
docker exec --user root cf-cli-container chown -R cfuser:cfuser /app
```

### Debugging Tools

#### Debug Mode Configuration
```bash
# Enable debug mode
export CF_DEBUG=true
export CF_LOG_LEVEL=DEBUG
export CF_TRACE_PERFORMANCE=true

# Run with detailed logging
python cf_cli.py --verbose config validate
```

#### Performance Profiling
```python
# tools/debug_profiler.py
import cProfile
import pstats
import io
from contextlib import contextmanager

@contextmanager
def profile_code():
    """Profile code execution"""
    pr = cProfile.Profile()
    pr.enable()
    yield
    pr.disable()

    # Print results
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    print(s.getvalue())

# Usage
with profile_code():
    from cf_cli import main
    main()
```

#### Memory Debugging
```python
# tools/memory_debugger.py
import tracemalloc
import psutil
import os

def start_memory_tracking():
    """Start memory tracking"""
    tracemalloc.start()
    return psutil.Process(os.getpid()).memory_info().rss

def print_memory_diff(baseline):
    """Print memory usage difference"""
    current = psutil.Process(os.getpid()).memory_info().rss
    diff_mb = (current - baseline) / 1024 / 1024

    print(f"Memory usage change: {diff_mb:.2f} MB")

    # Print top memory allocations
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    print("\nTop 10 memory allocations:")
    for stat in top_stats[:10]:
        print(stat)
```

---

## Backup and Recovery

### Configuration Backup Strategy

```bash
#!/bin/bash
# tools/backup_config.sh

# Create backup directory
BACKUP_DIR="/app/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup configuration files
cp -r .env* "$BACKUP_DIR/" 2>/dev/null || true
cp -r config/ "$BACKUP_DIR/" 2>/dev/null || true
cp -r secrets/ "$BACKUP_DIR/" 2>/dev/null || true

# Backup cache state
python cf_cli.py config perf-stats > "$BACKUP_DIR/cache_stats.json"

# Create backup manifest
cat > "$BACKUP_DIR/manifest.json" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "version": "$(python cf_cli.py --version | cut -d' ' -f2)",
  "environment": "${CF_ENVIRONMENT:-unknown}",
  "backup_type": "configuration",
  "files": $(find "$BACKUP_DIR" -type f | wc -l)
}
EOF

echo "Backup created: $BACKUP_DIR"
```

### Recovery Procedures

```bash
#!/bin/bash
# tools/restore_config.sh

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_directory>"
    exit 1
fi

BACKUP_DIR="$1"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "Backup directory not found: $BACKUP_DIR"
    exit 1
fi

# Verify backup integrity
if [ ! -f "$BACKUP_DIR/manifest.json" ]; then
    echo "Invalid backup: manifest.json not found"
    exit 1
fi

# Create backup of current configuration
./tools/backup_config.sh

# Restore configuration files
cp "$BACKUP_DIR/.env"* . 2>/dev/null || true
cp -r "$BACKUP_DIR/config/" . 2>/dev/null || true

# Clear current cache
python cf_cli.py config clear-cache

# Validate restored configuration
if python cf_cli.py config validate; then
    echo "Configuration restored successfully"
else
    echo "Configuration validation failed"
    exit 1
fi
```

### Automated Backup Scheduling

```yaml
# k8s/backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: cf-cli-backup
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: contextforge/cf-cli:v1.0
            command: ["bash", "/app/tools/backup_config.sh"]
            volumeMounts:
            - name: backup-storage
              mountPath: /app/backups
            - name: config
              mountPath: /app/config
              readOnly: true
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          - name: config
            configMap:
              name: cf-cli-config
          restartPolicy: OnFailure
```

---

## Migration Guide

### Version Migration

#### From v1.0 to v1.1
```bash
#!/bin/bash
# tools/migrate_v1.0_to_v1.1.sh

echo "Migrating from v1.0 to v1.1..."

# Backup current configuration
./tools/backup_config.sh

# Update environment variables
if grep -q "CF_CACHE_SIZE" .env*; then
    sed -i 's/CF_CACHE_SIZE/CF_CONFIG_CACHE_SIZE/' .env*
    echo "✓ Updated cache configuration variable names"
fi

# Add new performance settings
if ! grep -q "CF_CLI_ENABLE_PERF_OPT" .env.production; then
    echo "CF_CLI_ENABLE_PERF_OPT=true" >> .env.production
    echo "✓ Added performance optimization flag"
fi

# Clear old cache format
python cf_cli.py config clear-cache

# Validate new configuration
if python cf_cli.py config validate; then
    echo "✓ Migration completed successfully"
else
    echo "✗ Migration failed - check configuration"
    exit 1
fi
```

### Database Schema Migration

```python
# tools/migrate_database.py
from typing import List, Dict
import json
from pathlib import Path

class DatabaseMigrator:
    def __init__(self, db_path: str = "data/cf_cli.db"):
        self.db_path = Path(db_path)
        self.migrations_dir = Path("migrations")

    def get_pending_migrations(self) -> List[str]:
        """Get list of pending migrations"""
        applied = self._get_applied_migrations()
        available = sorted(self.migrations_dir.glob("*.py"))

        return [m.stem for m in available if m.stem not in applied]

    def apply_migration(self, migration_name: str) -> bool:
        """Apply a single migration"""
        migration_file = self.migrations_dir / f"{migration_name}.py"

        if not migration_file.exists():
            raise FileNotFoundError(f"Migration not found: {migration_name}")

        try:
            # Execute migration
            exec(migration_file.read_text())

            # Record as applied
            self._record_migration(migration_name)
            return True

        except Exception as e:
            print(f"Migration failed: {e}")
            return False

    def _get_applied_migrations(self) -> List[str]:
        """Get list of applied migrations"""
        migrations_log = self.db_path.parent / "migrations.log"
        if migrations_log.exists():
            return migrations_log.read_text().strip().split('\n')
        return []

    def _record_migration(self, migration_name: str):
        """Record migration as applied"""
        migrations_log = self.db_path.parent / "migrations.log"
        with open(migrations_log, 'a') as f:
            f.write(f"{migration_name}\n")
```

---

This deployment guide provides comprehensive coverage of production deployment scenarios,
security considerations, performance optimization, monitoring, and troubleshooting.
The guide is designed to be practical and actionable for DevOps teams deploying
the ContextForge CLI in real production environments.
