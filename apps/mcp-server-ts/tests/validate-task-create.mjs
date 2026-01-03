/**
 * Comprehensive Validation: task_create
 * Tests all scenarios, edge cases, and field combinations
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
    }, 10000);
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

await new Promise(resolve => setTimeout(resolve, 2000));

const PROJECT_ID = "P-8767f2bc";
const results = { passed: 0, failed: 0, tests: [] };
const createdTasks = [];

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

async function test() {
  try {
    console.log("╔═══════════════════════════════════════════════════════════╗");
    console.log("║       task_create - Comprehensive Validation             ║");
    console.log("╚═══════════════════════════════════════════════════════════╝\n");

    // TEST 1: Minimal required fields
    console.log("═══ Test 1: Minimal Required Fields ═══\n");
    try {
      const r = await sendRequest("tools/call", {
        name: "task_create",
        arguments: {
          task: {
            title: "Test: Minimal Fields",
            project_id: PROJECT_ID,
            status: "new",
            work_type: "task"
          }
        }
      });

      if (r.structuredContent?.task?.id) {
        createdTasks.push(r.structuredContent.task.id);
        pass("Minimal required fields", `ID: ${r.structuredContent.task.id}`);
      } else {
        throw new Error("No task ID returned");
      }
    } catch (e) {
      fail("Minimal required fields", e);
    }

    // TEST 2: With description
    console.log("\n═══ Test 2: With Description ═══\n");
    try {
      const r = await sendRequest("tools/call", {
        name: "task_create",
        arguments: {
          task: {
            title: "Test: With Description",
            project_id: PROJECT_ID,
            status: "new",
            work_type: "task",
            description: "This is a test description with details about the task."
          }
        }
      });

      if (r.isError) {
        throw new Error(r.content[0].text);
      }

      createdTasks.push(r.structuredContent.task.id);
      pass("With description", r.structuredContent.task.description?.substring(0, 30));
    } catch (e) {
      fail("With description", e);
    }

    // TEST 3: With priority
    console.log("\n═══ Test 3: Priority Variants ═══\n");
    const priorities = ["low", "medium", "high", "critical"];
    for (const priority of priorities) {
      try {
        const r = await sendRequest("tools/call", {
          name: "task_create",
          arguments: {
            task: {
              title: `Test: Priority ${priority}`,
              project_id: PROJECT_ID,
              status: "new",
              work_type: "task",
              priority: priority
            }
          }
        });

        if (r.structuredContent?.task?.priority === priority) {
          createdTasks.push(r.structuredContent.task.id);
          pass(`Priority: ${priority}`);
        } else {
          throw new Error(`Priority mismatch: expected ${priority}, got ${r.structuredContent?.task?.priority}`);
        }
      } catch (e) {
        fail(`Priority: ${priority}`, e);
      }
    }

    // TEST 4: With owner
    console.log("\n═══ Test 4: With Owner ═══\n");
    try {
      const r = await sendRequest("tools/call", {
        name: "task_create",
        arguments: {
          task: {
            title: "Test: With Owner",
            project_id: PROJECT_ID,
            status: "new",
            work_type: "task",
            owner: "TestOwner"
          }
        }
      });

      if (r.structuredContent?.task?.owner === "TestOwner") {
        createdTasks.push(r.structuredContent.task.id);
        pass("With owner", "Owner: TestOwner");
      } else {
        throw new Error("Owner not set correctly");
      }
    } catch (e) {
      fail("With owner", e);
    }

    // TEST 5: All work_type variants
    console.log("\n═══ Test 5: Work Type Variants ═══\n");
    const workTypes = ["task", "bug", "feature", "epic", "story"];
    for (const workType of workTypes) {
      try {
        const r = await sendRequest("tools/call", {
          name: "task_create",
          arguments: {
            task: {
              title: `Test: Work Type ${workType}`,
              project_id: PROJECT_ID,
              status: "new",
              work_type: workType
            }
          }
        });

        if (r.structuredContent?.task?.work_type === workType) {
          createdTasks.push(r.structuredContent.task.id);
          pass(`Work type: ${workType}`);
        } else {
          throw new Error(`Work type mismatch`);
        }
      } catch (e) {
        fail(`Work type: ${workType}`, e);
      }
    }

    // TEST 6: With due_date
    console.log("\n═══ Test 6: With Due Date ═══\n");
    try {
      const r = await sendRequest("tools/call", {
        name: "task_create",
        arguments: {
          task: {
            title: "Test: With Due Date",
            project_id: PROJECT_ID,
            status: "new",
            work_type: "task",
            due_date: "2025-12-31"
          }
        }
      });

      if (r.structuredContent?.task?.due_date) {
        createdTasks.push(r.structuredContent.task.id);
        pass("With due_date", r.structuredContent.task.due_date);
      } else {
        throw new Error("Due date not set");
      }
    } catch (e) {
      fail("With due_date", e);
    }

    // TEST 7: Error handling - missing required fields
    console.log("\n═══ Test 7: Error Handling ═══\n");

    // Missing title
    try {
      const r = await sendRequest("tools/call", {
        name: "task_create",
        arguments: {
          task: {
            project_id: PROJECT_ID,
            status: "new",
            work_type: "task"
          }
        }
      });

      if (r.isError) {
        pass("Missing title error", "Correctly rejected");
      } else {
        fail("Missing title error", new Error("Should have failed but succeeded"));
      }
    } catch (e) {
      pass("Missing title error", "Exception thrown as expected");
    }

    // Missing project_id
    try {
      const r = await sendRequest("tools/call", {
        name: "task_create",
        arguments: {
          task: {
            title: "Test: No Project",
            status: "new",
            work_type: "task"
          }
        }
      });

      if (r.isError) {
        pass("Missing project_id error", "Correctly rejected");
      } else {
        fail("Missing project_id error", new Error("Should have failed but succeeded"));
      }
    } catch (e) {
      pass("Missing project_id error", "Exception thrown as expected");
    }

    // TEST 8: Edge cases - special characters in title
    console.log("\n═══ Test 8: Edge Cases ═══\n");
    const specialTitles = [
      "Task with emoji 🚀",
      "Task with \"quotes\"",
      "Task with 'apostrophes'",
      "Task with <brackets>",
      "Task with & ampersand"
    ];

    for (const title of specialTitles) {
      try {
        const r = await sendRequest("tools/call", {
          name: "task_create",
          arguments: {
            task: {
              title: title,
              project_id: PROJECT_ID,
              status: "new",
              work_type: "task"
            }
          }
        });

        if (r.structuredContent?.task?.id) {
          createdTasks.push(r.structuredContent.task.id);
          pass(`Special chars: ${title.substring(0, 20)}...`);
        } else {
          throw new Error("Task not created");
        }
      } catch (e) {
        fail(`Special chars: ${title.substring(0, 20)}...`, e);
      }
    }

    // TEST 9: Response structure validation
    console.log("\n═══ Test 9: Response Structure Validation ═══\n");
    try {
      const r = await sendRequest("tools/call", {
        name: "task_create",
        arguments: {
          task: {
            title: "Test: Response Structure",
            project_id: PROJECT_ID,
            status: "new",
            work_type: "task"
          }
        }
      });

      const task = r.structuredContent.task;
      createdTasks.push(task.id);

      // Validate response has all expected fields
      const expectedFields = [
        "id", "title", "project_id", "status", "work_type",
        "created_at", "updated_at", "priority", "description"
      ];

      const missingFields = expectedFields.filter(field => !(field in task));

      if (missingFields.length === 0) {
        pass("Response structure", `All ${expectedFields.length} required fields present`);
      } else {
        throw new Error(`Missing fields: ${missingFields.join(", ")}`);
      }
    } catch (e) {
      fail("Response structure", e);
    }

    // CLEANUP
    console.log("\n═══ Cleanup ═══\n");
    let cleaned = 0;
    for (const taskId of createdTasks) {
      try {
        await sendRequest("tools/call", {
          name: "task_delete",
          arguments: { taskId }
        });
        cleaned++;
      } catch (e) {
        console.log(`⚠️  Failed to delete ${taskId}`);
      }
    }
    console.log(`Cleaned up ${cleaned}/${createdTasks.length} test tasks\n`);

    // SUMMARY
    const total = results.passed + results.failed;
    const rate = ((results.passed / total) * 100).toFixed(1);

    console.log("╔═══════════════════════════════════════════════════════════╗");
    console.log("║                    SUMMARY                                ║");
    console.log("╚═══════════════════════════════════════════════════════════╝\n");
    console.log(`Total Tests: ${total}`);
    console.log(`✅ Passed:   ${results.passed}`);
    console.log(`❌ Failed:   ${results.failed}`);
    console.log(`Success:     ${rate}%\n`);

    if (results.failed > 0) {
      console.log("Failed Tests:");
      results.tests.filter(t => !t.success).forEach(t => {
        console.log(`  ❌ ${t.name}: ${t.error}`);
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
