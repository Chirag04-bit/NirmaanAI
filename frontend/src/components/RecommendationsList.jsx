import React from "react";

export default function RecommendationsList({ recommendations }) {
  return (
    <section className="recommendations-section" id="recommendations-section">
      <div className="section-header">
        <div>
          <h2 className="section-title">Prescriptive Decision Directives</h2>
          <p className="section-subtitle">Operational action rules triggered under Phase 15 multi-criteria engine</p>
        </div>
        <span className="badge badge-epistemic">PHASE 15 DECISION ENGINE</span>
      </div>

      <div className="recommendations-grid" style={{ display: "grid", gap: "16px" }}>
        {recommendations.map((rec) => {
          const isCritical = rec.priority === "CRITICAL";

          return (
            <div
              key={rec.rule_id}
              id={`rec-card-${rec.rule_id}`}
              className={`glass-card ${isCritical ? "critical-card" : ""}`}
              style={{ padding: "18px 22px" }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <span className="badge badge-epistemic mono">{rec.rule_id}</span>
                  <span className="badge badge-epistemic mono">{rec.machine_id}</span>
                  <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: 600 }}>{rec.category}</span>
                </div>
                <div style={{ display: "flex", gap: "8px" }}>
                  <span className={`badge ${isCritical ? "badge-critical" : "badge-warning"}`}>{rec.priority}</span>
                  <span className="badge badge-info">{rec.urgency}</span>
                </div>
              </div>

              <div style={{ display: "flex", alignItems: "baseline", gap: "12px", marginBottom: "10px" }}>
                <h3 className="mono" style={{ fontSize: "17px", color: isCritical ? "#fca5a5" : "var(--cyan)" }}>
                  {rec.action}
                </h3>
              </div>

              <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginBottom: "10px", lineHeight: "1.4" }}>
                <strong>Trigger Antecedent:</strong> {rec.reason}
              </p>

              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", paddingTop: "10px", borderTop: "1px solid var(--border-subtle)", fontSize: "12px" }}>
                <span style={{ color: "var(--text-muted)" }}>
                  <strong>Operational Effect:</strong> {rec.impact}
                </span>
                <span className="badge badge-epistemic">{rec.epistemic_status}</span>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
