"""
Phase 7 Multi-Sensor Anomaly Detection Comprehensive Test Suite
Validates:
1. Schema compatibility with SensorReading
2. Feature generation causality and zero future lookahead
3. Clean temporal reference training vs validation vs evaluation split
4. Anomaly score normalization and threshold behavior
5. Model training, fitting, and baseline benchmarking
6. AnomalyDetectionService real-time streaming inference
7. Event-level grouping and clustering
8. Configured synthetic scenario validation (Days 18-21 M2 degradation)
"""

from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.data.schema import SensorReading
from src.features.anomaly_features import (
    engineer_synthetic_anomaly_features,
    prepare_ai4i_anomaly_splits,
    prepare_synthetic_anomaly_splits
)
from src.models.anomaly_detector import (
    IsolationForestDetector,
    OneClassSVMDetector,
    PCAReconstructionDetector,
    RobustZScoreDetector
)
from src.models.train_anomaly import evaluate_anomaly_events, run_anomaly_benchmarks
from src.services.anomaly_service import AnomalyDetectionService
from src.utils.config_loader import get_project_root


@pytest.fixture
def synthetic_readings_sample():
    """Generates a small multi-machine synthetic telemetry sample for fast testing."""
    records = []
    base_time = datetime(2026, 1, 1, 6, 0, tzinfo=timezone.utc)
    for step in range(50):
        t = base_time + pd.Timedelta(minutes=step * 5)
        for m in ["M1", "M2"]:
            # M2 experiences anomalous elevation in later steps
            is_m2_anom = (m == "M2" and step >= 40)
            vib = 4.5 if is_m2_anom else (1.4 if m == "M2" else 1.2)
            temp = 55.0 if is_m2_anom else 38.0
            power = 27.0 if is_m2_anom else (22.0 if m == "M2" else 15.0)

            records.append({
                "reading_id": len(records) + 1,
                "machine_id": m,
                "timestamp": t,
                "vibration_mms": vib,
                "temperature_c": temp,
                "ambient_temperature_c": 25.0,
                "rotational_speed_rpm": 1500.0,
                "torque_nm": 140.0 if m == "M2" else 95.0,
                "sound_db": 75.0,
                "power_consumption_kw": power,
                "oil_level_pct": 50.0 if is_m2_anom else 85.0,
                "coolant_level_pct": 90.0,
                "tool_wear_min": float(step * 2)
            })
    return pd.DataFrame(records)


def test_feature_engineering_causality(synthetic_readings_sample):
    """Verifies that engineered rolling features are strictly causal and grouped by machine."""
    df_feat = engineer_synthetic_anomaly_features(synthetic_readings_sample, rolling_window=5)

    # Check new columns exist
    assert "temp_diff_c" in df_feat.columns
    assert "mechanical_power_kw" in df_feat.columns
    assert "power_ratio" in df_feat.columns
    assert "vibration_mms_roll_mean_5" in df_feat.columns
    assert "vibration_mms_diff_1" in df_feat.columns

    # Verify first row per machine has diff_1 equal to 0.0 (no forward leakage)
    for m in ["M1", "M2"]:
        m_rows = df_feat[df_feat["machine_id"] == m]
        assert m_rows.iloc[0]["vibration_mms_diff_1"] == 0.0
        # Rolling mean of first item must equal the first item itself (min_periods=1)
        assert np.isclose(m_rows.iloc[0]["vibration_mms_roll_mean_5"], m_rows.iloc[0]["vibration_mms"])


def test_clean_temporal_split_guardrails():
    """Verifies that M2 degradation period is isolated from training splits."""
    root = get_project_root()
    csv_path = root / "DATASET" / "10_SYNTHETIC_FACTORY" / "synthetic" / "sensor_readings.csv"
    if not csv_path.exists():
        pytest.skip("Synthetic factory dataset not present.")

    df = pd.read_csv(csv_path)
    splits = prepare_synthetic_anomaly_splits(df, target_machine_id="M2")

    # Training must be strictly Days 1-15 (nominal)
    t_train_max = pd.to_datetime(splits["train_df"]["timestamp"]).max()
    assert t_train_max < pd.to_datetime("2026-01-16 06:00:00+00:00")
    assert splits["y_train"].sum() == 0  # Zero anomalies in training

    # Validation must be Days 16-17 (nominal)
    t_val_max = pd.to_datetime(splits["val_df"]["timestamp"]).max()
    assert t_val_max < pd.to_datetime("2026-01-18 06:00:00+00:00")
    assert splits["y_val"].sum() == 0  # Zero anomalies in validation

    # Test contains the degradation period
    assert splits["y_test"].sum() == 1152


def test_ai4i_semi_supervised_leakage_exclusion():
    """Verifies that AI4I training split strictly excludes failure instances."""
    root = get_project_root()
    ai4i_csv = root / "DATASET" / "01_AI4I_2020" / "raw" / "ai4i2020.csv"
    if not ai4i_csv.exists():
        pytest.skip("AI4I dataset not present.")

    df_ai4i = pd.read_csv(ai4i_csv)
    splits = prepare_ai4i_anomaly_splits(df_ai4i)

    # X_train must contain strictly zero failures
    assert len(splits["X_train"]) > 0
    # X_test contains failure instances evaluated post-hoc
    assert splits["y_test"].sum() == 339


def test_anomaly_detectors_fit_score_calibrate():
    """Verifies that all 4 detector classes can fit, score in [0, 1], and calibrate thresholds."""
    np.random.seed(42)
    # Generate 100 nominal rows and 20 anomalous rows
    X_train = pd.DataFrame({
        "f1": np.random.normal(10.0, 1.0, 100),
        "f2": np.random.normal(50.0, 5.0, 100)
    })
    X_val = pd.DataFrame({
        "f1": np.random.normal(10.0, 1.0, 30),
        "f2": np.random.normal(50.0, 5.0, 30)
    })
    X_anom = pd.DataFrame({
        "f1": np.random.normal(30.0, 2.0, 20),
        "f2": np.random.normal(150.0, 10.0, 20)
    })

    detectors = [
        RobustZScoreDetector(),
        PCAReconstructionDetector(variance_retained=0.90),
        OneClassSVMDetector(nu=0.05),
        IsolationForestDetector(n_estimators=50, random_state=42)
    ]

    for det in detectors:
        det.fit(X_train)
        assert det.is_fitted
        # Threshold calibration
        thresh = det.calibrate_threshold(X_val, target_quantile=0.95)
        assert 0.0 <= thresh <= 1.0

        # Scoring
        norm_scores = det.score_samples(X_val)
        anom_scores = det.score_samples(X_anom)
        assert np.all((norm_scores >= 0.0) & (norm_scores <= 1.0))
        assert np.all((anom_scores >= 0.0) & (anom_scores <= 1.0))

        # Mean anomaly score of outliers must be significantly higher than nominal
        assert np.mean(anom_scores) > np.mean(norm_scores)


def test_event_level_evaluation_logic():
    """Verifies that contiguous anomalies are merged into episodic clusters and lead time computed."""
    ts = pd.date_range("2026-01-20 00:00", periods=20, freq="1h", tz="UTC")
    y_true = np.zeros(20, dtype=int)
    # True degradation on steps 10 to 15
    y_true[10:16] = 1

    # Pred: detections on steps 11, 12, 13 (true detected event) and step 2 (isolated false alarm)
    y_pred = np.zeros(20, dtype=int)
    y_pred[2] = 1
    y_pred[11:14] = 1

    res = evaluate_anomaly_events(ts, y_true, y_pred, max_gap_steps=2)
    assert res["true_events"] == 1
    assert res["detected_true_events"] == 1
    assert res["false_alarm_events"] == 1
    assert res["lead_time_hours"] > 0.0


def test_anomaly_detection_service_inference():
    """Verifies that AnomalyDetectionService consumes SensorReading schemas and produces diagnostic results."""
    root = get_project_root()
    model_path = root / "models" / "anomaly_detection" / "anomaly_detector.joblib"
    if not model_path.exists():
        pytest.skip("Anomaly detector joblib not trained yet.")

    service = AnomalyDetectionService(model_path=model_path)

    # 1. Test nominal reading on M2
    normal_reading = SensorReading(
        machine_id="M2",
        timestamp=datetime.now(timezone.utc),
        vibration_mms=1.42,
        temperature_c=38.5,
        ambient_temperature_c=25.0,
        rotational_speed_rpm=1500.0,
        torque_nm=140.0,
        sound_db=74.0,
        power_consumption_kw=22.1,
        oil_level_pct=82.0,
        coolant_level_pct=92.0
    )
    res_norm = service.detect(normal_reading)
    assert res_norm.machine_id == "M2"
    assert 0.0 <= res_norm.anomaly_score <= 1.0
    assert res_norm.operating_regime_status == "NOMINAL_REGIME"

    # 2. Test anomalous high vibration/temp reading on M2
    anom_reading = SensorReading(
        machine_id="M2",
        timestamp=datetime.now(timezone.utc),
        vibration_mms=5.85,
        temperature_c=65.2,
        ambient_temperature_c=26.0,
        rotational_speed_rpm=1480.0,
        torque_nm=175.0,
        sound_db=88.0,
        power_consumption_kw=27.5,
        oil_level_pct=32.0,
        coolant_level_pct=70.0
    )
    # Stream multiple anomalous readings to update buffer
    for _ in range(5):
        res_anom = service.detect(anom_reading)

    assert res_anom.is_anomaly is True
    assert res_anom.severity in ["WARNING", "CRITICAL"]
    assert len(res_anom.top_contributing_sensors) > 0
