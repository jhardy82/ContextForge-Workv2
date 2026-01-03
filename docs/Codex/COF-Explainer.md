# Context Ontology Framework (COF) — Explainer

- generated_by: GitHub Copilot
- timestamp: 2025-08-14T00:00:00Z
- version: 1.0.0
- scope: repository
- related_schema: .github/schemas/context-object.schema.yaml

## Purpose
A quick reference to the Context Ontology Framework (COF) used by this workspace. It defines the canonical objects a task should ground itself in, and how they map to the repository’s context schema for consistent, verifiable assistance.

## COF Objects and Schema Mapping
- task: Problem framing, goals, constraints
  - schema: $.task.*
- environment: OS, shells, tools, runtime constraints
  - schema: $.environment.*
- references: Primary sources shaping decisions
  - schema: $.references[*]
- workspace: Paths, modules, tasks, scripts, structure
  - schema: $.workspace.*
- validation: Quality gates, tests, lint, evidence
  - schema: $.validation.*
- context_policy: Guardrails, sufficiency and clarity rules
  - schema: $.context_policy.*
- risks: Known risks with mitigations and severity
  - schema: $.risks[*]
- gaps: Missing info or weak coverage areas
  - schema: $.gaps[*]
- evidence_log: Artifacts, logs, proof of work
  - schema: $.evidence_log.*

See: `.github/schemas/context-object.schema.yaml` (source of truth for fields and structure).

## Usage in Prompts and Workflows
- Always ground responses in COF objects relevant to the ask.
- Prefer primary sources for “references” (UCL) and keep summaries crisp (SCF).
- When ambiguity/risk exists, expand context with additional references and validation evidence.

Minimal contract
- Inputs: task, environment, references
- Outputs: result + evidence_log pointers
- Validation: state quality gates (PSSA/Pester/logs) and outcomes

## Validation & Shape Compliance
- Triangle: Verify syntax and error handling; cite sources
- Circle: Validate integration with environment/tools/tasks
- Spiral: Add regression tests or AAR notes on deltas
- Fractal+: Reuse modules and maintain interface contracts as scope grows

## Freshness & TTL Guidance
- references: 30 days
- validation: 7 days
- environment/tools: 14 days
- risks: 14 days

Update this doc when schema or methodology evolves. Keep `Communication-to-ChatGPT-*` handoffs aligned with COF.

## Quick Example (#file injection)
- #file:.github/schemas/context-object.schema.yaml | Source schema for COF fields
- #file:docs/COF-Explainer.md | COF mapping and execution guidance

## Changelog
- 1.0.0 (2025-08-14): Initial creation to close COF explainer gap.
