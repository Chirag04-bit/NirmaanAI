"""
NirmaanAI Dataset-Wise Feature Extraction Registry
Coordinates isolated, reproducible feature extraction and artifact generation across all approved datasets.

Strict Architectural Rules:
- The registry NEVER merges distinct datasets into an artificial combined matrix.
- Each dataset executes within its own isolated, scientifically justified domain pipeline.
- Generates standard audit artifacts under models/features/<dataset_key>/:
  1. feature_dictionary.csv
  2. extracted_features.parquet
  3. metadata.json
"""

import json
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple
import pandas as pd

from src.features.ai4i_features import extract_ai4i_features
from src.features.cmapss_features import extract_cmapss_features
from src.features.defect_features import extract_defect_features
from src.features.electricity_features import extract_electricity_features
from src.features.industrial_iot_features import extract_industrial_iot_features
from src.features.production_features import extract_production_features
from src.features.secom_features import extract_secom_features
from src.features.synthetic_factory_features import extract_synthetic_factory_features
from src.features.textile_features import extract_textile_features
from src.utils.config_loader import get_project_root
from src.utils.logger import logger


class FeatureRegistry:
    """Central registry of isolated dataset-wise feature engineering pipelines."""

    PIPELINES: Dict[str, Callable] = {
        "ai4i": extract_ai4i_features,
        "cmapss": extract_cmapss_features,
        "secom": extract_secom_features,
        "electricity": extract_electricity_features,
        "industrial_iot": extract_industrial_iot_features,
        "manufacturing_production": extract_production_features,
        "manufacturing_defects": extract_defect_features,
        "textile": extract_textile_features,
        "synthetic_factory": extract_synthetic_factory_features,
    }

    @classmethod
    def list_supported_datasets(cls) -> List[str]:
        """Returns the list of registered dataset keys."""
        return list(cls.PIPELINES.keys())

    list_datasets = list_supported_datasets

    @classmethod
    def extract(
        cls,
        dataset_name: str,
        save_artifacts: bool = True,
        output_dir: Optional[Path] = None,
        **kwargs,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
        """
        Executes feature extraction for a single specified dataset.
        Saves artifacts to models/features/<dataset_name>/ if save_artifacts is True.
        """
        key = dataset_name.lower().strip()
        if key not in cls.PIPELINES:
            raise KeyError(
                f"Dataset '{dataset_name}' not registered. Supported datasets: {cls.list_supported_datasets()}"
            )

        extractor = cls.PIPELINES[key]
        logger.info(f"Running feature extraction pipeline for: {key}")
        df_features, feature_dict, metadata = extractor(**kwargs)

        if save_artifacts:
            root = get_project_root()
            base_out = output_dir or (root / "models" / "features" / key)
            base_out.mkdir(parents=True, exist_ok=True)

            # 1. Save feature dictionary
            dict_path = base_out / "feature_dictionary.csv"
            feature_dict.to_csv(dict_path, index=False)

            # 2. Save extracted features as Parquet
            parquet_path = base_out / "extracted_features.parquet"
            # Ensure timestamps are compatible with Parquet
            df_to_save = df_features.copy()
            for col in df_to_save.select_dtypes(include=["datetime64[ns, UTC]", "datetime64[ns]"]).columns:
                df_to_save[col] = df_to_save[col].astype(str)
            df_to_save.to_parquet(parquet_path, index=False)

            # 3. Save metadata JSON
            meta_path = base_out / "metadata.json"
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Saved feature artifacts for '{key}' to {base_out}")

        return df_features, feature_dict, metadata

    @classmethod
    def extract_all(
        cls,
        save_artifacts: bool = True,
        output_dir: Optional[Path] = None,
    ) -> Dict[str, Dict]:
        """
        Runs feature extraction across all registered datasets independently.
        Returns a dictionary of execution metadata per dataset.
        """
        all_metadata = {}
        for key in cls.list_supported_datasets():
            logger.info(f"--- Processing dataset pipeline: {key} ---")
            try:
                _, _, meta = cls.extract(key, save_artifacts=save_artifacts, output_dir=output_dir)
                all_metadata[key] = meta
            except Exception as e:
                logger.error(f"Error extracting features for '{key}': {e}", exc_info=True)
                all_metadata[key] = {"error": str(e), "status": "FAILED"}
        return all_metadata
