import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import {
  requestContextStore,
  RequestContextStore,
  type RequestContext,
} from "./requestContextStore.js";
import type { Logger } from "pino";

describe("RequestContextStore", () => {
  describe("Context initialization", () => {
    it("should generate requestId when not provided", () => {
      requestContextStore.runWithContext({}, () => {
        const requestId = requestContextStore.getRequestId();
        expect(requestId).toBeDefined();
        expect(requestId).toMatch(/^req-[a-f0-9-]+$/);
      });
    });

    it("should preserve provided requestId", () => {
      const customRequestId = "custom-req-123";

      requestContextStore.runWithContext(
        { requestId: customRequestId },
        () => {
          const requestId = requestContextStore.getRequestId();
          expect(requestId).toBe(customRequestId);
        }
      );
    });

    it("should set startTime automatically", () => {
      const beforeTime = Date.now();

      requestContextStore.runWithContext({}, () => {
        const context = requestContextStore.getContext();
        expect(context?.startTime).toBeDefined();
        expect(context?.startTime).toBeGreaterThanOrEqual(beforeTime);
        expect(context?.startTime).toBeLessThanOrEqual(Date.now());
      });
    });

    it("should preserve provided startTime", () => {
      const customStartTime = 1234567890000;

      requestContextStore.runWithContext({ startTime: customStartTime }, () => {
        const context = requestContextStore.getContext();
        expect(context?.startTime).toBe(customStartTime);
      });
    });
  });

  describe("Context retrieval", () => {
    it("should return full context object", () => {
      const correlationId = "trace-xyz-789";

      requestContextStore.runWithContext({ correlationId }, () => {
        const context = requestContextStore.getContext();

        expect(context).toBeDefined();
        expect(context?.requestId).toBeDefined();
        expect(context?.correlationId).toBe(correlationId);
        expect(context?.startTime).toBeDefined();
        expect(context?.metadata).toBeDefined();
      });
    });

    it("should return requestId from context", () => {
      const customRequestId = "req-test-456";

      requestContextStore.runWithContext(
        { requestId: customRequestId },
        () => {
          const requestId = requestContextStore.getRequestId();
          expect(requestId).toBe(customRequestId);
        }
      );
    });

    it("should return correlationId when present", () => {
      const correlationId = "correlation-abc-123";

      requestContextStore.runWithContext({ correlationId }, () => {
        const returnedCorrelationId = requestContextStore.getCorrelationId();
        expect(returnedCorrelationId).toBe(correlationId);
      });
    });

    it("should return undefined for correlationId when not set", () => {
      requestContextStore.runWithContext({}, () => {
        const correlationId = requestContextStore.getCorrelationId();
        expect(correlationId).toBeUndefined();
      });
    });
  });

  describe("Context isolation", () => {
    it("should maintain separate requestIds in nested contexts", () => {
      const outerRequestId = "outer-req-123";
      const innerRequestId = "inner-req-456";

      requestContextStore.runWithContext({ requestId: outerRequestId }, () => {
        const outerReqId = requestContextStore.getRequestId();
        expect(outerReqId).toBe(outerRequestId);

        requestContextStore.runWithContext(
          { requestId: innerRequestId },
          () => {
            const innerReqId = requestContextStore.getRequestId();
            expect(innerReqId).toBe(innerRequestId);
          }
        );

        // After inner context completes, outer context is restored
        const restoredOuterReqId = requestContextStore.getRequestId();
        expect(restoredOuterReqId).toBe(outerRequestId);
      });
    });

    it("should not interfere with concurrent async operations", async () => {
      const results: string[] = [];

      const operation1 = requestContextStore.runWithContextAsync(
        { requestId: "req-1" },
        async () => {
          await new Promise((resolve) => setTimeout(resolve, 10));
          const id = requestContextStore.getRequestId();
          results.push(id!);
          return id;
        }
      );

      const operation2 = requestContextStore.runWithContextAsync(
        { requestId: "req-2" },
        async () => {
          await new Promise((resolve) => setTimeout(resolve, 5));
          const id = requestContextStore.getRequestId();
          results.push(id!);
          return id;
        }
      );

      const operation3 = requestContextStore.runWithContextAsync(
        { requestId: "req-3" },
        async () => {
          await new Promise((resolve) => setTimeout(resolve, 15));
          const id = requestContextStore.getRequestId();
          results.push(id!);
          return id;
        }
      );

      const [result1, result2, result3] = await Promise.all([
        operation1,
        operation2,
        operation3,
      ]);

      expect(result1).toBe("req-1");
      expect(result2).toBe("req-2");
      expect(result3).toBe("req-3");
      expect(results).toContain("req-1");
      expect(results).toContain("req-2");
      expect(results).toContain("req-3");
    });

    it("should return undefined outside runWithContext", () => {
      const context = requestContextStore.getContext();
      expect(context).toBeUndefined();

      const requestId = requestContextStore.getRequestId();
      expect(requestId).toBeUndefined();

      const correlationId = requestContextStore.getCorrelationId();
      expect(correlationId).toBeUndefined();
    });

    it("should clear context after function completes", () => {
      let contextDuringExecution: RequestContext | undefined;

      requestContextStore.runWithContext({ requestId: "req-temp" }, () => {
        contextDuringExecution = requestContextStore.getContext();
      });

      // Context should exist during execution
      expect(contextDuringExecution).toBeDefined();
      expect(contextDuringExecution?.requestId).toBe("req-temp");

      // Context should be cleared after execution
      const contextAfterExecution = requestContextStore.getContext();
      expect(contextAfterExecution).toBeUndefined();
    });
  });

  describe("Metadata management", () => {
    it("should merge metadata with existing metadata", () => {
      requestContextStore.runWithContext(
        { metadata: { initial: "value1" } },
        () => {
          const context1 = requestContextStore.getContext();
          expect(context1?.metadata).toEqual({ initial: "value1" });

          requestContextStore.updateMetadata({ added: "value2" });

          const context2 = requestContextStore.getContext();
          expect(context2?.metadata).toEqual({
            initial: "value1",
            added: "value2",
          });

          requestContextStore.updateMetadata({ another: "value3" });

          const context3 = requestContextStore.getContext();
          expect(context3?.metadata).toEqual({
            initial: "value1",
            added: "value2",
            another: "value3",
          });
        }
      );
    });

    it("should work when no prior metadata exists", () => {
      requestContextStore.runWithContext({}, () => {
        const context1 = requestContextStore.getContext();
        expect(context1?.metadata).toEqual({});

        requestContextStore.updateMetadata({ key: "value" });

        const context2 = requestContextStore.getContext();
        expect(context2?.metadata).toEqual({ key: "value" });
      });
    });

    it("should not throw error when updating metadata outside context", () => {
      expect(() => {
        requestContextStore.updateMetadata({ test: "value" });
      }).not.toThrow();
    });
  });

  describe("Logger integration", () => {
    it("should create child logger with requestId", () => {
      const mockBaseLogger = {
        child: vi.fn(() => mockBaseLogger),
      } as unknown as Logger;

      requestContextStore.runWithContext({ requestId: "req-logger-1" }, () => {
        const childLogger = requestContextStore.withRequestLogger(
          mockBaseLogger
        );

        expect(mockBaseLogger.child).toHaveBeenCalledWith({
          requestId: "req-logger-1",
        });
      });
    });

    it("should include correlationId in logger when present", () => {
      const mockBaseLogger = {
        child: vi.fn(() => mockBaseLogger),
      } as unknown as Logger;

      requestContextStore.runWithContext(
        {
          requestId: "req-logger-2",
          correlationId: "correlation-xyz",
        },
        () => {
          const childLogger = requestContextStore.withRequestLogger(
            mockBaseLogger
          );

          expect(mockBaseLogger.child).toHaveBeenCalledWith({
            requestId: "req-logger-2",
            correlationId: "correlation-xyz",
          });
        }
      );
    });

    it("should return base logger when no context exists", () => {
      const mockBaseLogger = {
        child: vi.fn(() => mockBaseLogger),
      } as unknown as Logger;

      const returnedLogger = requestContextStore.withRequestLogger(
        mockBaseLogger
      );

      expect(returnedLogger).toBe(mockBaseLogger);
      expect(mockBaseLogger.child).not.toHaveBeenCalled();
    });
  });

  describe("Additional utility methods", () => {
    it("should return correct request duration", () => {
      vi.useFakeTimers();

      requestContextStore.runWithContext({}, () => {
        const duration1 = requestContextStore.getRequestDuration();
        expect(duration1).toBe(0);

        vi.advanceTimersByTime(1000);

        const duration2 = requestContextStore.getRequestDuration();
        expect(duration2).toBeGreaterThanOrEqual(1000);

        vi.advanceTimersByTime(500);

        const duration3 = requestContextStore.getRequestDuration();
        expect(duration3).toBeGreaterThanOrEqual(1500);
      });

      vi.useRealTimers();
    });

    it("should return undefined duration when outside context", () => {
      const duration = requestContextStore.getRequestDuration();
      expect(duration).toBeUndefined();
    });

    it("should correctly report hasContext", () => {
      expect(requestContextStore.hasContext()).toBe(false);

      requestContextStore.runWithContext({}, () => {
        expect(requestContextStore.hasContext()).toBe(true);
      });

      expect(requestContextStore.hasContext()).toBe(false);
    });

    it("should return context stats correctly", () => {
      vi.useFakeTimers();

      const stats1 = requestContextStore.getContextStats();
      expect(stats1).toBeNull();

      requestContextStore.runWithContext(
        {
          requestId: "req-stats",
          correlationId: "corr-stats",
          metadata: { key1: "value1", key2: "value2" },
        },
        () => {
          vi.advanceTimersByTime(2000);

          const stats = requestContextStore.getContextStats();
          expect(stats).not.toBeNull();
          expect(stats?.requestId).toBe("req-stats");
          expect(stats?.correlationId).toBe("corr-stats");
          expect(stats?.durationMs).toBeGreaterThanOrEqual(2000);
          expect(stats?.hasMetadata).toBe(true);
          expect(stats?.metadataKeys).toEqual(["key1", "key2"]);
        }
      );

      vi.useRealTimers();
    });

    it("should handle async context correctly", async () => {
      const result = await requestContextStore.runWithContextAsync(
        { requestId: "async-req" },
        async () => {
          await new Promise((resolve) => setTimeout(resolve, 10));

          const requestId = requestContextStore.getRequestId();
          expect(requestId).toBe("async-req");

          return "async-result";
        }
      );

      expect(result).toBe("async-result");

      // Context should be cleared after async execution
      const contextAfter = requestContextStore.getContext();
      expect(contextAfter).toBeUndefined();
    });

    it("should handle errors in async context", async () => {
      await expect(
        requestContextStore.runWithContextAsync(
          { requestId: "error-req" },
          async () => {
            throw new Error("Test error");
          }
        )
      ).rejects.toThrow("Test error");

      // Context should still be cleared after error
      const contextAfter = requestContextStore.getContext();
      expect(contextAfter).toBeUndefined();
    });
  });

  describe("Edge cases and robustness", () => {
    it("should handle empty metadata object", () => {
      requestContextStore.runWithContext({ metadata: {} }, () => {
        const context = requestContextStore.getContext();
        expect(context?.metadata).toEqual({});
      });
    });

    it("should handle context with all optional fields", () => {
      const fullContext = {
        requestId: "full-req",
        correlationId: "full-corr",
        startTime: 1234567890000,
        metadata: { key: "value" },
      };

      requestContextStore.runWithContext(fullContext, () => {
        const context = requestContextStore.getContext();
        expect(context?.requestId).toBe("full-req");
        expect(context?.correlationId).toBe("full-corr");
        expect(context?.startTime).toBe(1234567890000);
        expect(context?.metadata).toEqual({ key: "value" });
      });
    });

    it("should handle deep nesting of contexts", () => {
      requestContextStore.runWithContext({ requestId: "level-1" }, () => {
        expect(requestContextStore.getRequestId()).toBe("level-1");

        requestContextStore.runWithContext({ requestId: "level-2" }, () => {
          expect(requestContextStore.getRequestId()).toBe("level-2");

          requestContextStore.runWithContext({ requestId: "level-3" }, () => {
            expect(requestContextStore.getRequestId()).toBe("level-3");
          });

          expect(requestContextStore.getRequestId()).toBe("level-2");
        });

        expect(requestContextStore.getRequestId()).toBe("level-1");
      });
    });

    it("should handle return values from runWithContext", () => {
      const result = requestContextStore.runWithContext(
        { requestId: "return-test" },
        () => {
          return { value: 42, message: "success" };
        }
      );

      expect(result).toEqual({ value: 42, message: "success" });
    });
  });
});
