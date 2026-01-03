# TaskMan-v2 MVP Completion Action Plan

**Created**: 2025-12-27  
**Owner**: James  
**Status**: Active  
**Target**: Production-ready MVP in 5-7 weeks

---

## Executive Summary

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Production Readiness | 75% | 100% | 25% |
| JWT Authentication | 0% | 100% | P0-005 |
| CI/CD Pipeline | 40% | 100% | P0-006 |
| Branch Coverage | 0.4% | 70% | P0-007 |
| Test Collection | 95.8% | 99%+ | P0-008 |
| CLI Unification | 5 CLIs | 1 CLI | P1-001 |

**Total Effort**: ~160-200 hours across 5-7 weeks

---

## Phase 1: Critical Blockers (Weeks 1-3)

### P0-005: JWT Authentication
**Effort**: 12-15 days | **Risk**: HIGH | **Blocks**: Production deployment

| Task | Hours | Owner | DoD |
|------|-------|-------|-----|
| Create Auth0 tenant + application | 2h | - | Tenant created, callback URLs configured |
| FastAPI auth middleware | 8h | - | `verify_token` dependency, 401 on invalid |
| React Auth0 provider integration | 6h | - | Login/logout working, tokens in headers |
| RBAC role configuration | 4h | - | 4 roles: admin, developer, viewer, guest |
| Protected route middleware | 4h | - | Role-based endpoint protection |
| Playwright auth tests | 8h | - | Login flow, protected routes, logout |
| **Subtotal** | **32h** | | |

**Dependencies**: ADR-010 approved, Auth0 account created

### P0-006: CI/CD Pipeline
**Effort**: 10-12 days | **Risk**: HIGH | **Blocks**: Automated deployments

| Task | Hours | Owner | DoD |
|------|-------|-------|-----|
| Vercel frontend deployment | 4h | - | Auto-deploy on main push |
| Railway backend deployment | 6h | - | Docker deploy, health checks |
| Railway PostgreSQL setup | 4h | - | Managed DB, connection working |
| GitHub Actions workflow | 8h | - | Build → Test → Deploy pipeline |
| Coverage enforcement gate | 4h | - | Block if coverage < 70% |
| Staging environment | 6h | - | PR previews, staging Auth0 |
| **Subtotal** | **32h** | | |

**Dependencies**: ADR-011 approved, Vercel/Railway accounts

### P0-008: Test Collection Errors
**Effort**: 5-7 days | **Risk**: MEDIUM | **Blocks**: Coverage measurement

| Task | Hours | Owner | DoD |
|------|-------|-------|-----|
| Audit 93 collection errors | 4h | - | Categorized error list |
| Fix import errors | 8h | - | All imports resolve |
| Fix fixture errors | 6h | - | conftest.py cleaned |
| Remove/archive orphaned tests | 4h | - | No dead test files |
| Validate collection | 2h | - | `pytest --collect-only` clean |
| **Subtotal** | **24h** | | |

**Dependencies**: None (can start immediately)

---

## Phase 2: Stabilization (Weeks 4-6)

### P0-007: Branch Coverage Remediation
**Effort**: 14-18 days | **Risk**: HIGH | **Blocks**: Quality gate

| Task | Hours | Owner | DoD |
|------|-------|-------|-----|
| Generate coverage baseline | 2h | - | coverage-branch-baseline.json |
| Identify uncovered branches | 8h | - | Prioritized remediation list |
| cf_core domain tests | 20h | - | 70% branch coverage |
| FastAPI endpoint tests | 16h | - | All routes have tests |
| CLI command tests | 12h | - | All commands have tests |
| Integration tests | 12h | - | DB operations tested |
| **Subtotal** | **70h** | | |

**Dependencies**: P0-008 complete (clean test collection)

### P1-001: CLI Unification Phase 2
**Effort**: 5-6 days | **Risk**: LOW | **Unblocks**: User experience

| Task | Hours | Owner | DoD |
|------|-------|-------|-----|
| Migrate velocity commands | 8h | - | `cf velocity` working |
| Migrate context commands | 8h | - | `cf context` working |
| Deprecation warnings | 4h | - | Old CLIs warn users |
| Documentation update | 4h | - | CLI-REFERENCE.md updated |
| **Subtotal** | **24h** | | |

**Dependencies**: None (can parallelize with coverage)

### Staging Environment Hardening
**Effort**: 4-5 days | **Risk**: MEDIUM

| Task | Hours | Owner | DoD |
|------|-------|-------|-----|
| Railway staging project | 4h | - | Separate environment |
| Auth0 dev tenant | 4h | - | Isolated from prod |
| Seed data scripts | 6h | - | Reproducible test data |
| Environment parity check | 4h | - | Staging matches prod config |
| **Subtotal** | **18h** | | |

---

## Phase 3: Polish and Launch (Weeks 7-8)

### Security Hardening
**Effort**: 4-5 days | **Risk**: LOW

| Task | Hours | Owner | DoD |
|------|-------|-------|-----|
| OWASP Top 10 review | 8h | - | Checklist complete |
| Rate limiting | 4h | - | 100 req/min per user |
| Input validation audit | 4h | - | All endpoints validated |
| Dependency audit | 2h | - | `pip-audit` clean |
| **Subtotal** | **18h** | | |

### Documentation Polish
**Effort**: 3-4 days | **Risk**: LOW

| Task | Hours | Owner | DoD |
|------|-------|-------|-----|
| API documentation (OpenAPI) | 6h | - | /docs endpoint complete |
| Runbook for operations | 4h | - | Deployment, rollback, monitoring |
| Onboarding guide | 4h | - | <30 min onboarding |
| **Subtotal** | **14h** | | |

### Production Launch
**Effort**: 2 days | **Risk**: MEDIUM

| Task | Hours | Owner | DoD |
|------|-------|-------|-----|
| Pre-launch checklist | 4h | - | All gates green |
| Production deployment | 4h | - | Live and healthy |
| Smoke test suite | 2h | - | Critical paths verified |
| Monitoring setup | 4h | - | Alerts configured |
| Launch announcement | 2h | - | Stakeholders notified |
| **Subtotal** | **16h** | | |

---

## Total Effort Summary

| Phase | Duration | Hours | Risk |
|-------|----------|-------|------|
| Phase 1: Critical Blockers | 3 weeks | 88h | HIGH |
| Phase 2: Stabilization | 3 weeks | 112h | MEDIUM |
| Phase 3: Polish + Launch | 2 weeks | 48h | LOW |
| **Total** | **5-7 weeks** | **~248h** | |

---

## Decision Checkpoints

### Week 1 Checkpoint
- [ ] ADR-010 (Auth Provider) approved
- [ ] ADR-011 (Cloud Hosting) approved
- [ ] Auth0 tenant created
- [ ] Vercel/Railway accounts ready

### Week 3 Checkpoint
- [ ] JWT authentication working end-to-end
- [ ] CI/CD pipeline deploying to staging
- [ ] Test collection errors < 10

### Week 5 Checkpoint
- [ ] Branch coverage > 50%
- [ ] CLI unification complete
- [ ] Staging environment stable

### Week 7 Checkpoint
- [ ] Branch coverage > 70%
- [ ] Security review complete
- [ ] Documentation complete
- [ ] GO/NO-GO decision for production

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Auth0 integration issues | Medium | High | Use Keycloak fallback |
| Branch coverage < 70% | High | High | Focus on critical paths first |
| React 19 test compatibility | Medium | Medium | Use Playwright for E2E |
| Railway cold starts | Low | Low | Health check keep-alive |
| Scope creep | High | Medium | Strict P0-only focus |

---

## Success Criteria

### MVP Definition of Done
- [ ] JWT authentication working (login, logout, protected routes)
- [ ] CI/CD pipeline deploying automatically
- [ ] Branch coverage ≥ 70%
- [ ] Test collection errors < 5
- [ ] WCAG-AA accessibility verified
- [ ] Staging environment operational
- [ ] Production deployment successful
- [ ] Onboarding time < 30 minutes

---

## Quick Reference Commands

```bash
# Run tests with coverage
python -m pytest --cov=cf_core --cov-branch --cov-report=html

# Check test collection
python -m pytest --collect-only 2>&1 | grep -E "(ERROR|error)"

# Run Playwright E2E
cd TaskMan-v2 && npm run test:e2e

# Deploy to staging (manual)
railway up --environment staging

# Check branch coverage
python -m coverage report --show-missing --fail-under=70
```

---

## Links

* [ADR-010: Auth Provider](../adr/ADR-010-Auth-Provider-Selection.md)
* [ADR-011: Cloud Hosting](../adr/ADR-011-Cloud-Hosting-Selection.md)
* [ADR-012: Realtime Strategy](../adr/ADR-012-Realtime-Strategy.md)
* [ADR-013: Staging Environment](../adr/ADR-013-Staging-Environment.md)
* [ADR-014: Budget Constraints](../adr/ADR-014-Budget-Constraints.md)
* [Stack Compatibility Answers](STACK_COMPATIBILITY_ANSWERS.md)
