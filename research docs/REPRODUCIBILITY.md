# NirmaanAI — Research Package Reproducibility Guide
## Complete Execution Commands and Verification Protocols

---

### Prerequisites
- OS: Windows (or Linux with forward-slash path conversion)
- Python: 3.10+ (Tested on Python 3.14)
- Core Libraries: `numpy`, `pandas`, `scipy`, `scikit-learn`, `xgboost`, `matplotlib`, `pytest`

---

### Step 1: Verify Canonical Data Checksum
Before executing any generation scripts, verify that the canonical source file remains untouched:
```powershell
Get-FileHash data\synthetic\auto_components\operational_losses.csv -Algorithm MD5
```
Expected MD5 Output:
`34B12582B32D81E3121429C55EBF74E8`

---

### Step 2: Regenerate Master Tables
```powershell
python "research docs/scripts/generate_tables.py"
```
Outputs Table 1 through Table 14 into `research docs/tables/` in both CSV and Markdown formats.

---

### Step 3: Regenerate Dataset & Preprocessing Figures
```powershell
python "research docs/scripts/generate_dataset_figures.py"
```
Outputs classification class distributions, regression histograms, dataset scale comparisons, and tuning subset reduction plots.

---

### Step 4: Regenerate Model & Tuning Figures
```powershell
python "research docs/scripts/generate_model_figures.py"
```
Outputs holdout confusion matrices, ROC curves, PR curves, actual vs predicted scatter plots, temporal load forecasts, C-MAPSS degradation trajectories, anomaly distributions, and tuning comparison charts.

---

### Step 5: Regenerate System & Explainability Figures
```powershell
python "research docs/scripts/generate_system_figures.py"
```
Outputs SHAP feature importance charts, end-to-end architecture diagrams, factory health score breakdowns, financial loss charts, and the M2 case-study timeline.

---

### Step 6: Export Metadata & Manifest
```powershell
python "research docs/scripts/export_data_and_metadata.py"
```
Generates `metadata/epistemic_status_audit.csv`, `metadata/research_generation_manifest.json`, and human-readable documentation indices.

---

### Step 7: Run Automated Research Validation Suite
```powershell
pytest tests/research/test_research_evidence_package.py -v
```
Verifies existence of all 48 figures, 14 tables, manifest files, checksums, and numerical consistency.

---

### Step 8: Run Full Platform Regression
```powershell
pytest tests/ -q
```
Verifies that all platform tests (471+ tests) remain 100% green with zero regressions.
