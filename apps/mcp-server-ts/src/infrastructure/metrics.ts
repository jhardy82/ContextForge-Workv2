/**
 * Prometheus Metrics Service - Comprehensive observability
 *
 * Features:
 * - Singleton pattern MetricsService class
 * - 18 metrics across 6 categories (HTTP, MCP, Backend API, Circuit Breaker, Resources, System)
 * - Counters: request_total, tool_executions_total, backend_requests_total, errors
 * - Gauges: active_sessions, cache_size, memory_usage, cpu_usage, health_status
 * - Histograms: request_duration, tool_execution_duration, backend_request_duration
 * - Summary: event_loop_lag
 * - Automatic registration with prom-client default registry
 * - Helper methods for common recording patterns
 *
 * Usage:
 * ```typescript
 * import { metricsService } from "./infrastructure/metrics.js";
 *
 * // Record HTTP request
 * metricsService.recordHttpRequest("GET", "/tasks", 200, 256, 150);
 *
 * // Record tool execution
 * metricsService.recordToolExecution("task_list", true, 320);
 *
 * // Record backend request
 * metricsService.recordBackendRequest("GET", "/tasks", 200, 450);
 *
 * // Record circuit breaker event
 * metricsService.recordCircuitBreakerEvent("tasks", "OPEN");
 *
 * // Get all metrics
 * const metricsOutput = await metricsService.getMetrics();
 * ```
 */

import promClient from "prom-client";
import { config } from "../config/index.js";
import { logger } from "./logger.js";

/**
 * Metric categories and types
 */
interface HttpMetrics {
  request_total: promClient.Counter;
  request_duration_seconds: promClient.Histogram;
  response_size_bytes: promClient.Gauge;
}

interface McpMetrics {
  tool_executions_total: promClient.Counter;
  tool_execution_duration_seconds: promClient.Histogram;
}

interface BackendApiMetrics {
  backend_requests_total: promClient.Counter;
  backend_request_duration_seconds: promClient.Histogram;
  backend_errors_total: promClient.Counter;
}

interface CircuitBreakerMetrics {
  circuit_breaker_state: promClient.Gauge;
  circuit_breaker_failures_total: promClient.Counter;
}

interface ResourceMetrics {
  active_sessions: promClient.Gauge;
  cache_size: promClient.Gauge;
  cache_hits_total: promClient.Counter;
  cache_misses_total: promClient.Counter;
}

interface SystemMetrics {
  nodejs_memory_usage_bytes: promClient.Gauge;
  nodejs_cpu_usage_percent: promClient.Gauge;
  nodejs_event_loop_lag_seconds: promClient.Summary;
  nodejs_active_handles: promClient.Gauge;
}

/**
 * Circuit breaker state enum
 */
enum CircuitBreakerState {
  CLOSED = 0,
  OPEN = 1,
  HALF_OPEN = 2,
}

/**
 * MetricsService - Singleton for managing all metrics
 */
class MetricsService {
  private initialized = false;
  private enabledMetrics: boolean;

  // HTTP Metrics
  private http_request_total?: promClient.Counter;
  private http_request_duration_seconds?: promClient.Histogram;
  private http_response_size_bytes?: promClient.Gauge;

  // MCP Metrics
  private mcp_tool_executions_total?: promClient.Counter;
  private mcp_tool_execution_duration_seconds?: promClient.Histogram;

  // Backend API Metrics
  private backend_requests_total?: promClient.Counter;
  private backend_request_duration_seconds?: promClient.Histogram;
  private backend_errors_total?: promClient.Counter;

  // Circuit Breaker Metrics
  private circuit_breaker_state?: promClient.Gauge;
  private circuit_breaker_failures_total?: promClient.Counter;

  // Resource Metrics
  private active_sessions?: promClient.Gauge;
  private cache_size?: promClient.Gauge;
  private cache_hits_total?: promClient.Counter;
  private cache_misses_total?: promClient.Counter;

  // System Metrics
  private nodejs_memory_usage_bytes?: promClient.Gauge;
  private nodejs_cpu_usage_percent?: promClient.Gauge;
  private nodejs_event_loop_lag_seconds?: promClient.Summary;
  private nodejs_active_handles?: promClient.Gauge;

  constructor() {
    this.enabledMetrics = config.ENABLE_METRICS;
  }

  /**
   * Initialize all metrics
   */
  initialize(): void {
    if (this.initialized) {
      logger.warn("Metrics already initialized, skipping");
      return;
    }

    if (!this.enabledMetrics) {
      logger.info("Metrics disabled by configuration (ENABLE_METRICS=false)");
      return;
    }

    logger.info("Initializing Prometheus metrics service");

    try {
      // HTTP Metrics
      this.http_request_total = new promClient.Counter({
        name: "taskman_http_requests_total",
        help: "Total number of HTTP requests received",
        labelNames: ["method", "route", "status"],
      });

      this.http_request_duration_seconds = new promClient.Histogram({
        name: "taskman_http_request_duration_seconds",
        help: "HTTP request duration in seconds",
        labelNames: ["method", "route", "status"],
        buckets: [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
      });

      this.http_response_size_bytes = new promClient.Gauge({
        name: "taskman_http_response_size_bytes",
        help: "Size of HTTP response in bytes",
        labelNames: ["method", "route"],
      });

      // MCP Metrics
      this.mcp_tool_executions_total = new promClient.Counter({
        name: "taskman_mcp_tool_executions_total",
        help: "Total number of MCP tool executions",
        labelNames: ["tool_name", "status"],
      });

      this.mcp_tool_execution_duration_seconds = new promClient.Histogram({
        name: "taskman_mcp_tool_execution_duration_seconds",
        help: "MCP tool execution duration in seconds",
        labelNames: ["tool_name"],
        buckets: [0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30],
      });

      // Backend API Metrics
      this.backend_requests_total = new promClient.Counter({
        name: "taskman_backend_api_requests_total",
        help: "Total number of backend API requests",
        labelNames: ["method", "endpoint", "status"],
      });

      this.backend_request_duration_seconds = new promClient.Histogram({
        name: "taskman_backend_api_request_duration_seconds",
        help: "Backend API request duration in seconds",
        labelNames: ["method", "endpoint"],
        buckets: [0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
      });

      this.backend_errors_total = new promClient.Counter({
        name: "taskman_backend_api_errors_total",
        help: "Total number of backend API errors",
        labelNames: ["method", "endpoint", "error_type"],
      });

      // Circuit Breaker Metrics
      this.circuit_breaker_state = new promClient.Gauge({
        name: "taskman_circuit_breaker_state",
        help: "Circuit breaker state (0=CLOSED, 1=OPEN, 2=HALF_OPEN)",
        labelNames: ["service"],
      });

      this.circuit_breaker_failures_total = new promClient.Counter({
        name: "taskman_circuit_breaker_failures_total",
        help: "Total number of circuit breaker failures",
        labelNames: ["service"],
      });

      // Resource Metrics
      this.active_sessions = new promClient.Gauge({
        name: "taskman_active_sessions",
        help: "Number of active client sessions",
      });

      this.cache_size = new promClient.Gauge({
        name: "taskman_cache_size",
        help: "Current size of the fallback cache",
      });

      this.cache_hits_total = new promClient.Counter({
        name: "taskman_cache_hits_total",
        help: "Total number of cache hits",
      });

      this.cache_misses_total = new promClient.Counter({
        name: "taskman_cache_misses_total",
        help: "Total number of cache misses",
      });

      // System Metrics
      this.nodejs_memory_usage_bytes = new promClient.Gauge({
        name: "taskman_nodejs_memory_usage_bytes",
        help: "Node.js memory usage in bytes",
        labelNames: ["type"],
      });

      this.nodejs_cpu_usage_percent = new promClient.Gauge({
        name: "taskman_nodejs_cpu_usage_percent",
        help: "Node.js CPU usage percentage (0-100)",
      });

      this.nodejs_event_loop_lag_seconds = new promClient.Summary({
        name: "taskman_nodejs_event_loop_lag_seconds",
        help: "Node.js event loop lag in seconds",
        percentiles: [0.5, 0.9, 0.99],
      });

      this.nodejs_active_handles = new promClient.Gauge({
        name: "taskman_nodejs_active_handles",
        help: "Number of active handles in Node.js",
      });

      this.initialized = true;
      logger.info("Prometheus metrics initialized successfully (18 metrics)");
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      logger.error(
        {
          error: errorMessage,
          stack: error instanceof Error ? error.stack : undefined,
        },
        "Failed to initialize metrics"
      );
      throw error;
    }
  }

  /**
   * Check if metrics are enabled and initialized
   */
  isEnabled(): boolean {
    return this.enabledMetrics && this.initialized;
  }

  /**
   * Record HTTP request metrics
   */
  recordHttpRequest(
    method: string,
    route: string,
    statusCode: number,
    responseSize: number,
    durationMs: number
  ): void {
    if (!this.isEnabled()) return;

    const durationSeconds = durationMs / 1000;

    this.http_request_total?.inc({
      method: method.toUpperCase(),
      route,
      status: statusCode,
    });

    this.http_request_duration_seconds?.observe(
      {
        method: method.toUpperCase(),
        route,
        status: statusCode,
      },
      durationSeconds
    );

    this.http_response_size_bytes?.set(
      {
        method: method.toUpperCase(),
        route,
      },
      responseSize
    );
  }

  /**
   * Record MCP tool execution
   */
  recordToolExecution(
    toolName: string,
    success: boolean,
    durationMs: number
  ): void {
    if (!this.isEnabled()) return;

    const durationSeconds = durationMs / 1000;
    const status = success ? "success" : "error";

    this.mcp_tool_executions_total?.inc({
      tool_name: toolName,
      status,
    });

    this.mcp_tool_execution_duration_seconds?.observe(
      { tool_name: toolName },
      durationSeconds
    );
  }

  /**
   * Record backend API request
   */
  recordBackendRequest(
    method: string,
    endpoint: string,
    statusCode: number,
    durationMs: number,
    errorType?: string
  ): void {
    if (!this.isEnabled()) return;

    const durationSeconds = durationMs / 1000;

    this.backend_requests_total?.inc({
      method: method.toUpperCase(),
      endpoint,
      status: statusCode,
    });

    this.backend_request_duration_seconds?.observe(
      {
        method: method.toUpperCase(),
        endpoint,
      },
      durationSeconds
    );

    // Record error if present
    if (errorType) {
      this.backend_errors_total?.inc({
        method: method.toUpperCase(),
        endpoint,
        error_type: errorType,
      });
    }
  }

  /**
   * Record circuit breaker event
   */
  recordCircuitBreakerEvent(service: string, state: string): void {
    if (!this.isEnabled()) return;

    const stateValue = this.parseCircuitBreakerState(state);

    this.circuit_breaker_state?.set(
      { service },
      stateValue
    );

    if (state === "OPEN") {
      this.circuit_breaker_failures_total?.inc({ service });
    }
  }

  /**
   * Record cache operation
   */
  recordCacheHit(): void {
    if (!this.isEnabled()) return;
    this.cache_hits_total?.inc();
  }

  recordCacheMiss(): void {
    if (!this.isEnabled()) return;
    this.cache_misses_total?.inc();
  }

  /**
   * Update cache size gauge
   */
  setCacheSize(size: number): void {
    if (!this.isEnabled()) return;
    this.cache_size?.set(size);
  }

  /**
   * Update active sessions gauge
   */
  setActiveSessions(count: number): void {
    if (!this.isEnabled()) return;
    this.active_sessions?.set(count);
  }

  /**
   * Record system metrics
   */
  recordSystemMetrics(memoryUsage: NodeJS.MemoryUsage, cpuUsagePercent: number): void {
    if (!this.isEnabled()) return;

    // Record memory metrics
    this.nodejs_memory_usage_bytes?.set({ type: "heapUsed" }, memoryUsage.heapUsed);
    this.nodejs_memory_usage_bytes?.set({ type: "heapTotal" }, memoryUsage.heapTotal);
    this.nodejs_memory_usage_bytes?.set({ type: "rss" }, memoryUsage.rss);
    this.nodejs_memory_usage_bytes?.set({ type: "external" }, memoryUsage.external);

    // Record CPU usage
    this.nodejs_cpu_usage_percent?.set(cpuUsagePercent);
  }

  /**
   * Record event loop lag
   */
  recordEventLoopLag(lagMs: number): void {
    if (!this.isEnabled()) return;
    const lagSeconds = lagMs / 1000;
    this.nodejs_event_loop_lag_seconds?.observe(lagSeconds);
  }

  /**
   * Update active handles count
   */
  setActiveHandles(count: number): void {
    if (!this.isEnabled()) return;
    this.nodejs_active_handles?.set(count);
  }

  /**
   * Get all metrics as Prometheus text format
   */
  async getMetrics(): Promise<string> {
    if (!this.isEnabled()) {
      return "# Metrics disabled\n";
    }

    try {
      return await promClient.register.metrics();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      logger.error(
        { error: errorMessage },
        "Failed to generate metrics output"
      );
      return "# Error generating metrics\n";
    }
  }

  /**
   * Reset all metrics (primarily for testing)
   */
  reset(): void {
    if (!this.isEnabled()) return;

    try {
      promClient.register.clear();
      this.initialized = false;
      logger.info("Metrics cleared");
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      logger.error(
        { error: errorMessage },
        "Failed to reset metrics"
      );
    }
  }

  /**
   * Helper: Parse circuit breaker state string to numeric value
   */
  private parseCircuitBreakerState(state: string): number {
    switch (state.toUpperCase()) {
      case "CLOSED":
        return CircuitBreakerState.CLOSED;
      case "OPEN":
        return CircuitBreakerState.OPEN;
      case "HALF_OPEN":
        return CircuitBreakerState.HALF_OPEN;
      default:
        return CircuitBreakerState.CLOSED;
    }
  }

  /**
   * Get detailed metrics summary (for monitoring/debugging)
   */
  getMetricsSummary(): {
    enabled: boolean;
    initialized: boolean;
    metricCount: number;
  } {
    return {
      enabled: this.enabledMetrics,
      initialized: this.initialized,
      metricCount: this.initialized ? 18 : 0,
    };
  }
}

/**
 * Singleton instance
 */
export const metricsService = new MetricsService();

/**
 * Export types for use in other modules
 */
export type { HttpMetrics, McpMetrics, BackendApiMetrics, CircuitBreakerMetrics, ResourceMetrics, SystemMetrics };
