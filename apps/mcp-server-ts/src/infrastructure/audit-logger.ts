/**
 * Audit Logger - Separate file-based audit trail
 *
 * Features:
 * - Dedicated audit log file (separate from application logs)
 * - JSONL format for easy parsing
 * - Correlation ID tracking
 * - Log rotation support (via pino)
 *
 * Usage:
 * ```typescript
 * import { auditLogger } from "./infrastructure/audit-logger.js";
 *
 * auditLogger.info({
 *   operation: "task_create",
 *   agent: "task_tools",
 *   result: "success",
 *   correlationId: "abc-123"
 * }, "Task created successfully");
 * ```
 */

import pino from "pino";
import path from "node:path";
import fs from "node:fs";

// Ensure logs directory exists
const logsDir = path.join(process.cwd(), "logs");
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir, { recursive: true });
}

/**
 * Dedicated audit logger with file transport
 */
export const auditLogger = pino.default({
  level: "info",

  // Audit logs are always JSON (never pretty printed)
  transport: {
    target: "pino/file",
    options: {
      destination: path.join(logsDir, "audit.log"),
      mkdir: true,
    },
  },

  // Base fields for audit logs
  base: {
    service: "taskman-mcp-v2",
    logType: "audit",
  },

  // ISO timestamp
  timestamp: pino.stdTimeFunctions.isoTime,

  // No redaction on audit logs (they should be pre-sanitized)
  redact: [],
});

/**
 * Create audit logger with correlation ID
 */
export function createAuditLogger(correlationId: string): pino.Logger {
  return auditLogger.child({ correlationId });
}
