"""
Knowledge Curator Agent

Builds comprehensive knowledge graph from all research findings.
Consolidates entities, relations, and insights across all research agents.
"""

from typing import Dict, Any, List
from pathlib import Path
import json
from datetime import datetime

from cf_core.research.base_research_agent import BaseResearchAgent
from cf_core.research.mcp_integration import MCPToolkit
from cf_core.shared.result import Result


class KnowledgeCurator(BaseResearchAgent):
    """
    Curates comprehensive knowledge graph from research.

    Capabilities:
    - Consolidates entities from all research agents
    - Builds comprehensive relation network
    - Identifies knowledge clusters and patterns
    - Generates knowledge graph visualizations
    - Creates knowledge graph export

    MCP Tools Used:
    - memory: Knowledge graph operations
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Knowledge Curator.

        Args:
            config: Configuration dictionary with:
                - evidence_dir: Path to evidence logs
                - knowledge_graph_output: Path for graph export
        """
        super().__init__(config)
        self.toolkit = MCPToolkit(config)

        self.evidence_dir = Path(
            config.get("evidence_dir", "evidence")
        )
        self.knowledge_graph_output = Path(
            config.get("knowledge_graph_output", "knowledge_graph")
        )
        self.knowledge_graph_output.mkdir(parents=True, exist_ok=True)

        # All research agents to consolidate
        self.research_agents = [
            "DataPatternsAnalyst",
            "CLIArchitectureAnalyst",
            "FrameworkResearcher",
            "OutputSystemAnalyst",
            "IntegrationStrategist",
            "PerformanceAnalyst",
            "DesignSynthesizer",
            "SpecGenerator"
        ]

    async def research(self) -> Result[Dict[str, Any]]:
        """
        Execute knowledge curation.

        Returns:
            Result containing:
            - entities: Consolidated entity list
            - relations: Consolidated relation list
            - clusters: Knowledge clusters
            - statistics: Graph statistics
            - visualization_data: Data for graph visualization
        """
        try:
            self._record_finding(category="info", finding=f"Starting knowledge graph curation from all research agents", severity="info")

            # Step 1: Load all agent findings
            self._record_finding(category="info", finding=f"Loading findings from all research agents...", severity="info")
            all_findings = await self._load_all_agent_findings()

            self._record_finding(
                category="agent_findings",
                finding=f"Loaded findings from {len(all_findings)} research agents",
                severity="info",
                metadata={"agents": [a["name"] for a in all_findings]}
            )

            # Step 2: Extract and consolidate entities
            self._record_finding(category="info", finding=f"Extracting and consolidating entities...", severity="info")
            entities = await self._extract_entities(all_findings)

            self._record_finding(
                category="entities",
                finding=f"Extracted {len(entities)} unique entities",
                severity="info",
                metadata={
                    "types": list(set(e["entityType"] for e in entities)),
                    "count": len(entities)
                }
            )

            # Step 3: Extract and consolidate relations
            self._record_finding(category="info", finding=f"Extracting and consolidating relations...", severity="info")
            relations = await self._extract_relations(all_findings, entities)

            self._record_finding(
                category="relations",
                finding=f"Extracted {len(relations)} unique relations",
                severity="info",
                metadata={
                    "types": list(set(r["relationType"] for r in relations)),
                    "count": len(relations)
                }
            )

            # Step 4: Identify knowledge clusters
            self._record_finding(category="info", finding=f"Identifying knowledge clusters...", severity="info")
            clusters = self._identify_knowledge_clusters(entities, relations)

            self._record_finding(
                category="clusters",
                finding=f"Identified {len(clusters)} knowledge clusters",
                severity="info",
                metadata={"clusters": [c["name"] for c in clusters]}
            )

            # Step 5: Calculate graph statistics
            self._record_finding(category="info", finding=f"Calculating graph statistics...", severity="info")
            statistics = self._calculate_graph_statistics(
                entities, relations, clusters
            )

            self._record_finding(
                category="statistics",
                finding="Calculated comprehensive graph statistics",
                severity="info",
                metadata=statistics
            )

            # Step 6: Generate visualization data
            self._record_finding(category="info", finding=f"Generating visualization data...", severity="info")
            visualization_data = self._generate_visualization_data(
                entities, relations, clusters
            )

            # Step 7: Export knowledge graph
            self._record_finding(category="info", finding=f"Exporting knowledge graph...", severity="info")
            await self._export_knowledge_graph({
                "entities": entities,
                "relations": relations,
                "clusters": clusters,
                "statistics": statistics,
                "visualization_data": visualization_data
            })

            # Step 8: Store in memory MCP
            self._record_finding(category="info", finding=f"Storing knowledge graph in memory MCP...", severity="info")
            await self._store_knowledge_graph(entities, relations)

            # Compile results
            results = {
                "entities": entities,
                "relations": relations,
                "clusters": clusters,
                "statistics": statistics,
                "visualization_data": visualization_data,
                "output_directory": str(self.knowledge_graph_output)
            }

            self.log_success(
                f"Knowledge curation complete: {len(entities)} entities, "
                f"{len(relations)} relations, {len(clusters)} clusters"
            )

            return Result.ok(results)

        except Exception as e:
            self._record_finding(category="error", finding=f"Knowledge curation failed: {str(e)}", severity="critical")
            return Result.failure(f"Curation error: {str(e)}")

    async def _load_all_agent_findings(self) -> List[Dict[str, Any]]:
        """Load findings from all research agents."""
        findings = []

        for agent_name in self.research_agents:
            # Find evidence files for this agent
            evidence_files = list(
                self.evidence_dir.glob(f"research_{agent_name}_*.json")
            )

            if not evidence_files:
                self._record_finding(category="warning", finding=f"No evidence files found for {agent_name}", severity="warning")
                continue

            # Get most recent
            latest_file = sorted(evidence_files, key=lambda p: p.stat().st_mtime)[-1]

            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    evidence_data = json.load(f)

                findings.append({
                    "name": agent_name,
                    "evidence_file": str(latest_file),
                    "timestamp": evidence_data.get("timestamp"),
                    "findings": evidence_data.get("findings", []),
                    "summary": evidence_data.get("summary", {})
                })

                self.log_info(
                    f"Loaded {len(evidence_data.get('findings', []))} findings from {agent_name}"
                )

            except Exception as e:
                self._record_finding(category="error", finding=f"Failed to load {latest_file}: {str(e)}", severity="critical")

        return findings

    async def _extract_entities(
        self, all_findings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract and consolidate entities from all agents."""
        entities = []
        seen_entities = set()  # Track unique entities

        # Entity categories
        entity_categories = {
            "Project": ["P-UNIFIED-LOG", "P-READINESS-MIG", "P-CFWORK-DOCUMENTATION"],
            "Sprint": ["S-SPRINT-001", "S-SPRINT-002"],
            "Violation": ["FK_VIOLATION"],
            "Pattern": ["Result Monad", "Async/Await", "MCP Wrapper", "Evidence Logging"],
            "Component": ["Research Swarm", "Validation Swarm", "CLI Interface", "Output System"],
            "Tool": ["Typer", "Rich", "SQLite", "GitHub Actions", "MCP"],
            "Phase": ["Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phase 5", "Phase 6"]
        }

        # Extract entities from findings
        for agent in all_findings:
            summary = agent.get("summary", {})

            # Extract from DataPatternsAnalyst
            if agent["name"] == "DataPatternsAnalyst":
                violations = summary.get("violations_by_project", [])
                for violation in violations:
                    entity_name = violation.get("project_id", "")
                    if entity_name and entity_name not in seen_entities:
                        entities.append({
                            "name": entity_name,
                            "entityType": "Project",
                            "observations": [
                                f"Has {violation.get('tasks_count', 0)} orphaned tasks",
                                f"Discovered by DataPatternsAnalyst",
                                f"Impact: {violation.get('impact_rank', 'UNKNOWN')}"
                            ]
                        })
                        seen_entities.add(entity_name)

            # Extract from CLIArchitectureAnalyst
            elif agent["name"] == "CLIArchitectureAnalyst":
                integration_points = summary.get("integration_points", [])
                for point in integration_points:
                    entity_name = point.get("location", "")
                    if entity_name and entity_name not in seen_entities:
                        entities.append({
                            "name": entity_name,
                            "entityType": "IntegrationPoint",
                            "observations": [
                                f"Priority: {point.get('priority', 'UNKNOWN')}",
                                f"Type: {point.get('type', 'UNKNOWN')}",
                                "Discovered by CLIArchitectureAnalyst"
                            ]
                        })
                        seen_entities.add(entity_name)

            # Extract from FrameworkResearcher
            elif agent["name"] == "FrameworkResearcher":
                topics = summary.get("topics_researched", [])
                for topic in topics:
                    topic_name = topic if isinstance(topic, str) else topic.get("topic", "")
                    if topic_name and topic_name not in seen_entities:
                        entities.append({
                            "name": topic_name,
                            "entityType": "ResearchTopic",
                            "observations": [
                                "Researched by FrameworkResearcher",
                                "Best practices documented"
                            ]
                        })
                        seen_entities.add(topic_name)

            # Extract from DesignSynthesizer
            elif agent["name"] == "DesignSynthesizer":
                patterns = summary.get("design_patterns", [])
                for pattern in patterns:
                    pattern_name = pattern.get("name", "")
                    if pattern_name and pattern_name not in seen_entities:
                        entities.append({
                            "name": pattern_name,
                            "entityType": "DesignPattern",
                            "observations": [
                                f"Category: {pattern.get('category', 'UNKNOWN')}",
                                f"Confidence: {pattern.get('confidence', 'UNKNOWN')}",
                                "Identified by DesignSynthesizer"
                            ]
                        })
                        seen_entities.add(pattern_name)

                decisions = summary.get("architectural_decisions", [])
                for decision in decisions:
                    decision_name = decision.get("name", "")
                    if decision_name and decision_name not in seen_entities:
                        entities.append({
                            "name": decision_name,
                            "entityType": "ArchitecturalDecision",
                            "observations": [
                                f"ID: {decision.get('id', 'UNKNOWN')}",
                                f"Status: {decision.get('status', 'UNKNOWN')}",
                                "Decided by DesignSynthesizer"
                            ]
                        })
                        seen_entities.add(decision_name)

            # Extract from SpecGenerator
            elif agent["name"] == "SpecGenerator":
                code_specs = summary.get("code_specs", [])
                for spec in code_specs:
                    spec_name = spec.get("name", "")
                    if spec_name and spec_name not in seen_entities:
                        entities.append({
                            "name": spec_name,
                            "entityType": "CodeSpecification",
                            "observations": [
                                f"ID: {spec.get('id', 'UNKNOWN')}",
                                f"Phase: {spec.get('phase', 'UNKNOWN')}",
                                f"Priority: {spec.get('priority', 'UNKNOWN')}",
                                "Specified by SpecGenerator"
                            ]
                        })
                        seen_entities.add(spec_name)

        # Add standard entity categories
        for category, entity_names in entity_categories.items():
            for entity_name in entity_names:
                if entity_name not in seen_entities:
                    entities.append({
                        "name": entity_name,
                        "entityType": category,
                        "observations": [
                            f"Standard {category} entity",
                            "Part of ContextForge system"
                        ]
                    })
                    seen_entities.add(entity_name)

        return entities

    async def _extract_relations(
        self, all_findings: List[Dict[str, Any]], entities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract and consolidate relations from all agents."""
        relations = []
        seen_relations = set()  # Track unique relations

        # Entity name set for validation
        entity_names = {e["name"] for e in entities}

        # Helper to add relation
        def add_relation(from_name: str, to_name: str, relation_type: str):
            if from_name in entity_names and to_name in entity_names:
                relation_key = f"{from_name}|{relation_type}|{to_name}"
                if relation_key not in seen_relations:
                    relations.append({
                        "from": from_name,
                        "to": to_name,
                        "relationType": relation_type
                    })
                    seen_relations.add(relation_key)

        # Extract relations from findings
        for agent in all_findings:
            summary = agent.get("summary", {})

            # Relations from DataPatternsAnalyst
            if agent["name"] == "DataPatternsAnalyst":
                violations = summary.get("violations_by_project", [])
                for violation in violations:
                    project_id = violation.get("project_id", "")
                    if project_id:
                        add_relation(project_id, "FK_VIOLATION", "has_violation")

            # Relations from DesignSynthesizer
            elif agent["name"] == "DesignSynthesizer":
                patterns = summary.get("design_patterns", [])
                for pattern in patterns:
                    pattern_name = pattern.get("name", "")
                    if pattern_name:
                        # Pattern to component relations
                        for comp_name in ["Research Swarm", "Validation Swarm"]:
                            add_relation(comp_name, pattern_name, "uses_pattern")

                decisions = summary.get("architectural_decisions", [])
                for decision in decisions:
                    decision_name = decision.get("name", "")
                    # Decision to phase relations
                    phase = decision.get("phase", "")
                    if decision_name and phase:
                        add_relation(decision_name, phase, "implements_in")

                    # Decision to pattern relations
                    related_patterns = decision.get("related_patterns", [])
                    for pattern_name in related_patterns:
                        if decision_name:
                            add_relation(decision_name, pattern_name, "implements")

            # Relations from SpecGenerator
            elif agent["name"] == "SpecGenerator":
                code_specs = summary.get("code_specs", [])
                for spec in code_specs:
                    spec_name = spec.get("name", "")
                    phase = spec.get("phase", "")
                    if spec_name and phase:
                        add_relation(spec_name, phase, "implements_in")

        # Add standard relations
        standard_relations = [
            ("Research Swarm", "Validation Swarm", "feeds_into"),
            ("Validation Swarm", "CLI Interface", "integrates_with"),
            ("CLI Interface", "Output System", "uses"),
            ("Phase 1", "Phase 2", "precedes"),
            ("Phase 2", "Phase 3", "precedes"),
            ("Phase 3", "Phase 4", "precedes"),
            ("Phase 4", "Phase 5", "precedes"),
            ("Phase 5", "Phase 6", "precedes")
        ]

        for from_name, to_name, relation_type in standard_relations:
            add_relation(from_name, to_name, relation_type)

        return relations

    def _identify_knowledge_clusters(
        self, entities: List[Dict[str, Any]], relations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify knowledge clusters in the graph."""
        clusters = []

        # Cluster 1: Data Integrity
        data_integrity_entities = [
            e for e in entities
            if e["entityType"] in ["Project", "Sprint", "Violation"]
        ]
        clusters.append({
            "name": "Data Integrity",
            "description": "Entities related to database integrity and violations",
            "entity_count": len(data_integrity_entities),
            "entities": [e["name"] for e in data_integrity_entities],
            "priority": "CRITICAL"
        })

        # Cluster 2: Architecture & Design
        architecture_entities = [
            e for e in entities
            if e["entityType"] in ["DesignPattern", "ArchitecturalDecision", "Component"]
        ]
        clusters.append({
            "name": "Architecture & Design",
            "description": "Design patterns, architectural decisions, and system components",
            "entity_count": len(architecture_entities),
            "entities": [e["name"] for e in architecture_entities],
            "priority": "HIGH"
        })

        # Cluster 3: Implementation Specs
        spec_entities = [
            e for e in entities
            if e["entityType"] in ["CodeSpecification", "DatabaseSpecification", "APISpecification"]
        ]
        clusters.append({
            "name": "Implementation Specs",
            "description": "Implementation specifications for code, database, and APIs",
            "entity_count": len(spec_entities),
            "entities": [e["name"] for e in spec_entities],
            "priority": "HIGH"
        })

        # Cluster 4: Research & Tools
        research_entities = [
            e for e in entities
            if e["entityType"] in ["ResearchTopic", "Tool"]
        ]
        clusters.append({
            "name": "Research & Tools",
            "description": "Research topics and development tools",
            "entity_count": len(research_entities),
            "entities": [e["name"] for e in research_entities],
            "priority": "MEDIUM"
        })

        # Cluster 5: Integration Points
        integration_entities = [
            e for e in entities
            if e["entityType"] == "IntegrationPoint"
        ]
        clusters.append({
            "name": "Integration Points",
            "description": "CLI and system integration points",
            "entity_count": len(integration_entities),
            "entities": [e["name"] for e in integration_entities],
            "priority": "HIGH"
        })

        # Cluster 6: Implementation Phases
        phase_entities = [
            e for e in entities
            if e["entityType"] == "Phase"
        ]
        clusters.append({
            "name": "Implementation Phases",
            "description": "Phased implementation roadmap",
            "entity_count": len(phase_entities),
            "entities": [e["name"] for e in phase_entities],
            "priority": "HIGH"
        })

        return clusters

    def _calculate_graph_statistics(
        self,
        entities: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        clusters: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate comprehensive graph statistics."""

        # Entity statistics
        entity_types = {}
        for entity in entities:
            entity_type = entity["entityType"]
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1

        # Relation statistics
        relation_types = {}
        for relation in relations:
            relation_type = relation["relationType"]
            relation_types[relation_type] = relation_types.get(relation_type, 0) + 1

        # Connectivity statistics
        node_degrees = {}  # Number of connections per entity
        for relation in relations:
            from_node = relation["from"]
            to_node = relation["to"]
            node_degrees[from_node] = node_degrees.get(from_node, 0) + 1
            node_degrees[to_node] = node_degrees.get(to_node, 0) + 1

        # Most connected nodes
        most_connected = sorted(
            node_degrees.items(), key=lambda x: x[1], reverse=True
        )[:10]

        # Cluster statistics
        cluster_sizes = {c["name"]: c["entity_count"] for c in clusters}

        statistics = {
            "total_entities": len(entities),
            "total_relations": len(relations),
            "total_clusters": len(clusters),
            "entity_types": entity_types,
            "relation_types": relation_types,
            "most_connected_entities": [
                {"name": name, "connections": count}
                for name, count in most_connected
            ],
            "cluster_sizes": cluster_sizes,
            "graph_density": len(relations) / (len(entities) * (len(entities) - 1))
            if len(entities) > 1 else 0,
            "average_degree": sum(node_degrees.values()) / len(node_degrees)
            if node_degrees else 0
        }

        return statistics

    def _generate_visualization_data(
        self,
        entities: List[Dict[str, Any]],
        relations: List[Dict[str, Any]],
        clusters: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate data for knowledge graph visualization."""

        # Node data for visualization
        nodes = []
        for entity in entities:
            nodes.append({
                "id": entity["name"],
                "label": entity["name"],
                "type": entity["entityType"],
                "color": self._get_node_color(entity["entityType"]),
                "size": 10 + len(entity.get("observations", [])) * 2
            })

        # Edge data for visualization
        edges = []
        for relation in relations:
            edges.append({
                "source": relation["from"],
                "target": relation["to"],
                "label": relation["relationType"],
                "type": relation["relationType"]
            })

        # Cluster groups
        cluster_groups = {}
        for cluster in clusters:
            cluster_groups[cluster["name"]] = cluster["entities"]

        return {
            "nodes": nodes,
            "edges": edges,
            "clusters": cluster_groups,
            "layout": "force-directed",
            "format": "cytoscape"  # Compatible with Cytoscape.js
        }

    def _get_node_color(self, entity_type: str) -> str:
        """Get color for entity type."""
        color_map = {
            "Project": "#4CAF50",
            "Sprint": "#2196F3",
            "Violation": "#F44336",
            "DesignPattern": "#9C27B0",
            "ArchitecturalDecision": "#FF9800",
            "Component": "#00BCD4",
            "CodeSpecification": "#FFEB3B",
            "DatabaseSpecification": "#795548",
            "APISpecification": "#607D8B",
            "ResearchTopic": "#E91E63",
            "Tool": "#3F51B5",
            "IntegrationPoint": "#8BC34A",
            "Phase": "#FFC107"
        }
        return color_map.get(entity_type, "#9E9E9E")

    async def _export_knowledge_graph(self, graph_data: Dict[str, Any]) -> None:
        """Export knowledge graph to multiple formats."""

        # Export as JSON
        json_file = self.knowledge_graph_output / "knowledge_graph.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2)
        self._record_finding(category="info", finding=f"Exported knowledge graph to {json_file}", severity="info")

        # Export entities only
        entities_file = self.knowledge_graph_output / "entities.json"
        with open(entities_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data["entities"], f, indent=2)

        # Export relations only
        relations_file = self.knowledge_graph_output / "relations.json"
        with open(relations_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data["relations"], f, indent=2)

        # Export visualization data
        viz_file = self.knowledge_graph_output / "visualization.json"
        with open(viz_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data["visualization_data"], f, indent=2)

        # Export statistics
        stats_file = self.knowledge_graph_output / "statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data["statistics"], f, indent=2)

        self._record_finding(category="info", finding=f"Exported knowledge graph to {self.knowledge_graph_output}", severity="info")

    async def _store_knowledge_graph(
        self, entities: List[Dict[str, Any]], relations: List[Dict[str, Any]]
    ) -> None:
        """Store knowledge graph in memory MCP."""

        # Store entities
        await self.toolkit.memory_create_entities(entities)
        self._record_finding(category="info", finding=f"Stored {len(entities)} entities in memory MCP", severity="info")

        # Store relations
        await self.toolkit.memory_create_relations(relations)
        self._record_finding(category="info", finding=f"Stored {len(relations)} relations in memory MCP", severity="info")
