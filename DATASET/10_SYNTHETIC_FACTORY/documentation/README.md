# Dataset 10: Integrated Factory Digital Twin (Precision Auto-Components MSME)

## 1. Overview & Provenance
This dataset provides a physics-guided digital twin simulation of a 5-machine discrete precision auto-components manufacturing line (`LINE_01`). It interconnects high-frequency IoT telemetry, MES production schedules, ERP spare parts inventory, computerized maintenance management systems (CMMS), and activity-based rupee cost accounting.

- **Generator Source**: `src/data/synthetic_generator.py` (`FactorySimulator`)
- **Random Seed**: `42` (Deterministic reproducibility)
- **Simulation Duration**: 30 consecutive calendar days (720 hours)
- **Telemetry Sampling Interval**: Every 5 minutes (43,200 readings total across 5 machines)

> [!NOTE]
> **Research-Integrity Statement**: The synthetic environment provides controlled ground truth for algorithmic validation; it does not establish real-world machine causality. The simulator reproduces the configured degradation dynamics, including >1.8× baseline vibration elevation and cycle-time slowdown during the controlled degradation episodes, providing a testbed to verify whether downstream models can recover known relationships from noisy observations:
> $$\text{sensor degradation} \to \text{machine performance deterioration} \to \text{cycle-time increase} \to \text{queue/WIP accumulation} \to \text{bottleneck} \to \text{downtime/scrap} \to \text{loss}$$

## 2. Line Configuration & Machine Topology
The discrete auto-component line consists of 5 sequential manufacturing stations:
1. **M1 (CNC Lathe)**: Rough Turning & Profiling (Design Cycle: 60s, Baseline Power: 15 kW, Alert Vib: 3.5 mm/s)
2. **M2 (VMC Milling)**: Precision Pocket & Profile Milling (Design Cycle: 45s, Baseline Power: 22 kW, Alert Vib: 3.8 mm/s, Critical Vib: 5.5 mm/s)
3. **M3 (Grinder)**: Cylindrical & Surface Grinding (Design Cycle: 30s, Baseline Power: 11 kW, Alert Vib: 3.0 mm/s)
4. **M4 (Inspection)**: Automated Vision Inspection Station (Design Cycle: 20s, Baseline Power: 4.5 kW)
5. **M5 (Assembly)**: Packaging & Dispatch Cell (Design Cycle: 40s, Baseline Power: 7.5 kW)

## 3. Configured Ground-Truth Scenario Parameters (Machine 2 Degradation Episode)
The following numerical parameters are **intentionally configured ground-truth scenario parameters** within the simulator to model a controlled degradation episode. They are NOT measured factory observations, empirical measurements, real-world validated thresholds, or experimentally observed values:
- **Episode Window**: Days 18.0 to 21.0.
- **Physical Mechanism Simulated**: Spindle bearing lubrication starvation causing accelerated friction.
- **Configured Trajectory**:
  - RMS Vibration: $1.4\text{ mm/s}$ baseline $\to 3.8\text{ mm/s}$ (alert limit on Day 19) $\to 5.6\text{ mm/s}$ (emergency trip threshold on Day 21).
  - Spindle temperature: simulated $+18.0^\circ\text{C}$ elevation above diurnal ambient baseline.
  - Active power draw: simulated increase from $22.0\text{ kW}$ to $27.0\text{ kW}$.
  - Acoustic noise: simulated increase from $74\text{ dB}$ to $86\text{ dB}$.
- **Configured Shop-Floor Operational Cascades**:
  - Actual cycle time: slows from nominal $45.0\text{s} \to 58.0\text{--}65.0\text{s}$ ($\approx 37.8\%$ slowdown).
  - Dispatch delay: upstream queue buildup forces $12\text{--}28\text{ minutes}$ delay.
  - Part scrap rate: simulated increase from $1.5\%$ to $8.0\%$.
- **Configured Emergency Downtime & Inventory Scenario**:
  - Emergency halt on Day 21: $150\text{ minutes}$ (2.5 hours) of unplanned maintenance downtime (`MAINT_0003`).
  - Spindle bearing replaced by technician Suresh / Tech_Kuntal_Sr.
  - Spare parts stock for `SKU_SPINDLE_BEARING_M2` drops to 1 unit (below configured safety stock of 3 units).

## 4. Financial Loss Model (Configured MSME Assumptions)
Financial impact is calculated disaggregated per event and job using the balance equation:
$$\text{Loss}_{\text{Total}} = \text{Loss}_{\text{Downtime}} + \text{Loss}_{\text{Scrap}} + \text{Loss}_{\text{Rework}} + \text{Loss}_{\text{Energy}}$$

These rates are **configured simulation assumptions** based on Indian MSME benchmarks:
- **Downtime Loss**: $\text{Hours} \times ₹4,500/\text{hr}$
- **Scrap Loss**: $\text{Weight (kg)} \times ₹350/\text{kg}$
- **Rework Loss**: $\text{Hours} \times ₹280/\text{hr}$
- **Peak Electricity Tariff Surcharge**: $\Delta \text{kWh} \times (₹12.50 - ₹8.50)/\text{kWh}$

## 5. Schema & File Manifest
All tables adhere strictly to Pydantic v2 schemas in `src/data/schema.py`:
- `machines.csv` (5 rows, 12 cols)
- `sensor_readings.csv` (43,200 rows, 13 cols) & `sensor_readings.parquet`
- `production_jobs.csv` (300 rows, 12 cols)
- `maintenance_records.csv` (4 rows, 9 cols)
- `inventory_items.csv` (5 rows, 8 cols)
- `operational_losses.csv` (246 rows, 12 cols)
