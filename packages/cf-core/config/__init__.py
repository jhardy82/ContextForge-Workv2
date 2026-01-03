"""cf_core.config (stub)

Purpose: Minimal import-safe placeholders to unblock pytest collection per ADR.
Link: docs/adr/ADR-00XX-cf_core-test-stub-strategy.md

Replace with real implementations when available.
"""
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class AppConfig:
    name: str = "cf_core"
    version: str = "0.0.0-stub"
    settings: dict[str, Any] | None = None

DEFAULT_CONFIG = AppConfig()
