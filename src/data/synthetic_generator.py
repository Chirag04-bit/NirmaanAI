"""
NirmaanAI Physics-Guided Synthetic Factory Dataset Generator
Simulates realistic, reproducible MSME factory operations, multi-machine lines,
sensor degradation, and the Machine 2 slowdown/bottleneck scenario.
"""

from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from src.data.schema import (
    FailureMode,
    FinancialParameters,
    FactoryHealthSnapshot,
    HealthState,
    InventoryItem,
    JobStatus,
    Machine,
    MachineStatus,
    MaintenanceRecord,
    OperationalLossRecord,
    ProductionJob,
    SensorReading,
)
from src.utils.config_loader import get_base_config, get_factory_defaults, get_project_root
from src.utils.logger import logger


class FactorySimulator:
    """
    Physics-guided factory simulator generating synchronized telemetry, job queues,
    maintenance logs, and financial losses for Indian manufacturing MSMEs.
    """

    def __init__(self, seed: int = 42, num_days: int = 30, sample_interval_min: int = 5):
        self.seed = seed
        self.num_days = num_days
        self.sample_interval_min = sample_interval_min
        self.rng = np.random.RandomState(seed)
        self.defaults = get_factory_defaults()
        self.fin_params = self.defaults.get("financial_assumptions", {})
        
        # Base financial rates
        self.downtime_rate_inr = float(self.fin_params.get("downtime_hourly_cost_inr", 4500.0))
        self.base_elec_rate = float(self.fin_params.get("base_electricity_rate_inr_per_kwh", 8.50))
        self.peak_elec_rate = float(self.fin_params.get("peak_electricity_rate_inr_per_kwh", 12.50))
        self.scrap_rate_inr = float(self.fin_params.get("scrap_cost_rate_inr_per_kg", 350.0))
        self.rework_rate_inr = float(self.fin_params.get("rework_cost_inr_per_hour", 280.0))

    def generate_machines(self) -> List[Machine]:
        """Instantiates the 5-machine shop-floor setup."""
        machines = [
            Machine(
                machine_id="M1",
                name="Precision CNC Turning Center M1",
                machine_type="CNC Lathe",
                line_id="LINE_01",
                design_cycle_time_sec=60.0,
                baseline_power_kw=15.0,
                baseline_vibration_mms=1.2,
                alert_vibration_mms=3.5,
                critical_vibration_mms=5.0,
                rated_capacity_units_per_hour=50.0,
                status=MachineStatus.OPERATIONAL,
                installation_year=2021
            ),
            Machine(
                machine_id="M2",
                name="Multi-Axis Vertical Milling Center M2",
                machine_type="VMC Milling",
                line_id="LINE_01",
                design_cycle_time_sec=45.0,
                baseline_power_kw=22.0,
                baseline_vibration_mms=1.4,
                alert_vibration_mms=3.8,
                critical_vibration_mms=5.5,
                rated_capacity_units_per_hour=70.0,
                status=MachineStatus.OPERATIONAL,
                installation_year=2020
            ),
            Machine(
                machine_id="M3",
                name="Automated Loom / Surface Grinder M3",
                machine_type="Grinder",
                line_id="LINE_01",
                design_cycle_time_sec=30.0,
                baseline_power_kw=11.0,
                baseline_vibration_mms=0.9,
                alert_vibration_mms=3.0,
                critical_vibration_mms=4.5,
                rated_capacity_units_per_hour=100.0,
                status=MachineStatus.OPERATIONAL,
                installation_year=2022
            ),
            Machine(
                machine_id="M4",
                name="Automated Optical Inspection Station M4",
                machine_type="Inspection Station",
                line_id="LINE_01",
                design_cycle_time_sec=20.0,
                baseline_power_kw=4.5,
                baseline_vibration_mms=0.4,
                alert_vibration_mms=1.5,
                critical_vibration_mms=2.5,
                rated_capacity_units_per_hour=150.0,
                status=MachineStatus.OPERATIONAL,
                installation_year=2023
            ),
            Machine(
                machine_id="M5",
                name="Assembly & Packaging Cell M5",
                machine_type="Assembly Station",
                line_id="LINE_01",
                design_cycle_time_sec=40.0,
                baseline_power_kw=7.5,
                baseline_vibration_mms=0.6,
                alert_vibration_mms=2.0,
                critical_vibration_mms=3.5,
                rated_capacity_units_per_hour=80.0,
                status=MachineStatus.OPERATIONAL,
                installation_year=2022
            )
        ]
        return machines

    def generate_sensor_telemetry(
        self,
        start_time: Optional[datetime] = None
    ) -> List[SensorReading]:
        """
        Generates multi-sensor time-series telemetry.
        Simulates the Machine 2 degradation episode during Day 18 to Day 21:
        vibration elevation past alert threshold (3.8 mm/s) reaching critical threshold (5.5 mm/s).
        """
        if start_time is None:
            start_time = datetime(2026, 1, 1, 6, 0, tzinfo=timezone.utc)

        machines = self.generate_machines()
        total_intervals = int((self.num_days * 24 * 60) / self.sample_interval_min)
        readings: List[SensorReading] = []

        # Tool wear accumulator per machine
        tool_wear = {m.machine_id: 0.0 for m in machines}
        reading_counter = 1

        for step in range(total_intervals):
            current_time = start_time + timedelta(minutes=step * self.sample_interval_min)
            day_fraction = (step * self.sample_interval_min) / (24 * 60)
            current_day = int(day_fraction) + 1
            hour_of_day = current_time.hour

            # Diurnal temperature cycle: coolest at 05:00, peak at 14:00
            ambient_temp = 22.0 + 8.0 * np.sin((hour_of_day - 8) * np.pi / 12) + self.rng.normal(0, 0.5)

            for m in machines:
                m_id = m.machine_id
                
                # Baseline characteristics
                base_vib = m.baseline_vibration_mms
                base_power = m.baseline_power_kw
                
                # Check for Machine 2 degradation episode: Days 18 to 21
                is_m2_degrading = (m_id == "M2" and 18 <= current_day <= 21)
                
                if is_m2_degrading:
                    # Degradation severity ramps up over the 4 days
                    progress = (day_fraction - 17.0) / 4.0  # 0.0 to 1.0
                    wear_factor = 2.5 * progress
                    vib_noise = self.rng.normal(0, 0.3)
                    # Vibration ramps from baseline 1.4 up to 5.6 mm/s
                    vibration = base_vib + (4.2 * progress) + vib_noise
                    vibration = max(base_vib, vibration)
                    
                    # Thermal buildup due to bearing friction
                    temp_process = ambient_temp + 20.0 + (18.0 * progress) + self.rng.normal(0, 0.8)
                    power_kw = base_power + (5.0 * progress) + self.rng.normal(0, 0.5)
                    sound_db = 74.0 + (12.0 * progress) + self.rng.normal(0, 1.0)
                    
                    # Faster tool wear accumulation during degradation
                    tool_wear[m_id] += (self.sample_interval_min * 1.8)
                    oil_level = max(20.0, 85.0 - (50.0 * progress))
                else:
                    # Normal stable operation with Gaussian noise
                    vib_noise = self.rng.normal(0, 0.15)
                    vibration = max(0.2, base_vib + vib_noise)
                    temp_process = ambient_temp + 15.0 + self.rng.normal(0, 0.6)
                    power_kw = max(1.0, base_power + self.rng.normal(0, 0.4))
                    sound_db = max(40.0, 72.0 + self.rng.normal(0, 1.2))
                    
                    # Normal tool wear accumulation
                    tool_wear[m_id] += self.sample_interval_min
                    # Periodic tool reset upon replacement (every 220 minutes)
                    if tool_wear[m_id] > 220.0 and m_id != "M2":
                        tool_wear[m_id] = self.rng.uniform(5.0, 15.0)
                    oil_level = max(60.0, 90.0 - (current_day * 0.8))

                rotational_rpm = 1500.0 + self.rng.normal(0, 15.0)
                torque_nm = (power_kw * 60000.0) / (2 * np.pi * rotational_rpm)

                reading = SensorReading(
                    reading_id=reading_counter,
                    machine_id=m_id,
                    timestamp=current_time,
                    vibration_mms=round(float(vibration), 3),
                    temperature_c=round(float(temp_process), 2),
                    ambient_temperature_c=round(float(ambient_temp), 2),
                    rotational_speed_rpm=round(float(rotational_rpm), 1),
                    torque_nm=round(float(torque_nm), 2),
                    sound_db=round(float(sound_db), 1),
                    power_consumption_kw=round(float(power_kw), 2),
                    oil_level_pct=round(float(oil_level), 1),
                    coolant_level_pct=round(float(max(40.0, 95.0 - current_day * 0.5)), 1),
                    tool_wear_min=round(float(tool_wear[m_id]), 1)
                )
                readings.append(reading)
                reading_counter += 1

        return readings

    def generate_production_jobs(
        self,
        num_jobs: int = 300,
        start_time: Optional[datetime] = None
    ) -> List[ProductionJob]:
        """
        Generates scheduled and executed production batches distributed across 30 days and 2 daily shifts.
        Simulates Machine 2 cycle time slowdown from 45.0s to 58-65s on Days 18-21.
        """
        if start_time is None:
            start_time = datetime(2026, 1, 1, 6, 0, tzinfo=timezone.utc)

        machines = self.generate_machines()
        machine_map = {m.machine_id: m for m in machines}
        jobs: List[ProductionJob] = []

        operations = {
            "M1": "Rough Turning & Profiling",
            "M2": "Precision VMC Pocket Milling",
            "M3": "Surface Grinding & Finishing",
            "M4": "Automated Vision Inspection",
            "M5": "Final Assembly & Packaging"
        }

        # 30 days, 2 shifts/day, 5 machines = 300 jobs
        job_counter = 1
        days_to_run = self.num_days
        shifts_per_day = 2

        for day in range(1, days_to_run + 1):
            for shift in range(shifts_per_day):
                shift_start = start_time + timedelta(days=day - 1, hours=shift * 8.0)
                
                for m in machines:
                    if job_counter > num_jobs:
                        break

                    m_id = m.machine_id
                    job_start = shift_start + timedelta(minutes=15)
                    batch_qty = int(self.rng.choice([50, 100, 150, 200]))
                    
                    nominal_sec = batch_qty * m.design_cycle_time_sec
                    scheduled_duration = timedelta(seconds=nominal_sec)
                    job_scheduled_end = job_start + scheduled_duration
                    
                    is_m2_degrading = (m_id == "M2" and 18 <= day <= 21)

                    if is_m2_degrading:
                        # Machine 2 cycle slowdown: 45s nominal -> 58s to 65s!
                        slowdown_factor = self.rng.uniform(1.30, 1.45)
                        actual_cycle_sec = m.design_cycle_time_sec * slowdown_factor
                        actual_duration = timedelta(seconds=batch_qty * actual_cycle_sec)
                        
                        # Start dispatch delay due to queue buildup
                        start_delay = timedelta(minutes=self.rng.uniform(12.0, 28.0))
                        actual_start = job_start + start_delay
                        actual_end = actual_start + actual_duration
                        
                        # Increased scrap on degrading milling cutter
                        scrap = int(self.rng.binomial(batch_qty, 0.08))
                        completed = batch_qty - scrap
                        status = JobStatus.DELAYED
                    else:
                        # Normal minor variance
                        variance_factor = self.rng.uniform(0.98, 1.04)
                        actual_cycle_sec = m.design_cycle_time_sec * variance_factor
                        actual_duration = timedelta(seconds=batch_qty * actual_cycle_sec)
                        
                        # Minor start variance (-2 to +3 minutes)
                        start_delay = timedelta(minutes=self.rng.uniform(-2.0, 3.0))
                        actual_start = max(start_time, job_start + start_delay)
                        actual_end = actual_start + actual_duration
                        
                        # Low nominal scrap (1-2%)
                        scrap = int(self.rng.binomial(batch_qty, 0.015))
                        completed = batch_qty - scrap
                        status = JobStatus.COMPLETED

                    job = ProductionJob(
                        job_id=f"JOB_{job_counter:04d}",
                        machine_id=m_id,
                        operation_type=operations[m_id],
                        scheduled_start=job_start,
                        scheduled_end=job_scheduled_end,
                        actual_start=actual_start,
                        actual_end=actual_end,
                        batch_quantity=batch_qty,
                        completed_quantity=completed,
                        scrap_quantity=scrap,
                        actual_cycle_time_sec=round(float(actual_cycle_sec), 2),
                        status=status
                    )
                    jobs.append(job)
                    job_counter += 1

        return jobs

    def generate_maintenance_records(
        self,
        start_time: Optional[datetime] = None
    ) -> List[MaintenanceRecord]:
        """
        Generates scheduled preventive and unplanned maintenance logs.
        Includes the critical Machine 2 emergency stoppage event on Day 21.
        """
        if start_time is None:
            start_time = datetime(2026, 1, 1, 6, 0, tzinfo=timezone.utc)

        records = [
            # Regular preventive servicing
            MaintenanceRecord(
                record_id="MAINT_0001",
                machine_id="M1",
                timestamp=start_time + timedelta(days=7, hours=6),
                event_type="PREVENTIVE",
                failure_mode=FailureMode.NONE,
                downtime_minutes=45.0,
                technician_id="TECH_SURESH",
                corrective_action="Routine lubrication and chuck alignment inspection",
                notes="M1 turning center operating within normal tolerances."
            ),
            MaintenanceRecord(
                record_id="MAINT_0002",
                machine_id="M3",
                timestamp=start_time + timedelta(days=14, hours=14),
                event_type="TOOL_CHANGE",
                failure_mode=FailureMode.TWF,
                downtime_minutes=30.0,
                technician_id="TECH_RAHUL",
                corrective_action="Dressed grinding wheel and replenished coolant filter",
                notes="Grinding wheel replaced after reaching maximum wear threshold."
            ),
            # THE MACHINE 2 EMERGENCY BREAKDOWN (Day 21)
            MaintenanceRecord(
                record_id="MAINT_0003",
                machine_id="M2",
                timestamp=start_time + timedelta(days=21, hours=10, minutes=30),
                event_type="UNPLANNED_STOP",
                failure_mode=FailureMode.BEARING_WEAR,
                downtime_minutes=150.0,  # Exactly 2.5 hours
                technician_id="TECH_KUNTAL_SR",
                corrective_action="Replaced degraded spindle drive bearing and flushed thermal coolant jacket",
                notes="Vibration reached 5.6 mm/s causing emergency halt. Spindle bearing severely worn due to lubrication starvation."
            ),
            MaintenanceRecord(
                record_id="MAINT_0004",
                machine_id="M4",
                timestamp=start_time + timedelta(days=25, hours=8),
                event_type="PREVENTIVE",
                failure_mode=FailureMode.NONE,
                downtime_minutes=25.0,
                technician_id="TECH_AMIT",
                corrective_action="Optical camera lens cleaning and lighting calibration",
                notes="Routine vision inspection check passed."
            )
        ]
        return records

    def generate_inventory_items(self) -> List[InventoryItem]:
        """Generates raw material and component inventory status."""
        items = [
            InventoryItem(
                item_id="SKU_STEEL_BAR_20MM",
                item_name="AISI 4140 Alloy Steel Round Bar 20mm",
                category="RAW_MATERIAL",
                current_stock=450.0,
                safety_stock=150.0,
                unit_cost_inr=95.0,
                reorder_quantity=500.0,
                unit_of_measure="kg"
            ),
            InventoryItem(
                item_id="SKU_ALUM_BILLET_6061",
                item_name="Aluminium 6061 Billet 100x100mm",
                category="RAW_MATERIAL",
                current_stock=220.0,
                safety_stock=80.0,
                unit_cost_inr=240.0,
                reorder_quantity=300.0,
                unit_of_measure="kg"
            ),
            InventoryItem(
                item_id="SKU_SPINDLE_BEARING_M2",
                item_name="Precision Angular Contact Spindle Bearing (M2)",
                category="SPARE_PART",
                current_stock=2.0,
                safety_stock=3.0,  # STOCKOUT RISK!
                unit_cost_inr=3200.0,
                reorder_quantity=5.0,
                unit_of_measure="units"
            ),
            InventoryItem(
                item_id="SKU_ENDMILL_CARBIDE_10MM",
                item_name="Solid Carbide 4-Flute End Mill 10mm",
                category="SPARE_PART",
                current_stock=12.0,
                safety_stock=5.0,
                unit_cost_inr=1450.0,
                reorder_quantity=10.0,
                unit_of_measure="units"
            ),
            InventoryItem(
                item_id="SKU_YARN_COTTON_30S",
                item_name="Carded Cotton Yarn 30s Count (Textile Loom)",
                category="RAW_MATERIAL",
                current_stock=1200.0,
                safety_stock=400.0,
                unit_cost_inr=280.0,
                reorder_quantity=1000.0,
                unit_of_measure="kg"
            )
        ]
        return items

    def calculate_operational_losses(
        self,
        jobs: List[ProductionJob],
        maint_records: List[MaintenanceRecord]
    ) -> List[OperationalLossRecord]:
        """
        Computes disaggregated rupee financial losses across machines and events
        using configured MSME assumptions (Downtime ₹4500/hr, Scrap ₹350/kg, Rework ₹280/hr).
        """
        losses: List[OperationalLossRecord] = []
        loss_counter = 1

        # Calculate loss per maintenance stoppage
        for m in maint_records:
            dt_hours = m.downtime_minutes / 60.0
            dt_loss = dt_hours * self.downtime_rate_inr
            
            # Unplanned stops have secondary technician rework hours
            rework_h = 1.5 if m.event_type == "UNPLANNED_STOP" else 0.0
            rework_loss = rework_h * self.rework_rate_inr
            
            total_loss = dt_loss + rework_loss

            record = OperationalLossRecord(
                loss_id=loss_counter,
                machine_id=m.machine_id,
                timestamp=m.timestamp,
                downtime_minutes=m.downtime_minutes,
                downtime_loss_inr=round(dt_loss, 2),
                energy_wastage_kwh=0.0,
                energy_loss_inr=0.0,
                scrap_quantity=0,
                scrap_loss_inr=0.0,
                rework_hours=rework_h,
                rework_loss_inr=round(rework_loss, 2),
                total_financial_loss_inr=round(total_loss, 2)
            )
            losses.append(record)
            loss_counter += 1

        # Calculate scrap losses from production jobs
        for j in jobs:
            if j.scrap_quantity > 0:
                # Assume 0.8 kg metal/yarn per unit
                scrap_weight_kg = j.scrap_quantity * 0.8
                scrap_loss = scrap_weight_kg * self.scrap_rate_inr
                
                # Rework on 50% of scrapped units (0.25 hours/unit)
                rework_h = (j.scrap_quantity * 0.5) * 0.25
                rework_loss = rework_h * self.rework_rate_inr
                
                # If delayed past peak hours (18:00 to 22:00), calculate peak surcharge
                peak_energy_loss = 0.0
                if j.status == JobStatus.DELAYED and j.actual_end:
                    if 18 <= j.actual_end.hour <= 22:
                        # Extra peak surcharge: 22 kW * (12.50 - 8.50) * 1.5 hrs = ₹132
                        peak_energy_loss = 22.0 * (self.peak_elec_rate - self.base_elec_rate) * 1.5

                total_loss = scrap_loss + rework_loss + peak_energy_loss

                record = OperationalLossRecord(
                    loss_id=loss_counter,
                    machine_id=j.machine_id,
                    timestamp=j.actual_end or j.scheduled_end,
                    downtime_minutes=0.0,
                    downtime_loss_inr=0.0,
                    energy_wastage_kwh=round(22.0 * 1.5, 2) if peak_energy_loss > 0 else 0.0,
                    energy_loss_inr=round(peak_energy_loss, 2),
                    scrap_quantity=j.scrap_quantity,
                    scrap_loss_inr=round(scrap_loss, 2),
                    rework_hours=round(rework_h, 2),
                    rework_loss_inr=round(rework_loss, 2),
                    total_financial_loss_inr=round(total_loss, 2)
                )
                losses.append(record)
                loss_counter += 1

        return losses

    def reset_rng(self) -> None:
        """Resets random number generator to configured seed for deterministic reproducibility."""
        self.rng = np.random.RandomState(self.seed)

    def export_all(self, target_dir: str) -> Dict[str, str]:
        """
        Executes complete simulation and serializes datasets into CSV and Parquet files.
        """
        self.reset_rng()
        os.makedirs(target_dir, exist_ok=True)
        logger.info(f"Starting factory simulation export into {target_dir} (Seed={self.seed})...")

        # 1. Machines
        machines = self.generate_machines()
        df_machines = pd.DataFrame([m.model_dump() for m in machines])
        machines_path = os.path.join(target_dir, "machines.csv")
        df_machines.to_csv(machines_path, index=False)

        # 2. Sensor Telemetry
        telemetry = self.generate_sensor_telemetry()
        df_telemetry = pd.DataFrame([t.model_dump() for t in telemetry])
        telemetry_csv = os.path.join(target_dir, "sensor_readings.csv")
        telemetry_parquet = os.path.join(target_dir, "sensor_readings.parquet")
        df_telemetry.to_csv(telemetry_csv, index=False)
        df_telemetry.to_parquet(telemetry_parquet, index=False)

        # 3. Production Jobs
        jobs = self.generate_production_jobs()
        df_jobs = pd.DataFrame([j.model_dump() for j in jobs])
        jobs_path = os.path.join(target_dir, "production_jobs.csv")
        df_jobs.to_csv(jobs_path, index=False)

        # 4. Maintenance Records
        maintenance = self.generate_maintenance_records()
        df_maint = pd.DataFrame([m.model_dump() for m in maintenance])
        maint_path = os.path.join(target_dir, "maintenance_records.csv")
        df_maint.to_csv(maint_path, index=False)

        # 5. Inventory Items
        inventory = self.generate_inventory_items()
        df_inv = pd.DataFrame([i.model_dump() for i in inventory])
        inv_path = os.path.join(target_dir, "inventory_items.csv")
        df_inv.to_csv(inv_path, index=False)

        # 6. Operational Losses
        losses = self.calculate_operational_losses(jobs, maintenance)
        df_losses = pd.DataFrame([l.model_dump() for l in losses])
        losses_path = os.path.join(target_dir, "operational_losses.csv")
        df_losses.to_csv(losses_path, index=False)

        logger.info(
            f"Simulation export complete: {len(machines)} machines, "
            f"{len(telemetry)} telemetry records, {len(jobs)} jobs, "
            f"{len(maintenance)} maintenance records, {len(inventory)} inventory items, "
            f"{len(losses)} loss records."
        )

        return {
            "machines": machines_path,
            "sensor_readings_csv": telemetry_csv,
            "sensor_readings_parquet": telemetry_parquet,
            "production_jobs": jobs_path,
            "maintenance_records": maint_path,
            "inventory_items": inv_path,
            "operational_losses": losses_path
        }


class TextileLoomSimulator(FactorySimulator):
    """
    Textile Weaving & Spinning MSME simulator.
    Simulates spinning spindle vibration surges, ring frame bearing wear,
    yarn breakages, weaving loom bottlenecks, and rupee financial losses.
    """

    def __init__(self, seed: int = 101, num_days: int = 30, sample_interval_min: int = 5):
        super().__init__(seed=seed, num_days=num_days, sample_interval_min=sample_interval_min)
        # Textile specific financial assumptions
        self.downtime_rate_inr = 3800.0   # ₹3,800/hr for weaving shed downtime
        self.scrap_rate_inr = 280.0       # ₹280/kg for cotton yarn waste
        self.rework_rate_inr = 220.0      # ₹220/hr for mending/splicing

    def generate_machines(self) -> List[Machine]:
        """Instantiates the 5-machine textile manufacturing sequence."""
        return [
            Machine(
                machine_id="TX01",
                name="High-Production Carding Machine TX01",
                machine_type="Carding Engine",
                line_id="TX_LINE_01",
                design_cycle_time_sec=35.0,
                baseline_power_kw=18.0,
                baseline_vibration_mms=1.1,
                alert_vibration_mms=3.2,
                critical_vibration_mms=4.8,
                rated_capacity_units_per_hour=90.0,
                status=MachineStatus.OPERATIONAL,
                installation_year=2021
            ),
            Machine(
                machine_id="TX02",
                name="Ring Spinning Frame TX02 (1000 Spindles)",
                machine_type="Ring Spinning Frame",
                line_id="TX_LINE_01",
                design_cycle_time_sec=40.0,
                baseline_power_kw=28.0,
                baseline_vibration_mms=1.3,
                alert_vibration_mms=3.6,
                critical_vibration_mms=5.2,
                rated_capacity_units_per_hour=85.0,
                status=MachineStatus.OPERATIONAL,
                installation_year=2020
            ),
            Machine(
                machine_id="TX03",
                name="High-Speed Sectional Warper TX03",
                machine_type="Sectional Warping Frame",
                line_id="TX_LINE_01",
                design_cycle_time_sec=25.0,
                baseline_power_kw=14.0,
                baseline_vibration_mms=0.8,
                alert_vibration_mms=2.8,
                critical_vibration_mms=4.2,
                rated_capacity_units_per_hour=120.0,
                status=MachineStatus.OPERATIONAL,
                installation_year=2022
            ),
            Machine(
                machine_id="TX04",
                name="High-Speed Electronic Rapier Loom TX04",
                machine_type="Rapier Weaving Loom",
                line_id="TX_LINE_01",
                design_cycle_time_sec=50.0,
                baseline_power_kw=9.5,
                baseline_vibration_mms=1.7,
                alert_vibration_mms=3.9,
                critical_vibration_mms=5.5,
                rated_capacity_units_per_hour=65.0,
                status=MachineStatus.OPERATIONAL,
                installation_year=2022
            ),
            Machine(
                machine_id="TX05",
                name="Automatic Fabric Inspection & Folding TX05",
                machine_type="Inspection Range",
                line_id="TX_LINE_01",
                design_cycle_time_sec=20.0,
                baseline_power_kw=6.0,
                baseline_vibration_mms=0.5,
                alert_vibration_mms=2.2,
                critical_vibration_mms=3.5,
                rated_capacity_units_per_hour=150.0,
                status=MachineStatus.OPERATIONAL,
                installation_year=2023
            )
        ]

    def generate_sensor_telemetry(
        self,
        start_time: Optional[datetime] = None
    ) -> List[SensorReading]:
        """
        Generates textile sensor telemetry.
        Simulates Ring Spinning Frame TX02 spindle bearing failure on Days 16-19:
        vibration climbs past 5.0 mm/s, temperature rises due to lint friction.
        """
        if start_time is None:
            start_time = datetime(2026, 1, 1, 6, 0, tzinfo=timezone.utc)

        machines = self.generate_machines()
        total_intervals = int((self.num_days * 24 * 60) / self.sample_interval_min)
        readings: List[SensorReading] = []
        reading_counter = 1

        for step in range(total_intervals):
            current_time = start_time + timedelta(minutes=step * self.sample_interval_min)
            day_fraction = (step * self.sample_interval_min) / (24 * 60)
            current_day = int(day_fraction) + 1
            hour_of_day = current_time.hour

            ambient_temp = 24.0 + 7.0 * np.sin((hour_of_day - 8) * np.pi / 12) + self.rng.normal(0, 0.4)

            for m in machines:
                m_id = m.machine_id
                base_vib = m.baseline_vibration_mms
                base_power = m.baseline_power_kw

                # TX02 degradation on Days 16 to 19
                is_tx2_degrading = (m_id == "TX02" and 16 <= current_day <= 19)

                if is_tx2_degrading:
                    progress = (day_fraction - 15.0) / 4.0
                    vibration = base_vib + (3.9 * progress) + self.rng.normal(0, 0.25)
                    vibration = max(base_vib, vibration)
                    temp_process = ambient_temp + 22.0 + (16.0 * progress) + self.rng.normal(0, 0.7)
                    power_kw = base_power + (6.0 * progress) + self.rng.normal(0, 0.4)
                    sound_db = 78.0 + (10.0 * progress) + self.rng.normal(0, 0.9)
                    spindle_rpm = max(9000.0, 14500.0 - (3500.0 * progress) + self.rng.normal(0, 50.0))
                    oil_level = max(25.0, 80.0 - (45.0 * progress))
                else:
                    vibration = max(0.2, base_vib + self.rng.normal(0, 0.12))
                    temp_process = ambient_temp + 14.0 + self.rng.normal(0, 0.5)
                    power_kw = max(1.0, base_power + self.rng.normal(0, 0.3))
                    sound_db = max(45.0, 75.0 + self.rng.normal(0, 1.0))
                    spindle_rpm = 14500.0 + self.rng.normal(0, 30.0) if m_id == "TX02" else 850.0 + self.rng.normal(0, 10.0)
                    oil_level = max(65.0, 92.0 - (current_day * 0.7))

                torque_nm = (power_kw * 60000.0) / (2 * np.pi * max(100.0, spindle_rpm))

                reading = SensorReading(
                    reading_id=reading_counter,
                    machine_id=m_id,
                    timestamp=current_time,
                    vibration_mms=round(float(vibration), 3),
                    temperature_c=round(float(temp_process), 2),
                    ambient_temperature_c=round(float(ambient_temp), 2),
                    rotational_speed_rpm=round(float(spindle_rpm), 1),
                    torque_nm=round(float(torque_nm), 2),
                    sound_db=round(float(sound_db), 1),
                    power_consumption_kw=round(float(power_kw), 2),
                    oil_level_pct=round(float(oil_level), 1),
                    coolant_level_pct=round(float(max(50.0, 90.0 - current_day * 0.4)), 1),
                    tool_wear_min=round(float(step * 0.2 % 300.0), 1)
                )
                readings.append(reading)
                reading_counter += 1

        return readings

    def generate_production_jobs(
        self,
        num_jobs: int = 300,
        start_time: Optional[datetime] = None
    ) -> List[ProductionJob]:
        """Generates textile production job schedule across carding, spinning, warping, and weaving distributed across 30 days."""
        if start_time is None:
            start_time = datetime(2026, 1, 1, 6, 0, tzinfo=timezone.utc)

        machines = self.generate_machines()
        jobs: List[ProductionJob] = []

        operations = {
            "TX01": "Cotton Sliver Carding & Combing",
            "TX02": "Ring Spinning 30s Carded Yarn",
            "TX03": "High-Speed Sectional Warp Beam Sizing",
            "TX04": "Rapier Grey Fabric Weaving (100% Cotton)",
            "TX05": "Fabric Inspection, Calendering & Packaging"
        }

        job_counter = 1
        days_to_run = self.num_days
        shifts_per_day = 2

        for day in range(1, days_to_run + 1):
            for shift in range(shifts_per_day):
                shift_start = start_time + timedelta(days=day - 1, hours=shift * 8.0)

                for m in machines:
                    if job_counter > num_jobs:
                        break

                    m_id = m.machine_id
                    job_start = shift_start + timedelta(minutes=15)
                    batch_qty = int(self.rng.choice([100, 200, 300, 500]))
                    
                    nominal_sec = batch_qty * m.design_cycle_time_sec
                    job_scheduled_end = job_start + timedelta(seconds=nominal_sec)
                    is_tx2_degrading = (m_id == "TX02" and 16 <= day <= 19)

                    if is_tx2_degrading:
                        # Ring spinning slowdown: 40s nominal -> 55s
                        slowdown_factor = self.rng.uniform(1.30, 1.48)
                        actual_cycle_sec = m.design_cycle_time_sec * slowdown_factor
                        actual_duration = timedelta(seconds=batch_qty * actual_cycle_sec)
                        start_delay = timedelta(minutes=self.rng.uniform(15.0, 32.0))
                        actual_start = job_start + start_delay
                        actual_end = actual_start + actual_duration
                        # High yarn breakage scrap
                        scrap = int(self.rng.binomial(batch_qty, 0.09))
                        completed = batch_qty - scrap
                        status = JobStatus.DELAYED
                    else:
                        variance_factor = self.rng.uniform(0.98, 1.03)
                        actual_cycle_sec = m.design_cycle_time_sec * variance_factor
                        actual_duration = timedelta(seconds=batch_qty * actual_cycle_sec)
                        start_delay = timedelta(minutes=self.rng.uniform(-1.0, 3.0))
                        actual_start = max(start_time, job_start + start_delay)
                        actual_end = actual_start + actual_duration
                        scrap = int(self.rng.binomial(batch_qty, 0.012))
                        completed = batch_qty - scrap
                        status = JobStatus.COMPLETED

                    job = ProductionJob(
                        job_id=f"TX_JOB_{job_counter:04d}",
                        machine_id=m_id,
                        operation_type=operations[m_id],
                        scheduled_start=job_start,
                        scheduled_end=job_scheduled_end,
                        actual_start=actual_start,
                        actual_end=actual_end,
                        batch_quantity=batch_qty,
                        completed_quantity=completed,
                        scrap_quantity=scrap,
                        actual_cycle_time_sec=round(float(actual_cycle_sec), 2),
                        status=status
                    )
                    jobs.append(job)
                    job_counter += 1

        return jobs

    def generate_maintenance_records(
        self,
        start_time: Optional[datetime] = None
    ) -> List[MaintenanceRecord]:
        """Generates textile maintenance logs including the TX02 emergency spindle replacement."""
        if start_time is None:
            start_time = datetime(2026, 1, 1, 6, 0, tzinfo=timezone.utc)

        return [
            MaintenanceRecord(
                record_id="TX_MAINT_0001",
                machine_id="TX01",
                timestamp=start_time + timedelta(days=6, hours=8),
                event_type="PREVENTIVE",
                failure_mode=FailureMode.NONE,
                downtime_minutes=40.0,
                technician_id="TECH_RAMESH",
                corrective_action="Cleaned carding cylinder clothing and emptied waste fly collection box",
                notes="Carding machine sliver quality normal."
            ),
            MaintenanceRecord(
                record_id="TX_MAINT_0002",
                machine_id="TX02",
                timestamp=start_time + timedelta(days=19, hours=11),
                event_type="UNPLANNED_STOP",
                failure_mode=FailureMode.BEARING_WEAR,
                downtime_minutes=120.0,  # 2.0 hours
                technician_id="TECH_KUNTAL_SR",
                corrective_action="Replaced seized ring frame spindle bolster bearings and blown drive belt",
                notes="Vibration surged to 5.4 mm/s causing multiple end breaks and thermal trip on main motor."
            ),
            MaintenanceRecord(
                record_id="TX_MAINT_0003",
                machine_id="TX04",
                timestamp=start_time + timedelta(days=24, hours=14),
                event_type="PREVENTIVE",
                failure_mode=FailureMode.NONE,
                downtime_minutes=35.0,
                technician_id="TECH_DEV",
                corrective_action="Inspected rapier drive gearbox and adjusted warp tension load cell",
                notes="Loom reed and rapier head in sound operational condition."
            )
        ]

    def generate_inventory_items(self) -> List[InventoryItem]:
        """Generates textile raw material and spare parts inventory."""
        return [
            InventoryItem(
                item_id="TX_SKU_RAW_COTTON_SHANKAR6",
                item_name="Raw Cotton Bales (Shankar-6 Variety, 29mm staple)",
                category="RAW_MATERIAL",
                current_stock=2400.0,
                safety_stock=800.0,
                unit_cost_inr=165.0,
                reorder_quantity=2000.0,
                unit_of_measure="kg"
            ),
            InventoryItem(
                item_id="TX_SKU_RING_SPINDLE_BOLSTER",
                item_name="Precision Spindle Bolster Assembly (TX02)",
                category="SPARE_PART",
                current_stock=1.0,
                safety_stock=4.0,  # CRITICAL SHORTAGE
                unit_cost_inr=1850.0,
                reorder_quantity=10.0,
                unit_of_measure="units"
            ),
            InventoryItem(
                item_id="TX_SKU_RAPIER_TAPE_CARBON",
                item_name="Carbon Composite Flexible Rapier Tape (TX04)",
                category="SPARE_PART",
                current_stock=3.0,
                safety_stock=2.0,
                unit_cost_inr=5400.0,
                reorder_quantity=4.0,
                unit_of_measure="units"
            ),
            InventoryItem(
                item_id="TX_SKU_SIZING_STARCH",
                item_name="Modified Maize Sizing Starch for Warping",
                category="RAW_MATERIAL",
                current_stock=650.0,
                safety_stock=250.0,
                unit_cost_inr=45.0,
                reorder_quantity=500.0,
                unit_of_measure="kg"
            )
        ]


def generate_all_synthetic_datasets(base_output_dir: Optional[str] = None) -> Dict[str, Dict[str, str]]:
    """
    Master generation script: builds both Discrete Precision Auto-Components
    and Textile MSME Shop Floor datasets and serializes them into DATASET/ and data/.
    """
    root = get_project_root()
    if base_output_dir is None:
        base_output_dir = str(root)

    # 1. Discrete Precision Auto-Components Digital Twin (Dataset 10)
    auto_sim = FactorySimulator(seed=42, num_days=30, sample_interval_min=5)
    auto_paths_dataset = auto_sim.export_all(os.path.join(base_output_dir, "DATASET", "10_SYNTHETIC_FACTORY", "synthetic"))
    auto_paths_data = auto_sim.export_all(os.path.join(base_output_dir, "data", "synthetic", "auto_components"))

    # 2. Textile MSME Shop Floor Digital Twin (Dataset 09)
    textile_sim = TextileLoomSimulator(seed=101, num_days=30, sample_interval_min=5)
    textile_paths_dataset = textile_sim.export_all(os.path.join(base_output_dir, "DATASET", "09_TEXTILE_MANUFACTURING", "synthetic"))
    textile_paths_data = textile_sim.export_all(os.path.join(base_output_dir, "data", "synthetic", "textile"))

    return {
        "auto_components_dataset": auto_paths_dataset,
        "auto_components_data": auto_paths_data,
        "textile_dataset": textile_paths_dataset,
        "textile_data": textile_paths_data
    }


if __name__ == "__main__":
    generate_all_synthetic_datasets()

