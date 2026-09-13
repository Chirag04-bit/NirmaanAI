"""
NirmaanAI Industrial IoT 2040 Remaining Useful Life Tuning & Validation
Task: Remaining Useful Life Continuous Regression in Days (Remaining_Useful_Life_days)

Priority 7 Tuning Module
- Preserves target quarantine (Failure_Within_7_Days and Machine_ID excluded)
- 350,000 train machines, 75,000 validation machines
- Bounded deterministic hyperparameter exploration on XGBoost and Random Forest Regressors
- Model selection strictly on val.parquet via RMSE (lower is better)
- Exactly ONE blind evaluation on test.parquet
- Emits artifacts to models/tuned/industrial_iot_rul/
"""

import json
from pathlib import Path
import time
from typing import Dict, Any, List
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

from src.tuning.tuning_utils import (
    compute_regression_metrics,
    compute_improvement,
    load_baseline_benchmark,
)
from src.utils.config_loader import get_project_root
from src.utils.logger import logger


class IndustrialIoIRULTuning:
    DATASET_ID = "industrial_iot_rul"
    TARGET_COL = "Remaining_Useful_Life_days"
    PRIMARY_METRIC = "rmse"

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.root = get_project_root()
        self.data_dir = self.root / "models" / "processed" / "industrial_iot" / "rul"
        self.out_dir = self.root / "models" / "tuned" / self.DATASET_ID

    def load_data(self):
        """Loads model-ready preprocessed partitions."""
        train_df = pd.read_parquet(self.data_dir / "train.parquet")
        val_df = pd.read_parquet(self.data_dir / "val.parquet")
        test_df = pd.read_parquet(self.data_dir / "test.parquet")

        exclude = [self.TARGET_COL, "Machine_ID", "Failure_Within_7_Days"]
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

        logger.info(f"[{self.DATASET_ID}] Starting bounded tuning exploration across 350,000 machines...")

        candidates = []

        # 1. Bounded XGBoost Regressor
        for depth in [5, 6, 7]:
            for lr in [0.05, 0.1]:
                for n_est in [100, 150]:
                    candidates.append((
                        f"XGB_d{depth}_lr{lr}_n{n_est}",
                        XGBRegressor(
                            n_estimators=n_est,
                            max_depth=depth,
                            learning_rate=lr,
                            subsample=0.85,
                            colsample_bytree=0.85,
                            random_state=self.random_state,
                            n_jobs=-1,
                        ),
                        "XGBoost",
                    ))

        # 2. Bounded Random Forest Regressor
        for depth in [14, 18]:
            for min_leaf in [2, 4]:
                candidates.append((
                    f"RF_d{depth}_l{min_leaf}",
                    RandomForestRegressor(
                        n_estimators=100,
                        max_depth=depth,
                        min_samples_leaf=min_leaf,
                        random_state=self.random_state,
                        n_jobs=-1,
                    ),
                    "RandomForest",
                ))

        logger.info(f"[{self.DATASET_ID}] Evaluating {len(candidates)} bounded configurations on validation machines...")

        val_results = []
        trained_models = {}

        for name, model, family in candidates:
            logger.info(f"[{self.DATASET_ID}] Fitting {name}...")
            model.fit(data["X_train"], data["y_train"])
            trained_models[name] = model

            val_pred = model.predict(data["X_val"])
            metrics = compute_regression_metrics(data["y_val"], val_pred)
            metrics["candidate_name"] = name
            metrics["model_family"] = family
            val_results.append(metrics)

        df_comparison = pd.DataFrame(val_results)

        # Select validation champion based on lowest RMSE
        df_sorted = df_comparison.sort_values(by=[self.PRIMARY_METRIC, "mae"], ascending=True)
        champion_name = df_sorted.iloc[0]["candidate_name"]
        champion_model = trained_models[champion_name]
        champion_val_metrics = df_sorted.iloc[0].to_dict()
        tuned_val_score = champion_val_metrics[self.PRIMARY_METRIC]

        # Check meaningful improvement: RMSE reduction > 0.50 days
        val_delta = baseline_val_score - tuned_val_score  # Positive is improvement
        is_accepted = val_delta > 0.50
        decision_status = "TUNED_MODEL_ACCEPTED" if is_accepted else "BASELINE_RETAINED"

        logger.info(f"[{self.DATASET_ID}] Champion: {champion_name} (Val RMSE={tuned_val_score:.2f}, Baseline={baseline_val_score:.2f}, Reduction={val_delta:+.2f}) -> {decision_status}")

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
        improvement["meaningful_improvement_threshold_days"] = 0.50

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
            "task": "remaining_useful_life_regression_days",
            "epistemic_status": "CONTROLLED_INDUSTRIAL_SIMULATOR",
            "features_count": len(data["feature_cols"]),
            "quarantined_columns": ["Failure_Within_7_Days", "Machine_ID"],
            "train_rows": len(data["X_train"]),
            "val_rows": len(data["X_val"]),
            "test_rows": len(data["X_test"]),
            "configurations_evaluated": len(candidates),
            "champion_model": champion_name,
            "decision_status": decision_status,
            "baseline_val_score_rmse": baseline_val_score,
            "tuned_val_score_rmse": tuned_val_score,
            "baseline_test_score_rmse": baseline_test_score,
            "tuned_test_score_rmse": tuned_test_score,
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
    tuner = IndustrialIoIRULTuning()
    res = tuner.run_tuning()
    print("Industrial IoT RUL Tuning Complete:", res["champion"], res["improvement"])
