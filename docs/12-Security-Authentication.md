# 12 – Security & Authentication

**Status**: Complete
**Version**: 2.0
**Last Updated**: 2025-11-11
**Related**: [01-Overview](01-Overview.md) | [02-Architecture](02-Architecture.md) | [10-API-Reference](10-API-Reference.md) | [14-Deployment-Operations](14-Deployment-Operations.md)

---

## Overview

ContextForge implements **defense-in-depth security** with layered controls across authentication, authorization, secret management, and operational security. Security is not an afterthought but a foundational principle woven into every layer.

### Security Principles (Codex)

From [ContextForge Work Codex](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md):

1. **Trust Nothing, Verify Everything** - Evidence-based security with comprehensive logging
2. **Security is Layered** - Defense-in-depth acknowledges human fallibility and system complexity
3. **Logs First** - All security events must produce structured logs
4. **Configuration Must Reflect Clarity** - Defaults safe, overrides explicit, changes traceable

---

## Authentication

### JWT-Based Authentication (P0-005)

**Current Status**: Implementation planned for TaskMan-v2 production readiness

**Architecture**:
- JWT tokens for stateless authentication
- Refresh token rotation for security
- Role-based access control (RBAC)
- Token expiration: 15 minutes (access), 7 days (refresh)

### Auth Provider Options

**Option A: Auth0** (Recommended for MVP)
- **Pros**: Managed service, rapid integration, enterprise features
- **Cons**: Vendor lock-in, recurring costs
- **Use Case**: Fast production launch, minimal security overhead

**Option B: Keycloak**
- **Pros**: Self-hosted, full control, open source, SAML/OIDC support
- **Cons**: Operational overhead, requires Kubernetes/Docker expertise
- **Use Case**: Enterprise deployments with existing Keycloak infrastructure

**Option C: Custom JWT**
- **Pros**: Complete control, no external dependencies
- **Cons**: Security risks, maintenance burden, compliance overhead
- **Use Case**: Educational environments, prototypes only

---

## Backend Authentication Implementation

### JWT Verification Middleware

```python
# backend-api/dependencies/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from ..config import settings
from ..services.unified_logger import logger

security = HTTPBearer()

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Verify JWT token and return user payload.

    Emits:
        - auth_token_verified (success)
        - auth_token_invalid (failure)
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            logger.warn("auth_token_expired", user=payload.get("sub"))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )

        logger.info("auth_token_verified", user=payload.get("sub"))
        return payload

    except JWTError as e:
        logger.error("auth_token_invalid", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_current_user(payload: dict = Depends(verify_token)) -> dict:
    """Extract user info from verified token."""
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "roles": payload.get("roles", [])
    }
```

### Protected Endpoints

```python
# backend-api/routers/tasks.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..dependencies.database import get_db
from ..dependencies.auth import get_current_user
from ..schemas.task import TaskCreate, TaskResponse
from ..services.task_service import TaskService

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)  # Authentication required
):
    """Create a new task (authenticated users only)."""
    service = TaskService(db)
    return service.create_task(task, user_id=user["user_id"])

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Get task by ID (authenticated users only)."""
    service = TaskService(db)
    task = service.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Authorization: Can user access this task?
    if not service.can_user_access_task(task, user):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    return task
```

### Token Generation

```python
# backend-api/services/auth_service.py
from datetime import datetime, timedelta
from jose import jwt
from ..config import settings
from ..services.unified_logger import logger

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Generate JWT access token.

    Emits: token_created event
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    logger.info("token_created", user=data.get("sub"), expires_at=expire.isoformat())
    return encoded_jwt

def create_refresh_token(user_id: str) -> str:
    """Generate long-lived refresh token."""
    data = {"sub": user_id, "type": "refresh"}
    expires_delta = timedelta(days=7)
    return create_access_token(data, expires_delta)
```

---

## Frontend Authentication Integration

### Axios Interceptors

```typescript
// src/services/api.ts
import axios, { AxiosInstance } from 'axios';
import { logger } from './logger';

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
});

// Request interceptor - Add JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      logger.debug('auth_token_attached', endpoint: config.url);
    }
    return config;
  },
  (error) => {
    logger.error('auth_request_error', error: error.message);
    return Promise.reject(error);
  }
);

// Response interceptor - Handle 401 Unauthorized
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Attempt token refresh
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post('/api/v1/auth/refresh', {
          refresh_token: refreshToken,
        });

        const { access_token } = response.data;
        localStorage.setItem('access_token', access_token);

        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);

      } catch (refreshError) {
        // Refresh failed - redirect to login
        logger.warn('auth_refresh_failed', redirecting to login');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

### Authentication Context

```typescript
// src/contexts/AuthContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';
import { logger } from '../services/logger';

interface User {
  user_id: string;
  email: string;
  roles: string[];
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchCurrentUser();
    }
  }, []);

  const fetchCurrentUser = async () => {
    try {
      const response = await api.get('/api/v1/auth/me');
      setUser(response.data);
      logger.info('user_authenticated', user_id: response.data.user_id);
    } catch (error) {
      logger.error('user_fetch_failed', error);
      localStorage.removeItem('access_token');
    }
  };

  const login = async (email: string, password: string) => {
    const response = await api.post('/api/v1/auth/login', { email, password });
    const { access_token, refresh_token, user } = response.data;

    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    setUser(user);

    logger.info('user_logged_in', user_id: user.user_id);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    logger.info('user_logged_out');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

---

## Authorization (RBAC)

### Role Definitions

```python
# backend-api/models/roles.py
from enum import Enum

class Role(str, Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"
    GUEST = "guest"

ROLE_PERMISSIONS = {
    Role.ADMIN: [
        "task:create", "task:read", "task:update", "task:delete",
        "sprint:create", "sprint:read", "sprint:update", "sprint:delete",
        "project:create", "project:read", "project:update", "project:delete",
        "user:manage"
    ],
    Role.DEVELOPER: [
        "task:create", "task:read", "task:update",
        "sprint:read",
        "project:read"
    ],
    Role.VIEWER: [
        "task:read",
        "sprint:read",
        "project:read"
    ],
    Role.GUEST: [
        "task:read",
        "project:read"
    ]
}
```

### Permission Checking

```python
# backend-api/dependencies/authorization.py
from fastapi import Depends, HTTPException, status
from .auth import get_current_user
from ..models.roles import ROLE_PERMISSIONS
from ..services.unified_logger import logger

def require_permission(permission: str):
    """Dependency factory for permission-based authorization."""

    async def check_permission(user: dict = Depends(get_current_user)):
        user_roles = user.get("roles", [])

        # Check if user has required permission
        for role in user_roles:
            if permission in ROLE_PERMISSIONS.get(role, []):
                logger.info("permission_granted",
                           user=user["user_id"],
                           permission=permission)
                return user

        logger.warn("permission_denied",
                   user=user["user_id"],
                   permission=permission)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions: {permission} required"
        )

    return check_permission

# Usage
@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(require_permission("task:delete"))
):
    """Delete task (admin only)."""
    service = TaskService(db)
    service.delete_task(task_id)
```

---

## Secret Management

### Environment Variables

**Principle**: "Secret refs only; environment variables or SecretManagement; no plaintext credentials persisted."

```bash
# .env.example (committed to git)
DATABASE_URL=postgresql://user:password@localhost:5432/taskman
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=taskman
POSTGRES_PASSWORD=changeme
```

```bash
# .env (gitignored - actual secrets)
DATABASE_URL=postgresql://taskman_user:RealP@ssw0rd!@prod-db.internal:5432/taskman_prod
JWT_SECRET=e8f3a2b9c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0
JWT_ALGORITHM=HS256
```

### Python Configuration

```python
# backend-api/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()

settings = get_settings()
```

### PowerShell Secret Management

```powershell
# Store secrets securely (Windows)
Install-Module SecretManagement -Scope CurrentUser
Install-Module SecretManagement.KeePass -Scope CurrentUser

# Register secret vault
Register-SecretVault -Name ContextForge -ModuleName SecretManagement.KeePass

# Store secrets
Set-Secret -Name "DATABASE_URL" -Secret "postgresql://..." -Vault ContextForge
Set-Secret -Name "JWT_SECRET" -Secret "e8f3a2b9..." -Vault ContextForge

# Retrieve secrets
$dbUrl = Get-Secret -Name "DATABASE_URL" -Vault ContextForge -AsPlainText
```

### Production Secret Management

**Azure Key Vault**:
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(
    vault_url="https://contextforge-vault.vault.azure.net/",
    credential=credential
)

# Retrieve secret
jwt_secret = client.get_secret("JWT-SECRET").value
```

**AWS Secrets Manager**:
```python
import boto3

client = boto3.client('secretsmanager', region_name='us-east-1')

response = client.get_secret_value(SecretId='prod/contextforge/jwt-secret')
jwt_secret = response['SecretString']
```

---

## Security Headers

### FastAPI Middleware

```python
# backend-api/middleware/security.py
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

def add_security_middleware(app: FastAPI):
    """Add security-focused middleware."""

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    # Trusted Host (prevent host header attacks)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "*.contextforge.dev"]
    )

    @app.middleware("http")
    async def add_security_headers(request, call_next):
        """Add security headers to all responses."""
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response
```

---

## Vulnerability Management

### Dependency Scanning

```bash
# Python dependencies
pip install safety
safety check --json > security-report.json

# Node dependencies
npm audit --json > npm-audit.json
```

### OWASP Top 10 Mitigations

| Vulnerability | Mitigation | Implementation |
|---------------|------------|----------------|
| **Injection** | Parameterized queries | SQLAlchemy ORM, Pydantic validation |
| **Broken Auth** | JWT with refresh rotation | FastAPI security, 15min expiration |
| **XSS** | Input sanitization | React auto-escaping, CSP headers |
| **CSRF** | SameSite cookies | `SameSite=Strict` on cookies |
| **SSRF** | URL validation | Whitelist internal URLs |
| **Sensitive Data** | Encryption at rest | PostgreSQL encryption, env vars |
| **Broken Access** | RBAC enforcement | Permission decorators |
| **Logging Failures** | Unified logger | 90% logging coverage (Codex) |
| **Insecure Deserialization** | Schema validation | Pydantic models |
| **Vulnerable Components** | Dependency scanning | `safety`, `npm audit` |

---

## Security Logging

### Event Taxonomy

From [Codex Appendix B: Logging Taxonomy](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md):

**Authentication Events**:
- `auth_token_verified` - JWT token successfully verified
- `auth_token_invalid` - Invalid token provided
- `auth_token_expired` - Expired token used
- `user_logged_in` - Successful login
- `user_logged_out` - User logout
- `auth_refresh_failed` - Refresh token rotation failed

**Authorization Events**:
- `permission_granted` - User has required permission
- `permission_denied` - User lacks required permission
- `access_denied` - Resource access blocked

**Security Events**:
- `suspicious_activity` - Anomalous behavior detected
- `rate_limit_exceeded` - Too many requests
- `csrf_attempt` - Potential CSRF attack

### Structured Logging

```python
from ..services.unified_logger import logger

# Authentication success
logger.info("auth_token_verified",
           user=user_id,
           ip=request.client.host,
           user_agent=request.headers.get("user-agent"))

# Authorization failure
logger.warn("permission_denied",
           user=user_id,
           permission=permission,
           resource=resource_id,
           ip=request.client.host)

# Suspicious activity
logger.error("suspicious_activity",
            user=user_id,
            activity="multiple_failed_logins",
            count=5,
            ip=request.client.host)
```

---

## Rate Limiting (Planned)

### Implementation Strategy

```python
# backend-api/middleware/rate_limit.py
from fastapi import Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.route("/api/v1/auth/login")
@limiter.limit("5/minute")  # 5 login attempts per minute
async def login(request: Request):
    # Login logic
    pass

@app.route("/api/v1/tasks")
@limiter.limit("100/minute")  # 100 requests per minute
async def list_tasks(request: Request):
    # List tasks logic
    pass
```

---

## Compliance & Auditing

### Evidence Bundles

All security events produce **cryptographic evidence bundles** with SHA-256 hashing:

```python
import hashlib
import json

def create_evidence_bundle(event: dict) -> str:
    """Generate SHA-256 hash for event."""
    event_json = json.dumps(event, sort_keys=True)
    return hashlib.sha256(event_json.encode()).hexdigest()

# Usage
event = {
    "event_type": "auth_token_verified",
    "user_id": "user-123",
    "timestamp": "2025-11-11T18:30:00Z",
    "ip": "192.168.1.1"
}

evidence_hash = create_evidence_bundle(event)
logger.info("auth_token_verified",
           evidence_bundle_hash=evidence_hash,
           **event)
```

### Audit Log Retention

**Policy**:
- Security logs: **90 days** minimum
- Authentication events: **1 year**
- Authorization failures: **2 years**
- Compliance logs: **7 years** (regulatory requirement)

---

## Security Testing

### Penetration Testing

**Tools**:
- OWASP ZAP (automated scans)
- Burp Suite (manual testing)
- Nuclei (vulnerability scanning)

### Security Test Cases

```python
# tests/security/test_authentication.py
import pytest
from fastapi.testclient import TestClient

def test_auth_requires_valid_token(client: TestClient):
    """Endpoints reject requests without valid JWT."""
    response = client.get("/api/v1/tasks")
    assert response.status_code == 401

def test_auth_rejects_expired_token(client: TestClient, expired_token: str):
    """Expired tokens are rejected."""
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/api/v1/tasks", headers=headers)
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()

def test_rbac_enforces_permissions(client: TestClient, viewer_token: str):
    """Viewers cannot create tasks."""
    headers = {"Authorization": f"Bearer {viewer_token}"}
    response = client.post("/api/v1/tasks", headers=headers, json={"title": "Test"})
    assert response.status_code == 403
```

---

## Production Checklist

### Pre-Deployment

- [ ] JWT_SECRET rotated (256-bit minimum)
- [ ] All secrets moved to vault (Azure/AWS)
- [ ] Rate limiting enabled
- [ ] HTTPS enforced (redirect HTTP → HTTPS)
- [ ] Security headers configured
- [ ] CORS origins whitelisted
- [ ] Dependency vulnerabilities resolved
- [ ] Penetration test completed
- [ ] Security logs shipping to SIEM
- [ ] Incident response playbook documented

### Post-Deployment

- [ ] Authentication flow validated in production
- [ ] Authorization checks verified
- [ ] Log aggregation confirmed
- [ ] Security alerts configured
- [ ] Backup/restore tested
- [ ] Disaster recovery plan documented

---

## Cross References

### Foundation Documents

- [01-Overview.md](01-Overview.md) - System overview with security principles
- [02-Architecture.md](02-Architecture.md) - Security posture, secret management
- [10-API-Reference.md](10-API-Reference.md) - Authentication endpoints
- [14-Deployment-Operations.md](14-Deployment-Operations.md) - Production security

### Authoritative Source

- [docs/Codex/ContextForge Work Codex.md](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md) - **PRIMARY SOURCE**

### Implementation Details

- [TaskMan-v2/backend-api/dependencies/auth.py](../TaskMan-v2/backend-api/dependencies/auth.py) - JWT verification
- [TaskMan-v2/frontend/src/contexts/AuthContext.tsx](../TaskMan-v2/frontend/src/contexts/AuthContext.tsx) - Frontend auth

---

**Document Status**: Complete ✅
**Authoritative**: Yes (integrated with Codex)
**Next Review**: 2026-02-11 (quarterly)
**Maintained By**: ContextForge Security Team

---

*"Security is layered; defense-in-depth acknowledges both human fallibility and system complexity."*
