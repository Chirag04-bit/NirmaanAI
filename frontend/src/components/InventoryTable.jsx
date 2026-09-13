import React, { useState } from "react";
import "../styles/Inventory.css";

export default function InventoryTable({ inventory }) {
  const [expeditedSkus, setExpeditedSkus] = useState({});

  const handleExpedite = (skuId) => {
    setExpeditedSkus((prev) => ({
      ...prev,
      [skuId]: true,
    }));
  };

  const formatInr = (val) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(val);
  };

  return (
    <section className="inventory-section" id="inventory-section">
      <div className="section-header">
        <div>
          <h2 className="section-title">Smart Inventory &amp; Critical Spares Intelligence</h2>
          <p className="section-subtitle">Buffer protection, supplier lead time horizons, and proactive reorder alerts</p>
        </div>
        <span className="badge badge-epistemic">PHASE 10 INVENTORY OPTIMIZER</span>
      </div>

      <div className="glass-card inventory-card">
        <div className="table-responsive">
          <table className="inventory-table">
            <thead>
              <tr>
                <th>SKU IDENTIFIER</th>
                <th>DESCRIPTION</th>
                <th>TARGET</th>
                <th>ON-HAND</th>
                <th>SAFETY BUFFER</th>
                <th>POST-ACTION PROJ.</th>
                <th>LEAD TIME</th>
                <th>UNIT COST</th>
                <th>STATUS &amp; ACTION</th>
              </tr>
            </thead>
            <tbody>
              {inventory.map((item) => {
                const isBreached = item.is_safety_stock_breached;
                const isExpedited = expeditedSkus[item.sku_id];

                return (
                  <tr key={item.sku_id} className={isBreached ? "row-breached" : ""}>
                    <td className="mono font-bold text-cyan">{item.sku_id}</td>
                    <td className="font-semibold text-primary">{item.name}</td>
                    <td>
                      <span className="badge badge-epistemic mono">{item.target_machine}</span>
                    </td>
                    <td className="mono font-bold">{item.observed_stock.toFixed(1)}</td>
                    <td className="mono text-muted">{item.safety_stock.toFixed(3)}</td>
                    <td className="mono">
                      <span className={isBreached ? "crimson font-bold" : "text-primary"}>
                        {item.projected_post_action_stock.toFixed(1)}
                      </span>
                      {isBreached && <span className="breach-tag"> &lt; 1.134</span>}
                    </td>
                    <td className="mono">{item.supplier_lead_time_days.toFixed(1)} d</td>
                    <td className="mono">{formatInr(item.unit_cost_inr)}</td>
                    <td>
                      {isBreached ? (
                        isExpedited ? (
                          <span className="badge badge-healthy">PO EXPEDITED (12 QTY)</span>
                        ) : (
                          <button
                            id={`expedite-btn-${item.sku_id}`}
                            className="btn btn-primary btn-sm"
                            onClick={() => handleExpedite(item.sku_id)}
                          >
                            ⚡ Expedite Spare (Rule R-I01)
                          </button>
                        )
                      ) : (
                        <span className="badge badge-healthy">BUFFER SAFE</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="inventory-summary-footer">
          <div className="footer-callout">
            <span className="callout-icon">⚠️</span>
            <div className="callout-text">
              <strong>Buffer Depletion Warning:</strong> Executing the recommended spindle overhaul on Machine M2 consumes 1.0 unit of <code>SKU_SPINDLE_BEARING_M2</code>. Post-maintenance stock drops to 1.0 unit below the safety threshold (1.134 units). Supplier lead time is 7 days. Expedited purchase order required immediately.
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
