# NirmaanAI — Industrial IoT 2040 RUL Split-Leakage Audit

**Project**: NirmaanAI — AI-Powered Manufacturing Intelligence & Decision Platform  
**Target Pipeline**: `models/processed/industrial_iot/rul/`  
**Source Dataset**: `DATASET/05_INDUSTRIAL_IOT/raw/factory_sensor_simulator_2040.csv`  
**Audit Scope**: Verification of Entity/Machine Duplication, Temporal Dynamics & Partition Leakage  
**Audit Status**: **PASS (NO LEAKAGE DETECTED — SPLIT IS FULLY VALID)**  
**Correction Required**: **NO**  
**Model Tuning Status**: **NOT STARTED**  

---

## 1. Executive Summary

A comprehensive, ground-truth audit of the Industrial IoT 2040 dataset (`factory_sensor_simulator_2040.csv`) and its processed Remaining Useful Life (RUL) pipeline was conducted to resolve whether the random 70/15/15 row split introduces entity/machine leakage across train, validation, and test partitions.

### Key Finding:
- **Total Rows**: Exactly 500,000 records.
- **Unique Machine Entities (`Machine_ID`)**: Exactly 500,000 unique identifiers (`MC_000000` to `MC_499999`).
- **Rows per Machine Entity**: **Exactly 1.0** (0 duplicates across the entire 500k dataset).
- **Temporal Trajectories per Machine**: **None**. The dataset does not track longitudinal trajectories of machines over time; instead, it is a cross-sectional fleet snapshot of 500,000 distinct machines observed at varied stages of their operational lifecycle across 33 equipment types.
- **Entity Overlap Across Partitions**:
  - Train entities: 350,000
  - Validation entities: 75,000
  - Test entities: 75,000
  - $\text{Train} \cap \text{Val} = \mathbf{0}$
  - $\text{Train} \cap \text{Test} = \mathbf{0}$
  - $\text{Val} \cap \text{Test} = \mathbf{0}$

**Conclusion**: Because each row represents a distinct, unique machine entity, a random row-level split is **isomorphic to an entity-grouped split**. Zero machine operational signatures leak between partitions. The existing 70/15/15 split is methodologically sound, deployment-grounded, and requires no architectural changes.

---

## 2. Raw Dataset Structure Audit

### 2.1. Entity Identification
- **Entity Identifier Column**: `Machine_ID`.
- **Value Format**: `MC_XXXXXX` (e.g., `MC_000000`, `MC_000001`, ..., `MC_499999`).
- **Cardinality**: `nunique() = 500,000` out of `500,000` rows.
- **Duplication Rate**: Exactly **0.00%** (No machine ID appears more than once).

### 2.2. Temporal & Sequential Structure Analysis
- **Timestamps / Dates**: None. The schema contains no timestamp, date, or epoch column.
- **Cycle / Sequence Numbers**: None. There are no cycle counters (unlike NASA C-MAPSS, which has repeated cycles $1, 2, \dots, C_{\max}$ for 100 engines).
- **RUL Evolution**: RUL values do not evolve chronologically within the dataset because no machine is observed at multiple time steps. `Remaining_Useful_Life_days` is a single static ground-truth target per machine snapshot.
- **Temporal Nature**: This dataset is a **cross-sectional fleet snapshot**, analogous to a large annual maintenance census across hundreds of facilities.

---

## 3. Current Train / Validation / Test Partition Audit

To audit entity containment, the source `Machine_ID` was mapped through the preprocessing split index (`random_state=42`, 70% train, 15% validation, 15% test).

### Partition Overlap Metrics:

| Metric | Measured Value | Requirement for Zero Leakage | Status |
|---|---:|---:|---|
| **Unique Machines in Train** | 350,000 | 350,000 | PASS |
| **Unique Machines in Val** | 75,000 | 75,000 | PASS |
| **Unique Machines in Test** | 75,000 | 75,000 | PASS |
| **$\text{Train} \cap \text{Val}$ Overlap** | **0** | **0** | **PASS** |
| **$\text{Train} \cap \text{Test}$ Overlap** | **0** | **0** | **PASS** |
| **$\text{Val} \cap \text{Test}$ Overlap** | **0** | **0** | **PASS** |
| **Overlap Ratio** | **0.00%** | **0.00%** | **PASS** |

Zero machines appear in more than one partition.

---

## 4. Evaluation of Split Strategies

| Split Strategy | Applicability to Dataset Structure | Assessment & Deployment Justification |
|---|---|---|
| **A. Entity/Machine-Grouped Split** | **NATURALLY EQUIVALENT** | Since every row is an independent machine, the random 70/15/15 row split **is identically an entity-grouped split**. Each machine belongs to exactly one partition. |
| **B. Chronological Split Within Machines** | **NOT APPLICABLE** | Requires multiple chronological timestamps per machine. With 1 row per machine, chronological intra-machine splitting is mathematically impossible. |
| **C. Grouped + Chronological Split** | **NOT APPLICABLE** | No temporal sequence exists across machines. |
| **D. Random Row Split (Current)** | **OPTIMAL & VALID** | Ensures uniform distribution of all 33 equipment types (`Machine_Type`) and installation years (2000–2040) across train, val, and test, while guaranteeing 100% entity isolation. |

---

## 5. Deployment Scenario Grounding

In factory deployment, the RUL model is evaluated against **unseen machines** (i.e. predicting RUL for newly commissioned or newly surveyed equipment). Because test machines (`75,000` distinct entities) share zero `Machine_ID` overlap with training machines (`350,000` distinct entities), the evaluation accurately mirrors real-world zero-shot fleet generalization.

---

## 6. Audit Verdict

1. **Leakage Finding**: **NO LEAKAGE FOUND**.
2. **Methodological Validity**: **CONFIRMED**.
3. **Pipeline Action**: **PRESERVE AS-IS**. No pipeline modification, re-split, or retraining is warranted.
4. **Downstream Model Tuning**: **NOT STARTED**. Awaiting explicit user approval.
