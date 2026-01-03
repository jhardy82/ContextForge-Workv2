/**
 * Error Classes Tests
 *
 * Tests for standardized error types with consistent error codes,
 * retryable classification, and structured error context.
 *
 * @module core/errors.test
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  AppError,
  BackendUnavailableError,
  BackendTimeoutError,
  BackendError,
  ValidationError,
  NotFoundError,
  ConflictError,
  TimeoutError,
  CircuitBreakerOpenError,
  InternalError,
  isRetryableError,
  getErrorMessage,
  getErrorCode,
} from "./errors.js";

describe("Error Classes", () => {
  describe("BackendUnavailableError", () => {
    it("should have correct code", () => {
      const error = new BackendUnavailableError();
      expect(error.code).toBe("BACKEND_UNAVAILABLE");
    });

    it("should be retryable", () => {
      const error = new BackendUnavailableError();
      expect(error.retryable).toBe(true);
    });

    it("should have default message", () => {
      const error = new BackendUnavailableError();
      expect(error.message).toBe("Backend service is temporarily unavailable");
    });

    it("should accept custom message", () => {
      const error = new BackendUnavailableError("Custom unavailable message");
      expect(error.message).toBe("Custom unavailable message");
    });

    it("should accept context", () => {
      const error = new BackendUnavailableError("Error", { service: "api" });
      expect(error.context).toEqual({ service: "api" });
    });

    it("should have timestamp", () => {
      const error = new BackendUnavailableError();
      expect(error.timestamp).toBeDefined();
      expect(new Date(error.timestamp).getTime()).toBeLessThanOrEqual(Date.now());
    });

    it("should have stack trace", () => {
      const error = new BackendUnavailableError();
      expect(error.stack).toBeDefined();
    });
  });

  describe("BackendTimeoutError", () => {
    it("should have correct code", () => {
      const error = new BackendTimeoutError();
      expect(error.code).toBe("BACKEND_TIMEOUT");
    });

    it("should be retryable", () => {
      const error = new BackendTimeoutError();
      expect(error.retryable).toBe(true);
    });

    it("should have default message", () => {
      const error = new BackendTimeoutError();
      expect(error.message).toBe("Backend request timed out");
    });
  });

  describe("BackendError", () => {
    it("should have correct code", () => {
      const error = new BackendError("Server error");
      expect(error.code).toBe("BACKEND_ERROR");
    });

    it("should store status code", () => {
      const error = new BackendError("Server error", 500);
      expect(error.statusCode).toBe(500);
    });

    it("should be retryable for 429 status", () => {
      const error = new BackendError("Rate limited", 429);
      expect(error.retryable).toBe(true);
    });

    it("should be retryable for 500 status", () => {
      const error = new BackendError("Server error", 500);
      expect(error.retryable).toBe(true);
    });

    it("should be retryable for 503 status", () => {
      const error = new BackendError("Service unavailable", 503);
      expect(error.retryable).toBe(true);
    });

    it("should not be retryable for 400 status", () => {
      const error = new BackendError("Bad request", 400);
      expect(error.retryable).toBe(false);
    });

    it("should not be retryable for 404 status", () => {
      const error = new BackendError("Not found", 404);
      expect(error.retryable).toBe(false);
    });

    it("should not be retryable for 401 status", () => {
      const error = new BackendError("Unauthorized", 401);
      expect(error.retryable).toBe(false);
    });

    it("should not be retryable when no status code provided", () => {
      const error = new BackendError("Unknown error");
      expect(error.retryable).toBe(false);
    });
  });

  describe("ValidationError", () => {
    it("should have correct code", () => {
      const error = new ValidationError("Invalid input");
      expect(error.code).toBe("VALIDATION_ERROR");
    });

    it("should not be retryable", () => {
      const error = new ValidationError("Invalid input");
      expect(error.retryable).toBe(false);
    });

    it("should accept context with validation details", () => {
      const error = new ValidationError("Invalid email", {
        field: "email",
        value: "not-an-email",
      });
      expect(error.context).toEqual({
        field: "email",
        value: "not-an-email",
      });
    });
  });

  describe("NotFoundError", () => {
    it("should have correct code", () => {
      const error = new NotFoundError("Task", "123");
      expect(error.code).toBe("NOT_FOUND");
    });

    it("should not be retryable", () => {
      const error = new NotFoundError("Task", "123");
      expect(error.retryable).toBe(false);
    });

    it("should format message with resource and id", () => {
      const error = new NotFoundError("User", "abc-123");
      expect(error.message).toBe("User with ID 'abc-123' not found");
    });

    it("should include resource and id in context", () => {
      const error = new NotFoundError("Project", "proj-001");
      expect(error.context).toMatchObject({
        resource: "Project",
        id: "proj-001",
      });
    });

    it("should merge additional context", () => {
      const error = new NotFoundError("Task", "123", { workspace: "default" });
      expect(error.context).toMatchObject({
        resource: "Task",
        id: "123",
        workspace: "default",
      });
    });
  });

  describe("ConflictError", () => {
    it("should have correct code", () => {
      const error = new ConflictError("Version mismatch");
      expect(error.code).toBe("CONFLICT");
    });

    it("should be retryable", () => {
      const error = new ConflictError("Version mismatch");
      expect(error.retryable).toBe(true);
    });
  });

  describe("TimeoutError", () => {
    it("should have correct code", () => {
      const error = new TimeoutError("fetchData", 5000);
      expect(error.code).toBe("TIMEOUT");
    });

    it("should be retryable", () => {
      const error = new TimeoutError("fetchData", 5000);
      expect(error.retryable).toBe(true);
    });

    it("should store timeout duration", () => {
      const error = new TimeoutError("fetchData", 5000);
      expect(error.timeoutMs).toBe(5000);
    });

    it("should format message with operation and duration", () => {
      const error = new TimeoutError("fetchData", 5000);
      expect(error.message).toBe("Operation 'fetchData' timed out after 5000ms");
    });

    it("should include operation name and timeout in context", () => {
      const error = new TimeoutError("apiCall", 3000);
      expect(error.context).toMatchObject({
        operationName: "apiCall",
        timeoutMs: 3000,
      });
    });
  });

  describe("CircuitBreakerOpenError", () => {
    it("should have correct code", () => {
      const error = new CircuitBreakerOpenError("database");
      expect(error.code).toBe("CIRCUIT_BREAKER_OPEN");
    });

    it("should be retryable", () => {
      const error = new CircuitBreakerOpenError("database");
      expect(error.retryable).toBe(true);
    });

    it("should format message with service name", () => {
      const error = new CircuitBreakerOpenError("payment-service");
      expect(error.message).toBe("Circuit breaker is open for service 'payment-service'");
    });

    it("should include service name in context", () => {
      const error = new CircuitBreakerOpenError("api");
      expect(error.context).toMatchObject({
        serviceName: "api",
      });
    });
  });

  describe("InternalError", () => {
    it("should have correct code", () => {
      const error = new InternalError("Unexpected error");
      expect(error.code).toBe("INTERNAL_ERROR");
    });

    it("should not be retryable", () => {
      const error = new InternalError("Unexpected error");
      expect(error.retryable).toBe(false);
    });
  });

  describe("AppError base class", () => {
    it("should set correct name", () => {
      const error = new ValidationError("test");
      expect(error.name).toBe("ValidationError");
    });

    describe("toJSON", () => {
      it("should serialize error to JSON", () => {
        const error = new ValidationError("Invalid input", { field: "name" });
        const json = error.toJSON();

        expect(json).toMatchObject({
          name: "ValidationError",
          code: "VALIDATION_ERROR",
          message: "Invalid input",
          retryable: false,
          context: { field: "name" },
        });
        expect(json.timestamp).toBeDefined();
        expect(json.stack).toBeDefined();
      });

      it("should include all properties in JSON", () => {
        const error = new NotFoundError("Task", "123");
        const json = error.toJSON();

        expect(Object.keys(json)).toContain("name");
        expect(Object.keys(json)).toContain("code");
        expect(Object.keys(json)).toContain("message");
        expect(Object.keys(json)).toContain("retryable");
        expect(Object.keys(json)).toContain("timestamp");
        expect(Object.keys(json)).toContain("context");
        expect(Object.keys(json)).toContain("stack");
      });
    });
  });

  describe("isRetryableError", () => {
    it("should return true for retryable AppErrors", () => {
      expect(isRetryableError(new BackendUnavailableError())).toBe(true);
      expect(isRetryableError(new BackendTimeoutError())).toBe(true);
      expect(isRetryableError(new BackendError("error", 500))).toBe(true);
      expect(isRetryableError(new ConflictError("conflict"))).toBe(true);
      expect(isRetryableError(new TimeoutError("op", 1000))).toBe(true);
      expect(isRetryableError(new CircuitBreakerOpenError("svc"))).toBe(true);
    });

    it("should return false for non-retryable AppErrors", () => {
      expect(isRetryableError(new ValidationError("invalid"))).toBe(false);
      expect(isRetryableError(new NotFoundError("Task", "1"))).toBe(false);
      expect(isRetryableError(new InternalError("error"))).toBe(false);
      expect(isRetryableError(new BackendError("error", 400))).toBe(false);
    });

    it("should return false for non-AppError errors", () => {
      expect(isRetryableError(new Error("generic error"))).toBe(false);
      expect(isRetryableError(new TypeError("type error"))).toBe(false);
    });

    it("should return false for non-error values", () => {
      expect(isRetryableError("string error")).toBe(false);
      expect(isRetryableError(null)).toBe(false);
      expect(isRetryableError(undefined)).toBe(false);
      expect(isRetryableError(123)).toBe(false);
      expect(isRetryableError({})).toBe(false);
    });
  });

  describe("getErrorMessage", () => {
    it("should extract message from Error objects", () => {
      expect(getErrorMessage(new Error("test message"))).toBe("test message");
      expect(getErrorMessage(new ValidationError("validation failed"))).toBe(
        "validation failed"
      );
    });

    it("should return string errors directly", () => {
      expect(getErrorMessage("string error")).toBe("string error");
    });

    it("should return default message for unknown types", () => {
      expect(getErrorMessage(null)).toBe("Unknown error occurred");
      expect(getErrorMessage(undefined)).toBe("Unknown error occurred");
      expect(getErrorMessage(123)).toBe("Unknown error occurred");
      expect(getErrorMessage({})).toBe("Unknown error occurred");
    });
  });

  describe("getErrorCode", () => {
    it("should return code from AppError objects", () => {
      expect(getErrorCode(new ValidationError("test"))).toBe("VALIDATION_ERROR");
      expect(getErrorCode(new NotFoundError("Task", "1"))).toBe("NOT_FOUND");
      expect(getErrorCode(new BackendError("error", 500))).toBe("BACKEND_ERROR");
    });

    it("should return name from standard Error objects", () => {
      expect(getErrorCode(new Error("test"))).toBe("Error");
      expect(getErrorCode(new TypeError("test"))).toBe("TypeError");
      expect(getErrorCode(new RangeError("test"))).toBe("RangeError");
    });

    it("should return UNKNOWN_ERROR for non-error values", () => {
      expect(getErrorCode("string error")).toBe("UNKNOWN_ERROR");
      expect(getErrorCode(null)).toBe("UNKNOWN_ERROR");
      expect(getErrorCode(undefined)).toBe("UNKNOWN_ERROR");
      expect(getErrorCode(123)).toBe("UNKNOWN_ERROR");
    });
  });

  describe("Error inheritance", () => {
    it("all error types should be instances of AppError", () => {
      expect(new BackendUnavailableError()).toBeInstanceOf(AppError);
      expect(new BackendTimeoutError()).toBeInstanceOf(AppError);
      expect(new BackendError("test")).toBeInstanceOf(AppError);
      expect(new ValidationError("test")).toBeInstanceOf(AppError);
      expect(new NotFoundError("Task", "1")).toBeInstanceOf(AppError);
      expect(new ConflictError("test")).toBeInstanceOf(AppError);
      expect(new TimeoutError("op", 1000)).toBeInstanceOf(AppError);
      expect(new CircuitBreakerOpenError("svc")).toBeInstanceOf(AppError);
      expect(new InternalError("test")).toBeInstanceOf(AppError);
    });

    it("all error types should be instances of Error", () => {
      expect(new ValidationError("test")).toBeInstanceOf(Error);
      expect(new NotFoundError("Task", "1")).toBeInstanceOf(Error);
    });
  });
});
