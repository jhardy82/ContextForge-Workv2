# DTM Task Management VS Code Extension - PRD for GitHub Spark

## Overview

Build a VS Code extension that connects to the **Dynamic Task Manager (DTM)** API to provide a hierarchical task management interface directly within the VS Code sidebar. The extension enables developers to browse, view, and interact with Projects → Sprints → Tasks in a tree structure, with integrated AI prompt execution capabilities.

## Architecture Context

### DTM API Integration
- **Base API**: HTTP REST API running on `localhost:8000/api/v1`
- **Authentication**: JWT-based with token persistence
- **Health Check**: `/api/v1/health` endpoint for connection status
- **Current CLI Interface**: `cf_cli.py dtm` commands provide reference implementation

### Data Model Hierarchy (Current Implementation)
```
Projects (P-ALIAS-XXX) ✅ Available
├── Tasks (T-YYYYMMDD-XXX, T-DTM-XXX) ✅ Available
│   ├── Sacred Geometry Shape (Triangle, Circle, Spiral, Pentagon, etc.) ✅
│   ├── Status (new, in_progress, pending, completed, blocked) ✅
│   ├── Priority (low, medium, high, critical) ❌ Not in current API
│   └── Execution Prompts (Implementation, Testing, Validation) ❌ Not implemented

Note: Sprint management is NOT currently implemented in DTM API.
Sprints exist in the broader ContextForge ecosystem but not exposed via DTM endpoints.
```

### Sacred Geometry Framework
- **Triangle**: Stable foundations (high priority tasks)
- **Circle**: Unified workflows (integration tasks)
- **Spiral**: Iterative improvement (enhancement tasks)
- **Pentagon**: Harmonic resonance (optimization tasks)
- Shape-specific visual indicators and color coding

## Essential Features

### 1. Simplified Tree View (Phase 1 Implementation)
**Functionality**: Two-level expandable tree in VS Code sidebar (Sprint management deferred to Phase 2)
- **Projects Level**: Show all projects with expand/collapse ✅
- **Tasks Level**: Show all tasks under each project as child nodes ✅

**Future Enhancement (Phase 2)**: Add Sprint level between Projects and Tasks once DTM API implements sprint endpoints.**Visual Design**:
- Project icons: 📁 (folder icon)
- Sprint icons: 🎯 (target icon)
- Task icons: Based on Sacred Geometry shape (△ ○ 🌀 ⬟)
- Status color coding: 🟢 completed, 🟡 in_progress, 🔴 blocked, ⚪ new
- Hierarchical indentation with expand/collapse arrows

**API Integration** (Updated for Current Reality):
```typescript
// Currently Available Endpoints:
GET /api/projects -> get all projects ✅
GET /api/tasks -> get all tasks ✅
GET /api/tasks/{id} -> get single task ✅
POST /api/tasks -> create new task ✅
PUT /api/tasks/{id} -> update task ✅

// Missing Endpoints (Future Implementation):
GET /api/projects/{id}/sprints -> NOT IMPLEMENTED ❌
GET /api/sprints/{id}/tasks -> NOT IMPLEMENTED ❌
GET /api/sprints/{id} -> NOT IMPLEMENTED ❌
```### 2. Object Detail Viewer
**Functionality**: Modal or panel view showing complete object details
- **Project View**: ID, name, description, status, created_at, sprints_count
- **Sprint View**: ID, name, project_id, status, start_date, end_date, tasks_count
- **Task View**: Full JSON including title, description, status, priority, shape, prompts

**Implementation**:
- Click any tree item opens detail view
- JSON-formatted display with syntax highlighting
- Copy-to-clipboard functionality for any field
- "Refresh" button to reload data from API

### 3. AI Prompt Integration (Modified Approach)
**Functionality**: Send context-aware prompts to VS Code Chat and GitHub Copilot
- **Current Limitation**: Tasks don't contain pre-defined execution prompts in DTM API
- **Alternative Approach**: Generate prompts from task metadata
  - Implementation: "Help me implement: [task.title] - [task.description]"
  - Testing: "Create tests for: [task.title] with [task.shape] pattern"
  - Validation: "Validate implementation of: [task.title] with status [task.status]"
- **Prompt Composition**: Automatically include full task context (title, description, shape, status)**User Experience**:
```
Task Detail View:
┌─────────────────────────────────────┐
│ Task: T-DTM-001                     │
│ Title: CF-Enhanced Integration      │
│ Shape: Circle | Status: in_progress │
│                                     │
│ [Send Implementation Prompt] 🤖     │
│ [Send Testing Prompt] 🧪           │
│ [Send Validation Prompt] ✅         │
└─────────────────────────────────────┘
```

**API Integration** (Updated):
- Generate prompts from available task data: `task.title`, `task.description`, `task.shape`, `task.status`
- Compose contextual prompt: `${task.title}: ${task.description}\n\nShape: ${task.shape}\nStatus: ${task.status}\n\n[Generated prompt for implementation/testing/validation]`
- Send to VS Code Chat API or GitHub Copilot Chat API

### 4. Real-time Status Updates
**Functionality**: Auto-refresh tree view when DTM data changes
- **Polling Strategy**: Check DTM API every 30 seconds for updates
- **Change Detection**: Compare timestamps/versions to detect changes
- **Visual Feedback**: Loading spinners, success/error notifications

**Status Indicators**:
- 🟢 DTM API Connected
- 🟡 DTM API Connecting
- 🔴 DTM API Disconnected
- ⏳ Refreshing data...

## Technical Specifications

### VS Code Extension Architecture
```typescript
// Extension entry point
export function activate(context: vscode.ExtensionContext) {
    // Register tree data provider
    const dtmProvider = new DTMTreeProvider();
    vscode.window.createTreeView('dtmTaskManager', {
        treeDataProvider: dtmProvider
    });

    // Register commands
    vscode.commands.registerCommand('dtm.refreshTasks', () => dtmProvider.refresh());
    vscode.commands.registerCommand('dtm.showTaskDetails', (task) => showTaskDetails(task));
    vscode.commands.registerCommand('dtm.sendToChat', (prompt) => sendToVSCodeChat(prompt));
}
```

### DTM API Client
```typescript
interface DTMApiClient {
    // Health check
    checkHealth(): Promise<{ status: string; version: string; uptime: number }>;

    // Data retrieval
    getProjects(): Promise<Project[]>;
    getProject(id: string): Promise<Project>;
    getSprints(projectId: string): Promise<Sprint[]>;
    getTasks(sprintId: string): Promise<Task[]>;
    getTask(id: string): Promise<Task>;

    // Authentication
    authenticate(): Promise<boolean>;
    isAuthenticated(): boolean;
}
```

### Data Models
```typescript
interface Project {
    id: string;           // P-ALIAS-XXX format
    name: string;
    description?: string;
    status: 'active' | 'inactive' | 'completed';
    created_at: string;
    sprints?: Sprint[];
}

interface Sprint {
    id: string;           // S-YYYY-MM-DD format
    name: string;
    project_id: string;
    status: 'planned' | 'active' | 'completed';
    start_date?: string;
    end_date?: string;
    tasks?: Task[];
}

interface Task {
    id: string;           // T-YYYYMMDD-XXX or T-DTM-XXX format
    title: string;
    description?: string;
    status: 'new' | 'in_progress' | 'pending' | 'completed' | 'blocked';
    priority?: 'low' | 'medium' | 'high' | 'critical';  // May not be present in API
    shape?: 'Triangle' | 'Circle' | 'Spiral' | 'Pentagon' | 'Fractal';  // May not be present
    created_at: string;
    updated_at?: string;
    // Note: execution_prompts not implemented in current DTM API
    // Will be generated client-side from available task data
}
```

## User Experience Flow

### Initial Setup
1. User installs extension from VS Code Marketplace
2. Extension appears in Activity Bar as "DTM Tasks" 📋
3. First activation prompts for DTM API connection settings
4. Health check validates connection → shows green/red status indicator

### Daily Workflow
1. **Browse Hierarchy**: Click to expand Projects → Sprints → Tasks
2. **View Details**: Click any item to see full JSON in detail panel
3. **AI Assistance**: Click "Send to Chat" buttons to get AI help for specific tasks
4. **Stay Updated**: Tree automatically refreshes to show latest status changes

### Error Handling
- **Connection Failures**: Show retry button, fallback to cached data if available
- **Authentication Issues**: Prompt for re-authentication, clear expired tokens
- **API Errors**: Display user-friendly error messages with diagnostic info

## Known Gaps and Limitations

### **Phase 1 Limitations (Current DTM API)**
🔴 **Sprint Management**: No sprint endpoints available - hierarchical tree will be Projects → Tasks only
🔴 **Task Priority Field**: May not be present in all task objects from API
🔴 **Sacred Geometry Shape**: May not be present in all task objects from API
🔴 **Pre-defined Execution Prompts**: Not stored in DTM API - must be generated client-side
🔴 **Real-time Updates**: No WebSocket support - polling only
🔴 **Batch Operations**: No bulk task update endpoints available

### **Authentication Limitations**
🟡 **Mock JWT**: Current DTM server uses mock authentication - no real security
🟡 **Token Persistence**: Extension will need to handle token storage/refresh locally

### **Data Model Gaps**
🟡 **Project-Task Relationship**: No explicit project_id field in current task model
🟡 **Task Dependencies**: No dependency relationships available
🟡 **Task Assignment**: No assignee field in current API
🟡 **Task Phases**: No implementation/testing/validation phase tracking

### **Future Enhancements Required (Phase 2)**
- Sprint management endpoints (`/api/sprints`, `/api/projects/{id}/sprints`)
- Task-to-project relationship mapping
- Real authentication and authorization
- WebSocket support for real-time updates
- Bulk operations endpoints
- Task editing capabilities in extension UI
- Pre-defined execution prompt storage

### **Workarounds for Phase 1**
1. **No Sprints**: Group tasks under projects directly
2. **Missing Fields**: Handle gracefully with fallback values
3. **Generated Prompts**: Create AI prompts from available task data
4. **Polling Updates**: Use 30-second intervals instead of real-time
5. **Read-Only**: Focus on viewing/browsing rather than editing

## Success Criteria

### Core Functionality (Updated for Phase 1)
- ✅ Tree view displays Projects → Tasks hierarchy (Sprint level deferred)
- ✅ All available object data shows in detail view when clicked
- ✅ Generated AI prompts send to VS Code Chat with task context
- ✅ Polling-based status updates work within 30-second intervals
- ✅ Connection status indicator shows DTM API health

### User Experience (Updated)
- ✅ Intuitive navigation matches VS Code explorer patterns
- ✅ Sacred Geometry shapes display when available (graceful fallback to generic icons)
- ✅ Connection status is always visible and accurate
- ✅ Error states provide actionable guidance
- ✅ Missing data fields handled gracefully without breaking UI### Performance
- ✅ Initial load completes within 3 seconds
- ✅ Tree operations (expand/collapse) respond within 500ms
- ✅ API calls include proper timeout and retry logic
- ✅ Memory usage remains under 50MB during normal operation

## Package.json Configuration

```json
{
    "name": "dtm-task-manager",
    "displayName": "DTM Task Manager",
    "description": "Connect to Dynamic Task Manager API for hierarchical task management",
    "version": "1.0.0",
    "engines": { "vscode": "^1.80.0" },
    "categories": ["Other"],
    "activationEvents": ["onView:dtmTaskManager"],
    "main": "./out/extension.js",
    "contributes": {
        "views": {
            "explorer": [{
                "id": "dtmTaskManager",
                "name": "DTM Tasks",
                "icon": "$(checklist)",
                "contextualTitle": "DTM Task Manager"
            }]
        },
        "commands": [{
            "command": "dtm.refreshTasks",
            "title": "Refresh",
            "icon": "$(refresh)"
        }, {
            "command": "dtm.showTaskDetails",
            "title": "Show Details"
        }, {
            "command": "dtm.sendToChat",
            "title": "Send to Chat",
            "icon": "$(comment-discussion)"
        }],
        "configuration": {
            "title": "DTM Task Manager",
            "properties": {
                "dtm.apiUrl": {
                    "type": "string",
                    "default": "http://localhost:8000/api/v1",
                    "description": "DTM API base URL"
                },
                "dtm.refreshInterval": {
                    "type": "number",
                    "default": 30,
                    "description": "Auto-refresh interval in seconds"
                }
            }
        }
    }
}
```

## Dependencies

```json
{
    "dependencies": {
        "axios": "^1.5.0",           // HTTP client for DTM API calls
        "jsonwebtoken": "^9.0.0"     // JWT token handling
    },
    "devDependencies": {
        "@types/vscode": "^1.80.0",
        "@types/node": "^18.0.0",
        "typescript": "^5.0.0"
    }
}
```

## **Recommendation: Phased Development Approach**

### **Phase 1: MVP (Recommended for GitHub Spark)**
- **Scope**: Projects → Tasks tree view with current DTM API
- **Features**: View tasks, show details, generated AI prompts, connection status
- **Timeline**: 2-3 weeks (achievable with current infrastructure)
- **Value**: Immediate usability with existing DTM setup

### **Phase 2: Enhanced Features** (Future)
- **Prerequisites**: DTM API enhancements (sprint endpoints, task editing, real auth)
- **Features**: Full Projects → Sprints → Tasks hierarchy, task editing, real-time updates
- **Timeline**: Additional 2-3 weeks after API enhancements

### **GitHub Spark Prompt Recommendation**
Focus the GitHub Spark prompt on **Phase 1 MVP** with clear callouts about missing features and graceful handling of incomplete data. This ensures a working extension that can be enhanced later.

---

**Complexity Level**: Light-Medium Application (simplified from original scope due to API limitations)

**Development Time Estimate**: 2-3 weeks for initial implementation, 1 week for testing and refinement

**Key Differentiators**:
- Direct integration with ContextForge DTM ecosystem
- Sacred Geometry visual indicators
- AI prompt execution with full task context
- Real-time hierarchical task management within VS Code
