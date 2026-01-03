/**
 * MCP Protocol Compliance Test - Server
 *
 * Purpose: Validate SDK runtime behavior for CallToolResult field names
 * Evidence: CID-208 (Section 2.3 Phase 1 testing)
 *
 * Test Modes (via MCP_MODE env var):
 * - good: Returns structuredContent (correct per SDK spec)
 * - bad: Returns structured (current implementation, potentially wrong)
 * - both: Returns both fields (edge case validation)
 *
 * Expected Behavior (per SDK v1.20.2 source):
 * - structuredContent field MUST be present when outputSchema defined
 * - SDK should reject/ignore results with wrong field name
 *
 * Run: MCP_MODE=good node tests/mcp/test-server.js
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const mode = process.env.MCP_MODE ?? "good"; // good | bad | both

async function main() {
  console.error(`[SERVER] Starting MCP protocol test server in mode: ${mode}`);

  const server = new Server(
    {
      name: "taskman-mcp-protocol-test",
      version: "0.0.1",
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  // Register test tool with outputSchema (triggers structuredContent requirement)
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
      tools: [
        {
          name: "action_list_create",
          description: "Create an action list (protocol compliance test)",
          inputSchema: {
            type: "object",
            properties: {
              name: { type: "string", description: "Action list name" },
            },
            required: ["name"],
          },
          // 🚨 CRITICAL: Defining outputSchema triggers structuredContent requirement
          outputSchema: {
            type: "object",
            properties: {
              id: { type: "string" },
              name: { type: "string" },
            },
            required: ["id", "name"],
          },
        },
      ],
    };
  });

  // Tool invocation handler - returns different field names based on mode
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    if (request.params.name !== "action_list_create") {
      throw new Error(`Unknown tool: ${request.params.name}`);
    }

    const args = request.params.arguments as any;
    const payload = {
      id: "test-list-001",
      name: args.name ?? "Unnamed List",
    };

    console.error(`[SERVER] Tool invoked in ${mode} mode`);
    console.error(`[SERVER] Payload:`, JSON.stringify(payload));

    // Return different field configurations based on test mode
    if (mode === "good") {
      // ✅ CORRECT: SDK spec requires structuredContent
      console.error(`[SERVER] Returning structuredContent (correct)`);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(payload),
          },
        ],
        structuredContent: payload,
      } as any;
    }

    if (mode === "bad") {
      // ❌ WRONG: Current implementation uses 'structured'
      console.error(
        `[SERVER] Returning structured (incorrect - testing SDK rejection)`
      );
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(payload),
          },
        ],
        structured: payload, // Intentionally wrong field name
      } as any;
    }

    // mode === "both"
    // ⚠️ EDGE CASE: Both fields present (conflict scenario)
    console.error(`[SERVER] Returning both structured and structuredContent`);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(payload),
        },
      ],
      structured: payload,
      structuredContent: payload,
    } as any;
  });

  // Connect via stdio transport
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error(`[SERVER] Connected and ready for requests`);
}

main().catch((err) => {
  console.error("[SERVER] Fatal error:", err);
  process.exit(1);
});
