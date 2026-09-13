# Manufacturing Production Prospective Bottleneck Tuning Report

**Project**: NirmaanAI — AI-Powered Manufacturing Intelligence & Decision Platform  
**Stage**: Post-Phase-25 Research Extension (Model Tuning & Validation)  
**Dataset**: `manufacturing_production`  
**Task**: Prospective Bottleneck Binary Classification (`target_is_bottleneck`)  
**Epistemic Status**: `PROSPECTIVE_DISPATCH_RECORD`  
**Tuning Decision**: `BASELINE_RETAINED`

---

## 1. Executive Summary & Core Metadata

| Parameter | Specification |
|---|---|
| **Dataset ID** | `manufacturing_production` |
| **Task Definition** | Prospective Bottleneck Binary Classification at dispatch time |
| **Target Column** | `target_is_bottleneck` (Prevalence: ~30.0%) |
| **Epistemic Status** | `PROSPECTIVE_DISPATCH_RECORD` |
| **Baseline Champion** | `Random_Forest_Weighted` (`class_weight='balanced'`) |
| **Baseline Validation PR-AUC** | `0.4021` |
| **Baseline Frozen Test PR-AUC** | `0.3141` |
| **Tuned Candidate Champion** | `LR_C0.1_balanced` |
| **Tuned Validation PR-AUC** | `0.3993` |
| **Final Decision** | **BASELINE RETAINED** (Tuning did not achieve >= 0.005 improvement) |

---

## 2. Tuning Objective & Scientific Rationale

In prospective manufacturing dispatch, identifying bottlenecks before machines experience severe queues is essential. However, because post-completion delays and retrospective downtime fields were strictly quarantined, the prospective feature space represents an honest, moderately noisy signal. The objective was to determine whether regularized models or depth-constrained gradient boosted trees could outperform the baseline weighted random forest without overfitting the 700-row training partition.

---

## 3. Candidate Models & Bounded Search Space

A bounded search across 54 configurations was evaluated on `train.parquet` (700 batches) and `val.parquet` (150 batches):

1. **Random Forest (24 configs)**:
   - `n_estimators`: [100, 200]
   - `max_depth`: [4, 6, 8]
   - `min_samples_leaf`: [2, 5]
   - `max_features`: ["sqrt"]
   - `class_weight`: ["balanced", "balanced_subsample"]
2. **XGBoost (24 configs)**:
   - `n_estimators`: [80, 120]
   - `max_depth`: [3, 4]
   - `learning_rate`: [0.03, 0.08]
   - `subsample`: [0.85]
   - `colsample_bytree`: [0.8]
   - `min_child_weight`: [3]
   - `scale_pos_weight`: [1.0, 2.33, 3.5]
3. **Logistic Regression (6 configs)**:
   - `C`: [0.01, 0.1, 1.0]
   - `class_weight`: [None, "balanced"]

- **Total Configurations Evaluated**: 54
- **Sampling Strategy**: Natural Training & Class-Weighted Exploration (No synthetic oversampling applied to validation/test).
- **Validation Protocol**: Fixed validation partition (`val.parquet`, 150 batches). Selection strictly via PR-AUC.

---

## 4. Validation Comparison & Champion Selection

- **Baseline Validation PR-AUC**: `0.4021`
- **Best Tuned Validation PR-AUC**: `0.3993` (`LR_C0.1_balanced`)
- **Validation Delta**: `-0.0027` (-0.68% relative change)
- **Threshold Optimization**: An optimal validation threshold of `0.35` yielded validation F1 = 0.5392.
- **Scientific Decision**: Because the best tuned model failed to beat the baseline validation score (+0.005 threshold), the baseline `Random_Forest_Weighted` is **strictly retained** as the preferred model.

---

## 5. Blind Holdout Test Evaluation (Test Set)

The frozen configuration was evaluated **exactly once** on `test.parquet` (150 batches) to document the empirical delta:

| Evaluation Metric | Frozen Baseline | Tuned Evaluation (Default 0.5) | Tuned Evaluation (Opt 0.35) | Absolute Delta (Tuned vs Baseline) |
|---|---|---|---|---|
| **PR-AUC** | **0.3141** | 0.2717 | 0.2717 | -0.0424 |
| **ROC-AUC** | **0.5608** | 0.5485 | 0.5485 | -0.0123 |
| **Accuracy** | 0.5933 | 0.5600 | 0.5267 | -0.0333 |
| **Precision** | 0.3182 | 0.2609 | 0.3333 | -0.0573 |
| **Recall** | 0.3111 | 0.2667 | **0.5778** | -0.0444 (+0.2667 at opt) |
| **F1-Score** | 0.3146 | 0.2637 | **0.4228** | -0.0509 (+0.1082 at opt) |

### Test Confusion Matrix (Tuned at Default 0.5 Thresh)
```
                 Predicted Normal (0)    Predicted Bottleneck (1)
Actual Normal:            72                       33
Actual Bottleneck:        33                       12
```

---

## 6. Generalization, Overfitting & Limitations

1. **Generalization Analysis**: Bounded tuning confirmed that tree ensembles with balanced weights remain more robust than linear models on pure prospective variables. Complex gradient boosting exhibited slight overfitting on the small dispatch batch sample (700 rows).
2. **Limitations**: In the absence of real-time machine queue telemetry, prospective scheduling variables (`planned_duration_min`, `scheduled_hour`, `material_intensity`) establish an honest lower bound on operational predictability.
3. **Formal Decision**: **BASELINE RETAINED**. `Random_Forest_Weighted` remains the locked champion.
