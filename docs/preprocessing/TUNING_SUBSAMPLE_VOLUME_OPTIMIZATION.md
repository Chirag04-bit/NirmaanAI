# NirmaanAI — Tuning Subsample & Dataset Volume Optimization
## Post-Phase-25 Research & Engineering Extension

---

### 1. Motivation
During hyperparameter optimization, model benchmarking, and repeated pair-programming experiments across the 10 industrial manufacturing tasks, training iterations across massive cross-sectional datasets (notably the 500,000-row Industrial IoT datasets with 350,000 training observations) introduce significant computational latency without improving search discovery. 

The purpose of this extension is to introduce a controlled, deterministic **Data Volume Optimization / Tuning Subsample Layer** that dramatically speeds up hyperparameter space exploration while guaranteeing that canonical datasets, full training sets, and holdout test evaluations remain 100% intact and uncorrupted.

---

### 2. Core Architecture: Reduce Computation, Not Evidence

```
                          FULL DATASET
                               ↓
          Dataset-Wise Cleaning & Feature Engineering
                               ↓
              Train / Validation / Test Split
                               ↓
            +------------------+------------------+
            |                                     |
    CANONICAL TRAINING                     VALIDATION & TEST
       (Full 350k rows)                    (Permanently Untouched)
            |
            +---> TUNING SUBSAMPLE ONLY (105k rows)
            |           ↓
            |     Bounded Search Space & Model Selection
            |           ↓
            |     Frozen Champion Configuration
            |           ↓
            +---> FINAL CHAMPION RETRAINING (Full 350k rows)
                        ↓
            SINGLE BLIND TEST EVALUATION (Untouched test.parquet)
```

**Key Principle**:
Subsamples are **computational aids only**. They are never treated as canonical datasets, production data, or new experimental evidence. The final champion is always retrained on the **full available training partition**.

---

### 3. Why Random Row Deletion is Inappropriate
Arbitrary row deletion from canonical datasets destroys experimental reproducibility, alters class prevalence in imbalanced settings, disrupts temporal lag structure, and breaks cross-machine alignment:
1. **Severe Imbalance Sensitivity**: In Industrial IoT Failure, failure prevalence is only 6.0%. Naive random reduction risks dropping rare failure modes or creating high variance across random seeds.
2. **Cross-Sectional Machine Stratification**: Machine types must remain uniformly represented to ensure balanced gradient propagation across equipment categories.
3. **Temporal Causality**: In time-series tasks (Electricity, Textile, Synthetic Factory), random deletion destroys sequential continuity, lag features, and rolling windows.
4. **Scenario Integrity**: In Synthetic Factory, multi-machine (M1–M5) synchronization must be preserved to prevent artificial phase shift anomalies.

---

### 4. Dataset-Wise Subsample Decisions

| Dataset / Task | Canonical Full Train Rows | Tuning Subset Rows | Retention | Sampling Strategy | Justification |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **Industrial IoT Failure** | 350,000 | **105,000** | 30.0% | Deterministic Stratified Joint Class & Machine Type | Preserves exact 6.0% failure rate and 33 machine types; 4.1x faster search. |
| **Industrial IoT RUL** | 350,000 | **105,000** | 30.0% | Deterministic Decile-Binned Distribution-Aware Regression | Preserves full continuous RUL distribution across 33 machine types without temporal distortion. |
| **Electricity Consumption** | 18,279 | **9,140** | 50.0% | Deterministic Contiguous Chronological Window | Preserves exact 15-minute chronological ordering and causal lag structure. |
| **Textile Loom Telemetry** | 30,240 | **15,120** | 50.0% | Synchronized Temporal Stride (stride=2 across looms) | Preserves multi-loom alignment and nominal manifold geometry. |
| **Synthetic Factory Telemetry** | 20,415 | **10,210** | 50.0% | Synchronized Multi-Station Temporal Stride (stride=2 across M1–M5) | Preserves synchronized 10-minute cadence across all 5 stations prior to decision cutoff. |
| **AI4I 2020** | 7,000 | *Kept Full* | 100.0% | Full Data Retained | Compact size (7,000 rows); subsampling risks rare failure mode representation. |
| **NASA C-MAPSS FD001** | 14,130 | *Kept Full* | 100.0% | Full Data Retained | Engine trajectories (Engines 1–70) must remain intact to preserve run-to-failure curves. |
| **UCI SECOM** | 1,096 | *Kept Full* | 100.0% | Full Data Retained | Highly compact (1,096 rows) with only 6.6% defect prevalence. |
| **Manufacturing Production** | 700 | *Kept Full* | 100.0% | Full Data Retained | Dispatch log has only 700 training rows; reduction would degrade ranking quality. |
| **Manufacturing Defects** | 2,268 | *Kept Full* | 100.0% | Full Data Retained | Highly compact (2,268 rows); fits and tunes in under 1 second. |

---

### 5. Detailed Sampling Methodologies

#### A. Industrial IoT Failure Prediction
- **Source**: `models/processed/industrial_iot/failure/train.parquet` (350,000 rows)
- **Target Size**: 105,000 rows (30.0% retention)
- **Algorithm**: Joint stratified sampling across binary target `Failure_Within_7_Days` and categorical feature `Machine_Type_encoded`.
- **Prevalence Preservation**:
  - Full Training Class 1 Prevalence: **6.0063%**
  - Subsample Class 1 Prevalence: **6.0048%** ($\Delta = 0.0015\%$)
  - Machine Type Max Drift: **$< 0.001\%$**
- **Quarantine**: `Machine_ID` dropped; `Remaining_Useful_Life_days` quarantined.

#### B. Industrial IoT Remaining Useful Life (RUL)
- **Source**: `models/processed/industrial_iot/rul/train.parquet` (350,000 rows)
- **Target Size**: 105,000 rows (30.0% retention)
- **Algorithm**: Distribution-aware decile-binned quantile stratification on continuous target `Remaining_Useful_Life_days` combined with `Machine_Type_encoded`.
- **Distribution Preservation**:
  - Full Training Mean RUL: **452.58 days** ($\sigma = 289.03$)
  - Subsample Mean RUL: **452.59 days** ($\sigma = 289.14$) ($\Delta = 0.007\text{ days}$)
  - Machine Type Max Drift: **$< 0.002\%$**
- **Quarantine**: `Machine_ID` dropped; `Failure_Within_7_Days` quarantined.
- **Audit Note**: Cross-sectional fleet snapshot confirmed; zero longitudinal sequence assumed.

#### C. Electricity Consumption Forecasting
- **Source**: `models/processed/electricity/train.parquet` (18,279 rows)
- **Target Size**: 9,140 rows (50.0% retention)
- **Algorithm**: Deterministic contiguous chronological window selecting the most recent 50% of the training timeline.
- **Temporal Guarantee**: Strictly monotonic increasing timestamps; causal lag features (lags 1, 2, 4, 8, 96, 672) remain fully intact; zero random shuffling.

#### D. Textile Loom Telemetry
- **Source**: `models/processed/textile/train.parquet` (30,240 rows)
- **Target Size**: 15,120 rows (50.0% retention)
- **Algorithm**: Deterministic temporal downsampling with stride = 2 across loom groups, maintaining balanced loom representation and sequential ordering.
- **Integrity**: Validation and test partitions containing controlled degradation events remain completely untouched.

#### E. Synthetic Factory Telemetry
- **Source**: `models/processed/synthetic_factory/train.parquet` (20,415 rows)
- **Target Size**: 10,210 rows (50.0% retention)
- **Algorithm**: Synchronized multi-station temporal stride (stride = 2) across machines M1–M5 up to the pre-cutoff boundary (2026-01-15).
- **Scenario Safeguard**: Pre-cutoff training baseline represents the nominal operating envelope; Days 18–21 degradation scenario and `MAINT_0003` remain strictly isolated in prospective holdouts.

---

### 6. Representativeness Audit Summary

Every generated subset is accompanied by `representativeness_audit.json` recording:
1. **Numerical Moments**: Mean, standard deviation, min, max, 25th, 50th, 75th, 95th percentiles, and two-sample Kolmogorov-Smirnov test statistics.
2. **Target Distribution**: Exact class counts and proportions for classification; mean, standard deviation, and median for regression.
3. **Categorical Distributions**: Group-wise proportions and maximum drift metrics.
4. **Epistemic Label**: Formally designated as `CONTROLLED_COMPUTATIONAL_SUBSET`.

---

### 7. Leakage Controls & Integrity
- **Partition Isolation**: Subsets are drawn **strictly from `train.parquet`**. Validation (`val.parquet`) and test (`test.parquet`) partitions are never sampled or contaminated.
- **Identifier Quarantine**: `Machine_ID` is strictly excluded from all IoT training subsets to prevent machine memorization.
- **Cross-Target Quarantine**: RUL is excluded from Failure subsets; Failure labels are excluded from RUL subsets.
- **Temporal Directionality**: Future observations never enter past subsets; chronological ordering is strictly preserved in time-series subsets.

---

### 8. Computational Performance Benefit

Empirical benchmark testing demonstrates substantial speedups during hyperparameter search:

| Task / Model | Full Train Fit Time (350k rows) | Subset Fit Time (105k rows) | Speedup Factor | Time Reduction |
| :--- | :---: | :---: | :---: | :---: |
| **IoT Failure (Logistic Regression)** | 0.800 s | 0.194 s | **4.12x** | **75.7%** |
| **IoT Failure (Tree Ensembles, Est.)** | ~180 s per fold | ~45 s per fold | **~4.0x** | **~75.0%** |
| **IoT RUL (Tree Ensembles, Est.)** | ~240 s per fold | ~60 s per fold | **~4.0x** | **~75.0%** |

---

### 9. Limitations & Operating Policy
1. **Subsets Are Not Ground Truth**: The subsets must never be cited as standalone experimental datasets or production datasets.
2. **Final Retraining Mandatory**: Any champion hyperparameter configuration selected via tuning subsets **must be retrained on the full canonical training set** prior to final test evaluation.
3. **Validation Frozen**: Validation sets must remain full and unaltered to ensure fair, unbiased model comparison.

---

### 10. Reproducibility Instructions
To regenerate all tuning subsets deterministically:
```powershell
python -m src.data_preprocessing.generate_tuning_subsets
```
To run the automated validation test suite:
```powershell
pytest tests/preprocessing/test_tuning_subsample.py -v
```
All outputs are saved to `models/tuning_subsets/<dataset>/` with MD5 checksum verification.
