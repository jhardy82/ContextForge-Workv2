/**
 * Request Context Store - AsyncLocalStorage for request tracking
 *
 * Features:
 * - Request ID propagation across async boundaries
 * - Correlation ID tracking
 * - Automatic context injection in logs
 * - Thread-safe request isolation using Node.js AsyncLocalStorage
 *
 * Usage:
 * ```typescript
 * import { requestContextStore } from "./infrastructure/requestContextStore.js";
 *
 * // Execute operation with request context
 * requestContextStore.runWithContext({ requestId: "req-123" }, () => {
 *   // Any code here can access the request ID
 *   const id = requestContextStore.getRequestId(); // "req-123"
 * });
 * ```
 */

import { AsyncLocalStorage } from "node:async_hooks";
import { randomUUID } from "node:crypto";
import { logger } from "./logger.js";
import type { Logger } from "pino";

/**
 * Request context interface
 */
export interface RequestContext {
  /** Unique identifier for this request */
  requestId: string;

  /** Optional correlation ID for tracking across services */
  correlationId?: string;

  /** Request start timestamp (milliseconds since epoch) */
  startTime: number;

  /** Additional metadata for the request */
  metadata?: Record<string, unknown>;
}

/**
 * Request Context Store using AsyncLocalStorage
 *
 * Provides request-scoped storage that persists across async operations.
 * Each request gets isolated storage that doesn't interfere with concurrent requests.
 */
class RequestContextStore {
  private storage = new AsyncLocalStorage<RequestContext>();

  /**
   * Run operation within a request context
   *
   * Creates a new request context and executes the provided function within it.
   * The context is automatically propagated to all async operations.
   *
   * @param context - Partial context to initialize (requestId auto-generated if not provided)
   * @param fn - Function to execute within the context
   * @returns Result of the function execution
   *
   * @example
   * ```typescript
   * const result = requestContextStore.runWithContext({ correlationId: "trace-123" }, () => {
   *   // Request ID automatically generated
   *   console.log(requestContextStore.getRequestId()); // "req-abc-def-123"
   *   return doWork();
   * });
   * ```
   */
  runWithContext<T>(context: Partial<RequestContext>, fn: () => T): T {
    const fullContext: RequestContext = {
      requestId: context.requestId || `req-${randomUUID()}`,
      correlationId: context.correlationId,
      startTime: context.startTime || Date.now(),
      metadata: context.metadata || {},
    };

    return this.storage.run(fullContext, fn);
  }

  /**
   * Run async operation within a request context
   *
   * Async version of runWithContext.
   *
   * @param context - Partial context to initialize
   * @param fn - Async function to execute within the context
   * @returns Promise resolving to function result
   */
  async runWithContextAsync<T>(
    context: Partial<RequestContext>,
    fn: () => Promise<T>
  ): Promise<T> {
    const fullContext: RequestContext = {
      requestId: context.requestId || `req-${randomUUID()}`,
      correlationId: context.correlationId,
      startTime: context.startTime || Date.now(),
      metadata: context.metadata || {},
    };

    return new Promise((resolve, reject) => {
      this.storage.run(fullContext, async () => {
        try {
          const result = await fn();
          resolve(result);
        } catch (error) {
          reject(error);
        }
      });
    });
  }

  /**
   * Get the current request context
   *
   * @returns Current context, or undefined if not in a context
   *
   * @example
   * ```typescript
   * const context = requestContextStore.getContext();
   * if (context) {
   *   console.log("Request ID:", context.requestId);
   *   console.log("Duration:", Date.now() - context.startTime, "ms");
   * }
   * ```
   */
  getContext(): RequestContext | undefined {
    return this.storage.getStore();
  }

  /**
   * Get the current request ID
   *
   * @returns Request ID, or undefined if not in a context
   */
  getRequestId(): string | undefined {
    const context = this.getContext();
    return context?.requestId;
  }

  /**
   * Get the current correlation ID
   *
   * @returns Correlation ID, or undefined if not in a context or not set
   */
  getCorrelationId(): string | undefined {
    const context = this.getContext();
    return context?.correlationId;
  }

  /**
   * Get request duration in milliseconds
   *
   * @returns Duration since request start, or undefined if not in a context
   */
  getRequestDuration(): number | undefined {
    const context = this.getContext();
    return context ? Date.now() - context.startTime : undefined;
  }

  /**
   * Update metadata in the current context
   *
   * @param metadata - Metadata to merge with existing metadata
   *
   * @example
   * ```typescript
   * requestContextStore.updateMetadata({ userId: "user-123", action: "create" });
   * ```
   */
  updateMetadata(metadata: Record<string, unknown>): void {
    const context = this.getContext();
    if (context && context.metadata) {
      Object.assign(context.metadata, metadata);
    }
  }

  /**
   * Create a child logger with request context automatically injected
   *
   * The returned logger will include requestId and correlationId (if set)
   * in all log entries.
   *
   * @param baseLogger - Base logger to create child from (defaults to global logger)
   * @returns Child logger with request context
   *
   * @example
   * ```typescript
   * const log = requestContextStore.withRequestLogger();
   * log.info("Processing request"); // Includes requestId automatically
   * ```
   */
  withRequestLogger(baseLogger: Logger = logger): Logger {
    const context = this.getContext();
    if (!context) {
      return baseLogger;
    }

    const contextFields: Record<string, string> = {
      requestId: context.requestId,
    };

    if (context.correlationId) {
      contextFields.correlationId = context.correlationId;
    }

    return baseLogger.child(contextFields);
  }

  /**
   * Check if currently executing within a request context
   *
   * @returns True if in a context, false otherwise
   */
  hasContext(): boolean {
    return this.getContext() !== undefined;
  }

  /**
   * Get statistics about the current request context
   *
   * Useful for logging request summaries.
   *
   * @returns Context statistics, or null if not in a context
   */
  getContextStats(): {
    requestId: string;
    correlationId?: string;
    durationMs: number;
    hasMetadata: boolean;
    metadataKeys: string[];
  } | null {
    const context = this.getContext();
    if (!context) {
      return null;
    }

    return {
      requestId: context.requestId,
      correlationId: context.correlationId,
      durationMs: Date.now() - context.startTime,
      hasMetadata: !!context.metadata && Object.keys(context.metadata).length > 0,
      metadataKeys: context.metadata ? Object.keys(context.metadata) : [],
    };
  }
}

/**
 * Singleton instance of RequestContextStore
 *
 * Import and use this instance throughout the application.
 */
export const requestContextStore = new RequestContextStore();

/**
 * Type export for external use
 */
export type { Logger };
