# Electricity Load Forecasting Tuning & Validation Report
## Post-Phase-25 Research Extension — Task 6

### 1. Dataset
- **Name**: Industrial Grid Telemetry Electricity Consumption
- **Domain**: Power System Energy Forecasting
- **Input Data**: 15-minute interval historical active power demand with causal lag features (lags 1, 2, 4, 8, 96, 672), rolling statistical windows (4h, 24h, 7d), and cyclical calendar features (hour-of-day, day-of-week).
- **Temporal Nature**: Strictly chronological time series; zero random shuffling.

### 2. Task
- **Objective**: 15-minute ahead power consumption forecasting.
- **Target Variable**: `power_kw` (continuous active load in kW).
- **Evaluation Type**: Chronological Out-of-Sample Regression.

### 3. Epistemic Status
- **Classification**: `REAL_INDUSTRIAL_TELEMETRY`
- **Scientific Context**: Empirical smart grid sensor recordings capturing realistic daily load cycles, industrial shift schedules, weekend diurnal dips, and seasonal grid variation.

### 4. Baseline Champion
- **Model**: `XGBoost_Regressor` (Default hyperparameters: n_estimators=100, max_depth=6, learning_rate=0.1)
- **Baseline Source**: Commit `36e9013`, `models/benchmarks/electricity/`

### 5. Baseline Metrics
- **Validation**:
  - WAPE: 6.52% (0.06517)
  - MAE: 18.7997 kW
  - RMSE: 25.5905 kW
  - $R^2$: 0.9599
- **Frozen Baseline Test**:
  - WAPE: 6.63% (0.06626)
  - MAE: 19.8277 kW
  - RMSE: 27.0425 kW
  - $R^2$: 0.9580

### 6. Tuning Objective
- **Primary Metric**: Validation Weighted Absolute Percentage Error (WAPE)
- **Secondary Metrics**: MAE, RMSE, $R^2$, SMAPE
- **Success Criterion**: Validation WAPE reduction $\ge 0.10\%$ (0.0010) over baseline.

### 7. Candidate Models
- **XGBoost Regressor**: Gradient boosted trees exploring tree estimators, tree depth, learning rate, and minimum child weight regularizers for time-series forecasting.

### 8. Search Space
- `n_estimators`: [100, 150, 200]
- `max_depth`: [4, 6, 8]
- `learning_rate`: [0.03, 0.06, 0.10]
- `min_child_weight`: [1, 3]
- Total bounded search space: $3 \times 3 \times 3 \times 2 = 54$ configurations.

### 9. Number of Configurations Evaluated
- **Evaluated**: 54 deterministic configurations (Seed = 42).
- **Test Participation**: 0 configurations evaluated on test partition during tuning.

### 10. Sampling Strategy
- **Sampling**: Continuous sequential temporal series (No resampling, strictly preserving time-ordering).

### 11. Validation Protocol
- **Split Structure**: Strict Chronological Split
  - Train: First 70% of timeline (24,516 observations)
  - Validation: Middle 15% of timeline (5,254 observations)
  - Test: Final 15% of timeline (5,254 observations)
- **Causal Guarantee**: All features (lags, rolling means, rolling standard deviations) computed strictly backwards in time; zero future information leakage.

### 12. Best Validation Configuration
- **Model**: `XGB_n200_d8_lr0.03_mcw1`
  - `n_estimators`: 200
  - `max_depth`: 8
  - `learning_rate`: 0.03
  - `min_child_weight`: 1
  - `random_state`: 42
- **Validation WAPE**: 6.20% (0.06199)
- **Validation MAE**: 17.8802 kW
- **Validation RMSE**: 24.4383 kW
- **Validation $R^2$**: 0.9634

### 13. Tuned Champion
- **Champion Configuration**: `XGB_n200_d8_lr0.03_mcw1`
- **Artifact**: `models/tuned/electricity/locked_tuned_model.joblib`

### 14. Final Test Metrics (Evaluated Once on Final 15% Chronological Holdout)
- **WAPE**: 6.27% (0.06275)
- **MAE**: 18.7774 kW
- **RMSE**: 25.5648 kW
- **$R^2$**: 0.9625
- **SMAPE**: 7.50% (0.07498)

### 15. Baseline vs Tuned Table

| Metric | Baseline Val | Tuned Val | Baseline Test | Tuned Test | Test Delta |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **WAPE** | 6.52% (0.06517) | **6.20% (0.06199)** | 6.63% (0.06626) | **6.27% (0.06275)** | -0.35% (-5.30%) |
| **MAE (kW)** | 18.7997 | **17.8802** | 19.8277 | **18.7774** | -1.0503 (-5.30%) |
| **RMSE (kW)** | 25.5905 | **24.4383** | 27.0425 | **25.5648** | -1.4777 (-5.46%) |
| **$R^2$** | 0.9599 | **0.9634** | 0.9580 | **0.9625** | +0.0045 (+0.47%) |

### 16. Absolute Improvement
- **Validation WAPE**: -0.318% (-0.00318)
- **Validation MAE**: -0.9195 kW
- **Test WAPE**: -0.351% (-0.00351)
- **Test MAE**: -1.0503 kW

### 17. Relative Improvement
- **Validation WAPE**: +4.89% relative error reduction
- **Test WAPE**: +5.30% relative error reduction

### 18. Generalization Discussion
- Increasing tree depth to 8 allowed XGBoost to capture subtle cross-interactions between weekly seasonal cycles (lag 672) and sub-daily shift ramps, while a smaller learning rate of 0.03 prevented leaf-level noise fitting.
- The 0.32% WAPE gain on the validation period replicated cleanly on the unseen 15% future test set (0.35% error reduction).

### 19. Overfitting Analysis
- Unregularized deep trees can memorize short-term sensor blips; however, coupling `max_depth=8` with lower step size (`0.03`) and 200 iterations yielded monotonically decreasing validation loss.
- Out-of-sample $R^2$ improved from 0.9580 to 0.9625, confirming enhanced signal extraction without over-reliance on recent residual terms.

### 20. Limitations
- Abrupt structural shocks (e.g. multi-day grid blackout or major factory retooling) that fall outside the historical lag structure will require online adaptive retraining.
- Weather covariates (ambient outdoor temperature, solar irradiation) are absent from this telemetry stream.

### 21. Decision
- **`TUNED_MODEL_ACCEPTED`**
- Tuned configuration `XGB_n200_d8_lr0.03_mcw1` achieved an absolute validation WAPE reduction of 0.318% (exceeding the $\ge 0.10\%$ threshold) and reduced test WAPE from 6.63% to 6.27%.
