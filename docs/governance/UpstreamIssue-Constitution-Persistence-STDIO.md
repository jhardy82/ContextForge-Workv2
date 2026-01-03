# Constitution Persistence & Echo Defect — STDIO Transport

Package: `@pv-bhat/vibe-check-mcp`  |  Versions observed: 2.7.1, 2.7.6  |  Platform: Windows 11, PowerShell 7, Node.js v24.5.0

## Summary
`update_constitution` acknowledges success, but a subsequent `check_constitution` immediately returns an empty `rules` array over STDIO. Expected behavior (append semantics, per-session retention, FIFO cap 50, TTL ~1h) is that the rule is echoed back.

This was reproduced consistently across 2.7.1 and 2.7.6. A local shim that implements the expected semantics passes all tests, isolating the problem to the native STDIO implementation path.

## Expected vs Actual
| Aspect | Expected | Actual (STDIO) |
|--------|----------|----------------|
| First update + check | `rules` contains the appended rule (`["RULE_A"]`) | `rules=[]` |
| Subsequent appends | Ordered append with FIFO drop once >50 | Still `rules=[]` after each check |
| Session isolation | Distinct arrays per `sessionId` | Always empty (no leakage, but no persistence) |
| Reset after rules exist | Empties list, subsequent update repopulates | Always empty so reset is a no-op |
| TTL (<1h) | Rules retained | No retention (empty immediately) |

## Environment
- OS: Windows 11 x64
- Shell: PowerShell 7.4.x
- Node: v24.5.0
- Package: `@pv-bhat/vibe-check-mcp@2.7.1, @2.7.6`
- Transport: STDIO (CLI start)

## Minimal JSON‑RPC STDIO Repro
Start server (STDIO transport):
```
npx -y @pv-bhat/vibe-check-mcp start
```
Send JSON‑RPC (IDs illustrative):
```
{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"ReproClient","version":"1.0.0"}}}
{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}
{"jsonrpc":"2.0","id":2,"method":"vibe-check-mcp.update_constitution","params":{"sessionId":"issue-repro-001","goal":"test","plan":"append rule","userPrompt":"test","taskContext":"repro","rule":"RULE_A"}}
{"jsonrpc":"2.0","id":3,"method":"vibe-check-mcp.check_constitution","params":{"sessionId":"issue-repro-001"}}
```
Observed:
- Response id=2: success
- Response id=3: `{ "result": { "rules": [] } }` (expected `{"rules":["RULE_A"]}`)

## Behavior Matrix (Excerpt)
| Test Case | Native (STDIO) | Shim (Local) | Expected |
|---|---|---|---|
| Echo (1 rule) | `rules=[]` | `rules=[RULE_A]` | `rules=[RULE_A]` |
| Merge (2 rules) | `rules=[]` | `rules=[RULE_A,RULE_B]` | Append FIFO |
| Persistence (<1h) | `rules=[]` | `rules=[RULE_A]` | Retain |
| Reset Empty | `rules=[]` | `rules=[]` | Empty |
| Session Isolation | both empty | Distinct arrays | No leakage |
| Max Rules (51) | `rules=[]` | 50 retained FIFO | 50 retained |

Shim reproduces expected semantics; native STDIO path does not echo any rules.

## HTTP Mode Clarification
Starting with `--http` shows an HTTP listener and accepts repeated `initialize` calls, but we could not discover an external `tools/list` or `tools/call` endpoint (404 responses or initialize-only behavior). Treated HTTP as Not Applicable for echo validation.

## Hypotheses
1. In-memory session store not updated on STDIO update path.
2. Key/namespace mismatch between update vs check.
3. `sessionId` ignored or sanitized before storage.
4. Race/cleanup between update and check causing reset.
5. STDIO framing acknowledges success prematurely without persisting state.

## Impact
- Prevents agents from persisting session rules (breaks governance flows).
- Blocks tests relying on multi-rule constitution state.
- Forces shim usage and undermines parity.

## Requested
- Investigate STDIO persistence path so `check_constitution` echoes rules.
- Clarify HTTP support for tools or document limitation.
- Publish patch release; we will retest immediately.

## Retest Plan (Post-Fix Validation)
1. Echo: Single `update_constitution` then `check_constitution` → expect returned list with rule.
2. Merge: Add second distinct rule → expect both in insertion order.
3. Max / FIFO: Insert 51 unique rules → expect last 50 (drop earliest) preserved.
4. Isolation: Use two `sessionId` values; verify independent rule sets.
5. Reset: After population, call `reset_constitution` (if provided) or clear workflow then update; expect empty then fresh list.
6. Persistence: Wait several minutes (< TTL) and re-check; expect unchanged rule list.
7. Regression: Run JSON-RPC sequence in this issue; ensure parity with shim removed.

## Optional Node STDIO Repro
Script (`repro-vibe-check-constitution-stdio.js`) spawns server, sends initialize → tools/list → update → check, exits non‑zero if rules are empty.

Windows fallbacks if `npx` isn’t on PATH:
- Local install + direct module path:
  - `npm install @pv-bhat/vibe-check-mcp@2.7.6 --save-dev`
  - spawn: `node node_modules/@pv-bhat/vibe-check-mcp/dist/index.js start`
- Alternate spawns:
  - `npx.cmd @pv-bhat/vibe-check-mcp start`
  - `cmd /c npx @pv-bhat/vibe-check-mcp start`
  - `npm.cmd exec -y @pv-bhat/vibe-check-mcp start`
- Enable corepack if needed: `corepack enable`

Defect already validated via STDIO JSON‑RPC + shim; Node repro is optional.

## Evidence (available)
- JSON‑RPC transcripts (update→check empty)
- Shim parity suite: echo, merge, persistence, reset, isolation, max rules
- Detailed matrix & HTTP probe logs

Prepared: 2025‑11‑10
