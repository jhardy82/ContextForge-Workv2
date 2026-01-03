/**
 * @file useLogger.tsx
 * @description React hooks for correlation-aware logging in TaskMan-v2 frontend
 * @authority Constitutional Rule 6 (Correlation IDs and traceability)
 * @persona Full-Stack Developer (φ³)
 * @pattern React Context API + custom hooks for cross-component correlation tracking
 * @location TaskMan-v2/src/hooks/ (React hooks directory)
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import {
    ulog,
    loggedAction,
    getCorrelationId,
    setCorrelationId,
    newCorrelationId,
} from '../lib/unified-logger';

// ═══════════════════════════════════════════════════════════════════════════
// CORRELATION CONTEXT
// ═══════════════════════════════════════════════════════════════════════════

interface CorrelationContextValue {
    correlationId: string;
    refreshCorrelationId: () => string;
    log: typeof ulog;
    loggedAction: typeof loggedAction;
}

const CorrelationContext = createContext<CorrelationContextValue | undefined>(undefined);

// ═══════════════════════════════════════════════════════════════════════════
// CORRELATION PROVIDER
// ═══════════════════════════════════════════════════════════════════════════

interface CorrelationProviderProps {
    children: ReactNode;
}

/**
 * CorrelationProvider - Wraps app to provide correlation ID context
 * Automatically logs navigation events and manages session-level correlation
 *
 * @example
 * // In main.tsx or App.tsx
 * <CorrelationProvider>
 *   <App />
 * </CorrelationProvider>
 */
export function CorrelationProvider({ children }: CorrelationProviderProps): JSX.Element {
    const [correlationId, setStateCorrelationId] = useState<string>(getCorrelationId());

    /**
     * Generate new correlation ID for sub-operations (e.g., SPA navigation)
     */
    const refreshCorrelationId = (): string => {
        const newId = newCorrelationId();
        setCorrelationId(newId);
        setStateCorrelationId(newId);
        return newId;
    };

    // Log SPA navigation events
    useEffect(() => {
        const handleLocationChange = () => {
            ulog('spa_navigation', 'route', 'success', {
                path: window.location.pathname,
                search: window.location.search,
                hash: window.location.hash,
            });
        };

        // Listen for pushState/replaceState (React Router, etc.)
        window.addEventListener('popstate', handleLocationChange);

        return () => window.removeEventListener('popstate', handleLocationChange);
    }, []);

    const contextValue: CorrelationContextValue = {
        correlationId,
        refreshCorrelationId,
        log: ulog,
        loggedAction,
    };

    return (
        <CorrelationContext.Provider value={contextValue}>
            {children}
        </CorrelationContext.Provider>
    );
}

// ═══════════════════════════════════════════════════════════════════════════
// CUSTOM HOOKS
// ═══════════════════════════════════════════════════════════════════════════

/**
 * useLogger - Access logging functions with automatic correlation ID context
 *
 * @returns {object} { log, loggedAction, correlationId, refreshCorrelationId }
 *
 * @example
 * function TaskList() {
 *   const { log, loggedAction } = useLogger();
 *
 *   const handleCreateTask = async (taskData) => {
 *     await loggedAction('crud_create', 'task', async () => {
 *       const task = await api.createTask(taskData);
 *       log('task_created', 'task', 'success', { taskId: task.id });
 *       return task;
 *     });
 *   };
 *
 *   return <div>...</div>;
 * }
 */
export function useLogger(): CorrelationContextValue {
    const context = useContext(CorrelationContext);

    if (!context) {
        throw new Error('useLogger must be used within a CorrelationProvider');
    }

    return context;
}

/**
 * useCorrelationId - Get current correlation ID and refresh function
 *
 * @returns {object} { correlationId, refreshCorrelationId }
 *
 * @example
 * function ApiClient() {
 *   const { correlationId } = useCorrelationId();
 *
 *   const fetchData = async () => {
 *     const response = await fetch('/api/data', {
 *       headers: { 'X-Correlation-ID': correlationId }
 *     });
 *     return response.json();
 *   };
 *
 *   return <div>...</div>;
 * }
 */
export function useCorrelationId(): Pick<CorrelationContextValue, 'correlationId' | 'refreshCorrelationId'> {
    const context = useContext(CorrelationContext);

    if (!context) {
        throw new Error('useCorrelationId must be used within a CorrelationProvider');
    }

    return {
        correlationId: context.correlationId,
        refreshCorrelationId: context.refreshCorrelationId,
    };
}

/**
 * useLoggedEffect - useEffect wrapper with automatic logging
 *
 * @param {string} action - Operation type (e.g., 'component_mount')
 * @param {string} target - Target component/resource
 * @param {Function} effect - Effect function to execute
 * @param {Array} deps - Dependency array
 *
 * @example
 * function TaskDetail({ taskId }) {
 *   useLoggedEffect('component_mount', 'TaskDetail', () => {
 *     console.log('TaskDetail mounted');
 *   }, []);
 *
 *   useLoggedEffect('task_fetch', 'task', async () => {
 *     const task = await api.getTask(taskId);
 *     setTask(task);
 *   }, [taskId]);
 * }
 */
export function useLoggedEffect(
    action: string,
    target: string,
    effect: () => void | (() => void),
    deps: React.DependencyList
): void {
    const { log } = useLogger();

    useEffect(() => {
        log(action, target, 'success', { deps: deps.length });
        return effect();
    }, deps);
}

// ═══════════════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════════════

export default {
    CorrelationProvider,
    useLogger,
    useCorrelationId,
    useLoggedEffect,
};
