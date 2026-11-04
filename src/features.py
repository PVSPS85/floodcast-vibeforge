import pandas as pd
import numpy as np
from src.data_loader import load_data

def build_features(df):
    """
    Engineers hydrological features: rolling windows, lags, and catchment interactions.
    """
    df = df.copy()
    
    # 1. Temporal Features
    df["month"] = df["date"].dt.month
    df["day_of_year"] = df["date"].dt.dayofyear
    df["doy_sin"] = np.sin(2 * np.pi * df["day_of_year"] / 365.25)
    df["doy_cos"] = np.cos(2 * np.pi * df["day_of_year"] / 365.25)

    # 2. Hydrological Rolling Windows & 3. Lag Features
    # Grouping by station_id is critical to prevent leaking data between different rivers
    grouped = df.groupby("station_id")
    
    if "precipitation_mm" in df.columns:
        for w in [2, 3, 5, 7, 14]:
            df[f"precip_roll_sum_{w}d"] = grouped["precipitation_mm"].transform(
                lambda s: s.rolling(window=w, min_periods=1).sum()
            )
            
    lag_targets = [c for c in ["precipitation_mm", "soil_moisture", "temp_max_c"] if c in df.columns]
    for col in lag_targets:
        for lag in [1, 2, 3]:
            df[f"{col}_lag_{lag}d"] = grouped[col].shift(lag)

    # 4. Catchment Interactions
    if "precipitation_mm" in df.columns and "drainage_area_sqmi" in df.columns:
        df["rainfall_volume_proxy"] = df["precipitation_mm"] * df["drainage_area_sqmi"]

    # 5. NaN Handling (Backfilling the N/A values created by shifting/rolling at the start of each station)
    numeric_cols = [c for c in df.select_dtypes(include=["float64", "float32"]).columns if c != "discharge_cfs"]
    df[numeric_cols] = df.groupby("station_id")[numeric_cols].transform(lambda grp: grp.bfill())

    return df

if __name__ == "__main__":
    train_df, test_df = load_data("data")
    train_features = build_features(train_df)
    
    print(f"Original train shape: {train_df.shape}")
    print(f"Engineered train shape: {train_features.shape}")
    print(f"New columns added: {len(train_features.columns) - len(train_df.columns)}")
    print("features.py is working perfectly!")
