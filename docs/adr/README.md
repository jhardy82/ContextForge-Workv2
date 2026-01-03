# Architecture Decision Records (ADR)

This directory contains all Architecture Decision Records for the ContextForge project, organized by architectural layer and concern.

## Directory Structure

```
docs/adr/
├── foundation/          # Core architectural decisions and foundational strategies
├── data-layer/          # Database, schema, and repository patterns
├── business-logic/      # Service layer and domain logic
├── api-layer/           # API routing, contracts, and endpoints
├── quality/             # Testing, security, documentation, production readiness
├── infrastructure/      # Hosting, deployment, auth providers, budgets
└── archived/            # Deprecated or superseded decisions
```

## Foundation

Core architectural patterns and planning strategies that underpin the entire system.

- **[ADR-001: QSE-UTMW Architecture](foundation/ADR-001-QSE-UTMW-Architecture.md)** - Quantum Sync Engine and Universal Task Management Workflow methodology
- **[ADR-016: Schema Audit - ActionList Integration](foundation/ADR-016-Schema-Audit-ActionList-Integration.md)** - Phase 3: Comprehensive schema audit strategy for TaskMan-v2 integration
- **[ADR-025: ActionList Code Review Gap Analysis](foundation/ADR-025-ActionList-Code-Review-Gap-Analysis.md)** *(if created)* - Phase 3: Systematic code review framework

## Data Layer

Database schema design, migration strategies, and repository implementation patterns.

- **[ADR-024: ActionList Database Schema Migration](data-layer/ADR-024-ActionList-Database-Schema-Migration.md)** - Phase 3: PostgreSQL ARRAY field with GIN indexing for action_items
- **[ADR-017: ActionList Repository Implementation](data-layer/ADR-017-ActionList-Repository-Implementation-Strategy.md)** - Phase 3: Specialized repository with Result monad and FastAPI DI

## Business Logic

Service layer architecture and domain logic orchestration.

- **[ADR-018: ActionList Service Layer Architecture](business-logic/ADR-018-ActionList-Service-Layer-Architecture.md)** - Phase 3: Rich Service Pattern with cross-entity orchestration

## API Layer

API routing, endpoint design, and contract specifications.

- **[ADR-019: ActionList API Router Architecture](api-layer/ADR-019-ActionList-API-Router-Architecture.md)** - Phase 3: Rich router with 9 endpoints including sub-resources

## Quality

Testing strategies, security patterns, documentation approaches, and production readiness.

- **[ADR-020: ActionList Authentication & Authorization](quality/ADR-020-ActionList-Authentication-Authorization.md)** - Phase 3: JWT Bearer with service-layer ownership validation
- **[ADR-021: ActionList API Documentation Strategy](quality/ADR-021-ActionList-API-Documentation-Strategy.md)** - Phase 3: Enhanced auto-generated docs using FastAPI
- **[ADR-022: ActionList Integration Testing Strategy](quality/ADR-022-ActionList-Integration-Testing-Strategy.md)** - Phase 3: PostgreSQL test DB with 60/30/10 pyramid (41 tests)
- **[ADR-023: ActionList Production Readiness Review](quality/ADR-023-ActionList-Production-Readiness-Review.md)** - Phase 3: 6-dimension quality framework with 47 validation criteria

## Infrastructure

Deployment, hosting, authentication providers, staging environments, and budget constraints.

- **[ADR-010: Auth Provider Selection](infrastructure/ADR-010-Auth-Provider-Selection.md)** - Authentication service provider evaluation
- **[ADR-011: Cloud Hosting Selection](infrastructure/ADR-011-Cloud-Hosting-Selection.md)** - Cloud platform evaluation and selection
- **[ADR-011: GitHub Ecosystem Analysis](infrastructure/ADR-011-GitHub-Ecosystem-Analysis.md)** - GitHub integration analysis
- **[ADR-012: Realtime Strategy](infrastructure/ADR-012-Realtime-Strategy.md)** - Real-time communication architecture
- **[ADR-013: Staging Environment](infrastructure/ADR-013-Staging-Environment.md)** - Pre-production environment setup
- **[ADR-014: Budget Constraints](infrastructure/ADR-014-Budget-Constraints.md)** - Cost optimization and resource allocation
- **[ADR-015: GitHub Ecosystem Maximization](infrastructure/ADR-015-GitHub-Ecosystem-Maximization.md)** - GitHub-native tooling strategy

## Archived

Deprecated or superseded decisions kept for historical reference.

- **[ADR-003: TaskMan-v2 Backend API Placeholder](archived/ADR-003-TaskMan-v2-Backend-API-Placeholder.md)** - Early backend API design (superseded)
- **[ADR-00XX: cf_core Test Stub Strategy](archived/ADR-00XX-cf_core-test-stub-strategy.md)** - Legacy test approach (superseded)

---

## ADR Template

All ADRs follow this standard structure:

```markdown
# ADR-XXX: [Title]

**Status**: [Proposed | Accepted | Deprecated | Superseded]
**Date**: YYYY-MM-DD
**Phase**: [Phase 1 | Phase 2 | Phase 3]
**Deciders**: [Names or roles]

## Context

What is the issue we're seeing that is motivating this decision or change?

## Decision

What is the change that we're proposing and/or doing?

## Consequences

What becomes easier or more difficult to do because of this change?
```

## Cross-References

### Phase 3 Planning Documents

- [PHASE-3-EXECUTION-PLAN.md](../../PHASE-3-EXECUTION-PLAN.md) - Comprehensive Phase 3 implementation roadmap (12 tasks, 16h estimate)
- [PHASE-3-QUICK-REFERENCE.md](../../PHASE-3-QUICK-REFERENCE.md) - At-a-glance metrics and command reference
- [PHASE-3-ADR-CATALOG.md](../../PHASE-3-ADR-CATALOG.md) - Central index of Phase 3 ADRs with summaries

### Implementation Guides

- Phase 3 tasks reference ADRs as authoritative design documents
- Each ADR includes code examples and test strategies
- Production readiness checklist (ADR-023) gates all deployments

---

**Last Updated**: 2025-12-28
**Maintained By**: ContextForge Architecture Team
