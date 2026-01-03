/**
 * @module Phase Tracking Schemas
 * @description Zod validation schemas for phase tracking types.
 *
 * Provides runtime validation for all phase-related data structures.
 *
 * @packageDocumentation
 */

import { z } from "zod";

// ============================================================================
// PHASE STATUS & ENTITY TYPE SCHEMAS
// ============================================================================

/**
 * Phase status enum schema.
 *
 * @category Phase Tracking
 */
export const phaseStatusSchema = z.enum([
  "not_started",
  "in_progress",
  "completed",
  "skipped",
  "blocked",
]);

/**
 * Entity type schema.
 *
 * @category Phase Tracking
 */
export const phaseEntityTypeSchema = z.enum(["task", "sprint", "project"]);

/**
 * Phase name schema (all possible phases).
 *
 * @category Phase Tracking
 */
export const phaseNameSchema = z.enum([
  "research",
  "planning",
  "implementation",
  "testing",
]);

// ============================================================================
// INDIVIDUAL PHASE SCHEMAS
// ============================================================================

/**
 * ISO datetime validation (permissive for API responses).
 */
const isoDateTime = z
  .string()
  .regex(/^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(\.\d+)?(Z)?$/);

/**
 * Research phase schema.
 *
 * @category Phase Tracking
 */
export const researchPhaseSchema = z.object({
  status: phaseStatusSchema,
  has_research: z.boolean(),
  research_adequate: z.boolean(),
  research_artifact_ids: z.array(z.string()),
  notes: z.string().nullish(),
  completed_at: isoDateTime.nullish(),
});

/**
 * Planning phase schema.
 *
 * @category Phase Tracking
 */
export const planningPhaseSchema = z.object({
  status: phaseStatusSchema,
  has_acceptance_criteria: z.boolean(),
  has_definition_of_done: z.boolean(),
  has_implementation_plan: z.boolean(),
  plan_artifact_ids: z.array(z.string()),
  notes: z.string().nullish(),
  completed_at: isoDateTime.nullish(),
});

/**
 * Implementation phase schema.
 *
 * @category Phase Tracking
 */
export const implementationPhaseSchema = z.object({
  status: phaseStatusSchema,
  progress_pct: z.number().int().min(0).max(100),
  has_code_changes: z.boolean(),
  has_pull_request: z.boolean(),
  pr_merged: z.boolean(),
  deployed: z.boolean(),
  pr_urls: z.array(z.string()),
  commit_shas: z.array(z.string()),
  notes: z.string().nullish(),
  started_at: isoDateTime.nullish(),
  completed_at: isoDateTime.nullish(),
});

/**
 * Testing phase schema.
 *
 * @category Phase Tracking
 */
export const testingPhaseSchema = z.object({
  status: phaseStatusSchema,
  has_unit_tests: z.boolean(),
  has_integration_tests: z.boolean(),
  has_e2e_tests: z.boolean(),
  tests_passing: z.boolean(),
  coverage_pct: z.number().min(0).max(100).nullish(),
  has_manual_qa: z.boolean(),
  qa_approved: z.boolean(),
  validation_notes: z.string().nullish(),
  test_report_url: z.string().nullish(),
  started_at: isoDateTime.nullish(),
  completed_at: isoDateTime.nullish(),
});

// ============================================================================
// COMPOSITE PHASE TRACKING SCHEMAS
// ============================================================================

/**
 * Task phase tracking schema (4 phases).
 *
 * @category Phase Tracking
 */
export const taskPhaseTrackingSchema = z.object({
  research: researchPhaseSchema,
  planning: planningPhaseSchema,
  implementation: implementationPhaseSchema,
  testing: testingPhaseSchema,
});

/**
 * Sprint phase tracking schema (2 phases).
 *
 * @category Phase Tracking
 */
export const sprintPhaseTrackingSchema = z.object({
  planning: planningPhaseSchema,
  implementation: implementationPhaseSchema,
});

/**
 * Project phase tracking schema (2 phases).
 *
 * @category Phase Tracking
 */
export const projectPhaseTrackingSchema = z.object({
  research: researchPhaseSchema,
  planning: planningPhaseSchema,
});

// ============================================================================
// REQUEST/RESPONSE SCHEMAS
// ============================================================================

/**
 * Phase update request schema.
 *
 * @category Phase Tracking
 */
export const phaseUpdateRequestSchema = z.object({
  status: phaseStatusSchema.optional(),
  blocked_reason: z.string().max(500).nullish(),
  skip_reason: z.string().max(500).nullish(),
  additional_fields: z.record(z.unknown()).optional(),
});

/**
 * Block phase request schema.
 *
 * @category Phase Tracking
 */
export const blockPhaseRequestSchema = z.object({
  blocked_reason: z.string().max(500).nullish(),
});

/**
 * Skip phase request schema.
 *
 * @category Phase Tracking
 */
export const skipPhaseRequestSchema = z.object({
  skip_reason: z.string().max(500).nullish(),
});

/**
 * Phase data schema (flexible record).
 *
 * @category Phase Tracking
 */
export const phaseDataSchema = z.record(z.unknown());

/**
 * Single phase response schema.
 *
 * @category Phase Tracking
 */
export const phaseResponseSchema = z.object({
  phase_name: z.string(),
  status: phaseStatusSchema,
  data: phaseDataSchema,
});

/**
 * All phases response schema.
 *
 * @category Phase Tracking
 */
export const phasesResponseSchema = z.object({
  entity_id: z.string(),
  entity_type: phaseEntityTypeSchema,
  phases: z.record(phaseDataSchema),
});

/**
 * Phase summary response schema.
 *
 * @category Phase Tracking
 */
export const phaseSummaryResponseSchema = z.object({
  entity_id: z.string(),
  entity_type: phaseEntityTypeSchema,
  current_phase: z.string().nullable(),
  phases_completed: z.number().int().nonnegative(),
  phases_total: z.number().int().nonnegative(),
  completion_pct: z.number().min(0).max(100),
  phases: z.record(phaseDataSchema),
});

/**
 * Entity in phase response schema.
 *
 * @category Phase Tracking
 */
export const entityInPhaseResponseSchema = z.object({
  id: z.string(),
  phase: z.string(),
  status: z.string(),
  phase_data: phaseDataSchema,
});

/**
 * Blocked entity response schema.
 *
 * @category Phase Tracking
 */
export const blockedEntityResponseSchema = z.object({
  entity_type: phaseEntityTypeSchema,
  entity_id: z.string(),
  phase: z.string(),
  blocked_reason: z.string().nullish(),
});

/**
 * Phase analytics response schema.
 *
 * @category Phase Tracking
 */
export const phaseAnalyticsResponseSchema = z.object({
  entity_type: phaseEntityTypeSchema,
  total_entities: z.number().int().nonnegative(),
  by_phase: z.record(z.record(z.number().int().nonnegative())),
  blocked_count: z.number().int().nonnegative(),
  average_completion_pct: z.number().min(0).max(100),
});

// ============================================================================
// TOOL INPUT SCHEMAS
// ============================================================================

/**
 * Get phases input schema.
 *
 * @category Phase Tracking
 */
export const getPhasesInputSchema = z.object({
  entityType: phaseEntityTypeSchema,
  entityId: z.string().min(1),
});

/**
 * Get phase input schema.
 *
 * @category Phase Tracking
 */
export const getPhaseInputSchema = z.object({
  entityType: phaseEntityTypeSchema,
  entityId: z.string().min(1),
  phaseName: phaseNameSchema,
});

/**
 * Update phase input schema.
 *
 * @category Phase Tracking
 */
export const updatePhaseInputSchema = z.object({
  entityType: phaseEntityTypeSchema,
  entityId: z.string().min(1),
  phaseName: phaseNameSchema,
  update: phaseUpdateRequestSchema,
});

/**
 * Advance phase input schema.
 *
 * @category Phase Tracking
 */
export const advancePhaseInputSchema = z.object({
  entityType: phaseEntityTypeSchema,
  entityId: z.string().min(1),
});

/**
 * Block phase input schema.
 *
 * @category Phase Tracking
 */
export const blockPhaseInputSchema = z.object({
  entityType: phaseEntityTypeSchema,
  entityId: z.string().min(1),
  phaseName: phaseNameSchema,
  blockedReason: z.string().max(500).optional(),
});

/**
 * Unblock phase input schema.
 *
 * @category Phase Tracking
 */
export const unblockPhaseInputSchema = z.object({
  entityType: phaseEntityTypeSchema,
  entityId: z.string().min(1),
  phaseName: phaseNameSchema,
});

/**
 * Skip phase input schema.
 *
 * @category Phase Tracking
 */
export const skipPhaseInputSchema = z.object({
  entityType: phaseEntityTypeSchema,
  entityId: z.string().min(1),
  phaseName: phaseNameSchema,
  skipReason: z.string().max(500).optional(),
});

/**
 * Complete phase input schema.
 *
 * @category Phase Tracking
 */
export const completePhaseInputSchema = z.object({
  entityType: phaseEntityTypeSchema,
  entityId: z.string().min(1),
  phaseName: phaseNameSchema,
});

/**
 * Start phase input schema.
 *
 * @category Phase Tracking
 */
export const startPhaseInputSchema = z.object({
  entityType: phaseEntityTypeSchema,
  entityId: z.string().min(1),
  phaseName: phaseNameSchema,
});

/**
 * Get phase summary input schema.
 *
 * @category Phase Tracking
 */
export const getPhaseSummaryInputSchema = z.object({
  entityType: phaseEntityTypeSchema,
  entityId: z.string().min(1),
});

/**
 * Find by phase input schema.
 *
 * @category Phase Tracking
 */
export const findByPhaseInputSchema = z.object({
  entityType: phaseEntityTypeSchema,
  phaseName: phaseNameSchema,
  status: phaseStatusSchema.optional(),
  limit: z.number().int().positive().max(100).optional(),
});

/**
 * Find blocked entities input schema.
 *
 * @category Phase Tracking
 */
export const findBlockedInputSchema = z.object({
  entityType: phaseEntityTypeSchema,
  limit: z.number().int().positive().max(100).optional(),
});

/**
 * Get phase analytics input schema.
 *
 * @category Phase Tracking
 */
export const getPhaseAnalyticsInputSchema = z.object({
  entityType: phaseEntityTypeSchema,
  limit: z.number().int().positive().max(1000).optional(),
});
