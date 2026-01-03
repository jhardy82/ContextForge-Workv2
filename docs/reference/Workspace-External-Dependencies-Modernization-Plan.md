# Workspace External Dependencies Modernization Plan (Updated 2025-08-13)

Purpose: This plan aligns the modernization of all external dependencies in the workspace with the verified development environment state as of 2025-08-13. It incorporates the outcomes from the Development Environment Context discovery and ensures all steps meet enterprise policy, quality gates, and modernization goals.

Environment Constraints:

- Primary shell: Windows PowerShell 5.1 only; pwsh not installed.
- ExecutionPolicy: Process=Bypass; CurrentUser Undefined.
- PSGallery: Trusted but with HTTP method restrictions.
- Python: 3.12.9 `.venv` with key packages.
- Node/.NET: Node 24.5.0, .NET SDK 9.0.304.
- Quality gates: Enterprise PSSA zero-findings requirement — currently failing with 4911 findings.

Modernization Phases:

1. Phase 1 — Quality Gate Compliance & Secure Foundations

   - Achieve zero PSScriptAnalyzer errors/warnings.
   - Fix schema path test and restore missing refactor tool.
   - Acquire and configure code-signing certificate.
   - Adjust ExecutionPolicy to RemoteSigned (CurrentUser) outside automation.

2. Phase 2 — Dependency Management Hardening

   - Implement offline PSGallery caching with `Find-Module/Save-Module`.
   - Maintain module cache in `tools/psgallery/`.
   - Document Python requirements and schedule dependency health checks.

3. Phase 3 — Platform Modernization Preparation

   - Plan for PowerShell 7 adoption and readiness testing.

4. Phase 4 — Optional Orchestration Expansion

   - Introduce Python orchestration after PS 7 integration.

Risks:

- Policy approval for PS 7.
- Quality gate compliance as blocking condition.
- PSGallery access restrictions.

Rollout:

- Each phase gated by passing all relevant checks.
- AAR entry at each phase conclusion.
