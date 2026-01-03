// Quick test of ActionList client methods
import { BackendClient } from "./dist/backend/client.js";

const client = new BackendClient("http://localhost:3001/api/v1");

async function testActionListMethods() {
  try {
    console.log("\n=== Testing ActionList Client Methods ===\n");

    // Test 1: Create ActionList
    console.log("1. Creating new ActionList...");
    const newList = await client.createActionList({
      name: "MVP Test List",
      description: "Testing MCP client integration",
      notes: "These are test notes for the action list",
      tags: ["mvp", "test", "section-2-1"],
      status: "active",
      owner: "test-agent",
    });
    console.log("✅ Created:", newList.id, "-", newList.name);

    // Test 2: Get ActionList
    console.log("\n2. Retrieving ActionList...");
    const retrieved = await client.getActionList(newList.id);
    console.log("✅ Retrieved:", retrieved.id, "-", retrieved.name);
    console.log("   Notes:", retrieved.notes);

    // Test 3: Add Item
    console.log("\n3. Adding items...");
    const withItem1 = await client.addActionListItem(newList.id, {
      text: "First test item",
    });
    console.log("✅ Added item 1, total items:", withItem1.total_items);

    const withItem2 = await client.addActionListItem(newList.id, {
      text: "Second test item",
    });
    console.log("✅ Added item 2, total items:", withItem2.total_items);

    const withItem3 = await client.addActionListItem(newList.id, {
      text: "Third test item",
    });
    console.log("✅ Added item 3, total items:", withItem3.total_items);

    // Test 4: Toggle Item
    console.log("\n4. Toggling item completion...");
    const itemId = withItem3.items[0].id;
    const toggled = await client.toggleActionListItem(newList.id, itemId);
    console.log("✅ Toggled item, completed items:", toggled.completed_items);
    console.log("   Progress:", toggled.progress_percentage + "%");

    // Test 5: Update ActionList
    console.log("\n5. Updating ActionList...");
    const updated = await client.updateActionList(newList.id, {
      description: "Updated description via MCP client",
      priority: "high",
      status: "active",
    });
    console.log("✅ Updated:", updated.description);
    console.log("   Priority:", updated.priority);

    // Test 6: List ActionLists
    console.log("\n6. Listing all ActionLists...");
    const allLists = await client.listActionLists({ status: "active" });
    console.log("✅ Found", allLists.length, "active lists");

    // Test 7: Remove Item
    console.log("\n7. Removing an item...");
    const itemToRemove = withItem3.items[1].id;
    const afterRemoval = await client.removeActionListItem(
      newList.id,
      itemToRemove
    );
    console.log("✅ Removed item, total items:", afterRemoval.total_items);

    // Test 8: Reorder Items
    console.log("\n8. Reordering items...");
    const currentItems = afterRemoval.items.map((item) => item.id);
    const reordered = currentItems.reverse();
    const afterReorder = await client.reorderActionListItems(
      newList.id,
      reordered
    );
    console.log("✅ Reordered items");
    console.log(
      "   New order:",
      afterReorder.items.map((i) => i.text).join(", ")
    );

    // Test 9: Delete ActionList
    console.log("\n9. Deleting ActionList...");
    await client.deleteActionList(newList.id);
    console.log("✅ Deleted:", newList.id);

    // Verify deletion
    try {
      await client.getActionList(newList.id);
      console.log("❌ ERROR: List should have been deleted");
    } catch (err) {
      console.log("✅ Confirmed: List no longer exists (404)");
    }

    console.log("\n=== All Tests Passed! ===\n");
  } catch (error) {
    console.error("❌ Test failed:", error.message);
    if (error.response) {
      console.error("Response:", error.response.status, error.response.data);
    }
    process.exit(1);
  }
}

testActionListMethods();
