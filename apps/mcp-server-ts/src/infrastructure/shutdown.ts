/**
 * Shutdown Service - Graceful resource cleanup
 *
 * Features:
 * - Registers cleanup handlers for all resources
 * - Executes shutdowns in reverse registration order
 * - Timeout protection (30 second max)
 * - Idempotent (safe to call multiple times)
 *
 * Usage:
 * ```typescript
 * shutdownService.registerResource("database", async () => {
 *   await db.close();
 * });
 * ```
 */

type CleanupHandler = () => Promise<void> | void;

interface ShutdownStats {
  resourceCount: number;
  resources: string[];
  startTime: Date;
  endTime?: Date;
  durationMs?: number;
  errors: Array<{ resource: string; error: string }>;
}

class ShutdownService {
  private resources = new Map<string, CleanupHandler>();
  private isShuttingDown = false;
  private shutdownPromise: Promise<void> | null = null;
  private readonly SHUTDOWN_TIMEOUT_MS = 30000; // 30 seconds
  private stats: ShutdownStats | null = null;

  /**
   * Register a resource for cleanup on shutdown
   */
  registerResource(name: string, cleanup: CleanupHandler): void {
    if (this.isShuttingDown) {
      // CRITICAL: Use stderr to avoid corrupting STDIO transport
      console.error(`[Shutdown] Cannot register resource during shutdown: ${name}`);
      return;
    }

    this.resources.set(name, cleanup);
    // CRITICAL: Use stderr to avoid corrupting STDIO transport
    console.error(`[Shutdown] Registered resource: ${name}`);
  }

  /**
   * Unregister a resource (useful for testing)
   */
  unregisterResource(name: string): boolean {
    if (this.isShuttingDown) {
      // CRITICAL: Use stderr to avoid corrupting STDIO transport
      console.error(`[Shutdown] Cannot unregister resource during shutdown: ${name}`);
      return false;
    }

    return this.resources.delete(name);
  }

  /**
   * Gracefully shutdown all registered resources
   * This method is idempotent - calling it multiple times returns the same promise
   */
  async shutdown(): Promise<void> {
    // Idempotency: return existing shutdown promise if already shutting down
    if (this.shutdownPromise) {
      return this.shutdownPromise;
    }

    this.isShuttingDown = true;
    this.shutdownPromise = this.executeShutdown();
    return this.shutdownPromise;
  }

  private async executeShutdown(): Promise<void> {
    this.stats = {
      resourceCount: this.resources.size,
      resources: Array.from(this.resources.keys()),
      startTime: new Date(),
      errors: [],
    };

    // CRITICAL: Use stderr to avoid corrupting STDIO transport
    console.error(`[Shutdown] Initiating graceful shutdown`, {
      resourceCount: this.stats.resourceCount,
      resources: this.stats.resources,
    });

    const timeoutPromise = new Promise<void>((resolve) => {
      setTimeout(() => {
        console.error(`[Shutdown] Timeout exceeded (${this.SHUTDOWN_TIMEOUT_MS}ms)`);
        resolve();
      }, this.SHUTDOWN_TIMEOUT_MS);
    });

    const cleanupPromise = this.cleanupResources();

    // Race between timeout and cleanup
    await Promise.race([cleanupPromise, timeoutPromise]);

    if (this.stats) {
      this.stats.endTime = new Date();
      this.stats.durationMs = this.stats.endTime.getTime() - this.stats.startTime.getTime();

      console.error(`[Shutdown] Shutdown complete`, {
        durationMs: this.stats.durationMs,
        errorCount: this.stats.errors.length,
        errors: this.stats.errors,
      });
    }
  }

  private async cleanupResources(): Promise<void> {
    // Shutdown in reverse registration order (LIFO)
    const entries = Array.from(this.resources.entries()).reverse();

    for (const [name, cleanup] of entries) {
      try {
        console.error(`[Shutdown] Cleaning up resource: ${name}`);
        const start = Date.now();

        await cleanup();

        const duration = Date.now() - start;
        console.error(`[Shutdown] Successfully cleaned up: ${name} (${duration}ms)`);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        console.error(`[Shutdown] Error cleaning up resource: ${name}`, {
          error: errorMessage,
          stack: error instanceof Error ? error.stack : undefined,
        });

        if (this.stats) {
          this.stats.errors.push({
            resource: name,
            error: errorMessage,
          });
        }

        // Continue cleanup despite errors
      }
    }
  }

  /**
   * Check if shutdown is in progress
   */
  isShutdownInProgress(): boolean {
    return this.isShuttingDown;
  }

  /**
   * Get shutdown statistics (for monitoring/debugging)
   */
  getStats(): ShutdownStats | null {
    return this.stats;
  }

  /**
   * Get list of registered resources
   */
  getRegisteredResources(): string[] {
    return Array.from(this.resources.keys());
  }

  /**
   * Reset service (primarily for testing)
   */
  reset(): void {
    if (this.isShuttingDown) {
      // CRITICAL: Use stderr to avoid corrupting STDIO transport
      console.error("[Shutdown] Cannot reset during shutdown");
      return;
    }

    this.resources.clear();
    this.shutdownPromise = null;
    this.stats = null;
  }
}

// Singleton instance
export const shutdownService = new ShutdownService();
