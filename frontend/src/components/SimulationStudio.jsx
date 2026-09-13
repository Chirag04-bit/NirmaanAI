import React, { useState } from "react";
import "../styles/Simulation.css";

export default function SimulationStudio({ scenarios }) {
  const [selectedId, setSelectedId] = useState("SCEN_M2_D_FLOW_MITIGATION");

  const selectedScenario = scenarios.find((s) => s.scenario_id === selectedId) || scenarios[0];

  const formatInr = (val) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 2,
    }).format(val);
  };

  return (
    <section className="simulation-section" id="simulation-section">
      <div className="section-header">
        <div>
          <h2 className="section-title">Digital-Twin What-If Simulation Studio</h2>
          <p className="section-subtitle">Comparative counterfactual scenario evaluation for Machine M2</p>
        </div>
        <span className="badge badge-epistemic">PHASE 16 MONTE CARLO</span>
      </div>

      <div className="simulation-layout">
        {/* Left: Interactive Scenario Selector Table */}
        <div className="glass-card scenario-selector-card">
          <h3 className="card-heading">Evaluated Intervention Scenarios</h3>
          <div className="scenarios-list">
            {scenarios.map((scen) => {
              const isSelected = scen.scenario_id === selectedId;
              const isOptimal = scen.scenario_id === "SCEN_M2_D_FLOW_MITIGATION";

              return (
                <div
                  key={scen.scenario_id}
                  id={`scenario-item-${scen.scenario_id}`}
                  className={`scenario-item ${isSelected ? "selected" : ""}`}
                  onClick={() => setSelectedId(scen.scenario_id)}
                >
                  <div className="scenario-item-top">
                    <span className="scenario-item-name">{scen.name}</span>
                    {isOptimal && <span className="badge badge-healthy">RECOMMENDED OPTION</span>}
                  </div>
                  <div className="scenario-item-meta">
                    <span className="mono text-muted">{scen.interventions.join(", ")}</span>
                    <span className="scenario-avoided mono font-bold text-emerald">
                      +{formatInr(scen.avoided_loss_inr)}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Detailed Scenario Breakdown & Counterfactual Visual */}
        <div className="glass-card scenario-detail-card">
          <div className="detail-header">
            <div>
              <span className="badge badge-epistemic mono">{selectedScenario.scenario_id}</span>
              <h3 className="selected-scenario-title">{selectedScenario.name}</h3>
            </div>
            <span className="badge badge-info">{selectedScenario.epistemic_status}</span>
          </div>

          <div className="detail-metrics-strip">
            <div className="detail-metric">
              <span className="detail-lbl">Avoided Loss (INR):</span>
              <span className="detail-val mono text-emerald font-bold">
                {formatInr(selectedScenario.avoided_loss_inr)}
              </span>
            </div>
            <div className="detail-metric">
              <span className="detail-lbl">Remaining Gross Exposure:</span>
              <span className="detail-val mono crimson font-bold">
                {formatInr(selectedScenario.remaining_gross_exposure_inr)}
              </span>
            </div>
            <div className="detail-metric">
              <span className="detail-lbl">Post-Action Spare Stock:</span>
              <span className={`detail-val mono font-bold ${selectedScenario.projected_post_action_stock < 1.134 ? "amber" : "emerald"}`}>
                {selectedScenario.projected_post_action_stock.toFixed(1)} units
              </span>
            </div>
          </div>

          {/* Visual Comparison Progress Bars */}
          <div className="counterfactual-chart">
            <span className="chart-heading">Financial Exposure Mitigation Impact</span>
            
            <div className="bar-group">
              <div className="bar-label-row">
                <span>Baseline Gross Exposure (Scenario A):</span>
                <span className="mono crimson font-bold">{formatInr(97382.28)}</span>
              </div>
              <div className="chart-track">
                <div className="chart-bar baseline-bar" style={{ width: "100%" }}></div>
              </div>
            </div>

            <div className="bar-group">
              <div className="bar-label-row">
                <span>Selected Scenario Remaining Exposure:</span>
                <span className="mono text-cyan font-bold">{formatInr(selectedScenario.remaining_gross_exposure_inr)}</span>
              </div>
              <div className="chart-track">
                <div
                  className="chart-bar mitigated-bar"
                  style={{ width: `${(selectedScenario.remaining_gross_exposure_inr / 97382.28) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>

          <div className="scenario-assumptions-box">
            <h4 className="assumptions-title">Modeled Assumptions &amp; Causality</h4>
            <p className="assumptions-text">{selectedScenario.assumptions}</p>
          </div>

          <div className="epistemic-guardrail-notice">
            <span className="guardrail-icon">🛡️</span>
            <div className="guardrail-text">
              <strong>Strict Epistemic Guardrail:</strong> Counterfactual metrics like avoided breakdown and opportunity losses are mathematical projections ({selectedScenario.epistemic_status}). Diagnostic KPIs under intervention (failure probability, health score recovery) are explicitly marked <code>NOT_PROJECTABLE</code> without empirical post-intervention treatment telemetry.
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
