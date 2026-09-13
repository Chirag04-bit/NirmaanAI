# Manufacturing Defects Quality Classification Tuning & Validation Report
## Post-Phase-25 Research Extension — Task 8

### 1. Dataset
- **Name**: Manufacturing Process Quality & Defect Tracking
- **Domain**: Automated Assembly Quality Control
- **Input Data**: Multi-stage sensor metrics across production line stations (temperature, pressure, speed, vibration, torque, cycle times).
- **Target Variable**: `defect_detected` (Binary classification: 0 = nominal part, 1 = defective component).

### 2. Task
- **Objective**: Inline detection of defective manufacturing components.
- **Target Variable**: `defect_detected`
- **Evaluation Type**: Supervised Binary Classification with Class Imbalance.

### 3. Epistemic Status
- **Classification**: `REAL_MANUFACTURING_METRICS`
- **Scientific Context**: Industrial quality control metrics recorded from physical automated assembly stations. Real physical defect distributions with high class prevalence of nominal items.

### 4. Baseline Champion
- **Model**: `Random_Forest_Natural` (Default hyperparameters: n_estimators=100, max_depth=None, min_samples_leaf=1)
- **Baseline Source**: Commit `36e9013`, `models/benchmarks/manufacturing_defects/`

### 5. Baseline Metrics
- **Validation**:
  - ROC-AUC: 0.8184
  - PR-AUC: 0.9452
  - F1: 0.9701
  - Recall: 0.9951
  - Precision: 0.9463
  - Accuracy: 0.9486
- **Frozen Baseline Test**:
  - ROC-AUC: 0.8675
  - PR-AUC: 0.9570
  - F1: 0.9784
  - Recall: 0.9975
  - Precision: 0.9600
  - Accuracy: 0.9630

### 6. Tuning Objective
- **Primary Metric**: Validation ROC-AUC
- **Secondary Metrics**: PR-AUC, F1, Recall, Precision, Accuracy
- **Success Criterion**: Validation ROC-AUC improvement $\ge 0.0050$. If improvement $< 0.0050$, baseline is retained.

### 7. Candidate Models
- **Random Forest**: Ensembles exploring tree count, maximum depth (6, 10, None), and minimum leaf samples (1, 2, 4) to regularize leaf purity and suppress boundary variance.
- **XGBoost**: Gradient boosted trees exploring shallow depths (3, 4, 6) and learning rates (0.03, 0.06).

### 8. Search Space
- **Random Forest**:
  - `n_estimators`: [100, 150]
  - `max_depth`: [6, 10, None]
  - `min_samples_leaf`: [1, 2, 4]
- **XGBoost**:
  - `max_depth`: [3, 4, 6]
  - `learning_rate`: [0.03, 0.06]
- Total bounded search space: 18 Random Forest + 6 XGBoost = 24 configurations.

### 9. Number of Configurations Evaluated
- **Evaluated**: 24 deterministic configurations (Seed = 42).
- **Test Participation**: 0 configurations evaluated on test set during exploration.

### 10. Sampling Strategy
- **Sampling**: Natural empirical distribution (class weighting not required due to sufficient defect representations).

### 11. Validation Protocol
- **Split Structure**: Stratified Train/Val/Test Split (70/15/15)
  - Train: 2,268 parts
  - Validation: 486 parts
  - Test: 486 parts
- **Leakage Safeguards**: Standard scaler fitted strictly on training partition. Zero target or feature overlap.

### 12. Best Validation Configuration
- **Model**: `RF_n100_dNone_l4`
  - `n_estimators`: 100
  - `max_depth`: None
  - `min_samples_leaf`: 4
  - `random_state`: 42
- **Validation ROC-AUC**: 0.8389 (vs Baseline 0.8184)
- **Validation Improvement**: +0.0206 (+2.52%)

### 13. Tuned Champion
- **Champion Configuration**: `RF_n100_dNone_l4`
- **Artifact**: `models/tuned/manufacturing_defects/locked_tuned_model.joblib`

### 14. Final Test Metrics (Evaluated Once on 486-Part Test Partition)
- **ROC-AUC**: 0.8935
- **PR-AUC**: 0.9666
- **F1**: 0.9784
- **Recall**: 0.9975 (407 of 408 defective parts detected)
- **Precision**: 0.9599
- **Accuracy**: 0.9630
- **Confusion Matrix**: TN=61, FP=17, FN=1, TP=407
- **Threshold**: Optimal operating threshold = 0.50

### 15. Baseline vs Tuned Table

| Metric | Baseline Val | Tuned Val | Baseline Test | Tuned Test | Test Delta |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ROC-AUC** | 0.8184 | **0.8389** | 0.8675 | **0.8935** | +0.0261 (+3.01%) |
| **PR-AUC** | 0.9452 | **0.9374** | 0.9570 | **0.9666** | +0.0096 (+1.00%) |
| **F1 Score** | 0.9701 | **0.9689** | 0.9784 | **0.9784** | 0.0000 (0.00%) |
| **Recall** | 0.9951 | **0.9902** | 0.9975 | **0.9975** | 0.0000 (0.00%) |
| **Precision** | 0.9463 | **0.9485** | 0.9600 | **0.9599** | -0.0001 (-0.01%) |
| **Accuracy** | 0.9486 | **0.9465** | 0.9630 | **0.9630** | 0.0000 (0.00%) |

### 16. Absolute Improvement
- **Validation ROC-AUC**: +0.0206
- **Test ROC-AUC**: +0.0261
- **Test PR-AUC**: +0.0096

### 17. Relative Improvement
- **Validation ROC-AUC**: +2.52% relative improvement
- **Test ROC-AUC**: +3.01% relative improvement

### 18. Generalization Discussion
- Increasing the minimum samples per leaf from 1 to 4 effectively regularized the decision forest boundaries, smoothing out leaf probability estimates without collapsing tree expressive depth.
- The 0.0206 ROC-AUC validation gain translated into a strong +0.0261 test ROC-AUC gain (rising from 0.8675 to 0.8935), with 99.75% defect recall retained.

### 19. Overfitting Analysis
- Baseline random forests with `min_samples_leaf=1` created hyperspecific terminal leaves that slightly overfit sensor noise in the training set.
- Setting `min_samples_leaf=4` ensured that each leaf probability represents a statistically stable sample of assembly components, boosting ranking discrimination.

### 20. Limitations
- Production batch shifts: Substantial raw material supplier changes or tool retooling could shift feature distributions.
- Minor class imbalance requires continued monitoring of false alarm rates (17 false positives in test set).

### 21. Decision
- **`TUNED_MODEL_ACCEPTED`**
- Tuned configuration `RF_n100_dNone_l4` achieved an absolute validation ROC-AUC improvement of +0.0206 (surpassing the $\ge 0.0050$ threshold) and produced a test ROC-AUC of 0.8935.
