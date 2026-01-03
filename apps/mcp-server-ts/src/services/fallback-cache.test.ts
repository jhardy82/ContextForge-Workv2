import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { FallbackCache } from "./fallback-cache.js";

describe("FallbackCache", () => {
  let cache: FallbackCache<string, any>;

  beforeEach(() => {
    cache = new FallbackCache({ maxSize: 3, ttlMs: 1000, enableMetrics: false });
  });

  afterEach(() => {
    cache.stopCleanup();
    cache.clear();
  });

  describe("Basic operations", () => {
    it("should store and retrieve values", () => {
      cache.set("key1", "value1");
      expect(cache.get("key1")).toBe("value1");
    });

    it("should return undefined for missing key", () => {
      expect(cache.get("nonexistent")).toBeUndefined();
    });

    it("should delete entry and return true when key exists", () => {
      cache.set("key1", "value1");
      const deleted = cache.delete("key1");
      expect(deleted).toBe(true);
      expect(cache.get("key1")).toBeUndefined();
    });

    it("should return false when deleting non-existent key", () => {
      const deleted = cache.delete("nonexistent");
      expect(deleted).toBe(false);
    });
  });

  describe("LRU eviction", () => {
    it("should evict oldest entry when cache is full", () => {
      cache.set("key1", "value1");
      cache.set("key2", "value2");
      cache.set("key3", "value3");

      // Cache is full (maxSize=3), adding key4 should evict key1
      cache.set("key4", "value4");

      expect(cache.get("key1")).toBeUndefined();
      expect(cache.get("key2")).toBe("value2");
      expect(cache.get("key3")).toBe("value3");
      expect(cache.get("key4")).toBe("value4");
    });

    it("should update lastAccessedAt on get() access", () => {
      cache.set("key1", "value1");
      cache.set("key2", "value2");
      cache.set("key3", "value3");

      // Access key2 and key3 to update their lastAccessedAt
      cache.get("key2");
      cache.get("key3");

      // Now key1 is least recently accessed (only set, never get)
      // Adding key4 should evict key1
      cache.set("key4", "value4");

      expect(cache.get("key1")).toBeUndefined();
      expect(cache.get("key2")).toBe("value2");
      expect(cache.get("key3")).toBe("value3");
      expect(cache.get("key4")).toBe("value4");
    });

    it("should select least recently accessed entry for eviction", () => {
      cache.set("key1", "value1");
      cache.set("key2", "value2");
      cache.set("key3", "value3");

      // Access in order: key2, key3
      // This makes key1 the least recently accessed (never accessed after set)
      cache.get("key2");
      cache.get("key3");

      // key1 is least recently accessed (only set, never get), should be evicted
      cache.set("key4", "value4");

      expect(cache.get("key1")).toBeUndefined();
      expect(cache.get("key2")).toBe("value2");
      expect(cache.get("key3")).toBe("value3");
      expect(cache.get("key4")).toBe("value4");
    });

    it("should enforce maxSize constraint", () => {
      cache.set("key1", "value1");
      cache.set("key2", "value2");
      cache.set("key3", "value3");
      cache.set("key4", "value4");
      cache.set("key5", "value5");

      // Cache should never exceed maxSize of 3
      expect(cache.size()).toBe(3);
      expect(cache.getStats().size).toBe(3);
    });

    it("should increment evictions counter when evicting", () => {
      cache.set("key1", "value1");
      cache.set("key2", "value2");
      cache.set("key3", "value3");

      const statsBefore = cache.getStats();
      expect(statsBefore.evictions).toBe(0);

      // Trigger eviction
      cache.set("key4", "value4");

      const statsAfter = cache.getStats();
      expect(statsAfter.evictions).toBe(1);
    });
  });

  describe("TTL expiration", () => {
    beforeEach(() => {
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it("should return undefined for expired entries", () => {
      cache.set("key1", "value1", 1000);

      // Advance time past TTL
      vi.advanceTimersByTime(1001);

      expect(cache.get("key1")).toBeUndefined();
    });

    it("should clean up expired entries on get()", () => {
      cache.set("key1", "value1", 1000);
      expect(cache.size()).toBe(1);

      // Advance time past TTL
      vi.advanceTimersByTime(1001);

      cache.get("key1");
      expect(cache.size()).toBe(0);
    });

    it("should retain non-expired entries", () => {
      cache.set("key1", "value1", 2000);

      // Advance time but stay within TTL
      vi.advanceTimersByTime(1000);

      expect(cache.get("key1")).toBe("value1");
    });

    it("should respect custom ttlMs parameter", () => {
      cache.set("key1", "value1", 500);   // 500ms TTL
      cache.set("key2", "value2", 2000);  // 2000ms TTL

      // Advance to 600ms
      vi.advanceTimersByTime(600);

      expect(cache.get("key1")).toBeUndefined(); // Expired
      expect(cache.get("key2")).toBe("value2");  // Still valid
    });
  });

  describe("Statistics", () => {
    it("should increment hits on successful get()", () => {
      cache.set("key1", "value1");

      const statsBefore = cache.getStats();
      expect(statsBefore.hits).toBe(0);

      cache.get("key1");

      const statsAfter = cache.getStats();
      expect(statsAfter.hits).toBe(1);
    });

    it("should increment misses on failed get()", () => {
      const statsBefore = cache.getStats();
      expect(statsBefore.misses).toBe(0);

      cache.get("nonexistent");

      const statsAfter = cache.getStats();
      expect(statsAfter.misses).toBe(1);
    });

    it("should return accurate statistics via getStats()", () => {
      cache.set("key1", "value1");
      cache.set("key2", "value2");

      cache.get("key1"); // hit
      cache.get("key2"); // hit
      cache.get("key3"); // miss

      const stats = cache.getStats();

      expect(stats.hits).toBe(2);
      expect(stats.misses).toBe(1);
      expect(stats.size).toBe(2);
      expect(stats.maxSize).toBe(3);
      expect(stats.hitRate).toBeCloseTo(66.67, 1);
    });

    it("should reset size statistic on clear()", () => {
      cache.set("key1", "value1");
      cache.set("key2", "value2");

      expect(cache.getStats().size).toBe(2);

      cache.clear();

      expect(cache.getStats().size).toBe(0);
    });
  });

  describe("Edge cases", () => {
    it("should handle undefined values correctly", () => {
      cache.set("key1", undefined);

      // Getting undefined value should still count as hit
      const value = cache.get("key1");
      expect(value).toBeUndefined();

      const stats = cache.getStats();
      expect(stats.hits).toBe(1);
      expect(stats.size).toBe(1);
    });

    it("should handle null values correctly", () => {
      cache.set("key1", null);

      const value = cache.get("key1");
      expect(value).toBeNull();

      const stats = cache.getStats();
      expect(stats.hits).toBe(1);
      expect(stats.size).toBe(1);
    });

    it("should handle maxSize of 1 correctly", () => {
      const smallCache = new FallbackCache({ maxSize: 1, ttlMs: 1000, enableMetrics: false });

      smallCache.set("key1", "value1");
      expect(smallCache.size()).toBe(1);
      expect(smallCache.get("key1")).toBe("value1");

      // Adding second item should evict first
      smallCache.set("key2", "value2");
      expect(smallCache.size()).toBe(1);
      expect(smallCache.get("key1")).toBeUndefined();
      expect(smallCache.get("key2")).toBe("value2");

      smallCache.stopCleanup();
    });
  });
});
