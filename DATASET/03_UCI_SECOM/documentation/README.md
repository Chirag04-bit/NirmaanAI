# 03_UCI_SECOM Semiconductor Manufacturing Process Dataset

## Dataset Provenance & Overview
- **Origin**: UCI Machine Learning Repository (Michael McCann & Adrian Johnston, 2008).
- **Domain**: Modern semiconductor manufacturing process monitoring and wafer yield quality analysis.
- **License**: Open Access.

---

## IMPORTANT ARCHITECTURAL SPECIFICATION: Representation Distinction
The four files extracted within this directory:
1. `raw/uci-secom.csv` (6.05 MB)
2. `raw/secom.data` (5.38 MB)
3. `raw/secom_labels.data` (40.6 KB)
4. `raw/secom.names` (4.2 KB)

**ARE REPRESENTATIONS AND SUPPORTING FILES OF THE SAME SINGLE SECOM DATASET.**
They **MUST NOT** be counted as separate or distinct datasets in NirmaanAI.

- `uci-secom.csv` is the consolidated, pre-merged tabular representation containing:
  - Timestamp column (`Time`)
  - 590 numerical sensor features (`0` to `589`)
  - Target label column (`Pass/Fail`)
- `secom.data` is the original raw space-delimited sensor matrix of 590 numerical values per row.
- `secom_labels.data` contains the ground-truth binary classification label (`-1` or `1`) and sample timestamp for each of the 1,567 rows.
- `secom.names` is the original UCI documentation detailing feature attributes, donor notes, and citation guidelines.

---

## Dataset Schema & Statistics
- **Total Instances / Rows**: 1,567
- **Total Features**: 590 continuous sensor measurements
- **Total Columns in `uci-secom.csv`**: 592 (`Time` + 590 sensors + `Pass/Fail`)
- **Target Variable**: `Pass/Fail`
  - `-1`: Pass / Conforming wafer (1,463 samples, **93.36%**)
  - `+1`: Fail / Defective wafer (104 samples, **6.64%**)
- **Data Quality Characteristics**: High feature dimensionality with 41,951 missing values distributed across 538 feature columns. Severe class imbalance (~14:1 ratio).

---

## Data Leakage & Preprocessing Guardrails
1. **Fold-Isolation for Preprocessing**: Because of the high dimensionality and missingness, all imputation (e.g. median/KNN), scaling, and low-variance feature screening must strictly be fit on training folds only. Never fit imputers or feature selectors on the entire dataset prior to splitting.
2. **Collinearity Handling**: Multiple sensor columns exhibit near-zero variance or extreme correlation. Feature selection or PCA must be evaluated in Phase 7 to prevent model instability.
