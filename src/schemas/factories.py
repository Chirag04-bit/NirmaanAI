"""
NirmaanAI Factory Schemas (Pydantic v2)
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.schemas.common import ResponseMetadata


class FactoryResponse(BaseModel):
    """Core factory representation."""
    model_config = ConfigDict(from_attributes=True)

    factory_id: str = Field(description="Unique factory identifier.")
    factory_code: str = Field(description="Short human-readable factory code.")
    name: str = Field(description="Plant or enterprise name.")
    location: Optional[str] = Field(default=None, description="Geographic location.")
    industry: Optional[str] = Field(default=None, description="Industry sector.")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class FactoryOverviewResponse(BaseModel):
    """Executive factory overview synthesizing physical assets, health, alerts, and exposure."""
    model_config = ConfigDict(from_attributes=True)

    factory_id: str
    factory_name: str
    total_machines: int = Field(ge=0, description="Total physical machines installed.")
    active_machines: int = Field(ge=0, description="Machines in RUNNING or IDLE status.")
    critical_machines: int = Field(ge=0, description="Machines in CRITICAL or DEGRADED state.")
    plant_health_score: Optional[float] = Field(default=None, description="Composite plant health index [0-100].")
    plant_health_state: Optional[str] = Field(default=None, description="Plant health band: EXCELLENT, HEALTHY, WATCH, etc.")
    active_recommendations_count: int = Field(default=0, description="Total pending recommendations.")
    total_gross_exposure_inr: float = Field(default=0.0, description="Total plant gross financial exposure (INR).")
    metadata: Optional[ResponseMetadata] = None
