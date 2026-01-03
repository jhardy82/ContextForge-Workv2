# Phase 2: Architecture Summary

## Component Diagram

```mermaid
graph TB
    subgraph PowerShell["PowerShell Layer"]
        PS[Test-McpHeartbeat.ps1]
        CFO[ContextForge.Observability Module]
        PSLog[Write-CFLogEvent]
    end

    subgraph Environment["Environment Variables"]
        ENV1[CF_SESSION_ID=83e88a22]
        ENV2[CF_TRACE_ID=a1b2c3d4...]
    end

    subgraph Python["Python Layer"]
        UL[unified_logger.py]
        MCP[MCP Server / cf_cli.py]
        PyLog[logger.info/debug/error]
    end

    subgraph Storage["Storage Layer"]
        LogFile[logs/contextforge-2025-12-29.jsonl]
    end

    PS --> |Start-CFSession| CFO
    CFO --> |Sets| ENV1
    CFO --> |Sets| ENV2
    PS --> |Spawns subprocess| MCP
    ENV1 --> |Inherited by| MCP
    ENV2 --> |Inherited by| MCP
    MCP --> |Import| UL
    UL --> |Reads| ENV1
    UL --> |Reads| ENV2
    UL --> |Auto-binds context| PyLog
    PSLog --> |Appends| LogFile
    PyLog --> |Appends| LogFile

    style ENV1 fill:#90EE90
    style ENV2 fill:#90EE90
    style LogFile fill:#FFD700
    style UL fill:#87CEEB
```

## Sequence Diagram

```mermaid
sequenceDiagram
    participant PS as PowerShell Script
    participant CFO as ContextForge.Observability
    participant ENV as Environment Variables
    participant PY as Python Process
    participant UL as unified_logger
    participant LOG as Log File

    PS->>CFO: Start-CFSession
    CFO->>CFO: Generate session_id: "83e88a22"
    CFO->>CFO: Generate trace_id: "a1b2c3d4..."
    CFO->>ENV: Set CF_SESSION_ID=83e88a22
    CFO->>ENV: Set CF_TRACE_ID=a1b2c3d4...
    CFO->>LOG: Write session_start event

    PS->>PY: Spawn subprocess (inherits env)
    PY->>UL: Import unified_logger
    UL->>ENV: Read CF_SESSION_ID
    UL->>ENV: Read CF_TRACE_ID
    UL->>UL: Bind context to logger
    UL->>LOG: Write powershell_bridge_active

    PS->>LOG: Write task_start
    PY->>LOG: Write python_action (with session_id)
    PY->>LOG: Write python_result (with session_id)
    PS->>LOG: Write task_end

    PS->>CFO: Stop-CFSession
    CFO->>LOG: Write session_summary

    Note over LOG: All events share session_id="83e88a22"
```

## Data Flow Diagram

```mermaid
flowchart LR
    subgraph Input["Input: PowerShell"]
        A[Start-CFSession]
    end

    subgraph Processing["Processing: Bridge"]
        B[Generate IDs]
        C[Set Environment Variables]
        D[Spawn Python]
        E[Python Reads Env]
        F[Auto-Bind Logger]
    end

    subgraph Output["Output: Unified Logs"]
        G[contextforge-2025-12-29.jsonl]
        H[All events have session_id]
    end

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H

    style A fill:#FFB6C1
    style C fill:#90EE90
    style F fill:#87CEEB
    style H fill:#FFD700
```

## State Diagram

```mermaid
stateDiagram-v2
    [*] --> NoSession: PowerShell starts
    NoSession --> SessionActive: Start-CFSession
    SessionActive --> EnvVarsSet: Set CF_SESSION_ID, CF_TRACE_ID
    EnvVarsSet --> PythonSpawned: Spawn subprocess
    PythonSpawned --> ContextInherited: Python reads env vars
    ContextInherited --> LoggingCorrelated: Logger binds context
    LoggingCorrelated --> SessionEnded: Stop-CFSession
    SessionEnded --> [*]: Session complete

    note right of EnvVarsSet
        CF_SESSION_ID=83e88a22
        CF_TRACE_ID=a1b2c3d4...
    end note

    note right of LoggingCorrelated
        All logs share same session_id
        Full trace reconstruction possible
    end note
```

## Deployment Diagram

```mermaid
graph TB
    subgraph Workspace["ContextForge Workspace"]
        subgraph Scripts["scripts/"]
            S1[Test-McpHeartbeat.ps1]
            S2[Test-Phase2-Bridge.ps1]
        end

        subgraph Modules["modules/"]
            M1[ContextForge.Observability.psm1]
        end

        subgraph Python["python/services/"]
            P1[unified_logger.py]
        end

        subgraph MCP["TaskMan-v2/"]
            T1[mcp-server-taskman]
        end

        subgraph Logs["logs/"]
            L1[contextforge-2025-12-29.jsonl]
        end

        subgraph Docs["docs/"]
            D1[Phase2-PowerShell-Python-Bridge-Architecture.md]
            D2[ADR-005-PowerShell-Python-Bridge.md]
        end
    end

    S1 --> M1
    S2 --> M1
    M1 --> |Sets env vars| T1
    T1 --> P1
    P1 --> |Reads env vars| M1
    S1 --> L1
    S2 --> L1
    P1 --> L1

    style M1 fill:#FFB6C1
    style P1 fill:#87CEEB
    style L1 fill:#FFD700
```

---

## Key Metrics

| Metric | Value |
|--------|-------|
| **Lines of Code Changed** | ~20 (Python) + ~0 (PowerShell, already done) |
| **Files Modified** | 1 (`unified_logger.py`) |
| **Files Created** | 4 (docs, test script, ADR, quick ref) |
| **Breaking Changes** | 0 (backward compatible) |
| **Test Coverage** | End-to-end test script provided |
| **Implementation Time** | ~2 hours |
| **Complexity** | Low (environment variable pattern) |

---

## Success Criteria

- [✅] Python reads `CF_SESSION_ID` from environment
- [✅] Python reads `CF_TRACE_ID` from environment
- [✅] Logger auto-binds session context
- [✅] Logs write to unified daily file
- [✅] Bridge activation logged
- [✅] Backward compatible
- [ ] Test script passes
- [ ] Real MCP server validated
- [ ] Documentation complete

---

## Timeline

| Phase | Status | Date |
|-------|--------|------|
| **Design** | ✅ Complete | 2025-12-29 |
| **Python Implementation** | ✅ Complete | 2025-12-29 |
| **Test Script Creation** | ✅ Complete | 2025-12-29 |
| **Testing** | ⏳ In Progress | 2025-12-29 |
| **Validation** | ⏳ Pending | 2025-12-29 |
| **Production** | 🔄 Awaiting Tests | TBD |

---

*Architecture summary generated by Architect Agent*
*Last Updated: 2025-12-29*
