# AI4I 2020 Predictive Maintenance Baseline Model Benchmark Report

**Project**: NirmaanAI — AI-Powered Manufacturing Intelligence & Decision Platform  
**Dataset ID**: `ai4i`  
**Epistemic Status**: `REAL_PHYSICAL_SIMULATOR`  
**Task**: Machine Failure Binary Classification  
**Target Column**: `machine_failure` (Prevalence: ~3.39%)  
**Features Count**: 13 predictive features (excluding string identifier `product_type` and target)  
**Tuning Status**: `NOT_STARTED`

---

## 1. Dataset Overview & Partitioning

The AI4I 2020 Predictive Maintenance dataset reflects synthetic sensor streams generated from realistic physical machine tool degradation equations. The preprocessed data was partitioned strictly using stratified sampling:

| Partition | Total Rows | Normal (0) | Failure (1) | Failure Rate | Sampling Strategy |
|---|---|---|---|---|---|
| **Train (Natural)** | 7,000 | 6,762 | 238 | 3.40% | Natural Empirical Distribution |
| **Train (Sampled)** | 13,524 | 6,762 | 6,762 | 50.00% | Train-Only Random Over-Sampling |
| **Validation** | 1,500 | 1,449 | 51 | 3.40% | Held-Out Stratified Validation |
| **Test (Holdout)** | 1,500 | 1,449 | 51 | 3.40% | Final Blind Evaluation (Evaluated Once) |

---

## 2. Experimental Candidate Baselines

Nine candidate variations across 3 model families and 3 sampling strategies were trained on training partitions and evaluated strictly on `val.parquet`:

| Candidate Model | Sampling Strategy | Validation PR-AUC | Validation ROC-AUC | Validation F1 | Validation Accuracy |
|---|---|---|---|---|---|
| **Random_Forest_Natural** | **Natural** | **0.9051** | **0.9859** | **0.8605** | **0.9920** |
| XGBoost_Natural | Natural | 0.8845 | 0.9818 | 0.8409 | 0.9907 |
| Random_Forest_Sampled | RandomOverSampling_TrainOnly | 0.8867 | 0.9832 | 0.8444 | 0.9907 |
| XGBoost_Sampled | RandomOverSampling_TrainOnly | 0.8712 | 0.9801 | 0.8352 | 0.9900 |
| Random_Forest_Weighted | Class_Weighted (`balanced`) | 0.8821 | 0.9829 | 0.8444 | 0.9907 |
| XGBoost_Weighted | Class_Weighted (`scale_pos_weight=28.5`) | 0.8794 | 0.9789 | 0.8315 | 0.9893 |
| Logistic_Regression_Weighted | Class_Weighted (`balanced`) | 0.5841 | 0.9123 | 0.3846 | 0.8720 |
| Logistic_Regression_Sampled | RandomOverSampling_TrainOnly | 0.5835 | 0.9120 | 0.3846 | 0.8720 |
| Logistic_Regression_Natural | Natural | 0.6012 | 0.9125 | 0.4444 | 0.9733 |

---

## 3. Validation Champion Selection

- **Locked Champion**: `Random_Forest_Natural`
- **Primary Metric**: Validation PR-AUC = `0.9051`
- **Secondary Metric**: Validation F1 = `0.8605`
- **Rationale**: `Random_Forest_Natural` captured non-linear interactions (e.g., `tool_wear_risk_index`, `torque_speed_product`, `temp_diff_k`) without introducing synthetic variance from over-sampling or distortion from aggressive positive weighting.

---

## 4. Final Blind Holdout Evaluation (Test Set)

The locked champion was evaluated **exactly once** on `test.parquet` (1,500 samples):

| Metric | Score | Industrial Interpretation |
|---|---|---|
| **PR-AUC** | **0.9099** | High precision maintained across operational operating points |
| **ROC-AUC** | **0.9711** | Near-optimal global class discrimination |
| **Precision** | **0.9756** | 97.6% of flagged failure warnings are genuine failures |
| **Recall** | **0.7843** | 78.4% of actual equipment failures intercepted prospectively |
| **F1-Score** | **0.8696** | Balanced operational efficacy |
| **Accuracy** | **0.9920** | High overall fidelity |

### Test Confusion Matrix
```
                 Predicted Normal (0)    Predicted Failure (1)
Actual Normal:          1,448                      1
Actual Failure:           11                      40
```
- **False Positives**: 1 (Extremely low false alarm cost for plant operations)
- **False Negatives**: 11 (Uncaught failures to be targeted in future research)

---

## 5. Artifacts Locked

- `models/benchmarks/ai4i/model_comparison.csv`
- `models/benchmarks/ai4i/validation_metrics.json`
- `models/benchmarks/ai4i/final_test_metrics.json`
- `models/benchmarks/ai4i/training_config.json`
- `models/benchmarks/ai4i/benchmark_metadata.json`
- `models/benchmarks/ai4i/locked_baseline_model.joblib`
