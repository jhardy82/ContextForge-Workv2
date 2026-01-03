# CF-Enhanced Quality Gates API Documentation

## Overview

The CF-Enhanced Quality Gates API provides programmatic access to quality validation functionality, enabling integration with
existing development workflows and automated quality assurance processes.

## Core Classes

### QualityGateResult

Represents the outcome of a single quality gate validation.

```python
@dataclass
class QualityGateResult:
    """Result of a quality gate validation"""
    gate_type: str
    status: QualityGateStatus
    score: Optional[float] = None
    evidence: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    validation_timestamp: Optional[datetime] = None
    required: bool = True

    def is_passing(self) -> bool:
        """Check if the quality gate result is passing"""
        return self.status == QualityGateStatus.PASS

    def get_evidence_summary(self) -> str:
        """Get a summary of validation evidence"""
        if not self.evidence:
            return "No evidence available"
        return f"Validated {len(self.evidence)} evidence items"
```

#### Usage Example

```python
from python.cf_enhanced_quality_gates import QualityGateResult, QualityGateStatus

# Create a quality gate result
result = QualityGateResult(
    gate_type="COF",
    status=QualityGateStatus.PASS,
    score=95.0,
    evidence={
        "dimensions_validated": 13,
        "completeness_score": 95.0,
        "missing_dimensions": []
    },
    recommendations=["All COF dimensions validated successfully"]
)

print(f"Gate Status: {result.status}")
print(f"Evidence: {result.get_evidence_summary()}")
```

### QualityGateReport

Comprehensive report containing all quality gate validation results.

```python
@dataclass
class QualityGateReport:
    """Comprehensive quality gate validation report"""
    task_id: str
    project_context: Dict[str, Any]
    results: Dict[str, QualityGateResult]
    overall_status: QualityGateStatus
    validation_timestamp: datetime
    execution_duration: Optional[float] = None
    recommendations: Optional[List[str]] = None

    def get_failed_gates(self) -> List[str]:
        """Get list of failed quality gate names"""
        return [name for name, result in self.results.items()
                if result.status == QualityGateStatus.FAIL]

    def get_passing_percentage(self) -> float:
        """Calculate percentage of passing quality gates"""
        if not self.results:
            return 0.0
        passing_count = sum(1 for result in self.results.values()
                          if result.status == QualityGateStatus.PASS)
        return (passing_count / len(self.results)) * 100

    def generate_summary(self) -> str:
        """Generate human-readable summary of quality gate results"""
        failed_gates = self.get_failed_gates()
        passing_pct = self.get_passing_percentage()

        summary = f"Quality Gate Validation Summary for {self.task_id}:\n"
        summary += f"Overall Status: {self.overall_status}\n"
        summary += f"Passing Rate: {passing_pct:.1f}%\n"

        if failed_gates:
            summary += f"Failed Gates: {', '.join(failed_gates)}\n"

        return summary
```

#### Usage Example

```python
# Generate comprehensive quality report
report = runner.generate_comprehensive_report()
print(report.generate_summary())

# Check for failures
if report.get_failed_gates():
    print(f"Failed gates require attention: {report.get_failed_gates()}")

# Analyze passing rate
if report.get_passing_percentage() < 80:
    print("Quality threshold not met - remediation required")
```

### CFEnhancedQualityGateRunner

Main orchestration class for executing quality gate validations.

```python
class CFEnhancedQualityGateRunner:
    """CF-Enhanced Quality Gate validation runner"""

    def __init__(self, task_id: str, project_context: Dict[str, Any]):
        self.task_id = task_id
        self.project_context = project_context
        self.logger = self._setup_logging()

    def execute_tier_1_constitutional(self) -> Dict[str, QualityGateResult]:
        """Execute Tier 1: Constitutional Quality Gates"""
        results = {}

        # COF Gate validation
        results["COF"] = self.validate_cof_gate()

        # UCL Gate validation
        results["UCL"] = self.validate_ucl_gate()

        # Ethics Gate validation
        results["ETHICS"] = self.validate_ethics_gate()

        return results

    def execute_tier_2_operational(self) -> Dict[str, QualityGateResult]:
        """Execute Tier 2: Operational Quality Gates"""
        results = {}

        results["MEMORY_BANK"] = self.validate_memory_bank_gate()
        results["TEMPLATE"] = self.validate_template_gate()
        results["WORKFLOW"] = self.validate_workflow_gate()
        results["DOCUMENTATION"] = self.validate_documentation_gate()

        return results

    def execute_tier_3_cognitive(self) -> Dict[str, QualityGateResult]:
        """Execute Tier 3: Cognitive Quality Gates"""
        results = {}

        results["META_COGNITIVE"] = self.validate_meta_cognitive_gate()
        results["ADVERSARIAL"] = self.validate_adversarial_gate()
        results["MULTI_PERSPECTIVE"] = self.validate_multi_perspective_gate()

        return results

    def execute_all_tiers(self) -> QualityGateReport:
        """Execute all quality gate tiers and generate comprehensive report"""
        all_results = {}

        # Execute all tiers
        all_results.update(self.execute_tier_1_constitutional())
        all_results.update(self.execute_tier_2_operational())
        all_results.update(self.execute_tier_3_cognitive())
        all_results.update(self.execute_tier_4_integration())

        # Determine overall status
        overall_status = self._determine_overall_status(all_results)

        return QualityGateReport(
            task_id=self.task_id,
            project_context=self.project_context,
            results=all_results,
            overall_status=overall_status,
            validation_timestamp=datetime.utcnow(),
            recommendations=self._generate_recommendations(all_results)
        )
```

#### Usage Example

```python
# Initialize runner
runner = CFEnhancedQualityGateRunner("T-20250919-001", get_project_context())

# Execute specific tier
constitutional_results = runner.execute_tier_1_constitutional()

# Execute all tiers
comprehensive_report = runner.execute_all_tiers()

# Process results
if comprehensive_report.overall_status == QualityGateStatus.FAIL:
    handle_quality_failures(comprehensive_report)
else:
    proceed_with_task_completion()
```

## Quality Gate Validation Methods

### Constitutional Tier Validation

#### validate_cof_gate()

Validates Context Ontology Framework (COF) completeness across all 13 dimensions.

```python
def validate_cof_gate(self) -> QualityGateResult:
    """
    Validate COF gate compliance

    Returns:
        QualityGateResult: Validation result with evidence and recommendations

    Validation Criteria:
        - All 13 COF dimensions must be populated
        - Each dimension must have substantial analysis (>100 characters)
        - No placeholder text allowed
        - Evidence links must be provided for each dimension
    """
    cof_analysis = self._extract_cof_analysis()

    required_dimensions = [
        'Identity', 'Intent', 'Stakeholders', 'Context', 'Scope', 'Time',
        'Space', 'Modality', 'State', 'Scale', 'Risk', 'Evidence', 'Ethics'
    ]

    validated_dimensions = []
    missing_dimensions = []

    for dimension in required_dimensions:
        if self._validate_cof_dimension(cof_analysis, dimension):
            validated_dimensions.append(dimension)
        else:
            missing_dimensions.append(dimension)

    coverage_percentage = (len(validated_dimensions) / len(required_dimensions)) * 100

    return QualityGateResult(
        gate_type="COF",
        status=QualityGateStatus.PASS if coverage_percentage >= 100 else QualityGateStatus.FAIL,
        score=coverage_percentage,
        evidence={
            "validated_dimensions": validated_dimensions,
            "missing_dimensions": missing_dimensions,
            "coverage_percentage": coverage_percentage
        },
        recommendations=self._generate_cof_recommendations(missing_dimensions)
    )
```

#### validate_ucl_gate()

Validates Universal Context Law (UCL) compliance across all 5 laws.

```python
def validate_ucl_gate(self) -> QualityGateResult:
    """
    Validate UCL compliance

    Returns:
        QualityGateResult: Validation result with compliance evidence

    Validation Criteria:
        - UCL-1: Verifiability - No claims without evidence
        - UCL-2: Precedence - General knowledge precedence respected
        - UCL-3: Provenance - All artifacts declare inputs/outputs
        - UCL-4: Reproducibility - Processes are deterministic
        - UCL-5: Integrity - Raw inputs preserved
    """
    ucl_compliance = {}

    # Validate each UCL law
    ucl_compliance["UCL-1"] = self._validate_verifiability()
    ucl_compliance["UCL-2"] = self._validate_precedence()
    ucl_compliance["UCL-3"] = self._validate_provenance()
    ucl_compliance["UCL-4"] = self._validate_reproducibility()
    ucl_compliance["UCL-5"] = self._validate_integrity()

    compliant_laws = [law for law, compliant in ucl_compliance.items() if compliant]
    compliance_percentage = (len(compliant_laws) / 5) * 100

    return QualityGateResult(
        gate_type="UCL",
        status=QualityGateStatus.PASS if compliance_percentage >= 100 else QualityGateStatus.FAIL,
        score=compliance_percentage,
        evidence=ucl_compliance,
        recommendations=self._generate_ucl_recommendations(ucl_compliance)
    )
```

### Operational Tier Validation

#### validate_memory_bank_gate()

Validates memory bank currency and completeness.

```python
def validate_memory_bank_gate(self) -> QualityGateResult:
    """
    Validate memory bank currency

    Returns:
        QualityGateResult: Validation result with memory bank status

    Validation Criteria:
        - activeContext.md updated within session
        - progress.md reflects current state
        - systemPatterns.md updated if architectural changes occurred
        - All memory bank files have consistent timestamps
    """
    memory_bank_files = [
        "activeContext.md",
        "progress.md",
        "systemPatterns.md",
        "projectbrief.md",
        "productContext.md",
        "techContext.md"
    ]

    file_statuses = {}
    session_start = self._get_session_start_time()

    for file_name in memory_bank_files:
        file_path = Path(".copilot-tracking/memory-bank") / file_name
        if file_path.exists():
            last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
            is_current = last_modified >= session_start
            file_statuses[file_name] = {
                "exists": True,
                "last_modified": last_modified.isoformat(),
                "is_current": is_current
            }
        else:
            file_statuses[file_name] = {"exists": False, "is_current": False}

    critical_files = ["activeContext.md", "progress.md"]
    critical_current = all(
        file_statuses.get(file, {}).get("is_current", False)
        for file in critical_files
    )

    return QualityGateResult(
        gate_type="MEMORY_BANK",
        status=QualityGateStatus.PASS if critical_current else QualityGateStatus.FAIL,
        evidence=file_statuses,
        recommendations=self._generate_memory_bank_recommendations(file_statuses)
    )
```

### Cognitive Tier Validation

#### validate_meta_cognitive_gate()

Validates meta-cognitive analysis completeness.

```python
def validate_meta_cognitive_gate(self) -> QualityGateResult:
    """
    Validate meta-cognitive analysis

    Returns:
        QualityGateResult: Validation result with meta-cognitive evidence

    Validation Criteria:
        - Process reflection documented
        - Assumption validation performed
        - Approach evolution tracked
        - Bias identification completed
    """
    meta_analysis = self._extract_meta_cognitive_analysis()

    required_elements = [
        'process_reflection',
        'assumption_validation',
        'approach_evolution',
        'bias_identification'
    ]

    completed_elements = []
    for element in required_elements:
        if self._validate_meta_element(meta_analysis, element):
            completed_elements.append(element)

    completeness = (len(completed_elements) / len(required_elements)) * 100

    return QualityGateResult(
        gate_type="META_COGNITIVE",
        status=QualityGateStatus.PASS if completeness >= 75 else QualityGateStatus.FAIL,
        score=completeness,
        evidence={
            "completed_elements": completed_elements,
            "missing_elements": list(set(required_elements) - set(completed_elements)),
            "completeness_percentage": completeness
        },
        recommendations=self._generate_meta_cognitive_recommendations(completed_elements)
    )
```

## Integration Patterns

### Flask/FastAPI Integration

```python
from flask import Flask, jsonify, request
from python.cf_enhanced_quality_gates import CFEnhancedQualityGateRunner

app = Flask(__name__)

@app.route('/quality-gates/validate/<task_id>', methods=['POST'])
def validate_quality_gates(task_id: str):
    """API endpoint for quality gate validation"""
    try:
        project_context = request.json.get('project_context', {})
        runner = CFEnhancedQualityGateRunner(task_id, project_context)

        # Execute validation based on requested tier
        tier = request.json.get('tier', 'all')

        if tier == 'constitutional':
            results = runner.execute_tier_1_constitutional()
        elif tier == 'operational':
            results = runner.execute_tier_2_operational()
        elif tier == 'cognitive':
            results = runner.execute_tier_3_cognitive()
        else:  # all tiers
            report = runner.execute_all_tiers()
            return jsonify({
                'status': 'success',
                'report': {
                    'task_id': report.task_id,
                    'overall_status': report.overall_status.value,
                    'passing_percentage': report.get_passing_percentage(),
                    'failed_gates': report.get_failed_gates(),
                    'summary': report.generate_summary()
                }
            })

        return jsonify({
            'status': 'success',
            'tier': tier,
            'results': {
                name: {
                    'gate_type': result.gate_type,
                    'status': result.status.value,
                    'score': result.score
                } for name, result in results.items()
            }
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
```

### GitHub Actions Integration

```python
# .github/workflows/quality-gates.yml
name: CF Enhanced Quality Gates

on:
  pull_request:
    branches: [ main ]

jobs:
  quality-validation:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run CF Enhanced Quality Gates
      id: quality_gates
      run: |
        python -c "
        from python.cf_enhanced_quality_gates import CFEnhancedQualityGateRunner
        import json
        import sys

        runner = CFEnhancedQualityGateRunner('${{ github.event.pull_request.number }}', {
            'repository': '${{ github.repository }}',
            'pr_number': ${{ github.event.pull_request.number }},
            'branch': '${{ github.head_ref }}'
        })

        report = runner.execute_all_tiers()

        with open('quality_report.json', 'w') as f:
            json.dump({
                'overall_status': report.overall_status.value,
                'passing_percentage': report.get_passing_percentage(),
                'failed_gates': report.get_failed_gates(),
                'summary': report.generate_summary()
            }, f)

        if report.overall_status.value == 'FAIL':
            print('Quality gates failed - see report for details')
            sys.exit(1)
        "

    - name: Upload Quality Report
      uses: actions/upload-artifact@v3
      with:
        name: quality-gates-report
        path: quality_report.json

    - name: Comment PR with Results
      if: always()
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          const report = JSON.parse(fs.readFileSync('quality_report.json', 'utf8'));

          const comment = `## CF Enhanced Quality Gates Report

          **Overall Status:** ${report.overall_status}
          **Passing Rate:** ${report.passing_percentage.toFixed(1)}%

          ${report.failed_gates.length > 0 ?
            `**Failed Gates:** ${report.failed_gates.join(', ')}` :
            '✅ All quality gates passed!'}

          ### Summary
          \`\`\`
          ${report.summary}
          \`\`\`
          `;

          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          });
```

### PyTest Integration

```python
# conftest.py
import pytest
from python.cf_enhanced_quality_gates import CFEnhancedQualityGateRunner

@pytest.fixture
def quality_gate_runner():
    """Fixture for CF Enhanced Quality Gate Runner"""
    return CFEnhancedQualityGateRunner(
        task_id="TEST-001",
        project_context={"test_mode": True}
    )

# test_quality_gates.py
def test_constitutional_gates(quality_gate_runner):
    """Test constitutional quality gates pass"""
    results = quality_gate_runner.execute_tier_1_constitutional()

    assert all(result.status.value == "PASS" for result in results.values()), \
        f"Constitutional gates failed: {[name for name, result in results.items() if result.status.value != 'PASS']}"

def test_comprehensive_quality_validation(quality_gate_runner):
    """Test comprehensive quality gate validation"""
    report = quality_gate_runner.execute_all_tiers()

    assert report.get_passing_percentage() >= 80, \
        f"Quality threshold not met: {report.get_passing_percentage()}% (expected ≥80%)"

    if report.get_failed_gates():
        pytest.fail(f"Quality gates failed: {report.get_failed_gates()}")
```

## Error Handling

### Custom Exceptions

```python
class QualityGateException(Exception):
    """Base exception for quality gate operations"""
    pass

class QualityGateValidationError(QualityGateException):
    """Raised when quality gate validation fails"""
    def __init__(self, gate_type: str, message: str, evidence: dict = None):
        self.gate_type = gate_type
        self.evidence = evidence or {}
        super().__init__(f"Quality gate {gate_type} failed: {message}")

class QualityGateConfigurationError(QualityGateException):
    """Raised when quality gate configuration is invalid"""
    pass
```

### Error Handling Patterns

```python
try:
    runner = CFEnhancedQualityGateRunner(task_id, project_context)
    report = runner.execute_all_tiers()

except QualityGateValidationError as e:
    logger.error(f"Quality gate validation failed: {e}")
    logger.error(f"Gate: {e.gate_type}, Evidence: {e.evidence}")

    # Handle specific gate failures
    if e.gate_type == "COF":
        handle_cof_failure(e.evidence)
    elif e.gate_type == "UCL":
        handle_ucl_failure(e.evidence)

except QualityGateConfigurationError as e:
    logger.error(f"Quality gate configuration error: {e}")
    # Fallback to default configuration

except Exception as e:
    logger.error(f"Unexpected error in quality gate validation: {e}")
    # Implement fallback or retry logic
```

## Configuration

### Quality Gate Configuration

```python
from python.cf_enhanced_quality_gates import QualityGateConfig

# Custom configuration
config = QualityGateConfig(
    constitutional_thresholds={
        'cof_coverage': 95,          # COF dimension coverage percentage
        'ucl_compliance': 100,       # UCL law compliance percentage
        'ethics_completeness': 80    # Ethics analysis completeness
    },
    operational_thresholds={
        'memory_bank_currency_hours': 24,  # Memory bank update recency
        'template_consistency': 90,        # Template usage consistency
        'workflow_compliance': 85          # Workflow progression compliance
    },
    cognitive_thresholds={
        'meta_cognitive_completeness': 75,    # Meta-cognitive analysis completeness
        'adversarial_coverage': 80,           # Adversarial analysis coverage
        'multi_perspective_completeness': 85  # Multi-perspective analysis completeness
    },
    integration_thresholds={
        'cross_methodology_alignment': 95,    # CF-Copilot-Tracking alignment
        'template_consistency': 90,           # Template consistency across artifacts
        'quality_orchestration': 85          # Quality orchestration completeness
    }
)

# Use custom configuration
runner = CFEnhancedQualityGateRunner(task_id, project_context, config=config)
```

### Environment-based Configuration

```python
import os
from python.cf_enhanced_quality_gates import QualityGateConfig

def get_environment_config() -> QualityGateConfig:
    """Get quality gate configuration based on environment"""

    if os.getenv('ENVIRONMENT') == 'production':
        return QualityGateConfig(
            constitutional_thresholds={'cof_coverage': 100, 'ucl_compliance': 100},
            strict_mode=True,
            fail_fast=True
        )
    elif os.getenv('ENVIRONMENT') == 'development':
        return QualityGateConfig(
            constitutional_thresholds={'cof_coverage': 80, 'ucl_compliance': 90},
            strict_mode=False,
            warnings_as_errors=False
        )
    else:  # staging/testing
        return QualityGateConfig(
            constitutional_thresholds={'cof_coverage': 90, 'ucl_compliance': 95},
            strict_mode=True,
            fail_fast=False
        )

# Use environment-specific configuration
config = get_environment_config()
runner = CFEnhancedQualityGateRunner(task_id, project_context, config=config)
```

---

This API documentation provides comprehensive coverage of the CF-Enhanced Quality Gates system's programmatic interface,
enabling seamless integration with existing development workflows, CI/CD pipelines, and automated quality assurance processes.
