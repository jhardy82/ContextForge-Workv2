# VS Code Task Manager - Local Deployment & API Integration Guide

## 🏗️ Local Deployment Options

Based on the repository analysis, you have several deployment options:

### Option 1: Local Development Setup (Recommended)
This is a full-stack React + Node.js application with three components:

1. **Dashboard**: React app with Vite (Port 5173)
2. **API Server**: Express.js REST API (Port 3000/3001)
3. **VS Code Extension**: TypeScript extension

### Option 2: Use GitHub-hosted Version
1. **Open your web browser** and navigate to:
   ```url
   https://vs-code-task-manager--jhardy82.github.app
   ```

2. **Authentication:**
   - Uses GitHub Spark platform with built-in authentication
   - Sign in with your GitHub credentials
   - Authorize the VS Code Task Manager app if prompted

## 🚀 Quick Local Deployment

### Prerequisites
```bash
# Required tools
node --version  # v18+ recommended
npm --version   # Latest
git --version   # For cloning
```

### Step 1: Clone and Setup
```bash
# Clone the repository
git clone https://github.com/jhardy82/vs-code-task-manager.git
cd vs-code-task-manager

# Install dependencies for all components
npm install

# Install API server dependencies
cd api-server && npm install && cd ..

# Install VS Code extension dependencies
cd src/extension && npm install && cd ../..
```

### Step 2: Start Services
```bash
# Option A: Start all services with VS Code tasks
# Open in VS Code: code .
# Press Ctrl+Shift+P → "Tasks: Run Task" → "Start Full Development Stack"

# Option B: Manual startup (3 terminals)
# Terminal 1: Dashboard
npm run dev

# Terminal 2: API Server
npm run api:start

# Terminal 3: Extension (development)
cd src/extension && npm run watch
```

### Step 3: Access Applications
- **Dashboard**: http://localhost:5173
- **API Server**: http://localhost:3000/api
- **Extension**: Press `F5` in VS Code for Extension Development Host

## 📡 API Integration Details

### REST API Endpoints
The task manager provides a comprehensive REST API for integration:

#### Core Task Management
```bash
# Health check
GET /api/health

# Get all tasks (with filtering)
GET /api/tasks?status=in-progress&limit=10

# Get specific task
GET /api/tasks/{taskId}

# Create new task
POST /api/tasks
# Body: { "taskName": "...", "taskDescription": "...", "taskType": "task" }

# Update task
PUT /api/tasks/{taskId}
# Body: { "taskStatus": "in-progress" }

# Delete task
DELETE /api/tasks/{taskId}
```

#### Phase Management
```bash
# Update single phase
PUT /api/tasks/{taskId}/phase/{phase}
# Body: { "status": "completed" }

# Update multiple phases
PUT /api/tasks/{taskId}/phases
# Body: { "implementation": "completed", "testing": "in-progress" }

# Get phase status
GET /api/tasks/{taskId}/phases

# Reset all phases
POST /api/tasks/{taskId}/phases/reset
```

#### Bulk Operations & Statistics
```bash
# Import multiple tasks
POST /api/bulk-import
# Body: { "tasks": [{ "taskName": "...", "taskType": "task" }] }

# Get statistics
GET /api/statistics
```

### Task Data Schema
```json
{
  "taskId": "task-1234567890-abc123",
  "taskName": "System Resource Optimization",
  "taskDescription": "Optimize memory usage and disk space",
  "taskType": "task",
  "parentTrackingElement": "Performance Improvements",
  "taskImplementationPrompt": "Guide for implementation",
  "taskTestingPrompt": "Testing approach",
  "taskValidationPrompt": "Validation criteria",
  "taskStatus": "in-progress",
  "phases": {
    "implementation": "completed",
    "testing": "in-progress",
    "validation": "pending",
    "review": "pending"
  },
  "dependencies": [],
  "childTasks": [],
  "deliverables": ["Optimized system", "Performance report"],
  "dtmLink": "https://external-tracker.com/task-123",
  "createdAt": "2025-09-26T10:00:00Z",
  "updatedAt": "2025-09-26T12:00:00Z"
}
```

## 🔧 VS Code Extension Setup

### Install Extension Locally
```bash
# Build and install extension
cd vs-code-task-manager/src/extension
npm install
npm run compile
npx vsce package
code --install-extension *.vsix
```

### Configure Extension
1. **Open VS Code Settings** (`Ctrl+,`)
2. **Search for "Task Manager"**
3. **Configure settings:**
   - `taskManager.apiEndpoint`: `http://localhost:3000/api`
   - `taskManager.autoRefresh`: `true`
   - `taskManager.showPhaseDetails`: `true`

### Extension Features
- **Task Tree View**: View tasks in Explorer sidebar
- **Command Palette Integration**: `Ctrl+Shift+P` → "Task Manager: ..."
- **Context Menus**: Right-click tasks for actions
- **VS Code Chat Integration**: Send task prompts to GitHub Copilot Chat

## 💾 Data Import/Export Options

### Using Your System Analysis Data

Based on your system analysis (Correlation ID: 3a32c0d7), here's how to import your tasks:

#### API Import (Recommended for Local Deployment)
```bash
# Import your system optimization tasks
curl -X POST http://localhost:3000/api/bulk-import \
  -H "Content-Type: application/json" \
  -d '{
    "tasks": [
      {
        "taskName": "Memory Optimization",
        "taskDescription": "Reduce memory usage from 81.5% to <75%",
        "taskType": "task",
        "parentTrackingElement": "System Resource Optimization",
        "taskStatus": "planned",
        "deliverables": ["Close unused Chrome tabs", "Optimize VS Code workspaces"],
        "dtmLink": "correlation_id=3a32c0d7"
      },
      {
        "taskName": "Storage Space Recovery",
        "taskDescription": "Increase free space from 18.3% to >25%",
        "taskType": "task",
        "parentTrackingElement": "System Resource Optimization",
        "taskStatus": "planned",
        "deliverables": ["Run Disk Cleanup", "Clear temporary files"],
        "dtmLink": "correlation_id=3a32c0d7"
      }
    ]
  }'
```

### Step 2: Manual Task Creation (GitHub-hosted Version)

#### Option A: Manual Task Creation
Copy and paste from `system_analysis_task_summary.md`:

**High Priority Tasks:**
```markdown
✅ Memory Optimization
   - Close unused Chrome tabs (1,850+ MB)
   - Optimize VS Code workspaces (5,500+ MB)
   - Review background applications

✅ Storage Space Recovery
   - Run Disk Cleanup utility
   - Clear temporary files
   - Move large files to external storage
```

**Medium Priority Tasks:**
```markdown
✅ Process Management
   - Review Memory Compression (3,173 MB)
   - Consolidate browser processes
   - Close unused VS Code instances
```

#### Option B: JSON Import (if supported)
If the task manager supports JSON import, here's the structured data:

```json
{
  "project": "System Resource Optimization",
  "correlation_id": "3a32c0d7",
  "health_score": 75,
  "tasks": [
    {
      "id": "memory-opt-001",
      "title": "Memory Optimization",
      "priority": "HIGH",
      "status": "pending",
      "description": "Reduce memory usage from 81.5% to <75%",
      "subtasks": [
        "Close unused Chrome tabs (1,850+ MB)",
        "Optimize VS Code workspaces (5,500+ MB)",
        "Review background applications"
      ],
      "expected_savings": "15-25% memory reduction"
    },
    {
      "id": "storage-opt-001",
      "title": "Storage Space Recovery",
      "priority": "HIGH",
      "status": "pending",
      "description": "Increase free space from 18.3% to >25%",
      "subtasks": [
        "Run Disk Cleanup utility",
        "Clear temporary files",
        "Move large files to external storage"
      ],
      "expected_outcome": "60+ GB free space"
    }
  ]
}
```

### Step 3: Set Up Tracking

1. **Create Project:** "System Resource Optimization"
2. **Set Correlation ID:** 3a32c0d7 (for linking with analysis logs)
3. **Configure Priorities:**
   - HIGH: Memory & Storage optimization
   - MEDIUM: Process management
   - LOW: Monitoring setup

4. **Set Deadlines:**
   - Immediate actions: Today (next 15 minutes)
   - Short-term: Tomorrow (next hour)
   - Long-term: Next week

### Step 4: Progress Tracking Metrics

Track these key performance indicators:
- **Memory Usage:** Target <75% (currently 81.5%)
- **Disk Free Space:** Target >25% (currently 18.3%)
- **System Health Score:** Target >85 (currently 75)
- **Top Memory Processes:** Monitor reduction

### Step 5: Integration Options

If you want AI assistance with task management:

1. **Screenshots:** Take screenshots of the task manager interface - I can help optimize task structure
2. **Export Data:** If the app allows data export, I can analyze progress and suggest improvements
3. **API Access:** Check if the app has API documentation for automated updates

## 🏗️ Architecture & Deployment Notes

### Technology Stack
- **Frontend**: React 18 + TypeScript + Vite + TailwindCSS
- **Backend**: Node.js + Express.js REST API
- **Database**: GitHub Spark KV store (cloud) or SQLite (local)
- **Extension**: VS Code Extension API + TypeScript
- **Hosting**: GitHub Spark platform (cloud deployment)

### Local Development vs Production
```bash
# Local Development Ports
Dashboard:  http://localhost:5173  # Vite dev server
API:        http://localhost:3000  # Express server
Extension:  Extension Development Host

# Production (GitHub-hosted)
App:        https://vs-code-task-manager--jhardy82.github.app
API:        Integrated with Spark platform
Extension:  Connects to hosted API
```

### Integration Testing
```bash
# Test API connectivity
curl http://localhost:3000/api/health

# Test task creation
curl -X POST http://localhost:3000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"taskName": "Test Task", "taskType": "task"}'

# Run synchronization test
node test-synchronization.js
```

## 🚀 Recommended Next Steps

### For Your System Optimization Project

1. **Choose Deployment Method:**
   - **Quick Start**: Use GitHub-hosted version (sign in required)
   - **Full Control**: Deploy locally for API integration with your analyzer

2. **Import Your Data:**
   - Use the API endpoints above to import your 15 optimization tasks
   - Set correlation ID `3a32c0d7` in the `dtmLink` field for traceability

3. **VS Code Integration:**
   - Install the extension for seamless workflow
   - Configure API endpoint to match your deployment
   - Use task prompts with GitHub Copilot Chat

4. **Progress Tracking:**
   - Set target metrics: Memory <75%, Disk >25%, Health Score >85
   - Use phase management for implementation → testing → validation → review
   - Track deliverables completion

## 📞 Support & Troubleshooting

### Common Issues
- **Port Conflicts**: Change ports in `vite.config.ts` or API server config
- **Extension Not Loading**: Run `npm run compile` in extension directory
- **API Connection**: Verify CORS settings and server status
- **GitHub Authentication**: Check app permissions in GitHub settings

### Resources
- **Repository**: https://github.com/jhardy82/vs-code-task-manager
- **API Documentation**: See `api-tests.http` in repository
- **Extension Guide**: `EXTENSION_INSTALLATION.md`
- **Setup Guide**: `SETUP_GUIDE.md`

---
**Generated:** September 26, 2025
**For Project:** System Resource Analysis (Correlation ID: 3a32c0d7)
**Integration:** VS Code Task Manager API & Local Deployment
