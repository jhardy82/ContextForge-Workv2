# Action List Client Implementation Plan

**Status**: 🚧 PENDING IMPLEMENTATION
**Priority**: P1 (High)
**Estimated Time**: 30 minutes
**Dependencies**: MCP serverSampling fix (completed)

---

## Executive Summary

The TaskManager MCP server has a **4-layer architecture** for tool implementation:
1. ✅ Tool Declaration (MCP schema)
2. ✅ Request Handler (CallToolRequestSchema)
3. ✅ Handler Method (executeActionListCreate, etc.)
4. ❌ **Client API Method (MISSING)**

**Problem**: Action list tools are declared and handled but have no corresponding client API methods in the `TaskManagerClient` class.

**Impact**: All 8 action list tools fail with "Client method not found" errors:
- action_list_create
- action_list_get
- action_list_list
- action_list_update
- action_list_delete
- action_list_add_item
- action_list_remove_item
- action_list_toggle_item

**Solution**: Implement 8 missing client methods following the established pattern from working tools.

---

## Architecture Analysis

### Working Tool Example: `list_tasks`

**Layer 1: Tool Declaration** (index.ts:1169)
```typescript
{
  name: "task_manager_list_tasks",
  description: "List tasks with optional filtering",
  inputSchema: {
    type: "object",
    properties: {
      status: { type: "string", enum: ["pending", "in_progress", "completed"] },
      priority: { type: "string", enum: ["low", "medium", "high", "urgent"] }
      // ... more properties
    }
  }
}
```

**Layer 2: Request Handler** (index.ts:2301)
```typescript
this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  switch (name) {
    case "task_manager_list_tasks":
      return await this.handleListTasks(args);
    // ... other cases
  }
});
```

**Layer 3: Handler Method** (index.ts:2545)
```typescript
private async handleListTasks(args: any): Promise<any> {
  try {
    const result = await this.client.listTasks(args);
    return { content: [{ type: "text", text: JSON.stringify(result) }] };
  } catch (error) {
    // Error handling
  }
}
```

**Layer 4: Client API Method** (index.ts:645) ✅ **EXISTS**
```typescript
async listTasks(params: {
  status?: string;
  priority?: string;
  type?: string;
  assignee?: string;
  projectId?: string;
  sprintId?: string;
} = {}): Promise<any> {
  const queryParams = new URLSearchParams();
  if (params.status) queryParams.append('status', params.status);
  // ... more parameters
  
  const response = await fetch(`${this.baseURL}/tasks?${queryParams}`);
  return response.json();
}
```

### Broken Tool Example: `action_list_create`

**Layer 1: Tool Declaration** (index.ts:1943) ✅
```typescript
{
  name: "action_list_create",
  description: "Create a new action list with optional items",
  inputSchema: {
    type: "object",
    properties: {
      name: { type: "string", description: "Action list name" },
      description: { type: "string" },
      owner: { type: "string" },
      items: { type: "array" }
      // ... more properties
    },
    required: ["name"]
  }
}
```

**Layer 2: Request Handler** (index.ts:2301) ✅
```typescript
case "action_list_create":
  return await this.handleActionListCreate(args);
```

**Layer 3: Handler Method** (index.ts:3075) ✅
```typescript
private async handleActionListCreate(args: any): Promise<any> {
  try {
    const result = await this.client.createActionList(args);
    return { content: [{ type: "text", text: JSON.stringify(result) }] };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error creating action list: ${error.message}`
      }],
      isError: true
    };
  }
}
```

**Layer 4: Client API Method** ❌ **MISSING**
```typescript
// Should exist after line 1100 but DOES NOT
async createActionList(data: ActionListCreateInput): Promise<ActionListResponse> {
  // IMPLEMENTATION MISSING
}
```

---

## Implementation Plan

### Phase 1: Define TypeScript Interfaces (5 minutes)

Add after line 80 in `mcp-servers/task-manager/src/index.ts`:

```typescript
// Action List Interfaces
interface ActionListItem {
  id?: string;
  content: string;
  completed?: boolean;
  order?: number;
}

interface ActionListCreateInput {
  name: string;
  description?: string;
  owner?: string;
  priority?: string;
  status?: 'active' | 'completed' | 'archived';
  tags?: string[];
  project_id?: string;
  sprint_id?: string;
  notes?: string;
  items?: ActionListItem[];
}

interface ActionListUpdateInput {
  name?: string;
  description?: string;
  owner?: string;
  priority?: string;
  status?: 'active' | 'completed' | 'archived';
  tags?: string[];
  notes?: string;
}

interface ActionListFilters {
  status?: string;
  owner?: string;
  project_id?: string;
  sprint_id?: string;
  tags?: string[];
}

interface ActionListResponse {
  id: string;
  name: string;
  description?: string;
  owner?: string;
  status: string;
  created_at: string;
  updated_at: string;
  items: ActionListItem[];
}
```

### Phase 2: Implement Client Methods (20 minutes)

Add after line 1100 in `TaskManagerClient` class:

```typescript
// ====================================
// ACTION LIST OPERATIONS
// ====================================

/**
 * Create a new action list
 */
async createActionList(data: ActionListCreateInput): Promise<ActionListResponse> {
  const response = await fetch(`${this.baseURL}/action-lists`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to create action list');
  }
  
  return response.json();
}

/**
 * Get action list by ID
 */
async getActionList(id: string): Promise<ActionListResponse> {
  const response = await fetch(`${this.baseURL}/action-lists/${id}`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || `Action list ${id} not found`);
  }
  
  return response.json();
}

/**
 * List action lists with optional filters
 */
async listActionLists(filters: ActionListFilters = {}): Promise<ActionListResponse[]> {
  const queryParams = new URLSearchParams();
  
  if (filters.status) queryParams.append('status', filters.status);
  if (filters.owner) queryParams.append('owner', filters.owner);
  if (filters.project_id) queryParams.append('project_id', filters.project_id);
  if (filters.sprint_id) queryParams.append('sprint_id', filters.sprint_id);
  if (filters.tags?.length) {
    filters.tags.forEach(tag => queryParams.append('tags', tag));
  }
  
  const url = `${this.baseURL}/action-lists${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
  const response = await fetch(url);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to list action lists');
  }
  
  return response.json();
}

/**
 * Update action list
 */
async updateActionList(id: string, data: ActionListUpdateInput): Promise<ActionListResponse> {
  const response = await fetch(`${this.baseURL}/action-lists/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || `Failed to update action list ${id}`);
  }
  
  return response.json();
}

/**
 * Delete action list
 */
async deleteActionList(id: string): Promise<void> {
  const response = await fetch(`${this.baseURL}/action-lists/${id}`, {
    method: 'DELETE'
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || `Failed to delete action list ${id}`);
  }
}

/**
 * Add item to action list
 */
async addActionListItem(listId: string, item: ActionListItem): Promise<ActionListResponse> {
  const response = await fetch(`${this.baseURL}/action-lists/${listId}/items`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(item)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || `Failed to add item to action list ${listId}`);
  }
  
  return response.json();
}

/**
 * Remove item from action list
 */
async removeActionListItem(listId: string, itemId: string): Promise<ActionListResponse> {
  const response = await fetch(`${this.baseURL}/action-lists/${listId}/items/${itemId}`, {
    method: 'DELETE'
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || `Failed to remove item ${itemId} from action list ${listId}`);
  }
  
  return response.json();
}

/**
 * Toggle action list item completion status
 */
async toggleActionListItem(listId: string, itemId: string): Promise<ActionListResponse> {
  const response = await fetch(`${this.baseURL}/action-lists/${listId}/items/${itemId}/toggle`, {
    method: 'POST'
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || `Failed to toggle item ${itemId} in action list ${listId}`);
  }
  
  return response.json();
}
```

### Phase 3: Rebuild and Test (5 minutes)

**Rebuild**:
```bash
cd mcp-servers/task-manager
npm run build
```

**Expected Output**:
```
> task-manager-mcp@1.0.0 build
> esbuild src/index.ts --bundle --platform=node --outfile=dist/index.js --external:@modelcontextprotocol/sdk

  dist/index.js  108.5kb  # Should increase from 104kb due to new methods
```

**Reload VS Code**:
```
Ctrl+Shift+P → Developer: Reload Window
```

---

## Testing Plan

### Test 1: Create Action List
```
@workspace Create an action list named "MCP Implementation Tasks" with owner "engineering-team" and status "active"
```

**Expected Response**:
```json
{
  "id": "AL-001",
  "name": "MCP Implementation Tasks",
  "owner": "engineering-team",
  "status": "active",
  "created_at": "2025-12-04T...",
  "items": []
}
```

### Test 2: Add Items to Action List
```
@workspace Add item "Implement client methods" to action list AL-001
```

**Expected**: Item added, list returned with 1 item

### Test 3: Toggle Item Completion
```
@workspace Toggle completion for item 1 in action list AL-001
```

**Expected**: Item marked completed

### Test 4: List Action Lists
```
@workspace List all action lists with status active
```

**Expected**: Returns array including AL-001

### Test 5: Get Action List Details
```
@workspace Get details for action list AL-001
```

**Expected**: Full action list object with all items

### Test 6: Update Action List
```
@workspace Update action list AL-001 to set status completed
```

**Expected**: Action list status changed to completed

### Test 7: Remove Item
```
@workspace Remove item 1 from action list AL-001
```

**Expected**: Item removed, list returned without it

### Test 8: Delete Action List
```
@workspace Delete action list AL-001
```

**Expected**: Action list deleted successfully

---

## API Endpoint Verification

Before implementation, verify TaskManager API has these endpoints:

```bash
# Check API documentation or test endpoints
curl http://localhost:3001/api/action-lists
curl http://localhost:3001/api/action-lists/AL-001
curl -X POST http://localhost:3001/api/action-lists -H "Content-Type: application/json" -d '{"name":"Test"}'
```

**If endpoints don't exist**, action list functionality needs to be implemented in the API first.

---

## Error Handling Strategy

### Pattern from Working Tools

```typescript
async methodName(params): Promise<ResponseType> {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Default error message');
    }
    
    return response.json();
  } catch (error) {
    // Error propagates to handler method
    // Handler method catches and returns MCP error format
    throw error;
  }
}
```

### Common Errors to Handle

1. **404 Not Found**: Action list ID doesn't exist
2. **400 Bad Request**: Invalid input data
3. **500 Server Error**: API backend issue
4. **Network Error**: API not reachable

---

## Integration with Existing Code

### No Breaking Changes Required

All changes are **additive**:
- ✅ New interfaces added (no existing code modified)
- ✅ New methods added to client class (existing methods unchanged)
- ✅ Handlers already exist and call these methods
- ✅ Tool declarations already exist

### Code Review Checklist

- [ ] TypeScript interfaces match API contracts
- [ ] All 8 methods implemented with correct signatures
- [ ] Error handling follows established pattern
- [ ] Query parameter building matches existing tools
- [ ] HTTP methods correct (GET/POST/PUT/DELETE)
- [ ] Response parsing consistent
- [ ] No TypeScript compilation errors
- [ ] esbuild bundle successful

---

## Success Criteria

### Definition of Done

- [ ] All 8 action list client methods implemented
- [ ] TypeScript interfaces defined and correct
- [ ] Code compiles without errors
- [ ] MCP server rebuilt successfully (bundle size ~108kb)
- [ ] VS Code reloaded
- [ ] All 8 test scenarios pass
- [ ] No "method not found" errors
- [ ] Action lists create/read/update/delete work
- [ ] Items add/remove/toggle work
- [ ] Documentation updated

### Metrics

**Before Implementation**:
- ❌ 0/8 action list tools working
- ❌ "Client method not found" errors
- ❌ 39/47 task-manager tools functional (83%)

**After Implementation**:
- ✅ 8/8 action list tools working
- ✅ No method errors
- ✅ 47/47 task-manager tools functional (100%)

---

## Rollback Plan

If implementation causes issues:

**Step 1: Revert Code Changes**
```bash
cd mcp-servers/task-manager
git diff src/index.ts  # Review changes
git checkout src/index.ts  # Revert if needed
```

**Step 2: Rebuild Previous Version**
```bash
npm run build
```

**Step 3: Reload VS Code**
```
Ctrl+Shift+P → Developer: Reload Window
```

**Step 4: Verify**
Test that other task-manager tools still work (list_tasks, create_task, etc.)

---

## Related Issues

**Linear Issues**:
- CF-208: "🔍 Investigate TaskMan Action List API 404 Error" (In Progress)
  - This implementation addresses the MCP client side
  - API side may also need verification

**GitHub PR**:
- #78: feat(CF-130/CF-191): Enhanced Test Suite + TaskSettings + Workspace Sync
  - Consider including action list implementation in this PR

---

## Timeline

**Total Estimated Time**: 30 minutes

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 1 | Define TypeScript interfaces | 5 min | ⏳ Pending |
| 2 | Implement 8 client methods | 20 min | ⏳ Pending |
| 3 | Rebuild and reload VS Code | 2 min | ⏳ Pending |
| 4 | Test all 8 scenarios | 10 min | ⏳ Pending |
| 5 | Documentation update | 5 min | ⏳ Pending |

**Total**: ~42 minutes (includes testing)

---

## Next Steps

### Immediate
1. ⏳ Copy interface definitions to `src/index.ts` after line 80
2. ⏳ Copy client methods to `TaskManagerClient` class after line 1100
3. ⏳ Run `npm run build` to compile
4. ⏳ Reload VS Code window
5. ⏳ Execute Test 1 (create action list)

### Follow-up
6. ⏳ Complete all 8 test scenarios
7. ⏳ Update Linear CF-208 with implementation details
8. ⏳ Add action list examples to documentation
9. ⏳ Consider adding action list unit tests
10. ⏳ Verify API endpoints exist and work correctly

---

**Status**: Ready for implementation
**Blocker**: None (MCP serverSampling fix completed)
**Owner**: ContextForge Engineering Team
**Last Updated**: 2025-12-04
