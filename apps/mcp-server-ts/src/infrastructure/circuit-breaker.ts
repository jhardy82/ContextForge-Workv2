/**
 * Circuit Breaker - Phase 1.2
 *
 * Prevents cascading failures by:
 * - Opening circuit after error threshold
 * - Half-open state for recovery testing
 * - Closed state for normal operation
 *
 * Built on opossum library for production-ready circuit breaking
 */

import CircuitBreaker from "opossum";
import { logger } from "./logger.js";
import { CircuitBreakerOpenError } from "../core/errors.js";

/**
 * Circuit breaker options
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
  /** Name for logging */
  name?: string;
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
 * Create a circuit breaker for an async function
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

  // Event logging
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
