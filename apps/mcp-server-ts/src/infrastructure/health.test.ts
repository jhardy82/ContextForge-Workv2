import { describe, it, expect, beforeEach, vi, afterEach } from "vitest";
import { healthService, type HealthStatus } from "./health.js";
import { backendClient } from "../backend/client.js";
import { auditService } from "./audit.js";
import { lockingService } from "./locking.js";

// Mock the backend client
vi.mock("../backend/client.js", () => ({
  backendClient: {
    health: vi.fn(),
  },
}));

describe("Health Service", () => {
  beforeEach(() => {
    // Clear services
    auditService.clear();
    lockingService.forceRelease("task", "test-task-1");
    lockingService.forceRelease("project", "test-project-1");

    // Clear all locks
    const allLocks = lockingService.getAllLocks();
    allLocks.forEach((lock) => {
      lockingService.forceRelease(lock.objectType, lock.objectId);
    });

    // Reset mock
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("getHealthStatus", () => {
    it("should return healthy status when backend is healthy", async () => {
      // Mock successful backend health check
      vi.mocked(backendClient.health).mockResolvedValue(undefined);

      const status = await healthService.getHealthStatus();

      expect(status.healthy).toBe(true);
      expect(status.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
      expect(status.services.backend.healthy).toBe(true);
      expect(status.services.backend.latencyMs).toBeGreaterThanOrEqual(0);
      expect(status.services.locking.healthy).toBe(true);
      expect(status.services.audit.healthy).toBe(true);
    });

    it("should return unhealthy status when backend is down", async () => {
      // Mock backend failure
      vi.mocked(backendClient.health).mockRejectedValue(
        new Error("Connection refused")
      );

      const status = await healthService.getHealthStatus();

      expect(status.healthy).toBe(false);
      expect(status.services.backend.healthy).toBe(false);
      expect(status.services.backend.error).toBe("Connection refused");
      expect(status.services.backend.latencyMs).toBeUndefined();
    });

    it("should measure backend latency", async () => {
      // Mock backend with delay
      vi.mocked(backendClient.health).mockImplementation(async () => {
        await new Promise((resolve) => setTimeout(resolve, 50));
      });

      const status = await healthService.getHealthStatus();

      expect(status.services.backend.healthy).toBe(true);
      expect(status.services.backend.latencyMs).toBeGreaterThanOrEqual(50);
      expect(status.services.backend.latencyMs).toBeLessThan(200); // Should be close to 50ms
    });

    it("should handle non-Error backend failures", async () => {
      // Mock backend with non-Error rejection
      vi.mocked(backendClient.health).mockRejectedValue("String error");

      const status = await healthService.getHealthStatus();

      expect(status.services.backend.healthy).toBe(false);
      expect(status.services.backend.error).toBe("Unknown error");
    });

    it("should include locking service stats", async () => {
      vi.mocked(backendClient.health).mockResolvedValue(undefined);

      // Create some locks
      lockingService.checkout("task", "task-001", "agent-1");
      lockingService.checkout("task", "task-002", "agent-2");
      lockingService.checkout("project", "proj-001", "agent-1");

      const status = await healthService.getHealthStatus();

      expect(status.services.locking.healthy).toBe(true);
      expect(status.services.locking.activeLocks).toBe(3);
      expect(status.services.locking.oldestLockAgeMs).toBeGreaterThanOrEqual(0);
    });

    it("should handle zero locks in locking service", async () => {
      vi.mocked(backendClient.health).mockResolvedValue(undefined);

      const status = await healthService.getHealthStatus();

      expect(status.services.locking.healthy).toBe(true);
      expect(status.services.locking.activeLocks).toBe(0);
      expect(status.services.locking.oldestLockAgeMs).toBeNull();
    });

    it("should include audit service stats", async () => {
      vi.mocked(backendClient.health).mockResolvedValue(undefined);

      // Create some audit logs
      auditService.log({
        operation: "test_op_1",
        agent: "test_agent",
        result: "success",
      });
      auditService.log({
        operation: "test_op_2",
        agent: "test_agent",
        result: "success",
      });
      auditService.log({
        operation: "test_op_3",
        agent: "test_agent",
        result: "success",
      });

      const status = await healthService.getHealthStatus();

      expect(status.services.audit.healthy).toBe(true);
      expect(status.services.audit.logCount).toBe(3);
    });

    it("should handle zero logs in audit service", async () => {
      vi.mocked(backendClient.health).mockResolvedValue(undefined);

      const status = await healthService.getHealthStatus();

      expect(status.services.audit.healthy).toBe(true);
      expect(status.services.audit.logCount).toBe(0);
    });

    it("should check all services concurrently", async () => {
      const mockHealthCalls: number[] = [];

      vi.mocked(backendClient.health).mockImplementation(async () => {
        mockHealthCalls.push(Date.now());
      });

      // Add locks and logs to ensure other services are checked
      lockingService.checkout("task", "task-001", "agent-1");
      auditService.log({
        operation: "test_op",
        agent: "test_agent",
        result: "success",
      });

      const status = await healthService.getHealthStatus();

      // Verify backend was called
      expect(mockHealthCalls.length).toBe(1);

      // Verify all services are in the status
      expect(status.services.backend).toBeDefined();
      expect(status.services.locking).toBeDefined();
      expect(status.services.audit).toBeDefined();
    });

    it("should update timestamp on each call", async () => {
      vi.mocked(backendClient.health).mockResolvedValue(undefined);

      const status1 = await healthService.getHealthStatus();
      await new Promise((resolve) => setTimeout(resolve, 10));
      const status2 = await healthService.getHealthStatus();

      const timestamp1 = new Date(status1.timestamp).getTime();
      const timestamp2 = new Date(status2.timestamp).getTime();

      expect(timestamp2).toBeGreaterThan(timestamp1);
    });

    it("should aggregate health based on backend status", async () => {
      // Test 1: Backend healthy = overall healthy
      vi.mocked(backendClient.health).mockResolvedValue(undefined);
      const healthyStatus = await healthService.getHealthStatus();
      expect(healthyStatus.healthy).toBe(true);

      // Test 2: Backend unhealthy = overall unhealthy
      vi.mocked(backendClient.health).mockRejectedValue(new Error("Backend down"));
      const unhealthyStatus = await healthService.getHealthStatus();
      expect(unhealthyStatus.healthy).toBe(false);
    });

    it("should handle full audit log buffer (1000 logs)", async () => {
      vi.mocked(backendClient.health).mockResolvedValue(undefined);

      // Fill audit log to max (1000 logs)
      for (let i = 0; i < 1500; i++) {
        auditService.log({
          operation: `test_op_${i}`,
          agent: "test_agent",
          result: "success",
        });
      }

      const status = await healthService.getHealthStatus();

      // Should show 1000 logs (max buffer size)
      expect(status.services.audit.logCount).toBe(1000);
    });
  });

  describe("isHealthy", () => {
    it("should return true when backend is healthy", async () => {
      vi.mocked(backendClient.health).mockResolvedValue(undefined);

      const result = await healthService.isHealthy();

      expect(result).toBe(true);
      expect(backendClient.health).toHaveBeenCalledTimes(1);
    });

    it("should return false when backend is unhealthy", async () => {
      vi.mocked(backendClient.health).mockRejectedValue(new Error("Connection failed"));

      const result = await healthService.isHealthy();

      expect(result).toBe(false);
      expect(backendClient.health).toHaveBeenCalledTimes(1);
    });

    it("should handle non-Error rejections", async () => {
      vi.mocked(backendClient.health).mockRejectedValue("Unexpected error");

      const result = await healthService.isHealthy();

      expect(result).toBe(false);
    });

    it("should not throw errors on backend failure", async () => {
      vi.mocked(backendClient.health).mockRejectedValue(new Error("Backend error"));

      // Should not throw
      await expect(healthService.isHealthy()).resolves.toBe(false);
    });

    it("should be fast (only checks backend)", async () => {
      vi.mocked(backendClient.health).mockResolvedValue(undefined);

      const startTime = Date.now();
      await healthService.isHealthy();
      const duration = Date.now() - startTime;

      // Should be very fast (< 100ms without network delays)
      expect(duration).toBeLessThan(100);
    });
  });

  describe("integration with other services", () => {
    it("should reflect real locking service state", async () => {
      vi.mocked(backendClient.health).mockResolvedValue(undefined);
      vi.useFakeTimers();

      // Create locks at different times
      lockingService.checkout("task", "task-001", "agent-1");
      vi.advanceTimersByTime(5000); // 5 seconds
      lockingService.checkout("task", "task-002", "agent-2");

      const status = await healthService.getHealthStatus();

      expect(status.services.locking.activeLocks).toBe(2);
      expect(status.services.locking.oldestLockAgeMs).toBeGreaterThanOrEqual(5000);

      vi.useRealTimers();
    });

    it("should reflect real audit service state", async () => {
      vi.mocked(backendClient.health).mockResolvedValue(undefined);

      // Create logs
      for (let i = 0; i < 50; i++) {
        auditService.log({
          operation: `op_${i}`,
          agent: "test_agent",
          result: "success",
        });
      }

      const status = await healthService.getHealthStatus();

      expect(status.services.audit.logCount).toBe(50);
    });

    it("should show cleared audit logs", async () => {
      vi.mocked(backendClient.health).mockResolvedValue(undefined);

      // Create and clear logs
      auditService.log({ operation: "test", agent: "agent", result: "success" });
      auditService.clear();

      const status = await healthService.getHealthStatus();

      expect(status.services.audit.logCount).toBe(0);
    });

    it("should show released locks", async () => {
      vi.mocked(backendClient.health).mockResolvedValue(undefined);

      // Create and release locks
      lockingService.checkout("task", "task-001", "agent-1");
      lockingService.checkout("task", "task-002", "agent-1");
      lockingService.checkin("task", "task-001", "agent-1");

      const status = await healthService.getHealthStatus();

      expect(status.services.locking.activeLocks).toBe(1);
    });
  });

  describe("edge cases", () => {
    it("should handle backend timeout simulation", async () => {
      // Mock very slow backend
      vi.mocked(backendClient.health).mockImplementation(async () => {
        await new Promise((resolve) => setTimeout(resolve, 500));
      });

      const startTime = Date.now();
      const status = await healthService.getHealthStatus();
      const duration = Date.now() - startTime;

      expect(status.services.backend.healthy).toBe(true);
      expect(status.services.backend.latencyMs).toBeGreaterThanOrEqual(500);
      expect(duration).toBeGreaterThanOrEqual(500);
    });

    it("should handle concurrent health checks", async () => {
      vi.mocked(backendClient.health).mockResolvedValue(undefined);

      const [status1, status2, status3] = await Promise.all([
        healthService.getHealthStatus(),
        healthService.getHealthStatus(),
        healthService.getHealthStatus(),
      ]);

      expect(status1.healthy).toBe(true);
      expect(status2.healthy).toBe(true);
      expect(status3.healthy).toBe(true);

      // Backend health should be called 3 times (once per check)
      expect(backendClient.health).toHaveBeenCalledTimes(3);
    });

    it("should handle mixed concurrent isHealthy calls", async () => {
      vi.mocked(backendClient.health).mockResolvedValue(undefined);

      const results = await Promise.all([
        healthService.isHealthy(),
        healthService.isHealthy(),
        healthService.isHealthy(),
      ]);

      expect(results).toEqual([true, true, true]);
      expect(backendClient.health).toHaveBeenCalledTimes(3);
    });

    it("should handle alternating backend states", async () => {
      // First call: healthy
      vi.mocked(backendClient.health).mockResolvedValueOnce(undefined);
      const status1 = await healthService.getHealthStatus();
      expect(status1.healthy).toBe(true);

      // Second call: unhealthy
      vi.mocked(backendClient.health).mockRejectedValueOnce(new Error("Down"));
      const status2 = await healthService.getHealthStatus();
      expect(status2.healthy).toBe(false);

      // Third call: healthy again
      vi.mocked(backendClient.health).mockResolvedValueOnce(undefined);
      const status3 = await healthService.getHealthStatus();
      expect(status3.healthy).toBe(true);
    });
  });
});
