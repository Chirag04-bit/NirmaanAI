# NirmaanAI — Final Model-Ready Datasets Inventory

**Project**: NirmaanAI — AI-Powered Manufacturing Intelligence & Decision Platform  
**Location**: `C:\NIRMAAN AI`  
**Phase**: Strict Dataset-by-Dataset Cleaning, Preprocessing & Sampling  
**Status**: APPROVED, AUDITED & READY FOR FUTURE MODEL TUNING  

---

## 1. Directory Structure of Model-Ready Artifacts

All model-ready feature sets, partition splits, schemas, and fitted transformation pipelines are stored in:
`C:\NIRMAAN AI\models\processed/`

```
models/processed/
├── ai4i/
│   ├── cleaned_features.parquet
│   ├── preprocessed_features.parquet
│   ├── train.parquet (7,000 rows)
│   ├── val.parquet (1,500 rows)
│   ├── test.parquet (1,500 rows)
│   ├── training_sampled.parquet (13,526 rows)
│   ├── cleaning_metadata.json
│   ├── cleaning_report.json
│   ├── preprocessing_report.json
│   ├── processing_metadata.json
│   ├── feature_schema.json
│   └── preprocessing_pipeline.pkl
├── cmapss/
│   ├── cleaned_features.parquet
│   ├── preprocessed_features.parquet
│   ├── train.parquet (14,484 rows — Engines 1–70)
│   ├── val.parquet (3,091 rows — Engines 71–85)
│   ├── test.parquet (3,056 rows — Engines 86–100)
│   ├── cleaning_metadata.json
│   ├── cleaning_report.json
│   ├── preprocessing_report.json
│   ├── processing_metadata.json
│   ├── feature_schema.json
│   └── preprocessing_pipeline.pkl
├── secom/
│   ├── cleaned_features.parquet
│   ├── preprocessed_features.parquet
│   ├── train.parquet (1,096 rows)
│   ├── val.parquet (235 rows)
│   ├── test.parquet (236 rows)
│   ├── training_sampled.parquet (2,046 rows)
│   ├── cleaning_metadata.json
│   ├── cleaning_report.json
│   ├── preprocessing_report.json
│   ├── processing_metadata.json
│   ├── feature_schema.json
│   └── preprocessing_pipeline.pkl
├── electricity/
│   ├── cleaned_features.parquet
│   ├── preprocessed_features.parquet
│   ├── train.parquet (18,279 rows)
│   ├── val.parquet (3,917 rows)
│   ├── test.parquet (3,917 rows)
│   ├── cleaning_metadata.json
│   ├── cleaning_report.json
│   ├── preprocessing_report.json
│   ├── processing_metadata.json
│   ├── feature_schema.json
│   └── preprocessing_pipeline.pkl
├── industrial_iot/
│   ├── failure/
│   │   ├── cleaned_features.parquet
│   │   ├── preprocessed_features.parquet
│   │   ├── train.parquet (350,000 rows)
│   │   ├── val.parquet (75,000 rows)
│   │   ├── test.parquet (75,000 rows)
│   │   ├── training_sampled.parquet (657,956 rows)
│   │   ├── cleaning_metadata.json
│   │   ├── cleaning_report.json
│   │   ├── preprocessing_report.json
│   │   ├── processing_metadata.json
│   │   ├── feature_schema.json
│   │   └── preprocessing_pipeline.pkl
│   └── rul/
│       ├── cleaned_features.parquet
│       ├── preprocessed_features.parquet
│       ├── train.parquet (350,000 rows)
│       ├── val.parquet (75,000 rows)
│       ├── test.parquet (75,000 rows)
│       ├── cleaning_metadata.json
│       ├── cleaning_report.json
│       ├── preprocessing_report.json
│       ├── processing_metadata.json
│       ├── feature_schema.json
│       └── preprocessing_pipeline.pkl
├── manufacturing_production/
│   ├── cleaned_features.parquet
│   ├── preprocessed_features.parquet
│   ├── train.parquet (700 rows)
│   ├── val.parquet (150 rows)
│   ├── test.parquet (150 rows)
│   ├── cleaning_metadata.json
│   ├── cleaning_report.json
│   ├── preprocessing_report.json
│   ├── processing_metadata.json
│   ├── feature_schema.json
│   └── preprocessing_pipeline.pkl
├── manufacturing_defects/
│   ├── cleaned_features.parquet
│   ├── preprocessed_features.parquet
│   ├── train.parquet (2,268 rows)
│   ├── val.parquet (486 rows)
│   ├── test.parquet (486 rows)
│   ├── cleaning_metadata.json
│   ├── cleaning_report.json
│   ├── preprocessing_report.json
│   ├── processing_metadata.json
│   ├── feature_schema.json
│   └── preprocessing_pipeline.pkl
├── textile/
│   ├── cleaned_features.parquet
│   ├── preprocessed_features.parquet
│   ├── train.parquet (30,240 rows)
│   ├── val.parquet (6,480 rows)
│   ├── test.parquet (6,480 rows)
│   ├── cleaning_metadata.json
│   ├── cleaning_report.json
│   ├── preprocessing_report.json
│   ├── processing_metadata.json
│   ├── feature_schema.json
│   └── preprocessing_pipeline.pkl
└── synthetic_factory/
    ├── cleaned_features.parquet
    ├── preprocessed_features.parquet
    ├── train.parquet (20,415 rows)
    ├── val.parquet (8,750 rows)
    ├── test.parquet (14,035 rows)
    ├── cleaning_metadata.json
    ├── cleaning_report.json
    ├── preprocessing_report.json
    ├── processing_metadata.json
    ├── feature_schema.json
    └── preprocessing_pipeline.pkl
```

---

## 2. Partition & Schema Inventory Table

| Dataset & Task | Predictor Features | Target Column | Train Rows | Val Rows | Test Rows | Sampled Train Rows |
|---|---:|---|---:|---:|---:|---:|
| **AI4I 2020** | 14 | `machine_failure` | 7,000 | 1,500 | 1,500 | 13,526 |
| **NASA C-MAPSS** | 98 | `rul_clipped` | 14,484 | 3,091 | 3,056 | N/A |
| **UCI SECOM** | 436 | `target_defect` | 1,096 | 235 | 236 | 2,046 |
| **UCI Electricity** | 20 | `power_kw` | 18,279 | 3,917 | 3,917 | N/A |
| **Industrial IoT (Failure)** | 27 | `Failure_Within_7_Days` | 350,000 | 75,000 | 75,000 | 657,956 |
| **Industrial IoT (RUL)** | 27 | `Remaining_Useful_Life_days` | 350,000 | 75,000 | 75,000 | N/A |
| **Manufacturing Production** | 14 | `target_is_bottleneck` | 700 | 150 | 150 | N/A |
| **Manufacturing Defects** | 23 | `DefectStatus` | 2,268 | 486 | 486 | N/A |
| **Textile Manufacturing** | 16 | Telemetry stream | 30,240 | 6,480 | 6,480 | N/A |
| **Synthetic Factory** | 20 | Scenario stream | 20,415 | 8,750 | 14,035 | N/A |

---

## 3. Mandatory Verification Checklist

- [x] Raw schema audited independently per dataset
- [x] Missingness audited independently per dataset
- [x] Duplicates audited and verified
- [x] Invalid values checked against physical boundaries
- [x] Outliers analyzed (true degradation signals strictly preserved)
- [x] Target leakage quarantined and audited
- [x] Splits defined strictly by data topology (Stratified, Grouped, Chronological)
- [x] Preprocessing fit strictly on training data
- [x] Preprocessing pipelines serialized to `.pkl`
- [x] Sampling decisions made and documented
- [x] Sampling applied strictly to training partitions only
- [x] Validation and test partitions untouched
- [x] All final model-ready artifacts generated and verified
- [x] Dataset-specific unit and integration tests passed (29 tests)
- [x] Epistemic cross-dataset isolation verified (zero shared state)

---

## 4. Explicit Stopping Point Reminder

> [!IMPORTANT]
> **Zero Model Tuning Performed**: No hyperparameter tuning, GridSearchCV, Optuna trials, or model retraining have taken place. All model-ready feature sets are cleanly partitioned and locked. Awaiting explicit user instruction before proceeding to model tuning.
