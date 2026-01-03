import { TaskResponse } from '../api/generated/model';
import { Task, TaskPriority, TaskStatus } from './types';

/**
 * Maps properties from the backend TaskResponse to the frontend Task interface.
 * Handles field renaming and type conversions.
 */
export function mapTaskResponseToTask(response: TaskResponse): Task {
    // Map status - backend status should now match frontend TaskStatus union
    // but we cast to be safe or map specific legacy values if needed
    const status = response.status as unknown as TaskStatus;

    // Map priority - assuming lowercase match
    // Backend Priority: 'low' | 'medium' | 'high' | 'critical' (Need to verify)
    // Frontend TaskPriority: 'low' | 'medium' | 'high' | 'critical'
    const priority = (response.priority?.toLowerCase() || 'medium') as TaskPriority;

    return {
        id: response.id,
        title: response.title,
        summary: response.summary,
        description: response.description,
        status: status,
        priority: priority,

        // Sacred Geometry
        shape: response.shape as any, // Cast if enum values match

        // Hierarchy
        project_id: response.primary_project,
        sprint_id: typeof response.primary_sprint === 'string' ? response.primary_sprint : undefined, // Check if object or string
        // Note: TaskResponsePrimarySprint might be null.

        // Time tracking
        estimated_hours: typeof response.estimate_points === 'number' ? response.estimate_points : undefined, // Points != hours but approximate
        actual_hours: typeof response.actual_time_hours === 'number' ? response.actual_time_hours : undefined,
        due_date: response.due_at || undefined, // string | null -> string | undefined

        // Metadata
        created_at: response.created_at || new Date().toISOString(),
        updated_at: response.updated_at || new Date().toISOString(),
        assigned_to: response.owner, // Owner or assignee?
        tags: response.labels,

        // AI Mock fields
        ai_context: undefined,
        ai_suggestions: undefined,

        // Extended fields
        acceptance_criteria: response.acceptance_criteria?.map(ac => typeof ac === 'string' ? ac : JSON.stringify(ac)),
        dependencies: response.depends_on,
        blockers: response.blockers,
        notes: undefined,

        // Populate other Task fields as needed
    };
}
