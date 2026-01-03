# Enhanced Implementation Plan: TaskMan MCP Server v2 Stability Improvements

**Version:** 2.0
**Date:** 2025-11-06
**Status:** Ready for Implementation
**Based On:** STABILITY-IMPROVEMENT-RESEARCH.md, PHASE-0-VALIDATION-REPORT.md

---

## Executive Summary

This enhanced implementation plan addresses **22 stability improvements** across 4 major phases, with **comprehensive testing**, **validation gates**, and **architectural documentation** at each step.

**Timeline:** 28-41 days (with 20% buffer)
**Approach:** Iterative cycles with checkpoint gates
**Validation:** Phase 0 baseline established before implementation begins

### Critical Finding from Phase 0
**Status:** ❌ **BLOCKED - CRITICAL ISSUES**

Phase 0 validation (completed 2025-11-06) revealed:
- **CRITICAL-001:** 9 missing devDependencies blocking all development
- **HIGH-001:** 60+ TypeScript compilation errors
- **Remediation Required:** Install dependencies and fix compilation before proceeding

**Go/No-Go Decision:** Implementation **cannot proceed** until Phase 0 checkpoint passes.

---

## Phase 0: Pre-Implementation Validation & Remediation

**Duration:** 2-3 days
**Purpose:** Establish working baseline before improvements begin
**Status:** ❌ Failed initial validation - remediation required

### 0.1 Dependency Restoration (Day 0.1)

**Objective:** Install all missing devDependencies

**Tasks:**
1. Clean install to resolve dependency conflicts:
   ```bash
   cd TaskMan-v2/mcp-server-ts
   rm -rf node_modules package-lock.json
   npm install
   ```

2. Verify installation:
   ```bash
   npm list --depth=0
   # Expected: NO "UNMET DEPENDENCY" messages
   ```

3. Document installed versions:
   ```bash
   npm list --depth=0 > docs/dependency-baseline.txt
   ```

**Missing Packages (9 total):**
- typescript@^5.9.3
- vitest@^4.0.3
- tsx@^4.20.6
- @types/node@^24.9.1
- @types/express@^5.0.5
- @types/supertest@^6.0.3
- @vitest/coverage-v8@^4.0.3
- @vitest/ui@^4.0.3
- supertest@^7.1.4

**Success Criteria:**
- ✅ All dependencies installed
- ✅ No UNMET warnings in npm list
- ✅ node_modules populated correctly

---

### 0.2 TypeScript Compilation Fixes (Day 0.2-0.3)

**Objective:** Resolve 60+ compilation errors preventing build

**Error Categories (in priority order):**

#### **Priority 1: Infrastructure Errors (Critical)**

**1. Pino Logger Initialization (1 error)**
- **Location:** src/infrastructure/logger.ts:29
- **Error:** `TS2349: This expression is not callable`
- **Investigation Needed:** Pino v8 API compatibility
- **Fix Options:**
  - Research Pino v8 changelog for breaking changes
  - Test alternative import patterns: `pino.default()`, `import pino from 'pino'`
  - Consider downgrade to Pino v7 if v8 incompatible

**2. Missing Type Imports (2 errors)**
- **Location:** src/backend/client.ts:1344-1345
- **Error:** `Cannot find name 'ActionListStatus'`, `'ActionListPriority'`
- **Fix:**
  ```typescript
  import { ActionListStatus, ActionListPriority } from "../core/types.js";
  ```

**3. Generic Type Unwrapping (6 errors)**
- **Location:** src/backend/client.ts (multiple methods)
- **Error:** `Property 'query' does not exist on type 'ApiEnvelope<T>'`
- **Root Cause:** Axios response typing or ApiEnvelope definition mismatch
- **Investigation Required:**
  - Review ApiEnvelope<T> interface definition
  - Check axios response interceptors
  - May need explicit type unwrapping in methods

#### **Priority 2: Test Infrastructure (15 errors)**
- **Errors:** `Cannot find name 'vi'`, `Cannot find module 'supertest'`
- **Expected Resolution:** Installing vitest/supertest should auto-resolve
- **Post-Install Verification Required**

#### **Priority 3: Health Check Types (26 errors)**
- **Location:** src/features/health-checks/handlers.ts
- **Pattern:** Nullable array handling, type assertions
- **Fix Strategy:** Add null checks, proper type guards

#### **Priority 4: Nullable Arrays (3 errors)**
- **Fix:** Add `|| []` null coalescing operators where needed

#### **Priority 5: Schema Shape Access (1 error)**
- **Location:** src/features/action-lists/register.ts:441
- **Error:** `.shape` on refined Zod schema (ZodEffects limitation)
- **Fix:** Access `.shape` before applying `.refine()`

**Success Criteria:**
- ✅ `npm run typecheck` exits with code 0
- ✅ `npm run build` completes successfully
- ✅ dist/ directory generated with .js files
- ✅ No TypeScript errors in console output

---

### 0.3 Test Framework Validation (Day 0.3)

**Objective:** Confirm test suite can execute

**Tasks:**
1. Run test suite:
   ```bash
   npm test
   ```

2. Verify test framework loads:
   - Vitest initializes
   - Test files discovered
   - Tests can run (failures acceptable, framework errors not acceptable)

3. Check test coverage baseline:
   ```bash
   npm run test:coverage
   ```

4. Document baseline metrics:
   ```markdown
   ## Test Baseline (Phase 0)
   - Total test files: X
   - Tests passing: Y
   - Tests failing: Z
   - Coverage: N%
   ```

**Success Criteria:**
- ✅ Vitest framework loads without errors
- ✅ At least 1 test file executes successfully
- ✅ Coverage report generates (even if coverage is low)
- ✅ No "Cannot find module" errors in test output

---

### 0.4 Baseline Documentation (Day 0.3)

**Objective:** Document current state for comparison

**Create:** `docs/BASELINE-METRICS.md`

**Contents:**
```markdown
# Baseline Metrics (Phase 0 - Post-Remediation)

**Date:** YYYY-MM-DD
**Commit:** [git SHA]

## Build & Compilation
- TypeScript version: 5.9.3
- Compilation time: X seconds
- Build artifacts size: Y MB

## Testing
- Test files: N
- Unit tests: X passing / Y total
- Integration tests: X passing / Y total
- Coverage: N% (target: 90% for critical paths)

## Dependencies
- Runtime dependencies: 8
- Dev dependencies: 9
- Total packages (with transitive): ~N

## Performance (if measurable)
- Server startup time: X ms
- Tool registration time: Y ms
- Memory usage (idle): Z MB

## Known Issues
- [List any remaining non-blocking issues]
```

**Success Criteria:**
- ✅ Baseline metrics documented
- ✅ All metrics measurable and reproducible

---

### **CHECKPOINT GATE 0: Ready to Implement**

**Validation Criteria:**
- ✅ All dependencies installed (0 UNMET)
- ✅ TypeScript compilation passes (0 errors)
- ✅ Build succeeds and generates dist/
- ✅ Test suite runs (framework works)
- ✅ Baseline metrics documented

**Go Decision:** Proceed to Phase 1
**No-Go Decision:** Remediate issues, re-validate

**Estimated Remediation Time:** 0.5-1 day if issues found

---

## Phase 1: Operational Stability (Days 1-7)

**Focus:** Core reliability improvements
**Testing:** 70% unit, 20% integration, 10% E2E

### 1.1 Structured Logging Implementation (Days 1-2)

**Improvements:**
- [CRITICAL-001] Pino structured logging (already implemented, validate)
- [HIGH-001] Audit logging with correlation IDs
- [MEDIUM-001] Log rotation and retention

**Implementation Cycle:**

#### Research (0.5 days)
- Review Pino v8 best practices
- Research correlation ID propagation patterns
- Investigate log rotation libraries (pino-roll, rotating-file-stream)

**ADR Required:** ADR-001-Structured-Logging-Strategy.md
- Why Pino over Winston/Bunyan
- Correlation ID format (UUID v4 vs custom)
- Retention policy (30 days, 90 days?)
- Log levels per environment

#### Implementation (0.75 days)
1. Fix Pino initialization (from Phase 0 findings)
2. Add correlation ID middleware/context
3. Implement audit log writer (separate from main logs)
4. Configure log rotation (production only)

**Code Changes:**
```typescript
// src/infrastructure/logger.ts
export function withCorrelationLogger(correlationId: string): pino.Logger {
  return logger.child({ correlationId });
}

// src/infrastructure/audit-logger.ts (NEW)
export const auditLogger = pino({
  transport: {
    target: 'pino/file',
    options: { destination: './logs/audit.log' }
  }
});
```

#### Testing (0.5 days)
**Unit Tests (src/infrastructure/logger.test.ts):**
- ✅ Logger creates child with correlation ID
- ✅ Sensitive fields redacted (password, token, apiKey)
- ✅ Log levels respect NODE_ENV
- ✅ Audit logger writes to separate file

**Integration Tests:**
- ✅ Correlation ID propagates through tool call chain
- ✅ Request → Tool → Backend → Response carries same ID

**Coverage Target:** ≥90% for logger.ts

#### Validation (0.25 days)
- Run server in dev mode, verify pretty logs
- Run server in production mode, verify JSON logs
- Check audit.log file created and written to
- Verify log rotation triggers (if applicable)

**Success Metrics:**
- ✅ All logs JSON-structured in production
- ✅ Correlation IDs in 100% of requests
- ✅ Audit logs separate from application logs
- ✅ No performance degradation (< 1ms overhead per log)

---

### 1.2 Error Handling & Recovery (Days 2-3)

**Improvements:**
- [HIGH-002] Standardized error responses
- [MEDIUM-002] Graceful degradation patterns
- [LOW-001] Connection retry logic (already implemented, enhance)

**Implementation Cycle:**

#### Research (0.25 days)
- Review MCP SDK error handling patterns
- Research circuit breaker implementations (opossum)
- Study graceful degradation strategies

**ADR Required:** ADR-002-Error-Handling-Strategy.md
- Error classification (retryable vs fatal)
- Circuit breaker thresholds
- Fallback behavior per tool

#### Implementation (1 day)
1. Create standardized error types:
   ```typescript
   // src/core/errors.ts (NEW)
   export class BackendUnavailableError extends Error {
     code = 'BACKEND_UNAVAILABLE';
     retryable = true;
   }
   ```

2. Implement circuit breaker:
   ```typescript
   // src/infrastructure/circuit-breaker.ts (NEW)
   import CircuitBreaker from 'opossum';

   export const backendCircuitBreaker = new CircuitBreaker(
     backendClient.request,
     {
       timeout: 5000,
       errorThresholdPercentage: 50,
       resetTimeout: 30000
     }
   );
   ```

3. Add graceful degradation to each tool:
   ```typescript
   // Example: task_get tool
   try {
     return await backendCircuitBreaker.fire(request);
   } catch (error) {
     if (error.code === 'BACKEND_UNAVAILABLE') {
       return cachedTask || { error: 'Backend unavailable, retry later' };
     }
     throw error;
   }
   ```

**New Dependencies:**
- opossum@^6.0.0 (circuit breaker)

#### Testing (1.5 days)
**Unit Tests (src/core/errors.test.ts):**
- ✅ Custom error types serialize correctly
- ✅ Error classification (retryable vs fatal)

**Unit Tests (src/infrastructure/circuit-breaker.test.ts):**
- ✅ Circuit opens after threshold
- ✅ Circuit resets after timeout
- ✅ Half-open state handles probe requests

**Integration Tests (src/backend/client.integration.test.ts):**
- ✅ Retry logic for 429, 503 status codes
- ✅ Circuit breaker prevents cascading failures
- ✅ Graceful degradation returns cached data

**E2E Tests:**
- ✅ Backend down scenario: Tools return graceful errors
- ✅ Backend slow scenario: Timeouts respected
- ✅ Backend recovered scenario: Circuit closes

**Coverage Target:** ≥95% for error handling code

#### Validation (0.25 days)
- Simulate backend downtime (stop backend server)
- Verify circuit breaker opens
- Verify tools return graceful errors (not crashes)
- Verify circuit closes when backend recovers

**Success Metrics:**
- ✅ 0 unhandled exceptions during backend downtime
- ✅ Circuit breaker metrics available
- ✅ Mean time to detect (MTTD) backend failure < 5 seconds
- ✅ Mean time to recover (MTTR) < 30 seconds

---

### 1.3 Resource Management (Days 4-5)

**Improvements:**
- [CRITICAL-002] Connection pooling
- [HIGH-003] Memory leak prevention
- [MEDIUM-003] Request timeout enforcement

**Implementation Cycle:**

#### Research (0.5 days)
- Review axios connection pool configuration
- Research Node.js memory leak detection (clinic.js, heapdump)
- Study timeout strategies (per-request, global)

**ADR Required:** ADR-003-Connection-Pool-Configuration.md
- Pool size (maxSockets)
- Keep-alive settings
- Timeout values per operation type

#### Implementation (1 day)
1. Configure axios connection pool:
   ```typescript
   // src/backend/client.ts
   import http from 'http';
   import https from 'https';

   const httpAgent = new http.Agent({
     keepAlive: true,
     maxSockets: 10,
     maxFreeSockets: 5,
     timeout: 60000,
     keepAliveMsecs: 30000
   });

   axios.create({
     httpAgent,
     httpsAgent: new https.Agent({ /* same config */ })
   });
   ```

2. Add request timeout wrapper:
   ```typescript
   // src/infrastructure/timeout.ts (NEW)
   export async function withTimeout<T>(
     promise: Promise<T>,
     timeoutMs: number,
     operationName: string
   ): Promise<T> {
     return Promise.race([
       promise,
       new Promise<T>((_, reject) =>
         setTimeout(
           () => reject(new TimeoutError(operationName, timeoutMs)),
           timeoutMs
         )
       )
     ]);
   }
   ```

3. Add memory monitoring:
   ```typescript
   // src/infrastructure/memory-monitor.ts (NEW)
   setInterval(() => {
     const usage = process.memoryUsage();
     if (usage.heapUsed > THRESHOLD) {
       logger.warn({ memoryUsage: usage }, 'High memory usage detected');
     }
   }, 60000);
   ```

**New Dependencies:**
- clinic@^13.0.0 (dev dependency, memory profiling)

#### Testing (1.25 days)
**Unit Tests (src/infrastructure/timeout.test.ts):**
- ✅ Timeout triggers after specified duration
- ✅ Fast operations complete before timeout
- ✅ Timeout error includes operation name

**Integration Tests:**
- ✅ Connection pool limits concurrent requests
- ✅ Keep-alive connections reused
- ✅ Stale connections cleaned up

**Load Tests (NEW):**
- ✅ 100 concurrent requests handled without OOM
- ✅ Memory usage stable over 10-minute load test
- ✅ No connection leaks after 1000 requests

**Coverage Target:** ≥85% for resource management code

#### Validation (0.25 days)
- Run load test: `npm run test:load` (create script)
- Monitor memory usage: `clinic doctor -- node dist/index.js`
- Verify connection pool metrics
- Check for EventEmitter leaks

**Success Metrics:**
- ✅ Memory growth < 10MB per 1000 requests
- ✅ Connection pool size stable (no leaks)
- ✅ Request timeouts enforced (0 hung requests)
- ✅ No EventEmitter warnings

---

### 1.4 Input Validation (Days 5-6)

**Improvements:**
- [HIGH-004] Comprehensive Zod schemas (already implemented, enhance)
- [MEDIUM-004] Input sanitization
- [LOW-002] Field length limits

**Implementation Cycle:**

#### Research (0.25 days)
- Review Zod refinement capabilities
- Research input sanitization libraries (DOMPurify, validator.js)
- Study OWASP input validation guidelines

**ADR Required:** ADR-004-Input-Validation-Standards.md
- Validation library choice (Zod)
- Sanitization rules per field type
- Error message verbosity (security vs usability)

#### Implementation (0.75 days)
1. Enhance Zod schemas with length limits:
   ```typescript
   // src/features/tasks/schemas.ts
   export const taskCreateSchema = z.object({
     title: z.string().min(1).max(200),
     description: z.string().max(5000).optional(),
     tags: z.array(z.string().max(50)).max(20).optional()
   });
   ```

2. Add input sanitization:
   ```typescript
   // src/infrastructure/sanitizer.ts (NEW)
   import validator from 'validator';

   export function sanitizeString(input: string): string {
     return validator.trim(validator.escape(input));
   }
   ```

3. Apply to all tool handlers:
   ```typescript
   // Example: task_create handler
   const sanitizedTitle = sanitizeString(input.title);
   const validated = taskCreateSchema.parse({
     ...input,
     title: sanitizedTitle
   });
   ```

**New Dependencies:**
- validator@^13.11.0

#### Testing (0.75 days)
**Unit Tests (src/infrastructure/sanitizer.test.ts):**
- ✅ XSS payloads sanitized
- ✅ SQL injection attempts escaped
- ✅ Unicode normalization applied

**Unit Tests (per feature schema):**
- ✅ Length limits enforced
- ✅ Invalid formats rejected
- ✅ Optional fields handle null/undefined

**Fuzz Testing (NEW):**
- ✅ Random input doesn't crash server
- ✅ Deeply nested objects rejected
- ✅ Circular references rejected

**Coverage Target:** ≥95% for validation code

#### Validation (0.25 days)
- Run fuzz test suite
- Test with OWASP test vectors
- Verify error messages don't leak internals

**Success Metrics:**
- ✅ All OWASP input validation tests pass
- ✅ 0 crashes from malformed input
- ✅ Validation errors user-friendly
- ✅ No sensitive data in error messages

---

### 1.5 State Management (Days 6-7)

**Improvements:**
- [CRITICAL-003] Session state handling
- [HIGH-005] Cache invalidation
- [MEDIUM-005] Concurrency control (locking service already implemented)

**Implementation Cycle:**

#### Research (0.5 days)
- Review MCP session lifecycle
- Research cache invalidation strategies (TTL, event-based)
- Study distributed locking (Redlock algorithm)

**ADR Required:** ADR-005-State-Management-Strategy.md
- Session storage (in-memory vs persistent)
- Cache invalidation policy
- Lock timeout values

#### Implementation (1 day)
1. Implement session manager:
   ```typescript
   // src/infrastructure/session-manager.ts (NEW)
   export class SessionManager {
     private sessions = new Map<string, SessionState>();

     getOrCreate(sessionId: string): SessionState {
       if (!this.sessions.has(sessionId)) {
         this.sessions.set(sessionId, new SessionState());
       }
       return this.sessions.get(sessionId)!;
     }

     cleanup(sessionId: string): void {
       this.sessions.delete(sessionId);
     }
   }
   ```

2. Add cache with TTL:
   ```typescript
   // src/infrastructure/cache.ts (NEW)
   export class TTLCache<T> {
     private cache = new Map<string, { value: T; expiresAt: number }>();

     set(key: string, value: T, ttlMs: number): void {
       this.cache.set(key, {
         value,
         expiresAt: Date.now() + ttlMs
       });
     }

     get(key: string): T | undefined {
       const entry = this.cache.get(key);
       if (!entry || entry.expiresAt < Date.now()) {
         this.cache.delete(key);
         return undefined;
       }
       return entry.value;
     }
   }
   ```

3. Enhance locking service (already exists):
   ```typescript
   // src/infrastructure/locking-service.ts
   // Add: lock renewal, deadlock detection
   ```

#### Testing (1.25 days)
**Unit Tests (src/infrastructure/session-manager.test.ts):**
- ✅ Sessions created on demand
- ✅ Session cleanup removes data
- ✅ Concurrent session access handled

**Unit Tests (src/infrastructure/cache.test.ts):**
- ✅ TTL expiration works correctly
- ✅ Cache invalidation clears entries
- ✅ Cache hit/miss rates measurable

**Integration Tests:**
- ✅ Lock prevents concurrent task updates
- ✅ Lock timeout releases after 30 minutes
- ✅ Cache reduces backend calls (measure hit rate)

**Race Condition Tests (NEW):**
- ✅ Concurrent requests to same task handle locking
- ✅ No lost updates in race conditions

**Coverage Target:** ≥90% for state management code

#### Validation (0.25 days)
- Run concurrent request test: 10 requests to same task
- Verify only 1 writer at a time
- Check lock contention metrics
- Validate cache hit rate > 50% for repeated queries

**Success Metrics:**
- ✅ 0 lost updates in concurrent scenarios
- ✅ Cache hit rate > 50% for project/task queries
- ✅ Lock contention < 5% of requests
- ✅ Session cleanup prevents memory leaks

---

### **CHECKPOINT GATE 1: Operational Stability Achieved**

**Validation Criteria:**
- ✅ All Phase 1 tests passing (unit, integration, E2E)
- ✅ Test coverage ≥85% overall, ≥90% for critical paths
- ✅ 5 ADRs documented (ADR-001 through ADR-005)
- ✅ No high-severity bugs in backlog
- ✅ Performance baseline maintained (no regressions)
- ✅ Circuit breaker operational
- ✅ Memory leak tests passing

**Performance Benchmarks:**
- Server startup: < 2 seconds
- Tool registration: < 100ms
- Backend request (cached): < 10ms
- Backend request (uncached): < 500ms
- Memory usage (idle): < 100MB
- Memory growth: < 10MB per 1000 requests

**Go Decision:** Proceed to Phase 2
**No-Go Decision:** Fix failing tests, address high-severity bugs, re-validate

**Rollback Procedure:**
- Revert to Phase 0 baseline commit
- Restore previous dependencies (if changed)
- Document lessons learned

---

## Phase 2: Observability (Days 8-14)

**Focus:** Monitoring, metrics, and debugging capabilities
**Testing:** 70% unit, 30% integration

### 2.1 Health Checks (Days 8-9)

**Improvements:**
- [HIGH-006] Comprehensive health endpoints
- [MEDIUM-006] Dependency health monitoring
- [LOW-003] Graceful shutdown handling

**Implementation Cycle:**

#### Research (0.25 days)
- Review Kubernetes health check patterns (liveness, readiness, startup)
- Research health check libraries (lightship, terminus)

**ADR Required:** ADR-006-Health-Check-Design.md
- Health check types (liveness vs readiness)
- Dependency checks (backend, database, cache)
- Health check frequency

#### Implementation (1 day)
1. Fix existing health check types (from Phase 0 errors)
2. Implement /health/live endpoint:
   ```typescript
   // src/features/health-checks/handlers.ts
   export async function livenessProbe(): Promise<HealthCheckResult> {
     return { status: 'healthy', timestamp: new Date().toISOString() };
   }
   ```

3. Implement /health/ready endpoint:
   ```typescript
   export async function readinessProbe(): Promise<HealthCheckResult> {
     const backendHealthy = await checkBackendHealth();
     const dbHealthy = await checkDatabaseHealth();

     return {
       status: backendHealthy && dbHealthy ? 'healthy' : 'unhealthy',
       checks: { backend: backendHealthy, database: dbHealthy }
     };
   }
   ```

4. Implement graceful shutdown:
   ```typescript
   // src/index.ts
   process.on('SIGTERM', async () => {
     logger.info('SIGTERM received, starting graceful shutdown');
     await closeConnections();
     process.exit(0);
   });
   ```

#### Testing (1.5 days)
**Unit Tests:**
- ✅ Liveness probe always returns 200
- ✅ Readiness probe fails when backend down
- ✅ Graceful shutdown closes connections

**Integration Tests:**
- ✅ Health endpoints accessible via HTTP
- ✅ Backend health check makes real request
- ✅ Shutdown completes in-flight requests

**Coverage Target:** ≥90% for health check code

#### Validation (0.25 days)
- Test liveness: `curl http://localhost:3000/health/live`
- Test readiness: Stop backend, verify returns 503
- Test shutdown: Send SIGTERM, verify graceful exit

**Success Metrics:**
- ✅ Health endpoints respond in < 100ms
- ✅ Readiness accurately reflects backend state
- ✅ Graceful shutdown completes in < 5 seconds

---

### 2.2 Metrics & Telemetry (Days 9-11)

**Improvements:**
- [CRITICAL-004] Prometheus metrics (or equivalent)
- [HIGH-007] Request tracing with OpenTelemetry
- [MEDIUM-007] Performance instrumentation

**Implementation Cycle:**

#### Research (0.5 days)
- Review Prometheus best practices (metric naming, label cardinality)
- Research OpenTelemetry Node.js SDK
- Study distributed tracing patterns

**ADR Required:** ADR-007-Observability-Stack.md
- Metrics backend (Prometheus)
- Tracing backend (Jaeger, Zipkin, or cloud provider)
- Sampling strategy (always, rate-limited, or tail-based)

#### Implementation (1.5 days)
1. Add Prometheus metrics:
   ```typescript
   // src/infrastructure/metrics.ts (NEW)
   import { Registry, Counter, Histogram } from 'prom-client';

   export const registry = new Registry();

   export const requestCounter = new Counter({
     name: 'mcp_requests_total',
     help: 'Total MCP requests',
     labelNames: ['tool', 'status']
   });

   export const requestDuration = new Histogram({
     name: 'mcp_request_duration_seconds',
     help: 'MCP request duration',
     labelNames: ['tool'],
     buckets: [0.01, 0.05, 0.1, 0.5, 1, 5]
   });
   ```

2. Instrument tool handlers:
   ```typescript
   // Wrap each tool handler
   async function instrumentedHandler(handler: ToolHandler) {
     const end = requestDuration.startTimer({ tool: handler.name });
     try {
       const result = await handler();
       requestCounter.inc({ tool: handler.name, status: 'success' });
       return result;
     } catch (error) {
       requestCounter.inc({ tool: handler.name, status: 'error' });
       throw error;
     } finally {
       end();
     }
   }
   ```

3. Add OpenTelemetry tracing:
   ```typescript
   // src/infrastructure/tracing.ts (NEW)
   import { NodeSDK } from '@opentelemetry/sdk-node';
   import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';

   export const sdk = new NodeSDK({
     instrumentations: [getNodeAutoInstrumentations()]
   });
   ```

4. Expose /metrics endpoint:
   ```typescript
   // src/index.ts (HTTP transport)
   app.get('/metrics', async (req, res) => {
     res.set('Content-Type', registry.contentType);
     res.end(await registry.metrics());
   });
   ```

**New Dependencies:**
- prom-client@^15.1.0
- @opentelemetry/sdk-node@^1.19.0
- @opentelemetry/auto-instrumentations-node@^0.40.0

#### Testing (1.75 days)
**Unit Tests (src/infrastructure/metrics.test.ts):**
- ✅ Counters increment correctly
- ✅ Histograms record durations
- ✅ Metrics export in Prometheus format

**Integration Tests:**
- ✅ /metrics endpoint returns valid Prometheus format
- ✅ Request counts match actual requests
- ✅ Traces exported to backend (mock)

**Performance Tests:**
- ✅ Metrics overhead < 1ms per request
- ✅ No memory leaks from unbounded label cardinality

**Coverage Target:** ≥85% for observability code

#### Validation (0.25 days)
- Start server, make 100 requests
- Check /metrics endpoint shows mcp_requests_total=100
- Verify request duration buckets populated
- Check traces in Jaeger UI (if available)

**Success Metrics:**
- ✅ All tools instrumented
- ✅ Metrics overhead < 1% of request time
- ✅ Traces show end-to-end request flow
- ✅ Sampling rate configurable

---

### 2.3 Enhanced Logging (Days 11-12)

**Improvements:**
- [MEDIUM-008] Structured error context
- [LOW-004] Debug mode with verbose logging
- [LOW-005] Log sampling for high-volume operations

**Implementation Cycle:**

#### Research (0.25 days)
- Research log sampling strategies (rate-limiting, importance-based)
- Study structured error context patterns

**ADR Required:** ADR-008-Advanced-Logging-Patterns.md
- Log sampling algorithm
- Debug mode activation (env var, flag, or runtime toggle)
- Structured error context fields

#### Implementation (0.75 days)
1. Add log sampling:
   ```typescript
   // src/infrastructure/logger.ts
   export function sampledLogger(sampleRate: number): pino.Logger {
     return logger.child({
       shouldLog: Math.random() < sampleRate
     });
   }
   ```

2. Enhance error logging:
   ```typescript
   export function logError(
     error: Error,
     context: Record<string, unknown>
   ): void {
     logger.error({
       error: {
         message: error.message,
         stack: error.stack,
         code: (error as any).code,
         ...context
       }
     });
   }
   ```

3. Add debug mode:
   ```typescript
   if (process.env.DEBUG === 'true') {
     logger.level = 'trace';
   }
   ```

#### Testing (0.75 days)
**Unit Tests:**
- ✅ Log sampling respects rate
- ✅ Debug mode enables trace logs
- ✅ Error context includes all fields

**Integration Tests:**
- ✅ Sampled logs reduce volume by expected percentage
- ✅ Important logs never sampled (errors, audit)

**Coverage Target:** ≥90% for logging code

#### Validation (0.25 days)
- Enable debug mode: `DEBUG=true npm start`
- Verify trace logs visible
- Test log sampling with high request volume

**Success Metrics:**
- ✅ Debug mode increases log volume by 10x
- ✅ Log sampling reduces volume to target rate
- ✅ Error logs always include full context

---

### 2.4 Distributed Tracing (Days 12-13)

**Improvements:**
- [HIGH-008] Span propagation across services
- [MEDIUM-009] Custom span attributes
- [LOW-006] Trace sampling configuration

**Implementation Cycle:**

#### Research (0.25 days)
- Review W3C Trace Context specification
- Study OpenTelemetry semantic conventions

**ADR Required:** ADR-009-Distributed-Tracing-Strategy.md
- Trace ID format (W3C vs custom)
- Span naming conventions
- Sampling strategy per environment

#### Implementation (1 day)
1. Configure span propagation:
   ```typescript
   // src/infrastructure/tracing.ts
   import { W3CTraceContextPropagator } from '@opentelemetry/core';

   sdk.start({
     textMapPropagator: new W3CTraceContextPropagator()
   });
   ```

2. Add custom span attributes:
   ```typescript
   import { trace } from '@opentelemetry/api';

   const span = trace.getActiveSpan();
   span?.setAttributes({
     'mcp.tool.name': toolName,
     'mcp.task.id': taskId,
     'mcp.user.agent': userAgent
   });
   ```

3. Implement adaptive sampling:
   ```typescript
   // Sample 100% of errors, 10% of successes
   const sampler = (spanContext, traceId, spanKind, attributes) => {
     if (attributes['error']) {
       return { decision: SamplingDecision.RECORD_AND_SAMPLE };
     }
     return Math.random() < 0.1
       ? { decision: SamplingDecision.RECORD_AND_SAMPLE }
       : { decision: SamplingDecision.NOT_RECORD };
   };
   ```

#### Testing (1.5 days)
**Unit Tests:**
- ✅ Span attributes set correctly
- ✅ Trace context propagates to backend client
- ✅ Sampling respects configuration

**Integration Tests:**
- ✅ End-to-end trace includes all services
- ✅ Parent-child span relationships correct
- ✅ Error spans always sampled

**Coverage Target:** ≥85% for tracing code

#### Validation (0.25 days)
- Generate 1000 requests
- Check Jaeger UI for traces
- Verify sampling rate ~10% (excl. errors)
- Confirm span attributes visible

**Success Metrics:**
- ✅ 100% of requests have trace IDs
- ✅ Error spans sampled at 100%
- ✅ Success spans sampled at configured rate
- ✅ Trace context propagates to external services

---

### 2.5 Alerting & Notifications (Days 13-14)

**Improvements:**
- [MEDIUM-010] Alert rules for critical failures
- [LOW-007] Notification channels (email, Slack, PagerDuty)
- [LOW-008] Alert throttling/deduplication

**Implementation Cycle:**

#### Research (0.25 days)
- Review alerting best practices (Google SRE book)
- Research notification libraries (nodemailer, slack-notify)

**ADR Required:** ADR-010-Alerting-Strategy.md
- Alert severity levels
- Notification channels per severity
- Throttling/deduplication algorithm

#### Implementation (1 day)
1. Define alert rules:
   ```typescript
   // src/infrastructure/alerts.ts (NEW)
   export const alertRules = [
     {
       name: 'BackendDown',
       condition: () => circuitBreaker.isOpen(),
       severity: 'critical',
       channels: ['pagerduty', 'slack']
     },
     {
       name: 'HighErrorRate',
       condition: () => errorRate > 0.05,
       severity: 'warning',
       channels: ['slack']
     }
   ];
   ```

2. Implement alert manager:
   ```typescript
   export class AlertManager {
     async checkAndFire(): Promise<void> {
       for (const rule of alertRules) {
         if (rule.condition()) {
           await this.fireAlert(rule);
         }
       }
     }

     private async fireAlert(rule: AlertRule): Promise<void> {
       // Deduplicate: don't fire same alert within 5 minutes
       if (this.recentAlerts.has(rule.name)) return;

       this.recentAlerts.set(rule.name, Date.now());

       for (const channel of rule.channels) {
         await this.sendNotification(channel, rule);
       }
     }
   }
   ```

3. Add notification channels:
   ```typescript
   // src/infrastructure/notifiers/slack.ts (NEW)
   export async function sendSlackAlert(alert: Alert): Promise<void> {
     await fetch(process.env.SLACK_WEBHOOK_URL, {
       method: 'POST',
       body: JSON.stringify({
         text: `🚨 ${alert.severity.toUpperCase()}: ${alert.name}`,
         blocks: [{ type: 'section', text: { type: 'mrkdwn', text: alert.description } }]
       })
     });
   }
   ```

**New Dependencies:**
- nodemailer@^6.9.0 (optional, for email)

#### Testing (1.5 days)
**Unit Tests:**
- ✅ Alert conditions evaluate correctly
- ✅ Deduplication prevents spam
- ✅ Throttling respects time window

**Integration Tests:**
- ✅ Slack notifications sent (mock webhook)
- ✅ Email notifications sent (mock SMTP)
- ✅ PagerDuty alerts triggered (mock API)

**E2E Tests:**
- ✅ Trigger backend failure, verify alert fired
- ✅ Resolve issue, verify alert cleared

**Coverage Target:** ≥85% for alerting code

#### Validation (0.25 days)
- Trigger circuit breaker open
- Verify Slack alert received
- Trigger same alert again within 5 minutes
- Verify no duplicate notification

**Success Metrics:**
- ✅ Critical alerts fire within 60 seconds
- ✅ No duplicate alerts within deduplication window
- ✅ All notification channels operational
- ✅ Alert fatigue prevented (< 10 alerts/day)

---

### **CHECKPOINT GATE 2: Observability Complete**

**Validation Criteria:**
- ✅ All Phase 2 tests passing
- ✅ Test coverage ≥85% overall
- ✅ 5 more ADRs documented (ADR-006 through ADR-010)
- ✅ Health checks operational
- ✅ Metrics exposed and accurate
- ✅ Traces visible in backend
- ✅ Alerts fire correctly

**Observability Checklist:**
- ✅ /health/live endpoint responds
- ✅ /health/ready checks dependencies
- ✅ /metrics endpoint exports Prometheus format
- ✅ Traces exported to OpenTelemetry backend
- ✅ At least 3 alert rules configured
- ✅ Correlation IDs in all logs
- ✅ Structured logging operational

**Go Decision:** Proceed to Phase 3
**No-Go Decision:** Fix observability gaps, ensure monitoring operational, re-validate

**Rollback Procedure:**
- Revert to Phase 1 checkpoint commit
- Restore previous configuration
- Document observability issues

---

## Phase 3: Persistence & Reliability (Days 15-23)

**Focus:** Data persistence, backup, and recovery
**Testing:** 60% unit, 30% integration, 10% E2E

### 3.1 SQLite Integration (Days 15-17)

**Improvements:**
- [CRITICAL-005] SQLite persistent storage
- [HIGH-009] Migration framework
- [MEDIUM-011] Connection pooling (better-sqlite3 doesn't pool, but we can manage connections)

**Implementation Cycle:**

#### Research (0.5 days)
- Review better-sqlite3 best practices
- Research migration libraries (umzug, node-pg-migrate, custom)
- Study WAL mode benefits

**ADR Required:** ADR-011-Database-Strategy.md
- SQLite vs PostgreSQL vs other
- Migration framework (umzug)
- Backup strategy

**ADR Required:** ADR-012-Schema-Design.md
- Table structure
- Indexing strategy
- Normalization vs denormalization

#### Implementation (2 days)
1. Install dependencies:
   ```bash
   npm install better-sqlite3 umzug
   npm install -D @types/better-sqlite3
   ```

2. Create database client:
   ```typescript
   // src/infrastructure/database/client.ts (NEW)
   import Database from 'better-sqlite3';

   export const db = new Database('./data/taskman.db', {
     verbose: console.log
   });

   db.pragma('journal_mode = WAL');
   db.pragma('foreign_keys = ON');
   ```

3. Create migration framework:
   ```typescript
   // src/infrastructure/database/migrations.ts (NEW)
   import { Umzug, SequelizeStorage } from 'umzug';

   export const umzug = new Umzug({
     migrations: { glob: 'migrations/*.sql' },
     storage: new SequelizeStorage({ sequelize: db }),
     logger: logger
   });
   ```

4. Create initial migration:
   ```sql
   -- migrations/001_initial_schema.sql
   CREATE TABLE projects (
     id TEXT PRIMARY KEY,
     name TEXT NOT NULL,
     description TEXT,
     status TEXT NOT NULL,
     created_at TEXT NOT NULL,
     updated_at TEXT NOT NULL
   );

   CREATE TABLE tasks (
     id TEXT PRIMARY KEY,
     title TEXT NOT NULL,
     description TEXT,
     status TEXT NOT NULL,
     work_type TEXT NOT NULL,
     priority TEXT,
     project_id TEXT NOT NULL,
     created_at TEXT NOT NULL,
     updated_at TEXT NOT NULL,
     FOREIGN KEY (project_id) REFERENCES projects(id)
   );

   CREATE INDEX idx_tasks_project_id ON tasks(project_id);
   CREATE INDEX idx_tasks_status ON tasks(status);
   ```

5. Create repository pattern:
   ```typescript
   // src/infrastructure/database/repositories/task-repository.ts (NEW)
   export class TaskRepository {
     create(task: TaskCreate): TaskRecord {
       const stmt = db.prepare(`
         INSERT INTO tasks (id, title, status, project_id, created_at, updated_at)
         VALUES (?, ?, ?, ?, ?, ?)
       `);
       const id = crypto.randomUUID();
       const now = new Date().toISOString();
       stmt.run(id, task.title, task.status || 'new', task.project_id, now, now);
       return { id, ...task, created_at: now, updated_at: now };
     }

     findById(id: string): TaskRecord | undefined {
       const stmt = db.prepare('SELECT * FROM tasks WHERE id = ?');
       return stmt.get(id) as TaskRecord | undefined;
     }
   }
   ```

**New Dependencies:**
- better-sqlite3@^9.0.0
- umzug@^3.6.1

#### Testing (2.25 days)
**Unit Tests (src/infrastructure/database/repositories/task-repository.test.ts):**
- ✅ Create inserts task
- ✅ FindById retrieves task
- ✅ Update modifies task
- ✅ Delete soft-deletes task
- ✅ Foreign key constraints enforced

**Integration Tests:**
- ✅ Migrations run successfully
- ✅ WAL mode enabled
- ✅ Concurrent reads don't block
- ✅ Transaction rollback works

**Data Integrity Tests:**
- ✅ Crash during write doesn't corrupt DB
- ✅ Foreign key violations rejected
- ✅ Unique constraints enforced

**Coverage Target:** ≥90% for repository code

#### Validation (0.25 days)
- Run migrations: `npm run db:migrate`
- Verify tables created: `sqlite3 data/taskman.db ".tables"`
- Insert test data, query back
- Check WAL mode: `sqlite3 data/taskman.db "PRAGMA journal_mode;"`

**Success Metrics:**
- ✅ All migrations idempotent
- ✅ Database file created in ./data/
- ✅ Foreign keys enforced
- ✅ Indexes improve query performance (measure)

---

### 3.2 Backup & Recovery (Days 17-19)

**Improvements:**
- [HIGH-010] Automated backups
- [MEDIUM-012] Point-in-time recovery
- [LOW-009] Backup retention policy

**Implementation Cycle:**

#### Research (0.5 days)
- Review SQLite backup API
- Research backup strategies (full, incremental)
- Study restoration procedures

**ADR Required:** ADR-013-Backup-Strategy.md
- Backup frequency (hourly, daily)
- Retention policy (7 days, 30 days)
- Storage location (local, S3)

#### Implementation (1.5 days)
1. Create backup service:
   ```typescript
   // src/infrastructure/database/backup.ts (NEW)
   export class BackupService {
     async createBackup(): Promise<string> {
       const timestamp = new Date().toISOString().replace(/:/g, '-');
       const backupPath = `./backups/taskman_${timestamp}.db`;

       await db.backup(backupPath);
       logger.info({ backupPath }, 'Database backup created');

       return backupPath;
     }

     async restoreBackup(backupPath: string): Promise<void> {
       db.close();
       fs.copyFileSync(backupPath, './data/taskman.db');
       // Reinitialize db connection
       logger.info({ backupPath }, 'Database restored from backup');
     }
   }
   ```

2. Schedule automated backups:
   ```typescript
   // src/infrastructure/database/scheduler.ts (NEW)
   import cron from 'node-cron';

   export function scheduleBackups(): void {
     // Daily at 2 AM
     cron.schedule('0 2 * * *', async () => {
       await backupService.createBackup();
       await backupService.cleanupOldBackups(30); // Keep 30 days
     });
   }
   ```

3. Implement retention policy:
   ```typescript
   async cleanupOldBackups(retentionDays: number): Promise<void> {
     const cutoffDate = Date.now() - (retentionDays * 24 * 60 * 60 * 1000);
     const backups = fs.readdirSync('./backups');

     for (const backup of backups) {
       const stats = fs.statSync(`./backups/${backup}`);
       if (stats.mtimeMs < cutoffDate) {
         fs.unlinkSync(`./backups/${backup}`);
         logger.info({ backup }, 'Old backup deleted');
       }
     }
   }
   ```

**New Dependencies:**
- node-cron@^3.0.3

#### Testing (1.75 days)
**Unit Tests:**
- ✅ Backup creates valid SQLite file
- ✅ Restore replaces current database
- ✅ Retention policy deletes old backups

**Integration Tests:**
- ✅ Backup while writes in progress
- ✅ Restore doesn't lose recent data
- ✅ Scheduled backups trigger automatically

**Disaster Recovery Tests:**
- ✅ Delete database, restore from backup
- ✅ Corrupt database, restore from backup
- ✅ Restore to different environment

**Coverage Target:** ≥85% for backup code

#### Validation (0.25 days)
- Create manual backup: `npm run db:backup`
- Verify backup file valid: `sqlite3 backups/taskman_*.db ".tables"`
- Delete main DB, restore from backup
- Verify data intact

**Success Metrics:**
- ✅ Backups complete in < 5 seconds
- ✅ Restore completes in < 10 seconds
- ✅ 0 data loss in restore tests
- ✅ Retention policy enforced automatically

---

### 3.3 Transaction Management (Days 19-20)

**Improvements:**
- [CRITICAL-006] Atomic operations
- [HIGH-011] Optimistic concurrency control
- [MEDIUM-013] Deadlock detection

**Implementation Cycle:**

#### Research (0.25 days)
- Review SQLite transaction isolation levels
- Research optimistic locking patterns (ETags, version numbers)

**ADR Required:** ADR-014-Transaction-Strategy.md
- Transaction isolation level (SERIALIZABLE)
- Concurrency control (optimistic locking)
- Deadlock resolution (timeouts)

#### Implementation (1 day)
1. Add transaction wrapper:
   ```typescript
   // src/infrastructure/database/transaction.ts (NEW)
   export function withTransaction<T>(
     fn: (tx: Database.Transaction) => T
   ): T {
     const tx = db.transaction(fn);
     return tx();
   }
   ```

2. Implement optimistic locking:
   ```typescript
   // Add version column to tasks table (migration)
   ALTER TABLE tasks ADD COLUMN version INTEGER DEFAULT 1;

   // Update with version check
   export function updateWithVersion(
     id: string,
     updates: TaskUpdate,
     expectedVersion: number
   ): TaskRecord {
     return withTransaction((tx) => {
       const current = tx.prepare('SELECT version FROM tasks WHERE id = ?').get(id);
       if (current.version !== expectedVersion) {
         throw new ConcurrencyConflictError('Task was modified by another user');
       }

       tx.prepare('UPDATE tasks SET ..., version = version + 1 WHERE id = ?').run(...);
       return findById(id);
     });
   }
   ```

3. Add deadlock timeout:
   ```typescript
   db.pragma('busy_timeout = 5000'); // 5 second timeout
   ```

#### Testing (1.5 days)
**Unit Tests:**
- ✅ Transaction commits on success
- ✅ Transaction rolls back on error
- ✅ Optimistic lock prevents lost updates
- ✅ Version mismatch throws error

**Concurrency Tests:**
- ✅ 10 concurrent updates to same task
- ✅ Only 1 succeeds, others retry or fail gracefully
- ✅ No deadlocks with busy_timeout

**Coverage Target:** ≥95% for transaction code

#### Validation (0.25 days)
- Run concurrent update test
- Verify only 1 update succeeds
- Check version incremented correctly

**Success Metrics:**
- ✅ 0 lost updates in concurrent scenarios
- ✅ Transaction rollback on any error
- ✅ Deadlocks resolved within timeout
- ✅ Optimistic lock conflicts < 5% of updates

---

### 3.4 Query Optimization (Days 20-21)

**Improvements:**
- [MEDIUM-014] Index optimization
- [LOW-010] Query caching
- [LOW-011] N+1 query prevention

**Implementation Cycle:**

#### Research (0.25 days)
- Review SQLite query planner (EXPLAIN QUERY PLAN)
- Research index strategies (covering indexes, partial indexes)

**ADR Required:** ADR-015-Query-Optimization-Strategy.md
- Indexing strategy
- Query caching policy
- Performance SLOs (service level objectives)

#### Implementation (1 day)
1. Add indexes for common queries:
   ```sql
   -- migrations/002_add_indexes.sql
   CREATE INDEX idx_tasks_status_priority ON tasks(status, priority);
   CREATE INDEX idx_tasks_project_sprint ON tasks(project_id, sprint_id);
   CREATE INDEX idx_tasks_assignee ON tasks(assignee);
   ```

2. Implement query caching:
   ```typescript
   // src/infrastructure/database/query-cache.ts (NEW)
   const queryCache = new TTLCache<any>();

   export function cachedQuery<T>(
     key: string,
     query: () => T,
     ttlMs: number = 60000
   ): T {
     const cached = queryCache.get(key);
     if (cached !== undefined) return cached;

     const result = query();
     queryCache.set(key, result, ttlMs);
     return result;
   }
   ```

3. Create eager loading helpers:
   ```typescript
   // Prevent N+1: Load tasks with related data in one query
   export function findTasksWithRelations(projectId: string): TaskRecord[] {
     return db.prepare(`
       SELECT
         t.*,
         p.name as project_name,
         s.name as sprint_name
       FROM tasks t
       LEFT JOIN projects p ON t.project_id = p.id
       LEFT JOIN sprints s ON t.sprint_id = s.id
       WHERE t.project_id = ?
     `).all(projectId);
   }
   ```

#### Testing (1.5 days)
**Performance Tests:**
- ✅ Query with index < 10ms
- ✅ Query without index > 50ms (baseline)
- ✅ Cache hit < 1ms

**Unit Tests:**
- ✅ Query cache returns cached values
- ✅ Cache invalidation clears entries
- ✅ Eager loading prevents N+1

**Coverage Target:** ≥85% for query optimization code

#### Validation (0.25 days)
- Analyze query plans: `EXPLAIN QUERY PLAN SELECT ...`
- Verify indexes used
- Measure query times with 10,000 rows
- Check cache hit rate > 50%

**Success Metrics:**
- ✅ All queries < 50ms (95th percentile)
- ✅ Indexes reduce query time by 5x
- ✅ Cache hit rate > 50% for repeated queries
- ✅ No N+1 queries detected

---

### 3.5 Data Validation & Integrity (Days 21-23)

**Improvements:**
- [HIGH-012] Schema validation on write
- [MEDIUM-015] Data consistency checks
- [LOW-012] Automated integrity tests

**Implementation Cycle:**

#### Research (0.5 days)
- Review SQLite CHECK constraints
- Research data validation patterns

**ADR Required:** ADR-016-Data-Integrity-Strategy.md
- Validation layers (Zod + SQLite constraints)
- Consistency check frequency
- Corruption detection methods

#### Implementation (1.5 days)
1. Add CHECK constraints:
   ```sql
   -- migrations/003_add_constraints.sql
   ALTER TABLE tasks ADD CONSTRAINT chk_status
     CHECK (status IN ('planned', 'new', 'pending', 'in_progress', 'completed', 'blocked', 'cancelled'));

   ALTER TABLE tasks ADD CONSTRAINT chk_priority
     CHECK (priority IS NULL OR priority IN ('low', 'medium', 'high', 'critical'));
   ```

2. Create consistency checker:
   ```typescript
   // src/infrastructure/database/integrity.ts (NEW)
   export class IntegrityChecker {
     checkOrphanedTasks(): string[] {
       const orphans = db.prepare(`
         SELECT t.id FROM tasks t
         LEFT JOIN projects p ON t.project_id = p.id
         WHERE p.id IS NULL
       `).all();

       if (orphans.length > 0) {
         logger.warn({ count: orphans.length }, 'Orphaned tasks detected');
       }

       return orphans.map(o => o.id);
     }

     checkInvalidStatuses(): string[] {
       // Checks data integrity beyond constraints
       const invalid = db.prepare(`
         SELECT id FROM tasks
         WHERE status NOT IN (...)
         OR priority NOT IN (...)
       `).all();

       return invalid.map(i => i.id);
     }
   }
   ```

3. Schedule integrity checks:
   ```typescript
   // Daily at 3 AM
   cron.schedule('0 3 * * *', async () => {
     const checker = new IntegrityChecker();
     const issues = await checker.runAllChecks();
     if (issues.length > 0) {
       await alertManager.fireAlert({
         name: 'DataIntegrityIssues',
         severity: 'warning',
         description: `${issues.length} data integrity issues found`
       });
     }
   });
   ```

#### Testing (1.75 days)
**Unit Tests:**
- ✅ CHECK constraints prevent invalid data
- ✅ Orphaned task detection works
- ✅ Consistency checks catch issues

**Integration Tests:**
- ✅ Attempt to insert invalid data, verify rejected
- ✅ Delete project, verify tasks handled (cascade or prevent)
- ✅ Scheduled checks run automatically

**Chaos Tests:**
- ✅ Manually corrupt data, verify detected
- ✅ Integrity checker catches all issues

**Coverage Target:** ≥90% for integrity code

#### Validation (0.25 days)
- Run integrity checker: `npm run db:check-integrity`
- Verify clean bill of health
- Insert invalid data manually, re-run checker
- Verify issues detected

**Success Metrics:**
- ✅ All constraints enforced
- ✅ Integrity checks detect 100% of test issues
- ✅ 0 undetected data corruption in tests
- ✅ Automated checks run daily

---

### **CHECKPOINT GATE 3: Persistence & Reliability Complete**

**Validation Criteria:**
- ✅ All Phase 3 tests passing
- ✅ Test coverage ≥85% overall, ≥90% for database code
- ✅ 6 more ADRs documented (ADR-011 through ADR-016)
- ✅ SQLite database operational
- ✅ Migrations run successfully
- ✅ Backups automated and tested
- ✅ Transactions atomic
- ✅ Queries optimized
- ✅ Data integrity checks passing

**Database Health Checklist:**
- ✅ Database file exists and readable
- ✅ All tables have indexes on foreign keys
- ✅ WAL mode enabled
- ✅ Foreign key constraints enforced
- ✅ At least 1 successful backup exists
- ✅ Restore tested and validated
- ✅ Optimistic locking operational
- ✅ Integrity checks passing

**Performance SLOs:**
- Database startup: < 100ms
- Simple query (by ID): < 10ms
- Complex query (with joins): < 50ms
- Transaction commit: < 20ms
- Backup creation: < 5 seconds
- Restore from backup: < 10 seconds

**Go Decision:** Proceed to Phase 4
**No-Go Decision:** Fix database issues, ensure data integrity, re-validate

**Rollback Procedure:**
- Restore from Phase 2 checkpoint backup
- Document database migration issues
- Plan database schema fixes

---

## Phase 4: Quality & Testing (Days 24-28)

**Focus:** Comprehensive testing, security, and production readiness
**Testing:** 50% E2E, 30% integration, 20% new unit tests

### 4.1 Test Coverage Expansion (Days 24-25)

**Improvements:**
- [HIGH-013] Achieve ≥90% coverage on critical paths
- [MEDIUM-016] Integration test suite
- [LOW-013] E2E test scenarios

**Implementation Cycle:**

#### Research (0.25 days)
- Review uncovered code (from coverage reports)
- Identify critical paths without tests

**ADR Required:** ADR-017-Testing-Strategy.md
- Coverage targets per module
- Test pyramid ratios (70/20/10)
- Continuous integration requirements

#### Implementation (1 day)
1. Add missing unit tests:
   ```typescript
   // Identify from: npm run test:coverage --reporter=lcov
   // Focus on:
   // - Error handling branches
   // - Edge cases
   // - Boundary conditions
   ```

2. Expand integration tests:
   ```typescript
   // src/__tests__/integration/task-lifecycle.test.ts (NEW)
   describe('Task Lifecycle', () => {
     it('should handle complete task workflow', async () => {
       const project = await createProject({ name: 'Test' });
       const task = await createTask({ project_id: project.id, title: 'Task 1' });
       expect(task.status).toBe('new');

       await updateTask(task.id, { status: 'in_progress' });
       const updated = await getTask(task.id);
       expect(updated.status).toBe('in_progress');

       await completeTask(task.id);
       const completed = await getTask(task.id);
       expect(completed.status).toBe('completed');
     });
   });
   ```

3. Add E2E tests:
   ```typescript
   // src/__tests__/e2e/mcp-client.test.ts (NEW)
   describe('MCP Client E2E', () => {
     it('should execute full tool call chain', async () => {
       const mcpClient = new MCPClient();
       await mcpClient.connect();

       const result = await mcpClient.callTool('task_create', {
         title: 'E2E Test Task',
         project_id: 'test-project'
       });

       expect(result.success).toBe(true);
       expect(result.task.title).toBe('E2E Test Task');
     });
   });
   ```

#### Testing (1.5 days)
**Coverage Analysis:**
- ✅ Identify uncovered lines
- ✅ Prioritize critical paths
- ✅ Write tests until coverage targets met

**Test Quality:**
- ✅ Tests independent (no shared state)
- ✅ Tests deterministic (no flakiness)
- ✅ Tests fast (unit < 10ms, integration < 100ms)

**Coverage Target:** ≥90% overall, ≥95% for critical paths

#### Validation (0.25 days)
- Run: `npm run test:coverage`
- Verify coverage reports show ≥90%
- Check uncovered lines are non-critical

**Success Metrics:**
- ✅ Coverage ≥90% overall
- ✅ Coverage ≥95% for: repositories, services, critical tools
- ✅ 0 flaky tests
- ✅ Test suite runtime < 30 seconds

---

### 4.2 Security Testing (Days 25-27)

**Improvements:**
- [CRITICAL-007] Input validation security tests
- [HIGH-014] Authentication/authorization tests (if applicable)
- [MEDIUM-017] SQL injection prevention
- [LOW-014] Secrets management audit

**Implementation Cycle:**

#### Research (0.5 days)
- Review OWASP Top 10
- Research security testing tools (npm audit, snyk, semgrep)

**ADR Required:** ADR-018-Security-Testing-Strategy.md
- Security scanning tools
- Vulnerability remediation policy
- Secrets management approach

**ADR Required:** ADR-019-Secrets-Management.md
- Environment variable usage
- Secret rotation strategy
- API key handling

#### Implementation (1.5 days)
1. Add security tests:
   ```typescript
   // src/__tests__/security/input-validation.test.ts (NEW)
   describe('Input Validation Security', () => {
     it('should reject SQL injection attempts', async () => {
       const malicious = "'; DROP TABLE tasks; --";
       await expect(
         createTask({ title: malicious, project_id: 'test' })
       ).rejects.toThrow(); // Or sanitizes safely
     });

     it('should reject XSS payloads', async () => {
       const xss = "<script>alert('xss')</script>";
       const task = await createTask({ title: xss, project_id: 'test' });
       expect(task.title).not.toContain('<script>');
     });

     it('should reject excessively long inputs', async () => {
       const longString = 'a'.repeat(10000);
       await expect(
         createTask({ title: longString, project_id: 'test' })
       ).rejects.toThrow(/max length/i);
     });
   });
   ```

2. Run dependency vulnerability scan:
   ```bash
   npm audit
   # Address HIGH and CRITICAL vulnerabilities
   ```

3. Implement secrets management:
   ```typescript
   // src/infrastructure/config.ts (NEW)
   export const config = {
     backendUrl: requireEnv('BACKEND_URL'),
     apiKey: requireEnv('API_KEY'), // Never logged
     dbPath: process.env.DB_PATH || './data/taskman.db'
   };

   function requireEnv(key: string): string {
     const value = process.env[key];
     if (!value) {
       throw new Error(`Missing required env var: ${key}`);
     }
     return value;
   }
   ```

4. Add static analysis:
   ```bash
   npx semgrep --config=auto src/
   ```

**New Dev Dependencies:**
- semgrep (CLI tool, not npm package)

#### Testing (2.25 days)
**Security Tests:**
- ✅ All OWASP Top 10 test vectors
- ✅ SQL injection prevention
- ✅ XSS prevention
- ✅ Command injection prevention
- ✅ Path traversal prevention

**Secrets Audit:**
- ✅ No secrets in code
- ✅ No secrets in logs
- ✅ Environment variables validated

**Dependency Audit:**
- ✅ No HIGH or CRITICAL npm vulnerabilities
- ✅ All dependencies up-to-date (or exceptions documented)

**Coverage Target:** ≥95% for security-critical code

#### Validation (0.25 days)
- Run: `npm audit`
- Run: `npm run test:security` (create script)
- Review: Pino redaction working (test with sensitive data)
- Verify: No secrets in git history

**Success Metrics:**
- ✅ 0 HIGH or CRITICAL vulnerabilities
- ✅ All OWASP test vectors pass
- ✅ Secrets never logged
- ✅ Static analysis clean (or exceptions documented)

---

### 4.3 Performance Testing (Days 27-28)

**Improvements:**
- [MEDIUM-018] Load testing
- [LOW-015] Stress testing
- [LOW-016] Performance regression tests

**Implementation Cycle:**

#### Research (0.25 days)
- Review load testing tools (k6, artillery, autocannon)
- Research performance benchmarking strategies

**ADR Required:** ADR-020-Performance-Testing-Strategy.md
- Load testing tool (k6)
- Performance SLOs per operation
- Regression detection thresholds

#### Implementation (1 day)
1. Create load test scripts:
   ```javascript
   // tests/load/task-operations.js (NEW)
   import http from 'k6/http';
   import { check, sleep } from 'k6';

   export let options = {
     stages: [
       { duration: '30s', target: 20 },  // Ramp-up
       { duration: '1m', target: 50 },   // Steady
       { duration: '30s', target: 0 }    // Ramp-down
     ]
   };

   export default function() {
     const res = http.post('http://localhost:3000/mcp', JSON.stringify({
       tool: 'task_create',
       arguments: { title: 'Load Test Task', project_id: 'test-project' }
     }));

     check(res, {
       'status 200': (r) => r.status === 200,
       'response time < 500ms': (r) => r.timings.duration < 500
     });

     sleep(1);
   }
   ```

2. Add performance benchmarks:
   ```typescript
   // src/__tests__/performance/benchmarks.test.ts (NEW)
   import { performance } from 'perf_hooks';

   describe('Performance Benchmarks', () => {
     it('task_create should complete in < 100ms', async () => {
       const start = performance.now();
       await createTask({ title: 'Benchmark', project_id: 'test' });
       const duration = performance.now() - start;

       expect(duration).toBeLessThan(100);
     });
   });
   ```

3. Implement regression detection:
   ```typescript
   // Compare against baseline metrics from Phase 0
   const baseline = JSON.parse(fs.readFileSync('docs/BASELINE-METRICS.md'));
   expect(currentMetrics.taskCreateLatency).toBeLessThan(
     baseline.taskCreateLatency * 1.1 // 10% regression threshold
   );
   ```

**New Dev Dependencies:**
- k6 (install via CLI, not npm)

#### Testing (1.5 days)
**Load Tests:**
- ✅ Sustained load: 50 RPS for 5 minutes
- ✅ Peak load: 100 RPS for 1 minute
- ✅ Stress test: Increase until failure point

**Performance Benchmarks:**
- ✅ All operations meet SLOs
- ✅ No regressions vs Phase 0 baseline

**Resource Monitoring:**
- ✅ CPU usage < 80% under load
- ✅ Memory stable (no leaks)
- ✅ Database connections < pool limit

**Coverage Target:** N/A (performance tests)

#### Validation (0.25 days)
- Run: `k6 run tests/load/task-operations.js`
- Verify: 95th percentile < 500ms
- Check: Error rate < 1%
- Monitor: CPU, memory, disk I/O

**Success Metrics:**
- ✅ Handles 50 RPS sustained
- ✅ 95th percentile latency < 500ms
- ✅ Error rate < 1% under load
- ✅ No performance regressions vs baseline

---

### **CHECKPOINT GATE 4: Production Ready**

**Validation Criteria:**
- ✅ All Phase 4 tests passing
- ✅ Test coverage ≥90% overall, ≥95% critical paths
- ✅ 4 more ADRs documented (ADR-017 through ADR-020)
- ✅ Security tests passing
- ✅ No HIGH/CRITICAL vulnerabilities
- ✅ Load tests passing
- ✅ Performance SLOs met

**Production Readiness Checklist:**
- ✅ All 22 improvements implemented
- ✅ 20+ ADRs documented
- ✅ Comprehensive test suite (unit, integration, E2E)
- ✅ Test coverage ≥90%
- ✅ Security audit passing
- ✅ Load tests passing
- ✅ Observability operational (metrics, traces, logs, alerts)
- ✅ Database persistence with backups
- ✅ Circuit breaker operational
- ✅ Graceful degradation tested
- ✅ Documentation complete (README, API docs)
- ✅ Runbook created (operations guide)

**Final Performance Validation:**
- Server startup: < 2 seconds ✅
- Tool registration: < 100ms ✅
- Task create: < 100ms (95th %ile) ✅
- Task query: < 50ms (95th %ile) ✅
- Backend request: < 500ms (95th %ile) ✅
- Memory usage (idle): < 100MB ✅
- Sustained load: 50 RPS ✅

**Go Decision:** Deploy to production
**No-Go Decision:** Address critical gaps, retest, re-validate

---

## Post-Implementation: Documentation & Handoff (Days 29-30)

### Documentation Deliverables

1. **README.md (Updated)**
   - Installation instructions
   - Configuration guide
   - Quick start tutorial
   - Troubleshooting

2. **ARCHITECTURE.md (NEW)**
   - System architecture diagram
   - Component descriptions
   - Data flow diagrams
   - Technology stack

3. **API-DOCUMENTATION.md (NEW)**
   - All MCP tools documented
   - Request/response examples
   - Error codes
   - Rate limits (if applicable)

4. **RUNBOOK.md (NEW)**
   - Common operations
   - Monitoring dashboard guide
   - Alert response procedures
   - Backup/restore procedures
   - Troubleshooting guide

5. **ADR Index (20+ files)**
   - All architectural decisions documented
   - Rationale, context, consequences
   - Links between related ADRs

6. **CHANGELOG.md (Updated)**
   - Version 0.2.0 release notes
   - All 22 improvements listed
   - Breaking changes (if any)
   - Migration guide

### Handoff Activities

1. **Knowledge Transfer Session**
   - Walkthrough of architecture
   - Demo of monitoring/alerting
   - Q&A session

2. **Operations Training**
   - How to run server
   - How to check health
   - How to read logs
   - How to respond to alerts
   - How to backup/restore

3. **Development Handoff**
   - Code walkthrough
   - Test suite overview
   - How to add new tools
   - How to modify schemas

---

## Risk Management

### Identified Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Phase 0 fixes take longer than expected | Medium | High | Allocated buffer time, prioritized by blocker severity |
| Pino v8 incompatibility | Low | Medium | Research before implementation, consider downgrade to v7 if needed |
| SQLite performance under load | Medium | Medium | Load test early (Phase 3), have PostgreSQL migration plan as backup |
| Test coverage targets not met | Low | High | Incremental coverage checks at each checkpoint, prioritize critical paths |
| Dependencies introduce vulnerabilities | Medium | Medium | Weekly `npm audit`, pin dependency versions, review security advisories |
| Timeline slippage | Medium | Low | 20% buffer built into estimates, checkpoint gates allow early detection |

### Contingency Plans

1. **Phase 0 Blockers**
   - If Pino v8 unfixable: Downgrade to pino@^7.x
   - If dependencies unsolvable: Create isolated test environment, debug systematically

2. **Performance Issues**
   - If SQLite too slow: Implement read-through cache (Redis)
   - If memory leaks persist: Use clinic.js to identify, refactor culprit code

3. **Security Vulnerabilities**
   - Critical: Patch immediately, deploy hotfix
   - High: Fix within 48 hours
   - Medium/Low: Fix in next sprint

4. **Test Coverage Gaps**
   - Focus on critical paths first (task CRUD, backend client)
   - Accept lower coverage for non-critical code (e.g., notification channels)
   - Document coverage exceptions

---

## Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 0: Validation & Remediation | 2-3 days | Dependencies installed, compilation passing, baseline documented |
| Phase 1: Operational Stability | 7 days | Logging, error handling, resource management, input validation, state management |
| Phase 2: Observability | 7 days | Health checks, metrics, tracing, alerting |
| Phase 3: Persistence & Reliability | 9 days | SQLite, backups, transactions, query optimization, data integrity |
| Phase 4: Quality & Testing | 5 days | Test coverage, security, performance |
| Post-Implementation | 2 days | Documentation, handoff |
| **Total (with buffer)** | **30-41 days** | 22 improvements, 20+ ADRs, ≥90% coverage, production-ready |

**Critical Path:** Phase 0 → Phase 1 → Phase 3 (other phases can overlap)

---

## Success Criteria (Overall)

### Technical Criteria
- ✅ All 22 improvements implemented
- ✅ TypeScript compilation passes (0 errors)
- ✅ Test coverage ≥90% overall, ≥95% critical paths
- ✅ All checkpoint gates passed
- ✅ 20+ ADRs documented
- ✅ Security audit passing (0 HIGH/CRITICAL vulnerabilities)
- ✅ Load tests passing (50 RPS sustained)
- ✅ Performance SLOs met

### Operational Criteria
- ✅ Server starts successfully in < 2 seconds
- ✅ All MCP tools operational
- ✅ Health endpoints responding
- ✅ Metrics being exported
- ✅ Logs structured and searchable
- ✅ Alerts firing correctly
- ✅ Database persistence working
- ✅ Backups automated

### Documentation Criteria
- ✅ README complete with quick start
- ✅ Architecture documented
- ✅ API documentation complete
- ✅ Runbook created
- ✅ All ADRs written
- ✅ CHANGELOG updated

---

## Next Steps

**Immediate (After Approval):**
1. Begin Phase 0 remediation:
   ```bash
   cd TaskMan-v2/mcp-server-ts
   rm -rf node_modules package-lock.json
   npm install
   npm run typecheck
   ```

2. Fix compilation errors systematically (Priority 1 → Priority 5)

3. Create `docs/BASELINE-METRICS.md` once build passes

4. Validate Phase 0 checkpoint criteria

**After Phase 0 Passes:**
5. Begin Phase 1, Day 1: Structured Logging Implementation
6. Update todo list daily
7. Document ADRs as decisions are made
8. Run tests continuously (`npm run test:watch`)

---

## Appendix: Tool Reference

### Development Tools
- TypeScript 5.9.3
- Vitest 4.0.3 (test framework)
- tsx (TypeScript execution)
- Pino 8.19.0 (logging)
- Zod 3.25.76 (validation)
- better-sqlite3 9.0.0 (database)
- opossum 6.0.0 (circuit breaker)
- prom-client 15.1.0 (metrics)
- @opentelemetry/sdk-node 1.19.0 (tracing)
- k6 (load testing)

### Monitoring & Observability
- Prometheus (metrics collection)
- Jaeger/Zipkin (trace visualization)
- Grafana (dashboards) - optional
- Slack (alerts)
- PagerDuty (critical alerts) - optional

### Scripts to Create
```json
{
  "scripts": {
    "dev": "tsx src/index.ts",
    "build": "tsc -p tsconfig.json",
    "typecheck": "tsc --noEmit",
    "start": "node dist/index.js",
    "test": "vitest run",
    "test:watch": "vitest watch",
    "test:coverage": "vitest run --coverage",
    "test:security": "vitest run src/__tests__/security",
    "test:load": "k6 run tests/load/task-operations.js",
    "db:migrate": "tsx src/infrastructure/database/migrate.ts",
    "db:backup": "tsx src/infrastructure/database/backup-cli.ts",
    "db:check-integrity": "tsx src/infrastructure/database/integrity-cli.ts"
  }
}
```

---

**Version History:**
- v1.0 (2025-11-05): Initial implementation plan
- v2.0 (2025-11-06): Enhanced with Phase 0 findings, checkpoint gates, comprehensive testing, ADR requirements, security phase, realistic timeline (28-41 days)
