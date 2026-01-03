# Index Coverage Checklist

Use this checklist to track the creation or update of every workspace index that is still outstanding after the initial `README_INDEX.md` work.

- [x] `README_INDEX.md` (repo root)  
  - ✅ Created to list every `README.md` file discovered via `rg --files -g 'README.md' | sort`.
  - 🔁 Keep refreshed whenever README files move, are added, or are removed.

- [x] `AAR/INDEX.md`  
  - ✅ Lists every root-level `AAR.*` artifact with timestamps plus a directory overview.  
  - ⚠️ `AAR.QSE-CF-CLI-COMPREHENSIVE-TESTING-COMPLETE` has both `.md` and `.yaml`; keep content synchronized.

- [x] `projects/INDEX.md`  
  - ✅ Captures each `projects/` workspace with README headline and missing-doc callouts.  
  - ⚠️ Conflict logged for `taskman-mcp` existing in both prefixed and unprefixed directories.

- [x] `scripts/INDEX.md`  
  - ✅ Provides subdirectory counts plus a full list of root-level automation entry points.  
  - ⚠️ Follow up to document HostPolicy expectations per area (currently summarized in notes).

- [x] `tests/INDEX.md`  
  - ✅ Enumerates every suite with `.py`/`.ps1` counts and execution hints.  
  - ⚠️ Highlights `perf` vs `performance` and `mock` vs `mocks` duplication for consolidation review.

- [x] `out/INDEX.md`  
  - ✅ Lists every run directory with README headline placeholders plus usage tips.  
  - ⚠️ Notes naming collisions (`QA_COVERAGE_GAP_TEST*`, `TEST_FIX_*`) needing clearer differentiation.

- [x] `docs/authority/INDEX.md`  
  - ✅ Summarizes generated authority artifacts and key scripts with live links into `/authority`.  
  - ⚠️ Mixed naming patterns (`authority.map.*` vs `authority-map-*`) cataloged for follow-up standardization.
