/**
 * Minimal test - exact copy of working debug pattern
 */

process.env.TASK_MANAGER_API_ENDPOINT = "http://localhost:3001/api/v1";

import { spawn } from "child_process";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const server = spawn("node", [join(__dirname, "dist", "index.js")], {
  env: { ...process.env, TASKMAN_MCP_TRANSPORT: "stdio" },
  stdio: ["pipe", "pipe", "pipe"],
});

let outputBuffer = "";
const pendingRequests = new Map();
let requestId = 1;

function sendRequest(method, params = {}) {
  const id = requestId++;
  const request = { jsonrpc: "2.0", id, method, params };

  return new Promise((resolve, reject) => {
    pendingRequests.set(id, { resolve, reject });
    server.stdin.write(JSON.stringify(request) + "\n");

    setTimeout(() => {
      if (pendingRequests.has(id)) {
        pendingRequests.delete(id);
        reject(new Error("Timeout"));
      }
    }, 10000);
  });
}

server.stderr.on("data", () => {});

server.stdout.on("data", (data) => {
  outputBuffer += data.toString();
  const lines = outputBuffer.split("\n");
  outputBuffer = lines.pop() || "";

  for (const line of lines) {
    if (!line.trim() || line.includes('[AUDIT]')) continue;

    try {
      const response = JSON.parse(line);

      if (response.id && pendingRequests.has(response.id)) {
        const { resolve, reject } = pendingRequests.get(response.id);
        pendingRequests.delete(response.id);

        if (response.error) {
          reject(new Error(response.error.message));
        } else {
          resolve(response.result);
        }
      }
    } catch (e) {}
  }
});

await new Promise(resolve => setTimeout(resolve, 2000));

async function test() {
  try {
    console.log("Test 1: task_create");
    const r1 = await sendRequest("tools/call", {
      name: "task_create",
      arguments: {
        task: {
          title: "Minimal Test",
          project_id: "P-8767f2bc",
          status: "new",
          work_type: "task"
        }
      }
    });

    const taskId = r1.structuredContent.task.id;
    console.log(`✅ Created: ${taskId}\n`);

    console.log("Test 2: task_read");
    const r2 = await sendRequest("tools/call", {
      name: "task_read",
      arguments: { taskId }
    });
    console.log(`✅ Read: ${r2.structuredContent.task.title}\n`);

    console.log("Test 3: task_delete");
    await sendRequest("tools/call", {
      name: "task_delete",
      arguments: { taskId }
    });
    console.log("✅ Deleted\n");

    console.log("✅✅✅ ALL TESTS PASSED ✅✅✅");

    server.kill();
    process.exit(0);
  } catch (e) {
    console.error("❌", e.message);
    server.kill();
    process.exit(1);
  }
}

test();
