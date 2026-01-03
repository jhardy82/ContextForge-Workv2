/**
 * Locking Service - Map-based object checkout/checkin
 *
 * Features:
 * - Map<object_id, {agent, timestamp}> for checkout tracking
 * - 30-minute default timeout
 * - Automatic lock expiration
 * - Multi-object type support (projects, sprints, tasks, etc.)
 */

export interface Lock {
  agent: string;
  timestamp: number; // Unix timestamp milliseconds
  objectType: string; // "project", "sprint", "task", etc.
  objectId: string;
}

class LockingService {
  private locks = new Map<string, Lock>();
  private readonly defaultTimeoutMs = 30 * 60 * 1000; // 30 minutes

  /**
   * Generate lock key: {type}:{id}
   */
  private getLockKey(objectType: string, objectId: string): string {
    return `${objectType}:${objectId}`;
  }

  /**
   * Check if lock is expired
   */
  private isExpired(lock: Lock, timeoutMs: number = this.defaultTimeoutMs): boolean {
    const now = Date.now();
    return now - lock.timestamp > timeoutMs;
  }

  /**
   * Checkout object (acquire lock)
   * @returns true if checkout successful, false if locked by another agent
   */
  checkout(objectType: string, objectId: string, agent: string): boolean {
    const key = this.getLockKey(objectType, objectId);
    const existingLock = this.locks.get(key);

    // Check if already locked by different agent
    if (existingLock) {
      // Auto-release if expired
      if (this.isExpired(existingLock)) {
        this.locks.delete(key);
      } else if (existingLock.agent !== agent) {
        return false; // Locked by another agent
      } else {
        // Same agent, refresh timestamp
        existingLock.timestamp = Date.now();
        return true;
      }
    }

    // Acquire new lock
    this.locks.set(key, {
      agent,
      timestamp: Date.now(),
      objectType,
      objectId,
    });

    return true;
  }

  /**
   * Checkin object (release lock)
   * @returns true if checkin successful, false if not locked or locked by different agent
   */
  checkin(objectType: string, objectId: string, agent: string): boolean {
    const key = this.getLockKey(objectType, objectId);
    const existingLock = this.locks.get(key);

    if (!existingLock) {
      return false; // Not locked
    }

    // Auto-release if expired
    if (this.isExpired(existingLock)) {
      this.locks.delete(key);
      return true;
    }

    // Verify agent owns the lock
    if (existingLock.agent !== agent) {
      return false; // Different agent
    }

    this.locks.delete(key);
    return true;
  }

  /**
   * Check if object is locked
   * @returns Lock info if locked, null if available
   */
  checkLock(objectType: string, objectId: string): Lock | null {
    const key = this.getLockKey(objectType, objectId);
    const existingLock = this.locks.get(key);

    if (!existingLock) {
      return null;
    }

    // Auto-release if expired
    if (this.isExpired(existingLock)) {
      this.locks.delete(key);
      return null;
    }

    return { ...existingLock };
  }

  /**
   * Get all active locks
   */
  getAllLocks(): Lock[] {
    const now = Date.now();
    const activeLocks: Lock[] = [];

    // Clean up expired locks and collect active ones
    for (const [key, lock] of this.locks.entries()) {
      if (this.isExpired(lock)) {
        this.locks.delete(key);
      } else {
        activeLocks.push({ ...lock });
      }
    }

    return activeLocks;
  }

  /**
   * Force release lock (admin operation)
   */
  forceRelease(objectType: string, objectId: string): boolean {
    const key = this.getLockKey(objectType, objectId);
    return this.locks.delete(key);
  }

  /**
   * Get lock statistics
   */
  getStats(): {
    totalLocks: number;
    locksByType: Record<string, number>;
    oldestLockAge: number | null;
  } {
    const activeLocks = this.getAllLocks();
    const locksByType: Record<string, number> = {};
    let oldestTimestamp: number | null = null;

    for (const lock of activeLocks) {
      locksByType[lock.objectType] = (locksByType[lock.objectType] || 0) + 1;
      if (oldestTimestamp === null || lock.timestamp < oldestTimestamp) {
        oldestTimestamp = lock.timestamp;
      }
    }

    return {
      totalLocks: activeLocks.length,
      locksByType,
      oldestLockAge: oldestTimestamp ? Date.now() - oldestTimestamp : null,
    };
  }
}

// Singleton instance
export const lockingService = new LockingService();
