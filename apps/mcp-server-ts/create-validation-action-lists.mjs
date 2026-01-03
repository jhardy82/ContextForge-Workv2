/**
 * Use ActionList MCP tools to create validation checklists for other MCP tool sets
 * CRITICAL: Set environment variable BEFORE any imports
 */

// Set environment variable BEFORE any imports
process.env.TASK_MANAGER_API_ENDPOINT = "http://localhost:3001/api/v1";

import { spawn } from "child_process";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log("=== Creating Validation Action Lists for TaskMan MCP Tools ===\n");

const serverPath = join(__dirname, "dist", "index.js");
const server = spawn("node", [serverPath], {
  env: {
    ...process.env,
    TASK_MANAGER_API_ENDPOINT: "http://localhost:3001/api/v1",
    TASKMAN_MCP_TRANSPORT: "stdio",
    // Disable circuit breaker for bootstrap scripts (one-off admin operations)
    CIRCUIT_BREAKER_ENABLED: "false",
    TASKMAN_DEBUG: "true",
  },
  stdio: ["pipe", "pipe", "pipe"],
});

let outputBuffer = "";
const pendingRequests = new Map();
let requestId = 1;

function sendRequest(method, params = {}) {
  const id = requestId++;
  const request = {
    jsonrpc: "2.0",
    id,
    method,
    params,
  };

  return new Promise((resolve, reject) => {
    pendingRequests.set(id, { resolve, reject, method });
    server.stdin.write(JSON.stringify(request) + "\n");

    setTimeout(() => {
      if (pendingRequests.has(id)) {
        pendingRequests.delete(id);
        reject(new Error(`Timeout waiting for response to ${method}`));
      }
    }, 10000);
  });
}

server.stderr.on("data", (data) => {
  const output = data.toString().trim();
  if (output && !output.includes("TaskMan MCP")) {
    console.error("[Server Error]", output);
  }
});

server.stdout.on("data", (data) => {
  outputBuffer += data.toString();

  const lines = outputBuffer.split("\n");
  outputBuffer = lines.pop() || "";

  for (const line of lines) {
    if (!line.trim()) continue;

    try {
      const response = JSON.parse(line);

      if (response.id && pendingRequests.has(response.id)) {
        const { resolve, reject } = pendingRequests.get(response.id);
        pendingRequests.delete(response.id);

        if (response.error) {
          reject(
            new Error(
              `MCP error ${response.error.code}: ${response.error.message}`
            )
          );
        } else {
          resolve(response.result);
        }
      }
    } catch (e) {
      // Not valid JSON, ignore
    }
  }
});

// Wait for server to initialize
await new Promise((resolve) => setTimeout(resolve, 2000));

function requireStructured(result, op) {
  if (!result?.structuredContent) {
    let errorMsg = `${op} did not return structuredContent. Raw result keys: ${Object.keys(
      result ?? {}
    ).join(", ")}`;

    // If there's an error in content, extract it
    if (result?.content && Array.isArray(result.content)) {
      const textContent = result.content.find((c) => c.type === "text")?.text;
      if (textContent) {
        errorMsg += `\nError content: ${textContent}`;
      }
    }

    throw new Error(errorMsg);
  }
  return result.structuredContent;
}

async function callTool(name, args = {}) {
  return sendRequest("tools/call", { name, arguments: args });
}

async function getOrCreateProject({ name, description, status }) {
  const list = await callTool("project_list", { search: name, limit: 100 });
  const { projects } = requireStructured(list, "project_list");
  const existing = (projects ?? []).find((p) => p?.name === name);
  if (existing) {
    console.log(`ℹ️  Reusing existing project: ${existing.id}`);
    return existing;
  }

  const created = await callTool("project_create", {
    project: {
      name,
      description,
      status,
    },
  });
  const { project } = requireStructured(created, "project_create");
  return project;
}

async function getExistingActionLists(projectId) {
  console.log(`  🔍 Calling action_list_list for project ${projectId}...`);
  const list = await callTool("action_list_list", {
    project_id: projectId,
    limit: 100,
  });
  console.log(
    `  📦 action_list_list response:`,
    JSON.stringify(list).substring(0, 200)
  );
  const { action_lists } = requireStructured(list, "action_list_list");
  console.log(`  ✅ Got ${action_lists?.length ?? 0} action lists`);
  return action_lists ?? [];
}

async function getOrCreateActionList(
  projectId,
  { title, description, status, priority, notes }
) {
  const existingLists = await getExistingActionLists(projectId);
  const existing = existingLists.find((l) => l?.title === title);
  if (existing) {
    console.log(`ℹ️  Reusing existing action list: ${existing.id} (${title})`);
    return existing;
  }

  const created = await callTool("action_list_create", {
    title,
    description,
    status,
    priority,
    project_id: projectId,
    notes,
  });
  const { action_list } = requireStructured(created, "action_list_create");
  return action_list;
}

async function createValidationActionLists() {
  try {
    // Create/reuse a project for validation tasks
    console.log("Creating project for MCP validation tasks...");
    const project = await getOrCreateProject({
      name: "TaskMan MCP Tool Validation",
      description: "Systematic validation of all TaskMan MCP tools",
      status: "active",
    });
    console.log(`✅ Project ready: ${project.id}\n`);

    const actionLists = [];

    // 1. Create action list for Project MCP tools validation
    console.log("Creating action list for Project MCP tools...");
    const projectToolsList = await getOrCreateActionList(project.id, {
      title: "Project MCP Tools Validation",
      description:
        "Comprehensive validation checklist for all Project-related MCP tools",
      status: "active",
      priority: "high",
      notes: "Test all project CRUD operations and analytics",
    });
    const projectListId = projectToolsList.id;
    actionLists.push({ name: "Project Tools", id: projectListId });
    console.log(`✅ Created: ${projectListId}\n`);

    // Add items to Project tools list
    const projectItems = [
      "Test project_create - Create new project with all fields",
      "Test project_read - Retrieve project by ID",
      "Test project_list - List projects with filters (status, owner)",
      "Test project_update - Update project properties (name, description, status)",
      "Test project_delete - Delete project",
      "Test project_analytics - Get project analytics and statistics",
      "Verify foreign key relationships (cascading to tasks, action lists)",
      "Test error handling (404 for missing project, 422 for invalid data)",
    ];

    console.log(`Adding ${projectItems.length} items to Project tools list...`);
    for (let i = 0; i < projectItems.length; i++) {
      const result = await callTool("action_list_add_item", {
        action_list_id: projectListId,
        text: projectItems[i],
        order: i + 1,
      });
      // Log the result to see if these are failing
      console.log(
        `  [${i + 1}/${projectItems.length}] Result:`,
        JSON.stringify(result).substring(0, 150)
      );
    }
    console.log(`✅ Added ${projectItems.length} items\n`);

    // 2. Create action list for Task MCP tools validation
    console.log("Creating action list for Task MCP tools...");
    const taskToolsList = await getOrCreateActionList(project.id, {
      title: "Task MCP Tools Validation",
      description:
        "Comprehensive validation checklist for all Task-related MCP tools",
      status: "active",
      priority: "high",
      notes: "Test all task CRUD operations, mutations, and queries",
    });
    const taskListId = taskToolsList.id;
    actionLists.push({ name: "Task Tools", id: taskListId });
    console.log(`✅ Created: ${taskListId}\n`);

    // Add items to Task tools list
    const taskItems = [
      "Test task_create - Create new task with all fields",
      "Test task_read - Retrieve task by ID",
      "Test task_list - List tasks with filters (status, project, sprint, assignee)",
      "Test task_update - Update task properties (title, description, status)",
      "Test task_delete - Delete task",
      "Test task_search - Search tasks by keyword",
      "Test task_assign - Assign task to user",
      "Test task_set_status - Change task status",
      "Test task_add_comment - Add comment to task",
      "Test task_add_tag - Add tag to task",
      "Test task_bulk_update - Bulk update multiple tasks",
      "Verify relationships (project_id, sprint_id, parent_task_id)",
      "Test error handling (404, 422, validation errors)",
    ];

    console.log(`Adding ${taskItems.length} items to Task tools list...`);
    for (let i = 0; i < taskItems.length; i++) {
      const result = await callTool("action_list_add_item", {
        action_list_id: taskListId,
        text: taskItems[i],
        order: i + 1,
      });
      // Log the result to see if these are failing
      console.log(
        `  [${i + 1}/${taskItems.length}] Result:`,
        JSON.stringify(result).substring(0, 150)
      );
    }
    console.log(`✅ Added ${taskItems.length} items\n`);

    // 3. Create action list for Sprint MCP tools validation (if sprints exist)
    console.log("Creating action list for Sprint MCP tools (if available)...");
    const sprintToolsList = await getOrCreateActionList(project.id, {
      title: "Sprint MCP Tools Validation",
      description:
        "Comprehensive validation checklist for all Sprint-related MCP tools (if implemented)",
      status: "active",
      priority: "medium",
      notes: "Test sprint CRUD operations if sprint tools exist",
    });
    const sprintListId = sprintToolsList.id;
    actionLists.push({ name: "Sprint Tools", id: sprintListId });
    console.log(`✅ Created: ${sprintListId}\n`);

    // Add items to Sprint tools list
    const sprintItems = [
      "Verify sprint tools exist in MCP registration",
      "Test sprint_create - Create new sprint",
      "Test sprint_read - Retrieve sprint by ID",
      "Test sprint_list - List sprints for project",
      "Test sprint_update - Update sprint properties",
      "Test sprint_delete - Delete sprint",
      "Test sprint_add_task - Add task to sprint",
      "Test sprint_remove_task - Remove task from sprint",
      "Verify sprint-task relationships",
    ];

    console.log(`Adding ${sprintItems.length} items to Sprint tools list...`);
    for (let i = 0; i < sprintItems.length; i++) {
      await callTool("action_list_add_item", {
        action_list_id: sprintListId,
        text: sprintItems[i],
        order: i + 1,
      });
    }
    console.log(`✅ Added ${sprintItems.length} items\n`);

    // 4. Create action list for Integration testing
    console.log("Creating action list for Integration testing...");
    const integrationList = await getOrCreateActionList(project.id, {
      title: "Cross-Feature Integration Validation",
      description:
        "End-to-end testing across Projects, Tasks, Action Lists, and Sprints",
      status: "active",
      priority: "critical",
      notes: "Validate complete workflows using multiple MCP tool families",
    });
    const integrationListId = integrationList.id;
    actionLists.push({ name: "Integration", id: integrationListId });
    console.log(`✅ Created: ${integrationListId}\n`);

    // Add items to Integration list
    const integrationItems = [
      "Create project → Create tasks → Create action list → Link all together",
      "Create sprint → Assign tasks to sprint → Track progress",
      "Update task status → Verify action list progress updates",
      "Delete project → Verify cascade delete of tasks and action lists",
      "Bulk create tasks → Assign to multiple sprints → Update statuses",
      "Test concurrent updates with locking mechanism",
      "Verify audit logging across all operations",
      "Test error propagation across feature boundaries",
      "Validate data consistency after complex workflows",
      "Performance test: Create 100 tasks, 10 action lists, measure latency",
    ];

    console.log(
      `Adding ${integrationItems.length} items to Integration list...`
    );
    for (let i = 0; i < integrationItems.length; i++) {
      await callTool("action_list_add_item", {
        action_list_id: integrationListId,
        text: integrationItems[i],
        order: i + 1,
      });
    }
    console.log(`✅ Added ${integrationItems.length} items\n`);

    // Summary
    console.log("=".repeat(60));
    console.log("SUMMARY: Validation Action Lists Created");
    console.log("=".repeat(60));
    console.log(`Project: ${project.name} (${project.id})`);
    console.log(`\nAction Lists Created: ${actionLists.length}`);
    actionLists.forEach((list, index) => {
      console.log(`  ${index + 1}. ${list.name} (${list.id})`);
    });
    console.log(
      `\nTotal Validation Items: ${
        projectItems.length +
        taskItems.length +
        sprintItems.length +
        integrationItems.length
      }`
    );
    console.log(`\nNext Steps:`);
    console.log(
      `  1. Use action_list_list to view all lists: { project_id: "${project.id}" }`
    );
    console.log(
      `  2. Use action_list_read to view specific list: { action_list_id: "<id>" }`
    );
    console.log(
      `  3. Use action_list_toggle_item to mark items complete as you validate each tool`
    );
    console.log(
      `  4. Track progress via progress_percentage field in each action list`
    );

    server.kill();
    process.exit(0);
  } catch (error) {
    console.error("\n❌ Fatal Error:", error.message);
    if (error.stack) {
      console.error("\nStack trace:");
      console.error(error.stack);
    }
    server.kill();
    process.exit(1);
  }
}

createValidationActionLists();
