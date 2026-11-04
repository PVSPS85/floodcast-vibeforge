#!/usr/bin/env python3
"""
fetch_data.py
Creates and populates the dataset for the flood forecasting pipeline.

Produces:
- data/train.csv: Multi-year daily data for 5 river stations with target discharge_cfs.
- data/test.csv: Daily data for the same stations occurring strictly chronologically
                after train.csv, without the target column.

Schema:
- station_id: Unique station identifier
- date: YYYY-MM-DD
- precipitation_mm: Daily precipitation in millimeters
- temp_max_c: Daily maximum temperature in Celsius
- temp_min_c: Daily minimum temperature in Celsius
- soil_moisture: Volumetric soil moisture index [0.0 - 1.0]
- drainage_area_sqmi: Catchment drainage area in square miles
- mean_elevation_ft: Catchment mean elevation in feet
- slope_pct: Catchment mean basin slope percentage
- forest_cover_pct: Catchment forest cover percentage
- discharge_cfs: Streamflow discharge in cubic feet per second (train only)
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


# Station catchment static physical characteristics
STATIONS_METADATA: List[Dict[str, float]] = [
    {
        "station_id": "STATION_01",
        "drainage_area_sqmi": 344.0,
        "mean_elevation_ft": 1420.0,
        "slope_pct": 8.4,
        "forest_cover_pct": 74.5,
        "base_flow_cfs": 180.0,
    },
    {
        "station_id": "STATION_02",
        "drainage_area_sqmi": 118.0,
        "mean_elevation_ft": 950.0,
        "slope_pct": 11.2,
        "forest_cover_pct": 82.0,
        "base_flow_cfs": 65.0,
    },
    {
        "station_id": "STATION_03",
        "drainage_area_sqmi": 512.0,
        "mean_elevation_ft": 820.0,
        "slope_pct": 5.1,
        "forest_cover_pct": 48.0,
        "base_flow_cfs": 310.0,
    },
    {
        "station_id": "STATION_04",
        "drainage_area_sqmi": 225.0,
        "mean_elevation_ft": 1150.0,
        "slope_pct": 7.3,
        "forest_cover_pct": 66.5,
        "base_flow_cfs": 130.0,
    },
    {
        "station_id": "STATION_05",
        "drainage_area_sqmi": 1280.0,
        "mean_elevation_ft": 680.0,
        "slope_pct": 4.2,
        "forest_cover_pct": 52.0,
        "base_flow_cfs": 820.0,
    },
]


def generate_station_timeseries(
    meta: Dict[str, float],
    dates: pd.DatetimeIndex,
    random_seed: int = 42,
) -> pd.DataFrame:
    """
    Simulates physically realistic daily hydrometeorological timeseries
    for a river basin station based on rainfall-runoff and catchment characteristics.
    """
    rng = np.random.default_rng(random_seed)
    n_days = len(dates)

    # 1. Seasonality from day of year (doy)
    doy = (
        dates.day_of_year.to_numpy()
        if hasattr(dates, "day_of_year")
        else dates.dayofyear.to_numpy()
    )
    seasonal_temp_trend = 12.0 + 13.0 * np.sin(2 * np.pi * (doy - 105) / 365.25)
    temp_noise = rng.normal(0, 3.0, size=n_days)
    mean_temp = seasonal_temp_trend + temp_noise

    # Diurnal temperature variations (min and max)
    diurnal_range = rng.uniform(7.0, 14.0, size=n_days)
    temp_max_c = np.round(mean_temp + diurnal_range / 2.0, 2)
    temp_min_c = np.round(mean_temp - diurnal_range / 2.0, 2)

    # 2. Daily Precipitation (mixed process: Bernoulli rain days + Gamma intensity)
    # Higher rain probability in spring/autumn, with summer convective extremes
    seasonal_rain_prob = 0.28 + 0.10 * np.sin(2 * np.pi * (doy - 60) / 365.25)
    rain_days = rng.random(size=n_days) < seasonal_rain_prob

    # Gamma distribution for rainfall amounts on wet days
    rain_amount = np.zeros(n_days)
    raw_rain = rng.gamma(shape=1.4, scale=12.0, size=n_days)
    # Inject occasional extreme tropical/convective storm events (top storm surges)
    extreme_storm_prob = rng.random(size=n_days) < 0.02
    raw_rain[extreme_storm_prob] += rng.uniform(40.0, 95.0, size=np.sum(extreme_storm_prob))

    rain_amount[rain_days] = raw_rain[rain_days]
    precipitation_mm = np.round(rain_amount, 2)

    # 3. Dynamic Soil Moisture & Hydrological Runoff Routing
    # Modelled via simple Antecedent Precipitation Index (API) water balance
    soil_moisture = np.zeros(n_days)
    discharge_cfs = np.zeros(n_days)

    sm_current = 0.32
    baseflow = meta["base_flow_cfs"]
    quickflow = 0.0

    area = meta["drainage_area_sqmi"]
    slope = meta["slope_pct"]
    forest = meta["forest_cover_pct"]

    # Runoff coefficient modifier: higher slope & lower forest -> higher peak runoff
    runoff_multiplier = (1.0 + (slope - 6.0) * 0.05) * (1.0 - (forest - 50.0) * 0.004)
    runoff_multiplier = max(0.5, runoff_multiplier)

    # Flow recession coefficient (memory / storage routing)
    recession_k = 0.72 + 0.15 * (1.0 - slope / 15.0)

    for t in range(n_days):
        p = precipitation_mm[t]
        temp = mean_temp[t]

        # Potential evapotranspiration approximation
        pet = max(0.2, (temp + 5.0) * 0.12) if temp > -5.0 else 0.1

        # Soil moisture update: infiltration minus evapotranspiration and drainage
        sm_current = sm_current + (p * 0.003) - (pet * 0.002) - (sm_current * 0.02)
        sm_current = float(np.clip(sm_current, 0.08, 0.88))
        soil_moisture[t] = np.round(sm_current, 4)

        # Effective precipitation triggering direct runoff (higher when soil is saturated)
        saturation_factor = max(0.1, (sm_current - 0.20) / 0.60)
        direct_runoff_depth_mm = max(0.0, (p - 2.0) * saturation_factor * runoff_multiplier)

        # Runoff routing: quickflow pulse + linear reservoir recession
        # 1 mm of runoff over 1 sq mi ~= 92.8 cfs*day
        generated_flow = (direct_runoff_depth_mm * area * 0.82)
        quickflow = quickflow * recession_k + generated_flow * (1.0 - recession_k)

        # Baseflow seasonal variation with soil moisture recharge
        current_baseflow = baseflow * (0.7 + 0.6 * sm_current)

        # Total simulated streamflow with realistic measurement variability
        noise = rng.normal(0, 0.03 * (current_baseflow + quickflow) + 1.0)
        q_total = max(1.0, current_baseflow + quickflow + noise)
        discharge_cfs[t] = np.round(q_total, 2)

    df = pd.DataFrame({
        "station_id": meta["station_id"],
        "date": dates.strftime("%Y-%m-%d"),
        "precipitation_mm": precipitation_mm,
        "temp_max_c": temp_max_c,
        "temp_min_c": temp_min_c,
        "soil_moisture": soil_moisture,
        "drainage_area_sqmi": meta["drainage_area_sqmi"],
        "mean_elevation_ft": meta["mean_elevation_ft"],
        "slope_pct": meta["slope_pct"],
        "forest_cover_pct": meta["forest_cover_pct"],
        "discharge_cfs": discharge_cfs,
    })

    return df


def generate_dataset(
    train_start: str = "2018-01-01",
    train_end: str = "2022-12-31",
    test_start: str = "2023-01-01",
    test_end: str = "2023-12-31",
    output_dir: str = "data",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generates multi-station train and test splits respecting strict chronological ordering.
    """
    train_dates = pd.date_range(start=train_start, end=train_end, freq="D")
    test_dates = pd.date_range(start=test_start, end=test_end, freq="D")

    # Strict chronological assertion
    assert train_dates.max() < test_dates.min(), "test.csv must occur strictly after train.csv"

    train_station_dfs: List[pd.DataFrame] = []
    test_station_dfs: List[pd.DataFrame] = []

    for i, meta in enumerate(STATIONS_METADATA):
        # Continuous timeseries across train and test for each station
        full_dates = train_dates.append(test_dates)
        full_df = generate_station_timeseries(meta, full_dates, random_seed=100 + i * 37)

        # Split into train and test
        station_train = full_df[full_df["date"] <= train_end].copy()
        station_test = full_df[full_df["date"] >= test_start].copy()

        # Remove target column from test set
        station_test = station_test.drop(columns=["discharge_cfs"])

        train_station_dfs.append(station_train)
        test_station_dfs.append(station_test)

    train_df = pd.concat(train_station_dfs, ignore_index=True)
    test_df = pd.concat(test_station_dfs, ignore_index=True)

    # Sort deterministically by station_id and date
    train_df = train_df.sort_values(by=["station_id", "date"]).reset_index(drop=True)
    test_df = test_df.sort_values(by=["station_id", "date"]).reset_index(drop=True)

    # Ensure output directory exists
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    train_file = out_path / "train.csv"
    test_file = out_path / "test.csv"

    # Save CSVs with UTF-8 encoding
    train_df.to_csv(train_file, index=False, encoding="utf-8")
    test_df.to_csv(test_file, index=False, encoding="utf-8")

    print(f"Generated train.csv: {train_df.shape[0]} rows, {train_df.shape[1]} columns -> {train_file}")
    print(f"Generated test.csv:  {test_df.shape[0]} rows, {test_df.shape[1]} columns -> {test_file}")

    return train_df, test_df


if __name__ == "__main__":
    generate_dataset()
