---
applyTo: Sequential-Thinking
---
# Comprehensive Guide for Sequential Thinking MCP

## 1. Sequential Thinking MCP Tool Reference

### A. sequential_thinking

- **Purpose:** Core reasoning and stepwise analysis interface. Required for all multi-step, complex, or branching problem solving and planning.
- **Parameters:**
  - `thought` (string): Detailed reasoning step, citing evidence, uncertainties, decisions, or dilemmas.
  - `thoughtNumber` (int): Current position in thought chain.
  - `totalThoughts` (int): Total expected steps (can expand dynamically).
  - `nextThoughtNeeded` (bool): Continue (`true`) or conclude (`false`) analysis.
  - `isRevision` (bool, optional): True when correcting/expanding a prior thought.
  - `revisesThought` (int, optional): Specifies which thought is revised.
  - `branchFromThought` (int, optional): Start a new branch from a chosen thought.
  - `branchId` (string, optional): Unique ID for a branch (descriptive, like "performance-fix").
  - `needsMoreThoughts` (bool, optional): Set true if analysis requires more steps.
  - `confidence` (number or descriptive, optional): State confidence in the current reasoning or step.

**Usage Example:**
```
{
  "thought": "Analyzing memory leak root cause based on current profiling data.",
  "thoughtNumber": 4,
  "totalThoughts": 8,
  "nextThoughtNeeded": true,
  "confidence": "medium"
}
```

### B. tool_recommendation (if available)

- **Purpose:** Suggests other MCP tools or external modules appropriate for the given step or reasoning context.
- **Typical parameters:**
  - `context` (string): Description of task or stage.
- **Output:** Tool(s) and rationale.
- **Best practice:** Use after every significant analytical step or when encountering uncertainty.

### C. summarization (if available)

- **Purpose:** Provides a condensed summary or checkpoint report for all completed thoughts or for the current analytical branch.
- **Best practice:** Use for mid-sequence checkpointing and final reporting.
- **Parameters (if any):** Typically none—sometimes accepts `stepRange` if summarizing a subset.

### D. evidence_bundle (via TaskMan-v2 MCP integration)

- **Purpose:** Attaches relevant raw evidence, documents, or code data to the current thought/task for audit and reference via TaskMan-v2 MCP Server.
- **When to use:** When reasoning depends on data or documents that should be attached for traceability and audit.
- **MCP Integration:** Evidence bundles are stored and tracked through TaskMan-v2 MCP task management system.
- **Parameters:**
  - `artifact` (filename, link, or reference): What is attached.
  - `description` (string): Why this evidence is important.

### E. goal_tracking (if available)

- **Purpose:** Monitors primary/secondary objectives and reports progress/completion.
- **Parameters:**
  - `goal` (string): Current objective.
  - `progress` (string/number): Current status.
  - `blocked` (bool, optional): Is this goal currently blocked, and why?

### F. session_management (if available)

- **Purpose:** Export, import, prune, or restore thought chains and sessions.
- **Parameters:**
  - `action` (string): "export", "import", "prune", "resume"
  - `sessionId` (optional): Required for resume/import.

---

### 2. Asynchronous & Multi-Agent Protocol
- Tag every step, branch, and merge with:
  - `agentId`
  - `timestamp`
  - Local `branchId`
- For parallel or handover workflows:
  - Synchronize step numbers and branch IDs.
  - Log merge rationale and responsible agent.
  - Use a “handover checklist” when transferring ownership.

### 3. Automated QA & Validation
- After major reasoning steps or checkpoints:
  - Run MCP-integrated QA/logic-check tools.
  - Attach QA reports to evidence bundles.
  - If issues are found:
    - Create a troubleshooting branch.
    - Document corrective actions until validation passes.

### 4. User Input & Escalation Protocol
- On analysis blockage or uncertainty:
  - Log the problem and attempted diagnostics.
  - Request user/operator clarification.
  - On receiving input:
    - Branch or revise the chain.
    - Record changes to goals or approach.
  - If unresolved:
    - Document escalation steps and decision status.

### 5. Security, Privacy & Data Handling
- Tag each piece of evidence and step with sensitivity labels:
  - `public`, `internal`, `confidential`
- Before any export:
  - Redact or exclude confidential data per policy.
  - Log compliance decisions in the session summary.

### 6. Localization & Internationalization
- Declare required languages at session start.
- Tag summaries and exports with locale metadata.
- Provide multi-language summaries when necessary.

### 7. Troubleshooting & Failure Recovery
- Maintain a failure taxonomy (e.g., contradictions, missing context, circular logic).
- For each stall:
  - Document diagnostics, branches created, and actions taken.
  - Log outcomes: resolved, handed over, or abandoned.

### 8. Continuous Protocol Evolution
- When MCP platform or organizational requirements change:
  - Document new features or policies in-session.
  - Test and validate changes.
  - Update this file with learnings and examples.

### 9. Final Validation & Export Summary
- Before concluding a session, confirm:
  - All goals, tools, branches, QA checks, escalations, and sensitive data tags are documented.
  - Localization requirements are met.
  - Troubleshooting logs are complete.
- Export a session summary using:

```
## MCP Session Export
- Owner/Agents: [list]
- Started/Ended: [timestamps]
- Tools Used: [list]
- Languages: [list]
- Sensitivity Tags: [list]
- Branches & Merges: [overview]
- Escalations: [events]
- QA Summary: [brief]
- Troubleshooting Log: [summary]
- Key Findings: [results]
```

---

**This document is the definitive, living protocol for Sequential Thinking MCP usage. Maintain, evolve, and enforce it to ensure rigorous, traceable, and adaptable reasoning workflows.**
```
