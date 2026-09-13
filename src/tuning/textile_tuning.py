"""
NirmaanAI Textile Manufacturing Loom Telemetry Tuning & Validation
Task: Unsupervised Loom Telemetry Anomaly Detection & Degradation Tracking

Priority 9 Tuning Module
- Mathematically defined pre-selection validation metric: Anomaly Degradation Contrast Ratio (ADCR)
  ADCR = |mu_nominal - mu_val_tail| / (sigma_nominal + sigma_val_tail + eps)
  where mu_val_tail represents the mean of the bottom 10% anomaly score tail in validation.
- Bounded deterministic hyperparameter exploration on Isolation Forest, PCA Reconstruction, and Robust Z-score
- Model selection strictly on val.parquet via ADCR
- Exactly ONE blind evaluation on test.parquet
- Emits artifacts to models/tuned/textile/
"""

import json
from pathlib import Path
import time
from typing import Dict, Any, List
import joblib
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from src.tuning.tuning_utils import (
    compute_improvement,
    load_baseline_benchmark,
    PCAReconstructionModel,
    RobustZScoreModel,
)
from src.utils.config_loader import get_project_root
from src.utils.logger import logger



def compute_adcr(train_scores: np.ndarray, val_scores: np.ndarray) -> float:
    """
    Computes the Anomaly Degradation Contrast Ratio (ADCR) mathematically:
    ADCR = |mu_nominal - mu_val_tail| / (sigma_nominal + sigma_val_tail + eps)
    where val_tail is the bottom 10th percentile of scores (most anomalous tail).
    """
    mu_nom = float(np.mean(train_scores))
    sigma_nom = float(np.std(train_scores))

    threshold_tail = np.percentile(val_scores, 10)
    tail_scores = val_scores[val_scores <= threshold_tail]

    mu_tail = float(np.mean(tail_scores)) if len(tail_scores) > 0 else mu_nom
    sigma_tail = float(np.std(tail_scores)) if len(tail_scores) > 0 else sigma_nom

    eps = 1e-6
    adcr = abs(mu_nom - mu_tail) / (sigma_nom + sigma_tail + eps)
    return float(adcr)


class TextileTuning:
    DATASET_ID = "textile"
    PRIMARY_METRIC = "adcr"

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.root = get_project_root()
        self.data_dir = self.root / "models" / "processed" / self.DATASET_ID
        self.out_dir = self.root / "models" / "tuned" / self.DATASET_ID

    def load_data(self):
        train_df = pd.read_parquet(self.data_dir / "train.parquet")
        val_df = pd.read_parquet(self.data_dir / "val.parquet")
        test_df = pd.read_parquet(self.data_dir / "test.parquet")

        exclude = ["reading_id", "machine_id", "timestamp", "timestamp_dt"]
        feature_cols = [c for c in train_df.columns if c not in exclude]

        X_train = train_df[feature_cols].values
        X_val = val_df[feature_cols].values
        X_test = test_df[feature_cols].values

        return {
            "feature_cols": feature_cols,
            "X_train": X_train,
            "X_val": X_val,
            "X_test": X_test,
        }

    def run_tuning(self, save_artifacts: bool = True) -> Dict[str, Any]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        data = self.load_data()
        baseline = load_baseline_benchmark(self.DATASET_ID)

        logger.info(f"[{self.DATASET_ID}] Starting bounded unsupervised tuning using pre-defined ADCR metric...")

        candidates = []

        # 1. Bounded Isolation Forest
        for n_est in [100, 150, 200]:
            for contam in ["auto", 0.02, 0.05]:
                for max_feat in [0.8, 1.0]:
                    candidates.append((
                        f"IF_n{n_est}_c{contam}_f{max_feat}",
                        IsolationForest(
                            n_estimators=n_est,
                            contamination=contam,
                            max_features=max_feat,
                            random_state=self.random_state,
                            n_jobs=-1,
                        ),
                        "IsolationForest",
                    ))

        # 2. Bounded PCA Reconstruction
        for n_comp in [4, 6, 8]:
            candidates.append((
                f"PCA_comp{n_comp}",
                PCAReconstructionModel(n_components=n_comp, random_state=self.random_state),
                "PCAReconstruction",
            ))

        # 3. Robust Z-score
        candidates.append(("Robust_ZScore", RobustZScoreModel(), "RobustZScore"))

        logger.info(f"[{self.DATASET_ID}] Evaluating {len(candidates)} bounded configurations on validation loom telemetry...")

        val_results = []
        trained_models = {}

        # Evaluate baseline model on train & val to get baseline ADCR
        baseline_model_path = self.root / "models" / "benchmarks" / self.DATASET_ID / "locked_baseline_model.joblib"
        baseline_model = joblib.load(baseline_model_path)
        base_tr_scores = baseline_model.score_samples(data["X_train"])
        base_val_scores = baseline_model.score_samples(data["X_val"])
        base_adcr_score = compute_adcr(base_tr_scores, base_val_scores)
        base_test_scores = baseline_model.score_samples(data["X_test"])
        base_test_adcr = compute_adcr(base_tr_scores, base_test_scores)

        for name, model, family in candidates:
            model.fit(data["X_train"])
            trained_models[name] = model

            tr_scores = model.score_samples(data["X_train"])
            val_scores = model.score_samples(data["X_val"])

            adcr = compute_adcr(tr_scores, val_scores)
            metrics = {
                "candidate_name": name,
                "model_family": family,
                "adcr": float(adcr),
                "mean_val_score": float(np.mean(val_scores)),
                "std_val_score": float(np.std(val_scores)),
                "p95_val_score": float(np.percentile(val_scores, 95)),
                "p5_val_score": float(np.percentile(val_scores, 5)),
            }
            val_results.append(metrics)

        df_comparison = pd.DataFrame(val_results)

        # Select validation champion based on highest ADCR
        df_sorted = df_comparison.sort_values(by=[self.PRIMARY_METRIC], ascending=False)
        champion_name = df_sorted.iloc[0]["candidate_name"]
        champion_model = trained_models[champion_name]
        champion_val_metrics = df_sorted.iloc[0].to_dict()
        tuned_val_score = champion_val_metrics[self.PRIMARY_METRIC]

        # Check meaningful improvement: ADCR delta > 0.05
        val_delta = tuned_val_score - base_adcr_score
        is_accepted = val_delta > 0.05
        decision_status = "TUNED_MODEL_ACCEPTED" if is_accepted else "BASELINE_RETAINED"

        logger.info(f"[{self.DATASET_ID}] Champion: {champion_name} (Val ADCR={tuned_val_score:.4f}, Baseline={base_adcr_score:.4f}, Delta={val_delta:+.4f}) -> {decision_status}")

        # ONE Final Test Evaluation on Holdout test.parquet
        champ_tr_scores = champion_model.score_samples(data["X_train"])
        test_scores = champion_model.score_samples(data["X_test"])
        tuned_test_adcr = compute_adcr(champ_tr_scores, test_scores)

        final_test_metrics = {
            "champion_model": champion_name,
            "primary_selection_metric": self.PRIMARY_METRIC,
            "test_adcr": float(tuned_test_adcr),
            "mean_anomaly_score": float(np.mean(test_scores)),
            "std_anomaly_score": float(np.std(test_scores)),
            "p95_anomaly_score": float(np.percentile(test_scores, 95)),
            "p5_anomaly_score": float(np.percentile(test_scores, 5)),
            "min_anomaly_score": float(np.min(test_scores)),
            "max_anomaly_score": float(np.max(test_scores)),
        }

        improvement = compute_improvement(
            baseline_val=base_adcr_score,
            tuned_val=tuned_val_score,
            baseline_test=base_test_adcr,
            tuned_test=tuned_test_adcr,
            higher_is_better=True,
        )
        improvement["decision_status"] = decision_status
        improvement["meaningful_improvement_threshold_adcr"] = 0.05

        tuning_config = {
            "dataset_id": self.DATASET_ID,
            "primary_metric": self.PRIMARY_METRIC,
            "metric_definition": "Anomaly Degradation Contrast Ratio (ADCR) = |mu_nom - mu_tail| / (sigma_nom + sigma_tail + eps)",
            "champion_model_name": champion_name,
            "model_type": champion_model.__class__.__name__,
            "model_params": {k: str(v) for k, v in champion_model.get_params().items()},
            "random_seed": self.random_state,
            "tuning_performed": True,
            "configurations_evaluated": len(candidates),
        }

        tuning_metadata = {
            "dataset_id": self.DATASET_ID,
            "task": "loom_telemetry_anomaly_tracking",
            "epistemic_status": "CONTROLLED_SYNTHETIC",
            "features_count": len(data["feature_cols"]),
            "train_rows": len(data["X_train"]),
            "val_rows": len(data["X_val"]),
            "test_rows": len(data["X_test"]),
            "configurations_evaluated": len(candidates),
            "champion_model": champion_name,
            "decision_status": decision_status,
            "metric_name": "ADCR",
            "baseline_val_score": base_adcr_score,
            "tuned_val_score": tuned_val_score,
            "baseline_test_score": base_test_adcr,
            "tuned_test_score": tuned_test_adcr,
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
    tuner = TextileTuning()
    res = tuner.run_tuning()
    print("Textile Tuning Complete:", res["champion"], res["improvement"])
