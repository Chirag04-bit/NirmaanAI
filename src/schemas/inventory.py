"""
NirmaanAI Inventory Schemas (Pydantic v2)
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class InventoryItemResponse(BaseModel):
    """
    Inventory and spare parts contract.
    Preserves authoritative Phase 10 parameters (e.g. M2 bearing stock=2.0, SS=1.134, ROP=1.367).
    """
    model_config = ConfigDict(from_attributes=True)

    inventory_id: str
    factory_id: str
    sku_id: str
    item_name: str
    category: str
    current_stock: float
    safety_stock: float
    reorder_point: float
    lead_time_days: float
    unit_cost_inr: float
    reorder_quantity_eoq: Optional[float] = None
    days_of_stock: Optional[float] = None
    stock_status: Optional[str] = Field(
        default=None,
        description="OPTIMAL_BUFFER, REORDER_NOW, CRITICAL_DEFICIT, OUT_OF_STOCK, etc."
    )
    last_replenished: Optional[datetime] = None
    created_at: Optional[datetime] = None
