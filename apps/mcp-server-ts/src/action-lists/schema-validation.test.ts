import { describe, it, expect, beforeAll } from "vitest";
import fs from "fs/promises";
import path from "path";
import Ajv from "ajv";
import type { JSONSchemaType } from "ajv";

interface ActionListItem {
  id: string;
  text: string;
  validation_criteria: string;
  test_data?: Record<string, unknown>;
  expected_result: string;
  order: number;
  workflow?: string[];
  dependencies?: string[];
}

interface ActionListMetadata {
  phase?: string;
  tools_count?: number;
  estimated_tests?: number;
  integration_scenarios?: number;
  correlation_id?: string;
  [key: string]: unknown;
}

interface ActionList {
  $schema?: string;
  id: string;
  title: string;
  description?: string;
  geometry_shape: "Circle" | "Triangle" | "Spiral" | "Pentagon" | "Fractal";
  status: "planned" | "new" | "pending" | "active" | "in_progress" | "blocked" | "completed" | "archived" | "cancelled";
  priority: "low" | "medium" | "high" | "critical";
  project_id: string;
  metadata?: ActionListMetadata;
  items: ActionListItem[];
  notes?: string;
}

describe("Action List Schema Validation", () => {
  let ajv: Ajv;
  let schema: JSONSchemaType<ActionList>;
  const schemaPath = path.join(
    __dirname,
    "../core/schemas/action-list.schema.json"
  );

  beforeAll(async () => {
    // Load the action list schema
    const schemaContent = await fs.readFile(schemaPath, "utf-8");
    schema = JSON.parse(schemaContent) as JSONSchemaType<ActionList>;

    // Initialize AJV with strict mode
    ajv = new Ajv({
      strict: true,
      allErrors: true,
      verbose: true,
    });
  });

  it("should load the action list schema successfully", () => {
    expect(schema).toBeDefined();
    expect(schema.$schema).toBe("http://json-schema.org/draft-07/schema#");
    expect(schema.title).toBe("TaskMan MCP Action List Schema");
  });

  it("should have all required properties defined in schema", () => {
    expect(schema.required).toEqual([
      "id",
      "title",
      "geometry_shape",
      "status",
      "priority",
      "project_id",
      "items",
    ]);
  });

  it("should define geometry_shape enum values", () => {
    const geometryProp = schema.properties?.geometry_shape;
    expect(geometryProp).toBeDefined();
    if (geometryProp && "enum" in geometryProp) {
      expect(geometryProp.enum).toEqual([
        "Circle",
        "Triangle",
        "Spiral",
        "Pentagon",
        "Fractal",
      ]);
    }
  });

  it("should define status enum values", () => {
    const statusProp = schema.properties?.status;
    expect(statusProp).toBeDefined();
    if (statusProp && "enum" in statusProp) {
      expect(statusProp.enum).toEqual([
        "planned",
        "new",
        "pending",
        "active",
        "in_progress",
        "blocked",
        "completed",
        "archived",
        "cancelled",
      ]);
    }
  });

  it("should define priority enum values", () => {
    const priorityProp = schema.properties?.priority;
    expect(priorityProp).toBeDefined();
    if (priorityProp && "enum" in priorityProp) {
      expect(priorityProp.enum).toEqual(["low", "medium", "high", "critical"]);
    }
  });

  it("should validate task-validation-phase-2-2.json against schema", async () => {
    const actionListPath = path.join(
      __dirname,
      "../../action-lists/task-validation-phase-2-2.json"
    );
    const actionListContent = await fs.readFile(actionListPath, "utf-8");
    const actionList = JSON.parse(actionListContent);

    const validate = ajv.compile(schema);
    const valid = validate(actionList);

    if (!valid) {
      console.error("Validation errors:", validate.errors);
    }

    expect(valid).toBe(true);
    expect(actionList.id).toBe("AL-task-validation-phase-2-2");
    expect(actionList.geometry_shape).toBe("Triangle");
    expect(actionList.items).toHaveLength(37);
  });

  it("should validate project-validation-phase-2-2.json against schema", async () => {
    const actionListPath = path.join(
      __dirname,
      "../../action-lists/project-validation-phase-2-2.json"
    );
    const actionListContent = await fs.readFile(actionListPath, "utf-8");
    const actionList = JSON.parse(actionListContent);

    const validate = ajv.compile(schema);
    const valid = validate(actionList);

    if (!valid) {
      console.error("Validation errors:", validate.errors);
    }

    expect(valid).toBe(true);
    expect(actionList.id).toBe("AL-project-validation-phase-2-2");
    expect(actionList.geometry_shape).toBe("Circle");
    expect(actionList.items).toHaveLength(42);
  });

  it("should validate integration-validation-phase-2-2.json against schema", async () => {
    const actionListPath = path.join(
      __dirname,
      "../../action-lists/integration-validation-phase-2-2.json"
    );
    const actionListContent = await fs.readFile(actionListPath, "utf-8");
    const actionList = JSON.parse(actionListContent);

    const validate = ajv.compile(schema);
    const valid = validate(actionList);

    if (!valid) {
      console.error("Validation errors:", validate.errors);
    }

    expect(valid).toBe(true);
    expect(actionList.id).toBe("AL-integration-validation-phase-2-2");
    expect(actionList.geometry_shape).toBe("Spiral");
    expect(actionList.items).toHaveLength(20);
  });

  it("should validate phase-4-coverage-optimization.json against schema (dogfooding)", async () => {
    const actionListPath = path.join(
      __dirname,
      "../../action-lists/phase-4-coverage-optimization.json"
    );
    const actionListContent = await fs.readFile(actionListPath, "utf-8");
    const actionList = JSON.parse(actionListContent);

    const validate = ajv.compile(schema);
    const valid = validate(actionList);

    if (!valid) {
      console.error("Validation errors:", validate.errors);
    }

    expect(valid).toBe(true);
    expect(actionList.id).toBe("AL-phase-4-coverage-optimization");
    expect(actionList.geometry_shape).toBe("Pentagon");
    expect(actionList.status).toBe("in_progress");
    expect(actionList.items).toHaveLength(10);
  });

  it("should reject action list with missing required field (id)", () => {
    const invalidActionList = {
      // id missing
      title: "Test Action List",
      geometry_shape: "Circle",
      status: "planned",
      priority: "medium",
      project_id: "PRJ-001",
      items: [],
    };

    const validate = ajv.compile(schema);
    const valid = validate(invalidActionList);

    expect(valid).toBe(false);
    expect(validate.errors).toBeDefined();
    expect(validate.errors?.[0]?.params).toHaveProperty("missingProperty", "id");
  });

  it("should reject action list with invalid geometry_shape", () => {
    const invalidActionList = {
      id: "AL-test",
      title: "Test Action List",
      geometry_shape: "invalid_shape", // Not in enum
      status: "planned",
      priority: "medium",
      project_id: "PRJ-001",
      items: [],
    };

    const validate = ajv.compile(schema);
    const valid = validate(invalidActionList);

    expect(valid).toBe(false);
    expect(validate.errors).toBeDefined();
    expect(validate.errors?.[0]?.keyword).toBe("enum");
  });

  it("should reject action list with invalid status", () => {
    const invalidActionList = {
      id: "AL-test",
      title: "Test Action List",
      geometry_shape: "Circle",
      status: "invalid_status", // Not in enum
      priority: "medium",
      project_id: "PRJ-001",
      items: [],
    };

    const validate = ajv.compile(schema);
    const valid = validate(invalidActionList);

    expect(valid).toBe(false);
    expect(validate.errors).toBeDefined();
    expect(validate.errors?.[0]?.keyword).toBe("enum");
  });

  it("should reject action list with invalid priority", () => {
    const invalidActionList = {
      id: "AL-test",
      title: "Test Action List",
      geometry_shape: "Circle",
      status: "planned",
      priority: "ultra_high", // Not in enum
      project_id: "PRJ-001",
      items: [],
    };

    const validate = ajv.compile(schema);
    const valid = validate(invalidActionList);

    expect(valid).toBe(false);
    expect(validate.errors).toBeDefined();
    expect(validate.errors?.[0]?.keyword).toBe("enum");
  });

  it("should reject action list with invalid ID pattern", () => {
    const invalidActionList = {
      id: "INVALID_ID", // Should start with AL-
      title: "Test Action List",
      geometry_shape: "Circle",
      status: "planned",
      priority: "medium",
      project_id: "PRJ-001",
      items: [],
    };

    const validate = ajv.compile(schema);
    const valid = validate(invalidActionList);

    expect(valid).toBe(false);
    expect(validate.errors).toBeDefined();
    expect(validate.errors?.[0]?.keyword).toBe("pattern");
  });

  it("should reject action list with empty items array", () => {
    const invalidActionList = {
      id: "AL-test",
      title: "Test Action List",
      geometry_shape: "Circle",
      status: "planned",
      priority: "medium",
      project_id: "PRJ-001",
      items: [], // Empty array (minItems: 1)
    };

    const validate = ajv.compile(schema);
    const valid = validate(invalidActionList);

    expect(valid).toBe(false);
    expect(validate.errors).toBeDefined();
    expect(validate.errors?.[0]?.keyword).toBe("minItems");
  });

  it("should validate action list with valid item structure", () => {
    const validActionList: ActionList = {
      id: "AL-test-valid",
      title: "Valid Test Action List",
      geometry_shape: "Triangle",
      status: "planned",
      priority: "high",
      project_id: "PRJ-TEST-001",
      items: [
        {
          id: "item-1",
          text: "First test item",
          validation_criteria: "Item completes successfully",
          expected_result: "Success response",
          order: 1,
        },
        {
          id: "item-2",
          text: "Second test item with test_data",
          validation_criteria: "Data persisted correctly",
          test_data: {
            input: "test value",
            count: 5,
          },
          expected_result: "Data saved",
          order: 2,
        },
      ],
    };

    const validate = ajv.compile(schema);
    const valid = validate(validActionList);

    if (!valid) {
      console.error("Validation errors:", validate.errors);
    }

    expect(valid).toBe(true);
  });

  it("should validate action list with workflow field in items", () => {
    const actionListWithWorkflow: ActionList = {
      id: "AL-test-workflow",
      title: "Action List with Workflow",
      geometry_shape: "Spiral",
      status: "planned",
      priority: "critical",
      project_id: "PRJ-WORKFLOW",
      items: [
        {
          id: "workflow-item-1",
          text: "Multi-step integration test",
          validation_criteria: "All workflow steps complete",
          workflow: [
            "1. Create resource A",
            "2. Create resource B",
            "3. Link A → B",
            "4. Verify linkage",
          ],
          expected_result: "Linkage verified successfully",
          order: 1,
        },
      ],
    };

    const validate = ajv.compile(schema);
    const valid = validate(actionListWithWorkflow);

    if (!valid) {
      console.error("Validation errors:", validate.errors);
    }

    expect(valid).toBe(true);
  });

  it("should validate action list with metadata including correlation_id", () => {
    const actionListWithMetadata: ActionList = {
      id: "AL-test-metadata",
      title: "Action List with Metadata",
      geometry_shape: "Pentagon",
      status: "in_progress",
      priority: "medium",
      project_id: "PRJ-META",
      metadata: {
        phase: "4.1",
        tools_count: 5,
        estimated_tests: 15,
        correlation_id: "QSE-20251030-1627-6f322eea",
        custom_field: "allowed",
      },
      items: [
        {
          id: "meta-item-1",
          text: "Test with metadata",
          validation_criteria: "Metadata preserved",
          expected_result: "Success",
          order: 1,
        },
      ],
    };

    const validate = ajv.compile(schema);
    const valid = validate(actionListWithMetadata);

    if (!valid) {
      console.error("Validation errors:", validate.errors);
    }

    expect(valid).toBe(true);
  });

  it("should reject action list item with missing required field", () => {
    const invalidActionList = {
      id: "AL-test-invalid-item",
      title: "Action List with Invalid Item",
      geometry_shape: "Circle",
      status: "planned",
      priority: "medium",
      project_id: "PRJ-001",
      items: [
        {
          id: "item-1",
          text: "Test item",
          // validation_criteria missing
          expected_result: "Result",
          order: 1,
        },
      ],
    };

    const validate = ajv.compile(schema);
    const valid = validate(invalidActionList);

    expect(valid).toBe(false);
    expect(validate.errors).toBeDefined();
  });

  it("should reject action list item with invalid order (must be >= 1)", () => {
    const invalidActionList = {
      id: "AL-test-invalid-order",
      title: "Action List with Invalid Order",
      geometry_shape: "Circle",
      status: "planned",
      priority: "medium",
      project_id: "PRJ-001",
      items: [
        {
          id: "item-1",
          text: "Test item",
          validation_criteria: "Validation",
          expected_result: "Result",
          order: 0, // Invalid (minimum: 1)
        },
      ],
    };

    const validate = ajv.compile(schema);
    const valid = validate(invalidActionList);

    expect(valid).toBe(false);
    expect(validate.errors).toBeDefined();
    expect(validate.errors?.[0]?.keyword).toBe("minimum");
  });
});
