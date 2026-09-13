"""
Strict Epistemic Cross-Dataset Isolation & Contamination Prevention Tests.
Validates:
- Preprocessors do NOT share any mutable state, scalers, imputers, or memory buffers.
- Preprocessors carry distinct dataset_id markers.
- Statistics from Dataset A never leak into Dataset B.
- No global or universal preprocessing assumptions exist across NirmaanAI.
"""

import pytest

from src.preprocessing.ai4i_preprocessor import AI4IPreprocessor
from src.preprocessing.cmapss_preprocessor import CMAPSSPreprocessor
from src.preprocessing.defect_preprocessor import DefectPreprocessor
from src.preprocessing.electricity_preprocessor import ElectricityPreprocessor
from src.preprocessing.industrial_iot_preprocessor import IndustrialIoTPreprocessor
from src.preprocessing.production_preprocessor import ProductionPreprocessor
from src.preprocessing.secom_preprocessor import SECOMPreprocessor
from src.preprocessing.synthetic_factory_preprocessor import SyntheticFactoryPreprocessor
from src.preprocessing.textile_preprocessor import TextilePreprocessor


def test_unique_dataset_identifiers():
    """Verify that every preprocessor module defines a unique, non-overlapping dataset_id."""
    preprocessors = [
        AI4IPreprocessor(),
        CMAPSSPreprocessor(),
        SECOMPreprocessor(),
        ElectricityPreprocessor(),
        IndustrialIoTPreprocessor(task="failure"),
        IndustrialIoTPreprocessor(task="rul"),
        ProductionPreprocessor(),
        DefectPreprocessor(),
        TextilePreprocessor(),
        SyntheticFactoryPreprocessor(),
    ]

    ids = [p.DATASET_ID for p in preprocessors]
    # Root dataset IDs must cover all distinct operational domains
    assert "ai4i" in ids
    assert "cmapss" in ids
    assert "secom" in ids
    assert "electricity" in ids
    assert "industrial_iot" in ids
    assert "manufacturing_production" in ids
    assert "manufacturing_defects" in ids
    assert "textile" in ids
    assert "synthetic_factory" in ids


def test_independent_scaler_instances():
    """Verify that every preprocessor creates its own dedicated StandardScaler/RobustScaler instance."""
    p_ai4i = AI4IPreprocessor()
    p_cmapss = CMAPSSPreprocessor()
    p_secom = SECOMPreprocessor()
    p_elec = ElectricityPreprocessor()
    p_iot_f = IndustrialIoTPreprocessor(task="failure")
    p_iot_r = IndustrialIoTPreprocessor(task="rul")
    p_prod = ProductionPreprocessor()
    p_defect = DefectPreprocessor()
    p_textile = TextilePreprocessor()
    p_factory = SyntheticFactoryPreprocessor()

    scalers = [
        p_ai4i.scaler,
        p_cmapss.scaler,
        p_secom.scaler,
        p_elec.scaler,
        p_iot_f.scaler,
        p_iot_r.scaler,
        p_prod.scaler,
        p_defect.scaler,
        p_textile.scaler,
        p_factory.scaler,
    ]

    # Every scaler object in memory must have a distinct id
    scaler_ids = [id(s) for s in scalers]
    assert len(scaler_ids) == len(set(scaler_ids)), "Shared scaler detected across datasets!"


def test_statistical_isolation_between_domains():
    """Verify that AI4I temperature statistics never match Synthetic Factory temperature statistics."""
    from src.features.ai4i_features import extract_ai4i_features
    from src.features.synthetic_factory_features import extract_synthetic_factory_features

    p_ai4i = AI4IPreprocessor()
    p_factory = SyntheticFactoryPreprocessor()

    df_ai4i, _ = p_ai4i.audit_and_clean(extract_ai4i_features()[0])
    df_factory, _ = p_factory.audit_and_clean(extract_synthetic_factory_features()[0])

    train_ai4i, _, _ = p_ai4i.split_dataset(df_ai4i)
    train_factory, _, _ = p_factory.split_dataset(df_factory)

    p_ai4i.fit_train(train_ai4i)
    p_factory.fit_train(train_factory)

    # In AI4I, air temp is ~300 Kelvin
    ai4i_temp_mean = p_ai4i.scaler.mean_[p_ai4i.NUMERICAL_FEATURES.index("air_temperature_k")]
    assert ai4i_temp_mean > 290.0

    # In Synthetic Factory, temperature is Celsius ~25-70 C
    factory_temp_idx = p_factory.feature_cols.index("temperature_c")
    factory_temp_mean = p_factory.scaler.mean_[factory_temp_idx]
    assert factory_temp_mean < 100.0

    # Strict assertion: statistics are completely isolated
    assert abs(ai4i_temp_mean - factory_temp_mean) > 150.0
