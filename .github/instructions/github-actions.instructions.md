---
applyTo: ".github/workflows/*.yml"
description: "GitHub Actions essentials - quick reference for CI/CD workflows"
---

# GitHub Actions Quick Reference

## Workflow Structure

```yaml
name: CI Pipeline
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:  # Manual trigger

permissions:
  contents: read
  
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup
        run: echo "Build step"
```

## Key Patterns

### Caching
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

### Matrix Strategy
```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12']
    os: [ubuntu-latest, windows-latest]
```

### Secrets
```yaml
env:
  API_KEY: ${{ secrets.API_KEY }}
```

### Job Dependencies
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
```

### Artifacts
```yaml
- uses: actions/upload-artifact@v4
  with:
    name: test-results
    path: reports/
```

## Security Rules
- Never echo secrets
- Use `permissions:` to limit GITHUB_TOKEN scope
- Pin action versions: `@v4` not `@main`
- Use OIDC for cloud authentication when possible

## Full Reference
See `.github/instructions/archive/github-actions-full.md` for comprehensive guide.
