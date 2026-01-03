/**
 * Quick diagnostic: List all registered MCP tools
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
  const request = {
    jsonrpc: "2.0",
    id,
    method,
    params,
  };

  return new Promise((resolve, reject) => {
    pendingRequests.set(id, { resolve, reject });
    server.stdin.write(JSON.stringify(request) + "\n");

    setTimeout(() => {
      if (pendingRequests.has(id)) {
        pendingRequests.delete(id);
        reject(new Error("Timeout"));
      }
    }, 5000);
  });
}

server.stderr.on("data", () => {});

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
          reject(new Error(response.error.message));
        } else {
          resolve(response.result);
        }
      }
    } catch (e) {}
  }
});

await new Promise(resolve => setTimeout(resolve, 2000));

try {
  const result = await sendRequest("tools/list", {});
  const tools = result.tools || [];

  console.log(`\n=== All Registered Tools (${tools.length}) ===\n`);

  const categories = {
    "Task Tools": tools.filter(t => t.name.startsWith("task_")),
    "Project Tools": tools.filter(t => t.name.startsWith("project_")),
    "Sprint Tools": tools.filter(t => t.name.startsWith("sprint_")),
    "Action List Tools": tools.filter(t => t.name.includes("action")),
    "Other Tools": tools.filter(t =>
      !t.name.startsWith("task_") &&
      !t.name.startsWith("project_") &&
      !t.name.startsWith("sprint_") &&
      !t.name.includes("action")
    ),
  };

  for (const [category, toolsList] of Object.entries(categories)) {
    if (toolsList.length > 0) {
      console.log(`${category} (${toolsList.length}):`);
      toolsList.forEach(t => console.log(`  - ${t.name}`));
      console.log();
    }
  }

} catch (error) {
  console.error("Error:", error.message);
} finally {
  server.kill();
  process.exit(0);
}
