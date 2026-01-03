/**
 * @fileoverview Zod validation schemas for TaskMan MCP Server
 * 
 * This module provides comprehensive validation schemas for all domain entities
 * using Zod's runtime type validation. These schemas are used for:
 * - MCP tool input validation
 * - API response validation
 * - Type-safe data transformation
 * 
 * @remarks
 * All schemas follow a consistent pattern:
 * - Base schemas (e.g., `taskSchema`) for create operations
 * - Update schemas (e.g., `taskUpdateSchema`) with all fields optional
 * - Record schemas (e.g., `taskRecordSchema`) for database records with required id/timestamps
 * 
 * @see {@link types} for TypeScript type definitions
 * @category Schemas
 * @module core/schemas
 */

import { z } from "zod";
import {
  ActionListPriority,
  ActionListStatus,
  GeometryShape,
  Health,
  ProjectStatus,
  RiskLevel,
  Severity,
  ShapeStage,
  SprintStatus,
  TaskPriority,
  TaskStatus,
  ValidationState,
  WorkType,
} from "./types.js";

// ============================================================================
// HELPER SCHEMAS & UTILITIES
// ============================================================================

/**
 * ISO date string validation schema
 * 
 * @remarks
 * Accepts either:
 * - Full ISO-8601 datetime strings
 * - Simple date strings in YYYY-MM-DD format
 * 
 * @example
 * ```typescript
 * isoDate.parse("2024-10-15");         // ✅ Valid
 * isoDate.parse("2024-10-15T12:00:00"); // ✅ Valid
 * isoDate.parse("10/15/2024");          // ❌ Invalid
 * ```
 * 
 * @category Schemas
 */
const isoDate = z
  .string()
  .datetime()
  .or(z.string().regex(/\d{4}-\d{2}-\d{2}/));

/**
 * Permissive ISO datetime validation schema
 * 
 * @remarks
 * Supports both ISO-8601 (T separator) and SQL (space separator)
 * with optional milliseconds/microseconds. Designed to match backend
 * SQLAlchemy timestamp format for seamless data exchange.
 * 
 * @example
 * ```typescript
 * isoDateTime.parse("2024-10-15T12:34:56");        // ✅ ISO format
 * isoDateTime.parse("2024-10-15 12:34:56.123456"); // ✅ SQL format
 * isoDateTime.parse("2024-10-15T12:34:56.789Z");   // ✅ With timezone
 * ```
 * 
 * @category Schemas
 */
const isoDateTime = z
  .string()
  .regex(/^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(\.\d+)?(Z)?$/);

/**
 * UUID v4 validation schema
 * 
 * @remarks
 * Validates strings as proper UUID v4 format.
 * Used for correlation IDs, operation tracking, and entity references.
 * 
 * @example
 * ```typescript
 * uuid.parse("123e4567-e89b-12d3-a456-426614174000"); // ✅ Valid
 * uuid.parse("not-a-uuid");                           // ❌ Invalid
 * ```
 * 
 * @category Schemas
 */
const uuid = z.string().uuid();

/**
 * Flexible record schema for arbitrary key-value data
 * 
 * @remarks
 * Used for metadata, phases, execution traces, and other
 * extensible data structures where the schema is not strictly defined.
 * 
 * @category Schemas
 */
const unknownRecord = z.record(z.unknown());

/**
 * Creates a non-empty string schema with optional max length
 * 
 * @param max - Maximum string length (optional)
 * @returns Zod schema requiring at least 1 character
 * 
 * @remarks
 * Used for required string fields like titles and names.
 * Prevents empty strings from passing validation.
 * 
 * @example
 * ```typescript
 * const titleSchema = nonEmptyString(255);
 * titleSchema.parse("My Task");  // ✅ Valid
 * titleSchema.parse("");         // ❌ Invalid - empty
 * ```
 * 
 * @category Schemas
 */
const nonEmptyString = (max?: number) => {
  const base = z.string().min(1);
  return max ? base.max(max) : base;
};

/**
 * Creates an optional/nullable string schema with optional max length
 * 
 * @param max - Maximum string length (optional)
 * @returns Zod schema allowing string, null, or undefined
 * 
 * @remarks
 * Used for optional description fields and notes.
 * Accepts `null`, `undefined`, or valid string values.
 * 
 * @example
 * ```typescript
 * const descSchema = optionalString(1000);
 * descSchema.parse("Description");  // ✅ Valid
 * descSchema.parse(null);           // ✅ Valid
 * descSchema.parse(undefined);      // ✅ Valid
 * ```
 * 
 * @category Schemas
 */
const optionalString = (max?: number) => {
  const base = max ? z.string().max(max) : z.string();
  return base.nullish();
};

/**
 * Creates an optional/nullable array schema
 * 
 * @typeParam T - The Zod schema type for array elements
 * @param schema - Zod schema for validating array items
 * @returns Zod schema allowing array, null, or undefined
 * 
 * @remarks
 * Used for optional list fields like tags, assignees, and dependencies.
 * 
 * @example
 * ```typescript
 * const tagsSchema = optionalList(z.string());
 * tagsSchema.parse(["bug", "urgent"]);  // ✅ Valid
 * tagsSchema.parse(null);               // ✅ Valid
 * ```
 * 
 * @category Schemas
 */
const optionalList = <T extends z.ZodTypeAny>(schema: T) =>
  z.array(schema).nullish();

/**
 * Creates an optional/nullable number schema
 * 
 * @returns Zod schema allowing number, null, or undefined
 * 
 * @remarks
 * Used for optional numeric fields like estimated_hours, velocity.
 * 
 * @category Schemas
 */
const optionalNumber = () => z.number().nullish();

/**
 * Creates an optional/nullable integer schema
 * 
 * @returns Zod schema allowing integer, null, or undefined
 * 
 * @remarks
 * Used for optional integer fields like story points, sequence numbers.
 * Ensures whole numbers only (no decimals).
 * 
 * @category Schemas
 */
const optionalInt = () => z.number().int().nullish();

// ============================================================================
// PROJECT SCHEMAS
// ============================================================================

/**
 * Project creation/input schema
 * 
 * @remarks
 * Used for creating new projects via the MCP `create_project` tool.
 * The `id` field is optional - if not provided, one will be generated.
 * 
 * @example
 * ```typescript
 * const newProject = projectSchema.parse({
 *   name: "TaskMan v2 Migration",
 *   description: "Migrate to TypeScript MCP",
 *   status: ProjectStatus.Active
 * });
 * ```
 * 
 * @see {@link projectRecordSchema} for database record schema
 * @see {@link ProjectStatus} for valid status values
 * @category Schemas
 */
export const projectSchema = z.object({
  id: z.string().optional(),
  name: nonEmptyString(255),
  description: optionalString(),
  status: z.nativeEnum(ProjectStatus).optional(),
});

/**
 * Project analytics - project metadata sub-schema
 * 
 * @remarks
 * Part of the project analytics response. Contains basic project
 * information with timestamps.
 * 
 * @see {@link projectAnalyticsSchema} for the complete analytics schema
 * @category Schemas
 */
export const projectAnalyticsProjectSchema = z
  .object({
    id: z.string(),
    name: z.string(),
    status: z.string(),
    description: optionalString(),
    owner: optionalString(),
    created_at: z.string(),
    updated_at: z.string().optional(),
  })
  .passthrough();

/**
 * Project analytics - task statistics sub-schema
 * 
 * @remarks
 * Provides aggregated task metrics for a project including
 * totals, completion rates, and breakdowns by status/priority.
 * 
 * @see {@link projectAnalyticsSchema} for the complete analytics schema
 * @category Schemas
 */
export const projectAnalyticsTaskStatisticsSchema = z
  .object({
    total: z.number(),
    completed: z.number(),
    in_progress: z.number(),
    by_status: z.record(z.number()),
    by_priority: z.record(z.number()),
    completion_percentage: z.number(),
  })
  .passthrough();

/**
 * Project analytics - sprint statistics sub-schema
 * 
 * @remarks
 * Provides aggregated sprint metrics for a project including
 * totals and breakdowns by sprint status.
 * 
 * @see {@link projectAnalyticsSchema} for the complete analytics schema
 * @category Schemas
 */
export const projectAnalyticsSprintStatisticsSchema = z
  .object({
    total: z.number(),
    active: z.number(),
    completed: z.number(),
    planned: z.number(),
  })
  .passthrough();

/**
 * Complete project analytics response schema
 * 
 * @remarks
 * Combines project metadata with task and sprint statistics.
 * Used by the `get_project_statistics` MCP tool to provide
 * comprehensive project health metrics.
 * 
 * @example
 * ```typescript
 * const analytics = projectAnalyticsSchema.parse(apiResponse);
 * console.log(`${analytics.task_statistics.completion_percentage}% complete`);
 * ```
 * 
 * @see {@link projectAnalyticsProjectSchema}
 * @see {@link projectAnalyticsTaskStatisticsSchema}
 * @see {@link projectAnalyticsSprintStatisticsSchema}
 * @category Schemas
 */
export const projectAnalyticsSchema = z
  .object({
    project: projectAnalyticsProjectSchema,
    task_statistics: projectAnalyticsTaskStatisticsSchema,
    sprint_statistics: projectAnalyticsSprintStatisticsSchema
      .nullable()
      .optional(),
  })
  .passthrough();

/**
 * Project database record schema
 * 
 * @remarks
 * Extends {@link projectSchema} with required fields that are
 * present on all persisted project records: id, timestamps, and status.
 * 
 * @see {@link projectSchema} for the input schema
 * @category Schemas
 */
export const projectRecordSchema = projectSchema.extend({
  id: z.string(),
  created_at: isoDateTime,
  updated_at: isoDateTime,
  status: z.nativeEnum(ProjectStatus),
});

// ============================================================================
// SPRINT SCHEMAS
// ============================================================================

/**
 * Sprint creation/input schema
 * 
 * @remarks
 * Used for creating new sprints via the MCP `create_sprint` tool.
 * Sprints must be associated with a project via `project_id`.
 * 
 * Supports comprehensive sprint planning fields including:
 * - Date ranges (planned and actual)
 * - Capacity and velocity tracking
 * - Sprint goals and retrospective notes
 * 
 * @example
 * ```typescript
 * const newSprint = sprintSchema.parse({
 *   name: "Sprint 2025-01",
 *   project_id: "proj-123",
 *   start_date: "2025-01-01",
 *   end_date: "2025-01-14",
 *   capacity_points: 40
 * });
 * ```
 * 
 * @see {@link sprintRecordSchema} for database record schema
 * @see {@link SprintStatus} for valid status values
 * @category Schemas
 */
export const sprintSchema = z.object({
  id: z.string().optional(),
  name: nonEmptyString(255),
  description: optionalString(),
  status: z.nativeEnum(SprintStatus).optional(),
  project_id: nonEmptyString(50),
  start_date: isoDate.nullish(),
  end_date: isoDate.nullish(),
  actual_start_date: isoDate.nullish(),
  actual_end_date: isoDate.nullish(),
  capacity_points: optionalInt(),
  committed_points: optionalInt(),
  completed_points: optionalInt(),
  velocity: optionalNumber(),
  goals: optionalList(z.string()),
  retrospective_notes: optionalString(),
});

/**
 * Sprint database record schema
 * 
 * @remarks
 * Extends {@link sprintSchema} with required fields that are
 * present on all persisted sprint records: id, timestamps, and status.
 * 
 * @see {@link sprintSchema} for the input schema
 * @category Schemas
 */
export const sprintRecordSchema = sprintSchema.extend({
  id: z.string(),
  created_at: isoDateTime,
  updated_at: isoDateTime,
  status: z.nativeEnum(SprintStatus),
});

// ============================================================================
// TASK SCHEMAS
// ============================================================================

/**
 * Task creation/input schema - comprehensive 64+ field schema
 * 
 * @remarks
 * The most comprehensive schema in the system, supporting all task
 * management needs including:
 * 
 * **Core Fields**: title, description, status, priority, work_type
 * **Assignment**: owner, assignee, assignees, watchers
 * **Organization**: project_id, sprint_id, parent_task_id, subtasks
 * **Time Tracking**: estimated_hours, actual_hours, actual_minutes
 * **Dependencies**: depends_on, blocks
 * **Quality**: evidence_required, evidence_emitted, validation_state
 * **Metrics**: velocity_points, estimate_points, risk_level
 * **Sacred Geometry**: geometry_shape, shape_stage
 * 
 * @example
 * ```typescript
 * const newTask = taskSchema.parse({
 *   title: "Implement JWT authentication",
 *   description: "Add JWT token validation",
 *   work_type: WorkType.Feature,
 *   priority: TaskPriority.High,
 *   project_id: "proj-123",
 *   sprint_id: "sprint-001",
 *   estimated_hours: 8
 * });
 * ```
 * 
 * @see {@link taskRecordSchema} for database record schema
 * @see {@link taskUpdateSchema} for partial update schema
 * @see {@link TaskStatus} for valid status values
 * @see {@link WorkType} for valid work type values
 * @category Schemas
 */
export const taskSchema = z.object({
  title: nonEmptyString(255),
  description: optionalString(),
  status: z.nativeEnum(TaskStatus).optional(),
  work_type: z.nativeEnum(WorkType).optional(),
  priority: z.nativeEnum(TaskPriority).nullish(),
  owner: optionalString(100),
  tags: optionalList(z.string()),
  assignee: optionalString(100),
  assignees: optionalList(z.string()),
  deleted_at: isoDateTime.nullish(),
  parent_task_id: optionalString(50),
  subtasks: optionalList(z.string()),
  attachments: optionalList(z.string()),
  watchers: optionalList(z.string()),
  estimated_hours: optionalNumber(),
  actual_hours: optionalNumber(),
  phases: unknownRecord.nullish(),
  due_date: isoDateTime.nullish(),
  geometry_shape: z.nativeEnum(GeometryShape).nullish(),
  shape_stage: z.nativeEnum(ShapeStage).nullish(),
  project_id: nonEmptyString(50),
  sprint_id: optionalString(50),
  summary: optionalString(),
  completion_notes: optionalString(),
  velocity_points: optionalInt(),
  build_manifest: optionalString(),
  severity: z.nativeEnum(Severity).nullish(),
  estimate_points: optionalInt(),
  done_date: isoDateTime.nullish(),
  depends_on: optionalList(z.string()),
  blocks: optionalList(z.string()),
  risk_notes: optionalString(),
  correlation_hint: optionalString(),
  schema_version: optionalString(20),
  batch_id: optionalString(50),
  last_health: z.nativeEnum(Health).nullish(),
  last_heartbeat_utc: isoDateTime.nullish(),
  target_date: isoDateTime.nullish(),
  audit_tag: optionalString(100),
  task_sequence: optionalInt(),
  critical_path: z.boolean().nullish(),
  risk_level: z.nativeEnum(RiskLevel).nullish(),
  mitigation_status: optionalString(20),
  origin_source: optionalString(100),
  load_group: optionalString(50),
  agent_id: optionalString(100),
  content_hash: optionalString(64),
  eff_priority: optionalString(20),
  verification_requirements: optionalString(),
  validation_state: z.nativeEnum(ValidationState).nullish(),
  context_objects: optionalList(z.string()),
  context_dimensions: optionalList(z.string()),
  evidence_required: z.boolean().nullish(),
  evidence_emitted: z.boolean().nullish(),
  execution_trace_log: unknownRecord.nullish(),
  notes: optionalString(),
  aar_count: optionalInt(),
  last_aar_utc: isoDateTime.nullish(),
  misstep_count: optionalInt(),
  last_misstep_utc: isoDateTime.nullish(),
  actual_minutes: optionalInt(),
  correlation_id: uuid.nullish(),
});

/**
 * Task partial update schema
 * 
 * @remarks
 * Used for updating existing tasks via the MCP `update_task` tool.
 * All fields are optional (partial update semantics).
 * 
 * @example
 * ```typescript
 * const update = taskUpdateSchema.parse({
 *   status: TaskStatus.InProgress,
 *   actual_hours: 4.5,
 *   notes: "Making good progress"
 * });
 * ```
 * 
 * @see {@link taskSchema} for full task creation schema
 * @category Schemas
 */
export const taskUpdateSchema = z.object({
  title: nonEmptyString(255).nullish(),
  description: optionalString(),
  status: z.nativeEnum(TaskStatus).nullish(),
  work_type: z.nativeEnum(WorkType).nullish(),
  priority: z.nativeEnum(TaskPriority).nullish(),
  owner: optionalString(100),
  tags: optionalList(z.string()),
  assignee: optionalString(100),
  assignees: optionalList(z.string()),
  deleted_at: isoDateTime.nullish(),
  parent_task_id: optionalString(50),
  subtasks: optionalList(z.string()),
  attachments: optionalList(z.string()),
  watchers: optionalList(z.string()),
  estimated_hours: optionalNumber(),
  actual_hours: optionalNumber(),
  phases: unknownRecord.nullish(),
  due_date: isoDateTime.nullish(),
  geometry_shape: z.nativeEnum(GeometryShape).nullish(),
  shape_stage: z.nativeEnum(ShapeStage).nullish(),
  project_id: nonEmptyString(50).nullish(),
  sprint_id: optionalString(50),
  summary: optionalString(),
  completion_notes: optionalString(),
  velocity_points: optionalInt(),
  build_manifest: optionalString(),
  severity: z.nativeEnum(Severity).nullish(),
  estimate_points: optionalInt(),
  done_date: isoDateTime.nullish(),
  depends_on: optionalList(z.string()),
  blocks: optionalList(z.string()),
  risk_notes: optionalString(),
  correlation_hint: optionalString(),
  schema_version: optionalString(20),
  batch_id: optionalString(50),
  last_health: z.nativeEnum(Health).nullish(),
  last_heartbeat_utc: isoDateTime.nullish(),
  target_date: isoDateTime.nullish(),
  audit_tag: optionalString(100),
  task_sequence: optionalInt(),
  critical_path: z.boolean().nullish(),
  risk_level: z.nativeEnum(RiskLevel).nullish(),
  mitigation_status: optionalString(20),
  origin_source: optionalString(100),
  load_group: optionalString(50),
  agent_id: optionalString(100),
  content_hash: optionalString(64),
  eff_priority: optionalString(20),
  verification_requirements: optionalString(),
  validation_state: z.nativeEnum(ValidationState).nullish(),
  context_objects: optionalList(z.string()),
  context_dimensions: optionalList(z.string()),
  evidence_required: z.boolean().nullish(),
  evidence_emitted: z.boolean().nullish(),
  execution_trace_log: unknownRecord.nullish(),
  notes: optionalString(),
  aar_count: optionalInt(),
  last_aar_utc: isoDateTime.nullish(),
  misstep_count: optionalInt(),
  last_misstep_utc: isoDateTime.nullish(),
  actual_minutes: optionalInt(),
  correlation_id: uuid.nullish(),
});

/**
 * Task database record schema
 * 
 * @remarks
 * Extends {@link taskSchema} with required fields that are present
 * on all persisted task records: id, timestamps, status, and work_type.
 * 
 * @see {@link taskSchema} for the input schema
 * @see {@link taskUpdateSchema} for partial update schema
 * @category Schemas
 */
export const taskRecordSchema = taskSchema.extend({
  id: z.string(),
  status: z.nativeEnum(TaskStatus),
  work_type: z.nativeEnum(WorkType),
  priority: z.nativeEnum(TaskPriority).nullish(),
  created_at: isoDateTime,
  updated_at: isoDateTime,
});

// ============================================================================
// CONCURRENCY & METADATA SCHEMAS
// ============================================================================

/**
 * Concurrency control metadata schema
 * 
 * @remarks
 * Used for optimistic concurrency control. Supports multiple
 * concurrency strategies: token-based, ETag-based, and version-based.
 * Uses `passthrough()` to allow additional fields.
 * 
 * @example
 * ```typescript
 * const meta = concurrencyMetaSchema.parse({
 *   etag: "abc123",
 *   version: "1",
 *   updated_at: "2025-01-01T00:00:00Z",
 *   updated_by: "user@example.com"
 * });
 * ```
 * 
 * @category Schemas
 */
export const concurrencyMetaSchema = z
  .object({
    token: optionalString(),
    etag: optionalString(),
    version: optionalString(),
    updated_at: isoDateTime.nullish(),
    updated_by: optionalString(100),
  })
  .passthrough();

// ============================================================================
// TASK SUB-ENTITY SCHEMAS
// ============================================================================

/**
 * Task comment schema
 * 
 * @remarks
 * Represents a comment attached to a task. Comments support
 * tagging and author tracking. Uses `passthrough()` for extensibility.
 * 
 * @example
 * ```typescript
 * const comment = taskCommentSchema.parse({
 *   id: "comment-001",
 *   message: "Great progress on this task!",
 *   author: "alice@example.com",
 *   created_at: "2025-01-01T10:00:00Z",
 *   tags: ["feedback", "positive"]
 * });
 * ```
 * 
 * @category Schemas
 */
export const taskCommentSchema = z
  .object({
    id: z.string(),
    message: nonEmptyString(),
    author: optionalString(100),
    created_at: isoDateTime,
    updated_at: isoDateTime.nullish(),
    tags: optionalList(z.string()),
  })
  .passthrough();

/**
 * Task blocker schema
 * 
 * @remarks
 * Represents a blocker preventing task progress. Blockers can be
 * linked to external systems or other tasks, and have severity levels.
 * 
 * @example
 * ```typescript
 * const blocker = taskBlockerSchema.parse({
 *   id: "blocker-001",
 *   description: "Waiting for API access",
 *   severity: Severity.High,
 *   status: "open",
 *   created_at: "2025-01-01T10:00:00Z",
 *   external_reference: "JIRA-123"
 * });
 * ```
 * 
 * @see {@link Severity} for severity levels
 * @category Schemas
 */
export const taskBlockerSchema = z
  .object({
    id: z.string(),
    description: nonEmptyString(),
    severity: z.nativeEnum(Severity).nullish(),
    status: optionalString(50),
    created_at: isoDateTime,
    resolved_at: isoDateTime.nullish(),
    external_reference: optionalString(255),
    linked_task_id: optionalString(50),
  })
  .passthrough();

/**
 * Task checklist item schema
 * 
 * @remarks
 * Represents an item in a task's checklist. Items can be assigned,
 * have due dates, and maintain ordering within the checklist.
 * 
 * @example
 * ```typescript
 * const item = taskChecklistItemSchema.parse({
 *   id: "item-001",
 *   text: "Write unit tests",
 *   completed: false,
 *   assignee: "bob@example.com",
 *   due_date: "2025-01-15T17:00:00Z",
 *   order: 1
 * });
 * ```
 * 
 * @category Schemas
 */
export const taskChecklistItemSchema = z
  .object({
    id: z.string(),
    text: nonEmptyString(),
    completed: z.boolean().nullish(),
    completed_at: isoDateTime.nullish(),
    assignee: optionalString(100),
    due_date: isoDateTime.nullish(),
    order: optionalInt(),
    metadata: unknownRecord.nullish(),
  })
  .passthrough();

/**
 * Task hours log entry schema
 * 
 * @remarks
 * Records time logged against a task. Time is tracked in minutes
 * for precision. Supports agent identification for automated logging.
 * 
 * @example
 * ```typescript
 * const log = taskHoursLogSchema.parse({
 *   id: "log-001",
 *   task_id: "TASK-123",
 *   minutes: 90,
 *   logged_at: "2025-01-01T12:00:00Z",
 *   agent_id: "copilot-session-abc",
 *   note: "Code review and documentation"
 * });
 * ```
 * 
 * @category Schemas
 */
export const taskHoursLogSchema = z
  .object({
    id: z.string(),
    task_id: z.string(),
    minutes: z.number().int().nonnegative(),
    logged_at: isoDateTime,
    agent_id: optionalString(100),
    note: optionalString(),
    phase: optionalString(50),
  })
  .passthrough();

/**
 * Task telemetry schema
 * 
 * @remarks
 * Captures operational telemetry for task mutations. Used for
 * observability, debugging, and performance analysis. Records
 * latency, outcomes, and correlation IDs for distributed tracing.
 * 
 * @example
 * ```typescript
 * const telemetry = taskTelemetrySchema.parse({
 *   operation_id: "550e8400-e29b-41d4-a716-446655440000",
 *   tool_name: "task_update",
 *   task_id: "TASK-123",
 *   started_at: "2025-01-01T12:00:00Z",
 *   finished_at: "2025-01-01T12:00:01Z",
 *   latency_ms: 1250,
 *   outcome: "success",
 *   correlation_id: "550e8400-e29b-41d4-a716-446655440001"
 * });
 * ```
 * 
 * @category Schemas
 */
export const taskTelemetrySchema = z
  .object({
    operation_id: uuid,
    tool_name: nonEmptyString(100),
    task_id: optionalString(50),
    started_at: isoDateTime,
    finished_at: isoDateTime,
    latency_ms: z.number().nonnegative(),
    status_code: z.number().int().nullish(),
    outcome: z.enum(["success", "conflict", "error"]),
    request_id: optionalString(100),
    correlation_id: uuid.nullish(),
    error_code: optionalString(100),
    retries: optionalInt(),
  })
  .passthrough();

/**
 * Task mutation result schema
 * 
 * @remarks
 * Comprehensive result object returned from task mutations.
 * Includes the task record, concurrency metadata for optimistic
 * locking, telemetry data, and all related sub-entities.
 * 
 * @example
 * ```typescript
 * const result = taskMutationResultSchema.parse({
 *   task: { id: "TASK-123", title: "Updated task", ... },
 *   concurrency: { etag: "abc123", version: "2" },
 *   telemetry: { operation_id: "...", outcome: "success", ... },
 *   comments: [],
 *   blockers: [],
 *   checklist: [],
 *   hours: []
 * });
 * ```
 * 
 * @see {@link taskRecordSchema} for task structure
 * @see {@link concurrencyMetaSchema} for concurrency control
 * @see {@link taskTelemetrySchema} for telemetry data
 * @category Schemas
 */
export const taskMutationResultSchema = z.object({
  task: taskRecordSchema,
  concurrency: concurrencyMetaSchema.nullish(),
  telemetry: taskTelemetrySchema.nullish(),
  comments: optionalList(taskCommentSchema),
  blockers: optionalList(taskBlockerSchema),
  checklist: optionalList(taskChecklistItemSchema),
  hours: optionalList(taskHoursLogSchema),
});

// ============================================================================
// ACTION LIST SCHEMAS
// ============================================================================

/**
 * Action list schema
 * 
 * @remarks
 * Represents a checklist-style action list with Sacred Geometry
 * integration. Action lists can be associated with projects, sprints,
 * or tasks. Supports prioritization and geometry shape tracking.
 * 
 * @example
 * ```typescript
 * const actionList = actionListSchema.parse({
 *   title: "Sprint Planning Checklist",
 *   project_id: "P-001",
 *   status: ActionListStatus.InProgress,
 *   priority: ActionListPriority.High,
 *   geometry_shape: GeometryShape.Triangle,
 *   items: [
 *     { text: "Review backlog", completed: true, order: 1 },
 *     { text: "Estimate stories", completed: false, order: 2 }
 *   ]
 * });
 * ```
 * 
 * @see {@link ActionListStatus} for status values
 * @see {@link ActionListPriority} for priority levels
 * @see {@link GeometryShape} for geometry shapes
 * @category Schemas
 */
export const actionListSchema = z.object({
  id: z.string().optional(),
  title: nonEmptyString(255),
  description: optionalString(), // Added to match backend API
  project_id: optionalString(50),
  sprint_id: optionalString(50),
  task_id: optionalString(50),
  status: z.nativeEnum(ActionListStatus).nullish(),
  priority: z.nativeEnum(ActionListPriority).nullish(),
  geometry_shape: z.nativeEnum(GeometryShape).nullish(),
  shape_stage: z.nativeEnum(ShapeStage).nullish(),
  notes: optionalString(),
  items: z
    .array(
      z.object({
        id: z.string().optional(),
        text: nonEmptyString(),
        completed: z.boolean().optional(),
        order: z.number().optional(),
      })
    )
    .nullish(),
  metadata: unknownRecord.nullish(),
});

/**
 * Action list record schema (persisted version)
 * 
 * @remarks
 * Extends {@link actionListSchema} with a required `id` field,
 * representing a persisted action list from the database.
 * 
 * @see {@link actionListSchema} for base schema
 * @category Schemas
 */
export const actionListRecordSchema = actionListSchema.extend({
  id: z.string(),
});

/**
 * Action list update schema
 * 
 * @remarks
 * Schema for partial updates to an action list. All fields are optional
 * to support PATCH-style updates. Note: Domain uses 'title' while
 * backend API uses 'name' (mapping handled in client layer).
 * 
 * @example
 * ```typescript
 * const update = actionListUpdateSchema.parse({
 *   title: "Updated Checklist Name",
 *   status: ActionListStatus.Completed
 * });
 * ```
 * 
 * @category Schemas
 */
export const actionListUpdateSchema = z.object({
  title: nonEmptyString(255).optional(), // Domain uses 'title', backend API uses 'name' (mapped in client)
  description: z.string().optional(), // Added to match backend API
  status: z.nativeEnum(ActionListStatus).optional(),
  priority: z.nativeEnum(ActionListPriority).optional(),
  geometry_shape: z.nativeEnum(GeometryShape).optional(),
  shape_stage: z.nativeEnum(ShapeStage).optional(),
  notes: z.string().optional(),
  metadata: unknownRecord.nullish(),
});

// ============================================================================
// CONFIGURATION SCHEMAS
// ============================================================================

/**
 * Configuration item schema
 * 
 * @remarks
 * Represents a configuration item tracked by the system. Used for
 * CMDB-style configuration management, tracking versions and relationships
 * to tasks for change management purposes.
 * 
 * @example
 * ```typescript
 * const configItem = configItemSchema.parse({
 *   key: "database.connection_pool_size",
 *   type: "infrastructure",
 *   version: "1.0.0",
 *   related_task_id: "TASK-456",
 *   metadata: { environment: "production" }
 * });
 * ```
 * 
 * @category Schemas
 */
export const configItemSchema = z.object({
  id: z.string().optional(),
  key: nonEmptyString(255),
  type: nonEmptyString(100),
  version: optionalString(),
  related_task_id: optionalString(50),
  metadata: unknownRecord.nullish(),
});
