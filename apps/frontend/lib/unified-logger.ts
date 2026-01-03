/**
 * @file unified-logger.ts
 * @description Frontend unified logging module for TaskMan-v2
 * @authority Constitutional Rule 6 (Correlation IDs and traceability)
 *
 * Provides consistent logging interface matching the Python unified-logger
 * for cross-stack correlation and observability.
 */

// ═══════════════════════════════════════════════════════════════════════════
// CORRELATION ID MANAGEMENT
// ═══════════════════════════════════════════════════════════════════════════

let currentCorrelationId: string = generateCorrelationId();

/**
 * Generate a new correlation ID (UUID v4 format)
 */
function generateCorrelationId(): string {
    // Use crypto.randomUUID if available (modern browsers)
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
        return crypto.randomUUID();
    }
    // Fallback for older browsers
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = (Math.random() * 16) | 0;
        const v = c === 'x' ? r : (r & 0x3) | 0x8;
        return v.toString(16);
    });
}

/**
 * Get the current correlation ID
 */
export function getCorrelationId(): string {
    return currentCorrelationId;
}

/**
 * Set the correlation ID (for cross-component tracking)
 */
export function setCorrelationId(id: string): void {
    currentCorrelationId = id;
}

/**
 * Generate and set a new correlation ID
 */
export function newCorrelationId(): string {
    currentCorrelationId = generateCorrelationId();
    return currentCorrelationId;
}

// ═══════════════════════════════════════════════════════════════════════════
// LOG LEVEL TYPES
// ═══════════════════════════════════════════════════════════════════════════

export type LogLevel = 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR';

interface LogEntry {
    timestamp: string;
    level: LogLevel;
    category: string;
    event: string;
    correlation_id: string;
    data?: Record<string, unknown>;
}

// ═══════════════════════════════════════════════════════════════════════════
// UNIFIED LOGGING FUNCTION
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Unified logging function matching Python ulog interface
 *
 * @param category - Log category (e.g., 'auth', 'task', 'navigation')
 * @param event - Event name (e.g., 'login_success', 'task_created')
 * @param level - Log level (DEBUG, INFO, WARNING, ERROR)
 * @param data - Additional structured data
 *
 * @example
 * ulog('auth', 'login_attempt', 'INFO', { username: 'user@example.com' });
 * ulog('task', 'task_created', 'INFO', { taskId: 'TASK-001', title: 'New task' });
 */
export function ulog(
    category: string,
    event: string,
    level: LogLevel = 'INFO',
    data?: Record<string, unknown>
): void {
    const entry: LogEntry = {
        timestamp: new Date().toISOString(),
        level,
        category,
        event,
        correlation_id: currentCorrelationId,
        ...(data && { data }),
    };

    // In production, send to backend logging endpoint
    // For now, log to console with structured format
    const logMethod = getLogMethod(level);

    if (import.meta.env.DEV) {
        // Development: Pretty console output
        const prefix = `[${entry.timestamp}] [${level}] [${category}]`;
        logMethod(`${prefix} ${event}`, data || '');
    } else {
        // Production: Structured JSON for log aggregation
        logMethod(JSON.stringify(entry));
    }

    // TODO: Send to backend telemetry endpoint in production
    // sendToBackend(entry);
}

function getLogMethod(level: LogLevel): typeof console.log {
    switch (level) {
        case 'DEBUG':
            return console.debug;
        case 'INFO':
            return console.info;
        case 'WARNING':
            return console.warn;
        case 'ERROR':
            return console.error;
        default:
            return console.log;
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// LOGGED ACTION WRAPPER
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Higher-order function to wrap async actions with logging
 *
 * @param category - Log category
 * @param actionName - Name of the action being performed
 * @param action - Async function to execute
 * @returns Result of the action
 *
 * @example
 * const result = await loggedAction('api', 'fetch_tasks', async () => {
 *   return await api.getTasks();
 * });
 */
export async function loggedAction<T>(
    category: string,
    actionName: string,
    action: () => Promise<T>
): Promise<T> {
    const startTime = performance.now();

    ulog(category, `${actionName}_start`, 'DEBUG');

    try {
        const result = await action();
        const duration = performance.now() - startTime;

        ulog(category, `${actionName}_success`, 'INFO', {
            duration_ms: Math.round(duration),
        });

        return result;
    } catch (error) {
        const duration = performance.now() - startTime;

        ulog(category, `${actionName}_error`, 'ERROR', {
            duration_ms: Math.round(duration),
            error: error instanceof Error ? error.message : String(error),
            stack: error instanceof Error ? error.stack : undefined,
        });

        throw error;
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// CONVENIENCE EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

export const log = {
    debug: (category: string, event: string, data?: Record<string, unknown>) =>
        ulog(category, event, 'DEBUG', data),
    info: (category: string, event: string, data?: Record<string, unknown>) =>
        ulog(category, event, 'INFO', data),
    warn: (category: string, event: string, data?: Record<string, unknown>) =>
        ulog(category, event, 'WARNING', data),
    error: (category: string, event: string, data?: Record<string, unknown>) =>
        ulog(category, event, 'ERROR', data),
};

export default { ulog, loggedAction, log, getCorrelationId, setCorrelationId, newCorrelationId };
