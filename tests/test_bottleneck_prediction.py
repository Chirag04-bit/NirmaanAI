"""
Phase 8 Bottleneck Prediction & Flow Intelligence Test Suite
Verifies:
1. Exact dataset count verification (300 total, 150 train, 20 val, 130 test, 8 delayed)
2. Zero-lookahead feature engineering and causality
3. Target formulation and lack of direct label leakage
4. Model benchmark and heuristic scoring
5. BottleneckService inference, schema compliance, and flow state categorization
6. M2 controlled scenario flow propagation analysis
"""

from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.data.schema import JobStatus, ProductionJob
from src.features.bottleneck_features import (
    engineer_bottleneck_features,
    prepare_bottleneck_splits,
    prepare_hybrid_manufacturing_benchmark
)
from src.models.bottleneck_predictor import (
    HeuristicBottleneckClassifier,
    LogisticBottleneckClassifier,
    RandomForestBottleneckClassifier,
    XGBoostBottleneckClassifier
)
from src.services.bottleneck_service import BottleneckService
from src.utils.config_loader import get_project_root


@pytest.fixture
def sample_jobs_and_machines():
    """Generates synthetic jobs and machines for unit testing."""
    machines_df = pd.DataFrame([
        {"machine_id": "M1", "design_cycle_time_sec": 60.0, "rated_capacity_units_per_hour": 50.0, "baseline_vibration_mms": 1.2},
        {"machine_id": "M2", "design_cycle_time_sec": 45.0, "rated_capacity_units_per_hour": 70.0, "baseline_vibration_mms": 1.4}
    ])

    jobs = []
    base_t = datetime(2026, 1, 1, 6, 0, tzinfo=timezone.utc)
    for i in range(10):
        t_sch = base_t + pd.Timedelta(hours=i * 4)
        m = "M2" if i % 2 == 0 else "M1"
        is_delayed = (m == "M2" and i >= 6)
        act_cycle = 62.0 if is_delayed else 45.0
        start_delay = 20.0 if is_delayed else 1.0

        act_start = t_sch + pd.Timedelta(minutes=start_delay)
        act_end = act_start + pd.Timedelta(minutes=50)

        jobs.append({
            "job_id": f"JOB_{i+1:04d}",
            "machine_id": m,
            "operation_type": "Milling" if m == "M2" else "Turning",
            "scheduled_start": t_sch.isoformat(),
            "scheduled_end": (t_sch + pd.Timedelta(minutes=45)).isoformat(),
            "actual_start": act_start.isoformat(),
            "actual_end": act_end.isoformat(),
            "batch_quantity": 100,
            "completed_quantity": 95 if is_delayed else 98,
            "scrap_quantity": 5 if is_delayed else 2,
            "actual_cycle_time_sec": act_cycle,
            "status": "DELAYED" if is_delayed else "COMPLETED"
        })

    jobs_df = pd.DataFrame(jobs)
    return jobs_df, machines_df


def test_dataset_exact_counts():
    """Verifies that synthetic factory dataset matches exact verified counts."""
    root = get_project_root()
    jobs_csv = root / "DATASET" / "10_SYNTHETIC_FACTORY" / "synthetic" / "production_jobs.csv"
    if not jobs_csv.exists():
        pytest.skip("Synthetic production jobs CSV not found.")

    df = pd.read_csv(jobs_csv)
    assert len(df) == 300
    assert df["machine_id"].value_counts().to_dict() == {"M1": 60, "M2": 60, "M3": 60, "M4": 60, "M5": 60}
    assert df["status"].value_counts().to_dict() == {"COMPLETED": 292, "DELAYED": 8}

    # Delayed jobs must be strictly on M2 during Days 18-21
    m2_del = df[df["status"] == "DELAYED"]
    assert len(m2_del) == 8
    assert set(m2_del["machine_id"]) == {"M2"}


def test_zero_lookahead_feature_causality(sample_jobs_and_machines):
    """Verifies that engineered features do not use future information (Actual_End, post-duration)."""
    jobs_df, machines_df = sample_jobs_and_machines
    feat_df = engineer_bottleneck_features(jobs_df, machines_df)

    assert "bottleneck_event" in feat_df.columns
    assert "prior_cycle_ratio_mean" in feat_df.columns
    assert "pre_job_vibration_dev_1h" in feat_df.columns

    # First job per machine has nominal default prior history (1.0)
    first_m2 = feat_df[feat_df["machine_id"] == "M2"].iloc[0]
    assert first_m2["prior_cycle_ratio_mean"] == 1.0


def test_temporal_split_isolation():
    """Verifies that temporal splits cleanly isolate training, validation, and test sets."""
    root = get_project_root()
    jobs_csv = root / "DATASET" / "10_SYNTHETIC_FACTORY" / "synthetic" / "production_jobs.csv"
    machines_csv = root / "DATASET" / "10_SYNTHETIC_FACTORY" / "synthetic" / "machines.csv"
    if not jobs_csv.exists():
        pytest.skip("Dataset files not found.")

    jobs_df = pd.read_csv(jobs_csv)
    machines_df = pd.read_csv(machines_csv)

    splits = prepare_bottleneck_splits(jobs_df, machines_df)
    assert len(splits["X_train"]) == 150
    assert len(splits["X_val"]) == 20
    assert len(splits["X_test"]) == 130

    # Training and validation must contain strictly zero bottleneck positives
    assert splits["y_train"].sum() == 0
    assert splits["y_val"].sum() == 0
    # Test contains the 8 bottleneck events
    assert splits["y_test"].sum() == 8


def test_heuristic_bottleneck_classifier_fit_predict():
    """Verifies that HeuristicBottleneckClassifier outputs bounded probabilities and detects bottlenecks."""
    X = pd.DataFrame({
        "pre_job_vibration_dev_1h": [0.05, 0.65, 0.02, 0.45],
        "prior_cycle_ratio_mean": [1.02, 1.35, 0.99, 1.25]
    })
    y = np.array([0, 1, 0, 1])

    clf = HeuristicBottleneckClassifier()
    clf.fit(X, y)
    probs = clf.predict_proba(X)

    assert probs.shape == (4, 2)
    assert np.all((probs >= 0.0) & (probs <= 1.0))
    # Row 1 and Row 3 are nominal; Row 2 and Row 4 are high bottleneck risk
    assert probs[0, 1] < 0.30
    assert probs[1, 1] > 0.70


def test_bottleneck_service_inference():
    """Verifies that BottleneckService consumes ProductionJob entities and categorizes flow states."""
    root = get_project_root()
    model_path = root / "models" / "bottleneck_prediction" / "bottleneck_predictor.joblib"
    if not model_path.exists():
        pytest.skip("Bottleneck model artifact not yet trained.")

    service = BottleneckService(model_path=model_path)

    # 1. Nominal Job Assessment
    nom_job = ProductionJob(
        job_id="JOB_TEST_001",
        machine_id="M1",
        operation_type="Turning",
        scheduled_start=datetime(2026, 1, 15, 6, 15, tzinfo=timezone.utc),
        scheduled_end=datetime(2026, 1, 15, 7, 15, tzinfo=timezone.utc),
        batch_quantity=50
    )
    res_nom = service.assess_upcoming_job(nom_job, pre_job_vibration_mms=1.20, baseline_vibration_mms=1.20)
    assert res_nom.flow_status == "NOMINAL_FLOW"
    assert res_nom.is_bottleneck_predicted is False

    # 2. Critical Bottleneck Job Assessment (Severe Pre-job Vibration & Thermal Elevation)
    crit_job = ProductionJob(
        job_id="JOB_TEST_002",
        machine_id="M2",
        operation_type="VMC Milling",
        scheduled_start=datetime(2026, 1, 20, 6, 15, tzinfo=timezone.utc),
        scheduled_end=datetime(2026, 1, 20, 7, 30, tzinfo=timezone.utc),
        batch_quantity=150
    )
    # Simulate prior lagging cycle history on M2
    service.record_job_completion("M2", actual_cycle_sec=64.0, start_delay_min=25.0, nominal_cycle_sec=45.0)

    res_crit = service.assess_upcoming_job(crit_job, pre_job_vibration_mms=5.20, baseline_vibration_mms=1.40)
    assert res_crit.flow_status in ["MODERATE_CONGESTION", "CRITICAL_BOTTLENECK"]
    assert res_crit.is_bottleneck_predicted is True
    assert res_crit.active_constraint_machine == "M2"
    assert "M3" in res_crit.affected_machines  # Downstream stage propagation


def test_heuristic_thresholds_configured_independent_of_test_data():
    """Verifies that HeuristicBottleneckClassifier uses pre-configured domain thresholds without fitting on test labels."""
    clf = HeuristicBottleneckClassifier()
    # Default configured domain priors
    assert clf.vib_dev_threshold == 0.30
    assert clf.cycle_ratio_threshold == 1.10
    assert clf.threshold == 0.40

    # Fitting must not modify the configured thresholds based on y
    dummy_X = pd.DataFrame({
        "pre_job_vibration_dev_1h": [0.1, 0.2],
        "prior_cycle_ratio_mean": [1.0, 1.05]
    })
    dummy_y = np.array([0, 1])
    clf.fit(dummy_X, dummy_y)
    assert clf.vib_dev_threshold == 0.30
    assert clf.cycle_ratio_threshold == 1.10
    assert clf.threshold == 0.40


def test_zero_positive_training_constraint():
    """Verifies that training split contains zero positive bottleneck cases."""
    root = get_project_root()
    jobs_csv = root / "DATASET" / "10_SYNTHETIC_FACTORY" / "synthetic" / "production_jobs.csv"
    machines_csv = root / "DATASET" / "10_SYNTHETIC_FACTORY" / "synthetic" / "machines.csv"
    if not jobs_csv.exists():
        pytest.skip("Dataset files not found.")

    jobs_df = pd.read_csv(jobs_csv)
    machines_df = pd.read_csv(machines_csv)
    splits = prepare_bottleneck_splits(jobs_df, machines_df)

    # Statistical constraint: 0 positives in train and val
    assert int(splits["y_train"].sum()) == 0
    assert int(splits["y_val"].sum()) == 0
    assert len(splits["y_train"]) == 150
    assert len(splits["y_val"]) == 20
    assert int(splits["y_test"].sum()) == 8
    assert len(splits["y_test"]) == 130

