/**
 * DEBUG: Task validation with detailed logging
 */

process.env.TASK_MANAGER_API_ENDPOINT = "http://localhost:3001/api/v1";

import { spawn } from "child_process";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log("=== Task Validation DEBUG ===\n");

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
let responseCount = 0;

function sendRequest(method, params = {}) {
  const id = requestId++;
  const request = {
    jsonrpc: "2.0",
    id,
    method,
    params,
  };

  console.log(`[REQ ${id}] ${method} - ${JSON.stringify(params).substring(0, 50)}...`);

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
  // Suppress AUDIT logs
});

server.stdout.on("data", (data) => {
  outputBuffer += data.toString();
  const lines = outputBuffer.split("\n");
  outputBuffer = lines.pop() || "";

  for (const line of lines) {
    if (!line.trim()) continue;
    if (line.includes('[AUDIT]')) continue;

    console.log(`[STDOUT ${++responseCount}] ${line.substring(0, 80)}...`);

    try {
      const response = JSON.parse(line);

      console.log(`[PARSE ${responseCount}] ID=${response.id}, hasResult=${!!response.result}, hasError=${!!response.error}`);

      if (response.result) {
        console.log(`[RESULT ${responseCount}] keys=${Object.keys(response.result).join(",")}`);
        if (response.result.structuredContent) {
          console.log(`[STRUCT ${responseCount}] keys=${Object.keys(response.result.structuredContent).join(",")}`);
        }
      }

      if (response.id && pendingRequests.has(response.id)) {
        const { resolve, reject } = pendingRequests.get(response.id);
        pendingRequests.delete(response.id);

        if (response.error) {
          console.log(`[ERROR ${responseCount}] ${response.error.message}`);
          reject(new Error(`MCP error: ${response.error.message}`));
        } else {
          console.log(`[RESOLVE ${responseCount}] Resolving request ${response.id}`);
          resolve(response.result);
        }
      }
    } catch (e) {
      console.log(`[PARSE-ERR ${responseCount}] ${e.message}`);
    }
  }
});

await new Promise(resolve => setTimeout(resolve, 2000));

async function test() {
  try {
    const { backendClient } = await import("./dist/backend/client.js");

    console.log("\n--- Getting project ---");
    const project = await backendClient.getProject("P-8767f2bc");
    console.log(`✅ Project: ${project.id}\n`);

    console.log("--- Calling task_create ---");
    const result = await sendRequest("tools/call", {
      name: "task_create",
      arguments: {
        task: {
          title: "Debug Test",
          project_id: "P-8767f2bc",
          status: "new",
          work_type: "task"
        }
      }
    });

    console.log("\n--- Result Analysis ---");
    console.log("result type:", typeof result);
    console.log("result is null?", result === null);
    console.log("result is undefined?", result === undefined);

    if (result) {
      console.log("result keys:", Object.keys(result));
      console.log("has content?", !!result.content);
      console.log("has structuredContent?", !!result.structuredContent);

      if (result.structuredContent) {
        console.log("structuredContent keys:", Object.keys(result.structuredContent));
        console.log("has task?", !!result.structuredContent.task);

        if (result.structuredContent.task) {
          console.log("\n✅ SUCCESS!");
          console.log("Task ID:", result.structuredContent.task.id);
          console.log("Task Title:", result.structuredContent.task.title);
        } else {
          console.log("\n❌ NO TASK in structuredContent");
        }
      } else {
        console.log("\n❌ NO structuredContent");
      }
    } else {
      console.log("\n❌ result is null/undefined");
    }

    server.kill();
    process.exit(0);

  } catch (error) {
    console.error("\n❌ ERROR:", error.message);
    console.error(error.stack);
    server.kill();
    process.exit(1);
  }
}

test();
