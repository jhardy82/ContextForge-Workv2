/**
 * Debug single MCP tool call to understand response structure
 * FIXED: Set environment variable BEFORE any imports
 */

// CRITICAL: Set environment variable BEFORE any imports
process.env.TASK_MANAGER_API_ENDPOINT = "http://localhost:3001/api/v1";

import { spawn } from "child_process";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log("=== Single Tool Debug Test (Fixed) ===\n");

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
  console.error("[Server]", data.toString().trim());
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

async function testSingleTool() {
  try {
    console.log("Testing: action_list_create\n");

    // Import AFTER environment variable is set
    const { backendClient } = await import("./dist/backend/client.js");

    console.log("Creating project via backend client...");
    const project = await backendClient.createProject({
      name: "Debug Test Project",
      status: "active",
    });

    console.log("✅ Created project:", project.id, "\n");

    // Now test action_list_create via MCP
    console.log("Calling action_list_create via MCP...");
    const result = await sendRequest("tools/call", {
      name: "action_list_create",
      arguments: {
        action_list: {
          name: "Debug Test List",
          status: "active",
          project_id: project.id,
        }
      }
    });

    console.log("\n=== Full MCP Response ===");
    console.log(JSON.stringify(result, null, 2));

    console.log("\n=== Response Analysis ===");
    console.log("Type:", typeof result);
    console.log("Keys:", Object.keys(result));
    if (result.content) {
      console.log("Content type:", typeof result.content);
      console.log("Content length:", result.content.length);
      console.log("\nFirst content item:");
      console.log(JSON.stringify(result.content[0], null, 2));
    }

    console.log("\n✅ SUCCESS: MCP tool call completed");
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

testSingleTool();
