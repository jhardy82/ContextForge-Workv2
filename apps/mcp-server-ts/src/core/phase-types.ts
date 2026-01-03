/**
 * @module Phase Tracking Types
 * @description TypeScript type definitions for lifecycle phase tracking.
 *
 * Provides phase tracking for Task, Sprint, and Project entities:
 * - Research phase: Has research been conducted? Is adequate research attached?
 * - Planning phase: Has planning been completed?
 * - Implementation phase: What is the implementation status?
 * - Testing/Validation phase: What is the testing and validation status?
 *
 * Each phase can be: not_started, in_progress, completed, skipped, or blocked.
 *
 * @packageDocumentation
 */

import type { ISODateTimeString } from "./types.js";

/**
 * Phase status values.
 *
 * @category Phase Tracking
 */
export type PhaseStatus =
  | "not_started"
  | "in_progress"
  | "completed"
  | "skipped"
  | "blocked";

/**
 * Entity types that support phase tracking.
 *
 * @category Phase Tracking
 */
export type PhaseEntityType = "task" | "sprint" | "project";

/**
 * Phase names for Task entities (4 phases).
 *
 * @category Phase Tracking
 */
export type TaskPhaseName =
  | "research"
  | "planning"
  | "implementation"
  | "testing";

/**
 * Phase names for Sprint entities (2 phases).
 *
 * @category Phase Tracking
 */
export type SprintPhaseName = "planning" | "implementation";

/**
 * Phase names for Project entities (2 phases).
 *
 * @category Phase Tracking
 */
export type ProjectPhaseName = "research" | "planning";

/**
 * All possible phase names across entity types.
 *
 * @category Phase Tracking
 */
export type PhaseName =
  | "research"
  | "planning"
  | "implementation"
  | "testing";

/**
 * Research phase tracking.
 *
 * Tracks whether research has been conducted and if adequate
 * research artifacts are attached to the entity.
 *
 * @category Phase Tracking
 *
 * @example
 * ```typescript
 * const research: ResearchPhase = {
 *   status: "completed",
 *   has_research: true,
 *   research_adequate: true,
 *   research_artifact_ids: ["doc-001", "doc-002"],
 *   completed_at: "2025-01-01T12:00:00Z"
 * };
 * ```
 */
export interface ResearchPhase {
  status: PhaseStatus;
  has_research: boolean;
  research_adequate: boolean;
  research_artifact_ids: string[];
  notes?: string | null;
  completed_at?: ISODateTimeString | null;
}

/**
 * Planning phase tracking.
 *
 * Tracks whether planning has been completed, including
 * acceptance criteria, definition of done, and implementation plan.
 *
 * @category Phase Tracking
 *
 * @example
 * ```typescript
 * const planning: PlanningPhase = {
 *   status: "in_progress",
 *   has_acceptance_criteria: true,
 *   has_definition_of_done: true,
 *   has_implementation_plan: false,
 *   plan_artifact_ids: ["prd-001"]
 * };
 * ```
 */
export interface PlanningPhase {
  status: PhaseStatus;
  has_acceptance_criteria: boolean;
  has_definition_of_done: boolean;
  has_implementation_plan: boolean;
  plan_artifact_ids: string[];
  notes?: string | null;
  completed_at?: ISODateTimeString | null;
}

/**
 * Implementation phase tracking.
 *
 * Tracks the status of implementation work including
 * code changes, PRs, and deployments.
 *
 * @category Phase Tracking
 *
 * @example
 * ```typescript
 * const implementation: ImplementationPhase = {
 *   status: "in_progress",
 *   progress_pct: 75,
 *   has_code_changes: true,
 *   has_pull_request: true,
 *   pr_merged: false,
 *   deployed: false,
 *   pr_urls: ["https://github.com/org/repo/pull/123"],
 *   commit_shas: ["abc123"]
 * };
 * ```
 */
export interface ImplementationPhase {
  status: PhaseStatus;
  progress_pct: number;
  has_code_changes: boolean;
  has_pull_request: boolean;
  pr_merged: boolean;
  deployed: boolean;
  pr_urls: string[];
  commit_shas: string[];
  notes?: string | null;
  started_at?: ISODateTimeString | null;
  completed_at?: ISODateTimeString | null;
}

/**
 * Testing and validation phase tracking.
 *
 * Tracks the status of testing, QA, and validation activities.
 *
 * @category Phase Tracking
 *
 * @example
 * ```typescript
 * const testing: TestingPhase = {
 *   status: "completed",
 *   has_unit_tests: true,
 *   has_integration_tests: true,
 *   has_e2e_tests: false,
 *   tests_passing: true,
 *   coverage_pct: 85.5,
 *   has_manual_qa: true,
 *   qa_approved: true
 * };
 * ```
 */
export interface TestingPhase {
  status: PhaseStatus;
  has_unit_tests: boolean;
  has_integration_tests: boolean;
  has_e2e_tests: boolean;
  tests_passing: boolean;
  coverage_pct?: number | null;
  has_manual_qa: boolean;
  qa_approved: boolean;
  validation_notes?: string | null;
  test_report_url?: string | null;
  started_at?: ISODateTimeString | null;
  completed_at?: ISODateTimeString | null;
}

/**
 * Complete phase tracking for a Task entity.
 *
 * Tasks have all four phases: research, planning, implementation, testing.
 *
 * @category Phase Tracking
 *
 * @example
 * ```typescript
 * const taskPhases: TaskPhaseTracking = {
 *   research: { status: "completed", ... },
 *   planning: { status: "completed", ... },
 *   implementation: { status: "in_progress", ... },
 *   testing: { status: "not_started", ... }
 * };
 * ```
 */
export interface TaskPhaseTracking {
  research: ResearchPhase;
  planning: PlanningPhase;
  implementation: ImplementationPhase;
  testing: TestingPhase;
}

/**
 * Complete phase tracking for a Sprint entity.
 *
 * Sprints have two phases: planning, implementation.
 *
 * @category Phase Tracking
 */
export interface SprintPhaseTracking {
  planning: PlanningPhase;
  implementation: ImplementationPhase;
}

/**
 * Complete phase tracking for a Project entity.
 *
 * Projects have two phases: research, planning.
 *
 * @category Phase Tracking
 */
export interface ProjectPhaseTracking {
  research: ResearchPhase;
  planning: PlanningPhase;
}

/**
 * Generic phase data as returned by the API.
 *
 * @category Phase Tracking
 */
export type PhaseData = Record<string, unknown>;

/**
 * Phase update request payload.
 *
 * @category Phase Tracking
 */
export interface PhaseUpdateRequest {
  status?: PhaseStatus;
  blocked_reason?: string | null;
  skip_reason?: string | null;
  additional_fields?: Record<string, unknown>;
}

/**
 * Block phase request payload.
 *
 * @category Phase Tracking
 */
export interface BlockPhaseRequest {
  blocked_reason?: string | null;
}

/**
 * Skip phase request payload.
 *
 * @category Phase Tracking
 */
export interface SkipPhaseRequest {
  skip_reason?: string | null;
}

/**
 * Single phase response from API.
 *
 * @category Phase Tracking
 */
export interface PhaseResponse {
  phase_name: string;
  status: PhaseStatus;
  data: PhaseData;
}

/**
 * All phases response from API.
 *
 * @category Phase Tracking
 */
export interface PhasesResponse {
  entity_id: string;
  entity_type: PhaseEntityType;
  phases: Record<string, PhaseData>;
}

/**
 * Phase summary with progress metrics.
 *
 * @category Phase Tracking
 */
export interface PhaseSummaryResponse {
  entity_id: string;
  entity_type: PhaseEntityType;
  current_phase: string | null;
  phases_completed: number;
  phases_total: number;
  completion_pct: number;
  phases: Record<string, PhaseData>;
}

/**
 * Entity found in a specific phase.
 *
 * @category Phase Tracking
 */
export interface EntityInPhaseResponse {
  id: string;
  phase: string;
  status: string;
  phase_data: PhaseData;
}

/**
 * Blocked entity summary.
 *
 * @category Phase Tracking
 */
export interface BlockedEntityResponse {
  entity_type: PhaseEntityType;
  entity_id: string;
  phase: string;
  blocked_reason?: string | null;
}

/**
 * Phase analytics across entities.
 *
 * @category Phase Tracking
 */
export interface PhaseAnalyticsResponse {
  entity_type: PhaseEntityType;
  total_entities: number;
  by_phase: Record<string, Record<string, number>>;
  blocked_count: number;
  average_completion_pct: number;
}

/**
 * Default phases for Task entities.
 *
 * @category Phase Tracking
 */
export const DEFAULT_TASK_PHASES: TaskPhaseTracking = {
  research: {
    status: "not_started",
    has_research: false,
    research_adequate: false,
    research_artifact_ids: [],
  },
  planning: {
    status: "not_started",
    has_acceptance_criteria: false,
    has_definition_of_done: false,
    has_implementation_plan: false,
    plan_artifact_ids: [],
  },
  implementation: {
    status: "not_started",
    progress_pct: 0,
    has_code_changes: false,
    has_pull_request: false,
    pr_merged: false,
    deployed: false,
    pr_urls: [],
    commit_shas: [],
  },
  testing: {
    status: "not_started",
    has_unit_tests: false,
    has_integration_tests: false,
    has_e2e_tests: false,
    tests_passing: false,
    has_manual_qa: false,
    qa_approved: false,
  },
};

/**
 * Default phases for Sprint entities.
 *
 * @category Phase Tracking
 */
export const DEFAULT_SPRINT_PHASES: SprintPhaseTracking = {
  planning: {
    status: "not_started",
    has_acceptance_criteria: false,
    has_definition_of_done: false,
    has_implementation_plan: false,
    plan_artifact_ids: [],
  },
  implementation: {
    status: "not_started",
    progress_pct: 0,
    has_code_changes: false,
    has_pull_request: false,
    pr_merged: false,
    deployed: false,
    pr_urls: [],
    commit_shas: [],
  },
};

/**
 * Default phases for Project entities.
 *
 * @category Phase Tracking
 */
export const DEFAULT_PROJECT_PHASES: ProjectPhaseTracking = {
  research: {
    status: "not_started",
    has_research: false,
    research_adequate: false,
    research_artifact_ids: [],
  },
  planning: {
    status: "not_started",
    has_acceptance_criteria: false,
    has_definition_of_done: false,
    has_implementation_plan: false,
    plan_artifact_ids: [],
  },
};

/**
 * Get valid phase names for an entity type.
 *
 * @param entityType - The type of entity
 * @returns Array of valid phase names for that entity type
 *
 * @category Phase Tracking
 */
export function getPhaseNamesForEntityType(
  entityType: PhaseEntityType
): PhaseName[] {
  switch (entityType) {
    case "task":
      return ["research", "planning", "implementation", "testing"];
    case "sprint":
      return ["planning", "implementation"];
    case "project":
      return ["research", "planning"];
    default:
      return [];
  }
}

/**
 * Check if a phase name is valid for an entity type.
 *
 * @param entityType - The type of entity
 * @param phaseName - The phase name to check
 * @returns True if the phase is valid for the entity type
 *
 * @category Phase Tracking
 */
export function isValidPhaseForEntityType(
  entityType: PhaseEntityType,
  phaseName: string
): boolean {
  const validPhases = getPhaseNamesForEntityType(entityType);
  return validPhases.includes(phaseName as PhaseName);
}

/**
 * Get the next phase name in the lifecycle.
 *
 * @param entityType - The type of entity
 * @param currentPhase - The current phase name
 * @returns The next phase name, or null if at the end
 *
 * @category Phase Tracking
 */
export function getNextPhaseName(
  entityType: PhaseEntityType,
  currentPhase: string
): string | null {
  const phases = getPhaseNamesForEntityType(entityType);
  const currentIndex = phases.indexOf(currentPhase as PhaseName);

  if (currentIndex === -1 || currentIndex === phases.length - 1) {
    return null;
  }

  return phases[currentIndex + 1];
}
