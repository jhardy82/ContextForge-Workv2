/**
 * Phase Tracking MCP Tools Integration Tests
 *
 * Tests the phase tracking feature registration and tool functionality.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { beforeEach, describe, expect, it, vi } from "vitest";

import * as phaseSchemas from "../../core/phase-schemas.js";
import { registerPhaseFeatures } from "./register.js";

// Mock the circuit breaker client
vi.mock("../../backend/client-with-circuit-breaker.js", () => ({
  backendClientWithCircuitBreaker: {
    getPhases: vi.fn(),
    getPhase: vi.fn(),
    getPhaseSummary: vi.fn(),
    getPhaseAnalytics: vi.fn(),
    updatePhase: vi.fn(),
    advancePhase: vi.fn(),
    startPhase: vi.fn(),
    completePhase: vi.fn(),
    blockPhase: vi.fn(),
    unblockPhase: vi.fn(),
    skipPhase: vi.fn(),
  },
}));

// Mock audit logging
vi.mock("../../infrastructure/audit.js", () => ({
  auditLog: vi.fn(),
  withCorrelation: vi.fn((fn) => fn()),
}));

// Import the mocked client
import { backendClientWithCircuitBreaker as mockClient } from "../../backend/client-with-circuit-breaker.js";

describe("Phase Tracking MCP Tools", () => {
  let server: McpServer;
  let registeredTools: Map<string, any>;

  beforeEach(() => {
    vi.clearAllMocks();

    // Create a mock server that captures tool registrations
    registeredTools = new Map();
    server = {
      registerTool: vi.fn((name, config, handler) => {
        registeredTools.set(name, { config, handler });
      }),
    } as unknown as McpServer;

    // Register all phase features
    registerPhaseFeatures(server);
  });

  describe("Tool Registration", () => {
    it("should register all 11 phase tools", () => {
      expect(server.registerTool).toHaveBeenCalledTimes(11);
    });

    it("should register phase_get tool", () => {
      expect(registeredTools.has("phase_get")).toBe(true);
      const tool = registeredTools.get("phase_get");
      expect(tool.config.title).toBe("Get Entity Phases");
    });

    it("should register phase_get_single tool", () => {
      expect(registeredTools.has("phase_get_single")).toBe(true);
      const tool = registeredTools.get("phase_get_single");
      expect(tool.config.title).toBe("Get Single Phase");
    });

    it("should register phase_summary tool", () => {
      expect(registeredTools.has("phase_summary")).toBe(true);
      const tool = registeredTools.get("phase_summary");
      expect(tool.config.title).toBe("Get Phase Summary");
    });

    it("should register phase_analytics tool", () => {
      expect(registeredTools.has("phase_analytics")).toBe(true);
      const tool = registeredTools.get("phase_analytics");
      expect(tool.config.title).toBe("Get Phase Analytics");
    });

    it("should register phase_update tool", () => {
      expect(registeredTools.has("phase_update")).toBe(true);
      const tool = registeredTools.get("phase_update");
      expect(tool.config.title).toBe("Update Phase");
    });

    it("should register phase_advance tool", () => {
      expect(registeredTools.has("phase_advance")).toBe(true);
      const tool = registeredTools.get("phase_advance");
      expect(tool.config.title).toBe("Advance Phase");
    });

    it("should register phase_start tool", () => {
      expect(registeredTools.has("phase_start")).toBe(true);
      const tool = registeredTools.get("phase_start");
      expect(tool.config.title).toBe("Start Phase");
    });

    it("should register phase_complete tool", () => {
      expect(registeredTools.has("phase_complete")).toBe(true);
      const tool = registeredTools.get("phase_complete");
      expect(tool.config.title).toBe("Complete Phase");
    });

    it("should register phase_block tool", () => {
      expect(registeredTools.has("phase_block")).toBe(true);
      const tool = registeredTools.get("phase_block");
      expect(tool.config.title).toBe("Block Phase");
    });

    it("should register phase_unblock tool", () => {
      expect(registeredTools.has("phase_unblock")).toBe(true);
      const tool = registeredTools.get("phase_unblock");
      expect(tool.config.title).toBe("Unblock Phase");
    });

    it("should register phase_skip tool", () => {
      expect(registeredTools.has("phase_skip")).toBe(true);
      const tool = registeredTools.get("phase_skip");
      expect(tool.config.title).toBe("Skip Phase");
    });
  });

  describe("phase_get Tool", () => {
    const mockPhasesResponse = {
      entity_id: "task-123",
      entity_type: "task",
      phases: {
        research: { status: "completed", has_research: true },
        planning: { status: "in_progress", has_acceptance_criteria: true },
        implementation: { status: "not_started", progress_pct: 0 },
        testing: { status: "not_started", has_unit_tests: false },
      },
    };

    it("should call backend getPhases with correct parameters", async () => {
      vi.mocked(mockClient.getPhases).mockResolvedValue(mockPhasesResponse);

      const tool = registeredTools.get("phase_get");
      await tool.handler({ entityType: "task", entityId: "task-123" });

      expect(mockClient.getPhases).toHaveBeenCalledWith("task", "task-123");
    });

    it("should return parsed phases response", async () => {
      vi.mocked(mockClient.getPhases).mockResolvedValue(mockPhasesResponse);

      const tool = registeredTools.get("phase_get");
      const result = await tool.handler({
        entityType: "task",
        entityId: "task-123",
      });

      expect(result.content[0].type).toBe("text");
      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.entity_id).toBe("task-123");
      expect(parsed.phases).toHaveProperty("research");
    });
  });

  describe("phase_get_single Tool", () => {
    const mockPhaseResponse = {
      phase_name: "research",
      status: "completed",
      data: { has_research: true, research_adequate: true },
    };

    it("should call backend getPhase with correct parameters", async () => {
      vi.mocked(mockClient.getPhase).mockResolvedValue(mockPhaseResponse);

      const tool = registeredTools.get("phase_get_single");
      await tool.handler({
        entityType: "task",
        entityId: "task-123",
        phaseName: "research",
      });

      expect(mockClient.getPhase).toHaveBeenCalledWith(
        "task",
        "task-123",
        "research"
      );
    });

    it("should return parsed phase response", async () => {
      vi.mocked(mockClient.getPhase).mockResolvedValue(mockPhaseResponse);

      const tool = registeredTools.get("phase_get_single");
      const result = await tool.handler({
        entityType: "task",
        entityId: "task-123",
        phaseName: "research",
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.phase_name).toBe("research");
      expect(parsed.status).toBe("completed");
    });
  });

  describe("phase_summary Tool", () => {
    const mockSummaryResponse = {
      entity_id: "task-123",
      entity_type: "task",
      current_phase: "planning",
      phases_completed: 1,
      phases_total: 4,
      completion_pct: 25,
      phases: {},
    };

    it("should call backend getPhaseSummary with correct parameters", async () => {
      vi.mocked(mockClient.getPhaseSummary).mockResolvedValue(
        mockSummaryResponse
      );

      const tool = registeredTools.get("phase_summary");
      await tool.handler({ entityType: "task", entityId: "task-123" });

      expect(mockClient.getPhaseSummary).toHaveBeenCalledWith(
        "task",
        "task-123"
      );
    });

    it("should return parsed summary with completion metrics", async () => {
      vi.mocked(mockClient.getPhaseSummary).mockResolvedValue(
        mockSummaryResponse
      );

      const tool = registeredTools.get("phase_summary");
      const result = await tool.handler({
        entityType: "task",
        entityId: "task-123",
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.current_phase).toBe("planning");
      expect(parsed.completion_pct).toBe(25);
    });
  });

  describe("phase_analytics Tool", () => {
    const mockAnalyticsResponse = {
      entity_type: "task",
      total_entities: 50,
      by_phase: {
        research: { completed: 20, in_progress: 10, not_started: 20 },
        planning: { completed: 15, in_progress: 5, not_started: 30 },
      },
      blocked_count: 3,
      average_completion_pct: 35.5,
    };

    it("should call backend getPhaseAnalytics with entity type", async () => {
      vi.mocked(mockClient.getPhaseAnalytics).mockResolvedValue(
        mockAnalyticsResponse
      );

      const tool = registeredTools.get("phase_analytics");
      await tool.handler({ entityType: "task" });

      expect(mockClient.getPhaseAnalytics).toHaveBeenCalledWith(
        "task",
        undefined
      );
    });

    it("should pass limit parameter when provided", async () => {
      vi.mocked(mockClient.getPhaseAnalytics).mockResolvedValue(
        mockAnalyticsResponse
      );

      const tool = registeredTools.get("phase_analytics");
      await tool.handler({ entityType: "task", limit: 100 });

      expect(mockClient.getPhaseAnalytics).toHaveBeenCalledWith("task", 100);
    });

    it("should return parsed analytics", async () => {
      vi.mocked(mockClient.getPhaseAnalytics).mockResolvedValue(
        mockAnalyticsResponse
      );

      const tool = registeredTools.get("phase_analytics");
      const result = await tool.handler({ entityType: "task" });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.total_entities).toBe(50);
      expect(parsed.blocked_count).toBe(3);
    });
  });

  describe("phase_update Tool", () => {
    const mockUpdateResponse = {
      entity_id: "task-123",
      entity_type: "task",
      phases: {
        research: { status: "completed" },
      },
    };

    it("should call backend updatePhase with correct parameters", async () => {
      vi.mocked(mockClient.updatePhase).mockResolvedValue(mockUpdateResponse);

      const tool = registeredTools.get("phase_update");
      await tool.handler({
        entityType: "task",
        entityId: "task-123",
        phaseName: "research",
        update: { status: "completed" },
      });

      expect(mockClient.updatePhase).toHaveBeenCalledWith(
        "task",
        "task-123",
        "research",
        { status: "completed" }
      );
    });
  });

  describe("phase_advance Tool", () => {
    const mockAdvanceResponse = {
      entity_id: "task-123",
      entity_type: "task",
      phases: {
        research: { status: "completed" },
        planning: { status: "in_progress" },
      },
    };

    it("should call backend advancePhase", async () => {
      vi.mocked(mockClient.advancePhase).mockResolvedValue(mockAdvanceResponse);

      const tool = registeredTools.get("phase_advance");
      await tool.handler({ entityType: "task", entityId: "task-123" });

      expect(mockClient.advancePhase).toHaveBeenCalledWith("task", "task-123");
    });
  });

  describe("phase_start Tool", () => {
    const mockStartResponse = {
      entity_id: "task-123",
      entity_type: "task",
      phases: {
        research: { status: "in_progress" },
      },
    };

    it("should call backend startPhase", async () => {
      vi.mocked(mockClient.startPhase).mockResolvedValue(mockStartResponse);

      const tool = registeredTools.get("phase_start");
      await tool.handler({
        entityType: "task",
        entityId: "task-123",
        phaseName: "research",
      });

      expect(mockClient.startPhase).toHaveBeenCalledWith(
        "task",
        "task-123",
        "research"
      );
    });
  });

  describe("phase_complete Tool", () => {
    const mockCompleteResponse = {
      entity_id: "task-123",
      entity_type: "task",
      phases: {
        research: { status: "completed" },
      },
    };

    it("should call backend completePhase", async () => {
      vi.mocked(mockClient.completePhase).mockResolvedValue(
        mockCompleteResponse
      );

      const tool = registeredTools.get("phase_complete");
      await tool.handler({
        entityType: "task",
        entityId: "task-123",
        phaseName: "research",
      });

      expect(mockClient.completePhase).toHaveBeenCalledWith(
        "task",
        "task-123",
        "research"
      );
    });
  });

  describe("phase_block Tool", () => {
    const mockBlockResponse = {
      entity_id: "task-123",
      entity_type: "task",
      phases: {
        research: { status: "blocked", blocked_reason: "Waiting for input" },
      },
    };

    it("should call backend blockPhase with reason", async () => {
      vi.mocked(mockClient.blockPhase).mockResolvedValue(mockBlockResponse);

      const tool = registeredTools.get("phase_block");
      await tool.handler({
        entityType: "task",
        entityId: "task-123",
        phaseName: "research",
        blockedReason: "Waiting for input",
      });

      expect(mockClient.blockPhase).toHaveBeenCalledWith(
        "task",
        "task-123",
        "research",
        "Waiting for input"
      );
    });

    it("should call backend blockPhase without reason", async () => {
      vi.mocked(mockClient.blockPhase).mockResolvedValue(mockBlockResponse);

      const tool = registeredTools.get("phase_block");
      await tool.handler({
        entityType: "task",
        entityId: "task-123",
        phaseName: "research",
      });

      expect(mockClient.blockPhase).toHaveBeenCalledWith(
        "task",
        "task-123",
        "research",
        undefined
      );
    });
  });

  describe("phase_unblock Tool", () => {
    const mockUnblockResponse = {
      entity_id: "task-123",
      entity_type: "task",
      phases: {
        research: { status: "in_progress" },
      },
    };

    it("should call backend unblockPhase", async () => {
      vi.mocked(mockClient.unblockPhase).mockResolvedValue(mockUnblockResponse);

      const tool = registeredTools.get("phase_unblock");
      await tool.handler({
        entityType: "task",
        entityId: "task-123",
        phaseName: "research",
      });

      expect(mockClient.unblockPhase).toHaveBeenCalledWith(
        "task",
        "task-123",
        "research"
      );
    });
  });

  describe("phase_skip Tool", () => {
    const mockSkipResponse = {
      entity_id: "task-123",
      entity_type: "task",
      phases: {
        research: { status: "skipped", skip_reason: "Not needed" },
      },
    };

    it("should call backend skipPhase with reason", async () => {
      vi.mocked(mockClient.skipPhase).mockResolvedValue(mockSkipResponse);

      const tool = registeredTools.get("phase_skip");
      await tool.handler({
        entityType: "task",
        entityId: "task-123",
        phaseName: "research",
        skipReason: "Not needed",
      });

      expect(mockClient.skipPhase).toHaveBeenCalledWith(
        "task",
        "task-123",
        "research",
        "Not needed"
      );
    });
  });

  describe("Error Handling", () => {
    it("should propagate errors from backend client", async () => {
      const error = new Error("Backend unavailable");
      vi.mocked(mockClient.getPhases).mockRejectedValue(error);

      const tool = registeredTools.get("phase_get");

      await expect(
        tool.handler({ entityType: "task", entityId: "task-123" })
      ).rejects.toThrow("Backend unavailable");
    });
  });
});

describe("Phase Schemas", () => {
  describe("phaseStatusSchema", () => {
    it("should accept valid status values", () => {
      const validStatuses = [
        "not_started",
        "in_progress",
        "completed",
        "skipped",
        "blocked",
      ];

      for (const status of validStatuses) {
        expect(() => phaseSchemas.phaseStatusSchema.parse(status)).not.toThrow();
      }
    });

    it("should reject invalid status values", () => {
      expect(() => phaseSchemas.phaseStatusSchema.parse("invalid")).toThrow();
    });
  });

  describe("phaseEntityTypeSchema", () => {
    it("should accept valid entity types", () => {
      const validTypes = ["task", "sprint", "project"];

      for (const type of validTypes) {
        expect(() =>
          phaseSchemas.phaseEntityTypeSchema.parse(type)
        ).not.toThrow();
      }
    });

    it("should reject invalid entity types", () => {
      expect(() => phaseSchemas.phaseEntityTypeSchema.parse("epic")).toThrow();
    });
  });

  describe("phaseNameSchema", () => {
    it("should accept valid phase names", () => {
      const validPhases = ["research", "planning", "implementation", "testing"];

      for (const phase of validPhases) {
        expect(() => phaseSchemas.phaseNameSchema.parse(phase)).not.toThrow();
      }
    });

    it("should reject invalid phase names", () => {
      expect(() => phaseSchemas.phaseNameSchema.parse("deployment")).toThrow();
    });
  });

  describe("phasesResponseSchema", () => {
    it("should validate a complete phases response", () => {
      const response = {
        entity_id: "task-123",
        entity_type: "task",
        phases: {
          research: { status: "completed" },
          planning: { status: "in_progress" },
        },
      };

      expect(() =>
        phaseSchemas.phasesResponseSchema.parse(response)
      ).not.toThrow();
    });
  });

  describe("phaseSummaryResponseSchema", () => {
    it("should validate a complete summary response", () => {
      const response = {
        entity_id: "task-123",
        entity_type: "task",
        current_phase: "planning",
        phases_completed: 1,
        phases_total: 4,
        completion_pct: 25,
        phases: {},
      };

      expect(() =>
        phaseSchemas.phaseSummaryResponseSchema.parse(response)
      ).not.toThrow();
    });

    it("should accept null current_phase", () => {
      const response = {
        entity_id: "task-123",
        entity_type: "task",
        current_phase: null,
        phases_completed: 0,
        phases_total: 4,
        completion_pct: 0,
        phases: {},
      };

      expect(() =>
        phaseSchemas.phaseSummaryResponseSchema.parse(response)
      ).not.toThrow();
    });
  });

  describe("phaseAnalyticsResponseSchema", () => {
    it("should validate analytics response", () => {
      const response = {
        entity_type: "task",
        total_entities: 50,
        by_phase: {
          research: { completed: 20, in_progress: 10 },
        },
        blocked_count: 3,
        average_completion_pct: 35.5,
      };

      expect(() =>
        phaseSchemas.phaseAnalyticsResponseSchema.parse(response)
      ).not.toThrow();
    });
  });

  describe("phaseUpdateRequestSchema", () => {
    it("should accept empty update", () => {
      expect(() =>
        phaseSchemas.phaseUpdateRequestSchema.parse({})
      ).not.toThrow();
    });

    it("should accept status update", () => {
      const update = { status: "in_progress" };
      expect(() =>
        phaseSchemas.phaseUpdateRequestSchema.parse(update)
      ).not.toThrow();
    });

    it("should accept blocked_reason", () => {
      const update = { blocked_reason: "Waiting for review" };
      expect(() =>
        phaseSchemas.phaseUpdateRequestSchema.parse(update)
      ).not.toThrow();
    });

    it("should reject blocked_reason over 500 characters", () => {
      const update = { blocked_reason: "x".repeat(501) };
      expect(() =>
        phaseSchemas.phaseUpdateRequestSchema.parse(update)
      ).toThrow();
    });
  });
});
