/**
 * Feature-Specific Project Hooks
 */

import { normalizeError, type AppError } from '../errors';
import {
    useGetProjectApiV1ProjectsProjectIdGet,
    useListProjectsApiV1ProjectsGet,
} from '../generated/projects/projects';

/**
 * Hook for fetching all projects
 */
export function useProjects(params?: { status?: string }) {
  const query = useListProjectsApiV1ProjectsGet(params);

  return {
    projects: query.data?.projects ?? [],
    total: query.data?.total ?? 0,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error ? normalizeError(query.error) : null,
    refetch: query.refetch,
  };
}

/**
 * Hook for fetching a single project
 */
export function useProject(projectId: string, options?: { enabled?: boolean }) {
  const query = useGetProjectApiV1ProjectsProjectIdGet(projectId, {
    query: { enabled: options?.enabled ?? true },
  });

  return {
    project: query.data ?? null,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error ? normalizeError(query.error) : null,
    refetch: query.refetch,
  };
}

export type { AppError };
