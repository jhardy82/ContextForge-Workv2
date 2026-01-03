/**
 * Discover all MCP tools (not just action list tools)
 */

import { spawn } from "child_process";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log("=== MCP Tool Discovery Test (All Tools) ===\n");

const serverPath = join(__dirname, "dist", "index.js");
console.log("Starting TaskMan MCP v2 server...\n");

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
    }, 5000);
  });
}

server.stderr.on("data", (data) => {
  console.error("[Server Log]", data.toString().trim());
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
          reject(new Error(response.error.message || "Unknown error"));
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

console.log("Sending tools/list request...\n");

try {
  const result = await sendRequest("tools/list");

  console.log("\n✅ MCP Server Response Received\n");

  console.log(`Total tools: ${result.tools.length}\n`);

  // Group tools by prefix
  const grouped = {};
  result.tools.forEach(tool => {
    const prefix = tool.name.split("_")[0];
    if (!grouped[prefix]) grouped[prefix] = [];
    grouped[prefix].push(tool);
  });

  for (const [prefix, tools] of Object.entries(grouped)) {
    console.log(`${prefix.toUpperCase()} Tools: ${tools.length}`);
    console.log("=".repeat(60));
    tools.forEach((tool, i) => {
      console.log(`${i + 1}. ${tool.name}`);
      console.log(`   Description: ${tool.description}`);
    });
    console.log("");
  }

  server.kill();
  process.exit(0);

} catch (error) {
  console.error("\n❌ Error:", error.message);
  server.kill();
  process.exit(1);
}
