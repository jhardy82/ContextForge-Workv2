/**
 * Configuration Tests - Comprehensive validation of Zod schema
 *
 * Tests cover:
 * - Default values
 * - Type coercion (string → number, string → boolean)
 * - Value transformations (LOG_LEVEL lowercase)
 * - Validation constraints (ranges, patterns, enums)
 * - Error messages for invalid inputs
 * - Critical bug fix validation (port 3000 vs 3001)
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { validateConfig } from "./schema.js";

describe("Configuration Module", () => {
  let originalEnv: NodeJS.ProcessEnv;

  beforeEach(() => {
    // Save original environment
    originalEnv = { ...process.env };

    // Clear all test-related env vars to prevent pollution
    delete process.env.ENABLE_METRICS;
    delete process.env.ENABLE_TRACING;
    delete process.env.ENABLE_PERSISTENCE;
    delete process.env.CIRCUIT_BREAKER_ENABLED;
    delete process.env.FALLBACK_CACHE_ENABLED;
    delete process.env.HEALTH_CHECK_ENABLED;
  });

  afterEach(() => {
    // Restore original environment
    process.env = originalEnv;
    // Clear module cache to get fresh config
    vi.resetModules();
  });

  describe("Basic Defaults", () => {
    it("should use default port 3000 when PORT not set", async () => {
      delete process.env.PORT;
      vi.resetModules();
      const { config } = await import("./index.js");
      expect(config.PORT).toBe(3000);
    });

    it("should use development as default environment", async () => {
      delete process.env.NODE_ENV;
      vi.resetModules();
      const { config } = await import("./index.js");
      expect(config.NODE_ENV).toBe("development");
    });

    it("should use stdio as default transport", async () => {
      delete process.env.TASKMAN_MCP_TRANSPORT;
      vi.resetModules();
      const { config } = await import("./index.js");
      expect(config.TASKMAN_MCP_TRANSPORT).toBe("stdio");
    });

    it("should use info as default log level", async () => {
      delete process.env.LOG_LEVEL;
      vi.resetModules();
      const { config } = await import("./index.js");
      expect(config.LOG_LEVEL).toBe("info");
    });
  });

  describe("Environment Variable Overrides", () => {
    it("should use PORT environment variable when set", async () => {
      process.env.PORT = "8080";
      vi.resetModules();
      const { config } = await import("./index.js");
      expect(config.PORT).toBe(8080);
    });

    it("should use NODE_ENV when set to production", async () => {
      process.env.NODE_ENV = "production";
      vi.resetModules();
      const { config } = await import("./index.js");
      expect(config.NODE_ENV).toBe("production");
    });

    it("should use NODE_ENV when set to test", async () => {
      process.env.NODE_ENV = "test";
      vi.resetModules();
      const { config } = await import("./index.js");
      expect(config.NODE_ENV).toBe("test");
    });

    it("should use custom backend API endpoint", async () => {
      process.env.TASK_MANAGER_API_ENDPOINT = "https://api.example.com/v1";
      vi.resetModules();
      const { config } = await import("./index.js");
      expect(config.TASK_MANAGER_API_ENDPOINT).toBe("https://api.example.com/v1");
    });
  });

  describe("Type Coercion (Zod Feature)", () => {
    it("should coerce PORT string to number", async () => {
      process.env.PORT = "5000";
      vi.resetModules();
      const { config } = await import("./index.js");
      expect(typeof config.PORT).toBe("number");
      expect(config.PORT).toBe(5000);
    });

    it("should coerce boolean strings to booleans", async () => {
      // Clear potentially conflicting env vars first
      delete process.env.ENABLE_METRICS;
      delete process.env.ENABLE_TRACING;

      // Set test values
      process.env.ENABLE_METRICS = "true";
      process.env.ENABLE_TRACING = "false";

      vi.resetModules();
      const { config } = await import("./index.js");

      expect(config.ENABLE_METRICS).toBe(true);
      expect(config.ENABLE_TRACING).toBe(false);
    });

    it("should coerce numeric strings to numbers", async () => {
      process.env.BACKEND_TIMEOUT_MS = "60000";
      process.env.BACKEND_MAX_RETRIES = "5";
      vi.resetModules();
      const { config } = await import("./index.js");
      expect(typeof config.BACKEND_TIMEOUT_MS).toBe("number");
      expect(config.BACKEND_TIMEOUT_MS).toBe(60000);
      expect(typeof config.BACKEND_MAX_RETRIES).toBe("number");
      expect(config.BACKEND_MAX_RETRIES).toBe(5);
    });
  });

  describe("Value Transformations (Zod Feature)", () => {
    it("should transform LOG_LEVEL to lowercase", () => {
      const config = validateConfig({
        ...process.env,
        LOG_LEVEL: "INFO",
      });
      expect(config.LOG_LEVEL).toBe("info");
    });

    it("should transform mixed-case log levels", () => {
      const config = validateConfig({
        ...process.env,
        LOG_LEVEL: "WaRn",
      });
      expect(config.LOG_LEVEL).toBe("warn");
    });
  });

  describe("Validation Constraints", () => {
    it("should reject invalid NODE_ENV values", () => {
      expect(() =>
        validateConfig({
          ...process.env,
          NODE_ENV: "invalid",
        })
      ).toThrow();
    });

    it("should reject PORT below minimum (1)", () => {
      expect(() =>
        validateConfig({
          ...process.env,
          PORT: "0",
        })
      ).toThrow();
    });

    it("should reject PORT above maximum (65535)", () => {
      expect(() =>
        validateConfig({
          ...process.env,
          PORT: "65536",
        })
      ).toThrow();
    });

    it("should reject invalid TASKMAN_MCP_TRANSPORT", () => {
      expect(() =>
        validateConfig({
          ...process.env,
          TASKMAN_MCP_TRANSPORT: "websocket",
        })
      ).toThrow();
    });

    it("should reject invalid LOG_LEVEL", () => {
      expect(() =>
        validateConfig({
          ...process.env,
          LOG_LEVEL: "verbose",
        })
      ).toThrow();
    });

    it("should reject non-URL for TASK_MANAGER_API_ENDPOINT", () => {
      expect(() =>
        validateConfig({
          ...process.env,
          TASK_MANAGER_API_ENDPOINT: "not-a-url",
        })
      ).toThrow();
    });

    it("should reject BACKEND_MAX_RETRIES above 10", () => {
      expect(() =>
        validateConfig({
          ...process.env,
          BACKEND_MAX_RETRIES: "11",
        })
      ).toThrow();
    });

    it("should reject CIRCUIT_BREAKER_ERROR_THRESHOLD above 100", () => {
      expect(() =>
        validateConfig({
          ...process.env,
          CIRCUIT_BREAKER_ERROR_THRESHOLD: "101",
        })
      ).toThrow();
    });

    it("should reject CIRCUIT_BREAKER_ERROR_THRESHOLD below 1", () => {
      expect(() =>
        validateConfig({
          ...process.env,
          CIRCUIT_BREAKER_ERROR_THRESHOLD: "0",
        })
      ).toThrow();
    });

    it("should reject OTEL_SAMPLE_RATE above 1.0", () => {
      expect(() =>
        validateConfig({
          ...process.env,
          OTEL_SAMPLE_RATE: "1.5",
        })
      ).toThrow();
    });

    it("should reject OTEL_SAMPLE_RATE below 0.0", () => {
      expect(() =>
        validateConfig({
          ...process.env,
          OTEL_SAMPLE_RATE: "-0.1",
        })
      ).toThrow();
    });
  });

  describe("Backend API Endpoint Port Configuration", () => {
    it("should default TASK_MANAGER_API_ENDPOINT to port 3001", async () => {
      delete process.env.TASK_MANAGER_API_ENDPOINT;
      vi.resetModules();
      const { config } = await import("./index.js");
      expect(config.TASK_MANAGER_API_ENDPOINT).toBe("http://localhost:3001/api/v1");
    });

    it("should validate default endpoint uses correct port", () => {
      const config = validateConfig({});
      const url = new URL(config.TASK_MANAGER_API_ENDPOINT);
      expect(url.port).toBe("3001");
    });
  });

  describe("Configuration Shape", () => {
    it("should have all required properties", async () => {
      vi.resetModules();
      const { config } = await import("./index.js");

      // Environment
      expect(config).toHaveProperty("NODE_ENV");

      // Server
      expect(config).toHaveProperty("PORT");
      expect(config).toHaveProperty("TASKMAN_MCP_TRANSPORT");

      // Backend API
      expect(config).toHaveProperty("TASK_MANAGER_API_ENDPOINT");
      expect(config).toHaveProperty("BACKEND_TIMEOUT_MS");
      expect(config).toHaveProperty("BACKEND_MAX_RETRIES");

      // Logging
      expect(config).toHaveProperty("LOG_LEVEL");
      expect(config).toHaveProperty("LOG_FORMAT");

      // Persistence
      expect(config).toHaveProperty("ENABLE_PERSISTENCE");
      expect(config).toHaveProperty("PERSISTENCE_TYPE");

      // Observability
      expect(config).toHaveProperty("ENABLE_METRICS");
      expect(config).toHaveProperty("ENABLE_TRACING");

      // Resilience
      expect(config).toHaveProperty("CIRCUIT_BREAKER_ENABLED");
      expect(config).toHaveProperty("FALLBACK_CACHE_ENABLED");
    });

    it("should have correct types", async () => {
      vi.resetModules();
      const { config } = await import("./index.js");

      expect(typeof config.NODE_ENV).toBe("string");
      expect(typeof config.PORT).toBe("number");
      expect(typeof config.TASKMAN_MCP_TRANSPORT).toBe("string");
      expect(typeof config.TASK_MANAGER_API_ENDPOINT).toBe("string");
      expect(typeof config.BACKEND_TIMEOUT_MS).toBe("number");
      expect(typeof config.LOG_LEVEL).toBe("string");
      expect(typeof config.ENABLE_METRICS).toBe("boolean");
      expect(typeof config.CIRCUIT_BREAKER_ENABLED).toBe("boolean");
    });
  });

  describe("Comprehensive Defaults", () => {
    it("should provide all default values", () => {
      const config = validateConfig({});

      // Environment defaults
      expect(config.NODE_ENV).toBe("development");
      expect(config.PORT).toBe(3000);
      expect(config.TASKMAN_MCP_TRANSPORT).toBe("stdio");

      // Backend API defaults
      expect(config.TASK_MANAGER_API_ENDPOINT).toBe("http://localhost:3001/api/v1");
      expect(config.BACKEND_TIMEOUT_MS).toBe(30000);
      expect(config.BACKEND_MAX_RETRIES).toBe(3);
      expect(config.BACKEND_RETRY_DELAY_MS).toBe(1000);

      // Logging defaults
      expect(config.LOG_LEVEL).toBe("info");
      expect(config.LOG_FORMAT).toBe("json");

      // Persistence defaults
      expect(config.ENABLE_PERSISTENCE).toBe(false);
      expect(config.PERSISTENCE_TYPE).toBe("memory");

      // Observability defaults
      expect(config.ENABLE_METRICS).toBe(false);
      expect(config.ENABLE_TRACING).toBe(false);
      expect(config.OTEL_SAMPLE_RATE).toBe(1.0);

      // Resilience defaults
      expect(config.CIRCUIT_BREAKER_ENABLED).toBe(true);
      expect(config.CIRCUIT_BREAKER_ERROR_THRESHOLD).toBe(50);
      expect(config.FALLBACK_CACHE_ENABLED).toBe(true);

      // Health check defaults
      expect(config.HEALTH_CHECK_ENABLED).toBe(true);
    });
  });
});
