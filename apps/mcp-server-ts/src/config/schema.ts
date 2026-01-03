/**
 * Configuration Schema - Comprehensive environment variable validation using Zod
 *
 * Features:
 * - Zod schema validation with type inference
 * - Type-safe configuration object
 * - Validation at startup with detailed error messages
 * - Default values for all optional fields
 * - URL and port validation
 *
 * Migration from Joi: This module has been migrated to Zod for better TypeScript
 * integration, improved type inference, and consistency with modern TypeScript practices.
 */

import { z } from "zod";

/**
 * Helper function for boolean environment variables
 *
 * Zod's native { coerce: true } converts ANY non-empty string to true,
 * including "false" and "0". This helper correctly parses boolean strings.
 */
const booleanFromEnv = () =>
  z.preprocess((val) => {
    if (typeof val === "string") {
      return val.toLowerCase() === "true" || val === "1";
    }
    return val;
  }, z.boolean());

/**
 * Environment variable schema with comprehensive validation
 *
 * All fields include:
 * - Type validation
 * - Range/pattern constraints
 * - Default values
 * - Descriptive error messages
 */
const configSchemaInternal = z.object({
  // ============================================================================
  // ENVIRONMENT
  // ============================================================================

  NODE_ENV: z
    .enum(["development", "test", "production"])
    .default("development")
    .describe("Application environment"),

  // ============================================================================
  // SERVER CONFIGURATION
  // ============================================================================

  PORT: z
    .number({ coerce: true })
    .int()
    .min(1)
    .max(65535)
    .default(3000)
    .describe("HTTP server port for health checks and metrics"),

  TASKMAN_MCP_TRANSPORT: z
    .enum(["stdio", "http"])
    .default("stdio")
    .describe("MCP transport protocol (stdio for CLI, http for web)"),

  // ============================================================================
  // BACKEND API CONFIGURATION
  // ============================================================================

  TASK_MANAGER_API_ENDPOINT: z
    .string()
    .url()
    .default("http://localhost:3001/api/v1")
    .describe(
      "Backend REST API base URL (CORRECTED: 3001 match Docker Compose)"
    ),

  BACKEND_TIMEOUT_MS: z
    .number({ coerce: true })
    .int()
    .positive()
    .default(30000)
    .describe("Backend request timeout in milliseconds"),

  BACKEND_MAX_RETRIES: z
    .number({ coerce: true })
    .int()
    .min(0)
    .max(10)
    .default(3)
    .describe("Maximum retry attempts for failed backend requests"),

  BACKEND_RETRY_DELAY_MS: z
    .number({ coerce: true })
    .int()
    .positive()
    .default(1000)
    .describe("Initial retry delay in milliseconds (exponential backoff)"),

  // ============================================================================
  // LOGGING CONFIGURATION
  // ============================================================================

  LOG_LEVEL: z
    .preprocess(
      (val) => (typeof val === "string" ? val.toLowerCase() : val),
      z.enum(["trace", "debug", "info", "warn", "error", "fatal"])
    )
    .default("info")
    .describe("Minimum log level to output"),

  LOG_FORMAT: z
    .enum(["json", "pretty"])
    .default("json")
    .describe(
      "Log output format (json for production, pretty for development)"
    ),

  // ============================================================================
  // PERSISTENCE CONFIGURATION
  // ============================================================================

  ENABLE_PERSISTENCE: booleanFromEnv()
    .default(false)
    .describe("Enable persistent state storage (future enhancement)"),

  PERSISTENCE_TYPE: z
    .enum(["sqlite", "redis", "memory"])
    .default("memory")
    .describe("Type of persistence backend"),

  SQLITE_DB_PATH: z
    .string()
    .default("./data/taskman.db")
    .describe("SQLite database file path (when PERSISTENCE_TYPE=sqlite)"),

  REDIS_URL: z
    .string()
    .url()
    .default("redis://localhost:6379")
    .describe("Redis connection URL (when PERSISTENCE_TYPE=redis)"),

  // ============================================================================
  // LOCKING CONFIGURATION
  // ============================================================================

  LOCK_TIMEOUT_MS: z
    .number({ coerce: true })
    .int()
    .positive()
    .default(1800000) // 30 minutes
    .describe("Lock expiration timeout in milliseconds"),

  LOCK_CLEANUP_INTERVAL_MS: z
    .number({ coerce: true })
    .int()
    .positive()
    .default(60000) // 1 minute
    .describe("Interval for cleaning up expired locks"),

  // ============================================================================
  // HEALTH CHECK CONFIGURATION
  // ============================================================================

  HEALTH_CHECK_ENABLED: booleanFromEnv()
    .default(true)
    .describe("Enable health check endpoints"),

  BACKEND_HEALTH_CHECK_INTERVAL_MS: z
    .number({ coerce: true })
    .int()
    .positive()
    .default(30000)
    .describe("Interval for checking backend health (30s default)"),

  // ============================================================================
  // OBSERVABILITY CONFIGURATION
  // ============================================================================

  ENABLE_METRICS: booleanFromEnv()
    .default(false)
    .describe("Enable Prometheus metrics endpoint (/metrics)"),

  ENABLE_TRACING: booleanFromEnv()
    .default(false)
    .describe("Enable OpenTelemetry distributed tracing"),

  OTEL_EXPORTER_OTLP_ENDPOINT: z
    .string()
    .url()
    .default("http://localhost:4318/v1/traces")
    .describe("OpenTelemetry collector endpoint (OTLP/HTTP)"),

  OTEL_DEBUG: booleanFromEnv()
    .default(false)
    .describe("Enable OpenTelemetry diagnostic logging"),

  OTEL_SAMPLE_RATE: z
    .number({ coerce: true })
    .min(0)
    .max(1)
    .default(1.0)
    .describe("Trace sampling rate (0.0=none, 1.0=all, 0.1=10%)"),

  // ============================================================================
  // CIRCUIT BREAKER CONFIGURATION
  // ============================================================================

  CIRCUIT_BREAKER_ENABLED: booleanFromEnv()
    .default(true)
    .describe("Enable circuit breaker pattern for backend resilience"),

  CIRCUIT_BREAKER_ERROR_THRESHOLD: z
    .number({ coerce: true })
    .int()
    .min(1)
    .max(100)
    .default(50)
    .describe("Error percentage to open circuit (1-100)"),

  CIRCUIT_BREAKER_RESET_TIMEOUT_MS: z
    .number({ coerce: true })
    .int()
    .positive()
    .default(30000)
    .describe("Milliseconds before attempting circuit recovery"),

  CIRCUIT_BREAKER_VOLUME_THRESHOLD: z
    .number({ coerce: true })
    .int()
    .positive()
    .default(10)
    .describe("Minimum requests before calculating error rate"),

  // ============================================================================
  // FALLBACK CACHE CONFIGURATION
  // ============================================================================

  FALLBACK_CACHE_ENABLED: booleanFromEnv()
    .default(true)
    .describe("Enable fallback cache for read operations during outages"),

  FALLBACK_CACHE_MAX_SIZE: z
    .number({ coerce: true })
    .int()
    .positive()
    .default(1000)
    .describe("Maximum number of cache entries"),

  FALLBACK_CACHE_TTL_MS: z
    .number({ coerce: true })
    .int()
    .positive()
    .default(300000) // 5 minutes
    .describe("Cache entry time-to-live in milliseconds"),

  // ============================================================================
  // DEBUG CONFIGURATION
  // ============================================================================

  TASKMAN_DEBUG: booleanFromEnv()
    .default(false)
    .describe("Enable debug mode with verbose configuration logging"),

  // ============================================================================
  // GRACEFUL SHUTDOWN CONFIGURATION
  // ============================================================================

  GRACEFUL_SHUTDOWN_TIMEOUT_MS: z
    .number({ coerce: true })
    .int()
    .positive()
    .default(30000)
    .describe("Maximum time to wait for graceful shutdown"),
});

/**
 * Export the schema for external validation
 */
export const configSchema = configSchemaInternal;

/**
 * Type-safe configuration object inferred from Zod schema
 *
 * This type is automatically generated from the schema above,
 * ensuring perfect type safety between validation and usage.
 */
export type Config = z.infer<typeof configSchema>;

/**
 * Validate and extract configuration from environment variables
 *
 * @param env - Environment variables object (typically process.env)
 * @returns Validated and type-safe configuration object
 * @throws {z.ZodError} If validation fails, with detailed error messages
 *
 * @example
 * ```typescript
 * const config = validateConfig(process.env);
 * console.log(config.PORT); // Type-safe access: number
 * console.log(config.NODE_ENV); // Type-safe access: "development" | "test" | "production"
 * ```
 *
 * @example Error handling
 * ```typescript
 * try {
 *   const config = validateConfig(process.env);
 * } catch (error) {
 *   if (error instanceof z.ZodError) {
 *     console.error("Configuration validation failed:");
 *     error.errors.forEach(err => {
 *       console.error(`  - ${err.path.join('.')}: ${err.message}`);
 *     });
 *   }
 *   process.exit(1);
 * }
 * ```
 */
export function validateConfig(env: NodeJS.ProcessEnv): Config {
  try {
    return configSchema.parse(env);
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errorMessages = error.errors
        .map((err) => {
          const path = err.path.join(".");
          return `  - ${path}: ${err.message}`;
        })
        .join("\n");

      throw new Error(
        `Configuration validation failed:\n${errorMessages}\n\n` +
          `Please check your environment variables or .env file.`
      );
    }
    throw error;
  }
}

/**
 * Helper function to get environment-specific sampling rate
 *
 * @param env - Environment name
 * @returns Appropriate sampling rate (0.1 for production, 1.0 otherwise)
 */
export function getDefaultSampleRate(env: string): number {
  return env === "production" ? 0.1 : 1.0;
}
