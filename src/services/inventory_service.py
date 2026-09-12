"""
NirmaanAI Inventory Service Layer
Phase 10: Smart Inventory Intelligence

Exposes real-time API services for:
1. SKU Inventory State Audit & Operations Research Optimization (SS, ROP, EOQ, DoS).
2. Multi-tier Stockout / Shortage Risk Evaluation.
3. Plant-wide Inventory Health & Capital Summary.
4. Machine 2 Maintenance-Spare Coupling Evaluation (linking degradation alerts to spare availability).

RESEARCH INTEGRITY:
- Preserves Phase 6 empirical failure threshold (0.91) for equipment alerts.
- Configured synthetic vibration trigger (3.80 mm/s) explicitly labeled.
- Preserves 7-day physical vendor transit lead-time constraint.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib
import pandas as pd
from pydantic import BaseModel, Field

from src.features.inventory_features import (
    CONFIGURED_BOM_MAP,
    compute_sku_demand_statistics,
    derive_daily_sku_consumption,
    load_inventory_catalog,
)
from src.models.inventory_optimizer import InventoryOptimizer
from src.utils.config_loader import get_project_root
from src.utils.logger import logger


class SkuAuditRequest(BaseModel):
    sku_id: str = Field(description="Unique inventory SKU identifier")
    current_stock_override: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Optional override for current warehouse stock level"
    )
    unit_cost_override: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Optional override for unit cost in INR"
    )


class SkuAuditResponse(BaseModel):
    sku_id: str
    category: str
    current_stock: float
    unit_cost_inr: float
    d_mean_daily: float
    sigma_d_daily: float
    lead_time_mean_days: float
    lead_time_std_days: float
    service_level_target: float
    z_score: float
    safety_stock: float
    reorder_point: float
    eoq: float
    days_of_supply: float
    inventory_tier: str
    action_urgency: str
    shortage_risk_score: float
    reorder_needed: bool
    recommended_order_qty: float
    capital_tied_inr: float
    reorder_estimated_capital_inr: float


class PlantInventorySummaryResponse(BaseModel):
    total_skus_tracked: int
    skus_requiring_reorder: int
    critical_deficit_count: int
    total_working_capital_tied_inr: float
    total_reorder_commitment_inr: float
    sku_audits: List[SkuAuditResponse]


class MachineMaintenanceCouplingRequest(BaseModel):
    machine_id: str = Field(default="M2", description="Machine identifier (e.g. M2)")
    failure_prob: float = Field(ge=0.0, le=1.0, description="Predictive maintenance failure probability from Phase 6 model")
    vibration_mms: float = Field(ge=0.0, description="Current machine spindle vibration velocity in mm/s")
    current_spare_stock_override: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Optional override for current stock of SKU_SPINDLE_BEARING_M2"
    )


class MachineMaintenanceCouplingResponse(BaseModel):
    machine_id: str
    failure_prob: float
    empirical_decision_threshold: float
    is_empirical_failure_predicted: bool
    vibration_mms: float
    synthetic_vibration_trigger: float
    is_synthetic_vibration_alert: bool
    maintenance_required: bool
    bearing_sku: str
    current_bearing_stock: float
    stock_post_maintenance: float
    lead_time_days: float
    is_constrained_maintenance: bool
    coupling_status: str
    risk_level: str
    status_message: str
    lead_time_reality_caveat: str


class InventoryService:
    """Service facade providing real-time inventory intelligence and maintenance coupling."""

    def __init__(self, model_dir: Optional[Path] = None):
        root = get_project_root()
        self.model_dir = model_dir or (root / "models" / "inventory_intelligence")
        self.optimizer = InventoryOptimizer(default_annual_working_days=312)
        self._load_cached_state()

    def _load_cached_state(self) -> None:
        """Loads cached bundle or initializes baseline from data sources."""
        joblib_path = self.model_dir / "inventory_optimizer.joblib"
        if joblib_path.exists():
            try:
                bundle = joblib.load(joblib_path)
                self.optimizer = bundle["optimizer"]
                self.demand_stats = bundle["demand_stats"]
                self.bom_map = bundle["bom_map"]
                self.df_summary = bundle["sku_summary"]
                logger.info("Loaded precomputed InventoryOptimizer bundle.")
                return
            except Exception as e:
                logger.warning(f"Could not load precomputed bundle ({e}), initializing freshly.")

        # Fallback fresh initialization
        df_catalog = load_inventory_catalog()
        df_consumption = derive_daily_sku_consumption()
        self.demand_stats = compute_sku_demand_statistics(df_consumption)
        self.bom_map = CONFIGURED_BOM_MAP

    def audit_single_sku(self, req: SkuAuditRequest) -> SkuAuditResponse:
        """Performs real-time OR audit for a single SKU."""
        df_catalog = load_inventory_catalog()
        matches = df_catalog[df_catalog["sku_id"] == req.sku_id]

        if len(matches) == 0:
            raise ValueError(f"SKU '{req.sku_id}' not found in inventory catalog.")

        row = matches.iloc[0]
        current_stock = req.current_stock_override if req.current_stock_override is not None else float(row["current_stock"])
        unit_cost = req.unit_cost_override if req.unit_cost_override is not None else float(row["unit_cost"])

        bom_cfg = self.bom_map.get(req.sku_id, {
            "category": str(row.get("category", "GENERAL")),
            "lead_time_days": float(row.get("lead_time_days", 5.0)),
            "lead_time_std_days": 1.0,
            "service_level_target": 0.95,
            "order_setup_cost_inr": 1500.0,
            "annual_holding_rate": 0.20
        })

        sku_stats = self.demand_stats.get(req.sku_id, {
            "d_mean": 0.0,
            "sigma_d": 0.0,
            "min_daily": 0.0,
            "max_daily": 0.0,
            "days_observed": 0
        })

        audit_dict = self.optimizer.audit_sku_inventory(
            sku_id=req.sku_id,
            current_stock=current_stock,
            unit_cost=unit_cost,
            demand_stats=sku_stats,
            bom_config=bom_cfg
        )

        return SkuAuditResponse(**audit_dict)

    def get_plant_inventory_summary(self) -> PlantInventorySummaryResponse:
        """Calculates comprehensive plant-wide inventory state across all tracked SKUs."""
        df_catalog = load_inventory_catalog()
        audits: List[SkuAuditResponse] = []
        total_capital = 0.0
        total_reorder_capital = 0.0
        reorder_count = 0
        critical_count = 0

        for _, row in df_catalog.iterrows():
            req = SkuAuditRequest(sku_id=str(row["sku_id"]))
            audit = self.audit_single_sku(req)
            audits.append(audit)
            total_capital += audit.capital_tied_inr
            total_reorder_capital += audit.reorder_estimated_capital_inr
            if audit.reorder_needed:
                reorder_count += 1
            if audit.inventory_tier in ("OUT_OF_STOCK", "CRITICAL_DEFICIT"):
                critical_count += 1

        return PlantInventorySummaryResponse(
            total_skus_tracked=len(audits),
            skus_requiring_reorder=reorder_count,
            critical_deficit_count=critical_count,
            total_working_capital_tied_inr=round(total_capital, 2),
            total_reorder_commitment_inr=round(total_reorder_capital, 2),
            sku_audits=audits
        )

    def evaluate_maintenance_spare_coupling(
        self,
        req: MachineMaintenanceCouplingRequest
    ) -> MachineMaintenanceCouplingResponse:
        """
        Evaluates machine health degradation against spare bearing stock.
        """
        if req.current_spare_stock_override is not None:
            bearing_stock = req.current_spare_stock_override
        else:
            df_catalog = load_inventory_catalog()
            bearing_row = df_catalog[df_catalog["sku_id"] == "SKU_SPINDLE_BEARING_M2"]
            bearing_stock = float(bearing_row["current_stock"].iloc[0]) if len(bearing_row) > 0 else 1.0

        res_dict = self.optimizer.evaluate_machine2_maintenance_coupling(
            failure_prob=req.failure_prob,
            vibration_mms=req.vibration_mms,
            sku_spindle_stock=bearing_stock,
            lead_time_days=7.0,
            decision_threshold=0.91,
            synthetic_vibration_trigger=3.80
        )

        return MachineMaintenanceCouplingResponse(**res_dict)

    # Alias for convenience
    evaluate_maintenance_coupling = evaluate_maintenance_spare_coupling
