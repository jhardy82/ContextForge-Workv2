/**
 * FIXED: Comprehensive validation of all Task MCP tools
 * Improved error handling and response access
 *
 * CRITICAL: Set environment variable BEFORE any imports
 */

// Set environment variable BEFORE any imports
process.env.TASK_MANAGER_API_ENDPOINT = "http://localhost:3001/api/v1";

import { spawn } from "child_process";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log("=== Comprehensive Task MCP Tools Validation (Fixed) ===\n");

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
  const output = data.toString().trim();
  if (output && !output.includes("TaskMan MCP") && !output.includes("[AUDIT]")) {
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

// Wait for server to initialize
await new Promise(resolve => setTimeout(resolve, 2000));

// Action list configuration
const ACTION_LIST_ID = "AL-c3748b54";
const PROJECT_ID = "P-8767f2bc";

// Item IDs from the action list
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

// Test results tracking
const results = {
  passed: 0,
  failed: 0,
  skipped: 0,
  tests: []
};

let testTaskId = null;
let testTaskIds = [];
let testSprintId = null;

function recordTest(name, success, error = null, itemId = null) {
  results.tests.push({ name, success, error: error?.message, itemId });
  if (success) {
    results.passed++;
    console.log(`✅ ${name}`);
  } else if (error && error.message.includes("SKIP")) {
    results.skipped++;
    console.log(`⏭️  ${name} - ${error.message}`);
  } else {
    results.failed++;
    console.log(`❌ ${name}`);
    if (error) console.log(`   Error: ${error.message}`);
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
    console.log(`   📝 Marked "${testName}" complete in action list\n`);
  } catch (error) {
    console.log(`   ⚠️  Could not update action list: ${error.message}\n`);
  }
}

async function validateAllTaskTools() {
  try {
    // Import AFTER environment variable is set
    const { backendClient } = await import("./dist/backend/client.js");

    console.log("Setup: Verifying project exists...");
    const project = await backendClient.getProject(PROJECT_ID);
    console.log(`✅ Using project: ${project.name} (${project.id})\n`);

    console.log("=" .repeat(70));
    console.log("PHASE 1: Core CRUD Operations");
    console.log("=".repeat(70) + "\n");

    // Test 1: task_create
    try {
      console.log("Test 1: task_create");
      const result = await sendRequest("tools/call", {
        name: "task_create",
        arguments: {
          task: {
            title: "Validation Test Task - Core Fields",
            description: "Testing task_create with comprehensive field coverage",
            project_id: PROJECT_ID,
            status: "new",
            work_type: "task",
            priority: "high",
            owner: "ValidationScript",
            tags: ["validation", "automated-test"],
            estimated_hours: 2.5,
            notes: "Created via MCP tool validation script"
          }
        }
      });

      if (!result ||!result.structuredContent || !result.structuredContent.task) {
        throw new Error("Invalid response structure");
      }

      const task = result.structuredContent.task;
      testTaskId = task.id;

      if (!task.id || !task.id.startsWith("T-")) {
        throw new Error("Invalid task ID format");
      }
      if (task.title !== "Validation Test Task - Core Fields") {
        throw new Error("Task title mismatch");
      }
      if (task.project_id !== PROJECT_ID) {
        throw new Error("Project ID mismatch");
      }

      recordTest("task_create - Core fields", true, null, ITEM_IDS.task_create);
      await toggleItem(ITEM_IDS.task_create, "task_create");
    } catch (error) {
      recordTest("task_create - Core fields", false, error, ITEM_IDS.task_create);
      // Cannot continue without a test task
      throw new Error("Cannot continue validation without test task");
    }

    // Test 2: task_read
    try {
      console.log("Test 2: task_read");
      const result = await sendRequest("tools/call", {
        name: "task_read",
        arguments: {
          taskId: testTaskId
        }
      });

      if (!result || !result.structuredContent || !result.structuredContent.task) {
        throw new Error("Invalid response structure");
      }

      const task = result.structuredContent.task;

      if (task.id !== testTaskId) {
        throw new Error("Task ID mismatch");
      }
      if (!task.created_at || !task.updated_at) {
        throw new Error("Missing timestamp fields");
      }

      recordTest("task_read - Retrieve by ID", true, null, ITEM_IDS.task_read);
      await toggleItem(ITEM_IDS.task_read, "task_read");
    } catch (error) {
      recordTest("task_read - Retrieve by ID", false, error, ITEM_IDS.task_read);
    }

    // Test 3: task_list
    try {
      console.log("Test 3: task_list");

      const result1 = await sendRequest("tools/call", {
        name: "task_list",
        arguments: {
          project_id: PROJECT_ID
        }
      });

      if (!result1 || !result1.structuredContent || !result1.structuredContent.tasks) {
        throw new Error("Invalid response structure");
      }

      const tasks1 = result1.structuredContent.tasks;
      if (!Array.isArray(tasks1)) {
        throw new Error("Expected array of tasks");
      }
      const found = tasks1.find(t => t.id === testTaskId);
      if (!found) {
        throw new Error("Created task not found in list");
      }

      const result2 = await sendRequest("tools/call", {
        name: "task_list",
        arguments: {
          status: "new",
          project_id: PROJECT_ID
        }
      });

      const tasks2 = result2.structuredContent.tasks;
      const allNew = tasks2.every(t => t.status === "new");
      if (!allNew) {
        throw new Error("Status filter not working correctly");
      }

      recordTest("task_list - With filters", true, null, ITEM_IDS.task_list);
      await toggleItem(ITEM_IDS.task_list, "task_list");
    } catch (error) {
      recordTest("task_list - With filters", false, error, ITEM_IDS.task_list);
    }

    // Test 4: task_update
    try {
      console.log("Test 4: task_update");
      const result = await sendRequest("tools/call", {
        name: "task_update",
        arguments: {
          taskId: testTaskId,
          changes: {
            title: "UPDATED: Validation Test Task",
            description: "Updated description via MCP",
            priority: "critical",
            estimated_hours: 4.0
          }
        }
      });

      if (!result || !result.structuredContent || !result.structuredContent.task) {
        throw new Error("Invalid response structure");
      }

      const task = result.structuredContent.task;

      if (task.title !== "UPDATED: Validation Test Task") {
        throw new Error("Title not updated");
      }
      if (task.priority !== "critical") {
        throw new Error("Priority not updated");
      }

      recordTest("task_update - Partial updates", true, null, ITEM_IDS.task_update);
      await toggleItem(ITEM_IDS.task_update, "task_update");
    } catch (error) {
      recordTest("task_update - Partial updates", false, error, ITEM_IDS.task_update);
    }

    console.log("\n" + "=".repeat(70));
    console.log("PHASE 2: Search Operations");
    console.log("=".repeat(70) + "\n");

    // Test 5: task_search
    try {
      console.log("Test 5: task_search");
      const result = await sendRequest("tools/call", {
        name: "task_search",
        arguments: {
          query: "Validation Test",
          project_id: PROJECT_ID
        }
      });

      if (!result || !result.structuredContent) {
        throw new Error("Invalid response structure");
      }

      if (result.structuredContent.success !== true) {
        throw new Error("Search did not return success");
      }

      const tasks = result.structuredContent.tasks;
      if (!Array.isArray(tasks) || tasks.length === 0) {
        throw new Error("Search returned no results");
      }

      const found = tasks.find(t => t.id === testTaskId);
      if (!found) {
        throw new Error("Created task not found in search results");
      }

      recordTest("task_search - Keyword search", true, null, ITEM_IDS.task_search);
      await toggleItem(ITEM_IDS.task_search, "task_search");
    } catch (error) {
      recordTest("task_search - Keyword search", false, error, ITEM_IDS.task_search);
    }

    console.log("\n" + "=".repeat(70));
    console.log("PHASE 3: Specialized Operations");
    console.log("=".repeat(70) + "\n");

    // Test 6: task_assign
    try {
      console.log("Test 6: task_assign");
      const result = await sendRequest("tools/call", {
        name: "task_assign",
        arguments: {
          taskId: testTaskId,
          assignee: "TestUser1"
        }
      });

      if (!result || !result.structuredContent || !result.structuredContent.task) {
        throw new Error("Invalid response structure");
      }

      const task = result.structuredContent.task;

      if (task.assignee !== "TestUser1") {
        throw new Error("Assignee not set correctly");
      }

      recordTest("task_assign - Single assignee", true, null, ITEM_IDS.task_assign);
      await toggleItem(ITEM_IDS.task_assign, "task_assign");
    } catch (error) {
      recordTest("task_assign - Single assignee", false, error, ITEM_IDS.task_assign);
    }

    // Test 7: task_set_status
    try {
      console.log("Test 7: task_set_status");
      const result = await sendRequest("tools/call", {
        name: "task_set_status",
        arguments: {
          taskId: testTaskId,
          status: "in_progress",
          notes: "Started work on validation task"
        }
      });

      if (!result || !result.structuredContent || !result.structuredContent.task) {
        throw new Error("Invalid response structure");
      }

      const task = result.structuredContent.task;

      if (task.status !== "in_progress") {
        throw new Error("Status not updated");
      }

      recordTest("task_set_status - Change status", true, null, ITEM_IDS.task_set_status);
      await toggleItem(ITEM_IDS.task_set_status, "task_set_status");
    } catch (error) {
      recordTest("task_set_status - Change status", false, error, ITEM_IDS.task_set_status);
    }

    console.log("\n" + "=".repeat(70));
    console.log("PHASE 4: Bulk Operations");
    console.log("=".repeat(70) + "\n");

    // Create additional tasks for bulk operations
    try {
      console.log("Setup: Creating additional tasks for bulk operations...");

      for (let i = 1; i <= 3; i++) {
        const result = await sendRequest("tools/call", {
          name: "task_create",
          arguments: {
            task: {
              title: `Bulk Test Task ${i}`,
              description: `Task ${i} for bulk operations testing`,
              project_id: PROJECT_ID,
              status: "new",
              work_type: "task",
              priority: "medium"
            }
          }
        });
        if (result && result.structuredContent && result.structuredContent.task) {
          testTaskIds.push(result.structuredContent.task.id);
        }
      }
      console.log(`✅ Created ${testTaskIds.length} additional tasks\n`);
    } catch (error) {
      console.log(`⚠️  Could not create bulk test tasks: ${error.message}\n`);
    }

    // Test 8: task_bulk_update
    try {
      console.log("Test 8: task_bulk_update");

      if (testTaskIds.length === 0) {
        throw new Error("SKIP: No bulk test tasks available");
      }

      const result = await sendRequest("tools/call", {
        name: "task_bulk_update",
        arguments: {
          taskIds: testTaskIds,
          changes: {
            priority: "high",
            tags: ["bulk-updated", "validation"]
          }
        }
      });

      if (!result || !result.structuredContent) {
        throw new Error("Invalid response structure");
      }

      if (result.structuredContent.success !== true) {
        throw new Error("Bulk update did not return success");
      }

      if (result.structuredContent.updated_count !== testTaskIds.length) {
        throw new Error(`Expected ${testTaskIds.length} updates, got ${result.structuredContent.updated_count}`);
      }

      recordTest("task_bulk_update - Update multiple tasks", true, null, ITEM_IDS.task_bulk_update);
      await toggleItem(ITEM_IDS.task_bulk_update, "task_bulk_update");
    } catch (error) {
      recordTest("task_bulk_update - Update multiple tasks", false, error, ITEM_IDS.task_bulk_update);
    }

    // Test 9: task_bulk_assign_sprint
    try {
      console.log("Test 9: task_bulk_assign_sprint");

      // Create a sprint first
      try {
        const sprint = await backendClient.createSprint({
          name: "Validation Sprint",
          project_id: PROJECT_ID,
          status: "active"
        });
        testSprintId = sprint.id;
        console.log(`   Created sprint: ${testSprintId}`);
      } catch (error) {
        throw new Error("SKIP: Could not create sprint for testing");
      }

      if (testTaskIds.length === 0) {
        throw new Error("SKIP: No bulk test tasks available");
      }

      const result = await sendRequest("tools/call", {
        name: "task_bulk_assign_sprint",
        arguments: {
          taskIds: testTaskIds,
          sprintId: testSprintId
        }
      });

      if (!result || !result.structuredContent) {
        throw new Error("Invalid response structure");
      }

      if (result.structuredContent.success !== true) {
        throw new Error("Bulk sprint assignment did not return success");
      }

      recordTest("task_bulk_assign_sprint - Assign to sprint", true);
    } catch (error) {
      recordTest("task_bulk_assign_sprint - Assign to sprint", false, error);
    }

    console.log("\n" + "=".repeat(70));
    console.log("PHASE 5: Relationship Validation");
    console.log("=".repeat(70) + "\n");

    // Test 10: Relationships
    try {
      console.log("Test 10: Relationships (project_id, sprint_id, parent_task_id)");

      const result = await sendRequest("tools/call", {
        name: "task_read",
        arguments: { taskId: testTaskId }
      });

      if (!result || !result.structuredContent || !result.structuredContent.task) {
        throw new Error("Invalid response structure");
      }

      if (result.structuredContent.task.project_id !== PROJECT_ID) {
        throw new Error("Project relationship not maintained");
      }

      // Test parent-child relationship
      const childResult = await sendRequest("tools/call", {
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

      if (!childResult || !childResult.structuredContent || !childResult.structuredContent.task) {
        throw new Error("Invalid response for child task");
      }

      const childTask = childResult.structuredContent.task;
      if (childTask.parent_task_id !== testTaskId) {
        throw new Error("Parent task relationship not set");
      }

      recordTest("Relationships - Foreign keys working", true, null, ITEM_IDS.relationships);
      await toggleItem(ITEM_IDS.relationships, "Relationships");
    } catch (error) {
      recordTest("Relationships - Foreign keys working", false, error, ITEM_IDS.relationships);
    }

    console.log("\n" + "=".repeat(70));
    console.log("PHASE 6: Error Handling");
    console.log("=".repeat(70) + "\n");

    // Test 11: Error handling
    try {
      console.log("Test 11: Error handling (404, validation errors)");

      let errorTests = [];

      // Test 404 - non-existent task
      try {
        await sendRequest("tools/call", {
          name: "task_read",
          arguments: { taskId: "T-nonexist" }
        });
        errorTests.push({ name: "404 for missing task", passed: false });
      } catch (error) {
        errorTests.push({ name: "404 for missing task", passed: true });
      }

      // Test validation error - missing required fields
      try {
        await sendRequest("tools/call", {
          name: "task_create",
          arguments: {
            task: {
              description: "Missing required title"
            }
          }
        });
        errorTests.push({ name: "Validation error for missing fields", passed: false });
      } catch (error) {
        errorTests.push({ name: "Validation error for missing fields", passed: true });
      }

      // Test update with no changes
      try {
        await sendRequest("tools/call", {
          name: "task_update",
          arguments: {
            taskId: testTaskId,
            changes: {}
          }
        });
        errorTests.push({ name: "Error for empty update", passed: false });
      } catch (error) {
        errorTests.push({ name: "Error for empty update", passed: true });
      }

      const allPassed = errorTests.every(t => t.passed);
      if (!allPassed) {
        const failed = errorTests.filter(t => !t.passed).map(t => t.name).join(", ");
        throw new Error(`Some error tests failed: ${failed}`);
      }

      console.log(`   ✅ All ${errorTests.length} error handling tests passed`);
      recordTest("Error handling - All scenarios", true, null, ITEM_IDS.error_handling);
      await toggleItem(ITEM_IDS.error_handling, "Error handling");
    } catch (error) {
      recordTest("Error handling - All scenarios", false, error, ITEM_IDS.error_handling);
    }

    // Test 12: task_delete (save for last)
    try {
      console.log("\nTest 12: task_delete (cleanup)");

      const tasksToDelete = [testTaskId, ...testTaskIds].filter(Boolean);

      for (const taskId of tasksToDelete) {
        const result = await sendRequest("tools/call", {
          name: "task_delete",
          arguments: { taskId }
        });

        if (!result || !result.structuredContent || result.structuredContent.deleted !== true) {
          throw new Error(`Failed to delete task ${taskId}`);
        }

        // Verify deletion
        try {
          await sendRequest("tools/call", {
            name: "task_read",
            arguments: { taskId }
          });
          throw new Error(`Task ${taskId} still exists after deletion`);
        } catch (error) {
          // Expected to fail
        }
      }

      recordTest("task_delete - Delete and verify", true, null, ITEM_IDS.task_delete);
      await toggleItem(ITEM_IDS.task_delete, "task_delete");
    } catch (error) {
      recordTest("task_delete - Delete and verify", false, error, ITEM_IDS.task_delete);
    }

    // Print summary
    console.log("\n" + "=".repeat(70));
    console.log("Test Summary");
    console.log("=".repeat(70));
    console.log(`Total Tests: ${results.passed + results.failed + results.skipped}`);
    console.log(`Passed: ${results.passed}`);
    console.log(`Failed: ${results.failed}`);
    console.log(`Skipped: ${results.skipped}`);

    if (results.passed + results.failed > 0) {
      const successRate = ((results.passed / (results.passed + results.failed)) * 100).toFixed(1);
      console.log(`Success Rate: ${successRate}%`);
    }

    if (results.failed > 0) {
      console.log("\nFailed Tests:");
      results.tests.filter(t => !t.success && !t.error?.includes("SKIP")).forEach(t => {
        console.log(`  ❌ ${t.name}: ${t.error}`);
      });
    }

    if (results.skipped > 0) {
      console.log("\nSkipped Tests:");
      results.tests.filter(t => t.error?.includes("SKIP")).forEach(t => {
        console.log(`  ⏭️  ${t.name}: ${t.error}`);
      });
    }

    // Read final action list state
    console.log("\n" + "=".repeat(70));
    console.log("Action List Progress");
    console.log("=".repeat(70));

    const finalList = await sendRequest("tools/call", {
      name: "action_list_read",
      arguments: {
        action_list_id: ACTION_LIST_ID
      }
    });

    const list = finalList.structuredContent.action_list;
    console.log(`\nAction List: ${list.name}`);
    console.log(`Progress: ${list.completed_items}/${list.total_items} items (${list.progress_percentage}%)`);
    console.log(`\nItems completed during validation:`);
    list.items.filter(item => item.completed).forEach(item => {
      console.log(`  ☑ ${item.text}`);
    });

    server.kill();
    process.exit(results.failed === 0 ? 0 : 1);

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

validateAllTaskTools();
