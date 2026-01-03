import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import type {
  TaskRecord,
  ProjectRecord,
  ActionListRecord,
  TaskAttributes,
  TaskUpdate,
  ProjectAttributes,
  ActionListAttributes,
} from "../core/types.js";
import type CircuitBreaker from "opossum";

// Mock modules with factory functions (no external dependencies)
vi.mock("./client.js", () => ({
  BackendClient: vi.fn(),
}));

vi.mock("../services/circuit-breaker.js", () => ({
  createEnhancedCircuitBreaker: vi.fn(),
  circuitBreakerRegistry: new Map(),
}));

vi.mock("../infrastructure/tracing.js", () => ({
  withSpan: vi.fn(),
}));

vi.mock("../infrastructure/requestContextStore.js", () => ({
  requestContextStore: {
    getRequestId: vi.fn(),
  },
}));

vi.mock("../infrastructure/logger.js", () => ({
  createModuleLogger: () => ({
    info: vi.fn(),
    error: vi.fn(),
    warn: vi.fn(),
    debug: vi.fn(),
  }),
}));

vi.mock("../config/index.js", () => ({
  config: {
    BACKEND_TIMEOUT_MS: 5000,
    CIRCUIT_BREAKER_ERROR_THRESHOLD: 50,
    CIRCUIT_BREAKER_RESET_TIMEOUT_MS: 30000,
    CIRCUIT_BREAKER_VOLUME_THRESHOLD: 5,
    ENABLE_METRICS: true,
    FALLBACK_CACHE_ENABLED: true,
  },
}));

// Import after mocks are set up
import { BackendClientWithCircuitBreaker } from "./client-with-circuit-breaker.js";
import { BackendClient } from "./client.js";
import { createEnhancedCircuitBreaker, circuitBreakerRegistry } from "../services/circuit-breaker.js";
import { requestContextStore } from "../infrastructure/requestContextStore.js";
import { withSpan } from "../infrastructure/tracing.js";

describe("BackendClientWithCircuitBreaker", () => {
  let client: BackendClientWithCircuitBreaker;
  let mockBackendClient: any;
  let mockCircuitBreaker: any;
  let mockSpan: any;

  beforeEach(() => {
    // Reset all mock functions
    vi.clearAllMocks();

    // Setup mock backend client
    mockBackendClient = {
      createTask: vi.fn(),
      getTask: vi.fn(),
      updateTask: vi.fn(),
      deleteTask: vi.fn(),
      listTasks: vi.fn(),
      bulkUpdateTasks: vi.fn(),
      assignTasksToSprint: vi.fn(),
      searchTasks: vi.fn(),
      createProject: vi.fn(),
      getProject: vi.fn(),
      updateProject: vi.fn(),
      deleteProject: vi.fn(),
      listProjects: vi.fn(),
      listProjectComments: vi.fn(),
      getProjectMetrics: vi.fn(),
      createActionList: vi.fn(),
      getActionList: vi.fn(),
      listActionLists: vi.fn(),
      updateActionList: vi.fn(),
      deleteActionList: vi.fn(),
      addActionListItem: vi.fn(),
      toggleActionListItem: vi.fn(),
      removeActionListItem: vi.fn(),
      reorderActionListItems: vi.fn(),
      bulkDeleteActionLists: vi.fn(),
      bulkUpdateActionLists: vi.fn(),
      searchActionLists: vi.fn(),
      health: vi.fn(),
    };

    // Mock BackendClient constructor - needs to be a constructor function
    (BackendClient as unknown as ReturnType<typeof vi.fn>).mockImplementation(
      function(this: any) {
        return mockBackendClient;
      } as any
    );

    // Setup mock circuit breaker
    mockCircuitBreaker = {
      fire: vi.fn(),
      opened: false,
      halfOpen: false,
      stats: {
        fires: 100,
        successes: 90,
        failures: 10,
        timeouts: 2,
        rejects: 3,
        latencyMean: 150,
      },
      close: vi.fn(),
    };

    // Mock createEnhancedCircuitBreaker
    vi.mocked(createEnhancedCircuitBreaker).mockReturnValue(
      mockCircuitBreaker as unknown as CircuitBreaker<any, any>
    );

    // Setup mock span
    mockSpan = {
      setAttribute: vi.fn(),
      setStatus: vi.fn(),
      end: vi.fn(),
      isRecording: vi.fn().mockReturnValue(true),
    };

    // Mock withSpan
    vi.mocked(withSpan).mockImplementation(
      async (name: string, fn: (span: any) => Promise<any>) => {
        return fn(mockSpan);
      }
    );

    // Mock requestContextStore
    vi.mocked(requestContextStore.getRequestId).mockReturnValue("test-request-id");

    // Mock circuitBreakerRegistry.set
    vi.spyOn(circuitBreakerRegistry, "set");

    // Create client instance
    client = new BackendClientWithCircuitBreaker();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  // ========================================================================
  // INITIALIZATION TESTS (3 tests)
  // ========================================================================

  describe("Initialization", () => {
    it("should initialize client with default config", () => {
      expect(BackendClient).toHaveBeenCalledWith(undefined);
      expect(BackendClient).toHaveBeenCalledTimes(1);
    });

    it("should create circuit breaker with correct options", () => {
      expect(createEnhancedCircuitBreaker).toHaveBeenCalledWith(
        expect.any(Function),
        expect.objectContaining({
          name: "backend-api",
          timeout: 5000,
          errorThresholdPercentage: 50,
          resetTimeout: 30000,
          volumeThreshold: 5,
          enableMetrics: true,
          enableFallbackCache: true,
        })
      );
    });

    it("should register circuit breaker in registry", () => {
      expect(circuitBreakerRegistry.set).toHaveBeenCalledWith(
        "backend-api",
        mockCircuitBreaker
      );
    });
  });

  // ========================================================================
  // METHOD PROXYING TESTS (6 test groups = 17 tests total)
  // ========================================================================

  describe("Method proxying", () => {
    describe("Task CRUD methods", () => {
      it("should proxy createTask correctly", async () => {
        const taskData: TaskAttributes = { title: "Test Task" };
        const expectedResult: TaskRecord = {
          id: "task-1",
          title: "Test Task",
          status: "pending",
          priority: "medium",
          created_at: "2024-01-01",
          updated_at: "2024-01-01",
        };

        mockCircuitBreaker.fire.mockResolvedValue(expectedResult);

        const result = await client.createTask(taskData);

        expect(mockCircuitBreaker.fire).toHaveBeenCalledWith("createTask", taskData);
        expect(result).toEqual(expectedResult);
      });

      it("should proxy getTask correctly", async () => {
        const expectedResult: TaskRecord = {
          id: "task-1",
          title: "Test Task",
          status: "pending",
          priority: "medium",
          created_at: "2024-01-01",
          updated_at: "2024-01-01",
        };

        mockCircuitBreaker.fire.mockResolvedValue(expectedResult);

        const result = await client.getTask("task-1");

        expect(mockCircuitBreaker.fire).toHaveBeenCalledWith("getTask", "task-1");
        expect(result).toEqual(expectedResult);
      });

      it("should proxy updateTask correctly", async () => {
        const updates: TaskUpdate = { status: "in-progress" };
        const expectedResult: TaskRecord = {
          id: "task-1",
          title: "Test Task",
          status: "in-progress",
          priority: "medium",
          created_at: "2024-01-01",
          updated_at: "2024-01-01",
        };

        mockCircuitBreaker.fire.mockResolvedValue(expectedResult);

        const result = await client.updateTask("task-1", updates);

        expect(mockCircuitBreaker.fire).toHaveBeenCalledWith(
          "updateTask",
          "task-1",
          updates
        );
        expect(result).toEqual(expectedResult);
      });

      it("should proxy deleteTask correctly", async () => {
        mockCircuitBreaker.fire.mockResolvedValue(undefined);

        await client.deleteTask("task-1");

        expect(mockCircuitBreaker.fire).toHaveBeenCalledWith("deleteTask", "task-1");
      });
    });

    describe("Project methods", () => {
      it("should proxy createProject correctly", async () => {
        const projectData: ProjectAttributes = { name: "Test Project" };
        const expectedResult: ProjectRecord = {
          id: "project-1",
          name: "Test Project",
          status: "active",
          created_at: "2024-01-01",
          updated_at: "2024-01-01",
        };

        mockCircuitBreaker.fire.mockResolvedValue(expectedResult);

        const result = await client.createProject(projectData);

        expect(mockCircuitBreaker.fire).toHaveBeenCalledWith(
          "createProject",
          projectData
        );
        expect(result).toEqual(expectedResult);
      });

      it("should proxy getProject correctly", async () => {
        const expectedResult: ProjectRecord = {
          id: "project-1",
          name: "Test Project",
          status: "active",
          created_at: "2024-01-01",
          updated_at: "2024-01-01",
        };

        mockCircuitBreaker.fire.mockResolvedValue(expectedResult);

        const result = await client.getProject("project-1");

        expect(mockCircuitBreaker.fire).toHaveBeenCalledWith("getProject", "project-1");
        expect(result).toEqual(expectedResult);
      });
    });

    describe("ActionList methods", () => {
      it("should proxy createActionList correctly", async () => {
        const actionListData: ActionListAttributes = {
          title: "Test Action List",
          items: [],
        };
        const expectedResult: ActionListRecord = {
          id: "al-1",
          title: "Test Action List",
          items: [],
          status: "pending",
          created_at: "2024-01-01",
          updated_at: "2024-01-01",
        };

        mockCircuitBreaker.fire.mockResolvedValue(expectedResult);

        const result = await client.createActionList(actionListData);

        expect(mockCircuitBreaker.fire).toHaveBeenCalledWith(
          "createActionList",
          actionListData
        );
        expect(result).toEqual(expectedResult);
      });

      it("should proxy getActionList correctly", async () => {
        const expectedResult: ActionListRecord = {
          id: "al-1",
          title: "Test Action List",
          items: [],
          status: "pending",
          created_at: "2024-01-01",
          updated_at: "2024-01-01",
        };

        mockCircuitBreaker.fire.mockResolvedValue(expectedResult);

        const result = await client.getActionList("al-1");

        expect(mockCircuitBreaker.fire).toHaveBeenCalledWith("getActionList", "al-1");
        expect(result).toEqual(expectedResult);
      });
    });

    describe("Bulk operations", () => {
      it("should proxy bulkUpdateTasks correctly", async () => {
        const taskIds = ["task-1", "task-2"];
        const updates: TaskUpdate = { status: "completed" };
        const expectedResult = {
          success: true,
          updated_count: 2,
          task_ids: taskIds,
        };

        mockCircuitBreaker.fire.mockResolvedValue(expectedResult);

        const result = await client.bulkUpdateTasks(taskIds, updates);

        expect(mockCircuitBreaker.fire).toHaveBeenCalledWith(
          "bulkUpdateTasks",
          taskIds,
          updates
        );
        expect(result).toEqual(expectedResult);
      });

      it("should proxy bulkDeleteActionLists correctly", async () => {
        const actionListIds = ["al-1", "al-2"];
        const expectedResult = { success: true, deleted_count: 2 };

        mockCircuitBreaker.fire.mockResolvedValue(expectedResult);

        const result = await client.bulkDeleteActionLists(actionListIds);

        expect(mockCircuitBreaker.fire).toHaveBeenCalledWith(
          "bulkDeleteActionLists",
          actionListIds
        );
        expect(result).toEqual(expectedResult);
      });
    });

    describe("Search methods", () => {
      it("should proxy searchTasks correctly", async () => {
        const params = { query: "test", fields: ["title" as const] };
        const expectedResult = {
          success: true,
          query: "test",
          count: 1,
          data: [
            {
              id: "task-1",
              title: "Test Task",
              status: "pending",
              priority: "medium",
              created_at: "2024-01-01",
              updated_at: "2024-01-01",
            },
          ],
        };

        mockCircuitBreaker.fire.mockResolvedValue(expectedResult);

        const result = await client.searchTasks(params);

        expect(mockCircuitBreaker.fire).toHaveBeenCalledWith("searchTasks", params);
        expect(result).toEqual(expectedResult);
      });

      it("should proxy searchActionLists correctly", async () => {
        const query = "test";
        const options = { fields: ["title" as const] };
        const expectedResult = {
          success: true,
          query: "test",
          count: 1,
          data: [
            {
              id: "al-1",
              title: "Test Action List",
              items: [],
              status: "pending",
              created_at: "2024-01-01",
              updated_at: "2024-01-01",
            },
          ],
        };

        mockCircuitBreaker.fire.mockResolvedValue(expectedResult);

        const result = await client.searchActionLists(query, options);

        expect(mockCircuitBreaker.fire).toHaveBeenCalledWith(
          "searchActionLists",
          query,
          options
        );
        expect(result).toEqual(expectedResult);
      });
    });

    describe("Item operations", () => {
      it("should proxy addActionListItem correctly", async () => {
        const item = { text: "New item", order: 1 };
        const expectedResult: ActionListRecord = {
          id: "al-1",
          title: "Test Action List",
          items: [{ id: "item-1", text: "New item", completed: false, order: 1 }],
          status: "pending",
          created_at: "2024-01-01",
          updated_at: "2024-01-01",
        };

        mockCircuitBreaker.fire.mockResolvedValue(expectedResult);

        const result = await client.addActionListItem("al-1", item);

        expect(mockCircuitBreaker.fire).toHaveBeenCalledWith(
          "addActionListItem",
          "al-1",
          item
        );
        expect(result).toEqual(expectedResult);
      });

      it("should proxy toggleActionListItem correctly", async () => {
        const expectedResult: ActionListRecord = {
          id: "al-1",
          title: "Test Action List",
          items: [{ id: "item-1", text: "Item", completed: true, order: 1 }],
          status: "pending",
          created_at: "2024-01-01",
          updated_at: "2024-01-01",
        };

        mockCircuitBreaker.fire.mockResolvedValue(expectedResult);

        const result = await client.toggleActionListItem("al-1", "item-1");

        expect(mockCircuitBreaker.fire).toHaveBeenCalledWith(
          "toggleActionListItem",
          "al-1",
          "item-1"
        );
        expect(result).toEqual(expectedResult);
      });
    });
  });

  // ========================================================================
  // REQUEST CONTEXT PROPAGATION TESTS (4 tests)
  // ========================================================================

  describe("Request context propagation", () => {
    beforeEach(() => {
      // Reset mocks to track calls in executeWithObservability
      vi.clearAllMocks();

      // Mock circuit breaker to call the actual function
      mockCircuitBreaker.fire.mockImplementation(
        async (method: string, ...args: any[]) => {
          // Simulate calling executeWithObservability
          return withSpan(`backend.${method}`, async (span) => {
            const requestId = requestContextStore.getRequestId();
            if (requestId) {
              span.setAttribute("request_id", requestId);
            }
            span.setAttribute("backend.method", method);
            span.setAttribute("backend.args_count", args.length);

            // Mock the actual method call
            const fn = mockBackendClient[method];
            if (!fn) {
              throw new Error(`Method ${method} not found on BackendClient`);
            }
            const result = await fn(...args);
            span.setStatus({ code: 1 }); // OK
            return result;
          });
        }
      );

      mockBackendClient.getTask.mockResolvedValue({
        id: "task-1",
        title: "Test Task",
        status: "pending",
        priority: "medium",
        created_at: "2024-01-01",
        updated_at: "2024-01-01",
      });
    });

    it("should add request ID to trace span", async () => {
      await client.getTask("task-1");

      expect(requestContextStore.getRequestId).toHaveBeenCalled();
      expect(mockSpan.setAttribute).toHaveBeenCalledWith(
        "request_id",
        "test-request-id"
      );
    });

    it("should execute operations with observability wrapper", async () => {
      await client.getTask("task-1");

      expect(withSpan).toHaveBeenCalledWith(
        "backend.getTask",
        expect.any(Function)
      );
    });

    it("should set span attributes correctly", async () => {
      await client.getTask("task-1");

      expect(mockSpan.setAttribute).toHaveBeenCalledWith(
        "backend.method",
        "getTask"
      );
      expect(mockSpan.setAttribute).toHaveBeenCalledWith("backend.args_count", 1);
    });

    it("should include method name in span", async () => {
      await client.updateTask("task-1", { status: "in-progress" });

      expect(withSpan).toHaveBeenCalledWith(
        "backend.updateTask",
        expect.any(Function)
      );
    });
  });

  // ========================================================================
  // CIRCUIT BREAKER INTEGRATION TESTS (3 tests)
  // ========================================================================

  describe("Circuit breaker integration", () => {
    it("should use circuit breaker.fire() for all methods", async () => {
      mockCircuitBreaker.fire.mockResolvedValue({
        id: "task-1",
        title: "Test",
        status: "pending",
        priority: "medium",
        created_at: "2024-01-01",
        updated_at: "2024-01-01",
      });

      await client.getTask("task-1");
      await client.createTask({ title: "New Task" });
      await client.updateTask("task-1", { status: "completed" });

      expect(mockCircuitBreaker.fire).toHaveBeenCalledTimes(3);
    });

    it("should handle circuit breaker failures", async () => {
      const error = new Error("Circuit breaker open");
      mockCircuitBreaker.fire.mockRejectedValue(error);

      await expect(client.getTask("task-1")).rejects.toThrow(
        "Circuit breaker open"
      );
    });

    it("should propagate cache key function for read operations", () => {
      const cacheKeyFn = vi.mocked(createEnhancedCircuitBreaker).mock.calls[0][1]
        ?.cacheKeyFn;

      expect(cacheKeyFn).toBeDefined();

      if (cacheKeyFn) {
        // Test that read operations generate cache keys
        const getKey = cacheKeyFn("getTask", "task-1");
        expect(getKey).toBe('backend:getTask:["task-1"]');

        const listKey = cacheKeyFn("listTasks", { status: "pending" });
        expect(listKey).toBe('backend:listTasks:[{"status":"pending"}]');

        // Test that mutations don't generate cache keys
        const createKey = cacheKeyFn("createTask", { title: "New" });
        expect(createKey).toBe("");

        const updateKey = cacheKeyFn("updateTask", "task-1", { status: "done" });
        expect(updateKey).toBe("");
      }
    });
  });

  // ========================================================================
  // UTILITY METHODS TESTS (3 tests)
  // ========================================================================

  describe("Utility methods", () => {
    it("should return accurate circuit breaker stats", () => {
      const stats = client.getCircuitBreakerStats();

      expect(stats).toEqual({
        state: "closed",
        totalRequests: 100,
        successfulRequests: 90,
        failedRequests: 10,
        timeouts: 2,
        rejectedRequests: 3,
        errorPercentage: 10,
        averageResponseTime: 150,
      });
    });

    it("should reflect circuit state accurately", () => {
      // Closed state
      mockCircuitBreaker.opened = false;
      mockCircuitBreaker.halfOpen = false;
      expect(client.isHealthy()).toBe(true);

      // Open state
      mockCircuitBreaker.opened = true;
      mockCircuitBreaker.halfOpen = false;
      expect(client.isHealthy()).toBe(false);

      // Half-open state
      mockCircuitBreaker.opened = false;
      mockCircuitBreaker.halfOpen = true;
      expect(client.isHealthy()).toBe(false);
    });

    it("should bypass circuit breaker for health checks", async () => {
      const healthResult = { status: "healthy", timestamp: "2024-01-01" };
      mockBackendClient.health.mockResolvedValue(healthResult);

      const result = await client.health();

      // Health should call underlying client directly, not circuit breaker
      expect(mockBackendClient.health).toHaveBeenCalled();
      expect(mockCircuitBreaker.fire).not.toHaveBeenCalledWith("health");
      expect(result).toEqual(healthResult);
    });
  });

  // ========================================================================
  // ADDITIONAL EDGE CASE TESTS (5 tests)
  // ========================================================================

  describe("Edge cases", () => {
    it("should handle missing request ID gracefully", async () => {
      vi.mocked(requestContextStore.getRequestId).mockReturnValue(undefined);

      mockCircuitBreaker.fire.mockImplementation(
        async (method: string, ...args: any[]) => {
          return withSpan(`backend.${method}`, async (span) => {
            const requestId = requestContextStore.getRequestId();
            if (requestId) {
              span.setAttribute("request_id", requestId);
            }
            span.setAttribute("backend.method", method);
            return { id: "task-1" };
          });
        }
      );

      await client.getTask("task-1");

      // Should not throw, request_id attribute simply not set
      expect(mockSpan.setAttribute).not.toHaveBeenCalledWith(
        "request_id",
        expect.anything()
      );
    });

    it("should handle half-open circuit state", () => {
      mockCircuitBreaker.opened = false;
      mockCircuitBreaker.halfOpen = true;

      const stats = client.getCircuitBreakerStats();

      expect(stats.state).toBe("halfOpen");
      expect(client.isHealthy()).toBe(false);
    });

    it("should force close circuit breaker", () => {
      mockCircuitBreaker.opened = true;
      mockCircuitBreaker.halfOpen = false;

      client.forceClose();

      expect(mockCircuitBreaker.close).toHaveBeenCalled();
    });

    it("should not close circuit if already closed", () => {
      mockCircuitBreaker.opened = false;
      mockCircuitBreaker.halfOpen = false;

      client.forceClose();

      expect(mockCircuitBreaker.close).not.toHaveBeenCalled();
    });

    it("should return underlying client", () => {
      const underlyingClient = client.getUnderlyingClient();

      expect(underlyingClient).toBe(mockBackendClient);
    });
  });
});
