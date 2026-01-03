/**
 * HTTP Transport - Express application with health check endpoints
 *
 * Provides:
 * - Kubernetes-compatible health probes
 * - System information endpoint
 * - JSON request/response handling
 * - Error handling middleware
 */

import express from "express";
import { config } from "../config/index.js";
import { parseTaskLogic } from "../features/ai/register.js";
import { healthCheckService } from "../infrastructure/health.js";
import { logger } from "../infrastructure/logger.js";
import { metricsService } from "../infrastructure/metrics.js";

export function createHttpApp(): express.Application {
  const app = express();

  // Middleware
  app.use(express.json());

  // CORS Middleware
  app.use((req, res, next) => {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    res.header("Access-Control-Allow-Headers", "Content-Type, Authorization");
    if (req.method === "OPTIONS") {
      return res.sendStatus(200);
    }
    next();
  });

  // Request logging middleware
  app.use((req, res, next) => {
    const start = Date.now();

    res.on("finish", () => {
      const duration = Date.now() - start;
      logger.info(
        {
          method: req.method,
          path: req.path,
          status: res.statusCode,
          duration_ms: duration,
        },
        "HTTP request"
      );
    });

    next();
  });

  // Health check endpoints (Kubernetes probes)
  app.get("/health/live", async (_req, res) => {
    try {
      const health = await healthCheckService.checkLiveness();
      const statusCode = health.status === "ok" ? 200 : 503;
      res.status(statusCode).json(health);
    } catch (error) {
      logger.error(
        { error: error instanceof Error ? error.message : String(error) },
        "Liveness check failed"
      );
      res.status(503).json({
        status: "down",
        timestamp: new Date().toISOString(),
        error: "Liveness check failed",
      });
    }
  });

  app.get("/health/ready", async (_req, res) => {
    try {
      const health = await healthCheckService.checkReadiness();
      const statusCode =
        health.status === "ok" ? 200 : health.status === "degraded" ? 200 : 503;
      res.status(statusCode).json(health);
    } catch (error) {
      logger.error(
        { error: error instanceof Error ? error.message : String(error) },
        "Readiness check failed"
      );
      res.status(503).json({
        status: "down",
        timestamp: new Date().toISOString(),
        error: "Readiness check failed",
      });
    }
  });

  app.get("/health/startup", async (_req, res) => {
    try {
      const health = await healthCheckService.checkStartup();
      const statusCode = health.status === "ok" ? 200 : 503;
      res.status(statusCode).json(health);
    } catch (error) {
      logger.error(
        { error: error instanceof Error ? error.message : String(error) },
        "Startup check failed"
      );
      res.status(503).json({
        status: "down",
        timestamp: new Date().toISOString(),
        error: "Startup check failed",
      });
    }
  });

  // Legacy health endpoint (for backward compatibility)
  app.get("/health", async (_req, res) => {
    try {
      const health = await healthCheckService.checkReadiness();
      const statusCode =
        health.status === "ok" ? 200 : health.status === "degraded" ? 200 : 503;
      res.status(statusCode).json({
        ok: statusCode === 200,
        service: "taskman-mcp",
        version: "2.0.0",
        ...health,
      });
    } catch (error) {
      res.status(503).json({
        ok: false,
        service: "taskman-mcp",
        version: "2.0.0",
        error: "Health check failed",
      });
    }
  });

  // System information endpoint (for debugging)
  app.get("/health/info", (_req, res) => {
    try {
      const info = healthCheckService.getSystemInfo();
      res.json(info);
    } catch (error) {
      logger.error(
        { error: error instanceof Error ? error.message : String(error) },
        "System info failed"
      );
      res.status(500).json({
        error: "Failed to retrieve system information",
      });
    }
  });

  // Prometheus metrics endpoint (Phase 2)
  app.get("/metrics", async (_req, res) => {
    if (!config.ENABLE_METRICS) {
      return res.status(404).json({
        error: "Metrics disabled",
        message: "Set ENABLE_METRICS=true to enable Prometheus metrics",
      });
    }

    try {
      const metrics = await metricsService.getMetrics();
      res.setHeader("Content-Type", "text/plain; version=0.0.4; charset=utf-8");
      res.send(metrics);
    } catch (error) {
      logger.error(
        { error: error instanceof Error ? error.message : String(error) },
        "Metrics endpoint failed"
      );
      res.status(500).json({
        error: "Failed to retrieve metrics",
      });
    }
  });

  // AI Parse Endpoint (Phase 2)
  app.post("/ai/parse", (req, res) => {
    try {
      const { input } = req.body;
      if (!input || typeof input !== "string") {
        return res.status(400).json({ error: "Input text is required" });
      }

      const parsed = parseTaskLogic(input);
      res.json(parsed);
    } catch (error) {
      logger.error(
        { error: error instanceof Error ? error.message : String(error) },
        "AI parse failed"
      );
      res.status(500).json({ error: "Failed to parse input" });
    }
  });

  // 404 handler
  app.use((_req, res) => {
    res.status(404).json({
      error: "Not found",
      message: "The requested endpoint does not exist",
    });
  });

  // Error handling middleware
  app.use(
    (
      err: Error,
      _req: express.Request,
      res: express.Response,
      _next: express.NextFunction
    ) => {
      logger.error(
        {
          error: err.message,
          stack: err.stack,
        },
        "Express error handler caught error"
      );

      res.status(500).json({
        error: "Internal server error",
        message:
          process.env.NODE_ENV === "production"
            ? "An error occurred"
            : err.message,
      });
    }
  );

  return app;
}
