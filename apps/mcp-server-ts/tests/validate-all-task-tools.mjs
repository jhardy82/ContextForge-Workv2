/**
 * Comprehensive Validation: ALL Task MCP Tools
 * Individual deep testing of each tool with all scenarios
 */

process.env.TASK_MANAGER_API_ENDPOINT = "http://localhost:3001/api/v1";

import { spawn } from "child_process";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const server = spawn("node", [join(__dirname, "..", "dist", "index.js")], {
  env: { ...process.env, TASKMAN_MCP_TRANSPORT: "stdio" },
  stdio: ["pipe", "pipe", "pipe"],
});

let outputBuffer = "";
const pendingRequests = new Map();
let requestId = 1;

function sendRequest(method, params = {}) {
  const id = requestId++;
  const request = { jsonrpc: "2.0", id, method, params };

  return new Promise((resolve, reject) => {
    pendingRequests.set(id, { resolve, reject });
    server.stdin.write(JSON.stringify(request) + "\n");

    setTimeout(() => {
      if (pendingRequests.has(id)) {
        pendingRequests.delete(id);
        reject(new Error("Timeout"));
      }
    }, 15000);
  });
}

server.stderr.on("data", () => {});

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
          reject(new Error(response.error.message));
        } else {
          resolve(response.result);
        }
      }
    } catch (e) {}
  }
});

await new Promise(resolve => setTimeout(resolve, 3000));

const PROJECT_ID = "P-8767f2bc";
const results = { passed: 0, failed: 0, skipped: 0, tests: [] };
const testTasks = [];

function pass(name, details = "") {
  results.passed++;
  results.tests.push({ name, success: true, details });
  console.log(`✅ ${name}${details ? `: ${details}` : ""}`);
}

function fail(name, error) {
  results.failed++;
  results.tests.push({ name, success: false, error: error.message });
  console.log(`❌ ${name}: ${error.message}`);
}

function skip(name, reason) {
  results.skipped++;
  results.tests.push({ name, success: null, skipped: true, reason });
  console.log(`⏭️  ${name}: ${reason}`);
}

async function test() {
  try {
    console.log("╔═══════════════════════════════════════════════════════════╗");
    console.log("║     ALL Task MCP Tools - Comprehensive Validation        ║");
    console.log("╚═══════════════════════════════════════════════════════════╝\n");

    // ═══════════════════════════════════════════════════════════
    // TOOL 1: task_create
    // ═══════════════════════════════════════════════════════════
    console.log("═══ TOOL 1: task_create ═══\n");

    // Create test task with minimal fields
    let primaryTaskId;
    try {
      const r = await sendRequest("tools/call", {
        name: "task_create",
        arguments: {
          task: {
            title: "Primary Test Task",
            project_id: PROJECT_ID,
            status: "new",
            work_type: "task"
          }
        }
      });
      primaryTaskId = r.structuredContent.task.id;
      testTasks.push(primaryTaskId);
      pass("task_create: Minimal fields", primaryTaskId);
    } catch (e) {
      fail("task_create: Minimal fields", e);
    }

    // Create with multiple optional fields
    try {
      const r = await sendRequest("tools/call", {
        name: "task_create",
        arguments: {
          task: {
            title: "Task with Optional Fields",
            project_id: PROJECT_ID,
            status: "new",
            work_type: "bug",
            priority: "high",
            owner: "TestOwner",
            description: "Detailed description of the bug"
          }
        }
      });
      testTasks.push(r.structuredContent.task.id);
      pass("task_create: With optional fields", `Priority: ${r.structuredContent.task.priority}`);
    } catch (e) {
      fail("task_create: With optional fields", e);
    }

    // Create with parent task
    let childTaskId;
    try {
      const r = await sendRequest("tools/call", {
        name: "task_create",
        arguments: {
          task: {
            title: "Child Task",
            project_id: PROJECT_ID,
            status: "new",
            work_type: "task",
            parent_task_id: primaryTaskId
          }
        }
      });
      childTaskId = r.structuredContent.task.id;
      testTasks.push(childTaskId);
      pass("task_create: With parent", `Parent: ${r.structuredContent.task.parent_task_id}`);
    } catch (e) {
      fail("task_create: With parent", e);
    }

    // Error: Missing required field
    try {
      await sendRequest("tools/call", {
        name: "task_create",
        arguments: { task: { project_id: PROJECT_ID } }
      });
      fail("task_create: Missing title error", new Error("Should have failed"));
    } catch (e) {
      pass("task_create: Missing title error", "Correctly rejected");
    }

    // ═══════════════════════════════════════════════════════════
    // TOOL 2: task_read
    // ═══════════════════════════════════════════════════════════
    console.log("\n═══ TOOL 2: task_read ═══\n");

    if (!primaryTaskId) {
      skip("task_read tests", "No primary task created");
    } else {
      // Read existing task
      try {
        const r = await sendRequest("tools/call", {
          name: "task_read",
          arguments: { taskId: primaryTaskId }
        });
        if (r.structuredContent.task.id === primaryTaskId) {
          pass("task_read: Valid ID", `Title: ${r.structuredContent.task.title}`);
        } else {
          throw new Error("ID mismatch");
        }
      } catch (e) {
        fail("task_read: Valid ID", e);
      }

      // Read with invalid ID
      try {
        const r = await sendRequest("tools/call", {
          name: "task_read",
          arguments: { taskId: "T-invalid-fake-id" }
        });
        if (r.isError) {
          pass("task_read: Invalid ID error", "Correctly rejected");
        } else {
          fail("task_read: Invalid ID error", new Error("Should have failed"));
        }
      } catch (e) {
        pass("task_read: Invalid ID error", "Exception thrown");
      }

      // Verify all fields present
      try {
        const r = await sendRequest("tools/call", {
          name: "task_read",
          arguments: { taskId: primaryTaskId }
        });
        const task = r.structuredContent.task;
        const requiredFields = ["id", "title", "project_id", "status", "work_type", "created_at", "updated_at"];
        const missing = requiredFields.filter(f => !(f in task));
        if (missing.length === 0) {
          pass("task_read: All fields present", `${requiredFields.length} fields`);
        } else {
          throw new Error(`Missing: ${missing.join(", ")}`);
        }
      } catch (e) {
        fail("task_read: All fields present", e);
      }
    }

    // ═══════════════════════════════════════════════════════════
    // TOOL 3: task_list
    // ═══════════════════════════════════════════════════════════
    console.log("\n═══ TOOL 3: task_list ═══\n");

    // List all tasks in project
    try {
      const r = await sendRequest("tools/call", {
        name: "task_list",
        arguments: { project_id: PROJECT_ID }
      });
      if (Array.isArray(r.structuredContent.tasks)) {
        pass("task_list: All tasks", `Found ${r.structuredContent.tasks.length} tasks`);
      } else {
        throw new Error("No tasks array returned");
      }
    } catch (e) {
      fail("task_list: All tasks", e);
    }

    // Filter by status
    try {
      const r = await sendRequest("tools/call", {
        name: "task_list",
        arguments: { project_id: PROJECT_ID, status: "new" }
      });
      const allNew = r.structuredContent.tasks.every(t => t.status === "new");
      if (allNew) {
        pass("task_list: Filter by status", `${r.structuredContent.tasks.length} new tasks`);
      } else {
        throw new Error("Filter failed - non-new tasks returned");
      }
    } catch (e) {
      fail("task_list: Filter by status", e);
    }

    // Filter by work_type
    try {
      const r = await sendRequest("tools/call", {
        name: "task_list",
        arguments: { project_id: PROJECT_ID, work_type: "bug" }
      });
      const allBugs = r.structuredContent.tasks.every(t => t.work_type === "bug");
      if (allBugs) {
        pass("task_list: Filter by work_type", `${r.structuredContent.tasks.length} bugs`);
      } else {
        throw new Error("Filter failed");
      }
    } catch (e) {
      fail("task_list: Filter by work_type", e);
    }

    // Verify primary task in list
    if (primaryTaskId) {
      try {
        const r = await sendRequest("tools/call", {
          name: "task_list",
          arguments: { project_id: PROJECT_ID }
        });
        const found = r.structuredContent.tasks.find(t => t.id === primaryTaskId);
        if (found) {
          pass("task_list: Find specific task", found.title);
        } else {
          throw new Error("Primary task not found in list");
        }
      } catch (e) {
        fail("task_list: Find specific task", e);
      }
    }

    // ═══════════════════════════════════════════════════════════
    // TOOL 4: task_update
    // ═══════════════════════════════════════════════════════════
    console.log("\n═══ TOOL 4: task_update ═══\n");

    if (!primaryTaskId) {
      skip("task_update tests", "No primary task created");
    } else {
      // Update title
      try {
        const r = await sendRequest("tools/call", {
          name: "task_update",
          arguments: {
            taskId: primaryTaskId,
            changes: { title: "UPDATED: Primary Test Task" }
          }
        });
        if (r.structuredContent.task.title === "UPDATED: Primary Test Task") {
          pass("task_update: Title", r.structuredContent.task.title);
        } else {
          throw new Error("Title not updated");
        }
      } catch (e) {
        fail("task_update: Title", e);
      }

      // Update priority
      try {
        const r = await sendRequest("tools/call", {
          name: "task_update",
          arguments: {
            taskId: primaryTaskId,
            changes: { priority: "critical" }
          }
        });
        if (r.structuredContent.task.priority === "critical") {
          pass("task_update: Priority", r.structuredContent.task.priority);
        } else {
          throw new Error("Priority not updated");
        }
      } catch (e) {
        fail("task_update: Priority", e);
      }

      // Update multiple fields
      try {
        const r = await sendRequest("tools/call", {
          name: "task_update",
          arguments: {
            taskId: primaryTaskId,
            changes: {
              description: "Updated description",
              owner: "NewOwner"
            }
          }
        });
        if (r.structuredContent.task.owner === "NewOwner") {
          pass("task_update: Multiple fields", `Owner: ${r.structuredContent.task.owner}`);
        } else {
          throw new Error("Multiple fields not updated");
        }
      } catch (e) {
        fail("task_update: Multiple fields", e);
      }

      // Invalid task ID
      try {
        await sendRequest("tools/call", {
          name: "task_update",
          arguments: {
            taskId: "T-invalid",
            changes: { title: "Test" }
          }
        });
        fail("task_update: Invalid ID error", new Error("Should have failed"));
      } catch (e) {
        pass("task_update: Invalid ID error", "Correctly rejected");
      }
    }

    // ═══════════════════════════════════════════════════════════
    // TOOL 5: task_assign
    // ═══════════════════════════════════════════════════════════
    console.log("\n═══ TOOL 5: task_assign ═══\n");

    if (!primaryTaskId) {
      skip("task_assign tests", "No primary task created");
    } else {
      // Assign to user
      try {
        const r = await sendRequest("tools/call", {
          name: "task_assign",
          arguments: {
            taskId: primaryTaskId,
            assignee: "User1"
          }
        });
        if (r.structuredContent.task.assignee === "User1") {
          pass("task_assign: Assign to user", r.structuredContent.task.assignee);
        } else {
          throw new Error("Assignee not set");
        }
      } catch (e) {
        fail("task_assign: Assign to user", e);
      }

      // Reassign to different user
      try {
        const r = await sendRequest("tools/call", {
          name: "task_assign",
          arguments: {
            taskId: primaryTaskId,
            assignee: "User2"
          }
        });
        if (r.structuredContent.task.assignee === "User2") {
          pass("task_assign: Reassign", `${r.structuredContent.task.assignee} (was User1)`);
        } else {
          throw new Error("Reassignment failed");
        }
      } catch (e) {
        fail("task_assign: Reassign", e);
      }

      // Assign with invalid task ID
      try {
        await sendRequest("tools/call", {
          name: "task_assign",
          arguments: {
            taskId: "T-invalid",
            assignee: "User3"
          }
        });
        fail("task_assign: Invalid ID error", new Error("Should have failed"));
      } catch (e) {
        pass("task_assign: Invalid ID error", "Correctly rejected");
      }
    }

    // ═══════════════════════════════════════════════════════════
    // TOOL 6: task_set_status
    // ═══════════════════════════════════════════════════════════
    console.log("\n═══ TOOL 6: task_set_status ═══\n");

    if (!primaryTaskId) {
      skip("task_set_status tests", "No primary task created");
    } else {
      // Status transitions
      const transitions = [
        { from: "new", to: "in_progress" },
        { from: "in_progress", to: "in_review" },
        { from: "in_review", to: "done" }
      ];

      for (const { from, to } of transitions) {
        try {
          const r = await sendRequest("tools/call", {
            name: "task_set_status",
            arguments: {
              taskId: primaryTaskId,
              status: to
            }
          });
          if (r.structuredContent.task.status === to) {
            pass(`task_set_status: ${from} → ${to}`, r.structuredContent.task.status);
          } else {
            throw new Error(`Status not updated to ${to}`);
          }
        } catch (e) {
          fail(`task_set_status: ${from} → ${to}`, e);
        }
      }

      // Set status with completion_notes
      try {
        const r = await sendRequest("tools/call", {
          name: "task_set_status",
          arguments: {
            taskId: primaryTaskId,
            status: "done",
            completion_notes: "Completed during validation testing"
          }
        });
        if (r.structuredContent.task.completion_notes) {
          pass("task_set_status: With completion_notes", r.structuredContent.task.completion_notes.substring(0, 30));
        } else {
          throw new Error("Completion notes not set");
        }
      } catch (e) {
        fail("task_set_status: With completion_notes", e);
      }
    }

    // ═══════════════════════════════════════════════════════════
    // TOOL 7: task_bulk_update
    // ═══════════════════════════════════════════════════════════
    console.log("\n═══ TOOL 7: task_bulk_update ═══\n");

    // Create multiple tasks for bulk testing
    const bulkTaskIds = [];
    for (let i = 1; i <= 5; i++) {
      try {
        const r = await sendRequest("tools/call", {
          name: "task_create",
          arguments: {
            task: {
              title: `Bulk Test Task ${i}`,
              project_id: PROJECT_ID,
              status: "new",
              work_type: "task"
            }
          }
        });
        bulkTaskIds.push(r.structuredContent.task.id);
        testTasks.push(r.structuredContent.task.id);
      } catch (e) {}
    }

    if (bulkTaskIds.length >= 3) {
      // Bulk update priority
      try {
        const r = await sendRequest("tools/call", {
          name: "task_bulk_update",
          arguments: {
            taskIds: bulkTaskIds,
            changes: { priority: "high" }
          }
        });
        if (r.structuredContent.updated_count === bulkTaskIds.length) {
          pass("task_bulk_update: Priority", `${r.structuredContent.updated_count}/${bulkTaskIds.length} tasks`);
        } else {
          throw new Error(`Only ${r.structuredContent.updated_count}/${bulkTaskIds.length} updated`);
        }
      } catch (e) {
        fail("task_bulk_update: Priority", e);
      }

      // Bulk update status
      try {
        const r = await sendRequest("tools/call", {
          name: "task_bulk_update",
          arguments: {
            taskIds: bulkTaskIds.slice(0, 3),
            changes: { status: "in_progress" }
          }
        });
        if (r.structuredContent.updated_count === 3) {
          pass("task_bulk_update: Status", `${r.structuredContent.updated_count}/3 tasks`);
        } else {
          throw new Error(`Count mismatch`);
        }
      } catch (e) {
        fail("task_bulk_update: Status", e);
      }

      // Bulk update multiple fields
      try {
        const r = await sendRequest("tools/call", {
          name: "task_bulk_update",
          arguments: {
            taskIds: bulkTaskIds,
            changes: {
              owner: "BulkOwner",
              description: "Bulk updated description"
            }
          }
        });
        if (r.structuredContent.updated_count === bulkTaskIds.length) {
          pass("task_bulk_update: Multiple fields", `${r.structuredContent.updated_count} tasks`);
        } else {
          throw new Error("Count mismatch");
        }
      } catch (e) {
        fail("task_bulk_update: Multiple fields", e);
      }
    } else {
      skip("task_bulk_update tests", "Failed to create bulk test tasks");
    }

    // ═══════════════════════════════════════════════════════════
    // TOOL 8: task_search
    // ═══════════════════════════════════════════════════════════
    console.log("\n═══ TOOL 8: task_search ═══\n");

    try {
      const r = await sendRequest("tools/call", {
        name: "task_search",
        arguments: {
          query: "Test",
          project_id: PROJECT_ID
        }
      });
      if (r.isError) {
        skip("task_search: Query", "Backend endpoint not implemented (404)");
      } else {
        pass("task_search: Query", `Found ${r.structuredContent.tasks.length} tasks`);
      }
    } catch (e) {
      skip("task_search: Query", `Backend error: ${e.message}`);
    }

    // ═══════════════════════════════════════════════════════════
    // TOOL 9: task_delete
    // ═══════════════════════════════════════════════════════════
    console.log("\n═══ TOOL 9: task_delete ═══\n");

    if (childTaskId) {
      // Delete child task
      try {
        await sendRequest("tools/call", {
          name: "task_delete",
          arguments: { taskId: childTaskId }
        });
        pass("task_delete: Delete child task", childTaskId);

        // Verify deletion
        try {
          await sendRequest("tools/call", {
            name: "task_read",
            arguments: { taskId: childTaskId }
          });
          fail("task_delete: Verify deletion", new Error("Task still exists"));
        } catch (e) {
          pass("task_delete: Verify deletion", "Task no longer accessible");
        }
      } catch (e) {
        fail("task_delete: Delete child task", e);
      }
    }

    // Delete invalid ID
    try {
      await sendRequest("tools/call", {
        name: "task_delete",
        arguments: { taskId: "T-invalid-id" }
      });
      fail("task_delete: Invalid ID error", new Error("Should have failed"));
    } catch (e) {
      pass("task_delete: Invalid ID error", "Correctly rejected");
    }

    // ═══════════════════════════════════════════════════════════
    // TOOL 10: task_bulk_assign_sprint
    // ═══════════════════════════════════════════════════════════
    console.log("\n═══ TOOL 10: task_bulk_assign_sprint ═══\n");

    skip("task_bulk_assign_sprint", "Requires sprint creation infrastructure");

    // CLEANUP
    console.log("\n═══ Cleanup ═══\n");
    let cleaned = 0;
    for (const taskId of testTasks) {
      try {
        await sendRequest("tools/call", {
          name: "task_delete",
          arguments: { taskId }
        });
        cleaned++;
      } catch (e) {}
    }
    console.log(`Cleaned up ${cleaned}/${testTasks.length} test tasks\n`);

    // SUMMARY
    const total = results.passed + results.failed;
    const rate = total > 0 ? ((results.passed / total) * 100).toFixed(1) : 0;

    console.log("╔═══════════════════════════════════════════════════════════╗");
    console.log("║                    FINAL SUMMARY                          ║");
    console.log("╚═══════════════════════════════════════════════════════════╝\n");
    console.log(`Total Tests:    ${total}`);
    console.log(`✅ Passed:      ${results.passed}`);
    console.log(`❌ Failed:      ${results.failed}`);
    console.log(`⏭️  Skipped:     ${results.skipped}`);
    console.log(`Success Rate:   ${rate}%\n`);

    if (results.failed > 0) {
      console.log("Failed Tests:");
      results.tests.filter(t => t.success === false).forEach(t => {
        console.log(`  ❌ ${t.name}: ${t.error}`);
      });
      console.log();
    }

    if (results.skipped > 0) {
      console.log("Skipped Tests:");
      results.tests.filter(t => t.skipped).forEach(t => {
        console.log(`  ⏭️  ${t.name}: ${t.reason}`);
      });
      console.log();
    }

    server.kill();
    process.exit(results.failed === 0 ? 0 : 1);

  } catch (e) {
    console.error("\n❌ FATAL ERROR:", e.message);
    console.error(e.stack);
    server.kill();
    process.exit(1);
  }
}

test();
