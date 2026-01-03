/**
 * Session Manager - Phase 1.5
 *
 * Manages MCP session state
 */

import { logger } from "./logger.js";

export interface SessionState {
  id: string;
  createdAt: Date;
  lastAccessedAt: Date;
  data: Map<string, unknown>;
}

export class SessionManager {
  private sessions = new Map<string, SessionState>();
  private readonly sessionTimeoutMs: number;
  private cleanupInterval: NodeJS.Timeout | null = null;

  constructor(sessionTimeoutMs: number = 3600000) {
    // Default: 1 hour
    this.sessionTimeoutMs = sessionTimeoutMs;
  }

  /**
   * Get or create a session
   */
  getOrCreate(sessionId: string): SessionState {
    let session = this.sessions.get(sessionId);

    if (!session) {
      session = {
        id: sessionId,
        createdAt: new Date(),
        lastAccessedAt: new Date(),
        data: new Map(),
      };
      this.sessions.set(sessionId, session);
      logger.debug({ sessionId }, "Session created");
    } else {
      session.lastAccessedAt = new Date();
    }

    return session;
  }

  /**
   * Get session data
   */
  get<T>(sessionId: string, key: string): T | undefined {
    const session = this.sessions.get(sessionId);
    return session?.data.get(key) as T | undefined;
  }

  /**
   * Set session data
   */
  set(sessionId: string, key: string, value: unknown): void {
    const session = this.getOrCreate(sessionId);
    session.data.set(key, value);
  }

  /**
   * Delete session data key
   */
  delete(sessionId: string, key: string): void {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.data.delete(key);
    }
  }

  /**
   * Cleanup expired sessions
   */
  cleanup(sessionId: string): void {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.data.clear();
      this.sessions.delete(sessionId);
      logger.debug({ sessionId }, "Session cleaned up");
    }
  }

  /**
   * Start automatic cleanup of expired sessions
   */
  startCleanup(intervalMs: number = 300000): void {
    // Default: 5 minutes
    if (this.cleanupInterval) {
      return;
    }

    this.cleanupInterval = setInterval(() => {
      const now = Date.now();
      let cleanedCount = 0;

      for (const [sessionId, session] of this.sessions.entries()) {
        const age = now - session.lastAccessedAt.getTime();
        if (age > this.sessionTimeoutMs) {
          this.cleanup(sessionId);
          cleanedCount++;
        }
      }

      if (cleanedCount > 0) {
        logger.info({ cleanedCount }, "Expired sessions cleaned up");
      }
    }, intervalMs);

    logger.info({ intervalMs }, "Session cleanup started");
  }

  /**
   * Stop automatic cleanup
   */
  stopCleanup(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
      logger.info("Session cleanup stopped");
    }
  }

  /**
   * Get all active session IDs
   */
  getActiveSessions(): string[] {
    return Array.from(this.sessions.keys());
  }

  /**
   * Get session count
   */
  getSessionCount(): number {
    return this.sessions.size;
  }
}

// Singleton instance
export const sessionManager = new SessionManager();
