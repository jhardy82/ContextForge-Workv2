/**
 * BackendClient - Type-safe HTTP client for TaskMan v2 REST API
 *
 * Features:
 * - Exponential backoff retry for transient errors (429, 500, 503)
 * - Request/response interceptors for structured logging
 * - Generic CRUD methods with type safety
 * - Audit log integration
 *
 * Research Authority:
 * - Axios documentation: https://github.com/axios/axios-docs
 * - Microsoft TypeScript patterns: Azure SDK error handling
 * - Retry patterns: Azure Functions fixed-delay strategy
 */

import axios, {
  AxiosError,
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
} from "axios";
import { randomUUID } from "node:crypto";
import http from "node:http";
import https from "node:https";
import {
  actionListRecordSchema,
  projectAnalyticsSchema,
} from "../core/schemas.js";
import {
  ActionListAttributes,
  ActionListPriority,
  ActionListRecord,
  ActionListStatus,
  ConcurrencyMeta,
  ProjectAnalytics,
  ProjectAttributes,
  ProjectRecord,
  Severity,
  TaskAttributes,
  TaskMutationResult,
  TaskRecord,
  TaskStatus,
  TaskTelemetry,
  TaskUpdate,
  TelemetryOutcome,
} from "../core/types.js";
import { auditLog } from "../infrastructure/audit.js";
export interface ProjectCommentInput {
  message: string;
  author?: string;
  tags?: string[];
}

export interface ProjectBlockerInput {
  title: string;
  description?: string;
  severity?: Severity;
  linked_task_id?: string;
  external_reference?: string;
}

export interface ProjectMetaTaskInput {
  title: string;
  description?: string;
  owner?: string;
  due_date?: string;
}

export interface TaskBulkUpdateResult {
  [x: string]: unknown; // Index signature for SDK CallToolResult compatibility
  success: boolean;
  updated_count: number;
  task_ids: string[];
}

export interface TaskBulkAssignSprintResult {
  [x: string]: unknown; // Index signature for SDK CallToolResult compatibility
  success: boolean;
  assigned_count: number;
  sprint_id: string;
}

export interface TaskSearchParams {
  query: string;
  fields?: Array<
    "title" | "description" | "tags" | "notes" | "summary" | "completion_notes"
  >;
  project_id?: string;
  sprint_id?: string;
  skip?: number;
  limit?: number;
}

export interface TaskSearchResult {
  success: boolean;
  query: string;
  count: number;
  data: TaskRecord[];
}

/**
 * Backend API response envelope
 * - Backend returns: { success: boolean, data: T } or { success: false, error: string }
 */
interface ApiEnvelope<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

/**
 * Retry configuration for transient errors
 */
interface RetryConfig {
  maxAttempts: number;
  delays: number[]; // Milliseconds for each retry attempt
  retryableStatuses: number[]; // HTTP status codes to retry
}

const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxAttempts: 3,
  delays: [1000, 2000, 4000], // Exponential: 1s, 2s, 4s
  retryableStatuses: [429, 500, 503], // Rate limit, server error, unavailable
};

const HEADER_CONCURRENCY_TOKEN = "x-concurrency-token";
const HEADER_VERSION = "x-task-version";
const HEADER_ETAG = "etag";
const HEADER_LAST_MODIFIED = "last-modified";
const HEADER_UPDATED_BY = "x-updated-by";
const HEADER_REQUEST_ID = "x-request-id";
const HEADER_CORRELATION_ID = "x-correlation-id";

export interface TaskMutationOptions {
  concurrencyToken?: string | null;
  telemetryTool?: string;
}

export class TaskMutationError extends Error {
  readonly status?: number;
  readonly telemetry?: TaskTelemetry;
  readonly concurrency?: ConcurrencyMeta | null;
  readonly data?: unknown;

  constructor(
    message: string,
    options: {
      status?: number;
      telemetry?: TaskTelemetry;
      concurrency?: ConcurrencyMeta | null;
      data?: unknown;
      cause?: unknown;
    } = {}
  ) {
    super(message);
    this.name = "TaskMutationError";
    this.status = options.status;
    this.telemetry = options.telemetry;
    this.concurrency = options.concurrency;
    this.data = options.data;
    if (options.cause !== undefined) {
      (this as Error & { cause?: unknown }).cause = options.cause;
    }
  }
}

/**
 * Generic boundary-layer mapping for ALL resources
 * Backend API universally expects 'name' field, while MCP domain types use 'title'
 */

/**
 * Transform domain object (with 'title') to API DTO (with 'name')
 * Works for any resource: Project, Task, Sprint, ActionList
 */
function toApiDto<T extends Record<string, any>>(
  domain: T | Partial<T>
): Omit<T, "title"> & { name?: string } {
  const { title, ...rest } = domain as any;
  return {
    ...(title !== undefined && { name: title }),
    ...rest,
  } as any;
}

/**
 * Transform API DTO (with 'name') to domain object (with 'title')
 * Works for any resource: Project, Task, Sprint, ActionList
 */
function fromApiDto<T>(api: any): T {
  const { name, ...rest } = api;
  return {
    title: name,
    ...rest,
  } as T;
}

/**
 * Unwrap backend response - handles direct, enveloped, or paginated responses
 */
function unwrapResponse<T>(response: AxiosResponse): T {
  const body = response.data;

  // Case 1: Empty response (204 No Content)
  if (response.status === 204 || !body) {
    return undefined as T;
  }

  // Case 2: Envelope structure detected (legacy support)
  if (
    typeof body === "object" &&
    body !== null &&
    "success" in body &&
    "data" in body
  ) {
    if (body.success && body.data !== undefined) {
      return body.data as T;
    }
    throw new Error(body.error || body.message || "Operation failed");
  }

  // Case 3: Direct response (default for FastAPI Pydantic models)
  return body as T;
}

/**
 * Unwrap paginated list response - extracts array from pagination wrapper
 */
function unwrapListResponse<T>(
  response: AxiosResponse,
  resourceKey: string
): T[] {
  const body = response.data;

  // Case 1: Paginated wrapper (FastAPI default)
  if (body && typeof body === "object" && resourceKey in body) {
    return body[resourceKey] as T[];
  }

  // Case 2: Envelope with array data (legacy)
  if (body && typeof body === "object" && "success" in body && "data" in body) {
    if (body.success && Array.isArray(body.data)) {
      return body.data as T[];
    }
    throw new Error(body.error || body.message || "List operation failed");
  }

  // Case 3: Direct array (fallback)
  if (Array.isArray(body)) {
    return body as T[];
  }

  throw new Error(
    `Unexpected list response shape for ${resourceKey}: ${JSON.stringify(body)}`
  );
}

/**
 * Type-safe backend client with retry logic and audit logging
 */
export class BackendClient {
  private readonly client: AxiosInstance;
  private readonly retryConfig: RetryConfig;
  private readonly baseURL: string;
  private readonly debugEnabled: boolean;

  constructor(
    baseURL: string = process.env.TASK_MANAGER_API_ENDPOINT ||
      "http://localhost:3001/api/v1"
  ) {
    this.baseURL = baseURL;
    this.retryConfig = DEFAULT_RETRY_CONFIG;
    this.debugEnabled = process.env.TASKMAN_DEBUG === "true";

    // Connection pooling configuration (Phase 1.3)
    const httpAgent = new http.Agent({
      keepAlive: true,
      maxSockets: 10,
      maxFreeSockets: 5,
      timeout: 60000,
      keepAliveMsecs: 30000,
    });

    const httpsAgent = new https.Agent({
      keepAlive: true,
      maxSockets: 10,
      maxFreeSockets: 5,
      timeout: 60000,
      keepAliveMsecs: 30000,
    });

    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000, // 30 seconds
      headers: {
        "Content-Type": "application/json",
      },
      httpAgent,
      httpsAgent,
    });

    this.setupInterceptors();
  }

  /**
   * Conditional debug logging - only logs when TASKMAN_DEBUG=true
   */
  private debugLog(context: string, data: Record<string, unknown>): void {
    // CRITICAL: Use stderr to avoid corrupting STDIO transport
    if (this.debugEnabled) {
      console.error(`[DEBUG] ${context}:`, data);
    }
  }

  /**
   * Setup request/response interceptors for logging and error handling
   */
  private setupInterceptors(): void {
    // Request interceptor: Log outgoing requests
    this.client.interceptors.request.use(
      (config) => {
        // Temporary debug logging
        // CRITICAL: Use stderr to avoid corrupting STDIO transport
        if (this.debugEnabled || process.env.TASKMAN_DEBUG === "true") {
          console.error("[BackendClient] HTTP Request:", {
            method: config.method?.toUpperCase(),
            baseURL: config.baseURL,
            url: config.url,
            fullURL: `${config.baseURL}${config.url}`,
            data: config.data,
          });
        }

        auditLog({
          operation: "http_request",
          agent: "BackendClient",
          result: "initiated",
          details: {
            method: config.method?.toUpperCase(),
            url: config.url,
            timestamp: new Date().toISOString(),
          },
        });
        return config;
      },
      (error) => {
        auditLog({
          operation: "http_request",
          agent: "BackendClient",
          result: "error",
          details: {
            error: error.message,
            timestamp: new Date().toISOString(),
          },
        });
        return Promise.reject(error);
      }
    );

    // Response interceptor: Log responses and handle errors
    this.client.interceptors.response.use(
      (response) => {
        auditLog({
          operation: "http_response",
          agent: "BackendClient",
          result: "success",
          details: {
            status: response.status,
            url: response.config.url,
            timestamp: new Date().toISOString(),
          },
        });
        return response;
      },
      (error) => {
        auditLog({
          operation: "http_response",
          agent: "BackendClient",
          result: "error",
          details: {
            status: error.response?.status,
            message: error.message,
            url: error.config?.url,
            timestamp: new Date().toISOString(),
          },
        });
        return Promise.reject(error);
      }
    );
  }

  /**
   * Execute HTTP request with exponential backoff retry
   */
  private async requestWithRetry<T>(
    config: AxiosRequestConfig,
    attempt: number = 0,
    metrics?: { retries: number }
  ): Promise<AxiosResponse<ApiEnvelope<T>>> {
    try {
      const response = await this.client.request<ApiEnvelope<T>>(config);
      if (metrics) {
        metrics.retries = attempt;
      }
      return response;
    } catch (error) {
      const axiosError = error as AxiosError;
      const status = axiosError.response?.status;

      // Check if error is retryable
      const isRetryable =
        status !== undefined &&
        this.retryConfig.retryableStatuses.includes(status);
      const canRetry = attempt < this.retryConfig.maxAttempts - 1;

      if (isRetryable && canRetry) {
        const delay = this.retryConfig.delays[attempt];

        auditLog({
          operation: "http_retry",
          agent: "BackendClient",
          result: "scheduled",
          details: {
            attempt: attempt + 1,
            maxAttempts: this.retryConfig.maxAttempts,
            delayMs: delay,
            status,
            url: config.url,
          },
        });

        // Wait for exponential backoff delay
        await new Promise((resolve) => setTimeout(resolve, delay));

        // Retry request
        return this.requestWithRetry<T>(config, attempt + 1, metrics);
      }

      // Not retryable or max attempts reached
      if (metrics) {
        metrics.retries = attempt;
      }
      throw error;
    }
  }

  /**
   * Generic CREATE operation
   * POST /{resource}
   */
  async create<T>(resource: string, data: unknown): Promise<T> {
    const response = await this.requestWithRetry<T>({
      method: "POST",
      url: `/${resource}`,
      data,
    });

    return unwrapResponse<T>(response);
  }

  /**
   * Generic READ operation
   * GET /{resource}/{id}
   */
  async read<T>(resource: string, id: string): Promise<T> {
    const response = await this.requestWithRetry<T>({
      method: "GET",
      url: `/${resource}/${id}`,
    });

    return unwrapResponse<T>(response);
  }

  /**
   * Generic UPDATE operation
   * PUT /{resource}/{id}
   */
  async update<T>(resource: string, id: string, data: unknown): Promise<T> {
    const response = await this.requestWithRetry<T>({
      method: "PUT",
      url: `/${resource}/${id}`,
      data,
    });

    return unwrapResponse<T>(response);
  }

  /**
   * Generic DELETE operation
   * DELETE /{resource}/{id}
   */
  async delete(resource: string, id: string): Promise<void> {
    const response = await this.requestWithRetry<void>({
      method: "DELETE",
      url: `/${resource}/${id}`,
    });

    // 204 No Content returns undefined
    if (response.status === 204) {
      return;
    }

    // Check for error in envelope if present
    const body = response.data as any;
    if (
      body &&
      typeof body === "object" &&
      "success" in body &&
      !body.success
    ) {
      throw new Error(body.error || body.message || "Delete operation failed");
    }
  }

  /**
   * Generic LIST operation
   * GET /{resource}?filter=value
   */
  async list<T>(
    resource: string,
    params?: Record<string, unknown>
  ): Promise<T[]> {
    const response = await this.requestWithRetry<T[]>({
      method: "GET",
      url: `/${resource}`,
      params,
    });

    // Determine pagination key from resource name
    const resourceKey = resource; // e.g., "tasks", "projects", "action-lists"
    return unwrapListResponse<T>(response, resourceKey);
  }

  /**
   * Health check endpoint
   * GET /health
   */
  async health(): Promise<{ status: string; timestamp: string }> {
    const response = await this.client.get("/health");
    return response.data;
  }

  // #region Task helpers

  async createTask(data: TaskAttributes): Promise<TaskRecord> {
    return this.create<TaskRecord>("tasks", data);
  }

  async getTask(id: string): Promise<TaskRecord> {
    return this.read<TaskRecord>("tasks", id);
  }

  async updateTask(id: string, data: TaskUpdate): Promise<TaskRecord> {
    const result = await this.updateTaskWithMeta(id, data);
    return result.task;
  }

  async updateTaskWithMeta(
    id: string,
    data: TaskUpdate,
    options: TaskMutationOptions = {}
  ): Promise<TaskMutationResult> {
    const headers: Record<string, string> = {};

    if (options.concurrencyToken) {
      headers["if-match"] = options.concurrencyToken;
      headers[HEADER_CONCURRENCY_TOKEN] = options.concurrencyToken;
    }

    const startedAt = new Date();
    const metrics = { retries: 0 };
    const telemetryTool = options.telemetryTool ?? "backend:updateTask";

    try {
      const response = await this.requestWithRetry<TaskRecord>(
        {
          method: "PUT",
          url: `/tasks/${id}`,
          data,
          headers: Object.keys(headers).length ? headers : undefined,
        },
        0,
        metrics
      );

      if (!response.data.success || !response.data.data) {
        throw new Error(
          response.data.error ||
            response.data.message ||
            "Update operation failed"
        );
      }

      const finishedAt = new Date();
      const record = response.data.data;

      return {
        task: record,
        concurrency: this.extractConcurrencyMeta(response, record),
        telemetry: this.buildTelemetry({
          toolName: telemetryTool,
          taskId: id,
          startedAt,
          finishedAt,
          outcome: "success",
          status: response.status,
          requestId:
            this.getHeader(response.headers, HEADER_REQUEST_ID) ?? null,
          correlationId:
            this.getHeader(response.headers, HEADER_CORRELATION_ID) ?? null,
          retries: metrics.retries,
        }),
        comments: null,
        blockers: null,
        checklist: null,
        hours: null,
      };
    } catch (error) {
      throw this.createTaskMutationError({
        error,
        fallbackTool: telemetryTool,
        taskId: id,
        startedAt,
        retries: metrics.retries,
      });
    }
  }

  async updateTaskStatus(
    taskId: string,
    status: TaskStatus
  ): Promise<TaskRecord> {
    return this.updateTask(taskId, { status });
  }

  async assignTask(
    taskId: string,
    assignment: { assignee?: string | null; assignees?: string[] | null }
  ): Promise<TaskRecord> {
    const payload: TaskUpdate = {};

    if (assignment.assignee !== undefined) {
      payload.assignee = assignment.assignee;
    }

    if (assignment.assignees !== undefined) {
      payload.assignees = assignment.assignees;
    }

    if (Object.keys(payload).length === 0) {
      throw new Error("At least one assignment field must be provided.");
    }

    return this.updateTask(taskId, payload);
  }

  async deleteTask(id: string): Promise<void> {
    return this.delete("tasks", id);
  }

  async listTasks(params?: Record<string, unknown>): Promise<TaskRecord[]> {
    return this.list<TaskRecord>("tasks", params);
  }

  async bulkUpdateTasks(
    taskIds: string[],
    updates: TaskUpdate
  ): Promise<TaskBulkUpdateResult> {
    const response = await this.requestWithRetry<TaskBulkUpdateResult>({
      method: "POST",
      url: "/tasks/bulk/update",
      data: {
        task_ids: taskIds,
        updates,
      },
    });

    const payload = response.data as ApiEnvelope<TaskBulkUpdateResult> &
      TaskBulkUpdateResult;

    if (payload.success) {
      return {
        success: true,
        updated_count:
          payload.updated_count ?? payload.data?.updated_count ?? 0,
        task_ids: payload.task_ids ?? payload.data?.task_ids ?? [],
      };
    }

    throw new Error(
      payload.error || payload.message || "Bulk update operation failed"
    );
  }

  async assignTasksToSprint(
    taskIds: string[],
    sprintId: string
  ): Promise<TaskBulkAssignSprintResult> {
    const response = await this.requestWithRetry<TaskBulkAssignSprintResult>({
      method: "POST",
      url: "/tasks/bulk/assign-sprint",
      data: {
        task_ids: taskIds,
        sprint_id: sprintId,
      },
    });

    const payload = response.data as ApiEnvelope<TaskBulkAssignSprintResult> &
      TaskBulkAssignSprintResult;

    if (payload.success) {
      return {
        success: true,
        assigned_count:
          payload.assigned_count ?? payload.data?.assigned_count ?? 0,
        sprint_id: payload.sprint_id ?? payload.data?.sprint_id ?? sprintId,
      };
    }

    throw new Error(
      payload.error || payload.message || "Bulk sprint assignment failed"
    );
  }

  async searchTasks(params: TaskSearchParams): Promise<TaskSearchResult> {
    const response = await this.requestWithRetry<TaskRecord[]>({
      method: "GET",
      url: "/tasks/tasks-search",
      params: {
        q: params.query,
        fields: params.fields,
        project_id: params.project_id,
        sprint_id: params.sprint_id,
        skip: params.skip,
        limit: params.limit,
      },
    });

    const payload = response.data as ApiEnvelope<TaskRecord[]> &
      TaskSearchResult;

    if (payload.success && payload.data) {
      return {
        success: true,
        query: payload.query ?? params.query,
        count: payload.count ?? payload.data.length,
        data: payload.data,
      };
    }

    throw new Error(payload.error || payload.message || "Task search failed");
  }

  private getHeader(
    headers: AxiosResponse["headers"] | undefined,
    name: string
  ): string | undefined {
    if (!headers) {
      return undefined;
    }

    const normalized = name.toLowerCase();
    const values = headers as Record<string, string | string[] | undefined>;
    const candidate = values[normalized] ?? values[name];

    if (Array.isArray(candidate)) {
      return candidate[0];
    }

    return candidate;
  }

  private extractConcurrencyMeta<T>(
    response: AxiosResponse<ApiEnvelope<T>>,
    fallback?: { updated_at?: string | null; updated_by?: string | null }
  ): ConcurrencyMeta | null {
    const token = this.getHeader(response.headers, HEADER_CONCURRENCY_TOKEN);
    const etag = this.getHeader(response.headers, HEADER_ETAG) ?? null;
    const version = this.getHeader(response.headers, HEADER_VERSION) ?? null;
    const updatedAt =
      this.getHeader(response.headers, HEADER_LAST_MODIFIED) ??
      fallback?.updated_at ??
      null;
    const updatedBy =
      this.getHeader(response.headers, HEADER_UPDATED_BY) ??
      fallback?.updated_by ??
      null;

    if (!token && !etag && !version && !updatedAt && !updatedBy) {
      return null;
    }

    return {
      token: token ?? etag ?? null,
      etag,
      version,
      updated_at: updatedAt,
      updated_by: updatedBy,
    };
  }

  private buildTelemetry(params: {
    toolName: string;
    taskId: string;
    startedAt: Date;
    finishedAt: Date;
    outcome: TelemetryOutcome;
    status: number;
    requestId?: string | null;
    correlationId?: string | null;
    retries: number;
    errorCode?: string | null;
  }): TaskTelemetry {
    const latencyMs =
      params.finishedAt.getTime() - params.startedAt.getTime() >= 0
        ? params.finishedAt.getTime() - params.startedAt.getTime()
        : 0;

    return {
      operation_id: randomUUID(),
      tool_name: params.toolName,
      task_id: params.taskId,
      started_at: params.startedAt.toISOString(),
      finished_at: params.finishedAt.toISOString(),
      latency_ms: latencyMs,
      status_code: params.status > 0 ? params.status : null,
      outcome: params.outcome,
      request_id: params.requestId ?? null,
      correlation_id: params.correlationId ?? null,
      error_code: params.errorCode ?? null,
      retries: Number.isFinite(params.retries) ? params.retries : null,
    };
  }

  private resolveErrorCode(
    error: AxiosError<ApiEnvelope<unknown>>
  ): string | null {
    const responseData = error.response?.data;
    if (!responseData) {
      return null;
    }

    if (typeof responseData.error === "string" && responseData.error.length) {
      return responseData.error;
    }

    if (
      typeof (responseData as unknown as Record<string, unknown>).code ===
        "string" &&
      ((responseData as unknown as Record<string, unknown>).code as string)
        .length > 0
    ) {
      return (responseData as unknown as Record<string, unknown>)
        .code as string;
    }

    return null;
  }

  private createTaskMutationError(params: {
    error: unknown;
    fallbackTool: string;
    taskId: string;
    startedAt: Date;
    retries: number;
  }): TaskMutationError {
    const finishedAt = new Date();
    const axiosError = params.error as AxiosError<ApiEnvelope<unknown>>;
    const response = axiosError.response;
    const status = response?.status ?? 0;
    const outcome: TelemetryOutcome =
      status === 409 || status === 412 ? "conflict" : "error";
    const telemetry = this.buildTelemetry({
      toolName: params.fallbackTool,
      taskId: params.taskId,
      startedAt: params.startedAt,
      finishedAt,
      outcome,
      status,
      requestId: this.getHeader(response?.headers, HEADER_REQUEST_ID) ?? null,
      correlationId:
        this.getHeader(response?.headers, HEADER_CORRELATION_ID) ?? null,
      retries: params.retries,
      errorCode: this.resolveErrorCode(axiosError),
    });

    const concurrency = response ? this.extractConcurrencyMeta(response) : null;

    return new TaskMutationError(axiosError.message || "Task mutation failed", {
      status,
      telemetry,
      concurrency,
      data: response?.data,
      cause: axiosError,
    });
  }

  // #endregion Task helpers

  // #region Project helpers

  async createProject(data: ProjectAttributes): Promise<ProjectRecord> {
    const response = await this.requestWithRetry<ProjectRecord>({
      method: "POST",
      url: "/projects",
      data: data,
    });

    return unwrapResponse<ProjectRecord>(response);
  }

  async getProject(id: string): Promise<ProjectRecord> {
    const response = await this.requestWithRetry<ProjectRecord>({
      method: "GET",
      url: `/projects/${id}`,
    });

    return unwrapResponse<ProjectRecord>(response);
  }

  async updateProject(
    id: string,
    data: Partial<ProjectAttributes>
  ): Promise<ProjectRecord> {
    const response = await this.requestWithRetry<ProjectRecord>({
      method: "PUT",
      url: `/projects/${id}`,
      data: data,
    });

    return unwrapResponse<ProjectRecord>(response);
  }

  async deleteProject(id: string): Promise<void> {
    return this.delete("projects", id);
  }

  async listProjects(
    params?: Record<string, unknown>
  ): Promise<ProjectRecord[]> {
    return this.list<ProjectRecord>("projects", params);
  }

  async addSprintToProject(
    projectId: string,
    sprintId: string
  ): Promise<ProjectRecord> {
    const response = await this.requestWithRetry<ProjectRecord>({
      method: "POST",
      url: `/projects/${projectId}/sprints`,
      data: { sprint_id: sprintId },
    });

    if (response.data.success && response.data.data) {
      return response.data.data;
    }

    throw new Error(
      response.data.error ||
        response.data.message ||
        "Add sprint operation failed"
    );
  }

  async removeSprintFromProject(
    projectId: string,
    sprintId: string
  ): Promise<ProjectRecord | undefined> {
    const response = await this.requestWithRetry<ProjectRecord>({
      method: "DELETE",
      url: `/projects/${projectId}/sprints/${sprintId}`,
    });

    if (response.data.success) {
      return response.data.data;
    }

    throw new Error(
      response.data.error ||
        response.data.message ||
        "Remove sprint operation failed"
    );
  }

  async addProjectMetaTask(
    projectId: string,
    payload: ProjectMetaTaskInput
  ): Promise<unknown> {
    const response = await this.requestWithRetry<unknown>({
      method: "POST",
      url: `/projects/${projectId}/meta-tasks`,
      data: payload,
    });

    if (response.data.success) {
      return response.data.data;
    }

    throw new Error(
      response.data.error ||
        response.data.message ||
        "Add meta task operation failed"
    );
  }

  async addProjectComment(
    projectId: string,
    comment: ProjectCommentInput
  ): Promise<unknown> {
    const response = await this.requestWithRetry<unknown>({
      method: "POST",
      url: `/projects/${projectId}/comments`,
      data: comment,
    });

    if (response.data.success) {
      return response.data.data;
    }

    throw new Error(
      response.data.error ||
        response.data.message ||
        "Add comment operation failed"
    );
  }

  async listProjectComments(
    projectId: string,
    params?: Record<string, unknown>
  ): Promise<unknown[]> {
    const response = await this.requestWithRetry<unknown[]>({
      method: "GET",
      url: `/projects/${projectId}/comments`,
      params,
    });

    if (response.data.success && response.data.data) {
      return response.data.data;
    }

    throw new Error(
      response.data.error ||
        response.data.message ||
        "List comments operation failed"
    );
  }

  async addProjectBlocker(
    projectId: string,
    blocker: ProjectBlockerInput
  ): Promise<unknown> {
    const response = await this.requestWithRetry<unknown>({
      method: "POST",
      url: `/projects/${projectId}/blockers`,
      data: blocker,
    });

    if (response.data.success) {
      return response.data.data;
    }

    throw new Error(
      response.data.error ||
        response.data.message ||
        "Add blocker operation failed"
    );
  }

  async getProjectMetrics(projectId: string): Promise<ProjectAnalytics> {
    const response = await this.requestWithRetry<ProjectAnalytics>({
      method: "GET",
      url: `/projects/${projectId}/analytics`,
    });

    if (response.data.success && response.data.data) {
      return projectAnalyticsSchema.parse(response.data.data);
    }

    throw new Error(
      response.data.error ||
        response.data.message ||
        "Get metrics operation failed"
    );
  }

  // #endregion Project helpers

  // #region ActionList operations

  /**
   * Create a new action list
   * POST /action-lists
   */
  async createActionList(
    data: ActionListAttributes
  ): Promise<ActionListRecord> {
    // Pass data as-is (backend expects 'title')
    const apiPayload = { ...data };

    // Conditional debug logging BEFORE request
    this.debugLog("createActionList request", {
      url: `${this.baseURL}/action-lists`,
      method: "POST",
      data: apiPayload,
    });

    const response = await this.requestWithRetry<any>({
      method: "POST",
      url: "/action-lists",
      data: apiPayload,
    });

    // Conditional debug logging AFTER response
    this.debugLog("createActionList response", {
      status: response.status,
      hasData: !!response.data,
      dataKeys: response.data ? Object.keys(response.data) : [],
      fullResponse: JSON.stringify(response.data, null, 2),
    });

    const record = unwrapResponse<any>(response);

    // Map name → title for domain (Response has title aliased to name in schema? No, response calls it title in schema but aliased as name for validation?
    // Wait, let's look at schema again. ActionListResponse has `title = Field(..., validation_alias="name")`.
    // This means it reads "name" from input and puts it in "title".
    // If backend returns "title" in JSON, we are fine. If it returns "name", we need mapping.
    // I'll keep the return mapping for now if the backend *returns* name.

    return actionListRecordSchema.parse({
      ...record,
      // If record has title, use it. If it has name, use it as title.
      title: record.title || record.name,
      id: record.id,
    });
  }

  /**
   * Get an action list by ID
   * GET /action-lists/{id}
   */
  async getActionList(id: string): Promise<ActionListRecord> {
    const response = await this.requestWithRetry<any>({
      method: "GET",
      url: `/action-lists/${id}`,
    });

    const record = unwrapResponse<any>(response);

    return actionListRecordSchema.parse({
      ...record,
      title: record.title || record.name,
      id: record.id,
    });
  }

  /**
   * List action lists with optional filters
   * GET /action-lists?status=...&project_id=...
   */
  async listActionLists(
    filters?: Record<string, unknown>
  ): Promise<ActionListRecord[]> {
    const response = await this.requestWithRetry<any>({
      method: "GET",
      url: "/action-lists",
      params: filters,
    });

    const records = unwrapListResponse<any>(response, "action_lists");

    return records.map((record) =>
      actionListRecordSchema.parse({
        ...record,
        title: record.title || record.name,
        id: record.id,
      })
    );
  }

  /**
   * Update an action list
   * PUT /action-lists/{id}
   */
  async updateActionList(
    id: string,
    data: Partial<ActionListAttributes>
  ): Promise<ActionListRecord> {
    // Pass data as-is (backend expects 'title')
    const apiPayload: any = { ...data };

    const response = await this.requestWithRetry<any>({
      method: "PUT",
      url: `/action-lists/${id}`,
      data: apiPayload,
    });

    const record = unwrapResponse<any>(response);

    return actionListRecordSchema.parse({
      ...record,
      title: record.title || record.name,
      id: record.id,
    });
  }

  /**
   * Delete an action list
   * DELETE /action-lists/{id}
   * Returns HTTP 204 No Content on success (no response body)
   */
  async deleteActionList(id: string): Promise<void> {
    const response = await this.requestWithRetry<void>({
      method: "DELETE",
      url: `/action-lists/${id}`,
    });

    // 204 No Content means success with empty body
    if (response.status === 204) {
      return;
    }

    // If response has body, check success flag
    if (response.data && !response.data.success) {
      throw new Error(
        response.data.error ||
          response.data.message ||
          "Delete action list operation failed"
      );
    }
  }

  /**
   * Add an item to an action list
   * POST /action-lists/{id}/items
   */
  async addActionListItem(
    actionListId: string,
    item: { text: string; order?: number }
  ): Promise<ActionListRecord> {
    const response = await this.requestWithRetry<ActionListRecord>({
      method: "POST",
      url: `/action-lists/${actionListId}/items`,
      data: item,
    });

    if (response.data.success && response.data.data) {
      return actionListRecordSchema.parse(response.data.data);
    }

    throw new Error(
      response.data.error ||
        response.data.message ||
        "Add item operation failed"
    );
  }

  /**
   * Toggle an item's completion status
   * PATCH /action-lists/{id}/items/{item_id}
   */
  async toggleActionListItem(
    actionListId: string,
    itemId: string
  ): Promise<ActionListRecord> {
    const response = await this.requestWithRetry<ActionListRecord>({
      method: "PATCH",
      url: `/action-lists/${actionListId}/items/${itemId}`,
    });

    if (response.data.success && response.data.data) {
      return actionListRecordSchema.parse(response.data.data);
    }

    throw new Error(
      response.data.error ||
        response.data.message ||
        "Toggle item operation failed"
    );
  }

  /**
   * Remove an item from an action list
   * DELETE /action-lists/{id}/items/{item_id}
   */
  async removeActionListItem(
    actionListId: string,
    itemId: string
  ): Promise<ActionListRecord> {
    const response = await this.requestWithRetry<ActionListRecord>({
      method: "DELETE",
      url: `/action-lists/${actionListId}/items/${itemId}`,
    });

    if (response.data.success && response.data.data) {
      return actionListRecordSchema.parse(response.data.data);
    }

    throw new Error(
      response.data.error ||
        response.data.message ||
        "Remove item operation failed"
    );
  }

  /**
   * Reorder items in an action list
   * POST /action-lists/{id}/items/reorder
   */
  async reorderActionListItems(
    actionListId: string,
    itemIds: string[]
  ): Promise<ActionListRecord> {
    const response = await this.requestWithRetry<ActionListRecord>({
      method: "POST",
      url: `/action-lists/${actionListId}/items/reorder`,
      data: { item_ids: itemIds },
    });

    if (response.data.success && response.data.data) {
      return actionListRecordSchema.parse(response.data.data);
    }

    throw new Error(
      response.data.error ||
        response.data.message ||
        "Reorder items operation failed"
    );
  }

  /**
   * Bulk delete action lists
   */
  async bulkDeleteActionLists(
    actionListIds: string[]
  ): Promise<{ success: boolean; deleted_count: number }> {
    const response = await this.requestWithRetry<{
      success: boolean;
      deleted_count: number;
    }>({
      method: "POST",
      url: "/action-lists/bulk/delete",
      data: actionListIds, // Backend expects array directly in body
    });

    if (response.data.success && response.data.data) {
      return {
        success: true,
        deleted_count: response.data.data.deleted_count,
      };
    }

    throw new Error(
      response.data.error ||
        response.data.message ||
        "Bulk delete operation failed"
    );
  }

  /**
   * Bulk update action lists
   */
  async bulkUpdateActionLists(
    actionListIds: string[],
    updates: Partial<ActionListAttributes>
  ): Promise<{
    success: boolean;
    updated_count: number;
    action_list_ids: string[];
  }> {
    const response = await this.requestWithRetry<{
      success: boolean;
      updated_count: number;
      action_list_ids: string[];
    }>({
      method: "POST",
      url: "/action-lists/bulk/update",
      data: {
        action_list_ids: actionListIds,
        updates,
      },
    });

    if (response.data.success && response.data.data) {
      return {
        success: true,
        updated_count: response.data.data.updated_count,
        action_list_ids: response.data.data.action_list_ids || actionListIds,
      };
    }

    throw new Error(
      response.data.error ||
        response.data.message ||
        "Bulk update operation failed"
    );
  }

  /**
   * Search action lists with advanced filtering
   */
  async searchActionLists(
    query: string,
    options?: {
      fields?: Array<"title" | "description" | "notes">;
      project_id?: string;
      sprint_id?: string;
      status?: ActionListStatus;
      priority?: ActionListPriority;
      skip?: number;
      limit?: number;
    }
  ): Promise<{
    success: boolean;
    query: string;
    count: number;
    data: ActionListRecord[];
  }> {
    const params: Record<string, any> = { q: query };

    if (options?.fields) params.fields = options.fields;
    if (options?.project_id) params.project_id = options.project_id;
    if (options?.sprint_id) params.sprint_id = options.sprint_id;
    if (options?.status) params.status = options.status;
    if (options?.priority) params.priority = options.priority;
    if (options?.skip !== undefined) params.skip = options.skip;
    if (options?.limit !== undefined) params.limit = options.limit;

    const response = await this.requestWithRetry<{
      success: boolean;
      query: string;
      count: number;
      data: ActionListRecord[];
    }>({
      method: "GET",
      url: "/action-lists/search",
      params,
    });

    if (response.data.success && response.data.data) {
      return {
        success: true,
        query: response.data.data.query,
        count: response.data.data.count,
        data: response.data.data.data.map((record) =>
          actionListRecordSchema.parse(record)
        ),
      };
    }

    throw new Error(
      response.data.error || response.data.message || "Search operation failed"
    );
  }

  // #endregion ActionList operations

  // #region Phase Tracking operations

  /**
   * Get all phases for an entity
   * GET /phases/{entityType}/{entityId}
   */
  async getPhases(
    entityType: "task" | "sprint" | "project",
    entityId: string
  ): Promise<{
    entity_id: string;
    entity_type: string;
    phases: Record<string, unknown>;
  }> {
    const response = await this.requestWithRetry<any>({
      method: "GET",
      url: `/phases/${entityType}/${entityId}`,
    });
    return unwrapResponse(response);
  }

  /**
   * Get a specific phase for an entity
   * GET /phases/{entityType}/{entityId}/{phaseName}
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
    const response = await this.requestWithRetry<any>({
      method: "GET",
      url: `/phases/${entityType}/${entityId}/${phaseName}`,
    });
    return unwrapResponse(response);
  }

  /**
   * Update a specific phase
   * PATCH /phases/{entityType}/{entityId}/{phaseName}
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
    const response = await this.requestWithRetry<any>({
      method: "PATCH",
      url: `/phases/${entityType}/${entityId}/${phaseName}`,
      data: update,
    });
    return unwrapResponse(response);
  }

  /**
   * Advance entity to next phase
   * POST /phases/{entityType}/{entityId}/advance
   */
  async advancePhase(
    entityType: "task" | "sprint" | "project",
    entityId: string
  ): Promise<{
    entity_id: string;
    entity_type: string;
    phases: Record<string, unknown>;
  }> {
    const response = await this.requestWithRetry<any>({
      method: "POST",
      url: `/phases/${entityType}/${entityId}/advance`,
    });
    return unwrapResponse(response);
  }

  /**
   * Start a specific phase
   * POST /phases/{entityType}/{entityId}/{phaseName}/start
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
    const response = await this.requestWithRetry<any>({
      method: "POST",
      url: `/phases/${entityType}/${entityId}/${phaseName}/start`,
    });
    return unwrapResponse(response);
  }

  /**
   * Complete a specific phase
   * POST /phases/{entityType}/{entityId}/{phaseName}/complete
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
    const response = await this.requestWithRetry<any>({
      method: "POST",
      url: `/phases/${entityType}/${entityId}/${phaseName}/complete`,
    });
    return unwrapResponse(response);
  }

  /**
   * Block a specific phase
   * POST /phases/{entityType}/{entityId}/{phaseName}/block
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
    const response = await this.requestWithRetry<any>({
      method: "POST",
      url: `/phases/${entityType}/${entityId}/${phaseName}/block`,
      data: blockedReason ? { blocked_reason: blockedReason } : undefined,
    });
    return unwrapResponse(response);
  }

  /**
   * Unblock a specific phase
   * POST /phases/{entityType}/{entityId}/{phaseName}/unblock
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
    const response = await this.requestWithRetry<any>({
      method: "POST",
      url: `/phases/${entityType}/${entityId}/${phaseName}/unblock`,
    });
    return unwrapResponse(response);
  }

  /**
   * Skip a specific phase
   * POST /phases/{entityType}/{entityId}/{phaseName}/skip
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
    const response = await this.requestWithRetry<any>({
      method: "POST",
      url: `/phases/${entityType}/${entityId}/${phaseName}/skip`,
      data: skipReason ? { skip_reason: skipReason } : undefined,
    });
    return unwrapResponse(response);
  }

  /**
   * Get phase summary for an entity
   * GET /phases/{entityType}/{entityId}/summary
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
    const response = await this.requestWithRetry<any>({
      method: "GET",
      url: `/phases/${entityType}/${entityId}/summary`,
    });
    return unwrapResponse(response);
  }

  /**
   * Get phase analytics for entity type
   * GET /phases/{entityType}/analytics
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
    const response = await this.requestWithRetry<any>({
      method: "GET",
      url: `/phases/${entityType}/analytics`,
      params: limit ? { limit } : undefined,
    });
    return unwrapResponse(response);
  }

  // #endregion Phase Tracking operations
}

/**
 * Singleton instance with default configuration
 */
export const backendClient = new BackendClient();
