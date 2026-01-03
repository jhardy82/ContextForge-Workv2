/**
 * PRODUCTION: Comprehensive Task MCP Tools Validation
 *
 * Validates all 10 Task MCP tools with Action List progress tracking
 * Fixes applied:
 * - AUDIT log filtering (critical)
 * - Proper response structure handling
 * - Environment variable before imports
 * - Comprehensive error handling
 */

// CRITICAL: Set environment variable BEFORE any imports
process.env.TASK_MANAGER_API_ENDPOINT = "http://localhost:3001/api/v1";

import { spawn } from "child_process";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log("╔════════════════════════════════════════════════════════════════════╗");
console.log("║      Task MCP Tools Validation - Production Execution             ║");
console.log("╚════════════════════════════════════════════════════════════════════╝\n");

const serverPath = join(__dirname, "dist", "index.js");
const server = spawn("node", [serverPath], {
  env: {
    ...process.env,
    TASK_MANAGER_API_ENDPOINT: "http://localhost:3001/api/v1",
    TASKMAN_MCP_TRANSPORT: "stdio",
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
    }, 15000);
  });
}

server.stderr.on("data", (data) => {
  // Silent - only show errors in final report
});

server.stdout.on("data", (data) => {
  outputBuffer += data.toString();
  const lines = outputBuffer.split("\n");
  outputBuffer = lines.pop() || "";

  for (const line of lines) {
    if (!line.trim()) continue;

    // CRITICAL: Filter out AUDIT logs
    if (line.includes('[AUDIT]')) continue;

    try {
      const response = JSON.parse(line);

      if (response.id && pendingRequests.has(response.id)) {
        const { resolve, reject } = pendingRequests.get(response.id);
        pendingRequests.delete(response.id);

        if (response.error) {
          reject(new Error(`MCP error ${response.error.code}: ${response.error.message}`));
        } else {
          resolve(response.result);
        }
      }
    } catch (e) {
      // Not valid JSON, ignore
    }
  }
});

await new Promise(resolve => setTimeout(resolve, 2000));

// Configuration
const ACTION_LIST_ID = "AL-c3748b54";
const PROJECT_ID = "P-8767f2bc";

// Item IDs for tools that actually exist
const ITEM_IDS = {
  task_create: "item-6c4cb335",
  task_read: "item-2d432c9e",
  task_list: "item-59a0aa3a",
  task_update: "item-69164f8c",
  task_delete: "item-220a79a4",
  task_search: "item-aa3a1a1d",
  task_assign: "item-b13816eb",
  task_set_status: "item-57728131",
  task_bulk_update: "item-5b30279f",
  relationships: "item-61bd3fe2",
  error_handling: "item-ed8d3f22",
};

const results = {
  passed: 0,
  failed: 0,
  skipped: 0,
  tests: [],
  startTime: new Date(),
};

let testTaskId = null;
let testTaskIds = [];
let testSprintId = null;
let childTaskId = null;

function recordTest(name, success, error = null, itemId = null) {
  results.tests.push({ name, success, error: error?.message, itemId });
  if (success) {
    results.passed++;
    console.log(`✅ ${name}`);
  } else if (error && error.message.includes("SKIP")) {
    results.skipped++;
    console.log(`⏭️  ${name}`);
  } else {
    results.failed++;
    console.log(`❌ ${name}`);
    if (error) console.log(`   Error: ${error.message.substring(0, 100)}`);
  }
}

async function toggleItem(itemId, testName) {
  if (!itemId) return;

  try {
    await sendRequest("tools/call", {
      name: "action_list_toggle_item",
      arguments: {
        action_list_id: ACTION_LIST_ID,
        item_id: itemId
      }
    });
    console.log(`   📝 Marked complete in action list\n`);
  } catch (error) {
    console.log(`   ⚠️  Action list update failed: ${error.message}\n`);
  }
}

async function executeValidation() {
  try {
    const { backendClient } = await import("./dist/backend/client.js");

    console.log("Initializing...");
    const project = await backendClient.getProject(PROJECT_ID);
    console.log(`✅ Project: ${project.name}\n`);

    // PHASE 1: Core CRUD
    console.log("═══════════════════════════════════════════════════════════════════");
    console.log(" PHASE 1: Core CRUD Operations (5 tools)");
    console.log("═══════════════════════════════════════════════════════════════════\n");

    // Test 1: task_create
    try {
      const result = await sendRequest("tools/call", {
        name: "task_create",
        arguments: {
          task: {
            title: "Task Validation Test - Comprehensive",
            description: "Testing all Task MCP tools systematically",
            project_id: PROJECT_ID,
            status: "new",
            work_type: "task",
            priority: "high",
            owner: "ValidationScript",
            tags: ["validation", "mcp-test", "automated"],
            estimated_hours: 3.0,
            notes: "Created via comprehensive validation script"
          }
        }
      });

      if (result?.structuredContent?.task) {
        testTaskId = result.structuredContent.task.id;
        recordTest("task_create", true, null, ITEM_IDS.task_create);
        await toggleItem(ITEM_IDS.task_create, "task_create");
      } else {
        throw new Error("Invalid response structure");
      }
    } catch (error) {
      recordTest("task_create", false, error, ITEM_IDS.task_create);
      throw new Error("Cannot continue without test task");
    }

    // Test 2: task_read
    try {
      const result = await sendRequest("tools/call", {
        name: "task_read",
        arguments: { taskId: testTaskId }
      });

      if (result?.structuredContent?.task?.id === testTaskId) {
        recordTest("task_read", true, null, ITEM_IDS.task_read);
        await toggleItem(ITEM_IDS.task_read, "task_read");
      } else {
        throw new Error("Task ID mismatch");
      }
    } catch (error) {
      recordTest("task_read", false, error, ITEM_IDS.task_read);
    }

    // Test 3: task_list
    try {
      const result = await sendRequest("tools/call", {
        name: "task_list",
        arguments: { project_id: PROJECT_ID, status: "new" }
      });

      const tasks = result?.structuredContent?.tasks;
      if (Array.isArray(tasks) && tasks.find(t => t.id === testTaskId)) {
        recordTest("task_list", true, null, ITEM_IDS.task_list);
        await toggleItem(ITEM_IDS.task_list, "task_list");
      } else {
        throw new Error("Task not found in filtered list");
      }
    } catch (error) {
      recordTest("task_list", false, error, ITEM_IDS.task_list);
    }

    // Test 4: task_update
    try {
      const result = await sendRequest("tools/call", {
        name: "task_update",
        arguments: {
          taskId: testTaskId,
          changes: {
            title: "UPDATED: Task Validation Test",
            priority: "critical",
            estimated_hours: 5.0,
            tags: ["validation", "mcp-test", "automated", "updated"]
          }
        }
      });

      const task = result?.structuredContent?.task;
      if (task?.title === "UPDATED: Task Validation Test" && task?.priority === "critical") {
        recordTest("task_update", true, null, ITEM_IDS.task_update);
        await toggleItem(ITEM_IDS.task_update, "task_update");
      } else {
        throw new Error("Update not applied correctly");
      }
    } catch (error) {
      recordTest("task_update", false, error, ITEM_IDS.task_update);
    }

    // PHASE 2: Search
    console.log("\n═══════════════════════════════════════════════════════════════════");
    console.log(" PHASE 2: Search Operations (1 tool)");
    console.log("═══════════════════════════════════════════════════════════════════\n");

    // Test 5: task_search
    try {
      const result = await sendRequest("tools/call", {
        name: "task_search",
        arguments: { query: "Validation Test", project_id: PROJECT_ID }
      });

      const tasks = result?.structuredContent?.tasks;
      if (result?.structuredContent?.success && Array.isArray(tasks) && tasks.find(t => t.id === testTaskId)) {
        recordTest("task_search", true, null, ITEM_IDS.task_search);
        await toggleItem(ITEM_IDS.task_search, "task_search");
      } else {
        throw new Error("Search didn't find test task");
      }
    } catch (error) {
      recordTest("task_search", false, error, ITEM_IDS.task_search);
    }

    // PHASE 3: Specialized
    console.log("\n═══════════════════════════════════════════════════════════════════");
    console.log(" PHASE 3: Specialized Operations (2 tools)");
    console.log("═══════════════════════════════════════════════════════════════════\n");

    // Test 6: task_assign
    try {
      const result = await sendRequest("tools/call", {
        name: "task_assign",
        arguments: { taskId: testTaskId, assignee: "ValidationUser" }
      });

      if (result?.structuredContent?.task?.assignee === "ValidationUser") {
        recordTest("task_assign", true, null, ITEM_IDS.task_assign);
        await toggleItem(ITEM_IDS.task_assign, "task_assign");
      } else {
        throw new Error("Assignee not set");
      }
    } catch (error) {
      recordTest("task_assign", false, error, ITEM_IDS.task_assign);
    }

    // Test 7: task_set_status
    try {
      const result = await sendRequest("tools/call", {
        name: "task_set_status",
        arguments: {
          taskId: testTaskId,
          status: "in_progress",
          notes: "Validation in progress"
        }
      });

      if (result?.structuredContent?.task?.status === "in_progress") {
        recordTest("task_set_status", true, null, ITEM_IDS.task_set_status);
        await toggleItem(ITEM_IDS.task_set_status, "task_set_status");
      } else {
        throw new Error("Status not updated");
      }
    } catch (error) {
      recordTest("task_set_status", false, error, ITEM_IDS.task_set_status);
    }

    // PHASE 4: Bulk Operations
    console.log("\n═══════════════════════════════════════════════════════════════════");
    console.log(" PHASE 4: Bulk Operations (2 tools)");
    console.log("═══════════════════════════════════════════════════════════════════\n");

    // Create test tasks for bulk operations
    console.log("Creating 3 test tasks for bulk operations...");
    for (let i = 1; i <= 3; i++) {
      try {
        const result = await sendRequest("tools/call", {
          name: "task_create",
          arguments: {
            task: {
              title: `Bulk Test Task ${i}`,
              project_id: PROJECT_ID,
              status: "new",
              work_type: "task",
              priority: "medium"
            }
          }
        });
        if (result?.structuredContent?.task) {
          testTaskIds.push(result.structuredContent.task.id);
        }
      } catch (error) {
        console.log(`⚠️  Failed to create bulk test task ${i}`);
      }
    }
    console.log(`✅ Created ${testTaskIds.length} tasks\n`);

    // Test 8: task_bulk_update
    try {
      if (testTaskIds.length === 0) throw new Error("SKIP: No bulk test tasks");

      const result = await sendRequest("tools/call", {
        name: "task_bulk_update",
        arguments: {
          taskIds: testTaskIds,
          changes: { priority: "high", tags: ["bulk-updated"] }
        }
      });

      if (result?.structuredContent?.success && result.structuredContent.updated_count === testTaskIds.length) {
        recordTest("task_bulk_update", true, null, ITEM_IDS.task_bulk_update);
        await toggleItem(ITEM_IDS.task_bulk_update, "task_bulk_update");
      } else {
        throw new Error("Bulk update count mismatch");
      }
    } catch (error) {
      recordTest("task_bulk_update", false, error, ITEM_IDS.task_bulk_update);
    }

    // Test 9: task_bulk_assign_sprint
    try {
      // Create sprint
      const sprint = await backendClient.createSprint({
        name: "Validation Sprint",
        project_id: PROJECT_ID,
        status: "active"
      });
      testSprintId = sprint.id;
      console.log(`   Created sprint: ${testSprintId}`);

      if (testTaskIds.length === 0) throw new Error("SKIP: No bulk test tasks");

      const result = await sendRequest("tools/call", {
        name: "task_bulk_assign_sprint",
        arguments: { taskIds: testTaskIds, sprintId: testSprintId }
      });

      if (result?.structuredContent?.success && result.structuredContent.assigned_count === testTaskIds.length) {
        recordTest("task_bulk_assign_sprint", true);
      } else {
        throw new Error("Bulk sprint assignment count mismatch");
      }
    } catch (error) {
      recordTest("task_bulk_assign_sprint", false, error);
    }

    // PHASE 5: Integration
    console.log("\n═══════════════════════════════════════════════════════════════════");
    console.log(" PHASE 5: Integration & Error Handling");
    console.log("═══════════════════════════════════════════════════════════════════\n");

    // Test 10: Relationships
    try {
      const result = await sendRequest("tools/call", {
        name: "task_create",
        arguments: {
          task: {
            title: "Child Task",
            project_id: PROJECT_ID,
            status: "new",
            work_type: "task",
            parent_task_id: testTaskId
          }
        }
      });

      if (result?.structuredContent?.task?.parent_task_id === testTaskId) {
        childTaskId = result.structuredContent.task.id;
        recordTest("Relationships (parent-child)", true, null, ITEM_IDS.relationships);
        await toggleItem(ITEM_IDS.relationships, "Relationships");
      } else {
        throw new Error("Parent relationship not set");
      }
    } catch (error) {
      recordTest("Relationships (parent-child)", false, error, ITEM_IDS.relationships);
    }

    // Test 11: Error Handling
    try {
      let errorsPassed = 0;

      // Test 404
      try {
        await sendRequest("tools/call", {
          name: "task_read",
          arguments: { taskId: "T-nonexist" }
        });
      } catch {
        errorsPassed++;
      }

      // Test validation error
      try {
        await sendRequest("tools/call", {
          name: "task_create",
          arguments: { task: { description: "Missing title" } }
        });
      } catch {
        errorsPassed++;
      }

      // Test empty update
      try {
        await sendRequest("tools/call", {
          name: "task_update",
          arguments: { taskId: testTaskId, changes: {} }
        });
      } catch {
        errorsPassed++;
      }

      if (errorsPassed === 3) {
        recordTest("Error Handling (3 scenarios)", true, null, ITEM_IDS.error_handling);
        await toggleItem(ITEM_IDS.error_handling, "Error handling");
      } else {
        throw new Error(`Only ${errorsPassed}/3 error tests passed`);
      }
    } catch (error) {
      recordTest("Error Handling (3 scenarios)", false, error, ITEM_IDS.error_handling);
    }

    // Test 12: task_delete (cleanup)
    console.log("\n═══════════════════════════════════════════════════════════════════");
    console.log(" CLEANUP: Delete Test Tasks");
    console.log("═══════════════════════════════════════════════════════════════════\n");

    try {
      const tasksToDelete = [testTaskId, childTaskId, ...testTaskIds].filter(Boolean);
      let deletedCount = 0;

      for (const taskId of tasksToDelete) {
        try {
          const result = await sendRequest("tools/call", {
            name: "task_delete",
            arguments: { taskId }
          });
          if (result?.structuredContent?.deleted) deletedCount++;
        } catch (error) {
          console.log(`   ⚠️  Failed to delete ${taskId}`);
        }
      }

      if (deletedCount === tasksToDelete.length) {
        recordTest("task_delete (cleanup)", true, null, ITEM_IDS.task_delete);
        await toggleItem(ITEM_IDS.task_delete, "task_delete");
      } else {
        throw new Error(`Only deleted ${deletedCount}/${tasksToDelete.length} tasks`);
      }
    } catch (error) {
      recordTest("task_delete (cleanup)", false, error, ITEM_IDS.task_delete);
    }

    // SUMMARY
    console.log("\n╔════════════════════════════════════════════════════════════════════╗");
    console.log("║                      VALIDATION SUMMARY                            ║");
    console.log("╚════════════════════════════════════════════════════════════════════╝\n");

    const total = results.passed + results.failed + results.skipped;
    const successRate = results.failed === 0 ? 100 : ((results.passed / (results.passed + results.failed)) * 100).toFixed(1);

    console.log(`Total Tests:    ${total}`);
    console.log(`✅ Passed:      ${results.passed}`);
    console.log(`❌ Failed:      ${results.failed}`);
    console.log(`⏭️  Skipped:     ${results.skipped}`);
    console.log(`Success Rate:   ${successRate}%`);
    console.log(`Duration:       ${Math.round((new Date() - results.startTime) / 1000)}s`);

    if (results.failed > 0) {
      console.log("\nFailed Tests:");
      results.tests.filter(t => !t.success && !t.error?.includes("SKIP")).forEach(t => {
        console.log(`  ❌ ${t.name}`);
      });
    }

    // Read final action list state
    const finalList = await sendRequest("tools/call", {
      name: "action_list_read",
      arguments: { action_list_id: ACTION_LIST_ID }
    });

    const list = finalList.structuredContent.action_list;
    console.log("\n╔════════════════════════════════════════════════════════════════════╗");
    console.log("║                   ACTION LIST PROGRESS                             ║");
    console.log("╚════════════════════════════════════════════════════════════════════╝\n");
    console.log(`List: ${list.name}`);
    console.log(`Progress: ${list.completed_items}/${list.total_items} items (${list.progress_percentage}%)`);
    console.log("\nCompleted Items:");
    list.items.filter(item => item.completed).forEach(item => {
      console.log(`  ☑ ${item.text}`);
    });

    server.kill();
    process.exit(results.failed === 0 ? 0 : 1);

  } catch (error) {
    console.error("\n❌ FATAL ERROR:", error.message);
    server.kill();
    process.exit(1);
  }
}

executeValidation();
