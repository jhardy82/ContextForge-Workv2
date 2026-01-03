import { describe, it, expect, beforeEach, vi, afterEach } from "vitest";
import {
  notificationService,
  type NotificationEvent,
} from "./notifications.js";

describe("Notification Service", () => {
  beforeEach(() => {
    notificationService.clear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("on and off", () => {
    it("should subscribe to event type", () => {
      const handler = vi.fn();

      notificationService.on("task:created", handler);

      const stats = notificationService.getStats();
      expect(stats.totalHandlers).toBe(1);
      expect(stats.handlersByType["task:created"]).toBe(1);
    });

    it("should support multiple handlers for same event", () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();
      const handler3 = vi.fn();

      notificationService.on("task:created", handler1);
      notificationService.on("task:created", handler2);
      notificationService.on("task:created", handler3);

      const stats = notificationService.getStats();
      expect(stats.totalHandlers).toBe(3);
      expect(stats.handlersByType["task:created"]).toBe(3);
    });

    it("should support handlers for different event types", () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();
      const handler3 = vi.fn();

      notificationService.on("task:created", handler1);
      notificationService.on("task:updated", handler2);
      notificationService.on("lock:acquired", handler3);

      const stats = notificationService.getStats();
      expect(stats.totalHandlers).toBe(3);
      expect(stats.handlersByType["task:created"]).toBe(1);
      expect(stats.handlersByType["task:updated"]).toBe(1);
      expect(stats.handlersByType["lock:acquired"]).toBe(1);
    });

    it("should unsubscribe handler from event", () => {
      const handler = vi.fn();

      notificationService.on("task:created", handler);
      expect(notificationService.getStats().totalHandlers).toBe(1);

      notificationService.off("task:created", handler);
      expect(notificationService.getStats().totalHandlers).toBe(0);
    });

    it("should only remove specific handler", () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();

      notificationService.on("task:created", handler1);
      notificationService.on("task:created", handler2);

      notificationService.off("task:created", handler1);

      const stats = notificationService.getStats();
      expect(stats.totalHandlers).toBe(1);
      expect(stats.handlersByType["task:created"]).toBe(1);
    });

    it("should handle off for non-existent event type", () => {
      const handler = vi.fn();

      // Should not throw
      notificationService.off("task:created", handler);

      expect(notificationService.getStats().totalHandlers).toBe(0);
    });

    it("should handle off for non-subscribed handler", () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();

      notificationService.on("task:created", handler1);
      notificationService.off("task:created", handler2); // Different handler

      const stats = notificationService.getStats();
      expect(stats.totalHandlers).toBe(1); // handler1 still subscribed
    });
  });

  describe("emit", () => {
    it("should emit task:created event", async () => {
      const handler = vi.fn();
      notificationService.on("task:created", handler);

      await notificationService.emit({
        type: "task:created",
        taskId: "T-123",
        projectId: "P-456",
      });

      expect(handler).toHaveBeenCalledTimes(1);
      expect(handler).toHaveBeenCalledWith({
        type: "task:created",
        taskId: "T-123",
        projectId: "P-456",
      });
    });

    it("should emit task:updated event", async () => {
      const handler = vi.fn();
      notificationService.on("task:updated", handler);

      await notificationService.emit({
        type: "task:updated",
        taskId: "T-123",
        changes: ["status", "priority"],
      });

      expect(handler).toHaveBeenCalledWith({
        type: "task:updated",
        taskId: "T-123",
        changes: ["status", "priority"],
      });
    });

    it("should emit task:deleted event", async () => {
      const handler = vi.fn();
      notificationService.on("task:deleted", handler);

      await notificationService.emit({
        type: "task:deleted",
        taskId: "T-123",
      });

      expect(handler).toHaveBeenCalledWith({
        type: "task:deleted",
        taskId: "T-123",
      });
    });

    it("should emit lock:acquired event", async () => {
      const handler = vi.fn();
      notificationService.on("lock:acquired", handler);

      await notificationService.emit({
        type: "lock:acquired",
        objectType: "task",
        objectId: "T-123",
        agent: "agent-1",
      });

      expect(handler).toHaveBeenCalledWith({
        type: "lock:acquired",
        objectType: "task",
        objectId: "T-123",
        agent: "agent-1",
      });
    });

    it("should emit lock:released event", async () => {
      const handler = vi.fn();
      notificationService.on("lock:released", handler);

      await notificationService.emit({
        type: "lock:released",
        objectType: "task",
        objectId: "T-123",
        agent: "agent-1",
      });

      expect(handler).toHaveBeenCalledWith({
        type: "lock:released",
        objectType: "task",
        objectId: "T-123",
        agent: "agent-1",
      });
    });

    it("should emit lock:expired event", async () => {
      const handler = vi.fn();
      notificationService.on("lock:expired", handler);

      await notificationService.emit({
        type: "lock:expired",
        objectType: "task",
        objectId: "T-123",
      });

      expect(handler).toHaveBeenCalledWith({
        type: "lock:expired",
        objectType: "task",
        objectId: "T-123",
      });
    });

    it("should emit health:degraded event", async () => {
      const handler = vi.fn();
      notificationService.on("health:degraded", handler);

      await notificationService.emit({
        type: "health:degraded",
        service: "backend",
        reason: "Connection timeout",
      });

      expect(handler).toHaveBeenCalledWith({
        type: "health:degraded",
        service: "backend",
        reason: "Connection timeout",
      });
    });

    it("should emit health:recovered event", async () => {
      const handler = vi.fn();
      notificationService.on("health:recovered", handler);

      await notificationService.emit({
        type: "health:recovered",
        service: "backend",
      });

      expect(handler).toHaveBeenCalledWith({
        type: "health:recovered",
        service: "backend",
      });
    });

    it("should call all handlers for same event type", async () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();
      const handler3 = vi.fn();

      notificationService.on("task:created", handler1);
      notificationService.on("task:created", handler2);
      notificationService.on("task:created", handler3);

      await notificationService.emit({
        type: "task:created",
        taskId: "T-123",
        projectId: "P-456",
      });

      expect(handler1).toHaveBeenCalledTimes(1);
      expect(handler2).toHaveBeenCalledTimes(1);
      expect(handler3).toHaveBeenCalledTimes(1);
    });

    it("should not call handlers for different event types", async () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();

      notificationService.on("task:created", handler1);
      notificationService.on("task:updated", handler2);

      await notificationService.emit({
        type: "task:created",
        taskId: "T-123",
        projectId: "P-456",
      });

      expect(handler1).toHaveBeenCalledTimes(1);
      expect(handler2).not.toHaveBeenCalled();
    });

    it("should handle async handlers", async () => {
      const handler = vi.fn(async () => {
        await new Promise((resolve) => setTimeout(resolve, 10));
      });

      notificationService.on("task:created", handler);

      await notificationService.emit({
        type: "task:created",
        taskId: "T-123",
        projectId: "P-456",
      });

      expect(handler).toHaveBeenCalledTimes(1);
    });

    it("should handle sync handlers", async () => {
      const handler = vi.fn(() => {
        return "sync return value";
      });

      notificationService.on("task:created", handler);

      await notificationService.emit({
        type: "task:created",
        taskId: "T-123",
        projectId: "P-456",
      });

      expect(handler).toHaveBeenCalledTimes(1);
    });

    it("should handle no handlers gracefully", async () => {
      // Should not throw when no handlers are subscribed
      await expect(
        notificationService.emit({
          type: "task:created",
          taskId: "T-123",
          projectId: "P-456",
        })
      ).resolves.toBeUndefined();
    });

    it("should isolate handler errors", async () => {
      const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {});

      const handler1 = vi.fn(async () => {
        throw new Error("Handler 1 failed");
      });
      const handler2 = vi.fn();
      const handler3 = vi.fn(async () => {
        throw new Error("Handler 3 failed");
      });

      notificationService.on("task:created", handler1);
      notificationService.on("task:created", handler2);
      notificationService.on("task:created", handler3);

      await notificationService.emit({
        type: "task:created",
        taskId: "T-123",
        projectId: "P-456",
      });

      // All handlers should be called despite errors
      expect(handler1).toHaveBeenCalledTimes(1);
      expect(handler2).toHaveBeenCalledTimes(1);
      expect(handler3).toHaveBeenCalledTimes(1);

      // Errors should be logged
      expect(consoleErrorSpy).toHaveBeenCalledTimes(2);

      consoleErrorSpy.mockRestore();
    });

    it("should execute handlers in parallel", async () => {
      const executionOrder: number[] = [];

      const handler1 = vi.fn(async () => {
        await new Promise((resolve) => setTimeout(resolve, 30));
        executionOrder.push(1);
      });

      const handler2 = vi.fn(async () => {
        await new Promise((resolve) => setTimeout(resolve, 10));
        executionOrder.push(2);
      });

      const handler3 = vi.fn(async () => {
        await new Promise((resolve) => setTimeout(resolve, 20));
        executionOrder.push(3);
      });

      notificationService.on("task:created", handler1);
      notificationService.on("task:created", handler2);
      notificationService.on("task:created", handler3);

      await notificationService.emit({
        type: "task:created",
        taskId: "T-123",
        projectId: "P-456",
      });

      // handler2 should finish first (10ms), then handler3 (20ms), then handler1 (30ms)
      expect(executionOrder).toEqual([2, 3, 1]);
    });
  });

  describe("getStats", () => {
    it("should return zero stats when no handlers", () => {
      const stats = notificationService.getStats();

      expect(stats.totalHandlers).toBe(0);
      expect(stats.handlersByType).toEqual({});
    });

    it("should return correct stats for single handler", () => {
      const handler = vi.fn();
      notificationService.on("task:created", handler);

      const stats = notificationService.getStats();

      expect(stats.totalHandlers).toBe(1);
      expect(stats.handlersByType).toEqual({
        "task:created": 1,
      });
    });

    it("should return correct stats for multiple handlers", () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();
      const handler3 = vi.fn();
      const handler4 = vi.fn();

      notificationService.on("task:created", handler1);
      notificationService.on("task:created", handler2);
      notificationService.on("task:updated", handler3);
      notificationService.on("lock:acquired", handler4);

      const stats = notificationService.getStats();

      expect(stats.totalHandlers).toBe(4);
      expect(stats.handlersByType).toEqual({
        "task:created": 2,
        "task:updated": 1,
        "lock:acquired": 1,
      });
    });

    it("should update stats after removing handlers", () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();

      notificationService.on("task:created", handler1);
      notificationService.on("task:created", handler2);

      expect(notificationService.getStats().totalHandlers).toBe(2);

      notificationService.off("task:created", handler1);

      expect(notificationService.getStats().totalHandlers).toBe(1);
    });

    it("should show all event types with handlers", () => {
      notificationService.on("task:created", vi.fn());
      notificationService.on("task:updated", vi.fn());
      notificationService.on("task:deleted", vi.fn());
      notificationService.on("lock:acquired", vi.fn());
      notificationService.on("lock:released", vi.fn());
      notificationService.on("lock:expired", vi.fn());
      notificationService.on("health:degraded", vi.fn());
      notificationService.on("health:recovered", vi.fn());

      const stats = notificationService.getStats();

      expect(stats.totalHandlers).toBe(8);
      expect(Object.keys(stats.handlersByType)).toHaveLength(8);
    });
  });

  describe("clear", () => {
    it("should remove all handlers", () => {
      notificationService.on("task:created", vi.fn());
      notificationService.on("task:updated", vi.fn());
      notificationService.on("lock:acquired", vi.fn());

      expect(notificationService.getStats().totalHandlers).toBe(3);

      notificationService.clear();

      expect(notificationService.getStats().totalHandlers).toBe(0);
      expect(notificationService.getStats().handlersByType).toEqual({});
    });

    it("should prevent cleared handlers from being called", async () => {
      const handler = vi.fn();
      notificationService.on("task:created", handler);

      notificationService.clear();

      await notificationService.emit({
        type: "task:created",
        taskId: "T-123",
        projectId: "P-456",
      });

      expect(handler).not.toHaveBeenCalled();
    });

    it("should allow new handlers after clear", () => {
      notificationService.on("task:created", vi.fn());
      notificationService.clear();

      const newHandler = vi.fn();
      notificationService.on("task:created", newHandler);

      const stats = notificationService.getStats();
      expect(stats.totalHandlers).toBe(1);
    });
  });

  describe("edge cases", () => {
    it("should handle same handler registered multiple times", () => {
      const handler = vi.fn();

      notificationService.on("task:created", handler);
      notificationService.on("task:created", handler);
      notificationService.on("task:created", handler);

      // Set should deduplicate
      const stats = notificationService.getStats();
      expect(stats.handlersByType["task:created"]).toBe(1);
    });

    it("should handle handler returning promise", async () => {
      const handler = vi.fn(async () => {
        return { success: true };
      });

      notificationService.on("task:created", handler);

      await notificationService.emit({
        type: "task:created",
        taskId: "T-123",
        projectId: "P-456",
      });

      expect(handler).toHaveBeenCalledTimes(1);
    });

    it("should handle handler returning value", async () => {
      const handler = vi.fn(() => {
        return { success: true };
      });

      notificationService.on("task:created", handler);

      await notificationService.emit({
        type: "task:created",
        taskId: "T-123",
        projectId: "P-456",
      });

      expect(handler).toHaveBeenCalledTimes(1);
    });

    it("should handle handler returning void", async () => {
      const handler = vi.fn(() => {
        // No return
      });

      notificationService.on("task:created", handler);

      await notificationService.emit({
        type: "task:created",
        taskId: "T-123",
        projectId: "P-456",
      });

      expect(handler).toHaveBeenCalledTimes(1);
    });
  });
});
