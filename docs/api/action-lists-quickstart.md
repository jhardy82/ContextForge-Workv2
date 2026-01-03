# ActionList API Quick Start Guide

Get started with the TaskMan v2 ActionList API in minutes with practical examples and workflows.

---

## Prerequisites

Before you begin, ensure you have:

- [ ] TaskMan v2 backend running (default: `http://localhost:8002`)
- [ ] Valid JWT authentication token (see [Authentication Guide](./action-lists-authentication.md))
- [ ] API client (curl, Postman, or HTTP library)

---

## Your First Action List

### Step 1: Authenticate

Obtain a JWT token for API access:

**Request**:
```bash
curl -X POST http://localhost:8002/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo-user",
    "password": "demo-password"
  }'
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Save your token**:
```bash
export JWT_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### Step 2: Create Your First Action List

Create a simple action list with a title and description:

**Request**:
```bash
curl -X POST http://localhost:8002/api/v1/action-lists \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "AL-my-first-list",
    "title": "My First Action List",
    "description": "Learning the ActionList API",
    "owner": "demo-user",
    "priority": "medium"
  }'
```

**Response**:
```json
{
  "id": "AL-my-first-list",
  "title": "My First Action List",
  "description": "Learning the ActionList API",
  "status": "active",
  "owner": "demo-user",
  "tags": [],
  "project_id": null,
  "sprint_id": null,
  "items": [],
  "priority": "medium",
  "created_at": "2025-12-28T10:00:00Z",
  "updated_at": "2025-12-28T10:00:00Z",
  "completed_at": null
}
```

✅ **Success!** You've created your first action list.

---

### Step 3: View Your Action List

Retrieve the action list you just created:

**Request**:
```bash
curl -X GET http://localhost:8002/api/v1/action-lists/AL-my-first-list \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Response**:
```json
{
  "id": "AL-my-first-list",
  "title": "My First Action List",
  "description": "Learning the ActionList API",
  "status": "active",
  "owner": "demo-user",
  "tags": [],
  "items": [],
  "created_at": "2025-12-28T10:00:00Z",
  "updated_at": "2025-12-28T10:00:00Z"
}
```

---

## Common Workflows

### Workflow 1: Create List with Checklist Items

Create an action list with pre-populated checklist items:

**Request**:
```bash
curl -X POST http://localhost:8002/api/v1/action-lists \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "AL-sprint-tasks",
    "title": "Sprint 2025-Q1 Tasks",
    "description": "Backend API implementation checklist",
    "owner": "backend-team",
    "project_id": "PROJ-001",
    "sprint_id": "SPRINT-2025-Q1",
    "tags": ["api", "backend", "sprint-1"],
    "priority": "high",
    "due_date": "2025-12-31T23:59:59Z",
    "items": [
      {
        "text": "Implement JWT authentication",
        "completed": false,
        "order": 0
      },
      {
        "text": "Create CRUD endpoints for ActionLists",
        "completed": false,
        "order": 1
      },
      {
        "text": "Write API documentation",
        "completed": false,
        "order": 2
      },
      {
        "text": "Add integration tests",
        "completed": false,
        "order": 3
      }
    ]
  }'
```

**Response**:
```json
{
  "id": "AL-sprint-tasks",
  "title": "Sprint 2025-Q1 Tasks",
  "description": "Backend API implementation checklist",
  "status": "active",
  "owner": "backend-team",
  "project_id": "PROJ-001",
  "sprint_id": "SPRINT-2025-Q1",
  "tags": ["api", "backend", "sprint-1"],
  "priority": "high",
  "due_date": "2025-12-31T23:59:59Z",
  "items": [
    {"text": "Implement JWT authentication", "completed": false, "order": 0},
    {"text": "Create CRUD endpoints for ActionLists", "completed": false, "order": 1},
    {"text": "Write API documentation", "completed": false, "order": 2},
    {"text": "Add integration tests", "completed": false, "order": 3}
  ],
  "created_at": "2025-12-28T10:05:00Z",
  "updated_at": "2025-12-28T10:05:00Z"
}
```

---

### Workflow 2: Update Action List

Mark checklist items as completed by updating the action list:

**Request**:
```bash
curl -X PATCH http://localhost:8002/api/v1/action-lists/AL-sprint-tasks \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "text": "Implement JWT authentication",
        "completed": true,
        "order": 0
      },
      {
        "text": "Create CRUD endpoints for ActionLists",
        "completed": true,
        "order": 1
      },
      {
        "text": "Write API documentation",
        "completed": false,
        "order": 2
      },
      {
        "text": "Add integration tests",
        "completed": false,
        "order": 3
      }
    ]
  }'
```

**Response**:
```json
{
  "id": "AL-sprint-tasks",
  "title": "Sprint 2025-Q1 Tasks",
  "items": [
    {"text": "Implement JWT authentication", "completed": true, "order": 0},
    {"text": "Create CRUD endpoints for ActionLists", "completed": true, "order": 1},
    {"text": "Write API documentation", "completed": false, "order": 2},
    {"text": "Add integration tests", "completed": false, "order": 3}
  ],
  "updated_at": "2025-12-28T14:30:00Z"
}
```

---

### Workflow 3: List Action Lists with Filtering

Query action lists with filters and pagination:

**Example 1: Filter by status**
```bash
curl -X GET "http://localhost:8002/api/v1/action-lists?status=active&page=1&per_page=20" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Example 2: Filter by owner**
```bash
curl -X GET "http://localhost:8002/api/v1/action-lists?owner=backend-team" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Example 3: Filter by project and sprint**
```bash
curl -X GET "http://localhost:8002/api/v1/action-lists?project_id=PROJ-001&sprint_id=SPRINT-2025-Q1" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Response**:
```json
{
  "action_lists": [
    {
      "id": "AL-sprint-tasks",
      "title": "Sprint 2025-Q1 Tasks",
      "status": "active",
      "owner": "backend-team",
      "project_id": "PROJ-001",
      "sprint_id": "SPRINT-2025-Q1",
      "created_at": "2025-12-28T10:05:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20,
  "has_more": false
}
```

---

### Workflow 4: Add Tasks to Action List

Associate existing tasks with an action list:

**Step 1: Add first task**
```bash
curl -X POST "http://localhost:8002/api/v1/action-lists/AL-sprint-tasks/tasks?task_id=550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Step 2: Add second task**
```bash
curl -X POST "http://localhost:8002/api/v1/action-lists/AL-sprint-tasks/tasks?task_id=6ba7b810-9dad-11d1-80b4-00c04fd430c8" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Step 3: View associated tasks**
```bash
curl -X GET http://localhost:8002/api/v1/action-lists/AL-sprint-tasks/tasks \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Response**:
```json
[
  "550e8400-e29b-41d4-a716-446655440000",
  "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
]
```

---

### Workflow 5: Complete and Archive List

Mark a list as completed and archive it:

**Step 1: Mark as completed**
```bash
curl -X PATCH http://localhost:8002/api/v1/action-lists/AL-sprint-tasks \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "completed_at": "2025-12-28T18:00:00Z"
  }'
```

**Step 2: Archive the list**
```bash
curl -X PATCH http://localhost:8002/api/v1/action-lists/AL-sprint-tasks \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "archived"
  }'
```

---

### Workflow 6: Delete Action List

Permanently remove an action list:

**Warning**: This action cannot be undone. Consider archiving instead.

**Request**:
```bash
curl -X DELETE http://localhost:8002/api/v1/action-lists/AL-sprint-tasks \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**Response**: HTTP 204 No Content (success)

---

## Code Examples

### Python with Requests

```python
import requests
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8002/api/v1"
JWT_TOKEN = "your-jwt-token-here"

# Helper function
def make_request(method, endpoint, **kwargs):
    """Make authenticated API request."""
    headers = kwargs.get("headers", {})
    headers["Authorization"] = f"Bearer {JWT_TOKEN}"
    kwargs["headers"] = headers

    url = f"{BASE_URL}{endpoint}"
    response = requests.request(method, url, **kwargs)
    response.raise_for_status()
    return response.json() if response.content else None

# Create action list
action_list = make_request(
    "POST",
    "/action-lists",
    json={
        "id": "AL-python-example",
        "title": "Python API Example",
        "description": "Created via Python requests library",
        "owner": "automation",
        "priority": "high",
        "tags": ["automation", "python"]
    }
)
print(f"Created: {action_list['id']}")

# List action lists
lists = make_request("GET", "/action-lists?status=active")
print(f"Found {lists['total']} active lists")

# Update action list
updated = make_request(
    "PATCH",
    f"/action-lists/{action_list['id']}",
    json={"description": "Updated description"}
)
print(f"Updated: {updated['updated_at']}")

# Delete action list
make_request("DELETE", f"/action-lists/{action_list['id']}")
print("Deleted successfully")
```

---

### JavaScript with Fetch

```javascript
const BASE_URL = "http://localhost:8002/api/v1";
const JWT_TOKEN = "your-jwt-token-here";

// Helper function
async function apiRequest(method, endpoint, body = null) {
  const options = {
    method: method,
    headers: {
      "Authorization": `Bearer ${JWT_TOKEN}`,
      "Content-Type": "application/json"
    }
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, options);

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response.status === 204 ? null : response.json();
}

// Create action list
const actionList = await apiRequest("POST", "/action-lists", {
  id: "AL-javascript-example",
  title: "JavaScript API Example",
  description: "Created via Fetch API",
  owner: "frontend",
  priority: "medium",
  tags: ["frontend", "javascript"]
});
console.log(`Created: ${actionList.id}`);

// List action lists
const lists = await apiRequest("GET", "/action-lists?owner=frontend");
console.log(`Found ${lists.total} lists owned by frontend`);

// Update action list
const updated = await apiRequest("PATCH", `/action-lists/${actionList.id}`, {
  status: "completed",
  completed_at: new Date().toISOString()
});
console.log(`Updated: ${updated.updated_at}`);

// Delete action list
await apiRequest("DELETE", `/action-lists/${actionList.id}`);
console.log("Deleted successfully");
```

---

### PowerShell

```powershell
# Configuration
$BaseUrl = "http://localhost:8002/api/v1"
$JwtToken = "your-jwt-token-here"

# Helper function
function Invoke-TaskManApi {
    param(
        [string]$Method,
        [string]$Endpoint,
        [object]$Body
    )

    $headers = @{
        "Authorization" = "Bearer $JwtToken"
        "Content-Type" = "application/json"
    }

    $params = @{
        Uri = "$BaseUrl$Endpoint"
        Method = $Method
        Headers = $headers
    }

    if ($Body) {
        $params.Body = $Body | ConvertTo-Json -Depth 10
    }

    $response = Invoke-RestMethod @params
    return $response
}

# Create action list
$actionList = Invoke-TaskManApi -Method POST -Endpoint "/action-lists" -Body @{
    id = "AL-powershell-example"
    title = "PowerShell API Example"
    description = "Created via PowerShell Invoke-RestMethod"
    owner = "devops"
    priority = "high"
    tags = @("devops", "powershell")
}
Write-Host "Created: $($actionList.id)"

# List action lists
$lists = Invoke-TaskManApi -Method GET -Endpoint "/action-lists?owner=devops"
Write-Host "Found $($lists.total) lists owned by devops"

# Update action list
$updated = Invoke-TaskManApi -Method PATCH -Endpoint "/action-lists/$($actionList.id)" -Body @{
    description = "Updated via PowerShell"
}
Write-Host "Updated: $($updated.updated_at)"

# Delete action list
Invoke-TaskManApi -Method DELETE -Endpoint "/action-lists/$($actionList.id)"
Write-Host "Deleted successfully"
```

---

## Interactive Testing

### Swagger UI (Recommended)

1. **Open Swagger UI**: Navigate to `http://localhost:8002/docs`
2. **Authenticate**:
   - Click the **Authorize** 🔓 button
   - Enter: `Bearer <your-jwt-token>`
   - Click **Authorize**
3. **Test Endpoints**:
   - Expand any endpoint (e.g., "POST /action-lists")
   - Click **Try it out**
   - Edit the request body
   - Click **Execute**
   - View response below

**Benefits**:
- ✅ Interactive request builder
- ✅ Auto-generated curl commands
- ✅ Schema validation
- ✅ Response examples

---

### ReDoc (Clean Documentation)

For a clean, readable API reference:

1. **Open ReDoc**: Navigate to `http://localhost:8002/redoc`
2. **Browse Endpoints**: Scroll through organized endpoint documentation
3. **View Schemas**: Expand request/response schemas
4. **Copy Examples**: Use examples for your integration

---

## Troubleshooting

### Common Issues

**Issue 1: 401 Unauthorized**

```json
{
  "error": {
    "code": "MISSING_TOKEN",
    "message": "Authorization header missing"
  }
}
```

**Solution**: Add `Authorization: Bearer <token>` header to all requests.

---

**Issue 2: 400 Validation Error**

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {"field": "title", "message": "Field required"}
    ]
  }
}
```

**Solution**: Check required fields (`id`, `title`) are present in request body.

---

**Issue 3: 404 Not Found**

```json
{
  "error": {
    "code": "ACTION_LIST_NOT_FOUND",
    "message": "ActionList not found: AL-invalid-id"
  }
}
```

**Solution**: Verify the action list ID exists via `GET /action-lists` endpoint.

---

### Debug Checklist

When requests fail:

1. ✅ Verify token is valid (not expired)
2. ✅ Check request URL is correct (http://localhost:8002/api/v1/...)
3. ✅ Ensure Content-Type is `application/json`
4. ✅ Validate JSON request body is well-formed
5. ✅ Confirm required fields are present
6. ✅ Check error response for specific details

---

## Next Steps

Now that you're familiar with the basics, explore:

- **[Error Codes Reference](./action-lists-error-codes.md)** — Complete error catalog
- **[Authentication Guide](./action-lists-authentication.md)** — Deep dive into JWT auth
- **[API Documentation](/docs)** — Interactive Swagger UI
- **[Integration Testing](../adr/quality/ADR-022-ActionList-Integration-Testing-Strategy.md)** — Testing strategies

---

## Reference

### All Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/action-lists` | Create new action list |
| GET | `/action-lists` | List action lists (with filtering) |
| GET | `/action-lists/{list_id}` | Get specific action list |
| PUT/PATCH | `/action-lists/{list_id}` | Update action list |
| DELETE | `/action-lists/{list_id}` | Delete action list |
| GET | `/action-lists/{list_id}/tasks` | Get task IDs for list |
| POST | `/action-lists/{list_id}/tasks` | Add task to list |
| DELETE | `/action-lists/{list_id}/tasks/{task_id}` | Remove task from list |

---

### Request Schema Fields

**ActionListCreate** (POST):
- `id` (required): Action list ID (pattern: `AL-*`)
- `title` (required): Action list title
- `description` (optional): Detailed description
- `owner` (optional): Owner name
- `status` (optional): Status (active, completed, archived)
- `tags` (optional): Array of tags
- `project_id` (optional): Associated project
- `sprint_id` (optional): Associated sprint
- `items` (optional): Checklist items array
- `priority` (optional): Priority level
- `due_date` (optional): ISO-8601 timestamp

---

**ActionListUpdate** (PUT/PATCH):
All fields optional - only provided fields are updated.

---

## Support

**Need Help?**
- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc
- **Error Reference**: [action-lists-error-codes.md](./action-lists-error-codes.md)
- **Auth Guide**: [action-lists-authentication.md](./action-lists-authentication.md)

---

**Last Updated**: 2025-12-28
**API Version**: v1
**Maintainer**: ContextForge Documenter Agent
