# Authority Mapping & Freshness Gates

## Overview
The Authority Map system inventories key platform feature surfaces (AdminService routes, WMI classes, SQL views) across multiple provenance sources (contracts, fixtures, ADRs, docs, planning, source, legacy, mocks). It produces structured artifacts under `authority/` enabling coverage, gap detection, disambiguation, and freshness gating.

## Artifacts
- `authority.map.<ts>.json` – Feature records with sources, provenance_rank, bound contracts, source metadata (hash, bytes, modified_utc).
- `coverage.<ts>.json` – Coverage rollup including stale flag per feature.
- `gaps.<ts>.json` – Arrays: `missing_contracts`, `missing_fixtures`, `stale_contracts`, plus `unresolved_conflicts`.
- `disambiguation.<ts>.json` – Initial signals list & (post-processed) false_friends via similarity.
- `disambiguation.post.<ts>.json` – Output of `Invoke-AuthorityDisambiguation.ps1` with populated `false_friends`.
- `authority.scan.log.jsonl` – Optional start/complete events.

## Freshness Gate
`tests/AuthorityFreshness.Tests.ps1` fails the suite if any `stale_contracts` entries remain, ensuring contract updates keep pace with threshold (`StaleAfterHours` in builder script).

## Disambiguation Heuristic
`Invoke-AuthorityDisambiguation.ps1` computes pairwise Levenshtein similarity on normalized feature keys (length ≥6). Pairs with similarity ≥0.78 recorded as `false_friends` for analyst review.

## Workflow
1. Run builder: `pwsh authority/Build-AuthorityMap.*.ps1 -RepoRoot .`
2. Optional: run disambiguation: `pwsh authority/Invoke-AuthorityDisambiguation.ps1 -RepoRoot .`
3. Execute tests (Gate + Authority suites) to enforce freshness & structure.
4. Integrate in CI prior to parity mock generation (Phase C).

## Next Phases
- Parity mocks scaffold under `parity/mocks` (to host synthesized mocks aligned with contracts).
- Scenario descriptors (future) will validate authority-driven paths and golden data.

## Host Policy
Modern PowerShell 7 targeted; scripts are dev helpers (non-production).
