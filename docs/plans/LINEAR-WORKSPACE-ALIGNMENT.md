# Linear ↔ Workspace Project Alignment

**Created**: 2025-11-29
**Purpose**: Map Linear projects to workspace project naming conventions (P-XXX format)
**Status**: Active Alignment

---

## Alignment Strategy

1. **Workspace Naming Authority**: Workspace uses `P-XXX-YYY` naming convention
2. **Linear Updates Required**: Linear projects should be renamed to match workspace conventions
3. **New Workspace Projects**: Create folders for Linear projects that don't have workspace equivalents

---

## Alignment Matrix

| Linear Project (Current) | Linear ID | Workspace Project | Status | Action |
|--------------------------|-----------|-------------------|--------|--------|
| **Production Readiness** | `c734e3b6` | — | ❌ No match | Create `P-PRODUCTION-READINESS` |
| **Output Manager Core** | `c98eccd2` | `P-OUTPUTMANAGER-CENTRALIZATION` | ⚠️ Name mismatch | Rename Linear → `P-OUTPUTMANAGER-CENTRALIZATION` |
| **Output Manager Documentation & Examples** | `ee6c3c20` | `P-OUTPUTMANAGER-CENTRALIZATION` (subproject) | ⚠️ Subproject | Keep as-is (child of Output Manager Core) |
| **Output Manager QA & Validation** | `d9b5b59a` | `P-OUTPUTMANAGER-CENTRALIZATION` (subproject) | ⚠️ Subproject | Keep as-is |
| **Sacred Geometry Glyph Library** | `0e022a24` | `P-OUTPUTMANAGER-CENTRALIZATION` (subproject) | ⚠️ Subproject | Keep as-is |
| **Progress Visualization Suite** | `a8e77453` | `P-OUTPUTMANAGER-CENTRALIZATION` (subproject) | ⚠️ Subproject | Keep as-is |
| **Table Formatting Subsystem** | `ba7247cb` | `P-OUTPUTMANAGER-CENTRALIZATION` (subproject) | ⚠️ Subproject | Keep as-is |
| **Deterministic Serialization Engine** | `0e3ff09f` | `P-OUTPUTMANAGER-CENTRALIZATION` (subproject) | ⚠️ Subproject | Keep as-is |
| **Custom MCP Servers** | `2edbb1b5` | `P-TASKMAN-MCP` | ⚠️ Overlap | Rename Linear → `P-CUSTOM-MCP-SERVERS` |
| **CF_CORE CLI** | `16a44129` | `P-CF-CLI-ALIGNMENT` | ⚠️ Name mismatch | Rename Linear → `P-CF-CLI-ALIGNMENT` |
| **ContextForge-orch-helper** | `ff82d228` | `src/` package | ❌ No folder | Create `P-ORCH-HELPER` or rename Linear |
| **TaskMan-v2** | `b3cce660` | `P-TASKMAN-CONTAINERIZATION-002` | ⚠️ Mismatch | Rename Linear → `P-TASKMAN-V2` |
| **dynamic-task-manager** | `b72868a8` | `projects/dtm` | ✅ Aligned | Optional: Rename workspace → `P-DYNAMIC-TASK-MANAGER` |
| **Agent Definition Error Remediation** | `9e5e662e` | `P-AGENT-DEFINITION-REMEDIATION` | ✅ Aligned | Rename Linear → `P-AGENT-DEFINITION-REMEDIATION` |
| **Testing Documentation & Quality Gates** | `fd6ed976` | `P-CFWORK-DOCUMENTATION` (subproject) | ⚠️ Subproject | Rename Linear → `P-TESTING-QA-DOCUMENTATION` |
| **Custom Package Function Validation** | `fa819cbf` | — | ❌ No match | Create `P-PACKAGE-VALIDATION` |
| **MCP Integration Research & Installation** | `97e84ba5` | — | ❌ No match | Create `P-MCP-INTEGRATION` |

---

## Required Linear Project Renames

The following Linear projects should be updated to match workspace conventions:

| Current Linear Name | New Linear Name | Reason |
|---------------------|-----------------|--------|
| Output Manager Core | P-OUTPUTMANAGER-CENTRALIZATION | Match workspace |
| Custom MCP Servers | P-CUSTOM-MCP-SERVERS | Distinct from P-TASKMAN-MCP |
| CF_CORE CLI | P-CF-CLI-ALIGNMENT | Match workspace |
| TaskMan-v2 | P-TASKMAN-V2 | Clear naming |
| Agent Definition Error Remediation | P-AGENT-DEFINITION-REMEDIATION | P-format convention |
| Testing Documentation & Quality Gates | P-TESTING-QA-DOCUMENTATION | Clear naming |

---

## Required Workspace Folder Creation

| Linear Project | Workspace Folder to Create |
|----------------|---------------------------|
| Production Readiness | `projects/P-PRODUCTION-READINESS/` |
| ContextForge-orch-helper | `projects/P-ORCH-HELPER/` |
| Custom Package Function Validation | `projects/P-PACKAGE-VALIDATION/` |
| MCP Integration Research & Installation | `projects/P-MCP-INTEGRATION/` |

---

## Output Manager Subproject Structure

Linear has granular Output Manager sub-projects. Workspace keeps them unified:

```
P-OUTPUTMANAGER-CENTRALIZATION/
├── core/                  → Output Manager Core
├── docs/                  → Output Manager Documentation & Examples
├── qa/                    → Output Manager QA & Validation
├── glyphs/                → Sacred Geometry Glyph Library
├── progress/              → Progress Visualization Suite
├── tables/                → Table Formatting Subsystem
└── serialization/         → Deterministic Serialization Engine
```

---

## Cross-Reference: Workspace → Linear

| Workspace Project | Linear Project(s) |
|-------------------|-------------------|
| `P-CF-CLI-ALIGNMENT` | CF_CORE CLI |
| `P-CF-CLI-ALIGNMENT-001` | — (legacy, merge into CF_CORE CLI) |
| `P-CF-CORE-CONSOLIDATION` | — (may map to orch-helper) |
| `P-CF-SPECTRE-001` | — (PowerShell module, no Linear yet) |
| `P-CFWORK-DOCUMENTATION` | Testing Documentation & Quality Gates (partial) |
| `P-OUTPUTMANAGER-CENTRALIZATION` | Output Manager Core + 6 subprojects |
| `P-REDIS-CONTAINER-ARCH-001` | — (no Linear yet) |
| `P-TASKMAN-CONTAINERIZATION-001` | — (legacy) |
| `P-TASKMAN-CONTAINERIZATION-002` | TaskMan-v2 |
| `P-TASKMAN-MCP` | Custom MCP Servers (partial overlap) |
| `P-AGENT-DEFINITION-REMEDIATION` | Agent Definition Error Remediation |
| `QSE-SME-Development` | — (no Linear yet) |
| `dtm` | dynamic-task-manager |
| `taskman-mcp` | — (code harness, covered by P-TASKMAN-MCP) |

---

## Sacred Geometry Alignment

- **Circle (Completeness)**: All projects tracked in both systems
- **Triangle (Stability)**: Consistent naming across platforms
- **Spiral (Iteration)**: Alignment evolves as projects change
- **Fractal (Modularity)**: Subprojects roll up to parent projects

---

## Maintenance

1. **New Linear Project**: Follow `P-XXX-YYY` naming convention
2. **New Workspace Project**: Create matching Linear project
3. **Sync Cadence**: Review alignment weekly (Saturday)
4. **Evidence**: Update this document with each change

---

**Last Updated**: 2025-11-29
**Next Review**: 2025-12-06
