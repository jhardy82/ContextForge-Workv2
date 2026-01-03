# Quantum Research Synthesis - API Best Practices 2024/2025

**Compiled By**: Quantum Research Team  
**Date**: 2025-12-04  
**Target**: `vs-code-task-manager/api-server.cjs`  
**Linear Issue**: CF-208 (Action List API)

---

## 📊 Executive Summary

After comprehensive internal and external research, this document synthesizes **actionable recommendations** for modernizing the TaskMan API implementation to align with 2024/2025 industry best practices.

### Research Coverage

| Persona | Sources Analyzed | Key Findings |
|---------|-----------------|--------------|
| **Dr. Archaeon** | 26 internal code excerpts | Existing patterns: Result monad, CRUD operations, minimal validation |
| **Navigator Flux** | 15+ external sources | Modern patterns: Zod validation, RFC 7807 errors, OpenAPI 3.1 |
| **Architect Prism** | Pattern synthesis | Gap analysis: Missing validation middleware, inconsistent error format |
| **Validator Echo** | Library benchmarks | Recommended stack: Express + Zod + RFC 7807 |

---

## 🏛️ Dr. Archaeon - Internal Archaeology Findings

### Existing Codebase Patterns

**Current `api-server.cjs` Analysis** (682 lines):

| Pattern | Location | Assessment |
|---------|----------|------------|
| **Express Setup** | Lines 1-30 | ✅ Good: cors, express.json middleware |
| **Error Handling** | Various | ⚠️ Inconsistent: Mix of `error` and `message` keys |
| **Validation** | None | ❌ Missing: No request validation middleware |
| **ID Generation** | Various | ⚠️ Inconsistent: `task-${Date.now()}-${uuid}` vs `P-${base36}` |
| **Response Format** | Various | ⚠️ Inconsistent: No standard envelope |
| **Timestamps** | Various | ✅ Good: ISO 8601 format |

**Identified Conventions**:
```javascript
// Convention 1: Field naming uses camelCase prefixed by entity type
taskId, taskTitle, taskStatus       // ✅ Consistent
projectId, projectName              // ✅ Consistent  
sprintId, sprintName                // ✅ Consistent

// Convention 2: Timestamps always ISO 8601
createdAt: new Date().toISOString()  // ✅ Good

// Convention 3: In-memory storage arrays
let tasks = [...], let projects = [...], let sprints = [...]  // For testing
```

**Technical Debt Identified**:
1. No request body validation (any data accepted)
2. No global error handler (errors leak implementation details)
3. Inconsistent error response format
4. No API versioning strategy documentation
5. No OpenAPI specification

---

## 🧭 Navigator Flux - External Research Findings

### 1. Express.js Best Practices 2024 (Context7: 94.2 benchmark)

**Global Error Handler Pattern**:
```javascript
// RECOMMENDED: Centralized error handling middleware
app.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  res.status(statusCode).json({
    error: err.message,
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
});
```

**Async Error Wrapper**:
```javascript
// RECOMMENDED: Automatic promise rejection handling
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

app.get('/api/resource', asyncHandler(async (req, res) => {
  const data = await fetchData(); // Errors auto-propagate to error handler
  res.json(data);
}));
```

### 2. Request Validation (express-validator: 92.5 benchmark)

**Imperative Validation Pattern**:
```typescript
import { body, param, validationResult } from 'express-validator';

// Reusable validation middleware
const validate = (validations) => {
  return async (req, res, next) => {
    await Promise.all(validations.map(v => v.run(req)));
    const errors = validationResult(req);
    if (errors.isEmpty()) return next();
    res.status(400).json({ errors: errors.array() });
  };
};

// Usage
app.post('/api/v1/tasks',
  validate([
    body('taskTitle').notEmpty().withMessage('Task title is required'),
    body('taskPriority').optional().isIn(['low', 'medium', 'high', 'urgent'])
  ]),
  asyncHandler(async (req, res) => { /* handler */ })
);
```

### 3. Zod Schema Validation (Context7: 90.4 benchmark)

**TypeScript-First Validation**:
```typescript
import { z } from 'zod';

// Define schema with type inference
const TaskSchema = z.object({
  taskTitle: z.string().min(1, 'Task title is required'),
  taskDescription: z.string().optional(),
  taskPriority: z.enum(['low', 'medium', 'high', 'urgent']).default('medium'),
  taskStatus: z.enum(['pending', 'in_progress', 'completed', 'blocked']).default('pending'),
  estimatedHours: z.number().positive().optional(),
});

// Extract TypeScript type
type Task = z.infer<typeof TaskSchema>;

// Validation middleware
const validateBody = (schema) => (req, res, next) => {
  const result = schema.safeParse(req.body);
  if (!result.success) {
    return res.status(400).json({
      type: 'https://api.example.com/problems/validation-error',
      title: 'Validation Error',
      status: 400,
      errors: result.error.issues
    });
  }
  req.body = result.data; // Use validated + transformed data
  next();
};
```

### 4. RFC 7807 Problem Details Standard

**Standard Error Format**:
```javascript
// RFC 7807 compliant error response
{
  "type": "https://api.taskman.dev/problems/task-not-found",
  "title": "Task Not Found",
  "status": 404,
  "detail": "No task exists with ID 'task-xyz-123'",
  "instance": "/api/v1/tasks/task-xyz-123"
}

// For validation errors
{
  "type": "https://api.taskman.dev/problems/validation-error",
  "title": "Validation Error",
  "status": 400,
  "detail": "Request body failed validation",
  "errors": [
    { "field": "taskTitle", "message": "Task title is required" },
    { "field": "taskPriority", "message": "Invalid priority value" }
  ]
}
```

**Implementation**:
```javascript
// Custom AppError class for RFC 7807
class AppError extends Error {
  constructor(statusCode, title, detail, type = null) {
    super(detail);
    this.statusCode = statusCode;
    this.title = title;
    this.detail = detail;
    this.type = type || `https://api.taskman.dev/problems/${title.toLowerCase().replace(/\s+/g, '-')}`;
  }
  
  toRFC7807() {
    return {
      type: this.type,
      title: this.title,
      status: this.statusCode,
      detail: this.detail
    };
  }
}
```

### 5. OpenAPI 3.1 Documentation

**swagger-jsdoc Integration**:
```javascript
const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

const swaggerSpec = swaggerJsdoc({
  definition: {
    openapi: '3.1.0',
    info: {
      title: 'TaskMan API',
      version: '1.0.0',
      description: 'VS Code Task Manager MCP API'
    },
    servers: [
      { url: 'http://localhost:3001', description: 'Development' }
    ]
  },
  apis: ['./routes/*.js'], // Path to JSDoc annotated files
});

app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

/**
 * @openapi
 * /api/v1/tasks:
 *   get:
 *     summary: List all tasks
 *     tags: [Tasks]
 *     parameters:
 *       - in: query
 *         name: status
 *         schema:
 *           type: string
 *           enum: [pending, in_progress, completed, blocked]
 *     responses:
 *       200:
 *         description: List of tasks
 *         content:
 *           application/json:
 *             schema:
 *               type: array
 *               items:
 *                 $ref: '#/components/schemas/Task'
 */
```

### 6. Rate Limiting (express-rate-limit)

**Recommended Configuration**:
```javascript
const rateLimit = require('express-rate-limit');

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per window
  standardHeaders: true, // Return rate limit info in headers
  legacyHeaders: false,
  message: {
    type: 'https://api.taskman.dev/problems/rate-limit-exceeded',
    title: 'Too Many Requests',
    status: 429,
    detail: 'Rate limit exceeded. Please try again later.'
  }
});

app.use('/api/', apiLimiter);
```

### 7. Response Envelope Pattern

**Consistent Success Response**:
```javascript
// Standard envelope for all responses
{
  "success": true,
  "data": { /* actual payload */ },
  "meta": {
    "timestamp": "2025-12-04T10:30:00Z",
    "requestId": "req-abc123"
  }
}

// For paginated lists
{
  "success": true,
  "data": [ /* items */ ],
  "meta": {
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 156,
      "totalPages": 8
    },
    "timestamp": "2025-12-04T10:30:00Z"
  }
}
```

---

## 🔮 Architect Prism - Pattern Synthesis

### Gap Analysis: Current vs. Recommended

| Pattern | Current State | Recommended | Priority |
|---------|---------------|-------------|----------|
| **Error Format** | Inconsistent `{error: "..."}` | RFC 7807 Problem Details | 🔴 P0 |
| **Validation** | None | Zod schema validation | 🔴 P0 |
| **Error Handler** | Per-route try/catch | Global error middleware | 🔴 P0 |
| **Response Envelope** | Raw data | `{success, data, meta}` | 🟠 P1 |
| **API Documentation** | None | OpenAPI 3.1 + Swagger UI | 🟠 P1 |
| **Rate Limiting** | None | express-rate-limit | 🟠 P1 |
| **Request Logging** | Console only | Structured logging | 🟡 P2 |
| **Health Check** | Basic | Detailed status + dependencies | 🟡 P2 |

### Recommended Implementation Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer Architecture                    │
├─────────────────────────────────────────────────────────────┤
│  Request → Rate Limit → Logging → Validation → Handler      │
│                                                             │
│  ┌─────────┐  ┌────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │ Express │→ │ Rate Limit │→ │ Zod Schemas │→ │ Handler │ │
│  └─────────┘  └────────────┘  └─────────────┘  └─────────┘ │
│                                                             │
│  Response ← Error Handler ← Response Envelope ← Handler     │
│                                                             │
│  ┌─────────┐  ┌────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │ RFC7807 │← │ AppError   │← │  Envelope   │← │ Result  │ │
│  └─────────┘  └────────────┘  └─────────────┘  └─────────┘ │
├─────────────────────────────────────────────────────────────┤
│  Documentation: OpenAPI 3.1 + Swagger UI at /api-docs       │
└─────────────────────────────────────────────────────────────┘
```

### Sacred Geometry Alignment

| Pattern | Geometry | Alignment |
|---------|----------|-----------|
| **RFC 7807 Errors** | Triangle (Stability) | ✅ Three-point structure: type, title, detail |
| **Zod Validation** | Circle (Completeness) | ✅ Full input/output type coverage |
| **Response Envelope** | Spiral (Iteration) | ✅ Consistent structure enables progressive enhancement |
| **OpenAPI Docs** | Fractal (Modularity) | ✅ Self-documenting, reusable patterns |

---

## 🔬 Validator Echo - Implementation Verification

### Recommended Dependencies

```json
{
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "zod": "^3.24.2",
    "uuid": "^9.0.0",
    "express-rate-limit": "^7.1.5",
    "swagger-ui-express": "^5.0.0",
    "swagger-jsdoc": "^6.2.8"
  }
}
```

### Quality Gates

| Gate | Metric | Target |
|------|--------|--------|
| **Type Coverage** | Zod schema inference | 100% |
| **Validation Coverage** | All POST/PUT endpoints | 100% |
| **Error Standardization** | RFC 7807 compliance | 100% |
| **Documentation** | OpenAPI completeness | ≥90% |
| **Response Consistency** | Envelope usage | 100% |

---

## 📋 Implementation Checklist

### Phase 1: Foundation (P0 - Critical)

- [ ] Create `AppError` class with RFC 7807 support
- [ ] Add global error handler middleware
- [ ] Create `asyncHandler` wrapper utility
- [ ] Define Zod schemas for all entity types (Task, Project, Sprint, ActionList)
- [ ] Create `validateBody` middleware using Zod

### Phase 2: Enhancement (P1 - High)

- [ ] Implement response envelope wrapper
- [ ] Add rate limiting middleware
- [ ] Set up swagger-jsdoc configuration
- [ ] Add OpenAPI annotations to all endpoints
- [ ] Configure Swagger UI at `/api-docs`

### Phase 3: Polish (P2 - Medium)

- [ ] Add request ID tracking (correlation IDs)
- [ ] Implement structured logging
- [ ] Enhance health endpoint with dependency checks
- [ ] Add pagination helpers for list endpoints
- [ ] Write comprehensive API tests

---

## 🎯 Next Steps

1. **Create Implementation PR** with Phase 1 changes
2. **Update Linear sub-issues** with specific implementation tasks
3. **Execute validation** with Validator Echo test suite
4. **Document ADRs** for architectural decisions made

---

**Synthesis Complete** ✅  
**Confidence**: 95%  
**Ready For**: Implementation Phase
