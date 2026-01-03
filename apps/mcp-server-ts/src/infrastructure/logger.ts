/**
 * Structured Logger - Production-grade logging with Pino
 *
 * Features:
 * - JSON structured output for production
 * - Pretty formatting for development
 * - Correlation ID tracking
 * - Performance optimized (no string interpolation)
 * - Log levels: trace, debug, info, warn, error, fatal
 * - Automatic redaction of sensitive fields
 *
 * Usage:
 * ```typescript
 * import { logger } from "./infrastructure/logger.js";
 *
 * logger.info({ userId: "123", action: "login" }, "User logged in");
 * logger.error({ error: err.message, stack: err.stack }, "Operation failed");
 * ```
 */

import pino from "pino";
import { trace } from "@opentelemetry/api";

const isTest = process.env.NODE_ENV === "test";
const isDevelopment = process.env.NODE_ENV !== "production" && !isTest;
const logLevel = process.env.LOG_LEVEL || (isTest ? "silent" : isDevelopment ? "debug" : "info");

// CRITICAL: When using STDIO transport, logs MUST go to stderr
// stdout is reserved for JSON-RPC protocol messages
const isStdioTransport = process.env.TASKMAN_MCP_TRANSPORT === "stdio";

/**
 * Determine transport configuration
 * - Test: No transport (silent logging, no pino-pretty)
 * - STDIO transport: ALWAYS use stderr (CRITICAL for MCP protocol)
 * - Development: pino-pretty for readable output to stderr
 * - Production non-STDIO: raw JSON to stdout (default)
 */
function getTransportConfig(): pino.TransportSingleOptions | undefined {
  // Skip transport in test mode to avoid pino-pretty configuration issues
  if (isTest) {
    return undefined;
  }

  // CRITICAL: STDIO transport MUST use stderr to avoid corrupting JSON-RPC protocol
  // stdout is reserved exclusively for JSON-RPC messages
  if (isStdioTransport) {
    // In production STDIO mode, use pino/file to write JSON to stderr
    if (!isDevelopment) {
      return {
        target: "pino/file",
        options: {
          destination: 2, // stderr (fd 2) - CRITICAL for STDIO transport
        },
      };
    }
    // In development STDIO mode, use pino-pretty to stderr
    return {
      target: "pino-pretty",
      options: {
        colorize: true,
        ignore: "pid,hostname",
        translateTime: "HH:MM:ss.l",
        singleLine: false,
        destination: 2, // stderr - CRITICAL for STDIO transport
      },
    };
  }

  // Development (non-STDIO): pino-pretty for readable output
  if (isDevelopment) {
    return {
      target: "pino-pretty",
      options: {
        colorize: true,
        ignore: "pid,hostname",
        translateTime: "HH:MM:ss.l",
        singleLine: false,
      },
    };
  }

  // Production (non-STDIO): no transport (raw JSON to stdout is fine)
  return undefined;
}

/**
 * Main logger instance
 */
export const logger = pino.default({
  level: logLevel,

  // Configure transport based on environment
  transport: getTransportConfig(),

  // Base fields included in all logs
  base: {
    service: "taskman-mcp-v2",
    environment: process.env.NODE_ENV || "development",
    version: "0.1.0",
  },

  // Timestamp format
  timestamp: pino.stdTimeFunctions.isoTime,

  // Redact sensitive fields to prevent leaking secrets
  redact: {
    paths: [
      "password",
      "token",
      "authorization",
      "cookie",
      "secret",
      "apiKey",
      "api_key",
      "*.password",
      "*.token",
      "*.secret",
      "*.apiKey",
      "*.api_key",
      "req.headers.authorization",
      "req.headers.cookie",
    ],
    censor: "[REDACTED]",
  },

  // Serializers for common objects
  serializers: {
    err: pino.stdSerializers.err,
    error: pino.stdSerializers.err,
    req: pino.stdSerializers.req,
    res: pino.stdSerializers.res,
  },

  // Mixin for automatic trace context injection (Phase 2)
  // This adds trace_id and span_id to ALL log entries when in a trace context
  mixin() {
    const activeSpan = trace.getActiveSpan();
    if (!activeSpan) {
      return {};
    }

    const spanContext = activeSpan.spanContext();
    return {
      trace_id: spanContext.traceId,
      span_id: spanContext.spanId,
      trace_flags: spanContext.traceFlags,
    };
  },
});

/**
 * Create child logger with additional context
 *
 * Example:
 * ```typescript
 * const toolLogger = createContextLogger({ tool: "task_create" });
 * toolLogger.info("Task created");
 * ```
 */
export function createContextLogger(context: Record<string, unknown>): pino.Logger {
  return logger.child(context);
}

/**
 * Logger with correlation ID for tracking request chains
 *
 * Example:
 * ```typescript
 * const reqLogger = withCorrelationLogger("req-123");
 * reqLogger.info("Starting operation");
 * ```
 */
export function withCorrelationLogger(correlationId: string): pino.Logger {
  return logger.child({ correlationId });
}

/**
 * Create a logger for a specific module/component
 *
 * Example:
 * ```typescript
 * const backendLogger = createModuleLogger("backend-client");
 * backendLogger.debug("Making HTTP request");
 * ```
 */
export function createModuleLogger(moduleName: string): pino.Logger {
  return logger.child({ module: moduleName });
}

/**
 * Create a logger with automatic trace context injection
 *
 * Note: Trace context (trace_id, span_id) is now automatically included in ALL logs
 * via the parent logger mixin. This function is kept for API compatibility.
 *
 * Example:
 * ```typescript
 * const log = createTraceLogger();
 * log.info("Operation started"); // Includes trace_id and span_id if in trace context
 * ```
 */
export function createTraceLogger(): pino.Logger {
  // Trace context is automatically injected by parent logger mixin
  return logger;
}

/**
 * Create a module logger with automatic trace context
 *
 * Combines module name context with automatic trace ID injection.
 * Trace context is automatically included via parent logger mixin.
 *
 * Example:
 * ```typescript
 * const log = createModuleTraceLogger("backend-client");
 * log.info("Request sent"); // Includes module, trace_id, span_id
 * ```
 */
export function createModuleTraceLogger(moduleName: string): pino.Logger {
  // Trace context is automatically injected by parent logger mixin
  return logger.child({ module: moduleName });
}

/**
 * Log utility for timing operations
 *
 * Example:
 * ```typescript
 * const timer = startTimer();
 * await doSomething();
 * logger.info({ durationMs: timer() }, "Operation completed");
 * ```
 */
export function startTimer(): () => number {
  const start = Date.now();
  return () => Date.now() - start;
}

/**
 * Wrap async function with automatic logging
 *
 * Example:
 * ```typescript
 * const result = await loggedOperation(
 *   "fetchUser",
 *   { userId: "123" },
 *   async () => await fetchUser("123")
 * );
 * ```
 */
export async function loggedOperation<T>(
  operationName: string,
  context: Record<string, unknown>,
  operation: () => Promise<T>
): Promise<T> {
  const timer = startTimer();
  const opLogger = logger.child({ operation: operationName, ...context });

  opLogger.debug("Operation started");

  try {
    const result = await operation();
    opLogger.info({ durationMs: timer() }, "Operation completed successfully");
    return result;
  } catch (error) {
    opLogger.error(
      {
        durationMs: timer(),
        error: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
      },
      "Operation failed"
    );
    throw error;
  }
}

// Export type for type safety
export type Logger = pino.Logger;
