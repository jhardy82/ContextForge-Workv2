# CI/CD Artifact Validation

This document describes the CI/CD artifact validation workflow that ensures build artifacts meet security, integrity, and compliance requirements before deployment.

## Overview

The artifact validation system provides:

- **Security scanning** for known vulnerabilities and suspicious patterns
- **Integrity verification** through SHA-256 checksums
- **Schema validation** for structured artifact manifests
- **Format validation** for common artifact types (wheels, tarballs, JSON, etc.)
- **Size limits** to prevent oversized artifacts
- **Automated reporting** with PR comments and CI status checks

## Workflow Triggers

The validation workflow runs automatically on:

- **Push to main/develop** branches with artifact changes
- **Pull requests** that modify artifacts
- **Manual workflow dispatch** for ad-hoc validation
- **Called by other workflows** using `workflow_call`

## Validation Levels

### Basic Level
- File size validation
- Basic format checking
- Integrity verification (SHA-256)

### Standard Level (Default)
- Everything from Basic
- Security pattern scanning
- Schema validation
- Artifact type-specific validation

### Strict Level
- Everything from Standard
- Enhanced security rules
- Stricter size limits
- Additional compliance checks

## Supported Artifact Types

| Type | Extensions | Validation |
|------|------------|-------------|
| Python Wheel | `.whl` | pip inspection, metadata validation |
| Tarball | `.tar.gz` | Archive integrity, compression validation |
| JSON Data | `.json` | JSON syntax validation |
| JSONL Data | `.jsonl` | Line-by-line JSON validation |
| YAML Config | `.yml`, `.yaml` | YAML syntax validation |
| Documentation | `.md` | Markdown linting |
| Source Code | `.py`, `.ps1` | Security pattern scanning |

## Artifact Manifest Schema

Artifacts are tracked in `artifact-manifest.jsonl` with entries like:

```json
{
  "timestamp": "2025-12-30T10:15:30Z",
  "run_id": "ul_1764401747",
  "path": "build/artifacts/tests/summary.json",
  "type": "json_data",
  "size": 234,
  "sha256": "cbe892400bb0ca915dcc55c2937a798c38ded470de303a91b086bfdca77e79aa",
  "tags": ["test", "report"],
  "metadata": {
    "version": "1.0.0",
    "build_branch": "main",
    "validation_status": "passed"
  }
}
```

The manifest is validated against the JSON schema in `schemas/artifact-manifest.schema.json`.

## Security Scanning

The validation performs security checks for:

### Dangerous File Types
- Executable files (`.exe`, `.bat`, `.cmd`, `.scr`)
- Java bytecode (`.class`, `.jar`)
- Script files without proper validation

### Suspicious Patterns
- Dynamic code execution (`eval()`, `exec()`, `__import__`)
- System command execution (`subprocess`, `os.system`)
- Base64 decoding (potential obfuscation)
- Network requests in unexpected contexts

### Vulnerability Scanning
- Python packages scanned with `safety` for known CVEs
- Dependency analysis for security advisories

## Validation Reports

### JSON Report Format
```json
[
  {
    "artifact_path": "dist/mypackage-1.0.0.whl",
    "size_bytes": 1024576,
    "sha256_hash": "abc123...",
    "artifact_type": "python_wheel",
    "validation_level": "standard",
    "issues": [
      {
        "severity": "medium",
        "category": "security",
        "message": "Suspicious pattern found: subprocess",
        "artifact_path": "dist/mypackage-1.0.0.whl"
      }
    ],
    "passed": false,
    "validated_at": "2025-12-30T10:15:30Z"
  }
]
```

### Markdown Summary
- Overall pass/fail status
- Issue counts by severity
- Failed artifact details
- Remediation suggestions

## Usage Examples

### Validate Specific Artifacts
```bash
python scripts/validate-artifacts.py \
  --paths "dist/*.whl,build/artifacts/**/*" \
  --level standard \
  --output-file validation-report.json
```

### Validate Manifest Schema
```bash
python scripts/validate-artifacts.py \
  --validate-manifest \
  --manifest-path artifact-manifest.jsonl \
  --schema-path schemas/artifact-manifest.schema.json
```

### Generate Summary Report
```bash
python scripts/validate-artifacts.py \
  --generate-summary \
  --input validation-report.json \
  --output validation-summary.md
```

### Check Exit Code for CI
```bash
python scripts/validate-artifacts.py \
  --check-exit-code \
  --report validation-report.json \
  --fail-on critical,high
```

## Integration with Other Workflows

### Call from Another Workflow
```yaml
jobs:
  build:
    # ... build steps ...

  validate-artifacts:
    needs: build
    uses: ./.github/workflows/artifact-validation.yml
    with:
      artifact-paths: 'dist/**/*'
      validation-level: 'strict'
```

### PR Status Checks
The workflow automatically:
- Comments validation results on pull requests
- Sets GitHub status checks (pass/fail)
- Uploads detailed reports as workflow artifacts

## Configuration

### Environment Variables
- `VALIDATION_LEVEL`: Override default validation level
- `MAX_ARTIFACT_SIZE`: Custom size limit in bytes
- `SECURITY_SCAN_ENABLED`: Enable/disable security scanning

### Customization
- Modify `scripts/validate-artifacts.py` for custom validation rules
- Update `schemas/artifact-manifest.schema.json` for schema changes
- Add new artifact types to the validator class

## Troubleshooting

### Common Issues

**"File exceeds size limit"**
- Reduce artifact size or increase limit for validation level
- Check if large files are being included unnecessarily

**"Schema validation failed"**
- Verify manifest entries match the required schema
- Check for missing required fields or invalid data types

**"Suspicious pattern found"**
- Review flagged code for actual security issues
- Add exceptions for legitimate use cases
- Consider code refactoring to avoid suspicious patterns

### Debug Mode
Run with verbose logging:
```bash
python scripts/validate-artifacts.py --paths "dist/*" --level standard 2>&1 | tee validation.log
```

### Manual Testing
Test validation logic without CI:
```bash
# Create test artifacts
echo '{"test": "data"}' > test-artifact.json

# Run validation
python scripts/validate-artifacts.py --paths "test-artifact.json" --level basic
```

## Security Considerations

1. **Validation in Isolation**: Artifacts are scanned without execution
2. **Known Vulnerability Database**: Updated regularly via `safety`
3. **Pattern Matching**: Heuristic detection of suspicious code
4. **Size Limits**: Prevent resource exhaustion attacks
5. **Schema Enforcement**: Structured data validation

## Performance

- **Typical Runtime**: 30-60 seconds for 10-20 artifacts
- **Memory Usage**: ~50MB baseline + artifact sizes
- **Parallelization**: Artifacts validated sequentially for safety
- **Caching**: Schema and security databases cached per workflow run

## Future Enhancements

- [ ] Parallel artifact processing
- [ ] Custom validation rules via configuration
- [ ] Integration with external security scanners
- [ ] Artifact signing and verification
- [ ] Historical trend analysis
- [ ] Machine learning-based anomaly detection

## Related Documentation

- [GitHub Actions Workflows](../.github/workflows/)
- [Python Development Guidelines](../docs/09-Development-Guidelines.md)
- [Security Scanning Policies](../docs/security/)
- [Artifact Management Practices](../docs/artifacts/)
