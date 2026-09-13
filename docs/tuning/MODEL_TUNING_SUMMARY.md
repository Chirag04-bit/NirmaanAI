# NirmaanAI — Model Tuning & Validation Summary
## Post-Phase-25 Research Extension: Dataset-Wise Execution & Scientific Validation

---

### 1. Executive Summary
In this **Post-Phase-25 Research Extension**, systematic hyperparameter tuning and model optimization were conducted across all **9 NirmaanAI manufacturing datasets (10 distinct industrial predictive tasks)**.

All research adhered strictly to non-negotiable methodology rules:
1. **Benchmark Immutability**: `models/benchmarks/` remains completely frozen and unmodified. All tuned artifacts reside strictly in `models/tuned/<task>/`.
2. **Absolute Test-Set Blindness**: Held-out test sets (`test.parquet`) participated in **zero** training, feature selection, preprocessing fitting, sampling, hyperparameter search, candidate comparison, threshold selection, or model choice. Test sets were evaluated **exactly once** after champion configurations were locked.
3. **Scientific Restraint**: Hyperparameter tuning was never forced. If a tuned model failed to demonstrate a meaningful, statistically defensible validation improvement ($\Delta \ge 0.005$ on PR-AUC/ROC-AUC, $\Delta \ge 0.25$ cycles on C-MAPSS RMSE, $\Delta \ge 0.10\%$ on Electricity WAPE, or $\Delta \ge 0.10$ on anomaly contrast ratios), the baseline benchmark was formally **retained**.
4. **Pre-Registered Anomaly Metrics**: For unsupervised anomaly tracking, evaluation metrics (ADCR and MASI) were defined mathematically prior to model selection; raw anomaly scores were never conflated with classification accuracy.
5. **Data Integrity**: Canonical source dataset `data/synthetic/auto_components/operational_losses.csv` was verified before and after execution with MD5 hash `34B12582B32D81E3121429C55EBF74E8`.

**Result Summary**:
- **Total Tasks**: 10
- **Tuned Model Accepted**: 5 tasks (50%)
- **Baseline Retained**: 5 tasks (50%)
- **Total Configurations Evaluated**: 267 deterministic configurations (all `random_state=42`)
- **Regressions**: 0 regressions (458 passed, 2 skipped, 0 failed across full test suite).

---

### 2. Global Tuning & Validation Results

| # | Task Identifier | Epistemic Status | Baseline Champion | Tuned Champion | Configs | Baseline Val | Tuned Val | Val Rel Imprv | Baseline Test | Tuned Test | Test Delta | Decision |
| :-: | :--- | :--- | :--- | :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :--- |
| **1** | `manufacturing_production` | `REAL_WORLD_OBSERVATIONAL` | RF Weighted | RF_n200_d8_l2_sqrt_Wtd | 36 | 0.3547 | 0.3520 | -0.77% | 0.3141 | 0.3090 | -0.0051 (-1.64%) | **BASELINE_RETAINED** |
| **2** | `secom` | `REAL_MANUFACTURING_METRICS` | XGB Weighted | XGB_d4_lr0.08_col0.5_spw10_Nat | 32 | 0.2669 | **0.4733** | **+77.36%** | 0.1374 | **0.1964** | **+0.0590 (+42.94%)** | **TUNED_MODEL_ACCEPTED** |
| **3** | `industrial_iot_failure` | `CONTROLLED_INDUSTRIAL_SIMULATOR` | LR Sampled | LR_C1.0_l2_bal_Nat | 12 | 0.7607 | 0.7607 | +0.00% | 0.7596 | 0.7596 | 0.0000 (0.00%) | **BASELINE_RETAINED** |
| **4** | `ai4i` | `CONTROLLED_SYNTHETIC` | RF Natural | RF_n200_d8_l1_None_Nat | 14 | 0.8967 | 0.8997 | +0.33% | 0.9099 | 0.9135 | +0.0035 (+0.39%) | **BASELINE_RETAINED** |
| **5** | `cmapss` | `HIGH_FIDELITY_PHYSICS_SIMULATION` | XGB Regressor | XGB_n150_d6_lr0.03 | 35 | 12.8983 | **11.4643** | **+11.12%** | 13.3251 | **13.0794** | **-0.2457 (-1.84%)** | **TUNED_MODEL_ACCEPTED** |
| **6** | `electricity` | `REAL_INDUSTRIAL_TELEMETRY` | XGB Regressor | XGB_n200_d8_lr0.03_mcw1 | 54 | 0.0652 | **0.0620** | **+4.89%** | 0.0663 | **0.0627** | **-0.0035 (-5.30%)** | **TUNED_MODEL_ACCEPTED** |
| **7** | `industrial_iot_rul` | `CONTROLLED_INDUSTRIAL_SIMULATOR` | XGB Regressor | XGB_d6_lr0.05_n150 | 16 | 48.4887 | 48.3192 | +0.35% | 48.5980 | 48.3798 | -0.2181 (-0.45%) | **BASELINE_RETAINED** |
| **8** | `manufacturing_defects` | `REAL_MANUFACTURING_METRICS` | RF Natural | RF_n100_dNone_l4 | 24 | 0.8184 | **0.8389** | **+2.52%** | 0.8675 | **0.8935** | **+0.0261 (+3.01%)** | **TUNED_MODEL_ACCEPTED** |
| **9** | `textile` | `CONTROLLED_SYNTHETIC` | Isolation Forest | PCA_comp6 | 22 | 0.8553 | **2.0618** | **+141.06%** | 0.9431 | **2.8024** | **+1.8593 (+197.14%)** | **TUNED_MODEL_ACCEPTED** |
| **10** | `synthetic_factory` | `CONTROLLED_SYNTHETIC` | Isolation Forest | IF_n100_cauto_f1.0 | 22 | 4.7288 | 4.7288 | 0.00% | 2.1024 | 2.1024 | 0.0000 (0.00%) | **BASELINE_RETAINED** |

---

### 3. Detailed Analysis of Accepted Models

#### Priority 2: UCI SECOM Semiconductor Wafer Defect Classification
- **Breakthrough**: Feature fraction subsampling (`colsample_bytree=0.5`).
- **Mechanism**: In a regime of 436 features and heavy sensor collinearity, standard gradient boosting repeatedly split on redundant, high-variance sensors. Subsampling forced the ensemble to learn diverse defect representations across independent sensor banks.
- **Validation PR-AUC**: Improved from 0.2669 to 0.4733 (+77.36%).
- **Holdout Test PR-AUC**: Increased from 0.1374 to 0.1964 (+42.94%).
- **Operational Impact**: Optimized validation threshold ($\tau=0.20$) unlocked 50% holdout defect recall (6 of 12 defective wafers detected) with 0.19 precision, compared to 0.0% recall under standard default probability thresholds.

#### Priority 5: NASA C-MAPSS FD001 Turbofan Engine RUL
- **Breakthrough**: Step size shrinkage (`learning_rate=0.03`) with expanded estimators (150 trees).
- **Mechanism**: Grouped engine holdouts (Engines 1–70 train, 71–85 val, 86–100 test) prevent trajectory memorization. Smaller gradient steps prevented premature early-cycle RUL degradation predictions.
- **Validation RMSE**: Reduced from 12.90 to 11.46 cycles (+11.12% relative gain).
- **Holdout Test RMSE**: Reduced from 13.33 to 13.08 cycles on completely unseen engine trajectories.

#### Priority 6: Electricity Consumption Time-Series Forecasting
- **Breakthrough**: Deeper tree depth (`max_depth=8`) coupled with small step size (`lr=0.03`).
- **Mechanism**: Allowed the tree to capture non-linear cross-interactions between weekly seasonal lag features (lag 672) and sub-daily shift ramps without leaf over-fitting.
- **Validation WAPE**: Dropped from 6.52% to 6.20% (+4.89% relative improvement).
- **Holdout Test WAPE**: Dropped from 6.63% to 6.27% (test MAE reduced by over 1.05 kW).

#### Priority 8: Manufacturing Defects Quality Classification
- **Breakthrough**: Minimum leaf size regularization (`min_samples_leaf=4`).
- **Mechanism**: Setting leaf sample count to 4 prevented the random forest from isolating individual outlier parts at leaf boundaries, smoothing class probabilities.
- **Validation ROC-AUC**: Increased from 0.8184 to 0.8389 (+0.0206).
- **Holdout Test ROC-AUC**: Rose from 0.8675 to 0.8935 (+0.0261) with 99.75% defect recall retained.

#### Priority 9: Textile Loom Telemetry Anomaly Detection
- **Breakthrough**: Low-dimensional PCA Subspace Reconstruction ($k=6$).
- **Mechanism**: Axis-aligned Isolation Forest splits diffused subtle multi-channel sensor correlations. Learning the 6-dimensional physical operating manifold via PCA allowed orthogonal deviations to manifest as crisp, high-amplitude reconstruction residuals.
- **Validation ADCR**: Expanded from 0.8553 to 2.0618 (+141.06%).
- **Holdout Test ADCR**: Expanded to 2.8024 (+197.14%), providing exceptional signal-to-noise separation for prospective degradation monitoring.

---

### 4. Scientific Rigor & Retained Baselines

In 5 of the 10 tasks, hyperparameter tuning did not produce a statistically defensible validation improvement exceeding pre-registered acceptance thresholds:

1. **Manufacturing Production (`manufacturing_production`)**:
   - Best tuned candidate yielded validation PR-AUC of 0.3520 vs baseline 0.3547 (-0.0027 delta).
   - In keeping with non-negotiable rules, the baseline `Random_Forest_Weighted` was strictly **retained**.
2. **Industrial IoT Failure Prediction (`industrial_iot_failure`)**:
   - Baseline `Logistic_Regression_Sampled` achieved validation PR-AUC 0.7607 and test recall of 97.1%.
   - Alternative regularizers and tree candidates either degraded failure recall or matched baseline PR-AUC (delta = 0.0000). Baseline **retained**.
3. **AI4I 2020 Predictive Maintenance (`ai4i`)**:
   - Tuned RF achieved validation PR-AUC of 0.8997 vs baseline 0.8967 (+0.0030 delta).
   - Because the improvement fell below the pre-registered significance threshold ($\Delta < 0.0050$), the baseline `Random_Forest_Natural` was **retained**.
4. **Industrial IoT Remaining Useful Life (`industrial_iot_rul`)**:
   - Evaluated across 500,000 distinct machine records (350,000 train).
   - Tuned candidate yielded validation RMSE of 48.32 vs baseline 48.49 days (-0.17 day delta).
   - Delta fell well below the 0.50-day significance threshold; baseline **retained**.
5. **Synthetic Factory Anomaly Tracking (`synthetic_factory`)**:
   - Baseline Isolation Forest configuration (`n_estimators=100, contamination='auto', max_features=1.0`) was confirmed to be the exact global empirical optimum of the search space (validation MASI = 4.7288; delta = 0.0000). Baseline **retained**.

---

### 5. Architectural & Pipeline Isolation

All generated artifacts adhere to strict file and metadata isolation:
- **`models/benchmarks/`**: Completely untouched and verified against git commit `36e9013`.
- **`models/tuned/<task>/`**: Contains 7 self-contained artifacts per task:
  1. `validation_metrics.json`
  2. `final_test_metrics.json`
  3. `model_comparison.csv`
  4. `tuning_config.json`
  5. `tuning_metadata.json`
  6. `locked_tuned_model.joblib`
  7. `improvement_summary.json`
- **Global Rollup**: `models/tuned/global_tuning_summary.json` captures all 10 task trajectories.
- **Source Checksum**: `operational_losses.csv` verified at `34B12582B32D81E3121429C55EBF74E8`.

---

### 6. Verification Suite
The dedicated tuning test suite (`tests/tuning/`) comprises 21 automated tests covering:
1. `test_tuning_isolation.py`: Verifies zero alteration of benchmark files and correct tuned directory structure.
2. `test_tuning_test_holdout.py`: Verifies test-set blindness and one-time evaluation flags.
3. `test_tuning_no_leakage.py`: Verifies column quarantines, chronological ordering, and engine-grouped holdouts.
4. `test_tuning_reproducibility.py`: Verifies deterministic seeds and artifact reloadability.
5. `test_task_tuning_details.py`: Validates mathematical metric definitions (ADCR, MASI) and data checksum.

All 21 tuning tests pass cleanly, and full repository regression stands at **458 passed, 2 skipped, 0 failed**.
