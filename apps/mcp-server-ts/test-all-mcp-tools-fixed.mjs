/**
 * Comprehensive test of all 9 ActionList MCP tools via JSON-RPC protocol
 * FIXED: Set environment variable BEFORE any imports
 */

// CRITICAL: Set environment variable BEFORE any imports
process.env.TASK_MANAGER_API_ENDPOINT = "http://localhost:3001/api/v1";

import { spawn } from "child_process";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log("=== Testing All 9 ActionList MCP Tools ===\n");

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

const results = {
  passed: 0,
  failed: 0,
  tests: []
};

function recordTest(name, success, error = null) {
  results.tests.push({ name, success, error: error?.message });
  if (success) {
    results.passed++;
    console.log(`✅ ${name}`);
  } else {
    results.failed++;
    console.log(`❌ ${name}`);
    if (error) console.log(`   Error: ${error.message}`);
  }
}

async function testAllTools() {
  try {
    // Import AFTER environment variable is set
    const { backendClient } = await import("./dist/backend/client.js");

    // Setup: Create project
    console.log("Setup: Creating test project...");
    const project = await backendClient.createProject({
      name: "MCP Tools Test Project",
      status: "active",
    });
    console.log(`✅ Created project: ${project.id}\n`);

    let actionListId;
    let itemIds = [];

    console.log("Testing 9 ActionList MCP Tools:\n");

    // Test 1: action_list_create
    try {
      const result = await sendRequest("tools/call", {
        name: "action_list_create",
        arguments: {
          action_list: {
            name: "Comprehensive Test List",
            description: "Testing all MCP tools",
            status: "active",
            priority: "high",
            project_id: project.id,
            notes: "This is a test action list"
          }
        }
      });

      actionListId = result.structuredContent.action_list.id;
      recordTest("action_list_create", true);
    } catch (error) {
      recordTest("action_list_create", false, error);
      throw new Error("Cannot continue without creating action list");
    }

    // Test 2: action_list_read
    try {
      const result = await sendRequest("tools/call", {
        name: "action_list_read",
        arguments: {
          action_list_id: actionListId
        }
      });

      const list = result.structuredContent.action_list;
      if (list.id !== actionListId || list.name !== "Comprehensive Test List") {
        throw new Error("Retrieved action list doesn't match created list");
      }
      recordTest("action_list_read", true);
    } catch (error) {
      recordTest("action_list_read", false, error);
    }

    // Test 3: action_list_list
    try {
      const result = await sendRequest("tools/call", {
        name: "action_list_list",
        arguments: {
          project_id: project.id
        }
      });

      const lists = result.structuredContent.action_lists;
      if (!Array.isArray(lists) || lists.length === 0) {
        throw new Error("Expected at least one action list");
      }
      const found = lists.find(l => l.id === actionListId);
      if (!found) {
        throw new Error("Created action list not found in list");
      }
      recordTest("action_list_list", true);
    } catch (error) {
      recordTest("action_list_list", false, error);
    }

    // Test 4: action_list_add_item (add 3 items)
    try {
      // Add item 1
      const result1 = await sendRequest("tools/call", {
        name: "action_list_add_item",
        arguments: {
          action_list_id: actionListId,
          item: {
            text: "First test item",
            order: 1
          }
        }
      });
      const list1 = result1.structuredContent.action_list;
      itemIds.push(list1.items[list1.items.length - 1].id);

      // Add item 2
      const result2 = await sendRequest("tools/call", {
        name: "action_list_add_item",
        arguments: {
          action_list_id: actionListId,
          item: {
            text: "Second test item",
            order: 2
          }
        }
      });
      const list2 = result2.structuredContent.action_list;
      itemIds.push(list2.items[list2.items.length - 1].id);

      // Add item 3
      const result3 = await sendRequest("tools/call", {
        name: "action_list_add_item",
        arguments: {
          action_list_id: actionListId,
          item: {
            text: "Third test item",
            order: 3
          }
        }
      });
      const list3 = result3.structuredContent.action_list;
      itemIds.push(list3.items[list3.items.length - 1].id);

      recordTest("action_list_add_item", true);
    } catch (error) {
      recordTest("action_list_add_item", false, error);
    }

    // Test 5: action_list_toggle_item (complete first item)
    try {
      const result = await sendRequest("tools/call", {
        name: "action_list_toggle_item",
        arguments: {
          action_list_id: actionListId,
          item_id: itemIds[0]
        }
      });

      const list = result.structuredContent.action_list;
      const toggledItem = list.items.find(item => item.id === itemIds[0]);
      if (!toggledItem || toggledItem.completed !== true) {
        throw new Error("Item should be marked as completed");
      }
      recordTest("action_list_toggle_item", true);
    } catch (error) {
      recordTest("action_list_toggle_item", false, error);
    }

    // Test 6: action_list_reorder_items (reverse order)
    try {
      const newOrder = [itemIds[2], itemIds[1], itemIds[0]];
      const result = await sendRequest("tools/call", {
        name: "action_list_reorder_items",
        arguments: {
          action_list_id: actionListId,
          reorder: {
            item_ids: newOrder
          }
        }
      });

      const list = result.structuredContent.action_list;
      if (list.items[0].id !== itemIds[2]) {
        throw new Error("Items not reordered correctly");
      }
      recordTest("action_list_reorder_items", true);
    } catch (error) {
      recordTest("action_list_reorder_items", false, error);
    }

    // Test 7: action_list_update
    try {
      const result = await sendRequest("tools/call", {
        name: "action_list_update",
        arguments: {
          action_list_id: actionListId,
          changes: {
            name: "Updated Test List",
            description: "Description has been updated",
            status: "completed",
            priority: "medium"
          }
        }
      });

      const list = result.structuredContent.action_list;
      if (list.name !== "Updated Test List" || list.status !== "completed") {
        throw new Error("Action list not updated correctly");
      }
      recordTest("action_list_update", true);
    } catch (error) {
      recordTest("action_list_update", false, error);
    }

    // Test 8: action_list_remove_item (remove second item)
    try {
      const result = await sendRequest("tools/call", {
        name: "action_list_remove_item",
        arguments: {
          action_list_id: actionListId,
          item_id: itemIds[1]
        }
      });

      const list = result.structuredContent.action_list;
      if (list.items.length !== 2) {
        throw new Error(`Expected 2 items after removal, got ${list.items.length}`);
      }
      const stillExists = list.items.find(item => item.id === itemIds[1]);
      if (stillExists) {
        throw new Error("Removed item still exists in list");
      }
      recordTest("action_list_remove_item", true);
    } catch (error) {
      recordTest("action_list_remove_item", false, error);
    }

    // Test 9: action_list_delete
    try {
      await sendRequest("tools/call", {
        name: "action_list_delete",
        arguments: {
          action_list_id: actionListId
        }
      });

      // Verify deletion by trying to read it (should fail)
      try {
        await sendRequest("tools/call", {
          name: "action_list_read",
          arguments: {
            action_list_id: actionListId
          }
        });
        throw new Error("Action list should have been deleted but still exists");
      } catch (readError) {
        // Expected to fail - this is good
        recordTest("action_list_delete", true);
      }
    } catch (error) {
      recordTest("action_list_delete", false, error);
    }

    // Print summary
    console.log("\n" + "=".repeat(50));
    console.log("Test Summary");
    console.log("=".repeat(50));
    console.log(`Total Tests: ${results.passed + results.failed}`);
    console.log(`Passed: ${results.passed}`);
    console.log(`Failed: ${results.failed}`);
    console.log(`Success Rate: ${((results.passed / (results.passed + results.failed)) * 100).toFixed(1)}%`);

    if (results.failed > 0) {
      console.log("\nFailed Tests:");
      results.tests.filter(t => !t.success).forEach(t => {
        console.log(`  ❌ ${t.name}: ${t.error}`);
      });
    }

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

testAllTools();
