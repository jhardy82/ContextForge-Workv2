/**
 * @fileoverview Standardized Error Types for TaskMan MCP Server
 * 
 * @remarks
 * This module provides a comprehensive error hierarchy implementing:
 * - **Consistent error codes** for programmatic handling
 * - **Retryable vs fatal classification** for resilience patterns
 * - **Structured error context** for debugging and observability
 * - **JSON serialization** for logging and API responses
 * 
 * Error classes follow a clear inheritance hierarchy with {@link AppError}
 * as the base class. Each error type declares whether it's retryable,
 * enabling automatic retry logic in the backend client layer.
 * 
 * @example
 * ```typescript
 * import { NotFoundError, isRetryableError } from './errors';
 * 
 * try {
 *   // operation that may fail
 * } catch (error) {
 *   if (isRetryableError(error)) {
 *     // implement retry logic
 *   } else {
 *     // handle fatal error
 *   }
 * }
 * ```
 * 
 * @module core/errors
 * @category Errors
 */

// ============================================================================
// BASE ERROR CLASS
// ============================================================================

/**
 * Abstract base class for all application errors
 * 
 * @remarks
 * All custom errors in the TaskMan MCP server extend this class.
 * Provides common functionality including:
 * - Unique error codes for categorization
 * - Retryable flag for resilience patterns
 * - Timestamp capture for observability
 * - Structured context for debugging
 * - JSON serialization for logging/API responses
 * 
 * @example
 * ```typescript
 * // Custom error extending AppError
 * class MyCustomError extends AppError {
 *   readonly code = "MY_CUSTOM_ERROR";
 *   readonly retryable = false;
 *   
 *   constructor(message: string) {
 *     super(message, { custom: "context" });
 *   }
 * }
 * ```
 * 
 * @category Errors
 */
export abstract class AppError extends Error {
  /** Unique error code for programmatic handling */
  abstract readonly code: string;
  /** Whether this error type can be retried */
  abstract readonly retryable: boolean;
  /** ISO 8601 timestamp when error was created */
  readonly timestamp: string;
  /** Additional context for debugging */
  readonly context?: Record<string, unknown>;

  constructor(message: string, context?: Record<string, unknown>) {
    super(message);
    this.name = this.constructor.name;
    this.timestamp = new Date().toISOString();
    this.context = context;
    Error.captureStackTrace(this, this.constructor);
  }

  /**
   * Serialize error to JSON for logging/API responses
   * @returns Structured error object
   */
  toJSON() {
    return {
      name: this.name,
      code: this.code,
      message: this.message,
      retryable: this.retryable,
      timestamp: this.timestamp,
      context: this.context,
      stack: this.stack,
    };
  }
}

// ============================================================================
// BACKEND ERRORS (Retryable)
// ============================================================================

/**
 * Backend service unavailable error
 * 
 * @remarks
 * Thrown when the backend API cannot be reached. This is typically
 * a transient condition and should be retried with exponential backoff.
 * 
 * @example
 * ```typescript
 * throw new BackendUnavailableError("API server not responding", {
 *   endpoint: "/api/v1/tasks",
 *   attempts: 3
 * });
 * ```
 * 
 * @category Errors
 */
export class BackendUnavailableError extends AppError {
  readonly code = "BACKEND_UNAVAILABLE";
  readonly retryable = true;

  constructor(message: string = "Backend service is temporarily unavailable", context?: Record<string, unknown>) {
    super(message, context);
  }
}

/**
 * Backend request timeout error
 * 
 * @remarks
 * Thrown when a request to the backend exceeds the configured timeout.
 * Retryable - the operation may succeed on subsequent attempts.
 * 
 * @example
 * ```typescript
 * throw new BackendTimeoutError("Request exceeded 30s limit", {
 *   endpoint: "/api/v1/tasks",
 *   timeoutMs: 30000
 * });
 * ```
 * 
 * @category Errors
 */
export class BackendTimeoutError extends AppError {
  readonly code = "BACKEND_TIMEOUT";
  readonly retryable = true;

  constructor(message: string = "Backend request timed out", context?: Record<string, unknown>) {
    super(message, context);
  }
}

/**
 * Backend error response
 * 
 * @remarks
 * Thrown when the backend returns an error HTTP response.
 * Retryability is determined by status code:
 * - **Retryable**: 429 (rate limit), 500 (server error), 503 (unavailable)
 * - **Not retryable**: 400 (bad request), 404 (not found), 401/403 (auth)
 * 
 * @example
 * ```typescript
 * throw new BackendError("Rate limit exceeded", 429, {
 *   retryAfter: 60,
 *   endpoint: "/api/v1/tasks"
 * });
 * ```
 * 
 * @category Errors
 */
export class BackendError extends AppError {
  readonly code = "BACKEND_ERROR";
  readonly retryable: boolean;
  /** HTTP status code from backend response */
  readonly statusCode?: number;

  constructor(message: string, statusCode?: number, context?: Record<string, unknown>) {
    super(message, context);
    this.statusCode = statusCode;
    // 429, 500, 503 are retryable; 400, 404, etc. are not
    this.retryable = statusCode ? [429, 500, 503].includes(statusCode) : false;
  }
}

// ============================================================================
// CLIENT ERRORS (Not Retryable)
// ============================================================================

/**
 * Validation error
 * 
 * @remarks
 * Thrown when input data fails schema validation. Not retryable
 * because the same input will always fail validation.
 * 
 * @example
 * ```typescript
 * throw new ValidationError("Invalid task status", {
 *   field: "status",
 *   received: "invalid",
 *   expected: ["todo", "in_progress", "completed"]
 * });
 * ```
 * 
 * @category Errors
 */
export class ValidationError extends AppError {
  readonly code = "VALIDATION_ERROR";
  readonly retryable = false;

  constructor(message: string, context?: Record<string, unknown>) {
    super(message, context);
  }
}

/**
 * Resource not found error
 * 
 * @remarks
 * Thrown when a requested resource doesn't exist. Not retryable
 * because the resource won't appear without creation.
 * 
 * @example
 * ```typescript
 * throw new NotFoundError("Task", "TASK-999");
 * // Error message: "Task with ID 'TASK-999' not found"
 * ```
 * 
 * @category Errors
 */
export class NotFoundError extends AppError {
  readonly code = "NOT_FOUND";
  readonly retryable = false;

  constructor(resource: string, id: string, context?: Record<string, unknown>) {
    super(`${resource} with ID '${id}' not found`, { resource, id, ...context });
  }
}

// ============================================================================
// CONCURRENCY & RESILIENCE ERRORS
// ============================================================================

/**
 * Optimistic locking conflict error
 * 
 * @remarks
 * Thrown when a concurrent modification is detected (e.g., ETag mismatch).
 * Retryable - caller should fetch fresh data and retry the operation.
 * 
 * @example
 * ```typescript
 * throw new ConflictError("Task was modified by another process", {
 *   taskId: "TASK-123",
 *   expectedVersion: "v1",
 *   actualVersion: "v2"
 * });
 * ```
 * 
 * @category Errors
 */
export class ConflictError extends AppError {
  readonly code = "CONFLICT";
  readonly retryable = true;

  constructor(message: string, context?: Record<string, unknown>) {
    super(message, context);
  }
}

/**
 * Operation timeout error
 * 
 * @remarks
 * Thrown when an operation exceeds its time budget. Retryable -
 * the operation may complete within the time limit on retry.
 * Includes the timeout value for observability.
 * 
 * @example
 * ```typescript
 * throw new TimeoutError("database_query", 5000, {
 *   query: "SELECT * FROM tasks",
 *   table: "tasks"
 * });
 * // Message: "Operation 'database_query' timed out after 5000ms"
 * ```
 * 
 * @category Errors
 */
export class TimeoutError extends AppError {
  readonly code = "TIMEOUT";
  readonly retryable = true;
  /** The timeout duration that was exceeded (milliseconds) */
  readonly timeoutMs: number;

  constructor(operationName: string, timeoutMs: number, context?: Record<string, unknown>) {
    super(`Operation '${operationName}' timed out after ${timeoutMs}ms`, {
      operationName,
      timeoutMs,
      ...context,
    });
    this.timeoutMs = timeoutMs;
  }
}

/**
 * Circuit breaker open error
 * 
 * @remarks
 * Thrown when the circuit breaker is in open state for a service.
 * Retryable after the circuit breaker's cooldown period expires.
 * This prevents cascading failures when a service is unhealthy.
 * 
 * @example
 * ```typescript
 * throw new CircuitBreakerOpenError("taskman-api", {
 *   failureCount: 10,
 *   lastFailure: "2025-01-01T12:00:00Z",
 *   cooldownMs: 30000
 * });
 * ```
 * 
 * @see {@link https://martinfowler.com/bliki/CircuitBreaker.html} Circuit Breaker Pattern
 * @category Errors
 */
export class CircuitBreakerOpenError extends AppError {
  readonly code = "CIRCUIT_BREAKER_OPEN";
  readonly retryable = true;

  constructor(serviceName: string, context?: Record<string, unknown>) {
    super(`Circuit breaker is open for service '${serviceName}'`, { serviceName, ...context });
  }
}

// ============================================================================
// INTERNAL ERRORS
// ============================================================================

/**
 * Internal application error
 * 
 * @remarks
 * Thrown for unexpected internal failures. Not retryable by default
 * as these typically indicate bugs rather than transient conditions.
 * 
 * @example
 * ```typescript
 * throw new InternalError("Unexpected state in task processor", {
 *   taskId: "TASK-123",
 *   state: "invalid_state"
 * });
 * ```
 * 
 * @category Errors
 */
export class InternalError extends AppError {
  readonly code = "INTERNAL_ERROR";
  readonly retryable = false;

  constructor(message: string, context?: Record<string, unknown>) {
    super(message, context);
  }
}

// ============================================================================
// ERROR UTILITY FUNCTIONS
// ============================================================================

/**
 * Type guard to check if an error is retryable
 * 
 * @remarks
 * Use this function in catch blocks to determine if an operation
 * should be retried. Only returns `true` for {@link AppError}
 * instances with `retryable: true`.
 * 
 * @param error - The error to check
 * @returns `true` if the error is an AppError with retryable flag set
 * 
 * @example
 * ```typescript
 * try {
 *   await createTask(task);
 * } catch (error) {
 *   if (isRetryableError(error)) {
 *     await delay(1000);
 *     await createTask(task); // retry
 *   } else {
 *     throw error; // fatal, don't retry
 *   }
 * }
 * ```
 * 
 * @category Errors
 */
export function isRetryableError(error: unknown): boolean {
  if (error instanceof AppError) {
    return error.retryable;
  }
  return false;
}

/**
 * Extract error message safely from any value
 * 
 * @remarks
 * Handles Error instances, strings, and unknown values gracefully.
 * Useful for logging where the error type is unknown.
 * 
 * @param error - The value to extract a message from
 * @returns The error message string
 * 
 * @example
 * ```typescript
 * catch (error) {
 *   logger.error(getErrorMessage(error));
 *   // Works for Error, string, or any other type
 * }
 * ```
 * 
 * @category Errors
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === "string") {
    return error;
  }
  return "Unknown error occurred";
}

/**
 * Extract error code safely from any value
 * 
 * @remarks
 * Returns the error code for {@link AppError} instances,
 * the error name for standard errors, or "UNKNOWN_ERROR" for other types.
 * Useful for metrics and programmatic error handling.
 * 
 * @param error - The value to extract a code from
 * @returns The error code string
 * 
 * @example
 * ```typescript
 * catch (error) {
 *   metrics.increment(`errors.${getErrorCode(error)}`);
 * }
 * ```
 * 
 * @category Errors
 */
export function getErrorCode(error: unknown): string {
  if (error instanceof AppError) {
    return error.code;
  }
  if (error instanceof Error) {
    return error.name;
  }
  return "UNKNOWN_ERROR";
}
