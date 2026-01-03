/**
 * Phase 1: Verify Action List Tools Are Registered
 *
 * This script verifies that all 9 action list MCP tools are registered
 * with the MCP server and available for use.
 *
 * This is a gatekeeper for Phase 2 - if tools are not registered, Phase 2 cannot proceed.
 *
 * NOTE: This phase only checks tool registration. Functional testing will be done
 * in Phase 2 when creating the actual validation action lists.
 */

process.env.TASK_MANAGER_API_ENDPOINT = "http://localhost:3001/api/v1";

import { spawn } from "child_process";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log("=== Phase 1: Verify Action List Tools Registration ===\n");

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
  if (output && !output.includes("TaskMan MCP") && !output.includes("server connected")) {
    console.error("[Server]", output);
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
console.log("Server initialized\n");

async function verifyActionListTools() {
  let passed = 0;
  let failed = 0;

  try {
    // Step 1: Verify server connectivity
    console.log("Step 1: Testing MCP server connectivity...");
    try {
      const listResult = await sendRequest("tools/list", {});
      console.log(`✅ PASS: MCP server responding\n`);
      passed++;
    } catch (error) {
      console.log(`❌ FAIL: MCP server not responding - ${error.message}\n`);
      failed++;
      throw error;
    }

    // Step 2: List all registered tools
    console.log("Step 2: Listing all registered MCP tools...");
    const result = await sendRequest("tools/list", {});
    const allTools = result.tools || [];

    console.log(`Total tools registered: ${allTools.length}`);

    const taskTools = allTools.filter(t => t.name.startsWith("task_"));
    const projectTools = allTools.filter(t => t.name.startsWith("project_"));
    const actionListTools = allTools.filter(t =>
      t.name.startsWith("action_list_") || t.name.includes("action")
    );

    console.log(`  - Task tools: ${taskTools.length}`);
    console.log(`  - Project tools: ${projectTools.length}`);
    console.log(`  - Action list tools: ${actionListTools.length}\n`);

    // Step 3: Verify all required action list tools
    console.log("Step 3: Verifying all 9 required action list tools are registered...\n");

    const expectedTools = [
      {
        name: "action_list_create",
        description: "Create a new action list"
      },
      {
        name: "action_list_read",
        description: "Read/get an action list by ID"
      },
      {
        name: "action_list_list",
        description: "List action lists with optional filters"
      },
      {
        name: "action_list_update",
        description: "Update an action list"
      },
      {
        name: "action_list_delete",
        description: "Delete an action list"
      },
      {
        name: "action_list_add_item",
        description: "Add an item to an action list"
      },
      {
        name: "action_list_toggle_item",
        description: "Toggle item completion status"
      },
      {
        name: "action_list_remove_item",
        description: "Remove an item from an action list"
      },
      {
        name: "action_list_reorder_items",
        description: "Reorder items in an action list"
      }
    ];

    const toolNames = actionListTools.map(t => t.name);
    const missingTools = [];

    for (const expectedTool of expectedTools) {
      if (toolNames.includes(expectedTool.name)) {
        console.log(`✅ PASS: ${expectedTool.name}`);
        console.log(`         ${expectedTool.description}\n`);
        passed++;
      } else {
        console.log(`❌ FAIL: ${expectedTool.name}`);
        console.log(`         ${expectedTool.description}`);
        console.log(`         Status: NOT REGISTERED\n`);
        failed++;
        missingTools.push(expectedTool.name);
      }
    }

    if (missingTools.length > 0) {
      console.log(`\n❌ Missing tools (${missingTools.length}):`);
      missingTools.forEach(tool => console.log(`   - ${tool}`));
      console.log();
      throw new Error(`Missing ${missingTools.length} required tools`);
    }

    // Step 4: Verify tool schemas (check that tools have input schemas)
    console.log("\nStep 4: Verifying tool schemas are defined...\n");

    for (const expectedTool of expectedTools) {
      const tool = allTools.find(t => t.name === expectedTool.name);
      if (tool && tool.inputSchema) {
        console.log(`✅ PASS: ${expectedTool.name} has input schema defined`);
        passed++;
      } else {
        console.log(`❌ FAIL: ${expectedTool.name} missing input schema`);
        failed++;
      }
    }

    // Summary
    console.log("\n" + "=".repeat(70));
    console.log("PHASE 1 VERIFICATION SUMMARY");
    console.log("=".repeat(70));
    console.log(`Tests passed: ${passed}`);
    console.log(`Tests failed: ${failed}`);
    console.log(`Success rate: ${((passed / (passed + failed)) * 100).toFixed(1)}%`);
    console.log("=".repeat(70));

    if (failed === 0) {
      console.log("\n✅ PHASE 1 COMPLETE: All action list tools are registered!");
      console.log("\nVerified:");
      console.log("  ✓ MCP server is responsive");
      console.log("  ✓ All 9 action list tools are registered");
      console.log("  ✓ All tools have valid input schemas");
      console.log("\n📋 Ready to proceed to Phase 2:");
      console.log("   Create 9 task validation action lists with 61 test items\n");
      console.log("   Run: node phase2-create-task-validation-lists.mjs\n");
    } else {
      console.log("\n❌ PHASE 1 FAILED: Fix issues before proceeding to Phase 2\n");
      process.exit(1);
    }

  } catch (error) {
    console.error("\n❌ Fatal error during verification:", error.message);
    process.exit(1);
  } finally {
    server.kill();
    process.exit(failed === 0 ? 0 : 1);
  }
}

// Run verification
verifyActionListTools();
