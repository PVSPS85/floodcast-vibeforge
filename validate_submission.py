import pandas as pd
import sys
from pathlib import Path

def validate():
    print("Validating predictions.csv...")
    
    sub_path = Path("predictions.csv")
    test_path = Path("data/test.csv")
    
    if not sub_path.exists():
        print("FAIL: predictions.csv not found. Run solution.py first.")
        sys.exit(1)
        
    if not test_path.exists():
        print("FAIL: data/test.csv not found.")
        sys.exit(1)
        
    sub = pd.read_csv(sub_path)
    test = pd.read_csv(test_path)

    # 1. Column Check
    expected_cols = ["station_id", "date", "discharge_cfs"]
    if list(sub.columns) != expected_cols:
        print(f"FAIL: Columns must be exactly {expected_cols}. Found: {list(sub.columns)}")
        sys.exit(1)

    # 2. Row Count Check
    if len(sub) != len(test):
        print(f"FAIL: Row count mismatch. Expected {len(test)}, got {len(sub)}.")
        sys.exit(1)

    # 3. NaN Check
    if sub.isnull().values.any():
        print("FAIL: Found missing values (NaNs) in the submission.")
        sys.exit(1)

    # 4. Non-negative Check
    if (sub["discharge_cfs"] < 0).any():
        print("FAIL: Found negative discharge values. All predictions must be >= 0.0.")
        sys.exit(1)

    print("SUCCESS: predictions.csv is perfectly formatted for submission!")

if __name__ == "__main__":
    validate()