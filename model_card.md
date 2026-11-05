# 🃏 Model Card: Floodcast River Discharge & Flood Regressor
### **Team VibeForge**

---

## 📋 1. Model Overview

* **Model Name:** Floodcast CatBoost River Discharge Forecaster
* **Model Version:** 1.0.0
* **Model Architecture:** CatBoost Regressor (Gradient-Boosted Decision Trees with Symmetric Oblivious Trees)
* **Underlying Algorithm:** Optimized Gradient Boosting on Decision Trees (`catboost.CatBoostRegressor`)
* **Task Type:** Multi-Station Hydrological Time-Series Regression
* **Target Variable:** `discharge_cfs` — Daily mean/peak streamflow volumetric discharge in cubic feet per second (cfs)
* **Domain:** Environmental Hydrometeorology & Disaster Early Warning
* **License:** Open-Source Hackathon Submission (MIT)

---

## ⚙️ 2. Input Features & Engineering

The model takes as input both time-varying atmospheric telemetry and invariant catchment geomorphometric properties:

### A. Dynamic Meteorological Drivers (Daily Telemetry via Open-Meteo / NWIS)
* `precipitation_mm`: Total 24-hour liquid precipitation accumulation (mm).
* `temp_max_c`: Daily maximum ambient 2-meter air temperature (°C).
* `temp_min_c`: Daily minimum ambient 2-meter air temperature (°C).
* `soil_moisture`: Volumetric antecedent root-zone soil water content ($0\text{–}7\text{ cm}$, $\text{m}^3/\text{m}^3$).

### B. Static Physiographic Drivers (Catchment Attributes via USGS StreamStats)
* `drainage_area_sqmi`: Total watershed contributing surface drainage area (square miles).
* `mean_elevation_ft`: Mean basin elevation above sea level (feet).
* `slope_pct`: Average watershed topographic land surface slope (% grade).
* `forest_cover_pct`: Proportion of catchment area with forest canopy vegetative cover (% forested).
* `station_id`: Unique USGS 8-digit gauge identifier (handled natively via CatBoost categorical feature hashing).

### C. Engineered Hydrological Signals
* **Cumulative Antecedent Precipitation Windows:** 2-day, 3-day, 5-day, 7-day, and 14-day rolling precipitation sums (`precip_roll_sum_{w}d`).
* **Temporal Lags:** 1-day, 2-day, and 3-day lagged soil moisture, precipitation, and temperature measurements to capture soil saturation delay and routing lag.
* **Catchment Interaction Terms:** Runoff volume proxy defined as $\text{precipitation\_mm} \times \text{drainage\_area\_sqmi}$.
* **Seasonality Encodings:** Sinusoidal and cosinusoidal transforms of the day-of-year to model annual snowmelt and evapotranspiration cyclicity.

---

## 🎯 3. Training & Validation Setup

* **Training Dataset Size:** 219,150 historical daily records (2010-01-01 to 2021-12-31) across 50 diverse USGS stations.
* **Test Dataset Size:** 36,500 daily records (2022-01-01 to 2023-12-31).
* **Validation Methodology:** Strict chronological split (earlier 80% train, final 20% holdout validation) to eliminate future data leakage.
* **Extreme Event Loss Weighting:** Top 15% historical discharge observations receive a 2.5× sample weight multiplier during gradient calculation, ensuring high-flow crests and flood peaks are prioritized over baseflow.
* **Hydrologic Physical Bounding:** Non-negative post-processing constraint ($Q_{\text{pred}} \ge 0.0\text{ cfs}$) enforced via `np.clip(y_pred, 0.0, None)`.

---

## 📈 4. Evaluation Metrics & Benchmarks

The model is evaluated against the competition benchmark metric suite:

$$\text{Final Score} = 0.40 \times \text{Overall RMSE} + 0.30 \times \text{Extreme RMSE} + 0.20 \times \text{Overall MAE} + 0.10 \times (1 - R^2)$$

### Benchmark Results

* **Training RMSE:** `[INSERT TRAINING RMSE HERE]` *(e.g., 4,820.5 cfs)*
* **Extreme Event RMSE (Top 10% Peak Flows):** `[INSERT EXTREME EVENT RMSE HERE]` *(e.g., 8,412.3 cfs)*
* **Overall Validation MAE:** `[INSERT MAE HERE]` *(e.g., 2,845.1 cfs)*
* **Overall Validation R²:** `[INSERT R² HERE]` *(e.g., 0.916)*

---

## ⚠️ 5. Known Limitations & Edge Cases

1. **Geographic Scope (USGS Dependency):** The model relies on the standardized drainage and elevation parameters supplied by the USGS StreamStats database and USGS NWIS station identifiers. Generalization to international basins requires equivalent high-resolution digital elevation models (DEM) and soil moisture telemetry.
2. **Extreme Tail Events Beyond Historical Bounds:** In the presence of unprecedented atmospheric rivers or Category 5 convective storms exceeding any 100-year return period observed in the 2010–2021 training horizon, tree-based regressors may cap out at previously seen partition boundaries.
3. **Anthropogenic River Regulation:** Man-made infrastructure operations (dam releases, lock gate controls, reservoir retention schedules, and irrigation diversions) are not explicitly parameterized and can cause divergence in heavily dam-regulated sub-basins.
4. **Localized Flash Flooding:** Forecasts represent daily mean/peak discharge at the mainstem USGS gauge; localized flash flooding on un-gauged minor urban tributaries may occur faster than the daily hydrological routing timestep.

---

## 🛡️ 6. Ethical & Operational Use Considerations

* **Intended Use:** Operational situational awareness, hydrological anomaly screening, and early decision support for emergency management agencies.
* **Prohibited Use:** Should not be used as the sole automated trigger for critical life-safety infrastructure (such as automatic dam floodgate openings) without certified hydrologist in-the-loop review.
