"""
NirmaanAI Forecasting Training & Benchmarking Pipeline
Phase 9: Production & Energy Forecasting

Executes multi-horizon forecasting benchmarks:
1. Empirical Grid Electricity Load: UCI Electricity Load (Client MT_124, 1-hour resolution)
2. Synthetic MSME Shop Floor Energy: Sensor Readings (Sum of M1-M5, 1-hour resolution)
3. Synthetic MSME Production Throughput: Daily completed units

Adheres strictly to research-integrity rules:
- Chronological train/val/test splits (70% / 15% / 15%).
- Model selection performed strictly on validation split.
- Holdout test split evaluated once for final reporting.
- Downstream tariff calculation (₹8.50 base vs ₹12.50 peak) strictly separated from forecast targets.
"""

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
import pandas as pd

from src.features.forecasting_features import (
    build_energy_features,
    calculate_forecasting_metrics,
    prepare_synthetic_factory_energy_data,
    prepare_synthetic_production_throughput_data,
    prepare_uci_electricity_data,
    split_chronologically
)
from src.models.forecasting_models import (
    BaseForecaster,
    PersistenceForecaster,
    RandomForestForecaster,
    RidgeForecaster,
    SeasonalDiurnalForecaster,
    XGBoostForecaster
)
from src.utils.config_loader import get_project_root, load_yaml_config
from src.utils.logger import logger


@dataclass
class ForecastBenchmarkResult:
    dataset_name: str
    target_variable: str
    temporal_resolution: str
    model_name: str
    val_mae: float
    val_rmse: float
    val_r2: float
    val_wape: float
    val_smape: float
    test_mae: float
    test_rmse: float
    test_r2: float
    test_wape: float
    test_smape: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def calculate_energy_cost_inr(
    df_timestamps: pd.Series,
    power_kw: np.ndarray,
    interval_hours: float = 1.0,
    base_tariff: float = 8.50,
    peak_tariff: float = 12.50
) -> Dict[str, float]:
    """
    Computes downstream electricity costs in INR based on configured MSME assumptions.
    Peak tariff applies strictly during 18:00 - 22:00.
    Cost = kWh * Tariff.
    """
    hours = df_timestamps.dt.hour.values
    is_peak = (hours >= 18) & (hours < 22)

    kwh = power_kw * interval_hours
    peak_kwh = float(np.sum(kwh[is_peak]))
    base_kwh = float(np.sum(kwh[~is_peak]))
    total_kwh = peak_kwh + base_kwh

    cost_base = base_kwh * base_tariff
    cost_peak = peak_kwh * peak_tariff
    total_cost = cost_base + cost_peak

    return {
        "total_kwh": round(total_kwh, 2),
        "peak_kwh": round(peak_kwh, 2),
        "base_kwh": round(base_kwh, 2),
        "peak_kwh_ratio": round(peak_kwh / total_kwh, 4) if total_kwh > 0 else 0.0,
        "total_cost_inr": round(total_cost, 2),
        "cost_base_inr": round(cost_base, 2),
        "cost_peak_inr": round(cost_peak, 2)
    }


def run_forecasting_pipeline() -> Dict[str, Any]:
    """Executes the complete Phase 9 training, benchmarking, and artifact generation."""
    root = get_project_root()
    output_dir = root / "models" / "forecasting"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load factory defaults for tariff assumptions
    factory_defaults = load_yaml_config(str(root / "configs" / "factory_defaults.yaml"))
    fin_assumptions = factory_defaults.get("financial_assumptions", {})
    base_tariff = fin_assumptions.get("base_electricity_rate_inr_per_kwh", 8.50)
    peak_tariff = fin_assumptions.get("peak_electricity_rate_inr_per_kwh", 12.50)
    logger.info(f"Tariff Assumptions: Base = INR {base_tariff}/kWh, Peak (18-22h) = INR {peak_tariff}/kWh")

    benchmark_records: List[Dict[str, Any]] = []

    # =========================================================================
    # PART 1: Empirical Grid Electricity Forecasting (UCI MT_124)
    # =========================================================================
    uci_txt = root / "DATASET" / "04_ENERGY" / "raw" / "LD2011_2014.txt"
    logger.info("=== Benchmarking Empirical Grid Electricity Dataset (UCI MT_124) ===")
    
    # Prepare 2012-2014 hourly resampled load (26,304 timestamps)
    df_uci_raw = prepare_uci_electricity_data(
        file_path=uci_txt,
        client_id="MT_124",
        resample_freq="1h",
        start_date="2012-01-01",
        end_date="2014-12-31"
    )
    df_uci_feat = build_energy_features(df_uci_raw, target_col="power_kw", freq="1h")
    splits_uci = split_chronologically(df_uci_feat, train_ratio=0.70, val_ratio=0.15)

    uci_models = [
        PersistenceForecaster(lag_col_preference="lag_24h"),
        SeasonalDiurnalForecaster(),
        RidgeForecaster(alpha=10.0, random_state=42),
        RandomForestForecaster(n_estimators=80, max_depth=10, random_state=42),
        XGBoostForecaster(n_estimators=100, learning_rate=0.05, max_depth=5, random_state=42)
    ]

    best_val_rmse = float("inf")
    uci_champion_model: Optional[BaseForecaster] = None
    uci_champion_preds_test: Optional[np.ndarray] = None

    for model in uci_models:
        model.fit(splits_uci["X_train"], splits_uci["y_train"], feature_names=splits_uci["feature_names"])
        val_metrics = model.evaluate(splits_uci["X_val"], splits_uci["y_val"])
        test_metrics = model.evaluate(splits_uci["X_test"], splits_uci["y_test"])

        rec = ForecastBenchmarkResult(
            dataset_name="UCI_Electricity_LD2011_2014 (MT_124)",
            target_variable="power_kw",
            temporal_resolution="1-hour average active power (kW)",
            model_name=model.name,
            val_mae=val_metrics["mae"],
            val_rmse=val_metrics["rmse"],
            val_r2=val_metrics["r2"],
            val_wape=val_metrics["wape"],
            val_smape=val_metrics["smape"],
            test_mae=test_metrics["mae"],
            test_rmse=test_metrics["rmse"],
            test_r2=test_metrics["r2"],
            test_wape=test_metrics["wape"],
            test_smape=test_metrics["smape"]
        )
        benchmark_records.append(rec.to_dict())
        logger.info(
            f"[UCI - {model.name}] Val RMSE: {val_metrics['rmse']:.2f}, Val WAPE: {val_metrics['wape']:.4f} | "
            f"Test RMSE: {test_metrics['rmse']:.2f}, Test WAPE: {test_metrics['wape']:.4f}, Test R2: {test_metrics['r2']:.4f}"
        )

        # Model selection strictly on validation RMSE
        if val_metrics["rmse"] < best_val_rmse:
            best_val_rmse = val_metrics["rmse"]
            uci_champion_model = model
            uci_champion_preds_test = model.predict(splits_uci["X_test"])

    # =========================================================================
    # PART 2: Synthetic Shop Floor Energy Demand (Plant-Wide M1-M5)
    # =========================================================================
    sensor_parquet = root / "DATASET" / "10_SYNTHETIC_FACTORY" / "synthetic" / "sensor_readings.parquet"
    logger.info("=== Benchmarking Synthetic Shop Floor Plant Energy (M1 to M5) ===")
    
    df_plant_raw = prepare_synthetic_factory_energy_data(sensor_parquet, resample_freq="1h")
    df_plant_feat = build_energy_features(df_plant_raw, target_col="plant_power_kw", freq="1h")
    splits_plant = split_chronologically(df_plant_feat, train_ratio=0.70, val_ratio=0.15)

    plant_models = [
        PersistenceForecaster(lag_col_preference="lag_24h"),
        SeasonalDiurnalForecaster(),
        RidgeForecaster(alpha=1.0, random_state=42),
        RandomForestForecaster(n_estimators=50, max_depth=8, random_state=42),
        XGBoostForecaster(n_estimators=80, learning_rate=0.05, max_depth=4, random_state=42)
    ]

    best_plant_val_rmse = float("inf")
    plant_champion_model: Optional[BaseForecaster] = None
    plant_champion_preds_test: Optional[np.ndarray] = None

    for model in plant_models:
        model.fit(splits_plant["X_train"], splits_plant["y_train"], feature_names=splits_plant["feature_names"])
        val_metrics = model.evaluate(splits_plant["X_val"], splits_plant["y_val"])
        test_metrics = model.evaluate(splits_plant["X_test"], splits_plant["y_test"])

        rec = ForecastBenchmarkResult(
            dataset_name="Synthetic_Factory_Plant_Power",
            target_variable="plant_power_kw",
            temporal_resolution="1-hour total plant power (kW)",
            model_name=model.name,
            val_mae=val_metrics["mae"],
            val_rmse=val_metrics["rmse"],
            val_r2=val_metrics["r2"],
            val_wape=val_metrics["wape"],
            val_smape=val_metrics["smape"],
            test_mae=test_metrics["mae"],
            test_rmse=test_metrics["rmse"],
            test_r2=test_metrics["r2"],
            test_wape=test_metrics["wape"],
            test_smape=test_metrics["smape"]
        )
        benchmark_records.append(rec.to_dict())
        logger.info(
            f"[Synthetic Plant - {model.name}] Val RMSE: {val_metrics['rmse']:.2f}, Val WAPE: {val_metrics['wape']:.4f} | "
            f"Test RMSE: {test_metrics['rmse']:.2f}, Test WAPE: {test_metrics['wape']:.4f}, Test R2: {test_metrics['r2']:.4f}"
        )

        if val_metrics["rmse"] < best_plant_val_rmse:
            best_plant_val_rmse = val_metrics["rmse"]
            plant_champion_model = model
            plant_champion_preds_test = model.predict(splits_plant["X_test"])

    # Downstream Tariff Cost Estimation on Test Split (Plant Power)
    test_plant_timestamps = splits_plant["test_df"]["timestamp"]
    actual_test_cost = calculate_energy_cost_inr(
        test_plant_timestamps,
        splits_plant["y_test"],
        base_tariff=base_tariff,
        peak_tariff=peak_tariff
    )
    predicted_test_cost = calculate_energy_cost_inr(
        test_plant_timestamps,
        plant_champion_preds_test,
        base_tariff=base_tariff,
        peak_tariff=peak_tariff
    )

    # =========================================================================
    # PART 3: Synthetic Production Throughput Forecasting
    # =========================================================================
    jobs_csv = root / "DATASET" / "10_SYNTHETIC_FACTORY" / "synthetic" / "production_jobs.csv"
    logger.info("=== Benchmarking Synthetic Production Throughput (Daily Completed Units) ===")
    
    df_prod_raw = prepare_synthetic_production_throughput_data(jobs_csv)
    splits_prod = split_chronologically(
        df_prod_raw,
        train_ratio=0.70,
        val_ratio=0.15,
        target_col="target_completed_units"
    )

    prod_models = [
        PersistenceForecaster(lag_col_preference="lag_completed_1d"),
        RidgeForecaster(alpha=1.0, random_state=42),
        RandomForestForecaster(n_estimators=30, max_depth=4, random_state=42),
        XGBoostForecaster(n_estimators=40, learning_rate=0.08, max_depth=3, random_state=42)
    ]

    best_prod_val_rmse = float("inf")
    prod_champion_model: Optional[BaseForecaster] = None

    for model in prod_models:
        model.fit(splits_prod["X_train"], splits_prod["y_train"], feature_names=splits_prod["feature_names"])
        val_metrics = model.evaluate(splits_prod["X_val"], splits_prod["y_val"])
        test_metrics = model.evaluate(splits_prod["X_test"], splits_prod["y_test"])

        rec = ForecastBenchmarkResult(
            dataset_name="Synthetic_Production_Throughput",
            target_variable="target_completed_units",
            temporal_resolution="Daily completed unit volume",
            model_name=model.name,
            val_mae=val_metrics["mae"],
            val_rmse=val_metrics["rmse"],
            val_r2=val_metrics["r2"],
            val_wape=val_metrics["wape"],
            val_smape=val_metrics["smape"],
            test_mae=test_metrics["mae"],
            test_rmse=test_metrics["rmse"],
            test_r2=test_metrics["r2"],
            test_wape=test_metrics["wape"],
            test_smape=test_metrics["smape"]
        )
        benchmark_records.append(rec.to_dict())
        logger.info(
            f"[Synthetic Production - {model.name}] Val RMSE: {val_metrics['rmse']:.2f}, Val WAPE: {val_metrics['wape']:.4f} | "
            f"Test RMSE: {test_metrics['rmse']:.2f}, Test WAPE: {test_metrics['wape']:.4f}, Test R2: {test_metrics['r2']:.4f}"
        )

        if val_metrics["rmse"] < best_prod_val_rmse:
            best_prod_val_rmse = val_metrics["rmse"]
            prod_champion_model = model

    # =========================================================================
    # Serialization & Metadata Generation
    # =========================================================================
    # Save champion models
    joblib.dump(
        {
            "uci_energy_champion": uci_champion_model,
            "plant_energy_champion": plant_champion_model,
            "production_champion": prod_champion_model,
            "feature_names_uci": splits_uci["feature_names"],
            "feature_names_plant": splits_plant["feature_names"],
            "feature_names_prod": splits_prod["feature_names"],
            "tariff_assumptions": {
                "base_tariff_inr": base_tariff,
                "peak_tariff_inr": peak_tariff,
                "peak_window": "18:00 - 22:00"
            }
        },
        output_dir / "forecaster_champion.joblib"
    )
    logger.info(f"Saved forecasting models to {output_dir / 'forecaster_champion.joblib'}")

    metadata = {
        "subsystem": "Production & Energy Forecasting",
        "phase": "Phase 9",
        "dataset_separation": {
            "empirical_benchmark": "UCI Electricity Load Diagrams 2011-2014 (MT_124) - Real-world electrical grid load time series",
            "synthetic_shop_floor": "Synthetic Factory 10 - Controlled simulation of 5-machine manufacturing floor",
            "demarcation_note": "UCI meters represent electrical consumers on a utility grid and are NOT factory machines. Synthetic factory results represent generative simulation equations."
        },
        "tariff_assumptions": {
            "type": "Configured MSME Simulation Assumption",
            "base_electricity_rate_inr_per_kwh": base_tariff,
            "peak_electricity_rate_inr_per_kwh": peak_tariff,
            "peak_hours_window": "18:00 - 22:00",
            "source": "factory_defaults.yaml"
        },
        "temporal_specifications": {
            "uci_energy": {
                "native_frequency": "15-minute",
                "resampled_frequency": "1-hour",
                "target": "power_kw",
                "semantic_lag_mapping": {
                    "lag_1h": "t - 1 step (1 hour prior)",
                    "lag_2h": "t - 2 steps (2 hours prior)",
                    "lag_3h": "t - 3 steps (3 hours prior)",
                    "lag_24h": "t - 24 steps (same hour previous day)",
                    "lag_168h": "t - 168 steps (same hour previous week)"
                },
                "split_counts": {
                    "train": len(splits_uci["train_df"]),
                    "val": len(splits_uci["val_df"]),
                    "test": len(splits_uci["test_df"])
                }
            },
            "synthetic_plant_energy": {
                "native_frequency": "5-minute telemetry",
                "resampled_frequency": "1-hour",
                "target": "plant_power_kw",
                "split_counts": {
                    "train": len(splits_plant["train_df"]),
                    "val": len(splits_plant["val_df"]),
                    "test": len(splits_plant["test_df"])
                }
            },
            "synthetic_production": {
                "native_frequency": "daily aggregated jobs",
                "target": "target_completed_units",
                "split_counts": {
                    "train": len(splits_prod["train_df"]),
                    "val": len(splits_prod["val_df"]),
                    "test": len(splits_prod["test_df"])
                }
            }
        },
        "downstream_tariff_cost_validation": {
            "test_window_hours": len(splits_plant["test_df"]),
            "actual": actual_test_cost,
            "predicted": predicted_test_cost,
            "cost_prediction_error_pct": round(
                100.0 * abs(predicted_test_cost["total_cost_inr"] - actual_test_cost["total_cost_inr"]) / actual_test_cost["total_cost_inr"],
                2
            )
        },
        "benchmark_records": benchmark_records,
        "champion_models": {
            "uci_energy": uci_champion_model.name,
            "plant_energy": plant_champion_model.name,
            "production_throughput": prod_champion_model.name
        }
    }

    with open(output_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Saved forecasting metadata to {output_dir / 'metadata.json'}")

    return metadata


if __name__ == "__main__":
    run_forecasting_pipeline()
