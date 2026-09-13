# Table 14: Methodological Limitations, Boundary Constraints, and Epistemic Status Audit

| Limitation Item | Epistemic Status | Impact | Mitigation / Policy |
| :--- | :--- | :--- | :--- |
| Controlled Synthetic Factory Scenario | CONTROLLED_SYNTHETIC | Degradation scenarios on M1-M5 are synthetic benchmarks and must not be cited as real physical plant validation. | Strictly demarcated as controlled synthetic evidence in all documentation. |
| PostgreSQL & Docker Infrastructure | ENVIRONMENTAL_CONSTRAINT | PostgreSQL daemon and Docker virtualization were unavailable on local workstation environment. | Fallback to SQLite and in-memory persistent FastAPI execution validated with 100% green tests. |
| Prospective Industrial Field Validation | NOT_EMPIRICALLY_VALIDATED | Models have not been deployed in a live operational industrial plant subject to raw human overrides. | Platform is documented strictly as decision support; human-in-the-loop verification is mandatory. |
| SHAP Physical Causality Caveat | MODEL_OUTPUT | SHAP attributes model prediction variance to input features but does not prove physical mechanism causality. | Always paired with engineering RCA hypotheses; never claimed as mechanical causation. |
| Cross-Sectional Industrial IoT RUL | CROSS_SECTIONAL_FLEET_SNAPSHOT | Dataset contains exactly 1 row per Machine_ID; zero longitudinal wear tracking exists per machine. | Documented as fleet snapshot regression; no longitudinal degradation claims made. |
| AI4I Epistemic Status Divergence | RECONCILED: REAL_PHYSICAL_SIMULATOR | Earlier report had single-instance textual reference to CONTROLLED_SYNTHETIC. | Authoritative metadata provenance confirmed as REAL_PHYSICAL_SIMULATOR per UCI specification. |
| IoT RUL 0.50-Day Threshold Provenance | COMPUTATIONAL_TUNING_HEURISTIC | The 0.50-day acceptance rule was a project tuning heuristic, not a prior external registry pre-registration. | Formally declared as project computational tuning acceptance rule. |
| Anomaly Score Raw Magnitude Non-Equivalence | METHODOLOGICAL_RULE | Raw anomaly score magnitudes cannot be compared across algorithms as accuracy. | Evaluated exclusively through pre-registered separation ratios (ADCR and MASI). |
