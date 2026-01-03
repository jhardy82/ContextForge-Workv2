/**
 * TaskMan-v2 Frontend Type Definitions
 *
 * Core types for the TaskMan-v2 dashboard including Task, Project,
 * and API response types. Aligned with backend-api schema.
 */

// ============================================================================
// Task Status and Priority
// ============================================================================

export type TaskStatus =
  | "new" // Backend
  | "ready" // Backend
  | "active" // Backend
  | "in_progress"
  | "blocked"
  | "review"
  | "done"
  | "dropped" // Backend
  | "todo" // Legacy
  | "pending" // Legacy
  | "completed" // Legacy
  | "cancelled";

export type TaskPriority = "low" | "medium" | "high" | "critical";

export type SacredGeometryShape =
  | "circle"
  | "triangle"
  | "square"
  | "pentagon"
  | "hexagon"
  | "spiral";

// ============================================================================
// Core Task Type (64-field compatible)
// ============================================================================

export interface Task {
  id: string;
  title: string;
  summary?: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;

  // Sacred Geometry integration
  shape?: SacredGeometryShape;

  // Hierarchy
  project_id?: string;
  sprint_id?: string;
  parent_task_id?: string;

  // Time tracking
  estimated_hours?: number;
  actual_hours?: number;
  due_date?: string;

  // Metadata
  created_at: string;
  updated_at: string;
  assigned_to?: string;
  tags?: string[];

  // AI Integration
  ai_context?: string;
  ai_suggestions?: string[];

  // Extended fields (from 64-field schema)
  acceptance_criteria?: string[];
  dependencies?: string[];
  blockers?: string[];
  notes?: string;
}

// ============================================================================
// Project Type
// ============================================================================

export interface Project {
  id: string;
  name: string;
  description?: string;
  status: "active" | "archived" | "completed";
  created_at: string;
  updated_at: string;
  task_count?: number;
  completed_task_count?: number;
}

// ============================================================================
// Sprint Type
// ============================================================================

export interface Sprint {
  id: string;
  name: string;
  project_id: string;
  start_date: string;
  end_date: string;
  status: "planned" | "active" | "completed";
  goal?: string;
  task_count?: number;
  completed_task_count?: number;
}

// ============================================================================
// Connection Status
// ============================================================================

export interface ConnectionStatus {
  connected: boolean;
  status: "connected" | "disconnected" | "connecting" | "error";
  lastChecked?: Date;
  message?: string;
  error?: string;
}

// ============================================================================
// API Response Types
// ============================================================================

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface HealthCheckResponse {
  status: "healthy" | "unhealthy";
  version?: string;
  database?: "connected" | "disconnected";
  timestamp: string;
}

// ============================================================================
// AI Prompt Types
// ============================================================================

export type AIPromptType =
  | "implementation"
  | "testing"
  | "validation"
  | "documentation";

export const AI_PROMPT_TYPES: Record<
  AIPromptType,
  { label: string; icon: string }
> = {
  implementation: { label: "Implementation", icon: "🔧" },
  testing: { label: "Testing", icon: "🧪" },
  validation: { label: "Validation", icon: "✅" },
  documentation: { label: "Documentation", icon: "📝" },
};

export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  response: string;
  action_taken?: string;
  data?: any;
}

// ============================================================================
// Sacred Geometry Shapes
// ============================================================================

export const SACRED_GEOMETRY_SHAPES: Record<SacredGeometryShape, string> = {
  circle: "○",
  triangle: "△",
  square: "□",
  pentagon: "⬠",
  hexagon: "⬡",
  spiral: "🌀",
};

// ============================================================================
// Status Colors (for UI)
// ============================================================================

export const STATUS_COLORS: Record<TaskStatus, string> = {
  new: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
  ready: "bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200",
  active: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  in_progress: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  blocked: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  review:
    "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  done: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  dropped: "bg-gray-200 text-gray-500 dark:bg-gray-700 dark:text-gray-400",
  todo: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
  pending: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
  completed:
    "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  cancelled: "bg-gray-200 text-gray-500 dark:bg-gray-700 dark:text-gray-400",
};

export const PRIORITY_COLORS: Record<TaskPriority, string> = {
  low: 'bg-gray-100 text-gray-600',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-orange-100 text-orange-800',
  critical: 'bg-red-100 text-red-800',
};

// ============================================================================
// Tree Node Type (for task hierarchy display)
// ============================================================================

export interface TaskTreeNode extends Task {
  children?: TaskTreeNode[];
  expanded?: boolean;
  level?: number;
}

export interface ProjectTreeNode extends Project {
  tasks?: TaskTreeNode[];
  sprints?: Sprint[];
  expanded?: boolean;
}
