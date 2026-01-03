# Run Artifact README Template

```
# Phase X Run Summary

- **Run ID**: <phase timestamp or label>
- **Output Folder**: <folder name>
- **Database Snapshot**: `<path or n/a>`
- **Artifacts**: README.md, installation-logs.md, tooling-versions.json, ...
- **Next Notes**: <next steps/remediation>

## Environment Checks
- PowerShell 7 present: <True/False>
- Modules detected: <list>

## Usage
- Highlight key files to review.
- Point to AAR/evidence logs for full narrative.
```

Automation can populate the placeholders using `manifest.json` and `checks.json`. Update this template if run artifacts capture new metadata.
