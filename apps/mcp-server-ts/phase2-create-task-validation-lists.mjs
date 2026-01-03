/**
 * Phase 2: Create Task Tool Validation Action Lists
 *
 * This script creates 9 comprehensive action lists to validate all task management MCP tools:
 * 1. task_create
 * 2. task_list
 * 3. task_get
 * 4. task_search
 * 5. task_status_update
 * 6. task_update
 * 7. task_add_blocker
 * 8. task_remove_blocker
 * 9. task_delete
 *
 * Each action list contains 5-8 validation items covering happy paths, error scenarios,
 * edge cases, schema validation, and performance requirements.
 *
 * Total: 9 action lists with 61 validation items
 */

process.env.TASK_MANAGER_API_ENDPOINT = "http://localhost:3001/api/v1";

import { spawn } from "child_process";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log("=== Phase 2: Creating Task Tool Validation Action Lists ===\n");

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
        reject(new Error(`Timeout waiting for response to ${method}`));
      }
    }, 10000);
  });
}

server.stderr.on("data", (data) => {
  const output = data.toString().trim();
  if (
    output &&
    !output.includes("TaskMan MCP") &&
    !output.includes("server connected")
  ) {
    console.error("[Server]", output);
  }
});

server.stdout.on("data", (data) => {
  outputBuffer += data.toString();

  const lines = outputBuffer.split("\n");
  outputBuffer = lines.pop() || "";

  for (const line of lines) {
    if (!line.trim()) continue;

    try {
      const response = JSON.parse(line);

      if (response.id && pendingRequests.has(response.id)) {
        const { resolve, reject } = pendingRequests.get(response.id);
        pendingRequests.delete(response.id);

        if (response.error) {
          reject(
            new Error(
              `MCP error ${response.error.code}: ${response.error.message}`
            )
          );
        } else {
          resolve(response.result);
        }
      }
    } catch (e) {
      // Not valid JSON, ignore
    }
  }
});

// Wait for server to initialize
await new Promise((resolve) => setTimeout(resolve, 2000));
console.log("Server initialized\n");

function requireStructured(result, op) {
  if (!result?.structuredContent) {
    throw new Error(
      `${op} did not return structuredContent. Raw result keys: ${Object.keys(
        result ?? {}
      ).join(", ")}`
    );
  }
  return result.structuredContent;
}

async function callTool(name, args = {}) {
  return sendRequest("tools/call", { name, arguments: args });
}

async function getOrCreateProject({ name, description, status }) {
  const list = await callTool("project_list", { search: name, limit: 100 });
  const { projects } = requireStructured(list, "project_list");
  const existing = (projects ?? []).find((p) => p?.name === name);
  if (existing) {
    console.log(`ℹ️  Reusing existing project: ${existing.id}`);
    return existing;
  }

  const created = await callTool("project_create", {
    project: {
      name,
      description,
      status,
    },
  });
  const { project } = requireStructured(created, "project_create");
  return project;
}

async function createTaskValidationActionLists() {
  try {
    // Create/reuse project for validation tasks
    console.log("Creating project for task tool validation...");
    const project = await getOrCreateProject({
      name: "TaskMan Task Tool Validation",
      description: "Comprehensive validation of task management MCP tools",
      status: "active",
    });
    console.log(`✅ Project ready: ${project.id}\n`);

    const createdLists = [];

    // Define all 9 validation action lists with their items
    const validationLists = [
      {
        tier: 1,
        name: "Validate task_create Tool",
        description: "Comprehensive validation of task creation functionality",
        priority: "high",
        items: [
          "✓ Test valid task creation with required fields only (title, description)",
          "✓ Test valid task creation with all optional fields (priority, status, assignee, tags, due_date)",
          "✗ Test validation error when title is empty (should reject)",
          "✗ Test validation error when title exceeds 255 characters (should reject)",
          "✗ Test validation error when status has invalid enum value (should reject)",
          "✗ Test validation error when priority has invalid enum value (should reject)",
          "⏱ Test performance: response time <30ms for simple create",
          "📊 Test audit logging: verify correlation_id is tracked in audit logs",
        ],
      },
      {
        tier: 1,
        name: "Validate task_list Tool",
        description:
          "Validation of task listing with filters, pagination, and sorting",
        priority: "high",
        items: [
          "✓ Test list all tasks (should return array with ≥8 tasks from create tests)",
          "✓ Test filter by status=pending (should return filtered subset)",
          "✓ Test filter by priority=high (should return only high priority tasks)",
          "✓ Test pagination with limit=2, offset=1 (should return correct page)",
          "✓ Test sorting with order_by=created_at ascending (should be ordered)",
          "✓ Test empty results handling (filter with no matches returns valid empty array)",
          "⏱ Test performance: response time <20ms for list operation",
        ],
      },
      {
        tier: 2,
        name: "Validate task_get Tool",
        description: "Validation of retrieving individual tasks by ID",
        priority: "high",
        items: [
          "✓ Test get valid task by ID (should return task object)",
          "✓ Verify all fields in response match created task data",
          "✗ Test get non-existent task ID (should return 404 error)",
          "✗ Test get deleted task (should return 404 after task_delete validation)",
          "📊 Test audit trail: verify response includes audit metadata",
          "⏱ Test performance: response time <10ms for existing task",
        ],
      },
      {
        tier: 2,
        name: "Validate task_search Tool",
        description: "Validation of full-text search across tasks",
        priority: "medium",
        items: [
          "✓ Test search by title substring match (should find relevant tasks)",
          "✓ Test search by description substring match (should find in descriptions)",
          "✓ Test search with no results (should return valid empty array)",
          "✓ Test search with multiple criteria (title AND status filters)",
          "✓ Test case-insensitive search (uppercase/lowercase should match)",
          "⏱ Test performance: response time <50ms for search with 100 tasks",
        ],
      },
      {
        tier: 2,
        name: "Validate task_status_update Tool",
        description: "Validation of task status transitions",
        priority: "high",
        items: [
          "✓ Test status update: pending → in_progress (valid transition)",
          "✓ Test status update: in_progress → completed (valid transition)",
          "✓ Test status update: completed → pending (reversal, should be allowed)",
          "✗ Test validation error when status value is invalid enum (should reject)",
          "✓ Verify task_update is not needed for simple status changes",
          "🔄 Test concurrent status updates (race condition handling)",
          "📊 Test audit log: verify old→new status transition is recorded",
        ],
      },
      {
        tier: 3,
        name: "Validate task_update Tool",
        description: "Validation of partial task updates",
        priority: "high",
        items: [
          "✓ Test update single field only (e.g., title) - other fields unchanged",
          "✓ Test update multiple fields (title, priority, assignee) simultaneously",
          "✗ Test validation error when priority has invalid enum value (should reject)",
          "✓ Test update with empty optional fields (e.g., clear assignee by setting to null)",
          "✓ Verify partial updates work (not all fields required in update payload)",
          "✗ Test updating immutable fields (e.g., created_at) is rejected",
          "⏱ Test performance: response time <25ms for update operation",
        ],
      },
      {
        tier: 3,
        name: "Validate task_add_blocker Tool",
        description: "Validation of task blocking relationships",
        priority: "medium",
        items: [
          "✓ Test add valid blocker: task A blocks task B (should succeed)",
          "✗ Test validation error when task IDs don't exist (should reject)",
          "✗ Test prevent self-blocking: task blocks itself (should reject)",
          "✗ Test prevent circular blocking: A→B→A chain (should reject)",
          "✗ Test duplicate blocker rejection: add same blocker twice (should reject)",
          "✓ Verify task_get shows blocker in blockers array after adding",
          "⏱ Test performance: response time <20ms for add blocker",
        ],
      },
      {
        tier: 3,
        name: "Validate task_remove_blocker Tool",
        description: "Validation of removing task blocking relationships",
        priority: "medium",
        items: [
          "✓ Test remove valid blocker: delete A→B relationship (should succeed)",
          "✗ Test error when blocker relationship doesn't exist (should return error)",
          "✓ Verify task.blockers array updates immediately after removal",
          "✓ Confirm removal via task_get (blocker no longer in array)",
          "⏱ Test performance: response time <15ms for remove blocker",
        ],
      },
      {
        tier: 4,
        name: "Validate task_delete Tool",
        description: "Validation of task deletion and cleanup",
        priority: "high",
        items: [
          "✓ Test delete existing task (should return success)",
          "✗ Test delete non-existent task (should return 404 error)",
          "✓ Test delete task with blockers (should succeed and clean up references)",
          "✓ Verify deleted task no longer appears in task_list results",
          "✗ Verify task_get on deleted task returns 404 error",
          "⏱ Test performance: response time <20ms for delete operation",
        ],
      },
    ];

    // Create action lists and add items
    for (const listDef of validationLists) {
      console.log(`\n📋 Creating: ${listDef.name} (Tier ${listDef.tier})`);

      // Create the action list
      const createResult = await sendRequest("tools/call", {
        name: "action_list_create",
        arguments: {
          title: listDef.name,
          description: listDef.description,
          // status: omitted - let backend use default (schema mismatch between TS MCP and backend)
          priority: listDef.priority,
          project_id: project.id,
          notes: `Tier ${listDef.tier} validation - ${listDef.items.length} test items`,
        },
      });

      const actionListId = createResult.structuredContent?.action_list?.id;
      if (!actionListId) {
        throw new Error(`Failed to create action list: ${listDef.name}`);
      }

      console.log(`   ✅ Created list: ${actionListId}`);

      // Add items to the list
      console.log(`   Adding ${listDef.items.length} validation items...`);
      for (let i = 0; i < listDef.items.length; i++) {
        await sendRequest("tools/call", {
          name: "action_list_add_item",
          arguments: {
            action_list_id: actionListId,
            text: listDef.items[i],
            order: i + 1,
          },
        });
      }

      createdLists.push({
        tier: listDef.tier,
        name: listDef.name,
        id: actionListId,
        itemCount: listDef.items.length,
      });

      console.log(`   ✅ Added ${listDef.items.length} items`);
    }

    // Print summary
    console.log("\n" + "=".repeat(70));
    console.log("PHASE 2 CREATION SUMMARY");
    console.log("=".repeat(70));
    console.log(`Project: ${project.name} (${project.id})`);
    console.log(`\nCreated ${createdLists.length} validation action lists:\n`);

    let totalItems = 0;
    for (const list of createdLists) {
      console.log(`  Tier ${list.tier}: ${list.name}`);
      console.log(`           ID: ${list.id}`);
      console.log(`           Items: ${list.itemCount}\n`);
      totalItems += list.itemCount;
    }

    console.log(`Total validation items: ${totalItems}`);
    console.log("=".repeat(70));

    console.log("\n✅ PHASE 2 COMPLETE");
    console.log("All task tool validation action lists have been created!");
    console.log("\nExecution Order by Tier:");
    console.log("  Tier 1 (No dependencies): task_create, task_list");
    console.log(
      "  Tier 2 (Requires Tier 1): task_get, task_search, task_status_update"
    );
    console.log(
      "  Tier 3 (Requires Tier 2): task_update, task_add_blocker, task_remove_blocker"
    );
    console.log("  Tier 4 (Requires Tier 3): task_delete");
    console.log(
      "\nNext Step: Execute validation tests following tier dependency order\n"
    );
  } catch (error) {
    console.error("\n❌ Error creating validation lists:", error.message);
    process.exit(1);
  } finally {
    server.kill();
    process.exit(0);
  }
}

// Run creation
createTaskValidationActionLists();
