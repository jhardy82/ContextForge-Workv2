/**
 * Circuit Breaker + Fallback Cache Integration Tests
 *
 * Tests the real integration between circuit breaker and fallback cache
 * to ensure they work together correctly for resilience.
 *
 * Key scenarios tested:
 * 1. Cache on success - successful responses should be cached
 * 2. Fallback on circuit open - serve stale data when backend is down
 * 3. Cache invalidation - ensure expired data is not served
 * 4. Circuit recovery - fresh data served after circuit closes
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { createEnhancedCircuitBreaker, circuitBreakerRegistry } from "./circuit-breaker.js";
import { FallbackCache } from "./fallback-cache.js";
import { CircuitBreakerOpenError } from "../core/errors.js";

// Mock metrics service to avoid side effects
vi.mock("../infrastructure/metrics.js", () => ({
  metricsService: {
    recordBackendRequest: vi.fn(),
    recordCircuitBreakerEvent: vi.fn(),
    recordCacheHit: vi.fn(),
    recordCacheMiss: vi.fn(),
    setCacheSize: vi.fn(),
  },
}));

describe("Circuit Breaker + Fallback Cache Integration", () => {
  let testCache: FallbackCache<string, any>;

  beforeEach(() => {
    circuitBreakerRegistry.clear();
    // Create a real cache instance for integration testing
    testCache = new FallbackCache({
      maxSize: 10,
      ttlMs: 5000, // 5 second default TTL
      enableMetrics: false,
    });
    vi.useFakeTimers();
  });

  afterEach(() => {
    circuitBreakerRegistry.clear();
    testCache.stopCleanup();
    testCache.clear();
    vi.useRealTimers();
  });

  describe("Cache on success", () => {
    it("should cache successful responses", async () => {
      let callCount = 0;
      const breaker = createEnhancedCircuitBreaker(
        async (id: string) => {
          callCount++;
          return { id, data: `result-${callCount}`, timestamp: Date.now() };
        },
        {
          name: "cache-success-1",
          enableFallbackCache: true,
          cacheKeyFn: (id: string) => `task:${id}`,
        }
      );

      // Make a successful request
      const result1 = await breaker.fire("123");
      expect(result1.id).toBe("123");
      expect(result1.data).toBe("result-1");

      // Manually open circuit to force fallback
      breaker.open();

      // Should serve from cache (fallback will be called with args)
      const result2 = await breaker.fire("123");
      expect(result2.id).toBe("123");
      expect(result2.data).toBe("result-1"); // Same as first call (cached)

      expect(callCount).toBe(1); // Only called once, second was from cache
    });

    it("should update cache on subsequent successful requests", async () => {
      let callCount = 0;
      const breaker = createEnhancedCircuitBreaker(
        async (id: string) => {
          callCount++;
          return { id, version: callCount };
        },
        {
          name: "cache-success-2",
          enableFallbackCache: true,
          cacheKeyFn: (id: string) => `item:${id}`,
          volumeThreshold: 10, // High threshold to keep circuit closed
        }
      );

      // First request
      const result1 = await breaker.fire("abc");
      expect(result1.version).toBe(1);

      // Second request - should update cache
      const result2 = await breaker.fire("abc");
      expect(result2.version).toBe(2);

      // Open circuit and verify latest cached value
      breaker.open();
      const result3 = await breaker.fire("abc");
      expect(result3.version).toBe(2); // Latest cached value

      expect(callCount).toBe(2);
    });

    it("should generate correct cache keys with cacheKeyFn", async () => {
      const breaker = createEnhancedCircuitBreaker(
        async (type: string, id: string) => {
          return { type, id, data: "test-data" };
        },
        {
          name: "cache-success-3",
          enableFallbackCache: true,
          cacheKeyFn: (type: string, id: string) => `${type}:${id}`,
        }
      );

      // Cache different items with different keys
      await breaker.fire("task", "1");
      await breaker.fire("project", "1");

      // Open circuit
      breaker.open();

      // Both should be cached independently
      const task = await breaker.fire("task", "1");
      expect(task.type).toBe("task");

      const project = await breaker.fire("project", "1");
      expect(project.type).toBe("project");
    });
  });

  describe("Fallback on circuit open", () => {
    it("should serve from cache when circuit is open", async () => {
      let callCount = 0;
      const breaker = createEnhancedCircuitBreaker(
        async (id: string) => {
          callCount++;
          if (callCount > 1) {
            throw new Error("Service down");
          }
          return { id, data: "cached-data" };
        },
        {
          name: "fallback-1",
          enableFallbackCache: true,
          cacheKeyFn: (id: string) => `task:${id}`,
          volumeThreshold: 1,
        }
      );

      // First call succeeds and caches
      const result1 = await breaker.fire("999");
      expect(result1.data).toBe("cached-data");

      // Open circuit
      breaker.open();

      // Should serve from cache (circuit open triggers fallback)
      const result2 = await breaker.fire("999");
      expect(result2.data).toBe("cached-data");
      expect(callCount).toBe(1); // Only first call reached the function
    });

    it("should throw CircuitBreakerOpenError on cache miss", async () => {
      const breaker = createEnhancedCircuitBreaker(
        async (id: string) => {
          throw new Error("Service unavailable");
        },
        {
          name: "fallback-2",
          enableFallbackCache: true,
          cacheKeyFn: (id: string) => `task:${id}`,
        }
      );

      // Open circuit without caching anything
      breaker.open();

      // Should throw because no cached data exists
      await expect(breaker.fire("not-cached")).rejects.toThrow(CircuitBreakerOpenError);
    });

    it("should respect cache TTL during fallback", async () => {
      let callCount = 0;
      const breaker = createEnhancedCircuitBreaker(
        async (id: string) => {
          callCount++;
          if (callCount > 1) {
            throw new Error("Service down");
          }
          return { id, data: "expiring-data" };
        },
        {
          name: "fallback-3",
          enableFallbackCache: true,
          cacheKeyFn: (id: string) => `task:${id}`,
        }
      );

      // First call succeeds and caches with default TTL
      await breaker.fire("555");

      // Open circuit
      breaker.open();

      // Should serve from cache before TTL expires
      const result1 = await breaker.fire("555");
      expect(result1.data).toBe("expiring-data");

      // Advance time past cache TTL (default is 300000ms = 5 minutes in config)
      await vi.advanceTimersByTimeAsync(301000); // 5 minutes + 1 second

      // Cache should be expired, should throw error
      await expect(breaker.fire("555")).rejects.toThrow(CircuitBreakerOpenError);
    });

    it("should serve same cached data for multiple fallback requests", async () => {
      const breaker = createEnhancedCircuitBreaker(
        async (id: string) => {
          return { id, data: "consistent-data", timestamp: Date.now() };
        },
        {
          name: "fallback-4",
          enableFallbackCache: true,
          cacheKeyFn: (id: string) => `task:${id}`,
        }
      );

      // Cache data
      const original = await breaker.fire("777");

      // Open circuit
      breaker.open();

      // Multiple requests should return same cached data
      const result1 = await breaker.fire("777");
      const result2 = await breaker.fire("777");
      const result3 = await breaker.fire("777");

      expect(result1).toEqual(original);
      expect(result2).toEqual(original);
      expect(result3).toEqual(original);
    });
  });

  describe("Cache invalidation", () => {
    it("should update cache when new successful request completes", async () => {
      let version = 1;
      const breaker = createEnhancedCircuitBreaker(
        async (id: string) => {
          return { id, version: version++ };
        },
        {
          name: "invalidation-1",
          enableFallbackCache: true,
          cacheKeyFn: (id: string) => `task:${id}`,
          volumeThreshold: 10,
        }
      );

      // First request caches v1
      const result1 = await breaker.fire("abc");
      expect(result1.version).toBe(1);

      // Second request caches v2 (invalidates v1)
      const result2 = await breaker.fire("abc");
      expect(result2.version).toBe(2);

      // Open circuit and verify v2 is in cache
      breaker.open();
      const result3 = await breaker.fire("abc");
      expect(result3.version).toBe(2);
    });

    it("should not serve expired cache during fallback", async () => {
      const breaker = createEnhancedCircuitBreaker(
        async (id: string) => {
          return { id, data: "fresh-data" };
        },
        {
          name: "invalidation-2",
          enableFallbackCache: true,
          cacheKeyFn: (id: string) => `task:${id}`,
        }
      );

      // Cache data
      await breaker.fire("expired");

      // Advance time past cache TTL (default is 300000ms = 5 minutes)
      await vi.advanceTimersByTimeAsync(301000);

      // Open circuit
      breaker.open();

      // Should throw because cache is expired
      await expect(breaker.fire("expired")).rejects.toThrow(CircuitBreakerOpenError);
    });
  });

  describe("Circuit recovery", () => {
    it("should serve fresh data after circuit closes and update cache", async () => {
      let callCount = 0;
      let shouldFail = false;

      const breaker = createEnhancedCircuitBreaker(
        async (id: string) => {
          callCount++;
          if (shouldFail) {
            throw new Error("Service temporarily down");
          }
          return { id, data: `fresh-${callCount}` };
        },
        {
          name: "recovery-1",
          enableFallbackCache: true,
          cacheKeyFn: (id: string) => `task:${id}`,
          volumeThreshold: 1,
          resetTimeout: 1000,
        }
      );

      // Cache initial data
      const result1 = await breaker.fire("recovery");
      expect(result1.data).toBe("fresh-1");

      // Make it fail and open circuit
      shouldFail = true;
      breaker.open();

      // Serve from cache
      const result2 = await breaker.fire("recovery");
      expect(result2.data).toBe("fresh-1");

      // Advance time to allow circuit reset
      await vi.advanceTimersByTimeAsync(1100);
      expect(breaker.halfOpen).toBe(true);

      // Allow success again
      shouldFail = false;

      // Should serve fresh data and update cache
      const result3 = await breaker.fire("recovery");
      expect(result3.data).toBe("fresh-2");

      expect(callCount).toBe(2);
    });

    it("should handle half-open state probe failure and recovery", async () => {
      let attemptCount = 0;

      const breaker = createEnhancedCircuitBreaker(
        async (id: string) => {
          attemptCount++;
          if (attemptCount === 1) {
            // First call succeeds
            return { id, data: "cached-data" };
          } else if (attemptCount === 2) {
            // Second call fails (during half-open probe)
            throw new Error("Still failing");
          } else {
            // Third call succeeds
            return { id, data: "recovered-data" };
          }
        },
        {
          name: "recovery-2",
          enableFallbackCache: true,
          cacheKeyFn: (id: string) => `task:${id}`,
          volumeThreshold: 1,
          resetTimeout: 1000,
        }
      );

      // First call succeeds and caches
      await breaker.fire("test");
      expect(attemptCount).toBe(1);

      // Open circuit
      breaker.open();

      // Advance to half-open state
      await vi.advanceTimersByTimeAsync(1100);
      expect(breaker.halfOpen).toBe(true);

      // Half-open probe fails, but opossum calls fallback which returns cached data
      // (this is the actual opossum behavior - fallback is called on any failure)
      const fallbackResult = await breaker.fire("test");
      expect(attemptCount).toBe(2); // The probe attempt was made
      expect(fallbackResult.data).toBe("cached-data");

      // Circuit should reopen after half-open failure
      expect(breaker.opened).toBe(true);

      // Advance to half-open again
      await vi.advanceTimersByTimeAsync(1100);
      expect(breaker.halfOpen).toBe(true);

      // This time the probe succeeds and closes circuit
      const recoveredResult = await breaker.fire("test");
      expect(attemptCount).toBe(3);
      expect(recoveredResult.data).toBe("recovered-data");
      expect(breaker.opened).toBe(false);
    });

    it("should track cache hit rate correctly", async () => {
      const cache = new FallbackCache<string, any>({
        maxSize: 10,
        ttlMs: 5000,
        enableMetrics: false,
      });

      // Simulate cache hits and misses
      cache.set("key1", "value1");
      cache.set("key2", "value2");

      // 3 hits
      cache.get("key1");
      cache.get("key2");
      cache.get("key1");

      // 2 misses
      cache.get("nonexistent1");
      cache.get("nonexistent2");

      const stats = cache.getStats();

      expect(stats.hits).toBe(3);
      expect(stats.misses).toBe(2);
      expect(stats.hitRate).toBeCloseTo(60, 1); // 3/(3+2) = 60%

      cache.stopCleanup();
      cache.clear();
    });
  });
});
