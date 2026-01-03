# Dual-Database Architecture for TaskMan-v2

This service implements a robust **Dual-Database Architecture** to ensure high availability and developer productivity across different environments.

## 🏗️ Architecture Overview

The system maintains two potential database connections:

1.  **Primary (PostgreSQL)**: The production-grade relational database running in Docker/WSL.
2.  **Fallback (SQLite)**: A local, file-based database for offline development or when Postgres is unavailable.

### The Connection Manager
Located in `db/connection_manager.py`, the `ConnectionManager` orchestrates these connections:
- **Automatic Failover**: If the Primary is unreachable during a session request, it seamlessly switches to the Fallback.
- **Health Checks**: `/health` endpoint probes *both* databases and reports which one is active.
- **Circuit Breaker**: (Planned) Prevents thrashing by maintaining fallback state for a cooldown period.

## 🚀 Setup & Dependencies

To support this architecture, the `aiosqlite` driver is required for async SQLite access.

### Installation
Using `uv` (Recommended):
```bash
uv add aiosqlite
```

Using standard `pip`:
```bash
pip install aiosqlite
```

## ⚙️ Configuration

Configuration is managed via `.env` and `src/taskman_api/config.py`.

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_DATABASE__HOST` | Postgres Host | `localhost` |
| `APP_DATABASE__SQLITE_PATH` | Path to fallback DB | `taskman.db` |

## 🔍 How it Works

### 1. Initialization
On startup (`init_db`), the system attempts to create tables in **both** databases. This ensures the fallback is ready to go immediately if needed.

### 2. Session Request
When an API endpoint requests `get_async_session`:
1.  Manager checks current mode (Primary vs Fallback).
2.  Attempts to yield a session from the active engine.
3.  **Resilience**: If Primary fails, it catches the exception, switches mode to Fallback, and yields a fresh session from SQLite—all within the same request.

### 3. Health Check
The `/health` endpoint returns a detailed status:
```json
{
  "status": "degraded", // "degraded" if running on fallback
  "database": {
    "mode": "fallback",
    "connected": true,
    "primary": { "connected": false, "error": "..." },
    "fallback": { "connected": true, "latency_ms": 0.5 }
  }
}
```
