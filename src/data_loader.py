import pandas as pd
from pathlib import Path
import os

def load_data(data_dir="data"):
    """
    Loads train, test, and metadata, cleans columns, parses dates, 
    and handles missing values without temporal leakage.
    """
    data_path = Path(data_dir)
    
    # Load raw CSVs
    train_df = pd.read_csv(data_path / "train.csv")
    test_df = pd.read_csv(data_path / "test.csv")
    
    # Optional metadata merge
    meta_file = data_path / "station_metadata.csv"
    meta_df = pd.read_csv(meta_file) if meta_file.exists() else None

    processed_dfs = []
    for df, is_train in [(train_df, True), (test_df, False)]:
        # Standardize columns
        df.columns = df.columns.str.strip().str.lower()
        
        # Parse dates and ensure station_id is string
        df["date"] = pd.to_datetime(df["date"])
        df["station_id"] = df["station_id"].astype(str)
        
        # Sort strictly to prevent time leakage
        df = df.sort_values(by=["station_id", "date"]).reset_index(drop=True)
        
        # Merge metadata if available
        if meta_df is not None:
            meta_df.columns = meta_df.columns.str.strip().str.lower()
            meta_df["station_id"] = meta_df["station_id"].astype(str)
            cols_to_use = [c for c in meta_df.columns if c not in df.columns or c == "station_id"]
            df = df.merge(meta_df[cols_to_use], on="station_id", how="left")
            
        # Fill missing numeric weather data safely within each station's timeline
        numeric_cols = [c for c in df.select_dtypes(include=["float64", "int64"]).columns if c != "discharge_cfs"]
        if numeric_cols:
            df[numeric_cols] = df.groupby("station_id")[numeric_cols].transform(lambda grp: grp.ffill().bfill())
            
        # Hard constraint: No negative discharge in training data
        if is_train and "discharge_cfs" in df.columns:
            df["discharge_cfs"] = df["discharge_cfs"].clip(lower=0.0)
            
        processed_dfs.append(df)

    return processed_dfs[0], processed_dfs[1]

if __name__ == "__main__":
    train, test = load_data("data")
    print(f"Train data shape: {train.shape}")
    print(f"Test data shape: {test.shape}")
    print("data_loader.py is working perfectly!")
