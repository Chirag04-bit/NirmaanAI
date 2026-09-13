"""
NirmaanAI — Dataset and Preprocessing Publication Figures Generator
==================================================================
Generates high-resolution publication-quality figures for:
- Classification class distributions
- Regression target distributions (histograms + boxplots)
- Dataset training size comparisons
- Preprocessing tuning subset reduction
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Configure matplotlib publication styling
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["axes.edgecolor"] = "#2c3e50"
plt.rcParams["axes.linewidth"] = 0.8

BASE_DIR = r"C:\NIRMAAN AI"
FIG_DATASET_DIR = os.path.join(BASE_DIR, "research docs", "figures", "dataset")
FIG_PREPROC_DIR = os.path.join(BASE_DIR, "research docs", "figures", "preprocessing")
DATA_STAT_DIR = os.path.join(BASE_DIR, "research docs", "data", "dataset_statistics")


def generate_classification_class_distributions():
    """Publication figure showing class imbalance across all 5 classification tasks."""
    tasks = [
        ("AI4I 2020\n(Machine Failure)", "models/processed/ai4i/train.parquet", "machine_failure", ["Nominal (0)", "Failure (1)"], ["#2980b9", "#e74c3c"]),
        ("UCI SECOM\n(Wafer Defect)", "models/processed/secom/train.parquet", "target_defect", ["Pass (0)", "Defect (1)"], ["#27ae60", "#e67e22"]),
        ("Industrial IoT\n(7-Day Failure)", "models/processed/industrial_iot/failure/train.parquet", "Failure_Within_7_Days", ["Normal (0)", "Failure (1)"], ["#16a085", "#c0392b"]),
        ("Manufacturing Prod\n(Bottleneck)", "models/processed/manufacturing_production/train.parquet", "target_is_bottleneck", ["Standard (0)", "Bottleneck (1)"], ["#8e44ad", "#d35400"]),
        ("Manufacturing Defects\n(Quality Control)", "models/processed/manufacturing_defects/train.parquet", "DefectStatus", ["Clean (0)", "Defect (1)"], ["#34495e", "#e74c3c"])
    ]

    fig, axes = plt.subplots(1, 5, figsize=(18, 4.5))

    for idx, (title, path, target_col, class_names, colors) in enumerate(tasks):
        ax = axes[idx]
        df = pd.read_parquet(os.path.join(BASE_DIR, path))
        counts = df[target_col].value_counts().sort_index()
        total = len(df)
        props = counts / total * 100.0

        bars = ax.bar([0, 1], counts, color=colors, width=0.55, edgecolor="#1a252f", linewidth=1.0)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(class_names, fontsize=9, fontweight="bold")
        ax.set_title(title, fontsize=10, fontweight="bold", pad=8)
        ax.set_ylabel("Observation Count" if idx == 0 else "", fontsize=9)
        ax.grid(axis="y", linestyle="--", alpha=0.5)

        # Annotate counts and percentages
        for bar, count, prop in zip(bars, counts, props):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + (max(counts) * 0.02),
                f"{count:,}\n({prop:.1f}%)",
                ha="center", va="bottom", fontsize=8, fontweight="bold", color="#2c3e50"
            )
        ax.set_ylim(0, max(counts) * 1.22)

    plt.suptitle("NirmaanAI: Class Imbalance Profiles Across 5 Industrial Classification Tasks (Training Sets)", fontsize=12, fontweight="bold", y=1.03)
    plt.tight_layout()

    out_png = os.path.join(FIG_DATASET_DIR, "classification_class_distributions.png")
    plt.savefig(out_png, bbox_inches="tight")
    plt.close()
    print("Saved:", out_png)


def generate_regression_target_distributions():
    """Histogram and boxplot distributions for C-MAPSS, IoT RUL, and Electricity."""
    regr_specs = [
        ("NASA C-MAPSS FD001", "models/processed/cmapss/train.parquet", "rul_clipped", "RUL (Cycles, Capped at 125)", "#2980b9", 125),
        ("Industrial IoT Fleet RUL", "models/processed/industrial_iot/rul/train.parquet", "Remaining_Useful_Life_days", "RUL (Days)", "#16a085", None),
        ("Electricity Consumption", "models/processed/electricity/train.parquet", "power_kw", "Active Power Demand (kW)", "#8e44ad", None)
    ]

    fig, axes = plt.subplots(2, 3, figsize=(15, 7.5), gridspec_kw={"height_ratios": [3, 1]})

    for idx, (title, path, col, xlabel, color, cap) in enumerate(regr_specs):
        df = pd.read_parquet(os.path.join(BASE_DIR, path))
        series = df[col].dropna()

        # Histogram (Row 0)
        ax_hist = axes[0, idx]
        n, bins, patches = ax_hist.hist(series, bins=35, color=color, alpha=0.8, edgecolor="#1a252f", linewidth=0.8)
        ax_hist.set_title(f"{title}\nMean: {series.mean():.1f} | Med: {series.median():.1f} | Std: {series.std():.1f}", fontsize=10, fontweight="bold")
        ax_hist.set_ylabel("Frequency" if idx == 0 else "", fontsize=9)
        ax_hist.grid(axis="y", linestyle="--", alpha=0.5)

        # Boxplot (Row 1)
        ax_box = axes[1, idx]
        ax_box.boxplot(series, vert=False, patch_artist=True, boxprops=dict(facecolor=color, alpha=0.7), medianprops=dict(color="#c0392b", linewidth=1.5), whiskerprops=dict(linewidth=1.0), capprops=dict(linewidth=1.0), flierprops=dict(marker=".", markersize=3, alpha=0.3))
        ax_box.set_xlabel(xlabel, fontsize=9, fontweight="bold")
        ax_box.set_yticks([])
        ax_box.grid(axis="x", linestyle="--", alpha=0.5)

    plt.suptitle("NirmaanAI: Target Variable Distributions for Continuous Industrial Regression Tasks", fontsize=12, fontweight="bold", y=1.02)
    plt.tight_layout()

    out_png = os.path.join(FIG_DATASET_DIR, "regression_target_distributions.png")
    plt.savefig(out_png, bbox_inches="tight")
    plt.close()
    print("Saved:", out_png)


def generate_dataset_size_comparison():
    """Bar chart showing training set rows across all 10 datasets."""
    datasets = [
        ("Manufacturing Prod", 700, "Observational Log"),
        ("UCI SECOM", 1096, "Real Sensor Telemetry"),
        ("Manufacturing Defects", 2268, "Quality Metrology"),
        ("AI4I 2020", 7000, "Physical Milling Simulator"),
        ("NASA C-MAPSS", 14130, "Turbofan Simulation"),
        ("Electricity Load", 18279, "Industrial Grid Telemetry"),
        ("Synthetic Factory", 20415, "Multi-Station Simulator"),
        ("Textile Weaving", 30240, "Loom Telemetry Stream"),
        ("Industrial IoT Failure", 350000, "Large Fleet Simulator"),
        ("Industrial IoT RUL", 350000, "Large Fleet Simulator")
    ]

    names = [d[0] for d in datasets]
    rows = [d[1] for d in datasets]

    fig, ax = plt.subplots(figsize=(12, 5.5))
    colors = ["#3498db" if r < 50000 else "#e74c3c" for r in rows]
    bars = ax.barh(names, rows, color=colors, edgecolor="#1a252f", linewidth=0.8, height=0.6)

    ax.set_xscale("log")
    ax.set_xlabel("Training Rows (Log Scale)", fontsize=10, fontweight="bold")
    ax.set_title("NirmaanAI: Cross-Dataset Training Partition Scales (Logarithmic Scale)", fontsize=11, fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    for bar, val in zip(bars, rows):
        w = bar.get_width()
        ax.text(w * 1.15, bar.get_y() + bar.get_height() / 2.0, f"{val:,} rows", ha="left", va="center", fontsize=8.5, fontweight="bold")

    ax.set_xlim(200, 1500000)
    plt.tight_layout()

    out_png = os.path.join(FIG_DATASET_DIR, "dataset_size_comparison.png")
    plt.savefig(out_png, bbox_inches="tight")
    plt.close()
    print("Saved:", out_png)


def generate_tuning_subset_reduction():
    """Bar chart and statistical table showing tuning subset reduction and retention."""
    with open(os.path.join(BASE_DIR, "models", "tuning_subsets", "tuning_subsets_manifest.json")) as f:
        manifest = json.load(f)

    subsets = manifest["optimized_datasets"]
    tasks = list(subsets.keys())
    full_rows = [subsets[t]["full_train_rows"] for t in tasks]
    sub_rows = [subsets[t]["subset_train_rows"] for t in tasks]
    ret_pct = [subsets[t]["retention_pct"] for t in tasks]

    # Plot
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(tasks))
    width = 0.35

    b1 = ax.bar(x - width/2, full_rows, width, label="Canonical Full Training Rows", color="#2c3e50", edgecolor="#1a252f")
    b2 = ax.bar(x + width/2, sub_rows, width, label="Computational Tuning Subset", color="#27ae60", edgecolor="#1a252f")

    ax.set_xticks(x)
    ax.set_xticklabels([t.replace("_", " ").title() for t in tasks], rotation=15, ha="right", fontsize=9, fontweight="bold")
    ax.set_ylabel("Observation Count (Rows)", fontsize=10, fontweight="bold")
    ax.set_title("NirmaanAI: Data Volume Optimization — Full Training vs Tuning Subsets", fontsize=11, fontweight="bold")
    ax.legend(frameon=True, facecolor="white", edgecolor="#bdc3c7")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for idx, (f_r, s_r, r_p) in enumerate(zip(full_rows, sub_rows, ret_pct)):
        ax.text(idx + width/2, s_r + (max(full_rows) * 0.02), f"{s_r:,}\n({r_p:.1f}%)", ha="center", va="bottom", fontsize=8, fontweight="bold", color="#196f3d")

    ax.set_ylim(0, max(full_rows) * 1.18)
    plt.tight_layout()

    out_png = os.path.join(FIG_PREPROC_DIR, "tuning_subset_reduction.png")
    plt.savefig(out_png, bbox_inches="tight")
    plt.close()
    print("Saved:", out_png)

    # Export statistical CSV
    stat_rows = []
    for t in tasks:
        stat_rows.append({
            "Dataset": t,
            "Full Training Rows": subsets[t]["full_train_rows"],
            "Tuning Subset Rows": subsets[t]["subset_train_rows"],
            "Absolute Reduction": subsets[t]["full_train_rows"] - subsets[t]["subset_train_rows"],
            "Retention Percentage": f"{subsets[t]['retention_pct']:.1f}%",
            "Volume Reduction (%)": f"{100.0 - subsets[t]['retention_pct']:.1f}%",
            "Sampling Strategy": subsets[t]["strategy"],
            "Speedup Benefit": "4.12x (IoT linear fit) | ~4.0x (Tree grid)" if "iot" in t else "~2.0x"
        })
    df_stat = pd.DataFrame(stat_rows)
    df_stat.to_csv(os.path.join(DATA_STAT_DIR, "tuning_subset_statistics.csv"), index=False)
    print("Saved tuning_subset_statistics.csv")


if __name__ == "__main__":
    generate_classification_class_distributions()
    generate_regression_target_distributions()
    generate_dataset_size_comparison()
    generate_tuning_subset_reduction()
    print("All dataset and preprocessing figures generated successfully!")
