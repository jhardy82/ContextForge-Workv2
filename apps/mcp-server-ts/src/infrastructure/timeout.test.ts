/**
 * Timeout Utility Tests
 *
 * Tests for withTimeout and createTimeoutWrapper functions.
 * These utilities enforce timeouts on async operations.
 *
 * @module infrastructure/timeout.test
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { withTimeout, createTimeoutWrapper } from "./timeout.js";
import { TimeoutError } from "../core/errors.js";

describe("timeout utilities", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe("withTimeout", () => {
    it("should resolve when promise completes before timeout", async () => {
      const promise = Promise.resolve("success");
      const result = await withTimeout(promise, 1000, "testOperation");
      expect(result).toBe("success");
    });

    it("should resolve with complex objects", async () => {
      const data = { id: 1, name: "test", nested: { value: true } };
      const promise = Promise.resolve(data);
      const result = await withTimeout(promise, 1000, "fetchData");
      expect(result).toEqual(data);
    });

    it("should reject with TimeoutError when timeout expires", async () => {
      const slowPromise = new Promise<string>((resolve) => {
        setTimeout(() => resolve("too late"), 5000);
      });

      const timeoutPromise = withTimeout(slowPromise, 100, "slowOperation");

      // Advance time past the timeout
      vi.advanceTimersByTime(150);

      await expect(timeoutPromise).rejects.toThrow(TimeoutError);
      await expect(timeoutPromise).rejects.toMatchObject({
        code: "TIMEOUT",
        retryable: true,
        timeoutMs: 100,
      });
    });

    it("should include operation name in TimeoutError message", async () => {
      const slowPromise = new Promise<void>(() => {});

      const timeoutPromise = withTimeout(slowPromise, 50, "myCustomOperation");
      vi.advanceTimersByTime(100);

      try {
        await timeoutPromise;
        expect.fail("Should have thrown");
      } catch (error) {
        expect(error).toBeInstanceOf(TimeoutError);
        expect((error as TimeoutError).message).toContain("myCustomOperation");
        expect((error as TimeoutError).message).toContain("50ms");
      }
    });

    it("should propagate original error if promise rejects before timeout", async () => {
      const originalError = new Error("Original failure");
      const failingPromise = Promise.reject(originalError);

      await expect(
        withTimeout(failingPromise, 1000, "failingOperation")
      ).rejects.toThrow("Original failure");
    });

    it("should work with zero timeout (immediate timeout)", async () => {
      // Zero timeout with a slow promise that uses setTimeout (not setImmediate)
      // setTimeout(fn, 0) and setTimeout(reject, 0) race, but both are 0ms
      // so the timeout should fire since it's registered first in Promise.race
      const promise = new Promise<string>((resolve) => {
        setTimeout(() => resolve("result"), 10); // Give it 10ms delay
      });

      const timeoutPromise = withTimeout(promise, 0, "zeroTimeout");
      vi.advanceTimersByTime(1);

      await expect(timeoutPromise).rejects.toThrow(TimeoutError);
    });

    it("should work with very large timeout values", async () => {
      const promise = Promise.resolve("fast result");
      const result = await withTimeout(promise, Number.MAX_SAFE_INTEGER, "largeTimeout");
      expect(result).toBe("fast result");
    });

    it("should handle null return values", async () => {
      const promise = Promise.resolve(null);
      const result = await withTimeout(promise, 1000, "nullResult");
      expect(result).toBeNull();
    });

    it("should handle undefined return values", async () => {
      const promise = Promise.resolve(undefined);
      const result = await withTimeout(promise, 1000, "undefinedResult");
      expect(result).toBeUndefined();
    });
  });

  describe("createTimeoutWrapper", () => {
    it("should create a reusable timeout wrapper", async () => {
      const wrapper = createTimeoutWrapper(1000, "apiCall");

      const result = await wrapper(() => Promise.resolve("data"));
      expect(result).toBe("data");
    });

    it("should apply timeout to wrapped functions", async () => {
      const wrapper = createTimeoutWrapper(50, "slowApiCall");

      const slowFn = () =>
        new Promise<string>((resolve) => {
          setTimeout(() => resolve("slow data"), 200);
        });

      const promise = wrapper(slowFn);
      vi.advanceTimersByTime(100);

      await expect(promise).rejects.toThrow(TimeoutError);
    });

    it("should preserve function return type", async () => {
      const wrapper = createTimeoutWrapper(1000, "typedCall");

      interface User {
        id: number;
        name: string;
      }

      const fetchUser = (): Promise<User> =>
        Promise.resolve({ id: 1, name: "Test User" });

      const result = await wrapper(fetchUser);
      expect(result.id).toBe(1);
      expect(result.name).toBe("Test User");
    });

    it("should allow multiple calls with same wrapper", async () => {
      const wrapper = createTimeoutWrapper(1000, "multiCall");

      const result1 = await wrapper(() => Promise.resolve("first"));
      const result2 = await wrapper(() => Promise.resolve("second"));
      const result3 = await wrapper(() => Promise.resolve("third"));

      expect(result1).toBe("first");
      expect(result2).toBe("second");
      expect(result3).toBe("third");
    });

    it("should handle async functions with await", async () => {
      const wrapper = createTimeoutWrapper(1000, "asyncFn");

      const asyncFn = async (): Promise<number> => {
        return 42;
      };

      const result = await wrapper(asyncFn);
      expect(result).toBe(42);
    });

    it("should propagate errors from wrapped functions", async () => {
      const wrapper = createTimeoutWrapper(1000, "errorFn");

      const errorFn = async (): Promise<never> => {
        throw new Error("Function error");
      };

      await expect(wrapper(errorFn)).rejects.toThrow("Function error");
    });
  });

  describe("edge cases", () => {
    it("should handle promise that resolves just before timeout", async () => {
      const promise = new Promise<string>((resolve) => {
        setTimeout(() => resolve("just in time"), 99);
      });

      const timeoutPromise = withTimeout(promise, 100, "closeCall");

      // Advance to just before timeout
      vi.advanceTimersByTime(99);

      const result = await timeoutPromise;
      expect(result).toBe("just in time");
    });

    it("should handle concurrent timeout operations", async () => {
      const promise1 = withTimeout(
        new Promise((r) => setTimeout(() => r("a"), 50)),
        200,
        "op1"
      );
      const promise2 = withTimeout(
        new Promise((r) => setTimeout(() => r("b"), 100)),
        200,
        "op2"
      );
      const promise3 = withTimeout(
        new Promise<string>(() => {}),
        75,
        "op3"
      );

      vi.advanceTimersByTime(50);
      const result1 = await promise1;
      expect(result1).toBe("a");

      vi.advanceTimersByTime(25);
      await expect(promise3).rejects.toThrow(TimeoutError);

      vi.advanceTimersByTime(25);
      const result2 = await promise2;
      expect(result2).toBe("b");
    });
  });
});
