"""
NirmaanAI Inventory Intelligence Unit & Integration Tests
Phase 10: Smart Inventory Intelligence

Comprehensive verification suite for:
- Operations Research formulas (Safety Stock, ROP, EOQ, DoS).
- Mathematical validity and service-level scaling (Z=1.645 vs Z=2.326).
- Edge cases: zero demand, negative stock, invalid lead times, invalid costs.
- Stockout classification tiers.
- Machine 2 Maintenance-Spare Coupling (threshold 0.91, vibration 3.80 mm/s, 7-day lead time).
- End-to-end reproducibility and data integrity.
"""

import math
import pytest
import pandas as pd
import numpy as np

from src.features.inventory_features import (
    CONFIGURED_BOM_MAP,
    compute_sku_demand_statistics,
    derive_daily_sku_consumption,
    load_inventory_catalog,
)
from src.models.inventory_optimizer import InventoryOptimizer
from src.services.inventory_service import (
    InventoryService,
    MachineMaintenanceCouplingRequest,
    SkuAuditRequest,
)


class TestInventoryFormulas:
    """Validates deterministic Operations Research mathematical models."""

    def test_dynamic_safety_stock_calculation(self):
        """Tests standard formula: SS = Z * sqrt(L_mean * sigma_d^2 + d_mean^2 * sigma_L^2)"""
        d_mean = 10.0
        sigma_d = 2.0
        lt_mean = 4.0
        lt_std = 1.0
        service_level = 0.95  # Z = 1.645

        # Analytical:
        # variance_term = 4.0 * (2.0^2) + (10.0^2) * (1.0^2) = 4 * 4 + 100 * 1 = 16 + 100 = 116
        # sqrt(116) = 10.77033
        # SS = 1.645 * 10.77033 = 17.71719 -> 17.717
        ss = InventoryOptimizer.calculate_safety_stock(
            d_mean=d_mean,
            sigma_d=sigma_d,
            lead_time_mean=lt_mean,
            lead_time_std=lt_std,
            service_level=service_level
        )
        assert pytest.approx(ss, abs=0.01) == 17.717

    def test_reorder_point_calculation(self):
        """Tests ROP = (d_mean * L_mean) + SS"""
        d_mean = 10.0
        lt_mean = 5.0
        safety_stock = 25.0

        rop = InventoryOptimizer.calculate_reorder_point(
            d_mean=d_mean,
            lead_time_mean=lt_mean,
            safety_stock=safety_stock
        )
        # Expected: 10 * 5 + 25 = 75.0
        assert rop == 75.0

    def test_eoq_wilson_harris_formula(self):
        """Tests EOQ = sqrt((2 * D * S) / H)"""
        annual_demand = 3120.0  # e.g., 10 units/day * 312 days
        order_cost = 1500.0
        unit_cost = 100.0
        holding_rate = 0.20  # H = 100 * 0.20 = 20.0

        # Analytical: sqrt((2 * 3120 * 1500) / 20) = sqrt(9360000 / 20) = sqrt(468000) = 684.105
        eoq = InventoryOptimizer.calculate_eoq(
            annual_demand=annual_demand,
            order_setup_cost=order_cost,
            unit_cost=unit_cost,
            annual_holding_rate=holding_rate
        )
        assert pytest.approx(eoq, abs=0.01) == 684.105

    def test_days_of_supply(self):
        """Tests DoS = Current Stock / d_mean"""
        current_stock = 150.0
        d_mean = 15.0

        dos = InventoryOptimizer.calculate_days_of_supply(current_stock, d_mean)
        assert dos == 10.0

    def test_service_level_z_scaling(self):
        """Verifies Z=1.645 for 95% and Z=2.326 for 99% critical spares."""
        z_95 = InventoryOptimizer.get_z_score(0.95)
        z_99 = InventoryOptimizer.get_z_score(0.99)

        assert z_95 == 1.645
        assert z_99 == 2.326
        assert z_99 > z_95

        # Higher service level yields strictly higher safety stock under identical demand
        ss_95 = InventoryOptimizer.calculate_safety_stock(10.0, 2.0, 5.0, 1.0, 0.95)
        ss_99 = InventoryOptimizer.calculate_safety_stock(10.0, 2.0, 5.0, 1.0, 0.99)
        assert ss_99 > ss_95


class TestEdgeCasesAndValidation:
    """Validates robust handling of zero demand, boundary, and invalid inputs."""

    def test_zero_demand_scenario(self):
        """Zero demand must yield zero SS, zero ROP, zero EOQ, and zero DoS."""
        ss = InventoryOptimizer.calculate_safety_stock(0.0, 0.0, 5.0, 1.0, 0.95)
        rop = InventoryOptimizer.calculate_reorder_point(0.0, 5.0, ss)
        eoq = InventoryOptimizer.calculate_eoq(0.0, 1500.0, 100.0, 0.20)
        dos = InventoryOptimizer.calculate_days_of_supply(0.0, 0.0)

        assert ss == 0.0
        assert rop == 0.0
        assert eoq == 0.0
        assert dos == 0.0

    def test_zero_and_negative_stock(self):
        """Zero and negative stock should produce DoS=0 and OUT_OF_STOCK classification."""
        dos_zero = InventoryOptimizer.calculate_days_of_supply(0.0, 10.0)
        dos_neg = InventoryOptimizer.calculate_days_of_supply(-5.0, 10.0)
        assert dos_zero == 0.0
        assert dos_neg == 0.0

        status_neg = InventoryOptimizer.classify_stock_status(
            current_stock=-2.0,
            safety_stock=10.0,
            reorder_point=25.0,
            eoq=50.0
        )
        assert status_neg["inventory_tier"] == "OUT_OF_STOCK"
        assert status_neg["action_urgency"] == "IMMEDIATE_EXPEDITE"
        assert status_neg["shortage_risk_score"] == 1.0
        assert status_neg["reorder_needed"] is True

    def test_invalid_lead_time_raises(self):
        """Negative lead time must raise ValueError."""
        with pytest.raises(ValueError, match="Lead time mean cannot be negative"):
            InventoryOptimizer.calculate_safety_stock(10.0, 2.0, -1.0, 1.0)

        with pytest.raises(ValueError, match="Lead time mean cannot be negative"):
            InventoryOptimizer.calculate_reorder_point(10.0, -5.0, 10.0)

    def test_invalid_cost_parameters_raise(self):
        """Negative unit costs or invalid holding rates must raise ValueError."""
        with pytest.raises(ValueError, match="Unit cost cannot be negative"):
            InventoryOptimizer.calculate_eoq(1000.0, 100.0, -50.0, 0.20)

        with pytest.raises(ValueError, match="Annual holding rate must be positive"):
            InventoryOptimizer.calculate_eoq(1000.0, 100.0, 50.0, -0.05)

    def test_stockout_classification_tiers(self):
        """Verifies transitions across all 5 inventory health tiers."""
        ss = 20.0
        rop = 50.0
        eoq = 100.0

        # 1. OUT_OF_STOCK
        c1 = InventoryOptimizer.classify_stock_status(0.0, ss, rop, eoq)
        assert c1["inventory_tier"] == "OUT_OF_STOCK"

        # 2. CRITICAL_DEFICIT (0 < stock <= ss)
        c2 = InventoryOptimizer.classify_stock_status(15.0, ss, rop, eoq)
        assert c2["inventory_tier"] == "CRITICAL_DEFICIT"
        assert c2["action_urgency"] == "HIGH_PRIORITY"

        # 3. REORDER_NOW (ss < stock <= rop)
        c3 = InventoryOptimizer.classify_stock_status(35.0, ss, rop, eoq)
        assert c3["inventory_tier"] == "REORDER_NOW"
        assert c3["reorder_needed"] is True

        # 4. OPTIMAL_BUFFER (rop < stock <= rop + eoq)
        c4 = InventoryOptimizer.classify_stock_status(80.0, ss, rop, eoq)
        assert c4["inventory_tier"] == "OPTIMAL_BUFFER"
        assert c4["reorder_needed"] is False

        # 5. SURPLUS_INVENTORY (stock > rop + eoq)
        c5 = InventoryOptimizer.classify_stock_status(180.0, ss, rop, eoq)
        assert c5["inventory_tier"] == "SURPLUS_INVENTORY"
        assert c5["action_urgency"] == "MONITOR_HOLDING"


class TestMachine2MaintenanceCoupling:
    """Validates predictive maintenance and critical spare coupling for Machine 2."""

    def test_empirical_decision_threshold_091(self):
        """Strict Phase 6 threshold: 0.91 is required to trigger empirical maintenance alert."""
        # Below 0.91 without vibration trigger -> Normal
        res_sub = InventoryOptimizer.evaluate_machine2_maintenance_coupling(
            failure_prob=0.905,
            vibration_mms=2.0,
            sku_spindle_stock=1.0,
            decision_threshold=0.91,
            synthetic_vibration_trigger=3.80
        )
        assert res_sub["maintenance_required"] is False
        assert res_sub["coupling_status"] == "NORMAL_OPERATION"

        # At or above 0.91 -> Triggers maintenance
        res_sup = InventoryOptimizer.evaluate_machine2_maintenance_coupling(
            failure_prob=0.910,
            vibration_mms=2.0,
            sku_spindle_stock=1.0,
            decision_threshold=0.91,
            synthetic_vibration_trigger=3.80
        )
        assert res_sup["maintenance_required"] is True
        assert res_sup["is_empirical_failure_predicted"] is True

    def test_configured_synthetic_vibration_trigger(self):
        """Configured vibration trigger (>= 3.8 mm/s) triggers maintenance regardless of model probability."""
        res = InventoryOptimizer.evaluate_machine2_maintenance_coupling(
            failure_prob=0.30,
            vibration_mms=3.85,
            sku_spindle_stock=1.0,
            decision_threshold=0.91,
            synthetic_vibration_trigger=3.80
        )
        assert res["maintenance_required"] is True
        assert res["is_synthetic_vibration_alert"] is True
        assert res["is_empirical_failure_predicted"] is False

    def test_constrained_maintenance_and_lead_time_reality(self):
        """
        When stock is 1.0, maintenance can proceed, but drops stock to 0.0.
        Because supplier lead time is 7 days, a constrained maintenance warning must be issued.
        Emergency PO must NOT claim to eliminate transit delay.
        """
        res = InventoryOptimizer.evaluate_machine2_maintenance_coupling(
            failure_prob=0.95,
            vibration_mms=4.0,
            sku_spindle_stock=1.0,
            lead_time_days=7.0
        )
        assert res["is_constrained_maintenance"] is True
        assert res["stock_post_maintenance"] == 0.0
        assert res["coupling_status"] == "MAINTENANCE_PERMITTED_ZERO_POST_BUFFER"
        assert "7" in res["status_message"]
        assert "Emergency procurement does NOT eliminate transit time" in res["lead_time_reality_caveat"]

    def test_depleted_stock_blocks_maintenance(self):
        """When bearing stock is 0.0, maintenance cannot be executed."""
        res = InventoryOptimizer.evaluate_machine2_maintenance_coupling(
            failure_prob=0.95,
            vibration_mms=4.0,
            sku_spindle_stock=0.0,
            lead_time_days=7.0
        )
        assert res["is_constrained_maintenance"] is True
        assert res["coupling_status"] == "CRITICAL_MAINTENANCE_BLOCKED"
        assert res["risk_level"] == "CRITICAL"


class TestDataIntegrityAndReproducibility:
    """Verifies dataset immutability, temporal ordering, and determinism."""

    def test_source_catalog_and_jobs_exist(self):
        """Confirms underlying data files exist and have expected columns."""
        catalog = load_inventory_catalog()
        assert "sku_id" in catalog.columns
        assert "current_stock" in catalog.columns
        assert "unit_cost" in catalog.columns
        assert len(catalog) >= 5

    def test_synthetic_demand_derivation_deterministic(self):
        """Repeated consumption derivation must yield identical daily totals."""
        df1 = derive_daily_sku_consumption()
        df2 = derive_daily_sku_consumption()

        pd.testing.assert_frame_equal(df1, df2)
        assert len(df1) > 0

    def test_service_layer_end_to_end(self):
        """Verifies InventoryService execution and schema compliance."""
        service = InventoryService()
        req = SkuAuditRequest(sku_id="SKU_STEEL_BAR_20MM")
        audit = service.audit_single_sku(req)

        assert audit.sku_id == "SKU_STEEL_BAR_20MM"
        assert audit.safety_stock > 0
        assert audit.reorder_point > audit.safety_stock
        assert audit.days_of_supply >= 0

        # Plant-wide summary
        summary = service.get_plant_inventory_summary()
        assert summary.total_skus_tracked >= 5
        assert summary.total_working_capital_tied_inr > 0

        # M2 coupling check
        m2_req = MachineMaintenanceCouplingRequest(
            machine_id="M2",
            failure_prob=0.93,
            vibration_mms=3.95
        )
        m2_res = service.evaluate_maintenance_coupling(m2_req)
        assert m2_res.maintenance_required is True
        assert m2_res.bearing_sku == "SKU_SPINDLE_BEARING_M2"
