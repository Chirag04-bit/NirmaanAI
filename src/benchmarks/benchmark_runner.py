"""
NirmaanAI Baseline Model Benchmark Runner
Executes comprehensive dataset-by-dataset baseline model benchmarking across all 9 manufacturing datasets in strict isolation.

Guarantees:
- Zero cross-dataset contamination (independent processes/invocations)
- No hyperparameter tuning (standard defaults only)
- Holdout test evaluation strictly ONCE per dataset after validation champion selection
"""

import json
import time
from pathlib import Path
from typing import Dict, Any

from src.benchmarks.ai4i_benchmark import AI4IBenchmark
from src.benchmarks.cmapss_benchmark import CMAPSSBenchmark
from src.benchmarks.secom_benchmark import SECOMBenchmark
from src.benchmarks.electricity_benchmark import ElectricityBenchmark
from src.benchmarks.industrial_iot_failure_benchmark import IndustrialIoIFailureBenchmark
from src.benchmarks.industrial_iot_rul_benchmark import IndustrialIoIRULBenchmark
from src.benchmarks.production_benchmark import ProductionBenchmark
from src.benchmarks.defects_benchmark import DefectsBenchmark
from src.benchmarks.textile_benchmark import TextileBenchmark
from src.benchmarks.synthetic_factory_benchmark import SyntheticFactoryBenchmark
from src.utils.config_loader import get_project_root
from src.utils.logger import logger


BENCHMARK_REGISTRY = {
    "ai4i": AI4IBenchmark,
    "cmapss": CMAPSSBenchmark,
    "secom": SECOMBenchmark,
    "electricity": ElectricityBenchmark,
    "industrial_iot_failure": IndustrialIoIFailureBenchmark,
    "industrial_iot_rul": IndustrialIoIRULBenchmark,
    "manufacturing_production": ProductionBenchmark,
    "manufacturing_defects": DefectsBenchmark,
    "textile": TextileBenchmark,
    "synthetic_factory": SyntheticFactoryBenchmark,
}


def run_all_benchmarks(save_artifacts: bool = True) -> Dict[str, Any]:
    root = get_project_root()
    benchmarks_out = root / "models" / "benchmarks"
    benchmarks_out.mkdir(parents=True, exist_ok=True)

    summary = {
        "execution_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "datasets_benchmarked": len(BENCHMARK_REGISTRY),
        "results": {},
    }

    logger.info(f"Starting NirmaanAI Baseline Benchmarking Suite across {len(BENCHMARK_REGISTRY)} tasks...")

    for dataset_id, benchmark_cls in BENCHMARK_REGISTRY.items():
        logger.info(f"============================================================")
        logger.info(f"Executing Benchmark: {dataset_id.upper()}")
        logger.info(f"============================================================")
        start_t = time.time()
        benchmark_instance = benchmark_cls()
        result = benchmark_instance.run_benchmark(save_artifacts=save_artifacts)
        elapsed = time.time() - start_t

        summary["results"][dataset_id] = {
            "champion": result["champion"],
            "val_metrics": result["val_metrics"],
            "test_metrics": result["test_metrics"],
            "elapsed_seconds": round(elapsed, 2),
        }
        logger.info(f"[{dataset_id}] Benchmark completed in {elapsed:.2f}s. Champion: {result['champion']}")

    if save_artifacts:
        summary_path = benchmarks_out / "global_benchmark_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Global benchmark summary saved to {summary_path}")

    return summary


def compile_global_summary() -> Dict[str, Any]:
    """Compiles global benchmark summary directly from saved dataset artifacts."""
    root = get_project_root()
    benchmarks_out = root / "models" / "benchmarks"
    
    summary = {
        "compilation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "total_datasets": len(BENCHMARK_REGISTRY),
        "benchmarks": {},
    }

    for dataset_id in BENCHMARK_REGISTRY:
        d_path = benchmarks_out / dataset_id
        if (d_path / "benchmark_metadata.json").exists():
            with open(d_path / "benchmark_metadata.json") as f:
                meta = json.load(f)
            with open(d_path / "final_test_metrics.json") as f:
                test_m = json.load(f)
            summary["benchmarks"][dataset_id] = {
                "task": meta.get("task"),
                "epistemic_status": meta.get("epistemic_status"),
                "champion_model": meta.get("champion_model"),
                "test_score": meta.get("test_score", meta.get("test_score_rmse", meta.get("test_score_wape", meta.get("test_score_mean")))),
                "test_metrics": test_m,
                "tuning_status": meta.get("tuning_status", "NOT_STARTED"),
            }

    summary_path = benchmarks_out / "global_benchmark_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Compiled global benchmark summary saved to {summary_path}")
    return summary


if __name__ == "__main__":
    compile_global_summary()

