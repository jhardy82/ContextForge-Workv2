import { describe, it, expect, beforeEach, vi } from "vitest";
import { z } from "zod";
import {
  actionListSchema,
  actionListRecordSchema,
  actionListUpdateSchema,
} from "../../core/schemas.js";
import {
  ActionListStatus,
  ActionListPriority,
  GeometryShape,
} from "../../core/types.js";
import {
  validateGeometryShape,
  isValidGeometryShape,
} from "../../validation/sacred-geometry.js";

describe("Action List Integration Tests", () => {
  describe("Schema Validation with Sacred Geometry", () => {
    it("should validate action list with all 5 geometry shapes", () => {
      const shapes: GeometryShape[] = [
        GeometryShape.Circle,
        GeometryShape.Triangle,
        GeometryShape.Spiral,
        GeometryShape.Pentagon,
        GeometryShape.Fractal,
      ];

      shapes.forEach((shape) => {
        const actionList = {
          title: `Test Action List - ${shape}`,
          description: "Integration test",
          geometry_shape: shape,
          status: ActionListStatus.Active,
          priority: ActionListPriority.Medium,
        };

        expect(() => actionListSchema.parse(actionList)).not.toThrow();
        const result = actionListSchema.parse(actionList);
        expect(result.geometry_shape).toBe(shape);
      });
    });

    it("should validate action list with geometry_shape as string", () => {
      const actionList = {
        title: "Test Action List",
        geometry_shape: "Pentagon",
        status: ActionListStatus.Active,
      };

      expect(() => actionListSchema.parse(actionList)).not.toThrow();
      const result = actionListSchema.parse(actionList);
      expect(result.geometry_shape).toBe("Pentagon");
    });

    it("should accept action list without geometry_shape (backward compatible)", () => {
      const actionList = {
        title: "Test Action List",
        status: ActionListStatus.Active,
      };

      expect(() => actionListSchema.parse(actionList)).not.toThrow();
      const result = actionListSchema.parse(actionList);
      expect(result.geometry_shape).toBeUndefined();
    });

    it("should accept action list with null geometry_shape", () => {
      const actionList = {
        title: "Test Action List",
        geometry_shape: null,
        status: ActionListStatus.Active,
      };

      expect(() => actionListSchema.parse(actionList)).not.toThrow();
      const result = actionListSchema.parse(actionList);
      expect(result.geometry_shape).toBeNull();
    });
  });

  describe("Schema Validation with New Status Values", () => {
    it("should validate all new status values", () => {
      const statuses: ActionListStatus[] = [
        ActionListStatus.Active,
        ActionListStatus.Active,
        ActionListStatus.Active,
        ActionListStatus.Archived,
        ActionListStatus.Completed,
        ActionListStatus.Archived,
      ];

      statuses.forEach((status) => {
        const actionList = {
          title: `Test Action List - ${status}`,
          status: status,
        };

        expect(() => actionListSchema.parse(actionList)).not.toThrow();
        const result = actionListSchema.parse(actionList);
        expect(result.status).toBe(status);
      });
    });

    it("should validate status with string values", () => {
      const statusStrings = [
        "planned",
        "new",
        "pending",
        "active",
        "in_progress",
        "blocked",
        "completed",
        "archived",
        "cancelled",
      ];

      statusStrings.forEach((status) => {
        const actionList = {
          title: `Test Action List - ${status}`,
          status: status as ActionListStatus,
        };

        expect(() => actionListSchema.parse(actionList)).not.toThrow();
        const result = actionListSchema.parse(actionList);
        expect(result.status).toBe(status);
      });
    });

    it("should reject invalid status value 'complete'", () => {
      const actionList = {
        title: "Test Action List",
        status: "complete" as any, // Invalid - should be 'completed'
      };

      expect(() => actionListSchema.parse(actionList)).toThrow();
    });

    it("should reject invalid status value 'done'", () => {
      const actionList = {
        title: "Test Action List",
        status: "done" as any, // Invalid
      };

      expect(() => actionListSchema.parse(actionList)).toThrow();
    });
  });

  describe("Action List Record Schema", () => {
    it("should validate complete action list record with all fields", () => {
      const record = {
        id: "AL-test123",
        title: "Complete Test Action List",
        description: "Full integration test",
        project_id: "PRJ-001",
        sprint_id: "SPR-001",
        task_id: "TSK-001",
        status: ActionListStatus.Active,
        priority: ActionListPriority.High,
        geometry_shape: GeometryShape.Pentagon,
        notes: "Test notes",
        items: [
          { id: "item1", text: "Item 1", completed: false, order: 0 },
          { id: "item2", text: "Item 2", completed: true, order: 1 },
        ],
        metadata: { custom_field: "custom_value" },
      };

      expect(() => actionListRecordSchema.parse(record)).not.toThrow();
      const result = actionListRecordSchema.parse(record);
      expect(result.id).toBe("AL-test123");
      expect(result.geometry_shape).toBe(GeometryShape.Pentagon);
      expect(result.status).toBe(ActionListStatus.Active);
    });

    it("should require 'id' field in record schema", () => {
      const record = {
        title: "Test Action List",
        // Missing 'id'
      };

      expect(() => actionListRecordSchema.parse(record)).toThrow();
    });

    it("should validate minimal action list record", () => {
      const record = {
        id: "AL-minimal",
        title: "Minimal Test",
      };

      expect(() => actionListRecordSchema.parse(record)).not.toThrow();
      const result = actionListRecordSchema.parse(record);
      expect(result.id).toBe("AL-minimal");
      expect(result.title).toBe("Minimal Test");
    });
  });

  describe("Action List Update Schema", () => {
    it("should validate update with geometry_shape change", () => {
      const update = {
        geometry_shape: GeometryShape.Circle,
      };

      expect(() => actionListUpdateSchema.parse(update)).not.toThrow();
      const result = actionListUpdateSchema.parse(update);
      expect(result.geometry_shape).toBe(GeometryShape.Circle);
    });

    it("should validate update with status change", () => {
      const update = {
        status: ActionListStatus.Completed,
      };

      expect(() => actionListUpdateSchema.parse(update)).not.toThrow();
      const result = actionListUpdateSchema.parse(update);
      expect(result.status).toBe(ActionListStatus.Completed);
    });

    it("should validate update with multiple fields", () => {
      const update = {
        title: "Updated Title",
        status: ActionListStatus.Active,
        priority: ActionListPriority.High,
        geometry_shape: GeometryShape.Spiral,
        notes: "Updated notes",
      };

      expect(() => actionListUpdateSchema.parse(update)).not.toThrow();
      const result = actionListUpdateSchema.parse(update);
      expect(result.title).toBe("Updated Title");
      expect(result.status).toBe(ActionListStatus.Active);
      expect(result.geometry_shape).toBe(GeometryShape.Spiral);
    });

    it("should allow empty update object", () => {
      const update = {};

      expect(() => actionListUpdateSchema.parse(update)).not.toThrow();
    });
  });

  describe("Sacred Geometry Integration", () => {
    it("should integrate validateGeometryShape with schema validation", () => {
      const validShapes = ["Circle", "Triangle", "Spiral", "Pentagon", "Fractal"];

      validShapes.forEach((shapeStr) => {
        const normalized = validateGeometryShape(shapeStr);
        const actionList = {
          title: "Test",
          geometry_shape: normalized,
        };

        expect(() => actionListSchema.parse(actionList)).not.toThrow();
      });
    });

    it("should reject invalid geometry shapes via validateGeometryShape", () => {
      const invalidShapes = ["golden_ratio", "square", "invalid"];

      invalidShapes.forEach((shapeStr) => {
        expect(() => validateGeometryShape(shapeStr)).toThrow();
        expect(isValidGeometryShape(shapeStr)).toBe(false);
      });
    });

    it("should handle case-insensitive geometry shapes", () => {
      const variations = ["CIRCLE", "Circle", "circle", "PENTAGON", "Pentagon"];

      variations.forEach((variant) => {
        const normalized = validateGeometryShape(variant);
        expect(isValidGeometryShape(normalized)).toBe(true);

        const actionList = {
          title: "Test",
          geometry_shape: normalized,
        };

        expect(() => actionListSchema.parse(actionList)).not.toThrow();
      });
    });
  });

  describe("Status Migration Integration", () => {
    it("should transition from planned to in_progress to complete", () => {
      const transitions = [
        ActionListStatus.Active,
        ActionListStatus.Active,
        ActionListStatus.Completed,
      ];

      transitions.forEach((status) => {
        const actionList = {
          title: "Test",
          status: status,
        };

        expect(() => actionListSchema.parse(actionList)).not.toThrow();
        const result = actionListSchema.parse(actionList);
        expect(result.status).toBe(status);
      });
    });

    it("should support full lifecycle: planned → in_progress → complete → archived", () => {
      const lifecycle = [
        ActionListStatus.Active,
        ActionListStatus.Active,
        ActionListStatus.Completed,
        ActionListStatus.Archived,
      ];

      lifecycle.forEach((status, index) => {
        const actionList = {
          id: `AL-lifecycle-${index}`,
          title: `Lifecycle Test ${index}`,
          status: status,
        };

        expect(() => actionListRecordSchema.parse(actionList)).not.toThrow();
        const result = actionListRecordSchema.parse(actionList);
        expect(result.status).toBe(status);
      });
    });

    it("should support cancelled status for abandoned work", () => {
      const actionList = {
        title: "Cancelled Work",
        status: ActionListStatus.Cancelled,
      };

      expect(() => actionListSchema.parse(actionList)).not.toThrow();
      const result = actionListSchema.parse(actionList);
      expect(result.status).toBe(ActionListStatus.Cancelled);
    });
  });

  describe("Error Handling and Edge Cases", () => {
    it("should require non-empty title", () => {
      const actionList = {
        title: "",
        status: ActionListStatus.Active,
      };

      expect(() => actionListSchema.parse(actionList)).toThrow();
    });

    it("should enforce title max length of 255 characters", () => {
      const longTitle = "a".repeat(256);
      const actionList = {
        title: longTitle,
        status: ActionListStatus.Active,
      };

      expect(() => actionListSchema.parse(actionList)).toThrow();
    });

    it("should accept title exactly 255 characters", () => {
      const maxTitle = "a".repeat(255);
      const actionList = {
        title: maxTitle,
        status: ActionListStatus.Active,
      };

      expect(() => actionListSchema.parse(actionList)).not.toThrow();
    });

    it("should validate items array structure", () => {
      const actionList = {
        title: "Test",
        items: [
          { id: "item1", text: "Valid item", completed: false, order: 0 },
          { id: "item2", text: "", completed: true, order: 1 }, // Empty text should fail
        ],
      };

      expect(() => actionListSchema.parse(actionList)).toThrow();
    });

    it("should allow optional fields to be null", () => {
      const actionList = {
        title: "Test",
        description: null,
        project_id: null,
        sprint_id: null,
        task_id: null,
        status: null,
        priority: null,
        geometry_shape: null,
        notes: null,
        items: null,
        metadata: null,
      };

      expect(() => actionListSchema.parse(actionList)).not.toThrow();
    });
  });

  describe("Combined Geometry + Status Validation", () => {
    it("should validate action list with both geometry and new status", () => {
      const combinations = [
        { geometry: GeometryShape.Circle, status: ActionListStatus.Active },
        { geometry: GeometryShape.Triangle, status: ActionListStatus.Active },
        { geometry: GeometryShape.Spiral, status: ActionListStatus.Completed },
        { geometry: GeometryShape.Pentagon, status: ActionListStatus.Active },
        { geometry: GeometryShape.Fractal, status: ActionListStatus.Archived },
      ];

      combinations.forEach(({ geometry, status }) => {
        const actionList = {
          id: `AL-combo-${geometry}`,
          title: `Combination Test: ${geometry} + ${status}`,
          geometry_shape: geometry,
          status: status,
        };

        expect(() => actionListRecordSchema.parse(actionList)).not.toThrow();
        const result = actionListRecordSchema.parse(actionList);
        expect(result.geometry_shape).toBe(geometry);
        expect(result.status).toBe(status);
      });
    });

    it("should update both geometry and status in single operation", () => {
      const update = {
        geometry_shape: GeometryShape.Pentagon,
        status: ActionListStatus.Active,
        priority: ActionListPriority.High,
      };

      expect(() => actionListUpdateSchema.parse(update)).not.toThrow();
      const result = actionListUpdateSchema.parse(update);
      expect(result.geometry_shape).toBe(GeometryShape.Pentagon);
      expect(result.status).toBe(ActionListStatus.Active);
      expect(result.priority).toBe(ActionListPriority.High);
    });
  });

  describe("Backward Compatibility", () => {
    it("should accept action lists created before Sacred Geometry", () => {
      const legacyActionList = {
        id: "AL-legacy-001",
        title: "Legacy Action List",
        description: "Created before Sacred Geometry",
        status: ActionListStatus.Archived, // Old format might have been 'archived'
        priority: ActionListPriority.Medium,
        // No geometry_shape field
      };

      expect(() => actionListRecordSchema.parse(legacyActionList)).not.toThrow();
      const result = actionListRecordSchema.parse(legacyActionList);
      expect(result.id).toBe("AL-legacy-001");
      expect(result.geometry_shape).toBeUndefined();
    });

    it("should accept action lists with old archived status", () => {
      const actionList = {
        title: "Archived Work",
        status: ActionListStatus.Archived, // This status was kept in migration
      };

      expect(() => actionListSchema.parse(actionList)).not.toThrow();
      const result = actionListSchema.parse(actionList);
      expect(result.status).toBe(ActionListStatus.Archived);
    });
  });
});
