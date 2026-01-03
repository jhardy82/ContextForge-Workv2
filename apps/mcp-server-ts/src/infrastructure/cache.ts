/**
 * TTL Cache - Phase 1.5
 *
 * In-memory cache with time-to-live expiration
 */

import { logger } from "./logger.js";

interface CacheEntry<T> {
  value: T;
  expiresAt: number;
}

export class TTLCache<T> {
  private cache = new Map<string, CacheEntry<T>>();
  private readonly defaultTTL: number;
  private cleanupInterval: NodeJS.Timeout | null = null;
  private hits = 0;
  private misses = 0;

  constructor(defaultTTLMs: number = 60000) {
    // Default: 1 minute
    this.defaultTTL = defaultTTLMs;
  }

  /**
   * Set a value with optional custom TTL
   */
  set(key: string, value: T, ttlMs?: number): void {
    const ttl = ttlMs ?? this.defaultTTL;
    this.cache.set(key, {
      value,
      expiresAt: Date.now() + ttl,
    });
  }

  /**
   * Get a value (returns undefined if expired or not found)
   */
  get(key: string): T | undefined {
    const entry = this.cache.get(key);

    if (!entry) {
      this.misses++;
      return undefined;
    }

    if (entry.expiresAt < Date.now()) {
      this.cache.delete(key);
      this.misses++;
      return undefined;
    }

    this.hits++;
    return entry.value;
  }

  /**
   * Check if key exists and is not expired
   */
  has(key: string): boolean {
    const entry = this.cache.get(key);
    if (!entry) {
      return false;
    }

    if (entry.expiresAt < Date.now()) {
      this.cache.delete(key);
      return false;
    }

    return true;
  }

  /**
   * Delete a key
   */
  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  /**
   * Clear all entries
   */
  clear(): void {
    this.cache.clear();
    this.hits = 0;
    this.misses = 0;
  }

  /**
   * Get cache size
   */
  size(): number {
    return this.cache.size;
  }

  /**
   * Get cache hit rate
   */
  getHitRate(): number {
    const total = this.hits + this.misses;
    return total === 0 ? 0 : this.hits / total;
  }

  /**
   * Get cache statistics
   */
  getStats() {
    return {
      size: this.cache.size,
      hits: this.hits,
      misses: this.misses,
      hitRate: this.getHitRate(),
    };
  }

  /**
   * Get or compute value (with caching)
   */
  async getOrCompute(
    key: string,
    compute: () => Promise<T>,
    ttlMs?: number
  ): Promise<T> {
    const cached = this.get(key);
    if (cached !== undefined) {
      return cached;
    }

    const value = await compute();
    this.set(key, value, ttlMs);
    return value;
  }

  /**
   * Start automatic cleanup of expired entries
   */
  startCleanup(intervalMs: number = 60000): void {
    // Default: 1 minute
    if (this.cleanupInterval) {
      return;
    }

    this.cleanupInterval = setInterval(() => {
      const now = Date.now();
      let cleanedCount = 0;

      for (const [key, entry] of this.cache.entries()) {
        if (entry.expiresAt < now) {
          this.cache.delete(key);
          cleanedCount++;
        }
      }

      if (cleanedCount > 0) {
        logger.debug({ cleanedCount, cacheSize: this.cache.size }, "Expired cache entries cleaned up");
      }
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
}

// Create default cache instances
export const defaultCache = new TTLCache<any>();
export const projectCache = new TTLCache<any>(300000); // 5 minutes
export const taskCache = new TTLCache<any>(60000); // 1 minute
