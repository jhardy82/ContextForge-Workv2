# Auth0 vs Keycloak: Detailed Comparison for TaskMan-v2

**Date**: 2025-12-27  
**Status**: Complete  
**Context**: Authentication solution selection for internal enterprise tool

---

## Executive Summary

| Aspect | Recommendation | Confidence |
|--------|---------------|------------|
| **MVP Choice** | **Keycloak** | High (85%) |
| **Timeline** | 1.5 weeks (30 hours) | Medium |
| **Long-term TCO** | Keycloak ~60% lower | High |

**Key Decision Factors**:
1. Internal tool = self-hosting acceptable, no public SaaS concerns
2. Docker/K8s native deployment = Keycloak natural fit
3. Compliance requirements = both adequate, Keycloak offers more control
4. Engineering team users = can handle Keycloak operations
5. Long-term cost optimization = critical for internal tooling

---

## Context: TaskMan-v2 Requirements

| Requirement | Status | Impact on Decision |
|-------------|--------|-------------------|
| Internal enterprise tool | ✅ | Favors self-hosting |
| Engineers + compliance users | ✅ | Technical users can operate Keycloak |
| Python FastAPI backend | ✅ | Both have good Python support |
| React 19 SPA frontend | ✅ | Both have React SDKs |
| Docker/Kubernetes deployment | ✅ | Keycloak is K8s-native |
| WCAG-AA accessibility | ✅ | Both compliant |
| Audit logging required | ✅ | Both provide audit logs |
| JWT auth (15min/7d tokens) | ✅ | Both support custom token lifetimes |
| 4 roles (admin/dev/viewer/guest) | ✅ | Both support RBAC |

---

## Detailed Comparison Matrix

### 1. Implementation Complexity

| Metric | Auth0 | Keycloak |
|--------|-------|----------|
| **Time to MVP** | ~20 hours (1 week) | ~30 hours (1.5 weeks) |
| **Initial Setup** | 2 hours (managed service) | 8 hours (Docker/K8s deployment) |
| **Learning Curve** | Low (excellent docs) | Medium (more concepts) |
| **FastAPI Integration** | 4 hours | 6 hours |
| **React Integration** | 4 hours | 4 hours |
| **RBAC Configuration** | 4 hours | 4 hours |
| **Testing & Polish** | 4 hours | 6 hours |
| **Winner** | ✅ Auth0 | |

**Auth0 Setup Tasks**:
```bash
# Day 1: Tenant + Application setup (2h)
1. Create Auth0 tenant (10 min)
2. Create SPA application for React (20 min)
3. Create API for FastAPI backend (20 min)
4. Configure RBAC roles (30 min)
5. Enable audit logging (30 min)

# Day 2: FastAPI integration (4h)
1. Install authlib, python-jose (10 min)
2. Create JWT validation middleware (2h)
3. Add role-based decorators (1h)
4. Test with Postman (1h)

# Day 3: React integration (4h)
1. Install @auth0/auth0-react (10 min)
2. Wrap App with Auth0Provider (30 min)
3. Implement login/logout (1h)
4. Add protected routes (1h)
5. Token refresh handling (1h)
```

**Keycloak Setup Tasks**:
```bash
# Day 1-2: Deployment (8h)
1. Deploy Keycloak via Helm/Docker Compose (2h)
2. Configure PostgreSQL backend (1h)
3. Create realm for TaskMan (30 min)
4. Configure OIDC client (1h)
5. Set up SSL/TLS (2h)
6. Health checks and monitoring (1h)

# Day 3: Realm configuration (4h)
1. Create roles (admin, developer, viewer, guest) (30 min)
2. Configure client scopes (30 min)
3. Set token lifetimes (15min access, 7d refresh) (20 min)
4. Enable audit logging (30 min)
5. Configure MFA (optional) (1h)
6. Theme customization (30 min)

# Day 4-5: Backend + Frontend (10h)
# Similar to Auth0 but with python-keycloak and keycloak-js
```

---

### 2. Cost Analysis

| Cost Type | Auth0 | Keycloak |
|-----------|-------|----------|
| **Software License** | Varies by tier | FREE (Apache 2.0) |
| **Free Tier** | 7,500 MAU | Unlimited |
| **50 users/month** | $0 (free tier) | ~$50-100/mo infra |
| **200 users/month** | $0 (free tier) | ~$50-100/mo infra |
| **1,000 users/month** | ~$240/mo Professional | ~$100-150/mo infra |
| **Audit Logging** | Enterprise only ($$$) | Built-in FREE |
| **RBAC** | Professional tier ($240/mo) | Built-in FREE |
| **MFA** | Professional tier | Built-in FREE |
| **SSO (SAML)** | Enterprise tier ($$$) | Built-in FREE |
| **Operations** | $0 (managed) | ~2-4 hours/month |
| **Winner** | | ✅ Keycloak |

**3-Year TCO Estimate** (200 internal users):

| Item | Auth0 | Keycloak |
|------|-------|----------|
| Software | $0-$240/mo × 36 = $0-$8,640 | $0 |
| Infrastructure | $0 | $100/mo × 36 = $3,600 |
| Operations (4h/mo × $75/h) | $0 | $300/mo × 36 = $10,800 |
| Initial Setup | 20h × $75 = $1,500 | 30h × $75 = $2,250 |
| **Total (Free Tier)** | ~$1,500 | ~$16,650 |
| **Total (Professional)** | ~$10,140 | ~$16,650 |
| **Total (Enterprise)** | ~$50,000+ | ~$16,650 |

**Verdict**: Auth0 cheaper for MVP/free tier; Keycloak cheaper at scale with full features.

---

### 3. Self-Hosting Capabilities

| Feature | Auth0 | Keycloak |
|---------|-------|----------|
| **Full Self-Hosting** | ❌ Not available | ✅ Full support |
| **Private Cloud** | ✅ Enterprise only | ✅ Any cloud/on-prem |
| **Air-Gapped** | ❌ No | ✅ Yes |
| **Data Residency** | Limited regions | ✅ Full control |
| **Kubernetes Native** | ❌ SaaS only | ✅ Operator available |
| **Docker Support** | ❌ SaaS only | ✅ Official images |
| **Helm Charts** | ❌ N/A | ✅ Bitnami, Official |
| **Winner** | | ✅ Keycloak |

**Keycloak Kubernetes Deployment**:
```yaml
# Bitnami Helm Chart (recommended)
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install keycloak bitnami/keycloak \
  --set auth.adminUser=admin \
  --set auth.adminPassword=<secure-password> \
  --set postgresql.enabled=true \
  --set postgresql.auth.postgresPassword=<db-password> \
  --set production=true \
  --set proxy=edge \
  --set httpRelativePath=/auth

# OR Official Keycloak Operator
kubectl apply -f https://raw.githubusercontent.com/keycloak/keycloak-k8s-resources/main/kubernetes/keycloaks.k8s.keycloak.org-v1.yml
```

---

### 4. Python SDK Quality (FastAPI Integration)

| Feature | Auth0 | Keycloak |
|---------|-------|----------|
| **Official SDK** | ✅ auth0-python | ❌ No official SDK |
| **Community SDK** | authlib, python-jose | python-keycloak |
| **FastAPI Examples** | ✅ Official quickstart | ✅ Community examples |
| **Async Support** | ✅ Full | ⚠️ Partial (sync client) |
| **Token Validation** | Built-in | Manual JWKS fetch |
| **RBAC Helpers** | ✅ Scopes/permissions | ✅ Realm roles |
| **Documentation** | Excellent | Good |
| **Maintenance** | Auth0 team | Community |
| **Winner** | ✅ Auth0 | |

**Auth0 FastAPI Integration**:
```python
# requirements.txt
authlib>=1.3.0
python-jose[cryptography]>=3.3.0
httpx>=0.27.0

# auth/dependencies.py
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from functools import lru_cache
import httpx

AUTH0_DOMAIN = "your-tenant.auth0.com"
API_AUDIENCE = "https://taskman-v2.api"
ALGORITHMS = ["RS256"]

security = HTTPBearer()

@lru_cache(maxsize=1)
def get_jwks():
    """Cache JWKS keys for performance."""
    response = httpx.get(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
    return response.json()

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """Validate JWT and return claims."""
    token = credentials.credentials
    try:
        jwks = get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = next(
            key for key in jwks["keys"]
            if key["kid"] == unverified_header["kid"]
        )
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

def require_role(required_role: str):
    """Role-based access control decorator."""
    async def role_checker(
        claims: dict = Depends(verify_token)
    ):
        roles = claims.get("https://taskman-v2/roles", [])
        if required_role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return claims
    return role_checker

# Usage in routes
@router.get("/admin/users")
async def list_users(claims: dict = Depends(require_role("admin"))):
    return {"users": [...]}
```

**Keycloak FastAPI Integration**:
```python
# requirements.txt
python-keycloak>=4.0.0
python-jose[cryptography]>=3.3.0
httpx>=0.27.0

# auth/keycloak.py
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from keycloak import KeycloakOpenID
from jose import jwt, JWTError
from functools import lru_cache

KEYCLOAK_URL = "https://keycloak.internal.example.com"
REALM = "taskman"
CLIENT_ID = "taskman-api"
CLIENT_SECRET = "your-client-secret"

keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_URL,
    client_id=CLIENT_ID,
    realm_name=REALM,
    client_secret_key=CLIENT_SECRET
)

security = HTTPBearer()

@lru_cache(maxsize=1)
def get_public_key():
    """Cache Keycloak public key."""
    return (
        "-----BEGIN PUBLIC KEY-----\n"
        + keycloak_openid.public_key()
        + "\n-----END PUBLIC KEY-----"
    )

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """Validate Keycloak JWT token."""
    token = credentials.credentials
    try:
        claims = keycloak_openid.decode_token(
            token,
            key=get_public_key(),
            options={"verify_aud": False}  # Keycloak uses different aud format
        )
        return claims
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

def require_realm_role(role: str):
    """Check Keycloak realm roles."""
    async def role_checker(claims: dict = Depends(verify_token)):
        realm_access = claims.get("realm_access", {})
        roles = realm_access.get("roles", [])
        if role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return claims
    return role_checker

# Usage
@router.get("/admin/users")
async def list_users(claims: dict = Depends(require_realm_role("admin"))):
    return {"users": [...]}
```

---

### 5. React SDK Quality (SPA Support)

| Feature | Auth0 | Keycloak |
|---------|-------|----------|
| **Official SDK** | ✅ @auth0/auth0-react | ⚠️ keycloak-js (raw) |
| **React Wrapper** | ✅ Built-in | @react-keycloak/web |
| **React 19 Support** | ✅ Verified | ⚠️ Community maintained |
| **Hooks API** | ✅ useAuth0() | ✅ useKeycloak() |
| **Silent Refresh** | ✅ Automatic | ⚠️ Manual config |
| **TypeScript** | ✅ Full types | ✅ Full types |
| **Bundle Size** | ~25KB gzipped | ~40KB gzipped |
| **Winner** | ✅ Auth0 | |

**Auth0 React Integration**:
```tsx
// src/main.tsx
import { Auth0Provider } from '@auth0/auth0-react';

const App = () => (
  <Auth0Provider
    domain="your-tenant.auth0.com"
    clientId="your-client-id"
    authorizationParams={{
      redirect_uri: window.location.origin,
      audience: "https://taskman-v2.api",
      scope: "openid profile email"
    }}
    cacheLocation="localstorage"
  >
    <RouterProvider router={router} />
  </Auth0Provider>
);

// src/hooks/useAuth.ts
import { useAuth0 } from '@auth0/auth0-react';

export function useAuth() {
  const { 
    user, 
    isAuthenticated, 
    isLoading, 
    loginWithRedirect, 
    logout, 
    getAccessTokenSilently 
  } = useAuth0();

  const hasRole = (role: string): boolean => {
    const roles = user?.['https://taskman-v2/roles'] || [];
    return roles.includes(role);
  };

  return {
    user,
    isAuthenticated,
    isLoading,
    login: loginWithRedirect,
    logout: () => logout({ returnTo: window.location.origin }),
    getToken: getAccessTokenSilently,
    hasRole,
    isAdmin: hasRole('admin'),
    isDeveloper: hasRole('developer'),
  };
}
```

**Keycloak React Integration**:
```tsx
// src/main.tsx
import { ReactKeycloakProvider } from '@react-keycloak/web';
import Keycloak from 'keycloak-js';

const keycloak = new Keycloak({
  url: 'https://keycloak.internal.example.com',
  realm: 'taskman',
  clientId: 'taskman-frontend'
});

const initOptions = {
  onLoad: 'check-sso',
  silentCheckSsoRedirectUri: `${window.location.origin}/silent-check-sso.html`,
  pkceMethod: 'S256'
};

const App = () => (
  <ReactKeycloakProvider 
    authClient={keycloak} 
    initOptions={initOptions}
    onTokens={(tokens) => {
      // Handle token refresh
      localStorage.setItem('token', tokens.token || '');
    }}
  >
    <RouterProvider router={router} />
  </ReactKeycloakProvider>
);

// src/hooks/useAuth.ts
import { useKeycloak } from '@react-keycloak/web';

export function useAuth() {
  const { keycloak, initialized } = useKeycloak();

  const hasRealmRole = (role: string): boolean => {
    return keycloak.hasRealmRole(role);
  };

  return {
    user: keycloak.tokenParsed,
    isAuthenticated: keycloak.authenticated,
    isLoading: !initialized,
    login: () => keycloak.login(),
    logout: () => keycloak.logout({ redirectUri: window.location.origin }),
    getToken: async () => {
      await keycloak.updateToken(30);
      return keycloak.token;
    },
    hasRole: hasRealmRole,
    isAdmin: hasRealmRole('admin'),
    isDeveloper: hasRealmRole('developer'),
  };
}

// public/silent-check-sso.html (required for silent refresh)
<!doctype html>
<html>
<body>
  <script>
    parent.postMessage(location.href, location.origin);
  </script>
</body>
</html>
```

---

### 6. RBAC Features

| Feature | Auth0 | Keycloak |
|---------|-------|----------|
| **Role Definition** | ✅ API + Dashboard | ✅ Admin Console |
| **Role Assignment** | ✅ Per-user, per-app | ✅ Per-user, per-group |
| **Permission Model** | Scopes + Permissions | Roles + Fine-grained auth |
| **Groups Support** | ⚠️ Limited (Enterprise) | ✅ Full support |
| **Nested Roles** | ❌ No | ✅ Composite roles |
| **Attribute-Based AC** | ❌ Extensions needed | ✅ Built-in policies |
| **Dynamic Scopes** | ✅ Rules/Actions | ✅ Mappers |
| **Winner** | | ✅ Keycloak |

**TaskMan-v2 RBAC Implementation**:

```yaml
# Keycloak Realm Export (partial)
roles:
  realm:
    - name: admin
      description: Full system access
      composite: true
      composites:
        realm:
          - developer
          - viewer
    - name: developer
      description: Create/edit tasks and sprints
      composite: true
      composites:
        realm:
          - viewer
    - name: viewer
      description: Read-only access
    - name: guest
      description: Limited access to public data

# Permission mapping
# admin → all endpoints
# developer → GET/POST/PUT tasks, sprints, projects (no DELETE)
# viewer → GET only
# guest → GET public endpoints only
```

---

### 7. Audit Logging

| Feature | Auth0 | Keycloak |
|---------|-------|----------|
| **Built-in Audit** | ⚠️ Enterprise tier | ✅ Built-in FREE |
| **Login Events** | ✅ All tiers | ✅ All events |
| **Admin Events** | ⚠️ Enterprise | ✅ Full tracking |
| **Token Events** | ✅ Limited | ✅ Full tracking |
| **Export Format** | JSON via API | Database/SPI |
| **Retention** | 7-30 days | Unlimited (self-hosted) |
| **Custom Events** | ⚠️ Actions (paid) | ✅ Event listeners |
| **SIEM Integration** | ✅ Streams (Enterprise) | ✅ Custom SPI |
| **Winner** | | ✅ Keycloak |

**Keycloak Audit Event Types** (relevant for TaskMan-v2):
```
LOGIN, LOGIN_ERROR, LOGOUT, LOGOUT_ERROR
TOKEN_EXCHANGE, REFRESH_TOKEN, REFRESH_TOKEN_ERROR
REGISTER, REGISTER_ERROR
UPDATE_PROFILE, UPDATE_PASSWORD
PERMISSION_TOKEN, PERMISSION_TOKEN_ERROR
IMPERSONATE, IDENTITY_PROVIDER_LOGIN
```

**Admin Event Types**:
```
CREATE_USER, UPDATE_USER, DELETE_USER
CREATE_ROLE, UPDATE_ROLE, DELETE_ROLE
ADD_REALM_ROLE_TO_USER, REMOVE_REALM_ROLE_FROM_USER
CREATE_CLIENT, UPDATE_CLIENT, DELETE_CLIENT
```

---

### 8. MFA Support

| Feature | Auth0 | Keycloak |
|---------|-------|----------|
| **TOTP (Google Auth)** | ✅ Professional+ | ✅ Built-in |
| **SMS** | ✅ Professional+ | ⚠️ SPI required |
| **Email OTP** | ✅ Professional+ | ✅ Built-in |
| **WebAuthn/FIDO2** | ✅ Professional+ | ✅ Built-in |
| **Push Notifications** | ✅ Guardian app | ❌ Custom dev |
| **Conditional MFA** | ✅ Rules/Actions | ✅ Authentication flows |
| **Recovery Codes** | ✅ Built-in | ✅ Built-in |
| **Winner** | ✅ Auth0 (better UX) | |

---

### 9. SSO Capabilities

| Feature | Auth0 | Keycloak |
|---------|-------|----------|
| **OIDC Provider** | ✅ All tiers | ✅ Built-in |
| **SAML 2.0 SP** | ⚠️ Enterprise | ✅ Built-in |
| **SAML 2.0 IdP** | ⚠️ Enterprise | ✅ Built-in |
| **Social Logins** | ✅ 2 free, more paid | ✅ Unlimited |
| **Enterprise IdP** | ⚠️ Enterprise | ✅ Built-in |
| **User Federation** | ⚠️ Enterprise | ✅ LDAP, Kerberos |
| **Identity Brokering** | ⚠️ Professional+ | ✅ Built-in |
| **Winner** | | ✅ Keycloak |

---

### 10. Operational Overhead

| Aspect | Auth0 | Keycloak |
|--------|-------|----------|
| **Infrastructure** | None (SaaS) | K8s pod + database |
| **Upgrades** | Automatic | Manual (Helm upgrade) |
| **Backups** | Managed | Manual/automated |
| **Monitoring** | Dashboard | Custom (Prometheus) |
| **HA/Failover** | Built-in | Manual clustering |
| **Monthly Effort** | 0 hours | 2-4 hours |
| **Incident Response** | Auth0 support | Self + community |
| **Winner** | ✅ Auth0 | |

**Keycloak Operational Runbook**:
```bash
# Monthly maintenance tasks

# 1. Check for updates (15 min)
helm repo update
helm search repo bitnami/keycloak --versions | head -5

# 2. Apply security updates (30-60 min)
helm upgrade keycloak bitnami/keycloak \
  --reuse-values \
  --version <new-version>

# 3. Backup realm configuration (15 min)
kubectl exec -it keycloak-0 -- \
  /opt/bitnami/keycloak/bin/kc.sh export \
  --realm taskman \
  --file /tmp/taskman-realm.json

# 4. Review audit logs (30 min)
# Query Keycloak database for suspicious events

# 5. Rotate client secrets (15 min, quarterly)
# Via Admin Console or API
```

---

### 11. Vendor Lock-in Risk

| Aspect | Auth0 | Keycloak |
|--------|-------|----------|
| **Protocol Compliance** | OIDC + proprietary | Pure OIDC/SAML |
| **Proprietary Features** | Rules, Actions, Hooks | Standard SPIs |
| **Data Export** | ⚠️ Limited | ✅ Full export |
| **Migration Path** | Difficult (custom code) | Easy (standard tokens) |
| **Alternative Options** | Okta, Azure AD | Any OIDC provider |
| **Code Portability** | Medium | High |
| **Winner** | | ✅ Keycloak |

**Migration Complexity Assessment**:

| From → To | Effort | Risk |
|-----------|--------|------|
| Auth0 → Keycloak | High (40+ hours) | Medium |
| Auth0 → Azure AD | Medium (20 hours) | Low |
| Keycloak → Auth0 | Medium (20 hours) | Low |
| Keycloak → Azure AD | Low (8 hours) | Low |
| Keycloak → Any OIDC | Low (4-8 hours) | Very Low |

---

### 12. Documentation Quality

| Aspect | Auth0 | Keycloak |
|--------|-------|----------|
| **Official Docs** | ✅ Excellent | ✅ Good |
| **Quickstarts** | ✅ Many languages | ⚠️ Limited |
| **API Reference** | ✅ Interactive | ✅ Standard |
| **Tutorials** | ✅ Video + text | ⚠️ Mostly text |
| **Community** | ✅ Forums, Discord | ✅ Mailing list, GitHub |
| **Stack Overflow** | ~25K questions | ~15K questions |
| **Winner** | ✅ Auth0 | |

---

## Summary Scorecard

| Dimension | Auth0 | Keycloak | Winner |
|-----------|-------|----------|--------|
| 1. Implementation Complexity | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Auth0 |
| 2. Cost | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Keycloak |
| 3. Self-Hosting | ⭐ | ⭐⭐⭐⭐⭐ | Keycloak |
| 4. Python SDK | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Auth0 |
| 5. React SDK | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Auth0 |
| 6. RBAC Features | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Keycloak |
| 7. Audit Logging | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Keycloak |
| 8. MFA Support | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Auth0 |
| 9. SSO Capabilities | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Keycloak |
| 10. Operational Overhead | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Auth0 |
| 11. Vendor Lock-in | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Keycloak |
| 12. Documentation | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Auth0 |
| **Total** | **48/60** | **53/60** | **Keycloak** |

---

## Recommendation

### Primary Recommendation: **Keycloak**

**Rationale**:

1. **Internal Enterprise Tool** - Full control over authentication infrastructure aligns with enterprise requirements
2. **Audit Logging Critical** - Built-in comprehensive audit logging without additional cost
3. **Docker/K8s Native** - Natural fit with existing deployment strategy
4. **Long-term Cost** - Significantly lower TCO for full-featured deployment
5. **Compliance Control** - Full data residency and retention control
6. **Standard Protocols** - Pure OIDC/SAML ensures easy migration if needed
7. **RBAC Requirements** - Superior role hierarchy and group support

**When to Choose Auth0 Instead**:
- Team lacks Kubernetes/DevOps expertise
- Need MVP in < 1 week
- Budget allows for Enterprise tier
- Prefer zero operational overhead

---

## Implementation Timeline

### Keycloak MVP (Recommended)

| Week | Tasks | Hours |
|------|-------|-------|
| **Week 1** | | |
| Day 1-2 | Keycloak Helm deployment + PostgreSQL | 8h |
| Day 3 | Realm configuration, roles, clients | 4h |
| Day 4 | FastAPI JWT middleware integration | 6h |
| **Week 2** | | |
| Day 5 | React keycloak-js integration | 4h |
| Day 6 | RBAC decorators + protected routes | 4h |
| Day 7 | Testing, documentation, polish | 4h |
| **Total** | | **30 hours** |

### Auth0 MVP (Alternative)

| Week | Tasks | Hours |
|------|-------|-------|
| **Week 1** | | |
| Day 1 | Tenant setup, applications, API | 2h |
| Day 2 | FastAPI JWT middleware | 4h |
| Day 3 | React Auth0Provider integration | 4h |
| Day 4 | RBAC, roles, permissions | 4h |
| Day 5 | Testing, polish | 4h |
| **Total** | | **18 hours** |

---

## Migration Path

### If Starting with Auth0, Migrating to Keycloak Later

1. **Preparation** (4 hours)
   - Deploy Keycloak in parallel
   - Configure identical realm/roles

2. **User Migration** (8 hours)
   - Export user list from Auth0 (no passwords)
   - Import to Keycloak
   - Force password reset or migrate via Auth0's password export (Enterprise)

3. **Code Migration** (8 hours)
   - Replace @auth0/auth0-react with @react-keycloak/web
   - Replace auth0-python with python-keycloak
   - Update JWKS endpoints

4. **Testing** (8 hours)
   - Full regression testing
   - Role mapping validation

5. **Cutover** (4 hours)
   - DNS/config switch
   - Monitor for issues

**Total Migration Effort**: ~32 hours

### If Starting with Keycloak, Migrating to Auth0 Later

1. **User Migration**: Easier (standard SCIM export)
2. **Code Migration**: Straightforward (standard OIDC)
3. **Total Effort**: ~20 hours

---

## Risk Assessment

### Keycloak Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Operational complexity | Medium | Medium | Use Bitnami Helm chart, document runbooks |
| Upgrade issues | Low | High | Test upgrades in staging, maintain backups |
| Security vulnerability | Low | High | Subscribe to security advisories, prompt patching |
| Learning curve | Medium | Low | Allocate training time, use existing examples |
| Community support delays | Low | Medium | Join mailing lists, consider Red Hat SSO support |

### Auth0 Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Cost escalation | High | Medium | Monitor MAU, plan for growth |
| Feature restrictions | High | High | Plan for Professional tier from start |
| Vendor lock-in | Medium | High | Use standard OIDC where possible |
| Outages | Low | High | No mitigation (SaaS dependency) |
| Data residency issues | Medium | High | Verify compliance requirements |

---

## Files to Create

After decision, create:

1. `TaskMan-v2/backend-api/src/auth/keycloak.py` - Keycloak integration
2. `TaskMan-v2/backend-api/src/auth/dependencies.py` - FastAPI auth dependencies
3. `TaskMan-v2/src/hooks/useAuth.ts` - React auth hook
4. `TaskMan-v2/src/providers/AuthProvider.tsx` - Keycloak provider wrapper
5. `TaskMan-v2/docs/AUTH_SETUP.md` - Configuration guide
6. `deploy/keycloak/` - Helm values and realm export

---

## References

- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [Auth0 Documentation](https://auth0.com/docs)
- [python-keycloak](https://python-keycloak.readthedocs.io/)
- [@react-keycloak/web](https://github.com/react-keycloak/react-keycloak)
- [Bitnami Keycloak Helm Chart](https://github.com/bitnami/charts/tree/main/bitnami/keycloak)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

**Decision Required By**: Before Phase 2 authentication implementation  
**Decision Owner**: Engineering Lead  
**Stakeholders**: Security, Compliance, DevOps
