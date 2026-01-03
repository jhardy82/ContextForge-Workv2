# ContextForge Foundation - Complete Reference

**Version**: 3.0.0 (MVP v3.0)
**Purpose**: Comprehensive ContextForge philosophical and technical foundation
**Status**: APPROVED
**Authority**: ContextForge Work Codex v1.2 + MVP v3.0 Package

---

## Document Purpose

This is the **complete reference** for ContextForge Work foundations. Use for:
- Deep understanding of Work Codex principles
- Sacred Geometry pattern validation
- UCL compliance enforcement
- PAOAL execution guidance
- Complexity-based workflow selection
- MCP tool strategy
- Evidence bundle creation

**For quick reference**: See `copilot-instructions.md`
**For specialized topics**: See domain-specific instruction files

---

## ContextForge Work Codex - 11 Principles

### Preface

ContextForge isn't just a toolset; it's a discipline. It teaches us that context defines action, and that every system reflects the order—or disorder—of its makers. Technology is built on mathematics, but guided by human values. This Codex captures both.

---

### Principle 1: Trust Nothing, Verify Everything

**Core Tenet**: Evidence is the closing loop of trust. Logs and tests ground belief.

**Philosophy**: In professional environments, assumptions compound into catastrophic failures. Every claim must be verified, every assertion proven, every state change logged.

**Application**:
- All code changes require tests
- All decisions require evidence bundles
- All state mutations require structured logs
- Sacred Geometry gates validate completeness

**Example**:
```python
# ❌ Bad - assertion without evidence
def transfer_funds(amount):
    return "Transfer successful"

# ✅ Good - evidence-based with verification
def transfer_funds(amount: Decimal) -> TransferResult:
    """Transfer funds with complete audit trail."""
    if amount <= 0:
        raise ValueError("Amount must be positive")
    
    logger.info("transfer_initiated", amount=str(amount))
    
    result = db.execute_transfer(amount)
    
    if not result.success:
        logger.error("transfer_failed", reason=result.error)
        raise TransferError(result.error)
    
    logger.info("transfer_completed", 
                transaction_id=result.id,
                amount=str(amount),
                balance_after=str(result.new_balance))
    
    return result
```

**Work Codex Integration**:
- Combines with **Logs First** (#3) - evidence lives in logs
- Supports **Sacred Geometry Circle gate** - completeness requires evidence
- Enables **UCL Rule 3** - complete evidence required

---

### Principle 2: Workspace First

**Core Tenet**: Begin with what exists; build outward only when necessary.

**Philosophy**: Duplication is waste. Before creating new code, search existing. Before implementing new patterns, verify none exist. The workspace is your first resource.

**Application**:
- Search codebase before writing new functions
- Check existing patterns before designing new ones
- Query agent memory before repeating work
- Review past decisions (ADRs) before making new ones

**Example**:
```bash
# Before implementing password reset:
#search/codebase password reset
#search/codebase email sending

# Check if similar functionality exists:
grep -r "reset_password" src/
grep -r "send_email" src/

# Query past lessons:
# Use agent-memory to check if password reset has been attempted before
```

**Work Codex Integration**:
- Prevents violations of **Sacred Geometry Fractal gate** - inconsistent patterns
- Supports **Iteration is Sacred** (#8) - build on previous work
- Aligns with **Leave Things Better** (#4) - enhance rather than duplicate

---

### Principle 3: Logs First

**Core Tenet**: Truth lives in records, not assumptions.

**Philosophy**: Without logs, debugging is archaeology. With logs, it's forensics. Structured logging is not optional—it's the foundation of operational excellence.

**Application**:
- Emit structured logs at decision points
- Log state changes with before/after values
- Capture failures with complete context
- Use PAOAL Log phase for evidence generation

**Minimum Event Set** (from Work Codex):
1. `session_start` - Session initialization
2. `task_start` - Unit of work begins
3. `decision` - Branching/guard outcomes
4. `artifact_touch_batch` - Read operations
5. `artifact_emit` - Created/modified artifacts
6. `warning`/`error` - Structured errors
7. `task_end` - With outcome and duration
8. `session_summary` - Aggregated counts

**Coverage Target**: ≥90% of execution paths

**Example**:
```python
from python.services.unified_logger import logger

# Decision point
logger.info("decision",
            action="user_authentication",
            result="success" if user else "not_found",
            user_id=user_id if user else None)

# State change
logger.info("task_update",
            task_id=task.id,
            changes={"status": {"old": old_status, "new": new_status}},
            persisted_via="db")

# Evidence generation
logger.info("artifact_emit",
            path="reports/analysis.json",
            hash=sha256_hash,
            size=file_size,
            kind="analysis_report")
```

**Work Codex Integration**:
- Foundation for **Trust Nothing, Verify Everything** (#1)
- Enables **Sacred Geometry Spiral gate** - learning captured
- Required for **UCL Rule 3** - complete evidence

---

### Principle 4: Leave Things Better

**Core Tenet**: Every action should enrich the system for those who follow.

**Philosophy**: The Boy Scout Rule applied to software: leave the codebase cleaner than you found it. Fix technical debt opportunistically. Document discoveries. Share knowledge.

**Application**:
- Fix bugs while implementing features
- Refactor while changing code
- Add tests for untested code
- Document unclear behavior
- Extract reusable patterns

**Example**:
```python
# While implementing feature, also:
# 1. Fix nearby bug
# 2. Add missing docstring
# 3. Improve error handling

async def create_user(request: CreateUserRequest) -> User:
    """Create user with validation and audit logging.
    
    Args:
        request: Validated user creation parameters
        
    Returns:
        Created user instance
        
    Raises:
        ConflictError: If email already exists
        ValidationError: If password doesn't meet requirements
        
    Note:
        Password strength validated against OWASP standards.
        Email uniqueness checked atomically to prevent races.
    """
    # Feature implementation
    # + Bug fix: Added atomic email uniqueness check
    # + Improvement: Added password strength validation
    # + Documentation: Explained OWASP compliance
```

**Work Codex Integration**:
- Drives **Sacred Geometry Spiral gate** - continuous improvement
- Supports **Iteration is Sacred** (#8) - incremental enhancement
- Enables **Fractal gate** - consistent quality across scales

---

### Principle 5: Fix the Root, Not the Symptom

**Core Tenet**: Problems repeat until addressed at the source.

**Philosophy**: Symptoms are visible; root causes are hidden. Patch a symptom and it reappears. Fix the root and entire classes of bugs disappear.

**Application**:
- Use debugger to trace to root cause
- Analyze patterns, not instances
- Address systemic issues, not point failures
- Design out failure modes

**Example**:
```python
# ❌ Symptom fix - N+1 query problem
def get_tasks_with_users():
    tasks = db.query(Task).all()
    for task in tasks:
        task.user = db.query(User).get(task.user_id)  # N queries!
    return tasks

# ✅ Root fix - fix data loading strategy
def get_tasks_with_users():
    """Load tasks with users in single query (eager loading)."""
    return db.query(Task).options(
        joinedload(Task.user)  # 1 query with JOIN
    ).all()
```

**Work Codex Integration**:
- Required for **Sacred Geometry Triangle gate** - stable process
- Supports **Iteration is Sacred** (#8) - don't repeat mistakes
- Enables **vibe_learn** - capture root causes for future prevention

---

### Principle 6: Best Tool for the Context

**Core Tenet**: Every task has its proper tool; discernment is the engineer's art.

**Philosophy**: PowerShell for Windows automation, Python for data processing, SQL for queries, Bash for Linux. Match the tool to the context, not the other way around.

**Application**:
- MCP tools over manual CLI
- VS Code tasks over inline commands
- Scripts with error handling over one-liners
- Strategic tool selection (see tool-usage.instructions.md)

**Tool Selection Matrix**:

| Context | Preferred Tool | Rationale |
|---------|---------------|-----------|
| File operations | MCP (Read, Write, Edit) | Structured, logged, reversible |
| Complex reasoning | sequential-thinking | Systematic PAOAL execution |
| Failure capture | vibe_learn | Pattern extraction + memory |
| Database queries | dbhub MCP | Logged, parameterized, safe |
| Windows automation | PowerShell | Native, best-in-class |
| Data processing | Python | Rich ecosystem, testable |
| Git operations | mcp__github__* | Comprehensive, logged |

**Work Codex Integration**:
- Supports **PAOAL Plan phase** - tool selection upfront
- Aligns with **Sacred Geometry Golden Ratio** - efficiency
- Enables **Trust Nothing, Verify Everything** (#1) - logged tools

---

### Principle 7: Balance Order and Flow

**Core Tenet**: Rigid order calcifies; unchecked flow dissolves. The right path blends both.

**Philosophy**: Systems need structure (order) and adaptability (flow). Too much structure becomes bureaucracy. Too much flexibility becomes chaos. Balance is dynamic.

**Application**:
- Sacred Geometry provides structure (5 gates)
- PAOAL provides flow (adapt phase)
- Plan-based gates (not time-based) allow flexibility
- 3/5 gate minimum balances rigor with pragmatism

**Example**:
```yaml
# Order - Structure provided by gates
sacred_geometry:
  gates_required: 5
  minimum_pass: 3  # Balance - flexibility in pass rate
  enforcement_mode: ADVISORY  # Flow - tune before enforcing

# Flow - Adapt phase allows course correction
paoal:
  plan: "Repository → Service → API"
  act: "Implemented all 3 layers"
  observe: "Tests failing in API layer"
  adapt: "Refactored API to use async/await"  # Flow - adjust approach
  log: "Lesson: Always use async for I/O"
```

**Work Codex Integration**:
- **Sacred Geometry** provides order (5 gates)
- **PAOAL Adapt phase** provides flow (course correction)
- **Plan-based gates** balance both (complete when ready, not on schedule)

---

### Principle 8: Iteration is Sacred

**Core Tenet**: Progress spirals, not straight lines.

**Philosophy**: Perfection is aspirational, not initial. Ship something, learn from it, improve it. Spiral upward through iterations, not leaps.

**Application**:
- Plan-based gates allow iteration within gates
- PAOAL Adapt phase encourages refinement
- Sacred Geometry Spiral gate captures learning
- vibe_learn preserves lessons for next iteration

**Iteration Patterns**:

**Spiral Pattern**:
```
Iteration 1: Basic implementation (pass Circle + Triangle)
Iteration 2: Add learning (pass Spiral)
Iteration 3: Optimize (pass Golden Ratio)
Iteration 4: Refactor for consistency (pass Fractal)
```

**PAOAL Iteration**:
```
Cycle 1: Plan → Act → Observe (tests fail) → Adapt → Log
Cycle 2: Plan (revised) → Act (fix) → Observe (tests pass) → Log
```

**Work Codex Integration**:
- **Sacred Geometry Spiral gate** - learning required
- **PAOAL cycle** - built-in iteration (Observe → Adapt)
- **Plan-based gates** - iterate until criteria met

---

### Principle 9: Context Before Action

**Core Tenet**: To act without context is to cut against the grain.

**Philosophy**: Understand before implementing. Research before building. Plan before acting. Hasty action causes rework.

**Application**:
- PAOAL Plan phase before Act phase
- COF 13D analysis for complex tasks
- Documentation Specialist gathers requirements before Architect designs
- Researcher validates options before selection

**Example** (from MVP v3.0):
```markdown
# Bad - Act without context
User: "Add password reset"
Agent: [Immediately implements password reset]

# Good - Context before action
User: "Add password reset"
@meta-orchestrator: 
  - Routes to @documentation-specialist (gather requirements)
  @documentation-specialist:
    - What's the user flow?
    - Email or SMS?
    - Token expiration time?
    - Security requirements?
  - Routes to @architect (design with context)
  - Routes to @executor (implement with full context)
```

**Work Codex Integration**:
- **PAOAL** enforces this (Plan before Act)
- **COF 13D** provides context dimensions
- **Agent workflow** structures context gathering

---

### Principle 10: Resonance is Proof

**Core Tenet**: Solutions that harmonize across business, user, and technical needs endure.

**Philosophy**: Truth resonates. When business goals, user needs, and technical design all align, the solution is sound. Dissonance indicates problems.

**Application**:
- Check alignment across 3 dimensions:
  1. **Business**: Does it meet business goals?
  2. **User**: Does it serve user needs?
  3. **Technical**: Is it technically sound?
- If any dimension conflicts, investigate
- Sacred Geometry validates resonance

**Resonance Triangle**:
```
       Business Need
          /    \
         /      \
        /        \
   User Value - Technical Feasibility
```

**Example**:
```yaml
# Feature: Real-time collaboration
business_need: "Reduce review cycles by 40%"
user_value: "See changes as they happen"
technical_feasibility: "WebSockets + operational transform"

# Resonance check
alignment: ✅ All three harmonize
  - Business: Faster cycles achieved
  - User: Better experience
  - Technical: Well-understood pattern

# Counter-example: Feature with dissonance
business_need: "Ship fast"
user_value: "High security"
technical_feasibility: "Can skip auth for speed"

# Resonance check
alignment: ❌ Conflict detected
  - Technical approach violates user value
  - Must resolve: Add auth (slower) OR reduce security (risky)
```

**Work Codex Integration**:
- **COF Holistic dimension** - system-wide harmony
- **Sacred Geometry** - multiple gates ensure alignment
- **Quality gates** - prevent dissonant solutions

---

### Principle 11: Diversity, Equity, and Inclusion

**Core Tenet**: Teams and systems thrive when perspectives are varied, access is fair, and participation is open.

**Philosophy**: Homogeneous teams build biased systems. Diverse perspectives reveal blind spots, challenge assumptions, and produce better outcomes.

**Application**:
- Adversarial research uses 6 perspectives (Hexad)
- Critic evaluates from 5 aspects (STEEP)
- Consider accessibility in all designs
- Ensure equitable access to tools and knowledge

**Hexad Adversarial Research** (from MVP v3.0):
1. **Evidence Gatherer** - Diverse data sources
2. **Evidence Validator** - Cross-check assumptions
3. **Advocate** - Argue FOR (multiple viewpoints)
4. **Critic** - Argue AGAINST (challenge bias)
5. **Integrator** - Synthesize perspectives
6. **Diverger** - Preserve alternatives

**Work Codex Integration**:
- **Adversarial research** - multiple perspectives
- **STEEP analysis** - 5-dimensional security review
- **Accessibility** - built into design from start

---

## Sacred Geometry Pattern Library

### Overview

Sacred Geometry provides **objective quality measurement** using geometric patterns. Each pattern validates a different aspect of quality.

**Minimum**: 3/5 gates must pass for approval
**Production**: All 5 gates should pass

---

### Pattern 1: Circle (Completeness)

**Meaning**: Wholeness, completion, no gaps

**Visual**: ○ - Everything needed is present

**Validation Checks**:
- [ ] Code implementation complete (all features)
- [ ] Tests complete (unit + integration + system)
- [ ] Documentation complete (API docs + README + troubleshooting)
- [ ] Evidence bundle complete (PAOAL summary + deviations + lessons)

**Pass Criteria**: All 4 checks ✅

**Example**:
```yaml
circle_validation:
  code: ✅ All 5 endpoints implemented
  tests: ✅ 15 unit, 8 integration, 3 e2e tests
  docs: ✅ OpenAPI spec + README + examples
  evidence: ✅ PAOAL summary with all 5 phases
  
  result: PASS (4/4)
```

**When to Apply**:
- All code reviews
- Before marking tasks complete
- Production deployments

**Integration**:
- Combines with **Logs First** (#3) - evidence required
- Supports **Trust Nothing, Verify Everything** (#1) - completeness verified
- Required for **UCL Rule 3** - complete evidence

---

### Pattern 2: Triangle (Stability)

**Meaning**: Three-point stability, process followed

**Visual**: △ - Stable on all three points

**Three Points**:
1. **Plan** - Intention/design documented
2. **Execute** - Implementation completed
3. **Validate** - Tests pass + review approved

**Validation Checks**:
- [ ] Plan exists (design doc OR approach documented)
- [ ] Execution complete (all planned work implemented)
- [ ] Validation passed (tests green + quality gates passed)

**Pass Criteria**: All 3 checks ✅

**Example**:
```yaml
triangle_validation:
  plan: ✅ Architecture design documented in ADR-005
  execute: ✅ All 3 services implemented as designed
  validate: ✅ 47 tests passing, ruff + mypy clean
  
  result: PASS (3/3)
```

**When to Apply**:
- Process validation
- Checking work completeness
- Ensuring methodology followed

**Integration**:
- **PAOAL** implements this (Plan → Act → Observe)
- **Context Before Action** (#9) - plan before execute
- Prevents **Fix the Symptom** (#5) - ensures root addressed

---

### Pattern 3: Spiral (Learning)

**Meaning**: Progressive growth, continuous improvement

**Visual**: 🌀 - Outward growth through iteration

**Validation Checks**:
- [ ] Lessons documented (in PAOAL Log phase OR vibe_learn)
- [ ] Patterns extracted (reusable knowledge identified)
- [ ] Memory updated (significant insights stored via agent-memory)

**Pass Criteria**: 2/3 checks ✅ (at least lessons + patterns OR memory)

**Example**:
```yaml
spiral_validation:
  lessons: ✅ "Password reset endpoints MUST be async"
  patterns: ✅ "Rate limiting required for auth endpoints"
  memory: ✅ Stored in agent-memory under "auth-patterns"
  
  result: PASS (3/3)
```

**When to Apply**:
- After failures (mandatory with vibe_learn)
- After completing complex work
- When discovering new patterns

**Integration**:
- **vibe_learn protocol** - captures lessons
- **Iteration is Sacred** (#8) - learning from each cycle
- **Leave Things Better** (#4) - knowledge shared

---

### Pattern 4: Golden Ratio (Balance)

**Meaning**: Harmonious proportion, reasonable estimates

**Formula**: φ ≈ 1.618 (ideal), but 0.5x-2.0x acceptable range

**Validation Checks**:
- [ ] Estimate accuracy: actual/estimated between 0.5-2.0
- [ ] Technical debt managed (not increased unnecessarily)
- [ ] Value delivered (acceptance criteria met)

**Pass Criteria**: All 3 checks ✅

**Example**:
```yaml
golden_ratio_validation:
  estimate_accuracy:
    estimated_loc: 500
    actual_loc: 650
    ratio: 1.30  # ✅ Within 0.5-2.0 range
    
  technical_debt:
    before: 15 TODO comments
    after: 12 TODO comments  # ✅ Reduced, not increased
    
  value_delivered:
    acceptance_criteria_met: 5/5  # ✅ All criteria met
    
  result: PASS (3/3)
```

**When to Apply**:
- Estimate validation
- Resource efficiency check
- Value delivery confirmation

**Integration**:
- **PAOAL Plan phase** - estimates upfront
- **Balance Order and Flow** (#7) - efficiency without waste
- **Resonance is Proof** (#10) - effort matches value

---

### Pattern 5: Fractal (Consistency)

**Meaning**: Self-similar patterns at all scales

**Visual**: Same pattern repeated at different scales

**Validation Checks**:
- [ ] Code style matches existing patterns (linting passes)
- [ ] Architecture consistent (follows established layers)
- [ ] Naming conventions uniform (same patterns throughout)

**Pass Criteria**: All 3 checks ✅

**Example**:
```yaml
fractal_validation:
  code_style:
    ruff_check: ✅ PASS
    mypy_check: ✅ PASS
    
  architecture:
    layers: ✅ Repository → Service → API (standard pattern)
    consistent: ✅ Same dependency injection across all services
    
  naming:
    functions: ✅ snake_case throughout
    classes: ✅ PascalCase throughout
    files: ✅ kebab-case throughout
    
  result: PASS (3/3)
```

**When to Apply**:
- Code reviews
- Refactoring validation
- Ensuring codebase coherence

**Integration**:
- **Workspace First** (#2) - match existing patterns
- **Leave Things Better** (#4) - maintain quality
- Prevents duplication and inconsistency

---

## Universal Context Law (UCL) - Complete Specification

### Core Law

**"No orphaned, cyclical, or incomplete context may persist in the system."**

---

### Rule 1: No Orphans

**Definition**: All work has parent linkage to origin

**Why**: Prevents "where did this come from?" questions. Enables traceability.

**Validation**: Can trace work back to GitHub issue/epic/project

**Implementation** (in handoffs):
```markdown
## HANDOFF CONTEXT
Parent Linkage: GH-123 (Feature: User Authentication)
```

**Enforcement**:
- All agent handoffs MUST include `parent_linkage` field
- No work begins without GitHub issue/epic/task ID
- Meta-Orchestrator tracks lineage

**Example**:
```yaml
# ✅ Good - has parent
task:
  id: TASK-456
  parent_linkage: GH-123 (Feature: User Authentication)
  origin: Epic: Auth System Redesign
  
# ❌ Bad - orphaned
task:
  id: TASK-789
  parent_linkage: null  # WHERE DID THIS COME FROM?
```

---

### Rule 2: No Cycles

**Definition**: No circular dependencies in work chain

**Why**: Prevents deadlocks, ensures forward progress

**Validation**: Work flows toward completion, never backward to same agent

**Implementation**:
- Meta-Orchestrator tracks history: `[meta → docs → arch → exec → critic]`
- Detects cycles: `exec → critic → exec → critic → exec` ❌
- Breaks cycles by elevating to Meta for new routing

**Enforcement**:
- Track agent chain per task
- Prevent `Agent A → Agent B → Agent A`
- Escalate if cycle detected

**Example**:
```yaml
# ✅ Good - flows forward
workflow:
  chain: [meta, docs, arch, exec, critic, meta]
  direction: forward  # Always toward completion
  
# ❌ Bad - circular
workflow:
  chain: [exec, critic, exec, critic, exec]
  direction: circular  # DEADLOCK
  action: Elevate to meta-orchestrator
```

---

### Rule 3: Complete Evidence

**Definition**: All claims backed by proof

**Why**: Enables verification, prevents "trust me" assertions

**Validation**: Every deliverable has supporting evidence

**Implementation**:
- Tests prove code works
- Logs prove process followed
- Evidence bundles prove PAOAL executed
- Sources cited in research

**Enforcement**:
- Circle gate requires evidence
- PAOAL Log phase generates evidence
- All handoffs reference evidence

**Example**:
```yaml
# ✅ Good - evidence backed
claim: "Password reset implemented"
evidence:
  tests: "tests/test_password_reset.py (5 tests passing)"
  logs: "logs/2025-12-31-implementation.jsonl"
  paoal_summary: "evidence/FEAT-456-paoal.yaml"
  
# ❌ Bad - no evidence
claim: "Password reset implemented"
evidence: null  # TRUST ME?
```

---

### UCL Enforcement Mechanisms

**Triple-Check Protocol**:
1. **Initial Build** → Verify parent linkage exists
2. **Logs-First Diagnostics** → Check evidence completeness
3. **Reproducibility/DoD** → Validate no orphans/cycles

**Strategic Session Audits** (3/6/9 cadence):
- Every 3rd session: Quick UCL check
- Every 6th session: Full COF + UCL review
- Every 9th session: Complete compliance audit

**Compliance Gates**:
- Nothing is "done" until UCL validated
- Circle gate checks evidence (Rule 3)
- All handoffs checked for parent linkage (Rule 1)
- Meta-Orchestrator tracks chains (Rule 2)

---

## PAOAL Execution Model - Complete Templates

### Overview

PAOAL (Plan → Act → Observe → Adapt → Log) is the **systematic execution framework** for implementations.

**When to Use**:
- All medium/complex implementations (3+ files)
- When systematic execution needed
- When evidence trail required

**When NOT to Use**:
- Simple tasks (1-2 files, well-understood)
- Trivial changes (typo fixes, config updates)

---

### Phase 1: Plan

**Purpose**: Define approach before acting

**Outputs**:
- Implementation strategy/approach
- Estimated LOC and time
- Tool and pattern selection
- Implementation order

**Template**:
```yaml
plan:
  approach: "[Strategy description]"
  estimate:
    loc: [number]
    time: "[hours/days]"
  tools:
    - [tool 1]
    - [tool 2]
  patterns:
    - [pattern 1]
    - [pattern 2]
  order:
    1. [step 1]
    2. [step 2]
```

**Example**:
```yaml
plan:
  approach: "Repository → Service → API (TDD)"
  estimate:
    loc: 500
    time: "8 hours"
  tools:
    - Python 3.11
    - FastAPI
    - SQLAlchemy
    - pytest
  patterns:
    - Repository pattern
    - Dependency Injection
    - Async/await for I/O
  order:
    1. Define models (SQLAlchemy + Pydantic)
    2. Implement repository layer (DB access)
    3. Implement service layer (business logic)
    4. Implement API layer (FastAPI routes)
    5. Write tests at each layer
```

**Work Codex Integration**:
- **Context Before Action** (#9) - understand before implementing
- **Best Tool for the Context** (#6) - tool selection upfront

---

### Phase 2: Act

**Purpose**: Execute implementation

**Activities**:
- Implement with tests (TDD when appropriate)
- Atomic commits (one logical change per commit)
- Workspace-first (search before creating)
- Incremental evidence generation

**Template**:
```yaml
act:
  files_created:
    - path: [file path]
      lines: [LOC]
      purpose: [description]
  commits:
    - hash: [git hash]
      message: [conventional commit message]
  tests_added: [count]
  loc_total: [number]
```

**Example**:
```yaml
act:
  files_created:
    - path: "src/auth/repositories.py"
      lines: 120
      purpose: "PasswordResetRepository with token management"
    - path: "src/auth/services.py"
      lines: 80
      purpose: "PasswordResetService with email integration"
    - path: "src/auth/api.py"
      lines: 60
      purpose: "POST /auth/reset-password endpoint"
    - path: "tests/test_password_reset.py"
      lines: 150
      purpose: "Unit + integration tests"
  commits:
    - hash: "a1b2c3d"
      message: "feat(auth): add password reset repository"
    - hash: "e4f5g6h"
      message: "feat(auth): add password reset service"
    - hash: "i7j8k9l"
      message: "feat(auth): add password reset API endpoint"
    - hash: "m0n1o2p"
      message: "test(auth): add password reset test suite"
  tests_added: 12
  loc_total: 410
```

**Work Codex Integration**:
- **Logs First** (#3) - commits logged incrementally
- **Leave Things Better** (#4) - fix issues while implementing
- **Workspace First** (#2) - search before creating

---

### Phase 3: Observe

**Purpose**: Validate implementation

**Activities**:
- Run all tests (unit + integration + system)
- Check coverage (target ≥80%)
- Run linters (ruff, mypy)
- Validate against acceptance criteria

**Template**:
```yaml
observe:
  tests:
    unit: [pass/fail count]
    integration: [pass/fail count]
    system: [pass/fail count]
  coverage:
    percentage: [number]
    target: 80
  quality_checks:
    ruff: [pass/fail]
    mypy: [pass/fail]
  acceptance_criteria:
    - criterion: [description]
      status: [✅/❌]
```

**Example**:
```yaml
observe:
  tests:
    unit: 8/8 passing
    integration: 3/3 passing
    system: 1/1 passing
  coverage:
    percentage: 92
    target: 80
    status: ✅ EXCEEDS
  quality_checks:
    ruff: ✅ PASS
    mypy: ✅ PASS
  acceptance_criteria:
    - criterion: "User can request password reset via email"
      status: ✅
    - criterion: "Token expires after 1 hour"
      status: ✅
    - criterion: "Rate limited to 3 requests per hour"
      status: ✅
    - criterion: "Old password cannot be reused"
      status: ✅
    - criterion: "Email sent asynchronously"
      status: ✅
```

**Work Codex Integration**:
- **Trust Nothing, Verify Everything** (#1) - validation required
- **Sacred Geometry Circle** - completeness checked
- **Sacred Geometry Triangle** - validation point

---

### Phase 4: Adapt

**Purpose**: Refine based on observations

**Activities**:
- Refactor based on test results
- Optimize performance bottlenecks
- Handle discovered edge cases
- Adjust approach if blocked

**Template**:
```yaml
adapt:
  issues_found:
    - issue: [description]
      resolution: [what was done]
  optimizations:
    - optimization: [description]
      impact: [metric improvement]
  deviations_from_plan:
    - deviation: [what changed]
      rationale: [why it changed]
```

**Example**:
```yaml
adapt:
  issues_found:
    - issue: "Email sending blocking request (3s latency)"
      resolution: "Made email async with Celery task queue"
    - issue: "Token collision risk with UUID4"
      resolution: "Switched to cryptographically secure token generation"
  optimizations:
    - optimization: "Cached password hash lookup"
      impact: "Response time: 500ms → 80ms"
    - optimization: "Added database index on tokens.expires_at"
      impact: "Token validation: 120ms → 15ms"
  deviations_from_plan:
    - deviation: "Added Celery for async email (not in original plan)"
      rationale: "Required to meet <200ms API response requirement"
```

**Work Codex Integration**:
- **Fix the Root, Not the Symptom** (#5) - address underlying issues
- **Balance Order and Flow** (#7) - adjust when needed
- **Iteration is Sacred** (#8) - refinement expected

---

### Phase 5: Log

**Purpose**: Generate evidence and capture lessons

**Activities**:
- Create evidence bundle with PAOAL summary
- Document deviations from plan
- Capture lessons learned (vibe_learn)
- Store significant insights (agent-memory)

**Template**:
```yaml
log:
  evidence_bundle:
    path: [file path]
    hash: [SHA-256]
    size: [bytes]
  deviations:
    - [deviation 1]
    - [deviation 2]
  lessons_learned:
    - [lesson 1]
    - [lesson 2]
  patterns_extracted:
    - [pattern 1]
    - [pattern 2]
  stored_in_memory: [true/false]
```

**Example**:
```yaml
log:
  evidence_bundle:
    path: "evidence/FEAT-456-password-reset.yaml"
    hash: "sha256:a1b2c3..."
    size: 4096
  deviations:
    - "Added Celery for async email (not in original estimate)"
    - "Increased LOC from 500 to 650 due to comprehensive error handling"
  lessons_learned:
    - "Password reset endpoints MUST be async to meet latency requirements"
    - "Token generation MUST use cryptographically secure methods (not UUID4)"
    - "Rate limiting is essential for auth endpoints (prevent abuse)"
  patterns_extracted:
    - "Auth Endpoint Pattern: rate limit + async + secure tokens + comprehensive logging"
    - "Email Pattern: Always async, never block requests"
  stored_in_memory: true
  memory_tag: "auth-patterns"
```

**Work Codex Integration**:
- **Logs First** (#3) - evidence generated
- **Sacred Geometry Spiral** - learning captured
- **Leave Things Better** (#4) - knowledge shared

---

## Evidence Bundle Templates

### Simple Task Evidence

```yaml
task_id: TASK-123
complexity: SIMPLE
deliverables:
  - artifact: "health_check.py"
    lines_changed: 15
validation:
  tests_passed: true
  coverage: 95%
  linting: clean
```

### Medium Task Evidence (PAOAL)

```yaml
task_id: FEAT-456
complexity: MEDIUM
paoal_summary:
  plan:
    approach: "Repository → Service → API"
    estimate: "500 LOC, 8 hours"
  act:
    files_created: 3
    loc_actual: 650
    tests_added: 12
  observe:
    tests: "12/12 passing"
    coverage: 92%
    quality: "ruff + mypy clean"
  adapt:
    issues_resolved: 2
    optimizations: 2
  log:
    lessons: 3
    patterns: 2
estimates:
  estimated_loc: 500
  actual_loc: 650
  ratio: 1.30
sacred_geometry:
  circle: ✅ PASS
  triangle: ✅ PASS
  spiral: ✅ PASS
  golden_ratio: ✅ PASS
  fractal: ✅ PASS
  result: "5/5 gates passed"
```

### Complex Task Evidence (PAOAL + COF)

```yaml
task_id: EPIC-789
complexity: COMPLEX
paoal_summary: [as above]
cof_analysis:
  dimensions: 13
  motivational: "Reduce password reset support tickets by 80%"
  relational: "Integrates with email service, auth system, user management"
  situational: "Legacy system lacks self-service, high support burden"
  resource: "8 hours dev time, Celery infrastructure required"
  narrative: "User can reset password without calling support"
  recursive: "Lessons inform future auth features"
  computational: "Async task queue, cryptographic token generation"
  emergent: "Discovered need for rate limiting during implementation"
  temporal: "1 hour token expiration, 3 requests/hour rate limit"
  spatial: "Distributed: API server + Celery worker + email service"
  holistic: "Part of broader auth system redesign (EPIC-123)"
  validation: "12 tests, 92% coverage, 5/5 Sacred Geometry gates"
  integration: "Deployed via CI/CD, monitored via APM"
adr_created: true
adr_id: ADR-005
sacred_geometry: [as above]
```

---

## Complexity-Based Workflow Selection

### Decision Tree

```
Task Received → Complexity Check

SIMPLE (1-2 files):
  - No COF analysis
  - No PAOAL required
  - Direct routing to specialist
  - Basic evidence (tests + commit)
  
MEDIUM (3-5 files):
  - Partial COF (Motivational, Relational, Holistic + 2-3 others)
  - PAOAL required
  - Standard specialist chain
  - PAOAL evidence bundle
  
COMPLEX (6+ files OR architectural changes):
  - Full COF 13D analysis
  - PAOAL required
  - Multi-specialist collaboration
  - Comprehensive evidence + ADR
```

### Complexity Classification Algorithm

```python
def classify_complexity(task):
    files = count_affected_files(task)
    
    if has_architectural_changes(task):
        return "COMPLEX"
    
    if has_cross_system_integration(task):
        return "COMPLEX"
    
    if risk_level(task) == "CRITICAL":
        return "COMPLEX"
    
    if files <= 2:
        return "SIMPLE"
    elif files <= 5:
        return "MEDIUM"
    else:
        return "COMPLEX"
```

### Workflow Routing by Complexity

**SIMPLE**:
```
meta → specialist → meta
Example: meta → executor → meta
```

**MEDIUM**:
```
meta → docs → arch → exec → critic → meta
```

**COMPLEX**:
```
meta → docs → researcher → arch → exec → critic → meta
+ Full COF 13D
+ ADR creation
+ Comprehensive evidence
```

---

## MCP Tool Strategy Matrix

### Tool Selection by Situation

| Situation | Primary Tool | Fallback | When NOT to Use |
|-----------|--------------|----------|-----------------|
| Session start | constitution_check | Manual checklist | N/A |
| Complex reasoning | sequential-thinking | Manual PAOAL | Simple tasks |
| Unbiased analysis | runSubagent | Manual separation | When context must be shared |
| ANY failure | vibe_learn | Manual lesson capture | Never skip this |
| Query lessons | agent-memory | Project knowledge search | New work with no history |
| File operations | Read/Write/Edit | CLI (last resort) | When MCP unavailable |
| GitHub operations | mcp__github__* | gh CLI | Never use gh when MCP available |
| Database queries | dbhub | psql CLI | Never use CLI when MCP available |

### Fallback Protocols

**If vibe_learn unavailable**:
```markdown
## FAILURE CAPTURED (Manual)

**What Failed**: [Specific error/issue]
**Root Cause**: [Underlying problem]
**Attempted Solutions**: [All things tried]
**Lesson Learned**: [Actionable takeaway]
**Stored**: .github/lessons-learned/{YYYY}/{QQ}/{type}.md
```

**If agent-memory unavailable**:
```markdown
Store in project knowledge:
- .github/knowledge/{category}/{topic}.md
- Tag with: [failure_type, agent, project, pattern]
```

**If sequential-thinking unavailable**:
```markdown
Execute PAOAL manually:
1. Plan: [Document approach]
2. Act: [Implement]
3. Observe: [Run tests]
4. Adapt: [Refactor]
5. Log: [Create evidence]
```

---

## Integration Checklist

### Daily Operations

- [ ] Reference Work Codex for decisions
- [ ] Use appropriate Sacred Geometry pattern
- [ ] Enforce UCL (parent linkage, deliverables, evidence)
- [ ] Execute PAOAL for implementations
- [ ] Capture lessons on failures (vibe_learn)

### Weekly Review

- [ ] Review gate progress
- [ ] Check evidence completeness
- [ ] Update lessons learned repository
- [ ] Tune Sacred Geometry thresholds (if needed)

### Monthly Retrospective

- [ ] Analyze pattern usage
- [ ] Review COF dimension selection accuracy
- [ ] Update templates based on learnings
- [ ] Celebrate successes (gate completions, defect reductions)

---

## Quick Reference Cards

### Sacred Geometry 5-Gate Checklist

```
[ ] Circle: Complete (code + tests + docs + evidence)
[ ] Triangle: Stable (plan + execute + validate)
[ ] Spiral: Learning (lessons + patterns + memory)
[ ] Golden Ratio: Balanced (0.5-2.0x estimate + debt managed)
[ ] Fractal: Consistent (style + architecture + naming)

Minimum: 3/5 must pass
```

### PAOAL Quick Check

```
[ ] Plan: Approach documented, estimate provided
[ ] Act: Implementation with tests, commits atomic
[ ] Observe: Tests run, coverage checked, criteria validated
[ ] Adapt: Issues addressed, optimizations made
[ ] Log: Evidence bundle generated, lessons captured
```

### UCL Quick Check

```
[ ] Parent linkage present (no orphans)
[ ] No circular dependencies (no cycles)
[ ] Evidence complete (all claims proven)
```

---

## References

**Full Documentation**:
- Work Codex: `/mnt/project/ContextForge_Work_Codex___Professional_Principles_with_Philosophy.md`
- COF 13D: `/mnt/project/03-Context-Ontology-Framework.md`
- UCL: `/mnt/project/COF_and_UCL_Definitions.md`

**Implementation Files**:
- `.github/copilot-instructions.md` - Core principles overview
- `.github/instructions/sacred-geometry.instructions.md` - Detailed 5-gate framework
- `.github/instructions/paoal-execution.instructions.md` - Execution templates
- `.github/instructions/agent-handoffs.instructions.md` - UCL-compliant handoff structure
- `.github/instructions/tool-usage.instructions.md` - MCP tool strategy

---

**Document**: ContextForge Foundation - Complete Reference  
**Version**: 3.0.0 (MVP v3.0)  
**Status**: APPROVED  
**Use**: Comprehensive reference for ContextForge Work foundations  
**For Quick Lookup**: See `copilot-instructions.md`  
**Last Updated**: 2025-12-31
