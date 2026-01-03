from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel


class MetricResult(BaseModel):
    """Schema for a single collected metric."""
    name: str
    value: float
    unit: str = "percentage"
    metadata: dict[str, Any] = {}

class BaseMetricCollector(ABC):
    """Abstract base class for all QSE metric collectors."""

    @abstractmethod
    async def collect(self, **kwargs) -> MetricResult:
        """Collect the metric and return a MetricResult."""
        pass
