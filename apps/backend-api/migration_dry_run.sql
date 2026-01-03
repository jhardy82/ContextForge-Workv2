INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Generating static SQL
INFO  [alembic.runtime.migration] Will assume transactional DDL.
BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

INFO  [alembic.runtime.migration] Running upgrade  -> v2_0001, Initial Projects Schema (Comprehensive)
-- Running upgrade  -> v2_0001

CREATE TABLE projects (
    id VARCHAR(64) NOT NULL, 
    name VARCHAR(255) NOT NULL, 
    mission TEXT, 
    status VARCHAR(50), 
    owner VARCHAR(100), 
    start_date VARCHAR(20), 
    sprints JSONB DEFAULT '[]' NOT NULL, 
    team_members JSONB DEFAULT '[]' NOT NULL, 
    labels JSONB DEFAULT '[]' NOT NULL, 
    observability_json JSONB DEFAULT '{}' NOT NULL, 
    phases JSONB DEFAULT '{"research": {"status": "not_started", "has_market_research": false, "has_technical_research": false, "research_adequate": false}, "planning": {"status": "not_started", "has_prd": false, "has_architecture": false, "has_roadmap": false}}'::jsonb NOT NULL, 
    pending_reason VARCHAR(500), 
    blocked_reason VARCHAR(500), 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
    PRIMARY KEY (id)
);

CREATE INDEX idx_projects_id ON projects (id);

CREATE INDEX idx_projects_owner ON projects (owner);

CREATE INDEX idx_projects_start_date ON projects (start_date);

CREATE INDEX idx_projects_created_at ON projects (created_at);

CREATE INDEX idx_projects_updated_at ON projects (updated_at);

INSERT INTO alembic_version (version_num) VALUES ('v2_0001') RETURNING alembic_version.version_num;

INFO  [alembic.runtime.migration] Running upgrade v2_0001 -> v2_0002, Initial Sprints Schema (Comprehensive)
-- Running upgrade v2_0001 -> v2_0002

CREATE TABLE sprints (
    id VARCHAR(50) NOT NULL, 
    name VARCHAR(255) NOT NULL, 
    goal TEXT, 
    status VARCHAR(50), 
    start_date VARCHAR(20), 
    end_date VARCHAR(20), 
    primary_project VARCHAR(64), 
    cadence VARCHAR(20), 
    owner VARCHAR(100), 
    tasks JSONB DEFAULT '[]' NOT NULL, 
    imported_tasks JSONB DEFAULT '[]' NOT NULL, 
    velocity_target_points FLOAT, 
    actual_points FLOAT, 
    carried_over_points FLOAT, 
    definition_of_done JSONB DEFAULT '[]' NOT NULL, 
    scope_changes JSONB DEFAULT '[]' NOT NULL, 
    metrics JSONB DEFAULT '{}' NOT NULL, 
    timezone VARCHAR(50), 
    observability JSONB DEFAULT '{}' NOT NULL, 
    phases JSONB DEFAULT '{"planning": {"status": "not_started", "has_sprint_goal": false, "has_capacity_plan": false, "tasks_estimated": false}, "implementation": {"status": "not_started", "progress_pct": 0, "tasks_completed": 0, "tasks_total": 0}}'::jsonb NOT NULL, 
    pending_reason VARCHAR(500), 
    blocked_reason VARCHAR(500), 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(primary_project) REFERENCES projects (id) ON DELETE CASCADE
);

CREATE INDEX idx_sprints_id ON sprints (id);

CREATE INDEX idx_sprints_primary_project ON sprints (primary_project);

CREATE INDEX idx_sprints_owner ON sprints (owner);

CREATE INDEX idx_sprints_start_date ON sprints (start_date);

CREATE INDEX idx_sprints_end_date ON sprints (end_date);

CREATE INDEX idx_sprints_project_status ON sprints (primary_project, status);

CREATE INDEX idx_sprints_created_at ON sprints (created_at);

CREATE INDEX idx_sprints_updated_at ON sprints (updated_at);

UPDATE alembic_version SET version_num='v2_0002' WHERE alembic_version.version_num = 'v2_0001';

INFO  [alembic.runtime.migration] Running upgrade v2_0002 -> v2_0003, Initial Tasks Schema (Comprehensive)
-- Running upgrade v2_0002 -> v2_0003

CREATE TABLE tasks (
    id VARCHAR(50) NOT NULL, 
    title VARCHAR(255) NOT NULL, 
    description TEXT, 
    status VARCHAR(50), 
    priority VARCHAR(20), 
    owner VARCHAR(100) NOT NULL, 
    primary_project VARCHAR(64) NOT NULL, 
    primary_sprint VARCHAR(50) NOT NULL, 
    summary TEXT NOT NULL, 
    assignees JSONB DEFAULT '[]' NOT NULL, 
    severity VARCHAR(20), 
    related_projects JSONB DEFAULT '[]' NOT NULL, 
    related_sprints JSONB DEFAULT '[]' NOT NULL, 
    estimate_points FLOAT, 
    actual_time_hours FLOAT, 
    due_at TIMESTAMP WITH TIME ZONE, 
    parents JSONB DEFAULT '[]' NOT NULL, 
    depends_on JSONB DEFAULT '[]' NOT NULL, 
    blocks JSONB DEFAULT '[]' NOT NULL, 
    blockers JSONB DEFAULT '[]' NOT NULL, 
    acceptance_criteria JSONB DEFAULT '[]' NOT NULL, 
    definition_of_done JSONB DEFAULT '[]' NOT NULL, 
    quality_gates JSONB DEFAULT '{}' NOT NULL, 
    verification JSONB DEFAULT '{}' NOT NULL, 
    actions_taken JSONB DEFAULT '[]' NOT NULL, 
    related_links JSONB DEFAULT '[]' NOT NULL, 
    shape VARCHAR(20), 
    stage VARCHAR(50), 
    work_type VARCHAR(50), 
    work_stream VARCHAR(100), 
    business_value_score INTEGER, 
    cost_of_delay_score INTEGER, 
    automation_candidate BOOLEAN DEFAULT 'false', 
    cycle_time_days FLOAT, 
    risks JSONB DEFAULT '[]' NOT NULL, 
    observability JSONB DEFAULT '{}' NOT NULL, 
    phases JSONB DEFAULT '{"research": {"status": "not_started", "has_research": false, "research_adequate": false}, "planning": {"status": "not_started", "has_acceptance_criteria": false, "has_definition_of_done": false}, "implementation": {"status": "not_started", "progress_pct": 0, "has_code_changes": false}, "testing": {"status": "not_started", "has_unit_tests": false, "tests_passing": false}}'::jsonb NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(primary_project) REFERENCES projects (id) ON DELETE CASCADE, 
    FOREIGN KEY(primary_sprint) REFERENCES sprints (id) ON DELETE CASCADE
);

CREATE INDEX idx_tasks_id ON tasks (id);

CREATE INDEX idx_tasks_status ON tasks (status);

CREATE INDEX idx_tasks_priority ON tasks (priority);

CREATE INDEX idx_tasks_owner ON tasks (owner);

CREATE INDEX idx_tasks_primary_project ON tasks (primary_project);

CREATE INDEX idx_tasks_primary_sprint ON tasks (primary_sprint);

CREATE INDEX idx_tasks_status_priority ON tasks (status, priority);

CREATE INDEX idx_tasks_project_status ON tasks (primary_project, status);

CREATE INDEX idx_tasks_sprint_status ON tasks (primary_sprint, status);

CREATE INDEX idx_tasks_created_at ON tasks (created_at);

CREATE INDEX idx_tasks_updated_at ON tasks (updated_at);

CREATE INDEX idx_tasks_assignees_gin ON tasks USING gin (assignees);

CREATE INDEX idx_tasks_labels_gin ON tasks USING gin (related_links);

CREATE INDEX idx_tasks_depends_on_gin ON tasks USING gin (depends_on);

CREATE INDEX idx_tasks_blocks_gin ON tasks USING gin (blocks);

UPDATE alembic_version SET version_num='v2_0003' WHERE alembic_version.version_num = 'v2_0002';

INFO  [alembic.runtime.migration] Running upgrade v2_0003 -> v2_0004, Initial ActionLists Schema (Comprehensive)
-- Running upgrade v2_0003 -> v2_0004

CREATE TABLE action_lists (
    id VARCHAR(50) NOT NULL, 
    title VARCHAR(255) NOT NULL, 
    owner VARCHAR(100), 
    status VARCHAR(50) DEFAULT 'active' NOT NULL, 
    project_id VARCHAR(64), 
    sprint_id VARCHAR(50), 
    items JSONB DEFAULT '[]' NOT NULL, 
    tags JSONB DEFAULT '[]' NOT NULL, 
    geometry_shape VARCHAR(20), 
    priority VARCHAR(20), 
    due_date TIMESTAMP WITH TIME ZONE, 
    notes TEXT, 
    evidence_refs JSONB DEFAULT '[]' NOT NULL, 
    extra_metadata JSONB DEFAULT '{}' NOT NULL, 
    parent_deleted_at TIMESTAMP WITH TIME ZONE, 
    parent_deletion_note JSONB DEFAULT '{}' NOT NULL, 
    completed_at TIMESTAMP WITH TIME ZONE, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE SET NULL, 
    FOREIGN KEY(sprint_id) REFERENCES sprints (id) ON DELETE SET NULL
);

CREATE INDEX idx_action_lists_id ON action_lists (id);

CREATE INDEX idx_action_lists_owner ON action_lists (owner);

CREATE INDEX idx_action_lists_sprint_id ON action_lists (sprint_id);

CREATE INDEX idx_action_lists_project_id ON action_lists (project_id);

CREATE INDEX idx_action_lists_project_status ON action_lists (project_id, status);

CREATE INDEX idx_action_lists_created_at ON action_lists (created_at);

CREATE INDEX idx_action_lists_updated_at ON action_lists (updated_at);

CREATE INDEX idx_action_lists_tags_gin ON action_lists USING gin (tags);

UPDATE alembic_version SET version_num='v2_0004' WHERE alembic_version.version_num = 'v2_0003';

INFO  [alembic.runtime.migration] Running upgrade v2_0004 -> v2_0005, Initial StateStore Schema (Comprehensive)
-- Running upgrade v2_0004 -> v2_0005

CREATE TABLE conversation_sessions (
    id VARCHAR(100) NOT NULL, 
    title VARCHAR(255) NOT NULL, 
    status VARCHAR(20) DEFAULT 'active' NOT NULL, 
    agent_type VARCHAR(50) DEFAULT 'claude', 
    worktree VARCHAR(100), 
    project_id VARCHAR(50), 
    sprint_id VARCHAR(50), 
    turn_count INTEGER DEFAULT '0' NOT NULL, 
    token_estimate INTEGER DEFAULT '0' NOT NULL, 
    summary TEXT, 
    tags JSONB DEFAULT '[]' NOT NULL, 
    extra_metadata JSONB DEFAULT '{}' NOT NULL, 
    plan_ids JSONB DEFAULT '[]' NOT NULL, 
    checklist_ids JSONB DEFAULT '[]' NOT NULL, 
    task_ids JSONB DEFAULT '[]' NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    completed_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id)
);

CREATE INDEX idx_conv_sessions_status ON conversation_sessions (status);

CREATE INDEX idx_conv_sessions_project ON conversation_sessions (project_id);

CREATE INDEX idx_conv_sessions_created ON conversation_sessions (created_at);

CREATE TABLE conversation_turns (
    id VARCHAR(100) NOT NULL, 
    conversation_id VARCHAR(100) NOT NULL, 
    sequence INTEGER NOT NULL, 
    role VARCHAR(20) NOT NULL, 
    content TEXT NOT NULL, 
    content_type VARCHAR(20) DEFAULT 'text' NOT NULL, 
    tool_calls JSONB DEFAULT '[]' NOT NULL, 
    tool_results JSONB DEFAULT '[]' NOT NULL, 
    token_count INTEGER DEFAULT '0' NOT NULL, 
    is_summary BOOLEAN DEFAULT 'false' NOT NULL, 
    extra_metadata JSONB DEFAULT '{}' NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id)
);

CREATE INDEX idx_conv_turns_conv_id ON conversation_turns (conversation_id);

CREATE INDEX idx_conv_turns_conv_seq ON conversation_turns (conversation_id, sequence);

CREATE TABLE plans (
    id VARCHAR(100) NOT NULL, 
    title VARCHAR(255) NOT NULL, 
    description TEXT, 
    status VARCHAR(20) DEFAULT 'draft' NOT NULL, 
    steps JSONB DEFAULT '[]' NOT NULL, 
    conversation_id VARCHAR(100), 
    project_id VARCHAR(50), 
    sprint_id VARCHAR(50), 
    tags JSONB DEFAULT '[]' NOT NULL, 
    extra_metadata JSONB DEFAULT '{}' NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    approved_at TIMESTAMP WITH TIME ZONE, 
    completed_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id)
);

CREATE INDEX idx_plans_status ON plans (status);

CREATE INDEX idx_plans_conv ON plans (conversation_id);

CREATE INDEX idx_plans_project ON plans (project_id);

CREATE TABLE checklists (
    id VARCHAR(100) NOT NULL, 
    title VARCHAR(255) NOT NULL, 
    description TEXT, 
    status VARCHAR(20) DEFAULT 'active' NOT NULL, 
    items JSONB DEFAULT '[]' NOT NULL, 
    conversation_id VARCHAR(100), 
    plan_id VARCHAR(100), 
    task_id VARCHAR(50), 
    is_template BOOLEAN DEFAULT 'false' NOT NULL, 
    template_id VARCHAR(100), 
    tags JSONB DEFAULT '[]' NOT NULL, 
    extra_metadata JSONB DEFAULT '{}' NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    completed_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id)
);

CREATE INDEX idx_checklists_status ON checklists (status);

CREATE INDEX idx_checklists_template ON checklists (is_template);

CREATE INDEX idx_checklists_task ON checklists (task_id);

CREATE INDEX idx_checklists_plan ON checklists (plan_id);

UPDATE alembic_version SET version_num='v2_0005' WHERE alembic_version.version_num = 'v2_0004';

COMMIT;

