---
applyTo: "research*, investigate*, explore*, study*, learn*, documentation*, reference*, microsoft*, context7*"
description: "Research protocols using context7 and Microsoft Learn for comprehensive technical investigation"
version: "1.0"
framework: "Evidence-Based Research with Adversarial Validation"
---

# ContextForge Research Framework

**Philosophy**: "Trust Nothing, Verify Everything" + "Workspace First" + "Context Before Action"

**Primary Tools**:
- **context7**: Web and codebase search with context awareness
- **Microsoft Learn**: Official Microsoft documentation and learning paths
- **web_search**: General web search for current information
- **web_fetch**: Retrieve complete web pages

---

## Research Protocol Hierarchy

**Priority Order** (use in this sequence):

```
1. Workspace Search (highest priority)
   ↓ (if not found in workspace)
2. Project Knowledge Search
   ↓ (if not found in project)
3. context7 Search (contextual web/code search)
   ↓ (if Microsoft-specific)
4. Microsoft Learn (official Microsoft docs)
   ↓ (if current events/general)
5. web_search + web_fetch (general web)
```

**Critical Rule**: Always search workspace and project knowledge BEFORE external research

---

## Tool Capabilities

### 1. context7

**Best For**:
- Contextual web search with code awareness
- Finding implementation examples across codebases
- Discovering patterns in open-source projects
- Technical stack research (libraries, frameworks)
- Architecture patterns and best practices
- Community knowledge (Stack Overflow, GitHub issues)

**When to Use**:
- "How do others implement [feature] in [technology]?"
- "Find examples of [pattern] in [language]"
- "What are best practices for [technical topic]?"
- "Search for [library] usage patterns"
- "Find similar implementations of [feature]"

**Example Queries**:
```
# Good context7 queries (specific + technical)
context7: "FastAPI JWT authentication with refresh tokens"
context7: "React 19 useActionState hook examples"
context7: "PostgreSQL connection pooling best practices"
context7: "Python async error handling patterns"

# Bad context7 queries (too broad)
context7: "authentication" (too vague)
context7: "how to code" (too general)
```

---

### 2. Microsoft Learn

**Best For**:
- Official Microsoft product documentation
- Azure service references
- Microsoft 365 APIs and SDKs
- Power Platform guidance
- .NET framework documentation
- Windows Server administration
- SQL Server documentation
- Microsoft Graph API references

**When to Use**:
- Any Microsoft technology question
- Azure architecture decisions
- Microsoft Graph API usage
- Power Automate/Power Apps development
- .NET best practices
- Microsoft 365 integration
- Official feature documentation
- Version-specific guidance

**Example Queries**:
```
# Microsoft-specific queries (always use Microsoft Learn first)
ms-learn: "Microsoft Graph API batch requests"
ms-learn: "Azure Functions consumption plan limits"
ms-learn: "Power Automate HTTP action authentication"
ms-learn: "SharePoint REST API metadata"
ms-learn: ".NET 8 minimal APIs"
ms-learn: "Entra ID application permissions"

# When to NOT use Microsoft Learn
ms-learn: "React components" (not Microsoft-specific)
ms-learn: "PostgreSQL optimization" (not Microsoft product)
```

**Microsoft Product Detection**:
- Keywords: Azure, Graph, Entra, SharePoint, Power, .NET, SQL Server, Windows, Microsoft 365, Teams, Dynamics
- If query mentions these → **Microsoft Learn FIRST**

---

### 3. web_search + web_fetch

**Best For**:
- Current events and news
- General technical topics
- Non-Microsoft technologies
- Community consensus on tools
- Benchmark comparisons
- Recent developments (past week/month)

**When to Use**:
- "What's the latest version of [tool]?"
- "Compare [technology A] vs [technology B]"
- "Recent security vulnerabilities in [package]"
- "[Technology] release notes"

**Pattern**:
```bash
# Always use web_fetch after web_search for detailed content
web_search: "FastAPI vs Flask 2024 comparison"
# Then fetch top results:
web_fetch: [URL from search results]
```

---

## Research Workflows by Agent

### Orchestrator - Planning Research

**Before classifying complexity**:

```markdown
**@orchestrator researches task requirements**:

Step 1: Workspace Discovery
- Search existing codebase for similar implementations
- Check project knowledge for related work

Step 2: Technology Research (if unfamiliar)
- If Microsoft tech → Microsoft Learn
- If general tech → context7
- If current/recent → web_search

Step 3: Pattern Discovery (if COMPLEX)
- Use context7 for architecture patterns
- Use Microsoft Learn for Microsoft-specific patterns
- Document findings in complexity classification

**Evidence Required**:
- What was searched (queries)
- What was found (summaries)
- How it informs complexity classification
```

**Example**:
```markdown
User: "Implement SSO with Entra ID for our FastAPI app"

@orchestrator research sequence:
1. Workspace search: "Entra" "SSO" "authentication"
   - Found: No existing Entra integration
2. Microsoft Learn: "Entra ID OAuth 2.0 FastAPI"
   - Found: Official MSAL Python library, token validation patterns
3. context7: "FastAPI Entra ID integration examples"
   - Found: 3 GitHub repos with implementation patterns
4. Classification: COMPLEX (new integration, security-critical)
```

---

### Executor - Implementation Research

**During PAOAL Plan phase**:

```markdown
**@executor researches implementation approach**:

Step 1: Workspace-First (MANDATORY)
- Search for existing patterns in codebase
- Reuse before reinventing

Step 2: Official Documentation (for libraries/frameworks)
- Microsoft tech → Microsoft Learn
- Other tech → Official docs via context7 or web_search

Step 3: Implementation Examples (if needed)
- context7 for code examples
- Filter for quality (stars, recency, completeness)

Step 4: Edge Cases & Gotchas
- context7 for GitHub issues, Stack Overflow
- Microsoft Learn for known limitations

**Evidence Required**:
- Queries executed
- Examples found and evaluated
- Approach selected with rationale
- Documented in PAOAL plan
```

**Example**:
```markdown
**PAOAL Plan Phase - Research**:

Requirement: Implement password reset with email tokens

Research conducted:
1. Workspace: Found existing email service, token generation utils ✅
2. context7: "Python password reset token best practices"
   - Found: itsdangerous library for secure tokens
   - Found: Token expiration patterns (30-60 minutes standard)
3. Microsoft Learn: N/A (not Microsoft-specific)
4. context7: "FastAPI password reset implementation"
   - Found: 5 examples, selected pattern with email verification

Approach: 
- Reuse workspace email service
- Use itsdangerous for token generation (industry standard)
- 1-hour expiration (security best practice from research)
- Rate limiting (3 requests/hour per IP from examples)

Evidence: Research findings in PAOAL plan section
```

---

### Researcher Agent - Deep Investigation

**When orchestrator determines research needed**:

```markdown
**@researcher conducts comprehensive investigation**:

Triggers:
- Technology unfamiliar to team
- Multiple implementation options
- Architectural decision required
- New integration (external API, service)

Research Process:
1. **Scope Definition** (10 minutes)
   - What specific question needs answering?
   - What decision depends on this research?
   - What's the acceptable time investment?

2. **Systematic Search** (30-90 minutes)
   - Workspace + Project Knowledge (5 min)
   - Official Documentation (15-30 min)
     * Microsoft Learn (if MS tech)
     * context7 for official docs
   - Implementation Examples (15-30 min)
     * context7 for code examples
     * GitHub, Stack Overflow, technical blogs
   - Current State (10-20 min)
     * web_search for recent developments
     * Release notes, security advisories

3. **Adversarial Validation** (20-40 minutes)
   - Challenge findings with skeptical lens
   - Search for counter-examples
   - Identify limitations and gotchas
   - Verify claims with multiple sources

4. **Synthesis & Recommendation** (10-20 minutes)
   - Structured comparison if multiple options
   - Clear recommendation with confidence level
   - Evidence bundle with sources
   - Documented in research artifact

**Output**: Research artifact (Markdown or YAML)
```

---

## Research Artifact Template

```yaml
research:
  id: "RES-{YYYY}-{QQ}-{counter}"
  question: "{Specific question being researched}"
  context: "{Why this research is needed}"
  timestamp: "{ISO 8601}"
  
  search_strategy:
    workspace_search:
      queries: ["{query 1}", "{query 2}"]
      findings: "{What was found or not found}"
    
    microsoft_learn:
      queries: ["{query 1}"] # if applicable
      findings: "{Official documentation findings}"
      references: ["{URL 1}", "{URL 2}"]
    
    context7_search:
      queries: ["{query 1}", "{query 2}"]
      findings: "{Code examples, patterns found}"
      quality_assessment: "{How examples were evaluated}"
    
    web_search:
      queries: ["{query 1}"] # if needed
      findings: "{General web findings}"
      currency: "{How recent is information}"
  
  options_evaluated:
    - option: "{Option 1}"
      pros: ["{pro 1}", "{pro 2}"]
      cons: ["{con 1}", "{con 2}"]
      evidence: "{Sources}"
      
    - option: "{Option 2}"
      pros: ["{pro 1}"]
      cons: ["{con 1}"]
      evidence: "{Sources}"
  
  recommendation:
    selected_option: "{Option X}"
    rationale: |
      {Why this option was selected}
      {Evidence supporting decision}
    confidence: "high/medium/low"
    caveats: ["{caveat 1}", "{caveat 2}"]
  
  adversarial_validation:
    challenges_considered:
      - challenge: "{Counter-argument}"
        response: "{How addressed}"
    
    limitations: ["{limitation 1}", "{limitation 2}"]
    
    verification:
      sources_count: {number}
      sources_agreement: "unanimous/majority/divided"
  
  time_investment:
    estimated_minutes: {number}
    actual_minutes: {number}
    
  next_steps:
    - "{Action 1}"
    - "{Action 2}"
```

---

## Research Query Patterns

### Effective context7 Queries

**Pattern**: `{technology} + {specific feature} + {implementation detail}`

```
✅ Good:
- "React 19 server components data fetching"
- "PostgreSQL JSONB indexing strategies"
- "FastAPI background tasks with celery"
- "Python async database connection pooling"

❌ Bad:
- "React" (too broad)
- "database" (too vague)
- "how to authenticate" (too general)
```

---

### Effective Microsoft Learn Queries

**Pattern**: `{Microsoft product} + {specific API/feature} + {use case}`

```
✅ Good:
- "Microsoft Graph batch requests pagination"
- "Azure Functions durable entities"
- "Power Automate custom connector OAuth"
- "SharePoint REST API CAML query"

❌ Bad:
- "Microsoft API" (too vague)
- "Azure" (too broad)
- "Power Automate help" (too general)
```

---

### Effective web_search Queries

**Pattern**: `{technology} + {version/year} + {specific topic}`

```
✅ Good:
- "FastAPI 0.109 breaking changes"
- "React 19 migration guide 2024"
- "PostgreSQL 16 performance improvements"
- "Python 3.12 new features"

❌ Bad:
- "FastAPI updates" (too vague)
- "React migration" (missing version)
```

---

## Integration with PAOAL

### PAOAL Plan Phase Enhancement

```yaml
paoal:
  plan:
    # Existing fields
    approach: "{strategy}"
    estimate: {loc, time}
    
    # NEW: Research section
    research:
      workspace_search:
        queries: ["{query}"]
        reusable_found: true/false
        components_reused: ["{component 1}"]
      
      external_research:
        microsoft_learn:
          queries: ["{query}"] # if MS tech
          findings: "{summary}"
        
        context7:
          queries: ["{query}"]
          examples_found: {count}
          pattern_selected: "{pattern name}"
        
        web_search:
          queries: ["{query}"] # if needed
          findings: "{summary}"
      
      time_spent_minutes: {number}
      key_findings:
        - "{finding 1}"
        - "{finding 2}"
      
      decisions_informed:
        - decision: "{what was decided}"
          based_on: "{research finding}"
```

---

## Research Quality Standards

### Minimum Research Requirements

**SIMPLE tasks**:
- Workspace search: REQUIRED
- External research: OPTIONAL (only if unfamiliar tech)

**MEDIUM tasks**:
- Workspace search: REQUIRED
- Project knowledge search: REQUIRED
- Official docs (MS Learn or context7): REQUIRED
- Implementation examples (context7): RECOMMENDED

**COMPLEX tasks**:
- Workspace search: REQUIRED
- Project knowledge search: REQUIRED
- Official docs: REQUIRED
- Implementation examples: REQUIRED
- Adversarial validation: REQUIRED
- Research artifact: REQUIRED

---

### Evidence Standards

**For each research query**:
- Document what was searched
- Document what was found (or not found)
- Assess quality of findings (source credibility, recency, completeness)
- Explain how findings inform decisions

**Source Quality Assessment**:

```
High Quality:
- Official documentation (Microsoft Learn, official repos)
- Recent (< 1 year old)
- Maintained projects (active commits)
- Multiple confirming sources

Medium Quality:
- Community tutorials (reputable blogs)
- Moderately recent (1-2 years)
- Stack Overflow accepted answers
- Single source but authoritative

Low Quality:
- Outdated (> 2 years old)
- Unmaintained projects
- Unverified claims
- No supporting evidence
```

**Minimum**: Medium quality or better for production decisions

---

## Adversarial Research Protocol

**When to Use**: COMPLEX tasks, architectural decisions, security-critical features

**Process**:

```markdown
1. Primary Research (gather evidence)
   - Use all available tools systematically
   - Document findings

2. Adversarial Challenge (skeptical review)
   - What could go wrong with this approach?
   - What are we assuming that might be false?
   - What sources contradict our findings?
   - What edge cases are we missing?

3. Counter-Research (test challenges)
   - Search specifically for counter-examples
   - Look for "X doesn't work when Y" 
   - Find limitations and gotchas
   - Verify assumptions

4. Synthesis (balanced conclusion)
   - Acknowledge limitations
   - Document caveats
   - Provide confidence level
   - Note what's still uncertain
```

---

## Research Checklist (Before Implementation)

**Executor must complete BEFORE coding**:

```markdown
Research Checklist (PAOAL Plan):

Workspace Discovery:
- [ ] Searched codebase for existing implementations
- [ ] Searched project knowledge for related work
- [ ] Identified reusable components

Technology Research:
- [ ] Official documentation reviewed
  - [ ] Microsoft Learn (if MS tech)
  - [ ] context7 for official docs (other tech)
- [ ] Implementation examples evaluated
  - [ ] context7 search conducted
  - [ ] Quality assessment completed
  - [ ] Pattern selected and justified

Decision Validation:
- [ ] Multiple sources confirm approach
- [ ] Edge cases identified
- [ ] Limitations documented
- [ ] Security implications considered (if applicable)

Evidence:
- [ ] All queries documented
- [ ] Key findings summarized
- [ ] Sources referenced
- [ ] Time investment recorded

Ready to implement: YES / NO (if NO, continue research)
```

---

## Examples by Scenario

### Example 1: Microsoft-Specific Implementation

**Scenario**: Implement Microsoft Graph API batch requests

```markdown
**Research Sequence**:

1. Workspace Search:
   - Query: "Graph" "batch" "API"
   - Result: No existing batch implementation found

2. Microsoft Learn (PRIMARY):
   - Query: "Microsoft Graph JSON batching"
   - Found: Official batching documentation
   - Found: Request/response format specification
   - Found: Batching limits (20 requests per batch)
   - References: 
     * https://learn.microsoft.com/graph/json-batching
     * https://learn.microsoft.com/graph/sdks/batch-requests

3. context7 (SUPPLEMENTARY):
   - Query: "Microsoft Graph batch requests Python example"
   - Found: 3 implementation examples
   - Evaluated: Selected pattern with error handling
   - Reference: GitHub repo with 500+ stars, recently updated

4. Decision:
   - Use official MSAL library
   - Batch size: 20 (Microsoft limit)
   - Error handling: Individual request status checking
   - Retry logic: Exponential backoff for rate limits
   
Confidence: HIGH (official documentation + verified examples)
Time: 45 minutes
```

---

### Example 2: Non-Microsoft Technology

**Scenario**: Implement Redis caching for FastAPI

```markdown
**Research Sequence**:

1. Workspace Search:
   - Query: "Redis" "cache" "FastAPI"
   - Result: Found existing Redis connection utility ✅

2. context7 (PRIMARY for non-MS tech):
   - Query: "FastAPI Redis caching decorator pattern"
   - Found: 5 implementation examples
   - Evaluated: Selected pattern with TTL support
   - Best example: GitHub repo with 1.2k stars, active maintenance

3. context7 (VALIDATION):
   - Query: "FastAPI Redis connection pooling best practices"
   - Found: Connection pool management patterns
   - Found: async Redis client recommendations (aioredis)

4. web_search (CURRENT STATE):
   - Query: "Redis Python client 2024 best practices"
   - Found: redis-py 5.0 released (async support native)
   - Found: aioredis merged into redis-py

5. Decision:
   - Reuse workspace Redis connection utility
   - Use redis-py 5.0 (native async)
   - Cache decorator pattern from context7 example
   - TTL: Configurable per endpoint (default 5 minutes)
   
Confidence: HIGH (workspace reuse + verified patterns + current library)
Time: 35 minutes
```

---

### Example 3: Architecture Decision (COMPLEX)

**Scenario**: Choose between monolithic vs microservices for new feature set

```markdown
**Research Sequence** (Researcher Agent):

1. Workspace + Project Knowledge:
   - Current architecture: Monolithic FastAPI app
   - Team size: 4 developers
   - Deployment: Azure App Service

2. context7 - Monolithic Patterns:
   - Query: "FastAPI modular monolith architecture"
   - Found: 10+ examples of well-structured monoliths
   - Pattern: Feature-based modules within single app

3. context7 - Microservices Patterns:
   - Query: "FastAPI microservices architecture"
   - Found: 8 examples with service communication
   - Complexity: Service discovery, API gateway, distributed tracing

4. Microsoft Learn - Azure Considerations:
   - Query: "Azure microservices architecture patterns"
   - Found: Official guidance on when to use microservices
   - Key: Team size < 10 → monolith often better

5. Adversarial Validation:
   - Challenge: "Microservices offer better scalability"
   - Counter-research: "microservices complexity overhead small teams"
   - Finding: Coordination overhead outweighs benefits for small teams
   
6. Synthesis:
   - Option A (Modular Monolith):
     * Pros: Simpler deployment, easier debugging, team size appropriate
     * Cons: Scaling entire app (acceptable for current load)
   - Option B (Microservices):
     * Pros: Independent scaling, technology diversity
     * Cons: Deployment complexity, distributed debugging, overhead
   
7. Recommendation: MODULAR MONOLITH
   - Rationale: Team size (4), current load, deployment simplicity
   - Confidence: HIGH
   - Caveat: Reevaluate if team grows > 10 or scaling needs change
   
Time: 2 hours
Evidence: Research artifact RES-2025-Q4-001.md created
```

---

## Anti-Patterns to Avoid

### ❌ Don't Skip Workspace Search

```markdown
# WRONG
@executor: Implementing password reset
[Immediately searches context7 for examples]

# CORRECT
@executor: Implementing password reset
Step 1: Workspace search for existing auth patterns
Found: Email service, token utils → REUSE THESE
Step 2: context7 for password reset patterns specifically
```

---

### ❌ Don't Use Wrong Tool for Microsoft Tech

```markdown
# WRONG
User: "How do I authenticate with Microsoft Graph?"
@executor uses context7 first

# CORRECT
User: "How do I authenticate with Microsoft Graph?"
@executor uses Microsoft Learn FIRST (official source)
Then context7 for implementation examples
```

---

### ❌ Don't Accept First Result Without Validation

```markdown
# WRONG
context7: "FastAPI authentication"
[Takes first result, implements immediately]

# CORRECT
context7: "FastAPI authentication"
[Evaluates 3-5 results]
[Checks: recency, stars, maintenance, security practices]
[Selects best pattern with justification]
```

---

## Integration with Agent Files

### Add to triad-orchestrator.agent.md

```markdown
## Research Protocol (Before Classification)

For UNFAMILIAR technology or NEW integrations:

1. Quick research (10-15 minutes):
   - Workspace: Check for existing work
   - Microsoft Learn: If MS tech
   - context7: If other tech
   
2. Inform complexity classification:
   - Known patterns → SIMPLE/MEDIUM
   - Unknown territory → MEDIUM/COMPLEX
   - Multiple options → COMPLEX (requires researcher agent)

3. Document research in classification:
   - What was searched
   - What was found
   - How it informed routing decision
```

---

### Add to triad-executor.agent.md

```markdown
## PAOAL Plan: Research Requirements

BEFORE proposing implementation approach:

**Research Checklist**:
- [ ] Workspace search completed
- [ ] Project knowledge checked
- [ ] Official documentation reviewed (MS Learn or context7)
- [ ] Implementation examples evaluated (if needed)
- [ ] Research documented in plan

**Research Section in PAOAL Plan**:
```yaml
research:
  workspace: "{what found or not found}"
  official_docs: "{Microsoft Learn or context7 findings}"
  examples: "{context7 patterns evaluated}"
  decisions: "{how research informed approach}"
```

**Minimum Time**: 
- SIMPLE: 5 minutes (workspace only)
- MEDIUM: 15-30 minutes (workspace + docs + examples)
- COMPLEX: 30-90 minutes (comprehensive research)
```

---

## Quick Reference

### Research Decision Tree

```
Question: Where should I research this?

├─ Is it in our workspace?
│  └─ YES → Use workspace code ✅ STOP
│  └─ NO → Continue ↓
│
├─ Is it Microsoft technology?
│  └─ YES → Microsoft Learn FIRST
│  └─ NO → Continue ↓
│
├─ Need implementation examples?
│  └─ YES → context7
│  └─ NO → Continue ↓
│
├─ Need current information?
│  └─ YES → web_search + web_fetch
│  └─ NO → Done
```

---

### Tool Selection Matrix

| Scenario | Primary Tool | Secondary Tool | Time |
|----------|--------------|----------------|------|
| Existing workspace code | Workspace search | None | 5 min |
| Microsoft Graph API | Microsoft Learn | context7 (examples) | 20 min |
| Azure architecture | Microsoft Learn | context7 (patterns) | 30 min |
| React implementation | context7 | web_search (current) | 20 min |
| PostgreSQL optimization | context7 | web_search (benchmarks) | 25 min |
| Security best practices | context7 + MS Learn | web_search (advisories) | 40 min |
| Architecture decision | context7 | Researcher agent | 60-120 min |

---

## Version

**Document**: ContextForge Research Framework  
**Version**: 1.0  
**Tools**: context7 + Microsoft Learn + web_search + web_fetch  
**Integration**: PAOAL + Adversarial Research  
**Last Updated**: 2025-12-31
