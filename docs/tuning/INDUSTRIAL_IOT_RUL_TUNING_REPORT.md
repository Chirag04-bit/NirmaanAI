# Industrial IoT Factory Simulator Remaining Useful Life Tuning & Validation Report
## Post-Phase-25 Research Extension — Task 7

### 1. Dataset
- **Name**: Industrial IoT Factory Simulator 2040 (RUL Sub-task)
- **Domain**: Automated Manufacturing Machine Telemetry
- **Input Data**: Multi-sensor operating data across 500,000 factory machines.
- **Audit Finding**: Dataset represents a cross-sectional fleet snapshot of 500,000 distinct machines (exactly 1 record per `Machine_ID`). Zero temporal tracking or degradation trajectories exist within individual machines.

### 2. Task
- **Objective**: Machine Remaining Useful Life prediction in days.
- **Target Variable**: `Remaining_Useful_Life_days` (continuous days, non-negative).
- **Quarantined Fields**: `Machine_ID` (unique identifier), `Failure_Within_7_Days` (prospective classification label quarantined to prevent target leakage).
- **Evaluation Type**: Cross-Sectional Fleet Regression.

### 3. Epistemic Status
- **Classification**: `CONTROLLED_INDUSTRIAL_SIMULATOR`
- **Scientific Context**: High-throughput industrial simulator generating synthetic machine telemetry. Because each machine appears exactly once, this model serves as a fleet snapshot regressor rather than an ongoing degradation monitor.

### 4. Baseline Champion
- **Model**: `XGBoost_Regressor` (Default hyperparameters: n_estimators=100, max_depth=6, learning_rate=0.1)
- **Baseline Source**: Commit `36e9013`, `models/benchmarks/industrial_iot_rul/`

### 5. Baseline Metrics
- **Validation**:
  - RMSE: 48.4887 days
  - MAE: 38.3188 days
  - $R^2$: 0.9719
  - WAPE: 8.49%
- **Frozen Baseline Test**:
  - RMSE: 48.5980 days
  - MAE: 38.3695 days
  - $R^2$: 0.9716
  - WAPE: 8.48%

### 6. Tuning Objective
- **Primary Metric**: Validation RMSE ($\text{days}$)
- **Secondary Metrics**: MAE, $R^2$, WAPE, SMAPE
- **Success Criterion**: Validation RMSE reduction $\ge 0.50$ days over baseline. If delta $< 0.50$ days, the baseline is strictly retained.

### 7. Candidate Models
- **XGBoost Regressor**: Gradient boosted trees exploring tree count, max depth, and learning rates on a 50,000-row representative tuning sample.
- **Random Forest Regressor**: Parallel ensemble trees exploring max depth and split criteria.

### 8. Search Space
- **XGBoost**:
  - `max_depth`: [5, 6, 7]
  - `learning_rate`: [0.05, 0.10]
  - `n_estimators`: [100, 150]
- **Random Forest**:
  - `n_estimators`: [100]
  - `max_depth`: [12, 16]
  - `max_features`: ['sqrt', 0.5]
- Total bounded search space: 12 XGBoost + 4 Random Forest = 16 configurations.

### 9. Number of Configurations Evaluated
- **Evaluated**: 16 deterministic configurations (Seed = 42).
- **Test Participation**: 0 configurations evaluated on test set during exploration.

### 10. Sampling Strategy
- **Sampling**: Representative random stratified subsample of training partition for hyperparameter grid evaluation; final champion fitted across full 350,000-row training set.

### 11. Validation Protocol
- **Split Structure**: Machine-Disjoint Split (70/15/15)
  - Train: 350,000 distinct machines
  - Validation: 75,000 distinct machines
  - Test: 75,000 distinct machines
- **Leakage Safeguards**: Exactly 0 machine ID overlap between partitions. Preprocessing scaler fitted strictly on training data.

### 12. Best Validation Configuration
- **Model**: `XGB_d6_lr0.05_n150`
  - `max_depth`: 6
  - `learning_rate`: 0.05
  - `n_estimators`: 150
  - `random_state`: 42
- **Validation RMSE**: 48.3192 days (vs Baseline 48.4887 days)
- **Validation Improvement**: 0.1694 days (0.35%)

### 13. Tuned Champion
- **Champion Configuration**: `XGB_d6_lr0.05_n150`
- **Artifact**: `models/tuned/industrial_iot_rul/locked_tuned_model.joblib`

### 14. Final Test Metrics (Evaluated Once on 75,000 Machine Holdout)
- **RMSE**: 48.3798 days
- **MAE**: 38.2181 days
- **$R^2$**: 0.9718
- **WAPE**: 8.44% (0.08444)
- **SMAPE**: 25.76% (0.2576)

### 15. Baseline vs Tuned Table

| Metric | Baseline Val | Tuned Val | Baseline Test | Tuned Test | Test Delta |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **RMSE (days)** | 48.4887 | **48.3192** | 48.5980 | **48.3798** | -0.2181 (-0.45%) |
| **MAE (days)** | 38.3188 | **38.1663** | 38.3695 | **38.2181** | -0.1514 (-0.39%) |
| **$R^2$** | 0.9719 | **0.9721** | 0.9716 | **0.9718** | +0.0002 (+0.02%) |
| **WAPE** | 0.0849 | **0.0845** | 0.0848 | **0.0844** | -0.0004 (-0.47%) |

### 16. Absolute Improvement
- **Validation RMSE**: -0.1694 days
- **Test RMSE**: -0.2181 days

### 17. Relative Improvement
- **Validation RMSE**: +0.35% improvement
- **Test RMSE**: +0.45% improvement

### 18. Generalization Discussion
- With 350,000 training observations, the baseline model had already converged near the simulator's inherent generative noise boundary ($R^2 \approx 0.972$).
- The tuned configuration (`n_estimators=150, lr=0.05`) yielded a minor 0.17 day reduction in validation RMSE, but this represents marginal noise refinement rather than a meaningful structural improvement.

### 19. Overfitting Analysis
- Both baseline and tuned models exhibit negligible train-to-test divergence ($|RMSE_{val} - RMSE_{test}| < 0.1$ days), confirming robust stability.
- However, since the delta falls well below the pre-registered 0.50-day significance threshold, replacing the baseline would constitute scientific over-tuning without practical industrial benefit.

### 20. Limitations
- Single cross-sectional snapshot: The dataset cannot capture temporal wear-down dynamics or acceleration of failure over time.
- Large scale: Training full ensembles on 350,000 rows carries significant computational overhead for negligible gain.

### 21. Decision
- **`BASELINE_RETAINED`**
- In strict adherence to scientific restraint guidelines, the validation improvement of 0.1694 days fell short of the pre-specified 0.50-day acceptance threshold. The baseline benchmark model is formally retained.
