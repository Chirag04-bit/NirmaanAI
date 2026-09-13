# Table 9: Holdout Regression Performance Metrics across Predictive Tasks

| Task Identifier | Model Evaluated | MAE | RMSE | R2 Score | WAPE (%) | sMAPE (%) | Primary Metric | Epistemic Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| cmapss | XGB_n150_d6_lr0.03 | 9.6278 | 13.0794 | 0.9002 | 10.80% | 14.76% | RMSE | HIGH_FIDELITY_PHYSICS_SIMULATION |
| electricity | XGB_n200_d8_lr0.03_mcw1 | 18.7774 | 25.5648 | 0.9625 | 6.27% | 7.50% | WAPE | REAL_INDUSTRIAL_TELEMETRY |
| industrial_iot_rul | XGB_d6_lr0.05_n150 | 38.2181 | 48.3798 | 0.9718 | 8.44% | 25.76% | RMSE | CONTROLLED_INDUSTRIAL_SIMULATOR |
