# UCI SECOM Semiconductor Wafer Defect Baseline Model Benchmark Report

**Project**: NirmaanAI — AI-Powered Manufacturing Intelligence & Decision Platform  
**Dataset ID**: `secom`  
**Epistemic Status**: `REAL_SEMICONDUCTOR_INLINE_SENSORS`  
**Task**: Semiconductor Wafer Defect Binary Classification  
**Target Column**: `target_defect` (Defect prevalence: ~6.6%)  
**Features Count**: 436 active sensor signals (post-cleaning constant/collinear removal)  
**Tuning Status**: `NOT_STARTED`

---

## 1. High-Dimensional Imbalanced Challenge

UCI SECOM represents an authentic, notoriously challenging fab environment with 436 signals, severe class imbalance (1:14 defect ratio), high sensor noise, and missing observations. 

| Partition | Total Wafers | Normal (0) | Defective (1) | Defect Rate | Sampling Strategy |
|---|---|---|---|---|---|
| **Train (Natural)** | 1,096 | 1,023 | 73 | 6.66% | Natural Imbalanced Train |
| **Train (Sampled)** | 2,046 | 1,023 | 1,023 | 50.00% | Train-Only Random Over-Sampling |
| **Validation** | 235 | 220 | 15 | 6.38% | Held-Out Stratified Validation |
| **Test (Holdout)** | 236 | 220 | 16 | 6.78% | Final Blind Evaluation (Evaluated Once) |

---

## 2. Experimental Candidate Baselines

Nine candidate variations evaluated on `val.parquet`:

| Candidate Model | Sampling Strategy | Validation PR-AUC | Validation ROC-AUC | Validation Recall |
|---|---|---|---|---|
| **XGBoost_Weighted** | **Class_Weighted (`scale_pos_weight=14.0`)** | **0.2669** | **0.7242** | **0.0667** |
| Random_Forest_Weighted | Class_Weighted (`balanced`) | 0.2351 | 0.7011 | 0.0000 |
| XGBoost_Natural | Natural | 0.2214 | 0.6980 | 0.0000 |
| Random_Forest_Natural | Natural | 0.2105 | 0.6874 | 0.0000 |
| Random_Forest_Sampled | RandomOverSampling_TrainOnly | 0.1985 | 0.6721 | 0.0000 |
| XGBoost_Sampled | RandomOverSampling_TrainOnly | 0.1872 | 0.6654 | 0.0667 |
| Logistic_Regression_Weighted | Class_Weighted (`balanced`) | 0.1420 | 0.6120 | 0.4667 |
| Logistic_Regression_Sampled | RandomOverSampling_TrainOnly | 0.1415 | 0.6115 | 0.4667 |
| Logistic_Regression_Natural | Natural | 0.1250 | 0.5890 | 0.0000 |

---

## 3. Validation Champion Selection

- **Locked Champion**: `XGBoost_Weighted`
- **Primary Metric**: Validation PR-AUC = `0.2669`
- **Secondary Metric**: Validation ROC-AUC = `0.7242`
- **Epistemic Finding**: Without hyperparameter tuning, cost-sensitive threshold adjustment, or dimensionality reduction, tree models conservatively predict the majority class under standard default 0.5 decision thresholds, resulting in high accuracy (93.2%) but low default recall. Weighted XGBoost achieved the highest PR-AUC and ROC-AUC separation.

---

## 4. Final Blind Holdout Evaluation (Test Wafers)

Evaluated **exactly once** on `test.parquet` (236 wafers):

| Metric | Score | Industrial Interpretation |
|---|---|---|
| **ROC-AUC** | **0.6807** | Substantial ranking separation above random (0.50) |
| **PR-AUC** | **0.1374** | Doubled precision-recall baseline above empirical prevalence (0.067) |
| **Accuracy** | **0.9322** | Reflects majority class baseline |
| **Recall (at 0.5 threshold)** | **0.0000** | Illustrates uncalibrated threshold behavior prior to tuning |

### Test Confusion Matrix (Default 0.5 Threshold)
```
                 Predicted Normal (0)    Predicted Defective (1)
Actual Normal:           220                        0
Actual Defective:         16                        0
```
*Note: This benchmark floor faithfully documents the raw, un-tuned baseline behavior on high-dimensional sensor data.*

---

## 5. Artifacts Locked

- `models/benchmarks/secom/model_comparison.csv`
- `models/benchmarks/secom/validation_metrics.json`
- `models/benchmarks/secom/final_test_metrics.json`
- `models/benchmarks/secom/training_config.json`
- `models/benchmarks/secom/benchmark_metadata.json`
- `models/benchmarks/secom/locked_baseline_model.joblib`
