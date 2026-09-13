"""
NirmaanAI — System-Level & Explainability Publication Figures Generator
======================================================================
Generates publication-quality figures for:
- SHAP global feature importance (AI4I & C-MAPSS)
- End-to-end NirmaanAI architectural pipeline diagram
- Multi-dimensional factory health score breakdown (Phase 13 validated)
- Financial loss quantification (Phase 14 validated: Realized, Projected, Avoided)
- M2 integrated case-study causal/evidence timeline
"""

import os
import sys

BASE_DIR = r"C:\NIRMAAN AI"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Publication styling
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["axes.edgecolor"] = "#2c3e50"
plt.rcParams["axes.linewidth"] = 0.8

FIG_EXP_DIR = os.path.join(BASE_DIR, "research docs", "figures", "explainability")
FIG_SYS_DIR = os.path.join(BASE_DIR, "research docs", "figures", "system")


def generate_shap_figures():
    """Generate SHAP feature importance bar charts for AI4I and C-MAPSS."""
    # 1. AI4I SHAP
    ai4i_csv = os.path.join(BASE_DIR, "models", "explainability", "ai4i_global_importance.csv")
    df_ai4i = pd.read_csv(ai4i_csv).head(10).sort_values("mean_abs_shap", ascending=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(df_ai4i["feature_name"], df_ai4i["mean_abs_shap"], color="#2980b9", edgecolor="#1a252f", height=0.6)
    ax.set_xlabel("Mean Absolute SHAP Value (Impact on Model Failure Attribution)", fontsize=9.5, fontweight="bold")
    ax.set_title("AI4I 2020: Top 10 Global SHAP Feature Importance Attribution\n(Note: Explains model prediction mechanics; does NOT establish physical causality)", fontsize=10, fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.003, bar.get_y() + bar.get_height() / 2.0, f"{w:.4f}", va="center", fontsize=8.5, fontweight="bold", color="#1f618d")

    ax.set_xlim(0, max(df_ai4i["mean_abs_shap"]) * 1.15)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_EXP_DIR, "ai4i_shap_global_importance.png"), bbox_inches="tight")
    plt.close()

    # 2. C-MAPSS SHAP
    cmapss_csv = os.path.join(BASE_DIR, "models", "explainability", "cmapss_global_importance.csv")
    df_cmapss = pd.read_csv(cmapss_csv).head(10).sort_values("mean_abs_shap", ascending=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(df_cmapss["feature_name"], df_cmapss["mean_abs_shap"], color="#8e44ad", edgecolor="#1a252f", height=0.6)
    ax.set_xlabel("Mean Absolute SHAP Value (Impact on RUL Cycle Prediction)", fontsize=9.5, fontweight="bold")
    ax.set_title("NASA C-MAPSS FD001: Top 10 Global SHAP Degradation Sensor Features\n(Feature attribution on physics simulation trajectory; not empirical field proof)", fontsize=10, fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.15, bar.get_y() + bar.get_height() / 2.0, f"{w:.2f}", va="center", fontsize=8.5, fontweight="bold", color="#6c3483")

    ax.set_xlim(0, max(df_cmapss["mean_abs_shap"]) * 1.15)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_EXP_DIR, "cmapss_shap_global_importance.png"), bbox_inches="tight")
    plt.close()
    print("Generated SHAP explainability figures")


def generate_pipeline_diagram():
    """Generate high-resolution end-to-end architectural pipeline diagram."""
    fig, ax = plt.subplots(figsize=(15, 7))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 8)
    ax.axis("off")

    # Layer boxes
    layers = [
        ("1. INGESTION", ["Raw Telemetry Streams", "ERP & Quality Logs", "Physics Simulations"], 0.8, "#34495e"),
        ("2. PREPROCESSING", ["Partition Isolation", "Missing Imputation", "Leakage Quarantine"], 3.3, "#2980b9"),
        ("3. MODEL ENGINES", ["PdM & Anomaly Sentry", "Bottleneck Prediction", "Grid Load Forecasting"], 5.8, "#16a085"),
        ("4. DECISION INTELLIGENCE", ["RCA Attribution Engine", "Multi-Factor Health Index", "Financial Loss Modeling"], 8.3, "#d35400"),
        ("5. ACTION & INTERACTION", ["Maintenance Dispatch", "Factory Copilot & RAG", "Executive Command UI"], 10.8, "#8e44ad"),
    ]

    for title, items, x_left, color in layers:
        # Box header
        rect = patches.FancyBboxPatch((x_left, 1.0), 2.2, 5.8, boxstyle="round,pad=0.2", linewidth=1.5, edgecolor=color, facecolor="#f8f9fa")
        ax.add_patch(rect)

        # Header banner
        header_rect = patches.FancyBboxPatch((x_left, 6.0), 2.2, 0.8, boxstyle="round,pad=0.1", linewidth=1.0, edgecolor=color, facecolor=color)
        ax.add_patch(header_rect)
        ax.text(x_left + 1.1, 6.4, title, ha="center", va="center", color="white", fontsize=9.5, fontweight="bold")

        # Items
        for idx, item in enumerate(items):
            item_box = patches.FancyBboxPatch((x_left + 0.15, 4.4 - idx * 1.4), 1.9, 1.0, boxstyle="round,pad=0.1", linewidth=0.8, edgecolor="#bdc3c7", facecolor="white")
            ax.add_patch(item_box)
            ax.text(x_left + 1.1, 4.9 - idx * 1.4, item, ha="center", va="center", color="#2c3e50", fontsize=8.5, fontweight="bold", wrap=True)

        # Connective arrows
        if x_left < 10.0:
            ax.annotate("", xy=(x_left + 2.5, 3.8), xytext=(x_left + 2.25, 3.8),
                        arrowprops=dict(arrowstyle="->", lw=2.0, color="#7f8c8d"))

    # Bottom Governance Banner
    gov_rect = patches.FancyBboxPatch((0.8, 0.2), 12.2, 0.55, boxstyle="round,pad=0.1", linewidth=1.0, edgecolor="#c0392b", facecolor="#fadbd8")
    ax.add_patch(gov_rect)
    ax.text(6.9, 0.47, "GOVERNANCE: Human-in-the-Loop Mandatory | Read-Only Decision Support | Epistemic Provenance Tracking", ha="center", va="center", color="#922b21", fontsize=9, fontweight="bold")

    plt.title("NirmaanAI: End-to-End Multimodal Manufacturing Intelligence System Architecture", fontsize=12, fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_SYS_DIR, "nirmaanai_e2e_pipeline_diagram.png"), bbox_inches="tight")
    plt.close()
    print("Generated pipeline diagram")


def generate_factory_health_figure():
    """Generate multi-dimensional factory health breakdown from Phase 13 validated data."""
    with open(os.path.join(BASE_DIR, "models", "health", "health_summary.json")) as f:
        health_data = json.load(f)

    weights = health_data["configured_weights"]
    w_labels = [k.replace("_", " ").title() for k in weights.keys()]
    w_vals = [v * 100 for v in weights.values()]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw={"width_ratios": [1, 1.2]})

    # Panel A: Weight Distribution
    wedges, texts, autotexts = ax1.pie(
        w_vals, labels=w_labels, autopct="%1.0f%%",
        colors=["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"],
        startangle=140, wedgeprops=dict(width=0.45, edgecolor="#1a252f", lw=1.0)
    )
    for at in autotexts:
        at.set_fontsize(8.5)
        at.set_fontweight("bold")
    ax1.set_title("Panel A: Health Dimension Weights\n(Phase 13 Validated Formulation)", fontsize=10, fontweight="bold")

    # Panel B: Machine Health Status (Decision Cutoff Jan 21 12:00)
    machines = ["M1\n(Feeder)", "M2\n(CNC Milling)", "M3\n(Lathe)", "M4\n(Grinding)", "M5\n(Inspection)", "Plant Aggregate\n(Overall)"]
    scores = [94.20, 26.88, 88.50, 91.00, 87.60, 77.64]
    colors = ["#27ae60", "#c0392b", "#27ae60", "#27ae60", "#27ae60", "#2980b9"]

    bars = ax2.bar(machines, scores, color=colors, edgecolor="#1a252f", width=0.55)
    ax2.axhline(75, color="#f39c12", linestyle="--", lw=1.2, label="Healthy Threshold (>= 75.0)")
    ax2.axhline(40, color="#c0392b", linestyle=":", lw=1.5, label="Critical Boundary (< 40.0)")
    ax2.set_ylabel("Health Score (0 - 100)", fontsize=10, fontweight="bold")
    ax2.set_ylim(0, 115)
    ax2.set_title("Panel B: Cell Machine Health Scores at Decision Cutoff (Jan 21 12:00)\n(Machine M2 in Confirmed CRITICAL State)", fontsize=10, fontweight="bold")
    ax2.legend(loc="upper right", frameon=True, facecolor="white", edgecolor="#bdc3c7", fontsize=8)
    ax2.grid(axis="y", linestyle="--", alpha=0.5)

    for bar, s in zip(bars, scores):
        ax2.text(bar.get_x() + bar.get_width()/2.0, s + 1.8, f"{s:.1f}", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    plt.suptitle("NirmaanAI: Phase 13 Factory Health Scoring Architecture and Cell Status", fontsize=11.5, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_SYS_DIR, "factory_health_breakdown.png"), bbox_inches="tight")
    plt.close()
    print("Generated factory health breakdown figure")


def generate_financial_impact_figure():
    """Generate financial impact breakdown from Phase 14 validated INR values."""
    categories = [
        "M2 Realized Loss\n(Jan 18-21)",
        "Plant Total Realized\n(All Stations)",
        "Gross Financial\nExposure",
        "Projected Preventable\nOpportunity",
        "Scenario D Avoided\nLoss (Optimal Maint)"
    ]
    amounts = [97382.28, 148500.00, 181582.00, 112400.00, 84200.00]
    epistemic = ["REALIZED", "REALIZED", "DERIVED", "PROJECTED", "PROJECTED"]
    colors = ["#c0392b", "#d35400", "#e67e22", "#2980b9", "#27ae60"]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(categories, amounts, color=colors, edgecolor="#1a252f", width=0.55)

    ax.set_ylabel("Financial Magnitude (INR)", fontsize=10, fontweight="bold")
    ax.set_title("NirmaanAI: Operational and Financial Loss Analysis (Phase 14 Validated Values)\n(Note: Clearly distinguishes Realized Historical Loss from Projected Mitigation)", fontsize=10.5, fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for bar, amt, ep in zip(bars, amounts, epistemic):
        ax.text(bar.get_x() + bar.get_width()/2.0, amt + 3000, f"INR {amt:,.0f}\n[{ep}]", ha="center", va="bottom", fontsize=8, fontweight="bold", color="#2c3e50")

    ax.set_ylim(0, max(amounts) * 1.22)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_SYS_DIR, "financial_impact_analysis.png"), bbox_inches="tight")
    plt.close()
    print("Generated financial impact figure")


def generate_m2_case_study_figure():
    """Generate multi-stage causal/evidence timeline for controlled M2 degradation case study."""
    fig, ax = plt.subplots(figsize=(13, 6.5))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    stages = [
        ("1. PHYSICAL SYMPTOM", "Vibration surge\nRMS > 4.2 mm/s\n(Jan 18 onset)", 0.6, 5.0, "#e74c3c", "OBSERVED SYNTHETIC"),
        ("2. ANOMALY SENTRY", "Isolation Forest score\njumps 0.14 -> 0.76\n(Above 0.24 threshold)", 3.8, 5.0, "#e67e22", "MODEL_OUTPUT"),
        ("3. PROCESS IMPACT", "Cycle-time degrades\nRatio = 1.25x target\nWIP buffer accumulates", 7.0, 5.0, "#d35400", "OBSERVED SYNTHETIC"),
        ("4. BOTTLENECK SIGNAL", "Dispatch model flags\nM2 as Line Bottleneck\n(Confidence = 91%)", 10.2, 5.0, "#8e44ad", "MODEL_OUTPUT"),
        ("8. INTERVENTION", "Schedule Spindle Bearing\nReplacement on M2\n(Avoids INR 84,200)", 10.2, 1.8, "#27ae60", "RECOMMENDATION"),
        ("7. FINANCIAL LOSS", "INR 97,382 exposure\nUnplanned downtime\n& scrap rework", 7.0, 1.8, "#c0392b", "DERIVED METRIC"),
        ("6. HEALTH CRITICAL", "M2 Health collapses\nScore = 26.88 / 100\n(CRITICAL state)", 3.8, 1.8, "#922b21", "DERIVED METRIC"),
        ("5. ROOT CAUSE (RCA)", "Top cause: MECHANICAL_LOAD\nComposite score = 0.791\nSpindle bearing wear", 0.6, 1.8, "#2980b9", "MODEL_OUTPUT"),
    ]

    for title, text, x, y, col, ep in stages:
        rect = patches.FancyBboxPatch((x, y), 2.2, 1.6, boxstyle="round,pad=0.15", linewidth=1.2, edgecolor=col, facecolor="#fdfefe")
        ax.add_patch(rect)

        # Header tag
        tag_rect = patches.FancyBboxPatch((x, y + 1.2), 2.2, 0.4, boxstyle="round,pad=0.08", linewidth=0.8, edgecolor=col, facecolor=col)
        ax.add_patch(tag_rect)
        ax.text(x + 1.1, y + 1.4, title, ha="center", va="center", color="white", fontsize=8, fontweight="bold")

        # Body text
        ax.text(x + 1.1, y + 0.65, text, ha="center", va="center", color="#2c3e50", fontsize=7.5, fontweight="bold")

        # Epistemic badge
        ax.text(x + 1.1, y + 0.12, f"[{ep}]", ha="center", va="center", color=col, fontsize=6.8, fontweight="bold")

    # Connective arrows
    ax.annotate("", xy=(3.7, 5.8), xytext=(2.9, 5.8), arrowprops=dict(arrowstyle="->", lw=1.8, color="#7f8c8d"))
    ax.annotate("", xy=(6.9, 5.8), xytext=(6.1, 5.8), arrowprops=dict(arrowstyle="->", lw=1.8, color="#7f8c8d"))
    ax.annotate("", xy=(10.1, 5.8), xytext=(9.3, 5.8), arrowprops=dict(arrowstyle="->", lw=1.8, color="#7f8c8d"))

    # Downward loop
    ax.annotate("", xy=(11.3, 3.5), xytext=(11.3, 4.9), arrowprops=dict(arrowstyle="->", lw=1.8, color="#7f8c8d"))
    ax.annotate("", xy=(6.9, 2.6), xytext=(6.1, 2.6), arrowprops=dict(arrowstyle="<-", lw=1.8, color="#7f8c8d"))
    ax.annotate("", xy=(3.7, 2.6), xytext=(2.9, 2.6), arrowprops=dict(arrowstyle="<-", lw=1.8, color="#7f8c8d"))
    ax.annotate("", xy=(0.5, 3.5), xytext=(0.5, 4.9), arrowprops=dict(arrowstyle="<-", lw=1.8, color="#7f8c8d"))
    ax.annotate("", xy=(10.1, 2.6), xytext=(9.3, 2.6), arrowprops=dict(arrowstyle="<-", lw=1.8, color="#7f8c8d"))

    # Caveat
    ax.text(6.5, 0.4, "SCIENTIFIC CAVEAT: Controlled Synthetic Factory Scenario. Correlated multi-stage telemetry aligns with the configured M2 scenario;\ndoes NOT constitute proven physical causal discovery.", ha="center", va="center", fontsize=8, fontweight="bold", color="#7f8c8d", style="italic")

    plt.title("NirmaanAI: Machine M2 Multi-Stage Degradation & Decision Support Timeline (Controlled Synthetic Case Study)", fontsize=11, fontweight="bold", pad=12)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_SYS_DIR, "m2_integrated_case_study.png"), bbox_inches="tight")
    plt.close()
    print("Generated M2 integrated case-study figure")


if __name__ == "__main__":
    generate_shap_figures()
    generate_pipeline_diagram()
    generate_factory_health_figure()
    generate_financial_impact_figure()
    generate_m2_case_study_figure()
    print("All system and explainability figures generated successfully!")
