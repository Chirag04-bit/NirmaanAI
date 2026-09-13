import React from "react";
import "../styles/Navigation.css";

export default function Navigation({ activeTab, setActiveTab }) {
  const tabs = [
    { id: "overview", label: "Executive Overview", icon: "📊" },
    { id: "fleet", label: "Fleet Intelligence", icon: "⚙️", badge: "1 CRITICAL" },
    { id: "diagnostics", label: "Diagnostics & RCA", icon: "🔬" },
    { id: "inventory", label: "Spare Inventory", icon: "📦", badge: "BUFFER RISK" },
    { id: "simulation", label: "What-If Simulator", icon: "🔄" },
    { id: "recommendations", label: "Prescriptions", icon: "📋" },
    { id: "copilot", label: "Factory Copilot", icon: "🤖", badge: "RAG GROUNDED" },
  ];

  return (
    <nav className="nav-bar" id="main-navigation">
      <div className="nav-container">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            id={`nav-tab-${tab.id}`}
            className={`nav-tab ${activeTab === tab.id ? "active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="nav-icon">{tab.icon}</span>
            <span className="nav-label">{tab.label}</span>
            {tab.badge && (
              <span className={`nav-badge ${tab.id === "fleet" ? "badge-critical" : tab.id === "inventory" ? "badge-warning" : "badge-info"}`}>
                {tab.badge}
              </span>
            )}
          </button>
        ))}
      </div>
    </nav>
  );
}
