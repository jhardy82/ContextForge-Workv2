# Sacred Geometry Validation Framework - Detailed Reference

**Version**: 3.0.0 (MVP v3.0)
**Purpose**: Complete 5-gate validation framework for quality assurance
**Status**: APPROVED
**Authority**: MVP v3.0 Package + ContextForge Sacred Geometry Patterns

---

## Document Purpose

This file provides **detailed Sacred Geometry validation** for use by:
- **Critic agent** - Primary validator using 5-gate framework
- **All agents** - Understanding quality standards
- **Developers** - Self-validation before submission

**For quick reference**: See `copilot-instructions.md` or `contextforge-foundation.instructions.md`

---

## Sacred Geometry Overview

### Philosophy

**Core Principle**: Quality is multidimensional and geometric

**Why Geometry**: Geometric patterns provide:
- **Objective measurement** - Binary pass/fail per gate
- **Multiple perspectives** - 5 different aspects of quality
- **Flexibility** - 3/5 minimum allows pragmatism
- **Visual clarity** - Patterns easy to understand and remember

### The 5 Patterns

| Pattern | Meaning | Validation Focus |
|---------|---------|------------------|
| **Circle** | Completeness | Nothing missing (code + tests + docs + evidence) |
| **Triangle** | Stability | Process followed (plan → execute → validate) |
| **Spiral** | Learning | Knowledge captured (lessons → patterns → memory) |
| **Golden Ratio** | Balance | Efficiency (estimates accurate, debt managed) |
| **Fractal** | Consistency | Patterns match (style + architecture + naming) |

### Pass Thresholds

**Minimum** (Standard): 3/5 gates must pass
**Production** (Recommended): 5/5 gates should pass
**Advisory Mode**: Warn if <3, don't block
**Enforcing Mode**: Block if <3

---

## Gate 1: Circle (Completeness)

### Meaning

**Symbol**: ○  
**Concept**: Wholeness, completion, no gaps  
**Philosophy**: Work isn't done until ALL pieces are present

### Visual Metaphor

```
        Tests
           |
Code --- Circle --- Documentation
           |
       Evidence
```

A circle has no beginning or end - all parts must connect to be complete.

### Validation Checks (4 Required)

#### Check 1.1: Code Complete

**Criteria**: All planned features implemented

**Validation**:
```bash
# Compare implementation against acceptance criteria
- [ ] All user stories implemented
- [ ] All edge cases handled
- [ ] All error paths coded
- [ ] No TODO comments for required features
```

**Pass**: ✅ All acceptance criteria met  
**Fail**: ❌ Any required feature missing

**Example**:
```python
# ✅ PASS - All features complete
def reset_password(email, token, new_password):
    """Reset user password with token validation."""
    validate_email(email)           # ✅ Validation implemented
    verify_token(email, token)      # ✅ Token check implemented
    check_password_strength(new_password)  # ✅ Security check implemented
    update_password(email, new_password)   # ✅ Update implemented
    send_confirmation_email(email)  # ✅ Confirmation implemented
    log_password_reset(email)       # ✅ Audit implemented
    return {"status": "success"}

# ❌ FAIL - Missing features
def reset_password(email, token, new_password):
    """Reset user password."""
    update_password(email, new_password)
    return {"status": "success"}
    # Missing: token verification, password strength, confirmation email, audit
```

---

#### Check 1.2: Tests Complete

**Criteria**: Unit + integration + system tests present and passing

**Validation**:
```bash
# Test coverage check
pytest --cov=src --cov-report=term

Required:
- [ ] Unit tests ≥70% coverage
- [ ] Integration tests for happy paths
- [ ] Integration tests for error cases
- [ ] System tests for critical flows
```

**Pass**: ✅ All test types present, coverage ≥70%  
**Fail**: ❌ Any test type missing OR coverage <70%

**Example**:
```python
# ✅ PASS - Comprehensive tests
class TestPasswordReset:
    def test_valid_reset(self):           # Unit: happy path
    def test_invalid_token(self):         # Unit: error case
    def test_expired_token(self):         # Unit: error case
    def test_weak_password_rejected(self): # Unit: validation
    def test_email_sent(self):            # Integration: email service
    def test_audit_logged(self):          # Integration: logging
    def test_end_to_end_flow(self):       # System: complete flow

# ❌ FAIL - Incomplete tests
class TestPasswordReset:
    def test_valid_reset(self):  # Only happy path, no error cases
```

---

#### Check 1.3: Documentation Complete

**Criteria**: API docs + README + troubleshooting present

**Validation**:
```bash
Required:
- [ ] API documentation (OpenAPI/Swagger OR docstrings)
- [ ] README updates (if new feature/behavior)
- [ ] Troubleshooting guide (for complex features)
- [ ] Examples (for public APIs)
```

**Pass**: ✅ All required docs present  
**Fail**: ❌ Any required doc missing

**Example**:
```python
# ✅ PASS - Complete documentation
async def reset_password(email: str, token: str, new_password: str) -> PasswordResetResult:
    """Reset user password with token validation.
    
    This endpoint allows users to reset their password after receiving
    a reset token via email. The token must be valid and unexpired.
    
    Args:
        email: User's email address (validated format)
        token: Password reset token (from email)
        new_password: New password (must meet strength requirements)
        
    Returns:
        PasswordResetResult with status and details
        
    Raises:
        InvalidTokenError: If token is invalid or expired
        WeakPasswordError: If password doesn't meet requirements
        RateLimitError: If too many reset attempts
        
    Example:
        >>> result = await reset_password(
        ...     "user@example.com",
        ...     "abc123token",
        ...     "NewSecurePass123!"
        ... )
        >>> print(result.status)
        "success"
        
    Note:
        - Tokens expire after 1 hour
        - Rate limited to 3 attempts per hour
        - Password strength validated against OWASP standards
        - Confirmation email sent asynchronously
    """

# ❌ FAIL - No documentation
async def reset_password(email, token, new_password):
    # No docstring, no examples, no error documentation
```

---

#### Check 1.4: Evidence Complete

**Criteria**: PAOAL summary OR evidence bundle present

**Validation**:
```yaml
Required (for medium/complex tasks):
- [ ] PAOAL summary (all 5 phases)
- [ ] Deviations documented (if any)
- [ ] Lessons captured (if failures occurred)
- [ ] Evidence bundle file created
```

**Pass**: ✅ Evidence bundle complete  
**Fail**: ❌ Missing PAOAL summary OR deviations not explained

**Example**:
```yaml
# ✅ PASS - Complete evidence
evidence:
  paoal_summary:
    plan: "Repository → Service → API"
    act: "3 files, 410 LOC, 12 tests"
    observe: "12/12 tests passing, 92% coverage"
    adapt: "Made email async (latency requirement)"
    log: "3 lessons captured, 2 patterns extracted"
  deviations:
    - "Added Celery (not in original plan) - required for async email"
  lessons:
    - "Auth endpoints MUST be async"
    - "Always use cryptographically secure tokens"

# ❌ FAIL - No evidence
evidence: null
```

---

### Circle Gate: Combined Validation

**Pass Criteria**: All 4 checks ✅

**Validation Template**:
```yaml
circle_gate:
  code_complete: ✅/❌
  tests_complete: ✅/❌
  docs_complete: ✅/❌
  evidence_complete: ✅/❌
  
  result: PASS/FAIL (4/4 or <4/4)
```

**When to Apply**:
- All code reviews
- Before marking tasks complete
- Production deployments (mandatory)

**Rework Requirements** (if fails):
```markdown
## Circle Gate Failed: [X/4 checks passed]

**Missing**:
- [ ] [Specific missing piece 1]
- [ ] [Specific missing piece 2]

**Action Required**:
[Specific tasks to complete the circle]

**Estimated Rework Time**: [X hours]
```

---

## Gate 2: Triangle (Stability)

### Meaning

**Symbol**: △  
**Concept**: Three-point stability, process followed  
**Philosophy**: Stable structures stand on three legs - plan, execute, validate

### Visual Metaphor

```
       Plan
        /\
       /  \
      /    \
     /      \
    /________\
Execute    Validate
```

All three points must be solid for stability.

### Validation Checks (3 Required)

#### Check 2.1: Plan Exists

**Criteria**: Design doc OR approach documented before implementation

**Validation**:
```bash
Required (one of):
- [ ] Architecture Design Record (ADR)
- [ ] Design document in issue/PR
- [ ] Approach documented in PAOAL Plan phase
- [ ] Comments in code explaining approach
```

**Pass**: ✅ Plan documented before Act  
**Fail**: ❌ No plan, or plan created after implementation

**Example**:
```yaml
# ✅ PASS - Plan before implementation
paoal:
  plan:
    approach: "Repository → Service → API (TDD)"
    date: "2025-12-30"
  act:
    implementation_started: "2025-12-31"
    
# ADR-005: Password Reset Architecture
# Created: 2025-12-30 (before implementation)

# ❌ FAIL - No plan
paoal:
  plan: null
  act:
    implementation_started: "2025-12-31"
```

---

#### Check 2.2: Execution Complete

**Criteria**: All planned work implemented

**Validation**:
```bash
Required:
- [ ] All files in plan created
- [ ] All features in plan implemented
- [ ] Implementation matches design
- [ ] No deviations without explanation
```

**Pass**: ✅ Plan fully executed OR deviations explained  
**Fail**: ❌ Plan partially implemented without explanation

**Example**:
```yaml
# ✅ PASS - Plan executed with explained deviation
plan:
  files: [repository.py, service.py, api.py]
act:
  files_created: [repository.py, service.py, api.py, tasks.py]
  deviation: "Added tasks.py for Celery async email (latency requirement)"

# ❌ FAIL - Incomplete execution, no explanation
plan:
  files: [repository.py, service.py, api.py]
act:
  files_created: [service.py]  # Missing 2 files, no explanation
```

---

#### Check 2.3: Validation Passed

**Criteria**: Tests green + quality gates passed

**Validation**:
```bash
Required:
- [ ] All tests passing
- [ ] Linting clean (ruff)
- [ ] Type checking clean (mypy)
- [ ] Code review approved (if team workflow)
```

**Pass**: ✅ All validation steps passed  
**Fail**: ❌ Any validation step failed

**Example**:
```bash
# ✅ PASS - All validation passed
pytest: 47/47 passing ✅
ruff check .: 0 issues ✅
mypy src/: Success, no issues ✅
code_review: Approved ✅

# ❌ FAIL - Validation failed
pytest: 45/47 passing ❌ (2 failures)
ruff check .: 3 issues ❌
mypy src/: 5 type errors ❌
```

---

### Triangle Gate: Combined Validation

**Pass Criteria**: All 3 checks ✅

**Validation Template**:
```yaml
triangle_gate:
  plan_exists: ✅/❌
  execution_complete: ✅/❌
  validation_passed: ✅/❌
  
  result: PASS/FAIL (3/3 or <3/3)
```

**When to Apply**:
- Process validation
- Checking work completeness
- Ensuring methodology followed

**Rework Requirements** (if fails):
```markdown
## Triangle Gate Failed: Process Not Followed

**Point Failed**: [Plan/Execute/Validate]

**Action Required**:
- [ ] [Specific process step to complete]

**Estimated Rework Time**: [X hours]
```

---

## Gate 3: Spiral (Learning)

### Meaning

**Symbol**: 🌀  
**Concept**: Progressive growth, continuous improvement  
**Philosophy**: Each cycle adds knowledge - spiraling outward, not circular

### Visual Metaphor

```
        ┌──────→ Iteration 3 (broader knowledge)
       ↑
      ┌┴──────→ Iteration 2 (more knowledge)
     ↑
    ┌┴──────→ Iteration 1 (initial knowledge)
   Start
```

Knowledge accumulates and expands with each iteration.

### Validation Checks (2/3 Required)

#### Check 3.1: Lessons Documented

**Criteria**: Key learnings captured in PAOAL Log OR vibe_learn

**Validation**:
```bash
Required:
- [ ] Lessons identified (what went well, what didn't)
- [ ] Lessons documented (PAOAL Log phase OR vibe_learn)
- [ ] Lessons actionable (not just observations)
```

**Pass**: ✅ At least 1 actionable lesson documented  
**Fail**: ❌ No lessons OR lessons not actionable

**Example**:
```yaml
# ✅ PASS - Actionable lessons
lessons:
  - "Password reset endpoints MUST be async (latency requirement)"
  - "Always use cryptographically secure tokens (UUID4 is insufficient)"
  - "Rate limiting essential for auth endpoints (prevent abuse)"

# ❌ FAIL - No lessons OR not actionable
lessons:
  - "It works" # Not actionable
  - "Code is good" # Not specific
```

---

#### Check 3.2: Patterns Extracted

**Criteria**: Reusable knowledge identified for future use

**Validation**:
```bash
Required:
- [ ] Pattern identified (general principle, not task-specific)
- [ ] Pattern documented (can be applied elsewhere)
- [ ] Pattern tagged (easy to find later)
```

**Pass**: ✅ At least 1 reusable pattern extracted  
**Fail**: ❌ No patterns identified

**Example**:
```yaml
# ✅ PASS - Reusable patterns
patterns:
  - name: "Auth Endpoint Pattern"
    description: "rate limit + async + secure tokens + comprehensive logging"
    applies_to: ["login", "password_reset", "2fa"]
    
  - name: "Email Pattern"
    description: "Always async with task queue, never block requests"
    applies_to: ["notifications", "confirmations", "reports"]

# ❌ FAIL - Task-specific, not reusable
patterns:
  - "This password reset works" # Not a pattern
```

---

#### Check 3.3: Memory Updated

**Criteria**: Significant insights stored via agent-memory (if available)

**Validation**:
```bash
Required (if agent-memory available):
- [ ] Lesson stored with metadata
- [ ] Tagged appropriately
- [ ] Queryable for future work

Fallback (if agent-memory unavailable):
- [ ] Stored in project knowledge (.github/knowledge/)
- [ ] Indexed in knowledge map
```

**Pass**: ✅ Stored in memory OR project knowledge  
**Fail**: ❌ Not stored anywhere

**Example**:
```bash
# ✅ PASS - Stored in agent-memory
agent-memory store:
  key: "auth-patterns/password-reset"
  content: "Password reset endpoints must be async..."
  tags: ["auth", "async", "security", "rate-limiting"]
  
# ✅ PASS - Fallback to project knowledge
file: .github/knowledge/auth/password-reset-pattern.md
indexed: .github/knowledge/INDEX.md

# ❌ FAIL - Not stored
storage: null
```

---

### Spiral Gate: Combined Validation

**Pass Criteria**: 2/3 checks ✅ (flexible - learning takes time)

**Validation Template**:
```yaml
spiral_gate:
  lessons_documented: ✅/❌
  patterns_extracted: ✅/❌
  memory_updated: ✅/❌
  
  result: PASS/FAIL (≥2/3 or <2/3)
```

**When to Apply**:
- After failures (mandatory with vibe_learn)
- After completing complex work
- When discovering new patterns

**Rework Requirements** (if fails):
```markdown
## Spiral Gate Failed: Learning Not Captured

**Missing**: [Lessons/Patterns/Memory]

**Action Required**:
- [ ] Capture at least 2 actionable lessons
- [ ] Extract at least 1 reusable pattern
- [ ] Store in agent-memory OR project knowledge

**Estimated Rework Time**: 30 minutes
```

---

## Gate 4: Golden Ratio (Balance)

### Meaning

**Symbol**: φ ≈ 1.618  
**Concept**: Harmonious proportion, reasonable estimates  
**Philosophy**: Efficiency without waste, value without excess

### Visual Metaphor

```
Ideal Ratio: φ ≈ 1.618
Acceptable Range: 0.5 - 2.0

Too Low (0.5) ←──── 1.0 (Perfect) ────→ Too High (2.0)
Under-estimated        Accurate        Over-estimated
```

### Validation Checks (3 Required)

#### Check 4.1: Estimate Accuracy

**Criteria**: actual/estimated between 0.5-2.0

**Validation**:
```python
ratio = actual_loc / estimated_loc

if 0.5 <= ratio <= 2.0:
    result = "PASS"
else:
    result = "FAIL"
```

**Pass**: ✅ Ratio between 0.5-2.0  
**Fail**: ❌ Ratio <0.5 (under-delivered) OR >2.0 (over-scoped)

**Example**:
```yaml
# ✅ PASS - Good estimate
estimate:
  estimated_loc: 500
  actual_loc: 650
  ratio: 1.30  # Within 0.5-2.0

# ✅ PASS - Slight under-estimate
estimate:
  estimated_loc: 500
  actual_loc: 300
  ratio: 0.60  # Within 0.5-2.0

# ❌ FAIL - Severe over-scope
estimate:
  estimated_loc: 500
  actual_loc: 1200
  ratio: 2.40  # Outside range - scope creep
```

---

#### Check 4.2: Technical Debt Managed

**Criteria**: Debt not increased unnecessarily

**Validation**:
```bash
Required:
- [ ] TODO count: not increased significantly
- [ ] Code complexity: not increased unnecessarily
- [ ] Test coverage: not decreased
- [ ] Known issues: addressed OR documented
```

**Pass**: ✅ Debt stable or reduced  
**Fail**: ❌ Debt significantly increased without justification

**Example**:
```yaml
# ✅ PASS - Debt reduced
technical_debt:
  before:
    todos: 15
    coverage: 75%
  after:
    todos: 12  # Reduced
    coverage: 78%  # Improved

# ❌ FAIL - Debt increased
technical_debt:
  before:
    todos: 15
    coverage: 75%
  after:
    todos: 25  # Increased significantly
    coverage: 68%  # Decreased
  justification: null  # No explanation
```

---

#### Check 4.3: Value Delivered

**Criteria**: Acceptance criteria met

**Validation**:
```bash
Required:
- [ ] All acceptance criteria met
- [ ] User story complete
- [ ] Business value delivered
```

**Pass**: ✅ All criteria met  
**Fail**: ❌ Any criterion unmet

**Example**:
```yaml
# ✅ PASS - Full value delivered
acceptance_criteria:
  - criterion: "User can reset password via email"
    status: ✅ MET
  - criterion: "Token expires after 1 hour"
    status: ✅ MET
  - criterion: "Rate limited to 3/hour"
    status: ✅ MET
  result: 3/3 criteria met

# ❌ FAIL - Incomplete value
acceptance_criteria:
  - criterion: "User can reset password via email"
    status: ✅ MET
  - criterion: "Token expires after 1 hour"
    status: ❌ NOT MET (tokens don't expire)
  - criterion: "Rate limited to 3/hour"
    status: ❌ NOT MET (no rate limiting)
  result: 1/3 criteria met
```

---

### Golden Ratio Gate: Combined Validation

**Pass Criteria**: All 3 checks ✅

**Validation Template**:
```yaml
golden_ratio_gate:
  estimate_accuracy: ✅/❌ (ratio: X.XX)
  technical_debt_managed: ✅/❌
  value_delivered: ✅/❌
  
  result: PASS/FAIL (3/3 or <3/3)
```

**When to Apply**:
- Estimate validation
- Resource efficiency check
- Value delivery confirmation

**Rework Requirements** (if fails):
```markdown
## Golden Ratio Gate Failed: Imbalance Detected

**Issue**: [Estimate/Debt/Value]

**Action Required**:
- [ ] [Specific fix for imbalance]

**Estimated Rework Time**: [X hours]
```

---

## Gate 5: Fractal (Consistency)

### Meaning

**Symbol**: Same pattern at different scales  
**Concept**: Self-similar patterns across codebase  
**Philosophy**: Consistency reduces cognitive load and prevents errors

### Visual Metaphor

```
Module Level:    Repository → Service → API
Function Level:  Validate → Execute → Log
Line Level:      snake_case, type hints, docstrings

Same pattern, different scale
```

### Validation Checks (3 Required)

#### Check 5.1: Code Style Matches

**Criteria**: Linting passes (ruff)

**Validation**:
```bash
ruff check .

Required:
- [ ] 0 linting errors
- [ ] 0 style violations
- [ ] Formatting consistent
```

**Pass**: ✅ Ruff clean  
**Fail**: ❌ Any linting issues

---

#### Check 5.2: Architecture Consistent

**Criteria**: Follows established layers

**Validation**:
```bash
Required:
- [ ] Uses standard patterns (Repository, Service, API)
- [ ] Layer separation maintained
- [ ] Dependency direction correct (no circular imports)
```

**Pass**: ✅ Matches existing architecture  
**Fail**: ❌ Introduces new pattern inconsistent with codebase

---

#### Check 5.3: Naming Consistent

**Criteria**: Matches codebase conventions

**Validation**:
```bash
Required:
- [ ] Functions: snake_case
- [ ] Classes: PascalCase
- [ ] Constants: UPPER_SNAKE_CASE
- [ ] Files: kebab-case OR snake_case (consistent with project)
```

**Pass**: ✅ All naming matches conventions  
**Fail**: ❌ Inconsistent naming

---

### Fractal Gate: Combined Validation

**Pass Criteria**: All 3 checks ✅

**Validation Template**:
```yaml
fractal_gate:
  code_style_matches: ✅/❌
  architecture_consistent: ✅/❌
  naming_consistent: ✅/❌
  
  result: PASS/FAIL (3/3 or <3/3)
```

---

## Enforcement Modes

### ADVISORY Mode (Default)

**Behavior**: Warn if <3 gates pass, but don't block

**Use When**:
- New system being implemented
- Gates are being tuned
- Pass rate unknown

**Output Example**:
```
⚠️  Sacred Geometry Warning: 2/5 gates passed (minimum: 3/5)
Failed: Circle, Spiral
Action: Review rework requirements below
[Continue anyway? Y/N]
```

### ENFORCING Mode (Production)

**Behavior**: Block if <3 gates pass

**Use When**:
- Gates tuned (pass rate >70%)
- Production deployments
- Quality critical

**Output Example**:
```
❌ Sacred Geometry Failed: 2/5 gates passed (minimum: 3/5)
Failed: Circle, Spiral
Action: Complete rework requirements before proceeding
[Blocked - cannot merge]
```

---

## Complete Validation Report Template

```yaml
sacred_geometry_validation:
  task_id: FEAT-456
  timestamp: "2025-12-31T10:30:00Z"
  
  gates:
    circle:
      code_complete: ✅
      tests_complete: ✅
      docs_complete: ✅
      evidence_complete: ✅
      result: PASS (4/4)
      
    triangle:
      plan_exists: ✅
      execution_complete: ✅
      validation_passed: ✅
      result: PASS (3/3)
      
    spiral:
      lessons_documented: ✅
      patterns_extracted: ✅
      memory_updated: ❌
      result: PASS (2/3)
      
    golden_ratio:
      estimate_accuracy: ✅ (ratio: 1.30)
      technical_debt_managed: ✅
      value_delivered: ✅
      result: PASS (3/3)
      
    fractal:
      code_style_matches: ✅
      architecture_consistent: ✅
      naming_consistent: ✅
      result: PASS (3/3)
  
  summary:
    gates_passed: 5/5
    minimum_required: 3/5
    overall_result: ✅ APPROVED
    
  recommendation: "APPROVE - All quality gates passed"
```

---

**Document**: Sacred Geometry Validation Framework  
**Version**: 3.0.0 (MVP v3.0)  
**Status**: APPROVED  
**Use**: Quality validation by Critic agent and developers  
**Last Updated**: 2025-12-31
