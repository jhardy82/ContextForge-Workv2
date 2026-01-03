/**
 * Task2 API Client
 *
 * HTTP client for the TaskMan-v2 backend API (FastAPI).
 * Provides methods for task CRUD, projects, sprints, and health checks.
 */

import { mockTaskApi } from "./mock-task-api";
import {
  ActionList,
  AIPromptType,
  ConnectionStatus,
  HealthCheckResponse,
  Project,
  Sprint,
  Task,
} from "./types";
import { log } from "./unified-logger";

// GLOBAL SWITCH FOR MOCK MODE
export const IS_MOCK_MODE = true;

export class Task2ApiClient {
  private baseUrl: string;
  private connected: boolean = false;
  private lastHealthCheck: Date | null = null;

  constructor(baseUrl?: string) {
    this.baseUrl = (baseUrl || "/api/v1").replace(/\/$/, "");
    log.info("api", "api_client_init", { baseUrl: this.baseUrl });
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
        const data: HealthCheckResponse = await response.json();
        this.connected = data.status === "healthy";
        this.lastHealthCheck = new Date();

        log.info("api", "health_check_success", { status: data.status });

        return {
          connected: this.connected,
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

      log.warn("api", "health_check_failed", { error: errorMessage });

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

  async getTasks(filters?: {
    status?: string;
    project_id?: string;
    sprint_id?: string;
    limit?: number;
    offset?: number;
  }): Promise<Task[]> {
    try {
      const params = new URLSearchParams();
      if (filters?.status) params.append("status", filters.status);
      if (filters?.project_id) params.append("project_id", filters.project_id);
      if (filters?.sprint_id) params.append("sprint_id", filters.sprint_id);
      if (filters?.limit) params.append("limit", filters.limit.toString());
      if (filters?.offset) params.append("offset", filters.offset.toString());

      const url = `${this.baseUrl}/tasks${
        params.toString() ? `?${params}` : ""
      }`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`Failed to fetch tasks: ${response.status}`);
      }

      const data = await response.json();

      // Handle both array (legacy) and paginated response (standard)
      const tasks = Array.isArray(data) ? data : data.tasks || [];

      log.info("api", "tasks_fetched", { count: tasks.length });

      return tasks;
    } catch (error) {
      log.error("api", "tasks_fetch_failed", { error: String(error) });
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
      log.error("api", "task_fetch_failed", { taskId, error: String(error) });
      return null;
    }
  }

  async createTask(task: Partial<Task>): Promise<Task | null> {
    try {
      const response = await fetch(`${this.baseUrl}/tasks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(task),
      });

      if (!response.ok) {
        throw new Error(`Failed to create task: ${response.status}`);
      }

      const created = await response.json();
      log.info("api", "task_created", { taskId: created.id });

      return created;
    } catch (error) {
      log.error("api", "task_create_failed", { error: String(error) });
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
      log.info("api", "task_updated", { taskId });

      return updated;
    } catch (error) {
      log.error("api", "task_update_failed", { taskId, error: String(error) });
      return null;
    }
  }

  async deleteTask(taskId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/tasks/${taskId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error(`Failed to delete task: ${response.status}`);
      }

      log.info("api", "task_deleted", { taskId });
      return true;
    } catch (error) {
      log.error("api", "task_delete_failed", { taskId, error: String(error) });
      return false;
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
      log.info("api", "projects_fetched", { count: data.length });

      return data;
    } catch (error) {
      log.error("api", "projects_fetch_failed", { error: String(error) });
      return [];
    }
  }

  async getProject(projectId: string): Promise<Project | null> {
    try {
      const response = await fetch(`${this.baseUrl}/projects/${projectId}`);

      if (!response.ok) {
        if (response.status === 404) return null;
        throw new Error(`Failed to fetch project: ${response.status}`);
      }

      const data = await response.json();

      // Handle both array (legacy) and paginated response (standard)
      const projects = Array.isArray(data) ? data : data.projects || [];
      log.info("api", "projects_fetched", { count: projects.length });

      return projects;
    } catch (error) {
      log.error("api", "project_fetch_failed", {
        projectId,
        error: String(error),
      });
      return null;
    }
  }

  async createProject(project: Partial<Project>): Promise<Project | null> {
    try {
      const response = await fetch(`${this.baseUrl}/projects`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(project),
      });

      if (!response.ok) {
        throw new Error(`Failed to create project: ${response.status}`);
      }

      const created = await response.json();
      log.info("api", "project_created", { projectId: created.id });
      return created;
    } catch (error) {
      log.error("api", "project_create_failed", { error: String(error) });
      return null;
    }
  }

  // ============================================================================
  // Sprints API
  // ============================================================================

  async getSprints(projectId?: string): Promise<Sprint[]> {
    try {
      const url = projectId
        ? `${this.baseUrl}/sprints?project_id=${projectId}`
        : `${this.baseUrl}/sprints`;

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`Failed to fetch sprints: ${response.status}`);
      }

      const data = await response.json();

      // Handle both array (legacy) and paginated response (standard)
      const sprints = Array.isArray(data) ? data : data.sprints || [];
      log.info("api", "sprints_fetched", { count: sprints.length });

      return sprints;
    } catch (error) {
      log.error("api", "sprints_fetch_failed", { error: String(error) });
      return [];
    }
  }

  async createSprint(sprint: Partial<Sprint>): Promise<Sprint | null> {
    try {
      const response = await fetch(`${this.baseUrl}/sprints`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(sprint),
      });

      if (!response.ok) {
        throw new Error(`Failed to create sprint: ${response.status}`);
      }

      const created = await response.json();
      log.info("api", "sprint_created", { sprintId: created.id });

      return created;
    } catch (error) {
      log.error("api", "sprint_create_failed", { error: String(error) });
      return null;
    }
  }

  async updateSprint(
    sprintId: string,
    updates: Partial<Sprint>
  ): Promise<Sprint | null> {
    try {
      const response = await fetch(`${this.baseUrl}/sprints/${sprintId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error(`Failed to update sprint: ${response.status}`);
      }

      const updated = await response.json();
      log.info("api", "sprint_updated", { sprintId });

      return updated;
    } catch (error) {
      log.error("api", "sprint_update_failed", {
        sprintId,
        error: String(error),
      });
      return null;
    }
  }

  // ============================================================================
  // Action Lists API
  // ============================================================================

  async getActionLists(filters?: {
    status?: string;
    project_id?: string;
  }): Promise<ActionList[]> {
    try {
      const params = new URLSearchParams();
      if (filters?.status) params.append("status", filters.status);
      if (filters?.project_id) params.append("project_id", filters.project_id);

      const response = await fetch(
        `${this.baseUrl}/action-lists?${params.toString()}`
      );
      if (!response.ok)
        throw new Error(`Failed to fetch action lists: ${response.status}`);
      return await response.json();
    } catch (error) {
      log.error("api", "action_lists_fetch_failed", { error: String(error) });
      return [];
    }
  }

  async createActionList(
    data: Partial<ActionList>
  ): Promise<ActionList | null> {
    try {
      const response = await fetch(`${this.baseUrl}/action-lists`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!response.ok)
        throw new Error(`Failed to create action list: ${response.status}`);
      return await response.json();
    } catch (error) {
      log.error("api", "action_list_create_failed", { error: String(error) });
      return null;
    }
  }

  async addActionListItem(
    listId: string,
    text: string
  ): Promise<ActionList | null> {
    try {
      const response = await fetch(
        `${this.baseUrl}/action-lists/${listId}/items`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        }
      );
      if (!response.ok)
        throw new Error(`Failed to add item: ${response.status}`);
      return await response.json();
    } catch (error) {
      log.error("api", "action_list_add_item_failed", {
        listId,
        error: String(error),
      });
      return null;
    }
  }

  async toggleActionListItem(
    listId: string,
    itemId: string
  ): Promise<ActionList | null> {
    try {
      const response = await fetch(
        `${this.baseUrl}/action-lists/${listId}/items/${itemId}/toggle`,
        {
          method: "POST",
        }
      );
      if (!response.ok)
        throw new Error(`Failed to toggle item: ${response.status}`);
      return await response.json();
    } catch (error) {
      log.error("api", "action_list_toggle_item_failed", {
        listId,
        itemId,
        error: String(error),
      });
      return null;
    }
  }

  async deleteActionList(listId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/action-lists/${listId}`, {
        method: "DELETE",
      });
      if (!response.ok)
        throw new Error(`Failed to delete action list: ${response.status}`);
      return true;
    } catch (error) {
      log.error("api", "action_list_delete_failed", {
        listId,
        error: String(error),
      });
      return false;
    }
  }

  // ============================================================================
  // AI Agent API
  // ============================================================================

  async sendChatMessage(message: string): Promise<ChatResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/agent/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error(`Agent chat failed: ${response.status}`);
      }

      const data = await response.json();
      log.info("api", "agent_chat_success", { action: data.action_taken });
      return data;
    } catch (error) {
      log.error("api", "agent_chat_failed", { error: String(error) });
      return {
        response: "Sorry, I'm having trouble connecting to the server.",
        action_taken: "error",
      };
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
${
  task.acceptance_criteria?.length
    ? `Acceptance Criteria:\n${task.acceptance_criteria
        .map((c) => `- ${c}`)
        .join("\n")}`
    : ""
}
${
  task.dependencies?.length
    ? `Dependencies: ${task.dependencies.join(", ")}`
    : ""
}
${task.ai_context ? `Additional Context: ${task.ai_context}` : ""}
`.trim();

    const prompts: Record<AIPromptType, string> = {
      implementation: `You are implementing the following task. Provide a detailed implementation plan and code.

${baseContext}

Please provide:
1. Implementation approach
2. Key code changes needed
3. Potential edge cases to handle
4. Testing considerations`,

      testing: `You are writing tests for the following task. Provide comprehensive test coverage.

${baseContext}

Please provide:
1. Unit test cases
2. Integration test scenarios
3. Edge cases to test
4. Mocking requirements`,

      validation: `You are validating the implementation of the following task. Review against requirements.

${baseContext}

Please verify:
1. All acceptance criteria are met
2. Edge cases are handled
3. Error handling is proper
4. Code quality standards`,

      documentation: `You are documenting the following task. Provide clear documentation.

${baseContext}

Please document:
1. What was implemented
2. How to use the feature
3. Configuration options
4. Known limitations`,
    };

    log.info("api", "ai_prompt_generated", {
      taskId: task.id,
      promptType: type,
    });

    return prompts[type];
  }
}

// Export singleton for convenience
// Export singleton for convenience
// If IS_MOCK_MODE is true, we export the mock API implementation
// cast as Task2ApiClient (structural compatibility required)
export const task2Api = (IS_MOCK_MODE
  ? mockTaskApi
  : new Task2ApiClient()) as unknown as Task2ApiClient;
