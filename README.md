# ContextForge-Workv2

> Full-stack task management and context orchestration platform with AI-powered workflow automation.

## Overview

ContextForge-Workv2 is a monorepo containing:

- **Backend API** - FastAPI server with PostgreSQL database
- **Frontend** - React 19 + Vite 6 + TypeScript 5.7
- **VS Code Extension** - Task management integration
- **MCP Servers** - Model Context Protocol implementations (Python & TypeScript)
- **cf-core** - Shared domain library

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.11+
- pnpm 9+
- uv (Python package manager)
- PostgreSQL 15+

### Installation

```bash
# Clone the repository
git clone https://github.com/Jacintalama/ContextForge-Workv2.git
cd ContextForge-Workv2

# Install Node.js dependencies
pnpm install

# Install Python dependencies
uv sync

# Start development servers
pnpm dev
```

## Project Structure

```
ContextForge-Workv2/
├── apps/
│   ├── backend-api/         # FastAPI server
│   ├── frontend/            # React 19 + Vite 6
│   ├── vscode-extension/    # VS Code extension
│   ├── mcp-server-py/       # Python MCP server
│   └── mcp-server-ts/       # TypeScript MCP server
├── packages/
│   ├── cf-core/             # Domain library
│   ├── unified-logger/      # Logging framework
│   └── shared-utils/        # Common utilities
├── docs/                    # Documentation library
├── tools/                   # Build and deployment tools
└── .github/                 # CI/CD workflows and Copilot agents
```

## Development

### Backend (FastAPI)

```bash
cd apps/backend-api
uv sync
uvicorn main:app --reload
```

### Frontend (React)

```bash
cd apps/frontend
pnpm install
pnpm dev
```

### Running Tests

```bash
# Python tests
uv run pytest

# TypeScript/JavaScript tests
pnpm test
```

## Documentation

See the [docs/](docs/) directory for comprehensive documentation.

## License

MIT
