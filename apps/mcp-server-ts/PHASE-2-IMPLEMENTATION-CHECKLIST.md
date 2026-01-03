# Phase 2 Implementation Checklist - Step-by-Step Execution Guide

**Date**: November 7, 2025
**Status**: 🎯 READY TO EXECUTE
**Validation**: Every step must pass before proceeding to next
**Execution Mode**: Parallel where possible, sequential where dependencies exist

---

## Pre-Implementation Status ✅

- ✅ Phase 1 blocking issues resolved (imports + LOG_LEVEL)
- ✅ Server starts successfully
- ✅ All Phase 2 dependencies installed (276 packages)
- ✅ 4 research agents completed with full implementation code
- ✅ Configuration schema structure understood

---

## Phase 2.0: Configuration Foundation (15 minutes)

### Step 2.0.1: Update Configuration Schema ⏸️ READY
**File**: `src/config/schema.ts`

**Task**: Add Phase 2 environment variables to Joi schema

**Validation Before**:
```bash
# Verify current schema compiles
npm run build
```

**Changes Required**:
```typescript
// Add after existing Observability section (around line 107-120):

// Prometheus Metrics
METRICS_ENABLED: Joi.boolean()
  .default(true)
  .description("Enable Prometheus metrics collection"),

// OpenTelemetry Tracing
TRACING_ENABLED: Joi.boolean()
  .default(process.env.NODE_ENV === 'production')
  .description("Enable OpenTelemetry distributed tracing"),

OTEL_EXPORTER_OTLP_ENDPOINT: Joi.string()
  .uri()
  .default("http://localhost:4318/v1/traces")
  .description("OpenTelemetry OTLP exporter endpoint"),

OTEL_DEBUG: Joi.boolean()
  .default(false)
  .description("Enable OpenTelemetry diagnostic logging"),

OTEL_SAMPLE_RATE: Joi.number()
  .min(0)
  .max(1)
  .default(process.env.NODE_ENV === 'production' ? 0.1 : 1.0)
  .description("Trace sampling rate (0.0-1.0)"),

// Circuit Breaker
CIRCUIT_BREAKER_ENABLED: Joi.boolean()
  .default(true)
  .description("Enable circuit breaker for backend calls"),

CIRCUIT_BREAKER_ERROR_THRESHOLD: Joi.number()
  .min(1)
  .max(100)
  .default(50)
  .description("Error percentage to open circuit (1-100)"),

CIRCUIT_BREAKER_RESET_TIMEOUT_MS: Joi.number()
  .positive()
  .default(30000)
  .description("Milliseconds before attempting recovery"),

CIRCUIT_BREAKER_VOLUME_THRESHOLD: Joi.number()
  .positive()
  .default(10)
  .description("Minimum requests before calculating error rate"),

// Fallback Cache
FALLBACK_CACHE_ENABLED: Joi.boolean()
  .default(true)
  .description("Enable fallback cache for read operations"),

FALLBACK_CACHE_MAX_SIZE: Joi.number()
  .positive()
  .default(1000)
  .description("Maximum cache entries"),

FALLBACK_CACHE_TTL_MS: Joi.number()
  .positive()
  .default(300000) // 5 minutes
  .description("Cache entry time-to-live (ms)"),
```

**Add to Config Interface** (around line 136-178):
```typescript
// Metrics
METRICS_ENABLED: boolean;

// Tracing
TRACING_ENABLED: boolean;
OTEL_EXPORTER_OTLP_ENDPOINT: string;
OTEL_DEBUG: boolean;
OTEL_SAMPLE_RATE: number;

// Circuit Breaker
CIRCUIT_BREAKER_ENABLED: boolean;
CIRCUIT_BREAKER_ERROR_THRESHOLD: number;
CIRCUIT_BREAKER_RESET_TIMEOUT_MS: number;
CIRCUIT_BREAKER_VOLUME_THRESHOLD: number;

// Fallback Cache
FALLBACK_CACHE_ENABLED: boolean;
FALLBACK_CACHE_MAX_SIZE: number;
FALLBACK_CACHE_TTL_MS: number;
```

**Validation After**:
```bash
# Must compile without errors
npm run build

# Must show new config fields
node -e "import('./dist/config/index.js').then(m => console.log(Object.keys(m.config).filter(k => k.includes('METRICS') || k.includes('TRACING') || k.includes('CIRCUIT'))))"
```

**Success Criteria**:
- ✅ TypeScript compiles without errors
- ✅ Config object includes all new fields
- ✅ Default values set correctly
- ✅ No breaking changes to existing config

---

## Phase 2.1: Prometheus Metrics (45 minutes)

### Step 2.1.1: Create Metrics Service ⏸️ READY
**File**: `src/infrastructure/metrics.ts`

**Task**: Create comprehensive Prometheus metrics service

**Content**: Use complete implementation from Research Agent 1 output (6000+ lines)

**Key Components**:
- MetricsService class (singleton)
- 18 metrics:
  - Counters: HTTP requests, errors, tool executions, API calls, retries
  - Gauges: Active connections, memory, event loop, health status, resources
  - Histograms: HTTP duration, tool duration, API duration
  - Summary: Event loop lag
- Helper methods for recording metrics
- Integration points documented

**Validation After**:
```bash
# Must compile
npm run build

# Must export metricsService
node -e "import('./dist/infrastructure/metrics.js').then(m => console.log('metricsService exported:', !!m.metricsService))"
```

**Success Criteria**:
- ✅ File created with 600+ lines
- ✅ TypeScript compiles without errors
- ✅ metricsService singleton exports correctly
- ✅ All 18 metrics initialized

### Step 2.1.2: Create System Metrics Collector ⏸️ READY
**File**: `src/infrastructure/system-metrics.ts`

**Task**: Periodic collection of system metrics (memory, event loop)

**Content**: Use implementation from Research Agent 1

**Validation After**:
```bash
npm run build
node -e "import('./dist/infrastructure/system-metrics.js').then(m => console.log('systemMetricsCollector exported:', !!m.systemMetricsCollector))"
```

**Success Criteria**:
- ✅ File created (~150 lines)
- ✅ Compiles without errors
- ✅ systemMetricsCollector exports correctly

### Step 2.1.3: Integrate Metrics into HTTP Transport ⏸️ READY
**File**: `src/transports/http.ts` (UPDATE)

**Task**: Add /metrics endpoint and request/response middleware

**Changes Required**:
1. Import metricsService
2. Add metrics middleware to track requests
3. Add GET /metrics endpoint
4. Record active connections

**Validation After**:
```bash
# Start server in HTTP mode
TASKMAN_MCP_TRANSPORT=http npm run dev &
sleep 5

# Test metrics endpoint
curl http://localhost:3000/metrics | grep "taskman_"

# Stop server
kill %1
```

**Success Criteria**:
- ✅ Server starts without errors
- ✅ /metrics endpoint returns Prometheus format
- ✅ Metrics contain taskman_ prefix
- ✅ HTTP requests are tracked

### Step 2.1.4: Integrate Metrics into Backend Client ⏸️ READY
**File**: `src/backend/client.ts` (UPDATE)

**Task**: Add metrics to backend API calls

**Changes Required**:
1. Import metricsService
2. Add axios interceptors for request timing
3. Record API call metrics (duration, status, retries)

**Validation After**:
```bash
npm run build
# Visual inspection of client.ts for metrics calls
```

**Success Criteria**:
- ✅ Compiles without errors
- ✅ Metrics recorded for all API methods
- ✅ Retry attempts tracked

### Step 2.1.5: Bootstrap Metrics in Main Entry Point ⏸️ READY
**File**: `src/index.ts` (UPDATE)

**Task**: Initialize metrics at startup

**Changes Required**:
1. Import metricsService and systemMetricsCollector
2. Start system metrics if METRICS_ENABLED
3. Register for graceful shutdown

**Validation After**:
```bash
# Full integration test
npm run dev
# Press Ctrl+C - should see "Stopping metrics collection"
```

**Success Criteria**:
- ✅ Metrics start automatically when enabled
- ✅ System metrics collector runs
- ✅ Graceful shutdown stops metrics

---

## Phase 2.2: OpenTelemetry Tracing (60 minutes)

### Step 2.2.1: Create Instrumentation Module ⚠️ CRITICAL
**File**: `src/instrumentation.ts`

**Task**: Initialize OpenTelemetry SDK - MUST BE FIRST IMPORT

**Content**: Use complete implementation from Research Agent 2

**Key Features**:
- NodeSDK initialization
- Auto-instrumentation for HTTP, Express, Axios
- OTLP exporter configuration
- Graceful shutdown handler

**Validation After**:
```bash
npm run build
# Must not have import errors
node dist/instrumentation.js
```

**Success Criteria**:
- ✅ File created (~150 lines)
- ✅ Compiles without errors
- ✅ SDK initializes without throwing
- ✅ shutdownTracing() exported

### Step 2.2.2: Create Tracing Utilities ⏸️ READY
**File**: `src/infrastructure/tracing.ts`

**Task**: Helper functions for manual span creation

**Content**: Use implementation from Research Agent 2

**Key Features**:
- startToolSpan() - for MCP tools
- startBackendSpan() - for API calls
- recordSpanSuccess/Error() helpers
- Semantic attributes constants

**Validation After**:
```bash
npm run build
node -e "import('./dist/infrastructure/tracing.js').then(m => console.log('Exports:', Object.keys(m)))"
```

**Success Criteria**:
- ✅ File created (~200 lines)
- ✅ All helper functions export
- ✅ No import errors

### Step 2.2.3: Update Logger with Trace Context ⚠️ CRITICAL
**File**: `src/infrastructure/logger.ts` (UPDATE)

**Task**: Add automatic trace_id/span_id injection

**Changes Required**:
1. Import OpenTelemetry API
2. Add getTraceContext() function
3. Add traceContextMixin to Pino config
4. Update log methods to include trace context

**Validation After**:
```bash
npm run build
# Check that logger compiles with new imports
node -e "import('./dist/infrastructure/logger.js').then(m => console.log('logger exported:', !!m.logger))"
```

**Success Criteria**:
- ✅ Compiles without errors
- ✅ Logger still works (no breaking changes)
- ✅ Trace context mixin added

### Step 2.2.4: Update Main Entry Point - Import Instrumentation FIRST ⚠️ CRITICAL
**File**: `src/index.ts` (UPDATE)

**Task**: Add instrumentation import as VERY FIRST LINE

**Changes Required**:
```typescript
/**
 * CRITICAL: Import instrumentation FIRST before everything else
 */
import './instrumentation.js';

// NOW import everything else
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
// ... rest of imports
```

**Add to bootstrap()**:
```typescript
// Register tracing shutdown
if (config.TRACING_ENABLED) {
  const { shutdownTracing } = await import('./instrumentation.js');
  shutdownService.registerResource("tracing", async () => {
    logger.info("Shutting down OpenTelemetry tracing");
    await shutdownTracing();
  });
}
```

**Validation After**:
```bash
# Critical test - tracing MUST initialize before other code
TRACING_ENABLED=true OTEL_DEBUG=true npm run dev 2>&1 | head -20
# Should see OpenTelemetry initialization logs FIRST
```

**Success Criteria**:
- ✅ instrumentation.js imported FIRST
- ✅ Server starts without errors
- ✅ OpenTelemetry SDK initializes
- ✅ Tracing shutdown registered

### Step 2.2.5: Add Tool Span Wrappers ⏸️ READY
**Files**: Tool registration files (e.g., `src/features/tasks/register.ts`)

**Task**: Wrap tool executions with tracing spans

**Changes Required**:
1. Import tracing utilities
2. Wrap each tool handler with startToolSpan()
3. Record success/failure

**Validation After**:
```bash
# Start server with tracing
TRACING_ENABLED=true npm run dev
# Execute a tool and check logs for trace_id
```

**Success Criteria**:
- ✅ At least one tool wrapped with spans
- ✅ Trace IDs appear in logs
- ✅ No errors during tool execution

---

## Phase 2.3: Circuit Breaker Pattern (50 minutes)

### Step 2.3.1: Create Circuit Breaker Service ⏸️ READY
**File**: `src/services/circuit-breaker.ts`

**Task**: Opossum-based circuit breaker implementation

**Content**: Use complete implementation from Research Agent 3

**Key Features**:
- CircuitBreakerService class
- Event emission (open, close, halfOpen, success, failure, reject)
- Configurable thresholds
- Metrics integration

**Validation After**:
```bash
npm run build
node -e "import('./dist/services/circuit-breaker.js').then(m => console.log('createCircuitBreaker exported:', !!m.createCircuitBreaker))"
```

**Success Criteria**:
- ✅ File created (~300 lines)
- ✅ Compiles without errors
- ✅ createCircuitBreaker() exports

### Step 2.3.2: Create Fallback Cache (LRU) ⏸️ READY
**File**: `src/services/fallback-cache.ts`

**Task**: LRU cache for last successful responses

**Content**: Use implementation from Research Agent 3

**Key Features**:
- FallbackCache class with LRU eviction
- TTL support (5 minutes default)
- Pattern-based invalidation
- Cache metrics (hits, misses, evictions)

**Validation After**:
```bash
npm run build
node -e "import('./dist/services/fallback-cache.js').then(m => console.log('FallbackCache exported:', !!m.FallbackCache))"
```

**Success Criteria**:
- ✅ File created (~250 lines)
- ✅ Compiles without errors
- ✅ FallbackCache and cacheKeys export

### Step 2.3.3: Create Circuit Breaker Backend Client Wrapper ⏸️ READY
**File**: `src/backend/client-with-circuit-breaker.ts`

**Task**: Wrap BackendClient with circuit breaker protection

**Content**: Use implementation from Research Agent 3

**Key Features**:
- CircuitBreakerBackendClient class
- Individual breakers per operation
- Read operations: cache fallback
- Write operations: fail fast
- Cache invalidation on writes

**Validation After**:
```bash
npm run build
node -e "import('./dist/backend/client-with-circuit-breaker.js').then(m => console.log('circuitBreakerBackendClient exported:', !!m.circuitBreakerBackendClient))"
```

**Success Criteria**:
- ✅ File created (~500 lines)
- ✅ Compiles without errors
- ✅ circuitBreakerBackendClient exports

### Step 2.3.4: Integrate Circuit Breaker into Features ⏸️ READY
**Files**: Feature registration files (UPDATE)

**Task**: Replace backendClient with circuitBreakerBackendClient

**Changes Required**:
```typescript
// Before:
import { backendClient } from '../../backend/client.js';

// After:
import { circuitBreakerBackendClient } from '../../backend/client-with-circuit-breaker.js';

// Use circuitBreakerBackendClient instead of backendClient
```

**Validation After**:
```bash
npm run build
# Test with backend down - should use fallback cache
```

**Success Criteria**:
- ✅ All features use circuit breaker client
- ✅ Server starts without errors
- ✅ Fallback cache serves stale data when backend down

---

## Phase 2.4: Request ID Propagation (40 minutes)

### Step 2.4.1: Create Request Context Store ⏸️ READY
**File**: `src/infrastructure/requestContextStore.ts`

**Task**: AsyncLocalStorage for request context

**Content**: Use implementation from Research Agent 4

**Key Features**:
- RequestContextStore class (singleton)
- AsyncLocalStorage integration
- run() and runAsync() methods
- Context getters/setters

**Validation After**:
```bash
npm run build
node -e "import('./dist/infrastructure/requestContextStore.js').then(m => console.log('requestContextStore exported:', !!m.requestContextStore))"
```

**Success Criteria**:
- ✅ File created (~100 lines)
- ✅ Compiles without errors
- ✅ requestContextStore singleton exports

### Step 2.4.2: Update Logger with Request ID Mixin ⏸️ READY
**File**: `src/infrastructure/logger.ts` (UPDATE)

**Task**: Automatic request_id injection in all logs

**Changes Required**:
1. Import requestContextStore
2. Add getCurrentContext() call in log methods
3. Merge request context into log data automatically

**Validation After**:
```bash
npm run build
# Start server and check logs for request_id
npm run dev 2>&1 | grep "request_id"
```

**Success Criteria**:
- ✅ Compiles without errors
- ✅ request_id appears in logs automatically
- ✅ No manual context passing required

### Step 2.4.3: Add HTTP Request ID Middleware ⏸️ READY
**File**: `src/transports/http.ts` (UPDATE - if HTTP transport exists)

**Task**: Extract/generate X-Request-ID header

**Changes Required**:
1. Add middleware to extract X-Request-ID
2. Generate UUID if not provided
3. Store in request context
4. Add to response headers

**Validation After**:
```bash
# Test with HTTP transport
TASKMAN_MCP_TRANSPORT=http npm run dev &
curl -H "X-Request-ID: test-123" http://localhost:3000/health/ready -i | grep "X-Request-ID"
```

**Success Criteria**:
- ✅ X-Request-ID extracted from request
- ✅ X-Request-ID added to response
- ✅ request_id in logs matches header

### Step 2.4.4: Update Backend Client for Request ID Propagation ⏸️ READY
**File**: `src/backend/client.ts` (UPDATE)

**Task**: Add X-Request-ID to all backend API calls

**Changes Required**:
1. Import requestContextStore
2. Add axios request interceptor
3. Inject X-Request-ID header from context

**Validation After**:
```bash
npm run build
# Visual inspection of axios interceptors
```

**Success Criteria**:
- ✅ Compiles without errors
- ✅ Request ID propagated to backend
- ✅ No breaking changes

---

## Phase 2.5: Integration & Testing (30 minutes)

### Step 2.5.1: Full Server Startup Test ⏸️ READY
**Test**: Start server with all Phase 2 features enabled

**Command**:
```bash
# Set all Phase 2 env vars
METRICS_ENABLED=true \
TRACING_ENABLED=true \
CIRCUIT_BREAKER_ENABLED=true \
FALLBACK_CACHE_ENABLED=true \
npm run dev
```

**Validation**:
```bash
# Should see in startup logs:
# - OpenTelemetry SDK initialized
# - Metrics service initialized
# - System metrics collector started
# - Circuit breakers registered
# - Server started successfully
```

**Success Criteria**:
- ✅ Server starts without errors
- ✅ All Phase 2 services initialize
- ✅ No import errors
- ✅ Graceful shutdown works

### Step 2.5.2: Metrics Endpoint Test ⏸️ READY
**Test**: Verify Prometheus metrics export

**Command**:
```bash
# If HTTP transport available
TASKMAN_MCP_TRANSPORT=http npm run dev &
sleep 5
curl http://localhost:3000/metrics > /tmp/metrics.txt
cat /tmp/metrics.txt | grep "taskman_"
```

**Expected Output**:
```
taskman_http_requests_total
taskman_mcp_tool_executions_total
taskman_backend_api_calls_total
taskman_memory_usage_bytes
taskman_health_check_status
...
```

**Success Criteria**:
- ✅ /metrics endpoint responds 200
- ✅ Prometheus format valid
- ✅ All taskman_ metrics present
- ✅ Metric values reasonable

### Step 2.5.3: Tracing Integration Test ⏸️ READY
**Test**: Verify OpenTelemetry tracing works

**Command**:
```bash
# Start Jaeger locally (optional)
docker run -d --name jaeger -p 4318:4318 -p 16686:16686 jaegertracing/all-in-one

# Start server with tracing
TRACING_ENABLED=true \
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318/v1/traces \
npm run dev
```

**Validation**:
```bash
# Check logs for trace_id
grep "trace_id" logs/*.log

# Check Jaeger UI (if running)
open http://localhost:16686
```

**Success Criteria**:
- ✅ Traces exported to OTLP endpoint
- ✅ trace_id and span_id in logs
- ✅ Trace context propagates across operations
- ✅ Jaeger shows traces (if available)

### Step 2.5.4: Circuit Breaker Test ⏸️ READY
**Test**: Verify circuit breaker protects against failures

**Command**:
```bash
# Start server with circuit breaker
CIRCUIT_BREAKER_ENABLED=true npm run dev

# Simulate backend failure by stopping backend or using invalid endpoint
TASK_MANAGER_API_ENDPOINT=http://localhost:9999/api/v1 npm run dev
```

**Expected Behavior**:
1. First few requests fail (circuit closed)
2. After 50% error rate, circuit opens
3. Subsequent requests use fallback cache
4. After 30 seconds, circuit tries half-open
5. If successful, circuit closes

**Success Criteria**:
- ✅ Circuit opens after threshold
- ✅ Fallback cache serves stale data
- ✅ Circuit recovers automatically
- ✅ Metrics show circuit state changes

### Step 2.5.5: Request ID Propagation Test ⏸️ READY
**Test**: Verify request ID flows through entire system

**Command**:
```bash
npm run dev

# Execute any operation and check logs
# request_id should be consistent across all log entries for that operation
```

**Validation**:
```bash
# All logs from same request should have same request_id
grep "request_id" logs/*.log | grep "<specific-request-id>"
```

**Success Criteria**:
- ✅ request_id generated for all operations
- ✅ request_id consistent across log entries
- ✅ request_id propagated to backend calls
- ✅ X-Request-ID in HTTP responses

---

## Phase 2.6: Documentation & Cleanup (20 minutes)

### Step 2.6.1: Update .env.example ⏸️ READY
**File**: `.env.example`

**Task**: Add all Phase 2 environment variables

**Changes Required**:
```bash
# Phase 2: Observability & Resilience
METRICS_ENABLED=true
TRACING_ENABLED=false
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318/v1/traces
OTEL_DEBUG=false
OTEL_SAMPLE_RATE=1.0

# Circuit Breaker
CIRCUIT_BREAKER_ENABLED=true
CIRCUIT_BREAKER_ERROR_THRESHOLD=50
CIRCUIT_BREAKER_RESET_TIMEOUT_MS=30000
CIRCUIT_BREAKER_VOLUME_THRESHOLD=10

# Fallback Cache
FALLBACK_CACHE_ENABLED=true
FALLBACK_CACHE_MAX_SIZE=1000
FALLBACK_CACHE_TTL_MS=300000
```

**Success Criteria**:
- ✅ All Phase 2 variables documented
- ✅ Descriptions clear
- ✅ Default values match schema

### Step 2.6.2: Update README.md ⏸️ READY
**File**: `README.md`

**Task**: Document Phase 2 features

**Sections to Add**:
- Observability (Metrics & Tracing)
- Circuit Breaker & Resilience
- Request Tracking
- Monitoring Setup (Prometheus + Jaeger)

**Success Criteria**:
- ✅ README updated
- ✅ Examples provided
- ✅ Setup instructions clear

### Step 2.6.3: Create Phase 2 Completion Report ⏸️ READY
**File**: `PHASE-2-COMPLETION-REPORT.md`

**Task**: Document implementation results

**Content**:
- Implementation summary
- Test results
- Production readiness assessment
- Next steps (Phase 3?)

**Success Criteria**:
- ✅ Report created
- ✅ All tests documented
- ✅ Metrics captured

---

## Final Validation Checklist ✅

Before marking Phase 2 complete, verify ALL of these:

### Code Quality
- [ ] All TypeScript files compile without errors
- [ ] No ESLint warnings in new files
- [ ] All imports use correct paths (.js extensions)
- [ ] No unused imports or variables

### Functionality
- [ ] Server starts successfully with all features enabled
- [ ] Server starts successfully with features disabled
- [ ] Graceful shutdown works correctly
- [ ] All Phase 1 functionality still works

### Metrics
- [ ] /metrics endpoint returns valid Prometheus format
- [ ] All 18 metrics present
- [ ] Metrics update correctly during operation
- [ ] System metrics collector runs

### Tracing
- [ ] OpenTelemetry SDK initializes first
- [ ] trace_id appears in logs
- [ ] Traces export to OTLP endpoint
- [ ] Jaeger shows spans (if available)

### Circuit Breaker
- [ ] Circuit opens after error threshold
- [ ] Fallback cache serves stale data
- [ ] Circuit recovers automatically
- [ ] Write operations fail fast

### Request Tracking
- [ ] request_id generated for all operations
- [ ] request_id consistent across operation
- [ ] X-Request-ID propagated to backend
- [ ] X-Request-ID in HTTP responses

### Documentation
- [ ] .env.example updated
- [ ] README.md updated
- [ ] Completion report created
- [ ] All tests documented

### Production Readiness
- [ ] No breaking changes to existing APIs
- [ ] Configuration backward compatible
- [ ] Performance acceptable (< 5% overhead)
- [ ] Memory usage reasonable

---

## Success Metrics

### Before Phase 2: 90%
| Category | Score |
|----------|-------|
| Graceful Shutdown | 95% |
| Logging | 95% |
| Health Checks | 100% |
| Configuration | 90% |
| Metrics | 0% |
| Tracing | 0% |
| Circuit Breaker | 0% |
| Request Tracking | 30% |
| **TOTAL** | **90%** |

### After Phase 2 Target: 98%
| Category | Score Target |
|----------|--------------|
| Graceful Shutdown | 95% |
| Logging | 100% (with trace context) |
| Health Checks | 100% |
| Configuration | 95% |
| Metrics | 100% |
| Tracing | 100% |
| Circuit Breaker | 100% |
| Request Tracking | 100% |
| **TOTAL** | **98%** |

---

## Time Estimates

| Phase | Estimated | Status |
|-------|-----------|--------|
| 2.0: Configuration | 15 min | Pending |
| 2.1: Metrics | 45 min | Pending |
| 2.2: Tracing | 60 min | Pending |
| 2.3: Circuit Breaker | 50 min | Pending |
| 2.4: Request ID | 40 min | Pending |
| 2.5: Integration & Testing | 30 min | Pending |
| 2.6: Documentation | 20 min | Pending |
| **TOTAL** | **4 hours** | **0% Complete** |

---

## Execution Notes

**Parallel Execution Opportunities**:
- Step 2.1.1 and 2.1.2 can run in parallel
- Step 2.3.1 and 2.3.2 can run in parallel
- File creation steps can be batched

**Critical Path**:
1. Configuration (blocks everything)
2. Instrumentation.ts (must be imported first)
3. Update src/index.ts (integrates everything)

**Rollback Plan**:
- Keep Phase 1 working throughout
- Each phase is independent (can be disabled via config)
- Git commit after each major step

**Testing Strategy**:
- Validate after EVERY step (no skipping)
- Test with features enabled AND disabled
- Performance testing on final integration

---

**Checklist Generated**: November 7, 2025
**Ready for Execution**: ✅ YES
**Next Action**: Begin Step 2.0.1 - Update Configuration Schema
