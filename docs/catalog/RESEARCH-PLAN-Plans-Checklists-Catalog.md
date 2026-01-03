# Research Plan: Plans & Checklists Catalog

**Author**: Internal Research Agent
**Date**: 2025-12-06
**Version**: 1.0
**Status**: READY FOR EXECUTION

---

## Executive Summary

This research plan provides a comprehensive strategy for cataloging all plans and checklists in the ContextForge workspace. Based on reconnaissance findings of ~800+ related files, this plan defines clear scope boundaries, prioritization criteria, data extraction schemas, agent specialization, and output formats.

### Key Findings from Reconnaissance

| Category | Estimated Count | Primary Locations |
|----------|-----------------|-------------------|
| Plans | ~52+ files | `docs/plans/`, `projects/*/`, `.github/prompts/` |
| Checklists | ~42 files | `docs/checklists/`, `.bmad/*/workflows/`, `.QSE/` |
| Roadmaps | ~17+ files | `docs/roadmap/`, scattered |
| Action Lists | ~5+ files | root, `projects/` |
| Tasks | ~549 files | `trackers/tasks/` (OUT OF SCOPE) |
| Sprints | ~109 files | `trackers/sprints/` (OUT OF SCOPE) |
| AARs | ~119 files | `docs/aar/` (OUT OF SCOPE) |

---

## 1. Scope Definition

### 1.1 IN-SCOPE (Primary Focus)

#### Strategic Plans
- **Location**: `docs/plans/*.md`, `projects/*/implementation-plan.md`, `projects/*/*.plan.md`
- **Content**: Master task lists, implementation plans, migration plans, recovery protocols
- **Rationale**: These documents guide active development decisions and strategic direction

#### Checklists
- **Location**: `docs/checklists/*.md`, `.bmad/**/checklist.md`, `.QSE/checklists/`
- **Content**: Validation checklists, workflow checklists, repair checklists, process checklists
- **Rationale**: Ensures process compliance and provides verification frameworks

#### Roadmaps
- **Location**: `docs/roadmap/*.md`, `*roadmap*.md` (scattered)
- **Content**: Multi-phase strategic documents, modernization plans, implementation timelines
- **Rationale**: High-value strategic guidance for long-term planning

#### Action Lists
- **Location**: `ACTION-LIST*.md`, `NEXT-STEPS*.md`
- **Content**: Active work tracking with immediate relevance and urgency
- **Rationale**: Actionable items requiring immediate attention

### 1.2 OUT-OF-SCOPE (Excluded)

| Category | Count | Reason for Exclusion |
|----------|-------|----------------------|
| Individual Task Files | ~549 | Too granular; tracked in TaskMan-v2 database |
| Sprint Files | ~109 | Tactical execution; better queried from database |
| AARs | ~119 | Retrospective documentation, not planning |
| Agent Templates | ~40+ | Configuration files, not actionable plans |
| Prompt Templates | ~30+ | Static templates, not plans |

**Justification**: The catalog focuses on ACTIVE, STRATEGIC documents that influence current and future work priorities. Granular task/sprint data lives in TaskMan-v2 database and shouldn't be duplicated.

---

## 2. Prioritization Strategy

### 2.1 Tier Classification

#### Tier 1: CRITICAL (Analyze First)
- Files with "BLOCKING" or "CRITICAL" status indicators
- Files updated within last 30 days
- Files in `docs/plans/` root directory
- Files containing active project IDs (P-*)
- **Expected Count**: ~20-30 files
- **Priority Rationale**: Immediate impact on current work

#### Tier 2: HIGH (Analyze Second)
- Roadmap documents (`docs/roadmap/`)
- Project-specific implementation plans
- Action lists (`ACTION-LIST*.md`)
- Checklists tied to active projects
- **Expected Count**: ~40-50 files
- **Priority Rationale**: Strategic direction and compliance tracking

#### Tier 3: MEDIUM (Analyze Third)
- `.bmad` workflow checklists (process templates)
- `.QSE` plans and checklists
- Migration plans (`docs/migration/`)
- **Expected Count**: ~30-40 files
- **Priority Rationale**: Process standardization

#### Tier 4: LOW (Deferred)
- Archive directory plans
- Legacy workflow templates
- Files older than 90 days without updates
- **Expected Count**: ~20-30 files
- **Priority Rationale**: Historical reference only

### 2.2 Criticality Detection Criteria

| Criterion | Weight | Detection Method |
|-----------|--------|------------------|
| Recency | 30% | File modification date |
| Project Association | 25% | P-* ID pattern matching |
| Priority Markers | 20% | BLOCKING, CRITICAL, HIGH keywords |
| Cross-References | 15% | Count of references from other docs |
| Completion Rate | 10% | Checkbox completion percentage |

---

## 3. Data Extraction Schema

### 3.1 Core Metadata Fields

```json
{
  "file_path": "string - Absolute path to document",
  "file_name": "string - Filename without path",
  "category": "enum - Plan|Checklist|Roadmap|ActionList",
  "title": "string - Document title (H1 heading)",
  "document_version": "string - If specified in metadata",
  "created_date": "date - From metadata or Git",
  "last_modified": "date - Last modification date",
  "project_ids": "array - Associated project IDs (P-*)",
  "sprint_ids": "array - Associated sprint IDs (S-*)"
}
```

### 3.2 Status Indicators

```json
{
  "overall_status": "enum - ACTIVE|COMPLETED|BLOCKED|ARCHIVED|STALE",
  "blocking_items": "number - Count of BLOCKING items",
  "critical_items": "number - Count of CRITICAL items",
  "completion_percentage": "number - % checkboxes completed",
  "priority_level": "enum - 1-CRITICAL|2-HIGH|3-MEDIUM|4-LOW"
}
```

### 3.3 Content Analysis

```json
{
  "total_items": "number - Total actionable items",
  "completed_items": "number - [x] completed count",
  "pending_items": "number - [ ] pending count",
  "phases": "array - Identified phases",
  "current_phase": "string - Active phase"
}
```

### 3.4 Relevancy Markers

```json
{
  "dependencies": "array - Mentioned dependencies",
  "related_documents": "array - Cross-referenced docs",
  "technologies": "array - Mentioned tech stack",
  "key_stakeholders": "array - Owners/teams",
  "staleness_days": "number - Days since modification"
}
```

### 3.5 Status Detection Patterns

| Pattern | Detection Regex | Field Impact |
|---------|-----------------|--------------|
| Blocking | `⚠️\s*BLOCKING\|Status:\s*BLOCKING` | blocking_items++ |
| Completed | `✅\s*COMPLETE\|DONE\|FINISHED` | completed marker |
| Pending checkbox | `- \[ \]` | pending_items++ |
| Completed checkbox | `- \[x\]\|- \[X\]` | completed_items++ |
| Active status | `Status:\s*(ACTIVE\|IN PROGRESS)` | overall_status = ACTIVE |
| Priority | `PRIORITY\s*(\d)\|Priority:\s*(CRITICAL\|HIGH)` | priority_level |

---

## 4. Agent Specialization

### 4.1 Agent Roles

#### Agent 1: Plan Cataloger
- **Focus**: `docs/plans/*.md`, `projects/*/implementation-plan.md`
- **Responsibility**: Extract strategic plans, master task lists, migration plans
- **Output**:
  - `catalog-plans.json` - Machine-readable manifest
  - `catalog-plans-summary.md` - Human-readable summary

#### Agent 2: Checklist Cataloger
- **Focus**: `docs/checklists/*.md`, `.bmad/**/checklist.md`, `.QSE/checklists/`
- **Responsibility**: Extract workflow and validation checklists
- **Output**:
  - `catalog-checklists.json` - Machine-readable manifest
  - `catalog-checklists-summary.md` - Human-readable summary

#### Agent 3: Roadmap Cataloger
- **Focus**: `docs/roadmap/*.md`, `*roadmap*.md`
- **Responsibility**: Extract strategic roadmaps with phase tracking
- **Output**:
  - `catalog-roadmaps.json` - Machine-readable manifest
  - `catalog-roadmaps-summary.md` - Human-readable summary

#### Agent 4: Action List Cataloger
- **Focus**: `ACTION-LIST*.md`, `NEXT-STEPS*.md`
- **Responsibility**: Extract active action items with urgency indicators
- **Output**:
  - `catalog-action-lists.json` - Machine-readable manifest
  - `catalog-action-lists-summary.md` - Human-readable summary

#### Agent 5: Synthesis Agent (Orchestrator)
- **Focus**: Aggregate outputs from Agents 1-4
- **Responsibility**:
  1. Merge JSON manifests into unified catalog
  2. Calculate workspace-wide statistics
  3. Identify cross-document dependencies
  4. Produce executive summary
  5. Generate recommendations
- **Output**:
  - `PLANS-CHECKLISTS-CATALOG.md` - Final consolidated catalog
  - `catalog-unified.json` - Complete machine-readable data
  - `catalog-stats.json` - Aggregate statistics
  - `blocking-items-report.md` - Critical attention items

### 4.2 Handoff Protocol

```
┌─────────────────────────────────────────────────────────────┐
│  AGENT WORKFLOW SEQUENCE                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────┐    ┌─────────────┐                        │
│   │ Agent 1     │    │ Agent 2     │                        │
│   │ Plans       │    │ Checklists  │                        │
│   └──────┬──────┘    └──────┬──────┘                        │
│          │                  │          Parallel             │
│   ┌──────▼──────┐    ┌──────▼──────┐  Execution            │
│   │ Agent 3     │    │ Agent 4     │                        │
│   │ Roadmaps    │    │ ActionLists │                        │
│   └──────┬──────┘    └──────┬──────┘                        │
│          │                  │                               │
│          └────────┬─────────┘                               │
│                   │                                         │
│           ┌───────▼───────┐                                 │
│           │   Agent 5     │                                 │
│           │   Synthesis   │   Sequential                    │
│           └───────┬───────┘   Aggregation                   │
│                   │                                         │
│           ┌───────▼───────┐                                 │
│           │ Final Catalog │                                 │
│           └───────────────┘                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Handoff Requirements:**
1. Each agent produces JSON + Markdown outputs
2. JSON follows schema defined in Section 3
3. Synthesis agent waits for all agent outputs
4. Final output stored in `docs/catalog/`

---

## 5. Output Format

### 5.1 Catalog Table Structure

| Field | Type | Description |
|-------|------|-------------|
| ID | string | Unique catalog entry ID |
| Category | enum | Plan/Checklist/Roadmap/ActionList |
| Title | string | Document title |
| Path | string | Relative file path |
| Status | enum | ACTIVE/COMPLETED/BLOCKED/STALE |
| Priority | enum | 1-CRITICAL/2-HIGH/3-MEDIUM/4-LOW |
| Completion% | number | Percentage complete |
| Project | string | Associated project ID |
| LastModified | date | Last modification date |
| Staleness | number | Days since modification |
| BlockingCount | number | Number of blocking items |

### 5.2 Status Assessment Logic

```
IF completion_percentage >= 95%:
    status = COMPLETED
ELIF blocking_items > 0:
    status = BLOCKED
ELIF staleness_days > 60 AND completion_percentage < 95%:
    status = STALE
ELIF staleness_days <= 60 AND completion_percentage < 95%:
    status = ACTIVE
```

### 5.3 Relevancy Assessment

| Level | Criteria |
|-------|----------|
| HIGH | Active project linkage + modified <30 days + blocking items |
| MEDIUM | Active project linkage OR modified <60 days |
| LOW | No project linkage + modified >60 days |
| ARCHIVE | In archive/ directory OR explicitly marked |

### 5.4 Final Output Files

```
docs/catalog/
├── PLANS-CHECKLISTS-CATALOG.md      # Executive summary + tables
├── catalog-unified.json              # Machine-readable full data
├── catalog-stats.json                # Aggregate statistics
├── blocking-items-report.md          # Critical attention items
├── catalog-plans.json                # Plans manifest
├── catalog-plans-summary.md          # Plans summary
├── catalog-checklists.json           # Checklists manifest
├── catalog-checklists-summary.md     # Checklists summary
├── catalog-roadmaps.json             # Roadmaps manifest
├── catalog-roadmaps-summary.md       # Roadmaps summary
├── catalog-action-lists.json         # Action lists manifest
└── catalog-action-lists-summary.md   # Action lists summary
```

---

## 6. Recommendations Engine

### 6.1 Auto-Generated Recommendations

The synthesis agent shall generate recommendations for:

1. **Stale Documents** (staleness_days > 60)
   - Action: Review for relevancy or archive
   - Output: List in blocking-items-report.md

2. **Blocked Items** (blocking_items > 0)
   - Action: Escalate for resolution
   - Output: Prioritized list with context

3. **High Completion Documents** (completion_percentage >= 90%)
   - Action: Review for archival readiness
   - Output: Candidates for closure

4. **Orphaned Plans** (no project_id linkage)
   - Action: Associate with project or archive
   - Output: Orphan report section

### 6.2 Health Score Calculation

```
Workspace Health Score =
  (ACTIVE_docs * 3 + COMPLETED_docs * 2 - BLOCKED_docs * 5 - STALE_docs * 3)
  / total_docs * 100
```

---

## 7. Execution Timeline

| Phase | Agent(s) | Duration | Deliverable |
|-------|----------|----------|-------------|
| 1 | Agents 1-4 (parallel) | 30-45 min | Individual catalogs |
| 2 | Agent 5 (synthesis) | 15-20 min | Unified catalog |
| 3 | Review & Validation | 10-15 min | Final approved catalog |

**Total Estimated Time**: 60-90 minutes

---

## 8. Success Criteria

- [ ] All in-scope files cataloged (100% coverage)
- [ ] JSON schemas validated against specification
- [ ] Completion percentages calculated accurately
- [ ] Cross-references identified and linked
- [ ] Blocking items report generated
- [ ] Executive summary produced
- [ ] Recommendations engine output validated

---

## Appendix A: Sample Catalog Entry

```json
{
  "id": "PLAN-001",
  "file_path": "docs/plans/MASTER-TASK-LIST.md",
  "file_name": "MASTER-TASK-LIST.md",
  "category": "Plan",
  "title": "Master Task List - PowerShell Projects Workspace",
  "document_version": "1.0",
  "created_date": "2025-08-11",
  "last_modified": "2025-08-11",
  "project_ids": [],
  "sprint_ids": [],
  "overall_status": "STALE",
  "blocking_items": 1,
  "critical_items": 0,
  "completion_percentage": 15,
  "priority_level": "2-HIGH",
  "total_items": 20,
  "completed_items": 3,
  "pending_items": 17,
  "phases": ["Stage 6.1", "Stage 7"],
  "current_phase": "Stage 7",
  "dependencies": [],
  "related_documents": ["CF-S07-GHCA-to-CGPT-Strategic-Excellence-Planning.md"],
  "technologies": ["PowerShell", "Git"],
  "key_stakeholders": [],
  "staleness_days": 117,
  "relevancy": "LOW"
}
```

---

## Appendix B: File Discovery Commands

```powershell
# Plans
Get-ChildItem -Path . -Recurse -Filter "*plan*.md" -File | Where-Object { $_.FullName -notmatch "\\archive\\" }

# Checklists
Get-ChildItem -Path . -Recurse -Filter "*checklist*.md" -File

# Roadmaps
Get-ChildItem -Path . -Recurse -Filter "*roadmap*.md" -File

# Action Lists
Get-ChildItem -Path . -Recurse -Filter "ACTION-LIST*.md" -File
Get-ChildItem -Path . -Recurse -Filter "NEXT-STEPS*.md" -File
```

---

**Document Status**: READY FOR EXECUTION
**Next Step**: Deploy specialized agents per Section 4
