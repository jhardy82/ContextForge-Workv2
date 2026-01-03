/**
 * Activation Tools - Server Status Check and Tool Preparation
 *
 * Provides "activate_X_tools" actions for each TaskMan object type that:
 * 1. Check backend API server status
 * 2. Start the server if needed (via user guidance)
 * 3. Validate connectivity and prepare tools for use
 * 4. Return available tools and their capabilities
 *
 * Object Types:
 * - activate_task_tools: Prepare task management tools
 * - activate_project_tools: Prepare project management tools
 * - activate_action_list_tools: Prepare action list tools
 * - activate_taskman_server: General server activation and status
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { backendClient } from "../../backend/client.js";
import { config } from "../../config/index.js";
import { createModuleLogger } from "../../infrastructure/logger.js";

const logger = createModuleLogger("activation-tools");

/**
 * Server health status response
 */
interface ServerStatus {
  serverOnline: boolean;
  apiEndpoint: string;
  latencyMs: number | null;
  message: string;
  startupInstructions?: string[];
}

/**
 * Tool activation response
 */
interface ToolActivationResult {
  activated: boolean;
  serverStatus: ServerStatus;
  availableTools: string[];
  toolDescriptions: Record<string, string>;
  nextSteps?: string[];
  [key: string]: unknown;
}

type ToolResult<T> = {
  content: Array<{ type: "text"; text: string }>;
  structuredContent?: T;
};

function asJson<T>(payload: T): ToolResult<T> {
  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(payload, null, 2),
      },
    ],
    structuredContent: payload,
  };
}

/**
 * Check if the TaskMan backend API server is online
 */
async function checkServerStatus(): Promise<ServerStatus> {
  const apiEndpoint = config.TASK_MANAGER_API_ENDPOINT;
  const startTime = Date.now();

  try {
    // Try to hit the health endpoint
    const healthResponse = await backendClient.health();
    const latencyMs = Date.now() - startTime;

    if (healthResponse && healthResponse.status === "ok") {
      return {
        serverOnline: true,
        apiEndpoint,
        latencyMs,
        message: `TaskMan API server is online and healthy (${latencyMs}ms response time)`,
      };
    }

    return {
      serverOnline: false,
      apiEndpoint,
      latencyMs,
      message: `TaskMan API server responded but reported unhealthy status: ${healthResponse?.status || "unknown"}`,
      startupInstructions: getStartupInstructions(),
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    logger.warn({ error: errorMessage }, "Backend API health check failed");

    return {
      serverOnline: false,
      apiEndpoint,
      latencyMs: null,
      message: `TaskMan API server is not responding: ${errorMessage}`,
      startupInstructions: getStartupInstructions(),
    };
  }
}

/**
 * Get startup instructions for the TaskMan API server
 */
function getStartupInstructions(): string[] {
  return [
    "To start the TaskMan API server:",
    "1. Navigate to: cd vs-code-task-manager",
    "2. Install dependencies (if needed): npm install",
    "3. Start the server: npm start",
    "4. Or use PM2: pm2 start ecosystem.config.cjs",
    "",
    "The server should be running at: " + config.TASK_MANAGER_API_ENDPOINT,
    "",
    "Alternative: Start both frontend and API together:",
    "  cd vs-code-task-manager && npm run dev",
  ];
}

/**
 * Task management tools catalog
 */
const TASK_TOOLS: Record<string, string> = {
  task_create: "Create a new task with full attributes (title, description, status, priority, etc.)",
  task_read: "Retrieve a task by its ID",
  task_update: "Update an existing task's attributes",
  task_delete: "Soft-delete a task (sets deleted flag)",
  task_list: "List tasks with optional filtering (status, priority, project, sprint, etc.)",
  task_set_status: "Update task status with optional completion notes",
  task_assign: "Assign a task to one or more users",
  task_bulk_update: "Update multiple tasks at once",
  task_bulk_assign_sprint: "Assign multiple tasks to a sprint",
  task_search: "Full-text search across task fields",
};

/**
 * Project management tools catalog
 */
const PROJECT_TOOLS: Record<string, string> = {
  project_create: "Create a new project with metadata",
  project_read: "Retrieve a project by its ID",
  project_update: "Update project attributes",
  project_delete: "Soft-delete a project",
  project_list: "List projects with optional filtering",
  project_analytics: "Get project analytics and statistics",
  project_add_comment: "Add a comment to a project",
  project_list_comments: "List comments on a project",
  project_add_blocker: "Add a blocker to a project",
  project_list_blockers: "List project blockers",
  project_resolve_blocker: "Mark a blocker as resolved",
  project_add_meta_task: "Add a meta-task to a project",
  project_list_meta_tasks: "List project meta-tasks",
  project_update_meta_task: "Update a meta-task",
  project_link_task: "Link a task to a project",
  project_unlink_task: "Unlink a task from a project",
  project_sprint_create: "Create a new sprint in a project",
  project_sprint_list: "List sprints in a project",
  project_sprint_update: "Update a sprint",
  project_sprint_delete: "Delete a sprint",
};

/**
 * Action list tools catalog
 */
const ACTION_LIST_TOOLS: Record<string, string> = {
  action_list_create: "Create a new action list",
  action_list_read: "Retrieve an action list by ID",
  action_list_update: "Update action list metadata",
  action_list_delete: "Delete an action list",
  action_list_list: "List action lists with filtering",
  action_list_add_item: "Add an item to an action list",
  action_list_update_item: "Update an action list item",
  action_list_remove_item: "Remove an item from an action list",
  action_list_toggle_item: "Toggle item completion status",
  action_list_reorder_items: "Reorder items in an action list",
};

/**
 * Register activation tools
 */
export function registerActivationFeatures(server: McpServer): void {
  logger.info("Registering activation tools");

  // General server activation tool
  server.registerTool(
    "activate_taskman_server",
    {
      title: "Activate TaskMan Server",
      description:
        "Check TaskMan API server status and prepare for operations. " +
        "This tool verifies the backend is running and returns startup instructions if needed. " +
        "Call this first before using any task, project, or action list tools.",
      inputSchema: {
        verbose: z
          .boolean()
          .optional()
          .describe("Include detailed status information"),
      },
      outputSchema: {
        serverStatus: z.object({
          serverOnline: z.boolean(),
          apiEndpoint: z.string(),
          latencyMs: z.number().nullable(),
          message: z.string(),
          startupInstructions: z.array(z.string()).optional(),
        }),
        allTools: z.object({
          tasks: z.array(z.string()),
          projects: z.array(z.string()),
          actionLists: z.array(z.string()),
        }),
        ready: z.boolean(),
      },
    },
    async ({ verbose }) => {
      logger.info("Activating TaskMan server");
      const serverStatus = await checkServerStatus();

      const result = {
        serverStatus,
        allTools: {
          tasks: Object.keys(TASK_TOOLS),
          projects: Object.keys(PROJECT_TOOLS),
          actionLists: Object.keys(ACTION_LIST_TOOLS),
        },
        ready: serverStatus.serverOnline,
        ...(verbose && {
          toolDescriptions: {
            tasks: TASK_TOOLS,
            projects: PROJECT_TOOLS,
            actionLists: ACTION_LIST_TOOLS,
          },
        }),
      };

      if (!serverStatus.serverOnline) {
        logger.warn("TaskMan server not online during activation");
      } else {
        logger.info("TaskMan server activation successful");
      }

      return asJson(result);
    }
  );

  // Task tools activation
  server.registerTool(
    "activate_task_tools",
    {
      title: "Activate Task Management Tools",
      description:
        "Check server status and prepare task management tools. " +
        "Returns available task tools and their descriptions. " +
        "If server is offline, provides startup instructions.",
      inputSchema: {},
      outputSchema: {
        activated: z.boolean(),
        serverStatus: z.object({
          serverOnline: z.boolean(),
          apiEndpoint: z.string(),
          latencyMs: z.number().nullable(),
          message: z.string(),
          startupInstructions: z.array(z.string()).optional(),
        }),
        availableTools: z.array(z.string()),
        toolDescriptions: z.record(z.string(), z.string()),
        nextSteps: z.array(z.string()).optional(),
      },
    },
    async () => {
      logger.info("Activating task management tools");
      const serverStatus = await checkServerStatus();

      const result: ToolActivationResult = {
        activated: serverStatus.serverOnline,
        serverStatus,
        availableTools: Object.keys(TASK_TOOLS),
        toolDescriptions: TASK_TOOLS,
      };

      if (serverStatus.serverOnline) {
        result.nextSteps = [
          "Task tools are ready to use!",
          "Common operations:",
          "  - Use task_list to view existing tasks",
          "  - Use task_create to create a new task",
          "  - Use task_search to find tasks by keyword",
        ];
        logger.info("Task tools activated successfully");
      } else {
        result.nextSteps = [
          "Server is offline. Please start it first:",
          ...(serverStatus.startupInstructions || []),
          "",
          "After starting, call activate_task_tools again to verify.",
        ];
        logger.warn("Task tools not available - server offline");
      }

      return asJson(result);
    }
  );

  // Project tools activation
  server.registerTool(
    "activate_project_tools",
    {
      title: "Activate Project Management Tools",
      description:
        "Check server status and prepare project management tools. " +
        "Returns available project tools including sprint, blocker, and comment management. " +
        "If server is offline, provides startup instructions.",
      inputSchema: {},
      outputSchema: {
        activated: z.boolean(),
        serverStatus: z.object({
          serverOnline: z.boolean(),
          apiEndpoint: z.string(),
          latencyMs: z.number().nullable(),
          message: z.string(),
          startupInstructions: z.array(z.string()).optional(),
        }),
        availableTools: z.array(z.string()),
        toolDescriptions: z.record(z.string(), z.string()),
        nextSteps: z.array(z.string()).optional(),
      },
    },
    async () => {
      logger.info("Activating project management tools");
      const serverStatus = await checkServerStatus();

      const result: ToolActivationResult = {
        activated: serverStatus.serverOnline,
        serverStatus,
        availableTools: Object.keys(PROJECT_TOOLS),
        toolDescriptions: PROJECT_TOOLS,
      };

      if (serverStatus.serverOnline) {
        result.nextSteps = [
          "Project tools are ready to use!",
          "Common operations:",
          "  - Use project_list to view existing projects",
          "  - Use project_create to create a new project",
          "  - Use project_analytics to get project statistics",
          "  - Use project_sprint_create to create sprints",
        ];
        logger.info("Project tools activated successfully");
      } else {
        result.nextSteps = [
          "Server is offline. Please start it first:",
          ...(serverStatus.startupInstructions || []),
          "",
          "After starting, call activate_project_tools again to verify.",
        ];
        logger.warn("Project tools not available - server offline");
      }

      return asJson(result);
    }
  );

  // Action list tools activation
  server.registerTool(
    "activate_action_list_tools",
    {
      title: "Activate Action List Tools",
      description:
        "Check server status and prepare action list management tools. " +
        "Returns available action list tools for creating and managing checklists. " +
        "If server is offline, provides startup instructions.",
      inputSchema: {},
      outputSchema: {
        activated: z.boolean(),
        serverStatus: z.object({
          serverOnline: z.boolean(),
          apiEndpoint: z.string(),
          latencyMs: z.number().nullable(),
          message: z.string(),
          startupInstructions: z.array(z.string()).optional(),
        }),
        availableTools: z.array(z.string()),
        toolDescriptions: z.record(z.string(), z.string()),
        nextSteps: z.array(z.string()).optional(),
      },
    },
    async () => {
      logger.info("Activating action list management tools");
      const serverStatus = await checkServerStatus();

      const result: ToolActivationResult = {
        activated: serverStatus.serverOnline,
        serverStatus,
        availableTools: Object.keys(ACTION_LIST_TOOLS),
        toolDescriptions: ACTION_LIST_TOOLS,
      };

      if (serverStatus.serverOnline) {
        result.nextSteps = [
          "Action list tools are ready to use!",
          "Common operations:",
          "  - Use action_list_list to view existing action lists",
          "  - Use action_list_create to create a new checklist",
          "  - Use action_list_add_item to add items",
          "  - Use action_list_toggle_item to mark items complete",
        ];
        logger.info("Action list tools activated successfully");
      } else {
        result.nextSteps = [
          "Server is offline. Please start it first:",
          ...(serverStatus.startupInstructions || []),
          "",
          "After starting, call activate_action_list_tools again to verify.",
        ];
        logger.warn("Action list tools not available - server offline");
      }

      return asJson(result);
    }
  );

  logger.info("Activation tools registered successfully", {
    tools: [
      "activate_taskman_server",
      "activate_task_tools",
      "activate_project_tools",
      "activate_action_list_tools",
    ],
  });
}
