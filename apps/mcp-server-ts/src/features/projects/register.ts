import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import {
  backendClient,
  ProjectBlockerInput,
  ProjectCommentInput,
  ProjectMetaTaskInput,
} from "../../backend/client.js";
import {
  projectAnalyticsSchema,
  projectRecordSchema,
  projectSchema,
} from "../../core/schemas.js";
import { ProjectRecord, ProjectStatus, Severity } from "../../core/types.js";
import { auditLog, withCorrelation } from "../../infrastructure/audit.js";
import { lockingService } from "../../infrastructure/locking.js";

const PROJECT_LOCK_AGENT = "project-tools";

const projectIdSchema = z.string().min(1, "projectId is required");
const sprintIdSchema = z.string().min(1, "sprintId is required");

const projectCreateSchema = projectSchema.omit({ id: true });
const projectUpdateSchema = projectCreateSchema
  .partial()
  .refine(
    (value) =>
      Object.values(value).some((item) => item !== undefined && item !== null),
    {
      message: "At least one field must be provided to update a project.",
    }
  );

const projectListFiltersSchema = z.object({
  status: z.nativeEnum(ProjectStatus).optional(),
  search: z.string().min(1).optional(),
  limit: z.number().int().positive().max(100).optional(),
  cursor: z.string().min(1).optional(),
});

const projectCommentSchema: z.ZodType<ProjectCommentInput> = z.object({
  message: z.string().min(1, "message is required"),
  author: z.string().min(1).max(100).optional(),
  tags: z.array(z.string().min(1)).max(10).optional(),
});

const projectBlockerSchema: z.ZodType<ProjectBlockerInput> = z.object({
  title: z.string().min(1, "title is required"),
  description: z.string().optional(),
  severity: z.nativeEnum(Severity).optional(),
  linked_task_id: z.string().optional(),
  external_reference: z.string().optional(),
});

const projectMetaTaskSchema: z.ZodType<ProjectMetaTaskInput> = z.object({
  title: z.string().min(1, "title is required"),
  description: z.string().optional(),
  owner: z.string().optional(),
  due_date: z.string().datetime().optional(),
});

const commentsListParamsSchema = z.object({
  limit: z.number().int().positive().max(100).optional(),
  cursor: z.string().min(1).optional(),
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

async function withProjectLock<T>(
  projectId: string,
  operation: () => Promise<T>
): Promise<T> {
  const acquired = lockingService.checkout(
    "project",
    projectId,
    PROJECT_LOCK_AGENT
  );
  if (!acquired) {
    throw new Error(
      `Project ${projectId} is currently locked by another agent.`
    );
  }

  try {
    return await operation();
  } finally {
    lockingService.checkin("project", projectId, PROJECT_LOCK_AGENT);
  }
}

async function runWithAudit<T>(
  operation: string,
  subjectId: string | undefined,
  execute: () => Promise<T>
): Promise<T> {
  return withCorrelation(async () => {
    auditLog({
      operation,
      agent: PROJECT_LOCK_AGENT,
      result: "initiated",
      details: {
        subjectType: "project",
        subjectId,
      },
    });

    try {
      const result = await execute();
      auditLog({
        operation,
        agent: PROJECT_LOCK_AGENT,
        result: "success",
        details: {
          subjectType: "project",
          subjectId,
        },
      });
      return result;
    } catch (error) {
      auditLog({
        operation,
        agent: PROJECT_LOCK_AGENT,
        result: "error",
        details: {
          subjectType: "project",
          subjectId,
          message: error instanceof Error ? error.message : "Unknown error",
        },
      });
      throw error;
    }
  });
}

export function registerProjectFeatures(server: McpServer): void {
  server.registerTool(
    "project_create",
    {
      title: "Create Project",
      description: "Create a new project record.",
      inputSchema: {
        project: projectCreateSchema,
      },
      outputSchema: {
        project: projectRecordSchema,
      },
    },
    async ({ project }) => {
      const record = await runWithAudit("project_create", undefined, () =>
        backendClient.createProject(project)
      );
      return asJson({ project: record satisfies ProjectRecord });
    }
  );

  server.registerTool(
    "project_read",
    {
      title: "Get Project",
      description: "Retrieve a project by its identifier.",
      inputSchema: {
        projectId: projectIdSchema,
      },
      outputSchema: {
        project: projectRecordSchema,
      },
    },
    async ({ projectId }) => {
      const record = await runWithAudit("project_read", projectId, () =>
        backendClient.getProject(projectId)
      );
      return asJson({ project: record satisfies ProjectRecord });
    }
  );

  server.registerTool(
    "project_update",
    {
      title: "Update Project",
      description: "Update an existing project.",
      inputSchema: {
        projectId: projectIdSchema,
        changes: projectUpdateSchema,
      },
      outputSchema: {
        project: projectRecordSchema,
      },
    },
    async ({ projectId, changes }) =>
      withProjectLock(projectId, async () => {
        const record = await runWithAudit("project_update", projectId, () =>
          backendClient.updateProject(projectId, changes)
        );
        return asJson({ project: record satisfies ProjectRecord });
      })
  );

  server.registerTool(
    "project_delete",
    {
      title: "Delete Project",
      description: "Delete a project and release related locks.",
      inputSchema: {
        projectId: projectIdSchema,
      },
      outputSchema: {
        projectId: z.string(),
        deleted: z.literal(true),
      },
    },
    async ({ projectId }) =>
      withProjectLock(projectId, async () => {
        await runWithAudit("project_delete", projectId, () =>
          backendClient.deleteProject(projectId)
        );
        return asJson({ projectId, deleted: true });
      })
  );

  server.registerTool(
    "project_list",
    {
      title: "List Projects",
      description: "List projects with optional filters.",
      inputSchema: projectListFiltersSchema.shape,
      outputSchema: {
        projects: z.array(projectRecordSchema),
      },
    },
    async (filters) => {
      const listFilters = Object.fromEntries(
        Object.entries(filters ?? {}).filter(([, value]) => value !== undefined)
      );
      const projects = await runWithAudit("project_list", undefined, () =>
        backendClient.listProjects(listFilters)
      );
      return asJson({ projects: projects satisfies ProjectRecord[] });
    }
  );

  server.registerTool(
    "project_add_sprint",
    {
      title: "Add Sprint to Project",
      description: "Associate a sprint with a project.",
      inputSchema: {
        projectId: projectIdSchema,
        sprintId: sprintIdSchema,
      },
      outputSchema: {
        project: projectRecordSchema,
      },
    },
    async ({ projectId, sprintId }) =>
      withProjectLock(projectId, async () => {
        const record = await runWithAudit("project_add_sprint", projectId, () =>
          backendClient.addSprintToProject(projectId, sprintId)
        );
        return asJson({ project: record satisfies ProjectRecord });
      })
  );

  server.registerTool(
    "project_remove_sprint",
    {
      title: "Remove Sprint from Project",
      description: "Detach a sprint from the project.",
      inputSchema: {
        projectId: projectIdSchema,
        sprintId: sprintIdSchema,
      },
      outputSchema: {
        projectId: z.string(),
        sprintId: z.string(),
        project: projectRecordSchema.nullish(),
      },
    },
    async ({ projectId, sprintId }) =>
      withProjectLock(projectId, async () => {
        const record = await runWithAudit(
          "project_remove_sprint",
          projectId,
          () => backendClient.removeSprintFromProject(projectId, sprintId)
        );
        return asJson({ projectId, sprintId, project: record });
      })
  );

  server.registerTool(
    "project_add_meta_task",
    {
      title: "Add Project Meta Task",
      description: "Create a meta task scoped to a project.",
      inputSchema: {
        projectId: projectIdSchema,
        metaTask: projectMetaTaskSchema,
      },
      outputSchema: {
        projectId: z.string(),
        metaTask: z.unknown(),
      },
    },
    async ({ projectId, metaTask }) =>
      withProjectLock(projectId, async () => {
        const result = await runWithAudit(
          "project_add_meta_task",
          projectId,
          () => backendClient.addProjectMetaTask(projectId, metaTask)
        );
        return asJson({ projectId, metaTask: result });
      })
  );

  server.registerTool(
    "project_add_comment",
    {
      title: "Add Project Comment",
      description: "Attach a comment to a project.",
      inputSchema: {
        projectId: projectIdSchema,
        comment: projectCommentSchema,
      },
      outputSchema: {
        projectId: z.string(),
        comment: z.unknown(),
      },
    },
    async ({ projectId, comment }) =>
      withProjectLock(projectId, async () => {
        const result = await runWithAudit(
          "project_add_comment",
          projectId,
          () => backendClient.addProjectComment(projectId, comment)
        );
        return asJson({ projectId, comment: result });
      })
  );

  server.registerTool(
    "project_add_blocker",
    {
      title: "Add Project Blocker",
      description: "Record a blocker for a project.",
      inputSchema: {
        projectId: projectIdSchema,
        blocker: projectBlockerSchema,
      },
      outputSchema: {
        projectId: z.string(),
        blocker: z.unknown(),
      },
    },
    async ({ projectId, blocker }) =>
      withProjectLock(projectId, async () => {
        const result = await runWithAudit(
          "project_add_blocker",
          projectId,
          () => backendClient.addProjectBlocker(projectId, blocker)
        );
        return asJson({ projectId, blocker: result });
      })
  );

  server.registerTool(
    "project_get_comments",
    {
      title: "List Project Comments",
      description: "Retrieve comments attached to a project.",
      inputSchema: {
        projectId: projectIdSchema,
        params: commentsListParamsSchema.optional(),
      },
      outputSchema: {
        projectId: z.string(),
        comments: z.array(z.unknown()),
      },
    },
    async ({ projectId, params }) => {
      const response = await runWithAudit(
        "project_get_comments",
        projectId,
        () => backendClient.listProjectComments(projectId, params ?? {})
      );
      return asJson({ projectId, comments: response });
    }
  );

  server.registerTool(
    "project_get_metrics",
    {
      title: "Get Project Metrics",
      description: "Retrieve metrics for a project.",
      inputSchema: {
        projectId: projectIdSchema,
      },
      outputSchema: {
        projectId: z.string(),
        metrics: projectAnalyticsSchema,
      },
    },
    async ({ projectId }) => {
      const metrics = await runWithAudit("project_get_metrics", projectId, () =>
        backendClient.getProjectMetrics(projectId)
      );
      return asJson({ projectId, metrics });
    }
  );
}
