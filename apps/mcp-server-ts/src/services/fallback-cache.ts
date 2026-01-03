/**
 * Fallback Cache - LRU cache for circuit breaker fallback
 *
 * Features:
 * - LRU (Least Recently Used) eviction policy
 * - TTL-based expiration
 * - Type-safe get/set with generics
 * - Cache statistics (hits, misses, size)
 * - Metrics integration
 * - Automatic cleanup of expired entries
 *
 * Usage:
 * ```typescript
 * import { fallbackCache } from "./services/fallback-cache.js";
 *
 * // Store data
 * fallbackCache.set("key1", { data: "value" }, 60000); // 60s TTL
 *
 * // Retrieve data
 * const value = fallbackCache.get("key1");
 * if (value) {
 *   console.log("Cache hit:", value);
 * }
 * ```
 */

import { createModuleLogger } from "../infrastructure/logger.js";
import { shutdownService } from "../infrastructure/shutdown.js";
import { metricsService } from "../infrastructure/metrics.js";
import { config } from "../config/index.js";

const logger = createModuleLogger("fallback-cache");

/**
 * Cache entry with metadata
 */
interface CacheEntry<T> {
  /** Cached value */
  value: T;

  /** Timestamp when entry expires (milliseconds since epoch) */
  expiresAt: number;

  /** Timestamp when entry was created */
  createdAt: number;

  /** Timestamp when entry was last accessed (for LRU) */
  lastAccessedAt: number;

  /** Number of times entry has been accessed */
  accessCount: number;
}

/**
 * Cache statistics
 */
export interface CacheStats {
  /** Number of successful cache hits */
  hits: number;

  /** Number of cache misses */
  misses: number;

  /** Current number of entries in cache */
  size: number;

  /** Maximum allowed cache size */
  maxSize: number;

  /** Number of entries evicted due to size constraints */
  evictions: number;

  /** Number of entries expired due to TTL */
  expirations: number;

  /** Hit rate as percentage (0-100) */
  hitRate: number;
}

/**
 * Configuration options for FallbackCache
 */
export interface FallbackCacheOptions {
  /** Maximum number of entries (LRU eviction when exceeded) */
  maxSize: number;

  /** Default TTL in milliseconds */
  ttlMs: number;

  /** Enable metrics integration */
  enableMetrics?: boolean;
}

/**
 * LRU Cache with TTL expiration for circuit breaker fallback
 *
 * Thread-safe implementation using Map with LRU eviction policy.
 */
export class FallbackCache<K = string, V = any> {
  private cache: Map<K, CacheEntry<V>>;
  private stats: CacheStats;
  private maxSize: number;
  private defaultTTL: number;
  private enableMetrics: boolean;
  private cleanupInterval: NodeJS.Timeout | null = null;

  /**
   * Create a new fallback cache
   *
   * @param options - Cache configuration options
   */
  constructor(options: FallbackCacheOptions) {
    this.cache = new Map();
    this.maxSize = options.maxSize;
    this.defaultTTL = options.ttlMs;
    this.enableMetrics = options.enableMetrics ?? config.ENABLE_METRICS;

    this.stats = {
      hits: 0,
      misses: 0,
      size: 0,
      maxSize: this.maxSize,
      evictions: 0,
      expirations: 0,
      hitRate: 0,
    };

    logger.info({
      maxSize: this.maxSize,
      defaultTTL: this.defaultTTL,
      enableMetrics: this.enableMetrics,
    }, "Fallback cache initialized");

    // Register shutdown handler
    shutdownService.registerResource("fallback-cache", async () => {
      this.stopCleanup();
      this.clear();
    });
  }

  /**
   * Get value from cache (updates LRU order)
   *
   * @param key - Cache key
   * @returns Cached value, or undefined if not found or expired
   */
  get(key: K): V | undefined {
    const entry = this.cache.get(key);

    if (!entry) {
      this.stats.misses++;
      this.updateHitRate();
      if (this.enableMetrics) {
        metricsService.recordCacheMiss();
      }
      return undefined;
    }

    // Check if expired
    if (this.isExpired(entry)) {
      this.cache.delete(key);
      this.stats.expirations++;
      this.stats.misses++;
      this.stats.size = this.cache.size;
      this.updateHitRate();
      if (this.enableMetrics) {
        metricsService.recordCacheMiss();
        metricsService.setCacheSize(this.cache.size);
      }
      logger.debug({ key }, "Cache entry expired");
      return undefined;
    }

    // Update LRU metadata
    entry.lastAccessedAt = Date.now();
    entry.accessCount++;

    this.stats.hits++;
    this.updateHitRate();
    if (this.enableMetrics) {
      metricsService.recordCacheHit();
    }

    return entry.value;
  }

  /**
   * Set value in cache (evicts LRU if needed)
   *
   * @param key - Cache key
   * @param value - Value to cache
   * @param ttlMs - Optional TTL override (uses default if not specified)
   */
  set(key: K, value: V, ttlMs?: number): void {
    const now = Date.now();
    const ttl = ttlMs ?? this.defaultTTL;

    const entry: CacheEntry<V> = {
      value,
      expiresAt: now + ttl,
      createdAt: now,
      lastAccessedAt: now,
      accessCount: 0,
    };

    // Check if we need to evict
    if (!this.cache.has(key) && this.cache.size >= this.maxSize) {
      this.evictLRU();
    }

    this.cache.set(key, entry);
    this.stats.size = this.cache.size;

    if (this.enableMetrics) {
      metricsService.setCacheSize(this.cache.size);
    }

    logger.debug({
      key,
      ttl,
      cacheSize: this.cache.size,
    }, "Cache entry set");
  }

  /**
   * Check if key exists and is not expired
   *
   * @param key - Cache key
   * @returns True if key exists and not expired
   */
  has(key: K): boolean {
    const entry = this.cache.get(key);
    if (!entry) {
      return false;
    }

    if (this.isExpired(entry)) {
      this.cache.delete(key);
      this.stats.expirations++;
      this.stats.size = this.cache.size;
      return false;
    }

    return true;
  }

  /**
   * Delete specific key from cache
   *
   * @param key - Cache key
   * @returns True if key existed and was deleted
   */
  delete(key: K): boolean {
    const deleted = this.cache.delete(key);
    if (deleted) {
      this.stats.size = this.cache.size;
      if (this.enableMetrics) {
        metricsService.setCacheSize(this.cache.size);
      }
    }
    return deleted;
  }

  /**
   * Clear entire cache
   */
  clear(): void {
    const size = this.cache.size;
    this.cache.clear();
    this.stats.size = 0;

    if (this.enableMetrics) {
      metricsService.setCacheSize(0);
    }

    logger.info({ clearedEntries: size }, "Cache cleared");
  }

  /**
   * Get cache statistics
   *
   * @returns Current cache statistics
   */
  getStats(): CacheStats {
    return { ...this.stats };
  }

  /**
   * Manual cleanup of expired entries
   *
   * @returns Number of entries removed
   */
  cleanup(): number {
    const now = Date.now();
    let removed = 0;

    for (const [key, entry] of this.cache.entries()) {
      if (entry.expiresAt <= now) {
        this.cache.delete(key);
        removed++;
        this.stats.expirations++;
      }
    }

    if (removed > 0) {
      this.stats.size = this.cache.size;
      if (this.enableMetrics) {
        metricsService.setCacheSize(this.cache.size);
      }
      logger.debug({ removed, remaining: this.cache.size }, "Cache cleanup completed");
    }

    return removed;
  }

  /**
   * Start automatic cleanup interval
   *
   * @param intervalMs - Cleanup interval in milliseconds
   */
  startCleanup(intervalMs: number): void {
    if (this.cleanupInterval) {
      logger.warn("Cleanup already running");
      return;
    }

    this.cleanupInterval = setInterval(() => {
      this.cleanup();
    }, intervalMs);

    logger.info({ intervalMs }, "Cache cleanup started");
  }

  /**
   * Stop automatic cleanup
   */
  stopCleanup(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
      logger.info("Cache cleanup stopped");
    }
  }

  /**
   * Evict least recently used entry when max size reached
   *
   * @private
   */
  private evictLRU(): void {
    let oldestKey: K | null = null;
    let oldestTime = Infinity;

    for (const [key, entry] of this.cache.entries()) {
      if (entry.lastAccessedAt < oldestTime) {
        oldestTime = entry.lastAccessedAt;
        oldestKey = key;
      }
    }

    if (oldestKey !== null) {
      this.cache.delete(oldestKey);
      this.stats.evictions++;
      logger.debug({
        evictedKey: oldestKey,
        lastAccessed: new Date(oldestTime).toISOString(),
      }, "LRU entry evicted");
    }
  }

  /**
   * Check if entry has expired
   *
   * @param entry - Cache entry to check
   * @returns True if expired
   * @private
   */
  private isExpired(entry: CacheEntry<V>): boolean {
    return entry.expiresAt <= Date.now();
  }

  /**
   * Update hit rate percentage
   *
   * @private
   */
  private updateHitRate(): void {
    const total = this.stats.hits + this.stats.misses;
    this.stats.hitRate = total > 0 ? (this.stats.hits / total) * 100 : 0;
  }

  /**
   * Get all keys in cache (useful for debugging)
   *
   * @returns Array of cache keys
   */
  keys(): K[] {
    return Array.from(this.cache.keys());
  }

  /**
   * Get cache size
   *
   * @returns Number of entries in cache
   */
  size(): number {
    return this.cache.size;
  }
}

/**
 * Default fallback cache instance
 *
 * Configured from environment variables.
 */
export const fallbackCache = new FallbackCache({
  maxSize: config.FALLBACK_CACHE_MAX_SIZE,
  ttlMs: config.FALLBACK_CACHE_TTL_MS,
  enableMetrics: config.ENABLE_METRICS,
});

// Start automatic cleanup every 60 seconds
if (config.FALLBACK_CACHE_ENABLED) {
  fallbackCache.startCleanup(60000);
  logger.info("Fallback cache enabled with automatic cleanup");
}
