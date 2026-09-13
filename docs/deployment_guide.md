# NirmaanAI Production Deployment Guide
**Document Version**: `v0.24.0`  
**Target Platform**: Linux (Ubuntu 22.04 LTS / Debian 12 / RHEL 9), Docker Engine 24+, Docker Compose v2+  
**Architecture**: Multi-Container Microservices Topology  

---

## 1. System Architecture Overview

NirmaanAI is packaged as a three-tier, production-hardened containerized system:

```mermaid
graph TD
    subgraph Client_Network ["External / Ingress Network"]
        USER[Factory Operator / Plant Manager]
    end

    subgraph Host_Ingress ["Host Ports"]
        HTTP[Port 80: HTTP]
        HTTPS[Port 443: HTTPS / TLS]
        API_PORT[Port 8000: Direct API (Optional)]
    end

    subgraph Docker_Bridge ["Docker Network: nirmaan-network"]
        subgraph Frontend ["frontend Service (nginx:1.27-alpine)"]
            NGINX[Nginx Reverse Proxy & Static Server]
            SPA[Pre-compiled React 19 / Vite Distribution]
            NGINX --- SPA
        end

        subgraph Backend ["backend Service (python:3.12-slim)"]
            ENTRY[entrypoint.sh: DB Readiness & Alembic Migrations]
            UVICORN[Uvicorn ASGI Server - 4 Workers]
            FASTAPI[FastAPI Service & Intelligence Engines]
            ENTRY --> UVICORN
            UVICORN --> FASTAPI
        end

        subgraph Database ["db Service (postgres:16-alpine)"]
            PG[(PostgreSQL 16 Engine)]
            DATA[(Named Volume: pgdata)]
            PG --- DATA
        end

        NGINX -- "Proxy: /api/ -> backend:8000" --> UVICORN
        FASTAPI -- "Port 5432 (Internal)" --> PG
    end

    USER --> HTTP
    USER --> HTTPS
    HTTP --> NGINX
    HTTPS --> NGINX
```

---

## 2. Hardware & Host Prerequisites

| Component | Minimum Specification (Evaluation / Lab) | Recommended Specification (Production Factory) |
| :--- | :--- | :--- |
| **CPU Architecture** | x86_64 / amd64 (2 Cores) | x86_64 / amd64 (4+ Cores) |
| **System Memory (RAM)**| 4 GB | 8 GB – 16 GB |
| **Persistent Storage** | 20 GB SSD | 100 GB+ High-IOPS NVMe |
| **Operating System** | Ubuntu 22.04 LTS, Debian 12 | Enterprise Linux (RHEL 9, Rocky Linux 9, Ubuntu LTS) |
| **Container Engine** | Docker Engine 24.0+ | Docker Engine 26.0+ with Docker Compose v2.24+ |

---

## 3. Environment Variables Configuration

Copy the template file `.env.example` to create your active `.env`:

```bash
cp .env.example .env
chmod 600 .env
```

### Key Configuration Parameters
```ini
# Application Mode
APP_ENV=production
LOG_LEVEL=INFO

# PostgreSQL Configuration
POSTGRES_USER=nirmaan_admin
POSTGRES_PASSWORD=your_ultra_secure_password_here
POSTGRES_DB=nirmaanai

# Backend Database Connection String
DATABASE_URL=postgresql+psycopg://nirmaan_admin:your_ultra_secure_password_here@db:5432/nirmaanai

# Connection Pool Limits
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT_SECONDS=30
DB_POOL_RECYCLE_SECONDS=1800
```

> [!CAUTION]
> Never commit `.env` containing production passwords or API tokens to source control. Ensure permissions are restricted (`chmod 600 .env`).

---

## 4. Single-Command Deployment

### A. Local Development / Testing
```bash
# Build and start all three services in background
docker compose up -d --build

# Inspect container status
docker compose ps

# Tail logs across all services
docker compose logs -f
```

### B. Production Deployment
```bash
# Deploy with resource constraints and isolated database
docker compose -f docker-compose.prod.yml up -d --build

# Verify healthy status
docker compose -f docker-compose.prod.yml ps
```

---

## 5. Automated Database Initialization & Migrations

The `scripts/entrypoint.sh` entrypoint script handles database lifecycle automatically:
1. **Readiness Polling**: Polls `db:5432` with a 60-second timeout until PostgreSQL accepts TCP connections and executes queries.
2. **Schema Migration**: Executes `alembic upgrade head`, creating all required tables, foreign keys, and indexes.
3. **Deterministic Seeder**: Checks if the `factories` table is populated. If empty, runs `DatabaseSeeder.seed_all()` to import reference machine topology, sensor baselines, inventory items, and AI model outputs.

### Manual Migration Commands (Optional)
```bash
# Apply migrations manually
docker compose exec backend alembic upgrade head

# Roll back 1 migration revision
docker compose exec backend alembic downgrade -1

# Check current revision
docker compose exec backend alembic current
```

---

## 6. Service Healthchecks

All three containers include built-in Docker healthcheck probes:

| Service | Healthcheck Command | Interval | Timeout | Retries |
| :--- | :--- | :---: | :---: | :---: |
| **db** | `pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}` | 10s | 5s | 5 |
| **backend** | `curl -f http://127.0.0.1:8000/api/v1/health` | 20s | 5s | 3 |
| **frontend** | `wget -q -O - http://127.0.0.1/healthz` | 15s | 3s | 3 |

Inspect health status via:
```bash
docker inspect --format='{{json .State.Health}}' nirmaanai-backend-prod | jq
```

---

## 7. Nginx Routing & API Access

The frontend container runs Nginx on port `80`:
- **Static Dashboard**: `GET /` serves the pre-compiled React 19 bundle with client-side SPA fallback (`try_files $uri $uri/ /index.html`).
- **Backend API**: All requests to `/api/*` are reverse-proxied to `http://backend:8000/api/*` with `X-Forwarded-For` and `Host` headers preserved.
- **OpenAPI Documentation**: `GET /docs` and `GET /openapi.json` are reverse-proxied directly to FastAPI.

---

## 8. Backup & Persistence Operations

PostgreSQL data is stored in the Docker named volume `nirmaanai-pgdata-prod` (`/var/lib/postgresql/data`).

### Automated Backup
```bash
# Create timestamped SQL dump
docker compose exec db pg_dump -U nirmaan_admin nirmaanai | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Database Restore
```bash
# Restore from backup
gunzip < backup_20260913_120000.sql.gz | docker compose exec -T db psql -U nirmaan_admin -d nirmaanai
```

---

## 9. Security Hardening Checklist

- [x] **Non-Root Execution**: Backend runs as unprivileged user `nirmaan:nirmaan` (UID 10001).
- [x] **Database Isolation**: In production (`docker-compose.prod.yml`), database port 5432 is strictly private to the Docker bridge network.
- [x] **No Baked Secrets**: Zero credentials or `.env` files are copied into container images.
- [x] **Multi-Stage Builds**: Development compilers (`gcc`, `build-essential`) and Node.js runtimes are discarded from final minimal images.
- [x] **HTTP Security Headers**: Nginx enforces `X-Frame-Options: SAMEORIGIN` and `X-Content-Type-Options: nosniff`.
- [x] **Resource Caps**: CPU and memory reservation and limitation ceilings configured on all production containers.
