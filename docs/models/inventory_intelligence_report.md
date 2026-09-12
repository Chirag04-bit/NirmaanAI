# NirmaanAI — Phase 10 Model Report: Smart Inventory Intelligence & Operations Research

**Subsystem**: Smart Inventory Intelligence & Operations Research  
**Module**: Phase 10  
**Version**: 1.0.0  
**Date**: September 2026  
**Author**: NirmaanAI Core Research Team  
**Institution**: Institute of Engineering & Management (IEM), Kolkata  
**Project Guide**: Prof. Kuntal Mondal  

---

## 1. Executive Summary

Phase 10 implements NirmaanAI's **Smart Inventory Intelligence Subsystem**, providing small-and-medium manufacturing enterprises (MSMEs) with deterministic Operations Research (OR) models for dynamic inventory state management, safety stock optimization, reorder scheduling, and predictive maintenance-spare coupling.

### Subsystem Demarcation Across NirmaanAI:
- **Phase 6**: Machine Failure Classification & RUL Regression (Predictive Maintenance)
- **Phase 7**: Multivariate Telemetry Anomaly Detection (Unsupervised Health Monitoring)
- **Phase 8**: Production Flow Bottleneck Prediction (Flow Intelligence)
- **Phase 9**: Production Throughput & Energy Demand Forecasting (Capacity & Resource Planning)
- **Phase 10**: Smart Inventory Intelligence & Operations Research (Inventory & Maintenance-Spare Coupling)

### Key Achievements:
1. **Deterministic Operations Research Formulations**:
   - Implemented dynamic Safety Stock ($SS$), Reorder Point ($ROP$), Economic Order Quantity ($EOQ$ - Wilson-Harris formulation), and Days of Supply ($DoS$) with rigorous boundary and edge-case handling.
2. **Dual Uncertainty Safety Stock**:
   - Accurately models both daily demand variability ($\sigma_d$) and vendor lead-time variability ($\sigma_L$) simultaneously, preventing stockouts during supplier transit delays.
3. **Machine 2 Predictive Maintenance-Spare Coupling**:
   - Direct integration with Phase 6 equipment degradation semantics:
     - Empirical AI4I decision threshold: **$\tau = 0.91$** (strict research integrity; not replaced with 0.50).
     - Configured synthetic vibration trigger: **$\ge 3.80\text{ mm/s}$** (labeled as configured synthetic scenario trigger).
     - Physical Vendor Lead Time Constraint: Evaluates the **7-day vendor lead time** for `SKU_SPINDLE_BEARING_M2`. Acknowledges that emergency purchase orders cannot magically eliminate physical transit delay.
4. **Research Integrity Guardrail Enforced**:
   - In accordance with research-integrity directives, Phase 10 **strictly omits** supervised defect classification benchmarks (which belong to material quality inspection rather than inventory operations). No external datasets or fabricated inventory transactions were introduced.
   - All 17 targeted Phase 10 tests and all 85 full-project tests passed with zero regressions.

---

## 2. Dataset Demarcation & Data Sources

| Asset Path | Records / Scope | Nature of Data | Role in Phase 10 |
| :--- | :--- | :--- | :--- |
| `DATASET/10_SYNTHETIC_FACTORY/synthetic/inventory_items.csv` | 5 SKUs across 3 categories | Controlled factory simulation catalog | Warehouse stock levels, unit costs, baseline reorder quantities |
| `DATASET/10_SYNTHETIC_FACTORY/synthetic/production_jobs.csv` | 180 batches across 30 days | Controlled discrete manufacturing jobs | Causal basis for deriving daily SKU material consumption rates |
| `DATASET/10_SYNTHETIC_FACTORY/synthetic/maintenance_records.csv` | Component replacement history | Machine maintenance logs | Validation of spare part consumption episodes |

### Source Data Immutability:
- **No modification to raw datasets**: All raw data files in `DATASET/` remain untouched (`git status` confirms zero modifications in `DATASET/`).
- **No external datasets added**: All calculations operate entirely on existing project assets.

---

## 3. Synthetic Demand & Consumption Derivation

To avoid fabricating ungrounded inventory logs while providing continuous consumption statistics, daily consumption rates are derived causally from scheduled manufacturing jobs and Bills of Materials (BOM).

### 3.1. Configured Synthetic BOM Parameters
*(Documented as configured synthetic simulation parameters, not empirical industrial truths)*

| SKU Identifier | Target Machine | Operation / Usage | Consumption Coeff | UoM | Category | Lead Time ($\bar{L} \pm \sigma_L$) | Target Service Level ($Z$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SKU_STEEL_BAR_20MM` | M1 (CNC Lathe) | Rough Turning & Profiling | $0.40\text{ kg / unit}$ | kg | RAW_MATERIAL | $5.0 \pm 1.0\text{ days}$ | 95% ($Z=1.645$) |
| `SKU_ALUM_BILLET_6061` | M2 (VMC Mill) | Precision VMC Pocket Milling | $0.35\text{ kg / unit}$ | kg | RAW_MATERIAL | $5.0 \pm 1.0\text{ days}$ | 95% ($Z=1.645$) |
| `SKU_SPINDLE_BEARING_M2` | M2 (VMC Mill) | Maintenance Spindle Overhaul | $1.0\text{ unit / overhaul}$ | units | CRITICAL_SPARE | $7.0 \pm 2.0\text{ days}$ | 99% ($Z=2.326$) |
| `SKU_ENDMILL_CARBIDE_10MM` | M2 (VMC Mill) | Precision VMC Pocket Milling | $0.10\text{ tool / job}$ | units | TOOLING | $4.0 \pm 0.5\text{ days}$ | 99% ($Z=2.326$) |
| `SKU_YARN_COTTON_30S` | M3 (Loom / Finishing) | Surface Grinding & Finishing | $0.80\text{ kg / unit}$ | kg | RAW_MATERIAL | $6.0 \pm 1.5\text{ days}$ | 95% ($Z=1.645$) |

### 3.2. Causal Derivation Formula
For any calendar day $t$ and machine $m$:
$$\text{Consumption}_{sku, t} = \sum_{j \in \text{Jobs}(m, t)} \text{BatchQuantity}_j \times \text{Coeff}_{sku}$$
- **Zero Future Lookahead**: Aggregated strictly by scheduled job date $t$.
- **Spares**: Bearing replacement is consumed during scheduled machine degradation/overhaul.

---

## 4. Mathematical Core & Operations Research Formulations

### 4.1. Dynamic Safety Stock ($SS$)
When both daily demand ($d$) and vendor lead time ($L$) are stochastic random variables:
$$SS = Z \times \sqrt{\bar{L} \cdot \sigma_d^2 + \bar{d}^2 \cdot \sigma_L^2}$$
where:
- $Z$: Standard normal quantile corresponding to the target non-stockout probability during lead time.
- $\bar{L}$: Mean vendor replenishment lead time in working days.
- $\sigma_L$: Standard deviation of vendor replenishment lead time.
- $\bar{d}$: Mean daily consumption/demand.
- $\sigma_d$: Standard deviation of daily consumption/demand.

### 4.2. Reorder Point ($ROP$)
The inventory level that triggers a replenishment purchase order:
$$ROP = (\bar{d} \times \bar{L}) + SS$$

### 4.3. Economic Order Quantity ($EOQ$ — Wilson-Harris Formulation)
Minimizes total annual procurement ordering costs and inventory holding carrying costs:
$$EOQ = \sqrt{\frac{2 \times D \times S}{H}}$$
where:
- $D = \bar{d} \times 312$: Annualized demand based on configured 312 working days per year (standard Indian MSME 6-day work weeks).
- $S$: Configured order setup / logistics / procurement cost per purchase order (₹800 to ₹3,500).
- $H = \text{unit\_cost} \times i$: Annual inventory carrying / holding cost per unit, where $i \in [0.15, 0.22]$ is the annual holding cost rate (capital cost, warehouse space, insurance, obsolescence).

### 4.4. Days of Supply ($DoS$)
Operational runway before warehouse exhaustion at current consumption rate:
$$DoS = \frac{\text{Current Stock}}{\bar{d}}$$

---

## 5. Configured Simulation Assumptions

All assumptions are explicitly declared and distinguished from empirical ground truth:

1. **Annual Working Days**: Configured at **312 days** (52 weeks $\times$ 6 days/week), standard for Indian industrial MSMEs.
2. **Service Level Targets**:
   - **Standard Raw Materials**: Target = $95\%$, $Z = 1.645$. Provides balanced buffer without excessive working capital lockup.
   - **Critical Maintenance Spares & High-Wear Tooling**: Target = $99\%$, $Z = 2.326$. Mitigates catastrophic machine downtime risk.
3. **Ordering Setup Costs ($S$)**:
   - Raw materials bulk freight: ₹1,200 – ₹1,500 per PO.
   - Specialized precision bearings: ₹3,500 per PO (express courier, precision handling).
   - Tooling batches: ₹800 per PO.
4. **Annual Holding Cost Rate ($i$)**:
   - Configured at $15\%$ for durable mechanical spares, $20\%$ for standard alloy metals, and $22\%$ for moisture-sensitive textile inputs.

---

## 6. Shop-Floor SKU Optimization Audit & Results

The complete pipeline was executed across all warehouse SKUs. Results are summarized below:

| SKU Identifier | Category | Current Stock | Unit Cost (₹) | Daily Demand $\bar{d} \pm \sigma_d$ | Lead Time $\bar{L} \pm \sigma_L$ | Target $Z$ | Safety Stock ($SS$) | Reorder Point ($ROP$) | Recommended $EOQ$ | Days of Supply ($DoS$) | Inventory Tier | Recommended Action |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SKU_STEEL_BAR_20MM` | RAW_MATERIAL | $450.0\text{ kg}$ | ₹95.0 | $96.00 \pm 32.97$ | $5.0 \pm 1.0\text{ d}$ | $1.645$ (95%) | **199.11 kg** | **679.11 kg** | **2,174.69 kg** | 4.69 days | **REORDER_NOW** | Place standard PO for 2,174.7 kg |
| `SKU_ALUM_BILLET_6061` | RAW_MATERIAL | $220.0\text{ kg}$ | ₹240.0 | $89.25 \pm 27.71$ | $5.0 \pm 1.0\text{ d}$ | $1.645$ (95%) | **178.73 kg** | **624.98 kg** | **1,319.23 kg** | 2.46 days | **REORDER_NOW** | High-urgency PO: stock covers only 2.46 days vs 5 days lead time |
| `SKU_SPINDLE_BEARING_M2` | CRITICAL_SPARE | $2.0\text{ units}$ | ₹3,200.0 | $0.033 \pm 0.18$ | $7.0 \pm 2.0\text{ d}$ | $2.326$ (99%) | **1.13 units** | **1.37 units** | **12.31 units** | 60.06 days | **OPTIMAL_BUFFER** | Stock adequate under quiescent run rate; subject to M2 coupling |
| `SKU_ENDMILL_CARBIDE_10MM` | TOOLING | $12.0\text{ units}$ | ₹1,450.0 | $0.200 \pm 0.00$ | $4.0 \pm 0.5\text{ d}$ | $2.326$ (99%) | **0.23 units** | **1.03 units** | **18.56 units** | 60.00 days | **OPTIMAL_BUFFER** | Buffer healthy; monitor VMC cycle counts |
| `SKU_YARN_COTTON_30S` | RAW_MATERIAL | $1200.0\text{ kg}$ | ₹280.0 | $198.67 \pm 54.06$ | $6.0 \pm 1.5\text{ d}$ | $1.645$ (95%) | **536.43 kg** | **1,728.43 kg** | **1,554.02 kg** | 6.04 days | **REORDER_NOW** | Place standard PO for 1,554.0 kg |

### Operational Findings:
1. **Raw Material Stockout Hazards**: Both `SKU_STEEL_BAR_20MM` (4.69 DoS) and `SKU_ALUM_BILLET_6061` (2.46 DoS) have fallen below their respective Reorder Points ($679.1\text{ kg}$ and $625.0\text{ kg}$). For Aluminium 6061, current stock covers only 2.46 days of production, which is **shorter than the vendor's 5-day lead time**. Unless replenishment is expedited, a stockout will occur within 3 days.
2. **Total Capital Tied Up**:
   - Current warehouse stock capital: **₹455,350.00**
   - Immediate reorder commitment across 3 triggered raw materials: **₹958,335.38**

---

## 7. Machine 2 Predictive Maintenance-Spare Coupling

A major innovation of Phase 10 is closing the operational loop between equipment health forecasting (Phase 6) and physical maintenance logistics.

### 7.1. Decision Semantics & Trigger Rules
- **Empirical AI4I Failure Probability**: Evaluated by Phase 6 gradient boosted failure classifier.
  - Decision threshold: **$\tau = 0.91$** (strictly enforced from Phase 6 empirical precision-recall optimization; never substituted with default 0.50).
- **Synthetic Vibration Scenario Alert**: Telemetry trigger: **$vibration \ge 3.80\text{ mm/s}$**.
  - Clearly labeled as a **CONFIGURED SYNTHETIC SCENARIO TRIGGER**.

### 7.2. Four Coupling Scenarios Evaluated

```mermaid
flowchart TD
    A[M2 Health Monitoring] --> B{P(failure) >= 0.91 OR Vib >= 3.8 mm/s?}
    B -- No --> C[NORMAL_OPERATION<br/>Spare Buffer Sufficient]
    B -- Yes --> D{Current Bearing Stock >= 1?}
    D -- No (0 units) --> E[CRITICAL_MAINTENANCE_BLOCKED<br/>Immediate Unplanned Downtime<br/>Lead Time: 7 Days]
    D -- Yes (1 unit) --> F[CONSTRAINED_MAINTENANCE<br/>Replace immediately, but stock drops to 0<br/>7-Day Vendor Exposure Window]
    D -- Yes (>= 2 units) --> G[MAINTENANCE_PERMITTED<br/>Post-maintenance buffer preserved]
```

1. **Scenario A: Empirical Equipment Failure Alert ($P(\text{fail}) = 0.925 \ge 0.91$)**:
   - Current Bearing Stock: 2.0 units
   - Overhaul Requirement: 1.0 unit
   - Stock Post-Maintenance: 1.0 unit (below ROP 1.37, close to SS 1.13)
   - Status: `MAINTENANCE_PERMITTED_BUFFER_RETAINED` (Risk: Medium)
   - Action: Execute overhaul; trigger immediate replenishment PO for 12 bearings ($EOQ$).
2. **Scenario B: Configured Synthetic Vibration Alert ($vib = 4.15\text{ mm/s} \ge 3.80$)**:
   - Current Bearing Stock: 2.0 units
   - Status: `MAINTENANCE_PERMITTED_BUFFER_RETAINED` (Risk: Medium)
   - Action: Identical physical overhaul trigger initiated via vibration excursion.
3. **Scenario C: Quiescent Operation ($P = 0.12, vib = 1.80\text{ mm/s}$)**:
   - Status: `NORMAL_OPERATION` (Risk: Low).
4. **Scenario D: Depleted Warehouse Stock (Stress Test with Current Stock = 0.0)**:
   - Trigger: $P(\text{fail}) = 0.94$, $vib = 4.20\text{ mm/s}$
   - Current Bearing Stock: 0.0 units
   - Status: `CRITICAL_MAINTENANCE_BLOCKED` (Risk: Critical)
   - **Lead Time Reality Caveat**: Specialized precision angular contact spindle bearings have a configured vendor delivery lead time of **7.0 days ($\pm 2.0$ days)**. Issuing an emergency PO **cannot instantaneously eliminate physical road/air transit times**. Machine 2 must halt or operate under emergency derating until physical spare delivery.

---

## 8. Five-Tier Shortage Risk Taxonomy

| Tier Identifier | Trigger Condition | Operational Meaning | Action Urgency | Shortage Risk Score |
| :--- | :--- | :--- | :--- | :--- |
| `OUT_OF_STOCK` | $\text{Stock} \le 0$ | Complete stockout; line stoppage or halted maintenance | `IMMEDIATE_EXPEDITE` | 1.00 |
| `CRITICAL_DEFICIT` | $0 < \text{Stock} \le SS$ | Safety stock breached; high probability of stockout before vendor delivery | `HIGH_PRIORITY` | 0.85 |
| `REORDER_NOW` | $SS < \text{Stock} \le ROP$ | Standard reorder point crossed; replenishment needed | `STANDARD_REORDER` | 0.50 |
| `OPTIMAL_BUFFER` | $ROP < \text{Stock} \le ROP + EOQ$ | Inventory within target operating range | `NONE` | 0.05 |
| `SURPLUS_INVENTORY` | $\text{Stock} > ROP + EOQ$ | Excess buffer; working capital trapped in holding cost | `MONITOR_HOLDING` | 0.00 |

---

## 9. Research Integrity & Scientific Limitations

1. **Deterministic Operations Research Scope**:
   - Phase 10 utilizes analytical Operations Research models ($SS$, $ROP$, $EOQ$, $DoS$). It does **NOT** build artificial machine learning benchmarks on inventory data because the inventory dataset is a controlled simulation state rather than high-frequency transactional data.
2. **Strict Demarcation of Machine 2 Thresholds**:
   - The AI4I empirical decision threshold is maintained strictly at **0.91** from Phase 6. The $3.80\text{ mm/s}$ vibration trigger is documented explicitly as a **synthetic scenario trigger** rather than an empirical ISO vibration standard.
3. **Transit Lead-Time Reality**:
   - We explicitly reject the naive assumption that emergency procurement eliminates lead times. In real-world MSMEs, specialized spares take 5–10 days to ship.
4. **Exclusion of Future Modules**:
   - Defect classification, SHAP explanations, RAG assistants, digital twins, and general recommendation engines are strictly out-of-scope for Phase 10 and were omitted.

---

## 10. Verification & Test Suite Summary

The Phase 10 test suite (`tests/test_inventory_intelligence.py`) provides 17 comprehensive unit and integration tests:

| Test Class | Test Case | Target Verification | Result |
| :--- | :--- | :--- | :--- |
| `TestInventoryFormulas` | `test_dynamic_safety_stock_calculation` | Dual-uncertainty formula analytical check ($SS=17.717$) | **PASSED** |
| `TestInventoryFormulas` | `test_reorder_point_calculation` | Analytical check ($ROP = 75.0$) | **PASSED** |
| `TestInventoryFormulas` | `test_eoq_wilson_harris_formula` | Wilson-Harris square root formula check ($EOQ=684.105$) | **PASSED** |
| `TestInventoryFormulas` | `test_days_of_supply` | Ratio verification ($DoS=10.0$) | **PASSED** |
| `TestInventoryFormulas` | `test_service_level_z_scaling` | $Z=1.645$ (95%) vs $Z=2.326$ (99%) scaling property | **PASSED** |
| `TestEdgeCasesAndValidation` | `test_zero_demand_scenario` | $d=0 \implies SS=0, ROP=0, EOQ=0, DoS=0$ | **PASSED** |
| `TestEdgeCasesAndValidation` | `test_zero_and_negative_stock` | Negative stock handling & `OUT_OF_STOCK` tier assignment | **PASSED** |
| `TestEdgeCasesAndValidation` | `test_invalid_lead_time_raises` | Negative lead times raise `ValueError` | **PASSED** |
| `TestEdgeCasesAndValidation` | `test_invalid_cost_parameters_raise` | Negative costs and invalid holding rates raise `ValueError` | **PASSED** |
| `TestEdgeCasesAndValidation` | `test_stockout_classification_tiers` | Transitions across all 5 inventory health tiers | **PASSED** |
| `TestMachine2MaintenanceCoupling` | `test_empirical_decision_threshold_091` | Enforces threshold $\tau=0.91$ ($0.905 \to \text{No}$, $0.910 \to \text{Yes}$) | **PASSED** |
| `TestMachine2MaintenanceCoupling` | `test_configured_synthetic_vibration_trigger` | Configured trigger $\ge 3.80\text{ mm/s}$ activates alert | **PASSED** |
| `TestMachine2MaintenanceCoupling` | `test_constrained_maintenance_and_lead_time_reality` | Stock 1.0 drops to 0.0 post-overhaul with 7-day transit warning | **PASSED** |
| `TestMachine2MaintenanceCoupling` | `test_depleted_stock_blocks_maintenance` | Stock 0.0 halts maintenance (`CRITICAL_MAINTENANCE_BLOCKED`) | **PASSED** |
| `TestDataIntegrityAndReproducibility` | `test_source_catalog_and_jobs_exist` | Confirms dataset file integrity & required columns | **PASSED** |
| `TestDataIntegrityAndReproducibility` | `test_synthetic_demand_derivation_deterministic` | Verifies deterministic, repeatable demand derivation | **PASSED** |
| `TestDataIntegrityAndReproducibility` | `test_service_layer_end_to_end` | Pydantic v2 validation, single SKU, plant summary, M2 coupling | **PASSED** |

### Regression Suite Status:
- **Phase 10 Tests**: 17 / 17 Passed (100%)
- **Total Project Tests**: 85 / 85 Passed (100%)
- **Zero Regressions** across Phase 0 through Phase 9.
