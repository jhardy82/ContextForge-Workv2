# Working Document — WUScanSource Modernization & Orchestrator

Purpose
- Living document to guide, record, and validate implementation for the WUScanSource modernization,
  non-interactive testing, validator, and external orchestrator.
- Actively referenced during edits and runs; updated as changes land.

Scope
- PowerShell 5.1 diagnostic modernization and hardening.
- Non-interactive menu testing path and wrapper coverage.
- Evidence and outputs structure; validator behavior.
- Python-based orchestrator (dev tooling only) and integration points.
- Quality gates (PSScriptAnalyzer, Pester) and tasks wiring.

Key Artifacts (paths)
- SCCM/Get-WUScanSource.ps1
- build/Test-WUScanSourceMenu.ps1
- build/Validate-WUScanEvidence.ps1
- docs/README-Get-WUScanSource.md
- docs/sprint/Sprint-2025-08-WU-ScanSource.md
- cli/ (Python orchestrator scaffolding)

Working Contract
- Keep this doc in sync with: implemented features, assumptions, Microsoft Learn references used in code
 comments, known limitations, and next actions.
- Record deltas after each meaningful change (date + short note).

Active Requirements Checklist
- [ ] Non-interactive menu driver returns structured results and writes outputs consistently
- [ ] Wrapper supports presets and custom Actions; can invoke validator
- [ ] Validator auto-discovers latest run and tolerates schema variants
- [ ] Structured outputs: JSON, CSV, JSONL (audit), Evidence bundle
- [ ] Conflict taxonomy mapped to Microsoft Learn references in comments
- [ ] Quality gates: PSScriptAnalyzer clean, Pester smoke tests
- [ ] Orchestrator CLI (Python) with run/validate/summarize commands

Assumptions
- Primary runtime: Windows PowerShell 5.1
- No manual CM import; SCCM environment assumed when relevant
- gpresult may need elevation; treat as warn-only in validator

Decision Log
- 2025-08-13: Established this working doc and communication handoff to enable traceable, update-in-place documentation.

References (to be expanded)
- docs/README-Get-WUScanSource.md
- docs/reference/Windows-Update-ScanSource-Research-20250812.md

Next Updates Planned
- Add JSON schema notes for ScanResult.json and Evidence manifest
- Capture validator edge cases and elevation guidance
- Outline orchestrator command contracts and logging
