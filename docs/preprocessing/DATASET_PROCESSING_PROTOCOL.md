# NirmaanAI — Dataset Processing Protocol & Governance Architecture

**Project**: NirmaanAI — AI-Powered Manufacturing Intelligence & Decision Platform  
**Location**: `C:\NIRMAAN AI`  
**Phase**: Strict Dataset-by-Dataset Cleaning, Preprocessing & Sampling  
**Status**: APPROVED & LOCKED  

---

## 1. Governance Principles

To maintain scientific integrity across enterprise manufacturing AI, the following 8-step protocol is enforced on every dataset entering NirmaanAI:

```
RAW SOURCE (Immutable)
        ↓
STEP 1: Checksum & Immutability Verification
        ↓
STEP 2: Independent Domain Audit (Units, Physical Bounds, Gaps)
        ↓
STEP 3: Strict Leakage Quarantine (Target, Identity & Post-Event Features)
        ↓
STEP 4: Dataset-Specific Train / Validation / Test Splitting
        ↓
STEP 5: Preprocessing Fitting STRICTLY on Training Partition
        ↓
STEP 6: Sampling Analysis & Alternative Formulation (Train ONLY)
        ↓
STEP 7: Model-Ready Artifact Serialization (Parquet, JSON, PKL)
        ↓
STEP 8: Test Suite Validation & Epistemic Cross-Dataset Isolation Audit
```

---

## 2. Detailed Protocol Specifications

### Step 1: Checksum & Immutability Verification
- Source raw files in `DATASET/` and `data/` are strictly read-only.
- The reference operational loss checksum (`34B12582B32D81E3121429C55EBF74E8`) must be verified before and after any batch execution.
- Any modification to raw source files aborts execution immediately.

### Step 2: Independent Domain Audit
- No pooled assumptions across datasets.
- Numerical features are checked against physical boundaries (Kelvin vs. Celsius, positive torque, non-negative electrical load, ISO vibration limits).
- Missingness is categorized: MCAR (Missing Completely at Random), MAR, or structural.

### Step 3: Strict Leakage Quarantine
- Target surrogates (e.g. AI4I specific breakdown modes `TWF`, `HDF`, `PWF`, `OSF`, `RNF`) are quarantined from predictor sets.
- Cross-target leakage between dual-task datasets (e.g. Industrial IoT Failure vs. RUL) is completely eliminated.
- Post-event diagnostic observations (e.g. actual completion delays, realized cycle ratios) are excluded from prospective dispatch-time models.

### Step 4: Dataset-Specific Splitting
- Split selection is strictly dictated by data topology:
  - **Stratified Split**: For discrete cross-sectional classification (AI4I, SECOM, Defects).
  - **Grouped Split**: For multi-entity trajectories to prevent intra-entity contamination (C-MAPSS engines 1–70 train, 71–85 val, 86–100 test).
  - **Chronological Split**: For continuous time-series to ensure $t_{\text{train}} < t_{\text{val}} < t_{\text{test}}$ (UCI Electricity, Textile, Synthetic Factory).

### Step 5: Fit on Train Only
- Scaler parameters ($\mu, \sigma$, medians, quantiles) and imputer fill values are computed **strictly on the training partition**.
- Preprocessors transform validation and test sets using the pre-fitted parameters without recalculating.
- Fitting on all data is an automatic test failure.

### Step 6: Sampling on Train Only
- Severe class imbalance is documented with multiple scientifically grounded alternatives (class weighting, cost-sensitive learning, focal loss, oversampling).
- If an oversampled training set is exported (`training_sampled.parquet`), it applies **strictly to the training partition**.
- Validation and test partitions remain 100% untouched to ensure authentic generalization evaluation.
- Time-series and run-to-failure streams are prohibited from synthetic resampling.

### Step 7: Model-Ready Artifact Serialization
- Every dataset exports standardized model-ready artifacts into `models/processed/<dataset>/`:
  - `cleaned_features.parquet`
  - `preprocessed_features.parquet`
  - `train.parquet`, `val.parquet`, `test.parquet`
  - `training_sampled.parquet` (when applicable)
  - `cleaning_metadata.json`, `cleaning_report.json`
  - `preprocessing_report.json`, `processing_metadata.json`
  - `feature_schema.json`
  - `preprocessing_pipeline.pkl`

### Step 8: Test Suite Validation
- Every preprocessor must pass its dedicated test file in `tests/data_preprocessing/`.
- Cross-dataset isolation test (`test_cross_dataset_isolation.py`) must pass to guarantee zero shared state or pooled memory buffers.
