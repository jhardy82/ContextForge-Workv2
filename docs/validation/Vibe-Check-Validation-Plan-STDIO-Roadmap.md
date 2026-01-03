# Vibe Check STDIO Validation - Visual Roadmap

```mermaid
graph TD
    Start[Start: CLI-Managed Config ✅] --> Phase1[Phase 1: Foundation]

    Phase1 --> P1_1[1.1 Environment Validation<br/>- VS Code + Claude Code<br/>- Doctor command<br/>- Connection verification]
    Phase1 --> P1_2[1.2 Tool Discovery<br/>- Enumerate all 5 tools<br/>- Capture schemas<br/>- Document capabilities]

    P1_1 --> Phase2[Phase 2: Constitution]
    P1_2 --> Phase2

    Phase2 --> P2_1[2.1 Echo Test<br/>update → check → reset]
    Phase2 --> P2_2[2.2 Merge Test<br/>Multiple updates accumulate]
    Phase2 --> P2_3[2.3 Persistence Test<br/>Rules survive checks]
    Phase2 --> P2_4[2.4 Reset Test<br/>Complete clearing]

    P2_1 --> Phase3[Phase 3: Vibe Check Core]
    P2_2 --> Phase3
    P2_3 --> Phase3
    P2_4 --> Phase3

    Phase3 --> P3_1[3.1 Baseline<br/>goal + plan minimal]
    Phase3 --> P3_2[3.2 Enriched<br/>Full context parameters]
    Phase3 --> P3_3[3.3 Constitution Integration<br/>Rule-aware feedback]
    Phase3 --> P3_4[3.4 Strategic Cadence<br/>10-15% CPI dosage]

    P3_1 --> Phase4[Phase 4: Vibe Learn]
    P3_2 --> Phase4
    P3_3 --> Phase4
    P3_4 --> Phase4

    Phase4 --> P4_1[4.1 Category Coverage<br/>All 7 categories tested]
    Phase4 --> P4_2[4.2 Minimal Payload<br/>Required fields only]

    P4_1 --> Phase5[Phase 5: Multi-Provider]
    P4_2 --> Phase5

    Phase5 --> P5_1[5.1 Provider Tests<br/>Gemini/OpenAI/OpenRouter]

    P5_1 --> Phase6[Phase 6: Error Handling]

    Phase6 --> P6_1[6.1 Schema Validation<br/>Invalid inputs]
    Phase6 --> P6_2[6.2 Edge Cases<br/>Boundary conditions]

    P6_1 --> Phase7[Phase 7: Documentation]
    P6_2 --> Phase7

    Phase7 --> P7_1[7.1 Schema Capture<br/>Complete tool schemas]
    Phase7 --> P7_2[7.2 README Audit<br/>Drift detection]

    P7_1 --> Phase8[Phase 8: Integration]
    P7_2 --> Phase8

    Phase8 --> P8_1[8.1 Complete Workflow<br/>Multi-tool simulation]

    P8_1 --> Deliverables[Deliverables]

    Deliverables --> D1[Validation Report]
    Deliverables --> D2[Schema Documentation]
    Deliverables --> D3[Evidence Bundle]
    Deliverables --> D4[Integration Guide]

    D1 --> Complete[✅ Validation Complete]
    D2 --> Complete
    D3 --> Complete
    D4 --> Complete

    style Start fill:#90EE90
    style Phase1 fill:#87CEEB
    style Phase2 fill:#87CEEB
    style Phase3 fill:#87CEEB
    style Phase4 fill:#87CEEB
    style Phase5 fill:#FFD700
    style Phase6 fill:#87CEEB
    style Phase7 fill:#87CEEB
    style Phase8 fill:#87CEEB
    style Deliverables fill:#DDA0DD
    style Complete fill:#90EE90
```

## Execution Timeline

```mermaid
gantt
    title Vibe Check STDIO Validation Schedule
    dateFormat YYYY-MM-DD
    section Session 1
    Phase 1: Foundation           :s1p1, 2025-11-11, 30m
    Phase 2: Constitution          :s1p2, after s1p1, 1h
    section Session 2
    Phase 3: Vibe Check Core      :s2p3, 2025-11-12, 90m
    Phase 4: Vibe Learn           :s2p4, after s2p3, 45m
    section Session 3
    Phase 5: Multi-Provider       :s3p5, 2025-11-13, 30m
    Phase 6: Error Handling       :s3p6, after s3p5, 45m
    Phase 7: Documentation        :s3p7, after s3p6, 1h
    section Session 4
    Phase 8: Integration          :s4p8, 2025-11-14, 45m
    Report Generation             :s4rpt, after s4p8, 30m
```

## Test Coverage Matrix

| Phase | Tools Tested | Test Cases | Evidence Files | Est. Duration |
|-------|--------------|------------|----------------|---------------|
| 1 | All 5 tools | 2 | 2 JSONL | 30 min |
| 2 | Constitution (3) | 4 | 4 JSONL | 60 min |
| 3 | vibe_check | 4 | 4 JSONL | 90 min |
| 4 | vibe_learn | 2 | 2 JSONL | 45 min |
| 5 | vibe_check | 3 | 1 JSONL | 30 min |
| 6 | All 5 tools | 6 | 2 JSONL | 45 min |
| 7 | All 5 tools | 2 | 1 JSONL | 60 min |
| 8 | All 5 tools | 1 | 1 JSONL | 45 min |
| **Total** | **5 tools** | **24 cases** | **17 files** | **6-7 hours** |

## Constitution Framework Flow

```mermaid
sequenceDiagram
    participant Test as Test Harness
    participant MCP as Vibe Check MCP
    participant Store as Constitution Store

    Note over Test,Store: Phase 2.1: Echo Test
    Test->>MCP: update_constitution(sessionId, rule1)
    MCP->>Store: Store rule1
    Store-->>MCP: Confirmed
    MCP-->>Test: Success

    Test->>MCP: check_constitution(sessionId)
    MCP->>Store: Retrieve rules
    Store-->>MCP: [rule1]
    MCP-->>Test: {rules: [rule1]}

    Test->>MCP: reset_constitution(sessionId, [])
    MCP->>Store: Clear rules
    Store-->>MCP: Cleared
    MCP-->>Test: Success

    Test->>MCP: check_constitution(sessionId)
    MCP->>Store: Retrieve rules
    Store-->>MCP: []
    MCP-->>Test: {rules: []}

    Note over Test,Store: Phase 2.2: Merge Test
    Test->>MCP: update_constitution(sessionId, rule1)
    MCP->>Store: Add rule1
    Test->>MCP: update_constitution(sessionId, rule2)
    MCP->>Store: Add rule2 (merge)
    Test->>MCP: check_constitution(sessionId)
    MCP->>Store: Retrieve rules
    Store-->>MCP: [rule1, rule2]
    MCP-->>Test: {rules: [rule1, rule2]}
```

## CPI Strategic Cadence Pattern

```mermaid
graph LR
    P0[Phase 0<br/>Initialize] -->|MANDATORY| V1[vibe_check<br/>Checkpoint 1]
    V1 --> P1[Phase 1<br/>Scope]
    P1 --> P2[Phase 2<br/>Research]
    P2 --> P3[Phase 3<br/>Design]
    P3 -->|MANDATORY| V2[vibe_check<br/>Checkpoint 2]
    V2 --> P4[Phase 4<br/>Validate]
    P4 -.->|CONDITIONAL| V3[vibe_check<br/>Checkpoint 3?]
    V3 -.-> P5[Phase 5<br/>Sync]
    P4 --> P5
    P5 --> P6[Phase 6<br/>Execute]
    P6 -->|MANDATORY| V4[vibe_check<br/>Checkpoint 4]
    V4 --> P7[Phase 7<br/>Package]
    P7 --> P8[Phase 8<br/>Reflect]
    P8 -->|MANDATORY| V5[vibe_check<br/>Checkpoint 5]
    V5 --> Done[Complete]

    style V1 fill:#FFD700
    style V2 fill:#FFD700
    style V3 fill:#FFA500
    style V4 fill:#FFD700
    style V5 fill:#FFD700
    style P0 fill:#87CEEB
    style Done fill:#90EE90
```

**Legend:**
- 🟨 Solid: MANDATORY checkpoint (4 total)
- 🟧 Dashed: CONDITIONAL checkpoint (0-1 based on complexity)
- **Dosage:** 4-5 checkpoints / 8 phases = 10-15% ✅

## Success Metrics Dashboard

```mermaid
pie title Test Assertion Distribution
    "Constitution Tests" : 16
    "Vibe Check Tests" : 20
    "Vibe Learn Tests" : 10
    "Provider Tests" : 6
    "Error Handling Tests" : 12
    "Schema Tests" : 10
    "Integration Tests" : 6
```

**Target Success Rates:**
- ≥95% overall assertion pass rate
- 100% tool discovery success
- 100% schema capture completeness
- 100% evidence bundle generation

## Risk Heat Map

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Constitution empty return | Medium | High | Detailed capture + diagnostic |
| Provider key unavailable | Low | Low | Conditional phase |
| Connection instability | Low | Medium | Retry logic |
| Schema drift | Low | Medium | README comparison |

**Overall Risk Level:** 🟢 LOW - All risks have documented mitigations

## Evidence Bundle Structure

```
logs/vibe-check-stdio-validation-20251110/
├── 00-environment-validation.jsonl          (Phase 1.1)
├── 01-tools-enumeration.jsonl               (Phase 1.2)
├── 02-constitution-echo.jsonl               (Phase 2.1)
├── 03-constitution-merge.jsonl              (Phase 2.2)
├── 04-constitution-persistence.jsonl        (Phase 2.3)
├── 05-constitution-reset.jsonl              (Phase 2.4)
├── 06-vibe-check-baseline.jsonl             (Phase 3.1)
├── 07-vibe-check-enriched.jsonl             (Phase 3.2)
├── 08-vibe-check-constitution.jsonl         (Phase 3.3)
├── 09-vibe-check-cadence.jsonl              (Phase 3.4)
├── 10-vibe-learn-categories.jsonl           (Phase 4.1)
├── 11-vibe-learn-minimal.jsonl              (Phase 4.2)
├── 12-provider-tests.jsonl                  (Phase 5.1)
├── 13-error-handling.jsonl                  (Phase 6.1)
├── 14-edge-cases.jsonl                      (Phase 6.2)
├── 15-schema-capture.jsonl                  (Phase 7.1)
├── 16-workflow-integration.jsonl            (Phase 8.1)
├── summary.yaml                             (Final report)
└── README.md                                (Bundle documentation)
```

## Quick Start Checklist

### Prerequisites
- [x] VS Code MCP configuration (CLI-managed) ✅
- [x] Claude Code MCP configuration (CLI-managed) ✅
- [x] Node.js v24.5.0 verified ✅
- [x] Doctor command passed ✅
- [ ] Restart VS Code to load configuration
- [ ] Restart Claude Code to load configuration

### Session 1 Setup (30 minutes)
- [ ] Create `scripts/Test-VibeCheck-STDIO.ps1` harness
- [ ] Verify MCP connections in both editors
- [ ] Run Phase 1.1: Environment validation
- [ ] Run Phase 1.2: Tool discovery
- [ ] Capture baseline evidence

### Go/No-Go Decision Point
After Phase 1 completion, assess:
- ✅ All 5 tools discovered?
- ✅ Schemas documented?
- ✅ Both editors connected?
- ✅ Evidence logs generating?

**If YES to all:** Proceed to Phase 2
**If NO to any:** Troubleshoot before continuing

---

**Plan Status:** READY FOR EXECUTION
**Visual Aids:** Flowcharts, timeline, coverage matrix
**Next Action:** Review + approve → Create harness → Execute Phase 1
