import json
import os

from cf_core.services.metrics.base import BaseMetricCollector, MetricResult


class PytestCoverageCollector(BaseMetricCollector):
    """Metric collector for pytest coverage reports."""

    async def collect(self, coverage_file: str = "coverage.json", **kwargs) -> MetricResult:
        """
        Extract coverage percentage from a JSON coverage report.
        """
        # If path provided is relative, we check current working dir
        if not os.path.exists(coverage_file):
            return MetricResult(
                name="coverage",
                value=0.0,
                metadata={"error": "Coverage file not found", "path": coverage_file},
            )

        try:
            with open(coverage_file, encoding="utf-8") as f:
                data = json.load(f)

            # coverage.json structure usually has totals.percent_covered
            percent = data.get("totals", {}).get("percent_covered", 0.0)

            return MetricResult(
                name="coverage",
                value=float(percent),
                metadata={
                    "total_lines": data.get("totals", {}).get("num_statements", 0),
                    "missing_lines": data.get("totals", {}).get("missing_lines", 0),
                    "source": coverage_file,
                },
            )
        except Exception as e:
            return MetricResult(
                name="coverage", value=0.0, metadata={"error": str(e), "source": coverage_file}
            )
