/**
 * End-to-End Workflow Test
 * Validates complete ActionList lifecycle (Section 2.4 requirement)
 *
 * Workflow Steps:
 * 1. Create ActionList for a project
 * 2. Add 3 items to the list
 * 3. Toggle first item to completed
 * 4. Verify progress_percentage = 33.33%
 * 5. Remove second item
 * 6. Update ActionList metadata (name, status)
 * 7. Delete ActionList
 */

// Set environment before imports
process.env.TASK_MANAGER_API_ENDPOINT = "http://localhost:3001/api/v1";

import { backendClient } from "./dist/backend/client.js";

console.log("=== End-to-End ActionList Workflow Test ===\n");

async function runWorkflow() {
  try {
    // Setup: Create project
    console.log("Setup: Creating test project...");
    const project = await backendClient.createProject({
      name: "E2E Workflow Project",
      description: "End-to-end workflow test",
      status: "active",
    });
    console.log(`✅ Project created: ${project.id}\n`);

    // Step 1: Create ActionList
    console.log("Step 1: Create ActionList for project");
    const actionList = await backendClient.createActionList({
      name: "E2E Test List",
      description: "Complete workflow test",
      status: "active",
      project_id: project.id,
      priority: "high",
      notes: "Testing complete ActionList lifecycle",
    });
    const actionListId = actionList.id;
    console.log(`✅ Created: ${actionListId}`);
    console.log(`   Items: ${actionList.total_items}, Completed: ${actionList.completed_items}, Progress: ${actionList.progress_percentage}%\n`);

    // Step 2: Add 3 items
    console.log("Step 2: Add 3 items to the list");

    const withItem1 = await backendClient.addActionListItem(actionListId, {
      text: "First workflow item",
      order: 0,
    });
    console.log(`✅ Added item 1: ${withItem1.items[0].id}`);

    const withItem2 = await backendClient.addActionListItem(actionListId, {
      text: "Second workflow item",
      order: 1,
    });
    console.log(`✅ Added item 2: ${withItem2.items[1].id}`);

    const withItem3 = await backendClient.addActionListItem(actionListId, {
      text: "Third workflow item",
      order: 2,
    });
    console.log(`✅ Added item 3: ${withItem3.items[2].id}`);
    console.log(`   Total items: ${withItem3.total_items}\n`);

    // Get item IDs
    const item1Id = withItem3.items[0].id;
    const item2Id = withItem3.items[1].id;
    const item3Id = withItem3.items[2].id;

    // Step 3: Toggle first item to completed
    console.log("Step 3: Toggle first item to completed");
    const afterToggle = await backendClient.toggleActionListItem(actionListId, item1Id);
    console.log(`✅ Toggled item: ${item1Id}`);
    console.log(`   Completed: ${afterToggle.items[0].completed}`);
    console.log(`   Progress: ${afterToggle.completed_items}/${afterToggle.total_items}\n`);

    // Step 4: Verify progress_percentage = 33.33%
    console.log("Step 4: Verify progress_percentage = 33.33%");
    const current = await backendClient.getActionList(actionListId);
    const expectedProgress = 33.33;
    const actualProgress = current.progress_percentage;

    if (Math.abs(actualProgress - expectedProgress) < 0.01) {
      console.log(`✅ Progress verification PASSED: ${actualProgress}% (expected ${expectedProgress}%)`);
    } else {
      console.log(`❌ Progress verification FAILED: ${actualProgress}% (expected ${expectedProgress}%)`);
      throw new Error("Progress percentage mismatch");
    }
    console.log(`   Completed items: ${current.completed_items}/${current.total_items}\n`);

    // Step 5: Remove second item
    console.log("Step 5: Remove second item");
    const afterRemove = await backendClient.removeActionListItem(actionListId, item2Id);
    console.log(`✅ Removed item: ${item2Id}`);
    console.log(`   Remaining items: ${afterRemove.total_items}`);
    console.log(`   Updated progress: ${afterRemove.completed_items}/${afterRemove.total_items} = ${afterRemove.progress_percentage}%\n`);

    // Step 6: Update ActionList metadata
    console.log("Step 6: Update ActionList metadata (name, status, notes)");
    const updated = await backendClient.updateActionList(actionListId, {
      name: "Updated E2E Test List",
      status: "completed",
      notes: "Workflow test completed successfully",
      priority: "medium",
    });
    console.log(`✅ Updated ActionList`);
    console.log(`   Name: ${updated.name || 'N/A'}`);
    console.log(`   Status: ${updated.status}`);
    console.log(`   Priority: ${updated.priority}`);
    console.log(`   Completed At: ${updated.completed_at ? 'Set' : 'Not set'}\n`);

    // Step 7: Delete ActionList
    console.log("Step 7: Delete ActionList");
    await backendClient.deleteActionList(actionListId);
    console.log(`✅ Deleted ActionList: ${actionListId}`);

    // Verify deletion
    let deleted = true;
    try {
      await backendClient.getActionList(actionListId);
      deleted = false;
    } catch (error) {
      // Expected to throw 404
    }

    if (deleted) {
      console.log(`✅ Deletion verified (404 on GET)\n`);
    } else {
      throw new Error("ActionList was not deleted");
    }

    // Success Summary
    console.log("=== Workflow Test Summary ===");
    console.log("✅ All 7 steps completed successfully!");
    console.log("\nWorkflow Validated:");
    console.log("  1. ✅ Create ActionList");
    console.log("  2. ✅ Add 3 items");
    console.log("  3. ✅ Toggle item completion");
    console.log("  4. ✅ Verify progress calculation (33.33%)");
    console.log("  5. ✅ Remove item");
    console.log("  6. ✅ Update metadata");
    console.log("  7. ✅ Delete ActionList");
    console.log("\n✅ SUCCESS: Complete end-to-end workflow validated!");

    process.exit(0);

  } catch (error) {
    console.error("\n❌ WORKFLOW FAILED:", error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

runWorkflow();
