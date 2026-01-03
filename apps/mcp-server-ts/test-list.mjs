import { spawn } from "child_process";

// Set API endpoint
process.env.TASK_MANAGER_API_ENDPOINT = "http://localhost:3001/api/v1";

// Spawn MCP server
const server = spawn("node", ["dist/index.js"], {
  stdio: ["pipe", "pipe", "inherit"],
  env: { ...process.env },
});

let requestId = 1;
const pendingRequests = new Map();

function sendRequest(method, params) {
  return new Promise((resolve, reject) => {
    const id = requestId++;
    const request = {
      jsonrpc: "2.0",
      id,
      method,
      params,
    };

    pendingRequests.set(id, { resolve, reject });

    server.stdin.write(JSON.stringify(request) + "\n");

    setTimeout(() => {
      if (pendingRequests.has(id)) {
        pendingRequests.delete(id);
        reject(new Error(`Request ${id} timed out`));
      }
    }, 5000);
  });
}

server.stdout.on("data", (data) => {
  const lines = data
    .toString()
    .split("\n")
    .filter((l) => l.trim());
  for (const line of lines) {
    try {
      const response = JSON.parse(line);
      if (response.id && pendingRequests.has(response.id)) {
        const { resolve } = pendingRequests.get(response.id);
        pendingRequests.delete(response.id);
        resolve(response.result);
      }
    } catch (e) {
      // Not JSON, ignore
    }
  }
});

// Wait for server to initialize
await new Promise((resolve) => setTimeout(resolve, 2000));

try {
  // Make 3 sequential calls like the validation script does
  for (let i = 1; i <= 3; i++) {
    console.log(`\nCall #${i}: Testing action_list_list tool...`);
    const result = await sendRequest("tools/call", {
      name: "action_list_list",
      arguments: { project_id: "P-0002", limit: 10 },
    });

    if (result.structuredContent) {
      console.log(
        `✅ Call #${i} SUCCESS - Got ${
          result.structuredContent.action_lists?.length ?? 0
        } action lists`
      );
    } else {
      console.log(`❌ Call #${i} FAILED - No structuredContent!`);
      console.log("Result keys:", Object.keys(result));
      break;
    }

    // Small delay between calls
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
} catch (error) {
  console.error("❌ EXCEPTION:", error.message);
  console.error(error.stack);
} finally {
  server.kill();
  process.exit(0);
}
