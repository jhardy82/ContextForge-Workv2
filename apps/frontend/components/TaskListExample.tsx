/**
 * @file TaskListExample.tsx
 * @description Example component demonstrating unified logger integration patterns with Orval + TanStack Query
 * @authority Constitutional Rule 6 (Correlation IDs), AAR-QSE-Enhanced-Unified-Logging
 * @persona Full-Stack Developer (φ³)
 * @pattern Dual-layer logging (preserve React behavior + add structured logging)
 * @location TaskMan-v2/src/components/ (Example reference implementation)
 */

import { useQueryClient } from '@tanstack/react-query';
import React from 'react';
import { TaskResponse, TaskStatus } from '../api/generated/model';
import {
    getListTasksApiV1TasksGetQueryKey,
    useCreateTaskApiV1TasksPost,
    useDeleteTaskApiV1TasksTaskIdDelete,
    useListTasksApiV1TasksGet,
    useUpdateTaskApiV1TasksTaskIdPatch
} from '../api/generated/tasks/tasks';
import { useCorrelationId, useLoggedEffect, useLogger } from '../hooks/useLogger';

// ═══════════════════════════════════════════════════════════════════════════
// EXAMPLE: Task Management Component with Unified Logging & Orval/ReactQuery
// ═══════════════════════════════════════════════════════════════════════════

/**
 * TaskListExample - Demonstrates all logger integration patterns
 * Refactored to use Orval-generated hooks + React Query
 *
 * PATTERN 1: useLogger() hook for manual logging
 * PATTERN 2: Query/Mutation callbacks for logging results
 * PATTERN 3: useCorrelationId() for API request headers (passed via request options)
 * PATTERN 4: useLoggedEffect() for component lifecycle logging
 */
export function TaskListExample() {
    const { log } = useLogger();
    const { correlationId, refreshCorrelationId } = useCorrelationId();
    const queryClient = useQueryClient();

    // ───────────────────────────────────────────────────────────────────────
    // PATTERN 4: Component lifecycle logging with useLoggedEffect
    // ───────────────────────────────────────────────────────────────────────

    useLoggedEffect('component_lifecycle', 'TaskListExample_mount', () => {
        console.log('TaskListExample mounted');
        return () => {
            log('component_lifecycle', 'TaskListExample_unmount', 'INFO');
        };
    }, []);

    // ───────────────────────────────────────────────────────────────────────
    // DATA FETCHING: useQuery via Orval
    // ───────────────────────────────────────────────────────────────────────

    // Pass correlation ID in request headers
    const { data: taskList, isLoading, error, refetch } = useListTasksApiV1TasksGet(
        { page: 1, per_page: 100 }, // Params
        {
            request: {
                headers: {
                    'X-Correlation-ID': correlationId,
                }
            },
            query: {
                // Log on success/error can be handled here or via useEffect
            }
        }
    );

    // Map API response to tasks array
    const tasks = taskList?.tasks || [];

    // Log data loaded (Pattern 1)
    React.useEffect(() => {
        if (taskList) {
            log('task_list', 'tasks_loaded', 'INFO', {
                taskCount: taskList.tasks.length,
            });
        }
    }, [taskList, log]);

    React.useEffect(() => {
        if (error) {
            console.error('Failed to fetch tasks:', error);
            log('task_list', 'crud_read_failed', 'ERROR', { error: String(error) });
        }
    }, [error, log]);

    // ───────────────────────────────────────────────────────────────────────
    // MUTATIONS
    // ───────────────────────────────────────────────────────────────────────

    const createMutation = useCreateTaskApiV1TasksPost({
        mutation: {
            onSuccess: (newTask: TaskResponse) => {
                 // PATTERN 1: Log task creation event
                log('task', 'task_created', 'INFO', {
                    taskId: newTask.id,
                    taskTitle: newTask.title,
                });
                // Invalidate list to refetch
                queryClient.invalidateQueries({ queryKey: getListTasksApiV1TasksGetQueryKey() });
            },
            onError: (err) => {
                 log('task', 'task_create_failed', 'ERROR', { error: String(err) });
            }
        },
        request: {
            headers: { 'X-Correlation-ID': correlationId }
        }
    });

    const updateMutation = useUpdateTaskApiV1TasksTaskIdPatch({
        mutation: {
            onSuccess: (data: TaskResponse) => {
                log('task', 'task_updated', 'INFO', { taskId: data.id, status: data.status });
                queryClient.invalidateQueries({ queryKey: getListTasksApiV1TasksGetQueryKey() });
            },
             onError: (err) => {
                 log('task', 'task_update_failed', 'ERROR', { error: String(err) });
            }
        },
        request: {
            headers: { 'X-Correlation-ID': correlationId }
        }
    });

    const deleteMutation = useDeleteTaskApiV1TasksTaskIdDelete({
        mutation: {
            onSuccess: (data, variables) => {
                log('task', 'task_deleted', 'INFO', { taskId: variables.taskId });
                queryClient.invalidateQueries({ queryKey: getListTasksApiV1TasksGetQueryKey() });
            },
             onError: (err) => {
                 log('task', 'task_delete_failed', 'ERROR', { error: String(err) });
            }
        },
        request: {
             headers: { 'X-Correlation-ID': correlationId }
        }
    });

    // ───────────────────────────────────────────────────────────────────────
    // HANDLERS
    // ───────────────────────────────────────────────────────────────────────

    const handleCreateTask = (title: string) => {
        // Generate a simplified ID for now, or let backend handle it if schema allows.
        // Schema said ID is required.
        const id = `T-${Date.now()}`;
        createMutation.mutate({
            data: {
                id,
                title,
                summary: title,
                status: TaskStatus.new,
                owner: 'user-1',
                primary_project: 'PROJ-DEFAULT'
            }
        });
    };

    const handleUpdateStatus = (taskId: string, newStatus: TaskStatus) => {
        updateMutation.mutate({
            taskId,
            data: {
                status: newStatus
            }
        });
    };

    const handleDeleteTask = (taskId: string) => {
        deleteMutation.mutate({ taskId });
    };

    const handleRefreshCorrelation = (): void => {
        const newId = refreshCorrelationId();
        log('session', 'correlation_refreshed', 'INFO', {
            oldId: correlationId,
            newId,
        });
        // Force refetch to use new header
        setTimeout(() => refetch(), 0);
    };

    // ───────────────────────────────────────────────────────────────────────
    // RENDER
    // ───────────────────────────────────────────────────────────────────────

    return (
        <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
            <h1>Task List (Generated Client + Unified Logger)</h1>

            <div style={{ marginBottom: '20px', padding: '10px', background: '#f0f0f0' }}>
                <strong>Correlation ID:</strong> <code>{correlationId}</code>
                <button onClick={handleRefreshCorrelation} style={{ marginLeft: '10px' }}>
                    Refresh Correlation ID
                </button>
            </div>

            <button onClick={() => refetch()} disabled={isLoading} style={{ marginRight: '10px' }}>
                {isLoading ? 'Loading...' : 'Refetch Tasks'}
            </button>

            <button onClick={() => handleCreateTask('New Task ' + Date.now())}>
                Create Test Task
            </button>

            <div style={{ marginTop: '20px' }}>
                {tasks.length === 0 && !isLoading ? (
                    <p>No tasks loaded. (Or empty list)</p>
                ) : (
                    <ul>
                        {tasks.map((task) => (
                            <li key={task.id} style={{ marginBottom: '10px' }}>
                                <strong>{task.title}</strong> - Status: {task.status} - Created: {task.created_at}
                                <br />
                                <button
                                    onClick={() => handleUpdateStatus(task.id, TaskStatus.in_progress)}
                                    style={{ marginRight: '5px' }}
                                >
                                    Set In Progress
                                </button>
                                <button
                                    onClick={() => handleUpdateStatus(task.id, TaskStatus.done)}
                                    style={{ marginRight: '5px' }}
                                >
                                    Set Done
                                </button>
                                <button onClick={() => handleDeleteTask(task.id)}>Delete</button>
                            </li>
                        ))}
                    </ul>
                )}
                {error && <div style={{color: 'red'}}>Error: {String(error)}</div>}
            </div>

            <div style={{ marginTop: '30px', padding: '10px', background: '#e8f4f8' }}>
                <h3>📋 Changes from Manual Fetch:</h3>
                <ol>
                    <li>
                        <strong>orval hooks</strong> - Used <code>useListTasksApiV1TasksGet</code> instead of <code>fetch</code>
                    </li>
                    <li>
                        <strong>React Query</strong> - Automatic cache management and refetching
                    </li>
                    <li>
                        <strong>UseCorrelationId</strong> - Passed via request options headers
                    </li>
                    <li>
                        <strong>Types</strong> - Used <code>TaskResponse</code> instead of local interface
                    </li>
                </ol>
            </div>
        </div>
    );
}

export default TaskListExample;
