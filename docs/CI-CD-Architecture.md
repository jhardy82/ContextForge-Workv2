# ContextForge CI/CD Architecture

**Version**: 1.0.0
**Created**: 2025-12-06
**Status**: Active
**P0-006 Artifact**

---

## Overview

This document describes the ContextForge CI/CD (Continuous Integration/Continuous Deployment) architecture, including all GitHub Actions workflows, their purposes, and how they work together.

## CI/CD Maturity

**Current Level**: 63% (Level 0 CD, Level 3 CI)
**Target Level**: 85% (Level 2 CD, Level 4 CI)

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ContextForge CI/CD Pipeline                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │   COMMIT    │───▶│     PR      │───▶│   MERGE     │                 │
│  │   STAGE     │    │   STAGE     │    │   STAGE     │                 │
│  └─────────────┘    └─────────────┘    └─────────────┘                 │
│         │                 │                  │                          │
│         ▼                 ▼                  ▼                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │ pytest-pr   │    │ quality.yml │    │ security-   │                 │
│  │ .yml        │    │ (BLOCKING)  │    │ scanning    │                 │
│  │ (fast tests)│    │             │    │ .yml        │                 │
│  └─────────────┘    └─────────────┘    └─────────────┘                 │
│         │                 │                  │                          │
│         ▼                 ▼                  ▼                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │ coverage-   │    │ codeql.yml  │    │ deploy-     │                 │
│  │ check.yml   │    │ (security)  │    │ taskman.yml │                 │
│  │ (P0-007)    │    │             │    │ (prod)      │                 │
│  └─────────────┘    └─────────────┘    └─────────────┘                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Workflow Inventory

### Blocking Workflows (Must Pass for Merge)

| Workflow | File | Purpose | Trigger |
|----------|------|---------|---------|
| **Quality Gates** | `quality.yml` | CodeQL, Linting (ruff), Coverage, Stack validation | PR to main |
| **PR Tests** | `pytest-pr.yml` | Fast unit tests, JUnit reports | PR events |
| **Coverage Check** | `coverage-check.yml` | Validates P0-007 coverage config, 70% threshold | PR to main |

### Advisory Workflows (Informational)

| Workflow | File | Purpose | Trigger |
|----------|------|---------|---------|
| **Security Scanning** | `security-scanning.yml` | Bandit SAST, pip-audit, Safety | Schedule + Manual |
| **Observability** | `observability-tests.yml` | Schema validation tests | PR events |
| **DevSecOps** | `devsecops-pipeline.yml` | DAST, Container scanning (planned) | Schedule |

### Deployment Workflows

| Workflow | File | Purpose | Trigger |
|----------|------|---------|---------|
| **TaskMan Deploy** | `deploy-taskman.yml` | Production deployment via Docker + SSH | Manual dispatch |

## Coverage Configuration (P0-007)

### Source Paths Included
```toml
# From pyproject.toml [tool.coverage.run]
source = [
    "src",
    "python",
    "cf_core",
    "cli",
    "mcp_servers"
]
```

### Paths Excluded
```toml
# From pyproject.toml [tool.coverage.run]
omit = [
    "**/tests/**",
    "**/test_*.py",
    "**/__pycache__/**",
    "**/node_modules/**",
    ".venv/**"
]
```

### Threshold Enforcement
- **Minimum**: 70% line coverage
- **Target**: 80% line coverage
- **Branch Target**: 45% (currently 25%)

## Workflow Dependencies

```
┌────────────────────────────────────────────────────────────────┐
│                     Dependency Graph                           │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  P0-007 (Coverage Fix)                                         │
│       │                                                        │
│       ├───▶ coverage-check.yml (USES P0-007 config)            │
│       │                                                        │
│       ├───▶ quality.yml (USES P0-007 config)                   │
│       │                                                        │
│       └───▶ Branch Coverage 25%→45% (ENABLED BY P0-007)        │
│                                                                │
│  P0-005 (JWT Mock)                                             │
│       │                                                        │
│       └───▶ P0-009 (Auth0 Production)                          │
│                                                                │
│  DevSecOps (65%→85%)                                           │
│       │                                                        │
│       ├───▶ DAST (OWASP ZAP) - PLANNED                         │
│       │                                                        │
│       ├───▶ Container Scanning (Trivy) - PLANNED               │
│       │                                                        │
│       └───▶ IaC Security (tfsec) - PLANNED                     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Running Workflows Locally

### Coverage Check
```bash
# Activate venv
& ".venv/Scripts/Activate.ps1"

# Run with coverage
python -m pytest --cov=src --cov=python --cov=cf_core --cov=cli --cov=mcp_servers \
    --cov-report=term-missing --cov-fail-under=70 \
    tests/ -v
```

### Quality Gates
```bash
# Python linting
python -m ruff check .
python -m ruff format --check .

# Type checking (if configured)
python -m mypy src/ --strict
```

### Security Scanning
```bash
# Bandit SAST
python -m bandit -r src/ python/ cf_core/ cli/ -f json -o bandit-results.json

# Dependency audit
pip-audit --desc
```

## Adding New Workflows

When adding new GitHub Actions workflows:

1. **Follow the pattern** from `coverage-check.yml` (newest, most aligned with P0-007)
2. **Use environment variables** for configurable thresholds
3. **Add path filters** to avoid unnecessary runs
4. **Include manual dispatch** (`workflow_dispatch`) for testing
5. **Upload artifacts** for debugging
6. **Add PR comments** for visibility

## Roadmap

### Short Term (Sprint 1-2)
- [x] P0-007: Fix coverage configuration
- [x] P0-006: Add coverage-check.yml
- [ ] Branch coverage enforcement in CI

### Medium Term (Sprint 3-4)
- [ ] DAST integration (OWASP ZAP)
- [ ] Container scanning (Trivy)
- [ ] IaC security (tfsec)
- [ ] Multi-environment deployment

### Long Term (Sprint 5+)
- [ ] Blue-green deployments
- [ ] Canary releases
- [ ] Automated rollback on failure
- [ ] Performance regression testing

---

## Related Documents

- [09-Development-Guidelines.md](09-Development-Guidelines.md) - Code quality standards
- [13-Testing-Validation.md](13-Testing-Validation.md) - Testing framework
- [pyproject.toml](../pyproject.toml) - Coverage configuration (P0-007)

---

**Document Status**: Active ✅
**Last Updated**: 2025-12-06
**Maintained By**: Team ALPHA (Solution Architecture + DevOps)
