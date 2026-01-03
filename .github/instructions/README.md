# Instruction Authority Index

## Purpose
- Establish a single source of truth for how ContextForge operates in chats, how MCP servers integrate, and how specialized processes execute.
- Direct every contributor to the authoritative `*.instructions.md` files that govern their scope.

## Authoritative Baseline
- `copilot-instructions.md` is the ContextForge Codex. It applies to every prompt and response, defines mandatory principles and philosophies, and links to required sub-instructions. It **always** applies.

## What Counts as Authoritative
1. Any file named `*.instructions.md` is authoritative for the scope it declares (feature, MCP server, process, etc.).
2. When both a general document and a scoped instructions file exist, the scoped `*.instructions.md` governs its domain unless it contradicts the Codex.
3. If guidance conflicts, follow the precedence rules below and open an issue/PR to resolve ambiguity.

## Precedence & Conflict Resolution
1. **Baseline:** `copilot-instructions.md` (ContextForge Codex) — cannot be contradicted.
2. **Scoped instructions:** `<topic>.instructions.md` — refine or extend within their declared scope.
3. **Specificity wins:** when two scoped instructions overlap, the file located closest to the governed code/process (or with the narrower scope statement) takes precedence.
4. **Last-updated tie-breaker:** if specificity is equal, follow the file whose `last_updated` metadata is more recent until the conflict is explicitly resolved.
5. **Escalation:** if still unclear, fall back to the Codex and log a clarification task.

## Where to Find Instructions
Primary instructions live under `.github/instructions/`.
- **Feature guidance:** `.github/instructions/<feature>.instructions.md` or co-located next to the component it governs (e.g., `src/feature-x/feature-x.instructions.md`).
- **MCP servers:** `.github/instructions/<server-name>.instructions.md` or under the server directory (e.g., `mcp-servers/<server>/README.instructions.md`).
- **Processes & workflows:** `.github/instructions/<process>.instructions.md` or inside `docs/process/` when a deep dive is needed.

When in doubt, place the instructions file beside the code or workflow entrypoint it controls and link it back here.

## Naming Convention
- Use kebab-case for the base name with the `.instructions.md` suffix (for example, `vibe-check-mcp.instructions.md`).

## Minimum Required Sections
All instructions files must include (use the template below):
- Purpose
- Scope and audience
- Use in chat prompts and responses
- Setup and prerequisites
- Steps / How it works
- Commands and expected outputs
- Deliverables and acceptance checks
- Links to specialized documentation

## Contribution Policy (Short)
- Every new feature, MCP server, or specialized process must ship with a matching `*.instructions.md` based on the template.
- Any PR that changes governed behavior must update the relevant instructions file in the same change.
- Do not duplicate Codex language; link to `copilot-instructions.md` unless you are refining within your scope.

## Quick Links
- ContextForge Codex (baseline): `./copilot-instructions.md`
- Instructions template: `./TEMPLATE.instructions.md`

## Ownership & Maintenance
- The team that owns the code/process also owns its `*.instructions.md` file.
- Include `owner` and `last_updated` metadata in the file header.
- Re-run a vibe check when creating or materially changing instructions to ensure governance alignment.
