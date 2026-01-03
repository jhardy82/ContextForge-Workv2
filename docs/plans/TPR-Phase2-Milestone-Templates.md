# TPR Phase 2 Milestone Documentation Templates

**Active Project**: P-TPR - Testing Platform Refactor Phase 2
**Phase**: Reliability Expansion & Optimization | **Session**: 2025-11-25
**Purpose**: Acceptance gates, evidence bundles, and AAR templates for M1/M2/M3
**Authority**: plan-tprPhase2ReliabilityExpansionOptimization.prompt.md

---

## 1. Milestone Acceptance Gate Checklists

### M1: Foundation Hardening (Weeks 1-3)
**Theme**: Eliminate blockers, rationalize infrastructure, establish baseline observability

#### Pass/Fail Criteria

| Criterion | Target | Status | Evidence Required |
|-----------|--------|--------|-------------------|
| **Collection Error Rate** | 0% (down from 35.7%) | ⬜ PASS ⬜ FAIL | `pytest-collection.log` + error count = 0 |
| **Flake Rate** | <5% over 100-run sample | ⬜ PASS ⬜ FAIL | `flake-tracker.db` query result + `flake-rate-M1.json` |
| **Active Markers** | <50 (from 283) | ⬜ PASS ⬜ FAIL | `pytest.ini` marker count + `marker-audit-M1.md` |
| **Mutation Baseline** | Report generated for 5 modules | ⬜ PASS ⬜ FAIL | `mutmut-baseline-report.html` + module list |
| **Infrastructure Status** | FlakeTracker operational | ⬜ PASS ⬜ FAIL | `flake-tracker-health.json` + sample query output |

#### Evidence Bundle Requirements
- ✅ `pytest-collection.log` (SHA-256 hash required)
- ✅ `flake-tracker.db` SQLite export
- ✅ `pytest.ini` with consolidated markers
- ✅ `mutmut-baseline-report.html` + JSON summary
- ✅ `M1-acceptance-gate.json` (this checklist in structured format)

#### Blocking Conditions
- Any collection error >0 → FAIL
- Flake rate ≥5% → FAIL
- Active markers ≥50 → FAIL
- Mutation baseline missing for any of 5 modules → FAIL

---

### M2: Expansion & Optimization (Weeks 4-6)
**Theme**: Expand spatial diversity, establish performance baselines, enable parallelization

#### Pass/Fail Criteria

| Criterion | Target | Status | Evidence Required |
|-----------|--------|--------|-------------------|
| **Cross-OS Pass Rate** | ≥95% (Windows/Linux/macOS) | ⬜ PASS ⬜ FAIL | `cross-os-matrix-results.json` + per-platform logs |
| **Performance Baseline** | p50/p95/p99 for 10+ tests | ⬜ PASS ⬜ FAIL | `perf.benchmark.baseline.json` + histogram |
| **Parallelization Speedup** | 3-5x measured improvement | ⬜ PASS ⬜ FAIL | `speedup-analysis.json` (before/after comparison) |
| **Flake Rate Post-Parallel** | <7% (≤2% increase from M1) | ⬜ PASS ⬜ FAIL | `flake-rate-M2.json` + delta calculation |
| **Mutation Score** | ≥60% (ulog, dbcli, cf_cli) | ⬜ PASS ⬜ FAIL | `mutmut-score-M2.json` + per-module breakdown |

#### Evidence Bundle Requirements
- ✅ `cross-os-matrix-results.json` (GitHub Actions artifact)
- ✅ `perf.benchmark.baseline.json` + pytest-benchmark report
- ✅ `speedup-analysis.json` (pytest-xdist metrics)
- ✅ `flake-tracker.db` updated snapshot
- ✅ `mutmut-score-M2.json` + HTML report
- ✅ `M2-acceptance-gate.json` (this checklist in structured format)

#### Blocking Conditions
- Cross-OS pass rate <95% on any platform → FAIL
- Performance baseline incomplete (missing p95/p99 for any test) → FAIL
- Speedup <3x → FAIL
- Flake rate ≥7% or delta >2% → FAIL
- Mutation score <60% for any critical module → FAIL

---

### M3: Integration & Hardening (Weeks 7-8)
**Theme**: Consolidate gains, automate tier progression, finalize CI/CD integration

#### Pass/Fail Criteria

| Criterion | Target | Status | Evidence Required |
|-----------|--------|--------|-------------------|
| **Coverage Ladder Tiers** | 4/4 implemented (Unit/Int/Sys/Mut) | ⬜ PASS ⬜ FAIL | `coverage.ladder.v2.yaml` + tier progression log |
| **CI/CD Integration** | All gates operational | ⬜ PASS ⬜ FAIL | GitHub Actions workflow status (7 blocking + 11 advisory) |
| **Final Flake Rate** | <5% across all platforms | ⬜ PASS ⬜ FAIL | `flake-rate-M3-final.json` + 7-day trend |
| **Parallelization Stability** | No regression from M2 speedup | ⬜ PASS ⬜ FAIL | `speedup-analysis-M3.json` (M2 vs M3 comparison) |
| **Mutation Score Maintenance** | ≥60% maintained post-changes | ⬜ PASS ⬜ FAIL | `mutmut-score-M3.json` + regression report |
| **Documentation Complete** | 3 playbooks published | ⬜ PASS ⬜ FAIL | `playbooks/` directory with marker/parallel/mutation guides |

#### Evidence Bundle Requirements
- ✅ `coverage.ladder.v2.yaml` + tier tracking dashboard screenshot
- ✅ GitHub Actions workflow logs (all 18 workflows)
- ✅ `flake-rate-M3-final.json` + 7-day trend graph
- ✅ `speedup-analysis-M3.json` + stability report
- ✅ `mutmut-score-M3.json` + regression analysis
- ✅ `playbooks/` (marker-consolidation.md, parallelization.md, mutation-testing.md)
- ✅ `Phase2-AAR.yaml` (see Section 3)
- ✅ `M3-acceptance-gate.json` (this checklist in structured format)

#### Blocking Conditions
- Any coverage tier not implemented → FAIL
- Any blocking CI/CD gate failing → FAIL
- Flake rate ≥5% → FAIL
- Speedup regression >10% → FAIL
- Mutation score <60% for any critical module → FAIL
- Playbook count <3 → FAIL

---

## 2. Evidence Bundle Structure Specification

### File Naming Convention
```
M{1|2|3}-completion.tar.gz
Phase2-AAR.yaml
```

### M1-completion.tar.gz Structure
```
M1-completion/
├── manifest.json                      # Bundle metadata with SHA-256 hashes
├── acceptance-gate/
│   ├── M1-acceptance-gate.json        # Pass/fail checklist results
│   ├── M1-validation-summary.md       # Human-readable summary
│   └── blockers-resolved.log          # Log of resolved collection errors
├── collection-errors/
│   ├── pytest-collection.log          # Full pytest collection output
│   ├── error-analysis.json            # Structured error categorization
│   └── resolution-evidence/           # Per-error fix evidence
│       ├── error-001-fix.patch
│       └── error-015-fix.patch
├── flake-tracking/
│   ├── flake-tracker.db               # SQLite database export
│   ├── flake-rate-M1.json             # Statistical summary
│   └── flake-detection-log.jsonl      # 100-run sample results
├── marker-rationalization/
│   ├── pytest.ini                     # Updated configuration
│   ├── marker-audit-M1.md             # Before/after analysis (283 → <50)
│   └── marker-migration-script.py     # Automated consolidation script
├── mutation-baseline/
│   ├── mutmut-baseline-report.html    # Interactive mutation report
│   ├── mutmut-summary.json            # Aggregate statistics
│   └── module-reports/                # Per-module detailed reports
│       ├── ulog-mutations.json
│       ├── dbcli-mutations.json
│       └── cf_cli-mutations.json
└── logs/
    ├── session-M1.jsonl               # Unified logging baseline events
    ├── artifact-hashes.json           # SHA-256 manifest
    └── M1-timeline.json               # Milestone execution timeline
```

### M2-completion.tar.gz Structure
```
M2-completion/
├── manifest.json
├── acceptance-gate/
│   ├── M2-acceptance-gate.json
│   ├── M2-validation-summary.md
│   └── cross-platform-compatibility.md
├── cross-os-testing/
│   ├── cross-os-matrix-results.json   # GitHub Actions matrix results
│   ├── windows-test-log.txt
│   ├── linux-test-log.txt
│   ├── macos-test-log.txt
│   └── platform-isolation-patterns.md # Documented OS-specific test patterns
├── performance-benchmarking/
│   ├── perf.benchmark.baseline.json   # p50/p95/p99 for 10+ tests
│   ├── performance-histogram.png      # Visual distribution
│   ├── pytest-benchmark-report.html   # Interactive benchmark report
│   └── regression-thresholds.yaml     # CI/CD performance gates
├── parallelization/
│   ├── speedup-analysis.json          # Before/after comparison (3-5x target)
│   ├── pytest-xdist-metrics.log       # Worker distribution stats
│   ├── race-condition-mitigations.md  # Database fixture isolation patterns
│   └── parallel-config.yaml           # pytest-xdist configuration
├── mutation-scoring/
│   ├── mutmut-score-M2.json           # ≥60% for ulog, dbcli, cf_cli
│   ├── mutmut-report-M2.html          # Full mutation report
│   └── module-coverage/
│       ├── ulog-60.2%.json
│       ├── dbcli-62.5%.json
│       └── cf_cli-61.8%.json
├── flake-tracking/
│   ├── flake-rate-M2.json             # <7% target (≤2% increase)
│   ├── flake-tracker-delta.json       # M1 → M2 comparison
│   └── flake-quarantine-list.md       # Tests moved to quarantine
└── logs/
    ├── session-M2.jsonl
    ├── artifact-hashes.json
    └── M2-timeline.json
```

### M3-completion.tar.gz Structure
```
M3-completion/
├── manifest.json
├── acceptance-gate/
│   ├── M3-acceptance-gate.json
│   ├── M3-validation-summary.md
│   └── phase2-completion-certificate.md
├── coverage-ladder/
│   ├── coverage.ladder.v2.yaml        # 4-tier tracking (Unit/Int/Sys/Mut)
│   ├── tier-progression-dashboard.png # Visual dashboard screenshot
│   ├── automated-tracking-log.json    # Tier advancement history
│   └── ladder-advancement-rules.yaml  # Tier promotion criteria
├── cicd-integration/
│   ├── github-actions-status.json     # 18 workflows (7 blocking + 11 advisory)
│   ├── workflow-logs/                 # Individual workflow execution logs
│   │   ├── mutation-advisory.log
│   │   ├── performance-blocking.log
│   │   └── cross-os-blocking.log
│   └── gate-configuration.yaml        # CI/CD gate thresholds
├── flake-stability/
│   ├── flake-rate-M3-final.json       # <5% final target
│   ├── 7-day-trend.json               # Stability validation
│   ├── flake-trend-graph.png          # Visual trend analysis
│   └── zero-regression-report.md      # Platform-specific stability analysis
├── parallelization-stability/
│   ├── speedup-analysis-M3.json       # M2 vs M3 comparison (no regression)
│   ├── stability-metrics.json         # Variance analysis
│   └── optimization-summary.md        # Documented optimizations
├── mutation-maintenance/
│   ├── mutmut-score-M3.json           # ≥60% maintained
│   ├── regression-analysis.json       # Mutation score trend
│   └── codebase-changes-impact.md     # Impact of Phase 2 changes
├── playbooks/
│   ├── marker-consolidation.md        # Step-by-step marker rationalization guide
│   ├── parallelization.md             # pytest-xdist best practices
│   └── mutation-testing.md            # mutmut integration guide
├── Phase2-AAR.yaml                    # COF 13D retrospective (see Section 3)
└── logs/
    ├── session-M3.jsonl
    ├── artifact-hashes.json
    ├── M3-timeline.json
    └── phase2-velocity-analysis.json  # Comprehensive velocity tracking
```

### Evidence Bundle Creation Script
```powershell
# scripts/Create-EvidenceBundleM1.ps1
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('M1','M2','M3')]
    [string]$Milestone
)

$ErrorActionPreference = 'Stop'

$bundleName = "$Milestone-completion"
$tempDir = "artifacts/evidence/$bundleName"
$tarPath = "artifacts/evidence/$bundleName.tar.gz"

# Create bundle structure
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

# Copy artifacts based on milestone
switch ($Milestone) {
    'M1' {
        Copy-Item -Path "artifacts/test/pytest-collection.log" -Destination "$tempDir/collection-errors/"
        Copy-Item -Path "artifacts/flake-tracker.db" -Destination "$tempDir/flake-tracking/"
        Copy-Item -Path "pytest.ini" -Destination "$tempDir/marker-rationalization/"
        Copy-Item -Path "artifacts/mutation/mutmut-baseline-report.html" -Destination "$tempDir/mutation-baseline/"
    }
    'M2' {
        Copy-Item -Path "artifacts/test/cross-os-matrix-results.json" -Destination "$tempDir/cross-os-testing/"
        Copy-Item -Path "artifacts/benchmarks/perf.benchmark.baseline.json" -Destination "$tempDir/performance-benchmarking/"
        Copy-Item -Path "artifacts/mutation/mutmut-score-M2.json" -Destination "$tempDir/mutation-scoring/"
    }
    'M3' {
        Copy-Item -Path "coverage.ladder.v2.yaml" -Destination "$tempDir/coverage-ladder/"
        Copy-Item -Path "artifacts/cicd/github-actions-status.json" -Destination "$tempDir/cicd-integration/"
        Copy-Item -Path "playbooks/*" -Destination "$tempDir/playbooks/"
        Copy-Item -Path "Phase2-AAR.yaml" -Destination "$tempDir/"
    }
}

# Generate manifest with SHA-256 hashes
$manifest = @{
    milestone = $Milestone
    createdAt = (Get-Date -Format 'o')
    artifacts = @()
}

Get-ChildItem -Path $tempDir -Recurse -File | ForEach-Object {
    $hash = (Get-FileHash -Path $_.FullName -Algorithm SHA256).Hash
    $manifest.artifacts += @{
        path = $_.FullName.Replace("$tempDir\", "")
        size = $_.Length
        hash = $hash
    }
}

$manifest | ConvertTo-Json -Depth 10 | Out-File -Encoding utf8 "$tempDir/manifest.json"

# Create tar.gz bundle
tar -czf $tarPath -C (Split-Path $tempDir) (Split-Path $tempDir -Leaf)

# Output bundle info
Write-Host "✅ Evidence bundle created: $tarPath" -ForegroundColor Green
Write-Host "📦 Bundle hash: $((Get-FileHash -Path $tarPath -Algorithm SHA256).Hash)"
Write-Host "📊 Artifact count: $($manifest.artifacts.Count)"
```

---

## 3. AAR Template (COF 13D)

```yaml
---
$schema: "https://contextforge/schemas/aar-v1"
workId: "W-TPR-PHASE2-M{1|2|3}"
createdAt: "YYYY-MM-DDTHH:MM:SSZ"
contextRef:
  id: "TPR-PHASE2-{MILESTONE}-{YYYYMMDD}-{HHMM}"
  version: "v2.0.0"
  hash: "sha256:{COMPUTED_HASH}"
correlationId: "TPR-PHASE2-{MILESTONE}-{YYYYMMDD}-{HHMM}"
sessionId: "TPR-PHASE2-{YYYYMMDD}-{HHMM}-001"
hash: "sha256:{AAR_ARTIFACT_HASH}"
---

# AAR: TPR Phase 2 - Milestone {1|2|3} Retrospective

## Executive Summary

**Status**: {COMPLETE | PARTIAL | BLOCKED}
**Milestone Theme**: {Foundation Hardening | Expansion & Optimization | Integration & Hardening}
**Completion Date**: YYYY-MM-DD
**Duration**: {N} weeks (actual vs {M} weeks planned)
**Overall Success Rate**: {XX.X}% (target: ≥95%)

### Key Metrics Summary
- **Acceptance Gate**: {PASS | FAIL} ({X}/{Y} criteria met)
- **Evidence Bundle**: {COMPLETE | INCOMPLETE} (SHA-256: {hash})
- **Blocker Resolution**: {X}/{Y} resolved ({Z} deferred to {next milestone/phase})
- **Velocity**: {X} story points ({Y}% of planned capacity)

---

## COF 13-Dimensional Analysis

### 1. Motivational Context
**Purpose & Driving Forces**

- **Business Driver**: {Reliability improvement | Performance optimization | CI/CD maturity}
- **Stakeholder Goals**: {Reduce flake rate | Enable parallelization | Cross-platform parity}
- **Value Delivered**: {Quantified impact - e.g., "50% reduction in test execution time"}

**Reflection Questions**:
- Did this milestone advance the Phase 2 mission (Operational Excellence)?
- Which objectives contributed most to reliability/performance gains?
- Were any motivational shifts required mid-milestone?

---

### 2. Relational Context
**Dependencies & Cross-Links**

- **Upstream Dependencies**: {M1 blockers | Phase 1 carryover items}
- **Downstream Impact**: {M2/M3 prerequisites | Phase 3 enablers}
- **Cross-Project Links**: {TaskMan-v2 | CF_CLI | MCP integration}

**Reflection Questions**:
- How did M{N-1} outcomes enable this milestone?
- What context was inherited vs newly created?
- Which deliverables are prerequisites for M{N+1}?

---

### 3. Situational Context
**Environmental Conditions & Constraints**

- **Technical Environment**: {Windows/Linux/macOS | Python 3.12 | pytest 8.4}
- **Resource Constraints**: {2 developers, 40 hours/week | Limited macOS CI runners}
- **External Factors**: {Library deprecations | GitHub Actions quota | Platform-specific flakiness}

**Reflection Questions**:
- What environmental factors shaped execution strategy?
- Were any constraints lifted or tightened during execution?
- How did cross-OS differences impact outcomes?

---

### 4. Resource Context
**Time, Skill, Tools**

- **Time Allocation**: {Planned: X weeks | Actual: Y weeks | Variance: ±Z%}
- **Skill Utilization**: {pytest expertise | Mutation testing learning curve | Performance profiling}
- **Tool Adoption**: {mutmut (new) | pytest-xdist (familiar) | FlakeTracker (custom)}

**Reflection Questions**:
- Was allocated time sufficient for objectives?
- Which skills proved critical vs underutilized?
- Did tool choices meet expectations (quality, usability, maintenance)?

---

### 5. Narrative Context
**Communication & Storytelling**

- **Milestone Story**: "{One-sentence summary for stakeholders}"
- **Key Messages**: {What was achieved | What remains | Risks mitigated}
- **Audience**: {Engineering team | Product leadership | External auditors}

**Reflection Questions**:
- How was progress communicated (daily standups, milestone demos, AAR)?
- Were any narrative pivots required (scope changes, blocker escalations)?
- What story does the evidence bundle tell about quality?

---

### 6. Recursive Context
**Feedback Cycles & Iteration**

- **Iteration Pattern**: {Test → Fix → Validate | Build → Benchmark → Optimize}
- **Feedback Loops**: {Flake detection → Quarantine → Re-stabilization}
- **Learning Cycles**: {Dry-runs: X | Test cycles: Y | SME refinements: Z}

**Reflection Questions**:
- How many iterations were required to meet acceptance gates?
- Which feedback loops accelerated vs slowed progress?
- What patterns emerged from repeated test-fix cycles?

---

### 7. Computational Context
**Algorithms & Processing**

- **Key Algorithms**: {Mutation operator selection | Parallel test scheduling | Flake rate calculation}
- **Performance Characteristics**: {O(n) test execution | O(n²) mutation runtime}
- **Optimization Applied**: {Worker load balancing | Scoped mutation paths}

**Reflection Questions**:
- Were computational bottlenecks identified and addressed?
- How did parallelization impact runtime complexity?
- What algorithmic trade-offs were made (coverage vs speed)?

---

### 8. Emergent Context
**Unexpected Interactions & Outcomes**

- **Surprises**: {Platform-specific timing issues | Mutation score variability | Flake clustering}
- **Novel Insights**: {Marker bloat root cause | pytest-xdist race conditions}
- **Unplanned Opportunities**: {Coverage ladder automation potential}

**Reflection Questions**:
- What behaviors emerged that weren't anticipated in planning?
- Did any negative emergent properties require mitigation?
- Were positive emergent outcomes leveraged for future phases?

---

### 9. Temporal Context
**Timing, Sequencing, Deadlines**

- **Planned Timeline**: {Weeks 1-3 | M1 checkpoint YYYY-MM-DD}
- **Actual Timeline**: {Started: YYYY-MM-DD | Completed: YYYY-MM-DD | Delays: X days}
- **Critical Path**: {Collection error resolution → Marker consolidation → Mutation baseline}

**Reflection Questions**:
- Were milestone deadlines met or adjusted?
- Which tasks were parallelizable vs sequential blockers?
- How did temporal dependencies impact overall phase velocity?

---

### 10. Spatial Context
**Distribution Across Teams & Environments**

- **Team Distribution**: {Developer A: collection errors | Developer B: mutation infrastructure}
- **Environment Coverage**: {Windows (local) | Linux (CI) | macOS (GHA)}
- **Artifact Distribution**: {Code: repo | Logs: artifacts/ | Evidence: M{N}-completion.tar.gz}

**Reflection Questions**:
- How was work distributed across team members?
- Were spatial boundaries (dev/CI/prod) clearly defined?
- Did cross-environment testing reveal platform-specific issues?

---

### 11. Holistic Context
**System-Wide Integration & Synthesis**

- **Integration Points**: {pytest.ini ↔ CI/CD | FlakeTracker ↔ quarantine workflow}
- **System Health**: {Overall flake rate: X% | Cross-OS parity: Y% | Mutation score: Z%}
- **Unified View**: {Test pyramid coherence | Coverage ladder progression}

**Reflection Questions**:
- How do milestone outcomes fit into Phase 2's holistic vision?
- Were integration issues discovered between subsystems?
- Does the evidence bundle demonstrate system-wide coherence?

---

### 12. Validation Context
**Evidence That Requirements Are Met**

- **Acceptance Gate Results**: {Pass: X/Y criteria | Fail: Z criteria}
- **Evidence Artifacts**: {pytest logs | mutmut reports | benchmark JSONs}
- **Cryptographic Validation**: {SHA-256 hashes for N artifacts}

**Reflection Questions**:
- Is every acceptance criterion backed by verifiable evidence?
- Are there any unvalidated claims or assumptions?
- Does the evidence bundle meet COF/UCL transparency standards?

---

### 13. Integration Context
**How It Fits Into the Whole**

- **Phase 2 Contribution**: {Milestone 1/3 complete | 33% of Phase 2 objectives}
- **Broader Ecosystem**: {Enables TaskMan-v2 reliability | Supports CF_CLI refactoring}
- **Future Phases**: {Phase 3 prerequisites: X | Phase 4 enablers: Y}

**Reflection Questions**:
- How does this milestone advance the TPR roadmap?
- Are M{N} outputs compatible with downstream phases?
- What integration debt was incurred (to be addressed later)?

---

## Blockers & Resolutions

### Critical Blockers
| ID | Description | Impact | Resolution | Status |
|----|-------------|--------|------------|--------|
| BLK-001 | {15 collection errors} | {35.7% collection failure} | {Root cause: import cycles, fixed via...} | ✅ RESOLVED |
| BLK-002 | {Marker taxonomy ambiguity} | {283 markers, unclear usage} | {Consolidated to 42 markers via audit} | ✅ RESOLVED |

### Deferred Items
| ID | Description | Reason | Target Milestone |
|----|-------------|--------|------------------|
| DEF-001 | {Hypothesis property-based testing} | {Out of scope for Phase 2} | Phase 3 |
| DEF-002 | {pytest-bdd Gherkin integration} | {Low priority vs mutation testing} | Phase 4 |

---

## Velocity Analysis

### Story Point Tracking
- **Planned Capacity**: {X} story points
- **Actual Delivery**: {Y} story points ({Z}% of planned)
- **Variance Analysis**: {Over/under delivery reasons}

### Time Allocation
- **Development**: {A} hours ({B}% of total)
- **Testing**: {C} hours ({D}% of total)
- **Documentation**: {E} hours ({F}% of total)
- **Blocker Resolution**: {G} hours ({H}% of total)

---

## Lessons Learned

### What Worked Well ✅
1. {Systematic collection error triage (2 days per error timebox)}
2. {Automated marker migration script (reduced manual effort by 80%)}
3. {mutmut scoped runs (acceptable runtime <10min)}

### What Needs Improvement ⚠️
1. {Cross-OS flake detection required earlier platform parity}
2. {Mutation score variability not anticipated in planning}
3. {Evidence bundle automation should be earlier in workflow}

### Action Items for Next Milestone
- [ ] {Implement FlakeTracker auto-quarantine workflow}
- [ ] {Enhance mutation score tracking dashboard}
- [ ] {Create evidence bundle generation pre-commit hook}

---

## Evidence Summary

### Artifact Manifest
```json
{
  "milestone": "M{1|2|3}",
  "evidence_bundle": "M{1|2|3}-completion.tar.gz",
  "bundle_hash": "sha256:{HASH}",
  "artifact_count": {N},
  "total_size_mb": {X.Y},
  "created_at": "YYYY-MM-DDTHH:MM:SSZ",
  "acceptance_gate": "{PASS|FAIL}"
}
```

### Key Evidence Files
- ✅ `M{N}-acceptance-gate.json` (pass/fail criteria)
- ✅ `pytest-collection.log` (collection health)
- ✅ `flake-rate-M{N}.json` (stability metrics)
- ✅ `mutmut-score-M{N}.json` (mutation coverage)
- ✅ `manifest.json` (SHA-256 artifact hashes)

---

## Approval & Sign-Off

**Milestone Owner**: {Name}
**Approval Date**: YYYY-MM-DD
**Next Milestone Start**: YYYY-MM-DD (M{N+1} kickoff)

**Certification**:
- [ ] All acceptance criteria met (or deviations documented)
- [ ] Evidence bundle complete and cryptographically verified
- [ ] AAR COF 13D analysis complete
- [ ] Phase 2 velocity tracking updated
- [ ] Deferred items logged in Phase 3 backlog

---

## Metadata

**AAR Version**: 1.0
**Template Authority**: TPR-Phase2-Milestone-Templates.md
**Related Documents**:
- plan-tprPhase2ReliabilityExpansionOptimization.prompt.md
- TPR-Phase2-Technical-Research.md
- docs/13-Testing-Validation.md
- docs/03-Context-Ontology-Framework.md

**Evidence Correlation**: TPR-PHASE2-M{N}-{YYYYMMDD}-{HHMM}
```

---

## Quick Commands Reference

```powershell
# Generate M1 evidence bundle
.\scripts\Create-EvidenceBundleM1.ps1 -Milestone M1

# Generate M2 evidence bundle
.\scripts\Create-EvidenceBundleM2.ps1 -Milestone M2

# Generate M3 evidence bundle with AAR
.\scripts\Create-EvidenceBundleM3.ps1 -Milestone M3

# Validate evidence bundle integrity
.\scripts\Validate-EvidenceBundle.ps1 -BundlePath "artifacts/evidence/M1-completion.tar.gz"

# Generate AAR from template
.\scripts\Generate-AAR.ps1 -Milestone M1 -Template "TPR-Phase2-Milestone-Templates.md"

# Query FlakeTracker for milestone metrics
python cf_cli.py flake-tracker query --milestone M1 --format json

# Generate mutation score dashboard
mutmut html --directory artifacts/mutation/M2-report/

# Cross-OS matrix status
gh run list --workflow=cross-os-matrix.yml --limit 5 --json conclusion,name
```

---

## References

- **Authority**: plan-tprPhase2ReliabilityExpansionOptimization.prompt.md
- **COF 13D Framework**: docs/03-Context-Ontology-Framework.md
- **QSE Standards**: docs/13-Testing-Validation.md
- **Evidence Baseline**: .github/instructions/logging.instructions.md
- **Quality Gates**: docs/09-Development-Guidelines.md (Section 4.2)

**Template Version**: 1.0
**Last Updated**: 2025-11-25
**Next Review**: Phase 2 M3 Completion
