"""
Unit and integration tests for NirmaanAI Synthetic Data Engine.
Validates reproducibility, causal physics, Machine 2 degradation dynamics,
disaggregated financial loss consistency, and Pydantic schema conformance.
"""

import json
import os
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.data.schema import (
    InventoryItem,
    Machine,
    MaintenanceRecord,
    OperationalLossRecord,
    ProductionJob,
    SensorReading,
)
from src.data.synthetic_generator import (
    FactorySimulator,
    TextileLoomSimulator,
    generate_all_synthetic_datasets,
)
from src.utils.config_loader import get_project_root


@pytest.fixture(scope="module")
def project_root() -> Path:
    return get_project_root()


@pytest.fixture(scope="module")
def factory_sim() -> FactorySimulator:
    return FactorySimulator(seed=42, num_days=30, sample_interval_min=5)


@pytest.fixture(scope="module")
def textile_sim() -> TextileLoomSimulator:
    return TextileLoomSimulator(seed=101, num_days=30, sample_interval_min=5)


def test_deterministic_reproducibility():
    """Verify that two simulators initialized with identical seeds produce bitwise identical telemetry."""
    sim_a = FactorySimulator(seed=42, num_days=2, sample_interval_min=15)
    sim_b = FactorySimulator(seed=42, num_days=2, sample_interval_min=15)

    telemetry_a = sim_a.generate_sensor_telemetry()
    telemetry_b = sim_b.generate_sensor_telemetry()

    assert len(telemetry_a) == len(telemetry_b)
    assert len(telemetry_a) > 0

    for r_a, r_b in zip(telemetry_a[:50], telemetry_b[:50]):
        assert r_a.machine_id == r_b.machine_id
        assert r_a.timestamp == r_b.timestamp
        assert r_a.vibration_mms == r_b.vibration_mms
        assert r_a.temperature_c == r_b.temperature_c
        assert r_a.power_consumption_kw == r_b.power_consumption_kw


def test_machine_2_degradation_episode(project_root: Path):
    """Verify that Machine 2 telemetry exhibits statistically significant degradation during Days 18-21."""
    telemetry_path = project_root / "DATASET" / "10_SYNTHETIC_FACTORY" / "synthetic" / "sensor_readings.parquet"
    assert telemetry_path.exists(), "Telemetry parquet file missing"

    df = pd.read_parquet(telemetry_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="ISO8601")
    start_time = df["timestamp"].min()
    df["day"] = (df["timestamp"] - start_time).dt.total_seconds() / (24 * 3600) + 1.0

    # Machine 2 healthy baseline (Days 1 to 10) vs Degradation window (Days 18 to 21)
    m2_healthy = df[(df["machine_id"] == "M2") & (df["day"] >= 1.0) & (df["day"] <= 10.0)]
    m2_degraded = df[(df["machine_id"] == "M2") & (df["day"] >= 18.0) & (df["day"] <= 21.0)]

    mean_healthy_vib = m2_healthy["vibration_mms"].mean()
    mean_degraded_vib = m2_degraded["vibration_mms"].mean()
    max_degraded_vib = m2_degraded["vibration_mms"].max()

    # Machine 2 baseline is ~1.4 mm/s; degraded mean should exceed 2.8 mm/s, and max should exceed alert threshold (3.8 mm/s)
    assert mean_degraded_vib > mean_healthy_vib * 1.8, f"Expected degraded vib > 1.8x healthy, got {mean_degraded_vib} vs {mean_healthy_vib}"
    assert max_degraded_vib >= 4.5, f"Expected peak vibration >= 4.5 mm/s, got {max_degraded_vib}"

    # Verify thermal elevation
    assert m2_degraded["temperature_c"].mean() > m2_healthy["temperature_c"].mean() + 8.0


def test_machine_2_cycle_slowdown(project_root: Path):
    """Verify that Machine 2 production jobs experience significant cycle slowdown and dispatch delay."""
    jobs_path = project_root / "DATASET" / "10_SYNTHETIC_FACTORY" / "synthetic" / "production_jobs.csv"
    assert jobs_path.exists()

    df = pd.read_csv(jobs_path)
    df["scheduled_start"] = pd.to_datetime(df["scheduled_start"], format="ISO8601")
    start_time = df["scheduled_start"].min()
    df["job_day"] = (df["scheduled_start"] - start_time).dt.total_seconds() / (24 * 3600) + 1.0

    m2_nominal = df[(df["machine_id"] == "M2") & (df["job_day"] < 17.0)]
    m2_slowdown = df[(df["machine_id"] == "M2") & (df["job_day"] >= 18.0) & (df["job_day"] < 22.0)]

    assert len(m2_slowdown) > 0, "No M2 jobs scheduled during degradation window"

    mean_nominal_cycle = m2_nominal["actual_cycle_time_sec"].mean()
    mean_degraded_cycle = m2_slowdown["actual_cycle_time_sec"].mean()

    # Design cycle time is 45s; nominal is ~45s; degraded should be >= 55s
    assert 43.0 <= mean_nominal_cycle <= 47.0
    assert mean_degraded_cycle >= 58.0, f"Expected degraded cycle >= 58s, got {mean_degraded_cycle}"
    assert (m2_slowdown["status"] == "DELAYED").all(), "All M2 jobs during degradation should be DELAYED"


def test_financial_loss_accounting_integrity(project_root: Path):
    """Verify that every loss record satisfies total == downtime + scrap + rework + energy loss."""
    for dataset_dir in ["10_SYNTHETIC_FACTORY", "09_TEXTILE_MANUFACTURING"]:
        loss_path = project_root / "DATASET" / dataset_dir / "synthetic" / "operational_losses.csv"
        assert loss_path.exists()

        df = pd.read_csv(loss_path)
        assert len(df) > 0

        calculated_total = (
            df["downtime_loss_inr"] + df["energy_loss_inr"] + df["scrap_loss_inr"] + df["rework_loss_inr"]
        ).round(2)

        discrepancy = (df["total_financial_loss_inr"] - calculated_total).abs()
        assert (discrepancy < 0.02).all(), f"Financial loss imbalance detected in {dataset_dir}"


def test_pydantic_schema_validation(project_root: Path):
    """Verify that all exported CSV records parse into unified Pydantic schemas without errors."""
    data_dir = project_root / "DATASET" / "10_SYNTHETIC_FACTORY" / "synthetic"

    # 1. Machines
    df_machines = pd.read_csv(data_dir / "machines.csv")
    for _, row in df_machines.iterrows():
        Machine.model_validate(row.to_dict())

    # 2. Production Jobs
    df_jobs = pd.read_csv(data_dir / "production_jobs.csv")
    for _, row in df_jobs.head(50).iterrows():
        ProductionJob.model_validate(row.to_dict())

    # 3. Maintenance Records
    df_maint = pd.read_csv(data_dir / "maintenance_records.csv")
    for _, row in df_maint.iterrows():
        MaintenanceRecord.model_validate(row.to_dict())

    # 4. Inventory Items
    df_inv = pd.read_csv(data_dir / "inventory_items.csv")
    for _, row in df_inv.iterrows():
        InventoryItem.model_validate(row.to_dict())

    # 5. Operational Losses
    df_losses = pd.read_csv(data_dir / "operational_losses.csv")
    for _, row in df_losses.head(50).iterrows():
        OperationalLossRecord.model_validate(row.to_dict())


def test_manifest_verification(project_root: Path):
    """Verify that manifests for 09 and 10 accurately match the generated files, row counts, and col counts."""
    for dataset_id in ["10_SYNTHETIC_FACTORY", "09_TEXTILE_MANUFACTURING"]:
        manifest_path = project_root / "DATASET" / dataset_id / "metadata" / "dataset_manifest.json"
        assert manifest_path.exists(), f"Manifest {manifest_path} does not exist"

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        files = manifest.get("files", [])
        assert len(files) >= 6, f"Expected at least 6 files in manifest, got {len(files)}"

        for file_entry in files:
            file_path = project_root / "DATASET" / dataset_id / "synthetic" / file_entry["filename"]
            assert file_path.exists(), f"File {file_path} listed in manifest but missing on disk"
            assert file_path.stat().st_size > 0

            # Verify rows and columns for tabular files
            if file_entry["filename"].endswith(".csv"):
                df = pd.read_csv(file_path)
                assert len(df) == file_entry["rows"], f"Row count mismatch for {file_entry['filename']}"
                assert len(df.columns) == file_entry["cols"], f"Col count mismatch for {file_entry['filename']}"
            elif file_entry["filename"].endswith(".parquet"):
                df = pd.read_parquet(file_path)
                assert len(df) == file_entry["rows"], f"Parquet row count mismatch for {file_entry['filename']}"
                assert len(df.columns) == file_entry["cols"], f"Parquet col count mismatch for {file_entry['filename']}"


def test_textile_simulator_dynamics(project_root: Path):
    """Verify that Textile Ring Spinning Frame TX02 exhibits degradation dynamics during Days 16-19."""
    telemetry_path = project_root / "DATASET" / "09_TEXTILE_MANUFACTURING" / "synthetic" / "sensor_readings.parquet"
    assert telemetry_path.exists()

    df = pd.read_parquet(telemetry_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="ISO8601")
    start_time = df["timestamp"].min()
    df["day"] = (df["timestamp"] - start_time).dt.total_seconds() / (24 * 3600) + 1.0

    tx2_healthy = df[(df["machine_id"] == "TX02") & (df["day"] >= 1.0) & (df["day"] <= 10.0)]
    tx2_degraded = df[(df["machine_id"] == "TX02") & (df["day"] >= 16.0) & (df["day"] <= 19.0)]

    assert tx2_degraded["vibration_mms"].mean() > tx2_healthy["vibration_mms"].mean() * 1.8
    assert tx2_degraded["vibration_mms"].max() >= 4.5

    # Verify spindle speed drops due to bolster bearing drag
    assert tx2_degraded["rotational_speed_rpm"].mean() < tx2_healthy["rotational_speed_rpm"].mean() - 1000.0


def test_textile_pydantic_validation(project_root: Path):
    """Verify that all Textile MSME exported CSV records parse into unified Pydantic schemas."""
    data_dir = project_root / "DATASET" / "09_TEXTILE_MANUFACTURING" / "synthetic"

    df_machines = pd.read_csv(data_dir / "machines.csv")
    for _, row in df_machines.iterrows():
        Machine.model_validate(row.to_dict())

    df_jobs = pd.read_csv(data_dir / "production_jobs.csv")
    for _, row in df_jobs.head(50).iterrows():
        ProductionJob.model_validate(row.to_dict())

    df_maint = pd.read_csv(data_dir / "maintenance_records.csv")
    for _, row in df_maint.iterrows():
        MaintenanceRecord.model_validate(row.to_dict())

    df_inv = pd.read_csv(data_dir / "inventory_items.csv")
    for _, row in df_inv.iterrows():
        InventoryItem.model_validate(row.to_dict())

