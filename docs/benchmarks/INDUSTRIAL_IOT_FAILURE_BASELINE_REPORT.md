# Industrial IoT 2040 Machine Failure Baseline Model Benchmark Report

**Project**: NirmaanAI — AI-Powered Manufacturing Intelligence & Decision Platform  
**Dataset ID**: `industrial_iot_failure`  
**Epistemic Status**: `CONTROLLED_INDUSTRIAL_SIMULATOR`  
**Task**: 7-Day Machine Failure Binary Classification  
**Target Column**: `Failure_Within_7_Days` (Prevalence: ~6.0%)  
**Features Count**: 26 mechanical, thermal, fluid, and operational stress indicators  
**Quarantined Columns**: `Remaining_Useful_Life_days` (Dual-task leak prevention), `Machine_ID` (Zero entity leakage)  
**Tuning Status**: `NOT_STARTED`

---

## 1. Scale & Entity-Leakage Verification

Audited and verified: 500,000 unique machine entities with exactly 1 snapshot per machine. Zero machine overlap across splits.

| Partition | Total Machines | Normal (0) | Failure (1) | Failure Rate | Sampling Strategy |
|---|---|---|---|---|---|
| **Train (Natural)** | 350,000 | 328,995 | 21,005 | 6.00% | Natural Empirical Distribution |
| **Train (Sampled)** | 657,990 | 328,995 | 328,995 | 50.00% | Train-Only Random Over-Sampling |
| **Validation** | 75,000 | 70,495 | 4,505 | 6.01% | Independent Machines Validation |
| **Test (Holdout)** | 75,000 | 70,495 | 4,505 | 6.01% | Final Blind Evaluation (Evaluated Once) |

---

## 2. Experimental Candidate Baselines

Nine candidate variations evaluated on validation machines (75,000 rows):

| Candidate Model | Sampling Strategy | Validation PR-AUC | Validation ROC-AUC | Validation Recall | Validation F1 |
|---|---|---|---|---|---|
| **Logistic_Regression_Sampled** | **RandomOverSampling_TrainOnly** | **0.7522** | **0.9829** | **0.9698** | **0.6175** |
| Logistic_Regression_Weighted | Class_Weighted (`balanced`) | 0.7521 | 0.9829 | 0.9698 | 0.6175 |
| Logistic_Regression_Natural | Natural | 0.7480 | 0.9828 | 0.5842 | 0.6811 |
| XGBoost_Sampled | RandomOverSampling_TrainOnly | 0.7250 | 0.9780 | 0.8210 | 0.6540 |
| XGBoost_Weighted | Class_Weighted (`scale_pos_weight=15.6`) | 0.7241 | 0.9778 | 0.8190 | 0.6535 |
| XGBoost_Natural | Natural | 0.7180 | 0.9772 | 0.6120 | 0.6720 |
| Random_Forest_Sampled | RandomOverSampling_TrainOnly | 0.7105 | 0.9750 | 0.8100 | 0.6480 |
| Random_Forest_Weighted | Class_Weighted (`balanced`) | 0.7098 | 0.9748 | 0.8090 | 0.6475 |
| Random_Forest_Natural | Natural | 0.7012 | 0.9740 | 0.5980 | 0.6620 |

---

## 3. Validation Champion Selection

- **Locked Champion**: `Logistic_Regression_Sampled`
- **Primary Metric**: Validation PR-AUC = `0.7522`
- **Secondary Metric**: Validation ROC-AUC = `0.9829`, Recall = `0.9698`
- **Epistemic Insight**: In the Industrial IoT simulator, mechanical failure transitions are governed by smooth, continuous degradation functions of temperature, vibration, and fluid levels. Linear decision boundaries under balanced class sampling efficiently capture the degradation hyperplane with 97% recall and minimal overfitting on 350,000 records.

---

## 4. Final Blind Holdout Evaluation (Test Machines)

Evaluated **exactly once** on `test.parquet` (75,000 independent machines):

| Metric | Score | Industrial Interpretation |
|---|---|---|
| **PR-AUC** | **0.7596** | Robust, high precision across the warning operating spectrum |
| **ROC-AUC** | **0.9832** | Exceptional discriminative ranking ability |
| **Recall** | **0.9711 (97.1%)** | 4,375 out of 4,505 catastrophic equipment breakdowns prevented |
| **Precision** | **0.4548 (45.5%)** | Safe early warning ratio: 1 genuine failure per 2.2 maintenance alerts |
| **F1-Score** | **0.6195** | Strong predictive maintenance operational trade-off |
| **Accuracy** | **0.9283 (92.8%)** | Sound plant-wide operational performance |

### Test Confusion Matrix
```
                 Predicted Normal (0)    Predicted Failure (1)
Actual Normal:          65,250                    5,245
Actual Failure:            130                    4,375
```
- **Catastrophic Misses (False Negatives)**: Only 130 machines out of 75,000!

---

## 5. Artifacts Locked

- `models/benchmarks/industrial_iot_failure/model_comparison.csv`
- `models/benchmarks/industrial_iot_failure/validation_metrics.json`
- `models/benchmarks/industrial_iot_failure/final_test_metrics.json`
- `models/benchmarks/industrial_iot_failure/training_config.json`
- `models/benchmarks/industrial_iot_failure/benchmark_metadata.json`
- `models/benchmarks/industrial_iot_failure/locked_baseline_model.joblib`
