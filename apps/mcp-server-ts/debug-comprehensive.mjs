/**
 * Debug comprehensive test - Add logging to see actual responses
 */

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
  const request = { jsonrpc: "2.0", id, method, params };

  return new Promise((resolve, reject) => {
    pendingRequests.set(id, { resolve, reject });
    server.stdin.write(JSON.stringify(request) + "\n");

    setTimeout(() => {
      if (pendingRequests.has(id)) {
        pendingRequests.delete(id);
        reject(new Error("Timeout"));
      }
    }, 15000);
  });
}

server.stderr.on("data", (data) => {
  console.error("[STDERR]", data.toString().trim());
});

server.stdout.on("data", (data) => {
  console.log("[STDOUT-RAW]", data.toString());

  outputBuffer += data.toString();
  const lines = outputBuffer.split("\n");
  outputBuffer = lines.pop() || "";

  for (const line of lines) {
    if (!line.trim()) continue;
    if (line.includes('[AUDIT]')) {
      console.log("[AUDIT-FILTERED]", line);
      continue;
    }

    console.log("[JSON-PARSE-ATTEMPT]", line);

    try {
      const response = JSON.parse(line);
      console.log("[PARSED-RESPONSE]", JSON.stringify(response, null, 2));

      if (response.id && pendingRequests.has(response.id)) {
        const { resolve, reject } = pendingRequests.get(response.id);
        pendingRequests.delete(response.id);

        if (response.error) {
          reject(new Error(`${response.error.code}: ${response.error.message}`));
        } else {
          console.log("[RESOLVING]", response.id);
          resolve(response.result);
        }
      }
    } catch (e) {
      console.error("[PARSE-ERROR]", e.message);
    }
  }
});

await new Promise(resolve => setTimeout(resolve, 2000));

const PROJECT_ID = "P-8767f2bc";

console.log("\n=== TEST START ===\n");

try {
  console.log("Sending task_create request...");
  const r = await sendRequest("tools/call", {
    name: "task_create",
    arguments: {
      task: {
        title: "Debug Comprehensive Test",
        project_id: PROJECT_ID,
        status: "new",
        work_type: "task"
      }
    }
  });

  console.log("\n[RECEIVED RESULT]", JSON.stringify(r, null, 2));
  console.log("\n[RESULT.structuredContent]", r.structuredContent);
  console.log("\n[RESULT.structuredContent.task]", r.structuredContent?.task);

  const taskId = r.structuredContent.task.id;
  console.log(`\n✅ SUCCESS! Task ID: ${taskId}`);

  server.kill();
  process.exit(0);

} catch (e) {
  console.error("\n❌ ERROR:", e.message);
  console.error(e.stack);
  server.kill();
  process.exit(1);
}
