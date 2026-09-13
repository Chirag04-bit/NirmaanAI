import React, { useState, useEffect } from "react";
import Header from "./components/Header";
import Navigation from "./components/Navigation";
import KpiCards from "./components/KpiCards";
import MachineGrid from "./components/MachineGrid";
import InventoryTable from "./components/InventoryTable";
import SimulationStudio from "./components/SimulationStudio";
import RecommendationsList from "./components/RecommendationsList";
import CopilotChat from "./components/CopilotChat";

import {
  fetchFactoryInfo,
  fetchKpis,
  fetchMachines,
  fetchInventory,
  fetchSimulations,
  fetchRecommendations,
} from "./api/client";

import {
  MOCK_FACTORY_INFO,
  MOCK_KPIS,
  MOCK_MACHINES,
  MOCK_INVENTORY,
  MOCK_SIMULATION_SCENARIOS,
  MOCK_RECOMMENDATIONS,
} from "./api/mockData";

export default function App() {
  const [activeTab, setActiveTab] = useState("overview");
  const [factoryInfo, setFactoryInfo] = useState(MOCK_FACTORY_INFO);
  const [kpis, setKpis] = useState(MOCK_KPIS);
  const [machines, setMachines] = useState(MOCK_MACHINES);
  const [inventory, setInventory] = useState(MOCK_INVENTORY);
  const [scenarios, setScenarios] = useState(MOCK_SIMULATION_SCENARIOS);
  const [recommendations, setRecommendations] = useState(MOCK_RECOMMENDATIONS);

  useEffect(() => {
    async function loadData() {
      const [fInfo, kpiData, machData, invData, scenData, recData] = await Promise.all([
        fetchFactoryInfo(),
        fetchKpis(),
        fetchMachines(),
        fetchInventory(),
        fetchSimulations(),
        fetchRecommendations(),
      ]);
      setFactoryInfo(fInfo);
      setKpis(kpiData);
      setMachines(machData);
      setInventory(invData);
      setScenarios(scenData);
      setRecommendations(recData);
    }
    loadData();
  }, []);

  return (
    <div className="app-wrapper" id="nirmaanai-dashboard">
      <Header factoryInfo={factoryInfo} kpis={kpis} />
      <Navigation activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="main-content">
        {/* Executive KPI Header visible on Overview and Fleet */}
        {(activeTab === "overview" || activeTab === "fleet") && (
          <KpiCards kpis={kpis} onSelectTab={setActiveTab} />
        )}

        {/* Tab 1: Overview */}
        {activeTab === "overview" && (
          <div className="overview-view">
            <MachineGrid machines={machines} />
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginTop: "24px" }}>
              <RecommendationsList recommendations={recommendations} />
              <div className="glass-card" style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                    <h3 style={{ fontSize: "16px" }}>AI Factory Copilot Assistant</h3>
                    <span className="badge badge-info">RAG GROUNDED</span>
                  </div>
                  <p style={{ fontSize: "13px", color: "var(--text-secondary)", lineHeight: "1.5", marginBottom: "16px" }}>
                    Access natural-language decision support for machine failure risk, root causes, inventory replenishment, and financial loss quantization grounded in Phase 3–20 evidence.
                  </p>
                  <div className="badge badge-warning" style={{ marginBottom: "16px" }}>
                    Primary Alert: Machine M2 Mechanical Seizure Preemption
                  </div>
                </div>
                <button
                  id="open-copilot-btn"
                  className="btn btn-primary"
                  style={{ width: "100%" }}
                  onClick={() => setActiveTab("copilot")}
                >
                  Launch Full Copilot Chat Studio →
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Fleet Intelligence */}
        {activeTab === "fleet" && <MachineGrid machines={machines} />}

        {/* Tab 3: Diagnostics & RCA */}
        {activeTab === "diagnostics" && (
          <div>
            <div className="section-header">
              <div>
                <h2 className="section-title">Diagnostic Deep-Dive &amp; Root Cause Analysis</h2>
                <p className="section-subtitle">Select any machine asset to inspect telemetry, SHAP attributions, and fault trees</p>
              </div>
              <span className="badge badge-epistemic">PHASE 11 &amp; PHASE 12 XAI</span>
            </div>
            <MachineGrid machines={machines} />
          </div>
        )}

        {/* Tab 4: Spare Inventory */}
        {activeTab === "inventory" && <InventoryTable inventory={inventory} />}

        {/* Tab 5: What-If Simulator */}
        {activeTab === "simulation" && <SimulationStudio scenarios={scenarios} />}

        {/* Tab 6: Prescriptions */}
        {activeTab === "recommendations" && <RecommendationsList recommendations={recommendations} />}

        {/* Tab 7: Grounded Copilot */}
        {activeTab === "copilot" && <CopilotChat />}
      </main>

      {/* Academic / MSME Footer */}
      <footer style={{
        padding: "20px 28px",
        borderTop: "1px solid var(--border-subtle)",
        background: "rgba(10, 15, 28, 0.9)",
        fontSize: "12px",
        color: "var(--text-muted)",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexWrap: "wrap",
        gap: "12px"
      }}>
        <div>
          <strong>NirmaanAI</strong> — Digital Factory Brain for Indian MSMEs | Institute of Engineering &amp; Management (IEM), Kolkata
        </div>
        <div style={{ display: "flex", gap: "16px" }}>
          <span>Project Group: 59</span>
          <span>Project Guide: <strong>Prof. Kuntal Mondal</strong></span>
          <span>Dept of CSE (Artificial Intelligence)</span>
        </div>
      </footer>
    </div>
  );
}
