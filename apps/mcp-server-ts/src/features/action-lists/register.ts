import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

// Use circuit breaker-protected client (re-enabled after backend endpoint implemented)
import { backendClientWithCircuitBreaker as backendClient } from "../../backend/client-with-circuit-breaker.js";

import {
  actionListRecordSchema,
  actionListSchema,
  actionListUpdateSchema,
} from "../../core/schemas.js";
import {
  ActionListPriority,
  ActionListRecord,
  ActionListStatus,
} from "../../core/types.js";
import { auditLog, withCorrelation } from "../../infrastructure/audit.js";
import { lockingService } from "../../infrastructure/locking.js";

const ACTION_LIST_LOCK_AGENT = "action-list-tools";

const actionListIdSchema = z.string().min(1, "actionListId is required");
const actionListCreateSchema = actionListSchema;

const actionListListInputSchema = z.object({
  status: z.nativeEnum(ActionListStatus).optional(),
  priority: z.nativeEnum(ActionListPriority).optional(),
  owner: z.string().min(1).optional(),
  project_id: z.string().min(1).optional(),
  sprint_id: z.string().min(1).optional(),
  tags: z.array(z.string().min(1)).max(25).optional(),
  limit: z.number().int().positive().max(100).optional(),
  cursor: z.string().min(1).optional(),
});

const actionListUpdateBaseSchema = z
  .object({
    action_list_id: actionListIdSchema,
  })
  .extend(actionListUpdateSchema.shape);

const actionListUpdateInputSchema = actionListUpdateBaseSchema.refine(
  (value) =>
    Object.entries(value).some(
      ([key, val]) =>
        key !== "action_list_id" && val !== undefined && val !== null
    ),
  {
    message: "At least one field must be provided to update an action list.",
  }
);

const actionListAddItemInputSchema = z.object({
  action_list_id: actionListIdSchema,
  text: z.string().min(1, "Item text is required"),
  order: z.number().int().min(0).optional(),
});

const actionListReorderInputSchema = z.object({
  action_list_id: actionListIdSchema,
  item_ids: z.array(z.string().min(1)).min(1, "At least one item ID required"),
});

// Bulk Operations Schemas
const actionListBulkDeleteInputSchema = z.object({
  action_list_ids: z.array(z.string().min(1)).min(1, "At least one action list ID required"),
});

const actionListBulkUpdateInputSchemaBase = z.object({
  action_list_ids: z.array(z.string().min(1)).min(1, "At least one action list ID required"),
  status: z.nativeEnum(ActionListStatus).optional(),
  priority: z.nativeEnum(ActionListPriority).optional(),
  project_id: z.string().min(1).optional(),
  sprint_id: z.string().min(1).optional(),
  notes: z.string().optional(),
});

const actionListBulkUpdateInputSchema = actionListBulkUpdateInputSchemaBase.refine(
  (value) =>
    value.status !== undefined ||
    value.priority !== undefined ||
    value.project_id !== undefined ||
    value.sprint_id !== undefined ||
    value.notes !== undefined,
  {
    message: "At least one update field (status, priority, project_id, sprint_id, notes) must be provided",
  }
);

const actionListSearchInputSchema = z.object({
  q: z.string().min(1, "Search query is required"),
  fields: z.array(z.enum(["title", "description", "notes"])).optional(),
  project_id: z.string().min(1).optional(),
  sprint_id: z.string().min(1).optional(),
  status: z.nativeEnum(ActionListStatus).optional(),
  priority: z.nativeEnum(ActionListPriority).optional(),
  skip: z.number().int().min(0).optional(),
  limit: z.number().int().positive().max(100).optional(),
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

async function withActionListLock<T>(
  actionListId: string,
  operation: () => Promise<T>
): Promise<T> {
  const acquired = lockingService.checkout(
    "action-list",
    actionListId,
    ACTION_LIST_LOCK_AGENT
  );
  if (!acquired) {
    throw new Error(
      `ActionList ${actionListId} is currently locked by another agent.`
    );
  }

  try {
    return await operation();
  } finally {
    lockingService.checkin("action-list", actionListId, ACTION_LIST_LOCK_AGENT);
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
      agent: ACTION_LIST_LOCK_AGENT,
      result: "initiated",
      details: {
        subjectType: "action-list",
        subjectId,
      },
    });

    try {
      const result = await execute();
      auditLog({
        operation,
        agent: ACTION_LIST_LOCK_AGENT,
        result: "success",
        details: {
          subjectType: "action-list",
          subjectId,
        },
      });
      return result;
    } catch (error) {
      auditLog({
        operation,
        agent: ACTION_LIST_LOCK_AGENT,
        result: "error",
        details: {
          subjectType: "action-list",
          subjectId,
          message: error instanceof Error ? error.message : "Unknown error",
        },
      });
      throw error;
    }
  });
}

export function registerActionListFeatures(server: McpServer): void {
  // 1. Create ActionList
  server.registerTool(
    "action_list_create",
    {
      title: "Create Action List",
      description:
        "Create a new action list with optional project/sprint association.",
      inputSchema: actionListCreateSchema.shape,
      outputSchema: {
        action_list: actionListRecordSchema,
      },
    },
    async (input) => {
      const validated = actionListCreateSchema.parse(input);
      const record = await runWithAudit(
        "action_list_create",
        undefined,
        () => backendClient.createActionList(validated)
      );
      return asJson({ action_list: record satisfies ActionListRecord });
    }
  );

  // 2. Get ActionList
  server.registerTool(
    "action_list_read",
    {
      title: "Get Action List",
      description: "Retrieve an action list by its identifier.",
      inputSchema: {
        action_list_id: actionListIdSchema,
      },
      outputSchema: {
        action_list: actionListRecordSchema,
      },
    },
    async ({ action_list_id }) => {
      const record = await runWithAudit(
        "action_list_read",
        action_list_id,
        () => backendClient.getActionList(action_list_id)
      );
      return asJson({ action_list: record satisfies ActionListRecord });
    }
  );

  // 3. List ActionLists
  server.registerTool(
    "action_list_list",
    {
      title: "List Action Lists",
      description:
        "List action lists with optional filtering by status, project, sprint, owner, or tags.",
      inputSchema: actionListListInputSchema.shape,
      outputSchema: {
        action_lists: z.array(actionListRecordSchema),
      },
    },
    async (filters) => {
      const records = await runWithAudit("action_list_list", undefined, () =>
        backendClient.listActionLists(filters)
      );
      return asJson({ action_lists: records });
    }
  );

  // 4. Update ActionList
  server.registerTool(
    "action_list_update",
    {
      title: "Update Action List",
      description:
        "Update an action list's properties (name, description, status, priority, notes, etc).",
      inputSchema: actionListUpdateBaseSchema.shape,
      outputSchema: {
        action_list: actionListRecordSchema,
      },
    },
    async (input: z.infer<typeof actionListUpdateBaseSchema>) => {
      const validated = actionListUpdateInputSchema.parse(input);
      const { action_list_id, ...changes } = validated;
      const record = await withActionListLock(action_list_id, () =>
        runWithAudit("action_list_update", action_list_id, () =>
          backendClient.updateActionList(action_list_id, changes)
        )
      );
      return asJson({ action_list: record satisfies ActionListRecord });
    }
  );

  // 5. Delete ActionList
  server.registerTool(
    "action_list_delete",
    {
      title: "Delete Action List",
      description: "Permanently delete an action list and all its items.",
      inputSchema: {
        action_list_id: actionListIdSchema,
      },
      outputSchema: {
        success: z.boolean(),
      },
    },
    async ({ action_list_id }) => {
      await withActionListLock(action_list_id, () =>
        runWithAudit("action_list_delete", action_list_id, () =>
          backendClient.deleteActionList(action_list_id)
        )
      );
      return asJson({ success: true });
    }
  );

  // 6. Add Item to ActionList
  server.registerTool(
    "action_list_add_item",
    {
      title: "Add Item to Action List",
      description:
        "Add a new item to an action list with optional order specification.",
      inputSchema: actionListAddItemInputSchema.shape,
      outputSchema: {
        action_list: actionListRecordSchema,
      },
    },
    async ({ action_list_id, text, order }) => {
      const record = await withActionListLock(action_list_id, () =>
        runWithAudit("action_list_add_item", action_list_id, () =>
          backendClient.addActionListItem(action_list_id, { text, order })
        )
      );
      return asJson({ action_list: record satisfies ActionListRecord });
    }
  );

  // 7. Toggle Item Completion
  server.registerTool(
    "action_list_toggle_item",
    {
      title: "Toggle Action List Item",
      description:
        "Toggle the completion state of an item in an action list (completed ↔ pending).",
      inputSchema: {
        action_list_id: actionListIdSchema,
        item_id: z.string().min(1, "item_id is required"),
      },
      outputSchema: {
        action_list: actionListRecordSchema,
      },
    },
    async ({ action_list_id, item_id }) => {
      const record = await withActionListLock(action_list_id, () =>
        runWithAudit("action_list_toggle_item", action_list_id, () =>
          backendClient.toggleActionListItem(action_list_id, item_id)
        )
      );
      return asJson({ action_list: record satisfies ActionListRecord });
    }
  );

  // 8. Remove Item from ActionList
  server.registerTool(
    "action_list_remove_item",
    {
      title: "Remove Item from Action List",
      description: "Remove an item from an action list by its item ID.",
      inputSchema: {
        action_list_id: actionListIdSchema,
        item_id: z.string().min(1, "item_id is required"),
      },
      outputSchema: {
        action_list: actionListRecordSchema,
      },
    },
    async ({ action_list_id, item_id }) => {
      const record = await withActionListLock(action_list_id, () =>
        runWithAudit("action_list_remove_item", action_list_id, () =>
          backendClient.removeActionListItem(action_list_id, item_id)
        )
      );
      return asJson({ action_list: record satisfies ActionListRecord });
    }
  );

  // 9. Reorder ActionList Items
  server.registerTool(
    "action_list_reorder_items",
    {
      title: "Reorder Action List Items",
      description:
        "Reorder items in an action list by providing the desired sequence of item IDs.",
      inputSchema: actionListReorderInputSchema.shape,
      outputSchema: {
        action_list: actionListRecordSchema,
      },
    },
    async ({ action_list_id, item_ids }) => {
      const record = await withActionListLock(action_list_id, () =>
        runWithAudit("action_list_reorder_items", action_list_id, () =>
          backendClient.reorderActionListItems(action_list_id, item_ids)
        )
      );
      return asJson({ action_list: record satisfies ActionListRecord });
    }
  );

  // Bulk Operations Tools
  server.registerTool(
    "action_list_bulk_delete",
    {
      title: "Bulk Delete Action Lists",
      description: "Delete multiple action lists in a single operation.",
      inputSchema: actionListBulkDeleteInputSchema.shape,
      outputSchema: {
        success: z.boolean(),
        deleted_count: z.number(),
      },
    },
    async ({ action_list_ids }) => {
      const result = await runWithAudit(
        "action_list_bulk_delete",
        undefined,
        () => backendClient.bulkDeleteActionLists(action_list_ids)
      );
      return asJson(result);
    }
  );

  server.registerTool(
    "action_list_bulk_update",
    {
      title: "Bulk Update Action Lists",
      description: "Update multiple action lists with the same changes in a single operation.",
      inputSchema: actionListBulkUpdateInputSchemaBase.shape,
      outputSchema: {
        success: z.boolean(),
        updated_count: z.number(),
        action_list_ids: z.array(z.string()),
      },
    },
    async ({ action_list_ids, ...updates }) => {
      const result = await runWithAudit(
        "action_list_bulk_update",
        undefined,
        () => backendClient.bulkUpdateActionLists(action_list_ids, updates)
      );
      return asJson(result);
    }
  );

  server.registerTool(
    "action_list_search",
    {
      title: "Search Action Lists",
      description: "Search action lists with advanced filtering and pagination.",
      inputSchema: actionListSearchInputSchema.shape,
      outputSchema: {
        success: z.boolean(),
        query: z.string(),
        count: z.number(),
        data: z.array(actionListRecordSchema),
      },
    },
    async ({ q, fields, project_id, sprint_id, status, priority, skip, limit }) => {
      const result = await runWithAudit(
        "action_list_search",
        undefined,
        () => backendClient.searchActionLists(q, {
          fields,
          project_id,
          sprint_id,
          status,
          priority,
          skip,
          limit,
        })
      );
      return asJson(result);
    }
  );
}
