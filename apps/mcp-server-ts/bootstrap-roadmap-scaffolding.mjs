/**
 * Bootstrap REAL roadmap scaffolding via TaskMan MCP tools.
 *
 * Creates/reuses a roadmap Project, tiered Action Lists, and Task records
 * mirroring the current roadmap/todo set.
 *
 * Design goals:
 * - Use MCP tools ONLY (project_*, task_*, action_list_*)
 * - Idempotent: create-if-missing, reuse existing by exact name/title match
 * - Short-lived: spawns MCP server via stdio and exits
 */

process.env.TASK_MANAGER_API_ENDPOINT = "http://localhost:3001/api/v1";

import { spawn } from "child_process";
import { dirname, join } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log(
  "=== Bootstrapping Roadmap Scaffolding (Project + Tasks + Tiered Action Lists) ===\n"
);

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
    }, 15000);
  });
}

server.stderr.on("data", (data) => {
  const output = data.toString().trim();
  if (output && !output.includes("TaskMan MCP")) {
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
    } catch {
      // ignore non-JSON lines
    }
  }
});

function requireStructured(result, op) {
  if (result?.isError) {
    const message = Array.isArray(result?.content)
      ? result.content
          .map((c) => (typeof c?.text === "string" ? c.text : ""))
          .filter(Boolean)
          .join("\n")
      : "";
    throw new Error(
      `${op} returned isError=true${message ? `: ${message}` : ""}`
    );
  }

  if (result?.structuredContent) {
    return result.structuredContent;
  }

  // Fallback: some MCP servers return JSON as text content rather than structuredContent.
  if (Array.isArray(result?.content)) {
    const text = result.content
      .map((c) => (typeof c?.text === "string" ? c.text : ""))
      .filter(Boolean)
      .join("\n")
      .trim();

    if (text) {
      try {
        const parsed = JSON.parse(text);
        if (parsed && typeof parsed === "object") {
          return parsed;
        }
      } catch {
        // not JSON
      }
    }
  }

  throw new Error(
    `${op} did not return structuredContent and content was not JSON. Raw result keys: ${Object.keys(
      result ?? {}
    ).join(", ")}`
  );
}

async function callTool(name, args = {}) {
  return sendRequest("tools/call", { name, arguments: args });
}

function mapPriority(priority) {
  // TaskPriority enum: low|medium|high|critical
  switch (priority) {
    case "high":
      return "high";
    case "medium":
      return "medium";
    case "low":
      return "low";
    default:
      return "medium";
  }
}

function mapStatus(status) {
  // TaskStatus enum: planned|new|pending|in_progress|completed|blocked|cancelled
  switch (status) {
    case "in_progress":
      return "in_progress";
    case "completed":
      return "completed";
    case "pending":
      return "pending";
    default:
      return "pending";
  }
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

async function getExistingActionLists(projectId) {
  const list = await callTool("action_list_list", {
    project_id: projectId,
    limit: 100,
  });
  const { action_lists } = requireStructured(list, "action_list_list");
  return action_lists ?? [];
}

async function getOrCreateActionList(
  projectId,
  { title, description, status, priority, notes }
) {
  const lists = await getExistingActionLists(projectId);
  const existing = lists.find((l) => l?.title === title);
  if (existing) {
    console.log(`ℹ️  Reusing existing action list: ${existing.id} (${title})`);
    return existing;
  }

  const created = await callTool("action_list_create", {
    title,
    description,
    status,
    priority,
    project_id: projectId,
    notes,
  });
  const { action_list } = requireStructured(created, "action_list_create");
  return action_list;
}

async function getOrCreateTask(
  projectId,
  { title, description, status, priority, tags, notes }
) {
  const list = await callTool("task_list", {
    project_id: projectId,
    search: title,
    limit: 100,
  });
  const { tasks } = requireStructured(list, "task_list");
  const existing = (tasks ?? []).find((t) => t?.title === title);
  if (existing) {
    return existing;
  }

  const created = await callTool("task_create", {
    task: {
      title,
      description,
      status,
      priority,
      work_type: "task",
      project_id: projectId,
      tags,
      notes,
      origin_source: "copilot-bootstrap-2025-12-26",
      audit_tag: "roadmap-bootstrap",
    },
  });

  const { task } = requireStructured(created, "task_create");
  return task;
}

async function upsertActionListItems(actionListId, desiredItems) {
  const read = await callTool("action_list_read", {
    action_list_id: actionListId,
  });
  const { action_list } = requireStructured(read, "action_list_read");
  const existingTexts = new Set(
    (action_list?.items ?? []).map((i) => i?.text).filter(Boolean)
  );

  let nextOrder = (action_list?.items ?? []).length + 1;

  for (const itemText of desiredItems) {
    if (existingTexts.has(itemText)) {
      continue;
    }

    await callTool("action_list_add_item", {
      action_list_id: actionListId,
      text: itemText,
      order: nextOrder,
    });
    nextOrder += 1;
  }
}

const ROADMAP_PROJECT = {
  name: "ContextForge Post-Remediation Roadmap",
  description:
    "Real roadmap scaffolding created via TaskMan MCP tools (tiers, tasks, and checklists).",
  status: "active",
};

const ROADMAP_ITEMS = [
  // Completed / recent
  {
    id: "unblock-taskman-mcp-backend",
    title: "Unblock TaskMan MCP backend",
    status: "completed",
    priority: "high",
    tier: "tier0",
    notes: "Backend readiness + endpoint alignment",
  },
  {
    id: "iv-001a-deprecation-suppression",
    title: "IV-001: Gate DeprecationWarning suppression",
    status: "completed",
    priority: "high",
    tier: "tier0",
    notes: "Completed earlier in remediation",
  },

  // Remediation / cleanup epic
  {
    id: "iv-001-cleanup-catalog",
    title: "IV-001: Cleanup catalog (remaining items)",
    status: "pending",
    priority: "high",
    tier: "remediation",
    notes: "Umbrella epic for cleanup slices",
  },
  {
    id: "iv-001b-ruff-excludes",
    title: "IV-001: Ruff excludes for archives/backups",
    status: "pending",
    priority: "medium",
    tier: "remediation",
    notes: "Exclude archived dirs + reconcile Ruff config",
  },
  {
    id: "iv-001c-catalog-reconcile",
    title: "IV-001: Reconcile CODEBASE-CLEANUP-CATALOG.yaml",
    status: "pending",
    priority: "medium",
    tier: "remediation",
    notes: "Close fixed items; align with current repo state",
  },

  // Tier 1
  {
    id: "iv-002-taskman-logging",
    title: "IV-002: TaskMan-v2 Endpoint Logging Enhancement",
    status: "pending",
    priority: "high",
    tier: "tier1",
    notes: "Structured logging across routers + error standardization",
  },
  {
    id: "iv-003-evidence-gate",
    title: "IV-003: Enable Evidence Coverage Quality Gate (80%)",
    status: "pending",
    priority: "high",
    tier: "tier1",
    notes: "Remove warn-only; enforce evidence discipline",
  },
  {
    id: "iv-004-readme-updates",
    title: "IV-004: README updates for v0.3.0 features",
    status: "pending",
    priority: "high",
    tier: "tier1",
    notes: "Doc updates for new CLI features + Postgres config",
  },
  {
    id: "iv-005-autofix-automation",
    title: "IV-005: Autofix patch auto-application (bot commits)",
    status: "pending",
    priority: "medium",
    tier: "tier1",
    notes: "Auto-apply Ruff/PSSA patches in CI",
  },

  // Tier 2
  {
    id: "st-001-taskman-cicd",
    title: "ST-001: TaskMan-v2 CI/CD pipeline",
    status: "pending",
    priority: "high",
    tier: "tier2",
    notes: "Backend + frontend CI, integration, deployment automation",
  },
  {
    id: "st-002-frontend-tests",
    title: "ST-002: Frontend tests (70%+ coverage)",
    status: "pending",
    priority: "high",
    tier: "tier2",
    notes: "Vitest + RTL suite; depends on ST-001",
  },
  {
    id: "st-003-api-docs",
    title: "ST-003: API documentation generation",
    status: "pending",
    priority: "medium",
    tier: "tier2",
    notes: "OpenAPI + examples + error formats",
  },
  {
    id: "st-004-db-performance",
    title: "ST-004: DB performance monitoring (slow query detection)",
    status: "pending",
    priority: "medium",
    tier: "tier2",
    notes: "Slow query logs + health metrics",
  },
  {
    id: "st-005-e2e-playwright",
    title: "ST-005: E2E testing with Playwright",
    status: "pending",
    priority: "high",
    tier: "tier2",
    notes: "Critical user journeys; depends on ST-001",
  },
  {
    id: "st-006-mcp-parity",
    title: "ST-006: MCP parity analysis completion",
    status: "pending",
    priority: "medium",
    tier: "tier2",
    notes: "Run parity_check.py; generate feature matrix",
  },
  {
    id: "st-007-security-scan",
    title: "ST-007: Security scanning integration",
    status: "pending",
    priority: "medium",
    tier: "tier2",
    notes: "Trivy + SAST + dependency audit",
  },

  // Tier 3
  {
    id: "si-001-constitutional",
    title: "SI-001: Constitutional framework reactivation",
    status: "pending",
    priority: "low",
    tier: "tier3",
    notes: "COF 13D + UCL validation",
  },
  {
    id: "si-002-performance-infra",
    title: "SI-002: Performance monitoring infra (Prometheus + Grafana)",
    status: "pending",
    priority: "low",
    tier: "tier3",
    notes: "Dashboards, alerting, instrumentation",
  },
  {
    id: "si-003-onboarding-auto",
    title: "SI-003: Developer onboarding automation",
    status: "pending",
    priority: "medium",
    tier: "tier3",
    notes: "Interactive onboarding; env setup automation",
  },
  {
    id: "si-004-observability",
    title: "SI-004: Observability enhancement (OpenTelemetry tracing)",
    status: "pending",
    priority: "low",
    tier: "tier3",
    notes: "Distributed tracing; depends on SI-002",
  },

  // Tier 4
  {
    id: "bl-001-sprint3-deferred",
    title: "BL-001: Sprint 3 deferred items",
    status: "pending",
    priority: "low",
    tier: "tier4",
    notes: "Deferred lint/tests/CLI TODOs",
  },
  {
    id: "bl-002-hypothesis-testing",
    title: "BL-002: Hypothesis property testing expansion",
    status: "pending",
    priority: "low",
    tier: "tier4",
    notes: "Property tests; requires hypothesis",
  },
];

const TIER_DEFS = [
  {
    key: "remediation",
    title: "Remediation — Cleanup & Ruff",
    priority: "high",
    description:
      "Codebase remediation work (linting, catalog reconciliation, housekeeping).",
  },
  {
    key: "tier1",
    title: "Tier 1 — Immediate Value",
    priority: "high",
    description:
      "Fast, high-impact work (logging, evidence gate, docs, automation).",
  },
  {
    key: "tier2",
    title: "Tier 2 — Stabilization",
    priority: "high",
    description: "CI/CD, tests, docs, performance monitoring, parity analysis.",
  },
  {
    key: "tier3",
    title: "Tier 3 — Strategic Infrastructure",
    priority: "medium",
    description: "Constitutional framework, observability, onboarding.",
  },
  {
    key: "tier4",
    title: "Tier 4 — Backlog",
    priority: "low",
    description: "Deferred work and longer-horizon improvements.",
  },
  {
    key: "tier0",
    title: "Completed — Recent",
    priority: "low",
    description: "Recently completed work, captured for continuity.",
  },
];

// Wait for server to initialize
await new Promise((resolve) => setTimeout(resolve, 2000));

async function bootstrap() {
  try {
    const project = await getOrCreateProject(ROADMAP_PROJECT);
    console.log(`\n✅ Roadmap project ready: ${project.id}\n`);

    // Create tasks first (so action list items can reference IDs)
    const taskByRoadmapId = new Map();
    console.log(`Creating/reusing ${ROADMAP_ITEMS.length} roadmap tasks...`);

    for (const item of ROADMAP_ITEMS) {
      const taskTitle = `[${item.id}] ${item.title}`;
      const task = await getOrCreateTask(project.id, {
        title: taskTitle,
        description: `${item.title}\n\nRoadmap ID: ${item.id}\nTier: ${
          item.tier
        }\n\nNotes:\n${item.notes ?? ""}`,
        status: mapStatus(item.status),
        priority: mapPriority(item.priority),
        tags: ["roadmap", item.tier, item.id],
        notes: item.notes ?? undefined,
      });
      taskByRoadmapId.set(item.id, task);
    }

    console.log("✅ Tasks ensured\n");

    const actionLists = [];

    for (const tier of TIER_DEFS) {
      const list = await getOrCreateActionList(project.id, {
        title: tier.title,
        description: tier.description,
        status: "active",
        priority: tier.priority,
        notes: `Auto-generated roadmap list for ${tier.key}`,
      });

      const tierItems = ROADMAP_ITEMS.filter((i) => i.tier === tier.key).map(
        (i) => {
          const task = taskByRoadmapId.get(i.id);
          const taskIdSuffix = task?.id ? ` (task_id=${task.id})` : "";
          return `${i.id} — ${i.title}${taskIdSuffix}`;
        }
      );

      await upsertActionListItems(list.id, tierItems);

      actionLists.push({
        key: tier.key,
        title: tier.title,
        id: list.id,
        count: tierItems.length,
      });
    }

    console.log("=".repeat(72));
    console.log("SUMMARY: Roadmap scaffolding");
    console.log("=".repeat(72));
    console.log(`Project: ${project.name} (${project.id})`);
    console.log(`Tasks: ${ROADMAP_ITEMS.length}`);
    console.log(`Action Lists: ${actionLists.length}`);
    for (const l of actionLists) {
      console.log(`  - ${l.title}: ${l.count} items (${l.id})`);
    }

    server.kill();
    process.exit(0);
  } catch (error) {
    console.error("\n❌ Fatal Error:", error?.message ?? String(error));
    if (error?.stack) {
      console.error("\nStack trace:\n" + error.stack);
    }
    server.kill();
    process.exit(1);
  }
}

bootstrap();
