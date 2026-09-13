"""
NirmaanAI Inventory API Service
Preserves authoritative Phase 10 inventory contracts.
"""

from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.db.models.operations import InventoryItem
from src.schemas.inventory import InventoryItemResponse


class InventoryApiService:
    @staticmethod
    def list_inventory(
        db: Session,
        factory_id: Optional[str] = None,
        category: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[InventoryItemResponse], int]:
        stmt = select(InventoryItem)
        if factory_id:
            stmt = stmt.where(InventoryItem.factory_id == factory_id)
        if category:
            stmt = stmt.where(InventoryItem.category == category)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        offset = (page - 1) * page_size
        stmt = stmt.order_by(InventoryItem.sku_id).offset(offset).limit(page_size)
        items = db.scalars(stmt).all()
        responses = [InventoryItemResponse.model_validate(it) for it in items]
        return responses, total

    @staticmethod
    def get_by_sku(db: Session, sku_id: str) -> Optional[InventoryItemResponse]:
        item = db.scalar(select(InventoryItem).where(InventoryItem.sku_id == sku_id))
        if not item:
            return None
        return InventoryItemResponse.model_validate(item)

    @staticmethod
    def get_machine_inventory(db: Session, machine_id: str) -> List[InventoryItemResponse]:
        # Coupled machine spare items
        stmt = (
            select(InventoryItem)
            .where(InventoryItem.sku_id.like(f"%_{machine_id}%"))
            .order_by(InventoryItem.sku_id)
        )
        items = db.scalars(stmt).all()
        return [InventoryItemResponse.model_validate(it) for it in items]

    get_machine_spares = get_machine_inventory
