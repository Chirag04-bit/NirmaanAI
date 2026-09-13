"""
NirmaanAI Production Schemas (Pydantic v2)
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProductionJobResponse(BaseModel):
    """Production job scheduling, dispatch, and quantity tracking."""
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    factory_id: str
    machine_id: str
    product_id: Optional[str] = None
    operation_type: str
    scheduled_start: datetime
    scheduled_end: datetime
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    quantity: int
    completed_quantity: int
    scrap_quantity: int
    status: str
    batch_number: Optional[str] = None
    cycle_time_actual_sec: Optional[float] = None
    created_at: Optional[datetime] = None
