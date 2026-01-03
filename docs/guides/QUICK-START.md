# ContextForge Documentation Library - Quick Start Guide

**Welcome!** This guide will help you navigate the ContextForge Documentation Library and get up to speed quickly.

---

## 🎯 Your First 30 Minutes

### Step 1: Read the Overview (10 minutes)
Start with [01-Overview.md](01-Overview.md) to understand:
- What ContextForge is and why it exists
- The 11 core philosophies that guide development
- Key components and their relationships

**Key Takeaway**: ContextForge is a context-driven task management and workflow platform built on evidence-based engineering principles.

### Step 2: Understand the Framework (15 minutes)
Skim [03-Context-Ontology-Framework.md](03-Context-Ontology-Framework.md) to grasp:
- **COF 13 Dimensions** - The framework for capturing complete context
- **Universal Context Law (UCL)** - The governing principle for context integrity
- **Sacred Geometry** - Visual patterns for workflows (Triangle, Circle, Spiral, Golden Ratio, Fractal)
- **UTMW Methodology** - Understand → Trust → Measure → Validate → Work

**Key Takeaway**: Context defines action. Every decision and implementation should be grounded in the 13-dimensional framework.

### Step 3: Check the Index (5 minutes)
Browse [00-ContextForge-Library-Index.md](00-ContextForge-Library-Index.md) to see:
- Complete document catalog (15 documents)
- Quick navigation by role
- Key concepts cross-reference

**Key Takeaway**: All 15 documents are complete and production-ready.

---

## 📚 Reading Paths by Role

### 👨‍💻 Software Engineers (3-4 hours)

**Day 1: Foundations**
1. [01-Overview.md](01-Overview.md) - System vision (30 min)
2. [09-Development-Guidelines.md](09-Development-Guidelines.md) - Daily practices (1 hour)
3. [10-API-Reference.md](10-API-Reference.md) - API contracts (45 min)

**Day 2: Application Layer**
4. [04-Desktop-Application-Architecture.md](04-Desktop-Application-Architecture.md) - TaskMan-v2 details (1 hour)
5. [13-Testing-Validation.md](13-Testing-Validation.md) - Quality standards (1 hour)

**Start Contributing**: You're ready to pick up your first task!

---

### 🏗️ Architects (4-5 hours)

**Week 1: Architecture Deep Dive**
1. [02-Architecture.md](02-Architecture.md) - System design (1 hour)
2. [03-Context-Ontology-Framework.md](03-Context-Ontology-Framework.md) - Frameworks (1.5 hours)
3. [04-Desktop-Application-Architecture.md](04-Desktop-Application-Architecture.md) - TaskMan-v2 (1 hour)
4. [05-Database-Design-Implementation.md](05-Database-Design-Implementation.md) - Data layer (1 hour)

**Week 2: Strategic Vision**
5. [15-Future-Roadmap.md](15-Future-Roadmap.md) - P0-P3 initiatives (1 hour)
6. [Codex](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md) - Philosophies (1 hour)

**Lead Design**: You're ready to lead architectural decisions!

---

### 🔒 Security Engineers (2-3 hours)

**Security Essentials**
1. [12-Security-Authentication.md](12-Security-Authentication.md) - JWT, RBAC, secrets (1 hour)
2. [11-Configuration-Management.md](11-Configuration-Management.md) - Secret management (45 min)
3. [14-Deployment-Operations.md](14-Deployment-Operations.md) - CI/CD security (45 min)
4. [09-Development-Guidelines.md](09-Development-Guidelines.md) - Evidence On Trigger (30 min)

**Secure the Platform**: You're ready to conduct security reviews!

---

### 🚀 DevOps Engineers (2-3 hours)

**Operations Mastery**
1. [14-Deployment-Operations.md](14-Deployment-Operations.md) - CI/CD, Docker, K8s (1.5 hours)
2. [11-Configuration-Management.md](11-Configuration-Management.md) - Config management (1 hour)
3. [12-Security-Authentication.md](12-Security-Authentication.md) - Security practices (45 min)
4. [13-Testing-Validation.md](13-Testing-Validation.md) - Testing strategy (30 min)

**Deploy with Confidence**: You're ready to manage deployments!

---

### 🧪 QA Engineers (2-3 hours)

**Quality Standards**
1. [13-Testing-Validation.md](13-Testing-Validation.md) - QSE framework (1 hour)
2. [03-Context-Ontology-Framework.md](03-Context-Ontology-Framework.md) - UTMW workflow (45 min)
3. [09-Development-Guidelines.md](09-Development-Guidelines.md) - Code quality (45 min)
4. [08-Optimization-Standards.md](08-Optimization-Standards.md) - Performance testing (30 min)

**Ensure Quality**: You're ready to design test strategies!

---

### 📊 Product Managers (1-2 hours)

**Product Vision**
1. [01-Overview.md](01-Overview.md) - System overview (30 min)
2. [04-Desktop-Application-Architecture.md](04-Desktop-Application-Architecture.md) - TaskMan-v2 features (30 min)
3. [06-Idea-Capture-System.md](06-Idea-Capture-System.md) - Idea management (30 min)
4. [15-Future-Roadmap.md](15-Future-Roadmap.md) - Strategic roadmap (30 min)

**Drive Vision**: You're ready to prioritize features!

---

## 🔑 Core Concepts You Must Know

### 1. Context Ontology Framework (COF)

**What**: A 13-dimensional framework for capturing complete context.

**The 13 Dimensions**:
1. **Motivational** - Why this matters (REQUIRED)
2. **Relational** - Dependencies & connections (REQUIRED)
3. **Dimensional** - Scope, depth, integration
4. **Situational** - Environment & constraints
5. **Resource** - Time, skill, tools, budget
6. **Narrative** - User/stakeholder journey
7. **Recursive** - Meta-patterns & processes
8. **Computational** - Algorithmic efficiency
9. **Emergent** - Unexpected interactions
10. **Temporal** - Timing & sequencing
11. **Spatial** - Topology & layout
12. **Validation** - Evidence & requirements (REQUIRED)
13. **Sacred Geometry** - Pattern alignment

**When to Use**: Every task, idea, and feature should be analyzed through these 13 dimensions.

**Example**:
```json
{
  "task_id": "TASK-001",
  "title": "Add Redis caching to API",
  "cof_13d": {
    "motivational": "Reduce p95 latency from 450ms to <200ms",
    "relational": ["TASK-005 (database optimization)", "IDEA-003 (performance)"],
    "resource": {"estimated_hours": 8, "story_points": 5},
    "validation": {
      "success_criteria": ["p95 <200ms", "cache hit rate >80%"]
    }
  }
}
```

---

### 2. Universal Context Law (UCL)

**The Law**: *"No orphaned, cyclical, or incomplete context may persist in the system."*

**What It Means**:
- Every task must link to projects/initiatives (no orphans)
- No circular dependencies (no cycles)
- All 3 required COF dimensions must be present (no incomplete)

**Enforcement**:
- **Triple-Check Protocol**: Build → Logs → Evidence
- **Compliance Gates**: Linkage, Evidence, Geometry, Closure
- **Strategic Session Audits**: 3/6/9 cadence (every 3rd, 6th, 9th session)

**Example Violation**:
```python
# ❌ BAD: Orphaned task with no context
task = {
    "id": "TASK-999",
    "title": "Fix bug",  # What bug? Why? How does it relate to anything?
}

# ✅ GOOD: Complete context
task = {
    "id": "TASK-999",
    "title": "Fix authentication token expiration bug",
    "cof_13d": {
        "motivational": "Users losing sessions after 1 hour instead of 24 hours",
        "relational": ["PROJECT-AUTH-001", "BUG-REPORT-042"],
        "validation": {
            "success_criteria": ["Token expires after 24h", "No premature logouts"]
        }
    }
}
```

---

### 3. Sacred Geometry Patterns

**What**: Visual metaphors for workflow design and system architecture.

| Pattern | Symbol | Meaning | When to Use |
|---------|--------|---------|-------------|
| **Triangle** | △ | Stability, 3-phase workflows | Plan → Execute → Validate |
| **Circle** | ○ | Completeness, closed-loop validation | Workflows with feedback loops |
| **Spiral** | 🌀 | Iteration, progressive refinement | Agile sprints, continuous improvement |
| **Golden Ratio** | φ | Balance (38% planning / 62% execution) | Resource allocation, estimation |
| **Fractal** | ❄️ | Modularity, self-similar patterns | Component architecture, nested workflows |

**Example - Triangle Workflow**:
```
Phase 1 (Plan)    △
Phase 2 (Execute) △ △
Phase 3 (Validate)△ △ △
```

---

### 4. UTMW Methodology

**What**: A 5-phase workflow for any engineering task.

**The 5 Phases**:
1. **Understand** - Read code, review docs, trace execution (context building)
2. **Trust** - Run tests, validate logs, confirm assumptions (identify critical path)
3. **Measure** - Collect metrics, establish baselines, identify gaps (estimate effort)
4. **Validate** - Apply changes, run benchmarks, verify improvements (quality gates)
5. **Work** - Record actual data, update velocity, iterate (close the loop)

**Example - Optimization Task**:
```python
# Phase 1: Understand
# - Run cProfile to identify hotspots
# - Read slow function implementations

# Phase 2: Trust
# - Verify tests pass
# - Identify top 20% of functions by cumulative time (Golden Ratio)

# Phase 3: Measure
# - Baseline: p95 latency = 450ms
# - Estimate: 5 story points × 0.23 hrs/point = 1.15 hours

# Phase 4: Validate
# - Implement optimization
# - Benchmark: p95 latency = 180ms (✓ <200ms target)

# Phase 5: Work
# - Record actual time: 1.3 hours
# - Update DuckDB velocity tracker
```

---

### 5. Database Authority Principle

**The Principle**: PostgreSQL is the **single source of truth** for TaskMan-v2 task management.

**Architecture**:
- **PostgreSQL** (`172.25.14.122:5432/taskman_v2`) - Primary authority for tasks
- **DuckDB** (`db/velocity.duckdb`) - Analytics and velocity tracking
- **SQLite** (`db/trackers.sqlite`) - Legacy trackers (read-only)

**Important**:
- ❌ Never mutate CSV files directly
- ❌ Never treat SQLite as primary for new tasks
- ✅ Always write to PostgreSQL for task operations
- ✅ Use DuckDB for analytics queries

---

## 🛠️ Essential Tools & Commands

### CLI Commands

**Velocity Tracking**:
```bash
# Record work session
./cli/Invoke-VelocityTracker.ps1 -Action Record -TaskId "TASK-001" -Hours 2.5 -StoryPoints 5

# Predict completion time
./cli/Invoke-VelocityTracker.ps1 -Action Predict -StoryPoints 8

# Generate velocity report
./cli/Invoke-VelocityTracker.ps1 -Action Report
```

**Task Management**:
```bash
# List tasks
python cf_cli.py tasks list --status todo

# Create task
python cf_cli.py tasks create --title "Implement caching" --priority high

# Update task
python cf_cli.py tasks update TASK-001 --status in_progress
```

**Idea Capture**:
```bash
# Quick capture
cf-core idea "Use Redis for API caching"

# Promote idea to task
cf-core idea promote IDEA-001 --story-points 5
```

---

### API Endpoints

**FastAPI Backend** (http://localhost:8000):
```bash
# Health check
curl http://localhost:8000/health

# List tasks
curl http://localhost:8000/api/v1/tasks

# Create task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "New task", "priority": 3}'

# API documentation
open http://localhost:8000/docs
```

**MCP Tools** (via Claude Desktop):
```javascript
// List tasks
use_mcp_tool({
  server_name: "taskman-mcp-v2",
  tool_name: "list_tasks",
  arguments: { status: "todo" }
})

// Create task
use_mcp_tool({
  server_name: "taskman-mcp-v2",
  tool_name: "create_task",
  arguments: {
    title: "Implement feature",
    priority: 3,
    story_points: 5
  }
})
```

---

## 📖 Document Quick Reference

| Document | Purpose | Read Time | Priority |
|----------|---------|-----------|----------|
| [01-Overview](01-Overview.md) | System overview | 30 min | HIGH |
| [02-Architecture](02-Architecture.md) | System design | 45 min | HIGH |
| [03-COF](03-Context-Ontology-Framework.md) | COF/UCL/UTMW | 1 hour | HIGH |
| [04-Desktop-App](04-Desktop-Application-Architecture.md) | TaskMan-v2 | 1 hour | MEDIUM |
| [05-Database](05-Database-Design-Implementation.md) | Data layer | 1 hour | MEDIUM |
| [06-Idea-Capture](06-Idea-Capture-System.md) | Idea management | 45 min | LOW |
| [07-Workflow-Designer](07-Workflow-Designer.md) | Visual workflows | 30 min | LOW |
| [08-Optimization](08-Optimization-Standards.md) | Performance | 45 min | MEDIUM |
| [09-Dev-Guidelines](09-Development-Guidelines.md) | Code standards | 1 hour | HIGH |
| [10-API-Reference](10-API-Reference.md) | API docs | 45 min | HIGH |
| [11-Configuration](11-Configuration-Management.md) | Config mgmt | 45 min | MEDIUM |
| [12-Security](12-Security-Authentication.md) | Security | 45 min | MEDIUM |
| [13-Testing](13-Testing-Validation.md) | QA standards | 1 hour | HIGH |
| [14-Deployment](14-Deployment-Operations.md) | CI/CD/Ops | 1 hour | MEDIUM |
| [15-Roadmap](15-Future-Roadmap.md) | Future vision | 45 min | LOW |

**Total Reading Time**: ~12 hours (spread over 1-2 weeks)

---

## 🎓 Learning Milestones

### Week 1: Foundation ✅
- [ ] Read 01-Overview, 03-COF, 09-Dev-Guidelines
- [ ] Understand COF 13 Dimensions
- [ ] Learn Sacred Geometry patterns
- [ ] Complete first code review using UTMW

### Week 2: Application ✅
- [ ] Read 04-Desktop-App, 10-API-Reference
- [ ] Set up development environment
- [ ] Complete first task with full COF context
- [ ] Record velocity data

### Week 3: Quality & Ops ✅
- [ ] Read 13-Testing, 14-Deployment
- [ ] Write tests following QSE framework
- [ ] Deploy a feature through CI/CD
- [ ] Generate evidence bundle

### Week 4: Mastery ✅
- [ ] Read 15-Roadmap, Codex
- [ ] Lead architectural discussion
- [ ] Mentor new team member
- [ ] Contribute to documentation

---

## 🚨 Common Pitfalls to Avoid

### 1. Skipping Context
❌ **Bad**: "Fixed bug in login"
✅ **Good**: "Fixed JWT token expiration bug causing premature logouts (affects 15% of users)"

### 2. Orphaned Tasks
❌ **Bad**: Creating tasks with no project linkage
✅ **Good**: Every task links to a project/initiative

### 3. No Evidence
❌ **Bad**: Claiming "tests pass" without logs
✅ **Good**: Attaching test output, profiling data, benchmarks

### 4. Ignoring Velocity
❌ **Bad**: Estimating based on gut feeling
✅ **Good**: Using DuckDB velocity (0.23 hrs/point baseline)

### 5. Premature Optimization
❌ **Bad**: Optimizing without profiling
✅ **Good**: UTMW - Profile → Identify hot paths → Measure → Optimize → Validate

---

## 🆘 Getting Help

### Documentation
- [00-ContextForge-Library-Index.md](00-ContextForge-Library-Index.md) - Complete index
- [LIBRARY-MANIFEST.md](LIBRARY-MANIFEST.md) - Document inventory
- [Codex](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md) - Core philosophies

### Troubleshooting
- [09-Development-Guidelines.md](09-Development-Guidelines.md#troubleshooting) - Common issues
- [13-Testing-Validation.md](13-Testing-Validation.md#troubleshooting) - Test failures
- [14-Deployment-Operations.md](14-Deployment-Operations.md#troubleshooting) - Deployment issues

### Code Examples
- All documents include working code examples
- Check [10-API-Reference.md](10-API-Reference.md) for complete schemas
- Review [09-Development-Guidelines.md](09-Development-Guidelines.md) for patterns

---

## ✅ Quick Start Checklist

### First Day
- [ ] Read [01-Overview.md](01-Overview.md)
- [ ] Skim [03-Context-Ontology-Framework.md](03-Context-Ontology-Framework.md)
- [ ] Review [00-ContextForge-Library-Index.md](00-ContextForge-Library-Index.md)
- [ ] Set up development environment

### First Week
- [ ] Read role-specific documents (see Reading Paths above)
- [ ] Complete first task with full COF context
- [ ] Attend team standup
- [ ] Review first pull request

### First Month
- [ ] Read all 15 documents
- [ ] Lead a feature implementation
- [ ] Mentor a new team member
- [ ] Contribute to documentation improvements

---

**You're Ready!** Start with [01-Overview.md](01-Overview.md) and follow your role-specific reading path. Welcome to ContextForge! 🚀

---

*"Context defines action. Every system reflects the order—or disorder—of its makers."* — ContextForge Work Codex
