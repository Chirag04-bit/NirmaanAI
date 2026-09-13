# NirmaanAI — Operational & Financial Loss Analysis (INR) Report
## Phase 14: Decision Intelligence Subsystem

```
========================================================================================
NIRMAAN AI — OPERATIONAL & FINANCIAL LOSS ANALYSIS REPORT
Phase:          Phase 14 (Operational & Financial Loss Analysis - INR)
Status:         VALIDATED, VERIFIED, AND ACCOUNTING-RECONCILED
Implementation: src/decision/ (models, engine, service)
Target:         Machine-Level & Plant-Wide Operational Disruptions (INR)
Evaluation:     src/models/evaluate_loss.py -> models/loss/loss_summary.json
Test Suite:     tests/test_financial_loss.py (passing, full regression clean)
========================================================================================
```

---

## 1. Executive Summary & Epistemic Framework

The **NirmaanAI Operational & Financial Loss Analysis Engine** translates physical shop-floor disruptions (machine halts, tool wear scrap, technician rework, power demand excursions, and bottleneck delays) into quantified financial metrics in **Indian Rupees (INR)** for manufacturing MSMEs.

The core pipeline bridges raw telemetry and predictive intelligence into board-level decision metrics:

$$\mathbf{Telemetry\ /\ Events} \longrightarrow \mathbf{Operational\ Disruption} \longrightarrow \mathbf{Configured\ MSME\ Rates} \longrightarrow \mathbf{Financial\ Decomposition\ (INR)}$$

### 1.1 Strict Epistemic Classification
Every financial metric is systematically classified across:
1. `OBSERVED`: Quantities directly logged in operational records (e.g. 150 minutes unplanned downtime in `maintenance_records.csv`; 76 scrap parts in `production_jobs.csv`).
2. `DERIVED_FROM_OBSERVED`: Physical derivations (e.g. 5-minute active power $\text{kW} \times (5/60)\text{ h} = \text{kWh}$; scrap units $\times 0.8\text{ kg/unit}$).
3. `CONFIGURED_ASSUMPTION`: Standardized MSME cost parameters from [`configs/factory_defaults.yaml`](file:///c:/NIRMAAN%20AI/configs/factory_defaults.yaml).
4. `PROJECTED_OPPORTUNITY_COST`: Unproduced throughput contribution margin ($Q_{\text{lost}} \times \text{₹}320/\text{unit}$).
5. `CONTROLLED_SYNTHETIC`: Controlled scenario evaluation on simulated assets.

> [!IMPORTANT]
> **Projected opportunity cost is an operational capacity model and NOT equivalent to realized accounting loss.**

---

## 2. Formal Accounting Identities

The subsystem enforces two formal, non-overlapping mathematical identities:

### Identity 1: Realized Operational Loss
$$\text{REALIZED OPERATIONAL LOSS} = L_{\text{unplanned\_dt}} + L_{\text{scrap}} + L_{\text{prod\_rework}} + L_{\text{emerg\_labor}} + L_{\text{energy\_inefficiency}}$$

Where:
- $L_{\text{unplanned\_dt}}$ = Unplanned Downtime Loss (₹11,250.00 on M2; ₹0.00 on nominal machines)
- $L_{\text{scrap}}$ = Scrap Material Replacement Loss (₹186,760.00 total)
- $L_{\text{prod\_rework}}$ = Parts Rework Labor Overhead (₹23,345.00 total)
- $L_{\text{emerg\_labor}}$ = Emergency Technician Overhaul Labor (**₹420.00** on M2 for `MAINT_0003`)
- $L_{\text{energy\_inefficiency}}$ = Excess Power Consumption Loss above Rated Capacity (₹7,330.54 total)

$$\mathbf{\text{Plant Realized Operational Loss} = 11,250.00 + 186,760.00 + 23,345.00 + 420.00 + 7,330.54 = ₹229,105.54}$$

### Identity 2: Gross Financial Exposure
$$\text{GROSS FINANCIAL EXPOSURE} = \text{REALIZED OPERATIONAL LOSS} + \text{PROJECTED OPPORTUNITY COST}$$

$$\mathbf{\text{Plant Gross Financial Exposure} = 229,105.54 + 24,320.00 = ₹253,425.54}$$

### Identity 3: Downtime Classification & Routine Maintenance Pool
$$\text{TOTAL MAINTENANCE DOWNTIME} = \text{UNPLANNED DOWNTIME} + \text{SCHEDULED ROUTINE MAINTENANCE}$$

- **Total Maintenance Downtime**: **250 min** (4.17 hours, ₹18,750.00 allocation)
- **Unplanned Downtime**: **150 min** (2.50 hours, **₹11,250.00**) on M2 (`MAINT_0003`)
- **Scheduled / Routine Maintenance**: **100 min** (1.67 hours, **₹7,500.00**) on M1 (45 min, ₹3,375.00), M3 (30 min, ₹2,250.00), M4 (25 min, ₹1,875.00)

> [!NOTE]
> **Routine Maintenance Separation**: The ₹7,500.00 scheduled maintenance allocation represents planned operating maintenance (lubrication, tool replacement, camera lens cleaning) and is explicitly tracked in a separate planned maintenance pool, **NOT** merged into unplanned disruption loss.

---

## 3. Financial Assumptions & Provenance Audit

All financial cost parameters strictly adhere to [configs/factory_defaults.yaml](file:///c:/NIRMAAN%20AI/configs/factory_defaults.yaml):

| Parameter | Configured Value | Epistemic Provenance | Description |
| :--- | :--- | :--- | :--- |
| **Unplanned Downtime Rate** | **₹4,500.00 / hour** | `CONFIGURED_ASSUMPTION` | Idle machine + operator overhead + missed order penalty |
| **Base Electricity Tariff** | **₹8.50 / kWh** | `CONFIGURED_ASSUMPTION` | Standard industrial tariff rate |
| **Peak Electricity Tariff** | **₹12.50 / kWh** | `CONFIGURED_ASSUMPTION` | Peak window tariff schedule (18:00 to 22:00) |
| **Scrap Material Rate** | **₹350.00 / kg** | `CONFIGURED_ASSUMPTION` | Raw metal/yarn replacement cost |
| **Part Physical Mass** | **0.80 kg / unit** | `CONFIGURED_ASSUMPTION` | Nominal physical mass per finished unit |
| **Rework Technician Rate** | **₹280.00 / hour** | `CONFIGURED_ASSUMPTION` | Secondary correction technician rate |
| **Contribution Margin** | **₹320.00 / unit** | `CONFIGURED_ASSUMPTION` | Net margin per unit produced for opportunity cost |

### Energy Baseline Provenance Classification
- **M1 (15.0 kW)**: `CONFIGURED_SIMULATION_BASELINE` (configured in `factory_defaults.yaml`).
- **M2 (22.0 kW)**: `CONFIGURED_SIMULATION_BASELINE` (configured in `factory_defaults.yaml`).
- **M3 (11.0 kW)**: `CONFIGURED_SIMULATION_BASELINE` (configured in `factory_defaults.yaml`).
- **M4 (4.5 kW)**: `SIMULATION_METADATA_BASELINE` (persisted in `machines.csv`).
- **M5 (7.5 kW)**: `SIMULATION_METADATA_BASELINE` (persisted in `machines.csv`).

---

## 4. Machine-Level Attribution & Plant Rollup (Actual Calculated Values)

### 4.1 Machine-Level Breakdown ($M_1$ through $M_5$)

| Machine | Unplanned Downtime | Routine Maint (Cost Pool) | Scrap Loss | Prod Rework | Emerg Overhaul Labor | Energy Inefficiency | Realized Loss (INR) | Projected Opportunity Cost | Gross Exposure (INR) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **M1** | 0 min (₹0.00) | 45 min (₹3,375.00) | ₹35,560.00 | ₹4,445.00 | ₹0.00 | ₹1,044.87 | **₹41,049.87** | ₹0.00 | **₹41,049.87** |
| **M2** | 150 min (₹11,250.00) | 0 min (₹0.00) | ₹51,800.00 | ₹6,475.00 | ₹420.00 | ₹3,117.28 | **₹73,062.28** | ₹24,320.00 | **₹97,382.28** |
| **M3** | 0 min (₹0.00) | 30 min (₹2,250.00) | ₹34,720.00 | ₹4,340.00 | ₹0.00 | ₹1,037.22 | **₹40,097.22** | ₹0.00 | **₹40,097.22** |
| **M4** | 0 min (₹0.00) | 25 min (₹1,875.00) | ₹34,160.00 | ₹4,270.00 | ₹0.00 | ₹1,061.24 | **₹39,491.24** | ₹0.00 | **₹39,491.24** |
| **M5** | 0 min (₹0.00) | 0 min (₹0.00) | ₹30,520.00 | ₹3,815.00 | ₹0.00 | ₹1,069.93 | **₹35,404.93** | ₹0.00 | **₹35,404.93** |
| **PLANT TOTAL** | **150 min (₹11,250.00)** | **100 min (₹7,500.00)** | **₹186,760.00** | **₹23,345.00** | **₹420.00** | **₹7,330.54** | **₹229,105.54** | **₹24,320.00** | **₹253,425.54** |

### 4.2 Plant-Wide Totals by Category
- **Unplanned Downtime Loss**: **₹11,250.00** (150 min on M2, `MAINT_0003`)
- **Routine Maintenance Cost Pool**: **₹7,500.00** (100 min on M1, M3, M4)
- **Total Maintenance Downtime**: **250 min (₹18,750.00)**
- **Scrap Material Replacement Loss**: **₹186,760.00** (667 scrapped units)
- **Production Parts Rework Labor**: **₹23,345.00** (83.38 technician hours)
- **Emergency Maintenance Overhaul Labor**: **₹420.00** (1.50 technician hours on M2)
- **Total Labor Overhead**: **₹23,765.00**
- **Total Operational Energy Expenditure**: **₹398,189.47** (43,440.33 kWh total factory load)
- **Energy Inefficiency Loss (Excess Load)**: **₹7,330.54** (799.96 excess kWh)
- **Bottleneck Opportunity Cost**: **₹24,320.00** (76 unproduced units on M2)
- **Gross Financial Exposure**: **₹253,425.54**
- **Non-Overlapping Financial Exposure**: **₹253,425.54**

---

## 5. Machine 2 Controlled Synthetic Degradation Scenario

Authoritative evaluation of the Machine 2 degradation and emergency halt sequence:
- **Emergency Halt Event**: `MAINT_0003` at `2026-01-22 16:30:00+00:00`
- **Root Mechanism**: Spindle drive bearing wear and thermal buildup due to lubrication starvation
- **Precursor Degradation (Days 18–21)**:
  - 8 delayed production jobs (`JOB_0172` through `JOB_0207`)
  - Scrap quantity escalated to 6, 8, 10, 12 units (76 scrapped parts total)
  - Precursor scrap loss delta: **₹21,280.00**
  - Precursor production rework labor delta: **₹2,660.00**
  - Precursor energy inefficiency delta: **₹1,675.83**
  - Projected bottleneck opportunity cost: **₹24,320.00** (76 unproduced units $\times$ ₹320/unit)
- **Emergency Halt Disruption (`MAINT_0003`)**:
  - Unplanned Downtime: 150.0 minutes (2.5 hours) = **₹11,250.00**
  - Emergency Technician Overhaul Labor: 1.5 hours = **₹420.00**
  - Single-Event Emergency Halt Loss = $11,250.00 + 420.00 = \mathbf{₹11,670.00}$
- **Total M2 Realized Operational Loss**:
  $$\mathbf{M2\ Realized\ Loss = 11,250.00 + 51,800.00 + 6,475.00 + 420.00 + 3,117.28 = ₹73,062.28}$$
- **Total M2 Gross Financial Exposure**:
  $$\mathbf{M2\ Gross\ Exposure = 73,062.28 + 24,320.00 = ₹97,382.28}$$

---

## 6. Reference Artifact Reconciliation

Reconciliation against reference artifact `DATASET/10_SYNTHETIC_FACTORY/synthetic/operational_losses.csv`:

| Disruption Metric | Calculated Value | Reference Artifact Value | Agreement Status |
| :--- | :--- | :--- | :--- |
| **Total Downtime Allocation** | ₹18,750.00 | ₹18,750.00 | **100% Exact Match** |
| **Scrap Material Loss** | ₹186,760.00 | ₹186,760.00 | **100% Exact Match** |
| **Total Labor (Rework + Overhaul)** | ₹23,765.00 | ₹23,765.00 | **100% Exact Match** |
| **Energy Inefficiency Loss** | ₹7,330.54 | Not recorded | Independently derived from sensor telemetry |
| **Bottleneck Opportunity Cost** | ₹24,320.00 | Not recorded | Independently derived from delayed jobs |

### Explanation of Underlying Composition
In `operational_losses.csv`, all maintenance downtime (unplanned + routine) was combined under `downtime_loss_inr` (₹18,750.00), and both parts rework (₹23,345.00) and technician overhaul labor (**₹420.00**) were combined under `rework_loss_inr` (₹23,765.00).

Phase 14 first-principles calculations achieve **100% exact numerical match** with `operational_losses.csv` while rigorously resolving the underlying physical composition:
1. **Unplanned Downtime** (150 min, ₹11,250.00) is isolated from **Routine Maintenance** (100 min, ₹7,500.00).
2. **Production Parts Rework** (₹23,345.00) is isolated from **Emergency Maintenance Overhaul Labor** (₹420.00).
3. The **₹420.00** emergency overhaul labor is included in M2 realized operational loss and single-event halt disruption without double-counting.

---

## 7. Research Integrity & Limitations

> [!CAUTION]
> **RESEARCH INTEGRITY NOTICE**:
> 1. All financial parameters are configured simulation assumptions unless independently verified by empirical accounting audit.
> 2. Synthetic factory scenario losses demonstrate the internal mathematical consistency, epistemic rigor, and algorithmic validity of the NirmaanAI decision pipeline.
> 3. They do not constitute empirical proof of manufacturing profitability, industrial tariff validity, or real-world shop-floor losses.
> 4. Projected opportunity cost represents unproduced capacity margin and is distinct from realized accounting losses.
