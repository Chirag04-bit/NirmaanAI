import React from "react";
import "../styles/KpiCards.css";

export default function KpiCards({ kpis, onSelectTab }) {
  const formatInr = (val) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 2,
    }).format(val);
  };

  return (
    <div className="kpi-grid" id="executive-kpi-grid">
      {/* 1. Factory Health Index */}
      <div className="glass-card kpi-card health-card" id="kpi-factory-health">
        <div className="kpi-header">
          <span className="kpi-title">PLANT HEALTH INDEX</span>
          <span className="badge badge-warning">1 CRITICAL ASSET</span>
        </div>
        <div className="kpi-body">
          <div className="kpi-metric-group">
            <span className="kpi-value mono">{kpis.factory_health_index.toFixed(1)}</span>
            <span className="kpi-unit">/ 100</span>
          </div>
          <div className="kpi-subtext">
            <span className="subtext-highlight crimson">Machine M2: 26.88/100</span> (CRITICAL)
          </div>
        </div>
        <div className="kpi-footer">
          <span className="badge badge-epistemic">PHASE 13 COMPOSITE</span>
          <button className="kpi-action-btn" onClick={() => onSelectTab("fleet")}>View Fleet →</button>
        </div>
      </div>

      {/* 2. Gross Financial Exposure */}
      <div className="glass-card kpi-card finance-card" id="kpi-gross-exposure">
        <div className="kpi-header">
          <span className="kpi-title">GROSS FINANCIAL EXPOSURE</span>
          <span className="badge badge-critical">ACTION REQUIRED</span>
        </div>
        <div className="kpi-body">
          <div className="kpi-metric-group">
            <span className="kpi-value mono">{formatInr(kpis.gross_exposure_inr)}</span>
          </div>
          <div className="kpi-breakdown">
            <div className="breakdown-item">
              <span className="item-label">Realized Loss:</span>
              <span className="item-val mono crimson">{formatInr(kpis.realized_loss_inr)}</span>
            </div>
            <div className="breakdown-item">
              <span className="item-label">Projected Opp.:</span>
              <span className="item-val mono amber">{formatInr(kpis.projected_opportunity_inr)}</span>
            </div>
          </div>
        </div>
        <div className="kpi-footer">
          <span className="badge badge-epistemic">PHASE 14 AUTHORITATIVE</span>
          <button className="kpi-action-btn" onClick={() => onSelectTab("simulation")}>Simulate →</button>
        </div>
      </div>

      {/* 3. Avoidable Opportunity Loss */}
      <div className="glass-card kpi-card simulation-card" id="kpi-avoidable-loss">
        <div className="kpi-header">
          <span className="kpi-title">AVOIDABLE VIA SCENARIO D</span>
          <span className="badge badge-healthy">FLOW MITIGATION</span>
        </div>
        <div className="kpi-body">
          <div className="kpi-metric-group">
            <span className="kpi-value mono text-emerald">{formatInr(kpis.avoidable_opportunity_inr)}</span>
          </div>
          <div className="kpi-subtext">
            Remaining Exposure: <span className="mono text-cyan">{formatInr(kpis.gross_exposure_inr - kpis.avoidable_opportunity_inr)}</span>
          </div>
        </div>
        <div className="kpi-footer">
          <span className="badge badge-epistemic">PHASE 16 DIGITAL TWIN</span>
          <button className="kpi-action-btn" onClick={() => onSelectTab("simulation")}>Review Scenarios →</button>
        </div>
      </div>

      {/* 4. Active Bottleneck Flow */}
      <div className="glass-card kpi-card bottleneck-card" id="kpi-active-bottleneck">
        <div className="kpi-header">
          <span className="kpi-title">ACTIVE FLOW CONSTRAINT</span>
          <span className="badge badge-warning">LINE STARVATION</span>
        </div>
        <div className="kpi-body">
          <div className="kpi-metric-group">
            <span className="kpi-value mono text-amber">MACHINE M2</span>
          </div>
          <div className="kpi-breakdown">
            <div className="breakdown-item">
              <span className="item-label">Cycle Ratio:</span>
              <span className="item-val mono crimson">1.38x (&gt;1.20)</span>
            </div>
            <div className="breakdown-item">
              <span className="item-label">Delayed Units:</span>
              <span className="item-val mono crimson">76 Units</span>
            </div>
          </div>
        </div>
        <div className="kpi-footer">
          <span className="badge badge-epistemic">PHASE 8 BOTTLENECK</span>
          <button className="kpi-action-btn" onClick={() => onSelectTab("recommendations")}>Mitigate →</button>
        </div>
      </div>
    </div>
  );
}
