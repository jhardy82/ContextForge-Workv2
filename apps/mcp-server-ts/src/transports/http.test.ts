import { describe, it, expect, beforeEach, vi } from "vitest";
import { createHttpApp } from "./http.js";
import type { Express } from "express";
import request from "supertest";

// Mock the health check service to ensure predictable test results
vi.mock("../infrastructure/health.js", () => ({
  healthCheckService: {
    checkReadiness: vi.fn().mockResolvedValue({
      status: "ok",
      timestamp: new Date().toISOString(),
      uptime: 100,
      checks: {},
    }),
    checkLiveness: vi.fn().mockResolvedValue({
      status: "ok",
      timestamp: new Date().toISOString(),
      uptime: 100,
      checks: {},
    }),
    checkStartup: vi.fn().mockResolvedValue({
      status: "ok",
      timestamp: new Date().toISOString(),
      uptime: 100,
      checks: {},
    }),
    getSystemInfo: vi.fn().mockReturnValue({
      nodeVersion: process.version,
      platform: process.platform,
    }),
  },
}));

describe("HTTP transport", () => {
  let app: Express;

  beforeEach(() => {
    app = createHttpApp();
  });

  it("should create an express app", () => {
    expect(app).toBeDefined();
    expect(app).toHaveProperty("get");
    expect(app).toHaveProperty("post");
    expect(app).toHaveProperty("listen");
  });

  it("should be an Express application", () => {
    expect(typeof app.get).toBe("function");
    expect(typeof app.post).toBe("function");
    expect(typeof app.listen).toBe("function");
  });

  it("should create a new app instance each time", () => {
    const app1 = createHttpApp();
    const app2 = createHttpApp();
    expect(app1).not.toBe(app2);
  });

  it("should have standard Express methods", () => {
    const methods = ["get", "post", "put", "delete", "patch"];
    methods.forEach((method) => {
      expect(app).toHaveProperty(method);
      expect(typeof (app as any)[method]).toBe("function");
    });
  });

  it("should respond to health check endpoint", async () => {
    const response = await request(app).get("/health");
    expect(response.status).toBe(200);
    expect(response.body.ok).toBe(true);
    expect(response.body.service).toBe("taskman-mcp");
    expect(response.body.version).toBe("2.0.0");
  });

  it("should return JSON content type for health endpoint", async () => {
    const response = await request(app).get("/health");
    expect(response.headers["content-type"]).toMatch(/json/);
  });

  describe("Correlation ID middleware", () => {
    it("should add X-Request-ID header to responses", async () => {
      const response = await request(app).get("/health");
      expect(response.headers["x-request-id"]).toBeDefined();
      expect(response.headers["x-request-id"]).toMatch(/^req-/);
    });

    it("should add X-Correlation-ID header to responses", async () => {
      const response = await request(app).get("/health");
      expect(response.headers["x-correlation-id"]).toBeDefined();
    });

    it("should propagate incoming X-Correlation-ID header", async () => {
      const correlationId = "trace-from-upstream-123";
      const response = await request(app)
        .get("/health")
        .set("X-Correlation-ID", correlationId);
      expect(response.headers["x-correlation-id"]).toBe(correlationId);
    });

    it("should propagate incoming X-Request-ID as correlation", async () => {
      const requestId = "req-from-upstream-456";
      const response = await request(app)
        .get("/health")
        .set("X-Request-ID", requestId);
      // Should use the incoming request ID as correlation ID
      expect(response.headers["x-correlation-id"]).toBe(requestId);
    });

    it("should generate new correlation ID when none provided", async () => {
      const response = await request(app).get("/health");
      expect(response.headers["x-correlation-id"]).toMatch(/^corr-/);
    });
  });

  describe("Health check endpoints", () => {
    it("should respond to /health/live endpoint", async () => {
      const response = await request(app).get("/health/live");
      expect(response.status).toBe(200);
      expect(response.body.status).toBe("ok");
    });

    it("should respond to /health/ready endpoint", async () => {
      const response = await request(app).get("/health/ready");
      expect(response.status).toBe(200);
      expect(response.body.status).toBe("ok");
    });

    it("should respond to /health/startup endpoint", async () => {
      const response = await request(app).get("/health/startup");
      expect(response.status).toBe(200);
      expect(response.body.status).toBe("ok");
    });

    it("should respond to /health/info endpoint", async () => {
      const response = await request(app).get("/health/info");
      expect(response.status).toBe(200);
      expect(response.body.nodeVersion).toBeDefined();
      expect(response.body.platform).toBeDefined();
    });
  });

  describe("Error handling", () => {
    it("should return 404 for unknown endpoints", async () => {
      const response = await request(app).get("/unknown-endpoint");
      expect(response.status).toBe(404);
      expect(response.body.error).toBe("Not found");
      expect(response.body.message).toBe("The requested endpoint does not exist");
    });

    it("should return JSON for 404 errors", async () => {
      const response = await request(app).get("/does-not-exist");
      expect(response.headers["content-type"]).toMatch(/json/);
    });
  });
});
