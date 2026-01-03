/**
 * Memory Monitor Tests
 *
 * Tests for MemoryMonitor class that monitors memory usage
 * and warns when thresholds are exceeded.
 *
 * @module infrastructure/memory-monitor.test
 */

import { describe, it, expect, vi, beforeEach, afterEach, type Mock } from "vitest";
import { MemoryMonitor, memoryMonitor } from "./memory-monitor.js";
import { logger } from "./logger.js";

// Mock the logger
vi.mock("./logger.js", () => ({
  logger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
  },
}));

describe("MemoryMonitor", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe("constructor", () => {
    it("should create with default thresholds", () => {
      const monitor = new MemoryMonitor();
      expect(monitor).toBeDefined();
    });

    it("should accept custom warning threshold", () => {
      const monitor = new MemoryMonitor({ warning: 100 });
      expect(monitor).toBeDefined();
    });

    it("should accept custom critical threshold", () => {
      const monitor = new MemoryMonitor({ critical: 500 });
      expect(monitor).toBeDefined();
    });

    it("should accept both custom thresholds", () => {
      const monitor = new MemoryMonitor({ warning: 150, critical: 300 });
      expect(monitor).toBeDefined();
    });
  });

  describe("start", () => {
    it("should log when monitoring starts", () => {
      const monitor = new MemoryMonitor();
      monitor.start(60000);

      expect(logger.info).toHaveBeenCalledWith(
        expect.objectContaining({
          intervalMs: 60000,
          thresholds: expect.any(Object),
        }),
        "Memory monitoring started"
      );

      monitor.stop();
    });

    it("should not start twice if already running", () => {
      const monitor = new MemoryMonitor();
      monitor.start(60000);
      monitor.start(60000);

      // Should only log once
      expect(logger.info).toHaveBeenCalledTimes(1);

      monitor.stop();
    });

    it("should use default interval when not specified", () => {
      const monitor = new MemoryMonitor();
      monitor.start();

      expect(logger.info).toHaveBeenCalledWith(
        expect.objectContaining({
          intervalMs: 60000, // Default
        }),
        expect.any(String)
      );

      monitor.stop();
    });

    it("should accept custom interval", () => {
      const monitor = new MemoryMonitor();
      monitor.start(30000);

      expect(logger.info).toHaveBeenCalledWith(
        expect.objectContaining({
          intervalMs: 30000,
        }),
        expect.any(String)
      );

      monitor.stop();
    });
  });

  describe("stop", () => {
    it("should log when monitoring stops", () => {
      const monitor = new MemoryMonitor();
      monitor.start(60000);
      vi.clearAllMocks();

      monitor.stop();

      expect(logger.info).toHaveBeenCalledWith("Memory monitoring stopped");
    });

    it("should not log if not running", () => {
      const monitor = new MemoryMonitor();
      monitor.stop();

      expect(logger.info).not.toHaveBeenCalled();
    });

    it("should allow restart after stop", () => {
      const monitor = new MemoryMonitor();
      monitor.start(60000);
      monitor.stop();
      vi.clearAllMocks();

      monitor.start(60000);
      expect(logger.info).toHaveBeenCalledWith(
        expect.any(Object),
        "Memory monitoring started"
      );

      monitor.stop();
    });
  });

  describe("getMemoryUsage", () => {
    it("should return memory usage in MB", () => {
      const monitor = new MemoryMonitor();
      const usage = monitor.getMemoryUsage();

      expect(usage).toHaveProperty("heapUsedMB");
      expect(usage).toHaveProperty("heapTotalMB");
      expect(usage).toHaveProperty("rssMB");
      expect(usage).toHaveProperty("externalMB");
      expect(usage).toHaveProperty("arrayBuffersMB");
    });

    it("should return numeric values", () => {
      const monitor = new MemoryMonitor();
      const usage = monitor.getMemoryUsage();

      expect(typeof usage.heapUsedMB).toBe("number");
      expect(typeof usage.heapTotalMB).toBe("number");
      expect(typeof usage.rssMB).toBe("number");
      expect(typeof usage.externalMB).toBe("number");
      expect(typeof usage.arrayBuffersMB).toBe("number");
    });

    it("should return rounded values", () => {
      const monitor = new MemoryMonitor();
      const usage = monitor.getMemoryUsage();

      expect(Number.isInteger(usage.heapUsedMB)).toBe(true);
      expect(Number.isInteger(usage.heapTotalMB)).toBe(true);
      expect(Number.isInteger(usage.rssMB)).toBe(true);
    });

    it("should return positive values", () => {
      const monitor = new MemoryMonitor();
      const usage = monitor.getMemoryUsage();

      expect(usage.heapUsedMB).toBeGreaterThanOrEqual(0);
      expect(usage.heapTotalMB).toBeGreaterThanOrEqual(0);
      expect(usage.rssMB).toBeGreaterThanOrEqual(0);
    });
  });

  describe("memory checking intervals", () => {
    it("should check memory at specified intervals", () => {
      const monitor = new MemoryMonitor();
      monitor.start(1000);

      // Advance time by 3 intervals
      vi.advanceTimersByTime(3000);

      // Should have logged debug messages (assuming normal memory)
      expect(logger.debug).toHaveBeenCalled();

      monitor.stop();
    });

    it("should not check memory after stop", () => {
      const monitor = new MemoryMonitor();
      monitor.start(1000);

      vi.advanceTimersByTime(1000);
      const callCount = (logger.debug as Mock).mock.calls.length;

      monitor.stop();
      vi.clearAllMocks();

      vi.advanceTimersByTime(5000);
      expect(logger.debug).not.toHaveBeenCalled();
    });
  });

  describe("forceGC", () => {
    it("should warn if gc is not available", () => {
      const monitor = new MemoryMonitor();

      // global.gc should not be defined in normal tests
      monitor.forceGC();

      expect(logger.warn).toHaveBeenCalledWith(
        "Garbage collection not available (run with --expose-gc)"
      );
    });

    it("should call gc and log results if available", () => {
      const monitor = new MemoryMonitor();

      // Mock global.gc
      const mockGc = vi.fn();
      (global as any).gc = mockGc;

      monitor.forceGC();

      expect(mockGc).toHaveBeenCalled();
      expect(logger.info).toHaveBeenCalledWith(
        expect.objectContaining({
          beforeMB: expect.any(Number),
          afterMB: expect.any(Number),
          freedMB: expect.any(Number),
        }),
        "Garbage collection completed"
      );

      // Cleanup
      delete (global as any).gc;
    });
  });

  describe("threshold alerts", () => {
    it("should log debug for normal memory usage", () => {
      // Create monitor with very high thresholds to ensure "normal" status
      const monitor = new MemoryMonitor({
        warning: 10000, // 10 GB
        critical: 20000, // 20 GB
      });

      monitor.start(100);
      vi.advanceTimersByTime(100);

      expect(logger.debug).toHaveBeenCalledWith(
        expect.objectContaining({
          memoryUsage: expect.any(Object),
        }),
        "Memory usage normal"
      );

      monitor.stop();
    });

    // Note: Testing warning/critical thresholds requires mocking process.memoryUsage
    // which is more complex. In real scenarios, these would be integration tests.
  });

  describe("singleton instance", () => {
    it("should export singleton memoryMonitor", () => {
      expect(memoryMonitor).toBeInstanceOf(MemoryMonitor);
    });

    it("singleton should have default thresholds", () => {
      const usage = memoryMonitor.getMemoryUsage();
      expect(usage).toBeDefined();
    });
  });

  describe("edge cases", () => {
    it("should handle very short intervals", () => {
      const monitor = new MemoryMonitor();
      monitor.start(1);

      vi.advanceTimersByTime(10);

      // Should not throw
      expect(logger.debug).toHaveBeenCalled();

      monitor.stop();
    });

    it("should handle partial threshold overrides", () => {
      const monitor1 = new MemoryMonitor({ warning: 100 });
      const monitor2 = new MemoryMonitor({ critical: 500 });

      // Both should work without errors
      expect(monitor1.getMemoryUsage()).toBeDefined();
      expect(monitor2.getMemoryUsage()).toBeDefined();
    });
  });
});
