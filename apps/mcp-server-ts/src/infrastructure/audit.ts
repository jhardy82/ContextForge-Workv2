/**
 * Audit Service - Structured JSONL-style logging
 *
 * Features:
 * - In-memory log buffer with size limits
 * - Correlation ID tracking for operation chains
 * - Backend integration for persistence
 * - JSONL format for structured logging
 * - File-based audit trail (separate from application logs)
 */

import { auditLogger, createAuditLogger } from "./audit-logger.js";

export interface AuditEntry {
  timestamp: string; // ISO 8601
  correlationId?: string;
  operation: string;
  agent: string; // Tool/service name
  result: "initiated" | "success" | "error" | "scheduled";
  details?: Record<string, unknown>;
}

class AuditService {
  private logs: AuditEntry[] = [];
  private readonly maxLogs = 1000; // Keep last 1000 entries in memory
  private currentCorrelationId: string | null = null;

  /**
   * Generate unique correlation ID
   */
  generateCorrelationId(): string {
    return `audit-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Set active correlation ID for operation chain
   */
  setCorrelationId(id: string): void {
    this.currentCorrelationId = id;
  }

  /**
   * Clear active correlation ID
   */
  clearCorrelationId(): void {
    this.currentCorrelationId = null;
  }

  /**
   * Log audit entry with automatic correlation
   */
  log(entry: Omit<AuditEntry, "timestamp" | "correlationId">): void {
    const fullEntry: AuditEntry = {
      ...entry,
      timestamp: new Date().toISOString(),
      correlationId: this.currentCorrelationId || undefined,
    };

    this.logs.push(fullEntry);

    // Trim logs if exceeds max size
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs);
    }

    // Write to file-based audit logger (production and development)
    const logger = this.currentCorrelationId
      ? createAuditLogger(this.currentCorrelationId)
      : auditLogger;

    logger.info({
      operation: entry.operation,
      agent: entry.agent,
      result: entry.result,
      details: entry.details,
    }, `${entry.operation} - ${entry.result}`);

    // Console output for development (in addition to file)
    // CRITICAL: Use stderr to avoid corrupting STDIO transport
    if (process.env.NODE_ENV !== "production") {
      console.error(`[AUDIT] ${JSON.stringify(fullEntry)}`);
    }
  }

  /**
   * Get recent logs (last N entries)
   */
  getRecentLogs(count: number = 100): AuditEntry[] {
    return this.logs.slice(-count);
  }

  /**
   * Get logs for specific correlation ID
   */
  getLogsByCorrelation(correlationId: string): AuditEntry[] {
    return this.logs.filter((log) => log.correlationId === correlationId);
  }

  /**
   * Export logs as JSONL (one JSON object per line)
   */
  exportJSONL(): string {
    return this.logs.map((log) => JSON.stringify(log)).join("\n");
  }

  /**
   * Clear all logs (use with caution)
   */
  clear(): void {
    this.logs = [];
  }
}

// Singleton instance
const auditService = new AuditService();

/**
 * Convenience function for logging
 */
export function auditLog(entry: Omit<AuditEntry, "timestamp" | "correlationId">): void {
  auditService.log(entry);
}

/**
 * Convenience function for correlation ID management
 */
export function withCorrelation<T>(fn: () => T | Promise<T>): Promise<T> {
  const correlationId = auditService.generateCorrelationId();
  auditService.setCorrelationId(correlationId);

  try {
    const result = fn();
    if (result instanceof Promise) {
      return result.finally(() => auditService.clearCorrelationId());
    }
    auditService.clearCorrelationId();
    return Promise.resolve(result);
  } catch (error) {
    auditService.clearCorrelationId();
    throw error;
  }
}

export { auditService };
