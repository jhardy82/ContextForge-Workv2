# Decision Log (Provenance Governance)

| Date | Decision | Rationale | Impact | Reference |
|------|----------|-----------|--------|-----------|
| 2025-11-24 | Adopt Dual Export Matrix (YAML + MD) | Ensures integrity hashing + human readable summary | Protects provenance artifacts | decision-matrix.yaml |
| 2025-11-24 | Classify taskman.db & velocity_tracker.db as canonical | Persist authoritative state separately with checksum | Enables migration + manifest tracking | manifest.yaml |
| 2025-11-24 | Implement Dry-Run Retention Script | Prevent accidental deletion before validation | Safe archival workflow | Archive-AARs.ps1 |
| 2025-11-24 | GitIgnore Overrides for Evidence/AAR | Avoid broad *.jsonl exclusion of evidence bundles | Guarantees tracking of critical evidence | .gitignore |

Additional decisions appended as governance evolves.
