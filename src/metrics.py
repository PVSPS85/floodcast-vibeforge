import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def evaluate_predictions(df_val, target_col="discharge_cfs", pred_col="prediction"):
    """
    Calculates the 4 core hackathon metrics:
    1. Overall RMSE (40%)
    2. Top 10% Extreme Event RMSE (30%)
    3. MAE (20%)
    4. R-Squared (10%)
    """
    y_true = df_val[target_col].values
    y_pred = df_val[pred_col].values
    
    # 1. Overall Metrics
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    # 2. Extreme Event RMSE (Top 10% of discharge days per station)
    extreme_true = []
    extreme_pred = []
    
    for station, group in df_val.groupby("station_id"):
        # Find the 90th percentile threshold for this specific river
        threshold = group[target_col].quantile(0.90)
        extreme_days = group[group[target_col] >= threshold]
        
        extreme_true.extend(extreme_days[target_col].values)
        extreme_pred.extend(extreme_days[pred_col].values)
        
    extreme_rmse = np.sqrt(mean_squared_error(extreme_true, extreme_pred)) if extreme_true else 0.0
    
    print("-" * 40)
    print(f"Overall RMSE:        {rmse:.2f}")
    print(f"Extreme Peak RMSE:   {extreme_rmse:.2f}")
    print(f"Mean Absolute Error: {mae:.2f}")
    print(f"R-Squared Score:     {r2:.4f}")
    print("-" * 40)
    
    return rmse, extreme_rmse, mae, r2

if __name__ == "__main__":
    # Dummy test to verify syntax
    print("metrics.py syntax is correct!")