# Table 13: Dataset Volume Optimization and Computational Subsampling Efficiency

| Dataset | Optimization Status | Full Train Rows | Subset Train Rows | Retention (%) | Sampling Strategy | Measured Speedup |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| industrial_iot_failure | SUBSET_GENERATED | 350000 | 105000 | 30.0% | Deterministic stratified joint class & machine type sampling | 4.12x (75.7% time reduction) |
| industrial_iot_rul | SUBSET_GENERATED | 350000 | 105000 | 30.0% | Deterministic decile-binned distribution-aware regression sampling | 4.12x (75.7% time reduction) |
| electricity | SUBSET_GENERATED | 18279 | 9140 | 50.0% | Deterministic contiguous chronological window | ~2.0x (Est.) |
| textile | SUBSET_GENERATED | 30240 | 15120 | 50.0% | Deterministic synchronized temporal stride (stride=2 across looms) | ~2.0x (Est.) |
| synthetic_factory | SUBSET_GENERATED | 20415 | 10210 | 50.0% | Deterministic synchronized multi-station temporal stride (stride=2 across M1-M5) | ~2.0x (Est.) |
| ai4i | KEPT_FULL | 7000 | 7000 | 100.0% | Full Data Kept | Dataset size is already compact (7,000 train rows); volume reduction provides negligible gain while risking rare failure mode representation. |
| cmapss | KEPT_FULL | 14130 | 14130 | 100.0% | Full Data Kept | Engine-grouped physics trajectories must preserve complete run-to-failure curves across all 70 training engines (14,130 rows). |
| secom | KEPT_FULL | 1096 | 1096 | 100.0% | Full Data Kept | Wafer defect dataset is already small (1,096 train rows) with only 6.6% defect prevalence. |
| manufacturing_production | KEPT_FULL | 700 | 700 | 100.0% | Full Data Kept | Production dispatch log contains only 700 training rows; reduction would severely degrade ranking quality. |
| manufacturing_defects | KEPT_FULL | 2268 | 2268 | 100.0% | Full Data Kept | Batch quality dataset contains 2,268 training rows; highly compact and fast to train. |
