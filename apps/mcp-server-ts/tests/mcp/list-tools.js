/**
 * List all available MCP tools - debugging script
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

async function listTools() {
  const transport = new StdioClientTransport({
    command: "node",
    args: ["dist/index.js"],
  });

  const client = new Client(
    {
      name: "test-client",
      version: "1.0.0",
    },
    {
      capabilities: {},
    }
  );

  await client.connect(transport);
  console.log("✅ Connected to MCP server\n");

  const toolsResponse = await client.listTools();
  console.log(`📋 Available tools: ${toolsResponse.tools.length}\n`);

  for (const tool of toolsResponse.tools) {
    console.log(`🔧 ${tool.name}`);
    console.log(`   ${tool.description}`);
    console.log();
  }

  await client.close();
}

listTools().catch((error) => {
  console.error("❌ Error:", error.message);
  process.exit(1);
});
