/**
 * DTM (Developer Task Management) API Client
 *
 * HTTP client for the legacy DTM API server.
 * Provides methods for task CRUD, projects, and health checks.
 *
 * Note: This client is for backward compatibility with the older DTM API.
 * New development should use Task2ApiClient for the TaskMan-v2 backend.
 */

import { AIPromptType, ConnectionStatus, Project, Task } from "./types";
import { ulog } from "./unified-logger";

export class DTMApiClient {
  private baseUrl: string;
  private connected: boolean = false;
  private lastHealthCheck: Date | null = null;

  constructor(baseUrl?: string) {
    this.baseUrl = (
      baseUrl ||
      import.meta.env.VITE_API_URL ||
      "http://localhost:3001/api"
    ).replace(/\/$/, "");
    ulog("info", "dtm_api_client_init", { baseUrl: this.baseUrl });
  }

  // ============================================================================
  // Connection Status
  // ============================================================================

  isConnected(): boolean {
    return this.connected;
  }

  async checkHealth(): Promise<ConnectionStatus> {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(`${this.baseUrl}/health`, {
        method: "GET",
        signal: controller.signal,
      });
      clearTimeout(timeout);

      if (response.ok) {
        this.connected = true;
        this.lastHealthCheck = new Date();

        ulog("info", "dtm_health_check_success");

        return {
          connected: true,
          status: "connected",
          lastChecked: this.lastHealthCheck,
        };
      } else {
        throw new Error(`Health check failed: ${response.status}`);
      }
    } catch (error) {
      this.connected = false;
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";

      ulog("warn", "dtm_health_check_failed", { error: errorMessage });

      return {
        connected: false,
        status: "disconnected",
        error: errorMessage,
      };
    }
  }

  // ============================================================================
  // Tasks API
  // ============================================================================

  async getTasks(): Promise<Task[]> {
    try {
      const response = await fetch(`${this.baseUrl}/tasks`);

      if (!response.ok) {
        throw new Error(`Failed to fetch tasks: ${response.status}`);
      }

      const data = await response.json();
      ulog("info", "dtm_tasks_fetched", { count: data.length });

      return data;
    } catch (error) {
      ulog("error", "dtm_tasks_fetch_failed", { error: String(error) });
      return [];
    }
  }

  async getTask(taskId: string): Promise<Task | null> {
    try {
      const response = await fetch(`${this.baseUrl}/tasks/${taskId}`);

      if (!response.ok) {
        if (response.status === 404) return null;
        throw new Error(`Failed to fetch task: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      ulog("error", "dtm_task_fetch_failed", { taskId, error: String(error) });
      return null;
    }
  }

  async updateTask(
    taskId: string,
    updates: Partial<Task>
  ): Promise<Task | null> {
    try {
      const response = await fetch(`${this.baseUrl}/tasks/${taskId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error(`Failed to update task: ${response.status}`);
      }

      const updated = await response.json();
      ulog("info", "dtm_task_updated", { taskId });

      return updated;
    } catch (error) {
      ulog("error", "dtm_task_update_failed", { taskId, error: String(error) });
      return null;
    }
  }

  // ============================================================================
  // Projects API
  // ============================================================================

  async getProjects(): Promise<Project[]> {
    try {
      const response = await fetch(`${this.baseUrl}/projects`);

      if (!response.ok) {
        throw new Error(`Failed to fetch projects: ${response.status}`);
      }

      const data = await response.json();
      ulog("info", "dtm_projects_fetched", { count: data.length });

      return data;
    } catch (error) {
      ulog("error", "dtm_projects_fetch_failed", { error: String(error) });
      return [];
    }
  }

  // ============================================================================
  // AI Prompt Generation
  // ============================================================================

  generateAIPrompt(task: Task, type: AIPromptType): string {
    const baseContext = `
Task: ${task.title}
ID: ${task.id}
Status: ${task.status}
Priority: ${task.priority}
${task.description ? `Description: ${task.description}` : ""}
`.trim();

    const prompts: Record<AIPromptType, string> = {
      implementation: `Implement the following task:\n\n${baseContext}`,
      testing: `Write tests for:\n\n${baseContext}`,
      validation: `Validate implementation of:\n\n${baseContext}`,
      documentation: `Document:\n\n${baseContext}`,
    };

    return prompts[type];
  }
}

// Export singleton for convenience
export const dtmApi = new DTMApiClient();
