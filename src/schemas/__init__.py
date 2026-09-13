"""
NirmaanAI Schemas Package
Exports all typed Pydantic v2 schemas for Phase 18 API.
"""

from src.schemas.common import (
    Envelope,
    ErrorDetail,
    ErrorResponse,
    PaginatedResponse,
    PaginationParams,
    ResponseMetadata,
)
from src.schemas.factories import FactoryOverviewResponse, FactoryResponse
from src.schemas.machines import MachineOverviewResponse, MachineResponse
from src.schemas.sensors import (
    SensorReadingResponse,
    SensorResponse,
    TelemetryQueryParams,
    TelemetrySnapshotResponse,
)
from src.schemas.production import ProductionJobResponse
from src.schemas.maintenance import MaintenanceRecordResponse
from src.schemas.inventory import InventoryItemResponse
from src.schemas.ai_outputs import (
    AnomalyDetectionResponse,
    BottleneckResponse,
    FactoryHealthScoreResponse,
    ForecastingResponse,
    PredictiveMaintenanceResponse,
    RcaResultResponse,
    ShapExplanationResponse,
)
from src.schemas.finance import FinancialLossResponse, MachineFinancialSummaryResponse
from src.schemas.recommendations import RecommendationResponse
from src.schemas.simulations import SimulationScenarioResponse

__all__ = [
    "Envelope",
    "ErrorDetail",
    "ErrorResponse",
    "PaginatedResponse",
    "PaginationParams",
    "ResponseMetadata",
    "FactoryResponse",
    "FactoryOverviewResponse",
    "MachineResponse",
    "MachineOverviewResponse",
    "SensorResponse",
    "SensorReadingResponse",
    "TelemetrySnapshotResponse",
    "TelemetryQueryParams",
    "ProductionJobResponse",
    "MaintenanceRecordResponse",
    "InventoryItemResponse",
    "PredictiveMaintenanceResponse",
    "AnomalyDetectionResponse",
    "BottleneckResponse",
    "ForecastingResponse",
    "ShapExplanationResponse",
    "RcaResultResponse",
    "FactoryHealthScoreResponse",
    "FinancialLossResponse",
    "MachineFinancialSummaryResponse",
    "RecommendationResponse",
    "SimulationScenarioResponse",
]
