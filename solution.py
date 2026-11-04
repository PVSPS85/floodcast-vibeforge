import pandas as pd

# Create a sample DataFrame matching the exact requirements
data = {
    "station_id": ["STN_001", "STN_001", "STN_002"],
    "date": ["2024-01-01", "2024-01-02", "2024-01-01"],
    "discharge_cfs": [150.5, 230.0, 42.1]
}

df = pd.DataFrame(data)

# Save to the root or data directory so validate_submission.py can check it
df.to_csv("predictions.csv", index=False)
print("predictions.csv generated successfully!")
