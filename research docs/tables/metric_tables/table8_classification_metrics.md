# Table 8: Holdout Classification Performance Metrics across Imbalanced Tasks

| Task Identifier | Model Evaluated | Operating Threshold | Accuracy | Precision | Recall | F1 Score | ROC-AUC | PR-AUC | Specificity | FPR | FNR |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ai4i | RF_n200_d8_l1_None_Nat | 0.2 | 0.9893 | 0.807 | 0.902 | 0.8519 | 0.9829 | 0.9135 | 0.9924 | 0.0076 | 0.098 |
| secom | XGB_d4_lr0.08_col0.5_spw10_Nat | 0.2 | 0.9068 | 0.2857 | 0.25 | 0.2667 | 0.7057 | 0.1964 | 0.9545 | 0.0455 | 0.75 |
| industrial_iot_failure | LR_C10.0_ROS | 0.9 | 0.9623 | 0.6543 | 0.788 | 0.7149 | 0.9832 | 0.7596 | 0.9734 | 0.0266 | 0.212 |
| manufacturing_production | LR_C0.1_balanced | 0.35 | 0.3 | 0.2973 | 0.9778 | 0.456 | 0.4301 | 0.2717 | 0.0095 | 0.9905 | 0.0222 |
| manufacturing_defects | RF_n100_dNone_l4 | 0.49999999999999994 | 0.963 | 0.9599 | 0.9975 | 0.9784 | 0.8935 | 0.9666 | 0.7821 | 0.2179 | 0.0025 |
