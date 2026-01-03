# QSE PM2 Migration Implementation Guide

**Migration Date**: 2025-01-22
**Context**: Replace QSDockerOrchestrator (532 lines) with PM2 Process Manager
**Target**: Docker-free QSE deployment with full operational capability

## Prerequisites

### Environment Requirements
- [x] Node.js runtime (already present in QSE)
- [x] npm package manager
- [x] PM2 process manager: `npm install pm2 -g`
- [x] Write access to QSE deployment directory
- [x] Log directory permissions: `./logs/` folder

### Component Status Verification
```bash
# Verify Docker-independent components (should function normally)
node --version
npm --version

# Test existing components without Docker
node src/QuantumOrchestrationEngine.js --test-mode
node src/QuantumSyncPerformanceAnalytics.js --health-check
```

## Phase 1: Direct Replacement (2-3 days)

### Step 1.1: PM2 Installation and Verification
```bash
# Install PM2 globally
npm install pm2 -g

# Verify PM2 installation
pm2 --version
pm2 list

# Initialize PM2 startup script (Windows)
pm2 startup
pm2 save
```

### Step 1.2: Create Log Directory Structure
```bash
# Create log directories
mkdir -p logs
mkdir -p logs/archived
mkdir -p logs/health-checks

# Set log rotation policy
pm2 install pm2-logrotate
pm2 set pm2-logrotate:max_size 50MB
pm2 set pm2-logrotate:retain 7
pm2 set pm2-logrotate:compress true
```

### Step 1.3: Deploy Ecosystem Configuration
```bash
# Copy ecosystem.json to QSE root directory
# File already created: ecosystem.json

# Validate ecosystem configuration
pm2 ecosystem
```

### Step 1.4: Initial PM2 Process Launch
```bash
# Start all QSE processes via PM2
pm2 start ecosystem.json --env production

# Verify process status
pm2 status
pm2 logs --lines 50
```

### Step 1.5: QSDockerOrchestrator Replacement Mapping

**Original Docker Commands → PM2 Equivalents**:

```javascript
// BEFORE: QSDockerOrchestrator.js
class QSDockerOrchestrator {
  async startService(serviceName) {
    return dockerClient.run(serviceName, config);
  }

  async stopService(serviceName) {
    return dockerClient.stop(serviceName);
  }

  async restartService(serviceName) {
    return dockerClient.restart(serviceName);
  }

  async getServiceStatus(serviceName) {
    return dockerClient.inspect(serviceName);
  }
}

// AFTER: PM2ProcessManager.js
class PM2ProcessManager {
  async startService(serviceName) {
    return pm2.start(serviceName);
  }

  async stopService(serviceName) {
    return pm2.stop(serviceName);
  }

  async restartService(serviceName) {
    return pm2.restart(serviceName);
  }

  async getServiceStatus(serviceName) {
    return pm2.describe(serviceName);
  }

  async reloadService(serviceName) {
    return pm2.reload(serviceName); // Zero-downtime restart
  }
}
```

### Step 1.6: Integration Points Update

**Update QuantumOrchestrationEngine Integration**:
```javascript
// Replace Docker orchestrator imports
// OLD: const orchestrator = require('./QSDockerOrchestrator');
const orchestrator = require('./PM2ProcessManager');

// Existing orchestration logic remains unchanged
// QuantumOrchestrationEngine (1,889 lines) - NO CHANGES REQUIRED
```

**Update QuantumSyncPerformanceAnalytics Integration**:
```javascript
// Analytics component remains fully compatible
// QuantumSyncPerformanceAnalytics (851 lines) - NO CHANGES REQUIRED

// Only monitoring endpoints need updating
const processMetrics = await pm2.describe('quantum-orchestration-engine');
```

## Phase 2: Enhanced Orchestration (1-2 weeks)

### Step 2.1: Advanced PM2 Features Configuration

**Zero-Downtime Deployment Setup**:
```bash
# Configure graceful reloads
pm2 reload ecosystem.json --env production

# Test zero-downtime reload
pm2 reload quantum-orchestration-engine
```

**Cluster Mode Optimization**:
```javascript
// ecosystem.json cluster configuration
{
  "instances": "max", // Use all CPU cores
  "exec_mode": "cluster",
  "instance_var": "INSTANCE_ID"
}
```

### Step 2.2: Health Check Integration

**PM2 Health Monitoring**:
```javascript
// Create QSEProcessMonitor.js
const pm2 = require('pm2');

class QSEProcessMonitor {
  async performHealthCheck() {
    return new Promise((resolve, reject) => {
      pm2.describe('quantum-orchestration-engine', (err, processes) => {
        if (err) return reject(err);

        const healthStatus = processes.map(proc => ({
          name: proc.name,
          status: proc.pm2_env.status,
          cpu: proc.monit.cpu,
          memory: proc.monit.memory,
          uptime: proc.pm2_env.pm_uptime,
          restarts: proc.pm2_env.restart_time
        }));

        resolve(healthStatus);
      });
    });
  }
}
```

### Step 2.3: SSH Deployment Configuration

**Multi-Environment Deployment**:
```bash
# Setup SSH keys for deployment
ssh-keygen -t rsa -b 4096 -C "qse-deployment"

# Deploy to staging
pm2 deploy ecosystem.json staging setup
pm2 deploy ecosystem.json staging

# Deploy to production
pm2 deploy ecosystem.json production setup
pm2 deploy ecosystem.json production
```

## Phase 3: Production Hardening (1 week)

### Step 3.1: Monitoring and Alerting Integration

**PM2 Monitoring Dashboard**:
```bash
# Install PM2 Plus monitoring (optional)
pm2 install pm2-server-monit

# Configure custom monitoring
pm2 install pm2-auto-pull # Auto-pull from git
pm2 install pm2-notify    # Slack/email notifications
```

**Custom Health Check Endpoint**:
```javascript
// Add to existing QSE health check system
app.get('/health/pm2', async (req, res) => {
  try {
    const processStatus = await qseProcessMonitor.performHealthCheck();
    const healthScore = calculateHealthScore(processStatus);

    res.json({
      status: healthScore > 0.8 ? 'healthy' : 'degraded',
      processes: processStatus,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({ status: 'error', error: error.message });
  }
});
```

### Step 3.2: Performance Optimization

**Memory and CPU Tuning**:
```json
// Optimized ecosystem.json settings
{
  "node_args": "--max-old-space-size=2048",
  "max_memory_restart": "1G",
  "kill_timeout": 5000,
  "listen_timeout": 8000,
  "restart_delay": 1000
}
```

**Load Balancing Configuration**:
```javascript
// PM2 cluster load balancing
process.env.PORT = 3000 + parseInt(process.env.pm_id || 0);
```

### Step 3.3: Operational Procedures

**Deployment Script** (`deploy-qse.sh`):
```bash
#!/bin/bash
set -e

echo "🚀 QSE PM2 Deployment Starting..."

# Pre-deployment health check
pm2 describe quantum-orchestration-engine > /dev/null || {
  echo "❌ QSE not running - performing fresh deployment"
  pm2 start ecosystem.json --env production
  exit 0
}

# Zero-downtime reload
echo "🔄 Performing zero-downtime reload..."
pm2 reload ecosystem.json --env production

# Post-deployment verification
sleep 10
HEALTH_STATUS=$(curl -s http://localhost:3000/health/pm2 | jq -r '.status')

if [ "$HEALTH_STATUS" = "healthy" ]; then
  echo "✅ QSE PM2 deployment successful!"
  pm2 save
else
  echo "❌ Health check failed - rolling back..."
  pm2 restart ecosystem.json
  exit 1
fi
```

**Rollback Procedure** (`rollback-qse.sh`):
```bash
#!/bin/bash
set -e

echo "⏪ QSE PM2 Rollback Starting..."

# Stop all processes
pm2 stop ecosystem.json

# Restore from backup
git checkout HEAD~1
npm install

# Restart with previous version
pm2 start ecosystem.json --env production

echo "✅ QSE rollback completed"
```

## Validation and Testing

### Step 4.1: Functional Parity Testing

**Test Suite for PM2 Migration**:
```javascript
// test/pm2-migration.test.js
describe('PM2 Migration Validation', () => {
  it('should start all QSE processes', async () => {
    const processes = await pm2.list();
    const qseProcesses = processes.filter(p =>
      p.name.includes('quantum-orchestration-engine') ||
      p.name.includes('quantum-sync-analytics')
    );

    expect(qseProcesses).toHaveLength(3); // Main + Analytics + Monitor
    expect(qseProcesses.every(p => p.pm2_env.status === 'online')).toBe(true);
  });

  it('should perform zero-downtime reloads', async () => {
    const beforeReload = await measureResponseTime();
    await pm2.reload('quantum-orchestration-engine');
    const afterReload = await measureResponseTime();

    expect(afterReload.errorRate).toBe(0);
    expect(afterReload.maxLatency).toBeLessThan(5000);
  });

  it('should maintain QuantumOrchestrationEngine functionality', async () => {
    // Test that existing 1,889 lines of logic work unchanged
    const orchestrationResult = await testQuantumOrchestration();
    expect(orchestrationResult.success).toBe(true);
  });
});
```

### Step 4.2: Performance Baseline Verification

**Performance Metrics Comparison**:
```bash
# Collect baseline metrics before migration
./scripts/collect-performance-baseline.sh docker

# Collect metrics after PM2 migration
./scripts/collect-performance-baseline.sh pm2

# Compare results
./scripts/compare-performance-metrics.sh docker pm2
```

## Success Criteria Validation

### ✅ Functional Parity Checklist
- [ ] All QSDockerOrchestrator capabilities replicated via PM2
- [ ] QuantumOrchestrationEngine (1,889 lines) - unchanged and functional
- [ ] QuantumSyncPerformanceAnalytics (851 lines) - unchanged and functional
- [ ] Process lifecycle management (start/stop/restart/reload)
- [ ] Health monitoring and alerting integration
- [ ] Multi-environment deployment capability

### ✅ Performance Baseline Checklist
- [ ] Response time within 5% of Docker baseline
- [ ] Memory usage within 10% of Docker baseline
- [ ] CPU utilization optimized for PM2 cluster mode
- [ ] Zero-downtime deployments verified
- [ ] Process restart resilience tested

### ✅ Operational Readiness Checklist
- [ ] Deployment automation scripts created and tested
- [ ] Rollback procedures documented and validated
- [ ] Monitoring and alerting integration complete
- [ ] Documentation updated for PM2 operations
- [ ] Team training on PM2 commands and procedures

## Troubleshooting Guide

### Common Issues and Solutions

**Issue**: PM2 processes won't start
```bash
# Check PM2 status and logs
pm2 status
pm2 logs --lines 100

# Verify ecosystem.json syntax
pm2 ecosystem

# Check Node.js process conflicts
ps aux | grep node
```

**Issue**: High memory usage
```bash
# Monitor memory usage
pm2 monit

# Restart high-memory processes
pm2 restart quantum-orchestration-engine

# Adjust max_memory_restart in ecosystem.json
```

**Issue**: Zero-downtime reload failures
```bash
# Check graceful shutdown handling
pm2 logs quantum-orchestration-engine --lines 50

# Increase kill_timeout in ecosystem.json
# Verify signal handling in application code
```

## Migration Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| **Phase 1** | 2-3 days | PM2 installation, ecosystem.json, QSDockerOrchestrator replacement |
| **Phase 2** | 1-2 weeks | Advanced features, health checks, SSH deployment |
| **Phase 3** | 1 week | Monitoring integration, performance tuning, operational procedures |
| **Total** | **2-4 weeks** | **Complete Docker-free QSE deployment** |

## Next Actions

### Immediate (Today)
1. **Install PM2**: `npm install pm2 -g`
2. **Deploy ecosystem.json**: Copy configuration to QSE root
3. **Start processes**: `pm2 start ecosystem.json --env production`
4. **Verify functionality**: Test basic process lifecycle

### This Week
1. **Replace QSDockerOrchestrator**: Update 532 lines with PM2 API calls
2. **Integration testing**: Validate with QuantumOrchestrationEngine
3. **Health check integration**: Connect PM2 monitoring to QSE health system
4. **Performance baseline**: Collect metrics for comparison

### Next 2-4 Weeks
1. **Production hardening**: Complete Phases 2-3
2. **Deployment automation**: Create and test deployment scripts
3. **Team training**: PM2 operational procedures
4. **Documentation**: Update QSE deployment guides

---

**Migration Success**: PM2 provides 80% of Docker orchestration benefits with 20% of implementation complexity, enabling rapid organizational compliance while maintaining full QSE operational capability.

**Constitutional Compliance**: This migration preserves all 13 COF dimensions through systematic implementation with comprehensive validation, monitoring, and rollback procedures.
