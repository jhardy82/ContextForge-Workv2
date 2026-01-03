# QSE Compliance & Session Commands - Quick Reference

## Compliance Commands

### compliance-check
Record a compliance check against a quality gate.

**Syntax**:
```bash
cf-core qse compliance-check <GATE_ID> --checklist <NAME> --item <DESCRIPTION> [OPTIONS]
```

**Required**:
- `GATE_ID`: Quality gate identifier (e.g., GATE-001)
- `--checklist, -c`: Checklist name
- `--item, -i`: Checklist item description

**Optional**:
- `--status, -s`: Status (pending/passed/failed/skipped) [default: pending]
- `--evidence, -e`: Evidence ID to link

**Examples**:
```bash
# Basic compliance check
cf-core qse compliance-check GATE-001 \
  --checklist=Sprint3 \
  --item="Code coverage >= 80%"

# Check with passed status and evidence
cf-core qse compliance-check GATE-001 \
  -c Sprint3 \
  -i "All tests pass" \
  -s passed \
  -e EVD-1234567890

# Failed compliance check
cf-core qse compliance-check GATE-002 \
  -c Sprint3 \
  -i "Performance < 1000ms" \
  -s failed
```

**Output**:
```
╭─ ✓ Compliance Check Recorded ──────────╮
│ Checklist ID: CHK-1234567890           │
│ Checklist: Sprint3                      │
│ Item: Code coverage >= 80%              │
│ Gate: GATE-001                          │
│ Status: pending                         │
│ Evidence: None                          │
╰────────────────────────────────────────╯
```

---

### compliance-status
Show compliance status with Rich Table formatting.

**Syntax**:
```bash
cf-core qse compliance-status [OPTIONS]
```

**Optional**:
- `--checklist, -c`: Filter by checklist name
- `--gate, -g`: Filter by gate ID
- `--score`: Calculate and show compliance score

**Examples**:
```bash
# View all compliance items
cf-core qse compliance-status

# Filter by checklist with score
cf-core qse compliance-status --checklist=Sprint3 --score

# Filter by gate
cf-core qse compliance-status --gate=GATE-001
```

**Output**:
```
                    Compliance Status
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Checklist┃ Item             ┃ Gate   ┃ Status ┃ Evidence┃ Checked At     ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ Sprint3  │ Coverage >= 80%  │ GATE-001│ passed │ EVD-001 │ 2025-11-17 10:30│
│ Sprint3  │ Perf < 1000ms    │ GATE-002│ pending│ N/A     │ N/A            │
└──────────┴──────────────────┴────────┴────────┴─────────┴────────────────┘

╭─ Score for Sprint3 ─────────────╮
│ Compliance Score: 50.00%        │
│ Score = (passed + skipped) /    │
│         total * 100             │
╰─────────────────────────────────╯
```

---

## Session Commands

### session-create
Create a new QSE session for organizing evidence collection.

**Syntax**:
```bash
cf-core qse session-create <NAME> [OPTIONS]
```

**Required**:
- `NAME`: Session name (e.g., sprint3-day1)

**Optional**:
- `--tasks, -t`: Comma-separated task IDs
- `--description, -d`: Session description
- `--sprint, -s`: Sprint ID to link

**Examples**:
```bash
# Simple session
cf-core qse session-create sprint3-day1

# Session with tasks
cf-core qse session-create sprint3-day1 \
  --tasks=T-011,T-012,T-013

# Full session with all options
cf-core qse session-create sprint3-day1 \
  -t T-011,T-012 \
  -d "Sprint 3 core plugins implementation" \
  -s S-SPRINT3
```

**Output**:
```
╭─ ✓ Session Created ────────────────────────────╮
│ Session ID: SES-20251117-1234567890            │
│ Session Name: sprint3-day1                      │
│ Directory: .QSE/v2/Sessions/2025-11-17/         │
│ Description: Sprint 3 core plugins impl         │
│ Tasks: T-011, T-012                             │
│ Sprint: S-SPRINT3                               │
╰─────────────────────────────────────────────────╯
```

---

### session-show
Display comprehensive session details and metrics.

**Syntax**:
```bash
cf-core qse session-show <SESSION_ID>
```

**Required**:
- `SESSION_ID`: Session identifier (e.g., SES-20251117-1234567890)

**Examples**:
```bash
# Show session details
cf-core qse session-show SES-20251117-1234567890
```

**Output (Active Session)**:
```
╭─ Session Details: SES-20251117-1234567890 ─────╮
│ Session Name: sprint3-day1                      │
│ Status: active                                  │
│ Start Time: 2025-11-17 09:00                    │
│ End Time: N/A                                   │
│ Evidence Count: 15                              │
│ Compliance Score: 85.50%                        │
│ Task IDs: T-011, T-012, T-013                   │
│ Sprint ID: S-SPRINT3                            │
╰─────────────────────────────────────────────────╯
```

**Output (Ended Session)**:
```
╭─ Session Details: SES-20251117-1234567890 ─────╮
│ Session Name: sprint3-day1                      │
│ Status: ended                                   │
│ Start Time: 2025-11-17 09:00                    │
│ End Time: 2025-11-17 17:00                      │
│ Duration: 8.00 hours                            │
│ Evidence Count: 42                              │
│ Compliance Score: 92.50%                        │
│ Task IDs: T-011, T-012, T-013                   │
│ Sprint ID: S-SPRINT3                            │
╰─────────────────────────────────────────────────╯
```

---

## Status Values

### Compliance Status
- `pending`: Item not yet checked
- `passed`: Item meets requirements
- `failed`: Item does not meet requirements
- `skipped`: Item intentionally skipped

### Session Status
- `active`: Session currently running
- `ended`: Session completed
- `archived`: Session archived for historical reference

---

## Color Coding

### Compliance Status
- 🟢 **Green**: passed
- 🔴 **Red**: failed
- 🟡 **Yellow**: pending
- ⚪ **White**: skipped

### Session Status
- 🟢 **Green**: active
- 🔵 **Blue**: ended
- 🟡 **Yellow**: archived

---

## Workflow Examples

### Basic Compliance Workflow
```bash
# 1. Create a quality gate
cf-core qse gate-create code-coverage --type=coverage --threshold=80

# 2. Record compliance check
cf-core qse compliance-check GATE-code-coverage \
  -c Sprint3 \
  -i "Code coverage >= 80%" \
  -s passed

# 3. View compliance status
cf-core qse compliance-status --checklist=Sprint3 --score
```

### Session-Based Evidence Collection
```bash
# 1. Create session
cf-core qse session-create sprint3-day1 \
  -t T-011,T-012 \
  -d "QSE plugin implementation"

# 2. Collect evidence (will be linked to session)
cf-core qse evidence-collect src/plugin_qse.py \
  --session=SES-20251117-1234567890 \
  --type=code

# 3. Check compliance with evidence
cf-core qse compliance-check GATE-001 \
  -c Sprint3 \
  -i "Plugin implemented" \
  -s passed \
  -e EVD-1234567890

# 4. View session summary
cf-core qse session-show SES-20251117-1234567890
```

---

## Tips

1. **Task IDs**: Use comma separation without spaces: `T-011,T-012,T-013`
2. **Session IDs**: Copy from session-create output for accuracy
3. **Evidence Linking**: Link evidence to compliance checks for traceability
4. **Compliance Score**: Use `--score` flag to see percentage metrics
5. **Filtering**: Combine filters for precise queries (e.g., `--checklist` + `--gate`)

---

## Error Handling

All commands provide clear error messages:

### Validation Error
```
╭─ ✗ Validation Error ───────────╮
│ Invalid status: invalidstatus  │
│ Valid values: pending, passed, │
│ failed, skipped                │
╰────────────────────────────────╯
```

### Database Error
```
╭─ ✗ Error ──────────────────────╮
│ Database error: Connection     │
│ refused                        │
╰────────────────────────────────╯
```

### Not Found
```
╭─ Session Not Found ────────────╮
│ Session not found              │
│ Session ID: SES-invalid        │
╰────────────────────────────────╯
```

---

## Database Connection

All commands connect to:
```
postgresql://contextforge:contextforge@172.25.14.122:5432/contextforge
```

Connection management is automatic with proper cleanup on success or failure.
