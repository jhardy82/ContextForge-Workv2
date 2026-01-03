# ContextForge Documentation Library - Table of Contents

**Version**: 2.0
**Last Updated**: 2025-11-11
**Total Documents**: 15 (100% Complete)
**Total Lines**: 14,413

---

## 📑 Navigation Guide

### 🎯 Quick Access
- **New Users**: Start with [QUICK-START.md](QUICK-START.md)
- **Complete Index**: See [00-ContextForge-Library-Index.md](00-ContextForge-Library-Index.md)
- **Document Inventory**: See [LIBRARY-MANIFEST.md](LIBRARY-MANIFEST.md)

### 📚 Browse by Category
- [Foundation](#foundation-documents) - Core concepts and architecture
- [Application](#application-layer-documents) - Desktop apps and features
- [Data](#data--storage-documents) - Database design and persistence
- [Engineering](#engineering-standards-documents) - Development guidelines
- [Quality](#quality--testing-documents) - Testing and validation
- [Operations](#operations--security-documents) - Deployment and security
- [Roadmap](#roadmap--future-documents) - Strategic vision

---

## Foundation Documents

### [00 – ContextForge Library Index](00-ContextForge-Library-Index.md)
**Lines**: 461 | **Status**: ✅ Complete | **Priority**: HIGH

**Purpose**: Master index for the complete ContextForge documentation library.

**Contents**:
- Library organization by category
- Documentation statistics and completion status
- Quick navigation by role
- Key concepts cross-reference (COF, UCL, Sacred Geometry, UTMW)
- Learning paths for new users
- Maintenance schedule

**When to Read**: Start here for overview of all documentation

---

### [01 – Overview](01-Overview.md)
**Lines**: 575 | **Status**: ✅ Complete | **Priority**: HIGH

**Purpose**: High-level system overview and vision.

**Contents**:
1. **What is ContextForge?**
   - Context-driven task management platform
   - Evidence-based engineering
   - Sacred Geometry workflow patterns

2. **11 Core Philosophies**
   - Trust Nothing, Verify Everything
   - Logs First
   - Context Before Action
   - Balance Order and Flow
   - Sacred Geometry as Blueprint
   - Right-Sized Solutions
   - Evidence On Trigger
   - Iteration Over Perfection
   - Database Authority
   - Reproducible Operations
   - Documentation is Resilience

3. **Key Components**
   - CF-Enhanced CLI
   - TaskMan-v2 Desktop App
   - Database Authority (PostgreSQL)
   - Quality Software Engineering (QSE) Framework

**When to Read**: First document for all new team members

---

### [02 – Architecture](02-Architecture.md)
**Lines**: 412 | **Status**: ✅ Complete | **Priority**: HIGH

**Purpose**: System architecture and component relationships.

**Contents**:
1. **Component Inventory**
   - CLI Layer (CF-Enhanced, TaskMan MCP)
   - Application Layer (TaskMan-v2 Desktop)
   - Data Layer (PostgreSQL, DuckDB, SQLite)
   - Infrastructure Layer (GitHub Actions, Docker)

2. **Data Flows**
   - Task creation flow
   - Context enrichment flow
   - Evidence generation flow

3. **Sacred Geometry Integration**
   - Triangle (3-layer architecture)
   - Circle (closed-loop validation)
   - Fractal (repository pattern)

**When to Read**: After Overview, before implementation work

---

### [03 – Context Ontology Framework](03-Context-Ontology-Framework.md)
**Lines**: 736 | **Status**: ✅ Complete | **Priority**: HIGH

**Purpose**: Core frameworks that govern ContextForge development.

**Contents**:
1. **Context Ontology Framework (COF)**
   - 13 dimensions for complete context
   - Motivational, Relational, Dimensional, Situational, Resource, Narrative, Recursive, Computational, Emergent, Temporal, Spatial, Validation, Sacred Geometry
   - 3 REQUIRED dimensions: Motivational, Relational, Validation

2. **Universal Context Law (UCL)**
   - No orphaned, cyclical, or incomplete context
   - Triple-Check Protocol (Build → Logs → Evidence)
   - Compliance gates

3. **Sacred Geometry Patterns**
   - Triangle (△) - Stability
   - Circle (○) - Completeness
   - Spiral (🌀) - Iteration
   - Golden Ratio (φ) - Balance
   - Fractal (❄️) - Modularity

4. **UTMW Methodology**
   - Understand → Trust → Measure → Validate → Work

**When to Read**: Essential for all engineers; reference frequently

---

## Application Layer Documents

### [04 – Desktop Application Architecture](04-Desktop-Application-Architecture.md)
**Lines**: 650 | **Status**: ✅ Complete | **Priority**: MEDIUM

**Purpose**: TaskMan-v2 desktop application architecture and features.

**Contents**:
1. **Technology Stack**
   - Frontend: React 19 + TypeScript 5.x + Vite
   - Backend: FastAPI 0.100+ + Pydantic 2.x
   - Database: PostgreSQL 15+ (primary authority)

2. **64-Field Task Schema**
   - Core fields (task_id, title, description, status, priority)
   - Temporal fields (created_at, updated_at, due_date)
   - COF 13D fields (cof_motivational, cof_relational, etc.)
   - Evidence fields (evidence_bundle_url, sha256_hash)

3. **Features**
   - Task CRUD operations
   - Context enrichment
   - MCP integration
   - Evidence bundle generation

4. **Component Structure**
   - Frontend: Pages, Components, Services, State Management
   - Backend: Routes, Services, Models, Database

**When to Read**: When working on TaskMan-v2 features

---

### [06 – Idea Capture System](06-Idea-Capture-System.md)
**Lines**: 1,465 | **Status**: ✅ Complete | **Priority**: LOW

**Purpose**: Context-aware idea capture with COF 13D integration.

**Contents**:
1. **Philosophy**
   - Capture First, Perfect Later
   - Zero Friction (5-second CLI capture)
   - Context-Aware Enrichment (automatic COF population)

2. **COF 13-Dimensional Integration**
   - Capture strategies for all 13 dimensions
   - Progressive enrichment (captured → refining → refined)

3. **Capture Methods**
   - CLI: `cf-core idea "description"`
   - API: POST /api/v1/ideas
   - Voice capture (future)
   - MCP integration

4. **Idea Lifecycle**
   - captured → refining → refined → promoted → archived
   - One-click promotion to TaskMan-v2 tasks

5. **Search & Retrieval**
   - PostgreSQL full-text search
   - pgvector semantic search (OpenAI embeddings)
   - Dimension-based filtering
   - Graph traversal (related ideas)

6. **Database Schema**
   - ideas table with 13 COF dimensions
   - pgvector embeddings (1536 dimensions)
   - Status tracking and promotion metadata

**When to Read**: When implementing idea capture features

---

### [07 – Workflow Designer](07-Workflow-Designer.md)
**Lines**: 813 | **Status**: ✅ Complete | **Priority**: LOW

**Purpose**: Visual workflow builder using Sacred Geometry patterns.

**Contents**:
1. **Philosophy**
   - Geometry as Language
   - Visual Clarity
   - Constraint-Based Design
   - UTMW First

2. **Sacred Geometry Patterns**
   - Triangle: 3-phase workflows (Plan → Execute → Validate)
   - Circle: Closed-loop workflows with validation gates
   - Spiral: Iterative refinement cycles
   - Golden Ratio: Balanced resource distribution (38% plan / 62% execute)
   - Fractal: Nested sub-workflows

3. **UTMW Integration**
   - Each workflow phase maps to UTMW methodology
   - Understand/Trust → Measure → Validate → Work

4. **Architecture**
   - Web UI: React Flow visual designer
   - CLI: PowerShell designer (ContextForge.Spectre)
   - Backend: FastAPI workflow execution engine
   - Database: PostgreSQL workflow storage

5. **Workflow Templates**
   - Feature Implementation (Triangle)
   - Bug Fix (Circle)
   - Technical Debt (Spiral)
   - Optimization (Golden Ratio)
   - Refactoring (Fractal)

6. **ContextForge.Spectre Integration**
   - PowerShell Sacred Geometry rendering
   - Terminal-based workflow visualization
   - Progress tracking with symbols

**When to Read**: When designing workflows or building visual tools

---

## Data & Storage Documents

### [05 – Database Design & Implementation](05-Database-Design-Implementation.md)
**Lines**: 857 | **Status**: ✅ Complete | **Priority**: MEDIUM

**Purpose**: Database architecture, schema design, and migration management.

**Contents**:
1. **Database Authority Principle**
   - PostgreSQL (`172.25.14.122:5432/taskman_v2`) - Primary authority
   - DuckDB (`db/velocity.duckdb`) - Analytics
   - SQLite (`db/trackers.sqlite`) - Legacy (read-only)

2. **PostgreSQL Schema**
   - tasks table (64 fields with COF 13D)
   - ideas table (COF 13D + pgvector)
   - projects, sprints, quality_gates tables
   - Indexes, constraints, triggers

3. **Alembic Migrations**
   - Migration workflow
   - Version control
   - Rollback strategies

4. **DuckDB Analytics**
   - Velocity tracking (0.23 hrs/point baseline)
   - work_sessions, tasks, velocity_metrics tables
   - Sprint analytics

5. **SQLite Legacy**
   - Historical tracker data
   - Read-only access
   - Migration path to PostgreSQL

6. **Connection Management**
   - SQLAlchemy engine configuration
   - Connection pooling
   - Health checks

**When to Read**: When working on database schema or migrations

---

## Engineering Standards Documents

### [08 – Optimization Standards](08-Optimization-Standards.md)
**Lines**: 1,193 | **Status**: ✅ Complete | **Priority**: MEDIUM

**Purpose**: Performance profiling, benchmarking, and optimization standards.

**Contents**:
1. **Philosophy**
   - Golden Ratio (focus on top 20% hot paths)
   - Sacred Geometry Spiral (iterative optimization)
   - UCL Compliance (evidence-based optimization)

2. **Performance Targets**
   - API: p50 <100ms, p95 <200ms, p99 <500ms
   - Database: Simple queries <50ms, complex <200ms
   - CLI: Command completion <2s
   - Frontend: LCP <2.5s, FID <100ms, CLS <0.1

3. **Profiling Standards**
   - cProfile: Function-level hotspot identification
   - line_profiler: Line-by-line analysis
   - memory_profiler: Memory leak detection
   - py-spy: Production sampling
   - PostgreSQL EXPLAIN ANALYZE: Query optimization

4. **Benchmarking Framework**
   - pytest-benchmark: Python performance tests
   - Locust: API load testing
   - Lighthouse: Frontend performance auditing

5. **DuckDB Velocity Integration**
   - Baseline: 0.23 hours per story point
   - Prediction API for optimization tasks
   - Velocity tracking for optimization sprints

6. **UTMW Optimization Workflow**
   - Understand: Run profilers, collect baseline
   - Trust: Identify hot paths (Golden Ratio 20%)
   - Measure: Estimate using velocity (0.23 hrs/point)
   - Validate: Benchmark before/after
   - Work: Record actual completion data

7. **Evidence & Reporting**
   - Before/after benchmarks
   - Profiler outputs
   - SHA-256 evidence bundles

**When to Read**: Before starting performance optimization work

---

### [09 – Development Guidelines](09-Development-Guidelines.md)
**Lines**: 888 | **Status**: ✅ Complete | **Priority**: HIGH

**Purpose**: Daily development practices, code standards, and patterns.

**Contents**:
1. **Engineering Pillars**
   - Logs First (≥90% coverage)
   - Python-First orchestration
   - Evidence On Trigger
   - Quality Gates
   - Triple-Check Protocol

2. **Sacred Geometry Patterns**
   - Triangle: 3-layer architecture
   - Circle: Closed-loop validation
   - Fractal: Repository pattern

3. **Code Style**
   - Python: PEP 8, type hints, docstrings
   - TypeScript: ESLint, Prettier
   - PowerShell: PSSCriptAnalyzer

4. **Testing Standards**
   - Unit tests: 70% coverage
   - Integration tests: 40% coverage
   - Logging: 90% coverage

5. **Error Handling**
   - Try-except with structured logging
   - Error taxonomy (validation, operational, system)

6. **Git Workflow**
   - Branch naming conventions
   - Commit message format
   - Pull request requirements

**When to Read**: Reference daily during development

---

### [10 – API Reference](10-API-Reference.md)
**Lines**: 495 | **Status**: ✅ Complete | **Priority**: HIGH

**Purpose**: Complete API documentation for CLI, REST, and MCP interfaces.

**Contents**:
1. **CLI Commands**
   - cf_cli.py: Task management commands
   - tasks_cli.py: Advanced task operations
   - Invoke-VelocityTracker.ps1: Velocity tracking

2. **REST API Endpoints**
   - Tasks: GET/POST/PUT/DELETE /api/v1/tasks
   - Projects: /api/v1/projects
   - Quality Gates: /api/v1/quality-gates

3. **MCP Tools**
   - taskman-mcp-v2 server tools
   - list_tasks, create_task, update_task
   - search_tasks, bulk_update

4. **Request/Response Schemas**
   - Complete JSON schemas for all endpoints
   - Validation rules
   - Error response formats

5. **Authentication**
   - JWT token format (future)
   - API key authentication (future)

**When to Read**: When integrating with ContextForge APIs

---

### [11 – Configuration Management](11-Configuration-Management.md)
**Lines**: 1,463 | **Status**: ✅ Complete | **Priority**: MEDIUM

**Purpose**: Configuration management, secret handling, and environment setup.

**Contents**:
1. **Configuration Philosophy**
   - Secret refs only (no plaintext credentials)
   - Environment aware (dev/staging/prod)
   - Type safety (Pydantic validation)
   - Hierarchical loading (CLI → Env → .env → Defaults)
   - Fail fast (startup validation)

2. **Python Configuration (Pydantic Settings)**
   - TaskMan-v2 backend: config.py with Settings class
   - CF-Enhanced CLI: cf_cli/config/settings.py
   - Nested configuration models
   - Environment variable parsing

3. **Database Configuration**
   - PostgreSQL connection management
   - SQLAlchemy engine configuration
   - Connection pooling

4. **Environment Configuration**
   - .env file structure
   - Environment-specific configs (.env.development, .env.production)
   - CORS, logging, feature flags

5. **Secret Management**
   - Azure Key Vault integration
   - AWS Secrets Manager integration
   - PowerShell SecretManagement

6. **Feature Flags**
   - Feature flag configuration
   - Runtime toggles
   - Admin API for feature management

7. **Multi-Environment Strategy**
   - Environment detection (dev/staging/prod/test)
   - Environment-specific loading

8. **Configuration Validation**
   - JSON Schema validation
   - Pydantic validators
   - Startup validation checks

9. **TypeScript Configuration**
   - Vite configuration
   - Frontend environment variables

10. **PowerShell Configuration**
    - ContextForge.Configuration module

**When to Read**: When setting up environments or managing secrets

---

## Quality & Testing Documents

### [13 – Testing & Validation](13-Testing-Validation.md)
**Lines**: 829 | **Status**: ✅ Complete | **Priority**: HIGH

**Purpose**: Testing strategies, QSE framework, and quality gates.

**Contents**:
1. **QSE Framework**
   - Quality Software Engineering methodology
   - Evidence-based validation
   - Constitutional compliance

2. **UTMW Methodology**
   - Understand → Trust → Measure → Validate → Work
   - Applied to testing workflows

3. **Test Inventory**
   - 428 test files
   - 2,226 total tests
   - Python (pytest), JavaScript (Vitest), PowerShell (Pester)

4. **Coverage Targets**
   - Unit: 70%
   - Integration: 40%
   - System: 25%
   - Logging: 90%

5. **Test Categories**
   - Unit tests
   - Integration tests
   - E2E tests (Playwright)
   - Performance tests (pytest-benchmark)
   - Accessibility tests (axe-core)

6. **Quality Gates**
   - Pre-commit: Linting, type checking
   - CI: All tests pass, coverage thresholds
   - Pre-deployment: Integration tests, performance benchmarks

7. **Test Patterns**
   - Arrange-Act-Assert (AAA)
   - Given-When-Then (BDD)
   - Fixtures and mocking

**When to Read**: When writing tests or designing test strategies

---

## Operations & Security Documents

### [12 – Security & Authentication](12-Security-Authentication.md)
**Lines**: 827 | **Status**: ✅ Complete | **Priority**: MEDIUM

**Purpose**: Security practices, authentication, and authorization.

**Contents**:
1. **Authentication**
   - JWT tokens (implementation planned)
   - Token structure and validation
   - Refresh token flow

2. **Authorization**
   - Role-Based Access Control (RBAC)
   - Permission system
   - Resource-level permissions

3. **Secret Management**
   - Azure Key Vault integration
   - AWS Secrets Manager integration
   - Secret rotation policies (90-day)

4. **OWASP Top 10 Coverage**
   - SQL injection prevention
   - XSS protection
   - CSRF protection
   - Authentication bypass prevention

5. **Security Best Practices**
   - Input validation
   - Output encoding
   - Secure configuration
   - Dependency scanning

6. **Audit Logging**
   - Security event logging
   - Audit trail requirements
   - Log retention policies

**When to Read**: When implementing security features or conducting audits

---

### [14 – Deployment & Operations](14-Deployment-Operations.md)
**Lines**: 1,078 | **Status**: ✅ Complete | **Priority**: MEDIUM

**Purpose**: CI/CD pipelines, deployment strategies, and operational procedures.

**Contents**:
1. **CI/CD Pipelines**
   - GitHub Actions (18 workflows)
   - Build, test, deploy stages
   - Quality gates enforcement

2. **Deployment Strategies**
   - Blue-green deployment
   - Canary releases
   - Rollback procedures

3. **Docker Configuration**
   - Dockerfile optimization
   - Multi-stage builds
   - Image security scanning

4. **Kubernetes Deployment**
   - Deployment manifests
   - Service configuration
   - Ingress rules

5. **Monitoring**
   - Health checks
   - Log aggregation (Loki/Grafana planned)
   - Metrics collection (Prometheus planned)

6. **Disaster Recovery**
   - RTO/RPO targets
   - Backup strategies
   - Recovery procedures

7. **Operational Runbooks**
   - Common operational tasks
   - Troubleshooting guides
   - Incident response

**When to Read**: When working on CI/CD or operational procedures

---

## Roadmap & Future Documents

### [15 – Future Roadmap](15-Future-Roadmap.md)
**Lines**: 1,190 | **Status**: ✅ Complete | **Priority**: LOW

**Purpose**: Strategic vision, planned features, and architectural evolution.

**Contents**:
1. **P0 Initiatives (Blockers)**
   - P0-001: UCL Violation Alerting
   - P0-002: Logging Coverage Tracking
   - P0-003: Performance Gates
   - P0-004: Sacred Geometry Validator
   - P0-005: JWT Authentication

2. **P1 Initiatives (High Priority)**
   - P1-001: Context Graph Visualizer
   - P1-002: Advanced Search
   - P1-003: Bulk Operations API
   - P1-004: MCP v2 Protocol
   - P1-005: Real-time Collaboration

3. **P2 Initiatives (Medium Priority)**
   - P2-001: AI-Powered Context Enrichment
   - P2-002: Automated Evidence Generation
   - P2-003: Mobile Application
   - P2-004: Slack/Teams Integration

4. **P3 Initiatives (Future Vision)**
   - P3-001: Multi-Tenant SaaS
   - P3-002: Workflow Designer UI
   - P3-003: Enterprise Reporting
   - P3-004: API Marketplace

5. **Maturity Path**
   - Prototype → Production → Enterprise
   - 3-tier evolution timeline

6. **Sacred Geometry Evolution**
   - Advanced workflow patterns
   - ContextForge.Spectre enhancements

**When to Read**: For strategic planning and long-term vision

---

## Supporting Documents

### [QUICK-START.md](QUICK-START.md)
**Lines**: ~300 | **Status**: ✅ Complete | **Priority**: HIGH

**Purpose**: Quick start guide for new users.

**Contents**:
- Your First 30 Minutes
- Reading Paths by Role
- Core Concepts You Must Know
- Essential Tools & Commands
- Learning Milestones
- Common Pitfalls to Avoid

**When to Read**: First document for all new team members

---

### [LIBRARY-MANIFEST.md](LIBRARY-MANIFEST.md)
**Lines**: ~450 | **Status**: ✅ Complete | **Priority**: LOW

**Purpose**: Complete document inventory with metadata.

**Contents**:
- Document inventory by category
- Completion timeline
- Technology stack coverage
- Framework coverage
- Cross-reference matrix
- Validation checklist

**When to Read**: For document management and validation

---

### [TABLE-OF-CONTENTS.md](TABLE-OF-CONTENTS.md) (This Document)
**Lines**: ~650 | **Status**: ✅ Complete | **Priority**: MEDIUM

**Purpose**: Hierarchical navigation of all documentation.

**When to Read**: For browsing and finding specific topics

---

## Appendices

### [Codex/ContextForge Work Codex](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md)
**Lines**: 276 | **Status**: ✅ Complete | **Priority**: HIGH

**Purpose**: Authoritative source for ContextForge philosophies and principles.

**Contents**:
- 11 Core Philosophies (detailed)
- COF 13-Dimensional Framework
- Metrics & Validation standards
- Maturity Path
- Appendices (Database Authority, Logging Taxonomy, Coverage Targets)

**When to Read**: Reference frequently; essential for understanding "why"

---

### [Codex/COF and UCL Definitions](Codex/COF%20and%20UCL%20Definitions.md)
**Lines**: 71 | **Status**: ✅ Complete | **Priority**: MEDIUM

**Purpose**: Complete COF 13-dimensional definitions and UCL enforcement.

**When to Read**: When applying COF to tasks or validating UCL compliance

---

## Index by Topic

### Context & Philosophy
- [01-Overview](01-Overview.md) - Core philosophies
- [03-Context-Ontology-Framework](03-Context-Ontology-Framework.md) - COF 13D, UCL, Sacred Geometry
- [Codex](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md) - Authoritative principles

### Architecture & Design
- [02-Architecture](02-Architecture.md) - System architecture
- [04-Desktop-Application-Architecture](04-Desktop-Application-Architecture.md) - TaskMan-v2
- [05-Database-Design-Implementation](05-Database-Design-Implementation.md) - Data layer
- [07-Workflow-Designer](07-Workflow-Designer.md) - Visual workflows

### Development & Engineering
- [09-Development-Guidelines](09-Development-Guidelines.md) - Daily practices
- [10-API-Reference](10-API-Reference.md) - API documentation
- [11-Configuration-Management](11-Configuration-Management.md) - Configuration

### Quality & Performance
- [08-Optimization-Standards](08-Optimization-Standards.md) - Performance optimization
- [13-Testing-Validation](13-Testing-Validation.md) - Testing strategies

### Operations & Security
- [12-Security-Authentication](12-Security-Authentication.md) - Security practices
- [14-Deployment-Operations](14-Deployment-Operations.md) - CI/CD and ops

### Features & Vision
- [06-Idea-Capture-System](06-Idea-Capture-System.md) - Idea management
- [15-Future-Roadmap](15-Future-Roadmap.md) - Strategic roadmap

---

## Statistics

**Total Documents**: 15 core + 3 supporting = 18 documents
**Total Lines**: 14,413 (core) + ~1,400 (supporting) = ~15,813 lines
**Completion**: 100% ✅
**Last Updated**: 2025-11-11
**Next Review**: 2026-02-11 (quarterly)

---

**Navigation Tip**: Use Ctrl+F (or Cmd+F) to search this table of contents for specific topics.

**Maintained By**: ContextForge Documentation Team

---

*"Documentation is resilience: when people change, systems endure only if knowledge is captured."* — ContextForge Work Codex
