# 🐳 Dynamic Task Manager Docker Deployment Guide

## 📋 Overview

This guide provides comprehensive instructions for deploying the Dynamic Task Manager using Docker containers. The DTM supports both development and production deployment modes with full ContextForge integration.

## 🏗️ Architecture

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  FastAPI Backend│    │  ContextForge   │
│   (nginx/Vite)  │◄──►│  (Python 3.11+)│◄──►│  Integration    │
│   Port: 3000/5173│   │   Port: 8000    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                    ┌─────────────────┐
                    │      Redis      │
                    │   (Optional)    │
                    │   Port: 6379    │
                    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker Engine 20.10+ and Docker Compose 2.0+
- 4GB+ available RAM
- 2GB+ available disk space

### Production Deployment

```powershell
# Windows PowerShell
.\docker\scripts\Deploy-Production.ps1

# Or using Docker Compose directly
docker-compose up -d
```

```bash
# Linux/macOS
./docker/scripts/deploy-production.sh

# Or using Docker Compose directly
docker-compose up -d
```

**Access Points:**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Development Deployment

```powershell
# Windows PowerShell
.\docker\scripts\Deploy-Development.ps1 -OpenBrowser

# Or using Docker Compose directly
docker-compose -f docker-compose.dev.yml up -d
```

```bash
# Linux/macOS
./docker/scripts/deploy-development.sh

# Or using Docker Compose directly
docker-compose -f docker-compose.dev.yml up -d
```

**Access Points:**
- Frontend: http://localhost:5173 (Vite dev server)
- API: http://localhost:8000 (Hot reload enabled)
- SQLite Admin: http://localhost:8080
- API Docs: http://localhost:8000/docs

## 📦 Container Details

### Frontend Container (React + nginx)

**Production:**
- Base: `nginx:alpine`
- Multi-stage build with Node.js 18
- Optimized static assets with gzip compression
- Security headers and CORS handling
- Health checks and graceful shutdown

**Development:**
- Base: `node:18-alpine`
- Vite dev server with hot module replacement
- Volume mounts for live code updates
- Source map support for debugging

### Backend Container (FastAPI + ContextForge)

**Production:**
- Base: `python:3.11-slim`
- Multi-worker Uvicorn server (4 workers)
- Non-root user security
- Health checks and structured logging
- ContextForge integration layer

**Development:**
- Base: `python:3.11-slim`
- Single worker with auto-reload
- Debug tools and testing frameworks
- Volume mounts for live code updates
- Extended timeout for debugging

### Redis Container (Optional)

- Session storage and caching
- Persistent data volume
- Health monitoring
- Production-ready configuration

## 🔧 Configuration

### Environment Variables

#### Frontend
```env
NODE_ENV=production|development
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

#### Backend
```env
ENVIRONMENT=production|development
DATABASE_URL=sqlite:///./db/trackers.sqlite
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
LOG_LEVEL=INFO|DEBUG
UNIFIED_LOG_LEVEL=INFO|DEBUG
WORKERS=4
```

### Volume Mounts

**Production:**
```yaml
volumes:
  - ./db:/app/db                    # SQLite database
  - ./logs:/app/logs                # Application logs
  - ./.copilot-tracking:/app/.copilot-tracking:ro  # ContextForge config
```

**Development:**
```yaml
volumes:
  # Additional development mounts
  - ./python:/app/python            # Backend source
  - ./src:/app/src                  # Core source
  - ./dynamic-task-manager/src:/app/src  # Frontend source
```

## 🔍 Monitoring and Debugging

### Health Checks

All containers include comprehensive health checks:

```bash
# Check service health
docker-compose ps

# View health check logs
docker inspect dtm-backend --format='{{json .State.Health}}'
```

### Logging

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f backend

# View last N lines
docker-compose logs --tail=100 frontend
```

### Container Access

```bash
# Access backend container
docker-compose exec backend /bin/bash

# Access frontend container (development)
docker-compose -f docker-compose.dev.yml exec frontend-dev /bin/sh

# Run commands in container
docker-compose exec backend python -c "import sys; print(sys.version)"
```

## 🛠️ Development Workflow

### Hot Reload

**Frontend:**
- Vite dev server auto-reloads on file changes
- Source maps enabled for debugging
- HMR (Hot Module Replacement) active

**Backend:**
- FastAPI auto-reloads on Python file changes
- Debug mode enabled with extended timeouts
- Structured logging for development

### Testing in Containers

```bash
# Run backend tests
docker-compose -f docker-compose.dev.yml exec backend-dev python -m pytest

# Run frontend tests
docker-compose -f docker-compose.dev.yml exec frontend-dev npm test

# Run integration tests
docker-compose -f docker-compose.dev.yml exec backend-dev python -m pytest tests/integration/
```

## 🔒 Security Considerations

### Production Security

1. **Non-root containers:** All containers run as non-root users
2. **Minimal base images:** Using slim/alpine images
3. **Security headers:** nginx configured with security headers
4. **Resource limits:** Memory and CPU constraints defined
5. **Health monitoring:** Comprehensive health checks

### Network Security

```yaml
networks:
  dtm-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## 📈 Performance Optimization

### Production Optimizations

1. **Multi-stage builds** reduce final image size
2. **Multi-worker FastAPI** handles concurrent requests
3. **Nginx caching** for static assets
4. **Gzip compression** reduces transfer size
5. **Health-based load balancing** ready

### Resource Allocation

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '1.0'
      memory: 1G
```

## 🚧 Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check logs
docker-compose logs backend

# Check Docker daemon
docker system info

# Rebuild containers
docker-compose build --no-cache
```

**Port conflicts:**
```bash
# Check port usage
netstat -tlnp | grep :8000

# Use different ports
docker-compose up -d --scale backend=0
```

**Volume permissions:**
```bash
# Fix permissions
sudo chown -R $USER:$USER ./db ./logs

# Or use Docker user matching
docker-compose exec backend chown -R appuser:appuser /app/db
```

### Performance Issues

**High memory usage:**
- Reduce worker count in production
- Enable memory monitoring
- Check for memory leaks in logs

**Slow startup:**
- Use multi-stage build caching
- Optimize dependency installation
- Pre-warm containers

## 🔄 Deployment Automation

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Deploy to Production
  run: |
    docker-compose -f docker-compose.yml build
    docker-compose -f docker-compose.yml up -d
    docker-compose -f docker-compose.yml exec -T backend python -c "import requests; requests.get('http://localhost:8000/health')"
```

### Backup and Recovery

```bash
# Backup database
docker-compose exec backend cp /app/db/trackers.sqlite /app/db/trackers.sqlite.bak

# Backup volumes
docker run --rm -v dtm_db_data:/data -v $(pwd):/backup alpine tar czf /backup/dtm-backup.tar.gz /data
```

## 📚 Additional Resources

- [Docker Compose Reference](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [nginx Configuration](https://nginx.org/en/docs/)
- [ContextForge Integration Guide](../docs/contextforge-integration.md)

## 🆘 Support

For deployment issues:
1. Check logs: `docker-compose logs -f`
2. Verify health: `docker-compose ps`
3. Review configuration files
4. Consult troubleshooting section above

---

**Version:** 1.0.0
**Last Updated:** $(Get-Date -Format 'yyyy-MM-dd')
**Compatibility:** Docker 20.10+, Docker Compose 2.0+
