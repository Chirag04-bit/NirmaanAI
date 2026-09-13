"""
NirmaanAI Dataset-Specific Preprocessing Registry
Orchestrates isolated execution of dataset-specific cleaning, preprocessing, splitting, and sampling.

Strict Isolation Rules:
- The registry NEVER merges, pools, or concatenates datasets.
- Each pipeline executes strictly within its own domain-specific preprocessor class.
- All fitted preprocessing parameters (scalers, imputers) are fit strictly on training partitions.
- Prevents cross-dataset contamination and asserts dataset_id integrity.
"""

from pathlib import Path
from typing import Callable, Dict, List, Optional
from src.preprocessing.ai4i_preprocessor import AI4IPreprocessor
from src.preprocessing.cmapss_preprocessor import CMAPSSPreprocessor
from src.preprocessing.defect_preprocessor import DefectPreprocessor
from src.preprocessing.electricity_preprocessor import ElectricityPreprocessor
from src.preprocessing.industrial_iot_preprocessor import IndustrialIoTPreprocessor
from src.preprocessing.production_preprocessor import ProductionPreprocessor
from src.preprocessing.secom_preprocessor import SECOMPreprocessor
from src.preprocessing.synthetic_factory_preprocessor import SyntheticFactoryPreprocessor
from src.preprocessing.textile_preprocessor import TextilePreprocessor
from src.utils.logger import logger


class PreprocessingRegistry:
    """Central registry of independent, dataset-specific preprocessing pipelines."""

    PIPELINES: Dict[str, Callable] = {
        "ai4i": lambda: AI4IPreprocessor().run_pipeline(),
        "cmapss": lambda: CMAPSSPreprocessor().run_pipeline(),
        "secom": lambda: SECOMPreprocessor().run_pipeline(),
        "electricity": lambda: ElectricityPreprocessor().run_pipeline(),
        "industrial_iot_failure": lambda: IndustrialIoTPreprocessor(task="failure").run_pipeline(),
        "industrial_iot_rul": lambda: IndustrialIoTPreprocessor(task="rul").run_pipeline(),
        "industrial_iot": lambda: {
            "failure": IndustrialIoTPreprocessor(task="failure").run_pipeline(),
            "rul": IndustrialIoTPreprocessor(task="rul").run_pipeline(),
        },
        "manufacturing_production": lambda: ProductionPreprocessor().run_pipeline(),
        "manufacturing_defects": lambda: DefectPreprocessor().run_pipeline(),
        "textile": lambda: TextilePreprocessor().run_pipeline(),
        "synthetic_factory": lambda: SyntheticFactoryPreprocessor().run_pipeline(),
    }

    @classmethod
    def list_datasets(cls) -> List[str]:
        """Returns the list of registered dataset keys."""
        return list(cls.PIPELINES.keys())

    @classmethod
    def process(
        cls,
        dataset_name: str,
        save_artifacts: bool = True,
        output_dir: Optional[Path] = None,
    ) -> Dict:
        """
        Executes preprocessing for a single specified dataset.
        Enforces strict dataset ID validation.
        """
        key = dataset_name.lower().strip()
        if key not in cls.PIPELINES:
            raise KeyError(
                f"Dataset '{dataset_name}' not registered. Registered: {cls.list_datasets()}"
            )

        logger.info(f"--- Running isolated preprocessing pipeline for: {key} ---")
        pipeline_func = cls.PIPELINES[key]
        return pipeline_func()

    @classmethod
    def process_all(cls, save_artifacts: bool = True) -> Dict[str, Dict]:
        """
        Executes preprocessing across all datasets independently.
        Never shares state or combines dataframes.
        """
        results = {}
        # Core datasets to process
        core_keys = [
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
        for key in core_keys:
            try:
                res = cls.process(key, save_artifacts=save_artifacts)
                results[key] = {"status": "SUCCESS", "report": res}
            except Exception as e:
                logger.error(f"Error preprocessing '{key}': {e}", exc_info=True)
                results[key] = {"status": "FAILED", "error": str(e)}
        return results
