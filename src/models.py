"""
Unified model wrapper for river flood forecasting hackathon.

Supports:
- CatBoost (primary regressor) and LightGBM
- Sample weighting for extreme/peak discharge events
- Native categorical feature handling (e.g., station_id)
- Automatic non-negative clipping on predictions to respect hydrological bounds
"""

from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import joblib
import numpy as np
import pandas as pd

from catboost import CatBoostRegressor
from lightgbm import LGBMRegressor


class FloodCastModel:
    """
    Unified regressor wrapper for flood discharge forecasting.

    Parameters:
        model_type: Underlying regressor family ('catboost' or 'lightgbm').
        cat_features: List of column names or indices identifying categorical features.
        random_state: Random seed for reproducibility.
        **model_params: Additional keyword parameters forwarded to the underlying model.
    """

    SUPPORTED_MODELS = ("catboost", "lightgbm")

    def __init__(
        self,
        model_type: str = "catboost",
        cat_features: Optional[Sequence[str]] = None,
        random_state: int = 42,
        **model_params: Any,
    ) -> None:
        self.model_type = model_type.lower().strip()
        if self.model_type not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model_type '{model_type}'. Supported: {self.SUPPORTED_MODELS}"
            )

        self.cat_features: List[str] = list(cat_features) if cat_features is not None else []
        self.random_state = random_state
        self.model_params: Dict[str, Any] = model_params
        self.feature_names_: Optional[List[str]] = None
        self.is_fitted_: bool = False

        self.model: Union[CatBoostRegressor, LGBMRegressor] = self._build_model()

    def _build_model(self) -> Union[CatBoostRegressor, LGBMRegressor]:
        """Instantiate the underlying regressor with default and user parameters."""
        params = dict(self.model_params)

        if self.model_type == "catboost":
            params.setdefault("loss_function", "RMSE")
            params.setdefault("random_seed", self.random_state)
            params.setdefault("verbose", 0)
            if self.cat_features and "cat_features" not in params:
                params["cat_features"] = self.cat_features
            return CatBoostRegressor(**params)

        elif self.model_type == "lightgbm":
            params.setdefault("objective", "regression")
            params.setdefault("random_state", self.random_state)
            params.setdefault("verbose", -1)
            return LGBMRegressor(**params)

        raise ValueError(f"Unknown model_type: {self.model_type}")

    def _prepare_data(
        self,
        X: Union[pd.DataFrame, np.ndarray, Sequence],
        cat_features: Optional[List[str]] = None,
    ) -> Union[pd.DataFrame, np.ndarray]:
        """
        Prepares input features. Converts categorical string columns to 'category'
        dtype when using LightGBM.
        """
        active_cats = cat_features if cat_features is not None else self.cat_features

        if isinstance(X, pd.DataFrame):
            X_out = X.copy()
            if self.model_type == "lightgbm" and active_cats:
                for col in active_cats:
                    if col in X_out.columns:
                        X_out[col] = X_out[col].astype("category")
            return X_out

        return np.asarray(X)

    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.Series, np.ndarray, Sequence[float]],
        sample_weights: Optional[Union[pd.Series, np.ndarray, Sequence[float]]] = None,
        sample_weight: Optional[Union[pd.Series, np.ndarray, Sequence[float]]] = None,
        cat_features: Optional[Sequence[str]] = None,
        eval_set: Optional[
            Union[
                Tuple[Union[pd.DataFrame, np.ndarray], Union[pd.Series, np.ndarray]],
                List[Tuple[Union[pd.DataFrame, np.ndarray], Union[pd.Series, np.ndarray]]],
            ]
        ] = None,
        **fit_kwargs: Any,
    ) -> "FloodCastModel":
        """
        Fit the model on training data.

        Args:
            X: Training features (DataFrame or array-like).
            y: Target discharge values.
            sample_weights: Optional weights per sample to emphasize peak/extreme discharge events.
            sample_weight: Alias for sample_weights.
            cat_features: Optional override for categorical feature names.
            eval_set: Optional evaluation set for early stopping / validation.
            **fit_kwargs: Additional arguments forwarded to the underlying fit() method.

        Returns:
            self: The fitted model instance.
        """
        # Resolve sample weights alias
        weights = sample_weights if sample_weights is not None else sample_weight
        if weights is not None:
            weights = np.asarray(weights, dtype=np.float64)

        if cat_features is not None:
            self.cat_features = list(cat_features)

        if isinstance(X, pd.DataFrame):
            self.feature_names_ = list(X.columns)

        X_prepared = self._prepare_data(X, cat_features=self.cat_features)
        y_prepared = np.asarray(y, dtype=np.float64)

        # Prepare eval_set if provided
        prepared_eval_set = None
        if eval_set is not None:
            if isinstance(eval_set, tuple) and len(eval_set) == 2:
                eval_X, eval_y = eval_set
                prepared_eval_set = [(
                    self._prepare_data(eval_X, cat_features=self.cat_features),
                    np.asarray(eval_y, dtype=np.float64),
                )]
            elif isinstance(eval_set, list):
                prepared_eval_set = [
                    (
                        self._prepare_data(e_X, cat_features=self.cat_features),
                        np.asarray(e_y, dtype=np.float64),
                    )
                    for e_X, e_y in eval_set
                ]

        if self.model_type == "catboost":
            fit_params: Dict[str, Any] = dict(fit_kwargs)
            if weights is not None:
                fit_params["sample_weight"] = weights
            if prepared_eval_set is not None:
                fit_params["eval_set"] = prepared_eval_set
            if self.cat_features:
                fit_params["cat_features"] = self.cat_features

            self.model.fit(X_prepared, y_prepared, **fit_params)

        elif self.model_type == "lightgbm":
            fit_params = dict(fit_kwargs)
            if weights is not None:
                fit_params["sample_weight"] = weights
            if prepared_eval_set is not None:
                fit_params["eval_set"] = prepared_eval_set
            if self.cat_features:
                fit_params["categorical_feature"] = self.cat_features

            self.model.fit(X_prepared, y_prepared, **fit_params)

        self.is_fitted_ = True
        return self

    def predict(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        **predict_kwargs: Any,
    ) -> np.ndarray:
        """
        Generate predictions for input features.
        Raw predictions are automatically clipped to non-negative values (>= 0)
        to respect physical hydrological bounds.

        Args:
            X: Input feature matrix or DataFrame.
            **predict_kwargs: Additional arguments passed to predict().

        Returns:
            np.ndarray: 1D array of non-negative discharge predictions.
        """
        if not self.is_fitted_:
            raise RuntimeError("Model must be fitted before calling predict().")

        X_prepared = self._prepare_data(X, cat_features=self.cat_features)
        raw_preds = self.model.predict(X_prepared, **predict_kwargs)
        raw_preds_arr = np.asarray(raw_preds, dtype=np.float64).ravel()

        # Automatically clip predictions to non-negative values (>= 0)
        clipped_preds = np.clip(raw_preds_arr, 0.0, None)
        return clipped_preds

    @property
    def feature_importances_(self) -> np.ndarray:
        """Returns the feature importance values from the fitted model."""
        if not self.is_fitted_:
            raise RuntimeError("Model must be fitted to access feature importances.")

        if hasattr(self.model, "feature_importances_"):
            return np.asarray(self.model.feature_importances_)
        elif hasattr(self.model, "get_feature_importance"):
            return np.asarray(self.model.get_feature_importance())
        raise AttributeError(f"Underlying model {self.model_type} does not support feature importances.")

    def get_feature_importance_df(self) -> pd.DataFrame:
        """
        Returns a sorted DataFrame of feature importances with column names.
        """
        importances = self.feature_importances_
        names = self.feature_names_ or [f"feature_{i}" for i in range(len(importances))]
        df = pd.DataFrame({"feature": names, "importance": importances})
        return df.sort_values(by="importance", ascending=False).reset_index(drop=True)

    def save(self, filepath: str) -> None:
        """Serialize and save the FloodCastModel instance to disk."""
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> "FloodCastModel":
        """Load a serialized FloodCastModel instance from disk."""
        instance = joblib.load(filepath)
        if not isinstance(instance, cls):
            raise TypeError(f"Loaded object is of type {type(instance)}, expected {cls}.")
        return instance


# FastAPI App instance export for uvicorn server
try:
    from src.api import app
except Exception:
    app = None
