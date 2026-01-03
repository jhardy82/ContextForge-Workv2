# Documentation Topic Index

> Cross-reference index for the ContextForge documentation library.
> Updated: 2025-11-29

---

## Topic-Based Navigation

### Testing & Quality Assurance

| Topic | Primary Directory | Related |
| --- | --- | --- |
| Test Strategy | [testing/](testing/) | [validation/](validation/) |
| Pytest Configuration | [testing/PYTEST-RICH-DASHBOARD-HARNESS.md](testing/PYTEST-RICH-DASHBOARD-HARNESS.md) | pyproject.toml |
| Quality Gates | [testing/](testing/) | [governance/](governance/) |
| Test Reports | [reports/](reports/) | artifacts/test/ |

### Database & Data

| Topic | Primary Directory | Related |
| --- | --- | --- |
| Database Design | [database/](database/) | 05-Database-Design-Implementation.md |
| DuckDB Analytics | db/velocity.duckdb | [database/](database/) |
| Migrations | [migration/](migration/) | [database/](database/) |

### MCP (Model Context Protocol)

| Topic | Primary Directory | Related |
| --- | --- | --- |
| MCP Integration | [mcp/](mcp/) | [plugins/](plugins/) |
| MCP Servers | [mcp/](mcp/) | mcp-server/, mcp-server-ts/ |
| TaskMan MCP | [mcp/](mcp/) | projects/taskman-mcp/ |

### Architecture & Design

| Topic | Primary Directory | Related |
| --- | --- | --- |
| System Architecture | [architecture/](architecture/) | 02-Architecture.md |
| ADRs (Architecture Decision Records) | [adr/](adr/) | [architecture/](architecture/) |
| Context Ontology Framework | [ontology/](ontology/) | 03-Context-Ontology-Framework.md |
| Plugin Architecture | [plugins/](plugins/) | [architecture/](architecture/) |

### Development & Implementation

| Topic | Primary Directory | Related |
| --- | --- | --- |
| Development Guidelines | [guides/](guides/) | 09-Development-Guidelines.md |
| Implementation Status | [implementation/](implementation/) | [plans/](plans/) |
| API Reference | [api/](api/), [reference/](reference/) | 10-API-Reference.md |
| CLI Tools | [guides/](guides/) | cli/ |

### Planning & Research

| Topic | Primary Directory | Related |
| --- | --- | --- |
| Project Plans | [plans/](plans/) | [roadmap/](roadmap/) |
| Research Documents | [research/](research/) | [analysis/](analysis/) |
| Roadmaps | [roadmap/](roadmap/) | 15-Future-Roadmap.md |
| Sprint Planning | [sprint/](sprint/) | [plans/](plans/) |

### Governance & Standards

| Topic | Primary Directory | Related |
| --- | --- | --- |
| Work Codex | [Codex/](Codex/) | CLAUDE.md |
| Governance Policies | [governance/](governance/) | [policy/](policy/) |
| Organizational Standards | [organizational-standards/](organizational-standards/) | [technical-standards/](technical-standards/) |
| Ways of Work | [ways-of-work/](ways-of-work/) | [Codex/](Codex/) |

### Operations & Monitoring

| Topic | Primary Directory | Related |
| --- | --- | --- |
| Monitoring | [monitoring/](monitoring/) | [telemetry/](telemetry/) |
| Performance | [performance/](performance/) | [monitoring/](monitoring/) |
| Environment Setup | [environment/](environment/) | [guides/](guides/) |
| Deployment | [guides/](guides/) | 14-Deployment-Operations.md |

### AI & Agents

| Topic | Primary Directory | Related |
| --- | --- | --- |
| AI Assistants | [ai-assistants/](ai-assistants/) | [agents/](agents/) |
| Agent Personas | [Agent-Personas/](Agent-Personas/) | [agents/](agents/) |
| DTM (Dynamic Task Manager) | [dtm/](dtm/) | dynamic-task-manager/ |
| Gamification | [gamification/](gamification/) | python/gamification/ |

### Completed Work & Reviews

| Topic | Primary Directory | Related |
| --- | --- | --- |
| Completed Deliverables | [completed/](completed/) | [reports/](reports/) |
| After Action Reviews | [aar/](aar/) | [sessions/](sessions/) |
| Session Logs | [sessions/](sessions/) | [aar/](aar/) |

---

## Directory Quick Reference

### By File Count (Top 15)

```
research/     71 files  - Research documents
completed/    45 files  - Completed work
reference/    42 files  - Technical reference
reports/      41 files  - Status reports
plans/        40 files  - Project plans
testing/      34 files  - Test documentation
guides/       26 files  - User guides
mcp/          23 files  - MCP integration
architecture/ 18 files  - System design
roadmap/      18 files  - Planning roadmaps
aar/          17 files  - After Action Reviews
context/      15 files  - Evidence & artifacts
validation/   13 files  - Validation reports
implementation/ 12 files - Implementation guides
plugins/      12 files  - Plugin docs
```

### Alphabetical Directory List

| A-C | D-G | H-M | N-R | S-Z |
| --- | --- | --- | --- | --- |
| [aar/](aar/) | [database/](database/) | [harness/](harness/) | [ontology/](ontology/) | [sessions/](sessions/) |
| [adr/](adr/) | [design/](design/) | [implementation/](implementation/) | [OpenAI-Codex/](OpenAI-Codex/) | [sprint/](sprint/) |
| [agents/](agents/) | [dtm/](dtm/) | [indexes/](indexes/) | [organizational-standards/](organizational-standards/) | [technical-standards/](technical-standards/) |
| [ai-assistants/](ai-assistants/) | [environment/](environment/) | [knowledge-management/](knowledge-management/) | [output-manager/](output-manager/) | [telemetry/](telemetry/) |
| [analysis/](analysis/) | [evidence/](evidence/) | [logging/](logging/) | [performance/](performance/) | [templates/](templates/) |
| [api/](api/) | [gamification/](gamification/) | [mcp/](mcp/) | [phase-2-2/](phase-2-2/) | [testing/](testing/) |
| [architecture/](architecture/) | [governance/](governance/) | [metrics/](metrics/) | [phase-6/](phase-6/) | [validation/](validation/) |
| [archive/](archive/) | [guides/](guides/) | [migration/](migration/) | [plans/](plans/) | [ways-of-work/](ways-of-work/) |
| [authority/](authority/) | | [monitoring/](monitoring/) | [plugins/](plugins/) | [workflows/](workflows/) |
| [automation/](automation/) | | | [policy/](policy/) | [working/](working/) |
| [bugs/](bugs/) | | | [projects/](projects/) | [workspaces/](workspaces/) |
| [checklists/](checklists/) | | | [prompts/](prompts/) | |
| [Codex/](Codex/) | | | [python/](python/) | |
| [completed/](completed/) | | | [qse/](qse/) | |
| [Concepts/](Concepts/) | | | [reference/](reference/) | |
| [constitutional/](constitutional/) | | | [remediation/](remediation/) | |
| [context/](context/) | | | [reports/](reports/) | |
| | | | [research/](research/) | |
| | | | [roadmap/](roadmap/) | |

---

## Key Documents (Top Level)

| Document | Purpose |
| --- | --- |
| [01-Overview.md](01-Overview.md) | Project overview and introduction |
| [02-Architecture.md](02-Architecture.md) | System architecture documentation |
| [03-Context-Ontology-Framework.md](03-Context-Ontology-Framework.md) | COF 13-dimension framework |
| [09-Development-Guidelines.md](09-Development-Guidelines.md) | Development best practices |
| [13-Testing-Validation.md](13-Testing-Validation.md) | Testing strategy and validation |
| [15-Future-Roadmap.md](15-Future-Roadmap.md) | Future plans and roadmap |

---

*This index is manually maintained. For automated indexes, see `orchestrator/index/`.*
