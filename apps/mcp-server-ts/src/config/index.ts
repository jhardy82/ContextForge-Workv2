/**
 * Configuration Module - Load and validate environment variables
 *
 * Features:
 * - Loads .env file with dotenv (system env vars take precedence)
 * - Validates all configuration with Zod schema
 * - Type-safe configuration export
 * - Comprehensive startup logging in debug mode
 * - Fail-fast validation with detailed error messages
 *
 * Migration Notes:
 * - Migrated from Joi to Zod for better TypeScript integration
 * - Zod provides automatic type inference and better error messages
 * - Backend API runs on port 3001 (default: http://localhost:3001/api/v1)
 */

import * as dotenv from "dotenv";
import { validateConfig, type Config } from "./schema.js";

// Detect STDIO transport early (before config is parsed) to suppress dotenv output
const isStdioTransport = process.env.TASKMAN_MCP_TRANSPORT === "stdio";

// Load .env file (if it exists)
// Override: false ensures system/process environment variables take precedence over .env file
// This allows tests, CI/CD, and containers to set env vars without being overwritten
// CRITICAL: quiet: true prevents dotenv v17+ from outputting to stdout (corrupts STDIO transport)
// The condition in dotenv is: if (debug || !quiet) { _log(...) }
dotenv.config({ override: false, debug: false, quiet: isStdioTransport });

// Validate and export configuration
// This will throw a detailed error if validation fails
let config: Config;

try {
  config = validateConfig(process.env);
} catch (error) {
  // Enhanced error handling for Zod validation errors
  console.error("❌ Configuration validation failed!");
  console.error((error as Error).message);
  console.error("\nPlease check your environment variables or .env file.");
  console.error("See .env.example for reference configuration.");
  process.exit(1);
}

export { config };

// Comprehensive configuration logging on startup (debug mode only)
// CRITICAL: Use console.error (stderr) to avoid corrupting STDIO transport
// stdout is reserved for JSON-RPC protocol messages when using STDIO transport
if (config.TASKMAN_DEBUG) {
  console.error("✅ [Config] Configuration loaded and validated");
  console.error("[Config] Environment Configuration:", {
    // Environment
    NODE_ENV: config.NODE_ENV,

    // Server
    PORT: config.PORT,
    TASKMAN_MCP_TRANSPORT: config.TASKMAN_MCP_TRANSPORT,

    // Backend API
    TASK_MANAGER_API_ENDPOINT: config.TASK_MANAGER_API_ENDPOINT,
    BACKEND_TIMEOUT_MS: config.BACKEND_TIMEOUT_MS,
    BACKEND_MAX_RETRIES: config.BACKEND_MAX_RETRIES,

    // Logging
    LOG_LEVEL: config.LOG_LEVEL,
    LOG_FORMAT: config.LOG_FORMAT,

    // Persistence
    ENABLE_PERSISTENCE: config.ENABLE_PERSISTENCE,
    PERSISTENCE_TYPE: config.PERSISTENCE_TYPE,

    // Observability
    ENABLE_METRICS: config.ENABLE_METRICS,
    ENABLE_TRACING: config.ENABLE_TRACING,
    OTEL_SAMPLE_RATE: config.OTEL_SAMPLE_RATE,

    // Resilience
    CIRCUIT_BREAKER_ENABLED: config.CIRCUIT_BREAKER_ENABLED,
    FALLBACK_CACHE_ENABLED: config.FALLBACK_CACHE_ENABLED,

    // Health Checks
    HEALTH_CHECK_ENABLED: config.HEALTH_CHECK_ENABLED,
  });

  // Log validation summary
  console.error("[Config] Validation Summary:");
  console.error(`  ✓ Environment: ${config.NODE_ENV}`);
  console.error(`  ✓ Backend API: ${config.TASK_MANAGER_API_ENDPOINT}`);
  console.error(`  ✓ Transport: ${config.TASKMAN_MCP_TRANSPORT}`);
  console.error(`  ✓ Persistence: ${config.ENABLE_PERSISTENCE ? config.PERSISTENCE_TYPE : "disabled"}`);
  console.error(`  ✓ Observability: ${config.ENABLE_METRICS ? "metrics" : ""} ${config.ENABLE_TRACING ? "tracing" : ""}`);
  console.error(`  ✓ Resilience: Circuit Breaker ${config.CIRCUIT_BREAKER_ENABLED ? "enabled" : "disabled"}`);
}
