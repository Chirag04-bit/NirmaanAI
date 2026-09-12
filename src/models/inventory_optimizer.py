"""
NirmaanAI Inventory Optimizer & Operations Research Engine
Phase 10: Smart Inventory Intelligence

Implements deterministic Operations Research (OR) inventory optimization models:
- Dynamic Safety Stock (SS) accounting for both demand variance and vendor lead-time variance.
- Reorder Point (ROP).
- Economic Order Quantity (EOQ - Wilson-Harris model).
- Days of Supply (DoS).
- Multi-tier Stockout / Shortage Risk Classification.
- Machine 2 Predictive Maintenance-Spare Inventory Coupling.

RESEARCH INTEGRITY & LABELED SYNTHETIC RELATIONSHIPS:
- Pure deterministic Operations Research formulations.
- Explicit service-level quantile assumptions: Z=1.645 (95% standard) and Z=2.326 (99% critical spare).
- Machine 2 maintenance coupling preserves Phase 6 AI4I decision threshold (0.91).
- Physical vendor lead times are respected; emergency POs do not instantly eliminate transit delays.
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from scipy import stats

from src.utils.logger import logger


class InventoryOptimizer:
    """
    Operations Research Inventory Intelligence Engine for MSME Manufacturing.
    """

    # Configured standard Z-score mapping (explicit simulation assumptions)
    SERVICE_LEVEL_Z_MAP: Dict[float, float] = {
        0.90: 1.282,
        0.95: 1.645,  # Standard raw materials
        0.98: 2.054,
        0.99: 2.326,  # Critical maintenance spares & high-wear tooling
        0.999: 3.090
    }

    # Working days per calendar year in standard Indian MSME (6-day single/double shift)
    ANNUAL_WORKING_DAYS: int = 312

    def __init__(self, default_annual_working_days: int = 312):
        self.annual_working_days = default_annual_working_days

    @classmethod
    def get_z_score(cls, service_level: float) -> float:
        """
        Returns the standard normal quantile Z for the requested service level.
        Validates 0 < service_level < 1.0.
        """
        if not (0.0 < service_level < 1.0):
            raise ValueError(f"Service level must be strictly between 0 and 1, got {service_level}")

        rounded = round(service_level, 3)
        if rounded in cls.SERVICE_LEVEL_Z_MAP:
            return cls.SERVICE_LEVEL_Z_MAP[rounded]

        # Analytical fallback via SciPy
        return float(stats.norm.ppf(service_level))

    @staticmethod
    def calculate_safety_stock(
        d_mean: float,
        sigma_d: float,
        lead_time_mean: float,
        lead_time_std: float,
        service_level: float = 0.95
    ) -> float:
        """
        Calculates dynamic Safety Stock (SS) considering joint demand and lead-time uncertainties.
        Formula: SS = Z * sqrt(L_mean * sigma_d^2 + d_mean^2 * sigma_L^2)

        Edge cases:
        - Negative inputs raise ValueError.
        - Zero demand and zero variance yield SS = 0.0.
        """
        if d_mean < 0:
            raise ValueError(f"Mean daily demand d_mean cannot be negative: {d_mean}")
        if sigma_d < 0:
            raise ValueError(f"Demand std sigma_d cannot be negative: {sigma_d}")
        if lead_time_mean < 0:
            raise ValueError(f"Lead time mean cannot be negative: {lead_time_mean}")
        if lead_time_std < 0:
            raise ValueError(f"Lead time std cannot be negative: {lead_time_std}")

        if d_mean == 0.0 and sigma_d == 0.0:
            return 0.0

        z = InventoryOptimizer.get_z_score(service_level)
        variance_term = (lead_time_mean * (sigma_d ** 2)) + ((d_mean ** 2) * (lead_time_std ** 2))
        ss = z * math.sqrt(variance_term)
        return float(round(ss, 3))

    @staticmethod
    def calculate_reorder_point(
        d_mean: float,
        lead_time_mean: float,
        safety_stock: float
    ) -> float:
        """
        Calculates Reorder Point (ROP).
        Formula: ROP = (d_mean * lead_time_mean) + safety_stock
        """
        if d_mean < 0:
            raise ValueError(f"Mean daily demand d_mean cannot be negative: {d_mean}")
        if lead_time_mean < 0:
            raise ValueError(f"Lead time mean cannot be negative: {lead_time_mean}")
        if safety_stock < 0:
            raise ValueError(f"Safety stock cannot be negative: {safety_stock}")

        lead_time_demand = d_mean * lead_time_mean
        rop = lead_time_demand + safety_stock
        return float(round(rop, 3))

    @staticmethod
    def calculate_eoq(
        annual_demand: float,
        order_setup_cost: float,
        unit_cost: float,
        annual_holding_rate: float = 0.20
    ) -> float:
        """
        Calculates Economic Order Quantity (EOQ - Wilson-Harris formulation).
        Formula: EOQ = sqrt((2 * D * S) / H)
        where:
          D = annual demand
          S = setup / order placement cost
          H = annual holding cost per unit = unit_cost * annual_holding_rate
        """
        if annual_demand < 0:
            raise ValueError(f"Annual demand cannot be negative: {annual_demand}")
        if order_setup_cost < 0:
            raise ValueError(f"Order setup cost cannot be negative: {order_setup_cost}")
        if unit_cost < 0:
            raise ValueError(f"Unit cost cannot be negative: {unit_cost}")
        if annual_holding_rate <= 0:
            raise ValueError(f"Annual holding rate must be positive: {annual_holding_rate}")

        if annual_demand == 0.0:
            return 0.0

        h = unit_cost * annual_holding_rate
        if h <= 0:
            raise ValueError(f"Holding cost per unit must be strictly positive, got H={h}")

        eoq = math.sqrt((2.0 * annual_demand * order_setup_cost) / h)
        return float(round(eoq, 3))

    @staticmethod
    def calculate_days_of_supply(
        current_stock: float,
        d_mean: float
    ) -> float:
        """
        Calculates Days of Supply (DoS).
        Formula: DoS = current_stock / d_mean
        If d_mean <= 0, returns float('inf') if current_stock > 0 else 0.0.
        """
        if current_stock < 0:
            return 0.0
        if d_mean <= 0:
            return float('inf') if current_stock > 0 else 0.0

        dos = current_stock / d_mean
        return float(round(dos, 2))

    @staticmethod
    def classify_stock_status(
        current_stock: float,
        safety_stock: float,
        reorder_point: float,
        eoq: float
    ) -> Dict[str, Any]:
        """
        Classifies stock level into actionable operational tiers:
        - OUT_OF_STOCK: stock <= 0
        - CRITICAL_DEFICIT: 0 < stock <= safety_stock (severe stockout risk)
        - REORDER_NOW: safety_stock < stock <= reorder_point (procurement trigger)
        - OPTIMAL_BUFFER: reorder_point < stock <= (reorder_point + eoq)
        - SURPLUS_INVENTORY: stock > (reorder_point + eoq) (working capital trapped)
        """
        if current_stock <= 0:
            tier = "OUT_OF_STOCK"
            urgency = "IMMEDIATE_EXPEDITE"
            shortage_risk = 1.0
            reorder_needed = True
            recommended_order_qty = max(eoq, reorder_point - current_stock)
        elif current_stock <= safety_stock:
            tier = "CRITICAL_DEFICIT"
            urgency = "HIGH_PRIORITY"
            shortage_risk = 0.85
            reorder_needed = True
            recommended_order_qty = max(eoq, reorder_point - current_stock)
        elif current_stock <= reorder_point:
            tier = "REORDER_NOW"
            urgency = "STANDARD_REORDER"
            shortage_risk = 0.50
            reorder_needed = True
            recommended_order_qty = eoq
        elif current_stock <= (reorder_point + eoq):
            tier = "OPTIMAL_BUFFER"
            urgency = "NONE"
            shortage_risk = 0.05
            reorder_needed = False
            recommended_order_qty = 0.0
        else:
            tier = "SURPLUS_INVENTORY"
            urgency = "MONITOR_HOLDING"
            shortage_risk = 0.0
            reorder_needed = False
            recommended_order_qty = 0.0

        return {
            "inventory_tier": tier,
            "action_urgency": urgency,
            "shortage_risk_score": shortage_risk,
            "reorder_needed": reorder_needed,
            "recommended_order_qty": float(round(recommended_order_qty, 3))
        }

    def audit_sku_inventory(
        self,
        sku_id: str,
        current_stock: float,
        unit_cost: float,
        demand_stats: Dict[str, float],
        bom_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes end-to-end OR optimization and replenishment audit for a single SKU.
        """
        d_mean = demand_stats.get("d_mean", 0.0)
        sigma_d = demand_stats.get("sigma_d", 0.0)

        lt_mean = bom_config.get("lead_time_days", 5.0)
        lt_std = bom_config.get("lead_time_std_days", 1.0)
        service_level = bom_config.get("service_level_target", 0.95)
        setup_cost = bom_config.get("order_setup_cost_inr", 1500.0)
        holding_rate = bom_config.get("annual_holding_rate", 0.20)
        category = bom_config.get("category", "RAW_MATERIAL")

        annual_demand = d_mean * self.annual_working_days

        # Deterministic OR Formulations
        ss = self.calculate_safety_stock(
            d_mean=d_mean,
            sigma_d=sigma_d,
            lead_time_mean=lt_mean,
            lead_time_std=lt_std,
            service_level=service_level
        )

        rop = self.calculate_reorder_point(
            d_mean=d_mean,
            lead_time_mean=lt_mean,
            safety_stock=ss
        )

        eoq = self.calculate_eoq(
            annual_demand=annual_demand,
            order_setup_cost=setup_cost,
            unit_cost=unit_cost,
            annual_holding_rate=holding_rate
        )

        dos = self.calculate_days_of_supply(
            current_stock=current_stock,
            d_mean=d_mean
        )

        status = self.classify_stock_status(
            current_stock=current_stock,
            safety_stock=ss,
            reorder_point=rop,
            eoq=eoq
        )

        return {
            "sku_id": sku_id,
            "category": category,
            "current_stock": round(current_stock, 3),
            "unit_cost_inr": unit_cost,
            "d_mean_daily": d_mean,
            "sigma_d_daily": sigma_d,
            "lead_time_mean_days": lt_mean,
            "lead_time_std_days": lt_std,
            "service_level_target": service_level,
            "z_score": self.get_z_score(service_level),
            "safety_stock": ss,
            "reorder_point": rop,
            "eoq": eoq,
            "days_of_supply": dos,
            "inventory_tier": status["inventory_tier"],
            "action_urgency": status["action_urgency"],
            "shortage_risk_score": status["shortage_risk_score"],
            "reorder_needed": status["reorder_needed"],
            "recommended_order_qty": status["recommended_order_qty"],
            "capital_tied_inr": round(current_stock * unit_cost, 2),
            "reorder_estimated_capital_inr": round(status["recommended_order_qty"] * unit_cost, 2)
        }

    @staticmethod
    def evaluate_machine2_maintenance_coupling(
        failure_prob: float,
        vibration_mms: float,
        sku_spindle_stock: float,
        lead_time_days: float = 7.0,
        decision_threshold: float = 0.91,
        synthetic_vibration_trigger: float = 3.80
    ) -> Dict[str, Any]:
        """
        Evaluates the coupling between Machine 2 degradation and SKU_SPINDLE_BEARING_M2 inventory.

        RESEARCH INTEGRITY:
        - Empirical AI4I decision threshold is 0.91 (strict Phase 6 semantics, NOT 0.50).
        - Synthetic vibration trigger (3.8 mm/s) is labeled as a CONFIGURED SYNTHETIC SCENARIO TRIGGER.
        - Physical lead time constraint: 7 days vendor delivery cannot be resolved instantaneously by emergency PO.
        """
        # Triggers
        is_empirical_failure_predicted = failure_prob >= decision_threshold
        is_synthetic_vibration_alert = vibration_mms >= synthetic_vibration_trigger

        maintenance_required = is_empirical_failure_predicted or is_synthetic_vibration_alert

        # Bearing requirements for M2 spindle overhaul
        bearing_required = 1.0 if maintenance_required else 0.0
        stock_post_maintenance = sku_spindle_stock - bearing_required

        # Evaluate constraints
        is_constrained = False
        status_message = "Normal operation. Spindle bearing inventory sufficient."

        if not maintenance_required:
            coupling_status = "NORMAL_OPERATION"
            risk_level = "LOW"
        else:
            if sku_spindle_stock < 1.0:
                coupling_status = "CRITICAL_MAINTENANCE_BLOCKED"
                risk_level = "CRITICAL"
                is_constrained = True
                status_message = (
                    f"IMMEDIATE DOWNTIME HAZARD: Machine 2 maintenance triggered (fail_prob={failure_prob:.3f}, "
                    f"vib={vibration_mms:.2f} mm/s), but SKU_SPINDLE_BEARING_M2 stock is {sku_spindle_stock:.1f}. "
                    f"Physical vendor lead time is {lead_time_days} days. Emergency PO CANNOT instantly eliminate physical transit time. "
                    f"Machine 2 must halt or operate under emergency derating until spare arrives."
                )
            elif stock_post_maintenance == 0:
                coupling_status = "MAINTENANCE_PERMITTED_ZERO_POST_BUFFER"
                risk_level = "HIGH"
                is_constrained = True
                status_message = (
                    f"CONSTRAINED MAINTENANCE ALERT: 1 bearing available to service M2 immediately, but replacing it "
                    f"drops warehouse stock to 0.0 (below safety stock). Supplier lead time is {lead_time_days} days. "
                    f"Immediate purchase order required. Any concurrent bearing failure within {lead_time_days} days will shut down line."
                )
            else:
                coupling_status = "MAINTENANCE_PERMITTED_BUFFER_RETAINED"
                risk_level = "MEDIUM"
                status_message = (
                    f"Maintenance feasible with remaining spare buffer. Post-maintenance stock: {stock_post_maintenance:.1f}."
                )

        return {
            "machine_id": "M2",
            "failure_prob": failure_prob,
            "empirical_decision_threshold": decision_threshold,
            "is_empirical_failure_predicted": is_empirical_failure_predicted,
            "vibration_mms": vibration_mms,
            "synthetic_vibration_trigger": synthetic_vibration_trigger,
            "is_synthetic_vibration_alert": is_synthetic_vibration_alert,
            "maintenance_required": maintenance_required,
            "bearing_sku": "SKU_SPINDLE_BEARING_M2",
            "current_bearing_stock": sku_spindle_stock,
            "stock_post_maintenance": max(0.0, stock_post_maintenance),
            "lead_time_days": lead_time_days,
            "is_constrained_maintenance": is_constrained,
            "coupling_status": coupling_status,
            "risk_level": risk_level,
            "status_message": status_message,
            "lead_time_reality_caveat": (
                f"Configured vendor lead time is {lead_time_days} days. Emergency procurement does NOT eliminate transit time."
            )
        }
