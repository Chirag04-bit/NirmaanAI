"""
NirmaanAI UCI SECOM Baseline Model Benchmarking
Task: Semiconductor Wafer Defect Binary Classification

Evaluates:
- Logistic Regression (L2 regularized), Random Forest, XGBoost
- Variations:
  1. Natural Training
  2. Training-only Random Over-Sampling
  3. Class Weighting (scale_pos_weight=14.0 / class_weight='balanced')
Protocol:
- Validation comparison strictly on val.parquet
- Champion selected via validation PR-AUC / Recall
- Champion evaluated ONCE on holdout test.parquet
"""

import json
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier

from src.benchmarks.eval_utils import compute_classification_metrics
from src.utils.config_loader import get_project_root
from src.utils.logger import logger


class SECOMBenchmark:
    DATASET_ID = "secom"
    TARGET_COL = "target_defect"
    PRIMARY_METRIC = "pr_auc"

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.root = get_project_root()
        self.data_dir = self.root / "models" / "processed" / self.DATASET_ID
        self.out_dir = self.root / "models" / "benchmarks" / self.DATASET_ID

    def load_data(self):
        """Loads model-ready preprocessed partitions."""
        train_df = pd.read_parquet(self.data_dir / "train.parquet")
        val_df = pd.read_parquet(self.data_dir / "val.parquet")
        test_df = pd.read_parquet(self.data_dir / "test.parquet")
        sampled_train_df = pd.read_parquet(self.data_dir / "training_sampled.parquet")

        exclude = [self.TARGET_COL, "Time"]
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

    def run_benchmark(self, save_artifacts: bool = True):
        self.out_dir.mkdir(parents=True, exist_ok=True)
        data = self.load_data()

        candidates = [
            # 1. Natural Training
            ("Logistic_Regression_Natural", LogisticRegression(max_iter=1000, random_state=self.random_state), "Natural", False),
            ("Random_Forest_Natural", RandomForestClassifier(n_estimators=100, random_state=self.random_state), "Natural", False),
            ("XGBoost_Natural", XGBClassifier(n_estimators=100, random_state=self.random_state, eval_metric="logloss"), "Natural", False),

            # 2. Over-Sampled Training (Train Only)
            ("Logistic_Regression_Sampled", LogisticRegression(max_iter=1000, random_state=self.random_state), "RandomOverSampling_TrainOnly", True),
            ("Random_Forest_Sampled", RandomForestClassifier(n_estimators=100, random_state=self.random_state), "RandomOverSampling_TrainOnly", True),
            ("XGBoost_Sampled", XGBClassifier(n_estimators=100, random_state=self.random_state, eval_metric="logloss"), "RandomOverSampling_TrainOnly", True),

            # 3. Class-Weighted Training
            ("Logistic_Regression_Weighted", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=self.random_state), "Class_Weighted", False),
            ("Random_Forest_Weighted", RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=self.random_state), "Class_Weighted", False),
            ("XGBoost_Weighted", XGBClassifier(n_estimators=100, scale_pos_weight=14.0, random_state=self.random_state, eval_metric="logloss"), "Class_Weighted", False),
        ]

        val_results = []
        trained_models = {}

        logger.info(f"[{self.DATASET_ID}] Evaluating candidate baselines on validation wafers...")
        for name, model, strategy, is_sampled in candidates:
            if is_sampled:
                X_tr, y_tr = data["X_train_samp"], data["y_train_samp"]
            else:
                X_tr, y_tr = data["X_train_nat"], data["y_train_nat"]

            model.fit(X_tr, y_tr)
            trained_models[name] = model

            # Validation evaluation
            y_val_pred = model.predict(data["X_val"])
            y_val_prob = model.predict_proba(data["X_val"]) if hasattr(model, "predict_proba") else None
            metrics = compute_classification_metrics(data["y_val"], y_val_pred, y_val_prob)
            metrics["model_name"] = name
            metrics["sampling_strategy"] = strategy
            val_results.append(metrics)

        df_comparison = pd.DataFrame(val_results)

        # Select validation champion based on PR-AUC (with Recall as tie-breaker)
        df_sorted = df_comparison.sort_values(by=[self.PRIMARY_METRIC, "recall"], ascending=False)
        champion_name = df_sorted.iloc[0]["model_name"]
        champion_model = trained_models[champion_name]
        champion_val_metrics = df_sorted.iloc[0].to_dict()

        logger.info(f"[{self.DATASET_ID}] Validation Champion: {champion_name} (PR-AUC={champion_val_metrics['pr_auc']:.4f}, Recall={champion_val_metrics['recall']:.4f})")

        # ONE Final Test Evaluation on Holdout Wafers
        y_test_pred = champion_model.predict(data["X_test"])
        y_test_prob = champion_model.predict_proba(data["X_test"]) if hasattr(champion_model, "predict_proba") else None
        final_test_metrics = compute_classification_metrics(data["y_test"], y_test_pred, y_test_prob)
        final_test_metrics["champion_model"] = champion_name
        final_test_metrics["primary_selection_metric"] = self.PRIMARY_METRIC

        training_config = {
            "dataset_id": self.DATASET_ID,
            "target": self.TARGET_COL,
            "primary_metric": self.PRIMARY_METRIC,
            "champion_model_name": champion_name,
            "model_type": champion_model.__class__.__name__,
            "model_params": {k: str(v) for k, v in champion_model.get_params().items()},
            "random_seed": self.random_state,
            "tuning_performed": False,
        }

        benchmark_metadata = {
            "dataset_id": self.DATASET_ID,
            "task": "wafer_defect_classification",
            "epistemic_status": "REAL_SEMICONDUCTOR_INLINE_SENSORS",
            "features_count": len(data["feature_cols"]),
            "train_rows": len(data["X_train_nat"]),
            "train_sampled_rows": len(data["X_train_samp"]),
            "val_rows": len(data["X_val"]),
            "test_rows": len(data["X_test"]),
            "champion_model": champion_name,
            "validation_score_pr_auc": champion_val_metrics["pr_auc"],
            "test_score_pr_auc": final_test_metrics["pr_auc"],
            "historical_phase6_comparison": "Historical Phase 6: Random Forest / XGBoost defect classifier baseline preserved.",
            "tuning_status": "NOT_STARTED",
        }

        if save_artifacts:
            df_comparison.to_csv(self.out_dir / "model_comparison.csv", index=False)
            with open(self.out_dir / "validation_metrics.json", "w") as f:
                json.dump(val_results, f, indent=2)
            with open(self.out_dir / "final_test_metrics.json", "w") as f:
                json.dump(final_test_metrics, f, indent=2)
            with open(self.out_dir / "training_config.json", "w") as f:
                json.dump(training_config, f, indent=2)
            with open(self.out_dir / "benchmark_metadata.json", "w") as f:
                json.dump(benchmark_metadata, f, indent=2)
            joblib.dump(champion_model, self.out_dir / "locked_baseline_model.joblib")
            logger.info(f"[{self.DATASET_ID}] Benchmark artifacts locked and saved to {self.out_dir}")

        return {
            "comparison": df_comparison,
            "champion": champion_name,
            "val_metrics": champion_val_metrics,
            "test_metrics": final_test_metrics,
        }


if __name__ == "__main__":
    benchmark = SECOMBenchmark()
    res = benchmark.run_benchmark()
    print("SECOM Benchmark Complete:", res["champion"], res["test_metrics"])

