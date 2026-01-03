/**
 * Health Check Service - Kubernetes-compatible health probes
 *
 * Provides three types of health checks:
 * - Liveness: Is the process alive and responsive?
 * - Readiness: Can the service accept traffic?
 * - Startup: Has initialization completed?
 *
 * Endpoints:
 * - GET /health/live
 * - GET /health/ready
 * - GET /health/startup
 */

import { backendClient } from "../backend/client.js";
import { logger } from "./logger.js";
import { config } from "../config/index.js";

export interface HealthStatus {
  status: "ok" | "degraded" | "down";
  timestamp: string;
  uptime: number;
  checks: Record<string, HealthCheckResult>;
}

export interface HealthCheckResult {
  status: "pass" | "warn" | "fail";
  time?: string;
  output?: string;
  observedValue?: number | string;
  observedUnit?: string;
}

class HealthCheckService {
  private isStartupComplete = false;
  private lastBackendCheckTime = 0;
  private lastBackendCheckResult: HealthCheckResult | null = null;
  private readonly BACKEND_CHECK_CACHE_MS = 5000; // Cache for 5 seconds

  /**
   * Mark startup as complete
   * Call this after all initialization is done
   */
  markStartupComplete(): void {
    this.isStartupComplete = true;
    logger.info("Server startup complete");
  }

  /**
   * Liveness check - Is the process alive?
   *
   * This should always pass unless the process is completely hung.
   * Kubernetes will restart the pod if this fails.
   */
  async checkLiveness(): Promise<HealthStatus> {
    const checks: Record<string, HealthCheckResult> = {
      uptime: this.checkUptime(),
      memory: this.checkMemory(),
      eventLoop: await this.checkEventLoop(),
    };

    return {
      status: "ok",
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      checks,
    };
  }

  /**
   * Readiness check - Can the server accept traffic?
   *
   * This checks dependencies and should fail if the service
   * cannot properly handle requests.
   */
  async checkReadiness(): Promise<HealthStatus> {
    const checks: Record<string, HealthCheckResult> = {
      startup: {
        status: this.isStartupComplete ? "pass" : "fail",
        output: this.isStartupComplete ? "Complete" : "In progress",
      },
      memory: this.checkMemory(),
    };

    // Check backend connectivity (with caching)
    checks.backend = await this.checkBackend();

    // Determine overall status
    const hasFailures = Object.values(checks).some((c) => c.status === "fail");
    const hasWarnings = Object.values(checks).some((c) => c.status === "warn");

    return {
      status: hasFailures ? "down" : hasWarnings ? "degraded" : "ok",
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      checks,
    };
  }

  /**
   * Startup check - Has initialization completed?
   *
   * This is used during pod startup to delay traffic until ready.
   */
  async checkStartup(): Promise<HealthStatus> {
    const checks: Record<string, HealthCheckResult> = {
      startup: {
        status: this.isStartupComplete ? "pass" : "fail",
        output: this.isStartupComplete
          ? "Initialization complete"
          : "Waiting for startup",
      },
    };

    return {
      status: this.isStartupComplete ? "ok" : "down",
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      checks,
    };
  }

  /**
   * Check process uptime
   */
  private checkUptime(): HealthCheckResult {
    const uptimeSeconds = process.uptime();

    return {
      status: "pass",
      output: this.formatDuration(uptimeSeconds * 1000),
      observedValue: uptimeSeconds,
      observedUnit: "seconds",
    };
  }

  /**
   * Check memory usage
   */
  private checkMemory(): HealthCheckResult {
    const usage = process.memoryUsage();
    const heapUsedMB = usage.heapUsed / 1024 / 1024;
    const heapTotalMB = usage.heapTotal / 1024 / 1024;
    const heapPercent = (heapUsedMB / heapTotalMB) * 100;

    // Warn if heap usage is over 85%, fail if over 95%
    const status = heapPercent > 95 ? "fail" : heapPercent > 85 ? "warn" : "pass";

    return {
      status,
      output: `${heapUsedMB.toFixed(2)}MB / ${heapTotalMB.toFixed(2)}MB (${heapPercent.toFixed(1)}%)`,
      observedValue: heapPercent,
      observedUnit: "percent",
    };
  }

  /**
   * Check event loop lag (basic check)
   */
  private checkEventLoop(): Promise<HealthCheckResult> {
    // Simple check: measure time to execute setImmediate
    const start = Date.now();

    return new Promise<HealthCheckResult>((resolve) => {
      setImmediate(() => {
        const lag = Date.now() - start;

        // Warn if lag > 100ms, fail if > 1000ms
        const status = lag > 1000 ? "fail" : lag > 100 ? "warn" : "pass";

        resolve({
          status,
          output: `${lag}ms lag`,
          observedValue: lag,
          observedUnit: "milliseconds",
        });
      });
    });
  }

  /**
   * Check backend connectivity (with caching to avoid hammering)
   */
  private async checkBackend(): Promise<HealthCheckResult> {
    const now = Date.now();

    // Return cached result if recent
    if (
      this.lastBackendCheckResult &&
      now - this.lastBackendCheckTime < this.BACKEND_CHECK_CACHE_MS
    ) {
      return this.lastBackendCheckResult;
    }

    try {
      const start = Date.now();
      await backendClient.health();
      const duration = Date.now() - start;

      // Warn if response time > 1s, fail if > 5s
      const status = duration > 5000 ? "fail" : duration > 1000 ? "warn" : "pass";

      this.lastBackendCheckResult = {
        status,
        time: `${duration}ms`,
        output: status === "pass" ? "Healthy" : duration > 5000 ? "Unhealthy" : "Slow response",
        observedValue: duration,
        observedUnit: "milliseconds",
      };

      this.lastBackendCheckTime = now;
      return this.lastBackendCheckResult;

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unreachable";

      this.lastBackendCheckResult = {
        status: "fail",
        output: errorMessage,
      };

      this.lastBackendCheckTime = now;
      return this.lastBackendCheckResult;
    }
  }

  /**
   * Format duration in human-readable format
   */
  private formatDuration(ms: number): string {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) {
      return `${days}d ${hours % 24}h`;
    } else if (hours > 0) {
      return `${hours}h ${minutes % 60}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    } else {
      return `${seconds}s`;
    }
  }

  /**
   * Get detailed system information (for debugging)
   */
  getSystemInfo(): Record<string, unknown> {
    const memUsage = process.memoryUsage();

    return {
      node_version: process.version,
      platform: process.platform,
      arch: process.arch,
      uptime_seconds: process.uptime(),
      memory: {
        heap_used_mb: (memUsage.heapUsed / 1024 / 1024).toFixed(2),
        heap_total_mb: (memUsage.heapTotal / 1024 / 1024).toFixed(2),
        rss_mb: (memUsage.rss / 1024 / 1024).toFixed(2),
        external_mb: (memUsage.external / 1024 / 1024).toFixed(2),
      },
      config: {
        node_env: config.NODE_ENV,
        transport: config.TASKMAN_MCP_TRANSPORT,
        persistence: config.ENABLE_PERSISTENCE,
        metrics: config.ENABLE_METRICS,
        tracing: config.ENABLE_TRACING,
      },
    };
  }
}

// Singleton instance
export const healthCheckService = new HealthCheckService();

/**
 * Health Status Interface - Used by health service tests
 */
export interface HealthServiceStatus {
  healthy: boolean;
  timestamp: string;
  services: {
    backend: {
      healthy: boolean;
      latencyMs?: number;
      error?: string;
    };
    locking: {
      healthy: boolean;
      activeLocks: number;
      oldestLockAgeMs: number | null;
    };
    audit: {
      healthy: boolean;
      logCount: number;
    };
  };
}

/**
 * Health Service - Provides simple health check API
 * Used for quick health status checks and integration with monitoring
 */
class HealthService {
  /**
   * Get comprehensive health status including all services
   */
  async getHealthStatus(): Promise<HealthServiceStatus> {
    // Lazy import to avoid circular dependencies
    const { auditService } = await import("./audit.js");
    const { lockingService } = await import("./locking.js");

    // Check backend health with timing
    let backendHealthy = false;
    let backendLatencyMs: number | undefined;
    let backendError: string | undefined;

    const startTime = Date.now();
    try {
      await backendClient.health();
      backendHealthy = true;
      backendLatencyMs = Date.now() - startTime;
    } catch (error) {
      backendHealthy = false;
      if (error instanceof Error) {
        backendError = error.message;
      } else {
        backendError = "Unknown error";
      }
    }

    // Get locking service stats
    const allLocks = lockingService.getAllLocks();
    const activeLocks = allLocks.length;
    let oldestLockAgeMs: number | null = null;

    if (allLocks.length > 0) {
      const now = Date.now();
      const oldestLock = allLocks.reduce((oldest, lock) =>
        lock.timestamp < oldest.timestamp ? lock : oldest
      );
      oldestLockAgeMs = now - oldestLock.timestamp;
    }

    // Get audit service stats (use getRecentLogs as getLogs doesn't exist)
    const auditLogs = auditService.getRecentLogs(1000);
    const logCount = auditLogs.length;

    return {
      healthy: backendHealthy,
      timestamp: new Date().toISOString(),
      services: {
        backend: {
          healthy: backendHealthy,
          latencyMs: backendLatencyMs,
          error: backendError,
        },
        locking: {
          healthy: true, // Locking service is always healthy if running
          activeLocks,
          oldestLockAgeMs,
        },
        audit: {
          healthy: true, // Audit service is always healthy if running
          logCount,
        },
      },
    };
  }

  /**
   * Quick health check - returns true if backend is reachable
   */
  async isHealthy(): Promise<boolean> {
    try {
      await backendClient.health();
      return true;
    } catch {
      return false;
    }
  }
}

// Export singleton health service instance
export const healthService = new HealthService();
