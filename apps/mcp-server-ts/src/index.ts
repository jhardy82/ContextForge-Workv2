/**
 * TaskMan MCP v2 Server - Main Entry Point
 *
 * CRITICAL: instrumentation.ts MUST be imported first for OpenTelemetry to work
 *
 * Features:
 * - OpenTelemetry distributed tracing (Phase 2)
 * - Prometheus metrics (Phase 2)
 * - System metrics collection (Phase 2)
 * - Graceful shutdown with signal handlers
 * - Structured logging with Pino
 * - Health check endpoints
 * - Configuration validation
 * - Production-ready error handling
 */

// CRITICAL: Import instrumentation FIRST before anything else
import "./instrumentation.js";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { isInitializeRequest } from "@modelcontextprotocol/sdk/types.js";
import { randomUUID } from "node:crypto";

import { config } from "./config/index.js";
import { registerActionListFeatures } from "./features/action-lists/register.js";
import { registerActivationFeatures } from "./features/activation/register.js";
import { registerAiFeatures } from "./features/ai/register.js";
import { registerProjectFeatures } from "./features/projects/register.js";
import { registerTaskFeatures } from "./features/tasks/register.js";
import {
  defaultCache,
  projectCache,
  taskCache,
} from "./infrastructure/cache.js";
import { healthCheckService } from "./infrastructure/health.js";
import { logger } from "./infrastructure/logger.js";
import { memoryMonitor } from "./infrastructure/memory-monitor.js";
import { metricsService } from "./infrastructure/metrics.js";
import { sessionManager } from "./infrastructure/session-manager.js";
import { shutdownService } from "./infrastructure/shutdown.js";
import { systemMetricsCollector } from "./infrastructure/system-metrics.js";
import { shutdownTracing } from "./instrumentation.js";
import { createHttpApp } from "./transports/http.js";

async function bootstrap(): Promise<void> {
  logger.info("Starting TaskMan MCP v2 server", {
    version: "0.1.0",
    nodeVersion: process.version,
    platform: process.platform,
    transport: config.TASKMAN_MCP_TRANSPORT,
    metricsEnabled: config.ENABLE_METRICS,
    tracingEnabled: config.ENABLE_TRACING,
  });

  const server = new McpServer({
    name: "taskman-mcp-v2",
    version: "0.1.0",
  });

  // Register all feature sets
  logger.debug("Registering MCP features");
  registerActivationFeatures(server); // Register first - provides server status tools
  registerProjectFeatures(server);
  registerTaskFeatures(server);
  registerActionListFeatures(server);
  registerAiFeatures(server);
  logger.info("MCP features registered successfully");

  // Initialize observability (Phase 2)
  if (config.ENABLE_METRICS) {
    logger.info("Initializing Prometheus metrics");
    metricsService.initialize();
    logger.info("Prometheus metrics initialized successfully");
  }

  if (config.ENABLE_METRICS) {
    logger.info("Starting system metrics collection");
    systemMetricsCollector.start(30000); // Collect every 30 seconds
    logger.info("System metrics collection started");
  }

  // Start monitoring and management services (Phase 1)
  logger.debug("Starting resource management services");
  memoryMonitor.start(60000); // Check every minute
  sessionManager.startCleanup(300000); // Cleanup every 5 minutes
  defaultCache.startCleanup(60000); // Cleanup every minute
  projectCache.startCleanup(60000);
  taskCache.startCleanup(60000);
  logger.info("Resource management services started");

  // Register cleanup on shutdown
  shutdownService.registerResource("monitoring-services", async () => {
    logger.info("Stopping monitoring services");
    memoryMonitor.stop();
    sessionManager.stopCleanup();
    systemMetricsCollector.stop();
    defaultCache.stopCleanup();
    projectCache.stopCleanup();
    taskCache.stopCleanup();
  });

  // Register OpenTelemetry shutdown (Phase 2)
  shutdownService.registerResource("opentelemetry", async () => {
    logger.info("Shutting down OpenTelemetry");
    await shutdownTracing();
    logger.info("OpenTelemetry shutdown complete");
  });

  const transport = config.TASKMAN_MCP_TRANSPORT;

  if (transport === "http") {
    const app = createHttpApp();
    const port = config.PORT;

    // Session management for HTTP transport
    const httpTransports: Map<string, StreamableHTTPServerTransport> = new Map();

    // MCP endpoint - POST for client-to-server communication
    app.post("/mcp", async (req, res) => {
      const sessionId = req.headers["mcp-session-id"] as string | undefined;
      let mcpTransport: StreamableHTTPServerTransport;

      try {
        if (sessionId && httpTransports.has(sessionId)) {
          // Reuse existing transport for session
          mcpTransport = httpTransports.get(sessionId)!;
          logger.debug({ sessionId }, "Reusing existing MCP session");
        } else if (!sessionId && isInitializeRequest(req.body)) {
          // New initialization request - create new session
          mcpTransport = new StreamableHTTPServerTransport({
            sessionIdGenerator: () => randomUUID(),
            enableJsonResponse: true,
            onsessioninitialized: (newSessionId) => {
              httpTransports.set(newSessionId, mcpTransport);
              logger.info({ sessionId: newSessionId }, "New MCP session initialized");
            },
          });

          // Clean up session on close
          mcpTransport.onclose = () => {
            const sid = Array.from(httpTransports.entries())
              .find(([_, t]) => t === mcpTransport)?.[0];
            if (sid) {
              httpTransports.delete(sid);
              logger.info({ sessionId: sid }, "MCP session closed");
            }
          };

          // Connect server to this transport
          await server.connect(mcpTransport);
        } else if (sessionId && !httpTransports.has(sessionId)) {
          // Invalid session ID
          logger.warn({ sessionId }, "MCP request with invalid session ID");
          res.status(400).json({
            error: "Invalid session",
            message: "Session not found. Send initialize request first.",
          });
          return;
        } else {
          // Missing session ID for non-init request
          logger.warn("MCP request missing session ID");
          res.status(400).json({
            error: "Missing session",
            message: "Session ID required for this request type.",
          });
          return;
        }

        // Handle the MCP request
        await mcpTransport.handleRequest(req, res, req.body);
      } catch (error) {
        logger.error(
          { error: error instanceof Error ? error.message : String(error) },
          "Error handling MCP request"
        );
        if (!res.headersSent) {
          res.status(500).json({
            error: "Internal server error",
            message: "Failed to process MCP request",
          });
        }
      }
    });

    // MCP endpoint - GET for server-to-client SSE streaming
    app.get("/mcp", async (req, res) => {
      const sessionId = req.headers["mcp-session-id"] as string | undefined;

      if (!sessionId || !httpTransports.has(sessionId)) {
        logger.warn({ sessionId }, "SSE request with invalid or missing session ID");
        res.status(400).json({
          error: "Invalid session",
          message: "Valid session ID required for SSE stream.",
        });
        return;
      }

      try {
        const mcpTransport = httpTransports.get(sessionId)!;
        logger.debug({ sessionId }, "Opening SSE stream for MCP session");
        await mcpTransport.handleRequest(req, res);
      } catch (error) {
        logger.error(
          { error: error instanceof Error ? error.message : String(error), sessionId },
          "Error handling SSE stream"
        );
        if (!res.headersSent) {
          res.status(500).json({
            error: "Internal server error",
            message: "Failed to open SSE stream",
          });
        }
      }
    });

    // MCP endpoint - DELETE for session termination
    app.delete("/mcp", async (req, res) => {
      const sessionId = req.headers["mcp-session-id"] as string | undefined;

      if (!sessionId || !httpTransports.has(sessionId)) {
        logger.warn({ sessionId }, "DELETE request with invalid or missing session ID");
        res.status(400).json({
          error: "Invalid session",
          message: "Valid session ID required to terminate session.",
        });
        return;
      }

      try {
        const mcpTransport = httpTransports.get(sessionId)!;
        await mcpTransport.close();
        httpTransports.delete(sessionId);
        logger.info({ sessionId }, "MCP session terminated by client");
        res.status(204).send();
      } catch (error) {
        logger.error(
          { error: error instanceof Error ? error.message : String(error), sessionId },
          "Error terminating session"
        );
        res.status(500).json({
          error: "Internal server error",
          message: "Failed to terminate session",
        });
      }
    });

    // Register HTTP transport cleanup on shutdown
    shutdownService.registerResource("mcp-http-sessions", async () => {
      logger.info({ sessionCount: httpTransports.size }, "Closing MCP HTTP sessions");
      const closePromises = Array.from(httpTransports.values()).map((t) => t.close());
      await Promise.allSettled(closePromises);
      httpTransports.clear();
      logger.info("MCP HTTP sessions closed");
    });

    // Start HTTP server
    const httpServer = app.listen(port, () => {
      logger.info("TaskMan MCP v2 HTTP server started", { port });
      healthCheckService.markStartupComplete();
    });

    // Register HTTP server for graceful shutdown
    shutdownService.registerResource("http-server", async () => {
      logger.info("Closing HTTP server");
      return new Promise<void>((resolve, reject) => {
        httpServer.close((err) => {
          if (err) {
            logger.error({ error: err.message }, "Error closing HTTP server");
            reject(err);
          } else {
            logger.info("HTTP server closed successfully");
            resolve();
          }
        });
      });
    });
  } else if (transport === "stdio") {
    // Stdio transport for MCP client integration
    const stdioTransport = new StdioServerTransport();
    await server.connect(stdioTransport);

    logger.info("TaskMan MCP v2 server connected via stdio transport");
    healthCheckService.markStartupComplete();

    // Register MCP server for graceful shutdown
    shutdownService.registerResource("mcp-server", async () => {
      logger.info("Closing MCP server connection");
      await server.close();
      logger.info("MCP server closed successfully");
    });
  } else {
    logger.warn(
      "Unknown transport specified, server initialized without transport",
      {
        transport,
      }
    );
    healthCheckService.markStartupComplete();
  }
}

// Setup signal handlers for graceful shutdown
process.on("SIGINT", async () => {
  logger.info("SIGINT received, initiating graceful shutdown");
  try {
    await shutdownService.shutdown();
    logger.info("Graceful shutdown completed");
    process.exit(0);
  } catch (error) {
    logger.error({ error: error instanceof Error ? error.message : String(error) }, "Error during shutdown");
    process.exit(1);
  }
});

process.on("SIGTERM", async () => {
  logger.info("SIGTERM received, initiating graceful shutdown");
  try {
    await shutdownService.shutdown();
    logger.info("Graceful shutdown completed");
    process.exit(0);
  } catch (error) {
    logger.error({ error: error instanceof Error ? error.message : String(error) }, "Error during shutdown");
    process.exit(1);
  }
});

// Handle uncaught exceptions
process.on("uncaughtException", (error) => {
  logger.fatal({ error: error.message, stack: error.stack }, "Uncaught exception");
  shutdownService.shutdown().finally(() => process.exit(1));
});

// Handle unhandled promise rejections
process.on("unhandledRejection", (reason, promise) => {
  logger.fatal({ reason, promise }, "Unhandled promise rejection");
  shutdownService.shutdown().finally(() => process.exit(1));
});

// Start the server
bootstrap().catch((error) => {
  logger.fatal({
    error: error instanceof Error ? error.message : String(error),
    stack: error instanceof Error ? error.stack : undefined,
  }, "Failed to start TaskMan MCP v2 server");
  process.exit(1);
});
