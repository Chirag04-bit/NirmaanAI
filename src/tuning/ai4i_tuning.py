"""
NirmaanAI AI4I 2020 Predictive Maintenance Tuning & Validation
Task: Machine Failure Binary Classification (machine_failure)

Priority 4 Tuning Module
- Preserves target and failure mode quarantines (UDI, Product ID, product_type, TWF, HDF, PWF, OSF, RNF)
- Bounded deterministic hyperparameter exploration comparing Natural, Class-Weighted, and Train-Only ROS
- Model selection strictly on val.parquet via PR-AUC
- Validation threshold optimization (freezing threshold before test)
- Exactly ONE blind evaluation on test.parquet
- Emits artifacts to models/tuned/ai4i/
"""

import json
from pathlib import Path
import time
from typing import Dict, Any, List
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier

from src.tuning.tuning_utils import (
    compute_classification_metrics,
    find_optimal_validation_threshold,
    compute_improvement,
    load_baseline_benchmark,
)
from src.utils.config_loader import get_project_root
from src.utils.logger import logger


class AI4ITuning:
    DATASET_ID = "ai4i"
    TARGET_COL = "machine_failure"
    PRIMARY_METRIC = "pr_auc"

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.root = get_project_root()
        self.data_dir = self.root / "models" / "processed" / self.DATASET_ID
        self.out_dir = self.root / "models" / "tuned" / self.DATASET_ID

    def load_data(self):
        """Loads model-ready preprocessed partitions."""
        train_df = pd.read_parquet(self.data_dir / "train.parquet")
        val_df = pd.read_parquet(self.data_dir / "val.parquet")
        test_df = pd.read_parquet(self.data_dir / "test.parquet")
        sampled_train_df = pd.read_parquet(self.data_dir / "training_sampled.parquet")

        exclude = [self.TARGET_COL, "product_type"]
        feature_cols = [c for c in train_df.columns if c not in exclude]

        X_train_nat = train_df[feature_cols].values
        y_train_nat = train_df[self.TARGET_COL].values

        X_train_samp = sampled_train_df[feature_cols].values
        y_train_samp = sampled_train_df[self.TARGET_COL].values

        X_val = val_df[feature_cols].values
        y_val = val_df[self.TARGET_COL].values

        X_test = test_df[feature_cols].values
        y_test = test_df[self.TARGET_COL].values

        return {
            "feature_cols": feature_cols,
            "X_train_nat": X_train_nat,
            "y_train_nat": y_train_nat,
            "X_train_samp": X_train_samp,
            "y_train_samp": y_train_samp,
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

        logger.info(f"[{self.DATASET_ID}] Starting bounded tuning exploration...")

        candidates = []

        # 1. Random Forest bounded grid (Natural & Class-Weighted)
        for n_est in [100, 150, 200]:
            for depth in [8, 12, 16, None]:
                for min_leaf in [1, 2]:
                    for cw in [None, "balanced"]:
                        candidates.append((
                            f"RF_n{n_est}_d{depth}_l{min_leaf}_{cw}_Nat",
                            RandomForestClassifier(
                                n_estimators=n_est,
                                max_depth=depth,
                                min_samples_leaf=min_leaf,
                                class_weight=cw,
                                random_state=self.random_state,
                                n_jobs=-1,
                            ),
                            "RandomForest",
                            f"Natural_{cw}",
                            False,
                        ))

        # 2. XGBoost bounded grid (Natural & Scale-Pos-Weight)
        for depth in [4, 6]:
            for lr in [0.03, 0.08]:
                for spw in [1.0, 10.0, 28.5]:
                    candidates.append((
                        f"XGB_d{depth}_lr{lr}_spw{spw:.1f}_Nat",
                        XGBClassifier(
                            n_estimators=100,
                            max_depth=depth,
                            learning_rate=lr,
                            subsample=0.85,
                            colsample_bytree=0.85,
                            scale_pos_weight=spw,
                            random_state=self.random_state,
                            eval_metric="logloss",
                            n_jobs=-1,
                        ),
                        "XGBoost",
                        f"scale_pos_{spw:.1f}",
                        False,
                    ))

        # 3. Train-Only ROS variations
        for depth in [8, 12]:
            candidates.append((
                f"RF_d{depth}_ROS",
                RandomForestClassifier(
                    n_estimators=150,
                    max_depth=depth,
                    random_state=self.random_state,
                    n_jobs=-1,
                ),
                "RandomForest",
                "RandomOverSampling_TrainOnly",
                True,
            ))

        logger.info(f"[{self.DATASET_ID}] Evaluating {len(candidates)} bounded configurations on validation set...")

        val_results = []
        trained_models = {}
        val_probs = {}

        for name, model, family, strategy, is_sampled in candidates:
            X_tr = data["X_train_samp"] if is_sampled else data["X_train_nat"]
            y_tr = data["y_train_samp"] if is_sampled else data["y_train_nat"]

            model.fit(X_tr, y_tr)
            trained_models[name] = model

            val_prob = model.predict_proba(data["X_val"]) if hasattr(model, "predict_proba") else None
            val_probs[name] = val_prob
            val_pred = (val_prob[:, 1] >= 0.5).astype(int) if val_prob is not None else model.predict(data["X_val"])

            metrics = compute_classification_metrics(data["y_val"], val_pred, val_prob, threshold=0.5)
            metrics["candidate_name"] = name
            metrics["model_family"] = family
            metrics["sampling_strategy"] = strategy
            metrics["is_sampled"] = is_sampled
            val_results.append(metrics)

        df_comparison = pd.DataFrame(val_results)

        # Select validation champion based on PR-AUC
        df_sorted = df_comparison.sort_values(by=[self.PRIMARY_METRIC, "f1"], ascending=False)
        champion_name = df_sorted.iloc[0]["candidate_name"]
        champion_model = trained_models[champion_name]
        champion_val_metrics = df_sorted.iloc[0].to_dict()
        tuned_val_score = champion_val_metrics[self.PRIMARY_METRIC]

        # Optimize validation decision threshold
        champ_val_prob = val_probs[champion_name]
        optimal_thresh, val_f1_opt = find_optimal_validation_threshold(data["y_val"], champ_val_prob, metric_target="f1")
        logger.info(f"[{self.DATASET_ID}] Optimal validation threshold: {optimal_thresh:.2f} (val F1={val_f1_opt:.4f})")

        # Check meaningful improvement: val PR-AUC delta > 0.005
        val_delta = tuned_val_score - baseline_val_score
        is_accepted = val_delta > 0.005
        decision_status = "TUNED_MODEL_ACCEPTED" if is_accepted else "BASELINE_RETAINED"

        logger.info(f"[{self.DATASET_ID}] Champion: {champion_name} (Val PR-AUC={tuned_val_score:.4f}, Baseline={baseline_val_score:.4f}, Delta={val_delta:+.4f}) -> {decision_status}")

        # ONE Final Test Evaluation on Holdout test.parquet
        test_prob = champion_model.predict_proba(data["X_test"]) if hasattr(champion_model, "predict_proba") else None
        test_pred_default = (test_prob[:, 1] >= 0.5).astype(int) if test_prob is not None else champion_model.predict(data["X_test"])
        test_pred_opt = (test_prob[:, 1] >= optimal_thresh).astype(int) if test_prob is not None else test_pred_default

        final_test_metrics = compute_classification_metrics(data["y_test"], test_pred_default, test_prob, threshold=0.5)
        final_test_metrics_opt = compute_classification_metrics(data["y_test"], test_pred_opt, test_prob, threshold=optimal_thresh)

        final_test_metrics["champion_model"] = champion_name
        final_test_metrics["primary_selection_metric"] = self.PRIMARY_METRIC
        final_test_metrics["optimized_threshold_metrics"] = final_test_metrics_opt
        tuned_test_score = final_test_metrics[self.PRIMARY_METRIC]

        improvement = compute_improvement(
            baseline_val=baseline_val_score,
            tuned_val=tuned_val_score,
            baseline_test=baseline_test_score,
            tuned_test=tuned_test_score,
            higher_is_better=True,
        )
        improvement["decision_status"] = decision_status
        improvement["meaningful_improvement_threshold"] = 0.005

        tuning_config = {
            "dataset_id": self.DATASET_ID,
            "target": self.TARGET_COL,
            "primary_metric": self.PRIMARY_METRIC,
            "champion_model_name": champion_name,
            "model_type": champion_model.__class__.__name__,
            "model_params": {k: str(v) for k, v in champion_model.get_params().items()},
            "frozen_operating_threshold": optimal_thresh,
            "random_seed": self.random_state,
            "tuning_performed": True,
            "configurations_evaluated": len(candidates),
        }

        tuning_metadata = {
            "dataset_id": self.DATASET_ID,
            "task": "machine_failure_classification",
            "epistemic_status": "REAL_PHYSICAL_SIMULATOR",
            "features_count": len(data["feature_cols"]),
            "quarantined_columns": ["UDI", "Product ID", "product_type", "TWF", "HDF", "PWF", "OSF", "RNF"],
            "train_rows": len(data["X_train_nat"]),
            "train_sampled_rows": len(data["X_train_samp"]),
            "val_rows": len(data["X_val"]),
            "test_rows": len(data["X_test"]),
            "configurations_evaluated": len(candidates),
            "champion_model": champion_name,
            "decision_status": decision_status,
            "baseline_val_score": baseline_val_score,
            "tuned_val_score": tuned_val_score,
            "baseline_test_score": baseline_test_score,
            "tuned_test_score": tuned_test_score,
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
    tuner = AI4ITuning()
    res = tuner.run_tuning()
    print("AI4I Tuning Complete:", res["champion"], res["improvement"])
