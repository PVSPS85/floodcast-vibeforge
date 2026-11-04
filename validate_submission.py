import os
import sys
import pandas as pd

def validate_predictions():
    print("=" * 60)
    print(" 🌊 FLOODCAST VIBEFORGE - SUBMISSION VALIDATOR")
    print("=" * 60)
    
    possible_paths = ["predictions.csv", "data/predictions.csv"]
    target_path = None
    for path in possible_paths:
        if os.path.exists(path):
            target_path = path
            break

    if not target_path:
        print("❌ ERROR: Could not find 'predictions.csv'.")
        sys.exit(1)

    df = pd.read_csv(target_path)
    expected_columns = ["station_id", "date", "discharge_cfs"]
    if list(df.columns) != expected_columns:
        print(f"❌ ERROR: Columns mismatch. Expected {expected_columns}, got {list(df.columns)}")
        sys.exit(1)

    if df.isnull().sum().sum() > 0:
        print("❌ ERROR: Found missing/NaN values.")
        sys.exit(1)

    if (df["discharge_cfs"] < 0).sum() > 0:
        print("❌ ERROR: Found negative discharge predictions.")
        sys.exit(1)

    print("🎉 ALL SUBMISSION CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    validate_predictions()
