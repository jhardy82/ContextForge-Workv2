---
applyTo: "learn*, learning*, lesson*, retrospective*, AAR*, after action*, reflect*, vibe_learn*, pattern*, extract*, capture*"
description: "ContextForge learning capture and pattern extraction system with Sacred Geometry Spiral integration"
version: "2.0 (ContextForge-aligned)"
framework: "Sacred Geometry Spiral + UCL + Triple Storage"
---

# ContextForge Learning System

**Philosophy**: "Iteration is Sacred" - Learning from each cycle, spiraling outward with accumulated knowledge

**Sacred Geometry Pattern**: **Spiral** (progressive growth, continuous improvement)

---

## Core Principles

### 1. Sacred Geometry Spiral Gate
Learning is the **Spiral** pattern - each iteration adds knowledge, expanding outward:
```
        ┌──────→ Iteration 3 (broader knowledge)
       ↑
      ┌┴──────→ Iteration 2 (more knowledge)  
     ↑
    ┌┴──────→ Iteration 1 (initial knowledge)
   Start
```

**Validation**: Spiral gate passes when lessons captured + patterns extracted + memory updated

### 2. Universal Context Law (UCL)
All learnings must:
- **No Orphans**: Linked to originating task/project (parent linkage)
- **No Cycles**: Build on previous learnings (not circular reasoning)
- **Complete Evidence**: What happened, why, how to prevent/repeat

### 3. Triple Storage Protocol
Every learning stored in THREE places (redundancy + accessibility):
1. **vibe_learn** MCP tool (if available) - Agent memory optimization
2. **agent-memory** MCP tool (if available) - Queryable knowledge graph
3. **File system** (always) - Permanent project knowledge

---

## Learning Structure (ContextForge Format)

### Comprehensive Learning Template

```yaml
learning:
  # CORE IDENTIFICATION
  id: "L-{YYYY}-{QQ}-{counter}"  # e.g., L-2025-Q4-001
  timestamp: "{ISO 8601}"
  category: "technical/process/communication/tooling/security"
  
  # UCL COMPLIANCE
  parent_linkage:
    task_id: "{TASK-XXX}"
    project_id: "{PROJECT-YYY}"
    epic_id: "{EPIC-ZZZ}"  # if applicable
  
  # CONTEXT
  what_happened: |
    {1-2 sentence description of actual event/outcome}
  
  what_was_expected: |
    {1-2 sentence description of what should have happened}
  
  variance: |
    {1-2 sentence description of difference and why it matters}
  
  # ROOT CAUSE
  problem_created: |
    {Specific issue that occurred}
  
  why_problem: |
    {Underlying reason - root cause, not symptom}
  
  how_fixed: |
    {What was done to resolve it}
  
  # ACTIONABLE LESSON
  lesson: |
    {1-4 sentences: specific, actionable takeaway}
    {Must be applicable to future work}
    {Must explain WHAT to do differently}
  
  # PATTERN EXTRACTION
  pattern:
    name: "{Pattern name}"
    description: "{General principle extracted}"
    when_to_use: "{Applicable contexts}"
    when_not_to_use: "{Anti-patterns or exceptions}"
    confidence: "high/medium/low"
  
  # REUSABILITY
  applies_to:
    - "{context 1}"
    - "{context 2}"
  
  priority: "high/medium/low"
  
  reuse_potential: "high/medium/low"
  
  # EVIDENCE
  evidence:
    test_results: "{Reference to test output}"
    code_changes: "{Git commits or file references}"
    metrics: "{Performance data, coverage, etc.}"
    documentation: "{Where this is documented}"
  
  # IMPACT TRACKING
  impact:
    times_referenced: 0  # Incremented when learning applied
    times_prevented_issue: 0  # Incremented when proactively prevented problem
    times_ineffective: 0  # Incremented when learning didn't help
    effectiveness_score: 0  # Calculated: (prevented - ineffective) / referenced
  
  # STORAGE
  storage:
    vibe_learn_called: true/false
    agent_memory_key: "{key if stored}"
    file_path: ".github/learnings/{YYYY}/{QQ}/{category}/L-{id}.md"
    indexed: true/false  # In .github/learnings/INDEX.md
```

---

## Learning Capture Workflow

### Trigger Points

**ALWAYS capture learnings when**:
1. ✅ User says "learn!" or "capture this"
2. ✅ Quality gate fails (Sacred Geometry < 3/5)
3. ✅ Tests fail unexpectedly
4. ✅ Estimate significantly off (>2x variance)
5. ✅ Implementation approach changed mid-execution
6. ✅ Bug discovered in production/review
7. ✅ Pattern discovered during implementation
8. ✅ Retrospective or AAR conducted

### Capture Process (5 Steps)

#### Step 1: Extract Learning from Context

**Analyze systematically**:
```markdown
1. What just happened? (actual event)
2. What was supposed to happen? (expectation)
3. What's the gap? (variance)
4. Why did the gap occur? (root cause)
5. How was it fixed? (resolution)
6. What's the lesson? (actionable takeaway)
```

**Use sequential_thinking for complex situations**:
```
@agent uses sequential_thinking:
```
Task: Extract learning from recent failure

Analyze:
1. Event: [What happened]
2. Expectation: [What should have happened]
3. Root cause: [Why variance occurred - not symptom]
4. Fix applied: [How resolved]
5. Lesson: [Specific, actionable takeaway]
6. Pattern: [General principle if applicable]

Output: Structured learning ready for storage
```
```

#### Step 2: Formulate Learning (1-4 Sentences)

**Present to user for reflection**:
```markdown
**Learning Extracted**:

"{Specific actionable lesson in 1-4 sentences}"

**Rationale**:
- Problem: {What went wrong}
- Root Cause: {Why it happened}
- Prevention: {How to avoid next time}

**Pattern** (if applicable):
"{General principle extracted}"

**Applies to**: {contexts}
**Priority**: {high/medium/low}

---
**Reflection needed**: Does this accurately capture the lesson?
Please approve or suggest refinements.
```

#### Step 3: Reflect and Refine

**After user feedback**:
```markdown
**Reflected Learning** (refined):

"{Updated lesson incorporating user feedback}"

**Pattern refinement**:
"{Updated pattern if applicable}"

Ready to store.
```

#### Step 4: Triple Storage

**Storage Path 1: vibe_learn (if available)**
```python
vibe_learn(
    what_happened: "{actual event}",
    what_was_expected: "{expectation}",
    variance: "{gap and why}",
    lesson: "{actionable takeaway}",
    pattern: "{general principle}"
)
```

**Storage Path 2: agent-memory (if available)**
```python
agent_memory.store(
    key: "learning/{category}/{id}",
    content: {complete learning YAML},
    tags: [category, priority, project_id, pattern_name]
)
```

**Storage Path 3: File System (always)**
```markdown
File: .github/learnings/{YYYY}/{QQ}/{category}/L-{id}.md

Content:
```yaml
{Complete learning YAML from template above}
```

Index update:
File: .github/learnings/INDEX.md
Add entry: L-{id} | {category} | {lesson summary} | {date}
```

#### Step 5: Confirmation

```markdown
**Learning Captured** ✅

**Storage Status**:
- vibe_learn: ✅ Called / ⚠️ Unavailable (manual fallback used)
- agent-memory: ✅ Stored / ⚠️ Unavailable (file-only storage)
- File system: ✅ Stored at .github/learnings/{path}
- Index: ✅ Updated

**Learning ID**: L-{id}
**Category**: {category}
**Priority**: {priority}

This learning is now available for future reference and pattern matching.
```

---

## Impact Tracking & Evolution

### Incrementing Counters

**When learning is referenced/applied**:
```yaml
# Update learning file:
impact:
  times_referenced: {+1}
  last_referenced: "{timestamp}"
  context_applied: "{where it was used}"
```

**When learning prevents an issue**:
```yaml
impact:
  times_prevented_issue: {+1}
  prevention_context: "{what was avoided}"
```

**When learning proves ineffective**:
```yaml
impact:
  times_ineffective: {+1}
  ineffective_context: "{why it didn't help}"
  needs_refinement: true
```

### Effectiveness Scoring

**Automatic calculation**:
```python
effectiveness_score = (times_prevented_issue - times_ineffective) / max(times_referenced, 1)

# Score interpretation:
# > 0.5: Highly effective (promote to pattern)
# 0.0 - 0.5: Moderately effective (keep)
# < 0.0: Ineffective (review and possibly deprecate)
```

### Learning Lifecycle

```
NEW (times_referenced = 0)
  ↓ (applied in work)
ACTIVE (times_referenced > 0, effectiveness >= 0)
  ↓ (proven highly effective)
PATTERN (effectiveness > 0.5, times_prevented > 3)
  ↓ (extracted to skill file or instruction file)
INSTITUTIONALIZED (added to standard practices)

OR

ACTIVE (effectiveness < 0)
  ↓ (consistently ineffective)
UNDER_REVIEW (needs refinement)
  ↓ (cannot be improved)
DEPRECATED (archived, not deleted)
```

---

## Pattern Extraction & Promotion

### When to Extract Pattern

**Criteria for pattern extraction**:
1. Learning referenced ≥3 times
2. Effectiveness score >0.5
3. Applies to multiple contexts
4. General principle identified

**Pattern Promotion Process**:
```markdown
1. Identify candidate learning (meets criteria above)
2. Formulate general pattern from specific lesson
3. Identify applicable contexts (when to use / when not to use)
4. Create pattern template
5. Add to appropriate instruction file or skill
6. Link original learning to pattern (traceability)
```

### Pattern Template

```yaml
pattern:
  id: "P-{category}-{counter}"  # e.g., P-security-001
  name: "{Pattern name}"
  
  origin:
    learning_ids: ["L-2025-Q4-001", "L-2025-Q4-015"]
    discovered: "{date}"
  
  description: |
    {General principle - what the pattern is}
  
  rationale: |
    {Why this pattern works}
  
  when_to_use:
    - "{context 1}"
    - "{context 2}"
  
  when_not_to_use:
    - "{anti-pattern or exception 1}"
    - "{anti-pattern or exception 2}"
  
  implementation:
    - step: "{How to apply step 1}"
    - step: "{How to apply step 2}"
  
  evidence:
    examples: ["{reference 1}", "{reference 2}"]
    metrics: "{success metrics if applicable}"
  
  reusability: "high/medium/low"
  
  institutionalized_in:
    - file: "{instruction file or skill}"
      section: "{section name}"
```

---

## Integration with Sacred Geometry & PAOAL

### Spiral Gate Integration

**In Critic validation**:
```yaml
sacred_geometry:
  spiral:
    lessons_documented: ✅/❌
    patterns_extracted: ✅/❌  
    memory_updated: ✅/❌
    
    # Pass criteria: 2/3 checks ✅
    result: PASS/FAIL
```

**Spiral gate passes when**:
- Lessons captured (using this learning system) ✅
- Patterns extracted (if applicable) ✅
- Memory updated (triple storage executed) ✅

### PAOAL Log Phase Integration

**In Executor evidence bundle**:
```yaml
paoal:
  log:
    lessons_learned:
      - learning_id: "L-2025-Q4-042"
        lesson: "{lesson text}"
        category: "technical"
        stored: ✅
    
    patterns_extracted:
      - pattern_id: "P-security-003"
        pattern: "{pattern name}"
        extracted_from: ["L-2025-Q4-042"]
    
    storage_status:
      vibe_learn: ✅
      agent_memory: ✅
      file_system: ✅
```

### AAR Integration

**In Recorder After Action Review**:
```yaml
aar:
  lessons_learned:
    - learning_id: "L-{id}"  # Generated by learning system
      lesson: "{lesson}"
      priority: "high"
      effectiveness: "untested"  # Will be tracked over time
  
  patterns_extracted:
    - pattern_id: "P-{id}"  # If pattern extracted
      pattern: "{pattern}"
      reusability: "high"
```

---

## Queryability & Reuse

### Querying Learnings

**Via agent-memory (if available)**:
```python
# Find learnings by category
agent_memory.query(
    tags=["technical", "security"],
    type="learning"
)

# Find high-priority learnings
agent_memory.query(
    filter="priority=high",
    type="learning"
)

# Find learnings for specific context
agent_memory.query(
    tags=["authentication", "password"],
    type="learning"
)
```

**Via file system (always available)**:
```bash
# Search learning files
grep -r "authentication" .github/learnings/

# Find recent learnings
ls -lt .github/learnings/2025/Q4/

# Find high-effectiveness learnings
grep "effectiveness_score.*[0-9]\." .github/learnings/**/*.md | grep -v "0\."
```

### Applying Learnings Proactively

**Before starting similar work**:
```markdown
1. Query agent-memory for related learnings
2. Review learnings from same category
3. Apply lessons proactively (prevention)
4. Increment times_prevented_issue if prevented issue
```

**Example**:
```markdown
**@executor preparing to implement authentication**:

Before implementation, query learnings:
```python
learnings = agent_memory.query(tags=["authentication", "security"])
```

Found 3 relevant learnings:
- L-2025-Q4-008: "Always use bcrypt, never SHA-256 for passwords"
- L-2025-Q4-015: "Validate email format with RFC 5322 regex"
- L-2025-Q4-023: "Rate limit auth endpoints (3 requests/hour)"

Applying these lessons proactively in implementation plan...

[Implementation proceeds with lessons applied]

[After successful implementation]:
Update learnings:
- L-2025-Q4-008: times_prevented_issue +1 (avoided weak hashing)
- L-2025-Q4-015: times_referenced +1
- L-2025-Q4-023: times_prevented_issue +1 (prevented abuse vector)
```

---

## Learning Examples

### Example 1: Technical Learning

```yaml
learning:
  id: "L-2025-Q4-042"
  timestamp: "2025-12-31T15:30:00Z"
  category: "technical"
  
  parent_linkage:
    task_id: "FEAT-456"
    project_id: "AUTH-REDESIGN"
  
  what_happened: |
    Email validation regex accepted invalid addresses like "a@b"
  
  what_was_expected: |
    Email validation should reject malformed addresses per RFC 5322
  
  variance: |
    Regex pattern was too permissive (`.+@.+` instead of RFC 5322 compliant)
  
  problem_created: |
    Security vulnerability - invalid emails accepted into system
  
  why_problem: |
    Used overly simple regex pattern without validating against RFC standard
  
  how_fixed: |
    Replaced with RFC 5322 compliant regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
  
  lesson: |
    Always validate email addresses using RFC 5322 compliant regex, not simple patterns.
    Simple patterns like `.+@.+` are insufficient and create security vulnerabilities.
    Test with invalid inputs like "a@b", "user@", "@domain" to verify rejection.
  
  pattern:
    name: "RFC Compliance for Input Validation"
    description: "Use standards-compliant validation patterns instead of ad-hoc regex"
    when_to_use: "Email, URL, phone number, or any standardized format validation"
    when_not_to_use: "Internal identifiers or custom formats with no standard"
    confidence: "high"
  
  applies_to:
    - "Email validation in forms"
    - "User registration"
    - "Contact information collection"
    - "API input validation"
  
  priority: "high"
  reuse_potential: "high"
  
  evidence:
    test_results: "tests/test_email_validation.py::test_invalid_formats"
    code_changes: "commit abc123: Fix email regex in auth.py:78"
    metrics: "100% of invalid test cases now properly rejected"
  
  impact:
    times_referenced: 5
    times_prevented_issue: 3
    times_ineffective: 0
    effectiveness_score: 0.6  # (3-0)/5 = high effectiveness
  
  storage:
    vibe_learn_called: true
    agent_memory_key: "learning/technical/L-2025-Q4-042"
    file_path: ".github/learnings/2025/Q4/technical/L-2025-Q4-042.md"
    indexed: true
```

### Example 2: Process Learning

```yaml
learning:
  id: "L-2025-Q4-051"
  timestamp: "2025-12-31T16:45:00Z"
  category: "process"
  
  parent_linkage:
    task_id: "FEAT-478"
    project_id: "API-OPTIMIZATION"
  
  what_happened: |
    Implementation took 8 hours instead of estimated 3 hours
  
  what_was_expected: |
    Implementation should have completed in approximately 3 hours
  
  variance: |
    2.6x estimate overage due to missing sequential_thinking in planning phase
  
  problem_created: |
    Underestimate caused timeline slip and required rework
  
  why_problem: |
    Jumped directly to implementation without systematic planning
  
  how_fixed: |
    Backtracked to planning, used sequential_thinking to design approach systematically
  
  lesson: |
    Always use sequential_thinking MCP tool in PAOAL Plan phase for MEDIUM/COMPLEX tasks.
    Systematic planning catches issues before implementation and improves estimate accuracy.
    The 10 minutes spent planning saves hours in rework.
  
  pattern:
    name: "Sequential Thinking for Planning"
    description: "Use sequential_thinking MCP tool for systematic approach design before implementation"
    when_to_use: "MEDIUM (3-5 files) or COMPLEX (6+ files) tasks"
    when_not_to_use: "SIMPLE tasks (1-2 files) with well-understood approach"
    confidence: "high"
  
  applies_to:
    - "PAOAL Plan phase (all MEDIUM/COMPLEX tasks)"
    - "Architecture decision making"
    - "Multi-option technical decisions"
  
  priority: "high"
  reuse_potential: "high"
  
  evidence:
    test_results: "N/A (process learning)"
    code_changes: "N/A (planning improvement)"
    metrics: "Estimate variance: 3h → 8h (before), 5h → 6h (after applying learning)"
  
  impact:
    times_referenced: 8
    times_prevented_issue: 6
    times_ineffective: 0
    effectiveness_score: 0.75  # (6-0)/8 = very high effectiveness
  
  storage:
    vibe_learn_called: true
    agent_memory_key: "learning/process/L-2025-Q4-051"
    file_path: ".github/learnings/2025/Q4/process/L-2025-Q4-051.md"
    indexed: true
```

---

## Migration from Old Learning System

### For Existing Learnings in Instruction Files

**Old format**:
```markdown
## Learnings
* Prefer `const` over `let` whenever possible (3)
* Avoid `any` type (7)
```

**Migration process**:
```markdown
1. For each old learning:
   a. Extract lesson text
   b. Create new learning YAML
   c. Set times_referenced from counter
   d. Add to new learning system
   e. Remove from instruction file (keep link to new location)

2. In instruction file, replace with:
```markdown
## Learnings

See comprehensive learnings in:
- `.github/learnings/INDEX.md` (all learnings by category)
- Query via agent-memory: `tags=["typescript"]` for this file's learnings

Recent learnings from this instruction file:
- L-2025-Q4-001: Prefer `const` over `let` (referenced 3x)
- L-2025-Q4-002: Avoid `any` type (referenced 7x, pattern extracted)
```
```

---

## Quick Reference

### Learning Capture Command

**When user says "learn!"**:
```markdown
1. Extract learning from context (use sequential_thinking if complex)
2. Present learning to user for reflection (1-4 sentences)
3. Refine based on feedback
4. Execute triple storage (vibe_learn + agent-memory + file)
5. Confirm storage with learning ID
```

### Learning Application Command

**Before similar work**:
```markdown
1. Query agent-memory for related learnings
2. Review applicable lessons
3. Apply lessons proactively in plan
4. Track prevention (increment times_prevented_issue)
```

### Effectiveness Review Command

**Periodic review (monthly)**:
```markdown
1. List learnings with effectiveness_score < 0
2. Review ineffective learnings
3. Refine or deprecate as needed
4. Promote high-effectiveness learnings to patterns
```

---

## Version History

**v2.0** (ContextForge-aligned):
- Integrated Sacred Geometry Spiral gate
- Added UCL compliance (parent linkage, complete evidence)
- Implemented triple storage (vibe_learn + agent-memory + files)
- Added impact tracking and effectiveness scoring
- Added pattern extraction and promotion
- Integrated with PAOAL and AAR frameworks

**v1.1** (original):
- Simple counter-based tracking in instruction files

---

**Document**: ContextForge Learning System  
**Version**: 2.0  
**Framework**: Sacred Geometry Spiral + UCL + Triple Storage  
**Last Updated**: 2025-12-31
