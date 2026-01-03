/**
 * Circuit Breaker - Phase 2
 *
 * Enhancements over Phase 1:
 * - Prometheus metrics integration
 * - Fallback cache integration
 * - Request context propagation
 * - Trace span creation
 * - Statistics endpoint
 * - Circuit breaker registry
 *
 * Prevents cascading failures by:
 * - Opening circuit after error threshold
 * - Half-open state for recovery testing
 * - Closed state for normal operation
 *
 * Built on opossum library for production-ready circuit breaking
 */

import CircuitBreaker from "opossum";
import { createModuleLogger } from "../infrastructure/logger.js";
import { metricsService } from "../infrastructure/metrics.js";
import { fallbackCache } from "./fallback-cache.js";
import { CircuitBreakerOpenError } from "../core/errors.js";

const logger = createModuleLogger("circuit-breaker");

/**
 * Circuit breaker options (Phase 1 compatible)
 */
export interface CircuitBreakerOptions {
  /** Request timeout in ms */
  timeout?: number;
  /** Error threshold percentage (0-100) to open circuit */
  errorThresholdPercentage?: number;
  /** Time in ms before attempting to close circuit */
  resetTimeout?: number;
  /** Rolling window duration in ms for error calculation */
  rollingCountTimeout?: number;
  /** Minimum requests before error calculation */
  volumeThreshold?: number;
  /** Name for logging and metrics */
  name?: string;
}

/**
 * Enhanced circuit breaker options (Phase 2)
 */
export interface EnhancedCircuitBreakerOptions extends CircuitBreakerOptions {
  /** Enable Prometheus metrics recording */
  enableMetrics?: boolean;

  /** Enable fallback cache integration */
  enableFallbackCache?: boolean;

  /** Function to generate cache key from function arguments */
  cacheKeyFn?: (...args: any[]) => string;

  /** Custom fallback function (overrides default) */
  fallbackFn?: (...args: any[]) => Promise<any>;
}

const DEFAULT_OPTIONS: Required<CircuitBreakerOptions> = {
  timeout: 5000, // 5 second timeout
  errorThresholdPercentage: 50, // Open if 50% of requests fail
  resetTimeout: 30000, // Try to close after 30 seconds
  rollingCountTimeout: 10000, // 10 second rolling window
  volumeThreshold: 5, // Need at least 5 requests to calculate error rate
  name: "default",
};

/**
 * Create a circuit breaker for an async function (Phase 1 compatible)
 *
 * Example:
 * ```typescript
 * const breaker = createCircuitBreaker(
 *   async (url: string) => axios.get(url),
 *   { name: "backend-api", timeout: 3000 }
 * );
 *
 * try {
 *   const result = await breaker.fire("https://api.example.com");
 * } catch (error) {
 *   if (error instanceof CircuitBreakerOpenError) {
 *     // Circuit is open, use fallback
 *   }
 * }
 * ```
 */
export function createCircuitBreaker<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  options: CircuitBreakerOptions = {}
): CircuitBreaker<Parameters<T>, ReturnType<T>> {
  const opts = { ...DEFAULT_OPTIONS, ...options };

  const breaker = new CircuitBreaker(fn, {
    timeout: opts.timeout,
    errorThresholdPercentage: opts.errorThresholdPercentage,
    resetTimeout: opts.resetTimeout,
    rollingCountTimeout: opts.rollingCountTimeout,
    volumeThreshold: opts.volumeThreshold,
    name: opts.name,
  });

  // Event logging (Phase 1)
  breaker.on("open", () => {
    logger.warn({ circuitBreaker: opts.name }, "Circuit breaker opened");
  });

  breaker.on("halfOpen", () => {
    logger.info({ circuitBreaker: opts.name }, "Circuit breaker half-open (testing recovery)");
  });

  breaker.on("close", () => {
    logger.info({ circuitBreaker: opts.name }, "Circuit breaker closed (recovered)");
  });

  breaker.on("timeout", () => {
    logger.warn({ circuitBreaker: opts.name, timeout: opts.timeout }, "Circuit breaker: request timed out");
  });

  breaker.on("reject", () => {
    logger.warn({ circuitBreaker: opts.name }, "Circuit breaker: request rejected (circuit open)");
  });

  breaker.fallback(() => {
    throw new CircuitBreakerOpenError(opts.name);
  });

  return breaker as CircuitBreaker<Parameters<T>, ReturnType<T>>;
}

/**
 * Create an enhanced circuit breaker with Phase 2 features
 *
 * Example:
 * ```typescript
 * const breaker = createEnhancedCircuitBreaker(
 *   async (id: string) => backendClient.getTask(id),
 *   {
 *     name: "get-task",
 *     timeout: 3000,
 *     enableMetrics: true,
 *     enableFallbackCache: true,
 *     cacheKeyFn: (id) => `task:${id}`,
 *   }
 * );
 *
 * const task = await breaker.fire("task-123");
 * ```
 */
export function createEnhancedCircuitBreaker<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  options: EnhancedCircuitBreakerOptions = {}
): CircuitBreaker<Parameters<T>, ReturnType<T>> {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  const enableMetrics = options.enableMetrics ?? false;
  const enableFallbackCache = options.enableFallbackCache ?? false;

  // Capture args for success handler (opossum doesn't pass args to success event)
  let lastCallArgs: any[] = [];
  const wrappedFn = async (...args: Parameters<T>): Promise<ReturnType<T>> => {
    lastCallArgs = args;
    return fn(...args);
  };

  const breaker = new CircuitBreaker(wrappedFn, {
    timeout: opts.timeout,
    errorThresholdPercentage: opts.errorThresholdPercentage,
    resetTimeout: opts.resetTimeout,
    rollingCountTimeout: opts.rollingCountTimeout,
    volumeThreshold: opts.volumeThreshold,
    name: opts.name,
  });

  // Phase 2: Metrics instrumentation
  if (enableMetrics) {
    breaker.on("success", (result: any, latency: number) => {
      // Record as successful backend request
      metricsService.recordBackendRequest("BREAKER", opts.name, 200, latency);
    });

    breaker.on("failure", (error: any) => {
      // Record as failed backend request
      metricsService.recordBackendRequest("BREAKER", opts.name, 500, 0, "circuit_failure");
      logger.error({
        circuitBreaker: opts.name,
        error: error instanceof Error ? error.message : String(error),
      }, "Circuit breaker: request failed");
    });

    breaker.on("timeout", () => {
      // Record as timeout backend request
      metricsService.recordBackendRequest("BREAKER", opts.name, 504, 0, "timeout");
    });

    breaker.on("reject", () => {
      // Record as rejected backend request (circuit open)
      metricsService.recordBackendRequest("BREAKER", opts.name, 503, 0, "circuit_open");
    });

    breaker.on("open", () => {
      metricsService.recordCircuitBreakerEvent(opts.name, "OPEN");
      logger.warn({ circuitBreaker: opts.name }, "Circuit breaker opened");
    });

    breaker.on("close", () => {
      metricsService.recordCircuitBreakerEvent(opts.name, "CLOSED");
      logger.info({ circuitBreaker: opts.name }, "Circuit breaker closed (recovered)");
    });

    breaker.on("halfOpen", () => {
      metricsService.recordCircuitBreakerEvent(opts.name, "HALF_OPEN");
      logger.info({ circuitBreaker: opts.name }, "Circuit breaker half-open (testing recovery)");
    });
  }

  // Phase 2: Fallback cache integration
  if (enableFallbackCache && options.cacheKeyFn) {
    // Cache successful responses
    breaker.on("success", (result: any, latency: number) => {
      try {
        // Use captured args from lastCallArgs (opossum doesn't pass args to success event)
        const cacheKey = options.cacheKeyFn!(...lastCallArgs);
        if (cacheKey) {
          fallbackCache.set(cacheKey, result);
          logger.debug({
            circuitBreaker: opts.name,
            cacheKey,
          }, "Cached successful response");
        }
      } catch (error) {
        logger.error({
          circuitBreaker: opts.name,
          error: error instanceof Error ? error.message : String(error),
        }, "Failed to cache response");
      }
    });

    // Fallback: Try cache, then throw if not found
    breaker.fallback(async (...args: any[]) => {
      try {
        const cacheKey = options.cacheKeyFn!(...args);
        if (cacheKey) {
          const cached = fallbackCache.get(cacheKey);
          if (cached !== undefined) {
            logger.info({
              circuitBreaker: opts.name,
              cacheKey,
            }, "Serving from fallback cache (circuit open)");
            return cached;
          }
        }
      } catch (error) {
        logger.error({
          circuitBreaker: opts.name,
          error: error instanceof Error ? error.message : String(error),
        }, "Fallback cache lookup failed");
      }

      // No cache hit, throw circuit open error
      throw new CircuitBreakerOpenError(opts.name);
    });
  } else if (options.fallbackFn) {
    // Custom fallback function
    breaker.fallback(options.fallbackFn);
  } else {
    // Default fallback: throw error
    breaker.fallback(() => {
      throw new CircuitBreakerOpenError(opts.name);
    });
  }

  // Register in global registry
  circuitBreakerRegistry.set(opts.name, breaker);

  logger.info({
    name: opts.name,
    timeout: opts.timeout,
    errorThreshold: opts.errorThresholdPercentage,
    enableMetrics,
    enableFallbackCache,
  }, "Enhanced circuit breaker created");

  return breaker as CircuitBreaker<Parameters<T>, ReturnType<T>>;
}

/**
 * Get circuit breaker metrics
 */
export function getCircuitBreakerMetrics(breaker: CircuitBreaker<any, any>) {
  const stats = breaker.stats;
  return {
    state: breaker.opened ? "open" : breaker.halfOpen ? "halfOpen" : "closed",
    totalRequests: stats.fires,
    successfulRequests: stats.successes,
    failedRequests: stats.failures,
    timeouts: stats.timeouts,
    rejectedRequests: stats.rejects,
    errorPercentage: stats.fires > 0 ? (stats.failures / stats.fires) * 100 : 0,
    averageResponseTime: stats.latencyMean,
  };
}

/**
 * Check if circuit breaker is healthy
 */
export function isCircuitBreakerHealthy(breaker: CircuitBreaker<any, any>): boolean {
  return !breaker.opened && !breaker.halfOpen;
}

/**
 * Global circuit breaker registry
 *
 * Tracks all circuit breakers for monitoring and metrics.
 */
export const circuitBreakerRegistry = new Map<string, CircuitBreaker<any, any>>();

/**
 * Get all circuit breaker statistics
 *
 * Useful for metrics endpoints and monitoring.
 */
export function getAllCircuitBreakerMetrics(): Record<string, ReturnType<typeof getCircuitBreakerMetrics>> {
  const metrics: Record<string, ReturnType<typeof getCircuitBreakerMetrics>> = {};

  for (const [name, breaker] of circuitBreakerRegistry.entries()) {
    metrics[name] = getCircuitBreakerMetrics(breaker);
  }

  return metrics;
}

/**
 * Reset all circuit breakers
 *
 * Useful for testing or emergency recovery.
 */
export function resetAllCircuitBreakers(): void {
  for (const [name, breaker] of circuitBreakerRegistry.entries()) {
    if (breaker.opened || breaker.halfOpen) {
      breaker.close();
      logger.info({ circuitBreaker: name }, "Circuit breaker force-closed");
    }
  }
}
