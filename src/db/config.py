"""
NirmaanAI Database Configuration Module
Provides safe, environment-driven database configuration with credentials masking
and clean error reporting.
"""

import os
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load .env if present in project root
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")


class DatabaseConfigurationError(ValueError):
    """Raised when database configuration is missing, incomplete, or invalid."""
    pass


class DatabaseConfig:
    """Safe database configuration manager."""

    def __init__(
        self,
        database_url: Optional[str] = None,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 1800,
        echo: bool = False,
    ):
        raw_url = database_url or os.getenv("DATABASE_URL")
        if not raw_url or not raw_url.strip():
            raise DatabaseConfigurationError(
                "DATABASE_URL environment variable is not set. "
                "Configure DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>:<port>/<dbname> "
                "in your environment or .env file. See .env.example for guidance."
            )

        self._raw_url = raw_url.strip()
        self.database_url = self._normalize_driver(self._raw_url)
        self.pool_size = int(os.getenv("DB_POOL_SIZE", str(pool_size)))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", str(max_overflow)))
        self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT_SECONDS", str(pool_timeout)))
        self.pool_recycle = int(os.getenv("DB_POOL_RECYCLE_SECONDS", str(pool_recycle)))
        self.echo = os.getenv("DB_ECHO", "false").lower() in ("true", "1", "yes") or echo

    @staticmethod
    def _normalize_driver(url: str) -> str:
        """
        Ensures SQLAlchemy 2.x psycopg driver compatibility.
        Maps postgresql:// -> postgresql+psycopg:// if no specific driver is supplied.
        """
        if url.startswith("postgres://"):
            return "postgresql+psycopg://" + url[len("postgres://"):]
        if url.startswith("postgresql://") and not url.startswith("postgresql+"):
            return "postgresql+psycopg://" + url[len("postgresql://"):]
        return url

    @property
    def is_postgres(self) -> bool:
        """Returns True if configuring a PostgreSQL dialect."""
        return self.database_url.startswith("postgresql")

    @property
    def is_sqlite(self) -> bool:
        """Returns True if configuring an SQLite dialect (e.g., for testing)."""
        return self.database_url.startswith("sqlite")

    def get_masked_url(self) -> str:
        """
        Returns database URL with sensitive credentials masked.
        Never outputs raw passwords to logs or error messages.
        """
        try:
            parsed = urlparse(self.database_url)
            if parsed.password:
                netloc = f"{parsed.username}:******@{parsed.hostname}"
                if parsed.port:
                    netloc += f":{parsed.port}"
                return parsed._replace(netloc=netloc).geturl()
            return self.database_url
        except Exception:
            return "<masked-database-url>"

    def __repr__(self) -> str:
        return f"<DatabaseConfig url={self.get_masked_url()} pool_size={self.pool_size}>"


def get_default_config() -> DatabaseConfig:
    """Returns application default DatabaseConfig from environment."""
    return DatabaseConfig()


def is_postgres_available(database_url: Optional[str] = None, timeout_seconds: float = 1.5) -> bool:
    """
    Safely probes whether the configured PostgreSQL instance is reachable.
    Does not crash on network / connection failure.
    """
    try:
        cfg = DatabaseConfig(database_url=database_url)
        if not cfg.is_postgres:
            return False

        from sqlalchemy import create_engine, text
        engine = create_engine(
            cfg.database_url,
            connect_args={"connect_timeout": int(timeout_seconds)},
            pool_pre_ping=False,
        )
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return True
    except Exception:
        return False
