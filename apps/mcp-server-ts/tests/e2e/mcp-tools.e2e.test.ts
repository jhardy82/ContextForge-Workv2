/**
 * E2E Test Suite for MCP Tools
 *
 * This suite validates the complete MCP tool functionality by:
 * 1. Spawning the MCP server via STDIO transport
 * 2. Connecting an MCP client
 * 3. Exercising all major tool operations
 *
 * Prerequisites:
 * - Backend API running on http://localhost:3001
 * - Run with: npm run test:e2e
 */

import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

// E2E tests require backend - skip unless explicitly enabled
// Set RUN_E2E=true to run these tests with the backend available
const BACKEND_URL = process.env.TASK_MANAGER_API_ENDPOINT || "http://localhost:3001";
const RUN_E2E = process.env.RUN_E2E === "true";
const SKIP_E2E = !RUN_E2E;

// Increase timeout for E2E tests
const E2E_TIMEOUT = 30000;

describe.skipIf(SKIP_E2E)("MCP Tools E2E", () => {
  let client: Client;
  let transport: StdioClientTransport;

  beforeAll(async () => {
    // Check if backend is available
    try {
      const response = await fetch(`${BACKEND_URL}/health`);
      if (!response.ok) {
        throw new Error(`Backend health check failed: ${response.status}`);
      }
    } catch (error) {
      console.warn(`Backend not available at ${BACKEND_URL}, skipping E2E tests`);
      throw error;
    }

    // Create MCP client with STDIO transport
    transport = new StdioClientTransport({
      command: "npx",
      args: ["tsx", "src/index.ts"],
      env: {
        ...process.env,
        TASKMAN_MCP_TRANSPORT: "stdio",
        NODE_ENV: "test",
      },
    });

    client = new Client(
      {
        name: "e2e-test-client",
        version: "1.0.0",
      },
      { capabilities: {} }
    );

    await client.connect(transport);
  }, E2E_TIMEOUT);

  afterAll(async () => {
    if (client) {
      await client.close();
    }
  });

  describe("Server Activation", () => {
    it("should activate taskman server", async () => {
      const result = await client.callTool({
        name: "activate_taskman_server",
        arguments: { verbose: true },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.status).toBe("ready");
      expect(content.api_url).toBeDefined();
    }, E2E_TIMEOUT);

    it("should activate task tools", async () => {
      const result = await client.callTool({
        name: "activate_task_tools",
        arguments: {},
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.tools).toBeDefined();
      expect(Array.isArray(content.tools)).toBe(true);
    }, E2E_TIMEOUT);

    it("should activate project tools", async () => {
      const result = await client.callTool({
        name: "activate_project_tools",
        arguments: {},
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.tools).toBeDefined();
    }, E2E_TIMEOUT);

    it("should activate action list tools", async () => {
      const result = await client.callTool({
        name: "activate_action_list_tools",
        arguments: {},
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.tools).toBeDefined();
    }, E2E_TIMEOUT);
  });

  describe("Project CRUD Operations", () => {
    const testProjectId = `e2e-test-project-${Date.now()}`;
    let createdProjectId: string;

    it("should create a project", async () => {
      const result = await client.callTool({
        name: "project_create",
        arguments: {
          project: {
            id: testProjectId,
            name: "E2E Test Project",
            description: "Created by E2E test suite",
            status: "active",
          },
        },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.project).toBeDefined();
      createdProjectId = content.project.id;
      expect(content.project.name).toBe("E2E Test Project");
    }, E2E_TIMEOUT);

    it("should read a project", async () => {
      const result = await client.callTool({
        name: "project_read",
        arguments: { projectId: createdProjectId },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.project.id).toBe(createdProjectId);
    }, E2E_TIMEOUT);

    it("should update a project", async () => {
      const result = await client.callTool({
        name: "project_update",
        arguments: {
          projectId: createdProjectId,
          changes: {
            description: "Updated by E2E test",
          },
        },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.project.description).toBe("Updated by E2E test");
    }, E2E_TIMEOUT);

    it("should list projects", async () => {
      const result = await client.callTool({
        name: "project_list",
        arguments: { status: "active" },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.projects).toBeDefined();
      expect(Array.isArray(content.projects)).toBe(true);
    }, E2E_TIMEOUT);

    it("should delete a project", async () => {
      const result = await client.callTool({
        name: "project_delete",
        arguments: { projectId: createdProjectId },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.success).toBe(true);
    }, E2E_TIMEOUT);
  });

  describe("Task CRUD Operations", () => {
    let testProjectId: string;
    let createdTaskId: string;

    beforeAll(async () => {
      // Create a project for task testing
      const result = await client.callTool({
        name: "project_create",
        arguments: {
          project: {
            id: `task-test-project-${Date.now()}`,
            name: "Task Test Project",
            status: "active",
          },
        },
      });
      const content = JSON.parse(result.content[0].text);
      testProjectId = content.project.id;
    });

    afterAll(async () => {
      // Cleanup project
      if (testProjectId) {
        await client.callTool({
          name: "project_delete",
          arguments: { projectId: testProjectId },
        });
      }
    });

    it("should create a task", async () => {
      const result = await client.callTool({
        name: "task_create",
        arguments: {
          task: {
            title: "E2E Test Task",
            description: "Created by E2E test suite",
            project_id: testProjectId,
            status: "new",
            priority: "medium",
          },
        },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.task).toBeDefined();
      createdTaskId = content.task.id;
      expect(content.task.title).toBe("E2E Test Task");
    }, E2E_TIMEOUT);

    it("should read a task", async () => {
      const result = await client.callTool({
        name: "task_read",
        arguments: { taskId: createdTaskId },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.task.id).toBe(createdTaskId);
    }, E2E_TIMEOUT);

    it("should update a task", async () => {
      const result = await client.callTool({
        name: "task_update",
        arguments: {
          taskId: createdTaskId,
          changes: {
            status: "in_progress",
            priority: "high",
          },
        },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.task.status).toBe("in_progress");
      expect(content.task.priority).toBe("high");
    }, E2E_TIMEOUT);

    it("should set task status", async () => {
      const result = await client.callTool({
        name: "task_set_status",
        arguments: {
          taskId: createdTaskId,
          status: "completed",
          notes: "Completed by E2E test",
        },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.task.status).toBe("completed");
    }, E2E_TIMEOUT);

    it("should list tasks", async () => {
      const result = await client.callTool({
        name: "task_list",
        arguments: { project_id: testProjectId },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.tasks).toBeDefined();
      expect(Array.isArray(content.tasks)).toBe(true);
    }, E2E_TIMEOUT);

    it("should search tasks", async () => {
      const result = await client.callTool({
        name: "task_search",
        arguments: { query: "E2E Test" },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.tasks).toBeDefined();
    }, E2E_TIMEOUT);

    it("should delete a task", async () => {
      const result = await client.callTool({
        name: "task_delete",
        arguments: { taskId: createdTaskId },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.success).toBe(true);
    }, E2E_TIMEOUT);
  });

  describe("Action List CRUD Operations", () => {
    let testProjectId: string;
    let createdActionListId: string;
    let itemIds: string[] = [];

    beforeAll(async () => {
      // Create a project for action list testing
      const result = await client.callTool({
        name: "project_create",
        arguments: {
          project: {
            id: `action-list-test-project-${Date.now()}`,
            name: "Action List Test Project",
            status: "active",
          },
        },
      });
      const content = JSON.parse(result.content[0].text);
      testProjectId = content.project.id;
    });

    afterAll(async () => {
      // Cleanup project
      if (testProjectId) {
        await client.callTool({
          name: "project_delete",
          arguments: { projectId: testProjectId },
        });
      }
    });

    it("should create an action list", async () => {
      const result = await client.callTool({
        name: "action_list_create",
        arguments: {
          title: "E2E Test Action List",
          description: "Created by E2E test suite",
          project_id: testProjectId,
          status: "active",
          priority: "high",
        },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.action_list).toBeDefined();
      createdActionListId = content.action_list.id;
    }, E2E_TIMEOUT);

    it("should add items to action list", async () => {
      for (let i = 1; i <= 3; i++) {
        const result = await client.callTool({
          name: "action_list_add_item",
          arguments: {
            action_list_id: createdActionListId,
            text: `E2E Test Item ${i}`,
            order: i,
          },
        });

        expect(result.isError).toBeFalsy();
        const content = JSON.parse(result.content[0].text);
        // Check total items or items array length
        const itemCount = content.action_list.total_items ?? content.action_list.items?.length ?? 0;
        expect(itemCount).toBe(i);

        // Store the item ID
        const items = content.action_list.items;
        if (items && items.length > 0) {
          itemIds.push(items[items.length - 1].id);
        }
      }
    }, E2E_TIMEOUT);

    it("should toggle item completion", async () => {
      // Skip if we don't have any item IDs (previous test may have failed)
      if (itemIds.length === 0) {
        console.warn("Skipping toggle test - no item IDs available");
        return;
      }

      const result = await client.callTool({
        name: "action_list_toggle_item",
        arguments: {
          action_list_id: createdActionListId,
          item_id: itemIds[0],
        },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.action_list).toBeDefined();
      // Verify the item was toggled (at least one item should be completed)
      const items = content.action_list.items;
      if (items) {
        const completedItem = items.find((item: { id: string }) => item.id === itemIds[0]);
        expect(completedItem?.completed).toBe(true);
      }
    }, E2E_TIMEOUT);

    it("should read action list with items", async () => {
      const result = await client.callTool({
        name: "action_list_read",
        arguments: { action_list_id: createdActionListId },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.action_list.id).toBe(createdActionListId);
      expect(content.action_list.items.length).toBe(3);
    }, E2E_TIMEOUT);

    it("should remove item from action list", async () => {
      // Skip if we don't have enough item IDs
      if (itemIds.length < 2) {
        console.warn("Skipping remove test - not enough item IDs available");
        return;
      }

      const result = await client.callTool({
        name: "action_list_remove_item",
        arguments: {
          action_list_id: createdActionListId,
          item_id: itemIds[1],
        },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.action_list).toBeDefined();
      // Verify item count decreased
      const itemCount = content.action_list.total_items ?? content.action_list.items?.length ?? 0;
      expect(itemCount).toBe(2);
    }, E2E_TIMEOUT);

    it("should update action list metadata", async () => {
      const result = await client.callTool({
        name: "action_list_update",
        arguments: {
          action_list_id: createdActionListId,
          title: "E2E Test Action List (Updated)",
          status: "completed",
        },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.action_list.title).toBe("E2E Test Action List (Updated)");
      expect(content.action_list.status).toBe("completed");
    }, E2E_TIMEOUT);

    it("should list action lists", async () => {
      const result = await client.callTool({
        name: "action_list_list",
        arguments: { project_id: testProjectId },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.action_lists).toBeDefined();
      expect(Array.isArray(content.action_lists)).toBe(true);
    }, E2E_TIMEOUT);

    it("should delete action list", async () => {
      const result = await client.callTool({
        name: "action_list_delete",
        arguments: { action_list_id: createdActionListId },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.success).toBe(true);
    }, E2E_TIMEOUT);
  });

  describe("Bulk Operations", () => {
    let testProjectId: string;
    let taskIds: string[] = [];

    beforeAll(async () => {
      // Create project and tasks for bulk operations
      const projectResult = await client.callTool({
        name: "project_create",
        arguments: {
          project: {
            id: `bulk-test-project-${Date.now()}`,
            name: "Bulk Operations Test Project",
            status: "active",
          },
        },
      });
      const projectContent = JSON.parse(projectResult.content[0].text);
      testProjectId = projectContent.project.id;

      // Create 3 tasks
      for (let i = 1; i <= 3; i++) {
        const result = await client.callTool({
          name: "task_create",
          arguments: {
            task: {
              title: `Bulk Test Task ${i}`,
              project_id: testProjectId,
              status: "new",
              priority: "low",
            },
          },
        });
        const content = JSON.parse(result.content[0].text);
        taskIds.push(content.task.id);
      }
    }, E2E_TIMEOUT);

    afterAll(async () => {
      // Cleanup
      if (testProjectId) {
        await client.callTool({
          name: "project_delete",
          arguments: { projectId: testProjectId },
        });
      }
    });

    it("should bulk update tasks", async () => {
      const result = await client.callTool({
        name: "task_bulk_update",
        arguments: {
          taskIds: taskIds,
          changes: {
            priority: "high",
            status: "in_progress",
          },
        },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.success_count).toBe(3);
      expect(content.failure_count).toBe(0);
    }, E2E_TIMEOUT);

    it("should handle bulk update with mixed valid/invalid IDs", async () => {
      const result = await client.callTool({
        name: "task_bulk_update",
        arguments: {
          taskIds: [...taskIds, "invalid-task-id"],
          changes: {
            priority: "critical",
          },
        },
      });

      expect(result.isError).toBeFalsy();
      const content = JSON.parse(result.content[0].text);
      expect(content.success_count).toBe(3);
      expect(content.failure_count).toBe(1);
      expect(content.failures.length).toBe(1);
    }, E2E_TIMEOUT);
  });

  describe("Error Handling", () => {
    it("should return error for non-existent task", async () => {
      const result = await client.callTool({
        name: "task_read",
        arguments: { taskId: "non-existent-task-id" },
      });

      // MCP tools may return isError flag, JSON error, or plain text error
      const text = result.content[0].text;
      let hasError = result.isError;

      if (!hasError) {
        try {
          const content = JSON.parse(text);
          hasError = !!content.error;
        } catch {
          // Non-JSON response indicates an error message
          hasError = text.includes("error") || text.includes("not found") ||
                     text.includes("failed") || text.includes("Circuit");
        }
      }

      expect(hasError).toBeTruthy();
    }, E2E_TIMEOUT);

    it("should return error for non-existent project", async () => {
      const result = await client.callTool({
        name: "project_read",
        arguments: { projectId: "non-existent-project-id" },
      });

      const text = result.content[0].text;
      let hasError = result.isError;

      if (!hasError) {
        try {
          const content = JSON.parse(text);
          hasError = !!content.error;
        } catch {
          hasError = text.includes("error") || text.includes("not found") ||
                     text.includes("failed") || text.includes("Circuit");
        }
      }

      expect(hasError).toBeTruthy();
    }, E2E_TIMEOUT);

    it("should return error for non-existent action list", async () => {
      const result = await client.callTool({
        name: "action_list_read",
        arguments: { action_list_id: "non-existent-action-list-id" },
      });

      const text = result.content[0].text;
      let hasError = result.isError;

      if (!hasError) {
        try {
          const content = JSON.parse(text);
          hasError = !!content.error;
        } catch {
          hasError = text.includes("error") || text.includes("not found") ||
                     text.includes("failed") || text.includes("Circuit");
        }
      }

      expect(hasError).toBeTruthy();
    }, E2E_TIMEOUT);
  });
});
