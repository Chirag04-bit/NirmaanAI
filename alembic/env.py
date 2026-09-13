import os
from logging.config import fileConfig
from pathlib import Path
from sqlalchemy import create_engine, engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Load environment
root_dir = Path(__file__).resolve().parent.parent
load_dotenv(root_dir / ".env")

from src.db.base import Base
import src.db.models  # Ensures all models are registered on Base.metadata
from src.db.config import DatabaseConfig

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_database_url() -> str:
    """Retrieves normalized database URL from environment or configuration."""
    env_url = os.getenv("DATABASE_URL")
    if env_url and env_url.strip():
        return DatabaseConfig._normalize_driver(env_url.strip())
    # Fallback to valid configured url or sqlite file for schema management
    cfg_url = config.get_main_option("sqlalchemy.url")
    if cfg_url and cfg_url.strip() and not cfg_url.startswith("driver://"):
        return DatabaseConfig._normalize_driver(cfg_url.strip())
    return "sqlite:///alembic_schema.db"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    url = get_database_url()
    connectable = create_engine(
        url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
