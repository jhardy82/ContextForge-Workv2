---
applyTo: "**"
description: "Essential rules that apply to ALL tasks - minimal footprint"
---

# ContextForge Essential Rules

## Work Codex (7 Core Principles)
1. **Trust Nothing, Verify Everything** — Evidence closes trust loops
2. **Workspace First** — Search before creating
3. **Logs First** — Truth lives in records
4. **Leave Things Better** — Every action enriches the system
5. **Fix the Root** — Address causes, not symptoms
6. **Best Tool for Context** — Every task has its proper tool
7. **Iteration is Sacred** — Progress spirals, not straight lines

## CLI Commands
```bash
# ALWAYS use modular CLI
python -m cf_core.cli.main task list
python -m cf_core.cli.main sprint show S-001

# NEVER use deprecated
# ❌ scripts/cli/dbcli.py
# ❌ cf_cli.py directly
```

## Package Management
```bash
# ALWAYS
uv sync              # Install dependencies
uv add package       # Add new package

# NEVER
# ❌ pip install
# ❌ requirements.txt (use pyproject.toml)
```

## Git Workflow
- Commit after each logical unit of work
- Format: `type(scope): description`
- Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`
- Run `git status` before AND after changes

## Terminal Discipline
- Wait for command output before conclusions
- Verify claims with log files, not terminal memory
- One command at a time (no parallel terminal calls)

## Definition of Done
- [ ] Code runs without errors
- [ ] Tests pass: `python -m pytest`
- [ ] Linting passes: `python -m ruff check .`
- [ ] Changes committed with conventional message
- [ ] Pushed to remote branch
