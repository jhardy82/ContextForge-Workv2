---
applyTo: "codexer*, python research*, context7 research*"
description: "Advanced Python research assistant with Context 7 MCP integration"
---

# Codexer Quick Reference

## Context7 MCP Tools
- `resolve-library-id` — Resolve library names to Context7 IDs
- `get-library-docs` — Fetch documentation for library IDs

## Python Standards

### Environment
- **Always** use `venv` or `conda` — no exceptions
- Pin versions in `requirements.txt` or `pyproject.toml`

### Code Quality
- PEP 8: 79 chars, 4-space indent, `snake_case`
- Functions do ONE thing, <50 lines each
- Type hints mandatory (`typing` module)
- Specific exceptions (`ValueError`, `TypeError`), not generic `Exception`

### Structure
```
project/
├── src/           # Source code
├── tests/         # Test files
├── utils/         # Utilities
└── pyproject.toml # Dependencies
```

### Research Workflow
1. Use `resolve-library-id` to find library
2. Use `get-library-docs` for current API
3. Validate patterns against official docs
4. Test before recommending

## Full Reference
See `.github/instructions/archive/codexer-full.md`
