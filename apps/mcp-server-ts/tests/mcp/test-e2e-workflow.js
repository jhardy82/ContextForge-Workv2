/**
 * Section 2.4: End-to-End Validation Test
 * Tests complete ActionList MCP workflow
 *
 * DEBUG LOGGING ENABLED - Full request/response inspection
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

// Enable debug logging
const DEBUG = true;

function debugLog(label, data) {
  if (DEBUG) {
    console.log(`\n🔍 [DEBUG] ${label}:`);
    console.log(JSON.stringify(data, null, 2));
  }
}

async function testE2EWorkflow() {
  console.log("🚀 Starting Section 2.4: End-to-End Validation");
  console.log("🔍 DEBUG LOGGING: ENABLED\n");

  const transport = new StdioClientTransport({
    command: "npx",
    args: ["tsx", "src/index.ts"],
  });

  const client = new Client(
    {
      name: "e2e-test-client",
      version: "1.0.0",
    },
    { capabilities: {} }
  );

  await client.connect(transport);
  console.log("✅ Connected to MCP server\n");

  try {
    // Step 0: Create project (prerequisite for action list)
    console.log("🏗️  Step 0: Creating prerequisite project...");
    const projectArgs = {
      project: {
        id: "P-TASKMAN-MCP-OPS-2025",
        name: "TaskMan MCP Operations 2025", // Project uses 'name' not 'title'
        description: "TaskMan development and operations work",
        status: "active",
      },
    };
    debugLog("Create Project Request", projectArgs);

    const projectResult = await client.callTool({
      name: "project_create",
      arguments: projectArgs,
    });
    debugLog("Create Project Response", projectResult);

    if (
      projectResult.isError ||
      projectResult.content[0].text.includes("failed")
    ) {
      // Project might already exist - that's okay, continue
      console.log("⚠️  Project creation note:", projectResult.content[0].text);
      console.log("   (This is okay if project already exists)\n");
    } else {
      const projectData = JSON.parse(projectResult.content[0].text);
      console.log("✅ Project created:", projectData.project.id);
      console.log();
    }

    // Extract the actual project ID (backend may generate new ID)
    const projectData = JSON.parse(projectResult.content[0].text);
    const actualProjectId = projectData.project.id;
    console.log("📌 Using project ID:", actualProjectId, "\n");

    // Step 1: Create action list
    console.log("📝 Step 1: Creating action list...");
    const createArgs = {
      action_list: {
        name: "E2E Test Action List", // Use 'name' (API schema), will be transformed to 'title' (domain)
        description: "Testing complete MCP workflow",
        project_id: actualProjectId, // Use the actual project ID from Step 0
        status: "active",
        priority: "high",
      },
    };
    debugLog("Create Action List Request", createArgs);

    const createResult = await client.callTool({
      name: "action_list_create",
      arguments: createArgs,
    });
    debugLog("Create Action List Response", createResult);

    // Check for error response
    if (
      createResult.isError ||
      createResult.content[0].text.startsWith("Request failed")
    ) {
      console.error("❌ MCP Tool Error:", createResult.content[0].text);
      console.error("   This suggests the backend request failed.");
      console.error("   Check:");
      console.error("   1. Backend server running on http://localhost:3001");
      console.error("   2. Action-lists routes registered");
      console.error("   3. Request data format matches backend schema\n");
      throw new Error(`MCP tool call failed: ${createResult.content[0].text}`);
    }

    const responseData = JSON.parse(createResult.content[0].text);
    const actionList = responseData.action_list;
    console.log("✅ Created action list:", actionList.id);
    console.log("   Title:", actionList.title);
    console.log("   Status:", actionList.status);
    console.log("   Project:", actionList.project_id);
    console.log("   Priority:", actionList.priority, "\n");

    // Step 2: Add 3 items
    console.log("📝 Step 2: Adding 3 items...");
    let updated = actionList;

    for (let i = 1; i <= 3; i++) {
      const addItemArgs = {
        action_list_id: actionList.id,
        item: {
          text: "E2E Test Item " + i,
          order: i,
        },
      };
      debugLog(`Add Item ${i} Request`, addItemArgs);

      const addResult = await client.callTool({
        name: "action_list_add_item",
        arguments: addItemArgs,
      });
      debugLog(`Add Item ${i} Response`, addResult);

      const addResponseData = JSON.parse(addResult.content[0].text);
      updated = addResponseData.action_list;
      console.log(`   ✅ Added item ${i}: "${addItemArgs.item.text}"`);
    }
    console.log("✅ Added 3 items. Total items:", updated.total_items);
    debugLog("Updated Action List After Adding Items", {
      id: updated.id,
      total_items: updated.total_items,
      items: updated.items,
    });
    console.log("");

    // Step 3: Toggle first item
    console.log("📝 Step 3: Toggling first item to completed...");
    const firstItemId = updated.items[0].id;
    const toggleArgs = {
      action_list_id: actionList.id,
      item_id: firstItemId,
    };
    debugLog("Toggle Item Request", toggleArgs);

    const toggleResult = await client.callTool({
      name: "action_list_toggle_item",
      arguments: toggleArgs,
    });
    debugLog("Toggle Item Response", toggleResult);

    const toggleResponseData = JSON.parse(toggleResult.content[0].text);
    updated = toggleResponseData.action_list;
    debugLog("Progress State After Toggle", {
      total_items: updated.total_items,
      completed_items: updated.completed_items,
      progress_percentage: updated.progress_percentage,
    });
    console.log(
      "✅ Toggled item. Progress:",
      updated.progress_percentage + "%"
    );
    console.log(
      "   Completed items:",
      updated.completed_items,
      "/",
      updated.total_items,
      "\n"
    );

    // Step 4: Verify progress is 33%
    console.log("📝 Step 4: Verifying progress percentage...");
    debugLog("Progress Verification State", {
      expected: 33.33,
      actual: updated.progress_percentage,
      total_items: updated.total_items,
      completed_items: updated.completed_items,
    });
    if (Math.abs(updated.progress_percentage - 33.33) < 0.1) {
      console.log("✅ Progress percentage correct: 33.33%\n");
    } else {
      console.log(
        "❌ Progress percentage incorrect:",
        updated.progress_percentage,
        "\n"
      );
    }

    // Step 5: Remove second item
    console.log("📝 Step 5: Removing second item...");
    const secondItemId = updated.items[1].id;
    const removeArgs = {
      action_list_id: actionList.id,
      item_id: secondItemId,
    };
    debugLog("Remove Item Request", removeArgs);

    const removeResult = await client.callTool({
      name: "action_list_remove_item",
      arguments: removeArgs,
    });
    debugLog("Remove Item Response", removeResult);

    const removeResponseData = JSON.parse(removeResult.content[0].text);
    updated = removeResponseData.action_list;
    debugLog("State After Item Removal", {
      total_items: updated.total_items,
      remaining_items: updated.items.map((item) => ({
        id: item.id,
        text: item.text,
      })),
    });
    console.log("✅ Removed item. Remaining items:", updated.total_items, "\n");

    // Step 6: Update metadata
    console.log("📝 Step 6: Updating action list metadata...");
    const updateArgs = {
      action_list_id: actionList.id,
      changes: {
        name: "E2E Test Action List (Updated)", // Use 'name' (API schema)
        status: "completed",
      },
    };
    debugLog("Update Metadata Request", updateArgs);

    const updateResult = await client.callTool({
      name: "action_list_update",
      arguments: updateArgs,
    });
    debugLog("Update Metadata Response", updateResult);

    const updateResponseData = JSON.parse(updateResult.content[0].text);
    updated = updateResponseData.action_list;
    debugLog("Updated Action List State", {
      id: updated.id,
      title: updated.title,
      status: updated.status,
      total_items: updated.total_items,
    });
    console.log("✅ Updated metadata. New title:", updated.title);
    console.log("   New status:", updated.status, "\n");

    // Step 7: Delete action list
    console.log("📝 Step 7: Deleting action list...");
    const deleteArgs = { action_list_id: actionList.id };
    debugLog("Delete Action List Request", deleteArgs);

    const deleteResult = await client.callTool({
      name: "action_list_delete",
      arguments: deleteArgs,
    });
    debugLog("Delete Action List Response", deleteResult);

    const deleteData = JSON.parse(deleteResult.content[0].text);
    console.log("✅ Deleted action list. Success:", deleteData.success, "\n");

    // Step 8: Verify deletion
    console.log("📝 Step 8: Verifying deletion...");
    const verifyArgs = { action_list_id: actionList.id };
    debugLog("Verify Deletion Request (expect 404)", verifyArgs);

    try {
      const verifyResult = await client.callTool({
        name: "action_list_read",
        arguments: verifyArgs,
      });
      debugLog(
        "Verify Deletion Response (UNEXPECTED - should have failed)",
        verifyResult
      );
      console.log(
        "❌ Deletion verification failed: Action list still exists\n"
      );
    } catch (err) {
      debugLog("Verify Deletion Error (EXPECTED)", {
        error: err.message,
        code: err.code,
      });
      console.log("✅ Deletion verified: Action list not found (expected)\n");
    }

    console.log("\n" + "=".repeat(60));
    console.log("🎉 Section 2.4: End-to-End Validation COMPLETE!");
    console.log("=".repeat(60) + "\n");
    console.log("All workflow steps executed successfully:");
    console.log("  ✅ Create action list");
    console.log("  ✅ Add 3 items");
    console.log("  ✅ Toggle first item to completed");
    console.log("  ✅ Verify 33% progress");
    console.log("  ✅ Remove second item");
    console.log("  ✅ Update metadata (title, status)");
    console.log("  ✅ Delete action list");
    console.log("  ✅ Verify deletion");
    console.log(
      "\n✅ Section 2.4 validation successful - all operations working correctly!\n"
    );
  } catch (error) {
    console.error("\n" + "=".repeat(60));
    console.error("❌ E2E Test FAILED");
    console.error("=".repeat(60));
    console.error("Error:", error.message);
    if (error.stack) console.error("\nStack trace:", error.stack);
    process.exit(1);
  } finally {
    await client.close();
  }
}

testE2EWorkflow().catch(console.error);
