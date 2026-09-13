# Textile Manufacturing Loom Telemetry Baseline Model Benchmark Report

**Project**: NirmaanAI — AI-Powered Manufacturing Intelligence & Decision Platform  
**Dataset ID**: `textile`  
**Epistemic Status**: `CONTROLLED_SYNTHETIC`  
**Task**: Unsupervised Loom Telemetry Anomaly Detection & Degradation Tracking  
**Features Count**: 16 high-frequency vibration, acoustic, and thermal telemetry features  
**Tuning Status**: `NOT_STARTED`

---

## 1. Dataset Overview & Epistemic Characterization

The textile dataset captures multi-sensor telemetry across industrial weaving looms. As a `CONTROLLED_SYNTHETIC` benchmark without external binary ground truth labels, model evaluation focuses on unsupervised anomaly detection, reconstruction fidelity, and distribution contrast:

| Partition | Total Sensor Readings | Nominal Baseline State |
|---|---|---|
| **Train** | 30,240 | Nominal operational loom conditions |
| **Validation** | 6,480 | Independent operational window for score calibration |
| **Test (Holdout)** | 6,480 | Final blind holdout evaluation (Evaluated Once) |

---

## 2. Experimental Candidate Baselines

Evaluated on `val.parquet` (6,480 readings):

| Candidate Model | Mean Anomaly Score | Std Anomaly Score | 95th Percentile | Min Anomaly Score |
|---|---|---|---|---|
| **Isolation_Forest_Detector** | **-0.4933** | **0.0185** | **-0.4650** | **-0.5642** |
| PCA_Reconstruction_Detector | -0.1245 | 0.0412 | -0.0512 | -0.6841 |
| Robust_ZScore_Detector | -1.8420 | 0.8410 | -0.9210 | -6.4210 |

---

## 3. Validation Champion Selection

- **Locked Champion**: `Isolation_Forest_Detector`
- **Primary Metric**: Anomaly score distribution stability (Mean = `-0.4933`, Std = `0.0185`)
- **Rationale**: Isolation Forest effectively partitions multi-modal vibration-thermal anomalies without assuming linear Gaussian ellipsoids, providing a robust nominal threshold envelope for loom health monitoring.

---

## 4. Final Blind Holdout Evaluation (Test Set)

Evaluated **exactly once** on `test.parquet` (6,480 readings):

| Metric | Score | Industrial Interpretation |
|---|---|---|
| **Mean Anomaly Score** | **-0.4972** | Consistent alignment with validation nominal baseline (-0.4933) |
| **Std Anomaly Score** | **0.0189** | Controlled variance demonstrating stability under nominal operations |
| **95th Percentile Score** | **-0.4680** | Upper bound for nominal loom operating envelope |
| **5th Percentile Score** | **-0.5302** | Early alert boundary for degradation tracking |
| **Minimum Score (Peak Anomaly)**| **-0.5691** | Peak transient outlier captured cleanly |

---

## 5. Artifacts Locked

- `models/benchmarks/textile/model_comparison.csv`
- `models/benchmarks/textile/validation_metrics.json`
- `models/benchmarks/textile/final_test_metrics.json`
- `models/benchmarks/textile/training_config.json`
- `models/benchmarks/textile/benchmark_metadata.json`
- `models/benchmarks/textile/locked_baseline_model.joblib`
