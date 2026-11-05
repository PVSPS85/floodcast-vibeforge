"""
src/api.py
FastAPI REST Telemetry Backend for Floodcast.
Serves real USGS streamflow observations and CatBoost ML flood forecasts.
"""

from pathlib import Path
from typing import Dict, List, Optional
import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Floodcast Hydrologic Telemetry & Forecast API",
    description="Real-time river streamflow monitoring and CatBoost flood forecasting API.",
    version="1.0.0",
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path("data")


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Floodcast ML Telemetry Backend",
        "version": "1.0.0",
        "stations_endpoint": "/api/stations",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/stations")
def get_stations():
    metadata_path = DATA_DIR / "station_metadata.csv"
    if not metadata_path.exists():
        metadata_path = Path("../data/station_metadata.csv")

    if not metadata_path.exists():
        raise HTTPException(status_code=404, detail="station_metadata.csv not found")

    df = pd.read_csv(metadata_path, dtype={"station_id": str})
    return df.to_dict(orient="records")


@app.get("/api/stations/{station_id}")
def get_station_telemetry(station_id: str, days: Optional[int] = None):
    clean_id = station_id.strip()

    train_path = DATA_DIR / "train.csv"
    pred_path = Path("predictions.csv")

    if not train_path.exists():
        train_path = Path("../data/train.csv")
    if not pred_path.exists():
        pred_path = Path("../predictions.csv")

    records = []

    # Historical data from train.csv
    if train_path.exists():
        train_df = pd.read_csv(train_path, dtype={"station_id": str})
        station_train = train_df[train_df["station_id"] == clean_id].sort_values("date")
        for _, row in station_train.iterrows():
            q = max(0.0, float(row.get("discharge_cfs", 0.0)))
            records.append({
                "date": str(row["date"]),
                "discharge_cfs": q,
                "pred_discharge_cfs": q,
                "precipitation_mm": float(row.get("precipitation_mm", 0.0)),
                "temp_max_c": float(row.get("temp_max_c", 0.0)),
                "temp_min_c": float(row.get("temp_min_c", 0.0)),
                "soil_moisture": float(row.get("soil_moisture", 0.0)),
                "is_forecast": False,
            })

    # Forecast data from predictions.csv
    if pred_path.exists():
        pred_df = pd.read_csv(pred_path, dtype={"station_id": str})
        station_pred = pred_df[pred_df["station_id"] == clean_id].sort_values("date")
        for _, row in station_pred.iterrows():
            q = max(0.0, float(row.get("discharge_cfs", 0.0)))
            records.append({
                "date": str(row["date"]),
                "discharge_cfs": q,
                "pred_discharge_cfs": q,
                "precipitation_mm": 0.0,
                "temp_max_c": 0.0,
                "temp_min_c": 0.0,
                "soil_moisture": 0.0,
                "is_forecast": True,
            })

    if not records:
        raise HTTPException(
            status_code=404,
            detail=f"No telemetry found for station_id '{clean_id}'",
        )

    records.sort(key=lambda r: r["date"])

    if days and days > 0:
        records = records[-days:]

    return records

