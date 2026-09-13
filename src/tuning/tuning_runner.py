"""
NirmaanAI Tuning Runner & Summary Compiler
Compiles global tuning summary directly from saved task artifacts in models/tuned/.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any

from src.utils.config_loader import get_project_root
from src.utils.logger import logger


TASKS_ORDER = [
    "manufacturing_production",
    "secom",
    "industrial_iot_failure",
    "ai4i",
    "cmapss",
    "electricity",
    "industrial_iot_rul",
    "manufacturing_defects",
    "textile",
    "synthetic_factory",
]


def compile_global_tuning_summary() -> Dict[str, Any]:
    root = get_project_root()
    tuned_dir = root / "models" / "tuned"
    tuned_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "compilation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "total_tasks": len(TASKS_ORDER),
        "tasks_accepted": 0,
        "tasks_retained": 0,
        "tasks": {},
    }

    for task in TASKS_ORDER:
        t_dir = tuned_dir / task
        if (t_dir / "tuning_metadata.json").exists():
            with open(t_dir / "tuning_metadata.json") as f:
                meta = json.load(f)
            with open(t_dir / "improvement_summary.json") as f:
                imp = json.load(f)
            with open(t_dir / "final_test_metrics.json") as f:
                test_m = json.load(f)

            dec = meta.get("decision_status")
            if dec == "TUNED_MODEL_ACCEPTED":
                summary["tasks_accepted"] += 1
            else:
                summary["tasks_retained"] += 1

            summary["tasks"][task] = {
                "task_name": meta.get("task"),
                "epistemic_status": meta.get("epistemic_status"),
                "champion_model": meta.get("champion_model"),
                "decision_status": dec,
                "configurations_evaluated": meta.get("configurations_evaluated"),
                "baseline_val_score": meta.get("baseline_val_score", meta.get("baseline_val_score_rmse", meta.get("baseline_val_score_wape"))),
                "tuned_val_score": meta.get("tuned_val_score", meta.get("tuned_val_score_rmse", meta.get("tuned_val_score_wape"))),
                "val_abs_improvement": imp.get("val_abs_improvement"),
                "val_rel_improvement_pct": imp.get("val_rel_improvement_pct"),
                "baseline_test_score": meta.get("baseline_test_score", meta.get("baseline_test_score_rmse", meta.get("baseline_test_score_wape"))),
                "tuned_test_score": meta.get("tuned_test_score", meta.get("tuned_test_score_rmse", meta.get("tuned_test_score_wape"))),
                "test_abs_delta": imp.get("test_abs_delta"),
                "test_rel_delta_pct": imp.get("test_rel_delta_pct"),
                "final_test_metrics": test_m,
            }

    summary_path = tuned_dir / "global_tuning_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"Global tuning summary saved to {summary_path} (Accepted: {summary['tasks_accepted']}, Retained: {summary['tasks_retained']})")
    return summary


if __name__ == "__main__":
    compile_global_tuning_summary()
