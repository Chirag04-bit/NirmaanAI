# Dataset 09: Textile MSME Shop Floor Digital Twin Dataset

## 1. Overview & Provenance
This dataset simulates the operational dynamics of an Indian composite textile spinning and weaving MSME (`TX_LINE_01`). It models yarn spinning, warping, rapier weaving, spindle bearing degradation, broken ends, fabric defects, and activity-based rupee losses.

- **Generator Source**: `src/data/synthetic_generator.py` (`TextileLoomSimulator`)
- **Random Seed**: `101` (Deterministic reproducibility)
- **Simulation Duration**: 30 consecutive calendar days (720 hours)
- **Telemetry Sampling Interval**: Every 5 minutes (43,200 readings total across 5 machines)

## 2. Textile Line Configuration & Equipment
The spinning and weaving shed consists of sequential processing stations:
1. **TX01 (Carding Engine)**: High-Production Carding Machine (Design: 35s/sliver kg, Baseline Power: 18 kW, Alert Vib: 3.2 mm/s)
2. **TX02 (Ring Spinning Frame)**: 1000-Spindle Ring Frame for 30s Carded Yarn (Design: 40s/bobbin, Baseline Power: 28 kW, Spindle RPM: 14,500, Alert Vib: 3.6 mm/s, Critical Vib: 5.2 mm/s)
3. **TX03 (Sectional Warper)**: High-Speed Sectional Warp Beam Sizing (Design: 25s, Baseline Power: 14 kW, Alert Vib: 2.8 mm/s)
4. **TX04 (Rapier Weaving Loom)**: High-Speed Electronic Rapier Loom (Design: 50s/meter, Baseline Power: 9.5 kW, Alert Vib: 3.9 mm/s, Critical Vib: 5.5 mm/s)
5. **TX05 (Inspection Range)**: Automatic Fabric Inspection, Calendering & Packaging (Design: 20s/meter, Baseline Power: 6 kW)

## 3. Ring Spinning Degradation & Bottleneck Dynamics
- **Episode Timeline**: Days 16.0 to 19.0.
- **Physical Mechanism**: Ring spinning spindle bolster bearing wear exacerbated by airborne cotton fly and lint buildup in the bearing oil chamber.
- **Sensor Manifestation**:
  - RMS Vibration rises from 1.3 mm/s baseline $\to$ 3.6 mm/s (Day 17 alert) $\to$ 5.4 mm/s (Day 19 emergency halt).
  - Spindle speed drops from 14,500 RPM down to 11,200 RPM as bearing drag increases.
  - Spindle temperature rises $+16.0^\circ\text{C}$ above ambient.
  - Power consumption surges from 28.0 kW to 34.0 kW.
- **Operational Impact**:
  - Yarn delivery cycle time slows from 40.0s to 55.0s (37.5% slowdown).
  - High yarn breakage rate leads to a spike in scrap cotton waste (from 1.2% to 9.0%).
  - Weaving looms downstream suffer yarn starvation and scheduling delays (15–32 minutes dispatch delays).
- **Emergency Halt (Day 19)**:
  - TX02 undergoes a 120-minute (2.0 hours) emergency shutdown (`TX_MAINT_0002`).
  - Spindle bolster assembly replaced; lubrication reservoir flushed.
  - Inventory for `TX_SKU_RING_SPINDLE_BOLSTER` depleted to 1 unit (below safety stock of 4 units).

## 4. Financial Cost Accounting (INR)
Financial losses are computed according to Indian textile MSME benchmarks:
- **Downtime Loss**: $\text{Hours} \times ₹3,800/\text{hr}$
- **Cotton Yarn Waste / Scrap**: $\text{Weight (kg)} \times ₹280/\text{kg}$
- **Fabric Mending / Splicing Rework**: $\text{Hours} \times ₹220/\text{hr}$
- **Peak Electricity Tariff**: Surcharge of ₹4.00/kWh during 18:00–22:00 window.

## 5. Schema & File Manifest
- `machines.csv` (5 rows, 12 cols)
- `sensor_readings.csv` (43,200 rows, 13 cols) & `sensor_readings.parquet`
- `production_jobs.csv` (300 rows, 12 cols)
- `maintenance_records.csv` (3 rows, 9 cols)
- `inventory_items.csv` (4 rows, 8 cols)
- `operational_losses.csv` (264 rows, 12 cols)
