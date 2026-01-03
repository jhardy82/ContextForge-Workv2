/**
 * FINAL: Task MCP Tools Validation - Based on working debug pattern
 */

process.env.TASK_MANAGER_API_ENDPOINT = "http://localhost:3001/api/v1";

import { spawn } from "child_process";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log("╔═══════════════════════════════════════════════════════════╗");
console.log("║       Task MCP Tools - Final Validation                  ║");
console.log("╚═══════════════════════════════════════════════════════════╝\n");

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
const pendingRequests = new Map();
let requestId = 1;

function sendRequest(method, params = {}) {
  const id = requestId++;
  const request = {
    jsonrpc: "2.0",
    id,
    method,
    params,
  };

  return new Promise((resolve, reject) => {
    pendingRequests.set(id, { resolve, reject, method });
    server.stdin.write(JSON.stringify(request) + "\n");

    setTimeout(() => {
      if (pendingRequests.has(id)) {
        pendingRequests.delete(id);
        reject(new Error(`Timeout`));
      }
    }, 15000);
  });
}

server.stderr.on("data", () => {
  // Suppress all stderr including AUDIT logs
});

server.stdout.on("data", (data) => {
  outputBuffer += data.toString();
  const lines = outputBuffer.split("\n");
  outputBuffer = lines.pop() || "";

  for (const line of lines) {
    if (!line.trim() || line.includes('[AUDIT]')) continue;

    try {
      const response = JSON.parse(line);

      if (response.id && pendingRequests.has(response.id)) {
        const { resolve, reject } = pendingRequests.get(response.id);
        pendingRequests.delete(response.id);

        if (response.error) {
          reject(new Error(`${response.error.code}: ${response.error.message}`));
        } else {
          resolve(response.result);
        }
      }
    } catch (e) {
      // Ignore parse errors
    }
  }
});

await new Promise(resolve => setTimeout(resolve, 2000));

const ACTION_LIST_ID = "AL-c3748b54";
const PROJECT_ID = "P-8767f2bc";

const ITEM_IDS = {
  task_create: "item-6c4cb335",
  task_read: "item-2d432c9e",
  task_list: "item-59a0aa3a",
  task_update: "item-69164f8c",
  task_delete: "item-220a79a4",
  task_search: "item-aa3a1a1d",
  task_assign: "item-b13816eb",
  task_set_status: "item-57728131",
  task_bulk_update: "item-5b30279f",
  relationships: "item-61bd3fe2",
  error_handling: "item-ed8d3f22",
};

const results = { passed: 0, failed: 0, tests: [] };
let testTaskId, testTaskIds = [], testSprintId;

function pass(name, itemId = null) {
  results.passed++;
  results.tests.push({ name, success: true, itemId });
  console.log(`✅ ${name}`);
}

function fail(name, error, itemId = null) {
  results.failed++;
  results.tests.push({ name, success: false, error: error.message, itemId });
  console.log(`❌ ${name}: ${error.message.substring(0, 60)}`);
}

async function toggle(itemId) {
  if (!itemId) return;
  try {
    await sendRequest("tools/call", {
      name: "action_list_toggle_item",
      arguments: { action_list_id: ACTION_LIST_ID, item_id: itemId }
    });
    console.log(`   📝 Marked complete\n`);
  } catch (e) {
    console.log(`   ⚠️  Could not update action list\n`);
  }
}

async function validate() {
  try {
    const { backendClient } = await import("./dist/backend/client.js");

    console.log("Initializing...");
    await backendClient.getProject(PROJECT_ID);
    console.log("✅ Project verified\n");

    // PHASE 1: CRUD
    console.log("═══ PHASE 1: Core CRUD ═══\n");

    try {
      const r = await sendRequest("tools/call", {
        name: "task_create",
        arguments: {
          task: {
            title: "Task Validation - Comprehensive Test",
            description: "Testing all Task MCP tools",
            project_id: PROJECT_ID,
            status: "new",
            work_type: "task",
            priority: "high",
            tags: ["validation", "automated"],
            estimated_hours: 3.0
          }
        }
      });
      testTaskId = r.structuredContent.task.id;
      pass("task_create", ITEM_IDS.task_create);
      await toggle(ITEM_IDS.task_create);
    } catch (e) {
      fail("task_create", e, ITEM_IDS.task_create);
      throw new Error("Cannot continue");
    }

    try {
      const r = await sendRequest("tools/call", {
        name: "task_read",
        arguments: { taskId: testTaskId }
      });
      if (r.structuredContent.task.id === testTaskId) {
        pass("task_read", ITEM_IDS.task_read);
        await toggle(ITEM_IDS.task_read);
      } else throw new Error("ID mismatch");
    } catch (e) { fail("task_read", e, ITEM_IDS.task_read); }

    try {
      const r = await sendRequest("tools/call", {
        name: "task_list",
        arguments: { project_id: PROJECT_ID, status: "new" }
      });
      if (r.structuredContent.tasks.find(t => t.id === testTaskId)) {
        pass("task_list", ITEM_IDS.task_list);
        await toggle(ITEM_IDS.task_list);
      } else throw new Error("Task not in list");
    } catch (e) { fail("task_list", e, ITEM_IDS.task_list); }

    try {
      const r = await sendRequest("tools/call", {
        name: "task_update",
        arguments: {
          taskId: testTaskId,
          changes: { title: "UPDATED Test", priority: "critical", estimated_hours: 5.0 }
        }
      });
      if (r.structuredContent.task.priority === "critical") {
        pass("task_update", ITEM_IDS.task_update);
        await toggle(ITEM_IDS.task_update);
      } else throw new Error("Update failed");
    } catch (e) { fail("task_update", e, ITEM_IDS.task_update); }

    // PHASE 2: SEARCH
    console.log("\n═══ PHASE 2: Search ═══\n");

    try {
      const r = await sendRequest("tools/call", {
        name: "task_search",
        arguments: { query: "Validation", project_id: PROJECT_ID }
      });
      if (r.structuredContent.tasks.find(t => t.id === testTaskId)) {
        pass("task_search", ITEM_IDS.task_search);
        await toggle(ITEM_IDS.task_search);
      } else throw new Error("Not found");
    } catch (e) { fail("task_search", e, ITEM_IDS.task_search); }

    // PHASE 3: SPECIALIZED
    console.log("\n═══ PHASE 3: Specialized ═══\n");

    try {
      const r = await sendRequest("tools/call", {
        name: "task_assign",
        arguments: { taskId: testTaskId, assignee: "TestUser" }
      });
      if (r.structuredContent.task.assignee === "TestUser") {
        pass("task_assign", ITEM_IDS.task_assign);
        await toggle(ITEM_IDS.task_assign);
      } else throw new Error("Assign failed");
    } catch (e) { fail("task_assign", e, ITEM_IDS.task_assign); }

    try {
      const r = await sendRequest("tools/call", {
        name: "task_set_status",
        arguments: { taskId: testTaskId, status: "in_progress" }
      });
      if (r.structuredContent.task.status === "in_progress") {
        pass("task_set_status", ITEM_IDS.task_set_status);
        await toggle(ITEM_IDS.task_set_status);
      } else throw new Error("Status not set");
    } catch (e) { fail("task_set_status", e, ITEM_IDS.task_set_status); }

    // PHASE 4: BULK
    console.log("\n═══ PHASE 4: Bulk Operations ═══\n");

    console.log("Creating 3 test tasks...");
    for (let i = 1; i <= 3; i++) {
      try {
        const r = await sendRequest("tools/call", {
          name: "task_create",
          arguments: { task: { title: `Bulk ${i}`, project_id: PROJECT_ID, status: "new", work_type: "task" } }
        });
        testTaskIds.push(r.structuredContent.task.id);
      } catch (e) {}
    }
    console.log(`✅ Created ${testTaskIds.length} tasks\n`);

    try {
      const r = await sendRequest("tools/call", {
        name: "task_bulk_update",
        arguments: { taskIds: testTaskIds, changes: { priority: "high" } }
      });
      if (r.structuredContent.updated_count === testTaskIds.length) {
        pass("task_bulk_update", ITEM_IDS.task_bulk_update);
        await toggle(ITEM_IDS.task_bulk_update);
      } else throw new Error("Count mismatch");
    } catch (e) { fail("task_bulk_update", e, ITEM_IDS.task_bulk_update); }

    try {
      const sprint = await backendClient.createSprint({
        name: "Validation Sprint",
        project_id: PROJECT_ID,
        status: "active"
      });
      testSprintId = sprint.id;

      const r = await sendRequest("tools/call", {
        name: "task_bulk_assign_sprint",
        arguments: { taskIds: testTaskIds, sprintId: testSprintId }
      });
      if (r.structuredContent.assigned_count === testTaskIds.length) {
        pass("task_bulk_assign_sprint");
      } else throw new Error("Count mismatch");
    } catch (e) { fail("task_bulk_assign_sprint", e); }

    // PHASE 5: INTEGRATION
    console.log("\n═══ PHASE 5: Integration ═══\n");

    try {
      const r = await sendRequest("tools/call", {
        name: "task_create",
        arguments: { task: { title: "Child", project_id: PROJECT_ID, status: "new", work_type: "task", parent_task_id: testTaskId } }
      });
      if (r.structuredContent.task.parent_task_id === testTaskId) {
        pass("Relationships", ITEM_IDS.relationships);
        await toggle(ITEM_IDS.relationships);
        testTaskIds.push(r.structuredContent.task.id);
      } else throw new Error("Parent not set");
    } catch (e) { fail("Relationships", e, ITEM_IDS.relationships); }

    try {
      let errors = 0;
      try { await sendRequest("tools/call", { name: "task_read", arguments: { taskId: "T-fake" } }); } catch { errors++; }
      try { await sendRequest("tools/call", { name: "task_create", arguments: { task: {} } }); } catch { errors++; }
      try { await sendRequest("tools/call", { name: "task_update", arguments: { taskId: testTaskId, changes: {} } }); } catch { errors++; }

      if (errors === 3) {
        pass("Error Handling", ITEM_IDS.error_handling);
        await toggle(ITEM_IDS.error_handling);
      } else throw new Error(`Only ${errors}/3`);
    } catch (e) { fail("Error Handling", e, ITEM_IDS.error_handling); }

    // CLEANUP
    console.log("\n═══ CLEANUP ═══\n");

    try {
      const all = [testTaskId, ...testTaskIds].filter(Boolean);
      let deleted = 0;
      for (const id of all) {
        try {
          await sendRequest("tools/call", { name: "task_delete", arguments: { taskId: id } });
          deleted++;
        } catch (e) {}
      }
      if (deleted === all.length) {
        pass("task_delete", ITEM_IDS.task_delete);
        await toggle(ITEM_IDS.task_delete);
      } else throw new Error(`Only ${deleted}/${all.length}`);
    } catch (e) { fail("task_delete", e, ITEM_IDS.task_delete); }

    // SUMMARY
    const total = results.passed + results.failed;
    const rate = ((results.passed / total) * 100).toFixed(1);

    console.log("\n╔═══════════════════════════════════════════════════════════╗");
    console.log("║                    SUMMARY                                ║");
    console.log("╚═══════════════════════════════════════════════════════════╝\n");
    console.log(`Total:   ${total}`);
    console.log(`✅ Pass: ${results.passed}`);
    console.log(`❌ Fail: ${results.failed}`);
    console.log(`Rate:    ${rate}%\n`);

    if (results.failed > 0) {
      console.log("Failed:");
      results.tests.filter(t => !t.success).forEach(t => console.log(`  ❌ ${t.name}`));
      console.log();
    }

    const list = await sendRequest("tools/call", {
      name: "action_list_read",
      arguments: { action_list_id: ACTION_LIST_ID }
    });

    console.log("Action List Progress:");
    console.log(`${list.structuredContent.action_list.completed_items}/${list.structuredContent.action_list.total_items} items (${list.structuredContent.action_list.progress_percentage}%)\n`);

    server.kill();
    process.exit(results.failed === 0 ? 0 : 1);

  } catch (e) {
    console.error("\n❌ FATAL:", e.message);
    server.kill();
    process.exit(1);
  }
}

validate();
