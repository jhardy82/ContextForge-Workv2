---
schema_version: "1.1"
created_utc: "2025-12-27T12:00:00Z"
updated_utc: "2025-12-27T16:00:00Z"
owner: "James"
playwright_available: true
github_pro: true

# Related Decision Documents
related_adrs:
  - "../adr/ADR-010-Auth-Provider-Selection.md"
  - "../adr/ADR-011-Cloud-Hosting-Selection.md"
  - "../adr/ADR-012-Realtime-Strategy.md"
  - "../adr/ADR-013-Staging-Environment.md"
  - "../adr/ADR-014-Budget-Constraints.md"
  - "../adr/ADR-015-GitHub-Ecosystem-Maximization.md"
action_plan: "./MVP-ACTION-PLAN.md"

# GitHub Pro Features Available
github_ecosystem:
  actions_minutes: 3000
  packages_storage_gb: 2
  codespaces_hours: 180
  pages_private_repos: true
  environments: true
  protected_branches: true
  oauth_apps: true

product:
  app_type: "Internal tool"
  primary_domain: "Enterprise work orchestration platform - task management, analytics, AI-augmented development workflows"
  target_users: "Engineers (primary), Compliance/Audit teams (secondary), Leadership (tertiary) - technical professionals in enterprise environments requiring structured, evidence-backed work management"
  success_metrics:
    - "TaskMan-v2 production readiness: 75% → 100% (GitHub OAuth, CI/CD, 70% branch coverage as blockers)"
    - "CLI unification: 5 fragmented CLIs → 1 unified cf_core CLI with >80% test coverage, onboarding <30 min"
  delivery_timeline: "Q1 2026 (P0 blockers), Q2 2026 (P1 strategic), H2 2026 (P2 platform evolution)"

constraints:
  budget_sensitivity: "low"
  licensing_constraints: "none"
  compliance:
    - "none"
  data_residency: "UNKNOWN"
  auth_provider: "GitHub OAuth ($0) - all users are developers with GitHub accounts"
  hosting_preference: "GitHub Pages (frontend) + Railway (backend) - maximize GitHub Pro value"
  offline_required: "no"
  seo_required: "no"
  mobile_priority: "responsive-web"

team_and_ops:
  languages:
    typescript: "strong"
    csharp_dotnet: "none"
    python: "expert"
  preferred_frameworks:
    - "FastAPI 0.115.x (Python backend)"
    - "React 19 + Vite (frontend)"
    - "TanStack Query (data fetching)"
    - "shadcn/ui + Radix (components)"
    - "TailwindCSS (styling)"
    - "Playwright (E2E testing)"
    - "Pester (PowerShell testing)"
  repo_style: "mono"
  ci_cd: "GitHub Actions"
  release_strategy: "trunk"
  environments:
    - "development"
    - "production"
  observability_required: "advanced"

frontend_requirements:
  routing_style: "spa"
  state_management_needs:
    server_state: "high"
    client_state: "high"
  ui_system:
    design_system_needed: "yes"
    component_library_preference: "shadcn"
    theming: "both"
  accessibility:
    target_level: "WCAG-AA"
  internationalization:
    required: "no"
    locales: ["en-US"]
  performance:
    initial_load_priority: "medium"
    perceived_speed_priority: "high"
  responsiveness:
    required: "responsive"

data_and_integration:
  backend_control: "we_own"
  api_style: "REST"
  realtime: "polling"
  file_uploads: "none"
  search:
    needed: "basic"
  caching:
    needed: "standard"

quality_and_testing:
  e2e_testing_required: "yes"
  unit_testing_required: "yes"
  visual_regression_required: "yes"
  a11y_automation_required: "yes"
  evidence_pack_required: "yes"

security:
  threat_level: "medium"
  roles_and_permissions: "moderate"
  audit_logging: "yes"
  secrets_management: "server"

decision_weights:
  unification: 0.25
  developer_velocity: 0.20
  maintainability: 0.20
  performance: 0.10
  accessibility: 0.10
  testing_maturity: 0.10
  hosting_fit: 0.05

unknowns:
  - "Specific cloud provider preference not finalized (Azure vs AWS vs GCP)"
  - "Budget sensitivity for infrastructure not documented"
  - "Data residency requirements not specified"
  - "Staging environment not actively configured (dev → prod only)"
  - "Auth0 vs Keycloak final decision pending"
  - "WebSocket mentioned in README but not implemented - future realtime strategy unclear"
  - "Redis container available but unused - caching strategy TBD"

notes:
  contradictions:
    - "WebSocket endpoint mentioned in README (ws://localhost:8000/ws) but no implementation exists"
    - "Redis container running in Docker Compose but not integrated into API"
  assumptions:
    - "Auth0 will be used for MVP based on recommendation in security docs"
    - "Cloud-agnostic deployment targeting Docker/Kubernetes"
    - "No regulatory compliance required (SOC2/HIPAA/PCI) based on internal tool nature"
    - "TypeScript skill rated 'strong' based on code quality, not 'expert' (no advanced patterns)"
    - "Python skill rated 'expert' based on FastAPI maturity, uv adoption, strict typing"
  risks:
    - "5 CLI fragmentation creates maintenance burden and user confusion"
    - "React 19 + @testing-library ESM compatibility issues blocking some tests"
    - "No staging environment increases production deployment risk"
    - "Frontend is pure SPA - if SEO becomes needed, significant refactor required"
    - "Auth0 dependency introduces vendor lock-in; Keycloak requires ops expertise"

stack_recommendation:
  candidates:
    - "React 19 + Vite + TanStack Query + shadcn/ui (CURRENT - continue)"
    - "Next.js 15 App Router + RSC + shadcn/ui (future SSR option)"
    - "Remix + React Router v7 (if SSR without RSC complexity preferred)"
  
  top_candidate: "React 19 + Vite + TanStack Query + shadcn/ui (CURRENT)"
  
  rationale: |
    The existing stack is well-architected with 46+ shadcn/ui components, comprehensive 
    Playwright testing, WCAG-AA accessibility, and TanStack Query for server state. 
    The team has strong TypeScript skills and expert Python skills. The current SPA 
    architecture matches requirements (no SEO, internal tool). Switching to Next.js 
    would add complexity without clear benefit for an internal dashboard application.
    
    Focus should be on COMPLETION, not migration:
    1. Finish JWT authentication (P0-005)
    2. Complete CI/CD pipeline (P0-006)
    3. Achieve 70% branch coverage
    4. Unify 5 CLIs into 1 cf_core CLI
    
    Technology is NOT the blocker - execution velocity is.

  decision_blockers:
    - "Auth provider final selection (Auth0 vs Keycloak) - affects OAuth flow implementation"
    - "Cloud hosting target (Azure/AWS/GCP) - affects deployment pipelines"
    - "Realtime strategy (polling vs WebSocket vs SSE) - affects architecture if live updates needed"
    - "Staging environment requirement - critical for safe production deployments"
    - "Budget/licensing constraints if any (affects hosting and service choices)"
---

## Summary (human-readable)

### What we are optimizing for
- **Unification** (0.25 weight): Consolidate 5 fragmented CLIs → 1, reduce cognitive overhead
- **Developer velocity** (0.20 weight): Sub-30min onboarding, <100ms CLI operations
- **Maintainability** (0.20 weight): 80%+ test coverage, structured logging, evidence trails
- **Accessibility** (0.10 weight): WCAG-AA compliance with automated axe-core testing

### Non-negotiables
- Playwright E2E testing with evidence packs (screenshots, traces)
- WCAG-AA accessibility with automated checks
- Audit logging and structured JSONL evidence bundles (Codex requirement)
- PostgreSQL as primary database authority
- Python/FastAPI backend (expert-level team competency)

### Biggest risks
- **5 CLI fragmentation** creates user confusion and maintenance burden
- **No staging environment** increases production deployment risk
- **React 19 ESM issues** blocking some @testing-library tests
- **Auth provider undecided** (Auth0 recommended but not finalized)
- **Cloud provider undecided** creates deployment pipeline uncertainty

### Missing info that blocks stack finalization
- Cloud hosting preference (Azure vs AWS vs GCP) - affects CI/CD pipelines
- Auth provider final decision (Auth0 vs Keycloak) - affects implementation timeline
- Budget constraints (if any) - affects hosting tier and service selection
- Data residency requirements (if any) - affects cloud region selection
- Realtime strategy (if needed) - affects WebSocket vs polling architecture

---

## Research Evidence Sources

| Section | Primary Sources |
|---------|-----------------|
| Product | docs/01-Overview.md, docs/15-Future-Roadmap.md, TaskMan-v2/PRD.md |
| Constraints | docs/12-Security-Authentication.md, docs/14-Deployment-Operations.md |
| UX/Frontend | TaskMan-v2/package.json, playwright.config.ts, tailwind.config.js |
| Data/Backend | TaskMan-v2/backend-api/, docs/10-API-Reference.md |
| Team/Ops | .github/workflows/, AGENTS.md, pyproject.toml |
| Quality/Security | docs/13-Testing-Validation.md, TaskMan-v2/TESTING.md |

---

## Recommended Next Steps

1. **Finalize Auth Provider** → Auth0 for MVP (fastest path to production)
2. **Configure Staging Environment** → Add staging compose/configs before first prod deploy
3. **Set Cloud Target** → Choose primary cloud (recommendation: start with Vercel for frontend simplicity, keep backend Docker-portable)
4. **Complete P0 Blockers** → JWT auth (P0-005), CI/CD (P0-006)
5. **Achieve Coverage Gates** → 70% branch coverage before production
6. **CLI Unification** → Migrate to single `python -m cf_core.cli.main` entry point

The technology stack is already sound. **Execution, not architecture, is the critical path.**
