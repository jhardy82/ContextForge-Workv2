# Agent Prompts — Database Validation Mission
**Generated**: 2025-11-14
**Mission**: Complete remaining tasks for evidence sanitization hardening and database validation

---

## 🔐 AGENT 1: CYBERSECURITY ADVISOR (Security Lead)

### Mission Context
**Primary Responsibility**: Complete Task 1 remaining items - evidence sanitization security validation
**Success Criteria**: Zero security leaks, all linting clean, pytest passing, validation script confirms sanitization

### Applicable Instructions
Reference these instruction files from `.github/instructions/`:

1. **python.instructions.md** - Python coding standards
   - Virtual environment activation MANDATORY before any Python commands
   - PEP 8 compliance, 100-char line limit
   - Type hints and docstrings required
   - Terminal output requirements (Rich library integration)

2. **powershell.instructions.md** - PowerShell scripting standards
   - Verb-Noun naming conventions
   - Approved verbs only (Get-Verb)
   - Parameter validation and error handling
   - Security best practices (credential handling)

3. **Sequential-Thinking.instructions.md** - Problem-solving protocol
   - Use sequential_thinking MCP tool for complex analysis
   - Document reasoning steps with evidence
   - Branch analysis for alternative approaches
   - Track decisions and rationale

4. **vibe-check-mcp-integration.instructions.md** - Metacognitive oversight
   - Execute vibe_check at strategic checkpoints
   - Use vibe_learn to capture lessons from failures
   - Document risk assessment and mitigation

### Mission Objectives

#### Objective 1: Fix Linting Errors (IMMEDIATE)
**Research Subagent 1 (linting_analysis)**:
- Tool Usage: `grep_search`, `read_file`, `semantic_search`
- Deliverable: Complete list of 9 linting violations with line numbers and root causes
- Constraints: DO NOT modify files, report findings only
- Query Pattern: `grep_search` for line length violations >100 chars in evidence_sanitization.py and test_evidence_sanitization.py
- Expected Output: Structured data with:
  ```yaml
  violations:
    - file: python/evidence_sanitization.py
      line: 42
      issue: "Line length 127 chars (limit 100)"
      code_snippet: "# Full line context"
      recommendation: "Split into multiple lines using implicit line continuation"
  ```

**Primary Agent Action**:
- Apply fixes following PEP 8 line continuation rules
- Use implicit line continuation (parentheses) over explicit backslashes
- Maintain code readability - do not sacrifice clarity for brevity
- Run `ruff check` after each fix to verify
- Use `replace_string_in_file` tool with 3-5 lines context before/after

#### Objective 2: Security Validation Script (HIGH PRIORITY)
**Research Subagent 2 (security_pattern_research)**:
- Tool Usage: `semantic_search`, `grep_search`, `read_file`
- Search Targets: `scripts/`, `build/`, `tests/` directories
- Deliverable: Security validation patterns from existing codebase
- Constraints: DO NOT create script, report patterns only
- Query Patterns:
  - `semantic_search`: "security validation evidence leak detection"
  - `grep_search`: `def.*validate.*security|scan.*leak|check.*sensitive`
- Expected Output: Examples of:
  - Evidence file scanning patterns
  - Sensitive data detection regex
  - Hash format validation
  - Exit code conventions (0=pass, non-zero=fail)

**Primary Agent Action**:
- Create `scripts/validate_evidence_security.py` with:
  ```python
  # REQUIRED CHECKS:
  # 1. No absolute Windows paths (C:\Users\...)
  # 2. No UNC paths (\\network\share\...)
  # 3. No unredacted sensitive fields (current_user, password, token, etc.)
  # 4. All hashes are 64-char SHA-256 format
  # 5. All redacted_fields arrays populated correctly
  ```
- Use Rich library for output (panel, table, console.print)
- Exit code 0 if all checks pass, 1 if any fail
- Generate detailed report of violations found
- Include `--fix` flag for automatic remediation (optional)

#### Objective 3: Run Full Pytest Suite (CRITICAL)
**Research Subagent 3 (pytest_environment_diagnosis)**:
- Tool Usage: `read_file`, `grep_search`, `run_in_terminal`
- Diagnostic Commands: `pytest --collect-only`, `python -m pytest --version`
- Deliverable: Environment diagnosis with resolution steps
- Constraints: DO NOT run full pytest suite (primary agent responsibility)
- Files to Analyze:
  - `pytest.ini` or `pyproject.toml` [pytest] section
  - `.venv/` activation status
  - Installed pytest plugins
- Expected Output:
  ```yaml
  diagnosis:
    pytest_version: "7.4.3"
    collection_status: "40+ tests discovered"
    environment_issues:
      - "Virtual environment not activated"
      - "Missing pytest-cov plugin"
    resolution_steps:
      - "Activate .venv: & '.venv/Scripts/Activate.ps1'"
      - "Install plugins: pip install pytest-cov pytest-html"
  ```

**Primary Agent Action**:
- Activate virtual environment: `& ".venv/Scripts/Activate.ps1"`
- Verify activation: `$env:VIRTUAL_ENV` points to project .venv
- Run pytest with coverage: `python -m pytest --cov=python --cov-report=html --cov-report=term`
- Target: ≥80% coverage for evidence_sanitization.py
- Generate HTML report to `htmlcov/` directory
- Address any test failures immediately using vibe_learn

### Deliverables (File Creation Authority)
1. **Fixed Python Files**: evidence_sanitization.py, test_evidence_sanitization.py (linting clean)
2. **Security Validation Script**: scripts/validate_evidence_security.py
3. **Pytest HTML Report**: htmlcov/index.html
4. **Security Assessment**: Brief summary in mission status (no new file)

### Quality Gates
- [ ] All linting errors resolved (ruff check passes)
- [ ] Pytest coverage ≥80% for evidence_sanitization.py
- [ ] Security validation script passes on validation evidence
- [ ] Zero false positives in security scan
- [ ] Exit codes: 0 for success, non-zero for failures

### Coordination
- Report findings to Technical Account Manager (coordination lead)
- Share security patterns with DevOps Platform Engineer for CI integration
- Provide test coverage data to Software Quality Engineer

---

## 🧪 AGENT 2: SOFTWARE QUALITY ENGINEER (Testing & Quality Lead)

### Mission Context
**Primary Responsibility**: Complete Task 2 - Hashing standardization and regression tests
**Success Criteria**: SHA-256 enforced, programmatic summary computation, regression tests passing

### Applicable Instructions
Reference these instruction files from `.github/instructions/`:

1. **python.instructions.md** - Python coding standards
   - Virtual environment activation MANDATORY
   - pytest best practices
   - Type hints and comprehensive docstrings
   - Code coverage requirements (≥80%)

2. **powershell-pester-5.instructions.md** - Pester testing framework
   - Pester v5 conventions
   - Test structure (Describe, Context, It blocks)
   - Mock usage and test isolation
   - Coverage analysis

3. **Sequential-Thinking.instructions.md** - Systematic problem-solving
   - Break down complex testing scenarios
   - Document test case rationale
   - Use branched thinking for edge cases

### Mission Objectives

#### Objective 1: Enforce SHA-256 Hashing Standard (IMMEDIATE)
**Research Subagent 1 (hash_implementation_audit)**:
- Tool Usage: `grep_search`, `semantic_search`, `read_file`
- Search Patterns:
  - `hashlib.sha1|hashlib.md5|hash.*=.*sha1` (find non-SHA-256 usage)
  - `def.*hash|hash.*compute|generate.*hash` (find hash functions)
- Deliverable: Complete audit of hash generation code
- Constraints: DO NOT modify hash functions, report findings only
- Files to Search: `python/`, `src/`, `tests/` directories
- Expected Output:
  ```yaml
  hash_audit:
    sha256_usage:
      - file: python/evidence_logging_framework.py
        line: 156
        function: compute_hash()
        status: "CORRECT - using SHA-256"
    non_sha256_usage:
      - file: legacy/old_evidence.py
        line: 42
        function: quick_hash()
        algorithm: "SHA-1 (40-char)"
        status: "NEEDS MIGRATION"
    evidence_integration:
      - write_point: python/evidence_logging_framework.py:344
        sanitization: "Active via to_jsonl()"
        hash_generation: "After sanitization, before write"
  ```

**Primary Agent Action**:
- Add `hash_type: str = "sha256"` field to evidence entry schema
- Enforce 64-char hash length validation in EvidenceEntry class
- Add hash algorithm assertion: `assert len(hash) == 64, "SHA-256 must be 64-char hex"`
- Update all hash generation to explicitly use hashlib.sha256
- Add `hash_type` to all new evidence entries
- Migrate legacy evidence files (if any found)

#### Objective 2: Programmatic Summary Computation (HIGH PRIORITY)
**Research Subagent 2 (summary_computation_research)**:
- Tool Usage: `read_file`, `semantic_search`, `grep_search`
- Search Targets: Evidence bundle files, summary generation code
- Deliverable: Summary computation patterns and validation approaches
- Constraints: DO NOT implement summary logic, report patterns only
- Files to Analyze:
  - `tests/cli/evidence/validation-evidence-20251114-141308.jsonl` (current evidence)
  - Any summary computation functions in python/
- Expected Output:
  ```yaml
  summary_patterns:
    current_approach: "Manual summary entry at end of JSONL"
    proposed_approach: "Compute from entries programmatically"
    required_fields:
      - total_entries: "Count of non-summary entries"
      - total_duration_ms: "Sum of all duration_ms fields"
      - database_operations: "Count by operation type"
      - redaction_summary: "Count of redacted fields across entries"
    validation_strategy: "Compare computed vs stored summary, fail on drift"
  ```

**Primary Agent Action**:
- Create `compute_evidence_summary(entries: list[dict]) -> dict` function
- Required summary fields:
  ```python
  summary = {
      "entry_type": "summary",
      "total_entries": len([e for e in entries if e.get("entry_type") != "summary"]),
      "total_duration_ms": sum(e.get("duration_ms", 0) for e in entries),
      "operation_counts": Counter(e.get("operation") for e in entries),
      "redacted_fields_total": sum(len(e.get("redacted_fields", [])) for e in entries),
      "hash_type": "sha256",
      "generated_at": datetime.now(UTC).isoformat()
  }
  ```
- Add validation function: `validate_summary_accuracy(entries, summary) -> bool`
- Integrate into evidence generation workflow
- Add regression test for summary drift detection

#### Objective 3: Regression Test Suite (CRITICAL)
**Research Subagent 3 (regression_test_patterns)**:
- Tool Usage: `semantic_search`, `read_file`, `file_search`
- Search Targets: tests/ directory for regression test examples
- Deliverable: Regression test patterns and best practices
- Constraints: DO NOT create test files, report patterns only
- Query Patterns:
  - `semantic_search`: "regression test hash validation evidence framework"
  - `file_search`: `tests/**/test_*regression*.py`
- Expected Output: Examples of:
  - Property-based testing with hypothesis library
  - Snapshot testing for evidence output
  - Parametrized tests for multiple scenarios
  - Golden file comparisons

**Primary Agent Action**:
- Create `tests/test_evidence_hashing_regression.py`:
  ```python
  @pytest.mark.parametrize("data,expected_length", [
      (b"test", 64),  # SHA-256 always 64-char hex
      (b"a" * 10000, 64),  # Large data
  ])
  def test_hash_length_consistency(data, expected_length):
      hash_value = compute_hash(data)
      assert len(hash_value) == expected_length
      assert hash_value.isalnum()  # Hex characters only

  def test_no_sha1_40char_hashes():
      """Regression test: Ensure no 40-char SHA-1 hashes in evidence"""
      evidence_files = Path("tests/cli/evidence").glob("*.jsonl")
      for evidence_file in evidence_files:
          entries = load_jsonl(evidence_file)
          for entry in entries:
              hash_val = entry.get("hash", "")
              assert len(hash_val) != 40, f"SHA-1 detected: {hash_val}"
              assert len(hash_val) == 64, f"Invalid hash length: {len(hash_val)}"
  ```
- Create `tests/test_evidence_summary_regression.py`:
  ```python
  def test_summary_accuracy():
      """Regression test: Programmatic summary matches entry counts"""
      entries = generate_test_evidence(count=10)
      computed_summary = compute_evidence_summary(entries)

      assert computed_summary["total_entries"] == 10
      assert computed_summary["total_duration_ms"] == sum(e["duration_ms"] for e in entries)
      assert validate_summary_accuracy(entries, computed_summary)
  ```
- Run full regression suite: `pytest tests/test_*regression*.py -v`

### Deliverables (File Creation Authority)
1. **Enhanced Evidence Framework**: Updated EvidenceEntry with hash_type field
2. **Summary Computation**: compute_evidence_summary() function
3. **Regression Tests**: test_evidence_hashing_regression.py, test_evidence_summary_regression.py
4. **Test Reports**: pytest HTML report with regression coverage

### Quality Gates
- [ ] All hashes are SHA-256 with hash_type field
- [ ] Summary computation is programmatic (no manual math)
- [ ] Regression tests cover hash length, summary accuracy, no SHA-1
- [ ] Pytest coverage ≥85% for new summary computation code
- [ ] All regression tests passing

### Coordination
- Share hash audit findings with Cybersecurity Advisor
- Provide test patterns to DevOps Platform Engineer for CI integration
- Report summary computation logic to Technical Account Manager

---

## 🚀 AGENT 3: DEVOPS PLATFORM ENGINEER (CI/CD Lead)

### Mission Context
**Primary Responsibility**: Complete Task 3 - CI security lint and Task 4 - Documentation
**Success Criteria**: Guard script operational, GitHub Actions integrated, documentation complete

### Applicable Instructions
Reference these instruction files from `.github/instructions/`:

1. **github-actions-ci-cd-best-practices.instructions.md** - CI/CD pipeline design
   - Workflow structure and naming conventions
   - Job dependencies and conditional execution
   - Secret management and security scanning
   - Artifact retention and caching strategies
   - Matrix testing and parallelization

2. **python.instructions.md** - Python standards for guard scripts
   - Virtual environment requirements
   - CLI tool design with argparse or typer
   - Exit code conventions (0=pass, non-zero=fail)
   - Terminal output with Rich library

3. **powershell.instructions.md** - PowerShell helper functions
   - Pre-commit hook design
   - Invoke-Build task creation
   - Error handling and validation

4. **markdown.instructions.md** - Documentation standards
   - Heading structure (H2, H3 hierarchy)
   - Code block formatting with language tags
   - Link validation
   - Front matter requirements

### Mission Objectives

#### Objective 1: Create CI Security Lint Guard Script (IMMEDIATE)
**Research Subagent 1 (ci_pipeline_analysis)**:
- Tool Usage: `file_search`, `read_file`, `grep_search`
- Search Targets: `.github/workflows/` directory, existing CI workflows
- Deliverable: Current CI structure and integration points
- Constraints: DO NOT modify workflow files, report structure only
- Files to Analyze:
  - `.github/workflows/*.yml` (all existing workflows)
  - Pre-commit configuration (if exists)
  - Build scripts in `build/` or `scripts/`
- Expected Output:
  ```yaml
  ci_analysis:
    existing_workflows:
      - name: pytest-pr.yml
        triggers: [pull_request]
        jobs: [test-python]
        integration_point: "After test job, before merge"
      - name: quality.yml
        triggers: [push, pull_request]
        jobs: [lint, test, security]
        integration_point: "Add security-evidence-scan job"
    recommended_integration:
      workflow: quality.yml
      job_name: security-evidence-scan
      dependencies: [lint, test]
      artifact_upload: true
  ```

**Research Subagent 2 (guard_script_research)**:
- Tool Usage: `semantic_search`, `read_file`, `fetch_webpage`
- Search Targets: Existing guard/lint scripts, external best practices
- Deliverable: Guard script patterns and implementation approaches
- Constraints: DO NOT create guard script, report patterns only
- Query Patterns:
  - `semantic_search`: "security lint guard evidence validation CI gate"
  - `file_search`: `scripts/*guard*.py`, `build/*lint*.ps1`
  - Optional: `fetch_webpage` for GitHub Actions security scanning best practices
- Expected Output: Examples of:
  - File scanning patterns (glob, pathlib)
  - JSONL parsing and validation
  - Sensitive pattern detection (regex, string matching)
  - Error reporting formats (JSON, markdown)
  - Exit code strategies

**Primary Agent Action**:
- Create `scripts/guard_evidence_security.py`:
  ```python
  #!/usr/bin/env python3
  """
  CI Security Lint Guard - Evidence Bundle Validation

  Scans evidence JSONL files for security violations:
  1. Absolute Windows paths (C:\\Users\\...)
  2. UNC network paths (\\\\network\\share\\...)
  3. Unredacted sensitive fields (current_user, password, token, etc.)
  4. Non-SHA-256 hashes (40-char SHA-1, other formats)
  5. Missing redacted_fields arrays

  Exit Codes:
    0 - All checks passed
    1 - Security violations found
    2 - Invalid arguments or file errors
  """

  import typer
  from rich.console import Console
  from rich.panel import Panel
  from rich.table import Table
  from pathlib import Path
  import json
  import re

  app = typer.Typer()
  console = Console()

  SENSITIVE_PATTERNS = [
      r'C:\\Users\\[^\\]+',  # Windows user paths
      r'\\\\[a-zA-Z0-9\-]+\\',  # UNC paths
      r'"current_user":\s*"(?!REDACTED)[^"]+"',  # Unredacted current_user
      r'"password":\s*"(?!REDACTED|null)[^"]+"',  # Unredacted password
  ]

  @app.command()
  def scan(
      evidence_dir: Path = typer.Argument(..., help="Directory containing evidence JSONL files"),
      fail_fast: bool = typer.Option(False, help="Stop on first violation"),
      output_format: str = typer.Option("rich", help="Output format: rich, json, markdown")
  ):
      """Scan evidence files for security violations"""
      violations = []

      for evidence_file in evidence_dir.glob("*.jsonl"):
          file_violations = scan_file(evidence_file)
          violations.extend(file_violations)

          if fail_fast and file_violations:
              break

      # Report results
      if output_format == "rich":
          display_violations_rich(violations)
      elif output_format == "json":
          print(json.dumps(violations, indent=2))
      elif output_format == "markdown":
          display_violations_markdown(violations)

      # Exit with appropriate code
      sys.exit(1 if violations else 0)

  def scan_file(file_path: Path) -> list[dict]:
      """Scan single JSONL file for violations"""
      violations = []
      with open(file_path) as f:
          for line_num, line in enumerate(f, 1):
              entry = json.loads(line)

              # Check 1: Absolute paths
              if re.search(SENSITIVE_PATTERNS[0], line):
                  violations.append({
                      "file": str(file_path),
                      "line": line_num,
                      "type": "absolute_path",
                      "message": "Windows absolute path detected"
                  })

              # Check 2: Hash format
              hash_val = entry.get("hash", "")
              if len(hash_val) == 40:
                  violations.append({
                      "file": str(file_path),
                      "line": line_num,
                      "type": "hash_format",
                      "message": "SHA-1 (40-char) detected, use SHA-256"
                  })
              elif len(hash_val) != 64 and hash_val:
                  violations.append({
                      "file": str(file_path),
                      "line": line_num,
                      "type": "hash_format",
                      "message": f"Invalid hash length: {len(hash_val)}"
                  })

      return violations
  ```

- Create PowerShell wrapper `scripts/Invoke-EvidenceGuard.ps1`:
  ```powershell
  <#
  .SYNOPSIS
  Pre-commit hook for evidence security validation

  .DESCRIPTION
  Wraps guard_evidence_security.py for pre-commit hook integration
  #>
  [CmdletBinding()]
  param(
      [Parameter()]
      [string]$EvidencePath = "tests/cli/evidence",

      [Parameter()]
      [switch]$FailFast
  )

  & ".venv/Scripts/Activate.ps1"
  python scripts/guard_evidence_security.py $EvidencePath $(if($FailFast){"--fail-fast"})
  exit $LASTEXITCODE
  ```

#### Objective 2: GitHub Actions Integration (HIGH PRIORITY)
**Primary Agent Action**:
- Update `.github/workflows/quality.yml`:
  ```yaml
  security-evidence-scan:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install typer rich

      - name: Run Evidence Security Guard
        run: |
          python scripts/guard_evidence_security.py tests/cli/evidence --output-format json > violations.json

      - name: Upload violations report
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: evidence-violations
          path: violations.json

      - name: Comment on PR with violations
        if: failure() && github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const violations = JSON.parse(fs.readFileSync('violations.json', 'utf8'));
            const body = `## 🚨 Evidence Security Violations Detected\n\n${violations.length} violations found:\n\n${violations.map(v => `- **${v.type}** in \`${v.file}\` line ${v.line}: ${v.message}`).join('\n')}`;
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: body
            });
  ```

#### Objective 3: Documentation Updates (MEDIUM PRIORITY)
**Research Subagent 3 (documentation_gap_analysis)**:
- Tool Usage: `file_search`, `read_file`, `semantic_search`
- Search Targets: docs/ directory, existing documentation
- Deliverable: Documentation gaps and structure recommendations
- Constraints: DO NOT create docs, report gaps only
- Files to Analyze:
  - `docs/*.md` (all existing documentation)
  - README.md sections
  - AGENTS.md examples
- Expected Output:
  ```yaml
  documentation_gaps:
    missing_sections:
      - "CI/CD evidence validation pipeline"
      - "PowerShell pre-commit hook usage"
      - "better-sqlite3 PRAGMA return semantics"
    outdated_sections:
      - "Database connection examples (needs MCP update)"
      - "Evidence generation workflow (needs sanitization info)"
    recommended_structure:
      - docs/CI-CD-EVIDENCE-VALIDATION.md
      - docs/POWERSHELL-DEVELOPMENT-GUIDE.md
      - docs/DATABASE-PRAGMA-REFERENCE.md
  ```

**Primary Agent Action**:
- Create `docs/CI-CD-EVIDENCE-VALIDATION.md`:
  ```markdown
  # CI/CD Evidence Validation Pipeline

  ## Overview
  Automated security validation for evidence bundles using GitHub Actions.

  ## Guard Script Usage

  ### Local Execution
  \`\`\`powershell
  # Activate virtual environment
  & ".venv/Scripts/Activate.ps1"

  # Scan evidence directory
  python scripts/guard_evidence_security.py tests/cli/evidence

  # Fail-fast mode (stop on first violation)
  python scripts/guard_evidence_security.py tests/cli/evidence --fail-fast

  # JSON output for CI integration
  python scripts/guard_evidence_security.py tests/cli/evidence --output-format json
  \`\`\`

  ### Pre-Commit Hook
  \`\`\`powershell
  # PowerShell wrapper
  .\scripts\Invoke-EvidenceGuard.ps1 -FailFast
  \`\`\`

  ## GitHub Actions Integration

  The `security-evidence-scan` job runs automatically on all PRs and pushes to main.

  ### Workflow Configuration
  See `.github/workflows/quality.yml` for complete configuration.

  ### Violation Reporting
  - Violations are reported as PR comments
  - JSON report uploaded as workflow artifact
  - Build fails if violations detected (exit code 1)

  ## Validation Checks

  1. **Absolute Path Detection**: No C:\\Users\\ or UNC paths
  2. **Hash Format Enforcement**: SHA-256 only (64-char hex)
  3. **Sensitive Field Redaction**: current_user, password, token must be REDACTED
  4. **Redacted Fields Integrity**: redacted_fields array must be populated

  ## Exit Codes
  - `0`: All checks passed
  - `1`: Security violations found
  - `2`: Invalid arguments or file errors
  ```

- Update `docs/POWERSHELL-DEVELOPMENT-GUIDE.md`:
  - Add section on better-sqlite3 PRAGMA return semantics
  - Document PowerShell helper functions for evidence operations
  - Include pre-commit hook setup instructions

### Deliverables (File Creation Authority)
1. **Guard Script**: scripts/guard_evidence_security.py (Python)
2. **PowerShell Wrapper**: scripts/Invoke-EvidenceGuard.ps1
3. **GitHub Actions Workflow**: Updated .github/workflows/quality.yml
4. **Documentation**: docs/CI-CD-EVIDENCE-VALIDATION.md, updated POWERSHELL-DEVELOPMENT-GUIDE.md

### Quality Gates
- [ ] Guard script detects all violation types (paths, hashes, unredacted fields)
- [ ] Exit codes correct: 0=pass, 1=violations, 2=errors
- [ ] GitHub Actions workflow runs successfully
- [ ] PR comments generated for violations
- [ ] Documentation complete with copy-pasteable examples

### Coordination
- Receive security patterns from Cybersecurity Advisor
- Share CI integration with Software Quality Engineer for test automation
- Provide documentation to Technical Account Manager for review

---

## 🏗️ AGENT 4: INFRASTRUCTURE OPERATIONS MANAGER (CF_CLI & Resolver Lead)

### Mission Context
**Primary Responsibility**: Complete Task 5 - CF_CLI database resolver quality gates
**Success Criteria**: Resolver reviewed, unified contract documented, unit tests passing

### Applicable Instructions
Reference these instruction files from `.github/instructions/`:

1. **python.instructions.md** - Python standards for CF_CLI
   - Virtual environment requirements
   - Type hints for database resolver functions
   - Error handling and retry mechanisms
   - Database connection pooling best practices

2. **powershell.instructions.md** - PowerShell CF_CLI integration
   - Verb-Noun aliases (Set-Task, Get-TaskDetail)
   - Parameter validation
   - Pipeline support

3. **Sequential-Thinking.instructions.md** - Systematic code review
   - Analyze resolver architecture
   - Identify failure modes
   - Document decision rationale

### Mission Objectives

#### Objective 1: CF_CLI Database Resolver Review (IMMEDIATE)
**Research Subagent 1 (cf_cli_architecture_analysis)**:
- Tool Usage: `read_file`, `grep_search`, `semantic_search`
- Target File: `cf_cli.py` (8228 lines)
- Focus Areas:
  - Database connection factory: `_get_db()` function (line ~2391)
  - Retry decorator: `database_retry_decorator()` (line ~2124)
  - Database read utility: `_read_database()` (line ~2237)
  - Configuration loading and validation
- Deliverable: Architecture analysis and issue identification
- Constraints: DO NOT modify cf_cli.py, report findings only
- Expected Output:
  ```yaml
  resolver_analysis:
    connection_factory:
      location: "cf_cli.py:2391"
      pattern: "Delegates to configuration layer"
      databases_supported: ["PostgreSQL", "SQLite", "DuckDB"]
      connection_pooling: "Unknown - needs investigation"
    retry_mechanism:
      location: "cf_cli.py:2124"
      max_attempts: 2
      backoff: "Linear (needs exponential?)"
      exceptions_handled: "Database connection errors"
    potential_issues:
      - "No explicit connection timeout configuration"
      - "Retry mechanism may need exponential backoff"
      - "DSN parsing error handling unclear"
      - "No connection pool size limits documented"
    quality_gaps:
      - "Missing unit tests for DSN resolution"
      - "No integration tests for resolver failover"
      - "Credential handling not explicitly validated"
  ```

**Research Subagent 2 (task_management_validation_planning)**:
- Tool Usage: `read_file`, `grep_search`
- Target: Task management commands in cf_cli.py
- Focus: upsert, update, show command signatures
- Deliverable: Test scenario planning for task operations
- Constraints: DO NOT execute commands, report plan only
- Expected Output:
  ```yaml
  task_validation_plan:
    test_scenarios:
      upsert_create:
        command: "python cf_cli.py task upsert --id T-VAL-001 --title 'Test' --project P-001"
        expected: "Task created in taskman_v2 PostgreSQL"
        validation: "SELECT * FROM tasks WHERE id = 'T-VAL-001'"
      upsert_update:
        command: "python cf_cli.py task upsert --id T-VAL-001 --status in_progress"
        expected: "Task updated (idempotent)"
        validation: "Status changed, updated_at timestamp refreshed"
      show_details:
        command: "python cf_cli.py task show T-VAL-001"
        expected: "Rich UI display with task details"
        validation: "All fields visible, formatting correct"
  ```

**Primary Agent Action**:
- Execute CF_CLI task commands to validate database integration:
  ```powershell
  # Activate virtual environment
  & ".venv/Scripts/Activate.ps1"

  # Create test task
  python cf_cli.py task upsert --id T-VAL-RESOLVER-001 --title "Resolver Validation Task" --project P-VALIDATION --sprint S-2025-11 --status new

  # Update task
  python cf_cli.py task update T-VAL-RESOLVER-001 --status in_progress --actual-hours 1.5

  # Show task details
  python cf_cli.py task show T-VAL-RESOLVER-001

  # Verify in database via MCP
  # (Use database-mcp execute_query to confirm task exists)
  ```

- Document findings in resolver analysis report (no file creation until all data gathered)

#### Objective 2: Unified Resolver Contract (HIGH PRIORITY)
**Research Subagent 3 (resolver_quality_gate_research)**:
- Tool Usage: `semantic_search`, `read_file`, `grep_search`
- Search Targets: Existing unit tests for database operations
- Deliverable: Test coverage gaps and quality gate patterns
- Constraints: DO NOT create test files, report patterns only
- Query Patterns:
  - `grep_search`: `def test.*database|def test.*resolver|def test.*connection`
  - `file_search`: `tests/**/test_*database*.py`
- Expected Output:
  ```yaml
  quality_gate_research:
    existing_tests:
      - file: "tests/test_database_connection.py"
        coverage: "Basic connection tests"
        gaps: "No DSN parsing tests, no retry tests"
    test_patterns:
      dsn_resolution:
        - "Test PostgreSQL DSN parsing (host:port/database)"
        - "Test SQLite file path resolution"
        - "Test DuckDB path resolution"
      error_handling:
        - "Test connection timeout behavior"
        - "Test invalid credentials handling"
        - "Test retry mechanism with mock failures"
      connection_pooling:
        - "Test pool size limits"
        - "Test connection reuse"
        - "Test pool exhaustion handling"
  ```

**Primary Agent Action**:
- Create `docs/CF-CLI-DATABASE-RESOLVER-CONTRACT.md`:
  ```markdown
  # CF_CLI Database Resolver Contract

  ## Overview
  Unified interface for PostgreSQL, SQLite, and DuckDB database connections.

  ## Resolver Interface

  ### Connection Factory
  \`\`\`python
  def _get_db(connection_name: str) -> DatabaseConnection:
      """
      Get database connection by name.

      Args:
          connection_name: Database connection identifier
              - "taskman_v2" (PostgreSQL)
              - "trackers-sqlite" (SQLite)
              - "duckdb" (DuckDB)

      Returns:
          DatabaseConnection object with execute() method

      Raises:
          ConnectionError: If connection fails after retries
          ValueError: If connection_name not recognized
      """
  \`\`\`

  ### DSN Resolution Rules

  **PostgreSQL**:
  - Format: `postgresql://username:password@host:port/database`
  - Timeout: 30 seconds (configurable)
  - Max Connections: 10 (pool size)
  - Retry: 2 attempts with exponential backoff

  **SQLite**:
  - Format: `file:path/to/database.sqlite`
  - Relative paths resolved from workspace root
  - Max Connections: 5 (concurrent readers)
  - Retry: Not applicable (local file)

  **DuckDB**:
  - Format: `file:path/to/database.duckdb`
  - Relative paths resolved from workspace root
  - Separate MCP server (not via database-mcp)

  ## Quality Gates

  1. **DSN Parsing**: All formats parse correctly
  2. **Connection Validation**: Health check passes after connection
  3. **Retry Mechanism**: Exponential backoff with jitter
  4. **Error Messages**: Clear, actionable error messages
  5. **Credential Security**: No credential leakage in logs/errors

  ## Unit Test Requirements

  - Test DSN resolution for all three database types
  - Test retry mechanism with mock connection failures
  - Test connection timeout behavior
  - Test credential handling (no leakage)
  - Test error message clarity
  ```

- Create `tests/test_cf_cli_database_resolver.py`:
  ```python
  import pytest
  from unittest.mock import Mock, patch
  from cf_cli import _get_db, database_retry_decorator

  def test_get_db_postgresql():
      """Test PostgreSQL connection resolution"""
      conn = _get_db("taskman_v2")
      assert conn is not None
      assert conn.connection_type == "postgresql"
      # Health check
      result = conn.execute("SELECT 1 AS health")
      assert result[0]["health"] == 1

  def test_get_db_sqlite():
      """Test SQLite connection resolution"""
      conn = _get_db("trackers-sqlite")
      assert conn is not None
      assert conn.connection_type == "sqlite"
      # Health check
      result = conn.execute("SELECT 1 AS health")
      assert result[0]["health"] == 1

  def test_retry_decorator_max_attempts():
      """Test retry decorator respects max_attempts"""
      mock_func = Mock(side_effect=ConnectionError("Test failure"))
      decorated = database_retry_decorator(max_attempts=3)(mock_func)

      with pytest.raises(ConnectionError):
          decorated()

      assert mock_func.call_count == 3

  def test_dsn_parsing_postgresql():
      """Test PostgreSQL DSN parsing"""
      dsn = parse_postgresql_dsn("172.25.14.122:5432/taskman_v2")
      assert dsn["host"] == "172.25.14.122"
      assert dsn["port"] == 5432
      assert dsn["database"] == "taskman_v2"

  def test_dsn_parsing_sqlite_relative_path():
      """Test SQLite relative path resolution"""
      path = resolve_sqlite_path("db/trackers.sqlite")
      assert path.is_absolute()
      assert "db/trackers.sqlite" in str(path)

  @patch("cf_cli.psycopg2.connect")
  def test_connection_error_message_clarity(mock_connect):
      """Test error messages are clear and actionable"""
      mock_connect.side_effect = ConnectionError("Connection refused")

      with pytest.raises(ConnectionError) as exc_info:
          _get_db("taskman_v2")

      error_message = str(exc_info.value)
      assert "taskman_v2" in error_message
      assert "Connection refused" in error_message
      assert "credentials" not in error_message.lower()  # No credential leakage
  ```

### Deliverables (File Creation Authority)
1. **Resolver Contract**: docs/CF-CLI-DATABASE-RESOLVER-CONTRACT.md
2. **Unit Tests**: tests/test_cf_cli_database_resolver.py
3. **Task Validation Report**: Summary in mission status (no separate file)

### Quality Gates
- [ ] CF_CLI task commands execute successfully
- [ ] Database operations persist correctly
- [ ] Resolver contract documented with all three database types
- [ ] Unit tests cover DSN parsing, retry, error handling
- [ ] All unit tests passing (pytest -v tests/test_cf_cli_database_resolver.py)

### Coordination
- Share CF_CLI validation results with Technical Account Manager
- Provide resolver test patterns to Software Quality Engineer
- Report database integration status to Site Reliability Engineer

---

## 🔬 AGENT 5: SITE RELIABILITY ENGINEER (Integration Testing Lead)

### Mission Context
**Primary Responsibility**: Execute cross-database integration test with unified evidence bundle
**Success Criteria**: Sequential queries across all three databases, consistent sanitization, unified evidence

### Applicable Instructions
Reference these instruction files from `.github/instructions/`:

1. **python.instructions.md** - Python integration test standards
   - pytest integration test conventions
   - Fixture design for database connections
   - Test ordering and dependencies

2. **Sequential-Thinking.instructions.md** - Integration workflow design
   - Plan multi-database query sequences
   - Document evidence correlation logic
   - Track integration points

### Mission Objectives

#### Objective 1: Cross-Database Integration Test (IMMEDIATE)
**Research Subagent 1 (integration_test_scenario_research)**:
- Tool Usage: `semantic_search`, `read_file`, `file_search`
- Search Targets: tests/ directory for integration test examples
- Deliverable: Integration test patterns and scenarios
- Constraints: DO NOT execute queries, report scenarios only
- Query Patterns:
  - `semantic_search`: "integration test multi-database workflow"
  - `file_search`: `tests/**/test_*integration*.py`
- Expected Output:
  ```yaml
  integration_scenarios:
    sequential_query_workflow:
      step_1: "Query PostgreSQL for task list"
      step_2: "Query SQLite for local tracking data"
      step_3: "Query DuckDB for analytics metrics"
      step_4: "Generate unified evidence bundle"
      step_5: "Validate sanitization consistency"
    correlation_strategy:
      - "Single correlation_id for entire workflow"
      - "Sequential operation numbers (001, 002, 003)"
      - "Consistent timestamp across entries"
    validation_criteria:
      - "All paths normalized consistently"
      - "All sensitive fields redacted"
      - "All hashes SHA-256 format"
      - "Summary computed programmatically"
  ```

**Primary Agent Action**:
- Create `tests/test_cross_database_integration.py`:
  ```python
  import pytest
  from pathlib import Path
  from datetime import datetime, UTC
  import json

  @pytest.mark.integration
  def test_cross_database_sequential_workflow():
      """
      Integration test: Query all three databases in sequence,
      generate unified evidence bundle, validate sanitization.
      """
      correlation_id = f"QSE-{datetime.now(UTC).strftime('%Y%m%d-%H%M')}-INTEGRATION"
      evidence_entries = []

      # Step 1: Query PostgreSQL
      pg_result = execute_postgresql_query(
          connection="taskman_v2",
          query="SELECT current_user, current_database(), version()"
      )
      evidence_entries.append({
          "correlation_id": correlation_id,
          "operation": "postgresql_query",
          "database": "taskman_v2",
          "result": pg_result,
          "timestamp": datetime.now(UTC).isoformat()
      })

      # Step 2: Query SQLite
      sqlite_result = execute_sqlite_query(
          connection="trackers-sqlite",
          query="PRAGMA database_list"
      )
      evidence_entries.append({
          "correlation_id": correlation_id,
          "operation": "sqlite_query",
          "database": "trackers-sqlite",
          "result": sqlite_result,
          "timestamp": datetime.now(UTC).isoformat()
      })

      # Step 3: Query DuckDB
      duckdb_result = execute_duckdb_query(
          query="PRAGMA version"
      )
      evidence_entries.append({
          "correlation_id": correlation_id,
          "operation": "duckdb_query",
          "database": "metrics",
          "result": duckdb_result,
          "timestamp": datetime.now(UTC).isoformat()
      })

      # Step 4: Generate unified evidence bundle
      evidence_file = Path(f"tests/cli/evidence/integration-{correlation_id}.jsonl")
      with open(evidence_file, "w") as f:
          for entry in evidence_entries:
              sanitized = sanitize_evidence_record(entry)
              f.write(json.dumps(sanitized) + "\n")

      # Step 5: Validate sanitization consistency
      validate_evidence_bundle(evidence_file)

      # Assertions
      assert evidence_file.exists()
      assert len(evidence_entries) == 3

      # Load and validate
      with open(evidence_file) as f:
          loaded_entries = [json.loads(line) for line in f]

      for entry in loaded_entries:
          # Check 1: No absolute paths
          entry_str = json.dumps(entry)
          assert "C:\\Users\\" not in entry_str
          assert "james.e.hardy" not in entry_str

          # Check 2: Sensitive fields redacted
          if "current_user" in entry:
              assert entry["current_user"] == "REDACTED"

          # Check 3: Paths normalized
          if "file" in entry:
              assert "%WORKSPACE%" in entry["file"] or not entry["file"].startswith("C:")

          # Check 4: Hash format
          if "hash" in entry:
              assert len(entry["hash"]) == 64  # SHA-256

  def validate_evidence_bundle(evidence_file: Path):
      """Validate evidence bundle meets all security criteria"""
      with open(evidence_file) as f:
          entries = [json.loads(line) for line in f]

      # Validation checks
      for entry in entries:
          # Hash validation
          if "hash" in entry:
              assert len(entry["hash"]) == 64, f"Invalid hash length: {len(entry['hash'])}"
              assert entry.get("hash_type") == "sha256", "Missing hash_type field"

          # Redacted fields integrity
          if "redacted_fields" in entry:
              for field in entry["redacted_fields"]:
                  if field in entry:
                      assert entry[field] == "REDACTED", f"Field {field} not redacted"

      # Summary validation (if present)
      summary = next((e for e in entries if e.get("entry_type") == "summary"), None)
      if summary:
          non_summary_entries = [e for e in entries if e.get("entry_type") != "summary"]
          assert summary["total_entries"] == len(non_summary_entries)
  ```

#### Objective 2: Evidence Bundle Validation (HIGH PRIORITY)
**Research Subagent 2 (evidence_bundle_analysis)**:
- Tool Usage: `read_file`, `grep_search`
- Target: Evidence entry schema and validation logic
- Deliverable: Schema requirements and validation rules
- Constraints: DO NOT generate bundles, report structure only
- Files to Analyze:
  - `tests/cli/evidence/validation-evidence-20251114-141308.jsonl` (reference)
  - Schema definitions (if any in schemas/ directory)
- Expected Output:
  ```yaml
  schema_requirements:
    required_fields:
      - correlation_id: "QSE-YYYYMMDD-HHMM-UUID format"
      - operation: "Descriptive operation name"
      - timestamp: "ISO 8601 with UTC timezone"
      - hash: "64-char SHA-256 hex"
      - hash_type: "Must be 'sha256'"
    optional_fields:
      - duration_ms: "Operation duration in milliseconds"
      - result: "Query result data (sanitized)"
      - redacted_fields: "Array of field names redacted"
    summary_entry:
      entry_type: "summary"
      total_entries: "Count of non-summary entries"
      total_duration_ms: "Sum of all durations"
  ```

**Primary Agent Action**:
- Execute integration test:
  ```powershell
  # Activate virtual environment
  & ".venv/Scripts/Activate.ps1"

  # Run integration test
  pytest tests/test_cross_database_integration.py -v -s

  # Verify evidence bundle
  $evidenceFile = Get-ChildItem "tests/cli/evidence/integration-*.jsonl" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
  python scripts/validate_evidence_security.py (Split-Path $evidenceFile -Parent)
  ```

#### Objective 3: Sanitization Consistency Audit (CRITICAL)
**Research Subagent 3 (sanitization_consistency_audit)**:
- Tool Usage: `read_file`, `grep_search`, `semantic_search`
- Focus: Sanitization behavior differences across database types
- Deliverable: Consistency audit findings
- Constraints: DO NOT create reports, deliver findings only
- Analysis Areas:
  - PostgreSQL result set sanitization
  - SQLite PRAGMA output sanitization
  - DuckDB path normalization
- Expected Output:
  ```yaml
  consistency_audit:
    postgresql:
      field_redaction: "current_user consistently REDACTED"
      path_normalization: "Not applicable (no file paths)"
      edge_cases: "Version strings may contain sensitive info"
    sqlite:
      field_redaction: "Not applicable (no user fields)"
      path_normalization: "PRAGMA database_list paths normalized"
      edge_cases: "Temporary file paths need attention"
    duckdb:
      field_redaction: "Not applicable (no user fields)"
      path_normalization: "File paths normalized consistently"
      edge_cases: "Extension paths may leak info"
    recommendations:
      - "Add version string sanitization pattern"
      - "Document temporary file path handling"
      - "Test extension path normalization"
  ```

**Primary Agent Action**:
- Document findings in integration test results
- Report consistency issues to Cybersecurity Advisor
- No separate file creation (findings in test output and mission status)

### Deliverables (File Creation Authority)
1. **Integration Test**: tests/test_cross_database_integration.py
2. **Unified Evidence Bundle**: tests/cli/evidence/integration-[correlation-id].jsonl
3. **Integration Report**: Summary in mission status (no separate file)

### Quality Gates
- [ ] Integration test passes (all assertions)
- [ ] Evidence bundle generated with 3+ entries
- [ ] Sanitization consistent across all database types
- [ ] Security validation script passes on integration evidence
- [ ] No absolute paths, no unredacted fields, all SHA-256 hashes

### Coordination
- Receive test scenarios from Infrastructure Operations Manager
- Validate sanitization patterns with Cybersecurity Advisor
- Report integration results to Technical Account Manager

---

## 🎯 AGENT 6: TECHNICAL ACCOUNT MANAGER (Coordination Lead)

### Mission Context
**Primary Responsibility**: Coordinate all agents, synthesize findings, ensure mission completion
**Success Criteria**: All tasks complete, validation report generated, AAR documented

### Applicable Instructions
Reference these instruction files from `.github/instructions/`:

1. **QSM-Workflow.instructions.md** - Task management workflow
   - Phase coordination (0-8)
   - Evidence bundle requirements
   - AAR structure and content

2. **memory-bank.instructions.md** - Knowledge capture
   - Document lessons learned
   - Track progress across agents
   - Seed insights for future sessions

3. **Sequential-Thinking.instructions.md** - Coordination protocol
   - Track agent dependencies
   - Document decision rationale
   - Manage risk escalation

### Mission Objectives

#### Objective 1: Agent Coordination (CONTINUOUS)
- Monitor progress from all 5 primary agents
- Resolve blockers and dependencies
- Escalate risks to user when needed
- Maintain mission status document

**Coordination Matrix**:
```yaml
dependencies:
  cybersecurity_advisor:
    blocks: []
    blocked_by: []
    deliverables: [linting_fixes, security_script, pytest_report]

  software_quality_engineer:
    blocks: [devops_platform_engineer]  # Test patterns needed for CI
    blocked_by: []
    deliverables: [hash_standardization, summary_computation, regression_tests]

  devops_platform_engineer:
    blocks: []
    blocked_by: [software_quality_engineer]  # Needs test patterns
    deliverables: [guard_script, github_actions, documentation]

  infrastructure_ops_manager:
    blocks: [site_reliability_engineer]  # Resolver validation needed
    blocked_by: []
    deliverables: [resolver_contract, cf_cli_tests, validation_report]

  site_reliability_engineer:
    blocks: []
    blocked_by: [infrastructure_ops_manager]  # Needs CF_CLI validation
    deliverables: [integration_test, unified_evidence, consistency_audit]
```

#### Objective 2: Validation Report Synthesis (END OF MISSION)
- Collect findings from all agents
- Synthesize into comprehensive validation report
- Document remaining work (if any)
- Generate AAR for mission

**Report Structure**:
```markdown
# Database Validation Mission - Final Report

## Executive Summary
[High-level mission status and outcomes]

## Agent Deliverables

### Cybersecurity Advisor
- Linting errors: [RESOLVED/PENDING]
- Security script: [COMPLETE/INCOMPLETE]
- Pytest results: [COVERAGE %]

### Software Quality Engineer
- Hash standardization: [COMPLETE/INCOMPLETE]
- Summary computation: [COMPLETE/INCOMPLETE]
- Regression tests: [PASSING/FAILING]

### DevOps Platform Engineer
- Guard script: [OPERATIONAL/PENDING]
- GitHub Actions: [INTEGRATED/PENDING]
- Documentation: [COMPLETE/INCOMPLETE]

### Infrastructure Operations Manager
- Resolver contract: [DOCUMENTED/PENDING]
- CF_CLI validation: [COMPLETE/INCOMPLETE]
- Unit tests: [PASSING/FAILING]

### Site Reliability Engineer
- Integration test: [PASSING/FAILING]
- Unified evidence: [GENERATED/PENDING]
- Consistency audit: [COMPLETE/INCOMPLETE]

## Acceptance Criteria Status
- [ ] Evidence bundles contain no absolute paths
- [ ] All hashes are SHA-256 with hash_type field
- [ ] Summary is programmatically computed
- [ ] CI security lint operational
- [ ] Resolver contract documented
- [ ] Integration test passing

## Remaining Work
[List any incomplete items with owners]

## Lessons Learned
[Key insights from mission execution]

## Recommendations
[Suggestions for future improvements]
```

### Deliverables (File Creation Authority)
1. **Mission Status**: docs/MISSION-STATUS-Database-Validation-FINAL-[date].md
2. **After-Action Review**: docs/AAR-Database-Validation-Mission-Complete-[date].md
3. **Updated Checklist**: docs/CHECKLIST-Database-Validation-Mission.md (final status update)

---

## 📋 MISSION EXECUTION PROTOCOL

### Phase 1: Research & Analysis (Subagents)
**Duration**: 30-60 minutes
**Activities**:
- All research subagents execute simultaneously
- Gather data, analyze patterns, validate findings
- Report structured data to primary agents
- **NO FILE CREATION** during this phase

### Phase 2: Primary Agent Execution
**Duration**: 2-4 hours
**Activities**:
- Primary agents receive research findings
- Make architectural decisions
- Create/modify files as needed
- Execute validation tests
- Report progress to Technical Account Manager

### Phase 3: Integration & Validation
**Duration**: 1-2 hours
**Activities**:
- Site Reliability Engineer executes integration test
- All agents validate their deliverables
- Technical Account Manager synthesizes findings
- Generate final reports

### Phase 4: Mission Closure
**Duration**: 30 minutes
**Activities**:
- Technical Account Manager creates final validation report
- Generate comprehensive AAR
- Update mission checklist with final status
- User review and acceptance

---

## ✅ SUCCESS CRITERIA (MISSION COMPLETE)

### Task 1: Evidence Redaction Hardening
- [x] Implementation complete (sanitization module)
- [ ] Linting errors resolved
- [ ] Pytest passing with ≥80% coverage
- [ ] Security validation script operational

### Task 2: Hashing Standardization
- [ ] SHA-256 enforced with hash_type field
- [ ] Programmatic summary computation
- [ ] Regression tests passing

### Task 3: CI Security Lint
- [ ] Guard script operational
- [ ] GitHub Actions integrated
- [ ] Documentation complete

### Task 4: Documentation Updates
- [ ] CI/CD examples added
- [ ] PowerShell usage documented
- [ ] PRAGMA semantics documented

### Task 5: CF_CLI Resolver Quality Gates
- [ ] Resolver reviewed
- [ ] Unified contract documented
- [ ] Unit tests passing

### Integration Validation
- [ ] Cross-database test passing
- [ ] Unified evidence bundle generated
- [ ] Sanitization consistent across all database types

---

**Active Project**: Database-Validation-Mission
**Phase**: Agent Delegation with Research Architecture
**Session**: 2025-11-14
**Mission Status**: Research subagents defined, primary agents ready for activation
