# MVP Completion Action Plan

**Status**: Draft
**Version**: 1.0
**Created**: 2025-12-27
**Based On**: [15-Future-Roadmap.md](15-Future-Roadmap.md), [STACK_COMPATIBILITY_ANSWERS.md](stack/STACK_COMPATIBILITY_ANSWERS.md)

---

## Executive Summary

**Current Status**: 75% Production Ready
**Target**: 100% MVP Launch Ready
**Timeline**: 5-7 weeks (Q1 2026)

### Critical Blockers (Must Complete)

| ID | Blocker | Current | Target | Effort |
|----|---------|---------|--------|--------|
| P0-005 | JWT Authentication | 0% | 100% | 2-3 weeks |
| P0-006 | CI/CD Pipeline | 40% | 100% | 2-3 weeks |
| P0-007 | Branch Coverage | 0.4% | 70% | 4-6 weeks |
| P0-008 | Test Collection Errors | 95.8% | 99%+ | 1-2 weeks |

### Architecture Decision Required

| Decision | Options | Recommendation | Impact |
|----------|---------|----------------|--------|
| Auth Provider | Auth0 vs Keycloak | **Auth0** (MVP) | Affects P0-005 |
| Cloud Provider | Azure/AWS/GCP | Any (Docker/K8s) | Affects P0-006 |
| Staging Environment | Yes/No | **Yes** | Reduces production risk |

---

## Phase 1: Critical Blockers (Weeks 1-3)

**Goal**: Unblock production deployment by completing authentication and CI/CD foundation.

---

### Task 1.1: JWT Authentication Implementation (P0-005)

**Priority**: 🔥 CRITICAL
**Effort**: 12-15 days (2-3 weeks)
**Dependencies**: Auth0 account setup
**Risk Level**: HIGH (blocks production)

#### Subtasks

| ID | Subtask | Effort | Owner | Status |
|----|---------|--------|-------|--------|
| 1.1.1 | Create Auth0 tenant & configure application | 2h | DevOps | Pending |
| 1.1.2 | Implement JWT token verification middleware | 8h | Backend | Pending |
| 1.1.3 | Add HTTPBearer dependency injection | 4h | Backend | Pending |
| 1.1.4 | Implement RBAC (4 roles: admin, developer, viewer, guest) | 8h | Backend | Pending |
| 1.1.5 | Protect all API endpoints with auth decorators | 8h | Backend | Pending |
| 1.1.6 | Token refresh mechanism | 6h | Backend | Pending |
| 1.1.7 | Frontend: Auth0 React SDK integration | 8h | Frontend | Pending |
| 1.1.8 | Frontend: Protected route wrapper | 4h | Frontend | Pending |
| 1.1.9 | Frontend: Login/logout UI flow | 6h | Frontend | Pending |
| 1.1.10 | Integration tests for auth flows | 8h | QA | Pending |
| 1.1.11 | Security audit (OWASP checklist) | 4h | Security | Pending |

**Total Effort**: ~66 hours (~8-10 working days)

#### Implementation Details

**Backend Middleware** (`TaskMan-v2/backend-api/src/taskman_api/middleware/auth.py`):
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import Optional
import httpx

security = HTTPBearer()

class TokenPayload(BaseModel):
    sub: str
    email: Optional[str] = None
    roles: list[str] = []
    exp: int

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenPayload:
    """Verify JWT token from Auth0."""
    token = credentials.credentials
    try:
        # Fetch Auth0 JWKS for verification
        payload = jwt.decode(
            token,
            key=await get_auth0_public_key(),
            algorithms=["RS256"],
            audience=settings.auth0_audience,
            issuer=f"https://{settings.auth0_domain}/"
        )
        return TokenPayload(**payload)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

def require_role(allowed_roles: list[str]):
    """RBAC decorator for role-based access."""
    async def role_checker(token: TokenPayload = Depends(verify_token)):
        if not any(role in token.roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return token
    return role_checker
```

#### Definition of Done

- [ ] All 28 API endpoints protected with JWT verification
- [ ] RBAC enforced: admin (full), developer (CRUD tasks), viewer (read-only), guest (limited)
- [ ] Token refresh works (silent refresh before expiry)
- [ ] Secrets stored in environment variables (not committed)
- [ ] Auth0 production tenant configured
- [ ] Frontend login/logout works end-to-end
- [ ] 10+ auth integration tests passing
- [ ] Security scan (Bandit) passes with no HIGH/CRITICAL issues
- [ ] Audit logging for auth events (token_verified, permission_denied)

---

### Task 1.2: CI/CD Pipeline Foundation (P0-006)

**Priority**: 🔥 CRITICAL
**Effort**: 10-12 days (2-3 weeks)
**Dependencies**: P0-005 (for deployment testing)
**Risk Level**: HIGH

#### Current State

| Workflow | Status | Blocking |
|----------|--------|----------|
| taskman-docker-build.yml | ✅ Exists | No |
| playwright.yml | ✅ Exists | No |
| Backend tests | ⚠️ Partial | Yes |
| Deployment automation | ❌ Missing | Yes |
| Coverage gates | ⚠️ Partial | Yes |

#### Subtasks

| ID | Subtask | Effort | Owner | Status |
|----|---------|--------|-------|--------|
| 1.2.1 | Add pytest + coverage to backend workflow | 4h | DevOps | Pending |
| 1.2.2 | Add Vitest + coverage to frontend workflow | 4h | DevOps | Pending |
| 1.2.3 | Configure coverage threshold gates (70%) | 2h | DevOps | Pending |
| 1.2.4 | Add security scanning (Bandit + npm audit) | 4h | DevOps | Pending |
| 1.2.5 | Create staging environment configuration | 8h | DevOps | Pending |
| 1.2.6 | Implement blue-green deployment script | 8h | DevOps | Pending |
| 1.2.7 | Add database migration step (Alembic) | 4h | DevOps | Pending |
| 1.2.8 | Add health check verification post-deploy | 2h | DevOps | Pending |
| 1.2.9 | Implement rollback mechanism | 6h | DevOps | Pending |
| 1.2.10 | Add E2E smoke tests post-deployment | 6h | QA | Pending |
| 1.2.11 | Document deployment runbook | 4h | DevOps | Pending |

**Total Effort**: ~52 hours (~6-7 working days)

#### Workflow Enhancement

**Enhanced Backend Workflow** (`.github/workflows/taskman-backend-ci.yml`):
```yaml
name: TaskMan Backend CI

on:
  push:
    branches: [main]
    paths: ['TaskMan-v2/backend-api/**']
  pull_request:
    paths: ['TaskMan-v2/backend-api/**']

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: taskman_test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        ports: ['5432:5432']
        options: >-
          --health-cmd pg_isready
          --health-interval 10s

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: cd TaskMan-v2/backend-api && uv sync --all-extras

      - name: Run pytest with coverage
        run: |
          cd TaskMan-v2/backend-api
          uv run pytest --cov=src --cov-report=xml --cov-branch --cov-fail-under=70

      - name: Security scan (Bandit)
        run: |
          cd TaskMan-v2/backend-api
          uv run bandit -r src -f json -o bandit-report.json

      - name: Upload coverage
        uses: codecov/codecov-action@v4

  deploy-staging:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Deploy to staging
        run: echo "Deploy to staging environment"

  deploy-production:
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to production (blue-green)
        run: echo "Production deployment"
```

#### Definition of Done

- [ ] All commits trigger automated tests
- [ ] Coverage threshold (70%) enforced - builds fail if not met
- [ ] Security scans run on every PR
- [ ] Staging deployment automatic on main merge
- [ ] Production deployment requires manual approval
- [ ] Rollback tested and documented
- [ ] Health checks verify deployment success
- [ ] Deployment runbook documented

---

### Task 1.3: Test Collection Error Resolution (P0-008)

**Priority**: MEDIUM
**Effort**: 5-7 days
**Dependencies**: None
**Risk Level**: MEDIUM

#### Current State

- **Collection Success**: 95.8% (2,226 tests collected)
- **Collection Errors**: 93 errors
- **Target**: 99%+ (≤5 deferred errors)

#### Subtasks

| ID | Subtask | Effort | Owner | Status |
|----|---------|--------|-------|--------|
| 1.3.1 | Categorize all 93 errors (import, syntax, config, path) | 4h | QA | Pending |
| 1.3.2 | Fix import errors (~37 files) | 8h | QA | Pending |
| 1.3.3 | Fix syntax errors (~19 files) | 4h | QA | Pending |
| 1.3.4 | Fix pytest configuration errors (~23 files) | 6h | QA | Pending |
| 1.3.5 | Fix path/import errors (~14 files) | 4h | QA | Pending |
| 1.3.6 | Defer non-critical legacy tests (document) | 2h | QA | Pending |
| 1.3.7 | Verify 99%+ collection rate | 2h | QA | Pending |

**Total Effort**: ~30 hours (~4-5 working days)

#### Definition of Done

- [ ] ≥99% test collection success rate
- [ ] All fixable errors resolved
- [ ] Deferred tests documented with rationale
- [ ] CI gate enforces collection success

---

## Phase 2: Stabilization (Weeks 4-6)

**Goal**: Achieve branch coverage target and stabilize test infrastructure.

---

### Task 2.1: Branch Coverage Remediation (P0-007)

**Priority**: HIGH
**Effort**: 20-30 days (4-6 weeks, can overlap with Phase 1)
**Dependencies**: P0-008 (clean test collection)
**Risk Level**: HIGH

#### Current State

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Branch Coverage | 0.4% | 70% | -69.6% |
| Unit Test Coverage | ~60% | 70% | -10% |
| Integration Coverage | ~30% | 40% | -10% |

#### Phased Approach

**Week 1: Assessment & Quick Wins**
| ID | Subtask | Effort | Target Coverage |
|----|---------|--------|-----------------|
| 2.1.1 | Run coverage analysis (pytest-cov --branch) | 2h | Baseline |
| 2.1.2 | Identify critical paths with 0% coverage | 4h | Prioritized list |
| 2.1.3 | Fix low-hanging fruit (simple branches) | 8h | +5% |

**Week 2-3: Core Path Coverage**
| ID | Subtask | Effort | Target Coverage |
|----|---------|--------|-----------------|
| 2.1.4 | Add tests for API endpoint branches | 16h | 30% |
| 2.1.5 | Add tests for service layer branches | 16h | 40% |
| 2.1.6 | Add tests for error handling paths | 12h | 50% |

**Week 4-5: Edge Case Coverage**
| ID | Subtask | Effort | Target Coverage |
|----|---------|--------|-----------------|
| 2.1.7 | Add tests for validation branches | 12h | 55% |
| 2.1.8 | Add tests for configuration branches | 8h | 60% |
| 2.1.9 | Add tests for fallback/retry logic | 10h | 65% |

**Week 6: Final Push**
| ID | Subtask | Effort | Target Coverage |
|----|---------|--------|-----------------|
| 2.1.10 | Add remaining high-priority tests | 12h | 70% |
| 2.1.11 | Document coverage exclusions | 4h | N/A |
| 2.1.12 | Set up coverage regression alerts | 4h | N/A |

**Total Effort**: ~108 hours (~14-18 working days)

#### Focus Areas (by Impact)

1. **TaskMan-v2 Backend API** (highest value)
   - `src/taskman_api/services/` - Business logic branches
   - `src/taskman_api/api/` - Request validation branches
   - `src/taskman_api/core/errors.py` - Error handling branches

2. **cf_core Domain** (core functionality)
   - `cf_core/domain/` - Entity validation
   - `cf_core/services/` - Service layer logic
   - `cf_core/repositories/` - Data access patterns

3. **CLI Commands** (user-facing)
   - `cf_core/cli/commands/` - Input validation
   - Error handling and edge cases

#### Definition of Done

- [ ] Branch coverage ≥70% in critical paths
- [ ] All error handling paths tested
- [ ] CI gate enforces coverage threshold
- [ ] Coverage report generated on every PR
- [ ] No regression allowed (coverage can only increase)

---

### Task 2.2: CLI Unification Phase 2 (P1)

**Priority**: MEDIUM
**Effort**: 10-15 days
**Dependencies**: Phase 1 complete
**Risk Level**: LOW

#### Current State

- **Phase 1**: ✅ COMPLETE - `cf_core.cli.main` is PRIMARY
- **Remaining**: Migrate specialty commands (velocity, context, legacy)

#### Subtasks

| ID | Subtask | Effort | Owner | Status |
|----|---------|--------|-------|--------|
| 2.2.1 | Migrate velocity commands to cf_core | 8h | Platform | Pending |
| 2.2.2 | Migrate context commands to cf_core | 8h | Platform | Pending |
| 2.2.3 | Add deprecation warnings to legacy CLIs | 4h | Platform | Pending |
| 2.2.4 | Update all documentation references | 6h | Docs | Pending |
| 2.2.5 | Create migration guide for users | 4h | Docs | Pending |
| 2.2.6 | CLI test coverage >80% | 12h | QA | Pending |

**Total Effort**: ~42 hours (~5-6 working days)

#### Definition of Done

- [ ] All commands available via `python -m cf_core.cli.main`
- [ ] Legacy CLIs emit deprecation warnings
- [ ] Migration guide published
- [ ] CLI test coverage ≥80%
- [ ] Onboarding time <30 minutes (measured)

---

### Task 2.3: Staging Environment Setup

**Priority**: MEDIUM
**Effort**: 5-7 days
**Dependencies**: P0-006 (CI/CD)
**Risk Level**: MEDIUM (reduces production risk)

#### Subtasks

| ID | Subtask | Effort | Owner | Status |
|----|---------|--------|-------|--------|
| 2.3.1 | Provision staging infrastructure (Docker Compose) | 8h | DevOps | Pending |
| 2.3.2 | Configure staging database (PostgreSQL) | 4h | DevOps | Pending |
| 2.3.3 | Set up staging environment variables | 2h | DevOps | Pending |
| 2.3.4 | Configure Auth0 staging tenant | 2h | DevOps | Pending |
| 2.3.5 | Implement staging data seeding | 4h | DevOps | Pending |
| 2.3.6 | Add staging smoke tests | 6h | QA | Pending |
| 2.3.7 | Document staging access and usage | 4h | DevOps | Pending |

**Total Effort**: ~30 hours (~4-5 working days)

#### Definition of Done

- [ ] Staging environment accessible at staging.contextforge.dev
- [ ] Staging reflects main branch automatically
- [ ] Auth0 staging tenant configured
- [ ] Smoke tests run after every staging deployment
- [ ] Staging data reset mechanism available

---

## Phase 3: Polish and Launch (Weeks 7-8)

**Goal**: Final hardening, documentation, and production launch.

---

### Task 3.1: Security Hardening

**Priority**: HIGH
**Effort**: 5-7 days
**Dependencies**: P0-005 (auth), P0-006 (CI/CD)
**Risk Level**: LOW

#### Subtasks

| ID | Subtask | Effort | Owner | Status |
|----|---------|--------|-------|--------|
| 3.1.1 | OWASP Top 10 review | 8h | Security | Pending |
| 3.1.2 | Secret rotation procedure documentation | 4h | Security | Pending |
| 3.1.3 | Rate limiting implementation | 6h | Backend | Pending |
| 3.1.4 | CORS configuration hardening | 2h | Backend | Pending |
| 3.1.5 | Security headers (CSP, HSTS) | 4h | DevOps | Pending |
| 3.1.6 | Penetration testing (basic) | 8h | Security | Pending |
| 3.1.7 | Security incident response plan | 4h | Security | Pending |

**Total Effort**: ~36 hours (~4-5 working days)

#### Definition of Done

- [ ] OWASP Top 10 checklist completed
- [ ] Rate limiting active on all endpoints
- [ ] Security headers configured
- [ ] No HIGH/CRITICAL findings in security scan
- [ ] Incident response plan documented

---

### Task 3.2: Documentation Polish

**Priority**: MEDIUM
**Effort**: 3-5 days
**Dependencies**: All P0 complete
**Risk Level**: LOW

#### Subtasks

| ID | Subtask | Effort | Owner | Status |
|----|---------|--------|-------|--------|
| 3.2.1 | Update API documentation (OpenAPI) | 4h | Backend | Pending |
| 3.2.2 | Update deployment documentation | 4h | DevOps | Pending |
| 3.2.3 | Create user onboarding guide | 6h | Docs | Pending |
| 3.2.4 | Update README with production URLs | 2h | Docs | Pending |
| 3.2.5 | Create FAQ/troubleshooting guide | 4h | Docs | Pending |
| 3.2.6 | Record demo video (optional) | 4h | Product | Pending |

**Total Effort**: ~24 hours (~3-4 working days)

#### Definition of Done

- [ ] API docs current with all endpoints
- [ ] Deployment runbook complete
- [ ] User can onboard in <30 minutes
- [ ] README reflects production state

---

### Task 3.3: Production Launch Checklist

**Priority**: HIGH
**Effort**: 2-3 days
**Dependencies**: All above complete
**Risk Level**: MEDIUM

#### Pre-Launch Checklist

| Category | Check | Status |
|----------|-------|--------|
| **Auth** | JWT auth working end-to-end | ⬜ |
| **Auth** | RBAC enforced correctly | ⬜ |
| **Auth** | Auth0 production tenant live | ⬜ |
| **CI/CD** | All tests passing | ⬜ |
| **CI/CD** | Coverage ≥70% | ⬜ |
| **CI/CD** | Deployment pipeline tested | ⬜ |
| **CI/CD** | Rollback tested | ⬜ |
| **Security** | Security scan passed | ⬜ |
| **Security** | Rate limiting active | ⬜ |
| **Security** | Secrets in vault (not env) | ⬜ |
| **Monitoring** | Health endpoints working | ⬜ |
| **Monitoring** | Error alerting configured | ⬜ |
| **Docs** | API docs published | ⬜ |
| **Docs** | Runbook complete | ⬜ |
| **Data** | Production database provisioned | ⬜ |
| **Data** | Backup strategy implemented | ⬜ |

#### Launch Day Tasks

| ID | Task | Effort | Owner |
|----|------|--------|-------|
| 3.3.1 | Final staging validation | 2h | QA |
| 3.3.2 | Database migration execution | 1h | DevOps |
| 3.3.3 | Production deployment (blue-green) | 2h | DevOps |
| 3.3.4 | Smoke test production | 1h | QA |
| 3.3.5 | Monitor for 4 hours | 4h | All |
| 3.3.6 | Announce launch internally | 1h | Product |

**Total Effort**: ~11 hours

---

## Risk Register

| Risk | Probability | Impact | Mitigation | Owner |
|------|-------------|--------|------------|-------|
| Auth0 integration issues | Medium | High | Early POC in Week 1 | Backend |
| Coverage target not met | Medium | High | Prioritize critical paths, accept 65% minimum | QA |
| CI/CD complexity | Low | Medium | Use existing workflow patterns | DevOps |
| Staging environment delays | Medium | Medium | Use local Docker Compose as fallback | DevOps |
| React 19 ESM issues persist | Medium | Medium | Defer affected tests, document workarounds | Frontend |
| Team availability | Medium | High | Cross-train on critical tasks | All |

---

## Timeline Summary

```
Week 1-2:  ████████████████ JWT Auth (P0-005)
Week 2-3:  ████████████████ CI/CD Pipeline (P0-006)
Week 1-2:  ████████     Test Collection Errors (P0-008)
Week 2-6:  ████████████████████████████████ Branch Coverage (P0-007)
Week 4-5:  ████████████ CLI Unification Phase 2
Week 4-5:  ████████████ Staging Environment
Week 6-7:  ████████████ Security Hardening
Week 7:    ████████     Documentation Polish
Week 8:    ████         Production Launch
```

---

## Success Metrics

| Metric | Baseline | Target | Validation |
|--------|----------|--------|------------|
| Production Readiness | 75% | 100% | All P0 complete |
| Branch Coverage | 0.4% | 70% | pytest-cov report |
| Test Collection | 95.8% | 99%+ | pytest --collect-only |
| API Endpoints Protected | 0 | 28 | Security audit |
| CLI Commands | 5 fragmented | 1 unified | Command inventory |
| Onboarding Time | Unknown | <30 min | User testing |
| Security Findings | Unknown | 0 HIGH/CRITICAL | Bandit + npm audit |
| Deployment Time | Manual | <10 min automated | CI/CD metrics |

---

## Appendix A: Resource Requirements

| Role | Allocation | Weeks |
|------|------------|-------|
| Backend Developer | 1 FTE | 1-6 |
| Frontend Developer | 0.5 FTE | 1-3 |
| DevOps Engineer | 1 FTE | 2-6 |
| QA Engineer | 1 FTE | 1-7 |
| Security Engineer | 0.25 FTE | 6-7 |
| Technical Writer | 0.25 FTE | 7-8 |

**Total**: ~4 FTE for 8 weeks

---

## Appendix B: Decision Log

| Date | Decision | Rationale | Impact |
|------|----------|-----------|--------|
| 2025-12-27 | Use Auth0 for MVP | Faster implementation, managed service | P0-005 timeline |
| 2025-12-27 | Target 70% branch coverage | Balances quality vs. timeline | P0-007 scope |
| 2025-12-27 | Staging environment required | Reduces production deployment risk | Phase 2 scope |
| TBD | Cloud provider selection | Affects deployment pipelines | P0-006 |

---

## Related Documents

- [15-Future-Roadmap.md](15-Future-Roadmap.md) - Strategic roadmap
- [STACK_COMPATIBILITY_ANSWERS.md](stack/STACK_COMPATIBILITY_ANSWERS.md) - Technical constraints
- [13-Testing-Validation.md](13-Testing-Validation.md) - QSE framework
- [12-Security-Authentication.md](12-Security-Authentication.md) - Security requirements

---

**Document Status**: Draft ✅
**Next Review**: After Phase 1 completion
**Maintained By**: ContextForge Engineering Team
