/**
 * TaskMan v3 - Core Domain Objects (64-Field Schema)
 *
 * This file defines the comprehensive 64-field schema for Tasks, organized into
 * 9 logical categories. It serves as the single source of truth for the frontend
 * domain model.
 */

// 1. Task Identity (5 fields)
export interface TaskIdentity {
  id: string;
  task_id: string; // Human readable ID (e.g. TASK-123)
  title: string;
  description: string;
  task_type: 'feature' | 'bug' | 'chore' | 'epic' | 'story' | 'subtask' | 'initiative' | 'theme';
}

export type TaskStatus =
  | 'new'
  | 'ready'
  | 'active'
  | 'in_progress'
  | 'blocked'
  | 'review'
  | 'done'
  | 'dropped'
  | 'todo'      // Legacy
  | 'started'   // Legacy
  | 'pending'   // Legacy
  | 'completed' // Legacy
  | 'deferred'  // Legacy
  | 'canceled'; // Legacy

export type TaskPriority = 'critical' | 'high' | 'medium' | 'low' | 'trivial';
export type TaskSeverity = 'blocker' | 'critical' | 'major' | 'minor' | 'cosmetic';
export type TaskHealth = 'on_track' | 'at_risk' | 'off_track' | 'completed';

export interface TaskLifecycle {
  status: TaskStatus;
  priority: TaskPriority;
  severity: TaskSeverity;
  health: TaskHealth;
  risk_level: 'low' | 'medium' | 'high' | 'extreme';
  complexity: 'xs' | 's' | 'm' | 'l' | 'xl'; // T-shirt sizing
  effort_estimate: number; // Story points or hours
}

// 3. Task Relationships (6 fields)
export interface TaskRelationships {
  parent_task_id: string | null;
  epic_id: string | null;
  sprint_id: string | null;
  project_id: string | null;
  dependencies: string[]; // Array of Task IDs that block this task
  related_tasks: string[]; // Array of Task IDs related but not blocking
}

// 4. Task People (4 fields)
export interface TaskPeople {
  assignee: string | null; // User ID or Name
  created_by: string; // User ID
  reporter: string; // User ID
  stakeholders: string[]; // Array of User IDs
}

// 5. Task Temporal (8 fields)
export interface TaskTemporal {
  created_at: string; // ISO Date
  updated_at: string; // ISO Date
  start_date: string | null; // ISO Date
  due_date: string | null; // ISO Date
  completed_at: string | null; // ISO Date
  estimated_hours: number | null;
  actual_hours: number | null;
  remaining_hours: number | null;
}

// 6. Task Business Context (8 fields)
export interface TaskBusinessContext {
  business_value: number; // 0-100 or Fibonacci
  roi_score: number | null;
  customer_impact: 'high' | 'medium' | 'low' | 'none';
  strategic_alignment: number; // 0-10 score of alignment with company goals
  motivational_context: string | null; // "Why" this task is important
  success_criteria: string[]; // List of specific success conditions
  acceptance_criteria: string[]; // Formal Gherkin or list
  definition_of_done: string[]; // Specific DoD checklist items
}

// 7. Task Technical Context (10 fields)
export interface TaskTechnical {
  technical_scope: string | null;
  integration_points: string[];
  deployment_env: 'dev' | 'staging' | 'prod' | 'all';
  service_topology: string[]; // Microservices involved
  performance_targets: string | null; // e.g. "Page load < 200ms"
  algorithm_notes: string | null;
  data_structures: string | null;
  tech_debt_score: number; // 0-10
  refactor_candidate: boolean;
  deprecation_status: boolean;
}

// 8. Task Quality & Validation (8 fields)
export interface TaskQuality {
  test_coverage: number; // Percentage
  security_audit_status: 'pending' | 'passed' | 'failed' | 'not_required';
  accessibility_compliant: boolean;
  evidence_bundle_hash: string | null; // Link to test evidence bundle
  validation_status: 'unvalidated' | 'validated' | 'rejected';
  stability_score: number; // 0-100
  completeness_pct: number; // 0-100 manual progress tracking
  quality_gate_status: 'open' | 'closed' | 'breached';
}

// 9. Context of Fields (COF) Dimensions (8 fields)
// These represent abstract/meta dimensions for advanced filtering and AI context
export interface TaskCOFDimensions {
  cof_motivational: number; // 0-10
  cof_relational: number; // 0-10
  cof_situational: number; // 0-10
  cof_narrative: string | null;
  cof_sacred_geometry: string | null; // Abstract structural alignment
  cof_temporal: number; // 0-10 (Time pressure/relevance)
  cof_spatial: number; // 0-10 (Architectural spread)
  cof_holistic: number; // 0-10 (Overall system harmony)
}

// ==========================================
// COMPOSITE INTERFACES
// ==========================================

export interface Task extends
  TaskIdentity,
  TaskLifecycle,
  TaskRelationships,
  TaskPeople,
  TaskTemporal,
  TaskBusinessContext,
  TaskTechnical,
  TaskQuality,
  TaskCOFDimensions {
    // Helper/Legacy fields for backward compatibility if needed can go here
    // but we aim for purity in this v3 schema.
    tags: string[]; // Extra flexibility
}

// Hierarchy Types
export interface Project {
  id: string;
  name: string;
  key: string;
  description?: string;
  mission?: string;
  start_date?: string;
  owner?: string;
}

export interface Sprint {
  id: string;
  name: string;
  start_date?: string;
  end_date?: string;
  goal?: string;
  status: "planned" | "active" | "completed";
}

export type HierarchyLevel = 'initiative' | 'project' | 'epic' | 'sprint' | 'story' | 'task' | 'subtask';

export interface TreeNode extends Task {
  children?: TreeNode[];
  level: HierarchyLevel;
}

// Helper function to get a unique ID from a node
export function getNodeId(node: TreeNode | Task): string {
  console.debug('[DEBUG] getNodeId called for:', node?.id || 'unknown');
  return node?.id || node?.task_id || 'unknown';
}
