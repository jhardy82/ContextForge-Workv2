/**
 * Feature-Specific Sprint Hooks
 */

import { normalizeError, type AppError } from '../errors';
import {
    useGetSprintApiV1SprintsSprintIdGet,
    useListSprintsApiV1SprintsGet,
} from '../generated/sprints/sprints';

/**
 * Hook for fetching all sprints
 */
export function useSprints(params?: { project_id?: string; status?: string }) {
  const query = useListSprintsApiV1SprintsGet(params);

  return {
    sprints: query.data?.sprints ?? [],
    total: query.data?.total ?? 0,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error ? normalizeError(query.error) : null,
    refetch: query.refetch,
  };
}

/**
 * Hook for fetching a single sprint
 */
export function useSprint(sprintId: string, options?: { enabled?: boolean }) {
  const query = useGetSprintApiV1SprintsSprintIdGet(sprintId, {
    query: { enabled: options?.enabled ?? true },
  });

  return {
    sprint: query.data ?? null,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error ? normalizeError(query.error) : null,
    refetch: query.refetch,
  };
}

export type { AppError };
