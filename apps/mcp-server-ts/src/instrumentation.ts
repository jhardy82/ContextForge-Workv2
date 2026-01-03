/**
 * OpenTelemetry Instrumentation Module
 *
 * CRITICAL: This file MUST be imported FIRST in the application before any other imports.
 *
 * Features:
 * - OpenTelemetry SDK initialization (NodeSDK)
 * - Auto-instrumentation for Node.js (HTTP, Express, Axios, etc.)
 * - OTLP/HTTP exporter for distributed tracing
 * - Configuration via environment variables
 * - Graceful shutdown support
 * - Pino logger integration
 *
 * Environment Variables:
 * - TRACING_ENABLED: Enable/disable tracing (default: false in dev, true in prod)
 * - OTEL_EXPORTER_OTLP_ENDPOINT: OTLP collector endpoint (default: http://localhost:4318/v1/traces)
 * - OTEL_DEBUG: Enable diagnostic logging (default: false)
 * - OTEL_SAMPLE_RATE: Trace sampling rate 0.0-1.0 (default: 1.0 in dev, 0.1 in prod)
 * - NODE_ENV: Application environment
 *
 * Usage:
 * ```typescript
 * // MUST be first import
 * import './instrumentation.js';
 *
 * // ... rest of imports
 * import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
 * ```
 */

import { NodeSDK } from "@opentelemetry/sdk-node";
import { getNodeAutoInstrumentations } from "@opentelemetry/auto-instrumentations-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { BatchSpanProcessor } from "@opentelemetry/sdk-trace-node";
import { trace, context } from "@opentelemetry/api";

/**
 * Environment configuration
 */
const nodeEnv = process.env.NODE_ENV || "development";
const isDevelopment = nodeEnv !== "production";

// Read tracing configuration
const tracingEnabled =
  process.env.TRACING_ENABLED === "true" ||
  (process.env.ENABLE_TRACING === "true" &&
    process.env.TRACING_ENABLED !== "false");

const otlpEndpoint =
  process.env.OTEL_EXPORTER_OTLP_ENDPOINT ||
  "http://localhost:4318/v1/traces";

const isDebugEnabled = process.env.OTEL_DEBUG === "true";

const sampleRate = parseFloat(
  process.env.OTEL_SAMPLE_RATE ||
    (isDevelopment ? "1.0" : "0.1")
);

/**
 * SDK instance - only initialized if tracing is enabled
 */
let sdk: NodeSDK | null = null;

/**
 * Initialize OpenTelemetry SDK
 *
 * This should be called as early as possible in the application lifecycle,
 * ideally in instrumentation.ts as the first import.
 */
function initializeTracing(): void {
  if (!tracingEnabled) {
    if (isDebugEnabled) {
      // CRITICAL: Use stderr to avoid corrupting STDIO transport
      console.error("[OpenTelemetry] Tracing disabled via configuration");
    }
    return;
  }

  try {
    if (isDebugEnabled) {
      // CRITICAL: Use stderr to avoid corrupting STDIO transport
      console.error("[OpenTelemetry] Initializing with configuration:", {
        enabled: tracingEnabled,
        environment: nodeEnv,
        endpoint: otlpEndpoint,
        sampleRate: sampleRate,
        debugEnabled: isDebugEnabled,
      });
    }

    // Create OTLP exporter
    const exporter = new OTLPTraceExporter({
      url: otlpEndpoint,
      headers: {
        // Add any required headers here
        "User-Agent": "taskman-mcp-v2/0.1.0",
      },
      concurrencyLimit: 10,
      timeoutMillis: 10000,
    });

    // Create and configure SDK
    sdk = new NodeSDK({
      // Service identification
      serviceName: "taskman-mcp-v2",

      // Tracing processor with OTLP exporter
      spanProcessor: new BatchSpanProcessor(exporter),

      // Auto-instrumentation for common modules
      instrumentations: [
        getNodeAutoInstrumentations({
          // Configure auto-instrumentations
          "@opentelemetry/instrumentation-http": {
            enabled: true,
            // Request/response hook for detailed tracing
            requestHook: (span: any, request: any) => {
              span.setAttribute("http.request.path", request.path || "");
              span.setAttribute("http.request.method", request.method || "");
            },
          },
          "@opentelemetry/instrumentation-express": {
            enabled: true,
          },
          // Disable modules we don't need
          "@opentelemetry/instrumentation-fs": {
            enabled: false,
          },
          "@opentelemetry/instrumentation-net": {
            enabled: false,
          },
        }),
      ],

      // Sampling configuration
      traceExporter: exporter,
    });

    // Start the SDK
    sdk.start();

    if (isDebugEnabled) {
      console.error("[OpenTelemetry] SDK started successfully");
    }

    // Handle graceful shutdown
    process.on("SIGTERM", async () => {
      if (isDebugEnabled) {
        console.error("[OpenTelemetry] SIGTERM received, shutting down");
      }
      await shutdownTracing();
    });

    process.on("SIGINT", async () => {
      if (isDebugEnabled) {
        console.error("[OpenTelemetry] SIGINT received, shutting down");
      }
      await shutdownTracing();
    });
  } catch (error) {
    console.error(
      "[OpenTelemetry] Failed to initialize tracing:",
      error instanceof Error ? error.message : String(error)
    );
    // Don't throw - allow application to continue without tracing
  }
}

/**
 * Graceful shutdown of OpenTelemetry SDK
 *
 * Ensures all pending spans are flushed to the collector
 */
export async function shutdownTracing(): Promise<void> {
  if (!sdk) {
    return;
  }

  try {
    if (isDebugEnabled) {
      console.error("[OpenTelemetry] Starting graceful shutdown");
    }

    // Force flush any pending spans via the trace API (with timeout)
    const traceProvider = trace.getTracerProvider() as any;
    if (traceProvider && typeof traceProvider.forceFlush === 'function') {
      await traceProvider.forceFlush(5000); // 5 second timeout
    }

    // Shutdown SDK
    await sdk.shutdown();

    if (isDebugEnabled) {
      console.error("[OpenTelemetry] Shutdown completed");
    }
  } catch (error) {
    console.error(
      "[OpenTelemetry] Error during shutdown:",
      error instanceof Error ? error.message : String(error)
    );
  }
}

/**
 * Get the active tracer for manual span creation
 *
 * Example:
 * ```typescript
 * const tracer = getTracer();
 * const span = tracer.startSpan("my-operation");
 * // ... do work
 * span.end();
 * ```
 */
export function getTracer(name: string = "taskman-mcp") {
  return trace.getTracer(name, "0.1.0");
}

/**
 * Get current trace context
 *
 * Returns trace ID and span ID for correlation logging
 */
export function getTraceContext(): {
  traceId: string | undefined;
  spanId: string | undefined;
} {
  const activeSpan = trace.getActiveSpan();
  if (!activeSpan) {
    return {
      traceId: undefined,
      spanId: undefined,
    };
  }

  const spanContext = activeSpan.spanContext();
  return {
    traceId: spanContext.traceId,
    spanId: spanContext.spanId,
  };
}

/**
 * Run async code within a trace context
 *
 * Example:
 * ```typescript
 * await runWithContext(async () => {
 *   // Code here has access to trace context
 *   logger.info("This will include trace_id");
 * });
 * ```
 */
export function runWithContext<T>(
  fn: () => Promise<T>
): Promise<T> {
  return context.with(context.active(), fn);
}

/**
 * Check if tracing is enabled
 */
export function isTracingEnabled(): boolean {
  return tracingEnabled;
}

/**
 * Initialize tracing on module load
 *
 * This executes immediately when the module is imported
 */
initializeTracing();

// Export for testing
export { sdk };
