# ActionList API Error Codes Reference

Comprehensive error catalog for ActionList API endpoints with resolution guidance.

---

## HTTP Status Codes

### 2xx Success

| Status | Code | Description | When It Occurs |
|--------|------|-------------|----------------|
| 200 | OK | Request succeeded | GET, PUT, PATCH operations successful |
| 201 | CREATED | Resource created | POST operation created new action list |
| 204 | NO_CONTENT | Success with no body | DELETE operation successful |

---

## 4xx Client Errors

### 400 Bad Request

**Description**: The request contains invalid data or violates business rules.

| Error Code | Message | Cause | Resolution |
|------------|---------|-------|------------|
| VALIDATION_ERROR | Request validation failed | Missing required field | Check request schema, provide all required fields |
| INVALID_STATUS | Invalid status value | Status not in [active, completed, archived] | Use valid status value |
| INVALID_PRIORITY | Invalid priority value | Priority format incorrect | Use valid priority string |
| INVALID_TASK_ID | Task ID does not exist | Referenced task not found | Verify task exists before adding to list |
| INVALID_DATE_FORMAT | Date format incorrect | Due date not ISO-8601 | Use format: `2025-12-31T23:59:59Z` |
| DUPLICATE_TITLE | Action list title already exists | Title collision | Choose unique title or update existing list |

**Example Response**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "title",
        "message": "Field required",
        "type": "missing"
      }
    ]
  }
}
```

**Resolution Steps**:
1. Check the `details` array for specific field errors
2. Verify all required fields are present: `id`, `title`
3. Ensure field values meet constraints (min_length, max_length, pattern)
4. Validate referenced IDs exist (project_id, sprint_id, task_id)

---

### 401 Unauthorized

**Description**: Missing or invalid authentication credentials.

| Error Code | Message | Cause | Resolution |
|------------|---------|-------|------------|
| MISSING_TOKEN | Authorization header missing | No `Authorization` header | Add `Authorization: Bearer <token>` |
| INVALID_TOKEN | Token is invalid or expired | JWT signature invalid or token expired | Obtain new JWT token via auth endpoint |
| TOKEN_EXPIRED | Token has expired | Token lifetime exceeded | Refresh token or re-authenticate |

**Example Response**:
```json
{
  "error": {
    "code": "INVALID_TOKEN",
    "message": "Invalid or expired JWT token",
    "details": {
      "token_type": "Bearer",
      "expiry": "2025-12-28T10:00:00Z"
    }
  }
}
```

**Resolution Steps**:
1. Verify `Authorization` header is present
2. Ensure header format is `Bearer <jwt_token>`
3. Check token expiration timestamp
4. Obtain fresh token if expired

---

### 403 Forbidden

**Description**: Valid authentication but insufficient permissions.

| Error Code | Message | Cause | Resolution |
|------------|---------|-------|------------|
| INSUFFICIENT_PERMISSIONS | User lacks required permissions | Trying to modify others' lists | Request permission or authenticate as owner |
| RESOURCE_LOCKED | Resource is locked | Action list being modified elsewhere | Wait and retry |

**Example Response**:
```json
{
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "You do not have permission to modify this action list",
    "details": {
      "required_role": "owner",
      "user_role": "viewer",
      "resource_id": "AL-backend-tasks"
    }
  }
}
```

**Resolution Steps**:
1. Verify user has appropriate role for operation
2. Check resource ownership
3. Request permission elevation if necessary

---

### 404 Not Found

**Description**: Requested resource does not exist.

| Error Code | Message | Cause | Resolution |
|------------|---------|-------|------------|
| ACTION_LIST_NOT_FOUND | Action list not found | Invalid list_id or deleted | Verify ID, check if list was deleted |
| RESOURCE_NOT_FOUND | Resource not found | Generic 404 | Check endpoint path and ID format |

**Example Response**:
```json
{
  "error": {
    "code": "ACTION_LIST_NOT_FOUND",
    "message": "ActionList not found: AL-invalid-id",
    "details": {
      "resource_type": "ActionList",
      "resource_id": "AL-invalid-id"
    }
  }
}
```

**Resolution Steps**:
1. Verify the action list ID format: `AL-*`
2. Confirm the resource wasn't deleted
3. Query list endpoint to find valid IDs
4. Check for typos in the ID

---

### 422 Unprocessable Entity

**Description**: Request is well-formed but semantically invalid.

| Error Code | Message | Cause | Resolution |
|------------|---------|-------|------------|
| SEMANTIC_VALIDATION_ERROR | Business rule violation | Data valid but violates logic | Review business rules |
| INVALID_STATE_TRANSITION | Cannot transition to requested state | Status change not allowed | Check valid state transitions |
| CIRCULAR_DEPENDENCY | Circular reference detected | Task references create cycle | Remove circular dependencies |

**Example Response**:
```json
{
  "error": {
    "code": "INVALID_STATE_TRANSITION",
    "message": "Cannot transition from 'completed' to 'active'",
    "details": {
      "current_state": "completed",
      "requested_state": "active",
      "allowed_transitions": ["archived"]
    }
  }
}
```

**Resolution Steps**:
1. Review business logic for the operation
2. Check state transition rules
3. Ensure dependencies are satisfied
4. Verify data relationships are valid

---

## 5xx Server Errors

### 500 Internal Server Error

**Description**: Unexpected server-side failure.

| Error Code | Message | Cause | Resolution |
|------------|---------|-------|------------|
| INTERNAL_ERROR | Internal server error | Database failure, bug, or crash | Retry request, contact support if persists |
| DATABASE_ERROR | Database operation failed | Connection timeout, constraint violation | Check database health, retry |
| UNEXPECTED_ERROR | Unexpected error occurred | Unhandled exception | Report to development team |

**Example Response**:
```json
{
  "error": {
    "code": "DATABASE_ERROR",
    "message": "Database operation failed",
    "details": {
      "operation": "insert",
      "table": "action_lists",
      "error_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  }
}
```

**Resolution Steps**:
1. Note the error_id for support requests
2. Retry the request (may be transient)
3. Check system status page
4. Contact support if error persists

---

## Error Response Structure

All error responses follow a consistent structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional context (optional)
    }
  }
}
```

**Fields**:
- `code` (string): Machine-readable error code for programmatic handling
- `message` (string): Human-readable description of the error
- `details` (object): Additional context like field errors, constraints, etc.

---

## Common Error Patterns

### Validation Errors (400)

**Pattern**: Missing or invalid request fields

```bash
# Missing required field
POST /api/v1/action-lists
{
  "description": "Missing title field"
}

# Response: 400 VALIDATION_ERROR
```

**Fix**: Include all required fields with valid values.

---

### Authentication Errors (401)

**Pattern**: Missing or expired token

```bash
# No Authorization header
GET /api/v1/action-lists/AL-001

# Response: 401 MISSING_TOKEN
```

**Fix**: Add `Authorization: Bearer <token>` header.

---

### Not Found Errors (404)

**Pattern**: Invalid resource ID

```bash
# Non-existent action list
GET /api/v1/action-lists/AL-does-not-exist

# Response: 404 ACTION_LIST_NOT_FOUND
```

**Fix**: Verify ID exists via list endpoint first.

---

## Troubleshooting Guide

### Debug Checklist

When encountering errors, follow this checklist:

1. **Check HTTP Status**
   - 4xx → Client-side issue (your request)
   - 5xx → Server-side issue (report to team)

2. **Read Error Code**
   - Use error code table above for specific resolution

3. **Inspect Details**
   - Review `details` object for specific field errors
   - Note any constraint violations

4. **Verify Authentication**
   - Ensure token is present and valid
   - Check token expiration

5. **Validate Request Data**
   - Compare against schema documentation
   - Use Swagger UI `/docs` to test

6. **Check Resource Existence**
   - List resources to find valid IDs
   - Verify references (project_id, sprint_id, task_id)

---

## Support

**Need Help?**
- **Swagger UI**: Interactive docs at `/docs`
- **ReDoc**: Clean reference at `/redoc`
- **GitHub Issues**: Report bugs or request features
- **Team Slack**: #taskman-api for quick questions

---

**Last Updated**: 2025-12-28
**API Version**: v1
**Maintainer**: ContextForge Documenter Agent
