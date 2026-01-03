# TaskMan-v2 Port Configuration Reference

This document serves as the single source of truth for network port configurations within the TaskMan-v2 ecosystem.

## Core Services

| Service | Port | Source Config | Description |
| :--- | :--- | :--- | :--- |
| **Backend API** | **3001** | `backend-api/.env` | Main FastAPI application server. |
| **PostgreSQL** | **5434** | `docker-compose.taskman-v2.yml` | Primary database (mapped from container 5432). |
| **Frontend (Vite)** | **5176** | `vite.config.ts` | React application development server. |
| **Mock API** | **3002** | `src/mocks/server.js` | Standalone mock backend for frontend testing. |
| **PostgreSQL (Container)**| **5432** | Internal | Internal port within the Docker container. |

## Configuration Files

### Backend (`backend-api/.env`)
```env
API_PORT=3001
DATABASE_URL=postgresql://contextforge:contextforge@localhost:5434/taskman_v2
```

### Frontend (`vite.config.ts`)
```typescript
server: {
    port: 5176,
    proxy: {
        '/api': {
            target: 'http://localhost:3001',
            changeOrigin: true,
        },
    },
}
```

### Orval (`orval.config.ts`)
```typescript
target: 'http://localhost:3001/openapi.json',
```

## Troubleshooting
- **500 Errors on Backend**: usually indicate the Backend (3001) cannot talk to Postgres (5434). Check Docker.
- **CORS Errors**: Ensure Vite proxy is being used (request `/api/...`) or Backend allow_origins matches Frontend port (5176).
