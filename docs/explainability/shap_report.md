# NirmaanAI — Phase 11 Model Report: Explainable AI & SHAP Feature Attribution

**Subsystem**: Model Explainability & Interpretability (XAI)  
**Module**: Phase 11  
**Version**: 1.0.0  
**Date**: September 2026  
**Author**: NirmaanAI Core Research Team  
**Institution**: Institute of Engineering & Management (IEM), Kolkata  
**Project Guide**: Prof. Kuntal Mondal  

---

## 1. Executive Summary & Objective

Phase 11 introduces NirmaanAI's **Explainable AI (XAI)** layer using SHAP (SHapley Additive exPlanations) for already-approved predictive machine learning models. The subsystem answers the fundamental operational question:

$$\textbf{"WHY did NirmaanAI make this prediction?"}$$

### Core Scientific Guardrails:
1. **Model Attribution vs. Physical Causality**:
   - **SHAP explains the mathematical model's response surface**, NOT physical causality in the machine tool.
   - Attributions identify which features the model weighted to arrive at a specific probability or RUL estimate.
   - We strictly reject claiming that "SHAP proved feature $X$ physically caused failure". Physical root causes are addressed in later diagnostic phases.
2. **Zero Model Retraining & Frozen Predictions**:
   - Model weights, trees, and decision thresholds ($\tau = 0.91$ for AI4I equipment alerts) remain 100% frozen.
   - Predictions before and after SHAP explanation are byte-for-byte invariant.
3. **Strict Leakage Preservation**:
   - Variables barred in Phase 6 (`UDI`, `Product ID`, `TWF`, `HDF`, `PWF`, `OSF`, `RNF`) remain completely excluded from all explainers.

---

## 2. Explainer Selection & Model Suitability Audit

| Subsystem / Model | Model Class | Feature Space | Output Explaining Space | Explainer Method | Suitability Status | Scientific Justification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Phase 6: AI4I Failure Classifier** | `xgboost.XGBClassifier` | 10 engineered features | Additive log-odds margin (with logistic sigmoid probability mapping) | `shap.TreeExplainer` | **Primary Champion** | TreeExplainer computes exact Shapley values in tree margin space with zero additive error ($|\text{margin} - (\text{base} + \sum \text{SHAP})| = 0.0$). |
| **Phase 6: NASA C-MAPSS RUL** | `RandomForestRegressor` | 48 informative sensors & rolling stats | Remaining Useful Life in operational cycles | `shap.TreeExplainer` | **Secondary Champion** | TreeExplainer natively supports bagged ensemble forests, attributing cycle deviations from base $\approx 86.52\text{ cycles}$. |
| **Phase 7: Anomaly Detection** | PCA Reconstruction | 12 raw machine sensors | Unsupervised squared error | *None (Native Decomposition)* | **Ineligible for Supervised SHAP** | PCA is an unsupervised projection; native squared sensor error $e_i^2 = (x_i - \hat{x}_i)^2$ provides direct physical attribution. Forcing SHAP is mathematically inappropriate. |
| **Phase 8: Bottleneck Prediction** | Heuristic Flow Rules | Cycle ratios & dispatch delays | Binary thresholding | *None* | **Ineligible** | Rule-based physical heuristic; forcing SHAP onto a non-ML heuristic is scientifically dishonest. |
| **Phase 9: Energy Forecaster** | `XGBoostForecaster` | 15 autoregressive lag features | Active power in kW | `shap.TreeExplainer` | **Supporting** | Attributes autoregressive power inertia ($t-1, t-2, t-24, t-168$) for multi-step load forecasting. |

---

## 3. AI4I 2020 XGBoost Failure Classifier: Global Feature Attribution

Evaluated on the full holdout test set ($N=1,500$ observations):
- **Base Value (Log-Odds)**: $-0.00084$
- **Model Decision Threshold**: $\tau = 0.910$ (approved from Phase 6 precision-recall optimization)
- **Leakage Columns Excluded**: `UDI`, `Product ID`, `TWF`, `HDF`, `PWF`, `OSF`, `RNF`.

### 3.1. Global Feature Importance Ranking (Mean Absolute SHAP)

| Rank | Feature Name | Display Name | Unit | Mean \|SHAP\| | Relative Importance (%) | Physical Domain Interpretation |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- |
| **1** | `tool_wear_min` | Tool Wear Accumulated Time | min | **2.07145** | **32.31%** | Cumulative cutting time; primary driver of accelerated tertiary tool flank degradation. |
| **2** | `rotational_speed_rpm` | Spindle Rotational Speed | RPM | **1.10211** | **17.19%** | Spindle motor angular velocity; low RPM under load indicates near-stall conditions. |
| **3** | `mechanical_power_kw` | Instantaneous Mechanical Power Output | kW | **1.07034** | **16.70%** | Delivered mechanical power $(2\pi \cdot \text{RPM} \cdot \text{Torque})/60000$. |
| **4** | `temp_diff_k` | Thermal Stress Differential ($\Delta T$) | K | **0.82417** | **12.86%** | Temperature gradient $(T_{process} - T_{air})$; low values indicate thermal dissipation failure. |
| **5** | `torque_speed_ratio` | Load Stress Ratio ($\text{Torque}/\text{RPM}$) | Nm/RPM | **0.45926** | **7.16%** | Low-speed high-strain cutting laboring index. |
| **6** | `torque_nm` | Spindle Torque | Nm | **0.38338** | **5.98%** | Cutting resistance encountered by spindle motor. |
| **7** | `air_temperature_k` | Ambient Air Temperature | K | **0.21515** | **3.36%** | Factory ambient room temperature. |
| **8** | `process_temperature_k` | Internal Process Temperature | K | **0.21092** | **3.29%** | Spindle and workpiece cutting zone temperature. |
| **9** | `product_type_code` | Workpiece Quality Grade | Code | **0.07403** | **1.15%** | Workpiece grade (L=0, M=1, H=2); L-grade has tighter tolerance margins. |
| **10** | `tool_wear_risk_index` | Non-Linear Tool Wear Penalty | Index | **0.00000** | **0.00%** | Collinear quadratic term; tree splits prioritized linear `tool_wear_min` directly. |

### 3.2. Generated Visualizations
The following publication-grade figures were generated and saved under `docs/explainability/figures/`:
1. `ai4i_shap_summary_beeswarm.png`: Beeswarm summary plot displaying the distribution of SHAP values and their direction of impact across all test observations.
2. `ai4i_shap_bar_importance.png`: Bar chart of mean $|SHAP|$ ranking.
3. `ai4i_local_waterfall_tp.png`: Waterfall plot for True Positive case (Sample #11).
4. `ai4i_local_waterfall_fp.png`: Waterfall plot for False Positive case (Sample #966).

---

## 4. Local Explanations: Confusion Matrix Quadrants

To prevent cherry-picking, explanations were systematically extracted across all four quadrants of the test confusion matrix evaluated at $\tau = 0.910$:

### 4.1. True Positive (TP — Sample #11)
- **Actual Label**: 1 (Failure) | **Predicted Label**: 1 (Failure)
- **Model Output Probability**: $P = \mathbf{0.9952}$ (Log-Odds Margin = $+5.3248$)
- **Decision Threshold**: $\tau = 0.910$
- **Additive Consistency**: $\text{base} (-0.0008) + \sum \text{SHAP} (5.3256) = 5.3248$ (Error: $0.0$)
- **Top Risk-Increasing Drivers**:
  1. `temp_diff_k` $= 8.0\text{ K}$ ($\text{SHAP} = \mathbf{+3.6932}$): Abnormally low thermal dissipation gradient, indicating severe heat dissipation stress.
  2. `rotational_speed_rpm` $= 1350\text{ RPM}$ ($\text{SHAP} = \mathbf{+3.2864}$): Depressed spindle speed indicating motor laboring.
  3. `torque_speed_ratio` $= 0.0356$ ($\text{SHAP} = \mathbf{+0.3754}$): High load-to-speed ratio.
- **Top Mitigating Drivers**:
  1. `tool_wear_min` $= 32\text{ min}$ ($\text{SHAP} = \mathbf{-1.1350}$): Young tool flank life.
- **Narrative**: *"Prediction: FAILURE RISK (probability = 0.995 vs threshold 0.91). Factors driving the model toward failure prediction include Thermal Stress Differential (8.0 K, SHAP: +3.69) and Spindle Rotational Speed (1350.0 RPM, SHAP: +3.29). Factors mitigating predicted risk include Tool Wear Accumulated Time (32.0 min, SHAP: -1.14)."*

### 4.2. True Negative (TN — Sample #0)
- **Actual Label**: 0 (Healthy) | **Predicted Label**: 0 (Healthy)
- **Model Output Probability**: $P = \mathbf{0.0046}$ (Log-Odds Margin = $-5.3806$)
- **Top Mitigating Drivers**:
  1. `rotational_speed_rpm` $= 1549\text{ RPM}$ ($\text{SHAP} = \mathbf{-2.5971}$): Optimal nominal spindle operating velocity.
  2. `tool_wear_min` $= 81\text{ min}$ ($\text{SHAP} = \mathbf{-1.9027}$): Stable tool wear well below wear-out envelope.
  3. `mechanical_power_kw` $= 6.25\text{ kW}$ ($\text{SHAP} = \mathbf{-0.8438}$): Normal nominal power draw.
- **Narrative**: *"Prediction: NORMAL OPERATION (probability = 0.005 vs threshold 0.91). Spindle Rotational Speed (-2.60) and Tool Wear (-1.90) heavily mitigated failure probability."*

### 4.3. False Positive (FP — Sample #966)
- **Actual Label**: 0 (Healthy) | **Predicted Label**: 1 (Failure Alert)
- **Model Output Probability**: $P = \mathbf{0.9396}$ (Log-Odds Margin = $+2.7437$)
- **Why Did the Model Alert?**:
  - `tool_wear_min` $= 225\text{ min}$ ($\text{SHAP} = \mathbf{+4.3543}$): In AI4I, tool wear exceeding $200\text{ min}$ is statistically lethal in $>85\%$ of training cases.
  - While this specific machine survived without catastrophic fracture, the model's conservative threshold ($\tau=0.91$) correctly flagged the extreme wear condition.
- **Top Mitigating Drivers**:
  - `mechanical_power_kw` $= 6.99\text{ kW}$ ($\text{SHAP} = \mathbf{-0.9438}$) and `rotational_speed_rpm` $= 1386\text{ RPM}$ ($\text{SHAP} = \mathbf{-0.5827}$).

### 4.4. False Negative (FN — Sample #101)
- **Actual Label**: 1 (Failure) | **Predicted Label**: 0 (Normal Operation)
- **Model Output Probability**: $P = \mathbf{0.8120}$ (Log-Odds Margin = $+1.4633$)
- **Why Did the Model Miss $\tau = 0.91$?**:
  - Depressed speed ($1294\text{ RPM}$, $\text{SHAP} = +1.5969$) and high torque ($62.4\text{ Nm}$, $\text{SHAP} = +1.2776$) pushed the probability up to $0.812$.
  - However, moderate tool wear ($101\text{ min}$, $\text{SHAP} = -1.6581$) provided counter-evidence that prevented the probability from reaching the conservative $0.91$ threshold.
  - This demonstrates the trade-off of high-precision tuning ($\text{Precision}=0.9545$ at $\tau=0.91$).

---

## 5. NASA C-MAPSS FD001: RUL Regressor Feature Attribution

- **Champion Model**: `RandomForestRegressor` (100 bagged trees, 48 features).
- **Base Value (Expected RUL)**: $\mathbf{86.52\text{ cycles}}$ (training distribution mean).
- **Output Space**: Operational Cycles (Additive: $\text{RUL} = \text{base} + \sum \text{SHAP}$).

### 5.1. Top Degradation Sensors Ranked by Mean |SHAP|:
1. **`s4_roll_mean` (LPT Exhaust Gas Temperature, 5-cycle mean)**: **$15.55\text{ cycles}$** ($36.95\%$ relative importance).
2. **`s9_roll_mean` (Physical Core Speed, 5-cycle mean)**: **$6.40\text{ cycles}$** ($15.21\%$).
3. **`s11_roll_mean` (HPC Static Outlet Pressure, 5-cycle mean)**: **$5.72\text{ cycles}$** ($13.59\%$).
4. **`s21_roll_mean` (LPT Coolant Bleed Flow, 5-cycle mean)**: **$2.09\text{ cycles}$** ($4.96\%$).
5. **`s15_roll_mean` (Bypass Ratio, 5-cycle mean)**: **$1.88\text{ cycles}$** ($4.48\%$).

### 5.2. Representative High-RUL vs Low-RUL Cases:
- **High-RUL Early Life Engine**: Predicted RUL = $\mathbf{123.82\text{ cycles}}$ ($\text{base } 86.52 + 37.30$). Pushed upward by low LPT exhaust gas temperature (`s4_roll_mean`, $\text{SHAP} = +16.2\text{ cycles}$) and stable core speed (`s9_roll_mean`, $\text{SHAP} = +8.1\text{ cycles}$).
- **Low-RUL Late Life Engine**: Predicted RUL = $\mathbf{14.28\text{ cycles}}$ ($\text{base } 86.52 - 72.24$). Pushed downward severely by elevated LPT exhaust temperature (`s4_roll_mean`, $\text{SHAP} = -28.4\text{ cycles}$) and degraded HPC pressure (`s11_roll_mean`, $\text{SHAP} = -14.1\text{ cycles}$).

---

## 6. Machine 2 Synthetic Scenario Investigation

The AI4I explainer was evaluated on simulated Machine 2 operating points:
1. **Normal Baseline**: $vib = 1.40\text{ mm/s}$, speed $= 1500\text{ RPM}$, torque $= 38\text{ Nm}$, wear $= 45\text{ min}$. Model $P = 0.002$ (Threshold $0.91$). All features Mitigate risk.
2. **Degraded Episode**: $vib = 4.25\text{ mm/s}$ (Synthetic trigger active), speed $= 1380\text{ RPM}$, torque $= 65\text{ Nm}$, wear $= 215\text{ min}$, temp $= 58^\circ\text{C}$. Model $P = 0.998$ (Threshold $0.91$). Primary drivers: tool wear ($\text{SHAP} = +3.85$) and torque/speed ratio ($\text{SHAP} = +2.41$).

> [!WARNING]
> **Distribution-Shift & Causality Disclosure**:
> - **Distribution Shift**: The AI4I model was trained on empirical CNC milling center data. Machine 2 operates in the synthetic digital twin simulation with configured mechanical noise and thermal constants.
> - **Physical Causality Disclaimer**: SHAP measures feature sensitivity in the model's decision function. **SHAP does NOT prove that vibration physically causes bearing failure.**

---

## 7. Verification & Test Suite Summary

The Phase 11 test suite (`tests/test_explainability.py`) contains **13 comprehensive unit and integration tests**:

| Test Class | Test Case | Target Verification | Result |
| :--- | :--- | :--- | :---: |
| `TestExplainerInitialization` | `test_ai4i_explainer_loading` | Model loads with 10 features, $\tau=0.91$, base value extracted | **PASSED** |
| `TestExplainerInitialization` | `test_cmapss_explainer_loading` | Regressor loads with 48 features, valid base cycles | **PASSED** |
| `TestLeakageAndFeatureIntegrity` | `test_excluded_features_never_in_explainer` | Barred leakage features (UDI, Product ID, TWF, HDF, PWF, OSF, RNF) strictly absent | **PASSED** |
| `TestLeakageAndFeatureIntegrity` | `test_feature_dictionary_covers_all_model_features` | 100% of model features have documented human interpretations | **PASSED** |
| `TestAdditiveShapConsistency` | `test_ai4i_log_odds_additive_identity` | Exact additive check in log-odds space ($|\text{margin} - (\text{base} + \sum \text{SHAP})| < 10^{-4}$) | **PASSED** |
| `TestAdditiveShapConsistency` | `test_cmapss_cycles_additive_identity` | Exact additive check in operational cycle space | **PASSED** |
| `TestPredictionInvariance` | `test_predictions_unchanged_before_and_after_shap` | Model `predict_proba` identical before vs after SHAP explanation | **PASSED** |
| `TestRepresentativeLocalCases` | `test_local_cases_artifact_exists_and_valid` | Full coverage of TP, TN, FP, FN with verified labels and thresholds | **PASSED** |
| `TestServiceLayerAndMachine2` | `test_service_single_reading_explanation` | Real-time Pydantic v2 explanation inference and schema validation | **PASSED** |
| `TestServiceLayerAndMachine2` | `test_machine2_synthetic_explanation_and_disclaimers` | M2 scenario evaluation with shift notices and causality disclaimers | **PASSED** |
| `TestServiceLayerAndMachine2` | `test_deterministic_local_explanation` | Identical inputs produce identical SHAP values and narratives | **PASSED** |
| `TestServiceLayerAndMachine2` | `test_safe_handling_of_missing_or_partial_features` | Safe baseline imputation without KeyError or column duplication | **PASSED** |
| `TestServiceLayerAndMachine2` | `test_global_importance_csv_matches_model_features` | Verifies 10-feature global importance CSV monotonicity and ranking | **PASSED** |

### Regression Suite Status:
- **Phase 11 Tests**: 13 / 13 Passed (100%)
- **Total Project Tests**: **101 / 101 Passed (100%)**
- **Zero Regressions** across Phase 0 through Phase 10.
