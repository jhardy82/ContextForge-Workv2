/**
 * Read the existing Task validation action list to see current state
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

async function readTaskActionList() {
  try {
    const actionListId = "AL-c3748b54";

    console.log("=== Task MCP Tools Validation Action List ===\n");
    console.log(`Reading action list: ${actionListId}\n`);

    const result = await sendRequest("tools/call", {
      name: "action_list_read",
      arguments: {
        action_list_id: actionListId
      }
    });

    const list = result.structuredContent.action_list;

    console.log(`Name: ${list.name}`);
    console.log(`Description: ${list.description}`);
    console.log(`Status: ${list.status}`);
    console.log(`Priority: ${list.priority}`);
    console.log(`Notes: ${list.notes}`);
    console.log(`\nProgress: ${list.completed_items}/${list.total_items} items (${list.progress_percentage}%)`);
    console.log(`\nItems:`);

    list.items.forEach((item, index) => {
      const checkbox = item.completed ? '☑' : '☐';
      console.log(`  ${checkbox} [${item.id}] ${item.text}`);
    });

    console.log("\n" + "=".repeat(70));
    console.log("Item IDs for validation script:");
    console.log("=".repeat(70));
    list.items.forEach((item, index) => {
      console.log(`// Item ${index + 1}: ${item.text.substring(0, 50)}...`);
      console.log(`const item${index + 1}Id = "${item.id}";`);
    });

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

readTaskActionList();
