# Tool Usage - Strategic MCP Selection

**Version**: 3.0.0 (MVP v3.0)
**Purpose**: Strategic tool selection and fallback protocols
**Status**: APPROVED

---

## Tool Priority Hierarchy

```
1. MCP Tools (highest priority)
   ├── File ops: Read, Write, Edit, Glob, Grep
   ├── GitHub: mcp__github__* (47+ operations)
   ├── Database: dbhub, mcp__db-*
   ├── TaskMan: task_*, project_*
   ├── Reasoning: SeqThinking, vibe-check-mcp
   └── Research: context7, microsoft-docs-mcp

2. VS Code Tasks (.vscode/tasks.json)
   └── Pre-configured build/test/lint operations

3. Scripts with Error Handling
   └── PowerShell/Python with structured output

4. Inline CLI (last resort)
   └── Only for simple one-off operations
```

---

## MCP Tool Selection Matrix

| Situation | Primary Tool | Fallback | Never Use |
|-----------|--------------|----------|-----------|
| Session start | constitution_check | Manual checklist | N/A |
| Complex reasoning | sequential-thinking | Manual PAOAL | Simple tasks |
| ANY failure | vibe_learn | Manual lesson capture | **NEVER SKIP** |
| Query lessons | agent-memory | Project knowledge | New work |
| File read | Read tool | cat/type | N/A |
| File write | Write tool | echo/Out-File | N/A |
| File edit | Edit tool | sed/awk | N/A |
| Search files | Glob tool | find/ls | N/A |
| Search content | Grep tool | grep/rg | N/A |
| GitHub ops | mcp__github__* | gh CLI | Never use gh when MCP available |
| Database | dbhub | psql CLI | Never use CLI when MCP available |

---

## vibe_learn Protocol (MANDATORY on Failures)

### When to Use
- ANY implementation failure
- Unexpected behavior
- Tests failing
- Quality gates failing
- Estimate significantly off

### Protocol
```bash
# 1. Call vibe_learn with complete context
vibe_learn(
  failure: "What went wrong",
  root_cause: "Why it happened",
  lesson: "Actionable takeaway"
)

# 2. Store in agent-memory (if available)
agent-memory store key="pattern/lesson" value="..."

# 3. Update PAOAL Log phase
paoal.log.lessons_learned.append(lesson)
```

### Manual Fallback (if vibe_learn unavailable)
```markdown
## FAILURE CAPTURED (Manual)

**What Failed**: [Specific error]
**Root Cause**: [Underlying problem]
**Lesson Learned**: [Actionable takeaway]
**Stored**: .github/lessons-learned/{YYYY}/{QQ}/{type}.md
```

---

## sequential-thinking Integration

### When to Use
- Complex reasoning required
- PAOAL execution (especially Plan → Observe → Adapt)
- Ambiguous requirements
- Multiple solution paths

### Usage Pattern
```python
# Plan phase
sequential_thinking(
  task="Design password reset architecture",
  approach="Explore 3 approaches, evaluate tradeoffs"
)

# Adapt phase
sequential_thinking(
  task="Resolve email latency issue",
  context="Blocking SMTP call causing 3s delay",
  explore="Async solutions: Celery vs RabbitMQ vs background threads"
)
```

---

## runSubagent Best Practices

### When to Use
- Need independent analysis (no context bias)
- Adversarial validation
- Multiple perspectives

### Usage Pattern
```python
# Independent code review
runSubagent(
  role="Security Auditor",
  task="Review authentication implementation for vulnerabilities",
  context="[minimal context, no hints about what to find]"
)
```

---

## Transport Policy (STDIO-First)

**Preference Order**:
1. STDIO transport (VS Code default)
2. HTTP only when STDIO unavailable or remote service required

**Health Checks**:
```bash
# STDIO: Ping via SDK
# HTTP: Check /health endpoint
curl http://localhost:3001/api/health
# Expected: {"status": "ok"}
```

---

## Tool Selection Decision Tree

```
Need to read file?
├─ Yes → Use Read tool (not cat/type)
└─ No ↓

Need to modify file?
├─ Yes → Use Edit tool (not sed/awk)
└─ No ↓

Need GitHub operations?
├─ Yes → Use mcp__github__* tools
└─ No ↓

Need database queries?
├─ Yes → Use dbhub MCP server
└─ No ↓

Is this build/test/lint?
├─ Yes → Use VS Code Task
└─ No ↓

Is this simple one-off command?
├─ Yes → Inline CLI acceptable
└─ No → Create script with error handling
```

---

## Acceptable Inline CLI Commands

```bash
# ✅ Acceptable
git status
git add . && git commit
npm install
uv sync
cd path && command

# ❌ Never inline (use MCP)
cat file.txt          # Use Read
grep pattern file     # Use Grep
find . -name "*.py"   # Use Glob
echo "content" > file # Use Write
sed -i 's/old/new/'   # Use Edit
```

---

**Document**: Tool Usage - Strategic MCP Selection  
**Version**: 3.0.0 (MVP v3.0)  
**Last Updated**: 2025-12-31
