# Universal Context Law (UCL) — Explainer

- generated_by: GitHub Copilot
- timestamp: 2025-08-14T00:00:00Z
- version: 1.0.0
- scope: repository
- related_prompt: .github/prompt_templates/base_prompt.md (Context Validation / UCL Enforcement)

## Purpose
A quick reference for the Universal Context Law: include only the minimal,
decision-shaping context necessary; expand when sufficiency triggers occur.
This doc operationalizes UCL for this workspace and ties to the base prompt’s
Context Validation section.

## Core Rules (TL;DR)
- Sufficiency: Provide just enough authoritative context to make a correct decision.
- Priority: Prefer primary sources (schemas, policies, code under test) over secondary commentary.
- Brevity: Keep summaries crisp; avoid context bloat.
- Evidence: When decisions or claims are made, point to evidence (logs, artifacts, tests).

## When to Add More Context (Sufficiency Triggers)
- Ambiguity: Requirements unclear or conflicting.
- Risk: Security, compliance, or irreversible actions.
- Coupling: Multiple systems/files tightly linked.
- Drift: Docs and automation not aligned.
- Irreversibility: Destructive or hard-to-recover changes.

If any trigger is present, add references and validation evidence until ambiguity/risk is acceptably reduced.

## Preferred Sources (in order)
1) Schemas and policies (e.g., `.github/schemas/context-object.schema.yaml`, `.github/copilot-instructions.md`)
2) Authoritative prompts and SOPs (e.g., `.github/prompt_templates/base_prompt.md`)
3) Validated logs/artifacts (e.g., `docs/context/evidence`, AAR JSONL)
4) High-signal docs (maps, governance, checklists)

## Validation Hooks
- Always state which COF objects are used (task, environment, references, validation, evidence_log).
- Tie decisions to tests or logs when possible (Pester/PSSA, JSONL, task outputs).
- Favor smaller, fresher sources; avoid large caches unless essential.

## Freshness & TTL Guidance
- references: 30 days
- validation: 7 days
- environment/tools: 14 days
- risks: 14 days

## Usage Example (#file injection)
- #file:.github/prompt_templates/base_prompt.md | UCL enforcement mechanics
- #file:docs/UCL-Explainer.md | UCL rules and triggers

## Changelog
- 1.0.0 (2025-08-14): Initial creation to strengthen UCL clarity.
