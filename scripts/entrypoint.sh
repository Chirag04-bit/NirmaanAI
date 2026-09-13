#!/bin/sh
# ==============================================================================
# NirmaanAI Container Entrypoint Script (Phase 24)
# Automates PostgreSQL readiness polling, Alembic migrations, initial seeding,
# and graceful Uvicorn ASGI server execution.
# ==============================================================================

set -e

# Default timeout in seconds
DB_TIMEOUT=${DB_TIMEOUT:-60}
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}

echo "================================================================================"
echo " NirmaanAI Factory Intelligence Platform - Container Initialization"
echo " Version: v0.24.0 | Environment: ${APP_ENV:-production}"
echo "================================================================================"

# If DATABASE_URL is provided, attempt to parse DB_HOST and DB_PORT from it
if [ -n "$DATABASE_URL" ]; then
    echo "[INFO] Parsing connection endpoint from DATABASE_URL..."
    # Extract host and port using Python to safely handle URLs without leaking credentials
    PARSED_INFO=$(python -c "
import os, urllib.parse
url = os.environ.get('DATABASE_URL', '')
if url.startswith('postgresql+psycopg://'):
    url = url.replace('postgresql+psycopg://', 'http://', 1)
elif url.startswith('postgresql://'):
    url = url.replace('postgresql://', 'http://', 1)
try:
    p = urllib.parse.urlparse(url)
    h = p.hostname or 'db'
    port = p.port or 5432
    print(f'{h} {port}')
except Exception:
    print('db 5432')
")
    DB_HOST=$(echo "$PARSED_INFO" | awk '{print $1}')
    DB_PORT=$(echo "$PARSED_INFO" | awk '{print $2}')
fi

echo "[INFO] Awaiting PostgreSQL readiness at ${DB_HOST}:${DB_PORT} (Timeout: ${DB_TIMEOUT}s)..."

START_TIME=$(date +%s)
READY=0

while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))

    if [ "$ELAPSED" -ge "$DB_TIMEOUT" ]; then
        echo "[FATAL] PostgreSQL service at ${DB_HOST}:${DB_PORT} did not become ready within ${DB_TIMEOUT}s timeout." >&2
        echo "[FATAL] Startup aborted. Check database container logs and network configuration." >&2
        exit 1
    fi

    # Test TCP socket connection to PostgreSQL port using Python
    if python -c "
import socket, sys
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2.0)
try:
    s.connect(('$DB_HOST', int('$DB_PORT')))
    s.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; then
        # Additional check: verify database is actually accepting queries
        if python -c "
import os, sys
from sqlalchemy import create_engine, text
db_url = os.environ.get('DATABASE_URL', '')
if not db_url:
    sys.exit(0)
try:
    eng = create_engine(db_url, connect_args={'connect_timeout': 3})
    with eng.connect() as conn:
        conn.execute(text('SELECT 1'))
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; then
            echo "[INFO] PostgreSQL is healthy and accepting SQL connections (${ELAPSED}s elapsed)."
            READY=1
            break
        fi
    fi

    echo "[INFO] Database not yet ready (${ELAPSED}s elapsed)... retrying in 2s"
    sleep 2
done

# ------------------------------------------------------------------------------
# 2. Database Migrations (Alembic)
# ------------------------------------------------------------------------------
if [ -n "$DATABASE_URL" ]; then
    echo "[INFO] Applying Alembic schema migrations ('alembic upgrade head')..."
    alembic upgrade head
    echo "[INFO] Database schema is up to date."

    # --------------------------------------------------------------------------
    # 3. Deterministic Initial Seeder
    # --------------------------------------------------------------------------
    echo "[INFO] Verifying initial factory data seeding..."
    python -c "
import os, sys
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from src.db.models.factory import Factory
from src.db.seed.seeder import DatabaseSeeder

db_url = os.environ.get('DATABASE_URL', '')
if db_url:
    eng = create_engine(db_url)
    with Session(eng) as session:
        existing = session.execute(select(Factory)).scalars().first()
        if existing is None:
            print('[INFO] Database empty. Running deterministic Phase 17 factory seeder...')
            seeder = DatabaseSeeder(session)
            counts = seeder.seed_all()
            session.commit()
            print(f'[INFO] Seed completed successfully: {counts}')
        else:
            print(f'[INFO] Database already contains plant entity: {existing.factory_id} ({existing.name}). Skipping seed.')
"
fi

echo "================================================================================"
echo " Starting NirmaanAI Application Server: $@"
echo "================================================================================"

exec "$@"
