import React, { useState, useEffect } from "react";
import "../styles/Header.css";

export default function Header({ factoryInfo, kpis }) {
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="header-container" id="executive-header">
      <div className="header-left">
        <div className="brand-badge">
          <span className="brand-dot pulse"></span>
          <span className="brand-title">NIRMAAN AI</span>
          <span className="brand-version">v0.21.0</span>
        </div>
        <div className="factory-identity">
          <h1 className="factory-name">{factoryInfo.factory_name}</h1>
          <div className="factory-meta">
            <span className="meta-tag mono">FACILITY: {factoryInfo.factory_id}</span>
            <span className="meta-tag">{factoryInfo.location}</span>
            <span className="meta-tag badge badge-warning">CRITICAL ALERT (M2)</span>
          </div>
        </div>
      </div>

      <div className="header-right">
        <div className="telemetry-clock">
          <div className="clock-row">
            <span className="clock-label">LOCAL IST:</span>
            <span className="clock-value mono">{currentTime}</span>
          </div>
          <div className="clock-row">
            <span className="clock-label">DECISION CUTOFF:</span>
            <span className="cutoff-tag mono">2026-01-21 12:00 UTC</span>
          </div>
        </div>

        <div className="shift-card">
          <div className="shift-label">ACTIVE SHIFT</div>
          <div className="shift-val">{factoryInfo.active_shift.split(" ")[1]}</div>
          <div className="shift-status mono">
            {factoryInfo.is_live ? (
              <span className="live-pill active">LIVE BACKEND DATA</span>
            ) : (
              <span className="live-pill fallback">OFFLINE DEMO / FALLBACK DATA</span>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
