# 🃏 Model Card: FloodCast River Discharge Regressor

## 📋 Model Overview
* **Model Type:** Gradient Boosted Decision Trees (CatBoost Regressor / LightGBM)
* **Target Variable:** `discharge_cfs` (Daily Peak River Discharge in cubic feet per second)[cite: 3]
* **Task:** Multi-Station Time-Series Regression[cite: 3]
* **License:** Open-Source Hackathon Submission

---

## ⚙️ Model Architecture & Features

### Feature Set
* **Temporal Rolling Features:** 2-day, 5-day, 7-day, and 14-day rolling sums and means of precipitation[cite: 3].
* **Hydrological Lags:** 1-day, 2-day, and 3-day lagged soil moisture and temperature measurements[cite: 3].
* **Station Metadata Features:** Categorical Station IDs, latitude, longitude, and elevation ratios[cite: 3].
* **Interaction Terms:** Rainfall-to-elevation interaction terms representing catchment runoff acceleration[cite: 3].

### Hyperparameters
* `loss_function`: RMSE[cite: 5]
* `eval_metric`: RMSE / Custom Peak RMSE[cite: 5]
* `iterations`: 1500
* `learning_rate`: 0.03
* `depth`: 6
* `l2_leaf_reg`: 3.0

---

## 📈 Evaluation & Metric Results

The model is evaluated against the competition evaluation suite[cite: 5]:

| Evaluation Metric | Target Weight | Validation Performance |
| :--- | :--- | :--- |
| **Overall RMSE** | 40% | *Monitored via Chronological Split* |
| **Extreme Event RMSE (Top 10%)** | 30% | *Monitored via Peak Loss Weighting* |
| **Mean Absolute Error (MAE)** | 20% | *Monitored via Holdout CV* |
| **R² Score** | 10% | *Monitored via Holdout CV* |

---

## ⚠️ Limitations & Edge Cases
1. **Unseen Weather Extremes:** Model performance may degrade on unprecedented historic rainfall events outside the distribution of the training set.
2. **Post-Processing Requirement:** Models can theoretically output negative flow rates; predictions are post-processed with `np.clip(predictions, 0, None)` to enforce non-negativity.
3. **Station Transferability:** Station generalization depends on representative geographic and elevation metadata[cite: 3].
