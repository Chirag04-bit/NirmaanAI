import React from "react";
import "../styles/Diagnostics.css";

export default function MachineModal({ machine, onClose }) {
  if (!machine) return null;

  const isCritical = machine.status === "CRITICAL";

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content glass-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-group">
            <span className="badge badge-epistemic mono">{machine.machine_id}</span>
            <h2 className="modal-machine-name">{machine.name}</h2>
            <span className={`badge ${isCritical ? "badge-critical" : "badge-healthy"}`}>
              {machine.status}
            </span>
          </div>
          <button className="modal-close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          {/* Top Quick Status Bar */}
          <div className="status-banner">
            <div className="banner-item">
              <span className="banner-label">FACTORY HEALTH SCORE</span>
              <span className={`banner-val mono ${isCritical ? "crimson" : "emerald"}`}>
                {machine.health_score.toFixed(2)} / 100
              </span>
            </div>
            <div className="banner-item">
              <span className="banner-label">PREDICTIVE FAILURE RISK</span>
              <span className={`banner-val mono ${isCritical ? "crimson" : "emerald"}`}>
                {(machine.failure_probability * 100).toFixed(2)}%
              </span>
            </div>
            <div className="banner-item">
              <span className="banner-label">PCA ANOMALY ERROR</span>
              <span className={`banner-val mono ${machine.anomaly_score > machine.anomaly_threshold ? "crimson" : "emerald"}`}>
                {machine.anomaly_score.toFixed(4)} (thresh: {machine.anomaly_threshold})
              </span>
            </div>
            <div className="banner-item">
              <span className="banner-label">BOTTLENECK STATUS</span>
              <span className={`banner-val mono ${machine.is_bottleneck ? "amber" : "text-muted"}`}>
                {machine.is_bottleneck ? `ACTIVE (${machine.cycle_ratio}x)` : "NOMINAL"}
              </span>
            </div>
          </div>

          {/* Diagnostics Grid */}
          <div className="diag-grid">
            {/* Left: SHAP Explainability Waterfall */}
            <div className="diag-card shap-section">
              <div className="diag-card-header">
                <h3>Phase 11: SHAP Feature Importance</h3>
                <span className="badge badge-epistemic">STATISTICAL XAI</span>
              </div>
              <p className="diag-card-desc">Local feature attributions for elevated mechanical failure risk:</p>

              {machine.shap_top_features ? (
                <div className="shap-list">
                  {machine.shap_top_features.map((feat, idx) => (
                    <div key={idx} className="shap-row">
                      <div className="shap-row-info">
                        <span className="shap-name mono">{feat.feature}</span>
                        <span className="shap-attribution mono crimson">{feat.attribution}</span>
                      </div>
                      <div className="shap-bar-track">
                        <div
                          className="shap-bar-fill"
                          style={{ width: `${Math.abs(parseFloat(feat.attribution)) * 100 * 1.8}%` }}
                        ></div>
                      </div>
                      <span className="shap-desc">{feat.interpretation}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <span>Machine operates within nominal baseline envelope. No positive risk features detected.</span>
                </div>
              )}
            </div>

            {/* Right: Root Cause Analysis (Phase 12) & Telemetry */}
            <div className="diag-card rca-section">
              <div className="diag-card-header">
                <h3>Phase 12: Root Cause Analysis</h3>
                <span className="badge badge-epistemic">DIAGNOSTIC RCA</span>
              </div>
              <p className="diag-card-desc">Fault tree classification from sensor symptom signatures:</p>

              <div className="rca-diagnostic-box">
                <div className="rca-row">
                  <span className="rca-field">Primary Candidate Cause:</span>
                  <span className={`rca-result mono ${isCritical ? "crimson" : "emerald"}`}>
                    {machine.rca_status}
                  </span>
                </div>
                {machine.rca_details && (
                  <p className="rca-explanation">{machine.rca_details}</p>
                )}
              </div>

              <div className="prescribed-box">
                <span className="prescribe-title">Prescribed Intervention (Phase 15):</span>
                <div className="prescribe-action mono">
                  {machine.primary_recommendation}
                </div>
                {machine.recommendation_urgency && (
                  <span className="badge badge-critical mt-2">URGENCY: {machine.recommendation_urgency}</span>
                )}
              </div>

              <div className="live-sensors-table">
                <span className="sensors-table-title">Real-time Telemetry Baseline</span>
                <div className="sensors-grid">
                  <div className="sensor-box">
                    <span className="sensor-lbl">Spindle Vibration</span>
                    <span className={`sensor-num mono ${machine.vibration_mms > 2.5 ? "crimson" : ""}`}>{machine.vibration_mms} mm/s</span>
                  </div>
                  <div className="sensor-box">
                    <span className="sensor-lbl">Process Temperature</span>
                    <span className={`sensor-num mono ${machine.temperature_c > 75 ? "crimson" : ""}`}>{machine.temperature_c} °C</span>
                  </div>
                  <div className="sensor-box">
                    <span className="sensor-lbl">Active Power Load</span>
                    <span className="sensor-num mono">{machine.power_kw} kW</span>
                  </div>
                  <div className="sensor-box">
                    <span className="sensor-lbl">Accumulated Tool Wear</span>
                    <span className="sensor-num mono">{machine.tool_wear_min} min</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
