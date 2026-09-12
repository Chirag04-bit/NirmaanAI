# Dataset 09: Textile MSME Shop Floor Digital Twin Dataset

## 1. Overview & Provenance
This dataset provides a physics-guided digital twin simulation of an Indian composite textile spinning and weaving MSME (`TX_LINE_01`). It models yarn spinning, warping, rapier weaving, spindle bearing degradation, broken ends, fabric defects, and activity-based rupee losses.

- **Generator Source**: `src/data/synthetic_generator.py` (`TextileLoomSimulator`)
- **Random Seed**: `101` (Deterministic reproducibility)
- **Simulation Duration**: 30 consecutive calendar days (720 hours)
- **Telemetry Sampling Interval**: Every 5 minutes (43,200 readings total across 5 machines)

> [!NOTE]
> **Research-Integrity Statement**: The synthetic environment provides controlled ground truth for algorithmic validation; it does not establish real-world machine causality. The simulator reproduces the configured degradation dynamics, including >1.8× baseline vibration elevation and cycle-time slowdown during the controlled degradation episodes, providing a testbed to verify whether downstream models can recover known relationships from noisy observations:
> $$\text{sensor degradation} \to \text{machine performance deterioration} \to \text{cycle-time increase} \to \text{queue/WIP accumulation} \to \text{bottleneck} \to \text{downtime/scrap} \to \text{loss}$$

## 2. Textile Line Configuration & Equipment
The spinning and weaving shed consists of sequential processing stations:
1. **TX01 (Carding Engine)**: High-Production Carding Machine (Design: 35s/sliver kg, Baseline Power: 18 kW, Alert Vib: 3.2 mm/s)
2. **TX02 (Ring Spinning Frame)**: 1000-Spindle Ring Frame for 30s Carded Yarn (Design: 40s/bobbin, Baseline Power: 28 kW, Spindle RPM: 14,500, Alert Vib: 3.6 mm/s, Critical Vib: 5.2 mm/s)
3. **TX03 (Sectional Warper)**: High-Speed Sectional Warp Beam Sizing (Design: 25s, Baseline Power: 14 kW, Alert Vib: 2.8 mm/s)
4. **TX04 (Rapier Weaving Loom)**: High-Speed Electronic Rapier Loom (Design: 50s/meter, Baseline Power: 9.5 kW, Alert Vib: 3.9 mm/s, Critical Vib: 5.5 mm/s)
5. **TX05 (Inspection Range)**: Automatic Fabric Inspection, Calendering & Packaging (Design: 20s/meter, Baseline Power: 6 kW)

## 3. Configured Ground-Truth Scenario Parameters (Ring Spinning Degradation Episode)
The following numerical parameters are **intentionally configured ground-truth scenario parameters** within the simulator to model a controlled degradation episode. They are NOT measured factory observations, empirical measurements, real-world validated thresholds, or experimentally observed values:
- **Episode Window**: Days 16.0 to 19.0.
- **Physical Mechanism Simulated**: Ring spinning spindle bolster bearing wear exacerbated by airborne cotton lint friction.
- **Configured Trajectory**:
  - Spindle Speed: simulated drop from nominal $14,500\text{ RPM} \to 11,200\text{ RPM}$ as bearing drag increases.
  - RMS Vibration: simulated climb from $1.3\text{ mm/s}$ baseline $\to 3.6\text{ mm/s}$ (alert limit) $\to 5.4\text{ mm/s}$ (emergency halt).
  - Spindle temperature: simulated $+16.0^\circ\text{C}$ elevation above ambient.
  - Active power consumption: simulated surge from $28.0\text{ kW}$ to $34.0\text{ kW}$.
- **Configured Operational Impact**:
  - Actual cycle time: slows from nominal $40.0\text{s} \to 55.0\text{s}$ per bobbin ($37.5\%$ slowdown).
  - Scrap rate: simulated increase from nominal $1.2\%$ to $9.0\%$ due to warp end breakages.
  - Dispatch delay: downstream weaving looms suffer yarn starvation with $15\text{--}32\text{ minutes}$ delay.
- **Configured Emergency Downtime & Stockout Scenario**:
  - Emergency halt on Day 19: $120\text{ minutes}$ (2.0 hours) of unplanned maintenance stoppage (`TX_MAINT_0002`).
  - Spindle bolster assembly replaced; lubrication reservoir flushed.
  - Inventory for `TX_SKU_RING_SPINDLE_BOLSTER` depleted to 1 unit (below configured safety stock of 4 units).

## 4. Financial Cost Accounting (Configured MSME Assumptions)
Financial losses are computed according to the balance equation:
$$\text{Loss}_{\text{Total}} = \text{Loss}_{\text{Downtime}} + \text{Loss}_{\text{Scrap}} + \text{Loss}_{\text{Rework}} + \text{Loss}_{\text{Energy}}$$

These figures use **configured simulation assumptions** based on Indian textile MSME benchmarks:
- **Downtime Loss**: $\text{Hours} \times ₹3,800/\text{hr}$
- **Cotton Yarn Waste / Scrap**: $\text{Weight (kg)} \times ₹280/\text{kg}$
- **Fabric Mending / Splicing Rework**: $\text{Hours} \times ₹220/\text{hr}$
- **Peak Electricity Tariff Surcharge**: Surcharge of ₹4.00/kWh during 18:00–22:00 window.

## 5. Schema & File Manifest
All tables adhere strictly to Pydantic v2 schemas in `src/data/schema.py`:
- `machines.csv` (5 rows, 12 cols)
- `sensor_readings.csv` (43,200 rows, 13 cols) & `sensor_readings.parquet`
- `production_jobs.csv` (300 rows, 12 cols)
- `maintenance_records.csv` (3 rows, 9 cols)
- `inventory_items.csv` (4 rows, 8 cols)
- `operational_losses.csv` (265 rows, 12 cols)
