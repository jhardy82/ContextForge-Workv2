import { Task } from '@/types/objects';
import { v4 as uuidv4 } from 'uuid';

export const generateTask = (overrides: Partial<Task> = {}): Task => {
  const titles = [
    "Refactor legacy auth module",
    "Implement 64-field schema",
    "Design new dashboard widgets",
    "Optimize database queries",
    "Fix CORS preflight issues",
    "Update documentation pipeline",
    "Migrate to React 19",
    "Conduct security audit",
  ];

  const types = ['feature', 'bug', 'chore', 'story', 'subtask'] as const;
  const statuses = ['todo', 'in_progress', 'review', 'done'] as const;
  const priorities = ['critical', 'high', 'medium', 'low'] as const;

  const id = overrides.id || uuidv4();
  const created = new Date().toISOString();

  return {
    // 1. Identity
    id,
    task_id: `TASK-${Math.floor(Math.random() * 1000)}`,
    title: overrides.title || titles[Math.floor(Math.random() * titles.length)],
    description: overrides.description || "Auto-generated task description for testing.",
    task_type: overrides.task_type || types[Math.floor(Math.random() * types.length)],

    // 2. Status
    status: overrides.status || statuses[Math.floor(Math.random() * statuses.length)],
    priority: overrides.priority || priorities[Math.floor(Math.random() * priorities.length)],
    severity: 'major',
    health: 'on_track',
    risk_level: 'low',
    complexity: 'm',
    effort_estimate: 5,

    // 3. Relationships
    parent_task_id: null,
    epic_id: null,
    sprint_id: null,
    project_id: null,
    dependencies: [],
    related_tasks: [],

    // 4. People
    assignee: "user-1",
    created_by: "system",
    reporter: "system",
    stakeholders: [],

    // 5. Temporal
    created_at: created,
    updated_at: created,
    start_date: null,
    due_date: new Date(Date.now() + 86400000 * 7).toISOString(), // +7 days
    completed_at: null,
    estimated_hours: 8,
    actual_hours: 0,
    remaining_hours: 8,

    // 6. Business
    business_value: 80,
    roi_score: null,
    customer_impact: 'medium',
    strategic_alignment: 8,
    motivational_context: "Critical for Q4 launch",
    success_criteria: ["Passes all unit tests", "Client sign-off"],
    acceptance_criteria: ["Given X, When Y, Then Z"],
    definition_of_done: ["Code reviewed", "Merged to main"],

    // 7. Technical
    technical_scope: "Frontend and Backend",
    integration_points: ["API v2", "AuthZ Service"],
    deployment_env: 'all',
    service_topology: ["web-client", "api-gateway"],
    performance_targets: "< 100ms latency",
    algorithm_notes: null,
    data_structures: null,
    tech_debt_score: 2,
    refactor_candidate: false,
    deprecation_status: false,

    // 8. Quality
    test_coverage: 0,
    security_audit_status: 'pending',
    accessibility_compliant: true,
    evidence_bundle_hash: null,
    validation_status: 'unvalidated',
    stability_score: 100,
    completeness_pct: 0,
    quality_gate_status: 'open',

    // 9. COF Dimensions
    cof_motivational: 5,
    cof_relational: 5,
    cof_situational: 5,
    cof_narrative: "Part of the greater modernization arc.",
    cof_sacred_geometry: null,
    cof_temporal: 5,
    cof_spatial: 5,
    cof_holistic: 5,

    // Legacy
    tags: ["generated"],

    ...overrides
  };
};

export const generateTaskTree = (count: number = 10): Task[] => {
    return Array.from({ length: count }).map(() => generateTask());
};
