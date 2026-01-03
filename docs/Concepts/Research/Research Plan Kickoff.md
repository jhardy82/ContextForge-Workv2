# Prompt 1 — Research Charter Kickoff

Begin Phase 1: Discovery & Framing.
- Inventory all existing research artifacts and tool inventories in the workspace.
- Draft `research_charter_<ts>.yaml` with scope, objectives, constraints, initial research questions, and sub-questions.
- Identify success signals and evidence criteria.
- Output YAML snippet for the charter and a JSONL kickoff log.

# Prompt 2 — Comprehensive Inventory Sweep

Conduct an inventory sweep of all available research tools and prior outputs.
- Use context7 MCP, Microsoft Docs, githubRepo, search, analyzers, and local workspace inspection.
- Catalog each into `research_catalog_<ts>.yaml` with schema fields (id, source, type, reliability, location, method, query, status, notes, timestamp).
- Rank each as primary, secondary, or tertiary.
- Output updated catalog YAML snippet and highlight gaps.

# Prompt 3 — Gap Analysis & Plan Design

Start Phase 2: Plan Design.
- Review `research_charter_<ts>.yaml` and `research_catalog_<ts>.yaml`.
- Identify catalog gaps, dependencies, and unresolved questions.
- Create `research_plan_<ts>.yaml` with:
  - Selected methods and tool usage plan
  - Evaluation metrics and validation thresholds
  - Loop exit criteria
- Output plan YAML snippet and log tool decisions.

# Prompt 4 — Tool Utilization Map

Map every research tool available into a structured tool plan.
- For each tool, log name, role, trust_score, limitations, and planned queries.
- Record results in `research_plan_<ts>.yaml` under tools[].
- Confirm prioritization of primary sources over secondary/tertiary.
- Output YAML snippet and narrative summary of coverage.

# Prompt 5 — Risk & Reliability Setup

Anticipate risks, contradictions, and reliability issues before execution.
- Add a risks[] section to `research_plan_<ts>.yaml` with risk, mitigation, fallback.
- Define evidence ranking rules: primary = high, secondary = medium, tertiary = low.
- Log this as part of plan validation.
- Output YAML snippet for risks and reliability configuration.

# Prompt 6 — Kickoff Confirmation Menu

Summarize Phase 1–2 outputs in 3 bullets:
1. Research question(s) and scope
2. Sources & perspectives
3. Success metrics

Then present continuation options:
1. Proceed to Phase 3 (Execution)
2. Revise charter
3. Add tools/sources
4. BLOCKED with rationale

Emit updated artifacts (charter + plan YAML) and kickoff log JSONL.
