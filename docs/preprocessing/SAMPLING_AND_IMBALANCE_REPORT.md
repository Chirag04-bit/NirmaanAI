# NirmaanAI — Sampling & Class Imbalance Analysis Report

**Project**: NirmaanAI — AI-Powered Manufacturing Intelligence & Decision Platform  
**Location**: `C:\NIRMAAN AI`  
**Phase**: Strict Dataset-by-Dataset Cleaning, Preprocessing & Sampling  
**Status**: COMPLETE, ISOLATED & VERIFIED  

---

## 1. Executive Summary

In industrial artificial intelligence, synthetic resampling (such as naive SMOTE or random oversampling) is frequently misapplied, leading to artificial boundary distortion, severe variance inflation, and data leakage across temporal regimes.

**Strict Scientific Mandate**:
1. **Train-Only Application**: When sampling is justified, it is applied **strictly to the training partition**. Validation and test partitions retain their unadulterated natural class distributions to ensure honest evaluation.
2. **Prohibition on Continuous Trajectories**: For temporal time-series (UCI Electricity, Textile Loom, Synthetic Factory) and run-to-failure degradation (NASA C-MAPSS), sampling is **strictly prohibited** (`SAMPLING_NOT_REQUIRED`), as random interpolation destroys causal dynamics.
3. **Transparent Alternatives**: For imbalanced classification tasks, alternative algorithmic solutions (such as class weighting and focal loss) are documented alongside oversampling.

---

## 2. Dataset-by-Dataset Imbalance & Sampling Analysis

### 2.1. Dataset 01: UCI AI4I 2020 Predictive Maintenance
- **Task**: Binary machine failure classification.
- **Natural Class Distribution**: $339 / 10,000 = 3.39\%$ failure rate ($9,661$ healthy).
- **Training Set Imbalance**: $237$ failures vs. $6,763$ healthy tools ($3.39\%$).
- **Is Sampling Required?**: **YES (Investigated & Prepared)**.
- **Scientifically Plausible Methods**:
  1. *Class Weighting*: Set `scale_pos_weight = 28.5` in gradient boosted trees or `class_weight='balanced'` in logistic models.
  2. *Random Over-Sampling*: Sample minority failures with replacement to match healthy tools.
  3. *Focal Loss*: Dynamically down-weight well-classified healthy instances during gradient backpropagation.
- **Risks**: High duplication in oversampling may cause tree splits to memorize specific tool wear points.
- **Applied Action**: Generated `training_sampled.parquet` (13,526 rows, 50% positive) for training benchmarks only. Validation (1,500 rows, 3.40%) and Test (1,500 rows, 3.40%) remain completely untouched.

### 2.2. Dataset 02: NASA C-MAPSS FD001 Turbofan Run-to-Failure
- **Task**: Remaining Useful Life continuous regression.
- **Is Sampling Required?**: **NO — `SAMPLING_NOT_REQUIRED`**.
- **Reason**: C-MAPSS is a continuous run-to-failure degradation sequence across 100 engines. Synthetic oversampling, cycle dropping, or SMOTE is scientifically invalid and destroys temporal continuity.
- **Sampling Allowed?**: **STRICTLY PROHIBITED**. Validation and test partitions are pristine.

### 2.3. Dataset 03: UCI SECOM Semiconductor Manufacturing
- **Task**: In-line wafer defect classification.
- **Natural Class Distribution**: $104 / 1,567 = 6.64\%$ defect rate ($1,463$ passing wafers).
- **Training Set Imbalance**: $73$ defects vs. $1,023$ passes ($6.66\%$).
- **Is Sampling Required?**: **YES (Investigated & Prepared)**.
- **Scientifically Plausible Methods**:
  1. *Cost-Sensitive Loss*: Penalize false negatives by a factor of $14.0\times$.
  2. *Random Over-Sampling on Train*: Sample minority defective wafers to match passes.
- **Risks of SMOTE**: With 436 dimensions and only 73 defective samples, SMOTE creates synthetic points in vast empty feature space, generating non-physical wafer sensor combinations. Random oversampling on train is significantly safer.
- **Applied Action**: Generated `training_sampled.parquet` (2,046 rows, 50% defect rate). Validation (235 wafers, 6.38%) and Test (236 wafers, 6.78%) retain natural distributions.

### 2.4. Dataset 04: UCI Electricity Load Diagrams (Client MT_124)
- **Task**: Continuous hourly electrical load forecasting.
- **Is Sampling Required?**: **NO — `SAMPLING_NOT_REQUIRED`**.
- **Reason**: Time-series forecasting depends entirely on autocorrelation, lag structure, and diurnal seasonality. Synthetic timestamp sampling destroys time-series causality.
- **Sampling Allowed?**: **STRICTLY PROHIBITED**.

### 2.5. Dataset 05: Industrial IoT Simulator 2040
- **Task A: Failure Classification (`Failure_Within_7_Days`)**:
  - Natural Distribution: $30,032 / 500,000 = 6.01\%$ failure rate.
  - Training Imbalance: $21,022$ failures vs. $328,978$ healthy machines in 350,000 training records ($6.01\%$).
  - Sampling Decision: Train-only random oversampling investigated and generated as `training_sampled.parquet` (657,956 rows, 50% positive). Validation (75,000 rows, 6.01%) and Test (75,000 rows, 6.01%) retain pristine distributions.
- **Task B: RUL Prediction (`Remaining_Useful_Life_days`)**:
  - Target Type: Continuous regression (0 to 1,000 days).
  - Sampling Decision: **NO — `SAMPLING_NOT_REQUIRED`**. Class sampling is mathematically inapplicable.

### 2.6. Dataset 06: Manufacturing Production Discrete Scheduling
- **Task**: Prospective bottleneck risk prediction.
- **Natural Class Distribution**: $327 / 1,000 = 32.7\%$ bottleneck jobs ($673$ normal jobs).
- **Is Sampling Required?**: **NO — `SAMPLING_NOT_REQUIRED`**.
- **Reason**: The minority class possesses substantial sample support ($32.7\%$ is moderate imbalance). Class weighting (ratio $\approx 2.06$) is sufficient; synthetic alteration would disrupt discrete job-sequence dependencies.

### 2.7. Dataset 07: Manufacturing Process & Defect Quality
- **Task**: Batch quality classification.
- **Natural Class Distribution**: $2,723 / 3,240 = 84.0\%$ defective batches ($517$ pass batches).
- **Minority Class**: Passing/High-Quality batches (~16.0%).
- **Is Sampling Required?**: **NO — `SAMPLING_NOT_REQUIRED`**.
- **Reason**: Training set contains $362$ pass batches out of $2,268$, providing ample statistical support. Class weighting ($5.26\times$ for class 0) is recommended over resampling.

### 2.8. Dataset 08: Textile Manufacturing Loom Telemetry
- **Epistemic Status**: `CONTROLLED_SYNTHETIC`.
- **Is Sampling Required?**: **NO — `SAMPLING_NOT_REQUIRED`**.
- **Reason**: Continuous 1-minute loom telemetry across 5 machines. Random sampling or synthetic injection is prohibited.

### 2.9. Dataset 09: Synthetic Factory Auto-Components (Master Scenario)
- **Epistemic Status**: `CONTROLLED_SYNTHETIC`.
- **Is Sampling Required?**: **NO — `SAMPLING_NOT_REQUIRED`**.
- **Reason**: Deterministic 5-station factory scenario with controlled M2 degradation. Sampling would disrupt physical scenario dynamics.

---

## 3. Sampling Decision Summary Table

| Dataset | Primary Task | Imbalance Rate | Sampling Required? | Selected Method | Applied Scope | Validation / Test Untouched? |
|---|---|---:|---|---|---|---|
| **AI4I 2020** | Binary Classification | 3.39% failures | YES | Random Over-Sampling + Weighting | Train Only (`training_sampled.parquet`) | **YES (Untouched)** |
| **NASA C-MAPSS** | Continuous RUL | N/A (Regression) | NO | `SAMPLING_NOT_REQUIRED` | None | **YES (Untouched)** |
| **UCI SECOM** | Wafer Classification | 6.64% defects | YES | Random Over-Sampling + Weighting | Train Only (`training_sampled.parquet`) | **YES (Untouched)** |
| **UCI Electricity** | Time-Series Forecasting | N/A (Load curve) | NO | `SAMPLING_NOT_REQUIRED` | None | **YES (Untouched)** |
| **Industrial IoT (Failure)** | Binary Classification | 6.01% failures | YES | Random Over-Sampling + Weighting | Train Only (`training_sampled.parquet`) | **YES (Untouched)** |
| **Industrial IoT (RUL)** | Continuous RUL | N/A (Regression) | NO | `SAMPLING_NOT_REQUIRED` | None | **YES (Untouched)** |
| **Production** | Bottleneck Prediction | 32.7% bottlenecks | NO | `SAMPLING_NOT_REQUIRED` (Weighting advised) | None | **YES (Untouched)** |
| **Defects** | Quality Classification | 84.0% defects | NO | `SAMPLING_NOT_REQUIRED` (Weighting advised) | None | **YES (Untouched)** |
| **Textile** | Anomaly Telemetry | N/A (Time series) | NO | `SAMPLING_NOT_REQUIRED` | None | **YES (Untouched)** |
| **Synthetic Factory** | Factory Scenario | N/A (Scenario stream)| NO | `SAMPLING_NOT_REQUIRED` | None | **YES (Untouched)** |
