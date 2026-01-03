# ContextForge Implementation Architecture

**Status**: Production-Ready Design
**Phase**: 1A - Database Architecture Implementation
**Created**: 2025-09-22
**Research Foundation**: 24 technical questions with comprehensive answers

## Executive Summary

ContextForge is a decision-oriented contextual analysis system that structures and relates data influencing specific objectives using a 13-dimension Context Ontology Framework (COF). Unlike generic knowledge graphs, ContextForge provides:

- **Structured dimensional analysis** across 13 contextual dimensions
- **Multi-signal relationship validation** requiring agreement across semantic, statistical, structural, temporal, and spatial signals
- **Sacred Geometry pattern recognition** for stability analysis and motif detection
- **Bitemporal truth management** with complete provenance tracking
- **Dynamic influence scoring** with time-decay and confidence intervals

## Core Architecture

### Database Schema Design

#### Primary Context Storage

```sql
-- Context entities with 13 COF dimensions
CREATE TABLE contexts (
  id UUID PRIMARY KEY,
  kind TEXT NOT NULL,         -- entity type (frame, event, decision, etc.)
  title TEXT NOT NULL,        -- short human-readable label
  summary TEXT,               -- optional description

  -- COF 13 Dimensions as JSONB for flexibility and evolution
  dim_motivational JSONB,     -- goals, intent, success criteria
  dim_relational  JSONB,      -- stakeholders, organizational structure
  dim_temporal    JSONB,      -- deadlines, cadence, time constraints
  dim_spatial     JSONB,      -- locations, coordinates, boundaries
  dim_resource    JSONB,      -- budgets, assets, capabilities
  dim_operational JSONB,      -- processes, KPIs, workflows
  dim_risk        JSONB,      -- threats, mitigations, uncertainties
  dim_policy      JSONB,      -- rules, compliance, governance
  dim_knowledge   JSONB,      -- documentation, expertise, insights
  dim_signal      JSONB,      -- telemetry, events, metrics
  dim_outcome     JSONB,      -- targets, achievements, results
  dim_emergent    JSONB,      -- anomalies, surprises, discoveries
  dim_cultural    JSONB,      -- norms, values, organizational culture

  -- Metadata
  tags TEXT[],                -- flexible categorization
  confidence REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1) DEFAULT 0.8,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes for performance
CREATE INDEX idx_contexts_title ON contexts(title);
CREATE INDEX idx_contexts_kind ON contexts(kind);
CREATE INDEX idx_contexts_tags ON contexts USING GIN(tags);
CREATE INDEX idx_contexts_updated ON contexts(updated_at);

-- GIN indexes for JSONB dimension queries
CREATE INDEX idx_contexts_motivational ON contexts USING GIN(dim_motivational);
CREATE INDEX idx_contexts_temporal ON contexts USING GIN(dim_temporal);
CREATE INDEX idx_contexts_spatial ON contexts USING GIN(dim_spatial);
```

#### Relationship Edge Table

```sql
-- Multi-signal relationship edges with complete provenance
CREATE TABLE context_edges (
  id BIGSERIAL PRIMARY KEY,
  src UUID NOT NULL REFERENCES contexts(id) ON DELETE CASCADE,
  dst UUID NOT NULL REFERENCES contexts(id) ON DELETE CASCADE,

  -- Relationship metadata
  type TEXT NOT NULL,            -- depends_on, supports, conflicts_with, influences, related_to
  strength REAL NOT NULL CHECK (strength BETWEEN 0 AND 1),
  confidence REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),
  impact_weight REAL NOT NULL DEFAULT 1,

  -- Multi-signal validation scores
  semantic_score REAL CHECK (semantic_score BETWEEN 0 AND 1),
  statistical_score REAL CHECK (statistical_score BETWEEN 0 AND 1),
  structural_score REAL CHECK (structural_score BETWEEN 0 AND 1),
  temporal_score REAL CHECK (temporal_score BETWEEN 0 AND 1),
  spatial_score REAL CHECK (spatial_score BETWEEN 0 AND 1),

  -- Temporal validity
  started_at TIMESTAMPTZ DEFAULT now(),
  ended_at   TIMESTAMPTZ,

  -- Provenance and validation
  provenance JSONB NOT NULL,     -- source, method, thresholds, validation_rules
  signals_required INT NOT NULL DEFAULT 2,  -- minimum signals for promotion
  signals_passed INT NOT NULL,              -- actual signals that passed threshold

  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes for relationship queries
CREATE INDEX idx_edges_src ON context_edges(src);
CREATE INDEX idx_edges_dst ON context_edges(dst);
CREATE INDEX idx_edges_type ON context_edges(type);
CREATE INDEX idx_edges_strength ON context_edges(strength);
CREATE INDEX idx_edges_temporal ON context_edges(started_at, ended_at);

-- Adjacency index for graph traversal
CREATE INDEX idx_edges_adjacency ON context_edges(src, dst, type, strength);

-- Unique constraint to prevent duplicate edges
CREATE UNIQUE INDEX idx_edges_unique ON context_edges(src, dst, type)
WHERE ended_at IS NULL;
```

#### Bitemporal Versioning

```sql
-- Event sourcing for complete audit trail
CREATE TABLE context_events (
  id BIGSERIAL PRIMARY KEY,
  context_id UUID NOT NULL REFERENCES contexts(id),
  event_type TEXT NOT NULL,    -- created, updated, deleted, relationship_added
  event_data JSONB NOT NULL,   -- delta changes with old/new values
  correlation_id UUID,         -- for grouping related events
  user_id TEXT,               -- actor who made the change
  source TEXT,                -- system, api, import, user_interface
  timestamp TIMESTAMPTZ DEFAULT now()
);

-- Versioned snapshots for fast "as of T" queries
CREATE TABLE context_versions (
  context_id UUID NOT NULL,
  version INT NOT NULL,
  valid_from TIMESTAMPTZ NOT NULL,
  valid_to   TIMESTAMPTZ,
  snapshot_data JSONB NOT NULL,  -- complete state at this version
  PRIMARY KEY (context_id, version)
);

-- Indexes for temporal queries
CREATE INDEX idx_events_context_time ON context_events(context_id, timestamp);
CREATE INDEX idx_events_correlation ON context_events(correlation_id);
CREATE INDEX idx_versions_temporal ON context_versions(context_id, valid_from, valid_to);
```

### JSON Schema Validation

#### Motivational Dimension Schema

```json
{
  "$id": "schemas/motivational.schema.json",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "version": "1.0.0",
  "type": "object",
  "description": "Motivational context dimension capturing goals, intent, and success criteria",
  "properties": {
    "primary_goal": {
      "type": "string",
      "description": "Primary objective or purpose",
      "minLength": 10,
      "maxLength": 500
    },
    "success_criteria": {
      "type": "array",
      "description": "Measurable outcomes that indicate success",
      "items": {
        "type": "object",
        "properties": {
          "criterion": { "type": "string" },
          "metric": { "type": "string" },
          "target": { "type": ["string", "number"] },
          "weight": { "type": "number", "minimum": 0, "maximum": 1 }
        },
        "required": ["criterion", "metric", "target"]
      },
      "minItems": 1,
      "maxItems": 10
    },
    "priority": {
      "type": "string",
      "enum": ["low", "medium", "high", "critical"],
      "description": "Relative urgency and importance"
    },
    "alignment": {
      "type": "object",
      "description": "Alignment with broader organizational objectives",
      "properties": {
        "strategic_goals": { "type": "array", "items": { "type": "string" } },
        "okr_alignment": { "type": "string" },
        "stakeholder_buy_in": { "type": "number", "minimum": 0, "maximum": 1 }
      }
    },
    "constraints": {
      "type": "array",
      "description": "Limitations or requirements that constrain approach",
      "items": { "type": "string" },
      "maxItems": 20
    }
  },
  "required": ["primary_goal", "priority"],
  "additionalProperties": false
}
```

## Multi-Signal Relationship Engine

### Core Algorithm Implementation

```python
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

class SignalType(Enum):
    SEMANTIC = "semantic"
    STATISTICAL = "statistical"
    STRUCTURAL = "structural"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"

@dataclass
class RelationshipSignals:
    semantic: float
    statistical: float
    structural: float
    temporal: float
    spatial: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "semantic": self.semantic,
            "statistical": self.statistical,
            "structural": self.structural,
            "temporal": self.temporal,
            "spatial": self.spatial
        }

    def count_passed(self, thresholds: Dict[str, float]) -> int:
        passed = 0
        for signal_type, score in self.to_dict().items():
            if score >= thresholds.get(signal_type, 0.5):
                passed += 1
        return passed

class RelationshipSignalEngine:
    """
    Multi-signal relationship identification engine.
    Requires agreement across multiple signal families for relationship promotion.
    """

    def __init__(self,
                 stats_analyzer,
                 semantic_analyzer,
                 causal_analyzer,
                 spatial_analyzer,
                 structural_analyzer,
                 default_thresholds: Optional[Dict[str, float]] = None):
        self.stats = stats_analyzer
        self.semantic = semantic_analyzer
        self.causal = causal_analyzer
        self.spatial = spatial_analyzer
        self.structural = structural_analyzer

        # Default signal thresholds for promotion
        self.default_thresholds = default_thresholds or {
            "semantic": 0.6,      # High threshold for semantic similarity
            "statistical": 0.4,   # Moderate for statistical correlation
            "structural": 0.5,    # Moderate for structural overlap
            "temporal": 0.3,      # Lower for temporal relationships
            "spatial": 0.7        # High for spatial proximity
        }

        self.logger = logging.getLogger(__name__)

    def compute_signals(self, context_a: dict, context_b: dict) -> RelationshipSignals:
        """
        Compute all five signal family scores for relationship between contexts.
        """
        try:
            # Semantic similarity using embeddings or ontology
            semantic_score = self.semantic.similarity(
                context_a.get('text_content', ''),
                context_b.get('text_content', '')
            )

            # Statistical correlation of time series or metrics
            statistical_score = self.stats.correlation(
                context_a.get('metrics_series', []),
                context_b.get('metrics_series', [])
            )

            # Structural overlap (shared stakeholders, resources, etc.)
            structural_score = self.structural.overlap(
                context_a.get('structural_meta', {}),
                context_b.get('structural_meta', {})
            )

            # Temporal/causal relationship analysis
            temporal_score = self.causal.lead_lag_analysis(
                context_a.get('timeline', []),
                context_b.get('timeline', [])
            )

            # Spatial proximity analysis
            spatial_score = self.spatial.proximity(
                context_a.get('spatial_location', {}),
                context_b.get('spatial_location', {})
            )

            return RelationshipSignals(
                semantic=max(0.0, min(1.0, semantic_score)),
                statistical=max(0.0, min(1.0, statistical_score)),
                structural=max(0.0, min(1.0, structural_score)),
                temporal=max(0.0, min(1.0, temporal_score)),
                spatial=max(0.0, min(1.0, spatial_score))
            )

        except Exception as e:
            self.logger.error(f"Signal computation failed: {e}")
            # Return zero signals on failure
            return RelationshipSignals(0.0, 0.0, 0.0, 0.0, 0.0)

    def should_promote_relationship(self,
                                  signals: RelationshipSignals,
                                  min_signals_required: int = 2,
                                  custom_thresholds: Optional[Dict[str, float]] = None) -> Tuple[bool, Dict[str, bool]]:
        """
        Determine if relationship should be promoted based on multi-signal validation.
        Returns (should_promote, signal_results)
        """
        thresholds = custom_thresholds or self.default_thresholds

        signal_results = {}
        signals_passed = 0

        for signal_type, score in signals.to_dict().items():
            threshold = thresholds.get(signal_type, 0.5)
            passed = score >= threshold
            signal_results[signal_type] = passed

            if passed:
                signals_passed += 1

        should_promote = signals_passed >= min_signals_required

        self.logger.info(f"Relationship promotion: {signals_passed}/{len(signal_results)} signals passed, "
                        f"threshold: {min_signals_required}, promote: {should_promote}")

        return should_promote, signal_results

    def create_relationship_edge(self,
                               src_id: str,
                               dst_id: str,
                               relationship_type: str,
                               signals: RelationshipSignals,
                               confidence: float = 0.8) -> dict:
        """
        Create relationship edge data structure with full signal provenance.
        """
        signals_dict = signals.to_dict()
        signals_passed = signals.count_passed(self.default_thresholds)

        # Calculate composite strength as weighted average of passed signals
        passed_signals = [score for signal, score in signals_dict.items()
                         if score >= self.default_thresholds.get(signal, 0.5)]

        strength = np.mean(passed_signals) if passed_signals else 0.0

        return {
            "src": src_id,
            "dst": dst_id,
            "type": relationship_type,
            "strength": strength,
            "confidence": confidence,
            "semantic_score": signals.semantic,
            "statistical_score": signals.statistical,
            "structural_score": signals.structural,
            "temporal_score": signals.temporal,
            "spatial_score": signals.spatial,
            "signals_required": 2,
            "signals_passed": signals_passed,
            "provenance": {
                "method": "multi_signal_engine",
                "version": "1.0.0",
                "thresholds": self.default_thresholds,
                "signal_details": signals_dict
            }
        }
```

## Sacred Geometry Pattern Recognition

### Pentagon φ-Ratio Validation Engine

```python
import networkx as nx
import numpy as np
from typing import List, Dict, Optional, Set, Tuple
import math

class SacredGeometryPatternEngine:
    """
    Sacred Geometry pattern recognition for contextual relationship networks.
    Emphasizes Pentagon patterns with φ-ratio validation for stability analysis.
    """

    PHI = 1.6180339887498948  # Golden ratio
    PHI_TOLERANCE = 0.05      # 5% tolerance for φ-ratio validation

    def __init__(self, graph: nx.DiGraph):
        self.graph = graph
        self.phi_patterns = []
        self.stability_metrics = {}

    def is_phi_compliant(self, ratio: float, tolerance: Optional[float] = None) -> bool:
        """Check if ratio approximates the golden ratio φ within tolerance."""
        tol = tolerance or self.PHI_TOLERANCE
        return abs(ratio - self.PHI) <= self.PHI * tol

    def find_pentagon_cycles(self) -> List[List[str]]:
        """
        Find all 5-cycles (pentagon patterns) in the relationship graph.
        Returns list of node sequences forming pentagons.
        """
        pentagons = []

        # Use NetworkX to find cycles of length 5
        try:
            simple_cycles = list(nx.simple_cycles(self.graph))
            pentagons = [cycle for cycle in simple_cycles if len(cycle) == 5]
        except nx.NetworkXError:
            # Handle cases where graph has no cycles
            pass

        return pentagons

    def validate_pentagon_phi_ratios(self, pentagon_nodes: List[str]) -> Dict[str, float]:
        """
        Validate φ-ratio compliance for pentagon pattern.
        Analyzes edge weights and relationship strengths for golden ratio patterns.
        """
        if len(pentagon_nodes) != 5:
            return {"valid": False, "phi_score": 0.0}

        # Extract edge weights for the pentagon cycle
        edge_weights = []
        for i in range(5):
            src = pentagon_nodes[i]
            dst = pentagon_nodes[(i + 1) % 5]

            if self.graph.has_edge(src, dst):
                weight = self.graph[src][dst].get('strength', 0.0)
                edge_weights.append(weight)
            else:
                # Missing edge breaks the pentagon
                return {"valid": False, "phi_score": 0.0, "reason": "incomplete_cycle"}

        if len(edge_weights) < 5:
            return {"valid": False, "phi_score": 0.0, "reason": "insufficient_edges"}

        # Calculate ratios between consecutive edge weights
        ratios = []
        for i in range(5):
            w1 = edge_weights[i]
            w2 = edge_weights[(i + 1) % 5]

            if w2 > 0:  # Avoid division by zero
                ratios.append(w1 / w2)

        if not ratios:
            return {"valid": False, "phi_score": 0.0, "reason": "zero_weights"}

        # Check how many ratios are φ-compliant
        phi_compliant_count = sum(1 for r in ratios if self.is_phi_compliant(r))
        phi_score = phi_compliant_count / len(ratios)

        # Pentagon is considered valid if majority of ratios are φ-compliant
        is_valid = phi_score >= 0.6  # At least 60% of ratios must be φ-compliant

        return {
            "valid": is_valid,
            "phi_score": phi_score,
            "ratios": ratios,
            "phi_compliant_ratios": phi_compliant_count,
            "total_ratios": len(ratios),
            "edge_weights": edge_weights
        }

    def analyze_triangle_closures(self) -> Dict[str, int]:
        """
        Count triangle closure patterns for stability analysis.
        Triangles represent stable three-way relationships.
        """
        triangle_count = 0
        triangles = []

        # Find all 3-cycles (triangles)
        try:
            simple_cycles = list(nx.simple_cycles(self.graph))
            triangles = [cycle for cycle in simple_cycles if len(cycle) == 3]
            triangle_count = len(triangles)
        except nx.NetworkXError:
            pass

        return {
            "triangle_count": triangle_count,
            "triangles": triangles,
            "stability_indicator": triangle_count  # More triangles = more stability
        }

    def detect_spiral_patterns(self, node_positions: Dict[str, Tuple[float, float]]) -> List[Dict]:
        """
        Detect spiral patterns by fitting relationship paths to logarithmic curves.
        Spirals represent growth and evolutionary patterns.
        """
        spirals = []

        # Find paths of length 4+ and test for spiral patterns
        for start_node in self.graph.nodes():
            paths = nx.single_source_shortest_path(self.graph, start_node, cutoff=8)

            for end_node, path in paths.items():
                if len(path) >= 4:  # Minimum length for spiral detection
                    # Extract positions for path nodes
                    path_positions = []
                    for node in path:
                        if node in node_positions:
                            path_positions.append(node_positions[node])

                    if len(path_positions) >= 4:
                        # Test if positions follow logarithmic spiral pattern
                        spiral_fit = self._fit_logarithmic_spiral(path_positions)
                        if spiral_fit['r_squared'] > 0.8:  # Good fit threshold
                            spirals.append({
                                "path": path,
                                "positions": path_positions,
                                "spiral_params": spiral_fit,
                                "growth_factor": spiral_fit.get('growth_rate', 0.0)
                            })

        return spirals

    def _fit_logarithmic_spiral(self, positions: List[Tuple[float, float]]) -> Dict:
        """
        Fit positions to logarithmic spiral: r = a * e^(b*θ)
        Returns fit quality and parameters.
        """
        if len(positions) < 4:
            return {"r_squared": 0.0}

        try:
            # Convert Cartesian to polar coordinates
            polar_coords = []
            for x, y in positions:
                r = math.sqrt(x**2 + y**2)
                theta = math.atan2(y, x)
                if r > 0:  # Avoid log(0)
                    polar_coords.append((theta, math.log(r)))

            if len(polar_coords) < 3:
                return {"r_squared": 0.0}

            # Linear regression on log(r) vs θ
            thetas = np.array([coord[0] for coord in polar_coords])
            log_rs = np.array([coord[1] for coord in polar_coords])

            # Fit line: log(r) = log(a) + b*θ
            coeffs = np.polyfit(thetas, log_rs, 1)
            growth_rate = coeffs[0]  # b parameter
            log_a = coeffs[1]        # log(a)

            # Calculate R-squared
            predicted = np.polyval(coeffs, thetas)
            ss_res = np.sum((log_rs - predicted) ** 2)
            ss_tot = np.sum((log_rs - np.mean(log_rs)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

            return {
                "r_squared": r_squared,
                "growth_rate": growth_rate,
                "scale_factor": math.exp(log_a),
                "spiral_type": "logarithmic"
            }

        except (ValueError, ZeroDivisionError):
            return {"r_squared": 0.0}

    def comprehensive_pattern_analysis(self,
                                     node_positions: Optional[Dict[str, Tuple[float, float]]] = None) -> Dict:
        """
        Perform comprehensive Sacred Geometry pattern analysis on the relationship graph.
        """
        analysis = {
            "timestamp": np.datetime64('now'),
            "graph_stats": {
                "nodes": self.graph.number_of_nodes(),
                "edges": self.graph.number_of_edges(),
                "density": nx.density(self.graph)
            }
        }

        # Pentagon analysis (primary focus)
        pentagons = self.find_pentagon_cycles()
        pentagon_results = []

        for pentagon in pentagons:
            validation = self.validate_pentagon_phi_ratios(pentagon)
            pentagon_results.append({
                "nodes": pentagon,
                "validation": validation
            })

        valid_pentagons = [p for p in pentagon_results if p["validation"]["valid"]]

        analysis["pentagons"] = {
            "total_found": len(pentagons),
            "phi_compliant": len(valid_pentagons),
            "compliance_rate": len(valid_pentagons) / len(pentagons) if pentagons else 0,
            "details": pentagon_results
        }

        # Triangle stability analysis
        triangle_analysis = self.analyze_triangle_closures()
        analysis["triangles"] = triangle_analysis

        # Spiral pattern detection (if positions provided)
        if node_positions:
            spiral_analysis = self.detect_spiral_patterns(node_positions)
            analysis["spirals"] = {
                "patterns_found": len(spiral_analysis),
                "details": spiral_analysis
            }

        # Overall Sacred Geometry health score
        pentagon_score = len(valid_pentagons) / max(1, len(pentagons))
        triangle_score = min(1.0, triangle_analysis["triangle_count"] / max(1, self.graph.number_of_nodes() * 0.1))

        analysis["sacred_geometry_score"] = (pentagon_score * 0.6 + triangle_score * 0.4)

        return analysis
```

## Contextual Influence Calculation

### Dynamic Influence Engine

```python
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np

class ContextualInfluenceEngine:
    """
    Calculates dynamic contextual influence scores with time decay,
    confidence intervals, and multi-factor weighting.
    """

    def __init__(self,
                 default_decay_lambda: float = 0.02,  # 2% decay per day
                 confidence_threshold: float = 0.3):   # Minimum confidence for inclusion
        self.decay_lambda = default_decay_lambda
        self.confidence_threshold = confidence_threshold

    def calculate_influence(self,
                          edge: Dict,
                          current_time: datetime,
                          custom_decay: Optional[float] = None) -> float:
        """
        Calculate contextual influence score for a relationship edge.

        Formula: Influence = impact_weight × strength × confidence × time_decay

        Args:
            edge: Relationship edge with metadata
            current_time: Current timestamp for time decay calculation
            custom_decay: Optional override for decay lambda

        Returns:
            Influence score between 0 and 1
        """
        # Extract edge properties
        impact_weight = edge.get("impact_weight", 1.0)
        strength = edge.get("strength", 0.0)
        confidence = edge.get("confidence", 0.0)
        started_at = edge.get("started_at")

        # Skip low-confidence relationships
        if confidence < self.confidence_threshold:
            return 0.0

        # Calculate time decay
        time_decay = 1.0
        if started_at:
            if isinstance(started_at, str):
                started_at = datetime.fromisoformat(started_at.replace('Z', '+00:00'))

            dt = max(0, (current_time - started_at).days)
            decay_rate = custom_decay or self.decay_lambda
            time_decay = math.exp(-decay_rate * dt)

        # Calculate base influence
        influence = impact_weight * strength * confidence * time_decay

        # Apply signal quality boost for multi-validated relationships
        signals_passed = edge.get("signals_passed", 0)
        signals_required = edge.get("signals_required", 2)

        if signals_passed > signals_required:
            # Boost for relationships with strong multi-signal validation
            signal_boost = 1 + (0.1 * (signals_passed - signals_required))
            influence *= signal_boost

        return max(0.0, min(1.0, influence))

    def calculate_priority_score(self,
                               context: Dict,
                               edges: List[Dict],
                               current_time: datetime,
                               user_override: float = 0.0,
                               override_expiry: Optional[datetime] = None) -> Tuple[float, Dict]:
        """
        Calculate dynamic priority score for a context based on multiple factors.

        Priority = 0.35*urgency + 0.25*outcome_gain + 0.15*stakeholder_weight
                 - 0.15*risk_penalty + 0.05*freshness + 0.05*confidence + user_override

        Returns:
            (priority_score, score_breakdown)
        """
        # Extract context attributes
        urgency = self._extract_urgency(context, current_time)
        outcome_gain = self._extract_outcome_gain(context)
        stakeholder_weight = self._calculate_stakeholder_weight(context, edges)
        risk_penalty = self._calculate_risk_penalty(context)
        freshness = self._calculate_freshness(context, current_time)
        confidence = context.get("confidence", 0.8)

        # Apply time-limited user override
        effective_override = 0.0
        if user_override != 0.0 and override_expiry:
            if current_time <= override_expiry:
                effective_override = user_override

        # Calculate weighted priority score
        priority_score = (
            0.35 * urgency +
            0.25 * outcome_gain +
            0.15 * stakeholder_weight -
            0.15 * risk_penalty +
            0.05 * freshness +
            0.05 * confidence +
            effective_override
        )

        # Normalize to [0, 1] range
        priority_score = max(0.0, min(1.0, priority_score))

        score_breakdown = {
            "urgency": urgency,
            "outcome_gain": outcome_gain,
            "stakeholder_weight": stakeholder_weight,
            "risk_penalty": risk_penalty,
            "freshness": freshness,
            "confidence": confidence,
            "user_override": effective_override,
            "final_score": priority_score
        }

        return priority_score, score_breakdown

    def _extract_urgency(self, context: Dict, current_time: datetime) -> float:
        """Extract urgency score based on temporal constraints."""
        temporal_dim = context.get("dim_temporal", {})

        # Check for explicit deadlines
        deadline_str = temporal_dim.get("deadline")
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                days_until_deadline = (deadline - current_time).days

                if days_until_deadline < 0:
                    return 1.0  # Overdue - maximum urgency
                elif days_until_deadline <= 7:
                    return 0.9  # Within a week - high urgency
                elif days_until_deadline <= 30:
                    return 0.6  # Within a month - moderate urgency
                else:
                    return 0.3  # Future - low urgency
            except (ValueError, TypeError):
                pass

        # Fallback to priority level
        motivational_dim = context.get("dim_motivational", {})
        priority = motivational_dim.get("priority", "medium").lower()

        priority_map = {"critical": 1.0, "high": 0.8, "medium": 0.5, "low": 0.2}
        return priority_map.get(priority, 0.5)

    def _extract_outcome_gain(self, context: Dict) -> float:
        """Calculate expected outcome gain."""
        outcome_dim = context.get("dim_outcome", {})

        # Look for quantified value or impact
        impact_score = outcome_dim.get("impact_score", 0.5)
        value_rating = outcome_dim.get("value_rating", "medium")

        if isinstance(impact_score, (int, float)):
            return max(0.0, min(1.0, impact_score))

        # Fallback to qualitative rating
        value_map = {"critical": 1.0, "high": 0.8, "medium": 0.5, "low": 0.2}
        return value_map.get(value_rating.lower(), 0.5)

    def _calculate_stakeholder_weight(self, context: Dict, edges: List[Dict]) -> float:
        """Calculate stakeholder influence weight."""
        relational_dim = context.get("dim_relational", {})

        # Count high-influence stakeholders
        stakeholders = relational_dim.get("stakeholders", [])
        if not stakeholders:
            return 0.3  # Default low stakeholder weight

        # Weight by stakeholder influence levels
        total_weight = 0.0
        for stakeholder in stakeholders:
            if isinstance(stakeholder, dict):
                influence = stakeholder.get("influence_level", "medium")
                influence_map = {"executive": 1.0, "high": 0.8, "medium": 0.5, "low": 0.2}
                total_weight += influence_map.get(influence.lower(), 0.5)

        # Normalize by number of stakeholders
        return min(1.0, total_weight / len(stakeholders))

    def _calculate_risk_penalty(self, context: Dict) -> float:
        """Calculate risk penalty score."""
        risk_dim = context.get("dim_risk", {})

        risks = risk_dim.get("risks", [])
        if not risks:
            return 0.0  # No identified risks

        # Aggregate risk scores
        total_risk = 0.0
        for risk in risks:
            if isinstance(risk, dict):
                probability = risk.get("probability", 0.3)
                impact = risk.get("impact", 0.3)
                mitigation = risk.get("mitigation_effectiveness", 0.5)

                # Risk score = probability × impact × (1 - mitigation)
                risk_score = probability * impact * (1 - mitigation)
                total_risk += risk_score

        return min(1.0, total_risk / len(risks))

    def _calculate_freshness(self, context: Dict, current_time: datetime) -> float:
        """Calculate data freshness score."""
        updated_at = context.get("updated_at")
        if not updated_at:
            return 0.5  # No update timestamp

        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))

        days_old = (current_time - updated_at).days

        # Freshness decay - fully fresh for 1 day, then exponential decay
        if days_old <= 1:
            return 1.0
        else:
            return math.exp(-0.1 * days_old)  # 10% decay per day
```

## Minimum Viable Implementation

### Core MVP Components

Based on the research answers, the minimum viable implementation includes:

#### 1. Five Essential COF Dimensions
- **Motivational**: Goals, intent, success criteria
- **Relational**: Stakeholders, organizational structure
- **Temporal**: Deadlines, timelines, cadence
- **Resource**: Budgets, assets, capabilities
- **Outcome**: Targets, achievements, success metrics

#### 2. Four Relationship Types
- **depends_on**: Dependency relationships with blocking semantics
- **supports**: Positive influence relationships
- **conflicts_with**: Negative influence or contradiction relationships
- **influences**: General influence without specific positive/negative bias

#### 3. Basic Sacred Geometry Motifs
- **Triangle**: 3-cycle closure analysis for stability
- **Pentagon**: 5-cycle φ-ratio validation for harmony

#### 4. Core Infrastructure
- **Postgres + JSONB**: Hybrid relational/document storage
- **REST API**: Standard HTTP interface for CRUD operations
- **Basic UI**: Dimension checklist, simple graph visualization

### MVP Database Schema

```sql
-- Simplified MVP schema with 5 dimensions
CREATE TABLE contexts_mvp (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  summary TEXT,

  -- MVP: 5 essential dimensions
  dim_motivational JSONB,
  dim_relational   JSONB,
  dim_temporal     JSONB,
  dim_resource     JSONB,
  dim_outcome      JSONB,

  confidence REAL NOT NULL DEFAULT 0.8,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Simplified relationship table
CREATE TABLE context_edges_mvp (
  id BIGSERIAL PRIMARY KEY,
  src UUID NOT NULL REFERENCES contexts_mvp(id),
  dst UUID NOT NULL REFERENCES contexts_mvp(id),
  type TEXT NOT NULL CHECK (type IN ('depends_on', 'supports', 'conflicts_with', 'influences')),
  strength REAL NOT NULL CHECK (strength BETWEEN 0 AND 1),
  confidence REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Essential indexes
CREATE INDEX idx_contexts_mvp_title ON contexts_mvp(title);
CREATE INDEX idx_edges_mvp_src ON context_edges_mvp(src);
CREATE INDEX idx_edges_mvp_dst ON context_edges_mvp(dst);
```

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Set up Postgres database with MVP schema
- [ ] Implement basic CRUD operations for contexts and edges
- [ ] Create JSON Schema validation for 5 core dimensions
- [ ] Build simple REST API with FastAPI/Flask
- [ ] Add basic relationship creation and querying

### Phase 2: Intelligence (Weeks 3-4)
- [ ] Implement multi-signal relationship engine (semantic + statistical signals)
- [ ] Add basic Sacred Geometry pattern detection (triangles, pentagons)
- [ ] Implement contextual influence calculation engine
- [ ] Create dynamic priority scoring system
- [ ] Add basic completeness and validation checks

### Phase 3: Enhancement (Weeks 5-6)
- [ ] Expand to full 13-dimension COF framework
- [ ] Add bitemporal versioning and event sourcing
- [ ] Implement comprehensive Sacred Geometry analysis
- [ ] Create advanced multi-signal validation (all 5 signal types)
- [ ] Add user interface with graph visualization

### Phase 4: Production (Weeks 7-8)
- [ ] Performance optimization and caching
- [ ] Comprehensive testing and validation framework
- [ ] Security hardening and access control
- [ ] Documentation and deployment automation
- [ ] Monitoring and observability integration

## Success Metrics

### Objective Effectiveness Measures
- **Decision Quality Lift**: 15-30% improvement in decision outcome metrics
- **Time-to-Answer**: 40-60% reduction in analysis time vs manual methods
- **Insight Generation**: 3-5x increase in validated insights per analysis session
- **Calibration Accuracy**: >80% accuracy in relationship strength predictions

### Differentiation Validators
- **Query Efficiency**: <3 hops average vs 5-7 hops in generic graphs
- **Precision@K**: >85% precision for top-10 contextual recommendations
- **Decision Cycle Speed**: 2-3x faster decision cycles vs traditional approaches
- **Novel Insights**: Demonstrate motif-driven insights unavailable in existing tools

### Technical Performance Targets
- **Query Response**: <200ms for single-context queries, <1s for complex traversals
- **Scale**: Support 10K+ contexts with 100K+ relationships in MVP
- **Availability**: 99.9% uptime with graceful degradation
- **Data Quality**: >95% relationship validation accuracy

---

*This implementation architecture provides a comprehensive foundation for building ContextForge as a production-ready decision-oriented contextual analysis system with unique Sacred Geometry pattern recognition and multi-signal relationship validation capabilities.*
