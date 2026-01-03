/**
 * OpenTelemetry Tracing Utilities - Helper functions for manual span management
 *
 * This module wraps the OpenTelemetry API to provide convenient helper functions
 * for creating spans, setting attributes, recording exceptions, and managing
 * span context in async operations.
 *
 * Features:
 * - Span creation and context management
 * - Semantic attributes from OpenTelemetry conventions
 * - Error recording with stack traces
 * - Span status management (OK, ERROR, UNSET)
 * - Context propagation helpers
 * - Type-safe generic support
 *
 * Usage:
 * ```typescript
 * import { withSpan, createSpan, recordException } from "./infrastructure/tracing.js";
 *
 * // Simple span wrapper
 * const result = await withSpan("operation_name", { userId: "123" }, async () => {
 *   return await performOperation();
 * });
 *
 * // Manual span management
 * const span = createSpan("manual_operation");
 * try {
 *   await doSomething();
 *   setSpanStatus(span, { code: SpanStatusCode.OK });
 * } catch (error) {
 *   recordException(span, error);
 *   setSpanStatus(span, { code: SpanStatusCode.ERROR, message: "Operation failed" });
 * }
 * ```
 */

import {
  context,
  trace,
  SpanStatusCode,
  SpanStatus,
  Span,
  Attributes,
  Context,
} from "@opentelemetry/api";
import { createModuleLogger } from "./logger.js";

// Module logger for tracing diagnostics
const log = createModuleLogger("tracing");

/**
 * Tracer instance for creating spans
 */
const tracer = trace.getTracer("taskman-mcp-v2", "0.1.0");

/**
 * Semantic attribute keys from OpenTelemetry conventions
 */
export const SemanticAttributes = {
  // General attributes
  SERVICE_NAME: "service.name",
  SERVICE_VERSION: "service.version",
  SERVICE_INSTANCE_ID: "service.instance.id",

  // Operation attributes
  OPERATION_NAME: "operation.name",
  OPERATION_STATUS: "operation.status",
  OPERATION_DURATION_MS: "operation.duration_ms",

  // Error attributes
  ERROR_TYPE: "error.type",
  ERROR_MESSAGE: "error.message",
  ERROR_STACK: "error.stack",

  // Task attributes
  TASK_ID: "task.id",
  TASK_NAME: "task.name",
  TASK_STATUS: "task.status",
  TASK_PRIORITY: "task.priority",

  // Project attributes
  PROJECT_ID: "project.id",
  PROJECT_NAME: "project.name",

  // User attributes
  USER_ID: "user.id",
  USER_NAME: "user.name",

  // Action list attributes
  ACTION_LIST_ID: "action_list.id",
  ACTION_LIST_NAME: "action_list.name",

  // HTTP attributes
  HTTP_METHOD: "http.method",
  HTTP_URL: "http.url",
  HTTP_STATUS_CODE: "http.status_code",

  // Database attributes
  DB_OPERATION: "db.operation",
  DB_NAME: "db.name",
  DB_STATEMENT: "db.statement",

  // Cache attributes
  CACHE_HIT: "cache.hit",
  CACHE_KEY: "cache.key",
} as const;

/**
 * Create and start a new span with optional attributes
 *
 * @param name - The span name
 * @param attributes - Optional attributes to set on the span
 * @returns The created span
 *
 * Example:
 * ```typescript
 * const span = createSpan("fetch_user", { userId: "123" });
 * ```
 */
export function createSpan(name: string, attributes?: Attributes): Span {
  if (!name) {
    log.warn("createSpan called with empty name");
  }

  const span = tracer.startSpan(name, {
    attributes: {
      [SemanticAttributes.OPERATION_NAME]: name,
      ...attributes,
    },
  });

  log.debug({ span: name, attributes }, "Span created");
  return span;
}

/**
 * Execute a function within a new span context
 *
 * This is the recommended way to use spans as it ensures proper cleanup
 * and context propagation.
 *
 * @param name - The span name
 * @param attributes - Optional attributes to set on the span
 * @param fn - The function to execute within the span
 * @returns The result of the function
 *
 * @throws Re-throws any error from the function
 *
 * Example:
 * ```typescript
 * const user = await withSpan("get_user", { userId: "123" }, async () => {
 *   return await fetchUser("123");
 * });
 * ```
 */
export async function withSpan<T>(
  name: string,
  attributes: Attributes | undefined,
  fn: (span: Span) => Promise<T>
): Promise<T>;

export async function withSpan<T>(
  name: string,
  fn: (span: Span) => Promise<T>
): Promise<T>;

export async function withSpan<T>(
  name: string,
  attributesOrFn?: Attributes | ((span: Span) => Promise<T>),
  fn?: (span: Span) => Promise<T>
): Promise<T> {
  // Handle overloaded signature
  let attributes: Attributes | undefined;
  let actualFn: (span: Span) => Promise<T>;

  if (typeof attributesOrFn === "function") {
    attributes = undefined;
    actualFn = attributesOrFn;
  } else {
    attributes = attributesOrFn;
    actualFn = fn!;
  }

  const span = createSpan(name, attributes);

  try {
    return await context.with(trace.setSpan(context.active(), span), async () => {
      return await actualFn(span);
    });
  } catch (error) {
    // Record exception directly on the span
    if (error instanceof Error) {
      span.recordException(error);
    } else {
      span.recordException(new Error(String(error)));
    }

    // Set span status directly
    span.setStatus({
      code: SpanStatusCode.ERROR,
      message: error instanceof Error ? error.message : String(error),
    });

    throw error;
  } finally {
    span.end();
  }
}

/**
 * Get the currently active span from the context
 *
 * @returns The active span, or a no-op span if no span is active
 *
 * Example:
 * ```typescript
 * const span = getCurrentSpan();
 * span.addEvent("checkpoint", { step: 1 });
 * ```
 */
export function getCurrentSpan(): Span {
  const activeSpan = trace.getActiveSpan();
  if (activeSpan) {
    return activeSpan;
  }

  const spanFromContext = trace.getSpan(context.active());
  if (spanFromContext) {
    return spanFromContext;
  }

  // Return a no-op span as fallback
  const noopSpan = trace.getTracer("default").startSpan("no-op");
  noopSpan.end(); // Immediately end to make it truly no-op
  return noopSpan;
}

/**
 * Set an attribute on the current active span
 *
 * @param key - The attribute key
 * @param value - The attribute value
 *
 * Example:
 * ```typescript
 * setSpanAttribute("userId", "123");
 * setSpanAttribute("duration_ms", 1500);
 * ```
 */
export function setSpanAttribute(key: string, value: string | number | boolean | string[] | number[] | boolean[]): void {
  const span = getCurrentSpan();
  if (span && span.isRecording()) {
    span.setAttribute(key, value);
    log.debug({ key, value }, "Attribute set on span");
  }
}

/**
 * Set multiple attributes on the current active span
 *
 * @param attributes - Object containing attributes to set
 *
 * Example:
 * ```typescript
 * setSpanAttributes({
 *   userId: "123",
 *   duration_ms: 1500,
 *   status: "success"
 * });
 * ```
 */
export function setSpanAttributes(attributes: Attributes): void {
  const span = getCurrentSpan();
  if (span && span.isRecording()) {
    Object.entries(attributes).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        span.setAttribute(key, value);
      }
    });
    log.debug({ count: Object.keys(attributes).length }, "Attributes set on span");
  }
}

/**
 * Set the status of the current active span
 *
 * @param status - The span status (OK, ERROR, or UNSET)
 *
 * Example:
 * ```typescript
 * setSpanStatus({ code: SpanStatusCode.OK });
 * // or
 * setSpanStatus({ code: SpanStatusCode.ERROR, message: "Operation failed" });
 * ```
 */
export function setSpanStatus(status: SpanStatus): void {
  const span = getCurrentSpan();
  if (span && span.isRecording()) {
    span.setStatus(status);
    log.debug({ code: status.code, message: status.message }, "Span status set");
  }
}

/**
 * Record an exception in the current active span
 *
 * This automatically includes the error message and stack trace.
 * The span status is NOT automatically set; use setSpanStatus separately if needed.
 *
 * @param error - The error or exception to record
 * @param attributes - Optional additional attributes for the exception
 *
 * Example:
 * ```typescript
 * try {
 *   await performOperation();
 * } catch (error) {
 *   recordException(error, { operation: "fetch_user" });
 *   setSpanStatus({ code: SpanStatusCode.ERROR });
 * }
 * ```
 */
export function recordException(
  error: unknown,
  attributes?: Attributes
): void {
  const span = getCurrentSpan();

  if (!span || !span.isRecording()) {
    return;
  }

  let errorAttributes: Attributes = attributes || {};

  if (error instanceof Error) {
    span.recordException(error);

    errorAttributes = {
      ...errorAttributes,
      [SemanticAttributes.ERROR_TYPE]: error.constructor.name,
      [SemanticAttributes.ERROR_MESSAGE]: error.message,
      [SemanticAttributes.ERROR_STACK]: error.stack || "(no stack trace)",
    };
  } else {
    span.recordException(new Error(String(error)));

    errorAttributes = {
      ...errorAttributes,
      [SemanticAttributes.ERROR_TYPE]: typeof error,
      [SemanticAttributes.ERROR_MESSAGE]: String(error),
    };
  }

  setSpanAttributes(errorAttributes);
  log.debug({ error: String(error), attributes: errorAttributes }, "Exception recorded in span");
}

/**
 * Add an event to the current active span
 *
 * Events are useful for marking significant points within a span's duration.
 *
 * @param name - The event name
 * @param attributes - Optional attributes for the event
 *
 * Example:
 * ```typescript
 * addSpanEvent("cache_miss", { cacheKey: "user_123" });
 * addSpanEvent("retry", { attempt: 2 });
 * ```
 */
export function addSpanEvent(name: string, attributes?: Attributes): void {
  const span = getCurrentSpan();
  if (span && span.isRecording()) {
    span.addEvent(name, attributes);
    log.debug({ event: name, attributes }, "Event added to span");
  }
}

/**
 * Measure and record the duration of an operation
 *
 * @param operationName - The name of the operation
 * @param fn - The async function to measure
 * @param attributes - Optional attributes to set on the span
 * @returns The result of the function
 *
 * Example:
 * ```typescript
 * const result = await measureOperation("database_query", async () => {
 *   return await db.query("SELECT * FROM users");
 * }, { table: "users" });
 * ```
 */
export async function measureOperation<T>(
  operationName: string,
  fn: () => Promise<T>,
  attributes?: Attributes
): Promise<T> {
  return withSpan(operationName, attributes, async (span) => {
    const startTime = Date.now();

    try {
      const result = await fn();
      const duration = Date.now() - startTime;

      setSpanAttribute(SemanticAttributes.OPERATION_DURATION_MS, duration);
      setSpanAttribute(SemanticAttributes.OPERATION_STATUS, "success");

      return result;
    } catch (error) {
      const duration = Date.now() - startTime;
      setSpanAttribute(SemanticAttributes.OPERATION_DURATION_MS, duration);
      setSpanAttribute(SemanticAttributes.OPERATION_STATUS, "error");
      throw error;
    }
  });
}

/**
 * Run code with a specific context (useful for context propagation in async operations)
 *
 * @param ctx - The context to use
 * @param fn - The function to execute
 * @returns The result of the function
 *
 * Example:
 * ```typescript
 * const result = await runWithContext(spanContext, async () => {
 *   return await performOperation();
 * });
 * ```
 */
export async function runWithContext<T>(
  ctx: Context,
  fn: () => Promise<T>
): Promise<T> {
  return context.with(ctx, async () => {
    return fn();
  });
}

/**
 * Get the current context
 *
 * Useful for propagating context across async boundaries.
 *
 * @returns The active context
 *
 * Example:
 * ```typescript
 * const currentContext = getContext();
 * // Later, in a different async context:
 * await runWithContext(currentContext, async () => {
 *   // Operations here share the parent span
 * });
 * ```
 */
export function getContext(): Context {
  return context.active();
}

/**
 * Export SpanStatusCode for convenient use
 */
export { SpanStatusCode };
