"""
Evaluation metrics for river flood forecasting hackathon.

Evaluation Metric Components:
1. Overall RMSE across all samples (40% weight)
2. Extreme event RMSE calculated on top 10% highest discharge days per station (30% weight)
3. Overall MAE (20% weight)
4. Overall R² (10% weight)

All predictions are automatically clipped to non-negative values (>= 0) using numpy.
"""

from typing import Any, Dict, Optional, Sequence, Union
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score


# Metric weights defined by the competition
METRIC_WEIGHTS = {
    "overall_rmse": 0.40,
    "extreme_rmse": 0.30,
    "overall_mae": 0.20,
    "overall_r2": 0.10,
}


def _clip_non_negative(y: Union[Sequence[float], np.ndarray, pd.Series]) -> np.ndarray:
    """Helper to convert predictions to numpy array and clip values to >= 0."""
    arr = np.asarray(y, dtype=np.float64)
    return np.clip(arr, 0.0, None)


def calculate_overall_rmse(
    y_true: Union[Sequence[float], np.ndarray, pd.Series],
    y_pred: Union[Sequence[float], np.ndarray, pd.Series],
) -> float:
    """
    Calculate overall Root Mean Squared Error (RMSE) across all samples.
    Predictions are automatically clipped to non-negative values (>= 0).

    Args:
        y_true: Ground truth discharge values.
        y_pred: Predicted discharge values.

    Returns:
        float: Overall RMSE score.
    """
    y_true_arr = np.asarray(y_true, dtype=np.float64)
    y_pred_arr = _clip_non_negative(y_pred)

    if len(y_true_arr) == 0:
        return 0.0

    mse = np.mean((y_true_arr - y_pred_arr) ** 2)
    return float(np.sqrt(mse))


def calculate_extreme_rmse(
    df: pd.DataFrame,
    station_col: str = "station_id",
    target_col: str = "discharge_cfs",
    pred_col: str = "pred_discharge_cfs",
    quantile: float = 0.90,
) -> float:
    """
    Calculate RMSE on extreme events defined as the top 10% (by default quantile=0.90)
    highest actual discharge days per station.
    Predictions are automatically clipped to non-negative values (>= 0).

    Args:
        df: Evaluation DataFrame containing station_id, target, and prediction columns.
        station_col: Column name identifying monitoring stations.
        target_col: Column name of actual discharge values.
        pred_col: Column name of predicted discharge values.
        quantile: Quantile threshold for extreme events (default 0.90 for top 10%).

    Returns:
        float: Extreme event RMSE score across all stations' top discharge days.
    """
    if df.empty:
        return 0.0

    # Ensure clean evaluation data without NaNs in essential columns
    clean_df = df[[station_col, target_col, pred_col]].dropna().copy()
    if clean_df.empty:
        return 0.0

    # Automatically clip predictions to non-negative values
    clean_df[pred_col] = _clip_non_negative(clean_df[pred_col])

    # Calculate 90th percentile threshold of actual discharge per station
    thresholds = clean_df.groupby(station_col)[target_col].transform(
        lambda s: s.quantile(quantile)
    )

    # Filter to top 10% highest discharge days per station
    extreme_mask = clean_df[target_col] >= thresholds
    extreme_df = clean_df[extreme_mask]

    if extreme_df.empty:
        return 0.0

    return calculate_overall_rmse(
        extreme_df[target_col].to_numpy(),
        extreme_df[pred_col].to_numpy(),
    )


def calculate_mae(
    y_true: Union[Sequence[float], np.ndarray, pd.Series],
    y_pred: Union[Sequence[float], np.ndarray, pd.Series],
) -> float:
    """
    Calculate overall Mean Absolute Error (MAE) across all samples.
    Predictions are automatically clipped to non-negative values (>= 0).

    Args:
        y_true: Ground truth discharge values.
        y_pred: Predicted discharge values.

    Returns:
        float: Overall MAE score.
    """
    y_true_arr = np.asarray(y_true, dtype=np.float64)
    y_pred_arr = _clip_non_negative(y_pred)

    if len(y_true_arr) == 0:
        return 0.0

    mae = np.mean(np.abs(y_true_arr - y_pred_arr))
    return float(mae)


def calculate_r2(
    y_true: Union[Sequence[float], np.ndarray, pd.Series],
    y_pred: Union[Sequence[float], np.ndarray, pd.Series],
) -> float:
    """
    Calculate overall R² (Coefficient of Determination) across all samples.
    Predictions are automatically clipped to non-negative values (>= 0).

    Args:
        y_true: Ground truth discharge values.
        y_pred: Predicted discharge values.

    Returns:
        float: Overall R² score.
    """
    y_true_arr = np.asarray(y_true, dtype=np.float64)
    y_pred_arr = _clip_non_negative(y_pred)

    if len(y_true_arr) == 0:
        return 0.0

    # Handle single sample or constant targets gracefully
    if np.all(y_true_arr == y_true_arr[0]):
        return 1.0 if np.allclose(y_true_arr, y_pred_arr) else 0.0

    return float(r2_score(y_true_arr, y_pred_arr))


def evaluate_predictions(
    df_eval: pd.DataFrame,
    station_col: str = "station_id",
    target_col: str = "discharge_cfs",
    pred_col: str = "pred_discharge_cfs",
) -> Dict[str, float]:
    """
    Aggregator function that evaluates predictions across all competition metrics:
    1. overall_rmse: Overall RMSE across all samples (40% weight)
    2. extreme_rmse: Extreme event RMSE for top 10% highest discharge days per station (30% weight)
    3. overall_mae: Overall MAE (20% weight)
    4. overall_r2: Overall R² (10% weight)

    Predictions are automatically clipped to >= 0 using numpy before computing metrics.

    Args:
        df_eval: DataFrame containing station, target, and prediction columns.
        station_col: Name of column identifying stations (default: 'station_id').
        target_col: Name of column containing true discharge (default: 'discharge_cfs').
        pred_col: Name of column containing predicted discharge (default: 'pred_discharge_cfs').

    Returns:
        Dict[str, float]: Dictionary containing all 4 calculated metrics:
            - 'overall_rmse'
            - 'extreme_rmse'
            - 'overall_mae'
            - 'overall_r2'
    """
    required_cols = [station_col, target_col, pred_col]
    missing_cols = [col for col in required_cols if col not in df_eval.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in df_eval: {missing_cols}")

    # Prepare DataFrame and ensure predictions are clipped to non-negative values
    eval_df = df_eval[required_cols].dropna().copy()
    eval_df[pred_col] = _clip_non_negative(eval_df[pred_col])

    y_true = eval_df[target_col].to_numpy(dtype=np.float64)
    y_pred = eval_df[pred_col].to_numpy(dtype=np.float64)

    overall_rmse = calculate_overall_rmse(y_true, y_pred)
    extreme_rmse = calculate_extreme_rmse(
        eval_df,
        station_col=station_col,
        target_col=target_col,
        pred_col=pred_col,
        quantile=0.90,
    )
    overall_mae = calculate_mae(y_true, y_pred)
    overall_r2 = calculate_r2(y_true, y_pred)

    return {
        "overall_rmse": overall_rmse,
        "extreme_rmse": extreme_rmse,
        "overall_mae": overall_mae,
        "overall_r2": overall_r2,
    }


def calculate_composite_score(
    metrics: Dict[str, float],
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """
    Optional helper to compute a weighted composite score based on competition weights.
    By default uses:
    - 40% overall_rmse
    - 30% extreme_rmse
    - 20% overall_mae
    - 10% overall_r2 (inverted penalty: 1 - R² or subtracted based on custom scheme)

    Note: The specific combining formula depends on leaderboard definition.
    """
    w = weights or METRIC_WEIGHTS
    # Standard weighted error combination:
    # Error components weighted plus penalty for (1 - R²)
    score = (
        w["overall_rmse"] * metrics["overall_rmse"]
        + w["extreme_rmse"] * metrics["extreme_rmse"]
        + w["overall_mae"] * metrics["overall_mae"]
    )
    return float(score)

