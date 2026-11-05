#!/usr/bin/env python3
"""
fetch_metadata.py
Generates and writes data/station_metadata.csv for all 50 USGS river gauge stations.
"""

from pathlib import Path
import pandas as pd
import fetch_batch_data

def main():
    print("Extracting metadata for 50 USGS stations...")
    train_df = pd.read_csv("data/train.csv", dtype={"station_id": str})
    valid_station_ids = list(train_df["station_id"].unique())

    meta_lookup = {s["station_id"]: s for s in fetch_batch_data.USGS_STATIONS}

    rows = []
    for sid in valid_station_ids:
        meta = meta_lookup.get(sid, {})
        full_name = meta.get("name", f"USGS Station {sid}")

        # River and State parsing
        if " near " in full_name:
            river = full_name.split(" near ")[0]
        elif " at " in full_name:
            river = full_name.split(" at ")[0]
        elif " River " in full_name:
            river = full_name.split(" River ")[0] + " River"
        else:
            river = full_name.split()[0] + " River"

        # State extraction
        if "," in full_name:
            state = full_name.split(",")[-1].strip().split()[0].upper()
            if len(state) != 2:
                state = "US"
        else:
            state = "US"

        lat = float(meta.get("lat", 38.0))
        lon = float(meta.get("lon", -95.0))

        rows.append({
            "station_id": sid,
            "station_name": full_name,
            "latitude": lat,
            "longitude": lon,
            "state": state,
            "river_name": river,
        })

    out_df = pd.DataFrame(rows)
    out_path = Path("data/station_metadata.csv")
    out_df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"Successfully wrote {len(out_df)} stations to {out_path.resolve()}")

if __name__ == "__main__":
    main()
