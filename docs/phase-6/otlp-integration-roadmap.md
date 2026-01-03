# Phase 6: OTLP Integration Roadmap

**Task**: TASK-OBS-002 (OTLP-003)
**Status**: 📋 ROADMAP (Deferred to Phase 6.0)
**Estimated Effort**: 20-30 hours
**Prerequisites**: Phase 5 complete, cf_core production services deployed
**Target Timeline**: Q1 2026

---

## Executive Summary

This document provides the comprehensive roadmap for integrating OpenTelemetry Protocol (OTLP) with cf_core production services. OTLP integration is **intentionally deferred** from Phase 2.2 migration tooling to Phase 6.0 production services observability.

### Key Decision: Why Defer OTLP to Phase 6?

**Rationale** (from observability-design.md § 5.1):
1. **Usage Frequency**: Migration tooling executes <10 times over project lifetime (5 phases × 1-2 executions)
2. **Existing Adequacy**: Structlog JSONL with correlation IDs satisfies QSE evidence requirements
3. **Operational Overhead**: OTLP collector deployment (sidecar/agent), configuration (receivers/exporters/processors), storage (Prometheus/Jaeger/Elasticsearch) is massive overkill for infrequent development operations
4. **Industry Patterns**: OpenTelemetry documentation emphasizes OTLP for **high-frequency production services** (thousands of requests/hour), not migration tooling

**Alternative for Phase 2.2**: PrometheusMetricReader with local HTTP server (port 9464) available as optional enhancement (SHOULD priority, Phase 2.3) if stakeholders require visual dashboards during migration.

---

## Phase 6.0 Scope

### When to Implement
**Trigger**: Phase 5 complete AND cf_core production services deployed (cf_core.services.tasks, projects, sprints)

### What to Instrument
- **Production cf_core services**:
  - `cf_core.services.tasks` - Task CRUD operations
  - `cf_core.services.projects` - Project management
  - `cf_core.services.sprints` - Sprint lifecycle management
  - `cf_core.cli.*` - CLI command invocations (optional)
  - `cf_core.database.repositories` - Database operations (optional)

### Infrastructure Components
1. **OpenTelemetry Collector** - Sidecar (Kubernetes) or agent (VM deployments)
2. **Exporters**:
   - Prometheus (metrics)
   - Jaeger (distributed traces)
   - Elasticsearch (logs - optional, if not using structlog JSONL)
3. **Visualization**:
   - Grafana dashboards for service metrics
   - Jaeger UI for trace exploration

---

## Architecture Design

### Component Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                     cf_core Production Service                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Application Code (cf_core.services.tasks, projects, etc) │   │
│  │                                                            │   │
│  │  OpenTelemetry SDK:                                       │   │
│  │  - TracerProvider (W3C Trace Context)                     │   │
│  │  - MeterProvider (Prometheus metrics)                     │   │
│  │  - LoggerProvider (structured logs - optional)            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           │ OTLP/gRPC or OTLP/HTTP              │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │        OpenTelemetry Collector (Sidecar/Agent)           │   │
│  │                                                            │   │
│  │  Receivers:                                               │   │
│  │  - otlp (gRPC: 4317, HTTP: 4318)                          │   │
│  │                                                            │   │
│  │  Processors:                                              │   │
│  │  - batch (reduce export overhead)                         │   │
│  │  - memory_limiter (prevent OOM)                           │   │
│  │  - attributes (add env, region, cluster labels)           │   │
│  │                                                            │   │
│  │  Exporters:                                               │   │
│  │  - prometheus (metrics → Prometheus TSDB)                 │   │
│  │  - jaeger (traces → Jaeger backend)                       │   │
│  │  - elasticsearch (logs → ELK stack - optional)            │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ Remote Write / gRPC
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Observability Backends                      │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │  Prometheus  │  │    Jaeger    │  │  Elasticsearch/ELK  │   │
│  │     TSDB     │  │   Backend    │  │    (optional)       │   │
│  │              │  │              │  │                     │   │
│  │  - Metrics   │  │  - Traces    │  │  - Logs (JSONL)     │   │
│  │  - Alerts    │  │  - Spans     │  │  - Full-text search │   │
│  └──────────────┘  └──────────────┘  └─────────────────────┘   │
│         │                  │                      │              │
│         └──────────────────┴──────────────────────┘              │
│                            │                                     │
│                            ▼                                     │
│                   ┌────────────────┐                             │
│                   │    Grafana     │                             │
│                   │   Dashboards   │                             │
│                   └────────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
```

### Deployment Patterns

#### Option 1: Kubernetes Sidecar (Recommended for Cloud)
```yaml
# cf-core-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cf-core-tasks-service
spec:
  template:
    spec:
      containers:
      - name: cf-core-service
        image: cf-core:latest
        env:
        - name: OTEL_EXPORTER_OTLP_ENDPOINT
          value: "http://localhost:4318"  # Sidecar on localhost

      - name: otel-collector
        image: otel/opentelemetry-collector-contrib:0.90.0
        args: ["--config=/conf/otel-collector-config.yaml"]
        volumeMounts:
        - name: otel-collector-config
          mountPath: /conf

      volumes:
      - name: otel-collector-config
        configMap:
          name: otel-collector-config
```

#### Option 2: VM Agent (Recommended for On-Prem)
```bash
# Install OpenTelemetry Collector as systemd service
wget https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v0.90.0/otelcol-contrib_0.90.0_linux_amd64.deb
sudo dpkg -i otelcol-contrib_0.90.0_linux_amd64.deb

# Configure
sudo nano /etc/otelcol-contrib/config.yaml

# Start service
sudo systemctl enable otelcol-contrib
sudo systemctl start otelcol-contrib
```

---

## OpenTelemetry Collector Configuration

### Complete YAML Pipeline

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  # Batch events to reduce export overhead
  batch:
    timeout: 10s
    send_batch_size: 1024
    send_batch_max_size: 2048

  # Prevent out-of-memory errors
  memory_limiter:
    check_interval: 1s
    limit_mib: 512
    spike_limit_mib: 128

  # Add environment labels
  attributes:
    actions:
    - key: environment
      value: production
      action: insert
    - key: region
      value: us-east-1
      action: insert
    - key: cluster
      value: cf-core-prod
      action: insert
    - key: service.name
      from_attribute: service.name
      action: upsert

exporters:
  # Prometheus metrics exporter
  prometheus:
    endpoint: "0.0.0.0:9464"
    namespace: cf_core
    const_labels:
      environment: production

  # Jaeger traces exporter
  jaeger:
    endpoint: jaeger-collector:14250
    tls:
      insecure: false

  # Elasticsearch logs exporter (optional)
  elasticsearch:
    endpoints: ["https://elasticsearch:9200"]
    index: cf-core-logs
    auth:
      authenticator: basicauth
    tls:
      insecure: false

service:
  pipelines:
    # Metrics pipeline
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch, attributes]
      exporters: [prometheus]

    # Traces pipeline
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch, attributes]
      exporters: [jaeger]

    # Logs pipeline (optional - use if not relying on structlog JSONL)
    logs:
      receivers: [otlp]
      processors: [memory_limiter, batch, attributes]
      exporters: [elasticsearch]
```

---

## Metrics Taxonomy (13 Metrics)

### Migration Metrics

#### `migration_duration_seconds` (Histogram)
**Description**: Total duration of each migration phase
**Labels**:
- `phase`: Migration phase (phase1, phase2, etc.)
- `status`: success, failed, rolled_back
- `dry_run`: true, false

**Buckets**: [10, 30, 60, 120, 300, 600, 1800, 3600] (seconds)

**Example PromQL**:
```promql
# Average migration duration by phase
rate(migration_duration_seconds_sum[5m]) / rate(migration_duration_seconds_count[5m])

# 95th percentile migration latency
histogram_quantile(0.95, sum(rate(migration_duration_seconds_bucket[5m])) by (le, phase))
```

#### `phase_success_total` (Counter)
**Description**: Total successful phase completions
**Labels**:
- `phase`: Migration phase

#### `phase_failure_total` (Counter)
**Description**: Total failed phase executions
**Labels**:
- `phase`: Migration phase
- `error_type`: validation_failed, db_error, git_error, timeout

### Rollback Metrics

#### `rollback_duration_seconds` (Histogram)
**Description**: Rollback operation latency
**Labels**:
- `phase`: Migration phase being rolled back
- `operation`: git_restore, db_restore, shim_restore

**Buckets**: [5, 15, 30, 60, 90, 150, 250] (seconds)

**SLO**: 99% of rollbacks complete within 180 seconds

#### `rollback_success_total` (Counter)
**Description**: Successful rollback count
**Labels**:
- `phase`: Migration phase

#### `rollback_failure_total` (Counter)
**Description**: Failed rollback count
**Labels**:
- `phase`: Migration phase
- `reason`: git_failed, db_failed, shim_failed, corruption

### Operational Metrics

#### `health_check_latency_milliseconds` (Histogram)
**Description**: Health endpoint response time
**Labels**:
- `endpoint`: /health/live, /health/ready, /health/cf_core/config, etc.
- `check_type`: liveness, readiness, operational

**Buckets**: [1, 5, 10, 50, 100, 500, 1000, 5000] (milliseconds)

**SLO**: 99.9% of liveness checks < 50ms

#### `git_operation_duration_seconds` (Histogram)
**Description**: Git operation latency
**Labels**:
- `operation`: tag, commit, checkout, revert

**Buckets**: [0.1, 0.5, 1, 5, 10, 30, 60] (seconds)

#### `db_snapshot_size_bytes` (Gauge)
**Description**: Database snapshot file size
**Labels**:
- `phase`: Migration phase
- `db_type`: postgresql, sqlite, duckdb

#### `state_file_write_latency_milliseconds` (Histogram)
**Description**: .migration-state.json write latency
**Labels**:
- `phase`: Migration phase

**Buckets**: [1, 5, 10, 50, 100, 500] (milliseconds)

#### `artifacts_modified_total` (Counter)
**Description**: Total artifacts modified during migration
**Labels**:
- `phase`: Migration phase
- `file_type`: py, yaml, json, md

#### `test_coverage_percentage` (Gauge)
**Description**: Test coverage percentage per phase
**Labels**:
- `phase`: Migration phase
- `test_suite`: unit, integration, system

**Target**: ≥95% coverage

---

## Python Implementation

### SDK Initialization

```python
# cf_core/observability/otlp_provider.py
"""
OpenTelemetry SDK initialization for Phase 6 production services.
"""

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def configure_otlp_telemetry(
    service_name: str,
    service_version: str,
    environment: str = "production",
    otlp_endpoint: str = "http://localhost:4318",
) -> None:
    """
    Configure OpenTelemetry SDK with OTLP exporters.

    Args:
        service_name: Service name (e.g., "cf_core.services.tasks")
        service_version: Service version (e.g., "1.0.0")
        environment: Deployment environment (production, staging, dev)
        otlp_endpoint: OTLP collector HTTP endpoint

    Example:
        >>> configure_otlp_telemetry(
        ...     service_name="cf_core.services.tasks",
        ...     service_version="1.0.0",
        ...     environment="production"
        ... )
    """
    # Create resource with service metadata
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": service_version,
            "deployment.environment": environment,
        }
    )

    # Configure TracerProvider for distributed tracing
    trace_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
    trace_provider = TracerProvider(resource=resource)
    trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
    trace.set_tracer_provider(trace_provider)

    # Configure MeterProvider for metrics
    metric_exporter = OTLPMetricExporter(endpoint=otlp_endpoint)
    metric_reader = PeriodicExportingMetricReader(
        exporter=metric_exporter,
        export_interval_millis=60000,  # 1 minute
    )
    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[metric_reader],
    )
    metrics.set_meter_provider(meter_provider)


# Get global tracer and meter
def get_tracer(name: str):
    """Get tracer for instrumentation."""
    return trace.get_tracer(name)


def get_meter(name: str):
    """Get meter for metrics."""
    return metrics.get_meter(name)
```

### Service Instrumentation Example

```python
# cf_core/services/tasks.py (Phase 6 version with OTLP)
"""
Task service with OpenTelemetry instrumentation.
"""

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from cf_core.database.task_repository import TaskRepository
from cf_core.models.task import Task
from cf_core.observability.otlp_provider import get_meter, get_tracer

tracer = get_tracer(__name__)
meter = get_meter(__name__)

# Define metrics
task_create_duration = meter.create_histogram(
    name="task_create_duration_seconds",
    description="Task creation latency",
    unit="s",
)

task_create_total = meter.create_counter(
    name="task_create_total",
    description="Total tasks created",
)


class TaskService:
    """Task business logic service with OTLP instrumentation."""

    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def create(self, title: str, **kwargs) -> Task:
        """
        Create new task with validation, logging, and distributed tracing.
        """
        # Start distributed trace span
        with tracer.start_as_current_span(
            "task.create",
            attributes={
                "task.title": title,
                "task.priority": kwargs.get("priority", "medium"),
            },
        ) as span:
            import time

            start_time = time.time()

            try:
                # Validation
                if not title or len(title) < 3:
                    span.set_status(Status(StatusCode.ERROR, "Title too short"))
                    span.record_exception(ValueError("Title must be ≥3 characters"))
                    raise ValueError("Task title must be at least 3 characters")

                # Create task
                task = Task(
                    id=self._generate_id(),
                    title=title,
                    status="todo",
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                    **kwargs,
                )

                # Persist
                task = self.repository.create(task)

                # Record success metrics
                duration = time.time() - start_time
                task_create_duration.record(duration, {"status": "success"})
                task_create_total.add(1, {"status": "success"})

                # Add span attributes
                span.set_attribute("task.id", task.id)
                span.set_attribute("task.status", task.status)
                span.set_status(Status(StatusCode.OK))

                return task

            except Exception as e:
                # Record failure metrics
                duration = time.time() - start_time
                task_create_duration.record(duration, {"status": "error"})
                task_create_total.add(1, {"status": "error"})

                # Record exception in span
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
```

---

## W3C Trace Context Propagation

### Cross-Service Tracing

```python
# cf_core/services/projects.py
"""
Project service with cross-service trace propagation.
"""

from opentelemetry import trace
from opentelemetry.propagate import inject
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

tracer = get_tracer(__name__)


class ProjectService:
    """Project service that calls TaskService."""

    def __init__(self, task_service: TaskService):
        self.task_service = task_service

    def create_project_with_tasks(self, project_name: str, task_titles: list[str]):
        """Create project and associated tasks with distributed tracing."""
        with tracer.start_as_current_span("project.create_with_tasks") as span:
            span.set_attribute("project.name", project_name)
            span.set_attribute("project.task_count", len(task_titles))

            # Create project
            project = self._create_project(project_name)

            # Create tasks (child spans)
            for title in task_titles:
                # W3C Trace Context automatically propagates to child spans
                task = self.task_service.create(
                    title=title, project_id=project.id
                )

            return project
```

### HTTP Header Propagation

```python
# cf_core/cli/task_commands.py
"""
CLI commands with W3C Trace Context HTTP propagation.
"""

import httpx
from opentelemetry.propagate import inject

tracer = get_tracer(__name__)


@app.command()
def create(title: str):
    """Create task via HTTP API with trace propagation."""
    with tracer.start_as_current_span("cli.task.create") as span:
        # Prepare HTTP headers with W3C Trace Context
        headers = {}
        inject(headers)  # Injects traceparent, tracestate headers

        # Make HTTP request to cf_core API
        response = httpx.post(
            "https://cf-core-api/tasks",
            json={"title": title},
            headers=headers,  # Propagate trace context
        )

        span.set_attribute("http.status_code", response.status_code)
        return response.json()
```

---

## Grafana Dashboard Templates

### Dashboard 1: Migration Overview

```json
{
  "dashboard": {
    "title": "CF Core Migration Overview",
    "panels": [
      {
        "title": "Phase Success Rate",
        "targets": [
          {
            "expr": "sum(rate(phase_success_total[5m])) / (sum(rate(phase_success_total[5m])) + sum(rate(phase_failure_total[5m])))"
          }
        ],
        "type": "gauge"
      },
      {
        "title": "Migration Duration by Phase",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(migration_duration_seconds_bucket[5m])) by (le, phase))"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Rollback Latency (99th Percentile)",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, sum(rate(rollback_duration_seconds_bucket[5m])) by (le, operation))"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
```

### Dashboard 2: Service Health

```json
{
  "dashboard": {
    "title": "CF Core Service Health",
    "panels": [
      {
        "title": "Health Check Latency (P95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(health_check_latency_milliseconds_bucket[5m])) by (le, endpoint))"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Test Coverage by Phase",
        "targets": [
          {
            "expr": "test_coverage_percentage"
          }
        ],
        "type": "table"
      }
    ]
  }
}
```

---

## Implementation Checklist

### Prerequisites (Before Phase 6)
- [ ] Phase 5 complete (all migration phases validated)
- [ ] cf_core production services deployed
- [ ] Prometheus instance available
- [ ] Jaeger backend available (or use Jaeger all-in-one)
- [ ] Grafana instance available

### Phase 6.0 Tasks (20-30 hours)

#### Week 1: Collector Setup (8-12 hours)
- [ ] Deploy OpenTelemetry Collector (Kubernetes sidecar OR VM agent)
- [ ] Configure `otel-collector-config.yaml` with receivers, processors, exporters
- [ ] Test collector connectivity (gRPC 4317, HTTP 4318)
- [ ] Validate Prometheus exporter (http://localhost:9464/metrics)
- [ ] Validate Jaeger exporter (check Jaeger UI)

#### Week 2: SDK Integration (8-12 hours)
- [ ] Create `cf_core/observability/otlp_provider.py`
- [ ] Instrument `cf_core.services.tasks` with spans and metrics
- [ ] Instrument `cf_core.services.projects` with W3C Trace Context
- [ ] Instrument `cf_core.services.sprints`
- [ ] Add unit tests for instrumentation

#### Week 3: Dashboards & Validation (4-6 hours)
- [ ] Create Grafana dashboard "CF Core Migration Overview"
- [ ] Create Grafana dashboard "CF Core Service Health"
- [ ] Configure Prometheus alerting rules (SLO violations)
- [ ] Load test instrumented services (validate metric cardinality)
- [ ] Document OTLP integration in README

---

## Cost Estimates

### Infrastructure Costs (Monthly)

| Component | Resource | Cost |
|-----------|----------|------|
| **OpenTelemetry Collector** | 1 vCPU, 512 MB RAM | $10 |
| **Prometheus TSDB** | 10 GB storage, 30-day retention | $15 |
| **Jaeger Backend** | 2 vCPU, 2 GB RAM, 30-day retention | $30 |
| **Grafana** | Managed service (optional) | $20 |
| **Total** | | **$75/month** |

### Data Volume Estimates

| Metric | Volume | Notes |
|--------|--------|-------|
| **Metrics cardinality** | ~500 unique time series | 13 metrics × ~40 label combinations |
| **Trace volume** | ~1,000 spans/hour | cf_core production workload estimate |
| **Storage (Prometheus)** | ~5 GB/month | 1-year retention with 1-minute scrape interval |
| **Storage (Jaeger)** | ~8 GB/month | 30-day retention |

---

## Success Criteria

### Must-Have (Phase 6.0)
- [ ] OpenTelemetry Collector deployed and operational
- [ ] Prometheus receiving metrics from collector
- [ ] Jaeger receiving traces from collector
- [ ] Grafana dashboards rendering migration + service metrics
- [ ] W3C Trace Context propagation validated across services
- [ ] Documentation complete (README, runbook, troubleshooting)

### Should-Have
- [ ] Alerting rules configured (Prometheus Alertmanager)
- [ ] SLO dashboards created (migration duration, rollback latency)
- [ ] Cardinality control validated (<1000 unique time series)
- [ ] Cost monitoring dashboard (Grafana billing panel)

### Could-Have (Future)
- [ ] Elasticsearch log integration (if replacing structlog JSONL)
- [ ] Multi-tenant labeling (team, project, environment)
- [ ] Exemplar sampling for high-cardinality dimensions
- [ ] OpenTelemetry Operator (Kubernetes auto-instrumentation)

---

## References

### OpenTelemetry Documentation
- [OpenTelemetry Python SDK](https://opentelemetry.io/docs/instrumentation/python/)
- [OTLP Exporter Configuration](https://opentelemetry.io/docs/reference/specification/protocol/exporter/)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)

### Collector Configuration
- [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/)
- [Collector Configuration Reference](https://opentelemetry.io/docs/collector/configuration/)

### Observability Backends
- [Prometheus](https://prometheus.io/docs/introduction/overview/)
- [Jaeger](https://www.jaegertracing.io/docs/1.50/)
- [Grafana Dashboards](https://grafana.com/docs/grafana/latest/dashboards/)

### Related Documents
- [observability-design.md](../phase-2-2/task-13/observability-design.md) - Phase 2.2 observability design
- [CF-CORE-MIGRATION-PROJECT-PLAN.md](../../CF-CORE-MIGRATION-PROJECT-PLAN.md) - Overall migration roadmap

---

**Document Version**: 1.0.0
**Status**: 📋 ROADMAP (Phase 6.0 deferred)
**Last Updated**: 2025-11-03
**Next Review**: Upon Phase 5 completion
