# Idea Capture System

**Version**: 1.0.0
**Created**: 2025-11-11
**Status**: Active

---

## Purpose

The ContextForge Idea Capture System provides a friction-free method to capture, enrich, and promote ideas into actionable tasks using the 13-dimensional Context Ontology Framework (COF). This system bridges the gap between inspiration and execution, ensuring no valuable idea is lost while maintaining the rigor required for production work.

**Key Objectives**:
- Enable rapid idea capture with minimal friction
- Automatically enrich ideas with COF 13-dimensional context
- Support seamless promotion from idea → task
- Integrate with TaskMan-v2, Workflow Designer, and MCP
- Provide powerful search and retrieval capabilities

---

## Table of Contents

1. [Philosophy & Design Principles](#philosophy--design-principles)
2. [Architecture Overview](#architecture-overview)
3. [COF 13-Dimensional Integration](#cof-13-dimensional-integration)
4. [Capture Methods](#capture-methods)
5. [Idea Lifecycle](#idea-lifecycle)
6. [Promotion to Tasks](#promotion-to-tasks)
7. [Search & Retrieval](#search--retrieval)
8. [Database Schema](#database-schema)
9. [API Reference](#api-reference)
10. [CLI Usage](#cli-usage)
11. [Best Practices](#best-practices)

---

## Philosophy & Design Principles

### Core Principles

**1. Capture First, Perfect Later**

Ideas arrive at inconvenient times. The system prioritizes rapid capture over completeness, allowing refinement in subsequent stages.

```text
┌─────────────────────────────────────────────┐
│  Capture (5 seconds)                        │
│  "Quick thought: Use Redis for caching"     │
└────────────┬────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────┐
│  Enrich (automated, 2-3 seconds)            │
│  COF analysis adds dimensions               │
└────────────┬────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────┐
│  Refine (optional, minutes to days)         │
│  Add details, context, research             │
└────────────┬────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────┐
│  Promote (one-click)                        │
│  Becomes actionable task in TaskMan-v2      │
└─────────────────────────────────────────────┘
```

---

**2. Sacred Geometry Alignment**

**Circle (Completeness)**: All 13 COF dimensions considered for each idea

**Triangle (Stability)**: Three required dimensions for minimum viable capture:
- Motivational (why this idea matters)
- Relational (how it connects to existing work)
- Validation (success criteria)

**Spiral (Iteration)**: Ideas evolve through refinement cycles

**Golden Ratio (Balance)**: 20% of ideas promoted to tasks (focus on vital few)

**Fractal (Modularity)**: Ideas compose into larger initiatives

---

**3. Zero Friction Capture**

The system must be accessible everywhere:
- CLI: `cf-core idea "Quick thought..."`
- API: Single POST endpoint
- Voice: Natural language transcription
- MCP: AI-assisted capture via Claude
- Web UI: Quick-add widget
- Mobile: PWA support

**Friction Budget**: Capture must complete in <10 seconds from initiation to storage.

---

**4. Context-Aware Enrichment**

The system automatically infers COF dimensions using:
- NLP analysis of idea text
- Current project context (active sprint, team, priorities)
- Historical pattern matching (similar ideas, common workflows)
- User preferences and tagging history

---

## Architecture Overview

### System Components

```text
┌──────────────────────────────────────────────────────────────┐
│                    Capture Interfaces                         │
│  CLI │ API │ Voice │ MCP │ Web UI │ Mobile                   │
└───────────┬──────────────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────────────────────────┐
│                  Idea Capture Service                         │
│  - Input validation                                           │
│  - Duplicate detection                                        │
│  - Rate limiting                                              │
└───────────┬──────────────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────────────────────────┐
│              COF Enrichment Engine (AI-Powered)               │
│  - 13-dimensional analysis                                    │
│  - Context inference                                          │
│  - Template matching                                          │
│  - Embedding generation (OpenAI, local models)                │
└───────────┬──────────────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────────────────────────┐
│                PostgreSQL Database (Primary)                  │
│  - ideas table (13 COF dimension columns)                     │
│  - pgvector extension for embeddings                          │
│  - Full-text search indexes                                   │
└───────────┬──────────────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────────────────────────┐
│                   Retrieval & Search                          │
│  - Full-text search (PostgreSQL tsvector)                     │
│  - Semantic search (pgvector similarity)                      │
│  - Graph traversal (relational dimension links)               │
│  - Dimension-based filtering                                  │
└───────────┬──────────────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────────────────────────┐
│                Promotion to TaskMan-v2                        │
│  - One-click task creation                                    │
│  - COF dimensions → task metadata                             │
│  - Evidence bundle generation                                 │
│  - Workflow Designer integration                              │
└──────────────────────────────────────────────────────────────┘
```

---

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | FastAPI 0.100+ | REST API, WebSocket support |
| **Database** | PostgreSQL 15+ | Primary data store with pgvector |
| **Embeddings** | OpenAI text-embedding-3-small | Semantic search (1536 dimensions) |
| **NLP** | spaCy 3.7+ | Text analysis, entity extraction |
| **CLI** | CF_Core (Python) | Command-line interface |
| **Frontend** | React 19 | Web UI for browsing/refinement |
| **MCP** | Claude MCP Server | AI-assisted capture |

---

## COF 13-Dimensional Integration

### Dimension Capture Strategies

Each COF dimension has capture strategies ranging from **required** (must be present) to **optional** (inferred or added during refinement).

#### 1. Motivational Context (REQUIRED)

**Question**: Why does this idea matter?

**Capture Strategy**: Extract from initial input or prompt user

**Example Input**: "Quick thought: Use Redis for caching"

**Enrichment**:
```json
{
  "cof_motivational": "Performance improvement - reduce database load and API latency"
}
```

**NLP Indicators**: Keywords like "improve", "reduce", "faster", "fix", "enable"

---

#### 2. Relational Context (REQUIRED)

**Question**: How does this relate to existing work?

**Capture Strategy**: Link to active tasks, projects, or components

**Example**:
```json
{
  "cof_relational": {
    "relates_to": ["TASK-API-PERF-001", "P-CFWORK-OPTIMIZATION"],
    "blocks": [],
    "depends_on": ["Infrastructure setup"],
    "affects_components": ["backend-api", "TaskMan-v2"]
  }
}
```

**Auto-Inference**: Analyze current sprint, recently accessed tasks, project context

---

#### 3. Dimensional Context (Optional)

**Question**: What is the scope, depth, and integration complexity?

**Capture Strategy**: Infer from text analysis and historical patterns

**Example**:
```json
{
  "cof_dimensional": {
    "scope": "backend-api only",
    "depth": "surface (configuration change)",
    "integration": "1 system (TaskMan-v2)"
  }
}
```

**Auto-Inference**: Keyword analysis ("just config" → surface, "rewrite" → deep)

---

#### 4. Situational Context (Optional)

**Question**: What environmental factors influence this?

**Example**:
```json
{
  "cof_situational": {
    "urgency": "medium",
    "market_pressure": "none",
    "tech_debt": "low",
    "organizational_priority": "P1 (quick wins)"
  }
}
```

---

#### 5. Resource Context (Optional)

**Question**: What resources are needed?

**Example**:
```json
{
  "cof_resource": {
    "team": "Team Alpha (1 FTE)",
    "tools": ["Redis", "redis-py"],
    "budget": "None (open-source)",
    "time_estimate": "2-3 hours"
  }
}
```

**Auto-Inference**: Use DuckDB velocity data for time estimates

---

#### 6. Narrative Context (Optional)

**Question**: What's the user story or business case?

**Example**:
```json
{
  "cof_narrative": "As a developer, I want faster API responses so I can iterate more quickly during development."
}
```

**Template**: "As a [user], I want [goal], so that [benefit]"

---

#### 7. Recursive Context (Optional)

**Question**: How does this iterate and improve?

**Example**:
```json
{
  "cof_recursive": {
    "iteration_strategy": "Start with basic caching, expand to cache invalidation strategies",
    "feedback_loop": "Monitor cache hit rate via Prometheus",
    "learning_capture": "Document cache configuration patterns"
  }
}
```

---

#### 8. Sacred Geometry Context (Auto-Generated)

**Question**: Which Sacred Geometry patterns apply?

**Example**:
```json
{
  "cof_sacred_geometry": {
    "triangle": "Stable infrastructure pattern",
    "circle": "Complete caching strategy (read + write + invalidate)",
    "spiral": "Iterative: basic → advanced invalidation → distributed cache",
    "golden_ratio": "20% effort for 80% latency improvement",
    "fractal": "Reusable caching module for all services"
  }
}
```

**Auto-Inference**: Pattern matching against known Sacred Geometry applications

---

#### 9. Computational Context (Optional)

**Question**: What algorithms or data structures are involved?

**Example**:
```json
{
  "cof_computational": {
    "data_structures": "Hash map (Redis key-value store)",
    "algorithms": "LRU eviction policy",
    "complexity": "O(1) reads and writes",
    "scalability": "Vertical scaling to 100GB RAM"
  }
}
```

---

#### 10. Emergent Context (Placeholder)

**Question**: What unexpected insights might arise?

**Capture Strategy**: Leave empty initially, populate during implementation

**Example**:
```json
{
  "cof_emergent": "TBD - capture discoveries during implementation"
}
```

---

#### 11. Temporal Context (Optional)

**Question**: When does this need to happen?

**Example**:
```json
{
  "cof_temporal": {
    "deadline": "2025-12-01",
    "milestone": "Q4 Performance Initiative",
    "sequencing": "After PostgreSQL migration completes"
  }
}
```

---

#### 12. Spatial Context (Optional)

**Question**: Which teams/environments are involved?

**Example**:
```json
{
  "cof_spatial": {
    "team": "Team Alpha (Backend)",
    "environment": "Development → Staging → Production",
    "deployment": "Kubernetes cluster (us-east-1)"
  }
}
```

---

#### 13. Validation Context (REQUIRED)

**Question**: How do we know this succeeds?

**Capture Strategy**: Prompt for success criteria

**Example**:
```json
{
  "cof_validation": {
    "success_criteria": [
      "API p95 latency reduces from 450ms to <200ms",
      "Cache hit rate >80%",
      "No cache-related bugs in production"
    ],
    "measurement": "Prometheus metrics, load testing with Locust"
  }
}
```

---

## Capture Methods

### 1. CLI Capture (Fastest)

**Basic Capture** (5 seconds):
```bash
# Minimal capture
cf-core idea "Use Redis for API caching"

# With motivational context
cf-core idea "Use Redis for API caching" --why "Reduce latency by 50%"

# Link to existing task
cf-core idea "Use Redis for API caching" --relates-to TASK-API-PERF-001

# Add tags
cf-core idea "Use Redis for API caching" --tags performance,backend,quick-win
```

**Output**:
```text
✓ Idea captured: IDEA-20251111-001
  Title: Use Redis for API caching
  Status: captured
  COF Dimensions: 3/13 complete (Motivational, Relational, Validation)

View: cf-core idea show IDEA-20251111-001
Refine: cf-core idea refine IDEA-20251111-001
Promote: cf-core idea promote IDEA-20251111-001
```

---

**Interactive Capture** (30-60 seconds):
```bash
cf-core idea create --interactive

# Prompts:
# 1. Idea title (required): Use Redis for API caching
# 2. Why does this matter? (motivational): Reduce API latency
# 3. Related to existing tasks? (relational): TASK-API-PERF-001
# 4. Success criteria? (validation): p95 latency <200ms
# 5. Tags (optional): performance, backend
```

---

### 2. API Capture

**Endpoint**: `POST /api/v1/ideas`

**Minimal Request**:
```json
{
  "title": "Use Redis for API caching",
  "description": "Add Redis caching layer to reduce database queries",
  "cof_motivational": "Improve API performance",
  "cof_validation": {
    "success_criteria": ["p95 latency <200ms"]
  }
}
```

**Full Request** (with all dimensions):
```json
{
  "title": "Use Redis for API caching",
  "description": "Add Redis caching layer to reduce database queries and improve API response times for read-heavy endpoints",

  "cof_motivational": "Reduce API p95 latency from 450ms to <200ms, improving developer experience",
  "cof_relational": {
    "relates_to": ["TASK-API-PERF-001"],
    "affects_components": ["backend-api", "TaskMan-v2"]
  },
  "cof_dimensional": {
    "scope": "backend-api",
    "depth": "surface (configuration)",
    "integration": "1 system"
  },
  "cof_situational": {
    "urgency": "medium",
    "organizational_priority": "P1"
  },
  "cof_resource": {
    "team": "Team Alpha (1 FTE)",
    "tools": ["Redis", "redis-py"],
    "time_estimate": "2-3 hours"
  },
  "cof_narrative": "As a developer, I want faster API responses so I can iterate more quickly",
  "cof_recursive": {
    "iteration_strategy": "Start basic, add invalidation later"
  },
  "cof_sacred_geometry": {
    "triangle": "Stable infrastructure",
    "fractal": "Reusable caching module"
  },
  "cof_computational": {
    "data_structures": "Hash map (Redis)",
    "complexity": "O(1)"
  },
  "cof_temporal": {
    "milestone": "Q4 Performance Initiative"
  },
  "cof_spatial": {
    "team": "Team Alpha",
    "environment": "Dev → Staging → Prod"
  },
  "cof_validation": {
    "success_criteria": [
      "p95 latency <200ms",
      "Cache hit rate >80%"
    ],
    "measurement": "Prometheus metrics"
  },

  "tags": ["performance", "backend", "quick-win"]
}
```

**Response**:
```json
{
  "idea_id": "IDEA-20251111-001",
  "title": "Use Redis for API caching",
  "status": "captured",
  "created_at": "2025-11-11T14:23:45Z",
  "enrichment_status": "complete",
  "cof_completeness": {
    "required": "3/3",
    "optional": "8/10",
    "total": "11/13"
  },
  "_links": {
    "self": "/api/v1/ideas/IDEA-20251111-001",
    "refine": "/api/v1/ideas/IDEA-20251111-001/refine",
    "promote": "/api/v1/ideas/IDEA-20251111-001/promote"
  }
}
```

---

### 3. Voice Capture

**Flow**:
1. User speaks: "I have an idea to use Redis for API caching to reduce latency"
2. Transcription service (Whisper, Google Speech-to-Text) → text
3. COF enrichment engine extracts dimensions from transcript
4. User reviews and confirms capture

**CLI Usage**:
```bash
# Record voice note
cf-core idea voice

# Press Ctrl+C when done speaking
# Transcription: "I have an idea to use Redis for API caching to reduce latency"
# COF Analysis:
#   - Motivational: Performance improvement (reduce latency)
#   - Validation: <inferred> Measure latency improvement
#
# Confirm capture? [Y/n]: y
# ✓ Idea captured: IDEA-20251111-002
```

---

### 4. MCP Capture (AI-Assisted)

**Scenario**: User is chatting with Claude and has an idea

**User**: "I'm thinking we should use Redis for caching our API responses. We're seeing 450ms p95 latency and I think we could cut that in half."

**Claude** (via MCP):
```json
{
  "action": "capture_idea",
  "payload": {
    "title": "Use Redis for API caching",
    "description": "Add Redis caching layer to reduce API p95 latency from 450ms to <225ms",
    "cof_motivational": "Improve API performance - reduce p95 latency by 50%",
    "cof_validation": {
      "success_criteria": [
        "p95 latency reduces from 450ms to <225ms",
        "Cache hit rate >75%"
      ]
    },
    "source": "claude-conversation",
    "context": "User expressed concern about current API performance"
  }
}
```

**Claude Response**: "I've captured your idea as IDEA-20251111-003. Would you like me to help refine any of the COF dimensions or promote it to a task?"

---

## Idea Lifecycle

### Status States

```text
┌──────────┐
│ captured │  Initial state after capture
└────┬─────┘
     ↓
┌──────────┐
│ refining │  User actively adding context/dimensions
└────┬─────┘
     ↓
┌──────────┐
│ refined  │  COF dimensions sufficiently complete
└────┬─────┘
     ↓
┌──────────┐
│ promoted │  Converted to task in TaskMan-v2
└────┬─────┘
     ↓
┌──────────┐
│ archived │  Not promoted but kept for future reference
└──────────┘
```

### State Transitions

**captured → refining**: User starts editing idea
**refining → refined**: COF completeness ≥ 8/13 dimensions
**refined → promoted**: User clicks "Promote to Task"
**captured → archived**: User archives without promotion
**refined → archived**: User decides not to pursue

---

### Refinement Process

**Goal**: Progressively add COF dimensions to reach "refined" state

**CLI Workflow**:
```bash
# View idea with current COF completeness
cf-core idea show IDEA-20251111-001

# Output:
# ┌────────────────────────────────────────────────────┐
# │ IDEA-20251111-001: Use Redis for API caching      │
# ├────────────────────────────────────────────────────┤
# │ Status: captured                                   │
# │ COF Completeness: 3/13 (23%)                       │
# │   ✓ Motivational (required)                        │
# │   ✓ Relational (required)                          │
# │   ✓ Validation (required)                          │
# │   ✗ Dimensional                                    │
# │   ✗ Situational                                    │
# │   ... (8 more missing)                             │
# └────────────────────────────────────────────────────┘

# Add dimensions interactively
cf-core idea refine IDEA-20251111-001

# Prompts for missing dimensions one at a time:
# 1. Dimensional Context - Scope? [backend-api]: backend-api
# 2. Dimensional Context - Depth? [surface/deep]: surface
# 3. Resource Context - Team? [Team Alpha]: Team Alpha
# 4. Resource Context - Time estimate? [auto-calculate from velocity]: 2-3 hours
# ... continues until user exits or 8/13 reached

# Save and mark as refined
# ✓ Idea refined: IDEA-20251111-001 (8/13 dimensions)
# Ready to promote: cf-core idea promote IDEA-20251111-001
```

---

**Web UI Refinement** (Progressive Disclosure):

```text
┌──────────────────────────────────────────────────────────┐
│ IDEA-20251111-001: Use Redis for API caching            │
├──────────────────────────────────────────────────────────┤
│ Status: captured (23% complete)                          │
│                                                           │
│ Progress: ▰▰▰▱▱▱▱▱▱▱▱▱▱ 3/13 dimensions                │
│                                                           │
│ Required Dimensions: ✓ Complete                          │
│   ✓ Motivational: Reduce API latency                    │
│   ✓ Relational: Links to TASK-API-PERF-001              │
│   ✓ Validation: p95 <200ms, cache hit >80%              │
│                                                           │
│ Quick Wins (add these next):                             │
│   [ + Add Dimensional Context ] (scope, depth)           │
│   [ + Add Resource Context ] (team, time estimate)       │
│   [ + Add Temporal Context ] (deadline, milestone)       │
│                                                           │
│ Optional Dimensions (8 remaining):                       │
│   [Collapsed - expand to add]                            │
│                                                           │
│ [ Promote to Task ] [ Archive ]                          │
└──────────────────────────────────────────────────────────┘
```

---

## Promotion to Tasks

### One-Click Promotion

**Goal**: Convert refined idea → actionable task in TaskMan-v2 with minimal friction

**CLI**:
```bash
cf-core idea promote IDEA-20251111-001

# Output:
# Promoting idea to task...
# ✓ Task created: TASK-20251111-004
# ✓ COF dimensions transferred
# ✓ Evidence bundle generated: EB-IDEA-20251111-001.tar.gz
# ✓ Idea status updated: promoted
#
# View task: cf-core task show TASK-20251111-004
```

---

### Promotion Mapping

**Idea → Task Field Mapping**:

| Idea Field | Task Field | Transformation |
|------------|------------|----------------|
| `title` | `title` | Direct copy |
| `description` | `description` | Direct copy |
| `cof_motivational` | `metadata.motivation` | JSON field |
| `cof_validation.success_criteria` | `acceptance_criteria` | Array → bullet list |
| `cof_resource.time_estimate` | `estimated_hours` | Extract numeric value |
| `cof_temporal.deadline` | `due_date` | Parse date |
| `cof_situational.urgency` | `priority` | Map: high→5, medium→3, low→1 |
| `tags` | `tags` | Direct copy |
| `idea_id` | `metadata.source_idea_id` | Reference for traceability |

---

### Evidence Bundle Generation

**Contents**:
```text
EB-IDEA-{IDEA_ID}-{TIMESTAMP}.tar.gz
├── idea.json                  # Full idea data (13 COF dimensions)
├── enrichment_log.json        # NLP analysis, inference decisions
├── embedding.npy              # 1536-dimensional vector
├── related_ideas.json         # Similar ideas (top 5)
├── promotion_metadata.json    # Promotion timestamp, user, rationale
└── sha256.txt                 # Integrity hash
```

**SHA-256 Hash** (UCL compliance):
```bash
sha256sum EB-IDEA-20251111-001-20251111T142345Z.tar.gz > EB-IDEA-20251111-001.sha256
```

---

### Task Creation with COF Metadata

**TaskMan-v2 Task** (after promotion):

```json
{
  "task_id": "TASK-20251111-004",
  "title": "Use Redis for API caching",
  "description": "Add Redis caching layer to reduce database queries and improve API response times for read-heavy endpoints",
  "status": "todo",
  "priority": 3,
  "estimated_hours": 2.5,
  "due_date": "2025-12-01",
  "tags": ["performance", "backend", "quick-win"],

  "acceptance_criteria": [
    "p95 latency reduces from 450ms to <200ms",
    "Cache hit rate >80%",
    "No cache-related bugs in production"
  ],

  "metadata": {
    "source": "idea_promotion",
    "source_idea_id": "IDEA-20251111-001",
    "cof_13d": {
      "motivational": "Reduce API p95 latency from 450ms to <200ms",
      "relational": {
        "relates_to": ["TASK-API-PERF-001"],
        "affects_components": ["backend-api", "TaskMan-v2"]
      },
      "dimensional": {
        "scope": "backend-api",
        "depth": "surface",
        "integration": "1 system"
      },
      "situational": {
        "urgency": "medium",
        "organizational_priority": "P1"
      },
      "resource": {
        "team": "Team Alpha (1 FTE)",
        "tools": ["Redis", "redis-py"],
        "time_estimate": "2-3 hours"
      },
      "narrative": "As a developer, I want faster API responses",
      "recursive": {
        "iteration_strategy": "Start basic, add invalidation later"
      },
      "sacred_geometry": {
        "triangle": "Stable infrastructure",
        "fractal": "Reusable caching module"
      },
      "computational": {
        "data_structures": "Hash map (Redis)",
        "complexity": "O(1)"
      },
      "emergent": "TBD",
      "temporal": {
        "milestone": "Q4 Performance Initiative"
      },
      "spatial": {
        "team": "Team Alpha",
        "environment": "Dev → Staging → Prod"
      },
      "validation": {
        "success_criteria": ["p95 <200ms", "cache hit >80%"],
        "measurement": "Prometheus metrics"
      }
    },
    "evidence_bundle": "EB-IDEA-20251111-001-20251111T142345Z.tar.gz"
  }
}
```

---

## Search & Retrieval

### Search Methods

#### 1. Full-Text Search (PostgreSQL tsvector)

**Query**: Find ideas mentioning "Redis" or "caching"

```sql
SELECT idea_id, title, description
FROM ideas
WHERE to_tsvector('english', title || ' ' || description) @@ to_tsquery('english', 'Redis | caching')
ORDER BY ts_rank(to_tsvector('english', title || ' ' || description), to_tsquery('english', 'Redis | caching')) DESC
LIMIT 10;
```

**CLI**:
```bash
cf-core idea search "Redis caching"

# Output:
# Found 3 ideas:
#   1. IDEA-20251111-001: Use Redis for API caching (promoted)
#   2. IDEA-20251108-042: Redis cluster setup (archived)
#   3. IDEA-20251105-018: Cache invalidation strategies (refined)
```

---

#### 2. Semantic Search (pgvector)

**Query**: Find ideas semantically similar to "improve performance"

```python
# Generate embedding for search query
query_embedding = openai.Embedding.create(
    input="improve performance",
    model="text-embedding-3-small"
)["data"][0]["embedding"]

# pgvector similarity search
results = db.execute("""
    SELECT idea_id, title, description,
           1 - (embedding <=> %(query_vector)s::vector) AS similarity
    FROM ideas
    WHERE 1 - (embedding <=> %(query_vector)s::vector) > 0.7
    ORDER BY embedding <=> %(query_vector)s::vector
    LIMIT 5
""", {"query_vector": query_embedding})
```

**CLI**:
```bash
cf-core idea search-similar "improve performance" --min-similarity 0.7

# Output:
# Found 5 similar ideas:
#   1. IDEA-20251111-001: Use Redis for API caching (similarity: 0.89)
#   2. IDEA-20251109-023: Database query optimization (similarity: 0.85)
#   3. IDEA-20251107-015: Add CDN for static assets (similarity: 0.78)
#   4. IDEA-20251106-032: Lazy load heavy dependencies (similarity: 0.74)
#   5. IDEA-20251105-011: Implement connection pooling (similarity: 0.72)
```

---

#### 3. Dimension-Based Filtering

**Query**: Find ideas related to "backend-api" component with high priority

```sql
SELECT idea_id, title, status,
       cof_relational->>'affects_components' AS components,
       cof_situational->>'organizational_priority' AS priority
FROM ideas
WHERE cof_relational->>'affects_components' LIKE '%backend-api%'
  AND cof_situational->>'organizational_priority' IN ('P0', 'P1')
  AND status IN ('captured', 'refined')
ORDER BY created_at DESC;
```

**CLI**:
```bash
cf-core idea filter \
  --component backend-api \
  --priority P0,P1 \
  --status captured,refined

# Output:
# Found 8 ideas:
#   1. IDEA-20251111-001: Use Redis for API caching (P1, refined)
#   2. IDEA-20251110-056: Fix JWT authentication bug (P0, captured)
#   ... (6 more)
```

---

#### 4. Graph Traversal (Relational Links)

**Query**: Find all ideas related to TASK-API-PERF-001

```sql
WITH RECURSIVE related_ideas AS (
  -- Base case: Direct relations
  SELECT idea_id, title, cof_relational
  FROM ideas
  WHERE cof_relational->>'relates_to' LIKE '%TASK-API-PERF-001%'

  UNION

  -- Recursive case: Ideas related to related ideas
  SELECT i.idea_id, i.title, i.cof_relational
  FROM ideas i
  INNER JOIN related_ideas r ON i.cof_relational->>'relates_to' LIKE '%' || r.idea_id || '%'
)
SELECT * FROM related_ideas;
```

**CLI**:
```bash
cf-core idea graph TASK-API-PERF-001 --depth 2

# Output (ASCII tree):
# TASK-API-PERF-001 (Reduce API latency)
# ├── IDEA-20251111-001: Use Redis for API caching (promoted)
# │   ├── IDEA-20251110-045: Redis cluster setup
# │   └── IDEA-20251109-032: Cache invalidation strategy
# ├── IDEA-20251110-056: Add database indexes
# └── IDEA-20251109-078: Optimize N+1 queries
```

---

## Database Schema

### Primary Table: ideas

```sql
CREATE TABLE ideas (
    -- Identity
    id SERIAL PRIMARY KEY,
    idea_id VARCHAR(50) UNIQUE NOT NULL,  -- IDEA-YYYYMMDD-NNN format
    title VARCHAR(500) NOT NULL,
    description TEXT,

    -- COF 13 Dimensions (JSONB for flexibility)
    cof_motivational TEXT,               -- Why this idea matters
    cof_relational JSONB,                -- Relations to tasks/projects
    cof_dimensional JSONB,               -- Scope, depth, integration
    cof_situational JSONB,               -- Environmental context
    cof_resource JSONB,                  -- Team, tools, budget
    cof_narrative TEXT,                  -- User story, business case
    cof_recursive JSONB,                 -- Iteration, feedback loops
    cof_sacred_geometry JSONB,           -- Pattern alignment
    cof_computational JSONB,             -- Algorithms, data structures
    cof_emergent TEXT,                   -- Unexpected insights
    cof_temporal JSONB,                  -- Deadlines, milestones
    cof_spatial JSONB,                   -- Team topology, environments
    cof_validation JSONB,                -- Success criteria (REQUIRED)

    -- Metadata
    status VARCHAR(20) DEFAULT 'captured',  -- captured, refining, refined, promoted, archived
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100),  -- User identifier
    promoted_to_task_id VARCHAR(50),  -- Task ID if promoted
    promoted_at TIMESTAMP,
    archived_at TIMESTAMP,

    -- Tags & Classification
    tags TEXT[],  -- Array of tags
    category VARCHAR(50),  -- feature, bug-fix, optimization, research, etc.

    -- Search & Embeddings
    embedding VECTOR(1536),  -- OpenAI text-embedding-3-small
    search_vector TSVECTOR,  -- PostgreSQL full-text search

    -- Evidence & Audit
    evidence_bundle_path VARCHAR(255),  -- Path to evidence bundle
    enrichment_metadata JSONB,  -- NLP analysis, confidence scores

    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('captured', 'refining', 'refined', 'promoted', 'archived'))
);

-- Indexes
CREATE INDEX idx_ideas_status ON ideas(status);
CREATE INDEX idx_ideas_created_at ON ideas(created_at DESC);
CREATE INDEX idx_ideas_tags ON ideas USING GIN(tags);
CREATE INDEX idx_ideas_embedding ON ideas USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_ideas_search_vector ON ideas USING GIN(search_vector);
CREATE INDEX idx_ideas_promoted_task ON ideas(promoted_to_task_id) WHERE promoted_to_task_id IS NOT NULL;

-- Triggers
CREATE TRIGGER update_ideas_updated_at
BEFORE UPDATE ON ideas
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ideas_search_vector
BEFORE INSERT OR UPDATE ON ideas
FOR EACH ROW
EXECUTE FUNCTION tsvector_update_trigger(search_vector, 'pg_catalog.english', title, description);
```

---

### Related Tables

#### idea_refinement_history

Track refinement activity over time:

```sql
CREATE TABLE idea_refinement_history (
    id SERIAL PRIMARY KEY,
    idea_id VARCHAR(50) REFERENCES ideas(idea_id),
    user_id VARCHAR(100),
    dimension_name VARCHAR(50),  -- Which COF dimension was updated
    old_value JSONB,
    new_value JSONB,
    changed_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_refinement_idea ON idea_refinement_history(idea_id);
```

---

#### idea_relationships

Explicit many-to-many relationships between ideas:

```sql
CREATE TABLE idea_relationships (
    id SERIAL PRIMARY KEY,
    source_idea_id VARCHAR(50) REFERENCES ideas(idea_id),
    target_idea_id VARCHAR(50) REFERENCES ideas(idea_id),
    relationship_type VARCHAR(50),  -- similar, depends_on, blocks, supersedes
    confidence FLOAT,  -- 0.0-1.0 (for AI-inferred relationships)
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_relationships_source ON idea_relationships(source_idea_id);
CREATE INDEX idx_relationships_target ON idea_relationships(target_idea_id);
CREATE INDEX idx_relationships_type ON idea_relationships(relationship_type);
```

---

## API Reference

### Endpoints

#### POST /api/v1/ideas

Create new idea.

**Request**:
```json
{
  "title": "Use Redis for API caching",
  "description": "Add Redis caching layer...",
  "cof_motivational": "Reduce latency",
  "cof_validation": {"success_criteria": ["p95 <200ms"]},
  "tags": ["performance", "backend"]
}
```

**Response** (201 Created):
```json
{
  "idea_id": "IDEA-20251111-001",
  "status": "captured",
  "cof_completeness": {"required": "3/3", "optional": "2/10", "total": "5/13"}
}
```

---

#### GET /api/v1/ideas/{idea_id}

Retrieve idea by ID.

**Response** (200 OK):
```json
{
  "idea_id": "IDEA-20251111-001",
  "title": "Use Redis for API caching",
  "description": "Add Redis caching layer...",
  "status": "refined",
  "created_at": "2025-11-11T14:23:45Z",
  "cof_13d": { /* full 13 dimensions */ },
  "tags": ["performance", "backend"],
  "evidence_bundle_path": "EB-IDEA-20251111-001.tar.gz"
}
```

---

#### PUT /api/v1/ideas/{idea_id}

Update idea (refine dimensions).

**Request**:
```json
{
  "cof_resource": {
    "team": "Team Alpha",
    "time_estimate": "2-3 hours"
  }
}
```

**Response** (200 OK):
```json
{
  "idea_id": "IDEA-20251111-001",
  "status": "refining",
  "cof_completeness": {"total": "7/13"}
}
```

---

#### POST /api/v1/ideas/{idea_id}/promote

Promote idea to task.

**Request**:
```json
{
  "target_project": "P-CFWORK-OPTIMIZATION",
  "assign_to": "user@example.com"
}
```

**Response** (201 Created):
```json
{
  "task_id": "TASK-20251111-004",
  "idea_id": "IDEA-20251111-001",
  "evidence_bundle": "EB-IDEA-20251111-001-20251111T142345Z.tar.gz",
  "_links": {
    "task": "/api/v1/tasks/TASK-20251111-004"
  }
}
```

---

#### GET /api/v1/ideas/search

Search ideas (full-text and semantic).

**Query Parameters**:
- `q` (string): Search query
- `method` (enum): `fulltext` | `semantic` | `both` (default: both)
- `min_similarity` (float): Minimum similarity score (0.0-1.0, default: 0.7)
- `status` (string): Filter by status (comma-separated)
- `tags` (string): Filter by tags (comma-separated)
- `limit` (int): Max results (default: 10)

**Example**:
```
GET /api/v1/ideas/search?q=performance&method=semantic&min_similarity=0.75&status=refined,captured&limit=5
```

**Response** (200 OK):
```json
{
  "query": "performance",
  "method": "semantic",
  "results": [
    {
      "idea_id": "IDEA-20251111-001",
      "title": "Use Redis for API caching",
      "similarity": 0.89,
      "status": "refined"
    },
    /* 4 more results */
  ],
  "total": 5
}
```

---

## CLI Usage

### Commands

```bash
# Capture
cf-core idea "Quick thought..."                    # Minimal capture
cf-core idea create --interactive                  # Interactive capture
cf-core idea voice                                 # Voice capture

# View
cf-core idea show IDEA-20251111-001                # Show full details
cf-core idea list --status captured,refined        # List ideas
cf-core idea tree IDEA-20251111-001                # Show relationship graph

# Refine
cf-core idea refine IDEA-20251111-001              # Interactive refinement
cf-core idea edit IDEA-20251111-001                # Open in editor

# Search
cf-core idea search "Redis caching"                # Full-text search
cf-core idea search-similar "performance" --min-similarity 0.7  # Semantic
cf-core idea filter --component backend --priority P0,P1        # Dimension filter

# Promote
cf-core idea promote IDEA-20251111-001             # Promote to task
cf-core idea promote IDEA-20251111-001 --project P-CFWORK-OPT  # With project

# Manage
cf-core idea archive IDEA-20251111-001             # Archive idea
cf-core idea unarchive IDEA-20251111-001           # Unarchive
cf-core idea delete IDEA-20251111-001 --confirm    # Delete (rare)

# Analytics
cf-core idea stats                                 # Capture statistics
cf-core idea report --period month                 # Monthly capture report
```

---

## Best Practices

### 1. Capture Everything (Low Friction)

**Principle**: Better to capture and archive than lose ideas

**Bad**:
```bash
# Thinking: "This idea isn't fully formed yet, I'll capture it later"
# Result: Idea forgotten
```

**Good**:
```bash
# Capture immediately, refine later
cf-core idea "Use Redis for caching" --why "improve latency"
# Takes 5 seconds, prevents idea loss
```

---

### 2. Required Dimensions First

**Principle**: Focus on Triangle dimensions (Motivational, Relational, Validation)

**Minimal Viable Capture**:
```json
{
  "title": "Use Redis for caching",
  "cof_motivational": "Reduce API latency",
  "cof_relational": {"relates_to": ["TASK-API-PERF-001"]},
  "cof_validation": {"success_criteria": ["p95 <200ms"]}
}
```

**Result**: Idea is promotable even without optional dimensions

---

### 3. Progressive Refinement

**Principle**: Add dimensions gradually as you learn more

**Day 1** (Capture):
```bash
cf-core idea "Use Redis for caching" --why "improve latency"
# COF Completeness: 3/13
```

**Day 2** (Research):
```bash
cf-core idea refine IDEA-20251111-001
# Add Resource Context: Team Alpha, 2-3 hours
# Add Temporal Context: Q4 Performance Initiative
# COF Completeness: 5/13
```

**Day 3** (Deeper Analysis):
```bash
cf-core idea refine IDEA-20251111-001
# Add Computational Context: Hash map, O(1)
# Add Sacred Geometry: Fractal (reusable module)
# COF Completeness: 7/13
```

**Day 4** (Promote):
```bash
cf-core idea promote IDEA-20251111-001
# Ready for implementation
```

---

### 4. Use Templates for Common Patterns

**Feature Idea Template**:
```bash
cf-core idea create --template feature

# Prompts:
# 1. Feature name: [Redis caching]
# 2. User benefit: [Faster API responses]
# 3. Affected components: [backend-api]
# 4. Success criteria: [p95 <200ms]
# 5. Estimated effort: [2-3 hours]
```

**Bug Fix Template**:
```bash
cf-core idea create --template bugfix

# Prompts:
# 1. Bug description: [JWT tokens expiring prematurely]
# 2. Impact: [Users logged out every 10 minutes]
# 3. Root cause (if known): [Token TTL misconfigured]
# 4. Fix verification: [Test token TTL = 24 hours]
```

---

### 5. Regular Idea Review (Spiral Pattern)

**Principle**: Review captured ideas weekly to promote or archive

**Weekly Ritual**:
```bash
# View all captured/refined ideas
cf-core idea list --status captured,refined --sort created_at

# For each idea:
# - Promote if ready: cf-core idea promote IDEA-XXX
# - Archive if not valuable: cf-core idea archive IDEA-XXX
# - Refine if needs work: cf-core idea refine IDEA-XXX
```

**Goal**: Prevent idea backlog accumulation (Golden Ratio: promote 20%, archive 80%)

---

### 6. Link to Active Work (Relational Context)

**Principle**: Always link ideas to existing tasks/projects

**Good**:
```bash
cf-core idea "Use Redis for caching" --relates-to TASK-API-PERF-001
# Creates graph relationship, easy to find related ideas
```

**Bad**:
```bash
cf-core idea "Use Redis for caching"
# Orphaned idea, hard to find later
```

---

### 7. Measure Idea-to-Task Conversion (Validation)

**Principle**: Track promotion rate to validate idea capture value

**Analytics**:
```bash
cf-core idea stats --period month

# Output:
# ┌────────────────────────────────────────────────┐
# │ Idea Capture Statistics (November 2025)       │
# ├────────────────────────────────────────────────┤
# │ Total Captured: 47                             │
# │ Promoted to Tasks: 12 (26%)                    │
# │ Archived: 28 (60%)                             │
# │ Still Refining: 7 (14%)                        │
# │                                                │
# │ Average Refinement Time: 2.3 days              │
# │ Average COF Completeness at Promotion: 8.2/13  │
# │                                                │
# │ Top Tags: performance (18), backend (15), ...  │
# └────────────────────────────────────────────────┘
```

**Goal**: 20-30% promotion rate (Golden Ratio), <3 days refinement time

---

## Related Documents

- **[03-Context-Ontology-Framework.md](03-Context-Ontology-Framework.md)** - COF 13-dimensional framework
- **[05-Database-Design-Implementation.md](05-Database-Design-Implementation.md)** - PostgreSQL schema and pgvector
- **[07-Workflow-Designer.md](07-Workflow-Designer.md)** - Workflow Designer integration (planned)
- **[10-API-Reference.md](10-API-Reference.md)** - TaskMan-v2 API documentation
- **[15-Future-Roadmap.md](15-Future-Roadmap.md)** - P3-001 Idea Capture System initiative

---

**For professional philosophy guidance, see [ContextForge Work Codex](Codex/CODEX.md)**
