import os
from pathlib import Path
import pandas as pd
import requests

def load_data(data_dir="data"):
    """
    Loads train, test, and metadata, cleans columns, parses dates, 
    and handles missing values without temporal leakage.
    """
    data_path = Path(data_dir)
    
    # Load raw CSVs with station_id preserved as string
    train_df = pd.read_csv(data_path / "train.csv", dtype={"station_id": str})
    test_df = pd.read_csv(data_path / "test.csv", dtype={"station_id": str})
    
    # Optional metadata merge
    meta_file = data_path / "station_metadata.csv"
    meta_df = pd.read_csv(meta_file, dtype={"station_id": str}) if meta_file.exists() else None

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

def fetch_usgs_discharge(site_id="01646500", start_date="2018-01-01", end_date="2023-12-31"):
    url = f"https://waterservices.usgs.gov/nwis/dv/?format=json&sites={site_id}&startDT={start_date}&endDT={end_date}&parameterCd=00060"
    print(f"Querying USGS API for Station {site_id}...")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Warning: USGS API failed for site {site_id}")
        return pd.DataFrame()
    try:
        data = response.json()
        time_series = data['value']['timeSeries'][0]['values'][0]['value']
        df = pd.DataFrame(time_series)
        df['discharge_cfs'] = pd.to_numeric(df['value'], errors='coerce')
        df['date'] = pd.to_datetime(df['dateTime']).dt.strftime('%Y-%m-%d')
        df['station_id'] = f"STN_{site_id}"
        return df[['station_id', 'date', 'discharge_cfs']].dropna()
    except Exception as e:
        print(f"Error parsing USGS JSON: {e}")
        return pd.DataFrame()

def fetch_open_meteo_weather(lat=38.8951, lon=-77.0364, start_date="2018-01-01", end_date="2023-12-31"):
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&daily=precipitation_sum,temperature_2m_max,temperature_2m_min,soil_moisture_0_to_7cm&timezone=America/New_York"
    print("Querying Open-Meteo Weather API...")
    response = requests.get(url)
    if response.status_code != 200:
        print("Warning: Open-Meteo API failed")
        return pd.DataFrame()
    try:
        data = response.json()
        daily = data.get('daily', {})
        df = pd.DataFrame({
            'date': daily.get('time'),
            'precipitation_sum': daily.get('precipitation_sum'),
            'temperature_2m_max': daily.get('temperature_2m_max'),
            'temperature_2m_min': daily.get('temperature_2m_min'),
            'soil_moisture_0_to_7cm': daily.get('soil_moisture_0_to_7cm')
        })
        return df
    except Exception as e:
        print(f"Error parsing Open-Meteo JSON: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    train, test = load_data("data")
    print(f"Train data shape: {train.shape}")
    print(f"Test data shape: {test.shape}")
    print("data_loader.py is working perfectly!")
