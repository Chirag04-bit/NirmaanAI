# Synthetic Factory Anomaly Tracking Tuning & Validation Report
## Post-Phase-25 Research Extension — Task 10

### 1. Dataset
- **Name**: Auto Components Factory Synthetic Telemetry Stream
- **Domain**: Automated Automotive Component Manufacturing Cells (M1–M5)
- **Input Data**: Multi-machine synchronized sensory telemetry across 5 production machines.
- **Decision Cutoff**: 2026-01-21 12:00 UTC.
- **Quarantine Safeguard**: `MAINT_0003` occurred at 2026-01-22 16:30 UTC. It is strictly excluded from all training, hyperparameter exploration, and model selection.
- **MD5 Checksum Verification**: Source file `data/synthetic/auto_components/operational_losses.csv` verified at `34B12582B32D81E3121429C55EBF74E8`.

### 2. Task
- **Objective**: Unsupervised anomaly detection and early degradation tracking prior to decision cutoff.
- **Target Variable**: None (unsupervised anomaly scoring).
- **Evaluation Type**: Unsupervised Metric Formulation with Pre-Registered Multivariate Anomaly Separation Index (MASI).

### 3. Epistemic Status
- **Classification**: `CONTROLLED_SYNTHETIC`
- **Scientific Context**: Controlled synthetic factory simulation. Explicitly acknowledged as synthetic benchmark; results are never presented as real-world industrial validation.

### 4. Baseline Champion
- **Model**: `Isolation_Forest` (Default hyperparameters: n_estimators=100, contamination='auto', max_features=1.0)
- **Baseline Source**: Commit `36e9013`, `models/benchmarks/synthetic_factory/`

### 5. Baseline Metrics
- **Validation MASI**: 4.7288
- **Validation Score Statistics**: Mean = -0.5417, Std = 0.0633, P95 = -0.4873, P5 = -0.7072
- **Frozen Baseline Test MASI**: 2.1024
- **Frozen Test Score Statistics**: Mean = -0.5336, Std = 0.0452, P95 = -0.4873, P5 = -0.6169

### 6. Tuning Objective
- **Pre-Registered Metric**: Multivariate Anomaly Separation Index (MASI)
  $$\text{MASI} = \frac{|\mu_{\text{nominal}} - \mu_{\text{val\_tail}}|}{\sigma_{\text{nominal}} + \sigma_{\text{val\_tail}} + \epsilon}$$
  where $\mu_{\text{nominal}}$ and $\sigma_{\text{nominal}}$ are computed across the pre-degradation baseline window, and $\mu_{\text{val\_tail}}$ and $\sigma_{\text{val\_tail}}$ are computed across the degradation tail preceding the decision cutoff.
- **Methodological Rule**: Raw anomaly scores are never equated to accuracy. Metric was mathematically formulated prior to model selection.
- **Success Criterion**: Validation MASI improvement $\ge 0.1000$ over baseline. If delta $< 0.1000$, baseline is strictly retained.

### 7. Candidate Models
- **Isolation Forest**: Partitioning ensembles exploring tree count (100, 150, 200), contamination fractions (auto, 0.02, 0.05), and feature fractions (0.8, 1.0).
- **PCA Reconstruction Error**: Linear subspace modeling (k=2, 4, 6).
- **Robust Z-Score**: MAD-normalized deviation scoring.

### 8. Search Space
- **Isolation Forest**: 18 configurations ($3 \times 3 \times 2$).
- **PCA Reconstruction**: 3 configurations ($k \in [2, 4, 6]$).
- **Robust Z-Score**: 1 configuration.
- Total bounded search space: 22 configurations.

### 9. Number of Configurations Evaluated
- **Evaluated**: 22 deterministic configurations (Seed = 42).
- **Test Participation**: 0 configurations evaluated on test set during exploration.

### 10. Sampling Strategy
- **Sampling**: Continuous chronological telemetry (strictly unsupervised; no artificial resampling).

### 11. Validation Protocol
- **Split Structure**: Chronological Temporal Split preceding decision cutoff (2026-01-21 12:00 UTC)
  - Train: 1,440 timesteps (first 70% of pre-cutoff window)
  - Validation: 309 timesteps (remaining 30% of pre-cutoff window)
  - Test: 309 timesteps (held-out evaluation window)
- **Quarantine Guarantee**: `MAINT_0003` (2026-01-22 16:30 UTC) was completely quarantined from prospective training and tuning.

### 12. Best Validation Configuration
- **Model**: `IF_n100_cauto_f1.0` (Identical to Baseline Configuration)
  - `n_estimators`: 100
  - `contamination`: 'auto'
  - `max_features`: 1.0
  - `random_state`: 42
- **Validation MASI**: 4.7288 (Identical to baseline)
- **Validation Improvement**: 0.0000 (0.00%)

### 13. Tuned Champion
- **Champion Configuration**: `IF_n100_cauto_f1.0`
- **Artifact**: `models/tuned/synthetic_factory/locked_tuned_model.joblib`

### 14. Final Test Metrics (Evaluated Once on Held-Out Test Window)
- **Test MASI**: 2.1024
- **Mean Anomaly Score**: -0.5336
- **Std Anomaly Score**: 0.0452
- **P95 Anomaly Score**: -0.4873
- **P5 Anomaly Score**: -0.6169
- **Min / Max Score**: [-0.7198, -0.4679]

### 15. Baseline vs Tuned Table

| Metric | Baseline Val | Tuned Val | Baseline Test | Tuned Test | Test Delta |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **MASI (Separation)** | 4.7288 | **4.7288** | 2.1024 | **2.1024** | 0.0000 (0.00%) |
| **Score Variance ($\sigma$)** | 0.0633 | **0.0633** | 0.0452 | **0.0452** | 0.0000 |
| **P5 Floor Score** | -0.7072 | **-0.7072** | -0.6169 | **-0.6169** | 0.0000 |

### 16. Absolute Improvement
- **Validation MASI**: 0.0000
- **Test MASI**: 0.0000

### 17. Relative Improvement
- **Validation MASI**: 0.00%
- **Test MASI**: 0.00%

### 18. Generalization Discussion
- The default Isolation Forest parameters (`n_estimators=100, max_features=1.0`) were already optimal for capturing the multi-machine interaction structure on this synthetic telemetry stream.
- Neither increasing tree count to 200 nor reducing feature sampling to 0.8 yielded higher separation (MASI slipped slightly to 4.7111).
- PCA subspace models struggled on synthetic factory telemetry (MASI < 1.2), indicating that anomaly vectors here are non-linear, multi-machine coordinated offsets best segmented by tree partitioning.

### 19. Overfitting Analysis
- Because the grid exploration revealed that the baseline was already at the empirical global optimum of the search space, any artificial parameter perturbation would degrade separation.
- Retaining the baseline is the strictly sound scientific decision.

### 20. Limitations
- Synthetic origin: Operating distributions and degradation signatures are synthetically generated and do not reflect real-world mechanical wear.
- Maintenance event isolation: Retrospective evaluation on MAINT_0003 is strictly post-hoc and cannot be conflated with prospective online alerting.

### 21. Decision
- **`BASELINE_RETAINED`**
- The extensive hyperparameter grid search confirmed that the baseline configuration `IF_n100_cauto_f1.0` is already optimal (MASI = 4.7288). In accordance with non-negotiable scientific restraint rules, the baseline benchmark is formally retained.
