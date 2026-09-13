# AI4I 2020 Machine Failure Tuning & Validation Report

**Project**: NirmaanAI — AI-Powered Manufacturing Intelligence & Decision Platform  
**Stage**: Post-Phase-25 Research Extension (Model Tuning & Validation)  
**Dataset**: `ai4i`  
**Task**: Multi-Mode Machine Failure Classification (`machine_failure`)  
**Epistemic Status**: `REAL_PHYSICAL_SIMULATOR`  
**Tuning Decision**: `BASELINE_RETAINED`

---

## 1. Executive Summary & Core Metadata

| Parameter | Specification |
|---|---|
| **Dataset ID** | `ai4i` |
| **Task Definition** | Machine Failure Binary Classification under multi-mode physical stress |
| **Target Column** | `machine_failure` (Prevalence: ~3.39%) |
| **Epistemic Status** | `REAL_PHYSICAL_SIMULATOR` |
| **Baseline Champion** | `Random_Forest_Natural` |
| **Baseline Validation PR-AUC** | `0.9051` |
| **Baseline Frozen Test PR-AUC** | `0.9099` |
| **Tuned Candidate Champion** | `RF_n200_d8_l1_None_Nat` |
| **Tuned Validation PR-AUC** | `0.9081` (+0.0030 improvement, below 0.005 threshold) |
| **Final Decision** | **BASELINE RETAINED** |

---

## 2. Tuning Objective & Quarantine Integrity

The baseline model demonstrated high predictive efficacy (PR-AUC 0.9099, accuracy 99.2%). The tuning goal was to test whether deeper ensembles (200 trees), leaf regularizations, or gradient boosting could marginalize the remaining 11 false negatives without violating leakage constraints. Quarantines on `UDI`, `Product ID`, string `product_type`, and explicit failure modes (`TWF`, `HDF`, `PWF`, `OSF`, `RNF`) were strictly enforced.

---

## 3. Candidate Models & Bounded Search Space

62 bounded configurations evaluated on `train.parquet` (7,000 rows) and `val.parquet` (1,500 rows):

1. **Random Forest (48 configs)**:
   - `n_estimators`: [100, 150, 200]
   - `max_depth`: [8, 12, 16, None]
   - `min_samples_leaf`: [1, 2]
   - `class_weight`: [None, "balanced"]
2. **XGBoost (12 configs)**:
   - `max_depth`: [4, 6]
   - `learning_rate`: [0.03, 0.08]
   - `scale_pos_weight`: [1.0, 10.0, 28.5]
3. **Train-Only ROS (2 configs)**:
   - `RandomForest` on `training_sampled.parquet` (depth 8, 12)

- **Total Configurations Evaluated**: 62
- **Validation Protocol**: Selection strictly on `val.parquet` (1,500 rows) via PR-AUC.

---

## 4. Validation Comparison & Champion Selection

- **Baseline Validation PR-AUC**: `0.9051`
- **Best Tuned Validation PR-AUC**: `0.9081` (`RF_n200_d8_l1_None_Nat`)
- **Validation Delta**: `+0.0030` (+0.34% relative improvement)
- **Threshold Optimization**: Operating threshold of `0.20` yielded validation F1 = 0.8491.
- **Scientific Decision**: Because the validation delta (+0.0030) did not meet the mandatory +0.005 significance threshold, the model is **retained at baseline** to avoid unwarranted complexity.

---

## 5. Blind Holdout Test Evaluation (Test Set)

Evaluated **exactly once** on holdout `test.parquet` (1,500 samples):

| Evaluation Metric | Frozen Baseline (Default 0.5) | Tuned Candidate (Default 0.5) | Tuned Candidate (Opt 0.20) | Absolute Delta (Tuned vs Baseline) |
|---|---|---|---|---|
| **PR-AUC** | **0.9099** | **0.9135** | 0.9135 | **+0.0035** |
| **ROC-AUC** | **0.9711** | **0.9754** | 0.9754 | **+0.0043** |
| **Accuracy** | 0.9920 | 0.9920 | 0.9880 | +0.0000 |
| **Precision** | 0.9756 | 0.9756 | 0.7719 | +0.0000 |
| **Recall** | 0.7843 | 0.7843 | **0.8627** | +0.0000 (+0.0784 at opt) |
| **F1-Score** | 0.8696 | 0.8696 | 0.8148 | +0.0000 |

### Test Confusion Matrix (Tuned Candidate at Default 0.5 Threshold)
```
                 Predicted Normal (0)    Predicted Failure (1)
Actual Normal:          1,448                      1
Actual Failure:           11                      40
```

---

## 6. Generalization, Overfitting & Limitations

1. **Generalization**: Both the baseline and tuned 200-tree models generalize with exceptional fidelity, confirming that the engineered thermodynamic features (`temp_diff_k`, `torque_speed_product`, `tool_wear_risk_index`) carry robust physical signal.
2. **Limitations**: Marginal gains above 0.91 PR-AUC reflect irreducible noise in the synthetic stochastic failure transitions.
3. **Formal Decision**: **BASELINE RETAINED**. `Random_Forest_Natural` remains the locked production benchmark champion.
