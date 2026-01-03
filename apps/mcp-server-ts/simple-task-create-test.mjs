/**
 * Simple isolated test of task_create to debug response structure
 */

// Set environment variable BEFORE any imports
process.env.TASK_MANAGER_API_ENDPOINT = "http://localhost:3001/api/v1";

import { spawn } from "child_process";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log("=== Simple task_create Test ===\n");

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

  console.log(`\nSending request ${id}:`, JSON.stringify(request, null, 2));

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
  console.log("[STDERR]", data.toString().trim());
});

server.stdout.on("data", (data) => {
  outputBuffer += data.toString();

  const lines = outputBuffer.split("\n");
  outputBuffer = lines.pop() || "";

  for (const line of lines) {
    if (!line.trim()) continue;

    console.log("[STDOUT LINE]", line.substring(0, 100) + "...");

    try {
      const response = JSON.parse(line);

      console.log("\nParsed response:", JSON.stringify(response, null, 2).substring(0, 500));

      if (response.id && pendingRequests.has(response.id)) {
        const { resolve, reject } = pendingRequests.get(response.id);
        pendingRequests.delete(response.id);

        if (response.error) {
          console.log("\n❌ Response has error:", response.error);
          reject(new Error(`MCP error ${response.error.code}: ${response.error.message}`));
        } else {
          console.log("\n✅ Response OK");
          resolve(response.result);
        }
      }
    } catch (e) {
      console.log("[PARSE ERROR]", e.message);
    }
  }
});

// Wait for server to initialize
await new Promise(resolve => setTimeout(resolve, 2000));

async function test() {
  try {
    console.log("Calling task_create...");

    const result = await sendRequest("tools/call", {
      name: "task_create",
      arguments: {
        task: {
          title: "Simple Test Task",
          description: "Testing",
          project_id: "P-8767f2bc",
          status: "new",
          work_type: "task"
        }
      }
    });

    console.log("\n" + "=".repeat(70));
    console.log("RESULT:");
    console.log("=".repeat(70));
    console.log("typeof result:", typeof result);
    console.log("result is null?", result === null);
    console.log("result is undefined?", result === undefined);

    if (result) {
      console.log("result keys:", Object.keys(result));

      if (result.structuredContent) {
        console.log("\nstructuredContent exists!");
        console.log("structuredContent keys:", Object.keys(result.structuredContent));

        if (result.structuredContent.task) {
          console.log("\n✅✅✅ task field exists!");
          console.log("Task ID:", result.structuredContent.task.id);
          console.log("Task title:", result.structuredContent.task.title);
        } else {
          console.log("\n❌ task field MISSING in structuredContent");
        }
      } else {
        console.log("\n❌ structuredContent MISSING");
      }
    } else {
      console.log("\n❌ result is null/undefined");
    }

    server.kill();
    process.exit(0);

  } catch (error) {
    console.error("\n❌ Error:", error.message);
    if (error.stack) {
      console.error("\nStack:", error.stack);
    }
    server.kill();
    process.exit(1);
  }
}

test();
