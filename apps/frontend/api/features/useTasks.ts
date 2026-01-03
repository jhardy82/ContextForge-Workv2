/**
 * Feature-Specific Task Hooks
 *
 * Wraps generated Orval hooks with normalized error handling and
 * feature-specific data transformation.
 *
 * Per research: UI should import from feature hooks, not raw Orval hooks.
 */

import { useQueryClient } from '@tanstack/react-query';
import { normalizeError, type AppError } from '../errors';
import {
    getListTasksApiV1TasksGetQueryKey,
    useCreateTaskApiV1TasksPost,
    useDeleteTaskApiV1TasksTaskIdDelete,
    useGetTaskApiV1TasksTaskIdGet,
    useListTasksApiV1TasksGet,
    useUpdateTaskApiV1TasksTaskIdPut,
} from '../generated/tasks/tasks';

/**
 * Hook for fetching all tasks with normalized error handling
 */
export function useTasks(params?: { status?: string; priority?: string }) {
  const query = useListTasksApiV1TasksGet(params);

  return {
    tasks: query.data?.tasks ?? [],
    total: query.data?.total ?? 0,
    page: query.data?.page ?? 1,
    hasMore: query.data?.has_more ?? false,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error ? normalizeError(query.error) : null,
    refetch: query.refetch,
  };
}

/**
 * Hook for fetching a single task by ID
 */
export function useTask(taskId: string, options?: { enabled?: boolean }) {
  const query = useGetTaskApiV1TasksTaskIdGet(taskId, {
    query: { enabled: options?.enabled ?? true },
  });

  return {
    task: query.data ?? null,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error ? normalizeError(query.error) : null,
    refetch: query.refetch,
  };
}

/**
 * Hook for creating a new task with optimistic updates
 */
export function useCreateTask() {
  const queryClient = useQueryClient();
  const mutation = useCreateTaskApiV1TasksPost({
    mutation: {
      onSuccess: () => {
        // Invalidate and refetch tasks list
        queryClient.invalidateQueries({ queryKey: getListTasksApiV1TasksGetQueryKey() });
        console.debug('[API] Task created, invalidating task list');
      },
    },
  });

  return {
    createTask: mutation.mutateAsync,
    isCreating: mutation.isPending,
    isError: mutation.isError,
    error: mutation.error ? normalizeError(mutation.error) : null,
    reset: mutation.reset,
  };
}

/**
 * Hook for updating a task
 */
export function useUpdateTask() {
  const queryClient = useQueryClient();
  const mutation = useUpdateTaskApiV1TasksTaskIdPut({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: getListTasksApiV1TasksGetQueryKey() });
        console.debug('[API] Task updated, invalidating task list');
      },
    },
  });

  return {
    updateTask: (taskId: string, data: Parameters<typeof mutation.mutateAsync>[0]['data']) =>
      mutation.mutateAsync({ taskId, data }),
    isUpdating: mutation.isPending,
    isError: mutation.isError,
    error: mutation.error ? normalizeError(mutation.error) : null,
    reset: mutation.reset,
  };
}

/**
 * Hook for deleting a task
 */
export function useDeleteTask() {
  const queryClient = useQueryClient();
  const mutation = useDeleteTaskApiV1TasksTaskIdDelete({
    mutation: {
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: getListTasksApiV1TasksGetQueryKey() });
        console.debug('[API] Task deleted, invalidating task list');
      },
    },
  });

  return {
    deleteTask: mutation.mutateAsync,
    isDeleting: mutation.isPending,
    isError: mutation.isError,
    error: mutation.error ? normalizeError(mutation.error) : null,
    reset: mutation.reset,
  };
}

export type { AppError };
