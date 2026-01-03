/**
 * Timeout Utility - Phase 1.3
 *
 * Enforces timeouts on async operations
 */

import { TimeoutError } from "../core/errors.js";

/**
 * Wrap a promise with a timeout
 *
 * Example:
 * ```typescript
 * const result = await withTimeout(
 *   fetchData(),
 *   5000,
 *   "fetchData"
 * );
 * ```
 */
export async function withTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number,
  operationName: string
): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((_, reject) =>
      setTimeout(
        () => reject(new TimeoutError(operationName, timeoutMs)),
        timeoutMs
      )
    ),
  ]);
}

/**
 * Create a timeout wrapper function
 *
 * Example:
 * ```typescript
 * const fetchWithTimeout = createTimeoutWrapper(5000, "apiCall");
 * const result = await fetchWithTimeout(() => axios.get(url));
 * ```
 */
export function createTimeoutWrapper(timeoutMs: number, operationName: string) {
  return async <T>(fn: () => Promise<T>): Promise<T> => {
    return withTimeout(fn(), timeoutMs, operationName);
  };
}
