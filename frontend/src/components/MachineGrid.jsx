import React, { useState } from "react";
import MachineModal from "./MachineModal";
import "../styles/MachineGrid.css";

export default function MachineGrid({ machines }) {
  const [selectedMachine, setSelectedMachine] = useState(null);

  return (
    <section className="fleet-section" id="fleet-section">
      <div className="section-header">
        <div>
          <h2 className="section-title">Shop-Floor Fleet Intelligence</h2>
          <p className="section-subtitle">Real-time telemetry, predictive failure risk, and machine health scoring</p>
        </div>
        <div className="fleet-legend">
          <span className="legend-item"><span className="legend-dot healthy"></span> Nominal (4)</span>
          <span className="legend-item"><span className="legend-dot critical"></span> Critical (1)</span>
        </div>
      </div>

      <div className="machine-grid" id="machine-cards-grid">
        {machines.map((m) => {
          const isCritical = m.status === "CRITICAL";
          return (
            <div
              key={m.machine_id}
              id={`machine-card-${m.machine_id}`}
              className={`glass-card machine-card ${isCritical ? "critical-card" : "nominal-card"}`}
              onClick={() => setSelectedMachine(m)}
            >
              <div className="card-top">
                <div className="machine-ident">
                  <span className="machine-id-badge mono">{m.machine_id}</span>
                  <span className="machine-type-tag">{m.type}</span>
                </div>
                <span className={`badge ${isCritical ? "badge-critical" : "badge-healthy"}`}>
                  {m.status}
                </span>
              </div>

              <h3 className="machine-title">{m.name}</h3>

              <div className="health-visual">
                <div className="health-gauge">
                  <svg viewBox="0 0 100 100" className="gauge-svg">
                    <circle cx="50" cy="50" r="40" className="gauge-bg" />
                    <circle
                      cx="50"
                      cy="50"
                      r="40"
                      className={`gauge-bar ${isCritical ? "bar-critical" : "bar-healthy"}`}
                      strokeDasharray="251.2"
                      strokeDashoffset={251.2 - (251.2 * m.health_score) / 100}
                    />
                  </svg>
                  <div className="gauge-text">
                    <span className="gauge-number mono">{m.health_score.toFixed(1)}</span>
                    <span className="gauge-label">HEALTH</span>
                  </div>
                </div>

                <div className="risk-stats">
                  <div className="risk-row">
                    <span className="risk-label">Failure Risk:</span>
                    <span className={`risk-val mono ${isCritical ? "crimson" : "emerald"}`}>
                      {(m.failure_probability * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="risk-row">
                    <span className="risk-label">Anomaly Score:</span>
                    <span className={`risk-val mono ${m.anomaly_score > m.anomaly_threshold ? "crimson" : "emerald"}`}>
                      {m.anomaly_score.toFixed(3)}
                    </span>
                  </div>
                  <div className="risk-row">
                    <span className="risk-label">Bottleneck:</span>
                    <span className={`risk-val mono ${m.is_bottleneck ? "amber" : "text-muted"}`}>
                      {m.is_bottleneck ? "ACTIVE (1.38x)" : "NOMINAL"}
                    </span>
                  </div>
                </div>
              </div>

              <div className="sensor-strip">
                <div className="sensor-cell">
                  <span className="sensor-name">VIB</span>
                  <span className={`sensor-val mono ${m.vibration_mms > 2.5 ? "crimson" : ""}`}>{m.vibration_mms} mm/s</span>
                </div>
                <div className="sensor-cell">
                  <span className="sensor-name">TEMP</span>
                  <span className={`sensor-val mono ${m.temperature_c > 75 ? "crimson" : ""}`}>{m.temperature_c}°C</span>
                </div>
                <div className="sensor-cell">
                  <span className="sensor-name">POWER</span>
                  <span className="sensor-val mono">{m.power_kw} kW</span>
                </div>
                <div className="sensor-cell">
                  <span className="sensor-name">TOOL</span>
                  <span className="sensor-val mono">{m.tool_wear_min} m</span>
                </div>
              </div>

              <div className="card-action">
                <span className="inspect-link">Detailed Diagnostics &amp; RCA →</span>
              </div>
            </div>
          );
        })}
      </div>

      {selectedMachine && (
        <MachineModal
          machine={selectedMachine}
          onClose={() => setSelectedMachine(null)}
        />
      )}
    </section>
  );
}
