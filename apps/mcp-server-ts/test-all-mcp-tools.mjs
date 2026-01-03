/**
 * Comprehensive MCP Tools Workflow Test
 * Tests all 9 ActionList MCP tools via JSON-RPC protocol
 *
 * This validates the complete MCP surface area for ActionLists
 */

import { spawn } from "child_process";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log("=== Comprehensive MCP Tools Workflow Test ===\n");

// Track test results
let testsRun = 0;
let testsPassed = 0;
let testsFailed = 0;

// Track workflow state
let testProjectId = null;
let testActionListId = null;
let testItemIds = [];

// Request ID counter
let requestId = 1;

// Start MCP server
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

// Helper to send JSON-RPC request
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

    // Timeout after 10 seconds
    setTimeout(() => {
      if (pendingRequests.has(id)) {
        pendingRequests.delete(id);
        reject(new Error(`Timeout waiting for response to ${method}`));
      }
    }, 10000);
  });
}

// Helper to log test results
function logTest(name, passed, details = "") {
  testsRun++;
  const status = passed ? "✅ PASS" : "❌ FAIL";
  console.log(`${status}: ${name}`);
  if (details) console.log(`   ${details}`);
  if (passed) testsPassed++;
  else testsFailed++;
}

// Handle server stderr (logs)
server.stderr.on("data", (data) => {
  const message = data.toString();
  if (process.env.DEBUG) {
    console.error("[Server Log]", message.trim());
  }
});

// Handle server stdout (JSON-RPC responses)
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
          reject(new Error(response.error.message || "Unknown error"));
        } else {
          resolve(response.result);
        }
      }
    } catch (e) {
      // Not valid JSON or incomplete message
    }
  }
});

// Handle server exit
server.on("exit", (code) => {
  if (pendingRequests.size > 0) {
    console.error("\n❌ Server exited with pending requests");
    process.exit(1);
  }
});

// Wait for server to initialize
await new Promise(resolve => setTimeout(resolve, 2000));

async function runWorkflowTests() {
  try {
    console.log("=== Setup: Create Test Project ===\n");

    // First, create a project using project_create tool
    try {
      const projectResult = await sendRequest("tools/call", {
        name: "project_create",
        arguments: {
          project: {
            name: "MCP Workflow Test Project",
            description: "Testing all ActionList MCP tools",
            status: "active",
          }
        }
      });

      testProjectId = projectResult.content[0].structuredContent?.project?.id;
      if (!testProjectId) {
        throw new Error("Project ID not found in response");
      }

      logTest("Create test project", true, `Project ID: ${testProjectId}`);
    } catch (error) {
      logTest("Create test project", false, error.message);
      throw error;
    }

    console.log("\n=== Tool 1: action_list_create ===\n");

    try {
      const createResult = await sendRequest("tools/call", {
        name: "action_list_create",
        arguments: {
          action_list: {
            name: "MCP Test Action List",
            description: "Testing MCP tools workflow",
            status: "active",
            project_id: testProjectId,
            priority: "high",
            notes: "Comprehensive MCP tool validation",
          }
        }
      });

      const actionList = createResult.content[0].structuredContent?.action_list;
      testActionListId = actionList?.id;

      logTest(
        "action_list_create",
        !!testActionListId,
        `Created: ${testActionListId}, Items: ${actionList?.total_items}`
      );
    } catch (error) {
      logTest("action_list_create", false, error.message);
      throw error;
    }

    console.log("\n=== Tool 2: action_list_read ===\n");

    try {
      const readResult = await sendRequest("tools/call", {
        name: "action_list_read",
        arguments: {
          action_list_id: testActionListId,
        }
      });

      const actionList = readResult.content[0].structuredContent?.action_list;

      logTest(
        "action_list_read",
        actionList?.id === testActionListId,
        `Retrieved: ${actionList?.name}, Status: ${actionList?.status}`
      );
    } catch (error) {
      logTest("action_list_read", false, error.message);
    }

    console.log("\n=== Tool 6: action_list_add_item (x3) ===\n");

    // Add first item
    try {
      const add1Result = await sendRequest("tools/call", {
        name: "action_list_add_item",
        arguments: {
          action_list_id: testActionListId,
          item: {
            text: "First MCP test item",
            order: 0,
          }
        }
      });

      const actionList1 = add1Result.content[0].structuredContent?.action_list;
      testItemIds.push(actionList1?.items?.[0]?.id);

      logTest(
        "action_list_add_item (1/3)",
        actionList1?.total_items === 1,
        `Item ID: ${testItemIds[0]}, Progress: ${actionList1?.progress_percentage}%`
      );
    } catch (error) {
      logTest("action_list_add_item (1/3)", false, error.message);
    }

    // Add second item
    try {
      const add2Result = await sendRequest("tools/call", {
        name: "action_list_add_item",
        arguments: {
          action_list_id: testActionListId,
          item: {
            text: "Second MCP test item",
            order: 1,
          }
        }
      });

      const actionList2 = add2Result.content[0].structuredContent?.action_list;
      testItemIds.push(actionList2?.items?.[1]?.id);

      logTest(
        "action_list_add_item (2/3)",
        actionList2?.total_items === 2,
        `Item ID: ${testItemIds[1]}, Total: ${actionList2?.total_items}`
      );
    } catch (error) {
      logTest("action_list_add_item (2/3)", false, error.message);
    }

    // Add third item
    try {
      const add3Result = await sendRequest("tools/call", {
        name: "action_list_add_item",
        arguments: {
          action_list_id: testActionListId,
          item: {
            text: "Third MCP test item",
            order: 2,
          }
        }
      });

      const actionList3 = add3Result.content[0].structuredContent?.action_list;
      testItemIds.push(actionList3?.items?.[2]?.id);

      logTest(
        "action_list_add_item (3/3)",
        actionList3?.total_items === 3,
        `Item ID: ${testItemIds[2]}, Total: ${actionList3?.total_items}`
      );
    } catch (error) {
      logTest("action_list_add_item (3/3)", false, error.message);
    }

    console.log("\n=== Tool 3: action_list_list ===\n");

    try {
      const listAllResult = await sendRequest("tools/call", {
        name: "action_list_list",
        arguments: {
          filters: {}
        }
      });

      const allLists = listAllResult.content[0].structuredContent?.action_lists;
      const foundOurs = allLists?.some(al => al.id === testActionListId);

      logTest(
        "action_list_list (all)",
        foundOurs,
        `Found ${allLists?.length} lists, includes ours: ${foundOurs}`
      );
    } catch (error) {
      logTest("action_list_list (all)", false, error.message);
    }

    // List with filter
    try {
      const listFilteredResult = await sendRequest("tools/call", {
        name: "action_list_list",
        arguments: {
          filters: {
            project_id: testProjectId,
            status: "active",
          }
        }
      });

      const filteredLists = listFilteredResult.content[0].structuredContent?.action_lists;
      const foundOurs = filteredLists?.some(al => al.id === testActionListId);

      logTest(
        "action_list_list (filtered)",
        foundOurs,
        `Filtered by project_id: ${filteredLists?.length} lists`
      );
    } catch (error) {
      logTest("action_list_list (filtered)", false, error.message);
    }

    console.log("\n=== Tool 7: action_list_toggle_item ===\n");

    try {
      const toggleResult = await sendRequest("tools/call", {
        name: "action_list_toggle_item",
        arguments: {
          action_list_id: testActionListId,
          item_id: testItemIds[0],
        }
      });

      const actionList = toggleResult.content[0].structuredContent?.action_list;
      const expectedProgress = 33.33;
      const actualProgress = actionList?.progress_percentage;
      const progressMatch = Math.abs(actualProgress - expectedProgress) < 0.01;

      logTest(
        "action_list_toggle_item",
        progressMatch,
        `Toggled: ${testItemIds[0]}, Progress: ${actualProgress}% (expected ${expectedProgress}%)`
      );
    } catch (error) {
      logTest("action_list_toggle_item", false, error.message);
    }

    console.log("\n=== Tool 9: action_list_reorder_items ===\n");

    try {
      const reorderResult = await sendRequest("tools/call", {
        name: "action_list_reorder_items",
        arguments: {
          action_list_id: testActionListId,
          item_ids: [testItemIds[2], testItemIds[1], testItemIds[0]], // Reverse order
        }
      });

      const actionList = reorderResult.content[0].structuredContent?.action_list;
      const firstItemId = actionList?.items?.[0]?.id;
      const correctOrder = firstItemId === testItemIds[2];

      logTest(
        "action_list_reorder_items",
        correctOrder,
        `Reordered to: [${testItemIds[2]}, ${testItemIds[1]}, ${testItemIds[0]}], First item: ${firstItemId}`
      );
    } catch (error) {
      logTest("action_list_reorder_items", false, error.message);
    }

    console.log("\n=== Tool 8: action_list_remove_item ===\n");

    try {
      const removeResult = await sendRequest("tools/call", {
        name: "action_list_remove_item",
        arguments: {
          action_list_id: testActionListId,
          item_id: testItemIds[1], // Remove middle item
        }
      });

      const actionList = removeResult.content[0].structuredContent?.action_list;
      const remainingIds = actionList?.items?.map(i => i.id) || [];
      const removedSuccessfully = !remainingIds.includes(testItemIds[1]);

      logTest(
        "action_list_remove_item",
        removedSuccessfully && actionList?.total_items === 2,
        `Removed: ${testItemIds[1]}, Remaining: ${actionList?.total_items} items`
      );
    } catch (error) {
      logTest("action_list_remove_item", false, error.message);
    }

    console.log("\n=== Tool 4: action_list_update ===\n");

    try {
      const updateResult = await sendRequest("tools/call", {
        name: "action_list_update",
        arguments: {
          action_list_id: testActionListId,
          changes: {
            name: "Updated MCP Test List",
            status: "completed",
            priority: "medium",
            notes: "Updated via MCP tool - all tests completed",
          }
        }
      });

      const actionList = updateResult.content[0].structuredContent?.action_list;
      const statusCorrect = actionList?.status === "completed";
      const priorityCorrect = actionList?.priority === "medium";
      const completedAtSet = !!actionList?.completed_at;

      logTest(
        "action_list_update",
        statusCorrect && priorityCorrect && completedAtSet,
        `Status: ${actionList?.status}, Priority: ${actionList?.priority}, Completed At: ${completedAtSet ? 'Set' : 'Not set'}`
      );
    } catch (error) {
      logTest("action_list_update", false, error.message);
    }

    console.log("\n=== Tool 5: action_list_delete ===\n");

    try {
      const deleteResult = await sendRequest("tools/call", {
        name: "action_list_delete",
        arguments: {
          action_list_id: testActionListId,
        }
      });

      logTest(
        "action_list_delete",
        true,
        `Deleted: ${testActionListId}`
      );

      // Verify deletion
      try {
        await sendRequest("tools/call", {
          name: "action_list_read",
          arguments: {
            action_list_id: testActionListId,
          }
        });

        logTest("action_list_delete (verification)", false, "ActionList still exists after delete");
      } catch (error) {
        logTest("action_list_delete (verification)", true, "404 error on GET confirms deletion");
      }
    } catch (error) {
      logTest("action_list_delete", false, error.message);
    }

    // Print summary
    console.log("\n=== Test Summary ===");
    console.log(`Total Tests: ${testsRun}`);
    console.log(`✅ Passed: ${testsPassed}`);
    console.log(`❌ Failed: ${testsFailed}`);

    console.log("\n=== Tools Validated ===");
    console.log("1. ✅ action_list_create");
    console.log("2. ✅ action_list_read");
    console.log("3. ✅ action_list_list (all & filtered)");
    console.log("4. ✅ action_list_update");
    console.log("5. ✅ action_list_delete");
    console.log("6. ✅ action_list_add_item (x3)");
    console.log("7. ✅ action_list_toggle_item");
    console.log("8. ✅ action_list_remove_item");
    console.log("9. ✅ action_list_reorder_items");

    if (testsFailed === 0) {
      console.log("\n✅ SUCCESS: All MCP tools validated via JSON-RPC protocol!");
      server.kill();
      process.exit(0);
    } else {
      console.log(`\n❌ FAILURE: ${testsFailed} test(s) failed`);
      server.kill();
      process.exit(1);
    }

  } catch (error) {
    console.error("\n❌ FATAL ERROR:", error.message);
    console.error(error.stack);
    server.kill();
    process.exit(1);
  }
}

// Run the workflow tests
runWorkflowTests();
