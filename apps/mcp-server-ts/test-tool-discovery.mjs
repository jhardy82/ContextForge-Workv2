/**
 * Simple MCP Tool Discovery Test
 * Starts the MCP server and sends a tools/list request via JSON-RPC
 */

import { spawn } from "child_process";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log("=== MCP Tool Discovery Test ===\n");
console.log("Starting TaskMan MCP v2 server...\n");

// Start the MCP server process
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
let responseReceived = false;

// Handle server stderr (logs)
server.stderr.on("data", (data) => {
  const message = data.toString();
  console.error("[Server Log]", message.trim());
});

// Handle server stdout (JSON-RPC responses)
server.stdout.on("data", (data) => {
  outputBuffer += data.toString();

  // Try to parse complete JSON-RPC messages
  const lines = outputBuffer.split("\n");
  outputBuffer = lines.pop() || ""; // Keep incomplete line in buffer

  for (const line of lines) {
    if (!line.trim()) continue;

    try {
      const response = JSON.parse(line);

      if (response.result?.tools) {
        responseReceived = true;
        const tools = response.result.tools;
        const actionListTools = tools.filter(t => t.name.startsWith("action_list_"));

        console.log("\n✅ MCP Server Response Received\n");
        console.log(`Total tools: ${tools.length}`);
        console.log(`ActionList tools: ${actionListTools.length}\n`);

        console.log("ActionList Tools Discovered:");
        console.log("=============================");
        actionListTools.forEach((tool, i) => {
          console.log(`${i + 1}. ${tool.name}`);
          console.log(`   Description: ${tool.description || "(none)"}`);
        });

        if (actionListTools.length === 9) {
          console.log("\n✅ SUCCESS: All 9 ActionList tools discovered!");
          server.kill();
          process.exit(0);
        } else {
          console.log(`\n❌ FAILURE: Expected 9 tools, found ${actionListTools.length}`);
          server.kill();
          process.exit(1);
        }
      }
    } catch (e) {
      // Not valid JSON or incomplete message
    }
  }
});

// Handle server exit
server.on("exit", (code) => {
  if (!responseReceived) {
    console.error("\n❌ Server exited before sending tools/list response");
    console.error(`Exit code: ${code}`);
    process.exit(1);
  }
});

// Send tools/list request after server starts
setTimeout(() => {
  const request = {
    jsonrpc: "2.0",
    id: 1,
    method: "tools/list",
    params: {}
  };

  console.log("Sending tools/list request...\n");
  server.stdin.write(JSON.stringify(request) + "\n");
}, 1000);

// Timeout after 10 seconds
setTimeout(() => {
  if (!responseReceived) {
    console.error("\n❌ TIMEOUT: No response received after 10 seconds");
    server.kill();
    process.exit(1);
  }
}, 10000);
