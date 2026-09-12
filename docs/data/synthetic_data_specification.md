# NirmaanAI Synthetic Factory Data Specification & Mathematical Formulation

## 1. Executive Summary & Design Principles
The NirmaanAI Synthetic Data Engine (`src/data/synthetic_generator.py`) generates synchronized, multi-modal factory digital twins designed specifically for Indian MSMEs in two target verticals:
1. **Discrete Precision Auto-Components** (`DATASET/10_SYNTHETIC_FACTORY`): 5-machine cell (`M1` to `M5`) simulating high-precision CNC turning, VMC milling, grinding, vision inspection, and assembly.
2. **Textile Weaving & Spinning MSME** (`DATASET/09_TEXTILE_MANUFACTURING`): 5-machine process line (`TX01` to `TX05`) simulating carding, ring spinning, sectional warping, rapier weaving, and fabric inspection.

### Architectural Principles:
- **Physics-Guided Time Series**: Environmental and mechanical laws govern signal relationships (thermal conduction, diurnal ambient oscillation, load-torque relations, vibration power spectra).
- **Deterministic Reproducibility**: Governed by deterministic NumPy random state seeds (`seed=42` for Auto-Components, `seed=101` for Textile).
- **Cross-Layer Coupling**: Physical sensor deterioration directly drives MES job completion slowdowns, ERP inventory consumption, CMMS maintenance actions, and activity-based rupee losses.
- **Strict Schema Compliance**: Every generated entity validates against NirmaanAI unified Pydantic v2 schemas (`src/data/schema.py`) and SQLAlchemy ORM models (`src/data/sql_schema.py`).

---

## 2. Mathematical Models & Signal Physics

### 2.1 Ambient Environment & Diurnal Cycling
Factory ambient temperature oscillates cyclically over a 24-hour period with minimum at 05:00 and maximum at 14:00, modulated by Gaussian thermal fluctuations:
$$T_{\text{ambient}}(t) = 22.0 + 8.0 \cdot \sin\left(\frac{(h(t) - 8)\pi}{12}\right) + \epsilon_{\text{ambient}}, \quad \epsilon_{\text{ambient}} \sim \mathcal{N}(0, 0.5^2)$$
where $h(t) \in [0, 23]$ is the local solar hour of timestamp $t$.

### 2.2 Machine 2 (VMC Milling) Spindle Degradation Episode
Machine 2 operates with nominal baseline vibration $v_0 = 1.4\text{ mm/s}$ and nominal cutting power $P_0 = 22.0\text{ kW}$.
During the designated degradation episode spanning Day 18.0 to Day 21.0 ($t_{\text{start}} = 18.0, t_{\text{end}} = 21.0$):

The normalized degradation progress metric $\rho(t)$ is defined as:
$$\rho(t) = \frac{t_{\text{day}} - 17.0}{4.0} \in [0.0, 1.0]$$

#### Sensor Evolution Functions:
1. **Vibration (RMS mm/s)**:
   $$v_{M2}(t) = \max\left(v_0, \, v_0 + 4.2 \cdot \rho(t) + \mathcal{N}(0, 0.3^2)\right)$$
   *Evolution*: Climbs from $1.4\text{ mm/s} \to 3.8\text{ mm/s}$ (alert limit crossed on Day 19) $\to 5.6\text{ mm/s}$ (critical trip threshold on Day 21).

2. **Process Temperature ($^\circ\text{C}$)**:
   $$T_{\text{proc}}(t) = T_{\text{ambient}}(t) + 20.0 + 18.0 \cdot \rho(t) + \mathcal{N}(0, 0.8^2)$$
   Bearing lubrication starvation induces friction, generating an excess $+18.0^\circ\text{C}$ temperature buildup.

3. **Power Consumption (kW)**:
   $$P_{\text{active}}(t) = P_0 + 5.0 \cdot \rho(t) + \mathcal{N}(0, 0.5^2)$$
   Mechanical resistance elevates motor draw from $22.0\text{ kW}$ to $27.0\text{ kW}$.

4. **Acoustic Noise (dB)**:
   $$S_{\text{acoustic}}(t) = 74.0 + 12.0 \cdot \rho(t) + \mathcal{N}(0, 1.0^2)$$

5. **Spindle Torque (Nm)**:
   Derived directly from active power and rotational speed:
   $$\tau(t) = \frac{P_{\text{active}}(t) \times 60000}{2\pi \times \omega(t)}$$
   where $\omega(t) \sim \mathcal{N}(1500, 15^2)\text{ RPM}$.

6. **Lubrication Level (%)**:
   $$L_{\text{oil}}(t) = \max\left(20.0, \, 85.0 - 50.0 \cdot \rho(t)\right)$$

---

## 3. Production Scheduling & Cycle Slowdown Model

### 3.1 Nominal vs Degraded Execution
Under nominal conditions, the actual cycle time $C_{\text{actual}}$ fluctuates mildly around design cycle time $C_{\text{design}}$:
$$C_{\text{actual}} = C_{\text{design}} \times U(0.98, 1.04)$$

During the degradation episode on Machine 2 ($C_{\text{design}} = 45.0\text{ s}$):
$$C_{\text{actual, M2}} = C_{\text{design}} \times U(1.30, 1.45) \implies 58.5\text{ s} \text{ to } 65.2\text{ s} \quad (\approx 37.8\% \text{ slowdown})$$

### 3.2 Queue Delays and Scrap Binomial Distribution
- **Dispatch Delay**: Upstream buffer accumulation forces dispatch delays $\Delta t_{\text{start}} \sim U(12, 28)\text{ minutes}$.
- **Scrap Generation**: Degraded milling tolerances increase scrap probability from nominal $p_{\text{scrap}} = 0.015$ to degraded $p_{\text{scrap, deg}} = 0.080$:
  $$N_{\text{scrap}} \sim \text{Binomial}(N_{\text{batch}}, p_{\text{scrap}})$$
  $$N_{\text{completed}} = N_{\text{batch}} - N_{\text{scrap}}$$

---

## 4. Disaggregated Financial Loss Accounting (INR)

For every operational deviation or stoppage event, financial losses are calculated deterministically:

$$\text{Loss}_{\text{Total}} = \text{Loss}_{\text{Downtime}} + \text{Loss}_{\text{Scrap}} + \text{Loss}_{\text{Rework}} + \text{Loss}_{\text{Energy}}$$

### Financial Cost Components:
1. **Downtime Loss**:
   $$\text{Loss}_{\text{Downtime}} = \left(\frac{t_{\text{downtime\_min}}}{60}\right) \times R_{\text{downtime}}$$
   - Auto-Components: $R_{\text{downtime}} = ₹4,500/\text{hr}$
   - Textile MSME: $R_{\text{downtime}} = ₹3,800/\text{hr}$

2. **Scrap Loss**:
   $$\text{Loss}_{\text{Scrap}} = \left(N_{\text{scrap}} \times w_{\text{unit\_kg}}\right) \times R_{\text{scrap}}$$
   - Auto-Components: $w = 0.8\text{ kg/part}, R_{\text{scrap}} = ₹350/\text{kg}$
   - Textile: $w = 0.8\text{ kg/bobbin}, R_{\text{scrap}} = ₹280/\text{kg}$

3. **Technician Rework Loss**:
   $$\text{Loss}_{\text{Rework}} = h_{\text{rework}} \times R_{\text{rework}}$$
   - Auto-Components: $R_{\text{rework}} = ₹280/\text{hr}$
   - Textile: $R_{\text{rework}} = ₹220/\text{hr}$

4. **Time-of-Day (ToD) Peak Electricity Surcharge**:
   If job completion slips into the peak tariff window ($18:00 \le h < 22:00$):
   $$\text{Loss}_{\text{Energy}} = P_{\text{active}} \times t_{\text{duration\_hr}} \times (R_{\text{peak}} - R_{\text{base}})$$
   - Base Tariff: $R_{\text{base}} = ₹8.50/\text{kWh}$
   - Peak Tariff: $R_{\text{peak}} = ₹12.50/\text{kWh}$
   - Surcharge: $\Delta R = ₹4.00/\text{kWh}$

---

## 5. Summary Table: Empirical Baseline vs Synthetic Simulation

| Parameter | Discrete Auto-Components (Dataset 10) | Textile MSME (Dataset 09) |
| :--- | :--- | :--- |
| **Primary Line ID** | `LINE_01` (5 machines) | `TX_LINE_01` (5 machines) |
| **Critical Machine** | `M2` (VMC Milling Center) | `TX02` (Ring Spinning Frame) |
| **Degradation Episode** | Days 18 to 21 (Spindle bearing wear) | Days 16 to 19 (Spindle bolster lint friction) |
| **Baseline $\to$ Peak Vib** | $1.4\text{ mm/s} \to 5.6\text{ mm/s}$ | $1.3\text{ mm/s} \to 5.4\text{ mm/s}$ |
| **Nominal $\to$ Degraded Cycle** | $45.0\text{ s} \to 58.0\text{--}65.0\text{ s}$ | $40.0\text{ s} \to 55.0\text{ s}$ |
| **Emergency Halt** | Day 21 (150 min downtime, ₹11,670 loss) | Day 19 (120 min downtime, ₹7,930 loss) |
| **Inventory Alert** | `SKU_SPINDLE_BEARING_M2` drops to 1 (safety 3) | `TX_SKU_RING_SPINDLE_BOLSTER` drops to 1 (safety 4) |
| **Total Telemetry Rows** | 43,200 rows (CSV & Parquet) | 43,200 rows (CSV & Parquet) |
| **Total Jobs Simulated** | 300 batches | 300 batches |
