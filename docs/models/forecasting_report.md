# NirmaanAI — Phase 9 Model Report: Production & Energy Forecasting

**Subsystem**: Multi-Horizon Energy Demand & Production Throughput Forecasting  
**Module**: Phase 9  
**Version**: 1.0.0  
**Date**: September 2026  
**Author**: NirmaanAI Core Research Team  
**Institution**: Institute of Engineering & Management (IEM), Kolkata  
**Project Guide**: Prof. Kuntal Mondal  

---

## 1. Executive Summary
Phase 9 implements NirmaanAI's **Production & Energy Forecasting Subsystem**, providing manufacturing MSMEs with multi-horizon predictive intelligence over electrical energy consumption, downstream electricity expenditure in Indian Rupees (INR), and production throughput volume.

### Core Architectural Distinctions:
- **Phase 6**: Machine Failure Classification & RUL Regression (Predictive Maintenance)
- **Phase 7**: Multivariate Telemetry Anomaly Detection (Unsupervised Health Monitoring)
- **Phase 8**: Production Flow Bottleneck Prediction (Flow Intelligence)
- **Phase 9**: Production Throughput & Energy Demand Forecasting (Resource & Capacity Intelligence)

### Key Achievements:
1. **Empirical Grid Energy Benchmark (UCI `MT_124`)**:
   - Evaluated across 26,281 hourly timestamps spanning 2012–2014.
   - Baseline-first progression: Persistence (58.89 RMSE / 12.56% WAPE) $\to$ Seasonal Baseline (55.99 RMSE / 13.29% WAPE) $\to$ Ridge (34.99 RMSE / 8.25% WAPE) $\to$ Random Forest (27.96 RMSE / 6.84% WAPE) $\to$ **XGBoost Champion** (**26.23 RMSE / 6.50% WAPE**, $R^2 = \mathbf{0.9605}$).
2. **Synthetic Shop-Floor Plant Energy Demand**:
   - Plant-wide aggregated active power across 5 machines (`M1` to `M5`) over 30 days (720 hourly records).
   - **XGBoost Champion** selected strictly by validation RMSE (0.2658 kW vs 0.2801 kW for Random Forest), achieving **0.23 kW RMSE / 0.31% WAPE** on untouched holdout test data.
3. **Downstream Electricity Tariff Costing (INR)**:
   - Derived operational calculation applying configured MSME tariff rules: Base tariff = **₹8.50/kWh**, Peak tariff = **₹12.50/kWh** (strictly active during 18:00–22:00).
   - Over the holdout test window (83 hours), actual derived cost of **₹45,931.39** vs predicted derived cost of **₹45,920.72** (variance: **-₹10.67**, error: **0.02%**; preliminary run: ₹42,204.09 vs ₹42,208.57, error: 0.01%).
4. **Daily Production Throughput Forecasting**:
   - Forecasts completed units using causal planned batch quantities, shift types, and strictly historical lagging completion rates.
   - Ridge Champion achieves **10.52 units RMSE / 0.77% WAPE** ($R^2 = \mathbf{0.9938}$), reflecting the controlled scrap dynamics of the simulation.

---

## 2. Dataset Demarcation & Scientific Separation
To maintain strict research integrity, data assets are partitioned into two clearly demarcated categories:

| Dimension | Primary Empirical Benchmark | Synthetic Shop Floor Environment |
| :--- | :--- | :--- |
| **Dataset Name** | UCI Electricity Load Diagrams 2011–2014 (`04_ENERGY`) | Synthetic Factory 10 (`10_SYNTHETIC_FACTORY`) |
| **Asset Location** | `DATASET/04_ENERGY/raw/LD2011_2014.txt` | `DATASET/10_SYNTHETIC_FACTORY/synthetic/` |
| **Entity Nature** | Real-world utility grid electrical client (`MT_124`) | Controlled discrete manufacturing floor (`M1` to `M5`) |
| **Data Type** | Measured grid telemetry (15-min intervals) | Generative simulation telemetry (5-min intervals) & jobs |
| **Scientific Role** | Empirical time-series forecasting benchmark | Manufacturing energy coupling & throughput simulation |
| **Research Demarcation** | **Never represented as factory machinery.** Represents real utility-scale diurnal power demand. | **Controlled scenario validation only.** Does NOT constitute physical factory validation. |

### 2.1. UCI Meter Selection Provenance (`MT_124`)
A research-integrity audit was performed to document why meter `MT_124` was selected from among the 370 client columns in the UCI Electricity Load Diagrams dataset:
- **Historical Origin**: Client `MT_124` was established during **Phase 3 Exploratory Data Analysis** (documented in [notebooks/04_eda_energy_consumption.ipynb](file:///c:/NIRMAAN%20AI/notebooks/04_eda_energy_consumption.ipynb) and [docs/eda/eda_summary_report.md](file:///c:/NIRMAAN%20AI/docs/eda/eda_summary_report.md), Section 2.4).
- **Selection Criterion**: Chosen strictly for **data-quality and completeness reasons**:
  1. **Continuous History**: Out of 370 meters in `LD2011_2014.txt`, over 210 meters contain leading zeros for 1–3 years because meters were added incrementally. `MT_124` is one of the verified subset active continuously from day 1 (`2011-01-01 00:15:00`) to `2015-01-01` with 140,244 non-zero readings.
  2. **Industrial Load Magnitude**: Exhibits an average active power draw of $280.76\text{ kW}$ (max $765.55\text{ kW}$), representing commercial/industrial scale consumption rather than sub-2 kW domestic profiles.
  3. **Diurnal Cyclicity**: Exhibits strong 24-hour diurnal operational cyclicity characteristic of plant operations.
- **Independence Guarantee**: **Client `MT_124` was NOT selected after model forecasting comparisons or test performance tuning.** It was pre-specified as the project's empirical energy profile during Phase 3 EDA long before Phase 9 models were formulated.

---

## 3. Explicit Target Definitions & Temporal Resolutions

| Target ID | Target Variable | Dataset Source | Native Resolution | Model Resolution | Forecast Horizon | Description |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Target A** | `power_kw` | UCI `MT_124` | 15-minute | 1-hour average | 24 hours ($h=24$) | Mean active electricity demand (kW) for empirical client |
| **Target B** | `plant_power_kw` | Synthetic Sensors | 5-minute | 1-hour average | 24 hours ($h=24$) | Total active electrical load summed across machines `M1`–`M5` |
| **Target C** | `target_completed_units` | Synthetic Jobs | Per-job | Daily aggregated | 1 day ($h=1$) | Total finished batch units completed across the plant |

---

## 4. Native Data Frequency & Semantic Lag Feature Mapping
Lags were selected strictly after confirming the temporal sampling resolution of each dataset:

### Hourly Resolution Lag Mapping (Targets A & B):
- **Native Frequency**: UCI resampled from 15-min to 1-hour; Synthetic Sensors resampled from 5-min to 1-hour.
- `lag_1h` ($t-1$): Prior hour active load.
- `lag_2h` ($t-2$): Two hours prior active load.
- `lag_3h` ($t-3$): Three hours prior active load.
- `lag_24h` ($t-24$): Same hour previous day (captures 24-hour diurnal operational cycle).
- `lag_168h` ($t-168$): Same hour previous week (captures 7-day weekly seasonality and weekend shift patterns).
- `rolling_mean_6h`: Prior 6-hour moving average (strictly excluding current step via `shift(1)`).
- `rolling_mean_24h`: Prior 24-hour moving average (captures trailing daily baseline).
- `rolling_std_24h`: Prior 24-hour load volatility.
- `sin_hour`, `cos_hour`: Continuous Fourier cyclical encoding of hour-of-day ($[0, 23]$ mapped to $[-\pi, \pi]$).
- `sin_dow`, `cos_dow`: Continuous Fourier cyclical encoding of day-of-week ($[0, 6]$ mapped to $[-\pi, \pi]$).

### Production Throughput Lag Mapping (Target C):
- `total_planned_units`: Scheduled batch quantity for the target day (known at scheduling time).
- `total_planned_jobs`: Number of scheduled jobs across all machines.
- `lag_completed_1d` ($t-1\text{d}$): Completed units on the previous operating day.
- `lag_completed_7d` ($t-7\text{d}$): Completed units on the same day last week.
- `prior_completion_rate_3d`: 3-day rolling completion ratio ($\text{completed} / \text{planned}$) strictly lagged by 1 day.

---

## 5. Strict Chronological Train / Validation / Test Splitting
Time-series data was partitioned strictly forward-in-time to ensure no future information leaks into training:

```
Timeline: ─────────────────────────────────────────────────────────────►
          [   Train Split (70%)   ] [ Val Split (15%) ] [ Test Split (15%) ]
          ▲                       ▲                   ▲
          Start Date              T_val               T_test (Holdout)
```

- **UCI Electricity (`MT_124`)**:
  - Total records: 26,281 hourly timestamps (2012-01-08 to 2014-12-31 after 168h lag initialization).
  - **Train**: 18,279 hours (2012-01-08 to 2014-02-07).
  - **Validation**: 3,917 hours (2014-02-07 to 2014-07-20). Used strictly for model selection.
  - **Test (Holdout)**: 3,917 hours (2014-07-20 to 2014-12-31). Evaluated once for final reporting.
- **Synthetic Shop Floor Energy**:
  - Total records: 552 hourly timestamps (after 168h lag warm-up).
  - **Train**: 386 hours.
  - **Validation**: 83 hours.
  - **Test (Holdout)**: 83 hours.
- **Synthetic Production Throughput**:
  - Total records: 23 daily records (after 7-day lag warm-up).
  - **Train**: 16 days.
  - **Validation**: 3 days.
  - **Test (Holdout)**: 4 days.

---

## 6. Multi-Model Forecasting Benchmark Results

### 6.1. Empirical Grid Electricity Demand (`MT_124`, 1-Hour Resolution)

| Model | Model Nature | Val RMSE | Val WAPE | Test MAE | Test RMSE | Test $R^2$ | Test WAPE | Test sMAPE |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Persistence Baseline** | Naive Lag-24h | 55.71 | 0.1354 | 26.65 | 58.89 | 0.8008 | 12.56% | 12.01% |
| **Seasonal Diurnal Baseline** | Historical Conditional Mean | 44.66 | 0.1105 | 28.21 | 55.99 | 0.8199 | 13.29% | 13.77% |
| **Ridge Regression** | L2 Regularized Linear Model | 32.67 | 0.0834 | 17.51 | 34.99 | 0.9297 | 8.25% | 8.08% |
| **Random Forest Regressor** | Bagged Decision Ensembles | 26.27 | 0.0670 | 14.51 | 27.96 | 0.9551 | 6.84% | 6.70% |
| **XGBoost Regressor (Champion)** | Gradient Boosted Trees | **25.36** | **0.0647** | **13.80** | **26.23** | **0.9605** | **6.50%** | **6.37%** |

*Analysis*: On real-world empirical electricity data, XGBoost reduces test RMSE by **55.5%** relative to the Persistence baseline and achieves an $R^2$ of **0.9605** with a WAPE of **6.50%**, demonstrating high predictive fidelity across diurnal shifts.

---

### 6.2. Synthetic Shop Floor Plant Energy (M1–M5 Aggregated Load)

| Model | Model Nature | Val RMSE (kW) | Val WAPE | Test MAE (kW) | Test RMSE (kW) | Test WAPE | Test $R^2$ |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Persistence Baseline** | Naive Lag-24h | 0.3200 | 0.43% | 0.2743 | 0.3207 | 0.45% | -0.9557 |
| **Seasonal Diurnal Baseline** | Historical Conditional Mean | 0.6481 | 0.84% | 0.7937 | 0.8529 | 1.31% | -12.8087 |
| **Ridge Regression** | L2 Regularized Linear Model | 0.2917 | 0.39% | 0.2673 | 0.3424 | 0.44% | -1.2336 |
| **Random Forest Regressor** | Bagged Decision Ensembles | 0.2801 | 0.37% | 0.1903 | 0.2384 | 0.32% | -0.0829 |
| **XGBoost Regressor (Champion)** | Gradient Boosted Trees | **0.2658** | **0.35%** | **0.1874** | **0.2335** | **0.31%** | **-0.0391** |

**Model Attribution Resolution**:
- **Champion Selected by Validation Performance Only**: XGBoost achieved the lowest validation RMSE ($0.2658\text{ kW}$ vs $0.2801\text{ kW}$ for Random Forest) and is unambiguously designated as the single plant energy champion model.
- **Controlled Aggregation Nature**: Total plant power is mathematically derived in the generator as the sum of baseline machine rated power ($15 + 22 + 11 + 4.5 + 7.5 = 60.0\text{ kW}$) plus zero-mean Gaussian noise ($\sigma = 0.4\text{ kW}$ per machine). Hourly averaging across twelve 5-minute readings yields an empirical standard deviation of $\sim 0.23\text{ kW}$. The models autoregressively capture this stationary mean. Consequently, this benchmark represents a **controlled synthetic aggregation and time-series consistency task**, rather than independent empirical validation.

---

### 6.3. Synthetic Production Throughput (Daily Completed Units)

| Model | Model Nature | Val RMSE (units) | Val WAPE | Test MAE (units) | Test RMSE (units) | Test WAPE | Test $R^2$ |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Persistence Baseline** | Naive Lag-1d | 245.38 | 18.90% | 171.00 | 197.68 | 14.95% | -1.1740 |
| **Ridge Regression (Champion)** | L2 Regularized Linear Model | **15.02** | **1.28%** | **8.84** | **10.52** | **0.77%** | **0.9938** |
| **Random Forest Regressor** | Bagged Decision Ensembles | 54.21 | 4.10% | 21.37 | 26.09 | 1.87% | 0.9621 |
| **XGBoost Regressor** | Gradient Boosted Trees | 35.13 | 2.38% | 7.32 | 9.72 | 0.64% | 0.9947 |

**Synthetic Production Forecast Research-Integrity Audit**:
1. **Sample & Split Counts**:
   - Total records: 23 daily observations (derived from 30 total simulation days after 7-day lag initialization).
   - Chronological Partition: Train = 16 days (70%), Validation = 3 days (15%), Holdout Test = 4 days (15%).
2. **Target & Causal Predictors**:
   - Target: `target_completed_units` (daily completed units across all jobs).
   - Causal Predictors: `total_planned_jobs`, `total_planned_units`, `lag_completed_1d`, `lag_completed_7d`, `prior_completion_rate_3d`, `day_of_week`, `is_weekend`.
   - Strictly Excluded: `actual_end`, future cycle times, contemporaneous scrap, and machine failure outcomes cannot enter predictors.
3. **Physical Reason for High Performance ($R^2 = 0.9938$, $\text{WAPE} = 0.77\%$)**:
   - In the synthetic generator (`synthetic_generator.py`), scrap rate is bounded between $1.0\%$ and $3.0\%$ (mean $\approx 1.9\%$).
   - Mathematically: $\text{Completed} = \text{Planned} \times (1 - \text{scrap\_rate}) \approx 0.981 \times \text{Planned}$.
   - Pearson correlation between `total_planned_units` (known at schedule time) and `target_completed_units` is **0.9988**.
   - **Crucial Research Disclosure**: This near-deterministic mapping is an intrinsic artifact of the controlled synthetic simulation. It must NOT be interpreted as indicative of chaotic real-world factory floors where supply disruptions, labor shortages, and unmodeled machine breakdowns occur.

---

## 7. Downstream Tariff & Rupee Cost Estimation

### 7.1. Operational Costing Architecture
Downstream cost calculation is an **operational financial calculation derived from physical power forecasts and configured tariff assumptions**, NOT an independent machine learning model metric:

$$\text{Forecasted Cost (INR)} = \sum_{t} \hat{P}_t \times 1.0\text{ h} \times \text{Tariff}(t)$$

Where configured MSME simulation assumptions from `factory_defaults.yaml` define:
- **Base Electricity Rate**: $\text{₹}8.50\text{ per kWh}$ (20 hours daily: 22:00 to 18:00).
- **Peak Electricity Rate**: $\text{₹}12.50\text{ per kWh}$ (4 hours daily: 18:00 to 22:00 evening grid surcharge).

### 7.2. Holdout Test Split Cost Validation (83 Hours)

| Financial / Energy Metric | Actual Telemetry | Champion Model Forecast (XGBoost) | Estimation Error / Variance |
| :--- | :---: | :---: | :---: |
| **Total Energy (kWh)** | 4,980.08 | 4,979.13 | $-0.95\text{ kWh}$ ($-0.02\%$) |
| **Base Period Energy (kWh)** | 4,079.91 | 4,079.60 | $-0.31\text{ kWh}$ ($-0.01\%$) |
| **Peak Period Energy (kWh)** | 900.17 | 899.53 | $-0.64\text{ kWh}$ ($-0.07\%$) |
| **Peak Energy Ratio** | 18.08% | 18.07% | $-0.01\%$ |
| **Total Electricity Cost (INR)** | **₹45,931.39** | **₹45,920.72** | **-₹10.67 (-0.02%)** |
| - Base Period Cost (INR) | ₹34,679.26 | ₹34,676.64 | -₹2.62 |
| - Peak Period Cost (INR) | ₹11,252.14 | ₹11,244.08 | -₹8.06 |

*(Audit Note: In the initial preliminary execution before final zero-leakage target dropping, the 83-hour window computed ₹42,204.09 vs ₹42,208.57. Following strict target column exclusion, the exact reproducible figures are ₹45,931.39 vs ₹45,920.72. Both demonstrate <0.05% derived operational estimation variance.)*

---

## 8. Real-Time Service Architecture: 4-Stage Decoupled Pipeline
The service layer [forecasting_service.py](file:///c:/NIRMAAN%20AI/src/services/forecasting_service.py) maintains strict separation between predictive model inferences and downstream business logic:

```
┌────────────────────────────────────────────────────────┐
│ Stage 1: Pure Physical Inference                       │
│ Model predicts hourly active load: \hat{y} (kW)        │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Stage 2: Temporal Tariff Window Classification         │
│ Classify timestamp: Peak (18-22h) vs Base               │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Stage 3: Rupee Cost Projection                         │
│ Cost = \hat{y}_{kWh} \times Tariff(t)                  │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Stage 4: Operational Decision Alert                     │
│ If peak ratio > 25%: Alert shift reschedule advisory    │
└────────────────────────────────────────────────────────┘
```

---

## 9. Automated Test Suite Verification
All 7 unit and integration tests in `tests/test_forecasting.py` passed cleanly:
```
tests/test_forecasting.py::test_metric_calculations_stability PASSED     [ 14%]
tests/test_forecasting.py::test_chronological_split_isolation PASSED     [ 28%]
tests/test_forecasting.py::test_zero_lookahead_feature_causality PASSED  [ 42%]
tests/test_forecasting.py::test_zero_target_leakage_in_predictors PASSED [ 57%]
tests/test_forecasting.py::test_forecasting_models_baseline_hierarchy PASSED [ 71%]
tests/test_forecasting.py::test_forecasting_service_inference_and_tariffs PASSED [ 85%]
tests/test_forecasting.py::test_production_throughput_forecast_service PASSED [100%]
============================== 7 passed in 2.44s ==============================
```

---

## 10. Research Safeguards & Academic Limitations
1. **Empirical Grid vs Factory Shop Floor Boundary**: The UCI Electricity Load dataset represents utility-scale power draw across commercial/residential meters in Portugal. While it provides a rigorous benchmark for time-series forecasting algorithms, its physical parameters do not represent discrete machine shop floors.
2. **Synthetic Data Stationarity**: The synthetic factory energy profile reflects generative equations with Gaussian noise around rated machine power. Consequently, variance in nominal mode is minimal, yielding low absolute errors.
3. **Tariff Assumptions**: The ₹8.50 base rate and ₹12.50 peak rate represent external Indian MSME assumptions from `factory_defaults.yaml` and are not empirical discoveries of any dataset.
4. **Zero-Lookahead Guarantee**: All lag features ($y_{t-1}, y_{t-24}, y_{t-168}$) and rolling aggregations strictly exclude the contemporaneous and future observations, verified by automated perturbation testing.
