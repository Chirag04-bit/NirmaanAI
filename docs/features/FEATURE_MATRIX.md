# NirmaanAI Feature Engineering Matrix

This matrix provides the dataset-by-dataset audit of raw inputs, domain-engineered features, pruned leakage attributes, and temporal features available for prospective decision intelligence.

| Dataset | Raw Features | Engineered Features | Final Features | Leakage Removed | Temporal Features |
|---|---:|---:|---:|---:|---:|
| **AI4I 2020** | 14 | 8 | 15 | 7 (`UDI`, `Product ID`, `TWF`, `HDF`, `PWF`, `OSF`, `RNF`) | 0 (Static snapshots) |
| **NASA C-MAPSS FD001** | 26 | 71 | 91 | 6 (`s1`, `s5`, `s10`, `s16`, `s18`, `s19` zero variance) | 71 (Causal rolling mean/std/max, baseline degradation delta) |
| **UCI SECOM** | 592 | 0 | 436 | 154 (28 missing $>50\%$, 126 constant/zero-variance channels) | 0 (In-line wafer snapshots) |
| **UCI Electricity (MT_124)** | 2 | 19 | 20 | 0 (Strict forward-leakage prevention) | 16 (Lags 1h–168h, 24h rolling stats, load differences) |
| **Industrial IoT 2040** | 22 | 7 | 27 | 2 (`Failure_Within_7_Days` / `Remaining_Useful_Life_days` cross-target isolation) | 0 (Aggregated telemetry snapshots) |
| **Manufacturing Production** | 13 | 12 | 12 (Prospective) + 8 (Diagnostic) | 4 (`realized_start_delay_min`, `realized_completion_delay_min`, `realized_cycle_ratio`, `Job_Status`) | 4 (Scheduled timestamps & shift indicators) |
| **Manufacturing Defects** | 17 | 7 | 23 | 1 (`DefectRate` flagged for review/conditional leakage) | 0 (Batch quality logs) |
| **Textile Manufacturing** | 13 | 6 | 19 | 0 (Marked `CONTROLLED_SYNTHETIC`) | 3 (Causal rolling mean & max per loom) |
| **Synthetic Factory (M1–M5)** | 13 | 10 | 23 | 2 (`MAINT_0003` emergency bearing failure, post-cutoff telemetry) | 4 (Station-grouped causal rolling stats) |
| **TOTALS / SYSTEM-WIDE** | **702** | **140** | **666** | **176** | **98** |

---

### Legend & Methodology
- **Raw Features**: Original sensor, operational, environmental, or metadata columns present in raw source datasets.
- **Engineered Features**: Scientifically justified derived metrics (e.g., thermodynamic gradients, electromechanical torque-speed interactions, ISO 10816 vibration severity ratios, fluid depletion indices, causal rolling statistics).
- **Final Features**: Kept, un-leaked feature set approved for downstream training.
- **Leakage Removed**: Directly quarantined columns to prevent 100% trivial target leakage, identifier memorization, uninformative zero-variance noise, or post-event contamination.
- **Temporal Features**: Causal lookback features computed strictly on past and current values ($t' \le t$).
