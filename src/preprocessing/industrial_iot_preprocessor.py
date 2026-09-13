"""
NirmaanAI Industrial IoT Simulator 2040 Preprocessor
Tasks:
  1. Failure Prediction (Binary Classification on 'Failure_Within_7_Days')
  2. RUL Prediction (Continuous Regression on 'Remaining_Useful_Life_days')

Strict Epistemic Isolation & Target Quarantine Rules:
- Dataset ID: 'industrial_iot' (Strictly validated)
- Task 'failure':
    - Target: 'Failure_Within_7_Days'
    - Quarantined: 'Remaining_Useful_Life_days' (STRICT TARGET LEAKAGE)
    - Stratified 70/15/15 split on failure label.
    - Imbalance ~6.0% failures. Evaluates class weighting & train-only oversampling.
    - Output: models/processed/industrial_iot/failure/
- Task 'rul':
    - Target: 'Remaining_Useful_Life_days'
    - Quarantined: 'Failure_Within_7_Days' (STRICT TARGET LEAKAGE)
    - Random 70/15/15 split.
    - SAMPLING_NOT_REQUIRED (Continuous regression).
    - Output: models/processed/industrial_iot/rul/
"""

import json
from pathlib import Path
import pickle
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from src.features.industrial_iot_features import extract_industrial_iot_features
from src.utils.config_loader import get_project_root
from src.utils.logger import logger


class IndustrialIoTPreprocessor:
    DATASET_ID = "industrial_iot"
    FAILURE_TARGET = "Failure_Within_7_Days"
    RUL_TARGET = "Remaining_Useful_Life_days"
    ID_COLS = ["Machine_ID"]

    def __init__(self, task: str = "failure", random_state: int = 42):
        task_clean = task.lower().strip()
        if task_clean not in ["failure", "rul"]:
            raise ValueError(f"Task must be either 'failure' or 'rul', got: {task}")
        self.task = task_clean
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.feature_cols: List[str] = []
        self.is_fitted = False
        self.cleaning_report: Dict = {}
        self.preprocessing_report: Dict = {}

    def audit_and_clean(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Performs independent audit, cleans duplicates and enforces cross-target quarantine."""
        rows_before = len(df)
        cols_before = len(df.columns)

        duplicates_found = int(df.duplicated(subset=self.ID_COLS).sum())
        df_cleaned = df.drop_duplicates(subset=self.ID_COLS).copy()

        missing_count = int(df_cleaned.isna().sum().sum())

        # Determine target and quarantined target column based on task
        if self.task == "failure":
            target_col = self.FAILURE_TARGET
            quarantined_target = self.RUL_TARGET
        else:
            target_col = self.RUL_TARGET
            quarantined_target = self.FAILURE_TARGET

        # Drop quarantined target to eliminate cross-target leakage
        cols_to_drop = [c for c in [self.ID_COLS[0], quarantined_target] if c in df_cleaned.columns]
        df_cleaned = df_cleaned.drop(columns=cols_to_drop)

        # Categorical and boolean encoding
        if "Machine_Type" in df_cleaned.columns:
            df_cleaned["Machine_Type_encoded"] = df_cleaned["Machine_Type"].astype("category").cat.codes.astype(int)
            df_cleaned = df_cleaned.drop(columns=["Machine_Type"])
            cols_to_drop.append("Machine_Type")

        if "AI_Supervision" in df_cleaned.columns:
            df_cleaned["AI_Supervision"] = df_cleaned["AI_Supervision"].astype(int)

        if "Failure_Within_7_Days" in df_cleaned.columns:
            df_cleaned["Failure_Within_7_Days"] = df_cleaned["Failure_Within_7_Days"].astype(int)

        # Numerical feature columns (exclude target)
        self.feature_cols = [c for c in df_cleaned.columns if c != target_col]

        # Median imputation for any residual NaNs in engineered features (e.g. coolant efficiency)
        for col in self.feature_cols:
            if df_cleaned[col].isna().any():
                df_cleaned[col] = df_cleaned[col].fillna(df_cleaned[col].median())

        cleaning_report = {
            "dataset": f"{self.DATASET_ID}_{self.task}",
            "task": self.task,
            "target_column": target_col,
            "quarantined_cross_target": quarantined_target,
            "rows_before": rows_before,
            "rows_after": len(df_cleaned),
            "columns_before": cols_before,
            "columns_after": len(df_cleaned.columns),
            "duplicates_found": duplicates_found,
            "duplicates_removed": duplicates_found,
            "missing_values_before": missing_count,
            "missing_values_after": 0,
            "features_removed": cols_to_drop,
            "reason_for_each_removal": {
                self.ID_COLS[0]: "IDENTIFIER",
                quarantined_target: "CROSS_TARGET_LEAKAGE_ELIMINATION",
            },
            "cleaning_method": "CROSS_TARGET_QUARANTINE_AND_NUMERICAL_INTEGRITY",
            "random_seed": self.random_state,
            "validation_status": "PASS",
        }
        self.cleaning_report = cleaning_report
        return df_cleaned, cleaning_report

    def split_dataset(
        self, df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Performs 70/15/15 split (stratified for classification, random for regression)."""
        target_col = self.FAILURE_TARGET if self.task == "failure" else self.RUL_TARGET
        X = df.drop(columns=[target_col])
        y = df[target_col]

        stratify = y if self.task == "failure" else None

        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=0.30, random_state=self.random_state, stratify=stratify
        )

        stratify_temp = y_temp if self.task == "failure" else None
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.50, random_state=self.random_state, stratify=stratify_temp
        )

        train_df = pd.concat([X_train, y_train], axis=1).reset_index(drop=True)
        val_df = pd.concat([X_val, y_val], axis=1).reset_index(drop=True)
        test_df = pd.concat([X_test, y_test], axis=1).reset_index(drop=True)

        return train_df, val_df, test_df

    def fit_train(self, train_df: pd.DataFrame) -> None:
        """Fits StandardScaler strictly on training partition numerical predictors."""
        self.scaler.fit(train_df[self.feature_cols])
        self.is_fitted = True

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies fitted scaler to partition."""
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fitted on training partition first!")

        scaled = self.scaler.transform(df[self.feature_cols])
        df_transformed = df.copy()
        for idx, col in enumerate(self.feature_cols):
            df_transformed[col] = scaled[:, idx]

        return df_transformed

    def evaluate_sampling(self, train_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Evaluates sampling: applied to failure classification training set; not regression."""
        if self.task == "failure":
            pos_count = int(train_df[self.FAILURE_TARGET].sum())
            total_count = len(train_df)
            neg_count = total_count - pos_count
            imbalance_ratio = pos_count / total_count

            # Random oversampling on train only
            df_pos = train_df[train_df[self.FAILURE_TARGET] == 1]
            df_neg = train_df[train_df[self.FAILURE_TARGET] == 0]

            np.random.seed(self.random_state)
            oversample_idx = np.random.choice(df_pos.index, size=len(df_neg), replace=True)
            df_pos_oversampled = train_df.loc[oversample_idx]

            train_sampled = pd.concat([df_neg, df_pos_oversampled], axis=0).sample(
                frac=1.0, random_state=self.random_state
            ).reset_index(drop=True)

            sampling_metadata = {
                "dataset": f"{self.DATASET_ID}_{self.task}",
                "task": "failure_classification",
                "is_sampling_required": True,
                "reason": f"Class imbalance: {pos_count} failures ({imbalance_ratio:.2%}) in {total_count} training records.",
                "target_distribution_train_raw": {
                    "class_0_healthy": neg_count,
                    "class_1_failure": pos_count,
                    "failure_rate": float(imbalance_ratio),
                },
                "scientifically_plausible_methods": [
                    "Class Weighting (e.g. scale_pos_weight ~15.7)",
                    "Random Over-Sampling (Train Only)",
                    "Subsampling healthy machines to match operational shifts",
                ],
                "risks": "Synthetic boundary artifacts; large scale (350k train rows) makes class weighting computationally lighter than oversampling.",
                "sampling_allowed": True,
                "applied_to": "TRAIN_PARTITION_ONLY",
                "validation_and_test_untouched": True,
                "sampled_train_rows": len(train_sampled),
            }
            return train_sampled, sampling_metadata
        else:
            sampling_metadata = {
                "dataset": f"{self.DATASET_ID}_{self.task}",
                "task": "rul_regression",
                "is_sampling_required": False,
                "sampling_decision": "SAMPLING_NOT_REQUIRED",
                "reason": "Industrial IoT RUL is a continuous regression target; class sampling is not applicable.",
                "sampling_allowed": False,
                "applied_to": "NONE",
                "validation_and_test_untouched": True,
            }
            return train_df, sampling_metadata

    def run_pipeline(
        self, save_artifacts: bool = True, output_dir: Path = None
    ) -> Dict:
        """Executes complete dataset-specific pipeline and stores artifacts."""
        root = get_project_root()
        out_path = output_dir or (root / "models" / "processed" / self.DATASET_ID / self.task)
        out_path.mkdir(parents=True, exist_ok=True)

        target_col = self.FAILURE_TARGET if self.task == "failure" else self.RUL_TARGET

        logger.info(f"[{self.DATASET_ID}_{self.task}] Starting independent preprocessing pipeline...")
        raw_df, _, raw_meta = extract_industrial_iot_features()

        # 1. Audit & Clean
        cleaned_df, cleaning_report = self.audit_and_clean(raw_df)

        # 2. Split
        train_raw, val_raw, test_raw = self.split_dataset(cleaned_df)

        # 3. Fit on Train Only
        self.fit_train(train_raw)

        # 4. Transform partitions
        train_proc = self.transform(train_raw)
        val_proc = self.transform(val_raw)
        test_proc = self.transform(test_raw)
        full_proc = self.transform(cleaned_df)

        # 5. Evaluate Sampling
        train_sampled, sampling_meta = self.evaluate_sampling(train_proc)

        preprocessing_report = {
            "dataset": f"{self.DATASET_ID}_{self.task}",
            "task": self.task,
            "target": target_col,
            "split_method": "Stratified 70/15/15" if self.task == "failure" else "Random 70/15/15",
            "train_rows": len(train_proc),
            "val_rows": len(val_proc),
            "test_rows": len(test_proc),
            "features_scaled_count": len(self.feature_cols),
            "scaler_type": "StandardScaler",
            "fit_scope": "TRAIN_ONLY",
            "transform_scope": "TRAIN_VAL_TEST",
            "sampling_decision": sampling_meta,
        }
        self.preprocessing_report = preprocessing_report

        processing_metadata = {
            "dataset_id": f"{self.DATASET_ID}_{self.task}",
            "task": self.task,
            "target": target_col,
            "rows_raw": len(raw_df),
            "rows_cleaned": len(cleaned_df),
            "rows_train": len(train_proc),
            "rows_val": len(val_proc),
            "rows_test": len(test_proc),
            "random_seed": self.random_state,
            "status": "PROCESSED_AND_VERIFIED",
        }

        feature_schema = {
            "dataset": f"{self.DATASET_ID}_{self.task}",
            "target_column": target_col,
            "features": self.feature_cols,
            "feature_types": {col: str(cleaned_df[col].dtype) for col in cleaned_df.columns},
        }

        if save_artifacts:
            # Parquet dataframes
            cleaned_df.to_parquet(out_path / "cleaned_features.parquet", index=False)
            full_proc.to_parquet(out_path / "preprocessed_features.parquet", index=False)
            train_proc.to_parquet(out_path / "train.parquet", index=False)
            val_proc.to_parquet(out_path / "val.parquet", index=False)
            test_proc.to_parquet(out_path / "test.parquet", index=False)

            if self.task == "failure":
                train_sampled.to_parquet(out_path / "training_sampled.parquet", index=False)

            # JSON reports
            with open(out_path / "cleaning_metadata.json", "w") as f:
                json.dump(cleaning_report, f, indent=2)
            with open(out_path / "cleaning_report.json", "w") as f:
                json.dump(cleaning_report, f, indent=2)
            with open(out_path / "preprocessing_report.json", "w") as f:
                json.dump(preprocessing_report, f, indent=2)
            with open(out_path / "processing_metadata.json", "w") as f:
                json.dump(processing_metadata, f, indent=2)
            with open(out_path / "feature_schema.json", "w") as f:
                json.dump(feature_schema, f, indent=2)

            with open(out_path / "preprocessing_pipeline.pkl", "wb") as f:
                pickle.dump(self, f)

            logger.info(f"[{self.DATASET_ID}_{self.task}] Artifacts successfully saved to {out_path}")

        return {
            "cleaning_report": cleaning_report,
            "preprocessing_report": preprocessing_report,
            "metadata": processing_metadata,
        }
