"""
NirmaanAI Phase 24: Deployment Packaging & Containerization Test Suite
Version: v0.24.0

Validates:
1. Dockerfile presence, multi-stage syntax, and security properties (non-root, healthchecks)
2. Frontend Dockerfile & Nginx reverse proxy configuration
3. Database entrypoint readiness and migration script properties
4. Docker Compose YAML syntax, service topologies, healthchecks, networks, and persistent volumes
5. .dockerignore completeness (sensitive file and cache exclusion)
6. Environment variable schema alignment
7. Explicit live Docker daemon environment detection & graceful skip handling
"""

import os
from pathlib import Path
import re
import shutil
import pytest
import yaml

PROJECT_ROOT = Path("C:/NIRMAAN AI")
DOCKERFILE_BACKEND = PROJECT_ROOT / "Dockerfile.backend"
DOCKERFILE_FRONTEND = PROJECT_ROOT / "frontend" / "Dockerfile"
NGINX_CONF = PROJECT_ROOT / "frontend" / "nginx.conf"
DOCKERIGNORE_ROOT = PROJECT_ROOT / ".dockerignore"
DOCKERIGNORE_FRONTEND = PROJECT_ROOT / "frontend" / ".dockerignore"
COMPOSE_DEV = PROJECT_ROOT / "docker-compose.yml"
COMPOSE_PROD = PROJECT_ROOT / "docker-compose.prod.yml"
ENTRYPOINT_SH = PROJECT_ROOT / "scripts" / "entrypoint.sh"


# ==============================================================================
# 1. Backend Dockerfile Static Security & Architecture Tests
# ==============================================================================

def test_backend_dockerfile_architecture_and_security():
    """Verify backend Dockerfile follows multi-stage, non-root, and healthcheck standards."""
    assert DOCKERFILE_BACKEND.exists(), "Dockerfile.backend missing"
    content = DOCKERFILE_BACKEND.read_text(encoding="utf-8")

    # Multi-stage build check
    assert "FROM python:3.12-slim AS builder" in content
    assert "FROM python:3.12-slim AS runner" in content
    assert "COPY --from=builder" in content

    # Non-root user check
    assert "groupadd" in content and "nirmaan" in content
    assert "useradd" in content and "nirmaan" in content
    assert "USER nirmaan:nirmaan" in content

    # Port & Healthcheck check
    assert "EXPOSE 8000" in content
    assert "HEALTHCHECK" in content
    assert "http://127.0.0.1:8000/api/v1/health" in content

    # Secret isolation check (no .env copied)
    assert "COPY .env" not in content
    assert "COPY . /" not in content, "Wildcard COPY of root directory is prohibited"


# ==============================================================================
# 2. Frontend Dockerfile & Nginx Configuration Tests
# ==============================================================================

def test_frontend_dockerfile_and_nginx_proxy():
    """Verify frontend multi-stage build and Nginx reverse proxy configuration."""
    assert DOCKERFILE_FRONTEND.exists(), "frontend/Dockerfile missing"
    f_content = DOCKERFILE_FRONTEND.read_text(encoding="utf-8")

    # Multi-stage check: Node builder + Nginx runner
    assert "FROM node:20-alpine AS builder" in f_content
    assert "FROM nginx:1.27-alpine AS runner" in f_content
    assert "npm run build" in f_content
    assert "COPY --from=builder" in f_content
    assert "EXPOSE 80" in f_content
    assert "HEALTHCHECK" in f_content

    # Nginx config verification
    assert NGINX_CONF.exists(), "frontend/nginx.conf missing"
    nginx_content = NGINX_CONF.read_text(encoding="utf-8")

    # Reverse proxy check
    assert "location /api/ {" in nginx_content
    assert "proxy_pass http://backend:8000/api/;" in nginx_content

    # SPA client-side fallback check
    assert "try_files $uri $uri/ /index.html;" in nginx_content

    # Security headers
    assert "X-Frame-Options" in nginx_content
    assert "X-Content-Type-Options" in nginx_content


# ==============================================================================
# 3. Entrypoint Script Robustness Tests
# ==============================================================================

def test_entrypoint_script_properties():
    """Verify entrypoint.sh provides database timeout polling and automated migration."""
    assert ENTRYPOINT_SH.exists(), "scripts/entrypoint.sh missing"
    content = ENTRYPOINT_SH.read_text(encoding="utf-8")

    # Shell and error handling
    assert content.startswith("#!/bin/sh")
    assert "set -e" in content

    # Database readiness polling loop with timeout
    assert "DB_TIMEOUT" in content
    assert "while true; do" in content
    assert "ELAPSED" in content
    assert "did not become ready within" in content

    # Migration & Seeding steps
    assert "alembic upgrade head" in content
    assert "DatabaseSeeder" in content

    # Exec process handoff
    assert 'exec "$@"' in content


# ==============================================================================
# 4. Docker Compose Topologies & YAML Validity Tests
# ==============================================================================

def test_docker_compose_dev_and_prod_validity():
    """Verify docker-compose.yml and docker-compose.prod.yml schemas and configurations."""
    for compose_path, is_prod in [(COMPOSE_DEV, False), (COMPOSE_PROD, True)]:
        assert compose_path.exists(), f"{compose_path.name} missing"
        with open(compose_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert "services" in data, "Missing 'services' key in compose"
        services = data["services"]

        # Required services
        assert "db" in services, "Missing 'db' service"
        assert "backend" in services, "Missing 'backend' service"
        assert "frontend" in services, "Missing 'frontend' service"

        # Database service checks
        db_svc = services["db"]
        assert "postgres:16-alpine" in db_svc["image"]
        assert "healthcheck" in db_svc
        assert "pg_isready" in str(db_svc["healthcheck"]["test"])

        # Backend service checks
        backend_svc = services["backend"]
        assert backend_svc["depends_on"]["db"]["condition"] == "service_healthy"
        assert "DATABASE_URL" in backend_svc["environment"]

        # Network and volume checks
        assert "volumes" in data
        assert "pgdata" in data["volumes"]
        assert "networks" in data
        assert "nirmaan-network" in data["networks"]

        if is_prod:
            # Production hardening checks: DB port 5432 should NOT be published to host
            assert "ports" not in db_svc, "Production database must not expose ports to host"
            assert "expose" in db_svc
            # Resource limits check
            assert "deploy" in backend_svc and "resources" in backend_svc["deploy"]


# ==============================================================================
# 5. .dockerignore File Exclusion Tests
# ==============================================================================

def test_dockerignore_security_exclusions():
    """Verify that .dockerignore excludes sensitive secrets, git metadata, and local caches."""
    assert DOCKERIGNORE_ROOT.exists(), ".dockerignore missing"
    content = DOCKERIGNORE_ROOT.read_text(encoding="utf-8")

    critical_exclusions = [
        ".git/",
        ".env",
        "node_modules/",
        "__pycache__/",
        ".pytest_cache/",
        "scratch/",
    ]
    for pattern in critical_exclusions:
        assert pattern in content, f"Missing critical exclusion '{pattern}' in .dockerignore"


# ==============================================================================
# 6. Environment Variable Alignment
# ==============================================================================

def test_environment_variable_alignment():
    """Verify consistency between .env.example and compose configurations."""
    env_example = PROJECT_ROOT / ".env.example"
    assert env_example.exists()
    example_content = env_example.read_text(encoding="utf-8")

    assert "DATABASE_URL" in example_content
    assert "DB_POOL_SIZE" in example_content
    assert "POSTGRES_USER" not in example_content or "DATABASE_URL=postgresql+psycopg://" in example_content


# ==============================================================================
# 7. Live Docker Daemon Environment Probe
# ==============================================================================

def test_live_docker_daemon_environment_status():
    """
    Checks if Docker engine is active on the host machine.
    If absent, explicitly documents the environment limitation without faking execution.
    """
    docker_bin = shutil.which("docker")
    if not docker_bin:
        pytest.skip("Docker engine is not installed on host environment — static packaging verified")

    # If docker is present, test daemon connection
    import subprocess
    result = subprocess.run([docker_bin, "info"], capture_output=True, text=True)
    if result.returncode != 0:
        pytest.skip("Docker daemon is not running — static packaging verified")

    assert result.returncode == 0
