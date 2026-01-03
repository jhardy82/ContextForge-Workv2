/**
 * Memory Monitor - Phase 1.3
 *
 * Monitors memory usage and warns when thresholds exceeded
 */

import { logger } from "./logger.js";

export interface MemoryThresholds {
  /** Warning threshold in MB */
  warning: number;
  /** Critical threshold in MB */
  critical: number;
}

const DEFAULT_THRESHOLDS: MemoryThresholds = {
  warning: 200, // 200 MB
  critical: 400, // 400 MB
};

export class MemoryMonitor {
  private interval: NodeJS.Timeout | null = null;
  private thresholds: MemoryThresholds;

  constructor(thresholds: Partial<MemoryThresholds> = {}) {
    this.thresholds = { ...DEFAULT_THRESHOLDS, ...thresholds };
  }

  /**
   * Start monitoring memory usage
   */
  start(intervalMs: number = 60000): void {
    if (this.interval) {
      return; // Already running
    }

    this.interval = setInterval(() => {
      this.checkMemory();
    }, intervalMs);

    logger.info({
      intervalMs,
      thresholds: this.thresholds,
    }, "Memory monitoring started");
  }

  /**
   * Stop monitoring
   */
  stop(): void {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
      logger.info("Memory monitoring stopped");
    }
  }

  /**
   * Get current memory usage
   */
  getMemoryUsage() {
    const usage = process.memoryUsage();
    return {
      heapUsedMB: Math.round(usage.heapUsed / 1024 / 1024),
      heapTotalMB: Math.round(usage.heapTotal / 1024 / 1024),
      rssMB: Math.round(usage.rss / 1024 / 1024),
      externalMB: Math.round(usage.external / 1024 / 1024),
      arrayBuffersMB: Math.round(usage.arrayBuffers / 1024 / 1024),
    };
  }

  /**
   * Check memory and log warnings
   */
  private checkMemory(): void {
    const usage = this.getMemoryUsage();

    if (usage.heapUsedMB >= this.thresholds.critical) {
      logger.error({
        memoryUsage: usage,
        threshold: this.thresholds.critical,
      }, "CRITICAL: Memory usage exceeded critical threshold");
    } else if (usage.heapUsedMB >= this.thresholds.warning) {
      logger.warn({
        memoryUsage: usage,
        threshold: this.thresholds.warning,
      }, "WARNING: Memory usage exceeded warning threshold");
    } else {
      logger.debug({ memoryUsage: usage }, "Memory usage normal");
    }
  }

  /**
   * Force garbage collection (if --expose-gc flag is set)
   */
  forceGC(): void {
    if (global.gc) {
      const beforeMB = this.getMemoryUsage().heapUsedMB;
      global.gc();
      const afterMB = this.getMemoryUsage().heapUsedMB;
      logger.info({
        beforeMB,
        afterMB,
        freedMB: beforeMB - afterMB,
      }, "Garbage collection completed");
    } else {
      logger.warn("Garbage collection not available (run with --expose-gc)");
    }
  }
}

// Singleton instance
export const memoryMonitor = new MemoryMonitor();
