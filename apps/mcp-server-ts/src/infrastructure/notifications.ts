/**
 * Notifications Service - EventEmitter for system events
 *
 * Features:
 * - Type-safe event emission and subscription
 * - Support for task updates, lock changes, health alerts
 * - Async event handlers with error isolation
 */

import { EventEmitter } from "events";

export type NotificationEvent =
  | { type: "task:created"; taskId: string; projectId: string }
  | { type: "task:updated"; taskId: string; changes: string[] }
  | { type: "task:deleted"; taskId: string }
  | { type: "lock:acquired"; objectType: string; objectId: string; agent: string }
  | { type: "lock:released"; objectType: string; objectId: string; agent: string }
  | { type: "lock:expired"; objectType: string; objectId: string }
  | { type: "health:degraded"; service: string; reason: string }
  | { type: "health:recovered"; service: string };

type NotificationHandler = (event: NotificationEvent) => void | Promise<void>;

class NotificationService {
  private emitter = new EventEmitter();
  private handlers = new Map<string, Set<NotificationHandler>>();

  /**
   * Subscribe to specific event type
   */
  on(eventType: NotificationEvent["type"], handler: NotificationHandler): void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set());
    }
    this.handlers.get(eventType)!.add(handler);
  }

  /**
   * Unsubscribe from event type
   */
  off(eventType: NotificationEvent["type"], handler: NotificationHandler): void {
    const handlers = this.handlers.get(eventType);
    if (handlers) {
      handlers.delete(handler);
    }
  }

  /**
   * Emit notification event
   */
  async emit(event: NotificationEvent): Promise<void> {
    const handlers = this.handlers.get(event.type);
    if (!handlers || handlers.size === 0) {
      return;
    }

    // Execute handlers in parallel with error isolation
    const results = await Promise.allSettled(
      Array.from(handlers).map((handler) => handler(event))
    );

    // Log any handler errors
    results.forEach((result, index) => {
      if (result.status === "rejected") {
        console.error(
          `[Notification] Handler error for ${event.type}:`,
          result.reason
        );
      }
    });
  }

  /**
   * Get subscription statistics
   */
  getStats(): {
    totalHandlers: number;
    handlersByType: Record<string, number>;
  } {
    const handlersByType: Record<string, number> = {};
    let totalHandlers = 0;

    for (const [type, handlers] of this.handlers.entries()) {
      handlersByType[type] = handlers.size;
      totalHandlers += handlers.size;
    }

    return { totalHandlers, handlersByType };
  }

  /**
   * Clear all handlers (use with caution)
   */
  clear(): void {
    this.handlers.clear();
    this.emitter.removeAllListeners();
  }
}

// Singleton instance
export const notificationService = new NotificationService();
