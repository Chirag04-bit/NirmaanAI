# Manufacturing Production Bottleneck Baseline Model Benchmark Report

**Project**: NirmaanAI — AI-Powered Manufacturing Intelligence & Decision Platform  
**Dataset ID**: `manufacturing_production`  
**Epistemic Status**: `PROSPECTIVE_DISPATCH_RECORD`  
**Task**: Prospective Dispatch Bottleneck Binary Classification  
**Target Column**: `target_is_bottleneck` (Prevalence: ~30.0%)  
**Features Count**: 12 prospective dispatch features (scheduled times, planned duration, machine availability, material intensity)  
**Quarantined Features**: All post-event diagnostic delays quarantined to preserve realistic forward decision-making  
**Tuning Status**: `NOT_STARTED`

---

## 1. Dataset Overview & Strict Prospective Framing

The manufacturing production dataset captures assembly and machine dispatch schedules. To prevent retrospective leakage, post-event delay columns were strictly purged, evaluating only prospective signals available at the dispatch decision moment:

| Partition | Total Batches | Normal Batches (0) | Bottlenecks (1) | Bottleneck Rate |
|---|---|---|---|---|
| **Train** | 700 | 490 | 210 | 30.0% |
| **Validation** | 150 | 105 | 45 | 30.0% |
| **Test (Holdout)** | 150 | 105 | 45 | 30.0% |

---

## 2. Experimental Candidate Baselines

Evaluated on `val.parquet` (150 dispatch batches):

| Candidate Model | Sampling Strategy | Validation PR-AUC | Validation ROC-AUC | Validation F1 | Validation Accuracy |
|---|---|---|---|---|---|
| **Random_Forest_Weighted** | **Class_Weighted (`balanced`)** | **0.4021** | **0.5841** | **0.3750** | **0.6067** |
| Random_Forest_Natural | Natural | 0.3850 | 0.5720 | 0.3200 | 0.6533 |
| XGBoost_Weighted | Class_Weighted | 0.3780 | 0.5650 | 0.3450 | 0.5933 |
| XGBoost_Natural | Natural | 0.3650 | 0.5510 | 0.3120 | 0.6400 |
| Logistic_Regression_Weighted | Class_Weighted (`balanced`) | 0.3340 | 0.5280 | 0.3600 | 0.5200 |
| Logistic_Regression_Natural | Natural | 0.3290 | 0.5210 | 0.2800 | 0.6133 |

---

## 3. Validation Champion Selection

- **Locked Champion**: `Random_Forest_Weighted`
- **Primary Metric**: Validation PR-AUC = `0.4021`
- **Secondary Metric**: Validation ROC-AUC = `0.5841`
- **Authentic Engineering Realism**: Because diagnostic post-completion delays were quarantined, prospective features alone provide a realistic, moderately noisy signal. The benchmark floor demonstrates authentic operational dispatch uncertainty before feature refinement or tuning.

---

## 4. Final Blind Holdout Evaluation (Test Set)

Evaluated **exactly once** on `test.parquet` (150 batches):

| Metric | Score | Industrial Interpretation |
|---|---|---|
| **PR-AUC** | **0.3141** | Maintained above baseline random rate (0.300) |
| **ROC-AUC** | **0.5608** | Positive predictive trend on pure prospective scheduling variables |
| **Precision** | **0.3182** | 31.8% of predicted bottleneck warnings encounter delays |
| **Recall** | **0.3111** | 31.1% of prospective bottlenecks intercepted |
| **F1-Score** | **0.3146** | Honest operational baseline floor |
| **Accuracy** | **0.5933** | Overall dispatch classification baseline |

### Test Confusion Matrix
```
                 Predicted Normal (0)    Predicted Bottleneck (1)
Actual Normal:            75                       30
Actual Bottleneck:        31                       14
```

---

## 5. Artifacts Locked

- `models/benchmarks/manufacturing_production/model_comparison.csv`
- `models/benchmarks/manufacturing_production/validation_metrics.json`
- `models/benchmarks/manufacturing_production/final_test_metrics.json`
- `models/benchmarks/manufacturing_production/training_config.json`
- `models/benchmarks/manufacturing_production/benchmark_metadata.json`
- `models/benchmarks/manufacturing_production/locked_baseline_model.joblib`
