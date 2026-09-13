"""
NirmaanAI UCI Steel Industry Electricity Consumption Tuning & Validation
Task: Hourly Power Consumption (kW) Forecasting (Client MT_124)

Priority 6 Tuning Module
- Preserves chronological ordering (strictly non-overlapping causal windows)
- Zero lookahead leakage (causal lags and rolling windows only)
- Bounded deterministic hyperparameter exploration on XGBoost Regressor
- Model selection strictly on val.parquet via WAPE (lower is better)
- Exactly ONE blind evaluation on test.parquet
- Emits artifacts to models/tuned/electricity/
"""

import json
from pathlib import Path
import time
from typing import Dict, Any, List
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBRegressor

from src.tuning.tuning_utils import (
    compute_regression_metrics,
    compute_improvement,
    load_baseline_benchmark,
)
from src.utils.config_loader import get_project_root
from src.utils.logger import logger


class ElectricityTuning:
    DATASET_ID = "electricity"
    TARGET_COL = "power_kw"
    PRIMARY_METRIC = "wape"

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.root = get_project_root()
        self.data_dir = self.root / "models" / "processed" / self.DATASET_ID
        self.out_dir = self.root / "models" / "tuned" / self.DATASET_ID

    def load_data(self):
        """Loads model-ready preprocessed chronological partitions."""
        train_df = pd.read_parquet(self.data_dir / "train.parquet")
        val_df = pd.read_parquet(self.data_dir / "val.parquet")
        test_df = pd.read_parquet(self.data_dir / "test.parquet")

        exclude = [self.TARGET_COL, "timestamp"]
        feature_cols = [c for c in train_df.columns if c not in exclude]

        X_train = train_df[feature_cols].values
        y_train = train_df[self.TARGET_COL].values

        X_val = val_df[feature_cols].values
        y_val = val_df[self.TARGET_COL].values

        X_test = test_df[feature_cols].values
        y_test = test_df[self.TARGET_COL].values

        return {
            "feature_cols": feature_cols,
            "X_train": X_train,
            "y_train": y_train,
            "X_val": X_val,
            "y_val": y_val,
            "X_test": X_test,
            "y_test": y_test,
        }

    def run_tuning(self, save_artifacts: bool = True) -> Dict[str, Any]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        data = self.load_data()
        baseline = load_baseline_benchmark(self.DATASET_ID)
        baseline_val_score = baseline["val_score"]
        baseline_test_score = baseline["test_score"]

        logger.info(f"[{self.DATASET_ID}] Starting bounded tuning exploration across chronological windows...")

        candidates = []

        # Bounded XGBoost Regressor exploration
        for n_est in [100, 150, 200]:
            for depth in [5, 6, 8]:
                for lr in [0.03, 0.06, 0.1]:
                    for mcw in [1, 3]:
                        candidates.append((
                            f"XGB_n{n_est}_d{depth}_lr{lr}_mcw{mcw}",
                            XGBRegressor(
                                n_estimators=n_est,
                                max_depth=depth,
                                learning_rate=lr,
                                min_child_weight=mcw,
                                subsample=0.85,
                                colsample_bytree=0.85,
                                random_state=self.random_state,
                                n_jobs=-1,
                            ),
                            "XGBoost",
                        ))

        logger.info(f"[{self.DATASET_ID}] Evaluating {len(candidates)} bounded configurations on validation window...")

        val_results = []
        trained_models = {}

        for name, model, family in candidates:
            model.fit(data["X_train"], data["y_train"])
            trained_models[name] = model

            val_pred = model.predict(data["X_val"])
            metrics = compute_regression_metrics(data["y_val"], val_pred)
            metrics["candidate_name"] = name
            metrics["model_family"] = family
            val_results.append(metrics)

        df_comparison = pd.DataFrame(val_results)

        # Select validation champion based on lowest WAPE (and lowest MAE)
        df_sorted = df_comparison.sort_values(by=[self.PRIMARY_METRIC, "mae"], ascending=True)
        champion_name = df_sorted.iloc[0]["candidate_name"]
        champion_model = trained_models[champion_name]
        champion_val_metrics = df_sorted.iloc[0].to_dict()
        tuned_val_score = champion_val_metrics[self.PRIMARY_METRIC]

        # Check meaningful improvement: WAPE reduction > 0.001 (0.1% absolute)
        val_delta = baseline_val_score - tuned_val_score  # Positive is improvement
        is_accepted = val_delta > 0.001
        decision_status = "TUNED_MODEL_ACCEPTED" if is_accepted else "BASELINE_RETAINED"

        logger.info(f"[{self.DATASET_ID}] Champion: {champion_name} (Val WAPE={tuned_val_score:.4f}, Baseline={baseline_val_score:.4f}, Reduction={val_delta:+.4f}) -> {decision_status}")

        # ONE Final Test Evaluation on Holdout test.parquet
        test_pred = champion_model.predict(data["X_test"])
        final_test_metrics = compute_regression_metrics(data["y_test"], test_pred)
        final_test_metrics["champion_model"] = champion_name
        final_test_metrics["primary_selection_metric"] = self.PRIMARY_METRIC
        tuned_test_score = final_test_metrics[self.PRIMARY_METRIC]

        improvement = compute_improvement(
            baseline_val=baseline_val_score,
            tuned_val=tuned_val_score,
            baseline_test=baseline_test_score,
            tuned_test=tuned_test_score,
            higher_is_better=False,
        )
        improvement["decision_status"] = decision_status
        improvement["meaningful_improvement_threshold_wape"] = 0.001

        tuning_config = {
            "dataset_id": self.DATASET_ID,
            "target": self.TARGET_COL,
            "primary_metric": self.PRIMARY_METRIC,
            "champion_model_name": champion_name,
            "model_type": champion_model.__class__.__name__,
            "model_params": {k: str(v) for k, v in champion_model.get_params().items()},
            "random_seed": self.random_state,
            "tuning_performed": True,
            "configurations_evaluated": len(candidates),
        }

        tuning_metadata = {
            "dataset_id": self.DATASET_ID,
            "task": "electricity_consumption_forecasting",
            "epistemic_status": "REAL_INDUSTRIAL_TELEMETRY",
            "features_count": len(data["feature_cols"]),
            "train_rows": len(data["X_train"]),
            "val_rows": len(data["X_val"]),
            "test_rows": len(data["X_test"]),
            "configurations_evaluated": len(candidates),
            "champion_model": champion_name,
            "decision_status": decision_status,
            "baseline_val_score_wape": baseline_val_score,
            "tuned_val_score_wape": tuned_val_score,
            "baseline_test_score_wape": baseline_test_score,
            "tuned_test_score_wape": tuned_test_score,
            "val_abs_improvement": improvement["val_abs_improvement"],
            "val_rel_improvement_pct": improvement["val_rel_improvement_pct"],
            "test_abs_delta": improvement["test_abs_delta"],
            "test_rel_delta_pct": improvement["test_rel_delta_pct"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "tuning_status": "COMPLETED",
        }

        if save_artifacts:
            df_comparison.to_csv(self.out_dir / "model_comparison.csv", index=False)
            with open(self.out_dir / "validation_metrics.json", "w") as f:
                json.dump(val_results, f, indent=2)
            with open(self.out_dir / "final_test_metrics.json", "w") as f:
                json.dump(final_test_metrics, f, indent=2)
            with open(self.out_dir / "tuning_config.json", "w") as f:
                json.dump(tuning_config, f, indent=2)
            with open(self.out_dir / "tuning_metadata.json", "w") as f:
                json.dump(tuning_metadata, f, indent=2)
            with open(self.out_dir / "improvement_summary.json", "w") as f:
                json.dump(improvement, f, indent=2)
            joblib.dump(champion_model, self.out_dir / "locked_tuned_model.joblib")
            logger.info(f"[{self.DATASET_ID}] Tuned artifacts saved to {self.out_dir}")

        return {
            "comparison": df_comparison,
            "champion": champion_name,
            "val_metrics": champion_val_metrics,
            "test_metrics": final_test_metrics,
            "improvement": improvement,
            "metadata": tuning_metadata,
        }


if __name__ == "__main__":
    tuner = ElectricityTuning()
    res = tuner.run_tuning()
    print("Electricity Tuning Complete:", res["champion"], res["improvement"])
