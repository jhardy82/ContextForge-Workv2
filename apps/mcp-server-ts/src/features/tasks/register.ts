import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

// Phase 2: Use circuit breaker-protected client
import { backendClientWithCircuitBreaker as backendClient } from "../../backend/client-with-circuit-breaker.js";
import {
  taskRecordSchema,
  taskSchema,
  taskUpdateSchema,
} from "../../core/schemas.js";
import {
  GeometryShape,
  RiskLevel,
  ShapeStage,
  TaskPriority,
  TaskRecord,
  TaskStatus,
  TaskUpdate,
  ValidationState,
  WorkType,
} from "../../core/types.js";
import { auditLog, withCorrelation } from "../../infrastructure/audit.js";
import { lockingService } from "../../infrastructure/locking.js";

const TASK_LOCK_AGENT = "task-tools";

const taskIdSchema = z.string().min(1, "taskId is required");

const taskCreateSchema = taskSchema;

const taskUpdatePayloadSchema = taskUpdateSchema.refine(
  (value) =>
    value !== undefined &&
    Object.values(value).some((item) => item !== undefined && item !== null),
  {
    message: "At least one field must be provided to update a task.",
  }
);

const taskListFiltersSchema = z.object({
  status: z.nativeEnum(TaskStatus).optional(),
  work_type: z.nativeEnum(WorkType).optional(),
  priority: z.nativeEnum(TaskPriority).optional(),
  owner: z.string().min(1).optional(),
  assignee: z.string().min(1).optional(),
  project_id: z.string().min(1).optional(),
  sprint_id: z.string().min(1).optional(),
  search: z.string().min(1).optional(),
  tags: z.array(z.string().min(1)).max(25).optional(),
  geometry_shape: z.nativeEnum(GeometryShape).optional(),
  shape_stage: z.nativeEnum(ShapeStage).optional(),
  risk_level: z.nativeEnum(RiskLevel).optional(),
  validation_state: z.nativeEnum(ValidationState).optional(),
  critical_path: z.boolean().optional(),
  evidence_required: z.boolean().optional(),
  include_deleted: z.boolean().optional(),
  limit: z.number().int().positive().max(100).optional(),
  cursor: z.string().min(1).optional(),
});

const taskStatusUpdateSchema = z.object({
  taskId: taskIdSchema,
  status: z.nativeEnum(TaskStatus),
  notes: z.string().min(1).optional(),
  completion_notes: z.string().min(1).optional(),
  done_date: z.string().datetime().optional(),
});

const taskAssignmentInputSchema = {
  taskId: taskIdSchema,
  assignee: z.string().min(1).nullable().optional(),
  assignees: z.array(z.string().min(1)).optional(),
};

const taskAssignmentSchema = z
  .object(taskAssignmentInputSchema)
  .refine(
    (value) =>
      value.assignee !== undefined ||
      (value.assignees !== undefined && value.assignees.length > 0),
    {
      message: "Provide an assignee or one or more assignees to update.",
      path: ["assignee"],
    }
  );

const taskBulkUpdateInputSchema = z.object({
  taskIds: z.array(taskIdSchema).min(1),
  changes: taskUpdatePayloadSchema,
});

const taskBulkAssignSprintInputSchema = z.object({
  taskIds: z.array(taskIdSchema).min(1),
  sprintId: z.string().min(1),
});

const searchableTaskFields = [
  "title",
  "description",
  "tags",
  "notes",
  "summary",
  "completion_notes",
] as const;

const taskSearchInputSchema = z.object({
  query: z.string().min(1),
  fields: z.array(z.enum(searchableTaskFields)).min(1).optional(),
  project_id: z.string().min(1).optional(),
  sprint_id: z.string().min(1).optional(),
  skip: z.number().int().min(0).optional(),
  limit: z.number().int().positive().max(500).optional(),
});

type ToolResult<T> = {
  content: Array<{ type: "text"; text: string }>;
  structuredContent?: T;
};

function asJson<T>(payload: T): ToolResult<T> {
  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(payload),
      },
    ],
    structuredContent: payload,
  };
}

async function withTaskLock<T>(
  taskId: string,
  operation: () => Promise<T>
): Promise<T> {
  const acquired = lockingService.checkout("task", taskId, TASK_LOCK_AGENT);
  if (!acquired) {
    throw new Error(`Task ${taskId} is currently locked by another agent.`);
  }

  try {
    return await operation();
  } finally {
    lockingService.checkin("task", taskId, TASK_LOCK_AGENT);
  }
}

async function withTaskLocks<T>(
  taskIds: string[],
  operation: () => Promise<T>
): Promise<T> {
  const acquired: string[] = [];

  try {
    for (const taskId of taskIds) {
      const lock = lockingService.checkout("task", taskId, TASK_LOCK_AGENT);
      if (!lock) {
        throw new Error(`Task ${taskId} is currently locked by another agent.`);
      }
      acquired.push(taskId);
    }

    return await operation();
  } finally {
    for (const taskId of acquired) {
      lockingService.checkin("task", taskId, TASK_LOCK_AGENT);
    }
  }
}

function sanitizeTaskUpdatePayload(
  payload: Record<string, unknown>
): Record<string, unknown> {
  return Object.fromEntries(
    Object.entries(payload).filter(
      ([, value]) => value !== null && value !== undefined
    )
  );
}

async function runWithAudit<T>(
  operation: string,
  subjectId: string | undefined,
  execute: () => Promise<T>
): Promise<T> {
  return withCorrelation(async () => {
    auditLog({
      operation,
      agent: TASK_LOCK_AGENT,
      result: "initiated",
      details: {
        subjectType: "task",
        subjectId,
      },
    });

    try {
      const result = await execute();
      auditLog({
        operation,
        agent: TASK_LOCK_AGENT,
        result: "success",
        details: {
          subjectType: "task",
          subjectId,
        },
      });
      return result;
    } catch (error) {
      auditLog({
        operation,
        agent: TASK_LOCK_AGENT,
        result: "error",
        details: {
          subjectType: "task",
          subjectId,
          message: error instanceof Error ? error.message : "Unknown error",
        },
      });
      throw error;
    }
  });
}

export function registerTaskFeatures(server: McpServer): void {
  server.registerTool(
    "task_create",
    {
      title: "Create Task",
      description: "Create a new task record.",
      inputSchema: {
        task: taskCreateSchema,
      },
      outputSchema: {
        task: taskRecordSchema,
      },
    },
    async ({ task }) => {
      const record = await runWithAudit("task_create", undefined, () =>
        backendClient.createTask(task)
      );
      return asJson({ task: record satisfies TaskRecord });
    }
  );

  server.registerTool(
    "task_read",
    {
      title: "Get Task",
      description: "Retrieve a task by its identifier.",
      inputSchema: {
        taskId: taskIdSchema,
      },
      outputSchema: {
        task: taskRecordSchema,
      },
    },
    async ({ taskId }) => {
      const record = await runWithAudit("task_read", taskId, () =>
        backendClient.getTask(taskId)
      );
      return asJson({ task: record satisfies TaskRecord });
    }
  );

  server.registerTool(
    "task_update",
    {
      title: "Update Task",
      description: "Update an existing task.",
      inputSchema: {
        taskId: taskIdSchema,
        changes: taskUpdatePayloadSchema,
      },
      outputSchema: {
        task: taskRecordSchema,
      },
    },
    async ({ taskId, changes }) =>
      withTaskLock(taskId, async () => {
        const filteredChanges = sanitizeTaskUpdatePayload(
          changes
        ) as TaskUpdate;

        const record = await runWithAudit("task_update", taskId, () =>
          backendClient.updateTask(taskId, filteredChanges)
        );
        return asJson({ task: record satisfies TaskRecord });
      })
  );

  server.registerTool(
    "task_set_status",
    {
      title: "Set Task Status",
      description: "Update the status of a task and optional completion notes.",
      inputSchema: taskStatusUpdateSchema.shape,
      outputSchema: {
        task: taskRecordSchema,
      },
    },
    async ({ taskId, status, notes, completion_notes, done_date }) =>
      withTaskLock(taskId, async () => {
        const statusUpdate = sanitizeTaskUpdatePayload({
          status,
          notes,
          completion_notes,
          done_date,
        }) as TaskUpdate;

        const record = await runWithAudit("task_set_status", taskId, () =>
          backendClient.updateTask(taskId, statusUpdate)
        );

        return asJson({ task: record satisfies TaskRecord });
      })
  );

  server.registerTool(
    "task_assign",
    {
      title: "Assign Task",
      description: "Assign or reassign a task to one or more owners.",
      inputSchema: taskAssignmentInputSchema,
      outputSchema: {
        task: taskRecordSchema,
      },
    },
    async ({
      taskId,
      assignee,
      assignees,
    }: z.infer<typeof taskAssignmentSchema>) =>
      withTaskLock(taskId, async () => {
        const record = await runWithAudit("task_assign", taskId, () =>
          backendClient.assignTask(taskId, { assignee, assignees })
        );

        return asJson({ task: record satisfies TaskRecord });
      })
  );

  server.registerTool(
    "task_delete",
    {
      title: "Delete Task",
      description: "Delete a task and release related locks.",
      inputSchema: {
        taskId: taskIdSchema,
      },
      outputSchema: {
        taskId: z.string(),
        deleted: z.literal(true),
      },
    },
    async ({ taskId }) =>
      withTaskLock(taskId, async () => {
        await runWithAudit("task_delete", taskId, () =>
          backendClient.deleteTask(taskId)
        );
        return asJson({ taskId, deleted: true });
      })
  );

  server.registerTool(
    "task_list",
    {
      title: "List Tasks",
      description: "List tasks with optional filters.",
      inputSchema: taskListFiltersSchema.shape,
      outputSchema: {
        tasks: z.array(taskRecordSchema),
      },
    },
    async (filters) => {
      const listFilters = Object.fromEntries(
        Object.entries(filters ?? {}).filter(([, value]) => value !== undefined)
      );
      const tasks = await runWithAudit("task_list", undefined, () =>
        backendClient.listTasks(listFilters)
      );
      return asJson({ tasks: tasks satisfies TaskRecord[] });
    }
  );

  server.registerTool(
    "task_bulk_update",
    {
      title: "Bulk Update Tasks",
      description: "Apply the same changes to multiple tasks at once.",
      inputSchema: taskBulkUpdateInputSchema.shape,
      outputSchema: {
        success: z.literal(true),
        updated_count: z.number().int().nonnegative(),
        task_ids: z.array(taskIdSchema),
      },
    },
    async ({ taskIds, changes }) =>
      withTaskLocks(taskIds, async () => {
        const sanitized = sanitizeTaskUpdatePayload(changes) as TaskUpdate;

        if (Object.keys(sanitized).length === 0) {
          throw new Error(
            "At least one field must be provided after sanitizing the changes."
          );
        }

        const result = await runWithAudit("task_bulk_update", taskIds[0], () =>
          backendClient.bulkUpdateTasks(taskIds, sanitized)
        );

        return asJson(result);
      })
  );

  server.registerTool(
    "task_bulk_assign_sprint",
    {
      title: "Bulk Assign Tasks to Sprint",
      description: "Assign multiple tasks to a sprint in one operation.",
      inputSchema: taskBulkAssignSprintInputSchema.shape,
      outputSchema: {
        success: z.literal(true),
        assigned_count: z.number().int().nonnegative(),
        sprint_id: z.string().min(1),
      },
    },
    async ({ taskIds, sprintId }) =>
      withTaskLocks(taskIds, async () => {
        const result = await runWithAudit(
          "task_bulk_assign_sprint",
          sprintId,
          () => backendClient.assignTasksToSprint(taskIds, sprintId)
        );

        return asJson(result);
      })
  );

  server.registerTool(
    "task_search",
    {
      title: "Search Tasks",
      description: "Search tasks across multiple fields using query filters.",
      inputSchema: taskSearchInputSchema.shape,
      outputSchema: {
        success: z.literal(true),
        query: z.string(),
        count: z.number().int().nonnegative(),
        tasks: z.array(taskRecordSchema),
      },
    },
    async ({ query, fields, project_id, sprint_id, skip, limit }) => {
      const searchResult = await runWithAudit("task_search", undefined, () =>
        backendClient.searchTasks({
          query,
          fields,
          project_id,
          sprint_id,
          skip,
          limit,
        })
      );

      return asJson({
        success: searchResult.success,
        query: searchResult.query,
        count: searchResult.count,
        tasks: searchResult.data satisfies TaskRecord[],
      });
    }
  );
}
