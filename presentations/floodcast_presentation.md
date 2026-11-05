# Slide Blueprint: FloodCast Pitch Deck (3-5 Slides)

### Slide 1: Problem Statement & Objectives
- **Headline:** Real-Time River Discharge Forecasting for Flood Mitigation
- **Goal:** Accurately predict peak daily discharge (`discharge_cfs`) across multiple river stations.
- **Key Challenges:** Non-linear hydrological lag effects, sudden extreme rainfall events, zero-leakage temporal requirements.

### Slide 2: Data & Feature Engineering Pipeline
- **Inputs:** Historical river discharge, precipitation, temperature, and watershed metadata.
- **Key Features:** Rolling precipitation windows (2–14 days), lagged soil moisture, and catchment interaction ratios.
- **Validation:** Strict chronological holdout splits to mimic real-world forecasting.

### Slide 3: Model Architecture & Evaluation
- **Models Used:** Ensemble of CatBoost and LightGBM regressors with 2.5x sample weighting on top 15% peaks.
- **Post-Processing:** Strict physical non-negative clipping (`discharge_cfs >= 0.0`).
- **Metric Optimization:** Balanced target weighting (RMSE 40%, Extreme Event RMSE 30%, MAE 20%, R² 10%).

### Slide 4: Results, Validation & Output Compliance
- **Performance Highlights:** Validation RMSE, MAE, and $R^2$ scores across holdout test dates.
- **Integrity Verification:** 100% automated assertion pass for `predictions.csv` (zero nulls, non-negative bounds, row alignment).

### Slide 5: Limitations & Future Enhancements
- **Current Limitations:** Dependence on accurate regional rainfall input accuracy and USGS StreamStats geodatabases.
- **Next Steps:** Incorporating satellite-derived snowpack melt features and spatial graph neural networks (GNNs).
