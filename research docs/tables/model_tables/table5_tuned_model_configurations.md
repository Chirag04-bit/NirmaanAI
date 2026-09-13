# Table 5: Final Tuned Champion Model Hyperparameter Specifications

| Task Identifier | Tuned Model Name | Model Family | Primary Selection Metric | Configurations Evaluated | Operating Threshold | Key Tuned Hyperparameters |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| manufacturing_production | LR_C0.1_balanced | LogisticRegression | PR_AUC | 54 | 0.35 | {'C': '0.1', 'class_weight': 'balanced', 'dual': 'False', 'fit_intercept': 'True', 'intercept_scaling': '1', 'l1_ratio': '0.0', 'max_iter':  |
| secom | XGB_d4_lr0.08_col0.5_spw10_Nat | XGBClassifier | PR_AUC | 66 | 0.2 | {'objective': 'binary:logistic', 'colsample_bytree': '0.5', 'enable_categorical': 'True', 'eval_metric': 'logloss', 'learning_rate': '0.08', |
| industrial_iot_failure | LR_C10.0_ROS | LogisticRegression | PR_AUC | 20 | 0.9 | {'C': '10.0', 'dual': 'False', 'fit_intercept': 'True', 'intercept_scaling': '1', 'l1_ratio': '0.0', 'max_iter': '500', 'penalty': 'deprecat |
| ai4i | RF_n200_d8_l1_None_Nat | RandomForestClassifier | PR_AUC | 62 | 0.2 | {'bootstrap': 'True', 'ccp_alpha': '0.0', 'criterion': 'gini', 'max_depth': '8', 'max_features': 'sqrt', 'min_impurity_decrease': '0.0', 'mi |
| cmapss | XGB_n150_d6_lr0.03 | XGBRegressor | RMSE | 35 | 0.5 | {'objective': 'reg:squarederror', 'colsample_bytree': '0.8', 'enable_categorical': 'True', 'learning_rate': '0.03', 'max_depth': '6', 'n_est |
| electricity | XGB_n200_d8_lr0.03_mcw1 | XGBRegressor | WAPE | 54 | 0.5 | {'objective': 'reg:squarederror', 'colsample_bytree': '0.85', 'enable_categorical': 'True', 'learning_rate': '0.03', 'max_depth': '8', 'min_ |
| industrial_iot_rul | XGB_d6_lr0.05_n150 | XGBRegressor | RMSE | 16 | 0.5 | {'objective': 'reg:squarederror', 'colsample_bytree': '0.85', 'enable_categorical': 'True', 'learning_rate': '0.05', 'max_depth': '6', 'n_es |
| manufacturing_defects | RF_n100_dNone_l4 | RandomForestClassifier | ROC_AUC | 24 | 0.49999999999999994 | {'bootstrap': 'True', 'ccp_alpha': '0.0', 'criterion': 'gini', 'max_features': 'sqrt', 'min_impurity_decrease': '0.0', 'min_samples_leaf': ' |
| textile | PCA_comp6 | PCAReconstructionModel | ADCR | 22 | 0.5 | {'n_components': '6', 'random_state': '42'} |
| synthetic_factory | IF_n100_cauto_f1.0 | IsolationForest | MASI | 22 | 0.5 | {'bootstrap': 'False', 'contamination': 'auto', 'max_features': '1.0', 'max_samples': 'auto', 'n_estimators': '100', 'random_state': '42', ' |
