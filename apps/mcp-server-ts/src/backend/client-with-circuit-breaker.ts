/**
 * Backend Client with Circuit Breaker - Phase 2
 *
 * Features:
 * - Circuit breaker on all backend operations
 * - Fallback cache for read operations (GET/LIST)
 * - Request ID propagation
 * - Trace context propagation
 * - Metrics recording (request count, duration, errors)
 * - Type-safe proxy of BackendClient methods
 *
 * Usage:
 * ```typescript
 * import { backendClientWithCircuitBreaker } from "./backend/client-with-circuit-breaker.js";
 *
 * const task = await backendClientWithCircuitBreaker.getTask("task-123");
 * ```
 */

import type CircuitBreaker from "opossum";
import { config } from "../config/index.js";
import type {
  ActionListAttributes,
  ActionListRecord,
  ProjectAttributes,
  ProjectRecord,
  TaskAttributes,
  TaskRecord,
  TaskUpdate,
} from "../core/types.js";
import { createModuleLogger } from "../infrastructure/logger.js";
import { requestContextStore } from "../infrastructure/requestContextStore.js";
import { withSpan } from "../infrastructure/tracing.js";
import {
  circuitBreakerRegistry,
  createEnhancedCircuitBreaker,
} from "../services/circuit-breaker.js";
import { BackendClient } from "./client.js";

const logger = createModuleLogger("backend-client-circuit-breaker");

/**
 * Backend Client with Circuit Breaker and Observability
 *
 * Wraps all BackendClient methods with:
 * - Circuit breaker pattern (fail-fast when backend unhealthy)
 * - Fallback cache for read operations
 * - Request ID propagation
 * - Distributed tracing
 * - Metrics collection
 */
export class BackendClientWithCircuitBreaker {
  private client: BackendClient;
  private circuitBreaker: CircuitBreaker<any, any> | null = null;
  private circuitBreakerEnabled: boolean;

  constructor(baseURL?: string) {
    this.client = new BackendClient(baseURL);
    this.circuitBreakerEnabled = config.CIRCUIT_BREAKER_ENABLED;

    if (this.circuitBreakerEnabled) {
      // Create circuit breaker for backend client
      this.circuitBreaker = createEnhancedCircuitBreaker(
        async (method: string, ...args: any[]) => {
          return await this.executeWithObservability(method, args);
        },
        {
          name: "backend-api",
          timeout: config.BACKEND_TIMEOUT_MS,
          errorThresholdPercentage: config.CIRCUIT_BREAKER_ERROR_THRESHOLD,
          resetTimeout: config.CIRCUIT_BREAKER_RESET_TIMEOUT_MS,
          volumeThreshold: config.CIRCUIT_BREAKER_VOLUME_THRESHOLD,
          enableMetrics: config.ENABLE_METRICS,
          enableFallbackCache: config.FALLBACK_CACHE_ENABLED,
          cacheKeyFn: (method: string, ...args: any[]) => {
            // Only cache read operations
            if (method.startsWith("get") || method.startsWith("list")) {
              return `backend:${method}:${JSON.stringify(args)}`;
            }
            return ""; // Don't cache mutations
          },
        }
      );

      circuitBreakerRegistry.set("backend-api", this.circuitBreaker);
    }

    logger.info(
      {
        circuitBreakerEnabled: this.circuitBreakerEnabled,
        timeout: config.BACKEND_TIMEOUT_MS,
        errorThreshold: config.CIRCUIT_BREAKER_ERROR_THRESHOLD,
        metricsEnabled: config.ENABLE_METRICS,
        cacheEnabled: config.FALLBACK_CACHE_ENABLED,
      },
      "Backend client initialized"
    );
  }

  /**
   * Execute a method, using circuit breaker if enabled, otherwise direct call
   *
   * @private
   */
  private async executeMethod(method: string, ...args: any[]): Promise<any> {
    if (this.circuitBreakerEnabled && this.circuitBreaker) {
      return this.executeMethod(method, ...args);
    }
    // Circuit breaker disabled - call directly with observability
    return this.executeWithObservability(method, args);
  }

  /**
   * Execute method with full observability
   *
   * @private
   */
  private async executeWithObservability(
    method: string,
    args: any[]
  ): Promise<any> {
    return withSpan(`backend.${method}`, async (span) => {
      // Add request context
      const requestId = requestContextStore.getRequestId();
      if (requestId) {
        span.setAttribute("request_id", requestId);
      }

      span.setAttribute("backend.method", method);
      span.setAttribute("backend.args_count", args.length);

      // Execute method on underlying client
      const fn = (this.client as any)[method];
      if (!fn) {
        throw new Error(`Method ${method} not found on BackendClient`);
      }

      const result = await fn.apply(this.client, args);
      span.setStatus({ code: 1 }); // OK
      return result;
    });
  }

  // ========================================================================
  // TASK METHODS
  // ========================================================================

  async createTask(data: TaskAttributes): Promise<TaskRecord> {
    return this.executeMethod("createTask", data);
  }

  async getTask(id: string): Promise<TaskRecord> {
    return this.executeMethod("getTask", id);
  }

  async updateTask(id: string, data: TaskUpdate): Promise<TaskRecord> {
    return this.executeMethod("updateTask", id, data);
  }

  async updateTaskWithMeta(
    id: string,
    updates: Record<string, unknown>,
    options?: { ifMatch?: string }
  ): Promise<TaskRecord> {
    return this.executeMethod("updateTaskWithMeta", id, updates, options);
  }

  async updateTaskStatus(
    id: string,
    status: string,
    metadata?: Record<string, unknown>
  ): Promise<TaskRecord> {
    return this.executeMethod("updateTaskStatus", id, status, metadata);
  }

  async deleteTask(id: string): Promise<void> {
    return this.executeMethod("deleteTask", id);
  }

  async listTasks(params?: Record<string, unknown>): Promise<TaskRecord[]> {
    return this.executeMethod("listTasks", params);
  }

  async assignTask(
    taskId: string,
    assignment: { assignee?: string | null; assignees?: string[] | null }
  ): Promise<TaskRecord> {
    return this.executeMethod("assignTask", taskId, assignment);
  }

  async bulkUpdateTasks(
    taskIds: string[],
    updates: TaskUpdate
  ): Promise<{ success: boolean; updated_count: number; task_ids: string[] }> {
    return this.executeMethod("bulkUpdateTasks", taskIds, updates);
  }

  async assignTasksToSprint(
    taskIds: string[],
    sprintId: string
  ): Promise<{ success: boolean; assigned_count: number; sprint_id: string }> {
    return this.executeMethod("assignTasksToSprint", taskIds, sprintId);
  }

  async searchTasks(params: {
    query: string;
    fields?: Array<
      | "title"
      | "description"
      | "tags"
      | "notes"
      | "summary"
      | "completion_notes"
    >;
    project_id?: string;
    sprint_id?: string;
    skip?: number;
    limit?: number;
  }): Promise<{
    success: boolean;
    query: string;
    count: number;
    data: TaskRecord[];
  }> {
    return this.executeMethod("searchTasks", params);
  }

  // ========================================================================
  // PROJECT METHODS
  // ========================================================================

  async createProject(data: ProjectAttributes): Promise<ProjectRecord> {
    return this.executeMethod("createProject", data);
  }

  async getProject(id: string): Promise<ProjectRecord> {
    return this.executeMethod("getProject", id);
  }

  async updateProject(
    id: string,
    data: Record<string, unknown>
  ): Promise<ProjectRecord> {
    return this.executeMethod("updateProject", id, data);
  }

  async deleteProject(id: string): Promise<void> {
    return this.executeMethod("deleteProject", id);
  }

  async listProjects(
    params?: Record<string, unknown>
  ): Promise<ProjectRecord[]> {
    return this.executeMethod("listProjects", params);
  }

  async listProjectComments(projectId: string): Promise<any[]> {
    return this.executeMethod("listProjectComments", projectId);
  }

  async getProjectMetrics(projectId: string): Promise<any> {
    return this.executeMethod("getProjectMetrics", projectId);
  }

  // ========================================================================
  // ACTION LIST METHODS
  // ========================================================================

  async createActionList(
    data: ActionListAttributes
  ): Promise<ActionListRecord> {
    return this.executeMethod("createActionList", data);
  }

  async getActionList(id: string): Promise<ActionListRecord> {
    return this.executeMethod("getActionList", id);
  }

  async listActionLists(
    params?: Record<string, unknown>
  ): Promise<ActionListRecord[]> {
    return this.executeMethod("listActionLists", params);
  }

  async updateActionList(
    id: string,
    data: Record<string, unknown>
  ): Promise<ActionListRecord> {
    return this.executeMethod("updateActionList", id, data);
  }

  async deleteActionList(id: string): Promise<void> {
    return this.executeMethod("deleteActionList", id);
  }

  async addActionListItem(
    actionListId: string,
    item: { text: string; order?: number }
  ): Promise<ActionListRecord> {
    return this.executeMethod("addActionListItem", actionListId, item);
  }

  async toggleActionListItem(
    actionListId: string,
    itemId: string
  ): Promise<ActionListRecord> {
    return this.executeMethod("toggleActionListItem", actionListId, itemId);
  }

  async removeActionListItem(
    actionListId: string,
    itemId: string
  ): Promise<ActionListRecord> {
    return this.executeMethod("removeActionListItem", actionListId, itemId);
  }

  async reorderActionListItems(
    actionListId: string,
    itemIds: string[]
  ): Promise<ActionListRecord> {
    return this.executeMethod("reorderActionListItems", actionListId, itemIds);
  }

  async bulkDeleteActionLists(
    actionListIds: string[]
  ): Promise<{ success: boolean; deleted_count: number }> {
    return this.executeMethod("bulkDeleteActionLists", actionListIds);
  }

  async bulkUpdateActionLists(
    actionListIds: string[],
    updates: Record<string, unknown>
  ): Promise<{
    success: boolean;
    updated_count: number;
    action_list_ids: string[];
  }> {
    return this.executeMethod("bulkUpdateActionLists", actionListIds, updates);
  }

  async searchActionLists(
    query: string,
    options?: {
      fields?: Array<"title" | "description" | "notes">;
      project_id?: string;
      sprint_id?: string;
      status?: string;
      priority?: string;
      skip?: number;
      limit?: number;
    }
  ): Promise<{
    success: boolean;
    query: string;
    count: number;
    data: ActionListRecord[];
  }> {
    return this.executeMethod("searchActionLists", query, options);
  }

  // ========================================================================
  // PHASE TRACKING METHODS
  // ========================================================================

  /**
   * Get all phases for an entity
   */
  async getPhases(
    entityType: "task" | "sprint" | "project",
    entityId: string
  ): Promise<{
    entity_id: string;
    entity_type: string;
    phases: Record<string, unknown>;
  }> {
    return this.executeMethod("getPhases", entityType, entityId);
  }

  /**
   * Get a specific phase for an entity
   */
  async getPhase(
    entityType: "task" | "sprint" | "project",
    entityId: string,
    phaseName: string
  ): Promise<{
    phase_name: string;
    status: string;
    data: Record<string, unknown>;
  }> {
    return this.executeMethod("getPhase", entityType, entityId, phaseName);
  }

  /**
   * Update a specific phase
   */
  async updatePhase(
    entityType: "task" | "sprint" | "project",
    entityId: string,
    phaseName: string,
    update: {
      status?: string;
      blocked_reason?: string | null;
      skip_reason?: string | null;
      additional_fields?: Record<string, unknown>;
    }
  ): Promise<{
    entity_id: string;
    entity_type: string;
    phases: Record<string, unknown>;
  }> {
    return this.executeMethod("updatePhase", entityType, entityId, phaseName, update);
  }

  /**
   * Advance entity to next phase
   */
  async advancePhase(
    entityType: "task" | "sprint" | "project",
    entityId: string
  ): Promise<{
    entity_id: string;
    entity_type: string;
    phases: Record<string, unknown>;
  }> {
    return this.executeMethod("advancePhase", entityType, entityId);
  }

  /**
   * Start a specific phase
   */
  async startPhase(
    entityType: "task" | "sprint" | "project",
    entityId: string,
    phaseName: string
  ): Promise<{
    entity_id: string;
    entity_type: string;
    phases: Record<string, unknown>;
  }> {
    return this.executeMethod("startPhase", entityType, entityId, phaseName);
  }

  /**
   * Complete a specific phase
   */
  async completePhase(
    entityType: "task" | "sprint" | "project",
    entityId: string,
    phaseName: string
  ): Promise<{
    entity_id: string;
    entity_type: string;
    phases: Record<string, unknown>;
  }> {
    return this.executeMethod("completePhase", entityType, entityId, phaseName);
  }

  /**
   * Block a specific phase
   */
  async blockPhase(
    entityType: "task" | "sprint" | "project",
    entityId: string,
    phaseName: string,
    blockedReason?: string
  ): Promise<{
    entity_id: string;
    entity_type: string;
    phases: Record<string, unknown>;
  }> {
    return this.executeMethod("blockPhase", entityType, entityId, phaseName, blockedReason);
  }

  /**
   * Unblock a specific phase
   */
  async unblockPhase(
    entityType: "task" | "sprint" | "project",
    entityId: string,
    phaseName: string
  ): Promise<{
    entity_id: string;
    entity_type: string;
    phases: Record<string, unknown>;
  }> {
    return this.executeMethod("unblockPhase", entityType, entityId, phaseName);
  }

  /**
   * Skip a specific phase
   */
  async skipPhase(
    entityType: "task" | "sprint" | "project",
    entityId: string,
    phaseName: string,
    skipReason?: string
  ): Promise<{
    entity_id: string;
    entity_type: string;
    phases: Record<string, unknown>;
  }> {
    return this.executeMethod("skipPhase", entityType, entityId, phaseName, skipReason);
  }

  /**
   * Get phase summary for an entity
   */
  async getPhaseSummary(
    entityType: "task" | "sprint" | "project",
    entityId: string
  ): Promise<{
    entity_id: string;
    entity_type: string;
    current_phase: string | null;
    phases_completed: number;
    phases_total: number;
    completion_pct: number;
    phases: Record<string, unknown>;
  }> {
    return this.executeMethod("getPhaseSummary", entityType, entityId);
  }

  /**
   * Get phase analytics for entity type
   */
  async getPhaseAnalytics(
    entityType: "task" | "sprint" | "project",
    limit?: number
  ): Promise<{
    entity_type: string;
    total_entities: number;
    by_phase: Record<string, Record<string, number>>;
    blocked_count: number;
    average_completion_pct: number;
  }> {
    return this.executeMethod("getPhaseAnalytics", entityType, limit);
  }

  // ========================================================================
  // GENERIC CRUD METHODS
  // ========================================================================

  async create<T>(resource: string, data: unknown): Promise<T> {
    return this.executeMethod("create", resource, data);
  }

  async update<T>(resource: string, id: string, data: unknown): Promise<T> {
    return this.executeMethod("update", resource, id, data);
  }

  async delete(resource: string, id: string): Promise<void> {
    return this.executeMethod("delete", resource, id);
  }

  async list<T>(
    resource: string,
    params?: Record<string, unknown>
  ): Promise<T[]> {
    return this.executeMethod("list", resource, params);
  }

  // ========================================================================
  // HEALTH CHECK (bypass circuit breaker)
  // ========================================================================

  async health(): Promise<{ status: string; timestamp: string }> {
    // Health check bypasses circuit breaker to get true backend status
    return this.client.health();
  }

  // ========================================================================
  // CIRCUIT BREAKER UTILITIES
  // ========================================================================

  /**
   * Get circuit breaker statistics
   */
  getCircuitBreakerStats() {
    if (!this.circuitBreaker) {
      return {
        state: "disabled",
        totalRequests: 0,
        successfulRequests: 0,
        failedRequests: 0,
        timeouts: 0,
        rejectedRequests: 0,
        errorPercentage: 0,
        averageResponseTime: 0,
      };
    }
    const stats = this.circuitBreaker.stats;
    return {
      state: this.circuitBreaker.opened
        ? "open"
        : this.circuitBreaker.halfOpen
        ? "halfOpen"
        : "closed",
      totalRequests: stats.fires,
      successfulRequests: stats.successes,
      failedRequests: stats.failures,
      timeouts: stats.timeouts,
      rejectedRequests: stats.rejects,
      errorPercentage:
        stats.fires > 0 ? (stats.failures / stats.fires) * 100 : 0,
      averageResponseTime: stats.latencyMean,
    };
  }

  /**
   * Check if circuit breaker is healthy
   */
  isHealthy(): boolean {
    if (!this.circuitBreaker) {
      return true; // If disabled, always healthy
    }
    return !this.circuitBreaker.opened && !this.circuitBreaker.halfOpen;
  }

  /**
   * Force circuit breaker to close (for testing/emergency recovery)
   */
  forceClose(): void {
    if (!this.circuitBreaker) {
      return; // Nothing to close if disabled
    }
    if (this.circuitBreaker.opened || this.circuitBreaker.halfOpen) {
      this.circuitBreaker.close();
      logger.warn("Circuit breaker force-closed");
    }
  }

  /**
   * Get the underlying client (for direct access if needed)
   */
  getUnderlyingClient(): BackendClient {
    return this.client;
  }
}

/**
 * Singleton instance of backend client with circuit breaker
 *
 * Use this throughout the application for all backend API calls.
 */
export const backendClientWithCircuitBreaker = new BackendClientWithCircuitBreaker();

// Log initialization
logger.info("Backend client with circuit breaker ready");
