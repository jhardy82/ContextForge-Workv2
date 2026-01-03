/**
 * @module Core Types
 * @description Core type definitions for the TaskMan MCP Server.
 * These types define the domain model for projects, sprints, tasks, and action lists.
 * 
 * @packageDocumentation
 */

/**
 * Represents the result of an operation that can either succeed or fail.
 * 
 * @typeParam T - The type of the success value
 * @typeParam E - The type of the error (defaults to Error)
 * 
 * @example
 * ```typescript
 * const success: Result<number> = { ok: true, value: 42 };
 * const failure: Result<number> = { ok: false, error: new Error("Failed") };
 * ```
 */
export type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

/** UUID string type for unique identifiers */
export type UUID = string;

/** ISO 8601 date string (YYYY-MM-DD) */
export type ISODateString = string;

/** ISO 8601 datetime string with timezone */
export type ISODateTimeString = string;

/**
 * Status values for projects.
 * 
 * @category Core Types
 * 
 * @example
 * ```typescript
 * const status: ProjectStatus = ProjectStatus.Active;
 * ```
 */
export enum ProjectStatus {
  /** Project is currently active and accepting work */
  Active = "active",
  /** Project is inactive/paused */
  Inactive = "inactive",
}

/**
 * Status values for sprints.
 * 
 * @category Core Types
 * 
 * @example
 * ```typescript
 * const status: SprintStatus = SprintStatus.Active;
 * ```
 */
export enum SprintStatus {
  /** Sprint is planned but not yet started */
  Planned = "planned",
  /** Sprint is currently in progress */
  Active = "active",
  /** Sprint has been completed */
  Completed = "completed",
  /** Sprint was cancelled */
  Cancelled = "cancelled",
}

/**
 * Status values for tasks.
 * 
 * @category Core Types
 * 
 * @example
 * ```typescript
 * const status: TaskStatus = TaskStatus.InProgress;
 * ```
 */
export enum TaskStatus {
  /** Task is planned for future work */
  Planned = "planned",
  /** Task is newly created */
  New = "new",
  /** Task is pending assignment or action */
  Pending = "pending",
  /** Task is actively being worked on */
  InProgress = "in_progress",
  /** Task has been completed */
  Completed = "completed",
  /** Task is blocked by dependencies or issues */
  Blocked = "blocked",
  /** Task was cancelled */
  Cancelled = "cancelled",
}

/**
 * Types of work items. Supports various agile methodologies.
 * 
 * @category Core Types
 * 
 * @example
 * ```typescript
 * const type: WorkType = WorkType.Story;
 * ```
 */
export enum WorkType {
  /** Generic task */
  Task = "task",
  /** Large body of work (Epic) */
  Epic = "epic",
  /** User story */
  Story = "story",
  /** Bug/defect fix */
  Bug = "bug",
  /** New feature development */
  Feature = "feature",
  /** Research/investigation spike */
  Spike = "spike",
}

/**
 * Priority levels for tasks.
 * 
 * @category Core Types
 * 
 * @example
 * ```typescript
 * const priority: TaskPriority = TaskPriority.High;
 * ```
 */
export enum TaskPriority {
  /** Low priority - can be deferred */
  Low = "low",
  /** Medium priority - normal workflow */
  Medium = "medium",
  /** High priority - should be addressed soon */
  High = "high",
  /** Critical priority - requires immediate attention */
  Critical = "critical",
}

/**
 * Sacred Geometry shapes for ContextForge workflow visualization.
 * Each shape represents a fundamental pattern in work and development.
 *
 * The five shapes form a vocabulary for categorizing and visualizing work:
 * - **Circle**: Complete, holistic work (full features, releases)
 * - **Triangle**: Foundational work that others build upon (architecture, schemas)
 * - **Spiral**: Iterative improvement work (optimization, refactoring)
 * - **Pentagon**: Coordinated work balancing multiple concerns (integrations)
 * - **Fractal**: Modular, recursive work (component libraries, hierarchies)
 *
 * @category Sacred Geometry
 * @see {@link ShapeStage} for lifecycle stages within each shape
 * @see docs/sacred-geometry-guide.md for complete documentation
 *
 * @example
 * ```typescript
 * // Assign geometry to a task
 * const task = {
 *   title: "Build caching layer",
 *   geometry_shape: GeometryShape.Spiral,  // Will iterate and improve
 *   shape_stage: ShapeStage.Foundation,    // Starting phase
 * };
 * ```
 */
export enum GeometryShape {
  /** Circle - Completeness and closure. Use for self-contained, holistic work. */
  Circle = "Circle",
  /** Triangle - Stability and foundation. Use for work that others build upon. */
  Triangle = "Triangle",
  /** Spiral - Iterative improvement. Use for work that improves over cycles. */
  Spiral = "Spiral",
  /** Pentagon - Harmony and balance. Use for coordinated, multi-concern work. */
  Pentagon = "Pentagon",
  /** Fractal - Modularity and recursion. Use for self-similar, modular patterns. */
  Fractal = "Fractal",
}

/**
 * Lifecycle stages within a sacred geometry shape.
 *
 * Each shape progresses through three stages representing the natural
 * evolution of work from inception to completion:
 *
 * 1. **Foundation**: Initial setup, planning, scaffolding
 * 2. **Growth**: Active development, building core functionality
 * 3. **Optimization**: Refinement, polish, performance tuning
 *
 * @category Sacred Geometry
 * @see {@link GeometryShape} for the five geometry patterns
 * @see docs/sacred-geometry-guide.md for complete documentation
 *
 * @example
 * ```typescript
 * // Progress a task through stages
 * await updateTask(taskId, { shape_stage: ShapeStage.Growth });
 * // Later...
 * await updateTask(taskId, { shape_stage: ShapeStage.Optimization });
 * ```
 */
export enum ShapeStage {
  /** Foundation - Initial setup, groundwork, planning phase */
  Foundation = "foundation",
  /** Growth - Active development, building core functionality */
  Growth = "growth",
  /** Optimization - Refinement, polish, performance tuning */
  Optimization = "optimization",
}

/**
 * Status values for action lists.
 * 
 * @category Core Types
 */
export enum ActionListStatus {
  Planned = "planned",
  New = "new",
  Pending = "pending",
  Active = "active",
  InProgress = "in_progress",
  Blocked = "blocked",
  Completed = "completed",
  Archived = "archived",
  Cancelled = "cancelled",
}

export enum ActionListPriority {
  Low = "low",
  Medium = "medium",
  High = "high",
  Critical = "critical",
}

export enum Severity {
  Low = "low",
  Medium = "medium",
  High = "high",
  Critical = "critical",
}

export enum RiskLevel {
  Low = "low",
  Medium = "medium",
  High = "high",
  Critical = "critical",
}

export enum ValidationState {
  Pending = "pending",
  InProgress = "in_progress",
  Passed = "passed",
  Failed = "failed",
}

export enum Health {
  Excellent = "excellent",
  Good = "good",
  Fair = "fair",
  Poor = "poor",
  Critical = "critical",
}

export interface ProjectAttributes {
  name: string;
  description?: string | null;
  status?: ProjectStatus;
}

export interface ProjectRecord extends ProjectAttributes {
  id: string;
  created_at: ISODateTimeString;
  updated_at: ISODateTimeString;
}

export interface ProjectAnalyticsProject {
  id: string;
  name: string;
  status: string;
  description?: string | null;
  owner?: string | null;
  created_at: ISODateTimeString;
  updated_at?: ISODateTimeString;
  [key: string]: unknown;
}

export interface ProjectAnalyticsTaskStatistics {
  total: number;
  completed: number;
  in_progress: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  completion_percentage: number;
  [key: string]: unknown;
}

export interface ProjectAnalyticsSprintStatistics {
  total: number;
  active: number;
  completed: number;
  planned: number;
  [key: string]: unknown;
}

export interface ProjectAnalytics {
  project: ProjectAnalyticsProject;
  task_statistics: ProjectAnalyticsTaskStatistics;
  sprint_statistics?: ProjectAnalyticsSprintStatistics | null;
  [key: string]: unknown;
}

export interface SprintAttributes {
  name: string;
  description?: string | null;
  status?: SprintStatus;
  project_id: string;
  start_date?: ISODateTimeString | null;
  end_date?: ISODateTimeString | null;
  actual_start_date?: ISODateTimeString | null;
  actual_end_date?: ISODateTimeString | null;
  capacity_points?: number | null;
  committed_points?: number | null;
  completed_points?: number | null;
  velocity?: number | null;
  goals?: string[] | null;
  retrospective_notes?: string | null;
}

export interface SprintRecord extends SprintAttributes {
  id: string;
  created_at: ISODateTimeString;
  updated_at: ISODateTimeString;
}

export interface TaskAttributes {
  title: string;
  description?: string | null;
  status?: TaskStatus;
  work_type?: WorkType;
  priority?: TaskPriority | null;
  owner?: string | null;
  tags?: string[] | null;
  assignee?: string | null;
  assignees?: string[] | null;
  deleted_at?: ISODateTimeString | null;
  parent_task_id?: string | null;
  subtasks?: string[] | null;
  attachments?: string[] | null;
  watchers?: string[] | null;
  estimated_hours?: number | null;
  actual_hours?: number | null;
  phases?: Record<string, unknown> | null;
  due_date?: ISODateTimeString | null;
  geometry_shape?: GeometryShape | null;
  shape_stage?: ShapeStage | null;
  project_id: string;
  sprint_id?: string | null;
  summary?: string | null;
  completion_notes?: string | null;
  velocity_points?: number | null;
  build_manifest?: string | null;
  severity?: Severity | null;
  estimate_points?: number | null;
  done_date?: ISODateTimeString | null;
  depends_on?: string[] | null;
  blocks?: string[] | null;
  risk_notes?: string | null;
  correlation_hint?: string | null;
  schema_version?: string | null;
  batch_id?: string | null;
  last_health?: Health | null;
  last_heartbeat_utc?: ISODateTimeString | null;
  target_date?: ISODateTimeString | null;
  audit_tag?: string | null;
  task_sequence?: number | null;
  critical_path?: boolean | null;
  risk_level?: RiskLevel | null;
  mitigation_status?: string | null;
  origin_source?: string | null;
  load_group?: string | null;
  agent_id?: string | null;
  content_hash?: string | null;
  eff_priority?: string | null;
  verification_requirements?: string | null;
  validation_state?: ValidationState | null;
  context_objects?: string[] | null;
  context_dimensions?: string[] | null;
  evidence_required?: boolean | null;
  evidence_emitted?: boolean | null;
  execution_trace_log?: Record<string, unknown> | null;
  notes?: string | null;
  aar_count?: number | null;
  last_aar_utc?: ISODateTimeString | null;
  misstep_count?: number | null;
  last_misstep_utc?: ISODateTimeString | null;
  actual_minutes?: number | null;
  correlation_id?: UUID | null;
}

export interface TaskCreate extends TaskAttributes {}

export interface TaskUpdate
  extends Partial<Omit<TaskAttributes, "title" | "project_id">> {
  title?: string | null;
  project_id?: string | null;
}

export interface TaskRecord extends TaskAttributes {
  id: string;
  status: TaskStatus;
  work_type: WorkType;
  priority: TaskPriority | null | undefined;
  created_at: ISODateTimeString;
  updated_at: ISODateTimeString;
}

export type TelemetryOutcome = "success" | "conflict" | "error";

export interface ConcurrencyMeta {
  token?: string | null;
  etag?: string | null;
  version?: string | null;
  updated_at?: ISODateTimeString | null;
  updated_by?: string | null;
}

export interface TaskComment {
  id: string;
  message: string;
  author?: string | null;
  created_at: ISODateTimeString;
  updated_at?: ISODateTimeString | null;
  tags?: string[] | null;
}

export interface TaskBlocker {
  id: string;
  description: string;
  severity?: Severity | null;
  status?: string | null;
  created_at: ISODateTimeString;
  resolved_at?: ISODateTimeString | null;
  external_reference?: string | null;
  linked_task_id?: string | null;
}

export interface TaskChecklistItem {
  id: string;
  text: string;
  completed?: boolean | null;
  completed_at?: ISODateTimeString | null;
  assignee?: string | null;
  due_date?: ISODateTimeString | null;
  order?: number | null;
  metadata?: Record<string, unknown> | null;
}

export interface TaskHoursLog {
  id: string;
  task_id: string;
  minutes: number;
  logged_at: ISODateTimeString;
  agent_id?: string | null;
  note?: string | null;
  phase?: string | null;
}

export interface TaskTelemetry {
  operation_id: UUID;
  tool_name: string;
  task_id?: string | null;
  started_at: ISODateTimeString;
  finished_at: ISODateTimeString;
  latency_ms: number;
  status_code?: number | null;
  outcome: TelemetryOutcome;
  request_id?: string | null;
  correlation_id?: UUID | null;
  error_code?: string | null;
  retries?: number | null;
}

export interface TaskMutationResult {
  task: TaskRecord;
  concurrency?: ConcurrencyMeta | null;
  telemetry?: TaskTelemetry | null;
  comments?: TaskComment[] | null;
  blockers?: TaskBlocker[] | null;
  checklist?: TaskChecklistItem[] | null;
  hours?: TaskHoursLog[] | null;
}

export interface ActionListItem {
  id?: string;
  text: string;
  completed?: boolean;
  order?: number;
}

export interface ActionListAttributes {
  title: string;
  description?: string | null; // Added to match backend API
  project_id?: string | null;
  sprint_id?: string | null;
  task_id?: string | null;
  status?: ActionListStatus | null;
  priority?: ActionListPriority | null;
  notes?: string | null;
  items?: ActionListItem[] | null;
  metadata?: Record<string, unknown> | null;
}

export interface ActionListRecord extends ActionListAttributes {
  id: string;
}

export interface ConfigItemAttributes {
  key: string;
  type: string;
  version?: string | null;
  related_task_id?: string | null;
  metadata?: Record<string, unknown> | null;
}

export interface ConfigItemRecord extends ConfigItemAttributes {
  id: string;
}
