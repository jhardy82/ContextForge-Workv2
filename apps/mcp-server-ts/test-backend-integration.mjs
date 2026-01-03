/**
 * Backend Integration & Locking Behavior Test
 * Tests BackendClient methods, locking service, and audit logging
 */

// IMPORTANT: Set environment variable BEFORE importing modules
process.env.TASK_MANAGER_API_ENDPOINT = "http://localhost:3001/api/v1";

import { backendClient } from "./dist/backend/client.js";
import { lockingService } from "./dist/infrastructure/locking.js";
import { auditLog } from "./dist/infrastructure/audit.js";

// Verify configuration
console.log(`Backend API Endpoint: ${process.env.TASK_MANAGER_API_ENDPOINT}\n`);

console.log("=== Backend Integration & Locking Test ===\n");

const TEST_AGENT = "test-agent";
let testProjectId = null;
let testActionListId = null;
let testsPassed = 0;
let testsFailed = 0;

function logTest(name, passed, details = "") {
  const status = passed ? "✅ PASS" : "❌ FAIL";
  console.log(`${status}: ${name}`);
  if (details) console.log(`   ${details}`);
  if (passed) testsPassed++;
  else testsFailed++;
}

async function runTests() {
  try {
    // ===== Test 1: Create Project (prerequisite) =====
    console.log("\n--- Test 1: Create Test Project ---");
    try {
      const project = await backendClient.createProject({
        id: `P-TEST-${Date.now()}`,
        name: "Integration Test Project",
        description: "For backend integration testing",
        status: "active",
      });
      testProjectId = project.id;
      logTest("Create project", !!testProjectId, `Project ID: ${testProjectId}`);
    } catch (error) {
      logTest("Create project", false, error.message);
      throw error; // Can't continue without project
    }

    // ===== Test 2: Create ActionList =====
    console.log("\n--- Test 2: Create ActionList ---");
    try {
      const actionList = await backendClient.createActionList({
        id: `AL-TEST-${Date.now()}`,
        title: "Test Action List",
        description: "Integration test list",
        status: "active",
        project_id: testProjectId,
        priority: "medium",
        notes: "Testing backend client methods",
      });
      testActionListId = actionList.id;
      logTest("Create ActionList", !!testActionListId, `ActionList ID: ${testActionListId}`);
      logTest("Verify computed properties",
        actionList.total_items === 0 && actionList.completed_items === 0,
        `total_items=${actionList.total_items}, completed_items=${actionList.completed_items}`);
    } catch (error) {
      logTest("Create ActionList", false, error.message);
      throw error;
    }

    // ===== Test 3: Get ActionList =====
    console.log("\n--- Test 3: Read ActionList ---");
    try {
      const retrieved = await backendClient.getActionList(testActionListId);
      logTest("Read ActionList by ID", retrieved.id === testActionListId, `Retrieved: ${retrieved.name}`);
    } catch (error) {
      logTest("Read ActionList by ID", false, error.message);
    }

    // ===== Test 4: List ActionLists with Filters =====
    console.log("\n--- Test 4: List ActionLists ---");
    try {
      const allLists = await backendClient.listActionLists();
      logTest("List all ActionLists", Array.isArray(allLists), `Found ${allLists.length} lists`);

      const projectFiltered = await backendClient.listActionLists({ project_id: testProjectId });
      logTest("Filter by project_id",
        projectFiltered.some(al => al.id === testActionListId),
        `Found ${projectFiltered.length} lists for project`);
    } catch (error) {
      logTest("List ActionLists", false, error.message);
    }

    // ===== Test 5: Add Item =====
    console.log("\n--- Test 5: Add Item ---");
    try {
      const withItem = await backendClient.addActionListItem(testActionListId, {
        text: "Test item 1",
        order: 0,
      });
      logTest("Add item to ActionList",
        withItem.total_items === 1,
        `Items: ${withItem.total_items}, Progress: ${withItem.progress_percentage}%`);
    } catch (error) {
      logTest("Add item", false, error.message);
    }

    // ===== Test 6: Toggle Item =====
    console.log("\n--- Test 6: Toggle Item ---");
    try {
      const current = await backendClient.getActionList(testActionListId);
      const itemId = current.items[0].id;

      const toggled = await backendClient.toggleActionListItem(testActionListId, itemId);
      logTest("Toggle item completion",
        toggled.completed_items === 1 && toggled.progress_percentage === 100.0,
        `Progress: ${toggled.completed_items}/${toggled.total_items} = ${toggled.progress_percentage}%`);
    } catch (error) {
      logTest("Toggle item", false, error.message);
    }

    // ===== Test 7: Update ActionList =====
    console.log("\n--- Test 7: Update ActionList ---");
    try {
      const updated = await backendClient.updateActionList(testActionListId, {
        name: "Updated Test List",
        priority: "high",
        notes: "Updated notes with new information",
      });
      logTest("Update ActionList",
        updated.name === "Updated Test List" && updated.priority === "high",
        `Name: ${updated.name}, Priority: ${updated.priority}`);
    } catch (error) {
      logTest("Update ActionList", false, error.message);
    }

    // ===== Test 8: Locking Service =====
    console.log("\n--- Test 8: Locking Service ---");
    try {
      // Acquire lock
      const acquired = lockingService.checkout("action-list", testActionListId, TEST_AGENT);
      logTest("Acquire lock", acquired, `Lock acquired by ${TEST_AGENT}`);

      // Try to acquire same lock (should fail)
      const reacquire = lockingService.checkout("action-list", testActionListId, "another-agent");
      logTest("Lock prevents concurrent access", !reacquire, "Second agent blocked");

      // Release lock
      lockingService.checkin("action-list", testActionListId, TEST_AGENT);

      // Now should be able to acquire
      const afterRelease = lockingService.checkout("action-list", testActionListId, "another-agent");
      logTest("Lock released successfully", afterRelease, "Lock available after release");
      lockingService.checkin("action-list", testActionListId, "another-agent");
    } catch (error) {
      logTest("Locking service", false, error.message);
    }

    // ===== Test 9: Audit Logging =====
    console.log("\n--- Test 9: Audit Logging ---");
    try {
      // Audit logging is passive - just verify it doesn't throw
      auditLog({
        operation: "test_operation",
        agent: TEST_AGENT,
        result: "success",
        details: {
          message: "Integration test audit log",
        },
      });
      logTest("Audit logging", true, "Audit log written without errors");
    } catch (error) {
      logTest("Audit logging", false, error.message);
    }

    // ===== Test 10: Remove Item =====
    console.log("\n--- Test 10: Remove Item ---");
    try {
      const current = await backendClient.getActionList(testActionListId);
      const itemId = current.items[0].id;

      const afterRemove = await backendClient.removeActionListItem(testActionListId, itemId);
      logTest("Remove item from ActionList",
        afterRemove.total_items === 0,
        `Items remaining: ${afterRemove.total_items}`);
    } catch (error) {
      logTest("Remove item", false, error.message);
    }

    // ===== Test 11: Delete ActionList =====
    console.log("\n--- Test 11: Delete ActionList ---");
    try {
      await backendClient.deleteActionList(testActionListId);

      // Verify deletion (should throw 404)
      let deleted = true;
      try {
        await backendClient.getActionList(testActionListId);
        deleted = false; // If we get here, it wasn't deleted
      } catch (error) {
        // Expected to throw
      }
      logTest("Delete ActionList", deleted, "ActionList successfully deleted");
    } catch (error) {
      logTest("Delete ActionList", false, error.message);
    }

    // ===== Summary =====
    console.log("\n=== Test Summary ===");
    console.log(`Total Tests: ${testsPassed + testsFailed}`);
    console.log(`✅ Passed: ${testsPassed}`);
    console.log(`❌ Failed: ${testsFailed}`);

    if (testsFailed === 0) {
      console.log("\n✅ SUCCESS: All backend integration tests passed!");
      process.exit(0);
    } else {
      console.log(`\n❌ FAILURE: ${testsFailed} test(s) failed`);
      process.exit(1);
    }

  } catch (error) {
    console.error("\n❌ FATAL ERROR:", error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Run tests
runTests();
