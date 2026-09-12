"""
NirmaanAI Forecasting Test Suite
Phase 9: Production & Energy Forecasting

Tests:
1. Dataset ingestion & chronological structure
2. Strict temporal split isolation (Train < Val < Test)
3. Causal zero-lookahead feature independence (modifying future rows does not alter past features)
4. Robust metric calculations (WAPE, sMAPE, MAE, RMSE, R2)
5. Forecaster hierarchy: Persistence, Seasonal Diurnal, Ridge, Random Forest, XGBoost
6. Real-time ForecastingService inference & downstream tariff costing
7. Zero target leakage verification
"""

from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.features.forecasting_features import (
    build_energy_features,
    calculate_forecasting_metrics,
    prepare_synthetic_factory_energy_data,
    prepare_synthetic_production_throughput_data,
    prepare_uci_electricity_data,
    split_chronologically
)
from src.models.forecasting_models import (
    PersistenceForecaster,
    RandomForestForecaster,
    RidgeForecaster,
    SeasonalDiurnalForecaster,
    XGBoostForecaster
)
from src.services.forecasting_service import (
    EnergyForecastRequest,
    ForecastingService,
    ProductionForecastRequest
)
from src.utils.config_loader import get_project_root


def test_metric_calculations_stability():
    """Verifies that WAPE and sMAPE handle near-zero and typical values gracefully without ZeroDivisionError."""
    y_true = np.array([100.0, 200.0, 0.0, 50.0])
    y_pred = np.array([110.0, 190.0, 0.0, 55.0])

    metrics = calculate_forecasting_metrics(y_true, y_pred)
    assert metrics["mae"] == 6.25
    assert metrics["rmse"] > 0.0
    assert metrics["r2"] > 0.95
    assert 0.0 <= metrics["wape"] <= 1.0
    assert 0.0 <= metrics["smape"] <= 100.0

    # Test all-zeros edge case
    zero_metrics = calculate_forecasting_metrics(np.zeros(5), np.zeros(5))
    assert zero_metrics["wape"] == 0.0
    assert zero_metrics["smape"] == 0.0


def test_chronological_split_isolation():
    """Verifies that time-series splits strictly preserve chronological ordering with zero overlap."""
    dates = pd.date_range("2026-01-01", periods=100, freq="1h")
    df = pd.DataFrame({
        "timestamp": dates,
        "power_kw": np.random.uniform(50, 100, size=100)
    })
    df["target"] = df["power_kw"]

    splits = split_chronologically(df, train_ratio=0.70, val_ratio=0.15)
    train_df = splits["train_df"]
    val_df = splits["val_df"]
    test_df = splits["test_df"]

    assert len(train_df) == 70
    assert len(val_df) == 15
    assert len(test_df) == 15

    # Strict timestamp ordering
    assert train_df["timestamp"].max() < val_df["timestamp"].min()
    assert val_df["timestamp"].max() < test_df["timestamp"].min()


def test_zero_lookahead_feature_causality():
    """
    CRITICAL RESEARCH INTEGRITY:
    Modifying future rows in the raw time-series must NOT alter past engineered feature values.
    """
    dates = pd.date_range("2026-01-01", periods=300, freq="1h")
    raw_vals = np.linspace(50.0, 150.0, 300)
    
    df1 = pd.DataFrame({"timestamp": dates, "power_kw": raw_vals.copy()})
    feat1 = build_energy_features(df1, target_col="power_kw", freq="1h")

    # Create df2 where the last 50 rows are dramatically altered (e.g. multiplied by 10)
    df2 = pd.DataFrame({"timestamp": dates, "power_kw": raw_vals.copy()})
    df2.loc[250:, "power_kw"] = df2.loc[250:, "power_kw"] * 10.0
    feat2 = build_energy_features(df2, target_col="power_kw", freq="1h")

    # Inspect features for an earlier timestamp (e.g. index 50, which is well before index 250)
    features_to_check = ["lag_1h", "lag_2h", "lag_24h", "rolling_mean_6h", "rolling_mean_24h"]
    for col in features_to_check:
        val1 = feat1.iloc[50][col]
        val2 = feat2.iloc[50][col]
        assert np.isclose(val1, val2), f"Lookahead leak detected in {col}: {val1} != {val2}"


def test_zero_target_leakage_in_predictors():
    """Verifies that raw target columns are never present in the predictor feature names."""
    dates = pd.date_range("2026-01-01", periods=200, freq="1h")
    df = pd.DataFrame({"timestamp": dates, "power_kw": np.random.uniform(20, 40, size=200)})
    feat_df = build_energy_features(df, target_col="power_kw")
    splits = split_chronologically(feat_df)

    # Feature names must not contain the target variable
    assert "power_kw" not in splits["feature_names"]
    assert "target" not in splits["feature_names"]
    assert "timestamp" not in splits["feature_names"]


def test_forecasting_models_baseline_hierarchy():
    """Verifies that all models fit, predict, and produce valid positive continuous forecasts."""
    n_samples = 200
    n_features = 8
    X = np.random.uniform(10, 50, size=(n_samples, n_features))
    y = np.random.uniform(50, 100, size=n_samples)
    feature_names = [f"feat_{i}" for i in range(n_features)]
    feature_names[0] = "lag_1h"

    models = [
        PersistenceForecaster(lag_col_preference="lag_1h"),
        SeasonalDiurnalForecaster(),
        RidgeForecaster(alpha=1.0),
        RandomForestForecaster(n_estimators=10, max_depth=4),
        XGBoostForecaster(n_estimators=10, max_depth=3)
    ]

    for model in models:
        model.fit(X, y, feature_names=feature_names)
        preds = model.predict(X)
        assert len(preds) == n_samples
        assert np.all(preds >= 0.0), f"Model {model.name} produced negative predictions"
        
        metrics = model.evaluate(X, y)
        assert metrics["mae"] >= 0.0
        assert metrics["wape"] >= 0.0


def test_forecasting_service_inference_and_tariffs():
    """Verifies that ForecastingService correctly evaluates tariff windows (Peak ₹12.50 vs Base ₹8.50)."""
    root = get_project_root()
    artifact_path = root / "models" / "forecasting" / "forecaster_champion.joblib"
    if not artifact_path.exists():
        pytest.skip("Forecaster artifact not yet generated.")

    service = ForecastingService(model_artifact_path=artifact_path)

    # Test 24-hour horizon starting at 00:00 UTC
    req = EnergyForecastRequest(
        start_time=datetime(2026, 1, 15, 0, 0, tzinfo=timezone.utc),
        horizon_hours=24
    )
    res = service.forecast_plant_energy(req)

    assert len(res.hourly_forecasts) == 24
    assert res.total_predicted_kwh > 0.0
    assert res.total_estimated_cost_inr > 0.0

    # Check that exactly 4 hours (18:00, 19:00, 20:00, 21:00) are flagged as peak tariff
    peak_hours = [f for f in res.hourly_forecasts if f.is_peak_tariff]
    assert len(peak_hours) == 4
    for ph in peak_hours:
        assert 18 <= ph.hour < 22
        assert ph.tariff_rate_inr == 12.50

    base_hours = [f for f in res.hourly_forecasts if not f.is_peak_tariff]
    assert len(base_hours) == 20
    for bh in base_hours:
        assert bh.tariff_rate_inr == 8.50


def test_production_throughput_forecast_service():
    """Verifies that ForecastingService produces valid completed unit estimates and risk levels."""
    root = get_project_root()
    artifact_path = root / "models" / "forecasting" / "forecaster_champion.joblib"
    if not artifact_path.exists():
        pytest.skip("Forecaster artifact not yet generated.")

    service = ForecastingService(model_artifact_path=artifact_path)

    req = ProductionForecastRequest(
        target_date=datetime(2026, 1, 20, tzinfo=timezone.utc),
        planned_units=1200
    )
    res = service.forecast_production_throughput(req)

    assert res.planned_units == 1200
    assert res.predicted_completed_units > 0.0
    assert 0.0 < res.estimated_fulfillment_rate <= 1.5
    assert res.schedule_risk_level in ["LOW_RISK", "MODERATE_RISK", "HIGH_RISK"]
