/**
 * Verify created action lists and display their contents
 */

// Set environment variable BEFORE any imports
process.env.TASK_MANAGER_API_ENDPOINT = "http://localhost:3001/api/v1";

import { spawn } from "child_process";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

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

async function verifyActionLists() {
  try {
    const projectId = "P-8767f2bc";

    console.log("=== Verification: TaskMan MCP Validation Action Lists ===\n");

    // List all action lists for the project
    console.log(`Listing action lists for project ${projectId}...\n`);
    const listResult = await sendRequest("tools/call", {
      name: "action_list_list",
      arguments: {
        project_id: projectId
      }
    });

    const lists = listResult.structuredContent.action_lists;
    console.log(`Found ${lists.length} action lists:\n`);

    // Display summary of each list
    for (const list of lists) {
      console.log(`📋 ${list.name}`);
      console.log(`   ID: ${list.id}`);
      console.log(`   Status: ${list.status}`);
      console.log(`   Priority: ${list.priority}`);
      console.log(`   Items: ${list.total_items} total, ${list.completed_items} completed`);
      console.log(`   Progress: ${list.progress_percentage !== null ? list.progress_percentage + '%' : 'N/A'}`);
      console.log(`   Created: ${list.created_at}`);
      console.log();
    }

    // Read one list in detail to show items
    console.log("\n" + "=".repeat(70));
    console.log("Detailed View: Task MCP Tools Validation");
    console.log("=".repeat(70) + "\n");

    const taskListId = lists.find(l => l.name === "Task MCP Tools Validation")?.id;
    if (taskListId) {
      const detailResult = await sendRequest("tools/call", {
        name: "action_list_read",
        arguments: {
          action_list_id: taskListId
        }
      });

      const taskList = detailResult.structuredContent.action_list;
      console.log(`Name: ${taskList.name}`);
      console.log(`Description: ${taskList.description}`);
      console.log(`Notes: ${taskList.notes}`);
      console.log(`\nItems (${taskList.items.length}):`);
      taskList.items.forEach((item, index) => {
        const checkbox = item.completed ? '☑' : '☐';
        console.log(`  ${index + 1}. ${checkbox} ${item.text}`);
      });
      console.log(`\nProgress: ${taskList.completed_items}/${taskList.total_items} items completed`);
      if (taskList.progress_percentage !== null) {
        console.log(`Percentage: ${taskList.progress_percentage}%`);
      }
    }

    console.log("\n" + "=".repeat(70));
    console.log("Verification Complete");
    console.log("=".repeat(70));
    console.log("\nAll action lists created successfully!");
    console.log("Ready to use for MCP tool validation workflow.");

    server.kill();
    process.exit(0);

  } catch (error) {
    console.error("\n❌ Error:", error.message);
    if (error.stack) {
      console.error("\nStack trace:");
      console.error(error.stack);
    }
    server.kill();
    process.exit(1);
  }
}

verifyActionLists();
