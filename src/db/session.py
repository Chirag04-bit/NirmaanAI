"""
NirmaanAI Database Engine & Session Management
Follows SQLAlchemy 2.x best practices with connection pooling, transactional context managers,
and clean lifecycle control.
"""

from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.db.config import DatabaseConfig, get_default_config

_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker[Session]] = None


def get_engine(config: Optional[DatabaseConfig] = None) -> Engine:
    """
    Retrieves or initializes the global SQLAlchemy Engine.
    Uses connection pooling and ping validation for robust connection management.
    """
    global _engine
    if config is not None:
        return _build_engine(config)

    if _engine is None:
        _engine = _build_engine(get_default_config())
    return _engine


def _build_engine(config: DatabaseConfig) -> Engine:
    """Instantiates an Engine with dialect-appropriate pooling arguments."""
    if config.is_sqlite:
        # SQLite in-memory or file (typically used in unit tests)
        return create_engine(
            config.database_url,
            echo=config.echo,
            connect_args={"check_same_thread": False} if ":memory:" in config.database_url or "sqlite" in config.database_url else {},
        )
    # PostgreSQL production configuration
    return create_engine(
        config.database_url,
        pool_size=config.pool_size,
        max_overflow=config.max_overflow,
        pool_timeout=config.pool_timeout,
        pool_recycle=config.pool_recycle,
        pool_pre_ping=True,
        echo=config.echo,
    )


def get_session_factory(engine: Optional[Engine] = None) -> sessionmaker[Session]:
    """Returns a sessionmaker bound to the given or global engine."""
    global _session_factory
    target_engine = engine or get_engine()
    if _session_factory is None or engine is not None:
        factory = sessionmaker(bind=target_engine, autoflush=False, autocommit=False, expire_on_commit=False)
        if engine is None:
            _session_factory = factory
        return factory
    return _session_factory


@contextmanager
def get_db_session(engine: Optional[Engine] = None) -> Generator[Session, None, None]:
    """
    Context manager providing a transactional database session.
    Automatically commits on success and rolls back on exception.
    """
    factory = get_session_factory(engine)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def reset_engine():
    """Disposes global engine and resets sessionmaker (useful for test isolation)."""
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None
