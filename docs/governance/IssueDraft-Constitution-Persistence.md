# Upstream Issue Draft: Constitution Persistence & Echo Defect (STDIO Transport)

## Summary
`update_constitution` reports success but `check_constitution` returns an empty rules array under STDIO transport for versions 2.7.1 and 2.7.6 of `@pv-bhat/vibe-check-mcp` on Windows (Node.js v24.5.0). Expected behavior (per upstream code in `src/tools/constitution.ts`) is append semantics with per-session retention (FIFO cap 50, TTL ~1h) and successful echo via `check_constitution`.

## Affected Versions
- Observed: 2.7.1, 2.7.6 (global install via npx and npm)
- Platform: Windows 11, PowerShell 7, Node.js v24.5.0
- Transport: STDIO (CLI invocation) — HTTP mode not exposing tools (initialize-only; treated as N/A for echo verification)

## Environment
```
OS: Windows 11 x64
Shell: PowerShell 7.4.x
Node: v24.5.0
Package: @pv-bhat/vibe-check-mcp (2.7.1, 2.7.6)
Invocation: npx @pv-bhat/vibe-check-mcp start (STDIO)
```

## Repro (Minimal JSON-RPC STDIO Sequence)
1. Start server (stdio transport):
   ```bash
   npx -y @pv-bhat/vibe-check-mcp start
   ```
2. Client sends (IDs illustrative):
   ```json
   {"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"ReproClient","version":"1.0.0"}}}
   {"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}
   {"jsonrpc":"2.0","id":2,"method":"vibe-check-mcp.update_constitution","params":{"sessionId":"issue-repro-001","goal":"test","plan":"append rule","userPrompt":"test","taskContext":"repro","rule":"RULE_A"}}
   {"jsonrpc":"2.0","id":3,"method":"vibe-check-mcp.check_constitution","params":{"sessionId":"issue-repro-001"}}
   ```
3. Observed response for id=2: success acknowledgment (no error).
4. Observed response for id=3: `{ "result": { "rules": [] } }` (empty array) instead of `["RULE_A"]`.

### Optional Minimal Node STDIO Repro
For convenience, a tiny Node script reproduces the behavior over STDIO without the PowerShell harness.

File: `repro-vibe-check-constitution-stdio.js`

What it does:
- Spawns the server with STDIO (`npx @pv-bhat/vibe-check-mcp`)
- Sends `initialize` → `tools/list` → `tools/call(update_constitution)` → `tools/call(check_constitution)`
- Exits non‑zero if `rules` comes back empty (defect), zero otherwise

Run (PowerShell):
```
pwsh -NoProfile -Command "node './repro-vibe-check-constitution-stdio.js'"
```

Fallbacks if `npx` is not on PATH (Windows):
- Use direct module start if locally installed:
   - `npm install @pv-bhat/vibe-check-mcp@2.7.6 --save-dev`
   - Update the script to spawn: `node node_modules/@pv-bhat/vibe-check-mcp/dist/index.js start`
- Try alternate spawn targets:
   - `npx.cmd @pv-bhat/vibe-check-mcp start`
   - `cmd /c npx @pv-bhat/vibe-check-mcp start`
   - `npm.cmd exec -y @pv-bhat/vibe-check-mcp start`
- Ensure Corepack/npm is initialized: `corepack enable`

If the Node repro cannot be launched, the PowerShell harness remains sufficient to demonstrate the defect.

## Expected Behavior
- First `update_constitution` with a rule should create a per-session rule array containing that rule.
- Subsequent `check_constitution` should return the retained array.
- Additional updates should append (FIFO eviction after 50 rules).
- `reset_constitution` should clear rules; further updates repopulate.

## Actual Behavior
- `update_constitution` returns success.
- `check_constitution` returns empty `rules` array immediately after.
- Repeated updates do not change outcome; array remains empty.
- No error thrown; silent state loss.

## Behavior Matrix (Excerpt)
| Test Case | Native (STDIO) | Shim (Local) | Expected |
|-----------|----------------|--------------|----------|
| Echo (1 rule) | `rules=[]` | `rules=[RULE_A]` | `rules=[RULE_A]` |
| Merge (2 rules) | `rules=[]` | `rules=[RULE_A,RULE_B]` | Append FIFO |
| Persistence (<1h) | `rules=[]` | `rules=[RULE_A]` | Retain |
| Reset Empty | `rules=[]` | `rules=[]` | Empty |
| Session Isolation | both empty | Distinct arrays | No leakage |
| Max Rules (51) | `rules=[]` | 50 retained FIFO | 50 retained |
| HTTP Transport Echo | N/A (initialize-only; tools not exposed) | (n/a) | `rules=[RULE_A]` |

Full matrix: `logs/Constitution-Behavior-Matrix.md`

## HTTP Mode Clarification
Attempts using `npx @pv-bhat/vibe-check-mcp start --http --port <PORT>` showed:
- Server logs "HTTP listening" and handles repeated `initialize` requests.
- External JSON-RPC calls to candidate endpoints (`/rpc`, `/jsonrpc`, `/mcp`, root) for `tools/list` / `tools/call` returned 404 or produced only initialize responses.
- Concluded standalone HTTP mode is not a workaround for constitution echo; marked Not Applicable.
Evidence: `logs/Phase2-6b-Constitution-HTTP-Echo.md`.

## Hypotheses
1. In-memory session store not updated by `update_constitution` path (write discarded before read).
2. Separate namespace used for update vs check (key mismatch or serialization bug).
3. Session scoping regression: `sessionId` param ignored when persisting rules.
4. Race or immediate reset triggered by post-update code path.
5. CLI STDIO framing issue causing truncated payload parsing (tool returns success before commit).

## Suggested Diagnostic Directions
- Trace calls inside `constitution.ts` to confirm array mutation and storage path.
- Log the internal store after each update and before each check.
- Validate parameter names for `check_constitution` vs `update_constitution` (typo or mismatch).
- Add temporary verbose flag to print session rule count after update.

## Impact
- Prevents agents from enforcing session-specific constitutional rules.
- Blocks downstream validation plans relying on multi-rule contexts.
- Forces use of shim or manual state tracking, fragmenting tests.

## Workaround
- Local shim reproduces expected semantics for testing (PowerShell module `ConstitutionShim.psm1`). Not a production solution.

## Evidence Files
- Echo: `logs/Phase2-1-Constitution-Echo-Test.md`
- Merge: `logs/Phase2-2-Constitution-Merge-Test.md`
- Persistence: `logs/Phase2-3-Constitution-Persistence-Durability.md`
- Reset: `logs/Phase2-4-Constitution-Reset-Idempotency.md`
- Isolation: `logs/Phase2-5-Constitution-Session-Isolation.md`
- Max Rules: `logs/Phase2-6a-Constitution-MaxRules-FIFO.md`
- HTTP Echo: `logs/Phase2-6b-Constitution-HTTP-Echo.md`
- Matrix: `logs/Constitution-Behavior-Matrix.md`

## Requested
- Investigate and patch persistence so `check_constitution` echoes appended rules.
- Confirm intended HTTP usage or document limitation.
- Publish minor release with fix; we will retest immediately.

## Optional: Additional Data
- Can provide raw JSON-RPC STDIO transcript on request.
- Will monitor future versions and update issue with retest results.

---
Prepared: 2025-11-10
Maintainer follow-up appreciated.
