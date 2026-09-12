# NirmaanAI Synthetic Factory Data Specification & Mathematical Formulation

## 1. Executive Summary & Design Principles
The NirmaanAI Synthetic Data Engine (`src/data/synthetic_generator.py`) generates synchronized, multi-modal factory digital twins designed specifically for Indian MSMEs in two target verticals:
1. **Discrete Precision Auto-Components** (`DATASET/10_SYNTHETIC_FACTORY`): 5-machine cell (`M1` to `M5`) simulating precision CNC turning, VMC milling, grinding, vision inspection, and assembly.
2. **Textile Weaving & Spinning MSME** (`DATASET/09_TEXTILE_MANUFACTURING`): 5-machine process line (`TX01` to `TX05`) simulating carding, ring spinning, sectional warping, rapier weaving, and fabric inspection.

### Research-Integrity & Validation Framing:
- **Controlled Validation Environment**: The synthetic environment provides controlled ground truth for algorithmic validation; it does not establish real-world machine causality.
- **Recoverability Benchmark**: The controlled ground truth allows downstream experiments (Phases 6–10) to test whether NirmaanAI can recover known relationships from noisy/generated observations, specifically:
  $$\text{sensor degradation} \to \text{machine performance deterioration} \to \text{cycle-time increase} \to \text{queue/WIP accumulation} \to \text{bottleneck} \to \text{downtime/scrap} \to \text{operational and financial loss}$$
- **Configured vs Empirical Parameters**: All scenario thresholds, deterioration profiles, and downtime intervals are intentionally configured ground-truth scenario parameters. They must NOT be described as measured factory observations, empirical measurements, real-world validated thresholds, or experimentally observed values.
- **Deterministic Reproducibility**: Governed by deterministic NumPy random state seeds (`seed=42` for Auto-Components, `seed=101` for Textile), with automatic RNG resets before dataset serialization.
- **Strict Schema Compliance**: Every generated entity validates against NirmaanAI unified Pydantic v2 schemas (`src/data/schema.py`) and SQLAlchemy ORM models (`src/data/sql_schema.py`).

---

## 2. Mathematical Models & Configured Signal Dynamics

### 2.1 Ambient Environment & Diurnal Cycling
Factory ambient temperature oscillates cyclically over a 24-hour period with minimum at 05:00 and maximum at 14:00, modulated by Gaussian thermal fluctuations:
$$T_{\text{ambient}}(t) = 22.0 + 8.0 \cdot \sin\left(\frac{(h(t) - 8)\pi}{12}\right) + \epsilon_{\text{ambient}}, \quad \epsilon_{\text{ambient}} \sim \mathcal{N}(0, 0.5^2)$$
where $h(t) \in [0, 23]$ is the local solar hour of timestamp $t$.

### 2.2 Machine 2 (VMC Milling) — Configured Ground-Truth Scenario Parameters
Machine 2 is configured with nominal baseline vibration $v_0 = 1.4\text{ mm/s}$ and nominal cutting power $P_0 = 22.0\text{ kW}$.
During the controlled degradation episode spanning Day 18.0 to Day 21.0 ($t_{\text{start}} = 18.0, t_{\text{end}} = 21.0$):

The normalized degradation progress metric $\rho(t)$ is defined as:
$$\rho(t) = \frac{t_{\text{day}} - 17.0}{4.0} \in [0.0, 1.0]$$

#### Configured Evolution Functions:
1. **Vibration (RMS mm/s)**:
   $$v_{M2}(t) = \max\left(v_0, \, v_0 + 4.2 \cdot \rho(t) + \mathcal{N}(0, 0.3^2)\right)$$
   *Configured Scenario Trajectory*: Climbs from $1.4\text{ mm/s} \to 3.8\text{ mm/s}$ (alert limit on Day 19) $\to 5.6\text{ mm/s}$ (critical trip threshold on Day 21).

2. **Process Temperature ($^\circ\text{C}$)**:
   $$T_{\text{proc}}(t) = T_{\text{ambient}}(t) + 20.0 + 18.0 \cdot \rho(t) + \mathcal{N}(0, 0.8^2)$$
   Simulated bearing friction generates an excess $+18.0^\circ\text{C}$ temperature buildup.

3. **Power Consumption (kW)**:
   $$P_{\text{active}}(t) = P_0 + 5.0 \cdot \rho(t) + \mathcal{N}(0, 0.5^2)$$
   Simulated mechanical resistance elevates motor draw from $22.0\text{ kW}$ to $27.0\text{ kW}$.

4. **Acoustic Noise (dB)**:
   $$S_{\text{acoustic}}(t) = 74.0 + 12.0 \cdot \rho(t) + \mathcal{N}(0, 1.0^2)$$

5. **Spindle Torque (Nm)**:
   Derived deterministically from simulated power and speed:
   $$\tau(t) = \frac{P_{\text{active}}(t) \times 60000}{2\pi \times \omega(t)}$$
   where $\omega(t) \sim \mathcal{N}(1500, 15^2)\text{ RPM}$.

6. **Lubrication Level (%)**:
   $$L_{\text{oil}}(t) = \max\left(20.0, \, 85.0 - 50.0 \cdot \rho(t)\right)$$

### 2.3 Textile Ring Spinning Frame TX02 — Configured Ground-Truth Scenario Parameters
During the controlled degradation episode spanning Day 16.0 to Day 19.0:
1. **Spindle Speed**: Drops from nominal $14,500\text{ RPM} \to 11,200\text{ RPM}$ due to simulated bolster bearing drag.
2. **Vibration (RMS mm/s)**: Climbs from baseline $1.3\text{ mm/s} \to 5.4\text{ mm/s}$ emergency halt threshold.
3. **Yarn Delivery Cycle Time**: Slows from nominal $40.0\text{s} \to 55.0\text{s}$ per bobbin.
4. **Scrap Rate**: Escalates from nominal $1.2\% \to 9.0\%$ due to warp end breakages.
5. **Emergency Downtime**: $120\text{ min}$ (2.0 hours) unplanned stoppage on Day 19 (`TX_MAINT_0002`).
6. **Stockout Scenario**: Spindle bolster spare parts (`TX_SKU_RING_SPINDLE_BOLSTER`) inventory drops to 1 unit (below safety stock of 4).

---

## 3. Production Scheduling & Cycle Slowdown Model

### 3.1 Nominal vs Configured Degraded Execution
Under nominal conditions, the actual cycle time $C_{\text{actual}}$ fluctuates mildly around design cycle time $C_{\text{design}}$:
$$C_{\text{actual}} = C_{\text{design}} \times U(0.98, 1.04)$$

During the controlled degradation episode on Machine 2 ($C_{\text{design}} = 45.0\text{ s}$):
$$C_{\text{actual, M2}} = C_{\text{design}} \times U(1.30, 1.45) \implies 58.0\text{ s} \text{ to } 65.0\text{ s} \quad (\approx 37.8\% \text{ slowdown})$$

### 3.2 Queue Delays and Scrap Binomial Distribution
- **Configured Dispatch Delay**: Upstream buffer accumulation forces dispatch delays $\Delta t_{\text{start}} \sim U(12, 28)\text{ minutes}$.
- **Configured Scrap Generation**: Degraded milling tolerances increase scrap probability from nominal $p_{\text{scrap}} = 0.015$ to degraded $p_{\text{scrap, deg}} = 0.080$:
  $$N_{\text{scrap}} \sim \text{Binomial}(N_{\text{batch}}, p_{\text{scrap}})$$
  $$N_{\text{completed}} = N_{\text{batch}} - N_{\text{scrap}}$$
- **Emergency Downtime**: Day 21 emergency halt results in $150\text{ minutes}$ (2.5 hours) of unplanned maintenance downtime (`MAINT_0003`).

---

## 4. Disaggregated Financial Loss Model (INR)

For every operational deviation or stoppage event, financial losses are computed deterministically:

$$\text{Loss}_{\text{Total}} = \text{Loss}_{\text{Downtime}} + \text{Loss}_{\text{Scrap}} + \text{Loss}_{\text{Rework}} + \text{Loss}_{\text{Energy}}$$

### Distinction Between Configured Assumptions and Empirical Observations:
These rates represent **configured simulation assumptions** based on Indian MSME industry benchmarks. They provide a deterministic financial ground truth for evaluating downstream decision copilot recommendations; they are not empirical financial observations.

1. **Downtime Loss**:
   $$\text{Loss}_{\text{Downtime}} = \left(\frac{t_{\text{downtime\_min}}}{60}\right) \times R_{\text{downtime}}$$
   - Auto-Components configured rate: $R_{\text{downtime}} = ₹4,500/\text{hr}$
   - Textile MSME configured rate: $R_{\text{downtime}} = ₹3,800/\text{hr}$

2. **Scrap Loss**:
   $$\text{Loss}_{\text{Scrap}} = \left(N_{\text{scrap}} \times w_{\text{unit\_kg}}\right) \times R_{\text{scrap}}$$
   - Auto-Components configured rate: $w = 0.8\text{ kg/part}, R_{\text{scrap}} = ₹350/\text{kg}$
   - Textile MSME configured rate: $w = 0.8\text{ kg/bobbin}, R_{\text{scrap}} = ₹280/\text{kg}$

3. **Technician Rework Loss**:
   $$\text{Loss}_{\text{Rework}} = h_{\text{rework}} \times R_{\text{rework}}$$
   - Auto-Components configured rate: $R_{\text{rework}} = ₹280/\text{hr}$
   - Textile MSME configured rate: $R_{\text{rework}} = ₹220/\text{hr}$

4. **Time-of-Day (ToD) Peak Electricity Surcharge**:
   If job completion slips into the peak tariff window ($18:00 \le h < 22:00$):
   $$\text{Loss}_{\text{Energy}} = P_{\text{active}} \times t_{\text{duration\_hr}} \times (R_{\text{peak}} - R_{\text{base}})$$
   - Configured Base Tariff: $R_{\text{base}} = ₹8.50/\text{kWh}$
   - Configured Peak Tariff: $R_{\text{peak}} = ₹12.50/\text{kWh}$
   - Configured Surcharge: $\Delta R = ₹4.00/\text{kWh}$

---

## 5. Summary Table: Configured Ground-Truth Scenario Parameters

| Parameter | Discrete Auto-Components (Dataset 10) | Textile MSME (Dataset 09) | Status |
| :--- | :--- | :--- | :--- |
| **Primary Line ID** | `LINE_01` (5 machines) | `TX_LINE_01` (5 machines) | Configured line topology |
| **Target Machine** | `M2` (VMC Milling Center) | `TX02` (Ring Spinning Frame) | Configured scenario target |
| **Degradation Window** | Days 18 to 21 | Days 16 to 19 | Configured episode window |
| **Baseline $\to$ Peak Vib** | $1.4\text{ mm/s} \to 3.8 \to 5.6\text{ mm/s}$ | $1.3\text{ mm/s} \to 3.6 \to 5.4\text{ mm/s}$ | Configured scenario parameters |
| **Speed Dynamics** | Nominal $\sim 1500\text{ RPM}$ | $14,500\text{ RPM} \to 11,200\text{ RPM}$ | Configured scenario parameters |
| **Nominal $\to$ Degraded Cycle** | $45.0\text{ s} \to 58.0\text{--}65.0\text{ s}$ | $40.0\text{ s} \to 55.0\text{ s}$ | Configured scenario parameters |
| **Dispatch Delay** | $12\text{--}28\text{ minutes}$ | $15\text{--}32\text{ minutes}$ | Configured scenario parameters |
| **Scrap Rate** | $1.5\% \to 8.0\%$ | $1.2\% \to 9.0\%$ | Configured scenario parameters |
| **Emergency Downtime** | Day 21 ($150\text{ min}$, ₹11,670 loss) | Day 19 ($120\text{ min}$, ₹7,930 loss) | Configured scenario parameters |
| **Inventory Alert** | `SKU_SPINDLE_BEARING_M2` drops to 1 (safety 3) | `TX_SKU_RING_SPINDLE_BOLSTER` drops to 1 (safety 4) | Configured scenario parameters |
| **Total Telemetry Rows** | 43,200 rows (CSV & Parquet) | 43,200 rows (CSV & Parquet) | Simulated dataset output |
| **Total Jobs Simulated** | 300 batches | 300 batches | Simulated dataset output |
