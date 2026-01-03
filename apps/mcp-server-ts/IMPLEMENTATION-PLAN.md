# TaskMan MCP Server - Complete Implementation Plan
## Research → Implementation → Testing → Validation

**Created**: January 5, 2025
**Target Duration**: 4 weeks (80-100 hours)
**Methodology**: Iterative delivery with validation gates

---

## Overview

This plan provides a comprehensive, step-by-step approach to implementing all 22 stability improvements identified in the research report. Each improvement follows a four-stage cycle:

1. **Research** - Understand requirements, investigate solutions, make design decisions
2. **Implementation** - Write code, integrate with existing system
3. **Testing** - Unit tests, integration tests, manual verification
4. **Validation** - Performance benchmarks, acceptance criteria, sign-off

---

## Phase 1: Operational Stability (Week 1)
**Goal**: Production-ready server lifecycle management
**Duration**: 13-18 hours
**Dependencies**: None (foundational work)

### 1.1 Graceful Shutdown System

#### Research Phase (30 minutes)
**Objectives**:
- Study Node.js signal handling (SIGINT, SIGTERM, SIGHUP)
- Review MCP SDK cleanup requirements
- Research timeout strategies for graceful shutdown

**Tasks**:
- [ ] Read Node.js process documentation on signal handling
- [ ] Review @modelcontextprotocol/sdk server.close() behavior
- [ ] Research industry standard shutdown timeouts (typical: 30s)
- [ ] Document shutdown sequence requirements

**Research Questions**:
1. Does the MCP SDK require explicit cleanup?
2. What resources need cleanup (HTTP servers, file handles, timers)?
3. How do we handle in-flight requests during shutdown?

**Deliverables**:
- `docs/research/shutdown-design.md` with design decisions
- Sequence diagram of shutdown flow

---

#### Implementation Phase (90 minutes)
**Objectives**:
- Create shutdown service with resource registry
- Add signal handlers to index.ts
- Register all cleanup handlers

**Tasks**:
- [ ] Create `src/infrastructure/shutdown.ts`
  - ShutdownService class with resource registry
  - registerResource() method
  - shutdown() method with timeout protection
  - Idempotency guarantee (safe to call multiple times)

- [ ] Update `src/index.ts`
  - Import shutdownService
  - Register MCP server for cleanup
  - Register HTTP server (if applicable)
  - Add SIGINT handler
  - Add SIGTERM handler
  - Add uncaughtException handler
  - Add unhandledRejection handler

- [ ] Create `src/infrastructure/shutdown.test.ts`
  - Unit tests for ShutdownService
  - Mock resource cleanup scenarios

**Code Checklist**:
- [ ] Shutdown executes in reverse registration order
- [ ] Individual cleanup failures don't block others
- [ ] 30-second timeout protection implemented
- [ ] Logging at each shutdown stage
- [ ] Idempotent (handles multiple shutdown calls)

**Deliverables**:
- `src/infrastructure/shutdown.ts` (120 lines)
- Updated `src/index.ts` with signal handlers
- Unit tests with 100% coverage of shutdown logic

---

#### Testing Phase (45 minutes)
**Objectives**:
- Verify graceful shutdown under various scenarios
- Test timeout protection
- Validate idempotency

**Test Scenarios**:
1. **Normal Shutdown**: SIGINT → clean exit
2. **Slow Cleanup**: Resource takes 20s → completes successfully
3. **Hung Cleanup**: Resource takes 40s → timeout triggers at 30s
4. **Multiple Signals**: SIGINT followed by SIGTERM → idempotent
5. **Uncaught Exception**: Throw error → triggers shutdown → exits
6. **Unhandled Rejection**: Promise rejection → triggers shutdown

**Tasks**:
- [ ] Write integration test: `__tests__/shutdown.integration.test.ts`
- [ ] Test normal shutdown flow
- [ ] Test timeout protection
- [ ] Test idempotency with multiple signals
- [ ] Test error scenarios (uncaughtException, unhandledRejection)
- [ ] Manual test: Start server, send SIGINT, verify clean exit

**Validation Commands**:
```bash
# Unit tests
npm test src/infrastructure/shutdown.test.ts

# Integration tests
npm test __tests__/shutdown.integration.test.ts

# Manual test
npm run dev &
PID=$!
sleep 2
kill -SIGINT $PID
# Should see "Shutdown complete" message
```

**Deliverables**:
- Integration test suite with 6 scenarios
- Manual test results documented
- Test coverage report >95%

---

#### Validation Phase (30 minutes)
**Objectives**:
- Confirm acceptance criteria met
- Performance benchmarks
- Documentation complete

**Acceptance Criteria**:
- [ ] Server responds to SIGINT within 2 seconds
- [ ] Server responds to SIGTERM within 2 seconds
- [ ] Timeout protection triggers at 30 seconds
- [ ] No orphaned processes after shutdown
- [ ] All resources cleaned up (verified via logs)
- [ ] Uncaught exceptions trigger graceful shutdown

**Performance Benchmarks**:
- Normal shutdown latency: <2 seconds
- Timeout protection accuracy: ±1 second
- Memory leaks: 0 (verified with `node --expose-gc`)

**Tasks**:
- [ ] Run shutdown latency benchmark (10 iterations)
- [ ] Run memory leak detection test
- [ ] Verify resource cleanup with lsof (Linux/Mac) or handle.exe (Windows)
- [ ] Document results in validation report

**Deliverables**:
- `docs/validation/1.1-shutdown-validation.md`
- Performance benchmark results
- Sign-off: ✅ Ready for production

---

### 1.2 Structured Logging with Pino

#### Research Phase (45 minutes)
**Objectives**:
- Evaluate Pino vs Winston vs Bunyan
- Design log schema and standards
- Plan migration from console.log

**Tasks**:
- [ ] Compare logging libraries (performance, features, ecosystem)
- [ ] Research structured logging best practices
- [ ] Design log schema (service, level, timestamp, message, context)
- [ ] Identify sensitive fields to redact
- [ ] Plan console.log → logger migration strategy

**Research Questions**:
1. Pino vs Winston performance comparison?
2. What log levels to support? (trace, debug, info, warn, error, fatal)
3. JSON logs in production, pretty logs in development?
4. How to handle correlation IDs?
5. What fields to redact for security?

**Deliverables**:
- `docs/research/logging-design.md`
- Log schema specification
- Migration checklist

---

#### Implementation Phase (4 hours)
**Objectives**:
- Install and configure Pino
- Create logger infrastructure
- Migrate all console.log calls
- Add correlation ID support

**Tasks**:
- [ ] Install dependencies
  ```bash
  npm install pino pino-pretty
  npm install -D @types/pino
  ```

- [ ] Create `src/infrastructure/logger.ts`
  - Configure Pino with environment-based settings
  - Pretty printing for development
  - JSON output for production
  - Redaction rules for sensitive data
  - createContextLogger() helper
  - withCorrelationLogger() helper

- [ ] Update `src/infrastructure/audit.ts`
  - Replace console.log with logger.info()
  - Add structured context to log entries

- [ ] Update `src/backend/client.ts`
  - Replace console.log in interceptors
  - Add structured logging for requests/responses
  - Log errors with stack traces

- [ ] Update `src/features/*/register.ts`
  - Replace any console.log calls
  - Add context-aware logging

- [ ] Update `src/index.ts`
  - Use logger for startup messages
  - Log configuration on boot

**Migration Pattern**:
```typescript
// BEFORE
console.log('Task created:', taskId);
console.error('Error creating task:', error);

// AFTER
logger.info({ taskId }, 'Task created');
logger.error({ error: error.message, stack: error.stack }, 'Error creating task');
```

**Code Checklist**:
- [ ] All console.log replaced with logger.*
- [ ] All console.error replaced with logger.error()
- [ ] Sensitive fields redacted (passwords, tokens)
- [ ] Log levels appropriate (debug vs info vs warn vs error)
- [ ] Structured context included (ids, durations, counts)
- [ ] Correlation IDs tracked across operations

**Deliverables**:
- `src/infrastructure/logger.ts` (150 lines)
- Zero console.log calls in codebase (verified via grep)
- Migration complete across all modules

---

#### Testing Phase (90 minutes)
**Objectives**:
- Verify log output format
- Test redaction rules
- Validate log levels
- Test correlation ID propagation

**Test Scenarios**:
1. **Development Mode**: Pretty printed logs with colors
2. **Production Mode**: JSON structured logs
3. **Redaction**: Passwords/tokens are [REDACTED]
4. **Log Levels**: trace < debug < info < warn < error < fatal
5. **Correlation IDs**: Tracked across async operations
6. **Performance**: Logging doesn't slow down operations >5%

**Tasks**:
- [ ] Write unit tests: `src/infrastructure/logger.test.ts`
- [ ] Test log level filtering
- [ ] Test redaction rules
- [ ] Test correlation ID propagation
- [ ] Test child logger creation
- [ ] Performance benchmark (1000 log calls < 50ms)
- [ ] Manual test: Run server, verify log format

**Validation Commands**:
```bash
# Development logs (pretty)
NODE_ENV=development npm run dev

# Production logs (JSON)
NODE_ENV=production npm start

# Test redaction
LOG_LEVEL=debug npm test src/infrastructure/logger.test.ts

# Performance benchmark
npm run benchmark:logging
```

**Deliverables**:
- Unit tests with >90% coverage
- Performance benchmark results
- Log format examples documented

---

#### Validation Phase (30 minutes)
**Objectives**:
- Confirm log aggregation compatibility
- Verify no sensitive data leaks
- Performance validation

**Acceptance Criteria**:
- [ ] All logs are valid JSON in production mode
- [ ] Sensitive fields successfully redacted
- [ ] Log level filtering works correctly
- [ ] Correlation IDs present in all async operations
- [ ] No console.log calls remain in codebase
- [ ] Logging overhead <5% of request latency

**Integration Tests**:
- [ ] Send logs to local ELK/Splunk instance (if available)
- [ ] Verify logs are searchable and parseable
- [ ] Test log aggregation queries

**Tasks**:
- [ ] Grep codebase: `grep -r "console\\.log" src/` (should be empty)
- [ ] Run security audit: Check for leaked credentials in logs
- [ ] Performance comparison: Before/after logging migration
- [ ] Document log schema for operations team

**Deliverables**:
- `docs/validation/1.2-logging-validation.md`
- Log schema documentation
- Sign-off: ✅ Ready for production

---

### 1.3 Health Check Endpoints

#### Research Phase (30 minutes)
**Objectives**:
- Study Kubernetes health probe patterns
- Design health check endpoints
- Define health check logic

**Tasks**:
- [ ] Research K8s liveness vs readiness vs startup probes
- [ ] Study health check best practices (Google SRE book)
- [ ] Define health check criteria
- [ ] Design /health/* endpoint structure

**Research Questions**:
1. What's the difference between liveness and readiness?
2. What should we check for readiness? (backend connectivity, dependencies)
3. What timeout values are appropriate?
4. Should health checks be authenticated?

**Deliverables**:
- `docs/research/health-checks-design.md`
- Health check specification
- Endpoint design

---

#### Implementation Phase (3 hours)
**Objectives**:
- Create health check service
- Implement liveness probe
- Implement readiness probe
- Implement startup probe
- Add HTTP endpoints

**Tasks**:
- [ ] Create `src/infrastructure/health.ts`
  - HealthCheckService class
  - checkLiveness() method (basic process health)
  - checkReadiness() method (dependencies ready)
  - checkStartup() method (initialization complete)
  - markStartupComplete() method
  - Health status aggregation logic

- [ ] Update `src/transports/http.ts`
  - Add GET /health/live endpoint
  - Add GET /health/ready endpoint
  - Add GET /health/startup endpoint
  - Return proper HTTP status codes (200=ok, 503=down)

- [ ] Update `src/index.ts`
  - Call healthCheckService.markStartupComplete() after bootstrap
  - Add health check to shutdown sequence

- [ ] Create health check for backend
  - Periodic backend connectivity check
  - Track backend health status
  - Include in readiness check

**Health Check Logic**:
```typescript
Liveness:
  - Process is running (always true if endpoint responds)
  - Memory usage < 90%
  - CPU not pegged

Readiness:
  - Startup complete: true
  - Backend connectivity: successful within 1 second
  - No circuit breakers open

Startup:
  - Initialization complete flag set
```

**Code Checklist**:
- [ ] Health endpoints return proper status codes
- [ ] Health checks have reasonable timeouts
- [ ] Health response includes detailed status
- [ ] Backend connectivity tested without errors
- [ ] Startup completion tracked

**Deliverables**:
- `src/infrastructure/health.ts` (200 lines)
- Updated `src/transports/http.ts` with endpoints
- Health check logic implemented

---

#### Testing Phase (60 minutes)
**Objectives**:
- Test all health endpoints
- Verify status codes
- Test degraded states
- Load test health endpoints

**Test Scenarios**:
1. **Healthy State**: All checks pass → 200 OK
2. **Startup Pending**: Startup incomplete → 503
3. **Backend Down**: Backend unreachable → 503 (readiness)
4. **Degraded State**: Slow backend → 200 but status=degraded
5. **Memory Pressure**: High memory → warning in liveness
6. **Load Test**: 100 req/s to /health/live → <10ms p99

**Tasks**:
- [ ] Write integration tests: `__tests__/health.integration.test.ts`
- [ ] Test liveness endpoint
- [ ] Test readiness endpoint
- [ ] Test startup endpoint
- [ ] Test backend down scenario
- [ ] Load test health endpoints (autocannon)
- [ ] Manual test: curl endpoints

**Validation Commands**:
```bash
# Integration tests
npm test __tests__/health.integration.test.ts

# Manual tests
curl http://localhost:3000/health/live
curl http://localhost:3000/health/ready
curl http://localhost:3000/health/startup

# Load test
npx autocannon -c 100 -d 10 http://localhost:3000/health/live
```

**Deliverables**:
- Integration tests covering all scenarios
- Load test results (should handle 100+ req/s)
- Manual test documentation

---

#### Validation Phase (30 minutes)
**Objectives**:
- Kubernetes integration test
- Verify probe behavior
- Performance validation

**Acceptance Criteria**:
- [ ] /health/live responds in <50ms (p99)
- [ ] /health/ready accurately reflects backend status
- [ ] /health/startup correctly tracks initialization
- [ ] Kubernetes probes work correctly
- [ ] No false positives (probe kills healthy pod)
- [ ] No false negatives (probe misses unhealthy pod)

**Kubernetes Validation**:
- [ ] Deploy to K8s with probes configured
- [ ] Verify liveness probe restarts on failure
- [ ] Verify readiness probe removes from service on failure
- [ ] Verify startup probe delays liveness/readiness checks

**Tasks**:
- [ ] Create K8s manifest with probe configuration
- [ ] Deploy test pod to K8s cluster
- [ ] Simulate backend failure → verify readiness fails
- [ ] Simulate crash → verify liveness restarts pod
- [ ] Document probe configuration

**Deliverables**:
- `k8s/deployment.yaml` with probe configuration
- `docs/validation/1.3-health-validation.md`
- Sign-off: ✅ Ready for production

---

### 1.4 Configuration Management

#### Research Phase (45 minutes)
**Objectives**:
- Design comprehensive configuration schema
- Plan environment variable structure
- Research validation approaches

**Tasks**:
- [ ] List all configuration needs (35+ variables identified)
- [ ] Design configuration schema with Joi
- [ ] Plan .env file structure
- [ ] Research configuration best practices (12-factor app)
- [ ] Design validation error messages

**Configuration Categories**:
1. Server (port, transport, environment)
2. Backend (endpoint, timeout, retries)
3. Logging (level, format)
4. Persistence (type, paths, URLs)
5. Locks (timeout, cleanup interval)
6. Health (enabled, check intervals)
7. Observability (metrics, tracing)
8. Debug (flags, verbosity)

**Deliverables**:
- `docs/research/configuration-design.md`
- Configuration schema specification
- .env file template

---

#### Implementation Phase (2.5 hours)
**Objectives**:
- Create configuration schema
- Implement validation
- Update config loading
- Create .env templates

**Tasks**:
- [ ] Install dependencies
  ```bash
  npm install joi dotenv
  npm install -D @types/joi
  ```

- [ ] Create `src/config/schema.ts`
  - Define Joi schema for all configuration
  - Add validation rules (types, ranges, formats)
  - Define defaults for each variable
  - Add helpful error messages

- [ ] Update `src/config/index.ts`
  - Load .env file with dotenv
  - Validate against schema
  - Export typed configuration object
  - Log configuration (redacted) on startup

- [ ] Create `.env.example` template
  - Document all available variables
  - Provide example values
  - Include comments explaining each variable

- [ ] Create `.env.development` template
- [ ] Create `.env.production` template
- [ ] Create `.env.test` template

- [ ] Update `README.md` with configuration documentation

**Configuration Variables** (35 total):
```typescript
// Server
NODE_ENV, PORT, TASKMAN_MCP_TRANSPORT

// Backend
TASK_MANAGER_API_ENDPOINT, BACKEND_TIMEOUT_MS,
BACKEND_MAX_RETRIES, BACKEND_RETRY_DELAY_MS

// Logging
LOG_LEVEL, LOG_FORMAT

// Persistence
ENABLE_PERSISTENCE, PERSISTENCE_TYPE,
SQLITE_DB_PATH, REDIS_URL

// Locks
LOCK_TIMEOUT_MS, LOCK_CLEANUP_INTERVAL_MS

// Health
HEALTH_CHECK_ENABLED, BACKEND_HEALTH_CHECK_INTERVAL_MS

// Observability
ENABLE_METRICS, ENABLE_TRACING, OTEL_EXPORTER_OTLP_ENDPOINT

// Debug
TASKMAN_DEBUG

// (+ more as identified)
```

**Code Checklist**:
- [ ] All configuration validated at startup
- [ ] Helpful error messages on validation failure
- [ ] Defaults provided for optional variables
- [ ] Type-safe configuration object exported
- [ ] Sensitive values redacted in logs
- [ ] .env.example documented

**Deliverables**:
- `src/config/schema.ts` (300 lines)
- Updated `src/config/index.ts`
- `.env.example` with documentation
- Configuration documentation in README

---

#### Testing Phase (60 minutes)
**Objectives**:
- Test validation rules
- Test defaults
- Test error handling
- Test environment override

**Test Scenarios**:
1. **Valid Config**: All variables valid → loads successfully
2. **Missing Required**: PORT missing → validation error
3. **Invalid Type**: PORT='abc' → validation error
4. **Out of Range**: PORT=99999 → validation error
5. **Defaults Applied**: LOG_LEVEL unset → defaults to 'info'
6. **Environment Override**: Dev vs prod vs test configs

**Tasks**:
- [ ] Write unit tests: `src/config/schema.test.ts`
- [ ] Test validation rules for each variable
- [ ] Test default values
- [ ] Test error messages
- [ ] Test environment-specific configs
- [ ] Manual test: Start server with various configs

**Validation Commands**:
```bash
# Unit tests
npm test src/config/schema.test.ts

# Test validation errors
PORT=invalid npm start  # Should fail with clear error

# Test defaults
unset LOG_LEVEL && npm start  # Should default to 'info'

# Test environments
NODE_ENV=development npm start
NODE_ENV=production npm start
NODE_ENV=test npm test
```

**Deliverables**:
- Unit tests with 100% coverage of schema
- Error message examples documented
- Environment-specific test results

---

#### Validation Phase (30 minutes)
**Objectives**:
- Verify all configurations work
- Test portability across environments
- Documentation review

**Acceptance Criteria**:
- [ ] All 35+ configuration variables validated
- [ ] Validation catches type errors
- [ ] Validation catches range errors
- [ ] Defaults work correctly
- [ ] .env.example is accurate and complete
- [ ] Configuration loads in <100ms
- [ ] Error messages are helpful

**Portability Tests**:
- [ ] Dev environment: Loads successfully
- [ ] Test environment: Loads successfully
- [ ] Production environment: Loads successfully
- [ ] Docker container: Loads successfully

**Tasks**:
- [ ] Review .env.example completeness
- [ ] Test startup with each environment config
- [ ] Verify configuration documentation accuracy
- [ ] Benchmark configuration load time

**Deliverables**:
- `docs/validation/1.4-config-validation.md`
- Configuration guide for operations
- Sign-off: ✅ Ready for production

---

## Phase 1 Completion Checklist

**Before proceeding to Phase 2**:
- [ ] All Phase 1 implementations complete
- [ ] All Phase 1 tests passing
- [ ] All Phase 1 validations signed off
- [ ] Integration test: Full startup/shutdown cycle works
- [ ] Manual test: Deploy to staging environment
- [ ] Documentation: Phase 1 features documented
- [ ] Performance: No regression in latency/throughput
- [ ] Code review: Peer review completed
- [ ] Git: All changes committed with meaningful messages

**Phase 1 Deliverables**:
1. Graceful shutdown system (working)
2. Structured logging (100% migrated)
3. Health check endpoints (K8s-ready)
4. Configuration management (35+ variables)
5. Test coverage >85%
6. Documentation complete
7. Validation reports for all features

**Phase 1 Success Metrics**:
- ✅ Server can be stopped gracefully
- ✅ All logs are structured and aggregatable
- ✅ Kubernetes probes working
- ✅ Configuration flexible and validated
- ✅ Zero production incidents during Phase 1 deployment

---

## Phase 2: Observability (Week 2)
**Goal**: Full visibility into system behavior
**Duration**: 11-15 hours
**Dependencies**: Phase 1 (logging must be complete)

### 2.1 Prometheus Metrics

#### Research Phase (60 minutes)
**Objectives**:
- Study Prometheus best practices
- Design metric schema
- Identify instrumentation points

**Tasks**:
- [ ] Research Prometheus metric types (Counter, Gauge, Histogram, Summary)
- [ ] Study metric naming conventions
- [ ] Design metric labels (avoid high cardinality)
- [ ] Identify key metrics to instrument
- [ ] Research Grafana dashboard patterns

**Metrics Design**:
```
MCP Tool Metrics:
- mcp_tool_invocations_total (counter)
- mcp_tool_duration_seconds (histogram)
- mcp_tool_errors_total (counter)

Backend API Metrics:
- backend_requests_total (counter)
- backend_request_duration_seconds (histogram)
- backend_retries_total (counter)
- backend_circuit_breaker_state (gauge)

Infrastructure Metrics:
- active_locks_total (gauge)
- lock_wait_time_seconds (histogram)
- audit_buffer_size (gauge)
- audit_entries_total (counter)

System Metrics:
- process_cpu_usage (gauge)
- process_memory_bytes (gauge)
- process_uptime_seconds (gauge)
```

**Research Questions**:
1. What histogram buckets to use for latency? (.01, .05, .1, .5, 1, 2, 5)
2. What labels to add? (tool_name, status, method, endpoint)
3. How to avoid label cardinality explosion?
4. Default metrics from prom-client?

**Deliverables**:
- `docs/research/metrics-design.md`
- Metric specification document
- Label design guidelines

---

#### Implementation Phase (5 hours)
**Objectives**:
- Install prom-client
- Create metrics infrastructure
- Instrument all tool invocations
- Instrument backend client
- Create /metrics endpoint

**Tasks**:
- [ ] Install dependencies
  ```bash
  npm install prom-client
  ```

- [ ] Create `src/infrastructure/metrics.ts`
  - Initialize Prometheus registry
  - Define all metrics (15+ metrics)
  - Export metrics for use in other modules
  - Create metrics HTTP endpoint handler

- [ ] Instrument `src/features/tasks/register.ts`
  - Add timer for each tool invocation
  - Increment counter on invocation
  - Increment error counter on failures
  - Track tool-specific metrics

- [ ] Instrument `src/features/projects/register.ts`
  - Same as tasks (DRY: extract helper)

- [ ] Instrument `src/features/action-lists/register.ts`
  - Same as tasks

- [ ] Instrument `src/backend/client.ts`
  - Track request counts by method/endpoint
  - Track request latency by endpoint
  - Track retry counts
  - Track circuit breaker state

- [ ] Instrument `src/infrastructure/locking.ts`
  - Track active locks by object type
  - Track lock acquisition time
  - Track lock wait time

- [ ] Instrument `src/infrastructure/audit.ts`
  - Track audit buffer size
  - Track audit entries written

- [ ] Update `src/transports/http.ts`
  - Add GET /metrics endpoint
  - Serve Prometheus-formatted metrics

- [ ] Create metrics helper: `src/infrastructure/metrics-helper.ts`
  - instrumentTool() wrapper for consistent instrumentation
  - instrumentBackendCall() wrapper

**Instrumentation Pattern**:
```typescript
// Tool instrumentation
const timer = toolLatency.startTimer({ tool_name: "task_create" });
try {
  const result = await operation();
  toolInvocations.inc({ tool_name: "task_create", status: "success" });
  return result;
} catch (error) {
  toolInvocations.inc({ tool_name: "task_create", status: "error" });
  throw error;
} finally {
  timer();
}
```

**Code Checklist**:
- [ ] All MCP tools instrumented
- [ ] All backend calls instrumented
- [ ] Infrastructure components instrumented
- [ ] /metrics endpoint responds correctly
- [ ] Metrics follow Prometheus naming conventions
- [ ] Labels avoid high cardinality

**Deliverables**:
- `src/infrastructure/metrics.ts` (300 lines)
- `src/infrastructure/metrics-helper.ts` (100 lines)
- All features instrumented
- /metrics endpoint working

---

#### Testing Phase (90 minutes)
**Objectives**:
- Verify metrics are recorded
- Test metric accuracy
- Load test metrics endpoint
- Validate Prometheus scraping

**Test Scenarios**:
1. **Tool Invocation**: Call task_create → counter increments
2. **Tool Latency**: Measure duration → histogram records
3. **Tool Error**: Cause failure → error counter increments
4. **Backend Call**: API request → backend metrics update
5. **Lock Metrics**: Acquire lock → gauge increases
6. **Metrics Endpoint**: GET /metrics → valid Prometheus format
7. **Load Test**: 1000 requests → metrics accurate

**Tasks**:
- [ ] Write integration tests: `__tests__/metrics.integration.test.ts`
- [ ] Test metric recording for each tool
- [ ] Test metric endpoint response
- [ ] Validate Prometheus text format
- [ ] Load test: Generate 1000 operations, verify metrics
- [ ] Manual test: Scrape with Prometheus

**Validation Commands**:
```bash
# Integration tests
npm test __tests__/metrics.integration.test.ts

# Manual test
curl http://localhost:3000/metrics

# Load test
npm run load-test:tools

# Prometheus scrape test
docker run -p 9090:9090 -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus
```

**Prometheus Config**:
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'taskman-mcp'
    static_configs:
      - targets: ['host.docker.internal:3000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

**Deliverables**:
- Integration tests with metric verification
- Prometheus scrape config
- Load test results (metrics accurate under load)

---

#### Validation Phase (45 minutes)
**Objectives**:
- Create Grafana dashboards
- Verify metric utility
- Performance validation

**Acceptance Criteria**:
- [ ] All 15+ metrics recorded correctly
- [ ] /metrics endpoint responds in <100ms
- [ ] Metrics don't impact tool latency >2%
- [ ] Prometheus successfully scrapes metrics
- [ ] Grafana can visualize metrics
- [ ] Histograms have appropriate buckets

**Grafana Dashboard**:
- [ ] Create dashboard: Request Rate (tool invocations/sec)
- [ ] Create dashboard: Latency Percentiles (p50, p95, p99)
- [ ] Create dashboard: Error Rate
- [ ] Create dashboard: Backend Health
- [ ] Create dashboard: Lock Statistics
- [ ] Export dashboard JSON

**Tasks**:
- [ ] Set up local Prometheus + Grafana
- [ ] Configure Prometheus to scrape metrics
- [ ] Create Grafana dashboards
- [ ] Generate load to populate dashboards
- [ ] Validate dashboard accuracy
- [ ] Export dashboard for production

**Deliverables**:
- `grafana/dashboards/taskman-overview.json`
- `docs/validation/2.1-metrics-validation.md`
- Grafana dashboard screenshots
- Sign-off: ✅ Ready for production

---

### 2.2 OpenTelemetry Tracing

#### Research Phase (45 minutes)
**Objectives**:
- Study OpenTelemetry architecture
- Design tracing strategy
- Plan instrumentation

**Tasks**:
- [ ] Research OpenTelemetry vs Zipkin vs Jaeger
- [ ] Study auto-instrumentation capabilities
- [ ] Design span structure for MCP operations
- [ ] Plan trace context propagation
- [ ] Research OTLP exporters

**Tracing Design**:
```
Root Span: MCP Tool Invocation
├─ Child Span: Input Validation
├─ Child Span: Lock Acquisition
├─ Child Span: Backend API Call
│  ├─ HTTP Request
│  └─ Response Processing
└─ Child Span: Response Serialization

Context Propagation:
- MCP request → Backend request (via headers)
- Correlation ID → Trace ID mapping
```

**Research Questions**:
1. Use auto-instrumentation or manual?
2. What to use for trace backend? (Jaeger, Tempo, Cloud provider)
3. Sampling strategy? (Always, probabilistic, adaptive)
4. Performance overhead acceptable?

**Deliverables**:
- `docs/research/tracing-design.md`
- Span structure diagram
- Instrumentation strategy

---

#### Implementation Phase (3 hours)
**Objectives**:
- Install OpenTelemetry SDK
- Configure auto-instrumentation
- Add manual spans for MCP operations
- Set up OTLP exporter

**Tasks**:
- [ ] Install dependencies
  ```bash
  npm install @opentelemetry/api \
              @opentelemetry/sdk-node \
              @opentelemetry/auto-instrumentations-node \
              @opentelemetry/exporter-trace-otlp-http
  ```

- [ ] Create `src/infrastructure/tracing.ts`
  - Initialize OpenTelemetry SDK
  - Configure resource attributes (service name, version)
  - Set up OTLP exporter
  - Configure auto-instrumentations (HTTP, etc.)
  - Export initialization function

- [ ] Update `src/index.ts`
  - Call initializeTracing() FIRST (before any imports)
  - Add ENABLE_TRACING environment check

- [ ] Add manual spans to `src/features/tasks/register.ts`
  - Create span for each tool invocation
  - Add attributes (tool_name, task_id, etc.)
  - Track span status (ok, error)

- [ ] Update `src/backend/client.ts`
  - Propagate trace context to backend (W3C Trace Context headers)
  - Add span attributes (method, url, status)

- [ ] Create helper: `src/infrastructure/tracing-helper.ts`
  - withSpan() wrapper for easy instrumentation
  - addSpanAttributes() helper

**Auto-Instrumentation**:
- HTTP client/server (automatic)
- DNS resolution (automatic)
- Custom: MCP tool invocations (manual)

**Code Checklist**:
- [ ] Tracing initialized before any imports
- [ ] Auto-instrumentation enabled
- [ ] Manual spans for MCP tools
- [ ] Trace context propagated to backend
- [ ] Span attributes meaningful
- [ ] Error status recorded in spans

**Deliverables**:
- `src/infrastructure/tracing.ts` (150 lines)
- `src/infrastructure/tracing-helper.ts` (80 lines)
- MCP tools instrumented with manual spans
- Trace context propagation working

---

#### Testing Phase (60 minutes)
**Objectives**:
- Verify traces are exported
- Test span structure
- Validate trace context propagation
- Performance impact assessment

**Test Scenarios**:
1. **Basic Trace**: Call tool → trace appears in backend
2. **Span Hierarchy**: Parent/child relationships correct
3. **Trace Propagation**: MCP → Backend traces linked
4. **Error Tracking**: Tool error → span status=error
5. **Sampling**: Verify sampling strategy
6. **Performance**: Tracing overhead <5%

**Tasks**:
- [ ] Set up Jaeger locally
  ```bash
  docker run -d --name jaeger \
    -p 16686:16686 \
    -p 4318:4318 \
    jaegertracing/all-in-one:latest
  ```

- [ ] Write integration tests: `__tests__/tracing.integration.test.ts`
- [ ] Test trace export
- [ ] Test span attributes
- [ ] Test error recording
- [ ] Performance benchmark: With/without tracing
- [ ] Manual test: View traces in Jaeger UI

**Validation Commands**:
```bash
# Start Jaeger
docker run -d -p 16686:16686 -p 4318:4318 jaegertracing/all-in-one:latest

# Enable tracing
ENABLE_TRACING=true OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318/v1/traces npm start

# Generate traffic
npm run load-test:tools

# View traces
open http://localhost:16686
```

**Deliverables**:
- Integration tests for tracing
- Jaeger setup documentation
- Performance benchmark results
- Example trace screenshots

---

#### Validation Phase (30 minutes)
**Objectives**:
- End-to-end trace validation
- Performance impact assessment
- Production readiness check

**Acceptance Criteria**:
- [ ] Traces appear in Jaeger within 10 seconds
- [ ] Span hierarchy is correct
- [ ] Trace context propagates to backend
- [ ] Error spans capture stack traces
- [ ] Tracing overhead <5% latency increase
- [ ] Sampling configurable

**Production Readiness**:
- [ ] OTLP exporter can connect to production backend
- [ ] Sampling strategy appropriate (start with 1%, increase gradually)
- [ ] Trace retention policy defined
- [ ] Team trained on trace analysis

**Tasks**:
- [ ] Generate 100 operations, verify all traces
- [ ] Benchmark latency: Tracing on vs off
- [ ] Verify trace backend connectivity
- [ ] Document trace analysis workflows

**Deliverables**:
- `docs/validation/2.2-tracing-validation.md`
- Trace analysis guide
- Sign-off: ✅ Ready for production

---

### 2.3 Circuit Breaker Pattern

#### Research Phase (30 minutes)
**Objectives**:
- Study circuit breaker pattern
- Design circuit breaker configuration
- Plan integration with backend client

**Tasks**:
- [ ] Research opossum vs other circuit breaker libraries
- [ ] Study circuit breaker states (closed, open, half-open)
- [ ] Design thresholds (error rate, timeout)
- [ ] Plan fallback strategies

**Circuit Breaker Design**:
```
States:
- Closed: Normal operation
- Open: Fail fast, don't call backend
- Half-Open: Test if backend recovered

Configuration:
- Error threshold: 50% errors → open
- Timeout: 30 seconds
- Reset timeout: 30 seconds (try half-open)
- Rolling window: 10 seconds

Fallback:
- Return cached data (if available)
- Return error with retry-after header
```

**Research Questions**:
1. What error percentage triggers circuit break?
2. How long to stay open before testing?
3. What's the fallback strategy?
4. How to emit metrics?

**Deliverables**:
- `docs/research/circuit-breaker-design.md`
- Configuration specification
- State diagram

---

#### Implementation Phase (2 hours)
**Objectives**:
- Install opossum
- Integrate circuit breaker into backend client
- Add metrics
- Configure fallback

**Tasks**:
- [ ] Install dependencies
  ```bash
  npm install opossum
  npm install -D @types/opossum
  ```

- [ ] Update `src/backend/client.ts`
  - Import CircuitBreaker from opossum
  - Create circuit breaker instance in constructor
  - Wrap executeRequest() with circuit breaker
  - Configure thresholds
  - Set up event listeners (open, close, halfOpen)
  - Add fallback handler
  - Emit metrics on state changes

- [ ] Update `src/infrastructure/metrics.ts`
  - Add backend_circuit_breaker_state gauge
  - Add backend_circuit_breaker_events_total counter

- [ ] Create `src/infrastructure/circuit-breaker-health.ts`
  - Monitor circuit breaker state
  - Include in health checks

**Circuit Breaker Configuration**:
```typescript
new CircuitBreaker(this.executeRequest, {
  timeout: 30000,              // Request timeout
  errorThresholdPercentage: 50, // Open at 50% errors
  resetTimeout: 30000,         // Try to close after 30s
  rollingCountTimeout: 10000,  // 10s rolling window
  rollingCountBuckets: 10,     // 10 buckets
  name: "backend-api",
});
```

**Code Checklist**:
- [ ] Circuit breaker wraps all backend calls
- [ ] State transitions logged
- [ ] Metrics emitted on state changes
- [ ] Fallback returns meaningful error
- [ ] Configuration tunable via environment

**Deliverables**:
- Updated `src/backend/client.ts` with circuit breaker
- Circuit breaker metrics
- Configuration documented

---

#### Testing Phase (60 minutes)
**Objectives**:
- Test circuit breaker states
- Test threshold triggers
- Test recovery behavior
- Load test with failures

**Test Scenarios**:
1. **Normal Operation**: Requests succeed → circuit stays closed
2. **Partial Failures**: 30% errors → circuit stays closed
3. **Threshold Exceeded**: 60% errors → circuit opens
4. **Open Circuit**: New requests fail fast
5. **Half-Open**: After 30s, try request → success → circuit closes
6. **Half-Open Failure**: After 30s, try request → failure → circuit reopens

**Tasks**:
- [ ] Write integration tests: `__tests__/circuit-breaker.integration.test.ts`
- [ ] Mock backend to return errors
- [ ] Test closed → open transition
- [ ] Test open → half-open → closed transition
- [ ] Test open → half-open → open transition
- [ ] Test fallback behavior
- [ ] Load test with simulated failures

**Validation Commands**:
```bash
# Unit tests
npm test src/backend/client.test.ts

# Integration tests
npm test __tests__/circuit-breaker.integration.test.ts

# Load test with failures
npm run load-test:circuit-breaker
```

**Deliverables**:
- Integration tests covering all states
- Load test with failure scenarios
- Test results documented

---

#### Validation Phase (30 minutes)
**Objectives**:
- Validate circuit breaker behavior
- Verify metrics accuracy
- Production readiness

**Acceptance Criteria**:
- [ ] Circuit opens at 50% error rate
- [ ] Circuit closes after successful recovery
- [ ] Fallback prevents cascading failures
- [ ] Metrics accurately track state
- [ ] Health check reflects circuit state
- [ ] Configuration tunable

**Failure Scenarios**:
- [ ] Backend down: Circuit opens within 10 seconds
- [ ] Backend slow: Circuit opens on timeout
- [ ] Backend recovers: Circuit closes within 60 seconds
- [ ] Intermittent errors: Circuit stays closed (below threshold)

**Tasks**:
- [ ] Simulate backend outage, verify circuit opens
- [ ] Verify requests fail fast when circuit open
- [ ] Simulate backend recovery, verify circuit closes
- [ ] Check metrics accuracy
- [ ] Document circuit breaker tuning guide

**Deliverables**:
- `docs/validation/2.3-circuit-breaker-validation.md`
- Tuning guide for operations
- Sign-off: ✅ Ready for production

---

## Phase 2 Completion Checklist

**Before proceeding to Phase 3**:
- [ ] All Phase 2 implementations complete
- [ ] All Phase 2 tests passing
- [ ] Prometheus metrics working
- [ ] OpenTelemetry traces visible
- [ ] Circuit breaker tested
- [ ] Grafana dashboards created
- [ ] Jaeger traces validated
- [ ] Performance benchmarks acceptable
- [ ] Code review completed

**Phase 2 Deliverables**:
1. Prometheus metrics (15+ metrics)
2. Grafana dashboards
3. OpenTelemetry tracing
4. Jaeger integration
5. Circuit breaker pattern
6. Observability documentation

**Phase 2 Success Metrics**:
- ✅ P99 latency visible in Grafana
- ✅ Traces provide debugging value
- ✅ Circuit breaker prevents cascade failures
- ✅ Observability overhead <5%

---

## Phase 3: Persistence (Week 3)
**Goal**: Durable state management
**Duration**: 6-18 hours
**Dependencies**: Phase 1 (configuration)

### 3.1 SQLite Persistence Layer

#### Research Phase (60 minutes)
**Objectives**:
- Design database schema
- Plan migration from in-memory
- Research better-sqlite3 vs alternatives

**Tasks**:
- [ ] Research SQLite best practices
- [ ] Design schema for locks table
- [ ] Design schema for audit_logs table
- [ ] Plan transaction strategy
- [ ] Research WAL mode for concurrency

**Database Design**:
```sql
CREATE TABLE locks (
  lock_key TEXT PRIMARY KEY,
  agent TEXT NOT NULL,
  timestamp INTEGER NOT NULL,
  object_type TEXT NOT NULL,
  object_id TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_locks_expiry ON locks(timestamp);
CREATE INDEX idx_locks_type ON locks(object_type);

CREATE TABLE audit_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  correlation_id TEXT,
  operation TEXT NOT NULL,
  agent TEXT NOT NULL,
  result TEXT NOT NULL,
  details TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_correlation ON audit_logs(correlation_id);
CREATE INDEX idx_audit_operation ON audit_logs(operation);
```

**Research Questions**:
1. better-sqlite3 vs sqlite3 (answer: better-sqlite3 for sync API)
2. WAL mode for concurrency?
3. Automatic vacuum strategy?
4. Backup/restore approach?

**Deliverables**:
- `docs/research/persistence-design.md`
- Database schema specification
- Migration plan

---

#### Implementation Phase (5 hours)
**Objectives**:
- Install better-sqlite3
- Create persistence layer
- Integrate with locking service
- Integrate with audit service
- Add initialization/migration

**Tasks**:
- [ ] Install dependencies
  ```bash
  npm install better-sqlite3
  npm install -D @types/better-sqlite3
  ```

- [ ] Create `src/infrastructure/persistence/sqlite.ts`
  - SqlitePersistence class
  - initSchema() method
  - saveAuditLog() method
  - getRecentAuditLogs() method
  - saveLock() method
  - deleteLock() method
  - getAllLocks() method
  - cleanupExpiredLocks() method
  - close() method

- [ ] Update `src/infrastructure/locking.ts`
  - Add persistence option
  - Load locks from database on startup
  - Save locks to database on changes
  - Periodic cleanup of expired locks

- [ ] Update `src/infrastructure/audit.ts`
  - Add persistence option
  - Write logs to database asynchronously
  - Keep in-memory buffer for recent logs

- [ ] Create `src/infrastructure/persistence/index.ts`
  - Export persistence factory
  - Support ENABLE_PERSISTENCE config

- [ ] Update `src/index.ts`
  - Initialize persistence on startup
  - Register persistence cleanup in shutdown

- [ ] Create database initialization script
  - `scripts/init-db.ts`
  - Creates database file
  - Runs schema migrations

**Persistence Configuration**:
```typescript
// In config
ENABLE_PERSISTENCE=true
PERSISTENCE_TYPE=sqlite
SQLITE_DB_PATH=./data/taskman.db
```

**Code Checklist**:
- [ ] Database initialized on startup
- [ ] Schema migrations applied automatically
- [ ] Locks persisted synchronously (consistency)
- [ ] Audit logs persisted asynchronously (performance)
- [ ] Database closed on shutdown
- [ ] WAL mode enabled for concurrency
- [ ] Automatic vacuum configured

**Deliverables**:
- `src/infrastructure/persistence/sqlite.ts` (400 lines)
- Updated locking and audit services
- Database initialization script
- Migration strategy

---

#### Testing Phase (2 hours)
**Objectives**:
- Test database operations
- Test persistence across restarts
- Test concurrency
- Test performance

**Test Scenarios**:
1. **Lock Persistence**: Create lock → restart → lock still exists
2. **Audit Persistence**: Log entry → restart → entry still exists
3. **Expired Lock Cleanup**: Old lock → cleanup → removed from DB
4. **Concurrent Writes**: Multiple locks → no corruption
5. **Database Growth**: 10,000 logs → database size reasonable
6. **Performance**: Lock acquisition <5ms, audit write <2ms

**Tasks**:
- [ ] Write integration tests: `__tests__/persistence.integration.test.ts`
- [ ] Test lock persistence
- [ ] Test audit log persistence
- [ ] Test database recovery after crash
- [ ] Test expired lock cleanup
- [ ] Performance benchmark: Lock ops, audit writes
- [ ] Load test: 10,000 operations

**Validation Commands**:
```bash
# Integration tests
npm test __tests__/persistence.integration.test.ts

# Performance benchmark
npm run benchmark:persistence

# Database inspection
sqlite3 data/taskman.db "SELECT COUNT(*) FROM locks;"
sqlite3 data/taskman.db "SELECT COUNT(*) FROM audit_logs;"

# WAL mode check
sqlite3 data/taskman.db "PRAGMA journal_mode;"
```

**Deliverables**:
- Integration tests with restart scenarios
- Performance benchmarks
- Database inspection results

---

#### Validation Phase (60 minutes)
**Objectives**:
- Validate data durability
- Test backup/restore
- Production readiness

**Acceptance Criteria**:
- [ ] Locks survive server restarts
- [ ] Audit logs survive server restarts
- [ ] Lock acquisition latency <10ms
- [ ] Audit write latency <5ms (async)
- [ ] Database size manageable (vacuum works)
- [ ] No data corruption under load
- [ ] Backup/restore works

**Durability Tests**:
- [ ] Create 100 locks → kill -9 process → restart → verify locks
- [ ] Write 1000 audit logs → crash → restart → verify logs
- [ ] Concurrent writes → no corruption

**Backup/Restore**:
- [ ] Create backup script
- [ ] Test restore from backup
- [ ] Document backup strategy

**Tasks**:
- [ ] Crash testing (kill -9)
- [ ] Backup/restore testing
- [ ] Verify WAL checkpoint
- [ ] Document operational procedures

**Deliverables**:
- `scripts/backup-db.sh`
- `scripts/restore-db.sh`
- `docs/validation/3.1-persistence-validation.md`
- Operational runbook
- Sign-off: ✅ Ready for production

---

### 3.2 Redis Persistence (Optional)

**Note**: This is optional for distributed deployments. Skip if running single instance.

#### Research Phase (45 minutes)
**Objectives**:
- Design Redis schema
- Plan migration from in-memory
- Research ioredis vs node-redis

**Tasks**:
- [ ] Research Redis best practices
- [ ] Design key structure for locks
- [ ] Design key structure for audit logs
- [ ] Plan TTL strategy
- [ ] Research Redis persistence modes (RDB, AOF)

**Redis Design**:
```
Lock Keys:
  lock:task:abc123 → {"agent": "tool", "timestamp": 123456789}
  TTL: 30 minutes (auto-expire)

Audit Keys:
  audit:123456789 → {"operation": "...", "agent": "..."}
  audit:index → sorted set by timestamp
  TTL: 7 days
```

**Research Questions**:
1. ioredis vs node-redis? (answer: ioredis for better TypeScript support)
2. RDB vs AOF persistence?
3. How to handle Redis downtime?
4. Fallback to in-memory if Redis unavailable?

**Deliverables**:
- `docs/research/redis-design.md`
- Key schema specification

---

#### Implementation Phase (6 hours)
**Objectives**:
- Install ioredis
- Create Redis persistence layer
- Integrate with services
- Add connection pooling
- Implement fallback strategy

**Tasks**:
- [ ] Install dependencies
  ```bash
  npm install ioredis
  npm install -D @types/ioredis
  ```

- [ ] Create `src/infrastructure/persistence/redis.ts`
  - RedisPersistence class
  - connect() method
  - disconnect() method
  - saveLock() with TTL
  - getLock() method
  - deleteLock() method
  - getAllLocks() method
  - saveAuditLog() to sorted set
  - getRecentAuditLogs() from sorted set

- [ ] Update `src/infrastructure/locking.ts`
  - Support Redis persistence backend
  - Automatic lock expiration via TTL

- [ ] Update `src/infrastructure/audit.ts`
  - Support Redis persistence backend
  - Use sorted sets for time-based queries

- [ ] Create `src/infrastructure/persistence/factory.ts`
  - Persistence factory based on config
  - createPersistence(type: 'sqlite' | 'redis')

- [ ] Add connection health checks
  - Ping Redis periodically
  - Include in readiness probe
  - Fallback to in-memory if Redis down

- [ ] Add Redis connection pooling
- [ ] Add reconnection logic

**Redis Configuration**:
```typescript
ENABLE_PERSISTENCE=true
PERSISTENCE_TYPE=redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_KEY_PREFIX=taskman:
```

**Code Checklist**:
- [ ] Redis connection established on startup
- [ ] Connection included in shutdown sequence
- [ ] TTL set on locks (auto-cleanup)
- [ ] Sorted sets for audit logs
- [ ] Connection health monitored
- [ ] Reconnection on disconnect
- [ ] Fallback to in-memory on Redis failure

**Deliverables**:
- `src/infrastructure/persistence/redis.ts` (450 lines)
- `src/infrastructure/persistence/factory.ts` (80 lines)
- Redis integration complete
- Fallback strategy implemented

---

#### Testing Phase (2 hours)
**Objectives**:
- Test Redis operations
- Test TTL expiration
- Test connection failures
- Test performance

**Test Scenarios**:
1. **Lock Persistence**: Create lock → retrieve → correct
2. **Lock Expiration**: Create lock → wait 30min → expired
3. **Audit Persistence**: Write log → query → correct
4. **Connection Failure**: Kill Redis → fallback to in-memory
5. **Reconnection**: Restore Redis → reconnect automatically
6. **Performance**: Lock ops <3ms, audit writes <2ms

**Tasks**:
- [ ] Start local Redis
  ```bash
  docker run -d -p 6379:6379 redis:alpine
  ```

- [ ] Write integration tests: `__tests__/redis.integration.test.ts`
- [ ] Test lock operations
- [ ] Test TTL expiration
- [ ] Test audit log operations
- [ ] Test connection failure handling
- [ ] Test reconnection logic
- [ ] Performance benchmark

**Validation Commands**:
```bash
# Start Redis
docker run -d -p 6379:6379 redis:alpine

# Integration tests
npm test __tests__/redis.integration.test.ts

# Redis inspection
redis-cli KEYS "taskman:lock:*"
redis-cli ZRANGE "taskman:audit:index" 0 -1 WITHSCORES

# Performance benchmark
npm run benchmark:redis
```

**Deliverables**:
- Integration tests for Redis
- TTL expiration tests
- Connection failure tests
- Performance benchmarks

---

#### Validation Phase (60 minutes)
**Objectives**:
- Validate distributed scenario
- Test multi-instance coordination
- Production readiness

**Acceptance Criteria**:
- [ ] Locks shared across multiple instances
- [ ] Audit logs centralized
- [ ] Lock acquisition latency <5ms
- [ ] Connection failures handled gracefully
- [ ] Reconnection works automatically
- [ ] No data loss during Redis restart

**Multi-Instance Test**:
- [ ] Start Redis
- [ ] Start 3 TaskMan instances
- [ ] Create lock on instance 1
- [ ] Verify lock visible on instance 2 and 3
- [ ] Delete lock on instance 2
- [ ] Verify lock deleted on all instances

**Tasks**:
- [ ] Multi-instance coordination test
- [ ] Redis restart test (no data loss)
- [ ] Performance under load (3 instances)
- [ ] Document Redis operational procedures

**Deliverables**:
- `docs/validation/3.2-redis-validation.md`
- Multi-instance test results
- Redis operational runbook
- Sign-off: ✅ Ready for production

---

## Phase 3 Completion Checklist

**Before proceeding to Phase 4**:
- [ ] SQLite or Redis persistence implemented
- [ ] All tests passing
- [ ] Data survives restarts
- [ ] Performance acceptable
- [ ] Backup/restore tested
- [ ] Operational runbooks complete

**Phase 3 Deliverables**:
1. Persistence layer (SQLite or Redis)
2. Database schema
3. Migration scripts
4. Backup/restore scripts
5. Performance benchmarks
6. Operational documentation

**Phase 3 Success Metrics**:
- ✅ 100% lock retention across restarts
- ✅ 100% audit log retention
- ✅ Persistence latency <10ms
- ✅ Zero data corruption

---

## Phase 4: Quality (Week 4)
**Goal**: Comprehensive testing and documentation
**Duration**: 16-24 hours
**Dependencies**: Phases 1-3 complete

### 4.1 Comprehensive Integration Test Suite

#### Research Phase (60 minutes)
**Objectives**:
- Design test strategy
- Plan test coverage
- Research testing patterns

**Tasks**:
- [ ] Define test coverage goals (>85%)
- [ ] Design test scenarios for each tool
- [ ] Plan end-to-end workflow tests
- [ ] Research testing best practices

**Test Categories**:
1. **Tool Tests**: Each of 30+ tools
2. **Workflow Tests**: Multi-step operations
3. **Error Tests**: Error handling and recovery
4. **Performance Tests**: Latency and throughput
5. **Resilience Tests**: Failures and recovery
6. **Security Tests**: Input validation

**Test Scenarios** (10 per tool):
- Happy path
- Validation errors
- Not found errors
- Concurrent operations
- Large data sets
- Edge cases
- Error recovery
- Performance under load

**Deliverables**:
- `docs/research/test-strategy.md`
- Test plan document
- Coverage targets

---

#### Implementation Phase (12 hours)
**Objectives**:
- Write comprehensive test suite
- Achieve >85% coverage
- All tools tested

**Tasks**:
- [ ] Set up test infrastructure
  ```bash
  npm install -D vitest @vitest/coverage-v8 @vitest/ui
  ```

- [ ] Create test helpers: `__tests__/helpers/`
  - mockBackendClient()
  - createTestServer()
  - generateTestData()

- [ ] Write task tool tests: `__tests__/features/tasks.integration.test.ts`
  - task_create: 10 scenarios
  - task_read: 5 scenarios
  - task_update: 8 scenarios
  - task_delete: 5 scenarios
  - task_list: 10 scenarios
  - task_search: 8 scenarios
  - task_bulk_update: 6 scenarios
  - task_bulk_assign_sprint: 5 scenarios
  - task_set_status: 6 scenarios
  - task_assign: 6 scenarios

- [ ] Write project tool tests: `__tests__/features/projects.integration.test.ts`
  - project_create: 8 scenarios
  - project_read: 5 scenarios
  - project_update: 6 scenarios
  - project_delete: 5 scenarios
  - project_list: 8 scenarios
  - project_add_sprint: 5 scenarios
  - project_remove_sprint: 5 scenarios
  - project_add_meta_task: 5 scenarios
  - project_add_comment: 5 scenarios
  - project_add_blocker: 5 scenarios
  - project_get_comments: 5 scenarios
  - project_get_metrics: 5 scenarios

- [ ] Write action-list tool tests: `__tests__/features/action-lists.integration.test.ts`
  - Similar coverage for all action-list tools

- [ ] Write workflow tests: `__tests__/workflows/`
  - Create project → create tasks → assign sprint → complete
  - Create action-list → add items → toggle items → complete
  - Concurrent task updates with locking

- [ ] Write error handling tests: `__tests__/errors/`
  - Backend down scenarios
  - Network timeout scenarios
  - Validation error scenarios
  - Lock contention scenarios

- [ ] Write performance tests: `__tests__/performance/`
  - Latency benchmarks
  - Throughput benchmarks
  - Concurrent operation benchmarks

- [ ] Write security tests: `__tests__/security/`
  - SQL injection attempts (should be prevented by backend)
  - XSS attempts (should be sanitized)
  - Invalid input handling

**Test Template**:
```typescript
describe("task_create", () => {
  let server: McpServer;
  let testData: TaskAttributes;

  beforeEach(() => {
    server = createTestServer();
    testData = generateTestTaskData();
  });

  it("should create task with valid input", async () => {
    const result = await server.callTool("task_create", { task: testData });
    expect(result.content[0].text).toBeDefined();
    const parsed = JSON.parse(result.content[0].text);
    expect(parsed.task).toMatchObject(testData);
  });

  it("should fail with missing title", async () => {
    const invalid = { ...testData, title: undefined };
    await expect(server.callTool("task_create", { task: invalid }))
      .rejects.toThrow(/title.*required/i);
  });

  // ... 8 more scenarios
});
```

**Code Checklist**:
- [ ] All 30+ tools have test coverage
- [ ] Happy paths tested
- [ ] Error paths tested
- [ ] Edge cases tested
- [ ] Concurrent operations tested
- [ ] Performance benchmarks exist

**Deliverables**:
- 200+ test cases
- Test coverage >85%
- All tools tested
- Performance benchmarks

---

#### Testing Phase (3 hours)
**Objectives**:
- Run full test suite
- Generate coverage report
- Identify gaps
- Fix failing tests

**Tasks**:
- [ ] Run all tests
  ```bash
  npm test
  ```

- [ ] Generate coverage report
  ```bash
  npm run test:coverage
  ```

- [ ] Review coverage report
  - Identify uncovered lines
  - Identify uncovered branches
  - Prioritize gaps

- [ ] Fill coverage gaps
  - Write additional tests for uncovered code
  - Aim for >85% coverage

- [ ] Run tests in CI
  - Set up GitHub Actions workflow
  - Run tests on every commit

**Coverage Targets**:
- Overall: >85%
- Features: >90%
- Infrastructure: >80%
- Critical paths: 100%

**Validation Commands**:
```bash
# Run all tests
npm test

# Coverage report
npm run test:coverage
open coverage/index.html

# Watch mode (during development)
npm run test:watch

# UI mode (interactive)
npm run test:ui
```

**Deliverables**:
- All tests passing
- Coverage report >85%
- CI workflow configured
- Coverage gaps filled

---

#### Validation Phase (90 minutes)
**Objectives**:
- Validate test quality
- Verify coverage
- Sign off on testing

**Acceptance Criteria**:
- [ ] Test coverage >85%
- [ ] All tools tested
- [ ] All workflows tested
- [ ] Performance benchmarks exist
- [ ] Tests run in CI
- [ ] No flaky tests

**Test Quality Checks**:
- [ ] Tests are deterministic (no randomness)
- [ ] Tests are isolated (no shared state)
- [ ] Tests are fast (<5 min total)
- [ ] Tests are readable
- [ ] Tests assert meaningful behavior

**Tasks**:
- [ ] Review test quality with team
- [ ] Run tests 10 times to detect flakes
- [ ] Verify CI integration
- [ ] Document test running procedures

**Deliverables**:
- `docs/validation/4.1-testing-validation.md`
- Test quality report
- Sign-off: ✅ Testing complete

---

### 4.2 API Documentation

#### Research Phase (30 minutes)
**Objectives**:
- Choose documentation approach
- Design documentation structure

**Tasks**:
- [ ] Research OpenAPI/Swagger for HTTP endpoints
- [ ] Research JSDoc for TypeScript
- [ ] Design documentation structure
- [ ] Plan documentation generation

**Documentation Scope**:
1. MCP Tools (30+ tools)
2. HTTP Endpoints (health, metrics)
3. Configuration variables (35+)
4. Architecture diagrams
5. Operational runbooks

**Deliverables**:
- Documentation plan

---

#### Implementation Phase (4 hours)
**Objectives**:
- Document all MCP tools
- Document configuration
- Create architecture docs
- Generate API docs

**Tasks**:
- [ ] Create `docs/api/` directory structure

- [ ] Document MCP tools: `docs/api/mcp-tools.md`
  - List all tools with descriptions
  - Document input schemas
  - Document output schemas
  - Provide examples for each tool

- [ ] Document configuration: `docs/api/configuration.md`
  - List all 35+ variables
  - Document types and defaults
  - Provide examples
  - Document validation rules

- [ ] Create architecture docs: `docs/architecture/`
  - System architecture diagram
  - Data flow diagram
  - Component diagram
  - Sequence diagrams

- [ ] Document HTTP endpoints: `docs/api/http-endpoints.md`
  - Health endpoints
  - Metrics endpoint
  - Request/response formats

- [ ] Add JSDoc comments to all public methods
  - Tool handlers
  - Backend client methods
  - Infrastructure services

- [ ] Generate API docs from JSDoc
  ```bash
  npx typedoc --out docs/api/generated src/
  ```

**Documentation Template**:
```markdown
## task_create

Create a new task record.

### Input Schema

```typescript
{
  task: {
    title: string;          // Required, 1-200 chars
    description?: string;   // Optional, max 10000 chars
    status?: TaskStatus;    // Optional, default: "pending"
    priority?: Priority;    // Optional, default: "medium"
    tags?: string[];        // Optional, max 20 tags
    // ... more fields
  }
}
```

### Output Schema

```typescript
{
  task: TaskRecord;  // Full task object with ID
}
```

### Example

```typescript
const result = await mcpClient.callTool("task_create", {
  task: {
    title: "Implement logging",
    description: "Add structured logging with Pino",
    priority: "high",
    tags: ["infrastructure", "logging"]
  }
});
```

### Error Scenarios

- `ValidationError`: Title missing or too long
- `BackendError`: Backend API unreachable
```

**Code Checklist**:
- [ ] All tools documented
- [ ] All configuration documented
- [ ] Architecture diagrams created
- [ ] JSDoc comments added
- [ ] Examples provided

**Deliverables**:
- `docs/api/mcp-tools.md` (comprehensive tool reference)
- `docs/api/configuration.md`
- `docs/api/http-endpoints.md`
- `docs/architecture/` (diagrams)
- Generated API docs

---

#### Testing Phase (60 minutes)
**Objectives**:
- Verify documentation accuracy
- Test examples
- Review with team

**Tasks**:
- [ ] Verify all tools documented
- [ ] Test all examples in documentation
- [ ] Check for broken links
- [ ] Verify diagrams are accurate
- [ ] Spell check
- [ ] Technical review with team

**Validation Commands**:
```bash
# Test examples
npm run test:docs

# Check links
npx markdown-link-check docs/**/*.md

# Spell check
npx cspell "docs/**/*.md"
```

**Deliverables**:
- All examples tested and working
- Documentation reviewed
- No broken links

---

#### Validation Phase (30 minutes)
**Objectives**:
- Documentation completeness check
- User acceptance

**Acceptance Criteria**:
- [ ] All tools documented
- [ ] All configuration documented
- [ ] Examples tested
- [ ] Diagrams accurate
- [ ] No spelling errors
- [ ] Easy to navigate

**User Acceptance**:
- [ ] New developer can understand system from docs
- [ ] Operations team can configure from docs
- [ ] API reference is searchable

**Deliverables**:
- `docs/validation/4.2-documentation-validation.md`
- Sign-off: ✅ Documentation complete

---

### 4.3 Operational Runbooks

#### Research Phase (30 minutes)
**Objectives**:
- Identify operational scenarios
- Design runbook structure

**Tasks**:
- [ ] List operational scenarios
- [ ] Design runbook template
- [ ] Plan troubleshooting guides

**Operational Scenarios**:
1. Server startup
2. Server shutdown
3. Configuration changes
4. Backend outage
5. Database corruption
6. Performance issues
7. Memory leaks
8. Disk space issues
9. Monitoring alerts
10. Incident response

**Deliverables**:
- Runbook structure

---

#### Implementation Phase (2 hours)
**Objectives**:
- Write operational runbooks
- Create troubleshooting guides

**Tasks**:
- [ ] Create `docs/runbooks/` directory

- [ ] Write startup runbook: `docs/runbooks/startup.md`
  - Prerequisites
  - Environment setup
  - Configuration validation
  - Startup procedure
  - Health check verification

- [ ] Write shutdown runbook: `docs/runbooks/shutdown.md`
  - Graceful shutdown procedure
  - Verification steps
  - Emergency shutdown

- [ ] Write deployment runbook: `docs/runbooks/deployment.md`
  - Pre-deployment checks
  - Deployment procedure
  - Rollback procedure
  - Post-deployment verification

- [ ] Write troubleshooting guide: `docs/runbooks/troubleshooting.md`
  - Common issues and solutions
  - Debug procedures
  - Log analysis guide
  - Performance debugging

- [ ] Write incident response: `docs/runbooks/incident-response.md`
  - Severity levels
  - Escalation procedures
  - Communication templates
  - Post-mortem template

- [ ] Write backup/restore: `docs/runbooks/backup-restore.md`
  - Backup procedures
  - Restore procedures
  - Testing backup integrity

- [ ] Write monitoring guide: `docs/runbooks/monitoring.md`
  - Key metrics to monitor
  - Alert thresholds
  - Alert response procedures
  - Dashboard guide

**Runbook Template**:
```markdown
# Runbook: Backend Outage

## Symptoms
- Health check failing: /health/ready returns 503
- Circuit breaker open
- Logs show: "Backend unreachable"

## Impact
- MCP tools unable to create/update data
- Read-only operations work (cached)
- Moderate severity

## Diagnosis
1. Check backend health: `curl http://backend:8000/health`
2. Check network connectivity: `ping backend`
3. Check circuit breaker state: `curl http://localhost:3000/metrics | grep circuit_breaker_state`

## Resolution
1. Verify backend service is running
2. Check backend logs for errors
3. Restart backend service if needed
4. Monitor circuit breaker: Should auto-recover in 30s

## Prevention
- Set up backend monitoring
- Configure auto-restart
- Set up alerting for backend health

## Related
- docs/architecture/backend-integration.md
- docs/runbooks/troubleshooting.md
```

**Deliverables**:
- 7+ operational runbooks
- Troubleshooting guide
- Incident response procedures

---

#### Testing Phase (30 minutes)
**Objectives**:
- Validate runbooks with team
- Test procedures

**Tasks**:
- [ ] Walk through each runbook
- [ ] Verify procedures are accurate
- [ ] Test backup/restore procedures
- [ ] Review with operations team

**Deliverables**:
- Runbooks validated
- Procedures tested

---

#### Validation Phase (30 minutes)
**Objectives**:
- Operational readiness
- Team training

**Acceptance Criteria**:
- [ ] All operational scenarios documented
- [ ] Procedures tested
- [ ] Team trained
- [ ] Runbooks accessible

**Tasks**:
- [ ] Conduct runbook training session
- [ ] Create runbook quick-reference
- [ ] Add runbooks to on-call rotation

**Deliverables**:
- `docs/validation/4.3-runbooks-validation.md`
- Team training complete
- Sign-off: ✅ Operations ready

---

## Phase 4 Completion Checklist

**Final validation**:
- [ ] Test coverage >85%
- [ ] All tools tested
- [ ] Documentation complete
- [ ] Runbooks written
- [ ] Team trained
- [ ] CI/CD pipeline working

**Phase 4 Deliverables**:
1. Comprehensive test suite (200+ tests)
2. API documentation (complete)
3. Architecture documentation
4. Operational runbooks (7+)
5. Team training materials

**Phase 4 Success Metrics**:
- ✅ Test coverage >85%
- ✅ Documentation covers all features
- ✅ Operations team confident
- ✅ Zero ambiguity in procedures

---

## Final Production Readiness

### Pre-Production Checklist

**Phase 1 - Operational Stability**:
- [ ] Graceful shutdown working
- [ ] Structured logging implemented
- [ ] Health checks K8s-compatible
- [ ] Configuration validated

**Phase 2 - Observability**:
- [ ] Prometheus metrics exported
- [ ] Grafana dashboards created
- [ ] OpenTelemetry traces working
- [ ] Circuit breaker tested

**Phase 3 - Persistence**:
- [ ] State persists across restarts
- [ ] Backup/restore tested
- [ ] Performance acceptable

**Phase 4 - Quality**:
- [ ] Test coverage >85%
- [ ] Documentation complete
- [ ] Runbooks written
- [ ] Team trained

**Infrastructure**:
- [ ] Docker image built
- [ ] Kubernetes manifests created
- [ ] Secrets configured
- [ ] Resource limits set
- [ ] Monitoring configured
- [ ] Alerting configured

**Security**:
- [ ] Dependency audit clean
- [ ] No hardcoded secrets
- [ ] Input validation complete
- [ ] Security review done

**Performance**:
- [ ] Load tested
- [ ] Latency acceptable (p99 <1s)
- [ ] Memory usage acceptable
- [ ] No memory leaks

---

### Production Deployment

**Deployment Steps**:
1. [ ] Deploy to staging environment
2. [ ] Run smoke tests in staging
3. [ ] Monitor for 24 hours
4. [ ] Fix any issues found
5. [ ] Deploy to production (canary)
6. [ ] Monitor canary for 1 hour
7. [ ] Gradually increase traffic
8. [ ] Full production deployment
9. [ ] Monitor for 24 hours
10. [ ] Declare success

**Rollback Plan**:
- Revert to previous Docker image
- Restore database from backup
- Update DNS/load balancer
- Monitor for stability

---

### Success Metrics (30 days post-launch)

**Reliability**:
- [ ] Uptime >99.9%
- [ ] Zero data loss incidents
- [ ] MTBF >30 days
- [ ] MTTR <5 minutes

**Performance**:
- [ ] P50 latency <100ms
- [ ] P95 latency <500ms
- [ ] P99 latency <1000ms
- [ ] Throughput >100 req/s

**Observability**:
- [ ] 100% error logging
- [ ] Metrics used for debugging
- [ ] Traces provide value
- [ ] Alerts actionable

**Quality**:
- [ ] Zero critical bugs
- [ ] Test coverage maintained >85%
- [ ] Documentation up-to-date
- [ ] Team confidence high

---

## Timeline Summary

| Phase | Duration | Effort | Deliverables |
|-------|----------|--------|--------------|
| **Phase 1: Foundation** | Week 1 | 13-18h | Graceful shutdown, logging, health, config |
| **Phase 2: Observability** | Week 2 | 11-15h | Metrics, tracing, circuit breaker |
| **Phase 3: Persistence** | Week 3 | 6-18h | SQLite or Redis persistence |
| **Phase 4: Quality** | Week 4 | 16-24h | Tests, docs, runbooks |
| **Total** | 4 weeks | 46-75h | Production-ready MCP server |

**Contingency**: +25% buffer (12-19 hours)

**Grand Total**: 58-94 hours over 4 weeks

---

## Conclusion

This implementation plan provides a comprehensive roadmap to transform your TaskMan MCP server from a well-built development prototype into a production-grade service.

Each phase builds on the previous, with clear research → implementation → testing → validation cycles ensuring quality at every step.

The plan is **iterative** and **pragmatic**:
- Start with critical stability (Phase 1)
- Add observability (Phase 2)
- Ensure durability (Phase 3)
- Validate quality (Phase 4)

By following this plan, you will have:
✅ A stable, production-ready MCP server
✅ Comprehensive test coverage
✅ Full observability
✅ Operational confidence

**Next Steps**:
1. Review this plan with your team
2. Adjust timelines based on available resources
3. Start Phase 1: Operational Stability
4. Track progress using the TodoWrite tool
5. Validate at each gate before proceeding

Good luck! 🚀
