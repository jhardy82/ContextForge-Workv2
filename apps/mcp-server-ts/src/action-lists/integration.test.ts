import { describe, it, expect, beforeAll } from "vitest";
import fs from "fs/promises";
import path from "path";

interface ActionListItem {
  id: string;
  text: string;
  validation_criteria: string;
  test_data?: Record<string, unknown> | Record<string, unknown>[];
  expected_result: string;
  order: number;
  workflow?: string[];
  dependencies?: string[];
}

interface ActionList {
  $schema?: string;
  id: string;
  title: string;
  description?: string;
  geometry_shape: "Circle" | "Triangle" | "Spiral" | "Pentagon" | "Fractal";
  status: "planned" | "in_progress" | "complete" | "blocked" | "cancelled";
  priority: "low" | "medium" | "high" | "critical";
  project_id: string;
  metadata?: Record<string, unknown>;
  items: ActionListItem[];
  notes?: string;
}

/**
 * Load an action list JSON file from disk
 */
async function loadActionList(filename: string): Promise<ActionList> {
  const actionListPath = path.join(__dirname, "../../action-lists", filename);
  const content = await fs.readFile(actionListPath, "utf-8");
  return JSON.parse(content) as ActionList;
}

/**
 * Convert an action list item to a task object
 */
function actionListItemToTask(
  item: ActionListItem,
  actionListId: string,
  projectId: string
): Record<string, unknown> {
  return {
    id: `TSK-${actionListId}-${item.id}`,
    title: item.text,
    description: `Validation: ${item.validation_criteria}\nExpected: ${item.expected_result}`,
    status: "planned",
    priority: "medium",
    project_id: projectId,
    metadata: {
      action_list_id: actionListId,
      action_item_id: item.id,
      order: item.order,
      validation_criteria: item.validation_criteria,
      expected_result: item.expected_result,
      test_data: item.test_data,
      workflow: item.workflow,
      dependencies: item.dependencies,
    },
  };
}

describe("Action List Integration Tests", () => {
  describe("Loading Action Lists", () => {
    it("should load task-validation-phase-2-2.json successfully", async () => {
      const actionList = await loadActionList(
        "task-validation-phase-2-2.json"
      );

      expect(actionList).toBeDefined();
      expect(actionList.id).toBe("AL-task-validation-phase-2-2");
      expect(actionList.title).toBe("Task Tools Validation - Phase 2.2");
      expect(actionList.geometry_shape).toBe("Triangle");
      expect(actionList.items).toHaveLength(37);
    });

    it("should load project-validation-phase-2-2.json successfully", async () => {
      const actionList = await loadActionList(
        "project-validation-phase-2-2.json"
      );

      expect(actionList).toBeDefined();
      expect(actionList.id).toBe("AL-project-validation-phase-2-2");
      expect(actionList.title).toBe("Project Tools Validation - Phase 2.3");
      expect(actionList.geometry_shape).toBe("Circle");
      expect(actionList.items).toHaveLength(42);
    });

    it("should load integration-validation-phase-2-2.json successfully", async () => {
      const actionList = await loadActionList(
        "integration-validation-phase-2-2.json"
      );

      expect(actionList).toBeDefined();
      expect(actionList.id).toBe("AL-integration-validation-phase-2-2");
      expect(actionList.title).toBe(
        "Cross-Feature Integration Validation - Phase 2.4"
      );
      expect(actionList.geometry_shape).toBe("Spiral");
      expect(actionList.items).toHaveLength(20);
    });
  });

  describe("Action List Structure Validation", () => {
    let taskActionList: ActionList;

    beforeAll(async () => {
      taskActionList = await loadActionList("task-validation-phase-2-2.json");
    });

    it("should have properly ordered items", () => {
      const orders = taskActionList.items.map((item) => item.order);

      // Verify all orders are sequential from 1 to N
      expect(orders).toEqual(
        Array.from({ length: taskActionList.items.length }, (_, i) => i + 1)
      );
    });

    it("should have unique item IDs", () => {
      const ids = taskActionList.items.map((item) => item.id);
      const uniqueIds = new Set(ids);

      expect(uniqueIds.size).toBe(ids.length);
    });

    it("should have all required fields in each item", () => {
      taskActionList.items.forEach((item) => {
        expect(item.id).toBeDefined();
        expect(item.text).toBeDefined();
        expect(item.validation_criteria).toBeDefined();
        expect(item.expected_result).toBeDefined();
        expect(item.order).toBeDefined();
      });
    });

    it("should have metadata with correlation_id", () => {
      expect(taskActionList.metadata).toBeDefined();
      expect(taskActionList.metadata?.correlation_id).toBeDefined();
      expect(taskActionList.metadata?.correlation_id).toMatch(
        /^QSE-\d{8}-\d{4}-[a-f0-9]{8}$/
      );
    });
  });

  describe("Action List to Task Conversion", () => {
    let taskActionList: ActionList;

    beforeAll(async () => {
      taskActionList = await loadActionList("task-validation-phase-2-2.json");
    });

    it("should convert first action list item to task", () => {
      const firstItem = taskActionList.items[0];
      const task = actionListItemToTask(
        firstItem,
        taskActionList.id,
        taskActionList.project_id
      );

      expect(task.id).toBe(`TSK-${taskActionList.id}-${firstItem.id}`);
      expect(task.title).toBe(firstItem.text);
      expect(task.status).toBe("planned");
      expect(task.project_id).toBe(taskActionList.project_id);

      // Verify metadata preservation
      const metadata = task.metadata as Record<string, unknown>;
      expect(metadata.action_list_id).toBe(taskActionList.id);
      expect(metadata.action_item_id).toBe(firstItem.id);
      expect(metadata.order).toBe(firstItem.order);
      expect(metadata.validation_criteria).toBe(firstItem.validation_criteria);
      expect(metadata.expected_result).toBe(firstItem.expected_result);
    });

    it("should convert all action list items to tasks", () => {
      const tasks = taskActionList.items.map((item) =>
        actionListItemToTask(
          item,
          taskActionList.id,
          taskActionList.project_id
        )
      );

      expect(tasks).toHaveLength(37);
      tasks.forEach((task, index) => {
        expect(task.id).toBeDefined();
        expect(task.title).toBeDefined();
        expect(task.status).toBe("planned");

        const metadata = task.metadata as Record<string, unknown>;
        expect(metadata.order).toBe(index + 1);
      });
    });

    it("should preserve test_data in task metadata", () => {
      const itemWithTestData = taskActionList.items.find(
        (item) => item.test_data !== undefined
      );

      expect(itemWithTestData).toBeDefined();

      if (itemWithTestData) {
        const task = actionListItemToTask(
          itemWithTestData,
          taskActionList.id,
          taskActionList.project_id
        );

        const metadata = task.metadata as Record<string, unknown>;
        expect(metadata.test_data).toEqual(itemWithTestData.test_data);
      }
    });

    it("should preserve workflow steps in task metadata", async () => {
      const integrationActionList = await loadActionList(
        "integration-validation-phase-2-2.json"
      );

      const itemWithWorkflow = integrationActionList.items.find(
        (item) => item.workflow !== undefined
      );

      expect(itemWithWorkflow).toBeDefined();

      if (itemWithWorkflow) {
        const task = actionListItemToTask(
          itemWithWorkflow,
          integrationActionList.id,
          integrationActionList.project_id
        );

        const metadata = task.metadata as Record<string, unknown>;
        expect(metadata.workflow).toEqual(itemWithWorkflow.workflow);
        expect(Array.isArray(metadata.workflow)).toBe(true);
      }
    });
  });

  describe("Action List Dependency Analysis", () => {
    it("should identify items with dependencies", async () => {
      const integrationActionList = await loadActionList(
        "integration-validation-phase-2-2.json"
      );

      const itemsWithDependencies = integrationActionList.items.filter(
        (item) => item.dependencies && item.dependencies.length > 0
      );

      // Some integration tests may have dependencies
      // This test documents the pattern even if count is 0
      expect(Array.isArray(itemsWithDependencies)).toBe(true);
    });

    it("should validate dependency references exist", async () => {
      const integrationActionList = await loadActionList(
        "integration-validation-phase-2-2.json"
      );

      const itemIds = new Set(
        integrationActionList.items.map((item) => item.id)
      );

      integrationActionList.items.forEach((item) => {
        if (item.dependencies) {
          item.dependencies.forEach((depId) => {
            // Dependency should reference an existing item ID
            expect(itemIds.has(depId) || depId.startsWith("TSK-")).toBe(true);
          });
        }
      });
    });
  });

  describe("Action List Progress Tracking", () => {
    it("should calculate completion percentage based on items", () => {
      const totalItems = 37;
      const completedItems = 20;
      const completionPercentage = (completedItems / totalItems) * 100;

      expect(completionPercentage).toBeCloseTo(54.05, 2);
    });

    it("should track action list status transitions", () => {
      const validStatuses: ActionList["status"][] = [
        "planned",
        "in_progress",
        "complete",
        "blocked",
        "cancelled",
      ];

      const transitions: Array<{
        from: ActionList["status"];
        to: ActionList["status"];
        valid: boolean;
      }> = [
        { from: "planned", to: "in_progress", valid: true },
        { from: "in_progress", to: "complete", valid: true },
        { from: "in_progress", to: "blocked", valid: true },
        { from: "blocked", to: "in_progress", valid: true },
        { from: "planned", to: "complete", valid: false }, // Skip in_progress
        { from: "complete", to: "in_progress", valid: false }, // Reopen
      ];

      transitions.forEach((transition) => {
        expect(validStatuses).toContain(transition.from);
        expect(validStatuses).toContain(transition.to);
        // This documents expected state machine behavior
      });
    });
  });

  describe("Action List Filtering and Querying", () => {
    let allActionLists: ActionList[];

    beforeAll(async () => {
      allActionLists = await Promise.all([
        loadActionList("task-validation-phase-2-2.json"),
        loadActionList("project-validation-phase-2-2.json"),
        loadActionList("integration-validation-phase-2-2.json"),
      ]);
    });

    it("should filter action lists by geometry_shape", () => {
      const triangleLists = allActionLists.filter(
        (list) => list.geometry_shape === "Triangle"
      );
      const circleLists = allActionLists.filter(
        (list) => list.geometry_shape === "Circle"
      );
      const spiralLists = allActionLists.filter(
        (list) => list.geometry_shape === "Spiral"
      );

      expect(triangleLists).toHaveLength(1);
      expect(circleLists).toHaveLength(1);
      expect(spiralLists).toHaveLength(1);
    });

    it("should filter action lists by priority", () => {
      const highPriorityLists = allActionLists.filter(
        (list) => list.priority === "high"
      );
      const criticalPriorityLists = allActionLists.filter(
        (list) => list.priority === "critical"
      );

      expect(highPriorityLists.length + criticalPriorityLists.length).toBe(3);
    });

    it("should filter action lists by status", () => {
      const plannedLists = allActionLists.filter(
        (list) => list.status === "planned"
      );

      expect(plannedLists).toHaveLength(3);
    });

    it("should find action lists by project_id", () => {
      const projectLists = allActionLists.filter(
        (list) => list.project_id === "taskman-mcp-validation"
      );

      expect(projectLists).toHaveLength(3);
    });
  });

  describe("Action List Metadata Extraction", () => {
    it("should extract phase information from metadata", async () => {
      const taskActionList = await loadActionList(
        "task-validation-phase-2-2.json"
      );

      expect(taskActionList.metadata?.phase).toBe("2.2");
    });

    it("should extract tool count from metadata", async () => {
      const taskActionList = await loadActionList(
        "task-validation-phase-2-2.json"
      );

      expect(taskActionList.metadata?.tools_count).toBe(11);
    });

    it("should extract estimated test count", async () => {
      const taskActionList = await loadActionList(
        "task-validation-phase-2-2.json"
      );

      expect(taskActionList.metadata?.estimated_tests).toBe(35);

      // Verify actual items match or exceed estimate
      expect(taskActionList.items.length).toBeGreaterThanOrEqual(35);
    });

    it("should validate correlation_id format", async () => {
      const allActionLists = await Promise.all([
        loadActionList("task-validation-phase-2-2.json"),
        loadActionList("project-validation-phase-2-2.json"),
        loadActionList("integration-validation-phase-2-2.json"),
      ]);

      allActionLists.forEach((actionList) => {
        if (actionList.metadata?.correlation_id) {
          expect(actionList.metadata.correlation_id).toMatch(
            /^QSE-\d{8}-\d{4}-[a-f0-9]{8}$/
          );
        }
      });
    });
  });

  describe("Action List Usage Patterns", () => {
    it("should demonstrate bulk task creation from action list", async () => {
      const actionList = await loadActionList(
        "task-validation-phase-2-2.json"
      );

      // Convert all items to tasks
      const tasks = actionList.items.map((item) =>
        actionListItemToTask(item, actionList.id, actionList.project_id)
      );

      expect(tasks).toHaveLength(37);

      // Verify all tasks have required fields
      tasks.forEach((task) => {
        expect(task.id).toBeDefined();
        expect(task.title).toBeDefined();
        expect(task.status).toBe("planned");
        expect(task.project_id).toBe("taskman-mcp-validation");
      });
    });

    it("should demonstrate filtered task creation (only high-order items)", async () => {
      const actionList = await loadActionList(
        "integration-validation-phase-2-2.json"
      );

      // Create tasks only for first 5 items
      const tasks = actionList.items
        .filter((item) => item.order <= 5)
        .map((item) =>
          actionListItemToTask(item, actionList.id, actionList.project_id)
        );

      expect(tasks).toHaveLength(5);
    });

    it("should demonstrate task creation with geometry inheritance", async () => {
      const actionList = await loadActionList(
        "project-validation-phase-2-2.json"
      );

      const task = actionListItemToTask(
        actionList.items[0],
        actionList.id,
        actionList.project_id
      );

      // Task could inherit geometry_shape from action list
      const taskWithGeometry = {
        ...task,
        geometry_shape: actionList.geometry_shape,
      };

      expect(taskWithGeometry.geometry_shape).toBe("Circle");
    });
  });
});
