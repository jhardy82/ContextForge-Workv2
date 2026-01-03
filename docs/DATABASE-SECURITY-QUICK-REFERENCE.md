# Database Security Quick Reference

**Version**: 1.0
**Date**: 2025-12-29

---

## ✅ Development Environment (Current Status)

### Safe for Local Development
- ✅ Hardcoded credentials acceptable (documented as dev-only)
- ✅ .env files properly .gitignored (verified no commits)
- ✅ Docker containers running on localhost
- ✅ Credential helpers provide masked output option
- ⚠️ Recommend binding ports to 127.0.0.1 (currently 0.0.0.0)

---

## 🔴 Production Environment Blockers

### CRITICAL - Must Complete Before Production

#### 1️⃣ Rotate Production Credentials
```bash
# Current: contextforge/contextforge (WEAK - same as dev)
# Required: Strong unique password in Azure Key Vault

# Generate strong password
openssl rand -base64 24
# Example: K8xP2mR9vL4nQ1wS7jC0yH5zT

# Store in Key Vault
az keyvault secret set \
  --vault-name contextforge-vault \
  --name db-password \
  --value "GENERATED_PASSWORD"
```

**Impact**: 🔴 **HIGH** - Production database accessible with dev credentials

---

#### 2️⃣ Environment Variable Support
```bash
# ✅ COMPLETED - Both helpers support env vars

# Set these in production:
export PG_HOST="172.25.14.122"
export PG_PORT="5432"
export PG_USER="contextforge_prod"
export PG_PASSWORD="$(az keyvault secret show ...)"
export ENVIRONMENT="production"
```

**Impact**: 🔴 **HIGH** - Prevents hardcoded production credentials

---

#### 3️⃣ Localhost-Only Port Binding
```yaml
# Current: "5434:5432" binds to 0.0.0.0
# Required: "127.0.0.1:5434:5432"

# Update docker-compose files:
ports:
  - "127.0.0.1:5434:5432"  # ✅ Localhost only
```

**Impact**: 🟡 **MEDIUM** - Reduces attack surface

---

#### 4️⃣ Document SQL Injection Prevention
```python
# ✅ COMPLETED - Examples in security review

# Always use parameterized queries:
cursor.execute(
    "SELECT * FROM tasks WHERE id = %s",
    (task_id,)  # ✅ Safe
)

# NEVER use f-strings:
# cursor.execute(f"SELECT * FROM tasks WHERE id = {task_id}")  # ❌ VULNERABLE
```

**Impact**: 🟡 **MEDIUM** - Prevents SQL injection attacks

---

## 📋 Pre-Production Deployment Checklist

### Before deploying to production, verify:

- [ ] **Production credentials rotated** (not "contextforge/contextforge")
- [ ] **Azure Key Vault configured** with all secrets
- [ ] **Environment variables set** (PG_HOST, PG_PORT, PG_USER, PG_PASSWORD)
- [ ] **Docker ports bound to 127.0.0.1** (all containers)
- [ ] **Separate dev/prod environments** documented
- [ ] **Pre-commit hook installed** (blocks .env commits)
- [ ] **Parameterized queries** used throughout codebase
- [ ] **Audit logging enabled** (credential access)
- [ ] **Security review approved** by security team
- [ ] **Deployment guide followed** (docs/PRODUCTION-DATABASE-DEPLOYMENT.md)

---

## 🔍 Quick Security Validation

### Run these checks before production deployment:

```bash
# 1. Verify no .env files committed
git ls-files | grep "^\.env$"
# Expected: (no output)

# 2. Verify production credentials different
echo $PG_PASSWORD
# Expected: NOT "contextforge"

# 3. Verify localhost-only binding
docker ps --format '{{.Ports}}' | grep "0.0.0.0.*543[0-9]"
# Expected: (no output) OR "127.0.0.1:5434->5432/tcp"

# 4. Test Key Vault access
az keyvault secret show --vault-name contextforge-vault --name db-password
# Expected: Shows secret value

# 5. Verify SQL injection protection
grep -r "execute(f\"" . --include="*.py"
# Expected: (no results) OR only parameterized queries
```

---

## 📚 Documentation Links

- **Full Security Review**: [SECURITY-REVIEW-DATABASE-ACCESS.md](../SECURITY-REVIEW-DATABASE-ACCESS.md)
- **Production Deployment Guide**: [docs/PRODUCTION-DATABASE-DEPLOYMENT.md](../docs/PRODUCTION-DATABASE-DEPLOYMENT.md)
- **Database Access Guide**: [docs/AGENT-DATABASE-ACCESS.md](../docs/AGENT-DATABASE-ACCESS.md)

---

## 🆘 Emergency Contacts

**Security Issues**: security@contextforge.com
**Database Issues**: devops@contextforge.com
**Incident Response**: incident@contextforge.com

---

## 🔐 Security Rating

| Environment | Rating | Status |
|-------------|--------|--------|
| **Development** | 🟢 **ACCEPTABLE** | Safe for local use |
| **Production** | 🔴 **BLOCKS DEPLOYMENT** | Critical fixes required |

**Production Deployment**: ❌ **BLOCKED** until critical items completed

---

**Last Updated**: 2025-12-29
**Next Review**: Before production deployment
