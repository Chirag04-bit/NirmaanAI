# Table 6: Model Validation Results and Champion Selection

| Task Identifier | Baseline Model | Tuned Model | Selection Metric | Baseline Val | Tuned Val | Val Abs Imprv | Val Rel Imprv (%) | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| manufacturing_production | Random_Forest_Weighted | LR_C0.1_balanced | PR_AUC | 0.4021 | 0.3993 | -0.0027 | -0.68% | BASELINE_RETAINED |
| secom | XGBoost_Weighted | XGB_d4_lr0.08_col0.5_spw10_Nat | PR_AUC | 0.2669 | 0.4733 | 0.2064 | +77.36% | TUNED_MODEL_ACCEPTED |
| industrial_iot_failure | Logistic_Regression_Sampled | LR_C10.0_ROS | PR_AUC | 0.7522 | 0.7522 | 0.0 | +0.00% | BASELINE_RETAINED |
| ai4i | Random_Forest_Natural | RF_n200_d8_l1_None_Nat | PR_AUC | 0.9051 | 0.9081 | 0.003 | +0.34% | BASELINE_RETAINED |
| cmapss | XGBoost_Regressor | XGB_n150_d6_lr0.03 | RMSE | 12.8983 | 11.4643 | 1.434 | +11.12% | TUNED_MODEL_ACCEPTED |
| electricity | XGBoost_Regressor | XGB_n200_d8_lr0.03_mcw1 | WAPE | 0.0652 | 0.062 | 0.0032 | +4.89% | TUNED_MODEL_ACCEPTED |
| industrial_iot_rul | XGBoost_Regressor | XGB_d6_lr0.05_n150 | RMSE | 48.4887 | 48.3192 | 0.1694 | +0.35% | BASELINE_RETAINED |
| manufacturing_defects | Random_Forest_Natural | RF_n100_dNone_l4 | ROC_AUC | 0.8184 | 0.8389 | 0.0206 | +2.52% | TUNED_MODEL_ACCEPTED |
| textile | Isolation_Forest_Detector | PCA_comp6 | ADCR | 0.8553 | 2.0618 | 1.2065 | +141.06% | TUNED_MODEL_ACCEPTED |
| synthetic_factory | Isolation_Forest_Detector | IF_n100_cauto_f1.0 | MASI | 4.7288 | 4.7288 | 0.0 | +0.00% | BASELINE_RETAINED |
