import { describe, it, expect, beforeEach, vi, afterEach } from "vitest";
import { auditService, auditLog, withCorrelation, type AuditEntry } from "./audit.js";

describe("Audit Service", () => {
  beforeEach(() => {
    // Clear audit logs before each test
    auditService.clear();
    // Clear any correlation ID
    auditService.clearCorrelationId();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("generateCorrelationId", () => {
    it("should generate unique correlation IDs", () => {
      const id1 = auditService.generateCorrelationId();
      const id2 = auditService.generateCorrelationId();

      expect(id1).toMatch(/^audit-\d+-[a-z0-9]+$/);
      expect(id2).toMatch(/^audit-\d+-[a-z0-9]+$/);
      expect(id1).not.toBe(id2);
    });

    it("should include timestamp in correlation ID", () => {
      const before = Date.now();
      const id = auditService.generateCorrelationId();
      const after = Date.now();

      const timestamp = parseInt(id.split("-")[1]);
      expect(timestamp).toBeGreaterThanOrEqual(before);
      expect(timestamp).toBeLessThanOrEqual(after);
    });
  });

  describe("setCorrelationId and clearCorrelationId", () => {
    it("should set and clear correlation ID", () => {
      auditService.setCorrelationId("test-correlation-123");

      // Log entry should include correlation ID
      auditService.log({
        operation: "test_operation",
        agent: "test_agent",
        result: "success",
      });

      const logs = auditService.getRecentLogs(1);
      expect(logs[0].correlationId).toBe("test-correlation-123");

      auditService.clearCorrelationId();

      // New log should not have correlation ID
      auditService.log({
        operation: "test_operation_2",
        agent: "test_agent",
        result: "success",
      });

      const logs2 = auditService.getRecentLogs(1);
      expect(logs2[0].correlationId).toBeUndefined();
    });
  });

  describe("log", () => {
    it("should log audit entry with timestamp", () => {
      auditService.log({
        operation: "task_create",
        agent: "task_tools",
        result: "success",
        details: { taskId: "T-123" },
      });

      const logs = auditService.getRecentLogs(1);

      expect(logs).toHaveLength(1);
      expect(logs[0].operation).toBe("task_create");
      expect(logs[0].agent).toBe("task_tools");
      expect(logs[0].result).toBe("success");
      expect(logs[0].details).toEqual({ taskId: "T-123" });
      expect(logs[0].timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);

      // Verify timestamp is recent (within last 5 seconds)
      const timestamp = new Date(logs[0].timestamp).getTime();
      const now = Date.now();
      expect(now - timestamp).toBeLessThan(5000);
    });

    it("should include correlation ID when set", () => {
      auditService.setCorrelationId("correlation-456");

      auditService.log({
        operation: "task_update",
        agent: "task_tools",
        result: "success",
      });

      const logs = auditService.getRecentLogs(1);
      expect(logs[0].correlationId).toBe("correlation-456");
    });

    it("should support all result types", () => {
      const results: Array<"initiated" | "success" | "error" | "scheduled"> = [
        "initiated",
        "success",
        "error",
        "scheduled",
      ];

      results.forEach((result) => {
        auditService.log({
          operation: "test_operation",
          agent: "test_agent",
          result,
        });
      });

      const logs = auditService.getRecentLogs(4);
      expect(logs.map((log) => log.result)).toEqual(results);
    });

    it("should trim logs when exceeding max size", () => {
      // Add 1500 logs (max is 1000)
      for (let i = 0; i < 1500; i++) {
        auditService.log({
          operation: `operation_${i}`,
          agent: "test_agent",
          result: "success",
        });
      }

      const logs = auditService.getRecentLogs(2000);
      expect(logs).toHaveLength(1000);

      // Should keep the latest 1000
      expect(logs[0].operation).toBe("operation_500");
      expect(logs[999].operation).toBe("operation_1499");
    });

    it("should handle empty details object", () => {
      auditService.log({
        operation: "test_operation",
        agent: "test_agent",
        result: "success",
        details: {},
      });

      const logs = auditService.getRecentLogs(1);
      expect(logs[0].details).toEqual({});
    });

    it("should handle complex details object", () => {
      const complexDetails = {
        taskId: "T-123",
        changes: {
          status: "completed",
          priority: "high",
        },
        metadata: {
          updatedBy: "user@example.com",
          reason: "Task finished",
        },
      };

      auditService.log({
        operation: "task_update",
        agent: "task_tools",
        result: "success",
        details: complexDetails,
      });

      const logs = auditService.getRecentLogs(1);
      expect(logs[0].details).toEqual(complexDetails);
    });
  });

  describe("getRecentLogs", () => {
    it("should return recent logs with default count", () => {
      for (let i = 0; i < 150; i++) {
        auditService.log({
          operation: `operation_${i}`,
          agent: "test_agent",
          result: "success",
        });
      }

      const logs = auditService.getRecentLogs();
      expect(logs).toHaveLength(100); // Default is 100
      expect(logs[0].operation).toBe("operation_50");
      expect(logs[99].operation).toBe("operation_149");
    });

    it("should return specified number of logs", () => {
      for (let i = 0; i < 50; i++) {
        auditService.log({
          operation: `operation_${i}`,
          agent: "test_agent",
          result: "success",
        });
      }

      const logs = auditService.getRecentLogs(25);
      expect(logs).toHaveLength(25);
      expect(logs[0].operation).toBe("operation_25");
      expect(logs[24].operation).toBe("operation_49");
    });

    it("should return all logs if count exceeds total", () => {
      for (let i = 0; i < 10; i++) {
        auditService.log({
          operation: `operation_${i}`,
          agent: "test_agent",
          result: "success",
        });
      }

      const logs = auditService.getRecentLogs(100);
      expect(logs).toHaveLength(10);
    });

    it("should return empty array when no logs exist", () => {
      const logs = auditService.getRecentLogs(10);
      expect(logs).toEqual([]);
    });
  });

  describe("getLogsByCorrelation", () => {
    it("should return logs with matching correlation ID", () => {
      auditService.setCorrelationId("correlation-A");
      auditService.log({
        operation: "operation_1",
        agent: "test_agent",
        result: "success",
      });
      auditService.log({
        operation: "operation_2",
        agent: "test_agent",
        result: "success",
      });

      auditService.setCorrelationId("correlation-B");
      auditService.log({
        operation: "operation_3",
        agent: "test_agent",
        result: "success",
      });

      const logsA = auditService.getLogsByCorrelation("correlation-A");
      const logsB = auditService.getLogsByCorrelation("correlation-B");

      expect(logsA).toHaveLength(2);
      expect(logsA[0].operation).toBe("operation_1");
      expect(logsA[1].operation).toBe("operation_2");

      expect(logsB).toHaveLength(1);
      expect(logsB[0].operation).toBe("operation_3");
    });

    it("should return empty array for non-existent correlation ID", () => {
      auditService.setCorrelationId("correlation-A");
      auditService.log({
        operation: "operation_1",
        agent: "test_agent",
        result: "success",
      });

      const logs = auditService.getLogsByCorrelation("non-existent");
      expect(logs).toEqual([]);
    });

    it("should not return logs without correlation ID", () => {
      auditService.log({
        operation: "operation_without_correlation",
        agent: "test_agent",
        result: "success",
      });

      auditService.setCorrelationId("correlation-A");
      auditService.log({
        operation: "operation_with_correlation",
        agent: "test_agent",
        result: "success",
      });

      const logs = auditService.getLogsByCorrelation("correlation-A");
      expect(logs).toHaveLength(1);
      expect(logs[0].operation).toBe("operation_with_correlation");
    });
  });

  describe("exportJSONL", () => {
    it("should export logs in JSONL format", () => {
      auditService.log({
        operation: "operation_1",
        agent: "agent_1",
        result: "success",
      });

      auditService.log({
        operation: "operation_2",
        agent: "agent_2",
        result: "error",
        details: { errorCode: "ERR_123" },
      });

      const jsonl = auditService.exportJSONL();
      const lines = jsonl.split("\n");

      expect(lines).toHaveLength(2);

      const log1 = JSON.parse(lines[0]);
      const log2 = JSON.parse(lines[1]);

      expect(log1.operation).toBe("operation_1");
      expect(log1.agent).toBe("agent_1");
      expect(log1.result).toBe("success");

      expect(log2.operation).toBe("operation_2");
      expect(log2.agent).toBe("agent_2");
      expect(log2.result).toBe("error");
      expect(log2.details).toEqual({ errorCode: "ERR_123" });
    });

    it("should return empty string when no logs exist", () => {
      const jsonl = auditService.exportJSONL();
      expect(jsonl).toBe("");
    });

    it("should handle logs with correlation IDs", () => {
      auditService.setCorrelationId("correlation-123");
      auditService.log({
        operation: "operation_1",
        agent: "test_agent",
        result: "success",
      });

      const jsonl = auditService.exportJSONL();
      const log = JSON.parse(jsonl);

      expect(log.correlationId).toBe("correlation-123");
    });
  });

  describe("clear", () => {
    it("should clear all logs", () => {
      for (let i = 0; i < 50; i++) {
        auditService.log({
          operation: `operation_${i}`,
          agent: "test_agent",
          result: "success",
        });
      }

      expect(auditService.getRecentLogs(100)).toHaveLength(50);

      auditService.clear();

      expect(auditService.getRecentLogs(100)).toEqual([]);
    });

    it("should not affect current correlation ID", () => {
      auditService.setCorrelationId("correlation-123");

      auditService.log({
        operation: "operation_1",
        agent: "test_agent",
        result: "success",
      });

      auditService.clear();

      // Correlation ID should still be set
      auditService.log({
        operation: "operation_2",
        agent: "test_agent",
        result: "success",
      });

      const logs = auditService.getRecentLogs(1);
      expect(logs[0].correlationId).toBe("correlation-123");
    });
  });
});

describe("auditLog function", () => {
  beforeEach(() => {
    auditService.clear();
    auditService.clearCorrelationId();
  });

  it("should log via convenience function", () => {
    auditLog({
      operation: "test_operation",
      agent: "test_agent",
      result: "success",
      details: { test: "data" },
    });

    const logs = auditService.getRecentLogs(1);
    expect(logs).toHaveLength(1);
    expect(logs[0].operation).toBe("test_operation");
    expect(logs[0].agent).toBe("test_agent");
    expect(logs[0].details).toEqual({ test: "data" });
  });
});

describe("withCorrelation function", () => {
  beforeEach(() => {
    auditService.clear();
    auditService.clearCorrelationId();
  });

  it("should execute function with auto-generated correlation ID", async () => {
    await withCorrelation(() => {
      auditLog({
        operation: "test_operation",
        agent: "test_agent",
        result: "success",
      });
    });

    const logs = auditService.getRecentLogs(1);
    expect(logs[0].correlationId).toMatch(/^audit-\d+-[a-z0-9]+$/);
  });

  it("should clear correlation ID after function completes", async () => {
    await withCorrelation(() => {
      auditLog({
        operation: "test_operation_1",
        agent: "test_agent",
        result: "success",
      });
    });

    // Log outside withCorrelation should not have correlation ID
    auditLog({
      operation: "test_operation_2",
      agent: "test_agent",
      result: "success",
    });

    const logs = auditService.getRecentLogs(2);
    expect(logs[0].correlationId).toBeDefined();
    expect(logs[1].correlationId).toBeUndefined();
  });

  it("should handle async functions", async () => {
    await withCorrelation(async () => {
      await new Promise((resolve) => setTimeout(resolve, 10));
      auditLog({
        operation: "async_operation",
        agent: "test_agent",
        result: "success",
      });
    });

    const logs = auditService.getRecentLogs(1);
    expect(logs[0].operation).toBe("async_operation");
    expect(logs[0].correlationId).toBeDefined();
  });

  it("should clear correlation ID after async function completes", async () => {
    await withCorrelation(async () => {
      await new Promise((resolve) => setTimeout(resolve, 10));
      auditLog({
        operation: "async_operation_1",
        agent: "test_agent",
        result: "success",
      });
    });

    auditLog({
      operation: "async_operation_2",
      agent: "test_agent",
      result: "success",
    });

    const logs = auditService.getRecentLogs(2);
    expect(logs[0].correlationId).toBeDefined();
    expect(logs[1].correlationId).toBeUndefined();
  });

  it("should return function result", async () => {
    const result = await withCorrelation(() => {
      return 42;
    });

    expect(result).toBe(42);
  });

  it("should return async function result", async () => {
    const result = await withCorrelation(async () => {
      await new Promise((resolve) => setTimeout(resolve, 10));
      return "async result";
    });

    expect(result).toBe("async result");
  });

  it("should clear correlation ID even when function throws", async () => {
    try {
      await withCorrelation(() => {
        auditLog({
          operation: "test_operation",
          agent: "test_agent",
          result: "error",
        });
        throw new Error("Test error");
      });
      // Should not reach here
      expect.fail("Should have thrown error");
    } catch (error: any) {
      expect(error.message).toBe("Test error");
    }

    // Correlation ID should be cleared
    auditLog({
      operation: "after_error",
      agent: "test_agent",
      result: "success",
    });

    const logs = auditService.getRecentLogs(2);
    expect(logs[0].correlationId).toBeDefined();
    expect(logs[1].correlationId).toBeUndefined();
  });

  it("should handle nested withCorrelation calls", async () => {
    await withCorrelation(async () => {
      auditLog({
        operation: "outer_operation",
        agent: "test_agent",
        result: "initiated",
      });

      await withCorrelation(async () => {
        auditLog({
          operation: "inner_operation",
          agent: "test_agent",
          result: "success",
        });
      });

      // After inner withCorrelation completes, correlation ID is cleared
      auditLog({
        operation: "outer_operation",
        agent: "test_agent",
        result: "success",
      });
    });

    const logs = auditService.getRecentLogs(3);
    // First two logs should have correlation IDs
    expect(logs[0].correlationId).toBeDefined();
    expect(logs[1].correlationId).toBeDefined();
    // Third log has no correlation ID (inner withCorrelation cleared it)
    expect(logs[2].correlationId).toBeUndefined();

    // First and second logs should have different correlations
    expect(logs[0].correlationId).not.toBe(logs[1].correlationId);
  });
});
