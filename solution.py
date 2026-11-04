#!/usr/bin/env python3
"""
solution.py
Complete, self-contained end-to-end pipeline for the FloodCast hackathon.

Pipeline Steps:
1. Load data/train.csv and data/test.csv, parse date as datetime, cast station_id to string.
2. Impute missing numeric values using station-level medians.
3. Implement a chronological validation split (train on earlier dates, validate on final 20%).
4. Apply sample weights emphasizing the top 15% discharge events (2.5x weight).
5. Train FloodCastModel(model_type='catboost') from src.models, evaluate local validation
   predictions using evaluate_predictions from src.metrics, and print the four weighted scores.
6. Retrain model on full training set, predict on data/test.csv, and assert valid predictions.
7. Output predictions to predictions.csv with exact columns: station_id,date,discharge_cfs.
"""

from pathlib import Path
from typing import List, Tuple
import numpy as np
import pandas as pd

from src.metrics import evaluate_predictions
from src.models import FloodCastModel


def load_and_preprocess_data(
    train_path: str = "data/train.csv",
    test_path: str = "data/test.csv",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Step 1: Load train and test data, parse dates, cast station_id to string.
    """
    print(f"Loading data from {train_path} and {test_path}...")
    train_df = pd.read_csv(train_path, dtype={"station_id": str}, encoding="utf-8")
    test_df = pd.read_csv(test_path, dtype={"station_id": str}, encoding="utf-8")

    # Parse date as datetime
    train_df["date"] = pd.to_datetime(train_df["date"])
    test_df["date"] = pd.to_datetime(test_df["date"])

    # Cast station_id to string
    train_df["station_id"] = train_df["station_id"].astype(str)
    test_df["station_id"] = test_df["station_id"].astype(str)

    print(f"Loaded train.csv: {train_df.shape[0]} rows, test.csv: {test_df.shape[0]} rows.")
    return train_df, test_df


def impute_station_medians(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Step 2: Impute missing numeric values using station-level medians derived
    from the training set (with global medians as fallback).
    """
    numeric_cols = [
        c
        for c in test_df.columns
        if c not in ("station_id", "date") and pd.api.types.is_numeric_dtype(test_df[c])
    ]

    # Calculate station-level and global medians on train_df
    station_medians = train_df.groupby("station_id")[numeric_cols].median()
    global_medians = train_df[numeric_cols].median()

    # Impute train_df
    for col in numeric_cols:
        train_col_median = train_df["station_id"].map(station_medians[col])
        train_df[col] = train_df[col].fillna(train_col_median).fillna(global_medians[col])

    # Impute test_df using the train station-level medians
    for col in numeric_cols:
        test_col_median = test_df["station_id"].map(station_medians[col])
        test_df[col] = test_df[col].fillna(test_col_median).fillna(global_medians[col])

    # If target column in train has missing values, impute with station median
    if "discharge_cfs" in train_df.columns and train_df["discharge_cfs"].isna().any():
        target_station_median = train_df.groupby("station_id")["discharge_cfs"].median()
        train_df["discharge_cfs"] = (
            train_df["discharge_cfs"]
            .fillna(train_df["station_id"].map(target_station_median))
            .fillna(train_df["discharge_cfs"].median())
        )

    print(f"Station-level median imputation completed for {len(numeric_cols)} numeric features.")
    return train_df, test_df


def create_features(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """
    Engineers temporal and hydrological antecedent features across continuous timeseries.
    """
    # Tag original test order to ensure exact row-by-row alignment
    test_df["_orig_idx"] = np.arange(len(test_df))
    train_df["_is_test"] = False
    test_df["_is_test"] = True
    combined = pd.concat([train_df, test_df], ignore_index=True)
    combined = combined.sort_values(by=["station_id", "date"]).reset_index(drop=True)

    # Calendar features
    doy = (
        combined["date"].dt.day_of_year
        if hasattr(combined["date"].dt, "day_of_year")
        else combined["date"].dt.dayofyear
    )
    combined["day_of_year"] = doy
    combined["month"] = combined["date"].dt.month
    combined["temp_range"] = combined["temp_max_c"] - combined["temp_min_c"]

    # Hydrological antecedent rainfall features (lags and 3-day rolling precipitation)
    combined["precip_lag1"] = (
        combined.groupby("station_id")["precipitation_mm"].shift(1).bfill()
    )
    combined["precip_lag2"] = (
        combined.groupby("station_id")["precipitation_mm"].shift(2).bfill()
    )
    combined["precip_roll3"] = combined.groupby("station_id")["precipitation_mm"].transform(
        lambda s: s.rolling(3, min_periods=1).mean()
    )

    feature_cols = [
        "station_id",
        "precipitation_mm",
        "precip_lag1",
        "precip_lag2",
        "precip_roll3",
        "temp_max_c",
        "temp_min_c",
        "temp_range",
        "soil_moisture",
        "drainage_area_sqmi",
        "mean_elevation_ft",
        "slope_pct",
        "forest_cover_pct",
        "day_of_year",
        "month",
    ]

    # Split back into train and test
    processed_train = (
        combined[~combined["_is_test"]]
        .drop(columns=["_is_test", "_orig_idx"], errors="ignore")
        .copy()
    )
    processed_test = combined[combined["_is_test"]].drop(columns=["_is_test"]).copy()

    # Re-sort to maintain clean order; restore processed_test to original row sequence
    processed_train = processed_train.sort_values(by=["station_id", "date"]).reset_index(drop=True)
    processed_test = (
        processed_test.sort_values(by="_orig_idx")
        .drop(columns=["_orig_idx"])
        .reset_index(drop=True)
    )

    return processed_train, processed_test, feature_cols


def main() -> None:
    # Retain the original unmodified test_df to guarantee exact row-by-row alignment
    original_test_df = pd.read_csv("data/test.csv", dtype={"station_id": str}, encoding="utf-8")

    # 1. Load data
    train_df, test_df = load_and_preprocess_data()

    # 2. Impute missing values
    train_df, test_df = impute_station_medians(train_df, test_df)

    # Feature engineering
    train_df, test_df, feature_cols = create_features(train_df, test_df)

    # 3. Chronological validation split (earlier 80% train, final 20% validation)
    unique_dates = np.sort(train_df["date"].unique())
    split_idx = int(len(unique_dates) * 0.80)
    split_date = unique_dates[split_idx]
    print(f"\nChronological Validation Split Cutoff: {pd.to_datetime(split_date).strftime('%Y-%m-%d')}")

    train_split = train_df[train_df["date"] < split_date].copy()
    val_split = train_df[train_df["date"] >= split_date].copy()
    print(f"Train split size: {len(train_split)} rows | Val split size: {len(val_split)} rows")

    # 4. Apply sample weights emphasizing top 15% discharge events (2.5x weight)
    q85_val = float(np.quantile(train_split["discharge_cfs"], 0.85))
    sample_weights_val = np.where(train_split["discharge_cfs"] >= q85_val, 2.5, 1.0)
    print(f"Top 15% discharge threshold (val split): {q85_val:.2f} cfs (weight = 2.5x)")

    # 5. Train FloodCastModel(model_type='catboost') and evaluate on validation set
    print("\nTraining validation CatBoost model...")
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

    val_preds = val_model.predict(val_split[feature_cols])

    # Evaluate predictions
    val_eval_df = val_split[["station_id", "discharge_cfs"]].copy()
    val_eval_df["pred_discharge_cfs"] = val_preds
    metrics = evaluate_predictions(val_eval_df)

    print("\n" + "=" * 60)
    print("LOCAL VALIDATION EVALUATION SCORES:")
    print(f"  1. Overall RMSE       (40% weight): {metrics['overall_rmse']:.4f}")
    print(f"  2. Extreme Event RMSE (30% weight): {metrics['extreme_rmse']:.4f}")
    print(f"  3. Overall MAE        (20% weight): {metrics['overall_mae']:.4f}")
    print(f"  4. Overall R^2        (10% weight): {metrics['overall_r2']:.4f}")
    print("=" * 60)

    # 6. Retrain model on full training set and predict on test.csv
    print("\nRetraining CatBoost model on full training set...")
    q85_full = float(np.quantile(train_df["discharge_cfs"], 0.85))
    sample_weights_full = np.where(train_df["discharge_cfs"] >= q85_full, 2.5, 1.0)

    full_model = FloodCastModel(
        model_type="catboost",
        cat_features=["station_id"],
        iterations=600,
        learning_rate=0.06,
        depth=6,
        random_state=42,
    )
    full_model.fit(
        train_df[feature_cols],
        train_df["discharge_cfs"],
        sample_weights=sample_weights_full,
    )

    print("Generating predictions on test set...")
    test_preds = full_model.predict(test_df[feature_cols])

    # Assertions
    assert len(test_preds) == len(test_df), (
        f"Row count mismatch: got {len(test_preds)} predictions, expected {len(test_df)}"
    )
    assert not np.isnan(test_preds).any(), "Predictions contain NaN values!"
    assert np.all(test_preds >= 0.0), "Predictions contain negative values!"
    print(f"Assertions passed: {len(test_preds)} valid, non-negative predictions generated.")

    # 7. Output result to predictions.csv directly assigning columns from original_test_df
    output_path = Path("predictions.csv")
    predictions_df = pd.DataFrame({
        "station_id": original_test_df["station_id"],
        "date": original_test_df["date"],
        "discharge_cfs": np.round(test_preds, 2),
    })

    predictions_df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\nFinal submission successfully written to {output_path.resolve()}")
    print(f"Columns: {list(predictions_df.columns)}")
    print(f"Rows: {len(predictions_df)}")
    print("\nPredictions Sample:")
    print(predictions_df.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
