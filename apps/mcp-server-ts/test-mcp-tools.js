/**
 * Test script to verify MCP server tool registration
 * Tests ActionList tool discovery without requiring full MCP client
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { registerActionListFeatures } from "./dist/features/action-lists/register.js";

console.log("=== MCP Tool Discovery Test ===\n");

// Create a test MCP server instance
const server = new McpServer({
  name: "taskman-test",
  version: "0.1.0",
});

// Register ActionList features
console.log("Registering ActionList features...");
try {
  registerActionListFeatures(server);
  console.log("✅ ActionList features registered successfully\n");
} catch (error) {
  console.error("❌ Failed to register ActionList features:", error.message);
  process.exit(1);
}

// List all registered tools
console.log("Registered Tools:");
console.log("=================");

const toolNames = [
  "action_list_create",
  "action_list_read",
  "action_list_list",
  "action_list_update",
  "action_list_delete",
  "action_list_add_item",
  "action_list_toggle_item",
  "action_list_remove_item",
  "action_list_reorder_items",
];

let foundCount = 0;
for (const toolName of toolNames) {
  // Try to find tool in server's registered tools
  const found = server._tools?.has?.(toolName) || false;
  const status = found ? "✅" : "❌";
  console.log(`${status} ${toolName}`);
  if (found) foundCount++;
}

console.log(`\nDiscovery Result: ${foundCount}/${toolNames.length} tools found`);

if (foundCount === toolNames.length) {
  console.log("\n✅ SUCCESS: All 9 ActionList tools are registered");
  process.exit(0);
} else {
  console.log(`\n❌ FAILURE: Only ${foundCount}/9 tools found`);
  process.exit(1);
}
