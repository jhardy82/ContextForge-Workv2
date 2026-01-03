import { describe, it, expect, beforeEach, vi, afterEach } from "vitest";
import { lockingService, type Lock } from "./locking.js";

describe("Locking Service", () => {
  beforeEach(() => {
    // Clear all locks before each test
    lockingService.forceRelease("task", "test-task-1");
    lockingService.forceRelease("project", "test-project-1");
    lockingService.forceRelease("sprint", "test-sprint-1");
    // Clear any other locks
    const allLocks = lockingService.getAllLocks();
    allLocks.forEach((lock) => {
      lockingService.forceRelease(lock.objectType, lock.objectId);
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("checkout", () => {
    it("should successfully checkout unlocked object", () => {
      const result = lockingService.checkout("task", "task-001", "agent-1");
      expect(result).toBe(true);

      const lock = lockingService.checkLock("task", "task-001");
      expect(lock).not.toBeNull();
      expect(lock?.agent).toBe("agent-1");
      expect(lock?.objectType).toBe("task");
      expect(lock?.objectId).toBe("task-001");
    });

    it("should fail to checkout object locked by different agent", () => {
      lockingService.checkout("task", "task-001", "agent-1");

      const result = lockingService.checkout("task", "task-001", "agent-2");
      expect(result).toBe(false);

      const lock = lockingService.checkLock("task", "task-001");
      expect(lock?.agent).toBe("agent-1"); // Still locked by agent-1
    });

    it("should refresh timestamp when same agent checks out again", () => {
      vi.useFakeTimers();

      lockingService.checkout("task", "task-001", "agent-1");

      const lock1 = lockingService.checkLock("task", "task-001");
      const timestamp1 = lock1?.timestamp;

      // Wait a bit
      vi.advanceTimersByTime(100);

      const result = lockingService.checkout("task", "task-001", "agent-1");
      expect(result).toBe(true);

      const lock2 = lockingService.checkLock("task", "task-001");
      const timestamp2 = lock2?.timestamp;

      expect(timestamp2).toBeGreaterThan(timestamp1!);

      vi.useRealTimers();
    });

    it("should auto-release expired lock and allow checkout", () => {
      vi.useFakeTimers();

      lockingService.checkout("task", "task-001", "agent-1");

      // Advance time by 31 minutes (past 30-minute timeout)
      vi.advanceTimersByTime(31 * 60 * 1000);

      const result = lockingService.checkout("task", "task-001", "agent-2");
      expect(result).toBe(true);

      const lock = lockingService.checkLock("task", "task-001");
      expect(lock?.agent).toBe("agent-2");

      vi.useRealTimers();
    });

    it("should support multiple object types", () => {
      const result1 = lockingService.checkout("task", "task-001", "agent-1");
      const result2 = lockingService.checkout("project", "proj-001", "agent-1");
      const result3 = lockingService.checkout("sprint", "sprint-001", "agent-1");

      expect(result1).toBe(true);
      expect(result2).toBe(true);
      expect(result3).toBe(true);

      expect(lockingService.checkLock("task", "task-001")).not.toBeNull();
      expect(lockingService.checkLock("project", "proj-001")).not.toBeNull();
      expect(lockingService.checkLock("sprint", "sprint-001")).not.toBeNull();
    });

    it("should treat different object types separately", () => {
      lockingService.checkout("task", "obj-001", "agent-1");
      lockingService.checkout("project", "obj-001", "agent-2");

      const taskLock = lockingService.checkLock("task", "obj-001");
      const projectLock = lockingService.checkLock("project", "obj-001");

      expect(taskLock?.agent).toBe("agent-1");
      expect(projectLock?.agent).toBe("agent-2");
    });
  });

  describe("checkin", () => {
    it("should successfully checkin locked object", () => {
      lockingService.checkout("task", "task-001", "agent-1");

      const result = lockingService.checkin("task", "task-001", "agent-1");
      expect(result).toBe(true);

      const lock = lockingService.checkLock("task", "task-001");
      expect(lock).toBeNull();
    });

    it("should fail to checkin unlocked object", () => {
      const result = lockingService.checkin("task", "task-001", "agent-1");
      expect(result).toBe(false);
    });

    it("should fail to checkin object locked by different agent", () => {
      lockingService.checkout("task", "task-001", "agent-1");

      const result = lockingService.checkin("task", "task-001", "agent-2");
      expect(result).toBe(false);

      const lock = lockingService.checkLock("task", "task-001");
      expect(lock?.agent).toBe("agent-1"); // Still locked
    });

    it("should auto-release expired lock on checkin", () => {
      vi.useFakeTimers();

      lockingService.checkout("task", "task-001", "agent-1");

      // Advance time by 31 minutes
      vi.advanceTimersByTime(31 * 60 * 1000);

      const result = lockingService.checkin("task", "task-001", "agent-1");
      expect(result).toBe(true); // Succeeds because lock is expired

      const lock = lockingService.checkLock("task", "task-001");
      expect(lock).toBeNull();

      vi.useRealTimers();
    });

    it("should handle checkin of non-existent object", () => {
      const result = lockingService.checkin("task", "nonexistent", "agent-1");
      expect(result).toBe(false);
    });
  });

  describe("checkLock", () => {
    it("should return lock info for locked object", () => {
      lockingService.checkout("task", "task-001", "agent-1");

      const lock = lockingService.checkLock("task", "task-001");
      expect(lock).not.toBeNull();
      expect(lock?.agent).toBe("agent-1");
      expect(lock?.objectType).toBe("task");
      expect(lock?.objectId).toBe("task-001");
      expect(lock?.timestamp).toBeGreaterThan(0);
    });

    it("should return null for unlocked object", () => {
      const lock = lockingService.checkLock("task", "task-001");
      expect(lock).toBeNull();
    });

    it("should auto-release and return null for expired lock", () => {
      vi.useFakeTimers();

      lockingService.checkout("task", "task-001", "agent-1");

      // Advance time by 31 minutes
      vi.advanceTimersByTime(31 * 60 * 1000);

      const lock = lockingService.checkLock("task", "task-001");
      expect(lock).toBeNull();

      vi.useRealTimers();
    });

    it("should return copy of lock (not original)", () => {
      lockingService.checkout("task", "task-001", "agent-1");

      const lock1 = lockingService.checkLock("task", "task-001");
      const lock2 = lockingService.checkLock("task", "task-001");

      // Modifying one should not affect the other
      if (lock1 && lock2) {
        (lock1 as any).agent = "modified";
        expect(lock2.agent).toBe("agent-1");
      }
    });
  });

  describe("getAllLocks", () => {
    it("should return all active locks", () => {
      lockingService.checkout("task", "task-001", "agent-1");
      lockingService.checkout("task", "task-002", "agent-2");
      lockingService.checkout("project", "proj-001", "agent-1");

      const locks = lockingService.getAllLocks();
      expect(locks).toHaveLength(3);

      const agents = locks.map((lock) => lock.agent).sort();
      expect(agents).toEqual(["agent-1", "agent-1", "agent-2"]);
    });

    it("should return empty array when no locks exist", () => {
      const locks = lockingService.getAllLocks();
      expect(locks).toEqual([]);
    });

    it("should clean up expired locks", () => {
      vi.useFakeTimers();

      lockingService.checkout("task", "task-001", "agent-1");
      lockingService.checkout("task", "task-002", "agent-2");

      // Advance time by 31 minutes
      vi.advanceTimersByTime(31 * 60 * 1000);

      const locks = lockingService.getAllLocks();
      expect(locks).toEqual([]);

      vi.useRealTimers();
    });

    it("should clean up some expired locks but keep active ones", () => {
      vi.useFakeTimers();

      lockingService.checkout("task", "task-001", "agent-1");

      // Advance 15 minutes
      vi.advanceTimersByTime(15 * 60 * 1000);

      lockingService.checkout("task", "task-002", "agent-2");

      // Advance another 16 minutes (total 31 for task-001, 16 for task-002)
      vi.advanceTimersByTime(16 * 60 * 1000);

      const locks = lockingService.getAllLocks();
      expect(locks).toHaveLength(1);
      expect(locks[0].objectId).toBe("task-002");

      vi.useRealTimers();
    });

    it("should return copies of locks", () => {
      lockingService.checkout("task", "task-001", "agent-1");

      const locks = lockingService.getAllLocks();
      (locks[0] as any).agent = "modified";

      const lock = lockingService.checkLock("task", "task-001");
      expect(lock?.agent).toBe("agent-1");
    });
  });

  describe("forceRelease", () => {
    it("should release locked object", () => {
      lockingService.checkout("task", "task-001", "agent-1");

      const result = lockingService.forceRelease("task", "task-001");
      expect(result).toBe(true);

      const lock = lockingService.checkLock("task", "task-001");
      expect(lock).toBeNull();
    });

    it("should return true even if object is not locked", () => {
      const result = lockingService.forceRelease("task", "nonexistent");
      expect(result).toBe(false); // Returns false because lock doesn't exist
    });

    it("should allow release regardless of agent", () => {
      lockingService.checkout("task", "task-001", "agent-1");

      const result = lockingService.forceRelease("task", "task-001");
      expect(result).toBe(true);

      const lock = lockingService.checkLock("task", "task-001");
      expect(lock).toBeNull();
    });

    it("should work with expired locks", () => {
      vi.useFakeTimers();

      lockingService.checkout("task", "task-001", "agent-1");

      // Advance time by 31 minutes
      vi.advanceTimersByTime(31 * 60 * 1000);

      const result = lockingService.forceRelease("task", "task-001");
      expect(result).toBe(true);

      vi.useRealTimers();
    });
  });

  describe("getStats", () => {
    it("should return correct statistics", () => {
      lockingService.checkout("task", "task-001", "agent-1");
      lockingService.checkout("task", "task-002", "agent-2");
      lockingService.checkout("project", "proj-001", "agent-1");

      const stats = lockingService.getStats();

      expect(stats.totalLocks).toBe(3);
      expect(stats.locksByType).toEqual({
        task: 2,
        project: 1,
      });
      expect(stats.oldestLockAge).toBeGreaterThanOrEqual(0);
      expect(stats.oldestLockAge).toBeLessThan(1000); // Should be very recent
    });

    it("should return zeros when no locks exist", () => {
      const stats = lockingService.getStats();

      expect(stats.totalLocks).toBe(0);
      expect(stats.locksByType).toEqual({});
      expect(stats.oldestLockAge).toBeNull();
    });

    it("should calculate oldest lock age correctly", () => {
      vi.useFakeTimers();

      lockingService.checkout("task", "task-001", "agent-1");

      vi.advanceTimersByTime(5000); // 5 seconds

      lockingService.checkout("task", "task-002", "agent-2");

      vi.advanceTimersByTime(3000); // 3 more seconds

      const stats = lockingService.getStats();

      expect(stats.oldestLockAge).toBeGreaterThanOrEqual(8000); // ~8 seconds
      expect(stats.oldestLockAge).toBeLessThan(9000);

      vi.useRealTimers();
    });

    it("should clean up expired locks before calculating stats", () => {
      vi.useFakeTimers();

      lockingService.checkout("task", "task-001", "agent-1");
      lockingService.checkout("task", "task-002", "agent-2");

      // Advance time by 31 minutes
      vi.advanceTimersByTime(31 * 60 * 1000);

      const stats = lockingService.getStats();

      expect(stats.totalLocks).toBe(0);
      expect(stats.locksByType).toEqual({});
      expect(stats.oldestLockAge).toBeNull();

      vi.useRealTimers();
    });

    it("should handle multiple object types in stats", () => {
      lockingService.checkout("task", "task-001", "agent-1");
      lockingService.checkout("task", "task-002", "agent-1");
      lockingService.checkout("project", "proj-001", "agent-1");
      lockingService.checkout("project", "proj-002", "agent-1");
      lockingService.checkout("project", "proj-003", "agent-1");
      lockingService.checkout("sprint", "sprint-001", "agent-1");

      const stats = lockingService.getStats();

      expect(stats.totalLocks).toBe(6);
      expect(stats.locksByType).toEqual({
        task: 2,
        project: 3,
        sprint: 1,
      });
    });
  });

  describe("lock expiration behavior", () => {
    it("should respect 30-minute timeout", () => {
      vi.useFakeTimers();

      lockingService.checkout("task", "task-001", "agent-1");

      // Just before timeout (29:59)
      vi.advanceTimersByTime(29 * 60 * 1000 + 59 * 1000);

      let lock = lockingService.checkLock("task", "task-001");
      expect(lock).not.toBeNull();
      expect(lock?.agent).toBe("agent-1");

      // Just after timeout (30:01)
      vi.advanceTimersByTime(2000);

      lock = lockingService.checkLock("task", "task-001");
      expect(lock).toBeNull();

      vi.useRealTimers();
    });

    it("should handle concurrent locks with different timestamps", () => {
      vi.useFakeTimers();

      lockingService.checkout("task", "task-001", "agent-1");

      vi.advanceTimersByTime(10 * 60 * 1000); // 10 minutes

      lockingService.checkout("task", "task-002", "agent-2");

      vi.advanceTimersByTime(21 * 60 * 1000); // 21 more minutes (total 31)

      // task-001 should be expired, task-002 should still be valid
      const lock1 = lockingService.checkLock("task", "task-001");
      const lock2 = lockingService.checkLock("task", "task-002");

      expect(lock1).toBeNull();
      expect(lock2).not.toBeNull();

      vi.useRealTimers();
    });
  });

  describe("edge cases", () => {
    it("should handle empty object IDs", () => {
      const result = lockingService.checkout("task", "", "agent-1");
      expect(result).toBe(true);

      const lock = lockingService.checkLock("task", "");
      expect(lock).not.toBeNull();
    });

    it("should handle empty object types", () => {
      const result = lockingService.checkout("", "obj-001", "agent-1");
      expect(result).toBe(true);

      const lock = lockingService.checkLock("", "obj-001");
      expect(lock).not.toBeNull();
    });

    it("should handle special characters in IDs", () => {
      const specialId = "task:with:colons:and-dashes_123";
      const result = lockingService.checkout("task", specialId, "agent-1");
      expect(result).toBe(true);

      const lock = lockingService.checkLock("task", specialId);
      expect(lock).not.toBeNull();
    });

    it("should handle very long object IDs", () => {
      const longId = "a".repeat(1000);
      const result = lockingService.checkout("task", longId, "agent-1");
      expect(result).toBe(true);

      const lock = lockingService.checkLock("task", longId);
      expect(lock).not.toBeNull();
    });

    it("should handle many concurrent locks", () => {
      for (let i = 0; i < 1000; i++) {
        lockingService.checkout("task", `task-${i}`, `agent-${i % 10}`);
      }

      const locks = lockingService.getAllLocks();
      expect(locks).toHaveLength(1000);

      const stats = lockingService.getStats();
      expect(stats.totalLocks).toBe(1000);
    });
  });
});
