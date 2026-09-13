import json
from pathlib import Path
import pytest

from src.utils.config_loader import get_project_root


EXPECTED_DATASETS = [
    "ai4i",
    "cmapss",
    "secom",
    "electricity",
    "industrial_iot_failure",
    "industrial_iot_rul",
    "manufacturing_production",
    "manufacturing_defects",
    "textile",
    "synthetic_factory",
]


@pytest.fixture
def benchmarks_dir():
    root = get_project_root()
    return root / "models" / "benchmarks"


def test_all_10_dataset_benchmarks_exist(benchmarks_dir):
    for d in EXPECTED_DATASETS:
        d_path = benchmarks_dir / d
        assert d_path.exists(), f"Benchmark directory missing for {d}"
        assert (d_path / "model_comparison.csv").exists()
        assert (d_path / "validation_metrics.json").exists()
        assert (d_path / "final_test_metrics.json").exists()
        assert (d_path / "training_config.json").exists()
        assert (d_path / "benchmark_metadata.json").exists()
        assert (d_path / "locked_baseline_model.joblib").exists()


def test_zero_tuning_performed_across_all_datasets(benchmarks_dir):
    for d in EXPECTED_DATASETS:
        with open(benchmarks_dir / d / "training_config.json") as f:
            cfg = json.load(f)
        assert cfg["tuning_performed"] is False, f"Tuning was marked True in {d}"

        with open(benchmarks_dir / d / "benchmark_metadata.json") as f:
            meta = json.load(f)
        assert meta["tuning_status"] == "NOT_STARTED", f"Tuning status not 'NOT_STARTED' in {d}"


def test_independent_champion_models(benchmarks_dir):
    models = {}
    for d in EXPECTED_DATASETS:
        with open(benchmarks_dir / d / "benchmark_metadata.json") as f:
            meta = json.load(f)
        models[d] = meta["champion_model"]

    # Ensure every benchmark has a valid champion identified
    assert len(models) == 10
    for d, champ in models.items():
        assert champ and isinstance(champ, str)


def test_global_summary_integrity(benchmarks_dir):
    summary_path = benchmarks_dir / "global_benchmark_summary.json"
    assert summary_path.exists()

    with open(summary_path) as f:
        summary = json.load(f)

    assert summary["total_datasets"] == 10
    for d in EXPECTED_DATASETS:
        assert d in summary["benchmarks"]
        entry = summary["benchmarks"][d]
        assert entry["tuning_status"] == "NOT_STARTED"
        assert entry["champion_model"] is not None
