/**
 * Vitest Setup File
 *
 * This file runs before all tests to configure the test environment.
 * It sets up environment variables and global configuration needed
 * for the pino logger and other infrastructure to work correctly in tests.
 *
 * @see https://vitest.dev/config/#setupfiles
 */

// Set NODE_ENV to test to enable test-specific behavior
process.env.NODE_ENV = "test";

// Set log level to error for tests to reduce noise while passing config validation
// Note: "silent" is not a valid config schema value - only trace/debug/info/warn/error/fatal
process.env.LOG_LEVEL = "error";

// Disable pino-pretty transport in tests to avoid configuration issues
// The logger checks NODE_ENV !== "production" for pretty printing,
// but "test" will trigger the same code path. We'll handle this in logger.ts
process.env.PINO_PRETTY = "false";

/**
 * TODO: If pino logger issues persist, consider:
 * 1. Update logger.ts to check for NODE_ENV === "test" and use simple configuration
 * 2. Create a stub logger implementation for tests
 * 3. Export a test-friendly logger factory
 */
