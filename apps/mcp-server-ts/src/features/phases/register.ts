/**
 * Phase Tracking MCP Tools Registration
 *
 * Provides MCP tools for managing lifecycle phases on Tasks, Sprints, and Projects.
 *
 * Tools:
 * - phase_get: Get all phases for an entity
 * - phase_get_single: Get a specific phase
 * - phase_update: Update a specific phase
 * - phase_advance: Advance entity to next phase
 * - phase_start: Start a specific phase
 * - phase_complete: Complete a specific phase
 * - phase_block: Block a phase with reason
 * - phase_unblock: Unblock a phase
 * - phase_skip: Skip a phase with reason
 * - phase_summary: Get phase summary with metrics
 * - phase_analytics: Get phase analytics for entity type
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

import { backendClientWithCircuitBreaker as backendClient } from "../../backend/client-with-circuit-breaker.js";
import {
  phaseEntityTypeSchema,
  phaseNameSchema,
  phaseStatusSchema,
  phasesResponseSchema,
  phaseResponseSchema,
  phaseSummaryResponseSchema,
  phaseAnalyticsResponseSchema,
  phaseUpdateRequestSchema,
} from "../../core/phase-schemas.js";
import { auditLog, withCorrelation } from "../../infrastructure/audit.js";

const PHASE_AGENT = "phase-tools";

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

async function runWithAudit<T>(
  operation: string,
  details: Record<string, unknown>,
  execute: () => Promise<T>
): Promise<T> {
  return withCorrelation(async () => {
    auditLog({
      operation,
      agent: PHASE_AGENT,
      result: "initiated",
      details,
    });

    try {
      const result = await execute();
      auditLog({
        operation,
        agent: PHASE_AGENT,
        result: "success",
        details,
      });
      return result;
    } catch (error) {
      auditLog({
        operation,
        agent: PHASE_AGENT,
        result: "error",
        details: {
          ...details,
          message: error instanceof Error ? error.message : "Unknown error",
        },
      });
      throw error;
    }
  });
}

export function registerPhaseFeatures(server: McpServer): void {
  // =========================================================================
  // Phase Read Tools
  // =========================================================================

  server.registerTool(
    "phase_get",
    {
      title: "Get Entity Phases",
      description:
        "Get all lifecycle phases for a task, sprint, or project. " +
        "Returns the full phase tracking data including status of each phase.",
      inputSchema: {
        entityType: phaseEntityTypeSchema.describe(
          "Entity type: task, sprint, or project"
        ),
        entityId: z.string().min(1).describe("Entity identifier"),
      },
      outputSchema: {
        entity_id: z.string(),
        entity_type: phaseEntityTypeSchema,
        phases: z.record(z.unknown()),
      },
    },
    async ({ entityType, entityId }) => {
      const result = await runWithAudit(
        "phase_get",
        { entityType, entityId },
        () => backendClient.getPhases(entityType, entityId)
      );
      return asJson(phasesResponseSchema.parse(result));
    }
  );

  server.registerTool(
    "phase_get_single",
    {
      title: "Get Single Phase",
      description:
        "Get a specific phase for an entity. " +
        "Returns detailed phase data including status and all phase-specific fields.",
      inputSchema: {
        entityType: phaseEntityTypeSchema.describe(
          "Entity type: task, sprint, or project"
        ),
        entityId: z.string().min(1).describe("Entity identifier"),
        phaseName: phaseNameSchema.describe(
          "Phase name: research, planning, implementation, or testing"
        ),
      },
      outputSchema: {
        phase_name: z.string(),
        status: phaseStatusSchema,
        data: z.record(z.unknown()),
      },
    },
    async ({ entityType, entityId, phaseName }) => {
      const result = await runWithAudit(
        "phase_get_single",
        { entityType, entityId, phaseName },
        () => backendClient.getPhase(entityType, entityId, phaseName)
      );
      return asJson(phaseResponseSchema.parse(result));
    }
  );

  server.registerTool(
    "phase_summary",
    {
      title: "Get Phase Summary",
      description:
        "Get a summary of phase progress for an entity. " +
        "Returns current phase, completion percentage, and status of all phases.",
      inputSchema: {
        entityType: phaseEntityTypeSchema.describe(
          "Entity type: task, sprint, or project"
        ),
        entityId: z.string().min(1).describe("Entity identifier"),
      },
      outputSchema: {
        entity_id: z.string(),
        entity_type: phaseEntityTypeSchema,
        current_phase: z.string().nullable(),
        phases_completed: z.number().int().nonnegative(),
        phases_total: z.number().int().nonnegative(),
        completion_pct: z.number().min(0).max(100),
        phases: z.record(z.unknown()),
      },
    },
    async ({ entityType, entityId }) => {
      const result = await runWithAudit(
        "phase_summary",
        { entityType, entityId },
        () => backendClient.getPhaseSummary(entityType, entityId)
      );
      return asJson(phaseSummaryResponseSchema.parse(result));
    }
  );

  server.registerTool(
    "phase_analytics",
    {
      title: "Get Phase Analytics",
      description:
        "Get aggregate phase analytics for an entity type. " +
        "Returns counts by phase and status, blocked count, and average completion.",
      inputSchema: {
        entityType: phaseEntityTypeSchema.describe(
          "Entity type: task, sprint, or project"
        ),
        limit: z
          .number()
          .int()
          .positive()
          .max(1000)
          .optional()
          .describe("Maximum entities to analyze (default: 1000)"),
      },
      outputSchema: {
        entity_type: phaseEntityTypeSchema,
        total_entities: z.number().int().nonnegative(),
        by_phase: z.record(z.record(z.number().int().nonnegative())),
        blocked_count: z.number().int().nonnegative(),
        average_completion_pct: z.number().min(0).max(100),
      },
    },
    async ({ entityType, limit }) => {
      const result = await runWithAudit(
        "phase_analytics",
        { entityType, limit },
        () => backendClient.getPhaseAnalytics(entityType, limit)
      );
      return asJson(phaseAnalyticsResponseSchema.parse(result));
    }
  );

  // =========================================================================
  // Phase Mutation Tools
  // =========================================================================

  server.registerTool(
    "phase_update",
    {
      title: "Update Phase",
      description:
        "Update a specific phase for an entity. " +
        "Can update status, blocked reason, skip reason, and additional phase-specific fields.",
      inputSchema: {
        entityType: phaseEntityTypeSchema.describe(
          "Entity type: task, sprint, or project"
        ),
        entityId: z.string().min(1).describe("Entity identifier"),
        phaseName: phaseNameSchema.describe("Phase name to update"),
        update: phaseUpdateRequestSchema.describe("Phase update data"),
      },
      outputSchema: {
        entity_id: z.string(),
        entity_type: phaseEntityTypeSchema,
        phases: z.record(z.unknown()),
      },
    },
    async ({ entityType, entityId, phaseName, update }) => {
      const result = await runWithAudit(
        "phase_update",
        { entityType, entityId, phaseName },
        () => backendClient.updatePhase(entityType, entityId, phaseName, update)
      );
      return asJson(phasesResponseSchema.parse(result));
    }
  );

  server.registerTool(
    "phase_advance",
    {
      title: "Advance Phase",
      description:
        "Advance entity to the next lifecycle phase. " +
        "Completes current phase and starts the next one in sequence.",
      inputSchema: {
        entityType: phaseEntityTypeSchema.describe(
          "Entity type: task, sprint, or project"
        ),
        entityId: z.string().min(1).describe("Entity identifier"),
      },
      outputSchema: {
        entity_id: z.string(),
        entity_type: phaseEntityTypeSchema,
        phases: z.record(z.unknown()),
      },
    },
    async ({ entityType, entityId }) => {
      const result = await runWithAudit(
        "phase_advance",
        { entityType, entityId },
        () => backendClient.advancePhase(entityType, entityId)
      );
      return asJson(phasesResponseSchema.parse(result));
    }
  );

  server.registerTool(
    "phase_start",
    {
      title: "Start Phase",
      description:
        "Start a specific phase for an entity. " +
        "Sets phase status to in_progress.",
      inputSchema: {
        entityType: phaseEntityTypeSchema.describe(
          "Entity type: task, sprint, or project"
        ),
        entityId: z.string().min(1).describe("Entity identifier"),
        phaseName: phaseNameSchema.describe("Phase name to start"),
      },
      outputSchema: {
        entity_id: z.string(),
        entity_type: phaseEntityTypeSchema,
        phases: z.record(z.unknown()),
      },
    },
    async ({ entityType, entityId, phaseName }) => {
      const result = await runWithAudit(
        "phase_start",
        { entityType, entityId, phaseName },
        () => backendClient.startPhase(entityType, entityId, phaseName)
      );
      return asJson(phasesResponseSchema.parse(result));
    }
  );

  server.registerTool(
    "phase_complete",
    {
      title: "Complete Phase",
      description:
        "Mark a specific phase as completed. " +
        "Sets phase status to completed with completion timestamp.",
      inputSchema: {
        entityType: phaseEntityTypeSchema.describe(
          "Entity type: task, sprint, or project"
        ),
        entityId: z.string().min(1).describe("Entity identifier"),
        phaseName: phaseNameSchema.describe("Phase name to complete"),
      },
      outputSchema: {
        entity_id: z.string(),
        entity_type: phaseEntityTypeSchema,
        phases: z.record(z.unknown()),
      },
    },
    async ({ entityType, entityId, phaseName }) => {
      const result = await runWithAudit(
        "phase_complete",
        { entityType, entityId, phaseName },
        () => backendClient.completePhase(entityType, entityId, phaseName)
      );
      return asJson(phasesResponseSchema.parse(result));
    }
  );

  server.registerTool(
    "phase_block",
    {
      title: "Block Phase",
      description:
        "Mark a phase as blocked with an optional reason. " +
        "Blocked phases prevent progress until unblocked.",
      inputSchema: {
        entityType: phaseEntityTypeSchema.describe(
          "Entity type: task, sprint, or project"
        ),
        entityId: z.string().min(1).describe("Entity identifier"),
        phaseName: phaseNameSchema.describe("Phase name to block"),
        blockedReason: z
          .string()
          .max(500)
          .optional()
          .describe("Reason for blocking"),
      },
      outputSchema: {
        entity_id: z.string(),
        entity_type: phaseEntityTypeSchema,
        phases: z.record(z.unknown()),
      },
    },
    async ({ entityType, entityId, phaseName, blockedReason }) => {
      const result = await runWithAudit(
        "phase_block",
        { entityType, entityId, phaseName, blockedReason },
        () =>
          backendClient.blockPhase(entityType, entityId, phaseName, blockedReason)
      );
      return asJson(phasesResponseSchema.parse(result));
    }
  );

  server.registerTool(
    "phase_unblock",
    {
      title: "Unblock Phase",
      description:
        "Remove blocked status from a phase. " +
        "Allows the phase to resume progress.",
      inputSchema: {
        entityType: phaseEntityTypeSchema.describe(
          "Entity type: task, sprint, or project"
        ),
        entityId: z.string().min(1).describe("Entity identifier"),
        phaseName: phaseNameSchema.describe("Phase name to unblock"),
      },
      outputSchema: {
        entity_id: z.string(),
        entity_type: phaseEntityTypeSchema,
        phases: z.record(z.unknown()),
      },
    },
    async ({ entityType, entityId, phaseName }) => {
      const result = await runWithAudit(
        "phase_unblock",
        { entityType, entityId, phaseName },
        () => backendClient.unblockPhase(entityType, entityId, phaseName)
      );
      return asJson(phasesResponseSchema.parse(result));
    }
  );

  server.registerTool(
    "phase_skip",
    {
      title: "Skip Phase",
      description:
        "Skip a phase with an optional reason. " +
        "Skipped phases are marked as intentionally not completed.",
      inputSchema: {
        entityType: phaseEntityTypeSchema.describe(
          "Entity type: task, sprint, or project"
        ),
        entityId: z.string().min(1).describe("Entity identifier"),
        phaseName: phaseNameSchema.describe("Phase name to skip"),
        skipReason: z
          .string()
          .max(500)
          .optional()
          .describe("Reason for skipping"),
      },
      outputSchema: {
        entity_id: z.string(),
        entity_type: phaseEntityTypeSchema,
        phases: z.record(z.unknown()),
      },
    },
    async ({ entityType, entityId, phaseName, skipReason }) => {
      const result = await runWithAudit(
        "phase_skip",
        { entityType, entityId, phaseName, skipReason },
        () => backendClient.skipPhase(entityType, entityId, phaseName, skipReason)
      );
      return asJson(phasesResponseSchema.parse(result));
    }
  );
}
