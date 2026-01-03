# Sacred Geometry in TaskMan

Sacred Geometry provides a visual and conceptual framework for tracking work patterns in the ContextForge ecosystem. This guide explains how to use geometry shapes and stages to enhance task management and workflow visualization.

---

## Overview

The Sacred Geometry system in TaskMan consists of two complementary concepts:

1. **Geometry Shapes** - Five patterns representing different aspects of work
2. **Shape Stages** - Three phases within each shape representing lifecycle progress

Together, these form a 5×3 matrix of 15 possible states for categorizing and visualizing work.

---

## The Five Geometry Shapes

Each shape represents a fundamental pattern in work and development:

```
┌─────────────┬─────────────────────────────────────────────────────────────┐
│   Shape     │   Meaning                                                   │
├─────────────┼─────────────────────────────────────────────────────────────┤
│   Circle    │   Completeness, closure, holistic work                      │
│   Triangle  │   Stability, foundation, structured work                    │
│   Spiral    │   Iterative improvement, continuous progress                │
│   Pentagon  │   Harmony, balance, coordinated effort                      │
│   Fractal   │   Modularity, recursion, self-similar patterns              │
└─────────────┴─────────────────────────────────────────────────────────────┘
```

### Circle (○)

**Meaning:** Completeness and Closure

Use Circle for work that represents a complete, self-contained unit. Circle tasks are holistic - they encompass everything needed without external dependencies.

**Best for:**
- Full feature implementations
- Complete bug fixes with tests
- Documentation updates (all sections covered)
- Release cycles (start to finish)

**Example:**
```json
{
  "title": "Implement user authentication",
  "geometry_shape": "Circle",
  "description": "Complete auth system including login, logout, password reset, and session management"
}
```

### Triangle (△)

**Meaning:** Stability and Foundation

Use Triangle for foundational work that other tasks build upon. Triangle tasks create stable bases for future development.

**Best for:**
- Architecture decisions
- Core infrastructure setup
- Database schema design
- API contracts/interfaces
- Foundational libraries

**Example:**
```json
{
  "title": "Design database schema for user management",
  "geometry_shape": "Triangle",
  "description": "Foundation schema that authentication and authorization will build upon"
}
```

### Spiral (◎)

**Meaning:** Iterative Improvement

Use Spiral for work that improves over multiple passes. Spiral tasks expect refinement through iteration.

**Best for:**
- Performance optimization
- Refactoring efforts
- UI/UX improvements
- Algorithm tuning
- Feedback-driven enhancements

**Example:**
```json
{
  "title": "Optimize database query performance",
  "geometry_shape": "Spiral",
  "description": "Iterative improvement of slow queries - measure, optimize, repeat"
}
```

### Pentagon (⬠)

**Meaning:** Harmony and Balance

Use Pentagon for work requiring coordination between multiple elements. Pentagon tasks balance competing concerns.

**Best for:**
- Cross-team collaboration
- Multi-service integration
- Trade-off decisions
- Resource balancing
- Stakeholder alignment

**Example:**
```json
{
  "title": "Integrate payment processing across microservices",
  "geometry_shape": "Pentagon",
  "description": "Coordinate API, billing, notifications, and analytics services"
}
```

### Fractal (✳)

**Meaning:** Modularity and Recursion

Use Fractal for work that exhibits self-similar patterns at different scales. Fractal tasks can be decomposed into smaller, similar subtasks.

**Best for:**
- Component libraries
- Recursive algorithms
- Hierarchical structures
- Modular systems
- Pattern libraries

**Example:**
```json
{
  "title": "Build comment system with nested replies",
  "geometry_shape": "Fractal",
  "description": "Each comment can contain comments - same pattern at every level"
}
```

---

## The Three Shape Stages

Each geometry shape progresses through three stages:

```
┌──────────────┬─────────────────────────────────────────────────────────────┐
│   Stage      │   Description                                               │
├──────────────┼─────────────────────────────────────────────────────────────┤
│   foundation │   Initial setup and groundwork                              │
│   growth     │   Active development and expansion                          │
│   optimization│  Refinement and polish                                     │
└──────────────┴─────────────────────────────────────────────────────────────┘
```

### Foundation Stage

The beginning phase where groundwork is laid.

**Activities:**
- Requirements gathering
- Architecture planning
- Initial scaffolding
- Environment setup
- Research and exploration

**Transition to Growth:** When the basic structure exists and active development can begin.

### Growth Stage

The main development phase where functionality is built.

**Activities:**
- Feature implementation
- Core logic development
- Test writing
- Integration work
- Iteration based on feedback

**Transition to Optimization:** When functionality is complete and ready for polish.

### Optimization Stage

The refinement phase where quality is enhanced.

**Activities:**
- Performance tuning
- Code cleanup
- Documentation completion
- Edge case handling
- Final testing

**Completion:** Task is ready for review/release.

---

## Using Shapes and Stages Together

The combination of shape and stage creates a rich vocabulary for describing work:

```
                    ┌─────────────────────────────────────────────┐
                    │              Shape Stage                    │
                    ├───────────┬───────────┬───────────┬─────────┤
                    │ foundation│   growth  │optimization         │
┌───────┬───────────┼───────────┼───────────┼───────────┼─────────┤
│       │ Circle    │  Planning │ Building  │  Polishing│         │
│       │           │  holistic │ complete  │  complete │         │
│       │           │  approach │ feature   │  feature  │         │
│Shape  ├───────────┼───────────┼───────────┼───────────┼─────────┤
│       │ Triangle  │  Defining │ Building  │  Hardening│         │
│       │           │  foundation│ stable   │  stable   │         │
│       │           │           │ base      │  base     │         │
│       ├───────────┼───────────┼───────────┼───────────┼─────────┤
│       │ Spiral    │  First    │ Iterating │  Final    │         │
│       │           │  pass     │ and       │  refinement│        │
│       │           │           │ improving │           │         │
│       ├───────────┼───────────┼───────────┼───────────┼─────────┤
│       │ Pentagon  │  Aligning │ Coordinating│ Balancing│        │
│       │           │  stakeholders│ work   │  final    │         │
│       │           │           │           │  concerns │         │
│       ├───────────┼───────────┼───────────┼───────────┼─────────┤
│       │ Fractal   │  Defining │ Building  │  Unifying │         │
│       │           │  pattern  │ modules   │  modules  │         │
│       │           │           │           │           │         │
└───────┴───────────┴───────────┴───────────┴───────────┴─────────┘
```

---

## API Examples

### Creating a Task with Geometry

```json
POST /api/v1/tasks
{
  "title": "Implement caching layer",
  "project_id": "proj-123",
  "geometry_shape": "Spiral",
  "shape_stage": "foundation",
  "description": "Add Redis caching - will iterate on cache strategies"
}
```

### Creating an Action List with Geometry

```json
POST /api/v1/action-lists
{
  "title": "Authentication Sprint Tasks",
  "project_id": "proj-123",
  "geometry_shape": "Circle",
  "shape_stage": "growth",
  "items": [
    { "text": "Implement login endpoint", "order": 1 },
    { "text": "Add JWT token generation", "order": 2 },
    { "text": "Write authentication tests", "order": 3 }
  ]
}
```

### Updating Task Stage Progression

```json
PATCH /api/v1/tasks/task-456
{
  "shape_stage": "optimization"
}
```

### Filtering by Geometry

```
GET /api/v1/tasks?geometry_shape=Triangle&shape_stage=foundation
```

---

## MCP Tool Usage

The TaskMan MCP server exposes geometry fields through its tools:

### task_create

```javascript
await client.callTool({
  name: "task_create",
  arguments: {
    title: "Build component library",
    project_id: "proj-001",
    geometry_shape: "Fractal",
    shape_stage: "foundation"
  }
});
```

### task_list with Geometry Filter

```javascript
await client.callTool({
  name: "task_list",
  arguments: {
    project_id: "proj-001",
    geometry_shape: "Spiral"
  }
});
```

### action_list_create

```javascript
await client.callTool({
  name: "action_list_create",
  arguments: {
    title: "API Integration Checklist",
    project_id: "proj-001",
    geometry_shape: "Pentagon",
    shape_stage: "growth"
  }
});
```

---

## Validation Rules

### Valid Geometry Shapes

The following shapes are accepted (case-insensitive):

| Input | Normalized |
|-------|------------|
| `circle`, `CIRCLE`, `Circle` | `Circle` |
| `triangle`, `TRIANGLE`, `Triangle` | `Triangle` |
| `spiral`, `SPIRAL`, `Spiral` | `Spiral` |
| `pentagon`, `PENTAGON`, `Pentagon` | `Pentagon` |
| `fractal`, `FRACTAL`, `Fractal` | `Fractal` |

### Valid Shape Stages

| Input | Normalized |
|-------|------------|
| `foundation` | `foundation` |
| `growth` | `growth` |
| `optimization` | `optimization` |

### Error Responses

Invalid geometry shape:
```json
{
  "type": "https://taskman.api/errors/validation",
  "title": "Validation Error",
  "status": 400,
  "detail": "Invalid geometry shape: hexagon. Valid shapes: Circle, Triangle, Spiral, Pentagon, Fractal"
}
```

### Backward Compatibility

For backward compatibility, empty/null geometry values are accepted:
- `null`, `undefined`, `""` → Valid (no geometry assigned)

---

## Best Practices

### 1. Choose Shape Based on Work Nature

Ask yourself: "What is the fundamental pattern of this work?"
- **Is it self-contained?** → Circle
- **Does it create a foundation?** → Triangle
- **Will it improve iteratively?** → Spiral
- **Does it require coordination?** → Pentagon
- **Does it have recursive structure?** → Fractal

### 2. Progress Through Stages

Don't skip stages - each serves a purpose:
1. **Foundation**: Set yourself up for success
2. **Growth**: Build the core functionality
3. **Optimization**: Polish before delivery

### 3. Use Geometry for Visualization

When querying tasks, filter by geometry to visualize work patterns:
```javascript
// Find all foundation work (might be blocked by)
const foundations = await listTasks({ shape_stage: "foundation" });

// Find all iterative work (might need more cycles)
const spirals = await listTasks({ geometry_shape: "Spiral" });
```

### 4. Combine with Other Filters

Geometry works with other task properties:
```javascript
// High-priority foundation work
const criticalFoundations = await listTasks({
  shape_stage: "foundation",
  priority: "critical"
});
```

---

## Appendix: TypeScript Types

```typescript
enum GeometryShape {
  Circle = "Circle",
  Triangle = "Triangle",
  Spiral = "Spiral",
  Pentagon = "Pentagon",
  Fractal = "Fractal",
}

enum ShapeStage {
  Foundation = "foundation",
  Growth = "growth",
  Optimization = "optimization",
}

interface TaskWithGeometry {
  id: string;
  title: string;
  geometry_shape?: GeometryShape | null;
  shape_stage?: ShapeStage | null;
  // ... other fields
}
```

---

## Related Documentation

- [Task Schema Reference](../src/core/schemas.ts)
- [Action List Schema Reference](../src/core/schemas.ts)
- [Validation Functions](../src/validation/sacred-geometry.ts)
- [COF and UCL Definitions](../../docs/COF_and_UCL_Definitions.md)

---

*Sacred Geometry in TaskMan is inspired by the Context Ontology Framework (COF) principles of the ContextForge ecosystem.*
