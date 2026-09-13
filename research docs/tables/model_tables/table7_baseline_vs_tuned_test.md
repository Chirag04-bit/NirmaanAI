# Table 7: Single Blind Holdout Test Set Evaluation Results

| Task Identifier | Baseline Model | Tuned Model | Selection Metric | Baseline Test | Tuned Test | Test Delta | Test Rel Delta (%) | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| manufacturing_production | Random_Forest_Weighted | LR_C0.1_balanced | PR_AUC | 0.3141 | 0.2717 | -0.0424 | -13.49% | BASELINE_RETAINED |
| secom | XGBoost_Weighted | XGB_d4_lr0.08_col0.5_spw10_Nat | PR_AUC | 0.1374 | 0.1964 | 0.059 | +42.96% | TUNED_MODEL_ACCEPTED |
| industrial_iot_failure | Logistic_Regression_Sampled | LR_C10.0_ROS | PR_AUC | 0.7596 | 0.7596 | -0.0 | -0.00% | BASELINE_RETAINED |
| ai4i | Random_Forest_Natural | RF_n200_d8_l1_None_Nat | PR_AUC | 0.91 | 0.9135 | 0.0035 | +0.39% | BASELINE_RETAINED |
| cmapss | XGBoost_Regressor | XGB_n150_d6_lr0.03 | RMSE | 13.3251 | 13.0794 | 0.2457 | +1.84% | TUNED_MODEL_ACCEPTED |
| electricity | XGBoost_Regressor | XGB_n200_d8_lr0.03_mcw1 | WAPE | 0.0663 | 0.0627 | 0.0035 | +5.30% | TUNED_MODEL_ACCEPTED |
| industrial_iot_rul | XGBoost_Regressor | XGB_d6_lr0.05_n150 | RMSE | 48.598 | 48.3798 | 0.2181 | +0.45% | BASELINE_RETAINED |
| manufacturing_defects | Random_Forest_Natural | RF_n100_dNone_l4 | ROC_AUC | 0.8675 | 0.8935 | 0.0261 | +3.01% | TUNED_MODEL_ACCEPTED |
| textile | Isolation_Forest_Detector | PCA_comp6 | ADCR | 0.9431 | 2.8024 | 1.8593 | +197.14% | TUNED_MODEL_ACCEPTED |
| synthetic_factory | Isolation_Forest_Detector | IF_n100_cauto_f1.0 | MASI | 2.1024 | 2.1024 | 0.0 | +0.00% | BASELINE_RETAINED |
