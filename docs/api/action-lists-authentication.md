# ActionList API Authentication Guide

Complete authentication documentation for TaskMan v2 ActionList endpoints.

---

## Overview

All ActionList API endpoints require **JWT (JSON Web Token) Bearer authentication**. Unauthenticated requests will receive a `401 Unauthorized` response.

**Authentication Method**: Bearer Token (JWT)
**Token Type**: JSON Web Token (RFC 7519)
**Header Format**: `Authorization: Bearer <jwt_token>`

---

## Quick Start

### 1. Obtain JWT Token

**Endpoint**: `POST /api/v1/auth/login`

**Request**:
```bash
curl -X POST http://localhost:8002/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your-username",
    "password": "your-password"
  }'
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 2. Use Token in Requests

Add the `Authorization` header with `Bearer <token>`:

**Example**:
```bash
curl -X GET http://localhost:8002/api/v1/action-lists \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Python Example**:
```python
import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
headers = {"Authorization": f"Bearer {token}"}

response = requests.get(
    "http://localhost:8002/api/v1/action-lists",
    headers=headers
)
```

**JavaScript Example**:
```javascript
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";

fetch("http://localhost:8002/api/v1/action-lists", {
  headers: {
    "Authorization": `Bearer ${token}`
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## JWT Token Details

### Token Structure

JWT tokens consist of three Base64-encoded parts separated by dots:

```
<header>.<payload>.<signature>
```

**Example Token**:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

### Token Payload

The payload contains claims about the authenticated user:

```json
{
  "sub": "user-uuid",              // Subject (user ID)
  "username": "john.doe",          // Username
  "email": "john@example.com",     // Email
  "roles": ["user", "admin"],      // User roles
  "iat": 1703764800,               // Issued at (Unix timestamp)
  "exp": 1703768400,               // Expiration (Unix timestamp)
  "jti": "token-uuid"              // JWT ID (unique token identifier)
}
```

**Important Claims**:
- `sub`: User identifier (UUID format)
- `exp`: Token expiration timestamp (validate before use)
- `roles`: User permissions for authorization checks

---

## Token Lifecycle

### Obtaining Tokens

**Login Flow**:
```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Auth
    participant DB

    Client->>API: POST /auth/login (credentials)
    API->>Auth: Validate credentials
    Auth->>DB: Check user credentials
    DB-->>Auth: User found
    Auth->>Auth: Generate JWT
    Auth-->>API: Return access + refresh tokens
    API-->>Client: { access_token, refresh_token }
```

---

### Token Expiration

**Default Lifetime**:
- **Access Token**: 1 hour (3600 seconds)
- **Refresh Token**: 7 days (604800 seconds)

**Check Expiration**:
```python
import jwt
import time

token = "your-jwt-token-here"
decoded = jwt.decode(token, options={"verify_signature": False})

exp_timestamp = decoded["exp"]
current_timestamp = int(time.time())

if current_timestamp > exp_timestamp:
    print("Token expired - refresh needed")
else:
    seconds_remaining = exp_timestamp - current_timestamp
    print(f"Token valid for {seconds_remaining} seconds")
```

---

### Refreshing Tokens

When your access token expires, use the refresh token to obtain a new one without re-authenticating.

**Endpoint**: `POST /api/v1/auth/refresh`

**Request**:
```bash
curl -X POST http://localhost:8002/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
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

**Refresh Flow**:
```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Auth

    Client->>API: POST /auth/refresh (refresh_token)
    API->>Auth: Validate refresh token
    Auth->>Auth: Generate new access token
    Auth-->>API: New access token
    API-->>Client: { access_token }
```

---

## Authorization Levels

### Role-Based Access Control (RBAC)

ActionList endpoints enforce role-based permissions:

| Role | Create | Read | Update (Own) | Update (All) | Delete (Own) | Delete (All) |
|------|--------|------|--------------|--------------|--------------|--------------|
| **Viewer** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **User** | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| **Admin** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Notes**:
- "Own" means resources owned by the authenticated user
- "All" means any resources regardless of ownership
- Role is extracted from JWT token claims

---

### Permission Checks

**Example**: Update action list

```python
# Token payload
{
  "sub": "user-123",
  "roles": ["user"]
}

# Attempting to update
PATCH /api/v1/action-lists/AL-001

# Permission check
if action_list.owner == user_id or "admin" in roles:
    # Allow update
else:
    # 403 Forbidden
```

---

## Security Best Practices

### 1. Secure Token Storage

**Browser (Frontend)**:
```javascript
// Store in memory (most secure, lost on refresh)
let token = null;

// Or use sessionStorage (cleared on tab close)
sessionStorage.setItem('jwt_token', token);

// Avoid localStorage for sensitive tokens
// localStorage persists across browser sessions
```

**Backend/Script**:
```python
import os

# Use environment variables
token = os.getenv("TASKMAN_JWT_TOKEN")

# Or secure keyring
import keyring
token = keyring.get_password("taskman", "jwt_token")
```

---

### 2. Token Validation

Always validate tokens before use:

```python
import jwt
from datetime import datetime

def is_token_valid(token: str, secret_key: str) -> bool:
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        exp = datetime.fromtimestamp(payload["exp"])
        return datetime.now() < exp
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False
```

---

### 3. HTTPS Only

**Production Requirement**: Always use HTTPS to prevent token interception.

```bash
# ✅ Secure
curl https://api.taskman.example.com/api/v1/action-lists \
  -H "Authorization: Bearer <token>"

# ❌ Insecure (development only)
curl http://localhost:8002/api/v1/action-lists \
  -H "Authorization: Bearer <token>"
```

---

### 4. Token Rotation

Implement token rotation to minimize risk:

```python
class TokenManager:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None

    def refresh_if_needed(self):
        """Auto-refresh token if expiring soon (< 5 minutes)."""
        if self.expires_at - datetime.now() < timedelta(minutes=5):
            self.refresh_access_token()

    def refresh_access_token(self):
        """Request new access token using refresh token."""
        response = requests.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": self.refresh_token}
        )
        data = response.json()
        self.access_token = data["access_token"]
        self.expires_at = datetime.now() + timedelta(seconds=data["expires_in"])
```

---

## Error Handling

### Common Authentication Errors

| Status | Error Code | Cause | Solution |
|--------|------------|-------|----------|
| 401 | MISSING_TOKEN | No Authorization header | Add header with token |
| 401 | INVALID_TOKEN | Malformed or corrupted token | Obtain new token |
| 401 | TOKEN_EXPIRED | Token lifetime exceeded | Refresh token |
| 403 | INSUFFICIENT_PERMISSIONS | User lacks required role | Request permission upgrade |

**Example Error Response**:
```json
{
  "error": {
    "code": "TOKEN_EXPIRED",
    "message": "JWT token has expired",
    "details": {
      "expired_at": "2025-12-28T10:00:00Z",
      "current_time": "2025-12-28T11:30:00Z"
    }
  }
}
```

---

### Retry Strategy

Implement automatic retry with token refresh:

```python
def api_request_with_retry(url: str, method: str = "GET", **kwargs):
    """Make API request with automatic token refresh on 401."""
    headers = kwargs.get("headers", {})
    headers["Authorization"] = f"Bearer {get_current_token()}"
    kwargs["headers"] = headers

    response = requests.request(method, url, **kwargs)

    if response.status_code == 401:
        # Token expired - refresh and retry
        refresh_access_token()
        headers["Authorization"] = f"Bearer {get_current_token()}"
        response = requests.request(method, url, **kwargs)

    return response
```

---

## Development vs Production

### Development Environment

**Relaxed Settings** (localhost only):
- HTTP allowed (not HTTPS)
- Longer token expiration (12 hours)
- Debug logging enabled

**Configuration**:
```python
# config/development.py
JWT_SECRET_KEY = "dev-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 720  # 12 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30
```

---

### Production Environment

**Strict Security**:
- HTTPS required
- Short token expiration (1 hour)
- Secure secret key (environment variable)
- Rate limiting enabled

**Configuration**:
```python
# config/production.py
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # From secure vault
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
REFRESH_TOKEN_EXPIRE_DAYS = 7
REQUIRE_HTTPS = True
```

---

## Testing Authentication

### Swagger UI Authentication

1. Open Swagger UI: `http://localhost:8002/docs`
2. Click **Authorize** button (🔓 icon)
3. Enter token in format: `Bearer <your-token>`
4. Click **Authorize**
5. Test endpoints with "Try it out"

---

### Postman Setup

**Collection Variables**:
```json
{
  "base_url": "http://localhost:8002",
  "jwt_token": "{{jwt_token}}"
}
```

**Pre-request Script** (auto-refresh):
```javascript
// Check if token is about to expire
const token = pm.environment.get("jwt_token");
const payload = JSON.parse(atob(token.split('.')[1]));
const exp = payload.exp * 1000;
const now = Date.now();

if (now > exp - 300000) {  // Refresh if < 5 minutes remaining
    pm.sendRequest({
        url: pm.environment.get("base_url") + "/api/v1/auth/refresh",
        method: "POST",
        body: {
            mode: "json",
            raw: JSON.stringify({
                refresh_token: pm.environment.get("refresh_token")
            })
        }
    }, (err, res) => {
        pm.environment.set("jwt_token", res.json().access_token);
    });
}
```

---

## Troubleshooting

### Token Not Working

**Checklist**:
1. ✅ Header format is `Authorization: Bearer <token>` (note the space)
2. ✅ Token is not expired (check `exp` claim)
3. ✅ Token is complete (no truncation)
4. ✅ Using correct API endpoint
5. ✅ User has required permissions

**Debug Token**:
```bash
# Decode token payload (base64)
echo "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ" | base64 -d

# Or use jwt.io website
# Paste token at https://jwt.io to inspect claims
```

---

## Reference

**Related Documentation**:
- [Error Codes Reference](./action-lists-error-codes.md)
- [API Quick Start](./action-lists-quickstart.md)
- [ADR-020: Authentication & Authorization](../adr/quality/ADR-020-ActionList-Authentication-Authorization.md)

**External Resources**:
- [JWT.io](https://jwt.io) - Token decoder and validator
- [RFC 7519](https://tools.ietf.org/html/rfc7519) - JWT Specification
- [OAuth 2.0 Bearer Tokens](https://tools.ietf.org/html/rfc6750)

---

**Last Updated**: 2025-12-28
**API Version**: v1
**Maintainer**: ContextForge Documenter Agent
