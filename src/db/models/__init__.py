"""
NirmaanAI Database Models Package
Exports all declarative models across physical factory, operations, and AI intelligence domains.
"""

from src.db.models.factory import Factory, Machine, Product, Sensor
from src.db.models.operations import (
    InventoryItem,
    MachineTelemetrySnapshot,
    MaintenanceRecord,
    ProductionJob,
    SensorReading,
)
from src.db.models.ai_outputs import (
    AnomalyDetectionResult,
    BottleneckPredictionResult,
    FactoryHealthScore,
    FinancialLossRecord,
    ForecastingResult,
    OperationalRecommendation,
    PredictiveMaintenancePrediction,
    RcaResult,
    ShapExplanation,
    SimulationScenario,
)

__all__ = [
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
