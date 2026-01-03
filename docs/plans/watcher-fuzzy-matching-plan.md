# Transcript Coverage Watcher – Fuzzy / Semantic Matching Plan

Status: implemented (experimental flag)
Owner: system
Date: 2025-08-20
Shape: Triangle → Spiral (foundational algorithm then iterative tuning)

## 1. Problem Statement
Exact substring correlation between transcript command lines and UnifiedLogger events yields false negatives when:
- Minor typos ("gt-process" vs "Get-Process").
- Parameter reordering / casing differences.
- Extra or missing whitespace / punctuation.
- Aliases vs canonical cmdlet names.

Goal: Improve recall of legitimate logged actions without materially increasing false positives, under an opt‑in flag.

## 2. Matching Pipeline
For each unmatched (exact) transcript command candidate:
1. Normalize (lowercase, trim, collapse whitespace, strip trailing semicolons/pipes).
2. Tokenize into alphanum segments (drop empty) → token list.
3. Compute similarity against each event field candidate (action, target, details.command, details.raw) using:
   - Levenshtein distance similarity: `lev_sim = 1 - (distance / max(len(a), len(b)))`.
   - Token Jaccard similarity (unigrams) over token sets.
   - Optional bigram Jaccard (future: gated; not yet implemented for perf simplicity).
4. Aggregate score: `score = (lev_sim * 0.55) + (token_jaccard * 0.45)` (weights chosen empirically to balance structural & edit distance).
5. Accept if max score ≥ threshold (default 0.72) and Levenshtein similarity alone ≥ 0.60 (guardrail against token collisions).

## 3. Parameters / Flags

| Name | Type | Default | Purpose |
|------|------|---------|---------|
| EnableFuzzyMatch | switch | off | Activates fuzzy logic |
| FuzzyMinScore | double | 0.72 | Acceptance threshold |
| FuzzyMaxEventScan | int | 400 | Upper bound events scanned per cycle (recent slice) |
| FuzzyVerbose | switch | off | Emit per-candidate debug events (not default) |

## 4. Metrics & Logging
Event `transcript_fuzzy_eval` (one per scan) with fields:
`{ candidates, fuzzy_accepts, fuzzy_rejects, threshold, avg_score, max_score }`.

## 5. Performance Considerations

Worst case: C * E comparisons (commands * events). Bound E via recent window (already) + `FuzzyMaxEventScan` cap. Levenshtein implemented iterative O(n*m) but with early abandon if distance exceeds `(1-minScore)*maxLen`.

## 6. Risks / Mitigations

| Risk | Mitigation |
|------|------------|
| False positives | Dual condition (aggregate + min Levenshtein), experimental flag |
| Performance regression | Event scan cap + early distance exit |
| Threshold drift | Expose parameter; metrics for tuning |
| Overfitting to English tokens | Tokenization generic alphanum, future multilingual not blocked |

## 7. Acceptance Criteria
- Flag present and off by default.
- Gap count decreases for known near-miss transcript vs events cases.
- No change in results when flag disabled.
- Metrics event emitted with counts.

## 8. Future Enhancements (Deferred)
- Bigram / trigram token Jaccard.
- Embedding cosine similarity (requires model selection & caching).
- Alias expansion map (Get-Alias) to unify synonyms.
- Adaptive threshold (ROC-based tuning with historical labeled set).

## 9. Test Matrix

| Scenario | Expectation |
|----------|-------------|
| Typo single char | Matched via fuzzy, previously gap |
| Param case difference | Matched |
| Unrelated command | Remains gap |
| Threshold raised above score | Gap |

## 10. Rollback Plan
Disable flag (no code path executed); remove parameters & helper functions if abandoned.

---
Evidence: Integrated into `scripts/Watch-TranscriptCoverage.ps1` + `tests/TranscriptCoverage.Fuzzy.Tests.ps1`.
