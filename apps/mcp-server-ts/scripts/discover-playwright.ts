import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function main() {
  console.error("Starting Playwright MCP Server Discovery...");

  // We assume this script is run from the project root using tsx
  // e.g. npx tsx mcp-server-ts/scripts/discover-playwright.ts
  const rootDir = process.cwd();

  const transport = new StdioClientTransport({
    command: "npx.cmd",
    args: ["playwright", "run-mcp-server"],
    cwd: rootDir,
  });

  const client = new Client(
    {
      name: "DiscoveryClient",
      version: "1.0.0",
    },
    {
      capabilities: {},
    }
  );

  console.error("Connecting to server...");
  await client.connect(transport);
  console.error("Connected!");

  console.error("Listing tools...");
  const tools = await client.listTools();
  console.log(JSON.stringify(tools, null, 2));

  await client.close();
  process.exit(0);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
