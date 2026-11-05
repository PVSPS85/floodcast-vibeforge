#!/usr/bin/env python3
"""
scripts/generate_sample_submission.py
Generates data/sample_submission.csv based on data/test.csv if present,
or a 7-day 5-station fallback if missing.
"""

from pathlib import Path
import pandas as pd

def generate_sample_submission():
    test_path = Path("data/test.csv")
    output_path = Path("data/sample_submission.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if test_path.exists():
        print(f"Found {test_path}. Extracting station_id and date...")
        test_df = pd.read_csv(test_path, dtype={"station_id": str})
        sample_df = pd.DataFrame({
            "station_id": test_df["station_id"].astype(str),
            "date": test_df["date"],
            "discharge_cfs": 0.0
        })
        print(f"Extracted {len(sample_df):,} rows from test.csv.")
    else:
        print(f"{test_path} missing. Generating 5-station 7-day fallback...")
        starter_stations = ["01646500", "07010000", "08158000", "02087500", "11447650"]
        date_range = pd.date_range("2024-01-01", "2024-01-07", freq="D").strftime("%Y-%m-%d")
        
        rows = []
        for station_id in starter_stations:
            for d in date_range:
                rows.append({"station_id": station_id, "date": d, "discharge_cfs": 0.0})
        
        sample_df = pd.DataFrame(rows)
        print(f"Generated {len(sample_df)} fallback rows.")

    sample_df.to_csv(output_path, index=False)
    print(f"Successfully generated {output_path} with {len(sample_df):,} rows.")
    print("Columns:", list(sample_df.columns))
    print("Head:\n", sample_df.head(3))

if __name__ == "__main__":
    generate_sample_submission()

