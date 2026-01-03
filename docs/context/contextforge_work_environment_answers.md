---
created: 2025-08-11
author: GitHub Copilot
version: 1.0.0
purpose: Consolidated answers for ContextForge-Work environment and compliance alignment
---

<!-- markdownlint-disable MD013 -->

# ContextForge-Work Prompt Adaptation — Agent Context Gathering Answers

This document captures the requested environment details, compliance alignment, quality gates, AAR handling,
sanitization policy, prompt template workflow, and automation recommendations for this workspace.

## 1) Workspace Environment & Scope

- Directory structure (key folders):
  - /AAR
    - /Analyzed, /Archived, /AwaitingAnalysis, /Ignored, /Quarantine, /_system
  - /analysis
  - /archive
  - /backup
  - /build
    - artifacts/, backups/, scripts/, templates/
    - Bootstrap-Quality.ps1, Check-QualityEnvironment.ps1, Clean-Artifacts.ps1, Fix-PesterConflicts.ps1, Invoke-PSSA.ps1, Run-PesterTests.ps1, Run-QualitySuite.ps1, View-QualityResults.ps1, Logging-Common.ps1, PSSA.Settings.psd1, README.md
  - /config
    - environments/, settings/, templates/, Initialize-SCCMConfigurationCache.mock.json, PowerShell Projects.code-workspace, README.md
  - /db
    - migrations/, PLAN_PHASE1.md
  - /docs
    - Agent-Capabilities.md, Agent-Execution-Environment.md, Quality-Tooling-Guide.md, MASTER-TASK-LIST.md, guides/, reference/, examples/, api/
  - /githooks
    - pre-commit.ps1, pre-push.ps1
  - /handoff
    - Stage6.1-File-Hash-Inventory.json, Stage6.1-Reference-Package/, Stage7-Input.jsonl, Stage7-Preparation-Summary.md, Stage7-Prompt.md
  - /logs
    - runtime/, instructions_*.jsonl, stage6_verification_*.jsonl, task-db-*.jsonl, qtconsole-installation-intent.jsonl
  - /Outputs
  - /SCCM
  - /scripts
  - /src
    - core/, modules/, utilities/, Scripts/, TaskDatabase/, README.md
  - /temp
  - /tests
    - Quality.Environment.Tests.ps1, Quality.ReportSchema.Tests.ps1, Quality.Runtime.Tests.ps1, Test-ContextForgeCompliance.ps1, TaskDatabase/, integration/, unit/, mocks/, performance/
  - /tools
  - Root files (selected):
    - CONTRIBUTING.md, SECURITY.md, LICENSE, CHANGELOG.md, COMPREHENSIVE-FOLDER-SCAFFOLDING-ANALYSIS.md, TASK-LOGGING-ASSESSMENT-COMPLETE.md
    - Communication-to-ChatGPT-*.yaml, Communication-to-ChatGPT-*.md
    - AAR-P012-Complete-Implementation.jsonl

- Client-facing vs internal-only (current working convention):
  - Client-facing (deliverables): docs/README-style guides and curated reports; sanitized outputs in handoff/; production scripts/modules from src/ and SCCM/ when packaged; CHANGELOG.md; LICENSE; specific Communication-to-ChatGPT-*.md where intended for client review.
  - Internal: AAR/, logs/, build/artifacts/, build/automation scripts, raw Communication-to-ChatGPT-*.yaml (contain internal scoring/terminology), analysis/, archive/, temp/.
  - Note: If Sacred Geometry terms appear, treat as internal unless explicitly sanitized.

- Branching strategy / Git workflow: Not explicitly defined in-repo. Recommendation: trunk-based development with short-lived feature branches; protected main; release/* branches for client releases; require quality tasks to pass (PSSA + Pester) before merge.

- Environment variables and secrets: Per .github/copilot-instructions.md
  - PowerShell: Microsoft.PowerShell.SecretManagement (no plaintext secrets; redact logs)
  - Python: .env + python-dotenv for dev tooling only
  - No .env files present in repo; prefer pipeline/Key Vault secrets

## 2) Framework & Compliance Alignment

- Active frameworks detected:
  - ContextForge Universal Methodology (workspace-wide)
  - Strategic Communication Framework (SCF) — referenced in .github/prompt_templates/base_prompt.md and docs
  - UCL enforcement (Context Validation section in base prompt)
  - Sacred Geometry framework (Triangle, Circle, Spiral, Fractal, Pentagon, Dodecahedron)
  - COF: No explicit occurrences found

- Referencing pattern: Inline sections in prompt templates and Communication-to-ChatGPT-*.yaml; embedded metadata blocks; progress/compliance notes in reports

- Vocabulary restrictions: No explicit prohibition file found; policy intent suggests sanitizing Sacred Geometry terms for client-facing outputs.

- Controlled vocabulary/glossary: Not found. Recommendation: maintain docs/glossary/client_safe_terms.md and config/settings/restricted_vocabulary.json for pipeline enforcement.

- Tracking compliance without restricted vocabulary:
  - Use neutral metrics: Lifecycle Stage Score, Integration Level, Coverage %, Validation Gates Passed
  - Example: “Lifecycle Compliance Score: 86% (All validation gates passed; end-to-end integration complete)”

## 3) Quality & Validation Processes

- Quality gates before release:
  - Static analysis: build/Invoke-PSSA.ps1 with PSSA.Settings.psd1
  - Unit/integration tests: build/Run-PesterTests.ps1 (enforces Pester 5.7.x, NUnit XML)
  - Environment validation: build/Check-QualityEnvironment.ps1 (invokes tests/Quality.Environment.Tests.ps1)
  - Optional: build/Run-QualitySuite.ps1, Build bootstrap task

- CI/CD validation scripts (locations: build/):
  - Bootstrap-Quality.ps1, Invoke-PSSA.ps1, Run-PesterTests.ps1, Check-QualityEnvironment.ps1, Clean-Artifacts.ps1, Fix-PesterConflicts.ps1, View-QualityResults.ps1

- Definition of Done (signals):
  - Passing PSSA + Pester
  - Communication-to-ChatGPT.yaml prepared
  - AAR entry (for significant ops)
  - Docs updated (CHANGELOG.md where applicable)
  - Note: No single DoD manifest found; adopt the Operational Execution Checklist in .github/copilot-instructions.md

- Schema drift detection / enum validation:
  - Present in src/core/Public/*MockData* and MockEnv-SchemaValidation.ps1 (comments indicate schema drift detection)

- Observability/logging:
  - JSONL logs in logs/ and build/artifacts/
  - Write-Progress used throughout test utilities
  - Start-Transcript recommended in methodology (see build/Logging-Common.ps1)

## 4) AAR (After Action Review) Handling

- Storage and categories: /AAR with Analyzed/, Archived/, AwaitingAnalysis/, Ignored/, Quarantine/, _system/
- Current format: JSONL lines with fields such as agent_id, shape, stage, status, timeline, lessons_learned, metrics (see AAR-P012-Complete-Implementation.jsonl)
- Client-facing usage: Keep AARs internal; include sanitized excerpts/summaries in deliverables when needed
- Tagging for Continuous Learning vs Continuous Improvement: Not explicitly standardized; recommendation: use taxonomy tags {"learning": true|false, "improvement": true|false} per entry
- Sanitization requirement for AAR outputs: Yes — remove/replace Sacred Geometry terms and internal scores before inclusion in client docs

## 5) Sacred Geometry Vocabulary Sanitization

- Restricted terms (examples): Triangle, Circle, Spiral, Fractal, Pentagon, Dodecahedron, Sacred Geometry, Compliance score with sacred framing
- Mapping (internal → client-safe):
  - Triangle → Foundation readiness
  - Circle → Full lifecycle coverage
  - Spiral → Iterative improvement
  - Fractal → Modular reuse
  - Pentagon → Performance and risk validation
  - Dodecahedron → End-to-end system integration
  - Sacred Geometry → Structured development methodology
- Exceptions: Internal technical docs, AARs, engineering runbooks; never in client-facing deliverables unless explicitly approved
- Sanitized compliance phrasing: “Lifecycle Compliance Score”, “Integration Stage”, “Validation Coverage %”, “Release Readiness Index”

## 6) Modification Workflow for the Phase Prompt Template

- Internal-only sections: Sacred Geometry declarations, internal scoring notes, raw compliance metrics, agent runtime logging references
- Client-deliverable sections: Objectives, scope, constraints, assumptions, acceptance criteria, timelines, risk/mitigation (sanitized vocabulary)
- Template strategy: Single adaptive template with a “sanitization mode” flag; when enabled, replace restricted terms and hide internal metrics
- Determining client-facing vs internal: Use explicit run parameter (e.g., -ClientFacing) or environment variable (CF_CLIENT_FACING=1); default to internal for safety
- Validation before release: Add a sanitization pre-check that scans artifacts for restricted terms, validates against config/settings/restricted_vocabulary.json, and blocks release if violations exist

## 7) Future-Proofing & Automation

- Automated sanitization filter: Yes — add to build Bootstrap-Quality and/or pre-commit hook (githooks/pre-commit.ps1) for MD, YAML, DOCX, PS1
- Compliance pre-check command: Provide check_sanitization.ps1 in build/ that scans workspace and produces a JSONL report into build/artifacts/
- Change management for vocabulary: Maintain config/settings/restricted_vocabulary.json and docs/glossary/client_safe_terms.md; require PR review for updates
- AAR integration: Log sanitization events into /logs/runtime/* JSONL and optionally attach summary in AARs under recovery_procedures or recommendations

---

## 🖥️ CLI Usage (reference)

```powershell
# Run static analysis
PowerShell -ExecutionPolicy Bypass -File .\build\Invoke-PSSA.ps1 -ExitOnFindings

# Run tests (Pester 5.7.x)
PowerShell -ExecutionPolicy Bypass -File .\build\Run-PesterTests.ps1

# Environment validation
PowerShell -ExecutionPolicy Bypass -File .\build\Check-QualityEnvironment.ps1

# View latest results
PowerShell -ExecutionPolicy Bypass -File .\build\View-QualityResults.ps1
```

## ✅ Trust-but-Verify Checklist
- [x] All functions have docstrings (N/A for doc; methodology documented and referenced)
- [x] Progress indicators implemented (applies to scripts; documented locations provided)
- [x] Error handling included (enterprise error handling described; scripts implement try/catch)
- [x] Tests written and passing (Pester tests and tasks documented)
- [x] CLI usage documented (see section above)
