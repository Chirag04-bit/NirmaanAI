# Table 12: End-to-End NirmaanAI System-Level Subsystem Metrics and Provenance

| Subsystem | Core Metric | Epistemic Status | Validated Artifact |
| :--- | :--- | :--- | :--- |
| Phase 6: Predictive Maintenance | ROC-AUC = 0.983 | Recall = 0.971 | MODEL_OUTPUT | models/predictive_maintenance/pdm_summary.json |
| Phase 7: Anomaly Detection | Threshold = 0.2405 | ADCR = 2.8024 | MODEL_OUTPUT | models/anomaly_detection/anomaly_summary.json |
| Phase 8: Bottleneck Dispatch | Cycle-Time Ratio = 1.25x | PR-AUC = 0.314 | MODEL_OUTPUT | models/bottleneck_prediction/bottleneck_summary.json |
| Phase 9: Energy Forecasting | WAPE = 6.27% | MAE = 18.78 kW | MODEL_OUTPUT | models/forecasting/forecasting_summary.json |
| Phase 10: Inventory Intelligence | Stockout Risk < 0.05 | Reorder Lead = 3.2d | DERIVED | models/inventory_intelligence/inventory_summary.json |
| Phase 11: Explainability (SHAP) | Top Attribution: tool_wear_min (0.182 SHAP) | MODEL_OUTPUT | models/explainability/metadata.json |
| Phase 12: Root Cause Analysis (RCA) | Composite Score = 0.791 | Top Cause: MECHANICAL_LOAD | DERIVED | models/rca/rca_summary.json |
| Phase 13: Factory Health Index | Plant Health = 78.4 / 100 | M2 Status: CRITICAL (26.88) | DERIVED | models/health/health_summary.json |
| Phase 14: Financial Loss Quantification | Realized: INR 1,48,500 | M2 Exposure: INR 97,382 | Scenario D Avoided: INR 84,200 | DERIVED / PROJECTED | models/loss/loss_summary.json |
| Phase 15: Recommendations | Human-in-the-Loop Mandatory | Decision Support Only | DERIVED | models/recommendations/recommendation_summary.json |
| Phase 16: Discrete-Event Simulation | Capacity Utilization = 84.2% | Bottleneck Shift Resolved | CONTROLLED_SYNTHETIC | models/simulation/simulation_summary.json |
| Phase 20-21: Factory Copilot & RAG | Positive Evaluation = 100% (9/9 passed) | Retrieval Latency = 26.7 ms | MODEL_OUTPUT | models/copilot/copilot_evaluation.json |
