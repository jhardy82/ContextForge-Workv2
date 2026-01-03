**TaskMan MCP Server API v0.1.0**

***

# TaskMan MCP Server v2 (TypeScript)

**Model Context Protocol server providing API-based access to TaskMan-v2**

TypeScript implementation of the TaskMan MCP Server v2, featuring layered architecture, comprehensive validation, and extensive integration tests.

## Overview

This is the TypeScript implementation of the TaskMan MCP Server v2, integrated into the TaskMan-v2 project as a parallel implementation alongside the Python MCP server under `TaskMan-v2/mcp-server-ts/`.

### Integration Status

- **Core Implementation** (✅ Complete)
  - MCP protocol implementation via @modelcontextprotocol/sdk
  - Backend API client with axios and retries
  - Type-safe Zod schemas for all data structures
  - Layered architecture (config, core, features, transports)

- **TaskMan-v2 Integration** (✅ Complete)
  - Configured for TaskMan-v2 FastAPI backend (http://localhost:3001/api/v1)
  - Optional direct PostgreSQL access (172.25.14.122:5432/taskman_v2)
  - 24 validation test scripts (.mjs) for comprehensive testing
  - Isolated Node.js environment (node_modules)

### Key Differences from Python Implementation

| Feature | Python MCP | TypeScript MCP |
|---------|-----------|----------------|
| **Database Access** | Direct PostgreSQL | FastAPI REST API (primary) |
| **Sacred Geometry** | Implemented | Not implemented |
| **Rich UI** | Yes (Rich library) | No (focus on data) |
| **Testing** | 36 unit tests | 24 validation scripts |
| **Architecture** | FastMCP framework | Layered architecture |
| **Use Case** | Direct DB operations | API-mediated operations |

## Architecture

### TaskMan-v2 Integration

This MCP server coexists with TaskMan-v2's FastAPI REST API and Python MCP server:

```
TaskMan-v2/ (git submodule)
├── backend-api/          # FastAPI REST API (primary)
│   ├── alembic/          # Database migrations
│   ├── app/              # REST endpoints
│   └── .venv/            # Backend virtual environment
├── mcp-server/           # Python MCP Server (direct PostgreSQL)
│   ├── src/taskman_mcp/  # Python implementation
│   └── .venv/            # Python virtual environment
└── mcp-server-ts/        # TypeScript MCP Server ⬅️ THIS DIRECTORY
    ├── src/              # TypeScript implementation
    ├── dist/             # Compiled JavaScript
    ├── tests/            # Validation test scripts
    └── node_modules/     # Isolated Node environment
```

**Key Design Decisions**:

1. **API-First Approach**: Uses FastAPI REST endpoints as primary data source
   - Advantage: Leverages existing API validation and business logic
   - Fallback: Direct PostgreSQL access available if needed

2. **Type Safety**: Comprehensive Zod schemas for all data structures
   - Runtime validation of API responses
   - Compile-time TypeScript type checking
   - Schema-driven tool argument validation

3. **Validation-Focused Testing**: 24 .mjs validation scripts
   - End-to-end MCP protocol testing
   - Real database operations (requires backend running)
   - Comprehensive edge case coverage

### Project Structure

```
mcp-server-ts/
├── src/
│   ├── index.ts                    # Entry point
│   ├── config/                     # Runtime configuration
│   │   └── env.ts                  # Environment variables
│   ├── core/                       # Shared types and schemas
│   │   ├── schemas.ts              # Zod validation schemas
│   │   └── types.ts                # TypeScript interfaces
│   ├── features/                   # Domain features
│   │   ├── tasks/                  # Task management tools
│   │   │   ├── task-create.ts
│   │   │   ├── task-list.ts
│   │   │   ├── task-update.ts
│   │   │   └── task-delete.ts
│   │   ├── projects/               # Project tools
│   │   └── sprints/                # Sprint tools
│   ├── backend/                    # API client layer
│   │   └── client.ts               # Axios client with retries
│   ├── infrastructure/             # Cross-cutting concerns
│   │   ├── logging.ts              # Structured logging
│   │   └── audit.ts                # Audit trails
│   └── transports/                 # MCP transports
│       └── stdio.ts                # Standard I/O transport
├── tests/                          # Unit tests
│   ├── mcp/                        # MCP protocol tests
│   └── validate-*.mjs              # 24 validation scripts
├── dist/                           # Compiled output (built)
├── package.json                    # Dependencies and scripts
├── tsconfig.json                   # TypeScript configuration
├── .env                            # Environment config (gitignored)
├── .env.example                    # Environment template
└── README.md                       # This file
```

## Installation

### Prerequisites

- Node.js 20+
- npm or yarn
- TaskMan-v2 FastAPI backend running (http://localhost:3001)
- (Optional) PostgreSQL access for direct DB operations

### Setup Steps

1. **Navigate to directory**:
```bash
cd TaskMan-v2/mcp-server-ts
```

2. **Install dependencies**:
```bash
npm install
```

This installs:
- `@modelcontextprotocol/sdk` 1.20.2 (MCP protocol)
- `axios` 1.12.2 (HTTP client)
- `dotenv` 17.2.3 (environment config)
- `express` 5.1.0 (HTTP server)
- `zod` 3.25.76 (schema validation)
- Development tools: TypeScript, tsx, vitest

3. **Build the project**:
```bash
npm run build
```

This compiles TypeScript to JavaScript in the `dist/` directory.

## Configuration

### Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Backend API Base URL (TaskMan-v2 FastAPI backend)
BACKEND_API_URL=http://localhost:3001/api/v1

# PostgreSQL Direct Connection (optional, if bypassing backend API)
DB_HOST=172.25.14.122
DB_PORT=5432
DB_NAME=taskman_v2
DB_USER=contextforge
DB_PASSWORD=your_password_here

# MCP Server Settings
MCP_SERVER_NAME=TaskMan MCP Server (TypeScript)
LOG_LEVEL=info

# Node Environment
NODE_ENV=development
```

**Important**: The FastAPI backend must be running before starting this MCP server.

## Usage

### Running the MCP Server

**Development Mode** (with auto-reload):
```bash
npm run dev
```

**Production Mode** (compiled):
```bash
npm start
```

The server will:
1. Load environment configuration from `.env`
2. Initialize axios client for FastAPI backend
3. Register MCP tools for tasks, projects, and sprints
4. Start stdio transport (JSON-RPC over stdin/stdout)
5. Listen for MCP protocol messages

### Available Scripts

```bash
# Development
npm run dev              # Run with tsx (auto-reload)
npm run build            # Compile TypeScript to dist/
npm start                # Run compiled dist/index.js

# Testing
npm test                 # Run vitest unit tests
npm run test:watch       # Watch mode
npm run test:ui          # UI mode
npm run test:coverage    # With coverage

# Validation (requires backend running)
node tests/validate-task-create.mjs           # Test task creation
node tests/validate-all-task-tools.mjs        # Test all task tools
node tests/WORKING-comprehensive-validation.mjs  # Full validation suite

# Code Quality
npm run typecheck        # TypeScript type checking
```

### Available MCP Tools

#### Task Management

1. **task_create** - Create a new task via API
```json
{
  "title": "Implement feature X",
  "project_id": "P-abc123",
  "status": "new",
  "work_type": "task",
  "description": "Detailed description...",
  "priority": "high",
  "due_date": "2025-12-31",
  "owner": "username"
}
```

2. **task_list** - List tasks with filters
```json
{
  "project_id": "P-abc123",
  "status": "in_progress",
  "owner": "username",
  "limit": 50
}
```

3. **task_update** - Update existing task
```json
{
  "task_id": "T-xyz789",
  "status": "completed",
  "priority": "low",
  "description": "Updated description"
}
```

4. **task_delete** - Delete a task
```json
{
  "task_id": "T-xyz789"
}
```

**Note**: All operations go through the FastAPI backend, ensuring business logic consistency.

## Testing

### Unit Tests (Vitest)

The project uses Vitest for unit tests, but the test files need to be created in the appropriate locations (`src/**/*.test.ts`).

```bash
# Run unit tests
npm test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage
```

### Validation Scripts (.mjs)

The project includes 24 comprehensive validation scripts that test the MCP server end-to-end:

**Task Creation Validation**:
```bash
node tests/validate-task-create.mjs
```

Tests:
- Minimal required fields
- With description
- Priority variants (low, medium, high, critical)
- With owner
- Work type variants (task, bug, feature, epic, story)
- With due_date
- Error handling (missing fields)
- Edge cases (special characters)
- Response structure validation
- Cleanup (delete created tasks)

**Comprehensive Validation**:
```bash
node tests/WORKING-comprehensive-validation.mjs
```

Full test suite covering all MCP tools, resources, and edge cases.

**Prerequisites for Validation Scripts**:
1. TaskMan-v2 FastAPI backend must be running
2. PostgreSQL database must be accessible
3. Valid project ID must exist in database

### Test Results Format

```
╔═══════════════════════════════════════════════════════════╗
║       task_create - Comprehensive Validation             ║
╚═══════════════════════════════════════════════════════════╝

═══ Test 1: Minimal Required Fields ═══
✅ Minimal required fields: ID: T-abc123

═══ Test 2: With Description ═══
✅ With description: This is a test description

...

╔═══════════════════════════════════════════════════════════╗
║                    SUMMARY                                ║
╚═══════════════════════════════════════════════════════════╝

Total Tests: 25
✅ Passed:   25
❌ Failed:   0
Success:     100.0%
```

## Integration with Claude Code

### Configuration

Add the TypeScript MCP server to `.claude/settings.local.json`:

```json
{
  "mcpServers": {
    "taskman-typescript": {
      "command": "node",
      "args": ["dist/index.js"],
      "cwd": "${workspaceFolder}/TaskMan-v2/mcp-server-ts",
      "env": {
        "NODE_ENV": "production",
        "BACKEND_API_URL": "http://localhost:3001/api/v1"
      }
    }
  }
}
```

**Note**: Ensure the server is built (`npm run build`) before use.

### Usage in Claude Code

Once configured, Claude Code can invoke tools:

```typescript
// Create a task
await mcp.call("taskman-typescript:task_create", {
  title: "Fix authentication bug",
  project_id: "P-abc123",
  status: "new",
  work_type: "bug",
  priority: "critical"
});

// List tasks
const tasks = await mcp.call("taskman-typescript:task_list", {
  status: "in_progress",
  project_id: "P-abc123"
});

// Update task
await mcp.call("taskman-typescript:task_update", {
  task_id: "T-xyz789",
  status: "completed"
});
```

## Troubleshooting

### Backend Connection Issues

**Error**: `ECONNREFUSED` or `Network Error`

**Solutions**:
1. Verify FastAPI backend is running:
   ```bash
   # Check if backend is running
   curl http://localhost:3001/api/v1/health
   ```

2. Start the backend:
   ```bash
   cd TaskMan-v2/backend-api
   python -m uvicorn app.main:app --reload
   ```

3. Check `.env` configuration:
   ```env
   BACKEND_API_URL=http://localhost:3001/api/v1  # Verify this matches
   ```

### Build Issues

**Error**: `Cannot find module` after build

**Solution**: Rebuild the project:
```bash
npm run build
```

### TypeScript Errors

**Error**: Type checking failures

**Solutions**:
1. Run type checker:
   ```bash
   npm run typecheck
   ```

2. Fix errors in source files

3. Rebuild:
   ```bash
   npm run build
   ```

### Validation Script Failures

**Error**: Test timeouts or connection failures

**Solutions**:
1. Ensure backend is running
2. Verify database connection
3. Check project ID exists in test script
4. Increase timeout in validation script

## Development

### Adding New Tools

1. Create tool in `src/features/tasks/my-tool.ts`:

```typescript
import { z } from "zod";
import { backendClient } from "../../backend/client";

// Define input schema
const MyToolSchema = z.object({
  param1: z.string(),
  param2: z.number().optional(),
});

export async function myTool(args: unknown) {
  // Validate input
  const validated = MyToolSchema.parse(args);

  // Call backend API
  const response = await backendClient.post("/my-endpoint", validated);

  // Return result
  return {
    isError: false,
    content: [{
      type: "text",
      text: `Operation completed: ${response.data.id}`
    }],
    structuredContent: response.data
  };
}
```

2. Register in `src/index.ts`:

```typescript
import { myTool } from "./features/tasks/my-tool";

server.tool("my_tool", "Description of my tool", myTool);
```

3. Create validation script in `tests/validate-my-tool.mjs`

### Code Quality

Before committing:

1. Type check: `npm run typecheck`
2. Build: `npm run build`
3. Test: `npm test`
4. Validate: Run relevant validation scripts

## Version History

- **v0.1.0** (2025-10-30): Integrated with TaskMan-v2 FastAPI backend
  - Configured for TaskMan-v2 API endpoints
  - Added comprehensive .mjs validation scripts
  - Built and tested TypeScript compilation
  - Complete TaskMan-v2 integration documentation

## License

Part of the TaskMan-v2 project. See main repository for license details.

## Support

For issues, questions, or contributions, see the main TaskMan-v2 repository.
