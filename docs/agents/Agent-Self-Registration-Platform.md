# Agent Self-Registration Platform

## Overview

The Agent Self-Registration Platform is a comprehensive system for managing AI agents with gamification features, complement agent creation, and Sacred Geometry integration. This platform is fully integrated into the dbcli.py unified CLI system.

## Features

### Core Functionality
- **Agent Registration**: Register new agents with capabilities, specializations, and Sacred Geometry affinity
- **Complement Creation**: Automatically generate complement agents with inverted characteristics
- **Gamification System**: Points, levels, badges, and leaderboards for agent performance tracking
- **Activity Logging**: Track agent activities and automatically award points based on complexity
- **Sacred Geometry Integration**: Classify agents by geometric affinity (Triangle, Circle, Spiral, Fractal, Pentagon, Dodecahedron)

### Storage and Persistence
- **Agent Contracts**: JSON files stored in `contracts/agents/` directory
- **Gamification Events**: JSONL logging to `build/artifacts/gamify.jsonl`
- **Directory Structure**: Automatic creation of required directories
- **Unified Logging**: Integration with the UnifiedLogger system

## Command Reference

### Agent Registration
```bash
# Register a new agent
dbcli agent register --name "GitHub Copilot" --model "gpt-4-turbo" \
  --capabilities "code_analysis,code_generation,task_planning" \
  --specializations "powershell,python,documentation" \
  --geometry "Triangle"
```

### Agent Information
```bash
# Show detailed agent information
dbcli agent whoami --id AGENT-F54FD80A

# Show agent information in JSON format
dbcli agent whoami --id AGENT-F54FD80A --json
```

### Agent Listing
```bash
# List all agents
dbcli agent list

# List agents with JSON output
dbcli agent list --json

# Filter agents by status
dbcli agent list --status active
```

### Complement Creation
```bash
# Create a complement agent with inverted characteristics
dbcli agent complement --source AGENT-F54FD80A

# Create complement with JSON output
dbcli agent complement --source AGENT-F54FD80A --json
```

### Gamification Features
```bash
# Show leaderboard
dbcli agent leaderboard --limit 10

# Log agent activity
dbcli agent activity --id AGENT-F54FD80A --activity "task_completed" \
  --description "Implemented feature X" --complexity 2.5

# Show leaderboard in JSON format
dbcli agent leaderboard --limit 5 --json
```

## Gamification System

### Points and Levels
- **Points**: Earned through various activities with complexity multipliers
- **Levels**:
  - Initiate (0-99 points)
  - Apprentice (100-499 points)
  - Practitioner (500-999 points)
  - Expert (1000-2499 points)
  - Master (2500-4999 points)
  - Grandmaster (5000+ points)

### Activity Point Values
- `task_completed`: 10 points (base)
- `code_review`: 5 points
- `bug_fix`: 15 points
- `feature_implementation`: 20 points
- `documentation`: 8 points
- `test_creation`: 12 points
- `architecture_design`: 25 points

Points are multiplied by complexity factor (1.0-3.0+).

### Badges
- **First Registration**: Awarded upon initial agent registration
- **Complement Creator**: Awarded when creating complement agents
- **Custom Badges**: Can be awarded through the activity logging system

## Sacred Geometry Integration

Agents are classified by geometric affinity that reflects their working style and approach:

- **Triangle**: Stable foundation work, validation, testing
- **Circle**: Integration work, unified workflows, completion
- **Spiral**: Iterative improvement, progressive enhancement
- **Fractal**: Modular reuse, component-based architecture
- **Pentagon**: Harmony orchestration, balanced approaches
- **Dodecahedron**: Complete system integration, complexity management

## Complement Agent System

Complement agents are automatically generated with inverted characteristics:

### Geometry Inversions
- Triangle ↔ Circle
- Spiral ↔ Fractal
- Pentagon ↔ Dodecahedron

### Capability Inversions
- code_analysis ↔ code_generation
- task_planning ↔ task_execution
- architectural_design ↔ implementation_detail
- quality_assurance ↔ rapid_prototyping

### Specialization Inversions
- frontend ↔ backend
- database ↔ api_integration
- testing ↔ deployment

## Data Structures

### Agent Contract
```json
{
  "agent_id": "AGENT-12345678",
  "name": "Agent Name",
  "model": "gpt-4-turbo",
  "capabilities": ["code_analysis", "code_generation"],
  "specializations": ["python", "documentation"],
  "geometry_affinity": "Triangle",
  "registration_timestamp": "2025-08-29T17:19:38.189728+00:00",
  "status": "active",
  "gamification": {
    "points": 150,
    "streak": 5,
    "badges": [...],
    "level": "Apprentice",
    "achievements": []
  },
  "activity_log": [...],
  "complement_agents": [...]
}
```

### Complement Agent Contract
```json
{
  "agent_id": "COMP-87654321",
  "name": "Agent Name Complement Agent",
  "model": "complement",
  "complement_of": "AGENT-12345678",
  "relationship_type": "inverted_dimensions",
  ...
}
```

## Integration with ContextForge

The Agent Self-Registration Platform follows ContextForge Universal Methodology principles:

- **Host Policy**: PythonHelper (analytics/governance automation)
- **Logging First**: Comprehensive event logging with UnifiedLogger
- **Sacred Geometry**: Shape-based classification and workflow integration
- **Dual-Format Output**: Rich console display and JSON for automation
- **Evidence Collection**: Activity logging and gamification event tracking

## File Structure

```
contracts/
  agents/
    AGENT-*.agent.json        # Agent contract files
    COMP-*.agent.json         # Complement agent contracts

docs/
  agents/
    *.md                      # Agent profile documentation

build/
  artifacts/
    gamify.jsonl              # Gamification event log

python/
  agents/
    agent_cli.py              # Agent CLI implementation
    __init__.py               # Package initialization
```

## Error Handling

The platform includes comprehensive error handling:

- **Validation**: Input validation for all agent data
- **Recovery**: Graceful handling of missing files or corrupted data
- **Logging**: Detailed error logging with context and remediation suggestions
- **Exit Codes**: Standard exit codes for automation integration

## Future Enhancements

Planned features for future versions:

- **Team Formation**: Automatic team assembly based on complement relationships
- **Performance Analytics**: Detailed metrics and trend analysis
- **Achievement System**: Complex achievement unlocking based on activity patterns
- **Integration APIs**: REST API endpoints for external system integration
- **Agent Templates**: Predefined agent templates for common roles

## Examples

### Complete Workflow Example
```bash
# 1. Register primary agent
dbcli agent register --name "GitHub Copilot" --model "gpt-4-turbo" \
  --capabilities "code_analysis,code_generation" --geometry "Triangle"

# 2. Create complement agent
dbcli agent complement --source AGENT-F54FD80A

# 3. Log some activities
dbcli agent activity --id AGENT-F54FD80A --activity "feature_implementation" \
  --description "Built agent platform" --complexity 3.0

# 4. Check leaderboard
dbcli agent leaderboard --limit 5

# 5. Get detailed agent info
dbcli agent whoami --id AGENT-F54FD80A
```

This platform provides a complete foundation for agent management, gamification, and Sacred Geometry-based workflow integration within the ContextForge Universal Methodology framework.
