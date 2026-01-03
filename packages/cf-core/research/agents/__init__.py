"""
Research Agents Module

Collection of specialized research agents:
- DataPatternsAnalyst: Analyzes validation reports and database patterns
- CLIArchitectureAnalyst: Analyzes CLI structure and integration points
- FrameworkResearcher: Researches best practices and frameworks
- OutputSystemAnalyst: Analyzes output systems for consolidation
- IntegrationStrategist: Researches CI/CD integration patterns
- PerformanceAnalyst: Analyzes performance and optimization
- DesignSynthesizer: Synthesizes research into unified design
- SpecGenerator: Generates implementation specs
- KnowledgeCurator: Builds knowledge graph
"""

from cf_core.research.agents.data_patterns_analyst import DataPatternsAnalyst
from cf_core.research.agents.cli_architecture_analyst import CLIArchitectureAnalyst
from cf_core.research.agents.framework_researcher import FrameworkResearcher
from cf_core.research.agents.output_system_analyst import OutputSystemAnalyst
from cf_core.research.agents.integration_strategist import IntegrationStrategist
from cf_core.research.agents.performance_analyst import PerformanceAnalyst
from cf_core.research.agents.design_synthesizer import DesignSynthesizer
from cf_core.research.agents.spec_generator import SpecGenerator
from cf_core.research.agents.knowledge_curator import KnowledgeCurator

__all__ = [
    "DataPatternsAnalyst",
    "CLIArchitectureAnalyst",
    "FrameworkResearcher",
    "OutputSystemAnalyst",
    "IntegrationStrategist",
    "PerformanceAnalyst",
    "DesignSynthesizer",
    "SpecGenerator",
    "KnowledgeCurator"
]
