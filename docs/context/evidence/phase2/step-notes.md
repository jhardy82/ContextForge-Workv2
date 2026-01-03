## 2025-08-13 — Logging PoC scaffolding

- Change: Extended build/Logging-Common.ps1 with optional Windows Event Log hook
- Added: build/Forward-LogsToAzureMonitor.ps1 (PS7 stub for Logs Ingestion API batch forwarder)
- Notes: EventLog is disabled by default; configure with Set-StructuredLoggingOptions

## 2025-08-13 — Local-only logging policy applied

- Decision: No cloud components; enforce CF_NO_CLOUD=1
- Added: config/logging.local.json (cloud_ingestion_enabled=false)
- Added: build/Initialize-LocalLogging.ps1 (applies local config, logs logging_config_applied)
- Added: build/Summarize-StructuredLogs.ps1 (aggregates JSONL evidence)
- Added: docs/context/logging/Local-Only-Logging-Decision.md (runbook/notes)
- Added: handoff/Communication-to-ChatGPT-Logging-LocalOnly-20250813.yaml (handoff summary)
- Impact: JSONL baseline remains; Windows Event Log mirroring stays optional and off by default

## 2025-08-13 — Research backlog created

- Action: Added docs/context/Research-Backlog.md with prioritized topics and deliverables
- Purpose: Provide a transparent plan for remaining research areas and expected outputs
- Note: Aligned to PS 5.1-first and repo methodology; includes citations and PoC expectations

## 2025-08-13 — Logging options catalog created

- Action: Added docs/context/logging/Logging-Options-Catalog.md
- Scope: Built-in primitives, Windows Event Log, Azure Monitor ingestion, and community modules
- Recommendation: Keep JSONL baseline; add optional Event Log hook; plan PS7 Azure Monitor bridge

## 2025-08-13 — Markdownlint policy relaxed

- Change: Increased MD013 line_length to 240; disabled heading enforcement; set strict/stern to false
- Rationale: Practical authoring for conversational handoffs and research catalogs with longer contextual lines
- Impact: Reduces noise from MD013 in curated docs while retaining core formatting rules

## 2025-08-13 — Conversational handoff (verbose) created

- Action: Added handoff/Communication-to-ChatGPT-Conversational-VERBOSE-20250813.md
- Purpose: Context-rich operating guide for ChatGPT with methodology, quality gates, runbooks
- Notes: Wrapped long lines to satisfy markdownlint MD013

## 2025-08-13 — Conversational handoff created

- Action: Added handoff/Communication-to-ChatGPT-Conversational-20250813.md
- Purpose: Self-contained conversational brief for ChatGPT with operating rules and context
- Notes: Wrapped long lines to satisfy markdownlint MD013

## 2025-08-13 — Research Catalog created

- Action: Added docs/context/Research-Catalog.md (refreshable catalog of non-Learn sources)
- Contents: Curated PowerShell Gallery modules, vendor/community docs, GitHub repos, MVP/expert blogs
- Compatibility notes: PS 5.1 baseline; PnP.PowerShell flagged as PS 7.4+ only
- Refresh cadence: Monthly and on major releases; evidence and JSONL audit to record deltas
- Rationale: Consolidate verified, authoritative sources for repeatable research-first development

# Phase 2 Step Notes (Observed 2025-08-13)

This file captures concise, structured notes for each executed objective.

Template
- What: [brief]
- Why: [brief]
- How: [commands/paths]
- Where: [artifact/log locations]
- When: [timestamp]
- Confidence: [0-100%]
- Risk: [low/medium/high]

 Entries
- [Add entries as steps are executed]
- What: Research validation of local tooling versions and cmdlets
  Why: Confirm Phase 2 assumptions (Pester 5.7.x, PSScriptAnalyzer available, PS 5.1)
  How: Queried versions and commands via PowerShell; imported modules
  Where: N/A (console output); capability summary recorded in docs/context/Tooling-MCP-Capabilities.md
  When: 2025-08-13
  Confidence: 95%
  Risk: low

- What: Added official Microsoft Learn citations for cmdlets used
   Why: Complete the internet research requirement with canonical references
   How: Collected URLs via Microsoft Learn and appended to Research Validation section
   Where: docs/context/Tooling-MCP-Capabilities.md (Research Validation)
   When: 2025-08-13
   Confidence: 95%
   Risk: low
