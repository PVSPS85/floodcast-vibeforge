import os
import sys
import pandas as pd


def validate_predictions():
    """
    Validates predictions.csv against hackathon submission rules:
    1. Checks file existence (root or data/ directory).
    2. Verifies expected columns: station_id, date, discharge_cfs.
    3. Asserts zero missing (NaN/null) values.
    4. Asserts strictly non-negative discharge predictions (discharge_cfs >= 0).
    5. Validates non-empty rows and proper data types.
    """
    print("=" * 60)
    print(" 🌊 FLOODCAST VIBEFORGE - SUBMISSION VALIDATOR")
    print("=" * 60)

    # 1. File Location Check
    possible_paths = ["predictions.csv", "data/predictions.csv"]
    target_path = None
    
    for path in possible_paths:
        if os.path.exists(path):
            target_path = path
            break

    if not target_path:
        print("❌ ERROR: Could not find 'predictions.csv' in root directory or 'data/' folder.")
        print("   Please run 'python solution.py' first to generate your predictions.")
        sys.exit(1)

    print(f"✅ File Found: Found target file at '{target_path}'.")

    # 2. File Loading & Schema Verification
    try:
        df = pd.read_csv(target_path)
    except Exception as e:
        print(f"❌ ERROR: Failed to parse '{target_path}' as a CSV file. Details: {e}")
        sys.exit(1)

    expected_columns = ["station_id", "date", "discharge_cfs"]
    actual_columns = list(df.columns)

    if actual_columns != expected_columns:
        print("❌ ERROR: Column header mismatch!")
        print(f"   Expected: {expected_columns}")
        print(f"   Found:    {actual_columns}")
        sys.exit(1)

    print(f"✅ Schema Verified: Columns match strictly {expected_columns}.")

    # 3. Row Count Check
    row_count = len(df)
    if row_count == 0:
        print("❌ ERROR: 'predictions.csv' is completely empty (0 rows).")
        sys.exit(1)
    
    print(f"✅ Row Count Verified: File contains {row_count:,} prediction rows.")

    # 4. Null / NaN Value Check
    null_counts = df.isnull().sum()
    total_nulls = null_counts.sum()

    if total_nulls > 0:
        print(f"❌ ERROR: Found {total_nulls} missing/NaN values across columns:")
        for col, count in null_counts.items():
            if count > 0:
                print(f"   - {col}: {count} nulls")
        sys.exit(1)

    print("✅ Null Check Passed: Zero missing or NaN values detected.")

    # 5. Non-Negativity & Data Type Verification
    if not pd.api.types.is_numeric_dtype(df["discharge_cfs"]):
        print("❌ ERROR: 'discharge_cfs' column is not numeric.")
        sys.exit(1)

    negative_mask = df["discharge_cfs"] < 0
    negative_count = negative_mask.sum()

    if negative_count > 0:
        print(f"❌ ERROR: Found {negative_count} negative discharge predictions!")
        print("   River discharge cannot be negative. Apply np.clip(predictions, 0, None).")
        print("   Sample negative rows:")
        print(df[negative_mask].head())
        sys.exit(1)

    print("✅ Value Range Verified: All discharge predictions are strictly non-negative (>= 0).")

    # 6. Summary Report
    print("-" * 60)
    print("🎉 ALL SUBMISSION CHECKS PASSED SUCCESSFULLY!")
    print(f"   - Target Path: {target_path}")
    print(f"   - Total Predictions: {row_count:,}")
    print(f"   - Min Discharge: {df['discharge_cfs'].min():.2f} cfs")
    print(f"   - Max Discharge: {df['discharge_cfs'].max():.2f} cfs")
    print(f"   - Mean Discharge: {df['discharge_cfs'].mean():.2f} cfs")
    print("=" * 60)


if __name__ == "__main__":
    validate_predictions()
```[cite: 4, 6]

---

### 2. `README.md`

Comprehensive team, approach, and execution documentation[cite: 4, 6].

```markdown
# 🌊 FloodCast VibeForge: High-Performance River Discharge Forecasting

## 📌 Team Information
* **Team Name:** FloodCast VibeForge
* **Team Members:** Harshith, Pranav, Bhavya, Nishanth

---

## 🎯 Project Overview
This repository contains our Machine Learning solution for predicting peak daily river discharge (`discharge_cfs`) across multiple hydrological stations[cite: 3]. Our pipeline models complex hydrological dynamics using precipitation patterns, soil moisture retention, and river basin physical characteristics while strictly enforcing chronological validation to avoid data leakage[cite: 3, 6].

---

## 🔬 Technical Approach Summary
Our solution uses an ensemble gradient boosting framework (**CatBoost** and **LightGBM**) optimized specifically for time-series regression on tabular hydrological data[cite: 6]:

1. **Feature Engineering:** We extract short- and long-term rainfall accumulation windows (2-day, 5-day, 7-day, and 14-day rolling sums), soil moisture lags, and station-level catchment interaction metrics to capture watershed response dynamics[cite: 3].
2. **Chronological Cross-Validation:** Models are evaluated using chronological holdout validation splits to prevent temporal leakage and simulate real-world forecasting performance[cite: 6].
3. **Loss Function Optimization:** Models are trained using custom weighted objectives to balance overall Root Mean Squared Error (RMSE) against extreme peak discharge events (top 10% highest discharge days)[cite: 5].

---

## 🚀 Execution & Quickstart Guide

### 1. Environment Setup
Clone the repository and install the pinned dependencies:
```bash
git clone [https://github.com/PVSPS85/floodcast-vibeforge.git](https://github.com/PVSPS85/floodcast-vibeforge.git)
cd floodcast-vibeforge
pip install -r requirements.txt
