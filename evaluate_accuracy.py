#!/usr/bin/env python3
"""
evaluate_accuracy.py
Independent evaluation and verification script for the FloodCast CatBoost model.

Performs:
1. Loads data/train.csv and applies chronological 80/20 train/validation split.
2. Trains CatBoostRegressor with 2.5x sample weighting on top 15% peak flow events.
3. Generates predictions on the 20% validation split, strictly clipping at 0.0.
4. Calculates & outputs terminal report:
   - Overall R-squared (R^2)
   - Overall MAE
   - Overall RMSE
   - Extreme Event RMSE (top 10% actual discharge per station)
5. Generates high-resolution visualization comparing Actual vs. Predicted Discharge
   (hydrograph for the most active station + full validation scatter plot with 1:1 line).
6. Saves figure to accuracy_report.png in the root directory.
"""

import os
import sys
from pathlib import Path

# Configure matplotlib cache directory before importing
os.environ["MPLCONFIGDIR"] = os.path.abspath(".mpl_cache")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from solution import load_and_preprocess_data, impute_station_medians, create_features
from src.models import FloodCastModel
from src.metrics import calculate_extreme_rmse, evaluate_predictions


def main():
    print("=" * 72)
    print("   FLOODCAST MODEL ACCURACY & PERFORMANCE EVALUATION PIPELINE")
    print("=" * 72)

    # 1. Load and prepare dataset using official solution pipeline
    print("\n[Step 1/5] Loading and preprocessing dataset...")
    train_df, test_df = load_and_preprocess_data()
    train_df, test_df = impute_station_medians(train_df, test_df)
    train_df, test_df, feature_cols = create_features(train_df, test_df)

    # 2. Chronological 80/20 train/validation split
    print("\n[Step 2/5] Performing chronological 80/20 validation split...")
    unique_dates = np.sort(train_df["date"].unique())
    split_idx = int(len(unique_dates) * 0.80)
    split_date = unique_dates[split_idx]

    train_split = train_df[train_df["date"] < split_date].copy()
    val_split = train_df[train_df["date"] >= split_date].copy()

    train_start = pd.to_datetime(train_split["date"].min()).strftime("%Y-%m-%d")
    train_end = pd.to_datetime(train_split["date"].max()).strftime("%Y-%m-%d")
    val_start = pd.to_datetime(val_split["date"].min()).strftime("%Y-%m-%d")
    val_end = pd.to_datetime(val_split["date"].max()).strftime("%Y-%m-%d")

    print(f"  * Chronological Cutoff Date : {pd.to_datetime(split_date).strftime('%Y-%m-%d')}")
    print(f"  * Training Window (80%)     : {train_start} to {train_end} ({len(train_split):,} rows)")
    print(f"  * Validation Window (20%)   : {val_start} to {val_end} ({len(val_split):,} rows)")

    # 3. Compute 2.5x sample weights for top 15% peak discharge events
    q85_val = float(np.quantile(train_split["discharge_cfs"], 0.85))
    sample_weights_val = np.where(train_split["discharge_cfs"] >= q85_val, 2.5, 1.0)
    print(f"  * Peak Event Weighting      : 2.5x on values >= {q85_val:.2f} cfs (top 15%)")

    # 4. Train CatBoostRegressor
    print("\n[Step 3/5] Training CatBoostRegressor on 80% train split...")
    val_model = FloodCastModel(
        model_type="catboost",
        cat_features=["station_id"],
        iterations=600,
        learning_rate=0.06,
        depth=6,
        random_state=42,
    )
    val_model.fit(
        train_split[feature_cols],
        train_split["discharge_cfs"],
        sample_weights=sample_weights_val,
    )
    print("  * Model training completed successfully.")

    # 5. Generate validation predictions and enforce non-negative constraint
    print("\n[Step 4/5] Generating predictions and evaluating metrics...")
    raw_preds = val_model.predict(val_split[feature_cols])
    val_preds = np.clip(raw_preds, 0.0, None)

    val_eval_df = val_split[["station_id", "date", "discharge_cfs"]].copy()
    val_eval_df["pred_discharge_cfs"] = val_preds

    # Metric calculations
    y_true = val_eval_df["discharge_cfs"].to_numpy(dtype=np.float64)
    y_pred = val_eval_df["pred_discharge_cfs"].to_numpy(dtype=np.float64)

    overall_r2 = float(r2_score(y_true, y_pred))
    overall_mae = float(mean_absolute_error(y_true, y_pred))
    overall_rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    extreme_rmse = float(calculate_extreme_rmse(val_eval_df))

    composite_score = (
        0.40 * overall_rmse +
        0.30 * extreme_rmse +
        0.20 * overall_mae +
        0.10 * (1.0 - overall_r2)
    )

    # Format terminal report
    print("\n" + "=" * 72)
    print("                 MODEL ACCURACY & PERFORMANCE REPORT                   ")
    print("=" * 72)
    print(f"  1. Overall R-squared (R^2)          : {overall_r2:12.4f}  (10% weight)")
    print(f"  2. Overall MAE                      : {overall_mae:12.2f} cfs (20% weight)")
    print(f"  3. Overall RMSE                     : {overall_rmse:12.2f} cfs (40% weight)")
    print(f"  4. Extreme Event RMSE (Top 10% peak): {extreme_rmse:12.2f} cfs (30% weight)")
    print("-" * 72)
    print(f"  >> COMPOSITE BENCHMARK SCORE        : {composite_score:12.2f}")
    print("=" * 72)

    # 6. Generate visualization
    print("\n[Step 5/5] Generating publication-grade visualization: accuracy_report.png...")

    # Load station metadata for river names if available
    station_meta = {}
    if os.path.exists("data/station_metadata.csv"):
        try:
            meta_df = pd.read_csv("data/station_metadata.csv", dtype={"station_id": str})
            col_name = "station_name" if "station_name" in meta_df.columns else "name"
            station_meta = dict(zip(meta_df["station_id"], meta_df[col_name]))
        except Exception:
            pass

    # Find the most active station by maximum observed discharge on validation split
    station_peaks = val_eval_df.groupby("station_id")["discharge_cfs"].max()
    most_active_id = str(station_peaks.idxmax())
    active_name = station_meta.get(most_active_id, f"USGS #{most_active_id}")
    active_df = val_eval_df[val_eval_df["station_id"] == most_active_id].sort_values("date")

    active_q90 = float(active_df["discharge_cfs"].quantile(0.90))
    active_r2 = float(r2_score(active_df["discharge_cfs"], active_df["pred_discharge_cfs"]))
    active_rmse = float(np.sqrt(mean_squared_error(active_df["discharge_cfs"], active_df["pred_discharge_cfs"])))

    # Create 2-panel figure
    fig = plt.figure(figsize=(15, 11), facecolor="#0B1120")

    # Panel 1: Hydrograph Comparison for Most Active Station
    ax1 = plt.subplot(2, 1, 1, facecolor="#0F172A")
    ax1.plot(
        active_df["date"],
        active_df["discharge_cfs"],
        label="Actual Discharge (USGS NWIS)",
        color="#38BDF8",
        linewidth=2.2,
        alpha=0.95,
    )
    ax1.plot(
        active_df["date"],
        active_df["pred_discharge_cfs"],
        label="CatBoost Predicted Discharge",
        color="#F97316",
        linewidth=2.0,
        linestyle="--",
        alpha=0.95,
    )
    ax1.fill_between(
        active_df["date"],
        active_df["discharge_cfs"],
        active_df["pred_discharge_cfs"],
        color="#F97316",
        alpha=0.15,
        label="Prediction Residual Spread",
    )
    ax1.axhline(
        y=active_q90,
        color="#EF4444",
        linestyle=":",
        linewidth=1.8,
        label=f"Top 10% Extreme Flood Peak Threshold ({active_q90:,.0f} cfs)",
    )

    ax1.set_title(
        f"Validation Hydrograph: Actual vs. CatBoost Predicted Discharge\n"
        f"Primary Station: {active_name} (USGS #{most_active_id}) | Local R² = {active_r2:.4f} | Local RMSE = {active_rmse:,.1f} cfs",
        fontsize=13,
        fontweight="bold",
        color="#F8FAFC",
        pad=12,
    )
    ax1.set_xlabel("Observation Date", fontsize=11, color="#94A3B8")
    ax1.set_ylabel("Streamflow Discharge (cfs)", fontsize=11, color="#94A3B8")
    ax1.grid(True, linestyle="--", alpha=0.25, color="#64748B")
    ax1.tick_params(colors="#CBD5E1", labelsize=10)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    for spine in ax1.spines.values():
        spine.set_color("#334155")
    ax1.legend(loc="upper right", framealpha=0.9, facecolor="#1E293B", edgecolor="#475569", labelcolor="#F1F5F9")

    # Panel 2: Scatter Plot of Actual vs. Predicted Discharge across all validation data
    ax2 = plt.subplot(2, 1, 2, facecolor="#0F172A")

    # Subsample for clean plotting if very large, otherwise plot full
    plot_sample = val_eval_df if len(val_eval_df) <= 15000 else val_eval_df.sample(15000, random_state=42)
    max_val = max(val_eval_df["discharge_cfs"].max(), val_eval_df["pred_discharge_cfs"].max()) * 1.05

    # Scatter points with alpha
    ax2.scatter(
        plot_sample["discharge_cfs"],
        plot_sample["pred_discharge_cfs"],
        alpha=0.35,
        color="#38BDF8",
        edgecolors="none",
        s=16,
        label="Validation Station-Days (20% Holdout)",
    )

    # 1:1 perfect prediction reference line
    ax2.plot(
        [0, max_val],
        [0, max_val],
        color="#EF4444",
        linestyle="--",
        linewidth=2.0,
        label="Ideal 1:1 Parity Line (y = x)",
    )

    ax2.set_xlim(-max_val * 0.02, max_val)
    ax2.set_ylim(-max_val * 0.02, max_val)
    ax2.set_title(
        f"Validation Goodness-of-Fit: Actual vs. Predicted Discharge (All 50 Stations)",
        fontsize=13,
        fontweight="bold",
        color="#F8FAFC",
        pad=12,
    )
    ax2.set_xlabel("Actual Streamflow Discharge (cfs)", fontsize=11, color="#94A3B8")
    ax2.set_ylabel("Predicted Streamflow Discharge (cfs)", fontsize=11, color="#94A3B8")
    ax2.grid(True, linestyle="--", alpha=0.25, color="#64748B")
    ax2.tick_params(colors="#CBD5E1", labelsize=10)
    for spine in ax2.spines.values():
        spine.set_color("#334155")

    # Metrics Summary Box
    metrics_text = (
        f"Evaluation Metrics Summary:\n"
        f"─────────────────────────────\n"
        f"• Overall R²           : {overall_r2:.4f}\n"
        f"• Overall MAE          : {overall_mae:,.2f} cfs\n"
        f"• Overall RMSE         : {overall_rmse:,.2f} cfs\n"
        f"• Extreme Peak RMSE    : {extreme_rmse:,.2f} cfs\n"
        f"• Total Val Samples    : {len(val_eval_df):,} records\n"
        f"• Non-Negative Bounded : 100% Passed"
    )
    ax2.text(
        0.03,
        0.95,
        metrics_text,
        transform=ax2.transAxes,
        fontsize=10.5,
        fontfamily="monospace",
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.6", facecolor="#1E293B", edgecolor="#38BDF8", alpha=0.92),
        color="#F8FAFC",
    )
    ax2.legend(loc="lower right", framealpha=0.9, facecolor="#1E293B", edgecolor="#475569", labelcolor="#F1F5F9")

    plt.tight_layout(pad=2.5)

    output_fig_path = Path("accuracy_report.png")
    plt.savefig(output_fig_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"\n[Done] High-resolution visualization successfully saved to: {output_fig_path.resolve()}")
    print("=" * 72)


if __name__ == "__main__":
    main()

