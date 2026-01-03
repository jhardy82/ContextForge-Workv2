/**
 * System Metrics Collector - Periodic system metrics collection
 *
 * Features:
 * - Collects Node.js system metrics every 30 seconds
 * - Metrics collected:
 *   * Memory usage (heapUsed, heapTotal, external, rss)
 *   * CPU usage percentage
 *   * Event loop lag
 *   * Active handles/requests
 * - Updates MetricsService with collected metrics
 * - Graceful shutdown support
 * - Singleton pattern
 *
 * Usage:
 * ```typescript
 * import { systemMetricsCollector } from "./infrastructure/system-metrics.js";
 *
 * // Start collecting metrics every 30 seconds
 * systemMetricsCollector.start();
 *
 * // Stop collecting metrics
 * systemMetricsCollector.stop();
 * ```
 */

import { metricsService } from "./metrics.js";
import { logger } from "./logger.js";
import { shutdownService } from "./shutdown.js";

/**
 * System metrics snapshot
 */
export interface SystemMetricsSnapshot {
  timestamp: number;
  memory: {
    heapUsed: number;
    heapTotal: number;
    external: number;
    rss: number;
  };
  cpu: number; // percentage (0-100)
  eventLoopLag: number; // milliseconds
  activeHandles: number;
}

/**
 * SystemMetricsCollector - Collects and updates system metrics periodically
 */
class SystemMetricsCollector {
  private interval: NodeJS.Timeout | null = null;
  private collecting = false;
  private lastCpuUsage: NodeJS.CpuUsage | null = null;
  private collectionCount = 0;
  private readonly DEFAULT_INTERVAL_MS = 30000; // 30 seconds

  constructor() {
    // Register shutdown handler
    shutdownService.registerResource("system-metrics-collector", async () => {
      this.stop();
    });
  }

  /**
   * Start collecting system metrics
   */
  start(intervalMs: number = this.DEFAULT_INTERVAL_MS): void {
    if (this.interval) {
      logger.warn("System metrics collection already running");
      return;
    }

    this.collecting = true;
    this.collectionCount = 0;
    this.lastCpuUsage = process.cpuUsage();

    logger.info({
      intervalMs,
    }, "System metrics collection started");

    // Collect immediately on start
    this.collect();

    // Then collect periodically
    this.interval = setInterval(() => {
      this.collect();
    }, intervalMs);
  }

  /**
   * Stop collecting system metrics
   */
  stop(): void {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
      this.collecting = false;

      logger.info({
        collectionCount: this.collectionCount,
      }, "System metrics collection stopped");
    }
  }

  /**
   * Collect system metrics and update MetricsService
   */
  private collect(): void {
    try {
      const snapshot = this.getSystemMetricsSnapshot();

      // Update metrics service with full MemoryUsage object
      const memoryUsage = process.memoryUsage();
      metricsService.recordSystemMetrics(memoryUsage, snapshot.cpu);
      metricsService.recordEventLoopLag(snapshot.eventLoopLag);
      metricsService.setActiveHandles(snapshot.activeHandles);

      this.collectionCount++;

      // Log at debug level (detailed)
      logger.debug({
        memory: {
          heapUsedMB: Math.round(snapshot.memory.heapUsed / 1024 / 1024),
          heapTotalMB: Math.round(snapshot.memory.heapTotal / 1024 / 1024),
          rssMB: Math.round(snapshot.memory.rss / 1024 / 1024),
          externalMB: Math.round(snapshot.memory.external / 1024 / 1024),
        },
        cpu: snapshot.cpu.toFixed(2),
        eventLoopLagMs: snapshot.eventLoopLag.toFixed(2),
        activeHandles: snapshot.activeHandles,
        collectionCount: this.collectionCount,
      }, "System metrics collected");

    } catch (error) {
      logger.error({
        error: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
      }, "Error collecting system metrics");
    }
  }

  /**
   * Get current system metrics snapshot
   */
  private getSystemMetricsSnapshot(): SystemMetricsSnapshot {
    const timestamp = Date.now();
    const memory = process.memoryUsage();

    // Calculate CPU usage percentage
    const cpuUsage = process.cpuUsage();
    let cpuPercent = 0;

    if (this.lastCpuUsage) {
      // Calculate change in CPU usage (user + system time)
      const userUsageMicros = cpuUsage.user - this.lastCpuUsage.user;
      const systemUsageMicros = cpuUsage.system - this.lastCpuUsage.system;
      const totalUsageMicros = userUsageMicros + systemUsageMicros;

      // Convert to percentage (assuming 30-second interval)
      // Formula: (total microseconds / interval milliseconds / 1000) * 100
      cpuPercent = Math.min((totalUsageMicros / (this.DEFAULT_INTERVAL_MS * 1000)) * 100, 100);
    }

    this.lastCpuUsage = cpuUsage;

    // Measure event loop lag
    const eventLoopLag = this.measureEventLoopLag();

    // Get active handles (rough estimate using process internals)
    const activeHandles = this.getActiveHandlesCount();

    return {
      timestamp,
      memory: {
        heapUsed: memory.heapUsed,
        heapTotal: memory.heapTotal,
        external: memory.external,
        rss: memory.rss,
      },
      cpu: cpuPercent,
      eventLoopLag,
      activeHandles,
    };
  }

  /**
   * Measure event loop lag synchronously
   *
   * This is a simple measurement that checks how long it takes to schedule
   * an immediate callback. In milliseconds.
   */
  private measureEventLoopLag(): number {
    const start = Date.now();
    let lag = 0;

    // Use a synchronous busy-wait to measure lag
    const checkTime = () => {
      lag = Date.now() - start;
    };

    // Schedule callback immediately
    setImmediate(checkTime);

    // Busy-wait for the callback to execute (max 10ms)
    let loopCount = 0;
    while (lag === 0 && loopCount < 10000) {
      loopCount++;
    }

    // If we're still waiting, estimate based on loop count
    if (lag === 0) {
      lag = loopCount > 0 ? loopCount / 100 : 0;
    }

    return lag;
  }

  /**
   * Get approximate count of active handles
   *
   * This is an approximation based on internal Node.js structures.
   * A more accurate method would require native modules.
   */
  private getActiveHandlesCount(): number {
    try {
      // Try to get handles using process._getActiveHandles() (Node.js internal)
      const getActiveHandles = (process as any)._getActiveHandles;
      if (typeof getActiveHandles === "function") {
        return getActiveHandles().length;
      }
    } catch {
      // Silently fail - this is a best-effort measure
    }

    // Fallback: return 0 if unable to get handles
    return 0;
  }

  /**
   * Get current collection status
   */
  isCollecting(): boolean {
    return this.collecting;
  }

  /**
   * Get collection statistics
   */
  getStats(): {
    isCollecting: boolean;
    collectionCount: number;
    intervalMs: number | null;
  } {
    return {
      isCollecting: this.collecting,
      collectionCount: this.collectionCount,
      intervalMs: this.interval ? this.DEFAULT_INTERVAL_MS : null,
    };
  }
}

/**
 * Singleton instance
 */
export const systemMetricsCollector = new SystemMetricsCollector();
