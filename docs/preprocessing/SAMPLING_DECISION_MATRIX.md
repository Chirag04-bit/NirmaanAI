# NirmaanAI — Sampling Decision Matrix

This matrix formalizes the sampling policy across all 9 NirmaanAI manufacturing datasets.

| Dataset | Task | Imbalance | Sampling Allowed? | Strategy | Applied? | Reason |
|---|---|---|---|---|---|---|
| **AI4I 2020** | Machine Failure Classification | Severe (3.39% failures) | YES | Random Over-Sampling + Class Weighting | YES (Train Only) | Minority class has only 237 training samples; balanced training benchmark is generated for comparative evaluation. |
| **NASA C-MAPSS FD001** | Remaining Useful Life Prediction | None (Continuous Regression) | NO | `SAMPLING_NOT_REQUIRED` | NO | C-MAPSS is a continuous run-to-failure sequence. Resampling or row-dropping destroys temporal degradation causality. |
| **UCI SECOM** | Semiconductor Wafer Classification | Severe (6.64% defects) | YES | Random Over-Sampling + Cost-Sensitive Loss | YES (Train Only) | Defect instances are sparse (73 in train). Random oversampling on train partition avoids empty-space artifacts of SMOTE. |
| **UCI Electricity (MT_124)** | Hourly Load Forecasting | None (Continuous Time Series) | NO | `SAMPLING_NOT_REQUIRED` | NO | Electrical load curve requires strict chronological continuity and autocorrelation structure. Timestamp sampling is prohibited. |
| **Industrial IoT (Failure)** | Machine Failure Classification | Moderate (6.01% failures) | YES | Random Over-Sampling + Scale Pos Weight | YES (Train Only) | Large-scale failure classification; balanced training set provided while validation/test maintain natural 6% distribution. |
| **Industrial IoT (RUL)** | Equipment RUL Prediction | None (Continuous Regression) | NO | `SAMPLING_NOT_REQUIRED` | NO | Continuous longevity target; class resampling is mathematically inapplicable. |
| **Manufacturing Production** | Prospective Bottleneck Prediction | Moderate (32.7% bottlenecks) | NO | `SAMPLING_NOT_REQUIRED` (Weighting advised) | NO | Minority class is well-represented (229 cases in train). Resampling could distort discrete shop-floor scheduling sequences. |
| **Manufacturing Defects** | Batch Quality Classification | Moderate (16.0% pass batches) | NO | `SAMPLING_NOT_REQUIRED` (Weighting advised) | NO | Minority class has ample statistical support (362 cases in train). Class weighting during loss evaluation is superior to resampling. |
| **Textile Manufacturing** | Synthetic Loom Anomaly Tracking | Time-Series Telemetry | NO | `SAMPLING_NOT_REQUIRED` | NO | Continuous operational telemetry stream across 5 looms; random sampling breaks chronological sensor dynamics. |
| **Synthetic Factory (M1–M5)** | Multi-Station Health Monitoring | Scenario Telemetry Stream | NO | `SAMPLING_NOT_REQUIRED` | NO | Controlled scenario degradation stream; random sampling destroys deterministic scenario progression. |

---

### Core Principles
1. **Pristine Evaluation**: Validation and test sets are **never sampled**. They reflect the genuine operational base rate of the manufacturing plant.
2. **Train-Only Scope**: Any resampling artifact (`training_sampled.parquet`) is strictly quarantined to the training partition.
3. **Temporal Causality**: Time-series and run-to-failure degradation streams are never resampled.
