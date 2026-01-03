# Production Database Deployment Guide

**Version**: 1.0
**Date**: 2025-12-29
**Security Review**: [SECURITY-REVIEW-DATABASE-ACCESS.md](../SECURITY-REVIEW-DATABASE-ACCESS.md)

---

## Overview

This guide provides step-by-step instructions for **secure production deployment** of database access, addressing security findings from the database security review.

**⚠️ CRITICAL**: Do NOT deploy to production without completing ALL critical security items.

---

## Prerequisites

- [ ] Reviewed [SECURITY-REVIEW-DATABASE-ACCESS.md](../SECURITY-REVIEW-DATABASE-ACCESS.md)
- [ ] Access to Azure Key Vault (or equivalent secrets manager)
- [ ] Production database provisioned (PostgreSQL 16+)
- [ ] Firewall rules configured (database accessible only from app servers)

---

## Production Deployment Checklist

### 🔴 CRITICAL (Must Complete Before Production)

#### 1. Rotate Production Credentials

**Status**: ❌ **BLOCKER - Must complete**

```bash
# Generate strong password (16+ characters)
$prodPassword = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 24 | ForEach-Object {[char]$_})
# Example output: K8xP2mR9vL4nQ1wS7jC0yH

# Connect to production database
psql -h 172.25.14.122 -U postgres -d taskman_v2

# Create production user with strong password
CREATE USER contextforge_prod WITH PASSWORD 'YOUR_STRONG_PASSWORD_HERE';
GRANT ALL PRIVILEGES ON DATABASE taskman_v2 TO contextforge_prod;

# Revoke default user (if not needed)
REVOKE ALL PRIVILEGES ON DATABASE taskman_v2 FROM contextforge;
DROP USER contextforge;  -- Only if not used elsewhere
```

**Verification**:
```bash
# Test new credentials
psql -h 172.25.14.122 -U contextforge_prod -d taskman_v2 -c "SELECT 1;"
```

---

#### 2. Configure Azure Key Vault (or Equivalent)

**Status**: ❌ **BLOCKER - Must complete**

```bash
# Create Azure Key Vault (if not exists)
az keyvault create \
  --name contextforge-prod-vault \
  --resource-group contextforge-prod-rg \
  --location eastus

# Store database credentials
az keyvault secret set \
  --vault-name contextforge-prod-vault \
  --name db-host \
  --value "172.25.14.122"

az keyvault secret set \
  --vault-name contextforge-prod-vault \
  --name db-port \
  --value "5432"

az keyvault secret set \
  --vault-name contextforge-prod-vault \
  --name db-name \
  --value "taskman_v2"

az keyvault secret set \
  --vault-name contextforge-prod-vault \
  --name db-user \
  --value "contextforge_prod"

az keyvault secret set \
  --vault-name contextforge-prod-vault \
  --name db-password \
  --value "YOUR_STRONG_PASSWORD_HERE"  # From step 1

# Grant application access
az keyvault set-policy \
  --name contextforge-prod-vault \
  --object-id YOUR_APP_MANAGED_IDENTITY_ID \
  --secret-permissions get list
```

**Verification**:
```bash
# Test retrieval
az keyvault secret show \
  --vault-name contextforge-prod-vault \
  --name db-password \
  --query value -o tsv
```

---

#### 3. Update Credential Helpers for Production

**Status**: ✅ **COMPLETED** (Environment variable support added)

**Python** (`scripts/db_auth.py`):
```python
# ✅ Already supports environment variables
# Set these in production environment:
export PG_HOST="172.25.14.122"
export PG_PORT="5432"
export PG_DATABASE="taskman_v2"
export PG_USER="contextforge_prod"
export PG_PASSWORD="$(az keyvault secret show --vault-name contextforge-prod-vault --name db-password --query value -o tsv)"
export ENVIRONMENT="production"  # Triggers security warnings
```

**PowerShell** (`scripts/Get-DatabaseCredentials.ps1`):
```powershell
# ✅ Already supports environment variables
# Set these in production environment:
$env:PG_HOST = "172.25.14.122"
$env:PG_PORT = "5432"
$env:PG_DATABASE = "taskman_v2"
$env:PG_USER = "contextforge_prod"
$env:PG_PASSWORD = (az keyvault secret show --vault-name contextforge-prod-vault --name db-password --query value -o tsv)
$env:ENVIRONMENT = "production"  # Triggers security warnings
```

---

#### 4. Bind Docker Ports to Localhost Only

**Status**: ❌ **BLOCKER - Must complete**

**Update all Docker Compose files**:

```yaml
# docker-compose.taskman.yml - BEFORE
services:
  taskman-postgres:
    ports:
      - "5434:5432"  # ❌ Binds to 0.0.0.0 (all interfaces)

# docker-compose.taskman.yml - AFTER
services:
  taskman-postgres:
    ports:
      - "127.0.0.1:5434:5432"  # ✅ Localhost only
```

**Files to update**:
- [x] docker-compose.taskman.yml (port 5434)
- [ ] docker-compose.dev.yml (port 5435)
- [ ] docker-compose.test.yml (port 5433)
- [ ] All other compose files with exposed database ports

**Verification**:
```powershell
# Should NOT be accessible from network
Test-NetConnection -ComputerName YOUR_MACHINE_IP -Port 5434  # Should fail

# Should be accessible from localhost
Test-NetConnection -ComputerName 127.0.0.1 -Port 5434  # Should succeed
```

---

#### 5. Separate Development and Production Environments

**Status**: ❌ **BLOCKER - Must complete**

**Create separate configuration files**:

```bash
# .env.development (COMMITTED as .env.example)
PG_HOST=localhost
PG_PORT=5434
PG_DATABASE=taskman_v2
PG_USER=contextforge_dev
PG_PASSWORD=contextforge  # OK for local development

# .env.production (NEVER COMMITTED - .gitignored)
PG_HOST=172.25.14.122
PG_PORT=5432
PG_DATABASE=taskman_v2
PG_USER=contextforge_prod
PG_PASSWORD=${KEYVAULT_SECRET}  # Loaded at runtime

# .env.staging (NEVER COMMITTED - .gitignored)
PG_HOST=staging-db.internal
PG_PORT=5432
PG_DATABASE=taskman_v2
PG_USER=contextforge_staging
PG_PASSWORD=${KEYVAULT_SECRET}  # Loaded at runtime
```

**Load at runtime**:
```bash
# Production deployment script
#!/bin/bash
set -e

# Load production secrets from Key Vault
export PG_PASSWORD=$(az keyvault secret show \
  --vault-name contextforge-prod-vault \
  --name db-password \
  --query value -o tsv)

# Load .env.production (other non-secret configs)
source .env.production

# Start application
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

### 🟡 RECOMMENDED (Should Complete Before Production)

#### 6. Document Parameterized Query Patterns

**Status**: ✅ **COMPLETED** (Examples in security review)

**Add to developer documentation**:

```python
# ✅ SECURE: Always use parameterized queries
import psycopg2
from scripts.db_auth import get_db_credentials

creds = get_db_credentials('postgresql', format='dict')
conn = psycopg2.connect(**{
    'host': creds['host'],
    'port': creds['port'],
    'database': creds['database'],
    'user': creds['user'],
    'password': creds['password']
})

# Parameterized query (prevents SQL injection)
cursor = conn.cursor()
task_id = request.args.get('id')  # User input
cursor.execute(
    "SELECT * FROM tasks WHERE id = %s",
    (task_id,)  # ✅ Safely escaped parameter
)

# ❌ NEVER do this (SQL injection vulnerability)
# cursor.execute(f"SELECT * FROM tasks WHERE id = {task_id}")
```

---

#### 7. Add Pre-Commit Hook to Block .env Files

**Status**: ❌ **RECOMMENDED**

**Create `.git/hooks/pre-commit`**:

```bash
#!/bin/bash
# Pre-commit hook to prevent committing .env files

# Check for .env files in staged changes
if git diff --cached --name-only | grep -E "^\.env$|^\.env\..*$" | grep -v "\.env\.example$" | grep -v "\.env\.template$"; then
    echo "❌ ERROR: Attempting to commit .env file with potential secrets!"
    echo "📝 Use .env.example or .env.template instead."
    echo "🔒 Actual .env files should remain .gitignored."
    exit 1
fi

echo "✅ Pre-commit checks passed"
exit 0
```

```bash
# Make executable
chmod +x .git/hooks/pre-commit
```

---

#### 8. Enforce Password Complexity

**Status**: ❌ **RECOMMENDED**

**PostgreSQL Server Configuration** (`postgresql.conf`):

```ini
# Enable password encryption (default in PostgreSQL 10+)
password_encryption = scram-sha-256

# Require SSL connections (production only)
ssl = on
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'
```

**Application-level validation**:

```python
# Validate password complexity before creating users
import re

def validate_password(password: str) -> bool:
    """Validate password meets complexity requirements."""
    if len(password) < 16:
        raise ValueError("Password must be at least 16 characters")

    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain uppercase letter")

    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain lowercase letter")

    if not re.search(r'[0-9]', password):
        raise ValueError("Password must contain number")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValueError("Password must contain special character")

    return True
```

---

#### 9. Implement Audit Logging

**Status**: ❌ **RECOMMENDED**

**Add logging to credential access**:

```python
# scripts/db_auth.py - Enhanced with audit logging
import logging
import os
from datetime import datetime

# Configure audit logger (separate from application logs)
audit_logger = logging.getLogger('db_auth.audit')
audit_logger.setLevel(logging.INFO)

# File handler for audit trail
audit_handler = logging.FileHandler('logs/db_credential_access.audit.log')
audit_handler.setFormatter(logging.Formatter(
    '{"timestamp": "%(asctime)s", "event": "%(message)s"}'
))
audit_logger.addHandler(audit_handler)

def get_db_credentials(database="all", format="dict", mask_password=False):
    """Get database credentials with audit logging."""

    # Audit log (PII-safe)
    audit_logger.info(
        f"database={database}, format={format}, masked={mask_password}, "
        f"user={os.getenv('USER', 'unknown')}, "
        f"hostname={os.getenv('HOSTNAME', 'unknown')}"
    )

    # ... rest of function
```

---

#### 10. Use Docker Secrets for Production

**Status**: ❌ **RECOMMENDED**

**Create Docker secret**:

```bash
# Create secret from file
echo "YOUR_STRONG_PASSWORD" | docker secret create db_password -

# Or from Azure Key Vault
az keyvault secret show \
  --vault-name contextforge-prod-vault \
  --name db-password \
  --query value -o tsv | docker secret create db_password -
```

**Update Docker Compose for production**:

```yaml
# docker-compose.prod.yml
services:
  database:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: taskman_v2
      POSTGRES_USER: contextforge_prod
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password  # ✅ From secret
    ports:
      - "127.0.0.1:5432:5432"
    secrets:
      - db_password

secrets:
  db_password:
    external: true  # Created separately
```

---

### 🟢 OPTIONAL (Nice-to-Have)

#### 11. Document Connection Pooling

**Status**: ✅ **COMPLETED** (Examples in security review)

**Best practices**:
- Use SQLAlchemy connection pooling
- Pool size: 5-10 connections per worker
- Max overflow: 10-20 connections
- Pool timeout: 30 seconds
- Connection recycle: 1 hour

**Example**:
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "postgresql://user:pass@host/db",
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
)
```

---

#### 12. Credential Rotation Policy

**Status**: ❌ **OPTIONAL**

**Implement automated rotation** (every 90 days):

```bash
#!/bin/bash
# rotate-db-credentials.sh - Run quarterly

# Generate new password
NEW_PASSWORD=$(openssl rand -base64 24)

# Update database
psql -h 172.25.14.122 -U postgres -c \
  "ALTER USER contextforge_prod PASSWORD '$NEW_PASSWORD';"

# Update Key Vault
az keyvault secret set \
  --vault-name contextforge-prod-vault \
  --name db-password \
  --value "$NEW_PASSWORD"

# Restart applications (picks up new password from Key Vault)
kubectl rollout restart deployment/contextforge-api
```

**Schedule with cron or Azure Automation**:
```cron
# Rotate credentials quarterly (first day of Jan, Apr, Jul, Oct)
0 0 1 1,4,7,10 * /usr/local/bin/rotate-db-credentials.sh
```

---

## Deployment Process

### 1. Pre-Deployment Checklist

- [ ] All CRITICAL items completed
- [ ] All RECOMMENDED items completed (or documented why skipped)
- [ ] Production credentials rotated and stored in Key Vault
- [ ] Docker port bindings updated to 127.0.0.1
- [ ] Environment variables configured for production
- [ ] Pre-commit hooks installed
- [ ] Audit logging enabled
- [ ] Security review approved

### 2. Deployment Steps

```bash
# 1. Set production environment
export ENVIRONMENT=production

# 2. Load secrets from Key Vault
export PG_PASSWORD=$(az keyvault secret show \
  --vault-name contextforge-prod-vault \
  --name db-password \
  --query value -o tsv)

# 3. Load production environment variables
source .env.production

# 4. Verify configuration (masked)
python -c "from scripts.db_auth import get_db_credentials; \
  print(get_db_credentials('postgresql', format='url', mask_password=True))"
# Output: postgresql://contextforge_prod:***@172.25.14.122:5432/taskman_v2

# 5. Test database connectivity
python -c "from scripts.db_auth import test_connection; \
  print('Connection OK' if test_connection('postgresql') else 'Connection FAILED')"

# 6. Deploy application
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Post-Deployment Verification

```bash
# Check application started successfully
docker ps | grep contextforge

# Verify database connection from application
docker exec contextforge-app python -c "from scripts.db_auth import test_connection; \
  assert test_connection('postgresql'), 'DB connection failed'"

# Check audit logs
tail -f logs/db_credential_access.audit.log

# Verify port binding (should fail from external IP)
nc -zv YOUR_EXTERNAL_IP 5432  # Should timeout

# Verify port binding (should succeed from localhost)
nc -zv 127.0.0.1 5432  # Should connect
```

---

## Security Validation

### Run Security Checklist

```bash
# 1. Verify no hardcoded credentials in environment
grep -r "contextforge.*password" . --exclude-dir=.git --exclude="*.md"

# 2. Verify .env files not committed
git ls-files | grep "^\.env$"  # Should return nothing

# 3. Verify localhost-only binding
docker ps --format '{{.Ports}}' | grep "0.0.0.0.*543[0-9]"  # Should return nothing

# 4. Verify production credentials different from dev
# (Manual check - compare Key Vault vs. .env.example)

# 5. Test SQL injection protection
# (Run integration tests with malicious input)
```

---

## Rollback Procedure

If issues arise after deployment:

```bash
# 1. Revert to previous Docker Compose configuration
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.backup.yml up -d

# 2. Revert database credentials (if needed)
az keyvault secret set-version \
  --vault-name contextforge-prod-vault \
  --name db-password \
  --version PREVIOUS_VERSION_ID

# 3. Restart application with old credentials
kubectl rollout restart deployment/contextforge-api

# 4. Verify rollback successful
python -c "from scripts.db_auth import test_connection; \
  assert test_connection('postgresql'), 'Rollback failed'"
```

---

## Maintenance

### Regular Security Tasks

| Task | Frequency | Owner | Process |
|------|-----------|-------|---------|
| Credential rotation | 90 days | DevOps | `rotate-db-credentials.sh` |
| Security review | 180 days | Security | Re-run security scan |
| Audit log review | Weekly | Security | Check for anomalies |
| Access control review | Monthly | DevOps | Verify least privilege |
| Dependency updates | Monthly | DevOps | Update PostgreSQL, libraries |

---

## Troubleshooting

### Issue: "Connection refused" to production database

**Cause**: Firewall rules or network configuration

**Resolution**:
```bash
# Check firewall allows connection
nmap -p 5432 172.25.14.122

# Check application server can reach database
telnet 172.25.14.122 5432

# Verify credentials correct
psql -h 172.25.14.122 -U contextforge_prod -d taskman_v2 -c "SELECT 1;"
```

---

### Issue: "Password authentication failed"

**Cause**: Credentials out of sync or incorrect environment variables

**Resolution**:
```bash
# Verify environment variables set
echo $PG_PASSWORD  # Should show password (or be empty if from Key Vault)

# Verify Key Vault secret correct
az keyvault secret show \
  --vault-name contextforge-prod-vault \
  --name db-password \
  --query value -o tsv

# Test direct connection with known-good credentials
psql -h 172.25.14.122 -U postgres -d taskman_v2  # Use superuser to verify server OK
```

---

### Issue: "Permission denied" for application

**Cause**: Managed identity not granted Key Vault access

**Resolution**:
```bash
# Grant application access to Key Vault
az keyvault set-policy \
  --name contextforge-prod-vault \
  --object-id $(az ad sp show --id YOUR_APP_ID --query objectId -o tsv) \
  --secret-permissions get list

# Verify application can read secret
az login --identity  # From application VM
az keyvault secret show \
  --vault-name contextforge-prod-vault \
  --name db-password
```

---

## References

- [Security Review Report](../SECURITY-REVIEW-DATABASE-ACCESS.md)
- [Azure Key Vault Documentation](https://docs.microsoft.com/en-us/azure/key-vault/)
- [Docker Secrets Documentation](https://docs.docker.com/engine/swarm/secrets/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)
- [OWASP Database Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Database_Security_Cheat_Sheet.html)

---

**Document Version**: 1.0
**Last Updated**: 2025-12-29
**Next Review**: Before production deployment
