"""
NirmaanAI Production Database Layer (Phase 17)
Provides PostgreSQL persistence, connection lifecycle management, and relational ORM models.
"""

from src.db.base import Base, ProvenanceMixin, TimestampMixin, utcnow
from src.db.config import (
    DatabaseConfig,
    DatabaseConfigurationError,
    get_default_config,
    is_postgres_available,
)
from src.db.session import (
    get_db_session,
    get_engine,
    get_session_factory,
    reset_engine,
)
from src.db.models import (
    AnomalyDetectionResult,
    BottleneckPredictionResult,
    Factory,
    FactoryHealthScore,
    FinancialLossRecord,
    ForecastingResult,
    InventoryItem,
    Machine,
    MachineTelemetrySnapshot,
    MaintenanceRecord,
    OperationalRecommendation,
    PredictiveMaintenancePrediction,
    Product,
    ProductionJob,
    RcaResult,
    Sensor,
    SensorReading,
    ShapExplanation,
    SimulationScenario,
)

__all__ = [
    "Base",
    "TimestampMixin",
    "ProvenanceMixin",
    "utcnow",
    "DatabaseConfig",
    "DatabaseConfigurationError",
    "get_default_config",
    "is_postgres_available",
    "get_engine",
    "get_session_factory",
    "get_db_session",
    "reset_engine",
    "Factory",
    "Machine",
    "Sensor",
    "Product",
    "ProductionJob",
    "SensorReading",
    "MachineTelemetrySnapshot",
    "MaintenanceRecord",
    "InventoryItem",
    "PredictiveMaintenancePrediction",
    "AnomalyDetectionResult",
    "BottleneckPredictionResult",
    "ForecastingResult",
    "ShapExplanation",
    "RcaResult",
    "FactoryHealthScore",
    "FinancialLossRecord",
    "OperationalRecommendation",
    "SimulationScenario",
]
