"""
Base Research Agent

Abstract base class for all research agents in the swarm.
Research agents analyze codebases, gather best practices, and generate
implementation specifications using MCP tools.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pathlib import Path
import json
import hashlib

from cf_core.shared.result import Result


class BaseResearchAgent(ABC):
    """Base class for research agents"""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize research agent

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.findings = []
        self.agent_name = self.__class__.__name__.replace("Agent", "").replace("Analyst", "")
        self.evidence_dir = Path(self.config.get("evidence_dir", "evidence"))
        self.research_dir = Path(self.config.get("research_reports_dir", "research"))
        self.mcp_tools = {}

        # Ensure directories exist
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.research_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    async def research(self) -> Result[Dict[str, Any]]:
        """
        Execute research logic

        Returns:
            Result containing research findings
        """
        pass

    def _utc_now(self) -> str:
        """Get current UTC timestamp as ISO string"""
        return datetime.now(timezone.utc).isoformat()

    def _record_finding(
        self,
        category: str,
        finding: str,
        severity: str = "info",
        metadata: Dict[str, Any] = None
    ):
        """
        Record a research finding

        Args:
            category: Finding category (pattern, recommendation, issue, etc.)
            finding: Description of the finding
            severity: Severity level (info, warning, critical)
            metadata: Additional metadata about the finding
        """
        self.findings.append({
            "timestamp": self._utc_now(),
            "category": category,
            "finding": finding,
            "severity": severity,
            "metadata": metadata or {}
        })

    def _generate_report(self) -> Dict[str, Any]:
        """
        Generate research report from findings

        Returns:
            Dictionary containing complete research report
        """
        # Group findings by category
        by_category = {}
        for finding in self.findings:
            category = finding["category"]
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(finding)

        # Calculate statistics
        total_findings = len(self.findings)
        by_severity = {
            "info": len([f for f in self.findings if f["severity"] == "info"]),
            "warning": len([f for f in self.findings if f["severity"] == "warning"]),
            "critical": len([f for f in self.findings if f["severity"] == "critical"])
        }

        return {
            "agent_name": self.agent_name,
            "timestamp": self._utc_now(),
            "total_findings": total_findings,
            "findings_by_category": by_category,
            "findings_by_severity": by_severity,
            "all_findings": self.findings
        }

    def _log_evidence(self, report: Dict[str, Any]) -> Path:
        """
        Log evidence to JSON file with SHA-256 hash

        Args:
            report: Research report to log

        Returns:
            Path to evidence file
        """
        # Generate evidence filename
        timestamp = int(datetime.now(timezone.utc).timestamp())
        filename = f"research_{self.agent_name}_{timestamp}.json"
        filepath = self.evidence_dir / filename

        # Add evidence metadata
        evidence = {
            "version": "1.0",
            "agent": self.agent_name,
            "timestamp": self._utc_now(),
            "report": report
        }

        # Calculate SHA-256 hash of report
        report_json = json.dumps(report, sort_keys=True)
        evidence["sha256"] = hashlib.sha256(report_json.encode()).hexdigest()

        # Write evidence file
        with open(filepath, "w") as f:
            json.dump(evidence, f, indent=2)

        return filepath

    def _save_research_report(self, report: Dict[str, Any], filename: str):
        """
        Save research report as markdown file

        Args:
            report: Research report dictionary
            filename: Output filename (without extension)
        """
        filepath = self.research_dir / f"{filename}.md"

        # Convert report to markdown
        markdown = self._report_to_markdown(report)

        with open(filepath, "w") as f:
            f.write(markdown)

        return filepath

    def _report_to_markdown(self, report: Dict[str, Any]) -> str:
        """
        Convert research report to markdown format

        Args:
            report: Research report dictionary

        Returns:
            Markdown formatted report
        """
        lines = []

        # Header
        lines.append(f"# Research Report: {report['agent_name']}\n")
        lines.append(f"**Date**: {report['timestamp']}\n")
        lines.append(f"**Total Findings**: {report['total_findings']}\n")
        lines.append("---\n")

        # Summary
        lines.append("## Summary\n")
        lines.append(f"- **Info**: {report['findings_by_severity']['info']}")
        lines.append(f"- **Warning**: {report['findings_by_severity']['warning']}")
        lines.append(f"- **Critical**: {report['findings_by_severity']['critical']}\n")

        # Findings by category
        lines.append("## Findings by Category\n")
        for category, findings in report['findings_by_category'].items():
            lines.append(f"### {category.title()}\n")
            for finding in findings:
                severity_emoji = {
                    "info": "ℹ️",
                    "warning": "⚠️",
                    "critical": "🔥"
                }.get(finding["severity"], "")
                lines.append(f"- {severity_emoji} {finding['finding']}")
                if finding.get("metadata"):
                    lines.append(f"  - Metadata: {finding['metadata']}")
            lines.append("")

        # All findings detail
        if 'all_findings' in report and report['all_findings']:
            lines.append("## Detailed Findings\n")
            for i, finding in enumerate(report['all_findings'], 1):
                lines.append(f"### Finding {i}: {finding['category']}\n")
                lines.append(f"- **Severity**: {finding['severity']}")
                lines.append(f"- **Timestamp**: {finding['timestamp']}")
                lines.append(f"- **Finding**: {finding['finding']}")
                if finding.get("metadata"):
                    lines.append(f"- **Metadata**: ```json\n{json.dumps(finding['metadata'], indent=2)}\n```")
            lines.append("")

        return "\n".join(lines)

    def _read_file(self, filepath: str) -> str:
        """
        Read file contents

        Args:
            filepath: Path to file (relative or absolute)

        Returns:
            File contents as string
        """
        path = Path(filepath)
        if not path.is_absolute():
            # Try relative to project root
            path = Path.cwd() / filepath

        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        return path.read_text(encoding="utf-8")

    def _combine_files(self, filepaths: List[str]) -> str:
        """
        Read and combine multiple files

        Args:
            filepaths: List of file paths

        Returns:
            Combined file contents with headers
        """
        combined = []
        for filepath in filepaths:
            combined.append(f"\n\n### File: {filepath}\n")
            try:
                content = self._read_file(filepath)
                combined.append(content)
            except FileNotFoundError as e:
                combined.append(f"Error: {e}")

        return "\n".join(combined)

    async def execute(self) -> Result[Dict[str, Any]]:
        """
        Execute research agent with evidence logging

        Returns:
            Result containing research report and evidence path
        """
        # Run research
        result = await self.research()

        if result.is_failure:
            return result

        # Generate report
        report = self._generate_report()

        # Log evidence
        evidence_path = self._log_evidence(report)

        # Add evidence path to result
        result.value["evidence_path"] = str(evidence_path)
        result.value["report"] = report

        return result
