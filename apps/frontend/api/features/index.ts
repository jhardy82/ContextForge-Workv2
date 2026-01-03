/**
 * Feature Hooks Index
 *
 * Central export for all feature-specific API hooks.
 * UI components should import from here, not from generated/ or individual files.
 */

// Tasks
export {
  useCreateTask,
  useDeleteTask,
  useTask,
  useTasks,
  useUpdateTask,
} from "./useTasks";

// Projects
export { useProject, useProjects } from "./useProjects";

// Sprints
export { useSprint, useSprints } from "./useSprints";

// Error utilities
export {
  isNetworkError,
  isNotFoundError,
  isUnauthorizedError,
  normalizeError,
} from "../errors";
export type { AppError } from "../errors";
