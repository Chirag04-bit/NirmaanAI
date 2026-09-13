"""
NirmaanAI Base Declarative Schema & Reusable Mixins
Provides SQLAlchemy 2.x DeclarativeBase, UTC timestamp helpers, and research provenance mixins.
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    """Returns the current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Authoritative base declarative class for NirmaanAI PostgreSQL models."""
    pass


class TimestampMixin:
    """Provides standard audit creation and modification timestamps in UTC."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )


class ProvenanceMixin:
    """
    Research-grade provenance tracking for analytical, ML, and decision artifacts.
    Guarantees every persisted AI output records source, version, timestamp, and epistemic classification.
    """
    source: Mapped[str] = mapped_column(String(100), default="NIRMAAN_PIPELINE", nullable=False)
    dataset_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pipeline_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    as_of_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    provenance: Mapped[str] = mapped_column(
        String(60),
        default="DERIVED_FROM_OBSERVED",
        nullable=False,
    )
    epistemic_status: Mapped[str] = mapped_column(
        String(60),
        default="EMPIRICAL_EVIDENCE",
        nullable=False,
    )
