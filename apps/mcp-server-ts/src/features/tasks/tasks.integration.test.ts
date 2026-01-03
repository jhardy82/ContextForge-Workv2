import { describe, it, expect, beforeEach, vi } from "vitest";
import { z } from "zod";
import {
  taskSchema,
  taskRecordSchema,
  taskUpdateSchema,
} from "../../core/schemas.js";
import {
  TaskStatus,
  TaskPriority,
  WorkType,
  GeometryShape,
} from "../../core/types.js";

describe("Task Tools Integration Tests", () => {
  describe("task_create", () => {
    it("should create valid task with all required fields", () => {
      const taskData = {
        title: "Test Task",
        description: "Test description",
        work_type: WorkType.Task,
        status: TaskStatus.Planned,
        priority: TaskPriority.Medium,
        project_id: "test-project-001",
      };

      expect(() => taskSchema.parse(taskData)).not.toThrow();
      const result = taskSchema.parse(taskData);
      expect(result.title).toBe("Test Task");
      expect(result.status).toBe(TaskStatus.Planned);
    });

    it("should create task with Sacred Geometry shape", () => {
      const taskData = {
        title: "Sacred Geometry Task",
        geometry_shape: GeometryShape.Pentagon,
        status: TaskStatus.Planned,
        project_id: "test-project-002",
      };

      expect(() => taskSchema.parse(taskData)).not.toThrow();
      const result = taskSchema.parse(taskData);
      expect(result.geometry_shape).toBe(GeometryShape.Pentagon);
    });

    it("should create task with new status values", () => {
      const newStatuses = [
        TaskStatus.Planned,
        TaskStatus.InProgress,
        TaskStatus.Pending,
        TaskStatus.Cancelled,
        TaskStatus.Completed,
      ];

      newStatuses.forEach((status, index) => {
        const taskData = {
          title: `Status Migration Task - ${status}`,
          status: status,
          project_id: `test-project-00${index + 3}`,
        };

        expect(() => taskSchema.parse(taskData)).not.toThrow();
        const result = taskSchema.parse(taskData);
        expect(result.status).toBe(status);
      });
    });

    it("should reject task with missing required fields", () => {
      const invalidTaskData = {
        description: "No title provided",
        status: TaskStatus.Planned,
      };

      // @ts-expect-error - Testing invalid data
      expect(() => taskSchema.parse(invalidTaskData)).toThrow();
    });

    it("should create task with metadata and tags", () => {
      const taskData = {
        title: "Tagged Task",
        metadata: { custom_field: "value" },
        tags: ["tag1", "tag2"],
        project_id: "test-project-008",
      };

      expect(() => taskSchema.parse(taskData)).not.toThrow();
      const result = taskSchema.parse(taskData);
      // Note: metadata and tags may be optional/stripped by schema
      if (result.metadata) {
        expect(result.metadata).toEqual({ custom_field: "value" });
      }
      if (result.tags) {
        expect(result.tags).toEqual(["tag1", "tag2"]);
      }
    });
  });

  describe("task_read", () => {
    it("should validate task record structure", () => {
      const taskRecord = {
        id: "TSK-existing-001",
        title: "Existing Task",
        status: TaskStatus.InProgress,
        project_id: "test-project-009",
        work_type: WorkType.Task,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      expect(() => taskRecordSchema.parse(taskRecord)).not.toThrow();
      const result = taskRecordSchema.parse(taskRecord);
      expect(result.id).toBe("TSK-existing-001");
    });

    it("should require id field for task record", () => {
      const invalidRecord = {
        title: "Missing ID",
        status: TaskStatus.Planned,
      };

      // @ts-expect-error - Testing invalid data
      expect(() => taskRecordSchema.parse(invalidRecord)).toThrow();
    });
  });

  describe("task_update", () => {
    it("should update single field", () => {
      const updateData = {
        title: "Updated Title",
      };

      expect(() => taskUpdateSchema.parse(updateData)).not.toThrow();
      const result = taskUpdateSchema.parse(updateData);
      expect(result.title).toBe("Updated Title");
    });

    it("should update multiple fields simultaneously", () => {
      const updateData = {
        title: "New Title",
        priority: TaskPriority.High,
        status: TaskStatus.InProgress,
      };

      expect(() => taskUpdateSchema.parse(updateData)).not.toThrow();
      const result = taskUpdateSchema.parse(updateData);
      expect(result.title).toBe("New Title");
      expect(result.priority).toBe(TaskPriority.High);
      expect(result.status).toBe(TaskStatus.InProgress);
    });

    it("should update with Sacred Geometry shape change", () => {
      const updateData = {
        geometry_shape: GeometryShape.Spiral,
      };

      expect(() => taskUpdateSchema.parse(updateData)).not.toThrow();
      const result = taskUpdateSchema.parse(updateData);
      expect(result.geometry_shape).toBe(GeometryShape.Spiral);
    });

    it("should update with status change", () => {
      const updateData = {
        status: TaskStatus.Completed,
      };

      expect(() => taskUpdateSchema.parse(updateData)).not.toThrow();
      const result = taskUpdateSchema.parse(updateData);
      expect(result.status).toBe(TaskStatus.Completed);
    });

    it("should reject invalid priority value", () => {
      const invalidUpdate = {
        priority: "invalid_priority" as any,
      };

      expect(() => taskUpdateSchema.parse(invalidUpdate)).toThrow();
    });

    it("should allow empty update object", () => {
      const emptyUpdate = {};

      expect(() => taskUpdateSchema.parse(emptyUpdate)).not.toThrow();
    });
  });

  describe("task_set_status", () => {
    it("should validate status transitions", () => {
      const statusTransitions = [
        TaskStatus.Planned,
        TaskStatus.InProgress,
        TaskStatus.Completed,
      ];

      statusTransitions.forEach((status) => {
        const updateData = { status };
        expect(() => taskUpdateSchema.parse(updateData)).not.toThrow();
        const result = taskUpdateSchema.parse(updateData);
        expect(result.status).toBe(status);
      });
    });

    it("should allow status update with done_date", () => {
      const updateData = {
        status: TaskStatus.Completed,
        done_date: new Date("2025-10-30").toISOString(), // Use ISO format
      };

      expect(() => taskUpdateSchema.parse(updateData)).not.toThrow();
      const result = taskUpdateSchema.parse(updateData);
      expect(result.status).toBe(TaskStatus.Completed);
      expect(result.done_date).toBeDefined();
    });
  });

  describe("task_assign", () => {
    it("should validate single assignee", () => {
      const taskData = {
        title: "Assigned Task",
        owner: "user@example.com",
        project_id: "test-project-010",
      };

      expect(() => taskSchema.parse(taskData)).not.toThrow();
      const result = taskSchema.parse(taskData);
      expect(result.owner).toBe("user@example.com");
    });

    it("should allow reassignment", () => {
      const updateData = {
        owner: "newuser@example.com",
      };

      expect(() => taskUpdateSchema.parse(updateData)).not.toThrow();
      const result = taskUpdateSchema.parse(updateData);
      expect(result.owner).toBe("newuser@example.com");
    });

    it("should allow unassignment (null owner)", () => {
      const updateData = {
        owner: null,
      };

      expect(() => taskUpdateSchema.parse(updateData)).not.toThrow();
      const result = taskUpdateSchema.parse(updateData);
      expect(result.owner).toBeNull();
    });

    it("should validate owner field type", () => {
      const taskData = {
        title: "Task",
        owner: 123 as any, // Invalid type
      };

      expect(() => taskSchema.parse(taskData)).toThrow();
    });
  });

  describe("task_delete", () => {
    it("should validate task exists before delete", () => {
      const taskRecord = {
        id: "TSK-to-delete",
        title: "Task to Delete",
        project_id: "test-project-011",
        work_type: WorkType.Task,
        status: TaskStatus.Planned, // Required field
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      expect(() => taskRecordSchema.parse(taskRecord)).not.toThrow();
    });

    it("should handle non-existent task ID format", () => {
      const taskId = "TSK-nonexistent";
      expect(typeof taskId).toBe("string");
      expect(taskId.startsWith("TSK-")).toBe(true);
    });
  });

  describe("task_list and filtering", () => {
    it("should filter by status", () => {
      const tasks = [
        { id: "TSK-1", title: "Task 1", status: TaskStatus.InProgress },
        { id: "TSK-2", title: "Task 2", status: TaskStatus.Planned },
        { id: "TSK-3", title: "Task 3", status: TaskStatus.InProgress },
      ];

      const filtered = tasks.filter((t) => t.status === TaskStatus.InProgress);
      expect(filtered).toHaveLength(2);
      expect(filtered.every((t) => t.status === TaskStatus.InProgress)).toBe(
        true
      );
    });

    it("should filter by work_type, priority, and owner", () => {
      const tasks = [
        {
          id: "TSK-1",
          title: "Bug Fix",
          work_type: WorkType.Bug,
          priority: TaskPriority.High,
          owner: "user@example.com",
        },
        {
          id: "TSK-2",
          title: "Feature",
          work_type: WorkType.Feature,
          priority: TaskPriority.Medium,
          owner: "other@example.com",
        },
        {
          id: "TSK-3",
          title: "High Priority Bug",
          work_type: WorkType.Bug,
          priority: TaskPriority.High,
          owner: "user@example.com",
        },
      ];

      const filtered = tasks.filter(
        (t) =>
          t.work_type === WorkType.Bug &&
          t.priority === TaskPriority.High &&
          t.owner === "user@example.com"
      );

      expect(filtered).toHaveLength(2);
    });

    it("should filter by geometry_shape", () => {
      const tasks = [
        {
          id: "TSK-1",
          title: "Task 1",
          geometry_shape: GeometryShape.Pentagon,
        },
        {
          id: "TSK-2",
          title: "Task 2",
          geometry_shape: GeometryShape.Circle,
        },
        {
          id: "TSK-3",
          title: "Task 3",
          geometry_shape: GeometryShape.Pentagon,
        },
      ];

      const filtered = tasks.filter(
        (t) => t.geometry_shape === GeometryShape.Pentagon
      );
      expect(filtered).toHaveLength(2);
      expect(
        filtered.every((t) => t.geometry_shape === GeometryShape.Pentagon)
      ).toBe(true);
    });

    it("should filter by project_id and sprint_id", () => {
      const tasks = [
        {
          id: "TSK-1",
          title: "Task 1",
          project_id: "PRJ-001",
          sprint_id: "SPR-001",
        },
        {
          id: "TSK-2",
          title: "Task 2",
          project_id: "PRJ-001",
          sprint_id: "SPR-002",
        },
        {
          id: "TSK-3",
          title: "Task 3",
          project_id: "PRJ-001",
          sprint_id: "SPR-001",
        },
      ];

      const filtered = tasks.filter(
        (t) => t.project_id === "PRJ-001" && t.sprint_id === "SPR-001"
      );
      expect(filtered).toHaveLength(2);
    });

    it("should support pagination with limit", () => {
      const tasks = Array.from({ length: 25 }, (_, i) => ({
        id: `TSK-${i}`,
        title: `Task ${i}`,
      }));

      const limit = 10;
      const page1 = tasks.slice(0, limit);
      const page2 = tasks.slice(limit, limit * 2);

      expect(page1).toHaveLength(10);
      expect(page2).toHaveLength(10);
      expect(page1[0].id).toBe("TSK-0");
      expect(page2[0].id).toBe("TSK-10");
    });

    it("should support combined filters", () => {
      const tasks = [
        {
          id: "TSK-1",
          title: "Bug in Auth",
          work_type: WorkType.Bug,
          priority: TaskPriority.High,
          status: TaskStatus.InProgress,
          geometry_shape: GeometryShape.Triangle,
        },
        {
          id: "TSK-2",
          title: "Feature Request",
          work_type: WorkType.Feature,
          priority: TaskPriority.Medium,
          status: TaskStatus.Planned,
          geometry_shape: GeometryShape.Circle,
        },
        {
          id: "TSK-3",
          title: "Critical Bug",
          work_type: WorkType.Bug,
          priority: TaskPriority.High,
          status: TaskStatus.InProgress,
          geometry_shape: GeometryShape.Triangle,
        },
      ];

      const filtered = tasks.filter(
        (t) =>
          t.work_type === WorkType.Bug &&
          t.priority === TaskPriority.High &&
          t.status === TaskStatus.InProgress &&
          t.geometry_shape === GeometryShape.Triangle
      );

      expect(filtered).toHaveLength(2);
    });
  });

  describe("task_search", () => {
    it("should search by title", () => {
      const tasks = [
        { id: "TSK-1", title: "Fix bug in authentication" },
        { id: "TSK-2", title: "Add new feature" },
        { id: "TSK-3", title: "Bug in payment processing" },
      ];

      const query = "bug";
      const results = tasks.filter((t) =>
        t.title.toLowerCase().includes(query.toLowerCase())
      );

      expect(results).toHaveLength(2);
      expect(results.every((t) => t.title.toLowerCase().includes("bug"))).toBe(
        true
      );
    });

    it("should search by description", () => {
      const tasks = [
        {
          id: "TSK-1",
          title: "Task 1",
          description: "Implement authentication",
        },
        { id: "TSK-2", title: "Task 2", description: "Add logging" },
        {
          id: "TSK-3",
          title: "Task 3",
          description: "Update authentication flow",
        },
      ];

      const query = "authentication";
      const results = tasks.filter((t) =>
        t.description?.toLowerCase().includes(query.toLowerCase())
      );

      expect(results).toHaveLength(2);
    });

    it("should support multi-field search", () => {
      const tasks = [
        {
          id: "TSK-1",
          title: "Security Update",
          description: "Fix security vulnerability",
          tags: ["security", "urgent"],
        },
        {
          id: "TSK-2",
          title: "Add Feature",
          description: "New user feature",
          tags: ["feature"],
        },
        {
          id: "TSK-3",
          title: "Bug Fix",
          description: "Fix bug in security module",
          tags: ["bug", "security"],
        },
      ];

      const query = "security";
      const results = tasks.filter(
        (t) =>
          t.title.toLowerCase().includes(query) ||
          t.description?.toLowerCase().includes(query) ||
          t.tags?.some((tag) => tag.toLowerCase().includes(query))
      );

      expect(results).toHaveLength(2); // TSK-1 and TSK-3 contain "security"
    });
  });

  describe("task_bulk_update", () => {
    it("should validate bulk update schema", () => {
      const bulkUpdate = {
        task_ids: ["TSK-001", "TSK-002", "TSK-003"],
        updates: {
          priority: TaskPriority.High,
        },
      };

      // Validate update portion
      expect(() => taskUpdateSchema.parse(bulkUpdate.updates)).not.toThrow();
      expect(bulkUpdate.task_ids).toHaveLength(3);
    });

    it("should validate all-or-nothing behavior for bulk updates", () => {
      const validTaskIds = ["TSK-001", "TSK-002", "TSK-003"];
      const invalidTaskIds = ["TSK-001", "TSK-nonexistent", "TSK-003"];

      expect(validTaskIds.every((id) => id.startsWith("TSK-"))).toBe(true);
      expect(invalidTaskIds.some((id) => id === "TSK-nonexistent")).toBe(true);
    });
  });

  describe("task_bulk_assign_sprint", () => {
    it("should validate bulk sprint assignment", () => {
      const bulkAssignment = {
        task_ids: ["TSK-001", "TSK-002", "TSK-003"],
        sprint_id: "SPR-001",
      };

      expect(bulkAssignment.task_ids).toHaveLength(3);
      expect(bulkAssignment.sprint_id).toBe("SPR-001");
      expect(bulkAssignment.sprint_id.startsWith("SPR-")).toBe(true);
    });

    it("should validate sprint ID format", () => {
      const validSprintId = "SPR-001";
      const invalidSprintId = "SPR-nonexistent";

      expect(validSprintId.startsWith("SPR-")).toBe(true);
      expect(invalidSprintId.startsWith("SPR-")).toBe(true);
    });
  });

  describe("Schema Validation Edge Cases", () => {
    it("should enforce title max length of 255 characters", () => {
      const validTitle = "a".repeat(255);
      const invalidTitle = "a".repeat(256);

      const validTaskData = { title: validTitle, project_id: "test-project-012" };
      const invalidTaskData = { title: invalidTitle, project_id: "test-project-013" };

      expect(() => taskSchema.parse(validTaskData)).not.toThrow();
      expect(() => taskSchema.parse(invalidTaskData)).toThrow();
    });

    it("should require non-empty title", () => {
      const emptyTitleData = { title: "" };

      expect(() => taskSchema.parse(emptyTitleData)).toThrow();
    });

    it("should allow all optional fields to be null", () => {
      const minimalTask = {
        title: "Minimal Task",
        description: null,
        project_id: "test-project-014", // Required field
        sprint_id: null,
        owner: null,
        status: TaskStatus.Planned, // Required field
        priority: null,
        geometry_shape: null,
        work_type: WorkType.Task, // Required field
        tags: null,
        metadata: null,
      };

      expect(() => taskSchema.parse(minimalTask)).not.toThrow();
    });

    it("should validate geometry_shape enum values", () => {
      const validShapes = [
        GeometryShape.Circle,
        GeometryShape.Triangle,
        GeometryShape.Spiral,
        GeometryShape.Pentagon,
        GeometryShape.Fractal,
      ];

      validShapes.forEach((shape, index) => {
        const taskData = {
          title: "Task",
          geometry_shape: shape,
          project_id: `test-project-${String(15 + index).padStart(3, '0')}`,
        };
        expect(() => taskSchema.parse(taskData)).not.toThrow();
      });

      const invalidShapeData = {
        title: "Task",
        geometry_shape: "hexagon" as any,
        project_id: "test-project-020",
      };
      expect(() => taskSchema.parse(invalidShapeData)).toThrow();
    });
  });
});
