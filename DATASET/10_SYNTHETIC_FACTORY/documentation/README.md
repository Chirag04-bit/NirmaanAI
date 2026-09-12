# Dataset 10: Integrated Factory Digital Twin (Precision Auto-Components MSME)

## 1. Overview & Provenance
This dataset provides a physics-guided, synchronized digital twin of a 5-machine discrete precision auto-components manufacturing line (`LINE_01`). It connects high-frequency IoT telemetry, MES production schedules, ERP spare parts inventory, computerized maintenance management systems (CMMS), and activity-based rupee cost accounting.

- **Generator Source**: `src/data/synthetic_generator.py` (`FactorySimulator`)
- **Random Seed**: `42` (Deterministic reproducibility)
- **Simulation Duration**: 30 consecutive calendar days (720 hours)
- **Telemetry Sampling Interval**: Every 5 minutes (43,200 readings total across 5 machines)

## 2. Line Configuration & Machine Topology
The discrete auto-component line consists of sequential manufacturing stations:
1. **M1 (CNC Lathe)**: Rough Turning & Profiling (Design Cycle: 60s, Baseline Power: 15 kW, Alert Vib: 3.5 mm/s)
2. **M2 (VMC Milling)**: Precision Pocket & Profile Milling (Design Cycle: 45s, Baseline Power: 22 kW, Alert Vib: 3.8 mm/s, Critical Vib: 5.5 mm/s)
3. **M3 (Grinder)**: Cylindrical & Surface Grinding (Design Cycle: 30s, Baseline Power: 11 kW, Alert Vib: 3.0 mm/s)
4. **M4 (Inspection)**: Automated Vision Inspection Station (Design Cycle: 20s, Baseline Power: 4.5 kW)
5. **M5 (Assembly)**: Packaging & Dispatch Cell (Design Cycle: 40s, Baseline Power: 7.5 kW)

## 3. The Machine 2 Degradation & Bottleneck Scenario
- **Episode Timeline**: Days 18.0 to 21.0.
- **Physical Mechanism**: Spindle bearing lubrication starvation causing accelerated metal-on-metal friction.
- **Sensor Manifestation**:
  - Root Mean Square (RMS) Vibration rises from 1.4 mm/s baseline $\to$ 3.8 mm/s (Day 19 alert threshold) $\to$ 5.6 mm/s (Day 21 emergency trip).
  - Spindle temperature escalates $+18.0^\circ\text{C}$ above diurnal ambient baseline.
  - Active power surges from 22.0 kW to 27.0 kW under cutting load.
  - Acoustic emission increases from 74 dB to 86 dB.
- **Shop-Floor Operational Cascades**:
  - Machine 2 cycle time slows down from nominal 45.0s to 58.0s–65.0s (30–45% cycle slowdown).
  - Batch completion delays cascade upstream: Work-in-Progress (WIP) buffer overflows, causing queue wait times to jump 12–28 minutes.
  - Finished batches push past the 18:00 cutoff into peak electricity tariff hours (₹12.50/kWh vs base ₹8.50/kWh).
  - Part scrap rate on M2 jumps from 1.5% to 8.0%.
- **Emergency Halt (Day 21)**:
  - Emergency vibration trip halts M2 for 150 minutes (2.5 hours) of unplanned maintenance (`MAINT_0003`).
  - Spindle bearing replaced by technician Suresh/Tech_Kuntal_Sr.
  - Inventory check reveals `SKU_SPINDLE_BEARING_M2` stock dropped to 1 unit (below safety stock of 3), triggering an automated reorder alert.

## 4. Financial Loss Formulation (INR)
Financial impact is calculated disaggregated per event and job:
$$\text{Loss}_{\text{Total}} = \text{Loss}_{\text{Downtime}} + \text{Loss}_{\text{Scrap}} + \text{Loss}_{\text{Rework}} + \text{Loss}_{\text{Energy}}$$
- **Downtime**: $\text{Hours} \times ₹4,500/\text{hr}$
- **Scrap**: $\text{Weight (kg)} \times ₹350/\text{kg}$
- **Rework**: $\text{Hours} \times ₹280/\text{hr}$
- **Peak Energy Surcharge**: $\Delta \text{kWh} \times (₹12.50 - ₹8.50)/\text{kWh}$

## 5. Schema & File Manifest
All tables adhere strictly to Pydantic v2 schemas in `src/data/schema.py`:
- `machines.csv` (5 rows, 12 cols)
- `sensor_readings.csv` (43,200 rows, 13 cols) & `sensor_readings.parquet`
- `production_jobs.csv` (300 rows, 12 cols)
- `maintenance_records.csv` (4 rows, 9 cols)
- `inventory_items.csv` (5 rows, 8 cols)
- `operational_losses.csv` (245 rows, 12 cols)
