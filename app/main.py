"""
NirmaanAI Factory Intelligence API (Phase 18)
Production-grade FastAPI application serving factory topology, operational telemetry,
and Phase 0–17 intelligence subsystems.
"""

from contextlib import asynccontextmanager
import logging
from typing import Dict
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routes.health import router as root_health_router
from src.api.router import api_v1_router
from src.db.config import DatabaseConfigurationError

logger = logging.getLogger("nirmaanai.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and graceful shutdown."""
    logger.info("Initializing NirmaanAI Factory Intelligence API v0.18.0...")
    yield
    logger.info("Shutting down NirmaanAI Factory Intelligence API...")


def create_app() -> FastAPI:
    """Factory creating configured FastAPI application instance."""
    app = FastAPI(
        title="NirmaanAI Factory Intelligence API",
        version="0.18.0",
        description="Production API service layer for NirmaanAI manufacturing intelligence, predictive maintenance, and operational decision support.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # 1. CORS Middleware (Configured for local development & Phase 21 React/Vite dashboard)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # 2. Exception Handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed.",
                    "details": exc.errors(),
                }
            },
        )

    @app.exception_handler(DatabaseConfigurationError)
    async def database_config_exception_handler(request: Request, exc: DatabaseConfigurationError):
        logger.error(f"Database configuration failure: {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": {
                    "code": "DATABASE_UNAVAILABLE",
                    "message": "Database service is not configured or unavailable.",
                    "details": None,
                }
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": exc.detail,
                    "details": None,
                }
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected internal error occurred.",
                    "details": None,
                }
            },
        )

    # 3. Mount Routers
    app.include_router(root_health_router)
    app.include_router(api_v1_router)

    # 4. Root API Index
    @app.get("/", summary="API Root", tags=["System & Health"])
    def root_index() -> Dict[str, str]:
        return {
            "name": "NirmaanAI Factory Intelligence API",
            "version": "0.18.0",
            "docs": "/docs",
            "openapi": "/openapi.json",
            "health": "/health",
            "api_v1": "/api/v1",
        }

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
