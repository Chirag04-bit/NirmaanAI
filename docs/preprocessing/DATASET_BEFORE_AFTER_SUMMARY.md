# NirmaanAI — Dataset Before & After Processing Summary

**Project**: NirmaanAI — AI-Powered Manufacturing Intelligence & Decision Platform  
**Location**: `C:\NIRMAAN AI`  
**Phase**: Strict Dataset-by-Dataset Cleaning, Preprocessing & Sampling  
**Status**: COMPLETE, ISOLATED & VERIFIED  

---

## 1. Executive Summary

This document presents the side-by-side comparative audit of dataset dimensions, data quality indicators, and target distributions before and after our independent dataset-specific cleaning and preprocessing pipelines.

---

## 2. Before vs. After Summary Table

| Dataset | Metric | Before Processing (Raw / Extracted) | After Processing (Cleaned / Model-Ready) | Notes & Impact |
|---|---|---|---|---|
| **AI4I 2020** | Rows | 10,000 | 10,000 (Train: 7k, Val: 1.5k, Test: 1.5k) | Zero rows dropped; natural distribution intact |
| | Columns | 22 (includes 7 leakage features) | 15 (14 predictors + 1 target) | Quarantined `UDI`, `Product ID`, `TWF`, `HDF`, `PWF`, `OSF`, `RNF` |
| | Missing Values | 0 | 0 | 100% complete data |
| | Target Dist. | 3.39% failures (339 / 10,000) | 3.39% in Train, Val, Test (50% in Train Sampled) | Validation & Test maintain true operational base rate |
| **NASA C-MAPSS** | Rows | 20,631 | 20,631 (Train: 14,484, Val: 3,091, Test: 3,056) | Zero rows dropped; trajectory continuity preserved |
| | Columns | 99 (includes raw & causal rolling) | 99 (98 predictors + 1 target) | Invariant sensors pruned in feature extraction |
| | Engines | 100 engines | 100 engines (Train: 70, Val: 15, Test: 15) | Strict engine grouping; zero cross-engine leakage |
| | Target RUL | Unbounded linear [0, 361] cycles | Capped piecewise linear [0, 125] cycles | Mitigates healthy baseline gradient saturation |
| **UCI SECOM** | Rows | 1,567 | 1,567 (Train: 1,096, Val: 235, Test: 236) | Zero wafer records dropped |
| | Columns | 437 | 437 (436 sensor channels + 1 target) | 154 uninformative channels pruned in feature phase |
| | Missing Values | 4,164 across retained channels | 0 (imputed via training medians) | SimpleImputer fit strictly on training wafers |
| | Target Dist. | 6.64% defects (104 / 1,567) | 6.64% in Train, Val, Test (50% in Train Sampled) | Test set untouched |
| **UCI Electricity** | Rows | 26,113 | 26,113 (Train: 18,279, Val: 3,917, Test: 3,917) | Continuous hourly timeline preserved |
| | Columns | 21 (timestamp, load, causal lags) | 21 (20 predictors + 1 target) | Zero forward-looking features |
| | Ordering | Sorted chronological | Strictly chronological ($t_{\text{train}} < t_{\text{val}} < t_{\text{test}}$) | Zero temporal shuffling |
| **Industrial IoT (Failure)**| Rows | 500,000 | 500,000 (Train: 350k, Val: 75k, Test: 75k) | Zero machine records dropped |
| | Columns | 29 | 28 (27 predictors + 1 target) | Quarantined `Remaining_Useful_Life_days` and `Machine_ID` |
| | Target Dist. | 6.01% failures | 6.01% in Train, Val, Test (50% in Train Sampled) | Test set untouched |
| **Industrial IoT (RUL)** | Rows | 500,000 | 500,000 (Train: 350k, Val: 75k, Test: 75k) | Zero machine records dropped |
| | Columns | 29 | 28 (27 predictors + 1 target) | Quarantined `Failure_Within_7_Days` and `Machine_ID` |
| | Target Dist. | Continuous mean 452.4 days | Continuous mean 452.4 days | SAMPLING_NOT_REQUIRED |
| **Production** | Rows | 1,000 | 1,000 (Train: 700, Val: 150, Test: 150) | Discrete job schedule intact |
| | Columns | 29 (includes post-event delay) | 15 (14 prospective predictors + 1 target) | Excluded realized delays and terminal statuses |
| | Target Dist. | 32.7% bottlenecks | 32.7% across all splits | Prospective predictors only |
| **Defects** | Rows | 3,240 | 3,240 (Train: 2,268, Val: 486, Test: 486) | Zero batches dropped |
| | Columns | 24 | 24 (23 predictors + 1 target) | Ordinal encoding applied to Supplier Quality |
| | Target Dist. | 84.0% defective batches | 84.0% in Train, Val, Test | Stratified balance verified |
| **Textile** | Rows | 43,200 | 43,200 (Train: 30,240, Val: 6,480, Test: 6,480) | 1-minute telemetry preserved |
| | Machines | 5 looms (TX01–TX05) | 5 looms (TX01–TX05 represented in each split) | Per-machine chronological partitioning |
| | Outliers | True degradation spikes present | 0 outliers pruned | Degradation signals preserved |
| **Synthetic Factory** | Rows | 43,200 | 43,200 (Train: 20,415, Val: 8,750, Test: 14,035) | 1-minute factory scenario preserved |
| | Stations | 5 stations (M1–M5) | 5 stations (M1–M5) | Controlled degradation on M2 preserved |
| | Split Cutoff | Unsplit time-series stream | Temporal Decision Cutoff (`2026-01-21 12:00 UTC`) | Train/Val isolated from future emergency event |
